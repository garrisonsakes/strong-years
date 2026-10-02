/**
 * Shopify webhooks → access in our database. Store-parameterised (unit tested
 * without Next). The route (app/api/webhooks/shopify) verifies the HMAC first.
 *
 * Idempotency, in layers:
 *  1. the delivery: one shopify_webhooks row per X-Shopify-Webhook-Id (a retry of the
 *     same delivery is a "duplicate");
 *  2. the business key, because the webhook id header is not covered by the HMAC:
 *     order lines are unique on (shopify_line_id, kind), a membership on its origin
 *     order and contract, refunds mark lines that are already marked, contract events
 *     apply only with a higher revision_id, billing attempts only with a higher id.
 *     So the same signed body replayed under a new webhook id changes nothing.
 *
 * Out-of-order delivery: a contract or billing event that arrives before the order
 * that created the membership is "deferred" (the route answers 503, Shopify retries);
 * an older contract revision or billing attempt arriving after a newer one is ignored.
 */
import { env } from "../config";
import type { Store } from "../db/store";
import type { Member, Membership, Order, ShopifyProductRow } from "../db/types";
import { defaultMember, findMemberByEmail, normalizeEmail } from "../members";
import { addDays, addMonths, formatDate, moneyExact } from "../pricing";
import { alertOnCall, sendEmail } from "../notify";
import { isCheckoutOpen } from "../launch";
import { createGift } from "../gifts";
import { creditAffiliateOrder } from "../affiliates";
import { logConversion } from "../offers/experiments";
import { linkWaitlistToMember } from "../waitlist";
import { issueMagicLink } from "../auth/verification";
import { catalog, cartContextFromAttributes, consentMatchesCharge, idGreater, matchLine, orderDiscountCodes, shopifyAdmin, shopifyConfig, shopifyId, type ShopifyAdmin } from "./shopify";

/**
 * The webhook contract (shopify/config/webhook-topics.json is the fixture both sides are tested against).
 * CORE topics fire store-wide for any app holding the scope and are the ONLY source of membership truth:
 * orders/paid (initial + every Shopify Subscriptions renewal order), refunds/create, orders/cancelled,
 * customers/update|delete, inventory_levels/update (founding counter), app/uninstalled.
 * ENRICHMENT topics require read_own_subscription_contracts and fire only for contracts owned by the subscribing
 * app (shopify.dev WebhookSubscriptionTopic). On the launch path Shopify Subscriptions owns them, so these never
 * arrive; when they do (SUBSCRIPTION_ENGINE=app) they only refine status, they never grant or revoke access on
 * their own. There is no "orders/refunded" Admin API topic (refunds/create is the refund event).
 */
export const SHOPIFY_TOPICS_CORE = [
  "orders/paid",
  "orders/cancelled",
  "refunds/create",
  "disputes/create",
  "disputes/update",
  "customers/update",
  "customers/delete",
  "inventory_levels/update",
  "app/uninstalled",
] as const;
export const SHOPIFY_TOPICS_ENRICHMENT = [
  "subscription_contracts/create",
  "subscription_contracts/update",
  "subscription_contracts/activate",
  "subscription_contracts/pause",
  "subscription_contracts/cancel",
  "subscription_contracts/expire",
  "subscription_contracts/fail",
  "subscription_billing_attempts/success",
  "subscription_billing_attempts/failure",
] as const;
export const SHOPIFY_TOPICS = [...SHOPIFY_TOPICS_CORE, ...SHOPIFY_TOPICS_ENRICHMENT] as const;
export type ShopifyTopic = (typeof SHOPIFY_TOPICS)[number];

export function isShopifyTopic(t: string): t is ShopifyTopic {
  return (SHOPIFY_TOPICS as readonly string[]).includes(t);
}

export const GUARANTEE_DAYS = 14;
const WEBHOOK_ID = /^[A-Za-z0-9-]{8,80}$/;

export interface ShopifyDelivery {
  webhookId: string;
  topic: string;
  payload: unknown;
  now?: Date;
  admin?: ShopifyAdmin;
}

export type HandleStatus = "processed" | "duplicate" | "ignored" | "deferred";
export interface HandleResult {
  status: HandleStatus;
  summary: string;
}

type Json = Record<string, unknown>;
const obj = (v: unknown): Json => (v && typeof v === "object" && !Array.isArray(v) ? (v as Json) : {});
const arr = (v: unknown, max = 100): unknown[] => (Array.isArray(v) ? v.slice(0, max) : []);
const text = (v: unknown, max = 200): string => (typeof v === "string" ? v.slice(0, max) : "");

/** "12.00" × qty − discount, in cents; null if it doesn't look like money. */
function cents(v: unknown): number | null {
  const n = typeof v === "number" ? v : typeof v === "string" && /^\d{1,7}(\.\d{1,2})?$/.test(v.trim()) ? Number(v) : NaN;
  if (!Number.isFinite(n) || n < 0 || n > 100_000) return null;
  return Math.round(n * 100);
}

function date(v: unknown, fallback: Date): Date {
  if (typeof v !== "string" || v.length > 40) return fallback;
  const t = Date.parse(v);
  return Number.isNaN(t) ? fallback : new Date(t);
}

function addInterval(d: Date, interval: Membership["interval"]): Date {
  return interval === "year" ? addMonths(d, 12) : addMonths(d, 1);
}

async function ticket(store: Store, member: Pick<Member, "id" | "email"> | null, message: string, alert = true) {
  const t = await store.insert("support_tickets", { member_id: member?.id ?? null, email: member?.email ?? null, reason: "shopify_review", message: message.slice(0, 500), status: "open" });
  if (alert) await alertOnCall("Shopify order needs a person", `ticket-${t.id}`);
}

export async function handleShopifyWebhook(store: Store, d: ShopifyDelivery): Promise<HandleResult> {
  const now = d.now ?? new Date();
  if (!WEBHOOK_ID.test(d.webhookId)) return { status: "ignored", summary: "missing or malformed webhook id" };
  if (!isShopifyTopic(d.topic)) return { status: "ignored", summary: `topic not handled: ${d.topic.slice(0, 60)}` };
  try {
    await store.insert("shopify_webhooks", { id: d.webhookId, topic: d.topic, status: "processing", summary: null, processed_at: null });
  } catch {
    return { status: "duplicate", summary: "already received" };
  }
  let result: HandleResult;
  try {
    result = await dispatch(store, d.topic, obj(d.payload), now, d.admin ?? shopifyAdmin());
  } catch (err) {
    await store.remove("shopify_webhooks", { id: d.webhookId }); // let Shopify retry
    throw err;
  }
  if (result.status === "deferred") {
    await store.remove("shopify_webhooks", { id: d.webhookId });
    return result;
  }
  await store.update("shopify_webhooks", d.webhookId, { status: result.status === "processed" ? "processed" : "ignored", summary: result.summary.slice(0, 300), processed_at: now.toISOString() });
  return result;
}

