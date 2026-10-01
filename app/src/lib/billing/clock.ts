/**
 * Scheduled billing work:
 *  - 48-hour pre-charge reminders (email; SMS once enabled) before EVERY charge:
 *    trial conversions and every monthly renewal (AUDIT_BUSINESS F10, AUDIT_CODE M7);
 *    30-day notice for annual plans.
 *  - A yearly notice for monthly members on each anniversary (California ARL, F11).
 *  - In mock mode only: a "billing clock" that emits the invoice/subscription events
 *    Stripe would send (trial conversions, renewals, period ends), so the demo and the
 *    admin KPIs behave like a real account. With real Stripe, Stripe does this itself.
 */
import { env, offerRules } from "../config";
import type { Store } from "../db/store";
import type { Membership } from "../db/types";
import { addMonths, formatDate, moneyExact } from "../pricing";
import { sendEmail, sendSms } from "../notify";
import { sendPushToMember } from "../push";
import { handleStripeEvent } from "./webhook";
import { shopifyConfig } from "./shopify";

/**
 * Shopify-mode re-check (INTEGRATION.md §5). A cancellation or pause made on Shopify's
 * account page never reaches us as an event (contract webhooks fire only for the owning
 * app), so before any reminder we re-read what the ORDER data says and, if it can't be
 * sure, we word the email conditionally instead of asserting a charge.
 *   - the newest membership charge order must still be paid (a refund or admin cancel
 *     already ended the row, but belt and braces);
 *   - a membership whose period ended without a renewal order is lapsing, not renewing:
 *     no reminder;
 *   - we can never see a cancel/pause made in Shopify → "unsure" → conditional wording.
 */
export type RenewalCertainty = "certain" | "unsure" | "skip";
export async function renewalCertainty(store: Store, m: Membership, now: Date): Promise<RenewalCertainty> {
  if (m.processor !== "shopify") return "certain";
  const charges = await store.find("sy_orders", { membership_id: m.id, kind: "membership_charge" }, { orderBy: "created_at", desc: true });
  const last = charges[0];
  if (!last || last.status === "refunded") return "skip";
  if (m.current_period_end && new Date(m.current_period_end).getTime() <= now.getTime()) return "skip";
  return shopifyConfig.ownsContracts() && m.shopify_contract_id ? "certain" : "unsure";
}

/** Every upcoming charge gets a reminder; the decision no longer depends on order history (M7). */
export function needsPreChargeReminder(m: Membership): "pre_charge_48h" | "annual_30d" | null {
  if (m.cancel_at_period_end || m.status === "paused" || m.status === "canceled" || m.status === "refunded" || m.status === "expired") return null;
  if (m.plan === "gift" || m.interval === "none") return null;
  if (m.interval === "year") return "annual_30d";
  if (m.status === "trialing" || m.status === "active" || m.status === "past_due") return "pre_charge_48h";
  return null;
}

/** Cell B: the first renewal is the first full-price charge; after that the wording is the ordinary one. */
function charges_after_first(count: number): boolean {
  return count > 1;
}

/** The most recent yearly anniversary of a monthly membership, if it has had one (F11). */
export function lastAnniversary(m: Pick<Membership, "first_paid_at" | "created_at">, now: Date): Date | null {
  const start = new Date(m.first_paid_at ?? m.created_at);
  let years = now.getUTCFullYear() - start.getUTCFullYear();
  const candidate = (y: number) => addMonths(start, 12 * y);
  if (candidate(years) > now) years -= 1;
  return years >= 1 ? candidate(years) : null;
}

