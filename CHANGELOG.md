# CHANGELOG: everything built, decided and changed (append-only; newest at the bottom)

Every round, decision, canon update, number and file is logged here so nothing is lost. Format: date, what, where, why, status.

## 2026-09-30
- Teardown of Yang Mun (IG, TikTok, YouTube, Threads, X; 244 posts, 3,154 comments, 26 video forensics) → POSTDB_FINDINGS.md, VIDEO_RE.md, data/posts.*
- Characters (Chang Yin, Sun Yoon) + 10 archetypes → CHARACTERS.md, ARCHETYPES.md
- Content system, 390 hooks, 150 organic + 40 ad scripts, safety rules, evidence → CONTENT_SYSTEM.md, HOOKS.md, SCRIPTS.md, ADS_SCRIPTS.md, SAFETY_RULES.md, EVIDENCE.md
- Offer, funnel, ads, economics (R1–R19), blitz plan, ops, launch checklist → OFFER.md, FUNNEL.md, ADS.md, economics.xlsx, BLITZ.md, BLITZ_OPS.md, LAUNCH_CHECKLIST.md
- Pipeline, n8n core (109 nodes), schema, prompts, workers (compliance, assemble, QA, uniqueness, packager), members app (Stripe path), products (19 PDFs, 30 sessions, 6 programs, 50 recipes), prototype → PIPELINE.md, workers/, app/, products/, prototype/
- Audits rounds 1–4 → AUDIT_CODE.md, AUDIT_BUSINESS.md, AUDIT_FINAL.md

## 2026-10-01
- CANON UPDATE 2: Shopify commerce, no $1 trial, ebook front end $7/$12/$15, members app provisioned by webhooks, organic-first → BRIEF.md
- Organic-first model R20–R26, Organic_First sheet → tools/organic_engine.py, economics.xlsx, BLITZ.md §13
- Growth engine (metrics, scoring, winners, allocator, spend governor), schema, n8n growth (44 nodes) → workers/growth, schema_growth.sql, n8n_growth_workflow.json
- App: Shopify billing adapter, waitlist/prelaunch, launch sequence, attribution, CAPI/TikTok events, /b, /go → app/
- Shopify store provisioning, theme, post-purchase app (off), RUNBOOK → shopify/
- Organic playbook, account setup, 40 runway scripts → ORGANIC_ENGINE.md, ACCOUNT_SETUP.md, RUNWAY_SCRIPTS.md
- CANON UPDATE 3: cell B default ($12 = books + first month → $25), STARTER12, store-wide webhooks only, Essentials via human queue → BRIEF.md, INTEGRATION.md, LAUNCH_RUNBOOK.md
- Audit round 5 (critical: founding renewals vs cap; high: memberships never lapsed) fixed → AUDIT_FINAL.md §9
- Dashboard /admin/today + exceptions queue + digest; deploy kit + CI; DM bot (14 flows) + fallback post pack; production prep (refs, voices, 150 jobs, call sheet, B-roll); lifecycle (12 sequences) + affiliates + gift → app/, deploy/, workers/dm, production/
- GitHub repo garrisonsakes/strong-years (private) created; pushed
- Concept renders: chang_a/b, sun_a (Soul 2) → production/refs/out/concepts
- Launch-day prep: 6-post plan, render_day1.py (dry-run), bios, pfp, UPLOAD_TONIGHT.md, prelaunch deploy, warm-list sequences, platform review docs → production/launch_day, deploy/, data/warm_lists, docs/platform_reviews
- Posting plan 90d + cost model → POSTING_PLAN.md, COSTS.md, economics.xlsx Costs
- Virality system: rubric gate, assembler preflight, share+save reward, posting rules → VIRALITY_SYSTEM.md
- CANON UPDATE 4: 4 pages × 6, one render reposted, ascension ladder R1–R6, comment economy → BRIEF.md
- Stack research ×3 → STACK_DECISION.md, STACK_AUDIT_SUB1K.md, STACK_FINAL.md (Tier B ≈ $1.28/video)
- Engine research: ENGINE_100X.md (10/layer, 13 holes), ENGINE_NEXT50.md (50/layer), SYSTEM_RECAP.md
- Modular variants + Trial Reels engine, 6/12/24 h component scorecard, block-level learning, weekly gate refit, FB native, accessibility → workers/growth/variants.py, scorecard.py, predict.py, tools/refit_gate.py
- Monetization engine: intent→offer routing, qualify-in-2 DMs, price flexibility, experiment arms, RPC panel → MONETIZATION_ENGINE.md, workers/dm/routing.py, app/lib/offers
- CANON UPDATE 5: no paid media until ≥$30K MRR, all-in cost ≤25% MRR, $100K ≤45d, $250K in 60–90d, 20 Trial Reels/page/day, scale-on-MRR ladder, seeded launch → BRIEF.md
- Aggressive projection (per-platform posts/views, funnel, MRR, retained, cash, costs, margin) → data/projection_aggressive_central.csv, economics.xlsx Projection_Aggressive