async function dispatch(store: Store, topic: ShopifyTopic, p: Json, now: Date, admin: ShopifyAdmin): Promise<HandleResult> {
  switch (topic) {
    case "orders/paid":
      return orderPaid(store, p, now, admin);
    case "orders/cancelled":
      return orderCancelled(store, p, now);
    case "refunds/create":
      return refunded(store, p, now, admin);
    case "disputes/create":
    case "disputes/update":
      return dispute(store, p, now);
    case "customers/delete":
      return customerDelete(store, p);
    case "subscription_contracts/create":
    case "subscription_contracts/update":
    case "subscription_contracts/activate":
    case "subscription_contracts/pause":
    case "subscription_contracts/cancel":
    case "subscription_contracts/expire":
    case "subscription_contracts/fail":
      return contractEvent(store, topic, p, now);
    case "subscription_billing_attempts/success":
      return billingAttempt(store, p, true, now);
    case "subscription_billing_attempts/failure":
      return billingAttempt(store, p, false, now);
    case "customers/update":
      return customerUpdate(store, p);
    case "app/uninstalled":
      await ticket(store, null, "The Shopify app was uninstalled from the store. Webhooks have stopped: new orders won't provision access until it's reinstalled. Existing members keep their access.");
      return { status: "processed", summary: "app uninstalled: on-call alerted" };
    case "inventory_levels/update":
      return inventoryUpdate(store, p, admin);
  }
}

/* ---------------- orders/paid ---------------- */

interface MappedLine {
  row: ShopifyProductRow;
  lineId: string;
  amountCents: number;
  quantity: number;
  properties: Record<string, string>;
}

function lineProperties(li: Json): Record<string, string> {
  const out: Record<string, string> = {};
  for (const p of arr(li.properties, 20)) {
    const { name, value } = obj(p);
    if (typeof name === "string" && typeof value === "string" && name.length <= 40) out[name.toLowerCase().replace(/^_/, "").replace(/[\s-]+/g, "_")] = value.slice(0, 300);
  }
  return out;
}

async function memberForOrder(store: Store, email: string, firstName: string, customerId: string | null, attribution: Member["attribution"]): Promise<Member> {
  const existing = await findMemberByEmail(store, email);
  if (existing) {
    const patch: Partial<Member> = {};
    if (customerId && !existing.shopify_customer_id && !(await store.findOne("members", { shopify_customer_id: customerId }))) patch.shopify_customer_id = customerId;
    if (attribution && !existing.attribution) patch.attribution = attribution;
    else if (attribution?.last_touch && existing.attribution) patch.attribution = { ...existing.attribution, last_touch: attribution.last_touch };
    if (attribution?.ad_opt_out && !existing.ad_opt_out) patch.ad_opt_out = true;
    return Object.keys(patch).length ? ((await store.update("members", existing.id, patch)) ?? existing) : existing;
  }
  try {
    return await store.insert("members", {
      ...defaultMember(email, firstName),
      stripe_customer_id: null,
      attribution,
      ad_opt_out: Boolean(attribution?.ad_opt_out),
      shopify_customer_id: customerId && !(await store.findOne("members", { shopify_customer_id: customerId })) ? customerId : null,
    });
  } catch {
    const again = await findMemberByEmail(store, email);
    if (again) return again;
    throw new Error("could not create member");
  }
}

function planFor(row: ShopifyProductRow): Membership["plan"] {
  return row.entitlement === "annual" ? "annual" : row.entitlement === "essentials" ? "essentials" : "monthly";
}

