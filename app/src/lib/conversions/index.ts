/**
 * Server-side conversion events through an outbox.
 *
 *   recordConversion() -> (consent + safety checks) -> conversion_outbox rows, one per
 *   enabled platform, unique on (platform, event_id) -> sent right away, retried by
 *   the launch cron (flushConversions) with backoff.
 *
 * The unique key is the dedup: a webhook and a success redirect that both report
 * the same purchase, a double cron run, or a retried request never produce a second
 * event. The platforms dedupe on event_id as well.
 */
import type { Store } from "../db/store";
import type { Attribution, ConversionOutboxRow, ConversionPlatform } from "../db/types";
import { hasAdConsent } from "./consent";
import { buildMetaEvent, buildTikTokEvent, emailHash, enabledPlatforms, platformEnabled, sendToPlatform, type ConversionEvent } from "./adapters";

export interface ConversionInput {
  name: ConversionEvent;
  eventId: string;
  sourcePath: string;
  email?: string | null;
  valueCents?: number;
  contentName?: string;
  memberId?: string | null;
  attribution?: Attribution | null;
  /**
   * Quiz and other health-context surfaces: never forwarded to an ad platform, even
   * with consent (Washington MHMD: the visit itself can reveal health information).
   */
  healthContext?: boolean;
  now?: Date;
}

export type ForwardDecision = "queued" | "duplicate" | "no_consent" | "no_email" | "health_context" | "disabled" | "blocked";

export interface ConversionResult {
  decision: ForwardDecision;
  rows: ConversionOutboxRow[];
  /** Platforms that accepted the event during this call. */
  delivered: ConversionPlatform[];
}

const MAX_ATTEMPTS = 6;

function backoffMs(attempts: number): number {
  return Math.min(6 * 3600_000, 60_000 * 2 ** Math.max(0, attempts - 1));
}

async function dispatch(store: Store, row: ConversionOutboxRow, now: Date): Promise<boolean> {
  if (!platformEnabled(row.platform)) {
    await store.update("conversion_outbox", row.id, { status: "skipped", last_error: "platform disabled" });
    return false;
  }
  // Claim: only one worker sends a given row (pending/failed -> sending is a status we don't store,
  // so claim by bumping attempts on the exact version we read).
  const [claimed] = await store.updateWhere("conversion_outbox", { id: row.id, attempts: row.attempts, status: { in: ["pending", "failed"] } }, { attempts: row.attempts + 1, next_attempt_at: new Date(now.getTime() + backoffMs(row.attempts + 1)).toISOString() });
  if (!claimed) return false;
  const r = await sendToPlatform(row.platform, row.payload);
  if (r.ok) {
    await store.update("conversion_outbox", row.id, { status: "sent", sent_at: now.toISOString(), last_error: null });
    return true;
  }
  await store.update("conversion_outbox", row.id, { status: claimed.attempts >= MAX_ATTEMPTS ? "skipped" : "failed", last_error: (r.error ?? "error").slice(0, 120) });
  return false;
}

export async function recordConversion(store: Store, input: ConversionInput, siteUrl: string): Promise<ConversionResult> {
  const now = input.now ?? new Date();
  const none = (decision: ForwardDecision): ConversionResult => ({ decision, rows: [], delivered: [] });
  if (input.healthContext) return none("health_context");
  if (!input.email) return none("no_email");
  const platforms = enabledPlatforms();
  if (platforms.length === 0) return none("disabled");
  if (!(await hasAdConsent(store, { email: input.email, memberId: input.memberId, attribution: input.attribution }))) return none("no_consent");

  const neutral = { name: input.name, eventId: input.eventId, sourcePath: input.sourcePath, email: input.email, valueCents: input.valueCents, contentName: input.contentName, timeMs: now.getTime() };
  let built: Record<ConversionPlatform, Record<string, unknown>>;
  try {
    built = { meta: buildMetaEvent(neutral, siteUrl), tiktok: buildTikTokEvent(neutral, siteUrl) };
  } catch (err) {
    console.error("conversion blocked", (err as Error).message);
    return none("blocked");
  }
  const rows: ConversionOutboxRow[] = [];
  for (const p of platforms) {
    try {
      rows.push(
        await store.insert("conversion_outbox", {
          platform: p,
          event_id: input.eventId,
          event_name: input.name,
          payload: built[p],
          email_hash: emailHash(input.email),
          status: "pending",
          attempts: 0,
          next_attempt_at: now.toISOString(),
          last_error: null,
          sent_at: null,
        }),
      );
    } catch {
      /* (platform, event_id) already queued: deduplicated */
    }
  }
  if (rows.length === 0) return { decision: "duplicate", rows, delivered: [] };
  const delivered: ConversionPlatform[] = [];
  for (const row of rows) if (await dispatch(store, row, now)) delivered.push(row.platform);
  return { decision: "queued", rows, delivered };
}

/** Cron: retries failed/pending rows that are due. Consent is re-checked (it can be withdrawn). */
export async function flushConversions(store: Store, now = new Date(), limit = 200): Promise<{ sent: number; failed: number; skipped: number }> {
  const due = await store.find("conversion_outbox", { status: { in: ["pending", "failed"] }, next_attempt_at: { lte: now.toISOString() } }, { orderBy: "next_attempt_at", limit });
  let sent = 0;
  let failed = 0;
  let skipped = 0;
  const latest = due.length ? await latestConsentByHash(store) : new Map<string, string>();
  for (const row of due) {
    const stillOk = latest.get(row.email_hash) === "ad_tracking";
    if (!stillOk) {
      await store.update("conversion_outbox", row.id, { status: "skipped", last_error: "consent withdrawn" });
      skipped++;
      continue;
    }
    if (await dispatch(store, row, now)) sent++;
    else failed++;
  }
  return { sent, failed, skipped };
}

/** The outbox keeps only the email hash, so match consent rows by hash (newest wins). */
async function latestConsentByHash(store: Store): Promise<Map<string, string>> {
  const rows = await store.find("consent_log", { kind: { in: ["ad_tracking", "do_not_sell_share"] } }, { orderBy: "created_at", desc: true });
  const out = new Map<string, string>();
  const at = new Map<string, string>();
  for (const r of rows) {
    const h = emailHash(r.email);
    if (!out.has(h)) {
      out.set(h, r.kind);
      at.set(h, r.created_at);
    } else if (at.get(h) === r.created_at && r.kind === "do_not_sell_share") {
      out.set(h, r.kind); // a tie goes to the withdrawal
    }
  }
  return out;
}

export { hasAdConsent, AD_CONSENT_TEXT, recordAdConsent, withdrawAdConsent } from "./consent";
export { CONVERSION_EVENTS, type ConversionEvent } from "./adapters";
