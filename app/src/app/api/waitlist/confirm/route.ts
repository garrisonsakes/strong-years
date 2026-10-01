import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { clientMeta } from "@/lib/request";
import { confirmWaitlist } from "@/lib/waitlist";

export const runtime = "nodejs";

/** The button on /waitlist/confirm. Single-use token; a replay lands on the same "expired" page. */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  if (!(await hit(`waitlist:confirm:${clientIp(req)}`, LIMITS.waitlistConfirmPerIp))) return NextResponse.redirect(`${base}/waitlist/confirm?error=busy`, 303);
  const raw = await req.text();
  if (raw.length > 1024) return new NextResponse("Too large", { status: 413 });
  const token = (new URLSearchParams(raw).get("token") ?? "").slice(0, 100);
  const r = await confirmWaitlist(await getStore(), token, await clientMeta());
  if (!r.ok) return NextResponse.redirect(`${base}/waitlist/confirm?error=expired`, 303);
  return NextResponse.redirect(`${base}/waitlist/confirmed?k=${encodeURIComponent(r.access)}`, 303);
}
