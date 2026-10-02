/**
 * Shopify billing provider: config, the catalog → entitlement map, the /join and
 * /b redirects (to the store's PRODUCT PAGE, through the /discount/<code> share
 * link for cell B), the Admin API client (refund; contract cancel only when our
 * app owns the contract) and the self-serve 14-day refund.
 *
 * Shopify IDs live in the `shopify_products` table (data, not code). Prices in
 * that table mirror the store for display; Shopify charges what Shopify charges.
 * Attribution rides along as query parameters the theme turns into cart
 * attributes, is re-validated on the way back in (orders/paid) and is never used
 * to pick a product or a price: the row comes from the visitor's signed, sticky
 * cell only.
 *
 * INTEGRATION.md decisions (verified against shopify.dev, Oct 1 2026):
 *  - Cell B = the founding variant on the SAME monthly selling plan as founding_monthly
 *    plus the STARTER12 first-payment-only code (DiscountCodeBasicInput.recurringCycleLimit
 *    = 1, appliesOncePerCustomer). The free Shopify Subscriptions app bills only plans
 *    created in its own UI, and those plans offer all-cycle discounts only, so a
 *    fixed-first-cycle selling plan is not available on the launch path.
 *  - Selling plans don't work with cart permalinks ("Create cart permalinks" →
 *    Limitations), so every redirect lands on the product page; the theme's offer
 *    form adds the selling plan, records consent and goes to /checkout.
 *  - subscription_contracts/* and subscription_billing_attempts/* require
 *    read_own_subscription_contracts and fire only for contracts the subscribing app
 *    owns; the mutations are restricted the same way. Membership state therefore comes
 *    from orders/paid (initial + renewal orders), refunds/create and orders/cancelled;
 *    contract events are enrichment only.
 */
import { createHmac, timingSafeEqual } from "node:crypto";
import { fnv1a } from "../blitz";
import { env } from "../config";
import { isDeployed } from "../deployEnv";
import type { Store } from "../db/store";
import type { Attribution, Membership, ShopifyProductRow, TouchPoint } from "../db/types";
import { sanitizeAttribution, sanitizeTouch } from "../analytics/attribution";
import { alertOnCall, sendEmail } from "../notify";
import { formatDate, moneyExact } from "../pricing";
import { withinGuarantee } from "./cancel";
import { usedGuaranteeBefore, type RefundResult } from "./actions";
import type { BillingProvider } from "./provider";

type Env = Record<string, string | undefined>;

function str(e: Env, k: string, d = ""): string {
  const v = e[k];
  return v === undefined || v.trim() === "" ? d : v.trim();
}

