# SYSTEM_RECAP.md: everything built so far, by layer, with status and capacity

As of Oct 2 2026, repo commit `d7da474` plus ENGINE_NEXT50.md. Sources: the top-level docs, `app/README.md`, `workers/README.md`, `shopify/RUNBOOK.md`, `LAUNCH_RUNBOOK.md`, `deploy/README.md`, `production/` and a scan of the code and data files. Test counts come from `pytest --collect-only` (workers, tools, production) and from the suite READMEs (app, shopify). **I did not run the tests in this round.**

**Status key**
- **Built**: the code or content exists.
- **Tested**: an automated suite covers it.
- **Dry-run**: it runs end to end against mocks or fixtures, and nothing leaves the machine.
- **Needs key**: it needs a credential, account, contract or person before it can go live.
- **Spec**: the design exists in a document only, with no code yet.

Nothing in the repo has posted, spent or touched a live account. The K9SUPPS store is on a hard deny list.

---

## 1. Capacity table

| Measure | Value | Basis |
|---|---|---|
| Masters/day | **24** (4 IG pages × 6). STACK_FINAL budgets **25** | BRIEF CANON UPDATE 4; STACK_FINAL §0 |
| Platform variant files/day | **≈120** (24 masters × 5 files: IG, FB, TikTok, a distinct YouTube cut, and X; Threads posts the clean master or text) | `workers/assemble/variants.py` `render_variants` |
| Trial Reels/day/page | **Built today:** every IG reel in a page's first 14 days is a Trial Reel (≈6 per page per day). **Proposed:** a probe from 3 up to 10–20 per page per day (ENGINE_NEXT50 IG-1). The real cap is unpublished and may be as low as 5 [N1] | `tools/posting_rules.py` `ig_trial_reel` |
| Placements/day (pages × platforms) | **144** at canon 4 (4 pages × 6 platforms × 6/day). The 90-day plan file (7 handles) peaks at **270/day** from D+37 | CANON 4; `data/content/posting_plan_90d.csv` |
| API ceilings that bind | IG 100 publishes/24 h per account (Trial Reels included); FB ~25 posts/24 h per Page; TikTok ~15/day; Threads 250/24 h; IG DMs 750 private replies/h | ENGINE_100X §10.7, §8.9 |
| Scripts in library | **190** organic (S01–S190; 187 pass the virality gate, 3 are REWRITE) + **101** wave-2 drafts (100 pass) + **40** paid-ad scripts (A01–A40) + **40** runway set (S151–S190, inside the 190). **430** hooks | `data/content/scripts.json`, `scripts_wave2.py`, `ad_scripts.json`, `hooks.json` |
| Days of script coverage at 24/day | **7.8 days** (187 schedulable) → **12.0 days** with wave 2. In the 90-day plan, **12,072 of 13,800 rows (87%) are `GEN-needed`** | `posting_plan_90d.csv` `script_id` |
| Render cost/day, Tier B | **≈ $31/day** (24 × $1.28), **≈ $960/month** at 25/day. Optional switches: +$180/month (Pro hooks), +$60/month (Motion Control v3). Fixed costs ≈ **$480/month (≈ $16/day)**. Proposed trials at 15 per page per day ≈ **+$27/day** | STACK_FINAL §5; ENGINE_NEXT50 MOD-2 |
| Exception lane | $100/month (walk-and-talk, two-shot tests) | STACK_FINAL §3 |
| Pages | **4** IG pages + 4 FB Pages at canon 4. The plan file defines **7** handles: @changyin, @sunyoon.kitchen, @changandsun (D−7); @changyin.strength, @changyin.mobility (D+15); @sunyoon (D+22); @changyin.espanol (D+30) | CANON 4; POSTING_PLAN §1 |
| Platforms | **6**: IG Reels, FB Reels, TikTok, YouTube Shorts, Threads, X | POSTING_PLAN |
| Languages planned | **2**: English, and Spanish (@changyin.espanol pilot, 3/day, plus `prompts/08_localization_adapter.md`). Proposed: Meta AI translation and YouTube auto-dub before any Spanish renders | POSTING_PLAN; ENGINE_NEXT50 FB-3, TT-11 |
| DM keyword flows | **14** (BACK, BALANCE, BEGIN, BOOK, BREATH, FAMILY, GUT, JOIN, KNEES, SLEEP, SOUP, STRONG, TEST, WAITLIST) + `_global` | `workers/dm/flows/` |
| Email sequences | **12** lifecycle sequences with 29 steps: failed_payment, pre_renewal, gift_recipient, member_onboarding, books_to_membership, activation, activation_lapsed, annual_offer, gift_unclaimed, waitlist_nurture, win_back, daily_coach. Also: a 3-email Starter Books onboarding; the launch cron (≤3 emails + 2 pushes in 72 h); 2 warm-list sequences; and 14 coach tips | `app/content/lifecycle/sequences.json`, `shopify/emails/`, `data/warm_lists/sequences.json` |
| Shopify SKUs | **13 products** in 4 collections: Starter Books ×3 cells ($7/$12/$15), Founding $25/mo, Standard $35/mo, Essentials $12/mo, Founding Annual $249/yr, Gift ($49/$119), Wall Plan $9, Kit $29, Coached 12-week ×3 ($97/$147/$197). Discount codes STARTER12 and STARTER12S | `shopify/config/catalog.ts` |
| Product content | 30 daily sessions (4 tracks), 6 programs, 50 recipes, 19 PDFs (Reset, Kitchen, welcome kits per price, 12-week printable, programs) | `products/` |
| Production assets planned | 54 locked reference images (Chang 24, Sun 24, duo 6), the first 150 render jobs, 60 B-roll prompts, a 205-row performer call sheet, voice design and a pronunciation lexicon | `production/` |
| n8n | Core workflow **109 nodes**; growth workflow **44 nodes** | `n8n_core_workflow.json`, `n8n_growth_workflow.json` |

