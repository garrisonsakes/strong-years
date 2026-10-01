# ADS.md: Meta Paid Acquisition for Strong Years

Brand: **Strong Years** (OFFER.md). "Daily Practice" is the daily 8–12 minute session inside it. Prices and unit economics match OFFER.md and ECONOMICS.md; character facts match CHARACTERS.md (Chang Yin, 74, retired welder, hwagyo from Incheon's Chinatown; Sun Yoon, 76, Korean, from Incheon; in California since 1983; never "Master").

**Reviewer gate:** no reviewer is signed yet. Every review claim below is written as `[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: claim] FALLBACK: "line with no review claim"`. Ship the FALLBACK until a licensed reviewer has signed (and, if named or pictured, consented in writing). Concepts 6 and 14 depend on a real reviewer and have their own fallback versions.

Scope: Facebook + Instagram (Meta) paid acquisition for the US. Destinations and offers are defined in FUNNEL.md: Strength Age quiz (`/q/a`), Gut & Energy Check (`/q/b`), $1 trial page (`/start`), $7 Reset with 7 days of membership included (`/r7`), $17 Strong Kitchen with 7 days included (`/kitchen`), Gift (`/gift`: 3 months $49 / 12 months $119, no auto-renew).

Placeholders: `{{PRICE}}` (blitz: $25 for T25 and F25, $30 for F30; $20 only in the post-blitz `OFFER_MODE=standard` baseline), `{{DOMAIN}}`, `[PT NAME]`, `[RD NAME]`.

**Blitz mode (the launch default).** This file describes the **baseline** paid funnel ($1 trial, $7/$17 front ends). During the blitz, ads run from ADS_SCRIPTS.md into three sticky cells from L1 (F25 charge-today $25, F30 charge-today $30, T25 $1 for 7 days then $25; 50% founding / 50% trial; FUNNEL.md §0.2.1). Ad copy never states a price or offer that differs from the visitor's cell: price-bearing ads either state no price ("see the terms on the page") or run per cell with cell-matched copy. The winner is chosen at the BLITZ.md §11 day-10 and day-40 gates. Terms: 14-day money-back guarantee on the membership charge (one per person), founding price locked while subscribed (pauses included; never "for life"), cap 5,000 or `{{FOUNDING_CLOSE_DATE}}` whichever comes first, public counts per the `{{COUNT_LINE}}` rule, standard price after the cap configurable (default $35, client decision). The $1 trial lines here apply to cell T25, which is live from L1. Optimize on `Purchase` with the value set to each cell's expected contribution, so Meta doesn't favour one cell because its first charge is larger. Account: an existing ad account only with purchase history and no restricted-health ad history (K9SUPPS likeliest), otherwise a fresh Strong Years account; never an FA account (BLITZ_OPS.md §6.1).

---

## 1. The rules every ad follows (read before writing a single ad)

1. **AI disclosure in-creative, in the first 3 seconds.** A small but full-contrast tag in the top-left of every video and image: "AI character" (Rice text on an Ink box, never faded). Primary text includes "Chang Yin is an AI character" or "Sun Yoon is an AI character" in the first 2 lines. Upload source files with their C2PA/IPTC metadata intact so Meta's "AI info" label can apply; we want it applied, not avoided.
2. **No personal-attribute assertions.** Meta's policy bans ads that assert or imply the viewer's age, health, medical condition, disability, weight or other personal attributes. So: no "Are you over 60?", "your knee pain", "your arthritis", "if you've fallen", "you're getting weaker". Talk about the product, the test, the characters, or people in general: "Strength training for people over 60", "A standard fitness test used in senior fitness research", "Stairs are a leg-strength test". Never imply a CDC (or any agency) endorsement or program membership, and never use fall-risk or screening language in ad copy.
3. **No before/after transformation imagery.** Meta restricts before-and-after images for health and appearance. We never show bodies "before" and "after". What we can show: a real test being performed live, and (later) real members' consented, verified retest numbers stated as text, with a typicality statement.
4. **No disease claims, no "instantly", no fear bait.** No "reverse", "cure", "heal", "fix your arthritis", "lower blood pressure", "prevent falls" (say "train your balance"). No images of people falling, ambulances, hospital beds.
5. **No fake testimonials, no actors posing as members.** UGC-style ads are either the AI characters (labelled), [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: the real licensed humans (named),] FALLBACK: "real team members introduced as humans without credential claims," or real members (verified, consented, compensated with disclosure). Dramatizations with paid actors carry "Dramatization. Paid actor." on screen.
6. **Pricing clarity** anywhere price appears: "7 days for $1, then {{PRICE}}/month. Cancel online anytime." Meta's subscription-services policy expects the landing page to state the recurring terms clearly; ours does. Ads may say "we email you before every renewal" (true: FUNNEL.md canonical policies) but never "text CANCEL" unless SMS is live, and never "founding price for life".
7. **Character rules (CHARACTERS.md):** Chang is a retired welder who trains, never "Master", monk, doctor or therapist; the backstory is fiction and is never used as evidence of a health outcome.
8. **Design rules carry into ads:** no gray text, high contrast captions (Rice text on an Ink bar, or Ink on Paper), no slash decorations, no monospace index labels. Captions large enough to read on a phone held at arm's length: 60–72px on a 1080×1920 frame, max 2 lines.
9. **Product-led:** at least one shot of the actual product (the session screen with the level switch, the Strength Age card, Sun Yoon's recipe card, the printable chart) in every video ad.

---

## 2. Audience definitions

| Code | Audience | Meta setup | What they buy | Primary destination |
|---|---|---|---|---|
| W | Women 55–70 | Age 55–65+, women, US, Advantage+ audience with age as a suggestion (or hard min age 50 in testing) | $1 trial; $17 Kitchen; $7 Reset | `/q/a`, `/q/b` |
| M | Men 60–75 | Age 58–65+, men, US | $1 trial; $7 Reset; kit | `/q/a`, `/r7` |
| AC | Adult children 35–55 buying for parents | Age 35–55, all genders (skews women ~65%), US, broad; creative does the targeting | Gift 3 months $49 / 12 months $119 (prepaid, no auto-renew); $1 trial for themselves | `/gift`, `/q/a` (helper mode) |
| CG | Caregivers (family caregivers of an older adult) | Age 40–70, broad, US; no health-condition interest targeting (removed by Meta and not appropriate) | Gift; $1 trial (Rebuild track, chair-based) | `/gift`, `/start?trk=rebuild` |

Meta caps age targeting at "65+", so men 60–75 and women 55–70 are reached with a 65+ upper bound; the creative (character age, context) keeps delivery relevant. Do not rely on detailed interest targeting; Advantage+ audience and broad perform better at scale and avoid sensitive-interest issues.

---

## 3. 25 ad concepts

Format key: **UGC** = character talking to camera, phone-camera framing; **FA** = follow-along session clip; **QZ** = quiz ad; **ST** = live strength/balance test demonstration; **HX** = real human expert; **SY** = Sun Yoon kitchen; **ST-IMG** = static/carousel; **RM** = real member (only after verified reviews exist).

All videos: 9:16, 20–45 seconds unless noted, burned-in captions, "AI character" tag first 3 seconds, final card: product screen + CTA + "7 days for $1, then {{PRICE}}/mo" or "Free 3-minute test".

---

### Women 55–70 (W)

**Concept 1: "The 30-Second Chair Test"** (ST, UGC)
- **Angle:** Curiosity + self-measurement. A free test people can do right now.
- **Hook (0–3s):** Chang Yin sits, arms crossed, looks at camera: "Thirty seconds. How many times can you stand up from this chair?" On screen: "A standard senior fitness test."
- **Visual:** Garage gym, sturdy chair against a wall, big 30-second timer inset. He performs it at a steady pace, counts aloud. Cut to the Strength Age card on the kitchen table: "Typical for women 65–69: 11–16." End card: quiz screen.
- **Primary text:** "Chang Yin (an AI character) does the 30-second chair stand, a standard fitness test used in senior fitness research. Try it: sturdy chair against a wall, arms crossed, stand all the way up and sit all the way down for 30 seconds. Then see how your number compares with typical results by age and get a free 7-day plan. 3 minutes. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults.""
- **Headline:** What's your Strength Age? Free test
- **CTA:** Learn more → `/q/a`
- **Audience:** W (duplicate for M with men's norms on screen)

**Concept 2: "The Armrest Sign"** (UGC + FA)
- **Angle:** Recognizable everyday moment → simple solution.
- **Hook:** Close-up of hands pressing on chair armrests to stand. VO (Chang Yin): "Using the armrests to stand up is usually the first place leg strength shows up."
- **Visual:** He demonstrates three moves: slow sit-to-stand to a higher seat, counter squat, calf raises. Track switch shown: Rebuild / Steady / Strong / Iron.
- **Primary text:** "Standing up from a chair is a leg-strength test we all take every day. Chang Yin (an AI character) shows three moves that train exactly those muscles, with a seated version of each. It's day 1 of your Daily Practice in Strong Years: 8 minutes, levelled to you. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Try 7 days for $1, then {{PRICE}}/month. Cancel online anytime."
- **Headline:** 8 minutes. One chair. Stronger legs.
- **CTA:** Sign up → `/start`
- **Audience:** W

**Concept 3: "Toast Is Not Breakfast"** (SY, UGC)
- **Angle:** Blunt humor + protein education; Sun Yoon's personality is the hook.
- **Hook:** Sun Yoon holds up a slice of toast: "This is not breakfast. This is a plate."
- **Visual:** She makes silken tofu with soy, sesame and scallion in 3 minutes; on-screen "about 25g protein" (verified by RD calculation). Cut to Chang Yin finishing a leg session: "She's right." End card: Gut & Energy Check.
- **Primary text:** "Sun Yoon (an AI character) has opinions about breakfast. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Recipes checked by a registered dietitian.] FALLBACK: "Recipes built on published nutrition guidance for older adults." Muscles need protein at every meal, about 25–30 grams, and breakfast is where most of us come up short. Take her free 2-minute Gut & Energy Check and get a 7-day kitchen plan with three recipes to start tonight."
- **Headline:** Why am I tired after I eat? Free check
- **CTA:** Learn more → `/q/b`
- **Audience:** W (strongest candidate for the Kitchen-first test cell)

**Concept 4: "The 10-Second Counter Test"** (ST)
- **Angle:** Balance, framed as a test not a fear.
- **Hook:** Feet close-up at the kitchen counter, heel-to-toe. On screen: "Can you hold this for 10 seconds?"
- **Visual:** Chang Yin, one hand hovering over the counter, holds tandem stance, 10-second timer. Then the four balance stages as four quick photos. End: Steady Feet session screen.
- **Primary text:** "Heel to toe, one hand hovering over the kitchen counter, 10 seconds. It's one of four standard balance positions used in senior fitness research. Chang Yin (an AI character) walks through all four, safely, at the counter. Then take the free Strength Age test to get a balance-first plan. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults.""
- **Headline:** The 10-second balance test
- **CTA:** Learn more → `/q/a`
- **Audience:** W, M

**Concept 5: "The Jar Lid"** (UGC, SY + Chang Yin)
- **Angle:** Grip strength via a relatable domestic moment; couple chemistry.
- **Hook:** Sun Yoon hands Chang Yin a jar. He opens it easily. She: "Show-off. Show them how."
- **Visual:** Three grip moves: towel wring, water-jug carry, rubber-band finger spreads. Hands & Grip track screen.
- **Primary text:** "Grip strength is one of the simplest strength measures there is, and it's trainable at any age. Chang Yin (an AI character) shows three grip exercises using a towel, water jugs and a rubber band. They're from the *Grip & Hands* program in Strong Years. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." 7 days of Strong Years for $1, then {{PRICE}}/month. Cancel anytime online."
- **Headline:** Three moves for stronger hands
- **CTA:** Sign up → `/start`
- **Audience:** W, M

**Concept 6: "Yes, We're AI"** (UGC, candor)
- **Angle:** Trust differentiation against fake-guru accounts. Our honesty is the hook.
- **Hook:** Sun Yoon, straight to camera: "I'm not real. Neither is he. The exercises are."
- **Visual:** Cut to Chang Yin waving from the garage ("I'm 74. In our story. Watch."). Then the product: daily session, retest chart, recipe card. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Add a real photo of `[PT NAME]` reviewing a session on a laptop, name and credential on screen, and change the hook's last line to "The people who check our work are."] FALLBACK: "No reviewer shot; end on the product."
- **Primary text:** "Some wellness accounts pretend their AI teachers are real. We don't. Chang Yin and Sun Yoon are AI characters, and their story is fiction. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Every session is reviewed by `[PT NAME]`, a licensed physical therapist, and every recipe by `[RD NAME]`, a registered dietitian.] FALLBACK: "Every session and recipe is built from published guidelines for older adults, and our sources are on our site." What you get with Strong Years: a patient teacher every morning, an 8–12 minute Daily Practice with a chair-based version of everything, a real human coach live every Wednesday, and a monthly Strength Age test. 7 days for $1, then {{PRICE}}/month. Cancel anytime."
- **Headline:** [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Honest AI. Real physical therapist.] FALLBACK: "Honest AI. Real exercises."
- **CTA:** Learn more → `/start`
- **Audience:** All (run broad 35–65+); also the default retargeting ad for quiz completers

**Concept 7: "Do It With Me Now"** (FA, 45–60s)
- **Angle:** Give value in-feed; the viewer completes 60 seconds of the session before clicking.
- **Hook:** Chang Yin: "Stand up with me. Right now. Hold the counter." On screen: "60-second follow-along."
- **Visual:** One continuous minute: sit-to-stands, marching at the counter, slow exhale. Rep counter and timer on screen. Final 5s: "That was minute one of today's session."
- **Primary text:** "Did you do it with him? That was the first minute of today's Daily Practice. The full session is 8 minutes, levelled from chair-based Rebuild up to Iron, and there's a new one every day in Strong Years. Chang Yin is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Try 7 days for $1, then {{PRICE}}/month. Cancel anytime."
- **Headline:** Minute one done. 7 more?
- **CTA:** Sign up → `/start`
- **Audience:** W, M, CG

**Concept 8: "Coffee at 3 O'Clock"** (SY, UGC)
- **Angle:** Sleep/energy through blunt humor, routed to the kitchen quiz.
- **Hook:** Sun Yoon, pouring tea: "You drink coffee at three o'clock and then you blame the moon."
- **Visual:** She lists three evening habits (last caffeine before noon, light dinner, the 4-6 breath), Chang Yin demonstrates 20 seconds of slow-exhale breathing. End: quiz.
- **Primary text:** "Sun Yoon (an AI character) is blunt about evenings: caffeine lasts for hours, big late dinners sit heavy, and a slow breath helps you wind down. Take her free 2-minute Gut & Energy Check for a 7-day kitchen and evening plan. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Recipes checked by a registered dietitian.] FALLBACK: "Recipes built on published nutrition guidance for older adults." Not medical advice."
- **Headline:** Sun Yoon's 2-minute energy check
- **CTA:** Learn more → `/q/b`
- **Audience:** W

### Men 60–75 (M)

**Concept 9: "Strength Is the Retirement Plan"** (UGC)
- **Angle:** Independence and capability; strength framed as an asset to protect.
- **Hook:** Chang Yin picks up two full water jugs: "I'm 74. I was a welder for forty years. Everybody plans for money in retirement. Nobody plans for their legs." (Character line; on-screen tag "AI character, fictional story".)
- **Visual:** Farmer carry across the garage, then sit-to-stands with jugs (Strong level). Cut to the level switch and an empty monthly retest chart (axis and "Your number here" only; no example trend line, AUDIT F40).
- **Primary text:** "Chang Yin is an AI character: in his story, a 74-year-old retired welder who trains every morning with a chair and two water jugs. The research is real: muscle still responds to training at 60, 70 and beyond. Strong Years gives you a new 8–12 minute Daily Practice every day and a monthly Strength Age test so you can track it. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." 7 days for $1, then {{PRICE}}/month."
- **Headline:** Plan for your legs too
- **CTA:** Sign up → `/start`
- **Audience:** M

**Concept 10: "The Car-to-Kitchen Test"** (ST)
- **Angle:** Functional test from daily life.
- **Hook:** On screen: "Two full water jugs. Car to kitchen. No rest?" Chang Yin lifts them from a car trunk.
- **Visual:** He carries them to the kitchen, sets them down with a controlled squat. Explains the carry uses grip, legs and trunk together. Three training moves.
- **Primary text:** "Carrying groceries from the car is a strength test: grip, legs and trunk working together. Chang Yin (an AI character) shows how to train it at home with water jugs. Take the free Strength Age test to see how your legs and balance compare with typical results by age, and get a 7-day plan."
- **Headline:** The grocery test. Free Strength Age
- **CTA:** Learn more → `/q/a`
- **Audience:** M

**Concept 11: "Floor and Back Up"** (ST + FA)
- **Angle:** A skill most people stopped practising; framed as trainable.
- **Hook:** Chang Yin lowers himself to the floor using one hand and stands back up. On screen: "Getting up from the floor is a skill. Skills can be trained."
- **Visual:** Step-by-step progression starting from a sturdy chair and couch (half-kneel to stand with support). Safety line on screen: "Start with support. Stop if dizzy."
- **Primary text:** "Getting down to the floor and back up is something many people stop practising, which makes it harder over time. Chang Yin (an AI character) shows a safe progression that starts with a sturdy chair for support. It's part of Strong Years. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Check with your doctor before starting new exercise. 7 days for $1, then {{PRICE}}/month."
- **Headline:** Floor to standing, step by step
- **CTA:** Sign up → `/start`
- **Audience:** M, W

**Concept 12: "Golf, Fishing, Grandkids"** (UGC)
- **Angle:** Hobbies and roles men care about; rotation + grip + legs.
- **Hook:** Chang Yin with a golf club as a prop: "Your swing comes from your legs and your hips, not your arms."
- **Visual:** Band rotations, split-stance holds, grip work. Final shot: lifting a (real-weight) toddler-sized sandbag from floor to waist.
- **Primary text:** "Golf swing, casting a line, lifting a grandchild: it's all legs, hips, trunk and grip. Chang Yin (an AI character) trains all four in short daily sessions you can do in your garage. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Every session is reviewed by a licensed physical therapist.] FALLBACK: "Every session is built on published exercise guidelines for older adults." Try 7 days for $1."
- **Headline:** Train for what you love doing
- **CTA:** Sign up → `/start`
- **Audience:** M

**Concept 13: "Power Fades Faster Than Strength"** (UGC, mechanism)
- **Angle:** Mechanism-first for men who want the "why".
- **Hook:** Chang Yin: "Strength is how much you can lift. Power is how fast. Power fades faster as we age."
- **Visual:** Simple on-screen diagram (Ink on Paper, no gray): two lines, strength and power, power steeper. Then "fast up, slow down" chair stands; quick side steps at the counter.
- **Primary text:** "Leg power, the ability to move quickly, declines faster with age than strength, and it's what helps you catch yourself on a trip or cross the street in time. Strong Years trains it with 'fast up, slow down' movements at a counter. Chang Yin is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." 7 days for $1."
- **Headline:** Train power, not just strength
- **CTA:** Learn more → `/start`
- **Audience:** M

**Concept 14: "The Physical Therapist Explains"** (HX) [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: this entire concept, plus the reviewer's written consent to appear in ads and fair, disclosed compensation.] FALLBACK: run **Concept 14-F "A Real Coach Answers"** instead: a real human coach from the team (introduced by first name as "a coach on our team", no credential claim) answers one member question from the Wednesday Live Q&A in 30 seconds, then cuts to Chang Yin demonstrating. Lower third: "[First name], real person. Chang Yin, AI character." Primary text: "Every Wednesday a real person on our team answers member questions live. Every morning Chang Yin, an AI character, leads your Daily Practice. Strong Years: 7 days for $1, then {{PRICE}}/month." Headline: "AI coach. Real humans on Wednesdays."
- **Angle:** Real human credibility; the anti-Yang Mun.
- **Hook:** `[PT NAME]`, on camera in clinic clothes: "I'm a physical therapist. I check every session Chang Yin teaches. Here's why the chair stand is the first thing we train."
- **Visual:** PT explains in 30 seconds, then cuts to Chang Yin demonstrating. Lower third: "[PT NAME], PT, DPT, real person. Chang Yin, AI character."
- **Primary text:** "Meet `[PT NAME]`, PT, DPT, the real physical therapist who reviews every Strong Years session before you see it. Chang Yin, the AI character who teaches them, never gets tired, never rushes, and shows up every morning. Together: short strength and balance sessions with a chair-based version of everything. Try 7 days for $1, then {{PRICE}}/month."
- **Headline:** Reviewed by a real physical therapist
- **CTA:** Learn more → `/start`
- **Audience:** All.

### Adult children 35–55 (AC)

**Concept 15: "Ask Your Mom to Do This"** (UGC, adult-child hook)
- **Angle:** Give the adult child an action to take on their next call.
- **Hook:** On screen: "Next time you call your mom, ask her to do this." Chang Yin demonstrates the chair test.
- **Visual:** Split screen: a phone video call (real people or labelled dramatization) with a daughter counting while her mother does sit-to-stands. End: the free test + gift option.
- **Primary text:** "A simple way to check in on a parent's strength: the 30-second chair stand. Chang Yin (an AI character) shows how to do it safely. Do it together on a video call, then take the free Strength Age test for a 7-day plan. Want to give them the full program? Give Mom & Dad Strong Years: 3 months $49 or 12 months $119, prepaid, never auto-renews."
- **Headline:** A 30-second test to do together
- **CTA:** Learn more → `/q/a?mode=helper`
- **Audience:** AC

**Concept 16: "Give a Stronger Year"** (ST-IMG carousel; seasonal)
- **Angle:** Gift occasions (Mother's Day, Father's Day, Grandparents Day, holidays).
- **Cards:** 1) Sun Yoon holding a gift card: "Give your mom a stronger year." 2) The session screen: "A new 10-minute session every morning, with a seated version." 3) The Strength Age chart: "A monthly test you can do together." 4) [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `[PT NAME]` photo: "Reviewed by a real physical therapist."] FALLBACK: "Sun Yoon's recipe card: "Recipes every Sunday. Soft-food versions too."" 5) Price card: "3 months $49 · 12 months $119 · Never auto-renews."
- **Primary text:** "This year, give something they'll use every morning. Give Mom & Dad Strong Years: a daily strength and balance session led by Chang Yin (an AI character), Sun Yoon's recipes, and a monthly Strength Age test. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." 3 months $49 or 12 months $119, prepaid. Gifts never auto-renew. Delivered by email or as a printed card."
- **Headline:** Give Mom & Dad Strong Years, from $49
- **CTA:** Shop now → `/gift`
- **Audience:** AC

