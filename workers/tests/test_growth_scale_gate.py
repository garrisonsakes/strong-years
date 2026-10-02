"""CANON UPDATE 5 (BLITZ.md §14): the spend gate on TRAILING-7-DAY RETAINED MRR, the all-in cap (0.25 x retained MRR / 30
minus fixed and generation) and the scale-on-MRR ladder (governor.scale_rules). Property tests over 3,000 random states:
the cap is never exceeded, the gate never opens below the threshold, the ladder never steps down."""
from __future__ import annotations

import copy
import random

import pytest

from growth import config as G, governor as GV
from tests.test_growth_governor import NOW, budget, boost, planned_total, state

N_STATES = 3000


@pytest.fixture
def cfg():
    return G.load()


def _t7(hist, cfg):
    w = cfg["governor"]["spend_gate"]["window_days"]
    return sum(hist[-w:]) / w


# ---------------------------------------------------------------- config
def test_defaults_match_canon(cfg):
    g = cfg["governor"]
    assert g["spend_gate"] == {"retained_mrr_usd": 30000, "window_days": 7}
    assert g["all_in_cap"]["share_of_mrr"] == 0.25
    assert [(r["retained_mrr_usd"], r["pages_open"], r["masters_per_page"], r["trial_reels_per_page"], r["generation_tier"])
            for r in g["scale_rules"]] == [(0, 4, 6, 20, "standard"), (10000, 5, 8, 20, "standard"), (30000, 7, 9, 20, "standard"),
                                           (50000, 7, 9, 20, "standard"), (100000, 7, 9, 20, "pro")]


@pytest.mark.parametrize("patch", [
    {"spend_gate": {"retained_mrr_usd": 29999, "window_days": 7}},                 # gate may only be raised
    {"spend_gate": {"retained_mrr_usd": 30000, "window_days": 0}},
    {"all_in_cap": {"share_of_mrr": 0.31}}, {"all_in_cap": {"share_of_mrr": 0.19}},
])
def test_validate_refuses_gate_and_cap_outside_canon(cfg, patch):
    bad = copy.deepcopy(cfg)
    bad["governor"].update(patch)
    with pytest.raises(ValueError):
        G.validate(bad)


@pytest.mark.parametrize("mutate", [
    lambda r: r[1].update(retained_mrr_usd=0),                       # thresholds must strictly increase
    lambda r: r[2].update(pages_open=3),                             # capacity may never fall as MRR rises
    lambda r: r[4].update(generation_tier="standard") or r[3].update(generation_tier="pro") or r[4].update(generation_tier="cheap"),
    lambda r: r[2].update(masters_per_page=12),                      # above allocator.max_cadence
    lambda r: r[2].update(trial_reels_per_page=25),                  # above the 20/page/day cap
    lambda r: r[0].update(retained_mrr_usd=5000),                    # must start at $0
    lambda r: r[1].update(pages_open=True),
])
def test_validate_refuses_a_broken_ladder(cfg, mutate):
    bad = copy.deepcopy(cfg)
    mutate(bad["governor"]["scale_rules"])
    with pytest.raises(ValueError):
        G.validate(bad)


def test_scale_rules_are_protected_from_request_overrides():
    with pytest.raises(G.ProtectedOverride):
        G.load({"governor": {"spend_gate": {"retained_mrr_usd": 0}}})


# ---------------------------------------------------------------- gate and cap
def test_gate_closed_below_30k_trailing_retained_even_with_booked_mrr_far_above(cfg):
    # booked MRR is irrelevant: only the retained series is read; 6 days at $34K + 1 unreported day = $29,143 t7
    st = state(mrr={"retained_daily_usd": [34000] * 6}, booked_mrr_usd=900000)
    d = GV.decide(st, cfg, now=NOW)
    assert d["valid"] and d["status"] == "STOP" and planned_total(d) == 0 and not d["spend_gate"]["open"]
    assert any("spend gate closed" in r for r in d["reasons"])
    d = GV.decide(state(mrr={"retained_daily_usd": [29999.99] * 7}), cfg, now=NOW)
    assert planned_total(d) == 0 and not d["spend_gate"]["open"]
    d = GV.decide(state(mrr={"retained_daily_usd": [30000] * 7}), cfg, now=NOW)
    assert d["spend_gate"]["open"]


