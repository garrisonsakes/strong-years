/**
 * Gift memberships (AUDIT_CODE C1, H3).
 *
 * C1: a gift code never logs anyone in. The only way to use a gift is a claim
 * link emailed to the recipient address the gifter typed. Opening it proves you
 * own that inbox (the same proof as a magic link), then the gift is applied once.
 * The gifter's receipt never contains the code or the link.
 *
 * H3: a gift for someone who already pays never becomes their "current"
 * membership. It is applied as an account credit (Stripe customer balance), or
 * it extends a running gift. Only a brand-new recipient gets a gift membership row.
 */
import { env, mode } from "./config";
import type { Store } from "./db/store";
import type { Gift, Member, Membership } from "./db/types";
import { grantsAccess, pickBillingMembership } from "./entitlement";
import { normalizeEmail, upsertMember } from "./members";
import { sendEmail } from "./notify";
import { addMonths, formatDate, moneyExact } from "./pricing";
import { randomToken, sha256Hex } from "./auth/session";
import { stripe } from "./billing/stripeClient";

export const CLAIM_LINK_DAYS = 60;

export function giftCode(): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  const bytes = new Uint8Array(8);
  crypto.getRandomValues(bytes);
  return [...bytes].map((b) => alphabet[b % alphabet.length]).join("").replace(/(.{4})(.{4})/, "$1-$2");
}

export function normalizeCode(raw: string): string {
  const c = raw.toUpperCase().replace(/[^A-Z0-9]/g, "");
  return c.length === 8 ? `${c.slice(0, 4)}-${c.slice(4)}` : c;
}

export function maskEmail(e: string): string {
  const [u = "", d = ""] = e.split("@");
  return `${u.slice(0, 1)}${"•".repeat(Math.max(2, Math.min(6, u.length - 1)))}@${d}`;
}

async function issueClaimToken(store: Store, gift: Gift, now = new Date()): Promise<string> {
  const token = randomToken(32);
  await store.update("gifts", gift.id, {
    claim_token_hash: await sha256Hex(token),
    claim_expires_at: new Date(now.getTime() + CLAIM_LINK_DAYS * 86_400_000).toISOString(),
  });
  return token;
}

function claimUrl(token: string) {
  return `${env.siteUrl}/gift/claim?token=${token}`;
}

/** Called once, at purchase. Emails the recipient their claim link; the gifter gets a receipt without it. */
export async function createGift(
  store: Store,
  input: { gifter: Pick<Member, "email" | "first_name">; recipientName: string; recipientEmail: string; message: string; months: number; amountCents: number },
): Promise<{ gift: Gift; token: string }> {
  const gift = await store.insert("gifts", {
    gifter_email: input.gifter.email,
    gifter_name: input.gifter.first_name,
    recipient_name: input.recipientName,
    recipient_email: normalizeEmail(input.recipientEmail),
    message: input.message,
    months: input.months,
    amount_cents: input.amountCents,
    code: giftCode(),
    redeemed_member_id: null,
    redeemed_at: null,
    claim_token_hash: null,
    claim_expires_at: null,
    applied_as: null,
  });
  const token = await issueClaimToken(store, gift);
  const link = claimUrl(token);
  await sendEmail({
    to: gift.recipient_email,
    from: "sun",
    template: "gift_recipient",
    subject: `${input.gifter.first_name} gave you ${gift.months} months of Strong Years`,
    text: [
      `Hello ${gift.recipient_name},`,
      `${input.gifter.first_name} gave you ${gift.months} months of Strong Years. It is prepaid and it never renews by itself. Nobody will charge your card.`,
      gift.message ? `Their note: "${gift.message}"` : "",
      `Start here (this link is just for you, so please don't forward it): ${link}`,
      `Lost this email later? Go to ${env.siteUrl}/gift/redeem, type your gift code ${gift.code}, and we'll send a fresh link to this address.`,
      "Eight minutes a day with Chang Yin. I'll send recipes on Sundays. Eat breakfast. — Sun Yoon (AI character)",
    ]
      .filter(Boolean)
      .join("\n\n"),
    secrets: [token, link, gift.code],
  });
  await sendEmail({
    to: input.gifter.email,
    template: "gift_receipt",
    subject: "Your Strong Years gift is on its way",
    text: [
      `Thank you. We've emailed ${gift.recipient_name} at ${maskEmail(gift.recipient_email)} with a private link to start their gift.`,
      `The gift is prepaid for ${gift.months} months and never renews automatically. Total paid: ${moneyExact(input.amountCents)}. On your statement: STRONGYEARS MEMBER.`,
      `If they can't find the email, they can ask us for a new link at ${env.siteUrl}/gift/redeem. For privacy, the link only ever goes to their inbox.`,
    ].join("\n\n"),
  });
  return { gift, token };
}

