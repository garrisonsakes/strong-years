import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { getLaunchState } from "@/lib/launch";
import { isShopify } from "@/lib/billing/provider";
import { shopifyJoinUrl } from "@/lib/shopCheckout";
import { cleanKeywordParam, cleanPageParam, keywordTarget } from "@/lib/bioLinks";
import { ATTR_COOKIE, LAST_TOUCH_COOKIE, attributionFromUrl, encodeAttribution, touchFromUrl } from "@/lib/analytics/attribution";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * /b: the one link every DM, Story sticker, pinned comment and affiliate card uses
 * (ORGANIC_ENGINE.md §3, FUNNEL.md §4.19). It assigns nothing by itself: the sticky
 * cell comes from the signed visitor cookie the middleware sets, the product family
 * from the keyword "t", and attribution (utm_*, post_id/pid, page/p, keyword/t,
 * character, platform, mc_id, ref) from the query. Then it 302s:
 *   prelaunch → /waitlist (same parameters, so the sign-up is credited to the post)
 *   live      → the Shopify product page for the visitor's cell (cell B through the
 *               /discount/STARTER12 share link), or /join in Stripe mode.
 * Keywords never pick a price: BOOK/STRONG/SOUP… → the front end at the visitor's
 * cell; JOIN → the plain membership; FAMILY → the gift page.
 */
export async function GET(req: Request) {
  const url = new URL(req.url);
  const sp = Object.fromEntries(url.searchParams) as Record<string, string | undefined>;
  const t = cleanKeywordParam(sp.t ?? sp.keyword);
  const page = cleanPageParam(sp.p ?? sp.page);
  const ref = (sp.ref ?? "").trim().toUpperCase();
  const refOk = /^[A-Z0-9]{2,32}$/.test(ref) ? ref : null;

  // Aliases the middleware doesn't know (t, p, pid, ref) become ordinary attribution fields.
  const normalized = new URL(url.toString());
  if (t && !normalized.searchParams.get("keyword")) normalized.searchParams.set("keyword", t);
  if (page && !normalized.searchParams.get("page")) normalized.searchParams.set("page", page);
  if (sp.pid && !normalized.searchParams.get("post_id")) normalized.searchParams.set("post_id", sp.pid);
  if (refOk && !normalized.searchParams.get("utm_source")) {
    normalized.searchParams.set("utm_source", "affiliate");
    normalized.searchParams.set("utm_campaign", refOk);
  }
  const touch = touchFromUrl(normalized);
  const first = attributionFromUrl(normalized);

  const store = await getStore();
  const state = await getLaunchState(store);
  const forward = new URLSearchParams();
  for (const [k, v] of normalized.searchParams) {
    if (["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "platform", "page", "post_id", "keyword", "character", "mc_id", "ref", "lead", "sy_v"].includes(k) && v.length <= 200) forward.set(k, v);
  }
  let location: string;
  if (!state.live) {
    forward.set("from", "b");
    location = `/waitlist?${forward.toString()}`;
  } else if (isShopify()) {
    location = (await shopifyJoinUrl({ ...sp, offer: undefined }, keywordTarget(t), "b", touch)) ?? `/join?${forward.toString()}`;
  } else {
    location = `/join?${forward.toString()}`;
  }
  const res = NextResponse.redirect(new URL(location, url.origin), 302);
  res.headers.set("Cache-Control", "private, no-store");
  // The same cookies the middleware writes for ordinary attributed visits, now for the aliases too.
  const cookieHeader = req.headers.get("cookie") ?? "";
  if (touch) res.cookies.set(LAST_TOUCH_COOKIE, encodeAttribution(touch), { maxAge: 90 * 86400, path: "/", sameSite: "lax" });
  if (first && !new RegExp(`(^|;\\s*)${ATTR_COOKIE}=`).test(cookieHeader)) res.cookies.set(ATTR_COOKIE, encodeAttribution(first), { maxAge: 90 * 86400, path: "/", sameSite: "lax" });
  return res;
}
