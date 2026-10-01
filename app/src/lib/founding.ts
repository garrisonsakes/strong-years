import { billingProviderId } from "./billing/provider";
import { offerRules } from "./config";
/**
 * Round 8 (AUDIT_FINAL §7): the founding cap is enforced atomically.
 *
 * A founding checkout takes a spot when its checkout session is created, under a
 * lock (Postgres: pg_advisory_xact_lock inside reserve_founding_spot(); in-memory
 * store: a per-process mutex). The hold lasts FOUNDING_HOLD_MINUTES, longer than the
 * Stripe session (CHECKOUT_SESSION_MINUTES), so anyone who pays in time still holds
 * the spot. Fulfilment confirms the hold (same lock). A buyer who can't get a spot is
 * told before paying and sees the standard price on reload; nobody is ever charged
 * the founding price beyond the cap.
 *
 * Spots taken = founding memberships (refunds release the spot)
 *             + unexpired holds
 *             + confirmed holds whose membership row isn't written yet.
 */
import type { Store } from "./db/store";
import type { CheckoutIntent, FoundingHold } from "./db/types";

export const CHECKOUT_SESSION_MINUTES = 30;
export const FOUNDING_HOLD_MINUTES = 45;
const COUNTED = ["active", "past_due", "paused", "canceled", "expired"] as const;

/** Same rule fulfilment uses for `memberships.founding`. */
export function holdsFoundingSpot(i: Pick<CheckoutIntent, "arm" | "trial_days" | "membership_price_cents" | "price_cell" | "gift">): boolean {
  return i.arm === "B" && i.trial_days === 0 && i.membership_price_cents !== null && i.price_cell !== "standard" && !i.gift;
}

/** Everything that currently occupies a founding spot. `exceptIntent` leaves out one checkout's own hold. */
export async function foundingTaken(store: Store, now = new Date(), exceptIntent?: string): Promise<number> {
  // Shopify mode: the cap is inventory on the founding plan; the counter reads its DB mirror.
  if (billingProviderId() === "shopify") {
    const { shopifyFoundingTaken } = await import("./billing/shopifyWebhook");
    return shopifyFoundingTaken(store, offerRules.foundingCap);
  }
  const members = await store.find("memberships", { founding: true, status: { in: [...COUNTED] } });
  const holds = await store.find("founding_holds", { status: { in: ["held", "confirmed"] } });
  const withMembership = new Set(members.map((m) => m.checkout_intent_id).filter(Boolean));
  const nowIso = now.toISOString();
  let n = members.length;
  for (const h of holds) {
    if (h.intent_id === exceptIntent) continue;
    if (h.status === "held" && h.expires_at > nowIso) n++;
    else if (h.status === "confirmed" && !withMembership.has(h.intent_id)) n++;
  }
  return n;
}

/* ---- in-memory lock (one process; Postgres uses an advisory lock instead) ---- */
const locks = new WeakMap<Store, Promise<unknown>>();
async function withLock<T>(store: Store, fn: () => Promise<T>): Promise<T> {
  const prev = locks.get(store) ?? Promise.resolve();
  let release!: () => void;
  const mine = new Promise<void>((r) => (release = r));
  locks.set(store, prev.then(() => mine));
  await prev.catch(() => undefined);
  try {
    return await fn();
  } finally {
    release();
  }
}

async function upsertHold(store: Store, intentId: string, patch: Partial<FoundingHold>): Promise<void> {
  const existing = await store.findOne("founding_holds", { intent_id: intentId });
  if (existing) await store.update("founding_holds", existing.id, patch);
  else await store.insert("founding_holds", { intent_id: intentId, status: "held", confirmed_at: null, expires_at: new Date().toISOString(), ...patch });
}

/** Atomically takes a spot for this checkout, or returns false when the cohort is full. */
export async function reserveFoundingSpot(store: Store, intentId: string, cap: number, now = new Date()): Promise<boolean> {
  if (store.rpc) return Boolean(await store.rpc("reserve_founding_spot", { p_intent_id: intentId, p_cap: cap, p_hold_minutes: FOUNDING_HOLD_MINUTES }));
  return withLock(store, async () => {
    if ((await foundingTaken(store, now, intentId)) >= cap) return false;
    await upsertHold(store, intentId, { status: "held", expires_at: new Date(now.getTime() + FOUNDING_HOLD_MINUTES * 60_000).toISOString() });
    return true;
  });
}

/**
 * At fulfilment: confirm this checkout's spot. An unexpired hold is simply confirmed;
 * an expired or missing one (a very late webhook) is re-checked against the cap under
 * the same lock. False means the buyer is over the cap and must not get founding.
 */
export async function confirmFoundingSpot(store: Store, intentId: string, cap: number, now = new Date()): Promise<boolean> {
  if (store.rpc) return Boolean(await store.rpc("confirm_founding_spot", { p_intent_id: intentId, p_cap: cap }));
  return withLock(store, async () => {
    const h = await store.findOne("founding_holds", { intent_id: intentId });
    if (h?.status === "confirmed") return true;
    const live = h?.status === "held" && h.expires_at > now.toISOString();
    if (!live && (await foundingTaken(store, now, intentId)) >= cap) {
      if (h) await store.update("founding_holds", h.id, { status: "released" });
      return false;
    }
    await upsertHold(store, intentId, { status: "confirmed", confirmed_at: now.toISOString() });
    return true;
  });
}

/** Stripe session expired / checkout abandoned: give the spot back now. */
export async function releaseFoundingSpot(store: Store, intentId: string): Promise<void> {
  await store.updateWhere("founding_holds", { intent_id: intentId, status: "held" }, { status: "released" });
}
