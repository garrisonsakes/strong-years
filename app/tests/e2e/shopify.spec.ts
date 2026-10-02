import { createHmac } from "node:crypto";
import { existsSync, readFileSync, rmSync } from "node:fs";
import path from "node:path";
import { expect, test, type BrowserContext, type Page } from "@playwright/test";
import { findGrayOrLowContrastText, hasHorizontalOverflow } from "./helpers";

/**
 * The launch path end to end (Shopify billing): prelaunch → /join refused → waitlist
 * → confirm by email → checkout opens → launch email → its link on another device →
 * Shopify cart with the SAME cell and visitor → orders/paid webhook → sign in with an
 * email code → membership page. Runs on the second webServer (playwright.config.ts).
 */
const BASE = "http://localhost:3101";
const SINK = path.resolve(__dirname, "../../test-results/mail-sink/mail.jsonl");
const SHOP = "https://strongyears-demo.myshopify.com";
const WEBHOOK_SECRET = "e2e-shopify-webhook-secret-0123456789";
const ADMIN = `Basic ${Buffer.from("admin:strongyears-demo").toString("base64")}`;
const EMAIL = `ruth.${Date.now()}@example.com`;

test.use({ baseURL: BASE });
test.describe.configure({ mode: "serial" });

function mails(to: string): { subject: string; body: string; template: string }[] {
  if (!existsSync(SINK)) return [];
  return readFileSync(SINK, "utf8")
    .split("\n")
    .filter(Boolean)
    .map((l) => JSON.parse(l) as { to: string; subject: string; body: string; template: string })
    .filter((m) => m.to === to);
}

async function waitForMail(to: string, template: string) {
  for (let i = 0; i < 50; i++) {
    const m = mails(to).filter((x) => x.template === template).at(-1);
    if (m) return m;
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error(`no ${template} mail for ${to}`);
}

/**
 * Never leaves localhost: /join's redirect is read without following it (Playwright
 * doesn't intercept redirect targets), and anything aimed at a Shopify host is aborted.
 */
async function stubShop(ctx: BrowserContext): Promise<{ urls: string[] }> {
  const seen = { urls: [] as string[] };
  await ctx.route(/myshopify\.com/, (route) => route.abort());
  await ctx.route(/\/join(\?|$)/, async (route) => {
    const res = await route.fetch({ maxRedirects: 0 });
    const loc = res.headers()["location"] ?? "";
    if (loc.startsWith(SHOP)) {
      seen.urls.push(loc);
      await route.fulfill({ status: 200, contentType: "text/html", body: "<html><body><h1>Shopify checkout (test stub)</h1></body></html>" });
    } else {
      await route.fulfill({ response: res });
    }
  });
  return seen;
}

async function checkPage(page: Page) {
  expect(await findGrayOrLowContrastText(page)).toEqual([]);
  expect(await hasHorizontalOverflow(page)).toBe(false);
}

let deviceOneCell = "";
let deviceOneVid = "";

test.beforeAll(() => {
  if (existsSync(SINK)) rmSync(SINK);
});

test("prelaunch: /join and every checkout API refuse; the waitlist shows honest facts only", async ({ page, request }) => {
  await page.goto("/join?platform=ig&page=changyin.strong&post_id=REEL_E2E_01&keyword=JOIN&character=chang&utm_source=ig&utm_medium=bio");
  await expect(page).toHaveURL(/\/waitlist\?.*from=checkout/);
  await expect(page.getByTestId("waitlist-closed-note")).toBeVisible();
  await expect(page.getByTestId("waitlist-opening")).toContainText("opening date isn't set yet");
  await expect(page.getByTestId("launch-countdown")).toHaveCount(0); // no date → no countdown
  await expect(page.getByTestId("waitlist-cohort")).toContainText("Open to everyone until")   // CANON UPDATE 7: no seat cap;
  await expect(page.locator("body")).not.toContainText(/\$1\b|only \d+ left|spots? left today/i);
  const api = await request.post("/api/checkout", { data: { offer: "founding" } });
  expect(api.status()).toBe(403);
  for (const p of ["/checkout/founding", "/gift", "/upsell/program"]) {
    await page.goto(p);
    await expect(page).toHaveURL(/\/waitlist/);
  }
});

test("waitlist page screenshots at 390px and 1280px: no gray text, no overflow", async ({ browser }) => {
  for (const width of [390, 1280]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 } });
    const page = await ctx.newPage();
    await page.goto("/waitlist");
    await checkPage(page);
    await page.screenshot({ path: `screenshots/30-waitlist-${width}.png`, fullPage: true });
    await ctx.close();
  }
});

