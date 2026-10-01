# Yang Mun post database: findings

Built 2026-09-30. Data files are in `/home/claude/rebuild/data/`: `posts.csv`, `posts.xlsx` (11 sheets), `analysis.json`, `comment_insights.json`, `transcripts/` (64 Whisper transcripts), `tt/comments_*.json`, `yt_comments/`, `thumbs/sheet_*.jpg` (contact sheets used for visual coding) and `scripts/` (the pipeline can be re-run).

How to read the numbers:
- **rel** means relative performance: a post's views divided by the rolling median of the same account's 15 nearest posts in time. This controls for the account's large decay over time, so rel = 1.0 is a normal post for that period and 10 is a breakout.
- All rates (likes/views, comments/views, shares/views) are medians of per-post ratios.
- A cell marked **(inferred)** was coded by rules and then reviewed by hand. It was not observed directly.

---

## 0. Coverage (what was pulled vs what exists)

| Platform / account | Exists (public count) | Rows in DB | Full metadata | Transcript / visual | Why the rest is missing |
|---|---|---|---|---|---|
| TikTok @yangmun2 | 63 on profile counter (66 in feed listing) | **66** | **66** (views, likes, comments, shares, saves, exact timestamp, duration, caption) | **64/66 transcribed** (2 have music only, no voiceover); **66/66 covers visually coded** | Complete |
| TikTok comments | n/a | **2,854 comments** on the top 20 videos (up to 150 each) | text and likes (region field is empty) | n/a | Complete for the top 20 |
| YouTube @Yangmunv2 shorts | 105 | **105** | views and title: 105/105. Likes, date, duration: **23/105** | **105/105 thumbnails visually coded**, with on-screen text read from 40 of them | YouTube returned "Sign in to confirm you're not a bot" after about 12 requests. The fetcher retried at 1 request per ~10 min for the whole session. I did not bypass the bot check. |
| YouTube long videos | 21 | **21** | views and title | n/a | same |
| YouTube comments | n/a | 300 (the 12M and 953K shorts) | text | n/a | same bot check |
| Instagram @yangmunus | 403 posts | 18 known shortcodes (16 from the brief + 2 found by web search: `DRVIXpQD4aV`, `DTfpax6ACjr`) and **18 reels observed in the brief** (views, plus likes and comments for the onion reel) | **0 shortcodes returned metadata** | visual description from the brief | Every Instagram request returned **HTTP 429**. The fetcher backed off 7–15 min per attempt all session. The profile feed endpoint required login. Mirror sites: imginn, picuki, pixwox, imgsed, piokok and picnob returned 403. Inflact is gated by Cloudflare Turnstile, which I did not bypass. dumpor/greatfon/anonyig are JS shells with no data. Instagram "popular" pages are blocked by robots.txt for WebFetch and return an empty shell to curl. |
| Instagram @itsyangmuns | 353 posts | 16 known shortcodes | 0 | none | same |
| Threads @yangmunus / @itsyangmuns | 40.1K followers | 0 rows. Found 2 post URLs by search: `@yangmunus/post/DTDpAUUgN_f` ("Feeling stuck is not a failure"), `@itsyangmuns/post/DQkgSS8kmRc` ("This eBook explains how to restore your body's natural…") | 0 | none | Blocked by robots.txt for WebFetch; curl gets a login shell |
| Facebook page | ~1.4M followers | 0 | 0 | none | Blocked by robots.txt for WebFetch; curl returns an error/login page |

**Instagram totals:** 34 of ~756 shortcodes known (4.5%), 0% with metadata, and 18 brief observations used as the Instagram sample. Instagram conclusions below therefore rest on 18 observed reels (median 182.5K views, range 90.9K–1M), not on a full pull. A fetcher is still retrying. Re-running `python3 scripts/build.py && python3 scripts/analyze.py && python3 scripts/export.py` merges any rows it gets.

