import { defineConfig, devices } from "@playwright/test";

const PORT = 3100;
/** Second server: the launch path (Shopify billing, prelaunch at boot). */
export const SHOP_PORT = 3101;
export const MAIL_SINK = "test-results/mail-sink";

const base = { SESSION_SECRET: "e2e-session-secret-0123456789abcdef", CRON_SECRET: "e2e-cron", ALLOW_MOCK_CHECKOUT_IN_PROD_BUILD: "true", LOCAL_DEMO_BUILD: "true" };

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: /(smoke|shopify)\.spec\.ts/,
  fullyParallel: false,
  workers: 1,
  timeout: 90_000,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${PORT}`, trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      // The original in-app (Stripe simulator) funnel, checkout open: kept behind the adapter.
      command: `npx next start -p ${PORT}`,
      url: `http://localhost:${PORT}/start`,
      reuseExistingServer: false,
      timeout: 120_000,
      env: { ...base, BILLING_PROVIDER: "stripe", LAUNCH_MODE: "live" },
    },
    {
      command: `npx next start -p ${SHOP_PORT}`,
      url: `http://localhost:${SHOP_PORT}/waitlist`,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        ...base,
        BILLING_PROVIDER: "shopify",
        LAUNCH_MODE: "prelaunch",
        SHOPIFY_STORE_DOMAIN: "strongyears-demo.myshopify.com",
        SHOPIFY_CUSTOMER_ACCOUNT_URL: "https://shopify.com/00000/account",
        SHOPIFY_WEBHOOK_SECRET: "e2e-shopify-webhook-secret-0123456789",
        WAITLIST_MIN_FILL_MS: "0",
        DEV_MAIL_SINK_DIR: MAIL_SINK,
        NEXT_PUBLIC_SITE_URL: `http://localhost:${SHOP_PORT}`,
      },
    },
  ],
});
