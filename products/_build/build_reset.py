"""Product 1: 7-Day Strength Reset ($7 front end)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import render, cover_html, DISCLOSURE, PRODUCTS, box, say
from blocks import exercise_md, exercise_compact_md, stop_box, before_you_start_md
from library import EX, STAND_SLOW
from norms import table, mid_table, CHAIR, ARM, STEP, REACH, CHAIR_STEADI_BELOW, BANDS, BAL
from evidence import appendix_md

# Pricing canon (BRIEF.md CANON UPDATE 2 + 3, Oct 1 2026): the books are a one-time Shopify product ($7 / $12 / $15 cells,
# default $12); the launch default is cell B, "$12 today = books + first month, then $25/mo"; founding $25/mo locked for as
# long as you stay subscribed ($30 only if cell data supports it); $35 standard after the founding close date; Essentials $12/mo as
# the save offer; 14-day money-back guarantee on the membership charge; email reminders; NO $1 trial, ever; no "text CANCEL".
# build(price_cents) renders one PDF per price for the app (strength_reset_2500/3000/3500.pdf). 2000 = the app's
# fallback when a buyer has no membership price, so it (and the base strength_reset.pdf) carries the generic canon text.
PRICE_VARIANTS = [None, 2000, 2500, 3000, 3500]


def price_text(cents):
    tail = ("It renews every month **until you cancel**, and every membership comes with a **14-day money-back guarantee** on the first monthly charge. "
            "We email you a reminder before every renewal. Cancel online anytime, no phone call, from your account page "
            "(strongyears.com/account), or email us and a person handles it within one business day. If you bought the books on their own, nothing renews; you can add the membership later.")
    if cents == 2500:
        head = ("Your Strong Years membership is **$25 a month**. Founding members keep that price for as long as they stay subscribed. "
                "If you started with the $12 starter offer (both books plus a 7-day trial of the membership), your first $25 charge is on day 7, then monthly.")
    elif cents == 3000:
        head = "Your Strong Years founding membership is **$30 a month**, and it stays $30 for as long as you stay subscribed."
    elif cents == 3500:
        head = "Your Strong Years membership is **$35 a month**."
    else:
        head = ("During our launch, a Strong Years founding membership is **$25 a month**, locked for as long as you stay subscribed. "
                "When the founding group is full, new members pay $35 a month. "
                "If you started with the $12 starter offer (both books plus a 7-day trial of the membership), your first $25 charge is on day 7, then $25 a month.")
    return head + " " + tail


PRICE_CENTS = None
NAME = "7-Day Strength Reset"

# ------------------------------------------------------------------ days
# Each segment: (label, start, end, [(exercise_id, dose), ...])
DAYS = [
 dict(n=1, title="Legs first", mins="about 11 minutes", need="Sturdy chair against a wall, kitchen counter, a clear wall",
      opener="Stand up. Sit down. That's the whole secret, done well.\n\nToday we build the one movement you use forty times a day. Getting out of a chair. Slow and clean. Legs first.",
      close="Good. Write your numbers in the tracker. Same time tomorrow.",
      habit=("Sun's protein breakfast", "Put 25 to 30 grams of protein in your breakfast (E28). Two eggs plus a cup of soy milk or a small Greek yogurt gets most people there. Kidney disease? Ask your doctor for your number first."),
      segs=[("Warm-up", "0:00", "2:00", [("ankle_pumps", "10 pumps + 5 circles each way, seated"), ("seated_march", "45 seconds"), ("shoulder_rolls", "8 slow rolls")]),
            ("Main block: 2 rounds", "2:00", "9:00", [("sit_to_stand", "2 sets of 8 reps. Rest 45 seconds between sets."), ("heel_raise", "2 sets of 10 reps"), ("wall_sit_high", "2 holds of 15 seconds. Rest 30 seconds between."), ("standing_march", "45 seconds")]),
            ("Cool-down", "9:00", "11:00", [("calf_stretch", "20 seconds each leg, twice"), ("cyclic_sigh", "1 minute")])]),
 dict(n=2, title="Steady feet", mins="about 10 minutes", need="Kitchen counter, sturdy chair against a wall, shoes on",
      opener="Balance is a skill. Skills get better with practice.\n\nWe stay at the counter the whole time today. Hands hover. They don't wander. Hold the counter. Pride is not a safety rail.",
      close="Tell me your longest one-leg time. Honest number. Same time tomorrow.",
      habit=("Toothbrush balance", "While you brush your teeth, stand heel-to-toe with your free hand on the sink or a grab bar. Switch feet halfway. Two minutes, twice a day, is 28 minutes of balance practice a week without trying. Home balance practice is a core part of the Otago programme (E13)."),
      segs=[("Warm-up", "0:00", "1:30", [("weight_shift", "5 slow shifts each direction"), ("ankle_pumps", "10 pumps, seated, then stand slowly")]),
            ("Main block", "1:30", "8:30", [("tandem_stand", "3 holds of 10 seconds each side"), ("single_leg", "3 holds of 10 seconds each side"), ("heel_toe_walk", "2 lengths of the counter"), ("side_step", "2 sets of 10 steps each way"), ("sit_stand_nohands", "1 set of 6 slow reps")]),
            ("Cool-down", "8:30", "10:00", [("hip_flexor", "20 seconds each side"), ("breath_46", "1 minute")])]),
 dict(n=3, title="Arms, back and grip", mins="about 11 minutes", need="Wall, kitchen counter, a hand towel, two water bottles, a half-gallon or gallon jug, chair against a wall",
      opener="Grip is a number worth caring about.\n\nIn a study of 142,861 adults in 17 countries, every 5 kilograms of lower grip strength was linked with 16% higher death rates over the study (E07). A link, not a cause. But grip, pulling and carrying are how you live. Jars. Grocery bags. Grandkids.",
      close="Carry your groceries in two bags this week. One in each hand. Same time tomorrow.",
      habit=("Two-bag carry", "Every time you bring groceries in, carry two lighter bags, one in each hand, standing tall. It's the carry exercise with a purpose. Pick bags up with a hinge, long back, never a rounded one."),
      segs=[("Warm-up", "0:00", "2:00", [("shoulder_rolls", "8 rolls"), ("wall_slide", "6 slow slides"), ("chin_tuck", "6 tucks, 2-second hold")]),
            ("Main block: 2 rounds", "2:00", "10:00", [("wall_pushup", "2 sets of 8"), ("jug_row", "2 sets of 8 each arm"), ("bottle_curl", "2 sets of 10"), ("seated_press", "2 sets of 8"), ("towel_wring", "3 wrings each direction, 3-second squeeze"), ("carry", "2 walks of 30 seconds")]),
            ("Cool-down", "10:00", "11:00", [("chest_lift", "6 lifts"), ("cyclic_sigh", "30 seconds")])]),
 dict(n=4, title="Loosen up", mins="about 11 minutes", need="Chair against a wall, kitchen counter, a wall",
      opener="I'd rather lift than stretch. Sun knows this. Sun is standing behind me.\n\nMobility is how strength gets to use its full range. For back stiffness, exercise has the best evidence of anything: 249 trials, 24,486 people (E30). Nothing forced today. Long back. Easy breathing.",
      close="Notice how you feel getting out of bed tomorrow. Same time tomorrow.",
      habit=("After-dinner walk", "Walk 10 minutes after your biggest meal. Even 2 to 5 minutes of light walking after eating lowers the blood-sugar rise compared with sitting (E23). Indoors is fine: kitchen to front door, and back."),
      segs=[("Seated", "0:00", "5:00", [("ankle_pumps", "10 pumps + 5 circles each way"), ("neck_nods", "5 nods, 3 half-turns each side"), ("seated_rotation", "6 gentle turns each side"), ("chest_lift", "8 lifts"), ("hamstring_seated", "2 holds of 20 seconds each leg"), ("figure4", "20 seconds each side")]),
            ("Standing at the counter", "5:00", "10:00", [("hip_flexor", "2 holds of 20 seconds each side"), ("calf_stretch", "20 seconds each leg"), ("standing_birddog", "6 each side"), ("hip_hinge", "8 slow hinges")]),
            ("Close", "10:00", "11:00", [("breath_46", "1 minute")])]),
 dict(n=5, title="Legs, a little faster", mins="about 11 minutes", need="Chair against a wall, bottom stair with a handrail (or a sturdy step), kitchen counter",
      opener="Today we stand up faster.\n\nNot sloppy. Faster. Fast-intent training, lifting quick and lowering slow, gives older adults functional gains similar to or a little better than regular training (E39). Getting up quick is what saves you when you trip.",
      close="Fast up, slow down. You did it. Same time tomorrow.",
      habit=("Commercial-break stands", "Every time you get up from the sofa or the table, do it twice: stand, sit, then stand. Two extra stands, a dozen times a day, adds up."),
      segs=[("Warm-up", "0:00", "2:00", [("standing_march", "1 minute"), ("sit_to_stand", "1 easy set of 5")]),
            ("Main block", "2:00", "9:30", [("power_stand", "3 sets of 5. Rest 45 seconds between sets."), ("step_up", "2 sets of 6 each leg"), ("hip_hinge", "2 sets of 8"), ("side_step", "2 sets of 10 steps each way"), ("heel_raise", "1 set of 12")]),
            ("Cool-down", "9:30", "11:00", [("calf_stretch", "20 seconds each leg"), ("cyclic_sigh", "1 minute")])]),
 dict(n=6, title="Breathe, flow, walk", mins="about 12 minutes", need="Space to stand, a chair behind you, kitchen counter, walking shoes",
      opener="Today is softer. Not easier. Softer.\n\nSlow breathing, then five pieces of a gentle qigong set called baduanjin, then a short walk. We teach tai chi and qigong as exercise: slow weight shifts, stepping and turning. Balance is one of the most trainable things there is. We do a small taste today.",
      close="Five minutes of slow breathing before bed tonight. That's the habit. Same time tomorrow.",
      habit=("Five-minute wind-down", "Before bed, five minutes of cyclic sighing: two breaths in through the nose, one long breath out through the mouth. In a one-month study of 111 adults, it improved daily mood more than mindfulness meditation (E18). No breath holds."),
      segs=[("Breath", "0:00", "2:00", [("cyclic_sigh", "2 minutes")]),
            ("Baduanjin, five pieces", "2:00", "6:30", [("sky_lift", "4 slow reps"), ("draw_bow", "3 each side"), ("heaven_earth", "3 each side"), ("owl_look", "3 each side"), ("fists", "4 each side")]),
            ("Tai chi", "6:30", "7:30", [("cloud_hands", "1 minute, slow")]),
            ("Walk", "7:30", "11:00", [("walk", "3 minutes 30 seconds, easy to brisk")]),
            ("Close", "11:00", "12:00", [("breath_46", "1 minute, seated")])]),
 dict(n=7, title="Put it together, then retest", mins="about 8 minutes, then the retest", need="Everything from this week",
      opener="Last day. Short session, then we measure.\n\nMeasure twice. Lift once. Warm up with me, then rest five minutes and redo your six tests.",
      close="You did seven days. Now look at your numbers. Then decide what's next.",
      habit=("Call one person", "Call someone today and tell them what you did this week. Stronger social ties were linked with a 50% higher likelihood of survival across 148 studies (E37). A link, not a promise. But call anyway."),
      segs=[("Warm-up", "0:00", "1:30", [("standing_march", "45 seconds"), ("weight_shift", "4 shifts each direction")]),
            ("Full-body round", "1:30", "8:00", [("sit_to_stand", "1 set of 8"), ("wall_pushup", "1 set of 8"), ("tandem_stand", "2 holds of 10 seconds each side"), ("jug_row", "1 set of 8 each arm"), ("heel_raise", "1 set of 10"), ("cyclic_sigh", "30 seconds")])]),
]


SEEN = set()


def day_md(d):
    out = [f"# Day {d['n']}: {d['title']}\n",
           f"**Time:** {d['mins']}. **You need:** {d['need']}.\n",
           say("chang", d["opener"]),
           stop_box(),
           "## At a glance\n",
           "| Minutes | Part | Moves |", "|---|---|---|"]
    for label, a, b, moves in d["segs"]:
        names = "; ".join(f"{EX[m]['name']} ({dose.rstrip('.')})" for m, dose in moves)
        out.append(f"| {a}–{b} | {label} | {names} |")
    out.append("")
    seen = set()
    for label, a, b, moves in d["segs"]:
        out.append(f"## {label} ({a}–{b})\n")
        for m, dose in moves:
            if m in SEEN:
                out.append(exercise_compact_md(m, dose))
            else:
                out.append(exercise_md(m, dose))
                SEEN.add(m)
    out.append(say("chang", d["close"]))
    t, txt = d["habit"]
    out.append(box("note", f"Today's habit: {t}.", txt))
    out.append('<p class="check">☐ Session done &nbsp;&nbsp; ☐ Habit done &nbsp;&nbsp; Effort (1 easy to 5 hard): ____ &nbsp;&nbsp; Any pain above 3/10? ☐ No ☐ Yes</p>\n')
    return "\n".join(out)


def tests_md():
    return f"""
