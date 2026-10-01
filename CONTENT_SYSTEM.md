# CONTENT_SYSTEM.md: the Chang Yin & Sun Yoon content engine

What's in here: pillars, share-of-feed per page, 39 format templates, the CTA keyword system, captions and hashtags per platform, engagement mechanics, series devices, the multi-page architecture with uniqueness rules, posting schedule, KPIs, and the 30-day calendar for the first 3 pages.
Companion files: CHARACTERS.md (who), HOOKS.md (390 hooks), SCRIPTS.md (150 scripts), ADS_SCRIPTS.md (40 paid ads), SCRIPTS_COVERAGE.md (coverage tables), SAFETY_RULES.md (checker), EVIDENCE.md (sources), FUNNEL.md and OFFER.md (what the keywords sell). Build tool: `tools/build_content.py`.

---

## 0. The thesis in 10 lines
1. **Yang Mun's winners were props and food, not wisdom.** The onion in water got 1M views and 10.3K comments; blueberries 411K; honey on tomato 305K. People stop for a *physical thing happening*. We keep the prop mechanic and swap the payload: **a test you can do right now, a food with a real trial behind it, or a myth being smashed on camera.**
2. **Participation beats contemplation.** "Stand up. Sit down. No hands. How many?" puts the viewer's body in the loop in the first 5 seconds. That drives watch time, comments ("I got 11!") and saves. Yang Mun's content asks you to *watch*. Ours asks you to *do*.
3. **A number the viewer owns** (chair-stand count, one-leg seconds, floor score, grip, walking speed) is the most commentable object in health content. It's also the hook into the **Strength Age quiz** (FUNNEL.md §3.1).
4. **Two characters create conflict. Conflict creates shares.** Sun roasting Chang's vanity gets tagged to husbands. Sun's blunt truths get sent to sisters. Chang's tests get sent to parents by their 40-year-old kids, the gift buyers.
5. **Trust is the moat.** Openly AI, study in every caption, "see your doctor" where it matters, and **public debunks of the viral remedies** Yang Mun used. Every debunk is a positioning ad against the category.
6. **Strength is the visual.** A 74-year-old lifting, carrying and getting off the floor without hands is inherently thumb-stopping. It's the one thing a seated robed monk can never do.
7. **One idea, one number, one keyword per video.** Keep it simple, like the HeyGen case study says, but make it specific.
8. **Volume through structure, not repetition.** 7 pages × 7 posts/day of *unique* masters come from pillar × format × hook × set × wardrobe combinations. Nothing gets reposted.
9. **Series create habit.** 7-Day Strong, 30-Day Balance, Fiber Ladder, Frank's Comeback and the 50th-anniversary countdown bring people back daily, which mirrors the product's daily-session habit (OFFER.md).
10. **Every post has a job.** It reaches (hook), trusts (evidence plus honesty), converts (keyword → DM → quiz → $1 trial), or retains (series, replies). The calendar balances all four.

---

## 1. Content pillars (20)
Each pillar has an evidence anchor (EVIDENCE.md IDs) and a default CTA. Pillars P01–P20 are used by HOOKS.md, SCRIPTS.md, the calendar and the pipeline.

| ID | Pillar | What it is | Evidence anchors | Default CTA | Primary formats |
|---|---|---|---|---|---|
| P01 | **Strength proof & tests** | Chang's feats (labeled) + the viewer's self-tests (chair stand, one-leg, floor, grip, gait) | E06–E11, E03 | TEST / STRONG | F02, F16, F23 |
| P02 | **Legs & chair strength** | Sit-to-stand variations, step-ups, squats to a chair, wall sits | E01, E02, E20 | STRONG | F01, F17, F15 |
| P03 | **Balance & steady feet** | Otago-style drills, habit-stacked balance, home hazards | E12, E13, E14, E36 | BALANCE | F02, F15, F32 |
| P04 | **Grip, upper body & carry** | Towel wrings, carries, counter push-ups, jar tests | E07, E01 | STRONG / TEST | F15, F02 |
| P05 | **Mobility & stretching** | Hips, thoracic spine, ankles, shoulders; bed routines | E30, E30b | BACK | F20, F05, F01 |
| P06 | **Back/knee/shoulder relief & rehab** | Progression ladders, pain-monitoring rule, red flags | E30, E01, E15, E41 | BACK / KNEES | F14, F03 |
| P07 | **Breathwork & nervous system** | Cyclic sighing, 4-6 breath, exhale-first | E18, E19 | BREATH | F21 |
| P08 | **Tai chi / qigong / gentle yoga** | As exercise, with trial data; outdoor flows | E14, E15, E16, E17 | BALANCE / SLEEP | F22 |
| P09 | **Sleep & evening** | Wind-downs, night-bathroom safety, snoring red flag | E19, E46, E48 | SLEEP | F05 |
| P10 | **Digestion & gut** | Fiber ladder, post-meal walks, fermented foods | E23, E24, E25, E26 | GUT | F06, F31 |
| P11 | **Sun's kitchen: recipes** | Korean/Chinese home food, soups, cooking for one | E28 (+ cautions) | SOUP | F31, F12 |
| P12 | **Kitchen remedies with evidence** | Honey (cough), kiwi, prunes, ginger (honest), what not to use | E25, E27, E32, E33, E34 | GUT / SOUP | F06 |
| P13 | **Protein & muscle food** | Grams per meal, plate builds, cheap protein | E28 | SOUP | F18, F12 |
| P14 | **Physiology in 30s** | One mechanism with an anatomy inset (calf pump, fast fibers, bed-rest loss) | E04, E05, E47 | STRONG | F13, F30 |
| P15 | **Myth-busting** | Viral remedies, "too old", "walking is enough", vitamin D for falls | E-varies | varies | F04, F28 |
| P16 | **Blunt truths: aging, mindset, women 60+** | Sun's verdicts, loneliness, boundaries, grief, pro-living | E37 (+ opinion) | BEGIN / FAMILY | F07, F35 |
| P17 | **Couple life & relationships** | Banter, marriage wisdom, couple challenges | E37, varies | BEGIN / varies | F08, F34, F35 |
| P18 | **Community replies & Q&A** | Stitch or reply to real comments, Q&A stickers, "Sun reads comments" | varies | varies | F09, F10, F26 |
| P19 | **Challenges & series** | 7-Day Strong, 30-Day Balance, Fiber Ladder, retests | E01, E12, E24 | STRONG / BALANCE / GUT | F11 |
| P20 | **Behind the AI / trust** | Disclosure, how we pick studies, reviewer intros (real people only) | — | BEGIN / TEST | F08, F28 |

---

## 2. Formats (39 templates)
**House rules for every format:** frame 1 = motion or prop (never a static intro). Hook spoken and on screen within 0.5 s. Re-hook at 3–6 s. Payoff by 60% of runtime. Show-not-tell (≤30% talking head for Chang). One keyword said in the last line, on screen, and in caption line 1. `AI character` tag always on. On-screen text ≤7 words per card, ≤2 lines, high contrast (**no gray text**), no "//" or mono index-label decorations.

**Platform-fit key:** IG = Instagram Reels · TT = TikTok · YT = YouTube Shorts · FB = Facebook Reels · TH = Threads (text) · ★ = strongest fit.

### F01 Follow-Along Routine
- **Length:** 35–45 s (Reels/Shorts). A 60–90 s cut goes to FB/YT.
- **Beats:** 0–3 hook ("Do this with me. 40 seconds.") → 3–6 set up support (chair/counter visible) → 6–38 three moves × ~10 s each, real-time, rep counter on screen, one cue per move → 38–45 CTA.
- **Shots:** full body, eye level, fixed tripod-feel with a slight handheld drift. Rep counter top-right. A regression PiP (Frank) bottom-left for one move.
- **On-screen text:** move name + one cue ("Chair stands · breathe out up").
- **CTA:** STRONG / BACK / BALANCE. **Fit:** FB★ IG★ YT TT.

### F02 "Can You Do This?" Test
- **Length:** 35–45 s.
- **Beats:** 0–3 command-hook ("Sit down. Stand up. No hands.") → 3–9 safety setup → 9–20 the test demo with timer → 20–26 Chang's score (labeled "his level") → 26–35 **norm or study number** (E06–E11) → 35–41 regression ("Need hands? Start anyway") → CTA "Tell me your number / Comment TEST".
- **Shots:** timer or counter overlay, study card inset, Frank for the regression.
- **On-screen text:** test name as the title card, norms as one line.
- **CTA:** TEST / BALANCE / STRONG. **Fit:** TT★ IG★ YT★ FB★. Highest-commenting format; lead with it on day 1.

### F03 Form Fix (✗ / ✓)
- **Length:** 30–40 s.
- **Beats:** 0–3 wrong version with ✗ + quoted myth → 3–9 why (one mechanism line) → 9–25 right version, 2–3 cues → 25–32 real-life application (lift the laundry basket) → 32–36 red flag → CTA.
- **Shots:** side profile for hinges and squats. A split-screen ✗/✓ for 2 s.
- **CTA:** BACK / KNEES. **Fit:** IG★ YT★ TT FB.