test("waitlist signup → confirm → checkout opens → launch email → its link on another device lands on Shopify with the same cell", async ({ page, context, browser, request }) => {
  await page.goto("/join?platform=ig&page=changyin.strong&post_id=REEL_E2E_01&keyword=JOIN&utm_source=ig&utm_medium=bio");
  await page.getByLabel("Email", { exact: true }).fill(EMAIL);
  await page.getByTestId("waitlist-submit").click();
  // The consent box is required (browser validation keeps us on the page).
  await expect(page).toHaveURL(/\/waitlist/);
  await page.getByRole("checkbox", { name: /Email me when Strong Years opens/ }).check();
  await page.getByTestId("waitlist-submit").click();
  await expect(page.getByTestId("waitlist-thanks")).toBeVisible();
  const confirm = await waitForMail(EMAIL, "WL1_confirm");
  const link = confirm.body.match(/https?:\/\/\S+\/waitlist\/confirm\?token=[A-Za-z0-9_-]+/)![0];
  await page.goto(link);
  await page.getByTestId("waitlist-confirm-button").click();
  await expect(page.getByTestId("waitlist-confirmed")).toBeVisible();
  await expect(page.getByTestId("referral-link")).toContainText("/waitlist?ref=");
  await page.goto(link);
  await page.getByTestId("waitlist-confirm-button").click();
  await expect(page.getByTestId("waitlist-confirm")).toContainText("expired or was already used");
  const vid = (await context.cookies()).find((c) => c.name === "sy_vid")!.value;
  deviceOneVid = vid.slice(0, vid.lastIndexOf("."));

  // Checkout opens → launch email → its link on ANOTHER device lands on Shopify with the same cell.
  // Open checkout from the admin (same-origin, typed confirmation).
  const open = await request.post("/api/admin/launch", { headers: { authorization: ADMIN, origin: BASE }, form: { confirm: "OPEN" }, maxRedirects: 0 });
  expect(open.status()).toBe(303);
  // Device one: /join now redirects to the Shopify PRODUCT PAGE for this visitor's cell (through the /discount/
  // share link for cell B), with attribution and the visitor id as query parameters the theme stores.
  const landing = (raw: string) => {
    const u = new URL(raw);
    return u.pathname.startsWith("/discount/") ? new URL(u.searchParams.get("redirect")!, u.origin) : u;
  };
  const one = await stubShop(context);
  await page.goto("/join");
  await expect(page.getByRole("heading", { name: "Shopify checkout (test stub)" })).toBeVisible();
  const u1 = landing(one.urls[0]!);
  deviceOneCell = u1.searchParams.get("sku")!;
  expect(["bundle_t12", "bundle_m12", "ebook_e12"]).toContain(deviceOneCell);   // CANON UPDATE 6 adds the 7-day-trial cell t12
  expect(u1.searchParams.get("vid")).toBe(deviceOneVid);
  expect(u1.searchParams.get("post_id")).toBe("REEL_E2E_01");
  expect(u1.pathname).toMatch(/^\/products\/[a-z0-9-]+$/);
  if (deviceOneCell === "bundle_m12") expect(new URL(one.urls[0]!).pathname).toBe("/discount/STARTER12");

  // The launch cron, twice (idempotent): exactly one launch email.
  for (let i = 0; i < 2; i++) expect((await request.get("/api/cron/launch", { headers: { authorization: "Bearer e2e-cron" } })).status()).toBe(200);
  const launch = await waitForMail(EMAIL, "WL_launch_e1");
  expect(mails(EMAIL).filter((m) => m.template === "WL_launch_e1")).toHaveLength(1);
  expect(launch.body).not.toMatch(/\$1\b/);
  const launchLink = launch.body.match(/https?:\/\/\S+\/join\?\S+/)![0];

  // Device two: a fresh browser, no cookies. Same cell, same visitor.
  const ctx2 = await browser.newContext();
  const two = await stubShop(ctx2);
  const p2 = await ctx2.newPage();
  await p2.goto(launchLink);
  await expect(p2.getByRole("heading", { name: "Shopify checkout (test stub)" })).toBeVisible();
  const u2 = landing(two.urls[0]!);
  expect(u2.searchParams.get("sku")).toBe(deviceOneCell);
  expect(u2.searchParams.get("vid")).toBe(deviceOneVid);
  expect(u2.pathname).toBe(u1.pathname);
  expect(u2.searchParams.get("utm_source")).toBe("waitlist");
  // A tampered visitor id in the link is ignored: that browser just gets its own new visitor id.
  const t3 = await browser.newContext();
  const three = await stubShop(t3);
  const p3 = await t3.newPage();
  await p3.goto(launchLink.replace(/sy_v=[^&]+/, "sy_v=00000000-0000-4000-8000-000000000000.abcdef"));
  expect(landing(three.urls[0]!).searchParams.get("vid")).not.toBe(deviceOneVid);
  expect(landing(three.urls[0]!).searchParams.get("vid")).not.toContain("00000000-0000");
  await ctx2.close();
  await t3.close();
});

