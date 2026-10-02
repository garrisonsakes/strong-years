/**
 * Lifecycle email engine. Sequences are data (content/lifecycle/sequences.json):
 * each has an audience (a query over our tables), a kind (transactional / lifecycle /
 * marketing) and steps with a delay from the audience's anchor time. The engine runs
 * from /api/cron/lifecycle (hourly) and is safe to run any number of times:
 *
 * - idempotent: one email_sends row per (email, sequence, step), claimed before sending;
 * - consent: marketing needs an explicit opt-in (email_prefs), lifecycle stops on
 *   unsubscribe, transactional (billing facts) always goes; the daily coach email needs
 *   its own opt-in;
 * - unsubscribe: every non-transactional email carries a signed one-click link and the
 *   RFC 8058 headers (List-Unsubscribe + List-Unsubscribe-Post);
 * - quiet hours: nothing outside 08:00–20:00 in the recipient's time zone (it waits);
 * - cap: at most one non-transactional email per recipient per rolling 24 hours,
 *   highest-priority sequence first;
 * - steps owned elsewhere (the orders/paid welcome, the 48-hour billing reminder) are
 *   listed for completeness and never sent twice.
 *
 * Every subject and body is scanned by workers/compliance (`python -m compliance
 * templates ../app/content/lifecycle/sequences.json`, in the workers test suite).
 */
import { createHmac } from "node:crypto";
import sequencesJson from "../../../content/lifecycle/sequences.json";
import { env } from "../config";
import type { Store } from "../db/store";
import type { EmailSend, Member, Membership } from "../db/types";
import { getLaunchState } from "../launch";
import { moneyExact } from "../pricing";
import { renewalCertainty } from "../billing/clock";
import { safeEqual } from "../safeEqual";
import { bumpFor, ROUTING } from "../offers/route";
import { shopifyConfig } from "../billing/shopify";
import type { EmailInput } from "../notify";

export type Kind = "transactional" | "lifecycle" | "marketing";
export interface StepDef {
  id: string;
  after_hours: number;
  subject: string;
  body: string;
  /** Sent by another part of the app; the engine records it as skipped and never sends it. */
  owner?: string;
}
export interface SequenceDef {
  kind: Kind;
  from: "chang" | "sun" | "team";
  priority: number;
  audience: string;
  description: string;
  steps: StepDef[];
}
export interface SequencesFile {
  version: number;
  rules: { quiet_start_hour: number; quiet_end_hour: number; daily_cap: number; default_timezone: string };
  sequences: Record<string, SequenceDef>;
  coach_tips: { subject: string; body: string }[];
}

export const SEQUENCES = sequencesJson as unknown as SequencesFile;

/** One person eligible for one sequence right now, with the anchor its delays count from. */
export interface Candidate {
  sequence: string;
  email: string;
  memberId: string | null;
  firstName: string;
  timezone: string | null;
  anchor: Date;
  vars: Record<string, string>;
  /** Steps to consider (default: all); e.g. win-back keys steps by the membership. */
  stepSuffix?: string;
}

/* ------------------------------------------------------------------ unsubscribe (signed, one click) */

function secret(): string {
  return process.env.SESSION_SECRET || process.env.CRON_SECRET || "dev-only-unsubscribe-secret";
}

export function unsubscribeToken(email: string): string {
  return createHmac("sha256", secret()).update(`unsub:${email.toLowerCase()}`).digest("base64url").slice(0, 32);
}

export function verifyUnsubscribe(email: string, token: string): boolean {
  return !!email && !!token && safeEqual(unsubscribeToken(email), token);
}

export function unsubscribeUrl(email: string): string {
  return `${env.siteUrl}/api/unsubscribe?e=${encodeURIComponent(Buffer.from(email.toLowerCase()).toString("base64url"))}&t=${unsubscribeToken(email)}`;
}

