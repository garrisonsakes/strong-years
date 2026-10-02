# ENGINE_NEXT50.md: the next 50 improvements per layer (beyond ENGINE_100X.md)

Round of Oct 2 2026. Inputs: ENGINE_100X.md (the first 10 per layer, 13 holes, sources S1–S61), VIRALITY_SYSTEM.md, STACK_FINAL.md, BRIEF.md CANON UPDATE 4, plus a scan of `workers/`, `tools/`, `app/`, `shopify/` and `production/`. I ran 12 web searches and 8 fetches, only to support claims that needed a citation. Nothing was spent, no accounts were created, and no generation or external AI calls were made.

**How to read the multipliers.** Each item names one metric and gives an estimated multiplier (2×, 3× or 5×) **on that metric, for the slice of posts or users the item touches**, against the current canon. These are planning estimates, not forecasts. They do not stack: two 2× items on the same metric will not give 4×. Unless an item cites a source, treat the multiplier as an assumption **[A]** that the learning loop (§6) has to confirm. Confidence: **H** = the mechanism is documented and we control it; **M** = the mechanism is documented but the size is a guess; **L** = plausible but unproven. Guard items, which stop a loss rather than create a gain, are written as "avoids ÷N".

**Dedupe rule.** I left out anything already in ENGINE_100X.md §1–11, even under a different name. Where an item builds on an ENGINE_100X item, it cites it (for example "extends 100X §2.1").

