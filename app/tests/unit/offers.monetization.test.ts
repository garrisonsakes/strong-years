/**
 * Monetization engine (MONETIZATION_ENGINE.md): the routing table is the same data the DM bot reads and gives the same
 * answers on the shared vectors; sticky arms match the worker; exposures dedupe; one price per person; never raise a
 * shown price; the arm readout computes RPV; member context (prior / lapse); the human-handled ask paths.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { bDestination, route, type RouteContext } from "@/lib/offers/route";
import { armFor, assignArm, lockedPrice, logConversion, logExposure, readout, violatesRaise } from "@/lib/offers/experiments";
import { memberContext } from "@/lib/offers/context";
import { submitAsk } from "@/lib/offers/ask";
import { computeMonetization } from "@/lib/offers/metrics";
import { candidates } from "@/lib/lifecycle/engine";
import type { Membership, Order } from "@/lib/db/types";

const root = path.join(process.cwd(), "..");
const vectors = JSON.parse(readFileSync(path.join(root, "workers", "tests", "fixtures", "offer_routing_vectors.json"), "utf8")) as {
  routes: { ctx: RouteContext; offer: string; rule: string; variant?: string; bump_frame?: string }[];
  assign: { exp: string; subject: string; arm: string }[];
};
const V1 = "3f1c2a9e-0d5b-4b7a-9c11-2e8f0a6b7c3d";
const V2 = "aaaaaaaa-0d5b-4b7a-9c11-2e8f0a6b7c3d";

let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});
afterEach(() => vi.unstubAllEnvs());

describe("routing table", () => {
  it("is byte-identical to the worker's copy and gives the same answers on the shared vectors", () => {
    expect(readFileSync(path.join(process.cwd(), "src/lib/offers/routing.json"))).toEqual(readFileSync(path.join(root, "workers/dm/offer_routing.json")));
    for (const v of vectors.routes) {
      const r = route(v.ctx);
      expect([r.offer, r.rule, r.variant, r.bump?.frame], JSON.stringify(v.ctx)).toEqual([v.offer, v.rule, v.variant, v.bump_frame]);
    }
    for (const a of vectors.assign) expect(assignArm(a.exp, a.subject)).toBe(a.arm);
  });

  it("maps offers to /b families (the cell still decides the price) or our own free paths; win-back codes follow the cohort", () => {
    expect(bDestination(route({ mode: "launch", keyword: "BOOK" }), true)).toEqual({ kind: "family", target: "front_end", code: null });
    expect(bDestination(route({ mode: "launch", audience: "group" }), true)).toEqual({ kind: "path", path: "/ask/group" });
    expect(bDestination(route({ mode: "launch", lapse_days: 60 }), true)).toEqual({ kind: "family", target: "founding", code: "WINBACK12" });
    expect(bDestination(route({ mode: "launch", lapse_days: 60 }), false)).toEqual({ kind: "family", target: "founding", code: "WINBACK12S" });
  });
});

describe("experiments + guardrails", () => {
  it("logs one exposure per subject/surface/offer/day and locks a price arm to the first arm shown", async () => {
    const s = { visitorId: V1, memberId: null };
    await logExposure(store, { subject: s, surface: "b", offer: "front_end", experiment: "fe_cell", arm: "e12", shownPriceCents: 1200 });
    await logExposure(store, { subject: s, surface: "b", offer: "front_end", experiment: "fe_cell", arm: "e12", shownPriceCents: 1200 });
    expect(await store.count("offer_events", { kind: "exposure" })).toBe(1);
    // Whatever the hash says today, this person keeps the arm (and price) they were first shown.
    expect(await armFor(store, "fe_cell", s)).toBe("e12");
    expect(await lockedPrice(store, "front_end", s)).toBe(1200);
    expect(violatesRaise(1200, 1500)).toBe(true);
    expect(violatesRaise(1200, 1200)).toBe(false);
    expect(violatesRaise(null, 1500)).toBe(false);
  });

  it("reads out revenue per visitor by arm, counting only revenue after the first exposure", async () => {
    const now = new Date();
    await logExposure(store, { subject: { visitorId: V1, memberId: null }, surface: "dm", offer: "front_end", experiment: "dm_qualify", arm: "qualify2" }, now);
    await logExposure(store, { subject: { visitorId: V2, memberId: null }, surface: "dm", offer: "front_end", experiment: "dm_qualify", arm: "qualify2" }, now);
    await new Promise((r) => setTimeout(r, 5));
    await logConversion(store, { visitorId: V1, memberId: null, offer: "bundle_m12", revenueCents: 1200, ref: "shopify:1", channel: "dm" });
    await logConversion(store, { visitorId: V1, memberId: null, offer: "bundle_m12", revenueCents: 1200, ref: "shopify:1", channel: "dm" }); // replay
    const r = await readout(store);
    expect(r).toEqual([{ experiment: "dm_qualify", arm: "qualify2", visitors: 2, buyers: 1, revenue_cents: 1200, rpv_cents: 600, conversion: 0.5 }]);
    vi.stubEnv("DM_WORKER_URL", "http://workers.test");
    vi.stubEnv("WORKER_TOKEN", "t");
    const m = await computeMonetization(store, new Date(), 7, async () => new Response(JSON.stringify({ conversations: 4, qualified: 2, routed: {} })));
    expect(m.dm.rpc_cents).toBe(300);
  });
});

describe("member context", () => {
  const ms = (x: Partial<Membership>) => ({ plan: "monthly", status: "active", current_period_end: null, ...x }) as Membership;
  const od = (x: Partial<Order>) => ({ status: "paid", kind: "membership_charge", offer_code: "founding_monthly", ...x }) as Order;
  it("reads what a person owns, months paid, and days since a lapse", () => {
    const now = new Date("2026-12-01T00:00:00Z");
    expect(memberContext([ms({})], [od({}), od({}), od({ kind: "front_end", offer_code: "ebook_e12" })], now)).toEqual({ prior: ["books", "member"], member_months: 1 });
    expect(memberContext([ms({ status: "canceled", current_period_end: "2026-10-02T00:00:00Z" })], [od({})], now)).toEqual({ prior: [], lapse_days: 60 });
  });
});

describe("ask paths (human-handled)", () => {
  it("files a ticket + an exception without the email in the queue item, and enforces 5+ seats for groups", async () => {
    expect(await submitAsk(store, { kind: "group", firstName: "Ann", email: "ann@example.com", message: "Our center", seats: 3, visitorId: null })).toEqual({ ok: false, error: "seats" });
    expect(await submitAsk(store, { kind: "price", firstName: "Ann", email: "ann@example.com", message: "fixed income", visitorId: null })).toEqual({ ok: true });
    const ex = await store.find("exceptions", { type: "price_help" });
    expect(ex).toHaveLength(1);
    expect(JSON.stringify(ex[0])).not.toContain("ann@example.com");
    expect((await store.find("support_tickets", { reason: "price_help" }))[0]?.email).toBe("ann@example.com");
  });
});

describe("second purchase within 7 days", () => {
  it("offers the intent-matched bump to cell B buyers and stops at the first second purchase", async () => {
    const m = await store.insert("members", { email: "sue@example.com", first_name: "Sue", is_demo: false, attribution: { keyword: "SOUP" } } as never);
    await store.insert("sy_orders", { member_id: m.id, email: m.email, offer_code: "bundle_m12", kind: "membership_charge", amount_cents: 1200, status: "paid", is_demo: false } as never);
    const sp = (await candidates(store)).find((c) => c.sequence === "second_purchase");
    expect(sp?.vars.bump_subject).toContain("grocery");
    await store.insert("sy_orders", { member_id: m.id, email: m.email, offer_code: "wallplan", kind: "bump", amount_cents: 900, status: "paid", is_demo: false } as never);
    expect((await candidates(store)).some((c) => c.sequence === "second_purchase")).toBe(false);
  });
});
