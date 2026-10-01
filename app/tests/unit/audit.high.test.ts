/**
 * Regression tests for AUDIT_CODE.md high findings in app/ (H1–H8, H11, H12).
 * H9 and H10 are in workers/ and n8n (outside app/).
 */
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { SupabaseStore } from "@/lib/db/supabase";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { fulfillCheckoutIntent } from "@/lib/billing/fulfill";
import { handleStripeEvent } from "@/lib/billing/webhook";
import { cancelMembership, refundMembership } from "@/lib/billing/actions";
import { braintreeProcessor, mockCheckoutAllowed, volume30d } from "@/lib/billing/processors";
import { entitlementFor, grantsAccess, pickBillingMembership } from "@/lib/entitlement";
import { applyGift, expireGifts, giftMembershipRow } from "@/lib/gifts";
import { mrrCents, upsertMember } from "@/lib/members";
import { computeKpis } from "@/lib/kpis";
import { testSignatureHeader } from "@/lib/billing/verify";
import type { Gift, Membership } from "@/lib/db/types";

const DAY = 86_400_000;
let store: MemoryStore;
const saved = { ...process.env };
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});
afterEach(() => {
  for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
  Object.assign(process.env, saved);
});

const base: StartCheckoutInput = {
  offer: "founding",
  arm: "B",
  gentle: false,
  email: "h@example.com",
  firstName: "Hal",
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

async function buy(input: Partial<StartCheckoutInput> = {}, sub = `sub_${crypto.randomUUID().slice(0, 6)}`) {
  const r = await startCheckout(store, { ...base, ...input });
  if (!r.ok) throw new Error(JSON.stringify(r.errors));
  await handleStripeEvent(store, {
    id: `evt_${crypto.randomUUID()}`,
    type: "checkout.session.completed",
    data: { object: { id: "cs", metadata: { intent_id: r.intentId }, payment_status: "paid", customer: "cus", subscription: sub, invoice: `in_${sub}`, payment_intent: null } },
  });
  return r.intentId;
}

function ms(p: Partial<Membership>): Membership {
  return {
    id: crypto.randomUUID(), member_id: "m", plan: "monthly", arm: "B", offer_code: "founding", price_cents: 2500, interval: "month", status: "active", founding: true,
    stripe_subscription_id: "sub_x", trial_end: null, current_period_end: new Date(Date.now() + 10 * DAY).toISOString(), first_paid_at: new Date().toISOString(),
    guarantee_until: null, cancel_at_period_end: false, canceled_at: null, paused_until: null, partner_seat: false, processor: "stripe", price_cell: null,
    checkout_intent_id: null, gift_credit_cents: 0, pending_verification: false, stripe_customer_id: null, is_demo: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), ...p,
  };
}

describe("H1 refunds are scoped to one membership", () => {
  it("H1: a returning member's refund covers only the new membership's charge", async () => {
    // Six months on an old membership...
    await buy({ email: "ret@example.com" }, "sub_old");
    const member = (await store.findOne("members", { email: "ret@example.com" }))!;
    const old = (await store.findOne("memberships", { stripe_subscription_id: "sub_old" }))!;
    for (let i = 0; i < 5; i++) {
      await store.insert("sy_orders", { member_id: member.id, membership_id: old.id, email: member.email, offer_code: "founding", kind: "membership_charge", description: "renewal", amount_cents: 2500, amount_refunded_cents: 0, status: "paid", stripe_payment_intent: `pi_old_${i}`, stripe_invoice: null, checkout_intent_id: null, processor: "stripe", is_demo: false });
    }
    await cancelMembership(store, old, null, null);
    await store.update("memberships", old.id, { status: "canceled", current_period_end: new Date(Date.now() - DAY).toISOString() });
    // ...then rejoins, and taps Refund in the new window.
    await buy({ email: "ret@example.com" }, "sub_new");
    const fresh = (await store.findOne("memberships", { stripe_subscription_id: "sub_new" }))!;
    const r = await refundMembership(store, fresh);
    expect(r.ok).toBe(true);
    expect(r.refundedCents).toBe(fresh.price_cents);
    expect(await store.count("sy_orders", { membership_id: old.id, status: "refunded" })).toBe(0);
  });
});

