# OFFER.md — Chang Yin & Sun Yoon: offer architecture

Companion files: `economics.xlsx` (live model), `mrr_scenarios.csv`, `ECONOMICS.md` (verdict).
Every price, take rate and conversion rate below is also an input on the `Assumptions` sheet, so the offer and the model can't drift apart.

**Audit fixes (Sep 30 2026).** The canonical policies at the top of FUNNEL.md (SMS-conditional copy, 14-day money-back guarantee one per person, add-on refund terms, bonus vesting on day 15, reminders before every renewal, the California annual reminder, founding-price wording, the founding cap and counter display rule, human coverage hours, AI-chat law, quiet hours, the one quiz spec) override any older line here. `{{IF_SMS: …}}` = rendered only when `SMS_ENABLED=true`.

---

## 0. The recommendation on one screen

**Baseline offer (non-blitz / organic; app `OFFER_MODE=standard`).** This table is the steady-state funnel and the organic baseline. During the launch blitz, §0.1 (blitz mode) overrides it; nothing here is deleted.

| Layer | What | Price | Role |
|---|---|---|---|
| Entry (free) | 90-second **Strength Age Quiz** → personalised plan + estimated "strength age" | $0 | Opt-in (email + SMS). Every organic keyword DM lands here. |
| Front end A (default) | **7 days of Strong Years for $1** | $1 → $20/mo | Main path to monthly recurring revenue (MRR); ~50% of starts |
| Front end B | **7-Day Strength Reset** (7 follow-along sessions + printable plan) *with 7 days of membership included* | $7 → $20/mo | Buyers who want to own something; ~35% of starts |
| Front end C | **Sun Yoon's Strong Kitchen + Chang Yin's 12-Week Printable** bundle *with 7 days of membership included* | $17 → $20/mo | Recipe-led traffic (food reels); ~15% of starts |
| Order bump | Printable 12-week wall plan + weekly grocery lists | $9 | ~30% take |
| Upsell 1 | 12-week program of their choice (lifetime access, even after cancelling) | $27 | ~10% take |
| Upsell 2 | Physical kit: 3 resistance loops + door anchor + grip trainer | $29 | ~6% take (margin ~$17) |
| Downsell | Printables only | $7 | ~5% take |
| Core membership | **Strong Years** — monthly | **$20/mo** (test $12–30) | The business |
| Annual | Strong Years annual | **$119/yr** (test $79–199) | ~10% at checkout, trial end or day 21–75 campaigns |
| Gift | "Give Mom & Dad Strong Years": 3 months $49 / 12 months $119, prepaid, **no auto-renew** | $49 / $119 | Adult children aged 35–55 as buyers |
| Later (month 7) | Supplement subscribe & save, sold inside the membership only | $29–45/mo | Separate profit centre. Never on the front end. |

Everything is cheaper to enter than Yang Mun's offers ($19.99 ebook bundle, $49.99 Journey). Every path ends in a subscription that the buyer has clearly agreed to, and every path can be cancelled online in at most two screens (one save offer shown next to an equally prominent "Finish canceling" button).

### 0.1 Launch ladder (CANON UPDATE 2 + CANON UPDATE 3, Oct 1 2026; BRIEF.md; supersedes the 3-cell / $1-trial blitz mode below)

Commerce runs on Strong Years' own **Shopify** store (Shopify Payments, free Shopify Subscriptions app; Shop Pay / Apple Pay / Google Pay / PayPal on; Stripe stays behind a provider adapter, not the launch path; no Whop). **There is no $1 trial. Ever.** The front end is a real product at a real price. App default: `OFFER_MODE=ladder`, `FRONT_END_DEFAULT_CELL=m12`. Model: BLITZ.md §13, `economics.xlsx` sheet `Organic_First` (runs R20–R26; R20 = cell B default, R22 = cell A test). Traffic: organic-first (runway 7–21 days with a free waitlist CTA; checkout opens to the waitlist + warm lists + organic; paid only boosts proven posts and retargets under the spend governor's caps; cold ads only after the BLITZ.md §11 gate). **Launch default = cell B; cell A = the test cell** (INTEGRATION.md has the platform facts and citations behind this order). PDFs are delivered by the members app, watermarked, once the `orders/paid` webhook grants access; Shopify's Digital Downloads app is not used (it cannot watermark).

