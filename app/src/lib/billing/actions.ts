/**
 * Membership side effects. Each action updates Stripe (when configured) and our
 * own tables, so the UI is correct immediately; the webhook re-syncs afterwards.
 */
import { env, prices } from "../config";
import type { Store } from "../db/store";
import type { Member, Membership, Order } from "../db/types";
import { addMonths, formatDate, moneyExact } from "../pricing";
import { alertOnCall, sendEmail } from "../notify";
import { invoicePaymentIntent } from "./webhook";
import { trackMetaEvent } from "../analytics/meta";
import { accessUntil, withinGuarantee, type CancelReason, type SaveOffer } from "./cancel";
import { priceId, stripe } from "./stripeClient";
import { processorFor } from "./processors";
import { assertPriceAmount } from "./stripeSession";

async function recordCancellation(
  store: Store,
  m: Membership,
  reason: CancelReason | null,
  offer: SaveOffer | null,
  outcome: "canceled" | "saved_pause" | "saved_downgrade" | "undone",
) {
  await store.insert("cancellations", {
    membership_id: m.id,
    member_id: m.member_id,
    reason,
    offer_shown: offer?.kind ?? null,
    outcome,
  });
}

export async function cancelMembership(store: Store, m: Membership, reason: CancelReason | null, offerShown: SaveOffer | null) {
  const s = stripe();
  if (s && m.stripe_subscription_id) {
    await s.subscriptions.update(m.stripe_subscription_id, { cancel_at_period_end: true, pause_collection: null });
  }
  const updated = (await store.update("memberships", m.id, {
    cancel_at_period_end: true,
    canceled_at: new Date().toISOString(),
    status: m.status === "paused" ? "canceled" : m.status,
    paused_until: null,
  }))!;
  await recordCancellation(store, m, reason, offerShown, "canceled");
  const member = await store.get("members", m.member_id);
  const until = accessUntil(updated);
  if (member) {
    await sendEmail({
      to: member.email,
      template: "F_cancel_confirmation",
      subject: "Your Strong Years membership is cancelled",
      text: [
        "Your Strong Years membership is cancelled. You won't be charged again.",
        until ? `You have access until ${formatDate(until, env.displayTimeZone)}.` : "",
        "Your streak, Strength Age history and what the coach remembers are saved for 90 days, and you can restart anytime.",
        `Cancelled by mistake? Undo it here: ${env.siteUrl}/app/account`,
      ]
        .filter(Boolean)
        .join("\n\n"),
    });
  }
  return updated;
}

export async function undoCancel(store: Store, m: Membership) {
  const s = stripe();
  if (s && m.stripe_subscription_id) await s.subscriptions.update(m.stripe_subscription_id, { cancel_at_period_end: false });
  const updated = await store.update("memberships", m.id, {
    cancel_at_period_end: false,
    canceled_at: null,
    status: m.status === "canceled" ? "active" : m.status,
  });
  await recordCancellation(store, m, null, null, "undone");
  return updated;
}

export async function pauseMembership(store: Store, m: Membership, months: number, reason: CancelReason | null, offer: SaveOffer | null) {
  const safeMonths = Math.min(3, Math.max(1, Math.round(months)));
  const resumes = addMonths(new Date(), safeMonths);
  const s = stripe();
  if (s && m.stripe_subscription_id) {
    await s.subscriptions.update(m.stripe_subscription_id, {
      pause_collection: { behavior: "void", resumes_at: Math.floor(resumes.getTime() / 1000) },
    });
  }
  const updated = await store.update("memberships", m.id, { status: "paused", paused_until: resumes.toISOString() });
  await recordCancellation(store, m, reason, offer, "saved_pause");
  const member = await store.get("members", m.member_id);
  if (member) {
    await sendEmail({
      to: member.email,
      template: "pause_confirmation",
      subject: `Paused until ${formatDate(resumes, env.displayTimeZone)}`,
      text: `Your membership is paused. Nothing is charged until ${formatDate(resumes, env.displayTimeZone)}. We'll remind you a week before it restarts. Want to come back sooner or cancel instead? ${env.siteUrl}/app/account`,
    });
  }
  return updated;
}