describe("H2 entitlement gate", () => {
  it("H2: refunded, expired, paused, ended and gift-purchaser-only accounts have no access", () => {
    const now = Date.now();
    expect(entitlementFor([], now)).toMatchObject({ access: false, reason: "none" });
    expect(entitlementFor([ms({ status: "refunded" })], now)).toMatchObject({ access: false, reason: "refunded" });
    expect(entitlementFor([ms({ status: "paused" })], now)).toMatchObject({ access: false, reason: "paused" });
    expect(entitlementFor([ms({ status: "expired" })], now).access).toBe(false);
    expect(entitlementFor([ms({ status: "canceled", current_period_end: new Date(now - DAY).toISOString() })], now).access).toBe(false);
    expect(entitlementFor([ms({ plan: "gift", status: "active", current_period_end: new Date(now - DAY).toISOString() })], now).access).toBe(false);
  });
  it("H2: active, trialing, past-due and cancelled-until-period-end keep access", () => {
    for (const s of ["active", "trialing", "past_due"] as const) expect(grantsAccess(ms({ status: s }))).toBe(true);
    expect(grantsAccess(ms({ status: "canceled", current_period_end: new Date(Date.now() + DAY).toISOString() }))).toBe(true);
  });
  it("H2: every members-area page, the chat API and downloads check entitlement", () => {
    const root = path.resolve(__dirname, "../../src/app");
    const gated = ["app/page.tsx", "app/progress/page.tsx", "app/retest/page.tsx", "app/kitchen/page.tsx", "app/programs/page.tsx", "app/printables/[slug]/page.tsx", "app/chat/page.tsx", "app/partner/page.tsx"];
    for (const f of gated) expect(readFileSync(path.join(root, f), "utf8"), f).toMatch(/requireEntitled\(\)/);
    // The downloads index is the one page a books-only buyer (cell A) may open: it checks entitlement per file instead.
    expect(readFileSync(path.join(root, "app/printables/page.tsx"), "utf8")).toMatch(/entitlement\(member\.id\)/);
    expect(readFileSync(path.join(root, "api/chat/route.ts"), "utf8")).toMatch(/entitlement\(member\.id\)/);
    expect(readFileSync(path.join(root, "api/downloads/[file]/route.ts"), "utf8")).toMatch(/entitlement\(member\.id\)/);
  });
});

describe("H3 gifts never hijack billing", () => {
  it("H3: cancel targets the paying membership even when a newer gift row exists", () => {
    const paid = ms({ created_at: new Date(Date.now() - 20 * DAY).toISOString() });
    const gift = ms({ plan: "gift", stripe_subscription_id: null, price_cents: 0, interval: "none", created_at: new Date().toISOString() });
    expect(pickBillingMembership([gift, paid])!.id).toBe(paid.id);
  });
  it("H3: a gift for a new member starts a gift; for a gifted member extends it; gifts expire in every mode", async () => {
    const member = await upsertMember(store, { email: "g@example.com", firstName: "G" });
    const gift = { id: "g1", gifter_name: "Kid", months: 3, amount_cents: 4900 } as Gift;
    expect(await applyGift(store, member, gift)).toBe("gift_membership");
    expect(await applyGift(store, member, { ...gift, id: "g2" })).toBe("extension");
    const row = (await store.findOne("memberships", { member_id: member.id }))!;
    expect(new Date(row.current_period_end!).getTime()).toBeGreaterThan(Date.now() + 170 * DAY);
    await store.insert("memberships", { ...giftMembershipRow(member.id, { months: 3 }), current_period_end: new Date(Date.now() - 1000).toISOString() });
    expect(await expireGifts(store)).toBe(1);
  });
});

