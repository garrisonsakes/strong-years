"""SL-05.1 keyword registry (ENGINE_SAVAGE20 §B(b) 1): every launch keyword has a flow and a manual reply.

  cd production/launch_day && python3 -m pytest tests/test_keywords.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

import keyword_registry as kr  # noqa: E402


def test_registry_is_clean_and_covers_day1():
    r = kr.run()
    assert r["errors"] == []
    plan = json.loads((ROOT / "production" / "launch_day" / "day1_plan.json").read_text(encoding="utf-8"))
    flows, _ = kr.load_flows()
    for p in plan["posts"]:
        kw = p["cta_keyword"].upper()
        assert kw in flows, kw
        assert kr.manual_reply(flows[kw]), f"{kw} has no manual reply text"
    sheet = kr.manual_sheet(flows, sorted({p["cta_keyword"].upper() for p in plan["posts"]}))
    assert all(f"## {p['cta_keyword'].upper()}" in sheet for p in plan["posts"])


def test_dead_reserved_and_duplicate_keywords_fail():
    flows, glob = kr.load_flows()
    bad = dict(flows)
    bad["STOP"] = {"keyword": "STOP", "variants": [], "reply": ["x"]}                       # platform opt-out word
    bad["SOUPS"] = {"keyword": "SOUPS", "variants": [next(iter(flows["SOUP"].get("variants") or ["soup"]))], "reply": ["x"]}
    errs = kr.check(bad, glob, {}, {"NOPE": {"day1:D1-X"}})["errors"]
    assert any("STOP" in e and "reserved" in e for e in errs)
    assert any("NOPE" in e and "no flow" in e for e in errs)                                  # dead keyword on a post
    assert any("claimed by both" in e for e in errs) or "variants" not in flows["SOUP"]
