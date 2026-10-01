import { NextResponse } from "next/server";
import { env } from "@/lib/config";
import { getStore } from "@/lib/db";
import { runDigest } from "@/lib/digest";
import { safeEqual } from "@/lib/safeEqual";

export const runtime = "nodejs";

/** Cron at 11:00 and 12:00 UTC (07:00 ET in summer and winter); sends once per ET day. Bearer $CRON_SECRET. */
export async function GET(req: Request) {
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${env.cronSecret}`)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  return NextResponse.json(await runDigest(await getStore()));
}
