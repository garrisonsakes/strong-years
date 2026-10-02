/**
 * Minimal Admin GraphQL client: auth (static token OR Dev Dashboard client-credentials grant),
 * throttle-aware retries, and a DRY_RUN recorder that prints every operation instead of sending it.
 *
 * Auth note (2026): new "legacy custom apps" can't be created in the Shopify admin since Jan 1 2026.
 * The client creates a Dev Dashboard app in the SAME organization as the store and installs it; this
 * script then exchanges SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET for a 24-hour token
 * (POST https://{shop}/admin/oauth/access_token, grant_type=client_credentials;
 * shopify.dev/docs/apps/build/authentication-authorization/client-credentials-grant).
 * A pre-existing Admin API token (SHOPIFY_ADMIN_TOKEN) also works.
 */
import { OPS, type OpName } from "./operations.ts";
import { PRODUCTS } from "../config/catalog.ts";

export const API_VERSION = process.env.SHOPIFY_API_VERSION || "2026-07";

export interface RecordedOp {
  seq: number;
  step: string;
  op: OpName;
  kind: "query" | "mutation";
  variables: Record<string, unknown>;
}

export interface GraphQLRunner {
  dryRun: boolean;
  recorded: RecordedOp[];
  run<T = any>(step: string, op: OpName, variables?: Record<string, unknown>): Promise<T>;
}

type Fetch = typeof fetch;

/** Shops this script must never touch. Defaults include the K9SUPPS store. */
export function assertNotForbiddenShop(shopDomainOrName: string): void {
  const deny = (process.env.PROVISION_DENY_SHOPS || "k9supps,k9-supps,k9supp")
    .split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
  const v = shopDomainOrName.toLowerCase().replace(/[^a-z0-9]/g, "");
  for (const d of deny) {
    if (v.includes(d.replace(/[^a-z0-9]/g, ""))) {
      throw new Error(`Refusing to provision "${shopDomainOrName}": it matches the deny list (${d}). Strong Years must run on its own store.`);
    }
  }
}

export async function getAccessToken(shop: string, f: Fetch = fetch): Promise<string> {
  if (process.env.SHOPIFY_ADMIN_TOKEN) return process.env.SHOPIFY_ADMIN_TOKEN;
  const id = process.env.SHOPIFY_CLIENT_ID, secret = process.env.SHOPIFY_CLIENT_SECRET;
  if (!id || !secret) throw new Error("Set SHOPIFY_ADMIN_TOKEN, or SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (Dev Dashboard app installed on this store).");
  const res = await f(`https://${shop}/admin/oauth/access_token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "client_credentials", client_id: id, client_secret: secret }),
  });
  if (!res.ok) throw new Error(`Token exchange failed (${res.status}): ${await res.text()}`);
  const json = (await res.json()) as { access_token?: string };
  if (!json.access_token) throw new Error("Token exchange returned no access_token.");
  return json.access_token;
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export function liveRunner(shop: string, token: string, f: Fetch = fetch): GraphQLRunner {
  const recorded: RecordedOp[] = [];
  let seq = 0;
  return {
    dryRun: false,
    recorded,
    async run(step, op, variables = {}) {
      const query = OPS[op];
      recorded.push({ seq: ++seq, step, op, kind: query.trim().startsWith("mutation") ? "mutation" : "query", variables });
      for (let attempt = 1; attempt <= 6; attempt++) {
        const res = await f(`https://${shop}/admin/api/${API_VERSION}/graphql.json`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Shopify-Access-Token": token },
          body: JSON.stringify({ query, variables }),
        });
        if (res.status === 429 || res.status >= 500) { await sleep(500 * 2 ** attempt); continue; }
        const json = (await res.json()) as { data?: any; errors?: Array<{ message: string; extensions?: { code?: string } }> };
        if (json.errors?.some((e) => e.extensions?.code === "THROTTLED")) { await sleep(1000 * attempt); continue; }
        if (json.errors?.length) throw new Error(`${step} / ${op}: ${json.errors.map((e) => e.message).join("; ")}`);
        return json.data;
      }
      throw new Error(`${step} / ${op}: gave up after retries`);
    },
  };
}

/**
 * DRY_RUN: records and prints the operation, and answers with deterministic fake data so later steps
 * can be planned. Existence checks answer "not found", so the printed plan is the full first-run plan.
 */
