#!/usr/bin/env python3
"""Product library -> script briefs (ENGINE_SAVAGE20 #1).

  python3 tools/product_to_scripts.py [--out data/content/product_briefs.json] [--min 300]     exit 1 below --min

Sources (products/): the 30 daily sessions (every warm-up and block movement, steady track), the 6 programs and the
50 Strong Kitchen recipes. Each source item becomes one brief per proven grammar (IF_EVERY, MYTH, AUTHORITY,
COMMAND). Claims, safety lines, regressions and evidence ids are inherited from the product source; no outcome
claims are added. A brief is KEPT only if it clears, in order:
  1. the virality gate (tools/virality.score: pass, >= 60),
  2. the deterministic compliance scan (workers/compliance scanner, verdict pass),
  3. the competitor-corpus gate (workers/uniqueness/external: no shared 7-word shingle, TF-IDF cosine < 0.50),
  4. a CTA keyword that exists in the DM keyword registry (tools/keyword_registry),
  5. a hook not used by any earlier brief.
Rejected briefs are counted by reason. Offline, deterministic, no external AI.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workers"))
sys.path.insert(0, str(ROOT / "tools"))

import virality  # noqa: E402
from compliance import scanner  # noqa: E402
from uniqueness import external  # noqa: E402

GRAMMARS = ("IF_EVERY", "MYTH", "AUTHORITY", "COMMAND")
TYPE = {  # session type -> (page, cta keyword, habit phrase for IF_EVERY, myth line)
    "Strength": ("@changyin.strength", "STRONG", "push off your knees to stand", "Too old to get stronger?"),
    "Mobility": ("@changyin", "BACK", "feel stiff getting out of bed", "Stiff joints should rest?"),
    "Balance": ("@changyin", "BALANCE", "hold the wall to put on socks", "Balance just goes with age?"),
    "Breath + qigong": ("@changyin", "BREATH", "rush your breathing when you feel stressed", "Breathing is automatic, why practice?"),
    "Walk-and-talk": ("@changandsun", "BEGIN", "walk less than you used to", "Walking is not real exercise?"),
    "Rest + stretch": ("@changyin", "SLEEP", "go to bed with a tight back", "Rest days are lazy days?"),
}
PROGRAM_CTA = {"S70": "STRONG", "BKS": "BACK", "BAL": "BALANCE", "GRP": "STRONG", "WLK": "BEGIN", "GUT": "GUT"}
RECIPE_CTA = {"Soup": "SOUP"}
NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]
FOOTER = ("Chang & Sun are AI characters. Content is educational, built on published research, and not medical advice. "
          "Check with your doctor before starting new exercise.")


def _num_words(n: int) -> str:
    return NUM[n - 1] if 1 <= n <= len(NUM) else str(n)


def _short(s: str, n: int = 9) -> str:
    w = re.sub(r"\s+", " ", s or "").strip().rstrip(".").split()
    return " ".join(w[:n])


def _first_sentence(s: str) -> str:
    s = re.sub(r"^(Main version|Easier|Harder):\s*", "", s or "").strip()
    return re.split(r"(?<=[.!?])\s", s)[0].strip()


def movements() -> list[dict]:
    data = json.loads((ROOT / "products" / "sessions.json").read_text(encoding="utf-8"))
    out = []
    for s in data["sessions"]:
        for g in s["segments"]:
            if g.get("kind") not in ("warmup", "block") or not g.get("tracks"):
                continue
            t = g["tracks"].get("steady") or next(iter(g["tracks"].values()))
            out.append({"src": "session", "src_id": g["id"], "session": s["id"], "day": s["day_number"],
                        "type": s["type"], "title": s["title"], "name": t["name"], "dose": t.get("dose") or "",
                        "how": _first_sentence(t.get("how") or ""), "cue": (t.get("cues") or [""])[0],
                        "regression": g.get("regression") or "Sit and do the seated version.",
                        "tags": s.get("movement_tags") or [], "evidence": s.get("evidence") or [],
                        "addon": s.get("caption_movement_addon") or "", "set": s.get("set") or "SET-GARAGE"})
    return out


def _beat(t, vo, ost, shot, speaker="CHANG"):
    return {"t": t, "speaker": speaker, "vo": vo, "ost": ost, "shot": shot}


def movement_brief(m: dict, grammar: str) -> dict:
    page, cta, habit, myth = TYPE.get(m["type"], TYPE["Strength"])
    name, low = m["name"], m["name"].lower()
    day = _num_words(m["day"]) if m["day"] <= 12 else str(m["day"])
    secs = re.search(r"(\d+)\s*(seconds|sec)", m["dose"])
    reps = re.search(r"(\d+)\s*(reps|times|pumps|stands|steps|breaths|rolls|circles)", m["dose"])
    dose = m["dose"] or "ten slow reps"
    hook = {
        "IF_EVERY": f"If you {habit}, do the {low} every morning. Day {day}: {_short(dose, 5)}.",
        "MYTH": f"\"{myth}\" Not with the {low}. Day {day}: {_short(dose, 4)}.",
        "AUTHORITY": f"I'm 74. Every morning I do the {low}. Day {day}: {_short(dose, 5)}.",
        "COMMAND": f"Stand up and try the {low} with me. Day {day}: {_short(dose, 5)}.",
    }[grammar]
    if m["type"] in ("Rest + stretch", "Breath + qigong") and grammar == "COMMAND":
        hook = f"Sit tall and try the {low} with me. Day {day}: {_short(dose, 5)}."
    shot0 = f"{m['set']} | C-TRAIN-A | Chang holds the counter and does the {low} | eye-level, full body, handheld"
    beats = [
        _beat("0-3", hook, name.upper()[:28], shot0),
        _beat("3-10", f"Here's the part most people skip. {m['how']}", _short(m["cue"], 6), f"same | {m['set']} | Chang demonstrates the {low}, side 3/4 | medium-full"),
        _beat("10-22", f"{m['cue']} Breathe out as you stand or push. Hand on the counter or the chair. Go slow.", "Hand on the counter", "same | slow reps, counter in frame | medium-full"),
        _beat("22-30", f"Too much? {m['regression']}", "Easier version", "same | Chang shows the easier version on the chair | medium"),
        _beat("30-37", "Stop if you feel chest pain, dizziness or sharp pain. Save this for day "
              f"{day}. Send it to your sister who sits all day.", "Save · send", "same | Chang sits, nods | medium CU"),
        _beat("37-41", f"Comment {cta}. I'll send you the full session.", f"Comment {cta}", "same | Chang points to camera | medium CU"),
    ]
    caption = (f"Day {m['day']} · {m['title']} · {name}. {_short(dose, 8)}. Comment {cta} for the full session.\n"
               f"{m['addon']}\n{FOOTER}")
    return {"page": page, "speaker": "CHANG", "pillar": "P01", "has_movement": True, "movement_tags": m["tags"],
            "evidence": m["evidence"], "regression": m["regression"],
            "safety_cue": "Hand on the counter or chair (spoken + OST); stop rule spoken; caption add-on.",
            "cta_keyword": cta, "target_seconds": 41, "beats": beats, "caption": caption, "hook_line": hook,
            "title": f"{name} ({m['title']}, day {m['day']})", "source": {"kind": "session", "id": m["src_id"], "session": m["session"]},
            "_n": bool(secs or reps)}


def recipe_brief(r: dict, grammar: str) -> dict:
    cta = RECIPE_CTA.get(r["category"], "GUT")
    name, low = r["name"], r["name"][0].lower() + r["name"][1:]
    mins = r.get("minutes_active") or 15
    step = _first_sentence((r.get("steps") or ["Prep everything first."])[0])
    soft = r.get("soft_food") or ""
    soft = soft if "%" not in soft else ""          # an un-cited percentage would need an evidence id (C-01)
    meal = r["category"].lower()
    hook = {
        "IF_EVERY": f"If you eat the same {meal} every week, try this. {mins} minutes of work.",
        "MYTH": f"\"Cooking for one is not worth it?\" Not with {low}. {mins} minutes.",
        "AUTHORITY": f"Fifty years of cooking. Every week I make {low}. {mins} minutes.",
        "COMMAND": f"Grab one pot and make {low} with me. {mins} minutes.",
    }[grammar]
    shot0 = f"SET-KITCHEN | C-SUN-A | Sun lines up the ingredients for {low} on the counter | top-down, handheld"
    beats = [
        _beat("0-3", hook, _short(name.upper(), 5), shot0, "SUN"),
        _beat("3-12", f"Here's the step most people rush. {step}", "Step one", "same | Sun does step one | close-up hands", "SUN"),
        _beat("12-24", f"Serves {r.get('serves', 4)}. {_short(r.get('storage') or 'Keeps in the fridge.', 12)}.",
              f"Serves {r.get('serves', 4)}", "same | Sun stirs and portions | medium", "SUN"),
        _beat("24-32", f"Softer? {_short(soft or 'Cook it longer and chop it small.', 14)}.", "Softer version",
              "same | Sun shows the soft version | close-up", "SUN"),
        _beat("32-38", "Save this for Sunday. Send it to your sister who cooks for one.", "Save · send",
              "same | Sun tastes, smiles | medium CU", "SUN"),
        _beat("38-42", f"Comment {cta}. I'll send you the full recipe.", f"Comment {cta}", "same | Sun points to camera | medium CU", "SUN"),
    ]
    cautions = " ".join(r.get("cautions") or [])
    caption = f"{name}. {mins} minutes active. Comment {cta} for the full recipe card.\n{cautions}\n{FOOTER}".replace("\n\n", "\n")
    return {"page": "@sunyoon.kitchen", "speaker": "SUN", "pillar": "P07", "has_movement": False, "movement_tags": [],
            "evidence": [], "demo": True, "prop": name, "cta_keyword": cta, "target_seconds": 42, "beats": beats,
            "caption": caption, "hook_line": hook, "title": name, "source": {"kind": "recipe", "id": r["id"]}}


def program_brief(p: dict, grammar: str, wk: int) -> dict:
    cta = PROGRAM_CTA.get(p["id"], "JOIN")
    cp = p["checkpoints"][(wk - 1) % len(p["checkpoints"])]
    name, test = p["name"], cp["name"]
    weeks = p.get("length_weeks") or 12
    hook = {
        "IF_EVERY": f"If you sit most of the day, test this every month. The {test.lower()}.",
        "MYTH": f"\"You can't measure getting stronger at home?\" Not true. The {test.lower()}.",
        "AUTHORITY": f"I'm 74. Every month I do the {test.lower()}. Week {wk} of {weeks}.",
        "COMMAND": f"Grab a chair and do the {test.lower()} with me. Week {wk}.",
    }[grammar]
    shot0 = f"SET-GARAGE | C-TRAIN-A | Chang sets the chair against the wall for the {test.lower()} | eye-level, full body"
    beats = [
        _beat("0-3", hook, _short(test.upper(), 5), shot0),
        _beat("3-12", f"Here's how. {_short(cp['how'], 16)}.", "How to test", "same | Chang demonstrates | medium-full"),
        _beat("12-22", "Chair against the wall. Breathe out as you stand. Hand on the counter if you need it. Stop if anything feels sharp.",
              "Chair against the wall", "same | safety setup | medium"),
        _beat("22-32", f"Write your number down. {name} retests it at week {wk + 3 if wk + 3 <= weeks else weeks}.",
              "Write it down", "same | Chang writes on a card | close-up"),
        _beat("32-38", "Send this to your husband who says he's fine.", "Send this", "same | Chang laughs | medium CU"),
        _beat("38-42", f"Comment {cta}. I'll send you the program.", f"Comment {cta}", "same | Chang points to camera | medium CU"),
    ]
    caption = f"{name}: {test}. Comment {cta} for the {weeks}-week program.\n{FOOTER}"
    return {"page": "@changandsun", "speaker": "CHANG", "pillar": "P01", "has_movement": True,
            "movement_tags": ["sit_to_stand"], "evidence": re.findall(r"\bE\d+\b", str(cp.get("evidence") or "")),
            "regression": "Use your hands on your thighs; a higher seat.",
            "safety_cue": "Chair against the wall, stop rule (spoken).", "cta_keyword": cta, "target_seconds": 42,
            "beats": beats, "caption": caption, "hook_line": hook, "title": f"{name}: {test} (wk {wk})",
            "source": {"kind": "program", "id": p["id"]}}


def candidates() -> list[dict]:
    out = []
    for m in movements():
        out += [movement_brief(m, g) | {"grammar": g} for g in GRAMMARS]
    for p in json.loads((ROOT / "products" / "programs.json").read_text(encoding="utf-8"))["programs"]:
        for wk in (1, 4, 8):
            out += [program_brief(p, g, wk) | {"grammar": g} for g in GRAMMARS]
    for r in json.loads((ROOT / "products" / "kitchen_recipes.json").read_text(encoding="utf-8")):
        out += [recipe_brief(r, g) | {"grammar": g} for g in GRAMMARS]
    return out


ADD_RX = re.compile(r'add "([^"]+)"')


def inherit_safety(b: dict) -> dict:
    """Append the exact safety lines the scanner requires for the inherited movement tags (SAFETY_RULES §4.2) to the
    spoken safety beat, once. The product source carries the same lines; this keeps the brief self-contained."""
    c = scanner.scan(b)
    lines = [m.group(1) for x in c["required_missing"] for m in [ADD_RX.search(str(x))] if m]
    if lines:
        safety = next(x for x in b["beats"] if "Stop if" in x["vo"] or "sharp" in x["vo"])
        safety["vo"] = (safety["vo"] + " " + " ".join(dict.fromkeys(lines))).strip()
        b["target_seconds"] = min(59, b["target_seconds"] + 3 * len(lines))
    return b


def registry_keywords() -> set[str]:
    return {json.loads(f.read_text(encoding="utf-8")).get("keyword") for f in (ROOT / "workers" / "dm" / "flows").glob("*.json")} - {None}


def build(min_n: int = 300) -> dict:
    kws, seen, kept, why = registry_keywords(), set(), [], Counter()
    idx = external.default_index()
    for i, b in enumerate(candidates(), start=1):
        b.pop("_n", None)
        b["id"] = f"PB{i:04d}"
        key = re.sub(r"[^a-z0-9]", "", b["hook_line"].lower())
        if key in seen:
            why["duplicate hook"] += 1
            continue
        b = inherit_safety(b)
        v = virality.score(b)
        if not v["pass"]:
            why["virality gate"] += 1
            continue
        c = scanner.scan(b)
        if c["verdict"] != "pass":
            why[f"compliance {c['verdict']}"] += 1
            continue
        e = external.check_external(b, idx)
        if not e["allow"]:
            why["competitor corpus"] += 1
            continue
        if b["cta_keyword"] not in kws:
            why["keyword not in registry"] += 1
            continue
        seen.add(key)
        kept.append({**b, "status": "idea", "origin": "product", "virality": {"score": v["score"], "hook_class": v["hook_class"]},
                     "external": {"max_cosine": e["max_cosine"], "nearest": e["nearest"]}})
    src = Counter(b["source"]["kind"] for b in kept)
    ids = {k: len({b["source"]["id"] for b in kept if b["source"]["kind"] == k}) for k in src}
    ids["session_days"] = len({b["source"].get("session") for b in kept if b["source"]["kind"] == "session"})
    return {"version": 1, "generated_by": "tools/product_to_scripts.py", "kept": len(kept), "rejected": dict(why),
            "by_source": dict(src), "distinct_sources": ids, "by_grammar": dict(Counter(b["grammar"] for b in kept)),
            "by_page": dict(Counter(b["page"] for b in kept)), "ok": len(kept) >= min_n, "briefs": kept}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data" / "content" / "product_briefs.json"))
    ap.add_argument("--min", type=int, default=300)
    a = ap.parse_args(argv)
    res = build(a.min)
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"product briefs: kept {res['kept']} (min {a.min}) · sources {res['distinct_sources']} · "
          f"grammars {res['by_grammar']} · rejected {res['rejected']}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
