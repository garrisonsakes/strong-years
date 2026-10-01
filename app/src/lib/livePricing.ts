/**
 * Round 9 (AUDIT_FINAL end, condition 1): one live source for every price a page
 * mentions. Every number here comes from quoteCheckout() with exactly the inputs
 * startCheckout() uses (real cohort state, the visitor's price cell), so a page can
 * never say "$25 a month" while checkout charges $35 after the founding cohort fills.
 */
import type { FoundingOffer } from "./blitz";
import type { Arm, ShopifyProductRow } from "./db/types";
import { quoteCheckout, type OfferCode } from "./pricing";

export interface LivePrices {
  cohortOpen: boolean;
  /** Arm B: charged today and every month (founding price while open, standard after). */
  memberCents: number;
  /** Arm A: what the $1 trial renews at. */
  trialRenewCents: number;
  /** Reset / Kitchen front ends: the membership price after the included period, by arm. */
  frontEndRenewCents: Record<Arm, number>;
}

/** The same quote inputs checkout builds (lib/billing/checkout.ts). */
export function liveQuoteInputs(offer: Pick<FoundingOffer, "priceCents" | "cohortOpen">, arm: Arm) {
  return { foundingCents: arm === "B" ? offer.priceCents : undefined, cohortOpen: offer.cohortOpen, standardCents: offer.priceCents };
}

function renewCents(offer: Pick<FoundingOffer, "priceCents" | "cohortOpen">, code: OfferCode, arm: Arm, now: Date): number {
  const q = quoteCheckout({ offer: code, arm, now, ...liveQuoteInputs(offer, arm) });
  if (!q.recurring) throw new Error(`no recurring price for ${code}`);
  return q.recurring.priceCents;
}

export function livePrices(offer: Pick<FoundingOffer, "priceCents" | "cohortOpen">, now = new Date()): LivePrices {
  return {
    cohortOpen: offer.cohortOpen,
    memberCents: renewCents(offer, "founding", "B", now),
    trialRenewCents: renewCents(offer, "trial", "A", now),
    frontEndRenewCents: { A: renewCents(offer, "reset", "A", now), B: renewCents(offer, "reset", "B", now) },
  };
}

/**
 * CANON UPDATE 2 (Shopify): the membership prices a page may mention come from the
 * same catalog rows /join sends people to (shopify_products, mirroring the store),
 * chosen by the real cohort state. Fallbacks are the canon defaults.
 */
export interface ShopifyLivePrices {
  cohortOpen: boolean;
  /** What a new member pays per month right now (founding while open, standard after). */
  memberCents: number;
  foundingCents: number;
  standardCents: number;
  annualCents: number;
}

export function shopifyLivePrices(rows: Pick<ShopifyProductRow, "sku" | "recurring_cents" | "price_cents">[], cohortOpen: boolean): ShopifyLivePrices {
  const cents = (sku: string, fallback: number) => {
    const r = rows.find((x) => x.sku === sku);
    return r ? (r.recurring_cents ?? r.price_cents) : fallback;
  };
  const foundingCents = cents("founding_monthly", 2500);
  const standardCents = cents("standard_monthly", 3500);
  return { cohortOpen, foundingCents, standardCents, memberCents: cohortOpen ? foundingCents : standardCents, annualCents: cents("annual_founding", 24900) };
}
