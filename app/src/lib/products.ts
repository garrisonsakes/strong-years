/**
 * Real product content (../products): Daily Practice sessions 1–14 with 4-track variants,
 * Sun Yoon's Kitchen recipes (USDA-derived grams), and the downloadable PDFs.
 * Server-only data; pure selectors so they can be unit tested.
 */
import { bonusUnlockAt } from "./entitlement";
import sessionsData from "@/content/sessions.json";
import recipesData from "@/content/kitchen_recipes.json";
import type { Member, Membership, Order, Track } from "./db/types";

export interface TrackVariant {
  exercise: string;
  name: string;
  version: string;
  dose: string;
  advanced: boolean;
  how: string;
  cues: string[];
  breathe: string;
  safety: string[];
  equipment: string;
}

export interface Segment {
  n: number;
  id: string;
  name: string;
  kind: "intro" | "warmup" | "block" | "checkin" | "cooldown" | "close";
  start: string;
  end: string;
  duration_s: number;
  tracks: Record<Track, TrackVariant> | null;
  beats?: { t: string; speaker: string; vo: string; ost: string }[];
  on_screen?: string[];
  safety_callouts?: string[];
}

export interface ProductSession {
  id: string;
  day_number: number;
  week: number;
  weekday: string;
  type: string;
  title: string;
  duration_s: number;
  duration: string;
  track_descriptions: Record<Track, string>;
  gentle_day_swaps: { sore_knee: string; sore_back: string; low_energy: string };
  safety_global: { stop_rule: string; emergency: string; pain_rule: string; stand_slowly: string };
  caption_movement_addon: string;
  segments: Segment[];
}

interface SessionsFile {
  product: string;
  version: string;
  rotation: string[];
  tracks: Record<Track, string>;
  disclosure: string;
  sessions: ProductSession[];
}

export const SESSIONS = sessionsData as unknown as SessionsFile;

const WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

/** Monday of the week containing d (local date), at noon, to avoid DST edges. */
function mondayOf(d: Date): Date {
  const x = new Date(d.getFullYear(), d.getMonth(), d.getDate(), 12);
  x.setDate(x.getDate() - ((x.getDay() + 6) % 7));
  return x;
}

/**
 * Today's session: the weekday rhythm (Mon strength … Sun rest) and a two-week cycle
 * (DP01–DP07, then DP08–DP14) counted from the member's first week.
 */
export function sessionFor(date: Date, joinedAt: Date | string): ProductSession {
  const weeks = Math.max(0, Math.round((mondayOf(date).getTime() - mondayOf(new Date(joinedAt)).getTime()) / (7 * 86_400_000)));
  const week = (weeks % 2) + 1;
  const weekday = WEEKDAYS[date.getDay()]!;
  return SESSIONS.sessions.find((s) => s.week === week && s.weekday === weekday) ?? SESSIONS.sessions[0]!;
}

export type SwapKey = "knee" | "back" | "energy";
const SWAP_FIELD: Record<SwapKey, keyof ProductSession["gentle_day_swaps"]> = { knee: "sore_knee", back: "sore_back", energy: "low_energy" };

export interface SessionView {
  id: string;
  dayNumber: number;
  title: string;
  type: string;
  duration: string;
  minutes: number;
  track: Track;
  trackDescription: string;
  swapNote: string | null;
  opener: string | null;
  closer: string | null;
  steps: { name: string; kind: Segment["kind"]; time: string; variant: TrackVariant }[];
  safety: ProductSession["safety_global"];
}

export function sessionView(s: ProductSession, track: Track, swap: SwapKey | null): SessionView {
  const intro = s.segments.find((x) => x.kind === "intro");
  const close = s.segments.find((x) => x.kind === "close");
  return {
    id: s.id,
    dayNumber: s.day_number,
    title: s.title,
    type: s.type,
    duration: s.duration,
    minutes: Math.round(s.duration_s / 60),
    track,
    trackDescription: s.track_descriptions[track],
    swapNote: swap ? s.gentle_day_swaps[SWAP_FIELD[swap]] : null,
    opener: intro?.beats?.[1]?.vo ?? intro?.beats?.[0]?.vo ?? null,
    closer: close?.beats?.[close.beats.length - 1]?.vo ?? null,
    steps: s.segments
      .filter((x) => x.tracks && x.tracks[track])
      .map((x) => ({ name: x.name, kind: x.kind, time: `${x.start}–${x.end}`, variant: x.tracks![track] })),
    safety: s.safety_global,
  };
}

/* ---------------- Sun Yoon's Kitchen ---------------- */

export interface ProductRecipe {
  id: string;
  name: string;
  native: string | null;
  category: string;
  serves: number;
  minutes_active: number;
  minutes_total: number;
  per_serving: { kcal: number; protein_g: number; fiber_g: number; sodium_mg: number };
  ingredients: { amount: string; item: string; grams: number; source: string | null }[];
  steps: string[];
  soft_food: string | null;
  storage: string | null;
  cautions: string[];
}

export const RECIPES = recipesData as unknown as ProductRecipe[];

const byPrefix = (p: string) => RECIPES.filter((r) => r.id.startsWith(p));

export interface KitchenPlan {
  weekIndex: number;
  recipes: ProductRecipe[];
  groceries: { item: string; amounts: string[]; grams: number }[];
}

