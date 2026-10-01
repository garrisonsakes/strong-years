# BLITZ_OPS.md: the operating playbook for the Strong Years MRR blitz

**What this is:** the operating playbook that turns BLITZ.md's recommended configuration (R4: a charge-today founding membership at $25–30, an eligible existing ad account (§6.1) at $8K/day from launch, 4 shoutouts a day, warm cross-promo in week 1) into dated tasks, owners, copy, thresholds and scripts. It covers kickoff to day 30.

**Read with:** BRIEF.md (blitz addendum), BLITZ.md, `economics.xlsx` (sheets Blitz, Milestones, Blitz_Plan), OFFER.md, FUNNEL.md, ADS.md, PIPELINE.md §5 and §9, CONTENT_SYSTEM.md §8, CHARACTERS.md, SAFETY_RULES.md. Where this file and SAFETY_RULES.md differ, SAFETY_RULES.md wins. Where this file and a model number differ, the model wins. Change the model inputs, not this file.

**Conventions**
- **D−10 … D−1** are build days. **D0 = L1 = launch day = the model's Day 1** (the first paid day). Launch days count **L1, L2, … L30**.
- Example calendar (edit the dates, keep the offsets): kickoff **Fri Oct 2 2026 = D−10**. **Launch Mon Oct 12 = L1**. Live event **Wed Oct 14 = L3**. Founding-week bonus ends **Fri Oct 16 = L5**. **L14 = Sun Oct 25**, **L30 = Tue Nov 10**.
- Owners: **G** = Garrison (offer, money, media, final approvals) · **CL** = content lead (pipeline, creative, event production) · **DEV** = developer (app, data, integrations) · **VA1** = content QA and ad-ops VA · **VA2** = community, DM and partnerships VA · **SUP** = support agent (first-line billing and account help; from L1) · **ATT** = consumer-protection attorney · **REV** = credentialed reviewer (PT/DPT, RDN) · **PERF** = movement performer · **HOST** = the human co-host of the live event.
- `{{DOMAIN}}` = the site (e.g. strongyears.com). `{{FOUNDING_PRICE}}` = the founding cell price ($25 or $30; $25 is the default display until the L1–L5 test is read). `{{STANDARD_PRICE}}` = the price after the founding cap closes (decision D4; configurable, default $35). `[HOST NAME]`, `[PT NAME]` = real people, filled in only once they have signed.
- **Reviewer gate** (same convention as FUNNEL.md): any line that claims professional review is written as `[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: …] FALLBACK: "…"`. The app enforces it with `REVIEWER_SIGNED=false`.
- **Audit fixes (Sep 30 2026; AUDIT_BUSINESS.md).** The canonical policies at the top of FUNNEL.md override older lines here: `{{IF_SMS: …}}` fragments render only when `SMS_ENABLED=true` (so "text CANCEL" never appears while SMS is off); 14-day money-back guarantee on the membership charge, one per person; add-on refunds on request within 14 days; the founding-week program download unlocks on day 15; a reminder email before **every** renewal charge; the California annual reminder for every auto-renewing member; price notices exactly 30 days ahead; "locked while you stay subscribed (pauses included)", never "for life"; the cap is **5,000 or `{{FOUNDING_CLOSE_DATE}}` (default L90 = Sat Jan 9 2027), whichever comes first**; public counts use `{{COUNT_LINE}}` (below 1,000: "open to the first 5,000…" + a link to the live count; from 1,000: "{{COUNT}} of 5,000 taken as of {{COUNT_TIME}}"); human coverage 07:00–23:00 ET with a crisis-resources line, never "24/7". Items the audit found missing are tracked in LAUNCH_CHECKLIST.md.
- **Routes that exist.** The plan links only to app routes that exist: `/start`, `/join`, `/q/a`, `/q/b`, `/gift`, `/how-we-make-this`, `/safety`, `/terms`, `/privacy`, `/refunds`. Warm landing variants are `/start?v=w` (was `/w`) and `/start?v=walk` (was `/walk`); partner and shoutout links are `/start?via={slug}` (was `/p/{slug}`). `/live` and `/live/replay` must be built by D−8 (LAUNCH_CHECKLIST.md); fallback: run the premiere as a YouTube Premiere linked from `/start?ev=live`.
- **Keywords.** 12 standard keywords (FUNNEL.md §4: STRONG, BACK, SLEEP, SOUP, GUT, BALANCE, KNEES, BREATH, BEGIN, TEST, FAMILY, JOIN; FOUNDER is only a JOIN variant). LIVE is a temporary event keyword (L1–L3), not a 13th standard keyword.
- **Launch configuration (Sep 30 2026 update; supersedes "$8K/day charge-today from L1").** Blitz mode runs **three live cells from L1**, sticky per visitor: **F25** (founding, charged today, $25), **F30** (founding, charged today, $30) and **T25** ($1 for 7 days, then $25 as a founding member). Split **50% founding / 50% trial** (paid: 25/25/50; non-paid: F25 50%, T25 50%). Meta starts at **$3K/day** (the auditor's recommendation; **client decision**), steps to **$4K/day** only if charge-today passes the **day-10 gate**, and to full R4 ($8K/day, 100% charge-today) only if it also passes the **day-40 gate** (BLITZ.md §11; thresholds in §6.3 below and FUNNEL.md §0.2.1). If charge-today fails, the launch runs the R17 plan on the trial. R4 numbers in this file are the **graduated upside**, not the launch plan. Plan on the auditor central case (~$49K MRR on day 30 at $25 if R4 spend were run) and on R17 (~$21K on day 30) as the floor; **re-run the Blitz sheet with the 3-cell split and the gated ramp before L1.**
- **[A]** marks an assumption to validate in the first 72 hours. Every external fact carries a source link. The full list is in §10.

---

## 0. One screen

### 0.1 The targets against the model (Blitz_Plan, recommended config R4)

| Client milestone | R4 at ≤ $500K peak cash | Full-milestone variant at ~$630K peak cash | What this playbook does about it |
|---|---|---|---|
| **$10K MRR within a few days** | **Reached on L4** ($13.0K on L5, 456 members) | $13.5K on L5 | Realistic. It needs arm B (charge today), $8K/day of Meta from L1 and warm lists on L1–L3. |
| **$50K MRR by day 14** | $42.9K on L14 (reached L17) | **$50.4K on L14** | A stretch. The **L4 gate (§6.3)** decides whether to exercise the variant (ramp Meta to $12K/day by L6). |
| **$100K MRR by day 30** | $92.8K on L30 (reached L36) | **~$112K on L30** | A stretch. The same gate, plus shoutouts holding at 4 a day. |
| $500K MRR | not within 90 days | not within 90 days | Month 8–9 at best (BLITZ.md §1). Nothing in this playbook changes that. |

**Three unknowns decide everything. Measure them in the first 72 hours:**
1. **Arm-B purchase rate per opt-in.** The model uses 5.18% of cold opt-ins at $30. There's no benchmark for it.
2. **Cost per paid opt-in on the chosen ad account.** The model uses $6.36 on L1–L7 and $5.53 after that.
3. **Shoutout supply.** Can we book 25–30 distinct 50+ pages at ≤ $600 per post? Shoutouts produce about a third of R4's paid-channel opt-ins.

**An honest reading of the ad rules.** At the model's own assumptions, Meta alone lands at about **$107–123 of media per founding purchase** (L1–L14, $30 cell). That is inside the HOLD band in §6.4, not SCALE. The plan works on a **blended** basis because shoutouts (~$59 a purchase), warm lists (no media cost) and affiliates are cheaper. So SCALE decisions on Meta mean the ads are **beating** the model. Don't expect them on L1.

### 0.2 Decisions Garrison makes in the first hour of kickoff (D−10, 07:00)

| # | Decision | Default (our recommendation) | Why it can't wait |
|---|---|---|---|
| D1 | Cash commitment | **The gated plan:** $3K/day Meta from L1 (3 cells), $4K/day after a green day-10 gate, R4 ($8K/day, ≤ $500K peak cash) only after a green day-40 gate. The ≤ $630K variant is off the table until day 40. | Sets the Meta account spending cap, card limits and processor volume requests on D−10 |
| D2 | Legal entity that sells Strong Years | An **existing entity with 3+ months of clean processing** if one exists (faster underwriting), **but not the entity FA's core revenue runs through**. Otherwise a new LLC, which means slower underwriting and more reserve. | Processor applications go in on D−10 |
| D3 | Which ad accounts run Strong Years | See §6.1 criteria. An existing account **only** if it has purchase history **and** no restricted-health history. **Never an account that has run TRT, hormone, fertility, peptide or perimenopause-condition ads, and never a Founder Ascension account.** The K9SUPPS account is the likeliest candidate; if none qualifies, a fresh account under the Strong Years business with a verified domain. Meta classifies health & wellness at the data-source level ([Triple Whale](https://www.triplewhale.com/blog/meta-health-and-wellness-brands)), and a policy strike on Strong Years can reach every asset in the Business Portfolio. | Spending limits and payment methods are checked on D−10 |
| D4 | Standard price after the 5,000th founding member | **Configurable, default $35/mo** (`STANDARD_PRICE_CENTS=3500`; **client decision**), published on the terms page from L1 and actually charged to new members once the cap closes. The $1 trial runs as cell T25 from L1; trial members who convert while the cap is open get the $25 founding price and take a seat at their first full charge (§1.5 gap 2). | "Founding price locked while you stay subscribed" (never "for life") is only honest if the later price really is higher and really charged (16 CFR 233). If the cap stays open for months, the founding price becomes the de facto regular price: that's why the cap also closes on `{{FOUNDING_CLOSE_DATE}}`. If you won't charge the D4 price later, drop the "founding price" language and sell founding perks only. |
| D5 | Guarantee | **14-day money-back guarantee on the membership charge, one per person**, self-serve. Add-ons: refund on request within 14 days (watermarked downloads); kit 30 days. Founding-week program download unlocks on day 15. Refund-first discretion for up to 60 days where the member never used the product and downloaded nothing (§8.4); never advertised. | Model input (10% refunds). The copy depends on it. |
| D6 | Warm lists: what may be sent | Email to every segment with a documented marketing opt-in and no unsubscribe. **SMS only where the original consent language covers affiliated brands, or where counsel confirms it** (§3.1). | The consent audit runs D−10 afternoon |
| D7 | Affiliate commission | **30% recurring for 12 months** (default). **40% for 12 months is a client-decision option** (e.g. for the first 100 approved partners) (§5.1) | Recruiting starts L1 |
| D8 | Live-event human co-host | A named real person on the team, introduced as human. Credential claims only if REV has signed. | The script is written on D−8 |
| D9 | Reviewer | Sign a PT/DPT + RDN by D−4. Otherwise ship FALLBACK strings everywhere (`REVIEWER_SIGNED=false`). | Every bio, ad and page string depends on it |

### 0.3 Ten rules the whole team follows during the blitz
1. **Every counter, deadline and number shown to buyers is real.** Founding seats are counted from the payment processors. Bonuses end when we say they end. Nothing is inflated, reset or faked (§2.1).
2. **AI disclosure is everywhere:** bios, the first 3 seconds of every video, the first line of every DM, email footers, the event. A real human is always introduced as a human.
3. **No disease claims, no personal-attribute ads, no fake testimonials** (ADS.md §1, SAFETY_RULES.md).
4. **Refund first, argue never.** A refund costs less than a $15 dispute fee plus a strike on the ratio.
5. **Condition words never reach Meta:** URLs, events, pixels, page titles (the app enforces this in `src/lib/analytics/meta.ts`).
6. **One owner per decision.** Spend changes: G. Creative approvals: CL (G on anything new). Refunds: SUP within policy. Crisis: VA2 within 15 minutes.
7. **Decide on backend numbers, not Ads Manager.** Purchases, refunds and members come from Stripe/Braintree via Supabase.
8. **Change one thing per campaign per step.** A budget change over 20–25% resets learning ([AdLibrary](https://adlibrary.com/posts/meta-ads-learning-phase-50-events-guide)).
9. **Never route payments to hide chargebacks.** Load balancing to keep each MID under a monitoring threshold is treated as fraud against the acquirer and the networks ([Merchant Alternatives](https://merchantalternatives.com/glossary/load-balancing/)). §6.7 paces volume only within approved limits.
10. **Never evade an enforcement action.** If an ad account or page is restricted for policy, appeal it. Don't move the same ads to a backup account (§9).

---

## 1. Pre-launch compressed build (D−10 → D0)

### 1.1 Critical path

| Item | Lead time (source) | Start | Must be done by | If it's late |
|---|---|---|---|---|
| **Processor 1: Stripe live + risk pre-clearance** | Account opens in minutes. New accounts often see a **7–14-day payout hold**, and moderate-risk accounts a **10–15% rolling reserve held 90–180 days** ([terms.law](https://terms.law/FAQ/payment-processors/stripe-holds-faq.html)) | D−10 07:30 | D−3 (live test purchases) | No launch. The model already assumes a 10% reserve and a 5-day payout lag. |
| **Processor 2: Braintree (cards + PayPal wallet)** | Underwriting takes days to weeks [A]. Standard rate 2.89% + $0.29, $15 per chargeback ([PayPal](https://www.paypal.com/us/enterprise/paypal-braintree-fees)). Subscription underwriters typically hold **5–10% for 90–180 days** on new accounts ([SeamlessChex](https://www.seamlesschex.com/deep-dives/recurring-billing-merchant-accounts-how-subscription-businesses-get-approved-in-2026)) | D−10 09:00 | **L14** (the model assumes day 21) | Stay 100% on Stripe within its approved volume. If Stripe nears its cap, hold Meta spend (§6.7). |
| **Meta Business verification** | 3–10 working days ([duochat](https://www.duochat.in/help-center/get-verified-with-facebook/how-long-meta-business-verification-usually-takes)) | D−10 (only if the chosen portfolio isn't verified) | D−3 | Use a portfolio that is already verified. That's why D3 picks existing assets. |
| Domain verification + new dataset (pixel) + CAPI | Minutes (DNS TXT) + one dev day | D−10 / D−7 | D−3 | No Purchase optimization. Launch on Lead optimization and judge on backend numbers. |
| **Ad-account daily spending limit ≥ $15K** (so $8K/day plus Meta's right to spend **up to 75% over** the daily budget on a given day ([Jon Loomer](https://www.jonloomer.com/updates-to-meta-ads-budgeting/))) | Accounts under 30 days old typically start at **€25–100/day**. Caps rise after 30–60 days of clean payments, or on request with revenue and dispute data ([Prime Scale](https://primescalemedia.com/blog/meta-spend-caps-explained)) | D−10 10:00 | D−2 | Split the budget across AA1 and AA2 (§6.1). Never open fresh accounts to go around a cap. |
| **A2P 10DLC (SMS)** | Brand: minutes, or **7+ business days** under manual review. Campaign review: **10–15 days** ([Twilio](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/direct-standard-onboarding)). AT&T's review often takes 2–4 weeks, so **3–6 weeks in total** ([Telphi](https://www.telphiconsulting.com/blog/twilio-a2p-registration-timeline)) | **D−10 08:30** | **Not on the critical path** | Launch with email + in-app reminders. The daily text starts when approved (expect L10–L30). The founding charge doesn't need a pre-charge SMS, and the 48h pre-charge reminder (trial arm, if it's ever switched on) goes by email until SMS is approved. The first-renewal reminders (7 and 2 days before; for L1 buyers that is L25 and L30) go by email if SMS isn't live. |
| Toll-free verification (SMS backup) | Unpublished [A]. Numbers can't text US/Canada until approved ([Twilio](https://www.twilio.com/docs/messaging/compliance/toll-free/console-onboarding)) | D−10 08:30 | backup | — |
| Attorney review (checkout, terms, cancel, cross-brand sends, affiliate + shoutout contracts) | 3–5 business days [A] | D−10 11:00 | D−3 | **Checkout doesn't open without sign-off.** |
| Credentialed reviewer signed | 3–7 days [A] | D−10 11:00 | D−4 | Ship FALLBACK strings. The launch doesn't wait. |
| Performer shoot (driving videos for every exercise shown) | Book 2–4 days out [A] | Book D−10, shoot **D−6** | D−5 | Launch with non-exercise ads (Sun Yoon, candor, quiz, gift). Exercise ads join on L3. |
| App deploy (`/home/claude/rebuild/app`) | 7 build days | D−10 | Checkout live on **D−3** | No launch |
| 150 organic masters (93 for the 3 day-1 pages; 57 for pages that go live on day 15 or 22) + 40 ads | ~30–35 masters/day once the pipeline runs (PIPELINE.md §4.5) | D−9 | Ads **in review by D−2** | Launch with ≥ 20 approved ads |
| Shoutout bookings | 3–7 days from outreach to post [A] | D−10 | First post **L3** | Meta carries it. BLITZ lever 1 is lost (−$28.5K of day-30 MRR if there are none at all). |
| Warm-list consent audit | 1 day | D−10 13:00 | D−4 (sends scheduled) | Send only to cleared segments |

### 1.2 Hour-by-hour plan

Times are US Eastern. "Done when" is the acceptance test. Rows marked **CP** are on the critical path.

#### D−10 (Fri): everything with a queue is submitted by noon

| Time | Owner | Task | Done when |
|---|---|---|---|
| 07:00–07:30 | G + all | Kickoff. Make decisions D1–D9 (§0.2). Name the Slack channels `#war-room`, `#crisis` (paged) and `#approvals`. | Decisions logged in `#war-room` |
| 07:30–08:30 | G | **CP** Stripe: finish KYC under the D2 entity. Statement descriptor `STRONGYEARS MEMBER` + support URL. Enable Radar. In the dashboard, **enroll in dispute prevention** (Visa RDR, Order Insight, Ethoca) ([Stripe docs](https://docs.stripe.com/disputes/get-started/prevention)). Open a support/risk ticket that states the business model, expected volume (~$150K in month 1, ~$170–200K in month 2, from the Blitz sheet), price points, the 14-day refund policy and the cancel flow. Ask for pre-approval of ≥ $250K/month. | Ticket number logged. Dispute prevention shows as enrolled. |
| 07:30–09:00 | DEV | **CP** Vercel project from `/home/claude/rebuild/app`, Supabase production project, migrations applied, DNS for `{{DOMAIN}}`, sending domain for email (SPF, DKIM, DMARC at `p=none` first), Stripe test keys. | `https://staging.{{DOMAIN}}/start` renders |
| 07:30–10:00 | VA1 | Create the 3 day-1 pages × 6 platforms (PIPELINE §9 D1): unique aliases, authenticator 2FA, recovery codes in 1Password. **IG "AI-generated profile" label on**. Bios use the SAFETY_RULES §7 FALLBACK strings. Link everything in Accounts Center. | 18 accounts in the credential vault; label screenshots in `#approvals` |
| 07:30–12:00 | CL | Character reference pack (CHARACTERS §13.1), 24 images, human-selected and locked | Refs uploaded to `character_refs` |
| 08:30–09:30 | G | **CP** Twilio: register the 10DLC Brand (reuse the entity's existing Brand if it has one) and a Campaign ("Marketing + account notifications"). Paste the sample messages from §2.4 and FUNNEL §6.2, each with the brand name and STOP language. Also buy a toll-free number and submit toll-free verification. | Both submissions show "pending" |
| 09:30–10:00 | G | **CP** Braintree application (cards + PayPal) under the same entity, disclosing Stripe as the primary processor. | Submitted |
| 10:00–11:00 | G | **CP** Meta: confirm the Business Portfolio is verified. DEV adds the domain-verification TXT. Create dataset `SY-Web`. Assign AA1/AA2/AA3 (§6.1). In Billing & payments, read each account's **daily spending limit** and request an increase on AA1 to ≥ $15K/day. Add 2 payment methods with ≥ $150K of available credit each. Set an **account spending limit** equal to the D1 cash plan. | Limits and screenshots in `#war-room` |
| 10:00–12:00 | VA2 | Shoutout sourcing (§4.2): 60 candidate Facebook pages + 20 newsletters/podcasts into the Partner sheet | 80 rows with page URL, follower count and admin contact |
| 11:00–12:00 | G | **CP** Engage the attorney. Send FUNNEL §5, OFFER §2.3, this file's §2.1, §3.1, §4.6 and §5.5. Ask for markup by D−4. | Engagement letter signed |
| 11:00–12:00 | CL | Outreach to 10 PT/DPT and 5 RDN candidates (paid retainer, 3–4 h/week). Book PERF for D−6 09:00–13:00 with a video release. Contact 2 cultural consultants (FUNNEL §0.4). | 3 interviews booked. PERF confirmed. |
| 13:00–15:00 | G | **CP** Warm-list consent audit (§3.1): export the Unignorable and K9SUPPS contact tables with consent source, date, the exact opt-in text, SMS keyword log and unsubscribe status. Decide D6. | Segment table (§3.2) filled with real counts |
| 13:00–18:00 | DEV | Blitz config and code gaps (§1.5 items 1–7): the three launch cells (`BLITZ_PRICE_CELLS=2500,3000`, `ARM_B_SHARE=0.5`, `TRIAL_ARM_ENABLED=true`, `TRIAL_THEN_PRICE_CENTS=2500`; paid 25/25/50, non-paid 50/0/50; sticky by cookie + email), `FOUNDING_COHORT_CAP=5000`, `OFFER_MODE=blitz`, `{{OFFER_TERMS}}` rendering per recipient cell in emails and DMs, the public counter endpoint, the processor-agnostic payment table | PR open, unit tests pass |
| 13:00–18:00 | CL | ElevenLabs voice design for Chang and Sun, voices locked (CHARACTERS §13.3). Start the n8n import (PIPELINE §9 D2–D4 compressed). | Voice IDs saved. Workflow imports without errors. |
| 15:00–16:00 | G | Approve the shoutout outreach templates (§4.5) and the price ceilings (§4.4) | VA2 cleared to send |
| 16:00–18:00 | VA2 | Send the first 30 page outreaches (template A) | 30 sent |
| 17:30–17:45 | all | Standup (the §7.4 agenda, build version: blockers only) | — |

#### D−9 (Sat): the offer goes on the page

| Time | Owner | Task | Done when |
|---|---|---|---|
| 08:00–12:00 | DEV | Quiz A and B on staging, result pages with a **waitlist state** ("Doors open Monday Oct 12 at 7am ET. Want the founding-seat alert?" + email + optional SMS consent). Stripe products and prices: founding $25 and $30 cells, `{{STANDARD_PRICE}}` $35 (default, D4), $7/$17 order bumps on `/join`, bump $9, upsells $27/$29/$7, gifts $49/$119. The $1-then-$25 trial price for cell T25 (live from L1, `TRIAL_ARM_ENABLED=true`). | Every price exists in Stripe test mode |
| 08:00–18:00 | CL | Load prompts into `prompt_versions`, page DNA for the 3 pages. First 20 **non-exercise** scripts (candor, Sun Yoon kitchen, pinned posts × 3 per page) through the compliance checker. Write the 40 ad scripts: 8 concepts (ADS.md concepts 1, 2, 3, 6-fallback, 7, 9, 15, 24) × 5 hooks. | 20 scripts approved; 40 ad scripts in `#approvals` |
| 09:00–13:00 | VA1 | Connect ManyChat to the 3 IG/FB pages. Build the FUNNEL §4 flows (STRONG, TEST, BEGIN, SOUP, FAMILY first) with the crisis intents. | Test comment on a draft post fires the flow |
| 09:00–17:00 | VA2 | Vet 60 pages to a shortlist of 30 (§4.3). Send the second wave of 30 outreaches. | Shortlist sheet |
| 10:00–14:00 | G | Paste the §2 launch copy into the ESP (Customer.io or Klaviyo). Build the segments. Seed-test to 5 inboxes (Gmail, Yahoo, AOL, Outlook, iCloud: this audience uses all five). | Seed screenshots, nothing in spam |
| 14:00–17:00 | G | Write the founding-offer page changes (§2.1 copy) and the post-cap terms (D4) | DEV has the copy |

#### D−8 (Sun): members area and first renders

| Time | Owner | Task | Done when |
|---|---|---|---|
| 08:00–18:00 | DEV | Members area core: magic-link login, Today screen, Mux player, consent log, **cancel in at most two screens**, self-serve refund inside 14 days, receipt and confirmation emails (FUNNEL §5.5 A–F), admin view | E2E: buy → log in → play session → cancel → refund works in test mode |
| 08:00–18:00 | CL | Render the first 20 posts. Render the non-exercise ads (concepts 6-fallback, 7, 9, 15, 24 = 25 ads). | 45 renders in the QA queue |
| 09:00–15:00 | VA1 | QA the renders (face, hands, captions, AI tag in the first 3 seconds, no gray text, disclosures). Build the JOIN (FUNNEL §4.17) and LIVE ManyChat flows (§2.5). | Pass/fail labels in the review app |
| 10:00–12:00 | G + HOST | Event format and run of show (§2.8). HOST reads the script. | HOST confirmed |
| 12:00–16:00 | G | Build the Unignorable and K9SUPPS email/SMS kits (§3) in each brand's ESP as drafts | Drafts ready for attorney review |
| 09:00–17:00 | VA2 | Negotiate. Target 10 pages "agreed in principle" for L3–L9. | 10 verbal yeses |

#### D−7 (Mon): organic goes live, data plumbing

| Time | Owner | Task | Done when |
|---|---|---|---|
| 08:00–09:00 | VA1 | Publish the **3 pinned posts natively in-app** on each of the 3 pages (CHARACTERS §9.2, FALLBACK versions). Follow 10–20 relevant accounts by hand. No automation yet (PIPELINE §5.4, week 0). | 9 pins live, AI labels visible |
| 08:00–18:00 | DEV | **CP** Pixel + CAPI (`META_PIXEL_ID`, `META_CAPI_TOKEN`) with a shared `event_id` for deduplication. Persist UTMs, `mc_id` and `aff` through checkout. Install the affiliate tool snippet (§5.2) and connect it to Stripe. Stripe webhooks feed Supabase. | Test Events in Events Manager show Lead/Purchase from both browser and server, deduplicated |
| 09:00–10:00 | G | Follow up the processors. Send Stripe risk the staging checkout screenshots (terms box, consent box, cancel flow). Send Braintree its documents. | Replies logged |
| 10:00–12:00 | G + ATT | Attorney kickoff call. Walk through the checkout, the founding counter, cross-brand sends and the contracts. | Issues list |
| 13:00–16:00 | G | Reviewer interviews (3). Choose, and send the contract. | Offer sent |
| 08:00–18:00 | CL | Posts 21–60. Event premiere script locked (§2.8). | 60 masters |
| 09:00–17:00 | VA2 | Book the first 5 shoutouts (L3–L6) on the §4.6 terms, paid on proof | 5 signed bookings |
| 13:00–17:00 | SUP (onboard) | Help desk (Help Scout or Gorgias) with the §8 macros, the `help@` inbox, the "text CANCEL" keyword routing (built now, switched on only with SMS) | Test ticket answered from a macro |
| 17:30 | all | Standup | — |

#### D−6 (Tue): the performer shoot

| Time | Owner | Task | Done when |
|---|---|---|---|
| 09:00–13:00 | CL + PERF (+ REV if signed) | Driving-video shoot: 150–250 clips covering the exercise families in the 40 ads, the 30-second chair stand and the 4-stage balance test for the event, the regressions (PIPELINE §9 D6). Form check per the reviewer gate. | Clips tagged in `assets`, release on file |
| 09:00–18:00 | DEV | Staging E2E (Playwright). Lighthouse on `/q/a`, `/start`, checkout: **LCP < 2.0s on 4G** (FUNNEL §2.1). | CI green, LCP report |
| 10:00–12:00 | G | Sign the reviewer (or confirm FALLBACK). Draft the affiliate terms (§5) and the partner kit (§5.6). | Signed or `REVIEWER_SIGNED=false` confirmed |
| 13:00–18:00 | CL | Posts 61–90 | 90 masters |
| all day | VA1 | Organic: 1–2 posts/day/page (week-1 ramp). A human replies to comments for the first 60 minutes. | — |

#### D−5 (Wed): exercise ads, waitlist live

| Time | Owner | Task | Done when |
|---|---|---|---|
| 08:00–18:00 | CL | Render the exercise ads (concepts 1, 2, 3 = 15 ads) from the driving videos. Render the event premiere (3 segments, ~20 minutes in total). | 40 ads rendered |
| 09:00–12:00 | DEV | **Production deploy #1:** quiz + waitlist live on `{{DOMAIN}}`, **checkout behind a feature flag (off)** | `/q/a` live in production |
| 12:00 | VA1 | TEST and BEGIN keywords → quiz → waitlist, live on all 3 pages | A live comment test captures an email |
| 13:00–17:00 | G | Approve all 40 ads against the ADS.md §7 pre-launch checklist | 40 approvals or fix notes |
| 09:00–17:00 | VA2 | 10 shoutouts booked for L3–L9 | 10 signed |

#### D−4 (Thu): attorney markup, waitlist ads

| Time | Owner | Task | Done when |
|---|---|---|---|
| 09:00 | G | **Optional waitlist seeding: $300/day on AA2, D−4 to D−1** ($1.2K, outside the model), optimizing Lead to `/q/a`. This seeds `SY-Web` with Lead events and builds the founding list for L1's first email. | Delivering |
| 10:00–16:00 | DEV | Apply the attorney markup to checkout, terms and cancel. First version of the dashboard (§7.2). | Diff merged |
| 08:00–18:00 | CL | Posts 91–120. Event render review with HOST. | — |
| 10:00–14:00 | G | Warm-list sends finalized: attorney-approved copy, designated sender, suppression lists merged, scheduled for L1/L3/L6 (email) and L2/L8/L14 (SMS, cleared segments only) | Scheduled |
| 14:00–17:00 | VA2 + G | Affiliate recruiting list: 300 PTs, trainers, tai chi/chair-yoga instructors and activity directors (§5.3) | Sheet ready |

#### D−3 (Fri): live money

| Time | Owner | Task | Done when |
|---|---|---|---|
| 09:00–12:00 | DEV | **CP** Live Stripe keys (`ALLOW_LIVE_STRIPE=true`) behind a password gate. Live webhooks. Counter endpoint pointed at live data. Radar dispute rules for RDR/Ethoca (§6.8). | Live checkout reachable with the password |
| 12:00–15:00 | G + DEV | **CP** Test-purchase matrix #1 (§1.6), real cards, then refunds | Every row passes |
| 08:00–18:00 | CL | Posts 121–150. Final QA on all 40 ads. | **150 masters (93 usable at launch), 40 ads** |
| 13:00–15:00 | G | Event registration page `/live` published. Invite the waitlist (email). | Page live |
| 15:00–17:00 | G | Preliminary go/no-go (§1.4) | Open items have owners |

#### D−2 (Sat): ads into review

| Time | Owner | Task | Done when |
|---|---|---|---|
| 09:00–12:00 | VA1 + G | Upload the 40 ads to AA1 (the §6.2 campaign map), **scheduled to start L1 05:00 ET**, so review finishes early | All "In review" |
| 09:00–17:00 | DEV | Load test (200 concurrent checkouts), backups, Sentry alerts, a status page, the rollback plan | Report in `#war-room` |
| 10:00–14:00 | CL + HOST | YouTube Premiere scheduled. Facebook Live via an encoder test (Facebook's Premieres feature has been deprecated ([Social Media Today](https://www.socialmediatoday.com/news/meta-is-depreciating-its-video-premieres-option-on-facebook/626251/)), so the pre-recorded segments play inside a live stream, labeled as pre-recorded). | Test stream recorded |
| 14:00–14:30 | VA2 + SUP + G | Crisis tabletop: 5 scripted scenarios (§8.3) | Everyone knows the page path |
| 15:00–17:00 | G + DEV | **CP** Pixel/CAPI QA #2 in Test Events | Pass |

#### D−1 (Sun): dress rehearsal and go/no-go

| Time | Owner | Task | Done when |
|---|---|---|---|
| 10:00–12:00 | G + DEV + VA1 + SUP | **Dress rehearsal:** the full journey on 3 devices (an iPhone at the largest text size, an Android, a desktop). 3 live purchases ($25 cell, $30 cell, $25 + the $7 Reset order bump), 1 refund, 1 cancel, 1 gift. Check the emails, the counter (+1 on purchase, −1 on refund), the descriptor on the card app, CAPI event_ids, the affiliate attribution with a test link. | Every row passes |
| 12:00–13:00 | G | Check ad review status. Fix any rejections. | ≥ 20 ads approved (target 40) |
| 14:00–15:00 | CL + HOST + VA2 | Event technical rehearsal: stream, chat moderation, the co-host's live cues | Recording reviewed |
| 17:00–17:30 | all | **Go/no-go** (§1.4) | Signed in `#war-room` |
| 22:00 | DEV | Deploy freeze. Only hotfixes after this. | — |

#### D0 = L1 (Mon): launch day

| Time | Owner | Task |
|---|---|---|
| 05:00 | auto | Ads start (AA1). Checkout flag on. Counter public. |
| 06:45 | auto/VA1 | First organic post on each page (the launch pinned post goes up natively at 07:00) |
| 07:00 | auto | Email E1 to the Strong Years list (§2.3) |
| 08:00–08:15 | all | Standup #1 (§7.4) |
| 09:00 | auto | Unignorable email U1 and K9SUPPS email K1 (§3) |
| 10:00, 12:00, 15:00, 18:00 | G | Spend and funnel checks against §7.3. Changes only by the §6.4 rules. |
| 10:00–20:00 | VA2 | Comments and DMs on the launch posts (the first-60-minute rule), crisis first response during staffed hours |
| all day | SUP | Tickets: 2-hour first-response SLA on L1–L5 |
| 21:00 | G | Day-1 recap: arm-B purchase rate, cost per opt-in, refunds requested, any errors |

### 1.3 Staffing and hours during L1–L14
- Coverage **07:00–23:00 ET, 7 days** (the audience spans every US time zone and is up early). VA2 07:00–15:00, SUP 12:00–20:00, G or CL on call for `#crisis` 15:00–23:00. After 23:00 the crisis auto-replies run (FUNNEL §4.14) and a human reads them at 07:00. Say so in the auto-reply ("a person on our team will read this in the morning"), always with the crisis-resources line (988, free, 24/7; 911 in an emergency). **No public copy, page or chat message may say a human is available 24/7 or "on call".** Buying true 24/7 coverage (a BPO or paid rotation) is an open decision in LAUNCH_CHECKLIST.md.
- Add a **second support agent on L2** if tickets exceed 1 per 20 new members a day, or if first response goes past 2 hours.

### 1.4 Go/no-go checklist (D−1, 17:00). Any "no" in the first block stops the launch.

**Stop-ship items**
- [ ] Attorney sign-off on checkout, terms, cancel, founding copy, cross-brand sends
- [ ] Live test purchases pass all §1.6 rows, including the refund and cancel rows
- [ ] Consent log stores the timestamp, IP, exact rendered text, checkbox state, price cell and next charge date for every test order
- [ ] Cancel takes at most two screens and works on the largest iPhone text size; with `SMS_ENABLED=false`, the phrase "text CANCEL" appears on no page, email or receipt (grep the rendered templates)
- [ ] Founding counter reads the live processors; a refund decrements it; the displayed number matches Stripe exactly
- [ ] AI disclosure shows on every page header, the checkout, the first DM, email footers and all 3 pinned posts
- [ ] Crisis intents fire on test phrases in DMs and in the AI chat; the `#crisis` page reaches a human
- [ ] Dispute prevention enrolled (RDR, Ethoca, OI) and Radar rules set
- [ ] ≥ 20 ads approved; AA1 payment methods valid; account spending limit set

**Launch-with-workaround items**
- [ ] 10DLC approved (if not: email-only reminders; SMS copy parked)
- [ ] Braintree approved (if not: Stripe only; §6.7 caps apply)
- [ ] Reviewer signed (if not: `REVIEWER_SIGNED=false`)
- [ ] ≥ 4 shoutouts booked for L3–L6 (if not: VA2 books every day; Meta holds)

### 1.5 App deploy runbook (`/home/claude/rebuild/app`)

The app is a Next.js 15 + Supabase + Stripe project (`package.json` name `strong-years`). It runs in mock mode whenever an integration's env vars are missing (`src/lib/config.ts`), so **production must set every variable below, or it silently runs stubs.**

| Env var | Production value | Note |
|---|---|---|
| `NEXT_PUBLIC_SITE_URL` | `https://{{DOMAIN}}` | |
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | production project | Without them the store is **in-memory** and loses every order on redeploy |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `ALLOW_LIVE_STRIPE=true` | live keys from D−3 | Without them the built-in checkout **simulator** runs |
| `OFFER_MODE` | `blitz` | The app default. `standard` returns to the OFFER.md baseline ($20, $1 trial, $7/$17 front ends) |
| `BLITZ_PRICE_CELLS`, `BLITZ_DEFAULT_PRICE_CENTS`, `BLITZ_PRICE_TEST` | `2500,3000`, `2500`, `true` (inside the founding cells, L1–L14; then `false` with the winner as the default) | $25 is the default display until the test is read |
| `STANDARD_PRICE_CENTS` | `3500` = `{{STANDARD_PRICE}}` (D4, client decision) | Used after the cap closes |
| `PRICE_MONTHLY_CENTS` | `2000` | Baseline price, used only when `OFFER_MODE=standard` |
| `TRIAL_ARM_ENABLED`, `TRIAL_THEN_PRICE_CENTS`, `FRONTEND_PAGES_ENABLED` | `true`, `2500`, `false` | Cell T25 ($1 for 7 days, then $25) is live from L1; `/reset` and `/kitchen` redirect to `/join` ($7/$17 are order bumps) |
| `SMS_ENABLED` | `false` until 10DLC / toll-free approval (3–6 weeks) | Launch runs on email + DM |
| `ARM_B_SHARE` | `0.5` | 50% founding / 50% trial from L1 (the 3-cell launch). `1.0` only after a green day-40 gate (R4); `0` after a red day-10 or day-40 gate (R17). The L4 early-read fallback sets `0.25`. |
| `FOUNDING_COHORT_CAP` | `5000` | Real cap |
| `REVIEWER_SIGNED` | `false` until the contract is signed | Reviewer gate |
| `META_PIXEL_ID`, `META_CAPI_TOKEN` | the `SY-Web` dataset | |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | production key, `claude-haiku-4-5` | Otherwise scripted replies |
| `SESSION_SECRET`, `CRON_SECRET`, `ADMIN_USER`, `ADMIN_PASSWORD` | long random values | The code defaults are public demo values. **Change them.** |
| `SUPPORT_EMAIL`, `MAILING_ADDRESS`, `DISPLAY_TZ` | real values | The mailing address is a CAN-SPAM requirement |
| `FRIENDSHIP_LINE_NUMBER` | verified number, or blank | FUNNEL §4.14: verify before launch |
| Email/SMS provider keys (Resend/Postmark, Twilio) | production | Without them messages go only to the outbox table |

**Code gaps to close before L1 (DEV, D−10 to D−4).** These come from reading the current source.
1. **Founding price split cells.** Per-visitor cell assignment now reads `BLITZ_PRICE_CELLS=2500,3000` (`src/lib/config.ts`, default display `BLITZ_DEFAULT_PRICE_CENTS=2500`). Confirm it is sticky by cookie + email and stored on the order and the consent record. It's needed for the L1–L5 $25 vs $30 test.
2. **Trial converts at the founding price while the cap is open** (required: T25 is live from L1). Today arm A renews at `prices.monthly`. D4 says a trial member who converts before the cap closes gets `{{FOUNDING_PRICE}}` and takes a seat when that first full charge succeeds.
3. **Counter definition.** `foundingSpots(claimed)` must receive `claimed` = founding subscriptions whose first charge has succeeded **and** hasn't been fully refunded or charged back, across **both** processors. Cache it for 60 seconds. Show "updated [time]".
4. **Auto-close.** When `left ≤ 0`, the checkout already refuses founding orders ("The founding cohort is full. New members join at the standard price of {{STANDARD_PRICE}} a month."). Also fire a webhook to n8n that **pauses every ad whose name contains `FOUNDING`** and swaps the site banner.
5. **Second processor.** No Braintree code exists yet. Build a `payments` abstraction (`processor` column on orders and subscriptions, Braintree webhooks → the same tables). Target go-live **L21** (the model's Blitz!B56 assumption), only once built and approved; until then get written Stripe volume pre-approval (LAUNCH_CHECKLIST.md). Renewals stay on the processor that holds the card.
6. **Renewal reminders before every charge.** The code has `reminderHoursBeforeCharge: 48` for trials. Add an email (and SMS once approved) **7 days and 2 days before the first renewal** of a founding membership **and 3 days before every later renewal**, plus the **California annual reminder** every 12 months for all auto-renewing members and a price-change notice exactly 30 days ahead (§6.8).
7. **Founding-week bonus flag.** `BONUS_DEADLINE=2026-10-16T23:59:00-07:00`. Before the deadline, founding orders get the keep-forever program entitlement and **upsell 1 is skipped** (they already have it; lead with the kit). After it, the entitlement stops being granted. The program is usable in the app at once, but **the keep-forever download vests on day 15** (after the refund window); a refund inside 14 days removes it.
8. **SMS-conditional rendering.** Every `{{IF_SMS: …}}` fragment in templates renders only when `SMS_ENABLED=true`.
9. **Founding close date.** `FOUNDING_CLOSE_DATE` (default L90) closes the cohort even if 5,000 isn't reached; `{{COUNT_LINE}}` switches format at 1,000.

**Deploy steps:** `npm ci && npm run typecheck && npm test && npm run build`. Apply `supabase/migrations`. Deploy to Vercel production. Set the Stripe webhook endpoint (`/api/stripe/webhook` or the path in the repo). Run `npm run test:e2e` against production with the test-card matrix before the flag goes on.

### 1.6 Pixel/CAPI and money QA: test-purchase matrix (D−3 and D−1)

Every row uses a real card in live mode and is refunded within the hour. SUP refunds the rows so the refund path gets tested too.

| # | Path | Check |
|---|---|---|
| 1 | Ad click (Test Events code) → `/q/a` → result → `/join` founding $25 (default cell) → bump → upsell (kit) → decline | Server (CAPI) `Lead` on the neutral path `/q/a` and `Purchase`; the app is CAPI-only, so there's nothing to deduplicate unless a browser pixel is added on `/join` (then dedup on one `event_id`). **No quiz answers, no condition words in `event_source_url` or custom data.** Value = the charge. `utm_*` and `fbclid` stored on the order. |
| 2 | Founding $25 cell (forced by query param in staging only) | Cell stored on the order, the consent log and the Stripe metadata |
| 3 | `/join` + the $7 Reset order bump | Terms box shows "first month $25 today" plus the ticked $7 add-on; renewal $25 on today + 1 month |
| 4 | $1 trial, cell T25 (live in production) | Trial terms with $25 after day 7; the 48h reminder is scheduled (email while SMS is off); the first full charge takes a founding seat and locks $25 (gap 2); a T25 visitor who opens a `/join` link sees the trial version; cell stored on the order and consent log |
| 5 | Gift $49 | No auto-renew; gift email to the recipient; no `Subscribe` event |
| 6 | Affiliate link `?via=test` → founding | Referral appears in the affiliate tool with commission = 30% of the net charge (the D7 default) |
| 7 | Shoutout link `/start?via=testpage` | `utm_source=shoutout`, page slug on the order |
| 8 | Self-serve refund inside 14 days | Refund processed; counter −1; `Purchase` not re-sent; confirmation email; ledger row |
| 9 | Cancel on an iPhone with the largest text size | At most two screens; equal-prominence "Finish canceling"; confirmation email; access until period end |
| 10 | Text CANCEL (once SMS is live) or email "cancel" | Routed to SUP; cancelled within 1 hour during staffed time |
| 11 | Declined card (Stripe test decline in staging) | Plain-English error in Ink text; no double charge |
| 12 | Bank app statement | Shows `STRONGYEARS MEMBER` |

---

## 2. The founding-member launch

### 2.1 The founding cohort: mechanics and the honesty rules

**What a founding member gets (all real, all delivered):**
1. **The founding price, `{{FOUNDING_PRICE}}`/month, locked while the membership stays active, pauses included.** If a founding member cancels and later rejoins, they pay the price current at that time. The FAQ and the terms page say so.
2. A "Founding member" badge in the app and on their Courtyard profile.
3. The **founding annual option at $249/yr** (≈ 10 months at $25; AUDIT F07; client decision), offered only after renewal 1, from **L35**.
4. **Founding-week bonus, L1 to L5 only** (ends Fri 11:59pm PT): one 12-week program of their choice to keep forever, even after cancelling. It's the same program sold for $27 as upsell 1. The entitlement is only granted to orders placed before the deadline (`BONUS_DEADLINE`, §1.5 gap 7). It's usable in the app right away; **the download unlocks on day 15**, and the copy says so.

**The cap.** 5,000 founding seats (configurable `FOUNDING_COHORT_CAP`) **or `{{FOUNDING_CLOSE_DATE}}` (default L90), whichever comes first**, counted by the app from its member database, which records every successful first charge from both payment processors (§1.5 gap 3). A seat is taken when a founding membership's first charge succeeds. It's released if that charge is fully refunded or charged back. **The cap doesn't reset, isn't extended and is never "reopened for a few more".** When it's full, checkout switches to the standard membership at `{{STANDARD_PRICE}}` automatically (cell T25 continues at the standard price after the cap closes, unless the gates have already retired it) and the founding ads pause (§1.5 gap 4).

**The price after the cap: `{{STANDARD_PRICE}}` = $35/mo by default (D4; configurable, client decision).** It's stated on the terms page and in the founding FAQ from L1. The team commits to charging it. If it won't, drop the "founding price" language and sell only the founding perks (items 2–4).

**Cell fairness rule (from L1).** Paid visitors are split 25% F25 / 25% F30 / 50% T25; organic, warm-list, shoutout and affiliate traffic 50% F25 / 50% T25. The cell sticks by cookie and email, so no visitor ever sees two offers; emails and DMs render `{{OFFER_TERMS}}` for the recipient's cell. **Partner copy never states a price or an offer** (the landing page does). The $25-vs-$30 read happens inside the founding cells (L5 provisional, L14 confirmed). When the test ends:
- If **$25 wins**, every $30 founding member is moved down to $25 permanently and emailed about it on L6 ("We lowered your founding price. Nothing for you to do.").
- If **$30 wins**, the $25 members keep $25. It's their locked founding price.
- Either way, nobody is ever moved up.

**The counter (public display spec).** It shows on `/start`, `/join` (the founding checkout) and `/live`:
> **Founding seats taken: 1,284 of 5,000**
> Counted from our member database. Updated 9:42am ET. If someone takes a refund, their seat goes back.

Emails and posts show the number **as of a stated time** ("1,284 of 5,000 as of 6:30am ET Monday"). They never show a live-looking number in a static medium.

**Display rule `{{COUNT_LINE}}` (AUDIT F19).** Below 1,000 members, public copy (emails, DMs, posts, the `/join` box) reads: "Founding membership is open to the first 5,000 members or until {{FOUNDING_CLOSE_DATE}}, whichever comes first. See the live count: {{DOMAIN}}/terms#founding". From 1,000 it reads "{{COUNT}} of 5,000 founding seats taken as of {{COUNT_TIME}}". The terms page always shows the exact live count. Both versions are true; neither is a countdown. Counter-update posts run only once the count is ≥ 1,000.

**Language rules for everyone writing copy during the blitz**

| Allowed (true and verifiable) | Banned (fake scarcity or pressure) |
|---|---|
| "5,000 founding seats. 1,284 taken as of 9:42am ET." | "Only a few spots left!" (unless the count really is ≥ 4,900) |
| "Founding price locked while you stay subscribed. After the 5,000th founding member, new members pay {{STANDARD_PRICE}}." (default $35, D4) | "Price goes up tomorrow" (it goes up at the cap, not on a date) |
| "The founding-week bonus ends Friday at 11:59pm Pacific." | Countdown timers that reset per visitor. "Evergreen" deadlines. |
| "Charged today. Refund yourself in your account within 14 days." | "Risk-free" without the terms. "Free" for a charged product. |
| "The same program we sell for $27." | "A $217 value". "Was $99, now $30." (No fictitious former prices, 16 CFR 233.) |
| "Chang is an AI character. The chat and our host are live." | "Join Chang live" (he's pre-recorded) |
| Real aggregate numbers ("Members did 3,412 sessions this week") | Invented social proof, testimonials or "as seen in" |

### 2.2 The 5-day doors-open calendar (L1 Mon → L5 Fri)

| | **L1 Mon: doors open** | **L2 Tue: what it is** | **L3 Wed: the live test** | **L4 Thu: answers** | **L5 Fri: bonus ends** |
|---|---|---|---|---|---|
| **Organic (3 pages)** | 07:00 PIN-L1 posted natively and pinned (replaces pin 2). Keyword **JOIN** on the 12:45 and 19:00 slots. Other slots follow the calendar (CONTENT_SYSTEM §11). | FOUNDER on 1 slot per page, **LIVE** on 1 slot. 16:00 couple sketch about the test (F08). | 07:00 PIN-EVENT (replaces pin 3 until 23:59). 12:30 "starting in 30 minutes" Story. Premiere 13:00 + encore 19:00. | Clip of the event's best moment (with consent where a chat name shows; otherwise anonymized). Sun answers the 3 top questions (F26). | 12:45 counter-update post (real number). 19:00 Chang "last call" F11 episode. Pins restored at 23:59 PT. |
| **Paid (AA1)** | 05:00 launch ads start (§6.2), 3 cells. $3,000/day. | Same. First 150-opt-in read at 12:00 (§6.4). | Same. + `LIVE` retargeting ad to L1–L2 quiz completers who didn't buy ($100, 11:00–13:00). | **L4 early read** at 09:00 (§6.3; no spend step-up before the day-10 gate). | Same. Bonus-deadline wording pulled from ads at 23:59 PT (VA1 checklist). |
| **Email** | E1 07:00. E2 19:30 (non-buyers). | E3 07:00 | E4 07:00, E4b 12:45 (registrants), E5 16:00 | E6 07:00 | E7 07:00. E8 20:00 ET (non-buyers). |
| **SMS** (Strong Years consent only; after 10DLC approval; 10:00–20:00 recipient time; ≤ 1 a day) | S1 10:00 | — | S2 12:45 ET (registrants who opted in to texts) | — | S3 18:00 |
| **DM** | JOIN flow on. Messenger weekly-tip subscribers: tip + one launch line. | LIVE flow on | In-window reminders to LIVE-flow contacts (inside 24h only) | +22h check-ins | JOIN flow gets the "bonus ends tonight" line until 23:59 PT |
| **Warm lists** (§3) | Unignorable U1, K9SUPPS K1 (09:00) | SMS (cleared segments only) | Unignorable U2 (gift angle) | — | — |
| **Shoutouts** | — | — | First post (1) | 2 | 3 |
| **Affiliates** | Recruiting opens (§5) | | | | |

Model mapping: warm emails on model days 1, 3, 6, 9, 13, 20, 27, and SMS on days 2, 8, 14 (Blitz sheet send weights). Shoutouts ramp 1 → 4 a day from L3. Both match Blitz_Plan.

### 2.3 Launch emails (Strong Years list: waitlist + every quiz opt-in + DM email captures; buyers are suppressed and get onboarding instead)

**Cell rendering (3-cell launch).** Every launch email and DM below is written in the founding (charge-today) version. Recipients assigned to T25 get `{{OFFER_TERMS}}` swapped for the trial version: "• $1 for your first 7 days, then $25 a month as a founding member. We'll email you 2 days before the first $25 charge. • 14-day money-back guarantee on that first $25 charge (one per person). • Cancel online anytime, two screens at most, or reply 'cancel' to any email." Lines that say "You're charged today" or "{{FOUNDING_PRICE}} today" are part of `{{OFFER_TERMS}}` and never reach a T25 recipient.

**Sender:** `Chang Yin (Strong Years)` or `Sun Yoon (Strong Years)` for content emails, `Strong Years Team` for account emails, all from the same address (FUNNEL §6). **Footer on every email** (FUNNEL §6, FALLBACK version): *"Chang Yin and Sun Yoon are AI characters; their story is fictional. Sessions and recipes are built from published guidelines for older adults. General education, not medical advice. [Manage membership] [Unsubscribe] {mailing address}"*. Format: 20px body, one Persimmon button, Ink text only, plain-text version.

`{{FOUNDING_PRICE}}` is filled from the recipient's sticky cell. `{{COUNT}}` and `{{COUNT_TIME}}` are filled at send time.

---

**E1 · L1 07:00 · from Chang**
**Subject:** Doors are open. 5,000 founding seats.
**Preheader:** Price locked for as long as you stay. 14-day money-back.

> Hi {first_name},
>
> Chang here. I'm an AI character, made by the Strong Years team. The exercises are real.
>
> Strong Years is open today.
>
> Every morning: one 8 to 12 minute session with me. Strength, balance, mobility. A chair version of everything. Sun Yoon's recipes every Sunday. Your Strength Age test every month, so you see the change in numbers, not feelings.
>
> The first 5,000 members are founding members.
> • Your price is {{FOUNDING_PRICE}} a month, locked for as long as you stay subscribed. After the 5,000th founding member, new members pay {{STANDARD_PRICE}}.
> • You're charged today. If it isn't worth it, refund yourself in your account within 14 days. No questions. (One money-back guarantee per person.)
> • We'll email you before every renewal.
> • Cancel online anytime. Two screens at most, or reply "cancel" to any email{{IF_SMS: , or text CANCEL}}.
>
> {{COUNT_LINE}}
>
> Join by Friday at 11:59pm Pacific and you also keep one 12-week program of your choice forever, even if you cancel one day. It's the same program we sell for $27. From Saturday, it's not included.
>
> **[Become a founding member]** → `{{DOMAIN}}/join?utm_source=email&utm_medium=owned&utm_campaign=l1_e1`
>
> Your first session is 8 minutes. One chair against the wall. Arms crossed.
>
> Same time tomorrow.
> Chang
>
> P.S. Want to try the test first? On Wednesday at 1pm Eastern we premiere "Chang's 30-second test". I'm pre-recorded. The chat and our host, [HOST NAME], are live. [Save my seat] → `/live`

---

**E2 · L1 19:30 · from Sun Yoon · non-buyers only**
**Subject:** The honest version
**Preheader:** What it is, what it isn't.

> No, I'm not real. Sun Yoon is an AI character. My opinions came with me.
>
> What Strong Years is:
> • A short session every day. Short means 8 to 12 minutes. You won't become a bodybuilder. You'll get up from the chair more easily. That's the point.
> • A number every month. Chair stands, balance, a few more. It's a fitness estimate, not a medical test.
> • My recipes on Sunday. Protein at every meal. Grams, not vibes.
>
> What it isn't:
> • Not a doctor. Not physical therapy. If something hurts sharply, stop and call your doctor.
> • Not magic. Onion water is soup. Put the onion in the soup.
> • Not a trap. Cancel in two screens. Refund yourself within 14 days. We'd rather lose the money than your trust.
>
> {{COUNT_LINE}}
>
> **[Look inside first]** → `{{DOMAIN}}/start`
>
> Now go eat.
> Sun Yoon

---

**E3 · L2 07:00 · from Chang**
**Subject:** One chair. Thirty seconds. Wednesday.
**Preheader:** A premiere with a live chat and a real host.

> Chang here (AI character).
>
> Wednesday at 1pm Eastern (10am Pacific) we premiere "Chang's 30-second test". It's pre-recorded. The chat is live, and so is our host, [HOST NAME], a real person on the Strong Years team.
>
> You need: a sturdy chair with no wheels, pushed against a wall. Shoes on. 25 minutes.
>
> What happens: we do the 30-second chair stand together. You type your number in the chat. [HOST NAME] shows what published norms say for each age group. Then Sun Yoon does the balance test with you, and explains why ten seconds on one leg is worth practicing.
>
> Please don't do the standing tests if you've fallen recently, get dizzy when you stand up, or have been told not to exercise. Watch seated, and ask your doctor first.
>
> **[Save my seat]** → `/live` (adds it to your calendar and sends a reminder)
>
> Can't make 1pm? The encore is at 7pm Eastern.
> Chang

---

**E4 · L3 07:00 · from Chang · everyone not yet a member**
**Subject:** Today at 1pm Eastern
**Preheader:** Chair against the wall. That's the whole setup.

> Today at 1pm Eastern (10am Pacific): "Chang's 30-second test" premieres, with a live chat and our host [HOST NAME].
>
> Set the chair against the wall now, so it's ready.
>
> **[Join at 1pm]** → `/live`
>
> Encore at 7pm Eastern.
> Chang

**E4b · L3 12:45 · registrants only · from Strong Years Team**
**Subject:** Starting in 15 minutes
> Chair against the wall, shoes on, water nearby. **[Join now]** → `/live`. Chang is pre-recorded; the chat and [HOST NAME] are live.

---

**E5 · L3 16:00 · from Chang**
**Subject:** Your number, explained (replay inside)
**Preheader:** It's the most trainable number I know.

> Here's the replay: **[Watch the replay]** → `/live/replay`
>
> What your number means, in general. Published senior-fitness norms (the same ones the CDC's STEADI materials use) list typical 30-second chair-stand ranges by age. For people aged 70–74, under 12 for men and under 10 for women is below average (other ages are on the card in the replay). It's a number, not a diagnosis. Above it? Keep it there. Below it? Good news: leg strength is one of the most trainable things there is. A review of 121 trials in older adults found large gains in strength and in getting up from a chair with 2–3 sessions of strength training a week.
>
> Strong Years is that, 8 to 12 minutes a day, at your level, with a retest every month so you can watch the number move.
>
> {{COUNT_LINE}} The founding-week bonus (a 12-week program to keep forever) ends Friday at 11:59pm Pacific.
>
> **[Become a founding member]** → `/join`
>
> Tell me your number. I'm counting.
> Chang

(Evidence: E11 CDC STEADI norms and E01, the 121-RCT review, in EVIDENCE.md.)

---

**E6 · L4 07:00 · from Sun Yoon**
**Subject:** The questions you asked us yesterday
**Preheader:** Short answers. I'm older, so I'm right.

> Short version:
>
> **Is Chang real?** No. We're AI characters, made by a team. The exercises come from published research, and the sources are on our website. The Wednesday host is a real person, and we said so.
>
> **Is it safe for me?** Every session has a chair version and a "sore knee / sore back / low energy today" button. If you have a heart condition, recent surgery, a recent fall, dizziness, or take blood thinners, ask your doctor before starting. That's a real rule, not fine print.
>
> **Why charge today instead of a free trial?** Founding members lock their price. If it's not for you, refund yourself in your account within 14 days. Two taps.
>
> **How do I cancel?** Account → Membership → Cancel. Two screens at most. Or reply "cancel" to any email{{IF_SMS: , or text CANCEL}}. Nobody will call you, and you never need to call us (if you'd like to, our billing line is {{PHONE}}).
>
> **I'm bad with technology.** Big buttons, big captions, one button that says "Start today's session". If you get stuck, reply to this email and a person helps you.
>
> **Can my husband do it too?** Add a partner for $8 a month. He gets his own level. You'll still beat him at balance.
>
> **What do I need?** A sturdy chair. Later, a couple of water jugs or bands.
>
> {{COUNT_LINE}}
>
> **[See everything inside]** → `/start`
>
> Sun Yoon

---

**E7 · L5 07:00 · from Chang**
**Subject:** The founding-week bonus ends tonight
**Preheader:** 11:59pm Pacific. The founding price doesn't end tonight. The bonus does.

> One thing ends tonight at 11:59pm Pacific: the founding-week bonus. Join before then and you keep one 12-week program of your choice forever (Strong at 70, Back Strong, Balance & Steady Feet, Gut Reset with Sun Yoon, Grip & Hands, or Walk Stronger), even if you cancel one day.
>
> What doesn't end tonight: founding membership. It closes at 5,000 members or on {{FOUNDING_CLOSE_DATE}}, whichever comes first. {{COUNT_LINE}}
>
> Your price: {{FOUNDING_PRICE}} a month, charged today, locked while you stay. 14-day money-back. Cancel online anytime.
>
> **[Join before 11:59pm Pacific]** → `/join`
>
> Chang

**E8 · L5 20:00 ET · from Sun Yoon · non-buyers**
**Subject:** About 7 hours left on the bonus
> The bonus program ends at 11:59pm Pacific (2:59am Eastern). After that you can still join, but the program isn't yours to keep. That's all. No drama. **[Join tonight]** → `/join`. Sun Yoon

---

### 2.4 Launch SMS (only numbers that opted in to Strong Years texts; sent after 10DLC approval)

Rules: brand name first. STOP language on every marketing text. **10:00–20:00 recipient local time. At most 1 marketing text a day and never more than 3 contacts in 24 hours** (Florida's mini-TCPA allows 8am–8pm and 3 attempts per rolling 24 hours ([Klaviyo](https://help.klaviyo.com/hc/en-us/articles/4405332994843)); we run tighter than that everywhere). Florida also expects a callable phone number in messages, so include the support line in S1. Opt-outs are honored immediately, and always within 10 business days ([BCLP](https://www.bclplaw.com/en-US/events-insights-news/the-tcpas-new-opt-out-rules-take-effect-on-april-11-2025-what-does-this-mean-for-businesses.html)).

- **S1 · L1 10:00 local:** `Strong Years: doors are open. Founding members lock {{FOUNDING_PRICE}}/mo while subscribed. 14-day money-back. {{DOMAIN}}/join Help: {{PHONE}}. Reply STOP to opt out.`
- **S2 · L3 12:45 ET (event registrants who opted in):** `Strong Years: Chang's 30-second test premieres in 15 min. Chair against the wall. {{DOMAIN}}/live Reply STOP to opt out.`
- **S3 · L5 18:00 local:** `Strong Years: the founding-week bonus (a 12-week program to keep) ends tonight 11:59pm PT. {{DOMAIN}}/join Reply STOP to opt out.`
- **Renewal reminder (members; before every renewal: 7 and 2 days before the first renewal (L1 buyers renew on L32, so L25 and L30), then 3 days before each later renewal):** `Strong Years: your membership renews {date} at {{FOUNDING_PRICE}}. To keep going, do nothing. To cancel: {{DOMAIN}}/account or reply CANCEL.`

### 2.5 Launch DMs (ManyChat, IG + FB). All automated promotion happens inside the 24-hour window.

**Keyword JOIN** (routes to the founding checkout `/join`; the full flow with email capture and the crisis hook is FUNNEL.md §4.17). Variants: `join, joining, joined, jion, founder, founding, founders, foundr, founding member, 🔑` (FOUNDER, the earlier draft keyword, stays as a variant). Tags `kw_join`, `launch_l1`.

Public replies (rotate): "Sent it to your messages, {first_name}." · "In your DMs. The count is real, by the way." · "Sent. Chair against the wall for day one."

**DM 1**
> Hi {first_name}! Automated message from the Chang & Sun team (AI characters). Reply STOP anytime.
>
> Strong Years is open. The first 5,000 members are founding members: your price is locked for as long as you stay, there's a 14-day money-back guarantee, and you can cancel online in two screens.
>
> {{COUNT_LINE}}
>
> [See what's inside] [Take the 3-minute test first] [How much?]

- **See what's inside** → `{{DOMAIN}}/join?mc_id={{user_id}}&utm_source=ig&utm_medium=dm&utm_campaign=join`
- **Take the 3-minute test first** → `/q/a?...` ("It tells you which of the 4 levels to start on.")
- **How much?** → "Founding membership is {{FOUNDING_PRICE}} a month, charged today, and it renews monthly until you cancel. The price stays the same for as long as you're subscribed. If it's not for you, refund yourself in your account within 14 days. [See it]"

**+20 min if no click:** "Here's the link again, {first_name}: [Look inside]. Most people start with the chair version."
**+22 h check-in:** "Did you get a look? [I joined] [Still deciding] [I have a question]"
- Still deciding → "Most people take the 3-minute test first. It picks your starting level. [Take the test]"
- I have a question → human inbox: "A real person on our team will reply here, usually within a few hours today."
- I joined → "Welcome, founding member. Your first session is 8 minutes: [Start Day 1]"

**On L5 only, DM 1 gets one extra line:** "The founding-week bonus (a 12-week program to keep forever) ends tonight at 11:59pm Pacific."

**Keyword LIVE** (variants: `live, premiere, wednesday`; not `test`, which belongs to the TEST flow). Tags `kw_live`.
> Automated message from the Chang & Sun team (AI characters). "Chang's 30-second test" premieres Wednesday at 1pm Eastern (encore 7pm). Chang is pre-recorded; the chat and our host [HOST NAME] are live. You need a sturdy chair against a wall.
> [Remind me by email] [Add to my calendar] [Can I do it seated?]
- Remind me → email quick reply → registered for `/live` (email reminder E4b).
- Seated → "Yes. Watch seated and do the seated version Chang shows. If you've fallen recently or get dizzy standing, please skip the standing tests and ask your doctor first."

**Global intent: "is the count real?"** → "Yes. It counts members whose first payment went through and who haven't taken a refund. It updates about every minute from our payment system. If someone refunds, the seat goes back."

**Messenger marketing messages** (only to contacts subscribed to the "Weekly tip" topic, FUNNEL §4.15): the L1 weekly tip is a real tip ("Sit down slower than you stand up. Three seconds down.") plus one line: "Also: Strong Years is open, and the first 5,000 members lock their price. [Look]".

### 2.6 Launch pinned posts (all 3 pages; the pin "Hi, we're AI" never moves)

**PIN-L1 "Doors open"** (Duo, SET-TABLE, 30s; on @changyin, @changandsun; a Sun-led version on @sunyoon.kitchen). Corner tag "AI character" from 0:00.
> SUN: "Before anything: we're AI. Made by a team."
> CHANG: "Strong Years is open. Eight minutes a day. A chair version of everything."
> SUN: "First five thousand people are founding members. Their price never goes up while they stay."
> CHANG: "The count is on the page. Real count."
> SUN: "And if you don't like it, refund yourself in fourteen days. I'd rather you get your money back than lie to you."
> CHANG: "Comment JOIN. We'll send it."
> SUN: "He means the team sends it. He's pixels."
> On-screen end card: `Founding membership · 5,000 seats · 14-day money-back · Cancel online` + FALLBACK disclosure line.

Caption: "Comment JOIN and we'll send you the details. Strong Years is open: a new 8–12 minute session every morning, a monthly Strength Age test, and Sun Yoon's Sunday recipes. The first 5,000 members lock their price while they stay subscribed; the count is live on the page. Chang Yin and Sun Yoon are AI characters; sessions are built on published exercise guidelines for older adults. Not medical advice."

**PIN-EVENT** (Chang, SET-GARAGE, 20s; up L2 07:00 to L3 23:59):
> CHANG: "Wednesday. One chair. Thirty seconds." (pats the chair) "Say hello to Coach."
> "I'm pre-recorded. The chat is live. So is our host, a real person."
> "Comment LIVE. We'll send the time."
On-screen: `Wed 1pm ET · encore 7pm ET · chair against the wall`.

**Counter-update post** (F37 text / F36 carousel; weekly while the cap is open, **starting only once the count is ≥ 1,000**). It's only published if every number is pulled from the dashboard at posting time:
> "Founding seats: {{COUNT}} of 5,000 as of {date, time ET}. This week members did {{SESSIONS}} sessions and {{RETESTS}} Strength Age tests. Thank you for starting. Comment JOIN if you want the details. (AI characters. Real numbers.)"

### 2.7 Launch ad copy (AA1, FOUNDING campaign; ADS.md §1 rules apply, including the AI tag in the first 3 seconds)

Ad names contain `FOUNDING` so the auto-pause at the cap works (§1.5 gap 4).

**A1 · Chang UGC (concepts 1/2 creative)**
- Primary text: "Chang Yin is an AI character. The 8-minute sessions are real. / Strong Years is open: a new strength, balance and mobility session every morning, a chair version of everything, and a Strength Age test every month so you can see progress in numbers. / The first 5,000 members are founding members: {{FOUNDING_PRICE}}/month charged today, renewing monthly until you cancel, price locked while you stay subscribed. 14-day money-back. Cancel online in two screens."
- Headline: "Founding membership is open" · Description: "5,000 seats, counted on the page" · CTA: Sign Up

**A2 · Sun Yoon kitchen (concept 7/9 creative)**
- Primary: "Sun Yoon is an AI character. Her opinions are not negotiable. / Strong Years: 8–12 minutes of strength and balance a day with Chang, and her high-protein Sunday recipes with a grocery list. / Founding members lock {{FOUNDING_PRICE}}/month while subscribed. Charged today, renews monthly until you cancel, 14-day money-back."
- Headline: "Grams, not vibes. And a daily session." · CTA: Learn More

**A3 · Quiz first (concept 24 creative; the destination is `/q/a`, the offer appears after the result)**
- Primary: "Chang Yin is an AI character. The test is a standard one used in senior-fitness research. / One chair. Thirty seconds. Find your Strength Age in 3 minutes, free, then see a plan for your level."
- Headline: "Free 3-minute Strength Age test" · CTA: Learn More

**A4 · Adult children, gift (concept 15/16; GIFT campaign)**
- Primary: "Chang Yin and Sun Yoon are AI characters. The gift is real. / Give Mom & Dad Strong Years: a new 8-minute session every morning with a chair version of everything, plus Sun Yoon's recipes. 3 months for $49 or 12 months for $119, prepaid. It never renews automatically."
- Headline: "The gift she'll use every morning" · CTA: Shop Now

Personal-attribute check before upload (ADS §1 rule 2): none of these say "you" + age, health or condition.

### 2.8 The live launch event: "Chang's 30-second test, live"

**Format.** A **pre-recorded premiere with a live chat and a live human co-host.** The pre-recorded segments are labeled "PRE-RECORDED PREMIERE" on screen the whole time they play. HOST appears live on camera at the start, in the middle and at the end, and is introduced as a human. Showings: **L3 13:00 ET** and an **encore at 19:00 ET** (HOST live at both). Replay from 16:00.

**Where**
- `{{DOMAIN}}/live`: the primary room. Our own page, with an embedded player, a moderated chat, the counter and the offer. No pixel on the chat, and no chat content is sent to Meta.
- **YouTube Premiere** on the Chang channel (the "altered or synthetic content" box ticked; Premieres support live chat and a countdown ([YouTube Help](https://support.google.com/youtube/answer/10356739?hl=en))).
- **Facebook Live** on @changyin via an encoder (StreamYard/OBS). Facebook's Premieres feature has been deprecated, so the pre-recorded segments play inside the live stream, labeled as such on screen.
- IG: Story countdown sticker + Stories during the event pointing to `/live`. No IG Live.

**Roles:** HOST (live on camera) · CL (producer: switches segments, lower-thirds) · VA2 + one more moderator (chat: pin the safety note, hide spam and scams, run the crisis protocol, push numbers to HOST) · G (watches the counter and checkout errors, silent) · SUP (on tickets) · DEV (on call for `/live` and checkout).

**Run of show (45 minutes)**

| Clock | Segment | Who | Content |
|---|---|---|---|
| −15:00 | Waiting room | auto | Countdown, music, a looping card: "Chair against the wall · shoes on · water nearby · if you've fallen recently or get dizzy standing, watch seated". Pinned chat message with the same text. |
| 0:00 | Live open | HOST (live) | Script H1 below |
| 3:00 | Premiere 1: "Why 30 seconds matters" | Chang (pre-recorded, 5 min) | Chang explains the chair stand (E11), shows the setup (chair against the wall, arms crossed, feet flat, a counter nearby), demos 5 reps. Frank shows the version with hands on thighs ("Frank's level"). The stop rule: "Sharp pain, dizziness, chest tightness: stop and sit." |
| 8:00 | Premiere 2: "Do it with me" | Chang (pre-recorded, 3 min) | On-screen 30-second timer. Chang counts slowly aloud. "Type your number in the chat." |
| 11:00 | Live: numbers | HOST (live) | Reads 10–15 numbers from chat by first name only ("Maria, 11"). Uses the **norms card** (E11 thresholds + E49 normal ranges, pre-approved) for age bands in general. **Never interprets one person's health.** Script H2. |
| 18:00 | Premiere 3: "Balance, with Sun" | Sun Yoon + Chang (pre-recorded, 8 min) | The 4-stage balance test at the kitchen counter (feet together → semi-tandem → tandem → one leg), with "hand hovering over the counter" cues. Sun wins. Fridge leaderboard bit. "Write this down: practice, don't test yourself into a fall." |
| 26:00 | Live: what Strong Years is, and the offer | HOST (live) | Script H3: the offer, plainly, with the terms read aloud and on screen, and the live counter shown |
| 32:00 | Live Q&A | HOST (live) | 8 minutes. Questions pre-sorted by the moderators. Medical specifics get: "That's a question for your doctor. Here's what research says in general…" |
| 40:00 | Premiere 4: close | Chang + Sun (pre-recorded, 2 min) | "Retest in 30 days. Same chair." Sun: "And eat protein tonight. Grams, not vibes." |
| 42:00 | Live close | HOST (live) | Script H4 |

**HOST scripts (read naturally; the facts are fixed)**
- **H1 (open):** "Hi everyone, I'm [HOST NAME]. I'm a real person, and I work on the Strong Years team. Chang and Sun Yoon, who you're about to see, are AI characters our team created. Their parts are pre-recorded. I'm live, and so is this chat. Two safety things before we start. Your chair goes against a wall, with no wheels. And if you've had a fall recently, get dizzy when you stand, or your doctor has told you not to exercise, please watch seated today and talk to your doctor before trying the standing version. Type where you're watching from!" [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "I'm a licensed physical therapist, [credential]."] FALLBACK: no credential line.
- **H2 (numbers):** "Maria, 11. Jim, 14. Thank you! Here's the general picture, not a diagnosis for anyone. Published senior-fitness norms list typical chair-stand ranges by age, and for people 70 to 74, under 12 for men and under 10 for women is below average. The card on screen has the other age groups. If you're below it, that's the number to work on, and it's very trainable. If anything felt wrong just now, like dizziness or chest discomfort, please sit, rest, and call your doctor, or 911 if it's severe."
- **H3 (offer; read every line, and the same text shows on screen):** "Here's what Strong Years is, plainly. A new 8 to 12 minute session every morning at your level, with a chair version of everything. A monthly retest of these same numbers. Sun Yoon's recipes every Sunday. And a live Q&A every Wednesday with a real person from our team. The first 5,000 members are founding members. Right now [reads the live counter] seats are taken. Founding membership is charged today and renews every month until you cancel, and your price stays the same as long as you stay subscribed. If it's not for you, you can refund yourself in your account within 14 days, and you can cancel online in two screens, or by replying "cancel" to any email{{IF_SMS: , or by texting CANCEL}}. (SMS is off on L3, so the host reads the email version.) If you join by Friday at 11:59pm Pacific, you also keep one 12-week program forever. The link is below the video."
- **H4 (close):** "Write your number on the fridge. Retest in 30 days, same chair, same wall. Thank you for spending this time with us. I'm [HOST NAME], a real person. Chang and Sun are AI. The effort was yours."

**Chat moderation rules (VA2 + moderator)**
- Pin: "Safety: chair against a wall. Dizzy, chest pain or sharp pain? Stop, sit, and call your doctor, or 911 if it's severe."
- Hide immediately: links, phone numbers, WhatsApp/Telegram mentions, "DM me", crypto, investment, gift cards, and anyone claiming to be Chang or the team (**romance-scam protocol, §8.3**).
- Medical emergency language ("chest pain", "can't breathe", "I fell"): the moderator replies in chat "Please stop and call 911 now," flags HOST to repeat it aloud, and logs it in `#crisis`.
- Self-harm or abuse language: FUNNEL §4.14 wording. Don't discuss it in public chat. Follow up by DM or email when possible, and log it.
- "Is he real?" → the moderator pins the answer: "Chang and Sun are AI characters. [HOST NAME] and the moderators are real people."

**After the event:** the replay goes to `/live/replay` with the chat removed. Clips for organic only with chat names removed. The event's attributed purchases are tracked with `utm_campaign=live_l3`.

---

## 3. Warm-list launch kit (Unignorable and K9SUPPS)

### 3.1 Rules that decide who may receive what (the attorney confirms on D−4)

**Email (CAN-SPAM).**
- The **brand the person subscribed to sends the email**, from its own ESP, domain, unsubscribe and postal address. Strong Years is the advertiser. CAN-SPAM lets several marketers **designate one of them as the "sender"**, as long as that marketer is identified in the From line and meets the sender duties ([FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)).
- **From line:** `Unignorable` or `K9SUPPS`, never "Sun Yoon" or "Chang Yin". The header must identify whoever initiated the message (same source).
- **First line of every cross-brand email** says who's writing and why: "This is Unignorable. We're writing because our team just launched something new." The claim "made by the same team" must be literally true (confirm the entity relationship in D2).
- Unsubscribe from a cross-promo = unsubscribe from that brand's marketing. Honor it within 10 business days (FTC). Merge into the Strong Years suppression list too.
- Penalty exposure: up to $53,088 per violating email (FTC). Nobody improvises copy.

**No list transfer, no custom audiences.**
- Unignorable and K9SUPPS contacts are **never** copied into the Strong Years ESP, CRM or Meta. Strong Years only gets a person who clicks and opts in on the Strong Years quiz.
- Unignorable's buyers bought a perimenopause product, which makes the list health-inferred. Moving it between brands, or uploading it to Meta as a custom audience, raises consumer-health-data consent questions (state laws such as Washington's My Health My Data; OFFER §1.4) and risks the `SY-Web` dataset's classification.

**SMS (TCPA + carrier rules).**
- Prior express written consent must "clearly authorize **the seller**" to send marketing texts ([FCC final rule summary](https://www.consumerfinancialserviceslawmonitor.com/2025/09/fccs-final-rule-on-consent-kills-one-to-one-consent-requirement/)). The 2023 one-to-one rule was vacated, but seller authorization remains.
- **So: SMS about Strong Years goes only to Unignorable/K9SUPPS numbers whose opt-in language covers the company and its brands (or affiliated brands), or where counsel confirms the consent reaches this message.** Everyone else gets email only.
- Texts are sent **from the brand's existing registered number**, starting `Unignorable:` / `K9SUPPS:`, with STOP language.
- **Carrier compliance:** the message has to fit the brand's registered 10DLC campaign (use case + sample messages). **Before sending, add a cross-promotion sample message to that campaign.** If the provider requires re-vetting for the update, the SMS waits (10–15 days, [Twilio](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/direct-standard-onboarding)).
- Quiet hours are 10:00–20:00 recipient time, and each brand counts the cross-promo text toward its own frequency cap.

**Pixel hygiene.** Warm traffic lands on `{{DOMAIN}}/start?v=w` (women) or `{{DOMAIN}}/start?v=walk` (dog walkers). Neither URL nor the page copy mentions menopause, a condition or a symptom. UTMs: `utm_source=ug` or `utm_source=k9`, `utm_medium=owned_xbrand`, `utm_campaign={email id}`.

**Consent gaps the audit found (AUDIT_BUSINESS.md F22, §1.4, §5), closed before any send:**
1. **Health-inferred list, different brand.** Using the Unignorable list (a perimenopause purchase) to market a different brand's offer is processing of consumer health data beyond its original purpose in some states, even without a list transfer. **Counsel signs off on this use specifically on D−4**, in writing. Until then, and afterwards unless counsel says otherwise, **suppress Washington, Nevada and Connecticut residents** (by billing or shipping state, and by IP-derived state when no address exists) from every Unignorable cross-promo, unless their original opt-in language covers marketing from affiliated brands.
2. **SMS defaults to off.** Warm SMS is modelled at 0% (the auditor central case) and sent only if the D−10 audit produces, **per number**, a consent record (timestamp, source, the exact opt-in text) whose language names the seller or its affiliated brands, **and** counsel confirms it in writing. No record, no text. The campaign-registration step above still applies.
3. **"Same team" must be literally true.** The first line ("our team just launched something new") is used only if the D2 entity decision makes Strong Years and the sending brand the same company or a documented affiliate. Otherwise the line becomes "We're sharing a new membership from a company we work with", the email is treated as third-party advertising, and CAN-SPAM designated-sender duties are documented in a one-page agreement between the brands.
4. **Opt-outs travel.** An unsubscribe or STOP from a cross-promo is honoured by the sending brand within 10 business days and added to Strong Years' suppression list within 24 hours (as a hash, never as a contact record).
5. **Strong Years' own sending domain.** The Strong Years ESP domain is created on D−10 with DMARC `p=none`, so launch mail needs a warm-up: D−10 to D−1 seed and internal sends plus the waitlist (most engaged first, ≤ 500/day, doubling daily while complaints stay < 0.08% and bounces < 2%); L1–L5 cap sends by engagement tier; move DMARC to `p=quarantine` after 14 clean days.
6. **Records.** Keep the audit export, counsel's written confirmations and each send's segment definition for 5 years (TCPA claims run 4 years).

### 3.2 Segmentation (fill the counts from the D−10 audit)

| Code | Segment | Count | Consent status | Primary angle | Sends (L-day) |
|---|---|---|---|---|---|
| UG-A | Unignorable active MRR members ($27 Inner Circle, $97 Accelerator, Elite) | `n` | email ✓, SMS per audit | Gift first ("for your mom"), then "for you" if 55+ | U2, U4, U6 (3 max, to avoid distracting paying members) |
| UG-B | Unignorable buyers ($37 audit / OTOs), not on MRR, bought ≤ 12 months ago | `n` | email ✓ | "For you" + gift | U1–U7 |
| UG-C | Unignorable quiz leads, never bought, engaged ≤ 90 days | `n` | email ✓ | Gift first, then "for you" | U1–U7 |
| UG-D | Unignorable cancelled/lapsed members | `n` | email ✓ if not unsubscribed | Gift | U2, U4 |
| UG-E | No open or click in 180 days | `n` | — | **Excluded** (protects deliverability) | none |
| Age overlay | Where Unignorable's quiz captured age: **55+** gets "for you" first; **40–54** gets gift first | | | | |
| K9-A | K9SUPPS active subscribers | `n` | email ✓, SMS per audit | "Walk your dog stronger" + gift | K1–K3 |
| K9-B | K9SUPPS one-time buyers ≤ 12 months | `n` | email ✓ | Same | K1–K3 |
| K9-C | K9SUPPS buyers > 12 months / email-only leads | `n` | email ✓ | Gift | K2 |

Why gift-first for Unignorable: the list is women 40+, and many are exactly the adult child (35–55) in ADS.md's AC audience. Their parents are Strong Years' core buyer. The honest line for a 45-year-old is in U1.

### 3.3 Projected conversions (parameter table; every input is a Blitz-sheet assumption)

Inputs: deliverability 92% · open 30% · click-to-open 8% · share of contacts with cleared SMS consent 35% (**0% if the audit doesn't clear it**) · SMS click 6% · warm landing → quiz 85% · quiz → opt-in 60% · warm conversion multiplier 1.5 · arm-B purchase rate 5.18% of opt-ins ($30) · 12% of checkout-ready contacts buy a $49 gift instead · K9SUPPS relevance 0.35 × Unignorable · 10% of founding members refund. Unignorable schedule = 7 emails (weights 1, .8, .7, .6, .6, .5, .5) + 3 SMS (1, .8, .7).

| List | Contacts | SMS cleared? | Opt-ins (30 days) | Founding members | Gifts ($49) | **MRR added by L30** (after refunds) | Gift cash |
|---|---|---|---|---|---|---|---|
| Unignorable | 10,000 | yes | 797 | 54 | 8 | **$1,398** | $411 |
| Unignorable | 20,000 | yes | 1,594 | 109 | 17 | **$2,795** | $822 |
| Unignorable | 50,000 | yes | 3,985 | 272 | 42 | **$6,989** | $2,056 |
| Unignorable | 100,000 | yes | 7,970 | 545 | 84 | **$13,978** | $4,112 |
| Unignorable | 20,000 | **no (email only)** | 1,059 | 72 | 11 | **$1,857** | $546 |
| Unignorable | 100,000 | **no** | 5,293 | 362 | 56 | **$9,283** | $2,731 |
| K9SUPPS (model schedule: 7 email + 3 SMS) | 10,000 | yes | 279 | 19 | 3 | **$490** | $144 |
| K9SUPPS (**this kit: 3 email + 1 SMS**) | 10,000 | yes | 128 | 9 | 1 | **$225** | $66 |
| K9SUPPS (this kit) | 50,000 | yes | 641 | 44 | 7 | **$1,123** | $331 |

Reading it:
- At the placeholder sizes (20K + 10K), warm lists add about **$3K of MRR by L30**. That's a week-1 accelerant, as BLITZ.md §4 says.
- K9SUPPS gets 3 emails, not 7, because the relevance is low and the list is a supplement-subscription asset worth protecting. That costs about 10 members per 10K contacts.
- **Blitz_Plan's note is now corrected** (it said "≈ +$2–3K MRR per 10K in week 1"): the Blitz engine's own output is about **$1.4K of MRR per 10K Unignorable contacts by day 30** (≈ $0.8K by day 7; about $0.9K by day 30 without SMS; ≈ $1.2K if the $25 default price holds). BLITZ.md §4 states the assumptions. Plan on this number.

### 3.4 Unignorable kit: "for you" and "for your parents"

Landing pages: `/start?v=w` (the women's strength variant of `/start`: Sun Yoon-led hero, same offer, no condition words) and `/gift`. Every email ends with the Unignorable footer: unsubscribe, postal address, and *"Strong Years is a separate membership from Unignorable, made by the same team. Chang Yin and Sun Yoon are AI characters."*

**U1 · L1 09:00 · "for you" (UG-B, UG-C, 55+ overlay first)**
**From:** Unignorable · **Subject:** Strength is the other half · **Preheader:** From our team: something new, and honest about who it's for.

> This is Unignorable. We're writing because our team just launched something new, and some of you asked for exactly this.
>
> It's called **Strong Years**. It's about muscle: 8 to 12 minutes of strength, balance and mobility a day, with a chair version of everything. Strength drops faster than muscle size as we age, and it's one of the most trainable things there is at any age.
>
> It's coached by two AI characters we created: Chang Yin, a 74-year-old retired welder who lifts in his garage, and his wife **Sun Yoon**, 76, who makes the recipes and won't let anybody get away with anything. They're not real people, and they say so everywhere. The exercises are real and built on published guidelines.
>
> Who it's for, honestly: it's built for people 55 and up. If you're in your 40s and already lifting, it may feel gentle, and it might be perfect for your mom (more on that Wednesday).
>
> The first 5,000 members are founding members. The price is locked for as long as you stay subscribed, you're charged today, there's a 14-day money-back guarantee, and you can cancel online in two screens.
>
> **[See Strong Years]** → `{{DOMAIN}}/start?v=w&utm_source=ug&utm_medium=owned_xbrand&utm_campaign=u1`
>
> The Unignorable team

**U2 · L3 09:00 · "for your parents" (all UG segments)**
**From:** Unignorable · **Subject:** The gift your mom will actually use · **Preheader:** Prepaid. Never auto-renews. A card from Sun Yoon.

> This is Unignorable, with one idea for your mom or dad.
>
> Our team's new membership, **Strong Years**, gives them a new 8-minute session every morning with a chair version of everything, a strength test every month, and simple high-protein recipes every Sunday. Big buttons, big captions, works on the TV.
>
> **Give 3 months for $49, or a year for $119.** Prepaid. It never renews automatically. They get a welcome card from Sun Yoon, one of the AI characters who coach it. If they agree, you get a short monthly note like "Mom did 18 sessions."
>
> Want to try it together first? On your next call, do the free 3-minute Strength Age test with them: **[Do the test together]** → `/q/a?mode=helper&utm_source=ug&utm_campaign=u2`
>
> **[Give Strong Years]** → `/gift?utm_source=ug&utm_medium=owned_xbrand&utm_campaign=u2`
>
> The Unignorable team

**U3 · L6 09:00 · "for you", recipe-led (UG-B, UG-C)**
**From:** Unignorable · **Subject:** 30 grams of protein at breakfast, the Sun Yoon way

> This is Unignorable, sharing a recipe from our team's new membership.
>
> Sun Yoon (an AI character, and very sure of herself) says toast is not breakfast. Her version: two eggs scrambled soft with scallions, a bowl of warm rice, kimchi on the side, and a glass of milk or soy milk. That's roughly 25–30 grams of protein, the per-meal target research suggests for older adults. Watching sodium? Small portion of kimchi, or rinse it.
>
> Every Sunday, Strong Years members get three recipes like this, a printable grocery list, and one "kitchen remedy" with an honest grade: good evidence, some evidence, or tradition only.
>
> **[See the recipes and the daily sessions]** → `/start?v=w&utm_campaign=u3`
>
> {{COUNT_LINE}}
> The Unignorable team

**U4 · L9 09:00 · gift (UG-A, UG-C, UG-D)**
**From:** Unignorable · **Subject:** "Mom did 18 sessions"

> This is Unignorable. One more note about the gift, because a lot of you asked how it works.
>
> When you give Strong Years, your parent gets their own account and their own level. If they agree to share, you get one email a month: how many sessions they did, and their Strength Age trend. Nothing private and nothing medical, and they can switch it off anytime.
>
> 3 months $49 or 12 months $119, prepaid, never auto-renews. Printed cards from Sun Yoon can be mailed.
>
> **[Give Strong Years]** → `/gift?utm_campaign=u4`
> The Unignorable team

**U5 · L13 · re-send of U1 to non-openers** · Subject: "The 8-minute habit our team built" · same body.
**U6 · L20 · counter update (UG-A, UG-B, UG-C)** · Subject: "{{COUNT}} founding members so far" · Body: one paragraph with the real count and aggregate sessions ("Members did {{SESSIONS}} sessions last week"), the link to `/start?v=w`, and the gift line.
**U7 · L27 · early holiday gift (all UG except UG-E)** · Subject: "Holiday gift, sorted in 2 minutes" · Body: U2's gift offer + "Printed cards ordered by December 12 arrive before the holidays" (**set the real cut-off with the print vendor**).

**Unignorable SMS (cleared numbers only)**
- **U-S1 · L2 12:00 local:** `Unignorable: our team launched Strong Years, 8-min daily strength sessions built for 55+. {{DOMAIN}}/start?v=w Reply STOP to opt out.`
- **U-S2 · L8 12:00 local:** `Unignorable: gift idea for Mom or Dad: 3 months of Strong Years, $49, never auto-renews. {{DOMAIN}}/gift Reply STOP to opt out.`
- **U-S3 · L14 12:00 local (only if the count is ≥ 1,000; otherwise "founding membership is open to the first 5,000"):** `Unignorable: Strong Years founding seats are {{COUNT}}/5,000 taken. Price locked while subscribed. {{DOMAIN}}/start?v=w Reply STOP to opt out.`

### 3.5 Cross-sell inside Unignorable's post-purchase flow

Placement 1: the **final thank-you page**, after the OTO stack and the MRR-tier decision, below the access instructions. It never appears before or between OTOs (it mustn't compete with Unignorable's own offers).
Placement 2: a P.S. in the **day-3 post-purchase email** (after the audit report is delivered).

**Block copy (thank-you page)**
> **One more thing, from our team: a gift for your parents.**
> Strong Years is our new membership for people 55 and up: a new 8-minute strength and balance session every morning, with a chair version of everything, coached by two AI characters, Chang Yin and Sun Yoon. Give 3 months for $49 or a year for $119, prepaid, never renews. **[Give Strong Years]**
> Are you 55 or older yourself? Founding members lock their price while they stay subscribed. **[See the founding membership]**
> *Strong Years is a separate membership from Unignorable, billed as STRONGYEARS MEMBER.*

**Rules:** no one-click charge to the Unignorable card (a different descriptor on the statement causes disputes). A normal Strong Years checkout with its own terms box and consent box. No email prefill unless Unignorable's privacy policy discloses sharing with affiliated brands. `utm_source=ug_typ`.

**P.S. for the day-3 email:** "P.S. If your mom or dad keeps saying they should 'do some exercises', our team built them a membership: Strong Years, 8 minutes a day, chair-friendly. Gift it for $49 for 3 months, no auto-renew: {{DOMAIN}}/gift?utm_source=ug_d3"

### 3.6 K9SUPPS kit: "walk your dog stronger" (plus gifts to parents)

Landing: `{{DOMAIN}}/start?v=walk`, a `/start` variant that leads with the *Walk Stronger* 12-week program (it's in the membership, OFFER §1.2) and dog-walk framing. No claims about dog health.

**K1 · L1 09:00 · (K9-A, K9-B)**
**From:** K9SUPPS · **Subject:** Your dog walks you. Let's make it count. · **Preheader:** 8 minutes a day, and a better walk.

> This is K9SUPPS. Our team just launched something for the humans on the other end of the leash.
>
> **Strong Years** is a daily 8 to 12 minute strength and balance session with a chair version of everything, built for people 55 and up. Inside is **Walk Stronger**, a 12-week program built around the walk you already take: calf raises at the mailbox, a few sit-to-stands before you clip the leash, one-leg balance while your dog sniffs the same bush for the ninth time.
>
> In research on adults 60 and older, the survival benefit of daily steps levelled off at around 6,000–8,000 steps a day. A dog gets you a long way there. Strong legs make the rest of the walk easier.
>
> The coaches are AI characters our team created, Chang Yin (74) and Sun Yoon (76). They're not real, and they say so. The exercises are real. (We're also working on two more characters with a dog of their own. More when they're ready.)
>
> The first 5,000 members lock their price while subscribed. Charged today, 14-day money-back, cancel online in two screens.
>
> **[See Walk Stronger]** → `{{DOMAIN}}/start?v=walk&utm_source=k9&utm_medium=owned_xbrand&utm_campaign=k1`
>
> The K9SUPPS team

**K2 · L6 09:00 · gift (all K9)**
**From:** K9SUPPS · **Subject:** For the dog lover who raised you

> This is K9SUPPS. If your mom or dad is the reason you love dogs, here's a gift from our team's new membership: **Strong Years**, 8 minutes of strength and balance a day, chair-friendly, with the *Walk Stronger* program inside. 3 months $49 or 12 months $119, prepaid, never auto-renews. **[Give Strong Years]** → `/gift?utm_source=k9&utm_campaign=k2`
> The K9SUPPS team

**K3 · L13 09:00 · (K9-A, K9-B openers/clickers of K1 or K2 only)**
**From:** K9SUPPS · **Subject:** The mailbox calf raise

> One move from Walk Stronger: at the mailbox, hold the post or the fence, rise onto your toes, lower for 3 seconds, 10 times. Your dog will wait. Probably. Strong Years has a new session like this every morning. {{COUNT_LINE}} **[Start walking stronger]** → `/walk?utm_campaign=k3`
> The K9SUPPS team

**K-S1 · L2 12:00 local (cleared numbers only):** `K9SUPPS: our team launched Strong Years, daily 8-min strength for 55+, with a dog-walk program inside. {{DOMAIN}}/start?v=walk Reply STOP to opt out.`

(Evidence: E22 daily steps, E11/E12 legs and balance. Hank & Biscuit is ARCHETYPES.md #2, launching around day 45. Only mention the characters by name once their page exists.)

---

## 4. Paid shoutouts and partnerships

BLITZ.md lever 1: 4 posts a day from L3 is worth **+$28.5K of day-30 MRR**, and it's the cheapest channel in the model (about **$59 of media per founding purchase** at $600 per post, 120K views, 0.6% link clicks). It's also unbenchmarked. Its limit is supply: about 25–30 distinct pages rotating, each posting no more than once a week.

### 4.1 Target profile

| Category | Why it fits | Format we buy | Where to find them |
|---|---|---|---|
| **Nostalgia pages** (1950s–70s music, classic TV, classic cars, "remember when") | Huge 55–75 Facebook reach, high share rates, cheap per view. Chang's 1960s garage and Sun's lunch-counter story fit the tone. | Native video post or link post with our clip | Facebook search, Page transparency, Meta Ad Library (to see who already sells posts) |
| **Grandparenting pages** (grandparent humor, "grandma life") | The core buyer, plus family sharing | Video post (F08 couple sketch cut) | Facebook search, IG hashtags |
| **Women 55+ lifestyle** (pages, newsletters, podcasts) | Yang Mun's core audience (women 55–75) | Video post; newsletter sponsor slot; host-read podcast | IG/FB search, beehiiv Ad Network, Paved, Passionfroot |
| **Retirement lifestyle** (retiree travel, RV, retirement-money newsletters) | Active 60–75, higher income, fits the gift angle | Newsletter sponsor slot; FB post | Paved, beehiiv, Swapstack-style marketplaces, direct |
| **Home cooking** (comfort food, "cooking for two", Asian home cooking) | Sun Yoon's lane | Recipe video post (F31 cut) | Facebook/IG search |
| **Gardening, quilting, crafts** | Very large older-female audiences | Link post | Facebook search |
| **Dog lovers 55+** | Walk Stronger + gift | Video post | Facebook search |
| **Senior fitness creators** (chair yoga, walking, tai chi) | Credible but often competitors | **Affiliate (§5), not shoutout** | IG/YouTube |
| **Excluded:** religious/devotional pages, political pages, "miracle cure" health pages, rage-bait "boomer vs millennial" pages, pages with name-change histories | Brand safety; the non-religious positioning (CHARACTERS §2) | — | — |

### 4.2 Sourcing workflow (VA2; the Partner sheet is the single source of truth)
- **D−10 to L10:** 30 new candidates and 30 outreaches a day until **30 active, vetted pages** are on rotation. After that, 10 a day to replace dropped pages.
- Columns: page URL · followers · category · admin contact · Page transparency (created, name changes, manager countries) · insights screenshots received (Y/N) · 55+ share · US share · median reach of the last 10 posts · quoted price · effective CPM (price ÷ median reach × 1,000) · vetting pass (Y/N) · booked dates · results per post (§4.8).

### 4.3 Vetting checklist (every item must pass)
1. **Audience:** a Page Insights / Professional Dashboard screenshot shows **≥ 60% of the audience aged 55+** and **≥ 70% US**.
2. **Reach:** a screenshot of reach for the **last 10 posts**. We price on the **median**, not the follower count.
3. **Authenticity:** no follower spikes; comments from real-looking accounts; engagement 0.5–5%; no engagement-pod patterns.
4. **History:** Page transparency shows **no name change in 12 months**, the page is ≥ 2 years old, and the managers' countries are disclosed.
5. **Content scan (last 60 days):** no health misinformation or miracle cures, no political rage content, no AI people presented as real, nothing adult, no gambling or crypto.
6. **Mechanics:** agrees to run it as a **Partnership Ad / Paid Partnership**. Meta has required branded creator content to run through Partnership Ads since spring 2026 ([ContentGrip](https://www.contentgrip.com/meta-branded-content-rules-update/)); the label alone doesn't satisfy the FTC, so in-caption `#ad` is required too. Also agrees to post our exact copy with the AI disclosure, keep the post up ≥ 30 days, and send 24h and 72h insights screenshots.
7. **Business:** W-9 (US) or W-8BEN, an invoice, ACH or PayPal, one point of contact.
8. **Not a competitor** selling its own 55+ fitness subscription.
9. **A test post first** before any multi-post package.

### 4.4 Pricing benchmarks and our buy rule

| Market data | Benchmark | Source |
|---|---|---|
| Facebook sponsored posts | micro $250–1,250 per post; mega ~$25,000 per post | [Meltwater 2026](https://www.meltwater.com/en/blog/influencer-marketing-costs-rates-pricing) |
| Facebook page rate cards | $5–75 per 1,000 page likes; 500K–1M likes $7,500–15,000 per post; 1M+ $15,000+ | [SocialRails calculator](https://socialrails.com/free-tools/facebook-sponsored-post-rate-calculator) |
| Newsletters | Consumer $15–35 CPM; 5K–50K subscribers $500–3,000 per placement; 50K+ $3,000–20,000+ | [beehiiv](https://www.beehiiv.com/blog/newsletter-sponsorship-cost) |
| Newsletters (new publishers) | 2.5–5% of subscriber count per placement | [Paved](https://www.paved.com/blog/newsletter-sponsorship-rates/) |
| Podcasts | Pre-recorded $15–30 CPM; host-read $25–40 CPM | [Acast](https://www.acast.com/en/news-and-insights/how-much-does-podcast-advertising-cost) |

**Honest read:** the model's $600 for 120K views ($5 effective CPM) is at the **bottom** of the market. Rate cards for big pages are 10–25× higher. Many large nostalgia and hobby pages sell link posts far below their rate cards [A], and that's the supply we need. **We buy on verified median reach, never on followers.**

**Buy rule** (from Blitz_Plan: rebook at ≤ $60 per paying member, drop at > $90). The funnel math per 1,000 views: 0.6% clicks → 65% quiz start → 42% opt-in → 5.18% purchase ≈ **0.085 purchases per 1,000 views**.

| Channel | Target (≤ $60 per purchase) | Ceiling (≤ $90) | Walk away |
|---|---|---|---|
| Facebook/IG post, on verified median reach | **≤ $5.10 per 1,000 views** (≈ $610 for 120K) | **≤ $7.65 per 1,000** (≈ $920 for 120K) | above the ceiling |
| Newsletter (assumes 2% click-through of sends [A]) | ≤ $17 CPM on sends | ≤ $25 CPM | above; test once at ≤ $500 first |
| Podcast (host-read, vanity URL `{{DOMAIN}}/radio`) | test only, ≤ $20 CPM, 1–2 shows | — | if < 0.05 purchases per 1,000 downloads |

### 4.5 Outreach templates (VA2 sends; G approves changes)

**A. First contact (email, or Page DM if no email is listed)**
> Subject: Paid post for {Page name}: 55+ strength program
>
> Hi {first name},
>
> I run partnerships for Strong Years, a daily 8-minute strength and balance program for people 55+. Your page's audience looks like a great fit, and we'd like to pay for a post.
>
> What we'd send: a 30–45 second video of Chang Yin, an openly AI character (a 74-year-old retired welder who lifts in his garage), doing a one-chair strength test, plus a short caption. It's labeled as a paid partnership and as AI.
>
> To quote, could you send screenshots of (1) your audience age and country breakdown and (2) reach on your last 10 posts? We pay on reach, and we pay quickly: within 7 days of the post going live, by ACH or PayPal.
>
> Thanks,
> {name}, Strong Years partnerships · {phone}

**B. Follow-up (+48h)**
> Hi {first name}, following up on a paid post for {Page name}. If it's easier, a screenshot of your last 10 posts' reach is all we need to quote. {name}

**C. Counter-offer (the price is above our rule)**
> Thanks for the numbers. Your median reach over the last 10 posts is {median}. We pay about ${rate} per 1,000 views on median reach, which comes to ${offer} for one post. If that works, we'd book a first post on {date} and, if it performs, a weekly slot for the next 4 weeks at the same rate.

**D. Booking confirmation + brief**
> Confirmed: 1 post on {date} at {time ET}, ${price}, paid within 7 days of going live. Attached: the video, the caption (please use it exactly), and the link `{{DOMAIN}}/start?via={slug}`. Please run it with Meta's Paid Partnership label (we'll send the partnership request from our page), keep "#ad" at the start of the caption, and leave the post up for at least 30 days. Screenshots of reach and link clicks at 24h and 72h, please. Agreement attached for e-signature.

**E. Newsletter pitch**
> Subject: Sponsor slot for {Newsletter} (55+ strength program)
> Hi {name}, we'd like to test one sponsor slot. Strong Years is a daily 8-minute strength and balance program for people 55+, coached by openly AI characters and built on published exercise guidelines. Could you share your rate card, list size, average open rate and average sponsor click-through? We'd supply ~80 words + a link, marked "Sponsored".

**F. Podcast pitch**
> Hi {name}, we'd like to test a host-read spot on {show}. Would you share downloads per episode (30-day), the audience age split and your CPM? The host must say it's a paid ad and that our coaches are AI characters. We'll supply talking points and a vanity URL.

### 4.6 Contract terms (one-page insertion order; ATT approves the template on D−4)
1. **Deliverables:** format, date, time window (±2 hours), our supplied asset and caption used **verbatim**. Changes only with our written approval.
2. **Disclosure:** "#ad" at the start of the caption and the Meta **Paid Partnership** label (the platform tool alone isn't enough for the FTC: disclose in the post itself, in terms like "Ad" or "#ad" ([FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers))). The caption keeps the AI line: "Chang Yin is an AI character."
3. **No claims beyond the approved copy.** The page adds no health claims, testimonials or personal-attribute statements ("if you have bad knees…"), and doesn't reply to comments with medical advice. The page admin forwards questions to our link.
4. **Duration:** the post stays live and unedited for ≥ 30 days.
5. **Reporting:** screenshots of reach, views and link clicks at 24h and 72h. We track purchases ourselves.
6. **Make-good:** if 72h reach is < 60% of the page's stated median, one make-good post at no charge, or 50% refund, at our choice.
7. **Payment:** 100% within 7 days of the live post and the 24h screenshot. W-9/W-8 before payment. (1099-NEC is required for payments made in 2026 and later only at **$2,000+** a year ([OnPay](https://onpay.com/insights/1099-reporting-threshold-updates/)).)
8. **Partnership Ads permission (optional):** the page grants partnership-ad access for 30–60 days so we can put spend behind the post. A flat fee is agreed up front ($100–300 [A]).
9. **Exclusivity:** no competing 55+ fitness or supplement offer within 48 hours of our post.
10. **Conduct / termination:** we can cancel before posting for any content-safety reason with a full refund. The page warrants that the audience isn't bought or botted.
11. **Compliance:** both parties follow the FTC Endorsement Guides and platform rules. The page indemnifies for its own added content. We indemnify for our supplied content.

### 4.7 Creative we supply (price-free; the landing page carries the terms)
- **Video:** a 30–45s Chang or Sun clip (F02 "Can you do this?", F31 recipe, F08 couple sketch) with the AI tag burned in and the end card "Free 3-minute Strength Age test".
- **Caption (nostalgia/hobby pages):** "#ad Paid partnership with Strong Years. Remember when getting up off the floor was nothing? Chang Yin (an AI character; the exercise is real) shows the one-chair test used in senior-fitness research. Try it free in 3 minutes: {{DOMAIN}}/start?via={slug}"
- **Caption (women 55+ pages):** "#ad Paid partnership with Strong Years. Sun Yoon is an AI character and she has opinions about your breakfast. The 3-minute Strength Age test is free: {{DOMAIN}}/start?via={slug}"
- **Newsletter (80 words):** "**Sponsored: Strong Years.** One chair, thirty seconds: the chair-stand test is one of the standard fitness tests used in senior-fitness research. Strong Years turns it into a daily 8-minute practice, with a chair version of everything and a retest every month so you see progress in numbers. It's coached by two openly AI characters, Chang Yin and Sun Yoon, and built on published exercise guidelines. Take the free 3-minute Strength Age test: {{DOMAIN}}/start?via={slug}"

### 4.8 Tracking, rebooking and rotation
- Every post gets a unique path `{{DOMAIN}}/start?via={page-slug}-{mmdd}`, which carries `utm_source=shoutout&utm_medium=paid_social&utm_campaign={slug}`. The ledger (the Partner sheet → Supabase `shoutouts` table) records cost, 72h reach, our server-side clicks, opt-ins, purchases, refunds and **cost per purchase at 7 days**.
- **Rebook** weekly if cost per purchase ≤ $60. **Hold** (one more post at a renegotiated price) at $60–90. **Drop** above $90 (Blitz_Plan). Rotation: no page more than once a week. That's why 4 posts a day needs 25–30 pages.
- If fewer than 4 posts a day are bookable by L6, G shifts the gap's budget (~$600 per missing post) to Meta at the current marginal cost per purchase. The dashboard shows the resulting drop in the projection.

---

## 5. PT / coach / senior-center affiliate program

### 5.1 Commission design: **30% recurring for 12 months (default); 40% for 12 months is a client-decision option**

The math at $30 founding ($28.50 realized). Arm-B survival (Blitz: renewal curve 62/50/43/38.5/35% × 0.935, then 5% a month) gives about **4.8 paid months in the first 12**.

| Plan | Commission per referred member (12 months) | Compare |
|---|---|---|
| **30% × 12 months (default; the Blitz model's input, Blitz!B51)** | **~$41** | Meta ≈ $107–123 of media per founding purchase (model, L1–L14). Shoutouts ≈ $59. |
| 40% × 12 months (client option) | ~$55 | Still under half of Meta's cost, and paid **only out of cash collected**, after the refund window |
| Gift sales | 20% one-time ($9.80 / $23.80) | — |

**The case for the 40% option (client decision):** the model adds affiliates at only 3 a day (cap 120), and they barely move day-30 MRR (+$0.5K, BLITZ.md §5). The bottleneck is recruiting speed, not margin. A higher founding-partner rate may recruit faster, and even at 40% each referred member costs the business less than any paid channel. Referred members also convert about 2× better (Blitz input). If the client chooses it, offer 40% to the first 100 approved partners only and 30% after that (or from L60). Until then, every script and the partner agreement say 30%.

Terms: commissions accrue on **collected, non-refunded** membership revenue. They pay monthly on the 15th for charges older than 30 days (past the 14-day guarantee plus a chargeback buffer). Refunds and chargebacks claw back. $50 minimum payout. No commission on self-referrals or on the partner's own household.

### 5.2 Tooling

| Tool | Price (monthly) | Fits because | Watch-outs |
|---|---|---|---|
| **FirstPromoter** (recommended) | $49 up to $5K/mo of affiliate revenue; $99 up to $15K; $149 above ([pricing](https://firstpromoter.com/pricing)) | Integrates with **Stripe and Braintree** (our two processors). Recurring and lifetime commissions. **W-9/W-8BEN collection**. Fraud controls (self-referral detection, paid-ad traffic policy). Coupons synced to Stripe. | Confirm the Braintree integration works with our checkout during the D−7 install |
| Rewardful | $49 up to $7.5K; $99 up to $15K; $149+ up to $30K; 0% transaction fees ([pricing](https://www.rewardful.com/pricing)) | Clean two-way Stripe sync, PayPal/Wise payouts, coupon tracking | Stripe-centric: the Braintree share would go untracked. Tax forms aren't listed on the pricing page. |
| Tolt | $69 up to $10K; $99 up to $20K (auto payouts at a 2% fee, W-9 + 1099 filing); $199 up to $50K ([pricing](https://tolt.com/pricing)) | 1099 filing built in | 2% payout fee. Stripe-first. |

Setup (DEV, D−7): the snippet on every page, a `via` parameter persisted into Stripe/Braintree metadata, the conversion posted on the **first successful founding charge**, and refunds pushed back through webhooks. Tracking links look like `{{DOMAIN}}/start?via={slug}` (partner vanity) or `?via={code}`. Cookie window 60 days.

### 5.3 Who to recruit, where, and how many

| Segment | Why they convert | Where to find them | Special rules |
|---|---|---|---|
| Physical therapists / PTAs in private practice (geriatric, balance, Otago-trained) | "Home exercise adherence" is their daily problem | LinkedIn, Google Maps practice listings, IG `#geriatricPT #physicaltherapist` (search only; never in our posts) | HIPAA marketing rule, employer approval (§5.5) |
| Personal trainers who specialize in 55+ | Clients between sessions; a retention tool | IG `#over60fitness #seniorfitness`, NASM/ACE specialist directories | — |
| Tai chi, qigong, chair-yoga and aqua instructors | Classes of exactly our audience | Community-center schedules, YMCA listings, Facebook groups (with the admin's OK) | Never imply endorsement by any named program |
| Occupational therapists, home-care agencies, caregiver coaches | The gift and caregiver angle | LinkedIn, local agency sites | Gift commission focus |
| Senior-living activity directors | Group classes on the TV | LinkedIn, facility websites | **Free community license instead of commission** (below) |
| Senior centers / Area Agency on Aging programs | Trust hubs | Local government sites | **No commission.** Free community license only. |
| Micro-creators for 55+ (IG/YouTube/FB, 5K–100K followers) | Audience trust | Search + Modash/HypeAuditor | Treated as affiliates, with FTC disclosure |

**Quotas:** VA2 plus a part-time recruiter send **100 personalized outreaches a day from L1**. At an assumed 3% outreach → approved partner [A], that's 3 approved a day, matching the model's +3/day toward the cap of 120. Measure the real rate by L7 and adjust the outreach volume.

**Senior centers and nonprofits: the community license.** Free access for group sessions (a TV login, printable class cards, one Wednesday Q&A a month for the group). Individual members may join on their own. **No per-member payment to nonprofits or public agencies.** Paying per sign-up, or advertising "we donate $X per member", can trigger state commercial co-venturer rules and agency gift rules. Counsel reviews it first if ever wanted.

### 5.4 Recruitment scripts

**Email to a PT (private practice)**
> Subject: A daily home program your 60+ patients might actually do
>
> Hi Dr. {last name},
>
> Quick one. Strong Years is a daily 8–12 minute strength, balance and mobility program for people 55+, with a chair version of everything and a monthly retest (30-second chair stand, 4-stage balance, and more) so people see progress in numbers.
>
> The coaches are openly AI characters (a 74-year-old retired welder and his wife). The programming follows published guidance for older adults, and we're adding licensed reviewers [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "and every session is reviewed by [PT NAME], PT, DPT"] FALLBACK: omit the reviewer clause.
>
> Two ways to work with us:
> 1. **Free professional access**, so you can judge it yourself. No obligation.
> 2. If you like it, our **founding partner program**: 30% of membership revenue for 12 months for each member who joins through you, with a clinic poster, handouts and a QR code. (We'll walk you through the HIPAA-safe ways to share it: in person and in public, never from your patient list.)
>
> Want the free login? Reply "yes" and I'll send it.
>
> {name}, Strong Years partnerships · {phone}

**LinkedIn DM (PT/OT)**
> Hi {first name}, I work on Strong Years, a daily 8-minute strength and balance program for 55+ with a monthly retest. We'd like to give you free professional access to judge it; our founding partner program pays 30% for 12 months if you choose to recommend it. Interested in a login?

**IG DM (trainer, instructor, creator)**
> Hi {first name}! Love your chair-yoga posts. We built Strong Years (daily 8-min strength + balance for 55+, coached by openly AI characters). Can we send you free access? If you like it, our founding partners earn 30% recurring for 12 months. No pressure either way.

**Phone (clinic front desk → practice owner)**
> "Hi, this is {name} from Strong Years. We make a daily 8-minute home strength and balance program for people over 55. I'd like to offer the practice owner free professional access to review it. Is there an email I can send it to? … Thank you. It's not a referral arrangement for insured services. It's a consumer membership, and there's an optional partner program."

**Follow-up (+3 days)**
> Hi {first name}, just checking you saw the free access offer for Strong Years. Happy to send a login, a 2-minute walkthrough video, or the evidence notes behind the programming. {name}

**Approval / welcome**
> Welcome aboard, {first name}. Your login: {link}. Your partner link: {{DOMAIN}}/start?via={slug}. Your QR poster and handouts: {kit link}. Before you share: (1) do at least 5 sessions yourself, so your recommendation is genuinely yours; (2) always say you earn a commission; (3) share in person and in public, never from patient records. Questions? Reply here.

### 5.5 Compliance for partners (in the agreement; the attorney approves on D−4)
1. **Disclosure (FTC):** every recommendation says the partner earns a commission, clearly and next to the link ("I earn a commission if you join"). Hashtags like `#ad` or `#affiliate` go in the post itself, not the profile ([FTC Disclosures 101](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers)).
2. **Genuine expert opinion:** professionals recommend only after actually evaluating the program (free access plus **≥ 5 sessions completed**, logged). Expert endorsements must reflect a real evaluation.
3. **Approved claims only:** the partner kit's copy. No "treats", "prevents falls", "fixes back pain", "cures", no outcome promises, no testimonials unless they're real and permissioned through our review system (FUNNEL §7.10).
4. **HIPAA (PTs, OTs and other covered entities):** a communication promoting a third party's product **in exchange for payment** is "marketing" and needs the patient's written authorization. There's an exception for **face-to-face communications** ([HHS marketing guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/marketing/index.html); [45 CFR 164.508](https://www.law.cornell.edu/cfr/text/45/164.508)). **Allowed:** in-person conversation, in-clinic posters and handouts, the partner's public social posts, and their general newsletter if the list wasn't built from patient records. **Not allowed:** emailing or texting patients from clinic records with the partner link.
5. **Insurance and anti-kickback:** Strong Years is a consumer membership, never billed to Medicare, Medicaid or insurance. Partners must not bill it, imply coverage, or tie it to an insured service. Counsel to confirm the federal Anti-Kickback Statute position and **state fee-splitting and PT practice-act rules** (some states require disclosing a financial interest to patients).
6. **Employer approval:** partners employed by hospitals or clinics confirm they have their employer's permission to earn outside compensation.
7. **No paid ads, no brand bidding, no spam:** affiliates don't run Meta/Google ads using our name or characters, don't bid on brand terms, and don't send cold email or texts. Email only to their own opted-in lists, using our template; our suppression list is applied weekly. We can be liable for affiliate emails under CAN-SPAM.
8. **AI disclosure:** whenever a partner shows Chang or Sun, they say they're AI characters.
9. **Taxes:** W-9 before the first payout. 1099-NEC at $2,000+ a year for 2026 payments ([OnPay](https://onpay.com/insights/1099-reporting-threshold-updates/)).
10. **Termination:** immediate for any breach of 1–8. Unpaid commissions on non-compliant referrals are forfeited.

### 5.6 The partner kit (one folder, a link in the welcome email)
1. **"What it is / what it isn't" one-pager for professionals** (large print, black on white): the daily session structure, the 4 levels, the chair versions, the monthly retest, the safety rules (stop rules, the "sore knee / sore back / low energy" button, the pre-exercise screening advice (E43)), the evidence notes (E01, E11, E12, E13, E14, E28), and the AI disclosure.
2. **Free partner membership**, with the "5 sessions" tracker visible in the partner portal.
3. **Tracking link + QR code** (`{{DOMAIN}}/start?via={slug}`), printable.
4. **Clinic poster (11×17), copy:**
   > **8 minutes a day. One chair. Stronger legs.**
   > Strong Years: a daily strength and balance session for people 55+, with a chair version of everything and a monthly retest so you can see your progress.
   > Scan to take the free 3-minute Strength Age test.
   > *[QR]* · *Coached by AI characters. Built on published exercise guidelines. Ask your provider if you have a heart condition, recent surgery, a recent fall or dizziness. {Practice name} earns a commission if you join.*
5. **Handout (half page, 18pt+):** the same copy plus 3 bullets ("new session daily · chair version of everything · cancel online anytime").
6. **30-second talk track (face-to-face):** "Some of my patients like a short daily routine at home. This one's 8 minutes, has a chair version of everything, and retests your chair stand monthly. It's a paid membership, it's coached by AI characters, and I earn a commission if you join, so choose what's right for you. The test is free."
7. **Three social captions:**
   - "I tried Strong Years for two weeks: 8 minutes a day, a chair version of everything, and a retest every month. The coaches are AI characters (they say so), and the exercises follow published guidelines. Free 3-minute test: {link} (I earn a commission if you join.) #ad"
   - "The 30-second chair stand is one of the standard fitness tests used for older adults. Try it: chair against the wall, arms crossed, count your stands. Then see your Strength Age: {link} #ad (commission link)"
   - "Looking for a gift for your parents that they'll actually use? 3 months of Strong Years is $49 and never auto-renews. {link} #ad (I earn a commission.)"
8. **Newsletter blurb (own opted-in list only):** use §4.7's 80 words + "I earn a commission if you join."
9. **Patient/client FAQ:** Is it real? (AI coaches, real exercises) · Is it safe for me? (ask your provider; the stop rules) · Cost and cancelling (charged today, 14-day money-back, cancel online in two screens) · Tech help (reply to any email).
10. **The do-not list** (§5.5 items 3, 4, 7).
11. **Monthly partner report:** clicks, members, active members, commissions (from FirstPromoter).

---

## 6. Paid acquisition war room

### 6.1 Account structure (an existing account only with purchase history and no restricted-health history; otherwise a fresh Strong Years account; never FA)

**How to pick the accounts (G, D−10 10:00).** Score every existing ad account the client controls **except Founder Ascension's** (FA accounts are excluded outright). AA1 must pass all six criteria. If no existing account passes, AA1 is a **fresh ad account under the Strong Years business with a verified domain**, and the Blitz sheet's existing-account flag is set to 0 (about −$7.3K of day-30 MRR, BLITZ.md §5).

| # | Criterion | Why |
|---|---|---|
| 1 | **Purchase history** (purchase-optimized campaigns with real conversions) and ≥ 12 months of spend with no failed payments | Spending limits and trust. New accounts start at a daily cap around €25–100 ([Prime Scale](https://primescalemedia.com/blog/meta-spend-caps-explained)). |
| 2 | No ad disapprovals in the last 90 days, no restrictions ever | Enforcement history carries over |
| 3 | **Has never run condition-associated ads** (TRT, hormones, fertility, peptides, perimenopause symptoms) | Keeps Strong Years clear of health & wellness association. Meta applies that classification to data sources ([Triple Whale](https://www.triplewhale.com/blog/meta-health-and-wellness-brands)), so Strong Years gets its **own new dataset** regardless. |
| 4 | **Not a Founder Ascension account** (any of them) | FA accounts carry TRT/hormone/peptide history, and a Strong Years policy strike must not reach FA's pipeline |
| 5 | Meta's daily spending limit ≥ $15K, or approvable on request by D−2 | $8K/day plus Meta's right to spend up to 75% over the daily budget on a given day ([Jon Loomer](https://www.jonloomer.com/updates-to-meta-ads-budgeting/)) |
| 6 | Sits in a **verified** Business Portfolio | Business verification takes 3–10 working days if it has to be done from scratch |

Likely ranking, to confirm on D−10: **the K9SUPPS account for AA1** (purchase history, no restricted-health ads), provided it passes all six criteria. The next-best qualifying account, or a fresh Strong Years account, for **AA2**. **Unignorable's account is excluded** (perimenopause-condition creative), and so is every FA account.

| Account | Role | Campaigns | Notes |
|---|---|---|---|
| **AA1** | Scale | FOUNDING_ASC, RETARGET | Dataset `SY-Web`. Identity: the @changyin FB Page + IG account (Sun Yoon ads use @sunyoon.kitchen). |
| **AA2** | Test + gift | TEST_ABO, GIFT, the D−4 waitlist seeding | Takes spend if AA1 hits its cap |
| **AA3** | Non-policy backup | RT_BACKUP at $100/day from L1, so it has live Strong Years history | Used **only** for payment failures, spending caps or technical outages. **Never** to keep running ads that were restricted for policy (circumvention can take down the whole portfolio). |

- **Data:** one new dataset `SY-Web` (pixel + CAPI), shared to all three accounts. Domain `{{DOMAIN}}` verified. Events: `Lead`, `StartTrial`, `Purchase`, `Subscribe`, with no custom data beyond the offer code and value (the app enforces this).
- **Payments:** 2 cards on each account, each with ≥ $150K available. The **account spending limit** is set to the D1 cash plan (Meta only, through L30: R4 ≈ $240K; variant ≈ $345K. Shoutouts are paid outside Meta.) VA1 reconciles daily.
- **Roles:** G admin. VA1 "Advertiser" (can't change billing). 2FA on everyone. Two backup admins in the portfolio (ADS.md §4.1).
- **Portfolio risk:** Strong Years' accounts and the `SY-Web` dataset never sit in FA's Business Portfolio. Use the K9SUPPS portfolio if it's verified, or start verifying a separate Strong Years portfolio on D−10 (3–10 working days) and launch in it.

### 6.2 Campaign map on L1 ($3,000/day; the 3-cell launch)

| Campaign | Account | Optimization | Budget L1 | Ads | Setup |
|---|---|---|---|---|---|
| `SY_LAUNCH_ASC` | AA1 | **Purchase** (fires on a founding charge **and** on a $1 trial start; value = the cell's expected contribution, so Meta doesn't favour the larger first charge) | **$1,800** | the 20 strongest of the 40 (all formats), with no price in the creative or cell-matched copy | Advantage+ sales, US, age floor 45 (suggested audience 55+), members excluded via a daily customer-list sync. Lands on `/q/a` (quiz ads) or `/join`, which serves the visitor's cell. |
| `SY_TEST_ABO` | AA2 | **Lead** (quiz opt-in) | **$600** = 3 ad sets × $200 | 5 hook variants per ad set | Broad, one concept per ad set. Winners graduate to ASC on Purchase (§6.5). |
| `SY_GIFT` | AA2 | Purchase (gift) | **$350** | concepts 15–19 (A4) | Age 35–55, broad, lands on `/gift` |
| `SY_RETARGET` | AA1 | Purchase | **$200** | quiz-reminder + result-plan ads | Quiz started, not finished (7 days); quiz done, no purchase (14 days); members excluded |
| `SY_RT_BACKUP` | AA3 | Purchase | **$50** | 3 retargeting ads | Keeps AA3 warm |
| **Total** | | | **$3,000** | | At a green day-10 gate: scale to $4,000 (ASC $2,500, TEST $800, GIFT $450, RETARGET $200, BACKUP $50). At a green day-40 gate: the R4 map ($8,000: ASC $5,100, TEST $1,600, GIFT $800, RETARGET $400, BACKUP $100). |

Naming: `{CAMP}_{AUD}_{C#}_{H#}_{FMT}_{yyyymmdd}` (ADS.md §4.1), plus `FOUNDING` in any ad that mentions the founding offer, so the cap auto-pause can find it.

### 6.3 Day 1–40 spend ramp: the 3-cell launch and the two gates (BLITZ.md §11)

| L-day | Meta/day | Shoutout posts/day | Cells | Decision point |
|---|---|---|---|---|
| L1 | $3,000 | 0 | F25 25% · F30 25% · T25 50% (paid); F25 50% · T25 50% (non-paid) | 12:00 and 18:00 first reads (§6.4 early proxies) |
| L2 | $3,000 | 0 | same | Creative kills on ≥ 150 opt-ins |
| L3 | $3,000 | 1 | same | Event day. 21:00: 72-hour read on arm-B purchase rate vs T25 trial-start rate (the factor) |
| L4 | $3,000 | 2 | same | **09:00 early read** (below). No spend step-up before day 10. |
| L5 | $3,000 | 3 | same | 23:59 PT: provisional $25-vs-$30 call inside the founding cells |
| L6–L9 | $3,000 | 4 | same | Shoutouts at 4/day. T25 cohorts from L1 hit their first $25 charge from L8: trial→paid read starts. |
| **L10** (or when charge-today reaches **≥ 300 purchases**, whichever is later; latest L14) | **Day-10 gate** | | | **Green →** $4,000/day, charge-today stays at 50%. **Red →** charge-today 0%, T25 100%, the R17 plan (Meta ~$1,500/day + 4 shoutouts). |
| L11–L30 | $4,000 (green) or ~$1,500 (red) | 4 | 50/50 (green) or T25 only (red) | L14: $25-vs-$30 confirmed on refund-adjusted data; L25: first renewal reminders to L1 charge-today buyers |
| L31–L40 | same | 4 | same | Renewal 1 of the L1–L10 charge-today cohorts |
| **L40** | **Day-40 gate** | | | **Green →** full R4: $8,000/day, 100% charge-today at the winning price. **Renewal 1 < 50% →** back to R17 (trial), whatever the day-10 lines showed. **50–58% →** hold the day-10 configuration and fix retention. |

**Day-10 gate (G decides; BLITZ.md §11, thresholds 1, 2/2b and 4):**
- (1) Blended paid media per net paying member (at ≥ $4K/day for 5 days, or projected from the $3K/day read) **≤ $111 at $25 / ≤ $132 at $30**.
- (2) Charge-today factor = arm-B purchase rate ÷ T25 trial-start rate (per opt-in, same traffic mix) **≥ 0.64 at $25 / ≥ 0.57 at $30** at central media costs; **(2b) ≥ 0.48 / ≥ 0.43** if live cost per opt-in matches the upside (no Q4 uplift, no click loss).
- (4) 14-day refunds ≤ 12%, 30-day chargebacks < 0.35%.
- Plus the cell comparison: **net revenue per visitor to date** (all revenue net of refunds and chargebacks ÷ visitors assigned) and projected **payback** per cell from the Payback sheet. Charge-today stays only if (1) and (2 or 2b) pass on ≥ 300 charge-today purchases; the net-revenue-per-visitor and payback read explains why and picks the founding price.

**Day-40 gate (G decides; threshold 3):** renewal-1 survival of the L1–L10 charge-today cohorts, read L31–L40, **≥ 58%** → full R4. **< 50%** → R17 whatever (1)–(2) show. In between → hold. T25's trial→paid and renewal 1 are read alongside, so the final choice compares net revenue per visitor and payback for both arms on real renewals.

**L4 early read (no spend change; flags only):** blended cost per paid opt-in (L1–L3) ≤ $5.00 · arm-B purchase ÷ opt-in and T25 trial-start ÷ opt-in both recorded on ≥ 450 paid opt-ins · refunds so far ≤ 8% · checkout error rate < 1% · no processor warnings · chargebacks ≤ 2. **If cost per opt-in > $6.50 or the arm-B purchase rate < 4%**, move the founding share to 25% (T25 75%) until the day-10 gate and fix the funnel.

Cash: the gated plan's cash need is set by the Blitz sheet re-run (D1). For reference, R4 from L1 was −$260K on L30 and ≈ −$460K at its trough (BLITZ.md), and R17 bottoms at ≈ −$369K around day 222 (fixed opex, not media).

### 6.4 Daily kill / scale rules (the ECONOMICS.md $26 / $40 / $58 ladder, translated to every offer arm)

ECONOMICS.md's ladder is **cost per $1 trial start at a $20 price**: scale ≤ $26 (≈ 2.4× the value of a trial start), hold ≤ $40 (≈ 1.6×), kill > $58 (break-even). The value of a trial start = 42% trial→paid × $119 of 24-month contribution + $12.99 front end ≈ $63. The same value ratios applied to each blitz offer:

| Band | Arm A $1 trial @ $20 (ECONOMICS) | Arm A @ $30 | **Arm B founding @ $30** (per gross purchase) | Arm B founding @ $25 |
|---|---|---|---|---|
| Value per start / purchase | $63 | $81 | **$169** | $142 |
| **SCALE** (+20%/day) | **≤ $26** | ≤ $33 | **≤ $70** | ≤ $58 |
| **HOLD** | $26–40 | $33–51 | **$70–108** | $58–90 |
| **KILL** (pause the ad) | **> $58** | > $74 | **> $155** | > $130 |

How the arm-B values are built: 24-month contribution at the price (ECONOMICS price table: $183 at $30, $151 at $25) × 0.90 (14-day refunds) × 0.95 (arm-B renewal factor, 0.935 on the curve) + bumps/upsells/front ends $12.49 per purchase. Kill at $30 ≈ break-even. It sits close to ECONOMICS' own $30 break-even of $75.20 per trial ÷ 37% trial→paid, less front-end credit.

**Where the model's base case sits:** Meta ≈ $107–123 of media per founding purchase (L1–L14) = **HOLD**, near its upper edge. Blended (with shoutouts, warm and organic) ≈ $80–93 per net member = **HOLD**. SCALE on Meta means you're beating the model.

**Ad-level rules** (VA1 compiles at 09:30, G acts at 10:00; backend numbers only):
1. **Early proxy (first 150 opt-ins or $1,000 per creative):** cost per opt-in ≤ $5.00 → eligible to graduate; $5.00–6.50 → hold; **> $6.50 → pause**. Purchase ÷ opt-in < 4% after 150 opt-ins → pause (Blitz_Plan days 1–3).
2. **Purchase-level (≥ 8 purchases or ≥ $1,000 spend):** apply the ladder above.
3. **Fast kill:** spend ≥ one kill threshold ($155 at $30) with **0 purchases** → pause.
4. **Quality kills (regardless of cost):** refund rate by ad > 10% after 20 purchases (it's over-promising). Negative feedback visibly above the account norm. A comment section filling with "is this real?" anger → pull the ad and check the AI tag.
5. **Graduate TEST → ASC:** ≥ 30 opt-ins at ≤ $5.00 **and** backend purchase ÷ opt-in ≥ 5.5%. Use the same post ID to keep the social proof.
6. **Fatigue:** 7-day frequency > 3.5, or CTR down 30% from its peak → refresh the hook. HOLD-band cost for 5 days despite refreshes → retire (ADS.md §5.4).

**Campaign/account-level rules (Blitz_Plan, verbatim thresholds):**

| Window | Metric | Scale | Hold | Cut |
|---|---|---|---|---|
| L1–L3 | Cost per paid opt-in; arm-B purchase ÷ opt-in; T25 trial start ÷ opt-in | ≤ $5.00 and ≥ 5.5% | $5.00–6.50 or 4–5.5% | > $6.50 or < 4% after 150 opt-ins: pause the creative; if all fail, founding share to 25% (T25 75%) until the day-10 gate |
| L1–L14 | $25 vs $30 inside the founding cells: net revenue per visitor | winner by ≥ 15% on ≥ 300 founding purchases → all founding traffic to it (L14 confirms) | within 15%: keep the split | — |
| L10 / L40 | Charge-today vs T25: the day-10 and day-40 gates (§6.3) | green | — | red → T25 100% (R17) |
| L4–L14 | Media ÷ net new paying members (blended) | ≤ $95 | L4–L7: $95–125 · L8–L14: $95–110 | L4–L7 > $125 or L8–L14 > $110 two days running → −30% spend (AUDIT F02: the old > $95 cut fired on the model's own base case of $114 on L4 and $109 on L5) |
| L7–L14 | 14-day refund requests | ≤ 8% | 8–12% | > 12% → stop scaling; fix the promise–delivery gap |
| Daily | 30-day chargeback ratio / count (combined book) | < 0.35% and < 50 | 0.35–0.5% or 50–75 | ≥ 0.5% or ≥ 75 → stop scaling |
| Daily | Processor capacity / reserve | within approved volume, reserve ≤ 10% | — | at capacity → route to processor 2 **within its approval** before adding spend |
| L3–L30 | Shoutout cost per paying member | ≤ $60 → rebook | $60–90 | > $90 → drop the page |
| L14–L30 | First-session completion within 24h | ≥ 70% | 60–70% | < 60% → stop scaling |
| L31–L40 | Arm-B renewal 1 (day-40 gate) | ≥ 58% → R4 | 50–58% → hold | < 50% → R17 (trial only) |
| Always | Cash headroom vs the D1 cap | > 30% | 10–30% | < 10% → cut Meta to where day-0 cash covers media |

**Change discipline:** one budget change per campaign per day, at 10:00. Increases ≤ 20%. Bigger jumps go through a duplicate ASC with a different creative mix (horizontal scaling, ADS.md §5.4). The kill switch (pausing an ad) is always allowed.

### 6.5 The learning-phase plan

Meta needs about **50 optimization events per ad set per week** to leave learning. Budget changes over 20–25%, a new optimization event, targeting changes and adding or removing ads can reset it ([AdLibrary](https://adlibrary.com/posts/meta-ads-learning-phase-50-events-guide)).

| Campaign | Events per day at L1 budget | Expected exit | Plan |
|---|---|---|---|
| LAUNCH_ASC (Purchase, both cells; value = each cell's expected contribution) | $1,800 ÷ ~$60–120 per purchase or trial start ≈ **15–30 events/day** | ~day 3–4 | No edits for 72 hours except pausing ads. New ads join in **batches of ≤ 5 on Mon and Thu at 10:00** only. |
| TEST_ABO (Lead) | $200 ÷ ~$6.36 ≈ **31 opt-ins/day per ad set** | ~day 2 | Optimizes Lead because Purchase would need ~$765/day per ad set to reach 50 a week. Downstream quality is judged on backend purchase rate per ad (UTM ad ID). |
| GIFT (Purchase) | $350 ÷ ≤ $35 target ≈ 10/day | ~week 1 | Kill at > $50 gift CPA (ADS.md §5.2) |
| RETARGET / RT_BACKUP | < 50 a week | stays "learning limited" | Accepted; small budgets |

- Meta's built-in **creative testing** tool (2–5 test ads inside an existing campaign, ≤ 20% of budget recommended, Highest Volume bidding only ([Jon Loomer](https://www.jonloomer.com/meta-creative-testing/))) can run inside ASC from week 2 as a second route alongside TEST_ABO.
- **If Events Manager shows a health & wellness restriction on `SY-Web`:** switch ASC to Lead optimization with a cost cap, keep judging on backend purchases (ADS.md §4.1 fallback), and have DEV audit every URL and event for condition words the same day.

### 6.6 Creative production cadence: 5 new ads a day

| Time (ET) | Owner | Step |
|---|---|---|
| 07:30 | CL | Pull yesterday's ad ranks (§6.4) + the top 20 comments and DM objections → brief today's 5: **3 iterations** (new hooks on the top 2 concepts, from the ADS.md hook bank), **1 new concept** (the next unused of ADS.md's 25), **1 format swap** (a static or carousel version of a winner) |
| 08:00–12:00 | pipeline | n8n: script → compliance (two-pass) → keyframes → exercise motion from **driving videos only** → voice → lip-sync → assemble with the AI tag in the first 3 seconds → QA |
| 12:00–13:00 | VA1 → CL → G | ADS.md §7 pre-launch checklist. CL approves. **G approves any new claim, angle or number.** |
| 13:00–14:00 | VA1 | Upload to TEST_ABO (AA2), named per convention |
| Mon/Thu 10:00 | G | Graduate up to 5 winners into ASC |

- Weekly mix (35 ads): 40% Chang test/demo UGC · 20% Sun Yoon kitchen/candor · 15% quiz-first · 15% gift/adult child · 10% static/carousel.
- Volume: 40 on L1 + 5 a day ≈ **185 ads by L30**, with 20–30 live in ASC at any time. Cost: premium render ~$13.67 per video (PIPELINE.md §4.1), about $70 a day.
- Hard rule: no exercise is shown in an ad unless its motion came from a PERF driving video and was checked. Where AI renders a joint wrong, composite the real demonstrator (ADS.md §6).

### 6.7 Budget pacing across the two processors (within approvals; never to hide disputes)

Volume from the Blitz engine (R4): **month 1 ≈ $145K gross** (~4,300 card transactions, ~11 chargebacks), **month 2 ≈ $166K**, **month 3 ≈ $203K**. Assume the variant runs 20–30% higher [A].

| Rule | Detail |
|---|---|
| Ask for enough | Stripe: pre-approval for ≥ $250K/month (D−10 ticket). Braintree: ≥ $150K/month. Both are told the other exists, and why. |
| L1–L13 | 100% Stripe (cards, Apple Pay, Google Pay). The PayPal button stays hidden until Braintree is approved. |
| From Braintree go-live (target L14) | PayPal wallet → Braintree (the customer's choice). New **card** checkouts split by weighted random, starting 75% Stripe / 25% Braintree, tuned so each processor's projected 30-day volume stays **≤ 80% of its approved monthly volume**. |
| Renewals | Stay on the processor that holds the payment method. No card migration without the customer re-entering the card or a PCI-compliant transfer both processors agree to. |
| Daily ceiling | Per processor: approved monthly ÷ 30 × 1.3. If the 7-day average passes 80% of approved ÷ 30, email the underwriter a volume update **7–10 days before** crossing, with refund and chargeback stats. |
| Launch notices | Tell both processors the launch date, the L3 event and any variant decision **before** they happen. Surprise spikes are a leading trigger for holds ([terms.law](https://terms.law/FAQ/payment-processors/stripe-holds-faq.html)). |
| Disputes | Chargeback ratio and count are tracked **per processor and combined**, and the §6.4 thresholds apply to the combined book. Routing is never changed in response to a processor's dispute ratio. Doing that to stay under monitoring thresholds is treated as fraud against the acquirer ([Merchant Alternatives](https://merchantalternatives.com/glossary/load-balancing/)). |
| Reserves | Counted as unavailable cash (model: $14.5K held on L30 at 10%). Never counted as runway. |
| Visa VAMP | Visa now combines fraud reports and disputes into one ratio, so a renewal that draws both counts twice. Acquirers act before the 1.5% merchant line ([SeamlessChex](https://www.seamlesschex.com/blog/visa-s-october-2026-rules-and-your-recurring-billing-mid)). Our internal stop is 0.5%. |

### 6.8 The chargeback prevention stack

| Layer | Setting | Cost | Owner |
|---|---|---|---|
| Descriptor | `STRONGYEARS MEMBER` + support URL and phone. The same name on the receipt, the welcome email and the renewal reminders. | — | DEV |
| Terms + consent | Terms box above the pay button, separate unticked consent, consent log (FUNNEL §5.1) | — | DEV |
| Receipts | Instant email: amount, what it's for, "appears as STRONGYEARS MEMBER", renewal date, a cancel link | — | DEV |
| **Pre-bill reminders** | Arm A: 48h before the trial converts (email, + SMS when live). **Arm B: before every renewal (7 and 2 days before the first, 3 days before each later one).** Annual: 30 days before. **California annual reminder** every 12 months to every auto-renewing member. Price change: exactly 30 days' notice. | ~$0.01 each | DEV |
| Easy exit | Cancel in ≤ 2 screens, reply "cancel" by email, self-serve refund ≤ 14 days (one per person), "text CANCEL" once SMS is live, refund-first SOP (§8.4) | refunds | SUP |
| **Order Insight + CE 3.0** (Visa) | Lookups included. CE 3.0 blocks $15 each. **Pass IP, email and product description on every charge** so prior-transaction evidence can block disputes ([Stripe docs](https://docs.stripe.com/disputes/get-started/prevention)) | $15 per block | DEV |
| **Visa RDR** | Radar dispute rule: **auto-resolve every Visa dispute on membership, bump and upsell charges ≤ $60, all reason codes.** Resolved disputes don't count toward dispute rates. | **$15 per resolution** ([Stripe pricing](https://stripe.com/pricing)) | G sets, DEV implements |
| **Ethoca alerts** (Mastercard) | Auto-refund every alert ≤ $60. Protects against the Mastercard 100-a-month count. | **$29 per resolution** | same |
| Braintree / PayPal | PayPal disputes answered or refunded within 24h. Evaluate a third-party alert provider for Braintree card disputes before go-live [A]. | varies | SUP / G |
| Radar | Block the highest-risk scores. 3DS when the risk is elevated. Velocity limit: ≥ 3 attempts per card, email or IP in 1 hour → block. | — | DEV |
| Dunning | Smart Retries capped at 4 attempts over 14 days. Card account updater. An "update card" email/SMS with an Apple Pay link. 7 days of grace access. | — | DEV |
| Monitoring | Daily: dispute count and ratio per processor + combined, and RDR/Ethoca resolutions (they're early warnings even though they don't count) | — | VA1 → standup |

Budget: the model expects ~11 chargebacks in month 1. Assume about 3× that many **pre-dispute resolutions** at $15–29 [A]: under $1,000 a month, cheaper than a single monitoring program.

---

## 7. Daily command center

### 7.1 Data plumbing (DEV, D−7 to D−3)

| Source | Into (Supabase) | Refresh |
|---|---|---|
| Stripe + Braintree webhooks | `orders`, `subscriptions`, `refunds`, `disputes`, `early_warnings` | real time |
| Meta Marketing API (ad-level spend, impressions, clicks, CPM, frequency; daily negative feedback) | `ad_spend` | hourly |
| Shoutout ledger (Google Sheet) | `shoutouts` | hourly (n8n) |
| FirstPromoter API | `affiliates`, `referrals`, `commissions` | daily |
| ESP (sends, opens, clicks, unsubscribes; Strong Years + Unignorable/K9SUPPS cross-promo click counts only, **no contact data**) | `email_events` | hourly |
| ManyChat webhooks | `dm_events` | real time |
| App (sessions, completions, retests, chat crisis flags) | `sessions`, `crisis_events` | real time |
| Organic post metrics (PIPELINE W5) | `post_metrics` | every 6h |
| Help desk (tickets, tags, first response) | `tickets` | hourly |

The dashboard is Metabase on Supabase (or Looker Studio). Big numbers, Ink on Paper, **no gray text**, red and green reserved for the thresholds.

### 7.2 KPI dashboard spec

| KPI | Definition | Cuts | Target / threshold source |
|---|---|---|---|
| **MRR** | Σ active paying subscriptions × monthly price × 0.95 realized (annual ÷ 12; gifts excluded; trials excluded until converted) | **by arm (A trial, B $25, B $30)**, by channel (Meta, shoutout, Unignorable, K9SUPPS, affiliate, organic, event), by day | Milestones: $10K by L4, $42.9K L14 (R4) / $50K (variant), $92.8K L30 (R4) / $100K (variant) |
| **New paying members** | Gross = first successful membership charges (arm B) + trial conversions (arm A). Net = gross − full refunds in that cohort to date. | by arm, channel, ad, day | Model daily purchases: 87–133 (R4) |
| **Cost per paying member** | (Meta spend + shoutout cost + accrued affiliate commission) ÷ net new paying members | by channel, campaign, ad; daily and trailing 7 days | §6.4 ladder and blended table |
| Cost per paid opt-in | Meta spend ÷ quiz/founding-page opt-ins attributed to paid | campaign, ad | ≤ $5.00 scale / > $6.50 cut |
| **Arm-B purchase rate** | Founding purchases ÷ opt-ins (72h attribution) | channel, price cell, ad | Model 5.18% cold ($30); scale ≥ 5.5%; cut < 4% |
| **Trial → paid** | Arm-A conversions ÷ trials started ≥ 8 days ago | cohort day, ad | ≥ 42% (paid), ≥ 48% (organic) |
| **Refunds** | Count, $ and % of purchases inside the 14-day window, by reason code (§8.4) | cohort day, ad, channel, cell | ≤ 8% scale / > 12% stop |
| **Chargebacks** | 30-day rolling count and ratio (chargebacks ÷ settled card transactions); RDR/Ethoca resolutions shown separately | per processor + combined | < 0.35% and < 50 / ≥ 0.5% or ≥ 75 stop |
| **First-session completion** | % of new members who finish ≥ 1 session within 24h of purchase | cohort day, channel, device | ≥ 70% / < 60% stop scaling |
| **Shares and DMs per post** | Shares per 1K views; keyword comments per 1K views; DM button taps ÷ keyword comments; DM → opt-in | post, page, format, keyword | CONTENT_SYSTEM §10: shares ≥ 6/1K; keyword ≥ 4/1K; DM tap 55–70% |
| Founding seats | Live counter value; projected cap date at the trailing 3-day rate | — | Auto-close at 5,000 |
| Cash | Cumulative cash (reserve excluded) vs the D1 cap; reserve held; each processor's 30-day volume vs approval | — | Headroom > 30% |
| Renewal 1 | % of each cohort still paying after the first renewal | cohort day, channel, cell | ≥ 58% (arm B) |
| Checkout health | Page → checkout start → purchase; decline rate; JS/API error rate; LCP p75 | device | Errors < 1%; LCP < 2.0s |
| Support load | Tickets per 100 new members; first-response time; tag mix | — | FRT ≤ 2h (L1–L5), ≤ 4h after |
| Crisis flags | Open count, and the age of the oldest | — | 0 open older than 15 min in staffed hours |

### 7.3 Alert thresholds (n8n checks every 15 minutes → Slack; red also pages the owner)

| Alert | Yellow | Red | Owner | First action |
|---|---|---|---|---|
| Checkout error rate (1h) | ≥ 0.5% | ≥ 1% | DEV | Roll back the last deploy; post the status line |
| Payment decline rate (1h) | ≥ 12% | ≥ 20% | DEV + G | Check Radar and the processor status; consider a processor fallback |
| Zero purchases in 60 min, 08:00–22:00 ET | — | trigger | DEV | Synthetic test purchase |
| Cost per paid opt-in (since midnight, ≥ $1K spend) | > $5.50 | > $6.50 | G | §6.4 creative pauses |
| Arm-B purchase ÷ opt-in (trailing 300 opt-ins) | < 5.0% | < 4.0% | G | Check message match; the L4 gate fallback |
| Blended media ÷ net member (2-day) | L4–L7 > $110 · L8–L14 > $100 | L4–L7 > $125 · L8–L14 > $110 | G | −30% spend |
| Refund requests (trailing 7 days) | > 8% | > 12% | G + CL | Stop scaling; read the reason codes |
| Chargebacks (30-day combined) | ≥ 0.35% or ≥ 50 | ≥ 0.5% or ≥ 75 | G | Stop scaling; RDR/Ethoca coverage check |
| Early fraud warnings / alerts (24h) | ≥ 3 | ≥ 8 | DEV | Radar tightening |
| Processor volume vs approval (7-day run rate) | > 70% | > 85% | G | Notify the underwriter; shift new-card share |
| Payout paused / reserve changed | — | any | G | §9.2 R1 plan |
| Ad account or page warning / restriction | any warning | restriction | VA1 → G | §9.2 R3/R5 plan |
| Meta spend > 1.75× the daily budget | — | trigger | VA1 | Check the account spending limit |
| First-session completion (L-day cohort) | < 70% | < 60% | CL + DEV | Onboarding fix; stop scaling |
| Crisis flag unacknowledged | 10 min | 15 min | VA2 / on-call | Protocol §8.3 |
| Founding seats | ≥ 4,500 | ≥ 4,900 | G | Pre-stage post-cap copy; verify the auto-pause |
| Email complaint rate (per send) | ≥ 0.08% | ≥ 0.1% | G | Pause the sequence; check segments |
| Cash headroom vs cap | < 30% | < 10% | G | Cut Meta |

### 7.4 The 15-minute daily standup (08:00 ET, every day L1–L30; G chairs, VA1 keeps time)

| Minute | Item | Who | Output |
|---|---|---|---|
| 0–3 | **Numbers**, read from the dashboard's top row: MRR (total and by arm), new members yesterday, cost per member (Meta and blended), arm-B rate, refunds, chargebacks, first-session completion, founding seats, cash headroom | VA1 | — |
| 3–6 | **Reds and yellows**: each gets an owner, an action and a deadline | G | Logged in `#war-room` |
| 6–9 | **Spend**: apply §6.4. State today's budget for every campaign and any gate decision. | G | Budget line posted |
| 9–11 | **Creative**: yesterday's 5 (live? early read), today's 5 brief, graduations (Mon/Thu) | CL | — |
| 11–13 | **Ops and compliance**: crisis log, support themes and refund reasons, page and account health, processor messages, shoutouts booked vs needed, affiliates recruited | VA2, SUP, DEV | — |
| 13–15 | **Blockers and owners recap** | G | Decision log |

Rules: 60 seconds per item, and anything longer goes to a follow-up with only the people needed. Nobody presents slides. The dashboard is the agenda. At 21:00 VA1 posts an async recap (same top row + what changed today).

**Weekly review** (Mondays 09:00, 60 minutes, after the standup): price test status, shoutout roster (rebook/drop), affiliate funnel (outreach → approved → first referral), creative winners and losers, cohort refunds and first-session, cash vs plan, and next week's ramp decision.

---

## 8. SOPs: VA1, VA2, the content lead and support

### 8.1 Roles and coverage

| Role | Hours (ET) | Owns | Escalates to |
|---|---|---|---|
| VA1 (content QA + ad ops) | 07:00–15:00 | Render QA, ad uploads, naming, the 09:30 ad-rank sheet, the 21:00 recap, account health checks | CL (content), G (ads) |
| VA2 (community, DMs, partnerships) | 07:00–15:00 (+ event days) | Comments, DMs, crisis first response, shoutout sourcing, affiliate recruiting | G / on-call |
| CL (content lead) | 07:30–17:30 | Daily briefs, approvals, the event, pipeline health, **the evening crisis rota 15:00–23:00 on alternate days with G** | G |
| SUP (support) | 12:00–20:00 (+ a second agent from L2 if needed) | Tickets, refunds, cancellations, billing questions, the billing phone line, "text CANCEL" once SMS is live | G (> $150, legal, press) |

### 8.2 DM replies (humans; for anything automation can't handle)

**Rules**
- Humans sign as "{first name}, Strong Years team". Humans never reply **as** Chang or Sun in a private conversation about personal matters (FUNNEL §4.14 rule 5).
- Automated promotion only inside the 24-hour window. The HUMAN_AGENT tag (up to 7 days) is only for genuine human replies.
- Never give individual medical advice. Never say "you have…". Never promise results.
- Response targets: 2h during staffed hours (L1–L5), 4h after that. Crisis: 15 minutes.

**Reply library** (copy, personalize the first line, send)

| # | Situation | Reply |
|---|---|---|
| R1 | Price | "Founding membership is {{FOUNDING_PRICE}} a month, charged today, renewing monthly until you cancel. The price stays the same while you're subscribed. There's a 14-day money-back guarantee and you can cancel online in two screens. Here's the page: {link}" |
| R2 | How do I cancel? | "Here's how: {{DOMAIN}}/account → Membership → Cancel. It's two screens at most. Or reply CANCEL and I'll do it for you right now." (If they reply CANCEL: cancel, then confirm: "Done. You won't be charged again. You have access until {date}.") |
| R3 | Refund request | "Of course. I've refunded {amount} to your card. It usually shows in 5–10 business days. Your membership is cancelled, so there won't be any more charges." (Follow §8.4.) |
| R4 | "What's this charge?" | "That's Strong Years, our daily strength program. It shows as STRONGYEARS MEMBER. It looks like it was bought on {date} with the email {masked}. If you didn't mean to join, I'll refund it and cancel it right now. Just say the word." |
| R5 | "Is Chang real?" | "Straight answer: Chang Yin and Sun Yoon are AI characters our team created. They're not real people. The exercises and recipes are real and built on published guidelines for older adults, and the people replying to you here (like me) are real." |
| R6 | "Is the counter real?" | "Yes. It counts members whose first payment went through and who haven't taken a refund, and it updates every minute from our payment system. If someone refunds, their seat goes back." |
| R7 | Medical question ("Can I do this after my knee replacement?") | "That's a great question for your surgeon or physical therapist, because they know your knee. In general, every session has a chair version and a 'sore knee' button that swaps in an easier move. Please get their OK first." |
| R8 | Symptoms now ("chest pain", "I fell and can't get up", "can't breathe") | "Please call 911 right now. If you can't, ask someone near you to call." → pause automation → `#crisis` → log it. |
| R9 | Grief, loneliness, family pain | FUNNEL §4.14 rule 4 text, then within 24h a short human note: "Thank you for trusting us with this. I'm {first name}, a real person on the Strong Years team. I'm sorry you're carrying this. If it would help to talk to someone, the Friendship Line for adults 60+ is {verified number}, any time. We're glad you're here." No sales for 7 days. |
| R10 | Romantic attachment ("I love you Chang", "can we talk privately") | "That's kind of you. We want to be honest: Chang is an AI character our team created, not a person, and he can't have a relationship with anyone. If anyone ever messages you claiming to be Chang or Sun and asks for money, gift cards or to move to WhatsApp, it's a scam. Our team will never do that." (Tag `attach`. If it repeats, a human checks in kindly and suggests the Wednesday live with real people.) |
| R11 | "Is this a scam?" | "Fair question. We're Strong Years, a membership with openly AI coaches. You can see exactly what you'd pay before paying, cancel online in two screens, and refund yourself within 14 days. We never ask for gift cards, crypto or payment in messages." |
| R12 | Tech help (can't log in or find the session) | "Let's fix it. Tap this link, it logs you straight in: {magic link}. Then tap the big button that says 'Start today's session'. Still stuck? Reply with a photo of your screen and I'll walk you through it." |
| R13 | "Too hard" / "Too easy" | "Thank you for telling us. I've moved you to the {Rebuild/Steady/Strong/Iron} level, so tomorrow's session will match. You can switch anytime under Settings → My level." |
| R14 | "I can't afford it" | "Understood, and no pressure. The free Strength Age test and the free sessions on our page are yours anytime: {link}." (No discount. Essentials $12 is a cancel-flow save only, per OFFER §5.4.) |
| R15 | Gift question | "Gifts are prepaid: 3 months $49 or 12 months $119, and they never renew automatically. Your parent gets a welcome card from Sun Yoon. Here's the page: {{DOMAIN}}/gift" |
| R16 | Gift recipient confused ("Why do I have this?") | "Someone who cares about you gave you Strong Years! It's already paid for and it won't charge you. Tap here to start: {link}. If you'd like to know who sent it, it's on your welcome card." |
| R17 | Hostile ("AI is creepy / fake") | Public or private, once: "We hear you. We made the characters AI on purpose and say so everywhere, so nobody is fooled. The exercises are real. Totally fine if it's not for you." (No further engagement.) |
| R18 | Press, partner or business inquiry | "Thanks! Please email {press@ / partners@} and the right person will reply." → notify G. |
| R19 | Complaint about seeing too many ads | "Sorry about that. On the ad, tap ⋯ → 'Hide ad' or 'Why am I seeing this' to see fewer. If you're already a member, reply with your email and we'll make sure we stop showing you ads." (Add to the exclusion sync.) |
| R20 | Wants a human | "You've got one. I'm {first name} on the Strong Years team. What can I help with?" |

### 8.3 Comment moderation (VA2; CONTENT_SYSTEM §6.5 + this protocol)

| Comment type | Action | SLA |
|---|---|---|
| Keyword comment | Automation replies. The human rule: reply to the top 30–50 comments on each post in its first 60 minutes (CONTENT_SYSTEM §6.4) | 60 min |
| Genuine question | Reply in page voice (short, no medical advice), or the R7 pattern | 2h |
| "Is this real/AI?" | Pin the R5 answer on the post if it repeats | 1h |
| Personal medical story | Kind short reply + "please check with your doctor". Never an individual recommendation. | 2h |
| **Self-harm, abuse** | **No public character reply.** Hide the comment if it exposes the person's details. DM with the SAFETY §4.4 text (988, 911, findahelpline.com). `#crisis` alert. Human follow-up within 1h. | **15 min** |
| **Medical emergency** | Public reply: "Please call 911 now." DM the same. `#crisis`. | **15 min** |
| Links, phone numbers, "DM me", WhatsApp/Telegram, crypto, investment, gift cards | **Hide + ban + report** | 15 min |
| Accounts impersonating Chang, Sun or the team | **Romance-scam protocol** (below) | 15 min |
| Hate, slurs, cultural mockery | Hide + ban. Log for the cultural review. | 1h |
| Spam, promotion of other products | Hide | 4h |
| Criticism (fair) | Leave it up. Reply once if useful. | 4h |
| Misinformation from other commenters ("stop your meds") | Hide; reply: "Please don't change medicines without your doctor." | 1h |

**Romance-scam and impersonation protocol.** Viral elder personas attract fake accounts that DM fans, "fall in love", then ask for money. Our audience is exactly who they target.
1. **Prevention:** the pinned post "Hi, we're AI" plus a caption line monthly: *"Chang and Sun are AI characters. They will never message you first, ask for money, gift cards or crypto, or ask you to move to WhatsApp or Telegram. Our only accounts are @changyin, @sunyoon.kitchen and @changandsun."* The same line goes in the welcome email and the app.
2. **Auto-hide keywords** (ManyChat + the platform's hidden words): `whatsapp, telegram, hangout, signal me, dm me, text me, +1, gift card, crypto, bitcoin, invest, sugar, lonely? message me`, and variants.
3. **Daily sweep (VA2, 10:00):** search each platform for "Chang Yin", "Sun Yoon" and "changyin" handles. Report impersonators through each platform's impersonation form. Log the handle, the date and the report ID. Report weekly to G.
4. **Victim reply** (when someone says "Chang messaged me" or "I sent money"): *"Thank you for telling us. That wasn't us. Chang and Sun are AI characters and never message anyone first or ask for money. Please don't send anything else. If you already sent money, call your bank now, and report it at ReportFraud.ftc.gov and ic3.gov. The AARP Fraud Watch Network Helpline (877-908-3360, verify before launch) can also help, free."* Then `#crisis` (a human follows up within 24h). Log it.
5. **Never** reply publicly with the victim's details.

**Crisis protocol summary** (FUNNEL §4.14 + SAFETY §4.4; drilled on D−2):
- Detection: keyword/classifier on DMs, comments, chat and in-app messages.
- Self-harm: automation pauses; the fixed text goes out (988 / 911 / findahelpline.com); `#crisis` page; during staffed hours (07:00–23:00 ET) a human acknowledges within 15 minutes and follows up within 1h; outside them the fixed text is the response and a human reads it at 07:00. Logged for SB 243 reporting. The protocol is published at `{{DOMAIN}}/safety` and must match this section.
- Medical emergency: "Call 911 now." Pause automation. Page. Log.
- Abuse (including elder abuse): the resource text (Eldercare Locator 1-800-677-1116; 911 if in danger). Page. Log.
- Grief/loneliness: pause sales for 7 days; human note within 24h.
- **Tabletop scenarios (D−2):** (1) "I don't want to be here anymore" in a DM at 22:30; (2) "chest tightness during the chair test" in event chat; (3) "my son takes my money and won't let me leave" in an app chat; (4) "I sent $2,000 to Chang on WhatsApp"; (5) a commenter posts another member's phone number.

### 8.4 Refund handling (SUP; the policy is refund-first)

**Why:** a refund we make costs the charge. A dispute costs the charge + $15 + a strike on the ratio that decides whether we can keep processing.

| Case | Decision | Macro |
|---|---|---|
| Founding charge ≤ 14 days, any reason | **Refund in full immediately. No save attempt.** Cancel unless they ask to keep going. One money-back guarantee per person (a second request from the same email or card fingerprint → G decides). The bonus program download is revoked. | M1 |
| 15–60 days after the first charge, **0–1 sessions used and no downloads**, or "didn't realize it renews" | Refund the latest charge, cancel (discretion; never advertised) | M2 |
| A renewal charge disputed within 7 days, ≤ 1 session since the renewal | Refund the renewal, cancel | M3 |
| Duplicate charge or billing error | Refund immediately + apologize + log a bug | M4 |
| "I'll dispute it with my bank" | Refund immediately (M2 wording), cancel | M2 |
| Gift unredeemed ≤ 30 days | Refund | M5 |
| Bump, upsell or program ≤ 14 days, on request | Refund; download access revoked; one refund per add-on; repeat refunders flagged by card fingerprint | M6 |
| Kit (physical) ≤ 30 days | Refund; **no return required** (cheaper than return shipping) | M6 |
| Third refund-and-rejoin cycle | Refund, then G decides whether to block founding re-purchase | G |

- **Authority:** SUP up to $150 per customer per case. Above that, or anything legal, press-related or threatening → G.
- **Reason codes** (required; they feed the dashboard): `R-NOTUSED` · `R-FORGOT-RENEW` · `R-PRICE` · `R-TOO-HARD` · `R-TOO-EASY` · `R-TECH` · `R-AI` · `R-HEALTH` (a medical reason; don't ask for details) · `R-DUP` · `R-GIFT` · `R-FAMILY` (the purchase was made by or for a relative) · `R-OTHER`.

**Macros**
- **M1:** "Done. I've refunded {amount} to your card (5–10 business days to appear) and cancelled your membership, so there won't be any more charges. Your printables are yours to keep. Thank you for trying Strong Years. — {first name}, Strong Years team"
- **M2:** "I'm sorry about that. I've refunded your last charge of {amount} and cancelled your membership. You won't be charged again. If you ever want to come back, your progress is saved for 90 days. — {first name}"
- **M3:** "I've refunded the renewal of {amount} from {date} and cancelled, so nothing else will be charged. Sorry for the surprise. We'll keep working on making the reminder clearer. — {first name}"
- **M4:** "You're right, and I'm sorry: you were charged twice. I've refunded {amount}. It'll show in 5–10 business days. — {first name}"
- **M5:** "I've refunded the gift of {amount}. The recipient's access has been closed, and we won't contact them again. — {first name}"
- **M6:** "Refunded {amount} for the {item}. No need to send anything back. — {first name}"

### 8.5 Community moderation (the Courtyard)

**Rules** (pinned; plain language; 20px type):
1. Be kind. No comments about anyone's body, age or looks.
2. No medical advice to each other. Share what you did, not what someone else should do with their medicine.
3. No selling, no links, no phone numbers or addresses.
4. There are no private messages here, on purpose. If anyone asks you to talk somewhere else, tell us. Chang and Sun never do.
5. No politics or religion debates. This is the gym and the kitchen.
6. Share your numbers only if you want to. Everyone starts somewhere.

**Mechanics:** a prompt-based feed (OFFER §1.2). A new member's first 3 posts are held for approval. Links and phone numbers are auto-held. The crisis classifier runs on every post. Moderators (VA2 + SUP) check the queue at 08:00, 12:00, 16:00 and 20:00.

**Enforcement:** 1st issue: remove + private note ("We removed your post because {rule}. Thanks for understanding."). 2nd: 7-day posting pause. 3rd: removed from the Courtyard, with the membership kept and refunds available on request. Scams, harassment or a threat → immediate removal.

**Positive moderation:** reply to the first post of every new member within 4 hours with a real human welcome ("Welcome, Barbara! What was your first chair-stand number?"). Feature real member milestones **only with permission** captured through the review flow (FUNNEL §7.10).

### 8.6 Escalation matrix

| Trigger | To | Within |
|---|---|---|
| Crisis (self-harm, emergency, abuse) | On-call human (`#crisis` page) | 15 min |
| Legal threat, regulator letter, attorney contact | G → ATT | same day |
| Press inquiry | G (holding statements §9.3) | 2h |
| Injury report | G + CL (and REV if signed) | 2h |
| Processor or Meta enforcement message | G | 30 min |
| Refund > $150 or an unusual pattern | G | same day |
| Bug that affects payment or cancellation | DEV (page) | 15 min |

---

## 9. Risk register for the blitz

### 9.1 Register

| # | Risk | Likelihood | Impact | Early warning | Prevention | Owner |
|---|---|---|---|---|---|---|
| R1 | **Processor hold, reserve increase or closure** (Stripe) | Medium | Very high: cash and ability to sell | Stripe emails, payout delays, requests for documents | D−10 pre-clearance, launch notices, the §6.8 stack, volume within approval, a second processor | G |
| R2 | Braintree late or declined | Medium | Medium (capacity after about L45) | No decision by L10 | Apply D−10; standby: a high-risk ISO/merchant account application by L10 | G |
| R3 | **Ad account restricted or disabled** | Medium | High: stops ~70% of new members | Disapprovals, "restricted" banners, spend dropping | ADS.md §1 and §7 rules, AI tag, no personal attributes, the new dataset, AA1 criteria | G |
| R4 | Business Portfolio restriction (cascade) | Low–medium | Very high (FA assets too) | Portfolio-level warnings | D3 separation; 2FA; no circumvention | G |
| R5 | **Page restricted, reach cut or unpublished** | Medium | Medium (organic and ad identity) | Reach per post down > 50%, account status warnings | AI label on, uniqueness rules, warm-up ramp, no link spam (PIPELINE §5.5) | CL |
| R6 | **"Is this AI?" backlash / press exposé** ("AI grandpa sells to seniors") | Medium–high | High (brand, and platform attention) | Journalist email, hostile comment spikes, quote-posts | Disclosure everywhere, no fake testimonials, a real counter, easy cancel, real human hosts | G |
| R7 | Cultural criticism (Chinese/Korean heritage) | Low–medium | High | Comments from the community, creator videos | Paid consultants, CHARACTERS §14 checklist | CL |
| R8 | Member injured doing a session | Low | Very high | Ticket or DM mentioning a fall or injury | Chair versions, stop rules, screening advice, driving-video form accuracy, no unsafe form in ads | G + CL |
| R9 | Crisis message missed | Low–medium | Very high | Unacknowledged flags | Classifier + page + tabletop + rota | VA2 |
| R10 | Impersonators scamming fans | High | Medium–high | Victim messages | §8.3 protocol, daily sweep, warnings | VA2 |
| R11 | Refunds > 12% or a chargeback spike | Medium | High | Dashboard alerts | Promise–delivery match, onboarding, reminders, RDR/Ethoca | G |
| R12 | Arm-B conversion < 4% | Medium | High (the milestones slip) | 72h read | L4 gate fallback to 50% arm A; offer copy tests | G |
| R13 | Shoutout supply < 4 a day | Medium–high | Medium (−$28.5K day-30 MRR if there are none) | Bookings behind plan on L6 | 30-page roster, CPM-based pricing, newsletters as a supplement | VA2 |
| R14 | 10DLC late (expected) | High | Low–medium | — | Email-first design | G |
| R15 | Checkout or app outage on L1–L5 | Low–medium | High | Alerts | Load test, rollback, status page, synthetic purchases | DEV |
| R16 | Counter shows a wrong number | Low | High (integrity) | Mismatch with the processor dashboard (hourly check) | Single source of truth, reconciliation job | DEV |
| R17 | Cash cap breach | Medium (variant) | High | Headroom alerts | L4 gate, daily cash line | G |
| R18 | Warm-list complaints and spam traps | Medium | Medium (deliverability for the client's other brands) | Complaint rate ≥ 0.08% | Segment exclusions (UG-E), engagement gating, a sequence cap | G |
| R19 | Regulator inquiry on auto-renewal | Low | High | Letter | Attorney-approved flow, consent logs, reminders | G + ATT |
| R20 | A review claim published without a signed reviewer | Low | High | QA | `REVIEWER_SIGNED=false`, compliance checker | CL |

### 9.2 Response plans (the four blitz-critical risks)

**R1: Processor hold or reserve**
1. (0–30 min) G reads the notice and does **not** open a new account elsewhere to route around it. Reply within the hour with the documents asked for, plus a proactive pack: business description, the checkout/terms/cancel screenshots, the refund policy, the consent-log sample, dispute prevention enrollment, the refund and chargeback rates to date, daily volume and forecast.
2. (1h) Cut Meta to a level where cash covers media without payouts (§6.4 cash rule). Cash burn, not MRR, is what a hold threatens first.
3. (Same day) If Braintree is live and approved for the volume, **shift new card checkouts** to it within its approval, and tell Braintree why. Existing subscriptions stay where they are.
4. Customer impact: if payouts are held, members notice nothing. If processing is **stopped**, the checkout shows "Joining is paused for a few hours while we update our payment system" (H-4) and the founding counter freezes (the honest number).
5. Log everything. Ask the processor what threshold, document or change would lift the hold, and do exactly that.

**R3: Ad account restricted or disabled**
1. (0–15 min) VA1 screenshots the notice and pulls the list of recently rejected ads. G reads the stated policy.
2. (1h) File **one** well-documented appeal / "Request review" citing the specific ad, with the landing page and the AI disclosure evidence. Remove or fix the offending creative across all accounts (**the fix goes everywhere; the same ad does not get re-launched on AA2/AA3**).
3. Shift budget to AA2 **only if AA2 is in good standing and the restriction wasn't policy-related to the same content.** If the restriction names the business, the domain or the page, pause everything on Meta and appeal (circumvention risk to the portfolio).
4. Replace lost volume with shoutouts (buy the next week's posts early), warm-list re-sends to non-openers, and affiliates. Tell the team the projected MRR hit from the dashboard.
5. Root cause within 24h: which rule, which ad, which reviewer check failed. Update the ADS.md checklist.

**R5: Page restriction or reach cut**
1. VA1 checks Account Status / Account Quality for the specific violation. Confirm the AI label is still on and C2PA is present on recent posts.
2. Pause automated publishing on that page (`auto_publish=false`). Keep posting manually 1–2 a day, only formats with clean histories.
3. Appeal through the in-app flow. Don't create replacement pages (ban-evasion risk to the network, PIPELINE §5.6).
4. Owned audience first: the next email tells subscribers where else to find us (sibling pages, the app).
5. If a page is unpublished: holding statement H-5 on the sibling pages, and an email to affected followers who opted in.

**R6: "Is this AI?" backlash or a press exposé**
1. **Speed and consistency:** within 2 hours, one public statement (H-1 for comments, H-2 for press), pinned on all 3 pages. Everyone uses the same words.
2. **Show, don't argue:** link the "How we make this" page: the team, the evidence process, the reviewer if signed, the cancel/refund policy, the counter method.
3. **Offer receipts to the press:** screenshots of the disclosure in the bio, the first-3-seconds tag, the checkout terms, the 2-screen cancel, the refund policy. Offer an on-record conversation with G.
4. **Don't delete** critical comments (hide only abuse and scams). Don't pay for rebuttal content.
5. **Separate ourselves from Yang Mun honestly** (H-3): no pretend-real teacher, no clergy, no fake testimonials, no disease claims. Never attack the competitor.
6. If the story finds a real flaw (a claim, a bug, a missing disclosure), fix it the same day and say what was fixed.
7. Pause any ad that the story quotes until the story's claim is checked.

### 9.3 Pre-written holding statements (G approves the final wording on D−3; publish verbatim)

**H-1 · "Is this AI?" (comment reply and pinned note)**
> Yes. Chang Yin and Sun Yoon are AI characters, created by the Strong Years team, and we label them as AI everywhere: in our bios, on every video and on our website. They're not real people and they're not doctors. The exercises and recipes are real and built on published guidelines for older adults, and the people answering messages and hosting our live Q&A are real people. How we make this: {{DOMAIN}}/how-we-make-this

**H-2 · Press inquiry: general statement**
> Strong Years is a daily strength, balance and nutrition membership for people 55 and older. Its two coaches, Chang Yin and Sun Yoon, are openly AI characters. We disclose that on every profile, every video, in every direct message and at checkout, because we think people deserve to know who, or what, they're learning from. The content is general fitness and nutrition education built on published guidelines for older adults [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: and reviewed by licensed professionals]. It's not medical advice. Members can see the full price before paying, cancel online in two screens, and get a refund within 14 days. We're happy to show you exactly how it works. — {name}, {title}, {email}

**H-3 · Press: comparison with "fake monk" accounts**
> We built Strong Years to be the opposite of AI personas that pretend to be real teachers. Our characters are labeled as AI from the first second, they don't claim credentials or religious authority, we don't publish testimonials unless they're real and permissioned, and we don't make disease-cure claims. We'd rather be judged on the product: a short daily session, a monthly fitness retest, and honest recipes.

**H-4 · Payment pause (checkout banner + email to anyone mid-purchase)**
> Joining Strong Years is paused for a short time while we update our payment system. Nothing has changed for current members, and no one has been charged twice. The founding count is frozen at {{COUNT}} while we're paused. We'll email you as soon as it's open again.

**H-5 · Page unavailable (post on sibling pages + email)**
> Our @{handle} page is temporarily unavailable while we sort something out with the platform. Nothing has changed for members: your daily session is at {{DOMAIN}}/app as always. You can also find us at @{sibling handles}. — The Strong Years team (Chang and Sun are AI characters; we're the humans.)

**H-6 · Member injury report (private reply first; public only if raised publicly)**
> Private: "I'm so sorry this happened, and thank you for telling us. Please get checked by your doctor. If it's urgent, call 911. Could you tell us which session and which movement it was? We review every report with our team and will follow up with you personally. We've also paused billing on your account." (Log it; G + CL review the session within 24h; REV reviews it if signed.)
> Public: "We're sorry to hear this and have reached out privately. Every session has a chair version and stop rules, and we review every report. If anything hurts sharply, please stop and talk to your doctor."

**H-7 · Cultural criticism**
> Thank you for raising this. Chang and Sun's story is fiction, and we built it with paid Chinese-American and Korean-American cultural consultants to avoid stereotypes. No monks, temples or mysticism, no accent jokes. We take this seriously: we've shared your comment with our cultural reviewers and will update anything that misses the mark.

**H-8 · Counter correction (if the counter ever shows a wrong number)**
> Correction: between {time} and {time} our founding count showed {wrong number}. The correct number was {right number}, and it's fixed now. The count comes from our payment system, and a bug in how we displayed it caused the error. We're sorry. Nothing about anyone's membership or price changed.

**H-9 · "What do you do with my answers?"**
> Your quiz answers and anything you tell the coaches stay with us. We never send health details to advertising platforms, and we don't sell your information. You can see or delete what the AI coach remembers in Settings → Memory, anytime.

**H-10 · Billing error apology (email to affected members)**
> We made a mistake: on {date}, {n} members were charged {what happened}. If that's you, we've already refunded {amount}. You don't need to do anything, and your membership is unchanged. We're sorry. — {name}, Strong Years

---

## 10. Sources (fetched or searched 2026-09-30)

**Payments and chargebacks**
- Stripe pricing (dispute $15; Visa resolution $15; CE 3.0 block $15; Mastercard resolution $29; Billing 0.7%): https://stripe.com/pricing
- Stripe dispute prevention (RDR, Ethoca, Order Insight, CE 3.0): https://docs.stripe.com/disputes/get-started/prevention
- Stripe holds and reserves FAQ (moderate risk 10–15%, 90–180 days; new-account holds 7–14 days): https://terms.law/FAQ/payment-processors/stripe-holds-faq.html
- Subscription-merchant underwriting (5–10% for 90–180 days on new accounts): https://www.seamlesschex.com/deep-dives/recurring-billing-merchant-accounts-how-subscription-businesses-get-approved-in-2026
- Visa VAMP for recurring billing: https://www.seamlesschex.com/blog/visa-s-october-2026-rules-and-your-recurring-billing-mid
- Load balancing vs concealing chargebacks: https://merchantalternatives.com/glossary/load-balancing/
- Braintree fees (2.89% + $0.29; $15 chargeback): https://www.paypal.com/us/enterprise/paypal-braintree-fees

**Meta**
- Spending caps by account age: https://primescalemedia.com/blog/meta-spend-caps-explained
- Daily budget can spend up to 75% over; weekly cap 7×: https://www.jonloomer.com/updates-to-meta-ads-budgeting/
- Learning phase (50 events a week; reset triggers): https://adlibrary.com/posts/meta-ads-learning-phase-50-events-guide
- Creative testing tool (2–5 ads, ≤ 20% budget): https://www.jonloomer.com/meta-creative-testing/
- Health & wellness classification at the data-source level: https://www.triplewhale.com/blog/meta-health-and-wellness-brands
- Partnership Ads required for branded creator content (2026): https://www.contentgrip.com/meta-branded-content-rules-update/
- Business verification 3–10 working days: https://www.duochat.in/help-center/get-verified-with-facebook/how-long-meta-business-verification-usually-takes
- Facebook Premieres deprecated: https://www.socialmediatoday.com/news/meta-is-depreciating-its-video-premieres-option-on-facebook/626251/
- YouTube Premieres: https://support.google.com/youtube/answer/10356739?hl=en

**SMS, email and consent**
- Twilio 10DLC (manual brand review 7+ business days; campaign review 10–15 days): https://www.twilio.com/docs/messaging/compliance/a2p-10dlc/direct-standard-onboarding
- 10DLC total timeline 3–6 weeks; AT&T 2–4 weeks: https://www.telphiconsulting.com/blog/twilio-a2p-registration-timeline
- Twilio toll-free verification: https://www.twilio.com/docs/messaging/compliance/toll-free/console-onboarding
- FCC consent rule after the one-to-one vacatur: https://www.consumerfinancialserviceslawmonitor.com/2025/09/fccs-final-rule-on-consent-kills-one-to-one-consent-requirement/
- TCPA opt-out rules (April 2025): https://www.bclplaw.com/en-US/events-insights-news/the-tcpas-new-opt-out-rules-take-effect-on-april-11-2025-what-does-this-mean-for-businesses.html
- Florida mini-TCPA (8am–8pm; 3 per 24h): https://help.klaviyo.com/hc/en-us/articles/4405332994843
- FTC CAN-SPAM guide (designated sender; 10 business days; $53,088 per email): https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

**Endorsements, affiliates and health privacy**
- FTC Disclosures 101: https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers
- HHS HIPAA marketing guidance: https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/marketing/index.html
- 45 CFR 164.508: https://www.law.cornell.edu/cfr/text/45/164.508
- 1099-NEC $2,000 threshold from 2026: https://onpay.com/insights/1099-reporting-threshold-updates/
- FirstPromoter pricing: https://firstpromoter.com/pricing
- Rewardful pricing: https://www.rewardful.com/pricing
- Tolt pricing: https://tolt.com/pricing

**Shoutout, newsletter and podcast pricing**
- Meltwater influencer rates 2026: https://www.meltwater.com/en/blog/influencer-marketing-costs-rates-pricing
- SocialRails Facebook sponsored-post calculator: https://socialrails.com/free-tools/facebook-sponsored-post-rate-calculator
- beehiiv newsletter sponsorship costs: https://www.beehiiv.com/blog/newsletter-sponsorship-cost
- Paved newsletter benchmarks: https://www.paved.com/blog/newsletter-sponsorship-rates/
- Acast podcast CPMs 2026: https://www.acast.com/en/news-and-insights/how-much-does-podcast-advertising-cost

**Internal:** BLITZ.md, `economics.xlsx` (Blitz, Blitz_Plan), ECONOMICS.md, OFFER.md, FUNNEL.md, ADS.md, PIPELINE.md, CONTENT_SYSTEM.md, CHARACTERS.md, SAFETY_RULES.md, EVIDENCE.md (E01, E04, E11, E12, E13, E14, E22, E28, E29, E43, E49), ARCHETYPES.md (#2 Hank & Biscuit), `/home/claude/rebuild/app/src/lib/{config,pricing}.ts`, `src/lib/analytics/meta.ts`.