# Your six tests

Six simple tests. About 15 minutes. Do them before Day 1, then again after Day 7, the same way, in the same shoes, at about the same time of day.

These are the same tests used in senior fitness research: the Senior Fitness Test by Rikli and Jones (normal ranges from 7,183 US adults aged 60 to 94, E49) and the CDC's STEADI screening tools for older adults (E11, E50, E51). They compare you with typical people your age. **They are fitness checks, not a medical diagnosis.** A low number is a starting line, not a verdict.

<div class="box note" markdown="1">
<span class="label">What you need:</span> sturdy armless chair (about 17 inches high) pushed against a wall; a kitchen counter; a timer or phone; a 5-pound dumbbell (women) or 8-pound dumbbell (men), or a half-gallon jug of water (about 4.4 pounds) or a gallon jug (about 8.3 pounds); a ruler or tape measure; a strip of tape; 10 feet of clear floor. A helper makes it easier and safer.
</div>

{box("stop", "Skip the standing tests today", "if you ticked anything in the Before you start list, use a walker or wheelchair, or feel unwell. Do the arm curl and the sit-and-reach seated, follow every Easier version this week (that's our chair-based Rebuild level), and show this plan to your doctor.")}

## Test 1: 30-second chair stand

**Why it matters:** getting out of a chair is leg strength you use every day. The CDC uses this test in its older-adult screening (E11). Taking longer than 15 seconds for five stands is one of the European screening signs of low muscle strength (E06).