/** Every Sunday: 3 recipes (a breakfast, a lunch or dinner, a soup), rotating through all 24. */
export function kitchenPlan(date: Date): KitchenPlan {
  const weekIndex = Math.floor(mondayOf(date).getTime() / (7 * 86_400_000));
  const breakfasts = byPrefix("B");
  const mains = [...byPrefix("L"), ...byPrefix("D")];
  const soups = byPrefix("S");
  const recipes = [breakfasts[weekIndex % breakfasts.length]!, mains[weekIndex % mains.length]!, soups[weekIndex % soups.length]!];
  return { weekIndex, recipes, groceries: groceryList(recipes) };
}

export function groceryList(recipes: ProductRecipe[]) {
  const map = new Map<string, { item: string; amounts: string[]; grams: number }>();
  for (const r of recipes) {
    for (const ing of r.ingredients) {
      if (/^water\b/i.test(ing.item)) continue;
      const key = ing.item.split(",")[0]!.trim().toLowerCase();
      const cur = map.get(key) ?? { item: ing.item.split(",")[0]!.trim(), amounts: [], grams: 0 };
      cur.amounts.push(ing.amount);
      cur.grams += ing.grams;
      map.set(key, cur);
    }
  }
  return [...map.values()].sort((a, b) => a.item.localeCompare(b.item));
}

/* ---------------- Downloads (PDFs) ---------------- */

export interface Download {
  file: string;
  title: string;
  blurb: string;
  /** AUDIT_BUSINESS F08: bonus material vests on day 15 (after the money-back window). */
  lockedUntil?: string;
}

/**
 * What a member may download. Membership content goes to anyone with access; paid add-ons
 * go to their buyers. Price-bearing PDFs are rendered once per price so the billing text
 * always matches what this member actually pays.
 */
export function entitledDownloads(
  member: Pick<Member, "id">,
  m: (Pick<Membership, "arm" | "price_cents" | "founding" | "status" | "plan"> & Partial<Pick<Membership, "guarantee_until" | "current_period_end" | "offer_code">>) | null,
  orders: Pick<Order, "offer_code" | "kind" | "status">[],
  now = Date.now(),
): Download[] {
  const out: Download[] = [];
  const paid = orders.filter((o) => o.status === "paid");
  const bought = (sku: string) => paid.some((o) => o.offer_code === sku);
  // Shopify launch path: the Starter Books (both books, keep forever) come with every ebook_* order and with the
  // cell-B "$12 = books + first month" membership orders (bundle_m12*). Served here, watermarked; never via Digital Downloads.
  const starterBooks = paid.some((o) => /^(ebook_|bundle_m12)/.test(o.offer_code));
  const active = m && !["refunded", "expired", "incomplete", "paused"].includes(m.status);
  const unlockAt = m ? bonusUnlockAt({ plan: m.plan, guarantee_until: m.guarantee_until ?? null }) : null;
  const locked = unlockAt && unlockAt.getTime() > now ? unlockAt.toISOString() : undefined;
  const price = m?.price_cents && [2000, 2500, 3000, 3500].includes(m.price_cents) ? m.price_cents : 2000;
  if (active) {
    // The sessions themselves are in the app from day 1; the printable program book vests on day 15.
    out.push({ file: "daily_practice_sessions_1-14.pdf", title: "Daily Practice, sessions 1–14 (printable book)", blurb: "Every session's moves, all four levels, with the safety cues.", ...(locked ? { lockedUntil: locked } : {}) });
    if (m.plan !== "gift") {
      // No $1 trial exists (CANON UPDATE 2); a legacy arm-A row gets the founding kit for its price. CANON UPDATE 6: the
      // 7-day-trial founding row ($12 books today, first $25 on day 7) gets the kit whose billing text says exactly that.
      const starter = (m.offer_code ?? "").startsWith("bundle_m12") && m.founding;
      const trial = (m.offer_code ?? "").startsWith("bundle_t12") && m.founding;
      const kit = trial ? "welcome_kit_trial_2500.pdf" : starter ? "welcome_kit_starter_2500.pdf" : m.founding ? `welcome_kit_founding_${m.price_cents === 3000 ? 3000 : 2500}.pdf` : "welcome_kit_standard_3500.pdf";
      out.push({ file: kit, title: "Your Welcome Kit", blurb: "How it works, staying safe, reaching a human, and how to cancel." });
    }
  }
  if (bought("reset") || starterBooks) out.push({ file: `strength_reset_${price}.pdf`, title: "7-Day Strength Reset", blurb: "Seven sessions, six tests and a 7-day tracker. Yours to keep." });
  if (bought("kitchen") || starterBooks) out.push({ file: "strong_kitchen.pdf", title: "Sun Yoon's Strong Kitchen", blurb: "24 recipes with grams, soft-food versions and honest remedy grades." });
  if (bought("kitchen") || bought("wallplan")) out.push({ file: "twelve_week_printable.pdf", title: "12-Week Printable (The Wall Plan)", blurb: "The fridge calendar. Tick it every day." });
  return out;
}

export const ALL_DOWNLOAD_FILES = [
  "daily_practice_sessions_1-14.pdf",
  "welcome_kit_trial_2500.pdf",
  "welcome_kit_starter_2500.pdf",
  "welcome_kit_founding_2500.pdf",
  "welcome_kit_founding_3000.pdf",
  "welcome_kit_standard_3500.pdf",
  "strength_reset_2000.pdf",
  "strength_reset_2500.pdf",
  "strength_reset_3000.pdf",
  "strength_reset_3500.pdf",
  "strong_kitchen.pdf",
  "twelve_week_printable.pdf",
];
