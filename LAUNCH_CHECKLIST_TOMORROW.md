# LAUNCH_CHECKLIST_TOMORROW.md: Saturday Oct 3 2026, all times ET

The single page for launch day. Topology is CANON UPDATE 6 (BRIEF.md). It covers the 8 offline builds in the launch-tomorrow cut (ENGINE_SAVAGE20 §B(b)) plus SAVAGE #1 and #2. Posting is **by hand from the proxy accounts**. DM sends, email sends, n8n publishing, render keys and Shopify are **not live**. **AUTO** = a script on the team laptop (offline, no keys, posts nothing). **CLIENT** = a person tapping in the platform app.

## 0. Accounts and the velocity ramp

| # | Account | Platform | Handle | Day-1 role |
|---|---|---|---|---|
| 1 | ig_changyin | Instagram | @changyin | 3 rendered Reels (D1-CY-1..3) + 1 Story |
| 2 | ig_sunyoon_kitchen | Instagram | @sunyoon.kitchen | 3 rendered Reels (D1-SK-1..3) + 1 Story |
| 3 | ig_changandsun | Instagram | @changandsun | 1 intro Reel (GEN-needed: skip it if no file passed QA) + 1 Story |
| 4 | ig_changyin_strength | Instagram | @changyin.strength | 1 intro Reel (GEN-needed) + 1 Story |
| 5–8 | th_* | Threads, one per IG page | same as IG | 3 text posts each; the hook pre-screen probes |
| 9–12 | x_changyin, x_sunyoon_kitchen, x_changandsun, x_changyinstrong | X, one per IG page | @changyin, @sunyoon_kitchen, @changandsun, @changyinstrong | 2 probes each, **no links** |
| 13–16 | tt_* | TikTok, 4 accounts | same handles as IG | 1 each (GEN-needed), **by hand only** |
| 17 | fb_changandsun | Facebook, ONE page | Chang & Sun **[verify page name]** | FB variants of D1-CY-1 and D1-SK-1, + 1 text post |
| 18 | yt_changandsun | YouTube, ONE Shorts channel | **[verify handle]** | 1 Short (GEN-needed), **by hand only** |

**Ramp, per account per day** (`tools/topology.py` RAMP, an [A] assumption; D7 = CANON 6 steady state):

| Lane | D1 | D2 | D3 | D4 | D5 | D6 | D7 |
|---|---|---|---|---|---|---|---|
| IG main Reels | 3 (1 on the new pages) | 3 | 4 | 5 | 6 | 6 | 6 |
| IG Trial Reels | 0 | 2 | 5 | 10 | 15 | 20 | 20 |
| IG Stories (09:00 poll · 13:00 question box · 19:30 link sticker) | 1 | 2 | 3 | 3 | 3 | 3 | 3 |
| Threads | 3 | 6 | 8 | 10 | 12 | 12 | 12 |
| X | 2 | 3 | 4 | 5 | 6 | 6 | 6 |
| TikTok | 1 | 3 | 6 | 10 | 16 | 20 | 26 |
| FB page: video + long + text + photo | 2+0+1+0 | 4+0+1+1 | 6+1+1+1 | 8+1+1+1 | 10+2+1+1 | 12+2+1+1 | 12+2+1+1 |
| YouTube Shorts | 1 | 2 | 3 | 4 | 4 | 4 | 4 (6 after the quota raise) |
| **All accounts** | **40** | **84** | **132** | **187** | **250** | **288** | **312** |

Step up only if the previous day had no "limit", "unavailable", "try again later" or reach-restriction message on that account. One such message → that account repeats the day's numbers with **zero Trial Reels** until it clears (NEXT50 RO-1). A day without enough QA-passed files is posted short. Never fill a slot with an unchecked file.

## 1. Tonight (Fri Oct 2), in this order

1. **AUTO** `python3 tools/launch_gate.py`. This checks the keyword registry, the competitor corpus on the 6 day-1 posts, the caption rules, and the ≥300 product briefs. It must print `launch gate: OK`. If it fails, fix the item it names or HOLD that post.
2. **AUTO** `python3 deploy/scripts/check_secrets.py --repo-only --history` must print `check-secrets: OK`. Then `git config core.hooksPath deploy/hooks` once per clone, so every commit is scanned. CI runs the same scan.
3. **AUTO** Run frame-1 OCR on every rendered file before anyone uploads it: `qa/frame1.check_frame1(<file>, "ig"|"fb", expected=<on_screen_hook>)`. On FAIL (no text, more than 7 words, contrast below 4.5, or the wrong hook), mark the post HOLD.
4. **AUTO** Build the fallback pack (`POST /package/fallback`, or `packager/fallback.build_pack`). It rewrites time words in captions (required safety lines are left as written), holds any caption with a handle that isn't ours, and writes `posted_log.csv` with one row per placement.
5. **AUTO** `python3 tools/slots_ics.py --canon6 --date 2026-10-03` writes `production/launch_day/out/calendar/<account>_tomorrow.ics` and `<account>_week.ics`. **CLIENT:** each poster imports only their own accounts' files on their phone. Every event has a 10-minute alarm, the file id, the CTA keyword, trial yes/no and the skip rule.
6. **AUTO** `python3 tools/keyword_registry.py --manual-replies production/launch_day/manual_dm_replies.md` updates the sheet a person answers DMs from.
7. **AUTO** Pick the hook pre-screen: `growth/hook_prescreen.plan("2026-10-03", hooks)` takes the top 10 hooks that pass compliance and the handle allowlist. That is 20 text posts (10 on Threads, 10 on X) at 07:00 and 19:00, signed "(AI character)". On D1 X has 2 slots per account, so 8 of the 10 X probes go out.
8. **CLIENT** Profiles: on every account, name, bio, link and picture exactly as in `bios.md`. Turn on Instagram's account-level "AI-generated profile". Take screenshots.
9. **CLIENT** Comment-keyword test: from a personal test account, comment WAITLIST, TEST, BREATH, GUT, SOUP and STRONG. DMs are manual, so the team member on DM duty answers from `manual_dm_replies.md` within 60 minutes. Nothing auto-sends.
10. **CLIENT** Watch every `ig.mp4` / `fb.mp4` once with sound (UPLOAD_TONIGHT.md Part A.4). Any doubt means HOLD.

