"""Product 4: Daily Practice Sessions 1–30 — follow-along scripts (Markdown + PDF) and sessions.json for the app/video pipeline."""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import render, cover_html, DISCLOSURE, PRODUCTS, box, say
from library import EX, STOP, EMERGENCY, PAIN_RULE, STAND_SLOW, CONTRA, EASY_SHORT
from sessions_spec import SESSIONS
import sessions_spec2  # appends sessions 15–30
from retest_spec import RETEST
from evidence import appendix_md

NAME = "Daily Practice Sessions 1–30"
TRACKS = ["rebuild", "steady", "strong", "iron"]
TRACK_NAME = dict(rebuild="Rebuild", steady="Steady", strong="Strong", iron="Iron")
TRACK_DESC = dict(rebuild="Chair-based. Seated, or standing with both hands on the counter and the chair right behind you.",
                  steady="Standard version with counter or wall support.",
                  strong="Added load, slower lowering, less hand support.",
                  iron="For people who already train. Heavier, longer, some moves labelled advanced.")
FOOTER = ("Chang & Sun are AI characters. Content is educational, built on published research, and not medical advice. "
          "Check with your doctor before starting new exercise.")
MOVEMENT_ADDON = "Go at your own pace. Hold a counter or chair. Stop if you feel chest pain, dizziness, or sharp pain."
SUPPORT_WORDS = re.compile(r"\b(chair|counter|wall|rail|fence|sit|seated|sitting|hold|hands? on|bed|bench)\b", re.I)
BREATH_WORDS = re.compile(r"breath|breathe|sigh|exhale|count out loud", re.I)
SEATED = {"ankle_pumps", "seated_march", "shoulder_rolls", "neck_nods", "chin_tuck", "chest_lift", "seated_rotation", "hamstring_seated",
          "figure4", "towel_row", "towel_wring", "bottle_curl", "seated_press", "seated_chest_press", "seated_knee_ext", "seated_hinge",
          "cyclic_sigh", "breath_46", "bed_bridge"}
SEGMENT_EVIDENCE = {"Cloud hands": ["E17"], "Cyclic sighing": ["E18"], "4-6 breathing": ["E19"]}
EXTRA_EV = {1: ["E01", "E02", "E47"], 2: ["E30", "E19"], 3: ["E13", "E09"], 4: ["E39", "E40"], 5: ["E17", "E18", "E19"],
            6: ["E22", "E10", "E23"], 7: ["E41", "E46"], 8: ["E01", "E02"], 9: ["E30"], 10: ["E13", "E17"], 11: ["E39", "E40"],
            12: ["E17", "E29"], 13: ["E22", "E23"], 14: ["E41", "E46"]}


def mmss(s):
    return f"{s // 60}:{s % 60:02d}"


def short_easier(eid):
    if eid in EASY_SHORT:
        return EASY_SHORT[eid]
    t = EX[eid]["easier"]
    t = re.split(r"[.;]", t)[0]
    t = re.split(r", or ", t)[0]
    words = t.split()
    return " ".join(words[:8])


BED = {"bed_bridge", "pelvic_tilt_bed", "clam_bed", "knee_rock_bed"}
TABLE = {"finger_spread", "fist_flat", "thumb_touch", "wrist_curl", "jar_twist", "hand_stretch", "ball_squeeze", "book_pinch"}
BAND = {"band_row", "band_pull_apart", "pallof_press"}


def support_line(eid):
    if eid in BED:
        return "On your bed. Sit down first, then lie back slowly."
    if eid in TABLE:
        return "Sit at the table. Forearm resting on it."
    if eid in BAND:
        return "Sit or stand with the chair behind you. Check the band first."
    if eid == "stair_climb":
        return "Hand on the rail."
    if eid in ("suitcase_carry",):
        return "Clear path. Free hand trails along the counter."
    if eid == "floor_practice":
        return "Hand on the chair seat. Someone else is home."
    if eid in SEATED:
        return "Sit tall. Chair against the wall."
    if eid in ("wall_pushup", "wall_slide", "wall_sit_high"):
        return "Wall in front of you or behind you. Chair nearby."
    if eid == "step_up":
        return "Hand on the rail."
    if eid == "carry":
        return "Clear path. Walk along the counter or a hallway wall."
    if eid == "walk":
        return "Good shoes. Cane or walker if you use one."
    return "Hand on the counter. Chair behind you."


