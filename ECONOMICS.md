# ECONOMICS.md — the model, the verdict, the fastest path

Files: `economics.xlsx` (every number is a live formula; inputs are in blue on `Assumptions` with a source for each), `mrr_scenarios.csv` (month × scenario × subscribers × MRR), `OFFER.md` (what is being sold).
This file models the **baseline** offer ($1 trial → $20/mo). The launch runs in **blitz mode** (charge-today founding membership, $25 vs $30, 14-day money-back, cap 5,000; OFFER.md §0.1), which is modelled in BLITZ.md and the Blitz sheets.
All figures are pre-tax, in USD, and come from the workbook as delivered. "Month 2" means day 60.

---

## 1. The verdict

| Question | Answer |
|---|---|
| **$100K MRR in 30–60 days from organic alone?** | **No. Plan for less than a 5% chance.** Holding 5,000 paying members on day 60 needs ~111 new paying members a day from the start. At our calibrated conversion rate (~53 trial starts per 1M views, slightly *below* Yang Mun's implied ~64 buyers per 1M), that is ~4M views a day, ~130M a month, **from month 1**. That is about 3.6× Yang Mun's *average* month (~36M) on brand-new pages. Base-case organic reaches $100K MRR in **month 12**. |
| **$100K MRR by day 60 with paid?** | **Mechanically yes, with ~$650–740K of ad spend in 60 days and ~$390–490K of cash exposure on day 60.** Our view is it's possible but not likely: roughly a 25–35% chance. It depends on creative winning from week 1, cost per trial holding at ≤$45 at $12K+/day, and the payment processor and Meta ad account surviving the growth. |
| **$500K MRR?** | **S3 reaches it in month 9**, after ~$4.9M of cumulative ad spend and a **peak cash hole of ~$1.38M (month 8)**. Cash payback in month 16. **In the downside case it is not reached within 18 months** and the cash hole goes past $3.3M. S2 (disciplined paid) reaches ~$390K MRR by month 18 with a peak cash hole of only ~$114K. |
| **The honest recommendation** | Run **S2 as the plan and S3 as an option you exercise**. Launch on the S3 ramp only after 7–10 days of live data show cost per paid trial ≤ $40, trial→paid ≥ 40% and first-session completion ≥ 70%. If those hold, the day-60 target is within reach. If they don't, you've spent ~$60K to find out, not $700K. |

---

## 2. How the model works (one paragraph per block)

1. **Organic engine** (`S1–S3` rows "1. Organic funnel"; `Pages`). Posts per month = 7 pages × 6 posts a day × 30 = 1,260. Average views per post start at 6,000, grow 1.6× a month and cap at 40,000 (about ⅓ of Yang Mun's mature median, because 42 posts a day compete with each other). From month 12 reach decays 2% a month. That gives ~50M views a month at maturity. Followers = views × 8 per 1,000 (Yang Mun implies ~12.5 per 1,000; discounted for overlap across pages). Base followers: 0.3M at month 3 (**~13% of Yang Mun's 2.4M in 3 months**), 3.6M at month 12, 5.7M at month 18. The `Pages` sheet splits this per page. At month 12 the Chang Yin IG page is at ~45% of Yang Mun's current IG following and Chang Yin FB at ~59% of Yang Mun's FB.
2. **Organic conversion.** Views → keyword comments 0.30% → DM opened 85% → DM click 30% (+25% from bio and FB links) → quiz start 70% → opt-in 42% (Interact benchmark) → trial or front-end purchase 14%, plus 5% of last month's opt-ins through nurture. **Calibration check:** ~53 trial starts per 1M views vs Yang Mun's ~64 ebook buyers per 1M. We are deliberately a little below the only real comparable.
3. **Paid engine.** CPM $18 (Triple Whale H&W median $21.80, all categories $15.06). Link CTR 1.5% → CPC $1.20. Landing page → quiz 65% → opt-in 42% → trial 13%, so **base cost per paid trial start is $33.81** ($24.42 once 30-day nurture of paid opt-ins is included). A scale penalty raises cost per click by (spend ÷ $45K a month)^0.20: at $500K a month, cost per trial is ~1.6× base. The penalty stands in for auction pressure and creative fatigue.
4. **Conversion and cohorts.** Trial→paid is 42% for paid traffic and 48% for organic (Adapty health & fitness 42.2%). 77% of trials convert in the month they started, the rest the next month. 10% of new payers take the annual plan ($119; 30% renew at month 12). Monthly survival: 62% / 50% / 43% / 38.5% / 35% after renewals 1–5 (benchmark 59 / 45 / 37 / 32 / 28%), then 5% churn a month. **An 18×18 cohort waterfall** (section 7 of each scenario sheet) builds active members cell by cell.
5. **Revenue and cost.** Front-end revenue $12.99 per start. Membership at $20 × 0.95 realised. Stripe 2.9% + 30¢ + 0.7% billing. Refunds 6% on the front end and 2.5% on subscriptions. Chargebacks 0.35% plus a $15 fee. Kit cost. **Delivery cost $0.81 per member per month** (AI chat $0.07, voice $0.10, SMS $0.21, video $0.29, email/hosting/tools $0.15). Human coaching and support $0.40 per member. Fixed opex $30.5K a month. Social content $0.60 per post. Media buying and creative 6% of spend. Supplements (month 7+) are a separate contribution line and are **not** counted in MRR.
6. **Sprint60** (daily, days 1–90). A realistic spend ramp ($3K/day on day 1 → $12.5K/day by day 21, then held), a 7-day trial lag, nurture 15 days later, day-30 and day-60 renewals, and daily cash. **This is the sheet that answers the day-60 question.** The monthly sheets are coarser.
7. **Solver** (closed form, no goal-seek). The flat daily inflow of paying members needed to have N alive on day D, given the renewal curve, and the daily spend that inflow requires with the scale penalty solved algebraically.
8. **Sensitivity.** LTV:CAC for price × steady churn × cost per trial ($25 / $35 / $45), plus a price read-out with the break-even cost per trial.

---

## 3. Scenario results (from `Summary`; months are 30-day blocks)

| | S1 Organic only | S2 Organic + moderate paid | S3 Aggressive paid |
|---|---|---|---|
| **Ad spend schedule** | $0 | $25K → $175K/mo by month 7 | $260K, $480K, then $500–650K/mo; $550K from month 9 |
| **Month 2: members / MRR** | 320 / $5.8K | 1,109 / $20.0K | **5,529 / $99.4K** |
| Month 2: cumulative ad spend / cash position | $0 / −$43K | $75K / −$72K | $740K / **−$489K** |
| **Month 6: members / MRR** | 2,657 / $47.1K | 7,189 / **$127.1K** | 20,981 / $369.2K |
| Month 6: cumulative spend / cash position | $0 / +$36K | $525K / −$86K | $3.04M / **−$1.26M** |
| **Month 12: members / MRR** | 6,007 / **$103.7K** | 16,609 / $286.7K | 37,962 / $651.7K |
| Month 12: cumulative spend / cash position | $0 / +$508K | $1.58M / **+$472K** | $6.54M / −$918K |
| **Month 18: members / MRR** | 7,983 / $137.0K | 22,657 / $389.1K | 48,186 / $828.7K |
| Month 18: cumulative cash | +$1.17M | +$1.63M | +$0.64M |
| **Max cash exposure** | **−$51K** (month 3) | **−$114K** (month 4) | **−$1.38M** (month 8) |
| First month MRR ≥ $100K | 12 | 6 | 3 (day 60 ≈ $99K) |
| First month MRR ≥ $500K | not within 18 months | not within 18 months | **9** |
| First month with positive monthly cash flow | 4 | 5 | 9 |
| Cash breakeven (cumulative ≥ 0) | 6 | 8 | 16 |

**Daily view of S3 (`Sprint60`):** day 30: 1,893 members. **Day 60: 5,617 members, $101K MRR.** Day 90: 8,546 members, $152K MRR. Ad spend on days 1–60 is **$650K**. The lowest cumulative cash by day 60 is **−$389K**, and it's −$529K by day 90. Average paid trial starts are **~265 a day** (peak ~335), producing **~118 new paying members a day**.

**Unit economics at scale:** net paid CAC per paying member (after front-end revenue) is **~$52 in S2 and ~$73–93 in S3**, against **~$119 of 24-month contribution per paying member at $20**. That puts **LTV:CAC at ~2.3× for S2 and ~1.3–1.6× for S3**. That is why S3 burns cash for eight months. The front end returns ~25–40% of ad spend (the "self-liquidation ratio" row), so this is **not** a self-liquidating offer. Delivery plus human coaching costs ~7% of MRR, so gross margin is not the constraint. **Cost per paying member is.**

---

## 4. Solver: flat daily requirements (S3 inputs; organic subtracted)

| Target | Total new paying members/day | Paid trial starts/day | Ad spend/day | Ad spend over the window |
|---|---|---|---|---|
| 5,000 members ($100K MRR) by **day 60** | 111 | 250 | **$8.7K** | **$459K** |
| 5,000 by day 90 | 80 | 171 | $5.4K | $446K |
| 25,000 ($500K MRR) by **day 120** | 323 | 740 | $33.7K | $3.81M |
| 25,000 by day 180 | 241 | 524 | $21.9K | $3.79M |
| 25,000 by day 365 | 146 | 269 | $9.5K | $3.40M |

Read-out:
- **A flat rate from day 1 is a lower bound.** Ad accounts ramp, and a ramp needs a higher peak. That's why Sprint60's ramp needs **$650K** where the flat solver needs $459K. **Budget $650–750K in media for the day-60 target.**
- **Day 90 costs about the same money as day 60, with a lower peak and lower risk.** At a lower daily spend the scale penalty is smaller, and renewals start funding acquisition. If the goal is really "$100K MRR as fast as the cash allows", day 75–90 is the efficient answer.
- **$500K MRR costs ~$3.4–3.8M in media whichever deadline you pick.** A later deadline mostly lowers the peak daily spend and the risk of account and processor blowups.

---

## 5. Sensitivity (`Sensitivity` sheet; S2 retention curve)

**LTV:CAC at $20/mo** (24-month contribution ÷ net CAC per paying member):
| Cost per paid trial start | 3% churn | 5% churn | 8% churn |
|---|---|---|---|
| $25 | 3.67 | 3.32 | 2.92 |
| $35 | 2.15 | 1.95 | 1.71 |
| $45 | 1.52 | 1.38 | 1.21 |

**Price read-out** (trial→paid elasticity 0.30, 5% churn):
| Price | Trial→paid | 24-mo contribution per paying member | Break-even cost per trial | Cost per trial for 3.0× |
|---|---|---|---|---|
| $12 | 49% | $67 | $41.68 | $21.12 |
| $15 | 46% | $86 | $48.08 | $23.25 |
| **$20** | **42%** | **$119** | **$57.84** | **$26.51** |
| $25 | 39% | $151 | $66.81 | $29.50 |
| $30 | 37% | $183 | $75.20 | $32.29 |

- **The cost per trial start is the variable that decides the business.** Going from $25 to $45 cuts LTV:CAC by ~60%. Moving steady churn from 5% to 3% improves it by only ~10%.
- **Rule for the media buyer:** scale a creative or audience while its blended cost per trial is ≤ $26 (3× at $20) and hold at ≤ $40. Kill it above $58, which is the $20 break-even.
- Higher prices look better **only if** elasticity is as low as 0.30. The live price test (OFFER §2.4) exists to measure that elasticity. **Don't set the price from this table.**

### Stress cases (whole-model reruns)
| Case | S2 month-12 MRR | S2 max cash hole | S3 month-2 MRR | S3 month-12 MRR | S3 max cash hole |
|---|---|---|---|---|---|
| Base | $287K | −$114K | $99K | $652K | −$1.38M |
| CPM −20% (e.g. $14.40) | $333K | −$71K | $123K | $789K | −$0.78M |
| Trial→paid +8 points | $339K | −$86K | $118K | $773K | −$1.02M |
| Price $25 (*assumes no conversion loss*) | $351K | −$86K | $123K | $796K | −$1.00M |
| Organic 2× (breakout content) | $391K | −$56K | $105K | $755K | −$1.04M |
| Bump 45% + upsell 15% | $287K | −$86K | $99K | $652K | −$1.11M |
| Annual share 25% | $291K | −$65K | $93K | $670K | −$0.91M |
| Retention +5 points on every renewal | $310K | −$111K | $101K | $707K | −$1.28M |
| **Downside** (trial→paid 32%, CPM $22, benchmark retention, 6.5% churn) | $189K | −$255K | **$63K** | $381K | **−$3.35M, not recovered** |
| **Organic 3× ("breakout")** | — | — | S1 hits $100K MRR in month 6 and is cash-positive from month 2 | S3 hits $500K in month 7 | S3 breakeven month 10 |

---

## 6. What must be true for $100K MRR by day 60

1. **The funnel is live by day 5**: quiz → Strength Age result → compliant $1/$7/$17 checkout → members area with the Daily Session, email (SMS once 10DLC / toll-free verification clears, 3–6 weeks) and the 48h pre-billing reminder (by email until SMS is approved). The content engine can come second. Without the funnel, viral views produce nothing.
2. **~265 paid trial starts a day on average for days 1–53** (peak ~335), at a **blended cost per trial ≤ $45** while spending $12.5K+/day. That needs ≥ 20 creative concepts in rotation by day 10 and ~5 new ones every day (the AI pipeline makes this cheap). Hooks use the jacked-elder visual ("I'm 74. Watch me do this."), Sun Yoon's bluntness, and the adult-child gift angle.
3. **Trial → paid ≥ 42%.** That depends on first-session completion ≥ 70% within 24h and the day-5 reminder being framed as progress.
4. **$650–750K of media plus ~$60K of opex** available as cash, with **~$400–500K of exposure on day 60**. On the S3 path exposure keeps growing to ~$1.4M (month 8) before recurring revenue catches up.
5. **Payments infrastructure that holds**: processor underwriting approved for $500K+/month of negative-option volume, a second processor ready, Verifi RDR/Ethoca live, chargebacks < 0.4% **and** below 100 a month on Mastercard.
6. **The Meta account stays a fitness/cooking advertiser** (no condition words in domains, paths, events or ads; OFFER §2.6), so it can keep optimising for purchase and trial events. It is an existing account **only** if it has purchase history and no restricted-health ad history (K9SUPPS is the likeliest); otherwise a fresh Strong Years account. Never a Founder Ascension account.
7. **Organic is a free bonus, not the plan.** In the base case it contributes only ~6 new paying members a day by day 60.

If any of 2–6 fails, the realistic landing is **$100K MRR at day 90–150** (S3 downside ~ month 3–4, S2 month 6).

---

## 7. The fastest *sane* path (recommended operating plan)

**Week 0 (before day 1):** entity and processor applications (two), **A2P 10DLC / toll-free SMS registration (verification takes 3–6 weeks, so it starts at kickoff but is not on the launch critical path: launch runs on email + DM, and the 48h pre-billing reminder goes by email until SMS is approved)**, trademark filing, consent and cancel flows, checkout, quiz, the first 30 Daily Sessions and 4 weeks of Sun Yoon's Kitchen, AI chat with the crisis classifier. Pre-build 40 ad creatives and 150 organic posts. **Timing:** day 1 of the model is the **first paid day**, realistically 2–3 weeks after kickoff (processor underwriting and Meta business verification set the pace; SMS switches on later, when 10DLC clears). **Organic caveat:** the model's organic engine assumes 7 posting accounts from month 1 (7 pages × 6 posts/day), but the rollout (CONTENT_SYSTEM.md §8.1, PIPELINE.md §5.4) starts with 3 pages on a warm-up ramp and reaches 7 pages only around day 30, so early organic numbers in the model are optimistic. The xlsx is unchanged.

**Days 1–10 (test, ~$3–5K a day, ~$40K total):** organic on the 3 day-1 pages following the warm-up ramp (the model assumes 7 pages × 6/day; see the organic caveat above), with a comment keyword → DM → quiz on every post. Paid: 4 angles × 5 hooks × 2 front ends ($1 trial vs $7 Reset). **Decision gate on day 10:** cost per paid trial ≤ $40, trial→paid ≥ 40% (read from the first 3 days of conversions), first-session completion ≥ 70%, chargebacks+refunds < 1%.

**Days 11–60 (if the gate passes, S3 ramp):** step spend up ~20% a day on winners to $12–15K/day by day 21. Add the gift funnel (adult children) and the $27 Starter as a paid-only path to lift front-end revenue per start. Launch the 14-Day Challenge on the 1st of month 2 as an organic spike. Start the annual push at day 21. **If the gate fails, run the S2 schedule** and fix the funnel before scaling.

**Days 61–270 (towards $500K MRR):** keep the blended cost per trial ≤ $40 or cut spend. Ship the native app wrapper (month 3–4) for push notifications. Launch the Spanish archetype clone (*Años Fuertes*, month 4–5). It adds a second organic engine and lower-CPM Spanish-language inventory, which is the cheapest way to reduce the $1.4M cash hole. Launch the Plus tier ($30, human check-ins) in month 4. Supplements come in month 7, inside the membership only.

### Biggest levers, ranked by effect on S3 cash exposure (from §5)
1. **Cost per trial / CPM** (−20% CPM: hole $1.38M → $0.78M). Creative volume and landing-page speed are the product.
2. **Trial → paid** (+8 points: → $1.02M). This is the first 7 days of onboarding.
3. **Price** (+$5 with no conversion loss: → $1.00M). Test it; don't assume it.
4. **Organic breakout** (2×: → $1.04M). Content quality and the jacked-elder hook, plus a second language.
5. **Annual share and front-end AOV** (→ $0.91M / $1.11M). Cash timing, not LTV.
6. **Retention curve** (+5 points: → $1.28M within 18 months). A small effect on the cash hole but the largest on long-run value (S2 month-18 cash +$268K). It's also the defence against the downside case.

---

## 8. Assumptions most likely to be wrong (and which way)

| Assumption | Risk | Direction |
|---|---|---|
| CPM $18 for 55+ | No published age-band CPM found. The health & wellness median is $21.80. | Could be higher → use the downside case |
| Keyword comment rate 0.3% | Yang Mun's best reels reach ~1%. The average post is unknown. | Either way |
| Organic reach ramp (6K → 40K average views per post) | Labelled-AI accounts keep full reach on IG (BRIEF), but TikTok and YouTube are hostile to templated AI content | Downside on TikTok/YT, upside on IG/FB |
| Retention above benchmark | The engineered habit loop is unproven for this brand | The downside case uses the benchmark |
| Scale penalty 0.20 | Could be 0.3–0.4 above $10K/day if creative doesn't keep up | Downside for S3 |
| No price elasticity in the scenario sheets | Only the Sensitivity sheet applies elasticity | Price upside overstated in §5 stress row |

Sources for every benchmark are listed on the `Sources` sheet of `economics.xlsx`, and next to each input on `Assumptions` (column F).
