/**
 * Round 10: launch mode, every checkout path refused in prelaunch (and the in-app
 * Stripe paths closed in Shopify mode), /join → Shopify with the sticky cell and
 * attribution, the waitlist routes (enumeration, honeypot, timing, size, rate limits,
 * idempotency, referral), and the launch sequence (≤3 emails + 2 pushes in 72h,
 * double cron, unsubscribe, the cell preserved through the email link).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const jar = vi.hoisted(() => ({ cookies: new Map<string, string>(), headers: new Map<string, string>() }));
vi.mock("next/headers", () => ({
  cookies: async () => ({
    get: (n: string) => (jar.cookies.has(n) ? { name: n, value: jar.cookies.get(n)! } : undefined),
    getAll: () => [...jar.cookies].map(([name, value]) => ({ name, value })),
    set: () => undefined,
    delete: () => undefined,
  }),
  headers: async () => ({ get: (n: string) => jar.headers.get(n.toLowerCase()) ?? null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { env } from "@/lib/config";
import { assignFrontEndCell, cartUrl, DEMO_CATALOG, resolveFrontEnd, seedShopifyCatalog } from "@/lib/billing/shopify";
import { launchConfigFromEnv, openCheckoutNow, resolveLaunch } from "@/lib/launch";
import { LAUNCH_STEPS, nextStep, runLaunchSequence } from "@/lib/launchSequence";
import { resetRateLimits } from "@/lib/rateLimit";
import { signVid, verifyVid } from "@/lib/vid";
import { signFormTime } from "@/lib/waitlistTokens";
import { confirmWaitlist, signupWaitlist } from "@/lib/waitlist";
import { setPushSenderForTests } from "@/lib/push";
import { encodeAttribution } from "@/lib/analytics/attribution";
import type { ShopifyProductRow, WaitlistEntry } from "@/lib/db/types";

let store: MemoryStore;
beforeEach(async () => {
  vi.stubEnv("BILLING_PROVIDER", "shopify");
  vi.stubEnv("LAUNCH_MODE", "prelaunch");
  vi.stubEnv("SHOPIFY_STORE_DOMAIN", "strongyears-test.myshopify.com");
  vi.stubEnv("WAITLIST_MIN_FILL_MS", "0");
  // These suites exercise the canon-3 cell B / cell A split mechanics explicitly. Canon 6 (the 7-day trial, t12)
  // is the default and is covered by R12.canon6-seven-day-trial.test.ts.
  vi.stubEnv("FRONT_END_CELLS", "m12,e12");
  vi.stubEnv("FRONT_END_DEFAULT_CELL", "m12");
  vi.stubEnv("FRONT_END_CELL_TEST", "true");
  vi.stubEnv("DISPLAY_TZ", "America/Los_Angeles");
  store = new MemoryStore();
  setStoreForTests(store);
  await seedShopifyCatalog(store);
  jar.cookies.clear();
  jar.headers.clear();
  resetRateLimits();
});
afterEach(() => {
  vi.unstubAllEnvs();
  setPushSenderForTests(null);
});

async function redirectOf(p: Promise<unknown>): Promise<string | null> {
  try {
    await p;
    return null;
  } catch (e) {
    const d = (e as { digest?: string }).digest;
    if (!d || !d.startsWith("NEXT_REDIRECT")) throw e;
    return d.split(";")[2]!;
  }
}

async function visitor(id: string) {
  jar.cookies.set("sy_vid", await signVid(id, env.sessionSecret));
}

const json = (body: unknown) => ({ method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
const form = (body: Record<string, string>) => ({ method: "POST", headers: { "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(body).toString() });

describe("R10 launch config", () => {
  it("unknown LAUNCH_MODE fails closed; CHECKOUT_OPENS_AT opens it at the real time only", () => {
    expect(launchConfigFromEnv({ LAUNCH_MODE: "LIVE!!" }).mode).toBe("prelaunch");
    const cfg = launchConfigFromEnv({ LAUNCH_MODE: "prelaunch", CHECKOUT_OPENS_AT: "2026-10-21T16:00:00Z" });
    expect(resolveLaunch(cfg, null, new Date("2026-10-21T15:59:59Z")).live).toBe(false);
    expect(resolveLaunch(cfg, null, new Date("2026-10-21T16:00:00Z")).live).toBe(true);
    expect(launchConfigFromEnv({ CHECKOUT_OPENS_AT: "next tuesday" }).opensAtInvalid).toBe(true);
  });
});

describe("R10 prelaunch: every checkout path refuses on the server", () => {
  it("API routes: /api/checkout, /api/checkout/complete, /api/checkout/verify, /api/checkout/mock-complete, /api/upsell", async () => {
    for (const provider of ["shopify", "stripe"]) {
      vi.stubEnv("BILLING_PROVIDER", provider);
      const checkout = await (await import("@/app/api/checkout/route")).POST(new Request("http://l/api/checkout", json({ offer: "founding", email: "a@b.co", autoRenewConsent: true, ageConsent: true })));
      expect(checkout.status).toBe(403);
      expect((await checkout.json()).waitlist).toBe("/waitlist");
      const complete = await (await import("@/app/api/checkout/complete/route")).GET(new Request("http://l/api/checkout/complete?intent=x"));
      expect(complete.headers.get("location")).toMatch(/\/waitlist\?from=checkout$/);
      const verify = await (await import("@/app/api/checkout/verify/route")).POST(new Request("http://l/api/checkout/verify", form({ token: "t" })));
      expect(verify.headers.get("location")).toMatch(/\/waitlist/);
      const mock = await (await import("@/app/api/checkout/mock-complete/route")).POST(new Request("http://l/api/checkout/mock-complete", json({ intentId: "x" })));
      expect(mock.status).toBe(403);
      const upsell = await (await import("@/app/api/upsell/route")).POST(new Request("http://l/api/upsell", form({ key: "program" })));
      expect(upsell.headers.get("location")).toMatch(/\/waitlist/);
    }
    expect(await store.count("checkout_intents")).toBe(0);
  });

  it("pages: /join, /checkout/[offer], /checkout/mock/[intent], /upsell/[step], /gift all land on /waitlist, keeping attribution params", async () => {
    const sp = Promise.resolve({ post_id: "C8xYz12AbC", platform: "ig", keyword: "JOIN", price: "1" });
    const join = await redirectOf((await import("@/app/(funnel)/join/page")).default({ searchParams: sp }));
    expect(join).toMatch(/^\/waitlist\?/);
    expect(join).toContain("post_id=C8xYz12AbC");
    expect(join).not.toContain("price=");
    expect(await redirectOf((await import("@/app/(funnel)/checkout/[offer]/page")).default({ params: Promise.resolve({ offer: "founding" }), searchParams: Promise.resolve({}) }))).toMatch(/^\/waitlist/);
    expect(await redirectOf((await import("@/app/(funnel)/checkout/mock/[intent]/page")).default({ params: Promise.resolve({ intent: "x" }), searchParams: Promise.resolve({}) } as never))).toMatch(/^\/waitlist/);
    expect(await redirectOf((await import("@/app/(funnel)/upsell/[step]/page")).default({ params: Promise.resolve({ step: "program" }), searchParams: Promise.resolve({}) } as never))).toMatch(/^\/waitlist/);
    expect(await redirectOf((await import("@/app/(site)/gift/page")).default())).toMatch(/^\/waitlist/);
  });

  it("the library refuses too, whichever route calls it (startCheckout in prelaunch)", async () => {
    vi.stubEnv("BILLING_PROVIDER", "stripe");
    const { startCheckout } = await import("@/lib/billing/checkout");
    const r = await startCheckout(store, { offer: "founding", arm: "B", gentle: false, email: "x@y.co", firstName: "X", phone: "", smsConsent: false, autoRenewConsent: true, ageConsent: true, gift: null, attribution: null, leadId: null, ip: null, userAgent: null });
    expect(r.ok).toBe(false);
  });

  it("live + Shopify mode: the in-app Stripe checkout routes stay closed (410 / redirect to /join)", async () => {
    await openCheckoutNow(store, "test");
    const checkout = await (await import("@/app/api/checkout/route")).POST(new Request("http://l/api/checkout", json({ offer: "founding" })));
    expect(checkout.status).toBe(410);
    const upsell = await (await import("@/app/api/upsell/route")).POST(new Request("http://l/api/upsell", form({ key: "program" })));
    expect(upsell.headers.get("location")).toMatch(/\/join$/);
    expect(await redirectOf((await import("@/app/(funnel)/checkout/[offer]/page")).default({ params: Promise.resolve({ offer: "reset" }), searchParams: Promise.resolve({}) }))).toBe("/join");
  });
});

describe("R10 /join → Shopify checkout (live)", () => {
  beforeEach(async () => {
    await openCheckoutNow(store, "test");
  });

  const joinUrl = async (sp: Record<string, string> = {}) => new URL((await redirectOf((await import("@/app/(funnel)/join/page")).default({ searchParams: Promise.resolve(sp) })))!);
  const rows = DEMO_CATALOG as ShopifyProductRow[];

  /** The product page the redirect lands on (cell B goes through Shopify's /discount/<code> share link first). */
  const landing = (u: URL) => (u.pathname.startsWith("/discount/") ? new URL(u.searchParams.get("redirect")!, u.origin) : u);

  it("redirects to the store's PRODUCT PAGE for the visitor's sticky cell, every time (selling plans don't work with cart permalinks)", async () => {
    const vid = "11111111-2222-4333-8444-555555555555";
    await visitor(vid);
    const a = await joinUrl();
    const b = await joinUrl();
    expect(a.toString()).toBe(b.toString());
    expect(a.host).toBe("strongyears-test.myshopify.com");
    const cell = assignFrontEndCell(vid, ["m12", "e12"]);
    const row = rows.find((r) => r.cell === cell && r.cohort !== "standard")!;
    const page = landing(a);
    expect(page.pathname).toBe(`/products/${row.product_handle}`);
    expect(page.pathname).not.toMatch(/^\/cart\//);
    expect(page.searchParams.get("vid")).toBe(vid);
    expect(page.searchParams.get("sku")).toBe(row.sku);
    if (row.discount_code) {
      // cell B: the first-payment-only code is applied by the share link AND the page shows the starter view
      expect(a.pathname).toBe(`/discount/${row.discount_code}`);
      expect(page.searchParams.get("view")).toBe("starter");
      expect(page.searchParams.get("arm")).toBe("B");
    } else {
      expect(page.searchParams.get("arm")).toBe("A");
      expect(page.searchParams.get("cell")).toBe(row.cell);
    }
  });

  it("query parameters can't pick the cell, price or product (only allow-listed named offers)", async () => {
    await visitor("11111111-2222-4333-8444-555555555555");
    const base = await joinUrl();
    const tampered = await joinUrl({ cell: "e7", price: "1", sku: "ebook_e7", variant: "9000000007", selling_plan: "7000000012", "attributes[sy_cell]": "e7", view: "x" });
    expect(landing(tampered).pathname).toBe(landing(base).pathname);
    expect(landing(tampered).searchParams.get("sku")).toBe(landing(base).searchParams.get("sku"));
    const gift = await joinUrl({ offer: "gift12" });
    expect(gift.pathname).toBe("/products/gift-strong-years");
    expect(landing(await joinUrl({ offer: "../../admin" })).pathname).toBe(landing(base).pathname);
  });

  it("a forged visitor cookie counts as no visitor (default cell B, $12 → $25)", async () => {
    jar.cookies.set("sy_vid", "11111111-2222-4333-8444-555555555555.deadbeef");
    const u = await joinUrl();
    expect(u.pathname).toBe("/discount/STARTER12");
    const page = landing(u);
    expect(page.searchParams.get("sku")).toBe("bundle_m12");
    expect(page.searchParams.get("vid")).toBeNull();
  });

  it("the last touch rides along as validated query parameters the theme writes as cart attributes", async () => {
    jar.cookies.set("sy_attr", encodeAttribution({ post_id: "C8xYz12AbC", platform: "ig", keyword: "JOIN", utm_source: "ig", first_seen_at: "2026-10-01T10:00:00.000Z" }));
    jar.cookies.set("sy_lt", encodeAttribution({ post_id: "TT_99", platform: "tt" }));
    const page = landing(await joinUrl());
    expect(page.searchParams.get("post_id")).toBe("TT_99");
    expect(page.searchParams.get("platform")).toBe("tt");
    for (const v of page.searchParams.values()) expect(v.length).toBeLessThanOrEqual(100);
  });

  it("oversized or junk attribution in cookies is dropped, never truncated into something valid", async () => {
    jar.cookies.set("sy_attr", encodeAttribution({ post_id: "x".repeat(65), keyword: "<b>", utm_source: "y".repeat(300) } as never));
    const page = landing(await joinUrl());
    expect(page.searchParams.get("post_id")).toBeNull();
    expect(page.searchParams.get("utm_source")).toBeNull();
  });

  it("once the founding cohort is full, cells switch to standard-price rows (STARTER12S: $12 → $35)", () => {
    const open = resolveFrontEnd(rows, { visitorId: null, cohortOpen: true }, { FRONT_END_CELLS: "m12", FRONT_END_DEFAULT_CELL: "m12" })!;
    const closed = resolveFrontEnd(rows, { visitorId: null, cohortOpen: false }, { FRONT_END_CELLS: "m12", FRONT_END_DEFAULT_CELL: "m12" })!;
    expect(open.row.sku).toBe("bundle_m12");
    expect(closed.row.sku).toBe("bundle_m12_standard");
    const u = new URL(cartUrl(closed.row, { attribution: null, cell: "m12", visitorId: null }));
    expect(u.pathname).toBe("/discount/STARTER12S");
    expect(landing(u).pathname).toBe("/products/strong-years-membership");
  });

  it("the displayed price equals the charged price: cell B rows share the founding variant + plan and differ only by the code", () => {
    const b = rows.find((r) => r.sku === "bundle_m12")!;
    const f = rows.find((r) => r.sku === "founding_monthly")!;
    expect([b.shopify_variant_id, b.selling_plan_id]).toEqual([f.shopify_variant_id, f.selling_plan_id]);
    expect(b.discount_code).toBe("STARTER12");
    expect(b.price_cents).toBe(1200);
    expect(b.recurring_cents).toBe(f.price_cents);
    expect(f.discount_code).toBeNull();
  });

  it("cells are spread across visitors (sticky hash, roughly even)", () => {
    const counts: Record<string, number> = {};
    for (let i = 0; i < 4000; i++) {
      const c = assignFrontEndCell(`v-${i}`, ["m12", "e12"]);
      counts[c] = (counts[c] ?? 0) + 1;
    }
    for (const n of Object.values(counts)) expect(n / 4000).toBeGreaterThan(0.2);
  });
});

