/**
 * Who can use the members area, and which membership row the account and
 * billing actions act on (AUDIT_CODE H2, H3).
 */
import type { Membership } from "./db/types";

const ENDED = ["expired", "refunded", "incomplete"] as const;

function periodOpen(m: Membership, now: number): boolean {
  return Boolean(m.current_period_end && new Date(m.current_period_end).getTime() > now);
}

/**
 * Shopify launch path (Round 5 audit): the free Shopify Subscriptions app never sends us contract events, so a
 * cancellation, pause or dunned-out card on Shopify's side shows up only as the ABSENCE of the next renewal order.
 * An "active" Shopify row therefore grants access only while its paid period is open, plus a float for a late
 * renewal webhook (SHOPIFY_GRACE_DAYS, default 7, or the row's grace_until when a failure was reported).
 */
function shopifyFloatMs(): number {
  const n = Number((process.env.SHOPIFY_GRACE_DAYS ?? "").trim() || "7");
  return (Number.isFinite(n) && n >= 0 && n <= 30 ? n : 7) * 86_400_000;
}

function shopifyPaidThrough(m: Membership, now: number): boolean {
  if (!m.current_period_end) return true;
  const end = new Date(m.current_period_end).getTime();
  const grace = m.grace_until ? new Date(m.grace_until).getTime() : end + shopifyFloatMs();
  return Math.max(end, grace) > now;
}

/** True when this one membership row grants access right now. */
export function grantsAccess(m: Membership | null | undefined, now = Date.now()): boolean {
  if (!m) return false;
  // NEW-1: bought with this email by someone else until the inbox owner confirms it.
  if (m.pending_verification) return false;
  switch (m.status) {
    case "trialing":
      return true;
    case "past_due":
      // Shopify: a failed billing attempt opens a grace period; after it, access
      // stops until a payment succeeds. (Stripe dunning leaves grace_until unset.)
      return !m.grace_until || new Date(m.grace_until).getTime() > now;
    case "active":
      // A gift (or any prepaid row) only lasts until its end date, even if the expiry job hasn't run yet.
      if (m.plan === "gift") return periodOpen(m, now);
      return m.processor === "shopify" ? shopifyPaidThrough(m, now) : true;
    case "canceled":
      return periodOpen(m, now);
    default:
      // paused, refunded, expired, incomplete
      return false;
  }
}

/**
 * The membership that bills the member: a recurring plan that has not ended.
 * Cancel, pause, downgrade, refund and the partner seat act on this row, never on a gift (H3).
 */
export function pickBillingMembership(rows: Membership[], now = Date.now()): Membership | null {
  const recurring = rows
    .filter((r) => r.plan !== "gift" && !r.pending_verification && !(ENDED as readonly string[]).includes(r.status))
    .filter((r) => r.status !== "canceled" || periodOpen(r, now))
    .sort((a, b) => {
      // Prefer rows with a live processor subscription, then the newest.
      const live = Number(Boolean(b.stripe_subscription_id)) - Number(Boolean(a.stripe_subscription_id));
      return live !== 0 ? live : b.created_at.localeCompare(a.created_at);
    });
  return recurring[0] ?? null;
}

/** What the account page shows first: the billing membership, else a running gift, else the newest row. */
export function pickCurrentMembership(rows: Membership[], now = Date.now()): Membership | null {
  const billing = pickBillingMembership(rows, now);
  if (billing) return billing;
  const newest = [...rows].filter((r) => !r.pending_verification).sort((a, b) => b.created_at.localeCompare(a.created_at));
  return newest.find((r) => grantsAccess(r, now)) ?? newest.find((r) => !(ENDED as readonly string[]).includes(r.status)) ?? newest[0] ?? null;
}

export type AccessReason = "ok" | "none" | "paused" | "refunded" | "ended";

export interface Entitlement {
  access: boolean;
  reason: AccessReason;
  /** The row that grants access (if any). */
  granting: Membership | null;
}

export function entitlementFor(rows: Membership[], now = Date.now()): Entitlement {
  const granting = [...rows].sort((a, b) => b.created_at.localeCompare(a.created_at)).find((r) => grantsAccess(r, now)) ?? null;
  if (granting) return { access: true, reason: "ok", granting };
  if (rows.length === 0) return { access: false, reason: "none", granting: null };
  if (rows.some((r) => r.status === "paused")) return { access: false, reason: "paused", granting: null };
  if (rows.some((r) => r.status === "refunded")) return { access: false, reason: "refunded", granting: null };
  return { access: false, reason: "ended", granting: null };
}

/**
 * AUDIT_BUSINESS F08: the keep-forever bonus material (program PDFs, the launch-week
 * bonus) vests on day 15, after the 14-day money-back window. Daily sessions in the
 * app are available from day 1. Gifts have no refund window, so they vest at once.
 */
export function bonusUnlockAt(m: Pick<Membership, "plan" | "guarantee_until"> | null): Date | null {
  if (!m || m.plan === "gift" || !m.guarantee_until) return null;
  return new Date(m.guarantee_until);
}

export function bonusUnlocked(m: Pick<Membership, "plan" | "guarantee_until"> | null, now = Date.now()): boolean {
  const at = bonusUnlockAt(m);
  return !at || at.getTime() <= now;
}
