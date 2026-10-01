/**
 * R2-1 (pre-account hijack). Whoever types an email at checkout has not proved
 * they own it. So:
 *   - a checkout for an email nobody has verified gets a short, purchase-scoped
 *     session (finish the upsells, see the receipt) that can't read the account;
 *   - the first proof of inbox ownership (login link, gift claim link, purchase
 *     confirmation link) marks the email verified AND bumps session_version, which
 *     kills every session minted before it, including any checkout session;
 *   - a full session is only valid for a verified email.
 * Store-parameterised (no next/headers) so it is unit-testable.
 */
import type { Store } from "../db/store";
import type { Member } from "../db/types";
import { PURCHASE_SESSION_MINUTES, SESSION_DAYS, randomToken, sessionMatchesMember, sha256Hex, signSession, verifySession, type SessionPayload } from "./session";

export type SessionScope = "full" | "purchase";

export interface ResolvedSession {
  member: Member;
  scope: SessionScope;
}

/** Checks signature, expiry, session_version and scope against the member's verification state. */
export async function resolveSession(store: Store, token: string | undefined | null, secret: string): Promise<ResolvedSession | null> {
  const payload = await verifySession(token, secret);
  if (!payload) return null;
  const member = await store.get("members", payload.mid);
  if (!member) return null;
  // L7 + R2-1: sessions signed before the last revocation (logout everywhere, refund,
  // first verification of the email) are dead.
  if (!sessionMatchesMember(payload, member)) return null;
  if (payload.s === "purchase") {
    // Belt and braces: once the email is verified, purchase sessions are over even if
    // the version bump were somehow skipped.
    if (member.email_verified_at) return null;
    return { member, scope: "purchase" };
  }
  // A full session is only ever valid for an inbox someone has proved they own.
  if (!member.email_verified_at) return null;
  return { member, scope: "full" };
}

export async function signMemberSession(member: Pick<Member, "id" | "session_version">, scope: SessionScope, secret: string, now = Date.now()): Promise<string> {
  const ttl = scope === "purchase" ? PURCHASE_SESSION_MINUTES * 60 : SESSION_DAYS * 86400;
  const payload: SessionPayload = { mid: member.id, exp: Math.floor(now / 1000) + ttl, v: member.session_version ?? 1 };
  if (scope === "purchase") payload.s = "purchase";
  return signSession(payload, secret);
}

/**
 * First proof of inbox ownership: record it and revoke every earlier session
 * (someone else may have paid with this email before the owner showed up).
 * Later verifications change nothing, so ordinary logins don't sign out other devices.
 * Returns the member as it now stands.
 */
export async function markEmailVerified(store: Store, memberId: string, now = new Date()): Promise<Member | null> {
  for (let attempt = 0; attempt < 3; attempt++) {
    const m = await store.get("members", memberId);
    if (!m) return null;
    if (m.email_verified_at) return m;
    const v = m.session_version ?? 1;
    // Conditional on the version we read, so two racing verifications bump once.
    const [row] = await store.updateWhere("members", { id: memberId, email_verified_at: null, session_version: v }, { email_verified_at: now.toISOString(), session_version: v + 1 });
    if (row) {
      await registrationComplete(store, row);
      return row;
    }
  }
  return store.get("members", memberId);
}

/**
 * The account is registered once its inbox is proved: CompleteRegistration, only
 * with ad-measurement consent (lib/conversions), deduplicated on the member id.
 * Never allowed to break sign-in.
 */
async function registrationComplete(store: Store, member: Member): Promise<void> {
  try {
    const { recordConversion } = await import("../conversions");
    const { env } = await import("../config");
    await recordConversion(store, { name: "CompleteRegistration", eventId: `reg_${member.id}`, sourcePath: "/app", email: member.email, memberId: member.id, attribution: member.attribution }, env.siteUrl);
  } catch (err) {
    console.error("registration event failed", (err as Error).message);
  }
}

/** Stores a hashed one-time login link. */
export async function issueMagicLink(store: Store, memberId: string, siteUrl: string, next = "/app", ttlMs = 30 * 60_000): Promise<string> {
  const token = randomToken();
  await store.insert("magic_links", {
    token_hash: await sha256Hex(token),
    member_id: memberId,
    expires_at: new Date(Date.now() + ttlMs).toISOString(),
    used_at: null,
  });
  const n = next.startsWith("/") && !next.startsWith("//") ? `&next=${encodeURIComponent(next)}` : "";
  return `${siteUrl}/auth/verify?token=${token}${n}`;
}

/* ---------------- sign-in by email code ---------------- */

export const LOGIN_CODE_MAX_ATTEMPTS = 5;

function sixDigits(): string {
  const b = new Uint32Array(1);
  crypto.getRandomValues(b);
  return String(b[0]! % 1_000_000).padStart(6, "0");
}

async function codeHash(memberId: string, code: string): Promise<string> {
  return sha256Hex(`login-code:${memberId}:${code}`);
}

/**
 * One email, two ways in (no password): a one-time link, and a 6-digit code for
 * people who read mail on another device. Both on the same row, both single use,
 * 30 minutes. The code is bound to the member, so it can't be tried against anyone else.
 */
export async function issueLoginLinkAndCode(store: Store, memberId: string, siteUrl: string, next = "/app", ttlMs = 30 * 60_000): Promise<{ link: string; code: string }> {
  const token = randomToken();
  const code = sixDigits();
  await store.insert("magic_links", {
    token_hash: await sha256Hex(token),
    code_hash: await codeHash(memberId, code),
    attempts: 0,
    member_id: memberId,
    expires_at: new Date(Date.now() + ttlMs).toISOString(),
    used_at: null,
  });
  const n = next.startsWith("/") && !next.startsWith("//") ? `&next=${encodeURIComponent(next)}` : "";
  return { link: `${siteUrl}/auth/verify?token=${token}${n}`, code };
}

/**
 * Checks a typed code against the member's newest live code. Wrong guesses burn the
 * row after 5 tries (conditional update, so parallel guesses can't exceed it); the
 * right one is consumed in the same conditional update (single use).
 */
export async function consumeLoginCode(store: Store, memberId: string, rawCode: string, now = new Date()): Promise<boolean> {
  const code = rawCode.replace(/\s+/g, "");
  if (!/^\d{6}$/.test(code)) return false;
  const rows = (await store.find("magic_links", { member_id: memberId, used_at: null, expires_at: { gt: now.toISOString() } }, { orderBy: "created_at", desc: true, limit: 5 })).filter((r) => r.code_hash && (r.attempts ?? 0) < LOGIN_CODE_MAX_ATTEMPTS);
  if (rows.length === 0) return false;
  const h = await codeHash(memberId, code);
  const match = rows.find((r) => r.code_hash === h);
  if (!match) {
    // A wrong guess counts against every live code of this member.
    for (const r of rows) {
      const attempts = r.attempts ?? 0;
      const [bumped] = await store.updateWhere("magic_links", { id: r.id, attempts }, { attempts: attempts + 1 });
      if (bumped && attempts + 1 >= LOGIN_CODE_MAX_ATTEMPTS) await store.update("magic_links", r.id, { used_at: now.toISOString() });
    }
    return false;
  }
  const [won] = await store.updateWhere("magic_links", { id: match.id, used_at: null, attempts: match.attempts ?? 0 }, { used_at: now.toISOString() });
  return Boolean(won);
}
