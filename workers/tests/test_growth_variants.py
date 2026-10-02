"""Modular variants + Trial Reels (growth/variants.py, uniqueness.guard.check_variant)."""
from datetime import datetime, timedelta, timezone

import pytest

from growth import config as G
from growth import variants as V
from uniqueness import guard

NOW = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
M = {"master_id": "UG-CY-+12-1", "page": "@changyin", "duration_s": 42, "hook_grammar": "IF_EVERY", "pillar": "P01",
     "format": "F02", "character": "CHANG", "hook_text": "If you stand up five times",
     "hook_pool": [{"id": f"H-alt{k}", "text": f"alt hook {k}"} for k in range(3)]}


def test_generated_tests_differ_in_two_dims_incl_opening_and_one_auto_graduation():
    vs = V.assign_trial_params(V.generate(M, 6))
    assert len(vs) == 6 and all(v["variant_role"] == "TEST" and v["surface"] == "ig_trial" for v in vs)
    for i, v in enumerate(vs):
        assert len(v["dims_changed"]) >= 2 and set(v["dims_changed"]) & V.OPENING_DIMS
        for o in vs[:i]:
            assert len(V.dims_changed(v["signature"], o["signature"])) >= 2
    assert [v["trial_params"]["graduation_strategy"] for v in vs].count("SS_PERFORMANCE") == 1
    assert sum(v["cost_usd"] for v in vs) == pytest.approx(0.45 * sum("new_hook" in v["ops"] for v in vs) +
                                                           0.02 * sum("character_swap_vo" in v["ops"] for v in vs))
    # the first-14-days IG placement already auto-graduates: every trial of that body is MANUAL
    vs2 = V.assign_trial_params(V.generate(M, 2), {("@changyin", vs[0]["body_id"])})
    assert {v["trial_params"]["graduation_strategy"] for v in vs2} == {"MANUAL"}


def test_placement_fb_native_long_cut_and_remix():
    fb = V.placement(M, "facebook")
    assert fb["variant_role"] == "PLACEMENT" and fb["upload"] == "native_fb_video_reels"
    assert fb["share_to_facebook_from_ig"] is False and fb["close_line"] == V.CLOSE_BY_PLATFORM["facebook"]
    assert V.placement(M, "instagram")["share_to_facebook"] is False
    lc = V.fb_long_cut(M)
    assert 60 <= lc["length_s"] <= 180 and lc["body_id"] == fb["body_id"]      # the long cut IS the FB placement
    r = V.remix(M, 0)
    assert r["variant_role"] == "REMIX" and r["body_id"] != fb["body_id"] and len(r["dims_changed"]) >= 3


def test_trial_ramp_budget_and_config_limits():
    assert [V.trial_cap(a) for a in (-1, 0, 13, 14, 20, 21, 60)] == [0, 3, 3, 6, 6, 12, 12]
    assert V.trial_budget(40, trials_today=5, ig_published_24h=10) == 7
    assert V.trial_budget(40, trials_today=0, ig_published_24h=89) == 1          # hard stop 90 < API 100
    assert V.trial_cap(40, G.load({"variants": {"trial_reels_per_page_day": 20}})) == 20
    with pytest.raises(ValueError):
        G.load({"variants": {"trial_reels_per_page_day": 21}})
    with pytest.raises(ValueError):
        G.load({"variants": {"ig_publish_hard_stop": 100}})


def test_body_rule_and_guard_gate():
    p = {**V.placement(M, "tiktok"), "scheduled_at": NOW.isoformat()}
    led = [{"page": "@changyin", "surface": "tiktok", "body_id": p["body_id"], "at": (NOW - timedelta(days=10)).isoformat()}]
    assert V.body_rule_violations([p], led, now=NOW)
    led[0]["at"] = (NOW - timedelta(days=31)).isoformat()
    assert not V.body_rule_violations([p], led, now=NOW)
    # guard: same body twice on one feed surface, low-value edit, opening unchanged
    assert not guard.check_variant(p, [{**p, "variant_id": "other"}], now=NOW)["allow"]
    t = V.generate(M, 1)[0]
    low = {**t, "variant_id": "low", "signature": {**t["signature"], "caption": "story_first"}}
    r = guard.check_variant(low, [t], now=NOW)
    assert not r["allow"] and any("low-value edit" in x for x in r["reasons"])
    cap_only = {**t, "variant_id": "cap", "dims_changed": ["caption", "length"]}
    assert any("opening" in x for x in guard.check_variant(cap_only, [], now=NOW)["reasons"])
    acc, rej = V.gate(V.generate(M, 4) + [V.placement(M, "instagram")], [], now=NOW)
    assert len(acc) == 5 and not rej


def test_graduation_feed_gets_each_body_once():
    trials = [{"variant_id": "a", "page": "p", "body_id": "B1", "composite_6h": 61},
              {"variant_id": "b", "page": "p", "body_id": "B1", "composite_6h": 72},
              {"variant_id": "c", "page": "p", "body_id": "B2", "composite_6h": 40},
              {"variant_id": "d", "page": "p", "body_id": "B3", "auto_graduated": True, "composite_6h": 80},
              {"variant_id": "e", "page": "p", "body_id": "B4", "composite_6h": 90}]
    out = {d["body_id"]: d for d in V.graduate(trials, 50.0, [{"page": "p", "surface": "instagram", "body_id": "B4"}])}
    assert out["B1"]["action"] == "graduate" and out["B1"]["variant_id"] == "b"
    assert out["B2"]["action"] == "keep_master"
    assert out["B3"]["action"] == "skip_placement"
    assert out["B4"]["action"] == "already_in_feed"
