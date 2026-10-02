/**
 * The provisioning plan. Pure orchestration over a GraphQLRunner, so the same code path runs live and in
 * DRY_RUN (the snapshot test records every operation it would send).
 *
 * Idempotency keys: products/collections by handle, discounts by code, webhooks by topic+uri, pages by
 * handle, redirects by path, metafield definitions by namespace+key (TAKEN = already there), selling plan
 * groups by merchantCode. Inventory is set ONLY when a tracked variant is first created: re-running never
 * resets the founding seat count.
 */
import {
  COLLECTIONS, DISCOUNTS, EBOOK_CELLS, HARDSHIP_POLICY, MARKETS, FOUNDING_CAP, FOUNDING_CLOSE_DATE_DEFAULT, FUNNEL_ARMS, TRIAL_DAYS,
  METAFIELD_DEFINITIONS, METAFIELD_NAMESPACE, PRODUCTS, REDIRECTS, SELLING_PLANS, STANDARD_PRICE,
  FOUNDING_PRICE, WEBHOOK_PATH, WEBHOOK_TOPICS_APP_ENGINE, WEBHOOK_TOPICS_CORE, type ProductSpec,
} from "../config/catalog.ts";
import { contentPages, shopPolicies, type LegalFacts } from "./legal.ts";
import type { GraphQLRunner } from "./client.ts";

export type Engine = "shopify_subscriptions" | "app";
export type Phase = "core" | "verify" | "close-founding";

export interface PlanOptions {
  engine: Engine;
  phase: Phase;
  membersAppUrl: string;
  facts: LegalFacts;
  foundingCloseDateIso: string;
  /** ISO timestamp used for discount startsAt (fixed in tests for stable snapshots). */
  nowIso: string;
  confirmCloseFounding?: boolean;
  /** ARM_TEST_ON=false shows every visitor the default arm (B) and default cell (e12). Default true: 50/50 B vs A. */
  armTestOn?: boolean;
  log?: (s: string) => void;
}

export interface MembersCatalogRow {
  sku: string; entitlement: string; title: string;
  shopify_product_id: string; shopify_variant_id: string; selling_plan_id: string | null; inventory_item_id: string | null;
  price_cents: number; recurring_cents: number | null; interval: "month" | "year" | null;
  includes_ebook: boolean; gift_months: number | null; cell: string | null; cohort: "founding" | "standard" | null; active: boolean;
  /** Storefront handle: the members app's /b and /join redirect to the PRODUCT PAGE (selling plans don't work with cart permalinks, shopify.dev "Create cart permalinks" → Limitations). */
  product_handle: string;
  /** CANON UPDATE 6: trial rows (t12). Null for everything else. */
  trial_days?: number | null;
  /** Cell B in the Shopify Subscriptions engine: the same (variant, plan) as founding_monthly, told apart by this discount code on the order. Null otherwise. */
  discount_code: string | null;
}

export interface PlanReport {
  /** Rows for the members app `shopify_products` table (app/src/lib/db/types.ts ShopifyProductRow). Verify phase only. */
  membersCatalog?: MembersCatalogRow[];
  created: string[];
  updated: string[];
  skipped: string[];
  manual: string[];
  warnings: string[];
  ids: Record<string, string>;
}

function errs(step: string, payload: any, okCodes: string[] = []): void {
  const ue = (payload?.userErrors || []) as Array<{ message: string; code?: string; field?: string[] }>;
  const bad = ue.filter((e) => !okCodes.includes(e.code || ""));
  if (bad.length) throw new Error(`${step}: ${bad.map((e) => `${(e.field || []).join(".")} ${e.message}`).join("; ")}`);
}