def version_text(eid, version):
    e = EX[eid]
    if version == "easier":
        return e["easier"]
    if version == "harder":
        return e["harder"]
    return "Main version: " + " ".join(e["steps"][:2])


TYPE_EV = {"Strength": ["E01", "E02"], "Mobility": ["E30"], "Balance": ["E13"], "Breath + qigong": ["E17", "E18", "E19"],
           "Walk-and-talk": ["E22", "E23"], "Rest + stretch": ["E41", "E46"]}


def auto_vo(eid):
    e = EX[eid]
    first = e["steps"][0]
    return [support_line(eid), first] + e["cues"][:2] + [e["breathe"]]


def build_session(sp, sid=None, week=None):
    t = 0
    segs = []
    ev = set(EXTRA_EV.get(sp["n"], TYPE_EV.get(sp.get("type"), []))) if sid is None else set(sp.get("evidence", []))
    tags = set()
    for i, s in enumerate(sp["segments"], 1):
        start, end = t, t + s["secs"]
        t = end
        beats = []
        vo = list(s["vo"])
        if not vo and s["tracks"]:
            vo = auto_vo(s["tracks"]["steady"][0])
        tracks = {}
        main_ex = None
        if s["tracks"]:
            for tr in TRACKS:
                eid, ver, dose = s["tracks"][tr]
                e = EX[eid]
                adv = "advanced" in dose.lower()
                tracks[tr] = dict(exercise=eid, name=e["name"], version=ver, dose=dose, advanced=adv,
                                  how=version_text(eid, ver), cues=e["cues"], breathe=e["breathe"],
                                  safety=e["safety"], equipment=e["equip"])
                ev.update(e["ev"])
                tags.update(e["tags"])
            main_ex = s["tracks"]["steady"][0]
            # M-01 support cue in first 10 s; M-04 breathing cue
            if s["kind"] in ("warmup", "block", "cooldown") and not SUPPORT_WORDS.search(vo[0] if vo else ""):
                vo.insert(0, support_line(main_ex))
            if not any(BREATH_WORDS.search(x) for x in vo):
                vo.append(EX[main_ex]["breathe"])
        ev.update(SEGMENT_EVIDENCE.get(s["name"], []))
        n = len(vo)
        span = max(1, int(s["secs"] * 0.8))
        for k, line in enumerate(vo):
            off = 0 if k == 0 else min(s["secs"] - 3, 3 + int(k * span / max(1, n)))
            beats.append(dict(t=mmss(start + off), speaker=s.get("speaker", "CHANG"), vo=line, ost=""))
        # On-screen text
        ost = list(s["ost"])
        if main_ex:
            steady_dose = s["tracks"]["steady"][2]
            beats[0]["ost"] = s["name"]
            ost.insert(0, f"Easier: {short_easier(main_ex)}")
            if any(tracks[tr]["advanced"] for tr in TRACKS):
                ost.append("Advanced (Iron): not your starting point")
        # counting beat for rep-based blocks
        if main_ex and s["kind"] == "block" and re.search(r"\bsets? of\b|\breps\b", s["tracks"]["steady"][2]):
            beats.append(dict(t=mmss(start + int(s["secs"] * 0.45)), speaker="CHANG", vo="One... two... breathe out... three... slow down... four.", ost=""))
        for k, line in enumerate(s["sun"]):
            beats.append(dict(t=mmss(max(start, end - 8 - 4 * k)), speaker="SUN", vo=line, ost=""))
        # spread extra ost onto beats that have none
        free = [b for b in beats if not b["ost"]]
        for k, o in enumerate(ost):
            if k < len(free):
                free[k]["ost"] = o
            else:
                beats[-1]["ost"] = (beats[-1]["ost"] + " | " + o).strip(" |")
        beats.sort(key=lambda b: (int(b["t"].split(":")[0]) * 60 + int(b["t"].split(":")[1])))
        safety = []
        if main_ex:
            for tr in TRACKS:
                for x in tracks[tr]["safety"]:
                    if x not in safety:
                        safety.append(x)
        shot_set = sp["set"]
        segs.append(dict(n=i, id=f"{sid or ('DP%02d' % sp['n'])}-S{i:02d}", name=s["name"], kind=s["kind"], start=mmss(start), end=mmss(end),
                         duration_s=s["secs"], tracks=tracks or None, beats=beats, on_screen=ost, safety_callouts=safety,
                         track_panel=({TRACK_NAME[tr]: tracks[tr]["dose"] for tr in TRACKS} if tracks else None),
                         regression=(EX[main_ex]["easier"] if main_ex else None), progression=(EX[main_ex]["harder"] if main_ex else None),
                         shot=f"{shot_set} | {sp['wardrobe']} | {s['name']} | handheld eye-level, full body for movement, medium for talk"))
    speakers = sorted({s.get("speaker", "CHANG") for s in sp["segments"]} | ({"SUN"} if any(s["sun"] for s in sp["segments"]) else set()))
    return dict(id=sid or f"DP{sp['n']:02d}", day_number=sp["n"], week=week or (sp["n"] - 1) // 7 + 1, weekday=sp["weekday"], type=sp["type"],
                title=sp["title"], duration_s=t, duration=mmss(t), set=sp["set"], wardrobe=sp["wardrobe"], speakers=speakers,
                has_movement=True, movement_tags=sorted(tags), evidence=sorted(ev - {"E12", "E14", "E36"}, key=lambda x: (int(re.sub(r'\D', '', x)), x)),
                persistent_on_screen=["AI character (top-left pill, white on dark, 70% opacity)", "Stop if chest pain, dizziness or sharp pain (first 30 s and before each hard block)"],
                tracks=TRACKS, track_descriptions=TRACK_DESC, gentle_day_swaps=sp["swaps"],
                safety_global=dict(stop_rule=STOP, emergency=EMERGENCY, pain_rule=PAIN_RULE, stand_slowly=STAND_SLOW),
                caption_movement_addon=MOVEMENT_ADDON, caption_footer=FOOTER, segments=segs)


