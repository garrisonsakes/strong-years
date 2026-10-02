# PIPELINE.md: Chang Yin & Sun Yoon Content Factory

**What this is:** the production system that turns audience signals into 6–9 unique, compliance-checked, openly-AI short videos per day, per page, per platform (IG Reels, TikTok, YouTube Shorts, Facebook Reels, Threads, X). It starts at 4–6 pages and scales to 20+ pages and other languages. Humans approve only where it matters: new claims, sensitive topics, QA exceptions, and every video on a page until that page has earned trust.

**Companion files (this folder):**

| File | Role in the pipeline |
|---|---|
| `n8n_core_workflow.json` | Importable n8n workflow, 109 nodes: brief → script → compliance → shot plan → keyframes → video → voice → lip-sync → assemble → QA → packaging → posts, plus Publisher, Review webhook and Error handler. Validated: JSON parses, all 108 connections resolve, all 26 Code nodes pass `node --check`, and the Code nodes ran end-to-end against mock data. |
| `workers/` | The runnable Python/FastAPI workers the workflow calls: `/voice/stitch`, `/assemble`, `/variants` (render), `/qa`, `/uniqueness/check`, `/compliance/scan`, `/package`. See `workers/README.md`; `make test`, `make sample`. |
| `schema.sql` | Supabase/Postgres schema: 28 tables, 11 RPC functions and 6 views (claiming, uniqueness, budget, bandit, winner labels, human queue, provider health). Applied twice cleanly and smoke-tested on Postgres 16. |
| `schema_growth.sql`, `n8n_growth_workflow.json`, `workers/growth/` | The organic growth engine (§7.5): metrics snapshots, baselines, velocity scores, winners, remix and boost queues, bandit arms, spend budgets, append-only ledger and governor decisions; the hourly/nightly n8n workflow (44 nodes) that drives them; the worker endpoints behind `/growth/*`. Tested on Postgres 16 and with 258 growth tests (569 in the workers suite), including property tests on the spend governor. |
| `prompts/01–08_*.md`, `prompts/blocked_claims.json` | The production LLM prompts (loader splits on `<<<SYSTEM>>>`, `<<<USER>>>` and `<<<END>>>`) and the machine-readable blocked-claims list, with a regex self-test of 11 block cases and 4 pass cases, all passing. |
| `CHARACTERS.md`, `SAFETY_RULES.md`, `EVIDENCE.md` (sibling deliverables) | Supply `{{CHARACTER_BIBLE}}`, `{{SAFETY_RULES_MD}}` and `{{EVIDENCE_INDEX}}`. SAFETY_RULES.md is authoritative wherever it and this file differ. |

All prices were verified on 2026-09-30 from the URLs in §11. Anything marked **[A]** is an assumption. Validate it in week 1.

---

## 0. The summary on one screen

- **Architecture:** n8n (self-hosted, queue mode) orchestrates everything. Supabase holds state (every provider call is a row, so cost and failure are queryable). Claude writes, judges, plans and QA's. Nano Banana makes reference-locked keyframes. Kling 3.0, Seedance 2.0, Wan and Veo make non-speaking shots, and **exercise motion always comes from a real performer's driving video** via Kling Motion Control. ElevenLabs v3 does voice, InfiniteTalk does lip-sync, and a Remotion/ffmpeg worker assembles captions, re-signs C2PA and exports QA frames. A deterministic QA worker (ArcFace, SyncNet, EBU R128, OCR) and a vision-LLM QA both gate. Official APIs publish where audited, upload-post everywhere else. The metrics loop feeds a Thompson-sampling bandit and auto-remixes winners.
- **Volume at 7 videos/page/day** (4/10/20 pages are sizing scenarios; the launch itself is the 3 day-1 pages on the §5.4 ramp, §5.1): 4 pages = 28 base videos/day → 168 posts/day. 10 pages = 70 → 420. 20 pages = 140 → 840.
- **Cost per base video (blended across formats):** Lean **$0.89**, Standard **$4.04**, Premium **$13.67**. The recommended routing (60/35/5) averages **$2.63**.
- **Monthly, all-in (variable + tools + people):** 4 pages **≈ $7.2K**, 10 pages **≈ $14.8K**, 20 pages **≈ $24.7K**. Tools only: $2.9K / $7.7K / $15.3K. See §4.
- **Top risks:**
  1. YouTube's July 2026 inauthentic-content policy explicitly discourages AI personas discussing health. Treat YT as a funnel, not revenue, and keep it movement- and food-led.
  2. Duplicate-content suppression across sibling pages, handled by the uniqueness guard in §2.3.
  3. Health-claim liability, handled by the two-pass compliance gate and a signed credentialed reviewer.
  4. Unaudited APIs publish private-only. Both TikTok and YouTube do this, so launch through upload-post.
  5. ManyChat cost scales per account and per contact (§4.3).

---

## 1. Architecture

### 1.1 Stage map

```
 SIGNALS                         CREATE                                   GATE                    SHIP                     LEARN
 ───────                         ──────                                   ────                    ────                     ─────
 own comments (Graph/TT/YT) ─┐
 competitor winners (Apify) ─┼─> W1 Idea Miner ─> ideas ─> W2 Planner ─> briefs (slots D+1)
 trends / audio (Apify)     ─┤    (Claude)        (risk tier)  (bandit)       │
 bandit stats (Supabase)    ─┘                                                ▼
                                   W3 CORE (n8n_core_workflow.json)
                                   script (Claude + bible) ─> regex pre-scan ─> Compliance Judge ──revise≤2──┐
                                        ▲                                         │pass            human/block─> review app
                                        └─────────────────────────────────────────┘
                                   shot plan ─> keyframes (Nano Banana, ref-locked)
                                     ├─ gen_scene ──────> Wan 2.2 / Kling 3.0 / Seedance 2.0
                                     ├─ motion_transfer ─> Kling Motion Control + performer driving video
                                     ├─ library_broll / graphic (free)
                                     └─ lipsync_talk ───> ElevenLabs v3 (timestamps) ─> InfiniteTalk
                                   assemble (Remotion/ffmpeg: captions, PiP, music, -14 LUFS, C2PA sign)
                                   QA: ArcFace + SyncNet + R128 + OCR + black/freeze  ⊕  Claude vision
                                     ├─ auto (pass, trusted page, green) ──┐
                                     ├─ approval (drafts) ─> human ────────┤
                                     ├─ regen (≤3) ─> requeue              │
                                     └─ human (fail×3)                     ▼
                                   packaging per platform (Claude) ─> compliance pass 2 ─> variant renders ─> posts
                                                                                                                  │
 W4 Publisher (official APIs / upload-post; caps, spacing, AI flags) <─────────────────────────────────────────────┘
 W5 Metrics (T+1h,6h,24h,72h,7d) ─> v_post_scores ─> W7 Winner/Remix ─> derivative briefs (other pages, part 2, localize)
 W6 Comments/DM (ManyChat or Private Replies; crisis keywords → human) ─> dm_leads ─> orders (UTM/pid attribution)
 W8 Localization (transcreate → re-voice → re-lip-sync talking shots only → re-caption)
 W9 Token refresher · W10 Ops (circuit breaker, budget caps, daily cost report)
```

### 1.2 Workflows (n8n)

| # | Workflow | Trigger | What it does | In JSON? |
|---|---|---|---|---|
| W1 | Idea Mining | 05:00 and 15:00 page-local | Pulls the last 72 h of own comments (official APIs) plus competitor comments and winners (Apify), then runs `01_idea_miner`. Writes `ideas` with risk tier. Green goes to auto, yellow to the operator slate, red is dropped. | Spec |
| W2 | Brief Planner | 04:00 daily | For D+1, fills `pages × daily slots` with briefs. Thompson-samples arms (cluster × render archetype × hook archetype × speaker) from `experiment_arms`: 70% exploit, 20% adjacent, 10% wild. Assigns the quality tier (§4.1) and staggers sibling derivatives by ≥ 48 h. | Spec |
| W3 | **Core Production** | every 2 min | Claims 1 brief (`FOR UPDATE SKIP LOCKED`) and runs the full chain to scheduled posts | **Yes** |
| W4 | **Publisher** | every 5 min | Claims due posts (respects spacing and account status), fetches the Vault token, publishes via the official API or upload-post, and records the result with 3× backoff retry | **Yes** |
| — | **Review webhook** | POST | Approve, reject or fix-request from the review app or Slack | **Yes** |
| — | **Error handler** | Error Trigger | Dead-letter queue, requeue the brief, Slack alert | **Yes** |
| W5 | Metrics Ingest | hourly | For posts at T+1h, 6h, 24h, 72h and 7d, pulls insights per platform (§7.1) into `metrics`, and rolls up keyword comments, DM opt-ins and revenue. The growth workflow then normalises captures into `post_metrics` at 1/3/6/24/72 h (§7.5) | **Yes** (`n8n_growth_workflow.json`, hourly chain) |
| W6 | Comments → DM | real-time webhooks + 10-min sweep | Keyword → DM (ManyChat, or Meta Private Replies in-house). Crisis and medical-emergency keywords go to human now plus the crisis-resource auto-reply (SAFETY_RULES §4.4) | Spec |
| W7 | Winner & Remix | hourly | Scores every post against its page baseline (`/growth/score`), applies §7.3 and §7.5 rules (`/growth/actions`), queues `remix_jobs` (priority 90) for other pages and `boost_queue` candidates for a human; the nightly chain runs the allocator (`/growth/allocate`) and the spend governor in dry run (`/growth/governor/plan`) and posts the plan to Slack for approval | **Yes** (`n8n_growth_workflow.json`) |
| W8 | Localization | on winner flag + daily quota | Runs `08_localization_adapter`, reuses non-speaking shots, re-voices and re-lip-syncs talking shots, re-captions | Spec |
| W9 | Token Refresher | every 6 h | IG/FB long-lived tokens (60 d), TikTok (24 h access / 365 d refresh), Google OAuth. Writes Supabase Vault | Spec |
| W10 | Ops | every 10 min + 07:00 report | Circuit breaker (`v_provider_health_30m` > 20% failure → fallback level +1), budget caps, stuck-job reaper (status `rendering` > 90 min → requeue), daily cost and yield report to Slack | Spec |

