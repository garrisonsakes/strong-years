/**
 * Round 8 (AUDIT_FINAL §7): admin login lockout that rotating X-Forwarded-For can't
 * dodge. Failures are counted per trusted client IP AND per username, and every
 * failure past the free ones doubles the wait (1 min, 2, 4 … capped at 1 hour).
 * While a key is locked, even a correct password is refused, so guessing stops.
 * The real admin still gets in after the wait, or right away from another network
 * if only the IP key is locked; ADMIN_TOTP_SECRET adds a second factor so a stolen
 * password alone is useless. Edge-safe (Web Crypto). Per instance: multi-instance
 * hosting should also keep Vercel's firewall / WAF rate rule on /admin.
 */
export const FREE_ATTEMPTS = 5;
export const BASE_LOCK_MS = 60_000;
export const MAX_LOCK_MS = 60 * 60_000;
const FORGET_AFTER_MS = 24 * 60 * 60_000;

interface Entry {
  fails: number;
  lockedUntil: number;
  lastFail: number;
}

export class AdminGuard {
  private entries = new Map<string, Entry>();

  static keys(ip: string, username: string): string[] {
    return [`ip:${ip}`, `user:${username.trim().toLowerCase().slice(0, 64) || "(blank)"}`];
  }

  private entry(key: string, now: number): Entry | undefined {
    const e = this.entries.get(key);
    if (e && now - e.lastFail > FORGET_AFTER_MS && now >= e.lockedUntil) {
      this.entries.delete(key);
      return undefined;
    }
    return e;
  }

  /** Seconds until every key is unlocked (0 = not locked). */
  retryAfter(keys: string[], now = Date.now()): number {
    let until = 0;
    for (const k of keys) until = Math.max(until, this.entry(k, now)?.lockedUntil ?? 0);
    return until > now ? Math.ceil((until - now) / 1000) : 0;
  }

  fail(keys: string[], now = Date.now()): void {
    for (const k of keys) {
      const e = this.entry(k, now) ?? { fails: 0, lockedUntil: 0, lastFail: 0 };
      e.fails += 1;
      e.lastFail = now;
      if (e.fails >= FREE_ATTEMPTS) e.lockedUntil = now + Math.min(MAX_LOCK_MS, BASE_LOCK_MS * 2 ** (e.fails - FREE_ATTEMPTS));
      this.entries.set(k, e);
    }
  }

  success(keys: string[]): void {
    for (const k of keys) this.entries.delete(k);
  }
}

/* ------------------------------------------------------------------ TOTP (RFC 6238) */

function base32Decode(s: string): Uint8Array {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  const clean = s.toUpperCase().replace(/[\s=-]/g, "");
  let bits = 0;
  let value = 0;
  const out: number[] = [];
  for (const ch of clean) {
    const idx = alphabet.indexOf(ch);
    if (idx < 0) throw new Error("invalid base32");
    value = (value << 5) | idx;
    bits += 5;
    if (bits >= 8) {
      out.push((value >>> (bits - 8)) & 0xff);
      bits -= 8;
    }
  }
  return new Uint8Array(out);
}

export async function totpAt(secret: Uint8Array, counter: number, digits = 6): Promise<string> {
  const msg = new Uint8Array(8);
  let c = counter;
  for (let i = 7; i >= 0; i--) {
    msg[i] = c & 0xff;
    c = Math.floor(c / 256);
  }
  const key = await crypto.subtle.importKey("raw", secret as BufferSource, { name: "HMAC", hash: "SHA-1" }, false, ["sign"]);
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", key, msg as BufferSource));
  const off = mac[mac.length - 1]! & 0x0f;
  const bin = ((mac[off]! & 0x7f) << 24) | (mac[off + 1]! << 16) | (mac[off + 2]! << 8) | mac[off + 3]!;
  return String(bin % 10 ** digits).padStart(digits, "0");
}

/** Accepts the current 30-second code or one step either side (clock drift). */
export async function verifyTotp(base32Secret: string, code: string, now = Date.now()): Promise<boolean> {
  if (!/^\d{6}$/.test(code)) return false;
  let secret: Uint8Array;
  try {
    secret = base32Decode(base32Secret);
  } catch {
    return false;
  }
  if (secret.length < 10) return false;
  const step = Math.floor(now / 1000 / 30);
  let ok = false;
  for (const d of [-1, 0, 1]) if ((await totpAt(secret, step + d)) === code) ok = true;
  return ok;
}

/**
 * With ADMIN_TOTP_SECRET set, the browser's password box takes the password
 * followed by the 6-digit code from the authenticator app ("hunter2 123456" or
 * "hunter2123456").
 */
export function splitPasswordAndCode(raw: string): { password: string; code: string } {
  const m = raw.match(/^(.*?)\s?(\d{6})$/s);
  return m ? { password: m[1]!, code: m[2]! } : { password: raw, code: "" };
}

export function base32Encode(bytes: Uint8Array): string {
  const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  let bits = 0;
  let value = 0;
  let out = "";
  for (const b of bytes) {
    value = (value << 8) | b;
    bits += 8;
    while (bits >= 5) {
      out += alphabet[(value >>> (bits - 5)) & 31];
      bits -= 5;
    }
  }
  if (bits > 0) out += alphabet[(value << (5 - bits)) & 31];
  return out;
}

/**
 * Round 6 (launch eve): browsers re-send HTTP Basic credentials on cross-site form
 * posts, so every state-changing admin route must refuse a request whose Origin or
 * Sec-Fetch-Site says it came from another site. A forged page can neither set those
 * headers to same-origin nor remove them. Returns a reason string when the request
 * must be refused, else null.
 */
export function crossSiteReason(req: Request): string | null {
  const url = new URL(req.url);
  const origin = req.headers.get("origin");
  const site = req.headers.get("sec-fetch-site");
  if (origin && origin !== url.origin) return `origin ${origin} is not ${url.origin}`;
  if (site && site !== "same-origin" && site !== "none") return `sec-fetch-site ${site}`;
  return null;
}
