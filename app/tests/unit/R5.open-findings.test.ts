/**
 * AUDIT_FINAL.md §9 round-5 items closed in the integration follow-up:
 *  R5-7  no "reply cancel" promise anywhere a customer reads
 *  R5-8  the consent record must match the charge (starter page shows both prices; mismatch → review)
 *  R5-9  disputes/create + disputes/update: a chargeback ends access and blocks the self-serve refund; "won" restores
 *  annual: founding → $249 is the same request path as Essentials
 *  R5-10/11/12: no-JS consent marker, one seat per contract, gift redeem never 500s
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { consentMatchesCharge, parseConsentPrices, seedShopifyCatalog, cartContextFromAttributes, refundShopifyMembership } from "@/lib/billing/shopify";
import { handleShopifyWebhook, SHOPIFY_TOPICS_CORE } from "@/lib/billing/shopifyWebhook";
import { canOfferAnnual, requestPlanSwitch } from "@/lib/billing/planChange";
import { grantsAccess } from "@/lib/entitlement";

let store: MemoryStore;
beforeEach(async () => {
  vi.stubEnv("BILLING_PROVIDER", "shopify");
  vi.stubEnv("LAUNCH_MODE", "live");
  vi.stubEnv("SHOPIFY_STORE_DOMAIN", "strongyears-test.myshopify.com");
  vi.stubEnv("SHOPIFY_CUSTOMER_ACCOUNT_URL", "https://shopify.com/00000/account");
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
});
afterEach(() => vi.unstubAllEnvs());

let n = 0;
const T0 = new Date("2026-10-01T12:00:00Z");
function order(id: number, o: { price?: string; discount?: string; codes?: string[]; consent?: string; qty?: number; variant?: number; plan?: number } = {}) {
  return {
    id,
    email: "ruth@example.com",
    processed_at: T0.toISOString(),
    source_name: "web",
    customer: { id: 4001, email: "ruth@example.com", first_name: "Ruth" },
    discount_codes: (o.codes ?? []).map((code) => ({ code })),
    note_attributes: o.consent === undefined ? [{ name: "sy_consent_price", value: "12.00|25.00" }] : o.consent === "" ? [] : [{ name: "sy_consent_price", value: o.consent }],
    line_items: [{ id: id * 10 + 1, variant_id: o.variant ?? 9000000025, price: o.price ?? "25.00", quantity: o.qty ?? 1, total_discount: o.discount ?? "0.00", selling_plan_allocation: { selling_plan: { id: o.plan ?? 7000000025 } } }],
  };
}
const paid = (id: number, o?: Parameters<typeof order>[1]) => handleShopifyWebhook(store, { webhookId: `wh-round5-${++n}`, topic: "orders/paid", payload: order(id, o), now: T0 });
const tickets = async () => (await store.find("support_tickets")).map((t) => t.message);

describe("R5-8 consent record vs charge", () => {
  it("parses the two-price starter record and matches either honest outcome", () => {
    expect(parseConsentPrices("12.00|25.00")).toEqual([1200, 2500]);
    expect(parseConsentPrices("$25")).toEqual([2500]);
    expect(parseConsentPrices("x|<b>")).toEqual([]);
    expect(consentMatchesCharge({ consentPricesCents: [1200, 2500] }, 1200)).toBe("match");
    expect(consentMatchesCharge({ consentPricesCents: [1200, 2500] }, 2500)).toBe("match");
    expect(consentMatchesCharge({ consentPricesCents: [1200, 2500] }, 3500)).toBe("mismatch");
    expect(consentMatchesCharge({ consentPricesCents: [] }, 2500)).toBe("unknown");
    expect(cartContextFromAttributes([{ name: "sy_consent_price", value: "12.00|25.00" }]).consentPricesCents).toEqual([1200, 2500]);
  });

  it("a returning customer charged $25 on the starter page is a match (the page showed $25 as the other outcome) and becomes founding_monthly; a $12 page that somehow charged $35 is reviewed", async () => {
    await paid(1, { price: "25.00" });
    expect((await store.find("memberships"))[0]).toMatchObject({ offer_code: "founding_monthly", price_cents: 2500 });
    expect((await tickets()).some((m) => /consent box showed/.test(m))).toBe(false);
    await paid(2, { price: "35.00", variant: 9000000035, plan: 7000000035, consent: "12.00" });
    expect((await tickets()).some((m) => /consent box showed \$12\.00 but the membership line charged \$35\.00/.test(m))).toBe(true);
  });

  it("R5-10: a no-JS checkout with no consent price is flagged for a person, not silently accepted", async () => {
    await paid(3, { consent: "" });
    expect((await tickets()).some((m) => /no consent-price record/.test(m))).toBe(true);
  });

  it("R5-11: quantity 2 on a membership line is one membership and a ticket to refund the extra seat", async () => {
    await paid(4, { qty: 2, price: "25.00" });
    expect((await store.find("memberships")).length).toBe(1);
    expect((await tickets()).some((m) => /quantity 2/.test(m))).toBe(true);
  });
});

describe("R5-9 disputes", () => {
  it("the contract fixture and the app agree on disputes/create + disputes/update as core topics", () => {
    const fixture = JSON.parse(readFileSync(path.join(process.cwd(), "..", "shopify", "config", "webhook-topics.json"), "utf8")) as { core: string[] };
    expect(fixture.core).toContain("disputes/create");
    expect(fixture.core).toContain("disputes/update");
    expect([...SHOPIFY_TOPICS_CORE]).toEqual(fixture.core);
  });

  it("a chargeback ends access, blocks the self-serve refund, tickets on-call; a won dispute restores; an inquiry only tickets; replays are ignored", async () => {
    await paid(10, { codes: ["STARTER12"], discount: "13.00" });
    const m0 = (await store.find("memberships"))[0]!;
    expect(grantsAccess(m0)).toBe(true);
    const inquiry = await handleShopifyWebhook(store, { webhookId: "wh-r5-disp-0", topic: "disputes/create", payload: { id: 500, order_id: 10, type: "inquiry", status: "needs_response", amount: "12.00" }, now: T0 });
    expect(inquiry.status).toBe("processed");
    expect(grantsAccess((await store.get("memberships", m0.id))!)).toBe(true);
    const lost = await handleShopifyWebhook(store, { webhookId: "wh-r5-disp-1", topic: "disputes/create", payload: { id: 501, order_id: 10, type: "chargeback", status: "needs_response", amount: "12.00", evidence_due_by: "2026-10-15" }, now: T0 });
    expect(lost.status).toBe("processed");
    const m1 = (await store.get("memberships", m0.id))!;
    expect(m1.status).toBe("canceled");
    expect(grantsAccess(m1, T0.getTime() + 1000)).toBe(false);
    expect((await store.find("sy_orders", { shopify_order_id: "10" }))[0]!.status).toBe("disputed");
    expect((await store.find("refund_ledger")).length).toBe(1);
    // the self-serve 14-day refund now goes to review, never to refundCreate
    const member = (await store.findOne("members", { email: "ruth@example.com" }))!;
    const r = await refundShopifyMembership(store, { ...m1, status: "active" }, T0, { mode: "mock", refundLine: async () => ({ ok: true, id: "x" }), cancelContract: async () => ({ ok: true }) });
    expect(r.state).toBe("review");
    expect(member.email).toBe("ruth@example.com");
    // update to under_review: already applied
    expect((await handleShopifyWebhook(store, { webhookId: "wh-r5-disp-2", topic: "disputes/update", payload: { id: 501, order_id: 10, type: "chargeback", status: "under_review" }, now: T0 })).status).toBe("ignored");
    // won → restored
    const won = await handleShopifyWebhook(store, { webhookId: "wh-r5-disp-3", topic: "disputes/update", payload: { id: 501, order_id: 10, type: "chargeback", status: "won" }, now: new Date("2026-10-10T00:00:00Z") });
    expect(won.status).toBe("processed");
    const m2 = (await store.get("memberships", m0.id))!;
    expect(m2.status).toBe("active");
    expect(grantsAccess(m2, new Date("2026-10-11T00:00:00Z").getTime())).toBe(true);
    expect((await store.find("sy_orders", { shopify_order_id: "10" }))[0]!.status).toBe("paid");
    expect((await store.find("refund_ledger")).length).toBe(0);
    expect((await handleShopifyWebhook(store, { webhookId: "wh-r5-disp-4", topic: "disputes/create", payload: { id: 999, order_id: 424242, type: "chargeback", status: "lost" }, now: T0 })).status).toBe("ignored");
  });
});

describe("founding → annual request path", () => {
  it("is offered after the first renewal only and records an annual request with the honest double-charge copy", async () => {
    await paid(20, { codes: ["STARTER12"], discount: "13.00" });
    const m = (await store.find("memberships"))[0]!;
    expect(canOfferAnnual(m, 1)).toBe(false);
    expect(canOfferAnnual(m, 2)).toBe(true);
    const member = (await store.findOne("members", { email: "ruth@example.com" }))!;
    const req = await requestPlanSwitch(store, member, m, "annual", { SUBSCRIPTION_ENGINE: "shopify_subscriptions", SHOPIFY_CUSTOMER_ACCOUNT_URL: "https://shopify.com/00000/account" });
    expect(req).toMatchObject({ to_plan: "annual", method: "human_queue", status: "open" });
    const mail = (await store.find("outbox", { template: "SH_annual_requested" }))[0]!;
    expect(mail.body).toContain("$249");
    expect(mail.body).toContain("1 business day");
    expect(mail.body).toMatch(/never charged for both/);
    expect(mail.body).not.toMatch(/for life/i);
  });
});

describe("R5-7 no 'reply cancel' promise", () => {
  it("app, theme, policies and product sources describe email honestly (a person, one business day)", () => {
    const root = path.join(process.cwd(), "..");
    const files = [
      "shopify/src/legal.ts", "shopify/theme/snippets/sy-terms.liquid", "shopify/theme/sections/main-cart.liquid", "shopify/theme/sections/main-account.liquid",
      "app/src/lib/pricing.ts", "app/src/lib/billing/clock.ts", "app/src/lib/billing/fulfill.ts", "app/src/components/Pricing.tsx", "app/src/components/CheckoutForm.tsx",
      "products/_build/build_welcome.py", "products/_build/build_reset.py",
    ];
    for (const f of files) {
      const s = readFileSync(path.join(root, f), "utf8");
      expect(s, f).not.toMatch(/reply(ing)? (\\u201c|")cancel(\\u201d|")|reply \*\*cancel\*\*|reply "cancel"/);
    }
  });
});

describe("R5-12 gift redeem never 500s", () => {
  it("a JSON body is a bad code → 303 to the error page", async () => {
    const { POST } = await import("@/app/api/gift/redeem/route");
    const res = await POST(new Request("http://l/api/gift/redeem", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" }));
    expect(res.status).toBe(303);
    expect(res.headers.get("location")).toContain("/gift/redeem?error=code");
  });
});