test("Shopify orders/paid webhook provisions the member; sign in with the emailed code; membership page reads our DB and links to Shopify", async ({ page, request }) => {
  const order = {
    id: 880001,
    email: EMAIL,
    processed_at: new Date().toISOString(),
    customer: { id: 770001, email: EMAIL, first_name: "Ruth" },
    note_attributes: [
      { name: "sy_cell", value: "m12" },
      { name: "sy_ft_post_id", value: "REEL_E2E_01" },
    ],
    line_items: [{ id: 8800011, variant_id: 9000000025, title: "Founding", price: "25.00", quantity: 1, total_discount: "0.00", selling_plan_allocation: { selling_plan: { id: 7000000025 } } }],
  };
  const body = JSON.stringify(order);
  const send = (hmac: string, id: string) =>
    request.post("/api/webhooks/shopify", { headers: { "content-type": "application/json", "x-shopify-topic": "orders/paid", "x-shopify-webhook-id": id, "x-shopify-shop-domain": "strongyears-demo.myshopify.com", "x-shopify-hmac-sha256": hmac }, data: body });
  expect((await send("Zm9yZ2Vk", "e2e-wh-forged-0001")).status()).toBe(401);
  const okRes = await send(createHmac("sha256", WEBHOOK_SECRET).update(body).digest("base64"), "e2e-wh-0001");
  expect(okRes.status()).toBe(200);
  expect((await okRes.json()).status).toBe("processed");

  // Sign in: email → code → members area. No password anywhere.
  await page.goto("/login");
  await expect(page.locator("input[type=password]")).toHaveCount(0);
  await page.getByLabel("Email", { exact: true }).fill(EMAIL);
  await page.getByRole("button", { name: "Email me a sign-in code" }).click();
  await expect(page.getByTestId("login-sent")).toBeVisible();
  const mail = await waitForMail(EMAIL, "magic_link");
  const code = mail.subject.match(/(\d{6})/)![1]!;
  await page.getByLabel("The 6-digit code from the email").fill(code);
  await page.getByRole("button", { name: "Sign me in" }).click();
  await expect(page).toHaveURL(/\/app$/);
  await page.goto("/app/account");
  await expect(page.getByTestId("membership-card")).toContainText("Founding membership");
  await expect(page.getByTestId("membership-status")).toHaveText("Active");
  await expect(page.getByTestId("manage-cancel")).toHaveAttribute("href", "/app/account/cancel");
  await expect(page.getByTestId("refund")).toContainText("14-day money-back guarantee");
  // The cancel flow: ONE save offer (Essentials $12/mo, a request a person applies) beside an equally prominent
  // "Finish canceling" that goes to Shopify's account page. Same size, no third screen, no dark pattern.
  await page.getByTestId("manage-cancel").click();
  await expect(page.getByTestId("cancel-shopify")).toBeVisible();
  const save = page.getByTestId("save-offer");
  const finish = page.getByTestId("finish-cancel");
  await expect(save).toContainText("Essentials, $12 a month");
  await expect(finish).toHaveAttribute("href", "https://shopify.com/00000/account");
  const [sb, fb] = [await save.boundingBox(), await finish.boundingBox()];
  expect(Math.abs(sb!.height - fb!.height)).toBeLessThanOrEqual(2);
  expect(Math.abs(sb!.width - fb!.width)).toBeLessThanOrEqual(2);
  await checkPage(page);
  await save.click();
  await expect(page.getByTestId("cancel-essentials-requested")).toBeVisible();
  await expect(page.getByTestId("cancel-essentials-requested")).toContainText("1 business day");
  const reqMail = await waitForMail(EMAIL, "SH_essentials_requested");
  expect(reqMail.body).toContain("https://shopify.com/00000/account");
  await page.goto("/app/account");
  await checkPage(page);
  for (const width of [390, 1280]) {
    await page.setViewportSize({ width, height: 900 });
    await checkPage(page);
    await page.screenshot({ path: `screenshots/31-membership-shopify-${width}.png`, fullPage: true });
  }
});

