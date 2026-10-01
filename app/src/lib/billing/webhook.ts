/**
 * Stripe webhook handler. One code path for real Stripe events and for the
 * synthetic events the mock checkout / mock clock produce.
 *
 * Handled: checkout.session.completed, customer.subscription.updated/deleted,
 * invoice.paid, invoice.payment_failed, charge.refunded, charge.dispute.created.
 * Every event is logged in stripe_events and processed at most once.
 */
import { releaseFoundingSpot } from "../founding";
import { env, offerRules, prices } from "../config";
import type { Store } from "../db/store";
import type { Membership, MembershipStatus } from "../db/types";
import { addDays, formatDate, moneyExact } from "../pricing";
import { fulfillCheckoutIntent } from "./fulfill";
import { trackMetaEvent } from "../analytics/meta";
import { alertOnCall, sendEmail, sendSms } from "../notify";
import { stripe } from "./stripeClient";

export interface StripeLikeEvent {
  id: string;
  type: string;
  livemode?: boolean;
  data: { object: Record<string, unknown> };
}

export interface HandleResult {
  duplicate: boolean;
  handled: boolean;
  summary: string;
}

type Obj = Record<string, unknown>;
const s = (o: Obj, k: string): string | null => (typeof o[k] === "string" ? (o[k] as string) : null);
const n = (o: Obj, k: string): number | null => (typeof o[k] === "number" ? (o[k] as number) : null);
const o = (x: unknown): Obj => (x && typeof x === "object" ? (x as Obj) : {});
const idOf = (x: unknown): string | null => (typeof x === "string" ? x : typeof o(x).id === "string" ? (o(x).id as string) : null);
const iso = (unix: number | null) => (unix ? new Date(unix * 1000).toISOString() : null);

/** Subscription id on an invoice across API versions (basil moved it under parent). */
export function invoiceSubscriptionId(inv: Obj): string | null {
  return (
    idOf(inv.subscription) ??
    idOf(o(o(inv.parent).subscription_details).subscription) ??
    null
  );
}

function invoiceMembershipId(inv: Obj): string | null {
  return (
    s(o(o(o(inv.parent).subscription_details).metadata), "membership_id") ??
    s(o(o(inv.subscription_details).metadata), "membership_id")
  );
}

export function invoicePaymentIntent(inv: Obj): string | null {
  const direct = idOf(inv.payment_intent);
  if (direct) return direct;
  const payments = o(inv.payments).data;
  if (Array.isArray(payments) && payments[0]) return idOf(o(o(payments[0]).payment).payment_intent);
  return null;
}

function invoiceIntentId(inv: Obj): string | null {
  return (
    s(o(o(o(inv.parent).subscription_details).metadata), "intent_id") ??
    s(o(o(inv.subscription_details).metadata), "intent_id")
  );
}

async function membershipFor(store: Store, subId: string | null, membershipId: string | null, intentId: string | null = null): Promise<Membership | null> {
  if (membershipId) {
    const m = await store.get("memberships", membershipId);
    if (m) return m;
  }
  if (subId) {
    const m = await store.findOne("memberships", { stripe_subscription_id: subId });
    if (m) return m;
  }
  if (intentId) return store.findOne("memberships", { checkout_intent_id: intentId });
  return null;
}

/** Thrown when an event arrived before the state it refers to: the route answers 500 and Stripe retries. */
export class RetryLater extends Error {}

const CLAIM_STALE_MS = 5 * 60_000;

/** Best effort: the card fingerprint (one guarantee per person) and the saved card for upsells. */
async function cardDetails(subId: string | null): Promise<{ fingerprint: string | null; paymentMethod: string | null }> {
  const st = stripe();
  if (!st || !subId || subId.startsWith("sub_mock_")) return { fingerprint: null, paymentMethod: null };
  try {
    const sub = await st.subscriptions.retrieve(subId, { expand: ["default_payment_method"] });
    const pm = sub.default_payment_method;
    if (pm && typeof pm === "object") return { fingerprint: pm.card?.fingerprint ?? null, paymentMethod: pm.id };
  } catch (err) {
    console.error("card lookup failed", err);
  }
  return { fingerprint: null, paymentMethod: null };
}

function mapStatus(stripeStatus: string | null, paused: boolean): MembershipStatus | null {
  if (paused) return "paused";
  switch (stripeStatus) {
    case "trialing":
      return "trialing";
    case "active":
      return "active";
    case "past_due":
    case "unpaid":
      return "past_due";
    case "canceled":
      return "canceled";
    case "paused":
      return "paused";
    case "incomplete":
    case "incomplete_expired":
      return "incomplete";
    default:
      return null;
  }
}

