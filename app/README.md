# Strong Years — MVP web app

The membership, funnel and members area for **Strong Years** (Chang Yin & Sun Yoon, openly AI characters). Built from `../BRIEF.md` (incl. BLITZ addendum), `../OFFER.md`, `../FUNNEL.md` §0–3, 5–7, `../CHARACTERS.md` §1–6, 9, 11 and `../SAFETY_RULES.md`.

**Stack:** Next.js 15 (App Router, TypeScript strict) · Tailwind 3 · Supabase Postgres (+ RLS) · Stripe Checkout / Billing / Customer Portal / webhooks · Anthropic Claude (Haiku 4.5) · Resend or Postmark · Twilio · Meta CAPI (server-side) · Vitest · Playwright.

Everything runs with **zero keys**: each integration that has no env vars becomes a local stub, and a brass "Demo mode" banner says exactly which ones.

| Missing env | What happens instead |
|---|---|
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | In-memory store, seeded with rows flagged `is_demo` (resets on restart) |
| `STRIPE_SECRET_KEY` | Built-in checkout simulator at `/checkout/mock/:id` that emits the same `checkout.session.completed` event through the real webhook handler; a "billing clock" simulates renewals |
| `ANTHROPIC_API_KEY` | Local dev / in-memory demo (`ALLOW_RULES_ONLY_CHAT=true`): scripted in-character replies, rules still run. Any other deploy: the chat is offline (988 / 911 / Eldercare Locator / a human) |
| Resend / Postmark / Twilio keys | Messages are written to the `outbox` table (visible in `/admin`) |
| `META_PIXEL_ID` / `META_CAPI_TOKEN` | Events are stored in `analytics_events` only |

---

## Blitz mode (default, BRIEF.md "BLITZ CANON")

- **One primary offer:** the founding membership at `/join`, with the first month charged today and a 14-day money-back guarantee. The price is locked while the member stays subscribed. JOIN DMs, ads and every CTA route here.
- **Price test:** $25 vs $30, assigned 50/50 by an FNV hash of the sticky `sy_vid` cookie. The same visitor always sees the same price. The cell is logged on exposures, checkout intents and memberships; `/admin` shows visitors, checkouts, members, refunds and MRR per cell. With the test off, everyone sees $25.
- **Cohort cap:** 5,000 by default, counted from the real DB (founding memberships, minus refunds). Once the cap is reached, new members pay `STANDARD_PRICE_CENTS` (default $35) and get no founding lock.
- **Order bumps on `/join`:** $7 Reset, $17 Kitchen and $9 Wall Plan, all unticked and one-time. The $27/$29 upsells and the $7 downsell are unchanged.
- **Switched off (but still built):** the $1 trial arm and the standalone `/reset` and `/kitchen` pages. They redirect to `/join`.
- **Real product content:** `src/content/sessions.json` (DP01–DP14, 4 tracks, gentle-day swaps) drives Today. `kitchen_recipes.json` drives Sun Yoon's Kitchen: a breakfast, a main and a soup each week, with USDA grams and a merged grocery list.
- **PDFs:** stored in `content/downloads/`, not `public/`, and served by `/api/downloads/:file` only to entitled members. The Welcome Kit and Reset PDFs are rendered once per price ($25/$30 founding, $35 standard; the $1 trial renews at $25), so the billing text always matches what the member pays. Every download is watermarked with the buyer's name, email and order number (pdf-lib) and logged in `download_events`.
- **Processors:** Stripe is implemented. The Braintree adapter is a stub behind the same `PaymentProcessor` interface. Routing is `failover` or a deterministic `split`, with a rolling 30-day volume cap per processor. If every processor is over its cap, the checkout routes to the one with the most headroom and on-call is alerted.
- **SMS:** consumer texts are recorded as `skipped` until `SMS_ENABLED=true`. The 48-hour reminder goes by email, and the checkout terms say "by email".

---

## Shopify launch path (CANON UPDATE 2 + 3, Oct 1 2026) — the default

> **Order of operations, env vars, webhook topics and prices for the whole launch live in `../LAUNCH_RUNBOOK.md`** (the merged runbook; `../INTEGRATION.md` has the decisions and the Shopify doc citations). This section only describes what the app does.

