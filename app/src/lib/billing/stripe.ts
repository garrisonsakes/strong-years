/**
 * Stripe billing provider (BILLING_PROVIDER=stripe). Not the launch path since
 * CANON UPDATE 2; kept behind the adapter so it can be switched back on. The
 * implementation is the original in-app checkout, webhook and account actions
 * (lib/billing/checkout.ts, webhook.ts, actions.ts).
 */
import type { BillingProvider } from "./provider";
import { refundMembership } from "./actions";

export const stripeProvider: BillingProvider = {
  id: "stripe",
  refundMembership: (store, m, now) => refundMembership(store, m, now),
  manageUrl: () => null,
};
