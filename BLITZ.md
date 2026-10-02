# BLITZ.md: engineering for MRR speed (v6: §13 organic-first plan on the Shopify ladder per CANON UPDATE 2; v5 R7 launch plan and the $1-trial runs retained as history)

**Model.** `economics.xlsx` has three blitz sheets:
- **Blitz**: a daily model over **360 days**, with **19 runs** and per-run inputs. Arm-B members are tracked at their cohort's price, so mixed price cells are exact.
- **Payback** (new): channel-by-channel payback, the funding decision for R6/R17, and the graduation thresholds.
- **Milestones**: a flat-rate solver on the upside inputs.
- **Blitz_Plan**: the planning base, the rules, the annual-offer comparison and the milestone table.
- **Organic_First** (Oct 1 2026): the organic-first plan on the CANON UPDATE 2 Shopify ladder (ebook → post-purchase membership / subscription-inclusive $12), runs R20–R26, runway and waitlist solver, amplification caps, sensitivity, configuration ladder and sources. §13. Values come from `tools/organic_engine.py`; the result rows are live formulas over the daily rows.

**Chart data.** `mrr_blitz_daily.csv` gives day 1–360 with upside, central, profitable-6-month (R6) and profitable-12-month (R17) columns, plus `r7_central_MRR`, `r7_upside_MRR`, `r7_central_cash` and `r7_upside_cash`: members, MRR, retained MRR, spend, cash and reserve held. `r20_MRR` … `r26_MRR` and `r20_cash` … `r26_cash` carry the §13 organic-first runs (day 1 = checkout opens; runway opex is already in the cash).

All earlier sheets are unchanged. R15 keeps the audit-verified upside reference ($10,169 on day 4, $42,922 on day 14, $92,827 on day 30). The quick lever runs in §8 use the same engine in Python, which matches the workbook to the dollar on R5 and R4.

**Definitions.** Day 1 is the first paid day. MRR is active monthly members × price × 0.95, plus Essentials at $12 and annual members at price ÷ 12. **Retained MRR** is the MRR expected to survive the first renewal (days 31–60). "Cash" excludes the rolling reserve, which is held and not spendable.

**The annual offer (per the funnel/offer docs).** The founding annual is **$249, offered from day 35 to members who have already renewed once**. The take rate is 5%, which is an *assumption*: measure it. This replaces the earlier "$99 at renewal 1". It now applies to both R5 (central) and R4 (upside).

## 0. Summary: the launch plan (R7) against the alternatives (live in Blitz_Plan)