Commerce runs on our own Shopify store (Shopify Payments, the free Shopify Subscriptions app). This app is the members area, the waitlist, the bio-link hub, the `/b` redirect and the attribution layer, provisioned by Shopify webhooks. Stripe stays in the repo behind the adapter (`BILLING_PROVIDER=stripe`) but is not the launch path. **No $1 trial anywhere** (`blitz.trialArmEnabled` is hard-wired off; the trial strings left in Stripe-mode components are unreachable).

| Piece | Where |
|---|---|
| Provider adapter | `src/lib/billing/provider.ts` (id, interface, config checks), `shopify.ts` (catalog, cells, product-page redirect, Admin API, refund), `stripe.ts`, `active.ts` |
| Webhooks | `POST /api/webhooks/shopify` → `src/lib/billing/shopifyWebhook.ts`; the topic contract is `../shopify/config/webhook-topics.json` (`tests/unit/webhook-contract.test.ts`) |
| Checkout | `/join` and `/b` → 302 to the store's **product page** for the visitor's sticky cell (`src/lib/shopCheckout.ts`): cell B through `https://<store>/discount/STARTER12?redirect=/products/founding-membership?view=starter&arm=B&vid=…&<attribution>`; cell A to `/products/strong-years-starter-books?arm=A&cell=e12&…`. Never a cart permalink (selling plans don't work with them). In-app checkout routes answer 410 / redirect to `/join` |
| Bio links | `/go?p=cy|sk|cs|yt-cy…` (runway mode: free waitlist first; launch: the starter books first), `/tt` (TikTok alias), `/b?t=<keyword>&p=&pid=&mc_id=&ref=` (`src/lib/bioLinks.ts`, `src/app/b/route.ts`) |
| Sign-in | `/login`: one email with a 6-digit code **and** a one-time link, matched to the Shopify customer email. No password |
| Membership page | `/app/account` reads our DB; card / pause / the final cancel step link to `SHOPIFY_CUSTOMER_ACCOUNT_URL`; `/app/account/cancel` shows ONE save offer (Essentials $12/mo as a request a person applies within 1 business day, `src/lib/billing/planChange.ts`) beside an equal-size "Finish canceling"; the 14-day refund is self-serve (Admin API `refundCreate`; the contract itself is cancelled by a person on the launch path, because only the owning app can) |
| Downloads | `/app/printables` + `/api/downloads/:file`: every PDF (the Starter Books for `ebook_*` and `bundle_m12*` orders, the welcome kit, programs) served from `content/downloads/`, watermarked (pdf-lib) and logged. Shopify's Digital Downloads app is not used |
| Launch | `LAUNCH_MODE=prelaunch|live`, `CHECKOUT_OPENS_AT`, admin "Open checkout now"; `/waitlist` (+ `/thanks`, `/confirm`, `/confirmed`, `/starter`, `/unsubscribe`); `/api/cron/launch` every 15 min (≤3 emails + 2 pushes in 72 h) |
| Reminders | `/api/cron/reminders`: before every charge it re-checks the order data (`renewalCertainty`) and, on the launch path, words the email conditionally ("if your membership is still active…", link to Shopify's account page), because a cancel made on Shopify's page never reaches us as an event |
| Growth engine | `GET /api/growth/posts` (Bearer `GROWTH_API_TOKEN`) and the SQL view `growth_post_kpis` (service role only); `/admin#launch` shows per-post KPIs, waitlist size, post-launch conversion |
| Conversion events | `src/lib/conversions` (Meta CAPI + TikTok Events API, outbox, `event_id` dedup, consent-only, hashed email only) |

### `shopify_products` (the catalog table; `../shopify` `npm run verify` writes it as `out/members-catalog.<store>.json`)

| sku | entitlement | Shopify object | price | cell | cohort | discount_code |
|---|---|---|---|---|---|---|
| `ebook_e7` / `ebook_e12` / `ebook_e15` | ebook | the three Starter Books products (one price each) | $7 / $12 / $15 one-time | e7 / e12 / e15 | – | – |
| `founding_monthly` | founding | "Founding membership" variant, **inventory = 5,000 (the cap), track inventory, don't sell when out of stock**; the Subscriptions app's "Monthly, renews until you cancel" plan | $25/mo | – | founding | – |
| **`bundle_m12`** (launch default) | founding | **the same variant + the same monthly plan** + the STARTER12 first-payment-only code | $12 → $25/mo | m12 | founding | STARTER12 |
| `standard_monthly` / `bundle_m12_standard` | standard | "Membership" variant, monthly plan; the starter row uses STARTER12S | $35/mo · $12 → $35/mo | – / m12 | standard | – / STARTER12S |
| `essentials_monthly` | essentials | monthly plan on the Essentials product (the save offer) | $12/mo | – | – | – |
| `annual_founding` | annual | yearly plan, offered after renewal 1 | $249/yr | – | – | – |
| `gift3` / `gift12` | gift | one-time, line-item properties "Recipient name", "Recipient email", "Message" | $49 / $119 | – | – | – |
| `wallplan` | bump | optional cart add-on | $9 | – | – | – |

Two rows may share (variant, selling plan) and differ by `discount_code`; `matchLine` picks the row whose code is on the order, else the row without a code. A code never maps a line to another variant or plan. `product_handle` is where `/b` and `/join` send people.

### Webhooks (what the app relies on vs what it only enriches)

Registered by `../shopify` provisioning, exactly `../shopify/config/webhook-topics.json`:
- **Core (store-wide; the source of truth):** `orders/paid` (initial orders AND every Shopify Subscriptions renewal order, `source_name` containing `subscription`: it extends `current_period_end` by one period), `orders/cancelled`, `refunds/create` (Shopify's real refund topic; `orders/refunded` does not exist), `customers/update`, `customers/delete`, `inventory_levels/update` (the founding counter's DB mirror), `app/uninstalled`.
- **Enrichment (only when `SUBSCRIPTION_ENGINE=app`):** `subscription_contracts/*`, `subscription_billing_attempts/*`. They require `read_own_subscription_contracts` and fire only for contracts our own app owns. They refine status; they never grant or revoke access by themselves.
- A cancel or pause made on Shopify's account page therefore shows up as **no renewal order**: access lasts to `current_period_end` (+ `SHOPIFY_GRACE_DAYS` after a failed renewal that we learn about), then lapses.

### Webhook guarantees

HMAC of the raw body (fails closed with no secret: 503), shop-domain check, 1 MB cap. Idempotent by `X-Shopify-Webhook-Id` **and** by business keys (order line × kind, origin order, contract `revision_id`, billing attempt id), so a signed body replayed under a new webhook id changes nothing. A contract/billing event that arrives before its order answers 503 (Shopify retries). A failed renewal opens a `SHOPIFY_GRACE_DAYS` grace period, after which access stops until a payment succeeds.

## Run it locally

```bash
cd app
npm install
npm run build && npm start      # http://localhost:3000  (or: npm run dev)
```

- Landing: `/start`; founding checkout: `/join` (in standard mode `?arm=A|B` picks the trial vs founding arm)
- Quizzes: `/quiz/strength-age`, `/quiz/gut-energy` (Meta-safe aliases for ads: `/q/a`, `/q/b`)
- Front ends: `/reset` ($7), `/kitchen` ($17), `/gift` ($49 / $119 prepaid)
- Members: `/login` → "Enter the demo member area" (demo mode only), or buy anything and you're signed in
- Admin: `/admin` — basic auth, default `admin` / `strongyears-demo` only while running on in-memory demo data (**with Supabase configured, `ADMIN_PASSWORD` and `SESSION_SECRET` are required or admin and the members area stay locked**)
- Cron: `GET /api/cron/reminders` with `Authorization: Bearer $CRON_SECRET`

## Tests

```bash
npm run typecheck      # tsc --noEmit (strict + noUncheckedIndexedAccess)
npm run lint           # eslint (next/core-web-vitals + typescript)
npm test               # vitest: 583 unit tests
npm run test:e2e       # playwright: 14 legacy Stripe-path tests (port 3100) + 4 Shopify launch-path tests (port 3101)
npm run smoke -- https://members.example.com [--live]   # read-only checks against a deployed URL
npm run screenshots    # 13 key pages × 390px and 1280px → screenshots/ (+ checks.json)
```

Unit tests cover: quiz scoring (Strength Age formula, norms, clamps, profile routing, safety screen / Safe Mode, questionnaire-only estimate; Gut & Energy dimensions, tie-break, red-flag stop, protein target), crisis classifier (keyword, LLM merge, fixed referral text, scope limits, output guard, chat pipeline logging + human alert, opt-in memory), pricing & consent (both arms, front ends, gifts, terms text, unticked consent, 18+, SMS, founding cap, Meta-safe CAPI payloads, UTM/mc_id), the webhook handler (fulfilment, idempotency, trial conversion, dunning, refund, dispute, cancel, gift, signature verification) and the cancel flow (≤2 screens, one save offer, cancel/undo/pause/downgrade, refund window, 48-hour reminder job, billing clock, Strong Weeks streaks with grace).

The Playwright smoke test also asserts **no gray or low-contrast text** on the landing page (computed colour + contrast ≥ 4.5:1 on every text node), buttons ≥ 48px, no horizontal overflow at 390px, and that "Finish canceling" is the same size as the save offer. `screenshots/checks.json` runs the same contrast/overflow check on all 26 screenshots (currently: 0 issues).

---

## Environment variables

See `.env.example` (every variable is documented there). Required on every real deploy (any `NODE_ENV` other than `development`/`test`, unless it's a local in-memory demo marked `LOCAL_DEMO_BUILD=true`): `NEXT_PUBLIC_SITE_URL` (https, your domain), `MAILING_ADDRESS`, `EMAIL_FROM`, `SUPPORT_EMAIL`, `SESSION_SECRET` (32+ chars), `CRON_SECRET`, `ADMIN_USER`, `ADMIN_PASSWORD`, `ANTHROPIC_API_KEY` (or the chat stays offline), plus the Supabase pair and the Stripe pair. With any of the first eight missing or a placeholder, email is refused, the boot log says so, and `GET /api/health` returns 503 (names of the bad variables with `Authorization: Bearer $CRON_SECRET`). Live Stripe keys are refused unless `ALLOW_LIVE_STRIPE=true`.

## Deploy: Supabase + Stripe (test mode) + Vercel

**1. Supabase**
1. Create a project. Run every file in `supabase/migrations/` in name order (or `supabase db push`): the base schema, blitz processors, audit fixes, Round 7 (email verification, crisis clear) and Round 8 (`founding_holds` + the `reserve_founding_spot` / `confirm_founding_spot` functions). Validated against Postgres 16, RLS on every table.
2. Copy the project URL and the **service-role** key into `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` (server-only; never expose it to the browser). `anon`/`authenticated` roles get no table access; the public cohort count is the `founding_cohort_count()` RPC.

**2. Stripe (test mode)**
1. Create products/prices (or skip — the app falls back to inline `price_data` for everything except the $8 partner seat). Checkout always charges the quoted amount with inline `price_data` (L3), so price IDs are optional. If you create them for reporting: Founding $25 and $30 (the blitz test cells), Standard $35 (after the founding cap), the $1 trial renewing at $25, Essentials $12, Partner $8, and the founding Annual $249 (from L35, not sold in the app yet). Put the IDs in `STRIPE_PRICE_*`.
2. Settings → Billing → Customer portal: enable cancel (immediately at period end), update payment method, invoices. Optional `STRIPE_PORTAL_CONFIGURATION`.
3. Statement descriptor: `STRONGYEARS` (suffix `MEMBER` is set on one-off charges).
4. Webhook endpoint `https://<domain>/api/stripe/webhook` with events: `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.expired`, `customer.subscription.created`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`, `charge.refunded`, `charge.dispute.created`. Put its signing secret in `STRIPE_WEBHOOK_SECRET`.
5. Local testing: `stripe listen --forward-to localhost:3000/api/stripe/webhook`, and use Stripe **test clocks** to fast-forward trials.

**Test cards:** `4242 4242 4242 4242` (success, any future date/CVC) · `4000 0025 0000 3155` (3-D Secure) · `4000 0000 0000 0002` (declined) · `4000 0000 0000 0341` (attaches, then fails on renewal → dunning) · `4000 0000 0000 0259` (succeeds, then disputed → chargeback path).

**3. Vercel (or any Node host)**
1. Import the repo, root directory `app/`. Framework: Next.js. Node 22.
2. Add the env vars (Production + Preview), including every "required" one above. `NEXT_PUBLIC_SITE_URL` = your https domain. Never set `LOCAL_DEMO_BUILD` on a real deploy.
3. Point the host's health check / uptime monitor at `/api/health` (503 = unsafe config). After deploy, open it once with the cron secret and confirm `{"ok":true}`.
4. Rate limits: set `RATE_LIMIT_KV_URL` / `RATE_LIMIT_KV_TOKEN` (Upstash Redis REST). **Recommended for any multi-instance deploy, including Vercel**; without it each instance counts on its own.
5. Client IP (rate limits, admin lockout): nothing to do on Vercel, Fly, Netlify, Render, Railway, Heroku or Cloud Run (detected). Behind anything else set `TRUSTED_PROXY_HOPS`, `TRUSTED_PROXIES` or `CLIENT_IP_HEADER` (`TRUST_CLOUDFLARE=true` behind Cloudflare); the boot log warns if none applies.
6. Admin: set `ADMIN_USER`, a long `ADMIN_PASSWORD`, and ideally `ADMIN_TOTP_SECRET` (type the 6-digit code after the password).
7. `vercel.json` schedules `/api/cron/reminders` hourly (Vercel Cron sends `Authorization: Bearer $CRON_SECRET`). On the Hobby plan crons are daily-only — use Pro, or an external scheduler, so the 48-hour reminder lands on time.
8. Resend/Postmark: verify the sending domain (SPF/DKIM). Twilio: A2P 10DLC brand + campaign registration before sending (1–3 weeks); set the Messaging Service inbound webhook to `https://<domain>/api/sms/inbound` (makes "text CANCEL" work; signature-verified with `TWILIO_AUTH_TOKEN`).

---

## What's built (map to the brief)

**Funnel**
- `/start`: every FUNNEL.md §2 section — disclosure strip, hero (product-led phone UI + "Example" Strength Age card), candor block, honest problem, mechanism, a day inside, **Where should I begin?** (8 pain → session tiles), Strength Age explainer + example chart, meet the characters (labelled "AI character · illustration placeholder", no stock faces), value stack with honest anchors, pre-launch "no fake reviews" block, who it's for / not for, pricing, guarantee, FAQ, final CTA, mobile sticky bar. Reviewer gate: only FALLBACK strings render until `REVIEWER_SIGNED=true` **and** reviewer names are set.
- Pricing: arm A ($1 × 7 days → $25/mo while the founding cohort is open, the standard $35 after; every price on every page comes from `lib/livePricing.ts`, the same quote checkout charges) and arm B (founding: $25 or $30 today, 14-day money-back, price locked while subscribed, pauses included) side by side, 50/50 by default (`ARM_B_SHARE`), assigned arm first; **live cohort counter from the DB** (founding memberships started minus refunded; closes the arm at the cap). $7 Reset / $17 Kitchen attach a 7-day included trial (arm A) or first month charged today (arm B, the blitz setting). Gifts: prepaid, no auto-renew, recipient redemption with fresh consent.
- Auto-renew disclosure next to every CTA; checkout has the full terms box directly above the pay button, a **separate unticked** consent checkbox, an 18+ checkbox, and optional unticked SMS consent (TCPA text). The exact rendered terms, price, first-charge date, IP and UA are stored in `consent_log`.
- Quizzes: full FUNNEL §3 question sets, timers for the chair stand and balance stages, autosave + "Start over", safety screen → Safe Mode (P6, no number, doctor summary page, no bump/upsells), walker/wheelchair route, adult-child overlay, questionnaire-only estimate; Gut quiz red-flag stop screen (no email gate, no offer). Email + optional SMS opt-in. Results framed as a fitness estimate.
- Checkout → Stripe Checkout (subscription w/ trial for A; immediate first charge for B; payment mode for gifts; one-time lines added to the first invoice) → one-click upsells on the saved card ($27 keep-forever program → $7 printables downsell → $29 kit; gift flow shows the kit first) → welcome page with terms repeated.

**Members area `/app`** — Today's Daily Practice (video placeholder, steps with support cue / easier version / breath cue / stop rule, 4 tracks, sore knee / sore back / low energy swaps, too easy/too hard levelling), first-72-hours checklist, Strong Weeks streak with automatic grace week + "sick/traveling" protection, monthly retest (6 tests, same formula as the quiz, big-drop → Rebuild track + human check-in) with trend chart and table view, Sun Yoon's Kitchen (weekly recipes, grocery list, graded remedy, caution lines), 6 programs with week tracker, printables (weekly plan, grocery list, fridge chart, exercise cards), partner seat (+$8 with its own consent), settings (reminder time/channel, SMS opt-in, **memory: view, delete one, delete all**, opt-in toggle), account (plan, next charge, portal, self-serve refund inside the window, undo/resume).

**AI chat `/app/chat`** — persistent "AI character, not a doctor" banner; 18+ gate; pipeline per message: crisis classifier (regex + Claude classifier, most severe wins) → fixed referral text (988 / 911 / Eldercare Locator) + `crisis_events` row + support ticket + on-call alert (Slack/SMS/email) → scope guard (medication, diagnosis, red-flag symptoms get fixed safe replies) → Claude with a system prompt built from the CHARACTERS.md voice cards + SAFETY hard rules → output guard (doses, med changes, diagnoses, "I'm human", dependency lines) → opt-in memory extraction (health facts flagged sensitive). "Talk to a human" on every chat page.

**Cancel `/app/account/cancel`** — Screen 1: optional reason or "Skip and cancel now". Screen 2: exactly one save offer (Essentials $12 for price; pause 1–3 months otherwise) beside an equal-size "Finish canceling". Cancels immediately (no future charges, access to period end), confirmation + email, undo, refund link if in window. Also `/account` short link, and **text CANCEL** (Twilio inbound webhook `/api/sms/inbound`; STOP turns texts off). 48-hour pre-charge reminder job (trials, included periods, arm-B first renewal; 30-day notice for annual).

**Admin `/admin`** — MRR (by arm, gifts excluded), paying/active by arm, trials + conversion rate, founding cohort, churn, cancel-flow saves, refunds, chargebacks + 30-day ratio, revenue, leads; crisis/support log with "mark handled"; open tickets; Stripe event log; outbox.

**Analytics** — UTM + `mc_id` + `fbclid` captured first-touch in middleware and carried onto the member; Meta CAPI server events `Lead`, `StartTrial`, `Purchase`, `Subscribe` only; URLs aliased (`/q/a`, `/q/b`, `/checkout`…); any custom field containing a condition word is dropped; quiz answers and health data are never sent; emails hashed.

**Design** — palette from the characters' world (Paper, Ink, Persimmon, Jade, Brass-as-background-only), Fraunces + Atkinson Hyperlegible (self-hosted via @fontsource), 20px base, 60px buttons, 3px focus ring, **no gray in the Tailwind theme at all**, no `//`, no mono, no tracked caps kickers.

## Needs real keys / humans before launch
- Supabase project; Stripe test → live keys, price IDs, portal config, webhook secret; `ALLOW_LIVE_STRIPE=true` only on launch day. A second processor before $5K/day spend (OFFER.md 3.1).
- Anthropic key (chat currently scripted); Resend/Postmark domain; Twilio 10DLC registration; Meta pixel + CAPI token.
- On-call human + `ONCALL_*` targets (crisis alerts currently go to the outbox).
- Real character stills/videos (Mux or similar) to replace the labelled placeholders; a real human demonstrator where form accuracy matters.
- Signed credentialed reviewer before flipping `REVIEWER_SIGNED`; verify the Friendship Line number; US consumer-protection attorney review of checkout/trial/cancel (FUNNEL.md 0.5).
- Not built yet: annual-plan upgrade campaigns, Courtyard community, Sunday Premiere / Wednesday live embeds, winback sequence scheduling, native app wrapper.

## Audit fixes (Sep 30 2026)

See `../AUDIT_CODE.md` (Fix status column). Operational notes:

- **Webhooks fail closed.** `STRIPE_WEBHOOK_SECRET` is required; `DEV_ALLOW_UNSIGNED=true` only for local dev.
- **Refunds** are only reported once Stripe confirms. Anything else becomes a `refund_review` ticket in /admin. One money-back guarantee per person (email or card fingerprint).
- **Gifts** are claimed from a private link emailed to the recipient; codes only re-send that link. Gifts to paying members become account credit.
- **Members area** requires an active entitlement (`src/lib/entitlement.ts`).
- **Crisis classifier**: `src/lib/safety/crisis.ts`, corpus in `tests/fixtures/crisis_corpus.ts`. Without `ANTHROPIC_API_KEY`, ambiguous messages are treated as possible crises.
- **On-call hours**: `ONCALL_HOURS` / `ONCALL_TZ`; the chat and `/safety` state them honestly. Set `24/7` only once a real rotation or BPO covers nights.
- **Rate limits** are keyed on the trusted client IP (never one shared bucket) and are per instance unless `RATE_LIMIT_KV_URL/TOKEN` (Upstash REST, recommended for multi-instance) is set.
- **Policy pages** (`/terms`, `/refunds`, `/privacy`, `/health-data`, `/privacy-choices`, `/safety`) are drafts marked "DRAFT: attorney review required".
- Apply the new migration `supabase/migrations/20260930120000_audit_fixes.sql` (the app table is now `sy_orders`).

## Pipeline database vs app database (AUDIT H11)

The content pipeline's `schema.sql` (repo root) has its own `orders` table for DM/UTM attribution. The app's purchase table is `sy_orders`. Keep the two in **separate Supabase projects** if you can. If they have to share one, the different names keep them from colliding.

## Final-verifier fixes (AUDIT_FINAL.md)

- **NEW-1, checkout takeover:** checkout never signs anyone into an account that existed before it, and never writes a Stripe customer or card onto another member. A purchase made with an existing member's email is parked as `pending_verification`, grants no access, and the inbox owner gets a confirm / "this wasn't me" link (`/checkout/verify`). Emails are canonicalised (NFKC, case, whitespace, invisible characters) everywhere.
- **Crisis detector:** phrase rules plus a concept co-occurrence layer with negation, history, hypothetical and exertion-question suppression and a recent-turn context window. Measured on held-out sets written after each freeze: A 50.0% recall / 10.0% FP, B 68.3% / 10.0%, C (live) 70.0% / 8.3%. Rules alone don't reach the 95% / 5% target, so **production chat refuses to run without `ANTHROPIC_API_KEY`** (the fail-closed model classifier sits on top).
- **Round 7, chat outage:** every deploy that isn't local dev (any `NODE_ENV` other than `development`/`test`) needs the model. With no key, an API error or a timeout (classifier: one attempt, 2.5 s), a message the rules don't flag gets no coach reply at all: the chat shows the offline message (988, 911, Eldercare Locator 1-800-677-1116, "Talk to a human"), opens a `chat_offline_review` ticket and pages on-call once an hour. Only the in-memory demo build with `ALLOW_RULES_ONLY_CHAT=true` (e2e, screenshots) keeps scripted replies.
- **Round 7, "That's not what I meant":** under each resources reply (so 988 / 911 are always shown first) the member can clear a benign phrase that tripped the rules, within 24 hours, once. The crisis event, alert and follow-up ticket stay (the admin shows "Member said: not what I meant"); the message is un-flagged and the coach answers it. On a real deploy a model that is ≥0.8 confident it is a crisis keeps the resources up instead.
- **Round 8, founding cap:** a founding checkout takes a spot atomically when its checkout session is created (`reserve_founding_spot()` under a Postgres advisory lock; a mutex on the in-memory store). The hold lasts 45 minutes, the Stripe page 30, and fulfilment confirms the spot under the same lock; `checkout.session.expired` frees it early. A buyer who loses the race is stopped before paying ("Nothing was charged … now $35.00 a month") and sees the standard price on reload. A payment confirmed after its hold lapsed and its spot was retaken is not founding and opens a `refund_review` ticket.
- **Round 8, admin lockout:** client IP only from trusted proxy headers (Vercel `x-real-ip`, or `TRUSTED_PROXY_HOPS` / `TRUSTED_PROXIES`); failures counted per IP and per username; after 5, waits double from 1 minute to 1 hour, during which even the right password is refused. Optional `ADMIN_TOTP_SECRET` second factor.
- **R2-1, pre-account hijack:** typing an email at checkout proves nothing. A checkout for an email nobody has verified gets a 2-hour purchase-scoped session (upsells, receipt) that can't read the account; the welcome email carries a one-time link that verifies the inbox. The first inbox proof (login link, gift claim, purchase confirmation) sets `members.email_verified_at` and bumps `session_version`, killing every earlier session. Full sessions require a verified email.
- **Web push (PWA):** `public/sw.js`, `manifest.webmanifest`, opt-in after the first session and in Settings, a daily-practice nudge at the member's reminder hour (08:00–20:00 local, only if today's session isn't done), and a push copy of every pre-renewal reminder. Set `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY` (`npx web-push generate-vapid-keys`).
- **Watermarked downloads:** every PDF is stamped with the buyer's name, email and order id on every page (pdf-lib) and logged in `download_events`.
