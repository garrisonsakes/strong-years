import { describe, expect, it } from "vitest";
import { RECIPES, SESSIONS, entitledDownloads, groceryList, kitchenPlan, sessionFor, sessionView } from "@/lib/products";
import type { Membership, Order } from "@/lib/db/types";

describe("Daily Practice sessions 1–14 (products/sessions.json)", () => {
  it("loads 14 sessions in the weekly rotation, two weeks", () => {
    expect(SESSIONS.sessions).toHaveLength(14);
    expect(SESSIONS.sessions.map((s) => s.id)).toEqual(Array.from({ length: 14 }, (_, i) => `DP${String(i + 1).padStart(2, "0")}`));
    expect(SESSIONS.rotation[0]).toBe("Mon strength");
  });

  it("every exercise segment has all four track variants", () => {
    for (const s of SESSIONS.sessions) {
      for (const seg of s.segments.filter((x) => x.tracks)) {
        for (const t of ["rebuild", "steady", "strong", "iron"] as const) {
          expect(seg.tracks![t].name, `${seg.id} ${t}`).toBeTruthy();
          expect(seg.tracks![t].dose).toBeTruthy();
        }
      }
    }
  });

  it("picks today's session by weekday and a two-week cycle from the join week", () => {
    const joined = new Date(2026, 8, 28, 9); // Monday Sep 28 2026
    expect(sessionFor(new Date(2026, 8, 28, 10), joined).id).toBe("DP01");
    expect(sessionFor(new Date(2026, 8, 30, 10), joined).id).toBe("DP03"); // Wednesday balance
    expect(sessionFor(new Date(2026, 9, 4, 10), joined).id).toBe("DP07"); // Sunday
    expect(sessionFor(new Date(2026, 9, 5, 10), joined).id).toBe("DP08"); // week 2 Monday
    expect(sessionFor(new Date(2026, 9, 12, 10), joined).id).toBe("DP01"); // cycles
  });

  it("renders the member's track and the gentle-day swap", () => {
    const s = SESSIONS.sessions[0]!;
    const rebuild = sessionView(s, "rebuild", null);
    const iron = sessionView(s, "iron", "knee");
    const stand = (v: typeof rebuild) => v.steps.find((x) => x.variant.exercise === "sit_to_stand")!.variant;
    expect(stand(rebuild).dose).not.toBe(stand(iron).dose);
    expect(stand(iron).advanced).toBe(true);
    expect(iron.swapNote).toMatch(/higher seat/);
    expect(rebuild.swapNote).toBeNull();
    expect(rebuild.safety.stop_rule).toMatch(/chest pain/);
  });
});

describe("Sun Yoon's Kitchen (products/kitchen_recipes.json)", () => {
  it("loads 24 recipes with USDA grams per ingredient and per-serving nutrition", () => {
    expect(RECIPES).toHaveLength(24);
    for (const r of RECIPES) {
      expect(r.per_serving.protein_g).toBeGreaterThan(0);
      expect(r.ingredients.length).toBeGreaterThan(0);
    }
  });
  it("each week: a breakfast, a main and a soup, plus a merged grocery list without water", () => {
    const p = kitchenPlan(new Date(2026, 9, 1));
    expect(p.recipes.map((r) => r.id[0])).toEqual(["B", expect.stringMatching(/[LD]/), "S"]);
    expect(p.groceries.some((g) => /^water$/i.test(g.item))).toBe(false);
    const g = groceryList([RECIPES[0]!, RECIPES[0]!]);
    expect(g.every((x) => x.amounts.length === 2)).toBe(true);
  });
});

describe("download entitlements", () => {
  const m = (o: Partial<Membership>) => ({ arm: "B" as const, price_cents: 3000, founding: true, status: "active" as const, plan: "monthly" as const, ...o });
  const paid = (offer_code: string): Pick<Order, "offer_code" | "kind" | "status"> => ({ offer_code, kind: "bump", status: "paid" });

  it("members get the sessions PDF and the welcome kit that states their exact price", () => {
    const files = entitledDownloads({ id: "x" }, m({}), []).map((d) => d.file);
    expect(files).toEqual(["daily_practice_sessions_1-14.pdf", "welcome_kit_founding_3000.pdf"]);
    expect(entitledDownloads({ id: "x" }, m({ price_cents: 2500 }), []).map((d) => d.file)).toContain("welcome_kit_founding_2500.pdf");
    expect(entitledDownloads({ id: "x" }, m({ founding: false, price_cents: 3500 }), []).map((d) => d.file)).toContain("welcome_kit_standard_3500.pdf");
  });
  it("paid add-ons only go to buyers; refunded members lose membership files", () => {
    const files = entitledDownloads({ id: "x" }, m({ price_cents: 2500 }), [paid("reset"), paid("wallplan")]).map((d) => d.file);
    expect(files).toContain("strength_reset_2500.pdf");
    expect(files).toContain("twelve_week_printable.pdf");
    expect(files).not.toContain("strong_kitchen.pdf");
    expect(entitledDownloads({ id: "x" }, m({ status: "refunded" }), []).length).toBe(0);
  });
});
