"""The six 12-week Strong Years programs: programs.json, one PDF + Markdown per program, and the Gut Reset recipes
(also merged into kitchen_recipes.json)."""
import os, sys, json, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import render, cover_html, DISCLOSURE, PRODUCTS, box, say
from library import EX, STOP, EMERGENCY, PAIN_RULE, STAND_SLOW
from evidence import appendix_md
import build_sessions as BS
import build_kitchen as BK
from sessions_spec import SESSIONS
import sessions_spec2  # noqa: F401  (registers DP15–30)
from programs_spec import PROGRAMS, GUT_WEEKS
from gut_recipes import G
from recipes import R
from nutrition import calc

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAYNAME = dict(Mon="Monday", Tue="Tuesday", Wed="Wednesday", Thu="Thursday", Fri="Friday", Sat="Saturday", Sun="Sunday")
DP = {s["n"]: s for s in SESSIONS}
POOL = {}
for s in SESSIONS:
    POOL.setdefault(s["type"], []).append(s["n"])

RED_FLAGS = ("Not for exercise. For your doctor, today: chest pain or pressure; fainting; sudden weakness or numbness in the face, arm or leg; "
             "trouble speaking; a sudden severe headache; new confusion; one calf that is swollen, red and painful; a hot, swollen joint; night pain that "
             "wakes you and doesn't change with position; fever with back pain; loss of bladder or bowel control or numbness in the saddle area; "
             "a fall where you hit your head (especially on blood thinners). " + EMERGENCY)

PROGRESSION = {
    1: "Doses as written in the session. Learn the moves. Stop each set with one or two good reps left in the tank.",
    2: "Add 1–2 reps per set (never past 12). Holds up 5 seconds (never past 30).",
    3: "Where every rep felt easy two sessions in a row, use the Harder version or a heavier jug. Otherwise repeat week 2.",
    4: "Easy week: same moves, one set fewer. Then do your checkpoint at the weekend.",
}
PHASE_NAME = {1: "Foundation", 2: "Build", 3: "Strengthen"}

# ------------------------------------------------------------------ gut recipes into the kitchen engine
for r in G:
    BK.NUT[r["id"]] = calc(r)
    BK.BYID[r["id"]] = r
BK.SHOP.update({
    170285: ("Bread & grains", "Pearled barley (dry)", "barley", 0, ""),
    175238: ("Pantry", "Low-sodium black beans", "unit", 258, "can (15 oz)"),
    168460: ("Produce", "Soybean sprouts", "unit", 340, "bag (12 oz)"),
    174299: ("Pantry", "Black soybeans, cooked or canned", "unit", 258, "can (15 oz)"),
    174256: ("Pantry", "Peeled split mung beans (dry)", "oz", 28.35, ""),
    171955: ("Meat & fish", "Cod fillets", "lb", 454, ""),
    169994: ("Produce", "Garlic chives or chives", "unit", 113, "bunch"),
    168482: ("Produce", "Sweet potatoes", "count", 180, "medium"),
    168484: ("Produce", "Sweet potatoes", "count", 180, "medium"),
    169988: ("Produce", "Celery", "unit", 450, "bunch"),
    169979: ("Produce", "Napa cabbage", "lb", 454, ""),
    168893: ("Bread & grains", "Whole-wheat flour", "cup", 120, ""),
    169228: ("Produce", "Eggplant", "lb", 454, ""),
    168398: ("Frozen", "Corn", "unit", 454, "bag (16 oz)"),
    174258: ("Pantry", "Sweet potato glass noodles (dangmyeon)", "oz", 28.35, ""),
    170108: ("Produce", "Red bell pepper", "count", 119, ""),
    169941: ("Produce", "Fuyu persimmons (or ripe pears)", "count", 168, ""),
    168162: ("Pantry", "Prunes", "oz", 28.35, ""),
})
_orig_fmt = BK.fmt_qty


def fmt_qty(src, g):
    if BK.SHOP[src][2] == "barley":
        cups = math.ceil(g / 157 / 3.5 * 4) / 4
        return f"{cups:g} cups dry (makes about {g/157:.0f} cups cooked)"
    return _orig_fmt(src, g)


BK.fmt_qty = fmt_qty
BK.PANTRY.append("oyster sauce")


def staples_for(w):
    ings = []
    if w >= 2:
        ings.append(("", "kiwi", 28 * 75, 168153))
    if w >= 5:
        ings.append(("", "edamame", 14 * 78, 168411))
    if w >= 6:
        ings.append(("", "yogurt", 14 * 113, 170894))
    if w >= 7:
        ings += [("", "prunes", 14 * 47.5, 168162), ("", "flax", 14 * 7, 169414)]
    if w >= 9:
        ings.append(("", "oats", 4 * 40, 173904))
    return dict(id=f"ST{w}", ings=ings)