export async function resumeMembership(store: Store, m: Membership) {
  const s = stripe();
  if (s && m.stripe_subscription_id) await s.subscriptions.update(m.stripe_subscription_id, { pause_collection: null });
  return store.update("memberships", m.id, { status: "active", paused_until: null });
}

export async function downgradeToEssentials(store: Store, m: Membership, reason: CancelReason | null, offer: SaveOffer | null) {
  const s = stripe();
  if (s && m.stripe_subscription_id) {
    const sub = await s.subscriptions.retrieve(m.stripe_subscription_id);
    const item = sub.items.data.find((i) => i.price.recurring && i.price.unit_amount !== prices.partner) ?? sub.items.data[0];
    const essentials = priceId("essentials");
    if (essentials) await assertPriceAmount(s, essentials, prices.essentials);
    if (item) {
      await s.subscriptions.update(m.stripe_subscription_id, {
        proration_behavior: "none",
        items: [
          essentials
            ? { id: item.id, price: essentials }
            : {
                id: item.id,
                price_data: {
                  currency: "usd",
                  product: typeof item.price.product === "string" ? item.price.product : item.price.product.id,
                  unit_amount: prices.essentials,
                  recurring: { interval: "month" },
                },
              },
        ],
      });
    }
  }
  const updated = await store.update("memberships", m.id, { plan: "essentials", price_cents: prices.essentials });
  await recordCancellation(store, m, reason, offer, "saved_downgrade");
  const member = await store.get("members", m.member_id);
  if (member) {
    await sendEmail({
      to: member.email,
      template: "downgrade_confirmation",
      subject: "You're on Strong Years Essentials, $12 a month",
      text: `Done. From your next charge date your membership is ${moneyExact(prices.essentials)} a month until you cancel. Cancel anytime online in two screens at most: ${env.siteUrl}/app/account`,
    });
  }
  return updated;
}

export interface RefundResult {
  ok: boolean;
  /** "done": Stripe confirmed; "pending": Stripe accepted, bank still processing; "review": a person will handle it. */
  state: "done" | "pending" | "review" | "ineligible";
  refundedCents: number;
  message: string;
}

/** Resolves the payment behind an order: stored PI, else the invoice's PI from Stripe (C4). */
async function paymentFor(order: Order): Promise<string | null> {
  if (order.stripe_payment_intent) return order.stripe_payment_intent;
  const s = order.processor === "braintree" ? null : stripe();
  if (s && order.stripe_invoice && !order.stripe_invoice.startsWith("in_mock_")) {
    const inv = (await s.invoices.retrieve(order.stripe_invoice, { expand: ["payments"] })) as unknown as Record<string, unknown>;
    return invoicePaymentIntent(inv);
  }
  return null;
}

async function openRefundTicket(store: Store, m: Membership, why: string) {
  const member = await store.get("members", m.member_id);
  const t = await store.insert("support_tickets", { member_id: m.member_id, email: member?.email ?? null, reason: "refund_review", message: `Refund request for membership ${m.id}: ${why}`, status: "open" });
  await alertOnCall("Refund needs a person", `ticket-${t.id}`);
}

/** Has this person (email or card) already had a money-back refund? (AUDIT_BUSINESS F08) */
export async function usedGuaranteeBefore(store: Store, member: Pick<Member, "email" | "card_fingerprint">): Promise<boolean> {
  if (await store.findOne("refund_ledger", { email: member.email.toLowerCase() })) return true;
  if (member.card_fingerprint && (await store.findOne("refund_ledger", { card_fingerprint: member.card_fingerprint }))) return true;
  return false;
}

