import { NextResponse } from "next/server";
import { deployConfigProblems, isDeployed } from "@/lib/deployEnv";
import { safeEqual } from "@/lib/safeEqual";

export const dynamic = "force-dynamic";

/**
 * Round 9: health check for the host / uptime monitor. On a real deploy with missing
 * or placeholder config (site URL, mailing address, sender, secrets, admin user) it
 * returns 503 so the deploy fails loudly. Which variables are wrong is only shown
 * with the cron secret (Authorization: Bearer $CRON_SECRET).
 */
export async function GET(req: Request) {
  const deployed = isDeployed();
  const problems = deployed ? deployConfigProblems() : [];
  const secret = process.env.CRON_SECRET;
  const auth = req.headers.get("authorization") ?? "";
  const detail = Boolean(secret) && safeEqual(auth, `Bearer ${secret}`);
  if (problems.length) {
    return NextResponse.json({ ok: false, deployed, problems: detail ? problems : problems.length }, { status: 503, headers: { "Cache-Control": "no-store" } });
  }
  return NextResponse.json({ ok: true, deployed }, { headers: { "Cache-Control": "no-store" } });
}
