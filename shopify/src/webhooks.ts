/**
 * Contract between Shopify and the members app (Next.js, members.<domain>), plus the helpers it imports.
 * Endpoint: POST {MEMBERS_APP_URL}/api/webhooks/shopify  (topic in X-Shopify-Topic; route already in the members app).
 *
 * HMAC: Shopify signs every webhook with the APP's client secret (Dev Dashboard → app → Settings →
 * Client secret). It is not configurable per subscription. The members app stores it as
 * SHOPIFY_WEBHOOK_SECRET and verifies X-Shopify-Hmac-Sha256 over the RAW body before parsing.
 *
 * What the members app reads (all present in the standard order payload):
 *  - order.note_attributes[]  ← cart attributes the theme writes (attribution, cell, arm, consent)
 *  - order.line_items[].sku / product_id / variant_id / properties (gift recipient)
 *  - order.discount_codes[].code (affiliate / page codes, STARTER12)
 *  - order.customer.email (members sign in with an email code matched to this)
 *  - order.source_name, order.created_at, order.total_price, order.financial_status
 *  - order.metafields (strong_years namespace, included via metafieldNamespaces on the subscription)
 */
import { createHmac, timingSafeEqual } from "node:crypto";

export const ATTRIBUTION_KEYS = ["platform", "page", "post_id", "keyword", "character", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "mc_id"] as const;
export type AttributionKey = (typeof ATTRIBUTION_KEYS)[number];

/**
 * Cart attribute names the theme writes (theme/assets/strong-years.js). Identical to what the members app reads
 * (app/src/lib/billing/shopify.ts cartContextFromAttributes): flat "sy_" keys, every value <= 100 characters.
 *   sy_ft_<field>, sy_ft_at   first touch      sy_lt_<field>, sy_lt_at   last touch
 *   sy_cell  e7 | e12 | e15 | m12 (cell B)     sy_arm  A | B              sy_vid  visitor uuid
 *   sy_sku   members-app catalog sku of the offer form (ebook_e12, founding_monthly, bundle_m12, ...)
 *   sy_entry ebook | join | starter | gift | addon | cart
 *   sy_consent_sha / sy_consent_at / sy_consent_price / sy_consent_v   auto-renewal consent record
 */
export const MAX_ATTRIBUTE_VALUE = 100;

export function verifyShopifyHmac(rawBody: string | Buffer, hmacHeader: string | null | undefined, secret: string): boolean {
  if (!hmacHeader || !secret || hmacHeader.length > 100) return false;
  const digest = createHmac("sha256", secret).update(rawBody).digest();
  let given: Buffer;
  try { given = Buffer.from(hmacHeader, "base64"); } catch { return false; }
  return given.length === digest.length && timingSafeEqual(given, digest);
}

export interface NoteAttribute { name: string; value: string }
type Touch = Partial<Record<AttributionKey, string>> & { at?: string };

export interface Attribution {
  firstTouch: Touch;
  lastTouch: Touch;
  cell: string | null;
  arm: string | null;
  visitorId: string | null;
  sku: string | null;
  entry: string | null;
  consent: { sha256: string; at: string; price: string; v: string } | null;
}

/** Untrusted input: only sy_ keys, only <= 100 chars, at most 60 attributes. */
export function parseAttribution(noteAttributes: NoteAttribute[] | undefined): Attribution {
  const raw: Record<string, string> = {};
  for (const a of (noteAttributes || []).slice(0, 60)) {
    if (a && typeof a.name === "string" && typeof a.value === "string" && a.name.startsWith("sy_") && a.name.length <= 40 && a.value.length <= MAX_ATTRIBUTE_VALUE) raw[a.name] = a.value;
  }
  const ft: Touch = {}, lt: Touch = {};
  for (const f of ATTRIBUTION_KEYS) {
    if (raw[`sy_ft_${f}`]) ft[f] = raw[`sy_ft_${f}`];
    if (raw[`sy_lt_${f}`]) lt[f] = raw[`sy_lt_${f}`];
  }
  if (raw.sy_ft_at) ft.at = raw.sy_ft_at;
  if (raw.sy_lt_at) lt.at = raw.sy_lt_at;
  const okId = (v: string | undefined, re: RegExp) => (v && re.test(v) ? v : null);
  return {
    firstTouch: ft,
    lastTouch: lt,
    cell: okId(raw.sy_cell, /^[a-z0-9]{1,12}$/),
    arm: okId(raw.sy_arm, /^[A-Z]$/),
    visitorId: okId(raw.sy_vid, /^[0-9a-f-]{36}$/),
    sku: okId(raw.sy_sku, /^[a-z0-9_]{1,40}$/),
    entry: okId(raw.sy_entry, /^[a-z]{1,12}$/),
    consent: raw.sy_consent_sha && /^[0-9a-f]{64}$/.test(raw.sy_consent_sha)
      ? { sha256: raw.sy_consent_sha, at: raw.sy_consent_at || "", price: raw.sy_consent_price || "", v: raw.sy_consent_v || "1" }
      : null,
  };
}

