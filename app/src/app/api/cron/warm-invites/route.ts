import { NextResponse } from "next/server";
import { env } from "@/lib/config";
import { getStore } from "@/lib/db";
import { safeEqual } from "@/lib/safeEqual";
import { sendWarmInvites } from "@/lib/warmImport";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Hourly (vercel.json): the double opt-in email for warm-list imports, at most
 * WARM_INVITE_BATCH (default 100) per run so a big import never spikes the sending
 * domain. Claimed per row first, so overlapping runs never double-send.
 */
export async function GET(req: Request) {
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${env.cronSecret}`)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const result = await sendWarmInvites(await getStore());
  return NextResponse.json({ ok: true, ...result }, { headers: { "Cache-Control": "no-store" } });
}
