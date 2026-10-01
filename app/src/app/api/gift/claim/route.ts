import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { claimGift } from "@/lib/gifts";
import { SESSION_COOKIE } from "@/lib/auth/session";
import { sessionCookieOptions, verifiedSessionCookie } from "@/lib/auth/server";

/**
 * The claim link was emailed to the recipient, so whoever holds it has proved
 * they own that inbox: the same proof a login link needs. The token works once.
 */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  const f = await req.formData();
  const token = String(f.get("token") ?? "");
  const res = await claimGift(await getStore(), token, {
    firstName: String(f.get("first_name") ?? "").trim().slice(0, 60),
    ageConfirmed: Boolean(f.get("age")),
    share: Boolean(f.get("share")),
  });
  if (!res.ok && res.reason === "age") return NextResponse.redirect(`${base}/gift/claim?token=${encodeURIComponent(token)}&error=age`, 303);
  if (!res.ok) return NextResponse.redirect(`${base}/login?error=gift`, 303);
  const out = NextResponse.redirect(`${base}/app?gift=${res.appliedAs}`, 303);
  out.cookies.set(SESSION_COOKIE, await verifiedSessionCookie(res.member.id), sessionCookieOptions);
  return out;
}
