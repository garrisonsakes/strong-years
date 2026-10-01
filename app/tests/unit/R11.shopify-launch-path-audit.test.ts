/**
 * Round 5 (AUDIT_FINAL "Round 5: Shopify launch path"): adversarial probes of the launch-path money truth.
 *  - a Shopify membership whose period ended with no renewal order (cancelled or dunned-out on Shopify's side,
 *    which never sends us a contract webhook) must stop granting access after the grace float;
 *  - a late renewal order revives a lapsed membership (the money came);
 *  - refunds/create arriving BEFORE orders/paid (a retried delivery) must not leave access open;
 *  - founding renewal orders hand the seat back and the cap closing never blocks renewals.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/headers", () => ({
  cookies: async () => ({ get: () => undefined, getAll: () => [] }),
  headers: async () => ({ get: () => null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { handleShopifyWebhook } from "@/lib/billing/shopifyWebhook";
import { seedShopifyCatalog, type ShopifyAdmin } from "@/lib/billing/shopify";
import { runShopifyLapses } from "@/lib/billing/clock";
import { grantsAccess } from "@/lib/entitlement";
import { resetRateLimits } from "@/lib/rateLimit";

let store: MemoryStore;
let seq = 5000;
const nextId = () => `r11-${++seq}-0000-aaaa`;

beforeEach(async () => {
  vi.stubEnv("BILLING_PROVIDER", "shopify");
  vi.stubEnv("SHOPIFY_STORE_DOMAIN", "strongyears-test.myshopify.com");
  vi.stubEnv("SHOPIFY_GRACE_DAYS", "7");
  vi.stubEnv("SHOPIFY_LOCATION_ID", "77001");
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
  resetRateLimits();
});
afterEach(() => vi.unstubAllEnvs());

function order(id: number, o: { line: number; variant?: string; plan?: string | null; price?: string; discount?: string; codes?: string[]; source?: string; at: string; email?: string }) {
  return {
    id,
    email: o.email ?? "ruth@example.com",
    processed_at: o.at,
    source_name: o.source ?? "web",
    discount_codes: (o.codes ?? []).map((code) => ({ code, amount: "13.00", type: "fixed_amount" })),
    customer: { id: 4001, email: o.email ?? "ruth@example.com", first_name: "Ruth" },
    note_attributes: [],
    line_items: [{ id: o.line, variant_id: Number(o.variant ?? "9000000025"), title: "Founding", price: o.price ?? "25.00", quantity: 1, total_discount: o.discount ?? "0.00", properties: [], ...(o.plan === null ? {} : { selling_plan_allocation: { selling_plan: { id: Number(o.plan ?? "7000000025"), name: "Monthly" } } }) }],
  };
}

function mockAdmin(available = 4000): ShopifyAdmin & { adjustments: number[]; continueCalls: number } {
  const a = {
    mode: "mock" as const,
    adjustments: [] as number[],
    continueCalls: 0,
    refundLine: vi.fn(async () => ({ ok: true, id: "r1" })),
    cancelContract: vi.fn(async () => ({ ok: false, error: "owned by Shopify Subscriptions" })),
    adjustInventory: vi.fn(async (i: { delta: number }) => {
      a.adjustments.push(i.delta);
      available += i.delta;
      return { ok: true, available };
    }),
    allowOverselling: vi.fn(async () => {
      a.continueCalls++;
      return { ok: true };
    }),
  };
  return a;
}

describe("R11 Shopify launch path: access follows the money, not the row", () => {
  it("a cancelled-on-Shopify membership (no renewal order) stops granting access after period end + grace, and the lapse job expires it", async () => {
    const t0 = new Date("2026-10-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(1, { line: 11, at: t0.toISOString(), codes: ["STARTER12"], discount: "13.00" }), now: t0 });
    const m = (await store.find("memberships"))[0]!;
    expect(m.status).toBe("active");
    expect(m.current_period_end).toBe("2026-11-01T12:00:00.000Z");
    // Inside the paid period and inside the 7-day float (a renewal webhook can be late): access.
    expect(grantsAccess(m, Date.parse("2026-10-31T00:00:00Z"))).toBe(true);
    expect(grantsAccess(m, Date.parse("2026-11-05T00:00:00Z"))).toBe(true);
    // Period end + grace passed with no renewal order: no access, even though the row still says "active".
    expect(grantsAccess(m, Date.parse("2026-11-09T00:00:00Z"))).toBe(false);
    const n = await runShopifyLapses(store, new Date("2026-11-09T00:00:00Z"));
    expect(n).toBe(1);
    const after = (await store.get("memberships", m.id))!;
    expect(after.status).toBe("expired");
    expect(grantsAccess(after)).toBe(false);
    // The job is idempotent and never touches rows still inside their period.
    expect(await runShopifyLapses(store, new Date("2026-11-10T00:00:00Z"))).toBe(0);
  });

  it("a late renewal order revives a lapsed (expired) Shopify membership and extends it from the payment date", async () => {
    const t0 = new Date("2026-10-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(2, { line: 21, at: t0.toISOString() }), now: t0 });
    const m = (await store.find("memberships"))[0]!;
    await runShopifyLapses(store, new Date("2026-11-12T00:00:00Z"));
    expect((await store.get("memberships", m.id))!.status).toBe("expired");
    const t1 = new Date("2026-11-15T09:00:00Z");
    const r = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(3, { line: 31, at: t1.toISOString(), source: "subscription_contract" }), now: t1, admin: mockAdmin() });
    expect(r.status).toBe("processed");
    const after = (await store.get("memberships", m.id))!;
    expect(after.status).toBe("active");
    expect(after.current_period_end).toBe("2026-12-15T09:00:00.000Z");
    expect(grantsAccess(after, t1.getTime())).toBe(true);
    expect((await store.find("memberships")).length).toBe(1);
  });

  it("refunds/create delivered BEFORE orders/paid (retried delivery): the later orders/paid grants nothing and a person is told", async () => {
    const t0 = new Date("2026-10-01T12:00:00Z");
    const admin = mockAdmin();
    const r1 = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "refunds/create", payload: { id: 77, order_id: 4, refund_line_items: [{ line_item_id: 41, quantity: 1, subtotal: "12.00" }] }, now: t0, admin });
    expect(r1.status).toBe("processed");
    const r2 = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(4, { line: 41, at: t0.toISOString(), codes: ["STARTER12"], discount: "13.00" }), now: t0, admin });
    expect(r2.status).toBe("processed");
    const m = (await store.find("memberships"))[0]!;
    expect(m.status).toBe("refunded");
    expect(grantsAccess(m, t0.getTime())).toBe(false);
    const o = (await store.find("sy_orders", { shopify_line_id: "41" }))[0]!;
    expect(o.status).toBe("refunded");
    expect((await store.find("support_tickets")).length).toBeGreaterThan(0);
  });

  it("founding renewals give the seat back (inventory +1, idempotent); the first charge does not; a refund of the first charge does", async () => {
    const admin = mockAdmin(4000);
    const t0 = new Date("2026-10-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(5, { line: 51, at: t0.toISOString() }), now: t0, admin });
    expect(admin.adjustments).toEqual([]);
    const t1 = new Date("2026-11-01T12:00:00Z");
    const renewal = order(6, { line: 61, at: t1.toISOString(), source: "subscription_contract" });
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: renewal, now: t1, admin });
    expect(admin.adjustments).toEqual([1]);
    // Same renewal under a new webhook id: no second adjustment.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: renewal, now: t1, admin });
    expect(admin.adjustments).toEqual([1]);
    // Refund of the FIRST charge (NO_RESTOCK, as the self-serve refund issues it): the seat goes back.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "refunds/create", payload: { id: 9, order_id: 5, restock: false, refund_line_items: [{ line_item_id: 51, quantity: 1, restock_type: "no_restock", subtotal: "25.00" }] }, now: t1, admin });
    expect(admin.adjustments).toEqual([1, 1]);
    // A refund Shopify already restocked is not credited twice.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(7, { line: 71, at: t0.toISOString(), email: "dee@example.com" }), now: t0, admin });
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "refunds/create", payload: { id: 10, order_id: 7, refund_line_items: [{ line_item_id: 71, quantity: 1, restock_type: "cancel", subtotal: "25.00" }] }, now: t1, admin });
    expect(admin.adjustments).toEqual([1, 1]);
  });

  it("with no location on file the seat return is not silently lost: a person is told and the ledger row is released for a retry", async () => {
    vi.stubEnv("SHOPIFY_LOCATION_ID", "");
    const admin = mockAdmin(4000);
    const t0 = new Date("2026-10-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(8, { line: 81, at: t0.toISOString() }), now: t0, admin });
    const t1 = new Date("2026-11-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(9, { line: 91, at: t1.toISOString(), source: "subscription_contract" }), now: t1, admin });
    expect(admin.adjustments).toEqual([]);
    expect((await store.find("shopify_seat_ledger")).length).toBe(0);
    expect((await store.find("support_tickets")).some((t) => /seat not returned/i.test(t.message))).toBe(true);
    // Once the inventory mirror knows the location, the next renewal adjusts.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "inventory_levels/update", payload: { inventory_item_id: 8000000025, location_id: 77002, available: 3999, updated_at: "2026-11-01T12:01:00Z" }, admin });
    const t2 = new Date("2026-12-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(10, { line: 101, at: t2.toISOString(), source: "subscription_contract" }), now: t2, admin });
    expect(admin.adjustInventory).toHaveBeenCalledWith(expect.objectContaining({ locationId: "77002", delta: 1 }));
  });

  it("when the founding variant's available stock reaches 0, the variant is switched to continue selling so existing members' renewals never fail, and a person is told to run close-founding", async () => {
    const admin = mockAdmin(0);
    const r = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "inventory_levels/update", payload: { inventory_item_id: 8000000025, location_id: 1, available: 0, updated_at: "2026-12-01T00:00:00Z" }, admin });
    expect(r.status).toBe("processed");
    expect(admin.continueCalls).toBe(1);
    expect((await store.find("support_tickets")).some((t) => /close-founding/.test(t.message))).toBe(true);
    // Not for other items, not when stock is positive.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "inventory_levels/update", payload: { inventory_item_id: 8000000025, location_id: 1, available: 12, updated_at: "2026-12-02T00:00:00Z" }, admin });
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "inventory_levels/update", payload: { inventory_item_id: 123, location_id: 1, available: 0, updated_at: "2026-12-02T00:00:00Z" }, admin });
    expect(admin.continueCalls).toBe(1);
  });
});