async function orderPaid(store: Store, p: Json, now: Date, admin: ShopifyAdmin): Promise<HandleResult> {
  const orderId = shopifyId(p.id);
  if (!orderId) return { status: "ignored", summary: "order without id" };
  const customer = obj(p.customer);
  const email = normalizeEmail(text(p.email, 254) || text(p.contact_email, 254) || text(customer.email, 254));
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    await ticket(store, null, `Shopify order ${orderId} has no usable email, so nobody got access. Find the buyer in Shopify.`);
    return { status: "ignored", summary: "no email" };
  }
  const rows = await catalog(store);
  const ctx = cartContextFromAttributes(p.note_attributes);
  const codes = orderDiscountCodes(p);
  const mapped: MappedLine[] = [];
  const unmapped: string[] = [];
  for (const raw of arr(p.line_items, 50)) {
    const li = obj(raw);
    const alloc = obj(li.selling_plan_allocation);
    const plan = shopifyId(obj(alloc.selling_plan).id) ?? shopifyId(alloc.selling_plan_id);
    const row = matchLine(rows, shopifyId(li.variant_id), plan, codes);
    const lineId = shopifyId(li.id);
    const unit = cents(li.price);
    const qty = typeof li.quantity === "number" && li.quantity > 0 && li.quantity < 100 ? li.quantity : 1;
    const discount = cents(li.total_discount) ?? 0;
    if (!row || !lineId || unit === null) {
      unmapped.push(text(li.title, 60) || String(li.variant_id ?? "?"));
      continue;
    }
    mapped.push({ row, lineId, amountCents: Math.max(0, unit * qty - discount), quantity: qty, properties: lineProperties(li) });
  }
  if (unmapped.length && mapped.length === 0) {
    await ticket(store, { id: "", email }, `Shopify order ${orderId}: no line maps to a Strong Years product (${unmapped.join(", ")}). Add the variant/selling plan to shopify_products if it should grant access.`, false);
    return { status: "ignored", summary: "no Strong Years products" };
  }
  const firstName = (text(customer.first_name, 60) || text(obj(p.billing_address).first_name, 60) || "Friend").replace(/[<>\u0000-\u001F]/g, "");
  const member = await memberForOrder(store, email, firstName, shopifyId(customer.id), ctx.attribution);
  if (unmapped.length) await ticket(store, member, `Shopify order ${orderId}: lines not in the catalog (${unmapped.join(", ")}). Mapped lines were provisioned.`, false);
  const paidAt = date(p.processed_at ?? p.created_at, now);
  const renewal = /subscription/i.test(text(p.source_name, 60));
  if (!renewal && !(await isCheckoutOpen(store, now))) {
    await ticket(store, member, `Shopify order ${orderId} was paid while LAUNCH_MODE is prelaunch. Access was provisioned (the money was taken). Keep the store password-protected or the products unpublished until launch.`);
  }

  let recorded = 0;
  let membershipId: string | null = null;
  let newMembership: Membership | null = null;
  let ebookCents = 0;
  for (const line of mapped) {
    const kind: Order["kind"] = line.row.entitlement === "ebook" ? "front_end" : line.row.entitlement === "bump" ? "bump" : line.row.entitlement === "gift" ? "gift" : "membership_charge";
    let membership: Membership | null = null;
    if (kind === "membership_charge") {
      membership = renewal ? await renewalMembership(store, member, line.row) : await initialMembership(store, member, line.row, orderId, ctx.cell, paidAt, now);
      if (!membership) {
        await ticket(store, member, `Shopify renewal order ${orderId} (${line.row.sku}) has no matching membership.`);
        continue;
      }
      // R5-8: the consent record must match the charge. A starter page records "12.00|25.00" (the code price and
      // the plan price a returning customer pays once STARTER12 is refused), so both are honest outcomes; anything
      // else is reviewed by a person before the member is billed again.
      const consent = renewal ? "match" : consentMatchesCharge(ctx, line.amountCents);
      if (consent === "mismatch") {
        await ticket(store, member, `Shopify order ${orderId}: the consent box showed ${(ctx.consentPricesCents ?? []).map((c) => moneyExact(c)).join(" or ")} but the membership line charged ${moneyExact(line.amountCents)} (${line.row.sku}). Check the order and the discount before the first renewal; refund the difference if the page misled.`);
      } else if (consent === "unknown") {
        // R5-10: a no-JS checkout (or an older theme) recorded no consent price; a person confirms the terms were shown.
        await ticket(store, member, `Shopify order ${orderId}: no consent-price record on the membership line (${line.row.sku}, ${moneyExact(line.amountCents)}; a no-JS checkout?). Confirm the auto-renewal terms were shown before the first renewal.`, false);
      }
      if (line.quantity > 1) await ticket(store, member, `Shopify order ${orderId}: membership line ${line.row.sku} has quantity ${line.quantity}. One seat per contract: refund the extra ${moneyExact(line.amountCents - Math.round(line.amountCents / line.quantity))} and fix the contract in Apps → Subscriptions.`);
    }
    // A renewal order IS the renewal (billing-attempt webhooks never reach us on the launch path): it extends the
    // paid-through date by one period from the later of today and the current period end, and clears any grace.
    if (membership && renewal && !(await store.findOne("sy_orders", { shopify_line_id: line.lineId, kind: "membership_charge" }))) {
      const converting = membership.status === "trialing";
      // CANON UPDATE 6: the day-7 charge of a trial is its first real membership payment: the paid month runs from the
      // charge date, the 14-day money-back window starts now (not at the $0 checkout), the row becomes active.
      // Otherwise the renewal extends from the later of today and the current period end.
      const base = !converting && membership.current_period_end && new Date(membership.current_period_end).getTime() > paidAt.getTime() ? new Date(membership.current_period_end) : paidAt;
      await store.update("memberships", membership.id, {
        current_period_end: addInterval(base, membership.interval).toISOString(),
        grace_until: null,
        // "expired" here means the period lapsed with no renewal order (runShopifyLapses); the money came, so it's back.
        status: ["past_due", "paused", "canceled", "expired", "trialing"].includes(membership.status) ? "active" : membership.status,
        cancel_at_period_end: false,
        canceled_at: null,
        ...(converting ? { first_paid_at: paidAt.toISOString(), guarantee_until: addDays(paidAt, GUARANTEE_DAYS).toISOString(), price_cents: line.amountCents > 0 ? line.amountCents : membership.price_cents } : {}),
      });
      if (converting && line.amountCents !== (membership.price_cents ?? 0)) {
        await ticket(store, member, `Shopify order ${orderId}: the first charge after the 7-day trial was ${moneyExact(line.amountCents)} but the trial page promised ${moneyExact(membership.price_cents)} (${line.row.sku}). Check the selling plan's price; refund the difference if the page misled.`);
      }
      // Founding seat ledger rule 2: a renewal order consumed a seat it must not keep (renewals never count).
      if (line.row.entitlement === "founding" && line.row.inventory_item_id) await giveSeatBack(store, admin, line.row.inventory_item_id, `strongyears://seat-ledger/renewal/${orderId}`, orderId);
    }
    // refunds/create got here first (a retried delivery): record the line as refunded, grant nothing for it.
    const early = await store.findOne("shopify_early_refunds", { shopify_line_id: line.lineId });
    let order: Order;
    try {
      order = await store.insert("sy_orders", {
        member_id: member.id,
        email,
        offer_code: line.row.sku,
        kind,
        description: line.row.title,
        amount_cents: line.amountCents,
        status: early ? "refunded" : "paid",
        stripe_payment_intent: null,
        stripe_invoice: null,
        checkout_intent_id: null,
        membership_id: membership?.id ?? null,
        amount_refunded_cents: early ? line.amountCents : 0,
        processor: "shopify",
        shopify_order_id: orderId,
        shopify_line_id: line.lineId,
        is_demo: false,
        created_at: paidAt.toISOString(),
      });
    } catch {
      continue; // this line was recorded before (replay under a new webhook id)
    }
    if (early) {
      if (membership && !renewal && kind === "membership_charge") {
        await store.update("memberships", membership.id, { status: "refunded", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString(), grace_until: null });
      }
      await ticket(store, member, `Shopify order ${orderId}: the refund for line ${line.lineId} arrived before the paid order. Nothing was granted for it; make sure the subscription contract is cancelled in Apps → Subscriptions.`, false);
      recorded++;
      continue;
    }
    recorded++;
    if (kind === "front_end" || line.row.includes_ebook) ebookCents += kind === "front_end" ? order.amount_cents : 0;
    if (membership && !renewal) {
      membershipId = membership.id;
      newMembership = membership;
    }
    if (kind === "gift") await provisionGift(store, member, line, orderId);
  }
  if (recorded === 0) return { status: "ignored", summary: `order ${orderId} already recorded` };

  await linkWaitlistToMember(store, (await store.get("members", member.id)) ?? member, ctx.attribution, now);
  if (!renewal) await conversions(store, member, orderId, ebookCents, newMembership, ctx.attribution);
  if (newMembership) await welcome(store, member, newMembership, mapped.some((l) => l.row.entitlement === "ebook"));
  else if (!renewal && mapped.some((l) => l.row.entitlement === "ebook")) await booksWelcome(store, member);
  // Affiliates (30% x 12 months, 60-day link window, no self-referral). Never throws, never blocks access.
  await creditAffiliateOrder(store, { memberId: member.id, email, shopifyOrderId: orderId, discountCodes: codes, attribution: ctx.attribution, renewal, paidAt });
  // MONETIZATION_ENGINE.md §5: first-purchase lines → the offer attribution table (RPV / RPC / arm readout). Never throws.
  if (!renewal) {
    const lt = ctx.attribution?.last_touch ?? ctx.attribution;
    const channel = (lt?.utm_medium ?? lt?.utm_source ?? "direct").slice(0, 20);
    for (const line of mapped) await logConversion(store, { visitorId: ctx.visitorId, memberId: member.id, offer: line.row.sku, revenueCents: line.amountCents, ref: `shopify:${line.lineId}`, channel });
  }
  return { status: "processed", summary: `order ${orderId}: ${recorded} line(s)${membershipId ? `, membership ${membershipId.slice(0, 8)}` : ""}${renewal ? " (renewal)" : ""}` };
}

