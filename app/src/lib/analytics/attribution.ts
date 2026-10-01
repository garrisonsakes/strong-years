import type { Attribution, TouchPoint } from "../db/types";

export const ATTR_COOKIE = "sy_attr";
/** Last attributed touch (overwritten on every attributed visit). */
export const LAST_TOUCH_COOKIE = "sy_lt";
export const ARM_COOKIE = "sy_arm";

/**
 * Post-level attribution for the organic launch. Bio links and DM links carry:
 *
 *   ?platform=ig&page=changyin.strong&post_id=C8xYz12AbC&keyword=JOIN&character=chang
 *    &utm_source=ig&utm_medium=bio&utm_campaign=prelaunch
 *
 * Every field is validated and length-limited; anything that doesn't fit is dropped
 * (never truncated into something that looks valid). It's first-party reporting only:
 * nothing here ever changes a price (the price cell comes from the signed visitor id).
 */
export const PLATFORMS = ["ig", "tt", "yt", "fb", "th", "email", "dm", "web", "other"] as const;
const PLATFORM_ALIASES: Record<string, (typeof PLATFORMS)[number]> = {
  instagram: "ig",
  tiktok: "tt",
  youtube: "yt",
  facebook: "fb",
  threads: "th",
};

const UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"] as const;
const POST_KEYS = ["platform", "page", "post_id", "keyword", "character"] as const;
/** Max length of any single raw query value we even look at. */
export const MAX_PARAM_LENGTH = 200;
/** Cookies we accept back (an attacker can write anything into their own cookie). */
const MAX_COOKIE_LENGTH = 2048;

// Printable ASCII only, no quotes/angle brackets/control characters.
const SAFE_TEXT = /^[A-Za-z0-9 _.,:+@~()!*'/-]{1,100}$/;

function utmValue(v: string): string | undefined {
  const t = v.trim();
  return SAFE_TEXT.test(t) ? t : undefined;
}

export function cleanPlatform(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim().toLowerCase();
  if (t.length > 20) return undefined;
  const p = PLATFORM_ALIASES[t] ?? t;
  return (PLATFORMS as readonly string[]).includes(p) ? p : undefined;
}

export function cleanPage(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim().replace(/^@/, "").toLowerCase();
  return /^[a-z0-9_.]{1,64}$/.test(t) ? t : undefined;
}

export function cleanPostId(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim();
  return /^[A-Za-z0-9_-]{1,64}$/.test(t) ? t : undefined;
}

export function cleanKeyword(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim().toUpperCase();
  return /^[A-Z0-9]{2,24}$/.test(t) ? t : undefined;
}

export function cleanCharacter(v: unknown): "chang" | "sun" | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim().toLowerCase();
  return t === "chang" || t === "sun" ? t : undefined;
}

function cleanMcId(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim();
  return /^[A-Za-z0-9_-]{1,64}$/.test(t) ? t : undefined;
}

function cleanFbclid(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  const t = v.trim();
  return /^[A-Za-z0-9_-]{1,200}$/.test(t) ? t : undefined;
}

function cleanPath(v: unknown): string | undefined {
  if (typeof v !== "string") return undefined;
  return /^\/[A-Za-z0-9/_.-]{0,120}$/.test(v) ? v : undefined;
}

function cleanIso(v: unknown): string | undefined {
  if (typeof v !== "string" || v.length > 40) return undefined;
  return Number.isNaN(Date.parse(v)) ? undefined : new Date(v).toISOString();
}

/** Validates a touch from any untrusted source (query string, cookie, request body). */
export function sanitizeTouch(raw: Record<string, unknown> | null | undefined): TouchPoint | null {
  if (!raw || typeof raw !== "object") return null;
  const out: TouchPoint = {};
  for (const k of UTM_KEYS) {
    const v = raw[k];
    if (typeof v === "string" && v.length <= MAX_PARAM_LENGTH) {
      const c = utmValue(v);
      if (c) out[k] = c;
    }
  }
  const platform = cleanPlatform(raw.platform);
  if (platform) out.platform = platform;
  const page = cleanPage(raw.page);
  if (page) out.page = page;
  const postId = cleanPostId(raw.post_id);
  if (postId) out.post_id = postId;
  const keyword = cleanKeyword(raw.keyword);
  if (keyword) out.keyword = keyword;
  const character = cleanCharacter(raw.character);
  if (character) out.character = character;
  const mc = cleanMcId(raw.mc_id);
  if (mc) out.mc_id = mc;
  if (Object.keys(out).length === 0) return null;
  const path = cleanPath(raw.landing_path);
  if (path) out.landing_path = path;
  const at = cleanIso(raw.at);
  if (at) out.at = at;
  return out;
}

