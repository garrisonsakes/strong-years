#!/usr/bin/env python3
"""
organic_engine.py — Strong Years organic-first launch model on the CANON UPDATE 2 ladder
(BRIEF.md, Oct 1 2026; CANON UPDATE 3 ordering): Shopify store, ebook front end at $7 / $12 / $15.
LAUNCH DEFAULT = cell B: "$12 today = books + first month, then $25/mo" as ONE subscription purchase
(the founding plan on the free Shopify Subscriptions app + the STARTER12 first-payment-only code).
TEST CELL = cell A: one-time ebook -> founding offer on the thank-you page + 3 onboarding emails
(the one-click post-purchase page stays OFF: beta, needs access approval, never fires on
digital-only or wallet/PayPal orders; pp_take = 0 in the R22 test-cell run, 0.12 only when it is on).
No $1 trial anywhere. Runs R20–R26, the waitlist / list-size solver, the runway table, the
sensitivity table and the configuration ladder. Produces the values in economics.xlsx sheet
"Organic_First" and the r20…r26 columns of mrr_blitz_daily.csv.

What is inherited from the Blitz-sheet engine (scratch bs2.py, which matches the Blitz sheet to
the dollar on R4/R5): the renewal curve S, the arm-B renewal adjustment, the $249 annual after
renewal 1, Essentials $12 save offers and pauses, chargebacks, the rolling reserve, payout lag,
fixed opex, content cost per post, member COGS, the kill-rule contribution lines (SCALE/CUT) and
the §11 graduation logic. What changed for CANON UPDATE 2:

  * The quiz / $1-trial / charge-today arm structure is gone. Every path is: traffic -> ebook
    sales page -> ebook order -> (cell A) one-click post-purchase membership accept, or
    (cell B) a single subscription-inclusive purchase.
  * Shopify Payments fees (2.9% + 30¢ on Basic; no separate billing fee: Shopify Subscriptions
    is free) replace Stripe 2.9% + 30¢ + 0.7% Billing.
  * Founding cap 5,000 -> $35 standard afterwards (price per cohort day).
  * Post-purchase ELIGIBILITY: Shopify's post-purchase page is not shown for wallet / installment
    payments (Apple Pay, Google Pay, PayPal, Klarna…) and a subscription cannot be added
    post-purchase to an order WITHOUT A SHIPPING ADDRESS (digital-only orders). So cell A only
    works if the ebook order collects a shipping address, and only on card / Shop Pay orders.
    `pp_elig` carries that share; `elig_addr` = 0 models "ebook sold as a pure digital product".

Organic layers (pages, cadence, views by account age, platform multipliers, keyword -> DM -> link
rates, runway waitlist, boosts / retargeting caps, shoutouts, affiliates) are unchanged from v1 of
this file and keep their sources.

SCALE FAMILY R30–R36 (Oct 2 2026, "Scale plan to $250K", BLITZ.md §14): a port of the client-approved projection
data/projection_aggressive_central.csv (booked vs retained vs cash vs contracted_30d), see the last section of this file.
`python3 tools/organic_engine.py --scale` prints it; `python3 tools/organic_max_sheet.py` writes sheet Organic_Max and
appends the r30…r36 *_booked_MRR / *_retained_MRR / *_cash_scale / *_views_scale / *_posts_scale columns of
mrr_blitz_daily.csv. The older Organic-max family (formerly R30–R35, now OM30–OM35, `--max`) is legacy: its frozen
csv columns r30_MRR…r35_posts are left exactly as written.

Run:  python3 tools/organic_engine.py              -> prints the run table, solver, runway table
      python3 tools/organic_engine.py --json out    -> also writes the JSON used by the workbook writer
Every number marked ASSUMPTION is an assumption; sources are listed in SOURCES.
"""
import json, sys, math

# ----------------------------------------------------------------------------------------------
# Shared inputs. Blitz-sheet values except where marked SHOPIFY / LADDER.
# ----------------------------------------------------------------------------------------------
SH = dict(cpm=18.0, ctr=0.015, reflag=7,
 elas=0.30, S=[1,0.62,0.50,0.43,0.385,0.35], churn=0.05, sref_d=1500, pen=0.20, realized=0.95,
 disc=0.10, learn_new=1.35, learn_exist=1.15,
 deliv=0.92, open=0.30, ctor=0.08, sms_share=0.35, sclick=0.06, wlp=0.85, gift=0.12, gift_price=49,
 email_w={1:1.0,3:0.8,6:0.7,9:0.6,13:0.6,20:0.5,27:0.5}, sms_w={2:1.0,8:0.8,14:0.7}, k9mult=0.35,
 sh_cost=600, sh_reach=120000, sh_ramp=1,
 aff_start=10, aff_per_day=3, aff_cap=120, aff_visitors=1.83, comm=0.30,
 cap1=250000, proc2_day=21, cap2=500000, reserve=0.10, res_days=90, lag=5,
 cbB=0.003, cbFE=0.002, cb_fee=15,
 pct=0.029, fix=0.30, bill=0.0,            # SHOPIFY: Shopify Payments Basic 2.9% + 30¢; Subscriptions app free
 shop_plan=39.0,                            # SHOPIFY: Basic plan, monthly billing ($29/mo on annual)
 fe_ref=0.06, sub_ref=0.025, media=0.06,
 fixed=30500, cost_post=0.60, cogs=0.809674, varm=0.40,
 bump9_take=0.30, bump29_take=0.06, kit_cogs=12, kit_margin_price=29, txn_fe=1.0,
 ess_price=12, ess_churn=0.08, learn_allow=1.15,
 lp_org=0.70,                               # DM link click -> landing page actually loads
 found_cap=5000, std_price=35)

# ----------------------------------------------------------------------------------------------
# Ladder inputs (new). key, label, central value, unit, source / rationale
# ----------------------------------------------------------------------------------------------
LADDER_INPUTS = [
 ('fe_price','Ebook bundle price (cells $7 / $12 / $15; default display $12)',12,'$','CANON UPDATE 2.'),
 ('cvr_org','Landing visitor → ebook buyer, organic DM / bio-link traffic, at $12',0.05,'%','Tripwire pages: 1.5–5% cold, 8–15% warm (CartFlows 2026); 5–15% of new subscribers (Zanfia 2026). DM-originated visitors commented a keyword and clicked a DM link, so they sit between cold and warm: 5% central, 3% conservative, 8% upside. ASSUMPTION within the cited range.'),
 ('cvr_cold','Landing visitor → ebook buyer, cold Meta / shoutout traffic, at $12',0.03,'%','CartFlows: 1.5–5% cold. 3% central.'),
 ('cvr_warm','Landing visitor → ebook buyer, warm email lists (Unignorable / K9SUPPS), at $12',0.08,'%','CartFlows: 8–15% warm; low end because these lists did not opt in for this brand.'),
 ('fe_elas','Ebook conversion elasticity: cvr × (12 ÷ price)^fe_elas',0.5,'x','ASSUMPTION. $7 → ×1.31, $15 → ×0.89. Zanfia: below $7 reads as clearance; $10–30 is the sweet spot.'),
 ('elig_addr','Share of ebook orders that collect a shipping address (required for a post-purchase subscription)',0.0,'%','Shopify dev docs: "If the customer\'s checkout results in the creation of an order without a shipping address, then you can\'t add a subscription to the order using post-purchase. For example, a customer might have bought only digital products." Catalog default (shopify/config/catalog.ts ebooks requiresShipping: false) = 0: a pure digital product, so the post-purchase subscription cannot fire; the one-click sensitivity rows set it to 1 explicitly (the variant would have to be changed to require shipping).'),
 ('elig_pay','Share of ebook orders paid by card or Shop Pay (post-purchase page is NOT shown for Apple Pay, Google Pay, PayPal, Klarna, Affirm, Afterpay, gift cards)',0.70,'%','Shopify dev docs limitations (wallets/installments excluded; Shop Pay allowed per Rebuy/Shopify). Wallet share is an ASSUMPTION: 30% of a 55+ mobile checkout mix; sensitivity 0.50–0.85.'),
 ('pp_take','Post-purchase one-click accept of the $25/mo founding membership (of eligible orders)',0.12,'%','Published Shopify post-purchase benchmarks: 5–12% one-click acceptance (EasyApps, Mar 2026); 16.2% average across Zipify OCU merchants, ~4% under-optimised; 15–25% upsell acceptance for warm audiences (CartFlows). A recurring $25 subscription with a consent checkbox should sit BELOW product-upsell rates: 12% central, 6% conservative, 20% upside. ASSUMPTION within the cited range.'),
 ('pp_price_elas','Post-purchase take vs ebook price: take × (price ÷ 12)^pp_price_elas (dearer ebook = higher-intent buyer)',0.2,'x','ASSUMPTION. $7 → ×0.90, $15 → ×1.05.'),
 ('later_take','Thank-you page + 3 onboarding emails: membership purchases among ebook buyers who did not accept post-purchase (days 1–7)',0.04,'%','ASSUMPTION. Needs a new checkout (card re-entry unless Shop Pay). CartFlows: email lists convert 1–2% to paid; a 7-day buyer onboarding sequence to a $25 membership: 4% central, 2% conservative, 7% upside.'),
 ('later_split','Timing of later catches (day 1…7 after the ebook order)',[0.40,0.25,0.15,0.10,0.05,0.03,0.02],'','ASSUMPTION: thank-you page on day 1, emails on days 1, 3, 5.'),
 ('subB','Cell B: "$12 = books + first month, then $25/mo" purchase rate ÷ one-time $12 ebook purchase rate',0.70,'x','ASSUMPTION. Same price, same books, but a disclosed auto-renew at $25 (ROSCA consent box) costs conversion: 0.70 central, 0.55 conservative, 0.85 upside. Comparable: the Blitz arm-B factor (charge-today $25 vs $1 trial) is 0.40; this is a much smaller ask.'),
 ('renB1','Cell B: survival of the first $25 renewal on day 30',0.50,'%','ASSUMPTION between trial→paid 42% (Adapty, health & fitness) and the charge-today month-1 renewal 62% × 0.935. They paid $12 and received the books, but never chose to pay $25.'),
 ('ref_pp','14-day money-back refunds on post-purchase membership charges',0.12,'%','Blitz central (12%); upside 10%.'),
 ('mrr_cellB_at','MRR convention for cell B members in their first cycle',25,'$','MRR counts an active auto-renewing subscription at its contracted renewal price ($25), as the BLITZ.md definition does for charge-today. Cash in month 1 is $12. Retained MRR applies renB1, which is the honest number for cell B.'),
 ('bumps','Cart bumps on the ebook order: $9 wall plan 30%, $29 resistance kit 6% (physical; COGS $12)',0.30*9+0.06*29,'$/order','OFFER.md take rates; CANON UPDATE 2 bump list (the $27 / $7 upsells are gone).'),
]
LAD = {k:v for k,_,v,_,_ in LADDER_INPUTS}

