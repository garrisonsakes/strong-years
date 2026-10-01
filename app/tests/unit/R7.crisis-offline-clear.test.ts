/**
 * Round 7 (AUDIT_FINAL §6, C2 residuals):
 *  1. the "model required" guard covers every non-local deploy (NODE_ENV based);
 *  2. a model outage takes the chat fully offline for new messages: 988, 911,
 *     Eldercare Locator and a human, and never a rules-only coach reply;
 *  3. "That's not what I meant": after the resources are shown, the member can
 *     clear a benign phrase that tripped the rules; the alert and log stay.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const jar = vi.hoisted(() => ({ cookie: undefined as string | undefined }));
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: (n: string) => (n === "sy_session" && jar.cookie ? { name: n, value: jar.cookie } : undefined) }),
  headers: async () => ({ get: () => null }),
}));
const sdk = vi.hoisted(() => ({ calls: [] as { body: { max_tokens: number }; opts: { timeout?: number; maxRetries?: number } }[] }));
vi.mock("@anthropic-ai/sdk", () => ({
  default: class {
    messages = {
      create: async (body: { max_tokens: number }, opts: { timeout?: number; maxRetries?: number }) => {
        sdk.calls.push({ body, opts });
        throw new Error("529 overloaded");
      },
    };
  },
}));

import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { CLASSIFIER_TIMEOUT_MS, CLEAR_WINDOW_MS, clearCrisisFlag, handleChatTurn, setClassifierModelForTests, setReplyModelForTests, stubReply } from "@/lib/ai/chat";
import { env } from "@/lib/config";
import { upsertMember } from "@/lib/members";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { markEmailVerified, signMemberSession } from "@/lib/auth/verification";
import type { Member } from "@/lib/db/types";

const penv = process.env as Record<string, string | undefined>;
const saved = { ...process.env };
let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  jar.cookie = undefined;
  sdk.calls.length = 0;
});
afterEach(() => {
  setClassifierModelForTests(null);
  setReplyModelForTests(null);
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

/** A deployed build (NODE_ENV=production), not on Vercel, no demo override. */
function deployed(extra: Record<string, string> = {}) {
  penv.NODE_ENV = "production";
  delete penv.VERCEL_ENV;
  delete penv.ALLOW_RULES_ONLY_CHAT;
  delete penv.ANTHROPIC_API_KEY;
  Object.assign(penv, extra);
}

const member = () => upsertMember(store, { email: "rose@example.com", firstName: "Rose", ageConfirmed: true });

const HELP = [/\b988\b/, /\b911\b/, /Eldercare Locator at 1-800-677-1116/, /Talk to a human/];

