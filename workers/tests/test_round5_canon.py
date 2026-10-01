"""AUDIT_FINAL round 5: BRIEF.md CANON UPDATE hard lines in the publish path.

Before this fix the deterministic scanner had no rule for fall-prevention / fall-reduction claims,
"you"-directed mortality claims or condition hashtags, and the packager kept "#FallPrevention" in the
Instagram hashtags (it published with pass2_ok=True whenever the LLM judge passed).
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from compliance import rules as R
from compliance import scanner
from packager.packager import norm_hashtags
from tests.conftest import AUTH
from tests.test_packaging import LLM, SCRIPT

BLOCK = [
    "#ReverseDiabetes naturally",
    "This routine\ncuts\nyour fall\nrisk in half",
    "Skip this and you\nwill die\nsooner",
    "#fallprevention",
    "you'll fall less",
    "cuts your fall risk",
    "Do this and you'll never fall again",
    "Walk daily and you will live longer",
    "Protein adds years to your life",
    "Fewer\nfalls in 12 weeks",
    "#FearOfFalling #over60",
    "This lowers your risk of dying early",
]
PASS = [
    "I fell asleep during the breathing exercise",
    "Hold the counter. Breathe out as you stand.",
    "Leaves fall in October, soup season starts.",
    "In a 24-week class study (E14), people practised tai chi twice a week.",
    "#balancetraining #strengthafter60 #over60",
    "Train your balance with the counter nearby.",
    "If you have fallen recently, ask your doctor first.",
    "Kimchi keeps. Fall is kimchi season.",
]


@pytest.mark.parametrize("text", BLOCK)
def test_round5_canon_claims_block(text):
    r = scanner.scan(text=text)
    assert r["verdict"] == "block", (text, r["blocks"])
    assert {b["rule"] for b in r["blocks"]} & {"CANON-FALL", "CANON-MORT", "CANON-HASHTAG"}, r["blocks"]


@pytest.mark.parametrize("text", PASS)
def test_round5_canon_benign_pass(text):
    r = scanner.scan(text=text, evidence=["E14"])
    assert r["verdict"] != "block", (text, r["blocks"])


def test_round5_packager_drops_condition_hashtags():
    tags, notes = norm_hashtags(["#FallPrevention", "#kneepain", "#balance", "#over60", "#seniorfitness"], (3, 5))
    assert tags == ["#balance", "#over60", "#seniorfitness"]
    assert any("condition tag" in n for n in notes)


def test_round5_package_never_publishes_fallprevention(judge_pass):
    from app import app
    r = TestClient(app, headers=AUTH).post("/package", json={"packaging": LLM, "script": SCRIPT, "burned_in_text": ["AI character"]})
    assert r.status_code == 200
    ig = r.json()["packaging"]["instagram"]
    assert "#fallprevention" not in ig["hashtags"] and "#fallprevention" not in ig["caption"].lower()


def test_round5_tag_lists_are_scanned():
    r = scanner.scan(None, pass_no=2, packaging={"youtube": {"title": "Chair test", "tags": ["over60", "kneepain"]}},
                     burned_in_text=["AI character"])
    assert "CANON-HASHTAG" in {b["rule"] for b in r["blocks"]}


def test_round5_condition_hashtag_list_matches_build_content():
    path = Path(__file__).resolve().parents[2] / "tools" / "build_content.py"
    src = path.read_text()
    start = src.index('CONDITION_HASHTAG = re.compile(r"') + len('CONDITION_HASHTAG = re.compile(r"')
    gen = src[start:src.index('", re.I)', start)]
    assert gen == R.CONDITION_HASHTAG_PATTERN, "keep workers/compliance/rules.py and tools/build_content.py in sync"


# ---------------------------------------------------------------- Round 5 (Shopify launch path) additions
import pytest as _pt
from compliance.scanner import scan as _scan


@_pt.mark.parametrize("text,rule", [
    ("Price locked for life.", "CANON-FORLIFE"),
    ("Price locked for life.", "CANON-FORLIFE"),
    ("Founding price locked for  life of your membership", "CANON-FORLIFE"),
    ("Try it for $1 for 7 days.", "CANON-TRIAL"),
    ("Try it for ＄ 1 today.", "CANON-TRIAL"),
    ("Join the 7-day trial", "CANON-TRIAL"),
    ("Start your free trial", "CANON-TRIAL"),
    ("Only 37 founding spots left, closes at midnight!", "T-04"),
    ("Normally $99, today $12", "T-04"),
    ("\"My knees haven't hurt since week 2.\" — Linda, 68, member since March", "T-01b"),
    ("“I sleep through the night now.” - Ruth K., member since 2026", "T-01b"),
])
def test_round5_canon_rules_block(text, rule):
    r = _scan(text=text, kind="snippet")
    assert rule in [b["rule"] for b in r["blocks"]], r["blocks"]


@_pt.mark.parametrize("text", [
    "In a 204-person trial, tai chi matched physical therapy.",
    "trial and error in the kitchen",
    "Learning to cook is a skill for life.",
    "Eggs cost about $1.50 a dozen here.",
    "$1 a pound for cabbage",
    "Only 3 ingredients. Spots of oil on the pan.",
    "Eat like you're not in a hurry.",
    "\"Breathe out when you push,\" Chang says, 74.",
])
def test_round5_canon_rules_pass_benign(text):
    r = _scan(text=text, kind="snippet")
    assert not [b for b in r["blocks"] if b["rule"] in ("CANON-TRIAL", "CANON-FORLIFE", "T-04", "T-01b")], r["blocks"]
