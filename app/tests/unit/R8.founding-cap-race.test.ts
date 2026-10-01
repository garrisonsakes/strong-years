/**
 * AUDIT_FINAL §7 (Round 8) #1: founding cap race. With 2 spots left, concurrent
 * buyers used to all get founding. Spots are now taken atomically at checkout
 * creation (advisory lock in Postgres; a mutex for the in-memory store) and
 * confirmed at fulfilment. Postgres itself was checked with 50 parallel
 * reserve_founding_spot() calls at cap 2 → exactly 2 true (see handback).
 */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { FOUNDING_HOLD_MINUTES, CHECKOUT_SESSION_MINUTES, confirmFoundingSpot, foundingTaken, reserveFoundingSpot } from "@/lib/founding";
import { buildSessionParams } from "@/lib/billing/stripeSession";

const CAP = 10;
const saved = { ...process.env };
let store: MemoryStore;
beforeEach(async () => {
  store = new MemoryStore();
  setStoreForTests(store);
  process.env.FOUNDING_COHORT_CAP = String(CAP);
  // cap − 2: eight founding members already.
  for (let i = 0; i < CAP - 2; i++) await store.insert("memberships", { member_id: `m${i}`, founding: true, status: "active", checkout_intent_id: null });
});
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

const buyer = (i: number): StartCheckoutInput => ({
  offer: "founding",
  arm: "B",
  gentle: false,
  email: `buyer${i}@example.com`,
  firstName: `Buyer${i}`,
  phone: "",
  smsConsent: false,
  autoRenewConsent: true,
  ageConsent: true,
  gift: null,
  attribution: null,
  leadId: null,
  ip: null,
  userAgent: null,
  visitorId: `vid-${i}`,
});

async function pay(intentId: string, at?: Date) {
  const { fulfillCheckoutIntent } = await import("@/lib/billing/fulfill");
  if (at) return fulfillCheckoutIntent(store, intentId, { stripeCustomerId: `cus_${intentId}`, stripeSubscriptionId: `sub_${intentId}`, now: at });
  await handleStripeEvent(store, {
    id: `evt_${intentId}`,
    type: "checkout.session.completed",
    data: { object: { metadata: { intent_id: intentId }, payment_status: "paid", customer: `cus_${intentId}`, subscription: `sub_${intentId}` } },
  });
}

const founders = () => store.count("memberships", { founding: true });

