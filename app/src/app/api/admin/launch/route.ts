import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { openCheckoutNow } from "@/lib/launch";
import { parseBasicAuth } from "@/lib/safeEqual";

export const runtime = "nodejs";

/**
 * "Open checkout now" (admin; basic auth + lockout in middleware). A browser re-sends
 * basic-auth credentials on cross-site form posts, so this also requires a
 * same-origin request and a typed confirmation, which a forged form can't supply.
 */
export async function POST(req: Request) {
  const url = new URL(req.url);
  const origin = req.headers.get("origin");
  const site = req.headers.get("sec-fetch-site");
  if ((origin && origin !== url.origin) || (site && site !== "same-origin" && site !== "none")) {
    return NextResponse.json({ error: "Cross-site request refused." }, { status: 403 });
  }
  const f = new URLSearchParams((await req.text()).slice(0, 512));
  if (f.get("confirm") !== "OPEN") return NextResponse.redirect(`${url.origin}/admin?launch=confirm#launch`, 303);
  const by = parseBasicAuth(req.headers.get("authorization"))?.user ?? "admin";
  await openCheckoutNow(await getStore(), by);
  return NextResponse.redirect(`${url.origin}/admin?launch=opened#launch`, 303);
}
