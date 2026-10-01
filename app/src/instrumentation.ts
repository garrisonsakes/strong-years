/**
 * Round 9: boot-time config check. On a real deploy, missing or placeholder config
 * is logged loudly at startup; email stays blocked and /api/health returns 503
 * until it's fixed (lib/deployEnv.ts).
 */
export async function register() {
  const { deployConfigProblems, isDeployed } = await import("./lib/deployEnv");
  if (!isDeployed()) return;
  const { clientIpTrustConfigured } = await import("./lib/clientIp");
  if (!clientIpTrustConfigured()) {
    console.warn("[strong-years] No trusted proxy configured or detected: rate limits fall back to client-supplied addresses. Set TRUSTED_PROXY_HOPS, TRUSTED_PROXIES or CLIENT_IP_HEADER (see .env.example).");
  }
  if (!process.env.RATE_LIMIT_KV_URL) {
    console.warn("[strong-years] Rate limits are per instance. For more than one instance, set RATE_LIMIT_KV_URL/TOKEN (Upstash Redis REST).");
  }
  const problems = deployConfigProblems();
  if (problems.length) {
    console.error(`\n[strong-years] UNSAFE CONFIG, email is blocked and /api/health returns 503:\n  - ${problems.join("\n  - ")}\n`);
  }
}
