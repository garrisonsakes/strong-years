# ENGINE_SUBLAYERS.md: the content engine broken into 48 sub-units, 10 improvements each

Round of Oct 2 2026. Inputs: ENGINE_100X.md, ENGINE_NEXT50.md, VIRALITY_SYSTEM.md, PIPELINE.md, workers/README.md, SYSTEM_RECAP.md, and a grep of `workers/`, `tools/`, `app/src/`, `shopify/src/` and the two n8n JSON files to see what already exists. I ran 6 web searches and 6 fetches, all for claims that needed a citation. Nothing was spent, posted or generated.

**How to read this.** Each sub-unit (SL-01 … SL-48) has one line on what exists now, then 10 improvements ranked by expected impact. Columns: What · Why · Where (file or worker) · Cost · Conf (H/M/L). **Cost** is dev hours (`h`) plus any run-rate (`+$/mo`) or per-unit cost. **★** marks the items in the launch-tomorrow cut, ENGINE_SAVAGE20.md §B(b). IDs are `SL-nn.k`.

**Dedupe rule.** I left out anything in ENGINE_100X.md §1–11 or ENGINE_NEXT50.md (550 items), even under another name. Where an item builds on one of those, it cites it. Most items here are build mechanics (contracts, caches, idempotency, validators, calibration), because both earlier rounds were mostly about strategy.

