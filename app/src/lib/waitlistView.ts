import "server-only";
import { getStore } from "./db";
import { offerRules } from "./config";
import { foundingTaken } from "./founding";
import { getLaunchState } from "./launch";
import { catalog } from "./billing/shopify";
import { isShopify } from "./billing/provider";
import { livePrices, shopifyLivePrices } from "./livePricing";
import { getFoundingOffer } from "./request";

/** Everything the waitlist page states as fact, from the same sources checkout uses. */
export async function waitlistFacts(now = new Date()) {
  const store = await getStore();
  const state = await getLaunchState(store, now);
  const cap = offerRules.foundingCap;
  const claimed = Math.min(cap, await foundingTaken(store, now));
  const cohortOpen = claimed < cap;
  const memberCents = isShopify() ? shopifyLivePrices(await catalog(store), cohortOpen).memberCents : livePrices(await getFoundingOffer()).memberCents;
  const closeDate = (process.env.FOUNDING_CLOSE_DATE ?? "").trim() || null;
  const opensAt = state.opensAt && state.opensAt.getTime() > now.getTime() ? state.opensAt : null;
  return { live: state.live, opensAt, claimed, cap, cohortOpen, memberCents, closeDate };
}
