/**
 * The exceptions queue: everything a person must decide (compliance flags, judge
 * disagreements, upload/auth failures, refund and chargeback reviews, plan-switch
 * requests, consent-price mismatches, crisis escalations, boost approvals,
 * affiliate applications). Workers post items through POST /api/exceptions; the app
 * raises its own. Every decision is written to the append-only exception_events
 * trail with the person who made it. Approving a boost writes the governor's
 * human-approval record (governor_approvals) and forwards it to the workers.
 */
import type { Store } from "./db/store";
import type { ExceptionEvent, ExceptionRow, ExceptionStatus, ExceptionType, GovernorApproval } from "./db/types";

export const EXCEPTION_TYPES: readonly ExceptionType[] = [
  "compliance_flag",
  "judge_disagreement",
  "upload_auth_failure",
  "refund_review",
  "chargeback_review",
  "plan_switch_request",
  "consent_price_mismatch",
  "crisis_escalation",
  "boost_approval",
  "affiliate_application",
  "affiliate_fraud",
  "coach_flag",
  "clinical_interest",
  "group_quote",
  "price_help",
] as const;

export const TYPE_LABEL: Record<ExceptionType, string> = {
  compliance_flag: "Compliance flag",
  judge_disagreement: "Judge disagreement",
  upload_auth_failure: "Upload or sign-in failure",
  refund_review: "Refund review",
  chargeback_review: "Chargeback review",
  plan_switch_request: "Plan-switch request",
  consent_price_mismatch: "Consent-price mismatch",
  crisis_escalation: "Crisis escalation",
  boost_approval: "Boost approval",
  affiliate_application: "Affiliate application",
  affiliate_fraud: "Affiliate fraud check",
  coach_flag: "Coach flag",
  clinical_interest: "Labs + clinician interest (client clinical team)",
  group_quote: "Group quote (5+ gift seats)",
  price_help: "Price-help request (a person decides)",
};

/** Which decisions each type offers. Approve/reject are for requests; resolve closes a review. */
export function actionsFor(type: ExceptionType): ("approve" | "reject" | "resolve")[] {
  switch (type) {
    case "boost_approval":
    case "affiliate_application":
    case "plan_switch_request":
    case "group_quote":
    case "price_help":
      return ["approve", "reject"];
    case "refund_review":
    case "chargeback_review":
    case "compliance_flag":
    case "judge_disagreement":
      return ["approve", "reject", "resolve"];
    default:
      return ["resolve"];
  }
}

export interface NewException {
  type: ExceptionType;
  title: string;
  detail?: string;
  ref?: string | null;
  severity?: ExceptionRow["severity"];
  source: string;
  dedupe_key?: string;
  payload?: Record<string, unknown>;
}

const clip = (s: unknown, n: number) => (typeof s === "string" ? s.replace(/[\u0000-\u0008\u000B-\u001F]/g, "").slice(0, n) : "");

/** Validates a worker's body. Returns the cleaned item or a list of problems. */
export function parseException(body: unknown): { ok: true; item: NewException } | { ok: false; errors: string[] } {
  const b = (body && typeof body === "object" ? body : {}) as Record<string, unknown>;
  const errors: string[] = [];
  const type = b.type as ExceptionType;
  if (!EXCEPTION_TYPES.includes(type)) errors.push("type: unknown");
  const title = clip(b.title, 200).trim();
  if (!title) errors.push("title: required");
  const severity = (["low", "normal", "high", "critical"] as const).includes(b.severity as never) ? (b.severity as ExceptionRow["severity"]) : "normal";
  const source = clip(b.source, 60).trim() || "worker";
  const ref = b.ref === undefined || b.ref === null ? null : clip(String(b.ref), 120);
  const payload = b.payload && typeof b.payload === "object" && !Array.isArray(b.payload) ? (b.payload as Record<string, unknown>) : {};
  if (JSON.stringify(payload).length > 8000) errors.push("payload: too large");
  if (type === "boost_approval") {
    const p = payload as { boost_id?: unknown; requested_daily_usd?: unknown };
    if (typeof p.boost_id !== "string" || !/^[A-Za-z0-9_-]{1,80}$/.test(p.boost_id)) errors.push("payload.boost_id: required for boost_approval");
    if (typeof p.requested_daily_usd !== "number" || !(p.requested_daily_usd >= 0)) errors.push("payload.requested_daily_usd: required for boost_approval");
  }
  if (errors.length) return { ok: false, errors };
  return { ok: true, item: { type, title, detail: clip(b.detail, 4000), ref, severity, source, dedupe_key: clip(b.dedupe_key, 200) || undefined, payload } };
}

