import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { shopifyConfig, verifyShopifyHmac } from "@/lib/billing/shopify";
import { handleShopifyWebhook } from "@/lib/billing/shopifyWebhook";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Shopify sends at most a few KB; anything near this is not a real webhook. */
const MAX_BODY = 1024 * 1024;

/**
 * Shopify webhooks (orders, refunds, subscription contracts, billing attempts,
 * customers, app/uninstalled, inventory). Fails closed:
 *  - no SHOPIFY_WEBHOOK_SECRET configured → 503 (nothing processed, Shopify retries);
 *  - HMAC of the exact raw body must match X-Shopify-Hmac-Sha256 → else 401;
 *  - the shop domain header must be our store → else 401.
 * Then idempotent by X-Shopify-Webhook-Id plus business keys (lib/billing/shopifyWebhook.ts).
 * "deferred" (event before the order it belongs to) answers 503 so Shopify retries later.
 */
export async function POST(req: Request) {
  const secret = shopifyConfig.webhookSecret();
  if (!secret) return NextResponse.json({ error: "webhooks not configured" }, { status: 503 });
  const len = Number(req.headers.get("content-length") ?? "0");
  if (len > MAX_BODY) return NextResponse.json({ error: "too large" }, { status: 413 });
  const raw = Buffer.from(await req.arrayBuffer());
  if (raw.length > MAX_BODY) return NextResponse.json({ error: "too large" }, { status: 413 });
  if (!verifyShopifyHmac(raw, req.headers.get("x-shopify-hmac-sha256"), secret)) return NextResponse.json({ error: "invalid signature" }, { status: 401 });
  const shop = (req.headers.get("x-shopify-shop-domain") ?? "").toLowerCase();
  if (process.env.SHOPIFY_STORE_DOMAIN && shop !== shopifyConfig.storeDomain().toLowerCase()) return NextResponse.json({ error: "wrong shop" }, { status: 401 });
  let payload: unknown;
  try {
    payload = JSON.parse(raw.toString("utf8"));
  } catch {
    return NextResponse.json({ error: "bad json" }, { status: 400 });
  }
  const webhookId = (req.headers.get("x-shopify-webhook-id") ?? req.headers.get("x-shopify-event-id") ?? "").slice(0, 100);
  const topic = (req.headers.get("x-shopify-topic") ?? "").slice(0, 80);
  try {
    const r = await handleShopifyWebhook(await getStore(), { webhookId, topic, payload });
    if (r.status === "deferred") return NextResponse.json(r, { status: 503 });
    return NextResponse.json(r);
  } catch (err) {
    console.error("shopify webhook failed", topic, (err as Error).message);
    return NextResponse.json({ error: "processing failed" }, { status: 500 });
  }
}