def session_md(S):
    if not S.get("has_movement", True):
        out = [f"# Session {S['day_number']} · {S['weekday']}: {S['title']}\n",
               f"| Type | Length | Set | Wardrobe | Voices |", "|---|---|---|---|---|",
               f"| {S['type']} | {S['duration']} | {S['set']} | {S['wardrobe']} | {', '.join(x.title() for x in S['speakers'])} |\n",
               box("note", "On screen the whole lesson:", "the \"AI character\" corner tag. Recipe numbers as a card during the cooking segment."),
               "## Run of show\n",
               '<table class="small ros"><thead><tr><th>Time</th><th>Segment</th><th>Kind</th></tr></thead><tbody>']
        for g in S["segments"]:
            out.append(f"<tr><td>{g['start']}–{g['end']}</td><td><strong>{g['name']}</strong></td><td>{g['kind'].replace('_', ' ')}</td></tr>")
    else:
        out = [f"# Session {S['day_number']} · {S['weekday']}: {S['title']}\n",
               f"| Type | Length | Set | Wardrobe | Voices |", "|---|---|---|---|---|",
               f"| {S['type']} | {S['duration']} | {S['set']} | {S['wardrobe']} | {', '.join(x.title() for x in S['speakers'])} |\n",
               box("stop", "On screen the whole session:", "the \"AI character\" corner tag. In the first 30 seconds and before each hard block: \"Stop if chest pain, dizziness or sharp pain.\""),
               box("note", "Gentle-day swaps (the sore knee / sore back / low energy button):",
                   f"**Sore knee:** {S['gentle_day_swaps']['sore_knee']} **Sore back:** {S['gentle_day_swaps']['sore_back']} **Low energy:** {S['gentle_day_swaps']['low_energy']}"),
               "## Run of show\n",
               '<table class="small ros"><thead><tr><th>Time</th><th>Segment</th><th>Rebuild</th><th>Steady</th><th>Strong</th><th>Iron</th></tr></thead><tbody>']
        for g in S["segments"]:
            if g["tracks"]:
                base = g["tracks"]["steady"]["name"]
                cells = ""
                for tr in TRACKS:
                    x = g["tracks"][tr]
                    pre = "" if x["name"] == base else f"<em>{x['name']}:</em> "
                    cells += f"<td>{pre}{x['dose']}</td>"
                seg_label = f"<strong>{g['name']}</strong>" + (f"<br>{base}" if base.lower() != g["name"].lower() else "")
            else:
                cells = '<td colspan="4">All levels together</td>'
                seg_label = f"<strong>{g['name']}</strong>"
            out.append(f"<tr><td>{g['start']}–{g['end']}</td><td>{seg_label}</td>{cells}</tr>")
    out.append("</tbody></table>\n")
    out.append("## Script\n")
    for g in S["segments"]:
        out.append(f'<div class="seg" markdown="1">\n\n### {g["start"]}–{g["end"]} · {g["name"]}\n')
        out.append('<table class="small script"><thead><tr><th>Time</th><th>Who</th><th>Spoken</th><th>On screen</th></tr></thead><tbody>')
        for b in g["beats"]:
            out.append(f"<tr><td>{b['t']}</td><td>{b['speaker'].title()}</td><td>{b['vo']}</td><td>{b['ost']}</td></tr>")
        out.append("</tbody></table>\n")
        if g["tracks"]:
            e = EX[g["tracks"]["steady"]["exercise"]]
            out.append(f"**Cues:** {' '.join(e['cues'])} **Easier:** {g['regression']} **Harder:** {g['progression']}\n")
        if g["safety_callouts"]:
            out.append(f"**Safety callouts:** {' '.join(g['safety_callouts'])}\n")
        out.append("</div>\n")
    return "\n".join(out)


