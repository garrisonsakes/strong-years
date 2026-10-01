/**
 * AUDIT_FINAL §6 R2-1 (pre-account hijack). Someone pays for the $1 trial with an
 * email that has no account yet. Later the real owner logs in by magic link and
 * chats. The payer's checkout cookie must never show the owner's chat, or any
 * account data, before or after the owner verifies.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const jar = vi.hoisted(() => ({ cookie: undefined as string | undefined }));
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: (n: string) => (n === "sy_session" && jar.cookie ? { name: n, value: jar.cookie } : undefined) }),
  headers: async () => ({ get: () => null }),
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { currentMember, currentPurchaser } from "@/lib/auth/server";
import { issueMagicLink, markEmailVerified, resolveSession } from "@/lib/auth/verification";
import { PURCHASE_SESSION_MINUTES, signSession, verifySession } from "@/lib/auth/session";
import { env } from "@/lib/config";
import { createGift } from "@/lib/gifts";

let store: MemoryStore;
const saved = { ...process.env };
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  jar.cookie = undefined;
});
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

const OWNER = "future.owner@example.com";
const base: StartCheckoutInput = {
  offer: "trial",
  arm: "A",
  gentle: false,
  email: OWNER,
  firstName: "Mallory",
  phone: "",
  smsConsent: false,
  autoRenewConsent: true,
  ageConsent: true,
  gift: null,
  attribution: null,
  leadId: null,
  ip: null,
  userAgent: null,
};

const cookieOf = (res: Response) => res.headers.get("set-cookie")?.match(/sy_session=([^;]*)/)?.[1] ?? null;

/** Checkout + Stripe's completion event + the success redirect, like a real browser. */
async function pay(input: Partial<StartCheckoutInput>, pm = "pm_attacker") {
  const r = await startCheckout(store, { ...base, ...input });
  if (!r.ok) throw new Error(JSON.stringify(r.errors));
  await handleStripeEvent(store, {
    id: `evt_${r.intentId}`,
    type: "checkout.session.completed",
    data: { object: { metadata: { intent_id: r.intentId, payment_method: pm }, payment_status: "paid", customer: `cus_${pm}`, subscription: input.gift ? null : `sub_${r.intentId.slice(0, 6)}` } },
  });
  const { GET } = await import("@/app/api/checkout/complete/route");
  const res = await GET(new Request(`http://localhost/api/checkout/complete?intent=${r.intentId}`));
  return { intentId: r.intentId, res, cookie: cookieOf(res), setCookie: res.headers.get("set-cookie") ?? "", location: res.headers.get("location") ?? "" };
}

/** The real owner opens a login link from their inbox. */
async function ownerLogsIn(email = OWNER) {
  const m = (await store.findOne("members", { email }))!;
  const link = await issueMagicLink(store, m.id, "http://localhost");
  const { GET } = await import("@/app/auth/verify/route");
  const res = await GET(new Request(link));
  expect(res.headers.get("location")).toMatch(/\/app$/);
  return cookieOf(res)!;
}

async function chatAs(cookie: string | null, text: string) {
  jar.cookie = cookie ?? undefined;
  const { POST } = await import("@/app/api/chat/route");
  const res = await POST(new Request("http://localhost/api/chat", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ character: "chang", text }) }));
  return { status: res.status, body: (await res.json()) as { reply?: { content: string }; error?: string } };
}

async function asCookie<T>(cookie: string | null, fn: () => Promise<T>): Promise<T> {
  jar.cookie = cookie ?? undefined;
  return fn();
}