export async function runPlan(gql: GraphQLRunner, o: PlanOptions): Promise<PlanReport> {
  const log = o.log || (() => {});
  const r: PlanReport = { created: [], updated: [], skipped: [], manual: [], warnings: [], ids: {} };

  // ---------------------------------------------------------------- 0. context + guards
  const ctx = await gql.run<any>("Read shop context (currency, location, Online Store publication)", "ShopContext");
  const shop = ctx.shop;
  if (shop.currencyCode !== "USD") {
    const m = `Store currency is ${shop.currencyCode}; Strong Years launches in USD. Set Settings → General → Store currency = USD before any sale (can't be changed after the first order).`;
    if (!gql.dryRun) throw new Error(m); else r.warnings.push(m);
  }
  if (!shop.features?.eligibleForSubscriptions) r.warnings.push("Shop is not yet eligible for subscriptions (needs Shopify Payments activated and approved). Finish RUNBOOK step 3 first.");
  const location = (ctx.locations.nodes as any[]).find((l) => l.isActive) || ctx.locations.nodes[0];
  const onlineStore = (ctx.publications.nodes as any[]).find((p) => (p.catalog?.title || "").toLowerCase() === "online store");
  if (!onlineStore) r.warnings.push("Online Store publication not found: products can't be published to the storefront until the Online Store channel exists.");
  r.ids.shop = shop.id;
  r.ids.location = location?.id;

  if (o.phase === "verify") return verifyPhase(gql, o, r, onlineStore?.id);
  if (o.phase === "close-founding") return closeFoundingPhase(gql, o, r, onlineStore?.id);

  // ---------------------------------------------------------------- 1. metafield definitions
  for (const d of METAFIELD_DEFINITIONS) {
    const res = await gql.run<any>(`Metafield definition ${d.ownerType}.${METAFIELD_NAMESPACE}.${d.key}`, "MetafieldDefinitionCreate", {
      definition: {
        name: d.name, namespace: METAFIELD_NAMESPACE, key: d.key, type: d.type, ownerType: d.ownerType, description: d.description,
        access: { storefront: d.storefront },
      },
    });
    const p = res.metafieldDefinitionCreate;
    const taken = (p?.userErrors || []).some((e: any) => e.code === "TAKEN");
    errs(`metafield ${d.key}`, p, ["TAKEN"]);
    (taken ? r.skipped : r.created).push(`metafield-def:${d.ownerType}.${d.key}`);
  }

  // ---------------------------------------------------------------- 2. collections
  const collectionIds: Record<string, string> = {};
  for (const c of COLLECTIONS) {
    const found = await gql.run<any>(`Find collection ${c.handle}`, "CollectionByHandle", { handle: c.handle });
    const existing = found.collectionByIdentifier;
    if (existing) {
      const res = await gql.run<any>(`Update collection ${c.handle}`, "CollectionUpdate", { input: { id: existing.id, title: c.title, descriptionHtml: c.descriptionHtml } });
      errs(`collection ${c.handle}`, res.collectionUpdate);
      collectionIds[c.handle] = existing.id; r.updated.push(`collection:${c.handle}`);
    } else {
      const res = await gql.run<any>(`Create collection ${c.handle}`, "CollectionCreate", { input: { handle: c.handle, title: c.title, descriptionHtml: c.descriptionHtml } });
      errs(`collection ${c.handle}`, res.collectionCreate);
      collectionIds[c.handle] = res.collectionCreate.collection.id; r.created.push(`collection:${c.handle}`);
    }
    if (onlineStore) await gql.run(`Publish collection ${c.handle} to Online Store`, "PublishToOnlineStore", { id: collectionIds[c.handle], input: [{ publicationId: onlineStore.id }] });
  }

  // ---------------------------------------------------------------- 3. products
  const productIds: Record<string, string> = {};
  const variantIds: Record<string, string> = {};
  for (const p of PRODUCTS) {
    const found = await gql.run<any>(`Find product ${p.handle}`, "ProductByHandle", { handle: p.handle });
    const existing = found.productByIdentifier;
    const input = productSetInput(p, existing, collectionIds, location?.id);
    const res = await gql.run<any>(`${existing ? "Update" : "Create"} product ${p.handle} (${p.role}${p.cell ? `, cell ${p.cell}` : ""})`, "ProductUpsert", {
      input, identifier: { handle: p.handle },
    });
    errs(`product ${p.handle}`, res.productSet);
    const prod = res.productSet.product;
    productIds[p.handle] = prod.id;
    (prod.variants.nodes as any[]).forEach((v, i) => { variantIds[p.variants[i]?.sku || `${p.handle}-${i}`] = v.id; });
    (existing ? r.updated : r.created).push(`product:${p.handle}`);
    if (existing && p.variants.some((v) => v.tracked && v.initialQuantity !== undefined)) {
      r.skipped.push(`inventory:${p.handle} (exists; never reset by re-runs)`);
    }
    if (onlineStore && p.publishToOnlineStore && p.status !== "DRAFT") {
      await gql.run(`Publish ${p.handle} to Online Store`, "PublishToOnlineStore", { id: prod.id, input: [{ publicationId: onlineStore.id }] });
    }
    for (const file of p.digitalFiles || []) {
      r.manual.push(`Members app delivers ${file} for "${p.title}" (${p.handle}) as a watermarked download once orders/paid grants access; do NOT attach it in Digital Downloads (INTEGRATION.md: it cannot watermark).`);
    }
  }
  r.ids = { ...r.ids, ...Object.fromEntries(Object.entries(productIds).map(([k, v]) => [`product:${k}`, v])), ...Object.fromEntries(Object.entries(variantIds).map(([k, v]) => [`variant:${k}`, v])) };

  // ---------------------------------------------------------------- 4. selling plans
  if (o.engine === "app") {
    await createAppSellingPlans(gql, productIds, r);
  } else {
    r.manual.push(
      "Shopify Subscriptions → Plans → + Plan: \"Monthly, renews until you cancel\" (deliver every 1 month, no discount). Apply to: Strong Years Founding Membership, Strong Years Membership, Strong Years Essentials.",
      "Shopify Subscriptions → Plans → + Plan: \"Yearly, renews until you cancel\" (deliver every 1 year, no discount). Apply to: Strong Years Founding Annual.",
      "Then run: npm run verify (checks the plans, makes the membership products subscription-only).",
    );
  }

  // ---------------------------------------------------------------- 5. discounts
  for (const d of DISCOUNTS) {
    if (d.kind === "starter_first_payment" && o.engine === "app") { r.skipped.push(`discount:${d.code} (app engine uses the starter_b selling plan instead)`); continue; }
    const basic = discountInput(d, o.nowIso, productIds, collectionIds);
    const found = await gql.run<any>(`Find discount ${d.code}`, "DiscountByCode", { code: d.code });
    if (found.codeDiscountNodeByCode) {
      const res = await gql.run<any>(`Update discount ${d.code}`, "DiscountCodeUpdate", { id: found.codeDiscountNodeByCode.id, basicCodeDiscount: basic });
      errs(`discount ${d.code}`, res.discountCodeBasicUpdate); r.updated.push(`discount:${d.code}`);
    } else {
      const res = await gql.run<any>(`Create discount ${d.code} (${d.owner})`, "DiscountCodeCreate", { basicCodeDiscount: basic });
      errs(`discount ${d.code}`, res.discountCodeBasicCreate); r.created.push(`discount:${d.code}`);
    }
  }

  // ---------------------------------------------------------------- 5b. markets + hardship (MONETIZATION_ENGINE.md §3)
  for (const m of MARKETS) {
    if (m.handle === "us") continue;
    r.manual.push(`Settings → Markets → ${m.name} (${m.countries.join(", ")}): keep ${m.open ? "ACTIVE" : "INACTIVE until the Shopify Subscriptions multi-currency check and tax registration pass"}; currency ${m.currency}${m.priceAdjustmentPercent ? `; price list ${m.priceAdjustmentPercent}% on ONE-TIME products only (books, bumps, gifts), never the membership` : ""}. Then add the countries to open_countries in workers/dm/offer_routing.json (and the app copy).`);
  }
  r.manual.push(`Hardship requests: never a public code. A person issues a single-use ${HARDSHIP_POLICY.codePrefix}-<n> code per approved /ask/price request (${HARDSHIP_POLICY.options.map((o) => o.label).join(" or ")}, ${HARDSHIP_POLICY.options[0].cycles} cycles), within ${HARDSHIP_POLICY.reviewSla}, capped at ${HARDSHIP_POLICY.monthlyBudgetSeats} seats a month.`);
  r.manual.push("Settings → Payments → Shop Pay Installments: ON (US). It never applies to subscriptions or gift cards; it applies to the one-time prepaid 12 months ($249, DRAFT until the client decides) and to gifts.");

  // ---------------------------------------------------------------- 6. shop metafields (theme config)
  const shopMetafields = [
    { key: "cells", value: JSON.stringify({ ebook: EBOOK_CELLS, arms: FUNNEL_ARMS, test: o.armTestOn !== false, version: 2 }) },
    { key: "founding", value: JSON.stringify({ cap: FOUNDING_CAP, cap_label: FOUNDING_CAP.toLocaleString("en-US"), close_date: o.foundingCloseDateIso, price: FOUNDING_PRICE, standard_price: STANDARD_PRICE, count_line_threshold: 1000, few_left_threshold: 4900, closed: false }) },
    { key: "links", value: JSON.stringify({ members_url: o.membersAppUrl, support_email: o.facts.supportEmail, phone: o.facts.billingPhone, company: o.facts.companyLegalName, address: o.facts.mailingAddress, domain: o.facts.domain, sms_enabled: o.facts.smsEnabled, reviewer_signed: o.facts.reviewerSigned }) },
  ];
  const ms = await gql.run<any>("Set shop metafields (cells, founding, links)", "MetafieldsSet", {
    metafields: shopMetafields.map((m) => ({ ownerId: shop.id, namespace: METAFIELD_NAMESPACE, key: m.key, type: "json", value: m.value })),
  });
  errs("shop metafields", ms.metafieldsSet);

  // ---------------------------------------------------------------- 7. webhooks → members app
  const topics: string[] = [...WEBHOOK_TOPICS_CORE, ...(o.engine === "app" ? WEBHOOK_TOPICS_APP_ENGINE : [])];
  const uri = `${o.membersAppUrl.replace(/\/$/, "")}${WEBHOOK_PATH}`;
  const existingHooks = ((await gql.run<any>("List existing webhook subscriptions", "WebhookList")).webhookSubscriptions.nodes || []) as any[];
  for (const topic of topics) {
    const same = existingHooks.find((h) => h.topic === topic);
    if (same && same.uri === uri) { r.skipped.push(`webhook:${topic}`); continue; }
    if (same) {
      const res = await gql.run<any>(`Repoint webhook ${topic}`, "WebhookUpdate", { id: same.id, webhookSubscription: { uri } });
      errs(`webhook ${topic}`, res.webhookSubscriptionUpdate); r.updated.push(`webhook:${topic}`);
    } else {
      const res = await gql.run<any>(`Subscribe webhook ${topic} → members app`, "WebhookCreate", {
        topic,
        webhookSubscription: { uri, format: "JSON", ...(topic.startsWith("ORDERS_") ? { metafieldNamespaces: [METAFIELD_NAMESPACE] } : {}) },
      });
      errs(`webhook ${topic}`, res.webhookSubscriptionCreate); r.created.push(`webhook:${topic}`);
    }
  }
  if (o.engine === "shopify_subscriptions") {
    r.warnings.push("subscription_contracts/* and subscription_billing_attempts/* webhooks are NOT registered: they only fire for contracts owned by the subscribing app (read_own_subscription_contracts), and Shopify Subscriptions owns these contracts. The members app derives membership state from orders/paid (initial + every renewal order), refunds/create and orders/cancelled (config/webhook-topics.json is the contract).");
  }

  // ---------------------------------------------------------------- 8. pages + policies
  for (const pg of contentPages(o.facts)) {
    const found = await gql.run<any>(`Find page ${pg.handle}`, "PageByHandle", { query: `handle:${pg.handle}` });
    const existing = found.pages.nodes[0];
    if (existing) {
      const res = await gql.run<any>(`Update page ${pg.handle}`, "PageUpdate", { id: existing.id, page: { title: pg.title, body: pg.bodyHtml, templateSuffix: pg.templateSuffix, isPublished: true } });
      errs(`page ${pg.handle}`, res.pageUpdate); r.updated.push(`page:${pg.handle}`);
    } else {
      const res = await gql.run<any>(`Create page ${pg.handle}`, "PageCreate", { page: { handle: pg.handle, title: pg.title, body: pg.bodyHtml, templateSuffix: pg.templateSuffix, isPublished: true } });
      errs(`page ${pg.handle}`, res.pageCreate); r.created.push(`page:${pg.handle}`);
    }
  }
  for (const pol of shopPolicies(o.facts)) {
    const res = await gql.run<any>(`Set policy ${pol.type}`, "ShopPolicyUpdate", { shopPolicy: { type: pol.type, body: pol.body } });
    errs(`policy ${pol.type}`, res.shopPolicyUpdate); r.updated.push(`policy:${pol.type}`);
  }

  // ---------------------------------------------------------------- 9. redirects
  for (const rd of REDIRECTS) {
    const found = await gql.run<any>(`Find redirect ${rd.path}`, "RedirectList", { query: `path:${rd.path}` });
    const existing = (found.urlRedirects.nodes as any[]).find((n) => n.path === rd.path);
    if (existing && existing.target === rd.target) { r.skipped.push(`redirect:${rd.path}`); continue; }
    if (existing) {
      const res = await gql.run<any>(`Update redirect ${rd.path}`, "RedirectUpdate", { id: existing.id, urlRedirect: rd });
      errs(`redirect ${rd.path}`, res.urlRedirectUpdate); r.updated.push(`redirect:${rd.path}`);
    } else {
      const res = await gql.run<any>(`Create redirect ${rd.path} → ${rd.target}`, "RedirectCreate", { urlRedirect: rd });
      errs(`redirect ${rd.path}`, res.urlRedirectCreate); r.created.push(`redirect:${rd.path}`);
    }
  }

  log(`\nProvisioning ${gql.dryRun ? "plan (DRY RUN, nothing sent)" : "complete"}: ${r.created.length} created, ${r.updated.length} updated, ${r.skipped.length} unchanged.\n`);
  return r;
}

