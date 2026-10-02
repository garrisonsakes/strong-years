/**
 * Scheduled webhook self-heal (src/webhookHeal.ts). Dry run by default; live needs the same guards as
 * provisioning: DRY_RUN=false, SHOPIFY_STORE=xxx.myshopify.com, CONFIRM_STORE=<same>, MEMBERS_APP_URL=https://...
 * Exit code 2 when a topic had to be re-created or repointed, so the scheduler can alert and the
 * members app can reconcile orders since its last received delivery.
 */
import { assertNotForbiddenShop, dryRunner, getAccessToken, liveRunner } from "../src/client.ts";
import { ensureWebhooks } from "../src/webhookHeal.ts";
import type { Engine } from "../src/plan.ts";

async function main() {
  const dry = (process.env.DRY_RUN ?? "true") !== "false";
  const engine = (process.env.SUBSCRIPTION_ENGINE || "shopify_subscriptions") as Engine;
  const membersAppUrl = process.env.MEMBERS_APP_URL || "https://members.strongyears.com";
  const shop = process.env.SHOPIFY_STORE || "";
  if (!dry) {
    if (!/^[a-z0-9-]+\.myshopify\.com$/.test(shop)) throw new Error("SHOPIFY_STORE must be the store's xxx.myshopify.com domain.");
    assertNotForbiddenShop(shop);
    if (process.env.CONFIRM_STORE !== shop) throw new Error(`Live run blocked: set CONFIRM_STORE=${shop} to confirm the target store.`);
    if (!/^https:\/\//.test(membersAppUrl)) throw new Error("MEMBERS_APP_URL must be https (webhooks).");
  }
  const gql = dry ? dryRunner(() => {}, { engine }) : liveRunner(shop, await getAccessToken(shop));
  if (!dry) {
    const ctx = await gql.run<any>("Guard: confirm shop identity", "ShopContext");
    assertNotForbiddenShop(ctx.shop.name);
    assertNotForbiddenShop(ctx.shop.myshopifyDomain);
  }
  const r = await ensureWebhooks(gql, { engine, membersAppUrl });
  const healed = [...r.created, ...r.updated];
  console.log(JSON.stringify({ at: new Date().toISOString(), dry_run: dry, healed, unchanged: r.skipped.length, duplicates: r.duplicates }));
  if (healed.length && !dry) {
    console.error(`HEALED ${healed.length} webhook subscription(s). Deliveries were lost while they were missing: reconcile orders since the last received webhook.`);
    process.exitCode = 2;
  }
}

main().catch((e) => { console.error(e instanceof Error ? e.message : e); process.exit(1); });