1. Chair against the wall. Sit in the middle of the seat, feet flat, about shoulder-width apart.
2. Cross your arms over your chest, hands on opposite shoulders.
3. On "Go", stand all the way up, then sit all the way down. That's one.
4. Repeat as many times as you comfortably can in 30 seconds. If you're more than halfway up at 30 seconds, it counts.
5. Stop anytime if anything hurts, you feel dizzy or short of breath.

**Breathe out as you stand.** If you need your hands to stand, that's okay: count your stands and write an **H** next to the number. (Officially the CDC scores it 0 when arms are used, E11. We track your number anyway so you can see progress.)

**Your score:** number of full stands in 30 seconds.

Typical range (middle 50% for your age, E49):

{table("chair", CHAIR)}

The CDC counts scores **below** these numbers as below average: women 60–64 under 12, 65–69 under 11, 70–79 under 10, 80–84 under 9, 85–89 under 8, 90–94 under 4; men 60–64 under 14, 65–74 under 12, 75–79 under 11, 80–84 under 10, 85–89 under 8, 90–94 under 7 (E11).

## Test 2: Four-stage balance

**Why it matters:** the CDC uses the heel-to-toe stand as a key checkpoint: under 10 seconds is worth mentioning to your doctor (E50). In a study of 1,702 adults aged 51 to 75, people who couldn't stand on one leg for 10 seconds had higher death rates over about seven years (84% higher, E09). That is a warning sign, not a sentence. Balance is one of the most trainable things there is: practise it and it gets better, which is why it's in this week.