# ----------------------------------------------------------------------------------------------
# Organic inputs (unchanged from v1; sources in SOURCES)
# ----------------------------------------------------------------------------------------------
ORG_INPUTS = [
 ('pages_d1','Pages live on runway day 1',3,'pages','Client: 3 pages on day 1 (IG Chang Yin, FB Chang Yin, TikTok Chang Yin).'),
 ('pages_max','Pages live at full ramp',7,'pages','IG CY, IG SY, IG clips, FB CY, FB SY, TikTok CY, YT CY (Assumptions A). One new page every 3–4 days.'),
 ('page_days','Runway day each page goes live (1-based)',[1,1,1,4,7,10,14],'day','ASSUMPTION: IG CY, FB CY, TT CY day 1; IG SY day 4; FB SY day 7; YT CY day 10; IG clips day 14.'),
 ('page_plat','Platform of each page',['IG','FB','TT','IG','FB','YT','IG'],'','Buyer is 55+, so Facebook Reels are included from day 1 (Sun Yoon FB page from day 7).'),
 ('posts_d1','Posts per page per day at page launch',3,'posts','ASSUMPTION: a page starts at 3/day and ramps as the content pipeline and account trust build.'),
 ('posts_max','Posts per page per day at full cadence (central)',6,'posts','Client cadence 6–9/day/platform; 6 in central (Assumptions A), 9 in the upside.'),
 ('posts_ramp','Days for a page to ramp from launch cadence to full cadence',10,'days','ASSUMPTION.'),
 ('v_base','Mean views per post at page age 15 days, before platform and scenario multipliers',6000,'views','Assumptions A (v1 = 6,000 month-1 mean). Evidence (data/posts.csv): Yang Mun TikTok launch era, first 15 days (n=15) median 76.8K / mean 953K; days 16–30 (n=5) median 47.3K; return era (days 270–400, n=45, penalised account) median 1.9K / mean 10.5K; YouTube return era median 646. Industry: median IG reel 344 views (highviz 2026, 346 reels); TikTok 1–5K-follower accounts 350 views/post (Socialinsider 2025 via heistbrain). Central sits at 1/13 of the YM launch-era median because we post 6/day/page, run under the 2026 AI-label regime, and YM proves fresh distribution can collapse to near zero.'),
 ('v_growth','Growth in mean views per post per 30 days of page age',1.6,'x','Assumptions A (vg). Capped by v_cap.'),
 ('v_cap','Cap on mean views per post (central)',40000,'views','Assumptions A (vcap): ~1/3 of YM main-page median because 40+ posts/day cannibalize.'),
 ('plat_mult',"Platform view multiplier (IG/FB/TT/YT)",{'IG':1.3,'FB':1.0,'TT':0.7,'YT':0.5},'x','ASSUMPTION from POSTDB: in Sep 2026 the same asset did 40–100× better on IG than on TikTok/YouTube; FB assumed at par for a 55+ buyer (FB Reels reach rate 0.55% of followers vs IG 4.1%, Socialinsider Aug 2026, but new-page reach is discovery, not followers).'),
 ('v2v_dm','Views → landing visitors, IG/FB (keyword comment → DM → link)',0.003*0.85*0.30*1.25,'%','Assumptions B: keyword comments 0.3% of views (YM onion reel 1.03%, average far lower) × DM open 85% (chatautodm 2026: 80–90%) × DM CTA click 30% (25–45%) × 1.25 bio/pinned-link uplift. = 0.0956% of views.'),
 ('v2v_bio','Views → landing visitors, TikTok/YouTube (bio link only; no US comment triggers on TikTok)',0.02*0.015,'%','ASSUMPTION: profile visits 2% of views × bio-link CTR 1.5% (LinkDash 2026 benchmark: bio link CTR 1–2% of profile visits, via topmate.io). = 0.03% of views.'),
 ('scen_mult','Organic scenario multiplier on views (conservative / central / upside / breakout)',{'conservative':0.35,'central':1.0,'upside':1.75,'breakout':3.0},'x','Conservative = small-account medians (≈2.1K mean/post). Central = 6K. Upside = 10.5K (still 1/7 of YM launch-era TikTok median). Breakout = 18K (the existing §8 "3× base organic" lever; 1/4 of YM launch median, 1/50 of its mean).'),
 ('wl_rate','Runway: landing visitor → waitlist opt-in (email + web push)',0.45,'%','ASSUMPTION between two benchmarks: cold waitlist pages convert a median 11% of visitors (Waitlister 2026) and 15–40% with an incentive (craftuplearn); DM-originated flows that ask for the email inside the DM capture ~80% (Claire Bartholic case, creatorflow.so). Conservative 0.30, upside 0.60.'),
 ('c72','Waitlist → ebook buyer in the first 72 h after checkout opens',0.10,'%','Consumer waitlist → paying customer 10–15% (getwaitlist.com benchmarks); B2B >20%. Conservative 0.06, upside 0.15. Cell B multiplies by subB.'),
 ('c72_split','Share of the 72 h conversion landing on days 1 / 2 / 3',[0.5,0.3,0.2],'','ASSUMPTION: launch email + push + DM on day 1, reminder day 2, day 3 second reminder; no "doors close" copy (no fake scarcity).'),
 ('ctail','Waitlist → ebook buyer, days 4–14 (additional)',0.05,'%','ASSUMPTION: getwaitlist shows 12–15% click on update emails; half the 72 h rate over the next 11 days, decaying 15%/day.'),
 ('stale','Conversion loss per day of waitlist age (floor 0.70)',0.01,'%/day','ASSUMPTION: a 21-day-old opt-in converts ~80% as well as a fresh one.'),
 ('seed_age','Assumed age of an externally seeded waitlist on day 1',None,'days','Formula in the engine: runway ÷ 2 (collected evenly over the runway).'),
 ('eng_rate','Engaged viewers per view (retargeting audience)',0.043,'%','highviz 2026: median engagement per view 4.3%.'),
 ('eng_window','Retargeting audience window',30,'days','Meta engagement custom audiences: modelled at 30 days.'),
 ('win_share','Share of posts that beat the page baseline enough to boost (rel ≥ 2)',0.15,'%','POSTDB: 25% of YM TikToks have rel ≥ 2.79 (p75), 10% ≥ 13.7; 15% used.'),
 ('boost_per_win','Max boost spend per winning post',250,'$','ASSUMPTION: a winner gets $250 over its first 24 h; supply of winners caps boost spend.'),
 ('boost_eff','Boosted-organic cost per landing visitor vs cold Meta',0.65,'x','TikTok Spark Ads vs non-Spark: −4% CPM, +43% conversion rate, +142% engagement (TikTok via billo.app); Meta partnership ads: lift studies only, no published CPM/CPA delta. 0.65 central; 0.80 conservative.'),
 ('rt_eff','Retargeting cost per landing visitor vs cold Meta',0.50,'x','ASSUMPTION: engaged-viewer and waitlist-non-buyer retargeting converts 2–3× cold; 0.50 central, 0.70 conservative.'),
 ('rt_per_aud','Retargeting spend capacity per engaged person per day',0.03,'$','ASSUMPTION: ~2 impressions/person/day at a ~$15 CPM.'),
 ('boost_share','Share of the daily cap reserved for boosts (rest retargets)',0.6,'%','ASSUMPTION.'),
 ('cap_tiers','Daily paid cap tiers modelled',[0,500,1500,3000],'$/day','Task spec.'),
 ('exist','Ad account: 0 = fresh Strong Years account (learning multiplier 1.35 days 1–7, no history discount)',0,'1/0','BLITZ CANON: never run Strong Years ads from FA accounts; K9SUPPS account only if it has purchase history and no restricted-health history. Modelled fresh.'),
]
ORG = {k:v for k,_,v,_,_ in ORG_INPUTS}

SOURCES = [
 ('Shopify dev docs — post-purchase product offers, Limitations', 'https://shopify.dev/docs/apps/build/checkout/product-offers — post-purchase page not shown for installment/wallet services (Klarna, Affirm, AfterPay, Apple Pay, Amazon Pay, Google Pay), gift cards or "any payment method other than a credit card", third-party providers that retain CVV (Braintree, PayPal Payments Pro…), orders in a non-default currency or with duties, local delivery, orders < $0.50, non-Online-Store channels; "If the customer\'s checkout results in the creation of an order without a shipping address, then you can\'t add a subscription to the order using post-purchase. For example, a customer might have bought only digital products"; post-purchase extensions are in beta: a live store must request access'),
 ('Shopify dev docs — Create a post-purchase subscription', 'https://shopify.dev/docs/apps/build/checkout/product-offers/create-a-post-purchase-subscription — a subscription CAN be added post-purchase to a one-time order (not to an order that already has one; a one-time line cannot be converted); explicit BuyerConsent required before the payment method is vaulted'),
 ('Rebuy / UpsellPlus help — post-purchase considerations', 'https://help.rebuyengine.com/en/articles/6706477 ; https://help.upsellplus.com/en/article/selling-subscriptions-on-the-post-purchase-page-limitations-wyh5nj/ — "Post-Purchase offers will display for customers who check out using Shop Pay"; orders without a shipping address (digital products, local pickup) are ineligible for post-purchase subscription offers'),
 ('Shopify pricing (shopify.com/pricing, read Oct 1 2026)', 'Basic $29/mo (annual) or $39/mo monthly, online card rate 2.9% + 30¢ USD, 2% extra on third-party gateways; Grow 2.7% + 30¢; Advanced 2.5% + 30¢. Shopify Subscriptions app is free. Craftshift May 2026 breakdown agrees.'),
 ('Shopify Help — Shopify Payments payout timing', 'https://help.shopify.com/en/manual/payments/shopify-payments/payouts/payout-timing — US payouts settle in 3 business days (up to 5 for new merchants); reserves "may be retained to address potential losses from chargebacks or refunds"; account reviews can pause payouts. Modelled: 5-day lag and a 10% / 90-day reserve (conservative, as in the Blitz sheet).'),
 ('EasyApps — Shopify upsell conversion benchmarks (Mar 2026)', 'https://easyappsecom.com/guides/shopify-upsell-conversion-benchmarks — post-purchase upsell acceptance 3–8%; one-click post-purchase 5–12%; incremental revenue per order $8–18 (vendor data)'),
 ('Zipify — How to upsell on Shopify in 2026', 'https://zipify.com/blog-how-to-upsell-in-2026/ — OCU merchants average a 16.2% post-purchase conversion rate; under-optimised stores ~4%; 62.1% of upsell revenue is post-purchase (vendor data, 15,000+ stores)'),
 ('CartFlows — Tripwire funnel benchmarks (2026)', 'https://cartflows.com/blog/tripwire-funnel/ — tripwire page 1.5–5% cold, 8–15% warm; order bumps 20–40%; upsell acceptance 5–10% cold, 15–25% warm; email lists convert 1–2% to paid'),
 ('Zanfia — Using an ebook as a tripwire (2026)', 'https://zanfia.com/blog/using-an-ebook-as-a-tripwire-the-low-ticket-funnel-that-builds-buyers-2026/ — 5–15% of new subscribers buy the tripwire; $10–30 sweet spot; order bump 30–50%; no membership-continuity rate published'),
 ('Yang Mun post database', '/home/claude/rebuild/data/posts.csv, POSTDB_FINDINGS.md (244 posts; TikTok first 15 days n=15 median 76.8K mean 953K; days 16–30 n=5 median 47.3K; days 270–400 n=45 median 1.9K mean 10.5K; YouTube days 270–400 n=21 median 646; ratio-to-median quantiles p25 0.56 / p75 2.79 / p90 13.7)'),
 ('highviz.io Instagram Reels Report 2026 (346 reels)', 'https://www.highviz.io/instagram-reels-report/ — median reel 344 views (IQR 141–1,568), engagement per view 4.3%'),
 ('Socialinsider social media reach Aug 2026 (872,075 posts)', 'https://www.socialinsider.io/blog/social-media-reach/ — IG reach rate 4.90% (1–5K followers 6.65%), FB 1.80%; IG Reels 4.10%, FB Reels 0.55%'),
 ('Socialinsider 2025 TikTok benchmarks via heistbrain', 'https://heistbrain.com/benchmarks/tiktok-views.html — 1–5K followers 350 views/post, 5–10K 945, 10–50K 3,240, 100K–1M 34,900'),
 ('LinkDash 2026 via topmate.io', 'https://topmate.io/blog/instagram-creator-earnings-statistics-2026 — bio link CTR 1–2% of profile visits'),
 ('creatorflow.so comment-to-DM case studies', 'https://creatorflow.so/blog/comment-to-dm-automation-case-studies/ — DM open ~90%; DM-flow email capture 80%'),
 ('chatautodm.com Instagram automation statistics 2026', 'DM open 80–90%, DM CTA click 25–45%'),
 ('Waitlister 2026 statistics', 'https://waitlister.me/growth-hub/blog/waitlist-and-product-launch-statistics — median waitlist page converts 11% of visitors'),
 ('getwaitlist.com benchmarks', 'https://getwaitlist.com/blog/waitlist-benchmarks-conversion-rates — consumer waitlist → customer 10–15%; update emails 45–50% open, 12–15% click'),
 ('TikTok Spark Ads vs non-Spark (via billo.app)', 'https://billo.app/blog/partnership-ad-performance/ — −4% CPM, +43% conversion rate, +142% engagement'),
 ('Blitz sheet shared inputs', 'economics.xlsx Assumptions/Blitz (CPM $18 Triple Whale H&W; renewal curve 62/50/43/38.5/35 then −5%/mo; Adapty trial→paid 42.2% used only as a comparator for renB1)'),
]

# ----------------------------------------------------------------------------------------------
# Run definitions
# ----------------------------------------------------------------------------------------------
# CANON UPDATE 3 (Oct 1 2026): cell B ("$12 today = books + first month, then $25/mo", one subscription purchase on the
# founding plan + the STARTER12 first-payment-only code) is the LAUNCH DEFAULT; cell A (books only, founding offer on the
# thank-you page + 3 emails; the one-click post-purchase app stays scaffolded but OFF) is the test cell.
BASE = dict(price=25, cell='B', fe_price=12, sp_day=1, sp0=0, g=0.0, sp_max=0, post30=1, exist=0, sh_day=3, sh_max=0, sh_post30=1, aff=1,
            unig=20000, k9=10000, sh_ctr=0.004, lpv=0.85, cpm_mult=1.10, badj=0.935, sms_on=0,
            cvr_org=0.05, cvr_cold=0.03, cvr_warm=0.08, elig_addr=0.0, elig_pay=0.70, pp_take=0.12, later_take=0.04, subB=0.70, renB1=0.50, ref_pp=0.12,
            ann_mode=1, ann_start=35, ann_take=0.05, ann_price=249, save_take=0.25, down_share=0.5, pause_ret=0.5,
            runway=14, scen='central', posts_max=6, wl_rate=0.45, c72=0.10, ctail=0.05, seed_wl=0,
            cap=0, boost_eff=0.65, rt_eff=0.50, gate_on=0, gate_sp=8000, gate_post30=0.5, gate_sh=4)
UPS  = dict(BASE, lpv=1.0, cpm_mult=1.0, ref_pp=0.10, scen='upside', posts_max=9, wl_rate=0.60, c72=0.15, ctail=0.07, sh_ctr=0.006,
            cvr_org=0.08, cvr_cold=0.04, cvr_warm=0.12, pp_take=0.20, later_take=0.07, elig_pay=0.85, subB=0.85, renB1=0.58)
RUNS = [
 dict(BASE, name='R20 Organic-first, central, cell B (LAUNCH DEFAULT): $12 ebook sales page → "$12 today = books + first month, then $25/mo" as one subscription purchase (0.70 × the one-time ebook purchase rate; 50% survive the first $25 renewal); 7 pages ramping from 3, 6 posts/day/page, 14-day runway waitlist, warm lists 20K/10K, affiliates; no media'),
 dict(UPS,  name='R21 Organic-first, upside, cell B: upside conversion inputs (ebook 8%, subB 0.85, first renewal 58%), 9 posts/day/page, organic ×1.75, waitlist 60% / 72 h 15%; no media'),
 dict(BASE, name='R22 Organic-first, central, cell A (TEST CELL): $12 one-time ebook → founding offer on the thank-you page + 3 emails (4% later catches); the one-click post-purchase page is OFF at launch (12% of eligible orders only if it is switched on and approved); otherwise R20', cell='A', pp_take=0.0),
 dict(BASE, name='R23 = R20 + boost/retarget cap $1,500/day + 2 shoutouts/day from day 3', cap=1500, sh_max=2),
 dict(BASE, name='R24 = R23 + graduation to cold Meta when the §11 day-10 gate passes ($8K/day days 11–30 then $4K, 4 shoutouts/day). On central cell-B inputs the gate FAILS (cold Meta ≈ $102 per net paying member net of ebook profit vs a $68 12-month contribution), so R24 = R23. The gate passes only on upside cell-B inputs (sensitivity table)', cap=1500, sh_max=2, gate_on=1),
 dict(BASE, name='R25 = R20 with the $7 ebook cell (conversion ×1.31)', fe_price=7),
 dict(BASE, name='R26 = R20 with the $15 ebook cell (conversion ×0.89)', fe_price=15),
]

def Sk(s,k): return s['S'][k] if k<=5 else s['S'][5]*(1-s['churn'])**(k-5)
def fe_cvr(r, base, l=LAD): return base*(12.0/r['fe_price'])**l['fe_elas']
def pp_rate(r, l=LAD): return r['elig_addr']*r['elig_pay']*r['pp_take']*(r['fe_price']/12.0)**l['pp_price_elas']
def fe_unit(r, s=SH, l=LAD):
    """Front-end gross profit per ebook order (price + bumps, net of refunds, fees, kit COGS)."""
    gross=r['fe_price']+l['bumps']
    return gross*(1-s['fe_ref'])*(1-s['pct'])-s['fix']-s['bump29_take']*s['kit_cogs']