# ------------------------------------------------------------------ build program sessions + week plans
def build_program(P):
    out = dict(id=P["id"], name=P["name"], promise=P["promise"], who=P["who"], ask_first=P["ask_first"], equipment=P["equipment"],
               evidence=P["evidence"], length_weeks=12, checkpoints=[dict(name=a, how=b, evidence=c) for a, b, c in P["checkpoints"]],
               safety=dict(stop_rule=STOP, emergency=EMERGENCY, pain_rule=PAIN_RULE, stand_slowly=STAND_SLOW, red_flags=RED_FLAGS),
               release_note="All 12 weeks are complete and available on enrolment (scripts); videos render per VIDEO_PRODUCTION_QUEUE.json.")
    if P["id"] == "GUT":
        return build_gut(P, out)
    sessions = {}
    for key, spec in P["sessions"].items():
        sp = dict(n=0, weekday=f"Program day {key[0]}", type=f"{P['name']} program", title=spec["title"], set=spec["set"], wardrobe=spec["wardrobe"],
                  evidence=P["evidence"], swaps=dict(sore_knee="Use the Rebuild version of any standing leg move; skip floor practice and stairs today.",
                                                     sore_back="Seated versions of hinges and carries; keep every bend long-backed.",
                                                     low_energy="Do the warm-up, the first two blocks and the cool-down."),
                  segments=spec["segments"])
        S = BS.build_session(sp, sid=f"{P['id']}-{key}", week=int(key[1]))
        S["program"] = P["id"]
        S["phase"] = int(key[1])
        S["phase_name"] = PHASE_NAME[int(key[1])]
        assert 7.5 * 60 <= S["duration_s"] <= 12.5 * 60, (S["id"], S["duration"])
        sessions[key] = S
    weeks = []
    for w in range(1, 13):
        phase = (w - 1) // 4 + 1
        wk_in = (w - 1) % 4 + 1
        days = {}
        for i, d in enumerate(DAYS):
            role = P["week_days"][d]
            if role in ("A", "B"):
                S = sessions[f"{role}{phase}"]
                days[d] = dict(session=S["id"], title=S["title"], kind="program")
            else:
                pool = POOL[role]
                n = pool[(w - 1 + (1 if role == "Strength" and d == "Thu" else 0)) % len(pool)]
                days[d] = dict(session=f"DP{n:02d}", title=DP[n]["title"], kind="daily_practice", type=role)
        wk = dict(week=w, phase=phase, phase_name=PHASE_NAME[phase], deload=(wk_in == 4), checkpoint=(wk_in == 4),
                  progression=PROGRESSION[wk_in], days=days)
        if "walking" in P:
            wk["walking_goal"] = P["walking"][w - 1]
        if "steps" in P:
            wk["daily_steps_goal"] = P["steps"][w - 1]
        if P["id"] == "GRP":
            wk["daily_add_on"] = "2-minute hand routine every morning: 5 fist-flat-hook rounds and 2 rounds of thumb touches each hand."
        weeks.append(wk)
    out["weekly_structure"] = {d: P["week_days"][d] for d in DAYS}
    out["weeks"] = weeks
    out["sessions"] = list(sessions.values())
    out["checkpoint_weeks"] = [0, 4, 8, 12]
    return out


