# VIRALITY_SYSTEM.md: what every post is engineered to do, and where that is enforced

Goal: every post leaves the factory with the highest reach probability we can engineer for a 55+ audience, so what
remains is the platforms' distribution (and account health, which POSTDB Rule 0 shows can swing reach 40–100×).

Below, **[M]** means measured in Yang Mun's 244 posts (POSTDB_FINDINGS.md), **[W]** means a 2025–2026 platform or
industry source cited in §6, and **[A]** means an assumption. Every [A] weight gets re-fit from our own
shares-and-saves data once each page has about 30 posts (workers/growth).

## 1. Enforcement map

| Layer | What is enforced | Where | Fails how |
|---|---|---|---|
| Script | Virality rubric ≥ 60 (§2) | `tools/virality.py`, `tools/build_content.py` (`virality_gate`) | Build fails for S61+, every wave2/new script, and offer scripts at their floor (50). S01–S60 below 60 are marked `REWRITE` and never scheduled. |
| Launch day | Rubric ≥ 85 (top decile) | `production/launch_day/build_day1_plan.py` | The plan is not written |
| Writer | Same rubric as prose rule 10 | `prompts/02_script_writer.md` | The generator targets the gate |
| Render | R1–R6 (§3) | `workers/assemble/virality_gate.py`, called first in `assembler.assemble`; cover rule in `variants.render_variants` | `AssemblyError` / `ValueError` before any encode. `virality_gate: "warn"` exists only for legacy jobs |
| Learning | Shares + saves per view as the primary reward, a 1 h / 3 h retention proxy, a hook-family arm, and an exploration floor of at least 20% | `workers/growth/{baselines,scoring,allocator,config}.py` | Config cannot go below the 20% floor (existing guard) |
| Posting | 06:00–21:30 ET envelope, prime-window coverage, hashtag caps, Trial Reels for the first 14 days, remix of the top 3 within 24 h | `tools/posting_rules.py` (writes `data/content/posting_plan_flags.csv`) | Non-zero exit on any violation |

## 2. Script rubric (100 points; threshold 60; top decile 85)