**New sources** (S# = ENGINE_100X §12, N# = ENGINE_NEXT50 header):
- **P1** Shopify removes a webhook subscription after 19 consecutive failed retried deliveries. [shopify.dev, Troubleshoot webhooks](https://shopify.dev/docs/apps/build/webhooks/troubleshooting-webhooks)
- **P2** YouTube Data API: 10,000 units per project per day by default, `videos.insert` costs 1,600 units, `thumbnails.set` 50, reads 1 (50 IDs per `videos.list` call). There is no paid tier; the quota-extension form takes weeks. [V-] [OutlierKit, Jun 2026](https://outlierkit.com/resources/youtube-api-quota/) · [Blotato](https://www.blotato.com/blog/youtube-api-pricing)
- **P3** TikTok Content Posting API: unaudited clients can only post `SELF_ONLY` (private), for at most 5 users per 24 h. Creators have a daily cap of about 15 posts shared across all clients. [V-] [VorpLabs](https://vorplabs.com/agent-tools/tiktok-content-posting-api) · [Outstand](https://www.outstand.so/blog/tiktok-content-posting-api)
- **P4** Supabase daily backups are kept 7 days on Pro and 14 on Team. PITR is an add-on with a worst-case RPO of 2 min. [Supabase](https://supabase.com/features/database-backups)
- **P5** Gmail and Yahoo bulk senders (5,000+/day): spam complaints must stay below 0.3%, RFC 8058 one-click unsubscribe is mandatory and must be honoured within 48 h, and DMARC is required. [V-] [PowerDMARC](https://powerdmarc.com/bulk-email-sender-requirements/) · [Mailgun](https://www.mailgun.com/state-of-email-deliverability/chapter/yahoogle-bulk-senders/)
- **P6** LLM-judge position bias is systematic and worst when the candidates are close in quality. Swapping order and majority voting make more than 95% of cases reliable; the hard ~5% need a human. [Shi et al., IJCNLP-AACL 2025](https://aclanthology.org/2025.ijcnlp-long.18.pdf) · [arXiv 2406.07791](https://arxiv.org/pdf/2406.07791v9)

**Three findings that change the launch plan** (details in SL-27):
1. **YouTube can't take 24 Shorts a day per project.** The quota covers 6 uploads (10,000 ÷ 1,600) [P2]. At canon 4 (4 channels × 6) we need 38,400 units, 3.8× the default. File the extension now and post YouTube by hand or through upload-post until it is granted.
2. **TikTok API posts are private until the audit passes** [P3]. That makes the API useless for launch, so TikTok goes out by hand or via draft-to-inbox (NEXT50 TT-12). The private-only lane is still useful as a free staging lane (SAVAGE20 #18).
3. **A missed Shopify webhook is silent and eventually fatal.** After 19 straight failures the subscription is deleted [P1], and members stop being provisioned without any error showing. A reconciliation poller is needed (SL-39.3).

---

## A. Create

### SL-01 Script ideation (W1 idea miner, `prompts/01_idea_miner.md`, table `ideas`)
Now: W1 runs at 05:00 and 15:00 over own comments, competitors and trends, and writes `ideas` with a risk tier. Script supply covers 8–12 days; 87% of planned rows are `GEN-needed`.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Inventory-aware W1 frequency.** Compute approved-script days per page. Below 3 days, W1 runs every 2 h with double the target; above 10 days, it only mines | Supply is the binding constraint (87% GEN-needed). Ideation should follow the buffer, not the clock | SQL view `v_script_runway`; n8n W1 trigger | 3h | H |
| 2 | **Reject near-duplicate ideas at the idea stage** with the same TF-IDF/MinHash the guard uses (≥0.80 against the 291-script library plus 30 days of ideas) | Today a duplicate is caught only after a script (and sometimes renders) has been paid for | `uniqueness/textsim.py` via `/uniqueness/check` `mode=idea` | 3h | H |
| 3 | **Evidence id required at the idea** for health pillars (`ideas.evidence_ids` NOT NULL) | Cheapest place to reject an unsupported claim; it cuts judge `revise` loops downstream | `prompts/01` schema; `schema.sql` constraint | 2h | H |
| 4 | **Prompt-cache the fixed prefix** (character bible, SAFETY, hook-bank summary) | Cache reads are $0.20/MTok against $2 for Sonnet input (PIPELINE §1.3), and the prefix is most of the tokens | n8n *Build Script Request* `cache_control` | 2h | H |
| 5 | **Batch API for the 05:00 mining run** (results due by 08:00) | −50% on non-urgent tokens (PIPELINE §1.3) | W1 uses `/v1/messages/batches` | 2h | H |
| 6 | **Slot-fit field**: each idea names the allocator arm it serves (pillar × grammar × format × speaker), and W2 briefs only ideas that match sampled arms | Stops orphan ideas that no slot ever asks for; ties supply to the bandit | `prompts/01` output; `growth/allocator.py` | 3h | M |
| 7 | **Idea yield funnel by source** (own comments / competitor / trend → approved → posted → WINNER) | Cut low-yield sources and spend tokens where winners come from | view `v_idea_yield`; weekly readout | 2h | M |
| 8 | **Cross-page idea lock**: an idea is claimed by one page family, and siblings get it only as a REMIX with ≥3 dimensions changed | Keeps two pages from getting the same idea on the same day, which the text guard can miss when wording differs | `ideas.claimed_page` | 2h | M |
| 9 | **Risk-tier calibration sample**: 20 green ideas/week go to the reviewer. If more than 5% get flagged, tighten the tiering prompt | The green → auto path is only as safe as the tiering | `/admin/exceptions` type `tier_audit` | 2h | M |
| 10 | **Idea expiry** after 14 days unless tagged evergreen | Stale topical ideas reaching render waste money and read as tone-deaf | `ideas.expires_at`; `claim_next_brief` filter | 1h | M |

### SL-02 Hook writing (`prompts/02_script_writer.md`, `prompts/05_variant_generator.md`, `hooks.json`)
Now: the writer returns one hook per script; the hook bank has 430 entries; the rubric scores hook grammar.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Over-generate and rank**: 8 hook candidates per script, keep the top 3 by rubric hook points (grammar, number, first-clause length) | A hook costs ~$0.0003 to write and ~$0.45+ to render (NEXT50 MOD-2). Ranking before render is close to free | `prompts/05`; `tools/virality.py` `score_hook()` | 3h | H |
| 2 | **Compliance pre-scan each candidate** (`scanner.scan_text`) before ranking | Blocked phrasing should never win the ranking and then die at the judge | `compliance/scanner.py` call in the ranker | 1h | H |
| 3 | **Hook-level dedupe** within a page's 30-day window (textsim ≤0.60 on the hook alone) | The guard compares whole scripts, so a reused hook on a new body passes | `uniqueness/guard.py` `check_hook()` | 2h | H |
| 4 | **Spoken-duration check**: TTS the hook with Flash v2.5 and reject it if it runs over 3.2 s | Word counts miss long words and numbers; real duration is what the 3 s hold sees | `assemble/voice.py`; ~$0.0005/hook | 2h | M |
| 5 | **Hook ↔ body promise check**: the hook's noun (body part, food, number) must appear in the body's first 2 sentences | Hooks that promise one thing and deliver another lose viewers at 3–6 s | `tools/virality.py` validator | 2h | M |
| 6 | **Hook ↔ shot-1 contract**: an action verb in the hook ("watch my hands", "stand up") must exist in shot 1 of the shot plan | Turns a writing intention into a checked render fact | `prompts/04` contract; `assemble/virality_gate.py` | 2h | M |
| 7 | **Own-winner few-shot**: the writer prompt carries the verbatim hook lines of the top 5 own winners per grammar, refreshed weekly | Own data beats the competitor exemplars once ~30 posts/page exist (different from NEXT50 LL-35, which ships posterior numbers) | `growth/learning.py` `gene_table` → prompt variable | 3h | M |
| 8 | **Hook provenance**: every hook in `hooks.json` carries a source (POSTDB, comment id, writer version) and a parent | Lets learning credit sources and prompt versions | `data/content/hooks.json` schema | 2h | M |
| 9 | **Temperature by slot type**: 0.9 for explore slots, 0.4 for exploit slots | Explore should vary; exploit should reproduce a known pattern | allocator slot `type` → request | 1h | M |
| 10 | **Display normalisation**: digits rather than words, consistent units, no curly-quote or confusable characters | Prevents false OCR CER failures in QA and keeps numbers scannable | `compliance/textnorm.py` `display_norm()` | 1h | H |

### SL-03 Hook scoring (pre-post rubric in `tools/virality.py`; post-hoc hook component in `growth/scorecard.py`)
Now: the pre-post score is the rubric's hook grammar points. Post-hoc, IG uses `1 − reels_skip_rate`, FB uses the 3 s retention point, and everything else uses `hold_3s`, with shrinkage.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Rank on the lower confidence bound** (Beta posterior on 3 s hold with n = plays), not the mean | Small trials win on noise. The LCB makes 300-play posts prove themselves | `scorecard.py` `hook_lcb()` | 2h | H |
| 2 | **Explicit reach floor**: hook scores below 300 non-follower plays show as `insufficient` in `/admin/today`, not as a number | A noisy number gets acted on; a status doesn't | `scorecard.py`; admin view | 1h | H |
| 3 | **Void the hook score on attribution mismatch**: if the OCR of frame 1 doesn't match the logged hook id, drop the score | A wrong label poisons the hook arms | `qa/ocr.py` → `post_scores_components.valid` | 2h | H |
| 4 | **Hook regression set in CI**: 40 POSTDB hooks with known relative performance. CI fails if the rubric's ranking has Spearman ρ < 0.3 | Guards against rubric edits that silently stop predicting | `tools/test_virality_hooks.py` | 2h | H |
| 5 | **Score the rendered hook, not the script**: recompute rubric hook points from frame-1 OCR plus first-3 s ASR | A render that drops the number shouldn't keep the number's points | `qa/ocr.py` + `tools/virality.py` | 3h | M |
| 6 | **Length-bucket baselines for hold**: compare a 20 s reel's 3 s skip with other 20 s reels, not with 55 s ones | Skip norms differ by length, so mixed baselines bias toward one bucket | `growth/baselines.py` key + `len_bucket` | 2h | M |
| 7 | **Pairwise LLM hook ranking**, both orders, majority vote, for pre-post ties within 3 points [P6] | Absolute LLM scores are poorly calibrated; pairwise with order swap is the documented fix | new `prompts/09_hook_pairwise.md`; ~$0.003/pair | 4h | M |
| 8 | **Cross-platform transfer coefficient**: estimate how IG trial hold predicts TikTok and YouTube hold | Tells us how much to trust an IG winner on other platforms before NEXT50 IG-48 propagates it | `learning.py` weekly regression | 3h | M |
| 9 | **Leakage guard**: posts with a cover A/B or caption edit after 1 h are excluded from hook-score training | A mid-flight change contaminates the hook read | `scorecard.py` flag `edited_after_1h` | 1h | M |
| 10 | **Weekly hook leaderboard CSV** for writers (hook text, grammar, LCB, n) | Writers read a table faster than a dashboard | `data/hooks_leaderboard.csv` from `learning.py` | 1h | M |

### SL-04 Body writing (`prompts/02_script_writer.md`)
Now: the writer emits script JSON with claims and evidence ids; the judge loops `revise` up to 2 times.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Beat-sheet contract**: the body is 3–5 beats, each with a target time, a demo action and at most one claim id | The dip finder (NEXT50 LL-3) needs seconds mapped to beats, and the shot planner needs actions | `prompts/02` schema; JSON-schema check in *Parse Script* | 3h | H |
| 2 | **Quote the evidence, not just the id**: the writer gets the exact EVIDENCE.md excerpt for each claim | Paraphrase drift is the top cause of `revise` | `common/evidence.py` → prompt | 2h | H |
| 3 | **Pre-TTS duration estimate** (chars at 2.3 w/s) with a hard reject over the length bucket | Saves voice and lip-sync money on overlong bodies | `tools/virality.py` `est_duration()` | 1h | H |
| 4 | **Claim density cap**: at most 1 health claim per 15 s | Lower scanner and judge risk; easier for older viewers to follow | `compliance/rules.py` | 1h | H |
| 5 | **Safety-line position**: the movement safety line must come before the first demo beat | A safety line after the movement is useless and reads as a disclaimer tacked on | `compliance/scanner.py` position rule | 1h | H |
| 6 | **Sentence ceiling of 14 words** in bodies (auto-split) | Long sentences break TTS prosody and older listeners' working memory | `prompts/02` rule + validator | 1h | H |
| 7 | **Minimal-patch revise**: on `revise`, the writer gets only the flagged sentences and returns a patch | Keeps good beats, cuts tokens and stops loop regressions | n8n *Attach Revision Feedback* | 3h | M |
| 8 | **Proof object per body**: one countable proof (reps, seconds, grams) that the on-screen chip can show | Concrete numbers carry the rubric and the save trigger | `prompts/02`; validator | 1h | M |
| 9 | **Adaptive re-hook timing** from the measured median dip per pillar (refines NEXT50 HK-7's fixed 40–50%) | Put the re-hook where viewers actually leave | `learning.py` → writer variable | 2h | M |
| 10 | **Evergreen body fallback**: after 2 failed revises, swap in an approved evergreen body from the same pillar if it passes uniqueness; human only if none fits | Keeps slots filled without adding to the human queue | `claim_next_brief` + body bank | 3h | M |

### SL-05 Close / CTA
Now: one keyword per close; 14 DM flows; CTA phase rules in the plan; TikTok CTA rewrite in the packager.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 ★ | **Keyword registry check**: every close keyword in scripts and the day-1 plan must map to a flow in `workers/dm/flows/` (and to a manual reply script while DMs are manual) | A dead keyword burns the comment economy on the posts that matter most | `tools/build_content.py` + `production/launch_day` test | 1h | H |
| 2 | **Keyword collision check**: flag keywords that occur in normal comments ("BACK", "SLEEP"). Require a single-word comment or exact match to trigger | Prevents unwanted DMs to people who just wrote "my back hurts" | `dm/bot.py` matcher + corpus test on `data/posts` comments | 2h | H |
| 3 | **End-card keyword**: spoken and on screen in the last 2 s with ≥1.5 s dwell, checked | 100X's chip is mid-video; the close needs its own visual | `assemble/virality_gate.py` R7 | 2h | H |
| 4 | **No price in organic closes** (scanner rule; only the PRICE flow states a price) | Price-in-feed hurts reach on TikTok [S32] and invites "scam" replies | `compliance/rules.py` | 1h | H |
| 5 | **CTA ↔ landing parity**: the close's promise must match the first screen of `/b?t=<KEYWORD>` | A promise-to-page mismatch is the cheapest conversion leak to fix | `app/src/app/b/route.ts` test over flows | 2h | M |
| 6 | **Close starts ≥2.0 s before the end** | TikTok loops cut final words; the CTA must finish | `virality_gate.py` | 1h | M |
| 7 | **Choose the close by $/view** from the RPC panel, not by share rate | The close is the monetising block, so it should be scored in dollars | `growth/allocator.py` + `app/src/lib/offers/metrics.ts` | 3h | M |
| 8 | **No-CTA control posts**: 10% of posts carry no ask | Measures what a CTA costs in reach, per post rather than per day (NEXT50 LL-9 is day-level) | allocator `close=none` arm | 1h | M |
| 9 | **Soft close during a reach drop**: pages flagged by the reach-drop detector (100X §10.2) get non-ask closes | Protects a struggling account from more "spammy" signals | allocator rule | 1h | M |
| 10 | **Keyword shape**: ≤6 letters, no I/l/1 or O/0 ambiguity | Older and tremor-affected typing (NEXT50 X-H10) | `tools/build_content.py` lint | 0.5h | H |

### SL-06 Caption (`prompts/06_caption_hashtag_writer.md`, `packager/packager.py`)
Now: per-platform caption, exact footer, AI flags, length and hashtag caps, X link strip.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Caption from the final transcript** (post-TTS alignment), not the script | Edits made during `revise` must reach the caption | `packager.py` input | 1h | H |
| 2 | **Schema-validated caption with a deterministic template fallback** on parse failure | A caption parse error should never send a finished video to a human | `packager.py` | 2h | H |
| 3 | **Cross-page caption textsim ≤0.60** for sibling captions on the same day | The guard checks scripts; identical captions are an easy originality signal | `uniqueness/guard.py` `check_caption()` | 1h | H |
| 4 ★ | **Ban time-relative words** ("today", "this morning", "tonight") when the slot is more than 12 h from creation or crosses time zones | A "good morning" that posts at 7 pm reads as automated | `compliance/rules.py` `TIME_WORDS` + `packager.py` | 0.5h | H |
| 5 ★ | **Handle allowlist**: any `@handle` in a caption must be one of our own pages | Stops LLM-invented tags of strangers or brands | `packager.py` | 0.5h | H |
| 6 | **Spell-check** (hunspell en_US plus a whitelist of character and food names) | Typos read as scam to a 55+ audience | `packager.py` | 1h | H |
| 7 | **Caption cache** keyed on (script hash, platform, prompt version) | Retries and re-packages don't re-bill or drift | `packager.py` | 1h | H |
| 8 | **At most 2 emoji, none in line 1** | Screen readers read emoji names; line 1 is the truncation zone | `packager.py` | 0.5h | M |
| 9 | **Language detector**: English pages never get Spanish captions, and vice versa | Cheap guard for the localisation branch | `packager.py` (`langid`) | 1h | M |
| 10 | **Keyword-stuffing guard**: the search keyword appears once in line 1 and at most once more | Repetition reads as spam without helping search | `packager.py` | 0.5h | M |

### SL-07 Hashtags
Now: per-platform caps (IG 5, FB 3, TikTok 5, YT 3, Threads 1, X 2).

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Per-page curated allowlist** (~30 tags); the LLM may only pick from it | No trending-tag accidents; tags stay on-niche | `data/content/hashtags.json`; `packager.py` | 1h | H |
| 2 | **No condition hashtags** (#arthritis, #diabetes, #osteoporosis) | A condition tag next to a product or tip implies a health claim | `compliance/rules.py` | 1h | H |
| 3 | **CamelCase tags** (#ChairStands) | Screen readers read them correctly; easier for older readers | `packager.py` | 0.5h | H |
| 4 | **Weekly banned/flagged tag check** against a maintained list | Banned tags can suppress a post | manual list refresh; `packager.py` | 1h | M |
| 5 | **Sibling pages never use an identical tag set on the same day** | A fingerprint for network originality | `packager.py` + guard | 1h | M |
| 6 | **Zero-hashtag arm on IG** | Mosseri says tags don't raise reach (VIRALITY §6.3); measure it on our pages | allocator arm `tags=0` | 0.5h | M |
| 7 | **YouTube: the first 3 tags (shown above the title) are pillar tags** | They act as clickable topic links on Shorts | `packager.py` YT order | 0.5h | M |
| 8 | **Threads topic tag from the pillar map** | One tag per post; make it the community topic | `packager.py` | 0.5h | M |
| 9 | **Curated Spanish tag list** (not translated) | Literal translations miss the real tags people search | `hashtags.json` `es` | 1h | M |
| 10 | **Never tag a character name a clone uses** | Avoids feeding impersonators' discovery (100X Holes #2) | impersonation watch list → packager | 0.5h | M |

### SL-08 First-frame text
Now: R1 (≤0.05 s, ≤7 words, ≥1 s), hook text ≥72 px cap height, ≥7:1 contrast, never gray.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 ★ | **OCR frame 1 of every platform variant** (not just the master) against the intended hook (CER ≤2%) | Variants re-burn the hook; a burn bug ships the wrong text to one platform | `qa/ocr.py` `check_frame1(variant)` | 1h | H |
| 2 | **Measure contrast on rendered pixels** behind the text, not on declared colours | Video behind a pill or scrim can drop real contrast | `qa/probes.py` | 2h | H |
| 3 | **Hangul and Spanish glyph fallback** (Noto Sans KR); Figtree has no Hangul | Sun's Korean food words would render as tofu boxes | `assemble/overlay.py` font stack | 1h | H |
| 4 | **Semantic line breaks**: at most 2 lines, no orphan word, never split number + unit | Readability for older eyes | `assemble/overlay.py` | 2h | H |
| 5 | **No fade-in** on frame-1 text | Fades leave frame 0 blank in feed previews | `assemble/overlay.py` | 0.5h | H |
| 6 | **No emoji or symbols** in frame-1 text | They render inconsistently and screen readers misread them | `virality_gate.py` R1 | 0.5h | H |
| 7 | **Text never covers the face** (face bbox ∩ text box = 0) | A covered face kills the human signal in frame 1 | `layout.py` + `qa/face.py` | 3h | M |
| 8 | **Legibility at feed-preview size**: OCR the frame downscaled to 160 px wide | A first frame seen as a thumbnail must still read | `qa/ocr.py` | 2h | M |
| 9 | **Hook text persists across the first cut** until ≥1.5 s | A cut at 0.8 s that drops the text breaks R1's intent | `assemble/overlay.py` | 1h | M |
| 10 | **Digits on screen even when the voice says "ten"** | Numbers scan faster than words | `overlay.py` + `textnorm.display_norm()` | 0.5h | M |

### SL-09 Cover frame
Now: R6 (≤6 words, defaults to the frame-1 hook); `variants.cover()`.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Upload the cover natively** where the API allows (IG `cover_url`, YT `thumbnails.set` at 50 units [P2]) | Platform auto-picks are often mid-blink | posting nodes; `packager.py` | 2h | H |
| 2 | **Pick the sharpest, eyes-open frame** inside the hook slice (Laplacian variance plus eye aspect ratio) | The cover is the grid tile and the profile's first impression | `assemble/variants.py` `pick_cover_frame()` | 2h | M |
| 3 | **Face ≥30% of frame height** in 1:1 and 4:5 crops | Faces drive taps on grids and FB feeds | `qa/face.py` | 1h | M |
| 4 | **1:1 (FB feed) and 16:9 (YT channel tab) crop tests** (the 3:4 IG grid is NEXT50 IG-30) | Other surfaces crop differently | `qa/probes.py` | 1h | M |
| 5 | **Cover pHash against sibling covers** on the same day | Identical tiles across pages are an originality tell | `uniqueness/phash.py` | 1h | H |
| 6 | **Per-series colour band template** | Makes series recognisable on the grid | `assemble/graphics.py` | 2h | M |
| 7 | **Spell-check cover text** (OCR → hunspell) | A typo on the grid stays forever | `qa/ocr.py` | 0.5h | H |
| 8 | **Deterministic cover renders** (seeded) | Re-renders produce identical covers, so caching works | `variants.py` | 0.5h | M |
| 9 | **Character-name chip on covers for a page's first 30 days** | Recognition while the pages are new | `graphics.py` | 1h | L |
| 10 | **JPEG ≤1 MB, sRGB, metadata kept for C2PA** | Upload limits and colour shifts on iOS | `variants.py` | 0.5h | M |

### SL-10 Still generation (Nano Banana keyframes, `production/refs/`)
Now: reference-locked prompts (sha256), fal queue in n8n, idempotent on `brief:shot:stage:attempt`.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Generate at 1K and upscale only stills that pass QA** | 1K is $0.067 and 2K is $0.101 (PIPELINE §1.3); rejects shouldn't cost 2K | n8n *Build Keyframe Jobs* | 2h | H |
| 2 | **Assert the locked reference hash** in every request (refuse if absent) | Identity drift starts when someone swaps a reference | *Build Keyframe Jobs* + `production/refs` manifest | 1h | H |
| 3 | **Log the seed and prompt hash** per still | Exact reproduction for retakes and audits | `renders` columns | 1h | H |
| 4 | **Native 9:16 generation** (no crop from square) | Crops lose headroom and hands | prompt template | 0.5h | H |
| 5 | **Cost per accepted still** by provider and model | Rejects are part of the price; route on the real number | cost ledger (SL-45) | 1h | H |
| 6 | **Two candidates per keyframe; pick by ArcFace similarity** to the reference | +$0.067 per still is far cheaper than a failed video render | *Build Keyframe Jobs* `n=2` | 2h | M |
| 7 | **Versioned negative-prompt library** (extra fingers, text in image, logos) | Known failure modes, fixed once | `production/refs/negatives.json` | 1h | M |
| 8 | **Night pre-render at 22:00** for tomorrow's morning slots | Morning slots never wait on generation | n8n schedule | 1h | M |
| 9 | **Split the morning burst across fal and Higgsfield** before hitting 429s | Avoids queue stalls at peak | W10 router | 2h | M |
| 10 | **Record the provider still as a C2PA ingredient** of the master | A complete provenance chain | `assemble/c2pa_sign.py` | 2h | M |

### SL-11 Still QA
Now: ArcFace hook (needs the model) and Claude vision QA at the video level.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **OCR every still; any glyphs → reject** | Gibberish text is the most visible AI tell | `qa/ocr.py` `still_has_text()` | 1h | H |
| 2 | **Calibrate the ArcFace threshold** at the 1st percentile of ref-vs-ref similarity across the 54 locked refs | A guessed threshold either lets drift through or rejects good stills | `qa/face.py` + `production/refs` | 2h | H |
| 3 | **Run deterministic checks before Claude vision** | Vision costs $0.03–0.05; most rejects are deterministic | n8n order | 1h | H |
| 4 | **Cache QA verdicts by still hash** | Retries don't re-pay for QA | `qa/api.py` | 1h | H |
| 5 | **Exposure check**: reject if more than 2% of pixels are clipped | Blown highlights look synthetic | `qa/probes.py` | 1h | H |
| 6 | **Hand landmark count** (MediaPipe Hands) | Hands are the second most common AI tell | `qa/face.py` | 3h | M |
| 7 | **Apparent-age check** within ±5 years of the character spec | Characters must age consistently | `qa/face.py` | 2h | M |
| 8 | **Logo/brand detector** | No accidental brand placement | `qa/probes.py` | 3h | M |
| 9 | **Human spot-check of 5% of auto-passed stills** | Measures QA's miss rate | `/admin/exceptions` `still_audit` | 1h | M |
| 10 | **Cultural set sign-off cached per set id** (100X §9.7 sets the reviewer; this makes it one review per set, not per still) | Reviewer time scales with sets, not renders | `production/refs/sets.json` `signed_by` | 1h | M |

### SL-12 Voice render (ElevenLabs, `assemble/voice.py`)
Now: per-line TTS with timestamps, stitched with gaps; a pronunciation lexicon exists in `production/voices/`.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **TTS cache** keyed on (voice_id, text, settings, model) | Remixes and retries reuse identical lines for free | `voice.py` + R2 | 1h | H |
| 2 | **Apply the PLS lexicon on every request**, with a test | The lexicon exists; nothing proves it is sent | n8n *Build Voice Lines*; `production/voices/pronunciation.pls` | 1h | H |
| 3 | **Lock voice settings per character in config** (stability, similarity, style), versioned | Prevents silent drift between runs | `common/config.py` | 0.5h | H |
| 4 | **Daily character budget per vendor** with a hard stop | A runaway loop on TTS is a real bill | cost ledger (SL-45) | 1h | H |
| 5 | **Trim leading silence over 150 ms** per line | Dead air at frame 1 hurts R1 and the hook | `voice.py` | 0.5h | H |
| 6 | **Request PCM, not MP3** | Avoids a double lossy encode before AAC | *Build Voice Lines* | 0.5h | H |
| 7 | **Pass previous_text / next_text** for prosody continuity across lines | Line-by-line TTS otherwise resets intonation [A] | *Build Voice Lines* | 2h | M |
| 8 | **Set speed from text length** to hit 2.3 w/s rather than re-rendering | One call instead of a retake | `voice.py` | 1h | M |
| 9 | **Forced-alignment fallback** (local aeneas/WhisperX) when the vendor alignment is missing | Missing timestamps shouldn't fail a master | `voice.py` | 3h | M |
| 10 | **v4 promo rate for trials and drafts only until Oct 12** ($0.022 vs $0.08 per 1K chars) | Saves money on throwaway takes without changing the masters' voice | model map | 0.5h | M |

### SL-13 Voice QA
Now: loudness checks on the master; the transcript comes from TTS alignment; "true ASR pass" is a TODO in workers/README.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **ASR round-trip** (local Whisper small): WER ≤5% against the script | Catches skipped words and mispronunciations the alignment can't see | `qa/asr.py` (new) | 3h | H |
| 2 | **Clipping and true-peak check per line** before stitching | Stitching spreads one bad line through the master | `voice.py` | 0.5h | H |
| 3 | **Normalise each line to −20 LUFS before stitching** | An even voice level before the master pass | `voice.py` | 1h | H |
| 4 | **Upper bound on gaps**: 250–600 ms between lines | Long gaps read as glitches (accessibility.py only checks the lower bound) | `assemble/accessibility.py` | 0.5h | H |
| 5 | **Attach the QA verdict to the TTS cache entry** | A bad take is never reused | `voice.py` | 0.5h | H |
| 6 | **Per-line speech rate 2.0–2.6 w/s** | The total rate can hide one rushed line | `accessibility.py` | 0.5h | M |
| 7 | **Speaker-embedding similarity** (ECAPA) against the locked character voice | Catches voice drift when vendor models update | `qa/voice_id.py` (new) | 3h | M |
| 8 | **Human listen for lines containing names or Korean/Chinese food words** for the first 2 weeks | The lexicon is new; listen until it's proven | `/admin/exceptions` `voice_check` | 1h | M |
| 9 | **Spoken-language ID** (Spanish pages get Spanish audio) | Cheap localisation guard | `qa/asr.py` | 1h | M |
| 10 | **Artifact detector** (spectral-flatness spikes for clicks and breaths) | TTS artifacts are subtle but recurring | `qa/probes.py` | 3h | L |

### SL-14 Lip-sync render (InfiniteTalk via WaveSpeed)
Now: per-shot WAVs, fixed 60 s wait plus poll; talking head ≤40% of runtime.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Lip-sync only shots where the mouth is on screen for more than 1 s**; cutaways use plain voice-over | $0.03–0.06/s is billed per second synced | *Build Lip-sync Jobs* | 2h | H |
| 2 | **Audio hash in the job idempotency key** | A changed line re-renders only its own shot | `renders.idempotency_key` | 1h | H |
| 3 | **ArcFace on 3 output frames** | Lip-sync models can drift identity | `qa/face.py` | 1h | H |
| 4 | **Reject on a duration mismatch over 1 frame** against the audio | Prevents drift that gets worse over the master | *Check Lip-sync Done* | 0.5h | H |
| 5 | **Pad 200 ms of silence on both ends** of each shot WAV | Avoids mouth snaps at cuts | `voice.py` segmenter | 0.5h | M |
| 6 | **Poll with backoff** (or a provider webhook) instead of a fixed 60 s wait | Saves wall time on short shots | n8n poll sub-workflow | 2h | M |
| 7 | **CPU sync proxy** (mouth-open vs audio-energy correlation) until the SyncNet GPU worker exists | Some sync check now is better than none | `qa/probes.py` | 3h | M |
| 8 | **Cap lip-sync at 20 s per master** (hook plus close) | Keeps cost per master inside the Tier B envelope | shot planner rule | 1h | M |
| 9 | **A/B 480p-plus-upscale against 720p native** | Half the price if viewers can't tell | exception lane test | 2h | M |
| 10 | **Face-crop lip-sync, composited back** | Bills a smaller frame | `assemble/` compositor | 6h | L |

### SL-15 Slice retake (re-render only broken shots)
Now: QA can `requeue_brief` with `rerender_shots`, but PIPELINE §4.6 marks this **[A: worker honors it]**.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Make `rerender_shots` real**: *Build Video Jobs* filters to the failed shot ids and reuses the rest from R2 | Today a single bad shot may re-render the whole master | n8n *Build Video Jobs*; `requeue_brief` | 4h | H |
| 2 | **Failure taxonomy → retake strategy table** (identity → new still; anatomy → new seed; caption → re-assemble only; sync → re-lip-sync only) | The cheapest fix differs by failure | `qa/scoring.py` codes; n8n switch | 2h | H |
| 3 | **Caption-only failures never re-render video** | Re-assembly costs ~$0 | *Decide QA Route* | 1h | H |
| 4 | **Retake budget**: ≤2 retakes per shot and ≤$1 per master, then swap in library B-roll or a graphic | Stops retake spirals | cost ledger + router | 1h | H |
| 5 | **Reuse the stitched voice** unless the text changed | No re-TTS on visual retakes | n8n | 0.5h | H |
| 6 | **Seed policy**: retake 1 = seed+1 on the same still; retake 2 = a new still | A deterministic escalation | *Build Video Jobs* | 1h | M |
| 7 | **Retakes jump the queue** ahead of new briefs | Finish 90%-done masters first | `claim_next_brief` priority | 0.5h | M |
| 8 | **Retake rate by provider × model × shot type** feeds the router | Route away from what fails | view `v_retake_rate` | 2h | M |
| 9 | **Reviewers see only the changed shot** on retakes | Review time follows change size | review app | 2h | M |
| 10 | **Fail forward**: a non-critical B-roll shot that fails 3 times is dropped and the neighbour extended (if duration rules allow) | Ships the master instead of failing it | `assemble/assembler.py` manifest rewrite | 2h | M |

### SL-16 B-roll selection
Now: 60 B-roll prompts; library inserts; QA freeze detection.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Clip ≥ beat length**, or pick another clip (never loop or freeze) | Freezes fail QA and look cheap | manifest builder | 1h | H |
| 2 | **Required provenance field** per clip (generated / stock / licence id); untracked clips are blocked | A licence problem on a winner is expensive | selector + `assets.licence` | 1h | H |
| 3 | **No mirroring or flipping** | Flips reverse text and handedness and look like evasion | `assembler.py` | 0.5h | H |
| 4 | **Prefer free graphic inserts** (study cards) when the beat is a number | $0 and clearer than generated B-roll | shot planner rule | 1h | H |
| 5 | **Select by CLIP embedding** of the beat text against clip tags | Better matches than keyword tags | `assemble/broll_select.py` (new) | 4h | M |
| 6 | **Network-wide 7-day cooldown per clip** (per-page draws are NEXT50 MOD-3) | The same clip on 4 pages in a week is a duplication signal | selector | 1h | M |
| 7 | **B-roll people look 55+** (age estimator) | Representation for the audience | `qa/face.py` | 2h | M |
| 8 | **Library gap report**: beats with no clip above 0.25 cosine go to Sunday's batch | Generation follows demand | weekly job | 1h | M |
| 9 | **B-roll attribution**: does an insert at 2–3 s raise hold? | Tells us whether inserts earn their cost | `learning.py` gene `broll:*` | 2h | M |
| 10 | **Motion-energy match** to beat pacing (calm vs active) | Pacing coherence | selector | 2h | L |

---

## B. Assemble

### SL-17 Assembly (`assemble/assembler.py`, `POST /assemble`)
Now: 1080×1920 30 fps H.264 High, AAC 48 kHz, two-pass loudnorm, `+faststart`, word captions, PiP, C2PA, fingerprints, `_clean` mezzanine.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **JSON-schema validation of the manifest** with explicit error codes, before any encode | A cheap fail beats a 90 s encode followed by an obscure ffmpeg error | `assembler.py` + `assemble/manifest.schema.json` | 1h | H |
| 2 | **Snap cut points to word boundaries** from the alignment (no mid-word cuts) | Mid-word cuts sound broken and confuse captions | `assembler.py` | 2h | H |
| 3 | **Kill ffmpeg at 3× the expected duration**, with a structured error | Hung encodes block the queue until the 90-min reaper runs | `assembler.py` subprocess timeout | 1h | H |
| 4 | **Tag colour as bt709, limited range** | Prevents washed-out playback on iOS and after platform transcodes | `assembler.py` encode args | 0.5h | H |
| 5 | **Per-job work-dir quota and cleanup** | One box, 24+ masters a day; full disks fail everything | `assembler.py` | 0.5h | H |
| 6 | **540p preview render for human review**; final encode only after approval | Saves CPU on rejects and speeds review | `/assemble?preview=1` | 3h | M |
| 7 | **Build manifest in a C2PA assertion** (git sha, template version, model ids) | Any post traces back to the exact code and models | `c2pa_sign.py` | 2h | M |
| 8 | **x264 preset by lane** (veryfast for trials, medium for masters) | Trials are throwaway tests; masters live for months | `X264_PRESET` per request | 0.5h | M |
| 9 | **1 s keyframe interval** (`-g 30`) | Clean scrubbing and platform transcodes | encode args | 0.5h | M |
| 10 | **WebVTT sidecar** for YouTube uploads (FB SRT is NEXT50 FB-12) | YouTube indexes caption tracks for search | `assembler.py` output | 1h | M |

### SL-18 Captions burn-in (`assemble/captions.py`)
Now: word-by-word Figtree captions ≥56 px, ≥7:1 contrast, never gray, speech-span aware.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **OCR CER check on each variant's captions** after the hook burn | Variant burns can overlap or clip captions | `qa/ocr.py` | 1h | H |
| 2 | **Each caption chunk on screen for ≥0.7 s** (merge fast words) | Older readers need dwell time | `captions.py` | 0.5h | H |
| 3 | **Never split number + unit or a name** across chunks | "10 / reps" reads wrong | `captions.py` | 0.5h | H |
| 4 | **Digits and units in captions** even when the voice says words | Scan speed | `captions.py` + `display_norm()` | 0.5h | H |
| 5 | **Speaker colour in duo formats** (Chang vs Sun, both never gray, ≥7:1) | Who's talking is otherwise unclear with the sound off | `captions.py` style map | 1h | H |
| 6 | **Highlight the active word with colour and weight**, not colour alone | Colour-blind viewers | `captions.py` | 1h | M |
| 7 | **At most 32 chars per line and 2 lines** | Long lines force eye travel | `captions.py` | 1h | M |
| 8 | **Lead captions by 80 ms** | Reading starts slightly before speech | `captions.py` | 0.5h | M |
| 9 | **Captions move off the face box** dynamically | The face is the retention signal | `layout.py` + `qa/face.py` | 3h | M |
| 10 | **Captions from ASR of the final mix** when audio isn't our TTS (performer or third-party) | The README TODO; alignment only covers our TTS | `qa/asr.py` → `captions.py` | 2h | M |

### SL-19 Loudness
Now: two-pass loudnorm to −14 LUFS / −1.5 dBTP, music muted under speech. Per-platform targets are NEXT50 MOD-24.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Measure true peak again after the AAC encode** | Codecs create inter-sample peaks above the WAV's measured value | `qa/qa.py` on the final file | 0.5h | H |
| 2 | **Re-verify loudness on every variant** after the hook burn and trim | Variants re-encode audio; a trim can change integrated loudness | `variants.py` → `qa` | 0.5h | H |
| 3 | **At most 100 ms of silence before the first word** | Audio should start with frame 1 | `qa/probes.py` | 0.5h | H |
| 4 | **48 kHz end to end** (no resample chain) | Each resample costs quality | `voice.py`, `assembler.py` | 0.5h | H |
| 5 | **Speech-gated loudness measurement** | Quiet tails and silent cards shouldn't skew the target | `assembler.loudnorm` | 1h | M |
| 6 | **Loudness range ≤7 LU for speech** (tighten from 11) | A consistent level for hearing-aid users | `loudnorm(lra=7)` | 0.5h | M |
| 7 | **Noise floor below −60 dBFS in pauses** | Catches TTS hiss | `qa/probes.py` | 0.5h | M |
| 8 | **Mono-compatibility (phase) check** | Phone speakers are often mono | `qa/probes.py` | 0.5h | M |
| 9 | **Store the loudness report per variant** | Lets us correlate audio with retention later | `videos.qa_audio` | 0.5h | L |
| 10 | **Test a +1 LU hook lift** within limits | Perceived punch in the first second; test it, don't assume it | exception lane | 0.5h | L |

### SL-20 AI label and provenance
Now: AI tag on screen, `is_aigc` and `containsSyntheticMedia` forced, C2PA on masters and variants; dev cert held at review.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **`c2patool verify` in QA** (signature plus ingredient chain), not just presence | A present but broken manifest is worth nothing | `qa/qa.py` | 1h | H |
| 2 | **One disclosure-string registry** for the packager, app, DM and email | One wording, one place to change it, one test | `common/disclosure.py` → JSON shared with `app/src/lib/copy.ts` | 1h | H |
| 3 | **Re-burn the on-screen AI tag after a trim** if the cut removed it | Trims can start after the tag's first appearance | `variants.py` | 0.5h | H |
| 4 | **Code invariant: no experiment arm may vary disclosure** | Disclosure is never a test variable | `growth/config.py` validator | 0.5h | H |
| 5 | **Also write the IPTC `digitalsourcetype=trainedAlgorithmicMedia`** in XMP | Some platforms read IPTC as well as C2PA [A] | `c2pa_sign.py` | 1h | M |
| 6 | **Make TSA timestamping mandatory** | Signatures stay valid after the certificate expires | `C2PA_TSA_URL` required in live | 0.5h | M |
| 7 | **AI line in the email footer and app chat header**, tested | The same honesty on every surface | `app/content/lifecycle`, chat UI | 1h | M |
| 8 | **Native-reviewed Spanish disclosure phrases** | Machine translation of a legal-ish line is risky | `disclosure.json` `es` | 1h | M |
| 9 | **Disclosure in alt text and descriptions** for screen readers | The visual tag is invisible to them | `packager.py` | 0.5h | M |
| 10 | **Invisible watermark** (e.g. open-source TrustMark) bound to the manifest | Survives platforms stripping metadata | `c2pa_sign.py` | 6h | L |

### SL-21 Platform cuts (`assemble/variants.py`, `POST /variants`)
Now: hook burn-in per platform, trim, cover, C2PA re-sign; variant roles TEST / PLACEMENT / REMIX (`growth/variants.py`).

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Fan-out isolation**: one platform's variant failing never blocks the others | Today a single failure can hold a whole master's placements | `variants.py` per-platform try; n8n split | 1h | H |
| 2 | **Spec table per platform** (max size, duration, codec), checked before upload | Upload rejects otherwise surface at publish time, too late | `common/config.py` `PLATFORM_SPECS` | 1h | H |
| 3 | **Trims keep the close keyword**, or the variant is re-roled as no-CTA | A cut-down that loses the keyword wastes the comment economy | `variants.py` | 1h | H |
| 4 | **No re-encode when the platform spec equals the master** | Each encode costs quality | `variants.py` | 1h | H |
| 5 | **Deterministic naming** `{page}_{master}_{platform}_{role}_v{n}.mp4` plus sha256 in the DB | The manual fallback and audits need stable names | `variants.py` | 0.5h | H |
| 6 | **Render all platform outputs in one decode** (ffmpeg multi-output) | 3–4× faster variant builds [A] | `variants.py` | 3h | M |
| 7 | **YouTube cut swaps "link in bio" for a related-video cue** | Links aren't clickable on Shorts; NEXT50 TT-1 adds the link | `packager.py` YT close | 1h | M |
| 8 | **Log pHash distance from the master** per variant | Evidence for originality audits | `uniqueness/phash.py` | 0.5h | M |
| 9 | **Variant files expire 30 days after publish**; the mezzanine is kept | Storage hygiene without losing remixability | R2 lifecycle rule | 0.5h | M |
| 10 | **End-screen room check on YT long cuts** (≥25 s, last 20 s free of text) | End screens need the space | `variants.py` | 0.5h | M |

---

## C. Gate

### SL-22 Uniqueness check (`workers/uniqueness/`)
Now: TF-IDF (0.86 page / 0.80 network), MinHash, shingles, pHash, Chromaprint, stagger; same-page derivatives (100X §5.2); pre-flight (NEXT50 MOD-40).

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 ★ | **Check against the competitor corpus** (Yang Mun's 244 posts in `data/posts.*`) | Too close to the competitor is both an originality and a copying risk; the data is already in the repo | `uniqueness/guard.py` `check_external()` | 1.5h | H |
| 2 | **Fail closed** when the sibling store (Supabase) is unreachable in live mode | An outage must not mean "allow everything" | `guard.py` | 0.5h | H |
| 3 | **90-day history index**, not just today's siblings | Re-posting a 6-week-old body on the same page is the commonest repeat | `guard.py` + `assets` query | 2h | H |
| 4 | **Explain the nearest neighbour** (which dimension failed, the closest id, the score) to the reviewer | A reviewer can fix a specific overlap | `/uniqueness/check` response | 1h | H |
| 5 | **Apply the guard to carousels and statics** (pHash per slide) | Graphics are posted too and are trivially duplicated | `guard.py` + `graphics.py` | 1h | H |
| 6 | **Calibrate thresholds with labelled pairs** (humans judge "same post?") → ROC | 0.86 / 0.80 are [A] | `uniqueness/calibrate.py` | 3h | M |
| 7 | **CLIP frame-embedding similarity** | Catches re-shoots of the same composition that pHash misses | `uniqueness/embed.py` | 4h | M |
| 8 | **MinHash LSH index** | Lookup stays fast as the library grows | `guard.py` | 2h | M |
| 9 | **Weekly false-negative audit**: humans judge the 20 most similar allowed pairs | Measures what the guard misses | `/admin/exceptions` | 1h | M |
| 10 | **No two pages use the same music bed on the same day** (Chromaprint) | An audio fingerprint is a cheap duplicate signal | `audiofp.py` | 0.5h | M |

### SL-23 Compliance scan (`compliance/scanner.py`)
Now: blocked_claims, SAFETY §3.1 regexes, anti-evasion normalisation; pass 1 (script) and pass 2 (packaging, transcript, burned text).

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Scan OCR of the actual rendered pixels** on each variant (not only the manifest's burned text) | Catches template bugs and model-rendered text | `qa/ocr.py` → `scanner.scan_text` | 1h | H |
| 2 | **Scan the cover image text** | The grid tile is public copy | same | 0.5h | H |
| 3 | **Scan Page comment replies before sending** (FB replies as the Page, NEXT50 FB-21) | Replies are public claims too | `compliance/api.py` call in the reply path | 1h | H |
| 4 | **Rule coverage test**: every blocked_claims entry has ≥1 positive and ≥1 negative fixture | Untested rules decay | `tests/test_compliance_coverage.py` | 2h | H |
| 5 | **Version every verdict** (scanner version plus rules hash), and rescan the back catalogue when rules change | Old approvals were made under old rules | `compliance_reviews.rules_hash` | 1h | H |
| 6 | **Medication-name lexicon** (top 300 US drugs): any mention goes to human | Drug mentions next to exercise or food are high risk | `compliance/rules.py` | 2h | H |
| 7 | **"Studies show" proximity rule**: needs an evidence id in the same sentence | Vague authority claims are the commonest soft violation | `rules.py` | 2h | M |
| 8 | **Track reviewer overrides per rule**; rewrite rules overridden more than 30% of the time | False positives cost reviewer time and trust | `/admin/exceptions` aggregation | 1h | M |
| 9 | **Before/after imagery detector** (side-by-side body comparisons) | Banned by health rules on Meta [A] | `qa/probes.py` | 3h | M |
| 10 | **Under 200 ms per scan** (compiled regex cache) | Lets DMs and replies call it inline | `scanner.py` | 1h | M |

### SL-24 LLM judge (`compliance/judge.py`, `prompts/03`)
Now: mandatory, temperature 0, confidence floor 0.8, untrusted text tagged as data, fails to human.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Judge golden set** (100 labelled scripts including adversarial ones), run nightly; track precision and recall | We don't know the judge's miss rate | `tests/judge_golden/`; nightly CI with key | 3h | H |
| 2 | **Structured output** (tool-use JSON schema) | Unparsable output currently routes to human, wasting reviewer time | `judge.py` | 1h | H |
| 3 | **Prompt-cache SAFETY and EVIDENCE** | Most judge input is the same every call | `judge.py` `cache_control` | 1h | H |
| 4 | **Rationale must cite rule ids**; an unknown id makes the verdict invalid | Forces grounded verdicts | `judge.py` validator | 1h | H |
| 5 | **Injection suite** (comment-derived ideas carrying "ignore previous…") | Ideas come from public comments | `tests/test_judge_injection.py` | 1h | H |
| 6 | **Pin the model, and re-run the golden set before any change** to `MODEL_JUDGE` | Model swaps silently change policy | CI gate | 0.5h | H |
| 7 | **Batch API for pass 1 on D+2 scripts** | −50% on non-urgent judging | `judge.py` batch path | 1h | H |
| 8 | **Two-sample agreement on borderline cases** (confidence 0.8–0.9): re-run with rules in a different order; disagreement → human [P6] | The hard ~5% is exactly where single LLM verdicts flip | `judge.py` | 2h | M |
| 9 | **Tiering**: Sonnet first, Opus only when Sonnet says not-pass or confidence < 0.9 | Most scripts are clean; pay Opus only for hard ones | `judge.py` | 2h | M |
| 10 | **Drift monitor**: weekly pass rate by pillar; alert on a ±10-point shift | Catches prompt or model drift | weekly readout | 1h | M |

### SL-25 Human review (review app, `v_human_queue`)
Now: full review of masters, diff-only for trials (NEXT50 MOD-38), SLA alert above 2 h (NEXT50 RO-27).

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Reason-code taxonomy** on every reject or fix, fed back to the writer prompt and the scanner | Rejections should teach the system | review app + `exceptions` | 1h | H |
| 2 | **Unreviewed items past their slot are rescheduled**, never posted late | A 9 pm "good morning" is worse than a skip | n8n W4 guard | 1h | H |
| 3 | **Order the queue by slot deadline, then risk** | Clears what's due first | `v_human_queue` ORDER BY | 0.5h | H |
| 4 | **Keyboard-first UI** (A approve / R reject / F fix plus a code); target 20 s per variant | Review is the throughput bottleneck at 24 masters plus trials | `app/src/app/admin/review` | 4h | M |
| 5 | **Phone-friendly review page** | One person can clear the queue anywhere | same, responsive | 3h | M |
| 6 | **Batch-approve green items 10 at a time**, with one random deep check | Throughput without losing a sample | review app | 2h | M |
| 7 | **Platform UI overlay in the preview** (safe zones, captions on) | Reviewers see what viewers will see | review player | 3h | M |
| 8 | **Reviewer calibration**: 10 repeated items a week measure self-agreement | Drift in human judgement is real | `exceptions` | 1h | M |
| 9 | **Two reviewers for each new page's first 7 days** | New pages carry the most account risk | queue rule | 1h | M |
| 10 | **Throughput metric and forecast** (items/hour against tomorrow's volume) | Shows a shortfall before it hits | `/admin/today` | 1h | M |

---

## D. Ship

### SL-26 Scheduling (`tools/posting_rules.py`, W2, `briefs`)
Now: 06:00–21:30 ET envelope, prime slots, trial flags, hashtag caps, top-3 remix in 24 h.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Slot backfill**: when a master fails, promote the next-best approved evergreen into its slot | Empty slots are lost reach | W4 / `claim_next_brief` | 2h | H |
| 2 | **Global "pause all" switch** (breaking tragedy, platform incident) | One click stops every scheduled post | `LAUNCH_MODE=paused` read by W4 and the fallback pack | 1h | H |
| 3 ★ | **ICS export of tomorrow's slots** for people posting by hand | Proxy posters work from a calendar, not a CSV | `tools/posting_rules.py --ics` | 0.5h | H |
| 4 | **Freeze slots within 2 h** (no allocator reshuffle) | Prevents last-minute swaps after review | W2 rule | 0.5h | H |
| 5 | **Idempotent schedule writes** keyed on (page, platform, slot_ts) | Re-runs never double-book | `posts` unique index | 0.5h | H |
| 6 | **Morning schedule diff** (planned vs posted vs failed) | Shows what slipped, every day | digest section | 1h | H |
| 7 | **Constraint solver for slots** (API caps, ≥90 min spacing per page, sibling stagger, prime windows) | Greedy placement breaks as volume grows | `tools/schedule_solve.py` | 4h | M |
| 8 | **±7 min jitter** on slot times | 4 pages posting on the exact minute looks automated | `posting_rules.py` | 0.5h | M |
| 9 | **At most 2 consecutive same-pillar posts per page** | Variety for followers | `posting_rules.py` | 0.5h | M |
| 10 | **Apply the warm-up ramp automatically** from the PIPELINE §5.4 table per account age | The ramp is a document today | `posting_rules.py` `ramp()` | 1h | M |

### SL-27 Posting (W4 Publisher, `packager/fallback.py`)
Now: official API or upload-post with 3× backoff; manual post pack as fallback; publishing gated by `LAUNCH_MODE=live`.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **YouTube quota plan**: 6 uploads per project per day [P2] against 24 needed. File the extension on day 0; until it's granted, post YouTube through upload-post or by hand, and budget `thumbnails.set` (50) and reads (1) | Without this, 75% of YouTube uploads fail with `quotaExceeded` from the 7th upload | W4 quota governor; `docs/platform_reviews/` | 1h + form | H |
| 2 | **TikTok stays manual or draft-inbox until the audit passes** [P3] | Unaudited API posts are private; "success" would mean 0 views | W4 platform switch | 0.5h | H |
| 3 | **Post-publish verification**: read the media back, confirm it's published and public, store the permalink; retry if the container is FAILED | "Accepted" is not "live" | W4 *mark_post_result* | 2h | H |
| 4 | **IG container status poll** (`FINISHED` before `media_publish`) | Publishing an unprocessed container fails intermittently | W4 IG branch | 1h | H |
| 5 | **Before any publish retry, check it isn't already live** | Retries after a timeout are the main double-post cause | W4 | 1h | H |
| 6 | **One publish in flight per account** (lock) | Races cause doubles and spacing breaches | Redis lock | 0.5h | H |
| 7 | **Short-TTL signed R2 URLs** for media fetch | IG needs a public URL; unpublished content shouldn't sit public | `common/storage.py` | 1h | H |
| 8 | **Publishing heartbeat**: alert after 3 h with no success during the posting window | Silent failure is the worst failure | W10 | 0.5h | H |
| 9 | **Official API or upload-post only; no headless-browser posting**, ever | Browser automation is an account-integrity risk | policy + code review rule | 0h | H |
| 10 | **No caption edits in the first hour** after publish [A] | Unknown effect on distribution; don't risk it | W4 / review app lock | 0.5h | L |

---

## E. Learn

### SL-28 Metrics pulls per horizon (W5, `growth/adapters.py`, `snapshots.py`)
Now: snapshots at 1/3/6/24/72 h and 7 d; live fetch off by default; fixture mode.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 ★ | **Manual CSV import** in the canonical capture schema (for proxy-posted and API-less platforms) | Launch posts go out by hand; without this, days 1–7 teach the engine nothing | `growth/adapters.py` `normalize_manual_csv()` + `/growth/metrics/normalize` | 2h | H |
| 2 | **Archive raw payloads** (JSON to R2) | Re-parse history when metric definitions change (100X Holes #13) | `snapshots.py` | 1h | H |
| 3 | **Monotonic sanity check**: cumulative counters never decrease (log and drop the bad read) | Bad reads corrupt baselines | `snapshots.py` | 0.5h | H |
| 4 | **Late-read flag** (`late=true`, real age) with interpolation in scoring | Missed horizons happen; treat them honestly | `snapshots.py` + `scorecard.py` | 1h | H |
| 5 | **Batch IDs per call** (YouTube `videos.list` takes 50 IDs for 1 unit [P2]; Graph batch requests) | Quota and rate-limit headroom | `adapters.py` | 1h | H |
| 6 | **Spread pulls across the hour** by page hash | Avoids rate-limit bursts | W5 schedule | 0.5h | M |
| 7 | **Comment text pulls at 1 h and 24 h** | Feeds comment mining with fresh questions | `adapters.py` | 1h | M |
| 8 | **Hourly follower snapshot per page** | Attributes follower gains to posts | `snapshots.py` | 0.5h | M |
| 9 | **Profile visits and link clicks per post** where exposed | Intent signals between view and DM | `adapters.py` | 1h | M |
| 10 | **API-call accounting against quota** per platform per day | Know the ceiling before you hit it | cost ledger | 0.5h | M |

### SL-29 Scoring (`growth/scorecard.py`, `scoring.py`, `baselines.py`)
Now: component scores with empirical-Bayes shrinkage, composite weighted toward conversion, WINNER/PROMISING/NORMAL/LOSER.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Separate baselines for Trial Reels and feed posts** | Non-follower and follower audiences behave differently; mixing them biases both | `baselines.py` key + `surface` | 1h | H |
| 2 | **Stamp every score row with a config hash**, and recompute on change | Scores must be comparable over time | `post_scores_components.cfg_hash` | 1h | H |
| 3 | **Winsorise component z at ±4** | One viral post shouldn't wreck a page's baseline | `baselines.py` | 0.5h | H |
| 4 | **Edge-case unit tests** (0 views, all components missing, a single post) | Edge cases are where scoring breaks | `tests/test_growth_scorecard.py` | 1h | H |
| 5 | **Freeze scores at 7 d** | Later rewrites confuse learning | `scorecard.py` | 0.5h | H |
| 6 | **Phase-aware composite weights** (runway: reach and follows; launch: conversion) | The objective changes at D0 | `growth/config.py` `phase` | 1h | M |
| 7 | **Credit conversions for 7 days via `pid`**, updating the 7 d read | Buyers lag views | `scorecard.py` | 1h | M |
| 8 | **Plain-English explanation per post** ("hook 82, body 40: drop at 0:14") | Faster human decisions | `/admin/today` | 1h | M |
| 9 | **Bootstrap CI on the composite** | Shows when WINNER is noise | `scorecard.py` | 2h | M |
| 10 | **Composite → expected $ per 1K views** | Feeds dollar-EV allocation (SL-05.7) | `scorecard.py` + offers metrics | 2h | M |

### SL-30 Graduation (Trial → feed)
Now: one `SS_PERFORMANCE` trial per (page, body); the rest MANUAL. NEXT50 IG-2, IG-20, IG-24, IG-31 and LL-10 cover the policy.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Explicit graduation rule in config**: LCB(hold3s) > page median AND shares/reach ≥ page p60 at ≥1,000 non-follower plays | Today graduation is ad hoc | `growth/config.py` `GRADUATION` | 1h | H |
| 2 | **Evening graduation report**: candidates with a one-click "graduate" for the human | Graduation is manual while the API path is uncertain | `growth/api.py` `/growth/graduation/candidates` | 1h | H |
| 3 | **Reserve one feed slot per page per day** for graduates | A graduate shouldn't fight for a slot | `posting_rules.py` | 1h | H |
| 4 | **Re-run compliance pass 2 on graduation** | The caption may have been edited (NEXT50 IG-20) | `/package` re-call | 0.5h | H |
| 5 | **Close trials at 72 h** and release their slot | No zombie tests | `variants.py` | 0.5h | H |
| 6 | **At most 2 graduates per page per day** | Protects the feed cadence | config | 0.5h | M |
| 7 | **Audit false graduations**: graduates under the feed baseline feed a threshold refit | Graduation should keep getting better | `learning.py` | 1h | M |
| 8 | **Graduates feed the weekly email's "best of the week"** | Owned reach for proven content | lifecycle `daily_coach` | 1h | M |
| 9 | **Graduates become boost candidates only after the $30K MRR gate** (canon 5) | Keeps the governor consistent | `adpolicy.py` | 0.5h | H |
| 10 | **Graduation event → digest line** | Visibility | `learning.post_readout` | 0.5h | L |

### SL-31 Remix (`growth/actions.py`, W7)
Now: top 3 per page remixed within 24 h; ≥3 cheap dimensions changed including a new voice take; 1 for YouTube.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Typed remix brief** with explicit `keep` (grammar, beat 2) and `change` (set, prop, hook text) fields | The writer knows exactly what to preserve | `actions.py` → `briefs.remix_spec` | 1h | H |
| 2 | **Lineage tree** (`parent_id`, generation), max depth 3 | Stops remixes of remixes drifting into copies | `remix_jobs` | 1h | H |
| 3 | **Remix cost floor**: reuse voice for unchanged lines, regenerate only changed shots | Remixes should cost a fraction of a master | n8n + SL-15 | 2h | H |
| 4 | **Remix only wins that came from non-followers** | Follower spikes don't predict new-audience reach | `actions.py` rule | 0.5h | M |
| 5 | **Rescue remix**: a strong body with a weak hook gets a new hook only | Saves good bodies cheaply | `actions.py` | 1h | M |
| 6 | **Stop a family after 2 remixes underperform the parent by more than 30%** | Diminishing returns | `actions.py` | 0.5h | M |
| 7 | **Remixes take at most 30% of daily renders** | Protects exploration | allocator budget | 0.5h | M |
| 8 | **"Part 2" remix when the parent's comments ask a follow-up** | A sequel format with built-in demand | `actions.py` + comment mining | 1h | M |
| 9 | **Remix SLA measured** (winner flag → remix live) | 24 h is the rule; measure it | digest | 0.5h | M |
| 10 | **Remixes rank below fresh tests** when the exploration floor is at risk | The floor is canon | allocator | 0.5h | M |

### SL-32 Allocator (`growth/allocator.py`)
Now: Thompson sampling over pillar × grammar × format × speaker × length, hook-family arm, 20% floor.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Supply-aware substitution**: if approved inventory lacks the sampled arm, take the nearest arm and log the shortfall to ideation | The bandit can't allocate what doesn't exist | `allocator.py` + `v_script_runway` | 1h | H |
| 2 | **Seeded RNG with the seed logged** | Reproducible plans for debugging | `allocator.py` | 0.5h | H |
| 3 | **Constraint layer** (uniqueness, pillar mix, character mix); resample if infeasible | Plans must be postable as written | `allocator.py` | 2h | M |
| 4 | **Explore by information gain** (highest posterior variance) instead of uniformly | Learns faster at the same 20% | `allocator.py` explore branch | 2h | M |
| 5 | **Budget in dollars, not slots**: pick cheaper formats when the day's budget is tight | Canon 5's 25%-of-MRR cap is in dollars | `allocator.py` + cost ledger | 2h | M |
| 6 | **Retire arms after 30 days below p20 with n ≥ 20** | Stops paying for proven losers | `allocator.py` | 0.5h | M |
| 7 | **Cap the conversion reward per post** | One buyer shouldn't crown an arm | `scoring.py` | 0.5h | M |
| 8 | **Half-life per platform** (TikTok shorter than Facebook) | Platforms forget at different speeds | `growth/config.py` | 0.5h | M |
| 9 | **A "why" per slot** ("exploit IF_EVERY × F02, posterior 0.61") | Humans can sanity-check the plan | `/growth/allocate` response | 1h | M |
| 10 | **Allocator health panel** (explore/exploit share, a regret proxy) | Shows when learning stalls | `/admin/today` | 1h | M |

### SL-33 Gate refit (`tools/refit_gate.py`)
Now: weekly Pearson-based weight blend toward the target, λ = n/(n+200) capped at 0.5, max 30% move, dry run by default.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Out-of-sample check**: fit on 80%, report held-out correlation, refuse `--apply` if it doesn't improve | Stops overfitting to one week | `refit_gate.py` | 1h | H |
| 2 | **Minimum n per row** (rows with fewer than 30 observations keep their prior) | Small rows swing on noise | `refit_gate.py` | 0.5h | H |
| 3 | **Stamp the rubric version** on every script score | Know which gate admitted which script | `tools/virality.py` | 0.5h | H |
| 4 | **Keep 8 weight files; one-command rollback** | A bad refit is undone in seconds | `refit_gate.py --rollback` | 0.5h | H |
| 5 | **`--apply` requires an exceptions approval entry** | A human signs every gate change | `refit_gate.py` + exceptions | 1h | M |
| 6 | **Partial correlation controlling for page and platform** | Raw Pearson is confounded by account strength | `refit_gate.py` | 2h | M |
| 7 | **Refit the threshold too** (60 → whatever maximises expected composite × volume) | Weights move but the bar never does | `refit_gate.py --threshold` | 2h | M |
| 8 | **Saturation detector**: rows where 90% of scripts get full points get a stricter criterion proposed | A row that everyone passes carries no information | report section | 1h | M |
| 9 | **Quartile bins per feature** to catch inverted-U effects (length) | Linear r misses them | report | 1h | M |
| 10 | **Refit trial and feed reads separately** | Different audiences, different drivers | `--surface` flag | 1h | M |

---

## F. Audience and money

### SL-34 Comment mining (W1 input, W6)
Now: W1 reads 72 h of own comments; crisis keywords go to a human in DMs. NEXT50 HK-1, LL-4, LL-23 and LL-38 cover the uses of comments.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Scrub PII** (phones, emails, addresses) before storage and before any LLM call | Older commenters overshare; we shouldn't hold it | `growth/adapters.py` + `compliance/textnorm.py` `scrub_pii()` | 1h | H |
| 2 | **Crisis and medical-emergency lexicon on public comments**, not only DMs, routed to a human | "I fell and can't get up" can appear under a post | W6 sweep + `app/src/lib/safety` classifier | 1h | H |
| 3 | **Question detector** (interrogatives plus "how/can/should") to separate questions from praise | Questions are the raw material for hooks and FAQs | `growth/comments.py` (new) | 1h | H |
| 4 | **Public sources only for competitor comments**, per platform terms | Keeps mining defensible | W1 config; doc note | 0.5h | H |
| 5 | **Local embedding clustering** (MiniLM on CPU), daily | No per-comment LLM cost at volume | `growth/comments.py` | 3h | M |
| 6 | **Objection tags** (price / trust / "is this AI" / health) | Feeds DM copy, FAQs and the trust episodes | `comments.py` | 1h | M |
| 7 | **Quote consent rule**: quote a comment's text in video with first name only, no photo or surname | Respect, and fewer complaints | `prompts/02` rule; SAFETY note | 0.5h | M |
| 8 | **Discount bot-like comments** in the conversation score | Fake engagement inflates scorecards | `scorecard.py` filter | 1h | M |
| 9 | **Spanish comment share per page** | Data for the localisation trigger | `comments.py` | 0.5h | M |
| 10 | **Evidence-gap queue**: questions with no EVIDENCE.md entry go to research | Demand-led evidence building | `/admin/exceptions` `evidence_gap` | 1h | M |

### SL-35 DM routing (`workers/dm/bot.py`, `sender.py`, `routing.py`)
Now: signed webhook, 14 flows, bot disclosure, `HUMAN_AGENT` path, intent → offer routing, sends off until app review.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Dedupe on event id** (`mid`) | Meta re-delivers webhooks; duplicates mean double DMs | `bot.py` + Redis set (TTL 48 h) | 1h | H |
| 2 | **Acknowledge fast, process async** (enqueue, return 200) | Slow handlers trigger re-deliveries and backlogs at launch spikes | `dm/api.py` + Redis queue | 2h | H |
| 3 | **Track the 24 h window per user** (`window_opened_at`); refuse sends outside policy | Policy breaches cost the messaging permission | `sender.py` | 2h | H |
| 4 | **Honour STOP / unsubscribe / "leave me alone"** immediately and suppress | Basic consent; older users say it in words | `bot.py` `_global` flow | 0.5h | H |
| 5 | **Per-user rate limit**: at most 3 automated messages per hour | Prevents loops and spam perception | `sender.py` | 0.5h | H |
| 6 | **Signed link tokens per thread** (`pid` + uid) | Checkout attributes to the DM thread and keyword | `sender.py` + `app/src/lib/quoteSig.ts` pattern | 2h | H |
| 7 | **Dead-letter queue for send failures**, retried only inside the window | No lost replies, no late ones | `sender.py` | 1h | H |
| 8 | **Unknown-keyword handler**: a 3-button menu, not silence | Typos and free text are common | `_global.json` | 1h | M |
| 9 | **Abuse or harassment detection**: stop automation and hide | Protects the page and the bot | `bot.py` + scanner | 1h | M |
| 10 | **Replay tool**: run recorded threads through a new flow version offline | Safe flow changes | `dm/replay.py` (new) | 2h | M |

### SL-36 Waitlist (`app` `/waitlist`, consent log, launch cron)
Now: waitlist with confirm and unsubscribe, consent log, honeypot/bot checks, launch cron.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Normalise and dedupe emails** (case, whitespace, Gmail dots and +tags for the dedupe key only) | Double rows double the launch sends | `app/src/lib/waitlist.ts` | 1h | H |
| 2 | **Throttle the launch-day send** (e.g. 2,000/h, Gmail and Yahoo spread) | A cold domain blasting a list is how it gets junked [P5] | `/api/cron/launch` | 1h | H |
| 3 | **Warm up the sending domain** over the 7 days before launch (confirm emails, small sends) | Same reason | ops; ESP settings | 0.5h | H |
| 4 | **Nightly encrypted export of the list to R2** | The list is the asset; keep it outside one vendor | cron + `common/storage.py` | 1h | H |
| 5 | **Block disposable email domains** | Junk inflates the list and the bounce rate | `waitlist.ts` | 0.5h | M |
| 6 | **Confirm-email resend button**; 72 h link expiry | Older users lose emails; let them retry | `/waitlist/confirm` | 1h | M |
| 7 | **The confirm page shows the next step at once** (watch Day 1 now) | Value right after the opt-in raises later opens | `waitlist/page.tsx` | 1h | M |
| 8 | **Mobile Lighthouse ≥90**, LCP < 2.5 s on 4G | Older phones, rural connections (NEXT50 X-H32) | `app` perf budget in CI | 2h | M |
| 9 | **Tap targets ≥48 px, 18 px base font** on the form | Tremor and vision | `waitlist/page.tsx` | 0.5h | M |
| 10 | **Waitlist health by source** (confirm rate, bounces, complaints) | Finds bad sources fast | `/admin/today` | 1h | M |

### SL-37 Email (`app/src/lib/lifecycle/engine.ts`, `notify.ts`, 12 sequences)
Now: 12 sequences with 29 steps, unsubscribe route, `List-Unsubscribe` present, outbox; needs an ESP key.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Contract test**: every marketing send carries `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click`, and unsubscribe takes effect within 48 h [P5] | Mandatory for Gmail and Yahoo; a regression means rejections | `app` Vitest on `notify.ts` | 0.5h | H |
| 2 | **Auto-pause marketing at 0.2% complaints** (Google and Yahoo cap at 0.3% [P5]) | Leaves a margin before the hard limit | ESP webhook → `lifecycle` flag | 1h | H |
| 3 | **Separate subdomains** for transactional and marketing mail | A marketing complaint spike can't block receipts or magic links | DNS + `notify.ts` from-address | 0.5h | H |
| 4 | **Shared suppression list** from bounce and complaint webhooks, across all senders | One unsubscribe, everywhere | `app/src/lib/notify.ts` | 1h | H |
| 5 | **Idempotency on (contact, sequence, step)** | Cron retries must not double-send | `lifecycle/engine.ts` unique key | 0.5h | H |
| 6 | **At most one marketing email per contact per day** across sequences | Overlapping sequences pile up | `engine.ts` arbiter | 1h | H |
| 7 | **Snapshot tests of rendered templates** (never gray, ≥18 px body; NEXT50 AO-18 defines the template) | Template regressions are invisible until sent | `app` Vitest | 1h | M |
| 8 | **Wrapped links with `pid`/UTM and click logs** | Revenue attribution per email | `notify.ts` | 1h | M |
| 9 | **Seed-list inbox placement test** (10 seeds) before the launch send | Catches spam-folder placement before 10K sends | ops checklist | 1h | M |
| 10 | **Per-domain pacing** (Gmail / Yahoo / Outlook) | Smooths reputation | ESP settings | 0.5h | M |

### SL-38 Shopify provisioning (`shopify/src/provision.ts`, dry run by default)
Now: 13 products, collections, selling plans, discounts, metafields, webhooks, theme; K9SUPPS on a hard deny list.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Nightly drift detection** (live store vs `catalog.ts`; alert on any difference) | Manual admin edits silently break prices and plans | `shopify/src/provision.ts --check` cron | 2h | H |
| 2 | **Daily founding-seat reconciliation**: inventory against the seat ledger | The founding cap is a public promise (AUDIT C-level history) | `seatLedger.ts` job | 1h | H |
| 3 | **Duplicate the live theme** before every theme publish | One-click rollback | `provision.ts` theme step | 0.5h | H |
| 4 | **Startup scope check**: refuse if the token has more scopes than needed or the domain isn't allowlisted | Least privilege, plus the K9SUPPS guard in depth | `client.ts` | 1h | H |
| 5 | **GraphQL cost throttling** (read `throttleStatus`, back off) | Bulk provisioning hits cost limits | `client.ts` | 1h | H |
| 6 | **Selling-plan end-to-end test** in a dev store (create, renew via test clock if available, cancel) | Subscriptions are the MRR; test the real path | `shopify/tests/e2e` | 3h | M |
| 7 | **Bogus-gateway test orders** in staging for every SKU | Money QA per product, not just the hero | `shopify/tests` | 1h | M |
| 8 | **Versioned metafield schema** | Theme and app read them; changes must be coordinated | `operations.ts` | 1h | M |
| 9 | **Provision log → exceptions** with a diff summary | An audit trail for store changes | `provision.ts` | 0.5h | M |
| 10 | **Shopify API version upgrade calendar** (quarterly) with a contract-test run | Version sunsets break webhooks and queries | `docs/` + CI | 0.5h | M |

### SL-39 Webhooks (Shopify → `app/src/app/api/webhooks/shopify`, `shopifyWebhook.ts`)
Now: HMAC verification, webhook-id dedupe, handlers for orders/paid (including renewals), refunds, cancels, inventory, customers.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Respond 200 immediately and process async** (outbox/queue) | Slow handlers fail deliveries; 19 consecutive failures delete the subscription [P1] | `route.ts` → queue | 2h | H |
| 2 | **Reconciliation poller every 15 min**: orders and subscription contracts updated since the cursor | Catches anything the webhooks missed | `/api/cron/reconcile` (new) | 3h | H |
| 3 | **Hourly subscription-list check**; re-register and alert if any topic is missing | The deletion in [P1] is otherwise silent | cron + `shopify/src/webhooks.ts` | 1h | H |
| 4 | **Order guard**: ignore events older than the stored `updated_at` | Out-of-order deliveries can revoke a renewed member | `shopifyWebhook.ts` | 1h | H |
| 5 | **Serialise per customer** | Parallel events for one customer race on entitlements | queue partition key | 1h | H |
| 6 | **Dead-letter table and admin replay button** | Fix and replay without hand edits | `/admin/exceptions` action | 2h | H |
| 7 | **Contract tests on recorded payloads** for each topic at the pinned API version | Catches schema changes on upgrade | `app` Vitest fixtures | 1h | H |
| 8 | **p95 handler latency and failure rate on `/admin/today`** | Shows trouble before Shopify stops delivering | `kpis.ts` | 1h | M |
| 9 | **Rotate webhook secrets per environment**, with a written procedure | Staging and production must never share secrets | `deploy/secrets.example.env` doc | 0.5h | M |
| 10 | **Alert on a gap in `orders/paid`** during expected traffic (e.g. 2 h with none after launch) | A silent pipe looks like low sales | W10 | 0.5h | M |

### SL-40 Entitlement (`app/src/lib/entitlement.ts`, `billing/`)
Now: webhooks provision and revoke access in Supabase; gifts, partner seat, founding price, cancel flow.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Daily reconciliation**: Shopify active contracts vs app entitlements; mismatches go to exceptions | The strongest guard against paid-but-locked-out and free-riding | `/api/cron/reconcile` | 2h | H |
| 2 | **Property-based test** over random event sequences (pay, renew, fail, refund, cancel, gift, partner) | The governor has 3,000-state tests; money access deserves the same | `app` fast-check suite | 3h | H |
| 3 | **Derive entitlement from the event log**, with a nightly recompute and diff | Current state stays explainable and repairable | `entitlement.ts` | 3h | H |
| 4 | **Refund revokes immediately; a chargeback revokes and flags** | Clear money rules | `billing/actions.ts` | 0.5h | H |
| 5 | **Founding price lock survives pause and resume** | A broken promise is a refund and a complaint | `billing/planChange.ts` test | 1h | H |
| 6 | **Partner seat follows the primary** (auto-revoke on cancel) | Prevents orphaned free access | `members.ts` | 1h | H |
| 7 | **"Why does X have access?" explainer** in admin, from the event log | Support speed | `/admin` | 2h | M |
| 8 | **Explicit grace period on failed payment** (e.g. 3 days), with a banner | Older users fix cards slowly; don't lock them out at once | `billing/active.ts` | 1h | M |
| 9 | **Short-TTL signed entitlement cookie** (5 min), invalidated on revoke | Fewer DB reads at launch spikes | `auth/server.ts` | 2h | M |
| 10 | **Fail-soft for 15 min on DB errors for active members** (logged) | An outage shouldn't lock paying users out | `entitlement.ts` | 1h | M |

---

## G. Run

### SL-41 Exceptions (`common/exceptions.py`, `/admin/exceptions`)
Now: an append-only API for every human decision; feeds the digest.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Wire n8n's error workflow into exceptions** (dead-letter → row) | Failures now go to Slack only and get lost | n8n *Error handler* → `/exceptions` | 1h | H |
| 2 | **Aggregate repeats** (same type and fingerprint → one row with a count) | Noise hides the real fires | `exceptions.py` | 1h | H |
| 3 | **Slack for sev1 only**; everything else to the digest | Alert fatigue kills response | router | 0.5h | H |
| 4 | **Test that every exception type is in the enum** | Prevents unroutable types | `tests/` | 0.5h | H |
| 5 | **Severity levels with an SLA per type** | Not every exception is equal | `exceptions.py` | 1h | M |
| 6 | **Owner and acknowledge fields** | Someone owns each fire | schema | 1h | M |
| 7 | **Auto-resolve when the condition clears** | Keeps the queue honest | `exceptions.py` | 1h | M |
| 8 | **A runbook link per type** | Faster fixes at 2 am | `LAUNCH_RUNBOOK.md` anchors | 1h | M |
| 9 | **Exception budget**: more than 20 open sev2 freezes new pages and new flows | Stability before growth | config + digest | 0.5h | M |
| 10 | **Weekly CSV export** for postmortems | Patterns over time | cron | 0.5h | L |

### SL-42 Digest (07:00, `app/src/lib/digest.ts`, `/api/cron/digest`)
Now: 7 am digest from exceptions and KPIs; weekly growth readout.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Dead man's switch**: alert if the digest didn't send by 07:15 | A missing digest is itself a signal | W10 | 0.5h | H |
| 2 | **Freshness stamp per section** | Stale data looks current | `digest.ts` | 0.5h | H |
| 3 | **Canon-5 cost line**: all-in cost as % of MRR against the 25% cap | The canon's main financial guard | `digest.ts` + cost ledger | 0.5h | H |
| 4 | **Mobile-first HTML**, ≥16 px, high contrast, no gray | Read on a phone at 7 am | `digest.ts` template | 0.5h | H |
| 5 | **Fixed one-screen layout**: reach, owned contacts, MRR, cost, top 3 winners, top 3 fires | Same place, every day | `digest.ts` | 2h | M |
| 6 | **Delta vs 7-day average** on each number | Trend over level | `digest.ts` | 1h | M |
| 7 | **One-click actions** (approve graduates, open the review queue) | Turns reading into doing | signed admin links | 2h | M |
| 8 | **Pace line**: MRR vs the projection CSV's path to $100K by day 45 | Ahead or behind the plan, daily | `data/projection_aggressive_central.csv` | 1h | M |
| 9 | **"Decisions needed" count with deadlines** | Surfaces blocked work | exceptions query | 0.5h | M |
| 10 | **Slack copy of the digest** as well as email | Redundancy | `notify.ts` | 0.5h | L |

### SL-43 n8n orchestration (`n8n_core_workflow.json` 109 nodes, growth 44)
Now: queue mode, prepared JSON in `deploy/n8n/prepared/`, gated import, error workflow with a dead-letter queue.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Check `LAUNCH_MODE` at the head of every send branch** (DM, email, publish), not only publishing | One switch should stop every outbound action | n8n IF nodes; `patch_workflow.py` | 1h | H |
| 2 | **Pin the n8n version** in compose; upgrade through local staging | n8n upgrades change node behaviour | `deploy/docker-compose.yml` | 0.5h | H |
| 3 | **Prune execution data** (max age 7 d) | Postgres bloat at 24+ masters a day | n8n env `EXECUTIONS_DATA_PRUNE` | 0.5h | H |
| 4 | **Lint: no inline keys**; credentials only from the store | Leaks via exported JSON | `deploy/scripts/check_secrets.py` | 1h | H |
| 5 | **The error workflow also covers the growth workflow** | Growth failures are silent today | growth JSON `errorWorkflow` | 0.5h | H |
| 6 | **Poll-with-backoff sub-workflow** replacing the fixed 20/45/60 s waits | Wall time and execution count | sub-workflow | 2h | M |
| 7 | **Separate worker pools** for core and growth | A metrics backlog shouldn't starve production | queue-mode config | 1h | M |
| 8 | **One sub-workflow per provider** (fal, WaveSpeed, Higgsfield, ElevenLabs) | Swap models without touching core | n8n | 3h | M |
| 9 | **Move logic out of Code nodes into worker endpoints** | Testable in pytest, versioned in git | ongoing | n/a | M |
| 10 | **Dry-run diff on import** (nodes added, removed, changed) before overwriting production | Avoids clobbering hotfixes | `deploy/scripts/n8n_import.py --diff` | 1h | M |

### SL-44 Retries
Now: HTTP retry 3× / 5 s, requeue up to 3, circuit breaker on more than 20% failures, idempotent renders and posts.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Retry table by error class** (4xx: no retry except 429; 5xx and timeouts: exponential backoff with jitter) | Retrying a 400 wastes money and time | `common/` helper + n8n settings | 1h | H |
| 2 | **Honour `Retry-After`** | Providers say when; listen | same | 0.5h | H |
| 3 | **Poison detection**: the same payload failing 3× goes to dead-letter with no further retries | Ends infinite loops | n8n error workflow | 0.5h | H |
| 4 | **Retry budget in dollars per brief** | Retries are the hidden cost line | cost ledger check | 1h | H |
| 5 | **Retries on publish verify first** (SL-27.5) | Double posts are an account-health problem | W4 | (in SL-27) | H |
| 6 | **Per-provider concurrency semaphore** | Prevents retry storms after an outage | Redis semaphore | 1h | M |
| 7 | **Half-open circuit with one canary job** before a full revert | A fast, safe recovery | W10 | 1h | M |
| 8 | **Repair prompt for bad JSON** on a cheap model before regenerating | ~10× cheaper than a full regen | n8n *Parse* nodes | 1h | M |
| 9 | **Retry counts per provider per day** in the ledger | Shows which vendor is flaky | cost ledger | 0.5h | M |
| 10 | **Chaos test**: inject 500s and timeouts into mocked providers in CI | Proves the retry paths | `workers/tests` | 2h | M |

### SL-45 Cost ledger
Now: render costs are modelled (`tools/build_costs.py`, COSTS.md); W10 sends a daily cost report; nothing records per-call spend.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Append-only `cost_events` table** (provider, model, unit, qty, unit_price, brief/variant id, attempt) | Canon 5's 25%-of-MRR cap can't be enforced without real spend data | `schema_growth.sql` + `common/costs.py` | 2h | H |
| 2 | **One versioned price table** (JSON) from PIPELINE §1.3 | Prices change; one place to update them | `data/prices.json` | 1h | H |
| 3 | **Log token usage from every Anthropic response** per prompt version | LLM cost per stage and per prompt | n8n parse nodes → ledger | 1h | H |
| 4 | **Hard daily caps per provider** | A runaway loop can't drain a vendor balance | `claim_next_brief` + ledger | 1h | H |
| 5 | **Cost per published post and per WINNER** | The real unit economics of the engine | view `v_cost_per_winner` | 1h | H |
| 6 | **Waste %**: spend on failed or abandoned jobs | Targets retake and QA work | view | 0.5h | H |
| 7 | **Daily 25%-of-MRR guard** with an alert | Canon 5 | digest + W10 | 1h | H |
| 8 | **Forecast tomorrow's spend from the slot plan** before render starts | Approve the budget, not the bill | `/growth/allocate` + prices | 1h | M |
| 9 | **Monthly invoice reconciliation** (CSV import) | The ledger has to match reality | `tools/reconcile_costs.py` | 2h | M |
| 10 | **Unit economics per page** (cost vs owned contacts vs revenue) | Decides which pages scale | view | 2h | M |

### SL-46 Backups
Now: PIPELINE §5.6 says Supabase daily backups plus a weekly `pg_dump` to R2; nothing in the repo runs the dump, and there is no backup heartbeat.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Nightly `pg_dump` to R2 with 30-day retention** (not weekly) | Supabase Pro keeps only 7 days of daily backups [P4]; a weekly dump loses up to 7 days | `deploy/scripts/backup.sh` + cron | 1h, ~$1/mo | H |
| 2 | **Encrypt backups** (age) with the key held offline | The dumps contain member PII | `backup.sh` | 0.5h | H |
| 3 | **Nightly n8n export** of workflows and encrypted credentials | n8n is the factory's brain | `backup.sh` | 0.5h | H |
| 4 | **Weekly Shopify export** (customers, orders, contracts) to R2 | Vendor-independent copy of the money data | cron script | 1h | H |
| 5 | **Daily ESP list export** | The owned list must survive an ESP lockout | cron | 0.5h | H |
| 6 | **Backup heartbeat in the digest** (last success, size) | A backup that silently stopped is the common failure | digest | 0.5h | H |
| 7 | **R2 versioning and lifecycle** for masters | Protects against accidental deletes | R2 settings | 0.5h | M |
| 8 | **PITR add-on once MRR passes a threshold** (RPO 2 min [P4]) | Money data deserves minutes, not a day | decision gate | 0.5h | M |
| 9 | **Written RTO/RPO targets** (now: RPO 24 h, RTO 4 h) | Sets expectations and drills | `deploy/README.md` | 0.5h | M |
| 10 | **Mirror the content repo to a second remote** | A single GitHub account is a single point of failure | ops | 0.5h | M |

### SL-47 Secrets
Now: `check_secrets.py`, Vault for tokens, fail-closed worker auth, 90-day rotation (NEXT50 RO-13).

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 ★ | **Secret scan of the repo and its history** (gitleaks) before any push, then in CI | The repo has many keyed integrations, and nothing scans for leaks today | `.github/workflows/ci.yml` step | 0.5h | H |
| 2 | **Build-time test that no service key reaches the browser bundle** | One leaked Supabase service key bypasses all RLS | `app` build check (grep `.next/static`) | 0.5h | H |
| 3 | **Log scrubber** for token-shaped strings | Tokens in logs are the usual leak | `common/errors.py` + app logger | 1h | H |
| 4 | **Secret inventory** (name, owner, scope, expiry, rotation date; no values) | You can't rotate what you can't list | `deploy/SECRETS_INVENTORY.md` | 0.5h | H |
| 5 | **`.env` mode 600 on the box, never baked into image layers** | Image pulls shouldn't carry keys | `Dockerfile` + cloud-init | 0.5h | H |
| 6 | **Distinct webhook secrets per environment** | Staging can never sign production events | env files | 0.5h | H |
| 7 | **Separate Anthropic keys per workflow** (writer, judge, chat) | Smaller blast radius and per-stage spend | env + n8n credentials | 0.5h | M |
| 8 | **Exclude `tools/gpt_bridge.py` from the production image** | A dev-only external-AI tool has no place in production | `.dockerignore` | 0.5h | M |
| 9 | **Presigned R2 URLs** instead of a public bucket for unpublished media | Pre-publication content stays private | `common/storage.py` | 1h | M |
| 10 | **Break-glass procedure** (who, where, how), with 1Password sharing | 2 am recovery without guesswork | `deploy/README.md` | 0.5h | M |

### SL-48 CI (`.github/workflows/ci.yml`, `workers-ci.yml`)
Now: two workflows; ≈1,387 tests across suites; screenshot contrast checks.

| # | What | Why | Where | Cost | Conf |
|---|---|---|---|---|---|
| 1 | **Required checks on main**: workers-fast, app unit, shopify check, secret scan | Nothing merges red | branch protection | 0.5h | H |
| 2 | **Doc-number consistency test**: counts quoted in docs (rows, scripts, hooks, nodes) must match the data files | Would have caught NEXT50 X-H2 (21,756 vs 13,800) | `tools/test_doc_numbers.py` | 1h | H |
| 3 | **Docker build plus `/health` smoke** in CI | A broken image is found before deploy day | `workers-ci.yml` | 1h | H |
| 4 | **No auto-deploy from main** before go-live; deploy on tag only | Accidental production changes during launch week | workflow `on: push: tags` | 0.5h | H |
| 5 | **Run SQL migrations and RLS verify in CI** (`make test-sql` against a Postgres service) | RLS regressions are the worst data leak | `workers-ci.yml` service | 1h | H |
| 6 | **Nightly full suite**, including rendering and the judge golden set | The fast suite skips rendering | scheduled workflow | 1h | M |
| 7 | **Dependency caching and sharding** to keep CI under 10 min | Slow CI gets skipped | workflows | 1h | M |
| 8 | **Weekly dependency audit** (pip-audit, npm audit) | Known CVEs in a money app | scheduled workflow | 0.5h | M |
| 9 | **Coverage floor** on `growth/` and `billing/` (≥85%) | The two places a bug costs money | pytest-cov / Vitest | 1h | M |
| 10 | **Pre-commit hooks** (ruff, prettier) | Cheap hygiene | `.pre-commit-config.yaml` | 0.5h | L |

---

## H. The 15 biggest items in this file

| Rank | ID | Item | Why it's on top |
|---|---|---|---|
| 1 | SL-27.1 | YouTube quota plan (6 uploads per project per day vs 24 needed) | Hard ceiling on a primary platform [P2] |
| 2 | SL-39.2/3 | Shopify reconciliation poller plus subscription check | Silent loss of member provisioning [P1] |
| 3 | SL-28.1 | Manual metrics CSV import | Launch posts are manual; without it the first week teaches nothing |
| 4 | SL-15.1 | Make `rerender_shots` real | Biggest render-waste leak; PIPELINE marks it [A] |
| 5 | SL-01.1 | Inventory-aware ideation | 87% of plan rows are GEN-needed |
| 6 | SL-45.1 | Cost ledger | Canon 5's 25% cap is unenforceable without it |
| 7 | SL-40.1 | Shopify ↔ entitlement daily reconciliation | Paid-but-locked-out is the costliest support failure |
| 8 | SL-27.2 | TikTok manual until audit | API posts would be private [P3] |
| 9 | SL-46.1 | Nightly encrypted `pg_dump` | 7-day Supabase retention [P4] |
| 10 | SL-37.2 | Complaint-rate auto-pause | Gmail and Yahoo hard limit [P5] |
| 11 | SL-02.1 | Over-generate and rank hooks | Near-free lift before render |
| 12 | SL-24.1 | Judge golden set | The judge's miss rate is unknown |
| 13 | SL-22.1 | Competitor-corpus check | Copying risk on launch content |
| 14 | SL-35.1/2 | DM event dedupe plus async ack | Launch-spike double DMs |
| 15 | SL-25.1 | Review reason codes | Makes the human bottleneck teach the machine |