async function initialMembership(store: Store, member: Member, row: ShopifyProductRow, orderId: string, cell: string | null, paidAt: Date, now: Date): Promise<Membership> {
  const interval: Membership["interval"] = row.interval === "year" ? "year" : "month";
  // CANON UPDATE 6: a trial row starts "trialing". Nothing is paid for the membership yet, so the period that grants
  // access is the trial itself (current_period_end = trial_end); the day-7 renewal order converts it (orderPaid), and
  // no renewal order by trial_end + grace lapses it (runShopifyLapses) and returns the founding seat. The money-back
  // window is set at the first charge; until then guarantee_until = trial_end + 14 days keeps the bonus PDFs vested
  // on the same day they would be for a charge-today member.
  const trialDays = row.trial_days && row.trial_days >= 1 && row.trial_days <= 31 ? row.trial_days : 0;
  const trialEnd = trialDays ? addDays(paidAt, trialDays) : null;
  if (trialDays) {
    const prior = (await store.find("memberships", { member_id: member.id })).filter((m) => m.shopify_origin_order_id !== orderId && m.status !== "incomplete" && m.plan !== "gift");
    if (prior.length) await ticket(store, member, `Shopify order ${orderId}: ${member.email} started a second ${trialDays}-day trial (${row.sku}) after an earlier membership (${prior[0]!.offer_code ?? prior[0]!.plan}, ${prior[0]!.status}). One trial per person: cancel the new contract in the subscription app before day ${trialDays}, or convert it by hand if the earlier row was never charged.`);
  }
  const fields: Partial<Membership> = {
    member_id: member.id,
    plan: planFor(row),
    arm: trialDays ? "T" : "B",
    offer_code: row.sku,
    price_cents: row.recurring_cents ?? row.price_cents,
    interval,
    status: trialDays ? "trialing" : "active",
    founding: row.entitlement === "founding",
    first_paid_at: trialDays ? null : paidAt.toISOString(),
    guarantee_until: addDays(trialEnd ?? paidAt, GUARANTEE_DAYS).toISOString(),
    current_period_end: trialEnd ? trialEnd.toISOString() : addInterval(paidAt, interval).toISOString(),
    trial_end: trialEnd ? trialEnd.toISOString() : null,
    processor: "shopify",
    price_cell: cell ?? row.cell,
    shopify_origin_order_id: orderId,
    shopify_customer_id: member.shopify_customer_id ?? null,
    pending_verification: false,
    grace_until: null,
  };
  const existing = await store.findOne("memberships", { shopify_origin_order_id: orderId });
  if (existing) {
    // subscription_contracts/create got here first and left a placeholder: complete it,
    // keeping any status a newer contract event already set.
    const keep = existing.status !== "incomplete" ? { status: existing.status } : {};
    return (await store.update("memberships", existing.id, { ...fields, ...keep, member_id: existing.member_id }))!;
  }
  try {
    return await store.insert("memberships", {
      ...fields,
      cancel_at_period_end: false,
      canceled_at: null,
      paused_until: null,
      partner_seat: false,
      checkout_intent_id: null,
      gift_credit_cents: 0,
      stripe_subscription_id: null,
      stripe_customer_id: null,
      shopify_contract_id: null,
      shopify_revision: null,
      shopify_last_attempt_id: null,
      is_demo: false,
      created_at: now.toISOString(),
    });
  } catch {
    const again = await store.findOne("memberships", { shopify_origin_order_id: orderId });
    if (!again) throw new Error("membership insert failed");
    return again;
  }
}

async function renewalMembership(store: Store, member: Member, row: ShopifyProductRow): Promise<Membership | null> {
  const rows = await store.find("memberships", { member_id: member.id, processor: "shopify" }, { orderBy: "created_at", desc: true });
  const live = (m: Membership) => !["refunded", "expired"].includes(m.status);
  return (
    rows.find((m) => m.offer_code === row.sku && live(m)) ??
    rows.find((m) => m.plan === planFor(row) && live(m)) ??
    // Lapsed with no renewal order, and now the renewal order came (late dunning success): revive it.
    rows.find((m) => m.plan === planFor(row) && m.status === "expired") ??
    null
  );
}

async function provisionGift(store: Store, member: Member, line: MappedLine, orderId: string) {
  const p = line.properties;
  const recipientEmail = normalizeEmail(p.recipient_email ?? "");
  const recipientName = (p.recipient_name ?? "").replace(/[<>\u0000-\u001F]/g, "").trim().slice(0, 60);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipientEmail) || !recipientName) {
    await ticket(store, member, `Gift order ${orderId} has no recipient name/email (line properties "Recipient name" / "Recipient email"). Email the buyer.`);
    return;
  }
  await createGift(store, { gifter: { email: member.email, first_name: member.first_name }, recipientName, recipientEmail, message: (p.message ?? "").slice(0, 300), months: line.row.gift_months ?? 3, amountCents: line.amountCents });
}

async function conversions(store: Store, member: Member, orderId: string, ebookCents: number, membership: Membership | null, attribution: Member["attribution"]) {
  try {
    const { recordConversion } = await import("../conversions");
    const base = { sourcePath: "/checkout", email: member.email, memberId: member.id, attribution };
    if (ebookCents > 0) await recordConversion(store, { ...base, name: "Purchase", eventId: `shop_${orderId}_purchase`, valueCents: ebookCents, contentName: "starter_books" }, env.siteUrl);
    if (membership) await recordConversion(store, { ...base, name: "Subscribe", eventId: `shop_${orderId}_subscribe`, valueCents: membership.price_cents, contentName: membership.founding ? "founding" : "membership" }, env.siteUrl);
  } catch (err) {
    console.error("shopify conversion failed", (err as Error).message);
  }
}

