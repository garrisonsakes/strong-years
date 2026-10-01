import "server-only";
import { cookies, headers } from "next/headers";
import { ARM_COOKIE, ATTR_COOKIE, LAST_TOUCH_COOKIE, decodeAttribution, decodeTouch, mergeTouches } from "./analytics/attribution";
import { getStore } from "./db";
import type { Arm, Attribution } from "./db/types";
import { foundingTaken } from "./founding";
import { trustedClientIp } from "./clientIp";
import { foundingSpots } from "./pricing";
import { blitz, env, offerRules, prices } from "./config";
import { verifyVid } from "./vid";
import { hitLocal } from "./rateLimit";
import { trackInternal } from "./analytics/meta";
import { VID_COOKIE, assignArm, resolveFoundingOffer, testCell, type FoundingOffer } from "./blitz";

/** Arm A ($1 trial) only exists when the trial arm is enabled; blitz mode is all founding (B). */
export async function getArm(): Promise<Arm> {
  if (!blitz.trialArmEnabled) return "B";
  // QA override (?arm=A|B sets this cookie); otherwise a sticky hash of the signed visitor id.
  const forced = (await cookies()).get(ARM_COOKIE)?.value;
  if (forced === "A" || forced === "B") return forced;
  const vid = await getVisitorId();
  return vid ? assignArm(vid, offerRules.armBShare) : "B";
}

/** The verified visitor id (L5). A forged or unsigned cookie counts as no id. */
export async function getVisitorId(): Promise<string | null> {
  let secret: string;
  try {
    secret = env.sessionSecret;
  } catch {
    return null;
  }
  return verifyVid((await cookies()).get(VID_COOKIE)?.value, secret);
}

/** L5: price-test exposure logged on the server when the price renders (once a day per visitor). */
export async function logPriceExposure(): Promise<void> {
  const vid = await getVisitorId();
  if (!vid || !hitLocal(`exposure:${vid}`, { max: 1, windowMs: 24 * 60 * 60_000 })) return;
  const offer = await getFoundingOffer();
  const arm = await getArm();
  await trackInternal("price_cell_exposure", { cell: testCell(arm, offer, prices.monthly), arm, vid, source: "server" });
}

/** The founding offer this visitor sees: sticky price cell + real cohort state from the DB. */
export async function getFoundingOffer(): Promise<FoundingOffer> {
  const store = await getStore();
  return resolveFoundingOffer({
    visitorId: await getVisitorId(),
    claimed: await foundingTaken(store),
    cap: offerRules.foundingCap,
    testOn: blitz.enabled && blitz.priceTestOn,
    cells: blitz.priceCells,
    defaultCents: blitz.enabled ? blitz.defaultPriceCents : prices.founding,
    standardCents: blitz.enabled ? blitz.standardPriceCents : prices.founding,
  });
}

export const OPTOUT_COOKIE = "sy_optout";

/** "Do Not Sell or Share" (our cookie) or the browser's Global Privacy Control signal. */
export async function adsOptedOut(): Promise<boolean> {
  const jar = await cookies();
  if (jar.get(OPTOUT_COOKIE)?.value === "1") return true;
  return (await headers()).get("sec-gpc") === "1";
}

/** First touch (sy_attr) plus the latest touch (sy_lt), both re-validated. */
export async function getAttribution(): Promise<Attribution | null> {
  const jar = await cookies();
  const a = mergeTouches(decodeAttribution(jar.get(ATTR_COOKIE)?.value), decodeTouch(jar.get(LAST_TOUCH_COOKIE)?.value));
  if (await adsOptedOut()) return { ...(a ?? {}), ad_opt_out: true };
  return a;
}

export async function getFoundingSpots() {
  const store = await getStore();
  return foundingSpots(await foundingTaken(store));
}

export async function clientMeta() {
  const h = await headers();
  return {
    // Round 8: only an IP a trusted proxy wrote (consent log, Meta CAPI).
    ip: ((ip) => (ip === "unknown" ? null : ip))(trustedClientIp(h)),
    userAgent: h.get("user-agent"),
  };
}
