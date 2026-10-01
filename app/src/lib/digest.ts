/**
 * The 7am digest: once per Eastern-time day, at or after 07:00 ET, one email to
 * DIGEST_EMAIL (or ONCALL_EMAIL) with today's numbers and the open exceptions.
 * Idempotent: the day is claimed in digest_runs (unique) before anything is sent,
 * so a second cron call, a retry or a second instance sends nothing.
 */
import type { Store } from "./db/store";
import { openExceptions, syncAppExceptions, TYPE_LABEL } from "./exceptions";
import { moneyExact } from "./pricing";
import { computeToday } from "./today";
import { env } from "./config";
import type { EmailInput } from "./notify";

export const DIGEST_TZ = "America/New_York";
export const DIGEST_HOUR = 7;

export function easternDayAndHour(now: Date): { day: string; hour: number } {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone: DIGEST_TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23" }).formatToParts(now);
  const get = (t: string) => parts.find((p) => p.type === t)?.value ?? "";
  return { day: `${get("year")}-${get("month")}-${get("day")}`, hour: Number(get("hour")) % 24 };
}

export type DigestResult = { status: "sent" | "not_yet" | "already_sent" | "no_recipient" | "failed"; day: string };

export async function runDigest(store: Store, now = new Date(), send?: (i: EmailInput) => Promise<unknown>, fetcher?: typeof fetch): Promise<DigestResult> {
  const { day, hour } = easternDayAndHour(now);
  if (hour < DIGEST_HOUR) return { status: "not_yet", day };
  const to = process.env.DIGEST_EMAIL || process.env.ONCALL_EMAIL || "";
  if (!to) return { status: "no_recipient", day };
  if (await store.findOne("digest_runs", { day })) return { status: "already_sent", day };
  let claim;
  try {
    claim = await store.insert("digest_runs", { day, status: "claimed", sent_at: null });
  } catch {
    return { status: "already_sent", day };
  }
  try {
    await syncAppExceptions(store);
    const t = await computeToday(store, now, fetcher);
    const open = await openExceptions(store);
    const pct = (v: number | null) => (v === null ? "no data yet" : `${(v * 100).toFixed(1)}%`);
    const lines = [
      `Strong Years, ${day} (07:00 ET digest)`,
      "",
      `Reach 24 h: ${t.reach_24h === null ? `not connected (${t.workers.error ?? "no data"})` : t.reach_24h.toLocaleString("en-US")}`,
      `Waitlist confirmed: ${t.waitlist.confirmed} (+${t.waitlist.new24h} in 24 h)`,
      `Book buyers: ${t.buyers.books} (+${t.buyers.new24h})`,
      `Paying members: ${t.members.paying} (+${t.members.new24h})`,
      `MRR: ${moneyExact(t.mrr.total)} · 30 days new ${moneyExact(t.mrr.new30d)}, lost ${moneyExact(t.mrr.lost30d)}, net ${moneyExact(t.mrr.net30d)}`,
      `Renewal 1: ${pct(t.renewal1.rate)} (${t.renewal1.renewed} of ${t.renewal1.due})`,
      `Refunds 30 days: ${t.refunds.count30d} (${moneyExact(t.refunds.cents30d)}) · chargebacks ${t.chargebacks.count30d} (ratio ${pct(t.chargebacks.ratio30d)})`,
      `Founding seats: ${t.founding.claimed} of ${t.founding.cap}`,
      `Governor: ${t.workers.governor ? `${t.workers.governor.status}, spend switch ${t.workers.governor.spend_enabled ? "on" : "off"}, planned $${t.workers.governor.planned_daily_usd.toFixed(2)}` : "no plan (workers not connected or no data)"}`,
      "",
      `Top posts: ${t.top.slice(0, 5).map((p) => p.post_id).join(", ") || "none with data yet"}`,
      "",
      `Open exceptions: ${open.length}`,
      ...open.slice(0, 20).map((x) => `- [${x.severity}] ${TYPE_LABEL[x.type]}: ${x.title}`),
      "",
      `Decide them: ${env.siteUrl}/admin/exceptions · Today: ${env.siteUrl}/admin/today`,
    ];
    const doSend = send ?? (async (i: EmailInput) => (await import("./notify")).sendEmail(i));
    await doSend({ to, subject: `Strong Years digest ${day}: ${open.length} open, MRR ${moneyExact(t.mrr.total)}`, text: lines.join("\n"), template: "ops_digest", manageLine: "Internal operations email." });
    await store.update("digest_runs", claim.id, { status: "sent", sent_at: now.toISOString() });
    return { status: "sent", day };
  } catch (e) {
    console.error("digest failed", (e as Error).message);
    await store.update("digest_runs", claim.id, { status: "failed" });
    return { status: "failed", day };
  }
}
