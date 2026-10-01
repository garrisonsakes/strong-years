/** Both arms from day 1: founding charge-today ($25/$30) vs the $1 trial (then $25). */
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { assignArm, resolveFoundingOffer, testCell } from "@/lib/blitz";
import { blitz, offerRules, prices } from "@/lib/config";
import { quoteCheckout } from "@/lib/pricing";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";

const saved = { ...process.env };
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});
let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});

describe("3-cell test: founding $25 / founding $30 / $1 trial", () => {
  it("arm split is sticky per visitor and defaults to 50/50", () => {
    expect(offerRules.armBShare).toBe(0.5);
    const ids = Array.from({ length: 4000 }, (_, i) => `v${i}`);
    const b = ids.filter((v) => assignArm(v, 0.5) === "B").length / ids.length;
    expect(b).toBeGreaterThan(0.46);
    expect(b).toBeLessThan(0.54);
    for (const v of ids.slice(0, 50)) expect(assignArm(v, 0.5)).toBe(assignArm(v, 0.5));
  });
  it("the split is configurable (ARM_B_SHARE)", () => {
    process.env.ARM_B_SHARE = "0.8";
    const ids = Array.from({ length: 4000 }, (_, i) => `w${i}`);
    const b = ids.filter((v) => assignArm(v, offerRules.armBShare) === "B").length / ids.length;
    expect(b).toBeGreaterThan(0.76);
    expect(assignArm("x", 0)).toBe("A");
    expect(assignArm("x", 1)).toBe("B");
  });
  it("CANON UPDATE 2: the $1 trial can't be switched on; the dormant quote math still renews at the founding price", () => {
    process.env.TRIAL_ARM_ENABLED = "true";
    expect(blitz.trialArmEnabled).toBe(false);
    delete process.env.TRIAL_ARM_ENABLED;
    expect(prices.monthly).toBe(2500);
    const q = quoteCheckout({ offer: "trial", arm: "A", now: new Date(), timeZone: "America/Los_Angeles", domain: "x" });
    expect(q.recurring?.priceCents).toBe(2500);
    expect(q.terms.join(" ")).toMatch(/renews at \$25\.00/);
    expect(q.terms.join(" ")).toMatch(/14-day money-back guarantee on your first full membership charge/);
    expect(q.terms.join(" ")).not.toMatch(/30-day|CANCEL|email and text/);
  });
  it("after the founding cap, the trial renews at the standard price", () => {
    const q = quoteCheckout({ offer: "trial", arm: "A", now: new Date(), timeZone: "America/Los_Angeles", domain: "x", cohortOpen: false, standardCents: 3500 });
    expect(q.recurring?.priceCents).toBe(3500);
  });
  it("every checkout logs its test cell", async () => {
    const offer = resolveFoundingOffer({ visitorId: "v1", claimed: 0, cap: 5000, testOn: true, cells: [2500, 3000], defaultCents: 2500, standardCents: 3500 });
    expect(testCell("A", offer, 2500)).toBe("trial2500");
    expect(testCell("B", offer, 2500)).toMatch(/^p(2500|3000)$/);
    const r = await startCheckout(store, { offer: "trial", arm: "A", gentle: false, email: "t@example.com", firstName: "T", phone: "", smsConsent: false, autoRenewConsent: true, ageConsent: true, gift: null, attribution: null, leadId: null, ip: null, userAgent: null, visitorId: "v1" });
    if (!r.ok) throw new Error("checkout");
    expect((await store.get("checkout_intents", r.intentId))!.price_cell).toBe("trial2500");
  });
  it("trial guarantee: 14 days from the first full charge", async () => {
    const r = await startCheckout(store, { offer: "trial", arm: "A", gentle: false, email: "g@example.com", firstName: "G", phone: "", smsConsent: false, autoRenewConsent: true, ageConsent: true, gift: null, attribution: null, leadId: null, ip: null, userAgent: null });
    if (!r.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: "e1", type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId }, payment_status: "paid", subscription: "sub_t" } } });
    await handleStripeEvent(store, { id: "e2", type: "invoice.paid", data: { object: { id: "in_2", amount_paid: 2500, billing_reason: "subscription_cycle", payment_intent: "pi_2", parent: { subscription_details: { subscription: "sub_t" } }, lines: { data: [{ period: { end: 1_900_000_000 } }] } } } });
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_t" }))!;
    const days = (new Date(m.guarantee_until!).getTime() - new Date(m.first_paid_at!).getTime()) / 86_400_000;
    expect(Math.round(days)).toBe(14);
  });
});