describe("H4/H5 fail closed", () => {
  it("H4: text CANCEL is refused without SMS_ENABLED and a Twilio token", async () => {
    const { POST } = await import("@/app/api/sms/inbound/route");
    const body = "From=%2B15555550123&Body=CANCEL";
    const req = () => new Request("http://localhost/api/sms/inbound", { method: "POST", body, headers: { "content-type": "application/x-www-form-urlencoded" } });
    delete process.env.TWILIO_AUTH_TOKEN;
    process.env.SMS_ENABLED = "true";
    expect((await POST(req())).status).toBe(403);
    process.env.TWILIO_AUTH_TOKEN = "tok";
    process.env.SMS_ENABLED = "false";
    expect((await POST(req())).status).toBe(403);
    process.env.SMS_ENABLED = "true";
    expect((await POST(req())).status).toBe(403); // no signature
  });

  it("H5: the webhook refuses events when the secret is missing, unless DEV_ALLOW_UNSIGNED", async () => {
    const { POST } = await import("@/app/api/stripe/webhook/route");
    const payload = JSON.stringify({ id: "evt_forged", type: "customer.subscription.deleted", livemode: false, data: { object: { id: "sub_x" } } });
    process.env.STRIPE_SECRET_KEY = "sk_test_x";
    delete process.env.STRIPE_WEBHOOK_SECRET;
    delete process.env.DEV_ALLOW_UNSIGNED;
    const r1 = await POST(new Request("http://localhost/api/stripe/webhook", { method: "POST", body: payload, headers: { "stripe-signature": testSignatureHeader(payload, "") } }));
    expect(r1.status).toBe(500);
    expect(await store.count("stripe_events")).toBe(0);
    process.env.DEV_ALLOW_UNSIGNED = "true";
    const r2 = await POST(new Request("http://localhost/api/stripe/webhook", { method: "POST", body: payload }));
    expect(r2.status).toBe(200);
    process.env.STRIPE_WEBHOOK_SECRET = "whsec_real";
    const r3 = await POST(new Request("http://localhost/api/stripe/webhook", { method: "POST", body: payload, headers: { "stripe-signature": testSignatureHeader(payload, "") } }));
    expect(r3.status).toBe(400);
  });
});

describe("H6 the Braintree simulator never serves real buyers", () => {
  it("H6: simulator only with no live Stripe key and outside production", () => {
    process.env.BRAINTREE_ENABLED = "true";
    delete process.env.STRIPE_SECRET_KEY;
    expect(braintreeProcessor.status()).toBe("mock");
    process.env.STRIPE_SECRET_KEY = "sk_test_live_account_in_test_mode";
    expect(braintreeProcessor.status()).toBe("off");
    expect(mockCheckoutAllowed()).toBe(false);
    delete process.env.STRIPE_SECRET_KEY;
    process.env.VERCEL_ENV = "production";
    expect(braintreeProcessor.status()).toBe("off");
    expect(mockCheckoutAllowed()).toBe(false);
  });
});

describe("H7 no 1,000-row cap", () => {
  it("H7: SupabaseStore.find pages through every row", async () => {
    const rows = Array.from({ length: 2500 }, (_, i) => ({ id: String(i), amount_cents: 100 }));
    const s = new SupabaseStore("http://localhost:54321", "service-key");
    const ranges: [number, number][] = [];
    const builder = () => {
      const q = {
        select: () => q,
        order: () => q,
        eq: () => q,
        limit: () => Promise.resolve({ data: rows.slice(0, 5), error: null }),
        range: (a: number, b: number) => {
          ranges.push([a, b]);
          return Promise.resolve({ data: rows.slice(a, Math.min(b + 1, 1000 * (ranges.length) )).slice(0, 1000), error: null });
        },
      };
      return q;
    };
    (s as unknown as { client: unknown }).client = { from: builder };
    const all = await s.find("sy_orders");
    expect(all).toHaveLength(2500);
    expect(ranges).toEqual([[0, 999], [1000, 1999], [2000, 2999]]);
  });
  it("H7: processor volume uses one SQL sum when the store supports it", async () => {
    const calls: string[] = [];
    const fake = { ...store, rpc: async (fn: string) => (calls.push(fn), 123_456), find: async () => [] } as unknown as MemoryStore;
    expect(await volume30d(fake, "stripe")).toBe(123_456);
    expect(calls).toEqual(["processor_volume_cents"]);
  });
});

