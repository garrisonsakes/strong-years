/**
 * The two public link surfaces ORGANIC_ENGINE.md §3 calls for (pure parts; the
 * route and page import these):
 *
 *  /b   the DM / Story / bio redirect. "t" is the keyword the person commented
 *       (BOOK, STRONG, SOUP, FAMILY, JOIN…); it picks WHICH product family the
 *       redirect lands on (never a price or a cell) and is stored as the last-touch
 *       keyword. Prelaunch → /waitlist. Live → the visitor's sticky cell on the
 *       Shopify store (shopCheckout.ts), or /join in Stripe mode.
 *  /go  the bio link hub (one page, two modes). RUNWAY (prelaunch): the free
 *       waitlist tile first. LAUNCH: the starter books tile first. "p" names the
 *       page the person came from (cy, sk, cs, yt-cy…) and becomes attribution.
 */

export type BTarget = "front_end" | "founding" | "gift" | "essentials";

/** keyword (any case, any of the documented variants) → what /b sells. Unknown keywords sell the front end. */
export function keywordTarget(t: string | null | undefined): BTarget {
  const k = (t ?? "").trim().toLowerCase();
  if (!k) return "front_end";
  if (/^(join|member|membership|founding)$/.test(k)) return "founding";
  if (/^(family|gift|mom|dad|parent)$/.test(k)) return "gift";
  if (/^(essentials|basic)$/.test(k)) return "essentials";
  return "front_end";
}

/** The attribution keyword we keep: letters, digits, dash/underscore, upper-cased, at most 40 characters. */
export function cleanKeywordParam(t: string | null | undefined): string | null {
  if (!t) return null;
  const v = t.trim();
  return /^[A-Za-z0-9_-]{1,40}$/.test(v) ? v.toUpperCase() : null;
}

/** Page shorthand from bio links (p=cy, sk, cs, yt-cy, tt-sk…) → the page handle used in attribution. */
const PAGE_ALIASES: Record<string, string> = {
  cy: "changyin",
  sk: "sunyoon.kitchen",
  sy: "sunyoon",
  st: "changyin.strength",
  cs: "sunyoon", // retired duo page alias: old links land on Sun's main page
};
export function cleanPageParam(p: string | null | undefined): string | null {
  if (!p) return null;
  const v = p.trim().toLowerCase().slice(0, 40);
  if (!/^[a-z0-9._-]{1,40}$/.test(v)) return null;
  const m = v.match(/^(?:(yt|tt|fb|ig|th)-)?(.+)$/);
  if (!m) return null;
  const base = PAGE_ALIASES[m[2]!] ?? m[2]!;
  return m[1] ? `${m[1]}-${base}` : base;
}

export type GoMode = "runway" | "launch";

export interface GoTile {
  /** Short, plain label on the tile. */
  title: string;
  /** One line under it. Honest: free is free, a price is the price. */
  note: string;
  href: string;
  /** The first tile is the primary (filled) button. */
  primary?: boolean;
  testId: string;
}

export interface GoFacts {
  mode: GoMode;
  /** "$12" style display of what the front end costs today (null when unknown). */
  frontEndToday: string | null;
  /** Membership renewal price display, e.g. "$25". */
  memberPrice: string;
  cohortOpen: boolean;
  /** Which character's page the visitor came from (orders the tiles). */
  page: string | null;
}

/**
 * The tiles for /go. Runway mode leads with the free waitlist (ORGANIC_ENGINE.md
 * §3.2), launch mode with the starter books; Sun Yoon's page puts the kitchen
 * tile before the Strength Age test. Every tile links to a page that exists.
 */
export function goTiles(f: GoFacts, q: string): GoTile[] {
  const qs = q ? `?${q}` : "";
  const amp = q ? `&${q}` : "";
  const sunFirst = (f.page ?? "").includes("sunyoon");
  const dayOne: GoTile = { title: "Day 1 free (8 minutes)", note: "The first session, no sign-up. A chair and a counter.", href: `/start${qs}`, testId: "go-day1" };
  const test: GoTile = { title: "Your Strength Age test", note: "Three tests at home, about four minutes. A number to beat.", href: `/quiz/strength-age${qs}`, testId: "go-test" };
  const soups: GoTile = { title: "Sun Yoon's soups and the gut check", note: "Free. The protein grams are written in.", href: `/quiz/gut-energy${qs}`, testId: "go-soups" };
  const middle = sunFirst ? [soups, dayOne, test] : [dayOne, test, soups];
  if (f.mode === "runway") {
    return [
      { title: "Get first access (free)", note: "One email when checkout opens, with first access at the founding price. Unsubscribe in one click.", href: `/waitlist${qs}`, primary: true, testId: "go-waitlist" },
      ...middle,
    ];
  }
  const books: GoTile = {
    title: f.frontEndToday ? `Starter books: ${f.frontEndToday} today` : "Starter books",
    note: f.frontEndToday
      ? `${f.frontEndToday} today for both books${f.cohortOpen ? " and, in the launch default, your first founding month" : ""}. Every price and renewal is on the next page before you pay.`
      : "Both books to keep. The price is on the next page before you pay.",
    href: `/b?t=BOOK${amp}`,
    primary: true,
    testId: "go-books",
  };
  const gift: GoTile = { title: "A gift for a parent", note: "Prepaid, 3 or 12 months. It never renews.", href: `/b?t=FAMILY${amp}`, testId: "go-gift" };
  return [books, ...middle.slice(0, 2), gift];
}