Stand next to your kitchen counter, one hand hovering just above it. Eyes open. You can move your arms or body to balance, but not your feet. If you touch the counter or move your feet, that stage is over. A helper stands beside you.

1. **Feet side by side**, touching. Hold 10 seconds.
2. **Half step:** the arch of one foot beside the big toe of the other. Hold 10 seconds.
3. **Heel to toe:** one foot directly in front of the other. Hold 10 seconds.
4. **One foot:** stand on one foot. Hold 10 seconds.

Stop at the first position you can't hold for 10 seconds.

**Your score:** the last position you held for the full 10 seconds (0 to 4), plus how many seconds you held the next one.

## Test 3: 30-second arm curl

**Why it matters:** arm strength for carrying, lifting and pushing yourself up (E49).

1. Sit in the chair against the wall, back straight, feet flat.
2. Hold the weight in your stronger hand, arm hanging straight down beside the chair, palm facing in.
3. On "Go", curl the weight up, turning your palm up as it rises, then lower it all the way until your arm is straight.
4. Repeat as many full curls as you can in 30 seconds. Elbow stays by your side.

**Breathe out as you curl.** The research used 5 pounds for women and 8 pounds for men. A half-gallon jug is close to 5 pounds and a gallon jug is about 8 pounds but awkward to hold, so your number may differ from the chart. **Use the same object every time you retest.**

