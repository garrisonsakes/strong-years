import { NextResponse } from "next/server";
import { env, mode } from "@/lib/config";
import { getStore } from "@/lib/db";
import { runMockBillingClock, runReminders, runShopifyLapses } from "@/lib/billing/clock";
import { expireGifts } from "@/lib/gifts";
import { runDailyNudges } from "@/lib/push";
import { safeEqual } from "@/lib/safeEqual";

export const runtime = "nodejs";

/**
 * Hourly job (vercel.json). Pre-charge reminders before every charge, 30-day annual
 * notices, the yearly notice for monthly members, and gift expiry (H3, all modes).
 * In mock mode it also advances the simulated billing clock. Vercel Cron sends
 * "Authorization: Bearer $CRON_SECRET".
 */
export async function GET(req: Request) {
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${env.cronSecret}`)) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }
  const store = await getStore();
  const reminders = await runReminders(store);
  const giftsExpired = await expireGifts(store);
  const nudges = await runDailyNudges(store);
  // Shopify launch path: rows whose paid period ended with no renewal order lapse here (Round 5 audit).
  const shopifyLapsed = await runShopifyLapses(store);
  const clock = mode.mockStripe ? await runMockBillingClock(store) : null;
  return NextResponse.json({ ok: true, reminders, giftsExpired, nudges, shopifyLapsed, clock });
}
