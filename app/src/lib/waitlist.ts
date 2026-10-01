/**
 * The prelaunch waitlist (organic-first launch). Store-parameterised, so every rule
 * is unit tested without Next.
 *
 * Honest by construction:
 *  - no queue and no positions: everyone confirmed gets the same launch email at the
 *    same moment; referring friends earns one bonus PDF, never a better place;
 *  - the only price promise is "first access at the founding price", with the real
 *    founding counter; the only countdown is to the real CHECKOUT_OPENS_AT;
 *  - double opt-in: nothing is sent to a list address until its inbox confirms;
 *  - the same response for new, pending, confirmed and unsubscribed addresses
 *    (the route never tells anyone whether an email is on the list).
 */
import { randomToken, sha256Hex } from "./auth/session";
import { env } from "./config";
import { firstTouchOf, sanitizeAttribution } from "./analytics/attribution";
import { recordAdConsent, withdrawAdConsent } from "./conversions/consent";
import type { Store } from "./db/store";
import type { Attribution, Member, WaitlistEntry } from "./db/types";
import { normalizeEmail } from "./members";
import { sendEmail } from "./notify";
import { signAccess, signUnsub } from "./waitlistTokens";

export const WAITLIST_EMAIL_CONSENT_TEXT =
  "Email me when Strong Years opens, plus at most 3 launch emails in the 72 hours after that. One-click unsubscribe in every email.";
export const WAITLIST_PUSH_CONSENT_TEXT = "Send a notification to this device when checkout opens, and at most one reminder in the 72 hours after. Nothing else.";

/** The one referral reward (an existing product: the Wall Plan printable, sold as a $9 add-on). */
export const REFERRAL_BONUS_FILE = "twelve_week_printable.pdf";
export const REFERRAL_BONUS_NAME = "The Wall Plan (a printable 12-week plan, sold as a $9 add-on)";

export const CONFIRM_TTL_MS = 72 * 3600_000;
/** At most one signup email per address per 10 minutes, whatever anyone submits. */
export const SIGNUP_EMAIL_GAP_MS = 10 * 60_000;

const REF_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
export const REF_CODE = /^[A-HJ-NP-Z2-9]{8}$/;

export function newReferralCode(): string {
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return [...bytes].map((b) => REF_ALPHABET[b % REF_ALPHABET.length]).join("");
}

export function waitlistLinks(entry: Pick<WaitlistEntry, "id" | "referral_code">, now = Date.now()) {
  const access = signAccess(entry.id, now);
  return {
    access,
    starter: `${env.siteUrl}/waitlist/starter?k=${encodeURIComponent(access)}`,
    referral: `${env.siteUrl}/waitlist?ref=${entry.referral_code}`,
    unsubscribe: `${env.siteUrl}/waitlist/unsubscribe?u=${encodeURIComponent(signUnsub(entry.id))}`,
  };
}

export function isValidEmail(email: string): boolean {
  return email.length <= 254 && /^[^\s@<>"',;]+@[^\s@<>"',;]+\.[^\s@<>"',;]{2,}$/.test(email);
}

function cleanName(raw: string | undefined | null): string | null {
  const v = (raw ?? "").normalize("NFKC").replace(/[\u0000-\u001F\u007F<>]/g, "").trim().slice(0, 60);
  return v || null;
}

export interface SignupInput {
  email: string;
  firstName?: string | null;
  emailConsent: boolean;
  adConsent: boolean;
  ref?: string | null;
  visitorId: string | null;
  attribution: Attribution | null;
  ip: string | null;
  userAgent: string | null;
}

export type SignupOutcome = "created" | "resent_confirm" | "noted_confirmed" | "resubscribe" | "throttled";
export type SignupResult = { ok: true; outcome: SignupOutcome } | { ok: false; errors: { field: string; message: string }[] };

/** Validation happens before any lookup, so errors never depend on whether the email exists. */
export function validateSignup(input: Pick<SignupInput, "email" | "emailConsent">): { field: string; message: string }[] {
  const errors: { field: string; message: string }[] = [];
  if (!isValidEmail(normalizeEmail(input.email ?? ""))) errors.push({ field: "email", message: "Please check your email address." });
  if (!input.emailConsent) errors.push({ field: "consent", message: "Please tick the box so we're allowed to email you when it opens." });
  return errors;
}

async function issueConfirmToken(): Promise<{ token: string; hash: string }> {
  const token = randomToken(24);
  return { token, hash: await sha256Hex(token) };
}

