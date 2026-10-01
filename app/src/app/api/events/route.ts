import { NextResponse } from "next/server";
import { trackInternal } from "@/lib/analytics/meta";
import { logPriceExposure } from "@/lib/request";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";

const ALLOWED = new Set(["q_a_start", "q_a_step", "q_b_start", "q_b_step", "q_b_stop", "session_start", "session_done", "price_cell_exposure"]);

/** First-party funnel step events. Never forwarded to Meta. */
export async function POST(req: Request) {
  // M5: first-party events are capped per IP (exposure spam can't skew the price test).
  if (!(await hit(`events:ip:${clientIp(req)}`, LIMITS.eventsPerIp))) return NextResponse.json({ ok: false }, { status: 429 });
  try {
    const body = (await req.json()) as { name?: string; data?: Record<string, unknown> };
    if (!body.name || !ALLOWED.has(body.name)) return NextResponse.json({ ok: false }, { status: 400 });
    if (body.name === "price_cell_exposure") {
      // Deduplicated per signed visitor id per day (L5).
      await logPriceExposure();
      return NextResponse.json({ ok: true });
    }
    const n = typeof body.data?.n === "number" ? body.data.n : undefined;
    await trackInternal(body.name, n === undefined ? {} : { n });
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: false }, { status: 400 });
  }
}
