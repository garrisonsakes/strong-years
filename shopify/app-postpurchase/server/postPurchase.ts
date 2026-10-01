/**
 * Post-purchase offer server: two endpoints the members app mounts (Web-standard Request/Response, so they drop
 * into Next.js route handlers unchanged):
 *   POST /api/shopify/post-purchase/offer           → decides the offer (or none) for this order
 *   POST /api/shopify/post-purchase/sign-changeset  → returns the changeset JWT Shopify requires
 * CORS: the extension runs on Shopify's checkout origin, so both endpoints answer OPTIONS and send
 * Access-Control-Allow-Origin: *. Authentication is the inputData.token JWT (HS256, signed by Shopify with the
 * app's client secret), not cookies.
 *
 * Env: SHOPIFY_API_KEY (client id), SHOPIFY_API_SECRET (client secret), SY_FOUNDING_VARIANT_ID (numeric),
 * SY_FOUNDING_SELLING_PLAN_ID (numeric, from `npm run verify`), SY_WALLPLAN_VARIANT_ID (numeric),
 * SY_FOUNDING_OPEN ("true" until close-founding), SY_EBOOK_PRODUCT_IDS (comma-separated numeric).
 */
import { createHmac, randomUUID, timingSafeEqual, createHash } from "node:crypto";

const b64url = (b: Buffer | string) => Buffer.from(b).toString("base64").replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
const fromB64url = (s: string) => Buffer.from(s.replace(/-/g, "+").replace(/_/g, "/"), "base64");

export function signJwt(payload: Record<string, unknown>, secret: string): string {
  const header = b64url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const body = b64url(JSON.stringify(payload));
  const sig = b64url(createHmac("sha256", secret).update(`${header}.${body}`).digest());
  return `${header}.${body}.${sig}`;
}

export function verifyJwt(token: string, secret: string, nowSec = Math.floor(Date.now() / 1000)): Record<string, any> | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  const expected = createHmac("sha256", secret).update(`${parts[0]}.${parts[1]}`).digest();
  const given = fromB64url(parts[2]);
  if (given.length !== expected.length || !timingSafeEqual(given, expected)) return null;
  try {
    const header = JSON.parse(fromB64url(parts[0]).toString());
    if (header.alg !== "HS256") return null;
    const payload = JSON.parse(fromB64url(parts[1]).toString());
    if (typeof payload.exp === "number" && payload.exp < nowSec - 5) return null;
    return payload;
  } catch { return null; }
}

export interface OfferEnv {
  apiKey: string; apiSecret: string;
  foundingVariantId: number; foundingSellingPlanId: number; wallPlanVariantId: number;
  foundingOpen: boolean; ebookProductIds: number[];
  /** members DB lookup: is this buyer already an active member? (by referenceId → order → customer email) */
  isExistingMember?: (referenceId: string) => Promise<boolean>;
}

export function envFromProcess(e: NodeJS.ProcessEnv = process.env): OfferEnv {
  return {
    apiKey: e.SHOPIFY_API_KEY || "", apiSecret: e.SHOPIFY_API_SECRET || "",
    foundingVariantId: Number(e.SY_FOUNDING_VARIANT_ID || 0), foundingSellingPlanId: Number(e.SY_FOUNDING_SELLING_PLAN_ID || 0),
    wallPlanVariantId: Number(e.SY_WALLPLAN_VARIANT_ID || 0), foundingOpen: e.SY_FOUNDING_OPEN !== "false",
    ebookProductIds: (e.SY_EBOOK_PRODUCT_IDS || "").split(",").map(Number).filter(Boolean),
  };
}

/** Exact terms shown above the button (FUNNEL.md §5.6 wording, email-only reminders until SMS is live). */
export const FOUNDING_TERMS = [
  "Today: $25 for your first month of Strong Years, charged to the card you just used.",
  "Then $25 every month on the same date, until you cancel. As a founding member, your price stays the same for as long as you stay subscribed.",
  "14-day money-back guarantee: ask for a refund within 14 days of today's charge. Once per person.",
  "Cancel anytime online in at most two screens in your account, or reply \"cancel\" to any email.",
  "We'll remind you by email before every renewal: 7 and 2 days before the first, 3 days before each one after that.",
];
export const FOUNDING_TERMS_SHA256 = createHash("sha256").update(FOUNDING_TERMS.join(" | ")).digest("hex");