export type ClaimRequest = { status: "sent"; to: string; token: string } | { status: "not_found" } | { status: "redeemed" };

/**
 * /gift/redeem with a code: never logs in. It re-sends a fresh claim link to the
 * recipient's own inbox (and the response only ever shows a masked address).
 */
export async function requestGiftClaim(store: Store, rawCode: string): Promise<ClaimRequest> {
  const gift = await store.findOne("gifts", { code: normalizeCode(rawCode) });
  if (!gift) return { status: "not_found" };
  if (gift.redeemed_at) return { status: "redeemed" };
  const token = await issueClaimToken(store, gift);
  const link = claimUrl(token);
  await sendEmail({
    to: gift.recipient_email,
    template: "gift_claim_link",
    subject: "Your Strong Years gift link",
    text: `Hello ${gift.recipient_name}, here is your private link to start the gift from ${gift.gifter_name}: ${link}\n\nIt works once. If you didn't ask for this, you can ignore it.`,
    secrets: [token, link],
  });
  return { status: "sent", to: maskEmail(gift.recipient_email), token };
}

export async function giftForClaimToken(store: Store, token: string, now = new Date()): Promise<Gift | null> {
  if (!token) return null;
  const gift = await store.findOne("gifts", { claim_token_hash: await sha256Hex(token) });
  if (!gift || gift.redeemed_at) return null;
  if (!gift.claim_expires_at || new Date(gift.claim_expires_at) <= now) return null;
  return gift;
}

export type ClaimResult = { ok: true; member: Member; gift: Gift; appliedAs: NonNullable<Gift["applied_as"]> } | { ok: false; reason: "invalid" | "age" };

/** Applies the gift once. The caller may then sign in the recipient: they proved inbox access. */
export async function claimGift(store: Store, token: string, input: { firstName: string; ageConfirmed: boolean; share: boolean }, now = new Date()): Promise<ClaimResult> {
  if (!input.ageConfirmed) return { ok: false, reason: "age" };
  const hash = await sha256Hex(token || "-");
  // Single use, atomically: the first request clears the token and sets redeemed_at.
  const [gift] = await store.updateWhere("gifts", { claim_token_hash: hash, redeemed_at: null, claim_expires_at: { gt: now.toISOString() } }, { redeemed_at: now.toISOString(), claim_token_hash: null });
  if (!gift) return { ok: false, reason: "invalid" };

  const member = await upsertMember(store, { email: gift.recipient_email, firstName: input.firstName || gift.recipient_name, ageConfirmed: true });
  const appliedAs = await applyGift(store, member, gift, now);
  await store.update("gifts", gift.id, { redeemed_member_id: member.id, applied_as: appliedAs });
  if (input.share) {
    await store.insert("consent_log", { email: member.email, member_id: member.id, kind: "family_share", checked: true, text_shown: "Send the person who gave me this a monthly note with my session count.", price_cents: null, first_charge_at: null, offer_code: null, ip: null, user_agent: null });
  }
  return { ok: true, member, gift: { ...gift, redeemed_member_id: member.id, applied_as: appliedAs }, appliedAs };
}