async function welcome(store: Store, member: Member, m: Membership, withBooks = false) {
  const link = await issueMagicLink(store, member.id, env.siteUrl, "/app", 24 * 3600_000);
  const trial = m.status === "trialing" && m.trial_end;
  if (trial) {
    // CANON UPDATE 6: the 7-day trial welcome restates the full auto-renewal terms (ROSCA / state ARLs): the charge date,
    // the amount, the cadence, how to cancel online, and that cancelling before day 7 means no membership charge.
    const chargeDate = formatDate(m.trial_end!, member.timezone || env.displayTimeZone);
    await sendEmail({
      to: member.email,
      from: "chang",
      template: "SH_welcome_trial",
      subject: `Your 7-day trial has started. First charge ${chargeDate} unless you cancel.`,
      secrets: [link],
      text: [
        `${member.first_name}, welcome. Your 7-day trial of the ${m.founding ? "founding membership" : "membership"} started today${withBooks ? ", and your two Starter Books are yours to keep" : ""}.`,
        `Open the members area (this link works for 24 hours): ${link}`,
        `Later, sign in at ${env.siteUrl}/login with this email address. We send you a code; there's no password.`,
        `The terms, in plain words: nothing was charged for the membership today. On ${chargeDate} your card is charged ${moneyExact(m.price_cents)}, then ${moneyExact(m.price_cents)} every ${m.interval === "year" ? "year" : "month"} on the same date until you cancel${m.founding ? ". Founding price locked for as long as you stay subscribed (pauses included)" : ""}. We email you 2 days before that first charge.`,
        `Cancel online anytime, in at most two screens, on your account page: ${shopifyConfig.customerAccountUrl()}. Cancel before ${chargeDate} and the membership costs nothing. After the first charge: 14-day money-back guarantee, once per person, from your membership page.`,
        "— Chang Yin (AI character)",
      ].join("\n\n"),
    });
    return;
  }
  await sendEmail({
    to: member.email,
    from: "chang",
    template: "SH_welcome",
    subject: "Your Strong Years membership is ready",
    secrets: [link],
    text: [
      `${member.first_name}, welcome. Your ${m.founding ? "founding membership" : "membership"} is active.`,
      `Open the members area (this link works for 24 hours): ${link}`,
      `Later, sign in at ${env.siteUrl}/login with this email address. We send you a code; there's no password.`,
      `${moneyExact(m.price_cents)} a ${m.interval === "year" ? "year" : "month"}${m.founding ? ", locked for as long as you stay subscribed (pauses included)" : ""}. 14-day money-back guarantee: tap Refund on your membership page.`,
      `Cancel or pause anytime on your account page: ${shopifyConfig.customerAccountUrl()}`,
      "— Chang Yin (AI character)",
    ].join("\n\n"),
  });
}

/**
 * Starter Books only (cell A): email 1 of the 3-email onboarding (shopify/emails/01-day0-your-books.md).
 * The books are served by us, watermarked, behind a 24-hour sign-in link; the founding offer links to the
 * membership page (terms + consent there), never to a cart permalink. Emails 2 and 3 are the launch cron's.
 */
async function booksWelcome(store: Store, member: Member) {
  const link = await issueMagicLink(store, member.id, env.siteUrl, "/app/printables", 24 * 3600_000);
  const storeUrl = `https://${shopifyConfig.storeDomain()}`;
  await sendEmail({
    to: member.email,
    from: "chang",
    template: "SH_books_e1",
    subject: "Your books are here. Start with Day 0.",
    secrets: [link],
    text: [
      `${member.first_name}, your two books are ready. Download them here (this link works for 24 hours; after that, sign in at ${env.siteUrl}/login with this email, no password): ${link}`,
      "Start with Day 0 in the Reset: six simple tests, about 15 minutes, next to a sturdy chair against the wall and a kitchen counter. Write your numbers on the score sheet. On Day 7 you test again and compare.",
      "Three rules for every session: move slowly; breathe out when you push, stand or lift; stop if anything hurts sharply, or if you feel chest pain, dizziness or shortness of breath.",
      `Want a new session every day after the seven? Founding membership: $25 today for your first month, then $25 a month until you cancel. Founding price locked for as long as you stay subscribed. 14-day money-back guarantee. Cancel online anytime. Nothing is added unless you choose it on this page: ${storeUrl}/products/founding-membership?utm_source=email&utm_medium=onboarding&utm_campaign=books_e1`,
      "— Chang Yin (AI character; every movement in the book is built from published exercise guidelines for people our age)",
    ].join("\n\n"),
  });
}

/* ---------------- refunds ---------------- */

async function refunded(store: Store, p: Json, now: Date, admin: ShopifyAdmin): Promise<HandleResult> {
  // refunds/create carries one refund; an order-shaped payload with a refunds[] array is accepted too.
  const refunds = Array.isArray(p.refunds) ? arr(p.refunds, 20).map(obj) : [p];
  let changed = 0;
  let ended = 0;
  for (const r of refunds) {
    const items = arr(r.refund_line_items, 50).map(obj);
    if (items.length === 0) {
      const orderId = shopifyId(r.order_id ?? p.id);
      if (orderId && arr(r.transactions).length) await ticket(store, null, `Shopify refund on order ${orderId} has no line items (an amount-only refund). Check whether access should end.`, false);
      continue;
    }
    for (const it of items) {
      const lineId = shopifyId(it.line_item_id);
      if (!lineId) continue;
      const amount = cents(it.subtotal) ?? cents(obj(it.subtotal_set).shop_money ? obj(obj(it.subtotal_set).shop_money).amount : null);
      const restockType = text(it.restock_type, 20) || (r.restock === true ? "legacy_restock" : "no_restock");
      const known = await store.find("sy_orders", { shopify_line_id: lineId });
      if (known.length === 0) {
        // The paid order hasn't been delivered yet (Shopify retries it): park the refund so orders/paid grants nothing.
        const orderId = shopifyId(r.order_id ?? p.id);
        try {
          await store.insert("shopify_early_refunds", { shopify_order_id: orderId ?? "", shopify_line_id: lineId, shopify_refund_id: shopifyId(r.id), amount_cents: amount, restock_type: restockType });
          changed++;
        } catch {
          /* same refund delivered twice */
        }
        continue;
      }
      for (const o of known) {
        if (o.status === "refunded") continue;
        const refundedCents = Math.min(o.amount_cents, (o.amount_refunded_cents ?? 0) + (amount ?? o.amount_cents));
        const full = refundedCents >= o.amount_cents;
        const [row] = await store.updateWhere("sy_orders", { id: o.id, status: { in: ["paid", "refund_pending"] } }, { status: full ? "refunded" : "paid", amount_refunded_cents: refundedCents });
        if (!row) continue;
        changed++;
        if (full && o.kind === "membership_charge" && o.membership_id) {
          const m = await store.get("memberships", o.membership_id);
          if (m && m.status !== "refunded") {
            await store.update("memberships", m.id, { status: "refunded", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString(), grace_until: null });
            ended++;
            // Seat ledger rule 3: the refunded first founding charge gives its seat back, unless Shopify restocked it.
            if (m.founding && m.shopify_origin_order_id === o.shopify_order_id && restockType === "no_restock") {
              const row = (await store.find("shopify_products", { entitlement: "founding", active: true })).find((x) => x.inventory_item_id);
              if (row?.inventory_item_id) await giveSeatBack(store, admin, row.inventory_item_id, `strongyears://seat-ledger/refund/${shopifyId(r.id) ?? o.shopify_line_id}`, o.shopify_order_id ?? null);
            }
            // The contract must not renew. Our app can cancel only contracts it owns; on the launch path a person
            // cancels it in Apps → Subscriptions (the refund usually came from there anyway).
            const c = m.shopify_contract_id ? await admin.cancelContract(m.shopify_contract_id) : { ok: false, error: "no contract id on file" };
            if (!c.ok) await ticket(store, null, `Membership ${m.id.slice(0, 8)} was refunded in Shopify; make sure its subscription contract is cancelled in Apps → Subscriptions so it doesn't renew (${c.error ?? "unknown"}).`, false);
          }
        }
      }
    }
  }
  return changed ? { status: "processed", summary: `${changed} line(s) refunded, ${ended} membership(s) ended` } : { status: "ignored", summary: "nothing new to refund" };
}

