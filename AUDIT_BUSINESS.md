# AUDIT_BUSINESS.md: independent operator audit of the Strong Years blitz

Auditor stance: a skeptical direct-response and subscription operator who hadn't seen the project before. Scope: the business layers (model, offer, funnel, ads, content, retention, compliance, ops readiness). No project files were edited. Audit date: 2026-09-30.

Method:
- I read BRIEF (blitz addendum and canon), BLITZ, BLITZ_OPS, ECONOMICS, OFFER, FUNNEL, ADS, ADS_SCRIPTS, CONTENT_SYSTEM, CHARACTERS, SAFETY_RULES, EVIDENCE, POSTDB_FINDINGS §8, PIPELINE §4, EXPANSION and the products/ folder.
- I opened `economics.xlsx` with openpyxl twice: once for cached values and once for formulas.
- I rebuilt the Blitz engine in Python from the stated inputs, not by copying the formulas.
- I parsed all 150 scripts in SCRIPTS.md. I spot-checked 10 recipes against USDA FoodData Central values and 10 exercises for safety cues.
- I also read the app's privacy, terms, events and CAPI code, because several compliance promises live there.

---

## 0. Bottom line

1. **The workbook's arithmetic is correct and its assumptions are optimistic.** My independent engine reproduces R4 exactly: $10,169 on day 4, $42,922 on day 14 and $92,827 on day 30. Four inputs carry the plan, and all four sit at the favourable end of the evidence:
   - the arm-B conversion factor of 0.45 with a 0.935 renewal factor;
   - shoutouts at a 0.6% link-click rate per view on 120K views for $600;
   - no loss between a link click and a landing-page view;
   - a flat $18 CPM through an October–November launch.

   Moving each one to a defensible central value gives **~$49K MRR on day 30** at the $25 launch price. On that path $100K isn't reached within 90 days at the $500K cash cap.
2. **The playbook's own kill rule fires on the model's base case.** Blended media per net member on L4–L5 is $114 and $109, above the $95 cut line. That forces a 30% Meta cut from L6, and then day-30 MRR is $80.7K, not $92.8K.
3. **Day-30 MRR is a pre-churn peak.** In the charge-today arm, no founding member has faced a renewal by day 30. About 42% of the day-30 base is modelled to leave during days 31–60. The run-rate after the first renewal is about $54K, and it's hidden by new acquisition.
4. **The core product isn't built.** The pre-launch plan has no line for rendering the 8–12 minute daily session videos. Only sessions 1–14 exist, as scripts and a PDF. The six 12-week programs are sold as a $27 upsell and given as the L1–L5 bonus, and they don't exist yet. This is the biggest risk to refunds, renewal 1 and FTC exposure.
5. **Several compliance promises are made in copy but not delivered by the system:**
   - "text CANCEL" is offered while SMS is off;
   - ads and scripts say "we email before every renewal", but only the first renewal gets a reminder;
   - the privacy page says ad platforms receive only trial or purchase events, but the app sends a Lead event with hashed email and phone for every quiz opt-in;
   - the California annual reminder for monthly subscriptions is missing;
   - the Terms page is a policy summary, not a terms of service.

---

## 1. Independent recomputation of the blitz chain

### 1.1 The chain as stated (R4: arm B, $30, $8K/day Meta, 4 shoutouts a day, 20K + 10K warm contacts)

