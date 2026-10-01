/**
 * Round 10 (CANON UPDATE 2): Shopify webhooks provision and revoke access.
 * HMAC (forged, missing secret, wrong shop), replay (same id and same body under a
 * new id), out-of-order contract/billing events, grace period, refunds, customer
 * email change, app/uninstalled, the inventory-mirror founding counter and the
 * 14-day self-serve refund through a mocked Admin API.
 */
import { createHmac } from "node:crypto";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/headers", () => ({
  cookies: async () => ({ get: () => undefined, getAll: () => [] }),
  headers: async () => ({ get: () => null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { POST } from "@/app/api/webhooks/shopify/route";
import { handleShopifyWebhook, shopifyFoundingTaken } from "@/lib/billing/shopifyWebhook";
import { cartContextFromAttributes, refundShopifyMembership, seedShopifyCatalog, shopifyAdmin, verifyShopifyHmac, type ShopifyAdmin } from "@/lib/billing/shopify";
import { grantsAccess } from "@/lib/entitlement";
import { foundingTaken } from "@/lib/founding";
import { openCheckoutNow } from "@/lib/launch";
import { resetRateLimits } from "@/lib/rateLimit";

const SECRET = "shpss_test_secret_0123456789abcdef";
const SHOP = "strongyears-test.myshopify.com";
let store: MemoryStore;
let seq = 1000;

beforeEach(async () => {
  vi.stubEnv("BILLING_PROVIDER", "shopify");
  vi.stubEnv("SHOPIFY_WEBHOOK_SECRET", SECRET);
  vi.stubEnv("SHOPIFY_STORE_DOMAIN", SHOP);
  vi.stubEnv("SHOPIFY_CUSTOMER_ACCOUNT_URL", "https://shopify.com/12345/account");
  vi.stubEnv("FOUNDING_COHORT_CAP", "5000");
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
  resetRateLimits();
});
afterEach(() => {
  vi.unstubAllEnvs();
});

const sign = (body: string, secret = SECRET) => createHmac("sha256", secret).update(body).digest("base64");
const nextId = () => `wh-${++seq}-0000-aaaa`;

function req(topic: string, payload: unknown, opts: { id?: string; hmac?: string | null; shop?: string; raw?: string } = {}) {
  const body = opts.raw ?? JSON.stringify(payload);
  const h: Record<string, string> = { "content-type": "application/json", "x-shopify-topic": topic, "x-shopify-webhook-id": opts.id ?? nextId(), "x-shopify-shop-domain": opts.shop ?? SHOP };
  if (opts.hmac !== null) h["x-shopify-hmac-sha256"] = opts.hmac ?? sign(body);
  return new Request("http://localhost/api/webhooks/shopify", { method: "POST", headers: h, body });
}

function order(id: number, opts: { email?: string; lines?: { id: number; variant: string; plan?: string; price: string; discount?: string; props?: { name: string; value: string }[] }[]; attrs?: { name: string; value: string }[]; source?: string; customer?: number; codes?: string[]; processedAt?: string } = {}) {
  return {
    id,
    email: opts.email ?? "ruth@example.com",
    processed_at: opts.processedAt ?? new Date().toISOString(),
    source_name: opts.source ?? "web",
    discount_codes: (opts.codes ?? []).map((code) => ({ code, amount: "13.00", type: "fixed_amount" })),
    customer: { id: opts.customer ?? 4001, email: opts.email ?? "ruth@example.com", first_name: "Ruth" },
    note_attributes: opts.attrs ?? [],
    line_items: (opts.lines ?? [{ id: id * 10 + 1, variant: "9000000012", price: "12.00" }]).map((l) => ({
      id: l.id,
      variant_id: Number(l.variant),
      title: "x",
      price: l.price,
      quantity: 1,
      total_discount: l.discount ?? "0.00",
      properties: l.props ?? [],
      ...(l.plan ? { selling_plan_allocation: { selling_plan: { id: Number(l.plan), name: "Monthly" } } } : {}),
    })),
  };
}

const FOUNDING_LINE = (id: number) => ({ id, variant: "9000000025", plan: "7000000025", price: "25.00" });

async function deliver(topic: string, payload: unknown, id = nextId()) {
  return handleShopifyWebhook(store, { webhookId: id, topic, payload });
}

async function memberByEmail(email: string) {
  return (await store.findOne("members", { email }))!;
}

describe("R10 webhook route: HMAC, fail-closed, size", () => {
  it("accepts a correctly signed webhook", async () => {
    const res = await POST(req("orders/paid", order(1)));
    expect(res.status).toBe(200);
    expect((await res.json()).status).toBe("processed");
  });

  it("refuses a forged HMAC, a missing HMAC, a body signed with another secret, and a tampered body", async () => {
    const body = JSON.stringify(order(2));
    expect((await POST(req("orders/paid", null, { raw: body, hmac: "AAAA" }))).status).toBe(401);
    expect((await POST(req("orders/paid", null, { raw: body, hmac: null }))).status).toBe(401);
    expect((await POST(req("orders/paid", null, { raw: body, hmac: sign(body, "another-secret-0123456789") }))).status).toBe(401);
    const tampered = body.replace("12.00", "0.01");
    expect((await POST(req("orders/paid", null, { raw: tampered, hmac: sign(body) }))).status).toBe(401);
    expect(await store.count("members")).toBe(0);
  });

  it("fails closed with no secret configured (503, nothing processed)", async () => {
    vi.stubEnv("SHOPIFY_WEBHOOK_SECRET", "");
    const res = await POST(req("orders/paid", order(3)));
    expect(res.status).toBe(503);
    expect(await store.count("sy_orders")).toBe(0);
  });

  it("refuses another shop's webhook, oversized bodies and bad JSON", async () => {
    expect((await POST(req("orders/paid", order(4), { shop: "evil.myshopify.com" }))).status).toBe(401);
    const big = "x".repeat(1024 * 1024 + 10);
    expect((await POST(req("orders/paid", null, { raw: big }))).status).toBe(413);
    expect((await POST(req("orders/paid", null, { raw: "{not json" }))).status).toBe(400);
  });

  it("verifyShopifyHmac is constant-shape: wrong-length and junk headers are false", () => {
    expect(verifyShopifyHmac("a", "", SECRET)).toBe(false);
    expect(verifyShopifyHmac("a", "!!!", SECRET)).toBe(false);
    expect(verifyShopifyHmac("a", sign("a"), "")).toBe(false);
    expect(verifyShopifyHmac("a", sign("a"), SECRET)).toBe(true);
  });
});

describe("R10 orders/paid provisioning", () => {
  it("an ebook order creates the member and a front-end order, but no membership", async () => {
    await deliver("orders/paid", order(10));
    const m = await memberByEmail("ruth@example.com");
    expect(m.shopify_customer_id).toBe("4001");
    expect(m.email_verified_at).toBeNull(); // paying proves nothing about the inbox
    expect(await store.count("memberships", { member_id: m.id })).toBe(0);
    const o = (await store.find("sy_orders", { member_id: m.id }))[0]!;
    expect(o).toMatchObject({ kind: "front_end", amount_cents: 1200, processor: "shopify", shopify_order_id: "10" });
  });

  it("a founding order creates an active founding membership with the 14-day guarantee and a welcome email (link, no password)", async () => {
    await deliver("orders/paid", order(11, { lines: [FOUNDING_LINE(111)], attrs: [{ name: "sy_cell", value: "e12" }] }));
    const m = await memberByEmail("ruth@example.com");
    const ms = (await store.find("memberships", { member_id: m.id }))[0]!;
    expect(ms).toMatchObject({ status: "active", founding: true, price_cents: 2500, plan: "monthly", processor: "shopify", shopify_origin_order_id: "11", price_cell: "e12" });
    const days = (new Date(ms.guarantee_until!).getTime() - new Date(ms.first_paid_at!).getTime()) / 86_400_000;
    expect(days).toBe(14);
    expect(grantsAccess(ms)).toBe(true);
    const mail = await store.findOne("outbox", { template: "SH_welcome" });
    expect(mail?.body).toContain("/login");
    expect(mail?.body).not.toMatch(/token=[A-Za-z0-9]/); // the link is redacted in the stored copy
  });

  it("cell B: the founding line + STARTER12 (first payment only) maps to bundle_m12: a founding membership renewing at $25, books included; without the code the same line is founding_monthly", async () => {
    await deliver("orders/paid", order(12, { lines: [{ id: 121, variant: "9000000025", plan: "7000000025", price: "25.00", discount: "13.00" }], codes: ["STARTER12"] }));
    const ms = (await store.find("memberships"))[0]!;
    expect(ms).toMatchObject({ offer_code: "bundle_m12", founding: true, price_cents: 2500, price_cell: "m12" });
    expect((await store.find("sy_orders"))[0]).toMatchObject({ kind: "membership_charge", amount_cents: 1200 });
    await deliver("orders/paid", order(14, { email: "plain@example.com", customer: 4014, lines: [{ id: 141, variant: "9000000025", plan: "7000000025", price: "25.00" }] }));
    const plain = (await store.find("memberships", { member_id: (await memberByEmail("plain@example.com")).id }))[0]!;
    expect(plain).toMatchObject({ offer_code: "founding_monthly", price_cents: 2500 });
    // a code on the order never re-maps a one-time line to a membership
    await deliver("orders/paid", order(15, { email: "books@example.com", customer: 4015, lines: [{ id: 151, variant: "9000000012", price: "12.00" }], codes: ["STARTER12"] }));
    expect((await store.find("sy_orders", { email: "books@example.com" }))[0]).toMatchObject({ kind: "front_end", offer_code: "ebook_e12" });
  });

  it("a Shopify Subscriptions renewal order (orders/paid, source_name subscription_contract) extends the paid-through date by one period; a replay does not extend it twice", async () => {
    const t0 = new Date("2026-10-01T12:00:00Z");
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: order(20, { lines: [{ id: 201, variant: "9000000025", plan: "7000000025", price: "25.00", discount: "13.00" }], codes: ["STARTER12"], processedAt: t0.toISOString() }), now: t0 });
    const first = (await store.find("memberships"))[0]!;
    expect(first.current_period_end).toBe("2026-11-01T12:00:00.000Z");
    const t1 = new Date("2026-11-01T12:05:00Z");
    const renewal = order(21, { lines: [{ id: 211, variant: "9000000025", plan: "7000000025", price: "25.00" }], source: "subscription_contract", processedAt: t1.toISOString() });
    expect((await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: renewal, now: t1 })).status).toBe("processed");
    let m = (await store.get("memberships", first.id))!;
    expect(m.current_period_end).toBe("2026-12-01T12:05:00.000Z");
    expect(m.status).toBe("active");
    expect((await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/paid", payload: renewal, now: t1 })).status).toBe("ignored");
    m = (await store.get("memberships", first.id))!;
    expect(m.current_period_end).toBe("2026-12-01T12:05:00.000Z");
    // no renewal order by the period end + grace → access lapses on its own (that is how a cancellation made in
    // Shopify's account page shows up here; contract webhooks never reach us on the launch path)
    const { grantsAccess } = await import("@/lib/entitlement");
    expect(grantsAccess(m, new Date("2026-11-20T00:00:00Z").getTime())).toBe(true);
  });

  it("orders/cancelled on a provisioned membership order ends the membership and voids the lines", async () => {
    await deliver("orders/paid", order(30, { lines: [FOUNDING_LINE(301)] }));
    const before = (await store.find("memberships"))[0]!;
    expect(before.status).toBe("active");
    expect((await deliver("orders/cancelled", { id: 30 })).status).toBe("processed");
    expect((await store.get("memberships", before.id))!.status).toBe("refunded");
    expect((await store.find("sy_orders", { shopify_order_id: "30" }))[0]!.status).toBe("refunded");
    expect((await deliver("orders/cancelled", { id: 999 })).status).toBe("ignored");
  });

  it("cart attributes become first/last-touch attribution, validated and length-limited; junk and oversized values are dropped", async () => {
    const attrs = [
      { name: "sy_ft_post_id", value: "C8xYz12AbC" },
      { name: "sy_ft_platform", value: "instagram" },
      { name: "sy_ft_keyword", value: "join" },
      { name: "sy_ft_page", value: "<script>alert(1)</script>" },
      { name: "sy_lt_post_id", value: "TT_77" },
      { name: "sy_ft_utm_campaign", value: "x".repeat(101) },
      { name: "sy_price", value: "1" },
      { name: "not_ours", value: "y" },
    ];
    await deliver("orders/paid", order(13, { attrs }));
    const m = await memberByEmail("ruth@example.com");
    expect(m.attribution).toMatchObject({ post_id: "C8xYz12AbC", platform: "ig", keyword: "JOIN", last_touch: { post_id: "TT_77" } });
    expect(m.attribution?.page).toBeUndefined();
    expect(m.attribution?.utm_campaign).toBeUndefined();
    expect(JSON.stringify(m.attribution)).not.toContain("sy_price");
  });

  it("attribution is never pricing-relevant: the amount and entitlement come from the order line and the catalog row", () => {
    const ctx = cartContextFromAttributes([{ name: "sy_cell", value: "e7" }, { name: "sy_sku", value: "founding_monthly" }]);
    // consentPricesCents is what the page SHOWED (R5-8): it is compared with the charge, never used to set it
    expect(Object.keys(ctx)).toEqual(["attribution", "cell", "visitorId", "consentPricesCents"]);
    expect(ctx.consentPricesCents).toEqual([]);
  });

  it("an unmapped variant grants nothing and opens a ticket", async () => {
    const r = await deliver("orders/paid", order(14, { lines: [{ id: 141, variant: "123", price: "99.00" }] }));
    expect(r.status).toBe("ignored");
    expect(await store.count("memberships")).toBe(0);
    expect(await store.findOne("support_tickets", { reason: "shopify_review" })).not.toBeNull();
  });

  it("a gift order emails the recipient a claim link and doesn't create a membership for the buyer", async () => {
    await deliver("orders/paid", order(15, { lines: [{ id: 151, variant: "9000000049", price: "49.00", props: [{ name: "Recipient name", value: "Mom" }, { name: "Recipient email", value: "mom@example.com" }] }] }));
    expect(await store.findOne("gifts", { recipient_email: "mom@example.com" })).toMatchObject({ months: 3, amount_cents: 4900 });
    expect(await store.count("memberships")).toBe(0);
  });

  it("an order paid while still in prelaunch is provisioned (money was taken) but flagged for a person", async () => {
    vi.stubEnv("LAUNCH_MODE", "prelaunch");
    await deliver("orders/paid", order(16, { lines: [FOUNDING_LINE(161)] }));
    expect(await store.count("memberships")).toBe(1);
    const t = await store.find("support_tickets", { reason: "shopify_review" });
    expect(t.some((x) => /prelaunch/.test(x.message))).toBe(true);
  });
});

