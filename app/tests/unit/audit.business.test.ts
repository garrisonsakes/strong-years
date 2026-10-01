/**
 * Regression tests for the app-side items of AUDIT_BUSINESS.md
 * (F08 refund abuse, F09 text CANCEL, F10/F11 reminders, F12/F23 privacy & events).
 * F14 (NY re-disclosure, honest on-call hours) is in C2.chat-failclosed.test.ts.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { refundMembership } from "@/lib/billing/actions";
import { lastAnniversary, runAnnualNotices, runReminders } from "@/lib/billing/clock";
import { entitledDownloads } from "@/lib/products";
import { quoteCheckout } from "@/lib/pricing";
import { upsertMember } from "@/lib/members";
import { trackMetaEvent } from "@/lib/analytics/meta";
import { billingMembership } from "@/lib/auth/server";

const DAY = 86_400_000;
let store: MemoryStore;
const saved = { ...process.env };
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
  vi.restoreAllMocks();
});

const base: StartCheckoutInput = {
  offer: "founding",
  arm: "B",
  gentle: false,
  email: "biz@example.com",
  firstName: "Biz",
  phone: "",
  smsConsent: false,
  autoRenewConsent: true,
  ageConsent: true,
  gift: null,
  attribution: null,
  leadId: null,
  ip: null,
  userAgent: null,
};

async function join(email: string, extra: Partial<StartCheckoutInput> = {}) {
  const r = await startCheckout(store, { ...base, email, ...extra });
  if (!r.ok) throw new Error(JSON.stringify(r.errors));
  await handleStripeEvent(store, { id: `evt_${r.intentId}`, type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId }, payment_status: "paid", subscription: `sub_${r.intentId.slice(0, 6)}` } } });
  const member = (await store.findOne("members", { email }))!;
  return { member, m: (await billingMembership(member.id))! };
}

describe("F08 refund abuse", () => {
  it("F08: the printable program book vests on day 15; sessions are available now", () => {
    const now = Date.now();
    const m = { arm: "B" as const, price_cents: 2500, founding: true, status: "active" as const, plan: "monthly" as const, guarantee_until: new Date(now + 14 * DAY).toISOString() };
    const book = entitledDownloads({ id: "x" }, m, [], now).find((d) => d.file.startsWith("daily_practice"))!;
    expect(book.lockedUntil).toBe(m.guarantee_until);
    expect(entitledDownloads({ id: "x" }, m, [], now + 15 * DAY).find((d) => d.file.startsWith("daily_practice"))!.lockedUntil).toBeUndefined();
    // Bought add-ons are never locked.
    expect(entitledDownloads({ id: "x" }, m, [{ offer_code: "reset", kind: "bump", status: "paid" }], now).find((d) => d.file.startsWith("strength_reset"))!.lockedUntil).toBeUndefined();
  });

  it("F08: one money-back guarantee per person (email)", async () => {
    const first = await join("twice@example.com");
    expect((await refundMembership(store, first.m)).ok).toBe(true);
    // Rejoining signed in as themself (NEW-1: an unauthenticated repeat purchase would be pending).
    const second = await join("twice@example.com", { authMemberId: first.member.id });
    const r = await refundMembership(store, second.m);
    expect(r.ok).toBe(false);
    expect(r.state).toBe("review");
    expect(await store.count("support_tickets", { reason: "refund_review" })).toBe(1);
  });

  it("F08: one money-back guarantee per person (same card, new email)", async () => {
    const a = await join("card1@example.com");
    await store.update("members", a.member.id, { card_fingerprint: "fp_same" });
    expect((await refundMembership(store, a.m)).ok).toBe(true);
    const b = await join("card2@example.com");
    await store.update("members", b.member.id, { card_fingerprint: "fp_same" });
    expect((await refundMembership(store, b.m)).state).toBe("review");
  });

  it("F08: the self-serve refund leaves add-ons alone (their own terms)", async () => {
    const { m } = await join("bumps@example.com", { bumps: ["reset", "wallplan"] });
    const r = await refundMembership(store, m);
    expect(r.refundedCents).toBe(m.price_cents);
    expect(await store.count("sy_orders", { kind: "bump", status: "paid" })).toBe(2);
  });
});

describe("F09 'text CANCEL' only when texting works", () => {
  it("F09: checkout terms offer text CANCEL only with SMS_ENABLED", () => {
    const q = (sms: boolean) => quoteCheckout({ offer: "founding", arm: "B", now: new Date(), gentle: false, timeZone: "America/Los_Angeles", domain: "x", foundingCents: 2500, cohortOpen: true, standardCents: 3500, smsOn: sms }).terms.join(" ");
    expect(q(false)).not.toMatch(/CANCEL/);
    // R5-7: no "reply cancel" promise anywhere; email is described honestly (a person, one business day)
    expect(q(false)).not.toMatch(/replying "cancel"|reply "cancel"/);
    expect(q(false)).toMatch(/one business day/);
    expect(q(true)).toMatch(/texting CANCEL/);
  });
  it("F09: the welcome email doesn't offer text CANCEL while SMS is off", async () => {
    await join("welcome@example.com");
    const mail = (await store.findOne("outbox", { template: "E1_welcome_terms" }))!;
    expect(mail.body).not.toMatch(/text CANCEL/);
  });
});

describe("F10/F11 reminders", () => {
  it("F10: terms promise a reminder before every charge, and the job sends one before every renewal", async () => {
    const q = quoteCheckout({ offer: "founding", arm: "B", now: new Date(), gentle: false, timeZone: "America/Los_Angeles", domain: "x", foundingCents: 2500, cohortOpen: true, standardCents: 3500 });
    expect(q.terms.join(" ")).toMatch(/48 hours before every charge/);
    const { m } = await join("every@example.com");
    for (let i = 0; i < 3; i++) {
      await store.update("memberships", m.id, { current_period_end: new Date(Date.now() + (30 + i) * 3_600_000).toISOString() });
      expect((await runReminders(store)).sent).toBeGreaterThanOrEqual(1);
    }
  });
  it("F11: monthly members get a yearly notice on each anniversary, once", async () => {
    const member = await upsertMember(store, { email: "year@example.com", firstName: "Y" });
    const started = new Date(Date.now() - 366 * DAY);
    await store.insert("memberships", { member_id: member.id, plan: "monthly", arm: "B", offer_code: "founding", price_cents: 2500, interval: "month", status: "active", founding: true, stripe_subscription_id: null, trial_end: null, current_period_end: new Date(Date.now() + 20 * DAY).toISOString(), first_paid_at: started.toISOString(), guarantee_until: null, cancel_at_period_end: false, canceled_at: null, paused_until: null, partner_seat: false, is_demo: false });
    expect(lastAnniversary({ first_paid_at: started.toISOString(), created_at: started.toISOString() }, new Date())).not.toBeNull();
    expect(await runAnnualNotices(store)).toBe(1);
    expect(await runAnnualNotices(store)).toBe(0);
    const mail = (await store.findOne("outbox", { template: "ca_annual_notice" }))!;
    expect(mail.body).toMatch(/cancel/);
  });
});

describe("F12/F23 privacy and ad events", () => {
  it("F12: the gut & energy quiz sends nothing to Meta; Strength Age sends a neutral Lead", async () => {
    vi.doMock("next/headers", () => ({ cookies: async () => ({ get: () => undefined }), headers: async () => ({ get: () => null }) }));
    vi.resetModules();
    const { setStoreForTests: setS } = await import("@/lib/db");
    setS(store);
    const { POST } = await import("@/app/api/leads/route");
    const post = (quiz: string, email: string, answers: Record<string, unknown>) =>
      POST(new Request("http://localhost/api/leads", { method: "POST", body: JSON.stringify({ quiz, answers, firstName: "Q", email }) }));
    await post("gut_energy", "gut@example.com", { redFlags: [], ageBand: 2 });
    expect(await store.count("analytics_events", { name: "Lead" })).toBe(0);
    await post("strength_age", "sa@example.com", { taker: "self", sex: "woman", age: 70 });
    const lead = (await store.findOne("analytics_events", { name: "Lead" }))!;
    expect(String(lead.payload.event_source_url)).toMatch(/\/q\/a$/);
    expect(JSON.stringify(lead.payload)).not.toMatch(/gut|quiz_b|strength/i);
    vi.doUnmock("next/headers");
  });

  it("F12: a Do Not Sell/Share or GPC opt-out means nothing is sent to Meta", async () => {
    process.env.META_PIXEL_ID = "1";
    process.env.META_CAPI_TOKEN = "t";
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}", { status: 200 }));
    await trackMetaEvent({ name: "Purchase", eventId: "e", sourcePath: "/checkout", email: "a@b.c", attribution: { ad_opt_out: true } }, "https://x");
    const member = await upsertMember(store, { email: "opt@example.com", firstName: "O" });
    await store.update("members", member.id, { ad_opt_out: true });
    await trackMetaEvent({ name: "Subscribe", eventId: "e2", sourcePath: "/app", email: member.email, memberId: member.id }, "https://x");
    expect(spy).not.toHaveBeenCalled();
    expect(await store.count("analytics_events", { sent_to_meta: false })).toBe(2);
  });
});