### Tests per suite

| Suite | Count | Command | Status |
|---|---|---|---|
| `workers/` (pytest) | **627** collected across 25 files: textnorm 59, compliance 61, audit 62, governor 71, adapters 47, round-5 canon 43, growth schema SQL 29, actions 29, QA 27, judge-mandatory 22, scoring 22, snapshots 21, schema SQL 17, allocator 16, growth API 16, assemble 15, virality gate 13, DM bot 11, growth workflow 10, uniqueness 9, packaging 8, workflow 7, ops round 5, production pack 4, governor overrides 3 | `make test` (~4–5 min), `make test-fast`, `make test-sql` | Tested |
| `app/` unit (Vitest) | **583** (README figure; 412 `it`/`test` declarations, some parameterised) | `npm test` | Tested |
| `app/` e2e (Playwright) | **18** (14 legacy Stripe-path + 4 Shopify launch-path) + screenshot contrast checks on 26 shots | `npm run test:e2e`, `npm run screenshots` | Tested |
| `app/` smoke | **17** read-only checks against a deployed URL | `npm run smoke -- <url>` | Built (needs a deploy) |
| `shopify/` (Vitest) | **128** + Shopify Theme Check at 0 offenses | `npm run check` | Tested |
| `tools/` | **16** (posting rules, plan validator) | `pytest tools/` | Tested |
| `production/launch_day` | **15** (render_day1 dry run) | `pytest production/` | Tested (dry-run) |
| **Total** | **≈ 1,387** automated tests, plus the smoke and screenshot checks | | |

---

## 2. Features by layer

### 2.1 Strategy, canon and research (docs)

