import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { growthReport } from "@/lib/growth";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { safeEqual } from "@/lib/safeEqual";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Service-only endpoint for the growth engine: opt-ins, members and MRR per post_id,
 * first- and last-touch. Aggregates only (no personal data).
 *   Authorization: Bearer $GROWTH_API_TOKEN   (32+ characters; unset = endpoint off, 404)
 */
export async function GET(req: Request) {
  const token = process.env.GROWTH_API_TOKEN ?? "";
  if (token.length < 32) return NextResponse.json({ error: "Not found" }, { status: 404 });
  if (!(await hit(`growth:ip:${clientIp(req)}`, LIMITS.growthPerIp))) return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${token}`)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  return NextResponse.json(await growthReport(await getStore()), { headers: { "Cache-Control": "no-store" } });
}