/** SKU → role, so the members app never has to look up products to classify a line. */
export const SKU_ROLE: Record<string, string> = {
  "SY-BOOKS-E7": "ebook", "SY-BOOKS-E12": "ebook", "SY-BOOKS-E15": "ebook",
  "SY-FOUNDING-25": "founding",
  "SY-STANDARD-35": "standard",
  "SY-ANNUAL-249": "annual",
  "SY-ESSENTIALS-12": "essentials",
  "SY-GIFT-3M": "gift_3m", "SY-GIFT-12M": "gift_12m",
  "SY-WALLPLAN-9": "bump_wallplan",
  "SY-KIT-29": "bump_kit",
};

export interface OrderLike {
  id: number | string;
  admin_graphql_api_id?: string;
  email?: string;
  source_name?: string;
  created_at?: string;
  financial_status?: string;
  note_attributes?: NoteAttribute[];
  discount_codes?: Array<{ code: string }>;
  customer?: { id: number | string; email?: string } | null;
  line_items: Array<{ id: number | string; sku?: string | null; product_id?: number | null; variant_id?: number | null; price: string; quantity: number; properties?: NoteAttribute[] }>;
}

export interface MembershipGrant {
  kind: "ebook" | "membership" | "gift" | "addon";
  role: string;
  /** Access length implied by this paid order (membership: one billing period; gift: prepaid length). */
  months?: number;
  recipientEmail?: string;
  giftStart?: string;
}

/**
 * Classify an orders/paid payload into what the members app must grant. Works for initial orders AND for
 * Shopify Subscriptions renewal orders (renewals arrive as ordinary orders/paid events), so membership access
 * = "paid through" date extended by one period per paid membership order (+ a grace window for retries).
 */
export function classifyOrder(order: OrderLike): MembershipGrant[] {
  const grants: MembershipGrant[] = [];
  for (const li of order.line_items || []) {
    const role = SKU_ROLE[li.sku || ""];
    if (!role) continue;
    const props = new Map((li.properties || []).map((p) => [p.name, p.value]));
    if (role === "ebook") grants.push({ kind: "ebook", role });
    else if (role === "founding" || role === "standard" || role === "essentials") grants.push({ kind: "membership", role, months: 1 });
    else if (role === "annual") grants.push({ kind: "membership", role, months: 12 });
    else if (role === "gift_3m" || role === "gift_12m") grants.push({ kind: "gift", role, months: role === "gift_3m" ? 3 : 12, recipientEmail: props.get("Recipient email") || undefined, giftStart: props.get("Start date") || undefined });
    else grants.push({ kind: "addon", role });
  }
  return grants;
}

/** The cell-B first-payment codes (config/catalog.ts DISCOUNTS, kind starter_first_payment). */
export const STARTER_CODES = ["STARTER12", "STARTER12S"] as const;

/**
 * Cell B (launch default; shopify_subscriptions engine) = a membership line + STARTER12 (founding) or STARTER12S
 * (standard, after the founding close). The members app also delivers the Starter Books for these orders.
 */
export function isStarterCellB(order: OrderLike): boolean {
  const codes = (order.discount_codes || []).map((d) => d.code.toUpperCase());
  const skus = (order.line_items || []).map((l) => l.sku);
  return (codes.includes("STARTER12") && skus.includes("SY-FOUNDING-25")) || (codes.includes("STARTER12S") && skus.includes("SY-STANDARD-35"));
}

/** Page/affiliate codes → commission owner (30% recurring for 12 months is computed by the members app). */
export function affiliateCode(order: OrderLike): string | null {
  const c = (order.discount_codes || []).map((d) => d.code.toUpperCase()).find((x) => !(STARTER_CODES as readonly string[]).includes(x));
  return c || null;
}

/** Shopify Subscriptions renewal orders arrive as ordinary orders/paid events with this source_name. */
export function isRenewalOrder(order: Pick<OrderLike, "source_name">): boolean {
  return /subscription/i.test(order.source_name || "");
}