async function sendConfirmEmail(to: string, firstName: string | null, token: string, entry: Pick<WaitlistEntry, "id" | "referral_code">) {
  const link = `${env.siteUrl}/waitlist/confirm?token=${token}`;
  const unsub = waitlistLinks(entry).unsubscribe;
  await sendEmail({
    to,
    from: "team",
    template: "WL1_confirm",
    subject: "Confirm your email for the Strong Years waitlist",
    secrets: [token, link],
    manageLine: `Didn't ask for this? Ignore it and you'll never hear from us, or leave now: ${unsub}`,
    text: [
      `${firstName ? `${firstName}, one` : "One"} tap to confirm this is your email address (the link works for 72 hours):`,
      link,
      "Until you confirm, we won't send you anything else.",
      "What you signed up for: an email the moment checkout opens, with first access at the founding price, and at most 3 launch emails in the 72 hours after that.",
    ].join("\n\n"),
  });
}

async function sendAlreadyOnListEmail(entry: WaitlistEntry) {
  const links = waitlistLinks(entry);
  await sendEmail({
    to: entry.email,
    from: "team",
    template: "WL1b_already",
    subject: "You're already on the Strong Years waitlist",
    manageLine: `Leave the waitlist: ${links.unsubscribe}`,
    text: [
      "Someone (probably you) asked to join the Strong Years waitlist with this address. You're already on it, so there's nothing to do.",
      "We'll email you the moment checkout opens.",
      `Your free starter session: ${links.starter}`,
    ].join("\n\n"),
  });
}

export async function signupWaitlist(store: Store, input: SignupInput, now = new Date()): Promise<SignupResult> {
  const errors = validateSignup(input);
  if (errors.length) return { ok: false, errors };
  const email = normalizeEmail(input.email);
  const firstName = cleanName(input.firstName);
  const attribution = sanitizeAttribution(input.attribution);
  const existing = await store.findOne("waitlist", { email });
  const recentlyEmailed = (e: WaitlistEntry) => Boolean(e.last_signup_email_at && now.getTime() - new Date(e.last_signup_email_at).getTime() < SIGNUP_EMAIL_GAP_MS);

  if (existing) {
    // Keep the first touch; refresh the last touch so the growth engine sees the re-visit.
    const lt = attribution?.last_touch ?? firstTouchOf(attribution);
    const patch: Partial<WaitlistEntry> = {};
    if (lt) patch.attribution = { ...(existing.attribution ?? {}), last_touch: lt };
    if (recentlyEmailed(existing)) {
      if (Object.keys(patch).length) await store.update("waitlist", existing.id, patch);
      return { ok: true, outcome: "throttled" };
    }
    // Claim the email slot atomically, so two simultaneous submits send one email.
    const [claimed] = await store.updateWhere("waitlist", { id: existing.id, last_signup_email_at: existing.last_signup_email_at }, { ...patch, last_signup_email_at: now.toISOString() });
    if (!claimed) return { ok: true, outcome: "throttled" };
    if (claimed.status === "confirmed") {
      await sendAlreadyOnListEmail(claimed);
      return { ok: true, outcome: "noted_confirmed" };
    }
    const { token, hash } = await issueConfirmToken();
    const wasUnsub = claimed.status === "unsubscribed";
    await store.update("waitlist", claimed.id, {
      status: "pending",
      confirm_token_hash: hash,
      confirm_expires_at: new Date(now.getTime() + CONFIRM_TTL_MS).toISOString(),
      // A resubscribe asks again: the new answer replaces the old one.
      ad_consent_requested: input.adConsent && !attribution?.ad_opt_out,
      first_name: claimed.first_name ?? firstName,
    });
    await logEmailConsent(store, email, input);
    await sendConfirmEmail(email, claimed.first_name ?? firstName, token, claimed);
    return { ok: true, outcome: wasUnsub ? "resubscribe" : "resent_confirm" };
  }

  let referredBy: string | null = null;
  const ref = (input.ref ?? "").trim().toUpperCase();
  if (REF_CODE.test(ref)) {
    const referrer = await store.findOne("waitlist", { referral_code: ref });
    if (referrer && referrer.email !== email) referredBy = referrer.id;
  }
  const { token, hash } = await issueConfirmToken();
  let entry: WaitlistEntry | null = null;
  for (let attempt = 0; attempt < 3 && !entry; attempt++) {
    try {
      entry = await store.insert("waitlist", {
        email,
        first_name: firstName,
        status: "pending",
        confirm_token_hash: hash,
        confirm_expires_at: new Date(now.getTime() + CONFIRM_TTL_MS).toISOString(),
        last_signup_email_at: now.toISOString(),
        confirmed_at: null,
        unsubscribed_at: null,
        ad_consent_requested: input.adConsent && !attribution?.ad_opt_out,
        visitor_id: input.visitorId,
        referral_code: newReferralCode(),
        referred_by: referredBy,
        referral_reward_at: null,
        attribution,
        member_id: null,
        converted_at: null,
        ip: input.ip,
        user_agent: input.userAgent ? input.userAgent.slice(0, 300) : null,
      });
    } catch {
      // Either a referral-code collision (retry with a new code) or the same email
      // inserted by a simultaneous request (then it exists: same answer, no email).
      if (await store.findOne("waitlist", { email })) return { ok: true, outcome: "throttled" };
    }
  }
  if (!entry) return { ok: true, outcome: "throttled" };
  await logEmailConsent(store, email, input);
  await sendConfirmEmail(email, firstName, token, entry);
  return { ok: true, outcome: "created" };
}