**Concept 17: "Get a Note When Dad Does His Session"** (product demo)
- **Angle:** Peace of mind for distant adult children (opt-in by parent).
- **Hook:** A phone notification on screen: "Your dad did 18 sessions this month."
- **Visual:** Screen recording of the gifter update feature, with the opt-in screen shown ("Would you like Sam to get a note when you finish sessions? Your numbers are never shared unless you choose.").
- **Primary text:** "Live far from your parents? With a Strong Years gift, your mom or dad can choose to let you get a monthly note like "Mom did 18 sessions." It's their choice, and their numbers stay private unless they decide to share. A daily 8–12 minute strength and balance session led by Chang Yin, an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults.""
- **Headline:** Peace of mind, with their permission
- **CTA:** Learn more → `/gift`
- **Audience:** AC

**Concept 18: "What You Notice at the Holidays"** (UGC voiceover, seasonal Nov–Dec)
- **Angle:** Observational, warm, not fear-based.
- **Hook:** Adult-child voiceover (real person or labelled dramatization) over a staircase shot: "At Thanksgiving I noticed Dad held the rail on every single stair."
- **Visual:** Cut to Chang Yin's Step Builder at the bottom stair; then the gift card.
- **Primary text:** "Stairs, chairs and car doors get harder gradually, and it's easy to miss until the holidays. Strength training helps at any age. Strong Years gives your parent a patient teacher every morning (Chang Yin, an AI character). [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Give 3 months for $49 or a year for $119. Gifts never auto-renew."
- **Headline:** A gift for the stairs
- **CTA:** Shop now → `/gift`
- **Audience:** AC (Nov 1–Dec 23)
- **Policy note:** the statement is about the speaker's parent, not the viewer, which is acceptable; keep it observational and avoid implying the viewer's parent has a condition.