def contrib(r, price, stream, s=SH, l=LAD, months=12):
    """Contribution per paying member over `months` renewals (kill-rule / graduation line)."""
    pr=price*s['realized']
    nm=pr*(1-s['sub_ref']-s['pct']-s['bill']-s['cbB'])-s['fix']-s['cogs']-s['varm']
    if stream=='A':
        d0=pr*(1-s['pct']-s['bill'])-s['fix']-s['cogs']-s['varm']
        surv=[Sk(s,k)*r['badj'] for k in range(1,months)]
    else:
        d0=0.0  # first cycle paid inside the $12 ebook order (counted in fe_unit)
        surv=[r['renB1']*Sk(s,k)/Sk(s,1) for k in range(1,months)]
    return d0+nm*sum(surv)

def cold_cpv(r, sp, d, s=SH):
    """Cost per landing visitor on cold Meta at spend sp on day d (Blitz-sheet CPM/CTR/click-loss chain, no quiz)."""
    return s['cpm']*r['cpm_mult']*(1-s['disc']*r['exist'])/(1000*s['ctr'])/r['lpv']*max(1,sp/s['sref_d'])**s['pen']*((s['learn_exist'] if r['exist'] else s['learn_new']) if d<=7 else 1)

def members_per_order(r):
    """Paying members created per ebook order (cell A) net of refunds; cell B: members per purchase."""
    if r['cell']=='A':
        pp=pp_rate(r); return (pp+(1-pp)*r['later_take'])*(1-r['ref_pp'])
    return 1.0

def gate_pass(r, s=SH):
    """BLITZ.md §11 graduation: cold Meta at $8K/day must deliver a net paying member for ≤ its 12-month contribution,
    net of the front-end gross profit it carries. Returns (pass, cost per net member, line)."""
    cpv=cold_cpv(r, 8000, 10, s)
    cvr=fe_cvr(r, r['cvr_cold'])
    if r['cell']=='A':
        orders=cvr; mem=orders*members_per_order(r)
        cost=(cpv*(1+s['media']) - orders*fe_unit(r))/mem
        line=contrib(r, r['price'], 'A')
    else:
        orders=cvr*r['subB']; mem=orders*(1-s['fe_ref'])
        cost=(cpv*(1+s['media']) - orders*fe_unit(r))/mem
        line=contrib(r, r['price'], 'B')
    return (1 if cost<=line else 0), cost, line

# ----------------------------------------------------------------------------------------------
# Organic engine (unchanged)
# ----------------------------------------------------------------------------------------------
def organic_day(r, t, o=ORG, s=SH):
    if r.get('mx'): return organic_day_max(r, t, o, s)   # R30–R35 family (Organic-max); R20–R26 never set 'mx'
    mult = o['scen_mult'][r['scen']]
    views = visitors = posts = 0.0; pages = 0
    for pd_, plat in zip(o['page_days'], o['page_plat']):
        age = t - (pd_-1)
        if age < 0: continue
        pages += 1
        cad = o['posts_d1'] + (r['posts_max']-o['posts_d1'])*min(1.0, age/o['posts_ramp'])
        vpp = min(o['v_base']*o['v_growth']**((age-15)/30.0), o['v_cap'])*o['plat_mult'][plat]*mult
        vpp *= (cad/6.0)**(-0.3) if cad>6 else 1.0
        pv = cad*vpp
        rate = o['v2v_dm'] if plat in ('IG','FB') else o['v2v_bio']
        views += pv; posts += cad; visitors += pv*rate
    return dict(views=views, visitors=visitors, posts=posts, pages=pages)

# ----------------------------------------------------------------------------------------------
# Daily model
# ----------------------------------------------------------------------------------------------
def run(r, s=SH, o=ORG, l=LAD, days=360):
    r = dict(r); R = r['runway']; cellA = r['cell']=='A'
    gp, gcost, gline = gate_pass(r, s) if r['gate_on'] else (0, None, None)
    H={}; rows=[]; pre=[]
    g=lambda k,d: H.get(d,{}).get(k,0)
    # ---- runway: waitlist collection and opex before day 1 ----
    wl_cohorts=[]; cash=0.0; runway_cost=0.0; wl_org=0.0
    for t in range(R):
        od=organic_day(r,t,o,s)
        wl=od['visitors']*s['lp_org']*r['wl_rate']; wl_org+=wl
        wl_cohorts.append((R-t, wl))
        cost=(s['fixed']+s['shop_plan'])/30 + od.get('cost_posts',od['posts'])*s['cost_post'] + od.get('xcost',0.0)
        cash-=cost; runway_cost+=cost
        pre.append(dict(d=-(R-1-t), views=od['views'], visitors=od['visitors'], posts=od['posts'], pages=od['pages'], waitlist=wl, wl_cum=wl_org, cash=cash))
    if r['seed_wl']>0: wl_cohorts.append((R/2.0, r['seed_wl']))
    W0=sum(w for _,w in wl_cohorts)
    # waitlist -> ebook-buyer schedule (one-time-ebook-equivalent purchase rate; cell B × subB)
    wl_sched={}
    for age,w in wl_cohorts:
        sf=max(0.70, 1-o['stale']*age)
        for i,sh in enumerate(o['c72_split']): wl_sched[i+1]=wl_sched.get(i+1,0)+w*r['c72']*sf*sh
        tail=[0.85**i for i in range(11)]; ts=sum(tail)
        for i in range(11): wl_sched[4+i]=wl_sched.get(4+i,0)+w*r['ctail']*sf*tail[i]/ts
    pp=pp_rate(r); lsplit=l['later_split']
    actB=actBv=actP=actPv=ann=ess=paused=resbal=cumaff=cumV=0.0; eng_hist=[]; wl_nonbuy=W0
    cum_media=0.0; cum_found=0.0; cum_fe=0.0
    for d in range(1,days+1):
        t=R+d-1
        od=organic_day(r,t,o,s)
        # ---- paid plan: cold Meta only after the gate ----
        if r['gate_on'] and d>10 and gp:
            plan=r['gate_sp'] if d<=30 else r['gate_sp']*r['gate_post30']; shmax=r['gate_sh']
        else:
            shmax=r['sh_max']; plan=0.0
            if r['sp_max']>0 and d>=r['sp_day']:
                plan=min(r['sp_max'],r['sp0']*(1+r['g'])**(d-r['sp_day'])) if d<=30 else r['post30']*min(r['sp_max'],r['sp0']*(1+r['g'])**(30-r['sp_day']))
        sp_cold=plan
        winners=od['posts']*o['win_share']; boost_avail=winners*o['boost_per_win']
        sp_boost=min(r['cap']*o['boost_share'], boost_avail)
        eng_hist.append(od['views']*o['eng_rate']); aud=sum(eng_hist[-o['eng_window']:])+wl_nonbuy
        sp_rt=min(r['cap']-sp_boost, aud*o['rt_per_aud'])
        sp=sp_cold+sp_boost+sp_rt
        cpv=cold_cpv(r, max(sp,1), d, s)
        v_cold=sp_cold/cpv if sp_cold>0 else 0
        v_boost=sp_boost/(cpv*r['boost_eff']) if sp_boost>0 else 0
        v_rt=sp_rt/(cpv*r['rt_eff']) if sp_rt>0 else 0
        shp=(min(shmax,max(0,d-r['sh_day']+1)*s['sh_ramp']) if shmax>0 else 0)*(1 if d<=30 else r['sh_post30'])
        v_sh=shp*s['sh_reach']*r['sh_ctr']*r['lpv']
        L=r['unig']+r['k9']*s['k9mult']
        v_warm=L*(s['email_w'].get(d,0)*s['deliv']*s['open']*s['ctor']+r['sms_on']*s['sms_w'].get(d,0)*s['sms_share']*s['sclick'])*s['wlp']
        naff=min(s['aff_cap'],max(0,d-s['aff_start']+1)*s['aff_per_day']) if r['aff'] else 0
        v_aff=naff*s['aff_visitors']
        v_org=od['visitors']*s['lp_org']
        visitors=v_org+v_warm+v_sh+v_aff+v_cold+v_boost+v_rt
        # ---- ebook orders (one-time-equivalent rate), by source ----
        c_org=fe_cvr(r,r['cvr_org'])*r.get('intent_up',1.0); c_cold=fe_cvr(r,r['cvr_cold']); c_warm=fe_cvr(r,r['cvr_warm'])
        E_src=dict(org=v_org*c_org, warm=v_warm*(1-s['gift'])*c_warm, sh=v_sh*c_cold*1.2, aff=v_aff*c_warm, cold=v_cold*c_cold, boost=v_boost*c_org, rt=v_rt*c_org, wl=wl_sched.get(d,0))
        gifts=v_warm*s['gift']*c_warm
        E1=sum(E_src.values())
        cap_d=(s['cap1']+(s['cap2'] if d>=s['proc2_day'] else 0))/30
        capf=min(1,cap_d/g('gross',d-1)) if g('gross',d-1)>0 else 1
        wl_nonbuy=max(0.0, wl_nonbuy-wl_sched.get(d,0))
        # founding price for today's cohort
        pB=r['price'] if cum_found<s['found_cap'] else s['std_price']
        if cellA:
            E=E1*capf; P=0.0
            accept=E*pp                                  # one-click post-purchase, charged today
            later=sum(g('E_rem',d-i)*r['later_take']*lsplit[i-1] for i in range(1,8) if d-i>=1)
            B=accept+later
        else:
            E=0.0; P=E1*r['subB']*capf; B=0.0
        cum_found+=B+P
        refB=g('B',d-s['reflag'])*r['ref_pp'] if d>s['reflag'] else 0
        refBv=refB*g('pB',d-s['reflag']) if d>s['reflag'] else 0
        refP=g('P',d-s['reflag'])*s['fe_ref'] if d>s['reflag'] else 0
        # ---- renewals (both streams), annual, saves ----
        lostB=renB=lostBv=renBv=lostP=renP=lostPv=renPv=0.0
        Sb=lambda k: Sk(s,k)*r['badj'] if k>0 else 1
        Sp=lambda k: (r['renB1']*Sk(s,k)/Sk(s,1)) if k>0 else 1
        take=r['ann_take']; st=r['ann_start']
        for k in range(1,13):
            dd=d-30*k
            if dd<1: continue
            fk=(1-take) if (k>=2 and d-30*k+35>=st) else 1
            NBc=g('B',dd)*(1-r['ref_pp']); pBc=g('pB',dd)
            lb=NBc*fk*(Sb(k-1)-Sb(k)); rb=NBc*fk*Sb(k); lostB+=lb; renB+=rb; lostBv+=lb*pBc; renBv+=rb*pBc
            NPc=g('P',dd)*(1-s['fe_ref'])
            lp_=NPc*fk*(Sp(k-1)-Sp(k)); rp=NPc*fk*Sp(k); lostP+=lp_; renP+=rp; lostPv+=lp_*pBc; renPv+=rp*pBc
        on=take if d>=st else 0
        annB=g('B',d-35)*(1-r['ref_pp'])*Sb(1)*on if d>35 else 0; annBv=annB*g('pB',d-35) if d>35 else 0
        annP=g('P',d-35)*(1-s['fe_ref'])*Sp(1)*on if d>35 else 0; annPv=annP*g('pB',d-35) if d>35 else 0
        annew=annB+annP
        saved=(lostB+lostP)*r['save_take']; sdown=saved*r['down_share']; spause=saved*(1-r['down_share'])
        ret=g('spause',d-60)*r['pause_ret'] if d>60 else 0
        pexit=g('spause',d-60) if d>60 else 0
        ess+= sdown - ess*s['ess_churn']/30
        paused+= spause - pexit
        actB+=B-refB-lostB-annB+ret*(1 if cellA else 0)
        actBv+=B*pB-refBv-lostBv-annBv+ret*pB*(1 if cellA else 0)
        actP+=P-refP-lostP-annP+ret*(0 if cellA else 1)
        actPv+=P*pB-refP*pB-lostPv-annPv+ret*pB*(0 if cellA else 1)
        ann+=annew
        members=actB+actP
        mrr=(actBv+actPv)*s['realized']+ess*s['ess_price']*s['realized']+ann*r['ann_price']/12
        # retained: young cohorts (≤30 days) × their renewal-1 survival
        youngB=sum(g('B',j)*g('pB',j) for j in range(max(1,d-29),d+1)); refdone=sum(g('B',j)*g('pB',j) for j in range(max(1,d-29),d-6))*r['ref_pp']
        youngP=sum(g('P',j)*g('pB',j) for j in range(max(1,d-29),d+1)); refdoneP=sum(g('P',j)*g('pB',j) for j in range(max(1,d-29),d-6))*s['fe_ref']
        retained=((actBv-(youngB-refdone))+youngB*(1-r['ref_pp'])*Sb(1))*s['realized']+((actPv-(youngP-refdoneP))+youngP*(1-s['fe_ref'])*Sp(1))*s['realized']+ess*s['ess_price']*s['realized']+ann*r['ann_price']/12
        # ---- cash ----
        fe_rev=(E+P)*r['fe_price']; bump_rev=(E+P)*l['bumps']
        firstB=B*pB*s['realized']
        gross=fe_rev+bump_rev+firstB+renBv*s['realized']+renPv*s['realized']+gifts*s['gift_price']+annew*r['ann_price']+ess*s['ess_price']*s['realized']/30+ret*pB*s['realized']
        refunds=(fe_rev+bump_rev)*s['fe_ref']+refBv*s['realized']+(firstB+renBv*s['realized']+renPv*s['realized'])*s['sub_ref']
        txn=(E+P)*s['txn_fe']+B+renB+renP+gifts+annew+ess/30+ret   # conservative: the post-purchase accept is a second capture, so it carries its own 30¢
        cbn=(B+renB+renP+annew+ret)*s['cbB']+(E+P)*s['cbFE']
        fees=gross*(s['pct']+s['bill'])+txn*s['fix']+cbn*s['cb_fee']+(cbn*gross/max(txn,1e-9) if txn else 0)
        resadd=gross*s['reserve']; resrel=g('resadd',d-s['res_days']) if d>s['res_days'] else 0
        resbal+=resadd-resrel
        netin=gross-refunds-fees-resadd+resrel
        receipts=g('netin',d-s['lag']) if d>s['lag'] else 0
        cumaff+=E_src['aff']; cumV+=E1
        mem_all=members+ess+ann
        comm=(cumaff/cumV if cumV else 0)*mrr*s['comm']/30
        costs=sp*(1+s['media'])+shp*s['sh_cost']+comm+(s['fixed']+s['shop_plan'])/30+od.get('cost_posts',od['posts'])*s['cost_post']+od.get('xcost',0.0)+mem_all*(s['cogs']+s['varm'])/30+(E+P)*s['bump29_take']*s['kit_cogs']
        net=receipts-costs
        cash+=net
        cum_media+=sp+shp*s['sh_cost']; cum_fe+=fe_rev+bump_rev
        paid_orders=E_src['sh']+E_src['cold']+E_src['boost']+E_src['rt']
        paid_share=paid_orders/E1 if E1 else 0
        paid_new=paid_share*((B*(1-r['ref_pp'])) if cellA else P*(1-s['fe_ref']))
        cac=((sp*(1+s['media'])+shp*s['sh_cost'])-paid_orders*fe_unit(r))/paid_new if paid_new>0 else 0
        H[d]=dict(E=E,E_rem=(E*(1-pp) if cellA else 0),P=P,B=B,pB=pB,gross=gross,netin=netin,resadd=resadd,spause=spause)
        rows.append(dict(d=d,pages=od['pages'],posts=od['posts'],views=od['views'],visitors=visitors,v_org=v_org,v_wl=0,wl_buy=E_src['wl'],v_warm=v_warm,v_sh=v_sh,v_aff=v_aff,
                         sp_cold=sp_cold,sp_boost=sp_boost,sp_rt=sp_rt,sp=sp,v_paid=v_cold+v_boost+v_rt,shp=shp,orders=E+P,E=E,P=P,accept=(accept if cellA else 0),later=(later if cellA else 0),
                         B=B,pB=pB,refB=refB,fe_rev=fe_rev+bump_rev,
                         members=mem_all,mrr=mrr,ret=retained,gross=gross,receipts=receipts,costs=costs,net=net,cash=cash,res=resbal,cum_media=cum_media,cum_fe=cum_fe,cac=cac))
    info=dict(W0=W0, wl_org=wl_org, runway_cost=runway_cost, gate=gp, gate_cost=gcost, gate_line=gline, pp=pp, mpo=members_per_order(r), fe_unit=fe_unit(r),
              contribA=contrib(r,r['price'],'A'), contribB=contrib(r,r['price'],'B'))
    return rows, pre, info