def test_no_mrr_report_means_gate_closed(cfg):
    st = state()
    del st["mrr"]
    d = GV.decide(st, cfg, now=NOW)
    assert d["valid"] and planned_total(d) == 0 and d["spend_gate"]["trailing_retained_mrr_usd"] == 0


def test_all_in_cap_binds_below_the_budget_caps(cfg):
    # $36K retained -> 0.25 x 36000 / 30 = $300/day all-in; minus $16 fixed and $112 generation = $172 of paid room
    st = state(mrr={"retained_daily_usd": [36000] * 7}, budget=budget(daily_cap_usd=5000, monthly_cap_usd=90000))
    d = GV.decide(st, cfg, now=NOW)
    assert d["all_in_cap"]["cap_daily_usd"] == 300.0 and d["all_in_cap"]["room_usd"] == 172.0
    assert planned_total(d) == pytest.approx(172.0, abs=0.011)
    assert d["boosts"][0]["approved_daily_usd"] == 100.0 and d["retarget"]["next_daily_usd"] == 72.0 and d["cold"]["next_daily_usd"] == 0.0
    # money already spent today counts against the same room
    st["cash"]["spent_today_usd"] = 150
    assert planned_total(GV.decide(st, cfg, now=NOW)) <= 22.01


def test_unknown_costs_leave_no_paid_room(cfg):
    st = state(costs={})
    d = GV.decide(st, cfg, now=NOW)
    assert d["valid"] and planned_total(d) == 0 and "not reported" in d["all_in_cap"]["why"]


@pytest.mark.parametrize("junk", [{"retained_daily_usd": [float("nan")]}, {"retained_daily_usd": [-1]}, {"retained_daily_usd": "x"},
                                  {"retained_daily_usd": [2e9]}, "junk"])
def test_junk_mrr_is_a_zero_stop_plan(cfg, junk):
    d = GV.decide(state(mrr=junk), cfg, now=NOW)
    assert not d["valid"] and planned_total(d) == 0 and d["status"] == "STOP"


# ---------------------------------------------------------------- ladder
def test_ladder_steps_up_on_trailing_retained_and_never_down(cfg):
    sp = GV.scale_plan({"mrr": {"retained_daily_usd": [12000] * 7}, "ladder": {"level": 0}}, cfg)
    assert sp["level"] == 1 and sp["stepped_up"] and sp["pages_open"] == 5 and sp["cadence"] == 8 and sp["trial_reels_per_page"] == 20
    sp = GV.scale_plan({"mrr": {"retained_daily_usd": [12000] * 6}, "ladder": {"level": 0}}, cfg)   # 6 days: $10,286 t7 -> 1
    assert sp["level"] == 1
    sp = GV.scale_plan({"mrr": {"retained_daily_usd": [12000] * 5}, "ladder": {"level": 0}}, cfg)   # 5 days: $8,571 -> 0
    assert sp["level"] == 0
    sp = GV.scale_plan({"mrr": {"retained_daily_usd": [500] * 7}, "ladder": {"level": 4}}, cfg)     # MRR fell: no step down
    assert sp["level"] == 4 and sp["generation_tier"] == "pro" and sp["why"]
    sp = GV.scale_plan({"mrr": {"retained_daily_usd": [200000] * 7}, "ladder": {"level": 1, "reach_anomaly": True}}, cfg)
    assert sp["level"] == 1 and sp["paused"] and not sp["stepped_up"]
    sp = GV.scale_plan({"mrr": {"retained_daily_usd": [200000] * 7}, "ladder": {"level": 1}}, cfg)
    assert sp["level"] == 4 and sp["row"] == G.scale_rules(cfg)[4]


def test_decision_carries_the_scale_row(cfg):
    d = GV.decide(state(ladder={"level": 2}), cfg, now=NOW)
    assert d["scale"]["level"] == 4 and d["scale"]["masters_per_page"] == 9


