/**
 * AUDIT_FINAL NEW-1: a purchase made with an existing member's email, by someone
 * not signed in as them, is attached as "pending verification". Nothing about the
 * account opens, and nothing about the member changes, until the owner of that
 * inbox confirms it from the emailed link. If they say it wasn't them, billing
 * stops at once and a person refunds the payer.
 */
import { env } from "../config";
import type { Store } from "../db/store";
import type { Member } from "../db/types";
import { alertOnCall, sendEmail } from "../notify";
import { randomToken, sha256Hex } from "../auth/session";
import { stripe } from "./stripeClient";

export const VERIFY_DAYS = 7;

export async function sendPurchaseVerification(store: Store, intentId: string, member: Pick<Member, "email" | "first_name">, termsLines: string[]): Promise<string> {
  const token = randomToken(32);
  await store.update("checkout_intents", intentId, {
    verification: "pending",
    verify_token_hash: await sha256Hex(token),
    verify_expires_at: new Date(Date.now() + VERIFY_DAYS * 86_400_000).toISOString(),
  });
  const link = `${env.siteUrl}/checkout/verify?token=${token}`;
  await sendEmail({
    to: member.email,
    template: "purchase_verify",
    subject: "Please confirm your Strong Years purchase",
    text: [
      `Hi ${member.first_name}, someone just bought a Strong Years membership using this email address.`,
      `If it was you, confirm it here and you'll go straight to your Daily Practice: ${link}`,
      "If it wasn't you, open the same link and tap “This wasn't me”. Nothing on your account changes, billing stops, and the payer is refunded. Your own membership (if you have one) isn't affected either way.",
      "The terms of the purchase:",
      ...termsLines,
    ].join("\n\n"),
    secrets: [token, link],
  });
  return token;
}

export type VerifyOutcome = { ok: true; memberId: string; action: "confirm" | "reject" } | { ok: false };

export async function resolvePurchaseVerification(store: Store, token: string, action: "confirm" | "reject", now = new Date()): Promise<VerifyOutcome> {
  if (!token) return { ok: false };
  const hash = await sha256Hex(token);
  const [intent] = await store.updateWhere(
    "checkout_intents",
    { verify_token_hash: hash, verification: "pending", verify_expires_at: { gt: now.toISOString() } },
    { verification: action === "confirm" ? "confirmed" : "rejected", verify_token_hash: null },
  );
  if (!intent || !intent.member_id) return { ok: false };
  const membership = await store.findOne("memberships", { checkout_intent_id: intent.id });
  const member = await store.get("members", intent.member_id);
  if (!member) return { ok: false };

  if (action === "confirm") {
    if (membership) await store.update("memberships", membership.id, { pending_verification: false });
    // The account owner confirmed: their own card details may now be filled in where empty.
    if (!member.stripe_customer_id && intent.stripe_customer_id) await store.update("members", member.id, { stripe_customer_id: intent.stripe_customer_id });
    await sendEmail({
      to: member.email,
      from: "chang",
      template: "E1_welcome_terms",
      subject: "Confirmed. Your first session is 8 minutes.",
      text: `${member.first_name}, thanks for confirming. Your Daily Practice is ready: ${env.siteUrl}/app\n\nManage or cancel anytime: ${env.siteUrl}/app/account`,
    });
    return { ok: true, memberId: member.id, action };
  }

  // Rejected: stop billing now; a person refunds the payer (their card isn't on this account).
  if (membership) {
    const s = stripe();
    if (s && membership.stripe_subscription_id && !membership.stripe_subscription_id.startsWith("sub_mock_")) {
      await s.subscriptions.cancel(membership.stripe_subscription_id).catch((e) => console.error("cancel after rejected purchase failed", e));
    }
    await store.update("memberships", membership.id, { status: "canceled", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString() });
  }
  const t = await store.insert("support_tickets", {
    member_id: member.id,
    email: member.email,
    reason: "refund_review",
    message: `The owner of ${member.email} says they didn't make purchase ${intent.id}. Subscription cancelled; refund the payer in full.`,
    status: "open",
  });
  await alertOnCall("Purchase rejected by the email owner: refund the payer", `ticket-${t.id}`);
  return { ok: true, memberId: member.id, action };
}
