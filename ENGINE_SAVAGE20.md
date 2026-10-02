# ENGINE_SAVAGE20.md: the 20 highest-leverage moves nobody has listed yet, and the launch-tomorrow cut

Round of Oct 2 2026. Deduped against ENGINE_100X.md (§1–11), ENGINE_NEXT50.md (550 items) and ENGINE_SUBLAYERS.md (480 items). Sources: P1–P6 in ENGINE_SUBLAYERS.md, S# in ENGINE_100X §12, N# in the ENGINE_NEXT50 header. Multipliers are planning estimates **on the named metric, for the slice the item touches**, not forecasts. No spending, accounts or external AI were used.

---

## A. The SAVAGE 20

| # | Move | Multiplier → metric | Conf |
|---|---|---|---|
| 1 | Product library becomes the script source | 5× → days of approved-script coverage | M |
| 2 | Zero-render hook pre-screen on text surfaces | 3× → validated hooks per render-dollar | M |
| 3 | Render once, use twice (app sessions ↔ organic) | 2× → organic posts per render-dollar | M |
| 4 | Posting cockpit for human and proxy posters | 3× → on-time placements per day while APIs are gated | H |
| 5 | API capacity critical path (YouTube quota, TikTok audit, Meta review) | 4× → automated placements per day by week 3 | H |
| 6 | Span-highlighted review | 3× → human review throughput | M |
| 7 | Beta cohort of 50 real 60+ users before D+7 | 1.3× → checkout conversion; 2× → bugs found pre-scale | M |
| 8 | Monday cohort start for every new member | 1.5× → day-30 member retention | M |
| 9 | Unit-economics throttle per page | 1.5× → cost per owned contact (lower) | M |
| 10 | Feature flags per page × platform × feature | ÷4 → pages hit per incident | H |
| 11 | One trace id from brief to revenue | ÷3 → mean time to repair | H |
| 12 | Programmatic answer pages on our domain | 5× → owned non-social visits (from a small base) | L-M |
| 13 | TikTok Shop listing for the $29 kit and $12 books | 5× → TikTok revenue per 1K views (from ≈0) | L-M |
| 14 | Facebook/IG native Subscriptions as a second paid rail | 2× → paid conversion of FB-native viewers who won't leave the app | L-M |
| 15 | Facebook content monetization as a second revenue line | +$ per 1K FB views (new line) | L |
| 16 | Character sticker channel (GIPHY) | ∞ → free impressions in Stories and Messenger GIF search | L-M |
| 17 | Dial-a-workout phone line | 3× → owned contacts among 75+ | L-M |
| 18 | TikTok private-only lane as free staging | ÷3 → launch-week pipeline failures on public accounts | M |
| 19 | A paid 65+ viewer panel every week | 1.3× → 3 s hold on formats the panel shaped | M |
| 20 | Transparent earned-media push ("the AI grandparents who tell you they're AI") | 10× → follows per day for about a week | L |

### 1. Product library becomes the script source · 5× → days of approved-script coverage · M
The engine's binding constraint is supply. 87% of the 90-day plan is `GEN-needed` and the library covers 8–12 days (SYSTEM_RECAP §1). Meanwhile `products/` already holds evidence-checked, voice-consistent material: 30 daily sessions (`sessions.json`), 6 programs, 50 recipes (`kitchen_recipes.json`), the Strength Reset and the 12-week printable. **Plan:** write `tools/product_to_scripts.py`, which turns each session movement and each recipe into 4–6 script seeds (one per proven grammar: IF_EVERY, MYTH, NUMBER + body part + time, reply). Claims, safety lines and evidence ids are inherited from the product source, so the judge rarely loops. Seeds go into `ideas` with `source=product` and the same uniqueness check (SL-01.2). 30 sessions × ~8 movements × 4 grammars plus 50 recipes × 4 ≈ 1,150 seeds; at a 50% judge-plus-review pass rate that is ~24 days of extra coverage at 24/day. Every organic post also becomes a preview of the paid product, which tightens the offer link.

