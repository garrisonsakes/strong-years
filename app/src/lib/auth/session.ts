/**
 * Signed session cookie (HMAC-SHA256 via Web Crypto, so it also runs in middleware).
 * Login is passwordless: magic links by email (FUNNEL.md 5.4 "no passwords to remember").
 */
export const SESSION_COOKIE = "sy_session";
export const SESSION_DAYS = 60;

const enc = new TextEncoder();

function b64url(bytes: ArrayBuffer | Uint8Array): string {
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let s = "";
  for (const b of arr) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromB64url(s: string): string {
  const pad = s.length % 4 === 0 ? "" : "=".repeat(4 - (s.length % 4));
  return atob(s.replace(/-/g, "+").replace(/_/g, "/") + pad);
}

async function key(secret: string) {
  return crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}

export interface SessionPayload {
  mid: string; // member id
  exp: number; // epoch seconds
  /** members.session_version at sign-in; bumping it revokes every session (L7). */
  v?: number;
  /**
   * R2-1: "purchase" = minted by a checkout for an email nobody has verified yet.
   * It can finish the purchase (upsells, receipt) and nothing else, lasts
   * PURCHASE_SESSION_MINUTES, and dies when the inbox owner first verifies.
   */
  s?: "purchase";
}

export const PURCHASE_SESSION_MINUTES = 120;

export async function signSession(payload: SessionPayload, secret: string): Promise<string> {
  const body = b64url(enc.encode(JSON.stringify(payload)));
  const sig = await crypto.subtle.sign("HMAC", await key(secret), enc.encode(body));
  return `${body}.${b64url(sig)}`;
}

export async function verifySession(token: string | undefined | null, secret: string): Promise<SessionPayload | null> {
  if (!token) return null;
  const [body, sig] = token.split(".");
  if (!body || !sig) return null;
  const expected = b64url(await crypto.subtle.sign("HMAC", await key(secret), enc.encode(body)));
  if (expected.length !== sig.length) return null;
  let diff = 0;
  for (let i = 0; i < sig.length; i++) diff |= sig.charCodeAt(i) ^ expected.charCodeAt(i);
  if (diff !== 0) return null;
  try {
    const payload = JSON.parse(fromB64url(body)) as SessionPayload;
    if (!payload.mid || payload.exp < Date.now() / 1000) return null;
    return payload;
  } catch {
    return null;
  }
}

export async function sha256Hex(v: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", enc.encode(v));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function randomToken(bytes = 24): string {
  const a = new Uint8Array(bytes);
  crypto.getRandomValues(a);
  return b64url(a);
}

/** L7: a session is only valid for the member's current session_version. */
export function sessionMatchesMember(payload: Pick<SessionPayload, "v">, member: { session_version?: number | null }): boolean {
  return (payload.v ?? 1) === (member.session_version ?? 1);
}
