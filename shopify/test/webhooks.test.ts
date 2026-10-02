import { describe, it, expect } from "vitest";
import { createHmac } from "node:crypto";
import { verifyShopifyHmac, parseAttribution, classifyOrder, isStarterCellB, affiliateCode } from "../src/webhooks.ts";
import { seatActions, countLine } from "../src/seatLedger.ts";
import { signJwt, verifyJwt, handleOffer, handleSignChangeset, FOUNDING_TERMS_SHA256, type OfferEnv } from "../app-postpurchase/server/postPurchase.ts";

describe("webhook HMAC", () => {
  it("accepts Shopify's base64 HMAC of the raw body and rejects tampering", () => {
    const body = JSON.stringify({ id: 1 });
    const h = createHmac("sha256", "s3cret").update(body).digest("base64");
    expect(verifyShopifyHmac(body, h, "s3cret")).toBe(true);
    expect(verifyShopifyHmac(body + " ", h, "s3cret")).toBe(false);
    expect(verifyShopifyHmac(body, h, "other")).toBe(false);
    expect(verifyShopifyHmac(body, null, "s3cret")).toBe(false);
  });
});

describe("attribution from order note_attributes", () => {
  const notes = [
    { name: "sy_ft_utm_source", value: "ig" }, { name: "sy_ft_post_id", value: "C9abc" }, { name: "sy_ft_keyword", value: "STRONG" },
    { name: "sy_ft_character", value: "chang" }, { name: "sy_ft_at", value: "2026-10-01T10:00:00Z" },
    { name: "sy_lt_utm_source", value: "email" }, { name: "sy_lt_page", value: "duo" },
    { name: "sy_cell", value: "m12" }, { name: "sy_arm", value: "B" }, { name: "sy_vid", value: "0b8f9a52-6f3e-4c0e-9a51-2c1f1d3a8b7e" },
    { name: "sy_sku", value: "bundle_m12" }, { name: "sy_entry", value: "starter" },
    { name: "sy_consent_sha", value: "a".repeat(64) }, { name: "sy_consent_at", value: "2026-10-01T10:01:00Z" }, { name: "sy_consent_price", value: "25.00" },
    { name: "evil", value: "x" }, { name: "sy_ft_utm_campaign", value: "x".repeat(101) },
  ];
  it("reads the flat sy_ keys the theme writes, ignores unknown or oversized values", () => {
    const a = parseAttribution(notes);
    expect(a.firstTouch).toEqual({ utm_source: "ig", post_id: "C9abc", keyword: "STRONG", character: "chang", at: "2026-10-01T10:00:00Z" });
    expect(a.lastTouch).toEqual({ utm_source: "email", page: "duo" });
    expect(a).toMatchObject({ cell: "m12", arm: "B", sku: "bundle_m12", entry: "starter" });
    expect(a.consent?.sha256).toHaveLength(64);
  });
});

describe("order classification (initial and renewal orders)", () => {
  const order = (skus: string[], codes: string[] = []) => ({ id: 1, line_items: skus.map((sku, i) => ({ id: i, sku, price: "1", quantity: 1, properties: sku.startsWith("SY-GIFT") ? [{ name: "Recipient email", value: "mom@example.com" }, { name: "Start date", value: "2026-12-25" }] : [] })), discount_codes: codes.map((code) => ({ code })) });
  it("maps SKUs to grants", () => {
    expect(classifyOrder(order(["SY-BOOKS-E12", "SY-WALLPLAN-9"]))).toEqual([{ kind: "ebook", role: "ebook" }, { kind: "addon", role: "bump_wallplan" }]);
    expect(classifyOrder(order(["SY-FOUNDING-25"]))).toEqual([{ kind: "membership", role: "founding", months: 1 }]);
    expect(classifyOrder(order(["SY-ANNUAL-249"]))[0].months).toBe(12);
    expect(classifyOrder(order(["SY-GIFT-12M"]))[0]).toMatchObject({ kind: "gift", months: 12, recipientEmail: "mom@example.com", giftStart: "2026-12-25" });
  });
  it("detects cell B and affiliate codes", () => {
    expect(isStarterCellB(order(["SY-FOUNDING-25"], ["STARTER12"]))).toBe(true);
    expect(isStarterCellB(order(["SY-FOUNDING-25"]))).toBe(false);
    expect(affiliateCode(order(["SY-BOOKS-E7"], ["chang"]))).toBe("CHANG");
  });
});

