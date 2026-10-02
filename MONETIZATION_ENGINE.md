# MONETIZATION_ENGINE.md: one offer engine that fits every person who shows up

Oct 2 2026. Canon: BRIEF.md CANON UPDATE 2–4, OFFER.md §0.1, FUNNEL.md §4.19, ENGINE_100X.md §7–8. Nothing here changes a canon price. New price points (prepaid 12 months, family bundle) are provisioned as **DRAFT** and need a client decision. Hard rules that stay in force: no fake scarcity, the honest 5,000 cap, Shopify checkout, 14-day money-back guarantee, AI disclosure, no health claims, no countdowns, nothing pre-ticked, cancel in two screens.

**Goal:** the highest share of people buy *something that fits them*, and revenue per conversation (RPC) and revenue per visitor (RPV) go up. That happens by routing each person to the right offer family. It never happens by changing the price one person sees.

---

## 1. What the research says (≤15 searches, Oct 2026)

| Question | Finding | Confidence | What we do with it |
|---|---|---|---|
| Keyword → DM → purchase | Comment-triggered DMs open 85–92%. Link CTR is 18–35% for high-intent recipients. DM-to-purchase is 12–25% for digital products and 2–5% for **unqualified** flows. Qualified flows convert about 2.4× better [S1]. | Vendor numbers (V-). Use them as gates, not forecasts (ENGINE_100X §8.8). | A **2-question qualify** branch (goal, who it's for) in the BOOK flow. It runs as a 50/50 test against the direct link (`dm_qualify`). |
| One-page checkout for 55+ | I found no age-split checkout data in 2025–26 sources. Baymard's 2024 study lists 1,350+ checkout usability issues but publishes no age cut [S2]. Re-entering payment details cuts post-purchase conversion by about 78% [S8]. | Low for the age-specific claim. | Keep one product page → Shopify one-page checkout with Shop Pay first (ENGINE_100X §8.6). No second card entry anywhere. Our own forms (/ask) work without JavaScript. |
| Price anchoring / good-better-best | The sources were practitioner blogs. They say a middle tier anchored by a premium tier gets the most picks [S3]. | V- | The gift page shows **3 months $49 / 12 months $119**, both as per-month prices, with nothing preselected. No decoy SKUs are invented. |
| Annual vs monthly | Health & Fitness apps earn **68% of revenue from annual plans**. Median prices: $9.99/month, $39.94/year [S4]. | H (RevenueCat, large panel), but app-store buyers, not 55+ web. | Annual is offered at the canon moment (after renewal 1) through routing (R08). Annual is the biggest per-person lever after the cell. |
| Pay-what-you-want | Gneezy et al., *Science* 2010: PWYW raised purchases from 0.5% to 8.4%, but the average payment fell from $12.95 to $0.92 (below cost). PWYW plus a charity tie-in earned the most profit (4.5% bought, $5.33 average) [S5]. | H (field experiment, n≈113K riders). | **No open "pay what you want" price.** Price help is a **human-reviewed request** (/ask/price) using single-use codes, with a monthly seat budget. |
| Gift from adult children | 63M US family caregivers (AARP 2025). 83% of caregivers shop online; 41% spend $250+/month on the person they care for [S6]. | H for the size of the market; no data on gift conversion. | The tagger / FAMILY / "a parent" answer routes to the gift page. A caregiver **family bundle** (gift + books for the buyer) is a DRAFT proposal. |
| Pause vs cancel / win-back | 75% of paused customers returned to billing. 20–25% of new acquisitions are returning subscribers. Win-back cadence of 30/60/90 days, stop after 3–4 touches [S7]. | M (Recurly, vendor but large base). | Pause is already the default save offer (`cancel.ts saveOfferFor`; Essentials only for "too expensive"). Win-back is **tiered by how long the person has lapsed**, 3 touches at most. |
| Post-purchase / thank-you offers | Thank-you-page take rate is 10–16%; 14.6% in an independent study of 1,847 stores (physical goods) [S8]. | M | One thank-you offer, matched to the cell and the pillar (data table). |
| Shopify features | **Shop Pay Installments can't buy subscription products or gift cards**; US orders must be $35–$30,000 [S9]. Markets supports price lists with percentage or fixed per-market prices [S10]. Quantity-minimum discount codes work on Basic (validated against the Admin schema: `minimumRequirement.quantity`). | H (Shopify docs) | The **annual subscription can never be split into installments**, so the only honest installments path is a one-time **12-months-prepaid $249** product (DRAFT). Regional pricing applies only to one-time products, and only once a market is verified. The group rate uses `GROUP5` (20% off 5+ gift seats). |
| Referral timing | Practitioner guidance: ask right after the customer's first success moment [S11]. | V- | The referral ask fires once, at the first win (Strength Age improved, Day 7 complete, or a better retest), never before day 7. |

## 2. Intent → offer routing (data, not code)

- **Table:** `workers/dm/offer_routing.json`. There is a byte-identical copy at `app/src/lib/offers/routing.json`, and the app test fails if the two differ.
- **Evaluators:** `workers/dm/routing.py` and `app/src/lib/offers/route.ts`. Both run the same shared vectors in `workers/tests/fixtures/offer_routing_vectors.json`.
- **How it decides:** rules are first-match. Each rule's `when` uses equality, list membership, or `in/nin/lt/lte/gt/gte/has/lacks/exists`.
- **What a rule picks:** an **offer family**. It never picks a price: the front-end price comes from the visitor's sticky cell (m12/e12), and every other price comes from the catalog.

**Inputs:**
- keyword → pillar
- the two DM qualify answers (goal, who it's for)
- platform, surface (dm, b, go, tt, thank_you, email, app), follower, tagger
- device, hour, country
- what the person already owns (books / member / annual / gift_buyer / coached), months paid
- waitlist age, days since lapse
- Strength Age plateau, hardship flag

**Offer families:**
- front_end (the cell: $12 books + first month, or $12 books)
- founding $25, rejoin, win-back $12 / $9, Essentials $12, annual $249, prepaid12 (off)
- gift $49/$119, family bundle (off)
- coached $147, labs interest
- free Day 1, free waitlist
- group quote, price help
- none (value only)

**Rule order, in plain words:**
1. Runway → waitlist.
2. Hardship → a person.
3. A group → quote form.
4. Closed country → waitlist.
5. Coached member → no selling.
6. A member who asks for labs → labs interest (members only; licensed humans quote).
7. Member + plateau → coached. Member after renewal 1 → annual (app and email surfaces only).
8. Any other member → no selling.
9. Lapsed: up to 30 days → rejoin at the public price; 31–90 → $12 first month back; 90+ → $9 first month back.
10. Books-only buyer → founding, on thank-you and email only. Never in a DM (FUNNEL §4.19).
11. Tagger, "a parent", or FAMILY → gift: 12 months for repeat gifters, 3 months otherwise.
12. TikTok bio (go/tt only) → free Day 1 first.
13. JOIN → founding.
14. A cold 30-day waitlister → Day 1 first.
15. Late-night DM → front end, with "email me the link" first.
16. "Just help me start" + not a follower → Day 1.
17. Default → front end with the bump matched to the pillar.

**Where it runs:**
- **DM bot** (`bot.py`): BOOK dm1 has a "Help me choose" button → 2 questions → a `route` state, which maps the offer to the right DM state (gift, group, price help, free Day 1, member, books link). The answers go into `/b` (`g`, `a`) so the web routes the same way.
- **Global intents:** "can't afford / fixed income / too expensive" → the price-help path (a human). "Senior center / our group" → the group-quote path.
- **`/b`** (`app/src/app/b/route.ts`) routes live traffic using:
  - keyword, `g`/`a`, platform, the `x-vercel-ip-country` header
  - for a signed-in member, `memberContext` (what they own, how long they've lapsed)

  Families go through the sticky cell. Free and human paths redirect to our own pages. A lapsed member's `/b` adds the win-back code (`WINBACK12` / `WINBACK9`, or the `S` versions after the founding close) through Shopify's `/discount/<CODE>` share link.

## 3. Price flexibility within canon (`shopify/config/catalog.ts` + dry-run)

| Item | How | Status |
|---|---|---|
| Regional pricing | `MARKETS`: US is open. CA, UK/IE, ANZ, and a −40% purchasing-power tier stay **closed** until two checks pass: (a) the free Shopify Subscriptions app bills the membership correctly in that currency, and (b) tax registration. Adjustments apply to one-time products only, never the membership. The dry-run lists the exact Markets settings under `manual`. | config + manual |
| Hardship / pay what you can | `/ask/price` form → support ticket + `price_help` exception → a person issues a single-use `SYHELP-n` code (`HARDSHIP_POLICY`: Essentials price on the full membership, or 50% off, for 6 cycles; 50 seats/month; 2-business-day SLA). The copy promises only that a person reads it. | live path, human-run |
| Group rates (5+) | `/ask/group` quote form → `group_quote` exception → a person sends gift seats with `GROUP5` (20% off 5+ gift seats; never advertised publicly) or a draft order. | live path + code |
| Caregiver bundle | `family-bundle` $55 (3-month gift + Starter Books for the buyer). | DRAFT (client decision) |
| Installments on annual | Not possible on a subscription [S9]. Instead: `strong-years-12-months-prepaid` $249 one-time, no auto-renew; Shop Pay Installments applies at ≥$35. Same price as the annual, so nobody is shown two prices for a year. | DRAFT (client decision) |
| Pause instead of cancel | Already the default save offer (`cancel.ts`): pause 1/2/3 months free. Essentials is shown only for "too expensive". Both sit next to an equal-size "Finish canceling". | existing |
| Win-back by lapse | `WINBACK12/12S` ($12 first month back), `WINBACK9/9S` ($9). First payment only, once per customer, membership product only. Touches on days 30/60/90, 3 at most. | codes + routing |

**Activating a DRAFT product:**
1. The client approves the price.
2. Set `status: "ACTIVE"` and run `npm run provision`.
3. Add a members-catalog row in `plan.ts` verify:
   - prepaid12 → entitlement `gift`, `gift_months: 12`, the buyer as recipient
   - family bundle → gift 3 + ebook
4. Set `enabled: true` for the offer in the routing table (both copies).

**System codes** (`SYSTEM_CODES`) are excluded from affiliate crediting (`shopify/src/webhooks.ts affiliateCode`). The members app already credits only codes that belong to approved affiliates.

## 4. Dollars per conversation

- **Qualify in ≤2 questions, then route** (§2). Quick replies only. The answers are allow-listed values, stored on the contact and carried into `/b`.
- **Order bump matched to intent** (`bumps.by_pillar`). Knees, strength and balance get the wall plan (plus the $29 kit as a second bump). Kitchen and gut get "Sun Yoon's grocery lists", which is the same $9 SKU framed by intent. Nothing is pre-ticked. The frame table is data; the theme still has to read `t` (already passed to the product page as `keyword`) to choose the frame. That is theme work, not done here; the `bump_frame` test (matched vs generic) is defined.
- **Thank-you offer matched to the cell** (`thank_you`): e12 → founding (canon). m12 (already a member) → the $29 kit for movement pillars, the gift otherwise. One offer, never stacked.
- **Second purchase within 7 days** (`second_purchase` in `content/lifecycle/sequences.json` + `lifecycle/engine.ts`): m12 buyers only. Day 3 brings the bump matched to their entry keyword; day 6 the gift. It stops at the first bump or gift and respects the lifecycle engine's quiet hours and 1/day cap. Cell A keeps its 3 onboarding emails.
- **Referral ask at the first win** (`referral`): Strength Age improved, Day 7 complete, or a better retest. Asked once, not before day 7, not within 24 h of a ticket or refund request. Reward: the existing bonus PDF.

## 5. Experiment framework (`app/src/lib/offers/experiments.ts`, table `offer_events`)

- Every surface is a named experiment in the routing JSON: `fe_cell` (the live price cell), `dm_qualify`, `bump_frame`, `thankyou_offer`, `referral_moment`.
- **Sticky assignment:** `fnv1a(salt:subject)` → **murmur3 fmix32** → mod arms. It is identical in Python and TS and checked by the vectors.
- **Why the mixing step:** plain `fnv1a % 2` is just the parity of the odd characters in the input. Two 2-arm experiments hashed that way would put every person in the same arm of both.
- `fe_cell` keeps the live plain-fnv1a formula so the labels match what was sold.
- **`offer_events`** (migration `20261002000000_monetization_engine.sql`) is the offer attribution table:
  - `exposure`: one per subject/surface/experiment/offer/day, with the shown price
  - `conversion`: written from `orders/paid` for every first-purchase line, unique per line, with the channel from the last touch
  - `ask`: a group-quote or price-help request

  It holds no emails.
- **Guardrails in code:**
  - `armFor`: a price experiment is locked to the first arm logged for a person, even if the arms or salt change later. One price per person.
  - `lockedPrice` / `violatesRaise`: within 30 days, never show a person a higher price for an offer family than the lowest one already shown.
  - Routing data carries `max_offers_per_dm_thread: 1`, `max_sales_dms_per_7d: 2`, no countdowns, no pre-ticked boxes.
- **Weekly readout:** `readout()` gives RPV by arm. It counts revenue only after the subject's first exposure and is visible at `/admin/monetization` (7 or 30 days).

## 6. Measurement (`app/src/lib/offers/metrics.ts`)

- **RPV:** first-purchase revenue (from `offer_events` conversions) ÷ distinct visitors on offer surfaces (/b, /go, /tt, gift page) in the window.
- **RPC:** revenue whose last touch was a DM ÷ DM conversations started in the window. The denominator comes from the new worker endpoint `GET /dm/stats` (counts only; no ids leave the worker), which also reports the qualified share, the routed-offer mix and the arm counts.
- **Take rates per rung:**

  | Rung | Rate |
  |---|---|
  | R0 starter | buyers ÷ visitors |
  | bump | bump buyers ÷ starter buyers |
  | R1 books → membership | cell A buyers who joined ÷ cell A buyers |
  | R1a annual / prepaid | ÷ members charged |
  | G gift | ÷ all first-order buyers |
  | R3 coached | ÷ members charged |

  Renewals are excluded; renewal 1 keeps its own tile.
- **On `/admin/today`:** one panel (`app/src/app/admin/today/MonetizationPanel.tsx`, mounted with one line). The full view is the `/admin/monetization` route. High-contrast ink on rice; no gray text.

## 7. Things the client should know (found while building)

1. **The live cell test hashes with plain fnv1a % 2** (`shopify.ts assignFrontEndCell`). Any other 2-arm test that uses the same formula (the blitz arms in `blitz.ts`) is perfectly correlated with the cell. The new framework mixes the hash. Switching the cell hash before launch is cheap; after launch it would reshuffle people, so decide now.
2. **The gift for 12 months ($119) costs less than the founding annual ($249/yr).** A self-buyer can "gift" themselves a year for $119. Decide before launch: raise the 12-month gift, limit gifts to a different recipient email (already the intent), or accept it.
3. **The annual subscription cannot use Shop Pay Installments** (Shopify rule). The only honest installments path is the one-time prepaid year (DRAFT above).
4. **The win-back consent record:** the theme must record the code price and the plan price (as it does for STARTER12) on win-back pages, or `consentMatchesCharge` files a review ticket for each win-back order.
5. **Win-back emails:** the existing `win_back` sequence links to `/b?t=JOIN`. The code applies only when the member is signed in at `/b`. The next step is a signed member token on win-back links.
6. **Two Day 1 links:** the DM flows link Day 1 as `/s/l1`, while the members app's free Day 1 is `/start`. The routing table uses `/start`. Confirm `/s/l1` resolves on the production domain.

## 8. Files

- **Workers:**
  - `workers/dm/offer_routing.json`, `workers/dm/routing.py`
  - `workers/dm/bot.py` (qualify answers, route and experiment states, intent tags, answers carried into `/b`)
  - `workers/dm/flows/book.json`, `workers/dm/flows/_global.json`
  - `workers/dm/api.py` (`/dm/stats`)
  - `workers/tests/test_offer_routing.py`, `workers/tests/fixtures/offer_routing_vectors.json`
- **App:**
  - `app/src/lib/offers/{routing.json,route.ts,experiments.ts,metrics.ts,context.ts,ask.ts}`
  - `app/src/app/b/route.ts`
  - `app/src/app/(site)/ask/[kind]/page.tsx`, `app/src/app/api/offers/ask/route.ts`
  - `app/src/app/admin/today/MonetizationPanel.tsx`, `app/src/app/admin/monetization/page.tsx`
  - `app/src/lib/billing/shopifyWebhook.ts` (conversion log)
  - `app/src/lib/lifecycle/engine.ts`, `app/content/lifecycle/sequences.json`
  - `app/src/lib/db/{types,memory}.ts`, `app/src/lib/exceptions.ts`
  - `app/supabase/migrations/20261002000000_monetization_engine.sql`
  - `app/tests/unit/offers.monetization.test.ts`
- **Shopify:**
  - `shopify/config/catalog.ts` (DRAFT products, win-back and group codes, `SYSTEM_CODES`, `HARDSHIP_POLICY`, `MARKETS`)
  - `shopify/src/plan.ts` (group and win-back discount inputs, Markets / hardship / installments manual steps)
  - `shopify/src/webhooks.ts`, `shopify/test/plan.test.ts` + snapshot

## Sources

- [S1] Communipass, "Auto DM Statistics 2026" (vendor; cites Inrō and ManyChat 2026 playbooks): https://communipass.com/blog/auto-dm-statistics-2026-open-rates-conversion-benchmarks/
- [S2] Baymard Institute, "2024 E-Commerce Checkout research findings": https://baymard.com/blog/checkout-2024-launch ; no age split found in https://www.envisagedigital.co.uk/shopping-cart-abandonment-statistics/
- [S3] Good-better-best / decoy (practitioner): https://flexprice.io/glossary/good-better-best-pricing ; https://medium.com/@atticusli/the-decoy-effect-in-plan-selection-how-a-third-option-changes-everything-0f5cc35eeff0
- [S4] RevenueCat, "State of Subscription Apps 2026": https://www.revenuecat.com/state-of-subscription-apps
- [S5] Gneezy, Gneezy, Nelson, Brown, "Shared Social Responsibility", *Science* 329 (2010): https://www.science.org/doi/10.1126/science.1186744 ; numbers via https://newsroom.haas.berkeley.edu/name-your-price-pricing-strategy-aimed-achieving-corporate-social-responsibility-and/
- [S6] AARP, "Family Caregiver Retail Preferences": https://www.aarp.org/pri/topics/ltss/family-caregiving/caregiver-shopping-habits/ ; AARP/NAC "Caregiving in the US 2025": https://www.aarp.org/press/releases/2025-07-24-new-report-reveals-crisis-point-for-americas-63-million-family-caregivers.html
- [S7] Recurly, "Customer winback strategies for subscriptions": https://recurly.com/blog/customer-winback-strategies-for-subscriptions/
- [S8] Digital Applied, "Post-Purchase Upsell: The 2026 eCommerce AOV Playbook" (cites Yotpo 2025, Focus Digital Jul 2025, GemPages 2026): https://www.digitalapplied.com/blog/post-purchase-upsell-thank-you-page-2026-ecommerce-playbook
- [S9] Shopify Help Center, "Shop Pay Installments FAQ": https://help.shopify.com/en/manual/payments/shop-pay-installments/faq ; Shop Help "Shop Pay Installments plans": https://help.shop.app/hc/en-us/articles/32082086905108-Shop-Pay-Installments-plans
- [S10] shopify.dev, "About Shopify Markets": https://shopify.dev/docs/apps/build/markets ; Shopify Help, international pricing limitations: https://help.shopify.com/en/manual/international/pricing/limitations
- [S11] ReferralCandy, "Best time to ask for a referral": https://www.referralcandy.com/blog/best-time-to-ask-for-a-referral
