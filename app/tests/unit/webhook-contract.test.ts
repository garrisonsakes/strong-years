import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { SHOPIFY_TOPICS, SHOPIFY_TOPICS_CORE, SHOPIFY_TOPICS_ENRICHMENT, isShopifyTopic } from "@/lib/billing/shopifyWebhook";

/**
 * Contract test (INTEGRATION.md §2): the topics the Shopify provisioning registers
 * (shopify/config/webhook-topics.json, imported by shopify/config/catalog.ts) are
 * exactly the topics the members app handles. Core topics are the only source of
 * membership truth; enrichment topics only fire for contracts our own app owns.
 */
const fixture = JSON.parse(readFileSync(path.join(process.cwd(), "..", "shopify", "config", "webhook-topics.json"), "utf8")) as { core: string[]; enrichment: string[] };

describe("Shopify webhook contract (fixture-driven)", () => {
  it("provisioning's core topics == the app's core handlers, in order", () => {
    expect([...SHOPIFY_TOPICS_CORE]).toEqual(fixture.core);
  });

  it("provisioning's app-engine enrichment topics == the app's enrichment handlers", () => {
    expect([...SHOPIFY_TOPICS_ENRICHMENT]).toEqual(fixture.enrichment);
  });

  it("the handled set is exactly core + enrichment; 'orders/refunded' is not an Admin API topic and is not handled", () => {
    expect([...SHOPIFY_TOPICS]).toEqual([...fixture.core, ...fixture.enrichment]);
    expect(isShopifyTopic("orders/refunded")).toBe(false);
    expect(isShopifyTopic("refunds/create")).toBe(true);
    expect(isShopifyTopic("orders/paid")).toBe(true);
  });

  it("core topics are store-wide ones (no own_subscription_contracts topic is relied on for access)", () => {
    for (const t of fixture.core) expect(t.startsWith("subscription_")).toBe(false);
    for (const t of fixture.enrichment) expect(t.startsWith("subscription_")).toBe(true);
  });
});
