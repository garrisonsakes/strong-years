# CLAUDE.md: Strong Years (start here)

Owner: Garrison Sakes. Private repo `garrisonsakes/strong-years`. Handed off from claude.ai on Oct 2, 2026.

## What this is
This repo rebuilds and improves on the AI monk influencer "Yang Mun". There are two disclosed AI characters:
- **Chang Yin** (74) is a jacked retired welder. He covers strength, mobility, breath and rehab.
- **Sun Yoon** (76) is his wife, sweet but blunt. She covers the kitchen and remedies.

The product is the "Strong Years" MRR membership on Shopify. Growth is organic-first across IG, TikTok, FB, YT Shorts, Threads and X.

**Targets**
- $10K MRR by day 3–4
- $100K by day 45 at the latest
- $250K in 60–90 days
- 70–80%+ margin, ads included
- No paid media until retained MRR ≥ $30K

**Content:** 25–30 unique videos/day for ≤$1K/mo. Fully automated, minimal manual work.

## Canon (read in this order)
1. `BRIEF.md`. The CANON UPDATE 2–6 sections at the end override the earlier text, and **6 is newest**.
2. `CHANGELOG.md` is the append-only log of every decision. Append to it after each round.
3. `LAUNCH_RUNBOOK.md` gives the order of operations, and `LAUNCH_CHECKLIST_TOMORROW.md` is the day-1 checklist.
4. `INTEGRATION.md` holds the Shopify decisions with citations. `AUDIT_FINAL.md` covers audit rounds 1–5; round 6 is partial.

### Canon 6 core
**Offer**
- $12 today buys the Starter Books plus a 7-day founding-membership trial (mechanism: STARTER12 first-payment discount).
- The first $25 charge lands on day 7, then every 30 days.
- 5,000 founding seats, enforced as inventory.
- After the cap, standard is $35/mo. Other prices: $249/yr, $12 Essentials, gifts $49/$119.
- No $1 trial, ever.

**Accounts**
- IG: 4 pages, going to 6 at $30K retained MRR. Each page posts 6 main + 20 Trial Reels + 3 Stories per day, and gets its own Threads (12/day) and X (6/day).
- TikTok: 4→6 accounts × 26/day. Posted manually until the API audit passes.
- FB: ONE page (→2 only if easy) × 16/day.
- YT: ONE Shorts channel × 6/day (4/day until the quota is raised).
- Total: 300→458 posts/day.
- No collabs.

**Model of record:** `data/projection_master.csv` (gitignored, so use `git add -f`), plus the first sheet of `economics.xlsx`, `tools/organic_engine.py` and `tools/montecarlo.py`.

**v5 inputs**
- Views per video ramp by day: d1 500, d2 750, d3 1000, d4 1500, d5 2000, d6 2500, d7 3000, d8 3500, d9 4000, d10 5000, then +1000/day to 9000 at d14, and 10000 after.
- Hit factor: ×(1+40/150).
- Platform multipliers: FB 0.8, TT 0.7, YT 0.5, Threads/X 0.15. Trial Reels ≈ 1:1 with main feed.
- No page caps and no arbitrary multipliers.

**Conversion assumptions**
- Stories: 8% reach → 1.5% tap → 6% buy.
- Comments: 0.15% of views → 15% keyword → 95% DM delivered → 45% click → 8% buy.
- Bio: 0.2% click → 4% buy. Landing loads 70% of the time.
- Trial: 60% convert, 7%/mo churn.
- Coached tier: 5% at $147 from day 10.
- Seeds: waitlist of 1,500 at 10% over 3 days; lists of 30K at 1.5% over 14 days.

**Cost assumptions**
- $1.28 per master video, $0.225 per trial variant, $16/day fixed.
- Review: 20s per post at $20/h.

**Central results**