Other data picked up along the way:
- Third-party estimates for @yangmunus: 2,523,376 followers, **30-day follower change of −0.14% (about −3.3K in Sep 2026)**, 396 posts (HypeAuditor).
- Copycat accounts exist: IG @yangmunreal and @yangmunus.ig, YouTube @monkyangmun.
- A public critic reel titled "Yang Mun is a scam" exists (`DRC8j1PkVOK`).

---

## 1. Headline numbers per platform

| | TikTok (66) | YT shorts (105) | YT long (21) | IG main (18 observed, Sep 2026) |
|---|---|---|---|---|
| Total views | 15.21M | 17.50M | 19.4K | 4.68M (18 reels) |
| Median views | **3,257** | **2,100** | 464 | **182,500** |
| Mean views | 230K | 167K | 926 | 260K |
| p10 / p90 | 1,060 / 174K | 573 / 160K | 302 / 1,000 | 97K / 430K |
| Max | 8.3M | **12.0M** (the "11.5M" video Shalev bragged about is almost certainly this: `j8WRhcQvzRM`) | 7.8K | 1.0M (onion) |
| Top 1 post as share of all views | **54.6%** | **68.6%** | 40% | 21% |
| Top 3 posts as share of all views | **82.7%** | **80.3%** | 56% | 40% |
| Like rate | 4.9% | 5.6% (recent) / 2.5–3.0% (mega-hits) | n/a | 3.9% (onion) |
| Comment rate | 0.43% | 0.55% | n/a | 1.03% (onion, "comment HEAL") |
| Share rate | 1.35% | n/a | n/a | n/a |
| Save rate | 0.99% | n/a | n/a | n/a |
| Median duration | 74.5s | 39s (recent) | 6–12 min | n/a |

**Reach is driven by rare hits.** On both TikTok and YouTube, 3 posts produced more than 80% of all views. Everything else is a lottery ticket.

---

## 2. Timeline: launch spike, a 9-month gap, and a revival that barely reached anyone

**TikTok:**

| Month | Posts | Median views | Total views | Median duration |
|---|---|---|---|---|
| Oct 2025 | 16 | 73,800 | 14.36M | 83.5s |
| Nov 2025 | 5 | 47,300 | 375K | 107s |
| (18 Nov 2025 to 24 Aug 2026: **zero posts for 279 days**) | | | | |
| Aug 2026 | 11 | 1,221 | 89K | 68s |
| Sep 2026 | 34 | 1,882 | 384K | 43.5s |

- **Launch era** (Oct–Nov 2025, 21 posts): median 70.8K views, 14.7M total.
- **Return era** (Aug–Sep 2026, 45 posts): median 1.87K views, 473K total.

That is a **−97% drop in median reach**. Engagement quality did not change: like rate was 4.87% in the launch era and 4.92% in the return era. Viewers who saw the videos reacted the same way; far fewer were shown them.
- (inferred) This pattern fits an account-level distribution penalty, such as TikTok's "unoriginal / AI" enforcement, dormancy, or both. The brief notes TikTok demonetizes AI-grandma accounts.

**YouTube shorts by feed position (0 = newest):**

| Positions | Posts | Median views |
|---|---|---|
| 91–104 (~Nov 2025) | 14 | 20.5K (includes the 12M) |
| 81–90 | 10 | 183K |
| 70–80 | 11 | 63K |
| 61–69 | 9 | 2.4K |
| 41–60 | 20 | 1.85K |
| 21–40 | 20 | 970 |
| 0–20 (Sep 2026) | 21 | **646** |

- Dated anchors: the 12M short is from 2025-11-10 and the 953K short from 2025-12-05. The Sep 2026 shorts went up at **2 per day** and get 120–1,300 views each.
- The 35 oldest shorts have a median of 64K views. The 70 newest have a median of 1.3K (−98%).

**Instagram is the only channel still healthy.** The same asset posted in Sep 2026 performed very differently across platforms (IG numbers from the brief, TikTok and YouTube numbers from this DB):