| Step | Input (cell) | Value |
|---|---|---|
| CPM | Assumptions!E29 | $18.00 |
| Link CTR | Assumptions!E30 | 1.5%, so CPC = $1.20 |
| Landing → quiz start | Assumptions!E31 | 65% (no click→page-view loss modelled) |
| Quiz → opt-in | Assumptions!E32 | 42%, so the base cost per opt-in is **$4.396** (Blitz!B10) |
| Account discount / scale penalty / learning | Blitz!B7, B12, B9 | ×0.90 × (8000/1500)^0.2 = ×1.398, then ×1.15 on days 1–7. Cost per opt-in: **$6.36** on days 1–7, **$5.53** after |
| Opt-in → arm-B purchase | Blitz!B14 × B15 × (20/30)^B19 | 13% × 0.45 × 0.8855 = **5.18%** |
| Meta media per founding purchase | derived | **$122.8** on days 1–7, **$106.7** from day 8 |
| Shoutout opt-ins per post | Blitz!B42 × B43 × E31 × E32 | 120,000 × 0.6% × 0.65 × 0.42 = **196.6** (≈ $3.05 per opt-in vs Meta's $5.53) |
| Refunds | Blitz!B16, B17 | 10% of purchases, removed 7 days after the purchase |
| Renewal 1 / 2 (arm B) | Blitz!B20 × B22, B21 × B22 | 0.58 / 0.4675, applied at day +30 / +60 |
| MRR | Blitz!W | active × $30 × 0.95 |

### 1.2 Results: workbook vs my engine

| | Day 4 | Day 14 | Day 30 | Day 60 | Day 90 | Media to d30 | Cash d30 |
|---|---|---|---|---|---|---|---|
| **Workbook R4** (Blitz!W410/W420/W436) | $10,169 | $42,922 | $92,827 | $125,637 | $160,210 | $303,600 | −$259,937 |
| **My engine, same inputs** | $10,169 | $42,922 | $92,827 | $125,637 | $160,210 | $303,600 | −$260,804 |
| Members (both) | 357 | 1,506 | 3,257 | 4,408 | 5,621 | | |

The match is exact on MRR and members; cash is within 0.3% because my fee and chargeback approximations differ slightly. Channel split, days 1–30: Meta 2,180 purchases, shoutouts 1,079, warm 128, organic 119, affiliates 18. That matches BLITZ.md:77–81. Two small workbook defects: `mrr_blitz_daily.csv` is consistent with the workbook, and **Blitz!B7 is stored as the text "0.10"**. Excel and LibreOffice coerce it today, but it's fragile.

### 1.3 Sensitivities (Δ vs R4 on day-30 MRR; my engine)

| Change (one at a time) | d4 | d14 | d30 | First day ≥ $100K |
|---|---|---|---|---|
| R4 as modelled ($30) | $10.2K | $42.9K | **$92.8K** | 36 |
| **Launch default price $25** (OFFER.md:36; the model runs $30) | $9.0K | $37.8K | $81.7K | 49 |
| Arm-B factor 0.35 (vs 0.45) | $7.9K | $33.4K | $72.2K | 63 |
| Click → landing-page-view loss of 20% | $8.5K | $35.2K | $75.6K | 57 |
| Shoutout link rate 0.3% (vs 0.6%) | $9.7K | $37.0K | $78.6K | 59 |
| No shoutouts bookable | $9.3K | $31.1K | $64.3K | not in 90 d |
| Q4 CPM +20% | $8.9K | $38.5K | $83.3K | 46 |
| Price elasticity 0.8 (vs 0.3) | $8.3K | $35.0K | $75.8K | 58 |
| Fresh ad account (CPM effect only; ignores the spend cap) | $8.4K | $38.7K | $85.5K | 43 |
| **The playbook's own L4–L10 cut fires (−30% Meta from L6)** | $10.2K | $38.4K | **$80.7K** | 50 |

### 1.4 Auditor central case (my recommendation for planning)

I set each input to a defensible central value:

| Input | Workbook | Auditor central | Why |
|---|---|---|---|
| Price | $30 | **$25** | The launch default everywhere (OFFER.md:36, BLITZ_OPS.md:11) |
| Arm-B factor | 0.45 | **0.40** | Adapty's $3B dataset: in Health & Fitness, trials outperform direct purchase, and trial users renew 8–60% better at renewal 1 ([Adapty](https://adapty.io/blog/free-trial-vs-direct-purchase-subscription-apps/)). RevenueCat's "5× hard paywall" figure compares a hard paywall with freemium on app installs, not a $1 trial with charge-today on cold web traffic ([RevenueCat via BuildMVPFast](https://www.buildmvpfast.com/blog/hard-paywall-vs-free-trial-revenuecat-indie-app-2026)). |
| Click → landing-page view | 100% | **85%** | Meta counts link clicks that never load ([Meta help](https://www.facebook.com/business/help/172641445757289)). The in-app browser and older phones add loss. |
| Shoutout link rate per view | 0.6% | **0.4%** | Implies a $5 CPM on 50+ pages and 720 clicks a post. Unbenchmarked (BLITZ.md:137). |
| CPM | $18 | **$19.80 (+10%)** | Q4 CPMs run about 15% above Q3, and CPC rises 20–40% in October and 30–60% in Nov–Dec ([Stackmatix](https://www.stackmatix.com/blog/facebook-ads-cost-complete-guide)). The launch runs Oct 12 → Nov 10 (BLITZ_OPS.md:9). The 55+ base itself is fine: 25–44 targeting costs 20–40% more than 45–65+ (same source). |
| Organic | 7 pages from day 1 | **30%** | 3-page warm-up (ECONOMICS.md:129) |
| Refunds | 10% | **12%** | Instant PDFs plus self-serve refunds (§3) |
| Warm SMS | on | **off** | TCPA seller-consent audit likely fails for most contacts (BLITZ_OPS.md:676–680) |

| | Day 4 | Day 14 | Day 30 | Day 60 | First ≥ $10K / $50K / $100K |
|---|---|---|---|---|---|
| **Auditor central ($25, existing account)** | **$5.7K** | **$22.9K** | **$49.4K** | $64.7K | day 7 / day 32 / not within 90 |
| Auditor central at $30 | $6.5K | $26.0K | $56.1K | $73.5K | 6 / 27 / — |
| Auditor central, $25 + Meta $12K/day | $7.4K | $29.0K | $62.4K | $79.8K | 6 / 25 / — (peak cash ≈ −$830K by day 90) |
| Downside (all adverse at once: 0.35, 80% LPV, 0.3%, +15% CPM, fresh account, 13% refunds) | $3.7K | $15.2K | $33.3K | $43.8K | 10 / 76 / — |

**Renewal-adjusted read.** Applying the 0.58 arm-B renewal-1 factor to the day-30 base gives the run-rate the business actually keeps: R4 $53.8K, auditor central $28.6K. Report both numbers to the client every time a milestone is claimed.

**Cash.** R4's "peak −$455K" (Blitz!N38) is where the 90-day window ends, not the real trough: cash is still falling $2.6K a day on day 90 (Blitz!AI496). Extending the same inputs with the full survival curve, **the trough is ≈ −$530K around day 155, plus ≈ $60K of reserve held.** So the "$500K cap" configuration exceeds its own cap.

**Is "charge-today converts at 0.45× the trial-start rate" reasonable?**
- It's the upper edge of plausible.
- It implies parity in paying members (5.18% vs arm A's 5.46% per opt-in), so removing the trial loses almost no payers.
- Direct-purchase data from health and fitness points the other way. In Adapty's data, trials outperform direct purchase in H&F, and trial cohorts renew 8–60% better, which makes the 0.935 renewal factor the most optimistic reading.
- The 7-day refund lag also flatters the day-4 and day-14 figures. On day 14 about 800 of the 1,506 "members" are still inside their 14-day refund window.
- Plan on 0.35–0.40 and let the L1–L3 read move it up.

---

## 2. Prioritized findings

Severity: **C** = critical (blocks the milestones or creates material legal exposure at launch), **H** = high, **M** = medium, **L** = low. Line numbers are 1-indexed.

| ID | Sev | File:line | Issue | Why it matters ($ / risk) | Concrete fix |
|---|---|---|---|---|---|
| F01 | **C** | BLITZ_OPS.md:67–82 (critical path), :115–182; products/daily_practice_sessions_1-14.md; FUNNEL.md:1669; BLITZ_OPS.md:308 | **The core product isn't in the build plan.** The D−10→D0 plan renders 150 organic posts and 40 ads but no member session videos. Only 14 sessions exist, as scripts and a PDF. The six 12-week programs are sold as the $27 "keep forever" upsell and given as the L1–L5 bonus, and they don't exist. Assumptions!E115 budgets $6K/mo for member content with no pipeline, owner or cadence. | L1 buyers exhaust the content on day 15, which is exactly when the refund window closes. Refunds over 12% trip the stop-scaling rule. Renewal 1 below 50% halts spend. Selling a program that doesn't exist is an FTC §5 misrepresentation. Each 10 points of renewal 1 ≈ ±$9K of day-60 MRR in R4. | Add a critical-path line before go-live: sessions 1–30 rendered for all 4 tracks plus weeks 1–4 of at least 2 programs. Release dates on the programs page. Sell upsell 1 only for programs that are complete (or as "pre-order, weeks released weekly" with clear dates). Give the member-content pipeline a named owner and a daily cadence (1 session/day plus 4 program sessions/week). |
| F02 | **C** | economics.xlsx Blitz_Plan!A67; BLITZ.md:100; BLITZ_OPS.md:1166 vs BLITZ.md:84 | **The kill rule contradicts the base case.** The rule is "media ÷ net new members > $95 two days running → −30% spend" on L4–L10. The model's own blended figure is $114 (L4) and $109 (L5), and $96.5 on L10–L11. | Following the playbook, Meta is cut 30% on L6, giving $80.7K on day 30 (−$12.1K) and $100K on day 50, not day 36. Either the rules or the projections are wrong. The client will see a "failure" that is really the plan executing. | Recalibrate the bands against the model: learning-phase allowance of ≤ $125 on L1–L7 and ≤ $110 on L8–L14 at $30. Or restate the R4 projections with the cut applied. Put both in Blitz_Plan and re-run. |
| F03 | **C** | Blitz!B15, B22, B42–B43; Assumptions!E29–E31; BLITZ.md:8–17 | **The headline stacks four optimistic inputs:** arm-B factor 0.45 and renewal 0.935 (above the H&F evidence), a 0.6% shoutout link rate ($5 CPM, unbenchmarked), no click→page-view loss, and a flat CPM through the Q4 ramp. | The auditor central case is $49K on day 30 vs $92.8K, and $100K isn't reached within 90 days. A client who commits $455K on the stated plan is probably under-reserved by $150–350K for the same outcome. | Present R4 as the upside. Adopt the §1.4 central case as the plan. Add a click→landing-page-view input (0.85), a Q4 CPM seasonality vector, a shoutout link rate of 0.3–0.4% until L3–L6 data exists, and arm B at 0.40 with a 0.90 renewal factor. |
| F04 | H | BLITZ.md:4, :14; Blitz!S407+ (renewal at d+30) | **Day-30 MRR is pre-churn.** No arm-B member has faced a renewal by day 30. Refunds are removed on day +7, so days 4–14 also count members still inside the refund window. | "$100K MRR in month 1" can be hit while the retained run-rate is ~58% of it. The client may scale into the days-31–60 renewal cliff. | Add two rows to Blitz and the dashboard: "MRR net of open refund windows" and "renewal-adjusted MRR" (members × expected renewal-1 survival). Report milestones on both. |
| F05 | H | BLITZ.md:8, :44; Blitz!N7 vs OFFER.md:36, BLITZ_OPS.md:11, :314 | Every headline number uses **$30**, but **$25** is the default display on all non-paid traffic, and on paid traffic too if $25 wins. | At $25: $81.7K on day 30 (−$11.1K) and $100K on day 49. The client is anchored on the wrong number. | Report R4 at $25 as the base and $30 as the "if $30 wins" case. |
| F06 | H | Blitz!N38; BLITZ.md:51, :153 | The **"peak cash" figure is where the 90-day window ends.** Cash is still falling $2.6K a day on day 90. | The true trough is ≈ −$530K around day 155, plus ≈ $60K of reserve. The "$500K cap" configuration breaches its cap. | Extend the Blitz engine to 240 days with the full survival curve. State the trough and the day it happens. |
| F07 | H | OFFER.md:42, :263–264; FUNNEL.md:77, :2237, :2307; BLITZ_OPS.md:307, :1122; Blitz!B26 = 0 | **Founding annual at $99** (3.3 months of a $30 founding price, 67–72% off) opens on L21 to the same members. Save offers downgrade to $12 Essentials or switch to $99 annual. None of this is modelled. | Every founding member who takes the annual turns $28.50 of MRR into $8.25. At 15% uptake of 3,000 members that's −$9K MRR. The baseline's own rule of about 6× the monthly price (OFFER.md:138–144) is broken. | Price the founding annual at $249–299 (≈ 10 months). Model annual share and save-offer downgrades in Blitz. Hold the annual until after renewal 1 (day 35+), not L21. |
| F08 | H | FUNNEL.md:1753–1760; app/src/app/(site)/terms/page.tsx:29; BLITZ_OPS.md:43, :308 | **Refund-abuse vector.** All PDFs (the $7 Reset, the $17 Kitchen, the $9 Wall Plan) are delivered instantly. Membership refunds are self-serve for 14 days. The Terms page makes one-time products refundable for 30 days, while `/join` calls them "yours to keep". The L1–L5 keep-forever program is granted immediately and kept after a refund. D5 extends refund-first to 60 days. | A "buy everything, download, refund" loop costs ≈ $58 of revenue plus fees per abuser. At the 10% refund assumption, a 3-point uplift ≈ −$1.5K day-30 MRR and ≈ −$10K cash. Refunds also feed the >12% stop rule. | State the bump and upsell refund terms in the `/join` terms box. Watermark PDFs with the buyer's email. Make the bonus program vest on day 15. Self-serve refund covers the membership only; bumps are refunded by request. Flag repeat refunders by card fingerprint. |
| F09 | H | app/src/app/(site)/terms/page.tsx:28; FUNNEL.md:1635, :1700, :1713; OFFER.md:128 | **"Text CANCEL" is offered as a way to cancel while SMS is off** for 3–6 weeks and no number exists. | The CA ARL and ROSCA require the stated cancellation mechanism to work. A consumer who texts into a void → complaint → AG/chargeback evidence against you. | Render "text CANCEL" only when `SMS_ENABLED=true`, on every surface (terms page, thank-you page, confirmation emails). |
| F10 | H | ADS_SCRIPTS.md:988, :994; SCRIPTS.md:5133, :5336, :5348 vs FUNNEL.md:1762; BLITZ_OPS.md:1228; terms page:27 | Ads and scripts say **"We email before every renewal"**. The spec and code send reminders only before the first renewal. | A deceptive advertising claim in a paid ad (FTC §5), and chargeback bait ("they said they'd warn me"). | Either build reminders before every renewal and model the churn cost (typically −2 to −5 points per renewal) or change the copy to "before your first renewal". I'd choose the copy change. |
| F11 | H | terms page:27; FUNNEL.md:1723, :1727 | **California ARL (AB 2863):** an annual reminder is required for *all* automatic renewals, including monthly ones, and price-change notice must be **7–30 days** before the change ([Cooley](https://www.cooley.com/news/insight/2025/2025-06-04-california-automatic-renewal-law-amendments-take-effect-on-july-1-2025)). The docs give an annual reminder only to yearly plans, and price notice "at least 30 days". | Statutory exposure plus class actions under the UCL. Minnesota's 2025 law has similar annual-notice rules (confirm with counsel). | Add a month-12 anniversary reminder for monthly members. Set price notices to exactly 30 days. Have counsel produce a 50-state ARL matrix (CA, NY GBL §527-a acknowledgment contents, MN, VA, CO) and wire it into `legal_pack`. |
| F12 | H | app/src/app/(site)/privacy/page.tsx:9–14; app/src/app/api/leads/route.ts:124 | **The privacy page is 5 paragraphs, and one statement is false.** It says advertising tools only receive trial or purchase events, but a CAPI `Lead` with hashed email and phone fires on every quiz opt-in, with `content_name=quiz_b` and path `/quiz/gut-energy`. It's missing the entity, categories, purposes, a subprocessor list (Stripe, Supabase, Anthropic, ElevenLabs, Twilio, ManyChat, Mux, Meta), retention, CCPA/CPRA "sharing" disclosure plus a Do Not Sell/Share link and GPC, and the separate Washington MHMDA Consumer Health Data Privacy Policy. | FTC Health Breach Notification Rule and §5 precedents (GoodRx, BetterHelp). WA MHMDA has a private right of action. Hashed email sent to Meta is "sharing" under the CPRA. | Write a full privacy policy plus a consumer health data policy linked on every page. Send the Lead event with a neutral path (`/q/b`) and no quiz identifier. Get opt-in consent for health data (quiz Q4, Q12 and chat memory). Add a "Your Privacy Choices" link with GPC honoured. |
| F13 | H | app/src/app/(site)/terms/page.tsx (whole file); Assumptions!E117 | **There's no terms of service.** The "Terms" page is a membership and cancellation summary. It has no assumption-of-risk or exercise waiver, limitation of liability, arbitration or class waiver, governing law, 18+ eligibility, AI-chat terms, community rules, IP licence or DMCA. No insurance is in place or specified anywhere. | Home exercise for 70-year-olds (balance tests, eyes-closed stands, wall sits) creates real injury claims. Without a waiver, arbitration and coverage, one fall case can exceed the whole month-1 margin. | Have counsel draft a ToS with an exercise risk acknowledgment (clickwrap at checkout and before the first session). Bind general liability plus professional liability (fitness instruction) plus media liability plus cyber plus product liability (kit) before L1. Budget $8–15K a year. |
| F14 | H | OFFER.md:93–95; FUNNEL.md:129; BLITZ_OPS.md:221 | **AI companion laws.** "Ask Chang/Sun", with memory and persona, is a companion chatbot. OFFER.md:95 promises that a crisis "alerts a human on call", but BLITZ_OPS.md:221 has no human between 23:00 and 07:00. NY GBL Art. 47 (in force since Nov 2025) requires an AI notice at the start and **at least every 3 hours** of continuing interaction, plus crisis referral. CA SB 243 requires the crisis protocol to be **published on the website**, and annual reports from July 2027. Illinois' 2025 WOPR Act bars AI therapy, a risk for Sun Yoon's "heart-to-heart" chat. | The SB 243 private right of action is $1,000 per violation. The NY AG can seek $15K a day. A 70-year-old in crisis at 2am with no human is also reputational catastrophe risk. | Add a 3-hour re-disclosure timer. Publish `/safety` with the crisis protocol. Buy 24/7 on-call coverage (a BPO or rotation). Block therapy-style responses on grief and relationship topics and route them to 988 or a human. |
| F15 | H | SCRIPTS.md:439–468 (S09 "58% FEWER FALLS"), :700–726 (S17, #bloodpressure), hashtags at :202, :235, :432, :465, :560; HOOKS.md:487, :501; PIPELINE.md:433 | **Organic posts carry implied fall and BP claims and condition hashtags.** 38 of 150 scripts use hashtags such as #fallprevention (×20), #kneepain (×13) and #sarcopenia, and the S09 thumbnail says "58% FEWER FALLS". PIPELINE routes organic breakouts to paid amplification (Spark or Partnership ads) with no ad-policy gate. | The characters' speech is advertising (OFFER.md:219). The 58% came from 24 weeks of supervised 2×60-minute Tai Ji Quan, not the product's 8-minute sessions, which makes it an establishment-claim mismatch. Boosting a breakout would break ADS.md §1 and risk the SY-Web health & wellness classification (purchase optimisation lost, CPA up an estimated 30–100%). | Run the ADS validator on every post flagged for amplification. Replace condition hashtags with activity tags (#balancetraining). Reword S09 as "in a 24-week class study…" with no percentage on the thumbnail. |
| F16 | H | BLITZ_OPS.md:73, :1076–1083; Blitz!N13 / B8 | **Ad-account feasibility.** New accounts start at €25–100 a day. The model's "fresh account" toggle changes only CPM, so R4's $8K a day from L1 is infeasible unless K9SUPPS qualifies. Using the K9SUPPS account puts a live revenue business's portfolio in the policy blast radius of an AI-health brand. | If K9SUPPS fails the criteria, days 1–14 are spend-capped, and $10K MRR moves from day 4 to about day 10–15. If Strong Years gets a strike, K9SUPPS's revenue is exposed. | Add a spend-cap ramp input to Blitz. Prefer a separate Strong Years portfolio with the K9SUPPS account *shared in* only if Meta support confirms isolation. Otherwise start seeding a fresh account now (D−30), not at D−10. |
| F17 | H | OFFER.md:75 ("the main tool against churn"); BLITZ_OPS.md:74; OFFER.md:181 (native app month 3–4) | **The first cohorts reach renewal 1 without their retention triggers.** The daily SMS is off for 3–6 weeks, there's no push until the native wrapper in month 3–4, and email is the only nudge. The 0.62 renewal assumption cites "the daily habit loop" (Assumptions!F50). | Renewal 1 for L1–L14 cohorts falls on L31–L44, before SMS is likely live. At benchmark (0.59 × 0.935 = 0.55) vs 0.58, that's ≈ −$3K day-60 MRR; if habit formation fails, the loss is far larger. | Ship PWA web push (Android plus iOS home-screen) before L1. Submit toll-free verification alongside 10DLC (often faster). Offer WhatsApp member-initiated opt-in. A human coach calls or texts from a personal line in the first cohort's week 3. |
| F18 | M | FUNNEL.md:1752–1756; Blitz!B24–B25 | **Three unticked bumps** ($7, $17, $9) on a mobile checkout for a 55+ buyer. The $17 bundle contains "12-Week Printable" and the $9 Wall Plan is also a 12-week calendar, so the products overlap. The $7 Reset (7 sessions) is content the membership already includes. The model assumes 35% + 15% + 30% attach ($12.49 per purchase). | Decision load and "am I paying twice?" doubts reduce the founding conversion rate (each −5% ≈ −$4.6K day-30 MRR in R4). Overlapping products drive refunds and complaints. | Keep **one** bump on `/join` (the $17 Kitchen, reworded so it doesn't overlap). Move the $9 and $7 items to a one-click post-purchase page. Model attach at ≤ 30% combined. |
| F19 | M | FUNNEL.md:1736–1772; BLITZ_OPS.md:1212 | **Trust gap on `/join`:** there's no real named human or company (legal name, address), no PayPal until L14 (a high-trust wallet for 55+), "No phone calls" (the descriptor promises a phone, BLITZ_OPS.md:1225), and a counter reading "212 of 5,000" on L1–L3 works as reverse social proof. | Weak trust suppresses the one conversion step the whole plan rests on. | Add a "Who runs Strong Years" block with the founder's name and photo, a company address and a support phone. Show PayPal from L1 (via Stripe's PayPal method if the account is eligible, otherwise bring Braintree forward). Show the counter only once it's past 1,000, or as "founding cohort open" plus the real count on the terms page. |
| F20 | M | OFFER.md:37; BLITZ_OPS.md:310–312; FUNNEL.md:71 | **Founding cap timing.** At R4 pace the 5,000 cap closes around day 50, but the model keeps $30 pricing and conversion to day 90. At central-case pace, "founding" may run for 4–6 months and become the de facto regular price, which creates 16 CFR 233.1 introductory-price and state "former price" risk. | The model misstates days 50–90 (MRR per member +17% at $35, conversion −4.5%). In the slow case the "founding" and "locked" savings claims become deceptive. | Close the cap at "5,000 or [date], whichever comes first". Model the switch to the standard price. |
| F21 | M | OFFER.md:14 ("90-second"); BLITZ.md:142 ("7-question"); FUNNEL.md:626–760 (14 questions + 2 standing tests, "3 minutes") | **Quiz friction and inconsistency.** Paid cold traffic from the Facebook in-app browser is asked to push a chair against a wall and do a 4-stage balance test. The 65% and 42% benchmarks come from ordinary quizzes. | Likely 20–40% below the modelled rates (at −20% on this lever, −$17.2K day-30 MRR per BLITZ.md:142). There's also liability from unsupervised balance tests. | Default paid traffic to the short version (Q1–Q5 plus T1, with T2 moved into the app). Make standing tests optional ("do it later"). Settle one spec across OFFER, FUNNEL and BLITZ. |
| F22 | M | BLITZ_OPS.md:672–674, :722–806 | **Health-inferred warm list.** The Unignorable list (a perimenopause purchase) is used to email a different brand's offer. BLITZ_OPS blocks list transfer and custom audiences but not the use itself. | WA MHMDA and CT/NV health-data rules restrict processing consumer health data beyond the consented purpose. | Counsel sign-off on D−4 specifically for this. Suppress WA, NV and CT residents from cross-promotion unless the original consent covers it. |
| F23 | M | app/src/app/api/leads/route.ts:124; BLITZ_OPS.md:137, :285; FUNNEL.md:620 | **Event hygiene.** The Lead event carries `/quiz/gut-energy` in the source URL, which breaks BLITZ_OPS's own "no condition words" check. FUNNEL specifies profile-coded result events (`q_a_result_p6` = Safe Mode = chest pain or fall), which leak health status if ever wired to Meta. BLITZ_OPS expects browser plus server deduplicated events, but the app is CAPI-only (no `fbq`). | Health & wellness classification of SY-Web. The dedup QA row fails on D−3. Browser events are lost (lower match quality). | Use the rewritten `/q/a` and `/q/b` paths in CAPI. Delete the result-event spec from FUNNEL. Either add the browser pixel on `/join` only, or update the QA matrix to CAPI-only. |
| F24 | M | BLITZ_OPS.md:183, :291, :319, :683, :724, :810; FUNNEL.md:353 vs app/src/app routes | **Pages the plan links to don't exist in the app:** `/w`, `/walk`, `/live`, `/p/{slug}`, `/science`. The app has `/how-we-make-this`. | Warm emails, shoutout tracking and the L3 event would 404 on launch week. | Build them or point every link to existing routes. Add a link-check to the D−1 rehearsal. |
| F25 | M | BLITZ_OPS.md:273 | **Processor 2 (Braintree) isn't built**, but the model assumes it on day 21 and the capacity rules depend on it. | Stripe risk review at about $150K in month 1 on a new account is a single point of failure (a hold on the processor holding 100% of cash). | Build the payments abstraction pre-launch, or get written Stripe volume pre-approval. |
| F26 | M | OFFER.md:192 ("9pm–9am"); FUNNEL.md:125 ("8am–9pm"); BLITZ_OPS.md:528, :681 ("10:00–20:00") | **SMS quiet hours contradict each other.** FUNNEL's 8am–9pm breaches Florida's FTSA and similar 8pm state limits. | Mini-TCPA statutory damages per text. | Set one canonical window, 10:00–20:00 recipient local time, everywhere. |
| F27 | M | BRIEF.md:45, :51; OFFER.md:151; FUNNEL.md:1727; BLITZ_OPS.md:42 vs OFFER.md:35, BLITZ_OPS.md:305 | **"Founding price for life" vs "while subscribed".** Pause (OFFER.md:262) isn't addressed. | A "for life" claim is misleading when the lock ends on cancellation. | Use "locked while you stay subscribed (including pauses)" everywhere, and specify what happens on pause. |
| F28 | M | ECONOMICS.md:13–16, :127–133 vs BLITZ.md:153; ECONOMICS.md:129 vs BLITZ_OPS.md:9 | **Strategy contradiction.** ECONOMICS recommends S2 as the plan and a $3–5K a day test with a day-10 gate ("spend $60K to find out, not $700K"). BLITZ commits $8K a day from L1 with a 72-hour read. ECONOMICS says launch is 2–3 weeks after kickoff; BLITZ_OPS says 10 days. | The client gets two incompatible recommendations. The 10-day build is aggressive given processor, Meta verification and attorney lead times. | Pick one. My recommendation: $3K/day on L1–L3 → the L4 gate → R4 if green. Mark ECONOMICS §7 as superseded by BLITZ. |
| F29 | M | Assumptions!E113 ($6,000) vs PIPELINE.md:261 ($2.5–3.5K); Assumptions!E116–E118; FUNNEL.md:130 | **Opex is inconsistent and incomplete.** Reviewer cost differs between files. VAs (PIPELINE.md:260), 7-day support coverage (BLITZ_OPS.md:220–222), launch legal (attorney markup of checkout, 3 contracts and cross-brand sends ≈ $10–25K, not $2–5K), Verifi/Ethoca, the affiliate tool, the help desk and insurance are all missing. | Understated by roughly $10–20K a month in months 1–3. | Reconcile the numbers and add one-time launch costs as a separate line in Blitz. |
| F30 | M | SCRIPTS.md:700–726 (S17); products/strength_reset.md:440 vs :452 | **Wall-sit risk.** S17 frames isometric holds as a contest ("Who stops first? I do sixty seconds") for an audience that's often hypertensive, while its own safety line says 20 seconds. The product dose is 2 × 15 s, but "Easier" says "10 seconds instead of 20". | Valsalva and BP-spike risk, and a mixed message on dose. | Remove the competitive frame and cap the challenge at 20–30 s with "keep talking". Fix the dose text. |
| F31 | M | products/strength_reset.md:634; products/daily_practice_sessions_1-14.md:584, :520; CONTENT_SYSTEM.md:429 | **Risky balance progressions:** eyes-closed single-leg stance ("Chang's level") and backward walking with a hovering hand. The public "30-Day Balance" series ends with eyes closed. | A fall for a 75+ viewer at home is plausible and brings liability. | Eyes-closed work only with both hands resting on the counter, in the Iron track, never in public organic. Backward walking only with a hand on the counter. |
| F32 | M | FUNNEL.md:785–794, :2310; OFFER.md:268 | **The Strength Age scale** (−2.5 years per chair-stand rep) plus retest learning effects means most members are shown "years younger" on retest 1. The "hands used" score of +8 differs from STEADI's 0. | Implied efficacy framing. It's also a strong, legitimate retention device if made honest. | Show the rep and stage deltas first. Cap monthly improvement display. Add "early gains include practice with the test". |
| F33 | M | SCRIPTS.md (150 scripts); POSTDB_FINDINGS.md:293–295; CONTENT_SYSTEM.md:457; BLITZ_OPS.md:80 | **Scripts drift from the POSTDB rules:**<br>• 80 of 150 hooks fall outside the 13–22-word first line (rule 4).<br>• Only 14 of 150 use the winning "If you ___ every ___" grammar and 0 use "The number one ___ is not X" (rule 3).<br>• 4 scripts are under 70 words.<br>• 57 of 150 are for pages that go live only on day 15 or 22, so the launch has 93 usable masters on 3 pages, not 150. | Weak adherence to the proven hook set lowers the breakout odds that make organic worth anything. | Regenerate about 30% of hooks into the rule-3 grammar. Re-allocate the 57 scripts to the 3 day-1 pages or label them "day 15+". |
| F34 | M | EXPANSION.md:69 | US and US-Hispanic are priced at $20, against a $35 US standard after the cap. | A same-market price gap by language is a national-origin proxy (CA Unruh Act). It's also inconsistent with the blitz pricing. | Use one US price across languages, and geo-price only by country. |
| F35 | L | economics.xlsx Blitz!B7 | Numeric input stored as text ("0.10"). | Breaks under a strict-typing setting or with SUM. | Store it as the number 0.1. |
| F36 | L | BLITZ.md:87; Blitz_Plan!A55 | "One-screen cancel" and "48h pre-billing flow" are stale; the blitz uses two screens and reminders 7 and 2 days before renewal. | Spec drift. | Update both. |
| F37 | L | BLITZ_OPS.md:1225 vs terms page:28 | The descriptor lists "support URL and phone", but the Terms say "No phone calls". | Confusing, and a phone line helps a 55+ audience. | Keep a phone line for billing questions (not required for cancellation). |
| F38 | L | FUNNEL.md:353 vs :543 | Two sources pages: `/science` and `/how-we-make-this`. | A broken link. | Keep one. |
| F39 | L | ADS.md:56, :139 | "…compares with typical results for **your age**" in the concept doc. ADS_SCRIPTS is clean. | A borderline Meta personal-attributes issue if copied. | Use "…with typical results by age". |
| F40 | L | ADS_SCRIPTS.md:176, :1154 | Ads show a progress chart labelled "Example". | Hypothetical results imply typicality (FTC Endorsement Guides §255.2). | Show a chart with no trend (only the axis and "your number here"). |
| F41 | L | SCRIPTS.md:1638 (S46) | Sun Yoon advises on forgiving infidelity, then sends the viewer to BEGIN. | Off-brand for a strength product. It monetises emotional vulnerability and invites confessional DMs to an AI. | Cut it, or keep it without a sales CTA on IG only. |

**Severity counts:** Critical 3 · High 14 · Medium 17 · Low 7 · **Total 41.**

### What checked out
- **Recipes (10 of 24):** B1, B3, B4, L1, L3, L4, D2, D5, S1 and N1. Protein and fiber per serving, recomputed from USDA FoodData Central SR Legacy values, all fall within about ±10% of the stated figures. For example, B3 fiber is 10.5 vs 10.5 stated, and D2 protein is 39.9 vs 41.1 stated. Spot-verified sources: edamame, frozen, prepared, 11.9 g protein and 5.2 g fiber per 100 g ([MyFoodData/FDC 168411](https://tools.myfooddata.com/nutrition-facts/168411/wt1)); chicken breast raw ≈ 22.5 g ([FDC 171077](https://tools.myfooddata.com/nutrition-facts/171077/wt1)); farmed Atlantic salmon ≈ 20.7 g ([FDC 175167](https://tools.myfooddata.com/nutrition-facts/175167/wt1)). One minor gap: S1 fiber (2.3 stated vs about 2.5–3.2 depending on the tofu entry). L3 correctly uses cooked-pasta weights. The scripts' oat-bowl math (S104: 4 + 8 + 2 = 14 g) is correct.
- **Exercises (10):** chair sit-to-stand, heel raise, high wall sit, standing march, heel-to-toe stand, one-leg stand, heel-to-toe walk, side steps, wall push-up and jug row. Cues are good: chair against the wall, knee tracking, exhale on effort, a DVT red flag, osteoporosis hinge limits, shoes on and no socks on hard floors, stop rules with 911 triggers. The exceptions are F30 and F31. Joint-replacement cues appear in the sessions and SAFETY_RULES.
- **ADS_SCRIPTS (40 ads):** the AI tag in the first 3 s and in line 1, full recurring terms wherever a price appears, no "you + age", no before/after, no CDC naming. Meta policy exposure in the paid set is low. The risk is in organic amplification (F15) and the concept doc (F39).
- **Warm-list email and SMS legal design** (BLITZ_OPS.md §3.1): the CAN-SPAM designated-sender design is correct, TCPA seller-consent is gated, and there's no custom-audience upload. Only F22 remains.
- **The honest-scarcity design** is solid: a real database count, refunds decrement it, no timers, a real deadline bonus. Only F19 and F20 remain.

---

## 3. Offer and funnel conversion risks (summary)
1. **The single-point dependency is the arm-B purchase rate** (F03). Nothing on `/join` offsets the loss of the trial's low-risk entry. The founding page has no human identity, no reviews (correctly, since none exist yet), no PayPal until L14 and no phone (F19).
2. **Checkout load:** three bumps with overlapping contents (F18). Test one bump against zero on paid traffic during L1–L5 alongside the price test, or run the price test alone and hold bumps at one.
3. **Page speed:** `/join` targets LCP < 2.0 s with no images (good). The heavier risk is `/q/a` (video demo loops, audio, 16 screens) in the Facebook in-app browser. Add an LCP budget and a lite mode for the quiz and the result page, and measure time-to-first-question.
4. **Refund abuse:** see F08. Instant downloads plus self-serve refunds plus a keep-forever bonus is the textbook pattern.
5. **Promise vs delivery:** F01 is the conversion-to-retention bridge. The copy sells "a new session every day" and "all six programs".

## 4. Retention in months 2–3: is there enough?
**Not yet.** OFFER §5 has good mechanics: milestones at days 30, 60 and 90, churn predictors, one save offer, winback. But the inputs that make them work are missing at launch:
- **Content inventory** (F01): about 60 sessions and 6 programs are needed by day 90; 14 scripts exist.
- **Triggers** (F17): no SMS for 3–6 weeks, no push, email only.
- **Renewal-1 design for a charge-today cohort:** the trial arm had a "5 sessions done" pre-charge moment, but founding members get a reminder 7 and 2 days before renewal with no progress event. Add a **day-25 retest plus certificate** before the day-23 and day-28 reminders, so the renewal notice arrives right after a win.
- **Refund-window check-in:** a human or AI check-in on days 10–12 ("Is it working? Here's the easier track") before the day-14 refund cliff.
- **Cohort retention reporting:** renewal-1 by acquisition channel (shoutouts vs Meta vs warm), because shoutout buyers may churn differently.
- **Save-offer economics** (F07): $12 Essentials and $99 annual as saves dilute MRR. Test pause-first.
- **Community:** the Courtyard needs seeded humans (the moderation roster covers only 07:00–23:00).

## 5. Compliance exposure (condensed)
- **Health claims:** the paid set is clean. Organic carries implied fall and BP claims and condition hashtags (F15, F30). The Strength Age "years younger" framing (F32).
- **Fake scarcity:** well designed. The remaining risk is the "founding" price becoming permanent (F20) and the mixed "for life" wording (F27).
- **Auto-renewal:**
  - CA annual reminder and the 7–30-day price-notice window (F11);
  - a non-functional "text CANCEL" (F09);
  - the "every renewal" ad claim (F10);
  - MN and VA notice rules to confirm;
  - NY §527-a acknowledgment content (the confirmation email in FUNNEL §5.5 B is written for trials; it needs a founding version with the cancellation mechanism);
  - consent records of 3 years+ are already covered.
- **CAN-SPAM/TCPA:** the design is correct (BLITZ_OPS §3.1). Quiet-hours conflict (F26). Launch emails come from a new sending domain created on D−10 with DMARC p=none: add a warm-up schedule.
- **FTC endorsements and affiliates:** shoutouts need #ad plus a Partnership ad (covered). The PT affiliate material-connection and state practice-act items are covered (BLITZ_OPS.md:1034–1044). Affiliates also need W-9/1099 collection.
- **AI companion law:** F14 (NY 3-hour notice, SB 243 published protocol, 24/7 human coverage, Illinois therapy ban).
- **Meta ad policy:** low in ADS_SCRIPTS. It rises if organic winners are amplified (F15) or the event paths leak condition words (F23).
- **Privacy and health data:** F12, F22, F23.

## 6. Consistency: contradictions found (file:line)
| Topic | Contradiction |
|---|---|
| Price used in headline numbers | BLITZ.md:44 / Blitz!N7 **$30** vs OFFER.md:36, BLITZ_OPS.md:11 **$25 default** |
| Founding lock | BRIEF.md:45, :51; OFFER.md:151; FUNNEL.md:1727; BLITZ_OPS.md:42 "for life" vs OFFER.md:35; FUNNEL.md:71; BLITZ_OPS.md:305 "while subscribed" |
| Renewal reminders | ADS_SCRIPTS.md:988, :994; SCRIPTS.md:5133, :5336, :5348 "every renewal" vs FUNNEL.md:1762; BLITZ_OPS.md:274, :1228; terms page:27 "first renewal" |
| Cancel screens | BLITZ.md:87; Blitz_Plan!A55 "one-screen" vs OFFER.md:27, :132; FUNNEL.md:1761 "at most two screens" |
| SMS quiet hours | OFFER.md:192 (9pm–9am) vs FUNNEL.md:125 (8am–9pm) vs BLITZ_OPS.md:528, :681 (10:00–20:00) |
| Quiz length | OFFER.md:14 "90-second" / OFFER.md:109 "7–9 questions" vs BLITZ.md:142 "7-question" vs FUNNEL.md:626 "3 minutes", 14 questions + 2 tests |
| Crisis coverage | OFFER.md:95 "alerts a human on call" vs BLITZ_OPS.md:221 no human 23:00–07:00 |
| Launch timing | ECONOMICS.md:129 "2–3 weeks after kickoff" vs BLITZ_OPS.md:9 10 days (Oct 2 → Oct 12) |
| Launch strategy | ECONOMICS.md:16, :131 ($3–5K/day, day-10 gate) vs BLITZ.md:46, :153 ($8K/day from L1) |
| Processor 2 date | Blitz!B56 day 21 vs BLITZ_OPS.md:70 L14; code doesn't exist (BLITZ_OPS.md:273) |
| Reviewer cost | Assumptions!E113 $6,000/mo vs PIPELINE.md:261 $2,500–3,500 |
| Kill thresholds | Blitz_Plan!A67 and BLITZ_OPS.md:1166 cut at > $95 per net member vs BLITZ.md:84 base case $91–114 |
| Launch masters | BLITZ_OPS.md:80 "150 masters" vs CONTENT_SYSTEM.md:457 (57 of the 150 scripts are for pages that go live on day 15 or 22) |
| Organic pages | Blitz!J col (S3, 7 pages from day 1) vs ECONOMICS.md:129 / CONTENT_SYSTEM.md:457 (3 pages, ramping) |
| Bump refunds | FUNNEL.md:1753–1755 "yours to keep" vs terms page:29 "one-time products: 30 days" vs BLITZ_OPS.md:43 "up to 60 days" |
| Sources page | FUNNEL.md:353 `/science` vs FUNNEL.md:543 and the app `/how-we-make-this` |
| Event spec | FUNNEL.md:620 (`q_a_result_{profile}`) vs app `/api/events` whitelist vs BLITZ_OPS.md:285 (browser + server dedup; the app is CAPI-only) |
| US price | EXPANSION.md:69 US $20 vs BLITZ_OPS.md:42 standard $35 |
| Phone support | BLITZ_OPS.md:1225 (phone on the descriptor) vs terms page:28 "No phone calls" |
| Wall-sit dose | products/strength_reset.md:440 (15 s) vs :452 ("10 seconds instead of 20") |

Consistent across all files:
- the 12 keywords (FUNNEL.md:172; SCRIPTS uses all 12; FOUNDER kept only as a JOIN variant, FUNNEL.md:1571);
- page handles (`@changyin`, `@sunyoon.kitchen`, `@changandsun` on day 1; `.strength` and `.mobility` on day 15; `@sunyoon` on day 22; `.espanol` on day 30);
- character ages and backstory (74/76, married 1976, California since 1983);
- the calendar (Oct 12 = Mon = L1, L30 = Tue Nov 10);
- the 5,000 cap, the 14-day guarantee in blitz mode, the 30% affiliate default, and gift pricing.

## 7. Content quality: 10 random scripts rated (seeded sample of 30)
| Script | Score | Reason |
|---|---|---|
| S01 30-second chair stand | **8** | Demo in the first second, a number to beat, a strong keyword tie. Hook is 11 words; #fallprevention hashtag. |
| S07 "Lifting is dangerous after 60" | **8** | A clean myth hook, a real trial count, a built-in safety line. More talking than demo. |
| S32 "He was 20 grams short" | **8** | Object and number up front, Sun's voice perfect, protein on-strategy. |
| S104 Oats, 14 g fiber by 8 a.m. | **7** | Uses the rule-3 grammar, correct gram math. The mortality stat is observational (phrased "linked", fine). |
| S112 Blueberries in water, "watch what happens" | **7** | A clever parody of Yang Mun's format and brand-defining honesty. The payoff ("they float") risks a completion drop. |
| S149 Founding terms cross-examination | **7** | Turns compliance into content. But it claims "We email before every renewal" (F10). |
| S17 Wall-sit duet | **6** | Great challenge mechanic. Undercut by the BP claim and a competitive isometric hold (F30). |
| S57 "He snores: see the doctor" | **6** | Responsible safety message. No demo, 64 words, #sleepapnea, a weak link to SLEEP. |
| S129 Printer ink, friendship study | **5** | Accurate (Holt-Lunstad, 148 studies). An abstract hook, no object or body in the first 3 words, TikTok-bottom-tier topic. |
| S46 "He cheated 30 years ago" | **3** | Off-brand relationship counselling from an AI, monetised with BEGIN, invites confessional DMs (F41). |

Overall: **varied and mostly on-voice.** There are no duplicate hooks and no duplicate hook IDs, 35 formats and 20 pillars are used, and repeated sentences are mostly deliberate CTA and safety cues ("Breathe out as you stand" ×15). The weaknesses:
- under-use of the proven hook grammar (14 of 150), and 80 of 150 first lines outside the 13–22-word rule;
- 38 of 150 carry condition hashtags;
- 57 of 150 target pages that aren't live at launch.

## 8. Missing entirely (or only named, not built) before go-live
| Item | Status | Needed for |
|---|---|---|
| **Member session video production** (sessions 15–90 plus all 4 tracks) and **the six 12-week programs** | Missing (14 session scripts only) | Delivering what is sold; refunds; renewal 1 |
| **Terms of service** (exercise risk acknowledgment, liability limits, arbitration, AI-chat terms, 18+, community rules, DMCA) | Missing (the app `/terms` is a policy summary) | Injury and litigation exposure |
| **Full privacy policy + WA MHMDA consumer health data policy + "Your Privacy Choices"/GPC** | Missing (a 5-paragraph page with a false statement) | FTC, MHMDA, CPRA |
| **Data processing inventory** (RoPA, subprocessor list, DPAs with Anthropic/ElevenLabs/Twilio/ManyChat/Supabase/Mux/ESP, retention schedule, zero-retention settings for chat) | Missing | Privacy compliance, vendor risk |
| **Insurance** (general liability, professional/fitness instruction, media/IP, cyber, product liability for the kit) | Missing | Any injury or IP claim |
| **Sales tax** (Stripe Tax, nexus monitoring for digital subscriptions in states such as WA, PA and TX, and the physical kit) | Missing for the US (EXPANSION covers only MX/BR) | Liability accrues from the first sale in taxing states |
| **Entity setup** (formation, EIN, bank, registered agent, the "same team" relationship with Unignorable and K9SUPPS) | Decision D2 only | Processor underwriting, the CAN-SPAM "same team" line |
| **Reviewer contract template** (scope, indemnity, credential verification, naming consent, reviewer-gate evidence log) | Missing ("send the contract") | Unlocking the reviewer-gated copy |
| **Performer and demonstrator release** (incl. AI/derivative-motion and digital-replica clause; CA AB 2602-style specificity; "Frank" real demonstrator) | Mentioned ("video release"), no template | Driving-video use in AI renders |
| **24/7 crisis and moderation roster** | Partial (07:00–23:00) | SB 243 / NY Art. 47 duty of care |
| **Published crisis protocol page** (`/safety`) and **SB 243 incident log** | Missing | CA SB 243 |
| **50-state ARL matrix** and the **CA/MN annual reminder** job | Missing | Auto-renewal compliance |
| **Refund and cancellation policy covering bumps and upsells** consistently | Contradictory (F08) | Refund abuse, disputes |
| **Creative testing matrix** (concept × hook × format × audience cells, budget per cell, significance rule) | Partial (ADS.md §5, BLITZ_OPS.md §6.2/§6.6) | Disciplined creative learning at 5 ads a day |
| **Cohort retention dashboard** (renewal 1 by channel and price cell, refund-window MRR) | Partial (BLITZ_OPS.md §7.2 and `/admin` cover funnel KPIs) | Reading F04 correctly |
| **Pages linked by the plan:** `/w`, `/walk`, `/live`, `/p/{slug}` | Missing in the app | Warm, shoutout and event traffic |
| **Processor 2 code** (Braintree) | Missing (BLITZ_OPS.md:273) | Capacity and hold risk |
| **Email domain warm-up plan** | Missing (DMARC p=none on D−10) | Launch-email deliverability |
| **Affiliate tax onboarding** (W-9/1099) and **affiliate agreement template** | Terms described, no template | Affiliate program |
| **Accessibility audit** (WCAG 2.2 AA on the checkout and quiz) | Palette only (FUNNEL.md:267) | ADA web claims; conversion for 70+ |
| Customer support tool | **Exists** (Help Scout/Gorgias, BLITZ_OPS.md:143; macros §8) | — |
| Merchant descriptor | **Exists** (`STRONGYEARS MEMBER`) | — |
| Character reference pack job | **Exists** (CHARACTERS §13.1; BLITZ_OPS.md:96) | — |
| KPI dashboard | **Exists** (BLITZ_OPS.md §7.2; app `/admin`) | — |

---

### Sources used in this audit
- [Adapty: trial vs direct purchase, $3B revenue data](https://adapty.io/blog/free-trial-vs-direct-purchase-subscription-apps/)
- [RevenueCat 2026 data summarized (hard paywall vs freemium, trial lengths)](https://www.buildmvpfast.com/blog/hard-paywall-vs-free-trial-revenuecat-indie-app-2026)
- [dev.to/PaywallPro: opt-in vs opt-out trial conversion](https://dev.to/paywallpro/free-trial-vs-no-trial-model-a-paradigm-shift-in-subscription-conversions-p2)
- [Stackmatix: Q4 CPM/CPC seasonality; age-band cost differences](https://www.stackmatix.com/blog/facebook-ads-cost-complete-guide)
- [Triple Whale: BFCM 2025 CPM $22.26 (+7.8% YoY)](https://www.triplewhale.com/blog/facebook-ads-bfcm)
- [Meta: link clicks vs landing page views](https://www.facebook.com/business/help/172641445757289)
- [Cooley: California ARL amendments (AB 2863) effective July 1 2025](https://www.cooley.com/news/insight/2025/2025-06-04-california-automatic-renewal-law-amendments-take-effect-on-july-1-2025)
- [MyFoodData (USDA FDC) 168411 edamame](https://tools.myfooddata.com/nutrition-facts/168411/wt1), [171077 chicken breast](https://tools.myfooddata.com/nutrition-facts/171077/wt1), [175167 farmed Atlantic salmon](https://tools.myfooddata.com/nutrition-facts/175167/wt1)