**Your score:** full curls in 30 seconds. Write down what you lifted.

{table("arm", ARM)}

## Test 4: Two-minute step test

**Why it matters:** it measures your stamina for walking, stairs and chores (E49).

<div class="box stop" markdown="1">
<span class="label">This one gets your heart rate up.</span> Skip it if you have any of the "doctor first" items, if you get breathless easily, or if you have a heart condition, until your doctor says it's okay. You can slow down or rest at any time; the clock keeps running. **Stop if you feel chest pain, dizziness or unusual breathlessness.**
</div>

1. Find the height: halfway between your kneecap and the top of your hip bone. Put a strip of tape on the wall or counter at that height.
2. Stand side-on to the counter, one hand resting on it.
3. On "Go", march in place, lifting each knee up to the tape mark.
4. Count every time your **right** knee reaches the mark. March for two minutes.
5. Afterward, keep walking slowly around the kitchen for a minute. Don't sit down straight away.

**Your score:** number of right-knee lifts in two minutes.

{table("step", STEP)}

## Test 5: Chair sit-and-reach (long-back version)

**Why it matters:** flexibility behind the legs, which you use for putting on shoes, getting in the car and bending safely (E49).

<div class="box stop" markdown="1">
<span class="label">Osteoporosis, low bone density, or a past spine fracture?</span> Skip this test. Rounding forward is the one bending pattern we avoid for fragile bones (E40). You'll track your hips and hamstrings with the stretches instead.
</div>

1. Sit on the front edge of the chair (chair against the wall). Bend one knee, foot flat.
2. Straighten your other leg in front of you, heel on the floor, toes pointing up.
3. Put one hand on top of the other, middle fingers even.
4. **Keep your back long** and hinge forward from your hips, reaching toward your toes. Go slowly. Hold two seconds. No bouncing.
5. A helper measures from your middle fingertips to the toe of your shoe. Short of the toe is a minus number (−3 inches). Past the toe is a plus number (+2 inches). Touching the toe is 0.
6. Two tries. Keep the best.

**Breathe out as you reach.** Because we ask you to keep your back long, which is safer, your number may look a little lower than the chart. You're comparing with yourself.

**Your score:** best reach in inches (plus or minus).

{table("reach", REACH, " in")}

## Test 6: Timed Up and Go

**Why it matters:** it puts together standing up, walking, turning and sitting down, the moves behind getting around your home. The CDC uses it as a screening check: **12 seconds or longer** is worth mentioning to your doctor (E51).

1. Put a strip of tape on the floor 10 feet from the front of the chair. Clear the path.
2. Sit in the chair, back against the backrest. Wear your normal shoes; use your cane or walker if you normally do.
3. On "Go", stand up, walk to the tape **at your normal pace**, turn around, walk back and sit down.
4. The helper times you from "Go" until you are sitting. The helper walks beside you.

**Your score:** seconds. 12 seconds or more? Tell your doctor at your next visit. Standing up, walking and turning are exactly what this week trains, and the number usually moves with practice.

