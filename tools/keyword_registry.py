#!/usr/bin/env python3
"""DM keyword registry check (ENGINE_SAVAGE20 §B(b) item 1, SL-05.1).

  python3 tools/keyword_registry.py [--manual-replies OUT.md]     exit 1 on any error

Registry = every EN flow in workers/dm/flows/*.json (keyword + variants) plus the Spanish clone keywords
(tools/build_content_es.CTA_DELIV_ES → the EN flow named in its parenthetical). Errors:
  - a keyword (accent- and case-folded) defined twice, in any language or page;
  - a keyword or variant equal to a reserved word (platform opt-out/help words, the bot's exact intents) or
    containing a non-exact global intent phrase (those fire first in DMs: human, price, cancel, ...);
  - the same variant claimed by two flows;
  - a keyword used by the day-1 plan, scripts.json or scripts_es.json with no flow behind it, or a flow with no
    manual reply text (while DM sends are off, a person answers from the manual reply sheet).
Warnings (not failures): a variant of one flow contained in another flow's term (the bot takes the longest match),
and one-word everyday variants that will fire on ordinary comments.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOWS = ROOT / "workers" / "dm" / "flows"
PLATFORM_RESERVED = {"stop", "stopall", "stop all", "unsubscribe", "cancel", "end", "quit", "start", "unstop", "yes",
                     "no", "help", "info", "optout", "opt out", "revoke"}
EVERYDAY = {"age", "list", "steps", "mom", "dad", "gift", "heal", "reset", "kitchen", "recipe", "energy", "steady",
            "member", "knee", "back"}


def fold(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode() or str(s or "")
    return re.sub(r"\s+", " ", s.lower()).strip()


def _word_in(needle: str, hay: str) -> bool:
    if not re.search(r"\w", needle):
        return needle == hay
    return re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", hay) is not None


def load_flows(flows_dir: Path = FLOWS) -> tuple[dict, dict]:
    flows = {}
    for p in sorted(flows_dir.glob("*.json")):
        if not p.name.startswith("_"):
            f = json.loads(p.read_text(encoding="utf-8"))
            flows[f["keyword"].upper()] = f
    return flows, json.loads((flows_dir / "_global.json").read_text(encoding="utf-8"))


def es_keywords(en: set[str]) -> dict[str, str]:
    """Spanish keyword → EN clone flow keyword."""
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        from build_content_es import CTA_DELIV_ES  # noqa: PLC0415
    finally:
        sys.path.pop(0)
    fallback = {"LISTA": "WAITLIST", "LIBRO": "BOOK", "UNIRME": "JOIN"}  # FUNNEL.md §4.20–4.22
    out = {}
    for kw, deliv in CTA_DELIV_ES.items():
        hit = [t for t in re.findall(r"[A-Z]{3,}", deliv.split("(")[-1]) if t in en]
        out[kw] = hit[0] if hit else fallback.get(kw, "")
    return out


def used_keywords(root: Path = ROOT) -> dict[str, set[str]]:
    used: dict[str, set[str]] = {}
    plan = root / "production" / "launch_day" / "day1_plan.json"
    if plan.is_file():
        for p in json.loads(plan.read_text(encoding="utf-8"))["posts"]:
            used.setdefault(p["cta_keyword"].upper(), set()).add(f"day1:{p['post_id']}")
    for name in ("scripts.json", "scripts_es.json"):
        f = root / "data" / "content" / name
        if f.is_file():
            for s in json.loads(f.read_text(encoding="utf-8")):
                kw = s.get("cta_keyword") or (s.get("cta") or {}).get("keyword")
                if kw:
                    used.setdefault(kw.upper(), set()).add(f"{name}:{s['id']}")
    return used


def manual_reply(f: dict) -> str:
    replies = [r for r in f.get("reply") or [] if r.strip()]
    first = ((f.get("states") or {}).get(f.get("start") or "", {}).get("dm") or [""])[0]
    return (replies[0] + "\n\n" + first).strip() if replies or first else ""


def check(flows: dict, glob: dict, es: dict[str, str], used: dict[str, set[str]]) -> dict:
    errors, warnings = [], []
    exact = {fold(m) for it in glob.get("intents", []) if it.get("exact") for m in it["match"]}
    loose = {fold(m): it["id"] for it in glob.get("intents", []) if not it.get("exact") for m in it["match"]}
    reserved = PLATFORM_RESERVED | exact
    seen_kw: dict[str, str] = {}
    for kw, lang in [(k, "en") for k in flows] + [(k, "es") for k in es]:
        fk = fold(kw)
        if fk in seen_kw:
            errors.append(f"keyword {kw} ({lang}) collides with {seen_kw[fk]}")
        seen_kw[fk] = f"{kw} ({lang})"
    owner: dict[str, str] = {}
    for kw, f in list(flows.items()) + [(k, {"keyword": k, "variants": []}) for k in es]:
        terms = {fold(kw)} | {fold(v) for v in f.get("variants", [])}
        for t in sorted(terms):
            if t in reserved:
                errors.append(f"{kw}: term '{t}' is a reserved word (opt-out/opt-in/help)")
            for m, iid in loose.items():
                if re.search(r"\w", m) and _word_in(m, t):
                    errors.append(f"{kw}: term '{t}' contains the '{iid}' intent phrase '{m}' (intent fires first in DMs)")
            if t in owner and owner[t] != kw:
                errors.append(f"term '{t}' is claimed by both {owner[t]} and {kw}")
            owner.setdefault(t, kw)
            if t in EVERYDAY:
                warnings.append(f"{kw}: one-word everyday variant '{t}' will fire on ordinary comments")
    for t, kw in owner.items():
        for t2, kw2 in owner.items():
            if kw2 != kw and t != t2 and re.search(r"\w", t) and _word_in(t, t2):
                warnings.append(f"'{t}' ({kw}) is inside '{t2}' ({kw2}); the bot takes the longest match")
    for kw, f in flows.items():
        if not manual_reply(f):
            errors.append(f"{kw}: no manual reply text (reply[] / first DM)")
    for kw, f in es.items():
        if not f or f not in flows:
            errors.append(f"ES keyword {kw} maps to no EN flow")
    for kw, where in sorted(used.items()):
        if kw not in flows and kw not in es:
            errors.append(f"keyword {kw} used by {', '.join(sorted(where)[:3])} has no flow")
    return {"errors": sorted(set(errors)), "warnings": sorted(set(warnings)), "keywords": sorted(flows) + sorted(es),
            "used": {k: len(v) for k, v in sorted(used.items())}}


def run(root: Path = ROOT) -> dict:
    flows, glob = load_flows(root / "workers" / "dm" / "flows")
    return check(flows, glob, es_keywords(set(flows)), used_keywords(root))


def manual_sheet(flows: dict, keywords: list[str] | None = None) -> str:
    lines = ["# Manual DM reply sheet (DM sends are off: a person replies by hand)", "",
             "Reply once per person per keyword. Never as Chang or Sun in the first person about pain. "
             "Crisis words → the safety protocol (SAFETY_RULES). Replace {first_name}; links come from /admin/today.", ""]
    for kw in keywords or sorted(flows):
        if kw in flows:
            # a person is sending it, so the "(automated)" sender label would be false; keep the AI-character line
            text = re.sub(r"team assistant \(automated\)", "team (a real person on our team)", manual_reply(flows[kw]))
            lines += [f"## {kw}", "", text, ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual-replies", help="write the manual reply sheet for the day-1 keywords here")
    a = ap.parse_args(argv)
    r = run()
    print(f"keyword registry: {len(r['keywords'])} keywords, {len(r['used'])} in use; "
          f"{len(r['errors'])} errors, {len(r['warnings'])} warnings")
    for e in r["errors"]:
        print(" ERROR", e)
    for w in r["warnings"][:20]:
        print(" warn ", w)
    if a.manual_replies:
        flows, _ = load_flows()
        plan = json.loads((ROOT / "production" / "launch_day" / "day1_plan.json").read_text(encoding="utf-8"))
        kws = sorted({p["cta_keyword"].upper() for p in plan["posts"]})
        Path(a.manual_replies).write_text(manual_sheet(flows, kws), encoding="utf-8")
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
