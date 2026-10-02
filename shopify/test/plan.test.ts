import { describe, it, expect } from "vitest";
import { dryRunner, assertNotForbiddenShop } from "../src/client.ts";
import { runPlan, type Engine, type Phase } from "../src/plan.ts";
import { factsFromEnv } from "../src/provision.ts";
import { PRODUCTS, FOUNDING_CAP, FUNNEL_ARMS, SYSTEM_CODES } from "../config/catalog.ts";
import { readFileSync } from "node:fs";

const facts = factsFromEnv({ COMPANY_LEGAL_NAME: "Strong Years LLC", MAILING_ADDRESS: "1 Test St, Austin, TX 78701", SUPPORT_EMAIL: "help@strongyears.com", BILLING_PHONE: "(555) 010-0000", GOVERNING_STATE: "Texas", SY_DOMAIN: "strongyears.com", LEGAL_EFFECTIVE_DATE: "2026-10-01" } as any);

async function plan(engine: Engine, phase: Phase, simulateProvisioned = false, confirmCloseFounding = false, simulateTrialPlan = true) {
  const g = dryRunner(() => {}, { simulateProvisioned, engine, simulateTrialPlan });
  const report = await runPlan(g, { engine, phase, membersAppUrl: "https://members.strongyears.com", facts, foundingCloseDateIso: "2027-01-09", nowIso: "2026-10-01T00:00:00Z", confirmCloseFounding });
  return { ops: g.recorded, report };
}
const summary = (ops: any[]) => ops.map((o) => `${o.kind.padEnd(8)} ${o.op.padEnd(26)} ${o.step}`);

describe("provisioning plan (DRY_RUN snapshot)", () => {
  it("core phase, Shopify Subscriptions engine: full operation list", async () => {
    const { ops, report } = await plan("shopify_subscriptions", "core");
    expect(summary(ops)).toMatchSnapshot();
    expect(ops.map((o) => ({ op: o.op, variables: o.variables }))).toMatchSnapshot("variables");
    expect(report.manual.join("\n")).toMatch(/Shopify Subscriptions → Plans/);
  });

  it("core phase, app engine: creates app-owned selling plans with a fixed first-cycle price", async () => {
    const { ops } = await plan("app", "core");
    expect(summary(ops)).toMatchSnapshot();
    const spg = ops.filter((o) => o.op === "SellingPlanGroupCreate");
    expect(spg).toHaveLength(3);
    const founding = spg.find((o) => (o.variables as any).input.merchantCode === "sy-founding")!;
    const plansMade = (founding.variables as any).input.sellingPlansToCreate as any[];
    const starter = plansMade.find((p: any) => /first month/.test(p.name));
    // Canon 6 trial plan in the app engine: $0 first cycle, $25 after; the app sets nextBillingDate = checkout + 7 days.
    const trial = plansMade.find((p: any) => /7-day trial/.test(p.name));
    expect(trial.pricingPolicies).toEqual([
      { fixed: { adjustmentType: "PRICE", adjustmentValue: { fixedValue: "0.00" } } },
      { recurring: { afterCycle: 1, adjustmentType: "PRICE", adjustmentValue: { fixedValue: "25.00" } } },
    ]);
    expect(starter.pricingPolicies).toEqual([
      { fixed: { adjustmentType: "PRICE", adjustmentValue: { fixedValue: "12.00" } } },
      { recurring: { afterCycle: 1, adjustmentType: "PRICE", adjustmentValue: { fixedValue: "25.00" } } },
    ]);
    expect(ops.some((o) => o.op === "DiscountCodeCreate" && (o.variables as any).basicCodeDiscount.code === "STARTER12")).toBe(false);
    expect(ops.filter((o) => o.op === "WebhookCreate").map((o) => (o.variables as any).topic)).toContain("SUBSCRIPTION_CONTRACTS_CREATE");
  });

  it("verify phase snapshot (after the client created the plans)", async () => {
    const { ops, report } = await plan("shopify_subscriptions", "verify", true);
    expect(summary(ops)).toMatchSnapshot();
    expect(report.membersCatalog).toMatchSnapshot("members catalog");
  });

  it("verify phase, canon 6: the 7-day-trial plan yields t12 rows ($0 today, $25 recurring, trial_days 7); without it the catalog falls back to cell B and warns", async () => {
    const { report } = await plan("shopify_subscriptions", "verify", true);
    const cat = report.membersCatalog!;
    const t = cat.find((r) => r.sku === "bundle_t12")!;
    expect(t).toMatchObject({ entitlement: "founding", price_cents: 0, recurring_cents: 2500, interval: "month", cell: "t12", cohort: "founding", trial_days: 7, includes_ebook: false, discount_code: null, product_handle: "founding-membership" });
    expect(t.selling_plan_id).not.toBe(cat.find((r) => r.sku === "founding_monthly")!.selling_plan_id);
    const ts = cat.find((r) => r.sku === "bundle_t12_standard")!;
    expect(ts).toMatchObject({ entitlement: "standard", price_cents: 0, recurring_cents: 3500, cell: "t12", cohort: "standard", trial_days: 7 });
    expect(FUNNEL_ARMS.find((a) => a.default)!.id).toBe("T");
    const without = await plan("shopify_subscriptions", "verify", true, false, false);
    expect(without.report.membersCatalog!.some((r) => r.sku.startsWith("bundle_t12"))).toBe(false);
    expect(without.report.membersCatalog!.find((r) => r.sku === "bundle_m12")!.discount_code).toBe("STARTER12");
    expect(without.report.warnings.join("\n")).toMatch(/no "7-day trial" selling plan attached/);
  });

  it("close-founding is one-way and needs explicit confirmation", async () => {
    await expect(plan("shopify_subscriptions", "close-founding", true, false)).rejects.toThrow(/yes-close-founding/);
    const { ops } = await plan("shopify_subscriptions", "close-founding", true, true);
    expect(summary(ops)).toMatchSnapshot();
    const pol = ops.find((o) => o.op === "VariantInventoryPolicy")!;
    expect((pol.variables as any).variants[0].inventoryPolicy).toBe("CONTINUE");
  });
});

