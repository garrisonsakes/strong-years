/**
 * Intent → offer routing (MONETIZATION_ENGINE.md §2). The table is data (./routing.json, a byte-identical copy of
 * workers/dm/offer_routing.json; the unit test checks both and runs the shared vectors). This file only evaluates it,
 * exactly like workers/dm/routing.py. A rule picks an offer FAMILY; the price comes from the catalog and the visitor's
 * sticky front-end cell. Pure: no I/O.
 */
import data from "./routing.json";

export type OfferId = keyof typeof data.offers;
export type Surface = "dm" | "b" | "go" | "tt" | "thank_you" | "email" | "app" | "product_page" | "gift_page";

export interface RouteContext {
  mode?: "runway" | "launch";
  surface?: Surface;
  keyword?: string | null;
  pillar?: string | null;
  platform?: string | null;
  page?: string | null;
  follower?: boolean | null;
  tagger?: boolean;
  audience?: "self" | "parent" | "group" | null;
  goal?: string | null;
  device?: "ios" | "android" | "desktop" | null;
  hour?: number | null;
  country?: string | null;
  state?: string | null;
  prior?: string[];
  member_months?: number | null;
  waitlist_age_days?: number | null;
  opened_recently?: boolean | null;
  lapse_days?: number | null;
  plateau?: boolean;
  hardship?: boolean;
}

export interface Bump { sku: string; frame: string; second: string | null }
export interface Route { offer: OfferId; rule: string; variant?: string; alt?: OfferId; prefer_email?: boolean; bump?: Bump }

export const ROUTING = data;

type Cond = unknown;

function cond(value: unknown, c: Cond): boolean {
  if (c !== null && typeof c === "object" && !Array.isArray(c)) {
    for (const [op, arg] of Object.entries(c as Record<string, unknown>)) {
      if (op === "exists") {
        if ((value !== null && value !== undefined) !== Boolean(arg)) return false;
        continue;
      }
      if (op === "lacks") {
        if (Array.isArray(value) && value.includes(arg)) return false;
        continue;
      }
      if (value === null || value === undefined) return false;
      if (op === "in" && !(arg as unknown[]).includes(value)) return false;
      if (op === "nin" && (arg as unknown[]).includes(value)) return false;
      if (op === "has" && !(Array.isArray(value) && value.includes(arg))) return false;
      if (op === "lt" || op === "lte" || op === "gt" || op === "gte") {
        if (typeof value !== "number" || !Number.isFinite(value)) return false;
        const n = arg as number;
        if ((op === "lt" && !(value < n)) || (op === "lte" && !(value <= n)) || (op === "gt" && !(value > n)) || (op === "gte" && !(value >= n))) return false;
      }
    }
    return true;
  }
  if (value === null || value === undefined) return false;
  if (Array.isArray(c)) return c.includes(value);
  return value === c;
}

export function matches(ctx: RouteContext, when: Record<string, Cond>): boolean {
  return Object.entries(when).every(([k, c]) => cond((ctx as Record<string, unknown>)[k], c));
}

export function bumpFor(pillar: string | null | undefined): Bump | null {
  const by = data.bumps.by_pillar as Record<string, { sku: string | null; frame: string | null; second: string | null }>;
  const b = by[pillar ?? "general"] ?? by.general!;
  return b.sku && b.frame ? { sku: b.sku, frame: b.frame, second: b.second } : null;
}

export function route(input: RouteContext): Route {
  const ctx: RouteContext = { ...input };
  if (ctx.keyword && !ctx.pillar) ctx.pillar = (data.keyword_pillar as Record<string, string>)[ctx.keyword.toUpperCase()] ?? "general";
  if (ctx.goal && ctx.goal !== "start") ctx.pillar = ctx.goal;
  for (const r of data.rules as { id: string; when: Record<string, Cond>; offer: string; variant?: string; alt?: string; prefer_email?: boolean }[]) {
    if (!matches(ctx, r.when)) continue;
    const offer = (data.offers as Record<string, { enabled: boolean }>)[r.offer];
    if (!offer?.enabled) continue;
    const out: Route = { offer: r.offer as OfferId, rule: r.id };
    if (r.variant) out.variant = r.variant;
    if (r.alt) out.alt = r.alt as OfferId;
    if (r.prefer_email) out.prefer_email = true;
    const b = bumpFor(ctx.pillar);
    if (out.offer === "front_end" && b) out.bump = b;
    return out;
  }
  return { offer: "front_end", rule: "fallback" };
}

export function thankYouOffer(cell: string, pillar: string | null | undefined): string {
  const all = data.thank_you as unknown as Record<string, Record<string, string>>;
  const t: Record<string, string> = all[cell] ?? all.e12!;
  return t[pillar ?? ""] ?? t.default!;
}

export function winbackTier(lapseDays: number): { max_days: number; offer: string; code?: string } {
  return data.winback.tiers.find((t) => lapseDays <= t.max_days) ?? data.winback.tiers[data.winback.tiers.length - 1]!;
}

/** The win-back code for the cohort state: founding codes while the founding cohort is open, the "S" codes after. */
export function winbackCode(offer: OfferId, cohortOpen: boolean): string | null {
  const base = (data.offers as Record<string, { code?: string }>)[offer]?.code;
  return base ? (cohortOpen ? base : `${base}S`) : null;
}

/** Where /b sends a routed offer: a /b product family (the cell decides the price) or one of our own paths. */
export type BTargetOut = { kind: "family"; target: "front_end" | "founding" | "gift" | "essentials"; code: string | null } | { kind: "path"; path: string };

export function bDestination(r: Route, cohortOpen: boolean): BTargetOut {
  const o = (data.offers as Record<string, { target: string; path: string | null }>)[r.offer]!;
  if (o.target === "front_end" || o.target === "founding" || o.target === "gift" || o.target === "essentials") {
    return { kind: "family", target: o.target, code: winbackCode(r.offer, cohortOpen) };
  }
  if (o.target === "none") return { kind: "path", path: "/app" };
  return { kind: "path", path: o.path ?? "/" };
}

/** Allow-listed qualify answers from a query string (g, a); anything else is dropped. */
export function qualifyFromQuery(g: string | undefined, a: string | undefined): Pick<RouteContext, "goal" | "audience"> {
  const goal = g && g in data.qualify.goal ? g : null;
  const audience = a && a in data.qualify.audience ? (a as RouteContext["audience"]) : null;
  return { goal, audience };
}
