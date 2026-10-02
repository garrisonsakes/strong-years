/**
 * The launch sequence: after checkout opens, confirmed waitlisters get at most
 * 3 emails and 2 pushes, all inside the first 72 hours, then nothing more.
 *
 *   e1 at +0h, e2 at +24h, e3 at +66h   (emails; >= 12h apart per person)
 *   p1 at +0h, p2 at +47h               (pushes; only to devices that opted in,
 *                                         09:00–20:00 in DISPLAY_TZ, >= 12h apart)
 *
 * Idempotent under double or overlapping cron runs: each (person, step) is claimed
 * by inserting a launch_sends row with a unique key before anything is sent; the
 * loser of a race gets a duplicate-key error and sends nothing. A step that was
 * missed (cron down) is skipped, never bunched up with the next one.
 * Stops for anyone who unsubscribed or already joined.
 *
 * Every link goes to /join carrying the person's own signed visitor id (sy_v), so
 * the sticky cell (Shopify: the $7 / $12 / $15 books or "$12 = books + first month";
 * Stripe: founding $25 / $30) they were in at signup is the one they see on any device. Prices in the copy come from
 * lib/livePricing.ts, the same source checkout charges from.
 */
import { assignArm, resolveFoundingOffer, type FoundingOffer } from "./blitz";
import { blitz, env, offerRules, prices } from "./config";
import type { Store } from "./db/store";
import type { Arm, LaunchSend, WaitlistEntry } from "./db/types";
import { grantsAccess } from "./entitlement";
import { foundingTaken } from "./founding";
import { anchorLiveSince, type LaunchState } from "./launch";
import { livePrices, shopifyLivePrices, type ShopifyLivePrices } from "./livePricing";
import { isShopify } from "./billing/provider";
import { catalog, resolveFrontEnd, type FrontEnd } from "./billing/shopify";
import { money } from "./pricing";
import { sendPushToWaitlister, vapid } from "./push";
import { sendEmail } from "./notify";
import { signVid } from "./vid";
import { waitlistLinks } from "./waitlist";

export const LAUNCH_WINDOW_HOURS = 72;
export const MIN_GAP_HOURS = 12;

export interface LaunchStep {
  key: "e1" | "e2" | "e3" | "p1" | "p2";
  channel: "email" | "push";
  atHours: number;
}

export const LAUNCH_STEPS: LaunchStep[] = [
  { key: "e1", channel: "email", atHours: 0 },
  { key: "p1", channel: "push", atHours: 0 },
  { key: "e2", channel: "email", atHours: 24 },
  { key: "p2", channel: "push", atHours: 47 },
  { key: "e3", channel: "email", atHours: 66 },
];

/** The step to send now for one channel, or null (pure; unit tested). */
export function nextStep(channel: "email" | "push", elapsedHours: number, sent: Pick<LaunchSend, "step" | "created_at">[], now: Date): LaunchStep | null {
  if (elapsedHours < 0 || elapsedHours >= LAUNCH_WINDOW_HOURS) return null;
  const steps = LAUNCH_STEPS.filter((s) => s.channel === channel);
  const mine = sent.filter((x) => steps.some((s) => s.key === x.step));
  const last = mine.map((x) => x.created_at).sort().at(-1);
  if (last && now.getTime() - new Date(last).getTime() < MIN_GAP_HOURS * 3600_000) return null;
  // The latest step that's due; earlier ones that were missed are skipped.
  const due = steps.filter((s) => s.atHours <= elapsedHours);
  const latest = due.at(-1);
  if (!latest || mine.some((x) => x.step === latest.key)) return null;
  // Never go back in the sequence (e.g. e2 after e3 was already sent).
  const idx = steps.indexOf(latest);
  if (mine.some((x) => steps.findIndex((s) => s.key === x.step) > idx)) return null;
  return latest;
}

export function inPushHours(now: Date, tz = env.displayTimeZone): boolean {
  const h = Number(new Intl.DateTimeFormat("en-US", { timeZone: tz, hour: "2-digit", hourCycle: "h23" }).format(now));
  return h >= 9 && h < 20;
}

/** The person's own cell, from their signup visitor id (same rules as lib/request.ts). */
export function offerForVisitor(vid: string | null, claimed: number): { arm: Arm; offer: FoundingOffer } {
  const offer = resolveFoundingOffer({
    visitorId: vid,
    claimed,
    cap: offerRules.foundingCap,
    testOn: blitz.enabled && blitz.priceTestOn,
    cells: blitz.priceCells,
    defaultCents: blitz.enabled ? blitz.defaultPriceCents : prices.founding,
    standardCents: blitz.enabled ? blitz.standardPriceCents : prices.founding,
  });
  const arm: Arm = !blitz.trialArmEnabled ? "B" : vid ? assignArm(vid, offerRules.armBShare) : "B";
  return { arm, offer };
}

