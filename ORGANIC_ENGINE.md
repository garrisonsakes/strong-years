# ORGANIC_ENGINE.md: the Strong Years organic-first launch engine

**Status:** operating plan for CANON UPDATE 2 (BRIEF.md, Oct 1 2026): Shopify store, ebook front end (`{{EBOOK_PRICE}}` = $7 / $12 / $15 cells, default $12), founding membership $25/mo offered after the ebook payment, no $1 trial, organic-first with a 7–21 day runway on a free waitlist. Paid only boosts proven organic winners (spend governor caps, BLITZ.md §11 gates before any cold spend).
**Owner of every external action:** the client. We create no accounts, post nothing, contact no one, spend nothing and call no external AI APIs. Everything here is staged for the client to switch on.
**Companion files:** RUNWAY_SCRIPTS.md (the 40 new scripts, generated), FUNNEL.md §4.18 WAITLIST and §4.19 BOOK (new DM flows), ACCOUNT_SETUP.md (click-by-click account creation), `data/content/runway_calendar_R{21,14,7}.csv` (generated schedules), `tools/organic_engine.py` + economics.xlsx sheet `Organic_First` (the model behind every number in §0).

Labels used below: **[V]** verified against a primary or dated source (cited in §8), **[S]** secondary source only (blog/agency write-up; treat as likely, not certain), **[U]** unverifiable today (we say what would verify it), **[A]** our assumption, **[C]** client decision.

---

## 0. One screen

### 0.1 The honest math (read this before the calendar)

The organic model (`tools/organic_engine.py`, central inputs, **cell B default** ("$12 today = books + first month, then $25/mo"), 14-day runway) produces about **433 organic waitlist sign-ups by D0** and roughly **$2.1K MRR on D+4, $4.6K on D+14 and $9.0K on D+30** from organic alone (run R20; retained $4.6K after the first $25 renewal). The upside run (R21) is $7.6K / $16.3K / $31.0K. The books-only test cell (R22, cell A) is $0.07K / $0.2K / $0.5K. Organic traffic from new, AI-labeled pages does not reach $10K / $50K / $100K MRR inside 30 days on its own unless a post breaks out.

What closes the gap is the **size of the waitlist on D0**. The solver in the same file says how many confirmed waitlist sign-ups (from any source: our pages, partner creators, partner Facebook groups, the client's warm lists with valid consent) the targets need:

| Target | Cell A (ebook one-time, then post-purchase offer), central | Cell B ("$12 today = books + first month, then $25/mo"), central | Cell A, upside inputs |
|---|---|---|---|
| $10K MRR on D+4 | ~51,000 | **~4,700** | ~14,200 |
| $50K MRR on D+14 | ~200,000 | **~22,000** | ~62,000 |
| $100K MRR on D+30 | ~487,000 | **~49,000** | ~143,000 |

(Source: `python3 tools/organic_engine.py`, "Runway table / solver" block, 14-day runway rows R20/R21/R22. Every input is labeled in the file. Cell B (the launch default, CANON UPDATE 3) counts MRR at the contracted $25 and applies a 50% first-renewal survival; read the retained line.)

**So the engine is built around three jobs, in this order:**
1. **Fill the waitlist before D0** from our pages and, above all, from borrowed audiences (§4), because the D0 list is the variable that moves MRR most.
2. **Buy as many lottery tickets as the platforms tolerate** (6–9 unique videos per page per platform at full cadence, proven hook grammar, winners remixed inside 24 h) so a breakout can happen, without tripping new-account limits (§7).
3. **Convert on D0–D6 without pressure tricks**: one honest offer, a real 5,000 cap with a live counter, and the post-purchase membership offer (§5).

**[C] Decisions for the client before D−21:** (1) runway length R = 21 / 14 / 7 days (we recommend 21; the 7-day variant leans almost entirely on borrowed audiences); (2) whether cell B gets more than 50% of launch traffic (the solver says cell B needs ~10× less waitlist for the same MRR; the canon gates still decide the winner by net revenue per visitor and renewal 1); (3) the `{{CHECKOUT_OPENS_DATE}}` (it becomes the only countdown anywhere, because it's real).

### 0.2 Top organic levers, ranked by expected MRR impact

| # | Lever | Why it ranks here | Section |
|---|---|---|---|
| 1 | **Borrowed audiences into the waitlist before D0** (50+ creator collabs, Facebook page and group partners, newsletter content swaps, PT and senior-teacher affiliates) | The solver: D0 waitlist size dominates every milestone. One 200K-follower 60+ creator collab can equal the whole organic runway. | §4 |
| 2 | **IG + Facebook keyword → DM engine** (WAITLIST / value keywords → waitlist; BOOK from D0) | Comment→DM converts viewers into owned contacts at the moment of intent; it's the only automation Meta allows at volume (one private reply per comment). | §3, FUNNEL §4.18–4.19 |
| 3 | **Facebook Reels + Facebook Groups** | 68% of US adults 65+ use Facebook and 45% use it daily, vs 19% on Instagram and 5% daily on TikTok (Pew 2025) [V]. This is where our buyer is. | §2.3 |
| 4 | **Winner remix inside 24 h + IG Trial Reels for hook tests** | 3 posts make 80%+ of views (POSTDB §8 rule 11). Trial Reels test hooks on non-followers without burning the follower feed [V]. | §2.1, §6 |
| 5 | **Cell B / post-purchase take rate** (offer architecture, not traffic) | Same traffic, ~10× more MRR per waitlist member in the model. | §5 |

---

## 1. Calendar

### 1.1 Timeline (R = 21, the recommended runway)

| Days | Stage | What happens |
|---|---|---|
| **D−28 → D−22** | Critical path + account setup | Client creates and configures every account (ACCOUNT_SETUP.md); AI labels on; bios in waitlist mode; reference pack, voices and the first 150 posts rendered and judged (§7.3). |
| **D−23 → D−22** | Week 0 (PIPELINE §5.4) | 3 pinned posts per page posted **natively in-app** (CHARACTERS §9.2 PIN 1 "Hi, we're AI", PIN 2 FALLBACK "How we choose studies", PIN 3 is the runway disclosure post: S158 and S167 on D−21; @changandsun pins S174 when it posts). Follow 10–20 relevant real accounts by hand. No automation. |
| **D−21 → D−15** | Runway week 1 | 2 videos / page / platform / day; human replies to comments for the first 60 min of every post; ManyChat live (WAITLIST + value keywords in runway mode). Outreach wave 1 (§4) goes out from the client. |
| **D−14 → D−8** | Runway week 2 | 3 / day + 1 IG Trial Reel / day; Threads/X text 3 / day. First collab posts land. |
| **D−7 → D−1** | Runway week 3 | 5 / day (+1 Trial Reel). `@changyin.strength` and `@changyin.mobility` start (canon rollout day 15) on their own week-1 ramp. D−3: money QA, Shopify test orders, `/b` redirect test. D−1: go/no-go. |
| **D0** | Checkout opens | Waitlist launch email + push at 07:00 ET; announcement posts on all 3 pages; bio links flip to book mode; WAITLIST keyword becomes a BOOK variant. |
| **D+1 → D+6** | Launch week | 6 / day; ≤2 offer posts per page per day, the rest value; waitlist launch emails capped at 3 in the 72 h after the opening email. |
| **D+7 → D+13** | Week 2 | 7 / day target (up to 9 on pages past their week 4 that clear the §6 gates); `@sunyoon` starts D+1 (canon day 22, moved off D0); `@changyin.espanol` Mode A pilot at 3/day from D+8. Growth engine may queue boosts of WINNER posts for human approval (spend governor caps). |
| **D+14 → D+30** | Scale | Cadence by gates; day-10 BLITZ §11 gate decides any cold spend; remix and new briefs from the growth engine. |

### 1.2 Runway variants (generated from the same rules)

<!-- RUNWAY_SUMMARY:START -->
<!-- GENERATED by tools/build_content.py (build_runway_calendar): edit the sources, not this block -->
| Runway | Pages on D0 | Video masters before D0 (3 launch pages) | Avg videos/page/platform on D0–D6 | Total video masters D−R…D+30 (all pages) | Runway scripts placed | Launch scripts placed |
|---|---|---|---|---|---|---|
| 21 days | 5 | 210 | 6.0 | 1377 | 25/25 | 15/15 |
| 14 days | 3 | 105 | 5.0 | 1098 | 25/25 | 15/15 |
| 7 days | 3 | 42 | 3.0 | 820 | 25/25 | 15/15 |
<!-- RUNWAY_SUMMARY:END -->

- **R = 14:** account setup D−21 → D−15 (week 0 on D−16/D−15), posting from D−14. Launch week runs at the week-3 cadence (5/day), so D0–D6 volume leans on Stories, Threads/X text, the broadcast channel (if eligible) and email. Later pages: strength/mobility D+1, `@sunyoon` D+8, espanol D+16. Expected organic waitlist ~433 (model central); borrowed audiences carry the launch.
- **R = 7:** setup D−14 → D−8, posting from D−7. Launch week is the pages' second week (3/day + 1 Trial Reel). All 25 runway scripts still run (2–3 per page per day is dense but they're value posts). Expected organic waitlist ~134 (model central). Treat R = 7 as a **borrowed-audience launch with organic support**, not an organic launch. Later pages: strength/mobility D+8, `@sunyoon` D+15, espanol D+23.
- Every variant keeps the same ramp (PIPELINE §5.4). We never compress the ramp to hit a date: the restriction risk (§7) costs more than a smaller launch.

### 1.3 Cadence per page per platform

| Page age (week) | Videos / page / platform / day | IG Trial Reels / day | Threads + X text posts / day | Stories / page / day (IG + FB) |
|---|---|---|---|---|
| Week 0 (setup) | 0 (3 pinned, native) | 0 | 1 (intro) | 1–2 |
| Week 1 | 2 | 0 | 2 | 2–3 |
| Week 2 | 3 | 1 | 3 | 3–4 |
| Week 3 | 5 | 1 | 4 | 4–5 |
| Week 4+ | 6–7 (9 max on pages that clear §6 gates) | 1–2 | 4–5 | 5–6 |
| Launch week (D0–D6), whatever the week | page-age cadence, **≤2 offer posts** per page per day | 1 (value only, never offer) | 5 | 6 (counter, Q&A, "did you do day 1?") |

**Per platform, one master per page:** each page's master video goes to IG Reels, Facebook Page Reels, TikTok and YouTube Shorts with platform-native captions and CTA swaps (CONTENT_SYSTEM §8.2 rule 1 allows the same master across platforms for the *same* page; never across pages). Stagger the platforms by 20–40 minutes with the ±9 min jitter (PIPELINE §5.5). Threads and X get text posts (F37: Sun's verdicts, Chang's one-liners, the day's question) plus, on X, the native clip of the page's best video of the previous day. At full cadence one page is 6–9 videos × 4 video platforms + 4–5 text posts × 2 text platforms per day.

