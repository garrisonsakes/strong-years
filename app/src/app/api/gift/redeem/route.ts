import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { requestGiftClaim } from "@/lib/gifts";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";

/**
 * C1: a gift code never signs anyone in. Entering it only sends a fresh private
 * link to the recipient's own inbox (the address the gifter typed).
 */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  let code = "";
  try {
    const f = await req.formData();
    code = String(f.get("code") ?? "").slice(0, 40);
  } catch {
    // R5-12: a non-form body (wrong content type) is a bad code, not a 500.
    return NextResponse.redirect(`${base}/gift/redeem?error=code`, 303);
  }
  if (!(await hit(`gift:ip:${clientIp(req)}`, LIMITS.giftRedeemPerIp))) {
    return NextResponse.redirect(`${base}/gift/redeem?error=busy`, 303);
  }
  const r = await requestGiftClaim(await getStore(), code);
  if (r.status === "not_found") return NextResponse.redirect(`${base}/gift/redeem?error=code`, 303);
  if (r.status === "redeemed") return NextResponse.redirect(`${base}/gift/redeem?error=used`, 303);
  return NextResponse.redirect(`${base}/gift/redeem?sent=1&to=${encodeURIComponent(r.to)}`, 303);
}