### 2. Zero-render hook pre-screen on text surfaces · 3× → validated hooks per render-dollar · M
Hooks are tested today only after rendering (Trial Reels, NEXT50 LL-1). Text posts cost nothing to make. **Plan:** each morning, the top 12 candidate hooks for tomorrow (SL-02.1 ranker) go out as plain-text questions or statements in the characters' voice: Threads at 07:00 and 19:00 (already in NEXT50 TT-19's slots), the FB Page text post (100X §1.4), and X. Engagement per impression at 6 h ranks them (`/growth/score` with a `surface=text` baseline). Only the top 6 get rendered as trials. Text lanes have their own audiences, so this is a prior, not a verdict: the allocator treats the text score as a Beta prior with weight 5 on the hook arm. Build: `packager.py` `text_probe` role plus a `surface=text` baseline (≈4 h). It turns 10–20 trials a day per page into 10–20 *pre-qualified* trials.

### 3. Render once, use twice · 2× → organic posts per render-dollar · M
`products/VIDEO_PRODUCTION_QUEUE.json` plans the members' session videos, and the organic engine renders exercise demos separately. They are the same movements, the same characters and the same sets. **Plan:** one shot list feeds both queues. Each app session render emits (a) the full member video and (b) the clean mezzanine of every movement block as a body-bank entry (NEXT50 MOD-6 holds the reuse ledger). Organic bodies cut from member sessions carry a "this is Day 4 of the program" close, which links the content to the product. Cost per movement drops by roughly half, and the 30-day reuse ledger keeps pages distinct. Build: a shared `shot_id` namespace across `production/shot_list/` and `products/VIDEO_PRODUCTION_QUEUE.json`, plus a `body_bank` writer in `assemble/assembler.py` (≈6 h).

### 4. Posting cockpit for human and proxy posters · 3× → on-time placements per day while APIs are gated · H
Automated publishing is gated by Meta app review, the TikTok audit (posts are private until it passes [P3]) and the YouTube quota (6 uploads per project per day [P2]). For weeks, people will post. The fallback pack (`packager/fallback.py`) gives them files and captions but no loop back. **Plan:** a phone-first `/admin/post` page in the app, one card per due placement in slot order. Each card has the download button, a copy-caption button, a checklist (AI label toggled, cover chosen, trial or feed, no crossposting) and a "Posted" button that requires the permalink. The permalink feeds `posts.external_post_id`, which unlocks manual metrics import (SL-28.1) and attribution. Overdue cards turn red and then auto-skip (SL-25.2). Tonight's minimal slice is a `posted_log.csv` template and checklist inside the existing pack (§B(b) item 6); the full page lands in week 1 (≈8 h).

### 5. API capacity critical path · 4× → automated placements per day by week 3 · H
Three external queues decide when the factory can run unattended: Meta app review (publishing, DMs, insights), the TikTok Content Posting audit, and a YouTube quota extension (24 Shorts a day need 38,400 units against a 10,000 default [P2]). Each takes days to weeks, and none starts until someone files it. **Plan:** treat them as the launch's critical path, with owners and dates on `/admin/today`. File all three on D0 with the docs already in `docs/platform_reviews/`. Add a 60 s screen recording of the review app and the publish flow for each (reviewers ask for one). Until approval, route per platform: IG/FB by hand through the cockpit, TikTok via draft-to-inbox (NEXT50 TT-12), YouTube via upload-post or by hand. Add a W4 quota governor that never schedules more than 6 YouTube uploads per project per day. This is the single largest throughput multiplier in the system, and it costs forms, not code.

### 6. Span-highlighted review · 3× → human review throughput · M
Human review is the bottleneck at 24 masters plus 40–80 trials a day. Reviewers read whole scripts and watch whole videos to find the one risky sentence. **Plan:** the judge (structured output, SL-24.2) returns character spans for every sentence it considered (`risk: low|med|high`, `rule_id`), and the scanner returns its match spans. The review UI shows the transcript with only med/high spans highlighted and jumps the player to their timestamps. Green items with no highlighted span go to batch approval (SL-25.6). Track reviewer disagreement with highlights; spans the reviewer flagged that the judge didn't become golden-set cases (SL-24.1). Build: `prompts/03` output schema plus `app/src/app/admin/review` highlighting (≈6 h).

### 7. Beta cohort of 50 real 60+ users before D+7 · 1.3× → checkout conversion; 2× → bugs found before scale · M
Nothing in the system has been used by its real audience. **Plan:** from the warm lists and the waitlist (consented), recruit 50 people aged 60+ for a free 7-day run of the Strength Reset in the members app. They get the real onboarding, the real emails and the real DM flows (by hand while DMs are gated). Collect three things, with consent: a Strength Age before and after, a one-question day-7 survey, and an optional 15 s phone video. Use them as social proof in checkout and DMs (real people, clearly labelled), and as a usability pass on tap targets, font sizes and login. Founding seats are offered at the end at the normal price. It costs nothing but a coordinator's week, and it produces the only honest testimonials an AI-character brand can have.

