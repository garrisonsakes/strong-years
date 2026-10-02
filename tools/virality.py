#!/usr/bin/env python3
"""Quantitative virality gate for scripts (VIRALITY_SYSTEM.md §2).

score(script) -> {"score": 0-100, "pass": bool, "hook_class": str, "parts": {component: points}, "why": [str]}

The rubric is code so the build, the launch-day plan builder and the posting-plan builder all apply the same bar.
Weights come from the measured evidence in POSTDB_FINDINGS.md (Yang Mun's 244 posts, return-era rel) and from the
2025–2026 platform research cited in VIRALITY_SYSTEM.md. Anything below marked [A] is an assumption we will
re-weight from our own shares+saves data (workers/growth) once pages have 30 posts of history.

Accepts both script shapes: the source dicts in data/content/scripts_*.py (tuple beats: t, speaker, vo, ost, shot)
and the exported schema in data/content/scripts.json / runway_scripts.json (dict beats: t, vo, ost, shot).
"""
from __future__ import annotations

import re

# ---------------------------------------------------------------------------------------------------- weights
WEIGHTS = {            # sum = 100
    "hook_class": 25,  # POSTDB §3b/§3a hook-type rel, log-scaled below; the biggest measured lever
    "demo_on_self": 15,  # body demo on self rel 2.34, food demo 1.42, plain talking head 0.71 (POSTDB §3b)
    "first_line": 10,  # first spoken clause <= 12 words (~5 s at 2.3 w/s elder pace; 50-60% of drop-offs happen in the
                       # first 3 s, OpusClip 2025); the full first sentence may run to 22 (POSTDB §3a mega-hits)
    "number": 10,      # a concrete number in the hook or re-hook (POSTDB §7: 8 of the 15 best hooks carry one)
    "open_loop": 10,   # re-hook at 3-6 s; watch time decides whether distribution expands (Mosseri 2025-26)
    "share": 8,        # share trigger: shares correlate most with outperformance (POSTDB §3c: 0.34); sends per reach
                       # is the strongest non-follower signal (Mosseri 2025-26)
    "save": 7,         # save trigger: a reason to come back (routine, day N, tonight, write it down)
    "length": 10,      # 30-59 s rel 1.10-1.19 vs 90 s+ 0.70 (POSTDB §3b)
    "emotion": 2,      # identity / family / relief trigger in the first two beats [A]
    "cta_friction": 3, # last line short, one keyword, said once (CONTENT_SYSTEM §4)
}
def _load_override() -> None:
    """data/content/rubric_weights.json (written only by `tools/refit_gate.py --apply`) replaces WEIGHTS when it
    names the same rows and sums to 100; anything else is ignored."""
    import json as _json
    import os as _os
    p = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "data", "content", "rubric_weights.json")
    try:
        w = _json.load(open(p))
    except (OSError, ValueError):
        return
    if isinstance(w, dict) and set(w) == set(WEIGHTS) and abs(sum(float(v) for v in w.values()) - 100) < 0.5:
        WEIGHTS.update({k: float(v) for k, v in w.items()})


_load_override()
THRESHOLD = 60         # below this a script is rejected (build fails for S61+ and every new script)
TOP_DECILE = 85        # the launch-day 6 must clear this (a fixed bar, ~ the library's top decile)
# Hook classes, valued by the measured relative performance they stand on (POSTDB §3b TikTok return era, n = 45, and
# §3a all eras for IF_EVERY / MYTH). value = 0.2 + 0.8 * (ln rel - ln rel_min) / (ln rel_max - ln rel_min): log scale
# because rel is a ratio; the 0.2 floor because POSTDB §9 calls any rel difference under ~1.5x noise at these n.
# COMMAND (participation test, "Sit down. Stand up. No hands.") and OBJ3 ("Put honey on the tomato…", "Stand on salt…")
# are not separately coded in Yang Mun's data; their best examples are the watch-family hooks (rel 56, IG 305K), so
# they take WATCH's rel until our own shares+saves data re-weights them [A].
import math as _math
HOOK_REL = {"IF_EVERY": 5.5, "MYTH": 3.0, "NOT_X": 3.0, "AUTHORITY": 2.65, "WATCH": 2.06, "COMMAND": 2.06, "OBJ3": 2.06,
            "STORY": 1.74, "STATEMENT": 1.08, "LIST": 0.95, "SYMPTOM_IF": 0.86, "QUESTION": 0.70, "HOWTO": 0.61}