**Concept 19: "Retest Together on FaceTime"** (UGC, real people)
- **Angle:** A shared monthly ritual between parent and child.
- **Hook:** Split-screen video call, both people sit on chairs with arms crossed: "Ready? Thirty seconds. Go."
- **Visual:** Both do the chair stand; they compare numbers and laugh. Chang Yin's timer voice overlaid. Final: "Retest Day is the 1st of every month."
- **Primary text:** "One family's new monthly phone call: the Strength Age retest, together. Strong Years members retest every month. Start your own 7 days for $1, or give your parent a gift membership. Chang Yin is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults.""
- **Headline:** Your new monthly call
- **CTA:** Learn more → `/gift`
- **Audience:** AC
- **Requirement:** real people, paid and credited, with "Paid participants" on screen; no results claims.

**Concept 20: "Real Retest Numbers"** (RM, before/after test data without transformation imagery; only once real data exists)
- **Angle:** Proof from real, consented members.
- **Hook:** Real member on camera (recorded via the review system, FUNNEL.md 7.10): "My first chair test was [real number]. Last month it was [real number]."
- **Visual:** The member in their own home doing the test live; their real retest chart (with written consent). No body comparison imagery. On screen: "Real member. Paid for their time. Individual result; results vary."
- **Primary text:** `[REAL MEMBER STORY, in their words, ≤ 60 words, approved by member]` + "Chang Yin is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Results vary. [If available: 'Of members who did 12+ sessions a month for 3 months, X% improved their chair-stand count' with date range.]"
- **Headline:** Real member. Real numbers.
- **CTA:** Learn more → `/start`
- **Audience:** All; also make an AC version with a member whose child gifted the membership.

