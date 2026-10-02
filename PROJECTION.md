# PROJECTION.md: the full end-to-end roadmap and every metric, day 0 to 180
Generated from `tools/montecarlo.py` (300 simulated launches per level; per-post power-law reach, per-platform ramps, viral-hit effects on page baselines, the scale ladder and the $30K spend gate on retained MRR). Companion: `economics.xlsx` sheets Organic_Max (R30–R36) and Projection_Aggressive; `data/mc_{conservative,central,breakout}.csv` hold the p10/p50/p90 bands for every column. Every input is an ASSUMPTION within the cited ranges in BLITZ.md §13–14 and ENGINE_100X.md; the first 72 hours of live data replace them.
## 1. How reach is modeled (what changed from the earlier averages)
- Each post gets its own draw from a heavy-tailed (Pareto) distribution around the page's median. Most posts land at 0.5–2× the median; about 1 in 200 (central) gets a 20–300× hit.
- Pages start low: a brand-new page's median is ~500 views per post (central), ~250 (conservative), ~900 (breakout), and ramps ×1.45 every 14 days (central) until the 40K per-video cap and the 600K/day page ceiling.
- Platforms differ: Facebook ramps fastest and most reliably for 65+ (0.9× IG median, steadier tail); TikTok is the biggest lottery (0.6× median, fattest tail); YouTube Shorts is slow then compounds (0.4×); Threads/X are text-weight (0.12×).
- A hit raises the page's baseline ×1.6 for the following two weeks, decaying 4%/day.
- Trial Reels reach 35% of a main post's audience (non-followers) with variant decay; 10% graduate at 2.5× reach.
- Because 192–511 posts a day are 192–511 draws, the network total is far steadier than any single post; the real uncertainty is in the level (which world we're in), not the day-to-day.
## 2. The roadmap, day by day
| Phase | Days | What happens | Trigger |
|---|---|---|---|
| Runway | −7 to 0 | 4 pages post 6 masters + 10 Trial Reels/day each; free waitlist CTA; keyword→DM live; founding checkout opens to waitlisters on day −4 | Characters + voices approved |
| Open | 1–3 | Public checkout; waitlist buys (10% in 72 h central); warm lists mailed (1.5% over 14 d); ~190K–780K views/day | Day 1 |
| First rung | ~day 5–7 | Retained MRR ≥ $10K → page 5 opens, 8 masters/page, Trial Reels to 20/page | Governor, automatic |
| Gate | ~day 12–14 | Retained MRR ≥ $30K → pages 6–7 + Spanish open, 9 masters/page; paid shoutouts/boosts allowed under the 25% all-in cap | Governor, automatic |
| Learning | 14–30 | Scorecard has 2 weeks of our data; weekly gate refit; winners remixed across 7 pages in 24 h; coached program selling from day 10 | Automatic |
| Scale | 30–60 | Views approach page ceilings; growth shifts to retention, ascension, Spanish; second show at $50K | Governor |
| Compound | 60–180 | Renewals compound; cash runs ahead of retained MRR; PT/DE clones at $100K | Governor |
## 3. Central scenario, the planning line (p50; p10–p90 in brackets)
| Day | Pages | Posts/day | Views/day | New buyers/day | Active members | Booked MRR | **Retained MRR** | Cash collected | Cost/day |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 192 | 190,286 [154,471–372,295] | 109 | 109 | $2,584 | **$1,292** [1,232–1,594] | $-13,811 | $77 |
| 3 | 4 | 192 | 474,402 [345,152–914,989] | 149 | 398 | $9,447 | **$4,724** [4,325–5,589] | $-10,601 | $77 |
| 7 | 4 | 192 | 781,695 [568,850–1,260,925] | 142 | 944 | $22,411 | **$11,206** [9,997–12,985] | $-4,555 | $77 |
| 14 | 5 | 340 | 1,425,254 [1,114,872–1,911,522] | 232 | 2,420 | $61,144 | **$32,432** [30,205–35,684] | $11,738 | $127 |
| 21 | 7 | 511 | 2,199,404 [1,812,634–2,625,363] | 312 | 4,404 | $116,765 | **$64,414** [60,988–69,469] | $31,693 | $549 |
| 30 | 7 | 511 | 2,687,973 [2,305,228–3,044,937] | 385 | 7,606 | $209,172 | **$118,849** [113,329–125,041] | $61,965 | $993 |
| 45 | 7 | 511 | 3,545,668 [3,301,009–3,808,975] | 517 | 13,097 | $369,149 | **$229,000** [222,260–236,127] | $151,925 | $1,896 |
| 60 | 7 | 511 | 4,033,929 [3,880,246–4,197,687] | 598 | 18,987 | $543,339 | **$361,577** [354,068–369,531] | $273,085 | $2,992 |
| 90 | 7 | 511 | 4,200,000 [4,200,000–4,200,000] | 649 | 29,790 | $870,518 | **$645,443** [638,066–652,929] | $638,277 | $5,358 |
| 120 | 7 | 511 | 4,200,000 [4,200,000–4,200,000] | 676 | 39,113 | $1,155,132 | **$919,053** [911,889–926,477] | $1,155,032 | $7,640 |
| 180 | 7 | 511 | 4,200,000 [4,200,000–4,200,000] | 727 | 57,007 | $1,701,441 | **$1,446,662** [1,439,833–1,453,717] | $2,632,737 | $12,041 |

Probabilities (central): $10K retained by day 7: 90%; $30K by day 14: 92%; $100K by day 45: 100%; $250K by day 90: 100%.

## 4. Views by platform, central p50

| Day | Instagram | Facebook | TikTok | YouTube | Threads | X |
|---|---|---|---|---|---|---|
| 1 | 62,619 | 64,128 | 25,098 | 8,675 | 4,731 | 4,450 |
| 7 | 251,071 | 257,190 | 99,237 | 29,340 | 18,249 | 18,488 |
| 14 | 522,675 | 440,632 | 180,909 | 42,189 | 32,363 | 33,212 |
| 30 | 1,007,791 | 959,102 | 354,165 | 71,775 | 70,177 | 69,283 |
| 60 | 2,216,320 | 2,369,812 | 722,270 | 125,343 | 144,605 | 146,700 |
| 90 | 2,669,743 | 3,315,565 | 806,512 | 129,556 | 179,981 | 189,788 |

## 5. Conservative and breakout bands (retained MRR p50)

| Day | Conservative | Central | Breakout |
|---|---|---|---|
| 3 | $1,104 | $4,724 | $26,078 |
| 7 | $1,741 | $11,206 | $101,458 |
| 14 | $3,596 | $32,432 | $329,048 |
| 30 | $6,218 | $118,849 | $1,225,040 |
| 45 | $7,948 | $229,000 | $2,211,543 |
| 60 | $10,826 | $361,577 | $3,211,119 |
| 90 | $21,335 | $645,443 | $5,180,924 |
| 180 | $76,962 | $1,446,662 | $11,212,782 |

Conservative = a new-account restriction world: median 250 views/post, slow ramp, Trial Reels at 20% reach, funnel at half; no milestone inside 90 days; the fallback is Facebook volume + seeded lists. Breakout = everything at the top of the cited ranges; treat anything past day 45 there as a ceiling.

## 6. The funnel, every number (central | conservative | breakout)
| Step | Central | Conservative | Breakout | Source |
|---|---|---|---|---|
| Posts/day at 7 pages | 511 | 511 | 511 | canon 5 (9 IG + 20 trials + 13 FB + 9 TT + 4 YT + 9 TH + 9 X per page) |
| Median views/post, new page | 500 | 250 | 900 | ASSUMPTION; new-account warm-up |
| Ramp per 14 days | ×1.45 | ×1.25 | ×1.65 | ASSUMPTION; BLITZ §13.2 ×1.6/30 d |
| Per-video cap / page ceiling | 40K / 600K | 24K / 360K | 80K / 1.2M | ASSUMPTION |
| Hit probability per post | 1/200 (20–300×) | 1/400 | 1/120 | ASSUMPTION from Yang Mun's distribution |
| Trial Reel reach vs main | 35% | 20% | 60% | ASSUMPTION |
| Graduation rate / uplift | 10% / 2.5× | 6% | 18% | ASSUMPTION |
| Comments per view (winners / avg) | 1.2% / 0.4% | | | Yang Mun DB |
| Keyword comments share | 25% | | | ENGINE_100X |
| DM delivered / link clicked | 95% / 45% | | | ENGINE_100X DM benchmarks |
| Link clicks per view (all sources) | 0.4% | 0.2% | 0.6% | BLITZ §1 |
| Landing load (in-app browser) | 70% | 65% | 75% | BLITZ §1 |
| Visitor → $12 cell-B buyer | 5% | 2.5% | 8% | tripwire 1.5–5% cold, 8–15% warm |
| Runway waitlist → buyer in 72 h | 10% | 5% | 15% | launch-to-waitlist 5–15% |
| Borrowed list → buyer over 14 d | 1.5% | 0.5% | 3% | ASSUMPTION; never opted in for this brand |
| First-renewal survival (day 30, $25) | 50% | 40% | 60% | OFFER retention model |
| Monthly churn after | 7% | 10% | 5% | |
| Coached take ($147) from day 10 | 5% | 3% | 7% | ASSUMPTION |
| Realization (fees, failed cards) | 95% | | | |
| Paid: gate / cap / $ per member | $30K retained / 25% all-in / $85 | | | canon 5; BLITZ Payback |
| Generation per master / variant | $1.28 / $0.225 | | | STACK_FINAL Tier B |
| Fixed per day / review per post | $16 / 20 s at $20/h | | | COSTS.md |

## 7. Billing mechanics
- Day 0: $12 (STARTER12 first-cycle discount on the $25 founding plan; Shopify Payments 2.9% + 30¢). Books delivered watermarked by the members app; first founding month starts.
- Day 30: $25 renewal; 50% survive (refund window + cancels). Day 60, 90…: $25 with 7%/month churn.
- Booked MRR = members × $25 × 0.95 from day 0 (canon). Retained MRR applies first-renewal survival to all cohorts: the planning number. Cash = $12 today + $25 at each renewal, ×0.97, minus costs.
- Coached: $147/mo from day 10 for 5% of members ≥10 days old. Labs $399 (3%) and supplements (month 4+) are outside MRR.

## 8. What to watch in the first 72 hours (these replace the assumptions)
1. Views per Trial Reel and per main post, by platform, at 1/6/24 h.
2. Link clicks per view and landing loads.
3. Landing → buyer rate on the $12 page.
4. Waitlist conversion.
If all four land at central or better, the day-33/day-58 milestones hold. If Trial Reel reach caps near 5/day, volume shifts to Facebook the same day. If the funnel is at conservative, the seeded lists and the spend gate (which stays shut) decide the pace.
