# LAUNCH_DAY_PROXY.md: launch-day plan for proxy-created accounts (L = the first posting day, ET)

Use this when the launch date moves. `LAUNCH_CHECKLIST_TOMORROW.md` is the same plan written out for Oct 3. CANON UPDATE 6 governs. Before any of this, `python3 tools/preflight.py` must print READY.
- CLIENT = Garrison or his poster, on the proxy device that created the account. AUTO = the ops box.
- Regenerate the calendars for the real date: `python3 tools/topology.py --date L` (counts) and `python3 tools/slots_ics.py --canon6 --date L` (one .ics per account).

## L-1 (the day the accounts and the store exist)

| When | Who | What |
|---|---|---|
| as soon as the store exists | CLIENT + Claude | `cd shopify && DRY_RUN=false CONFIRM_STORE=… npm run provision:live`, then `npm run verify`. Place one $12 dev-store test order and check the order, the 7-day trial line, the founding inventory dropping by 1, and the members-app unlock email. Refund it. If the trial plan is missing, `verify` warns and the offer falls back to STARTER12 (cell B). |
| same | AUTO | Webhook self-heal cron live (exit 0 = all 9 core topics registered). |
| accounts made | CLIENT | Per account: AI label/toggle on, bio from `production/bios.md`, profile photo from `production/pfp/`, link to `/go`. No posting, following sprees or DMs on L-1. Let each account sit at least 12 h after creation, on the same proxy, before its first post. |
| evening | AUTO | Render day-1 masters and cuts (`production/launch_day/render_day1.py`). Every file must pass QA and human review before it enters the pack. |
| evening | CLIENT | Read the pack (`UPLOAD_TONIGHT.md` flow). Anything not READY_FOR_HUMAN_REVIEW → approved is skipped. |

## L (day 1): 40 posts, hook probes first

| Time | Who | What |
|---|---|---|
| 07:00 (sibling accounts 4 min apart) | CLIENT | Threads + X hook probes from the pack. X is text only, no link. |
| 07:00 | CLIENT | TikTok × 4 (one per account), "AI-generated content" toggle on. Upload by hand until the API audit passes (API posts stay private). |
| 08:00–08:15 | CLIENT | Intro Reel on each IG page, only if a QA-passed file exists. |
| 09:00 | CLIENT | One Story per IG page: poll (D1 has 4 Stories in total; the 13:00 question box joins on D2 and the 19:30 link sticker on D3). YouTube Short 1 (Studio upload, "altered or synthetic content: yes"). |
| 10:30 | CLIENT | FB page text post. |
| 13:00 | CLIENT | Read the 6 h numbers on the 07:00 probes into the canonical CSV. |
| 13:30 | AUTO | `hook_prescreen.score(...)` ranks the probes; the top 6 hooks are the D2 render picks. |
| 18:30 / 18:45 | CLIENT | FB Reels × 2, uploaded natively. |
| 19:00–21:15 | CLIENT | Second Reel per IG page at the calendar times (8 Reels on D1 with the intro), plus the 19:00 probe batch (Threads 3 and X 2 per page across the day). |
| after every post | CLIENT | One `posted_log.csv` row (status, `posted_at` with offset, https permalink, `posted_by`, `ai_label=y`). |
| 22:00 | AUTO | `fallback.read_posted_log(...)` reports 0 problems. Overnight: render D2. |

## Velocity ramp (posts/day, all accounts; `tools/topology.py`)

| Day | Total | IG Reels | IG Trial | IG Stories | Threads | X | TikTok | FB | YT |
|---|---|---|---|---|---|---|---|---|---|
| D1 | 40 | 8 | 0 | 4 | 12 | 8 | 4 | 3 | 1 |
| D2 | 84 | 12 | 8 | 8 | 24 | 12 | 12 | 6 | 2 |
| D3 | 132 | 16 | 20 | 12 | 32 | 16 | 24 | 9 | 3 |
| D4 | 187 | 20 | 40 | 12 | 40 | 20 | 40 | 11 | 4 |
| D5 | 250 | 24 | 60 | 12 | 48 | 24 | 64 | 14 | 4 |
| D6 | 288 | 24 | 80 | 12 | 48 | 24 | 80 | 16 | 4 |
| D7 | 312 | 24 | 80 | 12 | 48 | 24 | 104 | 16 | 4 |

The canon 300/day steady state is reached on D7. The 458 rung (6 IG, 6 TikTok, 2 FB, YT at 6) opens at $30K retained MRR, and the ops box is sized for it (`deploy/README.md` "Capacity").

## Day-1 targets (projection of record, central)
- Views per video ramp: d1 500, d2 750, d3 1000, d4 1500, d5 2000, d6 2500, d7 3000.
- At 40 posts × 500 views (× platform multipliers), day 1 is a calibration day. The number that matters is the 6 h hook-probe ranking, not sales.
- Report booked MRR, retained MRR and cash separately from D2 on (`snapshots.build`).

## Stop rules (any one pauses that account for 24 h)
- An action block, "unusual activity" prompt or reach drop to near zero after a post.
- A compliance flag on a live post: delete it, log it in `posted_log.csv` (`status=removed`) and fix the template before reuse.
- A post that is not READY in the pack. Skip it; never post an unreviewed file to fill a slot.
- Never post from an account on a device or proxy other than the one that created it.