export function productSetInput(p: ProductSpec, existing: any, collectionIds: Record<string, string>, locationId?: string) {
  const existingBySku = new Map<string, any>(((existing?.variants?.nodes || []) as any[]).map((v) => [v.sku, v]));
  return {
    handle: p.handle,
    title: p.title,
    status: p.status,
    vendor: "Strong Years",
    productType: p.productType,
    tags: p.tags,
    templateSuffix: p.templateSuffix || null,
    descriptionHtml: p.descriptionHtml,
    seo: { title: p.seoTitle, description: p.seoDescription },
    collections: p.collections.map((h) => collectionIds[h]).filter(Boolean),
    metafields: [
      { namespace: METAFIELD_NAMESPACE, key: "role", type: "single_line_text_field", value: p.role },
      ...(p.cell ? [{ namespace: METAFIELD_NAMESPACE, key: "cell", type: "single_line_text_field", value: p.cell }] : []),
    ],
    productOptions: [{ name: p.optionName, values: p.variants.map((v) => ({ name: v.option })) }],
    variants: p.variants.map((v, i) => {
      const prior = existingBySku.get(v.sku);
      const firstCreate = !prior;
      return {
        ...(prior ? { id: prior.id } : {}),
        position: i + 1,
        optionValues: [{ optionName: p.optionName, name: v.option }],
        price: v.price,
        sku: v.sku,
        taxable: v.taxable,
        inventoryPolicy: v.inventoryPolicy,
        inventoryItem: {
          sku: v.sku,
          tracked: v.tracked,
          requiresShipping: v.requiresShipping,
          ...(v.weightLb ? { measurement: { weight: { value: v.weightLb, unit: "POUNDS" } } } : {}),
        },
        // Seats/stock are set once, at creation. Re-runs never touch them (no silent resets of the founding count).
        ...(firstCreate && v.tracked && v.initialQuantity !== undefined && locationId
          ? { inventoryQuantities: [{ locationId, name: "available", quantity: v.initialQuantity }] }
          : {}),
      };
    }),
  };
}