describe("Round 8: founding cap is atomic", () => {
  it("R8: 50 parallel founding checkouts at cap−2 → exactly 2 get founding; 48 are stopped before paying, told why, charged nothing", async () => {
    const results = await Promise.all(Array.from({ length: 50 }, (_, i) => startCheckout(store, buyer(i))));
    const ok = results.filter((r) => r.ok);
    const full = results.filter((r) => !r.ok);
    expect(ok).toHaveLength(2);
    expect(full).toHaveLength(48);
    for (const r of full) {
      if (r.ok) continue;
      expect(r.cohortFull).toBe(true);
      expect(r.errors[0]!.message).toMatch(/last founding spot was taken/);
      expect(r.errors[0]!.message).toMatch(/Nothing was charged/);
      expect(r.errors[0]!.message).toMatch(/\$35\.00 a month \(the standard price\)/);
    }
    expect(await store.count("founding_holds", { status: "held" })).toBe(2);
    // Everyone who got through pays; the stopped ones never reached a payment page.
    for (const r of ok) if (r.ok) await pay(r.intentId);
    expect(await founders()).toBe(CAP);
    expect(await foundingTaken(store)).toBe(CAP);
    expect(await store.count("checkout_intents", { status: "failed" })).toBe(48);
  });

  it("R8: once full, the next buyer is quoted (and charged) the standard price, never founding", async () => {
    const two = await Promise.all([startCheckout(store, buyer(1)), startCheckout(store, buyer(2))]);
    for (const r of two) if (r.ok) await pay(r.intentId);
    const late = await startCheckout(store, buyer(3));
    expect(late.ok).toBe(true);
    if (!late.ok) return;
    expect(late.quote.recurring?.priceCents).toBe(3500);
    expect(late.quote.recurring?.founding).toBeFalsy();
    const intent = (await store.get("checkout_intents", late.intentId))!;
    expect(intent.price_cell).toBe("standard");
    await pay(late.intentId);
    expect(await founders()).toBe(CAP);
    expect((await store.findOne("memberships", { checkout_intent_id: late.intentId }))!.founding).toBe(false);
  });

  it("R8: an abandoned hold expires and frees the spot; Stripe's checkout.session.expired frees it at once", async () => {
    const a = await startCheckout(store, buyer(1));
    const b = await startCheckout(store, buyer(2));
    expect(a.ok && b.ok).toBe(true);
    // Full (two live holds): the next buyer is simply quoted the standard price.
    const c = await startCheckout(store, buyer(3));
    expect(c.ok && c.quote.recurring?.founding).toBeFalsy();
    // Stripe says buyer 2's page expired.
    if (b.ok) await handleStripeEvent(store, { id: "evt_exp", type: "checkout.session.expired", data: { object: { metadata: { intent_id: b.intentId } } } });
    const d = await startCheckout(store, buyer(4));
    expect(d.ok && d.quote.recurring?.founding).toBe(true);
    // Buyer 1 just walks away: after the hold lapses the spot is free again.
    const later = new Date(Date.now() + (FOUNDING_HOLD_MINUTES + 1) * 60_000);
    expect(await reserveFoundingSpot(store, "00000000-0000-0000-0000-00000000cafe", CAP, later)).toBe(true);
  });

  it("R8: payment confirmed in time keeps its spot; a very late one whose spot was retaken is not founding and goes to review", async () => {
    const a = await startCheckout(store, buyer(1));
    const b = await startCheckout(store, buyer(2));
    if (!a.ok || !b.ok) throw new Error("setup");
    await pay(a.intentId); // in time
    // Buyer 2's hold lapses (webhook delayed past the hold), and someone else takes the spot.
    const later = new Date(Date.now() + (FOUNDING_HOLD_MINUTES + 5) * 60_000);
    expect(await reserveFoundingSpot(store, "00000000-0000-0000-0000-0000000000aa", CAP, later)).toBe(true);
    await pay(b.intentId, later);
    const m = (await store.findOne("memberships", { checkout_intent_id: b.intentId }))!;
    expect(m.founding).toBe(false);
    expect(m.price_cell).toBe("over_cap");
    expect(await store.count("support_tickets", { reason: "refund_review" })).toBe(1);
    expect(await founders()).toBe(CAP - 1); // + the new holder, when they pay
  });

  it("R8: a late payment whose spot is still free is confirmed as founding", async () => {
    const a = await startCheckout(store, buyer(1));
    if (!a.ok) throw new Error("setup");
    const later = new Date(Date.now() + (FOUNDING_HOLD_MINUTES + 5) * 60_000);
    expect(await confirmFoundingSpot(store, a.intentId, CAP, later)).toBe(true);
  });

  it("R8: the Stripe payment page closes before the hold does; the $1 trial never takes a founding spot", async () => {
    const a = await startCheckout(store, buyer(1));
    if (!a.ok) throw new Error("setup");
    const intent = (await store.get("checkout_intents", a.intentId))!;
    const params = buildSessionParams(intent, a.quote);
    expect(params.expires_at).toBeDefined();
    expect(params.expires_at! - Date.now() / 1000).toBeLessThanOrEqual(CHECKOUT_SESSION_MINUTES * 60 + 2);
    expect(CHECKOUT_SESSION_MINUTES).toBeLessThan(FOUNDING_HOLD_MINUTES);
    const t = await startCheckout(store, { ...buyer(9), offer: "trial", arm: "A" });
    expect(t.ok).toBe(true);
    if (t.ok) expect(buildSessionParams((await store.get("checkout_intents", t.intentId))!, t.quote).expires_at).toBeUndefined();
    expect(await store.count("founding_holds")).toBe(1);
  });
});