def intro_md(all_sessions):
    total = sum(s["duration_s"] for s in all_sessions)
    rows = "\n".join(f"| {s['day_number']} | {s['weekday']} | {s['type']} | {s['title']} | {s['duration']} |" for s in all_sessions)
    return f"""
# How to use these scripts {{: .nobreak}}

These are the first 30 days of the Strong Years Daily Practice: 30 follow-along sessions, plus the guided monthly retest, with Chang Yin, 8 to 12 minutes each, in the weekly rotation members see in the app. **Monday strength, Tuesday mobility, Wednesday balance, Thursday strength, Friday breath and qigong, Saturday walk-and-talk, Sunday rest and stretch.**

Each session has:

- a **run of show** with minute marks and the dose for all four levels;
- the **full script**: every spoken line for Chang (and Sun Yoon's cameos), the time it lands, and the on-screen text;
- **cues, the easier and harder version, and safety callouts** for every move;
- **gentle-day swaps** for the app's "sore knee / sore back / low energy" button.

The same content is exported as `sessions.json` for the app and the video pipeline (one object per session, one object per segment, per-level variants, beats with timestamps).

## The four levels

| Level | Who it's for |
|---|---|
| **Rebuild** | {TRACK_DESC['rebuild']} Anyone who needs their hands to get out of a chair, uses a walker, or feels unsteady. If you can't stand safely at all, do every move seated and skip the standing balance holds. |
| **Steady** | {TRACK_DESC['steady']} Most new members. |
| **Strong** | {TRACK_DESC['strong']} |
| **Iron** | {TRACK_DESC['iron']} Anything past 12 reps, 3 sets or 30-second holds is labelled **Advanced** on screen (SAFETY M-06). |

Move up a level only when a move feels easy for every rep in two sessions in a row. Moving down is always allowed, any day.

## Production rules baked into every script

- **Support cue within the first 10 seconds** of every movement (chair against the wall, counter, rail) — M-01.
- **Easier version** on screen for every movement — M-02. **Stop rule** on screen in the first 30 seconds and before hard blocks — M-03.
- **Breathing cue** in every strength move: breathe out on the effort; never "hold your breath" — M-04, E42.
- **Chang's level** demonstrations carry the label "Chang's level — not your starting point" — M-07.
- Chairs shown against a wall; balance next to a counter; shoes on; no rugs; no socks on hard floors — M-09, M-10.
- Every generated movement clip passes human form review before publishing (knees track over toes, neutral spine on hinges, chair doesn't slide) — M-08.
- The "AI character" corner tag is on screen the whole time — D-02. Caption ends with the movement add-on and the disclosure footer — D-03.

{box("stop", "Before members start:", "the app runs the safety screen (chest pain, fainting, recent surgery or fracture, a doctor's limit on activity) and routes those members to the Rebuild level with a note to show their doctor the plan (E43). " + STOP + " " + EMERGENCY + " Pain rule: " + PAIN_RULE)}

## The 30 days at a glance

| # | Day | Type | Title | Length |
|---|---|---|---|---|
{rows}

Total follow-along time across 30 days: {total // 60} minutes.
"""


