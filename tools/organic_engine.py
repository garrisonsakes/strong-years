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
        cost=(s['fixed']+s['shop_plan'])/30 + od['posts']*s['cost_post']
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
        c_org=fe_cvr(r,r['cvr_org']); c_cold=fe_cvr(r,r['cvr_cold']); c_warm=fe_cvr(r,r['cvr_warm'])
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
        costs=sp*(1+s['media'])+shp*s['sh_cost']+comm+(s['fixed']+s['shop_plan'])/30+od['posts']*s['cost_post']+mem_all*(s['cogs']+s['varm'])/30+(E+P)*s['bump29_take']*s['kit_cogs']
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

if __name__=='__main__':
    main(sys.argv[2] if len(sys.argv)>2 and sys.argv[1]=='--json' else None)
