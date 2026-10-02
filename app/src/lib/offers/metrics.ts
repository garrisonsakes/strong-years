/**
 * Money-per-person metrics (MONETIZATION_ENGINE.md §6), shown in the /admin/today monetization panel.
 *
 *  RPV  revenue per visitor  = paid revenue (first orders + bumps + gifts, net of refunds) in the window
 *                              / distinct visitors who hit an offer surface (/b, /go, gift page) in the window
 *  RPC  revenue per conversation = revenue whose last touch was a DM (utm_medium=dm) in the window
 *                              / DM conversations started in the window (workers GET /dm/stats)
 *  Take rate per rung        = buyers of the rung / the people who could buy it (definitions inline below)
 *
 * Renewals are excluded from RPV/RPC (they measure the offer, not retention; renewal 1 has its own tile).
 */
import type { Store } from "../db/store";
import type { Order } from "../db/types";
import { readout, type ArmReadout } from "./experiments";

const DAY = 86_400_000;
type Fetcher = (url: string, init?: RequestInit) => Promise<Response>;

export interface DmStats { conversations: number; qualified: number; routed: Record<string, number> }

/** GET {DM_WORKER_URL|GROWTH_WORKER_URL}/dm/stats. Never throws. */
export async function fetchDmStats(days: number, fetcher: Fetcher = fetch): Promise<{ stats: DmStats | null; error: string | null }> {
  const base = (process.env.DM_WORKER_URL ?? process.env.GROWTH_WORKER_URL ?? "").replace(/\/$/, "");
  const token = process.env.WORKER_TOKEN ?? "";
  if (!base || !token) return { stats: null, error: "DM worker not connected" };
  try {
    const res = await fetcher(`${base}/dm/stats?days=${days}`, { headers: { "X-Worker-Token": token }, signal: AbortSignal.timeout(8000), cache: "no-store" });
    if (!res.ok) return { stats: null, error: `DM worker answered ${res.status}` };
    const j = (await res.json()) as Partial<DmStats>;
    return { stats: { conversations: Number(j.conversations) || 0, qualified: Number(j.qualified) || 0, routed: j.routed ?? {} }, error: null };
  } catch (e) {
    return { stats: null, error: `DM worker unreachable (${(e as Error).name})` };
  }
}

export interface TakeRate { rung: string; label: string; buyers: number; base: number; rate: number | null; definition: string }

export interface Monetization {
  days: number;
  visitors: number;
  revenue_cents: number;
  rpv_cents: number | null;
  dm: { conversations: number | null; revenue_cents: number; rpc_cents: number | null; qualified_share: number | null; error: string | null };
  takes: TakeRate[];
  arms: ArmReadout[];
}

const rate = (n: number, d: number) => (d > 0 ? n / d : null);

export async function computeMonetization(store: Store, now = new Date(), days = 7, fetcher: Fetcher = fetch): Promise<Monetization> {
  const since = new Date(now.getTime() - days * DAY).toISOString();
  const sinceDay = since.slice(0, 10);
  const [orders, exposures, conversions, dm, arms] = await Promise.all([
    store.find("sy_orders", { created_at: { gte: since }, is_demo: false }, { limit: 50_000 }),
    store.find("offer_events", { kind: "exposure", day: { gte: sinceDay } }, { limit: 50_000 }),
    store.find("offer_events", { kind: "conversion", day: { gte: sinceDay } }, { limit: 50_000 }),
    fetchDmStats(days, fetcher),
    readout(store, now, days),
  ]);
  const paid = orders.filter((o) => o.status !== "refunded");
  // A renewal order line is a membership charge on an offer code the member already had; the conversion log only
  // records first purchases (logConversion skips renewals), so revenue for RPV/RPC comes from it.
  const revenue = conversions.reduce((s, c) => s + c.revenue_cents, 0);
  const visitors = new Set(exposures.filter((e) => ["b", "go", "tt", "gift_page"].includes(e.surface)).map((e) => e.visitor_id ?? `m:${e.member_id}`)).size;
  const dmRevenue = conversions.filter((c) => c.channel === "dm").reduce((s, c) => s + c.revenue_cents, 0);
  const conv = dm.stats?.conversations ?? null;

  const code = (o: Order) => o.offer_code ?? "";
  const buyersOf = (pred: (o: Order) => boolean) => new Set(paid.filter(pred).map((o) => o.member_id ?? o.id)).size;
  const books = buyersOf((o) => o.kind === "front_end" || /^bundle_m12/.test(code(o)));
  const members = buyersOf((o) => o.kind === "membership_charge");
  const takes: TakeRate[] = [
    { rung: "R0", label: "Starter (books or $12 bundle)", buyers: books, base: visitors, rate: rate(books, visitors), definition: "first-order buyers / offer-surface visitors" },
    { rung: "bump", label: "Order bump ($9 / $29)", buyers: buyersOf((o) => o.kind === "bump"), base: books, rate: rate(buyersOf((o) => o.kind === "bump"), books), definition: "bump buyers / starter buyers" },
    { rung: "R1", label: "Books-only → membership", buyers: buyersOf((o) => /^founding_monthly|^standard_monthly/.test(code(o))), base: buyersOf((o) => o.kind === "front_end"), rate: rate(buyersOf((o) => /^founding_monthly|^standard_monthly/.test(code(o))), buyersOf((o) => o.kind === "front_end")), definition: "plain-membership buyers / books-only buyers (cell A)" },
    { rung: "R1a", label: "Annual", buyers: buyersOf((o) => /annual|prepaid/.test(code(o))), base: members, rate: rate(buyersOf((o) => /annual|prepaid/.test(code(o))), members), definition: "annual or prepaid-12 buyers / members charged" },
    { rung: "G", label: "Gift", buyers: buyersOf((o) => o.kind === "gift"), base: books + buyersOf((o) => o.kind === "gift"), rate: rate(buyersOf((o) => o.kind === "gift"), books + buyersOf((o) => o.kind === "gift")), definition: "gift buyers / all first-order buyers" },
    { rung: "R3", label: "Coached", buyers: buyersOf((o) => /^coached/.test(code(o))), base: members, rate: rate(buyersOf((o) => /^coached/.test(code(o))), members), definition: "coached buyers / members charged" },
  ];
  return {
    days,
    visitors,
    revenue_cents: revenue,
    rpv_cents: visitors ? Math.round(revenue / visitors) : null,
    dm: { conversations: conv, revenue_cents: dmRevenue, rpc_cents: conv ? Math.round(dmRevenue / conv) : null, qualified_share: dm.stats && conv ? dm.stats.qualified / conv : null, error: dm.error },
    takes,
    arms,
  };
}
