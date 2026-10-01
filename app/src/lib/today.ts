/**
 * /admin/today: one screen of the numbers that decide the day. Money and member
 * numbers come from our own tables; reach, post scores and the spend governor come
 * from the workers' growth API (GET /growth/summary). When something isn't
 * connected or has no data yet, the field is null and the page says so: nothing
 * is estimated or filled in.
 */
import type { Store } from "./db/store";
import type { Membership } from "./db/types";
import { growthReport, type PostRow } from "./growth";
import { foundingClaimed, mrrCents } from "./members";
import { offerRules } from "./config";

export interface WorkerPost {
  post_id: string;
  views_24h?: number | null;
  score?: number | null;
  class?: string | null;
}

export interface GateCheck {
  name: string;
  status: string;
  value: number | null;
  line: number | string | null;
  why?: string;
}

export interface WorkerSummary {
  reach_24h: number | null;
  posts: WorkerPost[];
  governor: {
    status: string;
    mode: string;
    spend_enabled: boolean;
    planned_daily_usd: number;
    decided_at: string | null;
    blitz9: GateCheck[];
    graduation: { passed: boolean; checks: GateCheck[] } | null;
  } | null;
}

export interface TodayPost extends PostRow {
  views_24h: number | null;
  score: number | null;
  class: string | null;
}

export interface Today {
  generated_at: string;
  reach_24h: number | null;
  waitlist: { confirmed: number; new24h: number };
  buyers: { books: number; new24h: number };
  members: { paying: number; new24h: number };
  mrr: { total: number; new30d: number; lost30d: number; net30d: number };
  renewal1: { due: number; renewed: number; rate: number | null };
  refunds: { count30d: number; cents30d: number; rate30d: number | null };
  chargebacks: { count30d: number; ratio30d: number | null };
  founding: { claimed: number; cap: number; left: number };
  top: TodayPost[];
  weakest: TodayPost[];
  workers: { connected: boolean; error: string | null; governor: WorkerSummary["governor"] };
  openExceptions: number;
}

type Fetcher = (url: string, init?: RequestInit) => Promise<Response>;

/** GET {GROWTH_WORKER_URL}/growth/summary with X-Worker-Token. Never throws. */
export async function fetchWorkerSummary(fetcher: Fetcher = fetch): Promise<{ summary: WorkerSummary | null; error: string | null }> {
  const base = (process.env.GROWTH_WORKER_URL ?? process.env.QA_WORKER_URL ?? "").replace(/\/$/, "");
  const token = process.env.WORKER_TOKEN ?? "";
  if (!base || !token) return { summary: null, error: "not connected (GROWTH_WORKER_URL / WORKER_TOKEN unset)" };
  try {
    const res = await fetcher(`${base}/growth/summary`, { headers: { "X-Worker-Token": token }, signal: AbortSignal.timeout(8000), cache: "no-store" });
    if (!res.ok) return { summary: null, error: `workers answered ${res.status}` };
    const j = (await res.json()) as Partial<WorkerSummary>;
    return {
      summary: {
        reach_24h: typeof j.reach_24h === "number" ? j.reach_24h : null,
        posts: Array.isArray(j.posts) ? j.posts.filter((p) => p && typeof p.post_id === "string").slice(0, 2000) : [],
        governor: j.governor ?? null,
      },
      error: null,
    };
  } catch (e) {
    return { summary: null, error: `workers unreachable (${(e as Error).name})` };
  }
}

const DAY = 86_400_000;
const isPaying = (m: Membership) => (m.status === "active" || m.status === "past_due") && m.plan !== "gift";