describe("plan invariants", () => {
  it("no founding seat cap: the founding variant is untracked and never sells out", async () => {
    expect(FOUNDING_CAP).toBeNull();
    const { ops } = await plan("shopify_subscriptions", "core");
    const f = ops.find((o) => o.op === "ProductUpsert" && (o.variables as any).input.handle === "founding-membership")!;
    const v = (f.variables as any).input.variants[0];
    expect(v.inventoryQuantities).toBeUndefined();
    expect(v.inventoryPolicy).toBe("CONTINUE");
    expect(v.inventoryItem.tracked).toBe(false);
  });

  it("STARTER12 discounts only the first subscription payment of the founding product", async () => {
    const { ops } = await plan("shopify_subscriptions", "core");
    const d = (ops.find((o) => o.op === "DiscountCodeCreate" && (o.variables as any).basicCodeDiscount.code === "STARTER12")!.variables as any).basicCodeDiscount;
    expect(d.recurringCycleLimit).toBe(1);
    expect(d.customerGets.appliesOnSubscription).toBe(true);
    expect(d.customerGets.appliesOnOneTimePurchase).toBe(false);
    expect(d.customerGets.value.discountAmount.amount).toBe("13.00"); // $25 - $13 = $12 today
    expect(d.customerGets.items.products.productsToAdd).toEqual(["gid://shopify/Product/DRYRUN-founding-membership"]);
  });

  it("page/affiliate codes never discount a membership (MRR is never discounted)", async () => {
    const { ops } = await plan("shopify_subscriptions", "core");
    for (const o of ops.filter((x) => x.op === "DiscountCodeCreate")) {
      const d = (o.variables as any).basicCodeDiscount;
      if ((SYSTEM_CODES as readonly string[]).includes(d.code)) {
        // System codes (MONETIZATION_ENGINE.md §3): a membership code discounts the FIRST payment only, once per
        // customer; the group code applies to gift seats (one-time) only.
        if (d.customerGets.appliesOnSubscription) expect([d.recurringCycleLimit, d.appliesOncePerCustomer]).toEqual([1, true]);
        else expect(d.customerGets.items.products.productsToAdd).toEqual(["gid://shopify/Product/DRYRUN-gift-strong-years"]);
        continue;
      }
      expect(d.customerGets.appliesOnSubscription).toBe(false);
      expect(d.customerGets.items.products.productsToAdd.every((id: string) => id.includes("starter-books"))).toBe(true);
    }
  });

  it("STARTER12S is the same first-payment-only offer on the standard membership after the founding close ($35 → $12)", async () => {
    const { ops } = await plan("shopify_subscriptions", "core");
    const d = (ops.find((o) => o.op === "DiscountCodeCreate" && (o.variables as any).basicCodeDiscount.code === "STARTER12S")!.variables as any).basicCodeDiscount;
    expect(d.recurringCycleLimit).toBe(1);
    expect(d.appliesOncePerCustomer).toBe(true);
    expect(d.customerGets.value.discountAmount.amount).toBe("23.00");
    expect(d.customerGets.items.products.productsToAdd).toEqual(["gid://shopify/Product/DRYRUN-strong-years-membership"]);
  });

  it("webhooks: exactly the fixture's core topics (config/webhook-topics.json), all pointing at the members app; enrichment topics only in the app engine", async () => {
    const fixture = JSON.parse(readFileSync(new URL("../config/webhook-topics.json", import.meta.url), "utf8")) as { core: string[]; enrichment: string[] };
    const toEnum = (t: string) => t.toUpperCase().replace("/", "_");
    const { ops } = await plan("shopify_subscriptions", "core");
    const hooks = ops.filter((o) => o.op === "WebhookCreate");
    expect(hooks.map((o) => (o.variables as any).topic)).toEqual(fixture.core.map(toEnum));
    expect(fixture.core).not.toContain("orders/refunded"); // not an Admin API topic; refunds/create is the refund event
    expect(fixture.core).toContain("refunds/create");
    for (const h of hooks) expect((h.variables as any).webhookSubscription.uri).toBe("https://members.strongyears.com/api/webhooks/shopify");
    const app = await plan("app", "core");
    const appHooks = app.ops.filter((o) => o.op === "WebhookCreate").map((o) => (o.variables as any).topic);
    expect(appHooks).toEqual([...fixture.core, ...fixture.enrichment].map(toEnum));
  });

  it("arm T (the 7-day trial, cell t12) is the launch default (CANON UPDATE 6); B (cell B) is the fallback, A the old test arm", () => {
    expect(FUNNEL_ARMS.find((a) => a.default)?.id).toBe("T");
    expect(FUNNEL_ARMS.find((a) => a.id === "T")?.cell).toBe("t12");
    expect(FUNNEL_ARMS.find((a) => a.id === "B")?.cell).toBe("m12");
    expect(FUNNEL_ARMS.filter((a) => a.default)).toHaveLength(1);
  });

  it("ebook cells are separate products with one real price each; gifts never renew; kit ships", () => {
    const ebooks = PRODUCTS.filter((p) => p.role === "ebook");
    expect(ebooks.map((p) => p.variants[0].price).sort()).toEqual(["12.00", "15.00", "7.00"]);
    expect(ebooks.every((p) => p.variants.length === 1 && !p.subscriptionOnly)).toBe(true);
    const gift = PRODUCTS.find((p) => p.role === "gift")!;
    expect(gift.subscriptionOnly).toBe(false);
    expect(gift.variants.map((v) => v.price)).toEqual(["49.00", "119.00"]);
    const kit = PRODUCTS.find((p) => p.role === "bump_kit")!;
    expect(kit.variants[0].requiresShipping).toBe(true);
    expect(kit.variants[0].initialQuantity).toBe(0);
    const prices = Object.fromEntries(PRODUCTS.filter((p) => p.subscriptionOnly && p.role !== "coached").map((p) => [p.role, p.variants[0].price]));
    expect(prices).toEqual({ founding: "25.00", standard: "35.00", annual: "249.00", essentials: "12.00" });
    // R3 coached cells (ASCENSION.md): one product per price, unlisted, honest cap = real inventory starting at 0.
    const coached = PRODUCTS.filter((p) => p.role === "coached");
    expect(coached.map((p) => [p.cell, p.variants[0].price])).toEqual([["c147", "147.00"], ["c97", "97.00"], ["c197", "197.00"]]);
    for (const p of coached) {
      expect(p.status).toBe("UNLISTED");
      expect(p.variants[0]).toMatchObject({ tracked: true, initialQuantity: 0, inventoryPolicy: "DENY" });
      expect(p.descriptionHtml).toMatch(/real person/);
    }
  });

  it("refuses the K9SUPPS store by domain or name", () => {
    expect(() => assertNotForbiddenShop("k9supps.myshopify.com")).toThrow(/Refusing/);
    expect(() => assertNotForbiddenShop("K9 Supps")).toThrow(/Refusing/);
    expect(() => assertNotForbiddenShop("strong-years.myshopify.com")).not.toThrow();
  });
});