describe("R10 replay and idempotency", () => {
  it("the same webhook id twice is a duplicate", async () => {
    const id = nextId();
    expect((await deliver("orders/paid", order(20, { lines: [FOUNDING_LINE(201)] }), id)).status).toBe("processed");
    expect((await deliver("orders/paid", order(20, { lines: [FOUNDING_LINE(201)] }), id)).status).toBe("duplicate");
    expect(await store.count("memberships")).toBe(1);
  });

  it("the same signed body replayed under a NEW webhook id (the header isn't covered by the HMAC) changes nothing", async () => {
    const body = JSON.stringify(order(21, { lines: [FOUNDING_LINE(211)] }));
    expect((await POST(req("orders/paid", null, { raw: body }))).status).toBe(200);
    const again = await POST(req("orders/paid", null, { raw: body }));
    expect((await again.json()).status).toBe("ignored");
    expect(await store.count("memberships")).toBe(1);
    expect(await store.count("sy_orders")).toBe(1);
    expect(await store.count("outbox", { template: "SH_welcome" })).toBe(1);
  });

  it("a handler error releases the claim so Shopify's retry is processed", async () => {
    const orig = store.find.bind(store);
    const spy = vi.spyOn(store, "find").mockImplementation(((t: string, ...rest: unknown[]) => (t === "shopify_products" ? Promise.reject(new Error("db down")) : (orig as (...a: unknown[]) => unknown)(t, ...rest))) as typeof store.find);
    const id = nextId();
    await expect(deliver("orders/paid", order(22), id)).rejects.toThrow("db down");
    spy.mockRestore();
    expect((await deliver("orders/paid", order(22), id)).status).toBe("processed");
  });
});