/**
 * Self-serve money-back refund (C4, H1, F08).
 *  - Only this membership's membership charge (+ the $1 trial fee), only inside
 *    the window, capped at one month plus the trial fee. Add-ons are one-time
 *    items with their own terms and are not part of the self-serve refund.
 *  - The processor must confirm. Nothing is marked refunded and no "refunded"
 *    email goes out unless Stripe says the refund succeeded. If there is no
 *    payment to refund, or the processor fails, a person gets a ticket instead.
 *  - One guarantee refund per person (email or card fingerprint); repeats go to a person.
 */
export async function refundMembership(store: Store, m: Membership, now = new Date()): Promise<RefundResult> {
  if (!withinGuarantee(m, now.getTime())) {
    return { ok: false, state: "ineligible", refundedCents: 0, message: "This membership is outside the money-back window. Reply to any email and a person will help." };
  }
  const member = await store.get("members", m.member_id);
  if (!member) return { ok: false, state: "ineligible", refundedCents: 0, message: "Account not found." };
  if (await usedGuaranteeBefore(store, member)) {
    await openRefundTicket(store, m, "repeat money-back request (email or card used before)");
    return { ok: false, state: "review", refundedCents: 0, message: "You've used the money-back guarantee before, so a person on our team will review this by email within one business day. Nothing has changed yet." };
  }
  const since = new Date(m.first_paid_at ?? m.created_at).getTime() - 60 * 60_000;
  const until = new Date(m.guarantee_until!).getTime();
  const cap = m.price_cents + prices.trialFee;
  const eligible = (await store.find("sy_orders", { membership_id: m.id, status: "paid" }))
    .filter((o) => o.kind === "membership_charge" || o.kind === "trial_fee")
    .filter((o) => {
      const t = new Date(o.created_at).getTime();
      return t >= since && t <= until;
    })
    .sort((a, b) => a.created_at.localeCompare(b.created_at));
  if (eligible.length === 0) {
    await openRefundTicket(store, m, "no eligible charge found on this membership");
    return { ok: false, state: "review", refundedCents: 0, message: "We couldn't find the charge to refund automatically, so a person on our team will sort it out by email within one business day. Nothing has changed yet." };
  }

  let budget = cap;
  let done = 0;
  let pending = 0;
  for (const ord of eligible) {
    const amount = Math.min(ord.amount_cents - (ord.amount_refunded_cents ?? 0), budget);
    if (amount <= 0) continue;
    const proc = processorFor(ord.processor);
    const live = proc.status() === "live";
    const pi = await paymentFor(ord);
    if (live && !pi) {
      await openRefundTicket(store, m, `order ${ord.id} has no resolvable payment yet`);
      return { ok: false, state: "review", refundedCents: done, message: "Your payment is still settling, so a person on our team will finish this refund by email within one business day. Nothing has changed yet." };
    }
    const r = await proc.refund(pi ?? `pi_mock_${ord.id}`, amount, `refund:${ord.id}:${amount}`);
    if (r.status === "failed") {
      await openRefundTicket(store, m, `processor refused refund for order ${ord.id}: ${r.error ?? "unknown"}`);
      return { ok: false, state: "review", refundedCents: done, message: "The card company didn't accept the refund automatically. A person on our team will finish it by email within one business day." };
    }
    if (r.status === "succeeded") {
      await store.update("sy_orders", ord.id, { status: ord.amount_cents - (ord.amount_refunded_cents ?? 0) - amount <= 0 ? "refunded" : "paid", amount_refunded_cents: (ord.amount_refunded_cents ?? 0) + amount });
      done += amount;
    } else {
      await store.update("sy_orders", ord.id, { status: "refund_pending" });
      pending += amount;
    }
    budget -= amount;
  }

  // The refund request is accepted: stop billing now either way.
  const s = m.processor === "braintree" ? null : stripe();
  if (s && m.stripe_subscription_id) await s.subscriptions.cancel(m.stripe_subscription_id);
  await store.insert("refund_ledger", { email: member.email.toLowerCase(), card_fingerprint: member.card_fingerprint ?? null, member_id: member.id, membership_id: m.id, amount_cents: done + pending, processor_refund_id: null });

  if (pending > 0) {
    await store.update("memberships", m.id, { status: "canceled", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString() });
    await sendEmail({
      to: member.email,
      template: "refund_processing",
      subject: "Your refund request is with your bank",
      text: `We've asked your card company to refund ${moneyExact(done + pending)}. They're still processing it; we'll email you as soon as it's confirmed. Your membership has ended and you won't be charged again.`,
    });
    return { ok: true, state: "pending", refundedCents: done, message: `Refund of ${moneyExact(done + pending)} requested. We'll email you when your bank confirms it.` };
  }
  await store.update("memberships", m.id, { status: "refunded", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString() });
  await sendEmail({
    to: member.email,
    template: "refund_confirmation",
    subject: "Your refund is on its way",
    text: `We've refunded ${moneyExact(done)} to your card. It usually shows in 5–10 days. Your membership has ended and you won't be charged again. Add-ons you bought separately are one-time purchases and weren't part of this refund; reply to this email if something about them wasn't right.`,
  });
  return { ok: true, state: "done", refundedCents: done, message: `Refunded ${moneyExact(done)}.` };
}

