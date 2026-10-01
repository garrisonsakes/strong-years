"""Product 3: 12-Week Strong Years Printable (wall plan, 4 tracks, monthly Strength Age retest sheet, habit tracker)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import render, cover_html, DISCLOSURE, PRODUCTS, box, say
from library import STOP, EMERGENCY, PAIN_RULE
from norms import BANDS, CHAIR, ARM, STEP, REACH, MID, BAL
from evidence import appendix_md

NAME = "12-Week Strong Years Printable"
PHASES = ["Weeks 1–2", "Weeks 3–4 ★", "Weeks 5–6", "Weeks 7–8 ★", "Weeks 9–10", "Weeks 11–12 ★"]

# Each row: (move, [6 phase doses]). Strength moves: Mon + Thu. Balance: Wed + a little daily. Walk: most days.
PLAN = {
 "Rebuild": dict(desc="Chair-based. Seated, or standing with both hands on the counter and the chair right behind you.",
   rows=[
    ("Chair sit-to-stand (Mon, Thu)", ["2×5, hands on thighs, cushion on seat", "2×6, hands on thighs", "3×6", "3×8", "3×8, no cushion", "3×8, arms crossed if you can"]),
    ("Seated chest press (Mon, Thu)", ["2×8, empty hands", "2×10, water bottles", "3×10", "3×12", "3×10, band behind chair", "3×12, band"]),
    ("Seated towel pull-apart (Mon, Thu)", ["3 pulls, 3-s squeeze", "4 pulls, 3 s", "5 pulls, 3 s", "5 pulls, 5 s", "3×10 band pulls", "3×12 band pulls"]),
    ("Seated heel raises (Mon, Wed, Thu)", ["2×10", "2×12", "3×12", "3×12, 2-s pause at the top", "Standing, both hands on counter, 2×10", "Standing, 3×10"]),
    ("Seated knee straightening (Mon, Thu)", ["1×8 each leg", "2×8 each", "2×10 each", "3×10 each", "3×10, 3-s hold", "3×10, 5-s hold"]),
    ("Balance at the counter, both hands (Wed + daily)", ["Feet together 3×10 s", "Feet together 3×20 s", "Half-step 3×10 s", "Half-step 3×20 s", "Heel-to-toe 3×10 s", "Heel-to-toe 3×15 s"]),
    ("Walking (most days)", ["3–5 min indoors, twice a day", "5 min, twice a day", "7 min, twice", "10 min, twice", "10–15 min, twice", "15 min, twice"]),
   ]),
 "Steady": dict(desc="Standard versions with counter or wall support. Most new members start here.",
   rows=[
    ("Sit-to-stand, arms crossed (Mon, Thu)", ["2×8", "3×8", "3×10", "3×10, 3-s lower", "3×12, 3-s lower", "3×8 power stands (fast up, slow down)"]),
    ("Push (Mon, Thu)", ["Wall push-up 2×8", "Wall 3×10", "Wall 3×12, feet back", "Counter push-up 2×8", "Counter 3×8", "Counter 3×10"]),
    ("One-arm jug row (Mon, Thu)", ["Half-gallon 2×8 each", "Half-gallon 3×10", "Gallon 2×8", "Gallon 3×8", "Gallon 3×10", "Gallon 3×10, 1-s pause"]),
    ("Heel raises at the counter (Mon, Thu)", ["2×10", "3×10", "3×12", "One hand 3×10", "One hand 3×12", "Single leg 2×6 each, both hands"]),
    ("Step-ups, hand on rail (Thu)", ["Toe taps 2×10", "Toe taps 3×10", "Step-ups 2×6 each", "3×6 each", "3×8 each", "3×10 each"]),
    ("High wall sit (Mon)", ["2×15 s", "2×20 s", "3×20 s", "3×20 s", "3×25 s", "3×30 s"]),
    ("Balance at the counter (Wed + toothbrush daily)", ["Heel-to-toe 3×10 s, hands on", "Heel-to-toe 3×15 s", "One leg 3×10 s, hands on", "One leg 3×15 s", "Heel-to-toe, hands hovering 3×15 s", "One leg, one hand hovering 3×15 s"]),
    ("Walking (most days)", ["15 min", "20 min", "20 min + 2×1 min brisk", "25 min + 3×1 min brisk", "30 min + 3×90 s brisk", "30 min + 4×90 s brisk"]),
   ]),
 "Strong": dict(desc="Added load, slower lowering, less hand support. For people who can do Steady comfortably.",
   rows=[
    ("Sit-to-stand (Mon, Thu)", ["3×8, 3-s lower", "3×10, 3-s lower", "3×8, jug at chest", "3×10, jug at chest", "3×6 power stands", "3×6 power stands, jug"]),
    ("Push (Mon, Thu)", ["Wall 2×10, feet back", "Counter 2×8", "Counter 3×8", "Counter 3×10", "Counter 3×10, 3-s lower", "Counter 3×12, 3-s lower"]),
    ("Jug row (Mon, Thu)", ["Gallon 2×10 each", "Gallon 3×10", "Gallon 3×10, pause", "Heavier bag 3×8", "Heavier bag 3×10", "Heavier bag 3×12"]),
    ("Step-ups (Thu)", ["2×6 each", "3×6 each", "3×8 each", "3×8, bag in free hand", "3×10, bag", "3×10, heavier bag"]),
    ("Hinge pick-up (Thu)", ["Jug from chair 2×8", "3×8", "3×10", "Jug from bottom step 3×8", "3×10", "Heavier, from step 3×10"]),
    ("Grocery carry (Thu)", ["2×30 s, two bags", "3×30 s", "3×40 s", "3×40 s, heavier", "3×45 s", "3×60 s"]),
    ("Balance (Wed + daily)", ["Heel-to-toe, one hand hovering 3×15 s", "3×20 s", "One leg, one hand hovering 3×15 s", "3×20 s", "Backward walk, hand on counter, 2 lengths", "One leg + clock reach 3 each"]),
    ("Walking (most days)", ["30 min", "30 min + 3×90 s brisk", "35 min + 4×90 s", "40 min + 4×2 min", "40 min, hills", "45 min, hills"]),
   ]),
 "Iron": dict(desc="For people who already train. Anything marked advanced is never your starting point.",
   rows=[
    ("Legs (Mon, Thu)", ["Sit-to-stand, jug, 3×10", "Counter split squat 3×8 each", "Split squat 3×10", "Split squat, jug, 3×8 ▲", "Split squat, jug, 3×10 ▲", "Power stands, jug, 4×6 ▲"]),
    ("Push (Mon, Thu)", ["Counter 3×10, 3-s lower", "Counter 3×12", "Counter 3×12, 3-s lower", "Bottom-stair push-up 3×6 ▲", "Stair 3×8 ▲", "Stair 3×10 ▲"]),
    ("Row (Mon, Thu)", ["Gallon 3×12, pause", "Heavy bag 3×10", "Heavy bag 3×12", "Kettlebell or heavy bag 4×10 ▲", "4×12 ▲", "4×12, 2-s pause ▲"]),
    ("Step-ups (Thu)", ["3×8, bag", "3×10, bag", "3×10, heavier bag", "Higher step 3×8", "Higher step 3×10", "Higher step, bag, 3×10 ▲"]),
    ("Hinge pick-up (Thu)", ["From step 3×8", "3×10", "Heavier 3×8", "Heavier 3×10", "4×8 ▲", "4×10 ▲"]),
    ("Carry (Thu)", ["3×45 s heavy", "3×60 s", "4×45 s heavier", "4×60 s ▲", "4×60 s, one hand, switch ▲", "5×60 s ▲"]),
    ("Balance (Wed + daily)", ["One leg, hands hovering 3×30 s", "One leg + clock reach", "Heel-to-toe walk 2 fwd + backward walk 2, hand on counter", "One leg on a folded towel, at counter", "Cloud hands with side steps 2 min", "All of the above, 2 rounds"]),
    ("Walking (most days)", ["45 min brisk", "45 min, hills", "50 min, 5×2 min fast", "50 min, hills", "60 min", "60 min, hills"]),
   ]),
}


def track_page(tr):
    p = PLAN[tr]
    head = "".join(f"<th>{ph}</th>" for ph in PHASES)
    rows = "\n".join(f"<tr><td><strong>{mv}</strong></td>" + "".join(f"<td>{d}</td>" for d in ds) + "</tr>" for mv, ds in p["rows"])
    return f"""
