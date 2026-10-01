# AUDIT_FINAL: pre-handoff verification (Sep 30 2026)

This is an independent final check. I re-ran every suite myself. Each critical and high finding was probed directly: the "Fix status" columns in AUDIT_CODE.md and AUDIT_BUSINESS.md were not taken on trust. I edited no repo files; this report is the only file I wrote.

Two things touched the repo, both as instructed:
- **`tools/build_content.py`** regenerated its outputs. They came out byte-identical, checked by md5.
- **`npm run build`** refreshed `app/.next`.

All probe scripts, logs and scratch databases lived outside the repo. The databases were dropped afterwards.

**Verdict in one line: NOT READY for live traffic.** One new critical defect needs fixing first: any buyer can take over an existing member's account by paying with that member's email. Two "fixed" findings regress on inputs outside their own test corpora: crisis-detector recall and scanner bypass. Everything else that remains is blocked on the client (keys, accounts, attorney, reviewer, cash).

---

## 1. Test results

| Suite | Command | Result |
|---|---|---|
| App lint | `npm run lint` | **PASS**, 0 problems |
| App typecheck | `npm run typecheck` | **PASS** |
| App unit | `npx vitest run` | **PASS**, 347/347 in 16 files. The C2 corpus prints 0/107 benign FPs |
| App build | `npm run build` | **PASS**, 59 routes, middleware 35.7 kB |
| App e2e | `npx playwright test` (Chromium from `/opt/pw-browsers`) | **PASS**, 12/12 in 14.1 s |
| Workers | `make test` | **PASS**, 206 passed in 141 s. This includes the 17 SQL tests, which run against the local Postgres 16 and are not skipped |
| Workers SQL (explicit) | `pytest tests/test_schema_sql.py` | **PASS**, 17/17 |
| Content tool | `python3 tools/build_content.py` | **PASS**, "VALIDATION: PASS". 150 scripts, 40 ads, 390 hooks; 23 regexes found 0 blocked claims; 0 fall/percentage hits |
| Compliance CLI | `python -m compliance scan ../data/content/scripts.json ../data/content/ad_scripts.json` | **PASS**, 190/190 pass (150 organic, 40 ads). `selftest`: ALL OK |
| Products audit | `products/_build/audit.py`, read-only (`build_all.py` has no check-only mode and would rewrite outputs) | **PASS**: STRUCTURAL CHECKS all passed on 73 sessions; Unresolved: 0 |
| Prototype | Playwright at 390×844, touch, full click-through plus jump to every step | **PASS**: 0 JS/console errors; 0 gray or low-contrast text; 0 overflow across 34 snapshots (see §4) |

The green suites don't cover what failed below. Each failure was reproduced with inputs that aren't in the repo's own fixtures.

---

## 2. Critical and high findings: verified status

### 2a. AUDIT_CODE