### 1.3 Model routing (verified Sept 2026 prices)

| Stage | Primary | Fallback 1 | Fallback 2 | Price basis |
|---|---|---|---|---|
| Idea mining, script, shot plan, variants | Claude Sonnet 5.5 | GPT-6.1-Sol | Claude Opus 5.5 | Sonnet $2 / $10 per MTok; Opus $4 / $20; Haiku 4.5 $1 / $5; batch −50%; cache read $0.20 |
| Compliance judge | Claude Opus 5.5 (temp 0) | Sonnet 5.5 for green, known templates | — | ~3k in / 1.5k out → ~$0.04 per script |
| Captions and packaging | Claude Haiku 4.5 | GPT-6-Luna ($0.10 / $0.50) | Sonnet | ~$0.01 per video |
| QA vision | Claude Sonnet 5.5 (12 frames + 3 refs) | Gemini Flash | — | ~$0.03–0.05 |
| Keyframes (reference-locked) | Nano Banana 2 (Gemini 3.1 Flash Image) | Nano Banana Pro | Higgsfield Soul (API) | NB2 $0.067 at 1K, $0.101 at 2K, $0.151 at 4K; **batch $0.034 at 1K**. NB Pro $120/M output tokens (≈ $0.13 at 2K **[A: derived]**) |
| Non-speaking scenes (props, food, cutaways) | Kling 3.0 Std i2v | Veo 3.1 Fast (liquids and physics) | Seedance 2.0 (premium, multi-ref) | Kling v3 Std $0.084/s (no audio); Veo 3.1 Fast $0.10/s (no audio), $0.15/s (audio); Seedance 2.0 Fast $0.24/s at 720p; Veo 3.1 $0.40/s |
| Exercise demos | **Kling 3.0 Motion Control** + performer driving video | Kling 2.6 Std MC (lean) | Wan 2.2 Animate (self-host) | v3 Pro $0.168/s; v3 Std ~$0.13/s; v2.6 Std $0.07/s; 3–30 s driving clip |
| Voice | ElevenLabs v3 (designed voices) | v4 (promo $0.022/1K chars until Oct 12) | Flash v2.5 | v3 $0.08 per 1K chars (API) |
| Lip-sync | InfiniteTalk (WaveSpeed) | InfiniteTalk self-host (lean) | OmniHuman 1.5 ($0.16/s) / HeyGen photo avatar (~$0.05/s **[A: third-party figure]**) | $0.03/s at 480p, $0.06/s at 720p, up to 10 min; 10–30 s compute per output second |
| Captions | Remotion (self-host; word timings from ElevenLabs) | ZapCap API ($0.10/min) | Submagic API (~$0.69/min) | ~$0 marginal |
| Assembly | Remotion + ffmpeg worker | Creatomate (~14 credits per 720p minute) | Shotstack | worker compute (§4.3) |
| Music | ElevenLabs Music, one-time library of 300 tracks | licensed library | — | $0.15/min → ~$45 one-time |
| Aggregator fallback | **Higgsfield API** (50+ models, 20 concurrent by default, failed requests not charged) | fal ↔ WaveSpeed swap | — | Kling 2.5 from ~$0.042/s |

Not used: the **Sora API** (shut down 2026-09-24).

### 1.4 Stage contracts (what each stage must output before the next may run)