| Asset (identical or near-identical script) | IG @yangmunus | TikTok | YouTube | IG ÷ TikTok |
|---|---|---|---|---|
| "Put honey on the tomato and see what happens" | 305K | 7.3K | n/a | **42×** |
| "If you have anxiety stuck in your head and chest" (foot point) | 173K | 1.9K | n/a | **92×** |
| "Sesame oil trick from the monastery" (behind the ear, sleep) | 131K | 1.7K | 0.4K (Y23, visual match) | **76×** |
| Standing on salt / salt under feet | 168K | 53.6K | 563 | 3× |
| Cabbage leaves on the back for pain | 111K | 58.7K | 478 | 1.9× |
| Cucumber + lime/lemon | 233K (cucumber/lemon/mint water, similar) | 1.8K | 3.1K + 2.2K (posted twice) | ~100× |

**Rule 0:** the creative is the same; the account's distribution state and the platform explain 40–100× differences. Plan for account health first and creative second.

**Posting automation:** 64% of return-era TikToks were published exactly on the hour (hh:00:00), which points to a scheduler. The launch era had 0% on the hour, so those were posted by hand. Return-era slots fall at 8–11am ET, and TikTok averages 1.6 posts per active day. YouTube posted in pairs daily. Instagram's ~1.1 posts/day per account is estimated from 403 posts in about 12 months.

**Re-uploads don't recover reach:**
- The 8.3M TikTok script was re-uploaded verbatim to the same account 10 days later and got 39.8K (−99.5%).
- On YouTube, 12 duplicate pairs were posted (for example "Who Is Master Yang Mun…" twice, "Do What's Best for You" twice, "Squeeze lemon on cucumber" twice). Each copy performs about like any other post of its period.

---

## 3. What wins: topic × hook × format × length

### 3a. Winners (all posts, launch era)

The 10 biggest posts across platforms:

| Views | Platform | Spoken/title hook | Topic | Hook type | Duration |
|---|---|---|---|---|---|
| 12.0M | YT | "You're Drinking Water the WRONG Way" (on-screen: "One small cup before sleep helps your body wash away the day's toxins") | kitchen remedy (water) | myth / wrong-way | 96s |
| 8.3M | TT | "If you drink hot water every morning on an empty stomach, listen carefully, because this simple habit can truly change your body." | kitchen remedy (water) | if you do X → outcome | 77s |
| 3.3M | TT | "There are five signs your body carries too much sugar, and if you ignore them, they slowly, quietly harm your health." | blood sugar | list + warning | 109s |
| 1.1M | YT | "1 minute of Yang Mun Wisdom" | quote/motivation | authority | n/a |
| 1.0M | IG | onions dropped into a pot of water, "comment HEAL" | kitchen remedy | n/a | n/a |
| 972K | TT | "The number one anti-aging vegetable in the world is not kale, not even spinach, and not broccoli either." | longevity | myth / not-X | 97s |
| 953K | YT | "The Hidden Cause of High Blood Pressure: Potassium Deficiency Explained" | blood pressure | hidden cause | 106s |
| 542K | TT | "Five painful signs your kidneys may already be crying for help." | organ warning signs | list + warning | 86s |
| 531K | TT | "If you drink warm water with three cloves of garlic every morning on an empty stomach, your body will begin to change in ways you cannot imagine." | kitchen remedy | if you do X → outcome | 83s |
| 521K | YT | "Words of Motivation from Yang Mun" | motivation | statement | n/a |

What the mega-hits have in common:
1. An **ordinary item everyone owns**: water, garlic, sugar, a vegetable.
2. A **daily habit or warning** in the first sentence, 13–22 words, spoken at elder pace (**2.3 words/sec, about 138 wpm**).
3. **77–110 seconds** long.
4. The **classic static set**: seated on the floor at a low wooden desk, open book, candle, temple interior. 19 of the 21 launch-era TikToks used this set.
5. Kinetic word-by-word caps captions in yellow and white.
6. A **spoken comment-keyword CTA near the end** ("If you listen till the end, comment hot water").