export const shopifyConfig = {
  storeDomain(e: Env = process.env) {
    return str(e, "SHOPIFY_STORE_DOMAIN", "strongyears-demo.myshopify.com").replace(/^https?:\/\//, "").replace(/\/.*$/, "");
  },
  webhookSecret(e: Env = process.env) {
    return str(e, "SHOPIFY_WEBHOOK_SECRET");
  },
  adminToken(e: Env = process.env) {
    return str(e, "SHOPIFY_ADMIN_TOKEN");
  },
  apiVersion(e: Env = process.env) {
    return str(e, "SHOPIFY_API_VERSION", "2026-07");
  },
  /** The customer account page where Shopify Subscriptions lets members cancel, pause, change card, upgrade. */
  customerAccountUrl(e: Env = process.env) {
    const v = str(e, "SHOPIFY_CUSTOMER_ACCOUNT_URL");
    if (/^https:\/\/\S+$/.test(v)) return v;
    return `https://${shopifyConfig.storeDomain(e)}/account`;
  },
  /** The location whose inventory holds the founding seats (needed for the seat ledger until the first inventory_levels/update arrives). */
  locationId(e: Env = process.env) {
    const v = str(e, "SHOPIFY_LOCATION_ID");
    return /^\d{1,20}$/.test(v) ? v : "";
  },
  graceDays(e: Env = process.env) {
    const n = Number(str(e, "SHOPIFY_GRACE_DAYS", "7"));
    return Number.isFinite(n) && n >= 0 && n <= 30 ? n : 7;
  },
  /**
   * Live front-end cells (must exist in the catalog). CANON UPDATE 6: t12 ("$12 today = Starter Books + a 7-day trial
   * of the founding membership; first $25 on day 7, then monthly") is THE offer. m12 (cell B, "$12 = books + first
   * month" on the free Shopify Subscriptions app) is the fallback when the store has no trial-capable plan yet, e12
   * (books only) the old test cell. resolveFrontEnd keeps only cells whose rows exist, so a store whose catalog has no
   * t12 row serves m12 without any config change. The cell split test is OFF by default (one offer, canon 6).
   */
  cells(e: Env = process.env): string[] {
    const list = str(e, "FRONT_END_CELLS", "t12,m12,e12")
      .split(",")
      .map((x) => x.trim().toLowerCase())
      .filter((x) => /^[a-z0-9]{1,12}$/.test(x));
    return list.length ? [...new Set(list)] : ["t12"];
  },
  defaultCell(e: Env = process.env) {
    return str(e, "FRONT_END_DEFAULT_CELL", "t12").toLowerCase();
  },
  cellTestOn(e: Env = process.env) {
    const v = str(e, "FRONT_END_CELL_TEST", "false");
    return v === "true" || v === "1";
  },
  /** Canon 6 trial length; the catalog row's trial_days wins when set. */
  trialDays(e: Env = process.env) {
    const n = Number(str(e, "SHOPIFY_TRIAL_DAYS", "7"));
    return Number.isInteger(n) && n >= 1 && n <= 31 ? n : 7;
  },
  /**
   * Who owns the subscription contracts. "shopify_subscriptions" (launch default): the free app owns them, so our
   * Admin token can neither cancel nor edit a contract (write_own_subscription_contracts covers only our own) and
   * contract webhooks never reach us. "app": the Strong Years app created the selling plans and owns the contracts.
   */
  contractControl(e: Env = process.env): "shopify_subscriptions" | "app" {
    return str(e, "SUBSCRIPTION_ENGINE", "shopify_subscriptions") === "app" ? "app" : "shopify_subscriptions";
  },
  ownsContracts(e: Env = process.env) {
    return shopifyConfig.contractControl(e) === "app";
  },
};

/* ---------------- ids + HMAC ---------------- */

/** Shopify ids arrive as numbers, numeric strings or GIDs; we store the numeric part. */
export function shopifyId(raw: unknown): string | null {
  if (typeof raw === "number" && Number.isSafeInteger(raw) && raw > 0) return String(raw);
  if (typeof raw !== "string") return null;
  const m = raw.trim().match(/^(?:gid:\/\/shopify\/[A-Za-z]+\/)?(\d{1,20})$/);
  return m ? m[1]! : null;
}

/** Compares ids numerically (Shopify ids grow over time). */
export function idGreater(a: string, b: string | null | undefined): boolean {
  if (!b) return true;
  try {
    return BigInt(a) > BigInt(b);
  } catch {
    return false;
  }
}

/** X-Shopify-Hmac-Sha256: base64 HMAC-SHA256 of the raw body with the app's secret. */
export function verifyShopifyHmac(raw: Buffer | string, header: string | null | undefined, secret: string): boolean {
  if (!secret || !header || header.length > 100) return false;
  const expected = createHmac("sha256", secret).update(raw).digest();
  let got: Buffer;
  try {
    got = Buffer.from(header, "base64");
  } catch {
    return false;
  }
  return got.length === expected.length && timingSafeEqual(got, expected);
}

/* ---------------- catalog ---------------- */

export async function catalog(store: Store): Promise<ShopifyProductRow[]> {
  return store.find("shopify_products", { active: true }, { orderBy: "sku" });
}

/**
 * The row an order line maps to: exact (variant, selling plan); a one-time row only when the line has no plan.
 * Two rows may share (variant, plan) and differ by discount_code (cell B): the row whose code is on the order wins,
 * otherwise the row without a code. A code on the order never maps a line to a different variant or plan.
 */
export function matchLine(rows: ShopifyProductRow[], variantId: string | null, sellingPlanId: string | null, discountCodes: readonly string[] = []): ShopifyProductRow | null {
  if (!variantId) return null;
  const codes = new Set(discountCodes.map((c) => c.toUpperCase()));
  const cands = rows.filter((r) => r.shopify_variant_id === variantId && (r.selling_plan_id ?? null) === (sellingPlanId ?? null));
  return cands.find((r) => r.discount_code && codes.has(r.discount_code.toUpperCase())) ?? cands.find((r) => !r.discount_code) ?? null;
}

/** Discount codes on an order payload (untrusted; upper-cased, at most 10). */
export function orderDiscountCodes(payload: unknown): string[] {
  const p = payload && typeof payload === "object" ? (payload as Record<string, unknown>) : {};
  const list = Array.isArray(p.discount_codes) ? p.discount_codes.slice(0, 10) : [];
  const out: string[] = [];
  for (const d of list) {
    const code = d && typeof d === "object" ? (d as { code?: unknown }).code : null;
    if (typeof code === "string" && /^[A-Za-z0-9_-]{1,40}$/.test(code)) out.push(code.toUpperCase());
  }
  return out;
}

export function assignFrontEndCell(visitorId: string, cells: string[], salt = "shopify-cell-v1"): string {
  if (!cells.length) throw new Error("no cells");
  return cells[fnv1a(`${salt}:${visitorId}`) % cells.length]!;
}

export interface FrontEnd {
  cell: string;
  row: ShopifyProductRow;
}

function rowForCell(rows: ShopifyProductRow[], cell: string, cohortOpen: boolean): ShopifyProductRow | null {
  const want = cohortOpen ? "founding" : "standard";
  const cands = rows.filter((r) => r.cell === cell);
  return cands.find((r) => r.cohort === want) ?? cands.find((r) => r.cohort === null) ?? null;
}

/**
 * The visitor's front-end cell: a sticky hash of the SIGNED visitor id (never a
 * query parameter), restricted to cells that exist for the current cohort state.
 */
export function resolveFrontEnd(rows: ShopifyProductRow[], input: { visitorId: string | null; cohortOpen: boolean }, e: Env = process.env): FrontEnd | null {
  const live = shopifyConfig.cells(e).filter((c) => rowForCell(rows, c, input.cohortOpen));
  const fallback = shopifyConfig.defaultCell(e);
  let cell = live.includes(fallback) ? fallback : live[0];
  if (shopifyConfig.cellTestOn(e) && input.visitorId && live.length) cell = assignFrontEndCell(input.visitorId, live);
  if (!cell) return null;
  const row = rowForCell(rows, cell, input.cohortOpen);
  return row ? { cell, row } : null;
}

/** Fixed products bought by name (/join?offer=gift3). Allow-listed; anything else is ignored. */
export const NAMED_OFFERS = ["gift3", "gift12", "founding_monthly", "essentials_monthly"] as const;

/* ---------------- cart attributes (attribution) ---------------- */

const TOUCH_FIELDS = ["platform", "page", "post_id", "keyword", "character", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "mc_id"] as const;
export const MAX_ATTRIBUTE_VALUE = 100;

export function attributionToCartAttributes(a: Attribution | null): Record<string, string> {
  const out: Record<string, string> = {};
  const clean = sanitizeAttribution(a);
  if (!clean) return out;
  for (const f of TOUCH_FIELDS) {
    const v = (clean as Record<string, unknown>)[f];
    if (typeof v === "string") out[`sy_ft_${f}`] = v;
  }
  if (clean.first_seen_at) out.sy_ft_at = clean.first_seen_at;
  const lt = clean.last_touch;
  if (lt) {
    for (const f of TOUCH_FIELDS) {
      const v = (lt as Record<string, unknown>)[f];
      if (typeof v === "string") out[`sy_lt_${f}`] = v;
    }
    if (lt.at) out.sy_lt_at = lt.at;
  }
  if (clean.ad_opt_out) out.sy_opt_out = "1";
  return out;
}

export interface CartContext {
  attribution: Attribution | null;
  cell: string | null;
  visitorId: string | null;
  /** Prices (in cents) the consent box showed: one, or two for a starter page ("12.00|25.00": code price | plan price). */
  consentPricesCents?: number[];
}

/** "12.00|25.00" → [1200, 2500]; anything that isn't money is ignored. */
export function parseConsentPrices(v: string | undefined): number[] {
  if (!v) return [];
  return v.split("|").slice(0, 3).map((x) => x.trim()).filter((x) => /^\$?\d{1,5}(\.\d{1,2})?$/.test(x)).map((x) => Math.round(Number(x.replace("$", "")) * 100));
}

/**
 * R5-8: the money truth check. The page recorded what it showed; Shopify charged what it charged. A starter page shows
 * both prices (the code price and the plan price a returning customer pays), so either is a match. Anything else is
 * a mismatch that a person reviews. No record at all (no-JS path, older theme) is "unknown".
 */
export function consentMatchesCharge(ctx: Pick<CartContext, "consentPricesCents">, chargedCents: number): "match" | "mismatch" | "unknown" {
  const shown = ctx.consentPricesCents ?? [];
  if (!shown.length) return "unknown";
  return shown.includes(chargedCents) ? "match" : "mismatch";
}

/**
 * Reads our cart attributes back from an order (note_attributes). Untrusted:
 * every value is length-checked and re-validated; unknown keys are ignored; at
 * most 60 attributes are looked at.
 */
export function cartContextFromAttributes(list: unknown): CartContext {
  const raw: Record<string, string> = {};
  if (Array.isArray(list)) {
    for (const item of list.slice(0, 60)) {
      if (!item || typeof item !== "object") continue;
      const { name, value } = item as { name?: unknown; value?: unknown };
      if (typeof name !== "string" || typeof value !== "string" || !name.startsWith("sy_") || name.length > 40 || value.length > MAX_ATTRIBUTE_VALUE) continue;
      raw[name] = value;
    }
  }
  const ft: Record<string, unknown> = {};
  const lt: Record<string, unknown> = {};
  for (const f of TOUCH_FIELDS) {
    if (raw[`sy_ft_${f}`] !== undefined) ft[f] = raw[`sy_ft_${f}`];
    if (raw[`sy_lt_${f}`] !== undefined) lt[f] = raw[`sy_lt_${f}`];
  }
  if (raw.sy_lt_at) lt.at = raw.sy_lt_at;
  const lastTouch: TouchPoint | null = sanitizeTouch(lt);
  const attribution = sanitizeAttribution({ ...ft, first_seen_at: raw.sy_ft_at, ad_opt_out: raw.sy_opt_out === "1" ? true : undefined, last_touch: lastTouch ?? undefined });
  const cell = raw.sy_cell && /^[a-z0-9]{1,12}$/.test(raw.sy_cell) ? raw.sy_cell : null;
  const visitorId = raw.sy_vid && /^[0-9a-f-]{36}$/.test(raw.sy_vid) ? raw.sy_vid : null;
  return { attribution, cell, visitorId, consentPricesCents: parseConsentPrices(raw.sy_consent_price) };
}

/**
 * Where /join and /b send the visitor: the store's PRODUCT PAGE for the row (the
 * theme's offer form adds the selling plan, records the auto-renewal consent and
 * applies the cell-B code), reached through Shopify's /discount/<code> share link
 * when the row carries one, so the code is already on the checkout even if the
 * visitor never ticks a thing. Selling plans don't work with cart permalinks, so a
 * /cart/<variant>:1 link is never used for a membership. Attribution and the
 * signed visitor id ride as query parameters the theme stores and writes as cart
 * attributes (sy_ft_*, sy_lt_*, sy_vid, sy_cell). Arm/cell for the theme's own
 * sticky assignment are set from the row so the page shows exactly this offer.
 */
export function checkoutUrl(row: ShopifyProductRow, ctx: CartContext, e: Env = process.env): string {
  const q = new URLSearchParams();
  if (row.trial_days) q.set("view", "trial");
  else if (row.discount_code) q.set("view", "starter");
  const arm = row.trial_days ? "T" : row.cell === "m12" ? "B" : row.entitlement === "ebook" ? "A" : null;
  if (arm) q.set("arm", arm);
  if (row.cell && row.cell !== "m12" && row.cell !== "t12") q.set("cell", row.cell);
  if (ctx.visitorId && /^[0-9a-f-]{36}$/.test(ctx.visitorId)) q.set("vid", ctx.visitorId);
  const a = sanitizeAttribution(ctx.attribution);
  const touch = (a?.last_touch ?? a) as Record<string, unknown> | null;
  if (touch) {
    for (const f of TOUCH_FIELDS) {
      const v = touch[f];
      if (typeof v === "string" && v) q.set(f, v.slice(0, MAX_ATTRIBUTE_VALUE));
    }
  }
  q.set("sku", row.sku);
  const handle = row.product_handle && /^[a-z0-9-]{1,80}$/.test(row.product_handle) ? row.product_handle : null;
  const path = handle ? `/products/${handle}` : `/products/${row.shopify_product_id}`;
  const page = `${path}?${q.toString()}`;
  const store = `https://${shopifyConfig.storeDomain(e)}`;
  if (row.discount_code && /^[A-Z0-9]{2,32}$/.test(row.discount_code)) {
    return `${store}/discount/${row.discount_code}?redirect=${encodeURIComponent(page)}`;
  }
  return `${store}${page}`;
}

/** @deprecated name kept for older call sites; see checkoutUrl. */
export const cartUrl = checkoutUrl;

/* ---------------- Admin API (refund + contract cancel) ---------------- */

export interface AdminResult {
  ok: boolean;
  id?: string | null;
  error?: string;
}

export interface ShopifyAdmin {
  readonly mode: "live" | "mock" | "off";
  refundLine(i: { orderId: string; lineItemId: string | null; amountCents: number; note: string }): Promise<AdminResult>;
  cancelContract(contractId: string): Promise<AdminResult>;
  /**
   * Founding seat ledger (shopify/src/seatLedger.ts rules). Shopify Subscriptions renewal orders decrement the
   * founding variant's inventory like any order, so a renewal gives the seat back (+1) and a refund of the
   * seat-consuming first charge gives it back too. inventoryAdjustQuantities needs write_inventory.
   */
  adjustInventory?(i: { inventoryItemId: string; locationId: string; delta: number; ref: string }): Promise<AdminResult & { available?: number }>;
  /** When the founding stock hits 0: inventoryPolicy CONTINUE so existing members' renewals never fail (write_products). */
  allowOverselling?(i: { productId: string; variantId: string }): Promise<AdminResult>;
}

type FetchLike = (url: string, init: RequestInit) => Promise<Response>;

/**
 * GraphQL Admin API. With no SHOPIFY_ADMIN_TOKEN: a local mock (dev, tests, demo) that
 * "succeeds", or, on a real deploy, "off" (every refund goes to a person).
 */
export function shopifyAdmin(e: Env = process.env, fetchImpl: FetchLike = (u, i) => fetch(u, i)): ShopifyAdmin {
  const token = shopifyConfig.adminToken(e);
  if (!token) {
    const mock = !isDeployed(e);
    const owns = shopifyConfig.ownsContracts(e);
    return {
      mode: mock ? "mock" : "off",
      async refundLine() {
        return mock ? { ok: true, id: `mock_refund_${crypto.randomUUID().slice(0, 8)}` } : { ok: false, error: "SHOPIFY_ADMIN_TOKEN not set" };
      },
      async cancelContract() {
        if (!owns) return { ok: false, error: "contract is owned by the Shopify Subscriptions app; cancel it in Apps → Subscriptions" };
        return mock ? { ok: true, id: null } : { ok: false, error: "SHOPIFY_ADMIN_TOKEN not set" };
      },
      async adjustInventory() {
        return mock ? { ok: true } : { ok: false, error: "SHOPIFY_ADMIN_TOKEN not set" };
      },
      async allowOverselling() {
        return mock ? { ok: true } : { ok: false, error: "SHOPIFY_ADMIN_TOKEN not set" };
      },
    };
  }
  const owns = shopifyConfig.ownsContracts(e);
  const endpoint = `https://${shopifyConfig.storeDomain(e)}/admin/api/${shopifyConfig.apiVersion(e)}/graphql.json`;
  async function gql<T>(query: string, variables: Record<string, unknown>): Promise<T> {
    const res = await fetchImpl(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Shopify-Access-Token": token },
      body: JSON.stringify({ query, variables }),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) throw new Error(`shopify admin ${res.status}`);
    const body = (await res.json()) as { data?: T; errors?: unknown };
    if (body.errors || !body.data) throw new Error("shopify admin graphql error");
    return body.data;
  }
  return {
    mode: "live",
    async refundLine({ orderId, lineItemId, amountCents, note }) {
      try {
        // The refund needs the parent sale transaction and its gateway.
        const o = await gql<{ order: { transactions: { id: string; kind: string; status: string; gateway: string }[] } | null }>(
          "query($id: ID!) { order(id: $id) { transactions(first: 10) { id kind status gateway } } }",
          { id: `gid://shopify/Order/${orderId}` },
        );
        const parent = o.order?.transactions.find((t) => (t.kind === "SALE" || t.kind === "CAPTURE") && t.status === "SUCCESS");
        if (!parent) return { ok: false, error: "no captured transaction" };
        const r = await gql<{ refundCreate: { refund: { id: string } | null; userErrors: { message: string }[] } }>(
          "mutation($input: RefundInput!) { refundCreate(input: $input) { refund { id } userErrors { message } } }",
          {
            input: {
              orderId: `gid://shopify/Order/${orderId}`,
              note: note.slice(0, 200),
              notify: true,
              refundLineItems: lineItemId ? [{ lineItemId: `gid://shopify/LineItem/${lineItemId}`, quantity: 1, restockType: "NO_RESTOCK" }] : [],
              transactions: [{ orderId: `gid://shopify/Order/${orderId}`, parentId: parent.id, gateway: parent.gateway, kind: "REFUND", amount: (amountCents / 100).toFixed(2) }],
            },
          },
        );
        if (r.refundCreate.userErrors.length || !r.refundCreate.refund) return { ok: false, error: r.refundCreate.userErrors[0]?.message ?? "refund failed" };
        return { ok: true, id: shopifyId(r.refundCreate.refund.id) };
      } catch (err) {
        return { ok: false, error: (err as Error).message };
      }
    },
    async adjustInventory({ inventoryItemId, locationId, delta, ref }) {
      try {
        const r = await gql<{ inventoryAdjustQuantities: { inventoryAdjustmentGroup: { changes: { delta: number; quantityAfterChange: number | null }[] } | null; userErrors: { message: string }[] } }>(
          "mutation($input: InventoryAdjustQuantitiesInput!) { inventoryAdjustQuantities(input: $input) { inventoryAdjustmentGroup { changes { delta quantityAfterChange } } userErrors { message } } }",
          { input: { name: "available", reason: "correction", referenceDocumentUri: ref, changes: [{ inventoryItemId: `gid://shopify/InventoryItem/${inventoryItemId}`, locationId: `gid://shopify/Location/${locationId}`, delta }] } },
        );
        if (r.inventoryAdjustQuantities.userErrors.length) return { ok: false, error: r.inventoryAdjustQuantities.userErrors[0]!.message };
        const after = r.inventoryAdjustQuantities.inventoryAdjustmentGroup?.changes?.[0]?.quantityAfterChange;
        return { ok: true, ...(typeof after === "number" ? { available: after } : {}) };
      } catch (err) {
        return { ok: false, error: (err as Error).message };
      }
    },
    async allowOverselling({ productId, variantId }) {
      try {
        const r = await gql<{ productVariantsBulkUpdate: { userErrors: { message: string }[] } }>(
          "mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) { productVariantsBulkUpdate(productId: $productId, variants: $variants) { userErrors { message } } }",
          { productId: `gid://shopify/Product/${productId}`, variants: [{ id: `gid://shopify/ProductVariant/${variantId}`, inventoryPolicy: "CONTINUE" }] },
        );
        return r.productVariantsBulkUpdate.userErrors.length ? { ok: false, error: r.productVariantsBulkUpdate.userErrors[0]!.message } : { ok: true };
      } catch (err) {
        return { ok: false, error: (err as Error).message };
      }
    },
    async cancelContract(contractId) {
      // subscriptionContractCancel needs write_own_subscription_contracts: it works only on contracts our app
      // created. Shopify Subscriptions owns the launch-path contracts, so this goes to a person instead.
      if (!owns) return { ok: false, error: "contract is owned by the Shopify Subscriptions app (SUBSCRIPTION_ENGINE=shopify_subscriptions); cancel it in Apps → Subscriptions" };
      try {
        const r = await gql<{ subscriptionContractCancel: { contract: { id: string } | null; userErrors: { message: string }[] } }>(
          "mutation($id: ID!) { subscriptionContractCancel(subscriptionContractId: $id) { contract { id } userErrors { message } } }",
          { id: `gid://shopify/SubscriptionContract/${contractId}` },
        );
        return r.subscriptionContractCancel.userErrors.length ? { ok: false, error: r.subscriptionContractCancel.userErrors[0]!.message } : { ok: true };
      } catch (err) {
        return { ok: false, error: (err as Error).message };
      }
    },
  };
}

/* ---------------- self-serve 14-day refund ---------------- */

async function reviewTicket(store: Store, m: Membership, why: string) {
  const member = await store.get("members", m.member_id);
  const t = await store.insert("support_tickets", { member_id: m.member_id, email: member?.email ?? null, reason: "refund_review", message: `Refund request for membership ${m.id}: ${why}`, status: "open" });
  await alertOnCall("Refund needs a person", `ticket-${t.id}`);
}

/**
 * The money-back guarantee on a Shopify membership: the first membership charge,
 * inside 14 days, once per person. The refund is made through the Admin API and only
 * reported as done when Shopify accepts it; the contract is cancelled so nothing
 * renews. The refunds/create webhook that follows finds the order already refunded.
 */
export async function refundShopifyMembership(store: Store, m: Membership, now = new Date(), admin: ShopifyAdmin = shopifyAdmin()): Promise<RefundResult> {
  if (!withinGuarantee(m, now.getTime())) return { ok: false, state: "ineligible", refundedCents: 0, message: "This membership is outside the money-back window. Reply to any email and a person will help." };
  const member = await store.get("members", m.member_id);
  if (!member) return { ok: false, state: "ineligible", refundedCents: 0, message: "Account not found." };
  if (await usedGuaranteeBefore(store, member)) {
    await reviewTicket(store, m, "repeat money-back request (email used before)");
    return { ok: false, state: "review", refundedCents: 0, message: "You've used the money-back guarantee before, so a person on our team will review this by email within one business day. Nothing has changed yet." };
  }
  const charge = (await store.find("sy_orders", { membership_id: m.id, kind: "membership_charge", status: "paid" }, { orderBy: "created_at" }))[0];
  if (!charge || !charge.shopify_order_id) {
    await reviewTicket(store, m, "no Shopify membership charge found");
    return { ok: false, state: "review", refundedCents: 0, message: "We couldn't find the charge to refund automatically, so a person on our team will sort it out by email within one business day. Nothing has changed yet." };
  }
  // Claim the order first so a double tap can't refund twice.
  const [claimed] = await store.updateWhere("sy_orders", { id: charge.id, status: "paid" }, { status: "refund_pending" });
  if (!claimed) return { ok: false, state: "review", refundedCents: 0, message: "A refund for this charge is already in progress." };
  const amount = charge.amount_cents - (charge.amount_refunded_cents ?? 0);
  const r = await admin.refundLine({ orderId: charge.shopify_order_id, lineItemId: charge.shopify_line_id ?? null, amountCents: amount, note: "14-day money-back guarantee (self-serve)" });
  if (!r.ok) {
    await store.update("sy_orders", charge.id, { status: "paid" });
    await reviewTicket(store, m, `Shopify refused the refund: ${r.error ?? "unknown"}`);
    return { ok: false, state: "review", refundedCents: 0, message: "The refund didn't go through automatically. A person on our team will finish it by email within one business day. Nothing has changed yet." };
  }
  await store.update("sy_orders", charge.id, { status: "refunded", amount_refunded_cents: charge.amount_cents });
  await store.insert("refund_ledger", { email: member.email.toLowerCase(), card_fingerprint: null, member_id: member.id, membership_id: m.id, amount_cents: amount, processor_refund_id: r.id ?? null });
  // Stop the renewal. Only a contract our app owns can be cancelled through the API; on the launch path
  // (Shopify Subscriptions owns it) a person cancels it in Apps → Subscriptions within 1 business day, which
  // is weeks before the next renewal date. Either way the member's access has already ended here.
  const c = m.shopify_contract_id ? await admin.cancelContract(m.shopify_contract_id) : { ok: false, error: "no contract id on file (contract webhooks are enrichment only)" };
  if (!c.ok) await reviewTicket(store, m, `refunded; now cancel the member's subscription contract in Shopify (Apps → Subscriptions → ${member.email}) so it doesn't renew: ${c.error ?? "unknown"}.`);
  await store.update("memberships", m.id, { status: "refunded", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString(), grace_until: null });
  await sendEmail({
    to: member.email,
    template: "refund_confirmation",
    subject: "Your refund is on its way",
    text: `We've refunded ${moneyExact(amount)} for your Strong Years membership (${formatDate(now, env.displayTimeZone)}). It usually shows in 5–10 days. Your membership has ended and we are closing the subscription on our side so nothing renews; if you see it still listed on your Shopify account page over the next business day, that is us finishing the paperwork, not a charge. Books and add-ons you bought separately are one-time purchases with their own terms; reply to this email if something about them wasn't right.`,
  });
  return { ok: true, state: "done", refundedCents: amount, message: `Refunded ${moneyExact(amount)}.` };
}

/* ---------------- demo catalog ---------------- */

/** Demo/test catalog with obviously fake ids. A real store's rows go in via SQL (README "Shopify setup"). */
export const DEMO_CATALOG: Omit<ShopifyProductRow, "id" | "created_at">[] = [
  { sku: "ebook_e7", entitlement: "ebook", title: "Strong Years starter books", shopify_product_id: "9100000001", shopify_variant_id: "9000000007", selling_plan_id: null, inventory_item_id: null, price_cents: 700, recurring_cents: null, interval: null, includes_ebook: true, gift_months: null, cell: "e7", cohort: null, active: true, product_handle: "strong-years-starter-books-c7", discount_code: null },
  { sku: "ebook_e12", entitlement: "ebook", title: "Strong Years starter books", shopify_product_id: "9100000001", shopify_variant_id: "9000000012", selling_plan_id: null, inventory_item_id: null, price_cents: 1200, recurring_cents: null, interval: null, includes_ebook: true, gift_months: null, cell: "e12", cohort: null, active: true, product_handle: "strong-years-starter-books", discount_code: null },
  { sku: "ebook_e15", entitlement: "ebook", title: "Strong Years starter books", shopify_product_id: "9100000001", shopify_variant_id: "9000000015", selling_plan_id: null, inventory_item_id: null, price_cents: 1500, recurring_cents: null, interval: null, includes_ebook: true, gift_months: null, cell: "e15", cohort: null, active: true, product_handle: "strong-years-starter-books-c15", discount_code: null },
  { sku: "founding_monthly", entitlement: "founding", title: "Founding membership", shopify_product_id: "9100000002", shopify_variant_id: "9000000025", selling_plan_id: "7000000025", inventory_item_id: "8000000025", price_cents: 2500, recurring_cents: 2500, interval: "month", includes_ebook: false, gift_months: null, cell: null, cohort: "founding", active: true, product_handle: "founding-membership", discount_code: null },
  // Cell B (launch default): same variant + plan as founding_monthly, $13 off the first payment with STARTER12.
  { sku: "bundle_m12", entitlement: "founding", title: "Starter books + first month of founding membership", shopify_product_id: "9100000002", shopify_variant_id: "9000000025", selling_plan_id: "7000000025", inventory_item_id: "8000000025", price_cents: 1200, recurring_cents: 2500, interval: "month", includes_ebook: true, gift_months: null, cell: "m12", cohort: "founding", active: true, product_handle: "founding-membership", discount_code: "STARTER12" },
  // CANON UPDATE 6 (the launch offer): founding variant on the subscription app's 7-day-trial plan; $0 membership line at
  // checkout, the Starter Books ride as a separate $12 one-time line (ebook_e12) on the same order; first $25 on day 7.
  { sku: "bundle_t12", entitlement: "founding", title: "7-day trial of founding membership (with the Starter Books)", shopify_product_id: "9100000002", shopify_variant_id: "9000000025", selling_plan_id: "7000000070", inventory_item_id: "8000000025", price_cents: 0, recurring_cents: 2500, interval: "month", includes_ebook: false, gift_months: null, cell: "t12", cohort: "founding", active: true, product_handle: "founding-membership", discount_code: null, trial_days: 7 },
  { sku: "bundle_t12_standard", entitlement: "standard", title: "7-day trial of membership (with the Starter Books)", shopify_product_id: "9100000003", shopify_variant_id: "9000000035", selling_plan_id: "7000000071", inventory_item_id: null, price_cents: 0, recurring_cents: 3500, interval: "month", includes_ebook: false, gift_months: null, cell: "t12", cohort: "standard", active: true, product_handle: "strong-years-membership", discount_code: null, trial_days: 7 },
  { sku: "standard_monthly", entitlement: "standard", title: "Membership", shopify_product_id: "9100000003", shopify_variant_id: "9000000035", selling_plan_id: "7000000035", inventory_item_id: null, price_cents: 3500, recurring_cents: 3500, interval: "month", includes_ebook: false, gift_months: null, cell: null, cohort: "standard", active: true, product_handle: "strong-years-membership", discount_code: null },
  { sku: "bundle_m12_standard", entitlement: "standard", title: "Starter books + first month of membership", shopify_product_id: "9100000003", shopify_variant_id: "9000000035", selling_plan_id: "7000000035", inventory_item_id: null, price_cents: 1200, recurring_cents: 3500, interval: "month", includes_ebook: true, gift_months: null, cell: "m12", cohort: "standard", active: true, product_handle: "strong-years-membership", discount_code: "STARTER12S" },
  { sku: "essentials_monthly", entitlement: "essentials", title: "Essentials", shopify_product_id: "9100000004", shopify_variant_id: "9000000120", selling_plan_id: "7000000120", inventory_item_id: null, price_cents: 1200, recurring_cents: 1200, interval: "month", includes_ebook: false, gift_months: null, cell: null, cohort: null, active: true, product_handle: "essentials-membership", discount_code: null },
  { sku: "annual_founding", entitlement: "annual", title: "Founding membership, yearly", shopify_product_id: "9100000005", shopify_variant_id: "9000000249", selling_plan_id: "7000000249", inventory_item_id: null, price_cents: 24900, recurring_cents: 24900, interval: "year", includes_ebook: false, gift_months: null, cell: null, cohort: null, active: true, product_handle: "founding-annual", discount_code: null },
  { sku: "gift3", entitlement: "gift", title: "Gift: 3 months", shopify_product_id: "9100000006", shopify_variant_id: "9000000049", selling_plan_id: null, inventory_item_id: null, price_cents: 4900, recurring_cents: null, interval: null, includes_ebook: false, gift_months: 3, cell: null, cohort: null, active: true, product_handle: "gift-strong-years", discount_code: null },
  { sku: "gift12", entitlement: "gift", title: "Gift: 12 months", shopify_product_id: "9100000006", shopify_variant_id: "9000000119", selling_plan_id: null, inventory_item_id: null, price_cents: 11900, recurring_cents: null, interval: null, includes_ebook: false, gift_months: 12, cell: null, cohort: null, active: true, product_handle: "gift-strong-years", discount_code: null },
  { sku: "wallplan", entitlement: "bump", title: "The Wall Plan + grocery lists", shopify_product_id: "9100000007", shopify_variant_id: "9000000009", selling_plan_id: null, inventory_item_id: null, price_cents: 900, recurring_cents: null, interval: null, includes_ebook: false, gift_months: null, cell: null, cohort: null, active: true, product_handle: "the-wall-plan", discount_code: null },
];

export async function seedShopifyCatalog(store: Store): Promise<void> {
  for (const row of DEMO_CATALOG) {
    if (!(await store.findOne("shopify_products", { sku: row.sku }))) await store.insert("shopify_products", row);
  }
}

export const shopifyProvider: BillingProvider = {
  id: "shopify",
  refundMembership: (store, m, now) => refundShopifyMembership(store, m, now),
  manageUrl: () => shopifyConfig.customerAccountUrl(),
};