## 2. Launch day (Sat Oct 3)

| Time | Who | What |
|---|---|---|
| 07:00 (sibling accounts 4 min apart) | CLIENT | Threads + X hook probes, from the pack. On X: text only, no link. |
| 08:00–08:15 | CLIENT | Intro Reels on @changandsun and @changyin.strength, **only if** a QA-passed file exists. Otherwise skip. |
| 09:00 | CLIENT | One Story per IG page: a poll. AI label on. |
| 09:00 | CLIENT | YouTube Short, if a file passed QA. TikTok ×4 at their 07:00 slots, likewise. Turn on TikTok's "AI-generated content" toggle. |
| 10:30 | CLIENT | FB page text post. |
| 13:00 | AUTO | `hook_prescreen.read_due(...)` lists the 07:00 probes. **CLIENT** reads the 6 h numbers and enters them in the canonical CSV. |
| 13:30 | AUTO | `hook_prescreen.score(...)` ranks the probes. The top 6 hooks become D2 render picks (a prior, not a verdict). |
| 18:30 / 18:45 | CLIENT | FB page: D1-CY-1, then D1-SK-1, uploaded **natively** to FB. |
| 19:00–21:15 | CLIENT | IG Reels D1-CY-1..3 and D1-SK-1..3 at the times in the calendar. The 19:00 probe batch goes out alongside. |
| after every post | CLIENT | Fill one `posted_log.csv` row: `status=posted`, `posted_at` with offset (e.g. `2026-10-03T19:02:00-04:00`), the live **https permalink**, `posted_by`, `ai_label=y`. A skipped post gets `status=skipped`. |
| 22:00 | AUTO | `fallback.read_posted_log(...)` must report 0 problems (bad permalink, missing AI label, late post). |

**Day-2 morning** (AUTO plus one export per platform by the CLIENT):
1. Export Instagram and FB from Meta Business Suite, TikTok from Studio, and YouTube from Studio Advanced.
2. Run `growth/manual_import.normalize_manual_csv(<export>)`, then `join_posted_log(rows, posted)`, then `snapshots.build`.
3. Rows that `join_posted_log` returns as unmatched are posts with no posted-log row. Fix the log; never guess a post's id.

## 3. Rules for proxy accounts (zero-build, all of them hard)

- **Same device and network per account every day.** No VPN hopping and no shared logins. Use roles (Business Suite, channel permissions) and never pass passwords around. One person owns each account for the whole week.
- **Account-level and per-post AI label on every post**, trials included: IG "AI info", FB "Made with AI", TikTok "AI-generated content", YouTube "altered or synthetic content". Every caption keeps the AI-character line.
- **Upload to Facebook natively.** Never use IG's "share to Facebook" toggle.
- **No likes, comments, follows or shares between sibling accounts,** and no engagement or follow automation of any kind.
- **YouTube and TikTok by hand only** until the quota raise and the TikTok audit.
- **More than 30 minutes past the slot → skip it** and log it as skipped. Never post late and never double up.
- **Captions exactly as in the pack.** Don't add "today/tonight", don't add other creators' @handles, and don't add links on X.
- **Stop all Trial Reels on the first "limit" or "unavailable" message.** Anyone can call "pause all" in the team channel, and everyone stops.
- **No spending, no boosts, no new accounts, no DM automation** (CANON 5 holds: no paid media until ≥ $30K MRR).

## 4. Where the pieces live

| Item | Code | Test |
|---|---|---|
| 1 Keyword registry | `tools/keyword_registry.py` | `production/launch_day/tests/test_keywords.py` |
| 2 Competitor corpus (7-word shingles + TF-IDF vs posts.csv, transcripts, niche_posts) | `workers/uniqueness/external.py` | `workers/tests/test_launch_tomorrow.py` |
| 3 Caption rules (evergreen time words, handle allowlist) | `workers/compliance/caption_rules.py` | same |
| 4 Frame-1 OCR | `workers/qa/frame1.py` | same |
| 5 Manual metrics CSV import | `workers/growth/manual_import.py` | same |
| 6 Posted log | `workers/packager/fallback.py` | same |
| 7 Calendar (.ics per account, CANON 6, Stories) | `tools/topology.py`, `tools/slots_ics.py --canon6` | `tools/test_launch_tools.py` |
| 8 Secret scan (pre-commit + CI) | `deploy/scripts/check_secrets.py`, `deploy/hooks/pre-commit`, `.github/workflows/ci.yml` | same |
| 9 Product library → ≥300 briefs through the virality gate | `tools/product_to_scripts.py` → `data/content/product_briefs.json` | same |
| 10 Hook pre-screen (top 10/day, Threads/X, 6 h read) | `workers/growth/hook_prescreen.py`, `workers/packager/text_probe.py` | `workers/tests/test_launch_tomorrow.py` |
| Gate runner | `tools/launch_gate.py` (CI `content` job) | — |
