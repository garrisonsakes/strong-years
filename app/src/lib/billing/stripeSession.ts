import { CHECKOUT_SESSION_MINUTES, holdsFoundingSpot } from "../founding";
import type Stripe from "stripe";
import { env, prices } from "../config";
import type { CheckoutIntent } from "../db/types";
import { offerDef, type CheckoutQuote, type OfferCode, type Sku } from "../pricing";
import type { PRICE_ENV } from "./stripeClient";

const SKU_PRICE: Partial<Record<Sku, keyof typeof PRICE_ENV>> = {
  trial_fee: "trial_fee",
  reset: "reset",
  kitchen: "kitchen",
  wallplan: "bump",
  gift3: "gift3",
  gift12: "gift12",
};

/**
 * L3: checkout never trusts a configured price ID for the amount. Every line is
 * built from the server quote with price_data, so the charge always equals the
 * terms shown. (Price IDs from env are only used for dashboard reporting via
 * product metadata.)
 */
function oneTime(sku: Sku, name: string, cents: number): Stripe.Checkout.SessionCreateParams.LineItem {
  return { quantity: 1, price_data: { currency: "usd", unit_amount: cents, product_data: { name, metadata: { sku, price_env: SKU_PRICE[sku] ?? "" } } } };
}

function recurring(cents: number, founding: boolean): Stripe.Checkout.SessionCreateParams.LineItem {
  const name = founding ? "Strong Years founding membership" : "Strong Years membership";
  return { quantity: 1, price_data: { currency: "usd", unit_amount: cents, recurring: { interval: "month" }, product_data: { name, metadata: { sku: "membership", plan: "monthly" } } } };
}

/** L3: a configured recurring price ID (partner seat, essentials) must match the amount we promise. */
export async function assertPriceAmount(s: Stripe, id: string, cents: number): Promise<void> {
  const p = await s.prices.retrieve(id);
  if (p.unit_amount !== cents || p.currency !== "usd") throw new Error(`Stripe price ${id} is ${p.unit_amount} ${p.currency}, expected ${cents} usd. Fix the env var before selling this.`);
}

export function buildSessionParams(intent: CheckoutIntent, quote: CheckoutQuote): Stripe.Checkout.SessionCreateParams {
  const def = offerDef(intent.offer_code as OfferCode);
  const items = quote.lines.filter((l) => l.sku !== "membership").map((l) => oneTime(l.sku, l.label, l.cents));
  const common = {
    customer_email: intent.email,
    client_reference_id: intent.id,
    metadata: { intent_id: intent.id, offer: intent.offer_code, arm: intent.arm ?? "gift", price_cell: intent.price_cell ?? "" },
    success_url: `${env.siteUrl}/api/checkout/complete?intent=${intent.id}&session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${env.siteUrl}/${intent.offer_code === "founding" ? "join" : `checkout/${intent.offer_code}`}?canceled=1`,
    custom_text: { submit: { message: quote.terms.join(" ").slice(0, 1200) } },
  };
  if (def.kind === "gift") {
    return {
      ...common,
      mode: "payment",
      line_items: items,
      // L15: a gift purchase does not keep the card on file (no one-click charges later).
      payment_intent_data: { statement_descriptor_suffix: "MEMBER", metadata: { intent_id: intent.id } },
    };
  }
  const founding = Boolean(quote.recurring?.founding);
  items.unshift(recurring(quote.recurring?.priceCents ?? prices.monthly, founding));
  return {
    ...common,
    // Round 8: a founding checkout holds a spot for FOUNDING_HOLD_MINUTES; the payment page
    // closes before that, so every completed payment still has its spot.
    ...(holdsFoundingSpot(intent) ? { expires_at: Math.floor(Date.now() / 1000) + CHECKOUT_SESSION_MINUTES * 60 } : {}),
    mode: "subscription",
    line_items: items,
    payment_method_collection: "always",
    subscription_data: {
      ...(intent.trial_days > 0 ? { trial_period_days: intent.trial_days } : {}),
      metadata: { intent_id: intent.id, arm: intent.arm ?? "", founding: String(founding), price_cell: intent.price_cell ?? "" },
      description: "STRONGYEARS MEMBER",
    },
  };
}
