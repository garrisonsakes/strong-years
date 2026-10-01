import { NextResponse } from "next/server";
import { mode } from "@/lib/config";
import { getStore } from "@/lib/db";
import { DEMO_EMAIL } from "@/lib/db/seed";
import { findMemberByEmail } from "@/lib/members";
import { SESSION_COOKIE } from "@/lib/auth/session";
import { sessionCookieOptions, sessionCookieValue } from "@/lib/auth/server";

/** Demo-only login as the seeded test member. Disabled whenever Supabase is configured. */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  if (!mode.mockDb) return NextResponse.redirect(`${base}/login`, 303);
  const member = await findMemberByEmail(await getStore(), DEMO_EMAIL);
  if (!member) return NextResponse.redirect(`${base}/login?error=demo`, 303);
  const res = NextResponse.redirect(`${base}/app`, 303);
  res.cookies.set(SESSION_COOKIE, await sessionCookieValue(member.id), sessionCookieOptions);
  return res;
}