The 8.3M video's comments are full of "Hot water" and "Hort Water".

### 3b. Return era (Aug–Sep 2026): the regime we will actually face

These are TikTok return-era medians (n = 45). IG observations confirm the same direction.

- **Format** (visually coded from covers):

| Format | n | rel |
|---|---|---|
| Body demo on self (acupoint/limb) | 4 | **2.34** |
| Food/recipe demo | 13 | **1.42** |
| Patient/second-person demo | 7 | 1.08 |
| Inset/diagram | 5 | 1.00 |
| Plain talking head | 10 | **0.71** |
| Classic desk (now stale) | 1 | 0.70 |
| Symbolic prop (chalkboard/mug) | 5 | **0.72** |

  On IG (brief sample), food/prop demos have a median of **410K vs 182.5K overall (rel 3.3)**, and symbolic props (skeleton, birdcage, phone+hammer, Q&A sticker) are the weakest at median 96K.

- **Duration:** 45–59s rel 1.19, 30–44s 1.15, under 30s 1.10, 60–89s 0.95, **90s+ 0.70**. Across all TikToks, Spearman correlation of rel with duration is −0.18. The launch era rewarded 80–110s monologues; the current regime rewards **30–59s demos**.

- **Topic:**

| Topic | Result |
|---|---|
| Blood sugar/BP | SP10 point "If your blood sugar is always high, do exactly what I am doing right now": **186K, rel 87**, the only return-era breakout |
| Longevity | rel 6.4 |
| Body/acupressure | 3.6 |
| Spiritual quotes | 1.9 |
| Gut | 1.7 |
| Kitchen remedy | 1.2 |
| Anxiety | 1.0 |
| Relationships | 0.76 |
| Sleep | 0.70 |
| Overthinking | 0.82 |
| Weight | **0.64** |

  Mind/relationship/sleep monologues are the bottom tier on TikTok. On YouTube they did well in the launch era (quotes and wisdom: median 188K across 13 shorts, nearly all from the Nov–Dec 2025 window, rel 2.2), and on IG they were moved to @itsyangmuns, whose median is only ~38K and decaying per the brief.

- **Hook type, return era, TikTok:**

| Hook type | rel |
|---|---|
| Authority ("elders in our monastery…", "I am over one hundred years old…") | 2.65 |
| Curiosity ("…and just watch what happens") | 2.06 |
| Story ("My mother used this remedy…") | 1.74 |
| Statement | 1.08 |
| Symptom "If you have X" | 0.86 |
| List | 0.95 |
| Question | **0.70** |
| How-to ("How to fall asleep fast…") | **0.61** |

  Across all eras, "if you do X → outcome" had the highest rel (5.5) and took 59% of TikTok views, and myth/"you're doing it wrong" was next (3.0). Question and how-to openers are consistently the bottom.

- **Claim strength:** strong claims ("instantly", "in one night", "clears the sugar from your veins", "never needed a hospital") do **not** outperform soft ones once decay is controlled. TikTok return era: strong rel 1.00, soft rel 1.00, none 0.88. All TikToks: strong 1.11, soft 1.00. On YouTube, strong claims have a median of 1.7K vs 1.5K for soft. **The reach comes from the specific everyday ingredient or body point and the visible demo, not from the size of the promise.** That is good news for a compliant rebuild.

### 3c. Top vs bottom decile (TikTok, by rel)

- **Top 10%** (rel ≥ 11.6): median duration **46s**. Formats: 3 classic desk, 2 patient demo, 1 self body demo, 1 food demo. Topics: 3 kitchen remedy, 2 BP/sugar, 1 pain, 1 longevity. Claims: 5 of 7 soft.
- **Bottom 10%** (rel ≤ 0.39): median duration **80s**. Hooks: 2 questions, 2 symptom "if you have X", 1 how-to, 1 geo callout. Formats: 2 plain talking head, 2 classic desk, 1 symbolic prop. Topics are scattered (mind, anxiety, sleep, pain).
- Among engagement metrics, **share rate correlates most with outperformance** (Spearman with rel: 0.34), ahead of comment rate (0.22) and like rate (0.13).

