/** AUDIT_BUSINESS F17: web push reminders (PWA) until SMS is approved. */
import { createECDH, randomBytes } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import webpush from "web-push";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { parseSubscription, runDailyNudges, saveSubscription, sendPushToMember, setPushSenderForTests } from "@/lib/push";
import { runReminders } from "@/lib/billing/clock";
import { upsertMember } from "@/lib/members";
import type { Member } from "@/lib/db/types";

const b64u = (b: Buffer) => b.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
function browserSub(n = 1) {
  const ecdh = createECDH("prime256v1");
  ecdh.generateKeys();
  return { endpoint: `https://fcm.googleapis.com/fcm/send/device-${n}`, keys: { p256dh: b64u(ecdh.getPublicKey()), auth: b64u(randomBytes(16)) } };
}

let store: MemoryStore;
const saved = { ...process.env };
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});
afterEach(() => {
  setPushSenderForTests(null);
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

async function entitledMember(tz = "America/New_York", reminder = "09:00"): Promise<Member> {
  const m = await upsertMember(store, { email: `p${Math.random()}@example.com`, firstName: "Pia" });
  await store.update("members", m.id, { timezone: tz, reminder_time: reminder });
  await store.insert("memberships", { member_id: m.id, plan: "monthly", arm: "B", offer_code: "founding", price_cents: 2500, interval: "month", status: "active", founding: true, stripe_subscription_id: null, trial_end: null, current_period_end: new Date(Date.now() + 20 * 86_400_000).toISOString(), first_paid_at: new Date().toISOString(), guarantee_until: null, cancel_at_period_end: false, canceled_at: null, paused_until: null, partner_seat: false, pending_verification: false, is_demo: false });
  const sub = parseSubscription(browserSub())!;
  await saveSubscription(store, m.id, sub, "vitest");
  return (await store.get("members", m.id))!;
}

describe("F17 web push", () => {
  it("F17: validates browser subscriptions before storing them", () => {
    expect(parseSubscription(browserSub())).not.toBeNull();
    expect(parseSubscription({ endpoint: "http://insecure.example/x", keys: browserSub().keys })).toBeNull();
    expect(parseSubscription({ endpoint: "https://fcm.googleapis.com/x", keys: { p256dh: "short", auth: "x" } })).toBeNull();
    expect(parseSubscription({})).toBeNull();
  });

  it("F17: the real library signs with VAPID and encrypts the payload for the device", async () => {
    const keys = webpush.generateVAPIDKeys();
    const req = webpush.generateRequestDetails(browserSub(), JSON.stringify({ title: "t", body: "b", url: "/app" }), {
      vapidDetails: { subject: "mailto:help@strongyears.example", publicKey: keys.publicKey, privateKey: keys.privateKey },
    });
    expect(String(req.headers.Authorization)).toMatch(/^vapid t=/);
    expect(req.headers["Content-Encoding"]).toBe("aes128gcm");
    expect(req.body!.length).toBeGreaterThan(0);
  });

  it("F17: without VAPID keys pushes are recorded as stubbed (testable offline)", async () => {
    delete process.env.VAPID_PUBLIC_KEY;
    delete process.env.VAPID_PRIVATE_KEY;
    const m = await entitledMember();
    await sendPushToMember(store, m, { title: "x", body: "y", url: "/app" }, "test");
    expect((await store.findOne("outbox", { channel: "push" }))!.status).toBe("stubbed");
  });

  it("F17: delivers to every device, and drops devices the browser has expired (410)", async () => {
    const m = await entitledMember();
    await saveSubscription(store, m.id, parseSubscription(browserSub(2))!, "vitest");
    const calls: string[] = [];
    setPushSenderForTests(async (sub) => {
      calls.push(sub.endpoint);
      if (sub.endpoint.endsWith("device-2")) throw Object.assign(new Error("gone"), { statusCode: 410 });
      return { statusCode: 201 };
    });
    expect(await sendPushToMember(store, m, { title: "x", body: "y", url: "/app" }, "test")).toBe(1);
    expect(calls).toHaveLength(2);
    expect(await store.count("push_subscriptions", { member_id: m.id })).toBe(1);
  });

  it("F17: daily nudge at the member's reminder hour, once a day, only if today's session isn't done", async () => {
    const m = await entitledMember("America/New_York", "09:00");
    const sent: string[] = [];
    setPushSenderForTests(async (_s, payload) => (sent.push(payload), { statusCode: 201 }));
    const nineNY = new Date("2026-10-01T13:05:00Z"); // 09:05 in New York
    expect((await runDailyNudges(store, new Date("2026-10-01T12:05:00Z"))).sent).toBe(0); // 08:05: not their hour
    expect((await runDailyNudges(store, nineNY)).sent).toBe(1);
    expect((await runDailyNudges(store, new Date("2026-10-01T13:40:00Z"))).sent).toBe(0); // same day: once
    expect(JSON.parse(sent[0]!)).toMatchObject({ url: "/app" });
    // Next day, but the session is already done: no nudge.
    await store.insert("practice_logs", { member_id: m.id, day: "2026-10-02", session_key: "s", track: "steady", swap: null, minutes: 8 });
    expect((await runDailyNudges(store, new Date("2026-10-02T13:05:00Z"))).sent).toBe(0);
  });

  it("F17: no nudges for members without access, and never before 08:00 local", async () => {
    const m = await entitledMember("America/Los_Angeles", "05:30");
    setPushSenderForTests(async () => ({ statusCode: 201 }));
    expect((await runDailyNudges(store, new Date("2026-10-01T12:40:00Z"))).sent).toBe(0); // 05:40 LA
    expect((await runDailyNudges(store, new Date("2026-10-01T15:10:00Z"))).sent).toBe(1); // 08:10 LA
    await store.updateWhere("memberships", { member_id: m.id }, { status: "refunded" });
    expect((await runDailyNudges(store, new Date("2026-10-02T15:10:00Z"))).sent).toBe(0);
  });

  it("F17: the pre-renewal reminder also goes by push", async () => {
    const m = await entitledMember();
    await store.updateWhere("memberships", { member_id: m.id }, { current_period_end: new Date(Date.now() + 30 * 3_600_000).toISOString() });
    setPushSenderForTests(async () => ({ statusCode: 201 }));
    await runReminders(store);
    const push = (await store.findOne("outbox", { channel: "push", template: "push_pre_charge" }))!;
    expect(push.body).toMatch(/\/app\/account/);
    expect(push.body).not.toMatch(/\$/); // no amounts on a lock screen
  });

  it("F17: service worker handles push and clicks (same-origin only); manifest and icons exist", () => {
    const root = path.resolve(__dirname, "../..");
    const sw = readFileSync(path.join(root, "public/sw.js"), "utf8");
    expect(sw).toMatch(/addEventListener\("push"/);
    expect(sw).toMatch(/addEventListener\("notificationclick"/);
    expect(sw).toMatch(/startsWith\("\/"\) && !data\.url\.startsWith\("\/\/"\)/);
    const manifest = JSON.parse(readFileSync(path.join(root, "public/manifest.webmanifest"), "utf8")) as { icons: { src: string }[]; start_url: string };
    expect(manifest.start_url).toBe("/app");
    for (const i of manifest.icons) expect(existsSync(path.join(root, "public", i.src))).toBe(true);
  });
});
