/**
 * Round 9, conditions 2 and 3 (+ ADMIN_USER):
 *  - a real deploy with missing/placeholder email config never sends email and
 *    fails /api/health loudly;
 *  - rate limits key on the trusted-proxy client IP on any host, never one shared bucket;
 *  - ADMIN_USER has no default outside local dev.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { deployConfigProblems, emailConfigProblems, isDeployed } from "@/lib/deployEnv";
import { rateLimitKey, trustConfigFromEnv, trustedClientIp } from "@/lib/clientIp";
import { LIMITS, clientIp, hit, resetRateLimits } from "@/lib/rateLimit";

const penv = process.env as Record<string, string | undefined>;
const saved = { ...process.env };
let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  resetRateLimits();
  for (const k of ["VERCEL", "VERCEL_ENV", "LOCAL_DEMO_BUILD", "ALLOW_RULES_ONLY_CHAT", "RENDER", "FLY_APP_NAME", "NETLIFY", "TRUST_CLOUDFLARE", "CLIENT_IP_HEADER", "TRUSTED_PROXY_HOPS", "TRUSTED_PROXIES", "RAILWAY_ENVIRONMENT", "DYNO", "K_SERVICE", "RESEND_API_KEY", "POSTMARK_SERVER_TOKEN"]) delete penv[k];
});
afterEach(() => {
  vi.unstubAllGlobals();
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

const GOOD = {
  NEXT_PUBLIC_SITE_URL: "https://strongyears.com",
  MAILING_ADDRESS: "Strong Years LLC, 100 Main St, Suite 2, Los Angeles, CA 90012",
  EMAIL_FROM: "hello@strongyears.com",
  SUPPORT_EMAIL: "help@strongyears.com",
};
function deploy(vars: Record<string, string | undefined>) {
  penv.NODE_ENV = "production";
  for (const k of ["NEXT_PUBLIC_SITE_URL", "MAILING_ADDRESS", "EMAIL_FROM", "SUPPORT_EMAIL"]) delete penv[k];
  for (const [k, v] of Object.entries(vars)) if (v === undefined) delete penv[k];
  else penv[k] = v;
}

describe("R9: what counts as a deploy", () => {
  it.each([
    [{ NODE_ENV: "production" }, true],
    [{ NODE_ENV: "production", LOCAL_DEMO_BUILD: "true" }, false],
    [{ NODE_ENV: "production", LOCAL_DEMO_BUILD: "true", VERCEL_ENV: "production" }, true],
    [{ NODE_ENV: "production", LOCAL_DEMO_BUILD: "true", SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "k" }, true],
    [{ NODE_ENV: undefined }, true],
    [{ NODE_ENV: "development" }, false],
  ])("R9 isDeployed(%j) = %s", (e, expected) => {
    expect(isDeployed(e)).toBe(expected);
  });
});

describe("R9: unsafe email config", () => {
  it.each([
    ["MAILING_ADDRESS unset", { ...GOOD, MAILING_ADDRESS: undefined }, /MAILING_ADDRESS: missing/],
    ["MAILING_ADDRESS placeholder", { ...GOOD, MAILING_ADDRESS: "[Company mailing address — set MAILING_ADDRESS]" }, /MAILING_ADDRESS: placeholder/],
    ["site URL unset", { ...GOOD, NEXT_PUBLIC_SITE_URL: undefined }, /NEXT_PUBLIC_SITE_URL: missing/],
    ["site URL localhost", { ...GOOD, NEXT_PUBLIC_SITE_URL: "http://localhost:3000" }, /NEXT_PUBLIC_SITE_URL: must be https/],
    ["site URL https localhost", { ...GOOD, NEXT_PUBLIC_SITE_URL: "https://127.0.0.1" }, /local host/],
    ["sender placeholder", { ...GOOD, EMAIL_FROM: "hello@strongyears.example" }, /EMAIL_FROM: placeholder/],
  ])("R9 email config: %s is caught", (_n, vars, re) => {
    expect(emailConfigProblems(vars).join("; ")).toMatch(re);
  });

  it("R9 email config: a complete config passes", () => {
    expect(emailConfigProblems(GOOD)).toEqual([]);
  });

  it("R9: on a deploy with MAILING_ADDRESS unset, email is refused (never handed to the provider)", async () => {
    deploy({ ...GOOD, MAILING_ADDRESS: undefined, RESEND_API_KEY: "re_test_placeholder" });
    const fetchSpy = vi.fn(async () => new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchSpy);
    const err = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const { sendEmail } = await import("@/lib/notify");
    const row = await sendEmail({ to: "a@b.co", subject: "Hi", text: "Hello", template: "t" });
    expect(row.status).toBe("failed");
    expect(row.provider).toBe("blocked_config");
    expect(fetchSpy).not.toHaveBeenCalled();
    err.mockRestore();
  });

  it("R9: on a deploy with localhost links, email is refused", async () => {
    deploy({ ...GOOD, NEXT_PUBLIC_SITE_URL: "http://localhost:3000", RESEND_API_KEY: "re_test_placeholder" });
    const fetchSpy = vi.fn(async () => new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchSpy);
    vi.spyOn(console, "error").mockImplementation(() => undefined);
    const { sendEmail } = await import("@/lib/notify");
    expect((await sendEmail({ to: "a@b.co", subject: "Hi", text: "Hello", template: "t" })).provider).toBe("blocked_config");
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("R9: with the full config, the same deploy sends, and the footer has the real address and https links", async () => {
    deploy({ ...GOOD, RESEND_API_KEY: "re_test_placeholder" });
    const fetchSpy = vi.fn(async (_u: string, _i: { body: string }) => new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchSpy);
    const { sendEmail } = await import("@/lib/notify");
    const row = await sendEmail({ to: "a@b.co", subject: "Hi", text: "Hello", template: "t" });
    expect(row.provider).toBe("resend");
    expect(fetchSpy).toHaveBeenCalledOnce();
    const body = JSON.parse(fetchSpy.mock.calls[0]![1].body) as { text: string };
    expect(body.text).toContain("https://strongyears.com/app/account");
    expect(body.text).toContain("100 Main St");
  });

  it("R9: local dev and the in-memory demo keep stubbing email as before", async () => {
    penv.NODE_ENV = "test";
    const { sendEmail } = await import("@/lib/notify");
    expect((await sendEmail({ to: "a@b.co", subject: "Hi", text: "Hello", template: "t" })).status).toBe("stubbed");
  });

  it("R9 health: 503 on a deploy with bad config; names only with the cron secret, never values", async () => {
    deploy({ ...GOOD, MAILING_ADDRESS: undefined, SESSION_SECRET: "s".repeat(40), CRON_SECRET: "cron-secret-value", ADMIN_USER: "owner", ADMIN_PASSWORD: "pw-value-123" });
    const { GET } = await import("@/app/api/health/route");
    const anon = await GET(new Request("http://x/api/health"));
    expect(anon.status).toBe(503);
    expect((await anon.json()).problems).toBe(1);
    const authed = await GET(new Request("http://x/api/health", { headers: { authorization: "Bearer cron-secret-value" } }));
    const j = (await authed.json()) as { problems: string[] };
    expect(j.problems).toEqual(["MAILING_ADDRESS: missing"]);
    expect(JSON.stringify(j)).not.toContain("pw-value-123");
  });

  it("R9 health: 200 when everything is set; ADMIN_USER missing fails it", async () => {
    deploy({ ...GOOD, SESSION_SECRET: "s".repeat(40), CRON_SECRET: "c", ADMIN_USER: "owner", ADMIN_PASSWORD: "pw" });
    const { GET } = await import("@/app/api/health/route");
    expect((await GET(new Request("http://x/api/health"))).status).toBe(200);
    delete penv.ADMIN_USER;
    expect(deployConfigProblems()).toContain("ADMIN_USER: missing");
    expect((await GET(new Request("http://x/api/health"))).status).toBe(503);
  });
});

describe("R9: rate-limit key on any host", () => {
  const h = (o: Record<string, string>) => new Headers(o);
  it("R9: unconfigured host → visitors do NOT share one bucket", async () => {
    const a = new Request("http://x/api/leads", { headers: { "x-forwarded-for": "198.51.100.1" } });
    const b = new Request("http://x/api/leads", { headers: { "x-forwarded-for": "198.51.100.2" } });
    expect(clientIp(a)).not.toBe(clientIp(b));
    for (let i = 0; i < LIMITS.checkoutPerIp.max; i++) expect(await hit(`checkout:ip:${clientIp(a)}`, LIMITS.checkoutPerIp)).toBe(true);
    expect(await hit(`checkout:ip:${clientIp(a)}`, LIMITS.checkoutPerIp)).toBe(false);
    expect(await hit(`checkout:ip:${clientIp(b)}`, LIMITS.checkoutPerIp)).toBe(true);
  });
  it("R9: platform detection: Render/Railway/Heroku (one hop), Fly, Netlify, Cloudflare, Vercel", () => {
    expect(trustedClientIp(h({ "x-forwarded-for": "6.6.6.6, 203.0.113.9" }), trustConfigFromEnv({ RENDER: "true" }))).toBe("203.0.113.9");
    expect(trustedClientIp(h({ "x-forwarded-for": "6.6.6.6, 203.0.113.9" }), trustConfigFromEnv({ DYNO: "web.1" }))).toBe("203.0.113.9");
    expect(trustedClientIp(h({ "fly-client-ip": "203.0.113.5", "x-forwarded-for": "6.6.6.6" }), trustConfigFromEnv({ FLY_APP_NAME: "sy" }))).toBe("203.0.113.5");
    expect(trustedClientIp(h({ "x-nf-client-connection-ip": "203.0.113.6" }), trustConfigFromEnv({ NETLIFY: "true" }))).toBe("203.0.113.6");
    expect(trustedClientIp(h({ "cf-connecting-ip": "203.0.113.7" }), trustConfigFromEnv({ TRUST_CLOUDFLARE: "true" }))).toBe("203.0.113.7");
    expect(trustedClientIp(h({ "x-real-ip": "203.0.113.8" }), trustConfigFromEnv({ VERCEL: "1" }))).toBe("203.0.113.8");
  });
  it("R9: when the host is known, the key is the trusted IP and spoofed entries change nothing", () => {
    const cfg = trustConfigFromEnv({ TRUSTED_PROXY_HOPS: "1" });
    expect(rateLimitKey(h({ "x-forwarded-for": "1.1.1.1, 203.0.113.9" }), cfg)).toBe("203.0.113.9");
    expect(rateLimitKey(h({ "x-forwarded-for": "2.2.2.2, 203.0.113.9" }), cfg)).toBe("203.0.113.9");
  });
});

describe("R9: ADMIN_USER is required outside local dev", () => {
  const basic = (u: string, p: string) => `Basic ${Buffer.from(`${u}:${p}`).toString("base64")}`;
  async function mw() {
    delete (globalThis as { __syAdminGuard?: unknown }).__syAdminGuard;
    vi.resetModules();
    return (await import("@/middleware")).middleware;
  }
  it("R9: deploy with ADMIN_PASSWORD but no ADMIN_USER → admin stays locked, even for admin:<password>", async () => {
    penv.NODE_ENV = "production";
    delete penv.ADMIN_USER;
    penv.ADMIN_PASSWORD = "pw-123";
    const res = await (await mw())(new NextRequest("http://localhost/admin", { headers: { authorization: basic("admin", "pw-123") } }));
    expect(res.status).toBe(401);
  });
  it("R9: local in-memory demo keeps the demo login", async () => {
    penv.NODE_ENV = "production";
    penv.LOCAL_DEMO_BUILD = "true";
    delete penv.ADMIN_USER;
    delete penv.ADMIN_PASSWORD;
    const res = await (await mw())(new NextRequest("http://localhost/admin", { headers: { authorization: basic("admin", "strongyears-demo") } }));
    expect(res.headers.get("x-middleware-next")).toBe("1");
  });
});