| Run | MRR d4 | MRR d14 | MRR d30 | MRR d90 | MRR d180 | Retained MRR d30 | Peak cash need (360 d) | Payback (cash breakeven) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **R7 LAUNCH PLAN, central inputs** (3-cell test days 1–10 at Meta $3K/day; day-10 gate **fails** → R17 settings) | **$1.7K** | **$8.5K** | **$22.8K** | **$62.0K** | **$111.5K** | **$14.0K** | **−$380K** (day 215) | Cash-flow positive from **day 216**; breakeven after day 360 | **The plan.** If live data looks like the central case, you pay ~$30K of Meta for the 10-day test and land on the profitable-at-12-months track. |
| **R7 LAUNCH PLAN, upside inputs** (same test; gate **passes** → R4 settings from day 11) | **$2.9K** | **$28.3K** | **$82.0K** | **$154.8K** | **$258.7K** | **$46.5K** | **−$431K** (day 135) | Cash-flow positive from **day 136**; **breakeven day 303** | **The plan if the upside is real.** It gets within ~$11K of R4 by day 30 and within 3% by day 90, having risked only 10 days of $3K/day before committing. |
| **R4 Upside** ($30, charge-today, $8K/day Meta + 4 shoutouts/day) | $10.2K | $42.9K | $92.8K | $159.5K | $262.0K | $52.4K | **−$460K** (day 125) | Cash-flow positive from day 126; **breakeven day 306** | **The target plan, but only once the live data graduates (§11).** On central inputs the same spend never pays back. |
| **R5 Central, max-MRR** ($25, same spend, kill rule) | $5.4K | $19.7K | $41.6K | $71.6K | $117.5K | $23.4K | **−$1.01M and still falling on day 360** | **None**: paid media per member ($161–174) exceeds 12-month contribution ($111) | **Not a business that pays back.** Fastest central MRR, bought at a loss. |
| **R6 Central, profitable** (payback ≤ 6 months: warm lists + organic + affiliates only, $1 trial arm, no Meta, no shoutouts) | $0 | $1.3K | $2.6K | $7.4K | $19.6K | $1.6K | **−$118K** (day 252; fixed opex, not media) | Cash-flow positive from day 253; the fixed-cost hole isn't repaid within 360 days | **Pays back per channel, but it's tiny.** No paid channel pays back in ≤ 6 months on central inputs. |
| R17 Central, profitable at ≤ 12-month payback (arm A; Meta $1.5K/day + 4 shoutouts/day) | $0 | $5.3K | $21.0K | $61.2K | $110.9K | $13.0K | −$369K (day 222) | Cash-flow positive from day 223; breakeven after day 360 (−$253K on day 360, recovering) | **The practical profitable plan:** channel payback about 8 months; 85–95% of R5’s MRR from day 90 on, at about a third of the cash hole. |
| **R20 Organic-first, central, cell B (LAUNCH DEFAULT)** (CANON UPDATE 2/3 ladder: "$12 today = books + first month, then $25/mo" as one subscription purchase on the free Shopify Subscriptions app's founding plan + the STARTER12 first-payment code; 7 pages, 6 posts/day/page, 14-day runway waitlist, lists 20K/10K, affiliates, **no media**; §13) | $2.1K | $4.6K | $9.0K | $30.2K | $83.6K | $4.6K | **−$84K** (day 121) | Cash-flow positive from day 125; breakeven day 235 | **The honest organic baseline.** MRR counts cell-B members at $25 from day 1; read the retained line (50% survive the first $25 charge). The ebook cash is inside the $12. |
| R21 Organic-first, upside, cell B (upside conversion inputs: ebook 8%, subB 0.85, first renewal 58%; 9 posts/day/page, organic ×1.75) | $7.6K | $16.3K | $31.0K | $114.2K | $398.1K | $18.2K | −$35K (day 35) | Cash-flow positive from day 41; **breakeven day 90** | Self-funding almost immediately; $100K MRR on day 85 with zero media. |
| **R22 Organic-first, central, cell A (TEST CELL)** ($12 one-time books → founding offer on the thank-you page + 3 emails, 4% later catches; the one-click post-purchase page is OFF at launch; otherwise R20) | $0.1K | $0.2K | $0.5K | $1.7K | $4.4K | $0.3K | −$90K (day 191) | Cash-flow positive from day 192; no breakeven within 360 days | **~1/18 of R20's MRR** at the same traffic; it earns more ebook cash per visitor ($9.4K vs $6.6K by day 30). With the post-purchase page switched on and approved (12% of 70% eligible orders) it reaches $1.4K on day 30. |
| R23 = R20 + boost/retarget cap $1,500/day + 2 shoutouts/day | $6.7K | $26.3K | $58.9K | $164.0K | $316.3K | $30.1K | −$185K (day 95) | Cash-flow positive from day 96; breakeven day 187 | **The closest honest configuration to the dates on central inputs:** $10K on day 6, $50K on day 26, $100K on day 59. Boosts, retargeting and shoutouts all pay back on cell B. |
| R24 = R23 + §11 graduation to cold Meta | = R23 | = R23 | = R23 | = R23 | = R23 | = R23 | = R23 | = R23 | **Gate fails on central cell-B inputs** (cold Meta ≈ $102 per net paying member net of ebook profit vs a $68 12-month contribution). It passes only on upside cell-B inputs: then $104K on day 30 at −$385K on R20 settings, $182K at −$361K on R23 settings (§13.6). |
| R25 = R20 with the $7 ebook cell | $2.5K | $5.7K | $11.6K | $39.4K | $119.8K | $5.9K | −$82K (day 114) | Cash-flow positive from day 119; breakeven day 213 | +29% MRR, −12% front-end cash vs $12 ($7 today, then $25). |
| R26 = R20 with the $15 ebook cell | $2.0K | $4.2K | $8.2K | $27.1K | $69.7K | $4.2K | −$84K (day 125) | Cash-flow positive from day 126; breakeven day 243 | −9% MRR, +6% front-end cash vs $12. |

Read with §10 (R6/R17 construction), §11 (graduation), §12 (R7 launch plan) and **§13 (organic-first plan on the Shopify ladder; R7, R17 and R4 keep the superseded $1-trial / charge-today structure and are retained as history)**.

**How the launch plan compares:**
- **Central:** R7 gives up $3.7K of day-4 MRR, $11.2K on day 14 and $18.8K on day 30 against R5 max-MRR. It converges by day 180 ($111.5K vs $117.5K) with a peak cash need of −$380K instead of −$1.01M, and it turns cash-flow positive (R5 never does).
- **Upside:** R7 trails R4 by $7.3K on day 4, $14.6K on day 14 and $10.8K on day 30. It's even by day 90–180 and needs $29K less peak cash.

---

## 1. Planning base: R5 CENTRAL (R4 is the UPSIDE case)

| Input | Upside (R4) | **Central (R5)** | Source of central value |
|---|---|---|---|
| Launch price | $30 | **$25** | The default on every page |
| Arm-B factor (charge-today purchase rate ÷ trial-start rate) | 0.45 | **0.40** (sensitivity 0.35–0.45: R11/R12) | Adapty: trials beat direct purchase in health & fitness |
| Shoutout link clicks per view | 0.6% | **0.4%** | 0.6% was unbenchmarked |
| Click → landing-page view | 100% | **85%** | Meta counts link clicks that never load |
| CPM | $18 | **+10% (Q4)** | Oct–Nov launch |
| Organic volume | 100% | **30%** | 3-page warm-up |
| Arm-B refunds | 10% | **12%** | Instant PDFs + self-serve refunds |
| Warm SMS | on | **off** | TCPA consent unproven |
| Kill/scale rule | off (never binds at $30) | **on** | §3 |
| Founding annual | $249 from day 35, 5% | $249 from day 35, 5% | Offer docs |
| Save offers (25% of cancellers; half → $12 Essentials, half pause) | off | **on** | OFFER §5.4 |

## 2. Central vs upside

| MRR | Day 4 | Day 14 | Day 30 | Day 60 | Day 90 | Day 180 |
|---|---|---|---|---|---|---|
| **R5 Central** | **$5.4K** | **$19.7K** | **$41.6K** | $56.2K | **$71.6K** | $117.5K |
| R5 retained (survives renewal 1) | $2.8K | $10.6K | **$23.4K** | $42.2K | $57.2K | $101.8K |
| R16 Central, plan as written (no rule/annual/saves; was R6) | $5.7K | $22.9K | $49.4K | $64.7K | $81.1K | $124.9K |
| R11 Central, arm-B 0.35 | $4.8K | $13.9K | $27.9K | $38.3K | $49.2K | $82.2K |
| R12 Central, arm-B 0.45 | $6.4K | $25.8K | $55.5K | $73.9K | $93.7K | $152.1K |
| **R4 Upside** | $10.2K | $42.9K | **$92.8K** | $125.0K | **$159.5K** | $262.0K |
| R4 retained | $5.3K | $23.4K | $52.4K | $93.2K | $126.2K | $223.2K |

| Cash (excl. reserve) | Day 4 | Day 14 | Day 30 | Day 90 | Day 180 | **Low point** | Reserve held |
|---|---|---|---|---|---|---|---|
| **R5 Central** | −$38K | −$115K | −$238K | −$488K | −$753K | **none within 360 days**: −$1.01M on day 360 and still falling | $40K on day 180 |
| **R4 Upside** | −$40K | −$127K | −$260K | −$426K | −$413K | **−$460K on day 125**; cash-flow positive from day 126, breakeven day 306 | $68K on that day |

First day reaching each MRR level:

| | $10K | $50K | $100K | $500K |
|---|---|---|---|---|
| R5 Central | day 8 | day 48 | day 144 | not within 360 days |
| R4 Upside | day 4 | day 17 | day 36 | not within 360 days |

The $249 annual brings forward upside cash: the low point moves from −$506K on day 155 (no annual, R15) to −$460K on day 125.

**What this means:**
- On central inputs, charge-today at $25 is about break-even on a 24-month view: paid media per net member is $161–174 against a $155 24-month contribution.
- Sustained paid spend keeps consuming cash through day 180, so **size the cash plan to the 180-day line.**
- The $1 trial (arm A) books less MRR by day 30 but more by day 90, and leaves a ~$246K smaller hole. It's the fallback if the arm-B factor reads ≤ 0.40.

## 3. The kill-rule contradiction: lines re-derived *and* the cut modelled

The thresholds come from unit economics:
- **SCALE** = 12-month contribution per net member.
- **CUT** = 24-month contribution per net member.
- Days 1–7 get a ×1.15 learning allowance.

| | At $25 | At $30 |
|---|---|---|
| SCALE (spend steps back toward plan at +20%/day) | ≤ $111 | ≤ $132 |
| HOLD | $111–155 | $132–185 |
| CUT (2 days above the line → Meta −30%) | > $155 | > $185 |

**How each case lands:**
- **Upside:** $112 per net member on days 4–10. That's inside SCALE, so the rule never fires.
- **Central:** $174. The rule fires on day 4, and Meta runs at $5,600/day instead of $8,000.
- **Cost of the rule:** −$7.8K of day-30 MRR, and about $190K of cash saved by day 180 (R16 vs R18, formerly R7).
- **I didn't loosen the lines to make the central case pass.** Loose lines would hide exactly the risk the audit found.

## 4. Retained run-rate

Report retained MRR next to every MRR claim:
- **Central:** $41.6K MRR on day 30 → **$23.4K retained**.
- **Upside:** $92.8K → **$52.4K retained**.
- **Day 14, net of open refund windows:** $18.3K central / $40.4K upside.

## 5. Founding annual: $249 from day 35 vs $99 at renewal 1 (Blitz_Plan, runs R5/R13 and R4/R14)

| | Central $249 d35 (R5) | Central $99 @R1 (R13) | Δ | Upside $249 d35 (R4) | Upside $99 @R1 (R14) | Δ |
|---|---|---|---|---|---|---|
| MRR day 30 | $41.6K | $41.6K | 0 | $92.8K | $92.8K | 0 |
| MRR day 90 | $71.6K | $70.3K | **+$1.3K** | $159.5K | $156.7K | **+$2.8K** |
| MRR day 180 | $117.5K | $114.8K | **+$2.8K** | $262.0K | $256.5K | **+$5.6K** |
| Cash day 30 | −$238K | −$238K | 0 | −$260K | −$260K | 0 |
| Cash day 90 | −$488K | −$486K | −$2.3K | −$426K | −$423K | −$3.6K |
| Cash day 180 | −$753K | −$751K | −$1.2K | −$413K | −$413K | +$0.4K |
| Annual members day 180 | 202 | 700 | | 395 | 1,380 | |

- **$249 wins on MRR.** Each switcher books $20.75/month instead of $8.25/month.
- **It's roughly neutral on cash.** There are fewer switchers, each paying 2.5× the price.
- **Neither version moves day-30 MRR.** The only thing $99-at-renewal-1 did better was catch would-be churners, and save offers now cover that.
- The 5% take at $249 is an assumption. Each ±1 point is worth about ±$0.1K of day-180 MRR and ±$7.5K of day-180 cash in the central case. It's a cash lever, not an MRR lever.

## 6. Milestones under the central case

These runs override the kill rule, use $25 and 20K/10K warm contacts, and stop paid spend after day 30.

| Milestone | Spend / mix needed | Media to target day | Cash on target day | Afterwards | **Verdict** |
|---|---|---|---|---|---|
| $10K by day 4 (R8) | Meta **$16K on day 1**, +20%/day to $20K; 4 shoutouts/day | $77K | −$86K | Held to day 30: $85.9K MRR, −$639K | **Stretch.** Needs a proven account able to spend $16K on day 1. |
| $50K by day 14 (R9) | Meta $16K→$30K/day; 6 shoutouts/day | $396K | −$396K | −$901K by day 30 | **Not credible at a $500K cap** |
| $100K by day 30 (R10) | Meta $12K→$25K/day; 6 shoutouts/day | $779K | −$752K | Retained $56K; MRR $59K by day 60 without further spend | **Not credible at a $500K cap** |
| $500K | none within 180 days | | | | **Not credible within 180 days** |

---

## 7. The 10 biggest single-input levers (central, Δ vs R16's $49.4K day-30 MRR)

1. Meta at $12K/day: +$13.1K (the cash low is $333K worse)
2. Shoutouts at 4/day vs none: +$12.4K
3. No click-loss: +$8.2K
4. $30 vs $25: +$6.7K
5. Arm-B factor ±0.05: ±$6.2K
6. Shoutout link rate 0.6%: +$6.2K
7. Arm A instead of arm B: −$6.3K on day 30, but +$13.1K on day 90 and a $246K smaller hole
8. Unignorable at 100K: +$5.8K
9. Fresh ad account: −$4.3K
10. Q4 CPM: −$3.4K

## 8. Levers that could actually close the gap (central R5 basis: $41.6K day 30 / $71.6K day 90 / −$753K day-180 cash)

Each row changes one thing on R5, which has the kill rule on, so the rule responds to changed unit economics.

| Lever | Setting | Day 4 | Day 14 | Day 30 (Δ) | Day 90 (Δ) | Day 180 (Δ) | Cash day 180 (Δ) |
|---|---|---|---|---|---|---|---|
| **Client lists** *(sizes are placeholders; plug in real counts)* | Unignorable 0 | $4.8K | $18.5K | $40.2K (−1.4) | $70.9K (−0.7) | $117.0K | −$758K (−5) |
| | Unignorable 50K | $6.4K | $21.4K | $43.8K (+2.2) | $72.7K (+1.1) | $118.4K | −$745K (+8) |
| | Unignorable 100K | $7.9K | $24.3K | $47.4K (+5.8) | $74.5K (+2.8) | $119.8K | −$731K (+22) |
| | Unignorable 250K | **$12.4K** | $32.9K | $58.1K (+16.4) | $79.7K (+8.1) | $124.0K | −$691K (+62) |
| | K9SUPPS 50K | $5.9K | $20.5K | $42.6K (+1.0) | $72.1K (+0.5) | $117.9K | −$749K (+4) |
| | Unignorable 100K + K9 50K + consented SMS | **$10.3K** | $29.7K | $52.6K (+11.0) | $77.1K (+5.4) | $121.9K | −$711K (+42) |
| **Shoutout supply** | 0/day | $5.0K | $12.2K | $23.6K (−18.1) | $34.8K (−36.8) | $58.4K | −$397K (+356) |
| | 6/day | $5.4K | $21.6K | $47.2K (+5.5) | $85.4K (+13.7) | $140.2K | −$869K (−116) |
| | 8/day | $5.4K | $23.0K | $52.2K (+10.6) | $98.9K (+27.3) | $162.7K | −$984K (−231) |
| | 8/day at a 0.6% link rate | $5.6K | $27.3K | **$63.8K (+22.1)** | $134.3K (+62.7) | $222.8K | −$934K (−182) |
| **Charge-today factor** | 0.35 | $4.8K | $13.9K | $27.9K (−13.7) | $49.2K (−22.4) | $82.2K | −$600K (+153) |
| | 0.45 | $6.4K | $25.8K | $55.5K (+13.9) | $93.7K (+22.1) | $152.2K | −$863K (−110) |
| | 0.50 | $7.1K | $28.6K | **$61.7K (+20.1)** | $104.1K (+32.5) | $169.1K | −$792K (−39) |
| **CPM** | Flat (no Q4 uplift) | $5.9K | $20.9K | $44.3K (+2.6) | $75.3K (+3.7) | $123.0K | −$728K (+25) |
| | −15% vs central | $6.5K | $25.7K | $55.4K (+13.8) | $91.8K (+20.2) | $148.0K | −$876K (−123) |
| | +20% vs central | $4.7K | $14.9K | $29.6K (−12.0) | $53.0K (−18.7) | $89.0K | −$579K (+174) |
| **Organic** | 7 pages live (100%) | $5.7K | $20.5K | $43.3K (+1.7) | $78.3K (+6.7) | $142.2K | −$683K (+70) |
| | **Breakout: 3× base organic** | $6.4K | $22.8K | $48.1K (+6.5) | **$97.4K (+25.8)** | **$212.7K (+95.1)** | **−$483K (+270)** |
| **Price** *(the rule's lines move with price)* | $20 | $4.6K | $13.0K | $25.0K (−16.6) | $44.2K (−27.5) | $74.6K | −$537K (+216) |
| | $25 (base) | $5.4K | $19.7K | $41.6K | $71.6K | $117.5K | −$753K |
| | $30 | $6.5K | $26.0K | **$56.1K (+14.5)** | $93.8K (+22.2) | $151.7K | −$881K (−128) |
| **Spanish launch** *(assumption: US Spanish-language clone from day 31; modelled at $20, the post-blitz localized baseline. Canon now requires one US price across languages (AUDIT F34), so the live price is the US price ($25, then $35); this row understates revenue per member until re-run; $3K/day Meta at 0.9× central CPM; 2 shoutouts/day; 30% organic; +$8K/mo fixed; no lists)* | added to R5 | — | — | $41.6K (0) | **$101.4K (+29.8)** | **$173.4K (+55.9)** | −$1,049K (−296) |

**Stacks** (combinations; day 4 / 14 / 30 / 90 MRR; cash day 30 → day 180):

| Stack | Day 4 | Day 14 | Day 30 | Day 90 | Cash d30 | Cash d180 |
|---|---|---|---|---|---|---|
| A: $30 + lists 100K/50K + 6 shoutouts/day + 7 pages live | $10.1K | $35.3K | $72.0K | $120.6K | −$307K | −$884K |
| B: A + charge-today 0.45 + shoutout link rate 0.5% | **$11.4K** | $42.0K | $86.7K | $149.0K | −$292K | **−$695K** |
| C: B + Meta $12K/day | **$13.6K** | **$49.8K** | **$103.4K** | $172.5K | −$404K | −$986K |

**How to read this:**
- **The gap to $10K on day 4 closes with lists alone** (≥ 100K Unignorable contacts + a K9 list with consented SMS), or with stack A. This is the most controllable milestone.
- **$50K on day 14 and $100K on day 30 need stack C.** That means five things going right at once: price $30, real lists ≥ 100K/50K, 6+ bookable shoutouts a day at a ≥ 0.5% link rate, a charge-today factor ≥ 0.45 and Meta at $12K/day. The day-30 cash is about −$0.4M and the day-180 line is about −$1.0M.
- **Two levers are measurable in the first 72 hours:** the charge-today factor and the shoutout link rate. Put the budget decision after that read, not before.
- **Only two levers improve both speed and cash:**
  - An **organic breakout** (+$95K MRR and +$270K cash by day 180).
  - **Lists** (free, front-loaded).
  - Every paid lever trades cash for speed.
- **The Spanish launch is a day-90+ lever,** not a day-30 lever. It adds about +$30K MRR by day 90 and +$56K by day 180, at about $300K more cash. Its CPM is an unbenchmarked assumption.
- **Lowering the price to $20 is the most damaging single move.** It cuts conversion value and pulls the rule's CUT line down to $124.

## 9. Rules (live in Blitz_Plan; the lines update with price)

| Window | Metric | Scale | Hold | Cut |
|---|---|---|---|---|
| Days 1–7 | Paid media ÷ paid net new members | ≤ $128 at $25 | up to $178 | > $178 two days running → Meta −30% |
| Day 8+ | Same | ≤ $111 at $25 / $132 at $30 | $111–155 | > $155 at $25 / $185 at $30 → −30% |
| Days 1–3 | Arm-B purchase ÷ opt-in | ≥ 5.2% (factor ≥ 0.45 → upside plan) | 4.2–5.2% | < 4.2% → 50% of traffic to arm A |
| Days 1–5 | $25 vs $30: MRR added per $ | winner by ≥ 15% on ≥ 300 purchases → 100% | — | — |
| Days 7–14 | 14-day refunds | ≤ 8% | 8–12% | > 12% → stop scaling |
| Daily | 30-day chargebacks | < 0.35% and < 50 | 0.35–0.5% or 50–75 | ≥ 0.5% or ≥ 75 → stop |
| Day 35+ | $249 annual take among renewed members | ≥ 5% | 2–5% | < 2% → test $199 |
| Days 25–35 | Renewal 1 of first cohorts | ≥ 58% | 50–58% | < 50% → hold spend |
| Always | Cash headroom, to the 180-day line | > 30% | 10–30% | < 10% → cut to the CUT-line equilibrium |

## 10. Bottom line

**Central plan:**

| | Day 4 | Day 14 | Day 30 | Day 90 |
|---|---|---|---|---|
| MRR | **$5.4K** | **$19.7K** | **$41.6K** ($23.4K retained) | **$71.6K** |
| Cash | −$38K | −$115K | −$238K | −$488K |

Cash is still falling at −$753K on day 180, with $40K of reserve held on top.

**Upside:**

| | Day 4 | Day 14 | Day 30 | Day 90 |
|---|---|---|---|---|
| MRR | $10.2K | $42.9K | $92.8K | $159.5K |
| Cash | −$40K | −$127K | −$260K | −$426K |

Upside cash bottoms at −$460K on day 125.

- **$10K by day 4** is reachable with real lists of ≥ 100K contacts.
- **$50K by day 14 and $100K by day 30** need stack C and about $1M of cash tolerance.

## 10. R6: central, profitable (Payback sheet → runs R6 and R17)

**Rule.** Fund a channel only while its **marginal cost per net paying member ≤ the contribution it earns within the payback target**:
- The target is **6 months** (the client brief) for R6 and **12 months** for R17.
- Meta is capped where marginal cost (average ÷ (1 − 0.2) above the $1.5K/day reference) still pays back.
- The 12-month contribution per member at $25 is **$105** for the $1 trial arm and **$111** for charge-today. The 6-month figures are $68 and $77.

| Channel (central inputs, $25) | Cost per net paying member | Payback | ≤ 6 mo? | ≤ 12 mo? |
|---|---|---|---|---|
| Warm lists (Unignorable, K9SUPPS) | ~$0 (list ops) | immediate | yes | yes |
| Organic (keyword DMs) | ~$0 | immediate | yes | yes |
| PT/coach affiliates (30% recurring) | no upfront cost | immediate | yes | yes |
| Shoutouts, $1 trial arm | $78 (net of front-end) | **8 months** | no | yes |
| Shoutouts, charge-today arm | $126 | 16 months | no | no |
| Meta ≤ $1.5K/day, $1 trial arm | $79 | **8 months** | no | yes (up to **$1.5K/day**) |
| Meta ≤ $1.5K/day, charge-today arm | $127 | 16 months | no | no |

**Findings:**
1. **On central inputs, charge-today never pays back within 12 months on any paid channel.** The 12% refunds, the 0.40 factor and the 15% click loss make its cost per member ~$127 against $111 of 12-month contribution. **The $1 trial pays back about twice as fast**, because its front end covers ~$28 of each member's acquisition cost and it filters out would-be refunders. For payback, the paid offer is **the $1 trial**. Charge-today stays for MRR speed only after graduation.
2. **At a strict ≤ 6-month target, no paid channel qualifies.** R6 is warm + organic + affiliates. It is contribution-positive per channel, but the $30.5K/month fixed opex keeps company cash negative (−$118K low). It adds only $2.6K MRR by day 30 and $19.6K by day 180. **Bigger real lists are the only way to grow R6 quickly:** each extra 100K Unignorable contacts adds about $7.6K of day-30 MRR at zero media ($2.6K → $10.2K). It's front-loaded: +$4.6K by day 90 and +$3.6K by day 180.
3. **At ≤ 12 months (R17), Meta runs $1.5K/day and shoutouts 4/day on the $1 trial.** That gives $21.0K on day 30, **$61.2K on day 90 and $110.9K on day 180**. It's cash-flow positive from day 223, with a −$369K low.
4. **Levers that would let paid channels pass a 6-month payback:**
   - price $30 (Meta trial-arm payback falls to about 7 months);
   - CPM without the Q4 uplift;
   - no click loss;
   - a trial→paid rate of ≥ 0.46.

   Measure these live; they are the graduation inputs.

## 11. Graduation rule: from R6/R17 to R4-level spend (plugs into the BLITZ_OPS day-10 and day-40 gates; live in the Payback sheet)

| # | Live threshold | At $25 | At $30 | Why |
|---|---|---|---|---|
| 1 | Blended paid media per net paying member at ≥ $4K/day, 5 days running | **≤ $111** | **≤ $132** | 12-month contribution (SCALE line): average payback ≤ 12 months at scale |
| 2 | Charge-today factor (arm-B purchase rate ÷ trial-start rate), **at central media costs** | **≥ 0.64** | **≥ 0.57** | Factor at which Meta at $8K/day averages the SCALE line |
| 2b | …**if live media costs match the upside** (no Q4 uplift, no click loss) | ≥ 0.48 | **≥ 0.43** | The threshold scales with measured cost per opt-in; R4 assumes 0.45 at $30 |
| 3 | Renewal-1 survival of charge-today cohorts (the day 1–10 cohorts, read on days 31–40) | **≥ 58%** (hold below 50%) | ≥ 58% | The survival the contribution lines assume |
| 4 | 14-day refunds / 30-day chargebacks | ≤ 12% / < 0.35% | same | Rule table |

**Gates:**
- **Day-10 gate** (as run in R7). If 1 and 2 (or 2b) pass on ≥ 300 charge-today purchases, switch to R4 settings from day 11: 100% charge-today at the winning price, Meta $8K/day, 4 shoutouts/day. Otherwise switch to R17 settings: the $1 trial, Meta $1.5K/day.
- **Day-40 gate.** Renewal 1 on the day 1–10 cohorts must be ≥ 58% to stay on R4 settings. If it's below 50%, drop to R17 whatever 1–2 showed. The model uses the assumed renewal curve, so it doesn't trip.

**Why graduation needs both lines.** Threshold 1 is the direct measurement. Thresholds 2/2b say *why* it passes or fails, so the fix is obvious: price, factor or media cost. Threshold 3 is the only one that can't be known before day 31. That's why full R4 spend is a day-40 decision, not a day-4 one.

## 12. R7: the launch plan (runs R7 = central inputs, R19 = upside inputs)

**Days 1–10.** Meta runs at $3K/day flat, plus shoutouts from day 3 (up to 4/day), warm cross-promo and affiliates from day 10. The three cells are sticky per visitor:

| Cell | Offer | Share of traffic |
|---|---|---|
| Trial | $1 for 7 days, then $25 | 50% |
| Founding A | Founding charge-today at $25 | 25% |
| Founding B | Founding charge-today at $30 | 25% |

The blended arm-B list price is $27.43 per purchase, weighted by each cell's conversion.

**Day-10 gate** (Payback sheet, formula-driven). The run graduates if the measured charge-today factor is at least the factor at which Meta at $8K/day averages the 12-month contribution at $30, given the run's own media cost:
- **Central:** factor 0.40 vs a required 0.57 → **fails** → R17 settings from day 11: 100% $1 trial at $25, Meta $1.5K/day, 4 shoutouts/day, $249 annual, save offers.
- **Upside:** factor 0.45 vs a required 0.43 → **passes** → R4 settings from day 11: 100% founding charge-today at $30, Meta $8K/day to day 30 then $4K/day, 4 shoutouts/day.

| | Day 4 | Day 14 | Day 30 | Day 90 | Day 180 | Retained d30 | Peak cash | Cash-flow + / breakeven |
|---|---|---|---|---|---|---|---|---|
| **R7 central** | $1.7K | $8.5K | $22.8K | $62.0K | $111.5K | $14.0K | −$380K (d215) | d216 / after d360 |
| **R7 upside** | $2.9K | $28.3K | $82.0K | $154.8K | $258.7K | $46.5K | −$431K (d135) | d136 / **d303** |

**Milestones under R7:**

| | $10K | $50K | $100K |
|---|---|---|---|
| Central | day 17 | day 70 | day 158 |
| Upside | day 10 | day 20 | day 40 |

**Why this is the right plan:**
- The first 10 days cost about $30K of Meta plus shoutouts. That buys the only three numbers that decide everything: the charge-today factor, the price winner, and cost per member.
- **If the upside is real, R7 reaches each milestone only 3–6 days after R4** ($10K: day 10 vs 4; $50K: day 20 vs 17; $100K: day 40 vs 36). If it isn't, R7 avoids R5's −$1M hole and lands on the track that turns cash-flow positive.

**Trade-off to accept.** The day-4 MRR is small in both cases ($1.7–2.9K). Half the traffic is on the trial, which books nothing until day 8, and Meta runs at only $3K/day. **The "$10K MRR in 3–5 days" milestone is deliberately traded for information.** If the client insists on it, the lever is warm lists (§8, §10: large real lists add several $K of early MRR at zero media), not Meta.

## 13. Organic-first plan (Shopify ladder) — runs R20–R26 (sheet `Organic_First`; engine `tools/organic_engine.py`; refresh `tools/organic_sheet_refresh.py`; chart columns `r20…r26` in `mrr_blitz_daily.csv`)

**What changed (BRIEF.md CANON UPDATE 2 + CANON UPDATE 3, Oct 1 2026).** No $1 trial, no charge-today-vs-trial cells. **The launch default is cell B:** traffic → sales page → **"$12 today = books + first month, then $25/mo" as ONE subscription purchase** (the founding variant on the free Shopify Subscriptions app's monthly plan plus the STARTER12 first-payment-only discount code; no second card entry, no post-purchase page needed). **Cell A is the test cell:** ebook order ($7 / $12 / $15 one-time; default $12) → founding offer on the thank-you page and in 3 onboarding emails (later catches). The one-click post-purchase app stays scaffolded but **off** at launch: it is beta (a live store needs Shopify's access approval), it never shows for Apple Pay / Google Pay / PayPal / installments, and a subscription cannot be added post-purchase to an order without a shipping address, which every digital-only books order is. Downstream is unchanged: $249 annual after renewal 1 (5%), Essentials $12 save offer, gifts, $9 / $29 bumps, $35 standard after the 5,000 founding cap. Fees are Shopify Payments on Basic (2.9% + 30¢ online card rate, shopify.com/pricing; Shopify Subscriptions app free), a $15 chargeback fee, a 5-day payout lag (Shopify: 3 business days, up to 5 for new merchants) and a 10% / 90-day reserve kept as a conservative assumption. Traffic is organic-first: pages post for a runway of R days with a free waitlist CTA; checkout opens to the waitlist + Unignorable / K9SUPPS lists + organic; paid only boosts proven posts and retargets under a daily cap; cold Meta only after the §11 gate. R7/R17/R4 above keep the superseded structure and are retained as history.

**Definitions kept from §0**, with one addition: cell-B members count in MRR at their contracted $25 renewal price from day 1 (they are active auto-renewing subscriptions), although their first-cycle cash is $12. For cell B, **retained MRR** (× the 50% first-renewal survival) is the honest number. Front-end (ebook + bump) cash is reported separately: it is real money, not MRR.

### 13.1 The ladder's unit economics (why cell A is the test cell, not the default)

| Step | Central | Range (sources in the sheet) |
|---|---|---|
| Landing visitor → $12 ebook buyer (cell A) | organic DM 5% · warm lists 8% · cold/shoutout 3% | tripwire pages 1.5–5% cold, 8–15% warm (CartFlows 2026); 5–15% of subscribers (Zanfia 2026). $7 cell ×1.31, $15 cell ×0.89 (elasticity 0.5, assumption) |
| Cell B: subscription-inclusive $12 purchase rate ÷ one-time ebook rate | **0.70** | assumption 0.55–0.85 (the arm-B factor for $25 charge-today vs a $1 trial was 0.40; this is a far smaller ask) |
| Cell B: survival of the first $25 renewal on day 30 | **50%** | assumption between trial→paid 42% and charge-today month-1 renewal 58% |
| Cell A: later catches (thank-you page + 3 emails, days 1–7, a new checkout) | **4%** of ebook orders | assumption; 2% / 7% |
| Cell A, only if the post-purchase page is switched on and approved: eligible orders × one-click accept | 70% (card + Shop Pay) × 100% (address collected) × **12%** | Shopify dev docs: no post-purchase page for wallets / installments / PayPal; "if the order has no shipping address… you can't add a subscription post-purchase"; one-click accept 5–16% (EasyApps, Zipify, CartFlows). Modelled as 0 at launch (R22), 12% in the sensitivity rows |
| **Paying members per ebook order, cell A (launch, post-purchase off), net of 12% refunds** | **0.035** | 0.11 with the post-purchase page on; 0.05–0.19 across the ranges |
| Front-end gross profit per order ($12 + $4.44 bumps, net of refunds, fees, kit COGS) | **$13.99** | $9.26 at $7, $16.65 at $15 |
| 12-month contribution per member | $101 (charge-today stream) · $68 (cell B) | the §11 SCALE lines on this ladder |

The arithmetic that decides everything: **cell B turns a landing visitor into 0.035 subscribers at $25 (0.0175 after renewal 1) and $0.58 of cash; cell A (post-purchase off) turns the same visitor into 0.0018 members and $0.82 of ebook cash.** Cell B books ~20× the MRR per visitor at launch, and still ~6× if the post-purchase page is later switched on.

### 13.2 Organic calibration (the only free traffic)

Pages ramp 3 → 7 over the first 14 runway days; each page ramps 3 → 6 posts/day (9 upside); views per post start at 6,000 at page age 15 days and grow ×1.6 per 30 days to a 40,000 cap (central), with platform multipliers IG 1.3 / FB 1.0 / TikTok 0.7 / YouTube 0.5 and a scenario multiplier (conservative 0.35 / central 1 / upside 1.75 / breakout 3). Evidence (data/posts.csv): Yang Mun's TikTok did a median 76.8K views/post in its first 15 days (n=15; mean 953K, top post 56% of all views) and 47.3K in days 16–30, then a median 1.9K/post once the account was penalised (days 270–400, n=45); YouTube shorts now 646 median. Industry medians for new accounts are 344 views/reel (highviz 2026) and ~350/post at 1–5K TikTok followers (Socialinsider 2025). Central = 1/13 of YM's launch-era median because we post 6/day/page under the 2026 AI-label regime. Views → landing visitors: 0.0956% on IG/FB (0.3% keyword comments × 85% DM open × 30% DM click × 1.25 bio uplift) and 0.03% on TikTok/YouTube (bio link only), × 70% page-load. Yang Mun's own realised yield was ~1.75 ebook buyers per 100K views; central R20 runs ~2 subscription-inclusive buyers per 100K from organic alone at steady state, so the visitor chain is already generous.

Resulting daily landing visitors (central, 14-day runway): 125 on day 1, 220 on day 30, 560 on day 90, ~1,000 from day 150 (views 211K/day → 1.7M/day at the cap). Conservative ×0.35, upside ×1.75, breakout ×3.

### 13.3 Runway and waitlist

| Case | Runway | Waitlist collected organically by day 1 | Runway opex | MRR d4 / d14 / d30 | Day-1 waitlist needed for $10K d4 · $50K d14 · $100K d30 | Unignorable contacts needed instead |
|---|---|---|---|---|---|---|
| **R20 central, cell B (default)** | 7 | 134 | $7.2K | $1.4K / $3.6K / $7.8K | **4.9K · 21.9K · 48.3K** | 240K · 621K · 971K |
| | 14 | 433 | $14.4K | $2.1K / $4.6K / $9.0K | **4.7K · 22.2K · 49.5K** | 223K · 609K · 959K |
| | 21 | 865 | $21.7K | $2.9K / $5.8K / $10.5K | **4.4K · 22.5K · 50.7K** | 203K · 595K · 947K |
| R21 upside, cell B | 7 / 14 / 21 | 376 / 1,290 / 2,623 | $7.2K / $14.5K / $21.9K | $4.1K / $11.0K / $24.5K → $12.0K / $22.5K / $38.4K | 1.8K · 10.3K · 22.0K → 0 · 7.9K · 19.6K | 105K · 301K · 453K → 0 · 223K · 384K |
| R22 central, cell A (test) | 7 | 134 | $7.2K | $0.05K / $0.2K / $0.4K | 225K · 826K · 1.9M | 7.1M · 13.0M · 19.9M |
| | 14 | 433 | $14.4K | $0.07K / $0.2K / $0.5K | 233K · 857K · 2.0M | 7.1M · 12.9M · 19.9M |
| | 21 | 865 | $21.7K | $0.1K / $0.3K / $0.5K | 242K · 890K · not reachable | 7.1M · 12.9M · 19.9M |

Waitlist → buyer: 10% in the first 72 h (consumer waitlist → customer 10–15%, getwaitlist.com) and 5% more over days 4–14, decaying 1%/day of list age (floor 0.7); landing visitor → waitlist opt-in 45% (DM-originated email capture ~80%, cold waitlist pages 11%). **The runway itself is nearly irrelevant to the milestones:** fresh pages collect hundreds, not tens of thousands, of names, and a week of runway costs ~$7K of opex. The waitlist that reaches the dates must be seeded from an audience that already exists.

### 13.4 Amplification only (cap tiers) and the closest-at-least-cash configurations

Central inputs, runway 14, no seeded waitlist (full ladder in the sheet, §6):

| Cell | Cap $/day | Shoutouts/day | MRR d4 / d14 / d30 | Retained d30 | $10K / $50K / $100K day | Peak cash | Paid media d30 | Ebook cash d30 |
|---|---|---|---|---|---|---|---|---|
| **B** | 0 | 0 | $2.1K / $4.6K / $9.0K | $4.6K | 37 / 129 / 202 | −$84K | $0 | $7K |
| **B** | 1,500 | 0 | $5.9K / $20.8K / $46.0K | $23.6K | 8 / 35 / 77 | −$116K | $45K | $33K |
| **B** | 1,500 | 2 | $6.7K / $26.3K / $58.9K | $30.1K | 6 / 26 / 59 | −$185K | $78K | $43K |
| B | 3,000 | 0 | $7.5K / $32.0K / $73.4K | $37.6K | 6 / 22 / 46 | −$173K | $87K | $53K |
| **B** | 3,000 | 4 | $8.2K / $42.1K / $98.1K | $50.3K | **5 / 17 / 31** | −$302K | $150K | $71K |
| A (test) | 0 | 0 | $0.1K / $0.2K / $0.5K | $0.3K | — / — / — | −$90K | $0 | $9K |
| A (test) | 1,500 | 0 | $0.2K / $1.0K / $2.3K | $1.3K | 156 / — / — | −$183K | $45K | $48K |
| A (test) | 3,000 | 4 | $0.2K / $1.9K / $4.9K | $2.8K | 70 / — / — | −$919K | $150K | $102K |

Boosted winners cost ~$1.00 per visitor (0.65 × cold) and convert at the organic rate; retargeting ~$0.78 (0.50 × cold). On cell B that is well inside the $68 contribution line, so **boosts, retargeting and shoutouts (~$44 per net member) all pay back on cell B**; on cell A with the post-purchase page off nothing paid pays back (≈ $600+ per net member), which is why cell A is a test cell and never the amplified one. Cold Meta ($1.55 per visitor before learning and scale penalties) fails the gate on every central input set (§13.6).

**Seeded waitlist needed per milestone (central, runway 14), with the peak cash of that configuration:**

| Cell | Cap / shoutouts | $10K by day 4 | $50K by day 14 | $100K by day 30 |
|---|---|---|---|---|
| **B** | $0 / 0 | **4.7K names (−$65K)** | **22K (−$24K)** | **49K (−$22K)** |
| B | $500 / 2 | 3.4K (−$155K) | 16K (−$113K) | 34K (−$62K) |
| B | $1,500 / 2 | 1.9K (−$178K) | 10.7K (−$147K) | 20K (−$118K) |
| B | $3,000 / 4 | 1.0K (−$298K) | 3.5K (−$289K) | 0.8K (−$298K) |
| A (test) | $0 / 0 | 233K (−$32K) | 857K (−$56K) | 1.98M (−$95K) |
| A (test) | $1,500 / 2 | 232K (−$71K) | 852K (−$67K) | 1.94M (−$105K) |

Note the pattern: a big seeded list makes the plan cheaper, not dearer, because every name that buys pays $12 up front. The day-30 retained MRR behind each cell-B "$100K" entry is ~$50K (the first renewal).

### 13.5 Sensitivity (R20 and R23; rows that swing day-30 MRR by > $5K are flagged in the sheet)

Flagged on R20 (base $9.0K): **cell A instead of B (−$8.6K with the post-purchase page off; −$7.6K with it on at 12%; −$6.6K at 20% of 85% eligible)**, organic breakout ×3 (+$10.2K), organic at Yang Mun launch-era reach ×12.8 (+$60.3K), Unignorable 100K / 250K (+$7.8K / +$22.5K), seeded waitlist 10K / 25K / 50K / 100K (+$21.8K / +$49.9K / +$91.8K / +$196K), cap $500 / $1,500 / $3,000 (+$12.4K / +$37.0K / +$64.4K), shoutouts 2 / 4 per day (+$12.8K / +$24.7K), gate-on cell B upside (+$95.0K). Below the flag line: subB 0.55 / 0.85 (−$1.9K / +$1.9K); the first-renewal survival (42% vs 58%) moves day-30 MRR by $0 (it moves retained MRR and everything after day 30).

Flagged on R23 (base $58.9K): cell A instead of B (−$55.9K off; −$49.4K with the post-purchase page on; −$42.8K at 20% of 85%), ebook conversion 3% / 8% (−$16.5K / +$24.7K), subB 0.55 / 0.85 (−$12.6K / +$12.6K), $7 / $15 ebook (+$17.9K / −$6.1K), founding $30 (+$11.8K), organic breakout / YM-era reach (+$10.5K / +$62.2K), seeded waitlist 10K / 25K / 50K / 100K (+$22.0K / +$49.4K / +$104K / +$213K), cap $500 / $3,000 (−$24.6K / +$27.4K), boost efficiency 0.80 (−$8.6K: the cap buys fewer, dearer visitors), shoutouts 4/day (+$11.9K), gate-on cell B upside (+$123K), gate-on cell A upside (−$31.6K: cold Meta on the test cell fails). The reserve, the annual take and the waitlist rates move day-30 MRR by < $0.3K (the reserve moves cash by ~$39K on R23).

### 13.6 Graduation to cold Meta (R24)

The §11 gate on this ladder: cold Meta at $8K/day must deliver a net paying member for no more than the 12-month contribution, net of the ebook profit each cold order carries. Central cell B: ~$102 per member vs $68 → **fails**, R24 = R23. Central cell A (post-purchase on): ~$591 vs $101 → fails; upside cell A: $148 vs $101 → fails. **Upside cell B (subB 0.85, first renewal 58%, cold ebook conversion 4%): $41 vs $79 → passes.** With the gate open from day 11 (Meta $8K/day to day 30, $4K after, 4 shoutouts/day) on R23 settings, that run reaches $10K on day 4, $50K on day 13 and $100K on day 21 ($182K MRR / $107K retained on day 30) at a −$361K cash low. That is the only configuration in this model that meets the client's dates, and it requires upside inputs on three unmeasured rates at once. Measure them in the first 10 days and let the gate decide.

### 13.7 What this means

1. **Cell B is the launch default (CANON UPDATE 3), cell A the test cell.** On every input set, "$12 = books + first month, then $25/mo" books ~20× the MRR per visitor of books-only-plus-emails at the same cash, and it is the only cell on which paid amplification pays back or graduates. Cell A stays live as the test cell because it earns more ebook cash per visitor and tells us the one-time purchase rate the subB factor is measured against.
2. **Cell A is operable without the post-purchase app.** Its membership comes from the thank-you page and the 3 onboarding emails (a new Shopify checkout with the consent box). The post-purchase app stays scaffolded and off: it would need Shopify's beta access approval, card-only payments and a shipping address on a digital order to fire at all; even switched on it lifts cell A to ~$1.4K on day 30 (R20 settings), not to cell B.
3. **The dates are reachable only with a seeded audience or cold Meta on upside inputs.** On central inputs with no seeded list, the closest honest configuration is cell B + $1,500/day boosts/retargeting + 2 shoutouts/day: $10K on day 6, $50K on day 26, $100K on day 59, peak cash −$185K, $30K retained on day 30. Adding a 20K-name seeded waitlist pulls $100K to day 30 at −$118K. With no seeded list and no media, cell B reaches $10K on day 37 and $100K on day 202 at −$84K.
4. **The $12 is real cash.** R20 earns $6.6K of front-end revenue by day 30 and $96K by day 180 with zero media; R23 earns $43K by day 30 against $78K of media, which is what makes boosts self-liquidating.
5. **Organic alone cannot carry the dates** under any evidence-based reach assumption: even at Yang Mun's launch-era per-post reach (×12.8), cell B with no media reaches $10K on day 2 but $100K only on day 48, at a cash low that needs the same seeded list or paid tiers.

## 14. Scale plan to $250K — runs R30–R36 (engine `tools/organic_engine.py` `sc_run`, `--scale`; sheet `Organic_Max`; chart columns `r30…r36_{booked_MRR,retained_MRR,cash_scale,views_scale,posts_scale}` in `mrr_blitz_daily.csv`)

**What it is.** A port of the client-approved projection `data/projection_aggressive_central.csv` (sheet `Projection_Aggressive`, kept). Run **R30A** reproduces that file cell-for-cell to its display rounding (180 days × 37 columns, every cell within ±0.5; `tools/test_scale_engine.py`). The canonical runs R30–R36 change ONE rule, per CANON UPDATE 5: the scale-ladder milestones, the $30K paid-media gate and the 25% all-in cap are read on **trailing-7-day RETAINED MRR** (exactly what `workers/growth/governor.py` gates on). The approved file steps them on the previous day's BOOKED MRR (ladder day 4 / day 9, paid from day 9 while retained MRR was $17K), which the canon does not allow; that is the only difference between R30 and R30A.

**Definitions.** booked MRR = 0.95 × ($25 × active members + $147 × coached members). **Retained MRR = 0.95 × $25 × (50% of first-cycle members + every renewed member): plan on this one** (coached revenue is never in it). cash = −$15K + $12 per buyer + $25 per renewal + coached $147/30 per day − 3% fees − daily cost (generation $1.28/master + $0.225/Trial Reel, $16 tools, review 20 s/post at $20/h, paid media); no team opex in this family. contracted_30d = renewals due in the next 30 days from survivors = retained MRR (monthly billing). margin = 1 − 30 × cost/day ÷ booked MRR. Every input (views/post $6K at age 15 growing ×1.6/30 days, learning +3%/week linear, platform lanes IG 1.0 / FB 0.8 / TT 0.7 / YT 0.5 / Threads+X 0.3, Trial Reels 10/page/day in week 1 then 20 at 0.35 reach + 0.1695 graduation bonus, 600K views/page/day ceiling, 0.4% clicks × 70% loads × 5% buy, lists 1.5% over 14 days, waitlist 10% over 3 days, $85 paid CPA, first renewal 50% then 7%/month, coached 5% from member day 10) is labelled ASSUMPTION with range and source in `SC_INPUTS` and in sheet `Organic_Max` §1.

**Ladder (config `governor.scale_rules` = engine `SC_LADDER`; never steps down).** $0: 4 pages × 6 masters × 20 Trial Reels · $10K: 5 × 8 × 20 · $30K: 7 × 9 × 20 + paid gate · $50K: 7 × 9 × 20 (second character show, second coach: not volume-modelled) · $100K: 7 × 9 × 20, tier `pro` (PT/DE clones and the Pro-tier cost are NOT in the approved projection; flagged).

### 14.1 Run table (days 1–180)

| Run | Definition | Booked $10K / 30K / 50K / 100K / 250K (day) | Retained $10K / 30K / 50K / 100K / 250K (day) | Booked d30 / d60 / d90 / d180 | **Retained d30 / d60 / d90 / d180** | Cash low (day) | Breakeven day | Margin d30 / d60 | Gate open | Ladder $10K / 30K / 50K / 100K (day) |
|---|---|---|---|---|---|---|---|---|---|---|
| **R30** | central: lists 30K, waitlist 1.5K | 3 / 9 / 12 / 20 / 35 | 6 / 15 / 21 / **33 / 58** | $207K / $542K / $859K / $1.64M | **$89K / $268K / $477K / $1.06M** | −$13.1K (1) | 9 | 90.5% / 88.6% | 19 | 10 / 19 / 25 / 37 |
| R31 | lists 150K, waitlist 5K | 2 / 4 / 7 / 12 / 26 | 3 / 8 / 13 / 25 / 52 | $302K / $605K / $915K / $1.69M | $127K / $311K / $519K / $1.10M | −$10.2K (1) | 4 | 90.5% / 88.0% | 12 | 7 / 12 / 17 / 29 |
| R32 | upside: clicks 0.5%, buy 6.5%, renewal-1 58%, churn 5%/mo, trial reach 50% | 2 / 6 / 9 / 14 / 23 | 4 / 9 / 13 / 20 / 36 | $386K / $998K / $1.57M / $3.16M | $193K / $558K / $963K / $2.16M | −$12.3K (1) | 6 | 89.5% / 87.2% | 13 | 8 / 13 / 17 / 24 |
| R33 | conservative: Trial Reel cap 5, reach ×0.6, funnel ×0.5 | 5 / 17 / 29 / 55 / 90 | 12 / 40 / 54 / 78 / 127 | $54K / $119K / $254K / $680K | $22K / $61K / $134K / $426K | −$13.8K (1) | 21 | 94.3% / 87.6% | 43 | 16 / 43 / 58 / 82 |
| R34 | R30, ladder OFF | 3 / 9 / 13 / 24 / 53 | 6 / 17 / 27 / 46 / 85 | $138K / $300K / $491K / $939K | $58K / $153K / $272K / $608K | −$13.1K (1) | 9 | 90.5% / 88.3% | 21 | — |
| R35 | R30, ascension OFF | 3 / 9 / 13 / 21 / 39 | 6 / 15 / 21 / 33 / 58 | $179K / $450K / $697K / $1.31M | $89K / $268K / $477K / $1.06M | −$13.1K (1) | 9 | 89.0% / 86.2% | 19 | 10 / 19 / 25 / 37 |
| R36 | R30, Facebook OFF | 3 / 10 / 14 / 23 / 42 | 7 / 18 / 25 / 39 / 66 | $157K / $432K / $765K / $1.57M | $68K / $213K / $414K / $1.01M | −$13.3K (1) | 11 | 90.5% / 88.7% | 22 | 11 / 22 / 29 / 43 |
| R30A | the approved file (booked-basis ladder/gate/cap) | 3 / 8 / 11 / 16 / 30 | 5 / 12 / 17 / 29 / 53 | $255K / $609K / $941K / $1.80M | $109K / $305K / $527K / $1.17M | −$13.1K (1) | 8 | 75.6% / 75.2% | 9 | 4 / 9 / 12 / 17 |

Read: on central inputs the canon targets hold on RETAINED MRR — $100K on day 33 (target: within 45 days) and $250K on day 58 (target: 60–90). Booked MRR runs 2–3 weeks ahead and is not the planning number. Ascension (R35) changes booked MRR only, never retained. The ladder is worth $456K of day-180 retained MRR (R30 vs R34); Facebook is worth $56K by day 180 but 8 days on the $250K date (R36). Gating on retained instead of booked costs R30 4 days on $100K and 5 on $250K versus the approved file, and keeps margin near 89–90% instead of 75% because the 25% cap sits on a smaller number. On conservative inputs (R33) $250K retained slips to day 127.

### 14.2 Sensitivity (R30, one input at a time)

| Change | Retained d30 / d60 / d90 / d180 | Retained $100K day | Retained $250K day | Gate open | All pages at ceiling |
|---|---|---|---|---|---|
| R30 base | $89K / $268K / $477K / $1.06M | 33 | 58 | 19 | 67 |
| Funnel rates −50% (views → clicks ×0.5) | $42K / $127K / $230K / $524K | 52 | 96 | 28 | 74 |
| Funnel rates +50% | $139K / $412K / $726K / $1.61M | 25 | 44 | 15 | 63 |
| Trial Reel reach 35% → 15% | $80K / $246K / $453K / $1.04M | 35 | 61 | 20 | 73 |
| Trial Reel cap 20 → 5 per page per day | $72K / $224K / $428K / $1.02M | 37 | 65 | 21 | 79 |
| Page ceiling 600K → 300K views/page/day | $80K / $186K / $289K / $577K | 36 | 79 | 19 | 31 |

**Binding constraint: the per-page view ceiling, then the funnel.** The first page hits 600K views/day on day 45 and all 7 by day 67; from then views are flat at 4.2M/day and growth comes only from member compounding. Halving the ceiling cuts day-180 retained MRR 46% and moves $250K from day 58 to day 79; the funnel (views → clicks) moves the $250K date by −14 / +38 days at ±50%. The Trial Reel lane is NOT binding: reach 15% or a 5/day cap costs 2–4% of day-180 retained MRR (3–7 days on $250K). So the next capacity lever after the $30K step is more pages (the $100K PT/DE clones, not modelled) or a better funnel, not more trials.

### 14.3 Three-way comparison

| Measure | ORIGINAL (Yang-Mun style: 1 page, 3/day, $19.99 ebook + Whop $19.99/mo; POSTDB) | CURRENT (R20) | UPDATED (R30) |
|---|---|---|---|
| Posts/day (d30) | 3 | 42 | 511 |
| Views/day d30 / d90 | 28K / 73K | 371K / 950K | 2.74M / 4.20M |
| Retained MRR d30 / d60 / d90 / d180 | $15 / $34 / $61 / $191 | $4.6K / $11.8K / $20.9K / $64.2K | $89K / $268K / $477K / $1.06M |
| Cost/day d30 (model basis) | $19 | $1,085 (incl. $1,018 team opex + plan) · $67 ex-opex | $654 (no team opex) |
| Margin d30 / d90 (1 − 30 × cost ÷ MRR) | negative | −260% / −23% | 90.5% / 86.7% |
| Breakeven day (cumulative cash ≥ 0) | 124 (no opex) | 235 | 9 |
| Features (SYSTEM_RECAP §2 rows) | 8 (observed) | 79 | 81 (+ spend gate / all-in cap, + scale ladder) |

ORIGINAL uses POSTDB's ~1.75 ebook buyers per 100K views, 15% Whop trial starts, 42% trial→paid and our central per-post reach on one page (at Yang Mun's launch-era reach ×12.8 its MRR is ×12.8 too). CURRENT's cost carries the $30.5K/month team opex; UPDATED's projection basis does not, so compare the ex-opex row.

### 14.4 Governor (CANON UPDATE 5, `workers/growth/governor.py` + `config.py`)

- **Spend gate:** no paid media of any kind (boost, retarget, cold) unless trailing-7-day retained MRR ≥ `governor.spend_gate.retained_mrr_usd` ($30K; config refuses anything lower; days not reported count as $0, so a short history keeps the gate shut). Below it the plan is all zeros with the reason.
- **All-in cap:** paid room per day = `all_in_cap.share_of_mrr` (0.25, config 0.20–0.30) × trailing-7-day retained MRR ÷ 30 − fixed − generation − already spent today; unknown costs → no room. It is a further envelope under the existing budget, cash-floor and §9/§11 rules.
- **Scale ladder:** `governor.scale_rules` (retained-MRR threshold → pages_open, masters_per_page, trial_reels_per_page, generation_tier); `governor.scale_plan()` returns the row (also in every decision as `scale`); `cadence` = masters_per_page is the value the allocator's `plan_day(cadence=…)` takes and the plan builder reads pages/trials/tier from the same row (allocator.py and the n8n plan builder are unchanged this round: they consume it through these existing parameters). It only steps up; a reach anomaly pauses it; stepping down is a human edit. Config validation refuses a ladder whose capacity falls as MRR rises.
- **Property tests:** 3,000 random states (cap never exceeded, gate never open below the threshold, ladder never below its input) + 100 random 30-day MRR paths (monotonic), `workers/tests/test_growth_scale_gate.py`; the existing 1,500-state governor property test now also checks the gate and the cap.