/** H3: credit, extend, or start, never replace a paying membership. */
export async function applyGift(store: Store, member: Member, gift: Gift, now = new Date()): Promise<NonNullable<Gift["applied_as"]>> {
  const rows = await store.find("memberships", { member_id: member.id }, { orderBy: "created_at", desc: true });
  const billing = pickBillingMembership(rows, now.getTime());
  if (billing && ["active", "trialing", "past_due", "paused"].includes(billing.status) && !billing.cancel_at_period_end) {
    const s = stripe();
    if (s && member.stripe_customer_id && !mode.mockStripe) {
      await s.customers.createBalanceTransaction(member.stripe_customer_id, {
        amount: -gift.amount_cents,
        currency: "usd",
        description: `Gift from ${gift.gifter_name} (${gift.months} months)`,
      });
    }
    await store.update("memberships", billing.id, { gift_credit_cents: (billing.gift_credit_cents ?? 0) + gift.amount_cents });
    await sendEmail({
      to: member.email,
      template: "gift_applied_credit",
      subject: `${gift.gifter_name}'s gift is now a ${moneyExact(gift.amount_cents)} credit`,
      text: [
        `${gift.gifter_name} gave you ${gift.months} months of Strong Years. Because you already have a membership, we've added ${moneyExact(gift.amount_cents)} to your account as a credit.`,
        "Your next charges use the credit first, so you won't pay until it runs out. Your membership itself hasn't changed: same price, same renewal date, and you can still cancel anytime in your account.",
      ].join("\n\n"),
    });
    return "credit";
  }
  const runningGift = rows.find((r) => r.plan === "gift" && grantsAccess(r, now.getTime()));
  if (runningGift) {
    const from = new Date(Math.max(now.getTime(), new Date(runningGift.current_period_end ?? now).getTime()));
    const end = addMonths(from, gift.months);
    await store.update("memberships", runningGift.id, { current_period_end: end.toISOString(), status: "active" });
    await sendEmail({ to: member.email, template: "gift_applied_extension", subject: "Your Strong Years gift was extended", text: `${gift.gifter_name} added ${gift.months} months. Your gift now runs until ${formatDate(end.toISOString(), env.displayTimeZone)}. It never renews by itself.` });
    return "extension";
  }
  await store.insert("memberships", giftMembershipRow(member.id, gift, now));
  return "gift_membership";
}

export function giftMembershipRow(memberId: string, gift: Pick<Gift, "months">, now = new Date()): Partial<Membership> {
  return {
    member_id: memberId, plan: "gift", arm: null, offer_code: `gift${gift.months}`, price_cents: 0, interval: "none", status: "active", founding: false,
    stripe_subscription_id: null, trial_end: null, current_period_end: addMonths(now, gift.months).toISOString(), first_paid_at: now.toISOString(),
    guarantee_until: null, cancel_at_period_end: true, canceled_at: null, paused_until: null, partner_seat: false, processor: "stripe", price_cell: null,
    checkout_intent_id: null, gift_credit_cents: 0, pending_verification: false, stripe_customer_id: null, is_demo: false,
  };
}

/** H3: the cron job ends prepaid gifts at their end date (in every mode, not just the mock clock). */
export async function expireGifts(store: Store, now = new Date()): Promise<number> {
  const rows = await store.updateWhere("memberships", { plan: "gift", status: "active", current_period_end: { lte: now.toISOString() } }, { status: "expired" });
  for (const m of rows) {
    const member = await store.get("members", m.member_id);
    if (member) {
      await sendEmail({
        to: member.email,
        template: "gift_ended",
        subject: "Your Strong Years gift has ended",
        text: `Your gift months have ended. Nothing was charged and nothing will be. If you'd like to keep going, you can join here: ${env.siteUrl}/join. Your progress is saved for 90 days.`,
      });
    }
  }
  return rows.length;
}
