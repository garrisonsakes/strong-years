import { NextResponse } from "next/server";
import { mockCheckoutAllowed, processorFor } from "@/lib/billing/processors";
import { getStore } from "@/lib/db";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { refuseIfPrelaunch } from "@/lib/launchGuard";

/**
 * Demo-only stand-in for Stripe Checkout (never available when STRIPE_SECRET_KEY is set).
 * Emits the same checkout.session.completed event Stripe would, through the real handler.
 */
export async function POST(req: Request) {
  const closed = await refuseIfPrelaunch(req, "json");
  if (closed) return closed;
  // H6: never in a production deployment, never next to a live processor.
  if (!mockCheckoutAllowed()) return NextResponse.json({ error: "Not available" }, { status: 404 });
  const form = await req.formData();
  const intentId = String(form.get("intent") ?? "");
  const outcome = String(form.get("outcome") ?? "success");
  const store = await getStore();
  const intent = await store.get("checkout_intents", intentId);
  if (!intent) return NextResponse.json({ error: "Unknown checkout" }, { status: 404 });
  if (processorFor(intent.processor).status() !== "mock") return NextResponse.json({ error: "Not available" }, { status: 404 });
  const base = new URL(req.url).origin;
  if (outcome !== "success") {
    return NextResponse.redirect(`${base}/checkout/mock/${intentId}?declined=1`, 303);
  }
  const short = intentId.slice(0, 8);
  await handleStripeEvent(store, {
    id: `evt_mock_${crypto.randomUUID()}`,
    type: "checkout.session.completed",
    livemode: false,
    data: {
      object: {
        id: `cs_mock_${short}`,
        metadata: { intent_id: intentId, payment_method: "pm_mock_visa" },
        payment_status: "paid",
        customer: `cus_mock_${short}`,
        subscription: intent.membership_price_cents !== null ? `sub_mock_${short}` : null,
        // Subscription-mode sessions carry an invoice, not a payment intent (as in real Stripe).
        payment_intent: intent.membership_price_cents !== null ? null : `pi_mock_${short}`,
        invoice: intent.membership_price_cents !== null ? `in_mock_${short}` : null,
      },
    },
  });
  return NextResponse.redirect(`${base}/api/checkout/complete?intent=${intentId}`, 303);
}