/* ---------------- subscription contracts ---------------- */

const TOPIC_STATUS: Partial<Record<ShopifyTopic, string>> = {
  "subscription_contracts/activate": "active",
  "subscription_contracts/pause": "paused",
  "subscription_contracts/cancel": "cancelled",
  "subscription_contracts/expire": "expired",
  "subscription_contracts/fail": "failed",
};

async function membershipForContract(store: Store, contractId: string, originOrderId: string | null): Promise<Membership | null> {
  return (await store.findOne("memberships", { shopify_contract_id: contractId })) ?? (originOrderId ? await store.findOne("memberships", { shopify_origin_order_id: originOrderId }) : null);
}

async function contractEvent(store: Store, topic: ShopifyTopic, p: Json, now: Date): Promise<HandleResult> {
  const id = shopifyId(p.id ?? p.admin_graphql_api_id);
  if (!id) return { status: "ignored", summary: "contract without id" };
  const origin = shopifyId(p.origin_order_id ?? p.admin_graphql_api_origin_order_id);
  const rev = typeof p.revision_id === "number" ? p.revision_id : typeof p.revision_id === "string" && /^\d{1,15}$/.test(p.revision_id) ? Number(p.revision_id) : null;
  const status = (TOPIC_STATUS[topic] ?? text(p.status, 20)).toLowerCase();
  const m = await membershipForContract(store, id, origin);
  if (!m) return { status: "deferred", summary: `contract ${id}: its order hasn't arrived yet` };
  if (rev !== null && m.shopify_revision !== null && m.shopify_revision !== undefined && rev <= m.shopify_revision) return { status: "ignored", summary: `contract ${id}: stale revision ${rev} <= ${m.shopify_revision}` };
  const patch: Partial<Membership> = { shopify_contract_id: id };
  if (rev !== null) patch.shopify_revision = rev;
  const ended = m.status === "refunded" || m.status === "expired";
  if (!ended) {
    if (status === "active") {
      if (m.status === "paused" || m.status === "canceled" || m.status === "incomplete") {
        patch.status = "active";
        patch.paused_until = null;
      }
      patch.cancel_at_period_end = false;
      patch.canceled_at = null;
    } else if (status === "paused") {
      patch.status = "paused";
    } else if (status === "cancelled" || status === "canceled") {
      patch.status = "canceled";
      patch.cancel_at_period_end = true;
      patch.canceled_at = m.canceled_at ?? now.toISOString();
    } else if (status === "expired") {
      patch.status = "expired";
    } else if (status === "failed") {
      patch.status = "past_due";
      patch.grace_until = m.grace_until ?? addDays(now, shopifyConfig.graceDays()).toISOString();
    }
  }
  await store.update("memberships", m.id, patch);
  return { status: "processed", summary: `contract ${id} → ${patch.status ?? m.status}${rev !== null ? ` (rev ${rev})` : ""}` };
}

/* ---------------- billing attempts ---------------- */

async function billingAttempt(store: Store, p: Json, success: boolean, now: Date): Promise<HandleResult> {
  const contractId = shopifyId(p.subscription_contract_id ?? p.admin_graphql_api_subscription_contract_id);
  if (!contractId) return { status: "ignored", summary: "billing attempt without contract" };
  const attemptId = shopifyId(p.id ?? p.admin_graphql_api_id);
  const m = await store.findOne("memberships", { shopify_contract_id: contractId });
  if (!m) return { status: "deferred", summary: `billing attempt for unknown contract ${contractId}` };
  if (attemptId && m.shopify_last_attempt_id && !idGreater(attemptId, m.shopify_last_attempt_id)) return { status: "ignored", summary: `stale billing attempt ${attemptId}` };
  const patch: Partial<Membership> = {};
  if (attemptId) patch.shopify_last_attempt_id = attemptId;
  const ended = ["refunded", "expired"].includes(m.status);
  if (success) {
    if (!ended) {
      const base = m.current_period_end && new Date(m.current_period_end).getTime() > now.getTime() ? new Date(m.current_period_end) : now;
      patch.current_period_end = addInterval(base, m.interval).toISOString();
      patch.grace_until = null;
      if (m.status === "past_due" || m.status === "paused") patch.status = "active";
    }
    await store.update("memberships", m.id, patch);
    return { status: "processed", summary: `renewed ${m.id.slice(0, 8)} until ${patch.current_period_end ?? m.current_period_end}` };
  }
  if (ended || m.status === "canceled") {
    await store.update("memberships", m.id, patch);
    return { status: "ignored", summary: "failure on an ended membership" };
  }
  const firstFailure = !m.grace_until;
  patch.status = "past_due";
  patch.grace_until = m.grace_until ?? addDays(now, shopifyConfig.graceDays()).toISOString();
  await store.update("memberships", m.id, patch);
  const member = await store.get("members", m.member_id);
  if (member && firstFailure) {
    await sendEmail({
      to: member.email,
      template: "SH_payment_failed",
      subject: "Your Strong Years payment didn't go through",
      text: [
        `${member.first_name}, your last membership payment didn't go through. Nothing else changes for ${shopifyConfig.graceDays()} days: your sessions stay open while you sort it out.`,
        `Update your card here: ${shopifyConfig.customerAccountUrl()}`,
        "If you'd rather stop, you can cancel on the same page. Nobody will call you.",
      ].join("\n\n"),
    });
  }
  return { status: "processed", summary: `payment failed for ${m.id.slice(0, 8)}, grace until ${patch.grace_until}` };
}

/* ---------------- disputes/create, disputes/update (R5-9) ---------------- */

const DISPUTE_RESTORES = new Set(["won"]);

