/**
 * Warm-list import (data/warm_lists): consent flags, suppression, Klaviyo and Mailchimp
 * headers, dry run vs commit, no resubscribe, and the batched double opt-in invites.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { classifyRow, importWarmList, mapHeaders, parseCsv, sendWarmInvites } from "@/lib/warmImport";
import { confirmWaitlist } from "@/lib/waitlist";

const TEMPLATES = path.resolve(__dirname, "../../../data/warm_lists");
let store: MemoryStore;
beforeEach(() => {
  vi.stubEnv("LAUNCH_MODE", "prelaunch");
  store = new MemoryStore();
  setStoreForTests(store);
});

const KLAVIYO = [
  "Email,First Name,Email Marketing Consent,Email Marketing Consent Timestamp,SMS Marketing Consent,Email Suppressions,Country,Strong Years Waitlist Opt-in,Strong Years Waitlist Opt-in At,Source",
  "ok1@test.dev,Linda,SUBSCRIBED,2025-03-01T10:00:00Z,SUBSCRIBED,,United States,true,2026-10-02T14:00:00Z,K9 popup",
  "nooptin@test.dev,Ray,SUBSCRIBED,2025-03-01T10:00:00Z,,,United States,false,,K9 popup",
  "bounce@test.dev,Bo,SUBSCRIBED,2025-03-01T10:00:00Z,,HARD_BOUNCE,United States,true,,K9 popup",
  "spam@test.dev,Sam,SUBSCRIBED,2025-03-01T10:00:00Z,,SPAM_COMPLAINT,United States,true,,K9 popup",
  "unsub@test.dev,Una,UNSUBSCRIBED,2025-03-01T10:00:00Z,,,United States,true,,K9 popup",
  "never@test.dev,Nev,NEVER_SUBSCRIBED,,SUBSCRIBED,,United States,true,,checkout",
  "uk@test.dev,Ann,SUBSCRIBED,2025-03-01T10:00:00Z,,,United Kingdom,true,,K9 popup",
  "OK1@Test.dev,Linda,SUBSCRIBED,2025-03-01T10:00:00Z,,,United States,true,,K9 popup",
  "not-an-email,X,SUBSCRIBED,,,,United States,true,,",
  "\"ok2@test.dev\",\"Mae, Jr\",SUBSCRIBED,,,,,yes,,",
].join("\n");

const MAILCHIMP = [
  "Email Address,First Name,Last Name,MEMBER_RATING,OPTIN_TIME,CONFIRM_TIME,Status,TAGS,CC",
  'mc1@test.dev,Joan,Lee,4,2024-01-01 10:00:00,2024-01-01 10:05:00,subscribed,"""sy-waitlist-yes"",""buyers""",US',
  'mc2@test.dev,Pat,Ng,2,2024-01-01 10:00:00,2024-01-01 10:05:00,subscribed,"""buyers""",US',
  'mc3@test.dev,Lou,Fay,1,2024-01-01 10:00:00,2024-01-01 10:05:00,cleaned,"""sy-waitlist-yes""",US',
  'mc4@test.dev,Kim,Day,1,2024-01-01 10:00:00,,pending,"""sy-waitlist-yes""",US',
].join("\n");

describe("CSV parsing and header mapping", () => {
  it("parses quotes, doubled quotes, CRLF and a BOM", () => {
    expect(parseCsv('﻿a,b\r\n"x, y","he said ""hi"""\r\n')).toEqual([["a", "b"], ["x, y", 'he said "hi"']]);
  });
  it("maps Klaviyo and Mailchimp export headers to the template columns", () => {
    const k = mapHeaders(parseCsv(KLAVIYO)[0]!);
    expect(Object.keys(k)).toEqual(expect.arrayContaining(["email", "first_name", "email_consent", "email_consent_at", "suppression", "country", "sy_waitlist_optin", "sy_waitlist_optin_at", "consent_source"]));
    const m = mapHeaders(parseCsv(MAILCHIMP)[0]!);
    expect(Object.keys(m)).toEqual(expect.arrayContaining(["email", "first_name", "email_consent", "tags", "country"]));
  });
  it("never reads an SMS consent column", () => {
    const k = mapHeaders(parseCsv(KLAVIYO)[0]!);
    expect(Object.values(k)).not.toContain(4); // "SMS Marketing Consent"
  });
  it("classifies in rule order", () => {
    const [h, ...rows] = parseCsv(KLAVIYO);
    const cols = mapHeaders(h!);
    const reasons = rows.map((r) => {
      const c = classifyRow(r, cols);
      return c.ok ? "ok" : c.reason;
    });
    expect(reasons).toEqual(["ok", "no_waitlist_optin", "suppressed_bounce_or_complaint", "suppressed_bounce_or_complaint", "no_brand_consent", "no_brand_consent", "not_us", "ok", "invalid_email", "ok"]);
  });
});

describe("importWarmList", () => {
  it("dry run (default) writes nothing and reports what a commit would do", async () => {
    const s = await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: false, batch: "t1" });
    expect(s.imported).toBe(2);
    expect(s.skipped).toMatchObject({ duplicate_in_file: 1, no_waitlist_optin: 1, suppressed_bounce_or_complaint: 2, no_brand_consent: 2, not_us: 1, invalid_email: 1 });
    expect(await store.count("waitlist")).toBe(0);
    expect(await store.count("consent_log")).toBe(0);
  });

  it("commit inserts pending rows with consent logged, no ad consent, no email yet", async () => {
    const s = await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: true, batch: "t1" });
    expect(s.imported).toBe(2);
    const rows = await store.find("waitlist");
    expect(rows.map((r) => r.email).sort()).toEqual(["ok1@test.dev", "ok2@test.dev"]);
    for (const r of rows) {
      expect(r.status).toBe("pending");
      expect(r.ad_consent_requested).toBe(false);
      expect(r.confirm_token_hash).toBeNull();
      expect(r.attribution).toMatchObject({ utm_source: "k9supps", utm_medium: "warm_list", utm_campaign: "t1" });
    }
    expect(rows.find((r) => r.email === "ok2@test.dev")?.first_name).toBe("Mae, Jr");
    const logs = await store.find("consent_log");
    expect(logs).toHaveLength(2);
    expect(logs[0]!.text_shown).toContain("SMS and ad-measurement consent were not imported");
    expect(await store.count("outbox")).toBe(0);
  });

  it("reads the Mailchimp opt-in tag and status", async () => {
    const s = await importWarmList(store, MAILCHIMP, { brand: "unignorable", commit: true });
    expect(s.imported).toBe(1);
    expect(s.skipped).toMatchObject({ no_waitlist_optin: 1, suppressed_bounce_or_complaint: 1, no_brand_consent: 1 });
    expect((await store.find("waitlist")).map((r) => r.email)).toEqual(["mc1@test.dev"]);
  });

  it("never touches an address already on the waitlist, including an unsubscribed one", async () => {
    await store.insert("waitlist", { email: "ok1@test.dev", status: "unsubscribed", referral_code: "AAAAAAAA", unsubscribed_at: "2026-09-01T00:00:00Z", ad_consent_requested: false });
    await store.insert("email_prefs", { email: "ok2@test.dev", lifecycle_opt_in: false, coach_opt_in: false, unsubscribed_at: "2026-09-01T00:00:00Z", source: "unsubscribe_page" });
    const s = await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: true });
    expect(s.imported).toBe(0);
    expect(s.skipped).toMatchObject({ already_on_waitlist: 1, unsubscribed_from_strong_years: 1 });
    expect((await store.findOne("waitlist", { email: "ok1@test.dev" }))?.status).toBe("unsubscribed");
  });

  it("is idempotent: importing the same file twice adds nobody", async () => {
    await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: true });
    const again = await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: true });
    expect(again.imported).toBe(0);
    expect(await store.count("waitlist")).toBe(2);
  });

  it("refuses a file without the consent columns", async () => {
    const s = await importWarmList(store, "Email,First Name\na@test.dev,A", { brand: "k9supps", commit: true });
    expect(s.errors.join(" ")).toMatch(/email_consent/);
    expect(s.errors.join(" ")).toMatch(/sy_waitlist_optin/);
    expect(await store.count("waitlist")).toBe(0);
  });

  it("the shipped templates parse and every example row lands where its comment says", async () => {
    for (const [file, brand] of [["klaviyo_template.csv", "k9supps"], ["mailchimp_template.csv", "unignorable"]] as const) {
      const csv = readFileSync(path.join(TEMPLATES, file), "utf8");
      const s = await importWarmList(store, csv, { brand, commit: false });
      expect(s.errors).toEqual([]);
      expect(s.imported).toBe(1);
      expect(s.rows).toBeGreaterThanOrEqual(4);
    }
  });
});

describe("sendWarmInvites (cron)", () => {
  it("sends one double opt-in email per imported row, in batches, never twice", async () => {
    await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: true });
    await store.insert("waitlist", { email: "organic@test.dev", status: "pending", referral_code: "BBBBBBBB", ad_consent_requested: false, last_signup_email_at: null, confirm_token_hash: null });
    const first = await sendWarmInvites(store, { limit: 1 });
    expect(first.sent).toBe(1);
    const second = await sendWarmInvites(store, { limit: 10 });
    expect(second.sent).toBe(1);
    const third = await sendWarmInvites(store, { limit: 10 });
    expect(third.sent).toBe(0);
    const mail = await store.find("outbox", { template: "WL1w_warm_confirm" });
    expect(mail.map((m) => m.to).sort()).toEqual(["ok1@test.dev", "ok2@test.dev"]);
    expect(mail[0]!.body).toContain("K9SUPPS email");
    expect(mail[0]!.body).toMatch(/Leave now|leave now/);
    // The organic pending row is not an import: the cron leaves it alone.
    expect(await store.count("outbox", { to: "organic@test.dev" })).toBe(0);
    expect(await store.count("outbox", { channel: "sms" })).toBe(0);
  });

  it("the invite confirms through the normal double opt-in", async () => {
    await importWarmList(store, KLAVIYO, { brand: "k9supps", commit: true });
    const fixed = "warmTokenAbc123";
    await sendWarmInvites(store, { limit: 1, token: () => fixed });
    const r = await confirmWaitlist(store, fixed, { ip: null, userAgent: null });
    expect(r.ok).toBe(true);
    if (r.ok) expect(r.entry.status).toBe("confirmed");
  });

  it("the cron route requires the secret", async () => {
    const { GET } = await import("@/app/api/cron/warm-invites/route");
    const res = await GET(new Request("http://localhost/api/cron/warm-invites"));
    expect(res.status).toBe(401);
  });

  it("the import route refuses an unknown brand and cross-site posts, and dry-runs by default", async () => {
    const { POST } = await import("@/app/api/admin/waitlist/import/route");
    expect((await POST(new Request("http://localhost/api/admin/waitlist/import?brand=acme", { method: "POST", body: KLAVIYO }))).status).toBe(400);
    expect((await POST(new Request("http://localhost/api/admin/waitlist/import?brand=k9supps", { method: "POST", body: KLAVIYO, headers: { origin: "https://evil.test" } }))).status).toBe(403);
    const dry = await POST(new Request("http://localhost/api/admin/waitlist/import?brand=k9supps", { method: "POST", body: KLAVIYO }));
    expect(dry.status).toBe(200);
    expect(((await dry.json()) as { committed: boolean }).committed).toBe(false);
    expect(await store.count("waitlist")).toBe(0);
    const wet = await POST(new Request("http://localhost/api/admin/waitlist/import?brand=k9supps&commit=1", { method: "POST", body: KLAVIYO }));
    expect(((await wet.json()) as { imported: number }).imported).toBe(2);
  });
});
