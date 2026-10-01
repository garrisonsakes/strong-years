/**
 * Web push (AUDIT_BUSINESS F17): the retention nudge until SMS is approved.
 * VAPID keys come from env (VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_SUBJECT).
 * Without them every push is written to the outbox as "stubbed", so the flows
 * are testable end to end. Messages never carry health details.
 */
import webpush from "web-push";
import { env } from "./config";
import type { Store } from "./db/store";
import type { Member, PushSubscriptionRow } from "./db/types";
import { grantsAccess, pickBillingMembership } from "./entitlement";

export interface PushPayload {
  title: string;
  body: string;
  /** Same-origin path the notification opens. */
  url: string;
  tag?: string;
}

export function vapid() {
  const publicKey = process.env.VAPID_PUBLIC_KEY ?? "";
  const privateKey = process.env.VAPID_PRIVATE_KEY ?? "";
  const subject = process.env.VAPID_SUBJECT ?? `mailto:${env.supportEmail}`;
  return { publicKey, privateKey, subject, configured: Boolean(publicKey && privateKey) };
}

export interface IncomingSubscription {
  endpoint?: unknown;
  keys?: { p256dh?: unknown; auth?: unknown };
}

/** Validates a browser PushSubscription.toJSON() before we store it. */
export function parseSubscription(raw: IncomingSubscription): { endpoint: string; p256dh: string; auth: string } | null {
  const endpoint = typeof raw?.endpoint === "string" ? raw.endpoint : "";
  const p256dh = typeof raw?.keys?.p256dh === "string" ? raw.keys.p256dh : "";
  const auth = typeof raw?.keys?.auth === "string" ? raw.keys.auth : "";
  if (!/^https:\/\/[a-z0-9.-]+(:\d+)?\//i.test(endpoint) || endpoint.length > 1024) return null;
  if (!/^[A-Za-z0-9_-]{40,200}$/.test(p256dh) || !/^[A-Za-z0-9_-]{10,64}$/.test(auth)) return null;
  return { endpoint, p256dh, auth };
}

export async function saveSubscription(store: Store, memberId: string, sub: { endpoint: string; p256dh: string; auth: string }, userAgent: string | null) {
  const existing = await store.findOne("push_subscriptions", { endpoint: sub.endpoint });
  if (existing) return store.update("push_subscriptions", existing.id, { member_id: memberId, p256dh: sub.p256dh, auth: sub.auth, failures: 0, user_agent: userAgent });
  return store.insert("push_subscriptions", { member_id: memberId, ...sub, user_agent: userAgent, failures: 0, last_sent_at: null });
}

/** Test seam: replace the network call. */
type Sender = (sub: PushSubscriptionRow, payload: string) => Promise<{ statusCode: number }>;
let senderOverride: Sender | null = null;
export function setPushSenderForTests(fn: Sender | null) {
  senderOverride = fn;
}

async function deliver(sub: PushSubscriptionRow, payload: string): Promise<{ statusCode: number }> {
  if (senderOverride) return senderOverride(sub, payload);
  const v = vapid();
  webpush.setVapidDetails(v.subject, v.publicKey, v.privateKey);
  const res = await webpush.sendNotification({ endpoint: sub.endpoint, keys: { p256dh: sub.p256dh, auth: sub.auth } }, payload, { TTL: 12 * 3600, urgency: "normal" });
  return { statusCode: res.statusCode };
}

/** Sends to every device the member subscribed. Returns how many deliveries succeeded. */
export async function sendPushToMember(store: Store, member: Pick<Member, "id" | "email">, payload: PushPayload, template: string): Promise<number> {
  const subs = await store.find("push_subscriptions", { member_id: member.id });
  if (subs.length === 0) return 0;
  const body = JSON.stringify(payload);
  const live = vapid().configured || senderOverride !== null;
  let ok = 0;
  for (const sub of subs) {
    if (!live) continue;
    try {
      const r = await deliver(sub, body);
      if (r.statusCode >= 200 && r.statusCode < 300) {
        ok++;
        await store.update("push_subscriptions", sub.id, { last_sent_at: new Date().toISOString(), failures: 0 });
      }
    } catch (err) {
      const code = (err as { statusCode?: number }).statusCode ?? 0;
      // 404/410: the browser dropped the subscription. Anything else: count and give up after 5.
      if (code === 404 || code === 410 || sub.failures >= 4) await store.remove("push_subscriptions", { id: sub.id });
      else await store.update("push_subscriptions", sub.id, { failures: sub.failures + 1 });
    }
  }
  await store.insert("outbox", {
    channel: "push",
    to: `member:${member.id}`,
    subject: payload.title,
    body: `${payload.body} (${payload.url})`,
    template,
    provider: live ? "webpush" : "stub",
    status: live ? (ok > 0 ? "sent" : "failed") : "stubbed",
  });
  return ok;
}

function localParts(tz: string, now: Date): { date: string; hour: number; minute: number } {
  const f = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23" });
  const p = Object.fromEntries(f.formatToParts(now).map((x) => [x.type, x.value]));
  return { date: `${p.year}-${p.month}-${p.day}`, hour: Number(p.hour), minute: Number(p.minute) };
}

/**
 * Hourly: the daily-practice nudge. One per member per local day, in the hour of
 * their chosen reminder time, only between 08:00 and 20:00 local, only if they
 * haven't done today's session, and only while their membership grants access.
 */
export async function runDailyNudges(store: Store, now = new Date()): Promise<{ sent: number; checked: number }> {
  const subs = await store.find("push_subscriptions");
  const memberIds = [...new Set(subs.map((s) => s.member_id))];
  let sent = 0;
  for (const id of memberIds) {
    const member = await store.get("members", id);
    if (!member) continue;
    const rows = await store.find("memberships", { member_id: id });
    const billing = pickBillingMembership(rows, now.getTime());
    const access = rows.find((r) => grantsAccess(r, now.getTime()));
    if (!access) continue;
    const local = localParts(member.timezone || env.displayTimeZone, now);
    const [h] = (member.reminder_time || "07:30").split(":").map(Number);
    const nudgeHour = Math.min(20, Math.max(8, h ?? 8));
    if (local.hour !== nudgeHour) continue;
    if (await store.findOne("practice_logs", { member_id: id, day: local.date })) continue;
    const key = new Date(`${local.date}T00:00:00Z`).toISOString();
    const membershipId = (billing ?? access).id;
    if (await store.findOne("reminders", { membership_id: membershipId, kind: "daily_nudge", charge_at: key })) continue;
    const n = await sendPushToMember(store, member, { title: "Your 8 minutes with Chang Yin", body: "Today's session is ready. A chair version is there if you need it.", url: "/app", tag: "daily" }, "push_daily_nudge");
    await store.insert("reminders", { membership_id: membershipId, kind: "daily_nudge", charge_at: key, sent_at: now.toISOString() });
    if (n > 0 || !vapid().configured) sent++;
  }
  return { sent, checked: memberIds.length };
}

/**
 * Organic launch: push to a confirmed waitlister's devices (waitlist_push, with
 * its own consent). Same delivery and pruning rules as members' reminders.
 */
export async function sendPushToWaitlister(store: Store, waitlistId: string, payload: PushPayload, template: string): Promise<number> {
  const subs = await store.find("waitlist_push", { waitlist_id: waitlistId });
  if (subs.length === 0) return 0;
  const body = JSON.stringify(payload);
  const live = vapid().configured || senderOverride !== null;
  let ok = 0;
  for (const sub of subs) {
    if (!live) continue;
    try {
      const r = await deliver(sub as unknown as PushSubscriptionRow, body);
      if (r.statusCode >= 200 && r.statusCode < 300) ok++;
    } catch (err) {
      const code = (err as { statusCode?: number }).statusCode ?? 0;
      if (code === 404 || code === 410 || sub.failures >= 4) await store.remove("waitlist_push", { id: sub.id });
      else await store.update("waitlist_push", sub.id, { failures: sub.failures + 1 });
    }
  }
  await store.insert("outbox", {
    channel: "push",
    to: `waitlist:${waitlistId}`,
    subject: payload.title,
    body: `${payload.body} (${payload.url})`,
    template,
    provider: live ? "webpush" : "stub",
    status: live ? (ok > 0 ? "sent" : "failed") : "stubbed",
  });
  return ok;
}