| Stage | Output (table) | Hard gate |
|---|---|---|
| Idea | `ideas` (risk_tier, evidence_ids) | red is never briefed; `needs_new_evidence` goes to the reviewer |
| Brief | `briefs` (slot, tier, render archetype R1–R4, editorial F##, pillar P##, speaker) | budget cap per page per day (`budgets`) |
| Script | `scripts` (versioned by attempt) | JSON schema valid; `claims[].evidence_ids` present |
| Compliance 1 | `compliance_reviews` | regex block hit overrides LLM pass; confidence < 0.8 goes to human |
| Shot plan | `shots` | talking-head ≤ 40% hard (≤ 30% target, CHARACTERS §13.2); generated seconds ≤ tier cap; exercises only via `motion_transfer` |
| Media | `renders` (+ `assets`) | every job idempotent on `brief:shot:stage:attempt` |
| Master | `videos` + asset | 1080×1920, 30 fps, H.264 High, AAC 48 kHz, −14 LUFS, C2PA signed |
| QA | `videos.qa_*` | worst of deterministic and vision verdicts |
| Compliance 2 | (in core) | regex over captions, burned text and ASR transcript; required footer; `is_aigc` and `containsSyntheticMedia` true; no links on X |
| Posts | `variants`, `posts` | per-account `daily_post_target`; draft unless page trusted and QA pass and green |

---

## 2. Volume math & uniqueness

### 2.1 Posts and base videos

Let **P** = pages, **N** = videos per page per day (6–9). Video platforms = IG, TikTok, YT, FB (4). Text-native platforms = Threads and X (2), which get text posts derived from the day's scripts, with 2–3 attaching the video.

| | 4 pages | 10 pages | 20 pages |
|---|---|---|---|
| Posts/day at N = 7 (P × 6 × N) | 168 | 420 | 840 |
| Posts/day at N = 9 | 216 | 540 | 1,080 |
| **Unique base videos/day** at N = 7 (P × N) | **28** | **70** | **140** |
| Base videos/month (N = 7) | 840 | 2,100 | 4,200 |
| Platform variant renders/day (≈ 4–5 per base, assembler only, ~$0.01 each) | 126 | 315 | 630 |
| Distinct **ideas** needed/day (each idea feeds ~2.2 scripts: 1 origin + sibling adaptations or a part 2) | ~13 | ~32 | ~64 |
| Ideas the miner must generate/day (1.5× for selection) | ~20 | ~48 | ~95 |
| Human spot-checks/day (all drafts on untrusted pages; 20% sample + flags on trusted) | ~28 (all, weeks 1–2) → ~9 | ~25 | ~45 |

**Why a base video can go to 4 platforms on the same page but never to 2 pages:** cross-posting your own original work to your own accounts on different platforms is normal publisher behavior. Instagram's 2026 aggregator penalty targets reposting others' content without "significant changes" ([Tubefilter](https://www.tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator/)). The platforms we can't fool, and shouldn't try to, are the ones that see **the same file or near-identical content on several accounts of one network**. So the unit of uniqueness is **(platform, page)**. The platform packaging still differs per platform (hook text, cover, caption, trim) so each post is native, and **no watermark from another platform ever appears**, because we render from the master.

### 2.2 Frequency: what to actually run per platform (per page)

The system supports 9/day everywhere. Reach per post isn't linear, so the per-account `daily_post_target` ramps (§5.4) and settles here:

| Platform | Steady-state target | Why | Official cap |
|---|---|---|---|
| TikTok | 6–9 | FYP tests each post on its own; volume works if hooks vary | 6 req/min per token + a per-creator daily cap returned by the API |
| FB Reels | 6–9 | Distribution rewards volume; older audience is here | 30 API reels / 24 h / Page |
| YT Shorts | 3–6 | The inauthentic-content policy targets templated volume; quality over count | 100 `videos.insert` per **project** per day → shard GCP projects |
| IG Reels | 3–4 main feed + 2–5 **Trial Reels** | Trial Reels go only to non-followers, which is a native test lane that doesn't fatigue followers | 100 API posts / 24 h |
| Threads | 6–9 text-native (2–3 with video) | Cheap, conversational; Sun Yoon wins here | 250 / 24 h |
| X | 6–9 text-native, **no links in body** | $0.015 per post vs $0.20 with a URL; links depress reach | pay-per-use |

### 2.3 Uniqueness strategy (legitimate, not evasion)

The aim is that a human editor would call two posts "different videos". We are not trying to trick hash matchers. That is also exactly what keeps us clear of "unoriginal", "reused" and "inauthentic" classifiers.

**Uniqueness levels**

| Level | What changes | Allowed use |
|---|---|---|
| L0 identical file | nothing | **Never** on two accounts |
| L1 packaging variant | hook text, cover, caption, hashtags, trim, safe-zone layout | Same page, different platforms (standard cross-posting) |
| L2 edit variant | L1 + reordered B-roll + new music + new CTA card | Same page, re-post of an evergreen winner ≥ 60 days later |
| L3 derivative | **new script** (≥ 4 of 6 axes changed, `05_variant_generator`), new keyframes, new voice, new renders; same evidence | Sibling pages, staggered ≥ 48 h |
| L4 new idea | everything | anywhere |

**Automated guards (all in `schema.sql` or the core workflow)**
1. **Semantic:** each script is embedded (1024-d) and `script_similarity()` rejects cosine > 0.86 vs the same page's last 90 days, or > 0.80 vs any other page's last 14 days.
2. **Lexical:** trigram index on `scripts.full_text`. `05_variant_generator` forbids > 6 consecutive shared words (safety lines excepted).
3. **Visual:** the assembler writes a per-second pHash sequence. Two posts on the same platform, on different pages, are blocked if > 40% of seconds are within Hamming distance ≤ 10.
4. **Audio:** Chromaprint fingerprint. Block the same voice track on two pages.
5. **Page DNA:** every page has a fixed, distinct set of sets and wardrobe codes, camera style, caption style, hook-archetype mix, music palette and CTA keywords (CHARACTERS.md §6, set codes). So even the same idea looks and sounds different.
6. **Stagger:** sibling derivatives land ≥ 48 h apart and never in the same slot hour.
7. **Disclosure is consistent across the network:** every page states it's part of the same studio (link to the same site, "Who makes this" page). An **openly affiliated network of branded pages** is normal media-publisher behavior. What Meta's inauthentic-behavior policy prohibits is deception about identity or purpose and artificially boosting distribution ([Meta policy](https://transparency.meta.com/policies/community-standards/inauthentic-behavior/)). We do neither.

---

## 3. Formats & shot economics (what we actually render)

Render archetypes (R1–R4) drive model routing. The editorial formats F## and pillars P## come from CHARACTERS.md and ride along in `briefs`.

| Archetype | Typical length | Talk (lip-sync) | Generated scene | Motion transfer | Library + graphics | Share of mix |
|---|---|---|---|---|---|---|
| R1 Talk + prop/test ("Can you do this?", study card) | 35 s | 10 s | 10 s | 0 | 15 s | 3/7 |
| R2 Prop/food demo (kitchen, Sun's ferments, post-meal walk) | 35 s | 8 s | 18 s | 0 | 9 s | 2/7 |
| R3 Motion exercise (wall sit, floor rise, grip, balance) | 35 s | 6 s | 0 | 20 s | 9 s | 1/7 |
| R4 Duo dialogue (Chang & Sun bits) | 40 s | 24 s (multi-speaker) | 8 s | 0 | 8 s | 1/7 |

**Library leverage:** pre-render once, reuse forever, and track per-page usage so no clip repeats on a page within 30 days.
- ~300 Chang and Sun "action" clips (walking, carrying groceries, garage lifts, kitchen). About $250 one-time at standard tier.
- ~150 food and hand macros.
- ~80 graphic templates (study card, timer, test scorecard).

This is why the lean tier works: 25–45% of every video is free library or graphics.

**Driving-video library (the safety moat):** one 4-hour shoot with a real 60+ performer (signed release, form [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: reviewed by the signed PT] FALLBACK: "checked by our team against published exercise guidance") yields 150–250 clips of 3–30 s: every exercise, regression and progression, and front / 45° / side angles. Kling Motion Control maps that exact, verified movement onto Chang. We never let a generative model *invent* an exercise.

---

## 4. Costs

### 4.1 Per-video cost at 3 quality tiers

Overgeneration factors (rejects and retakes) are included: Lean 1.3×, Standard 1.5×, Premium 2.0×. Voice takes: 2 / 3 / 4.

| Tier | Keyframes | Lip-sync | Scenes / motion | Voice | LLM + QA + assembly |
|---|---|---|---|---|---|
| **Lean** | NB2 batch 1K $0.034 | InfiniteTalk **self-hosted** on serverless H100 ≈ $0.008/s **[A: ~$2.50/GPU-h, ~10 s compute per output second]** | Wan 2.2 self-host ≈ $0.025/s **[A]**; Kling 2.6 MC $0.07/s → blended $0.03/s | $0.04/1K chars | $0.10 |
| **Standard** | NB2 2K $0.101 | InfiniteTalk 720p $0.06/s | Kling v3 Std / Veo 3.1 Fast ≈ $0.095/s; Kling v3 MC $0.13/s | $0.08/1K | $0.25 |
| **Premium** | NB Pro 2K ≈ $0.134 | OmniHuman 1.5 $0.16/s | Seedance 2.0 / Veo 3.1 ≈ $0.35/s; Kling v3 Pro MC $0.168/s | $0.08/1K | $0.56 |

| Tier | R1 Talk + prop | R2 Food/prop demo | R3 Motion exercise | R4 Duo | **Blended (3:2:1:1)** |
|---|---|---|---|---|---|
| Lean | $0.75 | $1.03 | $1.11 | $0.84 | **$0.89** |
| Standard | $3.31 | $4.41 | $5.25 | $4.31 | **$4.04** |
| Premium | $12.00 | $17.21 | $10.14 | $15.12 | **$13.67** |

**Routing policy (the lever that matters):**
- Every new, unproven idea renders **Lean** (a test).
- Formats with a proven hook and topic on that page render **Standard**.
- The top 5% (breakouts and their remixes, paid-ad candidates, and each page's pinned "Hi, we're AI" posts) render **Premium**.

Recommended mix 60/35/5 = **$2.63 per base video**. Localized versions reuse non-speaking shots: Lean ≈ $0.28, Standard ≈ $1.35 per localized video.

### 4.2 Monthly variable (generation) cost

| Base videos/month | Lean | Standard | Premium | **Recommended mix** |
|---|---|---|---|---|
| 4 pages (840) | $750 | $3,395 | $11,482 | **$2,212** |
| 10 pages (2,100) | $1,874 | $8,488 | $28,706 | **$5,531** |
| 20 pages (4,200) | $3,748 | $16,977 | $57,412 | **$11,061** |

### 4.3 Monthly fixed tools

| Item | 4 pages | 10 pages | 20 pages | Basis |
|---|---|---|---|---|
| n8n self-hosted (queue mode, Redis, 3–6 workers) | $40 | $80 | $160 | VPS **[A]**. n8n Cloud Pro (€50) caps at 10K executions/mo, and the two ticks alone generate about 30K. |
| Render + QA workers (ffmpeg/Remotion CPU; ArcFace/SyncNet serverless GPU) | $80 | $180 | $350 | **[A]** |
| Supabase Pro + compute | $35 | $60 | $135 | $25 Pro + compute add-on |
| Cloudflare R2 (90-day retention; intermediates purged at 7 days) | $5 | $10 | $20 | $0.015/GB-mo, zero egress |
| ManyChat (per IG/FB account) | $276 (4 × Business $69) | $1,390 (10 × Advanced $139) | $2,780 (20 × $139) + contact overage | per-account plans |
| upload-post | $33 (25 profiles) | $33 | $118 (75 profiles) | |
| X API (pay-per-use, text posts) | $16 | $41 | $81 | $0.015/post |
| Apify (competitor comments and trends) | $49 | $99 | $199 | $1.70–2.30 per 1K results |
| Fallback provider wallet (Higgsfield / HeyGen) | $100 | $200 | $300 | budget |
| Monitoring, Slack, 1Password, domain | $50 | $75 | $100 | |
| **Tools subtotal** | **$684** | **$2,168** | **$4,243** | |
| Tools subtotal with the **in-house DM bot** (Meta Private Replies API via n8n instead of ManyChat) | $408 | $778 | $1,463 | build ~3 days in week 3 |

Voice is billed at API rates inside the per-video cost. Buy the ElevenLabs plan whose credits match usage (Pro $99 → Scale $299 → Business $990), and the plan's effective rate is ≤ the API rate. Claude usage is also inside the per-video cost. With prompt caching on the bible and evidence blocks, the LLM share is about 5–10% of the total.

### 4.4 All-in monthly

| | 4 pages | 10 pages | 20 pages |
|---|---|---|---|
| Generation (recommended mix) | $2,212 | $5,531 | $11,061 |
| Tools | $684 | $2,168 | $4,243 |
| People: VAs at $1.8K each **[A]** | 1 VA: $1,800 | 2 VAs: $3,600 | 3 VAs: $5,400 |
| Credentialed reviewer retainer (PT/DPT + RD) **[A]** | $2,500 | $3,000 | $3,500 |
| Performer refresh shoots | $0 | $500 | $500 |
| **Total** | **≈ $7.2K** | **≈ $14.8K** | **≈ $24.7K** |
| Cost per published post (tools + generation) | $0.57 | $0.61 | $0.61 |

The operator (Garrison or a content lead) isn't costed. One-time setup: performer shoot $1.5–3K, reference-pack and voice design about $300, library pre-render about $450, cultural consultants (CHARACTERS §14) about $1–2K.

### 4.5 Render time, concurrency, throughput

| Step | Typical latency | Notes |
|---|---|---|
| Script + judge + plan (3 Claude calls) | 40–90 s | Revise loop adds about 40 s per pass |
| Keyframes (3–5 in parallel) | 20–60 s | NB Pro via AI Studio ~35 s ([OpenRouter latency](https://openrouter.ai/google/gemini-3-pro-image)) |
| Scenes / motion (2–4 jobs in parallel) | 2–8 min | queue-dependent **[A]** |
| Voice (7–12 lines) | 10–30 s | |
| Lip-sync (10–24 s of talk) | 3–12 min | 10–30 s compute per output second ([WaveSpeed](https://wavespeed.ai/docs/docs-api/wavespeed-ai/infinitetalk)) |
| Assemble + variants | 1–3 min | Remotion Lambda cuts this to under 1 min |
| QA (deterministic + vision) | 40–90 s | |
| **End-to-end per video** | **p50 ≈ 18 min, p95 ≈ 45 min** | |

- **Production window:** the planner writes D+1 briefs at 04:00, and core runs continuously. At 20 pages that's 140 videos/day ≈ 840 provider jobs. With 20–30 concurrent provider jobs, that clears in 3–5 h of wall-clock time, leaving a full day of buffer for human approvals and regen.
- **n8n:** Wait nodes over 65 s offload executions to the database, so 30+ in-flight videos cost nothing while waiting. Run queue mode with 3 workers × concurrency 10.
- **Provider concurrency:** Higgsfield starts at 20 concurrent per key. Confirm fal and WaveSpeed account limits and request increases **before 10 pages**. At 10+ pages, switch polling to provider **webhooks** (fal `?fal_webhook=`) resumed by Wait-on-webhook to cut executions.

### 4.6 Failure & retry handling

| Failure | Detection | Automatic action | Escalation |
|---|---|---|---|
| Provider 5xx or timeout on submit or poll | HTTP node retry (3×, 5 s) | Node-level retry | Error workflow → `job_failures` → requeue brief (max 3) |
| Job FAILED or poll timeout (`$runIndex` > max) | Check node throws | `log_failure` requeues with priority +10 | 3rd failure → brief `failed` + Slack |
| Provider degraded | `v_provider_health_30m` failure rate > 20% | W10 sets `fallback_level` → Build nodes switch model map (fal ↔ WaveSpeed ↔ Higgsfield) | Slack; auto-revert after 60 min healthy |
| LLM returns bad JSON | parse throws | requeue (the next attempt usually passes) | 3× → human |
| Compliance `revise` | verdict | loop to writer with numbered feedback (≤ 2) | → human queue |
| QA fail (identity, anatomy, caption number) | QA route | `requeue_brief` with `rerender_shots`, so only the broken shots re-render **[A: worker honors it]** | 3× → failed |
| Budget cap hit | `claim_next_brief` returns `budget_cap` | skip the page for the day | Slack daily report |
| Publish error | `onError: continue` → `mark_post_result` | reschedule +15 min, max 3 | `failed` → VA posts manually |
| Stuck execution | W10 reaper: `rendering` > 90 min | requeue | — |
| Idempotency | `renders.unique(idempotency_key)`, `posts.unique(platform, external_post_id)` | no double spend, no double post | — |

---

## 5. Account operations

### 5.1 Structure (legitimate multi-page operation)

1. **One legal entity and one verified Meta Business Portfolio.** Business verification also unlocks Advanced Access later.
2. **Each page = one editorial brand:** a FB Page plus an IG professional account (Business or Creator), and TikTok, YouTube, Threads and X accounts under the same name. Roll out per CONTENT_SYSTEM.md §8.1 (canonical): day 1 `@changyin` (flagship), `@sunyoon.kitchen`, `@changandsun`; day 15 `@changyin.strength`, `@changyin.mobility`; day 22 `@sunyoon`; day 30 `@changyin.espanol` (Mode A Spanish pilot at 3/day). Every new account then follows the §5.4 ramp. Scale to 20+ with **genuinely different editorial scopes** (e.g., balance and falls, grip and hands, sleep and breath, walking, bone health for women, Spanish, Portuguese, German). Never clone a page just to add volume.
3. **Logins:** every account gets a unique company-domain email alias (`ig.changyin@studio.com`) and **authenticator-app 2FA** with recovery codes in 1Password. The IG app allows up to 5 simultaneous logins per device ([Stackinfluence](https://stackinfluence.com/blog/how-many-instagram-accounts-can-i-have-tips)). **VAs work through Business Suite roles, not shared passwords.**
4. **Accounts Center:** link each IG account to its FB Page and group them under the company. That is truthful common ownership, and it's what you want Meta to see.
5. **No proxies, anti-detect browsers or device farms.** Those tools exist to make one operator look like many unrelated people. That is the exact signal "coordinated inauthentic behavior" enforcement looks for, and it contradicts our "openly one studio" position.

### 5.2 AI labels & provenance (per platform)

| Platform | Account-level | Post-level | How the pipeline enforces it |
|---|---|---|---|
| Instagram | **"AI-generated profile" label** (required for AI-person accounts; unlabeled accounts lose reach) ([TechCrunch](https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/)) | "AI info" label, auto-applied from C2PA/SynthID; manual in-app toggle | `page_accounts.ai_profile_label` must be true and `ai_label_verified_at` set before status `active`. The C2PA manifest is re-signed on every master. The VA verifies the first 10 posts show "AI info". |
| Facebook | Page transparency: bio plus "AI character" in the About section | AI info (C2PA) | same as IG |
| TikTok | Bio disclosure (SAFETY_RULES §7) | `is_aigc: true` on **every** post via the Content Posting API ([TikTok ref](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)) | Compliance pass 2 rejects packaging without `is_aigc` |
| YouTube | Channel About plus a pinned "Hi, we're AI" Short | `status.containsSyntheticMedia: true` on upload ([YouTube API](https://developers.google.com/youtube/v3/docs/videos)) | set in the YT upload node; pass 2 check |
| Threads / X | Bio disclosure | none required; the text says "Sun here" in character; the bio covers disclosure | pass 2 forbids "I'm a real…" claims |

**C2PA preservation:** Google image and video outputs carry SynthID (in-pixel, survives edits). **Our ffmpeg/Remotion re-encode strips C2PA manifests**, so the assembler re-signs the final master and every platform variant with `c2patool` (digitalSourceType `trainedAlgorithmicMedia`). Deterministic QA checks `c2pa_present`. Being openly AI is the strategy, so we *want* the auto-label.

### 5.3 Publishing paths (official vs scheduler)

| Platform | Official path | Gate before public posting | Launch path (days 1–30) |
|---|---|---|---|
| Instagram | Graph API content publishing (REELS container → publish; `trial_params` for Trial Reels) | **Standard Access is enough for accounts you own or manage** (no App Review) ([Meta](https://developers.facebook.com/docs/instagram-platform/overview)) | **Official from day 1** |
| Facebook Reels | `/{page_id}/video_reels` (30 per 24 h, 3–90 s) | Standard Access for own Pages | upload-post, then official in week 3 |
| Threads | Threads API (250 per 24 h) | same | upload-post, then official |
| TikTok | Content Posting API, Direct Post, `PULL_FROM_URL` (verify the R2 domain) | **Unaudited clients post private-only**, so you must pass the audit | **upload-post** until the audit passes (submit on day 1) |
| YouTube | Data API `videos.insert` (resumable) | **Unverified projects created after 28 Jul 2020 upload private-only**, so you must pass the audit ([docs](https://developers.google.com/youtube/v3/docs/videos/insert)). Default quota is 100 uploads per project per day. Set the OAuth app to *In production*, because *Testing* refresh tokens expire in 7 days. | **upload-post** until the audit passes |
| X | API v2 pay-per-use | credits prepaid | official (cheap) |

The `page_accounts.publisher` field flips each account from `upload_post` to `official` without touching the workflow. The Publisher's Switch routes by it.

### 5.4 Warm-up & ramp (per account)

| Week | Posts/day | Rules |
|---|---|---|
| 0 (setup) | 0 → 3 pinned | Complete profile, AI label, bio disclosure, link-in-bio. Post the 3 pinned posts (CHARACTERS §9.2: "Hi, we're AI…") **natively in-app**. Follow 10–20 relevant accounts manually. No automation yet. |
| 1 | 1–2 | API posting starts. A human replies to comments for the first 60 min on each post. Everything is draft plus approval. |
| 2 | 3 | IG: add 1 Trial Reel/day. Check reach per post is stable. |
| 3 | 5–6 | Raise only if there are no restrictions or strikes and the median views/post fell < 30% week over week |
| 4+ | 6–9 (§2.2 caps) | `auto_publish` turns on after **14 clean days** (no strikes, QA approval rate ≥ 90%, human edits ≤ 10%) |

### 5.5 What gets pages restricted, and the control for each

| Risk | Consequence | Control in this system |
|---|---|---|
| Undisclosed AI person (IG) | Reach cut (Reels, Explore, suggested) | Label is a hard precondition for `active` |
| Unlabeled realistic AI (TikTok) | FYP exclusion and strikes | `is_aigc` always true; C2PA signed |
| Same or near-same video on several accounts | "Unoriginal" or aggregator demotion; network-level suspicion | L3+ uniqueness, pHash/Chromaprint/embedding guards, 48 h stagger |
| Templated mass production on YouTube; AI persona giving health advice | YPP demonetization ([TechCrunch](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/)) | Don't depend on YPP. YT content leans on movement, food and story arcs rather than medical topics, with more narrative variety (`05` structures) |
| Health misinformation | Removal, strikes, ad account bans | Two-pass compliance, EVIDENCE IDs, blocked claims, human review for sensitive topics |
| Fake engagement (bought followers, pods, sibling pages boosting each other) | CIB takedown | **Prohibited.** Sibling pages may collab openly (Collab posts), never mass-like or comment-farm. |
| Comment-to-DM spam | DM feature restrictions | One DM per keyword comment; Meta 24 h window; no unsolicited cold DMs; opt-out honored |
| Links in comments, link-spam | Reach cut | Links only in bio and in DMs |
| Burst posting at identical minutes across pages | Automation flag **[A]** | ±9 min deterministic jitter, per-platform offsets, `min_spacing_minutes` |
| Token or credential sharing | Checkpoints, lockouts | Business Suite roles, Vault tokens, no password sharing |
| Music copyright | Muted or removed | Our own generated or licensed library only |
| Fabricated testimonials or reviews | FTC civil penalties (16 CFR 465) | Blocked claim BC09; no reviews in content |

### 5.6 Backup & redundancy

- **Owned audience first:** every DM flow asks for email (and SMS with consent, once 10DLC / toll-free verification clears; that takes 3–6 weeks, so launch captures email + DM only) → ESP. A page loss must never mean an audience loss.
- **Publishing redundancy:** official API ↔ upload-post ↔ manual VA posting from the review app, which exposes the file and caption.
- **Provider redundancy:** fal ↔ WaveSpeed ↔ Higgsfield ↔ self-host, switched automatically by the circuit breaker.
- **Data:** Supabase daily backups plus weekly `pg_dump` to R2. Masters are kept 12 months (cheap on R2).
- **Access:** 2 human admins per account, recovery codes in 1Password, and Meta Verified for Business on the flagship page for support access **[A: evaluate cost]**.
- **Never** pre-warm "spare" accounts to replace banned ones. That's ban evasion and it puts the whole network at risk. Appeal instead, and rely on the owned list.

---

## 6. Human roles

| Role | Daily time | Responsibilities |
|---|---|---|
| **Operator** (Garrison or content lead) | 45–75 min | 07:30: approve the yellow idea slate (10 min, one tap each). 10:00: clear the escalations queue (compliance `human`, QA fail ×3, crisis DMs). Weekly review (Monday, 60 min). Owns thresholds, the page roster and offers. |
| **VA 1: Content QA** | 3–4 h (4 pages) → 2 VAs at 20 pages | Clears the approval queue at **10:00 and 16:00** (SLA ≤ 6 business hours, because production runs D−1). Each review takes 45–90 s: watch at 1×, check the face, hands, captions and numbers, and the safety line. Samples 20% of auto-published posts. Labels 100 renders in week 1 for threshold calibration. Checks AI labels on new accounts. |
| **VA 2: Community & DMs** | 3–4 h | Replies in the first hour on top posts (as the page, in the page voice, never pretending to be human). Handles DM escalations. Runs the crisis protocol (SAFETY_RULES §4.4). Tags good comments as ideas (`comments.used_in_idea_id`). Manual posting fallback. |
| **Credentialed reviewer** (PT/DPT + RD, retainer) | 3–4 h/week | Approves new evidence IDs and new exercise families. Reviews `human` compliance items (supplements, pelvic health, cardiac and medication topics). Monthly evidence refresh (EVIDENCE.md protocol). Signs the "reviewed by" claim. **No reviewer means no "reviewed by" wording** (SAFETY_RULES §7). |
| **Performer** | 4 h/quarter | Driving-video shoots for new exercise families and regressions |

**Approval SLAs**

| Item | Who | SLA |
|---|---|---|
| Yellow ideas | Operator | same morning (unapproved ideas expire in 48 h) |
| Compliance `human` | Operator, or the reviewer for clinical topics | 24 h |
| Draft videos (untrusted pages, QA `review`) | VA 1 | ≤ 6 business hours |
| Crisis-flag comment or DM | VA 2 | **15 min** during staffed hours; auto-reply with resources is instant |
| Publish failures | VA 2 | same day |

**Weekly review (Monday, 60 min):** (1) per-page scorecard: median views, PI distribution, keyword rate, DM → opt-in, trial starts per 1K views, MRR attributed. (2) Top 10 winners and bottom 10 duds with hypotheses. (3) Bandit arm movements and any arms to kill. (4) QA stats: first-pass yield, regen rate, cost per shipped video. (5) Compliance: revise and block rates, new evidence requests. (6) Account health: restrictions, label checks, token expiries. (7) Decide next week's ramp targets and page launches.

---

## 7. Analytics & feedback loop

### 7.1 Metrics per post (and where they come from)

| Metric | IG | FB | TikTok | YouTube | Threads | X | Use |
|---|---|---|---|---|---|---|---|
| Views / plays | `views` | `fb_reels_total_plays` | `view_count` | `views` | `views` | `impression_count` | PI |
| 3 s hold / swipe-away | app only; proxy = avg watch ÷ duration | retention graph where exposed | Business API retention where available **[A]** | `audienceWatchRatio` at the ~10% ratio | — | — | hook quality |
| Avg watch % | `ig_reels_avg_watch_time` ÷ duration | `post_video_avg_time_watched` | `average_time_watched` (Business API) | `averageViewPercentage` | — | — | body quality |
| Shares, saves | `shares`, `saved` | `shares` | `share_count` | `shares` | `reposts`, `quotes` | `retweet_count`, `bookmark_count` | value signal |
| Comments / keyword comments | comments + keyword regex | same | same | — | `replies` | `reply_count` | funnel entry |
| Keyword DMs → opt-ins | ManyChat or own bot | same | (not US comment triggers) | — | — | — | conversion |
| Link clicks | UTM (bio and DM links) | UTM | UTM | UTM | UTM | UTM | conversion |
| Attributed revenue | `orders.attributed_post_id` | | | | | | $ / 1K views |

VA 1 captures app-only metrics (e.g., IG skip rate) weekly for the top 20 posts only.

**Attribution chain:** keyword comment → DM contains `https://site/…?utm_source=ig&utm_medium=organic_short&utm_campaign=<page>&utm_content=<brief8>-ig&pid=<post_id>`. The landing page stores `pid` in a first-party cookie and passes it to checkout metadata (Shopify note attributes / Stripe `metadata.pid`). The order webhook sets `orders.attributed_post_id`, and `metrics.revenue_usd` rolls up. Per-page coupon codes back this up for view-through.

### 7.2 Winner thresholds (implemented in `v_post_scores`)

Baselines are per page × platform, trailing 14 days, measured at ≥ 20 h:
- **PI** (performance index) = views₂₄ₕ ÷ page median views₂₄ₕ
- **Breakout:** PI ≥ 5 **or** ≥ 500K views
- **Winner:** PI ≥ 2 **and** (shares + saves)/views ≥ page P75 **or** keyword rate ≥ page P75
- **Converter:** funnel RPM ≥ 2× page median, whatever the views
- **Dud:** PI < 0.5
- **Bandit reward** (`bandit_update`): breakout 1.0, winner 0.85, converter 0.8, average 0.5, dud 0.0. The reward attaches to the arm (cluster × archetype × hook × speaker).

### 7.3 Auto-remix rules (W7)

| Trigger | Action (within 24 h) |
|---|---|
| **Winner** on page A / platform X | (1) Same-page **part 2** answering the top question comment (L3, post in 3–5 days). (2) **Sibling adaptations** for the 2 best-fit pages (L3, ≥ 48 h stagger, page DNA). (3) Hook added to `hook_library` (+1 win). (4) Topic arm posterior updated. |
| **Breakout** | Everything above, plus **premium re-render** of the idea for page A's other platforms where it wasn't the winner, **localization priority** (ES first), a long-form YouTube expansion brief (5–8 min, stitched from a real script), and a flag as a **paid-amplification candidate** (Spark Ads / Partnership ads, keeping the AI label) |
| **Converter** | 3 CTA and offer variants of the same video (L2, same page, 30+ days later), plus an offer-page test note |
| High hold proxy, low avg watch | Keep the hook and rewrite the body shorter (−25% words) |
| Low hold proxy, high completion | Keep the body; new hook archetype plus a new first frame |
| 5 consecutive duds in a cluster on a page | Cluster **cooldown 21 days** on that page |
| Winner older than 60 days (evergreen) | L2 re-post on the same page (new cover, hook text and music) |

### 7.4 North-star and guardrail metrics

- **North star:** MRR attributed per 1,000 views, per page.
- **Guardrails:** compliance block rate < 3%, human-edit rate < 10%, QA first-pass yield > 80%, cost per shipped video within ±15% of plan, zero platform strikes.

### 7.5 Organic growth engine (`workers/growth/`, `schema_growth.sql`, `n8n_growth_workflow.json`)

Organic first: pages post for the runway, the engine learns what works per page and platform, and paid money only ever amplifies a proven organic winner or retargets engaged viewers, under hard caps, after a human approves. Cold prospecting is locked behind the BLITZ.md §11 gates. Nothing in the engine publishes, spends or fakes engagement: every output is a queued job, a slot plan or a decision record. All thresholds live in `workers/growth/config.py` (`GET /growth/config` shows the effective values); a JSON file at `GROWTH_CONFIG_PATH` overrides them, and a request may pass `config_overrides` for what-ifs. The exploration floor (20%) and the env-only safety switches can't be lowered by a request.

**1. Metrics snapshots** (`/growth/metrics/normalize`, hourly). One adapter per platform (IG and FB Graph insights, TikTok, YouTube Analytics, Threads, X; `growth/adapters.register()` adds an X/Grok adapter later) turns raw payloads into one capture shape: views, reach, likes, comments, shares, saves, profile visits, link clicks, follows, avg watch %. Counters a platform doesn't expose are listed as `missing`, never faked as 0. Captures are de-duplicated (60 s), clock-skew clamped (15 min), future and ancient captures dropped, counters kept monotone, and picked into the horizons **1 h / 3 h / 6 h / 24 h / 72 h** (windows ×0.75–1.5; log-time interpolation when two captures bracket a horizon within ×3, flagged `interpolated`). DB rollups ride along: keyword comments, waitlist opt-ins (`dm_leads`), ebook buyers (one-time `orders.attributed_post_id`) and members (subscription orders). Live API pulls exist (`/growth/metrics/fetch`) but are off unless `GROWTH_LIVE_METRICS=1`, https-only, on the `METRICS_ALLOWED_HOSTS` allow-list, public IPs only, no redirects, 2 MB cap, token in the header only.

**2. Baselines and velocity scores** (`/growth/baselines`, `/growth/score`). Per page × platform × horizon, the last 30 posts give a robust centre (median) and spread (MAD × 1.4826) for six log-scale components: views, share rate, save rate, keyword-comment rate, profile→link click-through, and conversions per 1K views (opt-ins + 4 × buyers + 10 × members). Empirical-Bayes shrinkage pulls a young page toward the network prior (same platform, ≥ 10 posts) or, before that, a cold-start prior (8 pseudo-posts), so a page with zero history still scores. Rates are beta-smoothed with 200 pseudo-views, and skipped below 50 views. Score = weighted z (views 0.35, shares 0.15, saves 0.15, keyword comments 0.15, click-through 0.05, conversions 0.15), clipped at ±4. Classes on the latest horizon: **WINNER** score ≥ 1.5 at ≥ 6 h with ≥ 1,000 views and ≥ 2 components, or a breakout (≥ 500K views at ≥ 3 h); **PROMISING** ≥ 0.75 at ≥ 1 h; **LOSER** ≤ −1.0 at ≥ 24 h; **NORMAL** otherwise. The bandit reward is 0.6 × Φ(score/1.5) + 0.4 × conversion saturation (targets 2 opt-ins, 0.5 buyers, 0.2 members per 1K views); no conversion data earns no conversion credit.

**3. Winner actions as queued jobs** (`/growth/actions`). A WINNER queues (a) up to 3 **remix jobs** for other active, same-language pages (priority 90, ≥ 48 h stagger, never the source's slot hour, 1 per target page per day): same proven grammar with a new hook, a different set, a different speaker pairing where the page allows, a new opening frame, new captions and a fresh voice render; each job carries the uniqueness thresholds it must pass at `/uniqueness/check` plus `/compliance/scan` and the judge. YouTube sources get one remix, a 0.70 text threshold, ≤ 4 shared words and a distinct first frame (July 2026 inauthentic / mass-produced policy). (b) A **boost candidate** (Meta partnership ad / TikTok Spark, AI label kept) re-checked under the stricter ad policy: no "you + age/health/body" targeting, no before/after, no disease, blood-pressure or fall-prevention claims, no instant/miracle, no fear imagery, no credential for the AI characters, AI disclosure present, recurring terms next to any price; then the organic scanner and the **mandatory LLM judge**. Pass → `awaiting_human_approval`; any flag → `flagged_human`; judge unavailable → `needs_human`. Nothing here approves. (c) A **pin / feature / highlight suggestion**. A LOSER emits a **down-weight** (reward 0, ×0.8) for the allocator.

**4. Content allocator** (`/growth/allocate`, nightly for D+1). Thompson sampling over pillar × hook grammar × editorial format × speaker × length bucket per page and platform (only CONTENT_SYSTEM §1 pillar→format pairs, the page's speakers, DUO for the duo-only formats, no LAUNCH grammar, Threads/X text formats short only). Each arm is Beta(1 + successes, 1 + failures) with rewards decayed by a 14-day half-life, 20 neutral pseudo-observations centred on 0.5 (a baseline post) and up to 8 borrowed from its factor marginals. Exploit slots (80%) draw first among arms with direct evidence that aren't below baseline, then among arms sharing ≥ 3 factors with observed ones, then the rest; **explore slots (≥ 20%, hard floor)** go to the least-observed arms, proven grammars first. Constraints: cadence ≤ 9, ≤ 2 per pillar per day (relaxed only when the page runs fewer pillars than slots), no adjacent slots with the same grammar, no (pillar, grammar, format) repeat inside the page's recent window, running bits ≥ 1 per duo video and ≥ 1 per 3 solo videos with a 6-bit cooldown. Output is tomorrow's slot plan (hour, pillar, grammar, format, speaker, length range, render archetype, bit) for `tools/build_content.py`, inserted as queued briefs. Deterministic for a seed.

**5. Spend governor** (`/growth/governor/plan`, nightly; `/growth/governor/execute`). A pure function from state to an action plan, plus an append-only hash-chained audit log (`GET /growth/governor/audit`) and the `governor_decisions` table. Defaults: `SPEND_ENABLED=0`, `GROWTH_DRY_RUN=1`. Inputs: an **approved budget record** (named human, daily cap, monthly cap, cash floor, price $25/$30, expiry), cash (balance, spent today/month, 180-day line), current cold/retarget spend, daily paid media and paid net new members, 14-day refunds, 30-day chargebacks, renewal 1, the §11 graduation facts and the boost queue. Order: boosts, then retargeting, then cold, all inside min(daily cap − spent, monthly cap − spent, balance − cash floor). A **boost** is planned only for class WINNER + compliance pass + judge passed + a human approval record (by, at, max), at min(request, approval, $250/day). **Retargeting** ≤ its request and $1,000/day. **Cold** only once the §11 gate passes (blended paid media per net new member ≤ $111 at $25 / $132 at $30 over 5 days at ≥ $4K/day, charge-today factor ≥ 0.64 / 0.57 (upside case 0.48 / 0.43), ≥ 300 purchases, refunds ≤ 12%, chargebacks < 0.35%, renewal 1 ≥ 58% from day 40), starting at $50/day, +20%/day under SCALE, flat under HOLD, −30% under CUT, ≤ $8K/day; `governor.pre_gate_cold_daily_usd` (default 0) is the client switch for the R7 $3K/day pre-gate line. The §9 rule table sets the status, price-aware with the ×1.15 learning lines on days 1–7: CAC ≤ $111 / $132 SCALE, ≤ $155 / $185 HOLD, above that two days running CUT; refunds > 8% HOLD, > 12% no scaling; chargebacks ≥ 0.35% or 50 HOLD, ≥ 0.5% or 75 **STOP**; renewal 1 < 58% HOLD (< 50% hold spend) from day 25 on cohorts ≥ 100; cash headroom < 30% HOLD, < 10% CUT. Any NaN, inf, negative, absurd (> $1M) or wrongly typed input, or a missing/expired/unapproved budget, gives a zero plan with status STOP. The executor stub refuses without `SPEND_ENABLED=1`, `GROWTH_DRY_RUN=0`, a live valid plan and a human approval bound to that plan's `state_hash`; even then it only records that no ad client is wired. **No ad API is called anywhere in the codebase.**

**Tables** (`schema_growth.sql`, RLS forced, service_role only, same policy as §11 of `schema.sql`): `post_metrics`, `page_baselines`, `post_scores`, `winners`, `remix_jobs`, `boost_queue` (an `approved` row needs a passing judge and a named human, by check constraint), `bandit_arms`, `spend_budgets`, `spend_ledger` (append-only; a trigger refuses any day above the approved daily cap) and `governor_decisions` (append-only). Views `v_boost_approval_queue` and `v_remix_queue` for the review app.

**Workflow** (`n8n_growth_workflow.json`): hourly tick → captures + order rollups → normalize → baselines → score → winners → actions → remix/boost rows → Slack summary; nightly 23:10 → allocator → queued briefs → governor dry run → `governor_decisions` → Slack "plan for approval". The workflow never calls `/growth/governor/execute`, never writes `posts` or `spend_budgets`, and never touches an ads API.

### 7.6 Niche discovery and MRR-weighted iteration (`workers/discover/`, `schema_discover.sql`, `n8n_discover_workflow.json`)

What the best 55+ health / strength / mobility / kitchen posts are doing this week, across IG, FB, TikTok, YouTube Shorts, Threads and X, turned into our own scripts, and a value score that ranks our posts by money as well as reach. Nothing here posts, spends, logs in or re-hosts video.

**1. Crawl** (`/discover/crawl`; daily 03:00 ET for the last 90 days, kept to the top 500–1,000 by relative performance; hourly stream over the last 2 h for velocity). Seeds: `data/discover/seeds.json` (60 queries, 100 creators, every creator `to_verify` until a human checks the handle). Sources in priority per platform, first one with credentials wins: official APIs (YouTube Data API search → videos, `engagedViews` used where a payload carries it; TikTok Research API; IG Graph `business_discovery` and Meta Content Library where approved; Threads `keyword_search`; X recent search), then yt-dlp metadata (`--skip-download --dump-json`, YouTube only, cookie and credential flags refused), then a public-page fallback: og:/JSON-LD metadata only, robots.txt must allow the path (unreachable robots = disallow), Crawl-delay and per-host spacing honoured, https only, no cookies or auth, and hosts whose terms forbid automated collection (instagram.com, facebook.com, threads.net, x.com, tiktok.com) are refused outright. Unverified creators never use the fallback. Live I/O needs `DISCOVER_LIVE=1`; without it n8n or a researcher export pushes raw payloads and the same adapters parse them. Tests run on fixtures with no network.

**2. Normalize** to the `data/posts.csv` schema (POSTDB_FINDINGS) and `niche_posts` rows: rel_perf = metric ÷ rolling median of the creator's 15 nearest posts (platform median when a creator has < 3), metric = views (YouTube engagedViews when present) or engagement where a platform hides other accounts' views. Genes use the scorecard's own split (`growth.variants.decompose`): `hook:<grammar>`, `body:<pillar:format>`, `close:<CTA keyword>`, classified from public text by deterministic rules, plus lane (talking head / insert / movement).

**3. Trends** (`/discover/trends`): per platform × gene, recent 7 d vs prior window lift; rising = ≥ 3 recent posts and lift ≥ 1.5 (or a strong new gene). **Transfer detector**: a gene rising on TikTok / X / Facebook with no Instagram equivalent (absent, or present and not performing) → `niche_opportunities` "to_instagram", and the reverse "from_instagram". Feeds: daily top-20 (48 h) and weekly top-50 (7 d) by trend score; gate-refit rows (features + top-quartile label) for the virality gate and predictor; allocator exploration observations on our arm keys at weight 0.2, so a niche-proven gene gets explored sooner but never outweighs our own data.

**4. Remake briefs** (`/discover/remake` → `remake_queue`): mechanism, our angle in Chang's or Sun's voice, a running bit, 3 hooks (5 for GO-HARD) from our grammar templates, lane and a visual concept on our own set. Plagiarism guard: no line equal to a source sentence, no shared 7-word shingle with the source, visual concept only (no source frame, audio or media URL in the brief; the source URL lives in provenance). The table refuses a brief whose guard failed or that has no provenance. Every brief still passes `/compliance/scan`, the LLM judge and `/uniqueness/check` downstream.

**5. MRR-weighted iteration** (`/discover/value`, weekly): `growth.scorecard.value_score` blends virality (the scorecard components except conversion) with money (attributed new MRR per 1K views 70% + buyers per 1K 30%, each against the page's history with empirical-Bayes shrinkage and 20K pseudo-views), **50/50 by default, 30/70 in print mode**. `growth.actions.mrr_plan`: money ≥ 80 on ≥ 5K views → **GO-HARD**: remake with 5 hooks on every other page, the Facebook long cut, 5 Trial Reels, an email feature draft (a human sends), the DM pinned link, and a boost candidate held until the spend gate (MRR ≥ $30K; the governor and a human still decide). Virality ≥ 80 with money < 40 → reach remix + a CTA-swap experiment on the close block. Weekly readout: top posts by MRR, by views and by both. `v_post_attribution` counts only a lead's first subscription order as new MRR.

**Workflow** (`n8n_discover_workflow.json`, inactive, crawl nodes disabled until `LAUNCH_MODE=live`): daily 03:00 ET crawl → niche_posts → trends → opportunities + feeds → remake briefs → remake_queue → Slack; hourly stream → niche_post_reads; Monday 04:00 ET weekly top-50 + gate refit + value readout → Slack.

---

## 8. Localization branch

1. **Source selection:** winners and breakouts flagged `localize`, plus a daily quota per localized page (e.g., `@changyin.espanol` needs 3/day during the Mode A pilot; 50% localized winners, 50% native ideas from Spanish comments).
2. **Transcreate** with `08_localization_adapter`: same claims and IDs, syllable budget within ±12% per line, local units and foods, a localized single-word CTA keyword without accents (FUERZA), market rules (EU: no nutrition claims beyond generic; AI Act Art. 50 transparency).
3. **Compliance pass 1** in the target language (the same judge; the blocked-claims regexes get localized equivalents in `blocked_claims` rows with a locale tag **[A: add a `locale` column]**).
4. **Re-voice** with the same designed voices (`characters.voice_by_locale`, multilingual model). Re-generating TTS from the transcreated script beats dubbing the audio. ElevenLabs Dubbing ($0.33/min v1) is only for fast tests.
5. **Re-lip-sync only the talking shots** (InfiniteTalk from the original keyframes). **Reuse** every `gen_scene`, `motion_transfer`, library and graphic shot. This works because text is never baked into generated video; all text is overlay.
6. **Re-caption** (locale number formats, e.g., 142.861) and re-package with the local footer (SAFETY_RULES §7 ES footer).
7. **Localized pages are separate accounts** with their own uniqueness scope (the same idea in EN and ES isn't duplicate content), their own ramp, and their own DM flows and offer pages.
8. **New archetype** (e.g., a native Spanish character): add a `characters` row, a reference pack, a designed voice and a bible. Pages point to it via `character_ids`. **No workflow changes.**

---

## 9. Build plan: live in 14 days

**Critical-path items to start on day 1:** TikTok app audit, YouTube API audit, Meta Business verification, a signed credentialed reviewer, and the performer shoot booking.

### Week 1: foundations

| Day | Deliverables | Checklist |
|---|---|---|
| **D1** | Accounts and legal | ☐ Legal entity + Meta Business Portfolio + start business verification ☐ Domain + Google Workspace aliases ☐ Create the 3 day-1 pages (`@changyin`, `@sunyoon.kitchen`, `@changandsun`) × 6 platforms (18 accounts), unique emails, authenticator 2FA ☐ **Set the IG "AI-generated profile" label** on each IG account ☐ Bios per SAFETY_RULES §7 ☐ Submit the **TikTok Content Posting API audit** and the **YouTube API audit** ☐ Sign the credentialed reviewer (or strip "reviewed by" everywhere) ☐ Book the performer shoot (D6) |
| **D2** | Infra | ☐ Supabase project; enable `vector`, `pg_trgm`, `pgcrypto`; run `schema.sql` ☐ R2 bucket + public custom domain (also verify it for TikTok `PULL_FROM_URL`) ☐ VPS: n8n in queue mode + Redis + Postgres ☐ Vault secrets naming convention ☐ Slack channel + webhook |
| **D3** | Characters | ☐ Generate the 24-image reference pack (CHARACTERS §13.1) with NB Pro; human-select and lock ☐ ArcFace embeddings → `character_refs.embedding`, `characters.face_centroid` ☐ ElevenLabs Voice Design for Chang and Sun (CHARACTERS §13.3); lock voice IDs ☐ Load bibles → `characters.bible_md` |
| **D4** | Prompts and knowledge | ☐ Load `prompts/01–08` into `prompt_versions` (script: split on the markers and insert v1 active) ☐ Load SAFETY_RULES.md as `prompt_key = 'safety_rules_md'` ☐ Load EVIDENCE.md into `evidence`; `blocked_claims.json` plus the SAFETY_RULES §3.1 regexes into `blocked_claims` ☐ Page DNA for the 3 day-1 pages (sets, wardrobe, caption style, footer, movement add-on, CTA keywords, hashtag bank) |
| **D5** | Workers | ☐ Render worker: `/voice/stitch`, `/assemble` (Remotion template: high-contrast captions, PiP, study card, timer), `/variants`, C2PA signing ☐ QA worker: `/qa` (InsightFace ArcFace, SyncNet, ffmpeg ebur128/blackdetect/freezedetect, Tesseract/vision OCR, ffprobe, c2patool) |
| **D6** | Driving videos + library | ☐ 4 h performer shoot → 150–250 clips, tagged, form-checked ([ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: by the signed PT] FALLBACK: "by our team against published exercise guidance"), uploaded → `assets(kind = 'driving_video', license = release)` ☐ Pre-render 150 action and B-roll clips + 40 graphics → `assets` |
| **D7** | Import and wire | ☐ Import `n8n_core_workflow.json`; create credentials; set env vars; set Error workflow ☐ Verify every model endpoint ID and param in the `MODELS` maps on the fal and WaveSpeed pages ☐ Run 5 briefs manually, fixing as you go |

### Week 2: dry run → soft launch

| Day | Deliverables | Checklist |
|---|---|---|
| **D8** | Dry run at volume | ☐ 50 briefs across R1–R4 × 3 tiers, **no publishing** ☐ Measure cost/video, p50/p95 latency and first-pass yield |
| **D9** | QA calibration | ☐ VA 1 labels 100 renders (pass/review/fail) ☐ Tune the ArcFace, SyncNet and OCR bands to ≥ 90% agreement with humans ☐ Run the compliance self-tests (SAFETY_RULES §10–11) through the judge; 100% of block cases must block |
| **D10** | Review app + DM | ☐ Minimal review UI (Supabase + a simple page: video, script, claims, QA reasons, Approve/Reject/Fix → webhook). High-contrast buttons, no gray text. ☐ ManyChat flows for the 3 day-1 pages (keyword → deliverable DM → email capture → offer), with the crisis keyword flow |
| **D11** | Soft launch (= rollout day 1) | ☐ The 3 day-1 pages live (`@changyin`, `@sunyoon.kitchen`, `@changandsun`): pinned posts in-app, then 1–2/day/platform (§5.4 week 1) via IG official + upload-post (TikTok, YT, FB, Threads) + X official ☐ Every video goes through human approval |
| **D12** | Metrics | ☐ W5 metrics ingest + `v_post_scores` dashboard ☐ UTM + `pid` attribution tested with a live test purchase |
| **D13** | All launch pages | ☐ All 3 day-1 pages posting on the §5.4 ramp (no 4th page until rollout day 15) ☐ W1 idea miner + W2 planner on schedule (D+1 slots) ☐ Budget caps set per page |
| **D14** | Go-live review | ☐ Yield ≥ 80%, cost within ±20% of plan, zero platform warnings ☐ Ramp targets for week 3 ☐ Runbook handed to the VAs |

### Weeks 3–4: scale

- Ramp to 3/day (week 2), 5–6/day (week 3) and then 6–9/day where the §5.4 gates pass. Launch `@changyin.strength` and `@changyin.mobility` on rollout day 15 and `@sunyoon` on day 22, each starting at week 1 of the §5.4 ramp.
- Build W7 (winner/remix) and W10 (ops/circuit breaker). Switch polling to webhooks.
- Flip `publisher` to `official` per platform as the audits land.
- Replace ManyChat with the in-house Private Replies bot at 10+ pages if costs justify it.
- Pilot localization: `@changyin.espanol` from rollout day 30 at 3/day (Mode A pilot). It stays at 3/day until the full Spanish market launch in US month 4–5 (EXPANSION.md §4).
- `auto_publish` on for pages with 14 clean days.

### Month 2+: 10 → 20 pages

- New editorial scopes plus languages (ES, PT-BR, DE).
- Shard YouTube across GCP projects (≤ 100 uploads per project per day).
- Raise provider concurrency.
- Add VA 3.
- Quarterly performer shoot for new exercise families.

---

## 10. Risk register (top 10)

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | YouTube demonetizes or down-ranks an AI persona on health topics | High | Medium (YT is a funnel) | Movement and food focus, narrative variety, no YPP dependence, human reviewer credited |
| 2 | Sibling-page duplicate detection | Medium | High | L3 rule, 4 automated guards, stagger, distinct page DNA |
| 3 | Health-claim complaint or FTC action | Low–Med | Very high | Two-pass compliance, EVIDENCE IDs, credentialed reviewer, no testimonials, no outcome CTAs |
| 4 | Identity drift or uncanny renders erode trust | Medium | High | Reference lock, ArcFace gate, vision QA, driving-video motion, premium for winners |
| 5 | API audits delayed (TikTok, YouTube) | High | Medium | upload-post launch path |
| 6 | Provider outage or price change | Medium | Medium | 3-deep fallback chain, circuit breaker, self-host lean tier |
| 7 | ManyChat cost blow-up on a viral page | Medium | Medium | In-house Private Replies bot; contact pruning |
| 8 | Crisis content in DMs (self-harm, medical emergency) | Medium | Very high | Keyword detection → instant resources + 15-min human SLA; no companion-chatbot behavior (CA SB 243) |
| 9 | Cultural backlash (Chinese/Korean heritage) | Low–Med | High | Paid cultural consultants, CHARACTERS §14 checklist, no mysticism or clergy, light accents only |
| 10 | Operator bottleneck in approvals | Medium | Medium | D−1 production buffer, trust-based auto-publish, 2 fixed review windows |

---

## 11. Sources (verified 2026-09-30)

**Models & generation**
- Claude API pricing (Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 4.5 $1/$5; batch −50%): https://claude.com/pricing
- OpenAI API pricing (GPT-6.1-Sol $2/$10, GPT-6-Luna $0.10/$0.50): https://developers.openai.com/api/docs/pricing
- Gemini API pricing (Nano Banana 2: $0.067 at 1K, $0.101 at 2K, $0.151 at 4K; batch −50%): https://ai.google.dev/gemini-api/docs/pricing
- Nano Banana Pro ($2 / $120 per MTok, latency): https://openrouter.ai/google/gemini-3-pro-image
- Veo 3.1 tiers (Lite $0.05/s, Fast $0.10/s, standard $0.40/s): https://costgoat.com/pricing/google-veo · Veo 3.1 Fast on fal ($0.10 / $0.15 per s): https://fal.ai/models/fal-ai/veo3.1/fast/image-to-video
- Kling 3.0 on fal (V3 / O3, $0.168–0.392/s, 3–15 s, multi-shot, elements): https://fal.ai/kling-3 · Kling v3 Std i2v ($0.084/s): https://fal.ai/models/fal-ai/kling-video/v3/standard/image-to-video
- Kling v3 Motion Control Pro ($0.168/s): https://fal.ai/models/fal-ai/kling-video/v3/pro/motion-control · v3 MC spec (3–30 s driving video, orientation modes, $0.13/s std): https://vercel.com/ai-gateway/models/kling-v3.0-motion-control · v2.6 Std MC ($0.07/s): https://fal.ai/models/fal-ai/kling-video/v2.6/standard/motion-control
- Seedance 2.0 reference-to-video (9 images, 3 videos, 3 audio; std ~$3.02 per 10 s at 720p): https://fal.ai/models/bytedance/seedance-2.0/reference-to-video · Fast ($0.2419/s at 720p): https://fal.ai/models/bytedance/seedance-2.0/fast/reference-to-video
- InfiniteTalk on WaveSpeed ($0.03/s at 480p, $0.06/s at 720p, 10 min, 10–30 s compute per s): https://wavespeed.ai/docs/docs-api/wavespeed-ai/infinitetalk
- OmniHuman 1.5 on fal ($0.16/s): https://fal.ai/models/fal-ai/bytedance/omnihuman/v1.5
- Higgsfield API (50+ models, 20 concurrent, failed requests not charged): https://higgsfield.ai/blog/higgsfield-api · https://open.higgsfield.ai/pricing
- HeyGen API pricing breakdown (third-party): https://realtimeavatar.ai/blog/heygen-api-pricing-explained
- ElevenLabs API pricing (v3 $0.08/1K chars; Dubbing v1 $0.33/min, v2 $2.20/min; Music $0.15/min; Scribe v2 $0.22/h): https://elevenlabs.io/pricing/api · plan tiers: https://www.layer3labs.io/guides/elevenlabs-pricing

**Editing & captions**
- ZapCap vs Submagic API pricing ($0.10/min vs ~$0.69/min): https://zapcap.ai/api/alternatives/submagic/
- Creatomate credits (~14 per 720p minute): https://creatomate.com/pricing
- Remotion licensing: https://www.remotion.dev/docs/license

**Publishing & platform rules**
- Instagram content publishing (100 posts / 24 h, `trial_params`): https://developers.facebook.com/docs/instagram-platform/content-publishing
- Instagram access levels (Standard Access for own accounts): https://developers.facebook.com/docs/instagram-platform/overview
- Facebook Reels publishing (30 / 24 h, 3–90 s): https://developers.facebook.com/docs/video-api/guides/reels-publishing
- Threads API (250 posts / 24 h): https://developers.facebook.com/docs/threads/posts
- TikTok Content Posting API (unaudited = private; 6 req/min; `is_aigc`): https://developers.tiktok.com/doc/content-posting-api-get-started · https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
- YouTube quota (100 `videos.insert` per project per day): https://developers.google.com/youtube/v3/getting-started · unverified projects upload private-only: https://developers.google.com/youtube/v3/docs/videos/insert · `containsSyntheticMedia`: https://developers.google.com/youtube/v3/docs/videos
- X API pay-per-use ($0.015/post, $0.20 with URL): https://www.postzen.dev/blog/twitter-api-pricing
- Blotato (plans $29/$97/$499; IG cap 50 per 24 h; API not in trial): https://www.blotato.com/ai-info
- upload-post plans ($16 / $33 / $118 / $350; 5 / 25 / 75 / 225 profiles): https://www.upload-post.com/pricing
- Ayrshare plans: https://www.ayrshare.com/pricing/
- Metricool (API from Advanced $53/mo): https://www.blotato.com/blog/metricool-pricing
- ManyChat plans: https://manychat.com/pricing · API: https://api.manychat.com/swagger

**Policy**
- Instagram "AI-generated profile" label and reach limits (Aug 31 2026): https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/
- Instagram aggregator and unoriginal-content penalty: https://www.tubefilter.com/2026/04/30/instagram-removes-algorithm-recommendations-repost-content-aggregator/
- YouTube inauthentic-content clarification (July 2026): https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/
- TikTok AI labeling enforcement (secondary summary): https://www.auditsocials.com/blog/tiktok-ai-content-disclosure-rules-2026
- Meta inauthentic behavior policy: https://transparency.meta.com/policies/community-standards/inauthentic-behavior/
- Instagram login limit (5 per device): https://stackinfluence.com/blog/how-many-instagram-accounts-can-i-have-tips

**Infrastructure & data**
- n8n pricing (Starter €20 / 2.5K executions; Pro €50 / 10K; Business self-hosted €667): https://n8n.io/pricing/
- Supabase pricing (Pro $25): https://supabase.com/pricing
- Cloudflare R2 ($0.015/GB-mo, free egress): https://developers.cloudflare.com/r2/pricing/
- Apify Instagram comment scraper ($2.30 per 1K): https://apify.com/apify/instagram-comment-scraper · TikTok scraper ($1.70 per 1K): https://apify.com/clockworks/tiktok-scraper

---

## Appendix A: load prompts into `prompt_versions` (day 4)

```python
# pip install psycopg[binary]   ·   DATABASE_URL = Supabase direct connection string
import glob, os, re, psycopg
KEYS = {"01": ("idea_miner", "claude-sonnet-5-5", 0.8, 8000), "02": ("script_writer", "claude-sonnet-5-5", 0.9, 3000),
        "03": ("compliance_judge", "claude-opus-5-5", 0.0, 2500), "04": ("shot_planner", "claude-sonnet-5-5", 0.4, 4000),
        "05": ("variant_generator", "claude-sonnet-5-5", 0.95, 6000), "06": ("caption_writer", "claude-haiku-4-5", 0.8, 3500),
        "07": ("qa_vision", "claude-sonnet-5-5", 0.0, 2500), "08": ("localization_adapter", "claude-sonnet-5-5", 0.5, 4000)}
with psycopg.connect(os.environ["DATABASE_URL"]) as db:
    for f in sorted(glob.glob("prompts/0*.md")):
        key, model, temp, max_tok = KEYS[os.path.basename(f)[:2]]
        sys_t, usr_t = re.search(r"<<<SYSTEM>>>\n(.*?)<<<USER>>>\n(.*?)<<<END>>>", open(f).read(), re.S).groups()
        v = db.execute("select coalesce(max(version),0)+1 from prompt_versions where prompt_key=%s", (key,)).fetchone()[0]
        db.execute("update prompt_versions set active=false where prompt_key=%s", (key,))
        db.execute("insert into prompt_versions(prompt_key,version,system_text,user_template,model,temperature,max_tokens,active)"
                   " values (%s,%s,%s,%s,%s,%s,%s,true)", (key, v, sys_t, usr_t, model, temp, max_tok))
    db.execute("update prompt_versions set active=false where prompt_key='safety_rules_md'")
    db.execute("insert into prompt_versions(prompt_key,version,system_text,user_template,model,active) values "
               "('safety_rules_md',(select coalesce(max(version),0)+1 from prompt_versions where prompt_key='safety_rules_md'),%s,'','n/a',true)",
               (open("SAFETY_RULES.md").read(),))
```
Prompt changes are versioned. Roll back by flipping `active`. Every script row stores the `prompt_version_id` that produced it, so performance can be compared per prompt version.
