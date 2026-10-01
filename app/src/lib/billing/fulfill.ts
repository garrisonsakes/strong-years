/**
 * Provisioning after a successful checkout. Called from the Stripe webhook
 * (checkout.session.completed) and from the success redirect (whichever arrives
 * first). Idempotent: a completed intent is never fulfilled twice.
 */
import { env, messaging, offerRules } from "../config";
import type { Store } from "../db/store";
import type { CheckoutIntent, Member, Membership, Order, OrderKind } from "../db/types";
import { findMemberByEmail, upsertMember } from "../members";
import { sendPurchaseVerification } from "./verifyPurchase";
import { addDays, addMonths, formatDate, moneyExact, offerDef, type OfferCode } from "../pricing";
import { trackMetaEvent } from "../analytics/meta";
import { sendEmail, sendSms } from "../notify";
import { issueMagicLink } from "../auth/verification";
import { confirmFoundingSpot, holdsFoundingSpot } from "../founding";
import { createGift } from "../gifts";
import { recordAdConsent } from "../conversions/consent";
import { linkWaitlistToMember } from "../waitlist";

export interface FulfillContext {
  now?: Date;
  stripeCustomerId?: string | null;
  stripeSubscriptionId?: string | null;
  stripePaymentIntentId?: string | null;
  stripeInvoiceId?: string | null;
  stripePaymentMethodId?: string | null;
  /** Card fingerprint (one money-back guarantee per person). */
  cardFingerprint?: string | null;
}

export interface FulfillResult {
  member: Member;
  membership: Membership | null;
  orders: Order[];
  alreadyDone: boolean;
}

const LINE_TO_ORDER: Record<string, OrderKind> = {
  trial_fee: "trial_fee",
  front_end: "front_end",
  bump: "bump",
  membership_first_month: "membership_charge",
  gift: "gift",
};


