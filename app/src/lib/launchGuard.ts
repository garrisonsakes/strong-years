import "server-only";
import { NextResponse } from "next/server";
import { redirect } from "next/navigation";
import { getStore } from "./db";
import { PRELAUNCH_MESSAGE, getLaunchState } from "./launch";
import { isShopify } from "./billing/provider";

export const SHOPIFY_CHECKOUT_MESSAGE = "Checkout happens on the Strong Years store. Start at /join.";

/**
 * Server-side prelaunch refusal for every checkout API. Returns a response to send
 * back, or null when checkout is open. JSON callers get 403 + the waitlist URL;
 * browser form posts and redirects land on /waitlist.
 */
export async function refuseIfPrelaunch(req: Request, kind: "json" | "redirect"): Promise<NextResponse | null> {
  const state = await getLaunchState(await getStore());
  if (state.live) {
    // CANON UPDATE 2: in Shopify mode the in-app (Stripe) checkout routes are closed;
    // every purchase starts at /join, which redirects to the Shopify store.
    if (!isShopify()) return null;
    if (kind === "json") return NextResponse.json({ error: SHOPIFY_CHECKOUT_MESSAGE, join: "/join" }, { status: 410, headers: { "Cache-Control": "no-store" } });
    return NextResponse.redirect(new URL("/join", new URL(req.url).origin), 303);
  }
  if (kind === "json") {
    return NextResponse.json({ error: PRELAUNCH_MESSAGE, waitlist: "/waitlist", opensAt: state.opensAt?.toISOString() ?? null }, { status: 403, headers: { "Cache-Control": "no-store" } });
  }
  return NextResponse.redirect(new URL("/waitlist?from=checkout", new URL(req.url).origin), 303);
}

/** Pages: send prelaunch visitors to the waitlist, keeping attribution and lead params. */
export async function redirectIfPrelaunch(sp: Record<string, string | string[] | undefined> = {}, opts: { internalCheckout?: boolean } = {}): Promise<void> {
  const state = await getLaunchState(await getStore());
  if (state.live) {
    if (opts.internalCheckout && isShopify()) redirect("/join");
    return;
  }
  const keep = new URLSearchParams();
  for (const k of ["lead", "ref", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "platform", "page", "post_id", "keyword", "character"]) {
    const v = sp[k];
    if (typeof v === "string" && v.length <= 200) keep.set(k, v);
  }
  keep.set("from", "checkout");
  redirect(`/waitlist?${keep.toString()}`);
}