### 8. Monday cohort start for every new member · 1.5× → day-30 retention · M
Members join on random days and start alone. **Plan:** whatever day someone buys, their program starts the next Monday, together with everyone else who joined that week ("Cohort Oct 12"). The gap days carry a 3-day warm-up with one email a day. Content, emails, the Group's weekly thread and Chang's numbered episodes (NEXT50 CH-1) can then reference the cohort's week. The members app shows "412 people started with you" (a real count). This turns one person's habit into a group's habit with no extra content cost. Build: a `cohort_start` field in `members.ts`, lifecycle step offsets keyed to it, and the count on the Today screen (≈5 h).

### 9. Unit-economics throttle per page · 1.5× → cost per owned contact (lower) · M
Pages will differ wildly in yield (POSTDB Rule 0: 40–100× from account state). 100X §10.9 throttles by platform reach. Nothing throttles a *page* by money. **Plan:** a daily job computes, per page, 7-day spend (cost ledger, SL-45.1) divided by new owned contacts (waitlist, email, Messenger opt-ins attributed by `pid`). Pages above 3× the network median for 7 straight days drop to a maintenance cadence (2 a day, trials only), and the freed budget goes to the top-quartile page. It reverses automatically when the ratio recovers. This decides the canon-5 scale-on-MRR ladder with data, not intuition. Build: a view plus an allocator budget hook (≈4 h after the ledger exists).

### 10. Feature flags per page × platform × feature · ÷4 → pages hit per incident · H
Switches today are global env vars (`LAUNCH_MODE`, `SPEND_ENABLED`, `DM_SEND_ENABLED`). One bad flow, template or model change hits all 4 pages and 6 platforms at once. **Plan:** a `flags` table (`page`, `platform`, `feature`, `state`, `rollout_pct`, `owner`) read by W4, the DM bot, the lifecycle engine and the variant builder, with a 30 s cache. Every new template, flow or model route ships to one page first, then 50%, then all, with automatic rollback when the reach-drop detector or exception budget trips. Env vars stay as the master kill switch above the flags. Build ≈6 h across `common/config.py`, `app/src/lib/config.ts` and the n8n IF nodes.

### 11. One trace id from brief to revenue · ÷3 → mean time to repair · H
A failed post today means reading n8n executions, worker logs, Supabase rows and app logs separately. **Plan:** `brief_id` becomes the trace id, carried as an `X-Trace-Id` header on every n8n → worker call, stored on renders, variants and posts, embedded in the `pid` link, and logged by the app on clicks, orders and entitlements. One admin page, `/admin/trace/<id>`, shows the whole life of a post: script, judge verdict, renders and cost, QA, review, publish, metrics, DMs, revenue. This is also the attribution backbone the learning loop needs. Build: header propagation plus one join view (≈6 h); no new vendor.

### 12. Programmatic answer pages on our domain · 5× → owned non-social visits (from a small base) · L-M
Every script answers a question older adults search for ("chair exercises for bad knees", "how much protein after 70"). Nothing we make lives on the open web; it all sits inside platforms. **Plan:** each approved script with an evidence id generates a page at `/learn/<slug>`: the question as H1, a 150-word plain answer drawn from the script and its EVIDENCE excerpt, the embedded YouTube Short, a printable card, and the waitlist or Day-1 capture. Large type, never gray, fast. The pages are indexable, are linked from YouTube descriptions, and can be shared by adult children. Quality gate: only scripts with a citation and a human-approved answer, and no thin or duplicate pages. Build ≈8 h in the Next.js app (static generation from `data/content/scripts.json`).

### 13. TikTok Shop listing for the $29 kit and $12 books · 5× → TikTok revenue per 1K views (from ≈0) · L-M
100X §3.2 found that TikTok cuts reach on posts that send people off-platform [S32], so TikTok currently monetizes only through the waitlist and the free Day 1. TikTok Shop is the sanctioned in-app path. **Plan:** once a TikTok Shop seller account exists (an account action, not for this round), list the physical kit and the printed starter book as Shop products and tag them in movement posts ("the band Chang uses"). Membership stays off TikTok. Measure revenue per 1K TikTok views against the waitlist-only baseline. Compliance: product tags only on posts with no health outcome (100X §8.2).