export function discountInput(d: (typeof DISCOUNTS)[number], nowIso: string, productIds: Record<string, string>, collectionIds: Record<string, string>) {
  const base = {
    title: d.title,
    code: d.code,
    startsAt: nowIso,
    appliesOncePerCustomer: d.oncePerCustomer,
    combinesWith: { orderDiscounts: false, productDiscounts: false, shippingDiscounts: true },
  };
  if (d.kind === "group_quantity") {
    // 20% off the gift product when the cart holds 5+ of it (DiscountMinimumRequirementInput.quantity).
    return {
      ...base,
      context: { all: "ALL" },
      minimumRequirement: { quantity: { greaterThanOrEqualToQuantity: String(d.minQuantity ?? 5) } },
      customerGets: {
        value: { percentage: d.percent ?? 0.2 },
        items: { products: { productsToAdd: [productIds[d.product || "gift-strong-years"]].filter(Boolean) } },
        appliesOnSubscription: false,
        appliesOnOneTimePurchase: true,
      },
    };
  }
  if (d.kind === "starter_first_payment" || d.kind === "winback_first_payment") {
    return {
      ...base,
      context: { all: "ALL" },
      customerGets: {
        value: { discountAmount: { amount: d.amount, appliesOnEachItem: false } },
        items: { products: { productsToAdd: [productIds[d.product || "founding-membership"]].filter(Boolean) } },
        appliesOnSubscription: true,
        appliesOnOneTimePurchase: false,
      },
      // First payment only (DiscountCodeBasicInput.recurringCycleLimit: "the number of billing cycles for which the
      // discount can be applied"): $12 today, then the plan's full price on every renewal.
      recurringCycleLimit: 1,
    };
  }
  return {
    ...base,
    context: { all: "ALL" },
    customerGets: {
      value: { discountAmount: { amount: d.amount, appliesOnEachItem: false } },
      items: { products: { productsToAdd: EBOOK_CELLS.map((c) => productIds[c.handle]).filter(Boolean) } },
      appliesOnSubscription: false,
      appliesOnOneTimePurchase: true,
    },
  };
}

