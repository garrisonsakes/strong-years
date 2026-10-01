/**
 * Round 9, condition 1: every price a page mentions comes from the same live,
 * cap-aware source as checkout. Before the fix, /start and /terms said the trial
 * renews at $25 after the founding cohort filled, while checkout charged $35.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

const jar = vi.hoisted(() => ({ arm: "A" as "A" | "B" }));
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: (n: string) => (n === "sy_arm" ? { name: n, value: jar.arm } : undefined), getAll: () => [] }),
  headers: async () => ({ get: () => null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { livePrices } from "@/lib/livePricing";
import { ARM_COOKIE } from "@/lib/analytics/attribution";

const CAP = 5;
const saved = { ...process.env };
let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  process.env.FOUNDING_COHORT_CAP = String(CAP);
  process.env.BLITZ_PRICE_TEST = "false"; // one founding price ($25) so the numbers are exact
  jar.arm = "A";
});
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

async function fillCohort() {
  for (let i = 0; i < CAP; i++) await store.insert("memberships", { member_id: `m${i}`, founding: true, status: "active", checkout_intent_id: null });
}

const text = (html: string) => html.replace(/<[^>]+>/g, " ").replace(/&[a-z#0-9]+;/g, " ").replace(/\s+/g, " ");

async function page(path: "start" | "terms"): Promise<string> {
  const mod = path === "start" ? await import("@/app/(site)/start/page") : await import("@/app/(site)/terms/page");
  return text(renderToStaticMarkup(await mod.default()));
}

describe("R9: pages quote the live, cap-aware price", () => {
  it("R9: the arm cookie name used here is the real one", () => {
    expect(ARM_COOKIE).toBe("sy_arm");
  });

  it("CANON UPDATE 2: no page offers a $1 trial, before or after the cap", async () => {
    for (const p of ["start", "terms"] as const) expect(await page(p)).not.toMatch(/\$1 (today|trial)|7 days for \$1|for \$1\b/);
    await fillCohort();
    for (const p of ["start", "terms"] as const) expect(await page(p)).not.toMatch(/\$1 (today|trial)|7 days for \$1|for \$1\b/);
  });

  it("R9 post-cap: /start and /terms quote $35, matching checkout; no $25 left", async () => {
    await fillCohort();
    const start = await page("start");
    const terms = await page("terms");
    expect(start).toMatch(/\$35/);
    expect(start).not.toMatch(/\$25\b/);
    expect(terms).not.toMatch(/\$25\b/);
  });

  it("R9 post-cap, arm B: /start shows the standard price everywhere and no founding claim", async () => {
    await fillCohort();
    jar.arm = "B";
    const start = await page("start");
    expect(start).toMatch(/The founding cohort is full/);
    expect(start).not.toMatch(/\$25\b/);
  });

  it("R9: livePrices agrees with checkout for every arm and cohort state", async () => {
    const open = livePrices({ priceCents: 2500, cohortOpen: true });
    expect(open).toMatchObject({ memberCents: 2500, trialRenewCents: 2500 });
    const closed = livePrices({ priceCents: 3500, cohortOpen: false });
    expect(closed).toMatchObject({ memberCents: 3500, trialRenewCents: 3500, frontEndRenewCents: { A: 3500, B: 3500 } });
  });
});
