/**
 * INTEGRATION.md §4 and §5 on the Shopify launch path:
 *  - the Essentials save offer is a request (human queue on the launch path; Admin API
 *    queue when our app owns the contract), never a silent change, and the cancel
 *    link stays one tap away;
 *  - renewal reminders re-check what the order data says before sending and use
 *    conditional wording, because a cancel made on Shopify's page never reaches us.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { seedShopifyCatalog } from "@/lib/billing/shopify";
import { handleShopifyWebhook } from "@/lib/billing/shopifyWebhook";
import { canOfferEssentials, requestEssentialsSwitch } from "@/lib/billing/planChange";
import { renewalCertainty, runReminders } from "@/lib/billing/clock";

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
const paid = (id: number, at: Date, opts: { codes?: string[]; discount?: string; source?: string } = {}) =>
  handleShopifyWebhook(store, {
    webhookId: `wh-cancel-rem-${++n}`,
    topic: "orders/paid",
    now: at,
    payload: {
      id,
      email: "ruth@example.com",
      processed_at: at.toISOString(),
      source_name: opts.source ?? "web",
      customer: { id: 4001, email: "ruth@example.com", first_name: "Ruth" },
      discount_codes: (opts.codes ?? []).map((code) => ({ code })),
      note_attributes: [],
      line_items: [{ id: id * 10 + 1, variant_id: 9000000025, price: "25.00", quantity: 1, total_discount: opts.discount ?? "0.00", selling_plan_allocation: { selling_plan: { id: 7000000025 } } }],
    },
  });

describe("Essentials save offer as a request", () => {
  it("records a human-queue request on the launch path, opens a ticket, emails the member with the cancel link; a second tap doesn't duplicate it", async () => {
    await paid(1, new Date("2026-10-01T12:00:00Z"), { codes: ["STARTER12"], discount: "13.00" });
    const member = (await store.findOne("members", { email: "ruth@example.com" }))!;
    const m = (await store.find("memberships"))[0]!;
    expect(canOfferEssentials(m)).toBe(true);
    const req = await requestEssentialsSwitch(store, member, m, { SUBSCRIPTION_ENGINE: "shopify_subscriptions", SHOPIFY_CUSTOMER_ACCOUNT_URL: "https://shopify.com/00000/account" });
    expect(req).toMatchObject({ method: "human_queue", status: "open", to_plan: "essentials", from_plan: "bundle_m12" });
    expect((await store.find("plan_change_requests")).length).toBe(1);
    const again = await requestEssentialsSwitch(store, member, m, { SUBSCRIPTION_ENGINE: "shopify_subscriptions" });
    expect(again.id).toBe(req.id);
    expect((await store.find("support_tickets", { reason: "plan_change" })).length).toBe(1);
    const mail = (await store.find("outbox", { to: "ruth@example.com", template: "SH_essentials_requested" }))[0]!;
    expect(mail.body).toContain("1 business day");
    expect(mail.body).toContain("https://shopify.com/00000/account");
    expect(mail.body).not.toMatch(/for life/i);
    // nothing changed on the membership itself
    expect((await store.get("memberships", m.id))!.price_cents).toBe(2500);
  });

  it("queues the Admin API path only when our app owns the contract", async () => {
    await paid(2, new Date("2026-10-01T12:00:00Z"));
    const member = (await store.findOne("members", { email: "ruth@example.com" }))!;
    const m = (await store.find("memberships"))[0]!;
    await store.update("memberships", m.id, { shopify_contract_id: "555" });
    const req = await requestEssentialsSwitch(store, member, (await store.get("memberships", m.id))!, { SUBSCRIPTION_ENGINE: "app" });
    expect(req.method).toBe("admin_api");
  });

  it("Essentials is never offered to someone already at or below $12, or whose membership has ended", () => {
    expect(canOfferEssentials({ plan: "essentials", price_cents: 1200, status: "active" })).toBe(false);
    expect(canOfferEssentials({ plan: "monthly", price_cents: 2500, status: "refunded" })).toBe(false);
    expect(canOfferEssentials({ plan: "annual", price_cents: 24900, status: "active" })).toBe(false);
  });
});

describe("renewal reminders re-check the order data", () => {
  it("launch path: the reminder is conditional ('if your membership is still active') and points at Shopify's account page", async () => {
    const t0 = new Date("2026-10-01T12:00:00Z");
    await paid(3, t0, { codes: ["STARTER12"], discount: "13.00" });
    const m = (await store.find("memberships"))[0]!;
    expect(await renewalCertainty(store, m, t0)).toBe("unsure");
    const before = new Date("2026-10-30T13:00:00Z"); // 47 hours before the first $25 renewal
    const r = await runReminders(store, before);
    expect(r.sent).toBe(1);
    const mail = (await store.find("outbox", { to: "ruth@example.com", template: "C_pre_charge_48h" }))[0]!;
    expect(mail.subject).toMatch(/if your membership is still active/i);
    expect(mail.body).toContain("$12 starter month ends");
    expect(mail.body).toContain("$25.00");
    expect(mail.body).toContain("https://shopify.com/00000/account");
    expect(mail.body).toMatch(/already cancelled or paused/);
    expect(mail.body).not.toContain("/app/account/cancel");
  });

  it("no reminder once the paid-through date has passed without a renewal order, or after a refund", async () => {
    const t0 = new Date("2026-10-01T12:00:00Z");
    await paid(4, t0);
    const m = (await store.find("memberships"))[0]!;
    expect(await renewalCertainty(store, m, new Date("2026-11-02T00:00:00Z"))).toBe("skip");
    await handleShopifyWebhook(store, { webhookId: "wh-cancel-rem-refund", topic: "refunds/create", payload: { id: 9, order_id: 4, refund_line_items: [{ line_item_id: 41, subtotal: "25.00" }] } });
    expect(await renewalCertainty(store, (await store.get("memberships", m.id))!, t0)).toBe("skip");
    expect((await runReminders(store, new Date("2026-10-30T13:00:00Z"))).sent).toBe(0);
  });

  it("app engine with a contract on file: the plain wording (we do see contract events there)", async () => {
    vi.stubEnv("SUBSCRIPTION_ENGINE", "app");
    const t0 = new Date("2026-10-01T12:00:00Z");
    await paid(5, t0);
    const m = (await store.find("memberships"))[0]!;
    await store.update("memberships", m.id, { shopify_contract_id: "777" });
    expect(await renewalCertainty(store, (await store.get("memberships", m.id))!, t0)).toBe("certain");
    await runReminders(store, new Date("2026-10-30T13:00:00Z"));
    const mail = (await store.find("outbox", { to: "ruth@example.com", template: "C_pre_charge_48h" }))[0]!;
    expect(mail.subject).not.toMatch(/if your membership/i);
  });
});