async function createAppSellingPlans(gql: GraphQLRunner, productIds: Record<string, string>, r: PlanReport) {
  const groups = [
    { code: "sy-founding", name: "Founding membership", plans: ["monthly", "trial_7", "starter_b"], products: ["founding-membership"] },
    { code: "sy-monthly", name: "Membership", plans: ["monthly", "trial_7"], products: ["strong-years-membership", "essentials-membership", "coached-12-week", "coached-12-week-c97", "coached-12-week-c197"] },
    { code: "sy-yearly", name: "Yearly membership", plans: ["yearly"], products: ["founding-annual"] },
  ];
  for (const g of groups) {
    const firstProduct = g.products[0];
    const found = await gql.run<any>(`Check selling plan groups on ${firstProduct}`, "ProductByHandle", { handle: firstProduct });
    const has = (found.productByIdentifier?.sellingPlanGroups?.nodes || []).some((n: any) => n.name === g.name);
    if (has) { r.skipped.push(`selling-plan-group:${g.code}`); continue; }
    const plans = g.plans.map((k, i) => {
      const sp = SELLING_PLANS.find((s) => s.key === k)!;
      const pricingPolicies = sp.firstCyclePrice
        ? [
            { fixed: { adjustmentType: "PRICE", adjustmentValue: { fixedValue: sp.firstCyclePrice } } },
            { recurring: { afterCycle: 1, adjustmentType: "PRICE", adjustmentValue: { fixedValue: sp.recurringPrice } } },
          ]
        : [];
      return {
        name: sp.name,
        description: sp.description,
        options: [sp.name],
        position: i + 1,
        category: "SUBSCRIPTION",
        billingPolicy: { recurring: { interval: sp.interval, intervalCount: sp.intervalCount } },
        deliveryPolicy: { recurring: { interval: sp.interval, intervalCount: sp.intervalCount } },
        pricingPolicies,
      };
    });
    const res = await gql.run<any>(`Create selling plan group ${g.code} (app-owned)`, "SellingPlanGroupCreate", {
      input: { name: g.name, merchantCode: g.code, options: ["Plan"], position: 1, sellingPlansToCreate: plans },
      resources: { productIds: g.products.map((h) => productIds[h]).filter(Boolean) },
    });
    errs(`selling plan group ${g.code}`, res.sellingPlanGroupCreate);
    r.created.push(`selling-plan-group:${g.code}`);
  }
  for (const h of ["founding-membership", "strong-years-membership", "essentials-membership", "founding-annual"]) {
    const res = await gql.run<any>(`Make ${h} subscription-only`, "ProductUpdate", { product: { id: productIds[h], requiresSellingPlan: true } });
    errs(`requiresSellingPlan ${h}`, res.productUpdate);
  }
  r.warnings.push("App engine: the Strong Years app owns these contracts and MUST run billing (subscriptionBillingAttemptCreate on schedule), update the starter_b contract price to $25 after cycle 1, and handle dunning. That scheduler is not part of this package.");
  r.warnings.push(`App engine, canon 6 trial_7: the plan's first cycle is $0 (pricing policy); on subscription_contracts/create the app must call subscriptionContractSetNextBillingDate(contract, checkout + ${TRIAL_DAYS} days) and bill on that date (subscriptionBillingAttemptCreate); the plan's recurring price applies from cycle 2. Without that scheduler use a trial-capable subscription app instead (INTEGRATION.md §9).`);
}