**Hard platform limits we stay under** [V]: IG API 100 published posts / 24 h per account; Facebook Reels API 30 / 24 h per Page (PIPELINE §5.3); YouTube `videos.insert` 100 calls / day per project, private-only until the API audit passes; TikTok Content Posting API private-only for unaudited clients, 6 requests / minute per user token; Threads API 250 posts / 24 h.

### 1.4 Posting windows for a 55+ audience (US; schedule in ET, repeat the evening slot for PT)

| Platform | Slots (ET) | Notes |
|---|---|---|
| Facebook Reels | 06:30, 08:00, 10:00, 12:00, 15:00, 18:30, 20:00 | Morning-heavy; 65+ is the most Facebook-daily age group [V Pew]. Longer 60–90 s cuts of follow-alongs do well here (CONTENT_SYSTEM §5.2). |
| Instagram Reels | 07:00, 08:30, 11:00, 12:45, 16:00, 19:00, 21:00 | The legacy calendar slots (tools/build_content.py `SLOTS`). Trial Reel: schedule it to non-followers at 11:00. |
| TikTok | 08:00, 12:00, 17:00, 19:30, 21:00 | TikTok skews to the 55–64s and the adult children (FAMILY / gift). |
| YouTube Shorts | 09:00, 14:00, 18:00, 20:00 | Fewer, better: YT punishes templated sameness (§2.5). |
| Threads | 07:30, 12:30, 18:00 (+2 floating) | Text first; reply to every comment in the first hour. |
| X | 08:00, 13:00, 19:00 | Link only in a reply, never in the post body (§2.7). |

All slots are a **starting test [A]**: POSTDB §8 rule 16 found 8–11 a.m. ET plus an evening slot, on thin data (n = 45). The growth engine re-ranks slots weekly by 6-hour views per post per slot.

### 1.5 The day-by-day calendar (R = 21, three launch pages; generated)

Read it as: each row is one page on one day; the "Posts" column lists that page's videos in slot-priority order (Test → Kitchen → Series → AM → Story → Myth → Bed), and each video goes to all four video platforms. `S###` = a produced script (SCRIPTS.md / RUNWAY_SCRIPTS.md); `H###` = a hook from HOOKS.md to be scripted by the pipeline; series labels come from CONTENT_SYSTEM §7; `NEW` = a brief from the growth engine (winner remix or idea miner). Launch pages beyond the first three show their cadence only. The R = 14 and R = 7 schedules are in `data/content/runway_calendar_R14.csv` and `_R7.csv`.

