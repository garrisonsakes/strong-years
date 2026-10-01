import { NextResponse } from "next/server";
import { env } from "@/lib/config";
import { getStore } from "@/lib/db";
import { flushConversions } from "@/lib/conversions";
import { runLaunchSequence } from "@/lib/launchSequence";
import { safeEqual } from "@/lib/safeEqual";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Every 15 minutes (vercel.json): the launch sequence (no-op in prelaunch and after
 * the 72-hour window) and the conversion-event outbox retries. Safe to run twice at
 * once: every send is claimed with a unique key first.
 */
export async function GET(req: Request) {
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${env.cronSecret}`)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const store = await getStore();
  const launch = await runLaunchSequence(store);
  const conversions = await flushConversions(store);
  return NextResponse.json({ ok: true, launch, conversions }, { headers: { "Cache-Control": "no-store" } });
}
