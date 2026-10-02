/**
 * Experiment framework for offer surfaces (MONETIZATION_ENGINE.md §5). Every surface is a named experiment in
 * routing.json with sticky arms; every exposure and every paid order line lands in `offer_events` (the offer
 * attribution table); the weekly readout is revenue per visitor (RPV) by arm.
 *
 * Guardrails (code, not policy text):
 *  - one price per person: a price arm is locked to the first arm logged for that subject, even if the arm list or
 *    salt changes later;
 *  - never raise a shown price: within `never_raise_shown_price_days`, an offer family's price for a subject never
 *    goes above the lowest price already shown to them (lockedPrice tells the caller to keep the earlier offer).
 */
import { fnv1a } from "../blitz";
import type { Store } from "../db/store";
import type { OfferEvent } from "../db/types";
import { ROUTING } from "./route";

export interface Experiment { id: string; surface: string; arms: string[]; price_arm: boolean; salt: string; hash?: string; metric: string }
export const EXPERIMENTS = ROUTING.experiments as Experiment[];

/** murmur3 finalizer: plain fnv1a % 2 is the parity of the odd characters, so 2-arm tests would be confounded. */
export function fmix32(h: number): number {
  h ^= h >>> 16;
  h = Math.imul(h, 0x85ebca6b) >>> 0;
  h ^= h >>> 13;
  h = Math.imul(h, 0xc2b2ae35) >>> 0;
  h ^= h >>> 16;
  return h >>> 0;
}

/** Sticky arm; identical to workers/dm/routing.py assign(). fe_cell mirrors the live cell hash (plain fnv1a). */
export function assignArm(experimentId: string, subject: string | null | undefined): string | null {
  const e = EXPERIMENTS.find((x) => x.id === experimentId);
  if (!e || !subject) return null;
  let h = fnv1a(`${e.salt}:${subject}`);
  if (e.hash !== "fnv1a") h = fmix32(h);
  return e.arms[h % e.arms.length] ?? null;
}

export interface Subject { visitorId: string | null; memberId: string | null }
const VID = /^[0-9a-f-]{36}$/;
const today = (now: Date) => now.toISOString().slice(0, 10);

async function subjectEvents(store: Store, s: Subject, filter: Partial<Pick<OfferEvent, "kind" | "experiment" | "offer">>): Promise<OfferEvent[]> {
  const out: OfferEvent[] = [];
  if (s.visitorId && VID.test(s.visitorId)) out.push(...(await store.find("offer_events", { ...filter, visitor_id: s.visitorId }, { orderBy: "created_at", limit: 200 })));
  if (s.memberId) out.push(...(await store.find("offer_events", { ...filter, member_id: s.memberId }, { orderBy: "created_at", limit: 200 })));
  return out.sort((a, b) => a.created_at.localeCompare(b.created_at));
}

/** The arm this subject sees: the first arm ever logged for a price experiment (one price per person), else the hash. */
export async function armFor(store: Store, experimentId: string, s: Subject): Promise<string | null> {
  const e = EXPERIMENTS.find((x) => x.id === experimentId);
  if (!e) return null;
  if (e.price_arm) {
    const first = (await subjectEvents(store, s, { kind: "exposure", experiment: experimentId })).find((x) => x.arm);
    if (first?.arm) return first.arm;
  }
  return assignArm(experimentId, s.visitorId ?? s.memberId);
}

/**
 * Never raise a shown price: the lowest price shown to this subject for this offer family inside the window, or null.
 * A caller about to show a higher price keeps the earlier offer instead.
 */
export async function lockedPrice(store: Store, offer: string, s: Subject, now = new Date()): Promise<number | null> {
  const days = ROUTING.guardrails.never_raise_shown_price_days;
  const since = new Date(now.getTime() - days * 86_400_000).toISOString();
  const shown = (await subjectEvents(store, s, { kind: "exposure", offer })).filter((x) => x.created_at >= since && x.shown_price_cents !== null);
  return shown.length ? Math.min(...shown.map((x) => x.shown_price_cents!)) : null;
}

export function violatesRaise(locked: number | null, proposedCents: number | null): boolean {
  return locked !== null && proposedCents !== null && proposedCents > locked;
}