async function logEmailConsent(store: Store, email: string, input: Pick<SignupInput, "ip" | "userAgent">) {
  await store.insert("consent_log", { email, member_id: null, kind: "waitlist_email", checked: true, text_shown: WAITLIST_EMAIL_CONSENT_TEXT, price_cents: null, first_charge_at: null, offer_code: null, ip: input.ip, user_agent: input.userAgent });
}

export type ConfirmResult = { ok: true; entry: WaitlistEntry; access: string; firstTime: boolean } | { ok: false };

/**
 * Single use: the token hash is cleared in the same conditional update that confirms,
 * so a replayed, forwarded or prefetched-then-reused link does nothing.
 */
export async function confirmWaitlist(store: Store, token: string, meta: { ip: string | null; userAgent: string | null }, now = new Date()): Promise<ConfirmResult> {
  if (!token || token.length > 100 || !/^[A-Za-z0-9_-]+$/.test(token)) return { ok: false };
  const hash = await sha256Hex(token);
  const entry = await store.findOne("waitlist", { confirm_token_hash: hash });
  if (!entry || entry.status !== "pending" || !entry.confirm_expires_at || entry.confirm_expires_at <= now.toISOString()) return { ok: false };
  const [row] = await store.updateWhere("waitlist", { id: entry.id, confirm_token_hash: hash, status: "pending" }, { status: "confirmed", confirmed_at: entry.confirmed_at ?? now.toISOString(), confirm_token_hash: null, confirm_expires_at: null });
  if (!row) return { ok: false };
  const firstTime = !entry.confirmed_at;
  if (row.ad_consent_requested) await recordAdConsent(store, row.email, { ip: meta.ip, userAgent: meta.userAgent, source: "waitlist" });
  if (firstTime) {
    await rewardReferrer(store, row, now);
    try {
      const { recordConversion } = await import("./conversions");
      await recordConversion(store, { name: "Lead", eventId: `wl_${row.id}`, sourcePath: "/waitlist", email: row.email, attribution: row.attribution, now }, env.siteUrl);
    } catch (err) {
      console.error("waitlist conversion failed", (err as Error).message);
    }
    const links = waitlistLinks(row, now.getTime());
    await sendEmail({
      to: row.email,
      from: "chang",
      template: "WL2_confirmed",
      subject: "You're on the list. Here's a session to start with.",
      secrets: [links.access],
      manageLine: `Leave the waitlist: ${links.unsubscribe}`,
      text: [
        `${row.first_name ? `${row.first_name}, you're` : "You're"} on the Strong Years waitlist.`,
        "When checkout opens, you get the email first, with the founding price. There's no queue: everyone on the list hears at the same moment.",
        `While you wait, here's Day 1 of the Daily Practice, the chair version, free: ${links.starter}`,
        `If a friend would like it too, send them your link: ${links.referral}. When one of them confirms their email, you get ${REFERRAL_BONUS_NAME}, free. It doesn't move anyone up a list, because there isn't one.`,
        "— Chang Yin (AI character)",
      ].join("\n\n"),
    });
  }
  return { ok: true, entry: row, access: signAccess(row.id, now.getTime()), firstTime };
}

