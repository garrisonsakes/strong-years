/**
 * Builds the routing context for a known member (MONETIZATION_ENGINE.md §2): what they already own, how long they've
 * been paying, how long ago their last paid period ended. Pure over the rows passed in.
 */
import type { Membership, Order } from "../db/types";
import type { RouteContext } from "./route";

const DAY = 86_400_000;
const LIVE = new Set(["active", "past_due", "trialing", "paused"]);

export function memberContext(memberships: Membership[], orders: Order[], now = new Date()): Pick<RouteContext, "prior" | "member_months" | "lapse_days"> {
  const prior = new Set<string>();
  const paid = orders.filter((o) => o.status !== "refunded");
  if (paid.some((o) => o.kind === "front_end" || /^bundle_m12/.test(o.offer_code))) prior.add("books");
  if (paid.some((o) => o.kind === "gift")) prior.add("gift_buyer");
  if (paid.some((o) => /^coached/.test(o.offer_code))) prior.add("coached");
  const live = memberships.filter((m) => LIVE.has(m.status) && m.plan !== "gift");
  if (live.length) prior.add("member");
  if (live.some((m) => m.plan === "annual")) prior.add("annual");
  const charges = paid.filter((o) => o.kind === "membership_charge").length;
  const out: Pick<RouteContext, "prior" | "member_months" | "lapse_days"> = { prior: [...prior] };
  if (live.length) out.member_months = Math.max(0, charges - 1);
  else {
    const ended = memberships
      .filter((m) => m.plan !== "gift" && ["canceled", "expired"].includes(m.status) && m.current_period_end)
      .map((m) => new Date(m.current_period_end!).getTime())
      .filter((t) => t <= now.getTime());
    if (ended.length) out.lapse_days = Math.floor((now.getTime() - Math.max(...ended)) / DAY);
  }
  return out;
}