| Day | Retained MRR | Booked MRR | Cash |
|---|---|---|---|
| 30 | $116K | $138K | $138K |
| 45 | $205K | — | $293K |
| 60 | $292K | — | $502K |
| 90 | $455K | — | $1.04M |

Retained-MRR milestones: $10K d8, $30K d15, $100K d28, $250K d53.

Always report **booked MRR, retained MRR and cash** separately. MRR can never exceed what cash implies.

## Stack
**Commerce:** a separate Shopify store (never K9SUPPS) running the free Shopify Subscriptions app. Access comes only from store-wide webhooks:
- orders/paid, orders/cancelled
- refunds/create
- customers/update and customers/delete
- inventory_levels/update
- app/uninstalled
- disputes/*

subscription_contracts/* is enrichment only.

**`app/`:** Next.js App Router, TS strict, Tailwind, Supabase (RLS deny-by-default).
- Email-code auth and watermarked PDFs.
- Crisis-safe chat that fails closed.
- Waitlist/prelaunch mode, `/go` hub, `/b` keyword redirect.
- Server-side CAPI/TikTok events, consent-gated, no health data.

**`workers/` (Python FastAPI)**
- compliance: scanner → LLM judge → human review.
- assemble: virality preflight (hook ≤7 words on frame 1, captions, pattern interrupt by second 3, loop, safe areas).
- uniqueness: modular variants with roles TEST, PLACEMENT and REMIX. A body never repeats on the same page × platform within 30 days, and each variant changes 2+ dimensions.
- growth: metrics, velocity, Thompson-sampling allocator, per-component scorecard at 1/6/12/24h/7d, weekly gate refit.
- spend governor: opens at $30K retained MRR, keeps all-in cost ≤25% of MRR, follows the scale ladder. `SPEND_ENABLED=false`, dry-run, never calls ad APIs.
- discover: niche crawler, trend transfer across platforms, remake briefs with a plagiarism guard, MRR-weighted GO-HARD.
- dm: 14 keyword flows, inbound only.
- packager: fallback manual post pack.

**`shopify/`:** provision.ts, theme, RUNBOOK.md.

**`deploy/`:** compose, migrations, n8n import (core 109 nodes, growth 44, discover; publish and spend nodes disabled), `secrets.example.env`, cloud-init, CI.

**Video (STACK_FINAL Tier B ≈ $1.28/video)**
- Stills: Nano Banana 2 (gemini-3.1-flash-image, batch).
- Voice: ElevenLabs v3 with a fixed voice ID (Fish S2-pro as an alternative).
- On-camera slices only: Kling AI Avatar v2 Standard on fal (`fal-ai/kling-video/ai-avatar/v2/standard`, $0.0562/s); Hedra Character-3 as backup.
- Assembly: ffmpeg/Remotion. No CapCut.
- Kling Motion Control is for exercise demos only and needs a performer shoot.

**`production/`:** refs, voices, shot list, performer call sheet, `launch_day/render_day1.py`, `bios.md`, `UPLOAD_TONIGHT.md`, `pfp/`.

Concept renders are in `production/refs/out/concepts/`. Fixes still to apply:
- Chang: 1cm beard, flannel, plain ring, eyebrow scar.
- Sun: real kimchi jars.

**`tools/`:** build_content.py (generator + virality gate), posting_rules.py, refit_gate.py, product_to_scripts.py (1,124 briefs), topology.py, slots_ics.py, launch_tool, organic_engine.py, montecarlo.py, `gpt_bridge.py` (key read from env only).

**Research and strategy docs (root):**
- POSTDB_FINDINGS, VIDEO_RE
- CHARACTERS (+_ES: Don Chuy & Doña Lupe), ARCHETYPES
- CONTENT_SYSTEM, HOOKS
- SCRIPTS, RUNWAY_SCRIPTS, WAVE2_SCRIPTS, SCRIPTS_ES
- ORGANIC_ENGINE, ACCOUNT_SETUP
- FUNNEL (§4 DM flows), OFFER(+_ES), ASCENSION, MONETIZATION_ENGINE, EXPANSION
- VIRALITY_SYSTEM, STACK_DECISION, STACK_AUDIT_SUB1K, STACK_FINAL
- ENGINE_100X / NEXT50 / SUBLAYERS / SAVAGE20
- SYSTEM_RECAP, POSTING_PLAN, COSTS, PROJECTION, BLITZ

## Run the suites
At last report: app 595 unit / 18 e2e, workers 737, shopify 128.
- app: `cd app && npm ci && npm test && npm run test:e2e`
- workers: `cd workers && pip install -r requirements.txt && pytest -q`
- shopify: `cd shopify && npm ci && npm test`
- tools: `python3 tools/build_content.py` (see Known bugs)

## Known bugs / audit round 6 (unfinished; do these first)
1. `tools/build_content.py`: KeyError `_proven`, and 166 wave-2 scripts fail the gate. Make it green.
2. `test_render_day1.py` fails on HEAD with a speech-rate error.
3. Verify the 7-day trial end to end on a Shopify **dev store**. A 7-day first cycle is not native to the free app.
4. Build a Shopify webhook retry/re-register job. Shopify deletes a webhook after 19 failures.
5. Draft the YouTube quota increase request (~6 uploads per project per day; 4/day fallback).
6. Write `LAUNCH_DAY_PROXY.md`: an hour-by-hour plan with day-1 velocity.
7. Never let two agents write `economics.xlsx` at once; it was corrupted once and restored from e7702f0.

## Waiting on Garrison
- API keys: Gemini, fal.ai, ElevenLabs.
- The new Strong Years Shopify store, connected.
- Supabase, Vercel and Resend accounts.
- Real list sizes for Unignorable and K9SUPPS.
- Social accounts, created by him via proxy.
- Meta app review.
- Reviewers: attorney, PT/dietitian, cultural.
- Performer shoot.
- Names for the single FB page and the single YT channel.

## Token efficiency (always on)
Every session here bills Garrison's limited credits, so spend tokens only where they change the result.
- Search before reading: use Grep/Glob, then Read only the line range you need. Never re-read a file you already have unless it changed.
- Keep command output short: `pytest -q`, `npm test --silent`, and pipe long output through `tail -n 60` or `grep`. Compute, count and filter in a script and print only the summary.
- Read the canon docs only when the task needs them. CLAUDE.md is the summary; open BRIEF.md and others for detail, not by default.
- No subagents or parallel threads unless the work is truly independent and large. Do simple tasks directly.
- Batch independent tool calls in one step. Make edits with one validated push, not several speculative ones.
- Keep replies short: lead with the answer, no recaps of the investigation.
- Repo settings in `.claude/settings.json` cap Bash and MCP output and block reads of generated or binary files (node_modules, lockfiles, PDFs, media). Grep the source instead.

## Hard rules
**Never without Garrison:** spend money, create accounts or post from them, message real people, or sign up for anything.

**Off-limits:** never touch K9SUPPS, never use the FA ad accounts, no B2C cold email, no cookies or private APIs.

**Repo hygiene:** keep the repo private and never commit keys. The OpenAI key was pasted in the old chat; **rotate it**.

**Compliance**
- IG AI-generated label is mandatory.
- Follow YT's July 2026 inauthentic-content policy: distinct YT cuts.
- FTC, ROSCA and state auto-renew laws, CA SB 243.
- No disease, fall or mortality claims. No condition hashtags. Never say "for life". Use "guarantee" only in the refund phrase.

**Style:** no gray text, no `//` or mono kickers.

**Commit trailer:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Next steps after round 6
1. Once keys and the store exist: run the 48h render bake-off and get the faces and voices approved.
2. Place dev-store test orders.
3. Deploy (deploy/).
4. Post per LAUNCH_CHECKLIST_TOMORROW.md.