| ID | Verified | Evidence (my probe) |
|---|---|---|
| **C1 gift-code takeover** | **PASS** (gift path) | `POST /api/gift/redeem` with a code never sets a session cookie. It only emails a single-use claim link to the recipient (`lib/gifts.ts`); a bad code gives a 303 to `?error=code` with no session. The gifter receipt has no code or link, and the outbox redacts both (`secrets:`). Claiming is atomic (`updateWhere … redeemed_at null`). **But the same class of bug is still open through checkout. See NEW-1.** |
| **NEW-1 account takeover through checkout** | **FAIL, critical** | Reproduced live on `next start` in mock mode. Victim "Victoria" joins and chats (`VICTIM-SECRET my knee hurts after my hip surgery`). The attacker, in a fresh browser, runs `/join` again with **the victim's email** and pays. They land in `/app` as Victoria (`Greeting name: Victoria`) and **see the victim's chat history (`true`)** and the victim's other membership row. Cause: `fulfillCheckoutIntent` → `upsertMember` matches the existing member by typed email, and `/api/checkout/complete` mints a session for that member (`complete/route.ts`, M2 block). The path is the same with live Stripe. It also overwrites the victim's `stripe_customer_id` and `stripe_payment_method` with the attacker's (`members.ts:70-71`). The cheapest entry is the T25 cell: **$1**. **Fix:** when `intent.email` matches a pre-existing member and the buyer isn't already signed in as that member, don't set the cookie. Send a magic link instead, and never overwrite an existing customer or payment method from an unauthenticated checkout. |
| **C2 crisis-detector recall** | **FAIL** | I wrote 40 new realistic crisis messages, none of them in `tests/fixtures/crisis_corpus.ts`, and ran them with the model unavailable (the launch default without `ANTHROPIC_API_KEY`). **Recall was 29/40 (72.5%).** Missed: "I've decided I'm not going to be here by Christmas", "i keep thinking the world would be better without me in it", "no one would even notice if I died", "I've been hoarding my oxycodone for when I'm ready", "wish i could just fall asleep and not wake up", "I've been thinking of jumping off my balcony", "my left arm is tingling and my chest feels like it's being squeezed", "I've been lying on the kitchen floor for hours, can't get up", "my granddaughter forged my signature on checks", "someone from the bank got me to wire them $20,000…", "my son keeps me locked in the basement". If a model wrongly returns "none", 25/40 stay flagged. On 40 new benign messages there were **4 crisis false positives**: "I had a heart attack 5 years ago… cleared to exercise", "I can't breathe through my nose because of allergies…", "What should I do if I feel dizzy during a session?", "My friend passed out flyers…". There was also 1 grief-level flag. The 100%/0-FP result holds only on the repo's own corpus, so the lexicon is overfit. **Fix:** require the LLM classifier (key present, fail-closed) in production; add the misses above as a held-out set; add patterns for method and plan ("jump off", "hoarding … for when"), "better without me", confinement, forgery and wire scams, and "squeezed". |
| **C3 schema anon access** | **PASS** | I applied `schema.sql` to a fresh Postgres 16 with **Supabase-style default privileges**: `alter default privileges … grant all … to anon, authenticated, service_role`, which the repo's own SQL test doesn't simulate. Results: `anon` can SELECT 0 of 34 relations; `authenticated` has write grants on 0; every table has RLS. anon can execute only `is_reviewer()` (harmless, invoker, reads its own JWT claim). No definer function lacks `search_path`. `get_publish_token`, `delete from blocked_claims`, `update prompt_versions` and `select dm_leads` all return "permission denied"; `vault.decrypted_secrets` is denied. The app migrations (with an `auth` stub) give anon SELECT on 0 of 21; authenticated has only column-scoped self-row grants (M13 OK). |
| **C4 refund integrity** | **PASS** (code + tests + live mock) | `refundMembership` works like this: it is scoped to the `membership_id` and the guarantee window, and capped at price plus trial fee. It resolves the PaymentIntent from Stripe. If the processor is live and there's no PI, it opens a ticket with no email. It marks orders refunded and emails only when the processor returns `succeeded`; `pending` waits. A mock PI on a live key is refused. Live mock run: refund gives `?refund=done`. Webhook: an early `invoice.paid` returns 409. Residual (low): if `subscriptions.cancel` throws after the refund succeeds, the ledger and membership update are skipped. |
| **H1 refund scope** | **PASS** | Same code: `membership_id` filter, window filter and budget cap. |
| **H2 entitlement checks** | **PASS** | Live: buy, then self-serve refund. After that, `/app`, `/app/chat`, `/app/programs` and `/app/printables` all go to `/join?lapsed=refunded`, and `POST /api/chat` returns **403**. |
| **H3 gift vs billing membership** | **PASS** (tests + code) | `applyGift` credits a payer through the Stripe balance and never adds a "current" gift row; `expireGifts` runs in the cron in every mode. |
| **H4 unsigned text CANCEL** | **PASS** | e2e #9: refused while SMS is off with no Twilio token. |
| **H5 webhook signature** | **PASS** | Live server with `STRIPE_WEBHOOK_SECRET` set. No header: 400. **Signed with the empty key: 400.** Signed with a wrong key: 400. Correct key: passes verification (then the handler returns 500 on the bogus intent, as expected). Without a secret: 500 (e2e #10). `DEV_ALLOW_UNSIGNED` is ignored on Vercel production and with live keys. |
| **H6 Braintree/mock in prod** | **PASS** | A production build without the e2e flag gives `/checkout/mock/*` → 404 and `mock-complete` → 404, even with `BRAINTREE_ENABLED=true`. |
| **H7 1000-row cap** | **PASS** (tests + code) | `find` pages with `.range()`; the volume guard runs as a SQL sum. |
| **H8 fulfilment race** | **PASS** (tests + code) | Atomic `open→fulfilling` claim plus unique keys (`fulfill.ts:67`). |
| **H9 worker auth, SSRF, path traversal** | **PASS** | FastAPI TestClient. No `WORKER_TOKEN`: `/qa`, `/files` and `/health/details` return 503, and `/health` returns only `{"ok":true}`. With a token: no or wrong header gives 401. All 16 SSRF and local-read vectors return 422: `/etc/passwd`, `file://`, `file://localhost`, `../`, `OUTPUT_DIR/../..`, `http://169.254.169.254`, `https://169.254.169.254`, `127.0.0.1.nip.io`, `evil.r2.dev.attacker.com`, `attacker.com#.r2.dev`, `x.r2.dev@127.0.0.1`, `[::ffff:169.254.169.254]`, `localhost`, `gopher://`, `0x7f000001`, `metadata.google.internal`. All 6 `brief_id` traversals return 422, all 5 `/files` traversals return 404, and no escaped directory was created. Residual (low): the wildcard allowlist `.r2.dev` / `.cloudfront.net` admits attacker-owned buckets; the magic sniff limits the impact. Also DNS is resolved in `check_url` and again by httpx (a rebinding TOCTOU window). |
| **H10 scanner look-alike bypass** | **FAIL** | I built 10 new bypass strings with no condition word, so the obfuscated verb is what gets tested. Python scanner: **4/10 blocked**. Caught: small caps `ᴄᴜʀᴇs`, math bold `𝐜𝐮𝐫𝐞𝐬`, circled `Ⓒⓤⓡⓔⓢ`, `c/u/r/e/s`. **Pass through:** `cüres`, `c—u—r—e—s` (em dashes), `c*res`, `Detöx your liver`, `cu+U+0301res` (combining acute → `cúres`), `mírácle`. Controls without obfuscation all block. The repo's regression case "ćures arthritis" passes only because of the condition-word rule C-07; "ćures you overnight" is **not** blocked. The n8n JS pre-scan catches 3/9 of the same strings. Cause: `textnorm.canon` keeps precomposed Latin accents on purpose (to protect Spanish), and `_SPACED_RX` has no em dash or single-letter censor. **Fix:** fold diacritics in a *match-only* variant (NFKD, strip Mn) for en-US rules; add `—–` to the separators; treat a `*` inside a word as a wildcard for banned stems; mirror all of this in the n8n JS. |
| **H11 `orders` collision** | **PASS** | The app uses `sy_orders`, and the app migrations apply cleanly next to `schema.sql`'s `orders`. |
| **H12 external refunds and disputes** | **PASS** (tests + code) | |

### 2b. AUDIT_BUSINESS (critical and high)

| ID | Verified | Evidence |
|---|---|---|
| F01 core product not built | **PARTIAL, blocked on client** | Now built: `products/daily_practice_sessions_1-30.md/.pdf`; all six 12-week programs (`products/programs/*.md/.pdf`); `VIDEO_PRODUCTION_QUEUE.json` (73 videos, 659 base minutes, **≈$6.3K** at the standard tier). **No member video is rendered.** Rendering needs the client's generation keys and cash. `LAUNCH_CHECKLIST.md:15` still says "14 session scripts only" (stale). |
| F02 kill rule vs base case | **PASS** | BLITZ_OPS.md:1185 recalibrated to $125 on L4–L7 and $110 on L8–L14. |
| F03 optimistic stack | **PASS** | BLITZ.md §1: R5 central is the planning base and R4 the upside; R7 is the 3-cell gated launch. |
| F04 pre-churn MRR | **PARTIAL** | "Retained MRR" is in the model (BLITZ.md, the CSV). The `/admin` dashboard has no refund-window or renewal-adjusted MRR (LAUNCH_CHECKLIST #19 Partial). |
| F05 $30 headline | **PASS** | $25 is central; $30 is the upside. |
| F06 cash trough | **PASS** | 360-day engine; troughs stated (for example −$380K on day 215 for R7 central). |
| F07 founding annual $99 | **PASS in docs, not built** | $249 from L35 in OFFER, FUNNEL and BLITZ. The app has no annual offer (`config.ts:131 annual: 11900` is an unused constant). Not needed before L35. |
| F08 refund abuse | **PARTIAL** | Built: day-15 vesting (`entitlement.ts:75`), one guarantee per person (email or card fingerprint), and add-ons outside the self-serve refund. **Watermarking isn't built**: `/api/downloads` serves one shared file, yet FUNNEL copy promises "watermarked with your email" (§3). |
| F09 text CANCEL while SMS off | **PASS in app**, 1 doc leftover | Every app surface is gated on `messaging.smsEnabled`. The live-event script BLITZ_OPS.md:658 is still ungated. |
| F10 "every renewal" claim | **PASS** | Reminders now go before every charge (M7), so the claim is true. |
| F11 CA annual reminder | **PASS** | `clock.ts:27` sends a yearly notice to monthly members. |
| F12 privacy / Lead event | **PASS** (code); counsel pending | Lead fires on the neutral `/q/a` path; `/privacy`, `/health-data` and `/privacy-choices` exist and are marked as drafts. |
| F13 no ToS | **PARTIAL, blocked on attorney** | A draft `/terms` exists and is marked "attorney review required". |
| F14 AI-companion law | **PASS** (code); coverage decision open | 3-hour re-disclosure (`chat.ts:68`); `/safety` is published; `ONCALL_HOURS` wording is honest. 24/7 coverage is a client decision. |
| F15 condition hashtags / "58% FEWER FALLS" | **PASS** | Hashtag inventory across SCRIPTS, scripts.json, ADS_SCRIPTS, HOOKS, products and the prototype: **no condition hashtags** (e.g. `#fallprevention` 0, `#kneepain` 0). "FEWER FALLS" appears 0 times. |
| F16 ad-account feasibility | **OPEN, blocked on client** | Spend starts at $3K/day (gated). Account choice and limit confirmation belong to the client (LAUNCH_CHECKLIST #27). |
| F17 no retention triggers before SMS | **FAIL / open** | There's no PWA or web push in the app (no service worker or manifest). LAUNCH_CHECKLIST #25 says "Missing". |

---

## 3. Remaining canon contradictions (file:line)

I swept 385 .md/.json/.py/.ts/.tsx/.html files, excluding node_modules, .next, the raw scraped research data under `data/` (except `data/content/`) and the AUDIT_* files. These items came back clean:
- **"30-day money-back"**: 0.
- **"Doña Toña"**: 0.
- **"Fall-Proof"**: 0.
- **"Master" as Chang's title**: 0. All 34 hits are video "master" files or "never Master" rules.
- **Condition hashtags in content**: 0.
- **Fall-outcome claims in customer copy**: 0. The only hits are internal evidence notes and rule definitions.
- **Ungated "reviewed by licensed", "licensed humans" or "revisado por"**: 0. All 63 hits are inside `[ONLY PUBLISH ONCE…]` gates, `reviewerGate()` or rule files.
- **cure/detox/instantly in customer copy**: only myth-bust (MB-EX) or negation uses, plus "delivered instantly" (PDF delivery, FUNNEL.md:13).
- **Keyword count**: 12 everywhere (FUNNEL.md:60, :204; BLITZ_OPS.md:15), and scripts.json uses exactly those 12.
- **Handles**: `@changyin`, `@sunyoon.kitchen` and `@changandsun` on day 1; `.strength` and `.mobility` on day 15; `@sunyoon` on day 22; `.espanol` on day 30. Consistent, except item 16 below.
- **Standard price**: $35 everywhere.
- **Gift price**: $49 / $119 everywhere.

**Contradictions still present (23):**

| # | File:line | Contradiction |
|---|---|---|
| 1 | BLITZ_OPS.md:658 | Live-event H3 script: "you can cancel online in two screens, **or by texting CANCEL**". It isn't gated on SMS, and the event runs on L3 while SMS is off. |
| 2 | FUNNEL.md:638 | Standalone `/kitchen` page: "**30-day guarantee**". The canon says add-ons are refunded on request within 14 days, and "guarantee" may appear only as "14-day money-back guarantee". |
| 3 | app/src/components/Pricing.tsx:67 | Customer-facing bullet "Founding price locked **for life** of your membership". The canon (OFFER.md §0.1) says "locked while subscribed… never 'for life'". It renders on `/start` and on the quiz result. |
| 4 | BRIEF.md:45, :51 | The canon text itself still says "founding price locked for life" and "$20–25 charged today". OFFER.md §0.1, the updated canon, says never "for life" and $25/$30. |
| 5 | app/README.md:27 | "Reset PDFs rendered… **$20 for the trial arm**". The canonical trial is $1 → $25 (T25). |
| 6 | app/README.md:73 | "Recommended recurring prices: Monthly $20, **Founding $20**… Annual $119". The canon is founding $25/$30, standard $35 and annual $249. |
| 7 | app/README.md:93 | "arm A ($1 × 7 days → **$20/mo**) and arm B (**founding: $20 today**…)" |
| 8 | EXPANSION.md:69 | US-Hispanic price at the $20 tier. The US blitz price is $25/$30, then $35; this is AUDIT F34, still unfixed. |
| 9 | EXPANSION.md:625 | US Hispanic "Full US prices… **$20**… $119". |
| 10 | ARCHETYPES.md:18 | "$20 US (full US price)" |
| 11 | ARCHETYPES.md:51 | "full US price ($20/mo) for US Hispanic members" |
| 12 | BLITZ.md:179 | Spanish-launch sensitivity row uses a "$20 price" for a US Spanish clone (F34). |
| 13 | ADS.md:9 | `{{PRICE}}` "default $20/mo" in the ad concept doc (ADS_SCRIPTS itself is clean). |
| 14 | ADS.md:334 | "10% of new payers take annual (**$119**)". Blitz annual is $249 from day 35. |
| 15 | CONTENT_SYSTEM.md:319 | DM path "$1 × 7-day trial → membership (**$20/mo** control…)". Line :332 labels it baseline, but row 319 reads as live. |
| 16 | prototype/strong-years-funnel.html:420, :428 | The DM mock shows the account "**strongyears.chang**". The canonical handle is `@changyin`. |
| 17 | prototype/strong-years-funnel.html:1039 | "Cancel online or by email, **never by phone**". The canon (BLITZ_OPS.md:501, F37) keeps a billing phone line. |
| 18 | app/src/lib/config.ts:131 | `annual: 11900` ($119). The canon says $249; the constant is unused. |
| 19 | app/tests/unit/webhook.test.ts:118 | Test title says "starts the **30-day** guarantee" (stale label; the canon is 14 days). |
| 20 | FUNNEL.md:13, :1671, :1778, :1809 | Terms-box and email copy promise add-ons "**watermarked with your email**". No watermarking exists in the app or `/api/downloads`, so the copy isn't true. |
| 21 | LAUNCH_CHECKLIST.md:15 | Row 1 says "Missing (14 session scripts only)". Sessions 1–30 and all six programs now exist; only the videos are missing. |
| 22 | LAUNCH_CHECKLIST.md:24 | Row 10 says "Partial (first-renewal reminder only)". The code sends reminders before every charge plus the yearly notice (M7, F10, F11). |
| 23 | LAUNCH_CHECKLIST.md:40 | Row 21 says refund-abuse controls are "Missing". Vesting and one-per-person are built; only the watermark is missing. |

The informational hits need no action. OFFER.md, ECONOMICS.md and FUNNEL.md mention $20 or $119 only in sections explicitly labelled "non-blitz / organic baseline (`OFFER_MODE=standard`)". BLITZ_OPS.md:1007 uses `#fallprevention` as a *search* tag for recruiting PT affiliates, not in our posts.

---

## 4. Prototype (`prototype/strong-years-funnel.html`)

At 390×844 (mobile, touch), an automated driver clicked through the whole path:
- DM: STRONG, send, email, "Easy", "Take the test".
- Quiz: all questions, the 30-second chair test, the balance stages, "Show my Strength Age".
- Result: "Join as a founding member: $25 today".
- Offer, then checkout ("Pay $25 and join + $9 Wall Plan").
- Upsell yes, then kit yes, then welcome.

After that it jumped to all 8 steps and took a desktop 1280 snapshot.
- **JS errors:** 0 page errors, 0 console errors or warnings, 0 failed requests.
- **Gray or low-contrast text:** 0 elements on all 34 snapshots. The check treated these as failures: WCAG ratio below 4.5, a near-neutral gray, or alpha or opacity below 0.9 (inherited opacity included).
- **Horizontal overflow:** none.
- **Copy against the canon:** prices are consistent. Founding is $25 (the $30 cell appears only in a code comment). The trial is "$1, then $25". The gift is $49/$119. The guarantee reads "14-day money-back guarantee", and the price is "locked while you stay". The strip carries the FALLBACK reviewer line, and the AI labels are present. Two contradictions remain: the handle (#16) and "never by phone" (#17).
- **Minor UX:** "Start Day 1 now" on the welcome step only shows a toast, by design, so the driver can't reach "Members home" by clicking. It was reached through the jump menu and renders cleanly.

---

## 5. Go-live readiness

**Verdict: NOT READY. Engineering must fix three things before any paid traffic; the rest is client-gated.**

**Blocking, and fixable by the team (no client input needed):**
1. **NEW-1, checkout takeover (critical).** Don't mint a session for a pre-existing email from checkout; send a magic link. Don't overwrite an existing member's Stripe customer or payment method. Add a regression test that re-runs checkout with an existing email.
2. **C2, crisis recall.** Make the LLM classifier mandatory in production (boot assertion) and fail closed. Widen the lexicon using the 11 misses in §2a, and keep a held-out corpus the lexicon was never tuned on.
3. **H10, scanner.** Fold diacritics for matching; handle em dashes and `*` censoring. Do the same in the n8n JS.
4. Clean up the 23 contradictions in §3. Priority: #1, #3, #20 (customer-facing promises), then the app README price lines.

**Ready (verified):**
- The app builds and passes lint, typecheck, 347 unit and 12 e2e tests.
- Checkout, consent, cohort counter, cancel flow, refunds, entitlement, webhook verification, rate limits and draft policy pages all work.
- Workers: 206 tests, fail-closed auth, SSRF and traversal protection, C2PA gating.
- The pipeline schema is locked against anon and authenticated roles, even under Supabase default grants.
- Content: 150 scripts, 40 ads and 390 hooks are compliance-clean. The products (30 sessions, 6 programs, kitchen, welcome kits) pass their safety audit.
- The prototype is clean.

**Blocked on the client:**
- **Keys and accounts:**
  - Stripe: live keys, the `STRIPE_WEBHOOK_SECRET`, a volume pre-approval or Braintree credentials.
  - Supabase: two projects, app and pipeline.
  - `ANTHROPIC_API_KEY`: required once item 2 is done.
  - Video: generation and render keys (fal, ElevenLabs, WaveSpeed) and a trusted C2PA certificate.
  - Twilio 10DLC / toll-free (3–6 weeks).
  - Meta: an ad account with a confirmed limit and a verified domain.
  - ManyChat, the ESP and sending domain (plus warm-up), R2, Vercel and the domain.
- **Attorney:**
  - ToS with exercise-risk clickwrap, privacy policy and WA MHMDA policy.
  - 50-state auto-renewal matrix.
  - Sign-off on using the warm list.
  - Review of the reviewer, performer and affiliate templates.
  - Budget $10–25K.
- **Reviewer:** a signed and verified PT/RD. Until then `REVIEWER_SIGNED=false` and the FALLBACK copy runs, which is correct.
- **Business setup:** entity, EIN and bank; Stripe Tax and nexus; insurance (GL, professional, media, cyber, product).
- **Decisions:** the $35 standard price, the founding close date, the $249 annual, 24/7 crisis coverage and the launch spend.
- **Cash:**
  - Meta: $3K/day through the day-10 gate, about $30K.
  - Member videos: about $6.3K.
  - Launch legal: $10–25K.
  - Insurance: $8–15K a year.
  - Peak cash need: about −$380K on R7 central.

---

## 6. Re-verification (round 2, Sep 30 2026, 13:48–14:03 UTC)

The fixers had seen round 1's probes, so every probe here is new. No repo file was edited, except for three effects of running the tools as instructed:
- **`build_content.py` rebuilt its outputs.** It overwrote a hand edit to `ADS_SCRIPTS.md` made at 13:47 (see R2-5).
- **`npm run build` refreshed `app/.next`.**
- **The demo servers ran on in-memory stores.** No repo data was touched.

### 6.1 Test results (round 2)

| Suite | Result |
|---|---|
| Lint / typecheck | **PASS** / **PASS** |
| Unit (vitest) | **PASS**, 384/384 in 20 files (new: NEW-1, C2 held-out, F08 watermark, F17 push) |
| Build | **PASS**, 64 routes, middleware 35.7 kB |
| e2e (Chromium `/opt/pw-browsers`) | **PASS**, 13/13 (new: the NEW-1 test) |
| Workers `make test` | **PASS**, 228 passed in 162 s, SQL tests included |
| `tools/build_content.py` | **PASS**, VALIDATION: PASS; 150 scripts, 40 ads, 390 hooks; 0 blocked-claim hits; 0 fall/percentage hits. **But it rewrote `ADS_SCRIPTS.md` (R2-5)** |
| Compliance CLI (scripts.json + ad_scripts.json) | **PASS**, 190/190 pass; selftest ALL OK |
| Prototype click-through, 390×844 | **PASS**: DM → quiz → result → offer → checkout → upsell → welcome, then jump to all 8 steps. 0 JS/console errors, 0 gray or low-contrast text, 0 overflow across 34 snapshots. The handle now reads `changyin`, and "never by phone" is gone |

### 6.2 Findings re-verified

| Item | Round 2 | Evidence (new probes) |
|---|---|---|
| **NEW-1 checkout takeover** (existing account) | **PASS** | Live `next start` demo: victim "Vera" bought and chatted `VICTIM-SECRET`. Each attacker variant then paid from a fresh browser: `UPPERCASE`, mixed case with surrounding spaces, fullwidth local part `ｖｉｃｔｏｒｉａ…`, zero-width inside, soft hyphen inside, the **$1 trial** with the victim's email, and **two simultaneous checkouts** with the victim's email. Every one went to `/checkout/check-email` with no session cookie; `/app/chat` → `/login`; victim chat was not visible. Signed in as their own trial account, the attacker then bought founding with the victim's email and still saw no victim data (the intent's `auth_member_id` ≠ victim). Distinct identities (plus-addressing, a Cyrillic homoglyph, a combining accent in the domain, a trailing-dot domain, Turkish İ) each correctly create a *separate* account; none exposes the victim. The victim's Stripe customer and card are no longer overwritten (`fulfill.ts:100-115`). Race on a brand-new email: the first fulfilment owns the account and the second goes to check-email; only one session. |
| **R2-1 pre-account hijack** (new) | **FAIL, high** | Reproduced live. The attacker pays **$1 trial** with an email that has **no account yet** (`future.…@example.com`) and receives a checkout session. Later the real owner logs in by magic link and chats. **The attacker's session stays valid and shows the owner's chat (`victimChatVisible=true`).** NEW-1 treats "this checkout created the account" as proof of ownership, and a magic-link login doesn't bump `session_version`. **Fix:** mark checkout-created accounts `email_verified=false`; on the first magic-link, claim or verification login, bump `session_version` so every earlier checkout session is revoked. Better still, keep chat and memory closed until the email is verified. |
| **R2-2 gift checkout broken** (new) | **FAIL, high** (functional) | Live: on `/gift`, both 3-month and 12-month purchases always return *"The price or terms changed while this page was open. Nothing was charged."* Root cause: `/gift/page.tsx` builds views with `toView(quoteCheckout(…))` and never signs them. `CheckoutForm` sends `quoteSig: ""`, and `startCheckout` rejects any sig that is defined but doesn't match (`checkout.ts:101`). The quotes themselves are identical (page vs server re-quote: 0 differing fields). No e2e test buys a gift. That blocks the $49/$119 offer and the six "Adult-child gift" ads. **Fix:** sign the gift quotes as `/join` does (or treat an empty sig as absent), and add a gift purchase to e2e. The gift takeover paths (gifter = victim, recipient = victim) couldn't be exercised end to end because of this bug. Code review shows the gift path returns no session when `buyer_is_owner` isn't true (`complete/route.ts:62`). |
| **C2 production guard** | **PASS, with a scope caveat** | `next start` with `VERCEL_ENV=production` and no `ANTHROPIC_API_KEY` → `POST /api/chat` **503** with the 988/911 text. The same build with `NODE_ENV=production` but **no `VERCEL_ENV`** (self-hosting, Docker, Vercel *preview*) → chat runs rule-only. It answered "what is the least painful way to go" with a normal coaching reply. `env.isProduction` requires `VERCEL_ENV === "production"`. **Fix:** key the guard on `NODE_ENV === "production"` (with an explicit dev override), not on the host. |
| **C2 LLM on every message** | **PASS** | Through the test seam, `classifyMessage` called the model 9 times for 9 messages (benign, ambiguous, definite and rule-missed). A model verdict catches all 4 rule misses I tried. |
| **C2 fail-closed on error or timeout** | **PARTIAL** | Model throws, returns null or returns junk: the ambiguous message becomes **crisis/fail_closed**, as intended. **But 0/4 rule-missed crises are flagged**, and they get a normal (stub) coaching reply. The real SDK path is the same. A hanging endpoint through `ANTHROPIC_BASE_URL` timed out after **8.6 s** (4 s × `maxRetries: 1`, not the documented 4 s), then ambiguous → crisis, and the rule-miss "what's the least painful way to go" → **none**. HTTP 500 behaves the same way. So during an API outage, recall drops to the rule layer. **Fix:** when the classifier verdict is unavailable, don't generate a coaching reply. Show the "chat paused, 988/911, talk to a human" message, which is true fail-closed. Also set `maxRetries: 0` or a 2 s timeout. |
| **C2 rule-only recall, 30 fresh messages** (for the record) | 18/30 (60%); 17/29 excluding one overlap with the fixtures | Missed: "tonight's the night, I've made up my mind"; "don't see myself around next spring"; "stand at the edge of the train platform…"; "what's the least painful way to go"; "stopped taking my insulin on purpose so it'll be over"; "no point waking up tomorrow, I'm finished"; "calf hot red swollen, now short of breath"; "blood sugar meter says 38 and I'm shaking"; "heart beating 180 and won't slow down"; "holds my pills until I give him my pension check"; "the aide… ties me to the chair"; "opened credit cards in my name". **Benign flagged: 8/30.** Five of those are *definite* keyword hits that even a model saying "none" **can't clear**: "My son took my car in for new tires" (abuse), "I don't want to wake up at 5 anymore…" (self-harm), "I blacked out the date on the calendar", "I'd rather die than eat Sun's kimchi again haha", "I can't breathe well in the wildfire smoke…". Each would send a crisis referral and page the on-call human. Recommend letting a confident model downgrade *definite* hits from these idiom-prone patterns to "support". |
| **H10 scanner, 15 fresh bypass strings** | **PARTIAL**: 9/15 blocked | Blocked: `cȕres` (double grave), fullwidth spaced `ｃ ｕ ｒ ｅ ｓ`, Cyrillic+math `Dе𝐭ох`, `d.e.t.o.x.i.f.y`, `detoxxx`, `m1r4cl3`, `fℓush toxins`, `c__u__r__e`, superscript `ᶜᵘʳᵉˢ`. **Pass through, while the plain form blocks or revises:** `c‧u‧r‧e‧s` (U+2027), `c⸱u⸱r⸱e⸱s` (U+2E31), `Boosts ur imm-une system` (hyphen inside the word), `clinicaIly proven` (capital I for l), `Lowers stress lnstantly` (l for I). Also passes: the paraphrase "Say goodbye to your pills forever"; its plain form passes too, so it's LLM-judge territory. The n8n JS pre-scan behaves the same (`‧` and `⸱` pass; the other 7 tested match). **Fix:** add U+2027, U+2E31 and the other middle-dot or punctuation separators to the separator class; collapse single hyphens inside a word before matching; add an l↔I↔1 confusable fold for the match-only variant. |
| **H10, 15 fresh benign strings** | **PASS**: 0/15 blocked | Café/azúcar, Señora Pérez, Naïve, Sauté, Crème fraîche, "Procure a sturdy chair", "Obscure fact", "Manicure day", "Detour", "curling club", "Accurate form", "qigong/baduanjin", "60–90 seconds", "2-3 lb", "U.S. adults… (E01)". |
| **F08 watermark** | **PASS** | `lib/watermark.ts` (pdf-lib) runs in `/api/downloads/[file]`; unit test `F08.watermark.test.ts` (4). Live: bought founding + Reset as "Renée" and downloaded both PDFs. Every page carries `Licensed to Renee <renee.…@example.com> \| Order SY-771E7576 \| 2026-09-30 \| Personal use only…`: 87/87 pages on the Reset and 16/16 on the welcome kit. I rendered page 3 at 110 dpi and the footer is visible in dark ink on a white band. The served bytes differ from the source file. Cosmetic: `pdfSafe` cuts the line at 120 characters, so it ends "Please don't s…"; with a long email, the order ref and date would be cut first. Put the order ref before the email, or raise the limit. |
| **F17 web push** | **PASS, 1 low** | Present: `public/sw.js` (same-origin URLs only), `manifest.webmanifest`, icons, `lib/push.ts` (web-push, VAPID from env, outbox "stubbed" without keys), `/api/push/subscribe|unsubscribe` (auth + entitlement + rate limit), `PushOptIn` on `/app` and `/app/settings`, `runDailyNudges` in the cron; unit test `F17.push.test.ts` (8). Live with generated VAPID keys: subscribe → 200 and cron → 200. **Low:** subscribe accepts any `https://` endpoint, **including `https://169.254.169.254/…` and `https://127.0.0.1:8443/…`**, and the server later POSTs to it (blind SSRF). **Fix:** allowlist push-service hosts (fcm.googleapis.com, updates.push.services.mozilla.com, *.push.apple.com, *.notify.windows.com). |
| Rate-limit IP source (new, low) | note | `clientIp()` trusts the first `X-Forwarded-For` value. Outside Vercel, a client can rotate it and bypass every per-IP limit (I used exactly that to run the probes). On Vercel, use `x-real-ip` or `x-vercel-forwarded-for`. |

### 6.3 Canon greps (round 2, 404 files)

Run over the whole repo (the raw scraped research data under `data/` excluded, as in round 1):

| Check | Hits |
|---|---|
| "30-day money-back" | **0** |
| "Doña Toña" | **0** |
| "Fall-Proof" | **0** |
| "Master" as Chang's title | **0** (34 hits, all video "master" or "never Master") |
| Condition hashtags in content | **0** (3 hits, all in rule, test or blocklist code) |
| Fall-outcome claims in customer copy | **0** (evidence notes and rule definitions only) |
| Ungated reviewer claims | **0** (all 63 inside gates, `reviewerGate()` or rules) |
| cure/detox/instantly in customer copy | **0** beyond myth-bust, negation or non-health uses |
| Keyword count | **12** everywhere |
| Handles | canonical everywhere, prototype included |
| Prices | founding $25/$30 ✓; standard $35 ✓; trial $1 → $25 ✓ (the 5 "$1 → $20" lines are all labelled standard-mode baseline); gift $49/$119 ✓; annual $249 from L35 ✓ (`config.ts` now 24900; the $119 lines are labelled standard-mode) |
| "text CANCEL" | every customer-facing instance gated by `{{IF_SMS}}` or `smsEnabled`. BLITZ_OPS.md:658 was fixed |
| "for life" | no pricing use left in the app (Pricing.tsx fixed); "keep for life" refers only to the owned program download |

**All 23 round-1 contradictions are resolved.** Checked line by line: BLITZ_OPS:658, FUNNEL:638, Pricing.tsx:67, BRIEF:45/51 (annotated "superseded"), app/README ×3, EXPANSION ×2, ARCHETYPES ×2, BLITZ:179, ADS:9/334, CONTENT_SYSTEM:319, prototype ×2, config.ts:131, webhook.test.ts:118, the FUNNEL watermark copy and LAUNCH_CHECKLIST ×3.

**Remaining canon items (3, low):**

| # | File:line | Item |
|---|---|---|
| R2-3 | FUNNEL.md:13; LAUNCH_CHECKLIST.md:40 | Both still call PDF watermarking "in progress, verify", but it's built and verified (§6.2). Update the status. The customer copy can promise it again, if counsel is fine with that. |
| R2-4 | EXPANSION.md:98, :131, :144 | The market ranking still prices "US Spanish" at the "$20 tier". The row is an index, and :69 now says US-Hispanic pays the US price in every mode, but the $20.00 figure in the ranking table reads as a price. |
| R2-5 | ADS_SCRIPTS.md (generated) | **A 13:47 hand edit to this file was reverted when `tools/build_content.py` regenerated it** (md5 changed; the new file equals the 09:28 build). The regenerated file passes the canon sweep and the compliance CLI (40/40 ads), so no canon hit survives. But whatever the fixer changed by hand is gone. **Port the change into `tools/build_content.py`**, which generates this file, and don't hand-edit generated files. |

### 6.4 Go-live readiness verdict (final)

**NOT READY for paid traffic: 4 engineering items remain. Everything else is ready or blocked on the client.**

Must fix, no client input needed:
1. **R2-1 pre-account hijack (high).** Revoke checkout-minted sessions on the first verified email login, or gate chat and memory until the email is verified.
2. **R2-2 gift checkout broken (high).** Sign the gift quotes and add a gift purchase to e2e. Then re-probe the gift takeover paths end to end.
3. **C2 residuals.** Key the production guard on `NODE_ENV`, not `VERCEL_ENV`. Make an unavailable classifier pause the reply (988/911 + human) rather than send a coaching stub. Allow model downgrade of idiom-prone definite hits.
4. **H10 residuals.** Separators U+2027 and U+2E31, hyphen inside a word, and the l/I confusable fold, in Python and in n8n.

Ship-with (low): push endpoint allowlist, XFF trust, watermark line length, the classifier timeout, R2-3/R2-4 doc status, and R2-5 (port the ADS_SCRIPTS edit into the generator).

**Ready (verified this round):** the original NEW-1 takeover is closed across 10 email variants, the trial path, the signed-in path and races. The 23 canon contradictions are resolved. Watermarking and web push are live. All suites are green (384 unit, 13 e2e, 228 workers, 190/190 compliance). The prototype is clean.

**Blocked on the client (unchanged from §5):**
- **Keys and accounts:** Stripe live keys and webhook secret; Supabase ×2; `ANTHROPIC_API_KEY` (mandatory); VAPID keys; generation and render keys plus a C2PA certificate; Twilio 10DLC; a Meta ad account; ManyChat, the ESP, the domain and its warm-up.
- **Attorney:** ToS, privacy, MHMDA, the ARL matrix, the warm list and the templates.
- **Reviewer:** a signed PT/RD.
- **Business setup:** entity, tax and insurance.
- **Decisions:** standard price, close date, annual price, 24/7 coverage, spend.
- **Cash:** about $30K of Meta through the day-10 gate, about $6.3K of video, $10–25K legal, $8–15K a year of insurance, and a peak need of about −$380K on R7 central.

---

## 7. Round 3 (Sep 30 2026, 14:25–15:00 UTC)

I read the new **CANON UPDATE** (BRIEF.md:61–67) first. Every probe below is new and appears in no earlier round or repo fixture. No repo file was edited. `build_content.py` was re-run and its outputs came out **byte-identical** (see 7.5).

### 7.1 Suites

| Suite | Result |
|---|---|
| Lint / typecheck | **PASS** / **PASS** |
| Unit | **PASS**, 434/434 in 23 files |
| Build | **PASS**, 65 routes |
| e2e | **PASS**, 14/14 |
| Workers `make test` | **PASS**, 264 passed (SQL included) |
| `build_content.py` | **PASS**, VALIDATION: PASS. 25 regexes, 0 hits. **Every generated file is byte-identical on re-run**, so the generator is now the source of truth for ADS_SCRIPTS.md and the rest |
| Compliance CLI | **PASS**, 190/190 deterministic (the CLI is a report; publishing runs through the judged n8n and worker path) |
| Products audit | **PASS**, 73 sessions structural OK, Unresolved 0 |
| Prototype, 390 px | **PASS**, full funnel, 0 errors, 0 gray text, 0 overflow |

### 7.2 Pre-account hijack and checkout sessions: **PASS**

I tested live on `next start`. The attacker pays the $1 trial (with a Reset bump) using an email **nobody has verified** and gets a **purchase-scoped** cookie (token 120 minutes). With that cookie:
- `/app`, `/app/chat`, `/app/account`, `/app/printables`, `/app/settings`, `/app/partner` and `/app/progress` all redirect to `/login`.
- `POST /api/chat`, `/api/chat/clear` and `/api/push/subscribe` return **401**, and so does `GET /api/downloads/…`.
- Only `/welcome` and the upsell ladder open.

Then the owner logs in by magic link and chats:
- The attacker's cookie, and the **same cookie replayed in a fresh browser**, reach nothing, including `/welcome`.
- A new checkout by the attacker with that email goes to `/checkout/check-email`.

Also checked:
- The owner's full cookie replayed after logout: dead.
- The owner's *own* pre-verification purchase cookie replayed after verifying: dead.
- The purchase cookie with its scope claim deleted: signature fails, so `/login`.

Upsell-scoped sessions don't reach account data. One UX note: an unverified buyer can't download the $7 PDF until they click the email link, so the welcome copy should say so.

### 7.3 Gift checkout: **PASS**

- **3 months and 12 months both complete end to end:** simulator, then `/gift/thanks`. The thanks page HTML has no claim link or code.
- **Non-recipient claims fail:**
  - `POST /api/gift/claim` with an empty token, a random 43-character token, or the recipient's email as the "token": 303 `/login?error=gift` and no session cookie.
  - Guessing redeem codes: 8 attempts get `error=code`, then `error=busy` (rate limit). The code space is 32⁸.
- **Legitimate claim:** the recipient's claim link was only reachable through the outbox, so this is covered by unit tests `R2-1` and `R2-2`. The gift-claim link also verifies the inbox and revokes earlier sessions.

### 7.4 Crisis safety

| Check | Result | Evidence |
|---|---|---|
| Guard covers `NODE_ENV=production` with no Vercel env | **PASS** | `next start` with no `VERCEL_ENV` and no key, and again with `VERCEL_ENV=preview`: a benign message gets the **offline** reply (988, 911, Eldercare 1-800-677-1116, human) plus a ticket. `chatRequiresModel` is false only for `NODE_ENV=development|test`, or for an in-memory demo with `ALLOW_RULES_ONLY_CHAT=true` that is not Vercel production. |
| Outage on unflagged messages | **PASS** | Model unavailable. Benign → offline (no coach reply). Rule-missed crisis "I have been saving my heart pills for when I am ready" → crisis referral with 988. Definite crisis → referral. Nothing gets a rules-only coaching answer. |
| Clear flow can't suppress resources before they're shown | **PASS** | The clear call needs the *reply* id, which only exists once the referral has been saved and returned. Random or unknown id → 404. Clearing the real reply → 200, and with the model offline the follow-up is again the offline text with 988. A second clear → 409 (single use). The same message sent again → crisis referral again. Lookup is scoped by `member_id` (no IDOR). The admin keeps the event and shows "Member said 'That's not what I meant'… Still follow up." Low: cleared rows are dropped from the 4-turn context window, so a follow-up that relies on the cleared message loses that context. |

### 7.5 Content judge: **PASS**, with 3 low items

I ran worker TestClient probes against `/compliance/scan` (with `judge:false` in the body) and `/package`, using a local fake Anthropic endpoint.

| Judge condition | Result on both endpoints |
|---|---|
| No `ANTHROPIC_API_KEY` | **human**; `/package` gives `pass2_ok=false` |
| Judge hangs (timeout) | **human** |
| Judge returns HTTP 500 | **human** |
| Judge returns non-JSON | **human** |
| pass at confidence 0.5 | **human** |
| Prompt-injection output (pass followed by block) | **human** |
| Genuine pass, confidence 0.95 | **pass** |

- **n8n:** the judge node runs `onError=continue`. Parse Verdict turns any error or bad JSON into `human`, and publishing requires `judge_ok` plus exact `verdict === 'pass'`. The Pass-2 gate requires `pass2_ok === true`.
- **Low 1:** a judge reply with **no `confidence`** is treated as 1.0 and passes, in both the worker (`judge_passed`) and n8n (`?? 1`). Default it to 0.
- **Low 2:** unknown verdict strings ("BLOCK", "Human", "fail", "reject") are passed through raw as `final.verdict`. They can't publish (n8n matches `'pass'` exactly and `pass2_ok` is false), but normalise them to `human`. `confidence: "high"` makes the endpoint return 422 instead of `human`.
- **Low 3:** `/qa/score` trusts a caller-supplied `judge_passed: true` and returns `auto_publish`. The caller is authenticated n8n, but the stored judge result should be the source of truth.

**Scanner, 10 fresh bypasses: 9/10 blocked.** Blocked:
- `c∙u∙r∙e∙s` (U+2219)
- `c u  r   e s` (irregular spacing)
- `rev3rses aging`
- `de-tox`
- `mira cle`
- `Ⅽures` (Roman numeral)
- `cvres`
- `dеtοx` (Cyrillic/Greek)
- strikethrough `c̶u̶r̶e̶s̶`

Extras, all blocked: ZWJ/ZWNJ, `cur-e`, `D E T O X`. **The one that passes is `c|_|res you` (`|_|` standing for u).**

### 7.6 Canon greps (413 files, generated files included)

- **Zero:** "30-day money-back", "Doña Toña", "Fall-Proof", Chang as "Master", condition hashtags, fall-outcome claims in customer copy, "you"-directed mortality claims, ungated reviewer claims.
- **"text CANCEL":** every customer-facing use is gated on SMS.
- **"for life":** none in pricing.
- **Keywords:** 12. **Handles:** canonical.
- **Prices:** founding $25/$30, standard $35, trial $1 → $25 (153 hits; the 5 "$20" lines are labelled standard-mode), gift $49/$119, annual $249 from day 35.
- **cure/detox/instantly:** only myth-bust or negation uses.
- **Generated files** (SCRIPTS, HOOKS, ADS_SCRIPTS, calendar, JSON/CSV) regenerate byte-identical and are canon-clean. **Remaining contradictions: 0.**

### 7.7 Deep checks (three areas not examined before)

| Area | Result | Evidence |
|---|---|---|
| **Admin brute force** | **FAIL (medium)** | The lockout works per IP: 10 wrong passwords, then 429, and the correct password is also refused while locked. But the key is the **first `X-Forwarded-For` value**. Rotating it gave **30 wrong guesses with no lockout, and the correct password still worked** (200). The counter lives in memory per instance, so serverless cold starts reset it. With no XFF, every client shares one bucket, so anyone can lock the admin out for everyone. Basic auth only: no 2FA and no password-strength check, on a page that shows crisis logs. **Fix:** key on the platform's client IP (`x-vercel-forwarded-for`/`x-real-ip`) plus a global failure counter in KV. Put `/admin` behind SSO (Vercel/Cloudflare Access) or add TOTP, and enforce a ≥20-character `ADMIN_PASSWORD`. |
| **Webhook replay** | **PASS** | Valid signed event → fulfilled. Exact replay → `duplicate`. A new event id for the same intent → "already fulfilled", no double effect. Two concurrent deliveries of one new id → one handled, one duplicate. A signature 15 minutes old → 400 (outside Stripe's tolerance). A refund for an unknown PaymentIntent → a no-op. Note: the `livemode` mismatch check runs only when `STRIPE_SECRET_KEY` is set. It was unset here, so a `livemode:true` event was accepted. Harmless in the demo, but set the key in every deploy. |
| **Founding cap race** | **FAIL (medium)** | Cap 7, with 5 seeded, leaves 2 spots. 8 buyers opened `/join` together and all saw the founding offer ($25/$30 cells); all 8 paid. Result: **13/7 founding members, 6 over the cap**. Afterwards the page correctly says "full, $35". The cap is checked only when checkout starts, and every intent already in flight is fulfilled as founding. At launch volume the overshoot equals the checkouts in progress at the moment the cap is hit, which contradicts the "honest, real cap" canon and the "first 5,000" copy. **Fix:** reserve a spot when a founding intent is created (a TTL hold, counted in `claimed + held`); stop founding quotes when that reaches the cap; if an intent was quoted founding, honour it but show "5,000 plus those already checking out" in the terms. Or close at cap minus the expected in-flight count. |

### 7.8 Go-live verdict (round 3)

**Code readiness: READY FOR A CONTROLLED LAUNCH after 2 medium fixes.** Everything critical and high from rounds 1–2 is closed and re-verified with new probes. Closed:
- the checkout takeover and pre-account hijack;
- gift checkout;
- crisis guard and outage behaviour;
- the mandatory content judge;
- watermark and push;
- canon, at 0 contradictions.

Fix before paid traffic (engineering, no client input):
1. **Founding cap overshoot:** reserve spots or disclose in-flight honouring (medium; honesty canon).
2. **Admin brute-force bypass:** trusted IP source plus SSO or TOTP (medium).

Fix soon (low): judge defaults (missing confidence → 0; normalise verdicts; `/qa/score` trust), `c|_|res`, push endpoint allowlist, XFF trust in `rateLimit.clientIp`, watermark line length, the unverified-buyer PDF note, and livemode enforcement without a key.

**Client-blocked (not code):**
- **Keys and accounts:** Stripe live keys and webhook secret; Supabase ×2; **`ANTHROPIC_API_KEY`** (chat and the content judge are offline or human-routed without it, by design); VAPID; generation, render and C2PA; a Meta ad account; ManyChat, the ESP, the domain and warm-up; Twilio 10DLC (SMS later).
- **Attorney:** ToS and exercise clickwrap, privacy, MHMDA, the auto-renewal matrix, the warm list, the templates.
- **Reviewer:** a signed PT/RD (the FALLBACK copy is live until then).
- **Business setup:** entity, tax and insurance.
- **Decisions:** close date, 24/7 crisis coverage, launch spend.
- **Cash:**
  - Meta: about $30K through the day-10 gate.
  - Member videos: about $6.3K.
  - Legal: $10–25K.
  - Insurance: $8–15K a year.
  - Peak need: about −$380K on R7 central.

---

## 8. Round 4 (final, Sep 30 2026, 15:10–15:50 UTC)

Every probe below is new. No repo file was edited. The generator re-run left every output **byte-identical**.

### 8.1 Suites

| Suite | Result |
|---|---|
| Lint / typecheck | **PASS** / **PASS** |
| Unit | **PASS**, 453/453 (new: R8 admin lockout, R8 cap race) |
| Build | **PASS**, 65 routes |
| e2e | **PASS**, 14/14 |
| Workers `make test` | **PASS**, 275 passed (SQL included) |
| `build_content.py` | **PASS**, VALIDATION: PASS, 0 blocked-claim and 0 fall hits; all generated files byte-identical on re-run |
| Compliance CLI / selftest | **PASS**, 190/190 / ALL OK |
| Products audit | **PASS**, Unresolved 0 |
| Prototype, 390 px | **PASS**, 0 errors, 0 gray text, 0 overflow, 0 placeholders |

### 8.2 Re-probes of the round-3 fixes

| Fix | Result | Evidence |
|---|---|---|
| **Founding-cap reservation, real Postgres 16** | **PASS** | Fresh DB, all 5 app migrations, Supabase-style grants. Concurrent `reserve_founding_spot` calls through parallel psql processes: **cap 2 × 50 → exactly 2 true**; cap 5 with 2 held × 60 → exactly 3 true; a full cohort × 20 → 0. **Late confirmations** after every hold expired, cap 4 × 30 → exactly 4 true. A mixed follow-up, cap 6 × 30 → exactly 2 true, and `founding_taken` = 6. anon and authenticated get "permission denied" on both functions. Live app (in-memory, cap 7 with 5 seeded, 8 simultaneous buyers): **exactly 2 got founding, 7/7**. The other 6 were stopped *before paying* with "The price or terms changed… Nothing was charged", and the page now shows $35. Low: that message is generic; "The founding cohort just filled" would be clearer. Low: founding holds (45 min) can be taken by unpaid checkouts, so a griefer with many IPs could hold spots; the per-IP checkout limit (20/h) bounds it. |
| **Admin lockout (trusted IP + username) + TOTP** | **PASS** (brute force closed), 1 residual | With TOTP: password only → 401; password + current code → 200; a 60-second-old code → 401; a wrong code → 401. Rotating `X-Forwarded-For` over 8 wrong guesses → locked after 5 (429), and the correct password + code is refused during the lock with `retry-after: 60`. On a Vercel simulation (`VERCEL=1`), 5 wrong from `x-real-ip` A lock the **username**, so the right password from another IP is also refused, and spoofed XFF doesn't help. **Residual (low-medium, by design):** anyone who knows the username can keep the real admin locked out (five bad guesses, doubling to 1 hour). The username defaults to `admin`. **Set a non-default `ADMIN_USER`**, or put `/admin` behind Vercel/Cloudflare Access. Minor: a TOTP code can be reused within its 30-second step. |
| **Scanner lookalike pass** | **PARTIAL**: 11/14 blocked | Now blocked: `c\|_\|res` (last round's miss), `c(u)res`, Greek `cμres`, final-sigma `ςures`, small-capital `mɪracle`, circled `ⓓⓔⓣⓞⓧ`, underline-combining, Cyrillic `сугеs`, `aginɡ`, en-space and split-word variants. **Pass through:** `¢ures`, `©ures`, `detøx` (ø). On 10 benign strings, **"Vitamin D, 20 μg a day" is blocked** (H10-HOMOGLYPH on μ). No content uses μg today (grep = 0); write "mcg". "The cure-all myth… MYTH." blocks (acceptable: MB-EX needs evidence). |

### 8.3 Canon greps (418 files, generated files included)

All zero or clean, as in round 3:
- "30-day money-back", "Doña Toña", "Fall-Proof", Master, condition hashtags, fall claims, "you"-directed mortality claims, ungated reviewer claims: 0.
- "text CANCEL" is always SMS-gated.
- Prices: founding $25/$30, standard $35, trial $1 → $25, gift $49/$119, annual $249 from day 35.
- 12 keywords; canonical handles.
- **Remaining contradictions in files: 0.**

### 8.4 Day-1 embarrassment sweep

I crawled 25 public pages and 15 member pages at 390 px (demo login), and rendered all 14 transactional email templates through real flows: founding with a bump, trial, gift, a pending-verification purchase, gift claim, magic link, pre-charge reminders, the CA annual notice, partner invite, cancel and refund.

| Check | Result |
|---|---|
| Broken internal links | **0 of 50** (every `href` returns 2xx or 3xx; `/kitchen` and `/reset` redirect to `/join` by design) |
| Page JS errors | **0** |
| Visible placeholders (`{{…}}`, TODO, lorem, `[PT NAME]`, undefined, NaN, null, Invalid Date) on pages | **0** |
| **Wrong price shown** | **FAIL (medium, not day 1)**. Once the founding cohort is full, `/checkout/trial` and `/join` correctly charge and disclose **$35**. But `/start` still says "$1 today for 7 days, then **$25.00** every month" in 3 places (Pricing card, hero microcopy, sticky bar), and `/terms` says "Then $25 every month". The source is `prices.monthly` (the `BLITZ_TRIAL_PRICE_CENTS` default) in `start/page.tsx:389,394` and `Pricing.tsx:13`, which ignores cohort state. Consent is recorded on the correct checkout terms, but the landing page advertises a lower price than the one charged, which is chargeback and FTC exposure. **Fix:** derive the trial renewal price from `resolveFoundingOffer` everywhere. This must be done before the cap can close. |
| Email template defects | **2 medium, 2 low.** **(M)** With `MAILING_ADDRESS` unset, every email footer prints **"[Company mailing address — set MAILING_ADDRESS]"** (`config.ts:111`). **(M)** With `NEXT_PUBLIC_SITE_URL` unset, every link in every email and every redirect is **http://localhost:3000** (`config.ts:26`). Neither has a production guard (only `SESSION_SECRET` does). **Fix:** fail the boot, or refuse to send, when real data is configured and either is missing or isn't https. **(L)** Pre-charge reminder subjects and bodies say "0 sessions done" / "So far you've done 0 sessions" to people who haven't started; drop the line when the count is 0. **(L)** A pending-verification purchase by someone else on an existing member's email creates a second membership row, so that member gets duplicate pre-charge reminders and annual notices for a charge they never confirmed; skip `pending_verification` memberships in reminders. Otherwise the emails are clean: correct amounts, dates in words, AI disclosure, the refund line, cancel instructions, secrets redacted, and nothing unrendered. |
| Deployment caveat (medium, config) | `clientIp` returns `"unknown"` unless `VERCEL=1` (set automatically on Vercel) or `TRUSTED_PROXY_HOPS`/`TRUSTED_PROXIES` is set. Off Vercel without those, **every visitor shares one rate-limit bucket**. Measured: the 13th checkout attempt in the hour, site-wide, got 429. Deploy on Vercel (the plan, per `vercel.json`) or set the trusted-proxy variables. Better still, fall back to per-email limits when the IP is unknown. |

---

## FINAL READINESS VERDICT

**Code-ready: YES, for a Vercel deployment.** No critical or high issue is open. Every critical and high finding from the two original audits and rounds 1–3 has been fixed and re-verified with new probes; canon contradictions are at 0; all suites are green.

**Conditions on "yes":**
- Set these production env vars before the first real visitor:
  - `NEXT_PUBLIC_SITE_URL` (https)
  - `MAILING_ADDRESS`
  - a non-default `ADMIN_USER`, `ADMIN_PASSWORD` and `ADMIN_TOTP_SECRET`
- Fix the trial-renewal price copy before the founding cohort can close.
- The two email polish items and the low items above can ship in week 1.

**Blocked on the client (the app runs demo or offline without them):**
1. **Keys and accounts:**
   - Stripe live keys, webhook secret and volume pre-approval; Braintree optional.
   - Supabase: two projects (app and pipeline); apply the 5 app migrations and `schema.sql`.
   - **`ANTHROPIC_API_KEY`**: without it, coach chat is offline (988/911/human) and every post routes to human review.
   - VAPID keys for web push.
   - Content generation and render keys (fal, ElevenLabs, WaveSpeed/HeyGen), R2, and a trusted C2PA certificate.
   - Meta: an ad account with purchase history and no restricted-health history (or a fresh Strong Years account), a verified domain and CAPI token.
   - ManyChat.
   - Email: an ESP (Resend or Postmark), the sending domain, DMARC and warm-up.
   - Twilio 10DLC/toll-free, for SMS later.
2. **Attorney:**
   - ToS with the exercise-risk clickwrap.
   - Privacy policy, WA MHMDA policy, Do Not Sell/Share.
   - 50-state auto-renewal matrix.
   - Sign-off on the warm list (Unignorable).
   - Reviewer, performer and affiliate templates.
   - Budget $10–25K.
3. **Credentialed reviewer:** a signed PT/RD. The FALLBACK copy runs until `REVIEWER_SIGNED=true`.
4. **Business setup:**
   - Entity, EIN, bank and registered agent.
   - Stripe Tax and nexus.
   - Insurance: general, professional, media, cyber and product liability ($8–15K a year).
   - The physical mailing address.
5. **Decisions:**
   - Founding close date.
   - Standard $35 and annual $249 confirmation.
   - 24/7 crisis coverage or honest hours.
   - Launch spend ($3K/day gated plan).
   - Which ad account to use.
6. **Content production:** rendering the 73 member session and program videos (about $6.3K), plus the organic launch masters.
7. **Cash:**
   - Meta: about $30K through the day-10 gate.
   - Videos: about $6.3K.
   - Legal: $10–25K.
   - Insurance: $8–15K a year.
   - Peak cash need: about −$380K on the R7 central plan.

---

## 9. Round 5: Shopify launch path (Oct 1 2026, 05:50–07:10 UTC)

Independent auditor, no prior sight of the build. Read BRIEF.md (CANON UPDATE 2 and 3 binding), INTEGRATION.md, LAUNCH_RUNBOOK.md and rounds 1–4 first; nothing from those rounds is repeated here, only re-verified where the Shopify path changed it. Every probe ran; nothing was spent, created, posted or sent; no external AI API was called; the K9SUPPS store was not touched (the deny list in `shopify/src/client.ts` still refuses it). Unlike rounds 1–4, **this round edited the repo**: the CRITICAL/HIGH findings below are fixed with regression tests, and the docs that described the broken behaviour as working are corrected.

### 9.1 Suites (after the fixes)

| Suite | Result |
|---|---|
| App typecheck / lint | **PASS** / **PASS** (0 problems) |
| App unit | **PASS**, 574/574 in 34 files (new: `tests/unit/R11.shopify-launch-path-audit.test.ts`, 6 tests) |
| App build | **PASS** |
| App e2e (Chromium `/opt/pw-browsers`) | **PASS**, 18/18 (14 Stripe-path + 4 Shopify launch-path) |
| shopify/ `npm run check` | **PASS**: typecheck clean, 128 tests, Theme Check 0 offenses |
| workers `python3 -m pytest` | **PASS**, 591 (569 + 3 governor + 19 canon-rule tests); media tests included |
| `tools/build_content.py` | **PASS**, VALIDATION: PASS; 25 regexes × 190 scripts + 40 ads = 0 hits; all generated files byte-identical on re-run |
| Compliance CLI | **PASS**, 230/230 (190 scripts + 40 ads) under the widened rule set; `selftest` ALL OK |
| Products audit (`audit.py`, read-only) | **PASS**, Unresolved 0 |
| App migrations on a scratch Postgres 16 with Supabase default grants (all 8, incl. the new one) | **PASS**: every public table has RLS; `anon` and `authenticated` get "permission denied" on `shopify_products`, `shopify_webhooks`, `shopify_inventory`, `shopify_early_refunds`, `shopify_seat_ledger`, `waitlist`, `plan_change_requests`, `sy_orders`, `refund_ledger`, `launch_state`; `authenticated` keeps only the column-scoped self-row grants on `members`/`memberships`/`practice_logs`/`retests`/`memory_items`; the only anon-executable app function is `founding_cohort_count()` (a public number) |

### 9.2 Findings

Severity key: CRITICAL = money or access wrong for many customers; HIGH = money/access wrong for a class of customers or a legal promise false; MEDIUM = exploitable with effort or a doc/claim contradiction a customer could rely on; LOW = polish.

| # | Sev | Where | Finding | Repro | Status |
|---|---|---|---|---|---|
| **R5-1** | **CRITICAL → fixed** | `app/src/lib/billing/shopifyWebhook.ts` (orderPaid renewal branch, `inventoryUpdate`), `app/src/lib/billing/shopify.ts` (`ShopifyAdmin`), `shopify/src/seatLedger.ts` (unused), `LAUNCH_RUNBOOK.md:67,108`, `INTEGRATION.md §2` | **Founding renewals consumed cap seats and, at stock 0, every founding renewal would have failed.** The founding variant is tracked, policy DENY, quantity 5,000. Shopify docs: "the availability of inventory is checked during the billing attempt process… If one or more of a subscription's product variants are out of stock (and aren't configured to continue selling), then the billing attempt moves to a failed state with… an insufficient inventory… error" (shopify.dev → Build a subscription contract → Inventory tracking). Renewal orders are ordinary orders and decrement the variant. `seatLedger.ts` encodes the right rules but **nothing executed them**: the app's renewal path never adjusted inventory, the self-serve refund restocks `NO_RESTOCK`, the admin token was documented with `read_inventory` only, and no code ever set `inventoryPolicy CONTINUE`. Effects: (a) the "5,000 founding seats" counter double-counts (one member + one renewal = two seats), so the cohort would close at ~2,500 real members; (b) once available hit 0, Shopify Subscriptions' billing attempts for *existing* founding members fail with insufficient inventory, dunning retries 3× then **cancels paying members' contracts** (runbook step 10 setting); (c) the policy's "If someone takes a refund, their seat goes back" was false. The runbook's test (d) asserted "the seat ledger gives the seat back" for code that did not exist. | Unit (before the fix): a renewal `orders/paid` with `source_name subscription_contract` made 0 inventory calls; `inventory_levels/update` with `available: 0` made no policy change. Confirmed by reading: no `inventoryAdjust`/`write_inventory` anywhere in `app/`. | **Fixed.** `ShopifyAdmin` gains `adjustInventory` (`inventoryAdjustQuantities`, reason `correction`, `referenceDocumentUri strongyears://seat-ledger/<renewal|refund>/<id>`) and `allowOverselling` (`productVariantsBulkUpdate inventoryPolicy CONTINUE`). `orders/paid` renewal of a founding line → +1 (idempotent via the new `shopify_seat_ledger` table, keyed by reference URI; a redelivered webhook never adjusts twice). `refunds/create` of the seat-consuming first founding charge with `restock_type no_restock` → +1 (a Shopify-restocked refund is not credited twice). `inventory_levels/update` with `available ≤ 0` on the founding item → CONTINUE + an on-call ticket to run `close-founding`; if the policy call fails the ticket says to flip it by hand *now*. Location comes from the inventory mirror, else new env `SHOPIFY_LOCATION_ID`, else a ticket (no silent loss; the ledger row is released for retry). Admin token scopes now `+ write_inventory, write_products` (same Dev Dashboard app; `shopify/RUNBOOK.md` already requests them). Tests: R11 #4, #5, #6. Runbook §3 table, §4 table, §6 (d)/(d2) updated. |
| **R5-2** | **HIGH → fixed** | `app/src/lib/entitlement.ts:grantsAccess` (`active` → `true`), no lapse job in `clock.ts`, `INTEGRATION.md §2` ("access runs to the period end (+ grace…) and lapses") | **A Shopify membership never lapsed.** On the launch path no `subscription_contracts/*` or billing-attempt webhook ever reaches the app (Shopify Subscriptions owns the contracts), so a member who cancels or pauses on Shopify's account page, or whose card dunns out, keeps a row with `status: active`, and `grantsAccess` returned `true` for any non-gift `active` row regardless of `current_period_end`. Members area, daily sessions, chat, downloads and web-push stayed open indefinitely for anyone who had paid once. The round-3 test that claimed to cover this asserted access on a date *inside* the paid period. | Unit (before): founding order paid Oct 1, period end Nov 1, no renewal; `grantsAccess` on Nov 9 → `true`. | **Fixed.** `grantsAccess`: an `active` Shopify row grants access only while `current_period_end` + float (`grace_until` if set, else `SHOPIFY_GRACE_DAYS`, default 7, so a late renewal webhook never locks a paying member out) is in the future. New `runShopifyLapses` in `clock.ts`, run by `/api/cron/reminders` hourly: rows past period end + float with no renewal order → `expired` (conditional update, idempotent) + "Your Strong Years membership has ended" email (conditional wording: cancelled → nothing to do; failed card → update it and the next payment reopens everything). `renewalMembership` and the renewal branch now **revive an `expired` row** when a late renewal order arrives (the money came), extending from the payment date, no second membership. Tests: R11 #1, #2. Runbook §3/§4 and test (d3) updated. |
| **R5-3** | **MEDIUM → fixed** | `shopifyWebhook.ts:refunded` / `orderPaid` | **`refunds/create` before `orders/paid` left access open.** Shopify retries a failed `orders/paid` delivery for up to 48 h; a quick refund in that window (admin refund, or the buyer's self-serve refund via a different path) was answered "nothing new to refund" and forgotten, and the retried `orders/paid` then provisioned full access for a refunded order, never revoked. | Unit (before): refund for line 41 → `ignored`; then `orders/paid` with line 41 → membership `active`, `grantsAccess` true. | **Fixed.** An unknown refund line is parked in the new `shopify_early_refunds` table (unique on line + refund id); `orders/paid` records such a line as already refunded, ends the membership it would have started, and tickets a person to cancel the contract. Test: R11 #3. Migration `20261001150000_round5_shopify_launch_audit.sql` (RLS, service_role only; verified on Postgres 16). |
| **R5-4** | **MEDIUM → fixed** | `workers/growth/config.py:load`, `growth/api.py` (every endpoint accepts `config_overrides`), `governor.py:execute` | **Every governor cap could be lifted per request.** `POST /growth/governor/plan` with `config_overrides: {governor: {max_boost_daily_usd: 1e6, max_cold_daily_usd: 5e6, pre_gate_cold_daily_usd: 1e6, max_abs_usd: 1e9}}` returned an audited plan of **$1.52M/day** (boost $900K, cold $120K, retarget $500K) and `pre_gate_cold_daily_usd: 3000` opened cold spend with the §11 gate failed. `validate()` only checks caps are ≥ 0. The executor still refuses (no ad client, `SPEND_ENABLED` env-only), so no money could move today, but the "hard caps enforced by the spend governor" (BRIEF CANON UPDATE 2) were only as hard as the n8n JSON or whoever holds the worker token. | TestClient, token auth: planned 1,520,000.0, mode dry_run, status SCALE. | **Fixed.** `config.load()` refuses any `config_overrides.governor` key (`ProtectedOverride` → HTTP 422); caps and gate lines come only from DEFAULTS or the operator's `GROWTH_CONFIG_PATH` file. `execute()` additionally refuses a decision whose `config_fingerprint` differs from the operator's config. Tests: `tests/test_round5_governor_overrides.py` (3); two older tests that encoded the per-request override were updated. Re-verified: boost without judge → $0; class PROMISING → $0; no/future approval → $0; execute → refused (`SPEND_ENABLED`); unauthenticated → 401; negative/NaN/`1e308` money → STOP, $0. **No ad API client exists** (grep for facebook_business, `/act_`, adsets, TikTok business API: 0 hits outside a config comment). |
| **R5-5** | **MEDIUM → fixed** | `workers/compliance/rules.py` | **Four canon hard lines had no deterministic rule in the publish scanner** (the LLM judge was the only layer): "locked for life" (and `for life`, double-space), "$1" / "7-day trial" / "free trial" (CANON UPDATE 2: "No $1 trial. Ever."), named-and-aged quote testimonials (`"…" — Linda, 68, member since March`), and scarcity phrased with a modifier (`Only 37 founding spots left`, `closes at midnight`, `normally $99`). 20 fresh bypass strings (none in any fixture): **16/25 blocked before, 21/25 after**. Still passing, by design LLM-judge territory: fall-outcome paraphrases without the word "fall" ("you will never hit the floor again", "no more tumbles"), "you'll still be here at 95", and lowercase "the master, Chang Yin". | `python3 -m compliance text "Price locked for life."` → pass (before). | **Fixed.** New rules `CANON-FORLIFE`, `CANON-TRIAL`, `T-01b`, widened `T-04` (modifier between number and noun; "closes at midnight"; "normally $N"; "hurry" only in purchase phrasing so A31 "Eat like you're not in a hurry" still passes). 12 benign controls pass (clinical "trial", "$1.50 a dozen", "a skill for life", "3 ingredients", "Chang says, 74"). Corpus: 230/230 still pass. Tests appended to `tests/test_round5_canon.py` (19). |
| R5-6 | MEDIUM (doc) → fixed | `FUNNEL.md` §0–§3, §5 (138 "$1" lines, 36 "7 days for $1" buttons, the §0.2 offer table rows "Primary (3 live cells from L1)… or $1 for 7 days", "$1 7-day trial — Live from L1 as cell T25") | FUNNEL.md still presents the $1 trial and the F25/F30/T25 cells as the live launch in its offer tables and page specs; only §4.1's link rule and §4.19 carry the canon. Anyone building `/start` from §2 would build the trial. | grep | **Fixed** with a canon banner at the top of FUNNEL.md naming the superseded sections. The historical lines remain (the file is the funnel archive); rewriting 2,000 lines was out of scope. |
| R5-7 | MEDIUM | `shopify/src/legal.ts:cancelMethods`, membership policy §4, ToS §4, FAQ | The published policy promises cancellation "by replying 'cancel' to any email from us" with "stops all future charges immediately… confirmation email right away". On the launch path a cancel is a human action in Apps → Subscriptions; there is no inbox→ticket automation and no SLA stated. ROSCA/CA ARL: a promised cancel channel must work; an email that sits over a renewal date is a charge after cancellation. | Reading; no inbound-mail handler in `app/` (grep `inbound`, `reply`, `cancel_by_email` → only the ticket reason enum). | **Fixed (integration follow-up).** Every "reply cancel" promise removed from `shopify/src/legal.ts`, the theme terms/cart/account copy, the app (pricing, reminders, fulfilment, checkout) and the product kits; email is described as "a person reads it within one business day; for a same-day cancel use your account". Regression: `app/tests/unit/R5.open-findings.test.ts` greps every file; `audit.business.test.ts` F09 updated. |
| R5-8 | MEDIUM | `shopify/theme/sections/main-product-membership.liquid`, `strong-years.js` | Consent record vs charge for a **returning** customer: the starter page always records `sy_consent_price` = $12 and a terms hash that says "$12 today", but Shopify drops STARTER12 at checkout for a customer who already used it (`appliesOncePerCustomer`), charging $25. The checkout page shows $25 before payment (so the buyer sees the real price), but the stored consent record for that order says $12. | Reading (cannot complete a checkout here). | **Fixed (integration follow-up).** (1) The starter page now states the $25 path explicitly ("One starter offer per person… checkout shows $25 today instead") and records `sy_consent_price = "12.00|25.00"` (code price | plan price, consent v2), so the record is what was shown. (2) `orders/paid` compares the charged membership line with the recorded prices (`consentMatchesCharge`): match → nothing; mismatch → on-call ticket before the first renewal; no record (no-JS) → review ticket. (3) `/join` and `/b` send a signed-in member who already used a starter code to the plain membership page. Tests in `R5.open-findings.test.ts`. |
| R5-9 | MEDIUM | No `disputes/create` webhook; `shopifyWebhook.ts` | A lost chargeback on the membership charge creates no refund object, so access stays open and the member can also request the 14-day self-serve refund (`refundCreate`; Shopify should refuse while a dispute is open or the refundable amount is 0, but that is Shopify's check, not ours). Policy §2 says charged-back seats are released; nothing reads disputes. | Reading. | **Fixed (integration follow-up).** `disputes/create` + `disputes/update` added to `shopify/config/webhook-topics.json` core (provisioning snapshot updated) and handled in `shopifyWebhook.ts`: a chargeback marks the lines `disputed`, ends the membership, writes a `refund_ledger` row (which blocks the self-serve refund → review) and tickets on-call with the evidence due date; `won` restores lines, membership and the ledger; inquiries only ticket; replays ignored. Contract tests on both sides. |
| R5-10 | LOW | theme no-JS path (`main-product-membership.liquid` form) | Without JS the form posts `/cart/add` with `return_to=/checkout`: the required checkbox gates the submit, but `sy_consent_*` attributes are never written and STARTER12 is on the checkout only if the visitor arrived through the `/discount/` share link. | Reading. | **Fixed.** Hidden `attributes[sy_consent_v]=nojs`, `sy_sku`, `sy_entry` fields ride the no-JS post; the app treats a missing consent price as "unknown" and opens a review ticket (`R5.open-findings.test.ts`). |
| R5-11 | LOW | `shopify/config/catalog.ts` founding variant | A buyer can raise the founding line's quantity on the cart page: qty 2 + STARTER12 = $37 for two seats on one contract; the app records one membership. | Reading. | **Fixed.** The offer form posts `quantity=1`, the JS forces every subscription line to 1 before checkout, and `orders/paid` tickets any membership line with quantity > 1 (one membership is recorded). |
| R5-12 | LOW | `app/src/app/api/gift/redeem/route.ts` | A JSON body (wrong content type) throws → 500 with a stack line in the server log; no leak. | `curl -X POST -H 'content-type: application/json' -d '{}' /api/gift/redeem` → 500. | **Fixed.** `formData()` failure → 303 `?error=code` (test in `R5.open-findings.test.ts`). |
| R5-13 | LOW (doc) | `economics.xlsx` Organic_First row "Share of ebook orders that collect a shipping address = 1 … assumes the ebook product is set to require a shipping address" vs `catalog.ts` ebooks `requiresShipping: false` | Only the cell-A post-purchase sensitivity rows depend on it (modelled 0 at launch). | Reading. | **Fixed.** `elig_addr` central = 0 (the catalog default); the cell-A one-click sensitivity rows set it to 1 explicitly and say the variant would have to require shipping; sheet and csv refreshed (`tools/organic_sheet_refresh.py`); R20/R22/R23 headlines unchanged. |
| R5-14 | LOW | `schema.sql:create_variants_and_posts` | Inserts `scheduled` posts without checking the video's judge status; the gate is enforced upstream in n8n (judge_ok + verdict === 'pass', round 3) and `get_publish_token` is service_role-only, but the DB itself would accept an unjudged scheduled post from a buggy workflow edit. | Reading. | **Fixed.** `create_variants_and_posts` raises unless the video is `approved`/`packaged` when any post is `scheduled` (`schema.sql`). |

### 9.3 What was attacked and held (new probes, all on the Shopify path)

- **Webhook route:** forged / missing / wrong-secret HMAC → 401; no secret → 503; wrong shop → 401; 1 MB+ → 413; the same signed body under a new webhook id → no double provisioning (unique on `shopify_line_id`); renewal replay → one extension; refund replay → "nothing new"; `orders/cancelled` on a provisioned order ends it; a `customers/update` email change ends every session and re-requires inbox proof; an email collision is ticketed, not merged.
- **STARTER12 misuse:** scoped to the founding product only (`productsToAdd`), subscription purchases only, `recurringCycleLimit 1`, `appliesOncePerCustomer`, `combinesWith` product/order discounts off; cannot apply to the annual, gift, bumps, books or the standard product; STARTER12S is scoped to the standard product, which is DRAFT until `close-founding`; page codes (CHANG/SUNYOON/CHANGANDSUN) are one-time-only and scoped to the ebook cells, so MRR is never discounted. A second email can use STARTER12 again, which is a new customer getting the same public offer (and a separate 14-day guarantee, matched by email only on Shopify: the card-fingerprint half of "once per person" is Stripe-only; **LOW, note for counsel**). The `/discount/<CODE>?redirect=` share link is documented by Shopify Help ("Change the URL extension from /discount/code to /discount/code?redirect=/new-path… the discount is automatically applied… when the customer adds products… that meet the discount's requirements"); `recurringCycleLimit` is in `DiscountCodeBasicInput` as cited in INTEGRATION.md; cart permalinks with selling plans remain unsupported, and the app never emits one.
- **Prelaunch bypass (live `next start`, `LAUNCH_MODE=prelaunch`, Shopify mode):** `/join`, `/join?offer=gift3`, `/gift`, `/checkout/trial`, `/b?t=BOOK|JOIN|FAMILY`, `/kitchen` → waitlist; `POST /api/checkout`, `/api/checkout/mock-complete` → 403; `/api/upsell` → 303 to the waitlist; `/api/checkout/complete` → 405. The Shopify store itself is the only other door and is password-protected until D0 (runbook); an order paid in prelaunch is provisioned (money was taken) and ticketed.
- **Attribution injection (live, `LAUNCH_MODE=live`):** `pid=<script>…`, `utm_source="><img src=x>`, a 5,000-character `utm_campaign`, `mc_id=../../etc`, `ref=STARTER12` → every bad value dropped by the sanitiser; the redirect carries only `page=changyin&keyword=BOOK&vid=<uuid>&sku=bundle_m12`, URL-encoded inside `/discount/STARTER12?redirect=…`. `?cell=e7&sku=ebook_e7&price=1` and a forged `sy_cell` cookie → ignored; the cell comes from the signed visitor id (sticky across 3 requests; 20 fresh visitors split A/B). Keywords map to a product family, never a price. Cart attributes are re-validated on the way back in (`cartContextFromAttributes`: `sy_` prefix, ≤ 100 chars, `sy_vid` must be a UUID) and affect analytics only; the amount comes from the order line.
- **Server-side events:** `recordConversion` from the webhook sends `Purchase` / `Subscribe` with `content_name` starter_books|founding|membership, `event_source_url` /checkout, a SHA-256 email hash only, and only when the ad-measurement consent check passes (`conversions/consent.ts`: opt-out attribute, Do-Not-Sell log, GPC); `meta.ts` refuses condition words and quiz URLs.
- **RLS:** see §9.1.
- **Growth n8n workflow:** valid JSON, 44 nodes, 0 dangling connections, no publish or ad node (it writes `boost_queue` rows and posts a Slack approval request). Core workflow: 109 nodes, 0 dangling; publishing still runs through `get_publish_token` (service_role only).
- **Numbers (CFO pass):** `tools/organic_engine.py` re-run reproduces every BLITZ.md §13 headline: R20 $2.1K / $4.6K / $9.0K (d4/d14/d30), retained $4.6K; R22 $0.5K d30; R23 $6.7K / $26.3K / $58.9K, milestones days 6 / 26 / 59, trough −$185K; solver 4.7K / 22.2K / 49.5K names (runway 14). `economics.xlsx` `Organic_First` inputs match the engine (ebook cvr 5/3/8%, subB 0.70, renB1 50%, refunds 12%, bumps $4.44, Shopify Payments 2.9% + 30¢, Subscriptions app free, 5-day payout lag, 10%/90-day reserve). The cell-B MRR convention (count at $25 from day 1, "retained" × 50% first-renewal survival) is stated in the sheet, the engine and §13; the honest number is retained MRR, which is roughly half of every cell-B "$100K" entry (BLITZ §13.4 says so). No doc or checklist number contradicts the model; only R5-13 (shipping-address input) contradicts the catalog.

### 9.4 Runbook walk (as the client)

Every step is doable as written except: (1) the admin token scope line (fixed, now includes `write_inventory`, `write_products`); (2) the new `SHOPIFY_LOCATION_ID` (added to the table and `.env.example`; the dry run prints it as `r.ids.location`); (3) test (d) asserted a seat return that did not exist (fixed, with (d2) stock-0 and (d3) lapse checks added). Ordering is sound: the members app deploys (D−21 → D−10) before the store provisions webhooks to it (D−14 → D−10); Supabase migrations are listed in name order and the new file sorts last. Nothing in setup charges a real customer: provisioning is `DRY_RUN=true` by default, the store stays password-protected and in test mode until D0, and the money QA uses the 4242 test card. One ordering note: step 10 says to create the two plans in Apps → Subscriptions *before* `npm run verify`; the plan names must contain exactly "Monthly, renews until you cancel" / "Yearly, renews until you cancel" and must not contain "first month" (the verify phase keys on those strings).

### 9.5 Go / no-go

**Verdict: GO for a controlled launch (password off, organic traffic, no paid spend), conditional on:**
1. The R5-1/R5-2/R5-3 fixes are deployed with the new migration, `SHOPIFY_LOCATION_ID` set, and the Admin token re-issued with `write_inventory` + `write_products`; runbook tests (b), (d), (d2), (d3), (f) pass on the dev store, in particular **"Bill now" charges $25 and the founding stock goes back up by 1**.
2. ~~R5-7~~ done ("reply cancel" dropped everywhere; counsel still reviews the policies as a whole).
3. ~~R5-8 and R5-9~~ done (consent-price record and mismatch flag; `disputes/create|update` with revoke/restore). Suites after the follow-up: app unit 583/583 (35 files), e2e 18/18, shopify 128 + Theme Check 0, workers 591, content PASS, products 0 unresolved.
4. Everything rounds 1–4 already listed as client-blocked (keys, counsel, reviewer, entity, insurance, decisions, cash) is unchanged.

**NO-GO for paid spend** until the §11 gate passes (unchanged), and note that the governor's caps are now file-only: changing a cap means editing `GROWTH_CONFIG_PATH`, not an n8n node.
