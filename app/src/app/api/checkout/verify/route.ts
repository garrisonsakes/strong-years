import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { resolvePurchaseVerification } from "@/lib/billing/verifyPurchase";
import { SESSION_COOKIE } from "@/lib/auth/session";
import { sessionCookieOptions, verifiedSessionCookie } from "@/lib/auth/server";
import { refuseIfPrelaunch } from "@/lib/launchGuard";

/** The link was emailed to the account's own inbox; confirming it is proof of ownership, once. */
export async function POST(req: Request) {
  const closed = await refuseIfPrelaunch(req, "redirect");
  if (closed) return closed;
  const base = new URL(req.url).origin;
  const f = await req.formData();
  const action = String(f.get("action")) === "reject" ? "reject" : "confirm";
  const r = await resolvePurchaseVerification(await getStore(), String(f.get("token") ?? ""), action);
  if (!r.ok) return NextResponse.redirect(`${base}/login?error=expired`, 303);
  if (r.action === "reject") return NextResponse.redirect(`${base}/checkout/verify?done=rejected`, 303);
  const res = NextResponse.redirect(`${base}/welcome`, 303);
  res.cookies.set(SESSION_COOKIE, await verifiedSessionCookie(r.memberId), sessionCookieOptions);
  return res;
}