### F04 Myth-Bust with Prop (the Yang Mun killer)
- **Length:** 30–40 s.
- **Beats:** 0–3 the viral prop in hand (onion glass, salt, detox tea) + "Everybody is doing X. [Verdict]." → 3–9 "Show me the study" → none → 9–19 what the evidence *does* show (with a number) → 19–29 the prop's honest use (onion goes in soup) → 29–35 medication or doctor line → CTA.
- **Shots:** SET-TABLE prop close-up, Sun's over-the-glasses look, B-roll of the evidence-backed alternative.
- **On-screen text:** "MYTH ✗ ___" (required label, SAFETY MB-EX).
- **CTA:** SOUP / GUT / BEGIN. **Fit:** TT★ IG★ FB★ YT. Never name a creator. Say "the internet".

### F05 "Do This Before Bed"
- **Length:** 30–45 s.
- **Beats:** 0–3 "Before bed tonight… lying down… 90 seconds" → 3–30 two or three gentle moves in bed → 30–38 slow-breath finish (4-in/6-out) → 38–45 "sit before you stand" + CTA SLEEP.
- **Shots:** SET-BED, warm lamp, overhead plus side. Breathing ring animation.
- **CTA:** SLEEP / BACK. **Fit:** IG★ FB★ YT. Post at 21:00 in the viewer's local time.

### F06 Kitchen Remedy with Evidence
- **Length:** 30–40 s.
- **Beats:** 0–3 food prop + hook → 3–12 the trial (population, dose, result) → 12–18 honest size ("small study") → 18–27 how to eat it → 27–33 who should skip it (SAFETY §5) → CTA GUT/SOUP.
- **Shots:** CU food prep, study card inset, Chang tasting (bit).
- **CTA:** GUT / SOUP. **Fit:** IG★ FB★ TT YT.

