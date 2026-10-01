import { billingProviderId, type BillingProvider } from "./provider";
import { shopifyProvider } from "./shopify";
import { stripeProvider } from "./stripe";

/** The active billing provider (BILLING_PROVIDER, default shopify). */
export function billingProvider(): BillingProvider {
  return billingProviderId() === "stripe" ? stripeProvider : shopifyProvider;
}