export function unsubscribeHeaders(email: string): Record<string, string> {
  return { "List-Unsubscribe": `<${unsubscribeUrl(email)}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" };
}

export async function unsubscribe(store: Store, email: string, source: string, now = new Date()): Promise<void> {
  const e = email.toLowerCase();
  const pref = await store.findOne("email_prefs", { email: e });
  if (pref) await store.update("email_prefs", pref.id, { lifecycle_opt_in: false, coach_opt_in: false, unsubscribed_at: now.toISOString(), source });
  else await store.insert("email_prefs", { email: e, lifecycle_opt_in: false, coach_opt_in: false, unsubscribed_at: now.toISOString(), source });
}

/* ------------------------------------------------------------------ rendering */

export function render(tpl: string, vars: Record<string, string>): string {
  return tpl.replace(/\{\{(\w+)\}\}/g, (_, k: string) => vars[k] ?? "");
}

export function localHour(now: Date, tz: string | null, fallback: string): number {
  try {
    const h = new Intl.DateTimeFormat("en-US", { timeZone: tz || fallback, hour: "numeric", hourCycle: "h23" }).format(now);
    return Number(h) % 24;
  } catch {
    return Number(new Intl.DateTimeFormat("en-US", { timeZone: fallback, hour: "numeric", hourCycle: "h23" }).format(now)) % 24;
  }
}

/* ------------------------------------------------------------------ audiences */

const DAY = 86_400_000;
const paying = (m: Membership) => (m.status === "active" || m.status === "past_due") && m.plan !== "gift" && !m.pending_verification;
const fmtDate = (iso: string | null | undefined) => (iso ? new Date(iso).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" }) : "");

export async function candidates(store: Store, now = new Date()): Promise<Candidate[]> {
  const out: Candidate[] = [];
  const members = await store.find("members", { is_demo: false });
  const byId = new Map(members.map((m) => [m.id, m]));
  const memberships = await store.find("memberships", { is_demo: false });
  const msBy = new Map<string, Membership[]>();
  for (const m of memberships) msBy.set(m.member_id, [...(msBy.get(m.member_id) ?? []), m]);
  const orders = await store.find("sy_orders", { is_demo: false });
  const site = env.siteUrl;
  const base = (m: Member) => ({ email: m.email, memberId: m.id, firstName: m.first_name || "friend", timezone: m.timezone });
  const varsFor = (m: Member, extra: Record<string, string> = {}) => ({ first_name: m.first_name || "friend", site, account_url: `${site}/app/account`, ...extra });

  // Waitlist nurture: confirmed waitlisters during the runway who ALSO gave a separate tips opt-in
  // (the waitlist consent itself promises only the launch emails, so it never qualifies alone).
  const state = await getLaunchState(store);
  if (!state.live) {
    const prefs = new Map((await store.find("email_prefs", { lifecycle_opt_in: true })).map((p) => [p.email, p]));
    for (const w of await store.find("waitlist", { status: "confirmed" })) {
      if (!w.confirmed_at || w.member_id || !prefs.has(w.email)) continue;
      out.push({ sequence: "waitlist_nurture", email: w.email, memberId: null, firstName: w.first_name || "friend", timezone: null, anchor: new Date(w.confirmed_at), vars: { first_name: w.first_name || "friend", site } });
    }
  }

  for (const m of members) {
    const ms = msBy.get(m.id) ?? [];
    const live = ms.filter(paying);
    const mine = orders.filter((o) => o.member_id === m.id);
    const books = mine.find((o) => (o.kind === "front_end" || /^ebook_/.test(o.offer_code)) && o.status === "paid");

    // Books only → membership (cell A's 3 emails; email 1 is sent by orders/paid).
    if (books && ms.length === 0) out.push({ sequence: "books_to_membership", ...base(m), anchor: new Date(books.created_at), vars: varsFor(m, { founding_url: `${site}/b?t=JOIN` }) });

    // Second purchase within 7 days (MONETIZATION_ENGINE.md §4): cell B buyers only (cell A has its own 3 emails);
    // stops at the first bump or gift. The offer is matched to the keyword they came in on (routing table bumps).
    const bundle = mine.find((o) => /^bundle_m12/.test(o.offer_code) && o.status === "paid");
    if (bundle && now.getTime() - new Date(bundle.created_at).getTime() <= 7 * DAY && !mine.some((o) => (o.kind === "bump" || o.kind === "gift") && o.status === "paid")) {
      const kw = typeof m.attribution?.keyword === "string" ? m.attribution.keyword : null;
      const bump = bumpFor((ROUTING.keyword_pillar as Record<string, string>)[(kw ?? "").toUpperCase()] ?? "general");
      const grocery = bump?.frame === "grocery_lists";
      out.push({
        sequence: "second_purchase", ...base(m), anchor: new Date(bundle.created_at), stepSuffix: bundle.id.slice(0, 8),
        vars: varsFor(m, {
          bump_subject: grocery ? "Sun Yoon's grocery lists (optional)" : "The wall plan most people print (optional)",
          bump_line: grocery ? "Sun Yoon's weekly grocery lists come with the 12-week wall plan: one page per week, the protein grams written in, so the shopping is decided before you go." : "The 12-week wall plan is one large-print page you stick on the fridge and tick each morning.",
          bump_url: `https://${shopifyConfig.storeDomain()}/products/the-wall-plan`,
          gift_url: `${site}/b?t=FAMILY`,
        }),
      });
    }

    for (const ms1 of live) {
      const start = new Date(ms1.first_paid_at ?? ms1.created_at);
      out.push({ sequence: "member_onboarding", ...base(m), anchor: start, stepSuffix: ms1.id.slice(0, 8), vars: varsFor(m) });

      // Activation: no practice logged since joining (3 days) / in the last 7 days.
      const logs = await store.find("practice_logs", { member_id: m.id }, { orderBy: "created_at", desc: true, limit: 1 });
      const last = logs[0] ? new Date(logs[0].created_at) : null;
      if (!last && now.getTime() - start.getTime() >= 3 * DAY) out.push({ sequence: "activation", ...base(m), anchor: start, stepSuffix: `${ms1.id.slice(0, 8)}`, vars: varsFor(m) });
      if (last && now.getTime() - last.getTime() >= 7 * DAY) {
        const week = new Date(last.getTime() + 7 * DAY);
        out.push({ sequence: "activation_lapsed", ...base(m), anchor: week, stepSuffix: last.toISOString().slice(0, 10), vars: varsFor(m) });
      }

      // Pre-renewal, 7 days (the 48-hour one is the billing reminder): re-checked, worded conditionally.
      if (ms1.current_period_end && !ms1.cancel_at_period_end && ms1.interval !== "none") {
        const end = new Date(ms1.current_period_end);
        const certainty = await renewalCertainty(store, ms1, now);
        if (certainty !== "skip") {
          out.push({
            sequence: "pre_renewal",
            ...base(m),
            anchor: new Date(end.getTime() - 7 * DAY),
            stepSuffix: ms1.current_period_end.slice(0, 10),
            vars: varsFor(m, { renew_date: fmtDate(ms1.current_period_end), price: moneyExact(ms1.price_cents), if_active: certainty === "certain" ? "" : "If your membership is still active, " }),
          });
        }
      }

      // Failed payment recovery: only when we know a payment failed (past_due with a grace date).
      if (ms1.status === "past_due" && ms1.grace_until) {
        out.push({ sequence: "failed_payment", ...base(m), anchor: new Date(new Date(ms1.grace_until).getTime() - 7 * DAY), stepSuffix: ms1.grace_until.slice(0, 10), vars: varsFor(m, { grace_date: fmtDate(ms1.grace_until) }) });
      }

      // Founding annual offer after renewal 1 (a request, never a second charge).
      const paid = mine.filter((o) => o.membership_id === ms1.id && o.kind === "membership_charge" && o.status === "paid").sort((a, b) => a.created_at.localeCompare(b.created_at));
      if (ms1.founding && ms1.interval === "month" && paid.length >= 2) out.push({ sequence: "annual_offer", ...base(m), anchor: new Date(paid[1]!.created_at), stepSuffix: ms1.id.slice(0, 8), vars: varsFor(m) });

      // Daily coach email: separate opt-in only.
      out.push({ sequence: "daily_coach", ...base(m), anchor: new Date(now.getTime() - DAY), stepSuffix: now.toISOString().slice(0, 10), vars: varsFor(m) });
    }

    // Win-back 30/60/90 after the last membership ended; never while any membership is live.
    if (live.length === 0) {
      const ended = ms.filter((x) => x.plan !== "gift" && (x.status === "canceled" || x.status === "expired") && x.canceled_at).sort((a, b) => (b.canceled_at ?? "").localeCompare(a.canceled_at ?? ""))[0];
      if (ended) out.push({ sequence: "win_back", ...base(m), anchor: new Date(ended.canceled_at!), stepSuffix: ended.id.slice(0, 8), vars: varsFor(m, { join_url: `${site}/b?t=JOIN` }) });
    }

    // Gift recipient: the gift ends and never renews.
    for (const g of ms.filter((x) => x.plan === "gift" && x.status === "active" && x.current_period_end)) {
      out.push({ sequence: "gift_recipient", ...base(m), anchor: new Date(new Date(g.current_period_end!).getTime() - 7 * DAY), stepSuffix: g.id.slice(0, 8), vars: varsFor(m, { gift_end: fmtDate(g.current_period_end) }) });
    }
  }

  // Gift recipient who hasn't claimed yet: reminders to use the claim email (the code itself is never re-sent here).
  for (const g of await store.find("gifts", { redeemed_member_id: null })) {
    if (!g.recipient_email) continue;
    out.push({ sequence: "gift_unclaimed", email: g.recipient_email.toLowerCase(), memberId: null, firstName: g.recipient_name || "friend", timezone: null, anchor: new Date(g.created_at), stepSuffix: g.id.slice(0, 8), vars: { first_name: g.recipient_name || "friend", gifter: g.gifter_name || "Someone who cares about you", site, redeem_url: `${site}/gift/redeem` } });
  }
  void byId;
  return out;
}

