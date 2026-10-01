import { defineConfig } from "@playwright/test";

/**
 * make prelaunch-local: screenshots + brand checks against an already-running prelaunch server
 * (deploy/scripts/prelaunch_local.sh starts it on a real, seeded Postgres). No webServer here on purpose.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: /prelaunch\.screens\.spec\.ts/,
  outputDir: "test-results/prelaunch",
  fullyParallel: false,
  workers: 1,
  timeout: 60_000,
  reporter: [["list"]],
  use: { baseURL: process.env.PRELAUNCH_BASE_URL ?? "http://localhost:3300" },
});