_lo, _hi = _math.log(min(HOOK_REL.values())), _math.log(max(HOOK_REL.values()))
HOOK_CLASS_VALUE = {k: round(0.2 + 0.8 * (_math.log(v) - _lo) / (_hi - _lo), 3) for k, v in HOOK_REL.items()}
FIRST_CLAUSE_MAX = 12

_NUM_WORDS = r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|half|twice|double)\b"
NUMBER_RX = re.compile(r"\d|" + _NUM_WORDS, re.I)
SHARE_RX = re.compile(r"\b(send (this|it|him|her|them)|share (this|it)|tag (the|your|a)|show (him|her|them|your|this to)|"
                      r"forward (this|it)|do (this|the \w+ test) with (your|them|him|her)|for the (sister|husband|wife|mom|dad|friend)|"
                      r"your (sister|husband|wife|mother|father|mom|dad|kids|daughter|son|friend|parents) (who|needs|is|will|won't|still))\b", re.I)
SAVE_RX = re.compile(r"\b(save (this|it)|screenshot|write (this|it) down|come back (to|tomorrow)|do it tonight|tonight before bed|"
                     r"day (one|two|three|four|five|six|seven|\d)|tomorrow|every (morning|night|day) this week)\b", re.I)
PARTICIPATE_RX = re.compile(r"\b(tell me your (number|time|score|count)|comment (your|the) (number|score|time)|type \w+ if|how many did you|what('s| is) your (number|score))\b", re.I)
OPEN_LOOP_RX = re.compile(r"(\.\.\.|…|\?|\bbut\b|\bwatch\b|\bhere'?s\b|\bthe second\b|\bwait\b|\bwhat happens\b|\bnobody\b|\bthe (one|part|thing) (most|nobody|that)|\bshow (me|you)\b|\bstay\b|\bthen\b|\bnow\b|\buntil\b|\bthere isn'?t\b|\bno\.|\bokay\b)", re.I)
EMOTION_RX = re.compile(r"\b(i'?m \d\d|at \d\d|husband|wife|sister|mother|mom|dad|father|grand(ma|pa|kids|children|child)|daughter|son|kids|"
                        r"scared|afraid|fear|alone|lonely|widow\w*|proud|shame|no shame|embarrass\w*|cried|love|hate|stubborn|"
                        r"nobody|too old|too late|give up|gave up|the day you|your (age|future)|married|anniversary|fifty years)\b", re.I)
DEMO_VERB_RX = re.compile(r"\b(lifts?|carries|carry|stands?|sits?|squats?|steps?|walks?|holds?|presses|pulls?|pours?|chops?|stirs?|"
                          r"drops?|cracks?|slices?|peels?|drizzles?|whisks?|ladles?|kneels?|reaches|bends?|hinges?|marches|"
                          r"balances?|wrings?|opens?|closes?|pushes|rows?|places|puts|taps|dips|scoops?|eats?|tastes?|does|doing|"
                          r"slides?|flex\w*|weighs?|flips?|lines up|coughing|snoring|plays|loops?|halves|crumbles?|drains?)\b", re.I)
QUESTION_OPEN_RX = re.compile(r"^(what|why|how|which|where|who|do you|can you|did you|are you|is it|have you)\b", re.I)
HOWTO_RX = re.compile(r"^(how to|here'?s how to|the (best|right) way to)\b", re.I)
LIST_RX = re.compile(r"^(three|four|five|3|4|5|seven|7|ten|10)\s+(signs|things|mistakes|moves|questions|reasons|foods|ways)\b|\b(signs|mistakes) (your|after|of)\b", re.I)
AUTHORITY_RX = re.compile(r"^(i'?m \d\d|i am \d\d|at \d\d|fifty years|in \d+ trials|\d[\d,]* (adults|people|trials|women|men|studies)\b|a (lancet|bmj|jama|cochrane)|the (study|trial|review) (found|says))", re.I)
STORY_RX = re.compile(r"^(my (husband|wife|mother|father|mom|dad|friend|doctor|daughter|son)|he (says|said|cooked|flexes|hid|wanted)|she (said|says|asked)|our (daughter|son|kids)|i (weighed|graded|hid|caught|found|asked)|last (night|week|sunday))\b", re.I)
COMMAND_RX = re.compile(r"^(sit|stand|put|press|hold|lift|squeeze|march|wall sit|get|grab|try|do|press|step|reach|bend|take|pick|walk|carry|balance|breathe|close|open|look|watch|stop|start|come|count|lie|roll|turn|push|pull|drop|say|write|tell)\b", re.I)


