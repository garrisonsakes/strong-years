/**
 * Sliding-window rate limiter (AUDIT_CODE M5).
 * In-memory per server instance: good enough for one instance / the demo. With more
 * than one instance (serverless, autoscaling), each keeps its own counts, so set
 * RATE_LIMIT_KV_URL/TOKEN (Upstash Redis REST, recommended) to share them.
 */
import { rateLimitKey } from "./clientIp";

type Bucket = number[];
const g = globalThis as unknown as { __syRate?: Map<string, Bucket> };
const buckets = (g.__syRate ??= new Map());

export interface Limit {
  /** Max hits inside the window. */
  max: number;
  windowMs: number;
}

export const LIMITS = {
  leadsPerIp: { max: 10, windowMs: 60 * 60_000 },
  leadsPerEmail: { max: 3, windowMs: 60 * 60_000 },
  magicPerIp: { max: 10, windowMs: 60 * 60_000 },
  magicPerEmail: { max: 3, windowMs: 15 * 60_000 },
  chatPerMember: { max: 60, windowMs: 24 * 60 * 60_000 },
  chatBurst: { max: 8, windowMs: 60_000 },
  eventsPerIp: { max: 120, windowMs: 60 * 60_000 },
  giftRedeemPerIp: { max: 8, windowMs: 60 * 60_000 },
  checkoutPerIp: { max: 20, windowMs: 60 * 60_000 },
  adminFailuresPerIp: { max: 10, windowMs: 15 * 60_000 },
  waitlistPerIp: { max: 8, windowMs: 60 * 60_000 },
  waitlistPerEmail: { max: 3, windowMs: 60 * 60_000 },
  waitlistConfirmPerIp: { max: 20, windowMs: 60 * 60_000 },
  waitlistLinkPerIp: { max: 60, windowMs: 60 * 60_000 },
  growthPerIp: { max: 60, windowMs: 60 * 60_000 },
  loginCodePerIp: { max: 20, windowMs: 60 * 60_000 },
  loginCodePerEmail: { max: 10, windowMs: 15 * 60_000 },
} satisfies Record<string, Limit>;

function prune(b: Bucket, now: number, windowMs: number) {
  while (b.length && b[0]! <= now - windowMs) b.shift();
}

async function kvHit(key: string, limit: Limit): Promise<boolean | null> {
  const url = process.env.RATE_LIMIT_KV_URL;
  const token = process.env.RATE_LIMIT_KV_TOKEN;
  if (!url || !token) return null;
  try {
    const slot = Math.floor(Date.now() / limit.windowMs);
    const k = `rl:${key}:${slot}`;
    const res = await fetch(`${url}/pipeline`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify([["INCR", k], ["PEXPIRE", k, String(limit.windowMs)]]),
      signal: AbortSignal.timeout(800),
    });
    const data = (await res.json()) as { result: number }[];
    return (data[0]?.result ?? 0) <= limit.max;
  } catch {
    return null; // fall back to the local window
  }
}

/** Records a hit and returns true while the caller is under the limit. */
export async function hit(key: string, limit: Limit, now = Date.now()): Promise<boolean> {
  const kv = await kvHit(key, limit);
  if (kv !== null) return kv;
  return hitLocal(key, limit, now);
}

export function hitLocal(key: string, limit: Limit, now = Date.now()): boolean {
  const b = buckets.get(key) ?? [];
  prune(b, now, limit.windowMs);
  if (b.length >= limit.max) {
    buckets.set(key, b);
    return false;
  }
  b.push(now);
  buckets.set(key, b);
  return true;
}

/** Read-only check (admin lockout looks before verifying the password). */
export function isLimited(key: string, limit: Limit, now = Date.now()): boolean {
  const b = buckets.get(key) ?? [];
  prune(b, now, limit.windowMs);
  return b.length >= limit.max;
}

export function resetRateLimits() {
  buckets.clear();
}

/** Round 9: per-client key from the trusted-proxy logic (lib/clientIp.ts), never one shared bucket. */
export function clientIp(req: Request): string {
  return rateLimitKey(req.headers);
}