describe("founding seat ledger", () => {
  const ctx = (o: Partial<Parameters<typeof seatActions>[1]> = {}) => ({ inventoryItemId: "gid://shopify/InventoryItem/1", locationId: "gid://shopify/Location/1", productId: "gid://shopify/Product/1", variantId: "gid://shopify/ProductVariant/1", customerHadPriorFoundingOrder: false, processedRefs: new Set<string>(), ...o });
  it("first paid founding order consumes a seat (no action)", () => {
    expect(seatActions({ topic: "orders/paid", orderId: "10", foundingQty: 1 }, ctx(), 5000)).toEqual([]);
  });
  it("renewal orders give the seat back, once (idempotent by reference URI)", () => {
    const a = seatActions({ topic: "orders/paid", orderId: "11", foundingQty: 1 }, ctx({ customerHadPriorFoundingOrder: true }), 5000);
    expect(a).toHaveLength(1);
    expect((a[0].variables as any).input.changes[0].delta).toBe(1);
    expect(seatActions({ topic: "orders/paid", orderId: "11", foundingQty: 1 }, ctx({ customerHadPriorFoundingOrder: true, processedRefs: new Set([a[0].ref!]) }), 5000)).toEqual([]);
  });
  it("a guarantee refund returns the seat unless Shopify already restocked it", () => {
    expect(seatActions({ topic: "refunds/create", orderId: "10", refundId: "r1", foundingQtyRefunded: 1, restockType: "no_restock" }, ctx({ refundedOrderWasFirstFounding: true }), 5000)).toHaveLength(1);
    expect(seatActions({ topic: "refunds/create", orderId: "10", refundId: "r1", foundingQtyRefunded: 1, restockType: "return" }, ctx({ refundedOrderWasFirstFounding: true }), 5000)).toEqual([]);
  });
  it("at zero seats, renewals are protected (inventoryPolicy CONTINUE)", () => {
    const a = seatActions({ topic: "orders/paid", orderId: "12", foundingQty: 1 }, ctx({ availableAfter: 0 }), 5000);
    expect(a.map((x) => x.op)).toEqual(["VariantInventoryPolicy"]);
  });
  it("public count line follows the FUNNEL.md rule", () => {
    const base = { cap: 5000, closeDateHuman: "January 9, 2027", nowHuman: "Oct 3, 9:00 AM", domain: "strongyears.com" };
    expect(countLine({ ...base, available: 4500 })).toMatch(/^Founding membership is open to the first 5,000 members/);
    expect(countLine({ ...base, available: 3766 })).toBe("1,234 of 5,000 founding seats taken as of Oct 3, 9:00 AM");
    expect(countLine({ ...base, available: 0 })).toMatch(/full/);
  });
});

describe("post-purchase server", () => {
  const env: OfferEnv = { apiKey: "key", apiSecret: "secret", foundingVariantId: 111, foundingSellingPlanId: 222, wallPlanVariantId: 333, foundingOpen: true, ebookProductIds: [9] };
  const token = signJwt({ iss: "shopify", sub: "ref-1", exp: Math.floor(Date.now() / 1000) + 600 }, "secret");
  const req = (url: string, body: unknown, t = token) => new Request(url, { method: "POST", headers: { Authorization: `Bearer ${t}`, "Content-Type": "application/json" }, body: JSON.stringify(body) });
  it("JWT round trip and rejection", () => {
    expect(verifyJwt(token, "secret")?.sub).toBe("ref-1");
    expect(verifyJwt(token, "wrong")).toBeNull();
    expect(verifyJwt(token.slice(0, -2) + "xx", "secret")).toBeNull();
  });
  it("digital-only ebook order (no shipping address): no subscription offer, Wall Plan instead", async () => {
    const r = await (await handleOffer(req("https://x/offer", { referenceId: "ref-1", hasShippingAddress: false, lineItems: [{ productId: "gid://shopify/Product/9", variantId: 5 }] }), env)).json();
    expect(r.kind).toBe("wallplan");
  });
  it("ebook + kit order (has a shipping address): founding offer with full terms", async () => {
    const r = await (await handleOffer(req("https://x/offer", { referenceId: "ref-1", hasShippingAddress: true, lineItems: [{ productId: 9, variantId: 5 }, { productId: 10, variantId: 6 }] }), env)).json();
    expect(r.kind).toBe("founding");
    expect(r.terms.join(" ")).toMatch(/until you cancel/);
    expect(r.termsSha256).toBe(FOUNDING_TERMS_SHA256);
  });
  it("order that already has a subscription: no founding offer", async () => {
    const r = await (await handleOffer(req("https://x/offer", { referenceId: "ref-1", hasShippingAddress: true, lineItems: [{ productId: 9, variantId: 5, sellingPlanId: 1 }, { productId: 1, variantId: 333 }] }), env)).json();
    expect(r).toEqual({});
  });
  it("signs an add_subscription changeset only for the exact terms shown", async () => {
    const bad = await handleSignChangeset(req("https://x/sign", { referenceId: "ref-1", offerKind: "founding", consentTextSha256: "nope" }), env);
    expect(bad.status).toBe(409);
    const ok = await (await handleSignChangeset(req("https://x/sign", { referenceId: "ref-1", offerKind: "founding", consentTextSha256: FOUNDING_TERMS_SHA256 }), env, 1_800_000_000)).json();
    const p = verifyJwt(ok.token, "secret", 1_800_000_000)!;
    expect(p).toMatchObject({ iss: "key", sub: "ref-1", iat: 1_800_000_000, changes: [{ type: "add_subscription", variantId: 111, quantity: 1, sellingPlanId: 222 }] });
  });
  it("rejects requests without Shopify's token", async () => {
    expect((await handleOffer(req("https://x/offer", {}, "bad.token.here"), env)).status).toBe(401);
  });
});

describe("founding seat ledger without a cap", () => {
  it("does nothing when FOUNDING_CAP is null (the Oct 2 2026 default)", () => {
    const ctx = { processedRefs: new Set<string>(), inventoryItemId: "i", locationId: "l", productId: "p", variantId: "v", customerHadPriorFoundingOrder: true, availableAfter: 0 } as any;
    expect(seatActions({ topic: "orders/paid", orderId: "1", foundingQty: 1 } as any, ctx)).toEqual([]);
  });
});