| Layer | Launch ladder | Replaces |
|---|---|---|
| **Front end** | **Ebook bundle: 7-Day Strength Reset + Sun Yoon's Strong Kitchen, keep forever.** One-time Shopify product. Price cells **$7 / $12 / $15** (default display $12). Modelled conversion 5% of organic DM visitors at $12 (3% cold, 8% warm lists); $7 ×1.31, $15 ×0.89. | $7 / $17 bumps on a founding checkout; $1 trial |
| **Into MRR, cell B (LAUNCH DEFAULT)** | **"$12 today = books + first month, then $25/mo"** as ONE subscription purchase. **Mechanism (the only one the free Shopify Subscriptions app can bill):** the founding variant on the app's own "Monthly, renews until you cancel" plan plus the **STARTER12** discount code, $13 off the **first payment only** (`recurringCycleLimit: 1`), once per customer, auto-applied by the `/discount/STARTER12` share link every `/b` and `/join` redirect goes through and re-applied by the product page's offer form; after the founding close the standard product carries **STARTER12S** ($23 off → $12, then $35). The product page shows "$12 today, then $25 a month" and the checkout total is $12: the displayed price equals the charged price, and the renewal price is the plan price. (A fixed-first-cycle selling plan is only possible when our own app owns the plans and runs billing: `SUBSCRIPTION_ENGINE=app`, not the launch path.) ROSCA/state auto-renew: price, cadence, cancel path and the first renewal date stated at the checkout, express consent, email reminder before the first $25 charge, online cancel in ≤ 2 screens. Modelled at 0.70 × the one-time ebook purchase rate and 50% survival of the first $25 charge. ~20× cell A's MRR per visitor and the only cell on which paid amplification pays back or graduates (BLITZ.md §13.7). | F25 / F30 / T25 cells |
| **Into MRR, cell A (TEST CELL)** | **Books only** ($12 one-time) → the founding offer (**$25/mo, first month charged at that checkout**) on the **thank-you page** and in the **3 onboarding emails**; a new Shopify checkout with the terms box and the consent tick. Modelled: 4% of ebook orders within 7 days. **The one-click post-purchase app stays scaffolded but OFF at launch** (shopify.dev "About product offers"): it is beta and a live store needs access approval; the page is never shown for Apple Pay / Google Pay / PayPal / installments; and a subscription cannot be added post-purchase to an order with no shipping address, which every digital-only books order is. If it is ever switched on (card-only, address collected, approved), the model's 12% accept lifts cell A to ~$1.4K on day 30, still far below cell B. | — |
| **Gate** | Day-10 / day-40 gates pick the winning cell by **net revenue per visitor and renewal 1**, not by day-1 MRR. | Day-10 gate on charge-today factor |
| **Membership** | **Founding $25/mo** (test $30 only if cell data supports it), **locked for as long as you stay subscribed** (never "for life"); **honest 5,000 cap = inventory on the founding selling plan**; **$35 standard after the cap**; **founding annual $249 offered after renewal 1** (5% assumption); **Essentials $12/mo** as the save offer; gifts **$49 / 3 mo, $119 / 12 mo** one-time, no auto-renew. **14-day money-back guarantee on the membership charge, once per person.** | same, except the trial path |
| **Cart bumps** (optional, never required) | **$9** wall plan + grocery lists (30% take) · **$29** resistance kit, physical, Shopify ships (6% take, $12 COGS). Supplements only inside the membership from month 4+. | $9 bump, $27 / $29 upsells, $7 downsell |
| **Fees** | Shopify Payments on Basic: **2.9% + 30¢** online card rate (shopify.com/pricing); Shopify Subscriptions free; $15 chargebacks; payouts 3 business days (up to 5 for new merchants); Shopify may hold a reserve on a new account (modelled 10% / 90 days). | Stripe 2.9% + 30¢ + 0.7% Billing |
| **Members area** | Ours (Next.js at members.<domain>): Shopify webhooks provision and revoke access in Supabase from the store-wide topics only (`orders/paid` incl. every renewal order, `orders/cancelled`, `refunds/create`, `customers/update|delete`, `inventory_levels/update`, `app/uninstalled`; `subscription_contracts/*` and billing-attempt topics fire only for the owning app, so they are enrichment, never the source of truth); sign-in by email code / magic link matched to the Shopify customer email. | Stripe-provisioned |
| **Messaging at launch** | Email + DM + web push; SMS when 10DLC is approved (`SMS_ENABLED=false` until then). | same |

**What the model says (BLITZ.md §13, central inputs):** cell B (the default, R20) is ~$9K MRR on day 30 ($4.6K retained) with $6.6K of front-end cash and no media; cell A (the test cell, R22, post-purchase off) is ~$0.5K MRR but $9.4K of ebook cash; cell B + $1,500/day boosts/retargeting + 2 shoutouts/day (R23) reaches $10K on day 6, $50K on day 26 and $100K on day 59 at a −$185K low; a 20K-name seeded waitlist pulls $100K to day 30. The client's dates need a seeded audience or cold Meta on upside inputs.

### 0.1-old Blitz mode — SUPERSEDED on Oct 1 2026 by §0.1 above (kept as history; the $1 trial T25 cell, the F25/F30 charge-today cells and the $7/$17 order bumps are no longer the launch structure)


The blitz optimises for MRR speed **and** payback: charge-today books MRR sooner, the $1 trial pays back ~2× faster on central inputs (BLITZ.md Payback sheet), so the launch runs **both as live cells from L1** and lets the day-10 and day-40 gates choose. App default: `OFFER_MODE=blitz`. Models: BLITZ.md, `economics.xlsx` (Blitz, Blitz_Plan). Operations: BLITZ_OPS.md. Funnel copy: FUNNEL.md §0.2.1, §4.17, §5.6.

| Layer | Blitz mode | Baseline it replaces (above) |
|---|---|---|
| **Primary offer** | **Founding Membership**: first month **charged today** at the founding price, renews monthly at the same price until cancelled. **14-day money-back guarantee on the membership charge, one per person** (self-serve refund in the account). **Founding price locked while the member stays subscribed, pauses included** (never "for life"). **Honest cap: the first 5,000 founding members or `{{FOUNDING_CLOSE_DATE}}` (default L90; client decision), whichever comes first** (configurable `FOUNDING_COHORT_CAP`; the counter reads the real database count; never reset, extended or "reopened"; public display follows the FUNNEL.md `{{COUNT_LINE}}` rule). Checkout: `/join`. | $1 × 7-day trial → $20/mo |
| **Launch cells (from L1)** | **Three live cells, sticky per visitor:** F25 founding charge-today $25 · F30 founding charge-today $30 · T25 $1 for 7 days, then $25 as a founding member. **50% founding / 50% trial** (paid: 25/25/50; non-paid: F25 50%, T25 50%). $25 vs $30 is read inside the founding cells; nobody is ever moved up. Charge-today vs trial is decided by net revenue per visitor and payback at the **BLITZ.md §11 day-10 and day-40 gates** (FUNNEL.md §0.2.1 has the thresholds). | $20 control, $12–30 test matrix (§2.4) |
| **Standard price after the cap closes** | **Configurable, default $35/mo** (`STANDARD_PRICE_CENTS=3500`). **Client decision.** "Founding price locked" is only honest if this later price is real and actually charged (16 CFR 233); if it won't be, drop the founding-price language and sell founding perks only. | — |
| **$7 Strength Reset / $17 Strong Kitchen** | **Order bumps** on the founding checkout ($7 / $17), not standalone trial offers. Standalone `/reset` and `/kitchen` pages stay built but are off by default (they redirect to `/join`). | Front ends B and C with 7 days of membership included |
| **$9 Wall Plan bump, $27 / $29 upsells, $7 downsell** | Unchanged | same |
| **$1 7-day trial** | **Live from L1 as cell T25** (`TRIAL_ARM_ENABLED=true`, `ARM_B_SHARE=0.5`): $1 for 7 days, then $25/mo, founding price locked from the first full charge while the cohort is open. The model's Payback sheet shows it pays back ~2× faster than charge-today on central inputs. Goes to 100% if charge-today fails the day-10 gate. | Front end A (default) |
| **Gift** | **Unchanged**: 3 months $49 / 12 months $119, prepaid, no auto-renew. Not counted in MRR. | same |
| **Annual** | **Founding annual $249/yr** (≈ 10 months at $25; AUDIT F07: $99 was 67–72% off the founding monthly price and broke the ≈6× rule). Offered only **after renewal 1 (from L35)**. **Client decision.** Annual share and save-offer downgrades must be modelled in Blitz. | Trial end + day 21/45/75 |
| **Refunds** | 14-day money-back guarantee on the membership charge, one per person, self-serve. Add-ons ($7, $17, $9 bumps; $27 and $7 upsells) are watermarked digital downloads, refunded on request within 14 days; the kit 30 days. The founding-week keep-forever program download unlocks on day 15. "Guarantee" appears only as "14-day money-back guarantee" / "money-back guarantee" describing the refund policy, never next to a health outcome. | Same policy (the 30-day standard-mode guarantee is retired) |
| **Messaging at launch** | **Email + DM only.** 10DLC / toll-free SMS verification takes **3–6 weeks**, so SMS switches on when approved (`SMS_ENABLED=false` until then). Every pre-charge and pre-renewal reminder goes **by email** until SMS is live. | Email + SMS |