/**
 * A chargeback on an order we provisioned. Store-wide topic (read_orders). Any open or lost chargeback ends the
 * membership the order paid for and marks the person in the refund ledger (which also blocks the self-serve
 * money-back refund: the money is already being contested). An inquiry only tickets. A dispute later marked
 * "won" restores the lines and the membership. Idempotent per dispute id + status.
 */
async function dispute(store: Store, p: Json, now: Date): Promise<HandleResult> {
  const disputeId = shopifyId(p.id);
  const orderId = shopifyId(p.order_id);
  if (!disputeId || !orderId) return { status: "ignored", summary: "dispute without id/order" };
  const type = text(p.type, 20).toLowerCase();
  const status = text(p.status, 30).toLowerCase();
  const lines = await store.find("sy_orders", { shopify_order_id: orderId });
  if (!lines.length) return { status: "ignored", summary: `dispute ${disputeId}: order ${orderId} was never provisioned` };
  const first = lines[0]!;
  if (!first.member_id) return { status: "ignored", summary: `dispute ${disputeId}: order ${orderId} has no member` };
  const member = await store.get("members", first.member_id);
  if (type !== "chargeback") {
    await ticket(store, member, `Shopify ${type || "inquiry"} ${disputeId} on order ${orderId} (${status}). Reply with evidence in Shopify; access unchanged.`);
    return { status: "processed", summary: `inquiry ${disputeId} ticketed` };
  }
  const ledgerKey = `dispute_${disputeId}`;
  const ledger = await store.findOne("refund_ledger", { processor_refund_id: ledgerKey });
  if (DISPUTE_RESTORES.has(status)) {
    if (!ledger) return { status: "ignored", summary: `dispute ${disputeId} won: nothing to restore` };
    await store.remove("refund_ledger", { id: ledger.id });
    let restored = 0;
    for (const o of lines) {
      if (o.status !== "disputed") continue;
      await store.update("sy_orders", o.id, { status: "paid" });
      if (o.kind === "membership_charge" && o.membership_id) {
        const m = await store.get("memberships", o.membership_id);
        if (m && m.status === "canceled") {
          const end = addInterval(new Date(o.created_at), m.interval);
          await store.update("memberships", m.id, { status: "active", canceled_at: null, cancel_at_period_end: false, current_period_end: (end.getTime() > now.getTime() ? end : now).toISOString() });
          restored++;
        }
      }
    }
    await ticket(store, member, `Chargeback ${disputeId} on order ${orderId} was WON. ${restored} membership(s) restored; if the contract was cancelled in Apps → Subscriptions, invite the member to re-subscribe.`, false);
    return { status: "processed", summary: `dispute ${disputeId} won: ${restored} membership(s) restored` };
  }
  if (ledger) return { status: "ignored", summary: `dispute ${disputeId} already applied (${status})` };
  let ended = 0;
  let amount = 0;
  for (const o of lines) {
    if (o.status === "refunded") continue;
    await store.update("sy_orders", o.id, { status: "disputed" });
    amount += o.amount_cents;
    if (o.kind === "membership_charge" && o.membership_id) {
      const m = await store.get("memberships", o.membership_id);
      if (m && !["refunded", "expired", "canceled"].includes(m.status)) {
        await store.update("memberships", m.id, { status: "canceled", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString(), grace_until: null });
        ended++;
      }
    }
  }
  const membershipId = lines.find((o) => o.membership_id)?.membership_id ?? null;
  await store.insert("refund_ledger", { email: (member?.email ?? first.email).toLowerCase(), card_fingerprint: null, member_id: first.member_id, ...(membershipId ? { membership_id: membershipId } : {}), amount_cents: cents(p.amount) ?? amount, processor_refund_id: ledgerKey });
  await ticket(store, member, `Chargeback ${disputeId} on order ${orderId} (${status}). Access ended, seat released, self-serve refund blocked. Cancel the subscription contract in Apps → Subscriptions and respond to the dispute in Shopify Payments before ${text(p.evidence_due_by, 40) || "the due date"}.`);
  return { status: "processed", summary: `dispute ${disputeId} (${status}): ${ended} membership(s) ended` };
}

/* ---------------- orders/cancelled ---------------- */

/**
 * A cancelled order that we had provisioned (paid, then cancelled in the admin, with or without a refund)
 * ends what it granted: the membership it created, or the one-time lines. Unpaid/abandoned orders map to nothing.
 */
async function orderCancelled(store: Store, p: Json, now: Date): Promise<HandleResult> {
  const orderId = shopifyId(p.id);
  if (!orderId) return { status: "ignored", summary: "order without id" };
  const lines = await store.find("sy_orders", { shopify_order_id: orderId });
  if (!lines.length) return { status: "ignored", summary: `order ${orderId} was never provisioned` };
  let ended = 0;
  for (const o of lines) {
    if (o.status === "refunded") continue;
    await store.update("sy_orders", o.id, { status: "refunded", amount_refunded_cents: o.amount_cents });
    if (o.kind === "membership_charge" && o.membership_id) {
      const m = await store.get("memberships", o.membership_id);
      if (m && m.status !== "refunded" && m.shopify_origin_order_id === orderId) {
        await store.update("memberships", m.id, { status: "refunded", canceled_at: now.toISOString(), cancel_at_period_end: false, current_period_end: now.toISOString(), grace_until: null });
        ended++;
      }
    }
  }
  if (ended) await ticket(store, null, `Shopify order ${orderId} was cancelled in the admin; the membership it started has ended here. Confirm the subscription contract is cancelled in Apps → Subscriptions.`, false);
  return { status: "processed", summary: `order ${orderId} cancelled: ${lines.length} line(s) voided, ${ended} membership(s) ended` };
}

/* ---------------- customers/delete ---------------- */

/** The customer record was deleted in Shopify (GDPR or by hand): unlink it; access is a billing question, not an identity one. */
async function customerDelete(store: Store, p: Json): Promise<HandleResult> {
  const id = shopifyId(p.id);
  if (!id) return { status: "ignored", summary: "customer without id" };
  const member = await store.findOne("members", { shopify_customer_id: id });
  if (!member) return { status: "ignored", summary: "customer is not a member" };
  await store.update("members", member.id, { shopify_customer_id: null });
  await ticket(store, member, `Shopify customer ${id} was deleted in Shopify. Unlinked from the member; if this was an erasure request, delete the member from /admin too.`, false);
  return { status: "processed", summary: `customer ${id} unlinked` };
}

/* ---------------- customers/update ---------------- */