async function doneResult(store: Store, intentId: string): Promise<FulfillResult | null> {
  const intent = await store.get("checkout_intents", intentId);
  if (!intent || intent.status !== "complete" || !intent.member_id) return null;
  const member = (await store.get("members", intent.member_id))!;
  const membership = await store.findOne("memberships", { checkout_intent_id: intent.id });
  const orders = await store.find("sy_orders", { checkout_intent_id: intent.id });
  return { member, membership, orders, alreadyDone: true };
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Insert unless the unique key already exists (the DB constraint is the real guard). */
async function insertOnce<T extends "memberships" | "sy_orders">(store: Store, table: T, key: Partial<Record<string, unknown>>, row: Record<string, unknown>) {
  const existing = await store.findOne(table, key as never);
  if (existing) return existing;
  try {
    return await store.insert(table, row as never);
  } catch (err) {
    const again = await store.findOne(table, key as never);
    if (again) return again;
    throw err;
  }
}

export async function fulfillCheckoutIntent(store: Store, intentId: string, ctx: FulfillContext = {}): Promise<FulfillResult> {
  const first = await store.get("checkout_intents", intentId);
  if (!first) throw new Error(`checkout intent not found: ${intentId}`);
  const now = ctx.now ?? new Date();

  // H8: claim the intent atomically (open → fulfilling). The success redirect and the
  // webhook can arrive together; exactly one of them does the work.
  const [claimed] = await store.updateWhere("checkout_intents", { id: intentId, status: "open" }, { status: "fulfilling" });
  let intent = claimed;
  let recovery = false;
  if (!intent) {
    const done = await doneResult(store, intentId);
    if (done) return done;
    // Someone else is fulfilling: wait for them (up to ~5 s).
    for (let i = 0; i < 25; i++) {
      await sleep(200);
      const d = await doneResult(store, intentId);
      if (d) return d;
    }
    // Still not complete: the other worker probably crashed. Every write below is
    // idempotent (unique keys), so finishing the job is safe; emails are skipped.
    intent = (await store.get("checkout_intents", intentId))!;
    if (intent.status === "failed") throw new Error(`checkout intent ${intentId} failed`);
    recovery = true;
  }

  const def = offerDef(intent.offer_code as OfferCode);
  const isGift = def.kind === "gift";

  // NEW-1: typing someone's email at checkout proves nothing. The buyer owns the account
  // only if this checkout creates it, or they started checkout signed in as that member.
  // Decided once and stored, so a retry after a crash can't re-decide it.
  const existing = await findMemberByEmail(store, intent.email);
  const buyerIsOwner = intent.buyer_is_owner ?? (!existing || intent.auth_member_id === existing.id);
  if (intent.buyer_is_owner === null || intent.buyer_is_owner === undefined) {
    await store.update("checkout_intents", intent.id, { buyer_is_owner: buyerIsOwner, stripe_customer_id: ctx.stripeCustomerId ?? null });
  }
  const member =
    existing && !buyerIsOwner
      ? existing // never touch another person's contact details, Stripe customer or card
      : await upsertMember(store, {
          email: intent.email,
          firstName: intent.first_name,
          phone: intent.phone,
          smsOptIn: intent.sms_consent,
          ageConfirmed: intent.age_confirmed,
          attribution: intent.attribution,
          stripeCustomerId: ctx.stripeCustomerId ?? null,
          stripePaymentMethod: ctx.stripePaymentMethodId ?? null,
        });
  if (buyerIsOwner && ctx.cardFingerprint && !member.card_fingerprint) await store.update("members", member.id, { card_fingerprint: ctx.cardFingerprint });
  const pendingVerification = !buyerIsOwner;

  // Link the consent records captured before payment to the member.
  const consents = await store.find("consent_log", { email: intent.email.toLowerCase() });
  for (const c of consents) if (!c.member_id) await store.update("consent_log", c.id, { member_id: member.id });

  // Organic launch: only when the buyer provably owns this email (NEW-1) do we record
  // their ad-measurement box and carry their waitlist history (post-level attribution)
  // onto the member. Attribution is reporting only; it never touches the price.
  if (buyerIsOwner && !isGift) {
    if (intent.ad_consent && !recovery) await recordAdConsent(store, member.email, { memberId: member.id, ip: null, userAgent: null, source: `checkout ${intent.id}` });
    try {
      await linkWaitlistToMember(store, (await store.get("members", member.id)) ?? member, intent.attribution, now);
    } catch (err) {
      console.error("waitlist link failed", (err as Error).message);
    }
  }

  let membership: Membership | null = null;
  const giftAlready =
    isGift && intent.gift && recovery
      ? await store.findOne("gifts", { gifter_email: member.email, recipient_email: intent.gift.recipient_email.toLowerCase(), created_at: { gte: intent.created_at } })
      : null;
  if (isGift && intent.gift && !giftAlready) {
    // C1: the claim link goes only to the recipient; the gifter's receipt has no code or link.
    await createGift(store, {
      gifter: member,
      recipientName: intent.gift.recipient_name,
      recipientEmail: intent.gift.recipient_email,
      message: intent.gift.message,
      months: intent.gift.months,
      amountCents: intent.amount_today_cents,
    });
  } else if (intent.membership_price_cents !== null) {
    const trial = intent.trial_days > 0;
    const trialEnd = trial ? addDays(now, intent.trial_days) : null;
    // Round 8: the spot taken at checkout is confirmed under the same lock. A very late
    // payment whose hold lapsed and whose spot is gone does not become founding.
    let founding = intent.arm === "B" && !trial && intent.price_cell !== "standard";
    if (founding && holdsFoundingSpot(intent) && !(await confirmFoundingSpot(store, intent.id, offerRules.foundingCap, now))) {
      founding = false;
      await store.update("checkout_intents", intent.id, { price_cell: "over_cap" });
      intent.price_cell = "over_cap";
      await store.insert("support_tickets", {
        member_id: member.id,
        email: member.email,
        reason: "refund_review",
        message: `Founding cohort was full when this payment was confirmed (hold expired before fulfilment). Not marked founding. Refund the first charge or move to the standard price with the member's consent. Intent ${intent.id}.`,
        status: "open",
      });
    }
    membership = (await insertOnce(store, "memberships", { checkout_intent_id: intent.id }, {
      checkout_intent_id: intent.id,
      gift_credit_cents: 0,
      pending_verification: pendingVerification,
      stripe_customer_id: ctx.stripeCustomerId ?? null,
      member_id: member.id,
      plan: "monthly",
      arm: intent.arm,
      offer_code: intent.offer_code,
      price_cents: intent.membership_price_cents,
      interval: "month",
      status: trial ? "trialing" : "active",
      founding,
      stripe_subscription_id: ctx.stripeSubscriptionId ?? null,
      trial_end: trialEnd ? trialEnd.toISOString() : null,
      current_period_end: (trialEnd ?? addMonths(now, 1)).toISOString(),
      first_paid_at: trial ? null : now.toISOString(),
      guarantee_until: trial ? null : addDays(now, offerRules.guaranteeDaysFoundingArm).toISOString(),
      cancel_at_period_end: false,
      canceled_at: null,
      paused_until: null,
      partner_seat: false,
      processor: intent.processor ?? "stripe",
      price_cell: intent.price_cell ?? null,
      is_demo: false,
    })) as Membership;

    const next = formatDate(membership.current_period_end!, env.displayTimeZone);
    const price = moneyExact(membership.price_cents);
    const todayLine = trial
      ? `Today's charge: ${moneyExact(intent.amount_today_cents)} (${def.kind === "front_end" ? `the ${def.name}, including 7 days of Strong Years` : "7-day trial"})`
      : `Today's charge: ${moneyExact(intent.amount_today_cents)} (includes your first month of Strong Years)`;
    const refundLine = founding
      ? "Refunds: 14-day money-back guarantee on your membership charge, self-serve in your account or by replying to this email. One money-back guarantee per person. Add-ons you bought today are one-time purchases with their own terms (see the refund policy)."
      : "Refunds: 14-day money-back guarantee on your first full membership charge, counted from the day of that charge, self-serve in your account or by replying to this email. One money-back guarantee per person.";
    const cancelHow = messaging.smsEnabled
      ? `How to cancel: ${env.siteUrl}/app/account → Cancel (at most two screens, online, anytime), or text CANCEL. Emailing us also works: a person reads it within one business day.`
      : `How to cancel: ${env.siteUrl}/app/account → Cancel (at most two screens, online, anytime). Emailing us also works: a person reads it within one business day.`;
    if (!recovery && pendingVerification) {
      await sendPurchaseVerification(store, intent.id, member, [
        `Plan: Strong Years, monthly${founding ? " (founding price, locked while you stay subscribed, pauses included)" : ""}`,
        todayLine,
        trial ? `Trial ends: ${next}` : `Next charge: ${next}`,
        `After that: ${price} per month, until you cancel.`,
        cancelHow,
        refundLine,
      ]);
    }
    // R2-1: a new account's email isn't verified yet, so the welcome email carries the
    // one-time link that proves the inbox and opens the program (72 hours).
    const openLink = !recovery && !pendingVerification && !member.email_verified_at ? await issueMagicLink(store, member.id, env.siteUrl, "/app", 72 * 3600_000) : null;
    if (!recovery && !pendingVerification) await sendEmail({
      to: member.email,
      from: "chang",
      template: "E1_welcome_terms",
      subject: "Your first session is 8 minutes. Here it is.",
      secrets: openLink ? [openLink] : [],
      text: [
        openLink
          ? `${member.first_name}, tap to confirm this is your email and open your Daily Practice (one-time link, works for 72 hours): ${openLink}`
          : `${member.first_name}, your Daily Practice is ready: ${env.siteUrl}/app`,
        "Your membership details",
        `Plan: Strong Years, monthly${founding ? " (founding price, locked while you stay subscribed)" : ""}`,
        todayLine,
        trial ? `Trial ends: ${next}` : `Next charge: ${next}`,
        `After that: ${price} per month, until you cancel.`,
        cancelHow,
        "Before every renewal we email you a reminder with the date and amount.",
        refundLine,
        "On your statement: STRONGYEARS MEMBER",
        "— Chang Yin (AI coach)",
      ].join("\n"),
    });
    if (!recovery && !pendingVerification && member.sms_opt_in && member.phone) {
      await sendSms(
        member.phone,
        `Strong Years: Welcome, ${member.first_name}! Your first session is 8 min: ${env.siteUrl}/app. ${trial ? `Trial ends ${next}, then ${price}/mo until you cancel.` : `Next charge ${next}, ${price}/mo until you cancel.`} Chang Yin is an AI character. Reply STOP to opt out.`,
        "S1_welcome",
      );
    }
  }

  // Orders are tied to this membership (H1: refunds are scoped to it) and to the
  // invoice / payment intent (C4: refunds need a real payment to refund).
  const orders: Order[] = [];
  for (const line of intent.lines) {
    const kind = LINE_TO_ORDER[line.kind] ?? "front_end";
    const offerCode = line.kind === "bump" || line.kind === "front_end" ? (line.sku ?? intent.offer_code) : intent.offer_code;
    orders.push(
      (await insertOnce(store, "sy_orders", { checkout_intent_id: intent.id, kind, offer_code: offerCode }, {
        member_id: member.id,
        membership_id: membership?.id ?? null,
        email: member.email,
        offer_code: offerCode,
        kind,
        description: line.label,
        amount_cents: line.cents,
        amount_refunded_cents: 0,
        status: "paid",
        stripe_payment_intent: ctx.stripePaymentIntentId ?? null,
        stripe_invoice: ctx.stripeInvoiceId ?? null,
        checkout_intent_id: intent.id,
        processor: intent.processor ?? "stripe",
        is_demo: false,
      })) as Order,
    );
  }

  await store.update("checkout_intents", intent.id, {
    status: "complete",
    completed_at: new Date().toISOString(),
    member_id: member.id,
    stripe_session_id: intent.stripe_session_id,
  });

  if (recovery) return { member: (await store.get("members", member.id))!, membership, orders, alreadyDone: false };

  // Server-side conversion events (Meta-safe names; no health data).
  const base = {
    sourcePath: isGift ? "/gift" : `/checkout/${intent.offer_code}`,
    email: member.email,
    phone: member.phone,
    attribution: intent.attribution,
    memberId: member.id,
    contentName: intent.offer_code,
  };
  if (membership?.status === "trialing") {
    await trackMetaEvent({ ...base, name: "StartTrial", eventId: `trial_${intent.id}`, valueCents: intent.amount_today_cents }, env.siteUrl);
  }
  if (membership?.status === "active") {
    await trackMetaEvent({ ...base, name: "Subscribe", eventId: `sub_${intent.id}`, valueCents: membership.price_cents }, env.siteUrl);
  }
  await trackMetaEvent({ ...base, name: "Purchase", eventId: `purchase_${intent.id}`, valueCents: intent.amount_today_cents }, env.siteUrl);

  return { member: (await store.get("members", member.id))!, membership, orders, alreadyDone: false };
}

export type { CheckoutIntent };