### Caregivers (CG)

**Concept 21: "A Seated Version of Everything"** (FA, Rebuild track)
- **Angle:** Accessibility; wheelchair and walker users included.
- **Hook:** Chang Yin seated, a real (credited) seated demonstrator beside him in PiP: "Every session has a version you can do sitting down."
- **Visual:** Seated marches, knee extensions, towel rows, slow breathing.
- **Primary text:** "Caring for someone who can't do standing exercise? Every Strong Years session has a chair-based Rebuild version, done fully seated. Led by Chang Yin (an AI character), with movements demonstrated by a real coach. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Check with their doctor before starting. Gifts from $49, or try 7 days for $1."
- **Headline:** Seated strength sessions, daily
- **CTA:** Learn more → `/start?trk=rebuild`
- **Audience:** CG
- **Policy note:** "Caring for someone…" addresses a role, not a health attribute of the viewer; still, test a variant without it: "Daily seated strength sessions for older adults."

**Concept 22: "Ten Minutes for Both of You"** (UGC, real caregiver-and-parent pair, paid and credited)
- **Angle:** Caregiver's own wellbeing + shared activity.
- **Hook:** Two chairs side by side in a living room: "Ten minutes. Both of us. Every morning."
- **Visual:** The pair doing a Rebuild-track session together; the couple add-on screen ("Add your partner for $8/month").
- **Primary text:** "Do it together: add your partner to Strong Years for $8/month, each with your own level and progress. 10 minutes of seated or standing strength and balance, led by Chang Yin (an AI character). [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." 7 days for $1, then {{PRICE}}/month + $8 for your partner."
- **Headline:** Two people, one kitchen table
- **CTA:** Sign up → `/start`
- **Audience:** CG, AC