export async function handleStripeEvent(store: Store, event: StripeLikeEvent, opts: { expectLivemode?: boolean } = {}): Promise<HandleResult> {
  // L2: a test-mode event on a live key (or the reverse) is never processed.
  if (opts.expectLivemode !== undefined && Boolean(event.livemode) !== opts.expectLivemode) {
    return { duplicate: false, handled: false, summary: "livemode mismatch: ignored" };
  }
  // L2: claim the event. A redelivery while the first attempt is still running is
  // told to come back later instead of running the side effects twice.
  const nowIso = new Date().toISOString();
  let claimed = false;
  try {
    await store.insert("stripe_events", { id: event.id, type: event.type, livemode: Boolean(event.livemode), processed_at: null, claimed_at: nowIso, error: null, summary: null });
    claimed = true;
  } catch {
    const existing = await store.get("stripe_events", event.id);
    if (existing?.processed_at) return { duplicate: true, handled: false, summary: "duplicate" };
    const stale = new Date(Date.now() - CLAIM_STALE_MS).toISOString();
    const [again] = await store.updateWhere("stripe_events", { id: event.id, processed_at: null, claimed_at: null }, { claimed_at: nowIso });
    const [staleClaim] = again ? [again] : await store.updateWhere("stripe_events", { id: event.id, processed_at: null, claimed_at: { lt: stale } }, { claimed_at: nowIso });
    claimed = Boolean(again ?? staleClaim);
  }
  if (!claimed) throw new RetryLater(`event ${event.id} is being processed`);

  let summary = "ignored";
  let handled = false;
  try {
    const obj = event.data.object;
    switch (event.type) {
      case "checkout.session.completed":
      case "checkout.session.async_payment_succeeded": {
        const intentId = s(o(obj.metadata), "intent_id");
        const paid = s(obj, "payment_status");
        if (!intentId) {
          summary = "no intent_id metadata";
          break;
        }
        if (paid && paid !== "paid" && paid !== "no_payment_required") {
          summary = `payment_status=${paid}, waiting`;
          break;
        }
        const card = await cardDetails(idOf(obj.subscription));
        const res = await fulfillCheckoutIntent(store, intentId, {
          stripeCustomerId: idOf(obj.customer),
          stripeSubscriptionId: idOf(obj.subscription),
          stripePaymentIntentId: idOf(obj.payment_intent),
          stripeInvoiceId: idOf(obj.invoice),
          stripePaymentMethodId: card.paymentMethod ?? s(o(obj.metadata), "payment_method") ?? null,
          cardFingerprint: card.fingerprint,
        });
        if (res.membership && idOf(obj.subscription) && !res.membership.stripe_subscription_id) {
          await store.update("memberships", res.membership.id, { stripe_subscription_id: idOf(obj.subscription) });
        }
        handled = true;
        summary = res.alreadyDone ? `intent ${intentId} already fulfilled` : `fulfilled intent ${intentId} → member ${res.member.id}`;
        break;
      }

      case "checkout.session.expired": {
        // Round 8: an abandoned founding checkout gives its spot back right away.
        const intentId = s(o(obj.metadata), "intent_id");
        if (intentId) await releaseFoundingSpot(store, intentId);
        handled = true;
        summary = `checkout expired${intentId ? ` (intent ${intentId}, founding hold released)` : ""}`;
        break;
      }

      case "customer.subscription.updated":
      case "customer.subscription.created": {
        const m = await membershipFor(store, idOf(obj), s(o(obj.metadata), "membership_id"), s(o(obj.metadata), "intent_id"));
        if (!m) {
          // Checkout may not be fulfilled yet (events arrive in any order): retry later.
          if (s(o(obj.metadata), "intent_id")) throw new RetryLater("membership not created yet");
          summary = "membership not found";
          break;
        }
        const pause = o(obj.pause_collection);
        const paused = Boolean(obj.pause_collection) && Object.keys(pause).length > 0;
        const status = mapStatus(s(obj, "status"), paused);
        // M3: the membership item is the recurring one that isn't the partner seat,
        // wherever Stripe puts it in the list.
        const items = (Array.isArray(o(obj.items).data) ? (o(obj.items).data as unknown[]) : []).map(o);
        const partnerId = process.env.STRIPE_PRICE_PARTNER;
        const isPartner = (it: Obj) => {
          const price = o(it.price);
          return (partnerId && s(price, "id") === partnerId) || s(o(price.metadata), "kind") === "partner" || n(price, "unit_amount") === prices.partner;
        };
        const mainItem = items.find((it) => !isPartner(it)) ?? null;
        const itemEnd = mainItem ? n(mainItem, "current_period_end") : items[0] ? n(items[0], "current_period_end") : null;
        const periodEnd = n(obj, "current_period_end") ?? itemEnd;
        const unitAmount = mainItem ? n(o(mainItem.price), "unit_amount") : null;
        const planMeta = mainItem ? s(o(o(mainItem.price).metadata), "plan") : null;
        const patch: Partial<Membership> = {
          cancel_at_period_end: Boolean(obj.cancel_at_period_end),
          stripe_subscription_id: idOf(obj),
        };
        if (status && m.status !== "refunded") patch.status = status;
        if (periodEnd) patch.current_period_end = iso(periodEnd);
        if (n(obj, "trial_end")) patch.trial_end = iso(n(obj, "trial_end"));
        if (paused) patch.paused_until = iso(n(pause, "resumes_at"));
        else if (m.paused_until) patch.paused_until = null;
        if (obj.cancel_at_period_end && !m.canceled_at) patch.canceled_at = new Date().toISOString();
        if (!obj.cancel_at_period_end && m.canceled_at && m.status !== "canceled") patch.canceled_at = null;
        if (unitAmount && unitAmount !== m.price_cents && m.plan !== "gift") patch.price_cents = unitAmount;
        if (planMeta === "essentials" || planMeta === "monthly" || planMeta === "annual") patch.plan = planMeta;
        if (items.length) patch.partner_seat = items.some(isPartner);
        await store.update("memberships", m.id, patch);
        handled = true;
        summary = `synced membership ${m.id} (${patch.status ?? m.status})`;
        break;
      }

      case "customer.subscription.deleted": {
        const m = await membershipFor(store, idOf(obj), s(o(obj.metadata), "membership_id"), s(o(obj.metadata), "intent_id"));
        if (!m) {
          summary = "membership not found";
          break;
        }
        await store.update("memberships", m.id, {
          status: m.status === "refunded" ? "refunded" : "canceled",
          canceled_at: m.canceled_at ?? new Date().toISOString(),
          current_period_end: iso(n(obj, "ended_at")) ?? new Date().toISOString(),
          cancel_at_period_end: false,
        });
        handled = true;
        summary = `membership ${m.id} ended`;
        break;
      }

      case "invoice.paid": {
        const amount = n(obj, "amount_paid") ?? 0;
        const reason = s(obj, "billing_reason");
        const m = await membershipFor(store, invoiceSubscriptionId(obj), invoiceMembershipId(obj), invoiceIntentId(obj));
        if (!m) {
          // C4: Stripe often sends the first invoice before checkout.session.completed.
          // Don't swallow it: answer 500 so Stripe retries once the membership exists.
          if (reason === "subscription_create" || invoiceIntentId(obj)) throw new RetryLater("membership not created yet for this invoice");
          summary = "membership not found for invoice";
          break;
        }
        const pi = invoicePaymentIntent(obj);
        if (reason === "subscription_create") {
          // Paid inside checkout; orders already recorded. Link this membership's first-charge
          // orders to the invoice and payment intent so a refund can find the money.
          const invoiceId = s(obj, "id");
          const own = m.checkout_intent_id ? await store.find("sy_orders", { checkout_intent_id: m.checkout_intent_id }) : await store.find("sy_orders", { membership_id: m.id });
          let linked = 0;
          for (const ord of own) {
            if (ord.stripe_payment_intent && ord.stripe_invoice) continue;
            await store.update("sy_orders", ord.id, { stripe_payment_intent: ord.stripe_payment_intent ?? pi, stripe_invoice: ord.stripe_invoice ?? invoiceId, membership_id: ord.membership_id ?? m.id });
            linked++;
          }
          handled = true;
          summary = `initial invoice linked to ${linked} order(s)`;
          break;
        }
        // Gift credit (H3) is applied by Stripe's customer balance; keep our copy in step.
        const expected = m.price_cents + (m.partner_seat ? prices.partner : 0);
        if ((m.gift_credit_cents ?? 0) > 0 && amount < expected) {
          await store.update("memberships", m.id, { gift_credit_cents: Math.max(0, (m.gift_credit_cents ?? 0) - (expected - amount)) });
        }
        if (amount <= 0) {
          const lines0 = o(obj.lines).data;
          const end0 = Array.isArray(lines0) && lines0[0] ? n(o(o(lines0[0]).period), "end") : null;
          if (end0) await store.update("memberships", m.id, { current_period_end: iso(end0), status: "active" });
          summary = "zero invoice (covered by credit)";
          handled = true;
          break;
        }
        const invoiceId = s(obj, "id");
        if (invoiceId && (await store.findOne("sy_orders", { stripe_invoice: invoiceId }))) {
          summary = "invoice already recorded";
          break;
        }
        const member = await store.get("members", m.member_id);
        await store.insert("sy_orders", {
          member_id: m.member_id,
          membership_id: m.id,
          amount_refunded_cents: 0,
          email: member?.email ?? "",
          offer_code: m.offer_code,
          kind: "membership_charge",
          description: m.plan === "annual" ? "Strong Years annual" : `Strong Years ${m.plan}`,
          amount_cents: amount,
          status: "paid",
          stripe_payment_intent: pi,
          stripe_invoice: invoiceId,
          checkout_intent_id: null,
          processor: m.processor ?? "stripe",
          is_demo: m.is_demo,
        });
        const lines = o(obj.lines).data;
        const periodEnd = Array.isArray(lines) && lines[0] ? n(o(o(lines[0]).period), "end") : null;
        const wasTrial = m.status === "trialing";
        const now = new Date();
        const patch: Partial<Membership> = { status: "active" };
        if (periodEnd) patch.current_period_end = iso(periodEnd);
        if (!m.first_paid_at) {
          patch.first_paid_at = now.toISOString();
          patch.guarantee_until = addDays(now, offerRules.guaranteeDaysTrialArm).toISOString();
        }
        await store.update("memberships", m.id, patch);
        if (wasTrial && member) {
          await trackMetaEvent(
            { name: "Subscribe", eventId: `conv_${m.id}`, sourcePath: "/app", email: member.email, valueCents: amount, contentName: m.offer_code, memberId: member.id, attribution: member.attribution },
            env.siteUrl,
          );
        }
        handled = true;
        summary = `${wasTrial ? "trial converted" : "renewal"} ${moneyExact(amount)} for membership ${m.id}`;
        break;
      }

      case "invoice.payment_failed": {
        const m = await membershipFor(store, invoiceSubscriptionId(obj), invoiceMembershipId(obj), invoiceIntentId(obj));
        if (!m) {
          summary = "membership not found for invoice";
          break;
        }
        await store.update("memberships", m.id, { status: "past_due" });
        const member = await store.get("members", m.member_id);
        if (member) {
          await sendEmail({
            to: member.email,
            template: "dunning_1",
            subject: "Your card didn't go through. You still have access.",
            text: `Hi ${member.first_name}, your payment for Strong Years didn't go through. You keep full access for 7 days while you update your card: ${env.siteUrl}/app/account. Prefer to stop instead? Cancel in two screens at most from the same page.`,
          });
          if (member.sms_opt_in && member.phone) {
            await sendSms(member.phone, `Strong Years: your card didn't go through. Update it in one tap: ${env.siteUrl}/app/account. Reply STOP to opt out.`, "dunning_sms");
          }
        }
        handled = true;
        summary = `membership ${m.id} past_due`;
        break;
      }

      case "charge.refunded": {
        // H12: refunds made anywhere (our flow, the Stripe dashboard, partial) update the
        // orders and, when the membership charge is fully refunded, end the membership.
        const pi = idOf(obj.payment_intent);
        const inv = idOf(obj.invoice);
        let orders = pi ? await store.find("sy_orders", { stripe_payment_intent: pi }) : [];
        if (orders.length === 0 && inv) orders = await store.find("sy_orders", { stripe_invoice: inv });
        if (orders.length === 0) {
          summary = "refund for an unknown payment";
          handled = true;
          break;
        }
        const refundedTotal = n(obj, "amount_refunded") ?? 0;
        const full = Boolean(obj.refunded);
        // Allocate the cumulative refunded amount: our pending refunds first, then membership charges.
        const rank = (x: (typeof orders)[number]) => (x.status === "refund_pending" ? 0 : x.kind === "membership_charge" ? 1 : x.kind === "trial_fee" ? 2 : 3);
        let left = refundedTotal;
        const confirmedPending: typeof orders = [];
        for (const ord of [...orders].sort((a, b) => rank(a) - rank(b))) {
          const covered = full ? ord.amount_cents : Math.max(0, Math.min(ord.amount_cents, left));
          left -= covered;
          const isFull = covered >= ord.amount_cents;
          if (isFull && ord.status === "refund_pending") confirmedPending.push(ord);
          if (ord.status === "disputed") continue;
          await store.update("sy_orders", ord.id, { amount_refunded_cents: covered, status: isFull ? "refunded" : ord.status === "refund_pending" ? "refund_pending" : "paid" });
        }
        const memberships = new Set(orders.filter((x) => x.membership_id && (x.kind === "membership_charge" || x.kind === "trial_fee")).map((x) => x.membership_id!));
        let ended = 0;
        for (const mid of memberships) {
          const own = orders.filter((x) => x.membership_id === mid && (x.kind === "membership_charge" || x.kind === "trial_fee"));
          const fresh = await Promise.all(own.map((x) => store.get("sy_orders", x.id)));
          if (!fresh.every((x) => x?.status === "refunded")) continue;
          const m = await store.get("memberships", mid);
          if (!m || m.status === "refunded") continue;
          const st = stripe();
          if (st && m.stripe_subscription_id && !m.stripe_subscription_id.startsWith("sub_mock_") && ["active", "trialing", "past_due", "paused"].includes(m.status)) {
            await st.subscriptions.cancel(m.stripe_subscription_id).catch((e) => console.error("cancel after refund failed", e));
          }
          await store.update("memberships", mid, { status: "refunded", canceled_at: m.canceled_at ?? new Date().toISOString(), cancel_at_period_end: false, current_period_end: new Date().toISOString() });
          ended++;
        }
        // Our own refund was pending at the bank: now it's confirmed, tell the member.
        for (const ord of confirmedPending) {
          await sendEmail({
            to: ord.email,
            template: "refund_confirmation",
            subject: "Your refund is confirmed",
            text: `Your card company has confirmed the refund of ${moneyExact(ord.amount_cents)}. It usually shows in 5–10 days. You won't be charged again.`,
          });
        }
        summary = `refund ${full ? "(full)" : `(partial ${moneyExact(refundedTotal)})`} on ${orders.length} order(s); ${ended} membership(s) ended`;
        handled = true;
        break;
      }

      case "charge.dispute.created": {
        // H12: a dispute stops billing at once and flags the member for a person.
        const pi = idOf(obj.payment_intent);
        let orders = pi ? await store.find("sy_orders", { stripe_payment_intent: pi }) : [];
        if (orders.length === 0 && idOf(o(obj.charge).invoice)) orders = await store.find("sy_orders", { stripe_invoice: idOf(o(obj.charge).invoice)! });
        for (const ord of orders) await store.update("sy_orders", ord.id, { status: "disputed" });
        const mids = new Set(orders.map((x) => x.membership_id).filter((x): x is string => Boolean(x)));
        for (const mid of mids) {
          const m = await store.get("memberships", mid);
          if (!m) continue;
          const st = stripe();
          if (st && m.stripe_subscription_id && !m.stripe_subscription_id.startsWith("sub_mock_") && !["canceled", "refunded", "expired"].includes(m.status)) {
            await st.subscriptions.cancel(m.stripe_subscription_id).catch((e) => console.error("cancel after dispute failed", e));
          }
          if (!["refunded", "expired"].includes(m.status)) {
            await store.update("memberships", mid, { status: "canceled", canceled_at: new Date().toISOString(), cancel_at_period_end: false, current_period_end: new Date().toISOString() });
          }
        }
        const memberId = orders[0]?.member_id ?? null;
        const t = await store.insert("support_tickets", { member_id: memberId, email: orders[0]?.email ?? null, reason: "dispute", message: `Dispute on ${pi ?? "unknown payment"} (${orders.length} order(s)). Subscription cancelled.`, status: "open" });
        await alertOnCall("Chargeback / dispute opened", `ticket-${t.id}`);
        summary = `dispute recorded on ${orders.length} order(s); ${mids.size} membership(s) cancelled`;
        handled = true;
        break;
      }
    }
    await store.update("stripe_events", event.id, { processed_at: new Date().toISOString(), summary });
    return { duplicate: false, handled, summary };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    // Release the claim so Stripe's retry can run it.
    await store.update("stripe_events", event.id, { error: message, claimed_at: null });
    throw err;
  }
}

/** Used by the account page to describe the next charge. */
export function describeNextCharge(m: Membership): string | null {
  if (!m.current_period_end || m.cancel_at_period_end || m.status === "canceled") return null;
  return `${moneyExact(m.price_cents + (m.partner_seat ? 800 : 0))} on ${formatDate(m.current_period_end, env.displayTimeZone)}`;
}