async function event(store: Store, exceptionId: string, action: ExceptionEvent["action"], actor: string, note: string | null) {
  await store.insert("exception_events", { exception_id: exceptionId, action, actor, note });
}

/** Creates an item, or returns the existing open/closed one with the same (type, dedupe_key). */
export async function raiseException(store: Store, x: NewException): Promise<{ row: ExceptionRow; created: boolean }> {
  const dedupe = x.dedupe_key ?? `${x.source}:${x.ref ?? x.title}`.slice(0, 200);
  const existing = await store.findOne("exceptions", { type: x.type, dedupe_key: dedupe });
  if (existing) {
    await event(store, existing.id, "repeated", x.source, null);
    return { row: existing, created: false };
  }
  let row: ExceptionRow;
  try {
    row = await store.insert("exceptions", {
      type: x.type,
      status: "open",
      severity: x.severity ?? (x.type === "crisis_escalation" ? "critical" : "normal"),
      source: x.source,
      title: x.title,
      detail: x.detail ?? "",
      ref: x.ref ?? null,
      dedupe_key: dedupe,
      payload: x.payload ?? {},
      decided_by: null,
      decided_at: null,
      decision_note: null,
    });
  } catch {
    // A concurrent post won the unique (type, dedupe_key) race.
    const again = await store.findOne("exceptions", { type: x.type, dedupe_key: dedupe });
    if (!again) throw new Error("exception insert failed");
    return { row: again, created: false };
  }
  await event(store, row.id, "created", x.source, null);
  return { row, created: true };
}

export type Decision = "approve" | "reject" | "resolve";
const STATUS_OF: Record<Decision, ExceptionStatus> = { approve: "approved", reject: "rejected", resolve: "resolved" };

export interface DecideInput {
  id: string;
  decision: Decision;
  actor: string;
  note?: string;
  /** boost_approval only: the approved daily ceiling (defaults to the requested amount). */
  maxDailyUsd?: number;
}

export type DecideResult =
  | { ok: true; row: ExceptionRow; approval?: GovernorApproval; effects: string[] }
  | { ok: false; reason: "not_found" | "already_decided" | "not_allowed" | "bad_amount" | "no_actor" };

/** Approve / reject / resolve, once. The status claim is atomic (updateWhere on status = open). */
export async function decideException(store: Store, d: DecideInput, now = new Date(), forward: typeof forwardApproval = forwardApproval): Promise<DecideResult> {
  const actor = d.actor.trim().slice(0, 80);
  if (!actor) return { ok: false, reason: "no_actor" };
  const row = await store.get("exceptions", d.id);
  if (!row) return { ok: false, reason: "not_found" };
  if (row.status !== "open") return { ok: false, reason: "already_decided" };
  if (!actionsFor(row.type).includes(d.decision)) return { ok: false, reason: "not_allowed" };
  let max: number | null = null;
  if (row.type === "boost_approval" && d.decision === "approve") {
    const requested = Number((row.payload as { requested_daily_usd?: number }).requested_daily_usd ?? NaN);
    max = d.maxDailyUsd ?? requested;
    if (!Number.isFinite(max) || max < 0 || (Number.isFinite(requested) && max > requested)) return { ok: false, reason: "bad_amount" };
  }
  const note = d.note?.trim().slice(0, 1000) || null;
  const [claimed] = await store.updateWhere("exceptions", { id: row.id, status: "open" }, { status: STATUS_OF[d.decision], decided_by: actor, decided_at: now.toISOString(), decision_note: note });
  if (!claimed) return { ok: false, reason: "already_decided" };
  await event(store, row.id, d.decision, actor, note);
  const out: string[] = [];
  let approval: GovernorApproval | undefined;
  if (row.type === "boost_approval" && d.decision === "approve" && max !== null) {
    const boostId = String((row.payload as { boost_id: string }).boost_id);
    approval = await store.insert("governor_approvals", { boost_id: boostId, exception_id: row.id, approved_by: actor, approved_at: now.toISOString(), max_daily_usd: max, forwarded: "pending" });
    const status = await forward(approval);
    approval = (await store.update("governor_approvals", approval.id, { forwarded: status })) ?? approval;
    out.push(`governor approval recorded for boost ${boostId} (max $${max}/day, forwarded: ${status})`);
  }
  await closeMirroredTicket(store, claimed);
  if (row.type === "affiliate_application") {
    const { onAffiliateDecision } = await import("./affiliates");
    out.push(...(await onAffiliateDecision(store, claimed, d.decision, actor, now)));
  }
  return { ok: true, row: claimed, approval, effects: out };
}

