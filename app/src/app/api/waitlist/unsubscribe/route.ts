import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { clientMeta } from "@/lib/request";
import { unsubscribeWaitlist } from "@/lib/waitlist";
import { verifyUnsub } from "@/lib/waitlistTokens";

export const runtime = "nodejs";

/** One click from any waitlist email (the page has one button; mail scanners don't press it). */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  if (!(await hit(`waitlist:unsub:${clientIp(req)}`, LIMITS.waitlistLinkPerIp))) return NextResponse.redirect(`${base}/waitlist/unsubscribe?error=busy`, 303);
  const raw = await req.text();
  if (raw.length > 1024) return new NextResponse("Too large", { status: 413 });
  const id = verifyUnsub(new URLSearchParams(raw).get("u"));
  if (!id) return NextResponse.redirect(`${base}/waitlist/unsubscribe?error=link`, 303);
  await unsubscribeWaitlist(await getStore(), id, await clientMeta());
  return NextResponse.redirect(`${base}/waitlist/unsubscribe?done=1`, 303);
}