def build(upto=30):
    all_s = [build_session(sp) for sp in SESSIONS]
    full = all_s
    all_s = [S for S in all_s if S["day_number"] <= upto]
    for S in all_s:
        assert 8 * 60 - 30 <= S["duration_s"] <= 12 * 60 + 30, (S["id"], S["duration"])
    rt = build_session(RETEST, sid="RT01", week=0)
    if upto == 30:
      json.dump(dict(product=NAME, version="2026-09-30", rotation=["Mon strength", "Tue mobility", "Wed balance", "Thu strength", "Fri breath + qigong", "Sat walk-and-talk", "Sun rest + stretch"],
                   tracks=TRACK_DESC, disclosure=FOOTER, sessions=full, guided_tests=[rt]),
              open(os.path.join(PRODUCTS, "sessions.json"), "w"), indent=1, ensure_ascii=False)
    intro = intro_md(all_s)
    if upto != 30:
        intro = intro.replace("the first 30 days", f"the first {upto} days").replace("30 follow-along sessions", f"{upto} follow-along sessions").replace("The 30 days at a glance", f"The {upto} days at a glance").replace("across 30 days", f"across {upto} days")
    parts = [intro] + [session_md(S) for S in all_s] + [session_md(rt).replace("# Session 0 · Any (day 30, 60, 90...):", "# Guided retest (day 30, 60, 90…):", 1)]
    ids = set(["E41", "E42", "E43", "E46"])
    for S in all_s:
        ids.update(S["evidence"])
    parts.append(appendix_md(ids, intro="Every number Chang says out loud in these scripts traces to one of these entries (EVIDENCE.md). Grade A: Cochrane review, large meta-analysis or guideline. B: single good trial or small meta-analysis. C: observational link, not cause. D: physiology, lab or label data.\n"))
    md = "\n\n".join(parts)
    css = """
table.ros td, table.ros th { font-size: 12pt; }
table.script td:nth-child(1) { width: 8%; } table.script td:nth-child(2) { width: 9%; }
table.script td:nth-child(3) { width: 55%; }
.seg { margin-top: 8pt; }
"""
    cover = cover_html("Strong Years", f"Daily Practice<br>Sessions 1–{upto}", f"The first {upto} days of follow-along scripts with Chang Yin, plus the monthly retest.<br>Four levels. Every line, cue, timing and safety callout.",
                       "For members, coaches and the production team.", DISCLOSURE)
    out_pdf = os.path.join(PRODUCTS, f"daily_practice_sessions_1-{upto}.pdf")
    out_md = os.path.join(PRODUCTS, "daily_practice_sessions_1-30.md") if upto == 30 else None
    render(md, out_pdf, f"Daily Practice Sessions 1–{upto}", cover=cover, out_md=out_md, extra_css=css,
           md_header="<!-- Source for Daily Practice Sessions 1–30. Generated by products/_build/build_sessions.py from sessions_spec.py + library.py. Also exported as products/sessions.json. -->")
    return out_pdf


if __name__ == "__main__":
    print(build())
