#!/usr/bin/env node
/**
 * npm run provision            → DRY_RUN (default): prints every GraphQL operation, sends nothing
 * DRY_RUN=false npm run provision   → live, against SHOPIFY_STORE (requires CONFIRM_STORE=<same domain>)
 * npm run verify               → after the Shopify Subscriptions plans exist
 * node src/provision.ts --phase=close-founding --yes-close-founding   → one-way switch to the $35 standard price
 *
 * Env: SHOPIFY_STORE (xxx.myshopify.com), SHOPIFY_ADMIN_TOKEN or SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET,
 * MEMBERS_APP_URL, SY_DOMAIN, COMPANY_LEGAL_NAME, MAILING_ADDRESS, SUPPORT_EMAIL, BILLING_PHONE,
 * GOVERNING_STATE, FOUNDING_CLOSE_DATE (YYYY-MM-DD), SUBSCRIPTION_ENGINE (shopify_subscriptions|app),
 * SMS_ENABLED, REVIEWER_SIGNED, KIT_SHIP_DAYS. See RUNBOOK.md.
 */
import { assertNotForbiddenShop, dryRunner, getAccessToken, liveRunner, API_VERSION } from "./client.ts";
import { runPlan, defaultCloseDate, type Engine, type Phase } from "./plan.ts";
import { PLACEHOLDER_RE, type LegalFacts } from "./legal.ts";
import { FOUNDING_CAP } from "../config/catalog.ts";
import { mkdirSync, writeFileSync } from "node:fs";

function arg(name: string): string | undefined {
  const hit = process.argv.find((a) => a === `--${name}` || a.startsWith(`--${name}=`));
  if (!hit) return undefined;
  return hit.includes("=") ? hit.split("=").slice(1).join("=") : "true";
}

export function factsFromEnv(env: NodeJS.ProcessEnv = process.env): LegalFacts {
  const ph = (k: string) => env[k] || `{{${k}}}`;
  const close = env.FOUNDING_CLOSE_DATE || defaultCloseDate();
  const closeHuman = new Date(`${close}T12:00:00Z`).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" });
  return {
    brand: "Strong Years",
    companyLegalName: ph("COMPANY_LEGAL_NAME"),
    mailingAddress: ph("MAILING_ADDRESS"),
    supportEmail: ph("SUPPORT_EMAIL"),
    billingPhone: ph("BILLING_PHONE"),
    domain: env.SY_DOMAIN || "strongyears.com",
    membersUrl: env.MEMBERS_APP_URL || `https://members.${env.SY_DOMAIN || "strongyears.com"}`,
    foundingCloseDate: closeHuman,
    foundingCap: FOUNDING_CAP,
    foundingPrice: "$25",
    standardPrice: "$35",
    annualPrice: "$249",
    essentialsPrice: "$12",
    governingState: ph("GOVERNING_STATE"),
    kitShipDays: env.KIT_SHIP_DAYS || "2 business days",
    smsEnabled: env.SMS_ENABLED === "true",
    reviewerSigned: env.REVIEWER_SIGNED === "true",
    effectiveDate: env.LEGAL_EFFECTIVE_DATE || new Date().toISOString().slice(0, 10),
  };
}

async function main() {
  const dry = (process.env.DRY_RUN ?? "true") !== "false";
  const phase = (arg("phase") || "core") as Phase;
  const engine = (process.env.SUBSCRIPTION_ENGINE || "shopify_subscriptions") as Engine;
  const facts = factsFromEnv();
  const membersAppUrl = facts.membersUrl;

  if (!dry) {
    const shop = process.env.SHOPIFY_STORE;
    if (!shop || !/^[a-z0-9-]+\.myshopify\.com$/.test(shop)) throw new Error("SHOPIFY_STORE must be the store's xxx.myshopify.com domain.");
    assertNotForbiddenShop(shop);
    if (process.env.CONFIRM_STORE !== shop) throw new Error(`Live run blocked: set CONFIRM_STORE=${shop} to confirm the target store.`);
    const unresolved = JSON.stringify(facts).match(PLACEHOLDER_RE);
    if (unresolved) throw new Error(`Live run blocked: legal facts missing ${[...new Set(unresolved)].join(", ")} (they appear in the policies).`);
    if (!/^https:\/\//.test(membersAppUrl)) throw new Error("MEMBERS_APP_URL must be https (webhooks).");
  }

  const gql = dry ? dryRunner(undefined, { simulateProvisioned: phase !== "core", engine }) : liveRunner(process.env.SHOPIFY_STORE!, await getAccessToken(process.env.SHOPIFY_STORE!));
  console.log(`Strong Years provisioning · Admin API ${API_VERSION} · phase=${phase} · engine=${engine} · ${dry ? "DRY RUN (nothing is sent)" : `LIVE on ${process.env.SHOPIFY_STORE}`}`);

  if (!dry) {
    // Double-check by name too, after auth, before any write.
    const ctx = await gql.run<any>("Guard: confirm shop identity", "ShopContext");
    assertNotForbiddenShop(ctx.shop.name);
    assertNotForbiddenShop(ctx.shop.myshopifyDomain);
  }

  const report = await runPlan(gql, {
    engine, phase, membersAppUrl, facts,
    foundingCloseDateIso: process.env.FOUNDING_CLOSE_DATE || defaultCloseDate(),
    nowIso: new Date().toISOString(),
    confirmCloseFounding: arg("yes-close-founding") === "true",
    armTestOn: (process.env.ARM_TEST_ON || "true") !== "false",
    log: (s) => console.log(s),
  });

  const ops = gql.recorded.length, muts = gql.recorded.filter((x) => x.kind === "mutation").length;
  console.log(`\n${ops} operations (${muts} mutations).`);
  if (report.created.length) console.log(`Created: ${report.created.join(", ")}`);
  if (report.updated.length) console.log(`Updated: ${report.updated.join(", ")}`);
  if (report.skipped.length) console.log(`Unchanged: ${report.skipped.join(", ")}`);
  if (report.warnings.length) console.log(`\nWARNINGS:\n- ${report.warnings.join("\n- ")}`);
  if (report.manual.length) console.log(`\nMANUAL STEPS (RUNBOOK.md):\n- ${report.manual.join("\n- ")}`);
  if (report.membersCatalog) {
    const dir = new URL("../out/", import.meta.url);
    mkdirSync(dir, { recursive: true });
    const file = new URL(`members-catalog.${dry ? "dryrun" : process.env.SHOPIFY_STORE}.json`, dir);
    writeFileSync(file, JSON.stringify(report.membersCatalog, null, 2));
    console.log(`\nMembers app catalog (${report.membersCatalog.length} rows for the shopify_products table): ${file.pathname}`);
  }
}

const isMain = process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href;
if (isMain) {
  main().catch((e) => { console.error(`\nERROR: ${e.message}`); process.exit(1); });
}