def gut_lesson(wk):
    rid = wk["recipes"][0]
    r = BK.BYID[rid]
    steps = r["steps"]
    segs = [dict(name="Welcome", kind="intro", secs=30, tracks=None, speaker="SUN", sun=[],
                 vo=[f"Week {wk['w']} of Gut Reset. This week: {wk['theme'].lower()}.", "I'm Sun Yoon. AI character. Real recipes, real numbers from the USDA.",
                     "Not medical advice. Blood in your stool, black stool, weight loss you can't explain, or bad belly pain: no soup for that. Call your doctor. Today."],
                 ost=[f"Gut Reset · Week {wk['w']}", "Not for red-flag symptoms: call your doctor"]),
            dict(name="Why this week", kind="teach", secs=60, tracks=None, speaker="SUN", sun=[],
                 vo=[wk["lesson"], "Go up slowly and drink water, or you'll feel it."], ost=[wk["rung"]]),
            dict(name=f"Cook with me: {r['name']}", kind="kitchen_demo", secs=max(150, min(260, 28 * len(steps) + 30)), tracks=None, speaker="SUN", sun=[],
                 vo=[r["intro"]] + steps + ["Grams, not vibes. The numbers are on the recipe card."], ost=[r["name"]]),
            dict(name="Your habit this week", kind="teach", secs=45, tracks=None, speaker="SUN", sun=[],
                 vo=[wk["habit"], "Write it on the fridge."], ost=["This week's habit"]),
            dict(name="Who should skip or ask first", kind="teach", secs=35, tracks=None, speaker="SUN", sun=[],
                 vo=[" ".join(BK.cautions(r)) or "Allergies: check the ingredient list.", "Taking medicines? Food doesn't replace them. Nothing here asks you to change them."],
                 ost=["Who should skip or ask first"]),
            dict(name="Close", kind="close", secs=25, tracks=None, speaker="SUN", sun=[],
                 vo=["Two more recipes in your plan this week. Shopping list is in the app.", "Now go eat."], ost=["Grocery list in the app"])]
    sp = dict(n=0, weekday="Sunday", type="Gut Reset kitchen lesson", title=wk["theme"], set="SET-KITCHEN", wardrobe="S-KITCHEN",
              evidence=wk["evidence"] + ["E52", "E54"], swaps=dict(sore_knee="Cook sitting on a stool.", sore_back="Cook sitting on a stool.", low_energy="Make the simplest recipe this week."),
              segments=segs)
    S = BS.build_session(sp, sid=f"GUT-W{wk['w']:02d}", week=wk["w"])
    S["has_movement"] = False
    S["movement_tags"] = []
    S["caption_movement_addon"] = None
    S["program"] = "GUT"
    return S


def build_gut(P, out):
    weeks, lessons = [], []
    for wk in GUT_WEEKS:
        L = gut_lesson(wk)
        lessons.append(L)
        rec = [dict(id=x, name=BK.BYID[x]["name"], per_serving={k: round(v, 1) for k, v in BK.NUT[x][0].items()}) for x in wk["recipes"] + wk["extra"]]
        weeks.append(dict(week=wk["w"], theme=wk["theme"], rung=wk["rung"], habit=wk["habit"], deload=bool(wk.get("checkpoint")) and wk["w"] < 12,
                          checkpoint=bool(wk.get("checkpoint")), lesson=L["id"], featured_recipes=wk["recipes"], optional_recipes=wk["extra"], recipes=rec,
                          daily_practice="Your Strong Years daily session as usual (any level).", evidence=wk["evidence"]))
    out["weeks"] = weeks
    out["sessions"] = lessons
    out["checkpoint_weeks"] = [0, 4, 8, 12]
    out["recipes_added"] = [r["id"] for r in G]
    return out


# ------------------------------------------------------------------ Markdown / PDF
def plan_table(prog):
    head = "<tr><th>Week</th><th>Phase</th>" + "".join(f"<th>{d}</th>" for d in DAYS) + "</tr>"
    rows = []
    for wk in prog["weeks"]:
        cells = "".join(f"<td><strong>{wk['days'][d]['session']}</strong></td>" if wk["days"][d]["kind"] == "program" else f"<td>{wk['days'][d]['session']}</td>" for d in DAYS)
        rows.append(f"<tr><td>{wk['week']}{' ★' if wk['checkpoint'] else ''}</td><td>{wk['phase_name']}</td>{cells}</tr>")
    return (f'<table class="small plan"><thead>{head}</thead><tbody>' + "".join(rows) + "</tbody></table>\n\n"
            "★ = easy week, then checkpoint. **Bold** = program session. DP = Daily Practice session number (sessions.json).\n")


def checkpoint_md(prog):
    head = "<tr><th>Checkpoint</th><th>How</th><th>Start</th><th>Week 4</th><th>Week 8</th><th>Week 12</th></tr>"
    rows = "".join(f"<tr><td><strong>{c['name']}</strong> ({c['evidence']})</td><td>{c['how']}</td><td></td><td></td><td></td><td></td></tr>" for c in prog["checkpoints"])
    return f"""
# Your checkpoints

Start, then the end of weeks 4, 8 and 12. Same chair, same shoes, same time of day. These are fitness checks from published research, **not medical tests**.

<table class="write small"><thead>{head}</thead><tbody>{rows}</tbody></table>
"""


