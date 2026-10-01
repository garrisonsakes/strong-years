"""SAFETY_RULES.md §10 (must BLOCK) and §11 (must PASS) self-test cases, parsed from the markdown so the
tests stay in sync with the spec. Falls back to an embedded copy if the file isn't mounted."""
from __future__ import annotations

import re
from pathlib import Path

from common import config

_FALLBACK_BLOCK = [
    "Do this every night and your arthritis will be gone.",
    "My wife put onions in water and her blood pressure dropped instantly.",
    "As a master of qi with 60 years at the temple…",
    "Frank lost 22 pounds with our club.",
    "Hold your breath and push!",
    "5 sit-ups every morning for strong bones.",
    "Stop taking your blood pressure pills, try this instead.",
    "Take 5 g of creatine and your muscles come back.",
    "Studies show 90% of seniors…",
    "Only 3 spots left in the club tonight!",
]
_FALLBACK_PASS = [
    ("In a study of 1,702 adults aged 51 to 75, people who couldn't stand on one leg for 10 seconds had higher death "
     "rates over seven years. It's a warning sign, not a sentence. Hold the counter and practice.", ["E09"]),
    ("Two kiwis a day did as well as prunes for constipation in a small study, with fewer side effects. Go slowly "
     "and drink water.", ["E25"]),
    ("Wall sits lowered resting blood pressure the most of any exercise type, on average, over weeks of practice. "
     "Breathe through it. If your pressure is high, ask your doctor before long holds.", ["E20"]),
]


def _section(md: str, heading: str) -> str:
    m = re.search(r"^## " + re.escape(heading) + r".*?$(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1) if m else ""


def cases() -> tuple[list[tuple[str, list[str], str]], list[tuple[str, list[str], str]]]:
    """Returns (must_block, must_pass) as [(text, evidence_ids, note)]."""
    try:
        md = Path(config.SAFETY_RULES_PATH).read_text()
    except OSError:
        md = ""
    def parse(sec):
        out = []
        for m in re.finditer(r'^\d+\.\s+"(.*?)"(.*)$', sec, re.M):
            txt, tail = m.group(1), m.group(2)
            out.append((txt, re.findall(r"\bE\d{2}b?\b", tail), tail.strip()))
        return out
    blk = parse(_section(md, "10."))
    ok = parse(_section(md, "11."))
    if not blk:
        blk = [(t, [], "") for t in _FALLBACK_BLOCK]
    if not ok:
        ok = [(t, e, "") for t, e in _FALLBACK_PASS]
    return blk, ok


def run() -> dict:
    from compliance.scanner import scan
    blk, ok = cases()
    results = {"must_block": [], "must_pass": []}
    for text, ev, note in blk:
        r = scan(text=text, evidence=ev)
        results["must_block"].append({"text": text, "verdict": r["verdict"], "ok": r["verdict"] == "block",
                                      "rules": sorted({b["rule"] for b in r["blocks"]}), "spec_note": note})
    for text, ev, note in ok:
        r = scan(text=text, evidence=ev)
        results["must_pass"].append({"text": text, "verdict": r["verdict"], "ok": r["verdict"] == "pass",
                                     "evidence": ev, "issues": r["blocks"] + r["rewrites"] + [{"missing": m} for m in r["required_missing"]]})
    results["all_ok"] = all(x["ok"] for x in results["must_block"] + results["must_pass"])
    return results