**New sources** (S1–S61 refer to ENGINE_100X §12):
- N1: Trial Reel daily caps are not published. One podcast claims caps can be "as low as five" per day, with a 30-day Trial-Reel block for exceeding them. This is anecdotal and secondary. [riffon](https://riffon.com/insight/ins_3i06y6zoclgb) · [ALM Corp](https://almcorp.com/blog/instagram-schedule-trial-reels/)
- N2: Instagram can automatically share a Trial Reel with followers if it performs well on views within 72 h. The in-app scheduler allows 25 scheduled posts per day, up to 30 days ahead. [ALM Corp](https://almcorp.com/blog/instagram-schedule-trial-reels/) · [Meta Trial Reels](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first-see-what-perfoms-best/)
- N3: Facebook Trial Reels exist for Pages and professional-mode profiles, with an uneven rollout. Facebook and IG trials run separately. Secondary source. [lesliemlyon](https://lesliemlyon.com/facebook-trial-reels/)
- N4: Facebook Reels A/B testing allows "up to four different captions or thumbnails", and the winner is shown automatically. [About Meta, Nov 2023](https://about.fb.com/news/2023/11/helping-creators-test-content-and-earn-rewards/). Instagram has the same caption and thumbnail test. [MyMobile](https://www.mymobileindia.com/instagram-reels-ab-testing-update/)
- N5: Meta AI translation of Reels is free, with a voice clone and optional lip-sync. Languages include English, Spanish and Korean (list updated Jul 14 2026). Facebook creators need 1,000+ followers; every public IG account qualifies. Output is labelled "Translated with Meta AI". [About Meta](https://about.fb.com/news/2025/10/discover-reels-around-world-meta-ai-translation/)
- N6: YouTube auto-dubbing is open to all creators in 27 languages (Feb 2026). [Social Media Today](https://www.socialmediatoday.com/news/youtube-expands-auto-dubbing-to-all-creators/811375/) · [gHacks](https://www.ghacks.net/2026/02/05/youtube-makes-auto-dubbing-available-to-all-creators-worldwide/)
- N7: Instagram has a viewer Repost button; reposts appear to the reposter's followers. [Buffer](https://buffer.com/resources/repost-on-instagram/)
- N8: Threads Communities are topic communities open to all users (Oct 2025), with badges for highly engaged members being tested (Dec 2025). [About Meta](https://about.fb.com/news/2025/10/introducing-threads-communities-find-your-people/) · [TechCrunch](https://techcrunch.com/2025/12/15/threads-adds-new-communities-tests-badges-for-highly-engaged-members)
- N9: YouTube calls the Shorts "related video" link its most effective tool for turning Shorts viewers into long-form viewers. No numbers are given. [YouTube Blog](https://blog.youtube/creator-and-artist-stories/youtube-related-videos-traffic-guide/)
- N10: Pew's 84% (YouTube) and 71% (Facebook) are **all-adult** figures from the Feb–Jun 2025 survey. VIRALITY_SYSTEM §6 item 6 labels them as 65+ figures, which is wrong (see Holes H1). [Pew fact sheet](https://www.pewresearch.org/internet/fact-sheet/social-media/)

---

## 0. Summary: the 25 highest-multiplier items across all layers

| Rank | ID | Item | Multiplier → metric | Conf |
|---|---|---|---|---|
| 1 | IG-1 | Trial Reels at 10–20/day/page as **distinct REMIX renders** with a cap probe, never hook-swap copies | 5× → hook tests read per page per week | M |
| 2 | IG-2 | The feed post **is** the graduated Trial winner (no second feed copy of the same body) | 3× → follower-feed reach per post | M |
| 3 | MOD-1 | Hook-slice bank: render 4–6 on-camera hook slices per master in one avatar call, then assemble trials from the clean mezzanine | 5× → trial variants per avatar-dollar | M |
| 4 | LL-1 | Trial-only hook lab: score hooks only on Trial Reels (pure non-follower traffic) and feed the factor arms | 3× → hook-effect estimate precision | M |
| 5 | HK-1 | Comment-to-hook pipeline: the top question cluster's asker wording becomes tomorrow's hook text verbatim | 3× → share+save rate on answer posts | M |
| 6 | MON-1 | The Day-1 session plays **inside the DM** (video link plus 3 buttons), then the offer goes out on completion | 3× → DM → paid conversion | M |
| 7 | AO-1 | One-tap "Get Day 2 tomorrow" email capture on the Day-1 completion screen | 3× → view → owned-contact rate | M |
| 8 | FB-3 | Meta AI translation (Spanish) on flagship pages instead of separate Spanish renders at first | 5× → Spanish-language reach per render-dollar | M |
| 9 | TT-11 | YouTube auto-dub (Spanish) on long-form and Shorts | 5× → non-English YouTube views per dollar | M |
| 10 | CH-1 | Weekly numbered "Chang's 12-week arc" (viewers follow one plan in public) | 3× → returning-viewer share | L-M |
| 11 | MON-4 | Strength Age score shared as an image card with a referral link | 3× → referral share rate | M |
| 12 | FB-6 | Weekly real-coach Facebook Live in the Group, cut into 5 Reels | 3× → R3 coaching leads per week | M |
| 13 | AO-3 | Printed Day-1 sheet by mail as a lead magnet for people who won't use a PDF | 3× → 70+ email-to-member rate | L-M |
| 14 | LL-3 | Retention-curve "dip finder": auto-locate the second where viewers leave and send that beat back to the writer | 2–3× → avg watch % on rewrites | M |
| 15 | MOD-6 | Body bank with per-page 30-day reuse ledger, so trials stay distinct without new avatar seconds | 3× → distinct renders per dollar | M |
| 16 | IG-6 | IG Reels A/B on covers and captions for every feed post (up to 4) | 2–3× → plays per impression on grid and profile | M |
| 17 | TT-1 | YouTube Shorts → related long-form link on every Short | 3× → long-form views from Shorts | M |
| 18 | HK-6 | Hook grammar × first-frame object matrix (IF_EVERY × prop-in-hand) as a tested arm | 2–3× → 3 s hold | M |
| 19 | MON-7 | Coach-led R3 waitlist with honest cohort-cap counts, sold from the Group and the live | 3× → R1 → R3 ascension rate | M |
| 20 | TT-17 | Post into Threads Communities (N8), with real coaches replying | 3× → Threads reach | L-M |
| 21 | RO-1 | Trial-cap tripwire: auto-halt trials on the first "unavailable/limit" response or a reach collapse | avoids ÷5 on trial reach for 30 days (N1) | M |
| 22 | CH-5 | Viewer "Strong Weeks" leaderboard read out by Chang (first names, opt-in) | 2–3× → comments per follower | L-M |
| 23 | MON-12 | Annual plan offered at the week-6 plateau inside the app, not by email | 2–3× → annual take rate | L-M |
| 24 | X-H3 | "Adult child" landing and DM path for gift buyers | 3× → FAMILY keyword → gift purchase | L-M |
| 25 | HK-12 | Every 4th script is a "reply video" to a real comment, with the comment on screen | 2–3× → comments per view | M |

---

## 1. Facebook (FB-1 … FB-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **Facebook Trial Reels lane** (N3). A second, separate test audience. Use different hook arms from IG so each platform tests new arms | `tools/posting_rules.py` `fb_trial_reel()`; manual toggle in `packager/fallback.py` post pack until the API exposes it | 2× → FB winners found per week | M-L |
| 2 | **Reels A/B: 4 covers + 4 captions per FB Reel** (N4); the winner shows automatically | `assemble/variants.cover()` loops 4 texts from `hooks.json` siblings; `packager.py` `fb_ab=[...]` | 2× → plays per impression | M |
| 3 | **Meta AI translation to Spanish** on Pages ≥1K followers (N5), labelled; use before funding `@changyin.espanol` renders | Ops checklist; `POSTING_PLAN` espanol start gated on translated-reel reach | 5× → Spanish reach per render-dollar | M |
| 4 | **Group membership questions**: Q3 = "Email for Chang's free Day 1 plan (optional)" with consent text | Group settings; CSV export → `app/src/lib/waitlist.ts` import with `consent_log` kind `fb_group` | 3× → Group → email capture | M |
| 5 | **Group "Units"** for the 7-day reset: one unit per day, linked to the members app Day 1 | Community manager; content from `products/sessions.json` | 2× → Group 7-day activity | L |
| 6 | **Weekly real-coach Facebook Live** in the Group, recorded and cut into 5 Reels (human, original content) | `assemble` `coach_cut` profile (no avatar); posts as PLACEMENT | 3× → R3 leads per week | M |
| 7 | **Facebook Events** for each live (native RSVP reminders) | Page Events; ICS from 100X §7.10 | 2× → live attendance | M |
| 8 | **Page action button = "Send message"** opens Messenger at the `begin.json` flow | Page settings; `dm/flows/begin.json` entry ref | 2× → profile → DM starts | M |
| 9 | **Messenger ice-breakers** (4 FAQ buttons: knees, back, sleep, "is this real?") | `dm/bot.py` setup call; maps to `knees/back/sleep/_global` | 2× → DM thread starts | M |
| 10 | **Messenger persistent menu**: Day 1 · Waitlist/Join · Talk to a human | `dm/bot.py` profile API setup | 2× → returning DM sessions | M |
| 11 | **FB length bucket 60–90 s** for movement follow-alongs (IG stays 30–59 s) | `variants.py` `length_buckets.fb` | 2× → avg watch seconds | L-M |
| 12 | **SRT caption upload** alongside burned-in captions, for search and auto-translate | `packager.py` writes `.srt` from word timings; Graph `captions` edge | 2× → FB search impressions | L |
| 13 | **Keyword-first video title** (≤60 chars) on every FB Reel | `packager.py` `fb_title` | 2× → search-sourced plays | L |
| 14 | **Weekly "Ask Sun" text post** whose answers seed the nightly comment-mining job | `tools/build_content.py` F37 slot; mining reads FB comments | 3× → first-name answer scripts supplied | M |
| 15 | **Link-in-body vs link-in-first-comment test** for FB text posts | Allocator arm `link_pos`; `growth/allocator.py` | 2× → link CTR on the winning arm | L |
| 16 | **Never use native Page-to-Page crossposting** between siblings | `posting_rules.py` fails on `crosspost_from` | avoids ÷3 Page reach (originality) | M |
| 17 | **Breakfast-slot kitchen lane**: Sun's kitchen posts go first in the 06:30–08:00 FB slot | `posting_rules.py` slot affinity `pillar=kitchen` | 2× → FB kitchen plays | L |
| 18 | **"Photo of the printable" posts** (exercise card on a fridge, made with Nano Banana) | `assemble/graphics.py` `fb_photo` + library still | 2× → saves on photo posts | L |
| 19 | **Multi-photo "album" posts** of the week's 5 exercise cards | Graph `/photos` batch; `graphics.py` | 2× → shares vs single photo | L |
| 20 | **Pinned weekly "Start here" post** with the Group, Day 1 and "we never DM first" | `packager/fallback.py` pinned template | 2× → new-follower → Day 1 clicks | M |
| 21 | **Reply as the Page within 60 min**, with 5+ word replies, on the top 10 comments | Human inbox SLA in ORGANIC §6.3; queue from `dm/bot.py` | 2× → comments per post | L-M |
| 22 | **"Share to your walking group" close variant** for movement posts | `variants.py` close slot `fb_group_share` | 2× → shares per reach | L |
| 23 | **Facebook-native "Sunday soup" series** with a fixed time and episode number | `build_content.py` series slot; FB only | 2× → returning viewers on Sundays | L-M |
| 24 | **Sync FB Page "Featured" to the current winning Reel weekly** | Ops; `growth/actions.py` pin suggestion → FB | 2× → profile visit → play | L |
| 25 | **FB text posts in Sun's voice ≥80 words** (story shape) vs short ones | Allocator arm `fb_text_len` | 2× → dwell-weighted reach | L |
| 26 | **Separate FB Page bios** written for 65+ ("Gentle strength. Real coaches. AI characters.") | ACCOUNT_SETUP; `compliance/scanner.py` bio target | 2× → follow rate from profile | L |
| 27 | **Facebook Reels covers with a face plus 4 words** (not 6), larger type | `variants.cover()` `fb` profile | 2× → plays per profile impression | L |
| 28 | **Weekly Group "wins" thread** whose replies feed the CH "Your wins" episode (with consent) | CM template; consent capture in `app` upload form | 2× → Group posts per member | L-M |
| 29 | **Group rule post and moderation queue** for spam and scams (older-audience protection) | CM SOP; admin assist | avoids ÷2 Group trust | M |
| 30 | **Messenger "One-Time Notification"-style opt-in for "remind me when the next live starts"**, under the Marketing Messages rules | `dm/flows/_global.json` `notify_live` step | 2× → live attendance | L |
| 31 | **FB-only "grandkid" angle** (doing it with grandchildren) on duo posts | Writer prompt arm `fb_family` | 2× → shares | L |
| 32 | **Repurpose the best IG carousel as an FB multi-image post with a different first card** | `graphics.py` reorder; guard textsim | 2× → FB saves | L |
| 33 | **Post-level AI-info audit**: weekly check that every FB post carries the label | `growth/snapshots.py` reads label field when available; ops sample | avoids ÷N (label enforcement) | M |
| 34 | **FB "Page recommendations" status pulled into the reach-drop detector** | `growth/baselines.py` input from manual status log | avoids false LOSER marks | M |
| 35 | **FB Reels from the "coach" human Page tagged with the character Page** (honest, same owner) | Accounts Center disclosure; no reciprocal engagement | 2× → coach-Page reach | L |
| 36 | **Messenger Day-1 "check-in" at 24 h** (inside the window only when user-initiated) | `dm/flows/begin.json` step with window check in `sender.py` | 2× → Day 1 completions | M |
| 37 | **Group-only exclusive drop** (printable) to pull Page followers into the Group | `products/*.pdf` subset; CM | 2× → Page → Group join | L |
| 38 | **Monday "weekly plan" image post** that matches the Messenger broadcast | `graphics.py` `weekly_plan` | 2× → Messenger opt-ins | L |
| 39 | **Mirror IG polls as FB text polls** (FB Page polls) | Ops; poll results → `growth/snapshots` | 2× → comments | L |
| 40 | **Recycle a FB winner after 60 days as a new REMIX render**, never a re-upload | `growth/actions.py` remix rule `same_page_after_days=60` | 2× → reach per evergreen idea | M |
| 41 | **Older-user font check on FB covers on tablets** (10" render preview in QA) | `qa/qa.py` cover check at 1280 px | 2× → cover legibility | L |
| 42 | **FB caption line 1 = a plain question** ("Do your knees hurt on stairs?") | Packager caption templates `fb` | 2× → comment rate | L |
| 43 | **Holiday family Reels** (Thanksgiving, Lunar New Year, Chuseok) on the calendar | `data/calendar.csv` (100X Holes #5) adds cultural dates | 2× → seasonal shares | L-M |
| 44 | **Messenger quick-reply "Send to my daughter"** that forwards the gift page | `dm/flows/family.json` share button | 3× → FAMILY gift clicks | L-M |
| 45 | **FB Reels posted at 06:30 CT** for central-time early risers (with 100X Holes #6) | `posting_rules.py` slot per page offset | 2× → first-hour plays | L |
| 46 | **Weekly FB long cut uploaded as a regular video with chapters**, in addition to the reel | `variants.py` `fb_long` (100X §1.3) + chapter text | 2× → watch minutes | L |
| 47 | **Group "buddy" threads** (match members by start week) | CM template | 2× → week-4 Group retention | L |
| 48 | **Facebook-side keyword list held at ≤6 keywords** (cognitive load for 65+) | `dm/flows` FB variants restrict | 2× → keyword comment accuracy | L |
| 49 | **Group admin-post schedule in Business Suite** (scheduled once a week) | CM SOP | 2× → CM hours efficiency | M |
| 50 | **Page-level "who runs this" About section** naming the company and the real coaches | ACCOUNT_SETUP; legal review | 2× → trust → DM start | L |

## 2. Instagram, including Trial Reels at 10–20/day/page (IG-1 … IG-50)

**The Trial Reels design, in one paragraph.** 10–20 Trial Reels per page per day is reachable: the API allows 100 publishes per 24 h per account [S18], and Trial Reels count toward that. The originality rules decide whether it works. A Trial Reel is a public post shown to non-followers, and nothing exempts it from the "low-value edit" rules [S3][S20]. So every trial gets the **REMIX role**: a new hook slice (a fresh avatar take), a new TTS take, a different B-roll draw and a different length bucket. It has to pass the same-page uniqueness guard against every live trial and feed post from the last 30 days. Each body is used by **at most 3 trials**. 15 trials/day/page therefore needs 5 bodies/day/page, drawn from the page's 6 daily masters plus the body bank (MOD-6). The real daily cap on Trial Reels is unpublished and anecdotally can be as low as 5 [N1]. So the count **ramps by probe**: start at 3 per day, add 2 every 3 clean days, stop at 20, and halt on the first error or reach collapse (RO-1).

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **Trial Reels 10–20/day/page as distinct REMIX renders**, ramped by probe (3 → +2 every 3 clean days → 20 max) | New `workers/growth/trials.py` (`trial_quota(page, history)`); `posting_rules.py` replaces the 14-day `ig_trial_reel` rule with `variant_role=TRIAL` | 5× → hook tests read per page per week | M |
| 2 | **The feed post is the graduated winner** (`graduation_strategy=MANUAL`, promoted by our score). No separate feed copy of the same body | `trials.py` `graduate()`; publisher uses the trial media id | 3× → follower-feed reach per post | M |
| 3 | **Max 3 trials per body; ≥3 dimensions changed per trial** (hook, B-roll order, voice take, length) | `uniqueness/guard.py` rule 6 `trial_body_cap=3`; `variants.py` `remix_profile` logs the dimensions | avoids ÷5 account-wide originality demotion | M |
| 4 | **Trial slot timing spread across 07:00–20:00** (non-followers, any time zone) | `posting_rules.py` `trial_slots` grid at 45-min spacing | 2× → trial reach | L |
| 5 | **Trial hook arms drawn from the 430-hook bank by grammar family** (IF_EVERY, MYTH, WATCH…) | `growth/allocator.py` `hook_family` arm → `data/content/hooks.json` | 2× → share of trials beating the median | M |
| 6 | **IG Reels A/B test of covers and captions** (up to 4) on every feed post (N4) | `variants.cover()` × 4; manual in-app until API | 2–3× → plays per grid/profile impression | M |
| 7 | **Ask viewers to use the Repost button** on movement posts ("Repost so your friends do it too") (N7) | `variants.py` close slot `ig_repost` (test arm) | 2× → follower-of-follower reach | L-M |
| 8 | **Carousel slide 1 = the same hook as the day's winning trial** | `graphics.py` F36 reads the winning `hook_text` | 2× → carousel saves | M |
| 9 | **Carousel "save this" final card plus printable QR** | `graphics.py` last card | 2× → saves per reach | M |
| 10 | **Alt text written from the script's plain-language problem** | `packager.py` `alt_text` (extends 100X §2.4 with a template) | 2× → IG search impressions | L |
| 11 | **Highlights per series** (Chair Challenge, Soup Sundays, Ask Sun) refreshed weekly | Ops; covers from `graphics.py` | 2× → profile → follow | L |
| 12 | **Story sequence: poll → answer video tomorrow → link sticker** | `build_content.py` Story slot; poll result → script variable | 2× → Story replies | L-M |
| 13 | **Close Friends list = members only** ("members' corner" Stories) | Ops: add members by handle (opt-in form in `app`) | 2× → member retention signal | L |
| 14 | **"Reply with Reel" to the top question daily** (IG comment reply feature) | `build_content.py` F26 → publisher reply mode | 2× → comment threads | L-M |
| 15 | **Pinned comment with an open question plus the keyword** on every Reel (with 100X §4.8) | `packager.py` `first_comment` template | 2× → comments per view | L-M |
| 16 | **3 pinned grid posts**: "Who we are (AI + real coaches)", "Start Day 1", best evergreen | Ops; `packager/fallback.py` pins | 2× → profile → follow | M |
| 17 | **Collab-free "Remix" permission on movement Reels** (viewers do it next to Chang) | Publisher sets remix on for movement lane | 2× → UGC remixes | L |
| 18 | **Notes ("IG Notes") daily one-liner from Sun** | Ops (manual); text from `build_content.py` | 2× → DM opens | L |
| 19 | **Broadcast channel prompts that ask for emoji reactions and polls** (when eligible) | ORGANIC §3.6 template | 2× → channel engagement | L |
| 20 | **IG "Edit" a trial's caption before graduating it** (keyword line 1) | `trials.py` graduate step | 2× → search pick-up | L |
| 21 | **Separate IG and Trial captions** (trials get a non-follower framing: "New here? …") | `packager.py` `ig_trial_caption` | 2× → follows from trials | L-M |
| 22 | **A follow cue in trials only** ("follow for Day 2") | Close slot; never in feed copy | 2× → follows per trial view | L-M |
| 23 | **Trial captions carry no hashtags beyond 2 topic tags** (non-follower classification only) | `posting_rules.py` `ig_trial` hashtag cap 2 | 2× → topic-matched trial reach | L |
| 24 | **Track the graduation lag** (auto-share inside 72 h, N2) as a reward feature | `growth/snapshots.py` `graduated_at` | 2× → bandit update speed | M |
| 25 | **Account-level "repost" count stays at 0** (no viewer content reposted by us) | `posting_rules.py` asserts origin=master | avoids ÷10 rec eligibility [S20] | M |
| 26 | **Story link sticker → `/go?p=<page>-story`** with its own attribution code | `app/src/lib/bioLinks.ts` add `story` source | 2× → measured Story CTR | H |
| 27 | **IG profile link list ordered by the live CTA** (waitlist → books → join) | `/go` already switches; add `?p` experiment arm | 2× → bio-link CTR | L |
| 28 | **Monthly IG Live replaced by a live with a real coach** (no AI live) | CH policy; Live with the coach account | 2× → live → R3 leads | L-M |
| 29 | **IG Guides/"Collections" equivalents: saved-post series covers** | `graphics.py` series cover set | 2× → series completion | L |
| 30 | **Cover text contrast/size check on the 3:4 grid crop** | `assemble/variants.cover()` + `qa` grid-crop OCR | 2× → grid CTR | M |
| 31 | **Trial-to-feed delay ≥24 h** so the follower audience sees a different day's run | `trials.py` | 2× → follower reach | L |
| 32 | **Use the "AI info" label on every trial too** | `packager.py` forces AI flag for TRIAL role | avoids ÷N label penalty [S9] | H |
| 33 | **One "behind the scenes: how we make Chang" Reel per month** | `build_content.py` honesty slot | 2× → trust comments | L-M |
| 34 | **Pinned Story highlight "Is Chang real?"** | Ops | 2× → fewer hostile comments | L |
| 35 | **Keyword auto-reply in public comments ("Sent! Check your DMs")** to signal activity | `dm/bot.py` public reply (1 per comment) | 2× → keyword comments | L-M |
| 36 | **Stagger the 4 pages' trials so no two pages trial the same hook family in the same hour** | `trials.py` network scheduler | avoids self-competition | M |
| 37 | **Trial results posted to `/admin/today`** (wins, graduations, blocks) | `app` `/admin/today` reads `/growth/summary` trials block | 2× → operator decision speed | H |
| 38 | **IG "Add Yours" Story sticker for "my chair-stand count"** | Ops Story template | 2× → Story reach | L |
| 39 | **Separate trial budget per character** (Chang strength vs Sun kitchen) | `trials.py` quota by pillar | 2× → kitchen-lane winners | L |
| 40 | **Grid rhythm: every 3rd feed post is a carousel** | `posting_rules.py` grid rule | 2× → profile visit → follow | L |
| 41 | **Profile photo A/B across time (one change per 30 days only)** | Ops log | 2× → follow rate | L |
| 42 | **Reels audio named "Chang Yin – original audio"** so it can be reused by others | Publisher `audio_name` | 2× → audio page traffic | L |
| 43 | **IG search keyword map per page** (top 50 phrases from comment mining) | `data/content/keywords_<page>.json` from mining job | 2× → search plays | L-M |
| 44 | **Caption line 2 = the safety line** (keeps line 1 free for the keyword) | Packager template | protects reach and compliance | M |
| 45 | **DM "Send me the link" button text A/B** | `dm/flows/*.json` variants | 2× → button tap rate | M |
| 46 | **Weekly "most saved" carousel reposted to Stories with a new frame** (original frame, not reshare) | `graphics.py` | 2× → saves | L |
| 47 | **Flagship → sibling handoff once a week** ("Sun's page has the recipe") | Script slot; ≤1/week (100X §2.7) | 2× → sibling follows | L |
| 48 | **Trial winners' hooks back-propagate to TikTok and YouTube variants the same day** | `growth/actions.py` → `variant_build` (100X §5.7) | 2× → YT/TT hook quality | M |
| 49 | **Never trial an offer post** (CTA BOOK/JOIN) | `trials.py` rejects `cta_type∈{book,join}` | avoids ÷N commerce demotion | H |
| 50 | **Monthly IG "originality score" self-audit**: % of posts with fresh renders, reused bodies, guard overrides | `uniqueness/guard.py` report → `/admin/today` | avoids ÷5 enforcement | M |

## 3. TikTok, YouTube, Threads, X (TT-1 … TT-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **YouTube Shorts → related long-form link** on every Short (N9) | `packager.py` `yt_related_video_id` from weekly `yt_long` | 3× → long-form views from Shorts | M |
| 2 | **YouTube chapters + "Strong at 70" playlist** per series | `variants.py` `yt_long` writes chapter text | 2× → session watch time | M |
| 3 | **YouTube Shorts titles keyword-first** (≤40 chars), separate from the hook text | `packager.py` `yt_title` | 2× → search views | L-M |
| 4 | **YouTube "Test & compare" for long-form thumbnails** (3 thumbs) | `graphics.py` 3 thumbs for `yt_long` | 2× → long-form CTR | M |
| 5 | **YouTube community posts (polls)** twice a week | Ops; poll result → script variable | 2× → returning viewers | L |
| 6 | **YouTube "Members"-free premiere of the weekly long session at 10:00 ET Saturday** | Ops schedule | 2× → first-day views | L |
| 7 | **YouTube pinned comment with the Day 1 link** (links allowed in long-form) | `packager.py` YT long only | 2× → YT → waitlist | M |
| 8 | **TikTok "Search" keyword strategy**: spoken keyword + on-screen keyword in the first 3 s | Writer prompt; `virality.py` checks spoken keyword | 2× → TikTok search views | L-M |
| 9 | **TikTok Series/playlists** for the 7-day reset | Ops | 2× → series completion | L |
| 10 | **TikTok Stitch/Duet allowed on movement posts** | Publisher privacy flags | 2× → UGC | L |
| 11 | **YouTube auto-dubbing to Spanish** (N6) on long-form and Shorts, labelled | Channel setting; ops | 5× → non-English YT views per dollar | M |
| 12 | **TikTok draft-to-inbox upload** where direct post isn't approved, with the human post pack | `packager/fallback.py` TikTok pack (exists) + caption | protects cadence | M |
| 13 | **TikTok `is_aigc` flag on every upload** (verify the field is set by the API path) | `packager.py` test | avoids ÷N AIGC penalty | H |
| 14 | **TikTok platform weight learned from FYP share** (with 100X §3.3, §10.9) | `growth/allocator.py` platform arm | 2× → render dollars spent where reach is | M |
| 15 | **TikTok close = "Day 1 is free on my profile"** variant test against "comment DAY1" | `variants.py` close slot `tt` | 2× → profile clicks | L-M |
| 16 | **TikTok Q&A-style replies** (reply-to-comment video) every day | F26 lane on TikTok | 2× → comments | L-M |
| 17 | **Threads: post into Threads Communities** (fitness over 60, healthy cooking) (N8) | Publisher topic/community field; ops | 3× → Threads reach | L-M |
| 18 | **Threads: one real-coach account replies under character posts** (disclosed, same owner) | Coach account; inbox SLA | 2× → reply depth | L |
| 19 | **Threads: question posts at 07:00 and 19:00 ET** | `posting_rules.py` Threads slots | 2× → replies | L |
| 20 | **Threads: carousel of exercise cards** (images, 4.55% engagement band [S6]) | `graphics.py` Threads export | 2× → vs text-only | M |
| 21 | **X: post the 15 s cut with a question, no link in the post** (link in the profile) | `variants.py` `x` trim profile | 2× → replies | L |
| 22 | **X: bookmark trigger ("bookmark for tonight")** | Close slot `x` | 2× → bookmarks | L |
| 23 | **X: drop X if 30-day reach per post <10% of the best platform** | `growth/allocator.py` kill switch (with 100X §10.9) | saves render/ops time | M |
| 24 | **YouTube: no hook-swap of the same body on the same channel** (100X §3.4) **plus** a 14-day minimum gap on bodies shared with IG | `uniqueness/guard.py` cross-platform rule | avoids ÷N YPP / inauthentic flag | M |
| 25 | **YouTube "Shorts remix ON" only for movement** (100X §3.10 sets default; this adds tracking of remix count) | `adapters.py` remix count field when exposed | measure | L |
| 26 | **YouTube "Hype"/comments pinned by the channel weekly** | Ops | 2× → comments | L |
| 27 | **YouTube end screen to the Day 1 long session** | `yt_long` template | 2× → session starts | M |
| 28 | **TikTok LIVE only with a real coach (account ≥ eligibility)** | Policy | 2× → live followers | L |
| 29 | **TikTok captions with 3 keyword hashtags max** (search classification) | `posting_rules.py` TT cap 3 (from 5) | 2× → search pick-up | L |
| 30 | **TikTok video length 45–60 s for talk lane, 20–30 s for kitchen** | `variants.py` `tt` buckets | 2× → completion rate | L |
| 31 | **YouTube Shorts loop-free ending check** (R4 already) **plus** a "save for tonight" card | `overlay.py` card | 2× → saves | L |
| 32 | **YouTube channel "Course" for the 7-day reset** (YouTube Courses) | Ops | 2× → session retention | L |
| 33 | **Separate YT channel trailer for non-subscribers** | Ops; 60 s cut | 2× → subscribe rate | L |
| 34 | **TikTok photo mode carousels** of recipes (Sun) | `graphics.py` TT photo export | 2× → saves | L |
| 35 | **Threads: cross-post from IG off; native Threads text** | Publisher | 2× → Threads reach | L |
| 36 | **X: one weekly thread from Sun's "kitchen science" study cards** | `build_content.py` F28 → thread | 2× → bookmarks | L |
| 37 | **YouTube Shorts: first comment by the channel = a question** | `packager.py` `yt_first_comment` | 2× → comments | L |
| 38 | **Platform-specific opening frame for YouTube** (canon 4 "distinct cut"): open on the movement, hook text in the bottom third | `variants.py` `yt` profile | 2× → "viewed vs swiped" | L-M |
| 39 | **TikTok first 1 s motion** (no static open) checked by the gate | `virality_gate.py` R1c motion energy | 2× → 2 s hold | L-M |
| 40 | **TikTok post time learned per page** (local slot arm) | Allocator slot arm `tt` | 2× → first-hour views | L |
| 41 | **YouTube "pause and try" cards** at the exercise beat (long-form) | `yt_long` overlay | 2× → watch time | L |
| 42 | **YouTube metadata language set per video** (enables auto-dub and search) | `packager.py` `defaultAudioLanguage` | 2× → dub eligibility | M |
| 43 | **Threads: a weekly "ask a coach" thread** that a real coach answers | Coach account | 2× → replies | L |
| 44 | **X: Community Notes risk check** (no stat without a study card) | `compliance/scanner.py` X target requires evidence id | avoids ÷N reach | M |
| 45 | **TikTok: never repost the same file to two pages** (already) **plus** an audio-fingerprint check across pages | `uniqueness/audiofp.py` scope `tt` | avoids ÷N unoriginal flag | M |
| 46 | **YouTube "Add to Watch Later" verbal cue in long-form** | Script slot | 2× → return sessions | L |
| 47 | **TikTok "Add link" only to free Day 1** (profile tile order, 100X §8.10) **plus** the `/tt` A/B | `bioLinks.ts` experiment | 2× → TT → email | L |
| 48 | **YouTube Shorts length bucket 35–50 s** separate from IG | `variants.py` `yt` bucket | 2× → completion | L |
| 49 | **Threads link posts only once a week** (the rest are text and video) | `posting_rules.py` | 2× → Threads reach | L |
| 50 | **A per-platform "stop list"** of formats that underperform 3 weeks running | `growth/actions.py` down-weight by format × platform | 2× → reach per render | M |

## 4. Hooks and scripts (HK-1 … HK-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **The asker's wording becomes the hook** (top question cluster, quoted verbatim, first name on screen) | Nightly mining → `prompts/01_idea_miner.md` → `02_script_writer.md` field `hook_verbatim` | 3× → share+save on answer posts | M |
| 2 | **Hook bank refresh**: 50 new hooks/week generated from winning grammars × new objects | `tools/build_content.py` hooks validator; `data/content/hooks.json` | 2× → share of trials above median | M |
| 3 | **Ban weak grammars from trials** (QUESTION, HOW-TO at rel 0.6–0.7 [M]) unless exploring | `allocator.py` family prior floor | 2× → hook hold rate | M |
| 4 | **"Number + body part + time" template** ("30 seconds, your knees, no hands") | Writer prompt slot | 2× → 3 s hold | L-M |
| 5 | **Proof shot in frame 1 for movement** (the person already mid-rep) | Shot planner `prompts/04` rule | 2× → 3 s hold | M |
| 6 | **Grammar × first-frame object matrix as a tested arm** | `allocator.py` arm `hook_obj` | 2–3× → 3 s hold | M |
| 7 | **Re-hook at 40–50%** ("but the second one is the one that matters") | `virality.py` re-hook row | 2× → completion | L-M |
| 8 | **Script length matched to platform buckets** at write time (one script, 3 cut points marked) | `02_script_writer.md` `cut_points` | 2× → completion per platform | M |
| 9 | **Two-voice cold open** (Sun interrupts Chang in line 1) | Duo lane template | 2× → 3 s hold on duo | L-M |
| 10 | **Concrete daily-life stakes** (grandkid's car seat, the bus step) in line 2 | Writer rule; `virality.py` Emotion row | 2× → shares | L |
| 11 | **Contrarian-but-safe myths** from comment mining, scanned for claims | Mining → MYTH grammar; scanner | 2× → comments | M |
| 12 | **Every 4th script is a reply video** to a real comment shown on screen | `build_content.py` F26 quota | 2–3× → comments per view | M |
| 13 | **"Try it now" instruction inside 5 s** (viewer participates) | Writer rule | 2× → saves | L-M |
| 14 | **Open loop counter** ("3 things, the last one surprises doctors") — scanned for claims | Writer; scanner blocks "doctors hate" | 2× → completion | L |
| 15 | **Kitchen hooks lead with the result on the plate**, not the recipe name | Kitchen lane template | 2× → 3 s hold | L-M |
| 16 | **Hook text ≠ spoken hook** (complementary, not duplicated) | `virality_gate.py` R1d textsim(spoken, onscreen) ≤0.6 | 2× → hook comprehension | L |
| 17 | **Banned-opening list** ("Hi everyone", "Today I…", "So…") | `virality.py` hard fail | 2× → 1 s hold | M |
| 18 | **Line-level readability: grade ≤6** | `virality.py` Flesch-Kincaid check | 2× → completion (65+) | L-M |
| 19 | **Pause before the reveal (400 ms)** using SSML (extends 100X §4.2 to reveals) | `assemble/voice.py` `reveal_pause` | 2× → retention at the reveal | L |
| 20 | **One idea per script** (validator rejects 2+ exercises unless the format is a routine) | `build_content.py` validate_v2 | 2× → saves | L |
| 21 | **Callback hooks** ("Remember Tuesday's chair test?") for series viewers | Writer reads series state | 2× → returning-viewer share | L-M |
| 22 | **Seasonal hooks pre-written 3 weeks ahead** from `data/calendar.csv` | `build_content.py` | 2× → seasonal share | L |
| 23 | **Hook A/B on the caption line only** for FB/IG A/B tests (N4) | `packager.py` 4 captions | 2× → plays per impression | M |
| 24 | **Ending line = the next episode tease** (not a sign-off; R4-safe) | Writer rule | 2× → follow rate | L-M |
| 25 | **Sun's verdict as a 1-word on-screen stamp** ("NO." / "YES.") | `overlay.py` stamp asset | 2× → shares on duo | L |
| 26 | **Writer gets the last 14 days of per-beat retention dips** (LL-3) | `prompts/02` context block | 2× → avg watch % | M |
| 27 | **Ban numbers we can't cite** (every number maps to EVIDENCE.md or a demo) | `scanner.py` C-rules (extend to on-screen) | avoids ÷N health-claim demotion | H |
| 28 | **"You" in line 1** (second person) | `virality.py` row | 2× → 3 s hold | L |
| 29 | **Script variants by age band** (60s vs 70s+ framing) as an arm | `allocator.py` `age_frame` arm | 2× → shares in band | L |
| 30 | **Hooks tested first on trials, written into masters second** (write order flips) | `build_content.py` pipeline order | 2× → master hook quality | M |
| 31 | **Recipe scripts carry a "swap" line** (low-sodium, soft food) | Kitchen template | 2× → saves | L |
| 32 | **Exercise scripts carry an easier and a harder version** in 1 line each | Movement template (matches the app's levelling) | 2× → saves | L-M |
| 33 | **Weekly "worst hook" post-mortem**: the 5 lowest trials and why | `/admin/today` panel | 2× → writer learning speed | L |
| 34 | **Hook length ≤9 spoken words** for trials | `virality.py` trial threshold | 2× → 1 s hold | L |
| 35 | **First-name greeting in reply videos** (canon) **plus** the commenter's city (opt-in) | Writer; consent from comment author? public only | 2× → shares | L |
| 36 | **Duet-style "Sun reacts to Chang's old post"** (self-reaction, own content) | Duo lane | 2× → returning viewers | L |
| 37 | **Story hooks with a time stamp** ("Last Tuesday at 6 am…") | STORY grammar template | 2× → completion | L |
| 38 | **Myth hooks require a prop** (rel 3.0 with prop [M]) | Shot planner rule | 2× → 3 s hold | M |
| 39 | **"Watch my hands" cue** for kitchen and grip content | Writer | 2× → retention | L |
| 40 | **Never open with a disclaimer**; disclaimer in caption and end card | `virality_gate.py` checks first 2 s | 2× → 1 s hold | M |
| 41 | **Script-level "share target" named** ("send this to the friend who…") per pillar | `virality.py` share row (specific nouns) | 2× → sends | L-M |
| 42 | **A/B the hook voice: Chang vs Sun** on the same topic | `allocator.py` speaker arm (exists) used on trials | 2× → hook hold | L |
| 43 | **Callback to a viewer's win** ("Margaret did 12 today") with consent | CH-2 pipeline | 2× → comments | L |
| 44 | **Avoid medical vocabulary in hooks** (plain words: "sore knees" not "osteoarthritis") | `scanner.py` hook-only lexicon | 2× → reach (health demotion) | M |
| 45 | **Hook visual = the problem moment** (struggling to stand) before the fix | Shot planner | 2× → 3 s hold | L-M |
| 46 | **Writer quotas by grammar** match the allocator posterior each night | `build_content.py` reads `plan_day` `hook_families` | 2× → winning-grammar supply | M |
| 47 | **Keyword in the hook for search** ("Knee pain on stairs?") on 1 in 3 | Writer arm | 2× → search plays | L |
| 48 | **Reading-time check for on-screen text** (≥1.5 s per 5 words, 100X Holes #3) applied to mid-video text | `virality_gate.py` all text | 2× → comprehension | M |
| 49 | **Ad-script hooks reuse organic winners only** (boosts) | `growth/actions.py` boost candidates | 2× → ad CTR | M |
| 50 | **Rewrite the 3 REWRITE scripts (S37, S47, S49) or retire them** | `data/content/scripts_*.py` | cleans backlog | H |

## 5. Modular production (MOD-1 … MOD-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **Hook-slice bank**: render 4–6 on-camera hook slices per master in one batch (new TTS per slice), assemble trials from the clean mezzanine | `assemble/voice.py` `slices=[]`; `assembler.py` `hook_slices`; `variants.py` | 5× → trial variants per avatar-dollar | M |
| 2 | **Trial cost envelope**: ~$0.45 per trial (6 s Std avatar at $0.0562/s × 1.15 + TTS + assembly). 15/day × 4 pages ≈ $27/day | `tools/build_costs.py` `trial` line; n8n month guardrail | keeps 10–20/day inside budget | M |
| 3 | **B-roll draw without replacement per page** (30-day ledger) | `production/broll`; `uniqueness/guard.py` `broll_ledger` | avoids ÷N visual-duplicate flag | M |
| 4 | **Length buckets as cut points, not re-renders** | `variants.py` reads `cut_points` (HK-8) | 2× → variants per render | M |
| 5 | **Voice retake pool**: 3 takes per line at write time ($0.01 each) | `voice.py` | 2× → distinct audio fingerprints | M |
| 6 | **Body bank with per-page 30-day reuse ledger** | New table `body_ledger` in `schema_growth.sql`; `guard.py` reads it | 3× → distinct renders per dollar | M |
| 7 | **Set and wardrobe rotation table** (8 sets × wardrobes) drawn per variant | `CHARACTERS.md` §6 → `production/refs/manifest.json` | 2× → visual distinctness | M |
| 8 | **Render on demand for trials** (only trials scheduled for tomorrow get built) | n8n `variant_build` (100X §5.7) | saves ~20% trial render | M |
| 9 | **Slice-level QA** (ArcFace + lip-sync per slice) before assembly | `qa/face.py` per slice | 2× → fewer full re-renders | M |
| 10 | **Cached exercise renders reuse ≤2× and never on the same page** (STACK_FINAL B) enforced in code | `guard.py` rule on `render_id` | avoids ÷N flag | H |
| 11 | **Cover generation from the hook slice frame**, not the body | `variants.cover()` frame source | 2× → cover relevance | L |
| 12 | **Platform-clean mezzanine reused for all placements** (exists) **plus** a hash test that no platform file feeds another | `packager.py` test | avoids ÷N | H |
| 13 | **Assembly concurrency = 4 per box** with a queue depth alert | `deploy/docker-compose.yml` worker replicas | 2× → throughput | M |
| 14 | **Render-time budget per lane** with an alert at 2× the median | `assembler.py` timing → Slack | avoids queue stalls | M |
| 15 | **Trial assembly uses ffmpeg concat without re-encode where cuts align** | `assembler.py` stream-copy path | 3× → trial assembly speed | M |
| 16 | **Batch stills via Nano Banana Batch** (STACK_FINAL W6) for set rotation | `production/refs/render_refs.py` batch | 2× → still cost | H |
| 17 | **Shot-list templates per format** (39 formats) as JSON | `production/shot_list/build_shot_list.py` | 2× → planner consistency | M |
| 18 | **Duo shot/reverse-shot template** codified | `prompts/04_shot_planner.md` duo block | 2× → duo render success | M |
| 19 | **Auto-reject inserts with faces or text** via OCR and face detection | `qa/ocr.py`, `qa/face.py` on inserts | avoids ÷N weird inserts | M |
| 20 | **Pre-generate next week's B-roll on Sunday via Batch** | `production/broll/build_broll.py` cron | 2× → B-roll cost | M |
| 21 | **Variant metadata contract** (`variant_role`, `dims_changed`, `body_id`, `hook_id`) | `schema_growth.sql` `post.variant_meta` | enables LL items | H |
| 22 | **Caption timing re-derived per cut** (no drift after trims) | `captions.py` per variant | 2× → caption accuracy | M |
| 23 | **Music bed off by default** (100X Holes #1) **plus** a test arm "bed at −28 dB" | `assembler.py` mix arm | 2× → older-ear comprehension | L-M |
| 24 | **Loudness per platform** (−14 LUFS for all; FB older devices: compression check) | `qa/probes.py` | protects | M |
| 25 | **Per-variant C2PA re-sign test** (100X §5.9) **plus** a manifest diff in QA | `qa` C2PA check | avoids ÷N | H |
| 26 | **Template versioning**: every layout change bumps a version recorded on the post | `layout.py` `LAYOUT_VERSION` | enables attribution | M |
| 27 | **Weekly "golden set" render regression** (5 scripts) to catch quality drift | `workers/tests` + `make sample` | avoids ÷N quality | M |
| 28 | **Avatar vendor adapter per character** (canon 4) **plus** an automatic fallback to Hedra on fal errors | `assemble` adapter; STACK_FINAL §4 | protects cadence | M |
| 29 | **Billed-seconds ledger** (STACK_FINAL B7) per render | `assembler.py` → `costs` table | 2× → cost visibility | H |
| 30 | **Exception-lane budget enforcement in n8n** (walk-and-talk) | n8n node (STACK_FINAL §3) | protects budget | H |
| 31 | **Hook slices at 5 s multiples** for LipSync billing (W9) | `voice.py` slice padding | saves up to 20% | M |
| 32 | **Same-day re-render of a failed slice only** | `assembler.py` slice retry | 2× → retry cost | M |
| 33 | **Mezzanine archive 90 days in R2**, then delete | `deploy` lifecycle rule | saves storage | M |
| 34 | **Carousel generation straight from the script beats** | `graphics.py` | 2× → carousel supply | M |
| 35 | **Auto-crop 16:9 long-form from the 9:16 masters only for movement** | `variants.py` `yt_long` | 2× → long-form supply | L-M |
| 36 | **Spanish track via Meta/YT dubbing (FB-3, TT-11) before any Spanish render** | Ops gate | 5× → Spanish output per dollar | M |
| 37 | **Script-to-render SLA dashboard** (time from approval to READY) | `/admin/today` | 2× → on-time posts | M |
| 38 | **Human review shows only the diff for trials** (100X §10.6 extended to trials) | Review UI `variant diff` | 3× → reviewer throughput | M |
| 39 | **Trial reels skip the full-length QA run; slice QA + spec probe only** | `qa/qa.py` `role=TRIAL` profile | 2× → QA throughput | M |
| 40 | **Pre-flight uniqueness check before render**, not after (text + body ledger) | n8n order: guard text → render | saves wasted renders | M |
| 41 | **Prop library** (photographed props) for myth hooks | `production/refs` props set | 2× → myth hook supply | L |
| 42 | **Fixed lighting LUT per set** to keep identity consistent | `assembler.py` LUT per set | 2× → identity consistency | L |
| 43 | **"No hands visible" flag** on avatar slices that fail finger checks, auto-crop to MCU | `qa/face.py` + `layout.py` | avoids reject | L |
| 44 | **Text-overlay templates locked to the never-gray palette** | `layout.py` palette constants test | protects brand | H |
| 45 | **Variant cap per master = 1 feed + ≤3 trials + 5 platform placements** | `posting_rules.py` | avoids ÷N duplicate flags | M |
| 46 | **Library still refresh 10%/month** (new angles) | `render_refs.py` | 2× → visual freshness | L |
| 47 | **TTS pronunciation dictionary** (`production/voices/pronunciation.pls`) checked by ASR | `voice.py` ASR check (STACK_FINAL W4) | 2× → fewer mispronunciations | M |
| 48 | **Automatic aspect-safe reframe for 4:5 IG feed carousels** | `graphics.py` | 2× → grid quality | L |
| 49 | **Render queue priority**: offers and launch posts first, trials last | n8n queue priority | protects launch | H |
| 50 | **One-command day build**: `make day DATE=…` renders, packs and writes the review queue | `workers/Makefile` | 2× → ops speed | M |

## 6. Learning loop (LL-1 … LL-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **Trial-only hook lab**: hook arms update from Trial Reels only (pure non-follower) | `growth/scoring.py` `source=trial`; `allocator.py` hook arm | 3× → hook-effect precision | M |
| 2 | **Body arm separate from hook arm** (factorial, 100X §6.3) using trials sharing a body | `allocator.py` `body_id` arm | 2× → body-effect precision | M |
| 3 | **Retention dip finder**: the largest negative slope second → beat id → writer context | New `growth/dips.py`; YT `audienceWatchRatio` [S28]; FB retention graph [S16] | 2–3× → avg watch % on rewrites | M |
| 4 | **Comment cluster → topic demand score** used by the allocator's pillar arm | Mining job → `allocator.py` pillar prior | 2× → pillar hit rate | M |
| 5 | **Owned-contact reward** (email/Messenger opt-ins per 1K views) as a 4th reward term | `scoring.py` reward weights (config) | 2× → owned contacts per view | M |
| 6 | **Revenue attribution by `pid`** feeding the reward at 7 days | `growth/snapshots.py` rollups from `sy_orders` | 2× → MRR per post | M |
| 7 | **Per-page priors from the network** (empirical Bayes exists) **plus** per-character priors | `baselines.py` hierarchy level | 2× → cold-start accuracy | M |
| 8 | **Weekly model card**: what the bandit believes, top arms, exploration share | `/admin/today` | 2× → operator trust | M |
| 9 | **Holdout days** (one page × one day/week runs uniform random arms) | `allocator.py` `holdout` flag | measures true lift | M |
| 10 | **Trial graduation as a label** (Instagram's own judgment, N2) | `snapshots.py` | 2× → label volume | M |
| 11 | **A/B caption winner (N4) recorded as a label** | Manual import CSV → `/growth/metrics/normalize` | 2× → caption learning | L-M |
| 12 | **Survival-style horizon model** per platform (replaces fixed w priors after 2 weeks) | `baselines.py` | 2× → early-decision accuracy | M |
| 13 | **Daily "what changed" diff**: arms whose posterior moved >10% | Slack digest from `n8n_growth_workflow.json` | 2× → reaction speed | M |
| 14 | **Uniqueness-guard overrides tracked** against outcomes | `guard.py` log → `scoring.py` | avoids repeat penalties | M |
| 15 | **Account-state covariate per page per day** (100X §6.8) **plus** a manual "status screenshot" upload | `common/exceptions.py` | avoids false negatives | M |
| 16 | **Slot-time arm** per page × platform (learned) | `allocator.py` `slot` arm | 2× → first-hour reach | L-M |
| 17 | **Cover-text arm** | `allocator.py` | 2× → plays per impression | L |
| 18 | **Close-type arm** (share vs save vs keyword vs follow) | `allocator.py` `close_family` (100X §6.4) | 2× → targeted action rate | M |
| 19 | **Length-bucket arm per platform** | `allocator.py` `length` (exists) per platform | 2× → completion | M |
| 20 | **Pre-registration of tests in `data/tests.csv`** (hypothesis, metric, stop rule) | New CSV + validator | 2× → fewer false wins | M |
| 21 | **Sequential stopping (always-valid p or Bayes factor)** for pairwise tests | `growth/scoring.py` | 2× → test speed | M |
| 22 | **Competitor-free external signal**: Google Trends terms per pillar weekly (manual CSV) | `/growth/metrics/normalize` | 2× → topic timing | L |
| 23 | **Comment sentiment as a guardrail metric** (hostile share) | Mining job classifier (local) | avoids ÷N negative feedback | L-M |
| 24 | **"Not interested"/hide signals** where exposed (FB `post_negative_feedback`) | `adapters.py` FB_METRICS | avoids ÷N | M |
| 25 | **Learning-rate review**: half-life 14 d tested against 7 d and 28 d offline | `tests` replay harness | 2× → regret | L-M |
| 26 | **Offline replay simulator** from POSTDB + our logs | New `growth/replay.py` | 2× → safer config changes | M |
| 27 | **Network-level winner propagation** (a hook that wins on one page gets tested on the others within 48 h) | `growth/actions.py` | 2× → winner reuse | M |
| 28 | **Separate "fatigue" decay per hook** (performance drop on repeat use) | `allocator.py` fatigue term | 2× → hook longevity | L-M |
| 29 | **Funnel metrics per keyword** (comment → DM → tap → email → paid) | `growth_post_kpis` view by keyword | 2× → keyword pruning | H |
| 30 | **Daily cohort retention of members by acquisition post** | App SQL view `member_cohort_by_pid` | 2× → LTV-weighted reward | M |
| 31 | **Learn per-platform `w(h)` from data (100X §6.6) and publish the curve** | `/admin/today` | measure | M |
| 32 | **Anomaly detector on metric definitions** (sudden ratio jumps → drift alert) | `baselines.py` | avoids ÷N wrong learning | M |
| 33 | **Weekly human "taste" labels on 20 posts** (1–5) to train the predictor | Review UI | 2× → predictor quality | L |
| 34 | **Predictor (100X §6.9) adds visual features** (shot scale, face size, motion) | `growth/predict.py` | 2× → ranking quality | L |
| 35 | **Ship the posterior to the writer prompt** (top 5 arms, bottom 5) | `prompts/02` context | 2× → aligned scripts | M |
| 36 | **Weekly "kill list"** of arms with <5% posterior of being best | `allocator.py` prune | 2× → exploit share | M |
| 37 | **Exploration floor split** (20% total: 10% new hooks, 5% new formats, 5% new slots) | `config.py` | 2× → discovery rate | M |
| 38 | **Learning from DM text** (what people ask after the keyword) | `dm/bot.py` log → mining | 2× → script relevance | M |
| 39 | **Search-term capture from IG/TT insights (manual)** | CSV import | 2× → keyword map | L |
| 40 | **Trial vs feed lift ratio** per page as a health metric | `snapshots.py` | measure | M |
| 41 | **Learn the best trial count per page** (diminishing returns curve) | `trials.py` quota uses marginal winner yield | 2× → trials per winner | M |
| 42 | **Version tags on prompts** (`prompts/*.md` hash on each script) | `build_content.py` | enables attribution | H |
| 43 | **Writer A/B: prompt v_n vs v_n+1 on 10% of scripts** | `build_content.py` split | 2× → script quality | M |
| 44 | **Remix success rate** tracked (remix vs original score) | `growth/actions.py` → scoring | 2× → remix policy | M |
| 45 | **Exposure-adjusted share rate** (shares per non-follower view) | `scoring.py` | 2× → virality signal quality | M |
| 46 | **"First 100 views" quality gate**: if the 3 s hold <40% at 100 views, stop building platform variants | `variant_build` gate | saves renders | L-M |
| 47 | **Monthly re-fit of the rubric weights** from our data (VIRALITY §4 promise) | `tools/virality.py` weights file | 2× → gate accuracy | M |
| 48 | **Experiment log in the repo** (`data/experiments.jsonl`) | Append-only | 2× → institutional memory | H |
| 49 | **Kill-switch on learning when data is <30 posts/page** (priors only) | `config.py` | avoids noise chasing | M |
| 50 | **Quarterly external audit of the loop** (fresh eyes on metric drift) | Ops | avoids ÷N | M |

## 7. Audience ownership (AO-1 … AO-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **One-tap "Get Day 2 tomorrow" email capture on the Day-1 completion screen** (pre-filled when known) | `app/src/app/(day1)`; `waitlist.ts` `tipsConsent` | 3× → view → owned contact | M |
| 2 | **Second-chance capture**: a DM user who declines email is offered Messenger/IG broadcast opt-in instead | `dm/flows/_global.json` `decline_email` branch | 2× → owned contacts per DM | M |
| 3 | **Printable Day-1 sheet by mail** for people who won't download (address capture, cost ~$1) | `app` form; fulfilment vendor [A] | 3× → 70+ conversion to member | L-M |
| 4 | **Phone number capture for "call me" coach slots** (R3), consent-gated | `app` R3 waitlist form; `notify.ts` | 2× → R3 bookings | L-M |
| 5 | **Email "reply to this" asks** in daily tips (replies lift deliverability) | `lifecycle/sequences.json` `daily_coach` | 2× → inbox placement | M |
| 6 | **Double-opt-in skip for DM-captured emails** (the DM tap is the confirmation) where lawful | `waitlist.ts` source `dm` | 2× → confirmed contacts | M |
| 7 | **Weekly printable PDF in the email** (fridge chart) | `products/*` + lifecycle | 2× → email opens | L-M |
| 8 | **"Forward to a friend" link in every email with `ref=`** | `notify.ts` footer; `bioLinks.ts` | 2× → referred signups | L-M |
| 9 | **Waitlist position + "move up by sharing"** (honest, no fake scarcity) | `/waitlist/confirmed` | 2× → waitlist referrals | L-M |
| 10 | **Members' Messenger opt-in at checkout success** | Shopify thank-you block link → Messenger `ref` | 2× → owned channels per member | L |
| 11 | **Postcard at renewal month 2** (100X §7.9 extension) for members with an address | Ops | 2× → renewal 2 | L |
| 12 | **SMS for live reminders only** (after 10DLC) | `notify.ts` | 2× → live attendance | L-M |
| 13 | **Email list segmented by keyword of entry** (KNEES, SLEEP…) | `waitlist.ts` stores keyword; sequences branch | 2× → email CTR | M |
| 14 | **Sun's weekly recipe email** for kitchen-entry contacts | `lifecycle` new sequence `kitchen_weekly` | 2× → kitchen opens | M |
| 15 | **Quiz → email** (Strength Age quiz already) **plus** "send me my chart" PDF | `quiz` result page | 2× → quiz → email | M |
| 16 | **Gift-recipient capture becomes a contact** (fresh consent at claim) | Exists; add tips consent tick | 2× → contacts per gift | M |
| 17 | **Exit-intent-free design** (no popups for 65+); inline capture only | Design rule | protects trust | M |
| 18 | **Large-type email template (20 px, never gray)** | `notify.ts` templates; test for gray | 2× → email CTR (65+) | M |
| 19 | **Plain-text email variant** test | `notify.ts` | 2× → deliverability | L |
| 20 | **List hygiene: suppress 90-day non-openers** (re-permission first) | `lifecycle` rule | protects deliverability | H |
| 21 | **BIMI/DMARC enforcement** for the sending domain | DNS checklist | 2× → open rate | M |
| 22 | **Welcome email from Chang with a real coach signature** | `lifecycle` `member_onboarding` | 2× → reply rate | L |
| 23 | **IG/FB profile link → `/go` capture first, store second during runway** (exists) **plus** returning-visitor skip | `bioLinks.ts` cookie | 2× → returning CTR | L |
| 24 | **Messenger broadcast + email same day** (two channels, one message) | `sender.py` + lifecycle | 2× → reach per message | L |
| 25 | **"Text me the link" option for people without email handy** (after 10DLC) | `/go` form | 2× → capture rate (70+) | L |
| 26 | **Community guidelines email for Group joiners** | Group Q export → lifecycle | 2× → Group activity | L |
| 27 | **Members-only "Courtyard" community** (built later per app README) prioritised over new channels | `app` roadmap | 2× → member retention | M |
| 28 | **Weekly "Sunday note" email from Sun** (story, not sales) | lifecycle | 2× → opens | L-M |
| 29 | **Push opt-in after the 3rd completed session** (not the 1st) test | `push.ts` | 2× → push opt-in | L |
| 30 | **Calendar subscription (ICS feed) for all lives and series drops** | `app` `/api/calendar.ics` | 2× → attendance | L |
| 31 | **Customer portal reminders as owned touchpoints** (pre-renewal value recap) | `reminders` cron | 2× → renewal | M |
| 32 | **Lead magnet per pillar** (knees, sleep, gut) mapped to keywords | `products/` | 2× → DM → email | M |
| 33 | **Warm-list import with consent provenance** (`data/warm_lists`) | Existing templates | protects | H |
| 34 | **Email-to-Group bridge** (invite the email list to the Group monthly) | lifecycle | 2× → Group joins | L |
| 35 | **Direct-mail "Strength Age chart" for top-decile engaged contacts** | Ops | 2× → member conversion | L |
| 36 | **Contact deduplication across email/Messenger/IG handle** | `schema.sql` `contacts` merge | 2× → attribution accuracy | M |
| 37 | **Consent ledger export** for every channel | `consent_log` report | protects | H |
| 38 | **Unsubscribe reason capture (one click, optional)** | `/api/unsubscribe` page | 2× → list learning | L |
| 39 | **Email send-time by recipient time zone** | lifecycle scheduler | 2× → opens | L-M |
| 40 | **Older-reader preview text** (plain, ≤40 chars) | templates | 2× → opens | L |
| 41 | **Day-7 "how did it go?" one-question survey** | lifecycle | 2× → feedback volume | L |
| 42 | **Contact-level "channel preference" (email/Messenger/text)** | `app` settings | 2× → response rate | L |
| 43 | **Quarterly re-permission email** for tips-only contacts | lifecycle | protects | M |
| 44 | **Owned "Strong Years Radio" podcast feed** (audio of sessions) | Later; RSS from `products` | 2× → session completions | L |
| 45 | **YouTube channel memberships off; email is the community** | Policy | focus | M |
| 46 | **Referral-tracked printable cards in the kit** (exists 100X §7.9) **plus** unique codes | Shopify insert | 2× → referral attribution | M |
| 47 | **Group → email capture KPI on `/admin/today`** | `/admin/today` | measure | H |
| 48 | **Opt-in from comments with "EMAIL" keyword** | `dm/flows` new `email.json` | 2× → DM → email | M |
| 49 | **Messenger and IG DM transcripts → contact notes** (with retention policy) | `dm/bot.py` store | 2× → personalised follow-up | L |
| 50 | **Owned-audience target per page** (contacts/1K followers) in the weekly review | `/admin/today` | measure | H |

## 8. Monetization and DM (MON-1 … MON-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **Day-1 session plays inside the DM** (video link + "Done / Too hard / Too easy" buttons), then the offer on "Done" | `dm/flows/begin.json` steps; `sender.py` | 3× → DM → paid | M |
| 2 | **Keyword-specific Day-1** (KNEES gets the knee session) | `dm/flows/knees.json` → `sessions.json` id | 2× → completion | M |
| 3 | **Offer in DM only after a user tap** (window rule, 100X §8.1) **plus** the price stated plainly | Flow copy | 2× → trust → paid | M |
| 4 | **Strength Age share card with a referral link** | `app` quiz result → image (`graphics`) → `/b?ref=` | 3× → referral share rate | M |
| 5 | **Gift path from FAMILY keyword in 2 taps** | `dm/flows/family.json` → `/gift` | 2× → gift purchases | M |
| 6 | **Cell B vs A test continues** (canon) **plus** a $9 cell for 70+ entry | `shopify` catalog new cell [A] | 2× → front-end conversion | L |
| 7 | **R3 coached program waitlist with honest cohort caps**, sold from the Group and the live | `shopify` `coached-12-week*` products; `app` R3 page | 3× → R1 → R3 ascension | M |
| 8 | **R2 Strength Age retest at week 6 triggers the R3 offer** (canon trigger) | `app` retest → lifecycle | 2× → R3 offers seen | M |
| 9 | **Human-hosted "start week" onboarding call** for each week's new members (a real coach, 20 min, recorded) | `lifecycle` `member_onboarding` step + Zoom link | 2× → month-1 retention | L-M |
| 10 | **Pause instead of cancel for travel/illness** (exists) **plus** surfacing it in the reminder email | `reminders` copy | 2× → saves | M |
| 11 | **Essentials save offer** (exists) **plus** measured save rate on `/admin` | `/admin` | measure | H |
| 12 | **Annual plan offered at the week-6 plateau inside the app** | `app` Today screen card | 2–3× → annual take | L-M |
| 13 | **Partner seat (+$8) offered at week 2** | `app` partner seat | 2× → seats | L |
| 14 | **Kit ($29) offered to members at month 2** (physical bands, cards) | Shopify kit | 2× → AOV | L |
| 15 | **Post-purchase thank-you block** (exists) **plus** a Group invite | Shopify block | 2× → Group joins | L |
| 16 | **DM "Talk to a human" path tags sales questions for a call-back** | `dm` HELP path → ticket type `sales` | 2× → hesitant buyer conversion | L-M |
| 17 | **Abandoned checkout email** (Shopify) in Chang's voice with the terms | Shopify notifications | 2× → recovery | M |
| 18 | **Price shown with "per day" equivalent ($0.83/day)** test | Theme copy | 2× → CVR | L |
| 19 | **Founding counter honesty** (exists) **plus** weekly public update post | Content slot | 2× → urgency without fake scarcity | L |
| 20 | **Affiliate program for PTs** (exists) **plus** a co-branded Day-1 link | `/affiliates`; `bioLinks.ts` `ref` | 2× → affiliate sales | L-M |
| 21 | **Guarantee shown in the DM before the link** | Flow copy | 2× → tap → purchase | L |
| 22 | **Shop Pay only where it works** (100X Holes #9 test result) | Theme | 2× → mobile CVR | M |
| 23 | **"Buy for a parent" flow** that ships the gift to the parent and setup checklist to the buyer | `/gift` + lifecycle | 2× → gift conversion | L-M |
| 24 | **One DM, one ask** (no stacking offers) | Flow lint in `compliance templates` | 2× → CVR | M |
| 25 | **DM follow-up at 23 h only if the user tapped** (inside window) | `sender.py` | 2× → conversion | M |
| 26 | **Refund-request save: offer Essentials or pause first** (canon) measured | `/admin` | measure | H |
| 27 | **Supplements subscribe-and-save at month 4 (R5)** via licensed partner | Shopify / clinical partner | 2× → ARPU | L |
| 28 | **Labs (R4) offered only by humans after R3** | Policy | protects | H |
| 29 | **Bundle "books + 3 months" at $59** test | Catalog [A] | 2× → upfront cash | L |
| 30 | **DM keyword "PRICE" answers price plainly** | `dm/flows` new `price.json` | 2× → qualified clicks | M |
| 31 | **Checkout page shows Chang + real coach photo** (honest) | Theme | 2× → trust | L |
| 32 | **Win-back at day 30 after cancel** (sequence exists) **plus** a "what changed" note | lifecycle `win_back` | 2× → win-back | L-M |
| 33 | **Monthly "member-only session" drop** announced publicly | Content slot | 2× → join intent | L |
| 34 | **DM language fallback to Spanish** on espanol pages | `dm/flows` `variants.es` | 2× → Spanish conversions | M |
| 35 | **Order bump copy tested** (Wall Plan vs kit) | Theme | 2× → bump rate | L |
| 36 | **Membership page FAQ answers the top 10 DM questions** | Theme FAQ from DM log | 2× → CVR | M |
| 37 | **Group-only R3 info session** monthly | CM | 2× → R3 sales | L-M |
| 38 | **Thank-you DM after purchase** (if the purchase came from a DM thread) | `dm` + webhook join on `mc_id` | 2× → activation | L |
| 39 | **"Bring a friend month" for members** (both get a free printable) | lifecycle | 2× → referrals | L |
| 40 | **Price-test guardrails on `/admin`** (stop when a cell is 2σ worse) | `/admin` | protects | M |
| 41 | **Founding close date announced 14 days ahead, once** (FUNNEL rule) | Content | 2× → close-week sales | M |
| 42 | **Post-launch evergreen offer = books $12 → membership** | Canon cell B | — | H |
| 43 | **R3 coach capacity planning sheet** from waitlist counts | `tools/organic_engine.py` | protects | M |
| 44 | **Corporate/senior-center bulk licences** (10+ seats) | Later product | 2× → B2B revenue | L |
| 45 | **Medicare Advantage fitness benefit research** (honest, no claims) | Holes item | 2× → channel | L |
| 46 | **DM rate limiter visible on `/admin/today`** (750/h cap) | `sender.py` metrics | protects | H |
| 47 | **Comment-keyword typo tolerance** (KNEE, KNESS) | `dm/bot.py` `norm` fuzzy | 2× → DM match rate | M |
| 48 | **One CTA keyword per post, same on all platforms** | `posting_rules.py` | 2× → keyword accuracy | M |
| 49 | **In-app "Ask a coach" (human) priced in R3 only** | `app` chat routing | 2× → R3 value | L |
| 50 | **Monthly revenue review per keyword and per page** | `/admin` | measure | H |

## 9. Characters and retention (CH-1 … CH-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **"Chang's 12-week arc"**: Chang follows the program in public, weekly numbered episodes | `build_content.py` series; CHARACTERS timeline | 3× → returning-viewer share | L-M |
| 2 | **"Your wins" episodes from member submissions** (100X §9.2) **plus** a weekly cadence | `app` upload form | 2× → member retention | L-M |
| 3 | **Sun's running bit library expanded to 48** (24 exist) | `CHARACTERS.md` §7 | 2× → duo variety | L |
| 4 | **Character "seasons" (monthly theme)** | `data/calendar.csv` | 2× → series completion | L |
| 5 | **Viewer Strong Weeks leaderboard read by Chang** (first names, opt-in) | `app` streaks → script variable | 2–3× → comments per follower | L-M |
| 6 | **Characters remember a commenter's earlier question** (public, opt-in only) | Mining DB | 2× → repeat commenters | L |
| 7 | **Real coach recurring cameo** (human video, not AI) | Coach shoot | 2× → trust → R3 | M |
| 8 | **"Ask Sun" Friday** fixed slot | Content slot | 2× → Friday returns | L |
| 9 | **Character birthday and anniversary episodes** | Calendar | 2× → shares | L |
| 10 | **A recurring "grandson visit" storyline** (fictional, labelled) | CHARACTERS | 2× → returning viewers | L |
| 11 | **Episode recap card at the start of series posts** | `overlay.py` | 2× → series completion | L |
| 12 | **Consistent intro sound (2 notes)** for series | Audio asset | 2× → recognition | L |
| 13 | **Members get early episodes 24 h ahead** | `app` Today | 2× → member value | L |
| 14 | **Retention email that references the latest episode** | lifecycle | 2× → app opens | L |
| 15 | **Character voice consistency check** (Resemblyzer score per render) | `qa` voice check | avoids ÷N "different voice" complaints | M |
| 16 | **Identity drift check (ArcFace vs locked C01/C02)** per render | `qa/face.py` | avoids ÷N | M |
| 17 | **Wardrobe continuity by day of week** (Chang's Monday flannel) | refs manifest | 2× → recognition | L |
| 18 | **Comment "first name" replies capped so they feel personal, not mass** | Writer quota | protects authenticity | M |
| 19 | **Dependency safeguards** (100X Holes #11) **plus** monthly audit of chat logs | `app` chat review | protects | H |
| 20 | **Characters never claim lived experience as fact** (canon) checked by judge | `compliance/judge.py` | protects | H |
| 21 | **Weekly "Chang tried it" challenge results** with real numbers | Content | 2× → engagement | L |
| 22 | **Sun's "kitchen science" study-card series** | F28 | 2× → saves | L-M |
| 23 | **Character-specific emoji set** in captions (minimal) | Packager | 2× → brand recall | L |
| 24 | **Members can choose the coach voice for reminders (Chang or Sun)** | `app` settings | 2× → reminder response | L |
| 25 | **Quarterly character survey** (what do you want from Chang?) | lifecycle | 2× → content fit | L |
| 26 | **A real-human "community host" persona** (named staff) for Group and DMs | Ops | 2× → trust | M |
| 27 | **Chang's mistakes on purpose** (form slip, Sun corrects) | Movement scripts | 2× → comments | L |
| 28 | **Monthly live "Q&A with the team who makes Chang"** (humans) | Live | 2× → trust | L |
| 29 | **Character "rest days" acknowledged** (models recovery) | Content | 2× → member adherence | L |
| 30 | **Series finale + new season announcement** | Content | 2× → follows | L |
| 31 | **Member milestone videos generated with consent** (name on screen) | `assemble` template | 2× → retention | L-M |
| 32 | **Retention cohort view by first-touch character** | App SQL view | measure | H |
| 33 | **Two-character hand-off posts** (Chang ends, Sun starts the next) | Allocator pairing | 2× → cross-page follows | L |
| 34 | **"Strong at 70" real member stories (human video)** | Shoot | 2× → trust | M |
| 35 | **Character newsletter signature lines** | lifecycle | 2× → reply rate | L |
| 36 | **Cultural reviewer sign-off on seasonal content** (with 100X §9.7) | Review queue | protects | H |
| 37 | **Personal "streak saver" message from Chang in-app** | `app` push | 2× → week-2 retention | L-M |
| 38 | **Monthly "letters" episode** (reading viewer letters) | Content | 2× → comments | L |
| 39 | **Same set + same time for the Sunday soup** | Production | 2× → ritual returns | L |
| 40 | **Character Q&A pinned FAQ video** | Pin | 2× → fewer repeated questions | L |
| 41 | **Chang's "form rule of the week"** recurring card | Overlay | 2× → saves | L |
| 42 | **Explicit "I'm AI; coach X is real" line in every R3 mention** | Writer rule; scanner | protects | H |
| 43 | **Character tone guardrails against elderspeak** (100X §4.9) **plus** reviewer spot checks | Review | protects | M |
| 44 | **Sun's verdicts on viewer recipes** (submitted photos, consent) | Upload form | 2× → submissions | L |
| 45 | **Member-only "Chang's notebook" printable each month** | `products` | 2× → retention | L |
| 46 | **Re-engagement episode for lapsed viewers** ("Haven't seen you…") | Retargeting-free; content | 2× → returns | L |
| 47 | **Characters age with the calendar** (birthdays, seasons) | CHARACTERS timeline | 2× → realism | L |
| 48 | **Consistent end card per character** | `overlay.py` | 2× → recognition | L |
| 49 | **Retention target per character** (returning-viewer share) on `/admin/today` | `/admin/today` | measure | H |
| 50 | **Annual "year with Chang" recap** for members | `app` | 2× → annual renewals | L |

## 10. Risk and ops (RO-1 … RO-50)

| # | Item | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **Trial-cap tripwire**: halt trials on the first limit or "unavailable" response, or a trial reach collapse | `growth/trials.py`; Slack | avoids ÷5 trial reach for 30 days (N1) | M |
| 2 | **Daily publish budget table per account** (IG 100 incl. trials; FB 25; TT ~15; Threads 250) enforced before scheduling | `posting_rules.py` quota (100X §10.7) **plus** trial counts | avoids API blocks | M |
| 3 | **Second reviewer on any trial with a health number** | Review queue rule | protects | H |
| 4 | **Same-page originality audit weekly** (IG-50) | `guard.py` report | avoids ÷5 | M |
| 5 | **Incident runbook for reach collapse** (pause trials, pause offers, check status, appeal) | `LAUNCH_RUNBOOK` appendix | 2× → recovery speed | M |
| 6 | **Appeal templates** for wrong AI-label or originality flags | `docs/platform_reviews` | 2× → appeal success | L |
| 7 | **Backup publisher path** (manual post pack) for every platform (exists) **plus** drills monthly | `packager/fallback.py` | protects cadence | M |
| 8 | **Token refresh alerts** (100X §10.8) **plus** an automatic re-auth reminder 10 days out | n8n | protects | H |
| 9 | **Vendor outage fallback** (fal → Hedra) tested monthly | Adapter test | protects | M |
| 10 | **Spend guardrail on trial renders** (month-to-date cap) | n8n guardrail | protects budget | H |
| 11 | **Health-claim rescan on edited captions** (any human edit re-runs pass 2) | n8n | protects | H |
| 12 | **Access control: 2FA + hardware key for all admins** | ACCOUNT_SETUP | protects | H |
| 13 | **Secrets rotation every 90 days** | `deploy/scripts/check_secrets.py` age check | protects | M |
| 14 | **Database backups tested (restore drill) monthly** | `deploy` | protects | H |
| 15 | **Crisis on-call coverage report weekly** | `/admin` | protects | H |
| 16 | **Legal review of every new keyword flow** | `python -m compliance templates` + counsel | protects | M |
| 17 | **Rate-limit dashboard (DMs, API calls)** | `/admin/today` | protects | M |
| 18 | **Comment moderation filters per page** (hidden words: scams, links) | Platform settings | protects | M |
| 19 | **Scam-clone search** (100X §10.10) **plus** a takedown log | Ops | protects | M |
| 20 | **Brand-safety review of B-roll library quarterly** | Review | protects | M |
| 21 | **Change freeze 48 h before D0** | Runbook | protects | H |
| 22 | **Staging store and staging app for every change** | `shopify` dev store; Vercel preview | protects | H |
| 23 | **Synthetic monitoring of `/b`, `/join`, `/go` every 5 min** | Uptime monitor | protects | H |
| 24 | **Webhook failure alert** (Shopify retries) | `/api/webhooks/shopify` metrics | protects | H |
| 25 | **Chargeback ratio alert at 0.5%** | `/admin` | protects | H |
| 26 | **Refund spike alert** | `/admin` | protects | H |
| 27 | **Review SLA alert when the human queue >2 h** | n8n | protects cadence | M |
| 28 | **Labelling audit sample (10 posts/day)** | Ops | protects | M |
| 29 | **Insurance (media liability, E&O)** before scale | Client | protects | M |
| 30 | **Coach credential verification log** | Ops | protects | H |
| 31 | **Clinical rungs (R4–R6) kept in the client's clinical entity** | Canon | protects | H |
| 32 | **Data retention policy for DMs and chat** | `app` privacy; jobs | protects | H |
| 33 | **Age-gate 18+ on DM flows that sell** | Flow step | protects | M |
| 34 | **Accessibility audit (WCAG AA) on app and store** | Playwright axe | protects | M |
| 35 | **Kill switch for a single keyword flow** | `dm/flows` `enabled` flag | protects | H |
| 36 | **Postmortems for every incident** in `docs/incidents/` | Ops | 2× → repeat avoidance | M |
| 37 | **Single source of truth for prices** (LAUNCH_RUNBOOK §0) with a test that copy matches catalog | `shopify/test` + app test | protects | H |
| 38 | **Third-party font/asset licence register** | `docs` | protects | M |
| 39 | **Platform policy watch** (weekly) feeding `adapters.py` review (100X Holes #13) | Ops | protects | H |
| 40 | **Shadow-ban-like symptoms checklist** per platform | Runbook | 2× → diagnosis speed | L |
| 41 | **Load test the members app for launch spikes** | k6 script | protects | M |
| 42 | **CDN for downloads** (watermarking stays server-side) | Vercel/R2 | protects | M |
| 43 | **Ops headcount plan for 20 trials/day/page** (review minutes) | `tools/organic_engine.py` | protects | M |
| 44 | **Two-person rule for spend or price changes** | `/admin` approvals | protects | H |
| 45 | **Weekly KPI review ritual (30 min)** | Ops | 2× → decisions | M |
| 46 | **Audit log for every admin action** (exists for exceptions) extended to price toggles | `/admin` | protects | H |
| 47 | **Children's content guard** (no minors on screen; grandkids are off-screen or adults) | Shot planner; QA | protects | H |
| 48 | **Copyright check on music** (original audio only) | `qa` | protects | H |
| 49 | **Clear separation of the K9SUPPS store** (deny list exists) tested in CI | `shopify/test` | protects | H |
| 50 | **Quarterly risk register review** | Ops | protects | M |

## 11. Holes we hadn't considered (X-H1 … X-H50)

| # | Hole | Where | × → metric | Conf |
|---|---|---|---|---|
| 1 | **VIRALITY_SYSTEM §6 item 6 mislabels Pew all-adult figures (84%/71%) as 65+** (N10) | Fix the doc; rerun any platform-weight priors that used them | avoids mis-weighted priors | H |
| 2 | **POSTING_PLAN.md says 21,756 rows; `posting_plan_90d.csv` has 13,800** (after canon 4) | Regenerate the summary tables from `tools/plan_summary.py` | protects planning | H |
| 3 | **"Adult child" landing and DM path for gift buyers** | `/gift` + `family.json` | 3× → FAMILY → gift purchase | L-M |
| 4 | **87% of planned rows are `GEN-needed`**: script supply is the bottleneck, not render | `build_content.py` daily GEN quota + writer throughput | 2× → on-time posts | H |
| 5 | **Trial Reels have no published daily cap** (N1); the target needs a probe, not a plan | `trials.py` | avoids ÷5 | M |
| 6 | **Trial Reels aren't exempt from originality rules** [S3] | `guard.py` applies to TRIAL | avoids ÷5 | M |
| 7 | **Meta AI translation output is labelled and voice-cloned**: check consent wording for an AI voice (our own) | Ops/legal | protects | M |
| 8 | **Hearing aids and Bluetooth audio** (some viewers listen through hearing aids) | Mix test on hearing-aid streaming | 2× → comprehension | L |
| 9 | **Cataracts and contrast**: yellow-on-white fails for some older eyes | `layout.py` palette check (blue-yellow) | 2× → readability | L-M |
| 10 | **Tremor and small tap targets in DMs** (buttons vs typing) | Flows prefer buttons | 2× → DM completion | M |
| 11 | **Shared devices** (a spouse's phone) and the email in DMs | Flow asks "whose email is this?" | 2× → correct contact | L |
| 12 | **Library e-books / Large-print PDF versions** | `products/` large-print | 2× → 75+ satisfaction | L |
| 13 | **Pinterest for kitchen content** (recipe pins) [A, no fresh age data found] | Later channel; `graphics.py` 2:3 pins | 2× → recipe traffic | L |
| 14 | **Nextdoor for local senior groups** [A] | Later; no automation | 2× → local reach | L |
| 15 | **Senior centers and libraries as offline distribution** (printed Day-1 sheets) | Affiliates | 2× → offline signups | L |
| 16 | **Caregiver audience** (people caring for parents) | Content pillar | 2× → shares | L |
| 17 | **Medicare/insurance questions in DMs** (never answer; route to human) | `dm` scope guard | protects | H |
| 18 | **Time-of-month income effect** (Social Security payment days) on purchases [A] | Offer timing test | 2× → offer CVR | L |
| 19 | **Daylight-saving shifts** for slot times (Nov 1 2026) | `posting_rules.py` uses tz-aware ET | protects | H |
| 20 | **Holiday ops coverage** (Thanksgiving, Christmas) for review and crisis | Rota | protects | H |
| 21 | **Voice-assistant users** (Alexa/Google) asking for "Chang's exercise" | Later skill | 2× → habit | L |
| 22 | **TV casting of YouTube long-form** (100X Holes #12) **plus** large lower-thirds test | `yt_long` | 2× → TV watch time | L |
| 23 | **Grandparent–grandchild challenges** (consent, no minors on our screen) | Content | 2× → shares | L |
| 24 | **Spanish-language compliance review** (claims scanner in Spanish) | `compliance/scanner.py` es lexicon | protects | H |
| 25 | **Korean-language audience for Sun** via Meta translation (N5) | Test | 2× → reach | L |
| 26 | **Screen-reader users** (alt text, captions) | Packager | 2× → accessibility | M |
| 27 | **Account recovery** if the admin's phone is lost | 2 admins + backup codes | protects | H |
| 28 | **Ad account for boosts not set up early** (approval time) | ACCOUNT_SETUP | protects timeline | M |
| 29 | **Platform age skew within 65+** (65–74 vs 75+) | Content arms | 2× → fit | L |
| 30 | **Seasonal affective / winter indoor routines** | Calendar | 2× → winter retention | L |
| 31 | **Weather-triggered content** (heat waves, icy sidewalks) | Calendar + news | 2× → timely shares | L |
| 32 | **Rural connectivity** (low bandwidth) for videos in the app | `app` video bitrate ladder | 2× → completion | L |
| 33 | **Printer-friendly pages** for every app screen | CSS print | 2× → use | L |
| 34 | **Phone support line** for 75+ buyers (a human number) | Ops | 2× → conversion (75+) | L |
| 35 | **Fraud on gift cards / promo codes** | Shopify limits | protects | M |
| 36 | **Fake "Chang" accounts selling supplements** | Clone watch | protects | M |
| 37 | **Press inquiries about AI characters** | Comms policy | protects | M |
| 38 | **Clinicians' attitudes** (doctors may warn patients) | Outreach to PTs | 2× → referrals | L |
| 39 | **Partner/spouse decision makers** | Content for couples | 2× → couple seats | L |
| 40 | **Platform outage days** (move posts, don't double-post) | `posting_rules.py` reschedule | protects | M |
| 41 | **Daylight hours for filming the performer** (seasonal shoots) | Production plan | protects | L |
| 42 | **Model deprecation (Kling, Veo versions)** | Adapter pins + tests | protects | M |
| 43 | **ElevenLabs v4 promo ends Oct 12** (STACK_FINAL) | Budget update | protects budget | H |
| 44 | **The midterm election week** (100X Holes #5) **plus** no political-adjacent topics (Medicare policy) | Calendar | protects | M |
| 45 | **Content for people with walkers or wheelchairs** (quiz route exists) | Seated series | 2× → inclusion reach | M |
| 46 | **Mental health crossover** (loneliness) handled by humans | Canon | protects | H |
| 47 | **Sun's cultural recipes and allergy notes** (sesame, shellfish) | Kitchen template | protects | M |
| 48 | **Units (US cups vs grams)** in recipes | `kitchen_recipes.json` both | 2× → recipe use | L |
| 49 | **"Is this a scam?" comment handling** script | Pinned reply template | 2× → trust | M |
| 50 | **Founder/owner visibility** (a real company face) | About pages | 2× → trust | L |

---

**Honest limits.** Most multipliers here are assumptions. The ones with citations rest on platform features (N2–N9), not on measured lift. The biggest uncertainty sits under the headline request: **no public source gives a Trial Reel daily cap**, and the one figure I found ("as low as five") is anecdotal [N1]. The 10–20/day/page target is therefore designed as a probe with a tripwire, not a fixed cadence. Facebook Trial Reels are rolling out unevenly and are not confirmed in the API [N3]. Meta AI translation and YouTube auto-dub are free and labelled, but their reach for AI-character content is untested. I found no fresh age-split data for Pinterest or Nextdoor.
