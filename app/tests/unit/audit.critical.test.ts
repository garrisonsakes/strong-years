/**
 * Regression tests for AUDIT_CODE.md critical findings C1 and C4 (C2 has its own
 * files: C2.crisis-corpus.test.ts, C2.chat-failclosed.test.ts; C3 is outside app/).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { RetryLater, handleStripeEvent } from "@/lib/billing/webhook";
import { claimGift, requestGiftClaim } from "@/lib/gifts";
import { billingMembership } from "@/lib/auth/server";
import type { RefundOutcome } from "@/lib/billing/processors";

const refundImpl = vi.hoisted(() => ({
  live: false,
  outcome: { status: "succeeded", refundId: "re_1" } as RefundOutcome,
  calls: [] as { pi: string; amount: number }[],
}));

vi.mock("@/lib/billing/processors", async (orig) => {
  const real = await orig<typeof import("@/lib/billing/processors")>();
  return {
    ...real,
    processorFor: (id: "stripe" | "braintree") => {
      const p = real.processorFor(id);
      if (!refundImpl.live) return p;
      return {
        ...p,
        status: () => "live" as const,
        refund: async (pi: string, amount: number) => {
          refundImpl.calls.push({ pi, amount });
          return refundImpl.outcome;
        },
      };
    },
  };
});

let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  refundImpl.live = false;
  refundImpl.outcome = { status: "succeeded", refundId: "re_1" };
  refundImpl.calls = [];
});
afterEach(() => vi.restoreAllMocks());

const base: StartCheckoutInput = {
  offer: "founding",
  arm: "B",
  gentle: false,
  email: "buyer@example.com",
  firstName: "Bea",
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

async function buy(input: Partial<StartCheckoutInput> = {}, session: Record<string, unknown> = {}) {
  const r = await startCheckout(store, { ...base, ...input });
  if (!r.ok) throw new Error(JSON.stringify(r.errors));
  await handleStripeEvent(store, {
    id: `evt_${crypto.randomUUID()}`,
    type: "checkout.session.completed",
    data: { object: { id: "cs_1", metadata: { intent_id: r.intentId }, payment_status: "paid", customer: "cus_1", subscription: null, payment_intent: "pi_gift", ...session } },
  });
  return r.intentId;
}

describe("C1 gift codes never log anyone in", () => {
  it("C1: the gifter's receipt contains neither the code nor the claim link", async () => {
    await buy({ offer: "gift3", autoRenewConsent: false, gift: { recipient_name: "Mom", recipient_email: "victim@example.com", message: "", months: 3 } });
    const gift = (await store.findOne("gifts", { recipient_email: "victim@example.com" }))!;
    const receipt = (await store.findOne("outbox", { template: "gift_receipt" }))!;
    expect(receipt.to).toBe("buyer@example.com");
    expect(receipt.body).not.toContain(gift.code);
    expect(receipt.body).not.toMatch(/gift\/claim|token=/);
    // The recipient's email goes only to the recipient, and the stored copy is redacted (M6).
    const toRecipient = (await store.find("outbox", { template: "gift_recipient" }))!;
    expect(toRecipient.map((m) => m.to)).toEqual(["victim@example.com"]);
    expect(toRecipient[0]!.body).not.toContain(gift.code);
  });

  it("C1: entering a code only emails a fresh link to the recipient; the redeem route sets no cookie", async () => {
    await buy({ offer: "gift3", autoRenewConsent: false, gift: { recipient_name: "Mom", recipient_email: "victim@example.com", message: "", months: 3 } });
    const gift = (await store.findOne("gifts", { recipient_email: "victim@example.com" }))!;
    const { POST } = await import("@/app/api/gift/redeem/route");
    const form = new FormData();
    form.set("code", gift.code);
    const res = await POST(new Request("http://localhost/api/gift/redeem", { method: "POST", body: form }));
    expect(res.status).toBe(303);
    expect(res.headers.get("set-cookie")).toBeNull();
    expect(res.headers.get("location")).toMatch(/sent=1/);
    expect(res.headers.get("location")).not.toContain("victim@example.com");
    const sent = await store.find("outbox", { template: "gift_claim_link" });
    expect(sent.map((m) => m.to)).toEqual(["victim@example.com"]);
  });

  it("C1: a paying member targeted by a gift is never logged in by the buyer, and their billing row stays in charge (H3)", async () => {
    // The victim already pays.
    await buy({ email: "victim@example.com", firstName: "Vic" }, { subscription: "sub_victim", invoice: "in_v", payment_intent: null });
    const victim = (await store.findOne("members", { email: "victim@example.com" }))!;
    const paid = (await billingMembership(victim.id))!;
    // An attacker buys a gift "for" the victim and redeems the code.
    await buy({ email: "attacker@example.com", offer: "gift3", autoRenewConsent: false, gift: { recipient_name: "Vic", recipient_email: "victim@example.com", message: "", months: 3 } });
    const gift = (await store.findOne("gifts", { recipient_email: "victim@example.com" }))!;
    const claim = await requestGiftClaim(store, gift.code);
    expect(claim.status).toBe("sent");
    // Only the holder of the emailed token can claim; a wrong token does nothing.
    expect((await claimGift(store, "not-the-token", { firstName: "x", ageConfirmed: true, share: false })).ok).toBe(false);
    const ok = await claimGift(store, (claim as { token: string }).token, { firstName: "Vic", ageConfirmed: true, share: false });
    expect(ok.ok && ok.appliedAs).toBe("credit");
    expect((await billingMembership(victim.id))!.id).toBe(paid.id);
    // Single use.
    expect((await claimGift(store, (claim as { token: string }).token, { firstName: "Vic", ageConfirmed: true, share: false })).ok).toBe(false);
  });

  it("C1: the claim route signs in only with a valid emailed token, once", async () => {
    await buy({ offer: "gift12", autoRenewConsent: false, gift: { recipient_name: "Al", recipient_email: "al@example.com", message: "", months: 12 } });
    const gift = (await store.findOne("gifts", { recipient_email: "al@example.com" }))!;
    const { token } = (await requestGiftClaim(store, gift.code)) as { token: string };
    const { POST } = await import("@/app/api/gift/claim/route");
    const post = (t: string) => {
      const f = new FormData();
      f.set("token", t);
      f.set("first_name", "Al");
      f.set("age", "on");
      return POST(new Request("http://localhost/api/gift/claim", { method: "POST", body: f }));
    };
    const bad = await post("forged");
    expect(bad.headers.get("set-cookie")).toBeNull();
    const good = await post(token);
    expect(good.headers.get("set-cookie")).toMatch(/sy_session=/);
    const again = await post(token);
    expect(again.headers.get("set-cookie")).toBeNull();
  });
});

describe("C4 refunds only happen when the processor confirms", () => {
  async function foundingMember(email = "ref@example.com") {
    await buy({ email }, { subscription: `sub_${email}`, invoice: `in_${email}`, payment_intent: null });
    const member = (await store.findOne("members", { email }))!;
    return { member, m: (await billingMembership(member.id))! };
  }

  it("C4: with a live processor and no resolvable payment, nothing is marked refunded and no email is sent", async () => {
    const { m } = await foundingMember();
    refundImpl.live = true; // live Stripe, but the invoice's payment can't be resolved
    const { refundMembership } = await import("@/lib/billing/actions");
    const r = await refundMembership(store, m);
    expect(r.ok).toBe(false);
    expect(r.state).toBe("review");
    expect(await store.count("sy_orders", { status: "refunded" })).toBe(0);
    expect((await store.get("memberships", m.id))!.status).toBe("active");
    expect(await store.count("outbox", { template: "refund_confirmation" })).toBe(0);
    expect(await store.count("support_tickets", { reason: "refund_review" })).toBe(1);
  });

  it("C4: a failed processor refund leaves everything unchanged and opens a ticket", async () => {
    const { m } = await foundingMember();
    await store.updateWhere("sy_orders", { membership_id: m.id }, { stripe_payment_intent: "pi_real" });
    refundImpl.live = true;
    refundImpl.outcome = { status: "failed", refundId: null, error: "charge_already_refunded" };
    const { refundMembership } = await import("@/lib/billing/actions");
    const r = await refundMembership(store, m);
    expect(r.ok).toBe(false);
    expect(await store.count("sy_orders", { status: "refunded" })).toBe(0);
    expect(await store.count("outbox", { template: "refund_confirmation" })).toBe(0);
  });

  it("C4: a pending refund is not called 'refunded' until the webhook confirms it", async () => {
    const { m } = await foundingMember();
    await store.updateWhere("sy_orders", { membership_id: m.id }, { stripe_payment_intent: "pi_real" });
    refundImpl.live = true;
    refundImpl.outcome = { status: "pending", refundId: "re_p" };
    const { refundMembership } = await import("@/lib/billing/actions");
    const r = await refundMembership(store, m);
    expect(r.state).toBe("pending");
    expect(await store.count("sy_orders", { status: "refund_pending" })).toBe(1);
    expect(await store.count("outbox", { template: "refund_confirmation" })).toBe(0);
    await handleStripeEvent(store, { id: "evt_rf", type: "charge.refunded", data: { object: { payment_intent: "pi_real", refunded: true, amount_refunded: 2500 } } });
    expect(await store.count("sy_orders", { status: "refunded" })).toBe(1);
    expect(await store.count("outbox", { template: "refund_confirmation" })).toBe(1);
    expect((await store.get("memberships", m.id))!.status).toBe("refunded");
  });

  it("C4: invoice.paid arriving before checkout completion is retried, then links the payment", async () => {
    const r = await startCheckout(store, { ...base, email: "early@example.com" });
    if (!r.ok) throw new Error("checkout failed");
    const invoiceEvt = {
      id: "evt_inv_early",
      type: "invoice.paid",
      data: { object: { id: "in_early", billing_reason: "subscription_create", amount_paid: 2500, payment_intent: "pi_early", parent: { subscription_details: { subscription: "sub_early", metadata: { intent_id: r.intentId } } } } },
    };
    await expect(handleStripeEvent(store, invoiceEvt)).rejects.toBeInstanceOf(RetryLater);
    await handleStripeEvent(store, {
      id: "evt_cs_early",
      type: "checkout.session.completed",
      data: { object: { id: "cs_e", metadata: { intent_id: r.intentId }, payment_status: "paid", customer: "cus_e", subscription: "sub_early", invoice: "in_early", payment_intent: null } },
    });
    const res = await handleStripeEvent(store, invoiceEvt); // Stripe's retry, same event id
    expect(res.summary).toMatch(/linked/);
    const charge = (await store.findOne("sy_orders", { kind: "membership_charge", checkout_intent_id: r.intentId }))!;
    expect(charge.stripe_payment_intent).toBe("pi_early");
    expect(charge.stripe_invoice).toBe("in_early");
  });
});