# Your score sheet

Write your numbers on Day 0. Fill in the typical range for your age and sex from the charts. Then circle where you are: **Below**, **In**, or **Above** the typical range. On Day 7, write your retest number beside it.

Name: <span class="blank"></span> Age: <span class="blank s"></span> Woman / Man<br>Date (Day 0): <span class="blank"></span> Date (Day 7): <span class="blank"></span>

<table class="write">
<thead><tr><th>Test</th><th>Day 0</th><th>Typical for me</th><th>Below / In / Above</th><th>Day 7</th><th>Change</th></tr></thead>
<tbody>
<tr><td>1. Chair stands in 30 s (H if hands used)</td><td></td><td></td><td>B &nbsp; I &nbsp; A</td><td></td><td></td></tr>
<tr><td>2. Balance: last stage held 10 s (0–4) + seconds on the next</td><td></td><td>Stage 3 or 4</td><td>B &nbsp; I &nbsp; A</td><td></td><td></td></tr>
<tr><td>3. Arm curls in 30 s (what I lifted: ______)</td><td></td><td></td><td>B &nbsp; I &nbsp; A</td><td></td><td></td></tr>
<tr><td>4. Step test: right-knee lifts in 2 min</td><td></td><td></td><td>B &nbsp; I &nbsp; A</td><td></td><td></td></tr>
<tr><td>5. Sit-and-reach, inches (+/−)</td><td></td><td></td><td>B &nbsp; I &nbsp; A</td><td></td><td></td></tr>
<tr><td>6. Timed Up and Go, seconds</td><td></td><td>Under 12</td><td>Under 12 / 12+</td><td></td><td></td></tr>
</tbody></table>

# Your Strength Age

Your birthday gives you one age. Your legs and your balance give you another. Strength Age compares your chair stands and your balance with typical results for people your age and sex. It's a motivational estimate from published fitness norms, **not a medical test**. The Strong Years app adds a few questions about daily life, so the app's number can differ from this paper version by a year or two.

**Step 1: chair points.** Find your midpoint below (the middle of the typical range). Under 60? Use 60–64.

{mid_table()}

Chair points = 2.5 × (midpoint − your stands). Round to one decimal. Keep it between −12 and +12. **If you used your hands**, chair points are at least +8.

<div class="keep" markdown="1">

**Step 2: balance points.**

| Last position you held for 10 seconds | Balance points |
|---|---|
""" + "\n".join(f"| {a} | {b} |" for a, b in BAL) + f"""

</div>

**Step 3:** Strength Age = your age + chair points + balance points. Round to a whole year. It can't be more than 15 years below or 20 years above your age, and never below 40.

<div class="box note" markdown="1">
<span class="label">Two worked examples.</span>

**Mary, 71.** Midpoint for women 70–74 is 12.5. She did 11 stands: 2.5 × (12.5 − 11) = **+3.8**. She held heel-to-toe (position 3): **0**. 71 + 3.8 + 0 = 74.8, so her Strength Age is **75**. Her plan: legs first, every day.

**Tom, 68.** Midpoint for men 65–69 is 15.0. He did 17 stands: 2.5 × (15 − 17) = **−5**. He held one foot (position 4): **−3**. 68 − 5 − 3 = **60**. His plan: keep going, try the Harder versions.

(Mary and Tom are made-up examples to show the math.)
</div>

<table class="write">
<thead><tr><th></th><th>Day 0</th><th>Day 7</th></tr></thead>
<tbody>
<tr><td>My midpoint</td><td></td><td></td></tr>
<tr><td>Chair points</td><td></td><td></td></tr>
<tr><td>Balance points</td><td></td><td></td></tr>
<tr><td><strong>My Strength Age</strong></td><td></td><td></td></tr>
</tbody></table>
"""


def habits_md():
    out = ["# Your seven habit cards\n",
           "One small habit a day, attached to something you already do. Cut these out and stick today's card on the fridge. By Day 7 you'll have tried all seven. Keep the two you liked best.\n"]
    for d in DAYS:
        t, txt = d["habit"]
        out.append(f'<div class="box note" markdown="1">\n<span class="label">Day {d["n"]}: {t}.</span> {txt}\n\n☐ Done today\n</div>\n')
    return "\n".join(out)


def retest_md():
    return f"""
