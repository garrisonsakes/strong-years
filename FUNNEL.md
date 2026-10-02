# FUNNEL.md — Chang Yin & Sun Yoon: Acquisition, Conversion, Onboarding and Retention System

> **CANON BANNER (Round 5 audit, Oct 1 2026).** BRIEF.md CANON UPDATE 2 + 3 supersede every price, cell and button in §0–§3 and §5 of this file: **there is no $1 trial, no T25/F25/F30 cells and no "Start 7 days for $1" button.** The launch is Shopify cell B ("$12 today = both Starter Books + your first founding month, then $25/mo", STARTER12) with cell A ($12 books only, founding offer on the thank-you page + 3 emails) as the test. Read §4.19 and the launch link rule in §4.1 for the live copy; LAUNCH_RUNBOOK.md §0 is the price table. Lines below that still say "$1", "trial", "T25" or "F30" are historical and must not be built.

Membership brand: **Strong Years** (from OFFER.md). **Daily Practice** is the name of one feature inside it: the daily 8–12 minute follow-along session ("your Daily Practice"). Prices, bumps, upsells and test cells match OFFER.md and the `Assumptions` sheet in economics.xlsx; character facts match CHARACTERS.md.
Working domain placeholder: `{{DOMAIN}}` (e.g. strongyears.com). Price placeholder: `{{PRICE}}` (baseline control $20/mo; test cells $15 and $25). Blitz mode (the launch default) uses `{{FOUNDING_PRICE}}` ($25 default display; $25 vs $30 test) and `{{STANDARD_PRICE}}` (after the cap; default $35, client decision): see §0.2.1.
Human reviewer placeholders: `[PT NAME], PT, DPT` (physical therapist, content reviewer), `[RD NAME], RDN` (registered dietitian), `[MD NAME], MD` (medical advisor, optional but strongly recommended before paid scale).

**Reviewer gate (applies to both FUNNEL.md and ADS.md).** No reviewer is signed yet. Every sentence that claims professional review, names a reviewer, or promises a credentialed human is written as:
`[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: <claim>] FALLBACK: "<line that makes no review claim>"`
Until a licensed reviewer has signed a contract (and, for anyone named or pictured, a written consent to be named), ship the FALLBACK text only. Where a whole block depends on a named human (the "real humans" section, the PT ad, the live Q&A with a credentialed host), the fallback says what to show instead, or to omit the block.