def _beats(s: dict) -> list[dict]:
    out = []
    for b in s["beats"]:
        if isinstance(b, dict):
            out.append({"t": b.get("t", ""), "vo": b.get("vo") or "", "ost": b.get("ost") or "", "shot": b.get("shot") or ""})
        else:
            out.append({"t": b[0], "vo": b[2] or "", "ost": b[3] or "", "shot": b[4] or ""})
    return out


def _secs(s: dict) -> int:
    return int(s.get("secs") or s.get("target_seconds") or 0)


def _demo_flags(s: dict) -> tuple[bool, bool, str]:
    move = bool(s.get("move") if "move" in s else s.get("has_movement"))
    demo = bool(s.get("demo"))
    prop = s.get("prop") or ""
    return move, demo, prop


def classify_hook(hook: str, s: dict | None = None) -> list[str]:
    """Every class the hook text matches, best first. Mirrors build_content.proven_grammar for the proven four."""
    h = hook.strip().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    hl = h.lower()
    bare = hl.lstrip("'\"")
    classes = []
    if re.match(r"^if you\b", bare) and re.search(r"\bevery\b", bare):
        classes.append("IF_EVERY")
    if re.search(r"\bnot\b[^?!]{0,40}[,.]\s*not\b", bare):
        classes.append("NOT_X")
    quoted_myth = bool(re.match(r"^['\"]", h)) or (((s or {}).get("myth") or (s or {}).get("myth_bust")) and ("?" in bare or re.search(r"\b(not|no)\b|n't\b", bare)))
    if quoted_myth or re.search(r"\b(they lied|myth|not a remedy|show me the study|is it\?)\b", bare) or ((s or {}).get("pillar") == "P15" and re.search(r"\b(not|no)\b|n't\b|\?", bare)):
        classes.append("MYTH")
    if re.search(r"\bwatch what happens\b|\band (just )?watch\b|\bwatch (it|the|my|your|his|her|how|this|me|what)\b", bare):
        classes.append("WATCH")
    if AUTHORITY_RX.search(bare):
        classes.append("AUTHORITY")
    if STORY_RX.search(bare):
        classes.append("STORY")
    if HOWTO_RX.search(bare):
        classes.append("HOWTO")
    elif QUESTION_OPEN_RX.search(bare) and not classes:
        classes.append("QUESTION")
    if re.match(r"^if you (have|feel|get|suffer|are|can't|cannot|wake|struggle)\b", bare) and "IF_EVERY" not in classes:
        classes.append("SYMPTOM_IF")
    if LIST_RX.search(bare):
        classes.append("LIST")
    if COMMAND_RX.search(bare) and not {"HOWTO", "QUESTION"} & set(classes):
        classes.append("COMMAND")
    obj = (s or {}).get("obj") or (s or {}).get("hook_object")
    first3 = [re.sub(r"[^\w'-]", "", w).lower().strip("'") for w in h.split()[:3]]
    if obj and any(w.startswith(str(obj).lower()) for w in first3) and "OBJ3" not in classes:
        classes.append("OBJ3")
    if not classes:
        classes.append("STATEMENT")
    classes.sort(key=lambda c: -HOOK_CLASS_VALUE[c])
    return classes


