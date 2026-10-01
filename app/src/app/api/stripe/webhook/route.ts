import { NextResponse } from "next/server";
import { env } from "@/lib/config";
import { getStore } from "@/lib/db";
import { RetryLater, handleStripeEvent, type StripeLikeEvent } from "@/lib/billing/webhook";
import { verifyStripeSignature } from "@/lib/billing/verify";

export const runtime = "nodejs";

/**
 * H5: fail closed. Without STRIPE_WEBHOOK_SECRET nothing is processed, in every
 * environment, unless DEV_ALLOW_UNSIGNED=true (local development only; refused
 * in production builds). L2: events whose livemode doesn't match the key are ignored.
 */
export async function POST(req: Request) {
  const payload = await req.text();
  let event: StripeLikeEvent;
  if (!env.stripeWebhookSecret) {
    if (!env.devAllowUnsigned) {
      console.error("STRIPE_WEBHOOK_SECRET is not set: refusing webhook");
      return NextResponse.json({ error: "Webhook secret not configured." }, { status: 500 });
    }
    try {
      event = JSON.parse(payload) as StripeLikeEvent;
    } catch {
      return NextResponse.json({ error: "Bad payload" }, { status: 400 });
    }
  } else {
    try {
      event = verifyStripeSignature(payload, req.headers.get("stripe-signature"), env.stripeWebhookSecret);
    } catch (err) {
      console.error("stripe signature verification failed", err);
      return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
    }
  }
  const expectLivemode = env.stripeSecretKey ? env.stripeSecretKey.startsWith("sk_live") || env.stripeSecretKey.startsWith("rk_live") : undefined;
  try {
    const result = await handleStripeEvent(await getStore(), event, { expectLivemode });
    return NextResponse.json({ received: true, ...result });
  } catch (err) {
    if (err instanceof RetryLater) {
      // Out-of-order or in-flight: Stripe retries with backoff.
      return NextResponse.json({ error: "retry later", reason: err.message }, { status: 409 });
    }
    console.error("stripe webhook handler failed", err);
    // 500 makes Stripe retry; the event row keeps the error for the admin view.
    return NextResponse.json({ error: "handler failed" }, { status: 500 });
  }
}
