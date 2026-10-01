/**
 * AUDIT_FINAL NEW-1: paying with an existing member's email must never sign the
 * payer in as that member, and must never touch the member's Stripe customer or card.
 * The first test reproduces the verifier's scenario step by step.
 */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { entitlementFor } from "@/lib/entitlement";
import { resolvePurchaseVerification } from "@/lib/billing/verifyPurchase";
import { handleChatTurn } from "@/lib/ai/chat";
import { billingMembership } from "@/lib/auth/server";
import { normalizeEmail } from "@/lib/members";

let store: MemoryStore;
const saved = { ...process.env };
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

const base: StartCheckoutInput = {
  offer: "founding",
  arm: "B",
  gentle: false,
  email: "victoria@example.com",
  firstName: "Victoria",
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

/** Checkout + Stripe's completion event + the success redirect, like a real browser. */
async function pay(input: Partial<StartCheckoutInput>, stripe: { customer: string; pm: string; sub?: string | null }) {
  const r = await startCheckout(store, { ...base, ...input });
  if (!r.ok) throw new Error(JSON.stringify(r.errors));
  await handleStripeEvent(store, {
    id: `evt_${r.intentId}`,
    type: "checkout.session.completed",
    data: { object: { metadata: { intent_id: r.intentId, payment_method: stripe.pm }, payment_status: "paid", customer: stripe.customer, subscription: stripe.sub === undefined ? `sub_${r.intentId.slice(0, 6)}` : stripe.sub } },
  });
  const { GET } = await import("@/app/api/checkout/complete/route");
  const res = await GET(new Request(`http://localhost/api/checkout/complete?intent=${r.intentId}`));
  return { intentId: r.intentId, res, cookie: res.headers.get("set-cookie"), location: res.headers.get("location") ?? "" };
}

async function victim() {
  const v = await pay({}, { customer: "cus_victim", pm: "pm_victim" });
  expect(v.cookie).toMatch(/sy_session=/); // a brand-new account's buyer is its owner
  const member = (await store.findOne("members", { email: "victoria@example.com" }))!;
  await handleChatTurn(store, member, "chang", "VICTIM-SECRET my knee hurts after my hip surgery");
  return member;
}

describe("NEW-1 checkout never takes over an existing account", () => {
  it("NEW-1: verifier's scenario: attacker pays at /join with the victim's email → no session, victim's card untouched", async () => {
    const v = await victim();
    const vMembership = (await billingMembership(v.id))!;
    const attack = await pay({ firstName: "Mallory" }, { customer: "cus_attacker", pm: "pm_attacker" });
    expect(attack.cookie).toBeNull();
    expect(attack.location).toMatch(/\/checkout\/check-email$/);
    const after = (await store.get("members", v.id))!;
    expect(after.first_name).toBe("Victoria");
    expect(after.stripe_customer_id).toBe("cus_victim");
    expect(after.stripe_payment_method).toBe("pm_victim");
    // The new purchase is parked, grants nothing, and never becomes the billing row.
    const pending = (await store.findOne("memberships", { checkout_intent_id: attack.intentId }))!;
    expect(pending.pending_verification).toBe(true);
    expect(pending.stripe_customer_id).toBe("cus_attacker");
    expect((await billingMembership(v.id))!.id).toBe(vMembership.id);
    expect(entitlementFor([pending]).access).toBe(false);
    // The inbox owner is asked; nobody else is.
    const mail = (await store.findOne("outbox", { template: "purchase_verify" }))!;
    expect(mail.to).toBe("victoria@example.com");
    expect(mail.body).not.toMatch(/token=[A-Za-z0-9_-]{10,}/);
  });

  it.each([
    ["trial ($1)", { offer: "trial", arm: "A" } as Partial<StartCheckoutInput>],
    ["founding", { offer: "founding", arm: "B" } as Partial<StartCheckoutInput>],
    ["founding + bumps", { offer: "founding", arm: "B", bumps: ["reset", "kitchen", "wallplan"] } as Partial<StartCheckoutInput>],
  ])("NEW-1 variant: %s with the victim's email → no session", async (_n, input) => {
    const v = await victim();
    const a = await pay(input, { customer: "cus_x", pm: "pm_x" });
    expect(a.cookie).toBeNull();
    expect((await store.get("members", v.id))!.stripe_payment_method).toBe("pm_victim");
  });

  it("NEW-1 variant: bump-only front end (Reset page) with the victim's email → no session", async () => {
    process.env.FRONTEND_PAGES_ENABLED = "true";
    const v = await victim();
    const a = await pay({ offer: "reset", arm: "B" }, { customer: "cus_x", pm: "pm_x" });
    expect(a.cookie).toBeNull();
    expect((await store.get("members", v.id))!.stripe_customer_id).toBe("cus_victim");
  });

  it("NEW-1 variant: gift bought with the victim's email → thanks page, no session, no card change", async () => {
    const v = await victim();
    const a = await pay({ offer: "gift3", autoRenewConsent: false, gift: { recipient_name: "Al", recipient_email: "al@example.com", message: "", months: 3 } }, { customer: "cus_g", pm: "pm_g", sub: null });
    expect(a.cookie).toBeNull();
    expect(a.location).toMatch(/\/gift\/thanks$/);
    expect((await store.get("members", v.id))!.stripe_customer_id).toBe("cus_victim");
  });

  it.each([
    "  VICTORIA@Example.COM ",
    "Victoria@example.com​",
    "ｖｉｃｔｏｒｉａ@example.com",
    "vic­toria@example.com",
  ])("NEW-1 variant: email trick %j is the same account → no session", async (email) => {
    expect(normalizeEmail(email)).toBe("victoria@example.com");
    const v = await victim();
    const a = await pay({ email }, { customer: "cus_t", pm: "pm_t" });
    expect(a.cookie).toBeNull();
    expect(await store.count("members")).toBe(1);
    expect((await store.get("members", v.id))!.stripe_payment_method).toBe("pm_victim");
  });

  it("NEW-1: the member themself, signed in, can buy again and continue signed in", async () => {
    const v = await victim();
    const again = await pay({ offer: "founding", authMemberId: v.id }, { customer: "cus_victim2", pm: "pm_victim2" });
    expect(again.cookie).toMatch(/sy_session=/);
    // Even then, an existing Stripe customer and card are never replaced.
    expect((await store.get("members", v.id))!.stripe_customer_id).toBe("cus_victim");
  });

  it("NEW-1: only the emailed link opens the pending purchase; 'This wasn't me' stops billing and flags a refund", async () => {
    const v = await victim();
    const a = await pay({}, { customer: "cus_attacker", pm: "pm_attacker" });
    // A forged token does nothing.
    expect((await resolvePurchaseVerification(store, "forged", "confirm")).ok).toBe(false);
    const intent = (await store.get("checkout_intents", a.intentId))!;
    expect(intent.verification).toBe("pending");
    // Simulate the owner clicking "This wasn't me" with the real token (reissued for the test).
    const { sendPurchaseVerification } = await import("@/lib/billing/verifyPurchase");
    const token = await sendPurchaseVerification(store, a.intentId, v, []);
    const r = await resolvePurchaseVerification(store, token, "reject");
    expect(r.ok).toBe(true);
    const m = (await store.findOne("memberships", { checkout_intent_id: a.intentId }))!;
    expect(m.status).toBe("canceled");
    expect(await store.count("support_tickets", { reason: "refund_review" })).toBe(1);
    // Single use.
    expect((await resolvePurchaseVerification(store, token, "confirm")).ok).toBe(false);
  });

  it("NEW-1: confirming from the inbox unlocks the purchase and signs the owner in", async () => {
    const v = await victim();
    const a = await pay({ offer: "trial", arm: "A" }, { customer: "cus_2", pm: "pm_2" });
    const { sendPurchaseVerification } = await import("@/lib/billing/verifyPurchase");
    const token = await sendPurchaseVerification(store, a.intentId, v, []);
    const { POST } = await import("@/app/api/checkout/verify/route");
    const f = new FormData();
    f.set("token", token);
    f.set("action", "confirm");
    const res = await POST(new Request("http://localhost/api/checkout/verify", { method: "POST", body: f }));
    expect(res.headers.get("set-cookie")).toMatch(/sy_session=/);
    expect((await store.findOne("memberships", { checkout_intent_id: a.intentId }))!.pending_verification).toBe(false);
  });
});
