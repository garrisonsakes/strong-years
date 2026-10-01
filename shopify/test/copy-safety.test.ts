/**
 * Copy compliance for everything this package publishes: legal pages, policies, theme text, emails and the
 * checkout extensions. The BLOCK patterns are read straight from SAFETY_RULES.md §3.1 (single source of truth).
 */
import { describe, it, expect } from "vitest";
import { readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { contentPages, shopPolicies } from "../src/legal.ts";
import { factsFromEnv } from "../src/provision.ts";
import { PRODUCTS } from "../config/catalog.ts";
import { FOUNDING_TERMS } from "../app-postpurchase/server/postPurchase.ts";

const ROOT = path.resolve(new URL("..", import.meta.url).pathname);
const REPO = path.resolve(ROOT, "..");

function walk(dir: string, exts: string[]): string[] {
  return readdirSync(dir).flatMap((f) => {
    const p = path.join(dir, f);
    if (f === "node_modules") return [];
    return statSync(p).isDirectory() ? walk(p, exts) : exts.some((e) => p.endsWith(e)) ? [p] : [];
  });
}

function safetyPatterns(): RegExp[] {
  const md = readFileSync(path.join(REPO, "SAFETY_RULES.md"), "utf8");
  const block = md.split("### 3.1")[1].split("```")[1];
  return block.split("\n").map((l) => l.replace(/\s+→.*$/, "").trim()).filter(Boolean).map((src) => new RegExp(`\\b(?:${src})`, "i"));
}

const facts = factsFromEnv({ COMPANY_LEGAL_NAME: "Strong Years LLC", MAILING_ADDRESS: "1 Test St, Austin, TX 78701", SUPPORT_EMAIL: "help@strongyears.com", BILLING_PHONE: "(555) 010-0000", GOVERNING_STATE: "Texas" } as any);
const stripHtml = (s: string) => s.replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<style[\s\S]*?<\/style>/g, " ").replace(/\{%-?\s*comment\s*-?%\}[\s\S]*?\{%-?\s*endcomment\s*-?%\}/g, " ").replace(/\{%[\s\S]*?%\}/g, " ").replace(/\{\{[\s\S]*?\}\}/g, " ").replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ");