export async function computeToday(store: Store, now = new Date(), fetcher: Fetcher = fetch): Promise<Today> {
  const d1 = new Date(now.getTime() - DAY).toISOString();
  const d30 = new Date(now.getTime() - 30 * DAY).toISOString();
  const [waitlist, memberships, orders, growth, worker, openExceptions] = await Promise.all([
    store.find("waitlist"),
    store.find("memberships", { is_demo: false }),
    store.find("sy_orders", { is_demo: false }),
    growthReport(store, now),
    fetchWorkerSummary(fetcher),
    store.count("exceptions", { status: "open" }),
  ]);
  const confirmed = waitlist.filter((w) => w.status === "confirmed");
  const books = orders.filter((o) => o.kind === "front_end" || /^bundle_m12|^ebook_/.test(o.offer_code));
  const bookBuyers = new Set(books.filter((o) => o.status !== "refunded").map((o) => o.email));
  const newBookBuyers = new Set(books.filter((o) => o.created_at >= d1 && o.status !== "refunded").map((o) => o.email));
  const paying = memberships.filter(isPaying);

  // MRR movement over 30 days: new = paying memberships that started in the window; lost = memberships that ended in it.
  const newMrr = paying.filter((m) => (m.first_paid_at ?? m.created_at) >= d30).reduce((s, m) => s + mrrCents(m), 0);
  const lost = memberships.filter((m) => m.plan !== "gift" && m.canceled_at && m.canceled_at >= d30 && !isPaying(m));
  const lostMrr = lost.reduce((s, m) => s + Math.round(m.interval === "year" ? m.price_cents / 12 : m.price_cents), 0);

  // Renewal 1: monthly memberships whose first period has ended; renewed = a second paid membership charge exists.
  const charges = orders.filter((o) => o.kind === "membership_charge" && o.status === "paid");
  const chargesBy = new Map<string, number>();
  for (const o of charges) if (o.membership_id) chargesBy.set(o.membership_id, (chargesBy.get(o.membership_id) ?? 0) + 1);
  const due = memberships.filter((m) => m.interval === "month" && m.first_paid_at && new Date(m.first_paid_at).getTime() + 31 * DAY <= now.getTime());
  const renewed = due.filter((m) => (chargesBy.get(m.id) ?? 0) >= 2).length;

  const o30 = orders.filter((o) => o.created_at >= d30);
  const refunded30 = o30.filter((o) => o.status === "refunded" || o.amount_refunded_cents > 0);
  const disputed30 = o30.filter((o) => o.status === "disputed");
  const claimed = await foundingClaimed(store);

  const byId = new Map((worker.summary?.posts ?? []).map((p) => [p.post_id, p]));
  const posts: TodayPost[] = growth.last_touch.map((r) => {
    const w = byId.get(r.post_id);
    return { ...r, views_24h: w?.views_24h ?? null, score: w?.score ?? null, class: w?.class ?? null };
  });
  // Posts the workers scored but that drove nothing in our tables yet still count for "weakest".
  for (const w of worker.summary?.posts ?? []) {
    if (!posts.some((p) => p.post_id === w.post_id)) {
      posts.push({ post_id: w.post_id, platform: null, page: null, character: null, keywords: [], waitlist_signups: 0, waitlist_confirmed: 0, quiz_optins: 0, ebook_buyers: 0, members: 0, paying_members: 0, mrr_cents: 0, views_24h: w.views_24h ?? null, score: w.score ?? null, class: w.class ?? null });
    }
  }
  const value = (p: TodayPost) => p.mrr_cents * 1000 + p.members * 100 + p.ebook_buyers * 10 + p.waitlist_confirmed + (p.score ?? 0) / 100;
  const ranked = [...posts].sort((a, b) => value(b) - value(a) || a.post_id.localeCompare(b.post_id));
  const top = ranked.slice(0, 10);
  const weakest = ranked.length > 10 ? ranked.slice(-10).reverse() : [];

  return {
    generated_at: now.toISOString(),
    reach_24h: worker.summary?.reach_24h ?? null,
    waitlist: { confirmed: confirmed.length, new24h: confirmed.filter((w) => (w.confirmed_at ?? w.created_at) >= d1).length },
    buyers: { books: bookBuyers.size, new24h: newBookBuyers.size },
    members: { paying: paying.length, new24h: paying.filter((m) => (m.first_paid_at ?? m.created_at) >= d1).length },
    mrr: { total: paying.reduce((s, m) => s + mrrCents(m), 0), new30d: newMrr, lost30d: lostMrr, net30d: newMrr - lostMrr },
    renewal1: { due: due.length, renewed, rate: due.length ? renewed / due.length : null },
    refunds: { count30d: refunded30.length, cents30d: refunded30.reduce((s, o) => s + (o.amount_refunded_cents || o.amount_cents), 0), rate30d: o30.length ? refunded30.length / o30.length : null },
    chargebacks: { count30d: disputed30.length, ratio30d: o30.length ? disputed30.length / o30.length : null },
    founding: { claimed, cap: offerRules.foundingCap, left: Math.max(0, offerRules.foundingCap - claimed) },
    top,
    weakest,
    workers: { connected: !!worker.summary, error: worker.error, governor: worker.summary?.governor ?? null },
    openExceptions,
  };
}