/* ------------------------------------------------------------------ the run */

export interface RunResult {
  sent: number;
  skipped: Record<string, number>;
  failed: number;
}

type Sender = (input: EmailInput) => Promise<unknown>;

export async function runLifecycle(store: Store, now = new Date(), send?: Sender, file: SequencesFile = SEQUENCES): Promise<RunResult> {
  const doSend: Sender = send ?? (async (i) => (await import("../notify")).sendEmail(i));
  const result: RunResult = { sent: 0, skipped: {}, failed: 0 };
  const skip = (why: string) => (result.skipped[why] = (result.skipped[why] ?? 0) + 1);
  const prefs = new Map((await store.find("email_prefs")).map((p) => [p.email, p]));
  const recent = await store.find("email_sends", { status: "sent", sent_at: { gte: new Date(now.getTime() - DAY).toISOString() } });
  const capUsed = new Map<string, number>();
  for (const r of recent) if (file.sequences[r.sequence]?.kind !== "transactional") capUsed.set(r.email, (capUsed.get(r.email) ?? 0) + 1);

  const all = (await candidates(store, now)).sort((a, b) => (file.sequences[a.sequence]?.priority ?? 99) - (file.sequences[b.sequence]?.priority ?? 99));
  for (const c of all) {
    const seq = file.sequences[c.sequence];
    if (!seq) continue;
    const pref = prefs.get(c.email);
    if (seq.kind !== "transactional" && pref?.unsubscribed_at) {
      skip("unsubscribed");
      continue;
    }
    if (c.sequence === "daily_coach" && !pref?.coach_opt_in) continue;
    const due = seq.steps.filter((s) => c.anchor.getTime() + s.after_hours * 3_600_000 <= now.getTime());
    if (!due.length) continue;
    // Only the latest due step goes out; earlier ones that were missed (e.g. the person was capped) are skipped, never stacked.
    const step = due[due.length - 1]!;
    const stepKey = c.stepSuffix ? `${step.id}:${c.stepSuffix}` : step.id;
    if (await store.findOne("email_sends", { email: c.email, sequence: c.sequence, step: stepKey })) continue;
    if (step.owner) {
      await store.insert("email_sends", { email: c.email, member_id: c.memberId, sequence: c.sequence, step: stepKey, status: "skipped", reason: `owned by ${step.owner}`, sent_at: null }).catch(() => null);
      skip("owned_elsewhere");
      continue;
    }
    const hour = localHour(now, c.timezone, file.rules.default_timezone);
    if (hour < file.rules.quiet_end_hour || hour >= file.rules.quiet_start_hour) {
      skip("quiet_hours");
      continue;
    }
    if (seq.kind !== "transactional" && (capUsed.get(c.email) ?? 0) >= file.rules.daily_cap) {
      skip("daily_cap");
      continue;
    }
    let claim: EmailSend;
    try {
      claim = await store.insert("email_sends", { email: c.email, member_id: c.memberId, sequence: c.sequence, step: stepKey, status: "claimed", reason: null, sent_at: null });
    } catch {
      continue; // another run claimed it
    }
    const tip = c.sequence === "daily_coach" ? file.coach_tips[Math.floor(now.getTime() / DAY) % file.coach_tips.length]! : null;
    const vars = { ...c.vars, unsubscribe_url: unsubscribeUrl(c.email) };
    const subject = render(tip?.subject ?? step.subject, vars);
    const body = render(tip?.body ?? step.body, vars);
    try {
      await doSend({
        to: c.email,
        from: seq.from,
        subject,
        text: body,
        template: `LC_${c.sequence}_${step.id}`,
        ...(seq.kind === "transactional" ? {} : { headers: unsubscribeHeaders(c.email), manageLine: `Unsubscribe from these emails (one click): ${vars.unsubscribe_url}` }),
      });
      await store.update("email_sends", claim.id, { status: "sent", sent_at: now.toISOString() });
      if (seq.kind !== "transactional") capUsed.set(c.email, (capUsed.get(c.email) ?? 0) + 1);
      result.sent++;
    } catch (e) {
      await store.update("email_sends", claim.id, { status: "failed", reason: (e as Error).message.slice(0, 200) });
      result.failed++;
    }
  }
  return result;
}
