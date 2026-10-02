/** Static checks on the theme beyond Shopify Theme Check (run separately: npm run theme:check). */
import { describe, it, expect } from "vitest";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import path from "node:path";

const T = path.resolve(new URL("../theme", import.meta.url).pathname);
const files = (d: string) => readdirSync(path.join(T, d)).map((f) => path.join(T, d, f));
const read = (p: string) => readFileSync(p, "utf8");

function isGray(hex: string): boolean {
  let h = hex.replace("#", "");
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (h.length !== 6) return false;
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  const spread = Math.max(r, g, b) - Math.min(r, g, b);
  const mid = (r + g + b) / 3;
  return spread < 18 && mid > 50 && mid < 205; // near-neutral mid tones = "gray"
}

describe("design rules", () => {
  const css = read(path.join(T, "assets/strong-years.css")).replace(/\/\*[\s\S]*?\*\//g, "");
  it("no gray text: no gray/grey keywords and no mid-tone neutral colors anywhere in the CSS", () => {
    expect(/\b(gray|grey|silver|darkgray|lightgray|dimgray)\b/i.test(css)).toBe(false);
    const grays = (css.match(/#[0-9a-f]{3,6}\b/gi) || []).filter(isGray);
    expect(grays).toEqual([]);
  });
  it("no faded text tricks: no opacity or rgba on color declarations", () => {
    expect(/(^|[;{\s])color\s*:\s*rgba?\(/i.test(css)).toBe(false);
    expect(/opacity\s*:\s*0?\.\d/.test(css)).toBe(false);
  });
  it('no "//" decorations or mono index-label kickers in theme markup', () => {
    for (const f of [...files("sections"), ...files("snippets"), ...files("templates")].filter((f) => !f.endsWith("customers"))) {
      if (!existsSync(f) || !/\.(liquid|json)$/.test(f)) continue;
      const visible = read(f).replace(/https?:\/\//g, "").replace(/\{%-?\s*comment[\s\S]*?endcomment\s*-?%\}/g, "");
      expect(visible.includes("//"), f).toBe(false);
      expect(/font-family\s*:\s*[^;]*mono/i.test(visible), f).toBe(false);
    }
    expect(/monospace|ui-monospace/i.test(css)).toBe(false);
  });
  it("body text >= 20px and buttons >= 60px tall (55+ audience)", () => {
    expect(css).toMatch(/body\{[^}]*font:400 20px/);
    expect(css).toMatch(/\.btn\{[^}]*min-height:60px/);
  });
});

describe("checkout integrity", () => {
  const all = [...files("sections"), ...files("snippets")].map((f) => [f, read(f)] as const);
  it("no express/dynamic checkout buttons (they would skip the consent record and attribution)", () => {
    for (const [f, s] of all) expect(/payment_button|additional_checkout_buttons/.test(s), f).toBe(false);
  });
  it("the auto-renewal consent checkbox is never pre-ticked and is required", () => {
    for (const [f, s] of all) for (const m of s.matchAll(/<input[^>]*name="sy_consent"[^>]*>/g)) {
      expect(m[0], f).not.toMatch(/\bchecked\b/);
      expect(m[0], f).toMatch(/\brequired\b/);
    }
  });
  it("bumps are optional and unticked", () => {
    const s = read(path.join(T, "snippets/sy-bumps.liquid"));
    for (const m of s.matchAll(/<input[^>]*name="sy_bump"[^>]*>/g)) expect(m[0]).not.toMatch(/\bchecked\b|\brequired\b/);
  });
  it("the founding box states the close date only: no seat counts, no timers (no cap since Oct 2 2026)", () => {
    const s = read(path.join(T, "snippets/sy-count-line.liquid"));
    expect(s).toMatch(/close_date/);
    expect(/inventory_quantity|seats taken|few left|5,000/i.test(s)).toBe(false);
    expect(/countdown|setInterval|timer/i.test(s.replace(/No timers/g, ""))).toBe(false);
  });
});

describe("template wiring", () => {
  const sections = new Set(files("sections").map((f) => path.basename(f).replace(/\.(liquid|json)$/, "")));
  const templates = [...files("templates").filter((f) => f.endsWith(".json")), ...files("templates/customers")];
  it("every JSON template references sections that exist", () => {
    for (const f of templates) {
      const j = JSON.parse(read(f));
      for (const [id, sec] of Object.entries<any>(j.sections)) expect(sections.has(sec.type), `${f} → ${id}:${sec.type}`).toBe(true);
      expect(j.order.every((k: string) => k in j.sections), f).toBe(true);
    }
  });
  it("every template suffix provision.ts assigns exists", async () => {
    const { PRODUCTS } = await import("../config/catalog.ts");
    for (const p of PRODUCTS) if (p.templateSuffix) expect(existsSync(path.join(T, `templates/product.${p.templateSuffix}.json`)), p.handle).toBe(true);
    for (const s of ["legal", "faq", "characters", "welcome"]) expect(existsSync(path.join(T, `templates/page.${s}.json`))).toBe(true);
    expect(existsSync(path.join(T, "templates/product.starter.json"))).toBe(true);
  });
  it("every liquid section has a schema", () => {
    for (const f of files("sections").filter((f) => f.endsWith(".liquid"))) expect(read(f), f).toMatch(/\{% schema %\}/);
  });
});