export async function runReminders(store: Store, now = new Date()): Promise<{ sent: number; checked: number }> {
  const horizonMs = offerRules.reminderHoursBeforeCharge * 3_600_000;
  const annualHorizonMs = offerRules.annualReminderDays * 86_400_000;
  const candidates = await store.find("memberships", {
    status: { in: ["trialing", "active"] },
    current_period_end: { gt: now.toISOString(), lte: new Date(now.getTime() + annualHorizonMs).toISOString() },
  });
  let sent = 0;
  for (const m of candidates) {
    const chargeAt = m.current_period_end!;
    const kind = needsPreChargeReminder(m);
    if (!kind) continue;
    const ms = new Date(chargeAt).getTime() - now.getTime();
    if (kind === "pre_charge_48h" && ms > horizonMs) continue;
    const dup = await store.findOne("reminders", { membership_id: m.id, kind, charge_at: chargeAt });
    if (dup) continue;
    const member = await store.get("members", m.member_id);
    if (!member) continue;
    const certainty = await renewalCertainty(store, m, now);
    if (certainty === "skip") continue;
    const unsure = certainty === "unsure";
    const manageUrl = unsure ? shopifyConfig.customerAccountUrl() : `${env.siteUrl}/app/account`;
    // L8: the member's own time zone for the date they'll see on their statement.
    const date = formatDate(chargeAt, member.timezone || env.displayTimeZone);
    const gross = m.price_cents + (m.partner_seat ? 800 : 0);
    const price = moneyExact(gross);
    const credit = Math.min(m.gift_credit_cents ?? 0, gross);
    const creditLine = credit > 0 ? `Your gift credit covers ${moneyExact(credit)} of it, so ${moneyExact(gross - credit)} will be charged to your card.` : "";
    const sessions = await store.count("practice_logs", { member_id: m.member_id });
    const cancelLink = unsure ? manageUrl : `${env.siteUrl}/app/account/cancel`;

    if (kind === "annual_30d") {
      await sendEmail({
        to: member.email,
        template: "D_annual_renewal_notice",
        subject: unsure ? `If your yearly Strong Years membership is still active, it renews on ${date}` : `Your yearly Strong Years membership renews on ${date}`,
        text: unsure
          ? `If your yearly plan is still active, it renews on ${date} for ${price}. If you already cancelled it on your account page, nothing happens and you can ignore this. To check, cancel or switch to monthly: ${manageUrl}. This year you did ${sessions} sessions.`
          : `Your yearly plan renews on ${date} for ${price}. To keep it, do nothing. To cancel or switch to monthly: ${env.siteUrl}/app/account. This year you did ${sessions} sessions.`,
      });
    } else {
      const trial = m.status === "trialing";
      const firstRenewalAfterStarter = (m.offer_code ?? "").startsWith("bundle_m12") && !charges_after_first(await store.count("sy_orders", { membership_id: m.id, kind: "membership_charge" }));
      await sendEmail({
        to: member.email,
        template: "C_pre_charge_48h",
        subject: trial ? `${sessions} sessions done. Your membership continues on ${date}.` : unsure ? `A quick, honest reminder: if your membership is still active, the next charge is ${date}` : `A quick, honest reminder: your next charge is ${date}`,
        text: [
          `Hi ${member.first_name}, a quick, honest reminder.`,
          trial
            ? `Your 7-day trial of Strong Years ends on ${date}. If you'd like to continue, you don't need to do anything: we'll charge ${price} on ${date} and then monthly until you cancel.`
            : unsure
              ? `${firstRenewalAfterStarter ? `Your $12 starter month ends and, if` : `If`} your Strong Years membership is still active, it renews on ${date} at ${price}, then monthly until you cancel. If you already cancelled or paused it on your account page, nothing is charged and you can ignore this email.`
              : `${firstRenewalAfterStarter ? `Your $12 starter month ends and your` : `Your`} Strong Years membership renews on ${date} at ${price}, then monthly until you cancel.`,
          creditLine,
          unsure ? `To check, pause or cancel (no call needed): ${cancelLink}` : `If you'd rather not continue, cancel here in two screens at most: ${cancelLink}`,
          `So far you've done ${sessions} session${sessions === 1 ? "" : "s"}.`,
        ]
          .filter(Boolean)
          .join("\n\n"),
      });
      // Web push copy of the reminder on any device the member opted in (no amounts in a lock-screen banner).
      await sendPushToMember(store, member, { title: trial ? "Your trial ends soon" : "Your membership renews soon", body: `On ${date}. Details and cancel options are in your account.`, url: "/app/account", tag: "renewal" }, "push_pre_charge");
      if (member.sms_opt_in && member.phone) {
        await sendSms(
          member.phone,
          `Strong Years: your ${trial ? "trial ends" : "membership renews"} ${date}. Then ${price}/mo until you cancel. To keep going, do nothing. To cancel (2 screens max): ${cancelLink} or reply CANCEL. Reply STOP to opt out.`,
          "S6_pre_charge",
        );
      }
    }
    await store.insert("reminders", { membership_id: m.id, kind, charge_at: chargeAt, sent_at: now.toISOString() });
    sent++;
  }
  sent += await runAnnualNotices(store, now);
  return { sent, checked: candidates.length };
}

/**
 * F11: California's ARL (as amended July 2025) wants a yearly reminder for every
 * automatic renewal, monthly ones included. We send it to all monthly members on
 * each anniversary of their first charge.
 */
export async function runAnnualNotices(store: Store, now = new Date()): Promise<number> {
  const oneYearAgo = addMonths(now, -12).toISOString();
  const rows = await store.find("memberships", { interval: "month", status: { in: ["active", "past_due", "trialing"] }, first_paid_at: { lte: oneYearAgo } });
  let sent = 0;
  for (const m of rows) {
    if (m.cancel_at_period_end || m.plan === "gift") continue;
    const at = lastAnniversary(m, now);
    if (!at || now.getTime() - at.getTime() > 7 * 86_400_000) continue; // only in the week after the anniversary
    const key = at.toISOString();
    if (await store.findOne("reminders", { membership_id: m.id, kind: "ca_annual_notice", charge_at: key })) continue;
    const member = await store.get("members", m.member_id);
    if (!member) continue;
    const price = moneyExact(m.price_cents + (m.partner_seat ? 800 : 0));
    const next = m.current_period_end ? formatDate(m.current_period_end, member.timezone || env.displayTimeZone) : null;
    const sessions = await store.count("practice_logs", { member_id: m.member_id });
    await sendEmail({
      to: member.email,
      template: "ca_annual_notice",
      subject: "Your yearly Strong Years membership notice",
      text: [
        `Hi ${member.first_name}, once a year we send everyone this plain summary of their membership.`,
        `Plan: Strong Years, monthly. Price: ${price} a month, charged automatically until you cancel.${next ? ` Next charge: ${next}.` : ""}`,
        `How to cancel: online in two screens at most at ${env.siteUrl}/app/account/cancel, or email us (a person reads it within one business day).`,
        `This year you did ${sessions} session${sessions === 1 ? "" : "s"}.`,
      ].join("\n\n"),
    });
    await store.insert("reminders", { membership_id: m.id, kind: "ca_annual_notice", charge_at: key, sent_at: now.toISOString() });
    sent++;
  }
  return sent;
}

