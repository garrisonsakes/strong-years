import { beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { CANCEL_REASONS, cancelFlowScreens, saveOfferFor, withinGuarantee } from "@/lib/billing/cancel";
import { cancelMembership, downgradeToEssentials, pauseMembership, refundMembership, undoCancel } from "@/lib/billing/actions";
import { runMockBillingClock, runReminders } from "@/lib/billing/clock";
import { upsertMember } from "@/lib/members";
import type { Membership } from "@/lib/db/types";
import { computeStrongWeeks } from "@/lib/practice";

let store: MemoryStore;
const DAY = 86_400_000;

async function makeMembership(patch: Partial<Membership> = {}) {
  const member = await upsertMember(store, { email: `m${Math.random()}@example.com`, firstName: "Mae", smsOptIn: true, phone: "+15555550100" });
  const m = await store.insert("memberships", {
    member_id: member.id,
    plan: "monthly",
    arm: "B",
    offer_code: "founding",
    price_cents: 2000,
    interval: "month",
    status: "active",
    founding: true,
    stripe_subscription_id: null,
    trial_end: null,
    current_period_end: new Date(Date.now() + 20 * DAY).toISOString(),
    first_paid_at: new Date(Date.now() - 10 * DAY).toISOString(),
    guarantee_until: new Date(Date.now() + 4 * DAY).toISOString(),
    cancel_at_period_end: false,
    canceled_at: null,
    paused_until: null,
    partner_seat: false,
    is_demo: false,
    ...patch,
  });
  return { member, m };
}

beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});

describe("cancel flow rules", () => {
  it("has at most two screens", () => {
    expect(cancelFlowScreens()).toHaveLength(2);
  });

  it("shows exactly one save offer: downgrade for price, pause for everything else", () => {
    const monthly = { plan: "monthly" as const, price_cents: 2000 };
    expect(saveOfferFor("expensive", monthly).kind).toBe("downgrade");
    for (const r of CANCEL_REASONS.filter((x) => x.code !== "expensive")) {
      expect(saveOfferFor(r.code, monthly).kind).toBe("pause");
    }
    expect(saveOfferFor(null, monthly).kind).toBe("pause");
    // already on Essentials: nothing cheaper to offer, so pause
    expect(saveOfferFor("expensive", { plan: "essentials", price_cents: 1200 }).kind).toBe("pause");
  });

  it("the save offer copy never uses guilt or the character's feelings", () => {
    for (const r of CANCEL_REASONS) {
      const o = saveOfferFor(r.code, { plan: "monthly", price_cents: 2000 });
      expect(`${o.heading} ${o.body}`).not.toMatch(/miss you|sad|disappoint|are you sure/i);
    }
  });
});