describe("R10 subscription contracts and billing attempts (out of order)", () => {
  async function founding(orderId: number) {
    await deliver("orders/paid", order(orderId, { lines: [FOUNDING_LINE(orderId * 10)] }));
    await deliver("subscription_contracts/create", { id: orderId + 500, origin_order_id: orderId, status: "active", revision_id: 1, customer_id: 4001 });
    return (await store.findOne("memberships", { shopify_origin_order_id: String(orderId) }))!;
  }

  it("a contract event that arrives before its order is deferred (503 → Shopify retries), then applies", async () => {
    const r = await deliver("subscription_contracts/create", { id: 9001, origin_order_id: 30, status: "active", revision_id: 1 });
    expect(r.status).toBe("deferred");
    const res = await POST(req("subscription_contracts/create", { id: 9001, origin_order_id: 30, status: "active", revision_id: 1 }));
    expect(res.status).toBe(503);
    await deliver("orders/paid", order(30, { lines: [FOUNDING_LINE(301)] }));
    expect((await deliver("subscription_contracts/create", { id: 9001, origin_order_id: 30, status: "active", revision_id: 1 })).status).toBe("processed");
    expect(await store.findOne("memberships", { shopify_contract_id: "9001" })).toMatchObject({ status: "active" });
  });

  it("an older contract revision arriving after a newer one is ignored (cancel at rev 3, stale 'active' at rev 2)", async () => {
    const m = await founding(31);
    await deliver("subscription_contracts/update", { id: 531, status: "cancelled", revision_id: 3 });
    const stale = await deliver("subscription_contracts/update", { id: 531, status: "active", revision_id: 2 });
    expect(stale.status).toBe("ignored");
    const now = (await store.get("memberships", m.id))!;
    expect(now).toMatchObject({ status: "canceled", cancel_at_period_end: true, shopify_revision: 3 });
    expect(grantsAccess(now)).toBe(true); // access to the end of the paid period
    expect(grantsAccess(now, new Date(now.current_period_end!).getTime() + 1000)).toBe(false);
  });

  it("pause and resume follow the contract", async () => {
    const m = await founding(32);
    await deliver("subscription_contracts/pause", { id: 532, status: "paused", revision_id: 2 });
    expect(grantsAccess(await store.get("memberships", m.id))).toBe(false);
    await deliver("subscription_contracts/activate", { id: 532, status: "active", revision_id: 3 });
    expect(await store.get("memberships", m.id)).toMatchObject({ status: "active" });
  });

  it("a failed billing attempt opens a grace period; after it access stops; a later success restores it", async () => {
    const m = await founding(33);
    const t0 = new Date();
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "subscription_billing_attempts/failure", payload: { id: 7001, subscription_contract_id: 533, ready: true, error_code: "card_declined" }, now: t0 });
    const failed = (await store.get("memberships", m.id))!;
    expect(failed.status).toBe("past_due");
    expect(grantsAccess(failed, t0.getTime() + 86_400_000)).toBe(true);
    expect(grantsAccess(failed, t0.getTime() + 8 * 86_400_000)).toBe(false);
    expect(await store.count("outbox", { template: "SH_payment_failed" })).toBe(1);
    // A second failure doesn't extend the grace or email again.
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "subscription_billing_attempts/failure", payload: { id: 7002, subscription_contract_id: 533 }, now: new Date(t0.getTime() + 3 * 86_400_000) });
    expect((await store.get("memberships", m.id))!.grace_until).toBe(failed.grace_until);
    expect(await store.count("outbox", { template: "SH_payment_failed" })).toBe(1);
    await deliver("subscription_billing_attempts/success", { id: 7003, subscription_contract_id: 533, order_id: 99 });
    const ok = (await store.get("memberships", m.id))!;
    expect(ok).toMatchObject({ status: "active", grace_until: null });
    expect(new Date(ok.current_period_end!).getTime()).toBeGreaterThan(Date.now() + 25 * 86_400_000);
  });

  it("an older billing failure delivered after a newer success changes nothing", async () => {
    const m = await founding(34);
    await deliver("subscription_billing_attempts/success", { id: 8002, subscription_contract_id: 534 });
    const r = await deliver("subscription_billing_attempts/failure", { id: 8001, subscription_contract_id: 534 });
    expect(r.status).toBe("ignored");
    expect(await store.get("memberships", m.id)).toMatchObject({ status: "active", grace_until: null });
  });

  it("a renewal order (source subscription_contract) records a charge on the existing membership, no second membership", async () => {
    const m = await founding(35);
    await deliver("orders/paid", order(36, { lines: [FOUNDING_LINE(361)], source: "subscription_contract" }));
    expect(await store.count("memberships")).toBe(1);
    expect(await store.count("sy_orders", { membership_id: m.id, kind: "membership_charge" })).toBe(2);
    expect(await store.count("outbox", { template: "SH_welcome" })).toBe(1);
  });
});