function corpus(): Array<[string, string]> {
  const out: Array<[string, string]> = [];
  for (const p of contentPages(facts)) out.push([`page:${p.handle}`, stripHtml(p.bodyHtml)]);
  for (const p of shopPolicies(facts)) out.push([`policy:${p.type}`, stripHtml(p.body)]);
  for (const p of PRODUCTS) out.push([`product:${p.handle}`, stripHtml(p.descriptionHtml + " " + p.seoDescription)]);
  for (const f of walk(path.join(ROOT, "theme"), [".liquid", ".json"])) {
    const raw = readFileSync(f, "utf8");
    const text = f.endsWith(".json") ? JSON.stringify(JSON.parse(raw)).replace(/\\"/g, '"') : raw.replace(/\{%-?\s*schema\s*-?%\}[\s\S]*?\{%-?\s*endschema\s*-?%\}/g, " ");
    out.push([path.relative(ROOT, f), stripHtml(text)]);
  }
  for (const f of walk(path.join(ROOT, "emails"), [".md"])) out.push([path.relative(ROOT, f), readFileSync(f, "utf8").replace(/^---[\s\S]*?---/, "")]);
  for (const f of walk(path.join(ROOT, "app-postpurchase/extensions"), [".jsx"])) out.push([path.relative(ROOT, f), readFileSync(f, "utf8").replace(/\/\*[\s\S]*?\*\//g, " ").replace(/\/\/.*$/gm, " ")]);
  out.push(["post-purchase terms", FOUNDING_TERMS.join(" ")]);
  return out;
}

describe("SAFETY_RULES.md §3.1 blocked claims", () => {
  const patterns = safetyPatterns();
  it("loads the patterns from SAFETY_RULES.md", () => expect(patterns.length).toBeGreaterThan(15));
  it("the patterns really block known-bad copy (self-test)", () => {
    for (const bad of ["Guaranteed results in 14 days", "this melts belly fat", "100% safe for everyone", "detox your liver", "Stop taking your medication", "money-back guarantee you'll feel stronger", "lowers blood pressure instantly"]) {
      expect(patterns.some((re) => re.test(bad)), bad).toBe(true);
    }
    expect(patterns.some((re) => re.test("14-day money-back guarantee on your membership charge")), "allowed phrase").toBe(false);
  });
  for (const [name, text] of corpus()) {
    it(`no blocked claim in ${name}`, () => {
      const hits = patterns.map((re) => text.match(re)?.[0]).filter(Boolean);
      expect(hits).toEqual([]);
    });
  }
});

describe("canon wording", () => {
  const all = corpus();
  it('"guarantee" only appears as the money-back guarantee phrase', () => {
    for (const [name, text] of all) {
      const bad = [...text.matchAll(/guarantee/gi)].filter((m) => !/money-back guarantee$/i.test(text.slice(Math.max(0, m.index! - 11), m.index! + 9)));
      expect(bad.length, name).toBe(0);
    }
  });
  it('founding price is never "for life" and is "locked for as long as you stay subscribed"', () => {
    for (const [name, text] of all) expect(/for life|lifetime price/i.test(text), name).toBe(false);
    expect(all.some(([, t]) => /locked for as long as you stay subscribed/.test(t))).toBe(true);
  });
  it("no fake scarcity, no fake anchors, no fall or mortality outcome claims", () => {
    for (const [name, text] of all) {
      expect(/only \d+ (spots|seats) left|price goes up|was \$\d|ends tonight|hurry/i.test(text), name).toBe(false);
      expect(/prevent(s|ing)? falls?|fewer falls|reduce(s)? (your )?(risk of )?falls?|live longer|add years/i.test(text), name).toBe(false);
    }
  });
  it("no $1 trial anywhere (CANON UPDATE 2)", () => {
    for (const [name, text] of all) expect(/\$1 (for 7 days|trial|today)|7 days for \$1/i.test(text), name).toBe(false);
  });
  it('"text CANCEL" only renders when SMS is enabled', () => {
    for (const f of walk(path.join(ROOT, "theme"), [".liquid"])) {
      const raw = readFileSync(f, "utf8");
      for (const m of raw.matchAll(/text CANCEL/g)) expect(raw.slice(Math.max(0, m.index! - 80), m.index), f).toMatch(/sms_enabled/);
    }
    expect(all.filter(([n]) => n.startsWith("policy:") || n.startsWith("page:")).some(([, t]) => /text CANCEL/.test(t))).toBe(false);
  });
  it("no reviewer claim while REVIEWER_SIGNED is false", () => {
    for (const [name, text] of all.filter(([n]) => n.startsWith("page:") || n.startsWith("policy:"))) expect(/reviewed by licensed/i.test(text), name).toBe(false);
  });
  it("every membership surface states price, interval, renewal and online cancel (S-02)", () => {
    const pages = ["policy:SUBSCRIPTION_POLICY", "page:membership-and-cancellation"];
    for (const [name, text] of all.filter(([n]) => pages.includes(n))) {
      expect(text, name).toMatch(/\$25/);
      expect(text, name).toMatch(/every month/);
      expect(text, name).toMatch(/until you cancel/);
      expect(text, name).toMatch(/Cancel/);
    }
    const terms = readFileSync(path.join(ROOT, "theme/snippets/sy-terms.liquid"), "utf8");
    for (const must of ["renews at", "until you cancel", "Cancel anytime", "14-day money-back guarantee", "remind you"]) expect(terms).toContain(must);
  });
  it("AI-character disclosure is on every layout render and in every email", () => {
    expect(readFileSync(path.join(ROOT, "theme/sections/sy-header.liquid"), "utf8")).toMatch(/are AI characters/);
    expect(readFileSync(path.join(ROOT, "theme/sections/sy-footer.liquid"), "utf8")).toMatch(/are AI characters/);
    for (const f of walk(path.join(ROOT, "emails"), [".md"])) expect(readFileSync(f, "utf8"), f).toMatch(/AI character/);
  });
});