/**
 * Sends the approval record to the workers' governor (POST /growth/approvals/boost),
 * in the shape the governor reads: { boost_id, approval: { by, at, max_daily_usd } }.
 * Nothing is spent by this call: the governor still needs SPEND_ENABLED=1 and its own checks.
 */
export async function forwardApproval(a: GovernorApproval): Promise<GovernorApproval["forwarded"]> {
  const base = (process.env.GROWTH_WORKER_URL ?? process.env.QA_WORKER_URL ?? "").replace(/\/$/, "");
  const token = process.env.WORKER_TOKEN ?? "";
  if (!base || !token) return "not_configured";
  try {
    const res = await fetch(`${base}/growth/approvals/boost`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Worker-Token": token },
      body: JSON.stringify({ boost_id: a.boost_id, approval: { by: a.approved_by, at: a.approved_at, max_daily_usd: a.max_daily_usd }, exception_id: a.exception_id }),
      signal: AbortSignal.timeout(10_000),
    });
    return res.ok ? "sent" : "failed";
  } catch {
    return "failed";
  }
}

export async function openExceptions(store: Store): Promise<ExceptionRow[]> {
  const rows = await store.find("exceptions", { status: "open" }, { orderBy: "created_at" });
  const rank = { critical: 0, high: 1, normal: 2, low: 3 } as const;
  return rows.sort((a, b) => rank[a.severity] - rank[b.severity] || a.created_at.localeCompare(b.created_at));
}

/**
 * The app's own reviews already land in support_tickets and crisis_events (billing, disputes,
 * plan switches, consent records, crisis). This mirrors the open ones into the queue once
 * (dedupe by ticket / event id) so /admin/exceptions is the one place to decide. Resolving the
 * exception closes the ticket (see closeMirroredTicket). Run on page load, by the digest and cron.
 */
export async function syncAppExceptions(store: Store): Promise<number> {
  let created = 0;
  const tickets = await store.find("support_tickets", { status: "open" }, { limit: 500 });
  for (const t of tickets) {
    const type: ExceptionType | null =
      t.reason === "refund_review" ? "refund_review"
      : t.reason === "dispute" ? "chargeback_review"
      : t.reason === "plan_change" ? "plan_switch_request"
      : t.reason === "crisis_followup" ? "crisis_escalation"
      : /consent box showed|consent-price record/.test(t.message) ? "consent_price_mismatch"
      : null;
    if (!type) continue;
    const r = await raiseException(store, {
      type,
      title: `${TYPE_LABEL[type]} (ticket ${t.id.slice(0, 8)})`,
      detail: t.message.slice(0, 4000),
      ref: `ticket:${t.id}`,
      source: "app:tickets",
      dedupe_key: `ticket:${t.id}`,
      severity: type === "crisis_escalation" ? "critical" : type === "chargeback_review" ? "high" : "normal",
    });
    if (r.created) created++;
  }
  const crisis = await store.find("crisis_events", { handled_at: null }, { limit: 200 });
  for (const c of crisis) {
    const r = await raiseException(store, {
      type: "crisis_escalation",
      title: `Crisis ${c.category.replace("_", " ")} (event ${c.id.slice(0, 8)})`,
      detail: "Open /admin#crisis for the conversation. Acknowledge within 15 minutes during staffed hours (07:00–23:00 ET).",
      ref: `crisis:${c.id}`,
      source: "app:crisis",
      dedupe_key: `crisis:${c.id}`,
      severity: "critical",
    });
    if (r.created) created++;
  }
  return created;
}

export async function closeMirroredTicket(store: Store, row: ExceptionRow): Promise<void> {
  if (row.ref?.startsWith("ticket:")) await store.updateWhere("support_tickets", { id: row.ref.slice(7), status: "open" }, { status: "closed" });
}
