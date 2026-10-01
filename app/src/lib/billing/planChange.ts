/**
 * The Essentials ($12/mo) save offer on the Shopify launch path (INTEGRATION.md §4).
 * Shopify Subscriptions lets a member pause, skip or cancel on their account page,
 * but not swap the product, and our app can edit only contracts it owns
 * (write_own_subscription_contracts). So the members app records the request and:
 *   - SUBSCRIPTION_ENGINE=app: queued for the Admin API contract edit
 *     (subscriptionContractUpdateCalculate → commit, run by ops; method "admin_api");
 *   - launch path: a human-queue ticket with a 1-business-day SLA (method "human_queue").
 * Nothing changes on the member's bill until a person (or the script) confirms it,
 * and the copy says exactly that. No dark patterns: the cancel link stays one tap away.
 */
import type { Store } from "../db/store";
import type { Member, Membership, PlanChangeRequest } from "../db/types";
import { alertOnCall, sendEmail } from "../notify";
import { ESSENTIALS_CENTS } from "./cancel";
import { shopifyConfig } from "./shopify";

export const PLAN_CHANGE_SLA = "1 business day";

export const ANNUAL_CENTS = 24900;

export function canOfferEssentials(m: Pick<Membership, "plan" | "price_cents" | "status">): boolean {
  return m.plan === "monthly" && m.price_cents > ESSENTIALS_CENTS && !["refunded", "expired", "incomplete"].includes(m.status);
}

/** Founding annual ($249/yr) is offered to founding monthly members after their first renewal (OFFER.md §0.1). */
export function canOfferAnnual(m: Pick<Membership, "plan" | "founding" | "status" | "cancel_at_period_end">, chargeCount: number): boolean {
  return m.plan === "monthly" && m.founding && m.status === "active" && !m.cancel_at_period_end && chargeCount >= 2;
}

const TARGETS = {
  essentials: {
    label: "Strong Years Essentials ($12 a month: the Daily Practice and the monthly Strength Age retest, without the extras)",
    subject: "Got it: switching you to Essentials, $12 a month",
    alert: "Essentials switch requested",
    template: "SH_essentials_requested",
    queueNote: "Shopify Subscriptions owns the contract: edit it in Apps → Subscriptions (swap the line to Strong Years Essentials, $12/mo) or cancel and have the member re-subscribe to Essentials.",
    billing: "Your next renewal will be at the Essentials price once it's applied; if your renewal date is sooner than that, we'll refund the difference.",
  },
  annual: {
    label: "the Founding Annual plan ($249 a year, about ten months' worth, at your founding price; it renews yearly until you cancel and we email you 30 days before every yearly renewal)",
    subject: "Got it: switching you to the Founding Annual, $249 a year",
    alert: "Annual switch requested",
    template: "SH_annual_requested",
    queueNote: "Shopify Subscriptions owns the contract: cancel the monthly contract in Apps → Subscriptions on the day the member pays the $249 Founding Annual checkout (send them the founding-annual product link), so no month is double-charged.",
    billing: "Nothing is charged until a person confirms the switch with you by email: you pay the $249 at a checkout we send you, and your monthly plan ends the same day, so you are never charged for both.",
  },
} as const;

export async function requestPlanSwitch(store: Store, member: Pick<Member, "id" | "email" | "first_name">, m: Membership, to: PlanChangeRequest["to_plan"], e: Record<string, string | undefined> = process.env): Promise<PlanChangeRequest> {
  const open = await store.findOne("plan_change_requests", { membership_id: m.id, status: "open" });
  if (open) return open;
  const t = TARGETS[to];
  const method: PlanChangeRequest["method"] = shopifyConfig.ownsContracts(e) && m.shopify_contract_id ? "admin_api" : "human_queue";
  const req = await store.insert("plan_change_requests", {
    member_id: member.id,
    membership_id: m.id,
    shopify_contract_id: m.shopify_contract_id ?? null,
    from_plan: m.offer_code ?? m.plan,
    to_plan: to,
    status: "open",
    method,
    note: method === "admin_api" ? "Apply with the contract-edit script (app engine)." : t.queueNote,
    resolved_at: null,
  });
  const tk = await store.insert("support_tickets", { member_id: member.id, email: member.email, reason: "plan_change", message: `Switch to ${to} requested (request ${req.id.slice(0, 8)}, ${method}). SLA ${PLAN_CHANGE_SLA}. ${req.note ?? ""}`, status: "open" });
  await alertOnCall(t.alert, `ticket-${tk.id}`);
  await sendEmail({
    to: member.email,
    template: t.template,
    subject: t.subject,
    text: [
      `${member.first_name}, we've got your request to switch to ${t.label}.`,
      `A person on our team handles it within ${PLAN_CHANGE_SLA} and emails you. Until then nothing on your bill changes. ${t.billing}`,
      `Changed your mind, or want to cancel instead? Your account page, one tap, no call: ${shopifyConfig.customerAccountUrl(e)}`,
    ].join("\n\n"),
  });
  return req;
}

export async function requestEssentialsSwitch(store: Store, member: Pick<Member, "id" | "email" | "first_name">, m: Membership, e: Record<string, string | undefined> = process.env): Promise<PlanChangeRequest> {
  return requestPlanSwitch(store, member, m, "essentials", e);
}