<section class="pg" markdown="1">

# {tr} track: your 12-week wall plan

**{p['desc']}** Mon strength · Tue mobility · Wed balance · Thu strength · Fri breath · Sat walk · Sun rest. ★ = retest week. ▲ = advanced. Move up when every rep felt easy two sessions in a row; move down any day.

<table class="plan"><thead><tr><th>Move</th>{head}</tr></thead><tbody>
{rows}
</tbody></table>

</section>
"""


def retest_md():
    tests = ["1. Chair stands in 30 s (write H if hands used)", "2. Balance: last stage held 10 s (0–4)", "3. Arm curls in 30 s (what I lifted: ____)",
             "4. Step test: right-knee lifts in 2 min", "5. Sit-and-reach, inches (+/−)", "6. Timed Up and Go, seconds (12+ = tell your doctor)"]
    trs = "\n".join(f"<tr><td>{t}</td><td></td><td></td><td></td><td></td></tr>" for t in tests)
    mid = "".join(f"<tr><td>{b}</td><td>{MID['W'][i]}</td><td>{MID['M'][i]}</td><td>{CHAIR['W'][i]}</td><td>{CHAIR['M'][i]}</td></tr>" for i, b in enumerate(BANDS))
    bal = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in BAL)
    # blank chart as SVG
    W, H = 900, 420
    xs = [140, 390, 640, 860]
    grid = "".join(f'<line x1="120" y1="{30+i*48}" x2="880" y2="{30+i*48}" stroke="#16120E" stroke-width="1"/>' for i in range(8))
    labels = "".join(f'<text x="{x}" y="{400}" font-size="18" text-anchor="middle" fill="#16120E" font-family="Atkinson">{t}</text>' for x, t in zip(xs, ["Start", "Week 4", "Week 8", "Week 12"]))
    vlines = "".join(f'<line x1="{x}" y1="30" x2="{x}" y2="366" stroke="#1F5A46" stroke-width="2"/>' for x in xs)
    ylab = '<text x="20" y="190" font-size="18" fill="#16120E" font-family="Atkinson">Write</text><text x="20" y="212" font-size="18" fill="#16120E" font-family="Atkinson">ages</text><text x="20" y="234" font-size="18" fill="#16120E" font-family="Atkinson">here</text>'
    svg = f'<svg width="100%" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="{W}" height="{H}" fill="#FFFFFF"/>{grid}{vlines}{labels}{ylab}</svg>'
    return f"""