async function rewardReferrer(store: Store, entry: WaitlistEntry, now: Date) {
  if (!entry.referred_by) return;
  const referrer = await store.get("waitlist", entry.referred_by);
  if (!referrer || referrer.status !== "confirmed") return;
  const [won] = await store.updateWhere("waitlist", { id: referrer.id, referral_reward_at: null }, { referral_reward_at: now.toISOString() });
  if (!won) return; // one reward per person, however many friends confirm
  const links = waitlistLinks(won, now.getTime());
  await sendEmail({
    to: won.email,
    from: "sun",
    template: "WL3_referral_bonus",
    subject: "A friend joined. Your Wall Plan is ready.",
    secrets: [links.access],
    manageLine: `Leave the waitlist: ${links.unsubscribe}`,
    text: [
      "Someone you shared Strong Years with just confirmed their email. Thank you.",
      `As promised, ${REFERRAL_BONUS_NAME} is yours: ${env.siteUrl}/api/waitlist/bonus?k=${encodeURIComponent(links.access)}`,
      "That's the whole reward. It doesn't change your place (there's no line) or your price.",
      "— Sun Yoon (AI character)",
    ].join("\n\n"),
  });
}

export async function confirmedReferrals(store: Store, waitlistId: string): Promise<number> {
  return store.count("waitlist", { referred_by: waitlistId, status: "confirmed" });
}

/** One-click leave: stops every launch email and push, and withdraws ad-measurement consent. */
export async function unsubscribeWaitlist(store: Store, waitlistId: string, meta: { ip: string | null; userAgent: string | null }, now = new Date()): Promise<boolean> {
  const entry = await store.get("waitlist", waitlistId);
  if (!entry) return false;
  if (entry.status !== "unsubscribed") {
    await store.update("waitlist", entry.id, { status: "unsubscribed", unsubscribed_at: now.toISOString(), confirm_token_hash: null, confirm_expires_at: null });
    await withdrawAdConsent(store, entry.email, { ip: meta.ip, userAgent: meta.userAgent, source: "waitlist_unsubscribe" });
  }
  await store.remove("waitlist_push", { waitlist_id: entry.id });
  return true;
}

export async function saveWaitlistPush(store: Store, waitlistId: string, sub: { endpoint: string; p256dh: string; auth: string }, meta: { ip: string | null; userAgent: string | null }): Promise<boolean> {
  const entry = await store.get("waitlist", waitlistId);
  if (!entry || entry.status !== "confirmed") return false;
  if ((await store.count("waitlist_push", { waitlist_id: entry.id })) >= 5) return false;
  const existing = await store.findOne("waitlist_push", { endpoint: sub.endpoint });
  if (existing) await store.update("waitlist_push", existing.id, { waitlist_id: entry.id, p256dh: sub.p256dh, auth: sub.auth, failures: 0 });
  else await store.insert("waitlist_push", { waitlist_id: entry.id, ...sub, failures: 0 });
  await store.insert("consent_log", { email: entry.email, member_id: null, kind: "waitlist_push", checked: true, text_shown: WAITLIST_PUSH_CONSENT_TEXT, price_cents: null, first_charge_at: null, offer_code: null, ip: meta.ip, user_agent: meta.userAgent });
  return true;
}

/**
 * At purchase (buyer owns the email, NEW-1): link the waitlist entry to the member and
 * carry post-level attribution across devices. First touch = the earlier of the two
 * records; last touch = what this checkout saw.
 */
export async function linkWaitlistToMember(store: Store, member: Member, checkoutAttribution: Attribution | null, now = new Date()): Promise<void> {
  const entry = await store.findOne("waitlist", { email: normalizeEmail(member.email) });
  if (!entry) return;
  if (!entry.member_id) await store.updateWhere("waitlist", { id: entry.id, member_id: null }, { member_id: member.id, converted_at: now.toISOString() });
  const wl = entry.attribution;
  if (!wl) return;
  const current = member.attribution;
  const wlFirst = wl.first_seen_at ?? entry.created_at;
  const curFirst = current?.first_seen_at ?? member.created_at;
  const waitlistIsEarlier = !current || (!current.post_id && Boolean(wl.post_id)) || wlFirst < curFirst;
  if (!waitlistIsEarlier) return;
  const last = checkoutAttribution?.last_touch ?? firstTouchOf(checkoutAttribution) ?? current?.last_touch ?? wl.last_touch;
  const merged: Attribution = { ...wl, ...(current?.ad_opt_out ? { ad_opt_out: true } : {}) };
  if (last) merged.last_touch = last;
  else delete merged.last_touch;
  await store.update("members", member.id, { attribution: merged });
}