def summ(rows, pre, info):
    g=lambda d,k: rows[d-1][k]
    lo=min(range(len(rows)),key=lambda i:rows[i]['cash'])
    out=dict(W0=info['W0'],wl_org=info['wl_org'],runway_cost=info['runway_cost'],gate=info['gate'],gate_cost=info['gate_cost'],gate_line=info['gate_line'],
             m4=g(4,'mrr'),m14=g(14,'mrr'),m30=g(30,'mrr'),m90=g(90,'mrr'),m180=g(180,'mrr'),m360=g(360,'mrr'),ret30=g(30,'ret'),
             members30=g(30,'members'),orders30=sum(x['orders'] for x in rows[:30]),fe30=g(30,'cum_fe'),fe90=g(90,'cum_fe'),fe180=g(180,'cum_fe'),
             c4=g(4,'cash'),c14=g(14,'cash'),c30=g(30,'cash'),c90=g(90,'cash'),c180=g(180,'cash'),c360=g(360,'cash'),
             low=rows[lo]['cash'],lowday=lo+1,media30=g(30,'cum_media'),media180=g(180,'cum_media'),
             views30=sum(x['views'] for x in rows[:30]),visitors30=sum(x['visitors'] for x in rows[:30]))
    for t in (10000,50000,100000,500000):
        out[f'd{t//1000}']=next((x['d'] for x in rows if x['mrr']>=t),999)
    nets=[x['net'] for x in rows]
    out['cfpos']=next((i+1 for i in range(len(nets)-13) if all(x>0 for x in nets[i:i+14])),999)
    out['beday']=next((x['d'] for x in rows if x['d']>30 and x['cash']>=0),999)
    return out

def solve_seed(r, target, day, key='seed_wl', hi=2_000_000):
    def mrr_at(x):
        rr=dict(r); rr[key]=x; rows,_,_=run(rr, days=day); return rows[day-1]['mrr']
    if mrr_at(0)>=target: return 0
    if mrr_at(hi)<target: return None
    lo_,hi_=0,hi
    for _ in range(40):
        mid=(lo_+hi_)/2
        if mrr_at(mid)>=target: hi_=mid
        else: lo_=mid
    return hi_

MILESTONES=((10000,4),(50000,14),(100000,30))
SENS=[('Organic conservative (views ×0.35)',dict(scen='conservative')),('Organic upside (×1.75)',dict(scen='upside')),('Organic breakout (×3.0)',dict(scen='breakout')),
 ('Organic at Yang Mun launch-era per-post reach (×12.8: every post averages YM\'s first-15-day TikTok median of 76.8K)',dict(scen='ym')),
 ('9 posts/day/page',dict(posts_max=9)),('Views → visitors (IG/FB DM chain) −30%',dict(_v2v=0.7)),('Views → visitors +30%',dict(_v2v=1.3)),
 ('Ebook conversion 3% organic (vs 5%)',dict(cvr_org=0.03)),('Ebook conversion 8% organic',dict(cvr_org=0.08)),
 ('Cell A (test cell) instead of B: books only, thank-you page + 3 emails (4% later catches), post-purchase OFF',dict(cell='A',pp_take=0.0)),
 ('Cell A with the one-click post-purchase page ON and approved AND the ebook variant changed to require a shipping address (12% of 70% eligible orders)',dict(cell='A',pp_take=0.12,elig_addr=1.0)),
 ('Cell A, post-purchase ON, ebook left as a pure digital product (catalog default, requiresShipping false): the post-purchase subscription cannot fire',dict(cell='A',pp_take=0.12,elig_addr=0.0)),
 ('Cell A, post-purchase ON + shipping address, take 20% of 85% eligible',dict(cell='A',pp_take=0.20,elig_pay=0.85,elig_addr=1.0)),
 ('Cell A later catches 2% (vs 4%)',dict(cell='A',pp_take=0.0,later_take=0.02)),('Cell A later catches 7%',dict(cell='A',pp_take=0.0,later_take=0.07)),
 ('Cell B subB 0.55 (vs 0.70)',dict(subB=0.55)),('Cell B subB 0.85',dict(subB=0.85)),('Cell B renewal-1 42% (trial-like, vs 50%)',dict(renB1=0.42)),('Cell B renewal-1 58% (charge-today month-1)',dict(renB1=0.58)),
 ('Ebook $7',dict(fe_price=7)),('Ebook $15',dict(fe_price=15)),('Founding price $30',dict(price=30)),
 ('Membership refunds 10% (vs 12%)',dict(ref_pp=0.10)),
 ('Waitlist opt-in 30% (vs 45%)',dict(wl_rate=0.30)),('Waitlist opt-in 60%',dict(wl_rate=0.60)),('Waitlist 72 h conversion 6% (vs 10%)',dict(c72=0.06)),('Waitlist 72 h conversion 15%',dict(c72=0.15)),
 ('Lists 0 / 0 (vs 20K / 10K placeholders)',dict(unig=0,k9=0)),('Unignorable 100K',dict(unig=100000)),('Unignorable 100K + K9SUPPS 50K',dict(unig=100000,k9=50000)),('Unignorable 250K',dict(unig=250000)),
 ('Runway 7 days',dict(runway=7)),('Runway 21 days',dict(runway=21)),
 ('Seeded day-1 waitlist 10K',dict(seed_wl=10000)),('Seeded day-1 waitlist 25K',dict(seed_wl=25000)),('Seeded day-1 waitlist 50K',dict(seed_wl=50000)),('Seeded day-1 waitlist 100K',dict(seed_wl=100000)),
 ('Boost/retarget cap $500/day',dict(cap=500)),('Cap $1,500/day',dict(cap=1500)),('Cap $3,000/day',dict(cap=3000)),('Boost efficiency 0.80 (vs 0.65) at cap $1,500',dict(cap=1500,boost_eff=0.80,rt_eff=0.70)),
 ('Shoutouts 2/day',dict(sh_max=2)),('Shoutouts 4/day',dict(sh_max=4)),('No affiliates',dict(aff=0)),
 ('Shopify Payments reserve 0% (vs 10% / 90 days)',dict(_reserve=0.0)),('Annual take 10% (vs 5%)',dict(ann_take=0.10)),
 ('§11 gate on: cell B with upside conversion inputs (subB 0.85, renewal-1 58%, cold ebook CVR 4%) → gate PASSES → cold Meta $8K/day days 11–30, $4K after, 4 shoutouts/day',dict(gate_on=1,subB=0.85,renB1=0.58,cvr_cold=0.04,cvr_org=0.08,cvr_warm=0.12)),
 ('§11 gate on: cell A (post-purchase ON + shipping address) with upside conversion inputs → gate FAILS (cold cost per net member ≈ $148 vs $101)',dict(gate_on=1,cell='A',cvr_cold=0.04,cvr_org=0.08,cvr_warm=0.12,pp_take=0.20,later_take=0.07,elig_pay=0.85,elig_addr=1.0))]

def run_case(base, ch):
    o=dict(ORG); o['scen_mult']=dict(ORG['scen_mult'], ym=12.8)
    s=dict(SH); ch=dict(ch)
    if '_v2v' in ch: o['v2v_dm']=ORG['v2v_dm']*ch.pop('_v2v')
    if '_reserve' in ch: s['reserve']=ch.pop('_reserve')
    r=dict(base,**ch); rows,pre,info=run(r,s=s,o=o); return summ(rows,pre,info)

def main(write_json=None):
    res=[]
    for r in RUNS:
        rows,pre,info=run(r); res.append((r,rows,pre,info,summ(rows,pre,info)))
    print(f"{'run':6s} {'W0':>7s} {'d4':>7s} {'d14':>7s} {'d30':>7s} {'d90':>7s} {'d180':>7s} {'ret30':>7s} {'$10K':>5s} {'$50K':>5s} {'$100K':>5s} {'low':>7s} {'lowday':>6s} {'cf+':>4s} {'be':>4s} {'media30':>8s} {'fe30':>7s} {'gate':>4s}")
    for r,rows,pre,info,sm in res:
        print(f"{r['name'][:5]:6s} {sm['W0']:7.0f} {sm['m4']/1e3:7.1f} {sm['m14']/1e3:7.1f} {sm['m30']/1e3:7.1f} {sm['m90']/1e3:7.1f} {sm['m180']/1e3:7.1f} {sm['ret30']/1e3:7.1f} {sm['d10']:5d} {sm['d50']:5d} {sm['d100']:5d} {sm['low']/1e3:7.0f} {sm['lowday']:6d} {sm['cfpos']:4d} {sm['beday']:4d} {sm['media30']/1e3:8.1f} {sm['fe30']/1e3:7.1f} {sm['gate']:4d}")
        if r['gate_on']: print('   gate: cold cost per net member',round(info['gate_cost']),'vs 12-mo contribution',round(info['gate_line']))
    print('unit:', {k:round(v,2) for k,v in res[0][3].items() if k in ('pp','mpo','fe_unit','contribA','contribB')})
    print('\nRunway table / solver')
    rw=[]
    for base,nm in ((RUNS[0],'R20 central cell B'),(RUNS[1],'R21 upside cell B'),(RUNS[2],'R22 central cell A')):
        for R in (7,14,21):
            rr=dict(base, runway=R); rows,pre,info=run(rr); sm=summ(rows,pre,info)
            need={}; need_list={}
            for tgt,day in MILESTONES:
                need[f'{tgt}@{day}']=solve_seed(rr,tgt,day)
                need_list[f'{tgt}@{day}']=solve_seed(dict(rr,unig=0,k9=0),tgt,day,key='unig',hi=50_000_000)
            rw.append(dict(name=nm,R=R,summ=sm,need=need,need_list=need_list))
            print(nm,R,f"wl_org {sm['wl_org']:.0f} cost {sm['runway_cost']:.0f} d4 {sm['m4']:.0f} d14 {sm['m14']:.0f} d30 {sm['m30']:.0f}", {k:(round(v) if v is not None else None) for k,v in need.items()}, {k:(round(v) if v is not None else None) for k,v in need_list.items()})
    sens=[]
    for bi,bn in ((0,'R20'),(3,'R23')):
        b=res[bi][4]
        for nm,ch in SENS:
            sm=run_case(RUNS[bi],ch); sens.append(dict(base=bn,name=nm,summ=sm,d30_delta=sm['m30']-b['m30'],flag=abs(sm['m30']-b['m30'])>5000))
    ladder=[]
    for bi,bn in ((0,'central B'),(2,'central A'),(1,'upside B')):
        for cap in (0,500,1500,3000):
            for sh in (0,2,4):
                sm=run_case(RUNS[bi],dict(cap=cap,sh_max=sh))
                ladder.append(dict(scen=bn,cap=cap,sh=sh,summ=sm))
    # closest-at-least-cash combos: cell B central, amplification tiers, seeded waitlist solved per milestone
    combo=[]
    for cap,sh in ((0,0),(500,2),(1500,2),(3000,4)):
        for cell in ('B','A'):
            base=dict(RUNS[0] if cell=='B' else RUNS[2], cap=cap, sh_max=sh)
            row=dict(cell=cell,cap=cap,sh=sh)
            for tgt,day in MILESTONES:
                seed=solve_seed(base,tgt,day)
                row[f'seed_{tgt//1000}@{day}']=seed
                if seed is not None:
                    rows_,pre_,info_=run(dict(base,seed_wl=seed)); sm_=summ(rows_,pre_,info_)
                    row[f'low_{tgt//1000}@{day}']=sm_['low']; row[f'ret30_{tgt//1000}@{day}']=sm_['ret30']; row[f'm30_{tgt//1000}@{day}']=sm_['m30']; row[f'media30_{tgt//1000}@{day}']=sm_['media30']
            combo.append(row); print('combo',row)
    if write_json:
        json.dump(dict(combo=combo, runs=[dict(r=r,rows=rows,pre=pre,info=info,summ=sm) for r,rows,pre,info,sm in res], runway=rw, sens=sens, ladder=ladder,
                       inputs=[dict(key=k,label=l,value=v,unit=u,src=src) for k,l,v,u,src in ORG_INPUTS],
                       ladder_inputs=[dict(key=k,label=l,value=v,unit=u,src=src) for k,l,v,u,src in LADDER_INPUTS],
                       shared=SH, sources=SOURCES), open(write_json,'w'))
    return res, rw, sens, ladder

