import { beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent, invoiceSubscriptionId } from "@/lib/billing/webhook";
import { testSignatureHeader, verifyStripeSignature } from "@/lib/billing/verify";
import { foundingClaimed } from "@/lib/members";

let store: MemoryStore;

const baseInput: StartCheckoutInput = {
  offer: "trial",
  arm: "A",
  bump: true,
  gentle: false,
  email: "Ruth@Example.com",
  firstName: "Ruth",
  phone: "+1 555 555 0100",
  smsConsent: true,
  autoRenewConsent: true,
  ageConsent: true,
  gift: null,
  attribution: { utm_source: "ig", mc_id: "mc_42" },
  leadId: null,
  ip: "127.0.0.1",
  userAgent: "vitest",
};

async function checkout(input: Partial<StartCheckoutInput> = {}) {
  const res = await startCheckout(store, { ...baseInput, ...input });
  if (!res.ok) throw new Error(JSON.stringify(res.errors));
  return res;
}

function completed(intentId: string, extra: Record<string, unknown> = {}) {
  return {
    id: `evt_${crypto.randomUUID()}`,
    type: "checkout.session.completed",
    data: { object: { id: "cs_test_1", metadata: { intent_id: intentId }, payment_status: "paid", customer: "cus_1", subscription: "sub_1", payment_intent: "pi_1", ...extra } },
  };
}

beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});

describe("checkout intent + consent log", () => {
  it("refuses to start without the auto-renew box", async () => {
    const res = await startCheckout(store, { ...baseInput, autoRenewConsent: false });
    expect(res.ok).toBe(false);
    expect(await store.count("checkout_intents")).toBe(0);
    expect(await store.count("consent_log")).toBe(0);
  });

  it("stores the exact terms text, age and SMS consent before payment", async () => {
    const res = await checkout();
    expect(res.redirectUrl).toBe(`/checkout/mock/${res.intentId}`);
    const consents = await store.find("consent_log");
    expect(consents.map((c) => c.kind).sort()).toEqual(["age_18", "auto_renew", "sms"]);
    const ar = consents.find((c) => c.kind === "auto_renew")!;
    expect(ar.text_shown).toMatch(/renews at \$25\.00/);
    expect(ar.text_shown).toMatch(/Checkbox: I agree/);
    expect(ar.ip).toBe("127.0.0.1");
    expect(ar.price_cents).toBe(2500);
  });
});