export const UPSELLS = {
  program: { kind: "upsell_program" as const, cents: prices.programUpsell, label: "12-week program to keep forever" },
  printables: { kind: "downsell_printables" as const, cents: prices.printablesDownsell, label: "Printables pack" },
  kit: { kind: "upsell_kit" as const, cents: prices.kitUpsell, label: "The Strong Years Kit" },
};

export type UpsellKey = keyof typeof UPSELLS;

/** One-click post-purchase charge on the saved payment method. */
export const UPSELL_WINDOW_MS = 30 * 60_000;

export async function chargeUpsell(store: Store, member: Member, key: UpsellKey, detail: string | null, now = new Date()) {
  const u = UPSELLS[key];
  const already = await store.findOne("sy_orders", { member_id: member.id, kind: u.kind });
  if (already) return { ok: true, duplicate: true as const, orderId: already.id };
  // M8: one-click only right after a purchase (30 minutes), never as a standing endpoint.
  const last = await store.findOne("checkout_intents", { member_id: member.id, status: "complete" }, { orderBy: "created_at", desc: true });
  const doneAt = last?.completed_at ? new Date(last.completed_at).getTime() : 0;
  if (!last || !doneAt || now.getTime() - doneAt > UPSELL_WINDOW_MS) {
    return { ok: false, duplicate: false as const, error: "This offer was only available right after your purchase. No charge was made." };
  }
  const latest = await store.findOne("memberships", { member_id: member.id }, { orderBy: "created_at", desc: true });
  const processorId = latest?.processor ?? "stripe";
  const proc = processorFor(processorId);
  let pi: string | null = null;
  if (proc.status() === "live") {
    if (!member.stripe_customer_id || !member.stripe_payment_method) {
      return { ok: false, duplicate: false as const, error: "No saved card on file. Please use the regular checkout." };
    }
    const r = await proc.chargeOffSession({
      customerId: member.stripe_customer_id,
      paymentMethodId: member.stripe_payment_method,
      amountCents: u.cents,
      description: `${u.label}${detail ? `: ${detail}` : ""}`,
      metadata: { member_id: member.id, upsell: key },
      // M8: a double submit returns the same payment instead of charging twice.
      idempotencyKey: `upsell:${member.id}:${last.id}:${key}`,
    });
    if (!r.ok) return { ok: false, duplicate: false as const, error: r.error ?? "The payment didn't go through. No charge was made." };
    pi = r.paymentId;
  } else {
    pi = `${processorId === "braintree" ? "bt" : "pi"}_mock_${crypto.randomUUID().slice(0, 12)}`;
  }
  let order: Order;
  try {
    order = await store.insert("sy_orders", {
      member_id: member.id,
      membership_id: latest?.id ?? null,
      email: member.email,
      offer_code: key,
      kind: u.kind,
      description: `${u.label}${detail ? `: ${detail}` : ""}`,
      amount_cents: u.cents,
      amount_refunded_cents: 0,
      status: "paid",
      stripe_payment_intent: pi,
      stripe_invoice: null,
      // Unique (intent, kind, sku): a racing second submit can't record a second order.
      checkout_intent_id: last.id,
      processor: processorId,
      is_demo: false,
    });
  } catch {
    const dup = await store.findOne("sy_orders", { checkout_intent_id: last.id, kind: u.kind, offer_code: key });
    if (dup) return { ok: true, duplicate: true as const, orderId: dup.id };
    throw new Error("could not record upsell order");
  }
  if (key === "program" && detail) {
    await store.update("members", member.id, { active_program: detail, program_started_at: new Date().toISOString() });
  }
  await trackMetaEvent(
    { name: "Purchase", eventId: `upsell_${order.id}`, sourcePath: "/upsell", email: member.email, valueCents: u.cents, contentName: key, memberId: member.id, attribution: member.attribution },
    env.siteUrl,
  );
  return { ok: true, duplicate: false as const, orderId: order.id };
}