export function priceLine(_arm: Arm, offer: FoundingOffer): string {
  // CANON UPDATE 2: no $1 trial, so every cell gets the charge-today wording (arm is kept for the signature).
  const p = money(livePrices(offer).memberCents);
  return offer.founding
    ? `Founding membership: ${p} today for your first month, then ${p} a month, locked for as long as you stay subscribed. 14-day money-back guarantee.`
    : `Membership: ${p} today for your first month, then ${p} a month until you cancel. 14-day money-back guarantee.`;
}

/** Shopify mode: the person's own front-end cell, priced from the catalog rows /join sends them to. */
export function shopifyPriceLine(fe: FrontEnd | null, live: ShopifyLivePrices): string {
  const m = money(live.memberCents);
  const lock = live.cohortOpen ? ", locked for as long as you stay subscribed" : " until you cancel";
  const kind = live.cohortOpen ? "founding membership" : "membership";
  if (fe && fe.row.entitlement !== "ebook" && fe.row.recurring_cents && fe.row.trial_days) {
    const r = money(fe.row.recurring_cents);
    return `${money(live.booksCents ?? 1200)} today gets you the starter books (the 7-Day Strength Reset and Sun Yoon's Strong Kitchen, yours to keep) and a ${fe.row.trial_days}-day trial of the ${kind}: $0 today, then ${r} on day ${fe.row.trial_days} and ${r} a month${lock}. Cancel online anytime, before the first charge too. 14-day money-back guarantee on the first membership charge.`;
  }
  if (fe && fe.row.entitlement !== "ebook" && fe.row.recurring_cents) {
    return `${money(fe.row.price_cents)} today gets you the starter books (the 7-Day Strength Reset and Sun Yoon's Strong Kitchen, yours to keep) and your first month of the ${kind}. Then ${money(fe.row.recurring_cents)} a month${lock}. 14-day money-back guarantee on the membership.`;
  }
  const books = fe ? money(fe.row.price_cents) : null;
  return `${books ? `The starter books (the 7-Day Strength Reset and Sun Yoon's Strong Kitchen, yours to keep): ${books}.` : "The starter books are the first step."} Right after paying, you can add the ${kind} with one tap, no second card entry: ${m} for your first month, then ${m} a month${lock}. 14-day money-back guarantee on the membership.`;
}

export async function launchLink(entry: Pick<WaitlistEntry, "visitor_id">, step: string, medium: "email" | "push"): Promise<string> {
  const q = new URLSearchParams();
  if (entry.visitor_id) q.set("sy_v", await signVid(entry.visitor_id, env.sessionSecret));
  q.set("utm_source", "waitlist");
  q.set("utm_medium", medium);
  q.set("utm_campaign", "launch");
  q.set("utm_content", step);
  return `/join?${q.toString()}`;
}

function emailCopy(step: "e1" | "e2" | "e3", entry: WaitlistEntry, line: string, link: string, count: { claimed: number; cap: number }) {
  const hi = entry.first_name ? `${entry.first_name}, ` : "";
  const cancel = "Cancel online anytime, in two screens at most.";
  if (step === "e1") {
    return {
      subject: "Strong Years is open. You're hearing first.",
      text: [
        `${hi}checkout is open. Everyone on the waitlist gets this email at the same moment, before we tell anyone else.`,
        line,
        `Join here: ${link}`,
        "What you get: your Daily Practice with Chang Yin, 8 to 12 minutes a day at your level, with a chair version of everything. Sun Yoon's recipes every Sunday. A Strength Age you retest every month.",
        cancel,
        "— Chang Yin (AI character)",
      ].join("\n\n"),
    };
  }
  if (step === "e2") {
    return {
      subject: "What your first week looks like",
      text: [
        `${hi}here's the first week, so you know what you'd be signing up for.`,
        "Monday: legs first. Tuesday: the gentlest mobility day. Wednesday: balance at the counter. Thursday: upper body and grip. Friday: breath and qigong. Saturday: a walk. Sunday: rest, stretch, and Sun Yoon's new recipes.",
        "Every session has a chair version and a stop rule. If a day is bad, the low-energy version counts.",
        line,
        `Your link: ${link}`,
        "— Chang Yin (AI character)",
      ].join("\n\n"),
    };
  }
  return {
    subject: "The last launch email",
    text: [
      `${hi}this is the last email in the launch series. After this we won't write again unless you join or ask us to.`,
      `Founding membership is open to the first ${count.cap.toLocaleString("en-US")} members. Right now ${count.claimed.toLocaleString("en-US")} of ${count.cap.toLocaleString("en-US")} founding spots are claimed. That's a live count from our member database, not a countdown.`,
      line,
      `If you'd like it: ${link}`,
      "— Sun Yoon (AI character)",
    ].join("\n\n"),
  };
}

const PUSH_COPY: Record<"p1" | "p2", { title: string; body: string }> = {
  p1: { title: "Strong Years is open", body: "You're on the waitlist, so you're hearing first. Tap to see your founding price." },
  p2: { title: "Checkout is still open", body: "A reminder from Chang Yin. Tap to see the founding membership. This is the last notification." },
};

async function hasJoined(store: Store, entry: WaitlistEntry, now: Date): Promise<boolean> {
  if (entry.member_id || entry.converted_at) return true;
  const member = await store.findOne("members", { email: entry.email });
  if (!member) return false;
  const rows = await store.find("memberships", { member_id: member.id });
  const joined = rows.some((m) => m.plan !== "gift" && (grantsAccess(m, now.getTime()) || m.status === "trialing"));
  if (joined) await store.updateWhere("waitlist", { id: entry.id, member_id: null }, { member_id: member.id, converted_at: now.toISOString() });
  return joined;
}

async function claim(store: Store, waitlistId: string, step: LaunchStep): Promise<LaunchSend | null> {
  try {
    return await store.insert("launch_sends", { waitlist_id: waitlistId, step: step.key, channel: step.channel, status: "claimed", sent_at: null });
  } catch {
    return null; // someone else (a concurrent run) already took this step
  }
}

export interface LaunchRunResult {
  state: Pick<LaunchState, "live" | "reason"> & { liveSince: string | null };
  elapsedHours: number | null;
  emails: number;
  pushes: number;
  skippedJoined: number;
  done: boolean;
}

export async function runLaunchSequence(store: Store, now = new Date(), batch = 500): Promise<LaunchRunResult> {
  const state = await anchorLiveSince(store, now);
  const base = { state: { live: state.live, reason: state.reason, liveSince: state.liveSince?.toISOString() ?? null }, emails: 0, pushes: 0, skippedJoined: 0 };
  if (!state.live || !state.liveSince) return { ...base, elapsedHours: null, done: false };
  const elapsedHours = (now.getTime() - state.liveSince.getTime()) / 3600_000;
  if (elapsedHours >= LAUNCH_WINDOW_HOURS) return { ...base, elapsedHours, done: true };

  const entries = await store.find("waitlist", { status: "confirmed" }, { orderBy: "created_at" });
  const allSends = await store.find("launch_sends");
  const byEntry = new Map<string, LaunchSend[]>();
  for (const s of allSends) byEntry.set(s.waitlist_id, [...(byEntry.get(s.waitlist_id) ?? []), s]);
  const claimed = await foundingTaken(store, now);
  const count = { claimed, cap: offerRules.foundingCap };
  const pushOk = inPushHours(now);
  const shop = isShopify();
  const rows = shop ? await catalog(store) : [];
  const shopLive = shopifyLivePrices(rows, claimed < offerRules.foundingCap);
  let processed = 0;
  let emails = 0;
  let pushes = 0;
  let skippedJoined = 0;

  for (const entry of entries) {
    if (processed >= batch) break;
    const sent = byEntry.get(entry.id) ?? [];
    const email = nextStep("email", elapsedHours, sent, now);
    const push = pushOk ? nextStep("push", elapsedHours, sent, now) : null;
    if (!email && !push) continue;
    processed++;
    if (await hasJoined(store, entry, now)) {
      skippedJoined++;
      continue;
    }
    const { arm, offer } = offerForVisitor(entry.visitor_id, claimed);
    const line = shop ? shopifyPriceLine(resolveFrontEnd(rows, { visitorId: entry.visitor_id, cohortOpen: shopLive.cohortOpen }), shopLive) : priceLine(arm, offer);
    if (email) {
      const row = await claim(store, entry.id, email);
      if (row) {
        const link = `${env.siteUrl}${await launchLink(entry, email.key, "email")}`;
        const copy = emailCopy(email.key as "e1" | "e2" | "e3", entry, line, link, count);
        const links = waitlistLinks(entry, now.getTime());
        const res = await sendEmail({ to: entry.email, from: email.key === "e3" ? "sun" : "chang", template: `WL_launch_${email.key}`, subject: copy.subject, text: copy.text, manageLine: `Leave the waitlist (stops every launch email): ${links.unsubscribe}` });
        const ok = res.status === "sent" || res.status === "stubbed";
        // A provider failure releases the claim so the next run retries (the provider didn't take it).
        if (ok) await store.update("launch_sends", row.id, { status: "sent", sent_at: now.toISOString() });
        else await store.remove("launch_sends", { id: row.id });
        if (ok) emails++;
      }
    }
    if (push && (await store.count("waitlist_push", { waitlist_id: entry.id })) > 0) {
      const row = await claim(store, entry.id, push);
      if (row) {
        const url = await launchLink(entry, push.key, "push");
        const n = await sendPushToWaitlister(store, entry.id, { ...PUSH_COPY[push.key as "p1" | "p2"], url, tag: "launch" }, `WL_launch_${push.key}`);
        await store.update("launch_sends", row.id, { status: "sent", sent_at: now.toISOString() });
        if (n > 0 || !vapid().configured) pushes++;
      }
    }
  }
  return { ...base, elapsedHours, emails, pushes, skippedJoined, done: false };
}