# Day 7: the retest

Rest five minutes after today's session. Have some water. Then redo all six tests exactly the way you did on Day 0: same chair, same shoes, same weight for the curl, same helper if you had one. Write the numbers in the Day 7 column of your score sheet, and work out your Strength Age again.

{say("sun", "Sun Yoon. His wife. Also AI. Here's the honest version: in seven days, most of the change is your body getting better at the movement. Your brain learns the move. That's real. Building actual muscle takes weeks of training two or three times a week (E01, E02). So if your number went up one or two, good. If it didn't move, also fine. You started. Seven out of ten. Because I love you.")}

**What counts as progress this week:**

- One or two more chair stands. The chair stand is the number that usually moves first.
- A position further on the balance test, or more seconds on the next one.
- The Timed Up and Go a second or two quicker, walking at your normal pace.
- Getting up from the sofa without thinking about it.
- You did seven sessions. That's the habit, and the habit is the program.

**If a number went down:** tired, sore, a bad night's sleep, a different time of day. Retest in a week. If something hurts more than 3 out of 10 and isn't settling, or anything on the red-flag list appears, stop and call your doctor.
"""


NEXT_SAY = say("chang", "Seven days is a start. Strength is a habit. Habits need tomorrow.\n\nMuscle is a savings account. Deposit now. You'll need it later.")


def next_md():
    return f"""
# What's next: Strong Years

{NEXT_SAY}

You can repeat this week on your own. Here's how: do Days 1, 3 and 5 as your strength days, two or three times a week (that's what the research uses, E01, E02), Day 2 and Day 4 in between, and Day 6 on the weekend. When a move feels easy for all the reps, switch to its Harder version.

Or keep going with us in **Strong Years**, the membership this Reset is the front door to:

- **A new 8 to 12 minute session every day** with Chang Yin. The week rotates: Monday strength, Tuesday mobility, Wednesday balance, Thursday strength, Friday breath and qigong, Saturday walk-and-talk, Sunday rest and stretch.
- **Four levels, so it always fits:** Rebuild (all chair-based), Steady, Strong and Iron. A "sore knee / sore back / low energy today" button swaps in a gentler version.
- **Six 12-week programs** to finish, one at a time: Strong at 70, Back Strong, Balance and Steady Feet, Gut Reset with Sun Yoon, Grip and Hands, and Walk Stronger.
- **Sun Yoon's Kitchen every Sunday:** three recipes, a grocery list and one kitchen remedy graded honestly.
- **Your Strength Age retest every month**, charted, so you can see the line move.
- **A daily message** from Chang by email at the time you choose, **Ask Chang / Ask Sun** AI chat that remembers your level if you allow it, and a **real human coach** on a live Q&A every Wednesday.

**What it costs, plainly.** {price_text(PRICE_CENTS)}

Whatever you decide: keep your score sheet. Retest in 30 days. The number is yours.
"""


def tracker_md():
    rows = "\n".join(f"<tr><td>Day {d['n']}: {d['title']}</td><td></td><td></td><td></td><td></td><td></td></tr>" for d in DAYS)
    return f"""
# Your 7-day tracker

Stick this on the fridge. Tick it every day. Grace rule: miss a day, do the next day's session tomorrow. Don't double up.

<table class="write">
<thead><tr><th>Day</th><th>Date</th><th>Session ☐</th><th>Habit ☐</th><th>Effort 1–5</th><th>Pain above 3/10? Where?</th></tr></thead>
<tbody>
{rows}
</tbody></table>

**My best number this week:** <span class="blank" style="width:4in"></span>

**The move I'm proudest of:** <span class="blank" style="width:4in"></span>

**The habit I'm keeping:** <span class="blank" style="width:4in"></span>

**Who I told:** <span class="blank" style="width:4in"></span>
"""


INTRO_SAY = say("chang", "I'm Chang Yin. I'm 74. I'm also an AI character. A team of people made me, and they built this plan on published research for older adults. My life story is made up. The research is not. The sources are in the back of this book.\n\nHere's the deal. Seven days. One short session a day, 8 to 12 minutes. Most of it next to a chair and a kitchen counter.\n\nYou won't be a new person in seven days. Nobody is. What you will have: your six numbers, written down. Seven sessions done. One habit started.")


def intro_md():
    return f"""