def program_md(P, prog):
    lead = "sun" if P["id"] == "GUT" else "chang"
    who_line = ("I'm Sun Yoon. AI character. I cook, I read the studies, and I don't lie to you. " if lead == "sun"
                else "I'm Chang. AI character. Twelve weeks, one program, done properly. ")
    intro = say(lead, who_line + P["promise"] + "\n\nA little more, slowly. That's the whole method.")
    parts = [f"""
# {P['name']}: how it works {{: .nobreak}}

{intro}

**Who it's for.** {P['who']}

{box("stop", "Ask your doctor first if:", P['ask_first'])}

**What you need.** {P['equipment']}

{box("stop", "Every day:", STOP + " " + EMERGENCY + " Pain rule (E41): " + PAIN_RULE)}
"""]
    if P["id"] != "GUT":
        wd = " · ".join(f"{d}: {'program session ' + r if r in ('A', 'B') else r.lower()}" for d, r in P["week_days"].items())
        extra = ""
        if "walking" in P:
            extra += "\n**Walking goal each week:** " + " · ".join(f"wk {i+1}: {x}" for i, x in enumerate(P["walking"])) + "\n"
        if "steps" in P:
            extra += "\n**Daily steps goal each week** (count your baseline in week 1; E22): " + " · ".join(f"wk {i+1}: {x}" for i, x in enumerate(P["steps"])) + "\n"
        if P["id"] == "GRP":
            extra += "\n**Every morning:** a 2-minute hand routine: 5 rounds of fist-flat-hook and 2 rounds of thumb touches each hand.\n"
        parts.append(f"""
## Your week

{wd}. Program sessions are marked in **bold** in the plan; the other days use your Strong Years Daily Practice sessions (DP numbers).
{extra}
## How it progresses

Three 4-week phases: **Foundation** (weeks 1–4, A1/B1), **Build** (weeks 5–8, A2/B2) and **Strengthen** (weeks 9–12, A3/B3).

| Week in each phase | Rule |
|---|---|
| 1st | {PROGRESSION[1]} |
| 2nd | {PROGRESSION[2]} |
| 3rd | {PROGRESSION[3]} |
| 4th (easy week) | {PROGRESSION[4]} |

**Levels.** Every session has four versions: Rebuild (chair-based), Steady, Strong and Iron. Move up only when every rep felt easy two sessions in a row. Move down any day. **Advanced** doses are never a starting point.

## The 12-week plan

{plan_table(prog)}

{box("stop", "Red flags:", RED_FLAGS)}
""")
        parts.append(checkpoint_md(prog))
        parts.append("# The program sessions\n\nFull follow-along scripts for the six program sessions. The same content is in programs.json for the app and video pipeline.\n")
        for S in prog["sessions"]:
            md = BS.session_md(S)
            md = re.sub(r"^# Session 0 · Program day [AB]: ", f"# {S['id']} · Phase {S['phase']} ({S['phase_name']}): ", md, count=1)
            parts.append(md)
    else:
        rows = ["| Week | Theme | Rung | Featured recipes |", "|---|---|---|---|"]
        for wk in prog["weeks"]:
            rows.append(f"| {wk['week']}{' (easy + checkpoint)' if wk['checkpoint'] else ''} | {wk['theme']} | {wk['rung']} | " + ", ".join(BK.BYID[x]['name'] for x in wk['featured_recipes']) + " |")
        parts.append("## The 12-week plan\n\nEvery week: your daily Strong Years session as usual, a Sunday kitchen lesson with Sun, three featured recipes (plus one optional), one habit, and a grocery list for two.\n\n" + "\n".join(rows) + "\n\n" + box("stop", "Red flags:", "blood in the stool or black stool, vomiting blood, unexplained weight loss, severe belly pain, fever with belly pain, or a change in bowel habits lasting more than a few weeks: no soup for that. Call your doctor. Today. " + EMERGENCY))
        parts.append(checkpoint_md(prog))
        for wk, spec in zip(prog["weeks"], GUT_WEEKS):
            lines = [f"# Week {wk['week']}: {wk['theme']}\n", say("sun", spec["lesson"]),
                     f"**This week's habit:** {wk['habit']}\n", f"**Fiber ladder:** {wk['rung']}.\n",
                     "| Recipe | Protein | Fiber | Calories |", "|---|---|---|---|"]
            for rr in wk["recipes"]:
                ps = rr["per_serving"]
                opt = " (optional)" if rr["id"] in spec["extra"] else ""
                lines.append(f"| {rr['name']}{opt} | {round(ps['protein_g'])} g | {ps['fiber_g']} g | {BK.rnd(ps['kcal'])} |")
            cook = {x: (2 if BK.BYID[x]["serves"] == 1 else 1) for x in spec["recipes"]}
            st = staples_for(wk["week"])
            BK.BYID[st["id"]] = st
            if st["ings"]:
                cook[st["id"]] = 1
            gl = BK.grocery_md(dict(n=wk["week"], title=wk["theme"], note="Featured recipes for two, plus the week's fiber-ladder staples.",
                                    menu=[], cook=cook))
            gl = gl.split("### Shopping list", 1)[1]
            lines.append("\n### Shopping list" + gl)
            parts.append("\n".join(lines))
        parts.append("# The new recipes\n\n26 recipes written for Gut Reset. Numbers are per serving, calculated from USDA FoodData Central (E52); the ingredient-by-ingredient tables are at the back.\n")
        for r in G:
            parts.append(BK.recipe_md(r))
        parts.append("# The Sunday kitchen lessons\n\nTwelve short lessons with Sun. Full scripts; the same content is in programs.json.\n")
        for S in prog["sessions"]:
            md = BS.session_md(S)
            md = re.sub(r"^# Session 0 · Sunday: ", f"# {S['id']} · ", md, count=1)
            parts.append(md)
        saveR = BK.R
        BK.R = G
        m = BK.method_md().replace("# How we calculated the numbers", "# How we calculated the recipe numbers")
        BK.R = saveR
        parts.append(m)
    parts.append(appendix_md(prog["evidence"] + (["E41", "E42", "E43"] if P["id"] != "GUT" else [])))
    return "\n\n".join(parts)


