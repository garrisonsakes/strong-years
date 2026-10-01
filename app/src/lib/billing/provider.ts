import type { Store } from "../db/store";
import type { Membership } from "../db/types";
import type { RefundResult } from "./actions";
/**
 * Billing provider adapter (CANON UPDATE 2, Oct 1 2026).
 *
 *   BILLING_PROVIDER=shopify (default): commerce runs on our own Shopify store
 *     (Shopify Payments, Shopify Subscriptions, Digital Downloads). /join redirects
 *     to Shopify checkout; Shopify webhooks provision and revoke access here; cancel,
 *     pause, card and annual upgrade live on the Shopify customer account page.
 *   BILLING_PROVIDER=stripe: the original in-app Stripe checkout (kept, not the launch path).
 *
 * Unknown values fall back to shopify (the launch path), and /api/health reports them.
 * Edge-safe: no imports, so middleware and pages can both ask.
 */
export type BillingProviderId = "shopify" | "stripe";

type Env = Record<string, string | undefined>;

export function billingProviderId(e: Env = process.env): BillingProviderId {
  return (e.BILLING_PROVIDER ?? "").trim().toLowerCase() === "stripe" ? "stripe" : "shopify";
}

export function isShopify(e: Env = process.env): boolean {
  return billingProviderId(e) === "shopify";
}

/** Health/boot problems for the provider config (names and reasons only, never values). */
export function billingConfigProblems(e: Env = process.env): string[] {
  const out: string[] = [];
  const raw = (e.BILLING_PROVIDER ?? "").trim().toLowerCase();
  if (raw && raw !== "shopify" && raw !== "stripe") out.push("BILLING_PROVIDER: must be shopify or stripe (treated as shopify)");
  if (billingProviderId(e) !== "shopify") return out;
  const domain = (e.SHOPIFY_STORE_DOMAIN ?? "").trim();
  if (!domain) out.push("SHOPIFY_STORE_DOMAIN: missing");
  else if (!/^[a-z0-9][a-z0-9.-]{1,120}\.[a-z]{2,}$/i.test(domain)) out.push("SHOPIFY_STORE_DOMAIN: not a bare host name (e.g. strongyears.myshopify.com)");
  if (!e.SHOPIFY_WEBHOOK_SECRET || e.SHOPIFY_WEBHOOK_SECRET.length < 16) out.push("SHOPIFY_WEBHOOK_SECRET: missing or too short (webhooks are refused)");
  const acct = e.SHOPIFY_CUSTOMER_ACCOUNT_URL ?? "";
  if (!/^https:\/\/[^\s]+$/.test(acct)) out.push("SHOPIFY_CUSTOMER_ACCOUNT_URL: missing or not https");
  if (!e.SHOPIFY_ADMIN_TOKEN) out.push("SHOPIFY_ADMIN_TOKEN: missing (self-serve refunds go to a person)");
  return out;
}


/** What the rest of the app asks of whichever provider is active (lib/billing/active.ts). */
export interface BillingProvider {
  id: BillingProviderId;
  /** Self-serve 14-day money-back refund of the first membership charge. */
  refundMembership(store: Store, m: Membership, now?: Date): Promise<RefundResult>;
  /**
   * Where cancel / pause / card / annual upgrade happen. External URL for Shopify
   * (the customer account subscription page); null for Stripe (our own screens).
   */
  manageUrl(): string | null;
}