describe("H8 fulfilment runs once", () => {
  it("H8: the success redirect and the webhook racing create one membership and one set of orders", async () => {
    const r = await startCheckout(store, { ...base, email: "race@example.com", bumps: ["reset"] });
    if (!r.ok) throw new Error("checkout");
    const [a, b] = await Promise.all([
      fulfillCheckoutIntent(store, r.intentId, { stripeSubscriptionId: "sub_race" }),
      fulfillCheckoutIntent(store, r.intentId, { stripeSubscriptionId: "sub_race" }),
    ]);
    expect([a.alreadyDone, b.alreadyDone].sort()).toEqual([false, true]);
    expect(await store.count("memberships")).toBe(1);
    expect(await store.count("sy_orders")).toBe(2);
    expect(await store.count("outbox", { template: "E1_welcome_terms" })).toBe(1);
    const k = await computeKpis(store);
    expect(k.mrrCents).toBe(a.membership?.price_cents ?? b.membership!.price_cents);
  });
  it("H8: the database enforces one membership per intent and one order line per intent", () => {
    const sql = readFileSync(path.resolve(__dirname, "../../supabase/migrations/20260930120000_audit_fixes.sql"), "utf8");
    expect(sql).toMatch(/memberships_intent_uniq on public\.memberships \(checkout_intent_id\)/);
    expect(sql).toMatch(/sy_orders_intent_line_uniq on public\.sy_orders \(checkout_intent_id, kind, offer_code\)/);
  });
});

describe("H11 no table-name collision with the pipeline schema", () => {
  it("H11: the app's orders table is sy_orders everywhere", () => {
    const dir = path.resolve(__dirname, "../../supabase/migrations");
    const sql = readdirSync(dir).map((f) => readFileSync(path.join(dir, f), "utf8")).join("\n");
    expect(sql).toMatch(/create table if not exists public\.sy_orders/);
    expect(sql).not.toMatch(/public\.orders\b/);
  });
});

describe("H12 external refunds and disputes update the membership", () => {
  it("H12: a full dashboard refund ends the membership; a partial one doesn't", async () => {
    await buy({ email: "d1@example.com" }, "sub_d1");
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_d1" }))!;
    await store.updateWhere("sy_orders", { membership_id: m.id }, { stripe_payment_intent: "pi_d1" });
    await handleStripeEvent(store, { id: "evt_p", type: "charge.refunded", data: { object: { payment_intent: "pi_d1", refunded: false, amount_refunded: 500 } } });
    expect((await store.get("memberships", m.id))!.status).toBe("active");
    await handleStripeEvent(store, { id: "evt_f", type: "charge.refunded", data: { object: { payment_intent: "pi_d1", refunded: true, amount_refunded: m.price_cents } } });
    expect((await store.get("memberships", m.id))!.status).toBe("refunded");
  });
  it("H12: a dispute cancels at once and flags the member", async () => {
    await buy({ email: "d2@example.com" }, "sub_d2");
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_d2" }))!;
    await store.updateWhere("sy_orders", { membership_id: m.id }, { stripe_payment_intent: "pi_d2" });
    await handleStripeEvent(store, { id: "evt_dp", type: "charge.dispute.created", data: { object: { payment_intent: "pi_d2" } } });
    expect((await store.get("memberships", m.id))!.status).toBe("canceled");
    expect(await store.count("support_tickets", { reason: "dispute" })).toBe(1);
  });
  it("H12: MRR excludes scheduled cancellations and reports them separately", async () => {
    expect(mrrCents(ms({ cancel_at_period_end: true }))).toBe(0);
    await buy({ email: "c@example.com" }, "sub_c");
    const m = (await store.findOne("memberships", { stripe_subscription_id: "sub_c" }))!;
    await cancelMembership(store, m, null, null);
    const k = await computeKpis(store);
    expect(k.mrrCents).toBe(0);
    expect(k.scheduledChurnCents).toBe(m.price_cents);
  });
});