const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "POST, OPTIONS" };
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", ...cors } });

function auth(req: Request, env: OfferEnv): Record<string, any> | null {
  const h = req.headers.get("authorization") || "";
  const token = h.startsWith("Bearer ") ? h.slice(7) : "";
  return token ? verifyJwt(token, env.apiSecret) : null;
}

const numId = (gidOrNum: string | number | null | undefined) => Number(String(gidOrNum ?? "").split("/").pop());

export async function handleOffer(req: Request, env: OfferEnv): Promise<Response> {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (!auth(req, env)) return json({ error: "unauthorized" }, 401);
  const body = (await req.json().catch(() => ({}))) as { referenceId?: string; hasShippingAddress?: boolean; lineItems?: Array<{ productId: string | number; variantId: string | number; sellingPlanId?: string | number | null }> };
  const items = body.lineItems || [];
  const hasSub = items.some((l) => l.sellingPlanId);
  const boughtEbook = items.some((l) => env.ebookProductIds.includes(numId(l.productId)));
  const hasWallPlan = items.some((l) => numId(l.variantId) === env.wallPlanVariantId);
  const member = body.referenceId && env.isExistingMember ? await env.isExistingMember(body.referenceId) : false;

  // A subscription can be added post-purchase only when the order has a shipping address and no subscription yet.
  if (env.foundingOpen && boughtEbook && !hasSub && body.hasShippingAddress && !member && env.foundingSellingPlanId) {
    return json({
      kind: "founding",
      heading: "Keep going as a founding member: $25 a month.",
      body: [
        "Your Daily Practice with Chang Yin, 8 to 12 minutes a day at your level, with a chair-based version of everything. Sun Yoon's recipes every Sunday. A Strength Age you retest every month.",
      ],
      terms: FOUNDING_TERMS,
      termsSha256: FOUNDING_TERMS_SHA256,
      acceptLabel: "Join for $25 today",
      declineLabel: "No thanks, just the books",
    });
  }
  if (boughtEbook && !hasWallPlan && env.wallPlanVariantId) {
    return json({
      kind: "wallplan",
      heading: "Add The Wall Plan for $9?",
      body: ["A printable 12-week calendar for your fridge plus 12 weekly grocery lists from Sun Yoon. Large print, one page a week. Yours to keep."],
      terms: ["One payment of $9, charged to the card you just used. Nothing renews.", "Refund on request within 14 days."],
      acceptLabel: "Yes, add The Wall Plan for $9",
      declineLabel: "No thanks",
    });
  }
  return json({});
}

export async function handleSignChangeset(req: Request, env: OfferEnv, nowSec = Math.floor(Date.now() / 1000)): Promise<Response> {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
  if (!auth(req, env)) return json({ error: "unauthorized" }, 401);
  const body = (await req.json().catch(() => ({}))) as { referenceId?: string; offerKind?: string; consentTextSha256?: string };
  if (!body.referenceId) return json({ error: "referenceId required" }, 400);
  let changes: unknown[];
  if (body.offerKind === "founding") {
    if (!env.foundingOpen) return json({ error: "founding closed" }, 409);
    if (body.consentTextSha256 !== FOUNDING_TERMS_SHA256) return json({ error: "terms mismatch" }, 409);
    changes = [{ type: "add_subscription", variantId: env.foundingVariantId, quantity: 1, sellingPlanId: env.foundingSellingPlanId, initialShippingPrice: 0, recurringShippingPrice: 0 }];
  } else if (body.offerKind === "wallplan") {
    changes = [{ type: "add_variant", variantId: env.wallPlanVariantId, quantity: 1 }];
  } else return json({ error: "unknown offer" }, 400);
  const token = signJwt({ iss: env.apiKey, jti: randomUUID(), iat: nowSec, sub: body.referenceId, changes }, env.apiSecret);
  return json({ token });
}
