/**
 * Signed, stateless tokens for the waitlist (HMAC-SHA256 with SESSION_SECRET,
 * domain-separated per purpose so one kind can never be replayed as another):
 *
 *   form  : when the signup form was rendered (the timing check against bots)
 *   access: a confirmed waitlister's own pages (starter session, bonus PDF, push)
 *   unsub : one-click leave-the-list link in every email (no expiry, by design)
 *
 * The email-confirmation token is different: random, stored only as a hash, single
 * use (lib/waitlist.ts), so a replayed confirmation link does nothing.
 */
import { createHmac, timingSafeEqual } from "node:crypto";
import { env } from "./config";

type Purpose = "form" | "access" | "unsub";

function mac(purpose: Purpose, body: string, secret: string): string {
  return createHmac("sha256", `wl-${purpose}:${secret}`).update(body).digest("base64url").slice(0, 32);
}

function eq(a: string, b: string): boolean {
  const x = Buffer.from(a);
  const y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

function secret(): string {
  return env.sessionSecret;
}

/* ---------- form timing ---------- */

export function signFormTime(now = Date.now(), s = secret()): string {
  const body = String(now);
  return `${body}.${mac("form", body, s)}`;
}

export const FORM_MAX_AGE_MS = 24 * 3600_000;

export function minFillMs(): number {
  const raw = process.env.WAITLIST_MIN_FILL_MS;
  if (raw === undefined || raw.trim() === "") return 3000;
  const n = Number(raw);
  return Number.isFinite(n) && n >= 0 ? n : 3000;
}

/** True only for a token we signed, at least `minMs` old and at most a day old. */
export function formTimeOk(token: string | null | undefined, now = Date.now(), minMs = minFillMs(), s = secret()): boolean {
  if (!token || token.length > 80) return false;
  const [body, sig] = token.split(".");
  if (!body || !sig || !/^\d{10,16}$/.test(body)) return false;
  if (!eq(sig, mac("form", body, s))) return false;
  const age = now - Number(body);
  return age >= minMs && age <= FORM_MAX_AGE_MS;
}

/* ---------- access + unsubscribe ---------- */

export const ACCESS_TTL_MS = 60 * 86_400_000;

export function signAccess(waitlistId: string, now = Date.now(), s = secret()): string {
  const body = `${waitlistId}.${Math.floor((now + ACCESS_TTL_MS) / 1000)}`;
  return `${body}.${mac("access", body, s)}`;
}

export function verifyAccess(token: string | null | undefined, now = Date.now(), s = secret()): string | null {
  if (!token || token.length > 160) return null;
  const parts = token.split(".");
  if (parts.length !== 3) return null;
  const [id, exp, sig] = parts as [string, string, string];
  if (!/^[0-9a-f-]{36}$/.test(id) || !/^\d{9,11}$/.test(exp)) return null;
  if (!eq(sig, mac("access", `${id}.${exp}`, s))) return null;
  return Number(exp) * 1000 > now ? id : null;
}

export function signUnsub(waitlistId: string, s = secret()): string {
  return `${waitlistId}.${mac("unsub", waitlistId, s)}`;
}

export function verifyUnsub(token: string | null | undefined, s = secret()): string | null {
  if (!token || token.length > 120) return null;
  const [id, sig] = token.split(".");
  if (!id || !sig || !/^[0-9a-f-]{36}$/.test(id)) return null;
  return eq(sig, mac("unsub", id, s)) ? id : null;
}