# ---------------------------------------------------------------- property tests: 3,000 random states
def _rand_hist(rng):
    n = rng.randint(0, 10)
    base = rng.choice([0, 5000, 9999, 10000, 29999.99, 30000, 30001, 45000, 60000, 120000, 2e6])
    return [max(0.0, base * rng.uniform(0.6, 1.4)) if rng.random() < 0.7 else base for _ in range(n)]


def _rand_scale_state(rng):
    m = rng.choice([0, 1, 50, 100, 250, 500, 1000, 5000, 8000, 50000])
    st = state(mrr={"retained_daily_usd": _rand_hist(rng)},
               costs={"fixed_daily_usd": rng.choice([0, 16, 40, 400]), "generation_daily_usd": rng.choice([0, 40, 112, 900])},
               budget=budget(daily_cap_usd=rng.choice([0, 100, 500, 5000, 50000]), monthly_cap_usd=rng.choice([0, 9000, 900000])),
               cash={"balance_usd": rng.choice([0, 25000, 80000, 900000]), "spent_today_usd": rng.choice([0, 0, 50, 300]),
                     "spent_month_usd": rng.choice([0, 1000]), "line_180d_usd": 1e5},
               current={"cold_daily_usd": rng.choice([0, 50, 1000, 8000]), "retarget_daily_usd": rng.choice([0, 200]),
                        "retarget_requested_usd": rng.choice([0, 200, 1000])},
               boosts=[boost(post_id=f"b{i}", requested_daily_usd=m, approval={"by": "g", "at": "2026-10-14T00:00:00Z", "max_daily_usd": m})
                       for i in range(rng.randint(0, 4))],
               ladder={"level": rng.randint(0, 4), "reach_anomaly": rng.random() < 0.2})
    if rng.random() < 0.3:
        st["daily"] = [{"day": "d", "paid_media_usd": 4500, "paid_net_new_members": rng.choice([10, 50])}] * 3
    return st


def test_property_cap_gate_and_ladder_over_3000_random_states(cfg):
    rng = random.Random(20261002)
    thr = cfg["governor"]["spend_gate"]["retained_mrr_usd"]
    share = cfg["governor"]["all_in_cap"]["share_of_mrr"]
    n_open = n_spend = n_closed = n_up = 0
    for _ in range(N_STATES):
        st = _rand_scale_state(rng)
        d = GV.decide(st, cfg, now=NOW)
        assert d["valid"]
        total = planned_total(d)
        t7 = _t7(st["mrr"]["retained_daily_usd"], cfg)
        # gate never opens below the threshold
        assert d["spend_gate"]["open"] == (t7 >= thr)
        if t7 < thr:
            assert total == 0
            n_closed += 1
        else:
            n_open += 1
            n_spend += total > 0
        # the all-in cap is never exceeded
        room = share * t7 / 30 - st["costs"]["fixed_daily_usd"] - st["costs"]["generation_daily_usd"] - st["cash"]["spent_today_usd"]
        assert total <= max(0.0, room) + 0.011
        # ladder monotonic: never below the level it was given; paused on a reach anomaly
        lv0 = st["ladder"]["level"]
        sp = d["scale"]
        assert sp["level"] >= lv0
        if st["ladder"]["reach_anomaly"]:
            assert sp["level"] == lv0
        else:
            assert sp["level"] == max(lv0, G.scale_level_for(t7, cfg))
        n_up += sp["stepped_up"]
    assert n_open > 500 and n_closed > 500 and n_spend > 150 and n_up > 300     # every branch exercised


def test_property_ladder_is_monotonic_along_random_mrr_paths(cfg):
    rng = random.Random(7)
    for _ in range(N_STATES // 30):
        hist, level = [], 0
        for _day in range(30):
            hist.append(max(0.0, (hist[-1] if hist else rng.choice([0, 20000, 60000])) * rng.uniform(0.7, 1.4) + rng.choice([0, 3000])))
            sp = GV.scale_plan({"mrr": {"retained_daily_usd": hist[-7:]}, "ladder": {"level": level, "reach_anomaly": rng.random() < 0.1}}, cfg)
            assert sp["level"] >= level
            level = sp["level"]