/**
 * Round 5 audit: Shopify memberships whose paid period ended with no renewal order (cancelled, paused or
 * dunned out on Shopify's side, none of which sends us a webhook on the launch path) are expired here once
 * the float (SHOPIFY_GRACE_DAYS) has passed. A later renewal order revives the row (shopifyWebhook renewalMembership).
 */
export async function runShopifyLapses(store: Store, now = new Date()): Promise<number> {
  const floatDays = (() => {
    const n = Number((process.env.SHOPIFY_GRACE_DAYS ?? "").trim() || "7");
    return Number.isFinite(n) && n >= 0 && n <= 30 ? n : 7;
  })();
  const cutoff = new Date(now.getTime() - floatDays * 86_400_000).toISOString();
  const rows = await store.find("memberships", { processor: "shopify", status: { in: ["active", "past_due", "canceled", "paused"] }, current_period_end: { lte: cutoff } });
  let n = 0;
  for (const m of rows) {
    if (m.plan === "gift" || !m.current_period_end) continue;
    if (m.grace_until && new Date(m.grace_until).getTime() > now.getTime()) continue;
    const [row] = await store.updateWhere("memberships", { id: m.id, status: m.status }, { status: "expired", canceled_at: m.canceled_at ?? now.toISOString(), cancel_at_period_end: false });
    if (!row) continue;
    n++;
    const member = await store.get("members", m.member_id);
    if (!member) continue;
    await sendEmail({
      to: member.email,
      template: "SH_membership_ended",
      subject: "Your Strong Years membership has ended",
      text: [
        `${member.first_name}, your membership's last paid period ended on ${formatDate(m.current_period_end, member.timezone || env.displayTimeZone)} and no renewal payment came through, so the members area is closed for now. Nothing further is charged.`,
        `If you cancelled or paused it on your account page, that's all working as it should. If you meant to keep it and a payment failed, update your card on your account page and the next successful payment opens everything again: ${shopifyConfig.customerAccountUrl()}`,
        "Your downloaded books and printables are yours to keep.",
      ].join("\n\n"),
    });
  }
  return n;
}

/** Mock-mode billing clock. Never used when STRIPE_SECRET_KEY is set. */
export async function runMockBillingClock(store: Store, now = new Date()): Promise<{ events: number }> {
  const due = await store.find("memberships", {
    status: { in: ["trialing", "active", "paused", "past_due"] },
  });
  let events = 0;
  for (const m of due) {
    if (m.stripe_subscription_id && !m.stripe_subscription_id.startsWith("sub_mock_")) continue;
    const sub = m.stripe_subscription_id ?? `sub_mock_${m.id.slice(0, 8)}`;
    if (m.status === "paused") {
      if (m.paused_until && new Date(m.paused_until) <= now) {
        await store.update("memberships", m.id, { status: "active", paused_until: null, current_period_end: now.toISOString() });
        events++;
      }
      continue;
    }
    if (!m.current_period_end || new Date(m.current_period_end) > now) continue;
    if (m.cancel_at_period_end) {
      await handleStripeEvent(store, {
        id: `evt_mock_${crypto.randomUUID()}`,
        type: "customer.subscription.deleted",
        data: { object: { id: sub, metadata: { membership_id: m.id }, ended_at: Math.floor(now.getTime() / 1000) } },
      });
      events++;
      continue;
    }
    const nextEnd = addMonths(new Date(m.current_period_end), m.interval === "year" ? 12 : 1);
    const gross = m.price_cents + (m.partner_seat ? 800 : 0);
    const amountPaid = Math.max(0, gross - (m.gift_credit_cents ?? 0));
    await handleStripeEvent(store, {
      id: `evt_mock_${crypto.randomUUID()}`,
      type: "invoice.paid",
      data: {
        object: {
          id: `in_mock_${crypto.randomUUID().slice(0, 12)}`,
          billing_reason: "subscription_cycle",
          amount_paid: amountPaid,
          payment_intent: `pi_mock_${crypto.randomUUID().slice(0, 12)}`,
          parent: { subscription_details: { subscription: sub, metadata: { membership_id: m.id } } },
          lines: { data: [{ period: { end: Math.floor(nextEnd.getTime() / 1000) } }] },
        },
      },
    });
    events++;
  }
  return { events };
}
