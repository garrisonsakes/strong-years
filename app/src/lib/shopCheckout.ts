import "server-only";
import { getStore } from "./db";
import { catalog, checkoutUrl, NAMED_OFFERS, resolveFrontEnd } from "./billing/shopify";
import type { BTarget } from "./bioLinks";
import type { TouchPoint } from "./db/types";
import { isShopify } from "./billing/provider";
import { shopifyLivePrices } from "./livePricing";
import { money } from "./pricing";
import { offerRules } from "./config";
import { foundingTaken } from "./founding";
import { getAttribution, getVisitorId } from "./request";
import { currentMember } from "./auth/server";
import { trackInternal } from "./analytics/meta";

/**
 * /join in Shopify mode: the visitor's sticky cell (signed visitor id) picks the
 * catalog row; attribution rides along as cart attributes. Query parameters can
 * name only an allow-listed fixed product (gifts, the plain membership), never a
 * price or a cell. Returns null when the catalog has nothing to sell.
 */
export async function shopifyJoinUrl(sp: Record<string, string | undefined>, target: BTarget = "front_end", source = "join", touch: TouchPoint | null = null): Promise<string | null> {
  const store = await getStore();
  const rows = await catalog(store);
  const visitorId = await getVisitorId();
  const stored = await getAttribution();
  // /b passes the touch it parsed from its own URL (the middleware's cookie write lands on the response, not this request).
  const attribution = touch ? { ...(stored ?? {}), last_touch: touch } : stored;
  const named = (NAMED_OFFERS as readonly string[]).includes(sp.offer ?? "") ? sp.offer! : null;
  const cohortOpen = (await foundingTaken(store)) < offerRules.foundingCap;
  let row = named ? rows.find((r) => r.sku === named) ?? null : null;
  // /b keywords name a product FAMILY (never a price or a cell): JOIN → the plain membership, FAMILY → the gift page.
  if (!row && target === "founding") row = rows.find((r) => r.sku === (cohortOpen ? "founding_monthly" : "standard_monthly")) ?? null;
  if (!row && target === "gift") row = rows.find((r) => r.sku === "gift3") ?? null;
  if (!row && target === "essentials") row = rows.find((r) => r.sku === "essentials_monthly") ?? null;
  if (named === "founding_monthly" && !cohortOpen) row = rows.find((r) => r.sku === "standard_monthly") ?? null;
  let cell: string | null = null;
  if (!row) {
    const fe = resolveFrontEnd(rows, { visitorId, cohortOpen });
    if (!fe) return null;
    row = fe.row;
    cell = fe.cell;
  }
  // R5-8: the starter code is once per customer. A signed-in member who has already used it is sent to the plain
  // membership page (the price they will actually pay), not to a page that shows $12 first.
  if (row.discount_code && (await starterUsedBy(store, await currentMember().catch(() => null)))) {
    row = rows.find((r) => r.cohort === row!.cohort && !r.discount_code && r.entitlement === row!.entitlement) ?? row;
    cell = cell ? `${cell}-used` : cell;
  }
  await trackInternal("shop_redirect", { cell, sku: row.sku, vid: visitorId, source, target });
  return checkoutUrl(row, { attribution, cell, visitorId });
}

/** Has this member already bought with a starter (first-payment) code? */
async function starterUsedBy(store: Awaited<ReturnType<typeof getStore>>, member: { id: string } | null): Promise<boolean> {
  if (!member) return false;
  const orders = await store.find("sy_orders", { member_id: member.id, kind: "membership_charge" });
  return orders.some((o) => /^bundle_m12/.test(o.offer_code) && o.status !== "refunded");
}

export interface ShopCta {
  /** Button text for the visitor's own cell, e.g. "Get the starter books: $12". */
  label: string;
  /** The terms line under the button (what's charged today and after). */
  note: string;
  todayCents: number;
  memberCents: number;
  cohortOpen: boolean;
}

/**
 * Shopify mode: what /join will actually sell this visitor (their sticky cell), so
 * every CTA and note on our pages matches the Shopify checkout it leads to. Null in
 * Stripe mode (pages keep their Stripe copy).
 */
export async function getShopCta(): Promise<ShopCta | null> {
  if (!isShopify()) return null;
  const store = await getStore();
  const rows = await catalog(store);
  const cohortOpen = (await foundingTaken(store)) < offerRules.foundingCap;
  const live = shopifyLivePrices(rows, cohortOpen);
  const fe = resolveFrontEnd(rows, { visitorId: await getVisitorId(), cohortOpen });
  const m = money(live.memberCents);
  const lock = cohortOpen ? ", locked for as long as you stay subscribed" : " until you cancel";
  if (fe && fe.row.entitlement !== "ebook" && fe.row.recurring_cents) {
    const t = money(fe.row.price_cents);
    return {
      label: `Start for ${t}: the books + your first month`,
      note: `${t} today for the starter books (yours to keep) and your first month. Then ${money(fe.row.recurring_cents)} a month${lock}. We email you before every charge. 14-day money-back guarantee. Cancel online anytime, no call needed.`,
      todayCents: fe.row.price_cents,
      memberCents: fe.row.recurring_cents,
      cohortOpen,
    };
  }
  const t = fe ? money(fe.row.price_cents) : null;
  return {
    label: t ? `Get the starter books: ${t}` : "Get the starter books",
    note: `${t ? `${t}, one time, ` : "One time, "}for the 7-Day Strength Reset and Sun Yoon's Strong Kitchen, yours to keep. Right after, you can add the ${cohortOpen ? "founding " : ""}membership with one tap: ${m} for your first month, then ${m} a month${lock}. Nothing renews unless you choose the membership.`,
    todayCents: fe?.row.price_cents ?? 0,
    memberCents: live.memberCents,
    cohortOpen,
  };
}
