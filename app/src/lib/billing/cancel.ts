/**
 * Cancel flow rules (FUNNEL.md 7.8, OFFER.md 2.3/5.4, SAFETY_RULES.md S-02):
 * cancel online in at most two screens, one save offer shown next to an equally
 * prominent "Finish canceling" button. Tapping it cancels immediately.
 * Never handled by the AI characters. Pure functions here; side effects in actions.ts.
 */
import type { Membership } from "../db/types";

export const CANCEL_REASONS = [
  { code: "expensive", label: "It's too expensive" },
  { code: "no_time", label: "I don't have time" },
  { code: "not_using", label: "I'm not using it enough" },
  { code: "difficulty", label: "It's too hard, or too easy" },
  { code: "unwell", label: "I'm injured or unwell" },
  { code: "traveling", label: "I'm traveling" },
  { code: "human", label: "I want a real person, or something different" },
  { code: "other", label: "Other" },
] as const;

export type CancelReason = (typeof CANCEL_REASONS)[number]["code"];

export function isCancelReason(v: unknown): v is CancelReason {
  return typeof v === "string" && CANCEL_REASONS.some((r) => r.code === v);
}

export type SaveOffer =
  | { kind: "downgrade"; heading: string; body: string; button: string; priceCents: number }
  | { kind: "pause"; heading: string; body: string; button: string; months: [1, 2, 3] };

export const ESSENTIALS_CENTS = 1200;

/** Exactly one save offer per cancellation: pause, or downgrade to Essentials $12. */
export function saveOfferFor(reason: CancelReason | null, membership: Pick<Membership, "plan" | "price_cents">): SaveOffer {
  const canDowngrade = membership.plan === "monthly" && membership.price_cents > ESSENTIALS_CENTS;
  if (reason === "expensive" && canDowngrade) {
    return {
      kind: "downgrade",
      heading: "Switch to Essentials for $12 a month instead?",
      body: "You keep your Daily Practice, the daily message and the monthly Strength Age retest. No AI chat, live Q&A or programs. It starts at your next charge date.",
      button: "Switch to $12 a month",
      priceCents: ESSENTIALS_CENTS,
    };
  }
  const unwell = reason === "unwell";
  return {
    kind: "pause",
    heading: unwell ? "We're sorry. Pause free while you recover?" : "Pause for 1, 2 or 3 months, free?",
    body: unwell
      ? "Nothing is charged while paused, and when you come back we'll start you on the Rebuild track. Please follow your doctor's advice. We'll remind you a week before it restarts."
      : "Nothing is charged while paused. Your streak, Strength Age history and what the coach remembers are kept. We'll remind you a week before it restarts.",
    button: "Pause my membership",
    months: [1, 2, 3],
  };
}

/** The flow's screens, for tests and for the UI. Screen 2 is never followed by a third. */
export function cancelFlowScreens(): ["reason", "offer"] {
  return ["reason", "offer"];
}

export function withinGuarantee(m: Pick<Membership, "guarantee_until" | "status">, now = Date.now()): boolean {
  if (!m.guarantee_until) return false;
  if (m.status === "refunded") return false;
  return new Date(m.guarantee_until).getTime() >= now;
}

/** Access continues until the end of the paid (or trial) period after cancelling. */
export function accessUntil(m: Pick<Membership, "current_period_end" | "trial_end" | "status">): string | null {
  return m.current_period_end ?? m.trial_end ?? null;
}
