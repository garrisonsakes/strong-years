"""Launch-tomorrow tools (ENGINE_SAVAGE20 §B(b) 7–8 and #1): CANON 6 topology + per-account .ics, secret scan,
product library -> briefs. python3 -m pytest tools/test_launch_tools.py -q
"""
from __future__ import annotations

import collections
import importlib.util
import sys
from datetime import date
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "workers")]

import product_to_scripts as P  # noqa: E402
import slots_ics  # noqa: E402
import topology as T  # noqa: E402

LAUNCH = date(2026, 10, 3)


def _load_secrets():
    spec = importlib.util.spec_from_file_location("check_secrets", ROOT / "deploy" / "scripts" / "check_secrets.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ 7. topology + calendar
def test_canon6_accounts_and_steady_state_on_day7():
    by = collections.Counter(a["platform"] for a in T.ACCOUNTS)
    assert by == {"instagram": 4, "threads": 4, "x": 4, "tiktok": 4, "facebook": 1, "youtube": 1}
    assert {a["handle"] for a in T.ACCOUNTS if a["platform"] == "instagram"} == {
        "@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength"}
    d7 = [r for r in T.rows_for_day(LAUNCH, 7)]
    per = collections.Counter((r["page"], r["platform"]) for r in d7)
    for a in T.ACCOUNTS:
        for lane in T.ACCOUNT_LANES[a["platform"]]:
            assert per[(a["account"], lane)] == T.STEADY[lane], (a["account"], lane)
    assert sum(per.values()) == 4 * (6 + 20 + 3 + 12 + 6 + 26) + 16 + 4


def test_day1_ramp_uses_the_rendered_posts_and_no_trials():
    d1 = T.rows_for_day(LAUNCH, 1)
    ig = [r for r in d1 if r["platform"] == "ig_reels"]
    assert sorted(r["file_id"] for r in ig if r["file_id"]) == sorted(
        p["post_id"] for p in T.day1_posts())                      # all 6 day-1 renders, on their own pages
    assert not [r for r in d1 if r["platform"] == "ig_trial"]
    assert [r["file_id"] for r in d1 if r["platform"] == "fb_reels"] == ["D1-CY-1", "D1-SK-1"]   # ONE FB page
    stories = [r for r in d1 if r["platform"] == "ig_story"]
    assert len(stories) == 4 and all(r["variant_role"] == "STORY" for r in stories)
    for i in range(1, 8):                                          # hook pre-screen: 10 Threads probes every day
        rows = T.rows_for_day(LAUNCH, i)
        assert sum(r["variant_role"] == "TEXT_PROBE" for r in rows if r["platform"] == "threads") == 10
    totals = [len(T.rows_for_day(LAUNCH, i)) for i in range(1, 8)]
    assert totals == sorted(totals) and totals[0] < totals[-1] / 4


def test_no_account_posts_twice_in_the_same_minute_and_week_ics_per_account(tmp_path):
    rows = T.week(LAUNCH)
    keys = collections.Counter((r["date"], r["page"], r["slot_et"]) for r in rows)
    assert [k for k, n in keys.items() if n > 1] == []
    w = slots_ics.export(LAUNCH, tmp_path, rows=rows)
    assert set(w) == {a["account"] for a in T.ACCOUNTS}
    uids = []
    for f in tmp_path.glob("*.ics"):
        txt = f.read_bytes().decode()
        assert txt.startswith("BEGIN:VCALENDAR\r\n") and txt.endswith("END:VCALENDAR\r\n")
        assert all(len(line.encode()) <= 75 for line in txt.split("\r\n"))
        if f.name.endswith("_week.ics"):
            uids += [line for line in txt.split("\r\n") if line.startswith("UID:")]
    assert len(uids) == len(set(uids)) == len(rows)
    ig = (tmp_path / "ig_changyin_tomorrow.ics").read_text()
    assert "Instagram Story" in ig and "D1-CY-1" in ig and "TZID=America/New_York:20261003T" in ig


# ------------------------------------------------------------------ 8. secret scan
def test_secret_scan_flags_keys_in_a_patch_and_passes_the_repo():
    cs = _load_secrets()
    fake = "sk-ant-" + "a1B2" * 10
    patch = f"diff --git a/x.py b/x.py\n+++ b/x.py\n@@ -0,0 +1 @@\n+API = '{fake}'\n"
    hits = cs.scan_patch(patch, "staged")
    assert hits and all(fake not in h for h in hits)                # names the finding, never prints the value
    assert cs.scan_patch(patch.replace(fake, "os.environ['ANTHROPIC_API_KEY']"), "staged") == []
    assert cs.check_repo() == []
    assert (ROOT / "deploy" / "hooks" / "pre-commit").read_text().count("--staged") == 1
    assert "check_secrets.py --repo-only --history" in (ROOT / ".github" / "workflows" / "ci.yml").read_text()


# ------------------------------------------------------------------ 9. product library -> briefs
@pytest.fixture(scope="module")
def briefs():
    return P.build(300)


def test_product_library_yields_300_plus_gated_briefs(briefs):
    assert briefs["ok"] and briefs["kept"] >= 300
    ds = briefs["distinct_sources"]
    assert ds["session_days"] == 30 and ds["program"] == 6 and ds["recipe"] == 50
    assert set(briefs["by_grammar"]) == set(P.GRAMMARS)
    kws = P.registry_keywords()
    hooks = [b["hook_line"] for b in briefs["briefs"]]
    assert len(hooks) == len(set(hooks))
    for b in briefs["briefs"][::37]:                                 # spot re-check against every gate
        v = P.virality.score(b)
        assert v["pass"] and v["score"] >= P.virality.THRESHOLD
        assert P.scanner.scan(b)["verdict"] == "pass"
        assert P.external.check_external(b)["allow"]
        assert b["cta_keyword"] in kws and b["origin"] == "product" and b["status"] == "idea"
        assert "AI character" in b["caption"]
