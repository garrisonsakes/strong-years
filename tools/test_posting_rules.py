"""VIRALITY_SYSTEM.md §5 posting rules and §2 rubric (python3 -m pytest tools/test_posting_rules.py)."""
import importlib.util
import os
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, f"{name}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PR = _load("posting_rules")
V = _load("virality")


def test_slots_hashtags_trial_reels():
    assert PR.slot_ok("ig_reels", "07:00") and not PR.slot_ok("ig_reels", "23:15")
    assert PR.in_prime("fb_reels", "07:30") == "morning" and PR.in_prime("x", "15:00") is None
    assert PR.hashtag_ok("ig_reels", "#a #b #c #d #e") and not PR.hashtag_ok("ig_reels", "#a #b #c #d #e #f")
    assert not PR.hashtag_ok("threads", "#a #b")
    assert PR.ig_trial_reel("@changyin", -7) and PR.ig_trial_reel("@changyin", 6) and not PR.ig_trial_reel("@changyin", 7)
    assert PR.ig_trial_reel("@sunyoon", 22) and not PR.ig_trial_reel("@sunyoon", 21)


def test_remix_top3_within_24h():
    now = datetime(2026, 10, 9, 12, tzinfo=timezone.utc)
    ps = [{"post_id": f"p{i}", "page_id": "cy", "share_save_z": i, "published_at": (now - timedelta(hours=3)).isoformat()}
          for i in range(5)] + [{"post_id": "old", "page_id": "cy", "share_save_z": 9,
                                 "published_at": (now - timedelta(hours=30)).isoformat()}]
    o = PR.remix_top3(ps, now)
    assert [x["source_post_id"] for x in o] == ["p4", "p3", "p2"]
    assert all(datetime.fromisoformat(x["due_by"]) - now == timedelta(hours=24) for x in o)


def _s(hook, secs=45, tail="Comment STRONG. Send this to your sister. Save it for tomorrow.", **kw):
    beats = [{"t": "0-3", "vo": hook, "ost": "5 REPS", "shot": "lifts a kettlebell"},
             {"t": "3-10", "vo": "Watch what happens in two weeks.", "ost": "", "shot": ""},
             {"t": "40-45", "vo": tail, "ost": "", "shot": ""}]
    return {"id": "T", "beats": beats, "target_seconds": secs, "has_movement": True, **kw}


def test_rubric_orders_hook_classes_by_measured_rel():
    v = V.HOOK_CLASS_VALUE
    assert v["IF_EVERY"] == 1.0 and v["HOWTO"] == 0.2
    assert v["IF_EVERY"] > v["MYTH"] > v["AUTHORITY"] > v["WATCH"] > v["STORY"] > v["STATEMENT"] > v["QUESTION"] > v["HOWTO"]
    good = V.score(_s("If you stand up five times every morning, your legs remember."))
    bad = V.score(_s("How to get stronger legs when you are older and tired all day long?", secs=95, tail="Bye."))
    assert good["pass"] and good["top_decile"] and not bad["pass"]
    assert good["parts"]["first_line"] == V.WEIGHTS["first_line"]          # first clause <= 12 words
    assert bad["parts"]["share"] == 0 and bad["parts"]["length"] < V.WEIGHTS["length"]


def test_refit_gate_dry_run_and_floor():
    R = _load("refit_gate")
    lib = R.load_scripts()
    ids = sorted(lib)[:120]
    rows = [{"script_id": i, "composite": 40 + 4 * V.score(lib[i])["parts"]["share"], "horizon_h": 24} for i in ids]
    assert R.refit(rows[:10], lib)["status"] == "insufficient_data"
    rep = R.refit(rows, lib)
    assert rep["status"] == "ok" and not rep["applied"]
    assert abs(sum(rep["new"].values()) - 100) < 0.05 and min(rep["new"].values()) >= 1.0
    share = next(c for c in rep["changes"] if c["component"] == "share")
    assert share["new"] > share["old"] and share["new"] <= share["old"] * 1.3 + 0.1     # <= 30% per week


def test_trial_cap_ramp_by_page_day():
    assert [PR.trial_cap("@changyin", d) for d in (-7, 6, 7, 13, 14, 40)] == [3, 3, 6, 6, 12, 12]
    assert PR.IG_PUBLISH_HARD_STOP < PR.IG_PUBLISH_LIMIT_24H and PR.fb_long_target(6) == 2 and PR.fb_long_target(3) == 1
