/**
 * Read-only smoke test for a deployed URL. Buys nothing, signs nothing up, sends no
 * email: it only checks that the doors are shut where they must be and open where
 * they should be.
 *
 *   node --experimental-strip-types scripts/smoke.ts https://members.example.com [--live]
 *   (npm run smoke -- https://members.example.com)
 *
 * --live: expect checkout to be open (/join → the Shopify cart). Default: prelaunch.
 * Optional env: CRON_SECRET (adds the health detail), GROWTH_API_TOKEN (checks the endpoint shape).
 */
const args = process.argv.slice(2);
const base = (args.find((a) => /^https?:\/\//.test(a)) ?? "").replace(/\/$/, "");
const expectLive = args.includes("--live");
if (!base) {
  console.error("usage: smoke.ts <https://deployed-url> [--live]");
  process.exit(2);
}

type Check = { name: string; ok: boolean; detail: string };
const results: Check[] = [];
const check = (name: string, ok: boolean, detail = "") => results.push({ name, ok, detail });

async function req(path: string, init: RequestInit = {}) {
  return fetch(`${base}${path}`, { redirect: "manual", ...init, signal: AbortSignal.timeout(15_000) });
}

async function main() {
  const health = await req("/api/health", process.env.CRON_SECRET ? { headers: { authorization: `Bearer ${process.env.CRON_SECRET}` } } : {});
  const hb = (await health.json().catch(() => ({}))) as { ok?: boolean; problems?: unknown };
  check("health is ok (config complete)", health.status === 200 && hb.ok === true, JSON.stringify(hb.problems ?? ""));
  check("site URL is https", base.startsWith("https://"), base);

  const wl = await req("/waitlist");
  const wlHtml = await wl.text();
  check("/waitlist renders the form", wl.status === 200 && wlHtml.includes('action="/api/waitlist"'), String(wl.status));
  check("/waitlist has no $1 trial copy", !/\$1 (today|trial)|for \$1\b/.test(wlHtml));

  const join = await req("/join?post_id=SMOKE_TEST&platform=web");
  const loc = join.headers.get("location") ?? "";
  if (expectLive) check("/join → Shopify cart permalink with attribution", join.status >= 300 && join.status < 400 && /myshopify\.com\/cart\/\d+:1\?/.test(loc) && loc.includes("sy_ft_post_id"), loc.slice(0, 120));
  else check("/join → /waitlist in prelaunch", join.status >= 300 && join.status < 400 && /\/waitlist\?/.test(loc), loc);

  const api = await req("/api/checkout", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ offer: "founding" }) });
  check("in-app checkout API refuses (403 prelaunch / 410 Shopify)", api.status === 403 || api.status === 410, String(api.status));

  const hook = await req("/api/webhooks/shopify", { method: "POST", headers: { "content-type": "application/json", "x-shopify-topic": "orders/paid", "x-shopify-webhook-id": "smoke-0000-0001", "x-shopify-hmac-sha256": "Zm9yZ2Vk" }, body: "{}" });
  check("Shopify webhook refuses a forged HMAC (401)", hook.status === 401, `${hook.status}${hook.status === 503 ? " (SHOPIFY_WEBHOOK_SECRET missing)" : ""}`);

  const stripeHook = await req("/api/stripe/webhook", { method: "POST", body: "{}" });
  check("Stripe webhook refuses unsigned events", stripeHook.status >= 400, String(stripeHook.status));

  const cron = await req("/api/cron/launch");
  check("launch cron requires the secret", cron.status === 401, String(cron.status));

  const growth = await req("/api/growth/posts", process.env.GROWTH_API_TOKEN ? { headers: { authorization: `Bearer ${process.env.GROWTH_API_TOKEN}` } } : {});
  if (process.env.GROWTH_API_TOKEN) {
    const g = (await growth.json().catch(() => ({}))) as { first_touch?: unknown[]; last_touch?: unknown[] };
    check("growth endpoint returns per-post rows", growth.status === 200 && Array.isArray(g.first_touch) && Array.isArray(g.last_touch), String(growth.status));
  } else check("growth endpoint closed without a token", growth.status === 404 || growth.status === 401, String(growth.status));

  const go = await req("/go?p=cy");
  const goHtml = await go.text();
  check("/go bio hub renders", go.status === 200 && goHtml.includes("/waitlist"), String(go.status));
  if (!expectLive) check("/go leads with the free waitlist (prelaunch)", goHtml.indexOf("/waitlist") > -1 && (goHtml.indexOf("/waitlist") < goHtml.indexOf("myshopify.com") || !goHtml.includes("myshopify.com")));
  const b = await req("/b?t=STRONG&p=cy&pid=SMOKE_TEST");
  const bLoc = b.headers.get("location") ?? "";
  if (expectLive) check("/b keyword redirect goes to the store or /join", b.status === 302 && /myshopify\.com|\/join/.test(bLoc), bLoc);
  else check("/b keyword redirect goes to the waitlist with attribution (prelaunch)", b.status === 302 && bLoc.includes("/waitlist") && bLoc.includes("keyword=STRONG") && bLoc.includes("post_id=SMOKE_TEST"), bLoc);

  const admin = await req("/admin");
  check("/admin requires auth", admin.status === 401, String(admin.status));
  const app = await req("/app");
  check("/app requires sign-in", app.status >= 300 && app.status < 400 && (app.headers.get("location") ?? "").includes("/login"), app.headers.get("location") ?? "");

  const login = await req("/login");
  const loginHtml = await login.text();
  check("/login has no password field", login.status === 200 && !/type="password"/.test(loginHtml));
  check("CSP header present", Boolean(login.headers.get("content-security-policy")));

  const bad = results.filter((r) => !r.ok);
  for (const r of results) console.log(`${r.ok ? "PASS" : "FAIL"}  ${r.name}${r.detail ? `  [${r.detail}]` : ""}`);
  console.log(`\n${results.length - bad.length}/${results.length} passed`);
  process.exit(bad.length ? 1 : 0);
}

main().catch((err) => {
  console.error("smoke failed to run:", (err as Error).message);
  process.exit(2);
});
