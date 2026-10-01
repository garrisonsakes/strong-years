/**
 * Regression tests for AUDIT_CODE.md medium and low findings in app/.
 * Out of app/ scope: M4, M10 (workers), L11–L14 (n8n, workers, schema.sql).
 * M11 and M6-alerts live in C2.chat-failclosed.test.ts; M14 in M14.guards.test.ts.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { buildQuotes } from "@/lib/checkoutQuotes";
import { resolveFoundingOffer } from "@/lib/blitz";
import { handleStripeEvent, RetryLater } from "@/lib/billing/webhook";
import { chargeUpsell, UPSELL_WINDOW_MS } from "@/lib/billing/actions";
import { runReminders } from "@/lib/billing/clock";
import { buildSessionParams } from "@/lib/billing/stripeSession";
import { hitLocal, resetRateLimits } from "@/lib/rateLimit";
import { redactSecrets, sendEmail } from "@/lib/notify";
import { createMagicLink } from "@/lib/auth/server";
import { sessionMatchesMember } from "@/lib/auth/session";
import { upsertMember } from "@/lib/members";
import { quoteCheckout, validateCheckout } from "@/lib/pricing";
import { signVid, verifyVid } from "@/lib/vid";
import { parseBasicAuth, safeEqual } from "@/lib/safeEqual";
import { loginDemoLink, loginError } from "@/lib/loginView";
import { TrendChart } from "@/components/StrengthChart";
import { PhoneSession } from "@/components/Art";
import { trackMetaEvent } from "@/lib/analytics/meta";
import type { CheckoutIntent } from "@/lib/db/types";

const DAY = 86_400_000;
let store: MemoryStore;
const saved = { ...process.env };
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  resetRateLimits();
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
  email: "m@example.com",
  firstName: "Meg",
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

const founding = () => resolveFoundingOffer({ visitorId: null, claimed: 0, cap: 5000, testOn: false, cells: [2500, 3000], defaultCents: 2500, standardCents: 3500 });

describe("M1 the terms agreed are the terms shown", () => {
  it("M1: a signed quote passes; a stale or forged one is rejected before anything is stored", async () => {
    const { quotes } = buildQuotes({ offer: "founding", arm: "B", gentle: false, founding: founding() });
    const ok = await startCheckout(store, { ...base, quoteSig: quotes[""]!.sig! });
    expect(ok.ok).toBe(true);
    const bad = await startCheckout(store, { ...base, email: "x@example.com", quoteSig: "forged" });
    expect(bad.ok).toBe(false);
    expect(!bad.ok && bad.errors[0]!.message).toMatch(/changed while this page was open/);
    const stale = buildQuotes({ offer: "founding", arm: "B", gentle: false, founding: founding(), now: new Date(Date.now() - 3 * DAY) });
    expect((await startCheckout(store, { ...base, email: "y@example.com", quoteSig: stale.quotes[""]!.sig! })).ok).toBe(false);
    expect(await store.count("checkout_intents")).toBe(1);
  });
});

describe("M2 the success URL is not a reusable login", () => {
  it("M2: it signs in once, and never after 30 minutes", async () => {
    const r = await startCheckout(store, base);
    if (!r.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: "evt_m2", type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId }, payment_status: "paid", subscription: "sub_m2" } } });
    const { GET } = await import("@/app/api/checkout/complete/route");
    const url = `http://localhost/api/checkout/complete?intent=${r.intentId}`;
    expect((await GET(new Request(url))).headers.get("set-cookie")).toMatch(/sy_session=/);
    expect((await GET(new Request(url))).headers.get("set-cookie")).toBeNull();
    const r2 = await startCheckout(store, { ...base, email: "late@example.com" });
    if (!r2.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: "evt_m2b", type: "checkout.session.completed", data: { object: { metadata: { intent_id: r2.intentId }, payment_status: "paid", subscription: "sub_m2b" } } });
    await store.update("checkout_intents", r2.intentId, { completed_at: new Date(Date.now() - 31 * 60_000).toISOString() });
    expect((await GET(new Request(`http://localhost/api/checkout/complete?intent=${r2.intentId}`))).headers.get("set-cookie")).toBeNull();
  });
});

describe("M3 partner seat item order", () => {
  it("M3: subscription.updated reads the membership item, not items[0]", async () => {
    const r = await startCheckout(store, base);
    if (!r.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: "evt_m3a", type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId }, payment_status: "paid", subscription: "sub_m3" } } });
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_m3" }))!;
    await handleStripeEvent(store, {
      id: "evt_m3b",
      type: "customer.subscription.updated",
      data: { object: { id: "sub_m3", status: "active", items: { data: [{ current_period_end: 1_900_000_000, price: { unit_amount: 800 } }, { current_period_end: 1_900_000_000, price: { unit_amount: m.price_cents } }] } } },
    });
    const after = (await store.get("memberships", m.id))!;
    expect(after.price_cents).toBe(m.price_cents);
    expect(after.partner_seat).toBe(true);
    expect(after.plan).toBe("monthly");
  });
});

describe("M5 rate limits", () => {
  it("M5: sliding window blocks the N+1th hit and admin lockout exists", () => {
    const lim = { max: 3, windowMs: 60_000 };
    expect([1, 2, 3, 4].map(() => hitLocal("k", lim, 1000))).toEqual([true, true, true, false]);
    expect(hitLocal("k", lim, 70_000)).toBe(true);
    const mw = readFileSync(path.resolve(__dirname, "../../src/middleware.ts"), "utf8");
    expect(mw).toMatch(/Too many failed attempts/);
    for (const f of ["api/leads/route.ts", "api/auth/magic/route.ts", "api/chat/route.ts", "api/events/route.ts", "api/gift/redeem/route.ts", "api/checkout/route.ts"]) {
      expect(readFileSync(path.resolve(__dirname, "../../src/app", f), "utf8"), f).toMatch(/LIMITS\./);
    }
  });
});

describe("M6 no secrets in the outbox", () => {
  it("M6: magic-link tokens, claim tokens and codes are redacted in stored messages", async () => {
    const member = await upsertMember(store, { email: "t@example.com", firstName: "T" });
    const link = await createMagicLink(member.id);
    await sendEmail({ to: member.email, subject: "x", text: `Log in: ${link}`, template: "magic_link", secrets: [link] });
    const row = (await store.findOne("outbox", { template: "magic_link" }))!;
    expect(row.body).not.toContain(link.split("token=")[1]!);
    expect(redactSecrets("go to https://x/gift/claim?token=abc123&z=1 or https://x/gift/redeem?code=ABCD-EFGH")).toBe("go to https://x/gift/claim?token=[redacted]&z=1 or https://x/gift/redeem?code=[redacted]");
    expect(redactSecrets("your code is ABCD-EFGH", ["ABCD-EFGH"])).toBe("your code is [redacted]");
  });
});

describe("M7 reminders don't depend on member-wide history", () => {
  it("M7: a returning member with old charges still gets the reminder for the new membership", async () => {
    const member = await upsertMember(store, { email: "back@example.com", firstName: "B" });
    for (let i = 0; i < 4; i++) await store.insert("sy_orders", { member_id: member.id, email: member.email, offer_code: "founding", kind: "membership_charge", description: "old", amount_cents: 2500, status: "paid", stripe_payment_intent: null, stripe_invoice: null, checkout_intent_id: null, is_demo: false });
    await store.insert("memberships", { member_id: member.id, plan: "monthly", arm: "B", offer_code: "founding", price_cents: 2500, interval: "month", status: "active", founding: true, stripe_subscription_id: null, trial_end: null, current_period_end: new Date(Date.now() + 30 * 3_600_000).toISOString(), first_paid_at: new Date().toISOString(), guarantee_until: null, cancel_at_period_end: false, canceled_at: null, paused_until: null, partner_seat: false, is_demo: false });
    expect((await runReminders(store)).sent).toBe(1);
  });
});

describe("M8 one-click upsells", () => {
  async function paidMember() {
    const r = await startCheckout(store, base);
    if (!r.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: `evt_${r.intentId}`, type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId }, payment_status: "paid", subscription: "sub_m8" } } });
    return { member: (await store.findOne("members", { email: base.email }))!, intentId: r.intentId };
  }
  it("M8: a double submit records one order", async () => {
    const { member } = await paidMember();
    const [a, b] = await Promise.all([chargeUpsell(store, member, "kit", null), chargeUpsell(store, member, "kit", null)]);
    expect(a.ok && b.ok).toBe(true);
    expect(await store.count("sy_orders", { kind: "upsell_kit" })).toBe(1);
  });
  it("M8: only within 30 minutes of a purchase", async () => {
    const { member, intentId } = await paidMember();
    await store.update("checkout_intents", intentId, { completed_at: new Date(Date.now() - UPSELL_WINDOW_MS - 1000).toISOString() });
    const r = await chargeUpsell(store, member, "program", "strong-at-70");
    expect(r.ok).toBe(false);
    expect(await store.count("sy_orders", { kind: "upsell_program" })).toBe(0);
  });
});

describe("M9 CANCEL by text confirms by email", () => {
  it("M9: a signed CANCEL opts out of texts, cancels, and emails the confirmation", async () => {
    process.env.SMS_ENABLED = "true";
    process.env.TWILIO_AUTH_TOKEN = "tok";
    const r = await startCheckout(store, { ...base, phone: "+1 555 555 0199", smsConsent: true });
    if (!r.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: "evt_m9", type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId }, payment_status: "paid", subscription: "sub_m9" } } });
    const { POST } = await import("@/app/api/sms/inbound/route");
    const { createHmac } = await import("node:crypto");
    const params = new URLSearchParams({ From: "+15555550199", Body: "CANCEL" });
    const url = "http://localhost:3000/api/sms/inbound";
    const sig = createHmac("sha1", "tok").update(url + [...params.keys()].sort().map((k) => k + params.get(k)).join("")).digest("base64");
    const res = await POST(new Request(url, { method: "POST", body: params.toString(), headers: { "x-twilio-signature": sig } }));
    expect(res.status).toBe(204);
    const member = (await store.findOne("members", { email: base.email }))!;
    expect(member.sms_opt_in).toBe(false);
    expect((await store.findOne("memberships", { member_id: member.id }))!.cancel_at_period_end).toBe(true);
    expect(await store.count("outbox", { template: "F_cancel_confirmation" })).toBe(1);
  });
});

describe("M12 leads store validated answers only", () => {
  it("M12: unknown keys are dropped and oversized bodies refused", async () => {
    vi.doMock("next/headers", () => ({ cookies: async () => ({ get: () => undefined }), headers: async () => ({ get: () => null }) }));
    vi.resetModules();
    const { setStoreForTests: setS } = await import("@/lib/db");
    setS(store);
    const { POST } = await import("@/app/api/leads/route");
    const answers = { taker: "self", sex: "woman", age: 70, chairReps: 10, junk: "x".repeat(200), nested: { a: 1 } };
    const res = await POST(new Request("http://localhost/api/leads", { method: "POST", body: JSON.stringify({ quiz: "strength_age", answers, firstName: "Lu", email: "lu@example.com" }) }));
    expect(res.status).toBe(200);
    const lead = (await store.findOne("leads", { email: "lu@example.com" }))!;
    expect(lead.answers).not.toHaveProperty("junk");
    expect(lead.answers).not.toHaveProperty("nested");
    const big = await POST(new Request("http://localhost/api/leads", { method: "POST", body: JSON.stringify({ quiz: "strength_age", answers: { pad: "x".repeat(9000) }, firstName: "Lu", email: "lu2@example.com" }) }));
    expect(big.status).toBe(413);
    vi.doUnmock("next/headers");
  });
});

describe("M13 column-level grants", () => {
  it("M13: authenticated users can only update safe member columns", () => {
    const sql = readFileSync(path.resolve(__dirname, "../../supabase/migrations/20260930120000_audit_fixes.sql"), "utf8");
    expect(sql).toMatch(/revoke update on public\.members from authenticated/);
    const grant = sql.match(/grant update \(([^)]*)\)\s+on public\.members to authenticated/)![1]!;
    for (const col of ["stripe_customer_id", "stripe_payment_method", "email", "is_demo", "session_version"]) expect(grant).not.toContain(col);
  });
});

describe("Low findings", () => {
  it("L1: the login page never renders arbitrary links or text from the URL", () => {
    expect(loginDemoLink("https://evil.example/x", { mockDb: true, siteUrl: "http://localhost:3000" })).toBeNull();
    expect(loginDemoLink("http://localhost:3000/auth/verify?token=a", { mockDb: false, siteUrl: "http://localhost:3000" })).toBeNull();
    expect(loginDemoLink("http://localhost:3000/auth/verify?token=a", { mockDb: true, siteUrl: "http://localhost:3000" })).not.toBeNull();
    expect(loginError("<script>you've been hacked")).toMatch(/expired/);
  });

  it("L2: an in-flight redelivery is deferred and a livemode mismatch is ignored", async () => {
    await store.insert("stripe_events", { id: "evt_l2", type: "invoice.paid", livemode: false, processed_at: null, claimed_at: new Date().toISOString(), error: null, summary: null });
    await expect(handleStripeEvent(store, { id: "evt_l2", type: "invoice.paid", data: { object: {} } })).rejects.toBeInstanceOf(RetryLater);
    const r = await handleStripeEvent(store, { id: "evt_live", type: "invoice.paid", livemode: true, data: { object: {} } }, { expectLivemode: false });
    expect(r.summary).toMatch(/livemode mismatch/);
  });

  it("L3: checkout never charges a configured price ID's amount; it charges the quote", () => {
    process.env.STRIPE_PRICE_RESET = "price_wrong_amount";
    process.env.STRIPE_PRICE_FOUNDING_2500 = "price_wrong";
    const q = quoteCheckout({ offer: "founding", arm: "B", bumps: ["reset"], now: new Date(), gentle: false, timeZone: "America/Los_Angeles", domain: "x", foundingCents: 2500, cohortOpen: true, standardCents: 3500 });
    const params = buildSessionParams({ id: "i", offer_code: "founding", arm: "B", trial_days: 0, email: "a@b.c", price_cell: "p2500" } as CheckoutIntent, q);
    for (const li of params.line_items!) {
      expect(li.price).toBeUndefined();
      expect(li.price_data?.unit_amount).toBeGreaterThan(0);
    }
  });

  it("L4: the founding-full message doesn't mention a trial that's switched off", () => {
    process.env.TRIAL_ARM_ENABLED = "false";
    const q = quoteCheckout({ offer: "founding", arm: "B", now: new Date(), gentle: false, timeZone: "America/Los_Angeles", domain: "x", foundingCents: 2500, cohortOpen: true, standardCents: 3500 });
    const errs = validateCheckout({ quote: q, autoRenewChecked: true, ageChecked: true, email: "a@b.co", firstName: "A", smsChecked: false, phone: "", foundingSpotsLeft: 0 });
    expect(errs.map((e) => e.message).join(" ")).not.toMatch(/\$1 trial/);
  });

  it("L5: the visitor id is signed; an edited cookie doesn't pick a price", async () => {
    const v = await signVid("abc", "secret");
    expect(await verifyVid(v, "secret")).toBe("abc");
    expect(await verifyVid(v.replace("abc", "abd"), "secret")).toBeNull();
    expect(await verifyVid("abc", "secret")).toBeNull();
  });

  it("L6: constant-time compare, and passwords containing ':' work", () => {
    expect(safeEqual("a", "a")).toBe(true);
    expect(safeEqual("a", "ab")).toBe(false);
    expect(parseBasicAuth(`Basic ${btoa("admin:pa:ss")}`)).toEqual({ user: "admin", pass: "pa:ss" });
  });

  it("L7: bumping session_version revokes older sessions", () => {
    expect(sessionMatchesMember({ v: 1 }, { session_version: 1 })).toBe(true);
    expect(sessionMatchesMember({ v: 1 }, { session_version: 2 })).toBe(false);
    expect(sessionMatchesMember({}, { session_version: undefined })).toBe(true);
  });

  it("L8: reminder dates use the member's own time zone", async () => {
    const member = await upsertMember(store, { email: "tz@example.com", firstName: "Tz" });
    await store.update("members", member.id, { timezone: "Pacific/Auckland" });
    const at = new Date(Date.now() + 30 * 3_600_000);
    await store.insert("memberships", { member_id: member.id, plan: "monthly", arm: "B", offer_code: "founding", price_cents: 2500, interval: "month", status: "active", founding: true, stripe_subscription_id: null, trial_end: null, current_period_end: at.toISOString(), first_paid_at: new Date().toISOString(), guarantee_until: null, cancel_at_period_end: false, canceled_at: null, paused_until: null, partner_seat: false, is_demo: false });
    await runReminders(store);
    const mail = (await store.findOne("outbox", { template: "C_pre_charge_48h" }))!;
    const expected = new Intl.DateTimeFormat("en-US", { timeZone: "Pacific/Auckland", month: "long", day: "numeric" }).format(at);
    expect(mail.body).toContain(expected);
  });

  it("L9: the chart has a phone-sized drawing and the AI badge is 18px", () => {
    const html = renderToStaticMarkup(createElement(TrendChart, { title: "t", points: [{ label: "M1", value: 70 }, { label: "M2", value: 68 }] }));
    expect(html).toContain('viewBox="0 0 400 300"');
    expect(renderToStaticMarkup(createElement(PhoneSession))).toMatch(/text-\[18px\][^>]*>AI character/);
  });

  it("L10: CSP header is set and the CAPI token isn't in the URL", async () => {
    const cfg = readFileSync(path.resolve(__dirname, "../../next.config.ts"), "utf8");
    expect(cfg).toMatch(/Content-Security-Policy/);
    process.env.META_PIXEL_ID = "123";
    process.env.META_CAPI_TOKEN = "secret-token";
    // Round 10: nothing leaves without ad-measurement consent (lib/conversions).
    const { recordAdConsent } = await import("@/lib/conversions/consent");
    const { getStore } = await import("@/lib/db");
    await recordAdConsent(await getStore(), "a@b.c", { ip: null, userAgent: null, source: "test" });
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("{}", { status: 200 }));
    await trackMetaEvent({ name: "Purchase", eventId: "e1", sourcePath: "/checkout", email: "a@b.c", valueCents: 100 }, "https://x");
    const [url, init] = spy.mock.calls[0]!;
    expect(String(url)).not.toContain("secret-token");
    expect(String((init as RequestInit).body)).toContain("secret-token");
  });

  it("L15: a gift purchase doesn't keep the card on file", () => {
    const q = quoteCheckout({ offer: "gift3", arm: "B", now: new Date(), gentle: false, timeZone: "America/Los_Angeles", domain: "x" });
    const params = buildSessionParams({ id: "i", offer_code: "gift3", arm: null, trial_days: 0, email: "a@b.c", price_cell: null } as CheckoutIntent, q);
    expect(params.payment_intent_data?.setup_future_usage).toBeUndefined();
  });
});
