/**
 * Payment-processor abstraction. Stripe is implemented; Braintree is a stub adapter behind
 * the same interface (activation needs the client: merchant account, credentials, and the
 * braintree SDK wired into createCheckout / chargeOffSession / refund / cancel).
 */
import { mode, processorConfig } from "../../config";
import type { Store } from "../../db/store";
import type { CheckoutIntent, ProcessorId } from "../../db/types";
import type { CheckoutQuote } from "../../pricing";
import { alertOnCall } from "../../notify";
import { stripe } from "../stripeClient";
import { buildSessionParams } from "../stripeSession";
import { chooseProcessor, type RouteResult } from "./router";

export type ProcessorStatus = "live" | "mock" | "off";

export interface PaymentProcessor {
  id: ProcessorId;
  status(): ProcessorStatus;
  /** Returns where to send the buyer to pay. */
  createCheckout(intent: CheckoutIntent, quote: CheckoutQuote): Promise<{ redirectUrl: string; externalId: string | null }>;
  chargeOffSession(i: { customerId: string; paymentMethodId: string; amountCents: number; description: string; metadata: Record<string, string>; idempotencyKey?: string }): Promise<{ ok: boolean; paymentId: string | null; error?: string }>;
  /** C4: callers only mark money as refunded when this says "succeeded" (or later, via webhook, for "pending"). */
  refund(paymentId: string, amountCents: number, idempotencyKey?: string): Promise<RefundOutcome>;
}

export interface RefundOutcome {
  status: "succeeded" | "pending" | "failed";
  refundId: string | null;
  error?: string;
}

const mockCheckout = async (intent: CheckoutIntent) => ({ redirectUrl: `/checkout/mock/${intent.id}`, externalId: null });

export const stripeProcessor: PaymentProcessor = {
  id: "stripe",
  status: () => (mode.mockStripe ? "mock" : "live"),
  async createCheckout(intent, quote) {
    const s = stripe();
    if (!s) return mockCheckout(intent);
    const session = await s.checkout.sessions.create(buildSessionParams(intent, quote));
    return { redirectUrl: session.url!, externalId: session.id };
  },
  async chargeOffSession(i) {
    const s = stripe();
    if (!s) return { ok: true, paymentId: `pi_mock_${crypto.randomUUID().slice(0, 12)}` };
    try {
      const pi = await s.paymentIntents.create(
        {
          amount: i.amountCents,
          currency: "usd",
          customer: i.customerId,
          payment_method: i.paymentMethodId,
          off_session: true,
          confirm: true,
          description: i.description,
          metadata: i.metadata,
          statement_descriptor_suffix: "MEMBER",
        },
        i.idempotencyKey ? { idempotencyKey: i.idempotencyKey } : undefined,
      );
      return pi.status === "succeeded" ? { ok: true, paymentId: pi.id } : { ok: false, paymentId: null, error: "Your bank asked for extra confirmation. No charge was made." };
    } catch (err) {
      // M8: declines and 3DS-required errors are normal; show a friendly message, never a 500.
      console.error("off-session charge failed", (err as { code?: string }).code ?? err);
      return { ok: false, paymentId: null, error: "Your card was declined or your bank asked for extra confirmation. No charge was made." };
    }
  },
  async refund(paymentId, amountCents, idempotencyKey) {
    const s = stripe();
    if (!s) return { status: "succeeded", refundId: `re_mock_${crypto.randomUUID().slice(0, 12)}` };
    if (paymentId.startsWith("pi_mock_")) return { status: "failed", refundId: null, error: "mock payment on a live account" };
    try {
      const r = await s.refunds.create(
        { payment_intent: paymentId, amount: amountCents, reason: "requested_by_customer" },
        idempotencyKey ? { idempotencyKey } : undefined,
      );
      const status = r.status === "succeeded" ? "succeeded" : r.status === "pending" || r.status === "requires_action" ? "pending" : "failed";
      return { status, refundId: r.id, ...(status === "failed" ? { error: r.failure_reason ?? "refund failed" } : {}) };
    } catch (err) {
      return { status: "failed", refundId: null, error: err instanceof Error ? err.message : String(err) };
    }
  },
};

function braintreeCredsPresent() {
  return Boolean(process.env.BRAINTREE_MERCHANT_ID && process.env.BRAINTREE_PUBLIC_KEY && process.env.BRAINTREE_PRIVATE_KEY);
}

