/** AUDIT_BUSINESS F08 / AUDIT_FINAL #20: downloads are watermarked and logged. */
import { execFileSync } from "node:child_process";
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { pdfSafe, watermarkPdf } from "@/lib/watermark";
import type { Member, Membership } from "@/lib/db/types";

const auth = vi.hoisted(() => ({ member: null as Member | null, membership: null as Membership | null }));
vi.mock("@/lib/auth/server", () => ({
  currentMember: async () => auth.member,
  entitlement: async () => ({ access: Boolean(auth.membership), reason: "ok", granting: auth.membership }),
  currentMembership: async () => auth.membership,
}));
vi.mock("next/headers", () => ({ headers: async () => ({ get: (k: string) => (k === "user-agent" ? "vitest" : null) }), cookies: async () => ({ get: () => undefined }) }));

const root = path.resolve(__dirname, "../..");
const pdfText = (bytes: Uint8Array) => {
  const dir = mkdtempSync(path.join(tmpdir(), "wm-"));
  const f = path.join(dir, "x.pdf");
  writeFileSync(f, bytes);
  return execFileSync("pdftotext", ["-layout", f, "-"]).toString();
};

let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});

describe("F08 watermarked downloads", () => {
  it("F08: every page carries the buyer's name, email and order id", async () => {
    const src = new Uint8Array(readFileSync(path.join(root, "content/downloads/strong_kitchen.pdf")));
    const out = await watermarkPdf(src, { name: "Ruth", email: "ruth@example.com", orderRef: "SY-1234ABCD" });
    const text = pdfText(out);
    const pages = text.split("\f").filter((p) => p.trim());
    expect(pages.length).toBeGreaterThan(1);
    for (const p of pages) expect(p).toMatch(/Licensed to Ruth <ruth@example\.com> \| Order SY-1234ABCD/);
  });

  it("F08: names outside the PDF font are folded, never crash", async () => {
    expect(pdfSafe("José Nuñez 李")).toBe("Jose Nunez ?");
    const src = new Uint8Array(readFileSync(path.join(root, "content/downloads/twelve_week_printable.pdf")));
    await expect(watermarkPdf(src, { name: "Zoë 王", email: "zoe@example.com", orderRef: "M-1" })).resolves.toBeInstanceOf(Uint8Array);
  });

  it("F08: the download route stamps the buyer's order and logs the download", async () => {
    const m = await store.insert("members", { email: "bea@example.com", first_name: "Bea", timezone: "America/New_York", session_version: 1 } as Partial<Member>);
    auth.member = m;
    auth.membership = null; // one-time add-on only: still theirs to keep
    const order = await store.insert("sy_orders", { member_id: m.id, email: m.email, offer_code: "kitchen", kind: "bump", description: "Kitchen", amount_cents: 1700, status: "paid", stripe_payment_intent: null, stripe_invoice: null, checkout_intent_id: null, is_demo: false });
    const { GET } = await import("@/app/api/downloads/[file]/route");
    const res = await GET(new Request("http://localhost/api/downloads/strong_kitchen.pdf"), { params: Promise.resolve({ file: "strong_kitchen.pdf" }) });
    expect(res.status).toBe(200);
    const text = pdfText(new Uint8Array(await res.arrayBuffer()));
    expect(text).toContain(`Order SY-${order.id.slice(0, 8).toUpperCase()}`);
    expect(text).toContain("bea@example.com");
    const ev = (await store.findOne("download_events", { member_id: m.id }))!;
    expect(ev).toMatchObject({ file: "strong_kitchen.pdf", order_ref: `SY-${order.id.slice(0, 8).toUpperCase()}`, user_agent: "vitest" });
    // Not bought: refused, not logged.
    const no = await GET(new Request("http://localhost/api/downloads/strength_reset_2500.pdf"), { params: Promise.resolve({ file: "strength_reset_2500.pdf" }) });
    expect(no.status).toBe(403);
    expect(await store.count("download_events")).toBe(1);
  });
});