const num = (gid: string | null | undefined) => (gid ? String(gid).split("/").pop()! : null);
const cents = (money: string) => Math.round(Number(money) * 100);

async function verifyPhase(gql: GraphQLRunner, o: PlanOptions, r: PlanReport, onlineStoreId?: string): Promise<PlanReport> {
  const rows: MembersCatalogRow[] = [];
  for (const p of PRODUCTS) {
    const found = await gql.run<any>(`Verify ${p.handle}${p.subscriptionOnly ? " (selling plans)" : ""}`, "ProductByHandle", { handle: p.handle });
    const prod = found.productByIdentifier;
    if (!prod) { r.warnings.push(`${p.handle}: product missing; run the core phase first.`); continue; }
    const variants = prod.variants.nodes as any[];
    let planId: string | null = null, starterPlanId: string | null = null, trialPlanId: string | null = null;
    if (p.subscriptionOnly) {
      const wanted = p.role === "annual" ? "YEAR" : "MONTH";
      const plans = (prod.sellingPlanGroups.nodes as any[]).flatMap((g) => g.sellingPlans.nodes as any[]);
      const match = plans.find((s) => s.billingPolicy?.interval === wanted && s.billingPolicy?.intervalCount === 1 && !/first month|trial/i.test(s.name));
      starterPlanId = plans.find((s) => /first month/i.test(s.name))?.id ?? null;
      // CANON UPDATE 6: the 7-day-trial plan (trial-capable app or the app engine). Absent → no t12 rows → the members
      // app and the theme serve cell B; the warning says what to create.
      trialPlanId = plans.find((s) => /7[- ]day trial/i.test(s.name))?.id ?? null;
      if ((p.role === "founding" || p.role === "standard") && !trialPlanId) r.warnings.push(`${p.handle}: no "7-day trial" selling plan attached (CANON UPDATE 6). Create it in a trial-capable subscription app (INTEGRATION.md §9); until then visitors get cell B (STARTER12).`);
      if (!match) { r.warnings.push(`${p.handle}: no ${wanted === "YEAR" ? "yearly" : "monthly"} selling plan attached yet (Shopify Subscriptions → Plans).`); continue; }
      planId = match.id;
      r.ids[`selling-plan:${p.handle}`] = match.id;
      if (!prod.requiresSellingPlan) {
        const res = await gql.run<any>(`Make ${p.handle} subscription-only`, "ProductUpdate", { product: { id: prod.id, requiresSellingPlan: true } });
        errs(`requiresSellingPlan ${p.handle}`, res.productUpdate);
        r.updated.push(`subscription-only:${p.handle}`);
      } else r.skipped.push(`subscription-only:${p.handle}`);
      if (p.role === "founding" && variants[0]?.inventoryQuantity != null) r.ids["founding:seats_taken"] = String(FOUNDING_CAP - variants[0].inventoryQuantity);
    }
    p.variants.forEach((spec, i) => {
      const v = variants.find((x) => x.sku === spec.sku) || variants[i];
      if (!v) return;
      const base = { title: p.title, shopify_product_id: num(prod.id)!, shopify_variant_id: num(v.id)!, inventory_item_id: spec.tracked ? num(v.inventoryItem?.id) : null, price_cents: cents(spec.price), active: p.status !== "DRAFT" || p.role === "standard", product_handle: p.handle, discount_code: null as string | null };
      const recurring = p.subscriptionOnly ? cents(spec.price) : null;
      const interval: "month" | "year" | null = p.subscriptionOnly ? (p.role === "annual" ? "year" : "month") : null;
      const mk = (x: Partial<MembersCatalogRow> & Pick<MembersCatalogRow, "sku" | "entitlement">): MembersCatalogRow => ({
        selling_plan_id: num(planId), recurring_cents: recurring, interval, includes_ebook: false, gift_months: null, cell: null, cohort: null, ...base, ...x,
      });
      switch (p.role) {
        case "ebook": rows.push(mk({ sku: `ebook_${p.cell}`, entitlement: "ebook", includes_ebook: true, cell: p.cell! })); break;
        case "founding":
          rows.push(mk({ sku: "founding_monthly", entitlement: "founding", cohort: "founding" }));
          // Cell B (launch default, CANON UPDATE 3). Shopify Subscriptions engine: the SAME variant + monthly plan as
          // founding_monthly plus the STARTER12 first-payment-only discount ($13 off cycle 1 → $12 today, then $25/mo);
          // the members app tells the two rows apart by the discount code on the order (matchLine). App engine: its own
          // selling plan with a fixed first-cycle price, no code.
          rows.push(starterPlanId
            ? mk({ sku: "bundle_m12", entitlement: "founding", selling_plan_id: num(starterPlanId), price_cents: 1200, includes_ebook: true, cell: "m12", cohort: "founding" })
            : mk({ sku: "bundle_m12", entitlement: "founding", price_cents: 1200, includes_ebook: true, cell: "m12", cohort: "founding", discount_code: "STARTER12" }));
          // CANON UPDATE 6 (the launch offer): founding variant on the 7-day-trial plan, $0 membership line at checkout
          // (the $12 Starter Books are the ebook_e12 line on the same order), first $25 on day 7 as a renewal order.
          if (trialPlanId) rows.push(mk({ sku: "bundle_t12", entitlement: "founding", selling_plan_id: num(trialPlanId), price_cents: 0, cell: "t12", cohort: "founding", trial_days: TRIAL_DAYS }));
          break;
        case "standard":
          rows.push(mk({ sku: "standard_monthly", entitlement: "standard", cohort: "standard" }));
          // Cell B after the founding group closes: $12 today (books + first month), then the $35 standard price.
          if (!starterPlanId) rows.push(mk({ sku: "bundle_m12_standard", entitlement: "standard", price_cents: 1200, includes_ebook: true, cell: "m12", cohort: "standard", discount_code: "STARTER12S" }));
          if (trialPlanId) rows.push(mk({ sku: "bundle_t12_standard", entitlement: "standard", selling_plan_id: num(trialPlanId), price_cents: 0, cell: "t12", cohort: "standard", trial_days: TRIAL_DAYS }));
          break;
        case "essentials": rows.push(mk({ sku: "essentials_monthly", entitlement: "essentials" })); break;
        case "annual": rows.push(mk({ sku: "annual_founding", entitlement: "annual" })); break;
        case "gift": rows.push(mk({ sku: spec.sku.endsWith("12M") ? "gift12" : "gift3", entitlement: "gift", gift_months: spec.sku.endsWith("12M") ? 12 : 3 })); break;
        case "bump_wallplan": rows.push(mk({ sku: "wallplan", entitlement: "bump" })); break;
        case "bump_kit": rows.push(mk({ sku: "kit", entitlement: "bump" })); break;
        // R3 coached cells (ASCENSION.md): c147 is the default row; c97 / c197 are the price-test rows.
        case "coached": rows.push(mk({ sku: p.cell === "c147" ? "coached_monthly" : `coached_${p.cell!.slice(1)}`, entitlement: "coached", cell: p.cell! })); break;
      }
    });
  }
  r.membersCatalog = rows;
  for (const code of ["STARTER12", "STARTER12S"]) {
    const starter = await gql.run<any>(`Verify ${code} discount exists`, "DiscountByCode", { code });
    if (o.engine === "shopify_subscriptions" && !starter.codeDiscountNodeByCode) r.warnings.push(`${code} missing: re-run the core phase.`);
  }
  void onlineStoreId;
  return r;
}