| Component | Pts | Full credit when | Evidence |
|---|---|---|---|
| Hook grammar class | 25 | Scored by measured rel, log-scaled: `0.2 + 0.8·(ln rel − ln 0.61)/(ln 5.5 − ln 0.61)` | [M] §3a/§3b: IF_EVERY 5.5 → 1.00 · MYTH / NOT_X 3.0 → 0.78 · AUTHORITY 2.65 → 0.73 · WATCH 2.06 → 0.64 · COMMAND / OBJ3 → 0.64 [A, set to WATCH's rel] · STORY 1.74 → 0.58 · STATEMENT 1.08 → 0.41 · LIST 0.95 → 0.36 · SYMPTOM "if you have X" 0.86 → 0.33 · QUESTION 0.70 → 0.25 · HOW-TO 0.61 → 0.20. The 0.2 floor is there because §9 calls differences under 1.5× noise |
| Demo on self in frame 1 | 15 | Movement script (1.0); demo or prop with physical action (0.75); talking head 0 | [M] §3b body demo rel 2.34, food 1.42, talking head 0.71 |
| First line | 10 | First spoken clause ≤ 12 words and first sentence ≤ 22 | [W] 50–60% of drop-offs happen in the first 3 s; [M] mega-hit first sentences ran 13–22 words at 2.3 words/s, with the first clause ~11 |
| Concrete number | 10 | Number in the hook or re-hook (0.5 if only later) | [M] §7: 8 of the 15 best hooks carry one |
| Open loop | 10 | Re-hook by 3–6 s ("watch", "but", "here's", "?") | [W] watch time / early drop-off gates expansion |
| Share trigger | 8 | "Send this to…", "do it with your…", "show your…" | [M] §3c share rate is most correlated with rel (0.34); [W] sends per reach is the strongest non-follower signal |
| Save trigger | 7 | "Save it", "tonight before bed", "day 1", "tomorrow", "write it down" | [W] saves are a ranking input; [A] weight |
| Length | 10 | 30–59 s (0.6 for 25–69 s) | [M] 45–59 s rel 1.19, 30–44 s 1.15, 90 s+ 0.70 |
| Emotion | 2 | Family / age / identity cue in the first two beats | [A] |
| CTA friction | 3 | Last line ≤ 14 words, one keyword | [M] §4 keyword bait inflates comments without lifting likes |

**Pass rates.** Each row scores the same text with the final rubric.

| Set | Before (HEAD sources) | After |
|---|---|---|
| Library S01–S190 | 177/190 pass, 7 at ≥ 85 | **187/190 pass, 12 at ≥ 85**, median 72.2, p90 84. The 3 fails (S37, S47, S49) are legacy, marked REWRITE and unscheduled |
| Launch-day 6 | 69.4–86.5 (5 of 6 below 85) | **88.7–96.2, all ≥ 85** (S154 94.5 · S155 88.7 · S158 88.7 · S160 96.2 · S161 88.7 · S167 90.7) |
| Wave2 (in progress, another writer) | n/a | 100/101 pass |

The previous ordinal rubric passed 170/190 on the HEAD export. The launch-day rewrites added one save trigger to each
script and one share trigger to S154. Claims, safety lines and CTAs are unchanged.

## 3. Render rules (every master, before encode)

- **R1, frame-1 hook text.** The `on_screen` hook starts at ≤ 0.05 s, is ≤ 7 words, and is on screen for ≥ 1 s (a warning below that). Colours go through the existing never-gray, ≥ 7:1 contrast check.
- **R2, caption burn-in.** Any job with a voice track must carry word timings, which feed the existing word-by-word captions. Sound-off viewing is common [W].
- **R3, pattern interrupt by second 3.** A shot cut, PiP, study card, text card or explicit `pattern_interrupts_s` cue must land in (0.4, 3.0] s.
- **R4, loop-friendly ending.** No sign-off ("bye", "see you", "follow for more") in the last words. More than 0.8 s of dead air after the last word gives a warning.
- **R5, 9:16 safe areas.** Output must be 1080×1920, and caption safe-zone overrides can't be looser than the platform zone. The zones (top 12%, bottom 20–22%, right 12–14%) are stricter than the published IG Reels margins of about 108 px top, 300–320 px bottom and 100–120 px right [W].
- **R6, cover.** Cover text is ≤ 6 words. It defaults to the frame-1 hook, so the grid tile, the first frame and the hook all say the same thing.

Tests: `workers/tests/test_virality_gate.py`.

## 4. Learning loop

- **Components.** `share_save_rate = log((shares + saves) / views)`, smoothed with a 1.0% prior, has weight 0.35, the largest. `retention` comes from `avg_watch_pct` or `avg_watch_s / duration_s` and is used only at the 1 h and 3 h horizons (weight 0.15). Keyword comments drop to 0.05 because they are inflated [M §4].
- **Reward.** `0.45·Φ(z_share_save/1.5) + 0.25·Φ(score/1.5) + 0.30·conversion`. When a platform reports no shares or saves, the share-save term falls back to velocity.
- **Hook-family arm.** One Beta per hook grammar, pooled across pillar, format, speaker and length, with a 14-day half-life. Proven grammars start at 0.55. Each exploit draw is 0.65 arm + 0.35 family. Explore slots go least-observed first, then by best family. `plan_day` returns `hook_families`.
- **Exploration floor.** The 20% floor is untouched (`MIN_EXPLORE_FLOOR`).

Tests: `test_growth_scoring.py` and `test_growth_allocator.py` (new cases).

## 5. Posting rules (`tools/posting_rules.py`)

- **Time.** Hard: 06:00–21:30 ET. Soft: each page × platform × day has a morning prime slot (about 06:30–10:00) and an evening prime slot (about 18:00–21:30). The current plan covers 92% of page-days, with 0 envelope violations. The best-scoring master of the day goes in the first morning prime slot. This is a slot test, not a finding [M §16, n = 45].
- **Hashtags.** Maximum per post: IG 5 (a platform cap) · FB 3 · TikTok 5 · YT Shorts 3 · Threads 1 · X 2. Library scripts carry 4 on IG and TikTok, which passes.
- **Trial Reels.** `ig_trial_reel = true` on every IG reel in each page's first 14 days (468 IG rows in the 90-day plan, and all 6 launch-day posts). A Trial Reel is shown to non-followers first. Share it to followers if it beats the page median at 24 h.
- **Remix the top 3 within 24 h.** Every day, each page's top 3 posts from the last 24 h, ranked by `share_save_z`, get a remix order due within 24 h. A remix keeps the hook grammar, changes the object or set, and is a fresh render. It is never a re-upload: [M] the 8.3M re-upload got 39.8K.

## 6. External evidence (checked 2026-10-01)

1. Mosseri's ranking signals are watch time, likes per reach and sends per reach. Sends count most for non-followers, and a fast drop-off in the first seconds caps a Reel. [kompozy.io](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance) · [socialync.io](https://www.socialync.io/blog/adam-mosseri-shares-instagram-algorithm-2026)
2. Trial Reels go to non-followers first, and the creator can then share them to followers. They are schedulable since Apr 2026. Meta reports +80% non-follower Reels reach for users. [Social Media Today](https://www.socialmediatoday.com/news/instagram-allows-creators-to-schedule-trial-reels/816549/)
3. Instagram has capped hashtags at 5 since 18 Dec 2025. Mosseri says hashtags don't increase reach. [TechBuzz](https://www.techbuzz.ai/articles/instagram-caps-hashtags-at-five-to-combat-spam)
4. 50–60% of Shorts drop-offs happen in the first 3 s. This is OpusClip's internal data, not peer-reviewed. [OpusClip](https://www.opus.pro/blog/ideal-youtube-shorts-length-format-retention)
5. 69% of viewers watch with sound off in public, and 80% are more likely to finish a video with captions (Verizon Media / Publicis, 2019, the latest large study I found). [Forbes](https://www.forbes.com/sites/tjmccue/2019/07/31/verizon-media-says-69-percent-of-consumers-watching-video-with-sound-off/)
6. US adults 65+ (Pew, June 2025) use YouTube 84%, Facebook 71%, Instagram 50% and TikTok 37%. [Pew](https://www.pewresearch.org/internet/fact-sheet/social-media/)
7. IG Reels safe margins on 1080×1920 are about 108 top, 300–320 bottom, 60 left and 100–120 right, and the grid crops covers. [Outfy](https://www.outfy.com/blog/instagram-safe-zone/)

## 7. Honest limits

- **Not verified.** I found no public Meta data on how Facebook Reels distributes to 65+ viewers specifically, and no rigorous study isolating frame-1 on-screen text. R1 rests on the sound-off evidence, the early drop-off evidence and POSTDB rule 13.
- **Small samples.** The rubric's weights come from a small, single-competitor sample (TikTok return era n = 45, groups often under 10), and its regexes detect phrasing, not quality. A script can game a trigger word. The LLM judge and a human pass are still needed.
- **What the rubric can't see.** It can't judge the render: performance, lighting, voice, or whether the demo actually reads in frame 1. Render rules R1–R6 check structure, not taste.
- **Distribution is outside our control.** Account state matters most [M Rule 0]: the same creative did 40–100× better on IG than on TikTok. AI labelling, originality enforcement and page age all gate reach, and no script fixes them.
- **Timing.** Slot times are tests. The 55+ prime windows are assumptions until our own 1 h / 3 h data exists.
- **Retention proxy.** It needs the platform's average watch time in the snapshot (IG, TikTok and YT expose it; Threads and X don't). Without it, the reward rests on shares and saves.
