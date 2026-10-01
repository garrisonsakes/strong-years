import { expect, test, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { completeStrengthQuiz, findGrayOrLowContrastText, hasHorizontalOverflow } from "./helpers";

const OUT = path.join(__dirname, "..", "..", "screenshots");
const WIDTHS = [390, 1280] as const;
const report: Record<string, { gray: string[]; overflow: boolean }> = {};

async function shoot(page: Page, name: string, width: number) {
  await page.waitForLoadState("networkidle");
  const file = `${name}-${width}.png`;
  await page.screenshot({ path: path.join(OUT, file), fullPage: true });
  report[file] = { gray: await findGrayOrLowContrastText(page), overflow: await hasHorizontalOverflow(page) };
}

test.beforeAll(() => fs.mkdirSync(OUT, { recursive: true }));
test.afterAll(() => fs.writeFileSync(path.join(OUT, "checks.json"), JSON.stringify(report, null, 2)));

for (const width of WIDTHS) {
  test(`key pages at ${width}px`, async ({ browser }) => {
    const ctx = await browser.newContext({ viewport: { width, height: width === 390 ? 844 : 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();

    await page.goto("/start?arm=A");
    await shoot(page, "01-landing", width);

    await page.goto("/quiz/strength-age");
    await shoot(page, "02-quiz-intro", width);
    await page.getByRole("button", { name: "Start the test" }).click();
    await page.getByRole("radio", { name: "Me", exact: true }).click();
    await page.getByRole("radio", { name: "Woman" }).click();
    await page.getByRole("button", { name: "Continue" }).click();
    await page.getByRole("checkbox", { name: "None of these" }).click();
    await page.getByRole("radio", { name: "No", exact: true }).click();
    await shoot(page, "03-quiz-chair-test", width);

    await completeStrengthQuiz(page, { email: `screens${width}@example.com` });
    await shoot(page, "04-quiz-result", width);

    await page.goto("/join");
    await shoot(page, "05-join-founding-checkout", width);

    await page.goto("/gift");
    await shoot(page, "06-gift", width);

    await page.goto("/login");
    await page.getByTestId("demo-login").click();
    await page.waitForURL(/\/app$/);
    await shoot(page, "07-members-dashboard", width);
    await page.goto("/app/progress");
    await shoot(page, "08-progress-retest-chart", width);
    await page.goto("/app/chat");
    await page.getByTestId("chat-input").fill("What should I eat for breakfast?");
    await page.getByTestId("chat-send").click();
    await expect(page.getByTestId("chat-log")).toContainText("Chang Yin (AI character)");
    await shoot(page, "09-chat", width);
    await page.goto("/app/account/cancel");
    await shoot(page, "10-cancel-step1", width);
    await page.goto("/app/account/cancel?reason=expensive");
    await shoot(page, "11-cancel-step2", width);
    await page.goto("/app/kitchen");
    await shoot(page, "12-kitchen", width);
    await page.goto("/app/printables");
    await shoot(page, "14-downloads", width);
    await page.goto("/app/account");
    await shoot(page, "15-account", width);
    await page.goto("/safety");
    await shoot(page, "16-crisis-protocol", width);
    await page.goto("/privacy-choices");
    await shoot(page, "17-privacy-choices", width);
    await page.goto("/gift/redeem");
    await shoot(page, "18-gift-redeem", width);
    await ctx.close();

    const admin = await browser.newContext({ viewport: { width, height: 900 }, httpCredentials: { username: "admin", password: "strongyears-demo" } });
    const ap = await admin.newPage();
    await ap.goto("/admin");
    await shoot(ap, "13-admin", width);
    await admin.close();
  });
}