# Start here {{: .nobreak}}

{INTRO_SAY}

## Why legs first

Strength drops faster than muscle. Around age 75, muscle mass drops about 0.6 to 1% a year, but strength drops about 2.5 to 4% a year (E04). Ten days of bed rest cost healthy adults in their late 60s about 2 pounds (0.95 kg) of leg muscle (E05).

The good part: strength answers training at every age. A review of 121 trials with 6,700 older adults training two or three times a week found large gains in strength and easier chair stands (E01). In one small study, ten nursing-home residents around age 90 trained their legs for eight weeks and their strength rose 174% (E03). Ten people is a small study. It still shows muscle adapts in the 90s.

## How this week works

1. **Day 0: test.** Do the six tests (about 15 minutes) and fill in your score sheet. Work out your Strength Age.
2. **Days 1 to 7: one session a day.** Each day has a minute-by-minute plan, every move explained, with an **Easier** and a **Harder** version.
3. **One habit a day.** Seven small habits you attach to things you already do.
4. **Day 7: retest.** Same six tests. Compare.

## Pick your starting level

Every move in this book has three versions. Choose for each move, not for the whole book.

| If this is you | Start with |
|---|---|
| You need your hands to get out of a chair, use a walker, or feel unsteady standing | The **Easier** version of everything. It's chair-based. (In Strong Years this is the Rebuild level.) |
| You can stand up without your hands but don't exercise regularly | The **main** version. (Steady level.) |
| You exercise regularly and the main version feels easy for all the reps | The **Harder** version. (Strong or Iron level.) |

Start easier than you think. Finish wanting one more. "Three reps. Okay, two. Okay, one, but a good one."

## What you need

- A sturdy chair with no wheels, pushed against a wall.
- Your kitchen counter (a sturdy one, not a rolling island).
- A clear wall.
- A hand towel, two full water bottles, a half-gallon or gallon jug of water.
- The bottom stair with a handrail, or a sturdy low step (Day 5).
- A timer or phone, a ruler or tape measure, and a strip of tape (for the tests).
- Shoes with a grippy sole.

{before_you_start_md()}
"""


def build(price_cents=None):
    global PRICE_CENTS
    PRICE_CENTS = price_cents
    SEEN.clear()
    parts = [intro_md(), tests_md()]
    parts += [day_md(d) for d in DAYS]
    parts += [habits_md(), retest_md(), next_md(), tracker_md()]
    ids = {"E01", "E02", "E03", "E04", "E05", "E06", "E07", "E09", "E11", "E13", "E18", "E23", "E28",
           "E37", "E39", "E40", "E41", "E42", "E43", "E46", "E49", "E50", "E51"}
    for d in DAYS:
        for _, _, _, moves in d["segs"]:
            for m, _ in moves:
                ids.update(EX[m]["ev"])
    parts.append(appendix_md(ids))
    md = "\n\n".join(parts)
    cover = cover_html("Chang Yin's", NAME, "Six tests. Seven short sessions. One stronger week.<br>Built for adults 60 to 80, chair-first, at home.",
                       "With Sun Yoon, who checks his work.", DISCLOSURE)
    suffix = "" if price_cents is None else f"_{price_cents}"
    out_pdf = os.path.join(PRODUCTS, f"strength_reset{suffix}.pdf")
    out_md = os.path.join(PRODUCTS, "strength_reset.md") if price_cents is None else None
    hdr = (f"<!-- Source for {NAME}. Generated by products/_build/build_reset.py from the shared exercise library. "
           f"Edit the build script (or library.py), then re-run `python3 products/_build/build_all.py`. "
           "Pricing text follows BRIEF.md BLITZ CANON; per-price PDFs come from build(price_cents). -->")
    render(md, out_pdf, NAME, cover=cover, out_md=out_md, md_header=hdr)
    return out_pdf


if __name__ == "__main__":
    print(build())
