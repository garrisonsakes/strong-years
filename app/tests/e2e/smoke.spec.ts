import { expect, test } from "@playwright/test";
import { completeStrengthQuiz, findGrayOrLowContrastText, hasHorizontalOverflow } from "./helpers";

test.describe.configure({ mode: "serial" });

test("landing: one offer, no $1 trial even with ?arm=A (CANON UPDATE 2), real cohort counter, no gray text", async ({ page }) => {
  await page.goto("/start?arm=A");
  await expect(page.getByTestId("hero-cta")).toHaveAttribute("href", "/join");
  await expect(page.getByTestId("arm-a-card")).toHaveCount(0);
  expect(await page.locator("body").innerText()).not.toMatch(/\$1 (today|trial)|for \$1\b/);
  await page.goto("/start?arm=B");
  await expect(page.getByText("Chang Yin and Sun Yoon are AI characters.").first()).toBeVisible();
  await expect(page.getByTestId("arm-b-card")).toBeVisible();
  await expect(page.getByTestId("cohort-counter")).toContainText("founding spots claimed");
  await expect(page.getByText("The 14-day money-back guarantee.")).toBeVisible();
  await expect(page.getByTestId("hero-cta")).toHaveAttribute("href", "/join");
  expect(await findGrayOrLowContrastText(page)).toEqual([]);
  const minButtonHeight = await page.locator(".btn-primary, .btn-jade, .btn-outline").evaluateAll((els) =>
    Math.min(...els.filter((e) => (e as HTMLElement).offsetParent).map((e) => e.getBoundingClientRect().height)),
  );
  expect(minButtonHeight).toBeGreaterThanOrEqual(48);
});

test("/join: sticky $25 or $30 price cell, bumps change the total, switched-off offers route here", async ({ page }) => {
  await page.goto("/join");
  const h1 = await page.getByRole("heading", { level: 1 }).innerText();
  const price = h1.match(/\$(25|30) today/)![1];
  for (let i = 0; i < 2; i++) {
    await page.reload();
    await expect(page.getByRole("heading", { level: 1 })).toContainText(`$${price} today`);
  }
  await expect(page.getByTestId("terms-box")).toContainText(`renews at $${price}.00`);
  await expect(page.getByTestId("terms-box")).toContainText("14-day money-back guarantee");
  await expect(page.getByTestId("terms-box")).toContainText("remind you by email 48 hours");
  for (const k of ["reset", "kitchen", "wallplan"]) await expect(page.getByTestId(`bump-${k}`)).not.toBeChecked();
  await page.getByTestId("bump-reset").check();
  await page.getByTestId("bump-kitchen").check();
  await expect(page.getByTestId("terms-box")).toContainText(`$${Number(price) + 24}.00`);
  expect(await findGrayOrLowContrastText(page)).toEqual([]);
  for (const path of ["/checkout/founding", "/reset", "/kitchen"]) {
    await page.goto(path);
    await expect(page).toHaveURL(/\/join/);
  }
});