/** STUB. Same interface; routes through the test simulator until the real SDK is wired in. */
export const braintreeProcessor: PaymentProcessor = {
  id: "braintree",
  status: () => {
    if (!processorConfig.braintreeEnabled) return "off";
    // Credentials present but the adapter isn't implemented yet: stay out of rotation.
    if (braintreeCredsPresent()) return "off";
    // H6: the simulator is only reachable in a test build with no live processor at all.
    return braintreeSimulatorAllowed() ? "mock" : "off";
  },
  async createCheckout(intent) {
    if (braintreeProcessor.status() !== "mock") throw new Error("Braintree adapter is a stub. Implement createCheckout with the braintree SDK (Drop-in UI + Subscription.create) before activating.");
    return mockCheckout(intent);
  },
  async chargeOffSession() {
    if (braintreeProcessor.status() !== "mock") throw new Error("Braintree adapter is a stub (chargeOffSession).");
    return { ok: true, paymentId: `bt_mock_${crypto.randomUUID().slice(0, 12)}` };
  },
  async refund() {
    if (braintreeProcessor.status() !== "mock") return { status: "failed", refundId: null, error: "Braintree adapter is a stub (refund)." };
    return { status: "succeeded", refundId: `bt_re_mock_${crypto.randomUUID().slice(0, 12)}` };
  },
};

/** H6: simulators never run next to real money or in a production build. */
export function braintreeSimulatorAllowed(): boolean {
  return mode.mockStripe && process.env.NODE_ENV !== "production" && process.env.VERCEL_ENV !== "production";
}

/** H6: /checkout/mock/* and /api/checkout/mock-complete only exist in the test build. */
export function mockCheckoutAllowed(): boolean {
  return mode.mockStripe && (process.env.NODE_ENV !== "production" || process.env.ALLOW_MOCK_CHECKOUT_IN_PROD_BUILD === "true") && process.env.VERCEL_ENV !== "production";
}

/**
 * Shopify orders never go through the in-app processor router: Shopify Payments takes
 * the money, refunds go through lib/billing/shopify.ts. This entry only makes sure a
 * Shopify order handed to a Stripe-path helper is refused instead of mis-routed.
 */
const shopifyOrdersProcessor: PaymentProcessor = {
  id: "shopify",
  status: () => "off",
  async createCheckout() {
    throw new Error("Shopify checkout happens on the Shopify store (/join redirects there).");
  },
  async chargeOffSession() {
    return { ok: false, paymentId: null, error: "One-click charges happen in Shopify's post-purchase offer." };
  },
  async refund() {
    return { status: "failed", refundId: null, error: "Refund Shopify orders through lib/billing/shopify.ts." };
  },
};

export const PROCESSORS: Record<ProcessorId, PaymentProcessor> = { stripe: stripeProcessor, braintree: braintreeProcessor, shopify: shopifyOrdersProcessor };

export function processorFor(id: ProcessorId | null | undefined): PaymentProcessor {
  return PROCESSORS[id ?? "stripe"] ?? stripeProcessor;
}

/**
 * H7: 30-day paid volume per processor. On Supabase this is one SQL sum (no
 * 1,000-row cap, no row download per checkout); in memory it sums the rows.
 */
export async function volume30d(store: Store, id: ProcessorId, now = new Date()): Promise<number> {
  const since = new Date(now.getTime() - 30 * 86_400_000).toISOString();
  if (store.rpc) {
    const v = await store.rpc("processor_volume_cents", { p_processor: id, p_since: since });
    return Number(v ?? 0);
  }
  const orders = await store.find("sy_orders", { processor: id, status: "paid", created_at: { gte: since } });
  return orders.reduce((s, o) => s + o.amount_cents, 0);
}

export async function routeCheckout(store: Store, key: string, amountCents: number): Promise<RouteResult> {
  const candidates = await Promise.all(
    (["stripe", "braintree"] as ProcessorId[]).map(async (id) => ({
      id,
      available: PROCESSORS[id].status() !== "off",
      volume30dCents: await volume30d(store, id),
      capCents: id === "stripe" ? processorConfig.stripeCap : processorConfig.braintreeCap,
    })),
  );
  const result = chooseProcessor({ routing: processorConfig.routing, braintreeShare: processorConfig.braintreeShare, key, amountCents, candidates });
  if (result.overCap) await alertOnCall("Processor volume caps reached: raise caps or add capacity before adding ad spend", "kpis");
  return result;
}