<!-- RUNWAY_CALENDAR:START -->
<!-- GENERATED by tools/build_content.py (build_runway_calendar): edit the sources, not this block -->
| D | Stage | Page | Videos/platform | IG Trial | Threads/X text | Posts (in slot order) |
|---|---|---|---|---|---|---|
| -21 | RUNWAY | @changyin | 2 | 0 | 2 | S158 (runway·WAITLIST) · S01 (F02·STRONG) |
| -21 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | S167 (runway·WAITLIST) · S33 (F06·GUT) |
| -21 | RUNWAY | @changandsun | 2 | 0 | 2 | S169 (runway·BEGIN) · S52 (F34·BALANCE) |
| -20 | RUNWAY | @changyin | 2 | 0 | 2 | S04 (F16·TEST) · S19 (F11·STRONG) |
| -20 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | Fiber Ladder D1 · S40 (F07·KNEES) |
| -20 | RUNWAY | @changandsun | 2 | 0 | 2 | Frank's Comeback ep1 · S51 (F08·STRONG) |
| -19 | RUNWAY | @changyin | 2 | 0 | 2 | S159 (runway·TEST) · S06 (F28·STRONG) |
| -19 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | S31 (F04·SOUP) · S39 (F06·SOUP) |
| -19 | RUNWAY | @changandsun | 2 | 0 | 2 | S53 (F33·FAMILY) · S55 (F18·SOUP) |
| -18 | RUNWAY | @changyin | 2 | 0 | 2 | S10 (F21·BREATH) · S03 (F02·TEST) |
| -18 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | S160 (runway·GUT) · S35 (F06·GUT) |
| -18 | RUNWAY | @changandsun | 2 | 0 | 2 | S168 (runway·TEST) · S57 (F08·SLEEP) |
| -17 | RUNWAY | @changyin | 2 | 0 | 2 | 7-Day Strong D2 · S02 (F02·BALANCE) |
| -17 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | S36 (F31·GUT) · Fiber Ladder D2 |
| -17 | RUNWAY | @changandsun | 2 | 0 | 2 | Frank's Comeback ep2 · S54 (F08·BACK) |
| -16 | RUNWAY | @changyin | 2 | 0 | 2 | S152 (runway·STRONG) · S05 (F16·STRONG) |
| -16 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | S32 (F18·SOUP) · S41 (F07·BEGIN) |
| -16 | RUNWAY | @changandsun | 2 | 0 | 2 | S58 (F35·BREATH) · S56 (F34·STRONG) |
| -15 | RUNWAY | @changyin | 2 | 0 | 2 | S07 (F28·STRONG) · S11 (F05·SLEEP) |
| -15 | RUNWAY | @sunyoon.kitchen | 2 | 0 | 2 | S161 (runway·SOUP) · S34 (F04·GUT) |
| -15 | RUNWAY | @changandsun | 2 | 0 | 2 | S172 (runway·SOUP) · S59 (F08·TEST) |
| -14 | RUNWAY | @changyin | 3 | 1 | 3 | S16 (F02·STRONG) · S18 (F14·STRONG) · 7-Day Strong D3 |
| -14 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | S46 (F35·BEGIN) · S44 (F18·SOUP) · S45 (F06·GUT) |
| -14 | RUNWAY | @changandsun | 3 | 1 | 3 | S126 (F08·BACK) · Loser does dishes · S125 (F34·BALANCE) |
| -13 | RUNWAY | @changyin | 3 | 1 | 3 | S154 (runway·TEST) · S15 (F02·KNEES) · S08 (F28·BALANCE) |
| -13 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | Fiber Ladder D3 · S38 (F06·GUT) · S42 (F07·STRONG) |
| -13 | RUNWAY | @changandsun | 3 | 1 | 3 | S129 (F28·BEGIN) · S128 (F34·TEST) · S130 (F25·KNEES) |
| -12 | RUNWAY | @changyin | 3 | 1 | 3 | S12 (F05·SLEEP) · S61 (F02·TEST) · S20 (F03·BACK) |
| -12 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | S162 (runway·BEGIN) · S43 (F28·STRONG) · S50 (F07·BALANCE) |
| -12 | RUNWAY | @changandsun | 3 | 1 | 3 | S170 (runway·BALANCE) · S132 (F27·STRONG) · S127 (F31·GUT) |
| -11 | RUNWAY | @changyin | 3 | 1 | 3 | S153 (runway·WAITLIST) · 7-Day Strong D4 · S17 (F23·STRONG) |
| -11 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | S102 (F06·GUT) · S104 (F31·GUT) · Fiber Ladder D4 |
| -11 | RUNWAY | @changandsun | 3 | 1 | 3 | Frank's Comeback ep4 · S131 (F08·BACK) · S134 (F08·STRONG) |
| -10 | RUNWAY | @changyin | 3 | 1 | 3 | S21 (F13·STRONG) · S09 (F22·BALANCE) · REPLY video (F09) |
| -10 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | S166 (runway·SOUP) · S48 (F18·SOUP) · S99 (F04·SOUP) |
| -10 | RUNWAY | @changandsun | 3 | 1 | 3 | S171 (runway·BEGIN) · S133 (F29·BEGIN) · REPLY video (F09) |
| -9 | RUNWAY | @changyin | 3 | 1 | 3 | S151 (runway·STRONG) · S64 (F32·BALANCE) · S25 (F14·KNEES) |
| -9 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | REPLY video (F09) · S106 (F18·SOUP) · Fiber Ladder D5 |
| -9 | RUNWAY | @changandsun | 3 | 1 | 3 | H047 (F08·BALANCE) · H216 (F08·STRONG) · Frank's Comeback ep5 |
| -8 | RUNWAY | @changyin | 3 | 1 | 3 | 7-Day Strong D5 · S22 (F20·BACK) · S27 (F15·STRONG) |
| -8 | RUNWAY | @sunyoon.kitchen | 3 | 1 | 3 | S101 (F04·SOUP) · S111 (F18·SOUP) · S100 (F04·SOUP) |
| -8 | RUNWAY | @changandsun | 3 | 1 | 3 | H028 (F08·BEGIN) · H090 (F07·BEGIN) · H159 (F07·BEGIN) |
| -7 | RUNWAY | @changyin | 5 | 1 | 4 | S13 (F03·BACK) · S24 (F32·BALANCE) · S67 (F02·TEST) · S28 (F13·STRONG) · 7-Day Strong D6 |
| -7 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | S165 (runway·BEGIN) · H243 (F07·BEGIN) · S110 (F06·SOUP) · S113 (F18·SOUP) · Fiber Ladder D6 |
| -7 | RUNWAY | @changandsun | 5 | 1 | 4 | S173 (runway·TEST) · H056 (F34·STRONG) · H218 (F35·BEGIN) · Frank's Comeback ep6 · H217 (F08·STRONG) |
| -7 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -7 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -6 | RUNWAY | @changyin | 5 | 1 | 4 | S157 (runway·KNEES) · S62 (F32·STRONG) · S14 (F03·BACK) · S30 (F22·SLEEP) · S70 (F13·STRONG) |
| -6 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | S108 (F19·GUT) · H124 (F07·STRONG) · S103 (F04·GUT) · H160 (F06·GUT) · S114 (F06·GUT) |
| -6 | RUNWAY | @changandsun | 5 | 1 | 4 | H122 (F07·BEGIN) · H163 (F08·SLEEP) · H220 (F28·STRONG) · H222 (F35·BEGIN) · Frank's Comeback ep7 |
| -6 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -6 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -5 | RUNWAY | @changyin | 5 | 1 | 4 | S29 (F15·BALANCE) · 7-Day Strong D7 · S63 (F02·BALANCE) · S23 (F28·STRONG) · H154 (F05·BACK) |
| -5 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | H181 (F31·SOUP) · Fiber Ladder D7 · S112 (F04·GUT) · H129 (F07·SOUP) · S105 (F04·GUT) |
| -5 | RUNWAY | @changandsun | 5 | 1 | 4 | H219 (F34·BALANCE) · H242 (F07·FAMILY) · H221 (F08·STRONG) · H170 (F07·BEGIN) · H224 (F29·GUT) |
| -5 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -5 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -4 | RUNWAY | @changyin | 5 | 1 | 4 | S71 (F01·STRONG) · S68 (F17·STRONG) · 30-Day Balance D1 · S66 (F03·BACK) · S69 (F33·FAMILY) |
| -4 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | S164 (runway·WAITLIST) · H174 (F06·GUT) · H050 (F18·SOUP) · H185 (F31·SOUP) · Sun Answers #1 |
| -4 | RUNWAY | @changandsun | 5 | 1 | 4 | S174 (runway·WAITLIST) · H225 (F08·BEGIN) · Frank's Comeback ep8 · H223 (F34·STRONG) · H125 (F33·FAMILY) |
| -4 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -4 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -3 | RUNWAY | @changyin | 5 | 1 | 4 | S155 (runway·BREATH) · REMIX wk1 winner · REPLY video (F09) · S75 (F02·TEST) · S73 (F15·BALANCE) |
| -3 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | H182 (F18·SOUP) · H134 (F07·STRONG) · REMIX wk1 winner · REPLY video (F09) · H060 (F11·GUT) |
| -3 | RUNWAY | @changandsun | 5 | 1 | 4 | REMIX wk1 winner · REPLY video (F09) · H227 (F35·BEGIN) · H230 (F08·STRONG) · Frank's Comeback ep9 |
| -3 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -3 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -2 | RUNWAY | @changyin | 5 | 1 | 4 | 30-Day Balance D2 · S72 (F03·BACK) · H001 (F27·STRONG) · S26 (F28·KNEES) · H155 (F21·SLEEP) |
| -2 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | H186 (F18·SOUP) · Sun Answers #2 · H005 (F06·GUT) · H138 (F31·SOUP) · S107 (F04·BACK) |
| -2 | RUNWAY | @changandsun | 5 | 1 | 4 | H226 (F25·KNEES) · H135 (F34·STRONG) · H228 (F08·STRONG) · H177 (F08·BACK) · H233 (F08·BEGIN) |
| -2 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -2 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -1 | RUNWAY | @changyin | 5 | 1 | 4 | S156 (runway·WAITLIST) · H271 (F16·TEST) · H092 (F02·STRONG) · 30-Day Balance D3 · H121 (F27·STRONG) |
| -1 | RUNWAY | @sunyoon.kitchen | 5 | 1 | 4 | S163 (runway·WAITLIST) · H244 (F07·STRONG) · H187 (F31·SOUP) · H189 (F12·SOUP) · Sun Answers #3 |
| -1 | RUNWAY | @changandsun | 5 | 1 | 4 | S175 (runway·WAITLIST) · H234 (F18·SOUP) · Loser does dishes · H231 (F08·BEGIN) · H144 (F07·BEGIN) |
| -1 | RUNWAY | @changyin.strength | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| -1 | RUNWAY | @changyin.mobility | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +0 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | S176 (launch·BOOK) · S177 (launch·JOIN) · H004 (F02·BALANCE) · REMIX wk1 winner · H156 (F05·KNEES) · H272 (F16·BALANCE) |
| +0 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | S181 (launch·BOOK) · H010 (F31·SOUP) · H139 (F31·SOUP) · REMIX wk1 winner · H246 (F18·SOUP) · H191 (F31·SOUP) |
| +0 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | S186 (launch·BOOK) · REMIX wk1 winner · H180 (F07·BEGIN) · H236 (F28·STRONG) · H240 (F35·BEGIN) · Frank's Comeback ep11 |
| +0 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +0 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +1 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | S178 (launch·BOOK) · H007 (F13·KNEES) · 30-Day Balance D4 · H006 (F21·BREATH) · H008 (F15·BACK) · S65 (F28·STRONG) |
| +1 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | S182 (launch·BOOK) · H192 (F06·SOUP) · Sun Answers #4 · H017 (F06·GUT) · H143 (F18·SOUP) · S109 (F04·SOUP) |
| +1 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | S187 (launch·BOOK) · H235 (F27·BEGIN) · H147 (F07·BEGIN) · H238 (F35·BEGIN) · NEW P03/F15·BALANCE · NEW P01/F02·TEST |
| +1 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +1 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +1 | LAUNCH WEEK | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +2 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | S180 (launch·BOOK) · H157 (F22·SLEEP) · H273 (F16·TEST) · H012 (F17·STRONG) · 30-Day Balance D5 · H009 (F05·SLEEP) |
| +2 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | S183 (launch·BOOK) · H249 (F07·STRONG) · H193 (F31·SOUP) · H194 (F18·SOUP) · Sun Answers #5 · H020 (F07·STRONG) |
| +2 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | S188 (launch·JOIN) · NEW P03/F15·BALANCE · Frank's Comeback ep12 · NEW P03/F15·BALANCE · H150 (F29·BALANCE) · REMIX wk1 winner |
| +2 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +2 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +2 | LAUNCH WEEK | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +3 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | S179 (launch·BOOK) · H013 (F13·STRONG) · REMIX wk1 winner · REPLY video (F09) · H034 (F02·STRONG) · H016 (F15·STRONG) |
| +3 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | S184 (launch·JOIN) · H251 (F07·STRONG) · REMIX wk1 winner · REPLY video (F09) · H195 (F31·GUT) · H196 (F31·SOUP) |
| +3 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | S189 (launch·BOOK) · REPLY video (F09) · NEW P07/F21·BREATH · NEW P01/F02·TEST · Frank's Comeback ep13 · NEW P16/F07·BEGIN |
| +3 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +3 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +3 | LAUNCH WEEK | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +4 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | 30-Day Balance D6 · H015 (F22·BALANCE) · H018 (F02·TEST) · H064 (F28·BACK) · H161 (F05·SLEEP) · H035 (F02·STRONG) |
| +4 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | S185 (launch·FAMILY) · Sun Answers #6 · H022 (F06·GUT) · H252 (F07·GUT) · H067 (F04·GUT) · H254 (F07·STRONG) |
| +4 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | H247 (F07·BEGIN) · H294 (F07·BEGIN) · NEW P13/F18·SOUP · NEW P19/F11·STRONG · NEW P03/F15·BALANCE · Frank's Comeback ep14 |
| +4 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +4 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +4 | LAUNCH WEEK | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +5 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | H023 (F02·BALANCE) · 30-Day Balance D7 · H019 (F16·STRONG) · H024 (F13·BREATH) · REMIX wk1 winner · H162 (F21·BREATH) |
| +5 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | H197 (F06·GUT) · H198 (F31·SOUP) · Sunday Soup · H026 (F31·GUT) · H255 (F07·STRONG) · REMIX wk1 winner |
| +5 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | NEW P15/F28·BEGIN · H248 (F35·BEGIN) · REMIX wk1 winner · NEW P18/F10·BEGIN · H113 (F33·FAMILY) · H253 (F07·BEGIN) |
| +5 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +5 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +5 | LAUNCH WEEK | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +6 | LAUNCH WEEK | @changyin | 6 | 1 | 5 | H036 (F02·BALANCE) · H027 (F14·BACK) · 30-Day Balance D8 · H025 (F13·STRONG) · H029 (F27·STRONG) · H069 (F04·BALANCE) |
| +6 | LAUNCH WEEK | @sunyoon.kitchen | 6 | 1 | 5 | H256 (F08·BACK) · H200 (F11·GUT) · H201 (F28·GUT) · Sun Answers #8 · H199 (F31·GUT) · H258 (F18·SOUP) |
| +6 | LAUNCH WEEK | @changandsun | 6 | 1 | 5 | S190 (launch·BOOK) · Frank's Comeback ep15 · H101 (F07·BEGIN) · H257 (F35·BEGIN) · H250 (F35·BEGIN) · H260 (F07·BEGIN) |
| +6 | LAUNCH WEEK | @changyin.strength | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +6 | LAUNCH WEEK | @changyin.mobility | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +6 | LAUNCH WEEK | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +7 | WEEK 2 | @changyin | 7 | 1 | 4 | S136 (blitz library, JOIN-path terms) · H164 (F05·BACK) · H037 (F02·TEST) · H094 (F16·STRONG) · 30-Day Balance D9 · H030 (F13·STRONG) · H097 (F17·STRONG) |
| +7 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | S144 (blitz library, JOIN-path terms) · H070 (F04·BACK) · H259 (F07·STRONG) · H204 (F06·SOUP) · H205 (F12·SOUP) · Sun Answers #9 · H203 (F06·SOUP) |
| +7 | WEEK 2 | @changandsun | 7 | 1 | 4 | S147 (blitz library, JOIN-path terms) · H265 (F07·BEGIN) · H267 (F07·BEGIN) · Frank's Comeback ep16 · H264 (F35·BEGIN) · H269 (F07·BEGIN) · REMIX wk2 winner |
| +7 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +7 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +7 | WEEK 2 | @sunyoon | 2 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +8 | WEEK 2 | @changyin | 7 | 1 | 4 | S137 (blitz library, JOIN-path terms) · REMIX wk2 winner · REPLY video (F09) · H041 (F32·BALANCE) · H098 (F15·BALANCE) · 30-Day Balance D10 · H038 (F02·BACK) |
| +8 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | S142 (blitz library, JOIN-path terms) · H261 (F07·GUT) · REMIX wk2 winner · REPLY video (F09) · H208 (F28·SOUP) · H209 (F31·GUT) · Sun Answers #10 |
| +8 | WEEK 2 | @changandsun | 7 | 1 | 4 | S148 (blitz library, JOIN-path terms) · REPLY video (F09) · NEW P01/F02·TEST · NEW P19/F11·STRONG · Loser does dishes · NEW P03/F15·BALANCE · NEW P07/F21·BREATH |
| +8 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +8 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +8 | WEEK 2 | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +8 | WEEK 2 | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +9 | WEEK 2 | @changyin | 7 | 1 | 4 | S138 (blitz library, JOIN-path terms) · H099 (F02·TEST) · H073 (F21·BREATH) · H165 (F05·SLEEP) · H043 (F02·TEST) · H100 (F14·BACK) · 30-Day Balance D11 |
| +9 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | S143 (blitz library, JOIN-path terms) · H206 (F18·SOUP) · H262 (F07·STRONG) · H071 (F28·SOUP) · H266 (F07·STRONG) · H279 (F18·GUT) · H076 (F06·GUT) |
| +9 | WEEK 2 | @changandsun | 7 | 1 | 4 | S149 (blitz library, JOIN-path terms) · NEW P13/F18·SOUP · NEW P03/F15·BALANCE · NEW P01/F02·TEST · NEW P13/F18·SOUP · Frank's Comeback ep18 · NEW P18/F10·BEGIN |
| +9 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +9 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +9 | WEEK 2 | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +9 | WEEK 2 | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +10 | WEEK 2 | @changyin | 7 | 1 | 4 | S139 (blitz library, JOIN-path terms) · H042 (F02·BACK) · H102 (F15·KNEES) · REMIX wk2 winner · H168 (F15·BALANCE) · H048 (F02·BACK) · H103 (F05·SLEEP) |
| +10 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #11 · H210 (F31·SOUP) · H270 (F07·STRONG) · REMIX wk2 winner · H080 (F04·GUT) · H286 (F06·GUT) · H104 (F18·SOUP) |
| +10 | WEEK 2 | @changandsun | 7 | 1 | 4 | S150 (blitz library, JOIN-path terms) · NEW P15/F28·BEGIN · REMIX wk2 winner · NEW P19/F11·STRONG · NEW P03/F15·BALANCE · NEW P01/F02·TEST · Frank's Comeback ep19 |
| +10 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +10 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +10 | WEEK 2 | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +10 | WEEK 2 | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +11 | WEEK 2 | @changyin | 7 | 1 | 4 | 30-Day Balance D12 · H046 (F02·BALANCE) · H105 (F16·TEST) · H074 (F28·STRONG) · H169 (F05·BACK) · H051 (F17·STRONG) · H106 (F15·BACK) |
| +11 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #12 · H087 (F31·GUT) · H111 (F06·GUT) · H287 (F06·GUT) · H117 (F18·SOUP) · H293 (F18·SOUP) · H295 (F28·GUT) |
| +11 | WEEK 2 | @changandsun | 7 | 1 | 4 | NEW P07/F21·BREATH · NEW P13/F18·SOUP · NEW P18/F10·BEGIN · NEW P15/F28·BEGIN · NEW P07/F21·BREATH · NEW P03/F15·BALANCE · 50th countdown |
| +11 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +11 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +11 | WEEK 2 | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +11 | WEEK 2 | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +12 | WEEK 2 | @changyin | 7 | 1 | 4 | 30-Day Balance D13 · H049 (F05·SLEEP) · H107 (F16·BALANCE) · REMIX wk2 winner · REPLY video (F09) · H053 (F21·BREATH) · H108 (F15·STRONG) |
| +12 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #13 · H291 (F06·GUT) · NEW P11/F31·SOUP · REMIX wk2 winner · REPLY video (F09) · NEW P11/F31·SOUP · NEW P11/F31·SOUP |
| +12 | WEEK 2 | @changandsun | 7 | 1 | 4 | NEW P19/F11·STRONG · NEW P18/F10·BEGIN · REMIX wk2 winner · REPLY video (F09) · NEW P13/F18·SOUP · NEW P19/F11·STRONG · 50th countdown |
| +12 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +12 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +12 | WEEK 2 | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +12 | WEEK 2 | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +13 | WEEK 2 | @changyin | 7 | 1 | 4 | 30-Day Balance D14 · H052 (F02·STRONG) · H112 (F16·STRONG) · H077 (F03·KNEES) · H171 (F21·BREATH) · H055 (F14·STRONG) · H114 (F16·TEST) |
| +13 | WEEK 2 | @sunyoon.kitchen | 7 | 1 | 4 | Sunday Soup · NEW P11/F31·SOUP · NEW P11/F31·SOUP · NEW P11/F31·SOUP · NEW P11/F31·SOUP · NEW P12/F06·SOUP · NEW P11/F31·SOUP |
| +13 | WEEK 2 | @changandsun | 7 | 1 | 4 | NEW P01/F02·TEST · NEW P03/F15·BALANCE · NEW P15/F28·BEGIN · NEW P07/F21·BREATH · NEW P01/F02·TEST · NEW P13/F18·SOUP · 50th countdown |
| +13 | WEEK 2 | @changyin.strength | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +13 | WEEK 2 | @changyin.mobility | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +13 | WEEK 2 | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +13 | WEEK 2 | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +14 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D15 · H054 (F11·BALANCE) · H115 (F17·STRONG) · REMIX wk3 winner · H172 (F05·SLEEP) · H058 (F02·STRONG) · H116 (F21·BREATH) |
| +14 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #15 · NEW P11/F31·SOUP · NEW P12/F06·SOUP · REMIX wk3 winner · NEW P11/F31·SOUP · NEW P12/F06·SOUP · NEW P12/F06·SOUP |
| +14 | SCALE | @changandsun | 7 | 1 | 4 | NEW P09/F05·SLEEP · NEW P15/F28·BEGIN · REMIX wk3 winner · NEW P19/F11·STRONG · NEW P18/F10·BEGIN · NEW P03/F15·BALANCE · 50th countdown |
| +14 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +14 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +14 | SCALE | @sunyoon | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +14 | SCALE | @changyin.espanol | 3 | 0 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +15 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D16 · H057 (F02·BALANCE) · H118 (F14·BACK) · H081 (F28·STRONG) · H173 (F17·STRONG) · H274 (F16·STRONG) · H119 (F27·STRONG) |
| +15 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #16 · NEW P11/F31·SOUP · NEW P10/F06·GUT · NEW P11/F31·SOUP · NEW P11/F31·SOUP · NEW P12/F06·SOUP · NEW P11/F31·SOUP |
| +15 | SCALE | @changandsun | 7 | 1 | 4 | NEW P03/F15·BALANCE · NEW P18/F10·BEGIN · NEW P07/F21·BREATH · NEW P01/F02·TEST · NEW P15/F28·BEGIN · NEW P16/F07·BEGIN · 50th countdown |
| +15 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +15 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +15 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +15 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +16 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D17 · H059 (F02·BALANCE) · H120 (F05·SLEEP) · REMIX wk3 winner · REPLY video (F09) · H275 (F16·STRONG) · H126 (F27·STRONG) |
| +16 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #17 · NEW P10/F06·GUT · NEW P10/F06·GUT · REMIX wk3 winner · REPLY video (F09) · NEW P12/F06·SOUP · NEW P10/F06·GUT |
| +16 | SCALE | @changandsun | 7 | 1 | 4 | NEW P13/F18·SOUP · NEW P19/F11·STRONG · REMIX wk3 winner · REPLY video (F09) · NEW P16/F07·BEGIN · NEW P03/F15·BALANCE · 50th countdown |
| +16 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +16 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +16 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +16 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +17 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D18 · H123 (F27·STRONG) · H128 (F33·FAMILY) · H082 (F28·BALANCE) · H175 (F05·BALANCE) · H276 (F16·BALANCE) · H131 (F15·STRONG) |
| +17 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #18 · NEW P11/F31·SOUP · NEW P12/F06·SOUP · NEW P11/F31·SOUP · NEW P11/F31·SOUP · NEW P13/F18·SOUP · NEW P11/F31·SOUP |
| +17 | SCALE | @changandsun | 7 | 1 | 4 | NEW P09/F05·SLEEP · NEW P01/F02·TEST · NEW P07/F21·BREATH · NEW P13/F18·SOUP · NEW P15/F28·BEGIN · NEW P19/F11·STRONG · 50th countdown |
| +17 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +17 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +17 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +17 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +18 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D19 · H130 (F15·BALANCE) · H132 (F14·KNEES) · REMIX wk3 winner · H176 (F11·STRONG) · H277 (F16·STRONG) · H136 (F27·STRONG) |
| +18 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #19 · NEW P10/F06·GUT · NEW P12/F06·SOUP · REMIX wk3 winner · NEW P17/F08·BEGIN · NEW P10/F06·GUT · NEW P12/F06·SOUP |
| +18 | SCALE | @changandsun | 7 | 1 | 4 | NEW P16/F07·BEGIN · NEW P03/F15·BALANCE · REMIX wk3 winner · NEW P16/F07·BEGIN · NEW P07/F21·BREATH · NEW P01/F02·TEST · 50th countdown |
| +18 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +18 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +18 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +18 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +19 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D20 · H133 (F17·BEGIN) · H137 (F22·BALANCE) · H083 (F28·STRONG) · H178 (F21·BREATH) · H278 (F02·TEST) · H141 (F05·SLEEP) |
| +19 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #20 · NEW P11/F31·SOUP · NEW P11/F31·SOUP · NEW P13/F18·SOUP · NEW P10/F06·GUT · NEW P11/F31·SOUP · NEW P12/F06·SOUP |
| +19 | SCALE | @changandsun | 7 | 1 | 4 | NEW P18/F10·BEGIN · S60 (F27·BEGIN) · NEW P09/F05·SLEEP · NEW P16/F07·BEGIN · NEW P15/F28·BEGIN · NEW P19/F11·STRONG · 50th countdown |
| +19 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +19 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +19 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +19 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +20 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D21 · H140 (F14·STRONG) · H142 (F15·STRONG) · REMIX wk3 winner · REPLY video (F09) · H281 (F21·BREATH) · H146 (F14·BACK) |
| +20 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sunday Soup · NEW P13/F18·SOUP · NEW P17/F08·BEGIN · REMIX wk3 winner · REPLY video (F09) · NEW P10/F06·GUT · NEW P11/F31·SOUP |
| +20 | SCALE | @changandsun | 7 | 1 | 4 | NEW P13/F18·SOUP · NEW P03/F15·BALANCE · REMIX wk3 winner · REPLY video (F09) · NEW P07/F21·BREATH · NEW P16/F07·BEGIN · 50th countdown |
| +20 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +20 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +20 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +20 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +21 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D22 · H145 (F15·BACK) · H148 (F11·STRONG) · H084 (F24·STRONG) · H179 (F14·SLEEP) · H282 (F16·STRONG) · H086 (F28·BREATH) |
| +21 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #22 · NEW P11/F31·SOUP · NEW P12/F06·SOUP · NEW P13/F18·SOUP · NEW P10/F06·GUT · NEW P11/F31·SOUP · NEW P15/F28·BEGIN |
| +21 | SCALE | @changandsun | 7 | 1 | 4 | NEW P16/F07·BEGIN · NEW P13/F18·SOUP · NEW P01/F02·TEST · NEW P15/F28·BEGIN · NEW P03/F15·BALANCE · NEW P18/F10·BEGIN · 50th countdown |
| +21 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +21 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +21 | SCALE | @sunyoon | 5 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +21 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +22 | SCALE | @changyin | 7 | 1 | 4 | 30-Day Balance D23 · H149 (F27·BEGIN) · H088 (F28·KNEES) · REMIX wk4 winner · H089 (F16·TEST) · NEW ×2 (growth engine: winner remix / idea miner) |
| +22 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | Sun Answers #23 · NEW P13/F18·SOUP · NEW P12/F06·SOUP · REMIX wk4 winner · NEW P10/F06·GUT · NEW ×2 (growth engine: winner remix / idea miner) |
| +22 | SCALE | @changandsun | 7 | 1 | 4 | NEW P19/F11·STRONG · NEW P16/F07·BEGIN · REMIX wk4 winner · NEW P09/F05·SLEEP · NEW ×3 (growth engine: winner remix / idea miner) |
| +22 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +22 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +22 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +22 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +23 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +23 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +23 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +23 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +23 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +23 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +23 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +24 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +24 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +24 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +24 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +24 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +24 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +24 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +25 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +25 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +25 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +25 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +25 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +25 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +25 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +26 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +26 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +26 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +26 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +26 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +26 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +26 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +27 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +27 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +27 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +27 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +27 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +27 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +27 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +28 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +28 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +28 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +28 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +28 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +28 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +28 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +29 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +29 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +29 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +29 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +29 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +29 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +29 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +30 | SCALE | @changyin | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +30 | SCALE | @sunyoon.kitchen | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +30 | SCALE | @changandsun | 7 | 1 | 4 | NEW ×7 (growth engine: winner remix / idea miner) |
| +30 | SCALE | @changyin.strength | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +30 | SCALE | @changyin.mobility | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +30 | SCALE | @sunyoon | 6 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
| +30 | SCALE | @changyin.espanol | 3 | 1 | 2 | page library + NEW (see CONTENT_SYSTEM §8.1) |
<!-- RUNWAY_CALENDAR:END -->