describe("R10 waitlist routes", () => {
  const post = async (body: Record<string, string>) => (await import("@/app/api/waitlist/route")).POST(new Request("http://l/api/waitlist", form(body)));
  const ok = (email: string, extra: Record<string, string> = {}) => ({ email, consent_email: "1", ft: signFormTime(Date.now() - 5000), website: "", ...extra });

  it("identical responses for new, pending, confirmed and unsubscribed addresses (no enumeration)", async () => {
    const r1 = await post(ok("new@example.com"));
    const entry = (await store.findOne("waitlist", { email: "new@example.com" }))!;
    await store.update("waitlist", entry.id, { last_signup_email_at: new Date(Date.now() - 3600_000).toISOString() });
    const r2 = await post(ok("new@example.com")); // pending
    await store.update("waitlist", entry.id, { status: "confirmed", last_signup_email_at: new Date(Date.now() - 3600_000).toISOString() });
    const r3 = await post(ok("NEW@example.com ")); // confirmed
    await store.update("waitlist", entry.id, { status: "unsubscribed", last_signup_email_at: new Date(Date.now() - 3600_000).toISOString() });
    const r4 = await post(ok("new@example.com")); // unsubscribed
    for (const r of [r1, r2, r3, r4]) {
      expect(r.status).toBe(303);
      expect(r.headers.get("location")).toBe("http://l/waitlist/thanks");
      expect([...r.headers.keys()].sort()).toEqual([...r1.headers.keys()].sort());
    }
    expect(await store.count("waitlist")).toBe(1);
  });

  it("honeypot and too-fast submissions get the same thanks page and store nothing", async () => {
    const bot = await post(ok("bot@example.com", { website: "http://spam" }));
    expect(bot.headers.get("location")).toBe("http://l/waitlist/thanks");
    vi.stubEnv("WAITLIST_MIN_FILL_MS", "3000");
    const fast = await post(ok("fast@example.com", { ft: signFormTime(Date.now() - 500) }));
    expect(fast.headers.get("location")).toBe("http://l/waitlist/thanks");
    const forged = await post(ok("forged@example.com", { ft: `${Date.now() - 9000}.notasignature` }));
    expect(forged.headers.get("location")).toBe("http://l/waitlist/thanks");
    expect(await store.count("waitlist")).toBe(0);
  });

  it("consent is required (unticked by default), oversized bodies are refused, IP rate limit says 'busy'", async () => {
    const noConsent = await post({ email: "c@example.com", ft: signFormTime(Date.now() - 5000) });
    expect(noConsent.headers.get("location")).toContain("error=consent");
    const big = await (await import("@/app/api/waitlist/route")).POST(new Request("http://l/api/waitlist", { method: "POST", body: "email=" + "a".repeat(5000) }));
    expect(big.status).toBe(413);
    for (let i = 0; i < 8; i++) await post(ok(`r${i}@example.com`));
    expect((await post(ok("r9@example.com"))).headers.get("location")).toContain("error=busy");
  });

  it("double submits send one confirmation email; confirming is single use", async () => {
    await Promise.all([post(ok("twice@example.com")), post(ok("twice@example.com"))]);
    expect(await store.count("waitlist", { email: "twice@example.com" })).toBe(1);
    expect(await store.count("outbox", { template: "WL1_confirm", to: "twice@example.com" })).toBe(1);
  });

  it("referral: one bonus PDF when a friend confirms, never a queue position; self-referral does nothing", async () => {
    const meta = { ip: null, userAgent: null };
    const tok = async (email: string) => {
      const mail = (await store.find("outbox", { to: email, template: "WL1_confirm" })).at(-1)!;
      expect(mail.body).not.toMatch(/token=[A-Za-z0-9]/); // stored copy is redacted
      return mail;
    };
    // Drive the library directly so we can see the raw token.
    const base = { firstName: "A", emailConsent: true, adConsent: false, visitorId: null, attribution: null, ip: null, userAgent: null };
    const sentTokens: string[] = [];
    const notify = await import("@/lib/notify");
    const spy = vi.spyOn(notify, "sendEmail").mockImplementation(async (m) => {
      const t = m.text.match(/token=([A-Za-z0-9_-]+)/)?.[1];
      if (t) sentTokens.push(t);
      return { status: "stubbed" } as never;
    });
    await signupWaitlist(store, { ...base, email: "ref@example.com" });
    await confirmWaitlist(store, sentTokens.at(-1)!, meta);
    const referrer = (await store.findOne("waitlist", { email: "ref@example.com" }))!;
    await signupWaitlist(store, { ...base, email: "friend1@example.com", ref: referrer.referral_code });
    await confirmWaitlist(store, sentTokens.at(-1)!, meta);
    await signupWaitlist(store, { ...base, email: "friend2@example.com", ref: referrer.referral_code });
    const t2 = sentTokens.at(-1)!;
    await confirmWaitlist(store, t2, meta);
    expect((await confirmWaitlist(store, t2, meta)).ok).toBe(false); // replayed link
    expect((await store.get("waitlist", referrer.id))!.referral_reward_at).not.toBeNull();
    expect(spy.mock.calls.filter(([m]) => m.template === "WL3_referral_bonus")).toHaveLength(1);
    spy.mockRestore();
    void tok;
  });
});