async function closeFoundingPhase(gql: GraphQLRunner, o: PlanOptions, r: PlanReport, onlineStoreId?: string): Promise<PlanReport> {
  if (!o.confirmCloseFounding) throw new Error("close-founding is one-way (the founding group is never reopened). Re-run with --yes-close-founding.");
  const f = (await gql.run<any>("Read founding product", "ProductByHandle", { handle: "founding-membership" })).productByIdentifier;
  const s = (await gql.run<any>("Read standard product", "ProductByHandle", { handle: "strong-years-membership" })).productByIdentifier;
  if (!f || !s) throw new Error("Products missing; run core phase first.");
  // 1) Renewals of existing founding members must never fail on "out of stock": allow overselling the variant.
  const pol = await gql.run<any>("Founding variant: inventoryPolicy CONTINUE so renewals never fail", "VariantInventoryPolicy", {
    productId: f.id, variants: [{ id: f.variants.nodes[0].id, inventoryPolicy: "CONTINUE" }],
  });
  errs("founding inventory policy", pol.productVariantsBulkUpdate);
  // 2) New buyers can't add it any more.
  if (onlineStoreId) await gql.run("Unpublish founding product from Online Store (existing contracts keep billing)", "UnpublishFromOnlineStore", { id: f.id, input: [{ publicationId: onlineStoreId }] });
  // 3) Standard $35 goes live.
  const up = await gql.run<any>("Activate standard membership", "ProductUpdate", { product: { id: s.id, status: "ACTIVE" } });
  errs("standard activate", up.productUpdate);
  if (onlineStoreId) await gql.run("Publish standard membership", "PublishToOnlineStore", { id: s.id, input: [{ publicationId: onlineStoreId }] });
  const ms = await gql.run<any>("Mark founding group closed (theme switches every CTA to standard)", "MetafieldsSet", {
    metafields: [{ ownerId: r.ids.shop, namespace: METAFIELD_NAMESPACE, key: "founding", type: "json", value: JSON.stringify({ cap: FOUNDING_CAP, cap_label: FOUNDING_CAP.toLocaleString("en-US"), close_date: o.foundingCloseDateIso, price: FOUNDING_PRICE, standard_price: STANDARD_PRICE, count_line_threshold: 1000, few_left_threshold: 4900, closed: true }) }],
  });
  errs("founding metafield", ms.metafieldsSet);
  r.updated.push("founding:closed");
  return r;
}

export function defaultCloseDate(): string {
  return process.env.FOUNDING_CLOSE_DATE || FOUNDING_CLOSE_DATE_DEFAULT;
}