**Runway-mode overrides of the legacy calendar:** the blitz launch cells (S135–S150) never run during the runway. S136, S137, S138, S139, S142, S143, S144, S147, S148, S149 and S150 run in week 2 (D+7 → D+13), one per page per day, because their terms match the direct JOIN path; S135, S140, S141, S145 and S146 say "doors open today" and are held for a future doors-open moment. The DM flows of every value keyword route to the waitlist during the runway and to BOOK from D0 (FUNNEL §4.18 runway link rule).

---

## 2. Platform mechanics, 2025–2026 (researched Oct 1 2026; sources in §8)

### 2.1 Instagram

| Mechanic | What's true now | How we use it | Status |
|---|---|---|---|
| **AI-generated profile label** | Announced Aug 31 2026. Accounts whose subject is an AI-generated person must turn on "AI-generated profile" (Edit profile toggle). Unlabeled AI-persona accounts can lose reach in Reels recommendations, Explore and suggested accounts. Labeled accounts get **no penalty for being AI** per Meta. Detection and owner notices were to start "in the coming weeks"; appeals go through Account Status. A post-level "made/edited with AI" label is separate and can show instead of the profile label on a post. | Label ON before the first post on every page (hard precondition in `page_accounts`, PIPELINE §5.2). C2PA re-signed on every master so post-level "AI info" applies. VA checks the first 10 posts show the label. | [V] rule; [U] whether *viewers* engage less with labeled accounts. We measure it: labeled-page median 3-s hold and share rate vs the POSTDB baselines, weekly. |
| **Trial Reels** | Shown only to non-followers; can be scheduled (Apr 2026); "upgrade" to followers and the profile if it performs. API: `trial_params.graduation_strategy` = `MANUAL` or `SS_PERFORMANCE` (auto-graduate on performance). | From page week 2: 1 Trial Reel per day = an alternate hook of that day's best value script (same body, new frame 1 + hook). `SS_PERFORMANCE`. Never an offer post (followers must see offers, and offers aren't hook tests). | [V] |
| **Collab posts** | Up to 5 collaborators on a post or Reel; it appears on every collaborator's profile and feed; likes and comments are pooled; both accounts must be professional; collaborators can be added after posting. | **Only with real external partners** (§4.1). Never between our own pages (CONTENT_SYSTEM §8.2 rule 7: reads as network behavior). With any paid or gifted relationship, add the Paid partnership label and "#ad" (§4.5). | [V] mechanics via Sked; [S] reach effect |
| **Broadcast channels** | Creator accounts; one-to-many inbox channel; unlimited members; text, voice notes, polls, photos. Eligibility threshold is not published; secondary sources say roughly 10K followers. | Create as soon as the flagship is eligible: "Chang's Morning Note" (1 / day: today's session name, the counter on launch week, polls). Members join from Stories and the profile. Never a sales blast during the runway beyond "waitlist is open". | [S] threshold, [U] until the account shows the option |
| **Comment-keyword → DM** | Meta's private-reply API allows **one** private message per comment, within 7 days of the comment; the 24-hour window opens only when the person replies; the human-agent tag (7 days) is for real humans only and abusing it can remove send rights. | ManyChat flows FUNNEL §4.3–4.19; DM 1 must carry the whole value (one shot); public reply first; no links in public replies; no cold DMs. | [V] via Helm summary of Meta docs; ManyChat implements it |
| **Stories** | Link sticker, poll, question, countdown sticker (real date only). | Daily: link sticker to `/waitlist` (runway) or `/b` (launch); "Did you do day 1?" poll; Q&A sticker → F10 reply videos; the real `{{CHECKOUT_OPENS_DATE}}` countdown is the only countdown we ever use. | [V] standard features |
| **New-account limits** | Instagram publishes no daily post cap; DM/follow/like limits for new accounts are industry estimates (roughly 20–50 DMs, ~100 follows, ~250 likes a day). | We send no outbound DMs and follow by hand only in week 0; posting follows the §1.3 ramp. | [S] estimates only |

### 2.2 Threads

500M monthly users (June 2026); Communities out of beta; "Your Algo" lets users tune their feed [V]. Threads API: 250 posts / 24 h (PIPELINE §5.3). **Use:** Sun Yoon's text verdicts (F37), the day's question ("What did you carry today?"), replies within the first hour; join relevant Communities (fitness over 60, cooking, retirement) and post there as the page where the community allows. No automation of replies beyond the human-in-the-loop bot (CONTENT_SYSTEM §4).

### 2.3 Facebook (Pages, Reels, Groups): the 55+ home platform

- **Reach:** 68% of US adults 65+ use Facebook, 45% daily; 77% of 50–64s use it (Pew, Nov 2025) [V]. Roughly half of a user's feed is recommended content from accounts they don't follow, and Reels get the discovery push (Jan 2026 update: more same-day Reels; mid-video retention matters) [S].
- **Originality:** Meta's July 2025 rules demote and demonetize accounts that repeatedly repost others' content; reaction or commentary with a real contribution is fine [V]. A 2026 clarification says voiceover alone over third-party clips isn't original [S]. All our masters are original renders, so the risk is only in clips we might borrow: **never post another creator's footage**, even with commentary.
- **Groups:** the highest-engagement surface on Facebook [S]. A Page can join and post in groups whose admins allow Pages. **Use:** partner groups only, with written admin permission (§4.2): a weekly "Chair Challenge" thread the admin approves, a monthly live Q&A with a real team member, no links unless the group's rules allow them, no cross-posting of the same text to many groups (spam signal).
- **Messenger:** comment → Messenger DM works (FUNNEL §4.15); Marketing Messages opt-in gives a compliant channel past 24 h where available.
- **Page setup:** Page bio + About carry the AI disclosure; "Digital creator" category; the Page is linked to the IG account in Accounts Center (truthful common ownership).

### 2.4 TikTok

- **AI labeling:** realistic AI people must be labeled; C2PA metadata triggers the "AI-generated" label automatically; unlabeled realistic AI gets labeled retroactively, removed on repeat and can restrict the account [S]. In the Content Posting API, `is_aigc: true` adds "Creator labeled as AI-generated" to the post [V]. We set it on every post and in the in-app toggle when posting manually.
- **Unaudited API clients post private-only** [V]; publish through upload-post until the audit passes (PIPELINE §5.3).
- **US comment triggers aren't available** (BRIEF). TikTok renders swap the last line to "Tap the link in my bio and choose WAITLIST / BOOK"; bio link → `{{DOMAIN}}/tt` tiles; the keyword works as a TikTok DM keyword auto-reply where available.
- **Spark Ads (only for boosting proven winners, under the governor):** the creator account generates an authorization code per video (Ad settings → Generate) for 7, 30, 60 or 365 days; captions lock while authorized and the post can't be deleted until un-authorized [S]. Organic engagement accrues to the original post. Use the 30-day code for launch-month boosts; never boost an unlabeled AI post.
- **Monetization:** BRIEF reports TikTok demonetized "AI grandma" accounts as unoriginal [U: press reports, no policy text found]. We don't depend on TikTok Creator Rewards; TikTok's job is reach to the 55–64s and the adult children (FAMILY gifts). Only 5% of 65+ use TikTok daily [V Pew].

### 2.5 YouTube Shorts and the July 2026 inauthentic-content clarification

- **What YouTube clarified on July 16 2026** [V TechCrunch]: three kinds of content are ineligible for the YouTube Partner Program: (1) repetitive, template-based content with minimal variation (easy to mass-produce with AI, CGI or templates); (2) off-putting or distressing content made to manipulate emotions; (3) **AI personas discussing health, medical, finance or legal topics**. Channels with too much of any category lose monetization. YouTube's Trust & Safety lead: AI that makes "lots of videos really quickly that are very similar" is "content farming". Secondary write-ups add that the content generally stays visible but loses ad revenue, and that the decisive test is interchangeability ("same script skeleton… only the topic noun swapped") [S].
- **What it means for us:** our Shorts **will not be YPP-eligible** under category 3 (an AI persona talking health) whatever we do; we don't depend on YPP (PIPELINE §5.5). The real risk is the *spam/repetitive* reading, which can hurt distribution and channel standing. **Staying compliant:**
  1. One YouTube channel per editorial page, never cross-page duplicates; the growth engine's YouTube remix cap is 1 per source with a stricter text-similarity threshold (`workers/growth/config.py` remix.youtube: `max_remixes_per_source: 1`, `text_network_max: 0.70`).
  2. Vary structure, not just topic nouns: the 39 formats and 9 hook grammars rotate; the uniqueness guard blocks frame-1 set+prop repeats.
  3. Characters never present as credentialed (SAFETY D-05); the pinned "Hi, we're AI" Short and the About section disclose; `status.containsSyntheticMedia: true` on every upload [V API].
  4. YouTube cadence is capped at 4/day per channel even at full cadence elsewhere (§1.4); quality over volume here.
  5. Long-form only for proven topics filmed as real follow-along sessions (POSTDB rule 24).
- **API:** `videos.insert` = 1 unit in the uploads bucket, 100 calls/day per project; private-only until audit [V].

### 2.6 Cross-platform AI disclosure (summary)

IG profile label + post AI info (C2PA); Facebook About + AI info; TikTok `is_aigc` + bio; YouTube altered/synthetic = Yes + About + pinned Short; Threads/X bio. Burned-in `AI character` tag on every frame (SAFETY D-02) and the caption footer (SAFETY §7) everywhere. EU AI Act Art. 50 transparency applies to EU viewers (BRIEF).

### 2.7 X

Native video ranks; replies weigh far more than likes; external links in the post body are suppressed (secondary sources quote 30–80%) [S, U on the size]. **Use:** 3 posts/day (Sun verdicts, the day's clip natively, a question), the link only in the first reply, reply to replies within the hour. X is a minor channel for this audience; don't over-invest.

---

## 3. The path: view → waitlist → ebook buyer → member

### 3.1 The map

```
Video (IG/FB/TT/YT)  ──comment keyword──▶  DM 1 (AI disclosure + full value in one message)
      │                                           │
      ├─ bio link ─▶ {{DOMAIN}}/go (tiles)        ├─ RUNWAY: [Get first access (free)] → /waitlist → double opt-in → Day 1 starter
      ├─ Story link sticker                       │          → referral link (The Wall Plan bonus when a friend confirms)
      ├─ pinned posts / broadcast channel         └─ D0+:    [Send me the link] → /b (sticky cell) → Shopify PRODUCT PAGE
      └─ Threads/X reply link                        DEFAULT (cell B): "$12 today = books + first month, then $25/mo"
                                                       (founding plan + STARTER12 first-payment code; terms + consent on the page)
                                                     TEST (cell A): books paid ($12 one-time)
                                                       → thank-you page founding offer ($25/mo, full terms)
                                                       → 3 onboarding emails (same offer, full terms)
                                                       (one-click post-purchase app: scaffolded, OFF)
                                                     → members.{{DOMAIN}} access via orders/paid (store-wide webhooks)
```

### 3.2 Bio links (two modes; the client switches them on D0 at 07:00 ET)

| Page | Runway mode link | Launch mode link |
|---|---|---|
| @changyin | `{{DOMAIN}}/go?p=cy` → tiles: **Get first access (free)**, Day 1 free (8 min), Strength Age test, Sun's soups | `{{DOMAIN}}/go?p=cy` → tiles: **Starter books ({{EBOOK_PRICE}})**, Day 1 free, Strength Age test, Gift for a parent |
| @sunyoon.kitchen | same tiles, Sun's order: soups first | same, Strong Kitchen sample first |
| @changandsun | same tiles, couples test first | same, books first, then gift |
| TikTok (all pages) | `{{DOMAIN}}/tt` keyword tiles | same, BOOK tile first |
| YouTube | Description line 1 = `{{DOMAIN}}/go?p=yt-{page}`; pinned comment same | same |

`/go` and `/tt` are one app page (`app/src/app/(site)/go/page.tsx`, `/tt` redirects into it with `platform=tt`) whose mode follows the launch state (`LAUNCH_MODE` / `CHECKOUT_OPENS_AT` / the admin "Open checkout now"), so the flip is automatic, not 20 manual edits. Built and tested (`app/tests/unit/bio-links.test.ts`).

### 3.3 Keyword → DM

- **Runway:** WAITLIST (FUNNEL §4.18) + every value keyword (STRONG, BALANCE, BACK, KNEES, SLEEP, BREATH, SOUP, BEGIN, TEST, GUT) with the runway link rule (offer buttons → `/waitlist?t={keyword}`). WAITLIST is the CTA on 8 of the 25 runway scripts; the other 17 lead with value, so the keyword mix trains the audience to comment for something useful.
- **Launch:** BOOK (FUNNEL §4.19; WAITLIST becomes a variant of BOOK on D0), JOIN (§4.17) for people who want only the membership, FAMILY for gifts. Value keywords' offer buttons → `/b?t={keyword}`.
- **Every flow:** AI disclosure in DM 1, one private reply per comment, public reply without link or price, crisis classifier first (FUNNEL §4.14), human inbox on request.

### 3.4 Stories (per page per day)

| Runway | Launch week |
|---|---|
| 1 link sticker → `/waitlist` ("Day 1 is free") · 1 poll from today's main video ("Did you need your hands?") · 1 question sticker (feeds F10 reply videos) · 1 reshare of a sibling page's new Reel (≤1/day, CONTENT_SYSTEM §8.3) · the real opening-date countdown sticker from D−7 | 1 link sticker → `/b` · the live founding count as a screenshot of the real counter, twice a day · "Did you do Day 1?" poll · Q&A sticker answered by a real team member for offer questions · the gift tile on D+4 |

### 3.5 Pinned posts

| Window | Pin 1 | Pin 2 | Pin 3 |
|---|---|---|---|
| Runway | "Hi, we're AI" (CHARACTERS §9.2, duo; on every page) | "How we choose studies" (FALLBACK, no review claim) | Runway disclosure + WAITLIST: S158 (@changyin), S167 (@sunyoon.kitchen), S174 (@changandsun) |
| Launch week | "Hi, we're AI" (never moves) | S177 (@changyin) / S184 (@sunyoon.kitchen) / S188 (@changandsun): the terms, read out loud | S176 / S181 / S186: the doors-open offer post |
| After D+6 | "Hi, we're AI" | Terms post | S190 "No countdown, here's what changes" (@changandsun) / S178 Day 1 free (@changyin) / S182 page 14 (@sunyoon.kitchen) |

### 3.6 Broadcast channel (when eligible)

Name: "Chang's Morning Note". Runway: one line a day (today's session name, one tip, the waitlist link once a week). Launch week: the opening message at 07:00 on D0, then the real counter once a day and one Q&A answer. Never more than 1 message/day; never a fake deadline.

### 3.7 Email and push during the runway (the consent we collect limits what we may send)

The waitlist consent text is exact: "Email me when Strong Years opens, plus at most 3 launch emails in the 72 hours after that. One-click unsubscribe in every email." (`app/src/lib/waitlist.ts`). So **before D0 a waitlist address receives only the double-opt-in email** (with the Day 1 starter link). No nurture sequence, no "update" emails. Push consent allows one notification at opening and one reminder within 72 hours. Anything more needs a separate, explicit opt-in (the DM email capture in the value flows gets the general "short daily tips" consent and can receive the normal tips sequence; keep the two lists separate in the ESP).

---

## 4. Borrowed audiences (organic, no ad spend unless the client approves a paid shoutout)

Everything here is **sent by the client** (or a VA the client employs) from the client's own accounts and email. Templates are in §4.6. We contact no one.

### 4.1 Collabs with real 50+ creators (highest leverage)

**Target profile:** real people aged 50+ (or creators whose audience is 55+) in strength/fitness over 60, walking, cooking for one, retirement life, grandparenting, caregiving; 5K–500K followers on IG or Facebook; engagement ≥2% on Reels; no health-claim or supplement-scam history; US-based audience ≥50% (ask for a screenshot of audience insights).
**Volume:** wave 1 (D−21): 60 invitations; wave 2 (D−14): 60 more to lookalikes of whoever said yes; aim for 8–12 live collabs before D0 [A: 10–20% reply, half of replies agree].
**Formats that fit a real human + an AI character honestly:**
1. **"Chang's chair test vs mine"**: the creator films their own 30-second chair stand; we render Chang's side; posted as a Collab Reel (both profiles). The creator says on camera that Chang is an AI character our team makes.
2. **"Sun checks your kitchen"**: the creator sends a real "health hack" they've seen; Sun Yoon answers it; Collab Reel.
3. **Recipe swap**: the creator cooks one of Sun's recipes in their own kitchen; we post Sun's version; both linked.
**What we give:** a free founding membership for the creator (a material connection: disclose it, §4.5), first look at the books, and the content itself. Paid collabs only with client approval and the BLITZ_OPS §4 contract and vetting.
**Collab post rules:** both accounts professional; the post carries "#ad" or "Paid partnership" where any value changed hands; the creator never claims results from our product (no "I got stronger with Strong Years" unless it's true, documented and labeled with typical-results language, SAFETY T-02); our characters' AI disclosure stays in frame.

### 4.2 Facebook page and group partners

**Who:** groups for fitness after 60, walking clubs, retirement communities, caregivers of aging parents, Korean-American and Chinese-American community cooking groups (cultural fit with Sun and Chang, run by real admins), senior-center pages.
**The ask:** permission (in writing, saved in the Partner sheet) to post a weekly "Chair Challenge Wednesday" thread as the Page, plus a monthly live Q&A with a real team member. No link unless the rules allow one.
**What we give admins:** a ready weekly post they approve, a free founding membership for each admin (disclose), and a group-only printable each month.
**Never:** join-and-spam, the same text pasted into many groups, posting without admin permission, or replying to members' health stories with offers (FUNNEL §4.14 applies in groups too).

### 4.3 Newsletter swaps (honest version)

During the runway we have no newsletter to swap: the waitlist consent covers only launch emails. So the runway trade is **content for mention**: we give senior-focused newsletters (local senior-center bulletins, retirement and caregiving newsletters, Substack writers over 60) a free, ready-to-run block: one of Sun's recipes with grams, or Chang's 8-minute chair routine as a printable, with the credit line "From Strong Years (AI characters Chang & Sun) · free Day 1 at {{DOMAIN}}/waitlist?ref=nl-{slug}". After launch, the member newsletter (with its own consent) can run true swaps.
Paid newsletter placements are advertising: client approval, governor caps, "Sponsored" label by the newsletter.

### 4.4 Affiliate program: PTs, physical therapists, yoga-for-seniors and tai chi teachers, senior-center instructors

- **Commission:** 30% of membership revenue for 12 months per referred member (canon; 40% is a client option). Also 30% of the ebook price.
- **Tooling [A, verify]:** a Shopify affiliate app that supports recurring commissions on Shopify Subscriptions orders (e.g. UpPromote, GoAffPro or Refersion; confirm recurring-commission support for subscription contracts before choosing). Each partner gets a link `{{DOMAIN}}/b?ref={code}` and a printable QR card for classes.
- **Who and where:** physical therapists and PT clinics doing community wellness classes; yoga-for-seniors, chair-yoga and tai chi teachers; YMCA and senior-center instructors; personal trainers specializing in 60+. BLITZ_OPS §5.3 has the sourcing lists.
- **Compliance:** written agreement (attorney-approved template, BLITZ_OPS §5.5); FTC disclosure on every recommendation ("I earn a commission if you join"); licensed clinicians must follow their own board's rules on financial interests and must not present the membership as treatment. If a referral could involve patients covered by Medicare/Medicaid, the client's attorney reviews anti-kickback exposure before the clinician joins [U: membership isn't a federally reimbursed item, but the attorney decides]. Partners make no claims beyond our published content.

### 4.5 FTC disclosure for paid or gifted shoutouts

- The Endorsement Guides (16 CFR Part 255, revised 2023) apply to any material connection: payment, free membership, free books, affiliate commission. The disclosure must be clear and conspicuous: at the start of the caption ("#ad" or "Paid partnership with Strong Years"), **said in the video** for video posts, and the platform tool switched on (IG/FB Paid partnership label; TikTok `brand_content_toggle` / branded-content setting) [V FTC guidance; platform tools V].
- Virtual influencers are covered; our own pages are our own advertising, so their AI disclosure is the issue there (done), not an endorsement disclosure.
- No fake or AI-generated reviews or testimonials anywhere (FTC 2024 rule; SAFETY T-01). Partner posts about results need real, documented experience plus typical-results language.

### 4.6 Outreach templates (the client sends; personalize line 1 every time; ≤20 DMs/day from any one account)

**A. Creator DM (Instagram/Facebook)**
> Hi {first name}, I'm {client name}, founder of Strong Years. Your {specific Reel, e.g. "stairs at 71"} is exactly the energy we built this for.
> Straight up: our coaches are AI characters, Chang Yin (74, retired welder) and his wife Sun Yoon, made by our team and labeled as AI everywhere. The exercises and recipes are real and every number comes with its study.
> Would you do one Collab Reel with us? Idea: you do the 30-second chair test on camera, Chang does his, viewers pick a side. You'd say on camera that Chang is AI. In return: a free founding membership, early copies of our two starter books, and if you'd rather be paid, tell me your rate and I'll be honest about whether we can.
> No pressure either way. Can I send a 20-second example?

**B. Creator email**
Subject: A Collab Reel idea (with an honest AI disclosure)
> Hi {first name},
> I run Strong Years, a daily strength-and-kitchen program for adults 55+, taught by two openly AI characters (Chang Yin and Sun Yoon) that our team creates. Everything is labeled as AI, every exercise has a chair version, and every number cites its study.
> I'd love one Collab Reel with you before we open on {{CHECKOUT_OPENS_DATE}}: {one-line idea tailored to them}. You'd keep full creative control of your side and say on camera that our characters are AI. We'd offer a free founding membership and early copies of the books; if you prefer a paid collaboration, send your rate card and we'll use a one-page agreement with the #ad disclosure built in.
> Here's an example of our content: {link}. Thank you for considering it,
> {client name}, Strong Years · {email} · {phone}

**C. Facebook group admin**
> Hi {name}, thank you for running {group}. I'm {client name} from Strong Years (our coaches Chang and Sun are AI characters, clearly labeled). Would you allow our Page to post one thread a week, "Chair Challenge Wednesday": a 30-second chair test, members post their number, no links unless you allow them? You'd approve every post. We'd give every admin a free founding membership and a group-only printable each month. If it's not a fit, no problem at all.

**D. Newsletter editor**
Subject: Free recipe/routine block for {newsletter}, no strings
> Hi {name}, I make Strong Years, daily strength and kitchen content for adults 55+, presented by two AI characters (labeled as AI everywhere). Would a ready-to-run block help your next issue? Options: Sun Yoon's 30-gram tofu-and-egg breakfast with gram counts, or Chang's 8-minute chair routine as a printable. Credit line only; no payment either way. If it ever fits, I'd love to talk about a proper swap once our member newsletter is live.

**E. PT / physical therapist / chair-yoga or tai chi teacher (affiliate)**
Subject: A partner program for your 60+ clients (30% recurring, 12 months)
> Hi {name}, I'm {client name}, founder of Strong Years: a daily 8–12 minute strength session with a chair version of everything, for adults 55+, plus recipes with the protein grams in. Our on-screen coaches are AI characters (clearly labeled), and every routine is built on published exercise guidelines for older adults.
> Many of your clients need something between your sessions. Our partner program pays 30% of membership revenue for 12 months for each member you refer, plus 30% of the starter books. You'd get a personal link and a QR card for your classes, and you'd disclose the commission when you recommend us (we give you the wording).
> It is not treatment and we never present it as therapy; you stay the professional. Would a 15-minute call this week work? {calendar link}

**F. Senior-center activity director**
> Hi {name}, could Strong Years donate a printable "8-Minute Chair Builder" and a free class kit to your center? Our coaches are AI characters, and the routines are built on published guidelines for older adults. If your members like it, we'd be glad to set up a free group access code for the center. No obligation.

**Follow-up (all):** one follow-up after 4 days, then stop. Log every contact, reply and permission in the Partner sheet (BLITZ_OPS §4.2).

---

## 5. Launch week

### 5.1 D0 hour by hour (ET)

| Time | Action | Owner |
|---|---|---|
| 05:30 | Final check: Shopify live (products, cells, the Subscriptions monthly plan + STARTER12 for cell B), `/b` redirect lands on the product page with the code applied, members provisioning webhook, counter reads the real inventory, cancel flow works. Go/no-go from LAUNCH_RUNBOOK.md §9. | Operator |
| 06:45 | Config flip: `RUNWAY_MODE=false` → bio links to launch mode, WAITLIST → BOOK variant, value flows' buttons → `/b`. | Operator |
| 07:00 | Waitlist launch email + push notification. Announcement posts: S176 (@changyin), S181 (@sunyoon.kitchen), S186 (@changandsun, pinned) on all platforms; broadcast channel message. | Pipeline (approved), Operator |
| 07:00–09:00 | Reply to comments on the three announcement posts every 15 minutes (templates; offer questions answered with the full terms or "the full terms are in the DM"). | Operator + reviewer |
| 10:00 | S177 (@changyin, terms out loud). Stories: counter screenshot #1. | Pipeline |
| 12:00 | Check: orders by cell, post-purchase take rate, refunds, DM errors, payment failures. | Operator |
| 13:00–21:00 | Value posts per the calendar; Stories Q&A answered by a real team member; counter screenshot #2 at 18:00. | Pipeline + Operator |
| 21:30 | Day report (§6.4 dashboard), flags for tomorrow. | Operator |

### 5.2 D+1 → D+6 mix (per page per day)

| Day | Offer posts (≤2) | Value posts | Email (waitlist, max 3 in 72 h after the launch email) | Other |
|---|---|---|---|---|
| D0 | Announcement (+ terms post on @changyin) | 4 | Opening email 07:00 ("Strong Years is open": the §5.3 message) | Push 07:00 |
| D+1 | Day-1-free post (S178), page 14 (S182), who-shouldn't-buy (S187) | 5 | Launch email 1 of 3 (09:00): "Day 1 is free, here it is" | — |
| D+2 | Why 5,000 (S180), not a diet book (S183), what "locked" means (S188) | 5 | Launch email 2 of 3 (09:00): "Your questions, answered" · Launch email 3 of 3 (20:00): "If it's not for you" (the last one) | Push reminder (the one allowed) 18:00 |
| D+3 | Day 4 stairs (S179), worth it? (S184), questions (S189) | 5 | None: the 72-hour window closed at 07:00; non-buyers go quiet unless they opted in to tips | Live Q&A with a real team member (optional) |
| D+4 | Gift (S185) on @sunyoon.kitchen | 5–6 | — | — |
| D+5 | — | 6 | — | Counter screenshot (real) |
| D+6 | End of launch week (S190, pinned on @changandsun) | 5 | — | — |

The consent text allows one email "when Strong Years opens, plus at most 3 launch emails in the 72 hours after that", so all three launch emails go out between D0 07:00 and D+3 07:00, and buyers are suppressed from them (they get E1–E3 in §5.4 instead). [Operator: set the ESP to enforce "≤3 launch emails within 72 h of the opening email" as a hard rule.]

### 5.3 The honest founding message (use verbatim in the launch email, the S186 caption and the pinned terms post)

> **Strong Years is open.**
> Start with the two starter books: Chang Yin's 7-Day Strength Reset and Sun Yoon's Strong Kitchen. {{EBOOK_PRICE}}, one-time, not a subscription, yours to keep.
> After checkout you'll see one optional offer, the Founding Membership: {{FOUNDING_PRICE}}/month. If you add it, {{FOUNDING_PRICE}} is charged that day for your first month, then it renews monthly at the same price until you cancel. Cancel online anytime, in two screens. 14-day money-back guarantee on the membership charge, once per person. Your founding price is locked for as long as you stay subscribed, pauses included.
> Founding membership is open to the first 5,000 members. The number on the page is the real count from our system. There's no countdown and no midnight price change. If we ever close the founding cohort before 5,000, we'll say so at least a week ahead.
> Chang Yin and Sun Yoon are AI characters made by our team. The exercises and recipes are real, and every number comes with its study. Check with your doctor before starting new exercise.

**Live counter rules:** the counter shows `founding_members_active` from the database (the same number the cap enforces), refreshed every 60 s; it's never rounded up, never animated toward 5,000 and never shown as "spots left" with a made-up number. Screenshots in Stories are real screenshots with the time visible.

### 5.4 How posts, emails, the ebook and the membership offer interlock

1. **Posts** create intent and a keyword comment; every offer post states the one-time price and, if it mentions the membership, all the terms (enforced by the validator in tools/build_content.py).
2. **DM** (BOOK flow) gives the link via `/b`, which assigns the sticky cell and carries attribution to Shopify.
3. **Shopify checkout** sells the books (cell A) or the books + first month as one subscription purchase with its auto-renew disclosure and consent box (cell B).
4. **Post-purchase page (cell A):** one-click Founding Membership offer, terms in full above the button, a "No thanks, take me to my books" link of equal prominence.
5. **Thank-you page:** download buttons first; the same offer below with full terms.
6. **3 onboarding emails to buyers** (separate from the waitlist emails; transactional + offer with consent from checkout):
   - **E1 (immediately):** "Your books are here" (download links, start with Reset Day 1 tomorrow morning, chair against the wall). Footer: the founding offer with full terms.
   - **E2 (day 2, 07:30):** "How was Day 1?" (one tip from Day 2, the 30-second chair test to write down). Middle: what members get each morning (a session at your level), with the full terms and the link.
   - **E3 (day 5, 07:30):** "Day 5: the stair" (tip) + the honest version: "If you finish the 7 days and want a new session every morning, here's the founding membership…" full terms, counter link. After E3, buyers who didn't join get the normal tips sequence only if they opted in.
7. **The books themselves** end Day 7 with a "What's next" page: retest your chair number; if you want daily sessions, the founding membership (full terms, QR + link). No pressure language.
8. **Members** are provisioned in the app from Shopify webhooks (`orders/paid`, `subscription_contracts/*`); the BOOK DM flow suppresses sales DMs for buyers and members.

---

## 6. Daily rhythm for 1–2 people + automation

### 6.1 Roles

- **Operator** (client or one VA): approvals, posting checks, comments, DMs that need a human, partner outreach, daily report. ~6–8 h/day in runway, ~10 h on D0–D2.
- **Reviewer** (the human in the compliance loop; can be the client): reviews everything the deterministic scanner or the mandatory LLM judge flags or marks ambiguous; reviews every offer post, myth-bust (MB-EX) and reply video before it publishes. ~1–2 h/day.
- With one person, the same person holds both roles, and the review SLA in §6.3 still applies; nothing publishes unjudged (CANON UPDATE).

### 6.2 The day (ET)

| Time | Task | Who |
|---|---|---|
| 06:30 | Read the overnight growth digest (Slack): winners, flags, account health, DM errors | Operator |
| 06:45 | Approve today's queue (the review app shows script, render, scanner + judge results, platform captions) | Reviewer |
| 07:00–21:00 | Posts publish on schedule; **first-60-minute comment replies** on every post (templates; health questions get the deflection + general answer; crisis → FUNNEL §4.14) | Operator |
| 09:00 | Approve remix briefs from yesterday's winners (≤3 per winner, other pages only) | Operator |
| 11:00 | Partner outreach block (§4.6): 20 personalized messages max per sending account; follow-ups | Operator |
| 13:00 | Reply-video pick (the day's best question → F09/F10 brief) | Operator |
| 15:00 | Second review batch (tomorrow's renders) | Reviewer |
| 17:00 | Boost queue check (launch onward): approve or reject WINNER boosts inside governor caps | Client |
| 21:00 | Daily report (dashboard snapshot + 3 notes) | Operator |

### 6.3 Automation and review SLAs

| Step | What runs | SLA / rule |
|---|---|---|
| Script + caption generation | Pipeline (W1 idea miner, W2 planner), library scripts first | Briefs ready 48 h ahead |
| Deterministic scanner | `workers/compliance` (blocked claims, S-02 terms, movement cues, hashtags) | Every script, before render; block = never renders |
| **Mandatory LLM judge** | Pipeline judge (Claude safety layer; not run from this build environment) | Every script and caption before render; anything flagged or ambiguous → human |
| Human review | Review app queue | Runway: within 4 working hours, 07:00–21:00 ET. Launch week: within 1 hour, 06:30–22:00 ET. Offer posts and MB-EX: always human. Crisis DMs: human acknowledges in 15 min, follow-up in 1 h (FUNNEL §4.14). |
| Uniqueness guard | `workers/uniqueness` (pHash, Chromaprint, embeddings; YouTube stricter) | Every render; fail → re-render |
| Publish | Official APIs / upload-post per PIPELINE §5.3, jittered | Human approval for every post until the page has 14 clean days, then `auto_publish` (PIPELINE §5.4) |
| Growth engine (hourly) | `n8n_growth_workflow.json` + `workers/growth`: metrics at 1/3/6/24/72 h → baselines → scores → classes | **Flags:** WINNER (score ≥1.5 × page baseline at ≥6 h, ≥1,000 views, ≥2 components) and breakout (≥500K views → WINNER at ≥3 h); LOSER pages; reach-per-post drop >30% week over week (ramp hold); restriction or strike signals; DM error rate; AI label missing. **Actions (all need a human):** 3 remix requests per winner for other pages; boost candidates into `v_boost_approval_queue` (default cap $50/day per boost, $250 ceiling); nothing spends unless `SPEND_ENABLED=1` and `GROWTH_DRY_RUN=0`. |

### 6.4 Dashboard (one screen; daily and cumulative)

**Reach:** views per post (median and P90) per page per platform; 3-s hold; average watch %; shares per 1K views; saves per 1K; follows per 1K; Trial Reel graduation rate.
**Intent:** keyword comments per 1K views by keyword; DM delivery and button-tap rate; link clicks; waitlist sign-ups → confirmations (by page, keyword, partner `ref`); referral confirms; push opt-ins.
**Money (from D0):** `/b` visits by cell; ebook orders and conversion by cell and source; post-purchase take rate; thank-you and email take rates; founding members (the real counter); MRR (canon definition); refunds (ebook, membership 14-day); cancellations; first-renewal survival (D+30).
**Partners:** contacts sent, replies, yeses, live collabs, partner-attributed waitlist confirms and buyers, affiliate members.
**Health:** AI label verified per account; restrictions, strikes, action blocks; TikTok and YouTube audit status; publishing failures; scanner/judge block rate; human edit rate; complaint and unsubscribe rates; crisis cases (count only).

**Leading-indicator targets for D0 (R = 21) [A]:** organic confirmed waitlist ≥ 865 (model central) and borrowed-audience confirms large enough that total D0 waitlist ≥ 4,700 if cell B is weighted up (the $10K-on-D+4 line in §0.1). Below 2,000 confirmed on D−3: tell the client that the D+4 milestone is unlikely and move the energy to partners rather than raising cadence.

---

## 7. Risks, mitigations and the critical path

### 7.1 Risks

| Risk | What could happen | Mitigation |
|---|---|---|
| New-account restrictions at volume | Action blocks, reduced distribution, checkpoints when 3 new pages jump to 6–9 posts/day | The §1.3 ramp (never compressed for a date); week-0 native pins and manual follows; one person logging in per device; Business Suite roles, no shared passwords; no proxies or anti-detect tools; jitter; stop raising cadence if median views/post drops >30% week over week (PIPELINE §5.4). |
| AI-label reach effects | Labeled AI pages might get less engagement even without an algorithmic penalty; an unlabeled page loses Reels/Explore/suggested reach | Label on from day one (unlabeled is the certain loss); disclosure woven in with charm (CHARACTERS §9); measure labeled reach weekly vs POSTDB baselines; Facebook-first for the 65+ buyer. |
| YouTube "inauthentic" reading | Template-sameness flags; no YPP for an AI persona on health topics | We don't depend on YPP; YouTube cap 4/day; strict remix cap; structural variety; never credentialed personas (§2.5). |
| TikTok AI handling | Labeling errors, unoriginal flags, private-only API until audit | `is_aigc` always; C2PA; upload-post until audit; TikTok is not the 65+ channel anyway. |
| Comment→DM restrictions | Meta limits DM features for spammy patterns | One private reply per comment; no cold DMs; opt-out honored; no link in public replies. |
| Collab/partner misconduct | A partner makes health claims or skips #ad | One-page agreement with the claims list and disclosure clause; we review their caption before posting; remove the collab tag if they don't fix it. |
| Organic underperformance | The waitlist on D0 is in the hundreds, not thousands | Honest expectations (§0.1); partners first; cell B weighting option; paid boosts only of proven winners under the governor; don't fake urgency to compensate. |
| Impersonators/clones | Fake "Chang" accounts selling things | Pinned post names our only official handles; weekly impersonation reports. |
| Page loss | A page is disabled | Owned audience first (waitlist, email); appeal through Account Status; backup handles **planned, not created** (ACCOUNT_SETUP §9.4) to avoid looking like a network. |

### 7.2 Backup handles

Planned names only (ACCOUNT_SETUP §9.4 lists them). We do **not** create unused accounts: idle duplicates under the same brand read as network behavior and can't be warmed honestly. If a page is lost, the client creates the backup then, labels it, posts the "We moved" note from the remaining pages, and starts week 1 of the ramp.

### 7.3 Critical-path checklist for D−21 (anything unchecked moves D0)

| # | Item | Owner | Done when |
|---|---|---|---|
| 1 | **Reference pack locked** (CHARACTERS §13.1: Chang and Sun faces, wardrobe sets, 8 home sets, Frank, Mandu) | Content lead | Pack versioned; drift check passes on 20 test renders |
| 2 | **Voices designed** (ElevenLabs voice design, never cloned; CHARACTERS §13.3) | Content lead | Both voices approved by the client on 3 sample lines each |
| 3 | **First 150 posts rendered and judged**: runway weeks 1–2 for 3 pages (105 masters) + 21 Trial Reel variants + 24 buffer; includes S151–S175 | Pipeline + Reviewer | 150 in the review app with scanner pass, judge pass, human approval, C2PA present, burned-in AI tag |
| 4 | **Accounts created and configured** (ACCOUNT_SETUP.md): IG, FB Page, TikTok, YouTube, Threads, X for the 3 pages; AI labels on; 2FA; Business Manager | Client | Verification checklist in ACCOUNT_SETUP §10 complete |
| 5 | **Bio links in waitlist mode** (`/go`, `/tt`, YT description) | Client + DEV | Tapping each bio link reaches the waitlist page with the right `p=` |
| 6 | **Waitlist live** (double opt-in, Day 1 starter, referral bonus, push opt-in, consent text exact) | DEV | A live test signup confirms and receives exactly one email |
| 7 | **ManyChat runway flows** (WAITLIST §4.18 + runway link rule on all value flows; §4.14 classifier) | Operator | Live comment tests on each keyword from a test account |
| 8 | **API access**: IG/FB publishing tokens via the system user or OAuth; TikTok app audit submitted; YouTube audit submitted; upload-post connected as fallback | Client + DEV | Test post to a private/test destination on each platform |
| 9 | **Growth engine in dry run** with metrics ingestion working | DEV | Hourly digest arriving in Slack |
| 10 | **Partner sheet + wave-1 outreach list** (60 creators, 30 groups, 20 newsletters, 40 affiliate prospects) | Operator | List complete with personalization line per contact |
| 11 | **Pinned posts** rendered (PIN 1, PIN 2 FALLBACK) for native posting in week 0 | Pipeline | Approved files in the shared drive |
| 12 | **Decisions logged**: R, `{{CHECKOUT_OPENS_DATE}}`, cell weighting | Client | In BRIEF.md decision log |

**Before D0 (not D−21):** Shopify store, products and cells, the Subscriptions monthly plan + STARTER12/STARTER12S (cell B), `/b` redirect verified on the live theme (product page, code applied, attributes on the test order), members-area webhooks, counter, cancel flow, books final and served watermarked by the members app, onboarding emails E1–E3, attorney review of terms (LAUNCH_RUNBOOK.md §9 go/no-go). The post-purchase app is not a launch prerequisite (off by default).

---

## 8. Sources (accessed Oct 1 2026)

- Instagram AI-generated profile label: [TechCrunch, Aug 31 2026](https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/); [Implicator](https://www.implicator.ai/instagram-will-cut-the-reach-of-ai-personas-that-skip-its-new-label/); [MediaPost, Sep 1 2026](https://www.mediapost.com/publications/article/417580/instagram-limits-reach-for-creator-profiles-withou.html)
- Instagram Trial Reels: [Social Media Today, Apr 2 2026](https://www.socialmediatoday.com/news/instagram-allows-creators-to-schedule-trial-reels/816549/); `trial_params` / `graduation_strategy` and the 100-posts-per-24-h limit: [Meta, Instagram content publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/)
- Instagram Collab posts: [Sked Social](https://skedsocial.com/blog/instagram-collaboration-feature)
- Instagram broadcast channels (eligibility is secondary): [SocialRails](https://socialrails.com/social-media-terms/instagram-broadcast-channels)
- Comment-to-DM private replies, 24-hour window, human-agent tag: [Helm](https://helm.vision/blog/instagram-dm-comment-automation-rules/)
- New-account limit estimates: [Social Champ](https://www.socialchamp.com/blog/instagram-limits/)
- Social media use by age: [Pew Research Center, Nov 20 2025](https://www.pewresearch.org/internet/2025/11/20/americans-social-media-use-2025/) ([report PDF](https://www.pewresearch.org/wp-content/uploads/sites/20/2025/11/PI_2025.11.20_Social-Media-Use_REPORT.pdf)). Note: the 65+ YouTube figure we extracted (27%) looks like a daily-use number; verify in the PDF before quoting it.
- Facebook feed and Reels (secondary): [SocialPilot](https://www.socialpilot.co/blog/facebook-algorithm); Meta unoriginal-content policy: [TechCrunch, Jul 14 2025](https://techcrunch.com/2025/07/14/following-youtube-meta-announces-crackdown-on-unoriginal-facebook-content)
- Threads: [Social Media Today, Jun 16 2026](https://www.socialmediatoday.com/news/threads-reaches-500m-user-milestone/823099/)
- X (secondary): [SocialPilot](https://www.socialpilot.co/blog/twitter-algorithm)
- TikTok `is_aigc`, private-only for unaudited clients, rate limit: [TikTok for Developers, Direct Post reference](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post); AI label rules (secondary): [Cinerads](https://www.cinerads.com/blog/tiktok-ai-content-policy); Spark Ads authorization (secondary): [Novoads](https://novoads.ai/en/blog/tiktok-spark-ads-guide)
- YouTube July 16 2026 clarification: [TechCrunch, Jul 20 2026](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/); secondary detail: [CreatorBlade](https://creatorblade.com/blog/youtube-inauthentic-content-policy-2026-stay-monetized); July 2025 renaming of "repetitious" to "inauthentic": [PPC Land](https://ppc.land/youtube-clarifies-inauthentic-content-policy-changes/); upload quota and audit: [YouTube Data API, videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert)
- FTC: [FTC's Endorsement Guides: What People Are Asking](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking)
