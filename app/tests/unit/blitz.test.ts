import { afterEach, beforeEach, describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { assignPriceCell, resolveFoundingOffer } from "@/lib/blitz";
import { quoteCheckout } from "@/lib/pricing";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { foundingClaimed } from "@/lib/members";
import { chooseProcessor, type Candidate } from "@/lib/billing/processors/router";
import { routeCheckout } from "@/lib/billing/processors";
import { sendSms } from "@/lib/notify";
import { blitz } from "@/lib/config";
import { buildQuotes } from "@/lib/checkoutQuotes";

const now = new Date("2026-10-01T17:00:00Z");

describe("price-test assignment ($25 vs $30)", () => {
  it("is deterministic and sticky per visitor", () => {
    const a = assignPriceCell("visitor-123", [2500, 3000]);
    for (let i = 0; i < 5; i++) expect(assignPriceCell("visitor-123", [2500, 3000])).toBe(a);
  });

  it("splits close to 50/50 across visitors", () => {
    let n2500 = 0;
    const N = 10_000;
    for (let i = 0; i < N; i++) if (assignPriceCell(crypto.randomUUID(), [2500, 3000]) === 2500) n2500++;
    expect(n2500 / N).toBeGreaterThan(0.48);
    expect(n2500 / N).toBeLessThan(0.52);
  });

  it("defaults to blitz mode: $25 default, $35 standard, no $1 trial arm (CANON UPDATE 2), front-end pages off", () => {
    expect(blitz.enabled).toBe(true);
    expect(blitz.priceCells).toEqual([2500, 3000]);
    expect(blitz.defaultPriceCents).toBe(2500);
    expect(blitz.standardPriceCents).toBe(3500);
    expect(blitz.trialArmEnabled).toBe(false);
    expect(blitz.frontEndPagesEnabled).toBe(false);
  });
});

describe("resolveFoundingOffer (price cells + real cap)", () => {
  const base = { visitorId: "v1", claimed: 10, cap: 5000, testOn: true, cells: [2500, 3000], defaultCents: 2500, standardCents: 3500 };
  it("test on: the visitor's cell price, founding", () => {
    const o = resolveFoundingOffer(base);
    expect(o.founding).toBe(true);
    expect(o.priceCents).toBe(assignPriceCell("v1", [2500, 3000]));
    expect(o.cell).toBe(`p${o.priceCents}`);
    expect(o.left).toBe(4990);
  });
  it("test off (or no visitor id): the default $25", () => {
    expect(resolveFoundingOffer({ ...base, testOn: false })).toMatchObject({ priceCents: 2500, cell: "default", founding: true });
    expect(resolveFoundingOffer({ ...base, visitorId: null })).toMatchObject({ priceCents: 2500, cell: "default" });
  });
  it("cap reached: the cohort closes and new members pay the standard price with no founding lock", () => {
    expect(resolveFoundingOffer({ ...base, claimed: 5000 })).toMatchObject({ cohortOpen: false, founding: false, priceCents: 3500, cell: "standard", left: 0 });
  });
});

describe("blitz checkout quotes and bumps", () => {
  const q = (bumps: ("reset" | "kitchen" | "wallplan")[], extra: Partial<Parameters<typeof quoteCheckout>[0]> = {}) =>
    quoteCheckout({ offer: "founding", arm: "B", bumps, now, foundingCents: 3000, smsOn: false, ...extra });

  it("the $7 Reset, $17 Kitchen and $9 Wall Plan are unticked bumps on the founding checkout", () => {
    expect(q([]).bumpsAllowed).toEqual(["reset", "kitchen", "wallplan"]);
    expect(q([]).todayCents).toBe(3000);
    const all = q(["wallplan", "kitchen", "reset"]);
    expect(all.lines.map((l) => l.sku)).toEqual(["membership", "reset", "kitchen", "wallplan"]);
    expect(all.todayCents).toBe(3000 + 700 + 1700 + 900);
    expect(all.terms[0]).toMatch(/one-time, yours to keep/);
    expect(all.recurring!.priceCents).toBe(3000); // bumps never recur
  });
  it("other checkouts only get the Wall Plan; Safe Mode gets none", () => {
    expect(quoteCheckout({ offer: "trial", arm: "A", now, bumps: ["reset", "wallplan"] }).lines.map((l) => l.sku)).toEqual(["trial_fee", "wallplan"]);
    expect(q(["reset"], { gentle: true }).bumpsAllowed).toEqual([]);
    expect(q(["reset"], { gentle: true }).todayCents).toBe(3000);
  });
  it("uses the exact 14-day money-back guarantee phrase and email-only reminders until SMS is on", () => {
    const t = q([]).terms.join(" ");
    expect(t).toMatch(/14-day money-back guarantee/);
    expect(t).toMatch(/remind you by email 48 hours/);
    expect(q([], { smsOn: true }).terms.join(" ")).toMatch(/by email and text/);
  });
  it("closed cohort: standard membership wording, no founding lock", () => {
    const c = quoteCheckout({ offer: "founding", arm: "B", now, foundingCents: 3500, cohortOpen: false, standardCents: 3500 });
    expect(c.recurring!.founding).toBe(false);
    expect(c.lines[0]!.label).toBe("Strong Years membership, first month");
    expect(c.terms.join(" ")).not.toMatch(/founding price/);
    expect(c.todayCents).toBe(3500);
  });
  it("buildQuotes pre-computes every bump combination", () => {
    const founding = resolveFoundingOffer({ visitorId: null, claimed: 0, cap: 5000, testOn: false, cells: [2500, 3000], defaultCents: 2500, standardCents: 3500 });
    const { quotes, bumpsAllowed } = buildQuotes({ offer: "founding", arm: "B", gentle: false, founding, now });
    expect(bumpsAllowed).toHaveLength(3);
    expect(Object.keys(quotes)).toHaveLength(8);
    expect(quotes[""]!.todayLabel).toBe("$25.00");
    expect(quotes["reset,kitchen,wallplan"]!.todayLabel).toBe("$58.00");
  });
});

describe("blitz checkout end to end (in-memory)", () => {
  let store: MemoryStore;
  const input = (over: Partial<StartCheckoutInput> = {}): StartCheckoutInput => ({
    offer: "founding",
    arm: "B",
    bumps: [],
    gentle: false,
    email: `m${Math.random()}@example.com`,
    firstName: "Mae",
    phone: "",
    smsConsent: false,
    autoRenewConsent: true,
    ageConsent: true,
    gift: null,
    attribution: null,
    leadId: null,
    ip: null,
    userAgent: null,
    visitorId: "visitor-abc",
    ...over,
  });
  const complete = async (intentId: string) =>
    handleStripeEvent(store, { id: `evt_${crypto.randomUUID()}`, type: "checkout.session.completed", data: { object: { metadata: { intent_id: intentId }, payment_status: "paid", subscription: `sub_${intentId}`, payment_intent: `pi_${intentId}` } } });

  beforeEach(() => {
    store = new MemoryStore();
    setStoreForTests(store);
  });
  afterEach(() => {
    delete process.env.FOUNDING_COHORT_CAP;
  });

  it("logs the sticky price cell on the intent and the membership, and records bump orders by SKU", async () => {
    const res = await startCheckout(store, input({ bumps: ["reset", "wallplan"] }));
    if (!res.ok) throw new Error("checkout failed");
    const cellPrice = assignPriceCell("visitor-abc", [2500, 3000]);
    const intent = (await store.get("checkout_intents", res.intentId))!;
    expect(intent.price_cell).toBe(`p${cellPrice}`);
    expect(intent.visitor_id).toBe("visitor-abc");
    expect(intent.processor).toBe("stripe");
    expect(intent.amount_today_cents).toBe(cellPrice + 700 + 900);
    await complete(res.intentId);
    const m = (await store.findOne("memberships", { founding: true }))!;
    expect(m.price_cents).toBe(cellPrice);
    expect(m.price_cell).toBe(`p${cellPrice}`);
    const skus = (await store.find("sy_orders", { member_id: m.member_id })).map((o) => o.offer_code).sort();
    expect(skus).toEqual(["founding", "reset", "wallplan"]);
  });

  it("closes the founding cohort at the real cap and switches new members to the standard price", async () => {
    process.env.FOUNDING_COHORT_CAP = "2";
    for (let i = 0; i < 2; i++) {
      const r = await startCheckout(store, input({ visitorId: `v${i}` }));
      if (!r.ok) throw new Error("fail");
      await complete(r.intentId);
    }
    expect(await foundingClaimed(store)).toBe(2);
    const r3 = await startCheckout(store, input({ visitorId: "v-late" }));
    if (!r3.ok) throw new Error("fail");
    expect(r3.quote.recurring).toMatchObject({ priceCents: 3500, founding: false });
    await complete(r3.intentId);
    expect(await foundingClaimed(store)).toBe(2);
    const late = (await store.findOne("memberships", { price_cell: "standard" }))!;
    expect(late).toMatchObject({ founding: false, price_cents: 3500 });
  });
});

describe("processor routing", () => {
  const c = (id: "stripe" | "braintree", o: Partial<Candidate> = {}): Candidate => ({ id, available: true, volume30dCents: 0, capCents: 0, ...o });
  const base = { routing: "failover" as const, braintreeShare: 0, key: "k", amountCents: 3000 };
  it("failover: Stripe first; Braintree when Stripe is unavailable or over its volume cap", () => {
    expect(chooseProcessor({ ...base, candidates: [c("stripe"), c("braintree")] })).toMatchObject({ id: "stripe", reason: "primary" });
    expect(chooseProcessor({ ...base, candidates: [c("stripe", { available: false }), c("braintree")] })).toMatchObject({ id: "braintree", reason: "failover_unavailable" });
    expect(chooseProcessor({ ...base, candidates: [c("stripe", { volume30dCents: 99_000, capCents: 100_000 }), c("braintree")] })).toMatchObject({ id: "braintree", reason: "failover_capped" });
  });
  it("split: a deterministic share goes to Braintree", () => {
    let bt = 0;
    for (let i = 0; i < 4000; i++) if (chooseProcessor({ ...base, routing: "split", braintreeShare: 0.3, key: `k${i}`, candidates: [c("stripe"), c("braintree")] }).id === "braintree") bt++;
    expect(bt / 4000).toBeGreaterThan(0.27);
    expect(bt / 4000).toBeLessThan(0.33);
    const once = chooseProcessor({ ...base, routing: "split", braintreeShare: 0.3, key: "same", candidates: [c("stripe"), c("braintree")] }).id;
    expect(chooseProcessor({ ...base, routing: "split", braintreeShare: 0.3, key: "same", candidates: [c("stripe"), c("braintree")] }).id).toBe(once);
  });
  it("volume guard: all capped keeps selling on the most headroom and flags it; none available → null", () => {
    const r = chooseProcessor({ ...base, candidates: [c("stripe", { volume30dCents: 100_000, capCents: 100_000 }), c("braintree", { volume30dCents: 10_000, capCents: 11_000 })] });
    expect(r).toMatchObject({ id: "braintree", reason: "all_capped", overCap: true });
    expect(chooseProcessor({ ...base, candidates: [c("stripe", { available: false }), c("braintree", { available: false })] }).id).toBeNull();
  });
  it("routeCheckout: Braintree stays out of rotation unless enabled; enabled without credentials it runs as a mock", async () => {
    const store = new MemoryStore();
    setStoreForTests(store);
    expect((await routeCheckout(store, "x", 2500)).id).toBe("stripe");
    process.env.BRAINTREE_ENABLED = "true";
    process.env.PROCESSOR_ROUTING = "split";
    process.env.PROCESSOR_SPLIT_BRAINTREE = "1";
    try {
      expect((await routeCheckout(store, "x", 2500)).id).toBe("braintree");
      process.env.BRAINTREE_MERCHANT_ID = "m";
      process.env.BRAINTREE_PUBLIC_KEY = "p";
      process.env.BRAINTREE_PRIVATE_KEY = "k";
      expect((await routeCheckout(store, "x", 2500)).id).toBe("stripe"); // real creds but stub adapter: never routed
    } finally {
      for (const k of ["BRAINTREE_ENABLED", "PROCESSOR_ROUTING", "PROCESSOR_SPLIT_BRAINTREE", "BRAINTREE_MERCHANT_ID", "BRAINTREE_PUBLIC_KEY", "BRAINTREE_PRIVATE_KEY"]) delete process.env[k];
    }
  });
});

describe("SMS flag", () => {
  it("texts are skipped (not sent) until SMS_ENABLED; on-call alerts are exempt", async () => {
    const store = new MemoryStore();
    setStoreForTests(store);
    const a = await sendSms("+15555550100", "hello", "S1_welcome");
    expect(a.status).toBe("skipped");
    const b = await sendSms("+15555550100", "alert", "oncall_alert");
    expect(b.status).toBe("stubbed");
    process.env.SMS_ENABLED = "true";
    try {
      expect((await sendSms("+15555550100", "hello", "S1_welcome")).status).toBe("stubbed");
    } finally {
      delete process.env.SMS_ENABLED;
    }
  });
});

describe("content files", () => {
  it("all download PDFs exist in content/downloads", async () => {
    const { ALL_DOWNLOAD_FILES } = await import("@/lib/products");
    for (const f of ALL_DOWNLOAD_FILES) expect(fs.existsSync(path.join(__dirname, "..", "..", "content", "downloads", f)), f).toBe(true);
  });
});
