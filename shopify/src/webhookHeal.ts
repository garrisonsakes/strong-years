/**
 * Webhook self-heal. Shopify deletes a webhook subscription after 19 consecutive failed deliveries
 * (about 48 h of retries), and the members app loses access events silently from then on. This module
 * makes the store's subscriptions match config/webhook-topics.json again: missing topics are re-created,
 * topics pointing at the wrong URI are repointed, correct ones are left alone. It is the same code
 * path provisioning step 7 uses, so re-running it is always safe.
 *
 * Run on a schedule with `npm run webhooks:heal` (DRY_RUN=false for live, same guards as provision).
 * A re-created topic means deliveries were dropped: reconcile orders since the last delivery the
 * members app received (see RUNBOOK.md "Webhook self-heal").
 */
import { METAFIELD_NAMESPACE, WEBHOOK_PATH, WEBHOOK_TOPICS_APP_ENGINE, WEBHOOK_TOPICS_CORE } from "../config/catalog.ts";
import type { GraphQLRunner } from "./client.ts";

export interface WebhookHealReport {
  created: string[];
  updated: string[];
  skipped: string[];
  /** Extra subscriptions on a topic we own that point elsewhere (left in place; listed for a human). */
  duplicates: string[];
}

function userErrors(what: string, payload: any) {
  const ue = payload?.userErrors || [];
  if (ue.length) throw new Error(`${what}: ${ue.map((e: any) => `${(e.field || []).join(".")} ${e.message}`).join("; ")}`);
}

export function webhookTopics(engine: "shopify_subscriptions" | "app"): string[] {
  return [...WEBHOOK_TOPICS_CORE, ...(engine === "app" ? WEBHOOK_TOPICS_APP_ENGINE : [])];
}

export async function ensureWebhooks(gql: GraphQLRunner, o: { engine: "shopify_subscriptions" | "app"; membersAppUrl: string }): Promise<WebhookHealReport> {
  const r: WebhookHealReport = { created: [], updated: [], skipped: [], duplicates: [] };
  const uri = `${o.membersAppUrl.replace(/\/$/, "")}${WEBHOOK_PATH}`;
  const existing = ((await gql.run<any>("List existing webhook subscriptions", "WebhookList")).webhookSubscriptions.nodes || []) as any[];
  for (const topic of webhookTopics(o.engine)) {
    const mine = existing.filter((h) => h.topic === topic);
    const same = mine.find((h) => h.uri === uri) || mine[0];
    for (const h of mine) if (h !== same) r.duplicates.push(`${topic} → ${h.uri}`);
    if (same && same.uri === uri) { r.skipped.push(`webhook:${topic}`); continue; }
    if (same) {
      const res = await gql.run<any>(`Repoint webhook ${topic}`, "WebhookUpdate", { id: same.id, webhookSubscription: { uri } });
      userErrors(`webhook ${topic}`, res.webhookSubscriptionUpdate); r.updated.push(`webhook:${topic}`);
    } else {
      const res = await gql.run<any>(`Subscribe webhook ${topic} → members app`, "WebhookCreate", {
        topic,
        webhookSubscription: { uri, format: "JSON", ...(topic.startsWith("ORDERS_") ? { metafieldNamespaces: [METAFIELD_NAMESPACE] } : {}) },
      });
      userErrors(`webhook ${topic}`, res.webhookSubscriptionCreate); r.created.push(`webhook:${topic}`);
    }
  }
  return r;
}