async function customerUpdate(store: Store, p: Json): Promise<HandleResult> {
  const id = shopifyId(p.id);
  if (!id) return { status: "ignored", summary: "customer without id" };
  const member = await store.findOne("members", { shopify_customer_id: id });
  if (!member) return { status: "ignored", summary: "customer is not a member" };
  const updatedAt = typeof p.updated_at === "string" && !Number.isNaN(Date.parse(p.updated_at)) ? new Date(p.updated_at).toISOString() : null;
  if (updatedAt && member.shopify_customer_updated_at && updatedAt <= member.shopify_customer_updated_at) return { status: "ignored", summary: "stale customer update" };
  const patch: Partial<Member> = {};
  if (updatedAt) patch.shopify_customer_updated_at = updatedAt;
  const first = text(p.first_name, 60).replace(/[<>\u0000-\u001F]/g, "").trim();
  if (first) patch.first_name = first;
  const email = normalizeEmail(text(p.email, 254));
  let note = "";
  if (email && email !== member.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    if (await findMemberByEmail(store, email)) {
      await ticket(store, member, `Shopify customer ${id} changed email to one that already belongs to another member. Not merged; check by hand.`);
      note = ", email collision (ticket)";
    } else {
      // Sign-in follows the new inbox, which has to prove itself again; every session ends.
      patch.email = email;
      patch.email_verified_at = null;
      patch.session_version = (member.session_version ?? 1) + 1;
      note = ", email changed";
    }
  }
  await store.update("members", member.id, patch);
  return { status: "processed", summary: `customer ${id} updated${note}` };
}

/* ---------------- inventory mirror ---------------- */

async function inventoryUpdate(store: Store, p: Json, admin: ShopifyAdmin): Promise<HandleResult> {
  const item = shopifyId(p.inventory_item_id);
  const loc = shopifyId(p.location_id);
  const available = typeof p.available === "number" && Number.isSafeInteger(p.available) ? p.available : null;
  if (!item || !loc || available === null) return { status: "ignored", summary: "bad inventory payload" };
  const at = typeof p.updated_at === "string" && !Number.isNaN(Date.parse(p.updated_at)) ? new Date(p.updated_at).toISOString() : new Date().toISOString();
  const row = await store.findOne("shopify_inventory", { inventory_item_id: item, location_id: loc });
  if (row && row.shopify_updated_at >= at) return { status: "ignored", summary: "stale inventory level" };
  if (row) await store.updateWhere("shopify_inventory", { id: row.id, shopify_updated_at: row.shopify_updated_at }, { available, shopify_updated_at: at });
  else {
    try {
      await store.insert("shopify_inventory", { inventory_item_id: item, location_id: loc, available, shopify_updated_at: at });
    } catch {
      return { status: "deferred", summary: "inventory row raced; retry" };
    }
  }
  if (available <= 0) await foundingStockExhausted(store, admin, item);
  return { status: "processed", summary: `inventory ${item}@${loc} = ${available}` };
}

/* ---------------- founding seat ledger (shopify/src/seatLedger.ts rules, executed here) ---------------- */

/**
 * +1 on the founding variant for a renewal order or a refunded first charge. Idempotent by reference URI
 * (shopify_seat_ledger); the location comes from the inventory mirror, else SHOPIFY_LOCATION_ID, else a person.
 */
/** A trial that lapsed without its first charge gives its founding seat back (the $0 checkout consumed one). */
export async function releaseTrialSeat(store: Store, m: Pick<Membership, "id" | "founding" | "shopify_origin_order_id">, admin: ShopifyAdmin = shopifyAdmin()): Promise<void> {
  if (!m.founding) return;
  const row = (await store.find("shopify_products", { entitlement: "founding", active: true })).find((x) => x.inventory_item_id);
  if (!row?.inventory_item_id) return;
  await giveSeatBack(store, admin, row.inventory_item_id, `strongyears://seat-ledger/trial-lapse/${m.shopify_origin_order_id ?? m.id}`, m.shopify_origin_order_id ?? null);
}

async function giveSeatBack(store: Store, admin: ShopifyAdmin, inventoryItemId: string, ref: string, orderId: string | null) {
  try {
    await store.insert("shopify_seat_ledger", { ref, delta: 1, shopify_order_id: orderId });
  } catch {
    return; // already credited
  }
  const level = await store.findOne("shopify_inventory", { inventory_item_id: inventoryItemId });
  const locationId = level?.location_id ?? shopifyConfig.locationId();
  const r = admin.adjustInventory && locationId ? await admin.adjustInventory({ inventoryItemId, locationId, delta: 1, ref }) : { ok: false, error: locationId ? "admin client has no inventory access" : "no location on file (set SHOPIFY_LOCATION_ID or wait for inventory_levels/update)" };
  if (!r.ok) {
    await store.remove("shopify_seat_ledger", { ref });
    await ticket(store, null, `Founding seat not returned (${ref}): ${r.error ?? "unknown"}. Add 1 to the founding variant's available stock by hand (Products → Founding Membership) so renewals/refunds don't eat seats.`, false);
    return;
  }
  if (level && typeof r.available === "number") await store.update("shopify_inventory", level.id, { available: r.available });
}

/** Founding stock at 0: renewals must never fail on "out of stock" (Shopify checks inventory on every billing attempt). */
async function foundingStockExhausted(store: Store, admin: ShopifyAdmin, inventoryItemId: string) {
  const row = (await store.find("shopify_products", { entitlement: "founding", active: true })).find((x) => x.inventory_item_id === inventoryItemId);
  if (!row) return;
  const r = admin.allowOverselling ? await admin.allowOverselling({ productId: row.shopify_product_id, variantId: row.shopify_variant_id }) : { ok: false, error: "admin client cannot edit variants" };
  await ticket(store, null, r.ok
    ? `The founding group is full (stock 0). The founding variant now allows overselling so existing members' renewals keep working. Run \`npm run close-founding\` in shopify/ today (unpublishes founding, activates the $35 standard membership).`
    : `The founding group is full (stock 0) but the variant could NOT be switched to continue selling (${r.error ?? "unknown"}). Do it NOW in Products → Founding Membership → Inventory → "Continue selling when out of stock", then run close-founding; otherwise every founding renewal fails with insufficient inventory.`);
}

/**
 * The founding counter in Shopify mode: cap minus what Shopify says is still
 * available on the founding plan's inventory (summed over locations), from the DB
 * mirror. Until the first inventory webhook arrives, the count of founding
 * memberships we provisioned (refunds release the seat).
 */
export async function shopifyFoundingTaken(store: Store, cap: number): Promise<number> {
  const items = [...new Set((await store.find("shopify_products", { entitlement: "founding", active: true })).map((r) => r.inventory_item_id).filter((x): x is string => Boolean(x)))];
  if (items.length) {
    const levels = await store.find("shopify_inventory", { inventory_item_id: { in: items } });
    if (levels.length) {
      const available = levels.reduce((s, l) => s + Math.max(0, l.available), 0);
      return Math.max(0, Math.min(cap, cap - available));
    }
  }
  return store.count("memberships", { founding: true, status: { in: ["trialing", "active", "past_due", "paused", "canceled", "expired"] } });
}