**Concept 23: "Take This Plan to the Doctor"** (ST-IMG + short video)
- **Angle:** Safety-first; the Gentle Restart printable is the offer.
- **Hook:** A printed one-page plan on a clipboard: "A one-page exercise plan to show the doctor."
- **Visual:** The PDF pages: movements with pictures, stop rules, a line for the doctor's notes.
- **Primary text:** "Not sure what exercise is safe to start? Take the free Strength Age test (it has a safety check first), and if standing tests aren't right today, we'll give you a one-page seated plan to show the doctor. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults." Chang Yin is an AI character."
- **Headline:** A safe first plan, free
- **CTA:** Learn more → `/q/a`
- **Audience:** CG, AC

### Cross-audience quiz ads

**Concept 24: "What's Your Strength Age?"** (QZ, static + 6s motion)
- **Angle:** Pure curiosity. The number is the hook.
- **Visual:** The Strength Age card, huge number with a "?" in place of the value, three answer-style buttons drawn on the image ("Younger than my birthday", "About the same", "Older"). Persimmon and Ink on Paper.
- **Primary text:** "Your birthday gives you one age. Your legs and balance give you another. Find your Strength Age with two simple at-home fitness tests used in senior fitness research, plus a few questions. Free, 3 minutes, with a 7-day plan. Created with AI characters. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Reviewed by a licensed physical therapist.] FALLBACK: "Built on published exercise guidelines for older adults.""
- **Headline:** Free 3-minute Strength Age test
- **CTA:** Learn more → `/q/a`
- **Audience:** All (primary broad prospecting ad in Advantage+)