describe("R2-1: a checkout for an unverified email never opens the account", () => {
  it("R2-1: verifier's scenario: $1 trial with an unregistered email; owner logs in and chats; the payer's cookie sees nothing", async () => {
    const attack = await pay({});
    expect(attack.cookie).toBeTruthy();
    expect(attack.location).toMatch(/\/upsell\/program$/);
    // The payer's session is purchase-scoped: it can't read the account even now.
    expect(await asCookie(attack.cookie, currentMember)).toBeNull();
    expect((await asCookie(attack.cookie, currentPurchaser))?.scope).toBe("purchase");
    expect((await chatAs(attack.cookie, "hello")).status).toBe(401);

    // The real owner proves the inbox with a login link, then chats.
    const owner = await ownerLogsIn();
    const member = (await store.findOne("members", { email: OWNER }))!;
    expect(member.email_verified_at).toBeTruthy();
    expect(member.session_version).toBe(2); // the first verification revoked every earlier session
    expect((await asCookie(owner, currentMember))?.id).toBe(member.id);
    const ownerChat = await chatAs(owner, "OWNER-SECRET my knee hurts on the stairs");
    expect(ownerChat.status).toBe(200);

    // The payer's cookie is dead everywhere: no account, no chat, no purchase flow.
    expect(await asCookie(attack.cookie, currentMember)).toBeNull();
    expect(await asCookie(attack.cookie, currentPurchaser)).toBeNull();
    const again = await chatAs(attack.cookie, "what did I say earlier?");
    expect(again.status).toBe(401);
    expect(JSON.stringify(again.body)).not.toContain("OWNER-SECRET");
    const { POST: upsell } = await import("@/app/api/upsell/route");
    const f = new FormData();
    f.set("key", "kit");
    jar.cookie = attack.cookie!;
    expect((await upsell(new Request("http://localhost/api/upsell", { method: "POST", body: f }))).headers.get("location")).toMatch(/\/login$/);
  });

  it("R2-1: before anyone verifies, the checkout session can finish the upsells but not open chat, downloads or settings data", async () => {
    const a = await pay({});
    jar.cookie = a.cookie!;
    const { POST: upsell } = await import("@/app/api/upsell/route");
    const f = new FormData();
    f.set("key", "kit");
    const res = await upsell(new Request("http://localhost/api/upsell", { method: "POST", body: f }));
    expect(res.headers.get("location")).toMatch(/\/welcome$/);
    expect(await store.count("sy_orders", { kind: "upsell_kit" })).toBe(1);
    expect((await chatAs(a.cookie, "hi")).status).toBe(401);
    const { GET: download } = await import("@/app/api/downloads/[file]/route");
    const { ALL_DOWNLOAD_FILES } = await import("@/lib/products");
    const file = ALL_DOWNLOAD_FILES[0]!;
    const d = await download(new Request(`http://localhost/api/downloads/${file}`), { params: Promise.resolve({ file }) });
    expect(d.status).toBe(401);
  });

  it("R2-1: the purchase session is short-lived and its scope can't be edited", async () => {
    const a = await pay({});
    expect(a.setCookie).toMatch(new RegExp(`Max-Age=${PURCHASE_SESSION_MINUTES * 60}`));
    const payload = (await verifySession(a.cookie, env.sessionSecret))!;
    expect(payload.s).toBe("purchase");
    expect(payload.exp - Date.now() / 1000).toBeLessThanOrEqual(PURCHASE_SESSION_MINUTES * 60 + 1);
    // Dropping the scope breaks the signature.
    const [body] = a.cookie!.split(".");
    const forgedBody = Buffer.from(JSON.stringify({ ...payload, s: undefined })).toString("base64url");
    expect(await verifySession(`${forgedBody}.${a.cookie!.split(".")[1]}`, env.sessionSecret)).toBeNull();
    expect(body).not.toBe(forgedBody);
  });

  it("R2-1: a full-scope cookie for an unverified email (e.g. minted before this fix) opens nothing", async () => {
    await pay({});
    const m = (await store.findOne("members", { email: OWNER }))!;
    const legacy = await signSession({ mid: m.id, exp: Math.floor(Date.now() / 1000) + 86400, v: m.session_version }, env.sessionSecret);
    expect(await resolveSession(store, legacy, env.sessionSecret)).toBeNull();
    expect((await chatAs(legacy, "hi")).status).toBe(401);
  });

  it.each([
    ["founding (25 dollars)", { offer: "founding", arm: "B" } as Partial<StartCheckoutInput>],
    ["founding + bumps", { offer: "founding", arm: "B", bumps: ["reset", "kitchen"] } as Partial<StartCheckoutInput>],
    ["email trick (case, spaces, full-width)", { email: "  ＦＵＴＵＲＥ.Owner@EXAMPLE.com " } as Partial<StartCheckoutInput>],
  ])("R2-1 variant: %s → payer's session dies when the owner logs in", async (_n, input) => {
    const a = await pay(input);
    expect(await store.count("members")).toBe(1);
    await ownerLogsIn();
    expect(await asCookie(a.cookie, currentPurchaser)).toBeNull();
    expect((await chatAs(a.cookie, "hi")).status).toBe(401);
  });

  it("R2-1 variant: gift bought with the owner's unregistered email as the buyer → no account access; owner's login kills it", async () => {
    const a = await pay({ offer: "gift3", autoRenewConsent: false, gift: { recipient_name: "Al", recipient_email: "al@example.com", message: "", months: 3 } });
    expect(a.location).toMatch(/\/gift\/thanks$/);
    expect((await asCookie(a.cookie, currentPurchaser))?.scope).toBe("purchase");
    expect(await asCookie(a.cookie, currentMember)).toBeNull();
    await ownerLogsIn();
    expect(await asCookie(a.cookie, currentPurchaser)).toBeNull();
  });

  it("R2-1 variant: owner verifies by confirming their own purchase (not by login) → payer's session dies", async () => {
    const a = await pay({});
    // The owner buys too, not signed in: the account exists, so it's parked for inbox confirmation.
    const own = await pay({ offer: "founding", arm: "B", firstName: "Olive" }, "pm_owner");
    expect(own.location).toMatch(/\/checkout\/check-email$/);
    const m = (await store.findOne("members", { email: OWNER }))!;
    const { sendPurchaseVerification } = await import("@/lib/billing/verifyPurchase");
    const token = await sendPurchaseVerification(store, own.intentId, m, []);
    const { POST } = await import("@/app/api/checkout/verify/route");
    const f = new FormData();
    f.set("token", token);
    f.set("action", "confirm");
    const res = await POST(new Request("http://localhost/api/checkout/verify", { method: "POST", body: f }));
    const ownerCookie = cookieOf(res)!;
    expect((await asCookie(ownerCookie, currentMember))?.id).toBe(m.id);
    expect(await asCookie(a.cookie, currentPurchaser)).toBeNull();
  });

  it("R2-1 variant: owner verifies by claiming a gift sent to them → payer's session dies", async () => {
    const a = await pay({});
    const { token } = await createGift(store, { gifter: { email: "kid@example.com", first_name: "Kid" }, recipientName: "Owner", recipientEmail: OWNER, message: "", months: 3, amountCents: 6900 });
    const { POST } = await import("@/app/api/gift/claim/route");
    const f = new FormData();
    f.set("token", token);
    f.set("first_name", "Olive");
    f.set("age", "on");
    const res = await POST(new Request("http://localhost/api/gift/claim", { method: "POST", body: f }));
    expect(cookieOf(res)).toBeTruthy();
    expect(await asCookie(a.cookie, currentPurchaser)).toBeNull();
    expect((await asCookie(cookieOf(res), currentMember))?.email).toBe(OWNER);
  });

  it("R2-1: two login links opened at once bump the version once; later logins don't sign out other devices", async () => {
    const a = await pay({});
    const m = (await store.findOne("members", { email: OWNER }))!;
    const [x, y] = await Promise.all([markEmailVerified(store, m.id), markEmailVerified(store, m.id)]);
    expect(x!.session_version).toBe(2);
    expect(y!.session_version).toBe(2);
    expect(await asCookie(a.cookie, currentPurchaser)).toBeNull();
    const first = await ownerLogsIn();
    const second = await ownerLogsIn();
    expect((await asCookie(first, currentMember))?.id).toBe(m.id);
    expect((await asCookie(second, currentMember))?.id).toBe(m.id);
  });

  it("R2-1: the welcome email carries the one-time link that verifies the inbox (never stored in plain text)", async () => {
    await pay({});
    const mail = (await store.findOne("outbox", { template: "E1_welcome_terms" }))!;
    expect(mail.to).toBe(OWNER);
    expect(mail.body).toContain("confirm this is your email");
    expect(mail.body).not.toMatch(/token=[A-Za-z0-9_-]{10,}/);
    expect(await store.count("magic_links")).toBe(1);
  });

  it("R2-1: an already-verified member who buys while signed in keeps a full session", async () => {
    await pay({});
    const owner = await ownerLogsIn();
    const m = (await asCookie(owner, currentMember))!;
    const again = await pay({ offer: "founding", arm: "B", authMemberId: m.id }, "pm_owner2");
    expect((await asCookie(again.cookie, currentMember))?.id).toBe(m.id);
  });
});
