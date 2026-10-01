import { NextResponse } from "next/server";
import { currentMember } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { OPTOUT_COOKIE, clientMeta } from "@/lib/request";

/** CCPA/CPRA "Do Not Sell or Share": a cookie for this browser, and the account flag when logged in. */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  const member = await currentMember();
  if (member) {
    const store = await getStore();
    await store.update("members", member.id, { ad_opt_out: true });
    const meta = await clientMeta();
    await store.insert("consent_log", { email: member.email, member_id: member.id, kind: "do_not_sell_share", checked: true, text_shown: "Do not sell or share my personal information", price_cents: null, first_charge_at: null, offer_code: null, ip: meta.ip, user_agent: meta.userAgent });
  }
  const res = NextResponse.redirect(`${base}/privacy-choices?done=1`, 303);
  res.cookies.set(OPTOUT_COOKIE, "1", { path: "/", maxAge: 400 * 86400, sameSite: "lax" });
  return res;
}
