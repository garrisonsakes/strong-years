/**
 * Blitz pricing logic (pure; unit tested).
 * - Deterministic, sticky 50/50 price assignment from the visitor id cookie (sy_vid):
 *   the same visitor always gets the same cell, on any server, with no DB lookup.
 * - Real cohort cap: the founding price is only offered while the DB count is under the cap.
 *   After it closes, new members pay the configurable standard price with no founding lock.
 */
export const VID_COOKIE = "sy_vid";

/** FNV-1a 32-bit hash. Stable across runtimes (edge + node). */
export function fnv1a(input: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h >>> 0;
}

export function assignPriceCell(visitorId: string, cells: number[], salt = "blitz-price-v1"): number {
  if (cells.length === 0) throw new Error("no price cells");
  return cells[fnv1a(`${salt}:${visitorId}`) % cells.length]!;
}

export interface FoundingOfferInput {
  visitorId: string | null;
  claimed: number;
  cap: number;
  testOn: boolean;
  cells: number[];
  defaultCents: number;
  standardCents: number;
}

export interface FoundingOffer {
  cohortOpen: boolean;
  founding: boolean;
  priceCents: number;
  /** e.g. "p2500" when the visitor is in the price test, "default", or "standard" after the cap. */
  cell: string;
  claimed: number;
  cap: number;
  left: number;
}

export function resolveFoundingOffer(i: FoundingOfferInput): FoundingOffer {
  const left = Math.max(0, i.cap - i.claimed);
  const base = { claimed: i.claimed, cap: i.cap, left };
  if (left <= 0) return { ...base, cohortOpen: false, founding: false, priceCents: i.standardCents, cell: "standard" };
  if (i.testOn && i.visitorId) {
    const price = assignPriceCell(i.visitorId, i.cells);
    return { ...base, cohortOpen: true, founding: true, priceCents: price, cell: `p${price}` };
  }
  return { ...base, cohortOpen: true, founding: true, priceCents: i.defaultCents, cell: "default" };
}

/** Sticky arm from the (signed) visitor id: "B" founding charge-today, "A" the $1 trial. */
export function assignArm(visitorId: string, armBShare: number, salt = "blitz-arm-v1"): "A" | "B" {
  return fnv1a(`${salt}:${visitorId}`) % 10_000 < Math.round(armBShare * 10_000) ? "B" : "A";
}

/** The test cell a visitor is in: "p2500" / "p3000" (founding), "trial2500" (trial), or "standard". */
export function testCell(arm: "A" | "B", offer: Pick<FoundingOffer, "cell" | "cohortOpen">, trialPriceCents: number): string {
  if (arm === "A") return offer.cohortOpen ? `trial${trialPriceCents}` : "trial_standard";
  return offer.cell;
}