# ==============================================================================================
# LEGACY ORGANIC-MAX FAMILY OM30–OM35 (was 'R30–R35' until the Oct 2 2026 scale-plan round; SUPERSEDED by the R30–R36
# scale family at the end of this file; kept only because mrr_blitz_daily.csv columns r30_MRR…r35_posts were written from
# it and stay frozen). Oct 2 2026 client direction: NO paid media until MRR is real; $100K MRR within 30 days
# of checkout opening, organic only). 4 IG pages × 6 masters/day on the main feed + up to 20 Trial Reels per IG page
# per day (80/day), mostly spliced variants of the masters (new hook / first frame / on-screen text / length cut, each
# a distinct render under the >= 2-dimension rule, workers/growth/variants.py); winners auto-graduate to the feed.
# Facebook native 6 reels/day/page + 2 long cuts + text + photo; TikTok/YT/Threads/X distinct-cut reposts.
# R20–R26 above are untouched: run() only calls organic_day_max() when r['mx'] is set.
# Every input below is labelled; anything without a citation is an ASSUMPTION.
# ==============================================================================================
MX_INPUTS = [
 # key, label, central, upside, unit, source
 ('tr_ramp','Trial Reels per IG page per day by page age: days 0–6 / 7–13 / 14+',[3,6,20],[3,6,20],'reels','Client direction (3 → 6 → 20 by week 3); variants.py ramp 3/6/cap (max 20). Page age counts from the runway, so every page is at the cap by launch day 1 except the day-7 page.'),
 ('tr_cap','Hard cap on Trial Reels per page per day (the binding platform limit)',20,20,'reels','ASSUMPTION FLAG: Instagram publishes NO Trial Reel cap. API limit is 100 publishes/24 h incl. trials [ENGINE_100X S18]; one podcast claims caps "as low as five" with a 30-day trial block for exceeding them (ENGINE_NEXT50 N1, anecdotal). Sensitivity runs cap = 5.'),
 ('tr_days','Runway day each IG page goes live (4 IG pages, CANON 4)',[1,1,4,7],[1,1,4,7],'day','ASSUMPTION. In R30/R31 the feed layer is R20 (3 IG handles) plus the 4th CANON-4 IG page on day 7, so every trial page has a feed to graduate into.'),
 ('tr_rel','Views per Trial Reel ÷ views per main-feed reel of the same page at the same age, BEFORE variant decay',0.40,0.70,'x','ASSUMPTION. Nothing published: Meta says Trial Reels are shown to non-followers first and may be shared to followers if they perform within 72 h (ENGINE_NEXT50 N2); no reach figures exist. Industry median reel = 344 views (highviz 2026). A trial gets the non-follower test pool only, never follower reach: 0.40 central, 0.70 upside, 0.15 conservative.'),
 ('var_decay','Modular-variant decay: the n-th variant of one body (n ≥ 1; the master is n = 0) reaches var_decay^n of the master',0.6,0.6,'x','ASSUMPTION (client spec 0.6^n). No public evidence that hook-swapped variants of one body perform as distinct posts; Meta clusters near-identical creatives and demotes low-value edits [ENGINE_100X S3, S20, S44]. With 20 trials over 6 bodies (3.3 variants/body) the mean trial reaches 0.37 of n = 0.'),
 ('masters','Masters (bodies) per IG page per day',6,6,'bodies','Client direction / CANON 4.'),
 ('grad_rate','Share of Trial Reels that graduate (auto or by the 6 h composite) to the main feed',0.05,0.10,'%','ASSUMPTION. POSTDB: 25% of posts beat 2.79× the page median, 10% beat 13.7×; graduation needs a clear win on a noisy 6 h read, so 5% central (1 per page per day at 20 trials), 10% upside. Capped by the page\'s feed slots (6/day).'),
 ('grad_up','Views of a graduated winner on the feed ÷ a default master feed post',2.0,3.0,'x','ASSUMPTION. Selected on early data, so it regresses toward the mean: 2.0× central (below the POSTDB p75 rel 2.79), 3.0× upside. The graduate REPLACES a scheduled master (variants.py), so only the excess (grad_up − 1) is added.'),
 ('new_hook_share','Share of Trial Reels that carry a new hook (≈$0.45 each: new lip-sync + TTS); the rest are $0 frame / text / length variants',0.5,0.5,'%','COSTS.md §2b (12 trials/page: 6 new-hook at $0.45, 6 at $0). Sensitivity: every trial a fresh REMIX render at $1.28 (ENGINE_NEXT50 IG-1).'),
 ('fb_pages','Facebook Pages in the native program (one per IG page, same go-live days)',4,4,'pages','Client direction. R20 runs 2 FB pages.'),
 ('fb_long','Facebook long cuts (60–180 s) per page per day',2,2,'cuts','Client direction; COSTS §2b $0.20 each.'),
 ('fb_long_rel','Views per FB long cut ÷ a FB reel',0.6,0.8,'x','ASSUMPTION. Facebook removed the Reels length cap (ENGINE_100X §1.3, S5); 65+ lead long-form growth (S30), but long videos complete less.'),
 ('fb_tp','Facebook text + photo posts per page per day',2,2,'posts','Client direction; COSTS §2b ($0.05 photo, $0 text).'),
 ('fb_tp_rel','Views per FB text/photo post ÷ a FB reel',0.25,0.4,'x','ASSUMPTION. Format barely changes ENGAGEMENT on FB (images 5.20%, video 4.84%, text 4.76%, Buffer 52M posts, S6) but text/photo get far less recommended reach than Reels.'),
 ('fb_tp_v2v','Keyword→DM→link rate on FB text/photo ÷ the reel rate',0.5,0.7,'x','ASSUMPTION: no on-video CTA; the keyword lives in the caption.'),
 ('fb_fit','FB 65+ buyer-fit multiplier on views → landing visitors (FB program runs only)',1.25,1.5,'x','ASSUMPTION. 65+ use Facebook far more than IG (19% daily) or TikTok (5% daily) (Pew, ENGINE_100X S1); the FB-native "send this to your family group" close and FB-specific caption. NOT the +72% native-vs-crosspost reach result (S4, old photo test): R20 already treats FB as native at par, so that gain is not added again.'),
 ('rp_plat','Distinct-cut repost lanes per IG page and their view multiplier vs base (TT / YT / Threads / X)',{'TT':0.7,'YT':0.5,'TH':0.15,'X':0.10},{'TT':0.7,'YT':0.5,'TH':0.25,'X':0.15},'x','TT/YT from R20 (plat_mult). Threads/X ASSUMPTION (POSTDB: same asset did 40–100× better on IG than TikTok/YouTube in Sep 2026; Threads/X are text-first). Bio-link chain only (v2v_bio); TikTok has no purchase CTA (S32). R32+ only.'),
 ('learn_x','Scorecard loop: weekly uplift to the hit rate (→ mean views per post), compounding from week 2',0.04,0.08,'%/wk','ASSUMPTION. Thompson sampling over hook/body/close arms works under delayed batched feedback (S46, S47) but no source gives a magnitude. Under a power law, mean views scale ~ with the hit rate (POSTDB: 3 posts = 80% of views).'),
 ('learn_cap','Bound on the cumulative scorecard uplift',1.4,1.8,'x','ASSUMPTION. Central reaches the cap in ~9 weeks.'),
 ('intent_up','Intent-routed offers (keyword → matched /b?t= page + qualify-in-2 DM): multiplier on organic visitor → buyer',1.15,1.35,'x','ASSUMPTION with a heavy haircut on vendor data: qualified DM flows convert ~2.4× unqualified; DM→purchase 12–25% qualified vs 2–5% unqualified (Communipass 2026, V-; MONETIZATION_ENGINE S1); ENGINE_100X §8.8 says use vendor bands as gates, not forecasts.'),
 ('dm_mult','DM chain multiplier (keyword comment → DM open → link click) on IG/FB views → visitors',1.0,1.3,'x','Central = R20 chain (0.3% comments × 85% open × 30% click × 1.25 bio uplift; chatautodm / creatorflow). Upside 1.3 = DM click 39% (inside the 25–45% band). The solver scales this.'),
 ('asc_coach','R3 coached ($147/mo × 12 weeks): share of members who start at the week-6 trigger',0.05,0.07,'%','Client direction (5%). Fixed-term 3-month program → NOT MRR; a separate line. Contribution 45% after the certified trainer (ASSUMPTION); honest cohort caps ignored.'),
 ('asc_labs','R4 labs + clinician review ($399, one-time): share of members, at member day 60',0.03,0.04,'%','Client direction (3%). One-time; delivered and billed by the client\'s healthcare business (BRIEF ascension R4). Strong Years cash share 20% ASSUMPTION.'),
 ('asc_supp','R5 supplements subscribe & save from member month 4 (day 90): take of surviving members, $35/mo, 7%/mo churn, 35% margin',0.08,0.12,'%','Client direction (month 4; OFFER.md §4 says month 7: conflict noted). BRIEF: supplement subs churn 5–8.8%/mo. Recurring, but reported as a SEPARATE supplement MRR line, never in membership MRR. Take, price and margin are ASSUMPTIONS.'),
 ('seed_lists','R35: real lists that are mailed a runway waitlist invite (Unignorable / K9SUPPS contacts)',(20000,10000),(100000,50000),'contacts','Parametrised (BRIEF: list sizes unknown). Default = the 20K/10K placeholders already in R20.'),
 ('seed_opt','R35: list contact → waitlist opt-in over the runway',0.05,0.12,'%','ASSUMPTION from the model\'s own warm-list chain: 92% delivered × 30% open × 8% CTOR × 4.7 weighted sends × 45% opt-in ≈ 4.7%. These lists did not opt in to this brand. K9SUPPS counts at k9mult 0.35. Opted-in names leave the launch-email pool (no double counting).'),
]
MXC = {k:c for k,_,c,_,_,_ in MX_INPUTS}
MXU = {k:u for k,_,_,u,_,_ in MX_INPUTS}
MX_SOURCES = [
 ('ENGINE_100X.md §2.1, §5, §8; S18 IG trial_params', 'Trial Reels go to non-followers, graduation_strategy SS_PERFORMANCE; count toward the 100/24 h publish limit'),
 ('ENGINE_NEXT50.md N1 / N2 / IG-1', 'No published Trial Reel cap ("as low as five", anecdotal, riffon / ALM Corp); auto-share to followers within 72 h; trials should be distinct REMIX renders'),
 ('ENGINE_100X S3 / S20 / S44', 'Meta originality rules (low-value edits demoted account-wide), IG Apr 2026 repost crackdown (V-), near-identical creative clustering (V-)'),
 ('ENGINE_100X S1 (Pew)', '65+ use Facebook far more than IG (19% daily) or TikTok (5% daily)'),
 ('ENGINE_100X S6 (Buffer, 52M posts)', 'FB engagement images 5.20% / video 4.84% / text 4.76%'),
 ('MONETIZATION_ENGINE S1 (Communipass 2026, V-)', 'DM open 85–92%, link CTR 18–35%, DM→purchase 12–25% qualified, 2–5% unqualified; qualified 2.4×'),
 ('BRIEF.md ascension ladder; OFFER.md §4', 'R3 coached $147/mo 12 weeks; R4 labs $299–499 via the healthcare business; R5 supplements from month 4 (OFFER: month 7)'),
 ('COSTS.md §2b', 'new hook ≈ $0.45; frame/text/length $0; FB long $0.20; FB photo $0.05; full config 200 posts/day $223/day'),
 ('POSTDB_FINDINGS.md / BRIEF.md (Yang Mun)', '~1.75 ebook buyers per 100K views; 3-ebook bundle $19.99; Whop Inner Circle $19.99/mo, 3-day trial; ~7,000 ebook buyers in ~90 days'),
]

def _vpp(o, age, plat_m, mult, cad, posts_max=6):
    v = min(o['v_base']*o['v_growth']**((age-15)/30.0), o['v_cap'])*plat_m*mult
    return v*((cad/6.0)**(-0.3) if cad>6 else 1.0)

def _cad(o, r, age):
    return o['posts_d1'] + (r['posts_max']-o['posts_d1'])*min(1.0, age/o['posts_ramp'])

def _decay_mean(k, d):
    """Mean reach factor of k variants of one body, the n-th (n = 1..k) reaching d^n (fractional k interpolated)."""
    if k <= 0: return 0.0
    return d*(1-d**k)/(1-d)/k if d < 1 else 1.0

def roster(r, o=ORG):
    """Feed pages (day, platform, role). 'r20' = R20's 7 pages + the 4th CANON-4 IG page; 'canon4' = 4 IG + 4 FB native
    + 4 each of TT / YT / Threads / X distinct-cut reposts (the 144-placement grid of COSTS §2b)."""
    days = r['tr_days']
    if r['roster'] == 'r20':
        pg = [(d, p, 'feed') for d, p in zip(o['page_days'], o['page_plat'])]
        if r.get('tr_on'): pg.append((days[3], 'IG', 'feed'))
        return pg
    pg = []
    for d in days:
        pg += [(d, 'IG', 'feed'), (d, 'FB', 'fbprog'), (d, 'TT', 'rp'), (d, 'YT', 'rp'), (d, 'TH', 'rp'), (d, 'X', 'rp')]
    return pg

def learn_mult(r, t):
    if not r.get('learn_x'): return 1.0
    return min(r['learn_cap'], (1+r['learn_x'])**max(0.0, (t-7)/7.0))