test("quiz → result → /join (consent enforced, Reset bump) → upsells → members area → cancel", async ({ page }) => {
  await page.goto("/start?arm=B");
  await completeStrengthQuiz(page, { email: "ruth.e2e@example.com" });
  await expect(page.getByTestId("strength-age-number")).toHaveText("71");
  await expect(page.getByText("not a medical test")).toBeVisible();
  await page.getByTestId("result-cta").click();
  await page.waitForURL(/\/join\?lead=/);
  await expect(page.getByLabel("Email", { exact: true })).toHaveValue("ruth.e2e@example.com");
  await expect(page.getByTestId("auto-renew-consent")).not.toBeChecked();
  await page.getByTestId("pay-button").click();
  await expect(page.getByText("Please tick the box above to confirm the membership terms.")).toBeVisible();
  await page.getByTestId("bump-reset").check();
  await page.getByTestId("auto-renew-consent").check();
  await page.getByTestId("age-consent").check();
  await page.getByTestId("pay-button").click();
  await page.waitForURL(/\/checkout\/mock\//);
  await expect(page.getByTestId("mock-checkout")).toContainText("7-Day Strength Reset");
  await page.getByTestId("mock-pay").click();

  await page.waitForURL(/\/upsell\/program/);
  await page.getByTestId("upsell-no").click();
  await page.waitForURL(/\/upsell\/printables/);
  await page.getByTestId("upsell-no").click();
  await page.waitForURL(/\/upsell\/kit/);
  await page.getByTestId("upsell-yes").click();
  await page.waitForURL(/\/welcome/);
  await expect(page.getByText(/Next charge/)).toBeVisible();
  await expect(page.getByText("The Strong Years Kit")).toBeVisible();

  // R2-1: the checkout session can't open the program until the inbox is verified.
  await expect(page.getByTestId("start-day-1")).toHaveCount(0);
  await page.goto("/app");
  await expect(page).toHaveURL(/\/login/);
  await page.goto("/welcome");
  await page.getByTestId("send-open-link").click();
  await page.waitForURL(/\/login\?sent=1/);
  // Demo mode shows the emailed link on screen (it points at NEXT_PUBLIC_SITE_URL; open its path here).
  const open = new URL((await page.getByTestId("login-sent").getByRole("link", { name: "Log me in" }).getAttribute("href"))!);
  await page.goto(open.pathname + open.search);
  await expect(page.getByTestId("today")).toBeVisible();
  await expect(page.getByTestId("session-steps")).toContainText("·");
  await page.getByRole("link", { name: "Sore knee today" }).click();
  await expect(page.getByTestId("swap-note")).toBeVisible();
  await page.getByTestId("mark-done").click();
  await expect(page.getByText("Done. ✓")).toBeVisible();

  await page.goto("/app/printables");
  await expect(page.getByTestId("downloads")).toContainText("7-Day Strength Reset");
  await expect(page.getByTestId("downloads")).not.toContainText("Strong Kitchen");
  const pdf = await page.request.get((await page.getByRole("link", { name: "Download the PDF" }).last().getAttribute("href"))!);
  expect(pdf.status()).toBe(200);
  expect(pdf.headers()["content-type"]).toBe("application/pdf");
  expect((await page.request.get("/api/downloads/strong_kitchen.pdf")).status()).toBe(403);

  await page.goto("/app/account");
  await page.getByTestId("cancel-link").click();
  await expect(page.getByTestId("cancel-screen-1")).toBeVisible();
  await page.getByTestId("reason-no_time").click();
  await expect(page.getByTestId("cancel-screen-2")).toBeVisible();
  const [save, finish] = await Promise.all([page.getByTestId("save-offer").boundingBox(), page.getByTestId("finish-cancel").boundingBox()]);
  expect(Math.abs(save!.height - finish!.height)).toBeLessThanOrEqual(1);
  expect(Math.abs(save!.width - finish!.width)).toBeLessThanOrEqual(2);
  await page.getByTestId("finish-cancel").click();
  await expect(page.getByTestId("cancel-done")).toContainText("You won't be charged again.");
});

test("founding purchase counts toward the real cohort counter; the price test is logged for analysis", async ({ page, browser }) => {
  await page.goto("/start");
  const before = await page.getByTestId("cohort-counter").first().innerText();
  await page.goto("/join");
  await page.getByLabel("First name").fill("Walt");
  await page.getByLabel("Email", { exact: true }).fill("walt.e2e@example.com");
  await page.getByTestId("auto-renew-consent").check();
  await page.getByTestId("age-consent").check();
  await page.getByTestId("pay-button").click();
  await page.getByTestId("mock-pay").click();
  await page.waitForURL(/\/upsell\/program/);
  await page.goto("/start");
  const after = await page.getByTestId("cohort-counter").first().innerText();
  const n = (s: string) => Number(s.match(/([\d,]+) of/)![1]!.replace(/,/g, ""));
  expect(n(after)).toBe(n(before) + 1);

  const admin = await browser.newContext({ httpCredentials: { username: "admin", password: "strongyears-demo" } });
  const ap = await admin.newPage();
  await ap.goto("/admin");
  await expect(ap.getByTestId("price-test-table")).toContainText(/p(2500|3000)/);
  await admin.close();
});

test("AI chat: disclosure, crisis referral, and it shows in the admin crisis log", async ({ page, browser }) => {
  await page.goto("/login");
  await page.getByTestId("demo-login").click();
  await page.waitForURL(/\/app$/);
  await page.goto("/app/chat");
  await expect(page.getByTestId("ai-disclosure")).toContainText("AI character, not a doctor");
  await page.getByTestId("chat-input").fill("How do I get up from a chair more easily?");
  await page.getByTestId("chat-send").click();
  await expect(page.getByTestId("chat-log")).toContainText("Chang Yin (AI character)");
  await page.getByTestId("chat-input").fill("Honestly I just want to die");
  await page.getByTestId("chat-send").click();
  await expect(page.getByTestId("chat-log")).toContainText("988");
  // Round 7: a benign idiom that trips the rules: resources first, then the member clears it.
  await page.getByTestId("chat-input").fill("I'd rather die than eat Sun's kimchi again haha");
  await page.getByTestId("chat-send").click();
  await expect(page.getByTestId("not-what-i-meant")).toHaveCount(2);
  await page.getByTestId("not-what-i-meant").last().click();
  await expect(page.getByTestId("chat-log")).toContainText("Thanks for telling me. Let's carry on.");
  await expect(page.getByTestId("not-what-i-meant")).toHaveCount(1);

  const admin = await browser.newContext({ httpCredentials: { username: "admin", password: "strongyears-demo" } });
  const ap = await admin.newPage();
  await ap.goto("/admin");
  await expect(ap.getByTestId("admin")).toContainText("self harm");
  await expect(ap.getByText("MRR").first()).toBeVisible();
  await admin.close();
});

test("R2-2: both gift purchases complete in demo mode (signed quotes), no account access for the buyer", async ({ page }) => {
  for (const months of [3, 12] as const) {
    await page.goto("/gift");
    await page.getByTestId(`gift-${months}`).click();
    await page.getByLabel("Their first name").fill("Mei");
    await page.getByLabel(/Their email/).fill(`mei.${months}.e2e@example.com`);
    await page.getByLabel("First name", { exact: true }).fill("Lin");
    await page.getByLabel("Email", { exact: true }).fill(`lin.${months}.gift.e2e@example.com`);
    await page.getByTestId("age-consent").check();
    await page.getByTestId("pay-button").click();
    await page.waitForURL(/\/checkout\/mock\//);
    await expect(page.getByTestId("mock-checkout")).toContainText(months === 3 ? "$49" : "$119");
    await page.getByTestId("mock-pay").click();
    await page.waitForURL(/\/gift\/thanks/);
    await expect(page.getByTestId("gift-thanks")).toContainText("Your gift is on its way");
    await page.goto("/app");
    await expect(page).toHaveURL(/\/login/);
  }
});

test("gut quiz red-flag answers stop the quiz with no offer", async ({ page }) => {
  await page.goto("/quiz/gut-energy");
  await page.getByRole("button", { name: "Start" }).click();
  await page.getByRole("checkbox", { name: /Blood in your stool/ }).click();
  await page.getByRole("button", { name: "Continue" }).click();
  await expect(page.getByTestId("redflag-stop")).toContainText("call 911");
  await expect(page.getByText("7 days for $1")).toHaveCount(0);
});

test("mobile 390px: no horizontal overflow on key pages", async ({ browser }) => {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  for (const path of ["/start", "/join", "/quiz/strength-age", "/gift", "/login"]) {
    await page.goto(path);
    expect(await hasHorizontalOverflow(page), path).toBe(false);
  }
  await ctx.close();
});

test("cron endpoint requires the secret", async ({ request }) => {
  expect((await request.get("/api/cron/reminders")).status()).toBe(401);
  const ok = await request.get("/api/cron/reminders", { headers: { Authorization: "Bearer e2e-cron" } });
  expect(ok.status()).toBe(200);
});

test("H4: an unsigned text CANCEL is refused (SMS off, no Twilio token)", async ({ request }) => {
  const res = await request.post("/api/sms/inbound", {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    data: "From=%2B15555550123&Body=cancel",
  });
  expect(res.status()).toBe(403);
});

test("H5: the Stripe webhook refuses events when no signing secret is configured", async ({ request }) => {
  const res = await request.post("/api/stripe/webhook", { data: JSON.stringify({ id: "evt_forged", type: "checkout.session.completed", data: { object: {} } }) });
  expect(res.status()).toBe(500);
});

test("L7: logging out revokes the session cookie everywhere", async ({ page }) => {
  await page.goto("/login");
  await page.getByTestId("demo-login").click();
  await page.waitForURL(/\/app/);
  await expect(page.getByTestId("today")).toBeVisible();
  // Log out revokes every session (L7): the old cookie no longer opens the members area.
  const cookies = await page.context().cookies();
  await page.request.post("/api/auth/logout");
  await page.context().addCookies(cookies);
  await page.goto("/app");
  await expect(page).toHaveURL(/\/login/);
});

test("NEW-1: paying at /join with an existing member's email never signs the payer in", async ({ page }) => {
  await page.goto("/join");
  await page.getByLabel("First name").fill("Mallory");
  await page.getByLabel("Email", { exact: true }).fill("  DEMO@strongyears.example ");
  await page.getByTestId("auto-renew-consent").check();
  await page.getByTestId("age-consent").check();
  await page.getByTestId("pay-button").click();
  await page.getByTestId("mock-pay").click();
  await page.waitForURL(/\/checkout\/check-email/);
  await expect(page.getByTestId("check-email")).toBeVisible();
  await page.goto("/app");
  await expect(page).toHaveURL(/\/login/);
  expect((await page.context().cookies()).some((c) => c.name === "sy_session")).toBe(false);
});

test("draft policy pages exist and say so", async ({ page }) => {
  for (const path of ["/terms", "/refunds", "/privacy", "/health-data", "/privacy-choices", "/safety"]) {
    await page.goto(path);
    await expect(page.getByTestId("legal-draft")).toContainText("DRAFT: attorney review required");
  }
});
