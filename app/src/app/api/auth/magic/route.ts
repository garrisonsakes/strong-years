import { NextResponse } from "next/server";
import { env, mode } from "@/lib/config";
import { getStore } from "@/lib/db";
import { issueLoginLinkAndCode } from "@/lib/auth/verification";
import { findMemberByEmail, normalizeEmail } from "@/lib/members";
import { sendEmail } from "@/lib/notify";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { LOGIN_EMAIL_COOKIE } from "@/lib/loginView";

/**
 * Sign-in step 1: email a one-time link AND a 6-digit code to the member's address
 * (the Shopify customer email, in Shopify mode). Identical response whether or not
 * the address belongs to a member, and when rate-limited (no enumeration).
 */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  const f = await req.formData();
  const email = normalizeEmail(String(f.get("email") ?? "")).slice(0, 200);
  const sent = (extra = "") => {
    const res = NextResponse.redirect(`${base}/login?sent=1${extra}`, 303);
    // Which address the code is for (not a secret; the code is). 30 minutes, this browser only.
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) res.cookies.set(LOGIN_EMAIL_COOKIE, email, { httpOnly: true, sameSite: "lax", path: "/", maxAge: 30 * 60, secure: env.siteUrl.startsWith("https") });
    return res;
  };
  // M5: same "sent" screen when limited, so the limiter can't be used to probe accounts.
  if (!(await hit(`magic:ip:${clientIp(req)}`, LIMITS.magicPerIp)) || !(await hit(`magic:email:${email}`, LIMITS.magicPerEmail))) return sent();
  const store = await getStore();
  const member = await findMemberByEmail(store, email);
  // Same response whether or not the email exists (no account enumeration).
  if (!member) return sent();
  const { link, code } = await issueLoginLinkAndCode(store, member.id, env.siteUrl);
  const msg = await sendEmail({
    to: email,
    template: "magic_link",
    subject: `Your Strong Years sign-in code: ${code}`,
    text: `Your sign-in code is ${code}. Type it on the sign-in page, or tap this link to sign in (both work for 30 minutes, once): ${link}\n\nDidn't ask for this? Ignore it; nobody can sign in without this email.`,
    secrets: [link, code],
  });
  // L1: the link is only ever shown on-screen for the in-memory demo.
  const showLink = msg.status === "stubbed" && mode.mockDb;
  return sent(showLink ? `&link=${encodeURIComponent(link)}` : "");
}