| Feature | Where | Status |
|---|---|---|
| Brief and canon updates 1–4 (volume, ascension ladder R1–R6, comment economy) | `BRIEF.md` | Spec |
| Offer, funnel, characters, safety rules, evidence base | `OFFER.md`, `FUNNEL.md`, `CHARACTERS.md`, `SAFETY_RULES.md`, `EVIDENCE.md` | Spec |
| Competitor teardown (Yang Mun's 244 posts) and video reverse-engineering | `POSTDB_FINDINGS.md`, `VIDEO_RE.md`, `data/`, `video/` | Built (analysis) |
| Content system: 20 pillars, 39 formats, uniqueness rules | `CONTENT_SYSTEM.md`, `ARCHETYPES.md`, `HOOKS.md` | Spec |
| Organic engine: runway, cadence, windows, launch week, borrowed audiences | `ORGANIC_ENGINE.md`, `tools/organic_engine.py` | Spec + model |
| Economics and costs (scenarios, MRR blitz, cost model) | `ECONOMICS.md`, `COSTS.md`, `economics.xlsx`, `mrr_*.csv`, `tools/build_costs.py` | Built |
| Stack decision, sub-$1K audit, final no-waste stack (Tier B) and bake-off B1–B10 | `STACK_DECISION.md`, `STACK_AUDIT_SUB1K.md`, `STACK_FINAL.md` | Spec (bake-off not run) |
| Virality system (rubric, render rules, reward) | `VIRALITY_SYSTEM.md` | Built + tested |
| Engine research: 10 per layer (ENGINE_100X) and the next 50 per layer (ENGINE_NEXT50) | `ENGINE_100X.md`, `ENGINE_NEXT50.md` | Spec |
| Audits (business, code, final verifier) with fix status | `AUDIT_*.md` | Built |
| Paid ads plan, blitz ops, expansion | `ADS.md`, `ADS_SCRIPTS.md`, `BLITZ*.md`, `EXPANSION.md` | Spec |

### 2.2 Facebook, Instagram, TikTok, YouTube, Threads, X (posting layer)

| Feature | Where | Status |
|---|---|---|
| 90-day posting plan: 13,800 rows, 7 handles × 6 platforms, CTA phase rules | `tools/build_posting_plan.py`, `validate_plan.py`, `data/content/posting_plan_90d.csv` | Built + tested |
| Posting rules: the 06:00–21:30 ET envelope, prime slots, hashtag caps per platform, Trial Reels for the first 14 days, top-3 remix in 24 h | `tools/posting_rules.py` | Built + tested |
| Platform packaging: native captions, footer, AI flags, X link strip, CTA rewrite where no DM automation exists, UTM + `pid` links | `workers/packager/packager.py` (`POST /package`) | Built + tested |
| Manual post pack for any platform (the fallback publisher) | `workers/packager/fallback.py` | Built + tested |
| Launch-day plan: 6 posts, rubric ≥85, upload-tonight checklist, bios | `production/launch_day/` | Built (dry-run); needs a person to post |
| Platform API review docs (Meta app review, TikTok content posting audit, YouTube compliance) | `docs/platform_reviews/` | Spec; needs accounts |
| Publishing nodes in n8n (gated off until `LAUNCH_MODE=live`) | `n8n_core_workflow.json`, `deploy/scripts/n8n_import.py` | Built; needs keys and app approvals |
| Facebook Group, Messenger Marketing Messages, Trial Reels at 10–20/day, A/B covers | ENGINE_100X / ENGINE_NEXT50 | Spec |

### 2.3 Hooks and scripts

| Feature | Where | Status |
|---|---|---|
| 190 organic scripts, 101 wave-2 drafts, 40 ad scripts, 430 hooks, a 30-day calendar and R7/R14/R21 runway calendars | `data/content/` | Built |
| Content build and validators: proven-grammar share ≥45%, claims, mortality, uniqueness shingles, ads | `tools/build_content.py` → `SCRIPTS.md`, `SCRIPTS_COVERAGE.md` | Built + tested (build fails on violations) |
| Virality rubric (100 pts, gate 60, launch 85) | `tools/virality.py` | Built + tested |
| Prompt chain: idea miner → writer → judge → shot planner → variants → captions → QA vision → localization | `prompts/01–08`, `prompts/blocked_claims.json` | Built; generation needs `ANTHROPIC_API_KEY` |

### 2.4 Modular production (render and assembly)

| Feature | Where | Status |
|---|---|---|
| Voice stitch and segmentation, word timings | `workers/assemble/voice.py` (`POST /voice/stitch`) | Built + tested; ElevenLabs needs a key |
| Master assembly: 1080×1920, −14 LUFS, word-by-word captions (Figtree, never gray), AI tag, PiP, study cards, ducked bed, C2PA, pHash/audio fingerprint, `_clean` mezzanine | `workers/assemble/assembler.py` (`POST /assemble`) | Built + tested |
| Render preflight R1–R6 (frame-1 hook, captions, interrupt by 3 s, loop ending, safe areas, cover) | `workers/assemble/virality_gate.py` | Built + tested |
| Platform variants: hook burn-in, trim, cover, re-sign | `workers/assemble/variants.py` (`POST /variants`) | Built + tested |
| Graphics: carousels, study cards, static | `workers/assemble/graphics.py` | Built |
| Deterministic QA: spec, loudness, black/freeze, OCR CER, C2PA, ArcFace/SyncNet hooks | `workers/qa/` (`POST /qa`, `/qa/score`) | Built + tested; ArcFace needs the model, SyncNet needs a GPU worker |
| Uniqueness guard: TF-IDF, MinHash, shingles, pHash, Chromaprint, stagger | `workers/uniqueness/` (`POST /uniqueness/check`) | Built + tested; Supabase siblings need a key |
| End-to-end Day-1 renderer (Nano Banana → ElevenLabs → Kling/fal → assemble) | `production/launch_day/render_day1.py` | Dry-run (default); live needs Gemini, ElevenLabs and fal keys |
| Locked reference prompts (sha256), acceptance checklist, render script | `production/refs/` | Built (dry-run); needs a human sign-off |
| Voice design, calibration lines, pronunciation lexicon | `production/voices/` | Built (dry-run); needs ElevenLabs |
| First 150 render jobs, weekly queue, shot list | `production/shot_list/` | Built |
| B-roll prompts (60) and builder | `production/broll/` | Built (dry-run) |
| Performer call sheet (205 rows) | `production/performer/` | Built; needs a shoot and a performer release (`TEMPLATES/performer_release.md`) |

### 2.5 Compliance and safety

| Feature | Where | Status |
|---|---|---|
| Deterministic scanner: blocked claims, SAFETY §3.1 regexes, movement and food rules, disclosure, ad JSON, anti-evasion normalisation (NFKC, confusables, leetspeak, fuzzy) | `workers/compliance/scanner.py`, `textnorm.py/.js` | Built + tested |
| Mandatory LLM judge (fails to human) | `workers/compliance/judge.py`, `prompts/03` | Built + tested; needs `ANTHROPIC_API_KEY` |
| Human review queue (`v_human_queue`) | `schema.sql` | Built |
| Reviewer gate (`REVIEWER_SIGNED`) | workers + app | Built; needs a signed credentialed reviewer |
| Crisis classifier and safe chat pipeline (988 / 911 / Eldercare Locator, on-call alert) | `app/src/lib/safety/` | Built + tested; production needs a key and an on-call person |

### 2.6 Learning loop (growth engine)

| Feature | Where | Status |
|---|---|---|
| Metrics adapters (IG/FB Graph, TikTok, YouTube, Threads, X) → snapshots at 1/3/6/24/72 h | `workers/growth/adapters.py`, `snapshots.py` | Built + tested; live fetch off (`GROWTH_LIVE_METRICS=0`), needs tokens |
| Baselines (median/MAD, empirical Bayes) and composite score (WINNER/PROMISING/NORMAL/LOSER) | `baselines.py`, `scoring.py` | Built + tested |
| Thompson-sampling allocator (pillar × grammar × format × speaker × length), hook-family arm, 20% exploration floor | `allocator.py` | Built + tested |
| Winner actions: remix jobs, boost candidates, pins, loser down-weights | `actions.py`, `approvals.py` | Built + tested |
| Spend governor: deterministic plan, hash-chained audit, executor that refuses | `governor.py`, `adpolicy.py` | Built + tested (3,000-state property test); spend off by design, no ad client |
| Growth n8n workflow (hourly metrics → score → actions; nightly allocate → governor dry run → Slack) | `n8n_growth_workflow.json` | Built + tested (contract) |
| Growth schema with RLS and append-only ledgers | `schema_growth.sql` | Built + tested (SQL) |
| YouTube `engagedViews`, IG `reels_skip_rate`, trial-only hook lab, dip finder | ENGINE_100X / ENGINE_NEXT50 | Spec |

### 2.7 Audience ownership

| Feature | Where | Status |
|---|---|---|
| Waitlist (`/waitlist`, confirm, unsubscribe), consent log, launch cron | `app` | Built + tested; email needs Resend or Postmark |
| Bio-link hub `/go`, TikTok `/tt`, keyword redirect `/b?t=` with attribution | `app/src/lib/bioLinks.ts`, `src/app/b/route.ts` | Built + tested |
| Lifecycle email engine (12 sequences) and 7am digest | `app/content/lifecycle/`, `/api/cron/lifecycle`, `/api/cron/digest` | Built + tested; needs an email key |
| Web push (PWA): opt-in after the first session, daily nudge, renewal copy | `app/public/sw.js`, `src/lib/push.ts` | Built; needs VAPID keys |
| SMS (CANCEL/STOP inbound; reminders) | `app` Twilio | Built; off until 10DLC |
| Warm-list import templates and sequences | `data/warm_lists/` | Built; needs counsel sign-off |
| Meta CAPI and TikTok Events (consent-only, hashed email) | `app/src/lib/conversions` | Built + tested; needs pixel and tokens |

### 2.8 Monetization and DM

| Feature | Where | Status |
|---|---|---|
| Shopify store build: 13 products, collections, selling-plan specs, discounts, metafields, webhooks, policies, OS 2.0 theme (cell-aware, consent on the page, no express buttons) | `shopify/` (`npm run provision`, dry run by default) | Built + tested (128, Theme Check 0); needs the store and the client's ~175 clicks |
| Founding cap = real inventory (5,000), seat ledger, close-founding | `shopify/src/seatLedger.ts`, app webhook | Built + tested |
| Post-purchase one-click app | `shopify/app-postpurchase/` | Built; off at launch (needs Shopify approval) |
| Members app: Today, Kitchen, programs, retest, Strong Weeks, printables (watermarked), partner seat, cancel flow (≤2 screens, one save offer), self-serve refund, gifts, affiliates | `app/` | Built + tested |
| Shopify webhook handler (orders/paid incl. renewals, refunds, cancels, inventory, customers) | `app/src/lib/billing/shopifyWebhook.ts` | Built + tested; needs a secret |
| Stripe path (legacy, behind the adapter) | `app/src/lib/billing/stripe.ts` | Built + tested; not the launch path |
| Price tests ($25/$30; cells e7/e12/e15/m12) | app + theme | Built + tested |
| DM keyword bot (IG/Messenger webhook, signature check, 14 flows, 750/h awareness) | `workers/dm/bot.py`, `sender.py`, `APP_REVIEW.md` | Built + tested; live send needs Meta app review and tokens |
| Admin: MRR, cohorts, refunds, `/admin/today`, `/admin/exceptions`, affiliate statements | `app/src/app/admin` | Built + tested |
| R3 coached program products ($97/$147/$197) | `shopify/config/catalog.ts` | Built (catalog); needs coaches and a delivery process |
| R4–R6 (labs, supplements, clinician protocols) | BRIEF canon 4 | Spec; the client's clinical entity |

### 2.9 Characters and retention

| Feature | Where | Status |
|---|---|---|
| Character bible: backstory, visual spec, wardrobe, voice, 8 sets, 24 running bits | `CHARACTERS.md` | Spec |
| In-app AI chat in character with scope and output guards, opt-in memory | `app/src/app/app/chat` | Built + tested; needs a key |
| Strong Weeks streaks with grace, monthly retest and trend chart | `app` | Built + tested |
| Series, "Your wins" episodes, 12-week arc | ENGINE_100X / NEXT50 | Spec |

### 2.10 Risk, ops and deploy

| Feature | Where | Status |
|---|---|---|
| Ops stack: n8n (queue mode), Postgres, Redis, workers, DM bot, Caddy on one Hetzner box; cloud-init | `deploy/docker-compose.yml`, `cloud-init.yaml`, `caddy/` | Built; needs a server |
| Migrations with RLS verification, secrets check, n8n import gating | `deploy/scripts/` | Built + tested |
| Pre-launch deploy to Vercel (dry run by default) and a local pre-launch stack with screenshot contrast checks | `deploy/vercel_prelaunch.sh`, `deploy/local/` | Dry-run; `APPLY=1` needs Vercel and Supabase keys |
| Worker auth (fail-closed token/HMAC), SSRF fetch policy, sanitised errors | `workers/common`, `app.py` | Built + tested |
| Exceptions API (every human decision, append-only) | `workers/common/exceptions.py`, `app` `/admin/exceptions` | Built + tested |
| Launch runbook D−30 → D0, go/no-go, money QA | `LAUNCH_RUNBOOK.md`, `LAUNCH_CHECKLIST.md`, `ACCOUNT_SETUP.md` | Spec; needs the client |
| Contracts: affiliate, performer release, reviewer | `TEMPLATES/` | Draft; needs counsel |
| Policy pages (terms, refunds, privacy, health data, safety) | `app`, `shopify/src/legal.ts` | Draft; needs attorney review |

---

## 3. What blocks go-live (keys and people, in order)

1. Shopify store + Subscriptions plans + app token (`SHOPIFY_*`).
2. Supabase (app and pipeline) + Vercel.
3. Resend or Postmark domain.
4. `ANTHROPIC_API_KEY` (judge, chat, generation).
5. Gemini, ElevenLabs and fal keys (render).
6. Meta app review and tokens (publishing, DMs, insights), TikTok and YouTube API approvals.
7. C2PA signing certificate.
8. Signed credentialed reviewer, on-call person, cultural reviewers, coaches for R3.
9. Performer shoot.
10. Counsel review of the policies and the auto-renew terms.
11. 10DLC for SMS.

## 4. Known inconsistencies found during this recap

- POSTING_PLAN.md text says 21,756 rows; the CSV now has 13,800 (regenerated after canon 4). The summary tables should be rebuilt (ENGINE_NEXT50 X-H2).
- VIRALITY_SYSTEM §6 item 6 attributes the all-adult Pew figures to 65+ (ENGINE_NEXT50 X-H1).
- The canon-4 page count (4) and the plan file's handle count (7) differ. The allocator and costs should use one number.
- Script supply covers about 8–12 days at 24/day. The other 87% of planned rows depend on daily generation (judge plus human review throughput).
