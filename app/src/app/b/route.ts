import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { getLaunchState } from "@/lib/launch";
import { isShopify } from "@/lib/billing/provider";
import { shopifyJoinUrl } from "@/lib/shopCheckout";
import { cleanKeywordParam, cleanPageParam, keywordTarget } from "@/lib/bioLinks";
import { ATTR_COOKIE, LAST_TOUCH_COOKIE, attributionFromUrl, encodeAttribution, touchFromUrl } from "@/lib/analytics/attribution";
import { bDestination, qualifyFromQuery, route, type RouteContext } from "@/lib/offers/route";
import { assignArm, logExposure } from "@/lib/offers/experiments";
import { memberContext } from "@/lib/offers/context";
import { getVisitorId } from "@/lib/request";
import { currentMember } from "@/lib/auth/server";
import { foundingTaken } from "@/lib/founding";
import { offerRules } from "@/lib/config";

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
 *
 * MONETIZATION_ENGINE.md §2: live, the routing table (lib/offers/route.ts, the same data the DM bot uses) picks the
 * offer FAMILY from the keyword, the two DM qualify answers (g, a), platform, country and, for a signed-in member,
 * what they own and how long they've lapsed. Families still go through the sticky cell; free paths (Day 1, the
 * group-quote and price-help forms) are our own pages; a lapsed member gets the win-back code for their tier.
 * Every redirect logs one exposure row (offer_events).
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
    const member = await currentMember().catch(() => null);
    const visitorId = await getVisitorId();
    const cohortOpen = (await foundingTaken(store)) < offerRules.foundingCap;
    const country = (req.headers.get("x-vercel-ip-country") ?? "").toUpperCase();
    const ctx: RouteContext = {
      mode: "launch",
      surface: "b",
      keyword: t,
      platform: (sp.utm_source ?? sp.platform ?? "").toLowerCase().slice(0, 12) || null,
      country: /^[A-Z]{2}$/.test(country) ? country : null,
      ...qualifyFromQuery(sp.g, sp.a),
      ...(member ? memberContext(await store.find("memberships", { member_id: member.id }), await store.find("sy_orders", { member_id: member.id })) : {}),
    };
    // The keyword's own family (JOIN, FAMILY, ESSENTIALS) is respected for non-members; routing refines everything else.
    const r = route(ctx);
    const dest = bDestination(r, cohortOpen);
    const kwTarget = keywordTarget(t);
    const target = dest.kind === "family" ? (kwTarget !== "front_end" && dest.target === "front_end" ? kwTarget : dest.target) : null;
    await logExposure(store, {
      subject: { visitorId, memberId: member?.id ?? null }, surface: "b", offer: r.offer, rule: r.rule,
      experiment: target === "front_end" ? "fe_cell" : null, arm: target === "front_end" ? assignArm("fe_cell", visitorId) : null,
      channel: (sp.utm_medium ?? "").slice(0, 20) || null,
    });
    if (dest.kind === "path") {
      location = `${dest.path}${dest.path.includes("?") ? "&" : "?"}${forward.toString()}`;
    } else {
      const shop = await shopifyJoinUrl({ ...sp, offer: undefined }, target ?? "front_end", "b", touch);
      location = shop && dest.code ? withDiscount(shop, dest.code) : shop ?? `/join?${forward.toString()}`;
    }
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

/** Routes a store product URL through Shopify's /discount/<CODE> share link (the win-back code), once. */
function withDiscount(storeUrl: string, code: string): string {
  if (!/^[A-Z0-9]{2,32}$/.test(code) || storeUrl.includes("/discount/")) return storeUrl;
  const u = new URL(storeUrl);
  return `${u.origin}/discount/${code}?redirect=${encodeURIComponent(u.pathname + u.search)}`;
}