## 2026-10-02 (launch prep)
- (this round) niche crawler + MRR-weighted go-hard; Spanish character; 10-more-per-sublayer; 20-item savage round; R30–R36 scale model + governor gate/cap/ladder; brutal audit round 6; launch-day pack for proxy accounts; LAUNCH_LOG.md started
- Discover: workers/discover/ niche crawler (official APIs → yt-dlp → robots/ToS-gated public pages, DISCOVER_LIVE off by default), posts.csv + niche_posts genes, trend/transfer detector, guarded remake briefs, value_score (50/50, print 30/70) + GO-HARD mrr_plan + weekly readout, schema_discover.sql, n8n_discover_workflow.json (disabled), data/discover/seeds.json (60 queries, 100 creators to verify) → PIPELINE §7.6
- Sublayer + savage round: ENGINE_SUBLAYERS.md (48 sub-units × 10 = 480 items; new facts P1–P6: YT quota 6 uploads/project/day, TikTok unaudited = private, Shopify drops webhooks after 19 fails, Supabase 7-day backups, Gmail/Yahoo 0.3%) and ENGINE_SAVAGE20.md (20 new moves + launch-tomorrow cut: 8 offline builds, zero-build rules, week 1, later) → docs only, nothing built
- Scale plan to $250K: R30–R36 port of data/projection_aggressive_central.csv (R30A reproduces it cell-for-cell; R30–R36 step ladder, $30K gate and 25% cap on trailing-7-day RETAINED MRR; R31 lists 150K, R32 upside, R33 conservative, R34 ladder off, R35 ascension off, R36 FB off; legacy Organic-max renamed OM30–OM35) → tools/organic_engine.py, tools/organic_max_sheet.py, economics.xlsx Organic_Max, mrr_blitz_daily.csv (+35 r30…r36 columns), BLITZ.md §14; governor spend gate + all-in cap + scale_rules ladder → workers/growth/governor.py, config.py, tests
- Spanish market (Oct 2): Don Chuy & Doña Lupe duo chosen over Doña Carmen (staged) with cited US-Hispanic 55+ research → CHARACTERS_ES.md; 78-prompt ref pack + voices (es-US design, calibration, pronunciation) → production/refs_es/, production/voices/es/; 40 hooks + 40 scripts (25 runway, 15 launch) validated by tools/build_content_es.py (hooked into build_content.py; BC26–BC37 Spanish blocked claims, garantía / "de por vida" / "bloqueado mientras sigas suscrito") → SCRIPTS_ES.md; Años Fuertes Shopify Markets copy, handles, legal ⚖ flags, 3 emails → OFFER_ES.md; LISTA/LIBRO/UNIRME → FUNNEL §4.20–4.22; ES rows with configurable start ($30K rung) → tools/build_posting_plan.py; ES → PT → DE clone checklist → EXPANSION §0A
- Launch-tomorrow cut, tested (ENGINE_SAVAGE20 §B(b) 1–8 + #1 + #2): keyword registry test; competitor-corpus, caption-rule, frame-1 OCR, manual-CSV import, posted-log and hook pre-screen tests → workers/tests/test_launch_tomorrow.py, production/launch_day/tests/test_keywords.py; fixes: caption time-word rewrite no longer touches the §4.3 red-flag line ("That's for your doctor, today."), manual import joins carry the posted log's offset timestamp and the snapshots platform name
- CANON 6 topology + D1–D7 velocity ramp (4 IG + Threads/X each, 4 TikTok, 1 FB, 1 YT; Stories 09:00/13:00/19:30; 10 hook probes/day) → tools/topology.py; per-account .ics for launch day + week → tools/slots_ics.py --canon6
- Product library → 1,124 gated script briefs (30 sessions, 6 programs, 50 recipes × 4 grammars; virality gate + compliance + competitor corpus + keyword registry) → tools/product_to_scripts.py, data/content/product_briefs.json; tools/launch_gate.py (CI content job, which also runs tools/test_launch_tools.py); LAUNCH_CHECKLIST_TOMORROW.md
