import { describe, it, expect } from "vitest";
import type { GraphQLRunner, RecordedOp } from "../src/client.ts";
import { ensureWebhooks, webhookTopics } from "../src/webhookHeal.ts";

const URI = "https://members.strongyears.com/api/webhooks/shopify";

function fakeStore(existing: { id: string; topic: string; uri: string }[]): GraphQLRunner {
  const recorded: RecordedOp[] = [];
  let seq = 0;
  return {
    dryRun: true, recorded,
    async run(step, op, variables = {}) {
      recorded.push({ seq: ++seq, step, op, kind: op === "WebhookList" ? "query" : "mutation", variables });
      if (op === "WebhookList") return { webhookSubscriptions: { nodes: existing } } as any;
      if (op === "WebhookCreate") return { webhookSubscriptionCreate: { webhookSubscription: { id: "new" }, userErrors: [] } } as any;
      if (op === "WebhookUpdate") return { webhookSubscriptionUpdate: { webhookSubscription: { id: "upd" }, userErrors: [] } } as any;
      throw new Error(`unexpected op ${op}`);
    },
  };
}

describe("webhook self-heal", () => {
  const topics = webhookTopics("shopify_subscriptions");
  const healthy = topics.map((t, i) => ({ id: `gid://shopify/WebhookSubscription/${i}`, topic: t, uri: URI }));

  it("healthy store: no writes", async () => {
    const g = fakeStore(healthy);
    const r = await ensureWebhooks(g, { engine: "shopify_subscriptions", membersAppUrl: "https://members.strongyears.com/" });
    expect(r.created).toEqual([]); expect(r.updated).toEqual([]);
    expect(r.skipped.length).toBe(topics.length);
    expect(g.recorded.filter((o) => o.kind === "mutation")).toEqual([]);
  });

  it("re-creates topics Shopify deleted after 19 failed deliveries and repoints a stale URI", async () => {
    const store = healthy.filter((h) => h.topic !== "ORDERS_PAID" && h.topic !== "REFUNDS_CREATE")
      .map((h) => (h.topic === "ORDERS_CANCELLED" ? { ...h, uri: "https://old.example.com/hook" } : h));
    const g = fakeStore(store);
    const r = await ensureWebhooks(g, { engine: "shopify_subscriptions", membersAppUrl: "https://members.strongyears.com" });
    expect(r.created.sort()).toEqual(["webhook:ORDERS_PAID", "webhook:REFUNDS_CREATE"]);
    expect(r.updated).toEqual(["webhook:ORDERS_CANCELLED"]);
    const paid = g.recorded.find((o) => o.op === "WebhookCreate" && (o.variables as any).topic === "ORDERS_PAID")!;
    expect((paid.variables as any).webhookSubscription.uri).toBe(URI);
    expect((paid.variables as any).webhookSubscription.metafieldNamespaces).toBeTruthy();
  });

  it("keeps the correct subscription when a topic has duplicates and reports the extra one", async () => {
    const g = fakeStore([...healthy, { id: "dup", topic: "ORDERS_PAID", uri: "https://old.example.com/hook" }]);
    const r = await ensureWebhooks(g, { engine: "shopify_subscriptions", membersAppUrl: "https://members.strongyears.com" });
    expect(r.updated).toEqual([]); expect(r.created).toEqual([]);
    expect(r.duplicates).toEqual(["ORDERS_PAID → https://old.example.com/hook"]);
  });

  it("throws on Shopify userErrors instead of reporting success", async () => {
    const g = fakeStore([]);
    g.run = async (_s, op) => (op === "WebhookList" ? { webhookSubscriptions: { nodes: [] } } : { webhookSubscriptionCreate: { userErrors: [{ field: ["uri"], message: "is invalid" }] } }) as any;
    await expect(ensureWebhooks(g, { engine: "shopify_subscriptions", membersAppUrl: "https://x.example.com" })).rejects.toThrow(/is invalid/);
  });
});