describe("R7: the model-required guard covers every non-local deploy", () => {
  it.each([
    ["NODE_ENV=production (any host)", { NODE_ENV: "production" }, true],
    ["Vercel preview", { NODE_ENV: "production", VERCEL_ENV: "preview" }, true],
    ["Vercel production", { NODE_ENV: "production", VERCEL_ENV: "production" }, true],
    ["NODE_ENV unset (custom server)", { NODE_ENV: "" }, true],
    ["demo override on Vercel production is ignored", { NODE_ENV: "production", VERCEL_ENV: "production", ALLOW_RULES_ONLY_CHAT: "true" }, true],
    ["demo override with real data (Supabase) is ignored", { NODE_ENV: "production", ALLOW_RULES_ONLY_CHAT: "true", SUPABASE_URL: "https://x.supabase.co", SUPABASE_SERVICE_ROLE_KEY: "k" }, true],
    ["in-memory demo build with the explicit override (e2e servers)", { NODE_ENV: "production", ALLOW_RULES_ONLY_CHAT: "true" }, false],
    ["next dev", { NODE_ENV: "development" }, false],
    ["vitest", { NODE_ENV: "test" }, false],
  ] as const)("R7 guard: %s → requires model = %s", (_n, vars, expected) => {
    for (const k of ["VERCEL_ENV", "ALLOW_RULES_ONLY_CHAT", "SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]) delete penv[k];
    for (const [k, v] of Object.entries(vars)) {
      if (v === "") delete penv[k];
      else penv[k] = v;
    }
    expect(env.chatRequiresModel).toBe(expected);
  });
});

describe("R7: model outage → chat offline, never a rules-only reply", () => {
  const RULE_MISSED = [
    "I think this is my last week. I've made my peace",
    "I sat in the garage with the engine running yesterday",
    "Everyone would be relieved if I was dead",
    "the caregiver slaps my hands when I'm slow to eat",
  ];

  it.each(RULE_MISSED)("R7 outage: rule-missed crisis %j → offline resources, a person reads it, no coach reply", async (text) => {
    deployed();
    const m = await member();
    const res = await handleChatTurn(store, m, "chang", text);
    expect(res.safety).toBe("offline");
    for (const re of HELP) expect(res.reply.content).toMatch(re);
    expect(res.reply.content).not.toBe(stubReply("chang", text, m));
    expect(await store.count("support_tickets", { reason: "chat_offline_review", member_id: m.id })).toBe(1);
    expect(await store.count("chat_messages", { member_id: m.id, role: "assistant", safety: null })).toBe(0);
  });

  it("R7 outage: ordinary questions are not answered by rules either; the on-call is paged once per hour", async () => {
    deployed();
    const m = await member();
    for (const t of ["What's a good protein breakfast?", "my knee hurts on the stairs", "Can I take ibuprofen?"]) {
      const res = await handleChatTurn(store, m, "sun", t);
      expect(res.safety).toBe("offline");
    }
    expect(await store.count("chat_messages", { member_id: m.id, role: "assistant", safety: null })).toBe(0);
    expect(await store.count("chat_messages", { member_id: m.id, role: "assistant", safety: "offline" })).toBe(3);
    expect(await store.count("outbox", { channel: "alert" })).toBe(1);
  });

  it("R7 outage: a crisis the rules DO catch still gets the crisis response and an alert", async () => {
    deployed();
    const m = await member();
    const res = await handleChatTurn(store, m, "chang", "i want to kill myself");
    expect(res.safety).toBe("crisis");
    expect(res.reply.content).toMatch(/988/);
    expect(await store.count("crisis_events")).toBe(1);
  });

  it("R7 outage: the classifier answers but the reply model fails → offline, not a scripted stub", async () => {
    deployed();
    setClassifierModelForTests(async () => '{"category":"none","confidence":0.97}');
    setReplyModelForTests(async () => null);
    const m = await member();
    const res = await handleChatTurn(store, m, "chang", "How many squats should I do?");
    expect(res.safety).toBe("offline");
  });

  it("R7 outage: with a key but the API down, the classifier gets one short attempt (no retries, ≤3 s) and the chat goes offline", async () => {
    deployed({ ANTHROPIC_API_KEY: "sk-ant-test-placeholder" });
    const m = await member();
    const res = await handleChatTurn(store, m, "chang", "What should I eat before a walk?");
    expect(res.safety).toBe("offline");
    const cls = sdk.calls.filter((c) => c.body.max_tokens === 60);
    expect(cls).toHaveLength(1);
    expect(cls[0]!.opts.maxRetries).toBe(0);
    expect(cls[0]!.opts.timeout).toBe(CLASSIFIER_TIMEOUT_MS);
    expect(CLASSIFIER_TIMEOUT_MS).toBeLessThanOrEqual(3000);
    // No coach reply was even attempted after the classifier failed.
    expect(sdk.calls.filter((c) => c.body.max_tokens === 400)).toHaveLength(0);
  });

  it("R7: the in-memory demo build (explicit override) and local dev keep scripted replies", async () => {
    deployed({ ALLOW_RULES_ONLY_CHAT: "true" });
    const m = await member();
    expect((await handleChatTurn(store, m, "chang", "my knee hurts on the stairs")).safety).toBeNull();
    penv.NODE_ENV = "test";
    expect((await handleChatTurn(store, m, "chang", "my back is stiff")).safety).toBeNull();
  });
});

describe("R7: \"That's not what I meant\"", () => {
  const IDIOMS = [
    "My son took my car in for new tires",
    "I don't want to wake up at 5 anymore",
    "I blacked out the date on the calendar",
    "I'd rather die than eat Sun's kimchi again haha",
    "I can't breathe well in the wildfire smoke",
  ];

  it.each(IDIOMS)("R7 clear: %j → resources shown first, then the member clears it and gets a normal answer; the alert stays", async (text) => {
    const m = await member();
    const first = await handleChatTurn(store, m, "chang", text);
    expect(first.safety).toBe("crisis");
    expect(first.reply.content).toMatch(/911|988/);
    const event = (await store.findOne("crisis_events", { member_id: m.id }))!;
    expect(event.reply_message_id).toBe(first.reply.id);
    expect(event.alerted).toBe(true);

    const cleared = await clearCrisisFlag(store, m, first.reply.id);
    expect(cleared.ok).toBe(true);
    if (!cleared.ok) return;
    expect(cleared.reply.safety).toBeNull();
    expect(cleared.reply.content).toMatch(/^Thanks for telling me/);
    const after = (await store.get("crisis_events", event.id))!;
    expect(after.member_cleared_at).toBeTruthy();
    expect(after.alerted).toBe(true); // the log and the page to on-call are kept
    expect(await store.count("support_tickets", { member_id: m.id, reason: "crisis_followup" })).toBe(1);
    expect((await store.get("chat_messages", event.chat_message_id!))!.safety).toMatch(/^cleared:/);
    // The resources reply is still in the history.
    expect((await store.get("chat_messages", first.reply.id))!.safety).toMatch(/^crisis:/);
  });

  it("R7 clear: works once (two taps racing → one answer), and only for the member's own resources reply", async () => {
    const m = await member();
    const other = await upsertMember(store, { email: "sam@example.com", firstName: "Sam", ageConfirmed: true });
    const first = await handleChatTurn(store, m, "chang", "I'd rather die than eat Sun's kimchi again haha");
    expect(await clearCrisisFlag(store, other, first.reply.id)).toEqual({ ok: false, reason: "not_found" });
    const [a, b] = await Promise.all([clearCrisisFlag(store, m, first.reply.id), clearCrisisFlag(store, m, first.reply.id)]);
    expect([a.ok, b.ok].filter(Boolean)).toHaveLength(1);
    expect(await clearCrisisFlag(store, m, first.reply.id)).toEqual({ ok: false, reason: "already_cleared" });
  });

  it("R7 clear: nothing to clear unless resources were shown (ordinary reply, user message id, unknown id)", async () => {
    const m = await member();
    const normal = await handleChatTurn(store, m, "chang", "my knee hurts on the stairs");
    expect((await clearCrisisFlag(store, m, normal.reply.id)).ok).toBe(false);
    const crisis = await handleChatTurn(store, m, "chang", "I blacked out the date on the calendar");
    const ev = (await store.findOne("crisis_events", { member_id: m.id }))!;
    expect((await clearCrisisFlag(store, m, ev.chat_message_id!)).ok).toBe(false);
    expect((await clearCrisisFlag(store, m, "nope")).ok).toBe(false);
    expect(crisis.safety).toBe("crisis");
  });

  it("R7 clear: expires after 24 hours", async () => {
    const m = await member();
    const first = await handleChatTurn(store, m, "chang", "I blacked out the date on the calendar");
    const later = new Date(Date.now() + CLEAR_WINDOW_MS + 60_000);
    expect(await clearCrisisFlag(store, m, first.reply.id, later)).toEqual({ ok: false, reason: "expired" });
  });

  it("R7 clear: a model confident it IS a crisis keeps the resources up (no coach reply)", async () => {
    deployed();
    setClassifierModelForTests(async () => '{"category":"self_harm","confidence":0.95}');
    const m = await member();
    const first = await handleChatTurn(store, m, "chang", "I don't want to wake up at 5 anymore");
    const r = await clearCrisisFlag(store, m, first.reply.id);
    expect(r.ok && r.safety).toBe("kept");
    if (r.ok) expect(r.reply.content).toMatch(/988/);
    const ev = (await store.findOne("crisis_events", { member_id: m.id }))!;
    expect((await store.get("chat_messages", ev.chat_message_id!))!.safety).toMatch(/^flagged:/);
  });

  it("R7 clear: a confident 'none' from the model lets the coach answer on a real deploy", async () => {
    deployed();
    setClassifierModelForTests(async () => '{"category":"none","confidence":0.95}');
    setReplyModelForTests(async () => "Sun's kimchi is strong. Let's get your legs strong too.");
    const m = await member();
    const first = await handleChatTurn(store, m, "sun", "I'd rather die than eat Sun's kimchi again haha");
    expect(first.safety).toBe("crisis"); // a definite rule hit always shows the resources first
    const r = await clearCrisisFlag(store, m, first.reply.id);
    expect(r.ok && r.reply.content).toMatch(/kimchi is strong/);
  });

  it("R7 clear: during an outage the clear is recorded but the answer is the offline message", async () => {
    deployed();
    const m = await member();
    const first = await handleChatTurn(store, m, "chang", "I can't breathe well in the wildfire smoke");
    const r = await clearCrisisFlag(store, m, first.reply.id);
    expect(r.ok && r.safety).toBe("offline");
    if (r.ok) for (const re of HELP) expect(r.reply.content).toMatch(re);
    expect((await store.findOne("crisis_events", { member_id: m.id }))!.member_cleared_at).toBeTruthy();
  });

  it("R7 clear: the cleared message no longer feeds the context window", async () => {
    const m = await member();
    const first = await handleChatTurn(store, m, "chang", "I have a bottle of sleeping pills in the drawer for my trip");
    if (first.safety === "crisis") await clearCrisisFlag(store, m, first.reply.id);
    const next = await handleChatTurn(store, m, "chang", "What's a good protein breakfast?");
    expect(next.safety).toBeNull();
  });
});

describe("R7: routes", () => {
  async function entitledMember(): Promise<{ m: Member; cookie: string }> {
    const input: StartCheckoutInput = { offer: "trial", arm: "A", gentle: false, email: "ruth@example.com", firstName: "Ruth", phone: "", smsConsent: false, autoRenewConsent: true, ageConsent: true, gift: null, attribution: null, leadId: null, ip: null, userAgent: null };
    const r = await startCheckout(store, input);
    if (!r.ok) throw new Error("checkout");
    await handleStripeEvent(store, { id: `evt_${r.intentId}`, type: "checkout.session.completed", data: { object: { metadata: { intent_id: r.intentId, payment_method: "pm_r" }, payment_status: "paid", customer: "cus_r", subscription: "sub_r" } } });
    const m = (await markEmailVerified(store, (await store.findOne("members", { email: "ruth@example.com" }))!.id))!;
    return { m, cookie: await signMemberSession(m, "full", env.sessionSecret) };
  }
  const post = async (path: string, body: unknown) => {
    const mod = path === "/api/chat" ? await import("@/app/api/chat/route") : await import("@/app/api/chat/clear/route");
    const res = await mod.POST(new Request(`http://localhost${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }));
    return { status: res.status, body: (await res.json()) as { reply?: { id: string; content: string; clearable?: boolean }; offline?: boolean; safety?: string } };
  };

  it("R7 route: a deployed build with no model key answers 200 offline (resources), not a stub and not a 503", async () => {
    const { cookie } = await entitledMember();
    deployed();
    jar.cookie = cookie;
    const r = await post("/api/chat", { character: "chang", text: "my knee hurts on the stairs" });
    expect(r.status).toBe(200);
    expect(r.body.offline).toBe(true);
    for (const re of HELP) expect(r.body.reply!.content).toMatch(re);
  });

  it("R7 route: crisis reply is marked clearable; /api/chat/clear answers it once", async () => {
    const { cookie } = await entitledMember();
    jar.cookie = cookie;
    const first = await post("/api/chat", { character: "sun", text: "I'd rather die than eat Sun's kimchi again haha" });
    expect(first.body.safety).toBe("crisis");
    expect(first.body.reply!.clearable).toBe(true);
    const cleared = await post("/api/chat/clear", { messageId: first.body.reply!.id });
    expect(cleared.status).toBe(200);
    expect(cleared.body.reply!.content).toMatch(/^Thanks for telling me/);
    expect((await post("/api/chat/clear", { messageId: first.body.reply!.id })).status).toBe(409);
    jar.cookie = undefined;
    expect((await post("/api/chat/clear", { messageId: first.body.reply!.id })).status).toBe(401);
  });
});