export async function addPartnerSeat(store: Store, member: Member, m: Membership, partner: { name: string; email: string; share: boolean }) {
  const s = stripe();
  if (s && m.stripe_subscription_id) {
    const partnerPrice = priceId("partner");
    if (!partnerPrice) throw new Error("Set STRIPE_PRICE_PARTNER (a $8/month recurring price) to sell partner seats.");
    await assertPriceAmount(s, partnerPrice, prices.partner);
    await s.subscriptionItems.create({ subscription: m.stripe_subscription_id, price: partnerPrice, proration_behavior: "none" });
  }
  await store.update("memberships", m.id, { partner_seat: true });
  const row = await store.insert("partners", {
    owner_member_id: member.id,
    partner_name: partner.name,
    partner_email: partner.email.toLowerCase(),
    share_progress: partner.share,
    status: "active",
  });
  await sendEmail({
    to: partner.email,
    from: "sun",
    template: "partner_invite",
    subject: `${member.first_name} added you to Strong Years`,
    text: `Hello ${partner.name}. ${member.first_name} added you to Strong Years. You get your own level and your own Strength Age. Start here: ${env.siteUrl}/login. — Sun Yoon (AI character)`,
  });
  return row;
}

export async function removePartnerSeat(store: Store, member: Member, m: Membership) {
  const s = stripe();
  if (s && m.stripe_subscription_id) {
    const sub = await s.subscriptions.retrieve(m.stripe_subscription_id);
    const item = sub.items.data.find((i) => i.price.unit_amount === prices.partner);
    if (item) await s.subscriptionItems.del(item.id, { proration_behavior: "none" });
  }
  await store.update("memberships", m.id, { partner_seat: false });
  const partners = await store.find("partners", { owner_member_id: member.id, status: "active" });
  for (const p of partners) await store.update("partners", p.id, { status: "removed" });
}

export async function portalUrl(member: Member): Promise<string> {
  const s = stripe();
  if (s && member.stripe_customer_id) {
    const session = await s.billingPortal.sessions.create({
      customer: member.stripe_customer_id,
      return_url: `${env.siteUrl}/app/account`,
      ...(process.env.STRIPE_PORTAL_CONFIGURATION ? { configuration: process.env.STRIPE_PORTAL_CONFIGURATION } : {}),
    });
    return session.url;
  }
  return `${env.siteUrl}/app/account?portal=demo`;
}
