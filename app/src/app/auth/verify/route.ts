import { NextResponse } from "next/server";
import { consumeMagicLink, sessionCookieOptions, verifiedSessionCookie } from "@/lib/auth/server";
import { SESSION_COOKIE } from "@/lib/auth/session";

export async function GET(req: Request) {
  const url = new URL(req.url);
  const memberId = await consumeMagicLink(url.searchParams.get("token") ?? "");
  if (!memberId) return NextResponse.redirect(`${url.origin}/login?error=expired`, 303);
  const next = url.searchParams.get("next") ?? "/app";
  const safeNext = /^\/(app|gift|welcome)(\/|\?|$)/.test(next) ? next : "/app";
  const res = NextResponse.redirect(`${url.origin}${safeNext}`, 303);
  // R2-1: the link proves the inbox; the first proof revokes any session a checkout created.
  res.cookies.set(SESSION_COOKIE, await verifiedSessionCookie(memberId), sessionCookieOptions);
  return res;
}