### F07 Sun Yoon's Blunt Answer
- **Length:** 25–40 s.
- **Beats:** 0–3 one-line verdict to camera → 3–10 reason (a number if it's a health topic) → 10–25 the practical fix (one action) → 25–32 the soft line → CTA or share line ("Send this to your sister").
- **Shots:** SET-TABLE or SET-LIVING, jade cardigan, tea. Mostly CU. Optional cutaway.
- **CTA:** BEGIN / FAMILY / KNEES / STRONG. **Fit:** IG★ FB★ TT★ TH (text version).

### F08 Couple Banter Sketch
- **Length:** 25–40 s.
- **Beats:** 0–3 Sun's setup line (bit) → 3–8 Chang's excuse → 8–20 the lesson (one number) delivered inside the bit → 20–30 escalation or payoff → 30–35 tender or roast button → CTA.
- **Shots:** two-shot, with Sun's reaction in CU. She enters from the left.
- **CTA:** varies. **Fit:** TT★ IG★ FB★ YT.

### F09 Stitch / Reply to Comment
- **Length:** 25–40 s.
- **Beats:** 0–2 the comment on screen (IG/TT reply sticker; real comment, public, handle shown only with permission or blurred) → 2–5 character reaction → 5–30 answer (evidence or safety) → CTA.
- **Rules:** answer *general* questions only. Individual medical questions get "that's for your doctor" plus a general version. Never a testimonial (SAFETY T-02).
- **Fit:** TT★ IG★.

### F10 Q&A Sticker Reply
- **Length:** 20–35 s.
- **Beats:** 0–2 IG question sticker graphic (from Stories Q&A) → answer in a 3-beat structure → CTA.
- **Note:** run Q&A stickers in Stories 3×/week to harvest questions (Yang Mun's "Why do my headaches and acid reflux keep coming back" sticker did 98.7K).
- **Fit:** IG★ FB.

### F11 Challenge Episode (7-Day / 30-Day)
- **Length:** 35–45 s.
- **Beats:** 0–3 "Day N." + the day's promise → 3–8 yesterday's recap (fridge numbers) → 8–35 today's routine → 35–41 "Type N if you did it" + CTA.
- **Devices:** a persistent "DAY N/7" badge top-left, the same music bed, the same set, and a playlist/highlight.
- **CTA:** STRONG / BALANCE / GUT. **Fit:** IG★ TT★ FB★ YT (playlist).

### F12 What I Eat in a Day (at 74 / 76)
- **Length:** 40–45 s (a 60 s FB cut).
- **Beats:** 0–3 "What a 74-year-old who lifts eats in a day" → 4 meals × 8 s each with a protein counter → final total vs target (E28) → caution (kidneys) → CTA SOUP.
- **Shots:** overhead plates, a gram counter animating, Sun commentary VO ("He wanted a fifth dumpling. No.").
- **Fit:** IG★ TT★ YT.

### F13 Physiology in 30s (anatomy inset)
- **Length:** 30–40 s.
- **Beats:** 0–3 surprising mechanism hook ("You have a second heart in your legs") → 3–15 mechanism with an **anatomy inset** (top-right, illustrated, labeled) → 15–30 the move that uses it → 30–35 red flag if relevant → CTA.
- **Shots:** Chang demo + inset. Use an illustrated inset, not photoreal organs.
- **Fit:** YT★ TT★ IG.

### F14 Rehab Progression Ladder
- **Length:** 35–45 s.
- **Beats:** 0–3 the loop or problem → 3–11 evidence → 11–30 levels 1-2-3 (Frank = L1, Chang = L3) with a "move up when…" rule → 30–37 pain-monitoring rule → 37–41 red flag → CTA KNEES/BACK.
- **Fit:** YT★ IG★ FB.

### F15 "The One Exercise" / 3-Move List
- **Length:** 30–40 s.
- **Beats:** 0–3 promise ("3 moves. 3 times a week.") → evidence (one number) → move 1/2/3 at ~6 s each → safety → CTA.
- **Fit:** IG★ (saves) FB★ YT. Also works as an IG carousel (F36).

### F16 Number Shock / Stat Card
- **Length:** 25–35 s.
- **Beats:** 0–3 the number big on screen (e.g., "84%") with a prop action → 3–12 the population and context (C-grade = "linked") → 12–25 what to do about it (a test or move) → CTA TEST.
- **Rule:** SAFETY C-03, which requires population context on screen with any relative risk.
- **Fit:** TT★ YT★ IG.

### F17 Chair Coach (all seated or chair-supported)
- **Length:** 35–45 s.
- **Beats:** 0–3 "Can't stand long? Stay in the chair." → 5 seated moves → CTA STRONG.
- **Audience:** the deconditioned and 80+. It's the entry to the "Rebuild" track (OFFER.md). "Say hello to Coach" (the chair bit).
- **Fit:** FB★ IG YT.

### F18 Protein Plate Build
- **Length:** 30–40 s.
- **Beats:** 0–3 the "short" plate on a scale → add items with a gram counter → total vs 25–30 g/meal → kidney caution → CTA SOUP.
- **Fit:** IG★ TT★ FB.

### F19 Market Walk
- **Length:** 35–45 s.
- **Beats:** Sun walks an aisle: 3 buys (protein/fiber/fermented) + 1 "put it back" (a detox tea, a sugar "health" drink) → price + grams → CTA.
- **Set:** SET-MARKET (unbranded shelves, no real store names or logos).
- **Fit:** TT★ IG.

### F20 Morning Wake-Up Routine
- **Length:** 35–45 s.
- **Beats:** in bed → sitting → standing at the counter. Safety on standing up (E46). CTA BACK.
- **Post at:** 06:45 local.
- **Fit:** FB★ IG★.

### F21 Breath Reset (timed)
- **Length:** 30–45 s.
- **Beats:** 0–3 hook → evidence (E18/E19) → 15–25 s of *actual* guided breathing with a visual ring → no-hold safety → CTA BREATH.
- **Fit:** IG★ YT★ FB (looping).

### F22 Tai Chi / Qigong Minute
- **Length:** 35–45 s.
- **Beats:** 0–3 myth or number hook → trial data → one move taught with a rail or counter for support → "slow is the point" → CTA BALANCE/SLEEP.
- **Set:** SET-PROM fog or SET-YARD dusk. Soft ambient audio. Never temple imagery.
- **Fit:** IG★ FB★ YT.

### F23 Duet / "Do It With Me" Challenge
- **Length:** 30–40 s.
- **Beats:** Chang on the right half of the frame (leaving space) → a timed hold or reps → invite: "Duet me. Tell me your time."
- **Fit:** TT★ (Duet) IG (Remix).

### F24 3 Mistakes After 60
- **Length:** 30–40 s.
- **Beats:** mistake 1/2/3 (✗ then ✓ each, ~8 s) → CTA.
- **Examples:** holding your breath, using chair arms, only walking.
- **Fit:** IG★ YT★.

### F25 Frank's Level (side-by-side regression)
- **Length:** 30–40 s.
- **Beats:** Chang's version (labeled) vs Frank's version, split screen → "Frank's version is where most people start" → humor beat → CTA.
- **Rules:** Frank never reports results (SAFETY T-03).
- **Fit:** IG★ FB★ TT.

### F26 Sun Reads Comments
- **Length:** 30–45 s.
- **Beats:** 3–4 real (permissioned or anonymized) comments read by Sun with blunt, warm replies → one number or action → CTA.
- **Rules:** no testimonials of results. Choose questions and stories, not outcome claims.
- **Fit:** IG★ FB★ TT.

### F27 Wisdom Minute / Letter to My Younger Self
- **Length:** 30–45 s.
- **Beats:** slow push-in, reflective line → one concrete life or health lesson (with evidence if it's a health lesson) → tender close → soft CTA.
- **Set:** SET-LIVING evening or SET-PROM. Soft piano.
- **Note:** this is Yang Mun's "wisdom" lane (his top YT = "1 minute of wisdom"), but grounded in labor, marriage and science, never mysticism.
- **Fit:** FB★ YT★ IG.

### F28 Study Card / "Show Me the Study"
- **Length:** 30–40 s.
- **Beats:** 0–3 quoted myth → the printed card pulled from Chang's shorts pocket (bit) → 3 facts (who, how many, result) → the practical move → CTA.
- **Rules:** the card must be exact (SAFETY V-03).
- **Fit:** IG★ YT★ TT.

### F29 Walk & Talk
- **Length:** 35–45 s.
- **Beats:** tracking shot on the promenade. One idea, told walking. Step counter overlay. Stop for a bench move. CTA.
- **Fit:** FB★ YT IG.

### F30 Prop Anatomy (skeleton/spine model)
- **Length:** 30–40 s.
- **Beats:** Chang holds a spine or knee model (Yang Mun's skeleton-prop format, done accurately) → where load goes → the move → CTA.
- **Fit:** YT★ IG.

### F31 Recipe in 40
- **Length:** 35–45 s.
- **Beats:** 0–3 finished dish + hook → steps with quantities (overhead, 2–3 s each) → protein/fiber number → caution (sodium, iodine, etc.) → Chang tastes (grade bit) → CTA SOUP/GUT.
- **Fit:** IG★ FB★ TT★ YT.

### F32 Habit Stack ("While You…")
- **Length:** 25–35 s.
- **Beats:** existing habit (brushing teeth, kettle boiling, TV ads) + an attached drill → progression → CTA.
- **Note:** this is Yang Mun's "do this before you brush" format, but with a real drill.
- **Fit:** IG★ TT★ FB.

### F33 Send This to Your Parent (family share)
- **Length:** 25–40 s.
- **Beats:** 0–3 hook aimed at the **adult child** ("Your dad won't do this. Show him anyway.") → the one test or move → "Do it *with* them" → CTA FAMILY.
- **Audience:** 35–55 buyers of the gift offer (OFFER.md). Post in the 12:45 and 19:00 slots.
- **Fit:** IG★ TT★ FB.

### F34 Couple Workout / Couple Challenge
- **Length:** 30–40 s.
- **Beats:** the challenge setup (bet: dishes, tea) → exercises side by side (no partner-balance holds) → winner reveal → evidence line → CTA.
- **Fit:** TT★ IG★ FB.

### F35 Heart-to-Heart (relationships / letting go)
- **Length:** 30–45 s.
- **Beats:** a question from "a viewer" (real, paraphrased, anonymized) → Sun's blunt opinion → soft reframe → one action → a professional-help line where relevant → CTA BEGIN or a comment prompt.
- **Note:** this is Yang Mun's @itsyangmuns lane ("Let them"), done with honesty. **Crisis topics trigger SAFETY §4.4** (no script).
- **Fit:** FB★ IG★ TT.

### F36 IG Carousel (static, 7–10 slides)
- **Structure:** slide 1 hook (a number or test) → slide 2 who/why (study) → slides 3–7 steps with illustrations of Chang/Sun → slide 8 regressions → slide 9 safety → slide 10 CTA "Comment ___".
- **Rules:** 1080×1350, high contrast. Each carousel is unique to its page. Carousels rank on saves.
- **Cadence:** 1/day per page on IG (counts toward the daily 6–9).

### F37 Threads / Facebook Text Post
- **Structure:** Sun's one-line verdict + 3-line explanation + a question. Or Chang's "today's number" + a prompt.
- **Cadence:** 3–5/day on Threads (low cost, harvests comments for F09/F35).
- **Fit:** TH★ FB★.

### F38 Doors Open / Offer Card (founding launch week)
- **Length:** 45–50 s.
- **Beats:** 0–3 a physical "open" moment (garage door rolling up, whiteboard flipped, recipe card slapped down) → 3–17 what's inside, shown on the real product screens → 17–35 the offer terms said plainly: price, first month charged today, renews monthly, cancel online anytime, 14-day money-back, founding price stays while subscribed → 35–41 the real cap (first 5,000, live count on the page; never a "spots left" number) → doctor line → CTA JOIN.
- **Rules:** SAFETY S-01/S-02/T-04. `{{FOUNDING_PRICE}}` is filled from the live price split. No outcome promise, no countdown clock.
- **Fit:** IG★ FB★ TT (bio link) YT. Scripts S135, S138, S140, S141, S145, S149.

### F39 Pinned Post (founding-week variants)
- **Length:** 45 s.
- **Beats:** the CHARACTERS.md §9.2 pinned-post jobs (disclosure, "what's real", where to start) in each page's own voice, with the reviewer-gate FALLBACK wording until a reviewer signs.
- **Fit:** pinned on IG/TT/FB. Scripts S136 (Chang), S144 (Sun), S146 (Duo).

---

## 3. Share-of-feed targets per page (%)
The calendar builder (`SHARE` in tools/build_content.py) balances NEW slots toward these targets.

| Pillar | @changyin | @sunyoon.kitchen | @changandsun | @changyin.strength | @changyin.mobility | @sunyoon | @changyin.espanol |
|---|---|---|---|---|---|---|---|
| P01 Strength proof & tests | 12 | – | 6 | 20 | – | 6 | 12 |
| P02 Legs & chair | 9 | – | – | 22 | – | – | 10 |
| P03 Balance & falls | 12 | – | 8 | – | 10 | 8 | 12 |
| P04 Grip/upper/carry | 6 | – | – | 15 | – | – | – |
| P05 Mobility | 5 | – | – | – | 20 | – | – |
| P06 Back/knee/shoulder | 5 | – | – | 8 | 18 | – | 8 |
| P07 Breath | 4 | – | 5 | – | 14 | – | – |
| P08 Tai chi/qigong | 5 | – | – | – | 16 | – | – |
| P09 Sleep | 4 | – | 2 | – | 12 | – | – |
| P10 Gut | 2 | 15 | – | – | – | – | 6 |
| P11 Recipes | – | 22 | – | – | – | 5 | 8 |
| P12 Kitchen remedies | – | 13 | – | – | – | – | – |
| P13 Protein | 3 | 15 | 6 | 4 | – | 6 | 6 |
| P14 Physiology | 7 | 2 | – | 10 | – | – | 6 |
| P15 Myth-busting | 8 | 12 | 6 | 8 | 5 | 10 | 10 |
| P16 Blunt truths | 4 | 8 | 15 | – | – | 40 | 8 |
| P17 Couple | 2 | 3 | 35 | – | – | 10 | 6 |
| P18 Replies/Q&A | 4 | 5 | 8 | 5 | 5 | 12 | 4 |
| P19 Challenges/series | 6 | 5 | 6 | 8 | – | – | 4 |
| P20 Behind the AI | 2 | – | 3 | – | – | 3 | – |
| **Total** | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

**Rebalancing rule:** after day 14, each page's shares shift ±30% toward the pillars with the best **keyword-comments per 1,000 views** (conversion) and **shares per 1,000 views** (reach), but never below 50% of target for P03, P15 and P18 (the trust and safety pillars).

---

## 4. CTA keyword system → offers
**One keyword per video.** It's said in the last spoken line, shown on screen, written in caption line 1 ("Comment STRONG for…"), and repeated in a pinned comment. Keywords rotate so each page uses **every live keyword at least once a day**. The ManyChat flows are in FUNNEL.md §4 and the offer ladder is in OFFER.md.

| Keyword | Promise in the video (access, never outcome) | DM deliverable | Next step | Monetization path |
|---|---|---|---|---|
| **STRONG** | "the 8-minute chair builder" | 8-Minute Chair Builder (FUNNEL §4.3) | +22 h check-in → Strength Age quiz | Quiz → the visitor's blitz cell (F25/F30 charge-today at $25/$30, or T25 $1 × 7 days → $25; FUNNEL.md §0.2.1). Post-blitz baseline: $1 × 7-day trial → $20/mo |
| **BALANCE** | "the Steady Feet routine" | Steady Feet + 10-s test (§4.7) | Quiz | Same |
| **BACK** | "Morning Unlock" | 7-min routine starting in bed (§4.4) | Quiz | Same; program "Back Strong" inside membership |
| **KNEES** | "the Step Builder" | 10-min bottom-stair routine (§4.8) | Quiz | Same |
| **SLEEP** | "the wind-down" | Sleep Wind-Down, night 1 (§4.5) | Quiz | Same |
| **BREATH** | "the 4-6 breath" | 5-min guided breath (§4.9) | Quiz | Same |
| **SOUP** | "three of my soups" | Sun Yoon's Three Soups (§4.6) | Kitchen lesson → $17 Strong Kitchen bundle (7 days of membership included, OFFER front end C) | Membership |
| **BEGIN** | "where to start" | "Where should I begin?" menu (§4.10) | Picks a pain → session → quiz | Membership |
| **TEST** *(extended)* | "your strength age" | Direct link to Strength Age quiz (FUNNEL §3.1) | Result page → $1 trial | Membership |
| **FAMILY** *(extended)* | "the gift version" | "Give Mom & Dad" gift page (OFFER: 3 mo $49 / 12 mo $119, prepaid, no auto-renew) | Gift checkout | Gift → recipient converts at gift end (opt-in only) |
| **GUT** *(extended, new flow)* | "my 7-day fiber ladder" | Sun Yoon's 7-Day Fiber Ladder (PDF + 7 daily DMs, inside 24 h window, then email) | Kitchen lesson → quiz | Membership ("Gut Reset with Sun Yoon" program) |
| **JOIN** *(blitz, new flow)* | "the founding-member link and the full terms" | DM 1: AI-automation disclosure + the founding terms in plain words (price, first month charged today, renews monthly until cancelled, cancel online anytime in ≤2 screens, 14-day money-back, founding price stays while subscribed, first 5,000) → button to `/join` | Founding checkout (charge today, BLITZ.md arm B) | Membership MRR on day 0 (clone the TEST flow; used by the launch-week scripts S135–S150) |

**Blitz mode (the launch default, OFFER.md §0.1):** every "$1 trial" and "$17 front end" step in the Monetization column routes to the founding checkout `/join` instead ({{FOUNDING_PRICE}} charged today, $25 default display vs $30 test, 14-day money-back guarantee, cap 5,000; the $7 Reset and $17 Kitchen are order bumps there). The $20 control and the $1 trial are the non-blitz baseline. JOIN's full ManyChat flow is FUNNEL.md §4.17.

**Spanish page keywords** (map to the same flows, ES copy): FUERTE (STRONG), EQUILIBRIO (BALANCE), ESPALDA (BACK), RODILLAS (KNEES), SUEÑO (SLEEP), RESPIRA (BREATH), SOPA (SOUP), EMPEZAR (BEGIN), PRUEBA (TEST), FAMILIA (FAMILY).

**Platform mechanics**
- **IG + FB:** ManyChat comment→DM (works worldwide). Pin the keyword comment. Add misspellings to triggers (FUNNEL §4.1).
- **TikTok (US has no comment triggers):** the spoken CTA becomes "Tap the link in my bio and choose STRONG" on TT renders (the pipeline swaps the last line per platform). The bio link goes to `{{DOMAIN}}/tt` with keyword tiles. The keyword also works as a TikTok DM keyword auto-reply where available.
- **YouTube Shorts:** "Link below: STRONG" plus the related-video link to a long-form or a pinned comment with `{{DOMAIN}}/strong`. Description line 1 = the link.
- **Threads:** no automation. "Comment STRONG and we'll reply with the link" is answered by a human-in-the-loop bot, rate-limited.

**Keyword rotation per page per day (7 posts):** the 3 highest-converting keywords (by DM→trial) get 2 slots each, and the rest rotate through 1 slot. It re-ranks weekly.

---

## 5. Captions & hashtags per platform

### 5.1 Caption anatomy (all platforms)
1. **Line 1: CTA** "Comment STRONG for the 8-minute Chair Builder." (FUNNEL rule; ManyChat relies on it)
2. **Lines 2–4: value plus the study**, with a plain-English citation (journal + year) and numbers matching EVIDENCE.md.
3. **Line 5: safety or who-should-skip**, when relevant.
4. **Search line (TT/YT/IG):** natural phrases people type, e.g. "balance exercises for seniors, steady on your feet over 65".
5. **Hashtags** (see below).
6. **Footer** (auto): the AI disclosure + not-medical-advice string (SAFETY §7).

### 5.2 Per platform
| Platform | Caption length | Hashtags | Title/keyword SEO | Notes |
|---|---|---|---|---|
| **Instagram Reels** | 300–600 chars before the footer | 3–5: 1 broad (#over60), 2 niche (#chairexercises), 1 character tag (#changyin) | Line 2 contains the search phrase (IG search indexes captions) | Carousel captions can be longer. Add alt text. Collab posts between our pages are banned (uniqueness). Use them only with real partners. |
| **TikTok** | 150–300 chars | 3–5 incl. 1 trending-adjacent (#over60, #healthyaging, #koreangrandma) | On-screen keyword text in the first 3 s + a spoken keyword (TT search reads both) | AI-generated toggle ON. Original audio. No watermarks from other apps. |
| **YouTube Shorts** | Title ≤60 chars, plus a description with the link on line 1 | 2–3 in the description | Title = search phrase + curiosity ("…(Over 60)") | Altered-content toggle = Yes. Link to a long-form "hub" video per pillar (YT's compounding channel). |
| **Facebook Reels** | 200–500 chars | 1–3 | Plain sentences | The 55+ core audience. Longer (60–90 s) cuts of F01/F17/F27 do well. Share to Groups only where the rules allow. |
| **Threads** | 1–5 lines | 0–1 | — | Sun's text verdicts (F37). The question at the end harvests F09 material. |

### 5.3 Hashtag banks (rotate; never the same set twice in a row on a page)
- **Strength:** #strengthafter60 #over60fitness #seniorfitness #chairexercises #strengthtraining #over70 #liftingover60 #homeworkout
- **Balance:** #balancetraining #steadyfeet #balanceexercises #otago #taichi
- **Mobility/back/knees:** #mobility #morningstretch #kneestrength #hiphinge #stretching #morningroutine
- **Breath/sleep:** #breathwork #cyclicsighing #bedtimeroutine #sleepbetter #qigong
- **Kitchen:** #highfiber #fiber #koreanfood #kimchi #proteinbreakfast #cookingforone #koreangrandma #highprotein
- **Blunt/life:** #proaging #womenover60 #womenover70 #marriageadvice #friendship #agingparents
- **Characters:** #changyin #sunyoon #changandsun #aicharacter
- **Banned** (look spammy or copy Yang Mun): #usa #usahealth #newyork #wellnessjourney #healing #chinesemedicineworks #monk #detox · and any condition hashtag (#fallprevention, #kneepain, #backpain, #bloodpressure, #arthritis…): the build blocks them (tools/build_content.py `CONDITION_HASHTAG`)

---

## 6. Engagement mechanics

### 6.1 Comment prompts that produce stories (rotate; they feed F09/F26/F35 and build the confessional community Yang Mun has)
1. "What age did you first feel old? Sun Yoon wants to argue with you."
2. "Tell me your chair number. No shame. Twelve or three."
3. "Who taught you to cook? Name and dish."
4. "What's the one thing you want to be able to do at 85?"
5. "Married how long? Tell Sun the secret. She'll grade it."
6. "Who do you need to call this week? Just the first name."
7. "What's the worst health 'trick' you tried from the internet?"
8. "Your mother's cure-all dish. Go." (the dish, not a claim)
9. "What did you stop doing because you were scared of falling?"
10. "Which grandchild do you want to keep up with? Name and age."
11. "What would you tell your 50-year-old self?"
12. "Rate your balance 1–10. Then test it and tell me the real number."
13. "What's in your fridge that Sun would throw out?"
14. "What did your doctor say that you didn't want to hear?" (no medical replies, just empathy + "follow it")
15. "Widowed friends: what's your Tuesday dinner?"
16. "Name one person who kept you going this year."
17. "What's your stubborn husband's excuse for not stretching?"
18. "Did you forgive them? Yes, no, working on it."
19. "What did you carry today that you couldn't last year?" (effort, not product claims)
20. "Where do you walk? Describe it in 5 words."
21. "What's the hardest stair in your life? Front stoop, bus step, church steps?"
22. "Which food from childhood do you still crave?"
23. "Tell Chang what you lifted today. Groceries count."
24. "What does 'strong' mean to you at your age?"
25. "What's one thing your kids don't know you can still do?"

### 6.2 Save triggers
"Save this, do it tonight." Follow-alongs (F01/F05/F21) are designed to be **re-watched**. Carousels (F36). Recipes with quantities (F31). "Screenshot the numbers" test norms (F02).

### 6.3 Share-to-family triggers (the 35–55 gift buyer is a second audience)
- F33 format and the FAMILY keyword.
- Lines: "Send this to your mom. She'll say 'I'm fine.'" · "Send this to your dad who 'doesn't need help.'" · "Tag the sister who's doing the onion thing."
- Test videos framed for doing together: "Do the chair test with your parents this Sunday. Loser makes lunch."

### 6.4 Reply loop (the algorithm and community compounding engine)
- Every day, per page: pin 1 comment and reply as the character to 30–50 comments in the first 60 min (templates, human-approved for health topics). **1 reply video/day** from the best question (F09/F10/F26).
- Character replies use the voice card. Medical specifics get the deflection + a general answer. Crisis handling follows SAFETY §4.4.
- Monthly "Sun reads your stories" compilation (permissioned, anonymized).

### 6.5 Moderation
- Auto-hide: spam links, "is this real?" pile-ons get the transparency reply (FUNNEL global intent), and scam "DM me for crypto" comments.
- **Impersonator watch:** we're a viral AI brand, so clones will appear. Report weekly. The pinned "Hi, we're AI" post names our only official handles.

---

## 7. Series & retention devices
| Series | Page | Cadence | Device |
|---|---|---|---|
| **7-Day Strong** | @changyin | Days 1–7, 19:00 slot, then re-runs monthly with new variants | "DAY N/7" badge, fridge numbers, "type N if you did it" |
| **30-Day Balance** | @changyin (→ moves to @changyin.mobility on launch) | Days 8–37 | One minute/day, progressive (feet together → tandem → one-leg → head turns → eyes closed with the counter) |
| **Fiber Ladder** | @sunyoon.kitchen | Days 1–7 | +5 g/day, Sun's chart |
| **Sun Answers #N** | @sunyoon.kitchen / @sunyoon | Daily after day 7 | Numbered, from real comments |
| **Sunday Soup** | @sunyoon.kitchen | Weekly (Sunday) | Same intro sting, a new soup |
| **Frank's Comeback** | @changandsun | 3×/week | Frank's arc: showing up, regressions, jokes (no outcome claims) |
| **Loser Does Dishes** | @changandsun | Weekly | Couple challenge + the fridge leaderboard |
| **50th Anniversary Countdown** | @changandsun | Days 20–50, finale episode | Countdown badge; the finale is the tender "ten out of ten" |
| **Monthly Retest Day** | All | 1st of the month | "Retest your numbers" (mirrors the product's monthly Strength Age retest) |
| **Myth Monday** | Rotates | Weekly | "MYTH ✗" template (F04/F28) |

**Retention devices inside videos:** open loops ("The third one nobody does"), a callback to yesterday's numbers, a persistent world state (the fridge leaderboard, the hidden kettlebell), cliffhanger tags ("Tomorrow: the move that fixes the wobble. Hint: your toes."), and end-screen "Part 2 on the page" (only if part 2 exists).

---

## 8. Page architecture (multi-page, unique posts)

### 8.1 Pages
| Handle (proposed; check availability) | Lead | Audience | Job | Launch wave | Posts/day/platform |
|---|---|---|---|---|---|
| **@changyin** | Chang (+ Sun cameos) | 55–80 all, + adult kids | Flagship: tests, strength proof, myths, series | Day 1 | 7 (range 6–9) |
| **@sunyoon.kitchen** | Sun (+ Chang tasting) | Women 55–80 | Food, gut, protein, remedy myth-busting | Day 1 | 7 |
| **@changandsun** | Duo | Couples, women 55+, adult kids | Sitcom + relationships + family share | Day 1 | 7 |
| **@changyin.strength** | Chang | Men 60–80, ex-athletes, tradesmen | Deeper strength programming, form, power, grip | Day 15 | 6–7 |
| **@changyin.mobility** | Chang | Stiff, sore, sleepless; tai chi fans | Mobility, rehab ladders, breath, tai chi/qigong, sleep | Day 15 | 6–7 |
| **@sunyoon** | Sun | Women 55–80 | Blunt truths, relationships, grief, pro-living, women's strength | Day 22 | 6–7 |
| **@changyin.espanol** | Chang (natively written Spanish scripts, same designed voice via the multilingual model) + Frank | US Hispanic 55+ and LatAm | Strength + balance + kitchen in Spanish (Mode A pilot). Frank Delgado has an expanded role (a bilingual bridge). | Day 30 | 3 (Mode A pilot until the Spanish market launch, US month 4–5; EXPANSION.md §4) |
| *Archetype pages* | ARCHETYPES.md | Per market | New characters, new languages | Day 45+ (Spanish archetypes only after the Spanish market launch, EXPANSION.md §4) | 6 |

**Rollout (canonical):** day 1 @changyin, @sunyoon.kitchen, @changandsun · day 15 @changyin.strength, @changyin.mobility · day 22 @sunyoon · day 30 @changyin.espanol (Mode A Spanish pilot at 3/day). The Posts/day column is each page's **target cadence**; every new account reaches it through the warm-up ramp (PIPELINE.md §5.4, canonical): 1–2 posts/day in week 1, 3 in week 2, 5–6 in week 3, then 6–9 from week 4; `auto_publish` only after 14 clean days.

**AI wink on the Spanish page:** "Sí, hablo español. Soy IA. Tu abuela también quiere que hagas sentadillas." It turns the multilingual AI into an honest feature.

### 8.2 Uniqueness rules (hard, enforced by the pipeline)
1. **No reposts across pages.** Every page's post is a separately written and rendered master. The same master can go to IG/TT/YT/FB **for the same page**, with platform-native captions and CTA mechanics.
2. **Hook uniqueness:** a hook ID runs once per page. The same hook on a *different* page needs ≥21 days' gap, plus a different set, format, wardrobe and script. Embedding similarity to any post in the trailing 60 days across all pages must be <0.85 (the idea-miner checks this).
3. **Visual uniqueness:** a different set or wardrobe than any post on another page in the trailing 7 days on the same topic. Different first frame always.
4. **Audio uniqueness:** a fresh TTS render per master. Never reuse the voice file across pages. The music bed differs.
5. **Script uniqueness:** the same evidence ID can recur, but the example, move, joke and CTA line must differ.
6. **Topic spacing:** the same topic (e.g., one-leg balance) max 1×/day across the network, max 3×/week per page.
7. **No cross-page collab posts** (IG Collab) between our own pages. Platforms read that as network behavior.

### 8.3 Cross-promotion (allowed, natural)
- **Character cameos with a hand-off line:** Sun on @changyin: "Recipe's on my page." Chang on @sunyoon.kitchen: "The chair test is on mine."
- **Bio links** list sibling pages.
- **Series hand-offs:** "30-Day Balance continues on @changyin.mobility."
- **Pinned post #3** on each page lists the family of pages.
- **Stories:** reshare a sibling page's *new* Reel once a day with a one-line reason.
- **Cap:** ≤1 in 7 posts per page references another page.

### 8.4 Account hygiene (reach protection)
- IG "AI-generated profile" label ON (a 2026 requirement). TikTok AI toggle ON per post. YouTube altered-content toggle ON.
- Warm new accounts on the warm-up ramp (PIPELINE.md §5.4, canonical): 1–2 posts/day in week 1, 3 in week 2, 5–6 in week 3, then 6–9 from week 4; `auto_publish` only after 14 clean days. Up to 9/day only on pages past week 4 that clear the §10 kill thresholds.
- Separate device fingerprints and IPs per page is **not** our tactic. We run openly as one brand with multiple labeled pages. Use platform-sanctioned multi-account tools (Meta Business Suite, TikTok Business Center, YouTube Brand Accounts).

---

## 9. Posting schedule (6–9 posts/day/platform/page)
The audience is up early and is heavily US Eastern + Central. Times are the **audience's local time**. We schedule in ET for the US pages with a PT duplicate slot only for the 21:00 bed slot on FB (where time zone reach matters most). The Spanish page uses CT.

| Slot | ET | Purpose | Formats | Default keyword |
|---|---|---|---|---|
| 1 | 06:45 | AM routine | F20, F01, F02, F17 | BACK / STRONG |
| 2 | 08:30 | Test/challenge | F02, F16, F23 | TEST / BALANCE |
| 3 | 11:00 | Myth/numbers | F04, F28, F16, F13 | varies |
| 4 | 12:45 | Kitchen/lunch (SK) · adult-kid lunch-break share (CY/CS) | F31, F18, F06, F33 | SOUP / GUT / FAMILY |
| 5 | 16:00 | Story/couple | F08, F07, F35, F25 | BEGIN / varies |
| 6 | 19:00 | Series episode | F11 | per series |
| 7 | 21:00 | Before bed | F05, F21, F22 | SLEEP / BREATH |
| +8 (optional) | 14:00 | Reply video | F09, F10, F26 | varies |
| +9 (optional) | 17:30 | Carousel (IG) / text (TH/FB) | F36, F37 | varies |

**Network volume:** month 1 ramps (3 pages × 1–2/day in week 1, × 3 in week 2, × 5–6 in week 3) and reaches 3 pages × 7 = **21 unique masters/day** from week 4 (×4 platforms = 84 posts/day, plus carousels and Threads). Month 2, once the day-15/22 pages are past their own ramp = 6 English pages × 7 + @changyin.espanol × 3 = **about 45 masters/day**. At ~$0.20–0.60/reel (BRIEF) that's about $300–900/month in generation in month 2, excluding subscriptions.

---

## 10. KPIs, testing and kill/scale rules
| Metric | Target (initial, assumption, recalibrate day 14) | Kill (after 2 variants) | Scale |
|---|---|---|---|
| 3-second hold | ≥65% | <45% | ≥75%: remix the hook ×5 across formats and pages (respecting uniqueness) |
| Avg % watched (20–45 s) | ≥55% | <35% | — |
| Keyword comments / 1,000 views | ≥4 | <1 | ≥8: build a paid-ad variant (OFFER.md paid rules: no condition words) |
| Shares / 1,000 views | ≥6 | — | ≥12: family-share remix (F33) |
| Saves / 1,000 views | ≥8 (follow-alongs, recipes) | — | Carousel spin-off |
| DM opt-in rate (button tap / keyword comment) | 55–70% (FUNNEL) | <40%: fix the DM copy, not the video | — |

**Week-1 hook test protocol:** the 30 ★ hooks × 2 variants (different frame 1 or set) = 60 posts across the 3 launch pages during the week 1–2 ramp (hook tests take the ramp's limited slots first; the ready scripts fill the rest and roll forward). Rank on (3-s hold × keyword rate). The top 10 hooks feed the "REMIX" slots from week 2 and the paid-ad creative queue. The bottom 10 retire, and their category gets 5 fresh LLM hooks.

---

## 11. 30-day content calendar: first 3 pages (@changyin, @sunyoon.kitchen, @changandsun)
**How to read it:**
- **S##** = a ready script from SCRIPTS.md.
- **H###** = a hook from HOOKS.md. The LLM writes the script via CHARACTERS.md §12 with that hook's format and CTA.
- **Series** cells = the series episode from §7.
- **REMIX wkN winner** = re-cut the best hook of week N with a new set, format and script (never a repost).
- **REPLY** = the best comment-reply video (F09).
- **NEW Pxx/Fyy·KEY** = the library is used up for that slot, so the idea-miner generates a new hook for pillar Pxx in format Fyy with keyword KEY. The builder picks the pillar that's furthest below that page's share target (§3).

- **Cadence note:** this calendar is the **target cadence** (7 slots/page/day), reached from week 4. In weeks 1–3 the warm-up ramp (PIPELINE.md §5.4: 1–2 posts/day, then 3, then 5–6) fills only the earliest slots of each day in the order listed; unfilled library items roll forward.

The machine version is `data/content/calendar_30d.csv`. Regenerate it with `python3 tools/build_content.py` after editing hooks or scripts.

**Coverage:** the library fills about 78% of the 630 month-1 slots: 116 ready scripts (S01–S60 plus the launch-page expansion scripts and the 16 fixed founding-launch-week posts on days 1–7), 229 original hooks, and 146 series/remix/reply slots. About 22% are NEW briefs, mostly in weeks 3–4 on @changandsun and @sunyoon.kitchen. That's by design: by then, week 1–2 performance data should steer new hooks, rather than a pre-written library. (Expansion scripts S61–S134 written for @changyin.strength, @changyin.mobility and @sunyoon stay on those pages when they launch on days 15–22, and the H301–H390 blitz hooks are never scheduled as bare hooks because each is already a script. Month 1 reassigns original hooks tagged for pages that haven't launched yet: @changyin.strength and .mobility hooks run on @changyin; @sunyoon hooks with BEGIN/FAMILY go to @changandsun as duo adaptations; the rest go to @sunyoon.kitchen. The sibling pages launching on days 15–22 start from REMIXes of those winners plus NEW hooks, and never repost.)

<!-- CALENDAR:START -->
<!-- GENERATED by tools/build_content.py from data/content/: edit the sources, not this block -->
| Day | Theme | Page | 06:45 AM routine | 08:30 Test/Challenge | 11:00 Myth/Numbers | 12:45 Kitchen/Lunch | 16:00 Story/Couple | 19:00 Series | 21:00 Before bed |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Launch: the 3 tests | @changyin | **S136** (F39·BEGIN) | **S01** (F02·STRONG) | **S06** (F28·STRONG) | **S04** (F16·TEST) | **S135** (F38·JOIN) | **S19** (F11·STRONG) | **S10** (F21·BREATH) |
| 1 | Launch: the 3 tests | @sunyoon.kitchen | **S144** (F39·BEGIN) | **S33** (F06·GUT) | **S31** (F04·SOUP) | **S141** (F38·JOIN) | **S40** (F07·KNEES) | Fiber Ladder D1 | **S39** (F06·SOUP) |
| 1 | Launch: the 3 tests | @changandsun | **S146** (F39·JOIN) | **S147** (F11·STRONG) | **S51** (F08·STRONG) | **S52** (F34·BALANCE) | **S145** (F38·JOIN) | Frank's Comeback ep1 | **S53** (F33·FAMILY) |
| 2 | Legs first | @changyin | **S02** (F02·BALANCE) | **S03** (F02·TEST) | **S07** (F28·STRONG) | **S139** (F33·FAMILY) | **S05** (F16·STRONG) | 7-Day Strong D2 | **S11** (F05·SLEEP) |
| 2 | Legs first | @sunyoon.kitchen | **S32** (F18·SOUP) | **S35** (F06·GUT) | **S34** (F04·GUT) | **S36** (F31·GUT) | **S41** (F07·BEGIN) | Fiber Ladder D2 | **S46** (F35·BEGIN) |
| 2 | Legs first | @changandsun | **S54** (F08·BACK) | **S55** (F18·SOUP) | **S56** (F34·STRONG) | **S57** (F08·SLEEP) | **S58** (F35·BREATH) | Frank's Comeback ep2 | **S59** (F08·TEST) |
| 3 | Balance week begins | @changyin | **S15** (F02·KNEES) | **S16** (F02·STRONG) | **S08** (F28·BALANCE) | **S18** (F14·STRONG) | **S140** (F38·JOIN) | 7-Day Strong D3 | **S12** (F05·SLEEP) |
| 3 | Balance week begins | @sunyoon.kitchen | **S37** (F31·SOUP) | **S38** (F06·GUT) | **S43** (F28·STRONG) | **S45** (F06·GUT) | **S42** (F07·STRONG) | Fiber Ladder D3 | **S47** (F07·BEGIN) |
| 3 | Balance week begins | @changandsun | **S125** (F34·BALANCE) | **S126** (F08·BACK) | **S128** (F34·TEST) | **S148** (F33·FAMILY) | **S129** (F28·BEGIN) | Loser does dishes | **S130** (F25·KNEES) |
| 4 | Myth day | @changyin | **S17** (F23·STRONG) | **S61** (F02·TEST) | **S09** (F22·BALANCE) | **S20** (F03·BACK) | **S21** (F13·STRONG) | 7-Day Strong D4 | REPLY video (F09) |
| 4 | Myth day | @sunyoon.kitchen | **S48** (F18·SOUP) | **S44** (F18·SOUP) | **S99** (F04·SOUP) | **S102** (F06·GUT) | **S143** (F07·JOIN) | Fiber Ladder D4 | REPLY video (F09) |
| 4 | Myth day | @changandsun | **S131** (F08·BACK) | **S132** (F27·STRONG) | **S133** (F29·BEGIN) | **S127** (F31·GUT) | **S134** (F08·STRONG) | Frank's Comeback ep4 | REPLY video (F09) |
| 5 | Kitchen protein | @changyin | **S22** (F20·BACK) | **S64** (F32·BALANCE) | **S13** (F03·BACK) | **S25** (F14·KNEES) | **S27** (F15·STRONG) | 7-Day Strong D5 | **S24** (F32·BALANCE) |
| 5 | Kitchen protein | @sunyoon.kitchen | **S101** (F04·SOUP) | **S104** (F31·GUT) | **S100** (F04·SOUP) | **S142** (F33·FAMILY) | **S49** (F31·SOUP) | Fiber Ladder D5 | **S50** (F07·BALANCE) |
| 5 | Kitchen protein | @changandsun | H028 (F08·BEGIN) | H047 (F08·BALANCE) | H090 (F07·BEGIN) | H216 (F08·STRONG) | **S149** (F38·JOIN) | Frank's Comeback ep5 | H159 (F07·BEGIN) |
| 6 | Couple challenge | @changyin | **S62** (F32·STRONG) | **S67** (F02·TEST) | **S14** (F03·BACK) | **S28** (F13·STRONG) | **S138** (F38·JOIN) | 7-Day Strong D6 | **S30** (F22·SLEEP) |
| 6 | Couple challenge | @sunyoon.kitchen | **S108** (F19·GUT) | **S106** (F18·SOUP) | **S103** (F04·GUT) | **S110** (F06·SOUP) | **S111** (F18·SOUP) | Fiber Ladder D6 | H160 (F06·GUT) |
| 6 | Couple challenge | @changandsun | H217 (F08·STRONG) | H056 (F34·STRONG) | **S150** (F10·JOIN) | H218 (F35·BEGIN) | H122 (F07·BEGIN) | Frank's Comeback ep6 | H163 (F08·SLEEP) |
| 7 | Rest & breath | @changyin | **S63** (F02·BALANCE) | **S70** (F13·STRONG) | **S23** (F28·STRONG) | **S29** (F15·BALANCE) | **S137** (F11·BALANCE) | 7-Day Strong D7 | H154 (F05·BACK) |
| 7 | Rest & breath | @sunyoon.kitchen | **S112** (F04·GUT) | **S113** (F18·SOUP) | **S105** (F04·GUT) | **S114** (F06·GUT) | H124 (F07·STRONG) | Fiber Ladder D7 | H174 (F06·GUT) |
| 7 | Rest & breath | @changandsun | H219 (F34·BALANCE) | H220 (F28·STRONG) | H221 (F08·STRONG) | H222 (F35·BEGIN) | H242 (F07·FAMILY) | Frank's Comeback ep7 | H170 (F07·BEGIN) |
| 8 | Grip & hands | @changyin | **S66** (F03·BACK) | **S71** (F01·STRONG) | REMIX wk1 winner | **S68** (F17·STRONG) | **S69** (F33·FAMILY) | 30-Day Balance D1 | REPLY video (F09) |
| 8 | Grip & hands | @sunyoon.kitchen | H181 (F31·SOUP) | H182 (F18·SOUP) | REMIX wk1 winner | H186 (F18·SOUP) | H129 (F07·SOUP) | Sun Answers #1 | REPLY video (F09) |
| 8 | Grip & hands | @changandsun | H223 (F34·STRONG) | H224 (F29·GUT) | REMIX wk1 winner | H225 (F08·BEGIN) | H125 (F33·FAMILY) | Frank's Comeback ep8 | REPLY video (F09) |
| 9 | Floor skills | @changyin | **S72** (F03·BACK) | **S75** (F02·TEST) | **S26** (F28·KNEES) | **S73** (F15·BALANCE) | H001 (F27·STRONG) | 30-Day Balance D2 | H155 (F21·SLEEP) |
| 9 | Floor skills | @sunyoon.kitchen | H005 (F06·GUT) | H050 (F18·SOUP) | **S107** (F04·BACK) | H187 (F31·SOUP) | H134 (F07·STRONG) | Sun Answers #2 | H244 (F07·STRONG) |
| 9 | Floor skills | @changandsun | H226 (F25·KNEES) | H227 (F35·BEGIN) | H228 (F08·STRONG) | H230 (F08·STRONG) | H135 (F34·STRONG) | Frank's Comeback ep9 | H177 (F08·BACK) |
| 10 | Tai chi day | @changyin | H121 (F27·STRONG) | H271 (F16·TEST) | REMIX wk1 winner | H092 (F02·STRONG) | H004 (F02·BALANCE) | 30-Day Balance D3 | H156 (F05·KNEES) |
| 10 | Tai chi day | @sunyoon.kitchen | H010 (F31·SOUP) | H060 (F11·GUT) | REMIX wk1 winner | H189 (F12·SOUP) | H138 (F31·SOUP) | Sun Answers #3 | H246 (F18·SOUP) |
| 10 | Tai chi day | @changandsun | H231 (F08·BEGIN) | H233 (F08·BEGIN) | REMIX wk1 winner | H234 (F18·SOUP) | H144 (F07·BEGIN) | Loser does dishes | H180 (F07·BEGIN) |
| 11 | Gut week begins | @changyin | H006 (F21·BREATH) | H272 (F16·BALANCE) | **S65** (F28·STRONG) | H007 (F13·KNEES) | H008 (F15·BACK) | 30-Day Balance D4 | H157 (F22·SLEEP) |
| 11 | Gut week begins | @sunyoon.kitchen | H017 (F06·GUT) | H191 (F31·SOUP) | **S109** (F04·SOUP) | H192 (F06·SOUP) | H143 (F18·SOUP) | Sun Answers #4 | H249 (F07·STRONG) |
| 11 | Gut week begins | @changandsun | H235 (F27·BEGIN) | H236 (F28·STRONG) | H238 (F35·BEGIN) | H240 (F35·BEGIN) | H147 (F07·BEGIN) | Frank's Comeback ep11 | NEW P03/F15·BALANCE |
| 12 | Knees & stairs | @changyin | H009 (F05·SLEEP) | H273 (F16·TEST) | REMIX wk1 winner | H012 (F17·STRONG) | H013 (F13·STRONG) | 30-Day Balance D5 | REPLY video (F09) |
| 12 | Knees & stairs | @sunyoon.kitchen | H020 (F07·STRONG) | H193 (F31·SOUP) | REMIX wk1 winner | H194 (F18·SOUP) | H251 (F07·STRONG) | Sun Answers #5 | REPLY video (F09) |
| 12 | Knees & stairs | @changandsun | NEW P03/F15·BALANCE | NEW P01/F02·TEST | REMIX wk1 winner | NEW P03/F15·BALANCE | H150 (F29·BALANCE) | Frank's Comeback ep12 | REPLY video (F09) |
| 13 | Sun answers comments | @changyin | H015 (F22·BALANCE) | H034 (F02·STRONG) | H064 (F28·BACK) | H016 (F15·STRONG) | H018 (F02·TEST) | 30-Day Balance D6 | H161 (F05·SLEEP) |
| 13 | Sun answers comments | @sunyoon.kitchen | H022 (F06·GUT) | H195 (F31·GUT) | H067 (F04·GUT) | H196 (F31·SOUP) | H252 (F07·GUT) | Sun Answers #6 | H254 (F07·STRONG) |
| 13 | Sun answers comments | @changandsun | NEW P16/F07·BEGIN | NEW P07/F21·BREATH | H294 (F07·BEGIN) | NEW P01/F02·TEST | H247 (F07·BEGIN) | Frank's Comeback ep13 | NEW P13/F18·SOUP |
| 14 | Sunday soup | @changyin | H019 (F16·STRONG) | H035 (F02·STRONG) | REMIX wk1 winner | H023 (F02·BALANCE) | H024 (F13·BREATH) | 30-Day Balance D7 | H162 (F21·BREATH) |
| 14 | Sunday soup | @sunyoon.kitchen | H026 (F31·GUT) | H197 (F06·GUT) | REMIX wk1 winner | H198 (F31·SOUP) | H255 (F07·STRONG) | Sunday Soup | H256 (F08·BACK) |
| 14 | Sunday soup | @changandsun | NEW P15/F28·BEGIN | NEW P19/F11·STRONG | REMIX wk1 winner | NEW P03/F15·BALANCE | H248 (F35·BEGIN) | Frank's Comeback ep14 | NEW P18/F10·BEGIN |
| 15 | Back day | @changyin | H025 (F13·STRONG) | H036 (F02·BALANCE) | H069 (F04·BALANCE) | H027 (F14·BACK) | H029 (F27·STRONG) | 30-Day Balance D8 | H164 (F05·BACK) |
| 15 | Back day | @sunyoon.kitchen | H199 (F31·GUT) | H200 (F11·GUT) | H070 (F04·BACK) | H201 (F28·GUT) | H258 (F18·SOUP) | Sun Answers #8 | H259 (F07·STRONG) |
| 15 | Back day | @changandsun | H101 (F07·BEGIN) | H113 (F33·FAMILY) | H250 (F35·BEGIN) | H253 (F07·BEGIN) | H257 (F35·BEGIN) | Frank's Comeback ep15 | H260 (F07·BEGIN) |
| 16 | Numbers day | @changyin | H030 (F13·STRONG) | H037 (F02·TEST) | REMIX wk2 winner | H094 (F16·STRONG) | H097 (F17·STRONG) | 30-Day Balance D9 | REPLY video (F09) |
| 16 | Numbers day | @sunyoon.kitchen | H203 (F06·SOUP) | H204 (F06·SOUP) | REMIX wk2 winner | H205 (F12·SOUP) | H261 (F07·GUT) | Sun Answers #9 | REPLY video (F09) |
| 16 | Numbers day | @changandsun | H264 (F35·BEGIN) | H265 (F07·BEGIN) | REMIX wk2 winner | H267 (F07·BEGIN) | H269 (F07·BEGIN) | Frank's Comeback ep16 | REPLY video (F09) |
| 17 | Women who lift | @changyin | H038 (F02·BACK) | H041 (F32·BALANCE) | H073 (F21·BREATH) | H098 (F15·BALANCE) | H099 (F02·TEST) | 30-Day Balance D10 | H165 (F05·SLEEP) |
| 17 | Women who lift | @sunyoon.kitchen | H206 (F18·SOUP) | H208 (F28·SOUP) | H071 (F28·SOUP) | H209 (F31·GUT) | H262 (F07·STRONG) | Sun Answers #10 | H266 (F07·STRONG) |
| 17 | Women who lift | @changandsun | NEW P03/F15·BALANCE | NEW P01/F02·TEST | NEW P13/F18·SOUP | NEW P19/F11·STRONG | NEW P07/F21·BREATH | Loser does dishes | NEW P03/F15·BALANCE |
| 18 | Walk after dinner | @changyin | H042 (F02·BACK) | H043 (F02·TEST) | REMIX wk2 winner | H100 (F14·BACK) | H102 (F15·KNEES) | 30-Day Balance D11 | H168 (F15·BALANCE) |
| 18 | Walk after dinner | @sunyoon.kitchen | H210 (F31·SOUP) | H279 (F18·GUT) | REMIX wk2 winner | H076 (F06·GUT) | H270 (F07·STRONG) | Sun Answers #11 | H080 (F04·GUT) |
| 18 | Walk after dinner | @changandsun | NEW P18/F10·BEGIN | NEW P01/F02·TEST | REMIX wk2 winner | NEW P13/F18·SOUP | NEW P15/F28·BEGIN | Frank's Comeback ep18 | NEW P19/F11·STRONG |
| 19 | Sleep week | @changyin | H046 (F02·BALANCE) | H048 (F02·BACK) | H074 (F28·STRONG) | H103 (F05·SLEEP) | H105 (F16·TEST) | 30-Day Balance D12 | H169 (F05·BACK) |
| 19 | Sleep week | @sunyoon.kitchen | H087 (F31·GUT) | H286 (F06·GUT) | H287 (F06·GUT) | H104 (F18·SOUP) | H111 (F06·GUT) | Sun Answers #12 | H117 (F18·SOUP) |
| 19 | Sleep week | @changandsun | NEW P07/F21·BREATH | NEW P03/F15·BALANCE | NEW P18/F10·BEGIN | NEW P01/F02·TEST | NEW P13/F18·SOUP | Frank's Comeback ep19 | NEW P15/F28·BEGIN |
| 20 | Family share day | @changyin | H049 (F05·SLEEP) | H051 (F17·STRONG) | REMIX wk2 winner | H106 (F15·BACK) | H107 (F16·BALANCE) | 30-Day Balance D13 | REPLY video (F09) |
| 20 | Family share day | @sunyoon.kitchen | H291 (F06·GUT) | H293 (F18·SOUP) | REMIX wk2 winner | H295 (F28·GUT) | NEW P11/F31·SOUP | Sun Answers #13 | REPLY video (F09) |
| 20 | Family share day | @changandsun | NEW P19/F11·STRONG | NEW P07/F21·BREATH | REMIX wk2 winner | NEW P03/F15·BALANCE | NEW P18/F10·BEGIN | 50th countdown | REPLY video (F09) |
| 21 | Fermentation day | @changyin | H052 (F02·STRONG) | H053 (F21·BREATH) | H077 (F03·KNEES) | H108 (F15·STRONG) | H112 (F16·STRONG) | 30-Day Balance D14 | H171 (F21·BREATH) |
| 21 | Fermentation day | @sunyoon.kitchen | NEW P11/F31·SOUP | NEW P11/F31·SOUP | NEW P11/F31·SOUP | NEW P11/F31·SOUP | NEW P11/F31·SOUP | Sunday Soup | NEW P11/F31·SOUP |
| 21 | Fermentation day | @changandsun | NEW P01/F02·TEST | NEW P13/F18·SOUP | NEW P15/F28·BEGIN | NEW P19/F11·STRONG | NEW P03/F15·BALANCE | 50th countdown | NEW P07/F21·BREATH |
| 22 | Strength Age retest prompt | @changyin | H054 (F11·BALANCE) | H055 (F14·STRONG) | REMIX wk3 winner | H114 (F16·TEST) | H115 (F17·STRONG) | 30-Day Balance D15 | H172 (F05·SLEEP) |
| 22 | Strength Age retest prompt | @sunyoon.kitchen | NEW P12/F06·SOUP | NEW P11/F31·SOUP | REMIX wk3 winner | NEW P12/F06·SOUP | NEW P11/F31·SOUP | Sun Answers #15 | NEW P11/F31·SOUP |
| 22 | Strength Age retest prompt | @changandsun | NEW P09/F05·SLEEP | NEW P01/F02·TEST | REMIX wk3 winner | NEW P13/F18·SOUP | NEW P15/F28·BEGIN | 50th countdown | NEW P19/F11·STRONG |
| 23 | Myth day II | @changyin | H057 (F02·BALANCE) | H058 (F02·STRONG) | H081 (F28·STRONG) | H116 (F21·BREATH) | H118 (F14·BACK) | 30-Day Balance D16 | H173 (F17·STRONG) |
| 23 | Myth day II | @sunyoon.kitchen | NEW P12/F06·SOUP | NEW P11/F31·SOUP | NEW P12/F06·SOUP | NEW P10/F06·GUT | NEW P11/F31·SOUP | Sun Answers #16 | NEW P10/F06·GUT |
| 23 | Myth day II | @changandsun | NEW P03/F15·BALANCE | NEW P18/F10·BEGIN | NEW P07/F21·BREATH | NEW P03/F15·BALANCE | NEW P18/F10·BEGIN | 50th countdown | NEW P01/F02·TEST |
| 24 | Qigong evening | @changyin | H059 (F02·BALANCE) | H274 (F16·STRONG) | REMIX wk3 winner | H119 (F27·STRONG) | H120 (F05·SLEEP) | 30-Day Balance D17 | REPLY video (F09) |
| 24 | Qigong evening | @sunyoon.kitchen | NEW P12/F06·SOUP | NEW P11/F31·SOUP | REMIX wk3 winner | NEW P10/F06·GUT | NEW P11/F31·SOUP | Sun Answers #17 | REPLY video (F09) |
| 24 | Qigong evening | @changandsun | NEW P13/F18·SOUP | NEW P15/F28·BEGIN | REMIX wk3 winner | NEW P16/F07·BEGIN | NEW P19/F11·STRONG | 50th countdown | REPLY video (F09) |
| 25 | Steady-feet home | @changyin | H123 (F27·STRONG) | H275 (F16·STRONG) | H082 (F28·BALANCE) | H126 (F27·STRONG) | H128 (F33·FAMILY) | 30-Day Balance D18 | H175 (F05·BALANCE) |
| 25 | Steady-feet home | @sunyoon.kitchen | NEW P12/F06·SOUP | NEW P11/F31·SOUP | NEW P10/F06·GUT | NEW P12/F06·SOUP | NEW P11/F31·SOUP | Sun Answers #18 | NEW P17/F08·BEGIN |
| 25 | Steady-feet home | @changandsun | NEW P09/F05·SLEEP | NEW P16/F07·BEGIN | NEW P07/F21·BREATH | NEW P03/F15·BALANCE | NEW P01/F02·TEST | 50th countdown | NEW P13/F18·SOUP |
| 26 | Cooking for one | @changyin | H130 (F15·BALANCE) | H276 (F16·BALANCE) | REMIX wk3 winner | H131 (F15·STRONG) | H132 (F14·KNEES) | 30-Day Balance D19 | H176 (F11·STRONG) |
| 26 | Cooking for one | @sunyoon.kitchen | NEW P10/F06·GUT | NEW P13/F18·SOUP | REMIX wk3 winner | NEW P11/F31·SOUP | NEW P12/F06·SOUP | Sun Answers #19 | NEW P11/F31·SOUP |
| 26 | Cooking for one | @changandsun | NEW P16/F07·BEGIN | NEW P15/F28·BEGIN | REMIX wk3 winner | NEW P19/F11·STRONG | NEW P03/F15·BALANCE | 50th countdown | NEW P16/F07·BEGIN |
| 27 | Anniversary countdown | @changyin | H133 (F17·BEGIN) | H277 (F16·STRONG) | H083 (F28·STRONG) | H136 (F27·STRONG) | H137 (F22·BALANCE) | 30-Day Balance D20 | H178 (F21·BREATH) |
| 27 | Anniversary countdown | @sunyoon.kitchen | NEW P10/F06·GUT | NEW P13/F18·SOUP | NEW P12/F06·SOUP | NEW P11/F31·SOUP | NEW P10/F06·GUT | Sun Answers #20 | NEW P13/F18·SOUP |
| 27 | Anniversary countdown | @changandsun | NEW P18/F10·BEGIN | NEW P07/F21·BREATH | NEW P09/F05·SLEEP | NEW P01/F02·TEST | **S60** (F27·BEGIN) | 50th countdown | NEW P16/F07·BEGIN |
| 28 | Power (fast feet) | @changyin | H140 (F14·STRONG) | H278 (F02·TEST) | REMIX wk3 winner | H141 (F05·SLEEP) | H142 (F15·STRONG) | 30-Day Balance D21 | REPLY video (F09) |
| 28 | Power (fast feet) | @sunyoon.kitchen | NEW P11/F31·SOUP | NEW P12/F06·SOUP | REMIX wk3 winner | NEW P17/F08·BEGIN | NEW P10/F06·GUT | Sunday Soup | REPLY video (F09) |
| 28 | Power (fast feet) | @changandsun | NEW P13/F18·SOUP | NEW P15/F28·BEGIN | REMIX wk3 winner | NEW P19/F11·STRONG | NEW P03/F15·BALANCE | 50th countdown | REPLY video (F09) |
| 29 | Recap: your numbers | @changyin | H145 (F15·BACK) | H281 (F21·BREATH) | H084 (F24·STRONG) | H146 (F14·BACK) | H148 (F11·STRONG) | 30-Day Balance D22 | H179 (F14·SLEEP) |
| 29 | Recap: your numbers | @sunyoon.kitchen | NEW P11/F31·SOUP | NEW P13/F18·SOUP | NEW P12/F06·SOUP | NEW P11/F31·SOUP | NEW P10/F06·GUT | Sun Answers #22 | NEW P13/F18·SOUP |
| 29 | Recap: your numbers | @changandsun | NEW P16/F07·BEGIN | NEW P07/F21·BREATH | NEW P01/F02·TEST | NEW P16/F07·BEGIN | NEW P13/F18·SOUP | 50th countdown | NEW P15/F28·BEGIN |
| 30 | Day 30: retest + celebrate | @changyin | H149 (F27·BEGIN) | H282 (F16·STRONG) | REMIX wk4 winner | H086 (F28·BREATH) | H088 (F28·KNEES) | 30-Day Balance D23 | H089 (F16·TEST) |
| 30 | Day 30: retest + celebrate | @sunyoon.kitchen | NEW P11/F31·SOUP | NEW P15/F28·BEGIN | REMIX wk4 winner | NEW P12/F06·SOUP | NEW P10/F06·GUT | Sun Answers #23 | NEW P13/F18·SOUP |
| 30 | Day 30: retest + celebrate | @changandsun | NEW P19/F11·STRONG | NEW P03/F15·BALANCE | REMIX wk4 winner | NEW P18/F10·BEGIN | NEW P16/F07·BEGIN | 50th countdown | NEW P09/F05·SLEEP |
<!-- CALENDAR:END -->

### Day themes (the whole network aligns on a theme each day so cross-promotion feels natural)
Day 1 the 3 tests · 2 legs first · 3 balance week · 4 myth day · 5 kitchen protein · 6 couple challenge · 7 rest & breath · 8 grip · 9 floor skills · 10 tai chi · 11 gut week · 12 knees & stairs · 13 Sun answers · 14 Sunday soup · 15 back day (sibling pages launch) · 16 numbers day · 17 women who lift · 18 walk after dinner · 19 sleep week · 20 family share day (FAMILY push) · 21 fermentation · 22 Strength Age retest prompt (@sunyoon launches) · 23 myth day II · 24 qigong evening · 25 steady-feet home · 26 cooking for one · 27 anniversary countdown (S60) · 28 power/fast feet · 29 recap: your numbers · 30 retest + celebrate (@changyin.espanol launches as the Mode A Spanish pilot at 3/day).

---

## 12. Spanish page notes (@changyin.espanol)
- Scripts are **written natively in Spanish** (neutral Latin American, with US-Hispanic vocabulary), not translated line by line. The localization adapter (prompts/08) gets the CHARACTERS.md voice card plus these rules: *usted* by default for 60+ (warmth plus respect); Frank speaks Mexican-American Spanish naturally; food crossovers (Sun learns caldo de pollo from Frank; Chang makes "sopa de fideos" his way).
- Evidence lines are the same (numbers identical). The citation stays in English in the caption ("Estudio: Lancet 2015").
- The disclosure footer is in ES (SAFETY §7). The corner tag reads `Personaje IA`.
- Keywords: FUERTE, EQUILIBRIO, ESPALDA, RODILLAS, SUEÑO, RESPIRA, SOPA, EMPEZAR, PRUEBA, FAMILIA.
- Cadence: Mode A pilot at 3 posts/day from rollout day 30 (organic only). Paid media, localized pricing, checkout and the Spanish membership (*Años Fuertes*) start at the full Spanish market launch in US month 4–5 (EXPANSION.md §4).