def score(s: dict) -> dict:
    beats = _beats(s)
    hook = beats[0]["vo"] if beats else (s.get("hook_line") or "")
    spoken = " ".join(b["vo"] for b in beats)
    ost_all = " ".join(b["ost"] for b in beats)
    caption = s.get("caption") or ""
    secs = _secs(s)
    move, demo, prop = _demo_flags(s)
    parts: dict[str, float] = {}
    why: list[str] = []

    classes = classify_hook(hook, s)
    hc = classes[0]
    v = HOOK_CLASS_VALUE[hc]
    # a weak opener that still names the object/body part in the first three words gets OBJ3 credit (POSTDB §8 rule 2)
    if "OBJ3" in classes and v < HOOK_CLASS_VALUE["OBJ3"]:
        v = HOOK_CLASS_VALUE["OBJ3"]
    parts["hook_class"] = round(WEIGHTS["hook_class"] * v, 2)
    if v < 0.5:
        why.append(f"hook class {hc} is a bottom-tier opener (POSTDB §3b)")

    clause = re.split(r"[,.;:!?…—]", hook.strip(), maxsplit=1)[0]
    n = len(clause.split())
    n_sent = len(re.split(r"(?<=[.!?])\s", hook.strip())[0].split())
    fl = 1.0 if n <= FIRST_CLAUSE_MAX else (0.5 if n <= 16 else 0.2)
    if n_sent > 22:
        fl = min(fl, 0.5)
    parts["first_line"] = round(WEIGHTS["first_line"] * fl, 2)
    if fl < 1.0:
        why.append(f"first spoken clause {n} words / sentence {n_sent} (max {FIRST_CLAUSE_MAX} / 22)")

    first_two = " ".join(b["vo"] + " " + b["ost"] for b in beats[:2])
    num = 1.0 if NUMBER_RX.search(first_two) else (0.5 if NUMBER_RX.search(spoken) else 0.0)
    parts["number"] = round(WEIGHTS["number"] * num, 2)
    if num < 1.0:
        why.append("no concrete number in the hook or re-hook")

    frame1_action = bool(beats) and bool(DEMO_VERB_RX.search(beats[0]["shot"]))
    if move:
        d = 1.0
    elif demo or (prop and frame1_action):
        d = 0.75
    elif frame1_action:
        d = 0.6      # legacy script (no prop field) whose frame-1 shot shows a physical action with an object
    elif prop:
        d = 0.45
    else:
        d = 0.0
    parts["demo_on_self"] = round(WEIGHTS["demo_on_self"] * d, 2)
    if d < 0.75:
        why.append("no visible demo in frame 1 (talking head / symbolic prop: rel 0.71–0.72)")

    rehook = beats[1]["vo"] + " " + beats[1]["ost"] if len(beats) > 1 else ""
    ol = 1.0 if (OPEN_LOOP_RX.search(rehook) or OPEN_LOOP_RX.search(hook)) else 0.3
    parts["open_loop"] = round(WEIGHTS["open_loop"] * ol, 2)
    if ol < 1.0:
        why.append("no open loop / re-hook by second 3–6")

    tail = " ".join(b["vo"] + " " + b["ost"] for b in beats[-3:]) + " " + caption
    sh = 1.0 if (SHARE_RX.search(tail) or SHARE_RX.search(spoken)) else (0.5 if PARTICIPATE_RX.search(spoken) else 0.0)
    parts["share"] = round(WEIGHTS["share"] * sh, 2)
    if sh < 1.0:
        why.append("no share trigger ('send this to…', 'do it with your…'; shares rank first, POSTDB §3c)")
    sv = 1.0 if SAVE_RX.search(spoken + " " + ost_all + " " + caption) else (0.5 if PARTICIPATE_RX.search(spoken) else 0.0)
    parts["save"] = round(WEIGHTS["save"] * sv, 2)
    if sv < 1.0:
        why.append("no save trigger (a routine / day N / tonight / write it down)")

    ln = 1.0 if 30 <= secs <= 59 else (0.6 if 25 <= secs <= 69 else 0.2)
    parts["length"] = round(WEIGHTS["length"] * ln, 2)
    if ln < 1.0:
        why.append(f"{secs} s outside the 30–59 s band")

    em = 1.0 if EMOTION_RX.search(first_two + " " + hook) else (0.5 if EMOTION_RX.search(spoken) else 0.0)
    parts["emotion"] = round(WEIGHTS["emotion"] * em, 2)

    last = beats[-1]["vo"] if beats else ""
    kws = re.findall(r"\bComment [A-Z]{3,}\b", spoken)
    cf = 1.0 if (len(last.split()) <= 14 and len(set(kws)) <= 1) else 0.4
    parts["cta_friction"] = round(WEIGHTS["cta_friction"] * cf, 2)
    if cf < 1.0:
        why.append("CTA is long or asks for more than one keyword")

    total = round(sum(parts.values()), 1)
    return {"id": s.get("id"), "score": total, "pass": total >= THRESHOLD, "top_decile": total >= TOP_DECILE,
            "hook_class": hc, "hook_classes": classes, "parts": parts, "why": why}


def report(scores: list[dict]) -> str:
    n = len(scores)
    p = sum(1 for x in scores if x["pass"])
    t = sum(1 for x in scores if x["top_decile"])
    med = sorted(x["score"] for x in scores)[n // 2] if n else 0
    return f"virality gate: {p}/{n} pass (≥{THRESHOLD}), {t} top-decile (≥{TOP_DECILE}), median {med}"


if __name__ == "__main__":
    import json, sys, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts = json.load(open(os.path.join(root, "data", "content", "scripts.json")))
    rows = [score(s) for s in scripts]
    print(report(rows))
    for r in sorted(rows, key=lambda r: r["score"]):
        if "-v" in sys.argv or not r["pass"]:
            print(f"{r['id']:>5} {r['score']:5.1f} {r['hook_class']:<10} {'; '.join(r['why'])}")