**Concept 25: "Why Am I Tired After I Eat?"** (QZ, Sun Yoon static + 6s motion)
- **Angle:** The most common energy complaint, answered by the funniest character.
- **Visual:** Sun Yoon at the stove with a speech bubble: "Two minutes. Be honest. I will be." Five score bars (Fuel, Rhythm, Flow, Rest, Comfort) shown empty with Ink outlines.
- **Primary text:** "Sun Yoon's free Gut & Energy Check: 14 quick questions about breakfast, protein, water, walks and sleep, and a 7-day kitchen plan with three recipes to start tonight. Sun Yoon is an AI character. [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: Recipes checked by a registered dietitian.] FALLBACK: "Recipes built on published nutrition guidance for older adults." Not medical advice."
- **Headline:** The 2-minute energy check
- **CTA:** Learn more → `/q/b`
- **Audience:** W, AC

### Hook bank (for iterating winners; 3 hooks per winning concept per week)

Chair/legs: "Thirty seconds. One chair. How many?" · "This is the most important exercise after 60." · "Standing up is a strength test we take every day." · "The armrests are telling you something." · "You don't need a gym. You need a chair."
Balance: "Heel to toe. Ten seconds. Kitchen counter." · "Balance is a skill, not luck." · "The safest place to train balance is next to your sink."
Grip: "Can you open this jar?" · "Your hands are a strength test too."
Sun Yoon: "Toast is not breakfast." · "I'm going to talk about the bathroom." · "He complains. He still does it." · "You blame the moon." · "Eat like you're not in a hurry."
Candor: [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "I'm not real. The physical therapist is."] FALLBACK: ""I'm not real. The exercises are."" · "Some accounts pretend their AI teacher is real. We won't." · "They made me 74. I asked for 73. She said no." (CHARACTERS.md)
Chang (CHARACTERS.md openers): "I'm 74. Watch." · "Stand up." · "Try this with me." · "Measure twice. Lift once."
Adult children: "Ask your mom to do this on your next call." · "The gift she'll use every morning." · "Dad held the rail on every stair."

---

## 4. Campaign structure