describe("handleStripeEvent", () => {
  it("checkout.session.completed provisions member, trial membership, orders and consent links", async () => {
    const { intentId } = await checkout();
    const r = await handleStripeEvent(store, completed(intentId));
    expect(r.handled).toBe(true);
    const member = (await store.findOne("members", { email: "ruth@example.com" }))!;
    expect(member.sms_opt_in).toBe(true);
    expect(member.age_confirmed_at).not.toBeNull();
    expect(member.attribution?.mc_id).toBe("mc_42");
    const m = (await store.findOne("memberships", { member_id: member.id }))!;
    expect(m).toMatchObject({ status: "trialing", arm: "A", price_cents: 2500, founding: false, stripe_subscription_id: "sub_1", price_cell: "trial2500" });
    const orders = await store.find("sy_orders", { member_id: member.id });
    expect(orders.map((o) => o.kind).sort()).toEqual(["bump", "trial_fee"]);
    expect(orders.reduce((s, o) => s + o.amount_cents, 0)).toBe(1000);
    expect((await store.find("consent_log")).every((c) => c.member_id === member.id)).toBe(true);
    // welcome email repeats the terms; SMS welcome sent because of consent
    const email = (await store.findOne("outbox", { template: "E1_welcome_terms" }))!;
    expect(email.body).toMatch(/Trial ends/);
    expect(email.body).toMatch(/STRONGYEARS MEMBER/);
    expect(await store.count("outbox", { template: "S1_welcome" })).toBe(1);
    // server-side conversion events, Meta-safe names only
    const names = (await store.find("analytics_events")).map((e) => e.name).sort();
    expect(names).toEqual(["Purchase", "StartTrial"]);
  });

  it("is idempotent: the same event twice changes nothing", async () => {
    const { intentId } = await checkout();
    const evt = completed(intentId);
    await handleStripeEvent(store, evt);
    const second = await handleStripeEvent(store, evt);
    expect(second.duplicate).toBe(true);
    // a different event for the same intent is also a no-op
    await handleStripeEvent(store, completed(intentId));
    expect(await store.count("memberships")).toBe(1);
    expect(await store.count("sy_orders")).toBe(2);
  });

  it("arm B founding membership is active today and counts toward the cohort", async () => {
    const { intentId } = await checkout({ offer: "founding", arm: "B", bump: false, email: "walt@example.com" });
    await handleStripeEvent(store, completed(intentId));
    const m = (await store.findOne("memberships", { founding: true }))!;
    expect(m.status).toBe("active");
    expect(m.first_paid_at).not.toBeNull();
    const days = (new Date(m.guarantee_until!).getTime() - Date.now()) / 86_400_000;
    expect(Math.round(days)).toBe(14);
    expect(await foundingClaimed(store)).toBe(1);
    expect((await store.find("analytics_events")).map((e) => e.name).sort()).toEqual(["Purchase", "Subscribe"]);
  });

  it("invoice.paid converts a trial, records the charge and starts the 14-day guarantee", async () => {
    const { intentId } = await checkout();
    await handleStripeEvent(store, completed(intentId));
    const inv = {
      id: "evt_inv_1",
      type: "invoice.paid",
      data: { object: { id: "in_1", amount_paid: 2000, billing_reason: "subscription_cycle", payment_intent: "pi_2", parent: { subscription_details: { subscription: "sub_1" } }, lines: { data: [{ period: { end: 1_900_000_000 } }] } } },
    };
    const r = await handleStripeEvent(store, inv);
    expect(r.summary).toMatch(/trial converted/);
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_1" }))!;
    expect(m.status).toBe("active");
    expect(m.guarantee_until).not.toBeNull();
    expect(await store.count("sy_orders", { kind: "membership_charge" })).toBe(1);
  });

  it("reads the subscription id from both invoice shapes", () => {
    expect(invoiceSubscriptionId({ subscription: "sub_a" })).toBe("sub_a");
    expect(invoiceSubscriptionId({ parent: { subscription_details: { subscription: "sub_b" } } })).toBe("sub_b");
  });

  it("payment_failed → past_due + dunning; refund and dispute mark orders; deleted ends membership", async () => {
    const { intentId } = await checkout();
    await handleStripeEvent(store, completed(intentId));
    await handleStripeEvent(store, { id: "evt_f", type: "invoice.payment_failed", data: { object: { id: "in_f", subscription: "sub_1" } } });
    expect((await store.findOne("memberships", { stripe_subscription_id: "sub_1" }))!.status).toBe("past_due");
    expect(await store.count("outbox", { template: "dunning_1" })).toBe(1);

    await handleStripeEvent(store, { id: "evt_d", type: "charge.dispute.created", data: { object: { payment_intent: "pi_1" } } });
    expect(await store.count("sy_orders", { status: "disputed" })).toBe(2);
    expect((await store.findOne("memberships", { stripe_subscription_id: "sub_1" }))!.status).toBe("canceled");
    expect(await store.count("support_tickets", { reason: "dispute" })).toBe(1);

    await handleStripeEvent(store, { id: "evt_del", type: "customer.subscription.deleted", data: { object: { id: "sub_1", ended_at: 1_900_000_000 } } });
    expect((await store.findOne("memberships", { stripe_subscription_id: "sub_1" }))!.status).toBe("canceled");
  });

  it("subscription.updated syncs pause, cancel_at_period_end and period end (basil item shape)", async () => {
    const { intentId } = await checkout();
    await handleStripeEvent(store, completed(intentId));
    await handleStripeEvent(store, {
      id: "evt_u",
      type: "customer.subscription.updated",
      data: { object: { id: "sub_1", status: "active", cancel_at_period_end: true, pause_collection: null, items: { data: [{ current_period_end: 1_900_000_000, price: { unit_amount: 2000 } }] } } },
    });
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_1" }))!;
    expect(m.cancel_at_period_end).toBe(true);
    expect(m.canceled_at).not.toBeNull();
    expect(m.current_period_end).toBe(new Date(1_900_000_000 * 1000).toISOString());
  });

  it("gift checkout creates a prepaid gift, emails the recipient, and no subscription", async () => {
    const { intentId } = await checkout({ offer: "gift3", autoRenewConsent: false, gift: { recipient_name: "Mom", recipient_email: "mom@example.com", message: "Love you", months: 3 } });
    await handleStripeEvent(store, completed(intentId, { subscription: null }));
    expect(await store.count("memberships")).toBe(0);
    const gift = (await store.findOne("gifts", { recipient_email: "mom@example.com" }))!;
    expect(gift.months).toBe(3);
    expect(gift.code).toMatch(/^[A-Z2-9]{4}-[A-Z2-9]{4}$/);
    expect(await store.count("outbox", { template: "gift_recipient" })).toBe(1);
  });

  it("waits on unpaid async sessions", async () => {
    const { intentId } = await checkout();
    const r = await handleStripeEvent(store, completed(intentId, { payment_status: "unpaid" }));
    expect(r.handled).toBe(false);
    expect(await store.count("memberships")).toBe(0);
  });
});

describe("signature verification", () => {
  it("accepts a correctly signed payload and rejects a tampered one", () => {
    const secret = "whsec_test_secret";
    const payload = JSON.stringify({ id: "evt_sig", type: "invoice.paid", data: { object: {} } });
    const header = testSignatureHeader(payload, secret);
    expect(verifyStripeSignature(payload, header, secret).id).toBe("evt_sig");
    expect(() => verifyStripeSignature(payload.replace("evt_sig", "evt_bad"), header, secret)).toThrow();
    expect(() => verifyStripeSignature(payload, null, secret)).toThrow();
  });
});