---

## 4. CTAs and comment-bait inflation

60 of 64 transcribed TikToks end in a spoken CTA:

| CTA type | n | Median views | rel | Comment rate | Like rate |
|---|---|---|---|---|---|
| Keyword bait, no DM promise ("comment yes / balance / hot water / still / joy") + link | 12 | 67.8K | **3.38** | 0.65% | 4.6% |
| Keyword → DM lead magnet ("comment HEAL / sugar / calm / Journey and I'll send it") | 10 | ~2K | 1.0–3.1 | **0.80–1.5%** | 4.6–5.9% |
| Geo bait ("comment your country / USA") | 3 | 51–90K | 1.0–1.6 | 0.7–0.9% | 4.5–8.6% |
| Link in bio only | 21 | 26.8K | 0.96 | **0.24%** | 4.9% |
| None | 7 | 1.8K | 1.00 | 0.32% | 4.4% |

- **Keyword bait raises comment rate 2.7–3.4× and leaves like rate unchanged.** Comment counts on these accounts are therefore inflated signals, not deeper engagement.
- In the comment sample, **30.6% of comments are one or two word bait replies.** The most common: yes (412), balance (107), sugar (103), milk thistle (79), ebook/e-book (76), amen (31).
- The IG onion reel's 10.3K comments (1.03%) are the same effect.
- Lead-magnet keywords they use: HEAL → the *Time to Heal* ebook, "sugar" → "free guide", "calm" → "full guide… for free", "Journey" → the 30-day program. "Follow me first, then comment sugar" is on the 186K breakout, so they gate the lead magnet behind a follow.

**Geo bait backfires.** The on-screen hook "If you're not from USA Please scroll ‼️" appears on T10 and T20. "Comment your country" is spoken in 3 posts. Country mentions in comments:
- **US or US states: 117**
- **South Africa: 96**
- Jamaica 25, Uganda 25, Ghana 17, Philippines 14, Kenya 11, Canada 11, UK 11, Zambia 11, Trinidad 9, Nigeria 8

So **non-US mentions outnumber US mentions 2.6 to 1** (308 vs 117). The bait pulls in low-monetization geographies.

---

## 5. Audience signals from comments

Sample: 3,154 comments (2,854 TikTok, 300 YouTube). Counts are regex-based lower bounds.

| Signal | Count | Share |
|---|---|---|
| Gratitude / blessing ("thank you sir/master/teacher", 🙏) | 968 | 30.7% |
| Christian/religious language (God, Jesus, Amen, pray) | 106 | 3.4% |
| Purchase or product intent ("E book please", "ebook", "send me", "link") | 207 | 6.6% |
| "Is this AI / fake" (mostly the single word "AI"/"ai", plus "Is this AI?", "AI generated I thought you were real 😂", "I can't tell what's Ai and what's real any more 😭") | 27 | 0.9% |
| Skeptic / objection (scam, dangerous, see a doctor) | ~1 | ~0% on these posts |
| Personal health disclosure | 32 | 1.0% |
| Questions (containing "?") | 53 | 1.7% |

- The **audience barely questions the persona** (under 1% flag AI). The Christian framing ("Thank you father", "Amen", "God bless") says the buyer is an older, church-going, English-second-language or Global South viewer at least as often as a US woman aged 55–75.
- Age and gender cues are very sparse in comments this short (fewer than 1% carry them). One example is the top-liked comment: "true i am 53 y/o I been using this since very long…". IG comments were not retrievable. Per the brief they skew to US women 55–75 with confessional stories, so IG is probably the better US-female channel.
- **Recurring conditions mentioned:** blood sugar/diabetes (136 comments, 4.3%; partly the "comment sugar" bait); then skin/aging, blood pressure, cholesterol/heart (9 each); kidney and immunity/mucus (8 each); gut (7).
- **Questions they ask:** "what are the dangers of using garlic", "How old are you, may I ask?", dosing (how much, how often, "can I take with medication"), and "I cannot take garlic… I suffer from gastritis, GERD and ulcers". The practical need is a **safety and contraindication layer**, which Yang Mun never addresses.

