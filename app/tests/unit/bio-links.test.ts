/**
 * ORGANIC_ENGINE.md §3: the /b redirect (keyword → the right Shopify product for the
 * visitor's sticky cell, attribution carried) and the /go bio-link hub (runway mode
 * shows the free waitlist first; launch mode the starter books first).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const jar = vi.hoisted(() => ({ cookies: new Map<string, string>(), headers: new Map<string, string>() }));
vi.mock("next/headers", () => ({
  cookies: async () => ({
    get: (n: string) => (jar.cookies.has(n) ? { name: n, value: jar.cookies.get(n)! } : undefined),
    getAll: () => [...jar.cookies].map(([name, value]) => ({ name, value })),
    set: () => undefined,
    delete: () => undefined,
  }),
  headers: async () => ({ get: (n: string) => jar.headers.get(n.toLowerCase()) ?? null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { env } from "@/lib/config";
import { assignFrontEndCell, seedShopifyCatalog } from "@/lib/billing/shopify";
import { openCheckoutNow } from "@/lib/launch";
import { signVid } from "@/lib/vid";
import { cleanKeywordParam, cleanPageParam, goTiles, keywordTarget } from "@/lib/bioLinks";
import { GET as bRoute } from "@/app/b/route";

let store: MemoryStore;
beforeEach(async () => {
  vi.stubEnv("BILLING_PROVIDER", "shopify");
  vi.stubEnv("LAUNCH_MODE", "prelaunch");
  vi.stubEnv("SHOPIFY_STORE_DOMAIN", "strongyears-test.myshopify.com");
  // These suites exercise the canon-3 cell B / cell A split mechanics explicitly. Canon 6 (the 7-day trial, t12)
  // is the default and is covered by R12.canon6-seven-day-trial.test.ts.
  vi.stubEnv("FRONT_END_CELLS", "m12,e12");
  vi.stubEnv("FRONT_END_DEFAULT_CELL", "m12");
  vi.stubEnv("FRONT_END_CELL_TEST", "true");
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
  jar.cookies.clear();
  jar.headers.clear();
});
afterEach(() => vi.unstubAllEnvs());

const VID = "11111111-2222-4333-8444-555555555555";
async function visitor(vid = VID) {
  jar.cookies.set("sy_vid", await signVid(vid, env.sessionSecret));
}
async function b(query: string) {
  const res = await bRoute(new Request(`http://members.test/b?${query}`, { headers: { cookie: [...jar.cookies].map(([k, v]) => `${k}=${v}`).join("; ") } }));
  const loc = res.headers.get("location")!;
  const u = new URL(loc, "http://members.test");
  const landing = u.pathname.startsWith("/discount/") ? new URL(u.searchParams.get("redirect")!, u.origin) : u;
  return { res, u, landing };
}

describe("/b keyword and page parsing (pure)", () => {
  it("keywords name a product family, never a price: BOOK/STRONG/SOUP → front end, JOIN → membership, FAMILY → gift", () => {
    for (const k of ["BOOK", "book", "books", "STRONG", "SOUP", "KNEES", "", "12", "$1"]) expect(keywordTarget(k)).toBe("front_end");
    expect(keywordTarget("JOIN")).toBe("founding");
    expect(keywordTarget("family")).toBe("gift");
    expect(keywordTarget("essentials")).toBe("essentials");
    expect(keywordTarget(null)).toBe("front_end");
  });
  it("cleans the keyword and page aliases; junk is dropped", () => {
    expect(cleanKeywordParam("book")).toBe("BOOK");
    expect(cleanKeywordParam("<script>")).toBeNull();
    expect(cleanKeywordParam("x".repeat(60))).toBeNull();
    expect(cleanPageParam("cy")).toBe("changyin");
    expect(cleanPageParam("yt-sk")).toBe("yt-sunyoon.kitchen");
    expect(cleanPageParam("sunyoon")).toBe("sunyoon");
    expect(cleanPageParam("../etc")).toBeNull();
  });
});

describe("/b redirect", () => {
  it("prelaunch: sends everyone to the waitlist with the post credited (keyword, page, mc_id kept)", async () => {
    const { res, u } = await b("t=book&p=cy&mc_id=12345&utm_source=ig&utm_medium=dm&pid=REEL_7");
    expect(res.status).toBe(302);
    expect(u.pathname).toBe("/waitlist");
    expect(u.searchParams.get("keyword")).toBe("BOOK");
    expect(u.searchParams.get("page")).toBe("changyin");
    expect(u.searchParams.get("post_id")).toBe("REEL_7");
    expect(u.searchParams.get("mc_id")).toBe("12345");
    expect(u.searchParams.get("from")).toBe("b");
    expect(res.headers.get("cache-control")).toContain("no-store");
    // the last touch cookie carries the keyword even though the middleware never saw "t"
    const setCookie = res.headers.get("set-cookie") ?? "";
    expect(setCookie).toContain("sy_lt=");
    expect(decodeURIComponent(decodeURIComponent(setCookie.split(";")[0]!.slice("sy_lt=".length)))).toContain('"keyword":"BOOK"');
  });

  it("live: BOOK lands on the Shopify product page for the visitor's sticky cell with attribution and the visitor id; the same visitor always gets the same page", async () => {
    await openCheckoutNow(store, "test");
    await visitor();
    const one = await b("t=BOOK&p=cy&pid=REEL_7&utm_source=ig");
    const two = await b("t=STRONG&p=cy&pid=REEL_8&utm_source=ig");
    expect(one.u.host).toBe("strongyears-test.myshopify.com");
    expect(one.landing.pathname).toBe(two.landing.pathname);
    const cell = assignFrontEndCell(VID, ["m12", "e12"]);
    expect(one.landing.searchParams.get("sku")).toBe(cell === "m12" ? "bundle_m12" : "ebook_e12");
    expect(one.landing.searchParams.get("vid")).toBe(VID);
    expect(one.landing.searchParams.get("post_id")).toBe("REEL_7");
    expect(one.landing.searchParams.get("keyword")).toBe("BOOK");
    expect(one.landing.searchParams.get("page")).toBe("changyin");
    if (cell === "m12") {
      expect(one.u.pathname).toBe("/discount/STARTER12");
      expect(one.landing.searchParams.get("view")).toBe("starter");
    } else {
      expect(one.landing.pathname).toBe("/products/strong-years-starter-books");
    }
    expect(one.landing.pathname).not.toMatch(/^\/cart\//);
  });

  it("live: JOIN goes to the plain founding membership page, FAMILY to the gift page; a keyword never changes the price", async () => {
    await openCheckoutNow(store, "test");
    await visitor();
    const join = await b("t=JOIN");
    expect(join.u.pathname).toBe("/products/founding-membership");
    expect(join.u.searchParams.get("sku")).toBe("founding_monthly");
    expect(join.u.searchParams.get("view")).toBeNull();
    const gift = await b("t=FAMILY&p=cs");
    expect(gift.u.pathname).toBe("/products/gift-strong-years");
    const tampered = await b("t=BOOK&price=1&sku=ebook_e7&cell=e7&variant=9000000007");
    expect(tampered.landing.searchParams.get("sku")).not.toBe("ebook_e7");
  });

  it("live: an affiliate ref becomes attribution (utm_source=affiliate, utm_campaign=<code>); junk refs are ignored", async () => {
    await openCheckoutNow(store, "test");
    await visitor();
    const r = await b("t=BOOK&ref=chang");
    expect(r.landing.searchParams.get("utm_source")).toBe("affiliate");
    expect(r.landing.searchParams.get("utm_campaign")).toBe("CHANG");
    const junk = await b("t=BOOK&ref=%3Cscript%3E");
    expect(junk.landing.searchParams.get("utm_campaign")).toBeNull();
  });

  it("live in Stripe mode: /b falls back to /join with the parameters", async () => {
    vi.stubEnv("BILLING_PROVIDER", "stripe");
    await openCheckoutNow(store, "test");
    const { u } = await b("t=BOOK&p=cy");
    expect(u.pathname).toBe("/join");
    expect(u.searchParams.get("keyword")).toBe("BOOK");
  });
});

describe("/go tiles", () => {
  const base = { frontEndToday: "$12", memberPrice: "$25", cohortOpen: true, page: "changyin" } as const;
  it("runway mode: the free waitlist tile first; launch mode: the starter books first through /b", () => {
    const runway = goTiles({ ...base, mode: "runway" }, "page=changyin");
    expect(runway[0]!.testId).toBe("go-waitlist");
    expect(runway[0]!.href).toBe("/waitlist?page=changyin");
    expect(runway[0]!.primary).toBe(true);
    const launch = goTiles({ ...base, mode: "launch" }, "page=changyin");
    expect(launch[0]!.testId).toBe("go-books");
    expect(launch[0]!.href).toBe("/b?t=BOOK&page=changyin");
    expect(launch[0]!.title).toContain("$12");
    expect(launch.some((t) => t.testId === "go-gift")).toBe(true);
    expect(launch.some((t) => t.testId === "go-waitlist")).toBe(false);
  });
  it("Sun Yoon's page orders the kitchen tile first after the primary; every href is a page we have", () => {
    const sun = goTiles({ ...base, mode: "runway", page: "sunyoon.kitchen" }, "");
    expect(sun[1]!.testId).toBe("go-soups");
    for (const t of goTiles({ ...base, mode: "launch" }, "")) expect(t.href).toMatch(/^\/(b|waitlist|start|quiz\/strength-age|quiz\/gut-energy)(\?|$)/);
  });
  it("never a price in a tile when the catalog can't say what today costs", () => {
    const t = goTiles({ ...base, mode: "launch", frontEndToday: null }, "");
    expect(t[0]!.title).toBe("Starter books");
    expect(t[0]!.note).not.toMatch(/\$/);
  });
});

describe("/go page", () => {
  it("renders runway mode before launch and launch mode after, with the page carried into every link", async () => {
    const { default: Go } = await import("@/app/(site)/go/page");
    const { renderToStaticMarkup } = await import("react-dom/server");
    const before = renderToStaticMarkup(await Go({ searchParams: Promise.resolve({ p: "sk" }) }));
    expect(before).toContain('data-mode="runway"');
    expect(before).toContain("/waitlist?page=sunyoon.kitchen");
    expect(before).toContain("AI characters");
    expect(before).not.toMatch(/\$1\b/);
    await openCheckoutNow(store, "test");
    const after = renderToStaticMarkup(await Go({ searchParams: Promise.resolve({ p: "yt-cy" }) }));
    expect(after).toContain('data-mode="launch"');
    expect(after).toContain("/b?t=BOOK&amp;page=yt-changyin");
    expect(after).toContain("platform=yt");
  });
});
