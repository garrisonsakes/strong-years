import type { Page } from "@playwright/test";

/**
 * Brand rule check: no gray text anywhere. Returns every visible text element whose
 * computed colour is a mid-tone neutral (gray), is faded, or has contrast below 4.5:1
 * against its nearest opaque background.
 */
export async function findGrayOrLowContrastText(page: Page) {
  return page.evaluate(() => {
    const parse = (c: string) => {
      const m = c.match(/rgba?\(([^)]+)\)/);
      if (!m) return null;
      const [r, g, b, a] = m[1]!.split(",").map((x) => parseFloat(x));
      return { r: r!, g: g!, b: b!, a: a === undefined ? 1 : a };
    };
    const lum = (c: { r: number; g: number; b: number }) => {
      const f = (v: number) => {
        const s = v / 255;
        return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
      };
      return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b);
    };
    const bgOf = (el: Element | null): { r: number; g: number; b: number } => {
      while (el) {
        const c = parse(getComputedStyle(el).backgroundColor);
        if (c && c.a > 0.9) return c;
        el = el.parentElement;
      }
      return { r: 251, g: 246, b: 236 };
    };
    const bad: string[] = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const seen = new Set<Element>();
    while (walker.nextNode()) {
      const node = walker.currentNode;
      const el = node.parentElement;
      if (!el || seen.has(el) || !node.textContent?.trim()) continue;
      seen.add(el);
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || cs.display === "none" || el.closest("[aria-hidden='true'],svg,.sr-only,option,script,style")) continue;
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;
      const fg = parse(cs.color);
      if (!fg) continue;
      const spread = Math.max(fg.r, fg.g, fg.b) - Math.min(fg.r, fg.g, fg.b);
      const isGray = spread < 16 && fg.r > 60 && fg.r < 210;
      const bg = bgOf(el);
      const l1 = lum(fg);
      const l2 = lum(bg);
      const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
      const opacity = parseFloat(cs.opacity);
      if (isGray || ratio < 4.5 || fg.a < 0.9 || opacity < 0.9) {
        bad.push(`${el.tagName} "${node.textContent.trim().slice(0, 40)}" color=${cs.color} ratio=${ratio.toFixed(2)}`);
      }
    }
    return bad;
  });
}

export async function hasHorizontalOverflow(page: Page) {
  return page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
}

export async function completeStrengthQuiz(page: Page, opts: { email: string; reps?: number }) {
  await page.goto("/quiz/strength-age");
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.getByRole("button", { name: "Start the test" }).click();
  await page.getByRole("radio", { name: "Me", exact: true }).click();
  await page.getByRole("radio", { name: "Woman" }).click();
  await page.getByRole("button", { name: "Continue" }).click(); // age 70 default
  await page.getByRole("checkbox", { name: "None of these" }).click();
  await page.getByRole("radio", { name: "No", exact: true }).click();
  await page.getByLabel("How many full stands did you do?").fill(String(opts.reps ?? 12));
  await page.getByRole("button", { name: "Continue" }).click();
  await page.getByRole("radio", { name: /Position 3: heel to toe/ }).click();
  await page.getByRole("radio", { name: "With some effort" }).click();
  await page.getByRole("radio", { name: "Yes, with a rest" }).click();
  await page.getByRole("radio", { name: "Using one hand or a knee" }).click();
  await page.getByRole("radio", { name: "Up, holding the rail", exact: true }).click();
  await page.getByRole("radio", { name: "Keep up, but it takes effort" }).click();
  await page.getByRole("radio", { name: "Rarely", exact: true }).click();
  await page.getByRole("checkbox", { name: "Nothing in particular" }).click();
  await page.getByRole("radio", { name: "Keep living independently in my own home" }).click();
  await page.getByRole("radio", { name: "10", exact: true }).click();
  await page.getByLabel("First name").fill("Ruth");
  await page.getByLabel("Email", { exact: true }).fill(opts.email);
  await page.getByRole("button", { name: "Show my Strength Age" }).click();
  await page.waitForURL(/\/quiz\/strength-age\/result\//);
}