def build():
    progs = [build_program(P) for P in PROGRAMS]
    json.dump(dict(version="2026-09-30", disclosure=BS.FOOTER, tracks=BS.TRACK_DESC,
                   daily_practice_library="sessions.json (DP01–DP30, RT01)", programs=progs),
              open(os.path.join(PRODUCTS, "programs.json"), "w"), indent=1, ensure_ascii=False)
    # merged recipe file for the app
    data = json.load(open(os.path.join(PRODUCTS, "kitchen_recipes.json")))
    data = [d for d in data if not d["id"].startswith("G")]
    for d in data:
        d.setdefault("collection", "strong_kitchen")
    for r in G:
        per, tot, rows = BK.NUT[r["id"]]
        data.append(dict(id=r["id"], collection="gut_reset", name=r["name"], native=r["native"], category=r["cat"], serves=r["serves"],
                         minutes_active=r["active"], minutes_total=r["total"], per_serving={k: round(v, 1) for k, v in per.items()},
                         ingredients=[dict(amount=a, item=t, grams=g, source=(f"FDC {s}" if isinstance(s, int) else s)) for a, t, g, s in r["ings"]],
                         steps=r["steps"], soft_food=r["soft"], storage=r["store"], cautions=BK.cautions(r)))
    json.dump(data, open(os.path.join(PRODUCTS, "kitchen_recipes.json"), "w"), indent=1, ensure_ascii=False)
    css = """
.recipe { page-break-before: always; }
table.nut { width: 100%; border-collapse: separate; border-spacing: 6pt 0; margin: 4pt -6pt 2pt -6pt; }
table.nut td { background: #FFFFFF; border: 2pt solid #1F5A46; border-radius: 8pt; text-align: center; padding: 6pt 4pt; font-size: 14pt; width: 25%; }
table.nut .n { font-family: 'Fraunces'; font-weight: 700; font-size: 20pt; color: #B3311C; }
.twocol ul { list-style: none; padding-left: 0; }
table.ros td, table.ros th { font-size: 12pt; }
table.plan td, table.plan th { white-space: nowrap; padding: 4pt 5pt; }
table.script td:nth-child(1) { width: 8%; } table.script td:nth-child(2) { width: 9%; } table.script td:nth-child(3) { width: 55%; }
"""
    outs = []
    for P, prog in zip(PROGRAMS, progs):
        md = program_md(P, prog)
        slug = re.sub(r"[^a-z0-9]+", "_", P["name"].lower()).strip("_")
        lead = "Sun Yoon's" if P["id"] == "GUT" else "Strong Years program"
        title = P["name"].replace(" with Sun Yoon", "")
        cover = cover_html(lead, title, P["promise"] + "<br>12 weeks · four levels · every session scripted.", "Chang Yin & Sun Yoon", DISCLOSURE)
        out_pdf = os.path.join(PRODUCTS, "programs", f"program_{slug}.pdf")
        os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
        render(md, out_pdf, P["name"], cover=cover, out_md=out_pdf[:-4] + ".md", extra_css=css,
               md_header=f"<!-- Source for the {P['name']} 12-week program. Generated by products/_build/build_programs.py. -->")
        outs.append(out_pdf)
    return outs, progs


if __name__ == "__main__":
    outs, progs = build()
    from common import page_count
    for o in outs:
        print(page_count(o), o)
    for p in progs:
        print(p["id"], len(p["sessions"]), [s["duration"] for s in p["sessions"]])
