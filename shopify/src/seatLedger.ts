/**
 * Founding seat ledger. The founding cohort cap (5,000) is the REAL inventory of the founding variant
 * (SKU SY-FOUNDING-25), so the storefront counter reads inventory and nothing else.
 *
 * Problem this solves: with Shopify Subscriptions, every renewal order is an ordinary order that also
 * decrements inventory, and since Dec 2024 Shopify Subscriptions respects inventory (a renewal fails when the
 * variant is out of stock with policy DENY). Left alone, renewals would eat seats and, at 0, block renewals.
 *
 * Rules (pure function; the members app executes the returned operations with the Admin API):
 *  1. A customer's FIRST paid founding order consumes a seat (Shopify already decremented it). No action.
 *  2. Every LATER paid founding order is a renewal → +1 (give the seat back; renewals never consume seats).
 *  3. A refund of the seat-consuming first order (the 14-day money-back guarantee) → +1, unless the refund
 *     already restocked the line (restock_type != "no_restock"), to avoid double counting.
 *     Canon: "If someone takes a refund, their seat goes back."
 *  4. Cancellation does NOT return a seat (the count is "first charge succeeded and not refunded").
 *  5. When available reaches 0 → switch the variant to inventoryPolicy CONTINUE immediately (renewals of
 *     existing members must never fail) and run `--phase=close-founding` (unpublish + standard price live).
 * Idempotency: every adjustment carries referenceDocumentUri strongyears://seat-ledger/<kind>/<orderId>;
 * the members app stores processed URIs and skips duplicates (webhooks can be delivered more than once).
 */
import { FOUNDING_CAP } from "../config/catalog.ts";
import { OPS } from "./operations.ts";

export const FOUNDING_SKU = "SY-FOUNDING-25";

export interface SeatContext {
  inventoryItemId: string;
  locationId: string;
  productId: string;
  variantId: string;
  /** Has this customer already had a paid founding order before this one? (members DB) */
  customerHadPriorFoundingOrder: boolean;
  /** Was the refunded order the customer's seat-consuming first founding order? (members DB) */
  refundedOrderWasFirstFounding?: boolean;
  /** Current available quantity after this event (from the order/refund or an inventory read). */
  availableAfter?: number;
  processedRefs: Set<string>;
}

export type SeatEvent =
  | { topic: "orders/paid"; orderId: string; foundingQty: number }
  | { topic: "refunds/create"; orderId: string; refundId: string; foundingQtyRefunded: number; restockType: "no_restock" | "cancel" | "return" | "legacy_restock" };

export interface SeatAction { op: keyof typeof OPS; variables: Record<string, unknown>; why: string; ref?: string }

export function seatActions(ev: SeatEvent, ctx: SeatContext, cap: number | null = FOUNDING_CAP): SeatAction[] {
  const actions: SeatAction[] = [];
  if (cap == null) return actions;   // no seat cap since Oct 2 2026: the founding variant is untracked, nothing to keep

  const adjust = (delta: number, ref: string, why: string) => {
    if (ctx.processedRefs.has(ref) || delta === 0) return;
    actions.push({
      op: "InventoryAdjust",
      why,
      ref,
      variables: { input: { name: "available", reason: "correction", referenceDocumentUri: ref, changes: [{ inventoryItemId: ctx.inventoryItemId, locationId: ctx.locationId, delta }] } },
    });
  };
  if (ev.topic === "orders/paid" && ev.foundingQty > 0) {
    if (ctx.customerHadPriorFoundingOrder) adjust(ev.foundingQty, `strongyears://seat-ledger/renewal/${ev.orderId}`, "Renewal order: give the seat back (renewals never consume founding seats).");
  }
  if (ev.topic === "refunds/create" && ev.foundingQtyRefunded > 0 && ctx.refundedOrderWasFirstFounding && ev.restockType === "no_restock") {
    adjust(ev.foundingQtyRefunded, `strongyears://seat-ledger/refund/${ev.refundId}`, "Refund of the first founding charge: the seat goes back.");
  }
  const available = ctx.availableAfter;
  if (available !== undefined && available <= 0) {
    actions.push({
      op: "VariantInventoryPolicy",
      why: "Founding cap reached: allow renewals regardless of stock, then run --phase=close-founding.",
      variables: { productId: ctx.productId, variants: [{ id: ctx.variantId, inventoryPolicy: "CONTINUE" }] },
    });
  }
  return actions;
}

/** Public counter line (FUNNEL.md canonical {{COUNT_LINE}} rule). The theme implements the same rule in Liquid. */
export function countLine(opts: { cap: number; available: number; closeDateHuman: string; nowHuman: string; domain: string }): string {
  const taken = Math.max(0, opts.cap - Math.max(0, opts.available));
  if (taken >= opts.cap) return `The founding group is full. New members join at the standard price.`;
  if (taken < 1000) return `Founding membership is open to the first ${opts.cap.toLocaleString("en-US")} members or until ${opts.closeDateHuman}, whichever comes first. See the live count: ${opts.domain}/pages/membership-and-cancellation#founding`;
  return `${taken.toLocaleString("en-US")} of ${opts.cap.toLocaleString("en-US")} founding seats taken as of ${opts.nowHuman}`;
}