export function dryRunner(print: (s: string) => void = (s) => process.stdout.write(s), opts: { simulateProvisioned?: boolean; engine?: "shopify_subscriptions" | "app"; simulateTrialPlan?: boolean } = {}): GraphQLRunner {
  const recorded: RecordedOp[] = [];
  let seq = 0;
  const fakeId = (type: string, key: string) => `gid://shopify/${type}/DRYRUN-${key}`;
  return {
    dryRun: true,
    recorded,
    async run(step: string, op: OpName, variables: Record<string, unknown> = {}): Promise<any> {
      const query = OPS[op];
      const kind = query.trim().startsWith("mutation") ? "mutation" : "query";
      recorded.push({ seq: ++seq, step, op, kind, variables });
      print(`\n# [${seq}] ${step}\n${query.trim()}\n# variables:\n${JSON.stringify(variables, null, 2)}\n`);
      const v = variables as any;
      switch (op) {
        case "ShopContext":
          return {
            shop: { id: "gid://shopify/Shop/DRYRUN", name: "Strong Years (dry run)", currencyCode: "USD", myshopifyDomain: "strong-years.myshopify.com", primaryDomain: { url: "https://strongyears.com", host: "strongyears.com" }, features: { eligibleForSubscriptions: true, sellsSubscriptions: false } },
            locations: { nodes: [{ id: "gid://shopify/Location/DRYRUN-1", name: "Primary", isActive: true }] },
            publications: { nodes: [{ id: "gid://shopify/Publication/DRYRUN-online-store", catalog: { title: "Online Store" } }] },
          };
        case "ProductByHandle": {
          if (!opts.simulateProvisioned) return { productByIdentifier: null };
          const spec = PRODUCTS.find((p) => p.handle === v.handle);
          if (!spec) return { productByIdentifier: null };
          const plans = !spec.subscriptionOnly ? [] : [{
            id: fakeId("SellingPlanGroup", spec.handle), name: "Strong Years", appId: opts.engine === "app" ? "strong-years-offers" : "shopify-subscriptions",
            sellingPlans: { nodes: [
              { id: fakeId("SellingPlan", `${spec.handle}-${spec.role === "annual" ? "yearly" : "monthly"}`), name: spec.role === "annual" ? "Yearly, renews until you cancel" : "Monthly, renews until you cancel", billingPolicy: { interval: spec.role === "annual" ? "YEAR" : "MONTH", intervalCount: 1 } },
              ...(opts.engine === "app" && spec.role === "founding" ? [{ id: fakeId("SellingPlan", "starter-b"), name: "$12 first month with the Starter Books, then $25 a month", billingPolicy: { interval: "MONTH", intervalCount: 1 } }] : []),
              // CANON UPDATE 6: the simulated store has the 7-day-trial plan on the two membership products (TRIAL_SIMULATED=0 to test the fallback).
              ...((spec.role === "founding" || spec.role === "standard") && opts.simulateTrialPlan !== false ? [{ id: fakeId("SellingPlan", `${spec.handle}-trial-7`), name: "7-day trial, then $25 a month", billingPolicy: { interval: "MONTH", intervalCount: 1 } }] : []),
            ] },
          }];
          return { productByIdentifier: {
            id: fakeId("Product", spec.handle), handle: spec.handle, status: spec.status, requiresSellingPlan: false,
            variants: { nodes: spec.variants.map((x, i) => ({ id: fakeId("ProductVariant", `${spec.handle}-${i + 1}`), title: x.option, price: x.price, sku: x.sku, inventoryItem: { id: fakeId("InventoryItem", `${spec.handle}-${i + 1}`), tracked: x.tracked }, inventoryQuantity: x.tracked ? x.initialQuantity ?? 0 : null })) },
            sellingPlanGroups: { nodes: plans },
          } };
        }
        case "CollectionByHandle": return { collectionByIdentifier: null };
        case "DiscountByCode": return { codeDiscountNodeByCode: opts.simulateProvisioned ? { id: fakeId("DiscountCodeNode", v.code) } : null };
        case "WebhookList": return { webhookSubscriptions: { nodes: [] } };
        case "PageByHandle": return { pages: { nodes: [] } };
        case "RedirectList": return { urlRedirects: { nodes: [] } };
        case "ProductUpsert": {
          const h = v.input.handle as string;
          return { productSet: { product: { id: fakeId("Product", h), handle: h, status: v.input.status, variants: { nodes: (v.input.variants || []).map((x: any, i: number) => ({ id: fakeId("ProductVariant", `${h}-${i + 1}`), title: x.optionValues?.[0]?.name, price: x.price, sku: x.sku, inventoryItem: { id: fakeId("InventoryItem", `${h}-${i + 1}`) } })) } }, userErrors: [] } };
        }
        case "CollectionCreate": return { collectionCreate: { collection: { id: fakeId("Collection", v.input.handle), handle: v.input.handle }, userErrors: [] } };
        case "SellingPlanGroupCreate": return { sellingPlanGroupCreate: { sellingPlanGroup: { id: fakeId("SellingPlanGroup", v.input.merchantCode), sellingPlans: { nodes: [] } }, userErrors: [] } };
        default: {
          // Generic mutation success shape: { <field>: { userErrors: [] } }
          const field = (query.match(/\{\s*\n?\s*(\w+)\s*\(/) || [])[1] || "result";
          return { [field]: { userErrors: [] } };
        }
      }
    },
  };
}