<section class="pg" markdown="1">

# Monthly Strength Age retest

Start, then end of weeks 4, 8 and 12. Same chair, shoes, time of day and curl weight. Instructions: the 7-Day Strength Reset or the app. Fitness checks from senior fitness research (E49; CDC STEADI E11, E50, E51), **not a medical test**.

Name: <span class="blank"></span> Age: <span class="blank s"></span> Woman / Man

<table class="write"><thead><tr><th>Test</th><th>Start: date ______</th><th>Week 4: ______</th><th>Week 8: ______</th><th>Week 12: ______</th></tr></thead><tbody>
{trs}
<tr><td><strong>Chair points</strong> = 2.5 × (midpoint − stands), −12 to +12; hands used: at least +8</td><td></td><td></td><td></td><td></td></tr>
<tr><td><strong>Balance points</strong> (table on the next page)</td><td></td><td></td><td></td><td></td></tr>
<tr><td><strong>My Strength Age</strong> = age + chair points + balance points</td><td></td><td></td><td></td><td></td></tr>
</tbody></table>

</section>

<section class="pg" markdown="1">

# Your Strength Age chart

Put a dot for each retest and join them. It's a motivational estimate from published norms; the app version adds a few questions, so it can differ by a year or two.

{svg}

<h2 class="pb">The numbers you need</h2>

<table class="outer"><tr><td style="width:58%">
<table class="small"><thead><tr><th>Age</th><th>Women midpoint</th><th>Men midpoint</th><th>Women typical</th><th>Men typical</th></tr></thead><tbody>{mid}</tbody></table>
</td><td>
<table class="small"><thead><tr><th>Last balance position held 10 s</th><th>Points</th></tr></thead><tbody>{bal}</tbody></table>
<p class="fine">Under 60? Use 60–64. Strength Age stays within 15 years below and 20 years above your age, and never below 40. "Typical" chair stands = middle 50% for your age (E49). Below the CDC cutoffs, or a Timed Up and Go of 12 seconds or more, is worth mentioning to your doctor (E11, E51).</p>
</td></tr></table>

</section>
"""


def habits_md():
    days = "".join(f"<th>{d}</th>" for d in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    rows = "\n".join(f"<tr><td><strong>Wk {w}</strong></td>" + "<td>☐</td>" * 7 + "<td></td><td></td><td></td></tr>" for w in range(1, 13))
    return f"""
<section class="pg" markdown="1">

# Habit tracker: 12 weeks

Tick the day when you did the session. At the end of each week, write how many days you did each habit (0–7). Grace rule: a missed day is just a missed day. Don't double up; do tomorrow's session tomorrow.