/** One exposure row per (subject, surface, experiment, offer, day). Never throws: measurement never blocks a sale. */
export async function logExposure(
  store: Store,
  x: { subject: Subject; surface: string; offer: string; experiment?: string | null; arm?: string | null; rule?: string | null; shownPriceCents?: number | null; channel?: string | null },
  now = new Date(),
): Promise<void> {
  try {
    const visitor_id = x.subject.visitorId && VID.test(x.subject.visitorId) ? x.subject.visitorId : null;
    const member_id = x.subject.memberId ?? null;
    if (!visitor_id && !member_id) return;
    const day = today(now);
    const dup = await store.findOne("offer_events", { kind: "exposure", visitor_id, member_id, surface: x.surface, experiment: x.experiment ?? null, offer: x.offer, day });
    if (dup) return;
    await store.insert("offer_events", {
      kind: "exposure", visitor_id, member_id, surface: x.surface.slice(0, 40), experiment: x.experiment ?? null, arm: x.arm ?? null,
      offer: x.offer.slice(0, 40), rule: x.rule ?? null, shown_price_cents: x.shownPriceCents ?? null, revenue_cents: 0,
      channel: x.channel ?? null, ref: null, day,
    });
  } catch {
    /* measurement only */
  }
}

/** orders/paid line → a conversion row (unique per line). Never throws. */
export async function logConversion(store: Store, x: { visitorId: string | null; memberId: string | null; offer: string; revenueCents: number; ref: string; channel?: string | null }, now = new Date()): Promise<void> {
  try {
    if (await store.findOne("offer_events", { kind: "conversion", ref: x.ref })) return;
    await store.insert("offer_events", {
      kind: "conversion", visitor_id: x.visitorId && VID.test(x.visitorId) ? x.visitorId : null, member_id: x.memberId, surface: "order",
      experiment: null, arm: null, offer: x.offer.slice(0, 40), rule: null, shown_price_cents: null, revenue_cents: Math.max(0, Math.round(x.revenueCents)),
      channel: x.channel ?? null, ref: x.ref.slice(0, 120), day: today(now),
    });
  } catch {
    /* measurement only */
  }
}

export interface ArmReadout { experiment: string; arm: string; visitors: number; buyers: number; revenue_cents: number; rpv_cents: number; conversion: number }

/**
 * Weekly readout: for each (experiment, arm), distinct subjects exposed in the window, and the revenue of their
 * conversions on or after their first exposure (any offer: RPV is the whole-funnel number the gates use).
 */
export async function readout(store: Store, now = new Date(), days = 7): Promise<ArmReadout[]> {
  const since = today(new Date(now.getTime() - days * 86_400_000));
  const exp = await store.find("offer_events", { kind: "exposure", day: { gte: since } }, { limit: 50_000 });
  const conv = await store.find("offer_events", { kind: "conversion", day: { gte: since } }, { limit: 50_000 });
  const revByVid = new Map<string, OfferEvent[]>();
  const revByMember = new Map<string, OfferEvent[]>();
  for (const c of conv) {
    if (c.visitor_id) revByVid.set(c.visitor_id, [...(revByVid.get(c.visitor_id) ?? []), c]);
    if (c.member_id) revByMember.set(c.member_id, [...(revByMember.get(c.member_id) ?? []), c]);
  }
  // "exp|arm" → subject (visitor id, else member id) → first exposure + the ids it carries
  const groups = new Map<string, Map<string, { first: string; vid: string | null; mid: string | null }>>();
  for (const e of exp) {
    if (!e.experiment || !e.arm) continue;
    const g = `${e.experiment}|${e.arm}`;
    const m = groups.get(g) ?? new Map();
    const k = e.visitor_id ?? `m:${e.member_id}`;
    const cur = m.get(k);
    m.set(k, { first: cur && cur.first < e.created_at ? cur.first : e.created_at, vid: e.visitor_id ?? cur?.vid ?? null, mid: e.member_id ?? cur?.mid ?? null });
    groups.set(g, m);
  }
  const out: ArmReadout[] = [];
  for (const [g, subjects] of groups) {
    const [experiment, arm] = g.split("|") as [string, string];
    let revenue = 0;
    let buyers = 0;
    for (const s of subjects.values()) {
      const seen = new Set<string>();
      const rows = [...(s.vid ? revByVid.get(s.vid) ?? [] : []), ...(s.mid ? revByMember.get(s.mid) ?? [] : [])].filter((r) => r.created_at >= s.first && !seen.has(r.id) && seen.add(r.id));
      const rev = rows.reduce((t, r) => t + r.revenue_cents, 0);
      if (rev > 0) {
        revenue += rev;
        buyers += 1;
      }
    }
    const visitors = subjects.size;
    out.push({ experiment, arm, visitors, buyers, revenue_cents: revenue, rpv_cents: visitors ? Math.round(revenue / visitors) : 0, conversion: visitors ? buyers / visitors : 0 });
  }
  return out.sort((a, b) => a.experiment.localeCompare(b.experiment) || b.rpv_cents - a.rpv_cents);
}
