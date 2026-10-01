import { NextResponse } from "next/server";
import { SESSION_COOKIE } from "@/lib/auth/session";
import { currentMember, revokeSessions } from "@/lib/auth/server";

/** L7: logging out revokes every session for this member (shared family devices). */
export async function POST(req: Request) {
  const member = await currentMember();
  if (member) await revokeSessions(member.id);
  const res = NextResponse.redirect(`${new URL(req.url).origin}/start`, 303);
  res.cookies.set(SESSION_COOKIE, "", { path: "/", maxAge: 0 });
  return res;
}
