/**
 * Round 6 (AUDIT_FINAL "Round 6: launch eve"), BRIEF.md CANON UPDATE 6: "$12 today = Starter Books + a 7-day trial of
 * the founding membership; first $25 charge on day 7, then every month".
 *  - the trial order (books line $12 + membership line $0 on the trial plan) provisions a TRIALING row that grants
 *    access only until trial_end + the float, never forever;
 *  - the day-7 charge arrives as a renewal order and converts the row: active, paid month from the charge date,
 *    14-day money-back window from the charge, founding seat handed back (the $0 checkout consumed one);
 *  - no renewal order by trial_end + grace: the row expires, the seat is released, the member is told honestly;
 *  - the pre-charge reminder goes out before day 7 with the amount, the date and the cancel path;
 *  - a day-7 charge that differs from the promised price opens a ticket; a second trial on one email is ticketed;
 *  - the welcome email states the full auto-renewal terms; /b sends a t12 visitor to the trial view.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/headers", () => ({
  cookies: async () => ({ get: () => undefined, getAll: () => [] }),
  headers: async () => ({ get: () => null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { handleShopifyWebhook } from "@/lib/billing/shopifyWebhook";
import { checkoutUrl, resolveFrontEnd, seedShopifyCatalog, shopifyConfig, type ShopifyAdmin } from "@/lib/billing/shopify";
import { runReminders, runShopifyLapses } from "@/lib/billing/clock";
import { bonusUnlocked, grantsAccess } from "@/lib/entitlement";
import { resetRateLimits } from "@/lib/rateLimit";

let store: MemoryStore;
let seq = 6000;
const nextId = () => `r12-${++seq}-0000-aaaa`;
const T0 = new Date("2026-10-09T12:00:00Z");
const DAY = 86_400_000;
const at = (days: number) => new Date(T0.getTime() + days * DAY);

beforeEach(async () => {
  vi.stubEnv("BILLING_PROVIDER", "shopify");
  vi.stubEnv("SHOPIFY_STORE_DOMAIN", "strongyears-test.myshopify.com");
  vi.stubEnv("SHOPIFY_GRACE_DAYS", "7");
  vi.stubEnv("SHOPIFY_LOCATION_ID", "77001");
  vi.stubEnv("LAUNCH_MODE", "live");
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
  resetRateLimits();
});
afterEach(() => vi.unstubAllEnvs());

/** The canon-6 order: Starter Books ($12, one-time) + founding variant on the 7-day-trial plan ($0 today). */
function trialOrder(id: number, o: { lines: [number, number]; at: Date; email?: string; name?: string }) {
  const email = o.email ?? "ruth@example.com";
  return {
    id,
    email,
    processed_at: o.at.toISOString(),
    source_name: "web",
    discount_codes: [],
    customer: { id: 4100 + id, email, first_name: o.name ?? "Ruth" },
    note_attributes: [
      { name: "sy_consent_price", value: "0.00|25.00" },
      { name: "sy_consent_sha", value: "a".repeat(64) },
      { name: "sy_sku", value: "bundle_t12" },
    ],
    line_items: [
      { id: o.lines[0], variant_id: 9000000012, title: "Starter Books", price: "12.00", quantity: 1, total_discount: "0.00", properties: [] },
      { id: o.lines[1], variant_id: 9000000025, title: "Founding membership", price: "25.00", quantity: 1, total_discount: "25.00", properties: [], selling_plan_allocation: { selling_plan: { id: 7000000070, name: "7-day trial, then $25 a month" } } },
    ],
  };
}

/** The day-7 charge: Shopify Subscriptions / the trial app create a renewal order for the contract. */
function chargeOrder(id: number, o: { line: number; at: Date; price?: string; email?: string }) {
  const email = o.email ?? "ruth@example.com";
  return {
    id,
    email,
    processed_at: o.at.toISOString(),
    source_name: "subscription_contract",
    discount_codes: [],
    customer: { id: 4101, email, first_name: "Ruth" },
    note_attributes: [],
    line_items: [{ id: o.line, variant_id: 9000000025, title: "Founding membership", price: o.price ?? "25.00", quantity: 1, total_discount: "0.00", properties: [], selling_plan_allocation: { selling_plan: { id: 7000000070, name: "7-day trial, then $25 a month" } } }],
  };
}

function mockAdmin(available = 4000): ShopifyAdmin & { adjustments: number[] } {
  const a = {
    mode: "mock" as const,
    adjustments: [] as number[],
    refundLine: vi.fn(async () => ({ ok: true, id: "r1" })),
    cancelContract: vi.fn(async () => ({ ok: false, error: "owned by the subscription app" })),
    adjustInventory: vi.fn(async (i: { delta: number }) => {
      a.adjustments.push(i.delta);
      available += i.delta;
      return { ok: true, available };
    }),
    allowOverselling: vi.fn(async () => ({ ok: true })),
  };
  return a;
}