### 4.1 Account setup
- Business verification, domain verification for `{{DOMAIN}}`, 2FA on all admins, two backup admins, one backup ad account under the same Business Manager (warmed with small spend).
- Pixel + Conversions API (server-side) with event deduplication. Events: `PageView`, `Lead` (quiz email captured), `StartTrial` ($1 trial and the $7/$17 membership-included starts; value = the model's expected contribution per start, see 5.1), `Purchase` (all paid orders: $7, $17, $9 bump, $27/$7/$29 upsells, gifts), `Subscribe` (first full membership charge, sent server-side on day 7).
- **Health-and-wellness data restrictions:** Meta restricts sharing of certain data and lower-funnel event optimization for advertisers it classifies as health and wellness in the US (tightened from January 2025). Check Events Manager for restriction notices on the pixel/domain before launch. Mitigations: keep the pixel off any page with a condition in its URL, title or content headings (condition-specific SEO pages live on a subdomain without the pixel); use neutral event and URL names (`/q/a`, `q_a_complete`); do not pass quiz answers or profile names to Meta; position the site as fitness and nutrition education (which it is). If purchase optimization is restricted anyway, the fallback is: optimize for the highest allowed event (e.g., `Lead` or landing page views), bid with cost caps, and judge performance on our own back-end attribution (UTM + server data), not in-platform ROAS.
- Naming convention: `{camp}_{aud}_{concept#}_{hook#}_{format}_{yyyymmdd}` e.g. `TEST_W_C01_H2_ST_20261005`.

### 4.2 Campaigns

| Campaign | Type | Budget share (steady state) | Setup |
|---|---|---|---|
| **1. SCALE: Advantage+ Sales** | Advantage+ sales campaign, optimizing `StartTrial` (or `Purchase` if StartTrial isn't allowed) with value rules | 60–70% | US, age min 45 hard floor (suggest 55+), all winners (graduated post IDs) 20–40 ads, existing-customer cap 10–15% |
| **2. TEST: Creative testing** | Manual (ABO), 1 ad set per concept, broad audience per code (W/M/AC/CG) | 15–20% | 3–5 ads per ad set (hook variants of one concept), $60–120/day per ad set, 3–5 days |
| **3. GIFT: Adult children** | Advantage+ or manual CBO, optimizing gift `Purchase` | 10–15% (30–40% in Nov–Dec, April–June, and before Grandparents Day in September) | Age 35–55, broad; concepts 15–19, 16 heavy in seasons; kit shown first in the gift upsell flow |
| **4. RETARGET** | Manual, small | 5% | Quiz started, not completed (7 days): "Your result is 2 questions away" (Concept 24 variant). Quiz completed, no purchase (14 days): Concept 6 + Concept 14. Exclude trials and members. Frequency cap via budget |
| **5. LOOKALIKES (test once seeds exist)** | Manual | from Test budget | 1%, 1–3%, 3–5% LALs of paying members (seed ≥ 1,000; best seed: members with 3+ months and 2+ retests); value-based LAL from 90-day revenue. Compare against broad; keep only if CPA beats broad by ≥ 15% |

Exclusions everywhere except gift: current members and trials (customer list synced daily via API).

### 4.3 Budget ramp (follows ECONOMICS.md: S2 is the plan, S3 is an option you exercise)

| Phase | Daily spend | Focus |
|---|---|---|
| Days 1–10 (test) | ~$3–5K/day (~$40K total) | 4 angles × 5 hooks × 2 front ends ($1 trial vs $7 Reset). Concepts 1, 2, 3, 6, 7, 9, 15, 24 first |
| **Day-10 gate** | — | Cost per paid trial ≤ $40, trial→paid ≥ 40% (read from the first 3 days of conversions), first-session completion ≥ 70%, chargebacks + refunds < 1% |
| Days 11–60, gate passed (S3 ramp) | Step up ~20%/day on winners to $12–15K/day by day 21 | ≥ 20 concepts in rotation by day 10 and ~5 new ones a day; add the GIFT campaign and the $27 "Strong at 70 Starter" paid-only path; annual push from day 21 |
| Days 11–60, gate failed (S2) | Hold at the S2 schedule | Fix the funnel before scaling |
| Days 61+ | Only while blended cost per trial ≤ $40 | Spanish archetype (month 4–5) adds lower-CPM inventory |

Reach math from ECONOMICS.md: $100K MRR by day 60 needs ~265 paid trial starts a day on average (peak ~335) at a blended cost per trial ≤ $45 while spending $12.5K+/day, about $650–740K of spend in 60 days. The model rates that a 25–35% chance; the day-10 gate decides whether to try.

## 5. KPI targets, testing cadence and scaling rules

### 5.1 Unit economics that set the targets (from ECONOMICS.md; the live model is economics.xlsx)

- **Base cost per paid trial start: $33.81** (CPM $18, link CTR 1.5% → CPC $1.20; landing → quiz 65% → opt-in 42% → trial 13%). $24.42 once the 30-day nurture of paid opt-ins is counted. A scale penalty raises cost per click as spend grows (~1.6× base at $500K/month).
- **Trial → paid:** 42% paid traffic, 48% organic. 10% of new payers take annual ($119 in the standard-mode baseline; in blitz mode the founding annual is $249 from L35).
- **Front-end revenue per start:** $12.99 (trial/front-end price + $9 bump at ~30% + $27 upsell at ~10% + $29 kit at ~6% + $7 downsell at ~5%). The front end returns ~25–40% of ad spend; it is **not** self-liquidating.
- **24-month contribution per paying member at $20:** ~$119. Net paid CAC per paying member ~$52 (S2) to ~$73–93 (S3), so LTV:CAC ~2.3× (S2) and ~1.3–1.6× (S3).
- **Media-buyer rule (ECONOMICS.md):** scale a creative or audience while its blended cost per trial is **≤ $26** (3× at $20), hold at **≤ $40**, kill **above $58** (the $20 break-even).

Pass `StartTrial` with a value equal to the model's expected contribution per trial start (update monthly from real cohorts) so value-based bidding learns that trials are worth far more than $1. Keep quiz answers and any health information out of every event payload.

### 5.2 Creative and funnel KPI targets

| Metric | Target | Kill / investigate |
|---|---|---|
| CPM (US 55+) | ~$18 (model base; Q4 higher) | > $30 sustained |
| Hook rate (3-sec views ÷ impressions) | ≥ 30% | < 20% after 3,000 impressions |
| Hold rate (ThruPlay ÷ 3-sec views) | ≥ 18% | < 10% |
| Link CTR | ≥ 1.5% (model base) | < 0.8% after $100 |
| CPC (link) | ≤ $1.20 (model base) | > $2.00 |
| Landing → quiz start | ≥ 65% (model base) | < 45% (page problem, not ad) |
| Quiz completion | ≥ 60% | < 45% |
| Opt-in rate (quiz → email + SMS consent) | ≥ 42% (model base) | < 30% |
| Opt-in → trial | ≥ 13% (model base) | < 8% |
| Cost per paid trial start | Scale ≤ $26 · hold ≤ $40 | Kill > $58 |
| $7 Reset cost per start (membership included) | Same thresholds as the trial; compare revenue per start at day 67 | > $58 |
| Gift purchase CPA | ≤ $35 (AOV $49–119 + kit) | > $50 |
| Trial → paid (by ad) | ≥ 42% (model base; goal 50%) | < 35% (ad attracting curiosity clicks; check message match) |
| Refund rate by ad | ≤ 6% | > 10% (ad over-promising) |

Always evaluate ads on **trial → paid and refund rate by ad**, not just cost per trial. An ad with a $20 trial cost and 25% conversion is worse than one at $30 with 50%.

### 5.3 Testing cadence

- **Weekly cycle:**
  - Monday: launch 3–4 new concepts (1 ad set each, 3 hooks each) + 3 new hooks on each of the top 2 winners.
  - Thursday: first read (spend ≥ 1.5× target CPA per ad set, or ≥ 3,000 impressions per ad for hook metrics). Kill obvious losers.
  - Friday/Saturday: second read; graduate winners to ASC (use the same post ID to keep social proof: likes and comments).
  - Sunday: creative brief for next week, built from winners' hooks and comments (the comment section tells you which objection to answer next).
- **Volume:** 10–15 new ads per week during scale; the AI production pipeline makes this cheap, but every ad still gets a movement check for any exercise shown ([ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: by the signed PT] FALLBACK: "by our team against published guidance; no review claim in the ad") and a compliance check against Section 1.
- **What to test, in order:** 1) concept/angle, 2) hook (first 3 seconds), 3) format (UGC vs follow-along vs static), 4) character (Chang Yin vs Sun Yoon vs PT), 5) destination (quiz vs /start vs /r7), 6) primary text length (short vs long; this audience often reads long copy).
- **Offer and price tests** run on-site (split by visitor), not by duplicating ads: $15/$20/$25 cells; $1 trial vs $7 Reset as first offer on result pages; email gate vs no gate.
- **Monthly:** audience cluster review (W vs M vs AC performance and LTV by cluster; move budget to best day-67 net revenue per start, not best CPA).

