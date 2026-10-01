import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { getStore } from "@/lib/db";
import { consumeLoginCode } from "@/lib/auth/verification";
import { sessionCookieOptions, verifiedSessionCookie } from "@/lib/auth/server";
import { SESSION_COOKIE } from "@/lib/auth/session";
import { findMemberByEmail, normalizeEmail } from "@/lib/members";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { LOGIN_EMAIL_COOKIE } from "@/lib/loginView";

/**
 * Sign-in step 2: the 6-digit code from the email. Wrong code, unknown address,
 * expired code and rate limit all look the same to the caller. Limits: per IP and
 * per address, plus 5 wrong tries burn the code.
 */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  const fail = (e = "code") => NextResponse.redirect(`${base}/login?sent=1&error=${e}`, 303);
  const raw = await req.text();
  if (raw.length > 512) return new NextResponse("Too large", { status: 413 });
  const code = (new URLSearchParams(raw).get("code") ?? "").slice(0, 20);
  const email = normalizeEmail((await cookies()).get(LOGIN_EMAIL_COOKIE)?.value ?? "").slice(0, 200);
  if (!email) return NextResponse.redirect(`${base}/login?error=expired`, 303);
  if (!(await hit(`code:ip:${clientIp(req)}`, LIMITS.loginCodePerIp)) || !(await hit(`code:email:${email}`, LIMITS.loginCodePerEmail))) return fail("busy");
  const store = await getStore();
  const member = await findMemberByEmail(store, email);
  if (!member || !(await consumeLoginCode(store, member.id, code))) return fail();
  const res = NextResponse.redirect(`${base}/app`, 303);
  // The code proves the inbox, exactly like the link (R2-1: the first proof revokes older sessions).
  res.cookies.set(SESSION_COOKIE, await verifiedSessionCookie(member.id), sessionCookieOptions);
  res.cookies.delete(LOGIN_EMAIL_COOKIE);
  return res;
}