/** Validates a stored attribution record (cookie or body), including its nested last touch. */
export function sanitizeAttribution(raw: unknown): Attribution | null {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return null;
  const r = raw as Record<string, unknown>;
  const touch = sanitizeTouch(r) ?? {};
  const out: Attribution = {};
  for (const k of UTM_KEYS) if (touch[k]) out[k] = touch[k];
  for (const k of POST_KEYS) if (touch[k]) (out as Record<string, unknown>)[k] = touch[k];
  if (touch.mc_id) out.mc_id = touch.mc_id;
  const fbclid = cleanFbclid(r.fbclid);
  if (fbclid) out.fbclid = fbclid;
  const path = cleanPath(r.landing_path);
  if (path) out.landing_path = path;
  const seen = cleanIso(r.first_seen_at);
  if (seen) out.first_seen_at = seen;
  if (r.ad_opt_out === true) out.ad_opt_out = true;
  const lt = r.last_touch && typeof r.last_touch === "object" ? sanitizeTouch(r.last_touch as Record<string, unknown>) : null;
  if (lt) out.last_touch = lt;
  return Object.keys(out).length ? out : null;
}

/** Everything attribution-related a URL carries, validated. Null if nothing usable. */
function urlFields(url: URL): Record<string, string> {
  const raw: Record<string, string> = {};
  for (const k of [...UTM_KEYS, ...POST_KEYS, "mc_id", "fbclid"]) {
    const v = url.searchParams.get(k);
    if (v !== null && v.length <= MAX_PARAM_LENGTH) raw[k] = v;
  }
  return raw;
}

/** First touch: UTM params, post-level fields, ManyChat mc_id and fbclid. Null if none are valid. */
export function attributionFromUrl(url: URL, now = new Date()): Attribution | null {
  const raw = urlFields(url);
  const a = sanitizeAttribution(raw);
  if (!a) return null;
  a.landing_path = cleanPath(url.pathname) ?? "/";
  a.first_seen_at = now.toISOString();
  return a;
}

/** Last touch from a URL (no fbclid: that's a click id, first-touch only). */
export function touchFromUrl(url: URL, now = new Date()): TouchPoint | null {
  const t = sanitizeTouch(urlFields(url));
  if (!t) return null;
  t.landing_path = cleanPath(url.pathname) ?? "/";
  t.at = now.toISOString();
  return t;
}

export function encodeAttribution(a: Attribution | TouchPoint): string {
  return encodeURIComponent(JSON.stringify(a));
}

function decodeJson(raw: string | undefined | null): unknown {
  if (!raw || raw.length > MAX_COOKIE_LENGTH) return null;
  try {
    return JSON.parse(decodeURIComponent(raw));
  } catch {
    return null;
  }
}

/** Cookies are client-controlled: everything is re-validated on the way back in. */
export function decodeAttribution(raw: string | undefined | null): Attribution | null {
  return sanitizeAttribution(decodeJson(raw));
}

export function decodeTouch(raw: string | undefined | null): TouchPoint | null {
  const v = decodeJson(raw);
  return v && typeof v === "object" ? sanitizeTouch(v as Record<string, unknown>) : null;
}

/** First touch from sy_attr plus the latest touch from sy_lt. */
export function mergeTouches(first: Attribution | null, last: TouchPoint | null): Attribution | null {
  if (!first && !last) return null;
  const out: Attribution = { ...(first ?? {}) };
  if (last) out.last_touch = last;
  return out;
}

/** The touch a record's first-touch fields describe (for comparing and reporting). */
export function firstTouchOf(a: Attribution | null | undefined): TouchPoint | null {
  if (!a) return null;
  return sanitizeTouch({ ...a, at: a.first_seen_at });
}

/** Post-level credit for reporting. Last touch falls back to first touch when there was only one visit. */
export function postKey(a: Attribution | null | undefined, touch: "first" | "last"): { post_id: string; platform: string | null; page: string | null; character: string | null; keyword: string | null } | null {
  if (!a) return null;
  const t: TouchPoint | Attribution | undefined = touch === "last" ? (a.last_touch ?? a) : a;
  if (!t?.post_id) return null;
  return { post_id: t.post_id, platform: t.platform ?? null, page: t.page ?? null, character: t.character ?? null, keyword: t.keyword ?? null };
}

/** mc_id passthrough: append the ManyChat id to internal links so DM subscribers match purchases. */
export function withMcId(href: string, mcId: string | undefined | null): string {
  if (!mcId) return href;
  const [path, query = ""] = href.split("?");
  const params = new URLSearchParams(query);
  params.set("mc_id", mcId);
  return `${path}?${params.toString()}`;
}
