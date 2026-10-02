# LAUNCH_RUNBOOK.md — the one order of operations (supersedes shopify/RUNBOOK.md, ACCOUNT_SETUP.md, LAUNCH_CHECKLIST.md and app/README.md where they overlap)

Status: Oct 1 2026, integration round. Canon: BRIEF.md CANON UPDATE 2 + 3, OFFER.md §0.1, INTEGRATION.md (decisions and the Shopify doc citations). Nothing in this file has been executed against a live account; every step is for the client or a person the client employs. The K9SUPPS store is never touched (`shopify/src/client.ts` deny list).

The four originals stay for their detail (click paths, account bios, the audit-derived checklist, the app's internals) and each now carries a banner pointing here. **Where they differ from this file, this file wins.**

---

## 0. What launches (one table, every price)

| Thing | Price | Mechanism | Where it is set |
|---|---|---|---|
| Starter Books (7-Day Strength Reset + Sun Yoon's Strong Kitchen, keep forever) | **$12** default; $7 / $15 test cells (one product per cell) | one-time Shopify products; PDFs served by the members app, watermarked | `shopify/config/catalog.ts` EBOOK_CELLS; `app` rows `ebook_e7/e12/e15` |
| **Cell B, the launch default: "$12 today = both books + the first founding month, then $25/mo"** | **$12 → $25/mo** | founding variant on the Shopify Subscriptions "Monthly, renews until you cancel" plan + code **STARTER12** ($13 off the first payment only, once per customer); after the founding close **STARTER12S** on the standard product ($12 → $35) | catalog DISCOUNTS; theme `?view=starter`; app rows `bundle_m12`, `bundle_m12_standard` |
| Cell A, the test cell: books only, founding offer on the thank-you page + 3 emails | $12 one-time, then an optional $25/mo checkout | arm A in the theme; email 1 from the members app, 2–3 from the launch cron | `FUNNEL_ARMS`; `app` `SH_books_e1` |
| Founding Membership | **$25/mo**, locked while subscribed; **5,000 cap** = real inventory on the variant | Shopify Subscriptions monthly plan | catalog `founding-membership`; `FOUNDING_CAP` |
| Standard Membership (after the cap or the close date) | **$35/mo** | same plan; `npm run close-founding` flips it on | catalog `strong-years-membership` |
| Founding Annual (offered after renewal 1) | **$249/yr** | Shopify Subscriptions yearly plan | catalog `founding-annual` |
| Essentials (the save offer) | **$12/mo** | monthly plan; switched by a person within 1 business day from the app's cancel page | catalog `essentials-membership`; `app/src/lib/billing/planChange.ts` |
| Gifts | **$49 / 3 mo, $119 / 12 mo**, prepaid, never renew | one-time product, 2 variants, recipient properties | catalog `gift-strong-years` |
| Bumps (optional, never pre-ticked) | **$9** Wall Plan (digital) · **$29** kit (physical, stock 0 until kits arrive) | one-time products | catalog `the-wall-plan`, `strong-years-kit` |
| Refund | 14-day money-back guarantee on the membership charge, once per person; books/printables on request within 14 days; kit 30 days | self-serve in the members app (Admin API `refundCreate`); the contract is cancelled by a person in Apps → Subscriptions | `app/src/lib/billing/shopify.ts` |

**Not used / off by default:** the $1 trial (gone everywhere), Shopify's Digital Downloads app (cannot watermark), the one-click post-purchase app (`shopify/app-postpurchase/`, beta; needs access approval; never fires on digital-only or wallet/PayPal orders), the app-engine selling plans (`SUBSCRIPTION_ENGINE=app`, needs a billing scheduler nobody has built), Stripe (`BILLING_PROVIDER=stripe`, behind the adapter), SMS until 10DLC clears.

## 1. Order of operations (D−30 → D0)

| When | Step | Who | Detail in |
|---|---|---|---|
| D−30 → D−29 | Entity, bank, EIN, domains (`strongyears.com`, `members.strongyears.com`), company email aliases, 1Password vault, insurance quotes | client | LAUNCH_CHECKLIST.md §1 items 6–8 |
| D−28 → D−22 | Social accounts (3 IG, 3 FB Pages, Threads, TikTok, YouTube, X), AI-disclosure settings, ManyChat, upload-post, pipeline OAuth; bios link to `/go?p=…` / `/tt` (runway mode) | client | ACCOUNT_SETUP.md §1–10 |
| D−21 (or D−14 / D−7, client decision) | Runway starts: pages post, waitlist CTA, `LAUNCH_MODE=prelaunch`, `CHECKOUT_OPENS_AT` set | ops | ORGANIC_ENGINE.md §1, RUNWAY_SCRIPTS.md |
| D−21 → D−10 | **Members app deploy** (§3), Supabase migrations in name order (incl. `20261001120000_shopify_cell_b_integration.sql`), `/api/health` green, `/waitlist` and `/go` live | DEV | app/README.md |
| D−14 → D−10 | **Shopify store** (§2 steps 1–10): create, domain, Payments, customer accounts, install Shopify Subscriptions, create the Strong Years Offers app, provision (dry run → live), push the theme, create the 2 plans in the Subscriptions app, `npm run verify`, load the catalog into `shopify_products` | client + DEV | shopify/RUNBOOK.md §2 |
| D−10 | Legal: counsel reviews the generated policies and the 50-state auto-renewal matrix; ToS, privacy, health-data policy; reviewer and performer contracts | counsel | LAUNCH_CHECKLIST.md §1 items 2–4, 11, 14, 15 |
| D−10 | SMS 10DLC + toll-free registration submitted (3–6 weeks); email domain warm-up starts; warm-list counsel sign-off | DEV / client | LAUNCH_CHECKLIST.md items 22–24 |
| D−7 | Statement descriptor `STRONGYEARS MEMBER`; notifications (order confirmation terms block, Subscriptions 3-day reminder on); crisis roster and support tool live | DEV / client | §2 steps 13–14 |
| D−3 | **Money QA in Shopify test mode** (§6): the 7 test orders incl. `/b` and `/join` landing on the product page with the code applied, the renewal order ("Bill now") extending access, the refund, the cancel flow | DEV | §6 |
| D−1 | Go / no-go (§9) | client | |
| **D0 07:00 ET** | Disable test mode, remove the store password; admin "Open checkout now" (or `CHECKOUT_OPENS_AT` passes); bios flip by themselves (`/go` reads the launch state); WAITLIST → BOOK DM variant | client + ops | ORGANIC_ENGINE.md §5 |
| D0+ | Launch cron (≤3 emails + 2 pushes in 72 h), reminders cron hourly, growth KPIs in `/admin#launch`; day-10 / day-40 gates on net revenue per visitor + renewal 1 | ops | BLITZ.md §11, §13 |

## 2. Shopify store (what shopify/RUNBOOK.md §2 says, with the integration changes applied)

Steps 1–9 as in shopify/RUNBOOK.md (store, domain, Shopify Payments + PayPal, **new customer accounts**, install **Shopify Subscriptions** only, Dev Dashboard app "Strong Years Offers", `.env`, `npm run provision` dry run then `DRY_RUN=false npm run provision`, theme push). Then:

- **Step 10, plans:** in Apps → Subscriptions create "Monthly, renews until you cancel" (1 month, no plan discount; products: Founding Membership, Strong Years Membership, Strong Years Essentials) and "Yearly, renews until you cancel" (1 year; Founding Annual). Payment retries: 3 attempts, 3 days apart, then cancel. Run `npm run verify`: it checks the plans, confirms STARTER12 and STARTER12S exist, makes the 4 products subscription-only and writes `out/members-catalog.<store>.json` (now with `product_handle` and `discount_code`). Load it into `shopify_products`.
- **Step 11, Digital Downloads: skip.** The members app delivers every PDF (watermarked) once `orders/paid` arrives. Do not attach files in Shopify.
- **Step 12, post-purchase app: skip at launch.** Keep `shopify/app-postpurchase/` deployed only if the client later wants to test the one-click page on cell A after Shopify's access approval.
- **Step 13, thank-you block:** Settings → Checkout → Customize → Thank you → Add app block → "Founding offer" (URL `https://strongyears.com/products/founding-membership`, price $25); repeat on Order status. This is cell A's offer surface.
- **Step 14, notifications:** order confirmation gets the FUNNEL.md §5.5 B2 terms block inside `{% if subscription %}`; Apps → Subscriptions → Settings → Notifications: 3-day reminder on (the members app's conditional reminder goes out as well).
- **Steps 15–18** unchanged (kit stock when kits arrive; counsel review; test orders per §6; go live).

`ARM_TEST_ON=false` on provision shows every visitor the default (arm B, cell e12); the default `true` splits B/A 50/50, sticky per visitor.

## 3. Members app (Vercel or any Node host; Supabase)

Required env on a real deploy (`app/.env.example` documents all 100+): `NEXT_PUBLIC_SITE_URL`, `MAILING_ADDRESS`, `EMAIL_FROM`, `SUPPORT_EMAIL`, `SESSION_SECRET` (32+), `CRON_SECRET`, `ADMIN_USER`, `ADMIN_PASSWORD` (+ `ADMIN_TOTP_SECRET`), `ANTHROPIC_API_KEY` (or the chat stays offline), `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`, `RESEND_API_KEY` or Postmark, `VAPID_PUBLIC_KEY` / `VAPID_PRIVATE_KEY`, `RATE_LIMIT_KV_URL` / `_TOKEN`.

Shopify block (one table, same values on both sides):

| Variable | Value | Also used by |
|---|---|---|
| `BILLING_PROVIDER` | `shopify` | |
| `SHOPIFY_STORE_DOMAIN` | `<store>.myshopify.com` (bare host) | shopify/ `SHOPIFY_STORE` |
| `SHOPIFY_WEBHOOK_SECRET` | the Strong Years Offers app's **Client secret** (Shopify signs webhooks with it; not configurable per subscription) | shopify/ `SHOPIFY_CLIENT_SECRET` |
| `SHOPIFY_ADMIN_TOKEN` | the app's Admin API token (read_orders, write_orders, read_customers, read_inventory, **write_inventory, write_products**); refunds + the founding seat ledger (renewal/refund → +1 seat; stock 0 → continue selling) | |
| `SHOPIFY_LOCATION_ID` | the numeric id of the location holding the founding variant's stock (Settings → Locations; also in the first `inventory_levels/update` payload). Without it, the seat ledger opens a ticket instead of adjusting (Round 5) | shopify/ `r.ids.location` from the dry run |
| `SHOPIFY_API_VERSION` | **`2026-07`** | shopify/ provisioning uses 2026-07 |
| `SHOPIFY_CUSTOMER_ACCOUNT_URL` | the new customer-accounts URL (`https://shopify.com/<id>/account`) | theme `links` metafield |
| `SHOPIFY_GRACE_DAYS` | `7` — also the float after `current_period_end` during which an "active" Shopify row still grants access while a late renewal order may arrive; after it, `/api/cron/reminders` expires the row (Round 5: a cancel/pause/dunned-out contract on Shopify's side sends us no webhook) | |
| `SUBSCRIPTION_ENGINE` | `shopify_subscriptions` | shopify/ `SUBSCRIPTION_ENGINE` |
| `FRONT_END_CELLS` / `FRONT_END_DEFAULT_CELL` / `FRONT_END_CELL_TEST` | `m12,e12` / `m12` / `true` | theme arms via the `cells` metafield (`ARM_TEST_ON`) |
| `FOUNDING_COHORT_CAP` / `FOUNDING_CLOSE_DATE` | `5000` (= the founding variant's inventory) / default 2027-01-09 | catalog `FOUNDING_CAP`, `FOUNDING_CLOSE_DATE` |
| `LAUNCH_MODE` / `CHECKOUT_OPENS_AT` | `prelaunch` until D0 / the real opening moment | |
| `GROWTH_API_TOKEN` | 40+ chars, shared with `workers/growth` | n8n growth workflow |
| `MEMBERS_APP_URL` (shopify/) | `https://members.strongyears.com` → webhooks go to `/api/webhooks/shopify` | |

Cron: `/api/cron/launch` every 15 min, `/api/cron/reminders` hourly, `/api/cron/lifecycle` hourly at :05 (lifecycle emails), `/api/cron/digest` at 11:00 and 12:00 UTC (the 7am ET digest, sent once per ET day) (`vercel.json`), all with `Authorization: Bearer $CRON_SECRET`.

Ops round additions (same deploy): `EXCEPTIONS_API_TOKEN` (40+ chars, shared with the workers' `APP_URL` client), `GROWTH_WORKER_URL` + `WORKER_TOKEN` (the app reads `/growth/summary` for `/admin/today` and forwards boost approvals), `DIGEST_EMAIL` (or `ONCALL_EMAIL`), `LIFECYCLE_ENABLED` (default on). Admin screens: `/admin/today` (numbers, top/weakest posts, governor and the BLITZ §9/§11 readouts) and `/admin/exceptions` (every decision a person makes, with an append-only audit trail; approving a boost writes the governor's approval record). Affiliates: `/affiliates` (apply), approval in `/admin/exceptions`, statement CSV at `/api/admin/affiliates/statement?month=YYYY-MM`; the Shopify code for each approved affiliate is created by a person (the approval note says exactly how). One-click unsubscribe (RFC 8058) at `/api/unsubscribe`.

**Ops stack (Hetzner, `deploy/`):** `hcloud server create … --user-data-from-file deploy/cloud-init.yaml` → clone the repo → fill `deploy/.env` and `deploy/secrets.env` from the vault (`deploy/secrets.example.env` lists every secret by issuer) → `make check-secrets` → `make db-migrate DRY_RUN=1`, then `make db-migrate` (schema.sql, schema_growth.sql, app migrations; idempotent; RLS verified; `BOOTSTRAP=1` only on plain Postgres) → `make up` (n8n queue mode + Postgres + Redis, workers incl. the DM bot, the assembly worker, Caddy). `make n8n-import` keeps every publishing node disabled until `LAUNCH_MODE=live`; the growth workflow has no spend node.

## 4. Webhooks (the contract; `shopify/config/webhook-topics.json`)

Registered by provisioning, handled by the app, tested on both sides:

| Topic | Fires | The app does |
|---|---|---|
| `orders/paid` | every paid order, **including Shopify Subscriptions renewal orders** (`source_name` contains `subscription`) | provisions books / membership / gift / bump lines; a renewal extends `current_period_end` by one period and **gives the founding seat back** (`inventoryAdjustQuantities` +1, idempotent by reference URI; renewal orders decrement inventory like any order); cell B is recognised by the STARTER12/STARTER12S code on the order; a line whose refund arrived first grants nothing |
| `orders/cancelled` | an order cancelled in the admin | voids its lines; ends the membership it started |
| `refunds/create` | every refund (there is no `orders/refunded`) | marks lines refunded; a full membership refund ends the membership; ticket to cancel the contract; a refund of the seat-consuming first founding charge (NO_RESTOCK) gives the seat back; a refund that arrives before its `orders/paid` is parked (`shopify_early_refunds`) |
| `customers/update` / `customers/delete` | profile changes / deletion | email + name follow (with re-verification); unlink on delete |
| `inventory_levels/update` | the founding variant's stock | the founding counter's DB mirror; **at 0 the founding variant is switched to "continue selling"** (so existing members' renewals never fail with insufficient inventory, which Shopify checks on every billing attempt) and a ticket says to run `close-founding` |
| `app/uninstalled` | the app is removed | on-call ticket |
| `subscription_contracts/*`, `subscription_billing_attempts/*` | **only for contracts the subscribing app owns** (`read_own_subscription_contracts`); registered only when `SUBSCRIPTION_ENGINE=app` | enrichment of status; never the source of access |

A cancel or pause made on Shopify's account page is seen as the absence of the next renewal order: an "active" Shopify row grants access only until `current_period_end` + `SHOPIFY_GRACE_DAYS`; the hourly reminders cron then marks it `expired` and emails "your membership has ended" (conditional wording); a later renewal order revives it.

## 5. Links

- `/b?t=<keyword>&p=<page>&pid=<post>&mc_id=…&utm_*` (every DM, Story, pinned comment, affiliate card): prelaunch → `/waitlist`; live → the visitor's cell on the store (cell B through `https://<store>/discount/STARTER12?redirect=/products/founding-membership?view=starter…`; cell A to `/products/strong-years-starter-books…`; JOIN → the plain founding page; FAMILY → the gift page). Never a cart permalink.
- `/go?p=cy|sk|cs|yt-cy|…` and `/tt`: the bio-link hub; runway mode shows the free waitlist first, launch mode the starter books.
- `/join`: the same redirect without a keyword. Shopify's own `/join` redirect goes to `/products/founding-membership` (the plain $25 page).
- Emails and thank-you blocks link to product pages, never to `/cart/…`.

## 6. Money QA (Shopify test mode, card 4242 4242 4242 4242)

(a) `/b?t=BOOK` as an arm-A visitor (`?arm=A` once on the store): the books page, $12, pay → `orders/paid` → email `SH_books_e1` → sign in → `/app/printables` shows both books, watermarked. The thank-you block shows the founding offer.
(b) `/b?t=BOOK` as an arm-B visitor: lands on `/products/founding-membership?view=starter` with STARTER12 applied; the page says $12 today then $25/mo; tick consent; checkout total **$12**; the contract's next charge shows **$25**; order note attributes carry `sy_cell=m12`, `sy_sku=bundle_m12`, `sy_vid`, `sy_consent_sha`; founding inventory 5000 → 4999; the members app shows a founding membership at $25 with both books downloadable and `welcome_kit_starter_2500.pdf`.
(c) `/join` → the plain founding page, $25.
(d) Apps → Subscriptions → the (b) contract → **Bill now**: a renewal order arrives as `orders/paid` with `source_name subscription_contract`; the members app extends `current_period_end` by a month; **the founding variant's available stock goes back up by 1** (Products → Founding Membership; if it doesn't, a `support_tickets` row says why: scopes or `SHOPIFY_LOCATION_ID`). **Confirm the renewal charged $25, not $12** (the `recurringCycleLimit: 1` proof).
(d2) Set the founding variant's stock to 0 by hand → `inventory_levels/update` → the variant shows "Continue selling when out of stock" and a ticket says to run `close-founding`; set the stock back to 5,000 and switch the policy back to "Stop selling" before go-live.
(d3) Cancel the (b) contract on the customer account page, then `curl -H "Authorization: Bearer $CRON_SECRET" /api/cron/reminders` with the clock past period end + 7 days (or set `SHOPIFY_GRACE_DAYS=0` on the test deploy): the member's `/app` goes to `/app/account?lapsed=ended` and the "membership has ended" email is in the outbox.
(e) Gift 3 months with recipient properties → the recipient's claim email.
(f) Refund (b) from the members app within 14 days → `refundCreate` succeeds, access ends, a ticket says to cancel the contract in Apps → Subscriptions; do it; confirm no further renewal.
(g) The members app cancel page: "Switch to Essentials" and "Finish canceling" are the same size; the switch creates a `plan_change_requests` row + ticket + email; "Finish canceling" opens the Shopify account page where the cancel takes two taps. After a second paid month the account page offers "Switch to yearly: $249" the same way (request → a person sends the annual checkout and ends the monthly plan the day it is paid).
(i) Returning customer: with the (b) email, open the starter page again; the page says the $12 does not apply a second time; checkout shows $25; `orders/paid` maps it to `founding_monthly` with no mismatch ticket (the consent record is "12.00|25.00"). A signed-in member with a starter order is sent to the plain page by `/b` and `/join`.
(j) Disputes: in test mode trigger a chargeback on (b) → access ends, ticket; mark it won → access restored.
(h) Reminders cron with a membership 47 hours before renewal: the email is the conditional one ("if your membership is still active…") and links to the Shopify account page.

## 7. Content and product gates

- Products: `python3 products/_build/build_all.py` (rebuilds every PDF, copies the served ones into `app/content/downloads/`, runs the safety audit: must print `Unresolved: 0`). No `$1`, "for life", $19.99, $99 or "$25 or $30" anywhere.
- Scripts and prompts: `python3 tools/build_content.py` validation; nothing publishes unjudged (BRIEF.md CANON: scanner → LLM judge → human).
- Reviewer gate: only FALLBACK strings until `REVIEWER_SIGNED=true` and a signed contract exist.
- Lifecycle emails (`app/content/lifecycle/sequences.json`, 12 sequences) and the DM flows (`workers/dm/flows/`, 14 keywords) must pass `cd workers && python3 -m compliance templates ../app/content/lifecycle/sequences.json dm/flows/*.json` (also in the workers suite and `make validate-content`). The crisis texts are pinned verbatim by tests instead (the scanner routes any suicide mention to a human by design).
- DM bot: Meta App Review per `workers/dm/APP_REVIEW.md`; `DM_SEND_ENABLED=0` until it is approved (the outbox shows what would be sent). When API publishing is off, `POST /package/fallback` builds the manual post pack (per page/platform, uniqueness-approved variant, AI-label checklist, Business Suite + Buffer CSVs).
- Production: `production/refs/manifest.json` (Chang 24, Sun 24, duo 6; sha256-locked) and `production/refs/ACCEPTANCE.md`; `render_refs.py` and `voices/design_voices.py` are DRY_RUN until a person runs them with keys; `production/shot_list/plan_week.py` builds the D−21…D−15 queue and fails unless the compliance CLI passes; the performer call sheet (`production/performer/call_sheet.csv` / `.html`, 205 clips) and 60 no-face B-roll prompts are ready for the shoot and the first renders.
- Counsel: `TEMPLATES/affiliate_agreement.md` (draft) before the first affiliate approval.

## 8. Test suites (all green before go-live)

`cd app && npm run typecheck && npm run lint && npm test && npm run build && npm run test:e2e` · `cd shopify && npm run check` · `cd workers && python3 -m pytest` · `python3 products/_build/build_all.py`.

## 9. Go / no-go (D−1)

All of: §6 (a)–(h) passed on the test store · counsel sign-off on policies and the matrix · entity, bank, insurance bound · `/api/health` 200 · crisis roster covering 07:00–23:00 ET with the honest overnight line on `/safety` · AI disclosure on every account · bios load `/go` · the founding counter reads the real inventory · no gray text / no formulaic kickers on any page (the screenshot check reports 0 issues) · the K9SUPPS store untouched.

## 10. Client decisions still open

Closed in the round-5 follow-up (no decision needed): R5-7 "reply cancel" promise, R5-8 consent record, R5-9 disputes, R5-10 no-JS consent marker, R5-11 one seat per contract, R5-12 gift redeem, R5-13 sheet input, R5-14 DB schedule guard, and the founding → annual request path.

Runway length (7 / 14 / 21 days); `FOUNDING_CLOSE_DATE` (default 2027-01-09); whether to test $30 (only if cell data supports it); whether cell A's one-click page is worth the access request later; overnight crisis coverage; the seeded-list plan (BLITZ.md §13.4: ~20K names + $1,500/day pulls $100K to day 30 on central inputs); affiliate app choice with recurring-commission support for Shopify Subscriptions orders.

## 11. Test counts and the variants / scorecard round (Oct 2 2026)

**Round of Oct 2 2026 (modular variants, Trial Reels, scorecard, block-level learning, Facebook native, accessibility).** workers **647 passed, 0 failed, 0 skipped** (Postgres 16 up, so the schema SQL suites ran; was 611) · tools plan/posting-rules tests **21** (was 16) · `python3 tools/validate_plan.py`: 13,800 placements + 4,768 variant rows, **OK** · `python3 tools/posting_rules.py`: 0 problems, 97% of page-days have a morning and an evening prime slot.

What changed and how to run it:
- **Variants** (`workers/growth/variants.py`, `uniqueness.guard.check_variant`, `tools/posting_rules.check_variants`): roles TEST / PLACEMENT / REMIX; same body never twice on one page × surface in 30 d; Trial Reels 3/day (weeks 1–2), 6/day (week 3), then 12/day (config `variants.trial_reels_per_page_day`, max 20); every IG publish stops at 90/24 h. `POST /growth/variants` returns a master's gated Trial Reels with `trial_params` (one SS_PERFORMANCE per page × body). Graduation at 6 h: `variants.graduate`.
- **Plan**: `python3 tools/build_posting_plan.py` writes `posting_plan_90d.csv` (placements; FB rows are `fb_native` or `fb_long`) and `posting_plan_variants_90d.csv` (Trial Reels + FB text/photo). Full-cadence capacity per page per day: 6 masters → 36 placements + 12 Trial Reels + 1 FB text + 1 FB photo (2 of the 6 FB videos are 60–180 s long cuts); network 24 masters, 200 posts/day. Cost: COSTS.md §2b (+$12.60/day).
- **Scorecard** (`workers/growth/scorecard.py`, table `post_scores_components`, RLS deny-by-default): `POST /growth/scorecard` scores each read at 1/6/12/24 h and 7 d (0–100 per component, conversion weighs most; IG under 24 h is provisional; YouTube uses engagedViews) and queues the actions (`actions.scorecard_plan`: new bodies, new hooks, remix to all pages + boost watch, topic slot doubling, 14-day gene bench passed to `/growth/allocate` as `benched`). Adapters now ingest IG `reels_skip_rate`, the FB retention graph and first plays, and YT `engagedViews`.
- **Weekly** (Monday, ops): export last week's 24 h scorecard rows joined to `script_id`, run `python3 tools/refit_gate.py --scores <file>` (dry run; review `data/content/refit_gate_report.json`; `--apply` writes `data/content/rubric_weights.json`, which `tools/virality.py` loads), then `POST /growth/readout` posts the plain-English readout to `/admin/exceptions` as type `growth_readout`. **The members app must add `growth_readout` to `EXCEPTION_TYPES`** (app/src/lib/exceptions.ts) before that post is accepted; until then the call returns an error status and the readout text is still in the response. The 1 h → 24 h predictor (`growth/predict.py`) refuses to train below 200 posts.
- **Accessibility** (assembler preflight, `assemble/accessibility.py`): captions ≥ 56 px, hook text ≥ 72 px cap height (104 px Figtree ExtraBold), ≥ 7:1 contrast, music muted in every speech span, ≤ 2.5 words/s, 300 ms sentence pauses. The ElevenLabs request (`voice.tts_request` and the n8n "Build Voice Lines" node) caps `voice_settings.speed` at 0.95 and inserts the pause tag; verify on the live voices that `speed` and `[short pause]` behave on eleven_v3 [A].
- Pre-existing, not from this round: `python3 tools/build_content.py` fails at HEAD with `KeyError: '_proven'` in the wave2 validation (line 1216).

### Ops round (Oct 1 2026)

app unit 595 (37 files) · app e2e 18 · app lint, typecheck and build clean · shopify 128 + Theme Check 0 offenses · workers 611 · compliance CLI templates 258/258 strings pass (lifecycle 78, DM flows 180) · runway week D−21…D−15: 37 scripts pass. Supabase migrations: 9 (incl. `20261001200000_ops_exceptions_lifecycle_affiliates.sql`), applied twice on a scratch Postgres 16 by `make db-migrate` with RLS verified on both databases.
