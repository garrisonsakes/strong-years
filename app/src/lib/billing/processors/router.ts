/**
 * Processor routing (pure; unit tested). BLITZ.md "what must be true" #5: a second
 * processor before volume outgrows the first, and never route past a processor's
 * approved volume. Two strategies:
 *  - failover: primary (Stripe) unless it's unavailable or over its 30-day volume cap
 *  - split:    a deterministic share of checkouts to Braintree, the rest to Stripe,
 *              each still subject to its cap (spill to the other)
 */
import { fnv1a } from "../../blitz";
import type { ProcessorId } from "../../db/types";

export interface Candidate {
  id: ProcessorId;
  available: boolean;
  volume30dCents: number;
  /** 0 = uncapped */
  capCents: number;
}

export interface RouteInput {
  routing: "failover" | "split";
  braintreeShare: number;
  /** Stable key (e.g. checkout intent id or visitor id) for deterministic splitting. */
  key: string;
  amountCents: number;
  candidates: Candidate[];
  primary?: ProcessorId;
}

export interface RouteResult {
  id: ProcessorId | null;
  reason: "primary" | "split" | "failover_unavailable" | "failover_capped" | "all_capped" | "none_available";
  overCap: boolean;
}

export function underCap(c: Candidate, amount: number): boolean {
  return c.capCents <= 0 || c.volume30dCents + amount <= c.capCents;
}

export function chooseProcessor(i: RouteInput): RouteResult {
  const primary = i.primary ?? "stripe";
  const available = i.candidates.filter((c) => c.available);
  if (available.length === 0) return { id: null, reason: "none_available", overCap: false };
  const eligible = available.filter((c) => underCap(c, i.amountCents));
  const byId = (id: ProcessorId) => eligible.find((c) => c.id === id);

  if (i.routing === "split" && i.braintreeShare > 0) {
    const wantBraintree = fnv1a(`route:${i.key}`) % 10_000 < Math.round(i.braintreeShare * 10_000);
    const want = wantBraintree ? byId("braintree") : byId("stripe");
    if (want) return { id: want.id, reason: "split", overCap: false };
  }
  const p = byId(primary);
  if (p) return { id: p.id, reason: "primary", overCap: false };
  const other = eligible[0];
  if (other) {
    const primaryAvailable = available.some((c) => c.id === primary);
    return { id: other.id, reason: primaryAvailable ? "failover_capped" : "failover_unavailable", overCap: false };
  }
  // Everything is over its cap: keep selling on the available processor with the most headroom,
  // and flag it so a human is alerted (never silently drop a paying customer).
  const best = [...available].sort((a, b) => (a.capCents - a.volume30dCents) - (b.capCents - b.volume30dCents)).pop()!;
  return { id: best.id, reason: "all_capped", overCap: true };
}
