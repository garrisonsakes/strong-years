import { defineConfig } from "@playwright/test";

const PORT = 3200;

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: /screens\.spec\.ts/,
  fullyParallel: false,
  workers: 1,
  timeout: 180_000,
  reporter: [["list"]],
  use: { baseURL: `http://localhost:${PORT}` },
  webServer: {
    command: `npx next start -p ${PORT}`,
    url: `http://localhost:${PORT}/start`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { ALLOW_MOCK_CHECKOUT_IN_PROD_BUILD: "true", LOCAL_DEMO_BUILD: "true", BILLING_PROVIDER: "stripe", LAUNCH_MODE: "live" },
  },
});