---

## 6. Other findings

- **The persona's credibility claims are fabricated, and they help reach.** Examples: "I am over one hundred years old, and I have never once needed a hospital" (TikTok rel 4.4); "my teacher, Dr. Li Zhang Sheng, he lived to be 102"; "Monks like me have eaten one meal a day for over 2,000 years"; "I spent decades helping people in China villagers"; "40 years of Chinese medicine". Authority hooks have the highest return-era rel (2.65).
  - Implication for us: we need an **honest authority device that works as well**. Chang Yin's visible strength is the proof, and a named credentialed human reviewer is the backing (see rules).
- **Anti-doctor / anti-pharma lines** appear in 8 TikToks ("Pharmacies hate this", "Western doctors stay silent", "without the burden of pills"). Median rel 1.56 vs 1.00 without, on a small n. The lift is not worth the FTC and platform risk.
- **The Asian elder aesthetic changed.** Launch era: one consistent set (black or orange robe, floor desk, book, candle). Return era: randomized robes (maroon, saffron, navy, brown), sets (courtyards, forest rock, English cottage garden, mountain) and props. The IG main account (maroon robe, props) still works, which suggests the **scene rotation isn't what hurts TikTok; account state is**.
- **YouTube long-form failed:** 21 meditation/essay videos of 6–12 min, median 464 views, max 7.8K. Guided meditations reached nobody. This does not argue against long-form in general, but a mass-produced AI meditation library gets no discovery.
- **The "#podcast" shorts are not podcasts.** Visually they are the same solo desk shot, with #podcast #helpmemakethismakesense hashtags. They got 10K–259K in the launch era; the hashtag was a discovery hack, not a format.
- **Hashtags:** #usahealth #usa #wellness #newyork #trump #chinesemedicine #healthybodyhealthymind #wellnessjourney. Captions are often hashtags only (TikTok launch era: "#usa🇺🇸 #newyork #trump #chinesemedicine"). There is no measurable caption effect; the hook lives in the voiceover and on-screen text.

---

## 7. The 15 best hooks, verbatim

The full ranked 50 are in `posts.xlsx`, sheet "Hooks Verbatim".

1. "You're Drinking Water the WRONG Way 😳" (YT title, 12.0M)
2. "If you drink hot water every morning on an empty stomach, listen carefully, because this simple habit can truly change your body." (TT, 8.3M)
3. "There are five signs your body carries too much sugar, and if you ignore them, they slowly, quietly harm your health." (TT, 3.3M)
4. "The number one anti-aging vegetable in the world is not kale, not even spinach, and not broccoli either." (TT, 972K)
5. "The Hidden Cause of High Blood Pressure: Potassium Deficiency Explained" (YT, 953K)
6. "Five painful signs your kidneys may already be crying for help." (TT, 542K)
7. "If you drink warm water with three cloves of garlic every morning on an empty stomach, your body will begin to change in ways you cannot imagine." (TT, 531K)
8. "After dinner want to burn sugar fast?" (IG, 474K)
9. "If your blood sugar is always high, do exactly what I am doing right now." (TT, 186K, rel 87)
10. "3 Things to Say Every Morning to Change Your Entire Day" (YT, 372K)
11. "My friend, they lied to you again. They tell you the strongest anti-inflammatory foods are turmeric, ginger, blueberries." (TT, 162K)
12. "Put honey on the tomato and see what happens." (IG, 305K)
13. "Put turmeric on garlic, my friend, and just watch what happens." (TT, 64K, rel 56)
14. "If you are in pain, do not put fancy creams on your back." (TT 58.7K / IG 111K)
15. "Stand on natural salt for 10 minutes and watch your body change." (TT 53.6K / IG 168K)