async function outbox(template: string) {
  return (await store.find("outbox", { template })) as Array<{ subject: string | null; body: string; to: string }>;
}

describe("R12 canon 6: the 7-day trial end to end", () => {
  it("provisions a TRIALING founding row from the $12 books + $0 trial order, with the books unlocked and access bounded by trial_end + float", async () => {
    const r = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(1, { lines: [11, 12], at: T0 }), now: T0 });
    expect(r.status).toBe("processed");
    const m = (await store.find("memberships"))[0]!;
    expect(m.status).toBe("trialing");
    expect(m.arm).toBe("T");
    expect(m.founding).toBe(true);
    expect(m.price_cents).toBe(2500);
    expect(m.first_paid_at).toBeNull();
    expect(m.trial_end).toBe(at(7).toISOString());
    expect(m.current_period_end).toBe(at(7).toISOString());
    // Day 0 → day 7 + 7-day float: access. Day 15: no access (nothing was ever charged).
    expect(grantsAccess(m, at(0).getTime())).toBe(true);
    expect(grantsAccess(m, at(6.9).getTime())).toBe(true);
    expect(grantsAccess(m, at(13.9).getTime())).toBe(true);
    expect(grantsAccess(m, at(14.1).getTime())).toBe(false);
    // Bonus PDFs vest on the same day they would for a charge-today member (day 21 = trial end + 14), not during the trial.
    expect(bonusUnlocked(m, at(10).getTime())).toBe(false);
    expect(bonusUnlocked(m, at(21.1).getTime())).toBe(true);
    // The two lines: a $12 front-end order and a $0 membership charge, no consent-mismatch ticket ("0.00|25.00" was shown).
    const orders = await store.find("sy_orders");
    expect(orders.map((o) => [o.kind, o.amount_cents]).sort()).toEqual([["front_end", 1200], ["membership_charge", 0]]);
    expect((await store.find("support_tickets")).length).toBe(0);
    // The welcome states the full auto-renewal terms: date, amount, cadence, cancel path, "cancel before and it costs nothing".
    const w = await outbox("SH_welcome_trial");
    expect(w.length).toBe(1);
    expect(w[0]!.subject).toMatch(/7-day trial has started\. First charge .* unless you cancel/);
    expect(w[0]!.body).toMatch(/nothing was charged for the membership today/i);
    expect(w[0]!.body).toMatch(/charged \$25\.00, then \$25\.00 every month/);
    expect(w[0]!.body).toMatch(/Cancel online anytime/);
    expect(w[0]!.body).toMatch(/Cancel before .* and the membership costs nothing/);
    expect(w[0]!.body).not.toMatch(/for life|\$1\b|free trial/i);
  });

  it("the day-7 charge converts the trial: active, paid month from the charge date, money-back window from the charge, founding seat handed back", async () => {
    const admin = mockAdmin();
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(2, { lines: [21, 22], at: T0 }), now: T0, admin });
    const charged = at(7);
    const r = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: chargeOrder(3, { line: 31, at: charged }), now: charged, admin });
    expect(r.status).toBe("processed");
    expect(r.summary).toMatch(/renewal/);
    const m = (await store.find("memberships"))[0]!;
    expect(m.status).toBe("active");
    expect(m.first_paid_at).toBe(charged.toISOString());
    expect(m.guarantee_until).toBe(at(21).toISOString());
    expect(m.current_period_end).toBe("2026-11-16T12:00:00.000Z");
    expect(grantsAccess(m, at(30).getTime())).toBe(true);
    expect(grantsAccess(m, at(38.1).getTime())).toBe(true); // Nov 16 + 7-day float
    expect(grantsAccess(m, at(46).getTime())).toBe(false);
    // The seat: the $0 checkout consumed one; the renewal order consumed another and must hand it back (+1, once).
    expect(admin.adjustments).toEqual([1]);
    // One membership, two membership_charge lines ($0 then $25); a replay under a new webhook id changes nothing.
    expect((await store.find("memberships")).length).toBe(1);
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: chargeOrder(3, { line: 31, at: charged }), now: charged, admin });
    expect((await store.find("sy_orders", { kind: "membership_charge" })).map((o) => o.amount_cents).sort()).toEqual([0, 2500]);
    expect(admin.adjustments).toEqual([1]);
    expect((await store.find("support_tickets")).length).toBe(0);
    // The welcome for a converted trial is not re-sent; no "membership ended" mail.
    expect((await outbox("SH_welcome")).length).toBe(0);
    expect((await outbox("SH_trial_ended")).length).toBe(0);
  });

  it("no day-7 charge (cancelled in the trial, or the card failed and dunning gave up): the row lapses after trial_end + grace, the seat goes back, the member is told honestly", async () => {
    const admin = mockAdmin();
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(4, { lines: [41, 42], at: T0 }), now: T0, admin });
    // Inside the float nothing happens (a late renewal webhook may still come).
    expect(await runShopifyLapses(store, at(13))).toBe(0);
    expect((await store.find("memberships"))[0]!.status).toBe("trialing");
    // After it: expired, seat released (ledger row, idempotent by reference), honest email, no further access.
    expect(await runShopifyLapses(store, at(14.5))).toBe(1);
    const m = (await store.find("memberships"))[0]!;
    expect(m.status).toBe("expired");
    const ledger = await store.find("shopify_seat_ledger");
    expect(ledger.map((l) => l.ref)).toEqual(["strongyears://seat-ledger/trial-lapse/4"]);
    expect(ledger[0]!.delta).toBe(1);
    expect(grantsAccess(m, at(14.6).getTime())).toBe(false);
    const ended = await outbox("SH_trial_ended");
    expect(ended.length).toBe(1);
    expect(ended[0]!.body).toMatch(/no membership payment came through/);
    expect(ended[0]!.body).toMatch(/Nothing further is charged/);
    expect(ended[0]!.body).toMatch(/Starter Books are yours to keep/);
    // Idempotent.
    expect(await runShopifyLapses(store, at(15))).toBe(0);
    // A late charge after the lapse revives the row (the money came), exactly once.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: chargeOrder(5, { line: 51, at: at(16) }), now: at(16), admin });
    const revived = (await store.find("memberships"))[0]!;
    expect(revived.status).toBe("active");
    expect(grantsAccess(revived, at(20).getTime())).toBe(true);
  });

  it("the pre-charge reminder goes out before day 7 with the amount, the date, the cancel path and the conditional line", async () => {
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(6, { lines: [61, 62], at: T0 }), now: T0 });
    // Day 3: too early (48-hour horizon). Day 5.5: sent, once.
    expect((await runReminders(store, at(3))).sent).toBe(0);
    expect((await runReminders(store, at(5.5))).sent).toBe(1);
    expect((await runReminders(store, at(6))).sent).toBe(0);
    const r = await outbox("C_pre_charge_48h");
    expect(r.length).toBe(1);
    expect(r[0]!.body).toMatch(/7-day trial of Strong Years ends on/);
    expect(r[0]!.body).toMatch(/charge \$25\.00 on .* and then monthly/);
    expect(r[0]!.body).toMatch(/already cancelled it on your account page, nothing is charged/);
    expect(r[0]!.body).toContain(shopifyConfig.customerAccountUrl());
  });

  it("a day-7 charge that is not the promised $25 is ticketed before the next renewal; a second trial on the same email is ticketed", async () => {
    const admin = mockAdmin();
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(7, { lines: [71, 72], at: T0 }), now: T0, admin });
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: chargeOrder(8, { line: 81, at: at(7), price: "35.00" }), now: at(7), admin });
    const t1 = await store.find("support_tickets");
    expect(t1.length).toBe(1);
    expect(t1[0]!.message).toMatch(/first charge after the 7-day trial was \$35\.00 but the trial page promised \$25\.00/);
    // The same person starts another trial a month later (a second $0 checkout): provisioned, but a person looks at it.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(9, { lines: [91, 92], at: at(40) }), now: at(40), admin });
    const t2 = await store.find("support_tickets");
    expect(t2.length).toBe(2);
    expect(t2[1]!.message).toMatch(/second 7-day trial/);
  });

  it("/b sends the visitor to the trial view of the founding page; with no t12 row the store falls back to cell B without config changes", async () => {
    const rows = await store.find("shopify_products", { active: true });
    const fe = resolveFrontEnd(rows, { visitorId: "11111111-2222-4333-8444-555555555555", cohortOpen: true });
    expect(fe?.cell).toBe("t12");
    expect(fe?.row.trial_days).toBe(7);
    const url = checkoutUrl(fe!.row, { visitorId: "11111111-2222-4333-8444-555555555555", attribution: null, cell: "t12" });
    expect(url).toBe("https://strongyears-test.myshopify.com/products/founding-membership?view=trial&arm=T&vid=11111111-2222-4333-8444-555555555555&sku=bundle_t12");
    expect(url).not.toMatch(/discount|cart\//);
    // After the founding close: the standard trial row.
    expect(resolveFrontEnd(rows, { visitorId: "x", cohortOpen: false })?.row.sku).toBe("bundle_t12_standard");
    // A store whose verify run found no trial plan has no t12 rows: cell B (STARTER12) serves, same env.
    const noTrial = rows.filter((r) => !r.trial_days);
    const fb = resolveFrontEnd(noTrial, { visitorId: "x", cohortOpen: true });
    expect(fb?.cell).toBe("m12");
    expect(fb?.row.discount_code).toBe("STARTER12");
  });

  it("the trial row counts toward the founding cap until Shopify's inventory mirror exists", async () => {
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: trialOrder(10, { lines: [101, 102], at: T0 }), now: T0 });
    const { shopifyFoundingTaken } = await import("@/lib/billing/shopifyWebhook");
    expect(await shopifyFoundingTaken(store, 5000)).toBe(1);
  });
});
