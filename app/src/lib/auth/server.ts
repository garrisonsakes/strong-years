import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { env } from "../config";
import { isShopify } from "../billing/provider";
import { getStore } from "../db";
import type { Member, Membership } from "../db/types";
import { entitlementFor, grantsAccess, pickBillingMembership, pickCurrentMembership, type Entitlement } from "../entitlement";
import { PURCHASE_SESSION_MINUTES, SESSION_COOKIE, SESSION_DAYS, sha256Hex } from "./session";
import { issueMagicLink, markEmailVerified, resolveSession, signMemberSession, type ResolvedSession, type SessionScope } from "./verification";

async function currentSession(): Promise<ResolvedSession | null> {
  const jar = await cookies();
  return resolveSession(await getStore(), jar.get(SESSION_COOKIE)?.value, env.sessionSecret);
}

/**
 * The signed-in member, for anything that reads or changes the account (members
 * area, chat, memory, downloads, settings). R2-1: a purchase-scoped checkout
 * session is never enough, and a full session needs a verified email.
 */
export async function currentMember(): Promise<Member | null> {
  const s = await currentSession();
  return s?.scope === "full" ? s.member : null;
}

/**
 * R2-1: the buyer finishing a purchase (upsell ladder, receipt page, buying again).
 * Also accepts the short purchase-scoped session a checkout gives an unverified email.
 */
export async function currentPurchaser(): Promise<ResolvedSession | null> {
  return currentSession();
}

export async function requireMember(): Promise<Member> {
  const m = await currentMember();
  if (!m) redirect("/login");
  return m;
}

export async function memberships(memberId: string): Promise<Membership[]> {
  return (await getStore()).find("memberships", { member_id: memberId }, { orderBy: "created_at", desc: true });
}

export async function entitlement(memberId: string): Promise<Entitlement> {
  return entitlementFor(await memberships(memberId));
}

/**
 * H2: members-area pages, chat and downloads. A session alone is not enough:
 * refunded, expired, paused, gift-purchaser-only accounts go to /join?lapsed=…
 * (the account page stays reachable with requireMember so they can resume).
 */
export async function requireEntitled(): Promise<{ member: Member; entitlement: Entitlement }> {
  const member = await requireMember();
  const ent = await entitlement(member.id);
  if (!ent.access) {
    // Shopify mode: /join leaves for the store at once, so lapsed members see why on their membership page.
    if (isShopify()) redirect(ent.reason === "paused" ? "/app/account?paused=1" : `/app/account?lapsed=${ent.reason}`);
    redirect(ent.reason === "paused" ? "/app/account?paused=1" : `/join?lapsed=${ent.reason}`);
  }
  return { member, entitlement: ent };
}

export async function sessionCookieValue(memberId: string, scope: SessionScope = "full"): Promise<string> {
  const v = (await (await getStore()).get("members", memberId))?.session_version ?? 1;
  return signMemberSession({ id: memberId, session_version: v }, scope, env.sessionSecret);
}

/**
 * R2-1: the only way to mint a full session after an inbox proof (login link,
 * gift claim, purchase confirmation). The first one revokes every earlier session.
 */
export async function verifiedSessionCookie(memberId: string): Promise<string> {
  await markEmailVerified(await getStore(), memberId);
  return sessionCookieValue(memberId, "full");
}

export const sessionCookieOptions = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production" && env.siteUrl.startsWith("https"),
  path: "/",
  maxAge: SESSION_DAYS * 86400,
};

export const purchaseCookieOptions = { ...sessionCookieOptions, maxAge: PURCHASE_SESSION_MINUTES * 60 };

export async function createMagicLink(memberId: string, next = "/app"): Promise<string> {
  return issueMagicLink(await getStore(), memberId, env.siteUrl, next);
}

export async function consumeMagicLink(token: string): Promise<string | null> {
  const store = await getStore();
  const nowIso = new Date().toISOString();
  // Conditional claim: two clicks racing can't both succeed.
  const [row] = await store.updateWhere("magic_links", { token_hash: await sha256Hex(token), used_at: null, expires_at: { gt: nowIso } }, { used_at: nowIso });
  return row?.member_id ?? null;
}

/** The membership the account page shows (billing row first, never a gift over a paid plan). */
export async function currentMembership(memberId: string): Promise<Membership | null> {
  return pickCurrentMembership(await memberships(memberId));
}

/** The membership cancel / pause / refund / partner actions act on (H3). */
export async function billingMembership(memberId: string): Promise<Membership | null> {
  return pickBillingMembership(await memberships(memberId));
}

export function hasAccess(m: Membership | null, now = Date.now()): boolean {
  return grantsAccess(m, now);
}

/** L7: log out everywhere. */
export async function revokeSessions(memberId: string): Promise<void> {
  const store = await getStore();
  const m = await store.get("members", memberId);
  if (m) await store.update("members", memberId, { session_version: (m.session_version ?? 1) + 1 });
}
