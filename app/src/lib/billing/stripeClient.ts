import Stripe from "stripe";
import { env, mode } from "../config";

let client: Stripe | null = null;

/**
 * Real Stripe client, or null in mock mode. Refuses live keys unless ALLOW_LIVE_STRIPE=true,
 * so nothing can charge a real card by accident while the build is being tested.
 */
export function stripe(): Stripe | null {
  if (mode.mockStripe) return null;
  if (env.stripeSecretKey.startsWith("sk_live") && !env.allowLiveStripe) {
    throw new Error("Live Stripe key detected. Set ALLOW_LIVE_STRIPE=true only when you are ready to take real payments.");
  }
  if (!client) client = new Stripe(env.stripeSecretKey, { appInfo: { name: "strong-years" } });
  return client;
}

/** Stripe price IDs (test mode). Any that are missing fall back to inline price_data. */
export const PRICE_ENV = {
  monthly: "STRIPE_PRICE_MONTHLY",
  founding: "STRIPE_PRICE_FOUNDING",
  essentials: "STRIPE_PRICE_ESSENTIALS",
  annual: "STRIPE_PRICE_ANNUAL",
  partner: "STRIPE_PRICE_PARTNER",
  trial_fee: "STRIPE_PRICE_TRIAL_FEE",
  reset: "STRIPE_PRICE_RESET",
  kitchen: "STRIPE_PRICE_KITCHEN",
  bump: "STRIPE_PRICE_BUMP",
  program: "STRIPE_PRICE_PROGRAM",
  kit: "STRIPE_PRICE_KIT",
  printables: "STRIPE_PRICE_PRINTABLES",
  gift3: "STRIPE_PRICE_GIFT3",
  gift12: "STRIPE_PRICE_GIFT12",
} as const;

export function priceId(key: keyof typeof PRICE_ENV): string | null {
  return process.env[PRICE_ENV[key]] || null;
}