The $20 price, the $1 trial and the $7/$17 front ends in the rest of this file remain the **pre-canon baseline** for history; CANON UPDATE 2 removes the $1 trial from every mode (`OFFER_MODE=standard` is retained in the app only for the organic $20 price point; the ladder in §0.1 is the launch structure).

---

## 1. The membership

### 1.1 Name

| Candidate | Why it works | Risk |
|---|---|---|
| **Strong Years** *(recommended)* | Outcome and identity in two words ("these are my strong years"). Doesn't depend on age, religion or ethnicity. Translates cleanly: *Años Fuertes* (ES), *Starke Jahre* (DE), *Anos Fortes* (PT). Works as a brand when Chang Yin is swapped for another archetype. | Generic words, so trademark "STRONG YEARS" for the class 41 fitness-instruction category and check the .com/.app. Fallback: "Strong Years Club". |
| The Courtyard | Named after the set. Warm and communal. | Says nothing about the outcome. |
| Second Strength | Strong promise. | Implies they lost their strength, which can put people off. |
| Evergreen Strength | Positive and about longevity. | Sounds like a supplement brand. |
| Yin & Yoon Daily | Uses the characters' names. | Only works for these characters, so it doesn't clone to new ones. |

**Positioning line:** [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: *"Daily strength, balance and kitchen wisdom for your 60s, 70s and beyond. Coached by Chang Yin and Sun Yoon, AI characters, with every session and recipe reviewed by licensed physical therapists and dietitians."*] FALLBACK: *"Daily strength, balance and kitchen wisdom for your 60s, 70s and beyond. Coached by Chang Yin and Sun Yoon, AI characters, with every session and recipe built on published guidelines for older adults."*