<table class="habit"><thead><tr><th>Week</th>{days}<th>Protein breakfast (days)</th><th>Walk after a meal (days)</th><th>Toothbrush balance (days)</th></tr></thead><tbody>
{rows}
</tbody></table>

<p class="rule"><strong>The habits:</strong> 25–30 g protein at breakfast (kidney disease: ask your doctor for your number, E28) · a few minutes of walking after your biggest meal (E23) · heel-to-toe while you brush your teeth, hand on the sink (E13) · and call someone this week (E37).</p>

</section>
"""


INTRO_SAY = say("chang", "I'm Chang. AI character. This goes on your fridge, not in a drawer.\n\nPick your track. Do Monday and Thursday strength every week. The other days are shorter. Every four weeks, you retest and write the number down. That's the whole plan. Strong is a habit.")


def intro_md():
    return f"""
<section class="pg first" markdown="1">

# How to use your 12-week plan {{: .nobreak}}

{INTRO_SAY}

**Pick your track.** Rebuild if you need your hands to get out of a chair or use a walker. Steady if you can stand up without your hands but don't exercise. Strong if Steady is easy. Iron only if you already train. Not sure? Start one track lower.

**Why twice a week for strength.** A review of 121 trials in 6,700 older adults training 2 to 3 times a week found large gains in strength and easier chair stands (E01). The NSCA recommends 2 to 3 sessions a week, 1 to 3 sets of 6 to 12 reps, progressing gradually (E02).

**How it progresses.** Every two weeks the dose goes up a little: a rep, a set, a slower lowering, a heavier jug. Weeks 4, 8 and 12 end with your Strength Age retest.

{box("stop", "Safety, every day:", STOP + " " + EMERGENCY + " Pain rule: " + PAIN_RULE + " Chair against a wall, counter within reach, shoes on, no rugs. Sit a moment before you stand up from the floor or bed.")}

</section>
"""


def build():
    parts = [intro_md()] + [track_page(t) for t in ["Rebuild", "Steady", "Strong", "Iron"]] + [retest_md(), habits_md()]
    parts.append('<section class="pg" markdown="1">\n\n' + appendix_md(["E01", "E02", "E11", "E13", "E23", "E28", "E37", "E41", "E42", "E43", "E49", "E50", "E51"]) + "\n\n</section>")
    md = "\n\n".join(parts)
    css = """
table.plan { font-size: 12.5pt; table-layout: fixed; line-height: 1.25; margin-top: 4pt; }
section.pg h1 { font-size: 21pt; margin-bottom: 3pt; }
section.pg p { margin-bottom: 5pt; }
table.plan th { font-size: 13pt; }
table.plan td:first-child, table.plan th:first-child { width: 17%; }
table.plan td { padding: 3pt 5pt; }
table.plan th { padding: 4pt 5pt; }
table.habit { font-size: 14pt; }
table.habit td { height: 19pt; padding: 2pt 5pt; text-align: center; }
table.habit td:first-child { white-space: nowrap; }
table.habit td:first-child { text-align: left; }
.rule { font-size: 13pt; border-top: 2pt solid #1F5A46; padding-top: 6pt; }
@page { size: Letter landscape; margin: 0.45in 0.55in 0.6in 0.55in;
  @bottom-left { content: "Breathe out on the effort. Stop for chest pain, dizziness or sharp pain. Emergency: call 911."; font-family: 'Atkinson'; font-size: 12pt; color: #16120E; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font-family: 'Atkinson'; font-size: 12pt; color: #16120E; } }
table.write td { height: 21pt; padding: 3pt 6pt; }
table.outer, table.outer > tbody > tr > td { border: none; background: transparent; padding: 0 6pt 0 0; vertical-align: top; }
section.pg h1 { page-break-before: auto; }
section.pg { page-break-before: always; }
section.pg.first { page-break-before: avoid; }
"""
    cover = cover_html("Strong Years", "12-Week Printable", "Your wall plan for four levels: Rebuild, Steady, Strong and Iron.<br>Monthly Strength Age retest sheet and habit tracker.",
                       "From Chang Yin, for your fridge.", DISCLOSURE, wide=True)
    out_pdf = os.path.join(PRODUCTS, "twelve_week_printable.pdf")
    out_md = os.path.join(PRODUCTS, "twelve_week_printable.md")
    render(md, out_pdf, NAME, cover=cover, out_md=out_md, extra_css=css,
           md_header="<!-- Source for the 12-Week Strong Years Printable. Generated by products/_build/build_wallplan.py. Landscape Letter. -->")
    return out_pdf


if __name__ == "__main__":
    print(build())
