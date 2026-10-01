import fs from "node:fs";
import path from "node:path";
import { expect, test } from "@playwright/test";
import { findGrayOrLowContrastText, hasHorizontalOverflow } from "./helpers";

/** 390px prelaunch screens (/go hub, /waitlist) → screenshots/40-*.png + 40-checks.json. Run by make prelaunch-local. */
const OUT = path.join(__dirname, "..", "..", "screenshots");
const pages = [
  { file: "40-go-390.png", path: "/go" },
  { file: "40-go-tiktok-390.png", path: "/go?p=tt-cy" },
  { file: "40-waitlist-390.png", path: "/waitlist?utm_source=k9supps&utm_medium=warm_list&utm_campaign=k1" },
];
const report: Record<string, { gray: string[]; overflow: boolean; status: number }> = {};

test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
test.afterAll(() => fs.writeFileSync(path.join(OUT, "40-checks.json"), JSON.stringify(report, null, 2)));

for (const p of pages) {
  test(`${p.path} at 390px: no gray text, no overflow`, async ({ page }) => {
    const res = await page.goto(p.path, { waitUntil: "networkidle" });
    const status = res?.status() ?? 0;
    expect(status).toBe(200);
    await page.screenshot({ path: path.join(OUT, p.file), fullPage: true });
    const gray = await findGrayOrLowContrastText(page);
    const overflow = await hasHorizontalOverflow(page);
    report[p.file] = { gray, overflow, status };
    expect(gray, gray.join("\n")).toEqual([]);
    expect(overflow).toBe(false);
  });
}

test("prelaunch: /waitlist is the form, checkout is not open", async ({ page }) => {
  await page.goto("/waitlist");
  await expect(page.locator('form[action="/api/waitlist"]')).toBeVisible();
  const join = await page.request.get("/join", { maxRedirects: 0 });
  expect(join.headers()["location"] ?? "").not.toMatch(/myshopify\.com\/cart/);
});