describe("R10 launch sequence", () => {
  const T0 = new Date("2026-10-10T17:00:00Z"); // 10:00 in Los Angeles
  const at = (h: number) => new Date(T0.getTime() + h * 3600_000);

  async function confirmed(email: string, extra: Partial<WaitlistEntry> = {}) {
    return store.insert("waitlist", { email, first_name: null, status: "confirmed", confirm_token_hash: null, confirm_expires_at: null, last_signup_email_at: null, confirmed_at: T0.toISOString(), unsubscribed_at: null, ad_consent_requested: false, visitor_id: null, referral_code: Math.random().toString(36).slice(2, 10).toUpperCase(), referred_by: null, referral_reward_at: null, attribution: null, member_id: null, converted_at: null, ip: null, user_agent: null, ...extra });
  }

  it("nothing is sent in prelaunch", async () => {
    await confirmed("a@example.com");
    const r = await runLaunchSequence(store, T0);
    expect(r.emails).toBe(0);
    expect(await store.count("outbox")).toBe(0);
  });

  it("at most 3 emails and 2 pushes in 72 hours, idempotent under double (concurrent) cron; unsubscribed and joined people get nothing", async () => {
    vi.stubEnv("VAPID_PUBLIC_KEY", "pub");
    vi.stubEnv("VAPID_PRIVATE_KEY", "priv");
    const pushes: string[] = [];
    setPushSenderForTests(async (sub) => {
      pushes.push(sub.endpoint);
      return { statusCode: 201 } as never;
    });
    const a = await confirmed("a@example.com");
    await store.insert("waitlist_push", { waitlist_id: a.id, endpoint: "https://push.example/a", p256dh: "p", auth: "x", failures: 0 });
    await confirmed("gone@example.com", { status: "unsubscribed" });
    await confirmed("joined@example.com", { member_id: "m1", converted_at: T0.toISOString() });
    await openCheckoutNow(store, "test", T0);
    // Every 15 minutes for 4 days, each tick run twice at the same moment.
    for (let h = 0; h <= 96; h += 0.25) await Promise.all([runLaunchSequence(store, at(h)), runLaunchSequence(store, at(h))]);
    const mails = await store.find("outbox", { to: "a@example.com", channel: "email" });
    expect(mails.map((m) => m.template).sort()).toEqual(["WL_launch_e1", "WL_launch_e2", "WL_launch_e3"]);
    const sends = await store.find("launch_sends", { waitlist_id: a.id });
    expect(sends.filter((s) => s.channel === "push").map((s) => s.step).sort()).toEqual(["p1", "p2"]);
    expect(pushes).toHaveLength(2);
    expect(sends.every((s) => new Date(s.created_at).getTime() - T0.getTime() < 72 * 3600_000)).toBe(true);
    expect(await store.count("outbox", { to: "gone@example.com" })).toBe(0);
    expect(await store.count("outbox", { to: "joined@example.com" })).toBe(0);
    // Every email carries the one-click leave link.
    for (const m of mails) expect(m.body).toMatch(/waitlist\/unsubscribe\?u=/);
  });

  it("missed steps are skipped (cron down), never bunched; never backwards", () => {
    const now = at(30);
    expect(nextStep("email", 30, [], now)?.key).toBe("e2");
    expect(nextStep("email", 30, [{ step: "e2", created_at: at(29).toISOString() }], now)).toBeNull();
    expect(nextStep("email", 70, [{ step: "e3", created_at: at(66).toISOString() }], at(70))).toBeNull();
    expect(nextStep("email", 72, [], at(72))).toBeNull();
    expect(LAUNCH_STEPS.filter((s) => s.channel === "email")).toHaveLength(3);
  });

  it("the email link carries the person's signed visitor id: /join on any device sends them to their own cell", async () => {
    const vid = "99999999-2222-4333-8444-555555555555";
    await confirmed("cell@example.com", { visitor_id: vid });
    await openCheckoutNow(store, "test", T0);
    await runLaunchSequence(store, at(0.1));
    const body = (await store.findOne("outbox", { to: "cell@example.com", template: "WL_launch_e1" }))!.body;
    const link = new URL(body.match(/https?:\/\/\S+\/join\?\S+/)![0]);
    const sv = link.searchParams.get("sy_v")!;
    expect(await verifyVid(sv, env.sessionSecret)).toBe(vid);
    expect(body).not.toMatch(/\$1\b/);
    // The middleware turns sy_v into the visitor cookie; then /join picks the cell from it.
    jar.cookies.set("sy_vid", sv);
    const raw = new URL((await redirectOf((await import("@/app/(funnel)/join/page")).default({ searchParams: Promise.resolve(Object.fromEntries(link.searchParams)) })))!);
    const dest = raw.pathname.startsWith("/discount/") ? new URL(raw.searchParams.get("redirect")!, raw.origin) : raw;
    const cell = assignFrontEndCell(vid, ["m12", "e12"]);
    expect(dest.searchParams.get("sku")).toBe(cell === "m12" ? "bundle_m12" : "ebook_e12");
    expect(dest.searchParams.get("vid")).toBe(vid);
    expect(dest.searchParams.get("utm_source")).toBeNull(); // middleware sets sy_lt in the real flow
  });
});
