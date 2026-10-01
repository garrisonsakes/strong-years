/**
 * Ops round: exceptions queue (validation, dedupe, decisions + audit, boost approval → governor record,
 * ticket mirroring), /admin/today numbers with the workers growth API mocked, and the idempotent 7am digest.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { decideException, parseException, raiseException, syncAppExceptions } from "@/lib/exceptions";
import { computeToday, fetchWorkerSummary } from "@/lib/today";
import { easternDayAndHour, runDigest } from "@/lib/digest";
import { POST as postException } from "@/app/api/exceptions/route";

let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});
afterEach(() => vi.unstubAllEnvs());

const TOKEN = "x".repeat(40);
const boost = { type: "boost_approval", title: "Boost S151 on @changyin", source: "growth", ref: "post-S151", dedupe_key: "boost:b1", payload: { boost_id: "b1", requested_daily_usd: 50 } };

describe("exceptions queue", () => {
  it("validates worker items and requires boost fields", () => {
    expect(parseException({ type: "nope", title: "x" }).ok).toBe(false);
    expect(parseException({ type: "boost_approval", title: "x" }).ok).toBe(false);
    const ok = parseException(boost);
    expect(ok.ok).toBe(true);
  });

  it("POST /api/exceptions: 404 without a token, 401 with a wrong one, 201 then 200 (idempotent)", async () => {
    const req = (auth: string) => new Request("http://localhost/api/exceptions", { method: "POST", headers: { authorization: auth, "content-type": "application/json", "x-forwarded-for": "10.0.0.1" }, body: JSON.stringify(boost) });
    expect((await postException(req(`Bearer ${TOKEN}`))).status).toBe(404);
    vi.stubEnv("EXCEPTIONS_API_TOKEN", TOKEN);
    expect((await postException(req("Bearer wrong"))).status).toBe(401);
    expect((await postException(req(`Bearer ${TOKEN}`))).status).toBe(201);
    expect((await postException(req(`Bearer ${TOKEN}`))).status).toBe(200);
    expect(await store.count("exceptions")).toBe(1);
    expect((await store.find("exception_events")).map((e) => e.action).sort()).toEqual(["created", "repeated"]);
  });

  it("approving a boost writes the governor approval record once, capped at the request, with an audit trail", async () => {
    const parsed = parseException(boost);
    if (!parsed.ok) throw new Error("bad fixture");
    const { row } = await raiseException(store, parsed.item);
    const forward = vi.fn(async () => "sent" as const);
    expect(await decideException(store, { id: row.id, decision: "approve", actor: "garrison", maxDailyUsd: 80 }, new Date(), forward)).toEqual({ ok: false, reason: "bad_amount" });
    const res = await decideException(store, { id: row.id, decision: "approve", actor: "garrison", maxDailyUsd: 40, note: "ok" }, new Date(), forward);
    expect(res.ok).toBe(true);
    const appr = await store.findOne("governor_approvals", { boost_id: "b1" });
    expect(appr).toMatchObject({ approved_by: "garrison", max_daily_usd: 40, forwarded: "sent" });
    expect(forward).toHaveBeenCalledOnce();
    expect(await decideException(store, { id: row.id, decision: "reject", actor: "garrison" })).toEqual({ ok: false, reason: "already_decided" });
    const ev = await store.find("exception_events", { exception_id: row.id });
    expect(ev.map((e) => `${e.action}:${e.actor}`)).toContain("approve:garrison");
  });

  it("resolve-only types refuse approve; mirrored tickets close on resolve", async () => {
    const t = await store.insert("support_tickets", { member_id: null, email: null, reason: "dispute", message: "Chargeback on order 1", status: "open" });
    expect(await syncAppExceptions(store)).toBe(1);
    expect(await syncAppExceptions(store)).toBe(0);
    const x = (await store.find("exceptions"))[0]!;
    expect(x.type).toBe("chargeback_review");
    const crisis = await raiseException(store, { type: "crisis_escalation", title: "c", source: "dm" });
    expect(await decideException(store, { id: crisis.row.id, decision: "approve", actor: "a" })).toEqual({ ok: false, reason: "not_allowed" });
    await decideException(store, { id: x.id, decision: "resolve", actor: "a" });
    expect((await store.get("support_tickets", t.id))?.status).toBe("closed");
  });
});

describe("/admin/today", () => {
  const summary = {
    reach_24h: 120345,
    posts: [{ post_id: "p1", views_24h: 50000, score: 2.1, class: "WINNER" }, ...Array.from({ length: 14 }, (_, i) => ({ post_id: `q${i}`, views_24h: 100 * i, score: -1 + i / 10, class: "NORMAL" }))],
    governor: { status: "HOLD", mode: "dry_run", spend_enabled: false, planned_daily_usd: 0, decided_at: "2026-10-01T06:00:00Z", blitz9: [{ name: "refunds", status: "SCALE", value: null, line: null }], graduation: { passed: false, checks: [{ name: "purchases", status: "fail", value: 0, line: 300 }] } },
  };
  const fetcher = vi.fn(async () => new Response(JSON.stringify(summary), { status: 200 }));

  it("is honest when the workers aren't connected", async () => {
    const t = await computeToday(store, new Date("2026-10-02T12:00:00Z"), fetcher as unknown as typeof fetch);
    expect(t.reach_24h).toBeNull();
    expect(t.workers.connected).toBe(false);
    expect(t.renewal1.rate).toBeNull();
    expect(fetcher).not.toHaveBeenCalled();
  });

  it("merges the workers' reach, scores and governor with our money numbers", async () => {
    vi.stubEnv("GROWTH_WORKER_URL", "https://workers.test");
    vi.stubEnv("WORKER_TOKEN", "w".repeat(40));
    const m = await store.insert("members", { email: "a@example.com", first_name: "A", is_demo: false, attribution: { post_id: "p1", platform: "ig", page: "changyin" } } as never);
    const ms = await store.insert("memberships", { member_id: m.id, plan: "monthly", status: "active", price_cents: 2500, interval: "month", founding: true, first_paid_at: "2026-08-20T00:00:00Z", cancel_at_period_end: false, is_demo: false } as never);
    for (const d of ["2026-08-20", "2026-09-20"]) await store.insert("sy_orders", { member_id: m.id, email: m.email, kind: "membership_charge", status: "paid", amount_cents: 2500, amount_refunded_cents: 0, membership_id: ms.id, offer_code: "founding_monthly", is_demo: false, created_at: `${d}T00:00:00Z` } as never);
    const t = await computeToday(store, new Date("2026-10-02T12:00:00Z"), fetcher as unknown as typeof fetch);
    expect(t.reach_24h).toBe(120345);
    expect(t.mrr.total).toBe(2500);
    expect(t.renewal1).toEqual({ due: 1, renewed: 1, rate: 1 });
    expect(t.top[0]!.post_id).toBe("p1");
    expect(t.top[0]!.class).toBe("WINNER");
    expect(t.weakest).toHaveLength(10);
    expect(t.workers.governor?.status).toBe("HOLD");
    const bad = await fetchWorkerSummary((async () => new Response("no", { status: 503 })) as unknown as typeof fetch);
    expect(bad.error).toMatch(/503/);
  });
});

describe("7am digest", () => {
  it("waits for 07:00 ET, sends once per ET day", async () => {
    vi.stubEnv("DIGEST_EMAIL", "ops@example.com");
    const send = vi.fn(async () => undefined);
    expect(easternDayAndHour(new Date("2026-10-02T10:30:00Z"))).toEqual({ day: "2026-10-02", hour: 6 });
    expect((await runDigest(store, new Date("2026-10-02T10:30:00Z"), send)).status).toBe("not_yet");
    expect((await runDigest(store, new Date("2026-10-02T11:00:00Z"), send)).status).toBe("sent");
    expect((await runDigest(store, new Date("2026-10-02T12:00:00Z"), send)).status).toBe("already_sent");
    expect(send).toHaveBeenCalledOnce();
  });
});