describe("R10 refunds, customers, uninstall", () => {
  it("refunds/create on the membership line ends access and cancels the contract", async () => {
    await deliver("orders/paid", order(40, { lines: [FOUNDING_LINE(401)] }));
    await deliver("subscription_contracts/create", { id: 540, origin_order_id: 40, status: "active", revision_id: 1 });
    const admin: ShopifyAdmin = { mode: "mock", refundLine: vi.fn(), cancelContract: vi.fn(async () => ({ ok: true })) };
    await handleShopifyWebhook(store, { webhookId: nextId(), topic: "refunds/create", payload: { id: 1, order_id: 40, refund_line_items: [{ line_item_id: 401, quantity: 1, subtotal: "25.00" }] }, admin });
    const m = (await store.findOne("memberships", { shopify_origin_order_id: "40" }))!;
    expect(m.status).toBe("refunded");
    expect(grantsAccess(m)).toBe(false);
    expect(admin.cancelContract).toHaveBeenCalledWith("540");
    // The same refund again (orders/refunded shape) is a no-op.
    const again = await handleShopifyWebhook(store, { webhookId: nextId(), topic: "orders/refunded", payload: { id: 40, refunds: [{ id: 1, order_id: 40, refund_line_items: [{ line_item_id: 401, subtotal: "25.00" }] }] }, admin });
    expect(again.status).toBe("ignored");
  });

  it("a partial refund doesn't end access", async () => {
    await deliver("orders/paid", order(41, { lines: [FOUNDING_LINE(411)] }));
    await deliver("refunds/create", { id: 2, order_id: 41, refund_line_items: [{ line_item_id: 411, subtotal: "5.00" }] });
    expect(await store.findOne("memberships", { shopify_origin_order_id: "41" })).toMatchObject({ status: "active" });
  });

  it("customers/update: name updates; an email change re-requires inbox proof and ends sessions; a collision isn't merged; stale updates are ignored", async () => {
    await deliver("orders/paid", order(42, { customer: 4242, email: "a@example.com" }));
    const before = await memberByEmail("a@example.com");
    await store.update("members", before.id, { email_verified_at: new Date().toISOString() });
    await deliver("customers/update", { id: 4242, email: "A.New@Example.com", first_name: "Ann", updated_at: "2026-10-02T10:00:00Z" });
    const after = (await store.get("members", before.id))!;
    expect(after).toMatchObject({ email: "a.new@example.com", first_name: "Ann", email_verified_at: null });
    expect(after.session_version).toBe(before.session_version + 1);
    expect((await deliver("customers/update", { id: 4242, email: "old@example.com", updated_at: "2026-10-01T10:00:00Z" })).status).toBe("ignored");
    await deliver("orders/paid", order(43, { customer: 4343, email: "b@example.com" }));
    await deliver("customers/update", { id: 4343, email: "a.new@example.com", updated_at: "2026-10-03T10:00:00Z" });
    expect(await memberByEmail("b@example.com")).not.toBeNull();
  });

  it("app/uninstalled alerts a person and keeps members' access", async () => {
    await deliver("orders/paid", order(44, { lines: [FOUNDING_LINE(441)] }));
    await deliver("app/uninstalled", { id: 1, domain: SHOP });
    expect((await store.find("support_tickets")).some((t) => /uninstalled/.test(t.message))).toBe(true);
    expect(grantsAccess((await store.find("memberships"))[0]!)).toBe(true);
  });

  it("unknown topics are ignored and malformed webhook ids rejected", async () => {
    expect((await deliver("products/update", {})).status).toBe("ignored");
    expect((await handleShopifyWebhook(store, { webhookId: "x", topic: "orders/paid", payload: order(45) })).status).toBe("ignored");
  });
});

