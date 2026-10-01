import { env } from "./config";
import type { FoundingOffer } from "./blitz";
import type { Arm } from "./db/types";
import { BUMP_ORDER, quoteCheckout, type BumpKey, type CheckoutQuote, type OfferCode } from "./pricing";
import { toView, type QuoteView } from "./quoteView";
import { signQuote } from "./quoteSig";

export function bumpKey(keys: Iterable<BumpKey>): string {
  const set = new Set(keys);
  return BUMP_ORDER.filter((k) => set.has(k)).join(",");
}

/** Every bump combination, quoted on the server, so the terms box always shows exact totals. */
export function buildQuotes(i: { offer: OfferCode; arm: Arm; gentle: boolean; founding: FoundingOffer | null; now?: Date }) {
  const now = i.now ?? new Date();
  const domain = env.siteUrl.replace(/^https?:\/\//, "");
  const isB = i.arm === "B" && i.founding !== null;
  const base = {
    offer: i.offer,
    arm: i.arm,
    now,
    gentle: i.gentle,
    timeZone: env.displayTimeZone,
    domain,
    foundingCents: isB ? i.founding!.priceCents : undefined,
    // Both arms follow the real cohort: after the cap the trial also renews at the standard price.
    cohortOpen: i.founding ? i.founding.cohortOpen : true,
    standardCents: i.founding ? i.founding.priceCents : undefined,
  };
  const plain: CheckoutQuote = quoteCheckout({ ...base, bumps: [] });
  const allowed = plain.bumpsAllowed;
  const quotes: Record<string, QuoteView> = {};
  for (let mask = 0; mask < 1 << allowed.length; mask++) {
    const chosen = allowed.filter((_, idx) => mask & (1 << idx));
    const q = quoteCheckout({ ...base, bumps: chosen });
    quotes[bumpKey(chosen)] = { ...toView(q), sig: signQuote(q) };
  }
  return { quotes, bumpsAllowed: allowed, plain };
}

/**
 * R2-2: the gift page's two quotes, signed like /join's so /api/checkout accepts
 * exactly the terms the buyer saw (an unsigned view fails the M1 check).
 */
export function buildGiftQuotes(now: Date = new Date()): { q3: QuoteView; q12: QuoteView } {
  const domain = env.siteUrl.replace(/^https?:\/\//, "");
  const view = (offer: "gift3" | "gift12"): QuoteView => {
    const q = quoteCheckout({ offer, arm: "A", bump: false, now, timeZone: env.displayTimeZone, domain });
    return { ...toView(q), sig: signQuote(q) };
  };
  return { q3: view("gift3"), q12: view("gift12") };
}