describe("cancel actions", () => {
  it("Finish canceling cancels immediately (no further charges), keeps access to period end, emails confirmation", async () => {
    const { m } = await makeMembership();
    const updated = await cancelMembership(store, m, "no_time", saveOfferFor("no_time", m));
    expect(updated.cancel_at_period_end).toBe(true);
    expect(updated.canceled_at).not.toBeNull();
    expect(updated.status).toBe("active"); // access until current_period_end
    const c = (await store.findOne("cancellations", { membership_id: m.id }))!;
    expect(c).toMatchObject({ reason: "no_time", offer_shown: "pause", outcome: "canceled" });
    const mail = (await store.findOne("outbox", { template: "F_cancel_confirmation" }))!;
    expect(mail.body).toMatch(/won't be charged again/);
  });

  it("undo restores the membership", async () => {
    const { m } = await makeMembership();
    const c = await cancelMembership(store, m, null, null);
    const u = (await undoCancel(store, c))!;
    expect(u.cancel_at_period_end).toBe(false);
    expect(u.canceled_at).toBeNull();
  });

  it("pause and downgrade are recorded as saves", async () => {
    const { m } = await makeMembership();
    const p = (await pauseMembership(store, m, 2, "traveling", saveOfferFor("traveling", m)))!;
    expect(p.status).toBe("paused");
    expect(new Date(p.paused_until!).getTime()).toBeGreaterThan(Date.now() + 55 * DAY);
    const { m: m2 } = await makeMembership();
    const d = (await downgradeToEssentials(store, m2, "expensive", saveOfferFor("expensive", m2)))!;
    expect(d.plan).toBe("essentials");
    expect(d.price_cents).toBe(1200);
    expect((await store.find("cancellations")).map((c) => c.outcome).sort()).toEqual(["saved_downgrade", "saved_pause"]);
  });

  it("self-serve refund works inside the guarantee window and releases the founding spot", async () => {
    const { member, m } = await makeMembership();
    await store.insert("sy_orders", { member_id: member.id, membership_id: m.id, email: member.email, offer_code: "founding", kind: "membership_charge", description: "x", amount_cents: 2000, status: "paid", stripe_payment_intent: null, stripe_invoice: null, checkout_intent_id: null, is_demo: false });
    expect(withinGuarantee(m)).toBe(true);
    const r = await refundMembership(store, m);
    expect(r).toMatchObject({ ok: true, refundedCents: 2000 });
    expect((await store.get("memberships", m.id))!.status).toBe("refunded");
  });

  it("refund is refused outside the window (a human handles those)", async () => {
    const { m } = await makeMembership({ guarantee_until: new Date(Date.now() - DAY).toISOString() });
    expect((await refundMembership(store, m)).ok).toBe(false);
  });
});

describe("48h pre-charge reminder job", () => {
  it("reminds trials 48h before the first charge, once, by email and SMS", async () => {
    const { m } = await makeMembership({ status: "trialing", arm: "A", founding: false, first_paid_at: null, current_period_end: new Date(Date.now() + 40 * 3_600_000).toISOString() });
    const r1 = await runReminders(store);
    expect(r1.sent).toBe(1);
    const r2 = await runReminders(store);
    expect(r2.sent).toBe(0);
    expect(await store.count("reminders", { membership_id: m.id })).toBe(1);
    const mail = (await store.findOne("outbox", { template: "C_pre_charge_48h" }))!;
    expect(mail.body).toMatch(/two screens at most/);
    expect(await store.count("outbox", { template: "S6_pre_charge" })).toBe(1);
  });

  it("doesn't remind too early, or for cancelled / paused memberships", async () => {
    await makeMembership({ status: "trialing", current_period_end: new Date(Date.now() + 72 * 3_600_000).toISOString() });
    await makeMembership({ status: "trialing", cancel_at_period_end: true, current_period_end: new Date(Date.now() + 24 * 3_600_000).toISOString() });
    expect((await runReminders(store)).sent).toBe(0);
  });

  it("F10/M7: reminds before every renewal, not just the first", async () => {
    const { member, m } = await makeMembership({ current_period_end: new Date(Date.now() + 30 * 3_600_000).toISOString() });
    await store.insert("sy_orders", { member_id: member.id, email: member.email, offer_code: "founding", kind: "membership_charge", description: "x", amount_cents: 2000, status: "paid", stripe_payment_intent: null, stripe_invoice: null, checkout_intent_id: null, is_demo: false });
    expect((await runReminders(store)).sent).toBe(1);
    await store.insert("sy_orders", { member_id: member.id, email: member.email, offer_code: "founding", kind: "membership_charge", description: "y", amount_cents: 2000, status: "paid", stripe_payment_intent: null, stripe_invoice: null, checkout_intent_id: null, is_demo: false });
    await store.update("memberships", m.id, { current_period_end: new Date(Date.now() + 31 * 3_600_000).toISOString() });
    expect((await runReminders(store)).sent).toBe(1);
    expect(await store.count("reminders", { membership_id: m.id, kind: "pre_charge_48h" })).toBe(2);
  });
});

describe("mock billing clock", () => {
  it("converts a due trial and ends a cancelled membership", async () => {
    const { m: trial } = await makeMembership({ status: "trialing", arm: "A", first_paid_at: null, guarantee_until: null, current_period_end: new Date(Date.now() - 60_000).toISOString() });
    const { m: ending } = await makeMembership({ cancel_at_period_end: true, current_period_end: new Date(Date.now() - 60_000).toISOString() });
    await runMockBillingClock(store);
    const t = (await store.get("memberships", trial.id))!;
    expect(t.status).toBe("active");
    expect(t.first_paid_at).not.toBeNull();
    expect(new Date(t.current_period_end!).getTime()).toBeGreaterThan(Date.now());
    expect((await store.get("memberships", ending.id))!.status).toBe("canceled");
  });
});

describe("Strong Weeks streak with grace", () => {
  const today = new Date("2026-10-01T12:00:00Z"); // Thursday; week starts Mon 2026-09-28
  it("counts consecutive weeks with 3+ sessions and doesn't break on the week in progress", () => {
    const days = ["2026-09-14", "2026-09-15", "2026-09-17", "2026-09-21", "2026-09-23", "2026-09-25", "2026-09-29"];
    const s = computeStrongWeeks(days, [], today);
    expect(s.streak).toBe(2);
    expect(s.thisWeek).toBe(1);
  });
  it("bridges one missed week automatically, and protected weeks always", () => {
    const days = ["2026-09-07", "2026-09-08", "2026-09-09", "2026-09-21", "2026-09-22", "2026-09-23"];
    expect(computeStrongWeeks(days, [], today).streak).toBe(2);
    const twoGaps = ["2026-08-24", "2026-08-25", "2026-08-26", "2026-09-07", "2026-09-08", "2026-09-09", "2026-09-21", "2026-09-22", "2026-09-23"];
    expect(computeStrongWeeks(twoGaps, [], today).streak).toBe(2);
    expect(computeStrongWeeks(twoGaps, ["2026-08-31"], today).streak).toBe(3);
  });
});
