/**
 * Lifecycle engine (consent, RFC 8058 headers, quiet hours, 1/day cap, idempotency, owned steps)
 * and affiliates (apply → exception → approve → code; 30% x 12 months; 60-day link window; no self-referral; CSV).
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { runLifecycle, SEQUENCES, unsubscribe, unsubscribeToken, verifyUnsubscribe } from "@/lib/lifecycle/engine";
import { applyAffiliate, creditAffiliateOrder, monthlyStatement, statementCsv } from "@/lib/affiliates";
import { decideException } from "@/lib/exceptions";
import type { EmailInput } from "@/lib/notify";

let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
  vi.stubEnv("LAUNCH_MODE", "live");
});
afterEach(() => vi.unstubAllEnvs());

async function member(email: string, startIso: string) {
  const m = await store.insert("members", { email, first_name: "Ruth", timezone: "America/New_York", is_demo: false } as never);
  const ms = await store.insert("memberships", { member_id: m.id, plan: "monthly", status: "active", price_cents: 2500, interval: "month", founding: true, first_paid_at: startIso, current_period_end: "2026-12-01T00:00:00Z", cancel_at_period_end: false, processor: "stripe", pending_verification: false, is_demo: false } as never);
  return { m, ms };
}

describe("lifecycle engine", () => {
  it("sends the due onboarding step once, with one-click unsubscribe headers, inside quiet hours rules and the daily cap", async () => {
    await member("ruth@example.com", "2026-10-01T13:00:00Z");
    const sent: EmailInput[] = [];
    const send = async (i: EmailInput) => void sent.push(i);
    // 03:00 ET: quiet hours, nothing goes.
    expect((await runLifecycle(store, new Date("2026-10-02T07:00:00Z"), send)).sent).toBe(0);
    // 10:00 ET next day: day-1 onboarding.
    const r = await runLifecycle(store, new Date("2026-10-02T14:00:00Z"), send);
    expect(r.sent).toBe(1);
    expect(sent[0]!.template).toBe("LC_member_onboarding_d1");
    expect(sent[0]!.headers?.["List-Unsubscribe-Post"]).toBe("List-Unsubscribe=One-Click");
    expect(sent[0]!.headers?.["List-Unsubscribe"]).toMatch(/^<https?:\/\/.+\/api\/unsubscribe\?e=.+&t=.+>$/);
    // Same hour again: idempotent. Two hours later: capped (1/day), not duplicated.
    expect((await runLifecycle(store, new Date("2026-10-02T14:30:00Z"), send)).sent).toBe(0);
    expect(sent).toHaveLength(1);
  });

  it("unsubscribe stops lifecycle mail; transactional failed-payment notices still go, without unsubscribe headers", async () => {
    const { ms } = await member("ann@example.com", "2026-09-01T13:00:00Z");
    await store.update("memberships", ms.id, { status: "past_due", grace_until: "2026-10-08T00:00:00Z" });
    await unsubscribe(store, "ann@example.com", "test");
    const sent: EmailInput[] = [];
    await runLifecycle(store, new Date("2026-10-02T14:00:00Z"), async (i) => void sent.push(i));
    expect(sent.map((s) => s.template)).toEqual(["LC_failed_payment_f1"]);
    expect(sent[0]!.headers).toBeUndefined();
    expect(verifyUnsubscribe("ann@example.com", unsubscribeToken("ann@example.com"))).toBe(true);
    expect(verifyUnsubscribe("ann@example.com", "forged")).toBe(false);
  });

  it("owned steps (the orders/paid welcome) are recorded, never sent; the coach email needs its own opt-in", async () => {
    await member("bo@example.com", "2026-10-02T13:00:00Z");
    const sent: EmailInput[] = [];
    await runLifecycle(store, new Date("2026-10-02T14:00:00Z"), async (i) => void sent.push(i));
    expect(sent).toHaveLength(0);
    expect((await store.find("email_sends", { email: "bo@example.com" })).map((r) => `${r.step}:${r.status}`)).toEqual([expect.stringMatching(/^d0:.+:skipped$/)]);
    expect(SEQUENCES.sequences.daily_coach!.kind).toBe("marketing");
  });
});

describe("affiliates", () => {
  async function approved(email = "aff@example.com") {
    const a = await applyAffiliate(store, { email, name: "Grace Lee", channel: "youtube.com/@grace", audience: "60+", ftcAck: true, termsAck: true });
    if (!a.ok) throw new Error("apply failed");
    expect(a.affiliate.status).toBe("pending");
    const res = await decideException(store, { id: a.affiliate.exception_id!, decision: "approve", actor: "garrison" });
    expect(res.ok).toBe(true);
    return (await store.get("affiliates", a.affiliate.id))!;
  }

  it("needs the FTC acknowledgement; approval via the exceptions queue assigns a code", async () => {
    const bad = await applyAffiliate(store, { email: "x@example.com", name: "X Y", channel: "blog.example", audience: "", ftcAck: false, termsAck: true });
    expect(bad).toEqual({ ok: false, errors: ["ftc"] });
    const a = await approved();
    expect(a.status).toBe("approved");
    expect(a.code).toMatch(/^GRACELEE\d{2}$/);
  });

  it("credits 30% for 12 months by code or a link within 60 days, blocks self-referral, and writes a CSV", async () => {
    const a = await approved();
    const buyer = await store.insert("members", { email: "ruth@example.com", first_name: "Ruth", is_demo: false } as never);
    const line = await store.insert("sy_orders", { member_id: buyer.id, email: "ruth@example.com", kind: "membership_charge", status: "paid", amount_cents: 2500, amount_refunded_cents: 0, shopify_order_id: "o1", offer_code: "founding_monthly", is_demo: false } as never);
    const paidAt = new Date("2026-10-05T12:00:00Z");
    // Link older than 60 days: no credit.
    const stale = { utm_source: "affiliate", utm_campaign: a.code!, first_seen_at: "2026-07-01T00:00:00Z" };
    expect((await creditAffiliateOrder(store, { memberId: buyer.id, email: "ruth@example.com", shopifyOrderId: "o1", discountCodes: [], attribution: stale, renewal: false, paidAt })).commissions).toBe(0);
    // Fresh link: credited, 30%.
    const fresh = { ...stale, first_seen_at: "2026-09-20T00:00:00Z" };
    expect((await creditAffiliateOrder(store, { memberId: buyer.id, email: "ruth@example.com", shopifyOrderId: "o1", discountCodes: [], attribution: fresh, renewal: false, paidAt })).commissions).toBe(1);
    expect((await store.findOne("affiliate_commissions", { sy_order_id: line.id }))?.commission_cents).toBe(750);
    // Replay: nothing new.
    expect((await creditAffiliateOrder(store, { memberId: buyer.id, email: "ruth@example.com", shopifyOrderId: "o1", discountCodes: [], attribution: fresh, renewal: false, paidAt })).commissions).toBe(0);
    // Renewal 13 months later: outside the window.
    await store.insert("sy_orders", { member_id: buyer.id, email: "ruth@example.com", kind: "membership_charge", status: "paid", amount_cents: 2500, amount_refunded_cents: 0, shopify_order_id: "o2", offer_code: "founding_monthly", is_demo: false } as never);
    expect((await creditAffiliateOrder(store, { memberId: buyer.id, email: "ruth@example.com", shopifyOrderId: "o2", discountCodes: [], attribution: null, renewal: true, paidAt: new Date("2027-11-06T00:00:00Z") })).reason).toBe("outside 12 months");
    // Self-referral by code: blocked and flagged.
    const self = await store.insert("members", { email: "aff@example.com", first_name: "Grace", is_demo: false } as never);
    expect((await creditAffiliateOrder(store, { memberId: self.id, email: "aff@example.com", shopifyOrderId: "o3", discountCodes: [a.code!], attribution: null, renewal: false, paidAt })).reason).toBe("self-referral");
    expect(await store.count("exceptions", { type: "affiliate_fraud" })).toBe(1);
    // Statement: held inside the 14-day window, payable after; refunded lines reversed.
    const held = await monthlyStatement(store, "2026-10", new Date("2026-10-10T00:00:00Z"));
    expect(held.map((l) => l.state)).toEqual(["held"]);
    const csv = statementCsv(await monthlyStatement(store, "2026-10", new Date("2026-11-01T00:00:00Z")));
    expect(csv.split("\n")[0]).toBe("affiliate_code,affiliate_name,shopify_order_id,paid_at,base_usd,commission_usd,state");
    expect(csv).toContain("7.50,payable");
    await store.update("sy_orders", line.id, { status: "refunded" });
    expect((await monthlyStatement(store, "2026-10"))[0]!.state).toBe("reversed");
  });
});
