import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  esbuild: { jsx: "automatic" },
  test: {
    include: ["tests/unit/**/*.test.ts"],
    environment: "node",
    // The legacy suites exercise the Stripe path with checkout open. Shopify and
    // prelaunch suites set BILLING_PROVIDER / LAUNCH_MODE themselves (vi.stubEnv).
    env: { LAUNCH_MODE: "live", BILLING_PROVIDER: "stripe" },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      // Route handlers and server helpers import "server-only"; outside Next it's a no-op.
      "server-only": path.resolve(__dirname, "tests/stubs/server-only.ts"),
    },
  },
});
