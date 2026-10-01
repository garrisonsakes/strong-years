import { NextResponse } from "next/server";
import { env } from "@/lib/config";
import { getStore } from "@/lib/db";
import { runLifecycle } from "@/lib/lifecycle/engine";
import { safeEqual } from "@/lib/safeEqual";

export const runtime = "nodejs";

/** Hourly: the lifecycle email engine (idempotent, quiet hours, 1/day cap, consent). Bearer $CRON_SECRET. */
export async function GET(req: Request) {
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${env.cronSecret}`)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  if (process.env.LIFECYCLE_ENABLED === "false") return NextResponse.json({ ok: true, disabled: true });
  return NextResponse.json({ ok: true, ...(await runLifecycle(await getStore())) });
}
