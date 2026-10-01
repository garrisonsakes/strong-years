/**
 * Round 10: server-side conversion events (Meta CAPI + TikTok Events API, mocked),
 * sign-in by email code (no password), and the service-only per-post endpoint.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const jar = vi.hoisted(() => ({ cookies: new Map<string, string>() }));
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: (n: string) => (jar.cookies.has(n) ? { name: n, value: jar.cookies.get(n)! } : undefined), getAll: () => [], set: () => undefined, delete: () => undefined }),
  headers: async () => ({ get: () => null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { flushConversions, recordAdConsent, recordConversion, withdrawAdConsent } from "@/lib/conversions";
import { buildMetaEvent, buildTikTokEvent, emailHash } from "@/lib/conversions/adapters";
import { consumeLoginCode, issueLoginLinkAndCode, LOGIN_CODE_MAX_ATTEMPTS } from "@/lib/auth/verification";
import { defaultMember } from "@/lib/members";
import { resetRateLimits } from "@/lib/rateLimit";
import { handleShopifyWebhook } from "@/lib/billing/shopifyWebhook";
import { seedShopifyCatalog } from "@/lib/billing/shopify";
import { openCheckoutNow } from "@/lib/launch";

let store: MemoryStore;
const SITE = "https://strongyears.test";
beforeEach(async () => {
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
  resetRateLimits();
  jar.cookies.clear();
});
afterEach(() => {
  vi.unstubAllEnvs();
  vi.restoreAllMocks();
});

function keys() {
  vi.stubEnv("META_PIXEL_ID", "123");
  vi.stubEnv("META_CAPI_TOKEN", "meta-secret");
  vi.stubEnv("TIKTOK_PIXEL_CODE", "TTPIX");
  vi.stubEnv("TIKTOK_ACCESS_TOKEN", "tt-secret");
}

describe("R10 conversion events (Meta CAPI + TikTok Events API)", () => {
  it("disabled without keys: no network at all", async () => {
    const f = vi.spyOn(globalThis, "fetch");
    await recordAdConsent(store, "a@example.com", { ip: null, userAgent: null, source: "t" });
    expect((await recordConversion(store, { name: "Purchase", eventId: "e1", sourcePath: "/checkout", email: "a@example.com" }, SITE)).decision).toBe("disabled");
    expect(f).not.toHaveBeenCalled();
  });

  it("only with ad-tracking consent; withdrawn consent, GPC / Do Not Sell and health-context surfaces send nothing", async () => {
    keys();
    const f = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ code: 0 }), { status: 200 }));
    expect((await recordConversion(store, { name: "Lead", eventId: "e2", sourcePath: "/waitlist", email: "b@example.com" }, SITE)).decision).toBe("no_consent");
    await recordAdConsent(store, "b@example.com", { ip: null, userAgent: null, source: "t" });
    expect((await recordConversion(store, { name: "Lead", eventId: "e3", sourcePath: "/waitlist", email: "b@example.com", attribution: { ad_opt_out: true } }, SITE)).decision).toBe("no_consent");
    expect((await recordConversion(store, { name: "Lead", eventId: "e4", sourcePath: "/quiz/strength-age", email: "b@example.com", healthContext: true }, SITE)).decision).toBe("health_context");
    expect(f).not.toHaveBeenCalled();
    const r = await recordConversion(store, { name: "Lead", eventId: "e5", sourcePath: "/waitlist", email: "B@Example.com " }, SITE);
    expect(r.decision).toBe("queued");
    expect(r.delivered.sort()).toEqual(["meta", "tiktok"]);
    await withdrawAdConsent(store, "b@example.com", { ip: null, userAgent: null, source: "t" });
    expect((await recordConversion(store, { name: "Lead", eventId: "e6", sourcePath: "/waitlist", email: "b@example.com" }, SITE)).decision).toBe("no_consent");
  });

  it("deduplicated by event_id (a retry or a second source never makes a second event); tokens never in URLs", async () => {
    keys();
    const f = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ code: 0 }), { status: 200 }));
    await recordAdConsent(store, "c@example.com", { ip: null, userAgent: null, source: "t" });
    await recordConversion(store, { name: "Purchase", eventId: "shop_1_purchase", sourcePath: "/checkout", email: "c@example.com", valueCents: 1200 }, SITE);
    const again = await recordConversion(store, { name: "Purchase", eventId: "shop_1_purchase", sourcePath: "/checkout", email: "c@example.com", valueCents: 1200 }, SITE);
    expect(again.decision).toBe("duplicate");
    expect(f).toHaveBeenCalledTimes(2);
    for (const [url] of f.mock.calls) expect(String(url)).not.toMatch(/secret/);
    const tt = f.mock.calls.find(([u]) => String(u).includes("tiktok"))!;
    expect((tt[1] as RequestInit).headers).toMatchObject({ "Access-Token": "tt-secret" });
  });

  it("payloads carry only the hashed email and a condition-free URL: no plain email, IP, quiz answers or health words", () => {
    const e = { name: "Subscribe" as const, eventId: "x1", sourcePath: "/quiz/strength-age/result/abc", email: "Ruth@Example.com", valueCents: 2500, contentName: "founding", timeMs: 1_790_000_000_000 };
    const meta = buildMetaEvent(e, SITE);
    const tt = buildTikTokEvent(e, SITE);
    const s = JSON.stringify([meta, tt]);
    expect(s).not.toMatch(/ruth|example\.com|strength-age|abc|client_ip|user_agent/i);
    expect(meta.user_data.em[0]).toBe(emailHash("ruth@example.com"));
    expect(tt.user.email).toMatch(/^[0-9a-f]{64}$/);
    expect(tt.event).toBe("Subscribe");
    expect(buildTikTokEvent({ ...e, name: "Purchase" }, SITE).event).toBe("CompletePayment");
    expect(buildMetaEvent({ ...e, contentName: "arthritis_plan" }, SITE).custom_data.content_name).toBeUndefined();
  });

  it("failed sends retry with backoff from the cron; consent withdrawn meanwhile → skipped, not sent", async () => {
    keys();
    await recordAdConsent(store, "d@example.com", { ip: null, userAgent: null, source: "t" });
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("err", { status: 500 }));
    await recordConversion(store, { name: "Lead", eventId: "e9", sourcePath: "/waitlist", email: "d@example.com" }, SITE);
    expect(await store.count("conversion_outbox", { status: "failed" })).toBe(2);
    await withdrawAdConsent(store, "d@example.com", { ip: null, userAgent: null, source: "t" });
    const r = await flushConversions(store, new Date(Date.now() + 3600_000));
    expect(r.skipped).toBe(2);
  });

  it("a Shopify membership order emits Purchase (books) + Subscribe once, with consent, deduped on replay", async () => {
    keys();
    vi.stubEnv("BILLING_PROVIDER", "shopify");
    await openCheckoutNow(store, "t");
    const f = vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ code: 0 }), { status: 200 }));
    await recordAdConsent(store, "e@example.com", { ip: null, userAgent: null, source: "t" });
    const order = { id: 77, email: "e@example.com", customer: { id: 1 }, line_items: [{ id: 771, variant_id: 9000000012, price: "12.00", quantity: 1 }, { id: 772, variant_id: 9000000025, price: "25.00", quantity: 1, selling_plan_allocation: { selling_plan: { id: 7000000025 } } }] };
    await handleShopifyWebhook(store, { webhookId: "wh-conv-0001", topic: "orders/paid", payload: order });
    await handleShopifyWebhook(store, { webhookId: "wh-conv-0002", topic: "orders/paid", payload: order });
    const rows = await store.find("conversion_outbox");
    expect(rows.map((r) => `${r.platform}:${r.event_name}`).sort()).toEqual(["meta:Purchase", "meta:Subscribe", "tiktok:Purchase", "tiktok:Subscribe"]);
    expect(f).toHaveBeenCalledTimes(4);
    expect(JSON.stringify(rows.map((r) => r.payload))).not.toContain("e@example.com");
  });
});

describe("R10 sign-in by email code (no password)", () => {
  async function member(email = "pat@example.com") {
    return store.insert("members", { ...defaultMember(email, "Pat") });
  }

  it("the right code works once; wrong codes burn it after 5 tries; codes are bound to the member", async () => {
    const m = await member();
    const other = await member("other@example.com");
    const { code } = await issueLoginLinkAndCode(store, m.id, SITE);
    expect(await consumeLoginCode(store, other.id, code)).toBe(false);
    expect(await consumeLoginCode(store, m.id, code)).toBe(true);
    expect(await consumeLoginCode(store, m.id, code)).toBe(false);
    const { code: c2 } = await issueLoginLinkAndCode(store, m.id, SITE);
    const wrong = c2 === "000000" ? "111111" : "000000";
    for (let i = 0; i < LOGIN_CODE_MAX_ATTEMPTS; i++) expect(await consumeLoginCode(store, m.id, wrong)).toBe(false);
    expect(await consumeLoginCode(store, m.id, c2)).toBe(false);
  });

  it("expired codes fail; parallel right guesses succeed once", async () => {
    const m = await member();
    const { code } = await issueLoginLinkAndCode(store, m.id, SITE, "/app", 1000);
    expect(await consumeLoginCode(store, m.id, code, new Date(Date.now() + 5000))).toBe(false);
    const { code: c2 } = await issueLoginLinkAndCode(store, m.id, SITE);
    const r = await Promise.all([consumeLoginCode(store, m.id, c2), consumeLoginCode(store, m.id, c2)]);
    expect(r.filter(Boolean)).toHaveLength(1);
  });

  it("routes: same response for a member and a stranger; the code signs in and verifies the inbox; a wrong code doesn't", async () => {
    const m = await member();
    const magic = (await import("@/app/api/auth/magic/route")).POST;
    const fd = (email: string) => {
      const f = new FormData();
      f.set("email", email);
      return new Request("http://l/api/auth/magic", { method: "POST", body: f });
    };
    const a = await magic(fd("pat@example.com"));
    const b = await magic(fd("nobody@example.com"));
    expect(a.status).toBe(b.status);
    expect(a.headers.get("location")?.split("&")[0]).toBe(b.headers.get("location")?.split("&")[0]);
    const mail = (await store.findOne("outbox", { template: "magic_link" }))!;
    expect(mail.subject).not.toMatch(/\d{6}/); // the code is redacted from the stored copy
    // Read the real code by issuing one ourselves.
    const { code } = await issueLoginLinkAndCode(store, m.id, SITE);
    jar.cookies.set("sy_login_email", "pat@example.com");
    const route = (await import("@/app/api/auth/code/route")).POST;
    const bad = await route(new Request("http://l/api/auth/code", { method: "POST", body: "code=12345x" }));
    expect(bad.headers.get("location")).toContain("error=code");
    const good = await route(new Request("http://l/api/auth/code", { method: "POST", body: `code=${code}` }));
    expect(good.headers.get("location")).toBe("http://l/app");
    expect(good.headers.get("set-cookie")).toMatch(/sy_session=/);
    expect((await store.get("members", m.id))!.email_verified_at).not.toBeNull();
    jar.cookies.set("sy_login_email", "nobody@example.com");
    const stranger = await route(new Request("http://l/api/auth/code", { method: "POST", body: "code=123456" }));
    expect(stranger.headers.get("location")).toBe(bad.headers.get("location"));
  });
});

describe("R10 growth engine endpoint (service only)", () => {
  const TOKEN = "g".repeat(40);
  const get = async (auth?: string) => (await import("@/app/api/growth/posts/route")).GET(new Request("http://l/api/growth/posts", { headers: auth ? { authorization: auth } : {} }));

  it("off without a token (404), 401 with a wrong one, aggregates only with the right one", async () => {
    expect((await get(`Bearer ${TOKEN}`)).status).toBe(404);
    vi.stubEnv("GROWTH_API_TOKEN", TOKEN);
    expect((await get("Bearer nope")).status).toBe(401);
    vi.stubEnv("BILLING_PROVIDER", "shopify");
    await openCheckoutNow(store, "t");
    const attrs = [{ name: "sy_ft_post_id", value: "REEL_1" }, { name: "sy_ft_platform", value: "ig" }, { name: "sy_ft_keyword", value: "JOIN" }];
    await handleShopifyWebhook(store, { webhookId: "wh-growth-0001", topic: "orders/paid", payload: { id: 5, email: "g1@example.com", customer: { id: 9 }, note_attributes: attrs, discount_codes: [{ code: "STARTER12" }], line_items: [{ id: 51, variant_id: 9000000025, price: "25.00", total_discount: "13.00", quantity: 1, selling_plan_allocation: { selling_plan: { id: 7000000025 } } }] } });
    await handleShopifyWebhook(store, { webhookId: "wh-growth-0002", topic: "orders/paid", payload: { id: 6, email: "g2@example.com", customer: { id: 10 }, note_attributes: attrs, line_items: [{ id: 61, variant_id: 9000000012, price: "12.00", quantity: 1 }] } });
    await store.insert("waitlist", { email: "w@example.com", status: "confirmed", confirmed_at: new Date().toISOString(), referral_code: "ABCDEFGH", attribution: { post_id: "REEL_1" } });
    const res = await get(`Bearer ${TOKEN}`);
    expect(res.status).toBe(200);
    const body = await res.json();
    const row = body.first_touch.find((r: { post_id: string }) => r.post_id === "REEL_1");
    expect(row).toMatchObject({ platform: "ig", keywords: ["JOIN"], waitlist_confirmed: 1, ebook_buyers: 2, members: 1, paying_members: 1, mrr_cents: 2500 });
    expect(JSON.stringify(body)).not.toMatch(/@example\.com/);
  });
});