def organic_day_max(r, t, o=ORG, s=SH):
    mult = o['scen_mult'][r['scen']]*learn_mult(r, t)
    igp = r.get('ig_pen', 1.0)                       # originality demotion (sensitivity only)
    dm = o['v2v_dm']*r['dm_mult']; bio = o['v2v_bio']
    views = visitors = posts = cost_posts = xcost = trials = tr_views = grads = 0.0; pages = 0
    for pd_, plat, role in roster(r, o):
        age = t-(pd_-1)
        if age < 0: continue
        pages += 1
        cad = _cad(o, r, age); ramp = cad/r['posts_max']
        pm = r['rp_plat'][plat] if role == 'rp' else o['plat_mult'][plat]
        vpp = _vpp(o, age, pm, mult, cad)*(igp if plat == 'IG' else 1.0)
        rate = (dm if plat in ('IG', 'FB') else bio)
        fit = r['fb_fit'] if (plat == 'FB' and r.get('fbprog')) else 1.0
        pv = cad*vpp; views += pv; visitors += pv*rate*fit; posts += cad; cost_posts += cad
        if role == 'fbprog':
            nl = r['fb_long']*ramp; nt = r['fb_tp']*ramp
            lv = nl*vpp*r['fb_long_rel']; tv = nt*vpp*r['fb_tp_rel']
            views += lv+tv; visitors += lv*rate*fit + tv*rate*fit*r['fb_tp_v2v']
            posts += nl+nt; xcost += nl*0.20 + nt*0.5*0.05
    if r.get('tr_on'):
        for pd_ in r['tr_days']:
            age = t-(pd_-1)
            if age < 0: continue
            ramp_ = r['tr_ramp']; ntr = min(r['tr_cap'], ramp_[0] if age < 7 else ramp_[1] if age < 14 else ramp_[2])
            cad = _cad(o, r, age)
            vfeed = _vpp(o, age, o['plat_mult']['IG'], mult, cad)*igp
            k = ntr/r['masters']
            tv = ntr*r['tr_rel']*vfeed*_decay_mean(k, r['var_decay'])
            g = min(ntr*r['grad_rate'], cad)
            gv = g*vfeed*(r['grad_up']-1)
            views += tv+gv; visitors += (tv+gv)*dm
            trials += ntr; tr_views += tv; grads += g; posts += ntr
            xcost += ntr*r['new_hook_share']*0.45
    return dict(views=views, visitors=visitors, posts=posts, pages=pages, cost_posts=cost_posts, xcost=xcost,
                trials=trials, tr_views=tr_views, grads=grads)

MX_OFF = dict(mx=1, roster='r20', tr_on=1, fbprog=0, learn_x=0, learn_cap=1.0, intent_up=1.0, asc=0, seed_lists=None, ig_pen=1.0)
def _mx(base, up=False, **kw):
    src = MXU if up else MXC
    d = dict(base, **{k: v for k, v in src.items() if k not in ('seed_lists',)}); d.update(MX_OFF)
    d['intent_up'] = 1.0; d['dm_mult'] = src['dm_mult'] if up else 1.0; d['learn_x'] = 0
    d.update(kw); return d

OM30 = _mx(BASE, name='R30 = R20 + 80 Trial Reels/day (4 IG pages × 20, ramp 3→6→20), central trial inputs (0.40 rel, 0.6^n decay, 5% graduate at 2.0×); 4th CANON-4 IG feed page added so every trial page can graduate; $0 media')
OM31 = _mx(UPS, up=True, name='R31 = R30 upside: R21 organic/conversion inputs + upside trial inputs (0.70 rel, 10% graduate at 3.0×, DM chain ×1.3); $0 media')
OM32 = dict(OM30, roster='canon4', fbprog=1, name='R32 = R30 + Facebook native program (4 FB Pages × 6 native reels + 2 long cuts + text + photo, FB 65+ fit ×1.25) + distinct-cut TT/YT/Threads/X reposts (the 144-placement CANON-4 grid)')
OM33 = dict(OM32, learn_x=MXC['learn_x'], learn_cap=MXC['learn_cap'], name='R33 = R32 + scorecard learning loop (+4%/week hit rate from week 2, capped ×1.4)')
OM34 = dict(OM33, intent_up=MXC['intent_up'], asc=1, name='R34 = R33 + intent-routed offers (organic visitor→buyer ×1.15) + ascension lines (R3 coached 5%, R4 labs 3%, R5 supplements from month 4) reported separately')
OM35 = dict(OM34, seed_lists=MXC['seed_lists'], seed_opt=MXC['seed_opt'], name='R35 = R34 + seeded waitlist from the real lists (default Unignorable 20K / K9SUPPS 10K, 5% runway opt-in; opted-in names leave the launch-email pool)')
RUNS_MAX = [OM30, OM31, OM32, OM33, OM34, OM35]
OM34U = dict(_mx(UPS, up=True), roster='canon4', fbprog=1, fb_fit=MXU['fb_fit'], learn_x=MXU['learn_x'], learn_cap=MXU['learn_cap'], intent_up=MXU['intent_up'], asc=1,
            name='R34 with EVERY organic input at upside (R21 base + all upside Organic-max inputs)')

def prep(r):
    """Apply R35's list seeding: names that opt in leave the warm-email pool."""
    r = dict(r)
    if r.get('seed_lists'):
        u, k = r['seed_lists']; opt = r['seed_opt']
        r['seed_wl'] = r.get('seed_wl', 0) + (u + k*SH['k9mult'])*opt
        r['unig'] = u*(1-opt); r['k9'] = k*(1-opt)
    return r

def ascension(rows, r, s=SH, a=None):
    """Separate ascension lines from the daily cell-B purchase series. Returns per-day dicts (not in MRR)."""
    a = a or (MXU if r.get('_asc_up') else MXC)
    P = [x['P'] for x in rows]; n = len(rows); out = []; supp = 0.0; cum_c = cum_l = cum_cash = 0.0
    Sp = lambda k: r['renB1']*Sk(s, k)/Sk(s, 1) if k > 0 else 1
    coach_starts = [0.0]*n
    for i in range(n):
        d = i+1
        j = i-42
        coach_starts[i] = P[j]*(1-s['fe_ref'])*Sp(1)*a['asc_coach'] if j >= 0 else 0.0
        coach_active = sum(coach_starts[max(0, i-83):i+1])
        coach_rev = coach_active*147/30
        jl = i-60
        labs = P[jl]*(1-s['fe_ref'])*Sp(2)*a['asc_labs'] if jl >= 0 else 0.0
        js = i-90
        supp += (P[js]*(1-s['fe_ref'])*Sp(3)*a['asc_supp'] if js >= 0 else 0.0) - supp*0.07/30
        supp_rev = supp*35/30
        cum_c += coach_rev; cum_l += labs*399
        cum_cash += coach_rev*0.45 + labs*399*0.20 + supp_rev*0.35
        out.append(dict(d=d, coach_rr=coach_active*147, labs_cum=cum_l, supp_mrr=supp*35, coach_cum=cum_c, asc_cash=cum_cash))
    return out

def run_max(r, s=SH, o=ORG, days=360):
    r = prep(r)
    rows, pre, info = run(r, s=s, o=o, days=days)
    asc = ascension(rows, r) if r.get('asc') else None
    if asc:
        for x, y in zip(rows, asc): x['cash'] += y['asc_cash']; x['asc'] = y
    return rows, pre, info, asc

def summ_max(rows, pre, info, asc, r, o=ORG):
    sm = summ(rows, pre, info)
    if asc:   # cash already includes ascension contribution: recompute cash-based fields
        lo = min(range(len(rows)), key=lambda i: rows[i]['cash']); sm['low'] = rows[lo]['cash']; sm['lowday'] = lo+1
        nets = [rows[0]['cash']] + [rows[i]['cash']-rows[i-1]['cash'] for i in range(1, len(rows))]
        sm['cfpos'] = next((i+1 for i in range(len(nets)-13) if all(x > 0 for x in nets[i:i+14])), 999)
        sm['beday'] = next((x['d'] for x in rows if x['d'] > 30 and x['cash'] >= 0), 999)
        for d in (30, 90, 180): sm[f'supp{d}'] = asc[d-1]['supp_mrr']; sm[f'coach{d}'] = asc[d-1]['coach_rr']; sm[f'labs{d}'] = asc[d-1]['labs_cum']
    for d in (1, 30, 90, 180):
        sm[f'v{d}'] = rows[d-1]['views']; sm[f'p{d}'] = rows[d-1]['posts']
    sm['cost30'] = rows[29]['costs']; sm['cost90'] = rows[89]['costs']
    od = organic_day_max(prep(r), r['runway']+29, o) if r.get('mx') else organic_day(r, r['runway']+29, o)
    sm['trials30'] = od.get('trials', 0); sm['trv30'] = od.get('tr_views', 0); sm['grads30'] = od.get('grads', 0)
    sm['vpt30'] = od['tr_views']/od['trials'] if od.get('trials') else 0
    sm['vis30'] = rows[29]['visitors']; sm['seed'] = prep(r).get('seed_wl', 0)
    return sm

