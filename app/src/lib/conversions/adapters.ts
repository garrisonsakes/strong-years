/**
 * Meta Conversions API and TikTok Events API adapters. Pure builders plus one
 * send function each. Every outbound event carries exactly:
 *   event name (a fixed standard name), event id (dedup), time, a Meta-safe page URL
 *   (lib/analytics/meta.ts safeSourceUrl: quiz and condition-word paths are aliased),
 *   the SHA-256 of the normalised email, and optionally a currency value and an
 *   offer code with no condition word in it.
 * Never: phone, IP, user agent, click ids, quiz answers, health information, UTM
 * values, post ids or free text.
 * Disabled (no network at all) until the platform's env keys are set.
 */
import { containsConditionWord, safeSourceUrl, sha256 } from "../analytics/meta";
import type { ConversionPlatform } from "../db/types";

export const CONVERSION_EVENTS = ["Lead", "CompleteRegistration", "StartTrial", "Purchase", "Subscribe"] as const;
export type ConversionEvent = (typeof CONVERSION_EVENTS)[number];

/** TikTok's standard event names for ours. */
export const TIKTOK_EVENT_NAMES: Record<ConversionEvent, string> = {
  Lead: "Lead",
  CompleteRegistration: "CompleteRegistration",
  StartTrial: "StartTrial",
  Purchase: "CompletePayment",
  Subscribe: "Subscribe",
};

export interface NeutralEvent {
  name: ConversionEvent;
  eventId: string;
  sourcePath: string;
  email: string;
  valueCents?: number;
  contentName?: string;
  timeMs: number;
}

export class ConversionSafetyError extends Error {}

const EVENT_ID = /^[A-Za-z0-9_-]{1,100}$/;
const OFFER_CODE = /^[a-z0-9_]{1,32}$/;

export function emailHash(email: string): string {
  return sha256(email.normalize("NFKC").trim().toLowerCase());
}

function common(e: NeutralEvent, siteUrl: string) {
  if (!CONVERSION_EVENTS.includes(e.name)) throw new ConversionSafetyError(`event not allowed: ${e.name}`);
  if (!EVENT_ID.test(e.eventId)) throw new ConversionSafetyError("bad event id");
  const url = safeSourceUrl(siteUrl, e.sourcePath);
  if (containsConditionWord(new URL(url).pathname)) throw new ConversionSafetyError("condition-revealing URL");
  const content = e.contentName && OFFER_CODE.test(e.contentName) && !containsConditionWord(e.contentName) ? e.contentName : undefined;
  const value = e.valueCents !== undefined && Number.isFinite(e.valueCents) && e.valueCents >= 0 ? Math.round(e.valueCents) / 100 : undefined;
  return { url, content, value, time: Math.floor(e.timeMs / 1000), hash: emailHash(e.email) };
}

export function buildMetaEvent(e: NeutralEvent, siteUrl: string) {
  const c = common(e, siteUrl);
  const custom: Record<string, string | number> = { currency: "USD" };
  if (c.value !== undefined) custom.value = c.value;
  if (c.content) custom.content_name = c.content;
  return {
    event_name: e.name,
    event_time: c.time,
    event_id: e.eventId,
    action_source: "website",
    event_source_url: c.url,
    user_data: { em: [c.hash] },
    custom_data: custom,
  };
}

export function buildTikTokEvent(e: NeutralEvent, siteUrl: string) {
  const c = common(e, siteUrl);
  const properties: Record<string, string | number> = { currency: "USD" };
  if (c.value !== undefined) properties.value = c.value;
  if (c.content) properties.content_id = c.content;
  return {
    event: TIKTOK_EVENT_NAMES[e.name],
    event_time: c.time,
    event_id: e.eventId,
    user: { email: c.hash },
    page: { url: c.url },
    properties,
  };
}

type Env = Record<string, string | undefined>;

export function platformEnabled(p: ConversionPlatform, env: Env = process.env): boolean {
  if (p === "meta") return Boolean(env.META_PIXEL_ID && env.META_CAPI_TOKEN);
  return Boolean(env.TIKTOK_PIXEL_CODE && env.TIKTOK_ACCESS_TOKEN);
}

export function enabledPlatforms(env: Env = process.env): ConversionPlatform[] {
  return (["meta", "tiktok"] as const).filter((p) => platformEnabled(p, env));
}

export interface SendResult {
  ok: boolean;
  error?: string;
}

/** POSTs one stored event. Tokens go in the body/header, never in the URL (URLs end up in logs). */
export async function sendToPlatform(p: ConversionPlatform, event: Record<string, unknown>, env: Env = process.env): Promise<SendResult> {
  try {
    if (p === "meta") {
      const body: Record<string, unknown> = { data: [event], access_token: env.META_CAPI_TOKEN };
      if (env.META_TEST_EVENT_CODE) body.test_event_code = env.META_TEST_EVENT_CODE;
      const res = await fetch(`https://graph.facebook.com/v21.0/${encodeURIComponent(env.META_PIXEL_ID ?? "")}/events`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(5000),
      });
      return res.ok ? { ok: true } : { ok: false, error: `meta ${res.status}` };
    }
    const body: Record<string, unknown> = { event_source: "web", event_source_id: env.TIKTOK_PIXEL_CODE, data: [event] };
    if (env.TIKTOK_TEST_EVENT_CODE) body.test_event_code = env.TIKTOK_TEST_EVENT_CODE;
    const res = await fetch("https://business-api.tiktok.com/open_api/v1.3/event/track/", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Access-Token": env.TIKTOK_ACCESS_TOKEN ?? "" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return { ok: false, error: `tiktok ${res.status}` };
    // TikTok answers 200 with a non-zero code for rejected events.
    const data = (await res.json().catch(() => ({}))) as { code?: number };
    return data.code === undefined || data.code === 0 ? { ok: true } : { ok: false, error: `tiktok code ${data.code}` };
  } catch (err) {
    return { ok: false, error: (err as Error).name || "network" };
  }
}