**Heritage (keeps the client's names):** make the characters an openly fictional Chinese–Korean married couple. Chang Yin draws on Chinese movement traditions (tai chi, qigong, baduanjin) combined with modern progressive strength training. Sun Yoon draws on Korean home cooking (fermented foods, soups, banchan-style vegetables), which fits naturally with a "Gut Reset". The "About" page, bio and pinned post say they are AI characters with a fictional story. No temple, no robes, no clergy, no "six decades of practice" presented as fact. Use a paid cultural reviewer from each heritage for names, food, set dressing and captions.

### 1.2 What's inside: feature → cost → value → retention

"Cost" is the monthly cost of delivering it to one member, taken from `Assumptions` section G. The total is **≈ $0.81 per member per month**, plus **$0.40 for human coaching and support**, which comes to about 6–7% of a $20 price.

| # | Feature | What exactly | Delivery cost/member/mo | Perceived-value driver | Retention mechanism |
|---|---|---|---|---|---|
| 1 | **Daily Session** | 8–12 min follow-along video with Chang Yin. The day rotates: Mon strength, Tue mobility, Wed balance, Thu strength, Fri breath + qigong flow, Sat walk-and-talk, Sun rest + stretch. Auto-levelled from 4 tracks: **Rebuild** (chair-based), **Steady**, **Strong**, **Iron**. A "sore knee / sore back / low energy today" button swaps in a modified version. | ~$0.29 video delivery (Mux) | "A coach who knows me, every day." A personal trainer costs $60–100 a session. | **Habit** (same time, same place, same face), **personalisation** |
| 2 | **12-week programs** | *Strong at 70*, *Back Strong* (a back-friendly strength program; say "move with less stiffness", never "fix back pain"), *Balance & Steady Feet* (Otago-style progressions + tai chi), *Gut Reset with Sun Yoon* (fibre, fermented foods, protein at every meal), *Grip & Hands*, *Walk Stronger*. One active program at a time, with a week number on the dashboard. | ~$0 (same video pipeline) | Something they can finish. People value a structured program 3–5× more than a content library. | **Sunk progress** ("week 7 of 12"), **identity** |
| 3 | **Sun Yoon's Kitchen** | Every Sunday: 3 recipes + a printable grocery list + one "remedy" with an **evidence note**. The note grades the remedy: *good evidence / some evidence / tradition only, enjoy it as food*. That honest grading is the difference from Yang Mun's onion water. Protein target per meal for older adults. | ~$0 | Blunt, warm, practical. The grocery list is useful as a household object. | **Variable reward** (what's Sunday's recipe?), **social** (people cook for their family) |
| 4 | **Daily coach message** | SMS by default (email or WhatsApp by choice): a 1–2 line nudge + link to today's session, in the character's voice, signed "— Chang Yin (AI coach)". A Sunday message from Sun Yoon. | ~$0.21 SMS (55% opt-in × 30 × $0.0125) | "Someone checks on me." | **Habit trigger**, and the main tool against churn |
| 5 | **Ask Chang Yin / Ask Sun Yoon** (AI chat) | Text chat + optional voice-note replies. It remembers the member's level, injuries, goals and grandkids' names *if the member opts in*. It can swap exercises, adapt recipes and explain why. Hard limits in §1.4. | ~$0.07 AI (Claude Haiku 4.5, cached) + ~$0.10 voice | The feature with the biggest gap between cost and perceived value: people pay $8–16/mo for companion apps just for the memory (BRIEF). | **Personalisation**, **relationship**. Memory is also a switching cost. |
| 6 | **Strength Age re-test** (monthly) | 6 at-home tests: 30-second chair stand, 4-stage balance, 2-minute step test, arm curl (a water bottle is fine), sit-and-reach, timed up-and-go. The score is compared against published senior fitness norms and gives an estimated "strength age" and trend. It is framed as a fitness estimate, not a medical assessment. | ~$0 | A number that moves. It's shareable ("I'm 71 with a strength age of 63"). | **Sunk progress**, **variable reward**, **identity** |
| 7 | **Streaks & milestones** | Session streaks with "grace days" (for people in their 70s, a rigid streak that breaks makes them quit). Badges at 7/30/100 sessions; a printed certificate mailed at 100 sessions (~$1.50 each, well worth it). | ~$0.02 | Pride and proof. | **Sunk progress**, **identity** |
| 8 | **The Courtyard** (community) | In-app feed with prompts only ("post your chair-stand score", "what did you cook?"). Moderated by humans. No open DMs between members, which protects a 55–75 audience from romance scams. | in support cost | Belonging (AARP: 40% of adults 45+ are lonely, BRIEF) | **Social**, **identity** |
| 9 | **Sunday Premiere + Wednesday Live Q&A** | Sunday: a 20-minute pre-recorded episode "premieres" at a fixed time with live chat. Wednesday: a **real human** coach answers questions live for 30 minutes and is introduced as a human ([ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: introduced as a named DPT or CSCS] FALLBACK: "introduced by first name as a coach on our team, no credential claim"). Replays are kept. | ~$0.40 incl. support (in the model) | Real people behind the AI builds trust. Appointment viewing. | **Habit**, **social**, **trust** |
| 10 | **Printables** | Weekly plan, grocery list, exercise cards, a fridge "Strength Age" chart. | ~$0 | A physical reminder in the kitchen. | **Habit trigger** |
| 11 | **Couple / family plan** | +$8/mo adds a partner with their own level and progress; a family dashboard for adult children (with the parent's consent). | ~$0.81 | "We do it together." | **Social**; a household cancels less often than one person |
| 12 | **Gifting** | Prepaid gift from an adult child, with a printed or e-card from Sun Yoon. The adult child gets a monthly "Mom did 18 sessions" email if the parent consents. | ~$0.81 | Solves the gift problem for adult children. | Two people invested in one membership |

**What is cheap to deliver vs what drives value.** Almost everything that creates perceived value is fixed-cost content (sessions, programs, recipes) or code (personalisation, streaks, strength age). The only variable costs are SMS ($0.21), video ($0.29) and AI ($0.17 including voice). At 25,000 members, delivery plus human coaching is about **$30K/mo against ~$450K MRR**. The two most important retention features are the daily message and the monthly re-test, and they cost the least.

### 1.3 The value stack (honest anchors only)
Anchor against **real alternatives**, not against made-up "was" prices. Yang Mun's "was $38.97" is exactly the fictitious former price that the FTC Guides Against Deceptive Pricing (16 CFR 233) prohibit.
- A personal trainer 1× per week costs about $240–400/mo. A physical-therapy exercise program costs $30–60 in copays per visit. A meal-planning app costs $10–15/mo. SMS coaching costs $9.99–29/mo (BRIEF). An AI companion costs $8–16/mo (BRIEF).
- Copy: *"Less than one personal-training session a month, for a coach who shows up every single day."*

### 1.4 AI chat: required safeguards
Legally, the chat is a companion chatbot. California SB 243 has been in force since Jan 1 2026. It requires a clear disclosure that the user is talking to an AI, crisis-referral protocols, annual reports from July 1 2027, and it creates a private right of action worth $1,000 per violation ([Jones Walker](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/ai-regulatory-update-californias-sb-243-mandates-companion-ai-safety-and-accoun.html)). Other states are passing similar laws; have counsel confirm them. Build to the strictest standard everywhere:
1. **Disclosure.** Persistent "AI coach" label on the chat, the first message and every voice note: "I'm Chang Yin, an AI character. I'm not a doctor or physical therapist." Repeat it every session **and at least every 3 hours of continuing interaction** (New York GBL Art. 47, in force since Nov 2025; copy in FUNNEL.md §6.3a). Adults only (18+ gate at signup).
2. **Crisis protocol.** A classifier runs on every message for self-harm, abuse, acute medical emergency (chest pain, stroke signs, a fall with injury or head strike) and elder-abuse signals. It returns fixed referral text ("If you're thinking about harming yourself, call or text 988, free, 24/7. If you're in danger or it's a medical emergency, call 911." plus the Eldercare Locator for abuse), logs the event (needed for SB 243 reporting) and pages the team. **Human coverage is 7:00–23:00 Eastern, 7 days;** outside those hours the fixed text is the response and a person reads the message at 7:00. The copy never promises a human on call around the clock (buying 24/7 coverage is an open item in LAUNCH_CHECKLIST.md). The model never role-plays through a crisis. **The crisis protocol is published at `{{DOMAIN}}/safety`** (California SB 243), and annual reports start July 2027.
3. **Scope limits.** No diagnosis. No changes to medication, doses or timing ("ask your pharmacist"). No "stop taking X". No supplement advice that interacts with anticoagulants or diabetes drugs; it routes to a clinician instead. Red-flag symptoms get "stop and call your doctor today".
4. **Memory with consent.** Members can see and delete what it remembers ("What do you remember about me?"). Health details are treated as sensitive data under state consumer-health-data laws (e.g. Washington My Health My Data): opt-in, never shared with ad platforms.
5. **No dependency design.** No romantic framing, no guilt-tripping when a member leaves, and cancellation is never handled by the character's feelings ("I'll miss you" is banned in save flows).
6. **Human escalation.** "Talk to a human coach" is one tap away, answered within 24h (staffed 7:00–23:00 Eastern).
7. **No AI therapy.** Grief, relationship and mental-health conversations get a fixed referral reply and a human, never counselling from the character (Illinois WOPR Act 2025). Sun Yoon's "heart-to-heart" framing is not used in the chat.

---

## 2. Front ends, upsells and how each attaches the subscription

### 2.1 The paths

| Path | Traffic | Page flow | Attach method |
|---|---|---|---|
| **Quiz → $1 trial** | Organic keyword DMs ("comment STRONG"), paid cold | DM button → short Strength Age quiz (~90 seconds: 5 questions + the chair stand, with "do it later" always offered; FUNNEL §3.1) → email (+ SMS consent once SMS is live) → **Strength Age result page** (score + 7-day plan preview) → checkout | **Trial-to-subscription**: "$1 today for 7 days, then $20 every month until you cancel". Required, **unticked** consent checkbox. |
| **$7 Strength Reset** | Paid (offer ads), bio link, Chang Yin "do this every morning" reels | Sales page → checkout → bump → upsell 1 → upsell 2 / downsell → welcome | **Membership included**: the $7 includes 7 days of Strong Years, and continuation at $20/mo is disclosed in the order box. *Split-test* against **product only + a one-click "add your 7 free days" button after purchase**. That version gets fewer members but produces fewer disputes. Pick the winner by revenue per buyer at day 67 **net of refunds and chargebacks**. |
| **$17 Kitchen bundle** | Sun Yoon's food reels, Pinterest later | Recipe landing page → checkout | Same as $7. |
| **14-Day Strength Challenge** (monthly cohort, starts on the 1st) | Organic events, email list, re-engaging past buyers | Countdown landing page → $9 → cohort group + daily live check-in | 14 days of membership included, then $20/mo. Events create a burst of urgency every month. |
| **Gift** | Adult-children ads (Mother's Day, Father's Day, Grandparents Day in Sept, holidays), "for Mom" retargeting | Gift page → choose 3/12 months → recipient email/SMS → printable card | **Prepaid, no auto-renew.** When the gift is about to end, the *recipient* is asked to continue on their own card with fresh consent. |
| **Free quiz only** (didn't buy) | Everyone who opted in but didn't purchase | 10-day email + SMS nurture: 3 free sessions, Sun Yoon recipe, re-test prompt, then a $1-trial reminder | Same as the $1 trial. Modelled as 5% of last month's opt-ins. |

### 2.2 Order bump, upsells, downsell (as modelled)
- **Bump ($9, ~30%)**: "The Wall Plan": a printable 12-week calendar + 12 weekly grocery lists. It's low risk and people like having something on the fridge.
- **Upsell 1 ($27, ~10%)**: choose one 12-week program to **keep forever**. Ownership matters to buyers aged 60+. This also works as a save lever later: "you keep your program either way".
- **Upsell 2 ($29, ~6%)**: the physical kit. A fixed $12 landed cost gives $17 contribution. It also puts the brand in the member's home and raises session starts in week 1.
- **Downsell ($7, ~5%)**: printables only for people who decline upsell 1.
- **Annual upgrade**: offered at trial end ("keep going for $119/yr, about $9.92 a month") and in the day 21/45/75 campaigns. Not offered at the first checkout: an annual price on the front end lowers trial starts for cold traffic.
- **Front-end revenue per start in the model: $12.99.** At a base $33.81 cost per paid trial start, the front end covers about 38% of ad spend (sheet row "self-liquidation ratio"). It is **not** a self-liquidating offer. Profit comes from the subscription. §2.5 covers how to get closer to break-even on the front end.

### 2.3 Compliance built into the checkout (ROSCA + state auto-renewal laws + card networks)
Why this matters: the FTC's click-to-cancel rule was vacated in July 2025, but the FTC restarted rulemaking (advance notice of proposed rulemaking, Mar 2026) and **ROSCA enforcement continues**, with recent settlements of $7.5M and $60M ([Gibson Dunn](https://www.gibsondunn.com/ftc-restarts-negative-option-rulemaking-after-eighth-circuit-vacatur-enforcement-under-rosca-continues/)). California's amended auto-renewal law, in force since Jul 1 2025, requires express affirmative consent (with records kept 3 years), online cancellation through the same channel as signup, an annual reminder, 7–30 days' notice of price changes, and notice before a trial longer than 31 days converts ([Cooley](https://www.cooley.com/news/insight/2025/2025-06-04-california-automatic-renewal-law-amendments-take-effect-on-july-1-2025)).

Checkout specification:
1. The renewal terms go **directly above the pay button**, in type at least as large as the price and in black on white: *"You pay $1 today. On [date] your Strong Years membership renews at $20.00 every month until you cancel. Cancel anytime online in at most two screens at strongyears.com/account, or reply 'cancel' to any email{{IF_SMS: , or text CANCEL}}."*
2. A **separate unticked checkbox**: "I agree to the automatic renewal terms above." Store a timestamp, IP, the exact text shown and the price in a consent log.
3. The confirmation email and SMS repeat the terms, the cancel link and the first charge date.
4. A **reminder 48 hours before the first charge**, and a **reminder before every renewal charge after that** (7 and 2 days before the first renewal, 3 days before each later one; 30 days before an annual renewal), by email{{IF_SMS: + SMS}}, with a one-tap cancel link. This lowers disputes more than any other single step. **Until 10DLC / toll-free SMS verification is approved (3–6 weeks, §3.3), this reminder goes by email only.**
5. Cancellation: **cancel online in at most two screens: one save offer shown next to an equally prominent "Finish canceling" button** (the save offer is a pause or a downgrade; tapping "Finish canceling" cancels immediately), then an on-screen confirmation and a confirmation email. It is never phone-only and never handled by the AI character.
6. **The California annual reminder for every auto-renewing member, monthly included** (AB 2863), sent every 12 months with the plan, price, frequency and cancel method; and price-change notice sent **exactly 30 days** before the change (inside California's 7–30 day window). Counsel supplies a 50-state ARL matrix (CA, NY GBL §527-a acknowledgment, MN, VA, CO) for `legal_pack`.
7. Card descriptor `STRONGYEARS MEMBER` + a support URL, so the charge on a bank statement is recognisable.

### 2.4 Pricing test matrix

| Monthly | Annual | Months of monthly price | Hypothesis |
|---|---|---|---|
| $12 | $79 | 6.6 | Highest trial→paid, lowest revenue per start. Only worth it if it lifts trial starts by more than 40%. Useful as the $12 "Essentials" downgrade tier (with a $9 test cell) rather than the headline price. |
| $15 | $99 | 6.6 | Level with Calm ($16.99) and Headspace ($12.99). A safe second arm. |
| **$20** | **$119** | **6.0** | **Control.** Matches the Yang Mun Whop price ($19.99) while giving far more. Base case in the model. |
| $25 | $149 | 6.0 | Test once retention data exists. If early renewals hold within 3 points of control, $25 wins. |
| $30 | $199 | 6.6 | Better as a **"Plus" tier** (monthly 10-minute video check-in with a human coach + small-group live) than as the base price. |

How to run it:
- **Primary metric: net revenue per trial start at day 67.** That covers the front end, the first charge and the first renewal, net of refunds and chargebacks. Secondary: trial→paid and the first renewal rate.
- **Sample size:** to detect 42% vs 37% trial→paid (80% power, α 0.05) you need about 1,500 trial starts per arm. That's about 5 days of S3 traffic or about 3 weeks of S2 traffic. Run 3 arms at most at a time.
- **Order:** weeks 1–3 test $15 / $20 / $25 on paid traffic only (organic stays on $20 so the community sees one price). Then the annual price ($99 / $119 / $149). Then the Plus tier.
- In the model, `Sensitivity` shows higher prices winning on LTV:CAC if trial→paid elasticity is 0.30. **That elasticity is the unknown the test exists to measure.** Don't raise the price on the strength of the model.
- Price changes for existing members follow the California notice rules. Grandfather founding members as a loyalty and retention lever ("founding price locked while you stay subscribed, pauses included"; never "for life").
- **Blitz mode replaces this matrix at launch** with the founding $25 vs $30 test (days 1–5; §0.1). This matrix applies to the baseline funnel after the blitz.

### 2.5 Making the front end closer to self-liquidating
To fully cover the ad spend you need front-end revenue per start of about $34 at a base cost per trial of $34. Levers, in order of size:
1. A **$27 "Strong at 70 Starter"** (the program + 14 days of membership) as a paid-traffic-only path. Expect trial starts to fall 30–50%, but profit per start roughly doubles.
2. Bump take above 40%: show the product and the fridge, and write the bump in Sun Yoon's voice.
3. Offer the kit before upsell 1 in the gift flow. Gift buyers aged 35–55 accept physical products at 2–3× the rate.
4. **Gift traffic** usually has a higher order value ($49–119 prepaid) and no trial risk. Push it hard in Q4 and the Mother's Day, Father's Day and Grandparents Day windows.

### 2.6 Meta ad-account constraints that change the funnel
Since early 2025 Meta labels advertisers "associated with medical conditions" as health & wellness. Those advertisers can't optimise for or build audiences from purchase events ([Triple Whale](https://www.triplewhale.com/blog/meta-health-and-wellness-brands)). Design to stay a **fitness/cooking** advertiser:
- Domains, URL paths, page titles, pixel event names and quiz URLs **never name a condition** (use `/strong-at-70`, not `/back-pain-reset`, and `/program/back-strong`).
- Quiz answers about limitations stay first-party only. They are never sent through the Meta Conversions API or pixel.
- Ads talk about strength, balance, energy and cooking, not symptoms or diseases. The "remedy" content stays on organic channels and is framed as food with an evidence note.
- **Which ad account runs Strong Years (BLITZ CANON):** an existing account **only** if it has purchase history **and** no restricted-health history (no TRT, hormone, peptide or perimenopause-condition ads). The K9SUPPS account is the likeliest candidate. Otherwise open a fresh account under the Strong Years business with a verified domain. **Never run Strong Years ads from Founder Ascension accounts.** (BLITZ_OPS.md §6.1 has the scoring criteria.)

---

## 3. Tech & billing stack

### 3.1 Checkout and billing: what each option costs

| Option | Fees | Good | Bad | Verdict |
|---|---|---|---|---|
| **Stripe (own account) + Stripe Billing** | 2.9% + 30¢ card, +0.7% Billing, $15 dispute (+$15 counter fee, refunded if won) ([Stripe](https://stripe.com/billing/pricing), [Chargeflow](https://www.chargeflow.io/blog/stripe-dispute-fees)) | Full control of the checkout UX, Apple Pay (60% of web2app payments per FunnelFox), smart retries, card updater, 1-click upsells via saved payment methods | Underwriting risk (negative option + health + fast growth) can bring rolling reserves | **Primary.** Add a **second processor** (a second Stripe account on a separate entity, or Checkout.com/Adyen) before spend passes $5K/day. |
| Whop | 2.7% + 30¢ domestic, +1.5% international, +1% FX, +0.5% optional billing, payout fees ($2.50 next-day ACH), $15 dispute ([MemberTape](https://membertape.com/whop/fees/)) | Fastest to launch. Yang Mun uses it. | The Whop brand is unfamiliar to 55–75 buyers, limited UX, risk of account freezes, and it doesn't own the member experience | Only as a **week-1 stopgap**. |
| Skool | $9/mo + 10% or $99/mo + 2.9% ([Skool](https://www.skool.com/pricing)) | Community is built in | A dev-community UI that doesn't suit a 70-year-old. No personalisation, no SMS, no AI. | No. |
| Circle | $89–419/mo + 0.5–2% + Stripe ([SchoolMaker](https://schoolmaker.com/blog/circle-so-pricing)) | Good community; branded app on the Plus plan | Personalisation and streaks would need to be built around it anyway | Possible as the Courtyard in phase 1 only. |
| Kajabi | $143–399/mo (annual) + 2.9% + 30¢ + 0.7% on subscriptions ([ClickFunnels](https://www.clickfunnels.com/blog/kajabi-pricing/)) | Courses + email | Rigid. Weak personalisation. | No. |
| App stores (in-app purchase) | 15–30% commission | Discovery; 55+ trust the App Store | You lose 15–30% of revenue. Since Epic v. Apple, US apps may link out to web checkout **with no commission on web purchases** (apps must still offer in-app purchase as well) ([RevenueCat](https://www.revenuecat.com/blog/growth/apple-anti-steering-ruling-monetization-strategy)) | **Web-first.** Ship a native wrapper in month 3–4 for retention (push notifications, home-screen icon). Sell on the web and link out from the US app. |

**Web funnels beat in-app funnels:** FunnelFox 2026 reports web paywalls convert about 2× better than in-app (3.0% vs 1.5%) and that upsells lift LTV by more than 200% ([FunnelFox](https://funnelfox.com/state-of-web2app/)).

### 3.2 Recommended build
- **Days 1–10:** Stripe Checkout (with the custom consent block) + a simple members area (Next.js + Supabase + Mux) + Twilio SMS + email platform (Customer.io or Klaviyo) + ManyChat (Instagram/FB comment → DM) + the quiz. The Courtyard can start on Circle or a moderated in-app feed.
- **Days 10–45:** a **custom PWA** with a big-type UI (minimum 18px body text, 56px buttons, black on white, no gray text anywhere). It needs: the level engine, the Today screen, streaks with grace days, the Strength Age re-test, the program tracker, AI chat (Claude Haiku 4.5 with Sonnet 5.5 for escalations; prompt caching brings a message to about $0.003), voice notes (ElevenLabs), and the consent and cancel center.
- **Month 3–4:** Capacitor/React Native wrapper for iOS/Android with push notifications and a web link-out for purchases in the US.
- **Clone-ability:** all character voice, language, price and legal copy lives in a per-market config (`locale`, `character`, `currency`, `legal_pack`), so *Años Fuertes* is a config change plus a content pipeline, not a rebuild.

### 3.3 Messaging
- **SMS (US):** Twilio 10DLC, $0.0083 per segment + $0.0035–0.0045 carrier fees ([Twilio](https://www.twilio.com/en-us/sms/pricing/us)). Needs TCPA express written consent at the quiz, a STOP keyword, quiet hours: send only 10:00–20:00 recipient local time (the canonical window; stricter than Florida's 8am–8pm), and A2P 10DLC brand/campaign registration (or toll-free verification). **Allow 3–6 weeks** (brand review up to 7+ business days, campaign review 10–15 days, carrier review often 2–4 weeks; BLITZ_OPS.md §1.1), so start it at kickoff and **launch on email + DM**. SMS switches on when approved; until then the 48h pre-charge reminder and every renewal reminder go by email.
- **WhatsApp:** marketing templates to US numbers have been paused since April 2025. Utility messages cost about $0.006, and service-window replies are free ([MessageCentral](https://www.messagecentral.com/blog/whatsapp-business-api-pricing-usa)). Use it in the US only for member-initiated conversations. Use it as the primary channel in LATAM/Spanish-speaking markets.

### 3.4 Refunds, chargebacks, dunning
- **Policy (all modes):** a **14-day money-back guarantee on the first membership charge, one per person** (matched on email and card fingerprint), refunded self-serve from the account page. **Add-ons** (bumps, upsells, front-end products) are watermarked digital downloads, refunded on request within 14 days, not self-serve; the kit 30 days, no return needed. The founding-week keep-forever program download unlocks on day 15. Repeat refunders are flagged by card fingerprint. Every refund you make yourself avoids a $15 dispute fee plus a strike on your chargeback ratio.
- **Thresholds to stay far below:** Visa VAMP 1.5% (from Apr 1 2026, merchants with 1,500+ transactions a month) ([Chargeflow](https://www.chargeflow.io/blog/vamp-visa-acquirer-monitoring-program)); Mastercard ECM at ≥1.5% **and** ≥100 chargebacks a month for 2 months ([Chargeflow](https://www.chargeflow.io/blog/avoid-mastercard-chargeback-monitoring-programs)). **Internal target: <0.4%** (the model uses 0.35%). Warning: in S3's first quarter (~19–25K card transactions a month) the Mastercard 100-chargeback count trips at only 0.4–0.5%, so the count matters as much as the ratio.
- **Tools:** Verifi RDR + Ethoca alerts auto-refund disputes before they become chargebacks; the 48h pre-billing reminder; a recognisable descriptor; and "text CANCEL" support once SMS is live.
- **Dunning:** Stripe smart retries + card account updater. A pre-dunning email 7 days before a card expires. A failed payment triggers an SMS "update card" link (one tap, Apple Pay) and 7 days of continued access. FunnelFox reports up to 17.5% of failed subscriptions are recovered, and involuntary churn is roughly a third of all churn in Recurly's benchmarks ([Recurly](https://recurly.com/research/churn-rate-benchmarks/)).

---

## 4. Supplements later (subscribe & save)

**When:** month 7 (the model's `supp_start` = 7), inside the membership only, only after membership retention is proven and the chargeback ratio has been below 0.4% for 90 days.
**Where:** inside the membership only. It appears as "Chang Yin's Stack" content, Sun Yoon's pantry, and at the day-60 milestone. It is never on the front end, never in cold ads (to protect the Meta account classification and the trust of people who came for free content), and never in the AI chat as a sales pitch.

**Candidate products** (chosen because published human evidence supports a plausible benefit for adults 60+ who do resistance training):
| Product | Claim you can make (structure/function) | Claim you can never make |
|---|---|---|
| Creatine monohydrate 3–5 g | "Supports muscle strength and power when combined with resistance training" | "Treats sarcopenia", "prevents falls" |
| Protein (whey or plant) + leucine | "Helps you reach daily protein needs for muscle maintenance" | "Reverses muscle loss" |
| Vitamin D3 (+K2) | "Supports normal muscle function and bone health" | "Prevents osteoporosis" |
| Omega-3 | "Supports heart and joint health" | "Lowers blood pressure", "cures arthritis" |
| Psyllium / prebiotic fibre (fits Gut Reset) | "Supports regularity and digestive health" | "Treats IBS" |
| Magnesium glycinate | "Supports relaxation and sleep quality" | "Treats insomnia" |
| Sun Yoon's tea line (ginger, barley, citrus) | Food/flavour positioning only | Any remedy claim |

**DSHEA and FDA rules:** only structure/function or general well-being claims. The label must carry the boldface disclaimer: "This statement has not been evaluated by the Food and Drug Administration. This product is not intended to diagnose, treat, cure, or prevent any disease." You must notify the FDA **within 30 days** of first marketing the claim. No claim may diagnose, mitigate, treat, cure or prevent a disease ([FDA](https://www.fda.gov/food/information-industry-dietary-supplements/notifications-structurefunction-and-related-claims-dietary-supplement-labeling)). The FTC separately requires competent and reliable scientific evidence for the claim as a consumer would read it, and the AI characters' dialogue counts as advertising.

**Safety in the flow:** a medication checklist at signup (anticoagulants, diabetes drugs, kidney disease flag → "check with your doctor first", and a block on buying creatine or magnesium until they acknowledge it).

**Synergy with the client's existing capability:** reuse the K9SUPPS/Flopeptides supplier, 3PL and subscription tooling. Keep **peptides completely out of this brand.** They carry regulatory risk, the audience is elderly, and they would undermine the credible, evidence-based positioning.

**Economics (modelled separately from membership MRR):** 5% of members × $36/mo × 55% contribution. At 25,000 members that is about $25K/mo in contribution. It helps, but it isn't the thesis.

---

## 5. Retention engineering

### 5.1 First 72 hours (most 3-day-trial cancellations happen on Day 0–1, per [RevenueCat](https://www.revenuecat.com/blog/growth/subscription-app-trends-benchmarks-2026). The trial here is 7 days, but the same urgency applies)
| Time | Action | Why |
|---|---|---|
| Minute 0 | Welcome video from Chang Yin (60s) + Sun Yoon (20s). "Your first session is 8 minutes. Do it now, in your chair." | Get a first session done in the first 10 minutes. It's the strongest predictor of retention. |
| +5 min | Baseline **Strength Age** (3 of the 6 tests, 4 minutes) | Gives a number to beat and makes the first month feel invested. |
| +10 min | SMS consent confirmed, pick a reminder time ("When do you have your morning tea?"). Add to home screen with a picture guide. | Anchors a habit to an existing routine. |
| Day 1 evening | Sun Yoon SMS: tonight's 15-minute dinner + grocery list | A second reason to open the app. |
| Day 2 | Session 2 + "tell Chang Yin what hurts" (sets up personalisation) + first AI chat prompt | Memory makes the product harder to leave. |
| Day 3 | Streak 3 badge + a one-question check-in ("too easy / just right / too hard") → level adjusted | People who feel it was made for them stay. |
| Day 5 | **Pre-billing reminder** (48h before the charge) framed as progress: "5 sessions done. Your membership continues on Friday at $20. Change or cancel here." | Compliance, and it prevents chargebacks. |
| Day 7 | Converts. "Week 1 done" summary + invitation to the Wednesday live | |

### 5.2 Milestones
- **Day 7:** first-week recap and choose a 12-week program (the program is the long commitment).
- **Day 30:** re-test **Strength Age**, a shareable card showing the stand and balance changes first (member's choice; no before/after imagery, and "early gains include practice with the test"), the mailed printed certificate is queued, first annual offer ("lock in $119/yr").
- **Day 60:** program at week 8; a Sun Yoon "kitchen graduation" recipe pack; couple/family add-on offer; supplement stack introduction (from month 7).
- **Day 90:** second re-test; "90-day Strong" certificate mailed; invite to a peer-mentor role ("Courtyard Elder", a status badge); a **second annual push** with a founding price.

### 5.3 Churn predictors (score daily; trigger automatically)
| Signal | Threshold | Automatic response |
|---|---|---|
| No session in 5 days | 5 days | Sun Yoon SMS ("Chang Yin is sulking. 5 minutes today?") + a 5-minute "comeback" session |
| No first session by day 2 | — | Human-coach SMS (a real human, signed as a human) |
| Session-length decline 3 weeks running | −30% | Offer an easier level or a different program |
| Skipped the monthly re-test | day 35 | A tailored "your 30-day number" nudge |
| Visited the cancel page, then returned | any | Personal note + pause option |
| Failed payment | any | Dunning (§3.4) |
| SMS STOP but still active | any | Email/app nudges only. Respect the opt-out fully. |
| Single-member household, low community activity, age 75+ | profile | Invite to the Wednesday live + a weekly buddy prompt |

### 5.4 Save offers (one per cancellation, shown next to an equally prominent "Finish canceling" button; at most two screens)
1. **Pause** 1, 2 or 3 months, $0, keeping the streak and memory ("travel, surgery, grandkids": good reasons shouldn't cost you a member).
2. **Downgrade** to **Essentials $12/mo** (daily session + daily message; no AI, live or programs). Run a $9 test cell.
3. **Switch to annual** (standard mode: $119; blitz mode: the $249 founding annual, only after renewal 1). One time. In blitz mode, test pause-first: the $12 Essentials and annual saves dilute MRR (AUDIT F07).
Target: 20–30% of people who start the cancel flow accept a save.

### 5.5 Annual conversion campaigns
- Offers at day 21, 45 and 75, trial end, and after the member's second Strength Age improvement ("you're 4 years younger than at signup. Lock in the price for a year").
- Standard mode: the annual test cells ($99 / $119 control / $149). Blitz mode: the $249 founding annual from L35 (client decision).
- Q4 gift push: "buy a year for Mom, get a year for yourself at 50% off".

### 5.6 Winback
- Day 7 after cancelling: "your streak and memory are saved for 90 days" (a true statement: the data is kept for 90 days).
- Day 30: new program launch + $1 for the first month back.
- Day 90: a gift from Sun Yoon (free recipe pack) + the re-test prompt.
- Day 180: annual at a founding-level price.
- Stop after 4 touches. Respect the email and SMS opt-outs.

### 5.7 Retention targets that decide which scenario you get
| Metric | Benchmark | Model base | "Godly" goal |
|---|---|---|---|
| Trial → paid | 42.2% (Adapty H&F) | 42% paid / 48% organic | 50%+ |
| Still paying after renewal 1 | 59.2% | 62% | 70% |
| Still paying after renewal 3 | 37.1% | 43% | 55% |
| Steady monthly churn | ~4.1–4.3% (Recurly B2C) | 5.0% | 3.5% |
| Chargeback rate | VAMP limit 1.5% | 0.35% | <0.25% |

In `Sensitivity`, moving steady churn from 5% to 3% improves LTV:CAC by about 10%. Moving the early survival curve (renewals 1–3) matters more, because that's where 40–60% of each cohort is lost. **Put the retention budget into the first 90 days.**