### 14. Facebook/IG native Subscriptions as a second paid rail · 2× → paid conversion of FB-native viewers · L-M
A share of the 65+ Facebook audience will never leave the app to check out. Meta's creator subscriptions let them pay inside the app. **Plan:** when a flagship page meets eligibility, offer a low tier ("Chang's Inner Circle", subscriber-only weekly session plus a badge) priced to sit below Essentials, so it never undercuts the members app. Subscribers get a code to claim app access at a discount, which moves them onto our owned rail. Track it as a separate cell in MONETIZATION_ENGINE §5. Risk: the platform's revenue share and dependence on it, so this stays a side rail and never the main offer.

### 15. Facebook content monetization as a second revenue line · +$ per 1K FB views · L
Facebook is a primary channel with the highest 65+ reach, and we already post native Reels, long cuts and text there. **Plan:** apply when eligible, after confirming that AI-character content with clear disclosure is allowed under the current originality rules [S3]. If allowed, route long cuts (100X §1.3) and weekly sessions there. Book it as non-MRR revenue in the projection, never as part of the canon targets. If not eligible, record the reason and stop.

### 16. Character sticker channel (GIPHY) · free impressions · L-M
Sun's one-word verdict stamp (NEXT50 HK-25) and Chang's "one more rep" are natural reaction stickers. GIPHY results appear in IG Stories, Messenger and many messaging GIF pickers. **Plan:** make 24 short transparent stickers from existing renders (verdict stamps, a thumbs-up, "Day 1 done"), tagged and disclosed as AI characters in the channel bio, and apply for a brand channel. Every use by a member or fan is a free brand impression inside private conversations, where the adult-child and peer referral loops happen. Cost: an afternoon of graphics work.

### 17. Dial-a-workout phone line · 3× → owned contacts among 75+ · L-M
The oldest viewers don't use apps or PDFs and often don't read email (NEXT50 X-H21, X-H34 sit nearby but are about support). Voice calls need no 10DLC, which applies to SMS. **Plan:** a local number where callers hear today's 5-minute session in Chang's voice (the same TTS we already render), choose 1 for seated or 2 for standing, and at the end can "press 9 to have Chang text or mail you the week's chart". Callers who leave a number or address (with consent) become owned contacts; the printed chart (NEXT50 AO-3) closes the loop. The number goes on the kit insert, the printable and the FB Page. Twilio voice plus a static IVR is about 1 day of work and pennies per call. Disclosure ("Chang is an AI character") is the first line of every call.

### 18. TikTok private-only lane as free staging · ÷3 → launch-week failures on public accounts · M
Unaudited TikTok API posts are forced to `SELF_ONLY` [P3]. That is useless for reach and perfect for staging. **Plan:** point W4's TikTok branch at a private staging account and run the full publish, verify and metrics path every day of launch week with real files, real captions and real retries. Every failure there (encoding limits, caption length, token refresh, retry doubles) is fixed before it can happen on a public account on any platform. It also produces the audit evidence TikTok asks for. No cost; it uses a constraint we have anyway.

### 19. A paid 65+ viewer panel every week · 1.3× → 3 s hold on formats the panel shaped · M
NEXT50 LL-33 has *internal* taste labels. We have no outside eyes from the actual audience. **Plan:** 10 adults aged 65–80 (local senior center or a research panel, paid per session), 45 minutes a week, watching 20 posts on their own phones. Record where they stop, what they'd share and with whom, what reads as fake, and whether captions and text are legible. Insights go to the writer prompt and the gate refit as labelled data. Cost about $500/month, so it's gated behind canon 5's spend rule, not tonight.

