/**
 * Meta Conversions API (server-side) with the OFFER.md 2.6 / FUNNEL.md 1 rules baked in:
 *  - only standard event names: Lead, CompleteRegistration, StartTrial, Purchase, Subscribe
 *  - no condition words anywhere in the event name, URL or custom data
 *  - quiz answers, profile names and health details are never sent
 *  - email/phone are SHA-256 hashed as Meta requires
 * Outbound events go through lib/conversions (opt-in consent, hashed email only,
 * outbox with event_id dedup). With no platform keys, events are only written to
 * analytics_events.
 */
import { createHash } from "node:crypto";
import { getStore } from "../db";
import type { Attribution } from "../db/types";

export const META_EVENTS = ["Lead", "CompleteRegistration", "StartTrial", "Purchase", "Subscribe"] as const;
export type MetaEventName = (typeof META_EVENTS)[number];

/** Words that would get the ad account classified as health & wellness. */
export const CONDITION_WORDS = [
  "pain", "arthritis", "osteo", "diabet", "blood", "pressure", "hypertension", "cholesterol", "heart",
  "knee", "back", "hip", "joint", "gut", "bloat", "constipat", "ibs", "reflux", "digest", "sleep", "insomnia",
  "anxiety", "depress", "dementia", "memory", "menopaus", "prostate", "fall", "balance", "dizz", "sarcopenia",
  "cancer", "stroke", "weight", "obes", "sore", "stiff", "injur", "rehab", "therapy", "symptom", "disease",
  "condition", "medic", "doctor", "diagnos", "health", "red_flag", "redflag", "safe_mode",
];

export function containsConditionWord(value: string): boolean {
  const v = value.toLowerCase();
  return CONDITION_WORDS.some((w) => v.includes(w));
}

/** Public paths → Meta-safe aliases (FUNNEL.md 1: `/s/ln1`, not `/knee-pain-lesson`). */
const SAFE_PATHS: [RegExp, string][] = [
  [/^\/quiz\/strength-age(\/.*)?$/, "/q/a"],
  [/^\/quiz\/gut-energy(\/.*)?$/, "/q/b"],
  [/^\/checkout\/.*$/, "/checkout"],
  [/^\/upsell\/.*$/, "/upsell"],
  [/^\/gift.*$/, "/gift"],
  [/^\/start.*$/, "/start"],
  [/^\/waitlist.*$/, "/waitlist"],
  [/^\/join.*$/, "/join"],
];

export function safeSourceUrl(siteUrl: string, path: string): string {
  const clean = path.split("?")[0] ?? "/";
  for (const [re, alias] of SAFE_PATHS) if (re.test(clean)) return `${siteUrl}${alias}`;
  return containsConditionWord(clean) ? `${siteUrl}/` : `${siteUrl}${clean}`;
}

export function sha256(v: string): string {
  return createHash("sha256").update(v.trim().toLowerCase()).digest("hex");
}

export interface MetaEventInput {
  name: MetaEventName;
  eventId: string;
  sourcePath: string;
  email?: string | null;
  phone?: string | null;
  valueCents?: number;
  contentName?: string; // must be an offer code, e.g. "trial"
  attribution?: Attribution | null;
  memberId?: string | null;
  leadId?: string | null;
  clientIp?: string | null;
  userAgent?: string | null;
}

export interface MetaPayload {
  event_name: MetaEventName;
  event_time: number;
  event_id: string;
  action_source: "website";
  event_source_url: string;
  user_data: Record<string, string | string[]>;
  custom_data: Record<string, string | number>;
}

export class MetaSafetyError extends Error {}

export function buildMetaPayload(input: MetaEventInput, siteUrl: string, now = Date.now()): MetaPayload {
  if (!META_EVENTS.includes(input.name)) throw new MetaSafetyError(`event name not allowed: ${input.name}`);
  const custom: Record<string, string | number> = { currency: "USD" };
  if (input.valueCents !== undefined) custom.value = Math.round(input.valueCents) / 100;
  if (input.contentName) custom.content_name = input.contentName;
  if (input.attribution?.utm_campaign) custom.utm_campaign = input.attribution.utm_campaign;
  if (input.attribution?.utm_source) custom.utm_source = input.attribution.utm_source;
  if (input.attribution?.mc_id) custom.mc_id = input.attribution.mc_id;

  // Drop (never forward) any custom field that carries a condition word, e.g. a
  // campaign named "knee-promo". The event itself still goes through.
  for (const [k, v] of Object.entries(custom)) {
    if (typeof v === "string" && containsConditionWord(v)) delete custom[k];
  }
  if (input.contentName && !custom.content_name) {
    throw new MetaSafetyError("content_name must be an offer code without condition words");
  }
  const user: Record<string, string | string[]> = {};
  if (input.email) user.em = [sha256(input.email)];
  if (input.phone) user.ph = [sha256(input.phone.replace(/[^0-9]/g, ""))];
  if (input.clientIp) user.client_ip_address = input.clientIp;
  if (input.userAgent) user.client_user_agent = input.userAgent;
  if (input.attribution?.fbclid) user.fbc = `fb.1.${now}.${input.attribution.fbclid}`;
  if (input.attribution?.mc_id) user.external_id = [sha256(`mc:${input.attribution.mc_id}`)];

  const url = safeSourceUrl(siteUrl, input.sourcePath);
  return {
    event_name: input.name,
    event_time: Math.floor(now / 1000),
    event_id: input.eventId,
    action_source: "website",
    event_source_url: url,
    user_data: user,
    custom_data: custom,
  };
}

/**
 * Records a conversion: always a local analytics row (no identifiers, nothing
 * health-related), and, only with ad-measurement consent, a hashed-email-only
 * event to each enabled ad platform through the conversion outbox
 * (lib/conversions). `sent_to_meta` says whether Meta accepted it in this call.
 */
export async function trackMetaEvent(input: MetaEventInput & { healthContext?: boolean }, siteUrl: string) {
  const store = await getStore();
  let payload: MetaPayload;
  try {
    payload = buildMetaPayload(input, siteUrl);
  } catch (err) {
    console.error("meta event blocked", err);
    return null;
  }
  let sent = false;
  try {
    const { recordConversion } = await import("../conversions");
    const r = await recordConversion(
      store,
      {
        name: input.name,
        eventId: input.eventId,
        sourcePath: input.sourcePath,
        email: input.email,
        valueCents: input.valueCents,
        contentName: input.contentName,
        memberId: input.memberId,
        attribution: input.attribution,
        healthContext: input.healthContext,
      },
      siteUrl,
    );
    sent = r.delivered.includes("meta");
  } catch (err) {
    console.error("conversion outbox failed", err);
  }
  // Store without the hashed identifiers; nothing health-related is ever in here.
  return store.insert("analytics_events", {
    name: payload.event_name,
    member_id: input.memberId ?? null,
    lead_id: input.leadId ?? null,
    payload: { event_id: payload.event_id, event_source_url: payload.event_source_url, custom_data: payload.custom_data },
    sent_to_meta: sent,
  });
}

/** First-party funnel step events (never sent to Meta). Names use letters/numbers only. */
export async function trackInternal(name: string, data: Record<string, unknown> = {}, ids: { memberId?: string | null; leadId?: string | null } = {}) {
  if (!/^[a-z0-9_]+$/.test(name)) throw new Error(`bad internal event name ${name}`);
  const store = await getStore();
  return store.insert("analytics_events", {
    name,
    member_id: ids.memberId ?? null,
    lead_id: ids.leadId ?? null,
    payload: data,
    sent_to_meta: false,
  });
}