**Hook grammar that wins:**
- Name an everyday object or body spot, a time anchor (every morning, empty stomach, before bed, after dinner) and an implied transformation, in 13–22 words.
- Or a contrarian "not X, not Y" or "they lied".
- Put the object in the first 3 words when there is a demo ("Put honey…", "Stand on salt…", "Squeeze lime…").

---

## 8. 25 rules for the Chang Yin / Sun Yoon rebuild

**Do:**

1. **Lead with a visible physical demo, 30–59s.** Return-era winners are body-on-self demos (rel 2.3) and food demos (rel 1.4; IG median 410K). Chang Yin demonstrates on his own body: a movement, a stretch, a point, a lift. Put his strength in frame in the first second.
2. **Put the object or body part in the first three words.** "Put honey on the tomato…", "Stand on salt…", "Press this spot…". The launch mega-hits named water, garlic or sugar in the first sentence.
3. **Use the winning hook set:** "If you [daily action] every [time anchor], [transformation]" (rel 5.5, 59% of TikTok views); "The number one ___ is not X, not Y" (myth, rel 3.0); "…and just watch what happens" (rel 2.1). Keep a bank of 50+ variants per topic.
4. **Write the first line in 13–22 words at about 2.3 words/sec** (elder pace). Total script of 70–130 words for 30–59s.
5. **Build a "curiosity + proof" series around everyday US kitchen items** (water, garlic, lemon, honey, tomato, cucumber, cabbage, salt, ginger, cinnamon, oats, eggs). 6–7 of the top 10 posts across platforms name one (water ×2, sugar, onion, a vegetable, garlic, potassium). Use honest benefit framing ("may help", "why this works: …").
6. **Prioritize topics by return-era rel:**
   - First: blood sugar and blood pressure, longevity and "stay strong at any age", body/acupressure/mobility, gut.
   - Second: pain, kitchen remedies, anxiety breathwork.
   - Last on TikTok: sleep, relationships, overthinking, weight. Route mind and relationship content to Sun Yoon and IG, where the brief shows confessional comments.
7. **Replace fake authority with real proof.** Their authority hooks win (rel 2.65), but they rest on "I am over one hundred", "my teacher lived to 102" and "monks like me". Our equivalents are the jacked physique shown lifting, "Here's the mechanism" (insulin, nitric oxide, vagal tone), and a named credentialed reviewer in the caption. Never invent ages or teachers.
8. **Use keyword-to-DM CTAs that deliver a real lead magnet**, and read the comment numbers skeptically. Keyword bait lifts comment rate about 3× with no like lift. A lead magnet ("comment STRONG and I'll send the 7-day routine") produces qualified leads, which ManyChat on IG and FB can route (not TikTok in the US).
9. **Gate the lead magnet behind a follow, gently.** Their only return-era breakout uses "Follow me first, then comment sugar." Test "follow + keyword" vs keyword only.
10. **Give most of the budget and posting volume to Instagram.** The same assets did 40–100× better on IG than on TikTok or YouTube in Sep 2026. Treat TikTok and YouTube as fresh, labeled, original-content accounts, not dumping grounds for cross-posts.
11. **Plan for power laws:** 3 posts = 80%+ of all views. Volume (6–9 per day across pages) buys lottery tickets. Within 24h, turn any post above 5× the account median into 5–10 new variants (new object, same hook grammar). Don't re-upload the same file: the re-upload fell from 8.3M to 39.8K.
12. **Track shares, not comments.** Share rate correlates most with outperformance (0.34 vs comments 0.22 and likes 0.13). Add share triggers ("send this to someone who still ___") like their 8.3M close.
13. **Carry the hook in kinetic on-screen text (word-by-word, high contrast) and a top text box.** Their mega-hits used large yellow and white word-by-word captions; the return era moved to small lower-center captions and a top text box. Test both. Never use gray text.
14. **Answer the safety questions the comments ask.** Examples: "dangers of garlic", "I have gastritis/GERD", "can I take it with medication". Add a 3-second "skip this if you take ___ / have ___" line. It builds trust and meets the "competent and reliable evidence" standard.
15. **Target US viewers with US cues, not geo bait.** Mention US store items and US schedules, and use the IG AI label so reach isn't suppressed. The comment sample runs 2.6:1 non-US to US.
16. **Post on a scheduler, 8–11am ET plus an evening slot.** They schedule on the hour (64% of return-era TikToks). The timing data is thin (n = 45, no clear winner), so treat this as a slot test, not a finding.
17. **Rotate sets and wardrobe, but keep one signature anchor.** Their launch identity (floor desk, open book, candle) was instantly recognizable. Ours could be a wooden training yard, kettlebell and tea table. The return-era randomization didn't hurt IG.
18. **Use a second person on screen for pain and body topics.** Patient demos worked: cabbage on the back got IG 111K / TikTok 58.7K, salt under the feet got IG 168K / TikTok 53.6K. Sun Yoon can be the "patient", the skeptic or the blunt reality check. Their format already proves two-person scenes work.