### 20. Transparent earned-media push · 10× → follows per day for about a week · L
"AI grandparents who tell you they're AI and point you to real coaches" is a story journalists will cover, for or against. **Plan:** prepare before anyone else frames it: a one-page fact sheet (how Chang is made, the disclosure on every post, real coaches, the safety rules and the crisis path), a behind-the-scenes Reel (NEXT50 IG-33), and named humans for interviews (NEXT50 X-H50). Pitch three aging and tech reporters in week 3, once there are real member stories (#7). Confidence is low and the variance is high, but the cost is a day, and an unprepared response (NEXT50 X-H37) is the worse version of the same event.

---

## B. Launch-tomorrow cut, across all four lists

Launch = the first public posts tomorrow at 08:00 ET, by hand from the proxy accounts (`production/launch_day/day1_plan.json`: IG and FB Reels; Kling avatar plus Veo inserts). Commerce opens later (seeded launch, canon 5). DM sends, email sends, n8n publishing and render keys are not live.

### (a) Already built (in code and tested; verify, don't rebuild)
- **100X:** §2.1 and §5.1 (TEST / PLACEMENT / REMIX roles, at most one `SS_PERFORMANCE` trial per body: `growth/variants.py`) · §2.2 and §6.2 (`reels_skip_rate` as the hook score: `scorecard.py`) · §3.1 and §6.1 (YouTube `engagedViews` denominators) · §5.2 (guard aware of same page and role: `uniqueness/guard.py`) · §5.3–5.4 (remix with ≥3 dimensions and a new voice take) · §5.9 (C2PA re-sign on variants) · §4.2–4.4 (2.5 w/s, ≥250 ms pauses, hook ≥72 px, captions ≥56 px: `assemble/accessibility.py`) · §1.1 (Facebook-specific caption and close) · §3.2 (TikTok CTA rewrite in the packager) · §8.4 (bot disclosure) and §8.7 (`HUMAN_AGENT` path: `dm/flows/_global.json`) · §6.9 (predictor stub that only ranks: `growth/predict.py`) · Holes #1 and #3 (captions, size, contrast, no music under speech).
- **NEXT50:** TT-13 (`is_aigc` on every upload) · IG-1 (partly: `trial_cap` and trial roles exist; the 10–20/day probe is not built) · LL-47 (rubric refit exists as weekly `tools/refit_gate.py`, dry run by default) · LL-2 (block- and gene-level attribution: `growth/learning.py`).
- **Elsewhere:** two-pass loudnorm, `+faststart`, the waitlist honeypot, `List-Unsubscribe`, Shopify webhook-id dedupe, the app's message outbox. SUBLAYERS and SAVAGE20 items are new by construction.

### (b) Buildable before 08:00 ET and safe to ship, in order
Rules for this list: offline code only, covered by a test, no keys, no live sends, no store or n8n changes, and each item protects tomorrow's posts or the first week of learning. Total ≈ 8.5 h, split across 3–4 parallel agents.

| Order | Item | File targets | Est. | Why tonight |
|---|---|---|---|---|
| 1 | **SL-05.1 keyword registry check** over the day-1 plan and the scripts (each keyword maps to a flow and, while DMs are manual, a manual reply script) | `tools/build_content.py`; `production/launch_day/tests/test_keywords.py` | 1h | A dead keyword on the 6 launch posts wastes the launch's comments |
| 2 | **SL-22.1 competitor-corpus similarity** run on the 6 day-1 scripts and captions | `workers/uniqueness/guard.py` `check_external()`; `workers/tests/test_uniqueness.py` | 1.5h | Launch content must not read as a copy of Yang Mun |
| 3 | **SL-06.4 + SL-06.5 caption rules** (time-relative words, handle allowlist), then re-run pass 2 on the day-1 captions | `workers/compliance/rules.py`; `workers/packager/packager.py`; tests | 1h | Hand-posted captions written days ago are where "this morning" slips in |
| 4 | **SL-08.1 frame-1 OCR per variant**, run on the 6 rendered files before upload | `workers/qa/ocr.py` `check_frame1()`; `workers/tests/test_qa.py` | 1h | The last automated check before a human uploads |
| 5 | **SL-28.1 manual metrics CSV import** (canonical schema; one row per post per read) | `workers/growth/adapters.py` `normalize_manual_csv()`; `workers/tests/test_growth_adapters.py` | 2h | Without it, the first week of hand-posted data never reaches scoring |
| 6 | **SAVAGE #4 minimal slice**: `posted_log.csv` (post_id, platform, posted_at, permalink, trial y/n, AI label y/n) and a per-post checklist in the fallback pack | `workers/packager/fallback.py`; `workers/tests/test_ops_round.py` | 1.5h | Closes the loop from a human post to a permalink to metrics (#5) |
| 7 | **SL-26.3 ICS export** of tomorrow's slots | `tools/posting_rules.py --ics`; `tools/test_posting_rules.py` | 0.5h | Posters work from their phone calendar |
| 8 | **SL-47.1 secret scan** of the repo and history; add the CI step | `.github/workflows/ci.yml` | 0.5h | Before anyone pushes launch-night fixes |

**Zero-build launch rules** (operator checklist, from all lists): upload to FB natively and never use the IG "share to Facebook" toggle (100X §1.1, NEXT50 FB-16) · AI label on in-app for every post including trials (100X §2.6, NEXT50 IG-32) · stop all trials on the first "limit" or "unavailable" message (NEXT50 RO-1) · no likes or comments between sibling pages (100X §10.4) · no follow or like automation (100X §2.10) · YouTube and TikTok by hand only (SL-27.1, SL-27.2) · an item not posted within 30 min of its slot is skipped, not posted late (SL-25.2) · one person can call "pause all" (SL-26.2).

**Deliberately not tonight:** anything that touches Shopify, webhooks, entitlements, the DM bot, email sending, n8n imports, render providers, the allocator or the gate. All of it is either not live tomorrow or too risky to change the night before (NEXT50 RO-21 change freeze).

### (c) Week 1 (D+1 → D+7), in priority order
1. **File the platform approvals** (SAVAGE #5): Meta app review, the TikTok audit, the YouTube quota extension; plus the W4 quota governor (SL-27.1).
2. **Posting cockpit, full version** (SAVAGE #4) and the TikTok staging lane (SAVAGE #18).
3. **Cost ledger and the daily 25% guard** (SL-45.1–45.7), then the per-page throttle (SAVAGE #9).
4. **Before checkout opens:** Shopify reconciliation poller, subscription check, async acknowledge, order guard (SL-39.1–39.4); entitlement reconciliation (SL-40.1); founding-seat reconciliation (SL-38.2).
5. **Before email goes out:** complaint auto-pause, split subdomains, suppression, idempotency, throttled launch send (SL-37.1–37.5, SL-36.2–36.3).
6. **Before DMs go live:** event dedupe, async acknowledge, 24 h window, STOP handling, rate limit (SL-35.1–35.5).
7. **Supply:** product library to scripts (SAVAGE #1), inventory-aware W1 (SL-01.1), hook over-generation (SL-02.1), prompt caching and batching (SL-01.4–01.5, SL-24.3, SL-24.7).
8. **Render waste:** make `rerender_shots` real (SL-15.1–15.5), TTS cache (SL-12.1), 1K-then-upscale (SL-10.1).
9. **Learning from week-1 data:** trial/feed baselines (SL-29.1), LCB hook ranking (SL-03.1), graduation rule and evening report (SL-30.1–30.2); 100X §6.5 horizons; NEXT50 LL-1 trial-only hook lab and RO-1 tripwire in code.
10. **Ops:** nightly encrypted backups and heartbeat (SL-46.1–46.6), n8n error workflow into exceptions (SL-41.1), the `LAUNCH_MODE` head check on every send branch (SL-43.1), required CI checks and the doc-number test (SL-48.1–48.2), span-highlighted review (SAVAGE #6), beta cohort recruiting (SAVAGE #7).

### (d) Later (D+8 onward, gated by canon 5's MRR ladder and the data)
- **Weeks 2–4:** feature flags and trace ids (SAVAGE #10–11); Monday cohorts (#8); render once, use twice (#3); text hook pre-screen (#2); judge golden set and two-sample borderline checks (SL-24.1, SL-24.8); the rest of SL-02/03/04/05; NEXT50's top 25 (IG-1 probe, MOD-1 hook-slice bank, MON-1 Day 1 inside the DM, AO-1, FB-3 / TT-11 dubbing, …) in its own ranked order.
- **Month 2:** answer pages (#12), dial-a-workout (#17), stickers (#16), the viewer panel (#19), the PR push (#20), uniqueness calibration and embeddings (SL-22.6–22.8), allocator upgrades (SL-32.3–32.6).
- **When eligible or when spend unlocks:** TikTok Shop (#13), FB/IG Subscriptions (#14), FB content monetization (#15), PITR (SL-46.8), invisible watermarking (SL-20.10), face-crop lip-sync (SL-14.10).
- **Everything else** in ENGINE_100X, ENGINE_NEXT50 and ENGINE_SUBLAYERS: by each file's own ranking, re-ranked monthly against measured data via the weekly readout.

### Counts
ENGINE_100X: 100 items + 13 holes · ENGINE_NEXT50: 550 · ENGINE_SUBLAYERS: 480 (48 sub-units × 10) · SAVAGE20: 20. **Total ≈1,163.** (a) about 20 built · (b) 8 builds plus 8 zero-build rules · (c) 10 groups (~45 items) · (d) the rest.