describe("R10 founding counter = DB mirror of the founding plan inventory", () => {
  it("falls back to founding memberships, then follows inventory_levels/update (stale levels ignored)", async () => {
    await deliver("orders/paid", order(50, { lines: [FOUNDING_LINE(501)] }));
    expect(await foundingTaken(store)).toBe(1);
    await deliver("inventory_levels/update", { inventory_item_id: 8000000025, location_id: 1, available: 4990, updated_at: "2026-10-02T10:00:00Z" });
    expect(await foundingTaken(store)).toBe(10);
    await deliver("inventory_levels/update", { inventory_item_id: 8000000025, location_id: 1, available: 4999, updated_at: "2026-10-02T09:00:00Z" });
    expect(await shopifyFoundingTaken(store, 5000)).toBe(10);
    await deliver("inventory_levels/update", { inventory_item_id: 8000000025, location_id: 1, available: 0, updated_at: "2026-10-02T11:00:00Z" });
    expect(await foundingTaken(store)).toBe(5000);
  });
});

describe("R10 14-day self-serve refund via the Shopify Admin API (mocked)", () => {
  async function setup() {
    await openCheckoutNow(store, "test");
    await deliver("orders/paid", order(60, { lines: [FOUNDING_LINE(601)] }));
    await deliver("subscription_contracts/create", { id: 560, origin_order_id: 60, status: "active", revision_id: 1 });
    return (await store.findOne("memberships", { shopify_origin_order_id: "60" }))!;
  }

  it("refunds the first membership charge, cancels the contract and ends access; once per person", async () => {
    const m = await setup();
    const admin: ShopifyAdmin = { mode: "live", refundLine: vi.fn(async () => ({ ok: true, id: "r1" })), cancelContract: vi.fn(async () => ({ ok: true })) };
    const r = await refundShopifyMembership(store, m, new Date(), admin);
    expect(r).toMatchObject({ ok: true, state: "done", refundedCents: 2500 });
    expect(admin.refundLine).toHaveBeenCalledWith(expect.objectContaining({ orderId: "60", lineItemId: "601", amountCents: 2500 }));
    expect(admin.cancelContract).toHaveBeenCalledWith("560");
    expect(await store.get("memberships", m.id)).toMatchObject({ status: "refunded" });
    // A second membership later: the guarantee was used.
    await deliver("orders/paid", order(61, { lines: [FOUNDING_LINE(611)] }));
    const m2 = (await store.findOne("memberships", { shopify_origin_order_id: "61" }))!;
    expect((await refundShopifyMembership(store, m2, new Date(), admin)).state).toBe("review");
  });

  it("outside 14 days: ineligible; Shopify refusing: a person, nothing changed; a double tap refunds once", async () => {
    const m = await setup();
    expect((await refundShopifyMembership(store, m, new Date(Date.now() + 15 * 86_400_000))).state).toBe("ineligible");
    const refusing: ShopifyAdmin = { mode: "live", refundLine: async () => ({ ok: false, error: "nope" }), cancelContract: async () => ({ ok: true }) };
    expect((await refundShopifyMembership(store, m, new Date(), refusing)).state).toBe("review");
    expect(await store.get("memberships", m.id)).toMatchObject({ status: "active" });
    const slow: ShopifyAdmin = { mode: "live", refundLine: vi.fn(async () => ({ ok: true, id: "r" })), cancelContract: async () => ({ ok: true }) };
    const [a, b] = await Promise.all([refundShopifyMembership(store, m, new Date(), slow), refundShopifyMembership(store, m, new Date(), slow)]);
    expect([a.ok, b.ok].filter(Boolean)).toHaveLength(1);
    expect(slow.refundLine).toHaveBeenCalledTimes(1);
  });

  it("the Admin client: mock without a token locally, off on a deploy, GraphQL with the token in a header (never the URL)", async () => {
    expect(shopifyAdmin({ NODE_ENV: "test" }).mode).toBe("mock");
    expect(shopifyAdmin({ NODE_ENV: "production" }).mode).toBe("off");
    expect((await shopifyAdmin({ NODE_ENV: "production" }).refundLine({ orderId: "1", lineItemId: null, amountCents: 1, note: "" })).ok).toBe(false);
    const calls: { url: string; init: RequestInit }[] = [];
    const fake = async (url: string, init: RequestInit) => {
      calls.push({ url, init });
      const q = JSON.parse(String(init.body)).query as string;
      const data = q.includes("transactions") && !q.includes("refundCreate") ? { order: { transactions: [{ id: "gid://shopify/OrderTransaction/9", kind: "SALE", status: "SUCCESS", gateway: "shopify_payments" }] } } : { refundCreate: { refund: { id: "gid://shopify/Refund/77" }, userErrors: [] } };
      return new Response(JSON.stringify({ data }), { status: 200 });
    };
    const admin = shopifyAdmin({ SHOPIFY_ADMIN_TOKEN: "shpat_secret", SHOPIFY_STORE_DOMAIN: SHOP }, fake);
    expect(await admin.refundLine({ orderId: "60", lineItemId: "601", amountCents: 2500, note: "t" })).toEqual({ ok: true, id: "77" });
    expect(calls[0]!.url).toBe(`https://${SHOP}/admin/api/2026-07/graphql.json`);
    expect(calls.every((c) => !c.url.includes("shpat_secret"))).toBe(true);
    expect((calls[0]!.init.headers as Record<string, string>)["X-Shopify-Access-Token"]).toBe("shpat_secret");
    expect(JSON.parse(String(calls[1]!.init.body)).variables.input.transactions[0]).toMatchObject({ amount: "25.00", kind: "REFUND", parentId: "gid://shopify/OrderTransaction/9" });
  });
});