def original_ym(days=360, reach=1.0, s=SH, o=ORG):
    """ORIGINAL: a Yang-Mun-style single page, 3 posts/day, $19.99 3-ebook bundle + Whop "Inner Circle" $19.99/mo
    (3-day trial). POSTDB / BRIEF: ~1.75 ebook buyers per 100K views; trial→paid 42% (H&F, BRIEF); the renewal curve
    S of the Blitz sheet. ASSUMPTIONS: 15% of ebook buyers start the Whop trial; 6% fees+refunds; reach uses OUR
    central per-post curve on one FB-type page (multiplier 1.0) unless `reach` scales it (YM launch era ≈ ×12.8).
    Lean cost: 3 posts × $1.12 (COSTS §2b) + $16/day tools; with_fixed adds our $30.5K/month team opex."""
    rows = []; paid = [0.0]*(days+1); cash = cashf = 0.0
    for d in range(1, days+1):
        age = d-1 + 15                    # page posts from day 1; age offset so day 1 ≈ our page-age-15 baseline
        vpp = min(o['v_base']*o['v_growth']**((age-15)/30.0), o['v_cap'])*reach
        views = 3*vpp; buyers = views*1.75e-5
        paid[d] = buyers*0.15*0.42
        act = sum(paid[j]*Sk(s, (d-j)//30) for j in range(1, d+1))
        mrr = act*19.99
        cash_in = (buyers*19.99 + mrr/30)*0.94
        cost = 3*1.12 + 16
        cash += cash_in - cost; cashf += cash_in - cost - (s['fixed']+s['shop_plan'])/30
        rows.append(dict(d=d, views=views, posts=3, mrr=mrr, cash=cash, cashf=cashf, cost=cost))
    g = lambda d, k: rows[d-1][k]
    be = next((x['d'] for x in rows if x['cash'] >= 0), 999); bef = next((x['d'] for x in rows if x['d'] > 30 and x['cashf'] >= 0), 999)
    return rows, dict(m30=g(30, 'mrr'), m90=g(90, 'mrr'), m180=g(180, 'mrr'), v30=g(30, 'views'), v90=g(90, 'views'), cost=3*1.12+16, be=be, be_fixed=bef, posts=3)

def solve_key(base, setter, lo, hi, target=100000, day=30, iters=30):
    def f(x):
        rows, _, _, _ = run_max(setter(dict(base), x), days=day); return rows[day-1]['mrr']
    if f(lo) >= target: return lo
    if f(hi) < target: return None
    for _ in range(iters):
        mid = (lo+hi)/2
        if f(mid) >= target: hi = mid
        else: lo = mid
    return hi

def _set(k):
    def s_(r, x): r[k] = x; return r
    return s_
def _set_scen(r, x):
    r['scen'] = 'x'; ORG['scen_mult']['x'] = x; return r

SENS_MAX = [
 ('Trial Reel cap 5/page/day (the anecdotal real cap; 20 trials/day total)', dict(tr_cap=5)),
 ('Trial Reel cap 10/page/day', dict(tr_cap=10)),
 ('Views per Trial Reel 0.15× feed (conservative)', dict(tr_rel=0.15)), ('Views per Trial Reel 0.70× feed (upside)', dict(tr_rel=0.70)),
 ('Variant decay 0.4^n (harsher clustering)', dict(var_decay=0.4)), ('Variant decay 0.8^n', dict(var_decay=0.8)), ('No variant decay (every variant = a fresh post)', dict(var_decay=0.9999)),
 ('Graduation 2% (vs 5%)', dict(grad_rate=0.02)), ('Graduation 10%', dict(grad_rate=0.10)), ('Graduate uplift 1.5× (vs 2.0×)', dict(grad_up=1.5)), ('Graduate uplift 3.0×', dict(grad_up=3.0)),
 ('Originality demotion: IG reach ×0.7 account-wide (trial volume read as low-value edits)', dict(ig_pen=0.7)), ('Originality demotion ×0.4', dict(ig_pen=0.4)),
 ('FB 65+ fit 1.0 (vs 1.25)', dict(fb_fit=1.0)), ('FB 65+ fit 1.5', dict(fb_fit=1.5)),
 ('Scorecard uplift 0 (no learning)', dict(learn_x=0)), ('Scorecard uplift +8%/wk, cap 1.8', dict(learn_x=0.08, learn_cap=1.8)),
 ('Intent routing 1.0 (no uplift)', dict(intent_up=1.0)), ('Intent routing 1.35', dict(intent_up=1.35)),
 ('DM chain ×0.7', dict(dm_mult=0.7)), ('DM chain ×1.3', dict(dm_mult=1.3)),
 ('Organic reach conservative ×0.35', dict(scen='conservative')), ('Organic reach upside ×1.75', dict(scen='upside')), ('Organic breakout ×3', dict(scen='breakout')),
 ('Ebook/sub page conversion 3% (vs 5%)', dict(cvr_org=0.03)), ('Conversion 8%', dict(cvr_org=0.08)),
 ('subB 0.55 (vs 0.70)', dict(subB=0.55)), ('subB 0.85', dict(subB=0.85)),
 ('Lists 100K / 50K seeded at 12% opt-in', dict(seed_lists=(100000, 50000), seed_opt=0.12)),
 ('Lists 20K / 10K at 12% opt-in', dict(seed_lists=(20000, 10000), seed_opt=0.12)),
 ('Every Trial Reel a fresh REMIX render ($1.28 each; cost only)', dict(new_hook_share=1.28/0.45)),
]

def main_max(write_json=None):
    res = []
    for r in RUNS_MAX:
        rows, pre, info, asc = run_max(r); res.append((r, rows, pre, info, asc, summ_max(rows, pre, info, asc, r)))
    rows, pre, info, asc = run_max(OM34U); r34u = summ_max(rows, pre, info, asc, OM34U)
    rows20, pre20, info20 = run(RUNS[0]); s20 = summ(rows20, pre20, info20)
    s20.update({f'v{d}': rows20[d-1]['views'] for d in (1, 30, 90, 180)}); s20.update({f'p{d}': rows20[d-1]['posts'] for d in (1, 30, 90, 180)}); s20['cost30'] = rows20[29]['costs']
    print(f"{'run':5s} {'p/d30':>6s} {'v/d1':>7s} {'v/d30':>8s} {'v/d90':>8s} {'d4':>6s} {'d14':>6s} {'d30':>6s} {'d60':>6s} {'d90':>6s} {'d180':>6s} {'ret30':>6s} {'10K':>4s} {'50K':>4s} {'100K':>4s} {'low':>6s} {'lowd':>4s} {'cf+':>4s} {'be':>4s} {'$/d30':>6s} {'seed':>6s}")
    def line(nm, sm, rows):
        print(f"{nm:5s} {sm['p30']:6.0f} {sm['v1']/1e3:6.0f}K {sm['v30']/1e3:7.0f}K {sm['v90']/1e3:7.0f}K {sm['m4']/1e3:6.1f} {sm['m14']/1e3:6.1f} {sm['m30']/1e3:6.1f} {rows[59]['mrr']/1e3:6.1f} {sm['m90']/1e3:6.1f} {sm['m180']/1e3:6.1f} {sm['ret30']/1e3:6.1f} {sm['d10']:4d} {sm['d50']:4d} {sm['d100']:4d} {sm['low']/1e3:6.0f} {sm['lowday']:4d} {sm['cfpos']:4d} {sm['beday']:4d} {sm['cost30']:6.0f} {sm.get('seed',0):6.0f}")
    line('R20', s20, rows20)
    for r, rows_, pre_, info_, asc_, sm in res: line(r['name'][:3], sm, rows_)
    line('R34U', r34u, rows)
    for r, rows_, pre_, info_, asc_, sm in res:
        if asc_: print(r['name'][:3], 'ascension (not MRR): supp MRR d90/d180', round(sm['supp90']), round(sm['supp180']), '| coached run-rate d90/d180', round(sm['coach90']), round(sm['coach180']), '| labs gross cum d180', round(sm['labs180']))
    print('trial lane d30 (R30): trials', res[0][5]['trials30'], 'views/trial', round(res[0][5]['vpt30']), 'grads', round(res[0][5]['grads30'], 1))
    # solver on R34 (and R35) for $100K at day 30, $0 media
    base = OM34
    rows0, _, _, _ = run_max(base); od0 = organic_day_max(base, base['runway']+29)
    dm_rate = 0.85*0.30*SH['lp_org']*base['cvr_org']*base['subB']*base['intent_up']   # per keyword commenter, central
    sol = {}
    sol['tr_rel'] = solve_key(base, _set('tr_rel'), MXC['tr_rel'], 200.0)
    sol['grad_rate'] = solve_key(base, _set('grad_rate'), MXC['grad_rate'], 1.0)
    sol['grad_both'] = solve_key(base, lambda r, x: (r.update(grad_rate=1.0, grad_up=x) or r), 1.0, 500.0)
    sol['dm_mult'] = solve_key(base, _set('dm_mult'), 1.0, 200.0)
    sol['cvr_org'] = solve_key(base, _set('cvr_org'), base['cvr_org'], 1.0)
    sol['seed_wl'] = solve_key(base, _set('seed_wl'), 0, 2_000_000)
    sol['reach'] = solve_key(base, _set_scen, 1.0, 200.0)
    sol['seed_wl_r35'] = solve_key(OM35, _set('seed_wl'), 0, 2_000_000)
    ORG['scen_mult'].pop('x', None)
    print('solver (R34 base, $100K MRR day 30, $0 media):', {k: (round(v, 4) if v is not None else None) for k, v in sol.items()})
    print('  central views/trial d30', round(od0['tr_views']/od0['trials']), '| DM→purchase per commenter central', round(dm_rate*100, 2), '%')
    sens = []
    for bn, b in (('R34', OM34), ('R35', OM35)):
        bs = [x for x in res if x[0] is b][0][5]
        for nm, ch in SENS_MAX:
            if bn == 'R34' and 'seed_lists' in ch: continue
            rr = dict(b, **ch); rows_, pre_, info_, asc_ = run_max(rr); sm = summ_max(rows_, pre_, info_, asc_, rr)
            sens.append(dict(base=bn, name=nm, summ=sm, d30_delta=sm['m30']-bs['m30'], flag=abs(sm['m30']-bs['m30']) > 5000))
            print(f"  sens {bn} {nm[:60]:60s} d30 {sm['m30']/1e3:6.1f} Δ {(sm['m30']-bs['m30'])/1e3:+6.1f} {'FLAG' if abs(sm['m30']-bs['m30'])>5000 else ''}")
    orig, osm = original_ym(); orig_ym, osm_ym = original_ym(reach=12.8)
    print('ORIGINAL (central reach):', {k: round(v) for k, v in osm.items()}); print('ORIGINAL (YM launch reach ×12.8):', {k: round(v) for k, v in osm_ym.items()})
    out = dict(res=res, r34u=r34u, s20=s20, rows20=rows20, sol=sol, sol_ref=dict(vpt30=od0['tr_views']/od0['trials'], dm_rate=dm_rate, v30=rows0[29]['views']),
               sens=sens, orig=(orig, osm), orig_ym=(orig_ym, osm_ym))
    return out



# ==============================================================================================
# SCALE FAMILY R30–R36 — "Scale plan to $250K" (Oct 2 2026; BLITZ.md §14; sheet Organic_Max).
# A PORT of the client-approved projection data/projection_aggressive_central.csv. Run R30A (basis 'booked_prev') reproduces
# that file cell-for-cell to its display rounding (tools/test_scale_engine.py: every cell within ±0.5). The canonical runs
# R30–R36 differ from the file in ONE rule, by instruction (CANON UPDATE 5 + the governor): the scale-ladder milestones,
# the $30K paid-media gate and the 25% all-in cap are evaluated on TRAILING-7-DAY RETAINED MRR (basis 'retained_t7'), the
# same number workers/growth/governor.py gates on. The approved file itself steps them on the previous day's BOOKED MRR.
#   booked_MRR    = 0.95 × ($25 × active members + $147 × coached members)  (run-rate at the contracted renewal price)
#   retained_MRR  = 0.95 × $25 × (50% of first-cycle members + every member who has renewed)   ← PLAN ON THIS ONE
#   contracted_30d= renewals falling due in the next 30 days from surviving members, at their expected survival
#                   (monthly billing: every surviving member renews inside 30 days, so it equals retained_MRR)
#   cash          = −$15K pre-launch + $12 per new buyer + $25 per renewal + $147/30 per coached member per day, less 3%
#                   payment fees and the day's cost (generation + paid + $16 tools + review at $20/h). No team opex.
# Every input below is labelled; anything without a citation is an ASSUMPTION (the projection's own value).
# ==============================================================================================
SC_INPUTS = [
 # key, label, central, low, high, unit, source / rationale
 ('v_base','Views per master post (IG feed basis) at page age 15 d, before learning',6000,2100,10500,'views','ORG v_base (Assumptions A); range = ORG scen_mult conservative ×0.35 / upside ×1.75. ASSUMPTION.'),
 ('v_growth','Growth of views per post per 30 days of page age',1.6,1.3,2.0,'x/30 d','ORG v_growth (Assumptions A). ASSUMPTION.'),
 ('age_launch','Page age on day 1 for the 4 launch pages',15,8,21,'days','14-day runway (R20 runway = 14; pages post from runway day −14). ASSUMPTION.'),
 ('age_new','Page age on its go-live day for a ladder page (pre-created, warmed)',7,0,14,'days','ASSUMPTION fitted to the approved projection: spare handles are created and warmed 7 days before the ladder opens them (ACCOUNT_SETUP).'),
 ('learn_wk','Scorecard learning loop: linear uplift on views per post per week from day 0',0.03,0.0,0.08,'%/wk','ASSUMPTION (approved projection; Organic-max used +4%/wk compounding). Thompson sampling works under delayed feedback (ENGINE_100X S46/S47); no source gives a magnitude.'),
 ('learn_cap','Bound on the learning uplift',1.4,1.0,1.8,'x','ASSUMPTION (Organic-max learn_cap). Never binds before day 93 at central, so it does not touch the approved 180-day file before the page ceiling.'),
 ('m_ig','IG feed views per master ÷ base',1.0,1.0,1.0,'x','Basis platform (POSTDB: IG did 40–100× TikTok/YouTube on the same asset in Sep 2026).'),
 ('m_fb','FB native reel views per master ÷ base',0.8,0.5,1.0,'x','ASSUMPTION (R20 plat_mult FB 1.0; FB Reels reach 0.55% of followers vs IG 4.1%, Socialinsider Aug 2026).'),
 ('m_tt','TikTok distinct-cut views per master ÷ base',0.7,0.3,1.0,'x','ORG plat_mult TT 0.7.'),
 ('m_yt','YouTube distinct-cut views per master ÷ base',0.5,0.2,0.7,'x','ORG plat_mult YT 0.5.'),
 ('m_thx','Threads + X text-first reposts, views per master ÷ base (both lanes together)',0.3,0.1,0.4,'x','ASSUMPTION (Organic-max rp_plat TH 0.15 + X 0.10–0.15).'),
 ('fb_extra','Facebook long cuts + text/photo posts per page per day',4,2,6,'posts','CANON 4 FB program (2 long cuts + text + photo).'),
 ('fb_extra_rel','Views per FB long cut / text / photo post ÷ base',0.5,0.25,0.6,'x','ASSUMPTION (Organic-max fb_long_rel 0.6, fb_tp_rel 0.25; blended).'),
 ('yt_posts','YouTube distinct cuts posted per page per day (views carried by m_yt × masters)',4,4,9,'posts','ASSUMPTION (approved projection counts 4 YT posts/page; the view lane is modelled per master).'),
 ('tr_warm','Trial Reels per IG page per day in the warm-up week (days 1–7)',10,3,10,'reels','CANON 5: compressed warm-up 10/day week 1, 20 from day 8.'),
 ('tr_cap','Trial Reels per IG page per day, steady state / hard cap',20,5,20,'reels','CANON 5 (20/page/day). ASSUMPTION FLAG: Instagram publishes no cap; one source says "as low as five" (ENGINE_NEXT50 N1). Sensitivity 5.'),
 ('tr_reach','Views per Trial Reel ÷ base (non-follower test pool only)',0.35,0.15,0.50,'x','ASSUMPTION. Meta: trials go to non-followers first (ENGINE_NEXT50 N2); no reach data published. Sensitivity 15%.'),
 ('tr_grad','Graduation bonus per Trial Reel ÷ base (winners re-shared to the feed / followers within 72 h)',0.1695,0.05,0.30,'x','ASSUMPTION fitted to the approved projection (trial lane = 0.5195 × base per trial = reach 0.35 + this). ≈ 5% graduate at 3.4× (POSTDB p75 rel 2.79, p90 13.7).'),
 ('page_ceiling','Views ceiling per page per day, all platforms together',600000,300000,1200000,'views/page/day','ASSUMPTION (approved projection). YM launch-era TikTok mean 953K/post was a single breakout page; a page-day ceiling keeps reach from compounding forever. Sensitivity 300K.'),
 ('click','Views → link clicks (keyword comment → DM link + bio link, all platforms blended)',0.004,0.002,0.006,'%','ASSUMPTION. R20 chain: IG/FB 0.0956% of views to LANDING (0.3% comments × 85% DM open × 30% click × 1.25); the projection uses 0.4% clicks × 70% loads = 0.28% (≈2.9× R20) because every master carries a pinned keyword + Stories link sticker + broadcast line (CANON 4 comment economy). Range = ±50% (sensitivity).'),
 ('land','Link click → landing page loads',0.70,0.60,0.85,'%','SH lp_org 0.70.'),
 ('conv','Landing visitor → "$12 today = books + first month, then $25/mo" purchase (cell B)',0.05,0.025,0.08,'%','LADDER cvr_org 5% (CartFlows 1.5–5% cold, 8–15% warm). ASSUMPTION within the cited range; subB is folded in.'),
 ('lists','Warm list contacts mailed at launch (Unignorable + K9SUPPS)',30000,10000,150000,'contacts','BRIEF: sizes unknown. R30 30K (= R20 20K + 10K), R31 150K.'),
 ('list_conv','Warm list contact → buyer over days 1–14',0.015,0.0075,0.03,'%','ASSUMPTION: CartFlows email lists convert 1–2% to paid.'),
 ('list_days','Days the list buyers are spread over',14,7,14,'days','Launch email sequence (email_w days 1–27, front-loaded) flattened. ASSUMPTION.'),
 ('wl','Waitlist on day 1',1500,500,5000,'names','R30 1.5K, R31 5K. Organic runway waitlist (R20 ≈ 433) + seeded lists. ASSUMPTION.'),
 ('wl_conv','Waitlist → buyer in the first 72 h',0.10,0.06,0.15,'%','ORG c72 10% (getwaitlist.com: consumer waitlist → customer 10–15%).'),
 ('wl_days','Days the waitlist buyers are spread over',3,3,3,'days','ORG c72_split (72 h), flattened.'),
 ('cpa','Paid media per buyer once the gate opens (boosts of winners + retargeting first)',85,60,130,'$','ASSUMPTION: between R20 boosted-organic (0.65× cold) and the §9 $111 scale line; BLITZ §9 says cold Meta ≈ $102 per net member.'),
 ('fe_price','First payment (books + first month)',12,7,15,'$','CANON UPDATE 2 cell B.'),
 ('price','Membership renewal price',25,25,25,'$/mo','CANON.'),
 ('realized','MRR realization (refunds, failed payments, discounts)',0.95,0.90,0.97,'x','SH realized 0.95.'),
 ('ren1','Survival of the first $25 renewal (day 30)',0.50,0.42,0.58,'%','LADDER renB1 (between Adapty trial→paid 42% and charge-today 62% × 0.935).'),
 ('churn_m','Monthly churn after the first renewal (continuous)',0.07,0.05,0.10,'%/mo','ASSUMPTION (approved projection). Blitz S curve months 2–5 ≈ 5–19%/mo; BRIEF supplement subs 5–8.8%/mo.'),
 ('coach_take','Members in the R3 coached program ($147/mo), from member day 10',0.05,0.02,0.07,'%','CANON 4: coached program offered from day 10 to anyone with a strength-age score; client direction 5%. Counted in BOOKED MRR, never in RETAINED. ASSUMPTION: held while the membership is active (the 12-week term is not ended in the projection).'),
 ('coach_day','Member day the coached offer starts',10,10,42,'day','CANON 5 seeded launch.'),
 ('coach_price','Coached program price',147,97,197,'$/mo','CANON 4 R3.'),
 ('fees','Payment fees on revenue',0.03,0.029,0.035,'%','Shopify Payments 2.9% + 30¢ (rounded to 3% in the projection).'),
 ('cash0','Cash on day 0 (pre-launch spend)',0,-1000,0,'$','Garrison Oct 2 2026: almost no money is spent before launch; was -15000.'),
 ('gen_master','Generation cost per master render (incl. its distinct platform cuts)',1.28,1.0,2.0,'$','COSTS.md §2b / ENGINE_NEXT50 IG-1: a fresh REMIX render $1.28.'),
 ('gen_trial','Generation cost per Trial Reel (half new-hook at $0.45, half $0 frame/text/length variants)',0.225,0.0,1.28,'$','COSTS.md §2b (new hook ≈ $0.45; frame/text/length $0); 1.28 = every trial a fresh REMIX.'),
 ('fixed','Tools per day',16,16,40,'$/day','COSTS.md (tools stack).'),
 ('review_s','Human review seconds per post',20,10,60,'s','ASSUMPTION (BLITZ_OPS review queue).'),
 ('review_rate','Review cost per hour',20,15,40,'$/h','ASSUMPTION.'),
 ('gate','Paid-media gate (no paid media of any kind below it)',30000,30000,50000,'$ MRR','CANON UPDATE 5 (config; client may raise to $50K).'),
 ('cap_share','All-in daily cap: share of MRR/30, minus fixed and generation',0.25,0.20,0.30,'%','CANON UPDATE 5 (config 20–30%).'),
]
SC = {k: c for k, _, c, _, _, _, _ in SC_INPUTS}
SC_LO = {k: lo for k, _, _, lo, _, _, _ in SC_INPUTS}
SC_HI = {k: hi for k, _, _, _, hi, _, _ in SC_INPUTS}
# Scale-on-MRR ladder (CANON UPDATE 5). Same rows as workers/growth/config.py DEFAULTS["governor"]["scale_rules"]
# (tools/test_scale_engine.py asserts equality). (threshold, pages_open, masters_per_page, trial_reels_per_page, tier).
# $50K (second character show + second coach) and $100K (PT/DE clones + Pro tier) carry NO volume or cost change in the
# approved projection; the model keeps that (flagged in BLITZ §14).
SC_LADDER = [(0, 4, 6, 20, 'standard'), (10000, 5, 8, 20, 'standard'), (30000, 7, 9, 20, 'standard'),
             (50000, 7, 9, 20, 'standard'), (100000, 7, 9, 20, 'pro')]
SC_MILESTONES = (10000, 30000, 50000, 100000, 250000)
SC_DEF = dict(SC, name='', basis='retained_t7', ladder=1, fb_on=1, reach_mult=1.0, click_mult=1.0)

R30 = dict(SC_DEF, name='R30 central: lists 30K, waitlist 1.5K; ladder, gate and cap on trailing-7-day RETAINED MRR')
R31 = dict(R30, lists=150000, wl=5000, name='R31 = R30 with lists 150K and waitlist 5K')
R32 = dict(R30, click=0.005, conv=0.065, ren1=0.58, churn_m=0.05, tr_reach=0.50,
           name='R32 upside: link clicks 0.5%, landing→buyer 6.5%, first renewal 58%, churn 5%/mo, Trial Reel reach 50%')
R33 = dict(R30, tr_cap=5, tr_warm=5, reach_mult=0.6, click_mult=0.5,
           name='R33 conservative: Trial Reel cap 5/page/day, reach ×0.6, funnel ×0.5 (views→clicks)')
R34 = dict(R30, ladder=0, name='R34 = R30 with the scale ladder OFF (4 pages × 6 masters all run)')
R35 = dict(R30, coach_take=0.0, name='R35 = R30 with ascension OFF (no coached program)')
R36 = dict(R30, fb_on=0, name='R36 = R30 with Facebook OFF (no FB reels, long cuts or text/photo)')
R30A = dict(R30, basis='booked_prev', name='R30A = the approved projection exactly (ladder, gate and cap on the previous day\'s BOOKED MRR)')
RUNS_SCALE = [R30, R31, R32, R33, R34, R35, R36]
SC_TAGS = ['r30', 'r31', 'r32', 'r33', 'r34', 'r35', 'r36']


def sc_metric(r, hist_b, hist_r):
    """The number the ladder, the gate and the cap read. retained_t7 = mean of the last 7 days' retained MRR, days before
    launch counted as $0 (fail-safe, the same rule as governor.trailing_retained). booked_prev = yesterday's booked MRR."""
    if r['basis'] == 'booked_prev':
        return hist_b[-1] if hist_b else 0.0
    if r['basis'] == 'retained_prev':
        return hist_r[-1] if hist_r else 0.0
    return sum(hist_r[-7:]) / 7.0


def sc_level(metric, ladder=SC_LADDER):
    lv = 0
    for i, row in enumerate(ladder):
        if metric >= row[0]:
            lv = i
    return lv


def sc_run(r, days=180):
    """One run of the scale family. Returns the daily rows (all projection columns + diagnostics)."""
    r = dict(SC_DEF, **r)
    surv = [1.0 if a < 30 else r['ren1'] * (1 - r['churn_m']) ** ((a - 30) / 30.0) for a in range(days + 1)]
    pages, B, rows, hist_b, hist_r = [], [], [], [], []
    cash = float(r['cash0']); lv = 0; ptot = 0.0; vtot = 0.0; btot = 0.0
    for t in range(1, days + 1):
        metric = sc_metric(r, hist_b, hist_r)
        if r['ladder']:
            lv = max(lv, sc_level(metric))                    # the ladder never steps down
        _, npg, mpp, trc, tier = SC_LADDER[lv]
        while len(pages) < npg:
            pages.append((t, r['age_launch'] if t == 1 else r['age_new']))
        trp = min(r['tr_warm'] if t <= 7 else trc, r['tr_cap'])
        L = min(r['learn_cap'], 1 + r['learn_wk'] * t / 7.0)
        trf = r['tr_reach'] + r['tr_grad']
        fb = (mpp * r['m_fb'] + r['fb_extra'] * r['fb_extra_rel']) if r['fb_on'] else 0.0
        lanes = dict(ig=mpp * r['m_ig'] + trf * trp, fb=fb, tt=mpp * r['m_tt'], yt=mpp * r['m_yt'], thx=mpp * r['m_thx'])
        comp = sum(lanes.values())
        V = dict.fromkeys(lanes, 0.0); capped = 0
        for s0, a0 in pages:
            age = a0 + (t - s0)
            v = r['v_base'] * r['reach_mult'] * r['v_growth'] ** ((age - 15) / 30.0) * L
            k = min(1.0, r['page_ceiling'] / (v * comp)) if comp > 0 else 0.0
            capped += k < 1.0
            for kk, w in lanes.items():
                V[kk] += v * k * w
        views = sum(V.values())
        clicks = views * r['click'] * r['click_mult']; land = clicks * r['land']
        masters = npg * mpp; trials = npg * trp
        fbp = (masters + r['fb_extra'] * npg) if r['fb_on'] else 0
        posts = masters + trials + fbp + masters + r['yt_posts'] * npg + masters + masters
        gen = r['gen_master'] * masters + r['gen_trial'] * trials
        gate_open = metric >= r['gate']
        paid = max(0.0, r['cap_share'] * metric / 30.0 - r['fixed'] - gen) if gate_open else 0.0
        b = (r['conv'] * land + (r['wl'] * r['wl_conv'] / r['wl_days'] if t <= r['wl_days'] else 0.0)
             + (r['lists'] * r['list_conv'] / r['list_days'] if t <= r['list_days'] else 0.0) + paid / r['cpa'])
        B.append(b); btot += b
        A = first = C = renp = 0.0
        for j in range(t):
            a = t - 1 - j; sv = B[j] * surv[a]
            A += sv
            if a < 30: first += B[j]
            if a >= r['coach_day']: C += r['coach_take'] * sv
            if a >= 30 and a % 30 == 0: renp += sv
        booked = (A * r['price'] + C * r['coach_price']) * r['realized']
        retained = (r['ren1'] * first + (A - first)) * r['price'] * r['realized']
        contracted = retained                                # monthly billing: every survivor renews within 30 days
        rev = b * r['fe_price'] + renp * r['price'] + C * r['coach_price'] / 30.0
        review = posts * r['review_s'] / 60.0
        cost = gen + paid + r['fixed'] + review * r['review_rate'] / 60.0
        cash += rev * (1 - r['fees']) - cost
        ptot += posts; vtot += views
        rows.append(dict(day=t, pages=npg, masters=masters, ig_main=masters, ig_trial=trials, fb_posts=fbp, tt=masters,
                         yt=r['yt_posts'] * npg, threads=masters, x=masters, posts_day=posts, posts_total=ptot,
                         views_ig=V['ig'], views_fb=V['fb'], views_tt=V['tt'], views_yt=V['yt'], views_th_x=V['thx'],
                         views_day=views, views_total=vtot, link_clicks=clicks, landing=land, new_buyers=b,
                         buyers_total=btot, active_members=A, coached_members=C, MRR=booked, retained_MRR=retained,
                         rev_day=rev, gen_cost=gen, paid_spend=paid, fixed=r['fixed'], review_min=review, cost_day=cost,
                         margin_pct=100 * (1 - 30 * cost / booked) if booked > 0 else None, cash=cash, booked_MRR=booked,
                         contracted_30d=contracted, cash_plus_contracted=cash + contracted,
                         metric=metric, level=lv, tier=tier, gate_open=gate_open, capped_pages=capped))
        hist_b.append(booked); hist_r.append(retained)
    return rows


def _first(rows, key, x):
    return next((w['day'] for w in rows if w[key] >= x), None)


def sc_summary(rows):
    g = lambda d, k: rows[d - 1][k]
    sm = {}
    for x in SC_MILESTONES:
        sm[f'bk{x // 1000}K'] = _first(rows, 'booked_MRR', x); sm[f'rt{x // 1000}K'] = _first(rows, 'retained_MRR', x)
    for d in (30, 60, 90, 180):
        if d <= len(rows):
            sm[f'bk{d}'] = g(d, 'booked_MRR'); sm[f'rt{d}'] = g(d, 'retained_MRR'); sm[f'cash{d}'] = g(d, 'cash')
    lo = min(rows, key=lambda w: w['cash']); sm['low'] = lo['cash']; sm['lowday'] = lo['day']
    sm['be'] = next((w['day'] for w in rows if w['cash'] >= 0), None)
    sm['mg30'] = g(30, 'margin_pct'); sm['mg60'] = g(60, 'margin_pct')
    sm['ladder'] = {SC_LADDER[i][0]: next((w['day'] for w in rows if w['level'] >= i), None) for i in range(1, len(SC_LADDER))}
    sm['gate'] = next((w['day'] for w in rows if w['gate_open']), None)
    sm['ceil1'] = next((w['day'] for w in rows if w['capped_pages'] > 0), None)
    sm['ceil_all'] = next((w['day'] for w in rows if w['capped_pages'] == w['pages']), None)
    for d in (1, 30, 90):
        sm[f'p{d}'] = g(d, 'posts_day'); sm[f'v{d}'] = g(d, 'views_day'); sm[f'c{d}'] = g(d, 'cost_day')
    return sm


SENS_SCALE = [
 ('Funnel rates −50% (views→clicks ×0.5)', dict(click_mult=0.5)),
 ('Funnel rates +50% (views→clicks ×1.5)', dict(click_mult=1.5)),
 ('Trial Reel reach 35% → 15%', dict(tr_reach=0.15)),
 ('Trial Reel cap 20 → 5 per page per day', dict(tr_cap=5, tr_warm=5)),
 ('Page ceiling 600K → 300K views/page/day', dict(page_ceiling=300000)),
]

SC_CSV_COLS = ['pages', 'masters', 'ig_main', 'ig_trial', 'fb_posts', 'tt', 'yt', 'threads', 'x', 'posts_day', 'posts_total',
               'views_ig', 'views_fb', 'views_tt', 'views_yt', 'views_th_x', 'views_day', 'views_total', 'link_clicks',
               'landing', 'new_buyers', 'buyers_total', 'active_members', 'coached_members', 'MRR', 'retained_MRR',
               'rev_day', 'gen_cost', 'paid_spend', 'fixed', 'review_min', 'cost_day', 'margin_pct', 'cash',
               'booked_MRR', 'contracted_30d', 'cash_plus_contracted']


def sc_verify_csv(path=None):
    """R30A against the approved file: per column (max abs error, max relative error, worst day)."""
    import csv as _csv, os as _os
    path = path or _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'data', 'projection_aggressive_central.csv')
    with open(path, newline='') as f:
        ref = list(_csv.DictReader(f))
    rows = sc_run(R30A, days=len(ref)); out = {}
    for c in SC_CSV_COLS:
        worst = (0.0, 0.0, None)
        for w, x in zip(rows, ref):
            a, e = float(w[c]), float(x[c]); err = abs(a - e); rel = err / max(1.0, abs(e))
            if err > worst[0]:
                worst = (err, rel, w['day'])
        out[c] = worst
    return out


def main_scale():
    res = [(r, sc_run(r)) for r in RUNS_SCALE]
    print(f"{'run':4s} {'p/d30':>6s} {'v/d30':>7s} {'v/d90':>7s} {'bk30':>7s} {'rt30':>7s} {'rt60':>7s} {'rt90':>7s} {'rt180':>8s}"
          f" {'bk100K':>6s} {'rt100K':>6s} {'bk250K':>6s} {'rt250K':>6s} {'low':>7s} {'be':>3s} {'mg30':>5s} {'gate':>4s}")
    for r, rows in res:
        sm = sc_summary(rows)
        print(f"{r['name'][:3]:4s} {sm['p30']:6.0f} {sm['v30']/1e6:6.2f}M {sm['v90']/1e6:6.2f}M {sm['bk30']/1e3:6.1f}K {sm['rt30']/1e3:6.1f}K"
              f" {sm['rt60']/1e3:6.1f}K {sm['rt90']/1e3:6.1f}K {sm['rt180']/1e3:7.1f}K {str(sm['bk100K']):>6s} {str(sm['rt100K']):>6s}"
              f" {str(sm['bk250K']):>6s} {str(sm['rt250K']):>6s} {sm['low']/1e3:6.1f}K {str(sm['be']):>3s} {sm['mg30']:5.1f} {str(sm['gate']):>4s}")
    worst = max(v[1] for v in sc_verify_csv().values())
    print('R30A vs data/projection_aggressive_central.csv: worst relative error', f'{worst:.2e}')
    return res

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--max': main_max()
    elif len(sys.argv)>1 and sys.argv[1]=='--scale': main_scale()
    else: main(sys.argv[2] if len(sys.argv)>2 and sys.argv[1]=='--json' else None)
