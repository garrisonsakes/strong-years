"""Markdown blocks shared by several products."""
from library import EX, STOP, EMERGENCY, PAIN_RULE, STAND_SLOW
from common import box, say


def eh_md(easier, harder):
    return (f'<table class="eh"><tr><td class="e"><strong>Easier:</strong> {easier}</td><td class="gap"></td>'
            f'<td class="h"><strong>Harder:</strong> {harder}</td></tr></table>\n')


def exercise_md(eid, dose, extra=None, heading_level=3, show_harder=True):
    e = EX[eid]
    h = "#" * heading_level
    lines = [f'<div class="exercise" id="ex-{eid}" markdown="1">\n', f"{h} {e['name']}\n",
             f'<p class="dose">{dose}</p>\n',
             f"**You need:** {e['equip']}. **Set up:** {e['setup']}\n"]
    for i, s in enumerate(e["steps"], 1):
        lines.append(f"{i}. {s}")
    lines.append("")
    lines.append(f"**Chang's cues:** {' '.join(e['cues'])} **Breathe:** {e['breathe']}\n")
    lines.append("</div>\n")
    lines.append(eh_md(e["easier"], e["harder"]))
    safety = list(e["safety"]) + ([extra] if extra else [])
    if safety:
        lines.append(box("note", "Safety:", " ".join(safety)))
    return "\n".join(lines) + "\n"


def stop_box():
    return box("stop", "Stop rule.", f"{STOP} {EMERGENCY} Pain rule: {PAIN_RULE}")


def before_you_start_md():
    return f"""
## Before you start

Most healthy adults can begin light-to-moderate exercise like this and build up gradually (E43). Some people should talk to their doctor first.

<div class="box stop" markdown="1">
<span class="label">Get your doctor's okay first if any of these are true:</span>

- You get chest pain, pressure or tightness when you're active, or unusual shortness of breath.
- You have fainted, nearly fainted, or get dizzy when you stand up.
- You have a heart, kidney, lung or metabolic condition (like diabetes) and you have symptoms, or your doctor has told you to limit activity.
- You've had surgery, a fracture, a fall with injury, or a hospital stay in the last few months.
- You have a new hip or knee: follow your surgeon's or physical therapist's precautions first.
</div>

**Set up a safe space.** Chair with no wheels, pushed against a wall. Kitchen counter within reach for anything standing. Good light. No rugs under your feet. Wear shoes with a grippy sole: no socks on hard floors, no bare feet on slippery floors. Water nearby. If you can, do the tests with someone home.

**Stand up slowly.** Many older adults get a blood-pressure dip when they stand up quickly (about 22% of community-dwelling older people, E46). {STAND_SLOW} Pump your ankles ten times first.

**Breathe out when it's hard.** Never hold your breath to push. Breath-holding while straining spikes blood pressure (E42).

**The pain rule (E41).** {PAIN_RULE}

<div class="box stop" markdown="1">
<span class="label">Not for exercise. For your doctor, today:</span> chest pain or pressure; fainting; sudden weakness or numbness in the face, arm or leg; trouble speaking; a sudden severe headache; new confusion; one calf that is swollen, red and painful; a hot, swollen joint; night pain that wakes you and doesn't change with position; loss of bladder or bowel control or numbness in the saddle area; a fall where you hit your head (especially on blood thinners). **{EMERGENCY}**
</div>
"""


def exercise_compact_md(eid, dose, heading_level=3):
    """Short repeat of an exercise already described in full earlier in the same book."""
    e = EX[eid]
    h = "#" * heading_level
    safety = " ".join(e["safety"])
    return (f'<div class="compact" markdown="1">\n\n{h} {e["name"]}\n\n<p class="dose">{dose}</p>\n\n'
            f'<a class="pref" href="#ex-{eid}">Same move as before</a>. **Cues:** {" ".join(e["cues"])} **Breathe:** {e["breathe"]}\n\n'
            + (f'**Safety:** {safety}\n\n' if safety else '') + '</div>\n' + eh_md(e["easier"], e["harder"]))