**Canonical policies (audit fixes, Sep 30 2026; AUDIT_BUSINESS.md F08–F14, F19–F21, F26–F27). These override any older line in this file and apply to OFFER.md, ADS.md and BLITZ_OPS.md too.**
- **SMS-conditional copy.** Anything written as `{{IF_SMS: …}}` renders only when `SMS_ENABLED=true`. Until 10DLC / toll-free approval, "text CANCEL", "reply CANCEL", "we'll email and text you" and every SMS line are removed, not left in place. Cancellation methods shown to buyers are always ones that work today: online in the account (at most two screens) and replying "cancel" to any email.
- **Refunds.** (Watermarking PDFs with the buyer's email is an internal control in progress, LAUNCH_CHECKLIST #21; customer copy doesn't mention it until it's built and verified.) A **14-day money-back guarantee on the membership charge, one per person** (matched on email and card fingerprint), self-serve in the account. It covers the first membership charge in every mode (the old 30-day line in standard mode is retired). **Add-ons have their own terms:** the $7 Reset, the $17 Strong Kitchen, the $9 Wall Plan, the $27 keep-forever program and the $7 printables are digital downloads, delivered instantly and watermarked with the buyer's email; they're refunded **on request within 14 days** (email support; not part of the self-serve membership refund). The $29 kit: 30 days, no return needed. Refund-first SOP beyond the guarantee (BLITZ_OPS.md §8.4) is a support discretion, never advertised.
- **Bonus program vesting.** The founding-week keep-forever program (and any bonus PDF) is visible in the app from day 1 as member content, but the **keep-forever download unlocks on day 15**, after the refund window closes. Say so wherever the bonus is offered.
- **Renewal reminders go before every charge.** Monthly: email 7 and 2 days before the first renewal, then 3 days before every renewal after that. Annual: 30 days before. Trial arm (if on): 48 hours before the first charge. SMS copies only when SMS is live.
- **California annual reminder (AB 2863).** Once every 12 months, every auto-renewing member (monthly included) gets an email with the plan, the price, the billing frequency and how to cancel. Price changes: notice sent **exactly 30 days** before (inside California's 7–30 day window), with a one-tap cancel link.
- **Founding price wording.** "Locked while you stay subscribed (pauses included)". Never "for life". Cancel and rejoin = the price current then.
- **Founding cap and counter.** The cohort closes at **5,000 members or `{{FOUNDING_CLOSE_DATE}}` (default L90 = Sat Jan 9 2027; client decision), whichever comes first**, stated on `/join` and the terms page from L1. The count is the real database count (first charge succeeded, not refunded or charged back). Public display rule, `{{COUNT_LINE}}`: below 1,000 members show "Founding membership is open to the first 5,000 members or until {{FOUNDING_CLOSE_DATE}}, whichever comes first. See the live count: {{DOMAIN}}/terms#founding"; from 1,000 show "{{COUNT}} of 5,000 founding seats taken as of {{COUNT_TIME}}". Both are true; neither is a countdown. "Only a few left" is allowed only when the real count is ≥ 4,900.
- **Human coverage and crisis resources.** A real person on the team reads messages **7:00–23:00 Eastern, 7 days** (BLITZ_OPS.md §1.3). No copy promises a human "on call" or "24/7". Outside those hours, crisis messages get the automated crisis-resources reply immediately and a person reads them at 7:00 Eastern. The crisis-resources line, used everywhere a crisis could surface: "If you're thinking about harming yourself, call or text **988** (Suicide & Crisis Lifeline, free, 24/7). If you're in danger or it's a medical emergency, call **911**."
- **AI chat law.** The member chat ("Ask Chang Yin / Ask Sun Yoon") discloses AI at the start of every conversation and **again at least every 3 hours of continuing interaction** (New York GBL Art. 47). The crisis protocol is **published at `{{DOMAIN}}/safety`** (California SB 243), and incidents are logged for SB 243 reporting from July 2027. No therapy-style replies on grief, relationships or mental health (Illinois WOPR Act); those route to the crisis-resources line or a human.
- **SMS quiet hours:** 10:00–20:00 recipient local time, everywhere (stricter than Florida's 8am–8pm).
- **Quiz spec (one spec across OFFER, FUNNEL, BLITZ).** Paid and DM traffic get the **short Strength Age quiz** (~90 seconds: Q1–Q5 plus the chair stand T1, with "do it later" always offered). The 4-stage balance test and Q6–Q14 run in the app as the day-1 baseline. The full 14-question version below is the in-app/organic version.
- **Sources page:** `{{DOMAIN}}/how-we-make-this` (the only one; `/science` is retired).
- **Phone:** a billing phone line `{{PHONE}}` exists for questions; nobody ever needs to call to cancel.

Everything in this file is written to be pasted into the stack in OFFER.md §3: Stripe Checkout + Stripe Billing, a Next.js/Supabase/Mux members PWA, ManyChat (IG + FB Messenger), Customer.io or Klaviyo for email, Twilio 10DLC for SMS.

---

## 0. The architecture in one screen

### 0.1 What we are beating, and how

Yang Mun's machine: viral prop/food Reels → "comment HEAL" → DM → $19.99 ebook bundle or $49.99 one-time "30-Day Healing Journey" → weak Whop "Inner Circle" at $19.99–24.99/mo (35 reviews). Money is made once, on ebooks. Recurring revenue is an afterthought. Trust is borrowed from a fake 87-year-old monk, fake-looking reviewers, and remedy claims that got them exposed by the press.

Our machine inverts every one of those choices:

| Yang Mun | Chang Yin / Sun Yoon |
|---|---|
| Presented as a real 87-year-old monk with "six decades" of practice | Openly AI characters with a labelled fictional backstory, IG "AI-generated profile" label on; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: reviewed by named licensed humans] FALLBACK: "content built on published guidelines for older adults" |
| Religious costume (robes, temple) | Not clergy, never "Master". Chang, 74, a retired welder who lifts in his California garage, and Sun, 76, his blunt wife in her kitchen |
| Sells reading (294-page ebooks nobody finishes) | Sells doing: your Daily Practice, an 8–12 minute follow-along session every day, auto-levelled across four tracks |
| One-time purchase; recurring is a side door | Every front end is a door into the membership; the membership is the product |
| "Feel a shift in your calm" (unmeasurable) | Strength Age: a number you retest every month with real self-tests (chair stand, balance stages) |
| Remedy claims ("decrease blood pressure instantly") | Habits with evidence behind them (post-meal walks, protein targets, balance training), stated modestly |
| Rotating testimonials with shifting ages, AI-looking reviewer photos | Placeholder slots filled only by verified member quotes with written permission |
| "Was $38.97 / normally $99" anchors | Honest value framing: what the same help costs elsewhere, and what we are not |
| "Where should I begin?" maps pain → a book chapter to read | "Where should I begin?" maps pain → a specific 8-minute session you can do tonight, plus the test that shows it is working |

### 0.2 Offer ladder (matches OFFER.md §0 and §2)

**Baseline (non-blitz / organic) ladder.** During the launch blitz, §0.2.1 overrides it.

Every front end exists to start a Strong Years membership. No front end is a dead end.

| Step | Offer | Price | Purpose / take rate | What attaches the membership |
|---|---|---|---|---|
| Free | Strength Age Test (quiz A) | $0 | Main cold-traffic and DM entry (STRONG, TEST, BALANCE, KNEES, BACK keywords) | Result page → $1 trial |
| Free | Gut & Energy Check (quiz B) | $0 | Sun Yoon's entry (GUT, SOUP keywords) | Result page → $1 trial or $17 Kitchen |
| Free | Keyword lessons (STRONG, BACK, SLEEP, SOUP, GUT, BALANCE, KNEES, BREATH, BEGIN, TEST, FAMILY; plus JOIN in blitz mode, which goes straight to the founding checkout, §4.17) | $0 | DM lead magnets: one real follow-along session + printable card | Quiz or $1 trial |
| Front end A (default, ~50% of starts) | **7 days of Strong Years for $1** | $1, then `{{PRICE}}`/mo | Main conversion event | Trial-to-subscription, unticked consent checkbox |
| Front end B (~35%) | **7-Day Strength Reset**: 7 follow-along sessions + printable plan, *with 7 days of Strong Years included* | $7, then `{{PRICE}}`/mo | Buyers who want to own something | Continuation disclosed in the order box + unticked consent. Split-test vs. product-only + a post-purchase "add your 7 free days" button (OFFER.md 2.1) |
| Front end C (~15%) | **Sun Yoon's Strong Kitchen + Chang Yin's 12-Week Printable**, *with 7 days of Strong Years included* | $17, then `{{PRICE}}`/mo | Food-reel traffic, Sun Yoon fans | Same as B |
| Monthly event | **14-Day Strength Challenge** (cohort starts on the 1st) | $9, then `{{PRICE}}`/mo | Monthly urgency spike, re-engages past buyers | 14 days of membership included |
| Order bump | **The Wall Plan**: printable 12-week calendar + 12 weekly grocery lists | $9 | ~30% take | — |
| Upsell 1 | **One 12-week program to keep forever** (lifetime access, even after cancelling) | $27 | ~10% take | — |
| Upsell 2 | **Physical kit**: 3 resistance loops + door anchor + grip trainer | $29 | ~6% take (~$17 margin) | — |
| Downsell | Printables only | $7 | ~5% of upsell-1 decliners | — |
| Core | **Strong Years**, monthly | `{{PRICE}}`/mo (control $20; test $15 / $25) | The business | — |
| Downgrade | **Strong Years Essentials** (your Daily Practice + daily message; no AI chat, live or programs) | $12/mo (with a $9 test cell) | Cancel-flow save offer and price-sensitive winbacks | — |
| Upgrade | **Strong Years Plus** | $30/mo | Monthly 10-minute 1:1 video check-in with a human coach + small-group live. Launch month 4 | — |
| Add-on | **Couple / family** | +$8/mo | Partner with their own level and progress; family dashboard for adult children (with the parent's consent) | — |
| Annual | **Strong Years annual** | **$119/yr** (≈ $9.92/mo, about half of 12 × $20) | Offered at trial end and in day 21/45/75 campaigns, not at first checkout. $99 is a test cell only (no separate "founding annual" in standard mode; the blitz founding annual is §0.2.1) | Renews yearly; reminder before renewal |
| Gift | **Give Mom & Dad Strong Years** | 3 months $49 / 12 months $119, prepaid, **no auto-renew** | Adult children 35–55 | Recipient asked to continue with fresh consent when the gift ends |
| Later (month 7) | Supplement subscribe & save, inside the membership only | $29–45/mo | Separate profit centre, never on the front end | — |

**Pricing test cells (OFFER.md 2.4).** Monthly: $20 control vs $15 and $25, on paid traffic only (organic stays on $20 so the community sees one price). Annual, tested after monthly: **$119 control vs $99 and $149**. The $12 Essentials downgrade and the $30 Plus tier complete the $12/$15/$20/$25/$30 range. Primary metric: **net revenue per trial start at day 67** (front end + first charge + first renewal, net of refunds and chargebacks). About 1,500 trial starts per arm to detect a 5-point trial→paid difference; three arms at most at once.

### 0.2.1 Blitz mode (launch default, days 1–30+; matches OFFER.md §0.1 and the BRIEF.md BLITZ CANON; each line is flagged for client confirmation)

The $20 ladder above stays intact as the **non-blitz / organic baseline** (`OFFER_MODE=standard`). In blitz mode (`OFFER_MODE=blitz`, the app default) the ladder becomes:

| Step | Blitz-mode offer | Price | Notes |
|---|---|---|---|
| Free | Strength Age Test, Gut & Energy Check, keyword lessons | $0 | Result pages and lessons end in the visitor's assigned cell: `/join` (F25/F30) or the $1 trial checkout (T25) |
| **Primary (3 live cells from L1)** | **Founding Membership**, charged today (F25, F30), **or $1 for 7 days, then $25** (T25) | 50% founding (paid: $25 / $30 split; non-paid: $25) / 50% trial, sticky per visitor; winner by net revenue per visitor and payback at the day-10 and day-40 gates (below) | **14-day money-back guarantee** (self-serve). **Founding price locked** while subscribed. **Honest cap: first 5,000** (`FOUNDING_COHORT_CAP`, configurable); the counter reads the real database count and never resets. Checkout: `/join` (§5.6). DM keyword: JOIN (§4.17). |
| After the cap | Standard membership | `{{STANDARD_PRICE}}`: **configurable, default $35/mo** (**client decision**) | Must really be charged once the cap closes, or the "founding price" language is dropped (16 CFR 233) |
| Order bumps on `/join` | **$7 7-Day Strength Reset** · **$17 Sun Yoon's Strong Kitchen + 12-Week Printable** · $9 Wall Plan | $7 / $17 / $9 | The $7 and $17 products are bumps now, not trial front ends. `/reset` and `/kitchen` stay built but redirect to `/join` (`FRONTEND_PAGES_ENABLED=false`) |
| Upsells / downsell | $27 keep-forever program · $29 kit · $7 printables | unchanged | Founding-week bonus orders skip upsell 1 (they already get the program) |
| $1 7-day trial | **Live from L1 as cell T25** (`TRIAL_ARM_ENABLED=true`): $1 for 7 days, then $25/mo as a founding member | $1 → $25 | 50% of traffic; becomes 100% if charge-today fails the day-10 gate |
| Gift | Give Mom & Dad Strong Years | 3 months $49 / 12 months $119, prepaid, no auto-renew | **Unchanged.** Not counted in MRR |
| Annual | Founding annual | **$249/yr** (≈ 10 months at $25; AUDIT F07) | **Client decision.** Offered from **L35**, after renewal 1, not L21. Doesn't use a separate seat count |

**Launch test: three live cells from L1 (supersedes "charge-today only").** BLITZ.md's Payback sheet found the $1 trial pays back about 2× faster than charge-today on central inputs, while charge-today books MRR sooner. So blitz mode runs both from day 1:

| Cell | Offer | Paid traffic | Non-paid traffic (organic, warm, shoutouts, affiliates, email) |
|---|---|---|---|
| **F25** | Founding membership, first month **charged today**, $25/mo | 25% | 50% |
| **F30** | Founding membership, first month **charged today**, $30/mo | 25% | — (partners and the community see one founding price) |
| **T25** | **$1 for 7 days, then $25/mo** as a founding member (the seat is taken, and the price locked, when the first full charge succeeds while the cohort is open) | 50% | 50% |

- **Split:** 50% founding / 50% trial, **sticky per visitor** (cookie + email; `ARM_B_SHARE=0.5`, `TRIAL_ARM_ENABLED=true`, `BLITZ_PRICE_CELLS=2500,3000`, `TRIAL_THEN_PRICE_CENTS=2500`). Emails and DMs render `{{OFFER_TERMS}}` for the recipient's assigned cell, so nobody ever sees two offers.
- **Same everywhere:** 14-day money-back guarantee on the first membership charge (one per person; T25 also refunds the $1), the add-on terms, the 5,000 / `{{FOUNDING_CLOSE_DATE}}` cap, the `{{COUNT_LINE}}` rule. T25 gets the 48-hour pre-charge reminder (email until SMS is live).
- **$25 vs $30** is still read inside the founding cells (L5 provisional, L14 confirmed on refund-adjusted data); if $25 wins, F30 members move down, never up.
- **Winner between charge-today and trial:** net revenue per visitor (all revenue to date net of refunds and chargebacks ÷ visitors assigned to the cell) plus payback at the **BLITZ.md §11 gates**:
  - **Day-10 gate** (L10, or when charge-today reaches **≥ 300 purchases**, whichever is later; latest L14): charge-today stays at 50% and Meta steps to **$4K/day** only if **(1)** blended paid media per net paying member at ≥ $4K/day for 5 days (or its projection at the current spend) is **≤ $111 at $25 / ≤ $132 at $30**, and **(2)** the charge-today factor (arm-B purchase rate ÷ trial-start rate) is **≥ 0.64 at $25 / ≥ 0.57 at $30** at central media costs (**2b:** ≥ 0.48 / ≥ 0.43 if live media costs match the upside). Otherwise charge-today drops to 0% and the launch stays on the R17 plan (the $1 trial, Meta ~$1.5K/day + 4 shoutouts).
  - **Day-40 gate** (renewal 1 of the L1–L10 charge-today cohorts, read L31–L40): if **(3)** renewal-1 survival is **≥ 58%** (and refunds ≤ 12%, chargebacks < 0.35%), go to full R4 ($8K/day, 100% charge-today at the winning price). If renewal 1 is **below 50%**, drop back to R17 whatever (1)–(2) show. Between 50% and 58%: hold the day-10 configuration.
- **Why not pick now:** charge-today wins the MRR-speed milestones; the trial wins payback and cash. The live factor and renewal 1 are the two unknowns, and only the gates measure them.

**Messaging in blitz mode.** Launch runs on **email + DM**. 10DLC / toll-free SMS verification takes **3–6 weeks**, so SMS stays off (`SMS_ENABLED=false`) until approved, and every "we'll email and text you" line in this file reads "we'll email you" until then. The 48-hour pre-charge reminder (trial arm, if switched on) and the founding members' renewal reminders (7 and 2 days before the first renewal, 3 days before every later renewal) go **by email** until SMS is live.

**Refund copy in blitz mode.** Every mode uses the **14-day money-back guarantee on the membership charge, one per person** (the old 30-day standard-mode guarantee is retired). "Guarantee" appears only in "14-day money-back guarantee" / "money-back guarantee" describing the refund policy, never next to a health outcome.

### 0.3 What the member actually gets (the product the copy sells; matches OFFER.md 1.2)

Write no copy promising anything not on this list.

1. **Your Daily Practice**: one new 8–12 minute follow-along session with Chang Yin every day, auto-levelled across four tracks: **Rebuild** (chair-based, fully seated or holding a counter), **Steady** (standing, counter nearby), **Strong** (bands, water jugs) and **Iron** (heavier loads, for the already-strong). A "sore knee / sore back / low energy today" button swaps in a modified version. Weekly rhythm: Mon strength, Tue mobility, Wed balance, Thu strength, Fri breath + qigong flow, Sat walk-and-talk, Sun rest + stretch.
2. **12-week programs** (one active at a time, week number on the dashboard): *Strong at 70*, *Back Strong* ("move with less stiffness", never "fix back pain"), *Balance & Steady Feet* (Otago-style progressions + tai chi), *Gut Reset with Sun Yoon*, *Grip & Hands*, *Walk Stronger*.
3. **Focus tracks** (short on-demand libraries used by the "Where should I begin?" block): Knees & Stairs, Back & Posture, Steady Feet, Hands & Grip, Sleep Wind-Down, Breath & Calm, Walking Stronger, After-Meal Movement.
4. **Strength Age retest, monthly**: the 30-second chair stand and 4-stage balance test (the two that set the Strength Age number, same as the quiz), plus the 2-minute step test, arm curl, sit-and-reach and timed up-and-go. Charted over time. A fitness estimate, not a medical assessment.
5. **Sun Yoon's Kitchen**: every Sunday, 3 recipes + a printable grocery list + one "remedy" with an honest evidence grade (*good evidence / some evidence / tradition only, enjoy it as food*). Protein target per meal. Soft-food versions.
6. **Daily coach message**: SMS by default (email or WhatsApp by choice), 1–2 lines + today's link, signed "— Chang Yin (AI coach)". A Sunday message from Sun Yoon.
7. **Ask Chang Yin / Ask Sun Yoon** (AI chat): text + optional voice notes, opt-in memory, persistent AI disclosure, crisis protocol and scope limits exactly as OFFER.md 1.4.
8. **Streaks with grace days and milestones**: badges at 7/30/100 sessions; a printed certificate mailed at 100 sessions.
9. **The Courtyard** (community): prompt-based feed, human moderators, no open DMs between members.
10. **Sunday Premiere + Wednesday Live Q&A**: a 20-minute pre-recorded Sunday episode with live chat, and a 30-minute Wednesday live where a real human coach answers questions, introduced as a human. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: The Wednesday host is `[PT NAME]`, PT, DPT (or a named CSCS).] FALLBACK: "Wednesday Live Q&A with a real human coach from our team."
11. **Printables**: weekly plan, grocery list, large-print exercise cards, a fridge Strength Age chart.
12. **Couple / family add-on** (+$8/mo) and **gifting** (prepaid, no auto-renew; the gifter gets a monthly "Mom did 18 sessions" email only if the parent consents).

Demonstration accuracy rule: [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: every movement shown is reviewed frame by frame by the PT.] FALLBACK: "every movement shown is checked by our team against published exercise guidance before it is published." Where AI video cannot show a joint position accurately (knee tracking, spine position, hand placement on a chair), the session uses a real, credited human demonstrator in a picture-in-picture inset (CHARACTERS.md uses neighbour Frank, 79, for easier versions; a real demonstrator is used whenever form accuracy matters). Say so on the page.

### 0.4 Character, heritage and disclosure standard (applies to every asset below)

**Heritage (matches CHARACTERS.md §3; all backstory is fiction and labelled as fiction).**
- **Chang Yin, 74**, is a retired welder and **hwagyo**: ethnic Chinese, born and raised in **Incheon's Chinatown** in Korea (grandfather from Shandong). **Sun Yoon, 76**, is Korean, from Incheon; she ran a lunch counter for decades. They married in 1976 (50th anniversary in 2026) and have lived in **Northern California since 1983**. A Chinese man raised in Korea marrying a Korean woman is completely natural, which is how the two names sit together without looking careless.
- Names: Sun kept her family name, Yoon, as Korean women traditionally do; that's why she's "Sun Yoon" and not "Mrs. Chang". Fans call him "Chang" or "Coach Chang". **Never "Master"**, never monk, doctor, therapist or healer.
- His lane: modern progressive strength training ("Measure twice. Lift once.") plus Chinese movement practices (tai chi, qigong, baduanjin) taught as movement, not spirituality. Her lane: Korean home cooking (doenjang jjigae, miyeok-guk, kimchi, boricha barley tea, japgokbap mixed-grain rice) plus Korean-Chinese and Chinese family dishes (jajangmyeon on Sundays, congee, steamed fish, ginger soup).
- Paid, credited cultural reviewers: one Korean-American and one Chinese-American (ideally hwagyo-descended) consultant for backstory, names, food, set dressing and captions. No robes, temples, prayer beads, Buddhist iconography or "ancient secret" framing. Voices: warm, clear English with a light accent, never played for comedy.
- Label the story: "Chang Yin and Sun Yoon are AI characters. Their story is invented; the practices are real." Never present decades of teaching, credentials or any life event as fact, and never use the backstory as evidence of a health outcome.

**Disclosure block (use verbatim or near-verbatim everywhere):**
> Chang Yin and Sun Yoon are AI characters created by our team. They are not real people and they are not doctors. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Every session and recipe is reviewed by `[PT NAME], PT, DPT` and `[RD NAME], RDN` before it is published.] FALLBACK: "Sessions and recipes are written by our team from published exercise and nutrition guidelines for older adults." This is general fitness and nutrition education, not medical advice. Talk to your doctor before starting a new exercise program, especially if you have a heart condition, recent surgery, a recent fall, dizziness, or take blood-thinning medication.

Placement: page header strip on every landing page (not only footer), first DM message, email footer, SMS opt-in confirmation, checkout page above the pay button, in-app profile screen, IG/TikTok/YouTube bios.

**Testimonial rule.** No invented quotes, no composite quotes, no AI faces, no stock faces with quotes. Slots below look like `[REAL MEMBER QUOTE: …]`. Each filled slot needs: written permission (captured in the review flow, Section 7.10), the member's real first name + last initial, age only if they chose to share it, "Member since [month year]", a note if they received anything of value for the review ("received a free month"), and a typicality statement where results are mentioned ("Results vary. Most members report [X] after [Y] weeks" only when you have the data from your own retests).

**Claims rule.** We describe what a practice is, what it trains, and what research generally shows, with modest language: "can help", "trains", "research in older adults links X with Y". Never: cure, treat, reverse, heal (as a verb applied to disease), "instantly", "lower your blood pressure", "fix arthritis", "reverse diabetes", "melt fat". Sun Yoon's remedies are comfort and kitchen traditions, labelled "kitchen tradition, not a treatment" when there is no evidence behind a health effect.

### 0.5 Compliance baseline for money flows

- **ROSCA** (federal): before taking billing info, clearly disclose all material terms (price after trial, billing frequency, that it renews until cancelled, how to cancel); get **express informed consent** (unchecked checkbox or a button whose label states the charge); provide a **simple cancel method** at least as easy as signing up (online, self-serve).
- **FTC Negative Option Rule "click-to-cancel" amendments** were vacated by the 8th Circuit in July 2025; do not rely on that. ROSCA and state automatic-renewal laws still apply, so build to the strictest states: **California ARL (incl. AB 2863, effective July 2025)**, **Minnesota (2025)**, **New York**, Colorado, Virginia and others. Practically: online cancel with no call/chat requirement; at most one save offer, shown only with an equally prominent "Finish canceling" button; confirmation email of cancellation; annual-plan renewal notice 15–45 days before renewal; notice before a trial or promotional price converts; consent records kept (timestamp, IP, the exact disclosure text shown, the checkbox state).
- **Card-network trial rules** (Visa/Mastercard for digital trials): email the terms at signup with a cancel link; send a reminder before the first full charge; use a recognizable billing descriptor, e.g. `STRONGYEARS MEMBER` with support URL (OFFER.md 2.3).
- **TCPA / SMS**: separate, unchecked SMS consent with the required language; 10DLC registration; STOP/HELP; quiet hours 10:00–20:00 recipient local time (Florida's FTSA allows 8am–8pm; we run tighter everywhere); never make SMS consent a condition of purchase.
- **CAN-SPAM**: physical address, one-click unsubscribe, honest subject lines.
- **FTC health claims**: competent and reliable scientific evidence for any health benefit claim. Our copy stays at the level of "trains leg strength", "practice for balance", "a habit research links to steadier blood sugar after meals".
- **FTC fake reviews rule (2024)**: no fake, AI-generated or purchased reviews; no review suppression; no insider reviews without disclosure.
- **AI and chatbots**: disclose AI on every DM/chat surface; crisis protocol (Section 4.14), published at `{{DOMAIN}}/safety`. The member chat is a companion chatbot: California SB 243 (disclosure, published crisis protocol, incident log, annual reports from July 2027) and New York GBL Art. 47 (AI notice at the start and at least every 3 hours of continuing interaction). Illinois bars AI therapy, so grief and relationship topics route to resources or a human. Our DM bot is a transactional assistant; it meets the same standard anyway.
- **Auto-renewal notices**: a reminder email before every renewal charge; California's annual reminder to every auto-renewing member (monthly included); price-change notice exactly 30 days before. A 50-state ARL matrix from counsel (CA, NY GBL §527-a, MN, VA, CO) lives in `legal_pack`.
- Have a US consumer-protection attorney review checkout, trial and cancel flows before launch. Budget: $10–25K for launch (checkout, terms of service, privacy and consumer-health-data policies, the three contracts in TEMPLATES/, cross-brand sends and a 50-state auto-renewal matrix). It is cheaper than one state AG letter.

---

## 1. Funnel maps by entry path

Common spine for every path:

```
Attention (Reel / Short / ad)
  → Micro-commitment (comment keyword, DM, tap bio link, click ad)
    → Free value delivered on OUR domain (follow-along lesson page or quiz), pixel + email captured
      → Personalized result or lesson ends in ONE primary offer ($1 trial) + one fallback ($7 or $17)
        → Checkout (bumps) → one-click upsell ladder
          → Onboarding (email + SMS + in-app 72-hour checklist)
            → Retention system (daily session, weekly ritual, monthly Strength Age retest)
```

Tracking naming rule (important for Meta's health-and-wellness data restrictions, see ADS.md Section 7): URLs, page titles in the pixel payload, event names and custom parameters must not contain health conditions. Use `/s/ln1` not `/knee-pain-lesson`; `quiz_a_complete` not `bad_knees_quiz`. Keep the readable slug for organic SEO pages only, and do not fire the Meta pixel on those.

UTM convention: `utm_source={ig|fb|tt|yt|meta}&utm_medium={organic|dm|bio|paid}&utm_campaign={keyword or campaign id}&utm_content={post id or ad id}`. ManyChat passes `{{user_id}}` as `mc_id` so DM subscribers can be matched to purchases.

### 1.1 Instagram: comment keyword → DM → lesson/quiz → offer (the primary organic engine)

```
Reel ends: "Comment STRONG and I'll send you the full 8-minute routine."
  → ManyChat Comment trigger (keyword list incl. misspellings + emoji variants)
     → Public reply (5 rotating variants, no links in public reply)
     → Opening DM (AI disclosure + button "Send it") — button tap opens the 24h window
        → DM 2: lesson link {{DOMAIN}}/s/l{n}?mc_id=… (free follow-along video + printable card)
           + Quick reply: "Also email me the printable card" → email capture in DM (IG autofill)
        → +20 min if link not clicked: nudge
        → +22 h (inside 24h window): "Did you try it? How did your legs feel?" (3 buttons)
             → "Easy" → Strength Age Test link
             → "Hard" → Chair version link + Strength Age Test
             → "Didn't try yet" → 3-minute version link
  Lesson page → sticky CTA "Find your Strength Age (free, 3 min)" → quiz → result → $1 trial
  Email (if captured) → Keyword nurture sequence (3 emails) → joins main onboarding pre-purchase flow
```

Targets (assumptions, validate in week 1): comment→DM button tap 55–70%; DM→link click 45–60%; lesson page→quiz start 30–40%; quiz completion 60–70%; email capture at quiz 55–65%; quiz→$1 trial 8–14%. So roughly **1.2–2.5 trials per 100 keyword comments**. A Reel with 10K keyword comments (Yang Mun's onion video had 10.3K comments) ≈ 120–250 trials.

Posting rules to feed this path: every keyword Reel's on-screen text, caption line 1, and spoken last line all say the same keyword. Caption line 1: "Comment STRONG for the full routine." Pin a comment from the account that repeats the keyword. One keyword per Reel. Rotate the 12 keywords (Section 4: STRONG, BACK, SLEEP, SOUP, GUT, BALANCE, KNEES, BREATH, BEGIN, TEST, FAMILY, plus JOIN while blitz mode is on) across the 6–9 daily posts so each keyword appears at least daily on each page.

### 1.2 Instagram / Facebook bio link → landing

Bio text (IG, 150 chars): [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `Chang Yin & Sun Yoon · AI characters · PT-reviewed strength, balance & food for 55+ · Free Strength Age test ⬇️`] FALLBACK: "Chang Yin & Sun Yoon · AI characters · Strength, balance & food for 55+ · Free Strength Age test ⬇️"
Link: `{{DOMAIN}}/go` (own domain, not Linktree; fires pixel; carries `utm_source=ig&utm_medium=bio`).

`/go` page (mobile, one screen, no scroll needed for the first two buttons):
1. Character photo (both of them, kitchen table), line: "Hello. We are AI characters. The practices are real." + [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "Reviewed by a physical therapist."] FALLBACK: "(no review line)"
2. Button 1 (persimmon, full width): **Find my Strength Age — free, 3 minutes**
3. Button 2 (ink): **Try Strong Years — 7 days for $1**
4. Button 3 (outline, ink text): **Sun Yoon's Strong Kitchen — $17**
5. Button 4 (outline): **Give Mom & Dad Strong Years** → gift page
6. Small row: "Today's free session" (rotates daily; links to that day's lesson page).
7. Disclosure line (full contrast, not muted).

Expected split (assumption): 55% quiz, 20% trial page, 10% kitchen, 8% gift, 7% free session.

### 1.3 TikTok (no US comment triggers) → bio / DM

TikTok's comment-to-DM automation is not available for US accounts, so the path relies on bio link, pinned comments, and TikTok business-account DM keyword auto-replies (verify availability in the account's Business Suite; roll out if present).

```
Video ends: "The test is free. Tap my profile, first link." (spoken + on-screen)
  → Pinned comment from account: "Strength Age test is the link in our profile. It takes 3 minutes. 🔗"
  → Profile bio: "AI characters · Free Strength Age test ⬇️" ([ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: add "PT-reviewed"] FALLBACK: "no review wording in the bio") + link {{DOMAIN}}/tt
  → Alternate CTA on 1 in 3 videos: "Send me the word STRONG in a message."
      → TikTok DM keyword auto-reply: disclosure + link {{DOMAIN}}/s/l1?utm_source=tt&utm_medium=dm
  → Same lesson → quiz → offer spine
```

TikTok specifics:
- Label every video with TikTok's AI-generated content toggle; keep "AI character" in the bio. Unlabelled realistic AI is excluded from For You; labelled content keeps distribution.
- Avoid the "unoriginal" demonetization pattern: each post must have original scripting, a real teaching point, and varied scenes; never re-upload IG Reels with watermarks.
- `/tt` landing is the quiz start page directly (TikTok users bounce on multi-button pages); one button.
- If the bio link is unavailable on the account (TikTok applies follower thresholds to some account types), put `{{DOMAIN}}` as plain, speakable text on the final frame ("strongyears dot com"), say it aloud, and use the DM keyword auto-reply as the clickable route. Choose a domain that is easy to say and spell for exactly this reason.

### 1.4 YouTube → description / pinned comment

Shorts cannot carry clickable links in descriptions or comments. So:
```
Short → "Related video" set to a long-form session (e.g. "15-Minute Strength Session for Over 60s, Follow Along")
  → Long-form video: chapter 0:00 disclosure card (5 sec), then the full session
     → Description line 1: "Free Strength Age test: {{DOMAIN}}/yt?v=[videoID]"
     → Pinned comment (clickable on long-form): same link + "Tell me your chair-stand number below"
     → Verbal CTA at the natural pause (after the warm-up, around 2:00) and at the end
     → End screen: the next session in the playlist + subscribe
  → Quiz → offer spine
```

YouTube specifics: tick "altered or synthetic content" disclosure. The July 2026 "inauthentic content" policy targets templated mass production and AI personas posing as credentialed experts, so: never call Chang Yin a doctor, therapist or "Master" (he's a retired welder who trains); in each description, [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: name the real reviewer ("Reviewed by [PT NAME], PT, DPT")] FALLBACK: "Built by our team on published exercise guidelines for older adults."; make long-form sessions genuinely distinct (different routines, cues, levels). Long-form follow-along sessions are the YouTube format that converts for this audience because the viewer has already done the thing and felt it.

### 1.5 Paid (Meta) → quiz

```
Ad (character UGC-style, follow-along clip, quiz ad, strength test demo)
  → {{DOMAIN}}/q/a (Strength Age quiz) or /q/b (Gut & Energy) — no navigation, one CTA
     → Result page (personalized) → $1 trial checkout (bumps) → upsells → onboarding
  → Secondary ad set: → /r7 ($7 Strength Reset direct sales page) for buyers who resist subscriptions
  → Adult-child ad set: → /gift (gift page with "Give 3 months" as the lead and "Take the test together" as the soft option)
Retargeting (small budget; Advantage+ usually covers):
  quiz started not finished → "Your result is 2 questions away"
  quiz finished no purchase → result-specific ad (their profile's plan)
  trial started, not converted on day 5 → nothing (email/SMS handle it; do not pay to remind customers)
```

Full structure, creatives and KPIs are in ADS.md.

### 1.6 Email and SMS as the connective tissue

- Any captured email not yet a buyer → **Pre-purchase nurture** (7 emails over 10 days; reuse onboarding emails 1–3 copy adapted, plus result-specific emails built from the profile copy in Section 3).
- $7/$17 buyers in the product-only split-test arm who didn't add their 7 free days → **Buyer-to-member bridge** (emails on Reset days 5, 6, 7 and 9, see Section 6.6). Control-arm buyers already have 7 days of membership and follow onboarding.
- Trial and members → **Onboarding** (Section 6) → **Retention** (Section 7).

### 1.7 Path-level economics snapshot (assumptions, labelled)

| Path | Cost per trial start (assumption) | Trial→paid (assumption) | Notes |
|---|---|---|---|
| IG keyword DM | Content cost only (~$0.60/post in the model + ManyChat) | 48% (model base for organic); goal 50%+ | Highest intent; they already did a session |
| Bio link | Content only | 45–55% | |
| TikTok | Content only | 35–45% | Younger-skewing; more adult children |
| YouTube long-form | Content only | 55–65% | Followed a full session first |
| Meta paid → quiz | $33.81 base cost per paid trial start (ECONOMICS.md; ~$24 once 30-day nurture is counted) | 42% (model base for paid) | Scale ≤ $26, hold ≤ $40, kill > $58 |
| Meta paid → $7 Reset (membership included) | Tested head-to-head with the $1 trial on paid traffic | 42% base | Front-end revenue per start ~$12.99 across paths (not self-liquidating) |

The model (ECONOMICS.md) uses 42% trial→paid for paid traffic and 48% for organic, against the 42.2% health-and-fitness benchmark; the goal is 50%+. The other organic rows are directional assumptions to validate.

---

## 2. Main offer landing page: `{{DOMAIN}}/start`

Role: the page every non-quiz click lands on (bio button 2, email CTAs, retargeting, YouTube description alt link). Quiz result pages reuse sections 2.6 through 2.16 below the personalized result. Primary action on the whole page: **Start 7 days for $1**. One secondary path, placed low: "Other ways to start".

### 2.1 Visual direction (applies to every page in this system)

**Palette (all text pairs pass WCAG AA at body size; most pass AAA):**
| Token | Hex | Use |
|---|---|---|
| Paper | `#FBF6EC` | Page background (warm, not clinical white) |
| Ink | `#16120E` | All body text, all headings. There is no secondary text color |
| Persimmon | `#B3311C` | Primary buttons (white text on it, contrast ≈ 5.9:1), key numbers |
| Jade | `#1F5A46` | Secondary buttons and Strength Age chart line (white text ≈ 7.9:1) |
| Rice | `#FFFFFF` | Cards on paper, button text |
| Brass | `#E7B85A` | Thin highlight bars behind numbers, never text color |

No gray text anywhere: captions, fine print, disclosures, placeholder text in forms and disabled states all use Ink. Fine print is smaller (17px), never lighter. Disabled buttons show a label change ("Choose a level first") rather than a faded color.

**Type:** Headings in **Fraunces** (soft serif, 600 weight, optical size on), body and UI in **Atkinson Hyperlegible** (designed by the Braille Institute for low-vision readers; ideal for 55–75). Body 20px mobile / 21px desktop, line height 1.55, max line length 62 characters. H1 40px mobile / 60px desktop. Buttons 20px bold, minimum 60px tall, full-width on mobile, radius 14px, with a 3px Ink outline on focus.

**Layout and imagery rules:**
- Product-led: every section above the fold shows the actual product. Hero shows a real phone frame playing the day's session (Chang Yin mid-movement, captions on, track switch visible: Rebuild / Steady / Strong / Iron) beside a printed Strength Age card on the kitchen table.
- Characters appear in real contexts: Chang Yin in a sunlit garage gym with a sturdy kitchen chair, resistance bands and two water jugs; Sun Yoon at a stove with steam, onggi pots, a cutting board. Warm natural light, handheld-camera framing like their Reels.
- No robes, no temples, no incense, no mandalas, no gold "ancient" textures.
- Section headings are plain sentences. No numbered kicker labels above headings, no slash decorations, no all-caps tracked eyebrow text, no monospace anything.
- Screenshots over icons. Where an icon is needed, use a small photograph of the real object (a chair, a band, a bowl).
- Sticky bottom bar on mobile after the hero scrolls away: "7 days for $1" button + "Cancel online anytime" line, Ink on Rice.
- Accessibility: all video captioned by default; tap targets ≥ 48px; no auto-playing sound; no carousels that move on their own; respects reduced-motion.
- Speed: LCP under 2.0s on 4G; hero video is a 6-second muted loop (WebM/MP4, < 900KB) with poster image.

### 2.2 Section 0: disclosure strip (top of page, full width, Ink background, Rice text)

> Chang Yin and Sun Yoon are AI characters. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Every session is reviewed by a licensed physical therapist.] FALLBACK: "Every session is built on published exercise guidelines for older adults." [How we make this →]

### 2.3 Section 1: Hero

**Headline (test A, default):**
# Get stronger after 60. Eight minutes a day, and a number that shows your progress.

**Headline (test B):**
# Stand up from a chair, carry your groceries, climb the stairs. Train for the life you actually live.

**Headline (test C):**
# Your legs are the most important muscles you own. Let's make them stronger than last month.

**Subhead:**
Strong Years gives you your Daily Practice: one 8–12 minute follow-along session a day with Chang Yin, strength, balance and mobility, with a chair-based version of everything. Plus Sun Yoon's simple high-protein recipes every Sunday and a Strength Age retest every month, so you can see the change for yourself.

**Primary button:** Start 7 days for $1
**Microcopy under button (Ink, 17px):** Then {{PRICE}}/month. Renews monthly until you cancel. Cancel online in two screens at most, anytime.

**Trust row (4 items, photo icons):**
- [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by `[PT NAME], PT, DPT`] FALLBACK: "Built on published guidelines for older adults"
- A chair-based version of every session
- Big captions, big buttons, works on TV
- Cancel online anytime, no phone call

**Hero visual:** phone frame with the session playing (6s loop: Chang Yin doing a slow sit-to-stand with arms crossed, "Rep 6 of 10" on screen, track reading "Steady"), and a printed Strength Age card with the axis only and "Your number here" (no example trend line: hypothetical progress implies typical results, FTC Endorsement Guides §255.2). Never show a real member's numbers without permission.

### 2.4 Section 2: "Hello. We are AI characters." (the candor block, directly under the hero)

**Heading:** Yes, we are AI. Here is why that is good news for you.

**Body:**
Chang Yin and Sun Yoon are characters our team created with AI. We tell you this up front because you deserve to know who you are learning from, and because some accounts online pretend their AI teachers are real. We never will.

What is real: the movements, the progressions, the recipes and the safety checks. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Every session is written with and reviewed by `[PT NAME]`, a licensed physical therapist with `[X]` years working with older adults. Every recipe is checked by `[RD NAME]`, a registered dietitian.] FALLBACK: "Every session and recipe is built by our team from published exercise and nutrition guidelines for older adults, and we show our sources." When an AI video can't show a movement precisely enough, a real coach demonstrates it on screen.

Why characters at all? Because a patient teacher who never rushes you, shows up every single morning, and speaks slowly and clearly is exactly what most programs are missing. Chang Yin can do that 365 days a year. And on Wednesdays, a real human coach answers your questions live.

**Link (Jade, underlined):** Read exactly how we make each session →

### 2.5 Section 3: The honest problem

**Heading:** Strength doesn't leave all at once. It leaves one chair, one stair, one jar lid at a time.

**Body:**
Starting around age 30, most people lose muscle every decade, and the loss speeds up after 60. Leg power, the ability to move quickly, fades even faster than strength. That is why the first signs are small: pushing on the armrests to stand up, holding the rail on the stairs, asking someone else to open the jar.

Most people are never told the simple part: legs and balance respond to practice at any age. A little, often. Balance in particular is one of the most trainable things there is, and it often improves faster than strength.

**Heading (same section, second beat):** The good news is the part nobody says loudly enough.

**Body:**
Muscle still responds at 60, 70, 80 and beyond. In a well-known study, adults in their nineties who did supervised leg strength training for eight weeks more than doubled their leg strength. You do not need a gym. You need the right movements, in the right order, done most days, and a way to see it working.

**Bullets (large, Ink, with a small persimmon square marker):**
- Leg strength: standing up, getting off the floor, climbing stairs
- Balance: steadier on uneven ground, in the shower, in the dark
- Grip and upper body: jars, bags, grandchildren, suitcases
- Mobility and breath: turning to look behind you, reaching the top shelf, falling asleep calmer

Footnote line (Ink, 17px): Sources listed at `{{DOMAIN}}/how-we-make-this`: Rikli & Jones Senior Fitness Test norms (the chair stand and balance positions used in the Strength Age test); Fiatarone et al., JAMA 1990 (strength training in adults in their nineties).

### 2.6 Section 4: What makes this different (the mechanism)

**Heading:** Three things every other program for "seniors" gets wrong, and how we do it instead.

**Three cards (photo on top, heading, body):**

**Card 1: Too gentle to change anything → Real strength, started gently**
Chair yoga alone won't make your legs stronger. Muscle needs a challenge. Every session has a strength part, and every week it gets a little harder, only when you are ready.

**Card 2: One level for everyone → Four tracks that level with you**
Your Daily Practice is set to Rebuild (chair-based), Steady, Strong or Iron, and moves you up when the reps get easy. Sore knee, sore back or low energy today? One button swaps in a modified version.

**Card 3: No way to know if it's working → A number you retest every month**
Once a month, Chang Yin walks you through the Strength Age retest: how many times you can stand from a chair in 30 seconds, how long you can hold four balance positions, and four more simple at-home tests. Your number goes on your chart. Most people have never seen their strength measured. You will, every month.

### 2.7 Section 5: A day inside Strong Years (product walkthrough)

**Heading:** Here is what tomorrow morning looks like.

**Four screenshots in a vertical stack on mobile, with a caption under each:**
1. **7:30 am, a text from Chang Yin (AI coach), at the time you chose:** "Morning, [First name]. Today: strength, 9 minutes. [link] — Chang Yin (AI coach)" One tap and your Daily Practice opens at your level. No passwords to remember.
2. **The session:** Chang Yin counts every rep with you. Big captions. A timer you can see across the room. A pause button the size of a coaster.
3. **Done:** A check mark on your calendar and your streak (with grace days, because life happens). Your 12-week program shows "Week 3 of 12".
4. **Wednesday:** a real human coach answers member questions live for 30 minutes.
5. **Sunday:** Sun Yoon's three recipes and grocery list, and her message. Short, warm, and honest. She tells you when you skipped your walk.

**Button:** Start 7 days for $1

### 2.8 Section 6: "Where should I begin?" (the pain → session block that beats Yang Mun's chapter map)

**Heading:** Where should I begin?
**Subhead:** Tap the sentence that sounds most like you. We'll show you the exact session to do tonight, and how you'll know it's helping.

Eight tap-to-expand tiles in a 2-column grid (1 column on small phones). Each tile: a quote in Fraunces italic (their words), and when opened: the session, its length, the level to start at, and "How you'll know". Each has a small "Preview 30 seconds" video link.

| They say | Start with | Length | How you'll know it's working |
|---|---|---|---|
| "I push on the armrests to stand up." | **The Chair Builder** (Legs, Day 1) | 9 min | Your 30-second chair-stand count at the next monthly retest |
| "My knees complain on the stairs." | **Knees & Stairs, Session 1: The Step Builder** (partial-range step-ups at the bottom stair, holding the rail) | 10 min | Count the stairs you can climb without pulling on the rail |
| "I don't feel steady on my feet." | **Steady Feet, Session 1** (counter-supported balance ladder) | 8 min | How long you hold the tandem stance at your retest (goal: 10 seconds) |
| "My back is stiff every morning." | **Morning Unlock** (bed-to-standing mobility; cat-cow on the bed, hip hinges at the counter) | 7 min | How far you can turn to look behind you, and how many minutes of morning stiffness |
| "I can't open jars anymore." | **Hands & Grip, Session 1** (towel wrings, water-jug carries, finger spreads with a rubber band) | 8 min | Carry test: how long you can carry two full water jugs at your retest |
| "I lie awake with my mind racing." | **Sleep Wind-Down, Night 1** (slow exhale breathing, 4 seconds in, 6 out, plus gentle neck and hip release) | 10 min | Your own sleep log in the app: minutes to fall asleep, nights you woke rested |
| "I'm tired by 2 in the afternoon." | **After-Meal Walk + Sun Yoon's Protein Breakfast** (10-minute walk after your biggest meal; 25–30g protein breakfast) | 10 min | Your afternoon energy score, 1 to 5, logged for 14 days |
| "I haven't exercised in years, I don't know where to start." | **Day 1: The Gentle Start** (fully seated, Rebuild track) | 8 min | Finishing 3 sessions this week. That is the whole goal |

Under the grid, one line and button: "Not sure? The free Strength Age Test picks for you." **[Find my Strength Age (free)]** (Jade button; this is the only place on the page the quiz is offered, so the trial stays primary.)

Why this beats their block: theirs sends a tired, anxious person to read chapter 16 of a 294-page book. Ours gives them one short thing to do tonight and a way to see it working, which is the moment people decide to stay.

### 2.9 Section 7: Strength Age explained

**Heading:** What's your Strength Age?

**Body:**
Your birthday gives you one age. Your legs and your balance give you another. Strength Age compares your results on two well-known tests, the 30-second chair stand and the 4-stage balance test (both standard fitness tests used in senior fitness research), with typical results for men and women at each age.

If you stand up more times than is typical for your age, your Strength Age is younger. If fewer, it's older. Either way, it's a starting line, not a verdict, and you retest every month.

**Visual:** an empty chart (axis, month labels and "Your number here"), no example line. Under it (Ink, 17px): "Strength Age is a motivational estimate based on published fitness norms. It is not a medical test or diagnosis."

**Button:** Find my Strength Age (free, 3 minutes)

### 2.10 Section 8: Meet Chang Yin and Sun Yoon

**Heading:** Meet the two of them.

Two portraits side by side (real product stills from their videos).

**Chang Yin** (caption)
Chang Yin is 74, a retired welder who has trained in his California garage every morning for fourteen years, and he'd like you to join him. He grew up in the Chinese community of Incheon, Korea, and blends modern strength training with the slow, careful Chinese movement practices of tai chi, qigong and baduanjin. "Measure twice. Lift once." He counts every rep with you and never rushes.

**Sun Yoon** (caption)
Sun Yoon is his wife. She's 76, two years older, which she says makes her right. She's Korean, from Incheon, ran a lunch counter in California for decades, and is honest to a fault. She cooks cheap, high-protein, easy-to-chew food from both of their families: doenjang stew, seaweed soup, jajangmyeon on Sundays, congee, steamed fish, barley tea. She'll tell you your breakfast is too small. She's usually right.

**Small note (Ink, 17px):** Korean women traditionally keep their own family name when they marry. That's why she's Sun Yoon, not "Mrs. Chang." She will remind you.

**Disclosure (full contrast box, Rice card with Ink border):**
Chang Yin and Sun Yoon are AI characters, and their life story is made up. They are not real people, not doctors, and not religious teachers. The practices and recipes are real. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Each one is reviewed by the licensed professionals below.] FALLBACK: "Each one is built from published guidelines for older adults."

### 2.11 Section 9: The real humans behind every session

[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: this entire section.] FALLBACK: omit Section 2.11 entirely and replace it with a one-line "How we make this" link to a page listing the published guidelines each session and recipe is built on (CDC STEADI, ACSM older-adult exercise guidance, PROT-AGE protein recommendations, dietary fiber guidance).

**Heading:** The people who check every session before you see it.

Three real photos with real names (only with signed contracts and written consent to be named):
- **`[PT NAME]`, PT, DPT**, physical therapist, `[board certification e.g. Geriatric Clinical Specialist]`, `[X]` years with older adults. Writes the progressions and approves every movement.
- **`[RD NAME]`, RDN**, registered dietitian. Checks every recipe for protein, fiber, sodium and texture options.
- **`[MD NAME]`, MD**, medical advisor, `[specialty]`. Reviews our safety screening and "when to call your doctor" guidance.

Line under: "One of them hosts the Wednesday Live Q&A. Real people, on camera, by name."

### 2.12 Section 10: What's included (value stack, honest framing)

**Heading:** Everything you get for $1 this week.

A single Rice card with Ink text, each line with a photo thumbnail:

- **Your Daily Practice**: a new 8–12 minute follow-along session every day, auto-levelled (Rebuild, Steady, Strong, Iron), with a "sore knee / sore back / low energy today" button
- **Six 12-week programs**: Strong at 70, Back Strong, Balance & Steady Feet, Gut Reset with Sun Yoon, Grip & Hands, Walk Stronger
- **The monthly Strength Age retest** with your personal chart
- **Sun Yoon's Kitchen:** 3 recipes every Sunday, a grocery list, and one remedy with an honest evidence grade
- **A daily message from Chang Yin (AI coach)** at the time you choose
- **Ask Chang Yin / Ask Sun Yoon**: an AI coach chat that adapts exercises and recipes to you
- **Wednesday Live Q&A** with a real human coach, and a Sunday Premiere episode
- **Large-print printables**: weekly plan, grocery list, exercise cards, fridge chart
- **The Courtyard**, the members' community, moderated by real people
- Doing it together? **Add your partner for $8/month**, with their own level and progress

**Honest value framing (under the card, heading):** What this is, and what it isn't.

For comparison, a personal trainer once a week costs about $240–400 a month. A physical-therapy visit often means a $30–60 copay. A meal-planning app costs $10–15 a month. Strong Years is not physical therapy and it does not replace your doctor or a trainer who can watch you in person. It's what makes the other 29 days of the month count: less than one personal-training session a month, for a coach who shows up every single day. About 66 cents a day.

(Do not add a "total value $___" figure. There is no honest number for it, and we don't need one.)

**Button:** Start 7 days for $1

### 2.13 Section 11: Member voices (placeholder system)

**Heading:** What members say.

Layout: 3 quote cards + 1 "Strength Age change" card, each with a real photo only if the member uploaded it and consented.

`[REAL MEMBER QUOTE 1: ≤ 40 words, verified member, written permission on file. Name: First name + last initial. Age: only if member chose to share. "Member since [Month Year]". If they received any incentive: "Received a free month for sharing their experience."]`

`[REAL MEMBER QUOTE 2: same rules. Prefer a quote about a daily-life moment (stairs, grandkids, getting off the floor) over feelings.]`

`[REAL MEMBER QUOTE 3: same rules. Prefer a partner/couple or adult-child-who-gifted quote.]`

`[AGGREGATE CARD: only once ≥ 200 members have 2+ retests. Example format: "Of members who did at least 12 sessions a month for 3 months, [X]% improved their chair-stand count. Median change: [+Y] stands. Results vary." Source: our own retest data, date range stated.]`

**Pre-launch version (use until real quotes exist):**
Heading: "We're new, so we won't show you reviews we don't have."
Body: "Other accounts fill this space with quotes that may not be real. We'd rather show you nothing than make something up. Try it for 7 days for $1, and if you like it, tell us, and we'll ask your permission to share your words here."

That pre-launch block is itself a conversion asset for this audience, who have been burned by fake reviews. Keep a version of it permanently, above the real quotes: "Every quote here is from a real member, shared with permission. We never pay for reviews or write them ourselves."

### 2.14 Section 12: Who it's for, who it isn't for

**Heading:** Is this right for you?

**It's for you if:**
- You're around 55 to 85 and want to stay strong enough to live on your own terms
- You'd rather do 10 minutes at home than drive to a gym
- You want someone patient to follow, not a loud instructor
- You'd like to see proof you're getting stronger
- You use a cane, have a replaced hip or knee, or haven't exercised in years (start on the Rebuild track, and check with your doctor first)

**It's not for you if:**
- You're looking for a cure for a medical condition (we don't offer one, and anyone who does is not being honest with you)
- You're currently in rehab after surgery and haven't been cleared by your surgeon or physical therapist
- You want intense workouts; this is steady, safe progress

### 2.15 Section 13: Pricing and ways to start

(Baseline / non-blitz copy. In blitz mode this section shows the founding card from §5.6 items 2–5 with one button to `/join`, and no $1 trial, per §0.2.1.)

**Heading:** Start this week for $1.

**Main card (Rice, Persimmon top border, largest element on the page):**
- Line 1 (Fraunces 32px): **7 days of Strong Years for $1**
- Line 2: Then {{PRICE}} a month. Renews monthly until you cancel.
- Checklist: your Daily Practice every day, all six 12-week programs, Sun Yoon's recipes, your first Strength Age test, the Wednesday live Q&A
- **Button:** Start 7 days for $1
- Under button: "We'll email you{{IF_SMS: and text you}} 48 hours before your trial ends. Cancel online in two screens at most{{IF_SMS: , or by texting CANCEL}}. No phone call needed, no questions."

(No annual card on this page: OFFER.md keeps the annual price off the cold-traffic front end because it lowers trial starts. Annual is offered at trial end and in member campaigns, Section 7.11.)

**"Other ways to start" (smaller, three rows, each a link-button with Ink text on Rice, 2px Ink border):**
- **Rather own something first? 7-Day Strength Reset, $7.** Seven follow-along sessions and a printable plan, yours to keep. Includes 7 days of Strong Years, then {{PRICE}}/month unless you cancel.
- **Here for the food? Sun Yoon's Strong Kitchen + Chang Yin's 12-Week Printable, $17.** Includes 7 days of Strong Years, then {{PRICE}}/month unless you cancel.
- **Buying for your mom or dad? Give 3 months for $49, or a year for $119.** Prepaid, never auto-renews. They get a card from Sun Yoon, and if they agree, you get a monthly note like "Mom did 18 sessions."

### 2.16 Section 14: Guarantee

(Baseline copy. Blitz mode: heading "The 14-day money-back guarantee." and body "If your founding membership isn't worth it to you, for any reason, tap Refund in your account or reply to any email within 14 days of your first charge, and we'll refund it. No forms, no questions." per §0.2.1.)

**Heading:** The 14-day money-back guarantee.

**Body:**
Try Strong Years. If your membership charge wasn't worth it to you, for any reason, tap "Refund" in your account within 14 days of that charge, and we'll refund it (and the $1 too). One money-back guarantee per person. No forms, no questions. Add-ons you bought (like printables) are refunded on request within 14 days: just email us.

(Implementation per the canonical refund policy (top of file) and OFFER.md 3.4: self-serve refund in the account for 14 days after the first membership charge, one per person; add-ons refunded on request within 14 days; the kit 30 days. Every refund we make ourselves avoids a $15 dispute fee and a chargeback strike. The model assumes 6% front-end and 2.5% subscription refunds.)

### 2.17 Section 15: FAQ

**Is Chang Yin real?**
No. Chang Yin and Sun Yoon are AI characters created by our team. Their story (a retired welder from Incheon's Chinatown and a lunch-counter owner from Incheon, married 50 years, in California since 1983) is invented. We're telling you plainly because you should always know who, or what, you're learning from. What is real: the exercises, the progressions and the recipes. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Every session is designed and reviewed by `[PT NAME]`, a licensed physical therapist, and every recipe by `[RD NAME]`, a registered dietitian.] FALLBACK: "Every session and recipe is built by our team from published exercise and nutrition guidelines for older adults, and our sources are listed at {{DOMAIN}}/how-we-make-this." When an AI video can't show a movement precisely, a real, named coach demonstrates it. Chang Yin has no medical license and no teaching credentials, and we'll never say he does. What he has is patience, a slow clear voice, and he'll show up every morning.

**Who writes and checks the sessions?**
[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Our team writes them with `[PT NAME]`, PT, DPT, who approves every movement, every progression and every safety cue before publishing. Recipes are checked by `[RD NAME]`, RDN.] FALLBACK: "Our team writes them from published exercise and nutrition guidelines for older adults (CDC, ACSM, PROT-AGE), with conservative safety cues on every movement." You can read our full process at `{{DOMAIN}}/how-we-make-this`.

**I'm 78, I use a cane, and I haven't exercised in years. Can I do this?**
Very likely, yes, starting on the Rebuild track, where every movement is done seated or holding a sturdy counter. Please check with your doctor before starting any new exercise, especially if you've had a fall, surgery, heart problems or dizziness recently. If anything causes sharp pain, chest discomfort, dizziness or shortness of breath, stop and call your doctor.

**I have bad knees / a replaced hip / osteoporosis. Is it safe?**
Every session has options that avoid deep knee bending, twisting under load, and floor work, and a "sore knee / sore back" button that swaps in a modified version. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Our physical therapist wrote specific notes for knee replacements, hip replacements (including movement precautions you may have been given after surgery) and osteoporosis.] FALLBACK: "Sessions include general notes for people with knee or hip replacements and osteoporosis, drawn from published guidance." Follow your surgeon's or physical therapist's instructions first; ours never override theirs.

**Do I need equipment?**
No. A sturdy chair without wheels and a kitchen counter are enough. Later, two water jugs or a resistance band help you progress. We also sell an optional kit (3 resistance loops, a door anchor and a grip trainer, $29), but you never need it.

**How do I watch?**
On your phone, tablet or computer, or cast it to your TV. Captions are on by default and large. Everything works with one tap from our daily text or email, no app store required (there's an app too if you prefer).

**What happens after 7 days?**
Your trial costs $1. 48 hours before it ends, we email you{{IF_SMS: and text you}} a reminder. If you do nothing, your Strong Years membership continues at {{PRICE}} per month, charged on the same date each month, until you cancel. You can cancel anytime online in your account in at most two screens{{IF_SMS: , or by texting CANCEL}}.

**How do I cancel?**
Go to Account → Membership → Cancel, or reply "cancel" to any of our emails{{IF_SMS: , or text CANCEL}}. You'll see one option (pause or a cheaper plan) and a clear "Finish canceling" button right beside it, the same size. That's two screens at most. Your cancellation is confirmed on screen and by email. No phone calls, no chat, and the AI characters are never part of it.

**Can my husband or wife use it too?**
Yes. Add your partner for $8 a month. They get their own level, their own Strength Age and their own progress. Add them in Account → Partner.

**I'm buying this for my mother or father. How does that work?**
Choose "Give Mom & Dad Strong Years", pick 3 months ($49) or 12 months ($119), and we'll send them a welcome card from Sun Yoon by email or a printed card by mail. Gifts are prepaid and never renew automatically. If your parent agrees, you'll get a monthly note like "Mom did 18 sessions." When the gift ends, they can choose to continue on their own card, or you can extend it.

**Will this fix my arthritis, blood pressure or blood sugar?**
No program can promise that, and we don't. Strong Years is general fitness and nutrition education. Regular strength, balance and walking are habits your doctor will likely encourage, and research in older adults links them with better strength, balance and everyday function. Keep working with your doctor, and don't change any medication because of anything you see here.

**Is this religious or spiritual?**
No. Chang Yin is a retired welder, not a monk or a "master", and this isn't a religious practice. Tai chi and qigong appear as movement and breathing practices, taught for balance, mobility and calm.

**What's the Strength Age number? Is it medical?**
It's a motivational estimate that compares your chair-stand and balance results with published norms for your age and sex. It's a helpful way to see progress, not a medical test or a diagnosis.

**What if I miss days?**
Nothing bad happens. Your streak has grace days, your calendar keeps your progress, and Chang Yin picks up where you left off. Three sessions a week already makes a difference; every day is a bonus.

**Do you sell my information?**
No, we don't sell it. We use your information to run your membership and send you the messages you ask for. To measure our ads, we share limited data with advertising partners (for example, a scrambled, hashed email when you sign up); you can opt out at Your Privacy Choices. Your quiz answers and anything about your health are never shared with advertisers. You can delete your account and data anytime. Details: {{DOMAIN}}/privacy and {{DOMAIN}}/health-data.

### 2.18 Section 16: Final CTA

**Heading:** Tomorrow morning, eight minutes. That's all we're asking.

**Body:** Pick your level, follow Chang Yin, and test your Strength Age on day one. If it isn't worth it, you get every penny back.

**Button:** Start 7 days for $1
**Microcopy:** Then {{PRICE}}/month. Cancel online anytime.

### 2.19 Footer (Ink background, Rice text, full contrast)

Chang Yin and Sun Yoon are AI characters; their story is fictional. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Content reviewed by `[PT NAME]`, PT, DPT and `[RD NAME]`, RDN.] FALLBACK: "Content built from published exercise and nutrition guidelines for older adults." General fitness and nutrition education, not medical advice. Consult your physician before beginning any exercise program. Membership renews automatically at the price shown until cancelled; cancel online anytime at `{{DOMAIN}}/account` or by replying "cancel" to any email{{IF_SMS: , or by texting CANCEL}}. Terms · Privacy · Refunds · How we make this · Science · Contact (email + mailing address).

### 2.20 Page variants to build from these blocks

| URL | Changes |
|---|---|
| `/start` | As above |
| `/r7` 7-Day Strength Reset sales page | Hero: "Seven days. Seven short sessions. One stronger week." $7, includes 7 days of Strong Years, then {{PRICE}}/month unless you cancel (terms stated in the hero microcopy and order box). Keep sections 2, 3, 6 (limited to 7-day plan), 8, 9, 15 (Reset FAQ subset). Product-only split-test arm: "One-time $7, no subscription" with the membership offered after purchase |
| `/kitchen` Sun Yoon's Strong Kitchen + Chang Yin's 12-Week Printable, $17 | Hero in her voice: "Cheap food, lots of protein, and no nonsense." Contents: Sun Yoon's Strong Kitchen recipe collection (Korean, Korean-Chinese and Chinese home dishes adapted for protein and fiber, soft-food versions, soups, remedies with honest evidence grades: good evidence / some evidence / tradition only), weekly grocery template, plus Chang Yin's printable 12-week plan. Includes 7 days of Strong Years, then {{PRICE}}/month unless you cancel. 14-day money-back guarantee on the membership charge (one per person); the $17 bundle itself is an add-on, refunded on request within 14 days |
| `/gift` | Hero: "Give Mom & Dad Strong Years." Lead offer 3 months $49; 12 months $119; prepaid, never auto-renews. Kit ($29) offered first in the upsell flow. "Take the Strength Age test together on a video call" as a bonus idea |
| `/challenge` 14-Day Strength Challenge | Monthly cohort starting on the 1st, countdown page, $9 including 14 days of Strong Years, then {{PRICE}}/month unless you cancel; cohort group + daily live check-in |
| `/q/a/result/*` | Personalized result on top (Section 3 quizzes), then sections 4, 6, 7, 10, 13 onward. In blitz mode the offer block and CTAs point to `/join` |
| `/join` (blitz mode) | Lean founding checkout page: full copy in §5.6. In blitz mode `/r7`, `/reset` and `/kitchen` redirect here (the $7 and $17 products are order bumps) |

---

## 3. Quizzes

Build notes for both quizzes:
- One question per screen, answer buttons full width, 60px tall, Ink text on Rice with 2px Ink border; selected state = Jade fill, Rice text. Progress shown as "Question 4 of 14" in words (no progress bar that looks gray/empty; if a bar is used, the empty part is Paper with an Ink outline).
- Back button always visible. No timers pressuring answers. Autosave answers so a parent can finish later (magic link in email).
- Every screen carries the one-line disclosure in the footer: "Created with AI characters. Not medical advice." plus [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "Reviewed by `[PT NAME]`, PT, DPT."] FALLBACK: "(no review line)"
- Events: first-party analytics only (`q_a_start`, `q_a_step_{n}`). The only event sent to Meta is `Lead` on the neutral paths `/q/a` or `/q/b`, with no quiz identifier, answer or result. Result or profile events are never sent to any ad platform (a profile code like Safe Mode reveals health status).
- Email gate test: Cell 1 requires email to show the result; Cell 2 shows the result with an optional "Email me my plan" box. Decide on revenue per quiz start, not on lead rate.

### 3.1 Quiz A: "What's your Strength Age?"

**URL:** `{{DOMAIN}}/q/a`
**Promise:** "3 minutes. Two simple at-home tests and a few questions. Get your Strength Age and a 7-day plan made for your body."
**Which version runs where (one spec, see the canonical policies):** paid and DM traffic get the **short version**: Q1–Q5, then T1 (chair stand) with a "Do it later in the app" button of equal size, then the lead screen, about 90 seconds. T2 (balance) and Q6–Q14 run in the app as the day-1 baseline. This full version is the in-app and organic version. Test the full version against the short one on organic traffic only.

#### Intro screen
**Heading:** What's your Strength Age?
**Body:** Your birthday gives you one age. Your legs and balance give you another. Find yours with two simple fitness tests used in senior fitness research, and get a free 7-day plan.
**You'll need:** a sturdy chair without wheels pushed against a wall, a kitchen counter, and 3 minutes. If you can, have someone nearby.
**Button:** Start the test
**Small line:** Chang Yin is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: The tests and plans are reviewed by a licensed physical therapist.] FALLBACK: "The tests come from published senior fitness research (CDC STEADI, Rikli & Jones)."

#### Q1. Who is taking the test today?
- Me
- I'm helping my mom, dad or partner take it right now
- I'm taking it for someone else who isn't here (you'll answer the questions only; skip the tests)

Routing: option 3 skips both physical tests, computes a questionnaire-only estimate labelled as such, and adds the gift block to the result.

#### Q2. Are you a woman or a man?
- Woman
- Man
- Prefer not to say (we'll compare with combined averages)

#### Q3. How old are you? (or the person taking the test)
Number picker, 45 to 95. Under 60: "Our comparisons start at age 60, so we'll compare you with 60 to 64-year-olds. You'll likely look younger than you are. Good."

#### Q4. Safety check first. In the last few months, has any of these happened? (tick all that apply)
- Chest pain, pressure or tightness when active
- Dizziness, fainting or nearly fainting
- A fall
- Surgery or a hospital stay
- A doctor told you to limit physical activity
- None of these

Routing: any box except "None" → **Safe Mode**. Screen text: "Thank you for telling us. Let's skip the standing tests today. Please show your doctor the plan we'll make you before you start. We'll include a one-page summary you can print or forward." Safe Mode goes to Q6 onward, skips T1/T2, and assigns profile P6 Gentle Restart.

#### Q5. Do you use any of these to get around?
- No
- A cane, sometimes
- A cane, most of the time
- A walker
- A wheelchair

Routing: walker or wheelchair → seated tests only (T1 replaced by the seated arm test below; T2 skipped) → P6 Gentle Restart with a Rebuild-track (chair-based) plan. Cane users take tests with the counter version and extra safety copy.

#### T1. The 30-second chair stand (video-guided screen)
**Heading:** Test 1: Stand up, sit down, for 30 seconds.
**Instructions (with a 20-second demo loop, captions on):**
1. Push a sturdy chair against a wall so it can't slide.
2. Sit in the middle of the seat, feet flat, about shoulder-width apart.
3. Cross your arms over your chest. If you need your hands to stand, that's okay, just tick the box below.
4. When Chang Yin says "Go", stand all the way up, then sit all the way down. That's one.
5. Repeat as many times as you comfortably can in 30 seconds. Stop anytime if anything hurts, you feel dizzy or short of breath.

**Button:** Start my 30 seconds (big timer, Chang Yin's voice counts down "3, 2, 1, go" and "10 seconds left", with a chime at the end; the person counts their own stands, or the helper counts).
**Input:** "How many full stands did you do?" (number 0–30). Checkbox: "I needed to use my hands or arms."
**Seated alternative (walker/wheelchair route):** "Arm curl with a water bottle: how many curls in 30 seconds with your stronger arm?" recorded but used for tracking only, not for Strength Age.

#### T2. The 4-stage balance test
**Heading:** Test 2: How steady are you?
**Instructions:**
Stand next to your kitchen counter with one hand hovering just above it. Do not hold on unless you need to; if you need to, that stage is finished. Hold each position for 10 seconds. Stop at the first one you can't hold for 10 seconds without grabbing the counter or moving your feet.
1. Feet side by side, touching
2. One foot slightly ahead, the arch of the front foot beside the big toe of the back foot
3. One foot directly in front of the other, heel touching toe
4. Stand on one foot

(Illustrated with four real photos of feet positions; each stage has its own 10-second timer button.)

**Input:** "Which was the last position you held for the full 10 seconds?"
- I couldn't hold position 1
- Position 1: feet together
- Position 2: half step
- Position 3: heel to toe
- Position 4: one foot

#### Q6. Can you open a new, sealed jar?
- Easily
- With some effort
- I usually need a tool or someone's help
- No

#### Q7. Could you carry two full gallon jugs of water (about 8 pounds each) from the car to the kitchen?
- Yes, easily
- Yes, with a rest
- Only one at a time
- No

#### Q8. If you were sitting on the floor, how would you get up?
- Without using my hands
- Using one hand or a knee
- I'd need furniture to push on
- I couldn't get up on my own
- I'm not sure, I avoid the floor

#### Q9. A flight of about 10 stairs. What's true for you?
- Up without holding the rail
- Up, holding the rail
- Up, holding the rail and stopping to rest
- I avoid stairs

#### Q10. Walking with people your age, you usually:
- Keep up easily or lead
- Keep up, but it takes effort
- Fall behind
- I don't walk far

#### Q11. In a normal week, how often do you do strength exercise (weights, bands, bodyweight)?
- 2 or more times
- Once
- Rarely
- Never

#### Q12. Anywhere that often aches or feels stiff? (tick all)
- Knees
- Hips
- Lower back
- Shoulders or neck
- Hands or wrists
- Nothing in particular

#### Q13. A year from now, what would you most love to do more easily?
- Get down on the floor with my grandchildren, and back up
- Travel and walk all day without paying for it
- Garden, carry and lift things myself
- Keep living independently in my own home
- Feel steady and sure on my feet
- Look and feel strong again

#### Q14. How many minutes could you give this, most days?
- 5
- 10
- 15
- 20 or more

#### Lead screen
**Heading:** Your Strength Age is ready.
**Body:** Where should we send it, along with your 7-day plan and printable cards?
Fields: First name, Email.
Checkbox (unchecked, separate): "Text me my daily session link. Msg frequency varies, about 1/day. Msg & data rates may apply. Reply STOP to cancel, HELP for help. Consent is not a condition of purchase." + phone field appears only when ticked.
**Button:** Show my Strength Age
**Small line:** We never sell your information. Unsubscribe anytime.

#### Scoring logic

**Chair-stand reference midpoints** (middle of the "normal range" published by Rikli & Jones, Senior Fitness Test, the same norms behind CDC STEADI cutoffs):

| Age band | Women midpoint | Men midpoint | CDC STEADI below-average cutoff (W / M) |
|---|---|---|---|
| 60–64 | 14.5 | 16.5 | < 12 / < 14 |
| 65–69 | 13.5 | 15.0 | < 11 / < 12 |
| 70–74 | 12.5 | 14.5 | < 10 / < 12 |
| 75–79 | 12.5 | 14.0 | < 10 / < 11 |
| 80–84 | 11.5 | 12.5 | < 9 / < 10 |
| 85–89 | 10.5 | 11.0 | < 8 / < 8 |
| 90–94 | 7.5 | 9.5 | < 4 / < 7 |

Midpoints are the middle of the Rikli & Jones normal ranges (women 12–17, 11–16, 10–15, 10–15, 9–14, 8–13, 4–11; men 14–19, 12–18, 12–17, 11–17, 10–15, 8–14, 7–12, youngest to oldest band); every row was checked against those ranges and the CDC STEADI cutoffs (EVIDENCE.md E11, E49). "Prefer not to say": average the two midpoints. Under 60: use 60–64. Age 95 (the top of the Q3 picker) uses 90–94, the oldest published band.

**Components (years added to or subtracted from chronological age):**
1. **Chair (C):** `C = −2.5 × (reps − midpoint)`, clamped to −12…+12. If "used hands" is ticked, score it the STEADI way (the test counts as 0 stands, below-average): `C = +12`, show the stand count separately, and route to the Rebuild track.
2. **Balance (B):** couldn't hold 1 → +10; held 1 only → +8; held 2 → +5; held 3 → 0; held 4 → −3. For age 80+: held 3 → −2, held 4 → −5 (tandem is a strong result at that age).
3. **Self-report (S):** sum the items, then multiply by 0.5.
   - Jar: −1 / 0 / +2 / +3
   - Carry: −2 / 0 / +2 / +4
   - Floor: −3 / 0 / +3 / +5 / +2 (unsure)
   - Stairs: −2 / 0 / +2 / +4
   - Walking: −2 / 0 / +2 / +4
   - Strength training: −2 / −1 / 0 / +1
4. **Strength Age** = `age + C + B + S`, rounded to the nearest whole year, clamped to `[age − 15, age + 20]`, and never below 40.
5. **Questionnaire-only (Q1 option 3):** `age + 2 × S`, clamped to ±10, displayed as "Estimated from answers only. Take the two tests together for a real number."
6. **Safe Mode / walker / wheelchair:** no number. Display "Your starting line: the Rebuild track (chair-based)" instead.

**Flags used for routing:**
- `F_balance` = held stage ≤ 2
- `F_joint` = knees, hips or lower back ticked AND (stairs answer ≥ "holding rail and resting" OR floor answer ≥ "need furniture")
- `F_hands` = hands used on chair stand OR chair reps below the STEADI cutoff
- `gap` = Strength Age − age

**Profile assignment (first match wins):**
1. **P6 Gentle Restart:** Safe Mode, walker/wheelchair, chair reps < 5, or couldn't hold balance stage 1
2. **P3 Wobbly Foundations:** `F_balance`
3. **P4 Stiff Engine:** `F_joint`
4. **P1 Steady Oak:** gap ≤ −5
5. **P5 Quiet Slide:** gap ≥ +5
6. **P2 Rooted but Rusty:** everything else (gap −4 to +4)

#### Result page template (top of page, above the reused landing sections)

```
[Strength Age card, printable]
Your Strength Age: {SA}          Your birthday age: {age}
Chair stands: {reps} in 30 seconds (typical for {band} {sex}: {low}–{high})
Balance: held position {stage} for 10 seconds
Your profile: {profile name}
[Example sentence: "That's {gap_abs} years {younger/older} than your birthday age."]
Retest date: the 1st of next month
Small line: Strength Age is a motivational estimate from published fitness norms, not a medical test.
```

Then: profile copy (below), the 7-day plan, the offer block, then landing sections 4, 6, 7, 10, 13–16.

#### P1. Steady Oak (Strength Age 5+ years younger)

**Headline:** Your legs are younger than your birthday. Now let's keep it that way.
**Body:**
{First name}, your Strength Age is {SA}, which is {gap_abs} years younger than you are. You stood up {reps} times in 30 seconds; the typical range for your age is {low} to {high}. You held the {stage_name} for 10 seconds.

This is the group that has the most to protect. Strength and especially leg power drop fastest when people "coast," and it usually happens quietly, over a winter, an illness, or a busy year. Your plan is built to push you a little, so you keep the lead you've built.

**Your track:** Strong (Iron once the reps get easy; Steady on tired days)
**Your first 7 days:**
- Day 1: Legs, Strong level: tempo sit-to-stands with a water jug, split squats at the counter (12 min)
- Day 2: Balance + quick feet: side steps, heel-toe walk, single-leg reach (10 min)
- Day 3: Mobility + breath: hip openers, thoracic rotations, 5 minutes of slow-exhale breathing (10 min)
- Day 4: Upper body + grip: band rows, wall push-ups to counter push-ups, farmer carries (12 min)
- Day 5: Power day: "fast up, slow down" chair stands, step-ups (10 min)
- Day 6: 20-minute tai chi flow, the long one
- Day 7: Rest, walk, and Sun Yoon's high-protein Sunday soup

**What to expect by your first retest:** Most people who train 3+ times a week notice the sessions feel easier within two to three weeks. Your chair-stand number may climb by a couple of reps; if you're already near the top of the range, your goal is to hold it and improve your one-leg balance time.

**Offer block:** "Your plan runs inside Strong Years as your Daily Practice. Start it tomorrow for $1."
Primary button: **Start my Steady Oak plan: 7 days for $1**
Under: Then {{PRICE}}/month. Cancel online anytime.
Secondary line: "Want a finish line? Start the 12-week *Strong at 70* program on day 1; all six programs are included."
Fallback link: "Rather try one week with no subscription? 7-Day Strength Reset, $7."

#### P2. Rooted but Rusty (within 4 years)

**Headline:** You're right about where most people your age are. That's the problem, and the opportunity.
**Body:**
{First name}, your Strength Age is {SA}. You did {reps} chair stands (typical for your age: {low} to {high}) and held the {stage_name}.

"Average" at your age means the slide has started for most people: the armrests get used a little more each year. The good news is that "average" responds fast to training because you haven't been asking your legs for much. Three short sessions a week is enough to start moving your number.

**Your track:** Steady (Strong on good days)
**Your first 7 days:**
- Day 1: Legs: sit-to-stands to a slow count, counter squats, calf raises (9 min)
- Day 2: Balance: the counter balance ladder, heel-toe walk along the counter (8 min)
- Day 3: Morning mobility + breath (8 min)
- Day 4: Upper body + grip: wall push-ups, band rows or towel rows, jug carries (9 min)
- Day 5: Legs + power: faster chair stands, step-ups on the bottom stair (9 min)
- Day 6: 15-minute tai chi flow
- Day 7: Rest, a 15-minute walk after lunch, Sun Yoon's egg-and-tofu breakfast

**What to expect by your first retest:** A realistic first goal is 1 to 3 more chair stands and one balance stage further. Sessions that feel hard on day 1 usually feel easy by day 14; that's when Chang Yin moves you up.

**Offer block:** Primary button: **Start my plan: 7 days for $1**. Fallback: $7 Reset.

#### P3. Wobbly Foundations (balance first)

**Headline:** Your legs have work to do, but first, let's make you steady.
**Body:**
{First name}, you held the {stage_name} for 10 seconds but not the next one. That's your starting line. Balance is one of the most trainable things there is, and it often improves faster than strength: a few minutes at the kitchen counter most days, and the next position usually comes within weeks.

Please mention this result to your doctor at your next visit, especially if you've felt dizzy or unsteady; some causes of unsteadiness, like medicines or inner-ear issues, need a doctor's eye.

**Your track:** Steady, always at the counter (Rebuild on tired days); program: *Balance & Steady Feet*
**Your first 7 days (Steady Feet track + legs):**
- Day 1: Steady Feet 1: the counter balance ladder, weight shifts, heel and toe raises (8 min)
- Day 2: Legs: sit-to-stands, counter mini-squats (8 min)
- Day 3: Steady Feet 2: head turns while standing steady, reaching (8 min)
- Day 4: Walking Stronger 1: heel-toe walking along the counter, side steps (8 min)
- Day 5: Steady Feet 3 + legs (10 min)
- Day 6: Gentle tai chi, 12 minutes (tai chi has good evidence for balance in older adults)
- Day 7: Rest, plus Chang Yin's home safety checklist: lighting, rugs, grab bars, night lights

**What to expect by your first retest:** Our goal for month one is one balance stage further, or the same stage held more confidently. Balance often improves faster than strength.

**Offer block:** Primary button: **Start my Steady Feet plan: 7 days for $1**. Fallback: $7 Reset (Steady Feet edition).

#### P4. Stiff Engine (joints first)

**Headline:** Your {knees / hips / back} are talking. Here's how to train around them, and then through them.
**Body:**
{First name}, your Strength Age is {SA}, and you told us your {joint list} ache, with stairs or getting off the floor harder than you'd like. Joint aches are common and, for many people with everyday stiffness or arthritis, moving more (carefully) helps more than resting. Strengthening the muscles around the knee and hip is one of the most commonly recommended approaches for knee and hip osteoarthritis.

Our rule: some mild discomfort during exercise that settles within a day is usually okay; sharp pain, swelling that lasts, or pain that's worse the next day means back off, and check with your doctor or physical therapist. If you've had a joint replaced, follow your surgeon's precautions first.

**Your track:** Rebuild or Steady depending on the day (use the "sore knee / sore back" button); program: *Back Strong* or *Strong at 70*
**Your first 7 days:**
- Day 1: {Knees & Stairs 1 / Back & Posture 1 / Hip session}: pain-free-range strength (10 min)
- Day 2: Morning Unlock mobility (7 min)
- Day 3: Legs on the Rebuild track: seated knee extensions, sit-to-stands to a higher seat (use a cushion) (9 min)
- Day 4: Upper body + grip (8 min)
- Day 5: {Track session 2} (10 min)
- Day 6: 12-minute gentle tai chi
- Day 7: Rest + walk + Sun Yoon's ginger-and-greens soup (comfort food, not a treatment)

**What to expect by your first retest:** A realistic goal is doing the stairs with less effort or a higher chair-stand number using a slightly higher seat. Joint comfort varies week to week; that's why you choose your level every day.

**Offer block:** Primary: **Start my {Knees / Back / Hips} plan: 7 days for $1**. Fallback: $7 Reset (joint-friendly edition).

#### P5. Quiet Slide (Strength Age 5+ years older)

**Headline:** Your legs are older than you are. Let's go get those years back.
**Body:**
{First name}, your Strength Age is {SA}, {gap_abs} years older than your birthday. You did {reps} chair stands; typical for your age is {low} to {high}. This doesn't mean anything is wrong with you. It means your legs haven't been asked to work hard in a while, which is the most fixable problem on this page.

The research here is genuinely encouraging: in supervised studies, even people in their 80s and 90s gained substantial leg strength in a few months of progressive training. The people who gain the most are usually the ones starting from the lowest point.

**Your track:** Rebuild for week 1, then Steady
**Your first 7 days:**
- Day 1: The Chair Builder: sit-to-stands from a higher seat (add a firm cushion), seated leg lifts (8 min)
- Day 2: Balance at the counter, stages 1 to 3 (7 min)
- Day 3: Morning mobility + breath (7 min)
- Day 4: Upper body + grip on the Rebuild track (8 min)
- Day 5: The Chair Builder 2 (8 min)
- Day 6: 10-minute seated tai chi
- Day 7: Rest + 10-minute walk after your biggest meal + Sun Yoon's 30-gram-protein breakfast

**What to expect by your first retest:** For many people starting here, 2 to 4 more chair stands in the first month is realistic, and it often shows up first as "I didn't need the armrest."

**Offer block:** Primary: **Start my plan: 7 days for $1**. Fallback: $7 Reset.

#### P6. Gentle Restart (safety-first)

**Headline:** We'll start gently, and we'll start with your doctor in the loop.
**Body:**
{First name}, thank you for being honest in the safety questions. Because of {reason: a recent fall / surgery / dizziness / chest discomfort / your doctor's advice / using a walker or wheelchair}, we skipped the standing tests today. That's the right call.

Here's what we suggest: print or forward the one-page summary below to your doctor or physical therapist and ask, "Is it okay for me to do seated strength and breathing exercises for 10 minutes a day?" Most people in your situation hear "yes, and here's what to avoid," and you can bring those notes to your plan.

**[Download your one-page summary for your doctor]** (PDF: their answers, the proposed chair-based Rebuild plan, the exact movements with pictures, the stop rules, and a line for the doctor's notes.)

**Your track:** Rebuild (chair-based)
**Your first 7 days (once your doctor says go):**
- Day 1: Seated breathing and posture (6 min)
- Day 2: Seated leg strength: knee extensions, marches, heel raises (7 min)
- Day 3: Seated upper body with a towel (6 min)
- Day 4: Seated mobility: neck, shoulders, ankles (6 min)
- Day 5: Seated leg strength 2 (7 min)
- Day 6: Seated tai chi, 8 minutes
- Day 7: Rest + Sun Yoon's soft-food protein recipes

**Offer block (soft, no countdowns, no upsells on this path):**
"When you're ready, the full chair-based Rebuild track is inside Strong Years. You can try it for 7 days for $1, and we'll remind you 48 hours before it renews."
Button: **Save my plan and start when I'm ready** (email captured, sends the doctor PDF + a "Doctor said yes?" button email in 3 days)
Secondary button: **Start 7 days for $1**
Checkout for P6 shows no order bump and skips the upsell ladder, by design.

#### Adult-child overlay (Q1 option 2 or 3)
Added above the offer block on any profile:
**Heading:** Doing this for your mom or dad?
**Body:** Two options. Give them Strong Years (3 months $49 or 12 months $119, prepaid, never auto-renews) with a welcome card from Sun Yoon. Or start it yourself for $1 and add them as your partner for $8/month if you live together. Either way, you can do the monthly retest together on a video call.
Buttons: **Give 3 months ($49)** · **Start 7 days for $1**

### 3.2 Quiz B: "The Gut & Energy Check" (Sun Yoon's quiz)

**URL:** `{{DOMAIN}}/q/b`
**Promise:** "Sun Yoon's 2-minute kitchen check. Find out what's draining your energy after meals, and get a 7-day kitchen plan."

#### Intro screen
**Heading:** Why am I so tired after I eat?
**Body (Sun Yoon's voice):** Fourteen questions. Be honest with me, and I'll be honest with you. At the end you get a 7-day kitchen plan and three recipes to start tonight.
**Button:** Start
**Small line:** Sun Yoon is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Recipes and advice are reviewed by `[RD NAME]`, a registered dietitian.] FALLBACK: "Recipes and advice are built from published nutrition guidance for older adults." Not medical advice.

#### Q0. First, anything here in the last 3 months? (tick all)
- Losing weight without trying
- Blood in your stool, or black, tarry stools
- Trouble swallowing, or food getting stuck
- Vomiting that keeps coming back
- A change in bathroom habits lasting more than a few weeks, with no clear reason
- Severe or constant belly pain
- None of these

Routing: any box except "None" → **Stop screen** (no sale, no email gate):
> "{First name}, I'm going to be blunt, because I care: these are things to show a doctor, soon. Please call your doctor's office this week and tell them exactly what you ticked. No recipe or kitchen trick should replace that check. If the pain is severe, or you're vomiting blood, call 911."
> Button: "Show me gentle kitchen tips anyway" → a general tips page (no offer). Tag contact `flag_b_redflag`; they receive only a single follow-up email in 7 days ("Did you get that check-up?") and no promotional email for 30 days.

#### Q1. Your age
- 50–59 · 60–69 · 70–79 · 80+

#### Q2. Your approximate weight (optional, helps us set your protein number)
- Under 130 lb · 130–159 · 160–189 · 190–219 · 220+ · Skip

#### Q3. A usual breakfast looks like:
- Toast, cereal, a pastry or fruit, and coffee (0 pts)
- Eggs, Greek yogurt, cottage cheese, tofu, or leftovers with protein (3)
- Just coffee or tea (0)
- I skip breakfast (1)

#### Q4. How many of your meals include a palm-sized serving of protein (meat, fish, eggs, tofu, beans, Greek yogurt)?
- 3 (4) · 2 (2) · 1 (1) · 0 (0)

#### Q5. When do you usually feel most tired?
- Mid-morning (Rhythm 1)
- After lunch through mid-afternoon (Rhythm 0)
- Early evening (Rhythm 2)
- All day (Rhythm 0, Rest −1)
- Not often (Rhythm 3)

#### Q6. After your biggest meal, you usually:
- Sit or lie down (0)
- Do chores or potter around (2)
- Go for a walk (4)

#### Q7. How often do you feel uncomfortably full or bloated after eating?
- Most meals (0) · A few times a week (2) · Rarely (4)

#### Q8. Bathroom regularity:
- Like clockwork (4) · Sometimes stuck (2) · Often stuck (0) · Often loose (1)

#### Q9. Servings of vegetables, fruit, beans or whole grains per day:
- 5 or more (4) · 3–4 (3) · 1–2 (1) · 0–1 (0)

#### Q10. Glasses of water or tea per day (not counting coffee or alcohol):
- 6+ (3) · 4–5 (2) · 2–3 (1) · 0–1 (0)

#### Q11. Most nights you:
- Sleep 7+ hours and wake rested (4)
- Sleep enough but wake tired (1)
- Wake up 2 or more times (1)
- Struggle to fall asleep (0)

#### Q12. Your last coffee or caffeinated tea of the day is usually:
- Before noon (3) · Afternoon (1) · Evening (0) · I don't drink caffeine (3)

#### Q13. Alcohol in a typical week:
- None (3) · 1–3 drinks (2) · 4–7 drinks (1) · 8+ (0)

#### Q14. Is chewing or swallowing tougher foods hard for you?
- No (3) · Sometimes (1) · Yes (0)

#### Q15. Do you take 5 or more medicines or supplements daily?
- Yes · No
(Not scored. If Yes, the result adds: "Some medicines can affect appetite, digestion, sleep and energy. Bring a list to your pharmacist and ask, 'Could any of these be making me tired or affecting my stomach?' Pharmacists are glad to do this, often for free.")

#### Lead screen
Same structure as Quiz A. **Heading:** "Your kitchen plan is ready." **Button:** "Show my plan".

#### Scoring logic
Five dimensions, each normalized to 0–10 (10 = strong):
- **Fuel** = (Q3 + Q4) / 7 × 10
- **Rhythm** = (Q5 rhythm pts + Q6) / 7 × 10
- **Flow** = (Q8 + Q9 + Q10) / 11 × 10
- **Rest** = (Q11 + Q12 + Q13 + Q5 rest adj.) / 10 × 10, floor 0
- **Comfort** = (Q7 + Q14) / 7 × 10

**Profile** = the lowest dimension. Tie-break order: Fuel, Rhythm, Flow, Rest, Comfort. If every dimension ≥ 7 → **Steady Burner**.

**Protein target shown on result:** weight ranges map to midpoints (120, 145, 175, 205, 235 lb) → kg → × 1.0 to 1.2 g/kg/day, displayed as "about {low}–{high} grams of protein a day, roughly 25–30 grams per meal" (PROT-AGE study group recommendation for healthy older adults). Always add: "If you have kidney disease, ask your doctor before eating more protein." If weight skipped: "about 25–30 grams at each meal".

#### Result template
```
[Kitchen Card, printable, Sun Yoon's handwriting font for her note only; body text in Atkinson Hyperlegible]
Your five scores: Fuel {x}/10 · Rhythm {x}/10 · Flow {x}/10 · Rest {x}/10 · Comfort {x}/10 (horizontal bars: Jade fill, Ink outline, Ink labels)
Your profile: {name}
Sun Yoon's note: {1–2 sentences}
Your protein target: {n}
```

#### B1. Running on Toast (Fuel lowest)
**Headline:** You're running your body on toast and coffee. No wonder it's tired.
**Sun Yoon's note:** "I love toast. But toast is not breakfast. Toast is a plate."
**Body:** Your Fuel score is {x}/10. Most of your meals are light on protein, and breakfast especially. As we get older, our muscles need more protein per meal to maintain themselves than they did when we were young, and many older adults eat most of their protein at dinner. Spreading it out, about 25–30 grams at each meal, is one of the simplest changes you can make, and it pairs with strength exercise: food gives your muscles the material, exercise tells them to use it.
**Your 7-day kitchen plan:**
- Days 1–2: Add one protein to breakfast: two eggs, or a cup of Greek yogurt, or Sun Yoon's silken tofu with soy and scallion
- Days 3–4: Make lunch "palm + fist": a palm of protein, a fist of vegetables
- Day 5: Cook a pot of her doenjang tofu stew (24g protein a bowl), eat it twice
- Day 6: Snack swap: cottage cheese or a boiled egg instead of crackers
- Day 7: Count it once: write down your protein for one day. Most people are surprised
**Tonight's recipes:** Steamed egg custard (gyeran-jjim), 13g/bowl; Congee with shredded chicken and ginger, 22g/bowl; Doenjang tofu stew, 24g/bowl.
**Offer:** "Sun Yoon's full kitchen, 3 new recipes every Sunday, the *Gut Reset with Sun Yoon* 12-week program, and Strong Years, all inside Strong Years." Button: **Start 7 days for $1**. Alt link: **Food first: Sun Yoon's Strong Kitchen, $17 (includes 7 days of Strong Years).**

#### B2. The 2 PM Slump (Rhythm lowest)
**Headline:** You're not lazy. Your lunch is putting you to sleep.
**Sun Yoon's note:** "After lunch, Chang Yin walks around the block. Then he tells everyone he feels young. It's the walk, not him."
**Body:** Your Rhythm score is {x}/10. A big, starchy meal followed by sitting is a common recipe for an afternoon crash. Research in adults shows that even a short, easy walk after eating, as little as 2 to 5 minutes and better at 10 to 15, lowers the rise in blood sugar after the meal compared with sitting. Many people notice they feel more awake too.
**Your 7-day plan:**
- Every day: a 10-minute walk (or 10 minutes of Chang Yin's After-Meal Movement indoors) within 30 minutes of your biggest meal
- Days 1–3: Build lunch in this order: vegetables and protein first, rice or bread last
- Days 4–5: Swap half your white rice for Sun Yoon's mixed-grain rice (japgokbap)
- Day 6: Move your biggest meal earlier in the day if you can
- Day 7: Score your afternoon energy 1 to 5 each day, and compare with day 1
**Tonight's recipes:** Japgokbap mixed-grain rice; Steamed fish with ginger and scallion; Spinach namul (sesame spinach).
**Offer:** as B1, with "After-Meal Movement track inside" emphasized.

#### B3. Slow River (Flow lowest)
**Headline:** Things are moving slowly. Let's get the river running again, gently.
**Sun Yoon's note:** "Everybody wants to talk about energy. Nobody wants to talk about the bathroom. I will talk about the bathroom."
**Body:** Your Flow score is {x}/10: low fiber, low fluids, or not-so-regular bathroom trips. Adults over 50 are generally advised to get about 21 grams of fiber a day (women) or 30 grams (men), and most get far less. Add fiber slowly, over two to three weeks, with more water, or you'll feel bloated. Walking helps too. If constipation is new for you, lasts, or comes with pain or blood, see your doctor.
**Your 7-day plan:**
- Day 1: Add one glass of water or barley tea (boricha) with breakfast and lunch
- Days 2–3: Add one serving: a pear, a handful of berries, or a spoon of cooked beans
- Days 4–5: Seaweed soup (miyeok-guk) or a vegetable soup once a day
- Day 6: Add a 10-minute walk after breakfast
- Day 7: One mixed-grain meal (oats, barley or japgokbap)
**Tonight's recipes:** Miyeok-guk seaweed soup; Boricha barley tea; Oat-and-pear warm breakfast bowl.
**Offer:** Primary **Start 7 days for $1** (*Gut Reset with Sun Yoon* program featured); alt $17 Strong Kitchen.

#### B4. Wired-Tired (Rest lowest)
**Headline:** Tired all day, wide awake at night. Let's fix the evening first.
**Sun Yoon's note:** "You drink coffee at 3 o'clock and then you blame the moon."
**Body:** Your Rest score is {x}/10. Caffeine stays in the body for many hours, so an afternoon coffee can still be working at bedtime. Alcohol can help you fall asleep but tends to break up sleep later in the night. A calmer evening routine, a consistent wake time, and daytime movement and daylight all help. If you snore loudly, stop breathing at night, or feel sleepy while driving, please talk to your doctor; these can be signs of a sleep condition that needs a proper check.
**Your 7-day plan:**
- Day 1: Last caffeine before noon
- Day 2: Morning light: 10 minutes outside within an hour of waking
- Days 3–4: Chang Yin's Sleep Wind-Down session (10 minutes, slow-exhale breathing, 4 in, 6 out)
- Day 5: Same wake time every day this week, including the weekend
- Day 6: Warm, light dinner 3 hours before bed (Sun Yoon's congee)
- Day 7: Note your nights 1–5 and compare with day 1
**Tonight's recipes:** Plain congee with egg; Jujube and ginger tea (a warm caffeine-free evening drink; kitchen tradition, not a sleep treatment); Soft tofu soup.
**Offer:** **Start 7 days for $1** (Sleep Wind-Down track emphasized).

#### B5. Tender Belly (Comfort lowest)
**Headline:** Your stomach wants smaller, softer and slower. Let's give it that.
**Sun Yoon's note:** "Eat like you're not in a hurry. You're not in a hurry."
**Body:** Your Comfort score is {x}/10: frequent bloating or fullness, or chewing that's harder than it used to be. Eating smaller meals, slowing down, and choosing soft, moist, protein-rich foods often helps comfort and makes sure you still get enough protein. If chewing is getting harder, a dentist visit can make a big difference. If bloating is new, persistent or painful, please talk to your doctor.
**Your 7-day plan:**
- Days 1–2: Put the fork down between bites; aim for 20 minutes per meal
- Days 3–4: Four smaller meals instead of three big ones
- Day 5: Soft protein day: steamed egg custard, soft tofu, fish congee
- Day 6: Keep a note of foods that seem to bother you (no cutting out whole food groups on your own)
- Day 7: A gentle walk after your biggest meal
**Tonight's recipes:** Gyeran-jjim steamed egg custard; Soft tofu with warm soy dressing; Fish congee.
**Offer:** Primary **Start 7 days for $1** (soft-food versions in every weekly recipe set); alt $17 Strong Kitchen.

#### B6. Steady Burner (all dimensions ≥ 7)
**Headline:** Your kitchen is in good shape. Now your legs need to catch up with your plate.
**Sun Yoon's note:** "Good. Don't get proud. Go see Chang Yin."
**Body:** You're eating protein, fiber and water, moving after meals and sleeping reasonably well. The next thing most people at this stage are missing is strength training. Take Chang Yin's free Strength Age test next; it takes three minutes.
**Buttons:** **Find my Strength Age (free)** (primary, Jade) → quiz A with email prefilled; **Start 7 days for $1** (secondary).

#### Offer routing summary

| Profile | Primary offer | Secondary | Emphasized inside membership | Bump / upsell ladder (5.2–5.3) |
|---|---|---|---|---|
| A-P1 Steady Oak | $1 trial | $7 Reset | Strong/Iron track, *Strong at 70* | Full ($9 bump → $27 keep-forever program → $29 kit / $7 printables) |
| A-P2 Rooted but Rusty | $1 trial | $7 Reset | Steady track | Full |
| A-P3 Wobbly Foundations | $1 trial | $7 Reset (Steady Feet edition) | *Balance & Steady Feet* program, Steady Feet track | Full (kit = loops, not balance devices) |
| A-P4 Stiff Engine | $1 trial | $7 Reset (joint-friendly) | *Back Strong*, Knees & Stairs track | Full ($27 keep-forever *Back Strong* featured) |
| A-P5 Quiet Slide | $1 trial | $7 Reset | Rebuild → Steady, Chair Builder | Full |
| A-P6 Gentle Restart | Save plan (free) | $1 trial | Rebuild track | None: no bump, no upsells |
| B1–B5 | $1 trial (test: $17 Strong Kitchen as primary) | $17 Strong Kitchen | *Gut Reset with Sun Yoon* + matching track | Full (bump in Sun Yoon's voice) |
| B6 Steady Burner | Quiz A | $1 trial | Strength | Full |

---

## 4. ManyChat DM flows (Instagram + Facebook Messenger)

### 4.1 Global settings (apply to all 14 flows: the 11 standard flows, JOIN §4.17, WAITLIST §4.18 in runway mode, BOOK §4.19 from checkout open)

- **Channels:** Instagram (comment → DM works worldwide) and Facebook (comment → Messenger works). TikTok US: comment triggers unavailable, so reuse the DM copy below in TikTok's business keyword auto-replies where available.
- **Trigger matching:** "message contains word", case-insensitive, on all Reels and posts, plus Story replies and direct DMs. Include variants: e.g. STRONG = `strong, strength, stronger, strong!, strong please, 💪`. Misspellings seen in this demographic are common; add at least 3 per keyword (`stong, strog, srong`).
- **De-duplication:** if the contact received the same flow in the last 24 hours, skip the DM and post only the public reply. If they received a different flow, send it (people often comment several keywords, and each is a real interest signal; tag them all).
- **Tags written:** `kw_strong`, `kw_back`, `kw_sleep`, `kw_soup`, `kw_gut`, `kw_balance`, `kw_knees`, `kw_breath`, `kw_begin`, `kw_test`, `kw_family`, `kw_join`, `kw_waitlist` (§4.18, runway mode), `kw_book` (§4.19), plus `src_ig`/`src_fb`, `post_{id}`. Custom fields: `first_kw`, `kw_count`, `email`, `phone`, `mc_id`.
- **Links:** always to our domain with `?mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign={keyword}`. Never send a link in the public reply.
- **Launch link rule (CANON UPDATE 3, Oct 1 2026; replaces the blitz-mode rule):** there is no $1 trial. Every "7 days for $1" offer link and button written in §4.3–4.13 is read as `{{DOMAIN}}/b?t={keyword}` with the button text "Get the starter books" (the `/b` redirect lands the visitor on their sticky cell: the launch default is "$12 today = books + first month, then $25/mo"; the test cell is the $12 books alone), and any price line uses the §4.19 wording. Lesson pages and quizzes are unchanged. SMS capture (§4.16) stays off until 10DLC / toll-free approval. During the runway the §4.18 runway link rule applies instead.
- **24-hour window:** all automated promotional messages happen inside 24 hours of the person's last interaction. After that, only email/SMS follow up. Human-agent replies may use the HUMAN_AGENT tag (up to 7 days) only for genuine human conversations, never automation.
- **Persona rule:** the DM sender is "Chang Yin's team assistant (automated)". It quotes Chang Yin or Sun Yoon ("Chang Yin's note: …") but never pretends to be a person, never claims to remember someone personally, and never role-plays a relationship.
- **Disclosure:** the first message of every flow contains the AI line. Profile "About" in ManyChat and the IG account bio carry it too.
- **Global intents** (active in every conversation, override flows):
  - `human`, `person`, `agent`, `talk to someone` → human inbox, reply: "Got it. A real person on our team will reply here, usually within a day (Mon–Fri)."
  - `real?`, `is he real`, `are you real`, `AI` → "Good question, and you deserve a straight answer: Chang Yin and Sun Yoon are AI characters our team created. They're not real people. What's real is the content: [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: every session is reviewed by `[PT NAME]`, a licensed physical therapist, and every recipe by `[RD NAME]`, a registered dietitian.] FALLBACK: "every session and recipe is built from published exercise and nutrition guidelines for older adults." Want to see how we make it?" [How we make this]
  - `price`, `cost`, `how much` → "Strong Years is 7 days for $1, then {{PRICE}} a month, and you can cancel online anytime in at most two screens{{IF_SMS: or by texting CANCEL}}. There's also the $7 7-Day Strength Reset (yours to keep; it includes 7 days of Strong Years, then {{PRICE}}/month unless you cancel), and gifts for parents from $49 that never auto-renew." [See the options]
    - **Blitz mode version (replaces the line above while blitz mode is on):** "Founding membership is {{FOUNDING_PRICE}} a month. Your first month is charged today, and it renews monthly at the same price until you cancel. The founding price stays the same for as long as you're subscribed, for the first 5,000 members. 14-day money-back guarantee, and you can cancel online anytime in two screens. Gifts for parents start at $49 and never auto-renew." [See the founding membership] → `{{DOMAIN}}/join?mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=price`
  - `cancel`, `refund`, `stop charging` → "You can cancel right now, online: [Cancel link to account]. It takes two screens at most. If you'd like a refund, reply REFUND and a person will take care of it today." (Membership refund within 14 days is self-serve in every mode, one per person; add-on refunds on request; route to the human queue with priority.)
  - `stop`, `unsubscribe` → unsubscribe from ManyChat sequences, confirm: "Done. You won't get more automated messages from us here."
  - Crisis and distress protocol: see 4.14.

### 4.2 Public comment replies (rotating pool; ManyChat picks randomly)

Generic (any keyword):
1. "Sent it to your messages, {first_name}. Check your inbox."
2. "It's in your DMs now. Start with the chair against a wall."
3. "Sent. Go slowly the first time."
4. "Check your messages. Chang Yin says: sit tall first."
5. "In your inbox, {first_name}. If you don't see it, check Message Requests."

Keyword-flavored (add 2 per keyword to the pool for that keyword):
- STRONG: "Sent. Eight minutes, one chair." / "In your messages. Arms crossed, stand tall."
- BACK: "Sent. Try it before breakfast tomorrow." / "In your DMs. Gentle first, always."
- SLEEP: "Sent. Save it for tonight, 30 minutes before bed." / "In your messages. Breathe out longer than in."
- SOUP: "Sun Yoon sent the recipe. Check your messages." / "In your DMs. She says don't skip the garlic."
- BALANCE: "Sent. Stand by the counter for this one." / "In your inbox. Kitchen counter, one hand hovering."
- KNEES: "Sent. Bottom stair only for now." / "In your DMs. Slow and steady."
- BREATH: "Sent. Four seconds in, six out." / "In your messages. Try it right now."
- BEGIN: "Sent you the start menu. Pick the one that sounds like you." / "In your DMs. Start there."
- GUT: "Sun Yoon sent her 2-minute check. Be honest with her." / "In your messages. Kimchi is food, not magic."
- TEST: "Sent. One chair, 30 seconds." / "In your DMs. Chair against the wall first."
- FAMILY: "Sent you the family options." / "In your messages. Sun Yoon writes the card."
- JOIN (blitz mode): "Sent you the founding details and the full terms." / "In your DMs. The seat count on the page is real."

### 4.3 STRONG flow ("The 8-Minute Chair Builder")

**DM 1 (immediate):**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Quick note before anything: Chang Yin is an AI character. Our sessions are real; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions are reviewed by a licensed physical therapist.] FALLBACK: "our sessions are built on published exercise guidelines for older adults."
>
> You asked for the 8-minute Chair Builder, the routine that trains the muscles you use to stand up from a chair. Want it?
> [Button: Yes, send it]

**DM 2 (on button tap):**
> Here it is: {{DOMAIN}}/s/l1
>
> What you need: a sturdy chair against a wall and a kitchen counter.
> Chang Yin's note: "Do it slowly the first time. If you need your hands, use your hands. That's where we start, not where we stay."
>
> Safety: stop if anything hurts sharply or you feel dizzy or short of breath. If you've had a recent fall, surgery or heart problem, check with your doctor first.
>
> Want the large-print printable card by email too?
> [Quick reply: Yes, email it] [Quick reply: No thanks]

**Email capture (if "Yes, email it"):**
> What's your email? (Tap it below if Instagram suggests it.)
> [IG email quick-reply autofill] → validate → save to `email`
> Confirmation: "Sent to {email}. By sharing your email you'll get emails from Strong Years, including your printable card and short daily tips. Unsubscribe anytime with one click."

**If "No thanks":** "No problem. The routine is all yours at the link above."

**Nudge (+20 minutes, only if link not clicked):**
> {first_name}, the Chair Builder is here whenever you're ready: {{DOMAIN}}/s/l1
> It's 8 minutes. You can do it in your pajamas.

**Check-in (+22 hours, inside the window):**
> Did you try the Chair Builder? How did your legs feel?
> [Button: Easy] [Button: Hard] [Button: Haven't tried yet]

- **Easy →** "Good sign. Then you're ready to find out your Strength Age: a free 3-minute test with the same chair. You'll get a number and a 7-day plan. {{DOMAIN}}/q/a" [Button: Take the test]
- **Hard →** "That's honest, and very normal. Here's the fully seated version: {{DOMAIN}}/s/l1c. Chang Yin's note: 'Hard means we found the right place to start.' When you're ready, the free Strength Age test will build your plan from exactly where you are." [Button: Take the test]
- **Haven't tried yet →** "Here's the 3-minute version for today: {{DOMAIN}}/s/l1s. Three minutes is still a win." [Button: Open it]

After the check-in branch, if they tapped the test link but didn't finish: nothing more in DM (email/SMS handles it).

**Lesson page `/s/l1` structure:** disclosure strip → video (8 min, captions, track switch: Rebuild / Steady / Strong) → "Print the card" (email-gated if not captured) → "What's your Strength Age?" block with quiz button → a short "What happens inside Strong Years" strip → $1 trial button. Pixel event: `ln_view` (no condition words).

### 4.4 BACK flow ("Morning Unlock")

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions are reviewed by a licensed physical therapist.] FALLBACK: "our sessions are built on published exercise guidelines for older adults."
>
> You asked for Morning Unlock, the 7-minute routine for a stiff back first thing in the morning. It starts in bed. Send it?
> [Button: Yes, send it]

**DM 2:**
> Here it is: {{DOMAIN}}/s/l2
>
> Part 1 is done lying in bed, part 2 standing at your kitchen counter. Move in a range that feels easy; stiffness usually loosens as you go.
>
> Please see a doctor promptly, rather than exercising, if back pain comes with numbness in your groin or inner thighs, trouble controlling your bladder or bowels, fever, weakness in a leg, or started after a fall or accident.
>
> Want the printable card by email?
> [Yes, email it] [No thanks]

**Nudge (+20 min):** "{first_name}, Morning Unlock is best tomorrow before breakfast. Save this link: {{DOMAIN}}/s/l2"

**Check-in (+22 h):**
> Did you try Morning Unlock? How's your back this morning?
> [A bit looser] [About the same] [Haven't tried yet]

- **A bit looser →** "Good. Stiffness likes movement. The next step is strengthening the muscles that hold you up, so mornings keep getting easier. The free Strength Age test builds your plan: {{DOMAIN}}/q/a" [Take the test] [Or: Try the Back & Posture track, 7 days for $1]
- **About the same →** "That's common on day one; it usually takes a week or two of doing it daily. Try it three more mornings in a row. If it's getting worse, not better, check with your doctor or a physical therapist. Here's the link again: {{DOMAIN}}/s/l2"
- **Haven't tried →** "Here's a 3-minute version you can do right now in your chair: {{DOMAIN}}/s/l2s"

### 4.5 SLEEP flow ("Sleep Wind-Down, Night 1")

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: everything we share is reviewed by licensed professionals.] FALLBACK: "everything we share is built on published guidelines for older adults."
>
> You asked for the Sleep Wind-Down: 10 minutes of slow breathing and gentle stretches to do 30 minutes before bed. Send it?
> [Yes, send it]

**DM 2:**
> Here it is: {{DOMAIN}}/s/l3 (there's an audio-only version too, so you can keep the lights low)
>
> The one thing to remember: breathe out longer than you breathe in. Four seconds in, six seconds out.
>
> Sun Yoon's note: "And no coffee after lunch. I'm not joking."
>
> If you snore loudly, stop breathing in your sleep, or feel sleepy while driving, please talk to your doctor. Those are worth a proper check.
>
> Want the bedtime card by email?
> [Yes, email it] [No thanks]

**Nudge (+20 min):** "Save this for tonight, {first_name}: {{DOMAIN}}/s/l3. Set a reminder for 30 minutes before bed."

**Check-in (+22 h):**
> How did last night go?
> [Better than usual] [Same] [Didn't try yet]

- **Better →** "Lovely. One night is a start; a routine is what lasts. Strong Years has 10 Sleep Wind-Down sessions that rotate, plus daytime strength and walking, which also help sleep. 7 days for $1: {{DOMAIN}}/start?t=sleep" [Try it for $1] [Take the free Strength Age test]
- **Same →** "Sleep usually changes over a week or two, not one night. Try the Wind-Down 5 nights in a row, keep the same wake-up time, and get outside in the morning light. Here's Sun Yoon's 2-minute Gut & Energy Check too, since late caffeine and big dinners are common culprits: {{DOMAIN}}/q/b"
- **Didn't try →** "Tonight then. Here's the audio-only version: {{DOMAIN}}/s/l3a"

### 4.6 SOUP flow (Sun Yoon's "Three Soups")

**DM 1:**
> Hi {first_name}! This is Sun Yoon's team assistant (automated). Sun Yoon is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: her recipes are checked by a registered dietitian.] FALLBACK: "her recipes are built on published nutrition guidance for older adults."
>
> You asked for the soup. She's sending three: seaweed soup, doenjang tofu stew, and chicken-ginger congee. Cheap, high in protein or fiber, and soft to eat. Want them?
> [Yes, send the recipes]

**DM 2:**
> Here they are: {{DOMAIN}}/s/l4
>
> Sun Yoon's note: "These are what I make when someone in the house is tired. They are not medicine. They are dinner. Good dinner."
>
> Where should I send the printable recipe cards?
> [Email them to me] [No thanks]

**Nudge (+20 min):** "Sun Yoon wants to know if you've looked at the recipes yet. (She will ask again.) {{DOMAIN}}/s/l4"

**Check-in (+22 h):**
> Which soup are you making first?
> [Seaweed soup] [Doenjang tofu] [Congee] [Not cooking this week]

- **Any soup →** "Good choice. Sun Yoon has a 2-minute quiz that tells you what's draining your energy after meals, and gives you a 7-day kitchen plan: {{DOMAIN}}/q/b" [Take the Gut & Energy Check] [Get all 60 recipes: Sun Yoon's Kitchen, $17]
- **Not cooking →** "Then here's her no-cook high-protein breakfast (3 minutes, 25 grams of protein): {{DOMAIN}}/s/l4b. And her 2-minute kitchen check when you have a moment: {{DOMAIN}}/q/b"

### 4.7 BALANCE flow ("Steady Feet + the 10-second test")

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions are reviewed by a licensed physical therapist.] FALLBACK: "our sessions are built on published exercise guidelines for older adults."
>
> You asked about balance. We'll send two things: a 10-second test you can do at your kitchen counter, and an 8-minute Steady Feet session. Ready?
> [Yes, send both]

**DM 2:**
> Here they are: {{DOMAIN}}/s/l5
>
> The test: stand at your kitchen counter, one hand hovering above it. Put one foot directly in front of the other, heel touching toe. Can you hold it for 10 seconds without grabbing the counter?
>
> It's one of the four positions in a standard balance test used in senior fitness research. If you can't hold it yet, you're not alone: balance is one of the most trainable things there is, and it often improves faster than strength. Please mention it to your doctor at your next visit too.
>
> [Button: I held it 10 seconds] [Button: I couldn't] [Button: I'll try later]

- **Held it →** "Nicely done. Try the next one: standing on one foot, 10 seconds, still next to the counter. Then find your full Strength Age: {{DOMAIN}}/q/a"
- **Couldn't →** "Thank you for trying, and for being honest. The Steady Feet session at that link starts exactly where you are. Do it at the counter every day this week and test again on day 7. Many people improve quickly. Want the full picture? The free Strength Age test takes 3 minutes: {{DOMAIN}}/q/a"
- **Later →** Nudge at +20 min: "Kitchen counter, one hand hovering, heel to toe, 10 seconds. That's all. {{DOMAIN}}/s/l5"

Then email capture prompt (same pattern), then check-in +22 h:
> Did you do the Steady Feet session?
> [Yes] [Not yet]
- **Yes →** "Balance improves with daily practice. In Strong Years there's a balance day every Wednesday and a full Steady Feet track, plus a retest every month so you can see it change. 7 days for $1: {{DOMAIN}}/start?t=balance" [Try it for $1] [Free Strength Age test]
- **Not yet →** "Here's a 4-minute version: {{DOMAIN}}/s/l5s"

### 4.8 KNEES flow ("The Step Builder")

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions are reviewed by a licensed physical therapist.] FALLBACK: "our sessions are built on published exercise guidelines for older adults."
>
> You asked for the knee routine: The Step Builder, 10 minutes, done at the bottom stair while holding the rail. It trains the muscles around your knees that make stairs easier. Send it?
> [Yes, send it]

**DM 2:**
> Here it is: {{DOMAIN}}/s/l6
>
> The rule for knees: mild discomfort that settles by tomorrow is usually okay. Sharp pain, swelling that lasts, or pain that's worse the next day means ease off. If you've had a knee replaced, follow your surgeon's or physical therapist's instructions first.
>
> Chang Yin's note: "Bottom stair only. We are not climbing mountains yet."
>
> Printable card by email?
> [Yes, email it] [No thanks]

**Nudge (+20 min):** "The Step Builder is waiting: {{DOMAIN}}/s/l6. Bottom stair, hold the rail, 10 minutes."

**Check-in (+22 h):**
> How did your knees feel today, after trying it?
> [Fine or better] [A bit sore] [Didn't try yet]

- **Fine →** "Great. Stairs get easier as the muscles around the knee get stronger; that takes a few weeks of doing it most days. The Knees & Stairs track in Strong Years has 8 sessions that progress when you're ready. 7 days for $1: {{DOMAIN}}/start?t=knees" [Try it for $1] [Free Strength Age test]
- **A bit sore →** "Mild soreness the next day is common when muscles work in a new way. Try the chair version today, and go back to the step tomorrow: {{DOMAIN}}/s/l6c. If it's sharp pain or swelling, rest it and check with your doctor or physical therapist."
- **Didn't try →** "Here's a seated knee routine you can do right now: {{DOMAIN}}/s/l6c"

### 4.9 BREATH flow ("The 4–6 Breath")

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions are reviewed by licensed professionals.] FALLBACK: "our sessions are built on published guidelines for older adults."
>
> You asked for the breathing practice: 5 minutes of slow breathing, four seconds in, six seconds out, with Chang Yin counting. Send it?
> [Yes, send it]

**DM 2:**
> Here it is: {{DOMAIN}}/s/l7
>
> Try it right now, sitting down: breathe in through your nose for 4, out through your mouth slowly for 6. Five rounds.
>
> Slow breathing with a longer exhale is widely used to help people feel calmer. If you ever feel lightheaded, go back to normal breathing.
>
> If you're short of breath at rest, have chest pain, or breathing trouble is new, please call your doctor, or 911 if it's severe.
>
> Want the pocket card by email?
> [Yes, email it] [No thanks]

**Nudge (+20 min):** "Five minutes, one chair, four in, six out: {{DOMAIN}}/s/l7"

**Check-in (+22 h):**
> Did the breathing help you settle?
> [Yes] [Not really] [Didn't try]

- **Yes →** "Good. Try it twice a day this week: once in the morning, once before bed. Strong Years has a Breath & Calm track, a breath + qigong flow every Friday, and a short breath finish at the end of every Daily Practice. 7 days for $1: {{DOMAIN}}/start?t=breath" [Try it for $1] [Free Strength Age test]
- **Not really →** "That's fair; it takes practice. Try it lying down tonight with a hand on your belly. And movement helps calm too; Chang Yin's gentle tai chi flow is here: {{DOMAIN}}/s/l7t"
- **Didn't try →** "Right now, 60 seconds: in for 4, out for 6. Six times. That's it."

### 4.10 BEGIN flow (the "HEAL" equivalent: "Where should I begin?")

This is the general-purpose keyword used on broad, emotional, or multi-topic posts, and in the bio ("DM us BEGIN"). It brings Yang Mun's best page block into the DM.

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin and Sun Yoon are AI characters; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: everything we share is reviewed by a licensed physical therapist and a registered dietitian.] FALLBACK: "everything we share is built on published exercise and nutrition guidelines for older adults."
>
> Chang Yin always asks the same question first: where should you begin? Tap the one that sounds most like you.
> [I push on the armrests to stand up]
> [My knees complain on the stairs]
> [I don't feel steady on my feet]
> [My back is stiff every morning]
> [I lie awake at night]
> [I'm tired after I eat]
> [I haven't exercised in years]
> [Buying for my mom or dad]
> [Not sure, test me]

Routing:
- Armrests → STRONG DM 2
- Knees → KNEES DM 2
- Not steady → BALANCE DM 2
- Back → BACK DM 2
- Awake → SLEEP DM 2
- Tired after eating → GUT DM 2 (Sun Yoon's Gut & Energy Check)
- Haven't exercised → "Then we start seated, and slowly. Day 1: The Gentle Start, 8 minutes in a chair: {{DOMAIN}}/s/l0. Please check with your doctor first if you've had heart problems, dizziness, a recent fall or surgery." + email capture
- Buying for mom or dad → FAMILY DM 1 branch "My mom or dad"
- Not sure → TEST DM 2

Each branch then follows that keyword's nudge and check-in logic.

### 4.11 GUT flow (Sun Yoon's "Gut & Energy Check", modelled on SOUP)

**DM 1:**
> Hi {first_name}! This is Sun Yoon's team assistant (automated). Sun Yoon is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: her recipes are checked by a registered dietitian.] FALLBACK: "her recipes are built on published nutrition guidance for older adults."
>
> You asked about your gut. Sun Yoon says the honest answer starts with two minutes of questions, not a magic drink. She'll send her Gut & Energy Check and her 3-day gentle-fiber starter. Ready?
> [Button: Yes, send it]

**DM 2:**
> Here's her check: {{DOMAIN}}/q/b (2 minutes, then a 7-day kitchen plan and three recipes for tonight).
> And her starter: {{DOMAIN}}/s/l8. Add fiber slowly over two to three weeks, drink more water with it, and take a 10-minute walk after your biggest meal.
>
> Sun Yoon's note: "Kimchi is food, not medicine. Delicious food. Eat it because it's good, not because somebody on the internet promised you a miracle."
>
> One important thing first: if you've had blood in your stool, black stools, weight loss without trying, trouble swallowing, or bathroom changes lasting more than a few weeks, please call your doctor this week. No recipe replaces that check.
>
> Want the starter card by email?
> [Yes, email it] [No thanks]

**Nudge (+20 min, only if neither link clicked):** "Sun Yoon is waiting for your answers. She's patient. Mostly. {{DOMAIN}}/q/b"

**Check-in (+22 h):**
> Did you take Sun Yoon's check?
> [Yes, I got my plan] [Not yet] [I'd rather just cook]

- **Got my plan →** "Good. Days 1 to 3 of your plan are in your email. The full 12-week *Gut Reset with Sun Yoon* is inside Strong Years, with three new recipes every Sunday and Strong Years. 7 days for $1: {{DOMAIN}}/start?t=gut" [Try it for $1] [Food first: Sun Yoon's Strong Kitchen, $17]
- **Not yet →** "Two minutes, fourteen questions, one honest woman: {{DOMAIN}}/q/b"
- **Rather cook →** SOUP DM 2 (the Three Soups).

Quiz answers from this flow stay first-party only and are never sent to Meta (OFFER.md 2.6).

### 4.12 TEST flow (→ Strength Age quiz)

**DM 1:**
> Hi {first_name}! This is Chang Yin's team assistant (automated). Chang Yin is an AI character; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions are reviewed by a licensed physical therapist.] FALLBACK: "our sessions are built on published exercise guidelines for older adults."
>
> You asked for the test. It's the Strength Age test: a 30-second chair stand and a 10-second balance check at your kitchen counter, plus a few questions. 3 minutes, free, and you get a 7-day plan. Send it?
> [Button: Yes, test me]

**DM 2:**
> Here it is: {{DOMAIN}}/q/a
>
> You'll need a sturdy chair pushed against a wall, a kitchen counter, and ideally someone nearby. It starts with a few safety questions, and it skips the standing parts if they aren't right for you today.
>
> Chang Yin's note: "I'll go first. You go second. Measure twice, lift once."
>
> Your result and plan are emailed to you when you finish.

(If the contact already has the `q_a_complete` tag via the quiz webhook: "You've already got your Strength Age: {SA}. Here's your plan again: {result_link}. Your next retest is on the 1st.")

**Nudge (+20 min, if quiz not started):** "3 minutes, one chair, one counter: {{DOMAIN}}/q/a"

**Check-in (+22 h):**
> Did you get your Strength Age?
> [Younger than my birthday] [About the same] [Older] [Haven't done it yet]

- **Younger →** "Nicely done. Now let's keep it. Your Daily Practice keeps you there, with a retest every month so you can watch it. 7 days for $1: {{DOMAIN}}/start?t=test" [Try it for $1]
- **About the same →** "Average at our age usually means the slide has started. The good news: it responds fast. Your plan starts on the Steady track. 7 days for $1: {{DOMAIN}}/start?t=test"
- **Older →** "Thank you for doing it honestly. That's the most fixable number there is. Start on the Rebuild track, chair-based, and retest on the 1st. 7 days for $1: {{DOMAIN}}/start?t=test"
- **Haven't done it →** "Whenever you're ready: {{DOMAIN}}/q/a. Chair against the wall first."

### 4.13 FAMILY flow (→ gift-a-membership page)

**DM 1:**
> Hi {first_name}! This is the Strong Years team assistant (automated). Chang Yin and Sun Yoon are AI characters; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: our sessions and recipes are reviewed by a licensed physical therapist and a registered dietitian.] FALLBACK: "our sessions and recipes are built on published guidelines for older adults."
>
> You asked about Strong Years for your family. Who's it for?
> [My mom or dad] [My partner and me] [My parents and me]

- **My mom or dad →**
  > Give Mom & Dad Strong Years: **3 months for $49 or 12 months for $119**, prepaid, and it **never auto-renews**. They get a welcome card from Sun Yoon (by email, or printed and mailed), a new session with Chang Yin every morning with a chair-based version of everything, and Sun Yoon's recipes. If they agree, you get a monthly note like "Mom did 18 sessions." Their numbers stay private unless they choose to share.
  > {{DOMAIN}}/gift
  > [See gift options] [Do the chair test with them first] [Help me set it up]
  - "Do the chair test with them first" → {{DOMAIN}}/q/a?mode=helper ("Do it together on a video call.")
  - "Help me set it up" → human inbox: "A real person on our team will help you set it up, usually within a day."
- **My partner and me →** "Start 7 days for $1, then {{PRICE}}/month, and add your partner for $8/month. They get their own level, Strength Age and progress. {{DOMAIN}}/start?t=family" [Start for $1]
- **My parents and me →** both messages above, gift first.

**Check-in (+22 h, if no gift purchase and no trial):**
> Did you find the right option?
> [Yes, all done] [Still deciding] [I have a question]
- **Still deciding →** "Most people start with 3 months for $49. If your parent loves it, they can continue on their own card later, and only if they agree to it. Nothing renews by surprise. {{DOMAIN}}/gift"
- **Question →** human inbox.

Occasion boosts: in the 3 weeks before Mother's Day, Father's Day, Grandparents Day (September) and the holidays, DM 1 adds one line naming the occasion and the order-by date for printed cards.

### 4.14 Distress, crisis and confessional messages

Yang Mun's comments are full of confessional stories (estranged children, grief, heartbreak). Our audience will do the same in DMs. An automated sales reply to grief is both cruel and a brand risk. Rules:

1. **Keyword/AI-classifier detection** on all inbound DMs: self-harm and suicide language (e.g. "want to die", "end it", "no reason to live", "kill myself", "hurt myself"), medical emergency language ("chest pain now", "can't breathe", "stroke", "fell and can't get up"), abuse language, and grief/loneliness language ("my husband passed", "all alone", "my kids don't talk to me").
2. **Crisis (self-harm)** → pause all automation for this contact, send immediately:
   > I'm an automated assistant, and I'm really glad you wrote. What you're feeling matters. Please reach out to someone right now: call or text **988** (Suicide & Crisis Lifeline, free, 24/7). If you're in danger, call **911**. A person on our team reads messages from 7am to 11pm Eastern and will read yours (after 11pm, first thing in the morning).
   During staffed hours (7:00–23:00 ET), page `#crisis`: a human acknowledges within 15 minutes and follows up within 1 hour. Outside staffed hours the automated reply above is the response until 7:00 ET; never imply otherwise. Log every case (SB 243 reporting).
3. **Medical emergency** → "I'm an automated assistant. If this is happening now, please call 911 right away." Pause automation, alert human.
4. **Grief / loneliness / family pain** → pause sales flows for 7 days, send:
   > Thank you for telling us this. I'm an automated assistant, so I'll pass your message to a real person on our team who reads these. You're not alone in feeling this way; many people in our community have written something similar.
   A human replies within 24 hours with a short, kind, non-sales note. Optional: point to the Eldercare Locator (1-800-677-1116) or the Institute on Aging's Friendship Line for adults 60+ (1-888-670-1360; verify the number before launch) for loneliness; 988 if any risk language.
5. Never let an AI character "comfort" someone as if they were a friend, and never reply as Chang Yin or Sun Yoon to personal pain. The human replies as "[First name] from the Strong Years team". No therapy-style advice from any AI surface (Illinois WOPR Act); grief and relationship topics get the rule 4 text and, if there's any risk language, the crisis-resources line.
6. The full protocol is published at `{{DOMAIN}}/safety` (California SB 243) and matches this section word for word.

### 4.15 Facebook Messenger differences

- Same flows. Messenger allows a "Marketing Messages" opt-in (where available in the account): after the check-in, offer "Want one short tip from Chang Yin each week here in Messenger?" [Yes, weekly] → subscribes to Meta's marketing messages topic "Weekly tip". This gives a compliant channel past 24 hours.
- Facebook audience skews older than Instagram for 65+; expect higher DM→quiz conversion and lower email-typing ability, so offer "Use my Facebook email" via Messenger's email quick reply.

### 4.16 SMS capture from DM (optional, double opt-in)

After email capture on any flow:
> Would you like a text each morning with the day's session link? [Yes, text me] [No thanks]

On Yes: "What's your mobile number?" → on submit, the SMS platform sends:
> Strong Years: Reply Y to get your daily session link (about 1 msg/day). Msg & data rates may apply. Reply STOP to cancel, HELP for help. Chang Yin is an AI character. Consent not required to buy.

Only a "Y" reply subscribes the number. Store the consent record.

### 4.17 JOIN flow (blitz mode → founding checkout `/join`)

Live only while blitz mode is on. Used by the launch-week scripts (CONTENT_SYSTEM.md F38/F39, S135–S150), the pinned posts and the counter-update posts (BLITZ_OPS.md §2.5–2.6). Built by cloning the TEST flow.

**Trigger:** keyword JOIN on all Reels, posts, Story replies and direct DMs. Variants: `join, joining, joined, join!, jion, joim, founder, founding, founders, founding member, 🔑` (FOUNDER, the keyword in earlier launch drafts, is kept as a variant so old captions still work). Tags `kw_join`, `launch_l1` (first 5 days), `src_ig`/`src_fb`, `post_{id}`. Public replies: the JOIN pair in §4.2 plus the generic pool; never a link or a price in public.

**Before every message:** the §4.1 global intents and the §4.14 distress and crisis classifier run first and override this flow. A crisis or medical-emergency match sends the §4.14 text and stops the flow; a grief or loneliness match pauses all JOIN messages for 7 days and routes to a human; a safety question ("I fell last month", "I get dizzy", "I have a pacemaker") gets "Please check with your doctor before starting any new exercise, and start with the chair version. A person on our team can answer questions: [Talk to a person]" and no offer message in that turn.

**DM 1 (immediate):**
> Hi {first_name}! This is the Strong Years team assistant (automated). Chang Yin and Sun Yoon are AI characters, not real people. Reply STOP anytime.
>
> Here are the founding-member terms, in plain words (`{{OFFER_TERMS}}`, rendered for the contact's cell; the T25 version reads "• $1 for your first 7 days, then $25 a month. We'll email you 2 days before the first $25 charge."):
> • {{FOUNDING_PRICE}} a month. Your first month is charged today.
> • It renews every month at the same price until you cancel.
> • Cancel online anytime, in two screens at most.
> • 14-day money-back guarantee on the membership charge (one per person): refund yourself in your account.
> • Your founding price stays the same for as long as you stay subscribed, pauses included.
> • {{COUNT_LINE}}
>
> [Show me the page] [What's inside?] [Take the 3-minute test first]

- **Show me the page** → DM 2.
- **What's inside?** → "Every morning, a new 8 to 12 minute session with Chang Yin at your level, with a chair version of everything. Sun Yoon's recipes every Sunday. Your Strength Age retest every month. A live Q&A every Wednesday with a real person from our team. [Show me the page]"
- **Take the 3-minute test first** → `{{DOMAIN}}/q/a?mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=join` ("It picks which of the 4 levels you start on. Your result page has the founding link too.")

**DM 2 (on "Show me the page"):**
> Here it is: {{DOMAIN}}/join?mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=join
>
> It's one page: the terms at the top, then your details and payment. Nothing is pre-ticked.
>
> Want the link and the full terms by email too, so you can decide later?
> [Quick reply: Yes, email me] [Quick reply: No thanks]

**Email capture (on "Yes, email me"):**
> What's your email? (Tap it below if Instagram suggests it.)
> [IG email quick-reply autofill] → validate → save to `email` → n8n creates the lead and replies with a personal link `{{DOMAIN}}/join?lead={lead_id}&utm_source=ig&utm_medium=dm&utm_campaign=join`, which pre-fills first name and email on `/join`.
> Confirmation: "Sent to {email}, with the full terms. By sharing your email you'll get emails from Strong Years, including this link and short daily tips. Unsubscribe anytime with one click."

**If "No thanks":** "No problem. The link above works whenever you're ready."

**Nudge (+20 minutes, only if the link wasn't clicked):** "Here's the link again, {first_name}: {{DOMAIN}}/join. Most people start with the chair version."

**Check-in (+22 hours, inside the 24-hour window):**
> Did you get a look?
> [I joined] [Still deciding] [I have a question]
- **I joined** (or the `founding_member` tag is present) → "Welcome, founding member. Your first session is 8 minutes: [Start Day 1]." Suppress every other sales DM for this contact.
- **Still deciding** → "Fair. Most people take the free 3-minute test first. It picks your starting level: {{DOMAIN}}/q/a. The founding terms don't change while seats are open."
- **I have a question** → human inbox: "A real person on our team will reply here, usually within a few hours during the day."

**Launch-week line (L1–L5 only), added to DM 1:** "Join by Friday 11:59pm Pacific and you also keep one 12-week program forever, even if you cancel. You can use it in the app right away; the download unlocks on day 15." It's removed at the deadline (BLITZ_OPS.md §2.2).

**When the cap closes** (counter reaches 5,000, or {{FOUNDING_CLOSE_DATE}} arrives, whichever comes first): DM 1 swaps to the standard terms ("Strong Years is {{STANDARD_PRICE}} a month, first month charged today, renews monthly until you cancel, cancel online anytime, 14-day money-back guarantee. The founding cohort is full.") and the founding lines are removed from every template the same hour.

**Never in this flow:** a countdown, a "spots left" number that isn't the real count, a reply in Chang Yin's or Sun Yoon's first person, a health promise, or any message after 24 hours without a human.

### 4.18 WAITLIST flow (runway mode → free waitlist `{{DOMAIN}}/waitlist`) and the runway link rule

Live only while **runway mode** is on (CANON UPDATE 2: pages post for 7–21 days before checkout opens; ORGANIC_ENGINE.md §1). Used by the runway scripts with the WAITLIST keyword (S153, S156, S158, S163, S164, S167, S174, S175 in RUNWAY_SCRIPTS.md), the runway pinned post, bio links and Story link stickers. Built by cloning the TEST flow. The page, consent text, double opt-in and referral bonus already exist in the app (`app/src/lib/waitlist.ts`, `/api/waitlist/*`).

**Runway link rule (applies to §4.3–4.13 while runway mode is on):** every offer button in those flows ("7 days for $1", "See the founding membership", `/start?t=…`, `/join?t=…`) is replaced by **[Get first access (free)]** → `{{DOMAIN}}/waitlist?t={keyword}&mc_id={{user_id}}&utm_source={ig|fb}&utm_medium=dm&utm_campaign={keyword}`. Lesson pages and quizzes are unchanged; quiz result pages show the waitlist block instead of a price. The §4.1 `price` intent answers: "Strong Years isn't open yet. When it opens on {{CHECKOUT_OPENS_DATE}}, every price and term is on one page before you pay anything. Want first access? It's free." [Get first access (free)]. No price is quoted in DMs during the runway. When checkout opens, the rule flips to the BOOK flow (§4.19) the same hour.

**Trigger:** keyword WAITLIST on all Reels, posts, Story replies and direct DMs. Variants: `waitlist, wait list, waiting list, waitlst, watilist, list, first access, early access, notify me, 🔔`. Tags `kw_waitlist`, `runway`, `src_ig`/`src_fb`, `post_{id}`. Public replies (add to §4.2): "Sent. It's free, and day one is in there." / "In your messages. One email when doors open, that's it."

**Before every message:** the §4.1 global intents and the §4.14 classifier run first, exactly as in §4.17.

**DM 1 (immediate):**
> Hi {first_name}! This is the Strong Years team assistant (automated). Chang Yin and Sun Yoon are AI characters, not real people. Reply STOP anytime.
>
> The waitlist is free. You get:
> • Day 1 of Chang Yin's 7-Day Strength Reset, right now (8 minutes, one chair).
> • One email when Strong Years opens, plus at most 3 launch emails in the 72 hours after. Nothing else.
> • Optional: one phone notification when doors open.
> No card. Unsubscribe in one click.
>
> [Get first access (free)] [What is Strong Years?]

- **What is Strong Years?** → "A new 8 to 12 minute session with Chang Yin every morning, with a chair version of everything, Sun Yoon's recipes every Sunday, and a strength number you retest each month. Every price and term goes on one page before checkout, when doors open. [Get first access (free)]"

**DM 2 (on "Get first access"):**
> Here it is: {{DOMAIN}}/waitlist?t={first_kw}&mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=waitlist
>
> Type your email on the page and tap the box that says: "Email me when Strong Years opens, plus at most 3 launch emails in the 72 hours after that. One-click unsubscribe in every email." Then confirm from your inbox. Day 1 unlocks when you confirm.
>
> Or share your email here and we'll send the confirm link:
> [Quick reply: Use my email] [Quick reply: I'll use the page]

**Email capture (on "Use my email"):**
> What's your email? (Tap it below if Instagram suggests it.)
> [IG email quick-reply autofill] → validate → n8n posts to `/api/leads` with `source=dm_waitlist` and `consent_text` = the exact waitlist consent string → the app sends the double-opt-in email (nothing else is sent to an unconfirmed address).
> Confirmation: "Sent to {email}. Tap the button in that email to confirm, and Day 1 opens. That email is the only one until doors open."

**Nudge (+20 minutes, only if neither link nor email):** "Day 1 is 8 minutes and free, {first_name}: {{DOMAIN}}/waitlist. Chair against the wall first."

**Check-in (+22 hours, inside the 24-hour window):**
> Did you get Day 1?
> [Yes, did it] [Not yet] [I have a question]
- **Yes, did it** → "Good. Write your number down: how many stands, and did you need your hands? Your friends can join free too, and if one confirms, you get The Wall Plan printable: {{REFERRAL_LINK}}" (the referral reward is the one in `REFERRAL_BONUS_NAME`; never a better place in a queue, because there is no queue).
- **Not yet** → "Here it is again: {{DOMAIN}}/waitlist. Three minutes still counts."
- **I have a question** → human inbox.

**When checkout opens:** WAITLIST becomes a variant of BOOK (§4.19), so every runway post keeps converting; the DM 1 first line changes to "Doors are open."

**Never in this flow:** a price, a "spots left" or queue position, a countdown other than the real opening date, a second email before doors open, or SMS (10DLC not approved).

### 4.19 BOOK flow (launch → `/b` → the Shopify store: the $12 starter offer by default, books-only in the test cell)

Live from checkout open (D0). Used by the launch-week BOOK scripts (S176, S178–S183, S186, S187, S189, S190), bio links, pinned posts, Stories and the broadcast channel. CANON UPDATE 2 + 3: the front end is the Starter Books (7-Day Strength Reset + Sun Yoon's Strong Kitchen, keep forever). **Launch default (cell B): "$12 today = both books + your first founding month, then $25/mo"** as one subscription purchase (the founding plan + the STARTER12 first-payment-only code; the product page states the price, the renewal price, the first renewal date and the cancel path above an unticked consent box). **Test cell (A):** the books alone at the cell price `{{EBOOK_PRICE}}` ($7 / $12 / $15; default display $12), one-time, with the founding offer on the thank-you page and in 3 onboarding emails. The one-click post-purchase page is off at launch (beta; never on digital-only or wallet/PayPal orders). The DM below never states which cell the person will get; it states both honestly and the page they land on is the one they pay for.

**Trigger:** keyword BOOK on all Reels, posts, Story replies and direct DMs. Variants: `book, books, ebook, e-book, the book, bok, boook, reset, kitchen, strong kitchen, 📕, 📖` plus `waitlist` and its variants (from D0). Tags `kw_book`, `launch_week` (D0–D6), `src_ig`/`src_fb`, `post_{id}`, `cell_{A|B}` (written by the redirect, below). Public replies: "Sent you the link and what's inside." / "In your messages. One-time price, yours to keep." Never a link or a price in public.

**Before every message:** the §4.1 global intents and the §4.14 classifier run first, exactly as in §4.17.

**DM 1 (immediate):**
> Hi {first_name}! This is the Strong Years team assistant (automated). Chang Yin and Sun Yoon are AI characters, not real people. Reply STOP anytime.
>
> The starter books, in plain words:
> • Chang Yin's 7-Day Strength Reset: seven mornings, one chair, about 8 minutes a day, an easier version of every move.
> • Sun Yoon's Strong Kitchen: recipes with the protein and fiber grams written in, and a "who should skip" box on every page.
> • $12 today. The page you land on says exactly what that $12 buys: for most people it's both books plus your first month of Strong Years (then $25 a month until you cancel, cancel online anytime); some people see the books alone, one-time. Either way the books are yours to keep (PDF, download right away).
>
> [Send me the link] [What's inside?] [Is it a subscription?]

- **What's inside?** → three sample pages as images (Reset day 1, Strong Kitchen page 14, the who-should-skip box) + [Send me the link].
- **Is it a subscription?** → "It depends on the page you get, and the page says so before you pay. The starter offer is: $12 today for both books and your first month of the Founding Membership, then {{FOUNDING_PRICE}} a month until you cancel. The books-only page is $12 once, not a subscription, with the membership offered afterwards by email. Either way: cancel online anytime in two screens, 14-day money-back guarantee on the membership charge (once per person), founding price locked for as long as you stay subscribed, pauses included. Open to the first 5,000 founding members: {{COUNT_LINE}}." [Send me the link]

**DM 2 (on "Send me the link"):**
> Here it is: {{DOMAIN}}/b?t={first_kw}&mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=book
>
> It opens the offer page on our Shopify store (the price, what renews and when, and the cancel path are all on it before you pay). Shop Pay, Apple Pay, Google Pay and PayPal work at checkout. Nothing is pre-ticked.
>
> Want the link by email too, so you can decide later?
> [Quick reply: Yes, email me] [Quick reply: No thanks]

`{{DOMAIN}}/b` is our redirect (the members app, `app/src/app/b/route.ts`): the sticky cell comes from the signed visitor cookie (B = "$12 today = books + first month, then $25/mo", the default; A = the one-time books, the test cell), the product family from `t` (BOOK/STRONG/SOUP… → the front end; JOIN → the plain membership; FAMILY → the gift page; a keyword never picks a price), and `mc_id`, `pid`, `p`, `t`, `ref` and UTMs are stored in a first-party cookie. It 302s to the **product page** on the Shopify store (selling plans don't work with cart permalinks, so never `/cart/…`), through `/discount/STARTER12?redirect=…` for cell B so the first-payment code is already applied; the theme reads the attribution and visitor id from the query and writes them as cart attributes, which the `orders/paid` webhook reads, so the buy is credited to the post (PIPELINE.md §6 attribution chain). Before checkout opens, `/b` sends everyone to `/waitlist` with the same parameters.

**Email capture:** as §4.17 (IG autofill → `/api/leads`, `source=dm_book`). Confirmation: "Sent to {email}, with the link and what's inside. By sharing your email you'll get emails from Strong Years, including this link and short tips. Unsubscribe anytime with one click."

**Nudge (+20 minutes, only if the link wasn't clicked):** "Here's the link again, {first_name}: {{DOMAIN}}/b. Day 1 is free on our page if you'd rather try first: {{DOMAIN}}/s/l1"

**Check-in (+22 hours, inside the 24-hour window):**
> Did you get the books?
> [Yes, got them] [Still deciding] [I have a question]
- **Yes** (or the `book_buyer` tag from the `orders/paid` webhook) → "Enjoy them. Day 1 is page 3. Chair against the wall first." Suppress every other sales DM for this contact; for books-only buyers the membership offer belongs to the thank-you page and the 3 onboarding emails, not to DMs.
- **Still deciding** → "Fair. Try Day 1 free first: {{DOMAIN}}/s/l1. The book price doesn't jump at midnight."
- **I have a question** → human inbox.

**Never in this flow:** a countdown, a midnight price change, a "spots left" number that isn't the live count, a membership mention without the full terms, a reply in Chang Yin's or Sun Yoon's first person, or any message after 24 hours without a human.

### 4.20 LISTA flow (Spanish WAITLIST; @donchuyylupe runway → `{{DOMAIN}}/es/lista`)

Spanish clone of §4.18 for Don Chuy & Doña Lupe (CHARACTERS_ES.md; offer copy OFFER_ES.md). Live only during the Spanish page's own runway (`ES_RUNWAY_DAYS` after the governor opens the page at the **$30K retained-MRR rung**, tools/build_posting_plan.py). Used by the LISTA scripts ES07, ES10, ES14, ES19, ES22, ES24, ES25 (SCRIPTS_ES.md). Same app endpoints and double opt-in as §4.18 with `lang=es`; every Spanish string here goes through the certified translator before launch (OFFER_ES.md ⚖ flag). All §4.3–4.13 Spanish keyword flows (FUERTE, EQUILIBRIO, ESPALDA, RODILLAS, SUEÑO, RESPIRA, SOPA, EMPEZAR, PRUEBA, FAMILIA) follow the §4.18 runway link rule with **[Quiero enterarme primero (gratis)]**.

**Trigger:** keyword LISTA (variants: `lista, la lista, lista de espera, avísame, avisame, aviso, quiero, waitlist, 🔔`). Tags `kw_lista`, `lang_es`, `runway_es`, `src_ig`/`src_fb`, `post_{id}`. Public replies: "Te mandé mensaje. Es gratis." / "Ya está en tus mensajes. Un correo cuando abramos, nada más."

**Before every message:** the §4.1 global intents and the §4.14 classifier run first (Spanish classifier prompts; crisis lines in Spanish: 988 "Para español, oprima 2").

**DM 1 (immediate):**
> ¡Hola, {first_name}! Mensaje automático del equipo de Don Chuy y Doña Lupe (personajes de IA, no personas reales). Responde ALTO cuando quieras.
>
> La lista de espera es gratis. Te llega:
> • El día 1 del plan de Don Chuy, ahorita (8 minutos, una silla contra la pared).
> • Un correo cuando abra Años Fuertes, y máximo 3 correos de lanzamiento en las 72 horas siguientes. Nada más.
> Sin tarjeta. Te das de baja con un clic.
>
> [Quiero enterarme primero (gratis)] [¿Qué es Años Fuertes?]

- **¿Qué es Años Fuertes?** → "Una sesión nueva cada mañana con Don Chuy, de 8 a 12 minutos, con versión de silla para todo; las recetas de Doña Lupe cada domingo; y unas pruebas que repites cada mes. Todos los precios y términos van en una sola página antes de pagar, cuando abramos. [Quiero enterarme primero (gratis)]"

**DM 2 (on the button):**
> Aquí está: {{DOMAIN}}/es/lista?t={first_kw}&mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=lista
>
> Escribe tu correo en la página y marca la casilla que dice: "Mándenme un correo cuando abra Años Fuertes, y máximo 3 correos de lanzamiento en las 72 horas siguientes. Puedo darme de baja con un clic en cada correo." Luego confirma desde tu correo y se abre el día 1.
> [Respuesta rápida: Usar mi correo] [Respuesta rápida: Uso la página]

**Email capture:** as §4.18 (`source=dm_lista`, `lang=es`, consent text = the exact Spanish string above). Confirmation: "Listo, lo mandé a {email}. Toca el botón de ese correo para confirmar y se abre el día 1. Es el único correo hasta que abramos."

**Nudge (+20 minutes, only if neither link nor email):** "El día 1 son 8 minutos y es gratis, {first_name}: {{DOMAIN}}/es/lista. Primero la silla contra la pared."

**Check-in (+22 hours):** "¿Te llegó el día 1?" [Sí, ya lo hice] [Todavía no] [Tengo una pregunta] → as §4.18 in Spanish (the referral reward is the Spanish printable; never a "better place in line").

**When the Spanish checkout opens:** LISTA becomes a variant of LIBRO (§4.21); DM 1's first line changes to "Ya abrimos."

**Never in this flow:** a price, a queue position, a countdown other than the real opening date, a second email before opening, SMS, or a reply in Don Chuy's or Doña Lupe's first person.

### 4.21 LIBRO flow (Spanish BOOK; launch → `/b?lang=es` → the `/es` Shopify product page)

Spanish clone of §4.19. Live from the Spanish checkout opening. Used by ES26, ES27, ES29, ES31, ES33, ES35, ES37, ES39, ES40. Same cells as the US (default cell B "$12 hoy = los dos libros + tu primer mes, luego $25 al mes"; cell A books only at `{{EBOOK_PRICE}}`); the DM states both honestly and never says which one the person will get.

**Trigger:** keyword LIBRO (variants: `libro, libros, el libro, librito, recetario, plan, 📕, 📖` + `lista` and its variants from the opening). Tags `kw_libro`, `lang_es`, `launch_es`, `cell_{A|B}`. Public replies: "Te mandé el enlace y lo que trae." / "En tus mensajes. Todo escrito antes de pagar." Never a link or a price in public.

**DM 1 (immediate):**
> ¡Hola, {first_name}! Mensaje automático del equipo de Don Chuy y Doña Lupe (personajes de IA, no personas reales). Responde ALTO cuando quieras.
>
> Los libros de inicio, claro y sin letras chiquitas:
> • "Fuerza en 7 Días" de Don Chuy: siete mañanas, una silla, unos 8 minutos al día, con versión fácil de cada movimiento.
> • "La Cocina Fuerte" de Doña Lupe: recetas de casa con los gramos de proteína y fibra, y una cajita de quién debe saltarse cada una.
> • $12 hoy. La página te dice exactamente qué incluyen esos $12: para la mayoría, los dos libros + tu primer mes de Años Fuertes (luego $25 al mes hasta que canceles; cancelas en línea cuando quieras); algunas personas ven solo los libros, un solo pago. De cualquier forma, los libros son tuyos para quedártelos (PDF, se descargan al momento).
>
> [Mándame el enlace] [¿Qué trae?] [¿Es suscripción?]

- **¿Qué trae?** → three sample pages as images (día 1, página 14 de La Cocina Fuerte, the "quién debe saltarse esto" box) + [Mándame el enlace].
- **¿Es suscripción?** → "Depende de la página que te salga, y la página lo dice antes de pagar. La oferta de inicio es: $12 hoy por los dos libros y tu primer mes de la Membresía Fundadora, luego {{FOUNDING_PRICE}} al mes hasta que canceles. La página de solo libros es $12 una vez, no es suscripción, y la membresía se ofrece después por correo. En los dos casos: cancelas en línea cuando quieras en dos pantallas, garantía de devolución de 14 días en el cobro de la membresía (una vez por persona), y el precio fundador queda bloqueado mientras sigas suscrito, pausas incluidas. Abierta a los primeros 5,000 miembros fundadores: {{COUNT_LINE}}." [Mándame el enlace]

**DM 2:** "Aquí está: {{DOMAIN}}/b?t={first_kw}&lang=es&mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=libro. Abre la página de la oferta en nuestra tienda Shopify (el precio, qué se renueva y cuándo, y cómo se cancela, todo está ahí antes de pagar). Shop Pay, Apple Pay, Google Pay y PayPal. Nada viene marcado. ¿Te lo mando también por correo para decidir con calma? [Sí, mándamelo] [No, gracias]"

**Email capture, nudge (+20 min) and check-in (+22 h):** as §4.19 in Spanish ("Prueba el día 1 gratis primero: {{DOMAIN}}/es/s/l1. El precio de los libros no cambia a medianoche."). Book buyers (`book_buyer` tag) get no more sales DMs; the founding offer for books-only buyers lives on the thank-you page and in the 3 Spanish onboarding emails (OFFER_ES.md §4).

**Never in this flow:** as §4.19, plus: any Spanish health result ("más fuerte en 7 días"), "de por vida", or "garantía" outside "garantía de devolución de 14 días".

### 4.22 UNIRME flow (Spanish JOIN → `/join?lang=es`)

Spanish clone of §4.17 for people who want only the membership. Live from the Spanish checkout opening. Used by ES28, ES32, ES36.

**Trigger:** keyword UNIRME (variants: `unirme, unirse, me uno, membresía, membresia, inscribirme, join`). Tags `kw_unirme`, `lang_es`, `launch_es`.

**DM 1 (immediate; full terms BEFORE any link, S-02):**
> ¡Hola, {first_name}! Mensaje automático del equipo de Don Chuy y Doña Lupe (personajes de IA, no personas reales). Responde ALTO cuando quieras.
>
> La Membresía Fundadora de Años Fuertes, completa:
> • {{FOUNDING_PRICE}} al mes. El primer mes se cobra hoy y se renueva cada mes al mismo precio hasta que canceles.
> • Cancela en línea cuando quieras, en máximo dos pantallas.
> • Garantía de devolución de 14 días en el cobro de la membresía, una vez por persona.
> • Tu precio fundador queda bloqueado mientras sigas suscrito, pausas incluidas.
> • Abierta a los primeros 5,000 miembros fundadores: {{COUNT_LINE}}.
> • Te avisamos por correo antes de cada renovación anual (si eliges el plan anual después).
>
> [Mándame el enlace] [¿Qué trae?] [Mejor para mi mamá/papá]

- **¿Qué trae?** → the OFFER_ES.md §3.4 value stack, then [Mándame el enlace].
- **Mejor para mi mamá/papá** → the FAMILIA gift flow (§4.13 in Spanish: 3 meses $49 o 12 meses $119, pagados una vez, nunca se renueva solo).
- **DM 2:** "Aquí está: {{DOMAIN}}/join?t=unirme&lang=es&mc_id={{user_id}}. La página repite todos los términos y tiene una casilla sin marcar que tú decides."

**Never in this flow:** a link before the terms, urgency, a "spots left" number other than the live count, "de por vida", or a reply in a character's first person. Refund and cancel questions go to the Spanish-speaking human inbox (EXPANSION.md §3.2), which offers Essentials or a pause first, once, and then does what the person asked.

---

## 5. Checkout, order bumps, upsells and trial terms (prices and take rates as modelled in OFFER.md 2.2)

### 5.1 Checkout page (one page, mobile first)

Order of elements, top to bottom:
1. Disclosure strip (same as landing).
2. **Heading:** "Start your 7 days of Strong Years for $1" (or "Get the 7-Day Strength Reset" / "Get Sun Yoon's Strong Kitchen").
3. **What you're getting** (3 lines, with the product photo): "Your Daily Practice: a new 8–12 minute session every day · Monthly Strength Age retest · Sun Yoon's Sunday recipes · Wednesday live Q&A with a real human coach".
4. **Terms box, placed directly above the pay button, in type at least as large as the price, Ink on Rice (OFFER.md 2.3):**
   > **Today: $1.** Your 7-day trial starts now.
   > **On {trial_end_date}, your Strong Years membership renews at {{PRICE}}**, then {{PRICE}} every month on the same date, until you cancel.
   > **Cancel anytime** online in at most two screens at {{DOMAIN}}/account, or reply "cancel" to any email{{IF_SMS: , or text CANCEL}}. Cancel before {trial_end_date} and you won't be charged again.
   > **We'll remind you** by email{{IF_SMS: and text}} 48 hours before your trial ends, and before every renewal after that.
   > **14-day money-back guarantee** on your first membership charge, one per person, self-serve from your account.
   > **Add-ons:** Add-ons are digital downloads; refund on request within 14 days (email us). The kit: 30 days, no return needed.
5. Name, email, phone (optional) with a separate, unticked SMS consent checkbox.
6. Payment: Apple Pay / Google Pay / card. Express wallets sit below the terms box.
7. **Order bump** (unticked, see 5.2).
8. **Consent checkbox (separate, unticked, required):**
   > ☐ I agree to the automatic renewal terms above: $1 today, then {{PRICE}}/month from {trial_end_date} until I cancel. I can cancel online anytime. [Terms] [Membership & Cancellation Policy]
9. **Button (Persimmon, full width):** "Start my $1 trial". Under it: "Then {{PRICE}}/month from {trial_end_date}. Cancel anytime online."
10. Trust row: secure payment icons, support email, "Cancel online or by replying 'cancel' to any email; no phone call needed (billing questions: {{PHONE}})", and [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "Reviewed by a licensed physical therapist"] FALLBACK: ""Built on published exercise guidelines for older adults"".
11. Footer disclosure.

Nothing is pre-ticked. If the consent box isn't ticked, tapping the button scrolls to it with "Please tick the box above to confirm the membership terms" (Ink text, Brass highlight), rather than a faded button.

**$7 Reset and $17 Kitchen checkouts (control, membership included):** the terms box reads: "**Today: $7** for the 7-Day Strength Reset (yours to keep). **It includes 7 days of Strong Years.** On {date+7}, your membership renews at {{PRICE}}/month until you cancel. Cancel anytime online in at most two screens at {{DOMAIN}}/account, or reply "cancel" to any email{{IF_SMS: , or text CANCEL}}. We'll remind you 48 hours before, and before every renewal after that. The $7 Reset is an add-on: refund on request within 14 days." Same separate unticked consent checkbox. **Split-test arm (OFFER.md 2.1):** product-only checkout ("One-time payment of $7. No subscription.") followed by a post-purchase "Add your 7 free days of Strong Years" button with its own terms (5.3). Pick the winner on revenue per buyer at day 67 net of refunds and chargebacks.

**Consent record stored per order:** timestamp, IP, user agent, the exact rendered terms text, checkbox state, price cell, trial end date. Keep for at least 3 years (California) and preferably 4.

**Billing descriptor:** `STRONGYEARS MEMBER` + support URL.

### 5.2 Order bump: The Wall Plan, $9 (~30% take)

> ☐ **Yes, add The Wall Plan for $9.** A printable 12-week calendar for your fridge plus 12 weekly grocery lists from Sun Yoon. Large print, one page a week. Yours to keep, even if you cancel.

Written in Sun Yoon's voice on the Kitchen checkout: "☐ **Add The Wall Plan, $9.** Put it on the fridge. You'll walk past it ten times a day and feel guilty nine of them. That's the point."

Test to push take rate above 40% (OFFER.md 2.5): show a photo of the plan on a real fridge; Sun Yoon voice vs. neutral voice.

### 5.3 One-click upsell ladder

Post-purchase upsells charge the saved payment method with one click. Every page shows its price and terms next to the button, and every "no" link is plain and equally readable, never "No, I don't care about my health." The annual plan is **not** offered at first checkout (an annual price on the front end lowers cold-traffic trial starts); it's offered at trial end and in the day 21/45/75 campaigns (7.11).

**Upsell 1: Keep a 12-week program forever, $27 (~10% take)**
- **Headline:** Pick the program you want to keep forever.
- **Body:** Your membership includes all six 12-week programs while you're a member. For $27 once, choose one and keep it forever, even if you cancel one day: *Strong at 70*, *Back Strong*, *Balance & Steady Feet*, *Gut Reset with Sun Yoon*, *Grip & Hands* or *Walk Stronger*. Twelve weeks of sessions, a printable progress booklet, and Strength Age checkpoints at weeks 0, 6 and 12.
- **Button:** "Yes, I'll keep [program] forever for $27"
- **No link:** "No thanks, continue"
- (Later reused as a save lever: "you keep your program either way.")

**Downsell (if upsell 1 declined): Printables only, $7 (~5% take)**
- **Headline:** Just the paper, then?
- **Body:** The large-print exercise cards, the weekly plan sheets and the fridge Strength Age chart for your program, to print at home or at any drugstore photo counter. $7, yours to keep.
- **Button:** "Yes, add the printables for $7" · **No link:** "No thanks"

**Upsell 2: The Strong Years Kit, $29 (~6% take; $12 landed cost, ~$17 contribution)**
- **Headline:** Want the three things Chang Yin uses?
- **Body:** You don't need equipment to start. By week 3 or 4, many people are ready for more resistance, and a kit on the table is a good reminder to press play. Inside: 3 resistance loops (light, medium, heavy), a door anchor, and a grip trainer, with a large-print card showing how Chang Yin uses each one.
- **Button:** "Yes, send me the kit ($29)" · **No link:** "No thanks, I'll use water jugs"
- Gift flow: show the kit **before** upsell 1 (gift buyers aged 35–55 take physical products at 2–3× the rate; OFFER.md 2.5).

**Product-only split-test arm ($7/$17 buyers): the membership button**
- **Headline:** Your Reset is ready. Want your 7 free days of Strong Years too?
- **Body:** Keep going after the Reset with your Daily Practice: a new session every day, your monthly Strength Age retest and Sun Yoon's Sunday recipes. 7 days free, then {{PRICE}}/month. We'll remind you 48 hours before. Cancel online anytime.
- **Terms line (above button):** "Free for 7 days, then {{PRICE}}/month starting {date+7}, renewing monthly until you cancel."
- **Button:** "Yes, add my 7 free days" · **No link:** "No thanks, just the Reset"

**Gift buyers:** kit first (above), then "Give one to the other parent too? Second gift 50% off," then "And you? Start your own 7 days for $1" (full trial terms + consent checkbox on that page, since it creates a subscription).

**Paid-traffic-only path (test, OFFER.md 2.5):** a $27 "Strong at 70 Starter" (the program + 14 days of membership), for front-end revenue closer to self-liquidating.

### 5.4 Thank-you page (all front ends)

- **Heading:** "You're in. Your first Daily Practice takes 8 minutes."
- Big button: **Start Day 1 now** (auto-logged in via magic link).
- Three setup steps (each one tap): "When do you have your morning tea?" (reminder time) · add to home screen (picture guide) · print your card.
- Receipt summary with terms repeated ("Trial ends {date}. You'll be charged {{PRICE}} unless you cancel. Cancel here: [link]{{IF_SMS: or text CANCEL}}").
- Disclosure line.

### 5.5 Trial and membership terms language (exact text blocks)

**A. Checkout terms** (see 5.1).

**B. Confirmation email terms block (sent immediately; also by SMS once SMS is live). Also serves as the NY GBL §527-a acknowledgment: it must include the cancellation mechanism.**
> **Your membership details**
> Plan: Strong Years, monthly
> Today's charge: $1.00 for a 7-day trial (or: $7.00 for the 7-Day Strength Reset, including 7 days of Strong Years)
> Trial ends: {trial_end_date}
> After your trial: {{PRICE}} per month, charged on the {day} of each month, until you cancel
> How to cancel: {{DOMAIN}}/account → Membership → Cancel (at most two screens, online, anytime), or reply "cancel" to this email{{IF_SMS: , or text CANCEL}}.
> Reminders: we email you before every renewal charge (7 and 2 days before the first, 3 days before each one after that) and once a year with a summary of your plan.
> Refunds: 14-day money-back guarantee on your first membership charge, one per person, self-serve in your account. Add-ons: refund on request within 14 days. The kit: 30 days.
> Questions about billing: {{PHONE}} or reply to this email.

**B2. Founding version (blitz mode).** Same block with: "Plan: Strong Years founding membership, monthly · Today's charge: {{FOUNDING_PRICE}} for your first month (plus add-ons: {list}) · Next charge: {{FOUNDING_PRICE}} on {renewal_date}, then monthly until you cancel · Your founding price stays the same while you stay subscribed, pauses included · Your founding-week program download unlocks on {purchase_date + 15 days}" (if the bonus applies).
> On your statement: STRONGYEARS MEMBER

**C. Pre-conversion reminder (email + SMS, 48 hours before the first charge, for every trial and included-membership period):**
Email subject: "5 sessions done. Your membership continues on {weekday}."
> Hi {first_name}, a quick, honest reminder. Your 7-day trial of Strong Years ends on {trial_end_date}. If you'd like to continue, you don't need to do anything: we'll charge {{PRICE}} on {trial_end_date} and then monthly until you cancel. If you'd rather not continue, cancel here in two screens at most: [Cancel my trial]. Want to pay less? Keep going for $119 a year instead (about $9.92 a month): [Switch to yearly]. So far you've done {n} sessions. {one-line personalized progress}.

{{IF_SMS: SMS: "Strong Years: your trial ends {date}. Then {{PRICE}}/mo until you cancel. To keep going, do nothing. To cancel (2 screens max): {link} or reply CANCEL. Reply STOP to opt out."}}

**C2. Renewal reminders (every renewal charge, all modes; email, plus SMS once live).** Subject: "Your Strong Years membership renews on {date}". Body: "Your membership renews on {date} at {price}. To keep going, do nothing. To cancel: {{DOMAIN}}/account (two screens at most) or reply 'cancel'. This month you did {n} sessions." Timing: 7 and 2 days before the first renewal; 3 days before every later monthly renewal; 30 days before an annual renewal (D below).

**D. Annual renewal notice (sent 30 days before, inside the 15–45 day window some states require):**
Subject: "Your yearly Strong Years membership renews on {date}"
> Your yearly plan renews on {date} for $119. To keep it, do nothing. To cancel or switch to monthly: [Manage membership]. This year you did {n} sessions and your Strength Age went from {x} to {y}.

**D2. California annual reminder (all auto-renewing members, monthly included).** Sent every 12 months from the start date. Subject: "Your yearly summary: your Strong Years membership". Body: "You've been a member since {start_date}. Your plan: {plan}, {price} {per month / per year}, renewing automatically until you cancel. To cancel: {{DOMAIN}}/account (two screens at most) or reply 'cancel'. This year: {n} sessions, Strength Age {x} → {y}."

**E. Price change notice:** sent exactly 30 days before the change (inside California's 7–30 day window) by email{{IF_SMS: and SMS}}, with the new price, the date, and a one-tap cancel link. Founding members keep their founding price while they stay subscribed, pauses included (never "for life").

**F. Cancellation confirmation (email, immediately):**
> Your Strong Years membership is cancelled. You won't be charged again. You have access until {period_end}. Your streak, Strength Age history and what the coach remembers are saved for 90 days, and you can restart anytime. Cancelled by mistake? [Undo]

**G. Terms page summary box (top of the Membership & Cancellation Policy):** plain-language summary of A–F above, in 20px Ink text, before any legal text.

**SMS timing note (applies to B, C, C2, D2 and E):** 10DLC / toll-free SMS verification takes 3–6 weeks, so launch runs on email + DM. Until SMS is approved, the confirmation, the 48-hour pre-charge reminder, every renewal reminder, the annual reminder and price-change notices go by **email only**, and every `{{IF_SMS: …}}` fragment is removed.

**H. Add-on terms (bumps and upsells, printed in the terms box wherever an add-on is sold):** "Add-ons are digital downloads; refund on request within 14 days (email us). The kit: 30 days, no return needed. One refund per add-on. The founding-week keep-forever program unlocks for download on day 15."

### 5.6 Founding checkout page: `{{DOMAIN}}/join` (blitz mode)

The lean page that the JOIN DM flow (§4.17), founding ads (ADS_SCRIPTS.md), launch emails and quiz result pages route to in blitz mode. One page, one offer, no navigation, no images to load (LCP < 2.0s on 4G), the form above the fold on desktop and directly under the terms on mobile. Ink text on Rice or Paper everywhere; nothing muted or gray. Pixel events use neutral names (`join_view`, `Purchase`, `Subscribe`); no quiz answers or condition words are sent.

Order of elements, top to bottom:
1. **Disclosure strip** (same as every landing page, §2.2).
2. **Heading:** "Join as a founding member: {{FOUNDING_PRICE}} today."
3. **One line:** "Your Daily Practice with Chang Yin, 8 to 12 minutes a day at your level, with a chair-based version of everything. Sun Yoon's recipes every Sunday. A Strength Age you retest every month."
4. **Four checklist lines (bold, Jade marker):**
   - {{FOUNDING_PRICE}} today for your first month, then {{FOUNDING_PRICE}} a month until you cancel
   - Founding price locked for as long as you stay subscribed
   - 14-day money-back guarantee
   - Chang Yin and Sun Yoon are AI characters. The practices are real.
5. **Founding cohort box (2px Ink border):** `{{COUNT_LINE}}` (canonical rule: below 1,000 members it reads "Founding membership is open to the first 5,000 members or until {{FOUNDING_CLOSE_DATE}}, whichever comes first" with a link to the live count; from 1,000 it reads "{{COUNT}} of 5,000 founding seats taken" with a bar: Paper track, Ink outline, Jade fill) + "A live count from our member database. No timers, no made-up numbers. If someone takes a refund, their seat goes back."
5a. **Who runs Strong Years (small block, Ink on Rice):** founder's name and photo, the legal company name and mailing address, support email and billing phone `{{PHONE}}`: "Strong Years is made by {{COMPANY_LEGAL_NAME}}, {{MAILING_ADDRESS}}. Questions before you join? {{PHONE}} or {{SUPPORT_EMAIL}}."
6. **Your details:** first name, email (pre-filled when the link carries `lead=`). No phone field while SMS is off.
7. **Payment:** Apple Pay / Google Pay / card, and PayPal from L1 if the processor allows it (a high-trust wallet for 55+ buyers; AUDIT F19).
8. **Order bumps (each unticked, each with its own price):**
   - ☐ **Add the 7-Day Strength Reset, $7.** Seven follow-along sessions and a printable plan. Yours to keep, even if you cancel.
   - ☐ **Add Sun Yoon's Strong Kitchen + Chang Yin's 12-Week Printable, $17.** The recipe collection and the printable plan. Yours to keep.
   - ☐ **Add The Wall Plan, $9.** A printable 12-week calendar for your fridge plus 12 weekly grocery lists (§5.2).
   - Safe Mode visitors (`?gentle=1`, from quiz Q4/Q5 routing) see no bumps and no upsells.
   - Each bump carries its line of the add-on terms (§5.5 H). **L1–L5 test (AUDIT F18):** one bump (the $17 Kitchen) vs all three, alongside the price test; if one bump wins on net revenue per visitor, move the $7 and $9 items to the post-purchase page.
9. **Terms box, directly above the pay button, in type at least as large as the price:**
   > **Today: {{FOUNDING_PRICE}}** for your first month of Strong Years, plus any add-ons you ticked above.
   > **On {renewal_date}, your membership renews at {{FOUNDING_PRICE}}**, then every month on the same date, until you cancel. As a founding member, your price stays the same for as long as you stay subscribed.
   > **14-day money-back guarantee:** refund yourself in your account within 14 days of today's charge, or reply to any email.
   > **Cancel anytime** online in at most two screens at {{DOMAIN}}/account, or reply "cancel" to any email.
   > **We'll remind you** by email before every renewal: 7 and 2 days before the first, 3 days before each one after that, plus a yearly summary.
   > **Add-ons:** Add-ons are digital downloads; refund on request within 14 days (email us). The kit: 30 days, no return needed. Founding-week program download unlocks on day 15.
10. **Consent checkbox (separate, unticked, required):**
    > ☐ I agree to the automatic renewal terms above: {{FOUNDING_PRICE}} today, then {{FOUNDING_PRICE}}/month from {renewal_date} until I cancel. I can cancel online anytime. [Terms] [Membership & Cancellation Policy]
11. **Button (Persimmon, full width, Rice text):** "Join for {{FOUNDING_PRICE}} today". Under it, full contrast: "Renews at {{FOUNDING_PRICE}}/month on {renewal_date}. Cancel online anytime."
12. **Fine print (Ink, not muted):** "General fitness and nutrition education, not medical advice. Check with your doctor before starting new exercise. On your statement: STRONGYEARS MEMBER."

After payment: the §5.3 upsell ladder (founding-week orders skip upsell 1 and lead with the kit), then the §5.4 thank-you page with the founding terms in the receipt. Consent record as §5.1 (plus the price cell and the founding flag).

**States:**
- **Canceled at payment:** a Brass box at the top: "No payment was taken. You can try again, or come back anytime."
- **Cohort full:** heading "Join Strong Years: {{STANDARD_PRICE}} today."; the "founding price locked" line is removed; the counter box reads "The founding cohort is full. New members join at the standard price of {{STANDARD_PRICE}} a month."; every `{{FOUNDING_PRICE}}` in the terms box becomes `{{STANDARD_PRICE}}`.
- **Cells (§0.2.1):** F25 and F30 visitors see this page with `{{FOUNDING_PRICE}}` = $25 or $30. **T25 visitors never see `/join`'s charge-today terms:** they get the §5.1 trial checkout with `{{PRICE}}` = $25 and the founding lines ("your $25 price stays the same while you stay subscribed, pauses included"; the cohort box). Sticky per visitor; a T25 visitor who opens a `/join` link is shown the trial version.

---

## 6. Onboarding: days 0–14

Goal of onboarding, in priority order: (1) first session within 24 hours, (2) Strength Age baseline within 72 hours, (3) 3 sessions in the first 7 days, (4) daily text time set, (5) partner add-on or community touch. Members who hit (1)–(3) are the ones who convert from trial and stay; measure all emails by these actions, not opens.

Branching rules:
- Every email checks behavior first. If the member already did the thing an email asks for, send the "already done" variant (noted as **If done:**).
- Sender names: "Chang Yin (Strong Years)" for movement emails, "Sun Yoon (Strong Years)" for kitchen and honesty emails, "Strong Years Team" for account/billing emails. All three from the same address.
- Every email footer: "Chang Yin and Sun Yoon are AI characters; their story is fictional. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Sessions reviewed by `[PT NAME]`, PT, DPT; recipes by `[RD NAME]`, RDN.] FALLBACK: "Sessions and recipes built from published guidelines for older adults." General education, not medical advice. [Manage membership] [Unsubscribe] {mailing address}".
- Format: 20px body, single column, one button per email (Persimmon, 60px tall, white text), plain-text version always. No gray text in the template, including the footer.
- Time: send at the member's chosen session time minus 15 minutes (default 7:45 am local).

### 6.1 Email sequence (14 emails)

**E1. Day 0, immediately after signup**
From: Chang Yin (Strong Years)
Subject: Your first session is 8 minutes. Here it is.
Preview: Your Daily Practice is ready. Press play.
> {first_name}, welcome.
>
> I'll keep this short, because the best thing you can do right now is not read. It's stand up.
>
> Your first Daily Practice is 8 minutes. We've set your track from your answers:
> **Rebuild:** everything seated or holding a counter.
> **Steady:** on your feet, counter nearby.
> **Strong:** you'll want two water jugs.
> (**Iron** comes later, when Strong gets easy.)
>
> Not sure? Choose Rebuild. Nobody has ever been hurt by starting too easy. Sore knee or low energy today? Tap the button under the video and I'll swap in an easier version.
>
> [Start Day 1]
>
> Three rules for every session:
> 1. Move slowly. Slow is where strength is built.
> 2. Breathe out when you push, stand or lift.
> 3. Stop if anything hurts sharply, or if you feel dizzy or short of breath.
>
> Your trial: $1 today; {{PRICE}}/month from {trial_end_date} unless you cancel. We'll remind you 2 days before. Cancel anytime at {{DOMAIN}}/account.
>
> You can also ask me questions in the app. I'm an AI character, and I'll remind you of that. How we handle safety: {{DOMAIN}}/safety
>
> See you in the session,
> Chang Yin
>
> P.S. I'm an AI character, and I'll never pretend otherwise. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `[PT NAME]`, our physical therapist, has checked every movement you'll see.] FALLBACK: "Every movement you'll see is built from published exercise guidelines for people our age."

**E2. Day 1, morning**
From: Chang Yin
Subject: The hardest button is the first one
Preview: Today we find your starting line.
**If Day 1 not done:**
> {first_name}, the hardest button in any program is the first "play".
>
> So here's a smaller one: 3 minutes. Three sit-to-stands, three slow breaths, done. If you want to keep going after that, the full 8 minutes is right there.
>
> [Do the 3-minute start]
>
> Chang Yin
**If Day 1 done:**
> You did Day 1. Good. Today, before Day 2, let's find your starting line: your Strength Age.
>
> It takes 3 minutes: a chair against the wall for 30 seconds of sit-to-stands, then four balance positions at the kitchen counter. We'll save your number and chart it every month.
>
> This number is the reason most members stay. Not because it's always good news on day one, but because it's the first time anyone has measured their strength, and it's very satisfying to watch it change.
>
> [Find my Strength Age]
>
> Chang Yin

**E3. Day 2**
From: Sun Yoon (Strong Years)
Subject: What did you eat for breakfast?
Preview: Be honest. I will be.
> {first_name}, I'm Sun Yoon. Chang Yin's wife. I run the kitchen, and I don't lie about food.
>
> What did you eat for breakfast? If the answer is toast and coffee, you're not alone, and it's not enough. Your muscles need protein at every meal, about 25 to 30 grams, and more of us need it as we get older. Breakfast is where most people come up short.
>
> This week's easy fix, 3 minutes, 25 grams of protein:
> **Silken tofu with soy sauce, sesame oil and scallion**, or
> **Two eggs scrambled soft with a spoon of cottage cheese**, or
> **A cup of Greek yogurt with walnuts.**
>
> [See this week's 3 recipes]
>
> If you have kidney disease, ask your doctor before eating more protein. Everyone else: eat your eggs.
>
> Sun Yoon
>
> P.S. I'm an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: My recipes are checked by `[RD NAME]`, a real registered dietitian, who is very patient with me.] FALLBACK: "My recipes follow published nutrition guidance for older adults. I follow it too, mostly."

**E4. Day 3**
From: Chang Yin
Subject: {n} sessions. Here's what's happening in your legs.
Preview: And what soreness is normal.
> {first_name}, you've done {n} sessions. [If n = 0: "You haven't started yet, and that's okay. Today is a good day. [Start with 3 minutes]"]
>
> Here's what's happening. In the first few weeks, much of your new strength comes from your nervous system learning to use the muscle you already have: better coordination, more muscle fibers switching on together. Bigger changes in the muscle itself come with weeks and months of steady practice. That's why sessions start to feel easier within about two weeks, before you'd see any change in the mirror.
>
> Some muscle soreness a day or two after a new exercise is normal. It should feel like "used", not "injured", and fade in a couple of days. Sharp pain, swelling or pain in a joint that gets worse means ease off and switch to the Rebuild track.
>
> If today is Tuesday, it's mobility: the gentlest day of the week.
>
> [Start today's session]
>
> Chang Yin

**E5. Day 4**
From: Chang Yin
Subject: Where should you begin? (Your track)
Preview: Pick the one that sounds like you.
> {first_name}, the daily session keeps you strong all over. A **track** is for the one thing you most want to change. Tap the sentence that sounds like you, and I'll add that track to your home screen.
>
> [I push on the armrests to stand up] → Chair Builder
> [My knees complain on the stairs] → Knees & Stairs
> [I don't feel steady on my feet] → Steady Feet
> [My back is stiff every morning] → Back & Posture
> [I can't open jars anymore] → Hands & Grip
> [I lie awake at night] → Sleep Wind-Down
> [I'm tired after I eat] → After-Meal Movement
>
> Do your daily session first. Add the track on days you have 10 more minutes.
>
> Chang Yin
(Each option is a link that sets the track in-app and logs `track_set`.)

**E6. Day 5 (48 hours before trial end, required)**
From: Strong Years Team
Subject: Your trial ends {weekday}: here's what happens next
Preview: Keep going, switch to yearly, or cancel. Your choice.
> (Use terms block 5.5 C, plus:)
> Here's your week so far: {n} sessions · Strength Age {SA or "not taken yet: [take it]"} · Track: {track}.
>
> Three options, all one tap:
> **Keep going monthly:** do nothing.
> **Keep going for $119 a year instead (about $9.92 a month):** [Switch to yearly, $119]
> **Cancel:** [Cancel my trial]. No hard feelings, and your printable cards stay yours.

**E7. Day 6**
From: Strong Years Team
Subject: Meet the real people behind every session
Preview: And ask them your question live on Wednesday.
[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Send E7 as written below.] FALLBACK: "Send the fallback E7 instead: Subject "A real human answers your questions on Wednesday". Body: "{first_name}, you've been following Chang Yin all week. He's an AI character. On Wednesdays, a real human coach from our team answers member questions live for 30 minutes, introduced as a human. Send your question now: [Send my question]. Why we do it this way: AI characters give you a patient teacher every morning; real people make sure you can ask a human. You deserve both, and you deserve to know which is which.""
> {first_name}, you've been following Chang Yin all week. Here are the humans who check his work:
>
> **`[PT NAME]`, PT, DPT**: physical therapist, `[X]` years with older adults. Approves every movement and progression.
> **`[RD NAME]`, RDN**: registered dietitian. Checks every one of Sun Yoon's recipes.
>
> Every Wednesday, one of them goes live for 30 minutes and answers member questions. This week: {date, time ET}. Send your question now and they may answer it on air.
>
> [Send my question]
>
> Why we do it this way: AI characters let us give you a patient teacher every single morning. Real professionals make sure what he teaches is right. You deserve both, and you deserve to know which is which.

**E8. Day 7 (trial converts; transactional + welcome)**
From: Strong Years Team
Subject: Welcome to Strong Years, officially
Preview: Your receipt, and your week in numbers.
> {first_name}, your trial has ended and your membership is active. Receipt: {{PRICE}} charged on {date}; next charge {next_date}. Manage or cancel anytime: [Account].
>
> Your first week: {n} sessions · {minutes} minutes · Strength Age {SA}.
>
> Next week's rhythm: Mon strength · Tue mobility · Wed balance (and the live Q&A) · Thu strength · Fri breath + qigong flow · Sat walk-and-talk · Sun rest + stretch, Sun Yoon's recipes and the Sunday Premiere.
>
> This week, pick your 12-week program: *Strong at 70*, *Back Strong*, *Balance & Steady Feet*, *Gut Reset with Sun Yoon*, *Grip & Hands* or *Walk Stronger*. [Choose my program]
>
> [Start this week]
>
> Remember our promise: within 14 days of this first charge, if it isn't worth it, you get it back, and the $1 too. Just tap Refund in your account. (One money-back guarantee per person.)
>
> Rather pay less? Keep going for $119 a year (about $9.92 a month): [Switch to yearly]
(If the trial was cancelled: send the cancellation confirmation 5.5 F instead, plus "Your free lesson library stays open: [link]". Tag for winback.)

**E9. Day 8**
From: Sun Yoon
Subject: Who else in your house should be doing this?
Preview: Add your partner for $8 a month.
> {first_name}, Chang Yin does his session at 7. I used to watch from the kitchen door. Now I do it with him. (I'm better at balance. Don't tell him.)
>
> For $8 a month you can add your partner to your membership. Husband, wife, sister, friend. They get their own level, their own Strength Age and their own streak.
>
> [Add my partner]
>
> Buying for your parents? Give them 3 months for $49 or a year for $119. It's prepaid, never renews by itself, and they'll get a card from me.
>
> [Give a gift]
>
> People who train with someone else skip less. I'm not a scientist. I'm just married.
>
> Sun Yoon

**E10. Day 9**
From: Chang Yin
Subject: Put this on your fridge
Preview: Your week on one page.
> {first_name}, the best reminder isn't an app notification. It's a piece of paper you walk past ten times a day.
>
> Print your wall chart: your weekly rhythm, your three safety rules, and a box for each day. Tick it with a pen. It sounds old-fashioned. It works.
>
> [Print my wall chart]
>
> And if you haven't set a daily text yet, choose a time here and I'll send the day's session link each morning: [Set my time]
>
> Chang Yin

**E11. Day 10**
From: Sun Yoon
Subject: Day 10 is when people quit
Preview: I'll tell you why, and what to do instead.
> {first_name}, I'll be blunt. Around day 10, the excitement is gone, and the results you can see haven't arrived yet. This is when most people stop.
>
> So here's the rule in our house: **three sessions a week is a good week.** Not seven. Three. If you miss a day, you haven't failed. You've had a Tuesday.
>
> {If n ≥ 6: "You've done {n} sessions already. That's more than most people do in a month. Keep going."}
> {If n < 3: "You've done {n}. Let's make it {n+1} today, the 8-minute one. The Rebuild track is fine."}
>
> [Today's session]
>
> Sun Yoon

**E12. Day 11**
From: Chang Yin
Subject: The Friday flow
Preview: Slow minutes. Balance, breath, and quiet.
> {first_name}, on Fridays we do something different: a slower breath and qigong flow, with tai chi weight shifts. Tai chi is one of the best-studied movement practices for balance in older adults, and we think it'll become the session you look forward to.
>
> No religion, no costume, no special clothes. Just slow weight shifts, big breaths and soft knees.
>
> [Preview Friday's flow]
>
> Chang Yin

**E13. Day 12**
From: Strong Years Team
Subject: One word?
Preview: How is Strong Years going for you, in one word?
> {first_name}, you're nearly two weeks in. How's it going, in one word? Just hit reply. A real person on our team reads every answer, and we change things because of them ([insert a real change made from member feedback, e.g. "members asked for larger captions, so we made them bigger"; leave this sentence out until one exists]).
>
> If something's not working, a movement that hurts, a video that won't play, a level that's too hard, tell us, and we'll fix it or find you an alternative.
>
> [Or tap one: Great · Good · Okay · Not for me]
(Tap routes: Great/Good → community invite + review ask at day 30 (7.10); Okay → "What would make it better?" form; Not for me → human outreach + offer to pause, or a refund if they're inside the 14-day guarantee.)

**E14. Day 14**
From: Chang Yin
Subject: Two weeks. Let's check one number.
Preview: A 30-second mini test (optional).
> {first_name}, two weeks ago you did {baseline_reps} chair stands in 30 seconds. Want to see where you are now? It's optional, 30 seconds, and it's the quickest way to feel what you've done.
>
> [Do the 30-second mini test]
>
> Your full retest is on the 1st of {next_month}, and I'll walk you through it.
>
> What's next for the coming month:
> Week 3: I'll offer you the next step up in your legs sessions. Take it if the reps feel easy.
> Week 4: your first full Strength Age retest.
> Every Sunday: Sun Yoon's letter.
>
> Chang Yin
>
> P.S. If you're enjoying this, the yearly plan is $119, about $9.92 a month instead of {{PRICE}}: [See yearly]

### 6.2 SMS sequence (10 texts, only for opted-in members)

(Switches on only after 10DLC / toll-free verification is approved, 3–6 weeks from kickoff. Until then the launch runs on email + DM, and the matching emails in §6.1 carry every reminder.)

All texts start with "Strong Years:" and end with "Reply STOP to opt out" at least once a week (always on the first and trial-reminder texts). Short links on our domain. Send at the member's chosen time.

| # | Day | Condition | Text |
|---|---|---|---|
| S1 | 0 | On signup | Strong Years: Welcome, {first_name}! Your first session is 8 min. Your track is ready: {link}. Chang Yin is an AI character. Reply STOP to opt out. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: (add "sessions PT-reviewed" before STOP)] FALLBACK: "(no review wording)" |
| S2 | 1 | Day 1 not done | Strong Years: Morning, {first_name}. 3 minutes counts. Start here: {link} |
| S3 | 2 | Strength Age not taken | Strong Years: Chair against a wall, 30 seconds. Find your Strength Age today: {link} |
| S4 | 3 | Any | Strong Years: Today is mobility + breath, the gentlest day. 8 min: {link} |
| S5 | 4 | Any | Strong Years (Sun Yoon): 25g protein breakfast in 3 min. Tofu, soy, scallion. Recipe: {link} |
| S6 | 5 | Trial, required | Strong Years: your $1 trial ends {date}. Then {{PRICE}}/mo until you cancel. To keep going, do nothing. To cancel (2 screens max): {link}. Reply STOP to opt out. |
| S7 | 6 | Any | Strong Years: A real human coach answers member questions live on Wed {date}. Send yours: {link} |
| S8 | 8 | No partner added | Strong Years (Sun Yoon): Doing it together? Add your partner for $8/mo in 1 minute: {link} |
| S9 | 10 | Sessions < 3 | Strong Years: 3 sessions a week is a good week. Today's is 8 min: {link} |
| S10 | 14 | Any | Strong Years: 2 weeks! Want to see your chair-stand number now? 30 sec: {link} |

Timing rule: promotional texts only 10:00–20:00 recipient local time (canonical window). The member-requested daily session link may go at the member's chosen time because it's the informational message they asked for, so it never contains a promotion. All of §6.2 starts only once SMS is approved.

After day 14, the SMS channel becomes the **daily session link** only (one text per day at the chosen time: "Today: strength, 9 min. {link} — Chang Yin (AI coach)"), plus retest day and milestone texts (Section 7). Members can switch to "3 days a week" or "weekly" in settings. Cap: 1 marketing/promotional text per week on top of the daily link.

### 6.3 In-app first-72-hours checklist

Shown as a card at the top of the home screen: "Your first 3 days", 7 items, big tick boxes, each one tap to do. Completing all 7 unlocks a small reward: Sun Yoon's printable "Strong Kitchen" starter card and a badge on the calendar ("First Three Days").

| # | Item | Why it matters | When prompted | Nudge if not done |
|---|---|---|---|---|
| 1 | **Do your first session** (any level, any length) | The #1 predictor of conversion and retention | Hour 0 | Push/SMS/email at hour 4 and next morning with the 3-minute version |
| 2 | **Check your track** for tomorrow (Rebuild / Steady / Strong / Iron) and tap "too easy / just right / too hard" | Tomorrow's session is ready and levelled | After item 1 | In-app only |
| 3 | **Set your daily reminder time** (text, email or app notification) | Turns a decision into a routine | After item 1 | Email E10 |
| 4 | **Find your Strength Age** | Baseline for the monthly retest, the core retention loop | Day 1 | Email E2, SMS S3, in-app banner day 2 |
| 5 | **Pick your track** ("Where should I begin?") | Personal relevance | Day 2 | Email E5 |
| 6 | **Print your card or wall chart** | Physical cue in the home | Day 2 | Email E10 |
| 7 | **Say hello in the Courtyard, ask Chang Yin one question in the AI chat, or add your partner** (any counts) | Social commitment and personalisation | Day 3 | Email E9 |

Rules: the checklist never blocks content. Items can be done in any order. The card collapses (not disappears) after day 7 and reappears only if items 1 or 4 are still undone.

Key onboarding KPIs (targets, assumptions to validate): first session within 24h ≥ 70% of trials; Strength Age baseline within 72h ≥ 50%; 3+ sessions in first 7 days ≥ 45%; trial→paid ≥ 50% overall and ≥ 70% among members with 3+ sessions.

### 6.3a Ask Chang Yin / Ask Sun Yoon: chat disclosure copy (companion-chatbot law)

**First message of every chat session (fixed text, not generated):**
> I'm Chang Yin, an AI character made by the Strong Years team. I'm not a person, a doctor or a physical therapist. I can help you pick a session, swap an exercise or explain one. For anything about your health, please ask your doctor. If you're ever in crisis: call or text 988 (free, 24/7), or 911 in an emergency. How we handle safety: {{DOMAIN}}/safety

(Sun Yoon's version is the same with her name and "I can help with recipes and your kitchen plan.")

**Re-disclosure, at least every 3 hours of continuing conversation (New York GBL Art. 47), and after any gap of 30+ minutes:**
> A quick reminder: I'm an AI character, not a person. A real person on our team reads messages 7am–11pm Eastern if you'd like to talk to someone: [Talk to a person].

**Grief, relationships, mental health (Illinois WOPR Act, FUNNEL §4.14):** the chat doesn't counsel. Fixed reply: "That sounds hard, and it deserves a real person, not an AI. [Talk to a person on our team] If you're thinking about harming yourself, call or text 988 (free, 24/7). If you're in danger, call 911."

**Onboarding placement:** E1 adds one line: "You can also ask Chang Yin questions in the app. He's an AI character and he'll remind you of that. Our safety page: {{DOMAIN}}/safety." Checklist item 7 links to the chat with the first message above.

### 6.4 Variant: $7 Reset buyers

Control arm (7 days of Strong Years included): days 0–7 follow the Reset program (one email per day, same template, day number + session link + one teaching point) **and** the membership onboarding above (E1–E8), with E6 as the required 48-hour pre-billing reminder. Product-only arm: Reset emails only, each with one "What happens on day 8?" line linking to the "add your 7 free days" offer, then the bridge (6.6).

### 6.5 Variant: $17 Strong Kitchen buyers

Day 0 delivery email (all files + "Start with the soups"), then Sun Yoon's 5-email kitchen sequence (days 1, 2, 4, 6, 8: protein breakfast, soup day, after-meal walk, soft foods, "Chang Yin wants you in the garage"), alongside E1–E8 for the included 7 days of membership (control arm) or the bridge (product-only arm).

### 6.6 Buyer-to-member bridge (product-only split-test arm only)

**Bridge 1 (Reset day 5):** Subject: "Two days left in your Reset. Then what?" Body: honest framing that one week starts something and a routine keeps it, the offer (7 free days of Strong Years, then {{PRICE}}/mo, full terms), [Add my 7 free days].
**Bridge 2 (day 6):** Subject: "Your Strength Age, before and after" (if they took it) or "Take your Strength Age before day 7". The retest is the hook: "Members retest every month."
**Bridge 3 (day 7):** Sun Yoon: "Day 8 is tomorrow. You know what happens to plans with no day 8." Offer repeated.
**Bridge 4 (day 9):** Final: "We'll stop asking." Then they move to the free Sunday letter list (one session link a week), which is the evergreen nurture list. After that they're treated like quiz-only opt-ins (OFFER.md 2.1): ~10-day nurture ending in the $1 trial.

---

## 7. Retention system

### 7.1 The retention model and targets

The business model only works if members stay. Yang Mun's recurring product has 35 reviews; ours has to be the thing people do every morning.

**Targets (model base from ECONOMICS.md / OFFER.md 5.7; re-set after 60 days of data):**
| Metric | Benchmark | Model base | Goal |
|---|---|---|---|
| Trial → paid | 42.2% (Adapty H&F) | 42% paid / 48% organic | 50%+ |
| Still paying after renewal 1 | 59.2% | 62% | 70% |
| Still paying after renewal 3 | 37.1% | 43% | 55% |
| Steady monthly churn | ~4.1–4.3% (Recurly B2C) | 5.0% | 3.5% |
| Annual share of new payers | n/a | 10% | 15%+ |
| Chargeback rate | VAMP limit 1.5% | 0.35% | < 0.25% |
| Active rate (≥ 1 session/week) | n/a | n/a | ≥ 60% of paying members |

**What that's worth:** ECONOMICS.md puts 24-month contribution at ~$119 per paying member at $20/mo. The early survival curve (renewals 1–3) is where 40–60% of each cohort is lost, so it matters more than steady churn: moving steady churn from 5% to 3% improves LTV:CAC by only ~10%. Put the retention budget into the first 90 days.

**The core insight:** people don't cancel fitness memberships because of price; they cancel when they stop using them. So retention = usage. Every mechanic below exists to produce one of three things: a session today, a retest this month, or a reason to tell someone.

### 7.2 Habit loops

**Loop 1: The daily session (cue → routine → reward → investment)**
- **Cue:** one message at the member's chosen time, in their chosen channel (text is usually the strongest cue for this audience; test text vs. email vs. push by cohort). Always identical in structure so it becomes familiar: "Today: {type}, {minutes} min. {link}". Opening the link logs them in (magic link, no password).
- **Routine:** the session opens at their saved level, already playing after a 3-second countdown. No menu, no decisions. Length 8–12 min.
- **Reward (immediate and certain):** completion screen: big check mark, the day ticked on the calendar, weekly progress ("2 of 3 this week"), and Chang Yin's closing line, spoken and captioned ("That's your legs taken care of today.").
- **Reward (variable):** one in four completions shows a Sun Yoon "honest note", a rotating pool of ~200 short lines ("Chang Yin did his today too. He complained. You didn't. Good."), or a recipe that uses what most people have in the fridge. Variability keeps the completion screen worth seeing.
- **Investment:** after legs days, one optional tap: "How many reps did you do on the last set?" This builds a personal history that makes leaving feel like losing something.

**Loop 2: The weekly streak, not the daily streak.** Daily streaks punish this audience (a doctor's appointment breaks a 40-day chain and people quit out of shame). The streak unit is a **Strong Week = 3+ sessions in a Monday–Sunday week**. The home screen shows "Strong Weeks in a row: 6". One automatic "rest week" pass per 8 weeks (illness, travel); members can also mark "I was sick / traveling" to protect the streak.

**Loop 3: The kitchen loop.** Sunday recipes + grocery list → mid-week "Did you make it?" prompt → tap on the recipe card with a photo upload option → Sun Yoon's reply line (templated, fun, never pretending to see the photo). Photos (with permission) feed the community gallery.

**Loop 4: The household loop.** Couple add-on members (+$8/mo) see each other's weekly ticks (opt-in): "Tom did his session. Your turn?" OFFER.md assumes a household cancels less often than one person; validate in the first 60 days, and if the data agrees, make the add-on the most promoted feature after the Daily Practice itself.

### 7.3 Weekly rituals (rhythm matches OFFER.md 1.2)

| Day | Ritual | Channel | Purpose |
|---|---|---|---|
| Monday | **Strength** Daily Practice (legs-led; the flagship day) | Daily message + app | Anchors the week; legs drive Strength Age |
| Tuesday | **Mobility** (the gentlest day) | App | |
| Wednesday | **Balance** + **Wednesday Live Q&A**: 30 minutes, a real human coach answers member questions, introduced as a human. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Host named as `[PT NAME]`, PT, DPT or a named CSCS.] FALLBACK: "Host introduced by first name as "a coach on our team", with no credential claim." | App + live | Trust; appointment viewing; members see their questions answered |
| Thursday | **Strength** (upper body + grip) | App | |
| Friday | **Breath + qigong flow** (slow, with tai chi weight shifts) | App | Likely the most-loved session; social posts from members |
| Saturday | **Walk-and-talk**: Chang Yin walks the seaside promenade and talks while you walk yours | App (audio-friendly) | Low-effort weekend bridge |
| Sunday | **Rest + stretch**, **Sun Yoon's Kitchen** (3 recipes, grocery list, one remedy with an evidence grade), **Sunday Premiere** (20-minute episode with live chat), weekly recap ("This week: 4 sessions, 41 minutes, Strong Week #6") | Email + app + SMS from Sun Yoon | The weekly touchpoint that reaches inactive members |

### 7.4 The monthly Strength Age retest (the core retention mechanic)

**Why it works:** it turns an invisible benefit into a number, gives every month a finish line, and creates a reason to come back even for members who've lapsed ("just do the test").

**Retest Day = the 1st of every month** (members who joined in the last 14 days are skipped until next month).
- **Day −3 (email + text):** "Retest Day is {weekday}. Chair against the wall, 3 minutes. Last month: {SA}."
- **Day 0 (morning text):** "Strong Years: It's Retest Day! 3 minutes, one chair, one counter. {link}". The day's session *is* the retest plus a short celebration flow.
- **In-app flow:** the 6 at-home tests from OFFER.md 1.2 (30-second chair stand, 4-stage balance, 2-minute step test, arm curl with a water bottle, sit-and-reach, timed up-and-go). Strength Age is still computed from the chair stand and balance stage (same formula as Quiz A) so the number stays comparable with the quiz baseline; the other four are charted as their own lines. Then the chart updates with an animated line from last month.
- **Result screen language:**
  - Improved: "You did {reps} stands, {delta} more than last month, and held {stage_name} (last month: {prev_stage}). Your Strength Age moved from {prev} to {now}. Some early gains come from practice with the test itself; the trend over several months is what counts. Print your certificate?" (Always show the stand and balance changes first. Cap the displayed Strength Age change at 3 years per month; anything more is shown as "3+".) Certificate: large-print, name, month, both numbers, signed "Chang Yin and Sun Yoon (AI characters)" + [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: " · reviewed by [PT NAME], PT, DPT"] FALLBACK: "(no review line)".
  - Same: "Holding steady is a result. Most people lose strength every year; you didn't this month. Want Chang Yin to move you up a level in legs sessions?"
  - Worse (by 1–4 years): "Numbers move around: sleep, a cold, a busy month. Let's look at your month: you did {n} sessions. Aim for 3 a week this month and retest on the 1st."
  - Worse by 5+ years, or reps down by 4+, or balance down 2 stages: "That's a bigger change than usual. It may be nothing, but sudden changes in strength or balance are worth mentioning to your doctor, especially if you've been unwell, changed medicines or felt dizzy. For now we've set you to the Rebuild track." (Also triggers a human check-in email from the team.)
- **Day +1 email: "Your monthly report card"**: SA chart, sessions, minutes, Strong Weeks, favourite session, one recommendation for next month, the member's next goal (e.g. "10 seconds in heel-to-toe"), and, for monthly members with 2+ improvements, the annual offer.
- **Missed retest:** reminder on days 3 and 7 ("Still time for this month's test"); the retest window stays open until the 10th.
- **Aggregate data:** with consent, retest results feed an anonymized dataset that, after ≥ 200 members × 3 retests, becomes honest marketing proof ("members who did 12+ sessions a month improved their chair-stand count by a median of X"). Have a qualified reviewer check the analysis before publishing; [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "reviewed by our PT" may then be stated.] FALLBACK: "until then publish no review claim about it."

### 7.5 Milestone celebrations

| Milestone | Celebration | Channel |
|---|---|---|
| Session 1 | Chang Yin's welcome line + "First session" calendar badge | App |
| Session 3 | "Three. That's how habits start." + unlocks printable Strong Kitchen card | App + email |
| Session 10 | Sun Yoon's handwritten-style note (digital) + invite to community "10 Club" thread | App + email |
| First Strength Age improvement | Certificate + prompt to share (share card without numbers unless they choose) | App + email + SMS |
| Session 25 | Chang Yin video message (templated, name inserted with TTS; labelled AI) | App |
| 50 sessions | Choose a free bonus: Keep-Forever download of 5 sessions or the Soft-Food recipe collection | App |
| 100 sessions | **Mailed postcard from Sun Yoon** (physical, ~$1.50 all-in; printed, clearly from "the Strong Years team, on behalf of Sun Yoon, an AI character"; OFFER.md mails a printed certificate at 100 sessions, so send both in one envelope) + review ask (7.10) | Mail + email |
| 6 months membership | "Half a year" report card with all retests; annual offer at best price | Email |
| 1 year | Anniversary certificate + Strength Age year-in-review + referral ask ("Who should start their year today?") | Email + mail |
| 200, 365 sessions | Member name (first name + initial, opt-in) in the Sunday letter's "Strong Hall" | Email |

Rules: never celebrate with confetti-heavy UI that feels childish; the tone is warm and adult. Every celebration ends with one next action (today's session or next goal).

### 7.6 Community prompts

Community is hosted in-app (or Circle), moderated by humans, with Chang Yin and Sun Yoon posting only as clearly labelled characters making announcements ("Chang Yin (AI character)"), never replying to personal disclosures. Rules pinned: kindness, no medical advice between members, no selling, AI characters are characters.

Weekly rotating prompts (post Monday 9 am ET, human moderator seeds the first reply):
1. "What did your legs let you do this week that they didn't a month ago?"
2. "Show us your practice spot. Garage, kitchen, living room?" (photo)
3. "Sun Yoon's challenge: post the breakfast that got you to 25 grams of protein."
4. "Who are you getting stronger for?" (grandkids, spouse, yourself)
5. "What's the hardest movement for you right now? Chang Yin will pick three to make a video about."
6. "Retest week: share your change (numbers optional)."
7. "Your walking route this week, how far, and what you saw."
8. "What did your doctor or physical therapist say when you told them you're training?"
9. "Tell a new member one thing you wish you'd known in week one."
10. "Stairs report: how many without the rail?"
11. "Friday flow: where did you do it today?"
12. "One word for how you feel after a session."

Also: **Walking buddies** by ZIP code (opt-in; members see first name + town only and choose to connect; safety guidance to meet in public). **Couples board.** **"Starting over" thread** for returning members (normalizes lapses).

### 7.7 Re-engagement triggers by inactivity

Inactivity = no session and no retest. Messages stop the moment the member does anything.

| Days inactive | Channel | Message (full copy) |
|---|---|---|
| 3 | App push / SMS (their usual channel) | "Strong Years: 3 minutes today? Chang Yin kept your spot: {link}" |
| 5 | Email, from Chang Yin | Subject: "I made you a short one." Body: "{first_name}, it's been a few days, which happens to everyone. I made today's session 5 minutes on the Rebuild track, so there's nothing to think about. Press play and you're back. [5-minute session] Chang Yin" |
| 7 | SMS | "Strong Years (Sun Yoon): One week. I'm not angry. I'm making soup. Do 5 minutes and come eat. {link}" |
| 10 | Email, from Sun Yoon | Subject: "Is something wrong?" Body: "{first_name}, a week and a half without a session usually means one of three things: you're unwell, you're busy, or it stopped being right for you. If you're unwell: rest, and when you're ready, start on the Rebuild track. [Set me to Rebuild] If you're busy: three 8-minute sessions a week is enough. [Switch reminders to 3 days a week] If it's not right for you: tell us why in one line, or pause your membership for a month for free. [Pause] Sun Yoon" |
| 14 | Email + in-app | "Pause instead of paying for nothing" (honest): "You haven't used Strong Years in two weeks. We'd rather you pause than pay for something you're not using. Pause for 1, 2 or 3 months with one tap; your history and Strength Age are saved. [Pause my membership] Or come back with today's session: [Start]" |
| 21 | Email from the team (plain text, signed by a real human) | "Hi {first_name}, this is [Name] from the Strong Years team, a real person. I noticed you haven't been in for a few weeks and wanted to check nothing's wrong with the program: a video not playing, a movement that hurt, anything. Just reply to this and I'll sort it out personally." |
| 28 | Email (before next bill, only if 0 sessions in the billing period) | "Your next payment is on {date}. You haven't used your membership this month, so here are your choices: keep going [Today's session], pause free [Pause], move to Essentials at $12 [Switch], or cancel [Cancel]. No pressure either way." |
| Retest day | All channels | Lapsed members are always invited to Retest Day; it's the easiest way back. |

The day-14 pause email and the day-28 "you haven't used it" email cost some revenue in the short term. They buy trust, fewer chargebacks and refund requests, better reviews, and a much higher return rate later. For an audience burned by subscription traps, this is a moat.

### 7.8 Cancellation flow (compliant, never obstructive)

**Canonical rule (same in OFFER.md and SAFETY_RULES.md):** cancel online in at most two screens: one save offer shown next to an equally prominent "Finish canceling" button. Screen 1 is an optional one-tap reason (skippable); screen 2 is the single save offer beside "Finish canceling". The confirmation below appears only after the membership is already cancelled; it is not a third step.

**Entry points:** Account → Membership → "Cancel membership" (same visual weight as other account buttons), the link in every billing email, and replying "cancel" to any email (processed by a human or automation within 1 business day, cancellation effective from the reply date).

**Screen 1: "We'll cancel it right now. Can we ask why?" (optional)**
Reasons (one tap, or "Skip and cancel"):
- It's too expensive
- I don't have time
- I'm not using it enough
- It's too hard / too easy
- I'm injured or unwell
- I'm traveling
- I want a real person / something different
- Other

**Screen 2: one tailored option + finish button (both buttons identical in size; "Finish canceling" is Ink on Rice with a 2px Ink border, same height as the option button)**

| Reason | Offer shown |
|---|---|
| Too expensive | "Switch to Essentials for $12/month: the daily session and monthly retest, without recipes and community." [Switch to $12] |
| No time / not using it | "Pause for 1, 2 or 3 months, free. Nothing is charged while paused, and we'll remind you a week before it restarts." [Pause] |
| Too hard / too easy | "Let us fix the level: the Rebuild track (everything seated) or Strong/Iron (more challenge). Try it for a week." [Change my track] |
| Injured or unwell | "We're sorry. Pause free for up to 3 months while you recover, and when you come back, we'll start you on the Rebuild track. Please follow your doctor's advice." [Pause] |
| Traveling | "Pause for the length of your trip, or keep going with our 10-minute hotel-room sessions." [Pause] |
| Want a real person | "Strong Years Plus ($30/mo) adds a monthly 10-minute video check-in with a real human coach and a small-group live." [See Plus] |
| Member 60+ days, any reason (one time only) | Standard mode: "Switch to yearly at $119 (about $9.92 a month)." Blitz mode: pause first; the founding annual ($249, client decision) only after renewal 1. [Switch to yearly] |
| Other | Pause offer |

Beneath every offer: **[Finish canceling]**. Tapping it cancels immediately. No third screen, no "are you sure?" loop.

**After canceling: confirmation (shown once cancelled; not a step)**
> "Your membership is cancelled. You won't be charged again. You have access until {period_end}. Your streak, Strength Age history and what the coach remembers are saved for 90 days if you come back. [Undo cancellation] [Back to today's session]"
> Plus: "Within 14 days of your first membership charge? You can get a full refund here: [Refund my payment]." (One per person.)
Cancellation email (5.5 F) sent immediately.

**Guardrails:** max one save offer per cancellation; no required chat, call, survey or password re-entry beyond the normal login; process by end of day; test the flow quarterly on mobile with a 70+ tester. Measure save rate (target 20–30% via pause/downgrade), but never optimize by adding friction.

**Price lock:** members keep their signup price for as long as they stay subscribed. Mention it in the cancel flow only as a fact: "If you cancel and return later, you'll pay the current price, which may be higher." (Only true if prices actually rise; don't say it otherwise.)

### 7.9 Winback sequence (5 emails after cancellation)

Excludes: anyone who requested a refund with a complaint, anyone flagged for a medical issue, anyone who unsubscribed.

**W1. Day 3 after cancellation** (from Sun Yoon)
Subject: I kept your spot at the table
> {first_name}, you've cancelled, and that's fine. I only want to say one thing: your streak and Strength Age history are saved for 90 days. {If they improved: "You went from {x} to {y}. That's real."} If you ever want to come back, everything is where you left it.
> And here is a free session, no membership needed, because you should keep your legs either way: [Free 8-minute session]
> Sun Yoon

**W2. Day 10** (from Chang Yin)
Subject: A 30-second check (free)
> {first_name}, it's been a little while. Chair against the wall, arms crossed, 30 seconds. How many? Your last number was {reps}.
> [Log my number]
> Strength fades slowly when we stop, and comes back faster than it was built the first time. If you'd like to come back, your first month is $1 for 7 days again.
> [Come back for $1]

**W3. Day 21** (from the team; addresses the stated cancel reason)
Subject: You told us "{reason}". We listened.
> Variants by reason: Too expensive → "Essentials is $12/month, or yearly is $119 (about $9.92/month) with everything." Too hard → "We've added {n} new Rebuild-track sessions since you left." No time → "Our new 5-minute sessions." Want a real person → "Strong Years Plus: a monthly 10-minute check-in with a human coach." New program launched → name it (OFFER.md 5.6). Offer: "$1 for your first month back." (Only claim changes that actually happened.)
> [Come back: {tailored offer}]

**W4. Day 60** (from Sun Yoon)
Subject: Chang Yin asked about you
> Playful, honest line: "He didn't, actually. He's an AI character, and so am I. But the people on our team did notice you're gone." Then: a new recipe, a free recipe pack from Sun Yoon, and the new month's retest invitation (free, no login needed). No price offer in this one (OFFER.md 5.6: day 90 is a gift + retest prompt).
(Tone note: this "breaking the fourth wall" humor is on-brand and reinforces our honesty. Test it vs. a straight version.)

**W5. Day 90–180** (from the team; send at day 90 if no founding price is running, otherwise at day 180)
Subject: One last note from us
> "We'll stop emailing about coming back after this. If you ever want Strong Years again, it's at {{DOMAIN}}/return, where you can restart anytime. (Your saved history was kept for 90 days after cancelling.) If you'd like the free Sunday letter from Sun Yoon, with one free session each week, you're welcome to stay on that list: [Keep the Sunday letter] [Unsubscribe from everything]"
> Offer: the yearly plan at the lowest annual price live at the time (one time only; the OFFER.md 5.6 day-180 touch can repeat it).

Winback target (assumption): 8–15% of cancelled members reactivate within 90 days; reactivated members churn faster, so push them to annual.

### 7.10 Real-review collection system (FTC-compliant)

**Principles:** ask every eligible member, not just happy ones (selective asking is fine for timing, but never gate by sentiment: no "if you're happy, review us; if not, email us" routing); publish all reviews that meet content rules including negative ones; no incentives conditioned on positive sentiment; disclose any incentive; no employee or family reviews without disclosure; never write, edit (beyond typo-free display with permission) or AI-generate reviews.

**Flow:**
1. **Trigger moments:** 30 days of membership with ≥ 8 sessions; first Strength Age improvement; 100th session; 6-month anniversary. Max one ask per 60 days.
2. **In-app ask (1 screen):** "Would you tell other people what Strong Years has been like for you? Honest reviews help people decide, good or bad." [Write a review] [Not now]
3. **Review form:** star rating (1–5), text box ("What's changed for you, if anything? What could be better?"), optional photo, optional age, and three consent checkboxes (all unchecked):
   - "You may publish my review on your website with my first name and last initial."
   - "You may also use it in ads and social media." (separate consent for ads)
   - "You may show my age / my Strength Age change." (separate)
4. **Verification badge:** "Verified member since {month year}" pulled from billing records, shown on every published review.
5. **Incentive (optional, disclosed):** every reviewer, regardless of rating, gets a free month; each published review carries "Received a free month for leaving a review (any rating)."
6. **Publishing:** all reviews appear on `/reviews` with average rating and count computed from everything received (excluding only reviews that break content rules: profanity, personal medical details about others, spam). Content rule exclusions are logged.
7. **Health claim screening:** a member saying "my blood pressure dropped" is their experience, but using it in ads makes it our claim. Reviews with disease or medical outcome statements can appear on the reviews page (with "Individual experience; not a typical result; not medical advice") but are never used in ads or landing pages.
8. **Video testimonials:** invite members with 3+ months and an improved retest to a paid (disclosed) 15-minute recorded video call with a human producer. They say what they want; we don't script. Use with written release. These become the highest-performing ad creative (ADS.md concept 20+).
9. **Third-party reviews:** invite a random sample of members (not selected by sentiment) to review on Trustpilot/Google after 60 days. Same rules.

### 7.11 Annual-upgrade campaign (OFFER.md 5.5)

**Who and when:** at trial end (inside the 48-hour reminder and the day-7 welcome), on days 21, 45 and 75, and after a member's second Strength Age improvement. Only to members with ≥ 6 sessions in the last 30 days at days 45/75 (don't push a year on people who aren't using it). Never at the first cold-traffic checkout.

**Offer:** **$119/year** (≈ $9.92/month; about half of 12 × $20 = $240) with price lock for as long as they stay on yearly. In blitz mode the founding annual is **$249** (≈ 10 months at $25; AUDIT F07; client decision), offered only after renewal 1 (from L35). Credit unused days of the current month on switch (prorated). 30-day refund applies to the annual charge. Annual price test cells after monthly testing: $99 / **$119 control** / $149.

**Sequence (per wave, 4 touches over 7 days):**
1. **In-app card on Retest Day +1** (strongest moment): "You're {n} years younger than at signup. Lock in the price for a year: $119 instead of $240." [Switch to yearly]
2. **Email (Chang Yin):** Subject: "Your next 12 months, planned." Body: the 12-month roadmap (four 12-week programs back to back, e.g. Strong at 70 → Balance & Steady Feet → Grip & Hands → Walk Stronger), their chart so far, the savings math ($240 vs $119, save $121), terms line: "$119 today, renews yearly at $119 until you cancel; reminder before renewal." [Switch to yearly]
3. **SMS:** "Strong Years: Switch to yearly, $119 (save $121 vs monthly). {link}. Reply STOP to opt out."
4. **Email (Sun Yoon), day 7:** Subject: "Do the math with me." Honest: "$121 a year is a lot of tofu. If you're doing your sessions, yearly is cheaper. If you're not sure you'll keep going, stay monthly. I mean it." [Switch to yearly] [Stay monthly]

**Seasonal waves:** New Year ("Your strongest year"), Mother's/Father's Day and Grandparents Day (gift-annual push), Q4: "buy a year for Mom, get a year for yourself at 50% off" (OFFER.md 5.5).

Model base: 10% of new payers take annual; 30% of annual members renew at month 12 (ECONOMICS.md). Goal: 15%+ annual share.

### 7.12 Referral and gift-a-membership program (the adult-children engine)

**Referral ("Bring someone stronger with you"):**
- Every member gets a personal link and a printable card with a QR code (this audience shares on paper and by text more than by link).
- **Friend gets:** 14 days for $1 (instead of 7).
- **Member gets:** one free month when the friend becomes a paying member (after their first full charge, to avoid abuse). Unlimited.
- Share prompts at: first Strength Age improvement, milestone 25, retest days, and after a 5-star review ("Would you like to share Strong Years with someone?").
- Share copy prefilled for text message: "I've been doing 10-minute strength sessions every morning with this, and my legs are noticeably stronger. The teacher is an AI character, and it says so. 14 days for $1 with my link: {link}" [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: (may add: "and it's checked by a physical therapist")] FALLBACK: "(no review wording)"
- Disclosure: referral rewards are disclosed in the share page and in any public sharing ("I get a free month if you join").

**Gift a membership (sold to adult children 35–55 and caregivers):**
- **Products (OFFER.md):** 3 months $49 · 12 months $119, prepaid. Kit ($29) offered first in the gift upsell flow. Gifts never auto-renew.
- **Gift page `/gift` headline:** "Give your mom or dad a stronger year." Subhead: "A patient teacher every morning, safe for every level, and a monthly test you can do together on a video call."
- **Delivery options:** email card from Sun Yoon on a chosen date; printed card mailed ($3.95); or "I'll give it in person" (printable certificate with QR code).
- **Setup help:** the gifter can pre-fill the recipient's name, phone and preferred reminder time, and choose "Help me set it up" which sends the recipient a 1-page large-print guide and offers a human phone setup call (15 min, booked; the one place a phone call helps rather than traps).
- **Gifter loop (with the recipient's permission, asked at their first login):** "Would you like {gifter_name} to get a note when you finish sessions and retests? (Numbers are never shared unless you choose.)" If yes, the gifter gets a monthly one-line update (OFFER.md 1.2): "Mom did 18 sessions this month." This is the adult-child hook, and it's opt-in by the parent.
- **Gift expiry path:** 21 and 7 days before the gift ends: to the recipient: "Keep going on your own plan: {{PRICE}}/month or $119/year" (fresh consent at checkout, on the recipient's own card); to the gifter: "Extend {name}'s gift: 3 months $49, 12 months $119."
- **Couple / family add-on:** +$8/month adds a partner with their own level and progress, plus a family dashboard for adult children (only with the parent's consent). Test later: a two-household family plan for adult children paying for parents in another home while doing it themselves.

**Occasions calendar for gift pushes:** Mother's Day (from mid-April), Father's Day (from late May), Grandparents Day (September), Thanksgiving/holiday season (Nov 1–Dec 23), birthdays (gifter can schedule). (No "after a fall" occasion: gift copy never references falls; see ADS.md §1 rule 4.)

### 7.13 Retention dashboard (review weekly)

| Metric | Definition | Alert threshold |
|---|---|---|
| D1 activation | % of new trials with a session in 24h | < 60% |
| Baseline rate | % with Strength Age in 72h | < 45% |
| Trial→paid | by cohort, price cell, source | < 45% |
| Weekly active | % paying members with ≥ 1 session in last 7 days | < 55% |
| Strong Week rate | % with ≥ 3 sessions in last week | < 30% |
| Retest participation | % of eligible members who retest by the 10th | < 40% |
| Monthly churn | cancellations ÷ members at start of month, by tenure | > 8% (month 4+) |
| Pause rate / return from pause | | return < 50% |
| Refund rate | refunds ÷ first charges | > 6% |
| Chargeback rate | | > 0.4% (danger at 0.65–1%) |
| NPS / one-word reply mix | | NPS < 40 |
| Annual share of new payers | | < 10% (model base) |
| Referral rate | referred trials ÷ total trials | < 8% |