**Don't:**

19. **Don't lead with mind, relationship or quote monologues on TikTok or YouTube Shorts.** They sit in the bottom tier (return-era rel 0.64–0.82). Quotes only worked in the Nov–Dec 2025 YouTube window (188K median). Keep them for IG second pages and Sun Yoon.
20. **Don't use disease-cure or "instant" claims.** Strong claims don't outperform once decay is controlled (TikTok return era: strong rel 1.00 = soft rel 1.00). They carry FTC, platform-policy and press risk; the EBU and Columbia exposés quote exactly these lines.
21. **Don't use anti-doctor or anti-pharma framing.** ("Pharmacies hate this", "Western doctors stay silent".) Its small lift (rel 1.56, n = 8) doesn't justify the risk. Frame the content as "what to ask your doctor" plus mechanism.
22. **Don't use geo bait** ("If you're not from USA please scroll", "comment your country"). It floods comments with non-US viewers (South Africa alone nearly equals the US).
23. **Don't post 90s+ monologues in the current regime** (rel 0.70). Don't run open-ended question hooks ("What kind of exercise does your liver like most?", rel 0.70) or "How to…" openers (rel 0.61).
24. **Don't mass-produce AI meditation long-form.** 21 videos got a median of 464 views. Long-form only makes sense for a proven short topic, filmed as a real routine (a follow-along strength or mobility session).
25. **Don't dump cross-posts or duplicates.** YouTube carried 12 duplicate pairs, TikTok got a verbatim re-upload, and the 9-month TikTok gap preceded a −97% reach collapse. YouTube's July 2026 inauthentic-content policy targets exactly this templated repetition. Give each page its own script variants and keep posting continuously.

---

## 9. Method notes and caveats

- **Topic, hook, claim and CTA** were rule-coded from Whisper transcripts (TikTok), titles plus on-screen text (YouTube) and brief descriptions (IG), then corrected by hand. 178 rows carry manual topic/hook corrections or visual-format overrides.
- **Formats** were visually coded from 171 covers/thumbnails, stored as contact sheets in `data/thumbs/`. They reflect the cover frame, not every second of the video.
- **Topic taxonomy:** kidney or organ warning signs, fasting and fatigue were coded "other". Morning-routine and "stay healthy at any age" content was coded longevity/aging.
- **Relative performance** uses a centered rolling median (window 15, minimum 5). IG brief rows use the brief's stated median of ~125K. Group sizes are small (often n < 10), so treat a rel difference under about 1.5× as noise.
- **YouTube:** likes, dates and durations exist for only 23 recent shorts plus 2 mega-hits. The duration and CTA cuts for YouTube are therefore unreliable, and the CTA was not observable because there were no transcripts.
- **Comments:** 3,154 comments from 22 posts (top TikTok plus 2 YouTube). IG comments are missing, and those are the likely home of the US women 55–75 described in the brief.
