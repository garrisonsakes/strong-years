/**
 * AUDIT_FINAL §7 (Round 8) #2: rotating X-Forwarded-For used to reset the admin
 * lockout. Now: trusted client IP only, lockout per IP AND per username with
 * exponential backoff, and an optional TOTP second factor.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { AdminGuard, BASE_LOCK_MS, FREE_ATTEMPTS, MAX_LOCK_MS, base32Encode, splitPasswordAndCode, totpAt, verifyTotp } from "@/lib/adminGuard";
import { trustedClientIp, type TrustConfig } from "@/lib/clientIp";

const saved = { ...process.env };
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

async function freshMiddleware() {
  delete (globalThis as { __syAdminGuard?: unknown }).__syAdminGuard;
  vi.resetModules();
  return (await import("@/middleware")).middleware;
}
const basic = (user: string, pass: string) => `Basic ${Buffer.from(`${user}:${pass}`).toString("base64")}`;
const adminReq = (auth: string, xff?: string) =>
  new NextRequest("http://localhost/admin", { headers: { authorization: auth, ...(xff ? { "x-forwarded-for": xff } : {}) } });
const allowed = (res: Response) => res.status === 200 && res.headers.get("x-middleware-next") === "1";

describe("R8: trusted client IP", () => {
  const none: TrustConfig = { vercel: false, hops: 0, proxies: [] };
  const h = (o: Record<string, string>) => new Headers(o);
  it("R8 ip: with no trusted proxy configured, X-Forwarded-For is ignored", () => {
    expect(trustedClientIp(h({ "x-forwarded-for": "1.2.3.4" }), none)).toBe("unknown");
  });
  it("R8 ip: one trusted hop → the entry our proxy appended; client-prepended entries are ignored", () => {
    const cfg = { ...none, hops: 1 };
    expect(trustedClientIp(h({ "x-forwarded-for": "6.6.6.6, 9.9.9.9, 203.0.113.7" }), cfg)).toBe("203.0.113.7");
  });
  it("R8 ip: listed proxies are skipped from the right", () => {
    const cfg = { ...none, proxies: ["10.0.0.1", "10.0.0.2"] };
    expect(trustedClientIp(h({ "x-forwarded-for": "6.6.6.6, 203.0.113.7, 10.0.0.2, 10.0.0.1" }), cfg)).toBe("203.0.113.7");
  });
  it("R8 ip: on Vercel, the edge-set x-real-ip wins over any X-Forwarded-For", () => {
    expect(trustedClientIp(h({ "x-real-ip": "198.51.100.4", "x-forwarded-for": "6.6.6.6" }), { ...none, vercel: true })).toBe("198.51.100.4");
  });
  it("R8 ip: garbage is never used as a key", () => {
    expect(trustedClientIp(h({ "x-forwarded-for": "<script>" }), { ...none, hops: 1 })).toBe("unknown");
  });
});

describe("R8: AdminGuard backoff", () => {
  it("R8 guard: free attempts, then 1, 2, 4 … minutes, capped at an hour", () => {
    const g = new AdminGuard();
    const keys = AdminGuard.keys("1.1.1.1", "admin");
    let now = 1_000_000;
    for (let i = 0; i < FREE_ATTEMPTS - 1; i++) g.fail(keys, now);
    expect(g.retryAfter(keys, now)).toBe(0);
    g.fail(keys, now);
    expect(g.retryAfter(keys, now)).toBe(BASE_LOCK_MS / 1000);
    now += BASE_LOCK_MS;
    g.fail(keys, now);
    expect(g.retryAfter(keys, now)).toBe((2 * BASE_LOCK_MS) / 1000);
    for (let i = 0; i < 20; i++) g.fail(keys, now);
    expect(g.retryAfter(keys, now)).toBe(MAX_LOCK_MS / 1000);
    g.success(keys);
    expect(g.retryAfter(keys, now)).toBe(0);
  });
  it("R8 guard: the username key locks even when every attempt comes from a new IP", () => {
    const g = new AdminGuard();
    for (let i = 0; i < FREE_ATTEMPTS; i++) g.fail(AdminGuard.keys(`203.0.113.${i}`, "Admin "), 5);
    expect(g.retryAfter(AdminGuard.keys("198.51.100.99", "admin"), 5)).toBeGreaterThan(0);
    expect(g.retryAfter(AdminGuard.keys("198.51.100.99", "someone-else"), 5)).toBe(0);
  });
});

describe("R8: middleware lockout", () => {
  beforeEach(() => {
    process.env.ADMIN_USER = "admin";
    process.env.ADMIN_PASSWORD = "correct horse";
    delete process.env.ADMIN_TOTP_SECRET;
    delete process.env.VERCEL;
    delete process.env.TRUSTED_PROXIES;
    delete process.env.TRUSTED_PROXY_HOPS;
  });

  it("R8: the verifier's attack (wrong passwords with a new X-Forwarded-For each time) is locked out, and stays locked for the right password", async () => {
    const mw = await freshMiddleware();
    const statuses: number[] = [];
    for (let i = 0; i < 20; i++) statuses.push((await mw(adminReq(basic("admin", `guess${i}`), `10.9.${i}.${i}`))).status);
    expect(statuses.slice(0, FREE_ATTEMPTS)).toEqual(Array(FREE_ATTEMPTS).fill(401));
    expect(statuses.slice(FREE_ATTEMPTS).every((s) => s === 429)).toBe(true);
    const right = await mw(adminReq(basic("admin", "correct horse"), "10.9.99.99"));
    expect(right.status).toBe(429);
    expect(Number(right.headers.get("Retry-After"))).toBeGreaterThan(0);
  });

  it("R8: behind one trusted proxy, rotating the spoofed part of X-Forwarded-For still hits the same IP key", async () => {
    process.env.TRUSTED_PROXY_HOPS = "1";
    const mw = await freshMiddleware();
    for (let i = 0; i < FREE_ATTEMPTS; i++) await mw(adminReq(basic(`user${i}`, "x"), `6.6.6.${i}, 203.0.113.7`));
    // New username, same real IP → locked by IP.
    expect((await mw(adminReq(basic("admin", "correct horse"), "7.7.7.7, 203.0.113.7"))).status).toBe(429);
    // The admin from their own network is fine.
    expect(allowed(await mw(adminReq(basic("admin", "correct horse"), "198.51.100.20")))).toBe(true);
  });

  it("R8: a correct login works and resets the counters", async () => {
    const mw = await freshMiddleware();
    for (let i = 0; i < FREE_ATTEMPTS - 1; i++) await mw(adminReq(basic("admin", "nope")));
    expect(allowed(await mw(adminReq(basic("admin", "correct horse"))))).toBe(true);
    for (let i = 0; i < FREE_ATTEMPTS - 1; i++) expect((await mw(adminReq(basic("admin", "nope")))).status).toBe(401);
  });

  it("R8: with ADMIN_TOTP_SECRET, the password alone is refused; password + current code works", async () => {
    const secret = base32Encode(new TextEncoder().encode("strong-years-admin-2fa"));
    process.env.ADMIN_TOTP_SECRET = secret;
    const mw = await freshMiddleware();
    expect((await mw(adminReq(basic("admin", "correct horse")))).status).toBe(401);
    const bytes = new TextEncoder().encode("strong-years-admin-2fa");
    const code = await totpAt(bytes, Math.floor(Date.now() / 30_000));
    expect(allowed(await mw(adminReq(basic("admin", `correct horse ${code}`))))).toBe(true);
    const wrong = code === "000000" ? "111111" : "000000";
    expect((await mw(adminReq(basic("admin", `correct horse ${wrong}`)))).status).toBe(401);
  });
});

describe("R8: TOTP", () => {
  it("R8 totp: RFC 6238 test vector (SHA-1, T=59 → 94287082, 6 digits → 287082)", async () => {
    const key = new TextEncoder().encode("12345678901234567890");
    expect(await totpAt(key, 1, 8)).toBe("94287082");
    expect(await verifyTotp(base32Encode(key), "287082", 59_000)).toBe(true);
    expect(await verifyTotp(base32Encode(key), "287083", 59_000)).toBe(false);
    expect(await verifyTotp(base32Encode(key), "287082", 59_000 + 10 * 30_000)).toBe(false);
  });
  it("R8 totp: the code is read off the end of the password box", () => {
    expect(splitPasswordAndCode("pa:ss word 123456")).toEqual({ password: "pa:ss word", code: "123456" });
    expect(splitPasswordAndCode("secret123456")).toEqual({ password: "secret", code: "123456" });
    expect(splitPasswordAndCode("secret")).toEqual({ password: "secret", code: "" });
  });
});