### 5.4 Scaling rules

- **Graduate:** an ad with ≥ 10 trials at ≤ $26 cost per trial and trial→paid tracking ≥ 40% moves to ASC.
- **Vertical scaling:** raise budgets ~20% (daily during an S3 ramp, every 48–72 hours otherwise) while 3-day blended cost per trial ≤ $26–40 and 7-day ≤ $40. One change per campaign per step.
- **Pull back:** cut 20% when 3-day blended cost per trial > $40; pause any ad above $58; pause the campaign's worst ads before cutting budget.
- **Cost caps:** once ASC exceeds 50 trials/week, run a parallel ASC with cost cap at $26–33 and shift budget to whichever holds volume.
- **Horizontal scaling:** duplicate winning ASC into a second ASC with a different creative mix (e.g., Sun Yoon-heavy) rather than pushing one campaign past its efficient spend.
- **Creative fatigue:** refresh when 7-day frequency > 3.5 or CTR falls 30% from its peak; retire when cost per trial is > $40 for 5 days despite refreshes.
- **Guardrails:** stop scaling any week in which refund rate > 8%, chargeback rate > 0.4% (and watch the absolute count: Mastercard's 100-chargebacks-a-month trigger bites at scale, OFFER.md 3.4), or trial→paid drops below 40% (the day-10 gate).
- **Seasonality:** Q4 CPMs rise sharply; lean on gift campaigns ($49–119 prepaid, no trial risk) and pre-load retargeting pools in October.

---

## 6. Creative production notes

- **Characters:** use the CHARACTERS.md master prompts and wardrobe codes, never ad-hoc descriptions. Chang Yin: 74, 5'7", retired welder, visibly strong but believable, bushy white eyebrows, thin scar through the outer left eyebrow, realistic skin texture; his 1960s California garage gym (sturdy armless chair, water jugs, bands, handwritten training log). Sun Yoon: 76, 5'1", silver bob with a tortoiseshell clip, glasses on a jade-green beaded cord, jade cardigan or striped apron; her kitchen with kimchi crocks. Neighbour Frank (79) demonstrates easier versions.
- **Movement accuracy:** for any ad showing exercise technique, the movement must be checked ([ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: by the signed PT] FALLBACK: "by our team against published guidance"); where AI video misrenders joints (knee valgus, hand placement, feet positions in balance stages), composite a real, credited human demonstrator. Never show unsafe form in an ad, even for a second.
- **Audio:** the CHARACTERS.md ElevenLabs settings: Chang ~140 wpm, warm low baritone, light Mandarin/Korean-influenced accent; Sun ~155 wpm, crisp, light Korean accent. Never played for accent comedy.
- **Captions:** Rice on Ink bars, 2 lines max, sentence case, lower-center safe zone (clear of Reels UI).
- **End cards:** product screen + one CTA line + offer terms line in full contrast.
- **Static images:** real product UI, the Strength Age card, recipe cards; always an "AI character" tag if a character appears.

---

## 7. Meta ad-policy risk register (health + AI)

| Risk | Where it bites | How we avoid it |
|---|---|---|
| **Personal attributes** (age, health, medical conditions, disability) asserted about the viewer | Hooks like "Are you over 60?", "your bad knees", "if you have arthritis" | Talk about the test, the product, the characters, or people in general. Run all copy through a "you + attribute" check before launch |
| **Before/after imagery** in health | Transformation-style ads, split images | No body transformations. Live tests only; real members' numbers as text with consent and typicality statement |
| **Misleading health claims / unrealistic results** | "Instantly", "reverse", "prevent falls", "fix back pain", "lower blood sugar" | Claims ladder: describe what a practice trains; cite general research modestly; no outcome guarantees |
| **Sensational content** | Images of falls, injuries, hospital beds, shock hooks | Warm, everyday settings only |
| **Health & wellness data / optimization restrictions** | Pixel/domain classified as health; purchase optimization limited | Neutral URLs and events, pixel off condition pages, CAPI hygiene, fallback optimization plan (Section 4.1) |
| **AI-generated realistic people** | Viewers misled that Chang Yin is real; Meta "AI info" labels; community reports | In-creative "AI character" tag, disclosure in primary text, keep C2PA metadata, never imply real credentials or life history |
| **Subscription clarity** | Ads mentioning "$1" without recurring terms; landing pages hiding terms | Any price mention includes recurring terms; landing and checkout show terms before payment (FUNNEL.md 5.1) |
| **Testimonials and endorsements** | Actor UGC presented as members; unpaid-looking paid endorsements | Real members only, paid relationships disclosed ("Paid participant"), dramatizations labelled |
| **Religious/cultural sensitivity** | "Ancient secret", monk imagery, sacred symbols used as props | Not used. Tai chi and qigong presented as movement practices; cultural reviewers approve visuals |
| **Account risk from negative feedback** | High "hide ad"/report rates lower delivery and can trigger reviews | Monitor negative feedback per ad weekly; retire ads with elevated negative feedback even if they convert |
| **Landing-page mismatch** | Ad promises a free test; landing page pushes payment first | Quiz ads land on the quiz; the offer appears only after the result |

Pre-launch checklist for every ad: AI tag in first 3 seconds · AI disclosure in primary text · no "you + attribute" phrasing · no before/after · no disease or instant claims · pricing terms included wherever price appears · PT approval for any movement shown · RD approval for any nutrition number · consent/release on file for any real person · high-contrast captions, no gray text.
