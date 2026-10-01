"""Spend governor (growth/governor): a pure function that NEVER calls an ad API. Property tests over random and
adversarial states prove the invariants in the module docstring (I1-I8): caps can't be exceeded, boosts need
WINNER + compliance pass + judge + human approval, cold needs the BLITZ §11 gate, bad input -> zero plan, the
executor refuses in every environment, and the audit log is append-only and hash-chained."""
from __future__ import annotations

import copy
import itertools
import json
import math
import random
from datetime import datetime, timedelta, timezone

import pytest

from growth import config as G, governor as GV

NOW = datetime(2026, 10, 15, 6, 0, tzinfo=timezone.utc)


def budget(**k):
    d = {"id": "bud-1", "daily_cap_usd": 500, "monthly_cap_usd": 9000, "cash_floor_usd": 20000, "status": "approved",
         "approved_by": "garrison", "approved_at": "2026-10-01T00:00:00Z", "expires_at": "2026-12-31T00:00:00Z"}
    d.update(k)
    return d


def boost(post_id="w1", **k):
    d = {"post_id": post_id, "class": "WINNER", "compliance_verdict": "pass", "judge_passed": True, "requested_daily_usd": 120,
         "approval": {"by": "garrison", "at": "2026-10-14T00:00:00Z", "max_daily_usd": 100}}
    d.update(k)
    return d


def state(**k):
    d = {"price_usd": 25, "campaign_day": 12,
         "budget": budget(), "cash": {"balance_usd": 80000, "spent_today_usd": 0, "spent_month_usd": 1000, "line_180d_usd": 100000},
         "current": {"cold_daily_usd": 0, "retarget_daily_usd": 200, "retarget_requested_usd": 200},
         "daily": [{"day": f"2026-10-{d:02d}", "paid_media_usd": 4500, "paid_net_new_members": 50} for d in range(7, 15)],
         "refund_rate_14d": 0.05, "chargeback_rate_30d": 0.001, "chargeback_count_30d": 3,
         "renewal1": {"rate": 0.62, "cohort_n": 400},
         "graduation": {"charge_today_purchases": 800, "factor": 0.7, "media_cost_case": "central", "days_at_min_spend": 8},
         "boosts": [boost()]}
    d.update(k)
    return d


@pytest.fixture
def cfg():
    return G.load()


def planned_total(d: dict) -> float:
    return sum(b["approved_daily_usd"] for b in d["boosts"]) + d["retarget"]["next_daily_usd"] + d["cold"]["next_daily_usd"]


def check_invariants(st: dict, d: dict, cfg: dict) -> None:
    g = cfg["governor"]
    assert d["mode"] == "dry_run"                                        # tests never enable spend
    assert d["status"] in ("SCALE", "HOLD", "CUT", "STOP")
    total = planned_total(d)
    assert math.isclose(total, d["totals"]["planned_daily_usd"], abs_tol=0.011)
    assert total >= 0 and all(b["approved_daily_usd"] >= 0 for b in d["boosts"])
    assert d["retarget"]["next_daily_usd"] >= 0 and d["cold"]["next_daily_usd"] >= 0
    if not d["valid"]:
        assert total == 0 and d["status"] == "STOP" and d["boosts"] == []
        return
    v, errs = GV.validate_state(st, cfg, NOW)
    assert errs == []
    # I1: never above the daily cap, the monthly cap or the cash headroom
    assert total <= max(0.0, v["daily_cap_usd"] - v["spent_today_usd"]) + 0.011
    assert total <= max(0.0, v["monthly_cap_usd"] - v["spent_month_usd"]) + 0.011
    assert total <= max(0.0, v["balance_usd"] - v["cash_floor_usd"]) + 0.011
    # I2 / I3: boosts
    by_id = {b["post_id"]: b for b in v["boosts"]}
    for b in d["boosts"]:
        src = by_id[b["post_id"]]
        if b["status"] == "approved":
            assert src["class"] == "WINNER" and src["compliance_verdict"] == "pass" and src["judge_passed"]
            assert src["approval"] and src["approval"]["by"] and src["approval"]["max"] is not None
            assert b["approved_daily_usd"] <= min(src["requested"], src["approval"]["max"], g["max_boost_daily_usd"]) + 0.011
        else:
            assert b["approved_daily_usd"] == 0
    # I4 / I5: cold
    cold = d["cold"]["next_daily_usd"]
    grad = d["gates"]["graduation"]["passed"]
    if d["status"] == "STOP":
        assert total == 0
    if not grad and float(g.get("pre_gate_cold_daily_usd", 0) or 0) == 0:
        assert cold == 0
    if grad:
        cur = v["cold_daily_usd"]
        if d["status"] == "SCALE":
            assert cold <= (cur * (1 + g["scale_step"]) if cur > 0 else g["initial_daily_usd"]) + 0.011
        elif d["status"] == "HOLD":
            assert cold <= cur + 0.011
        elif d["status"] == "CUT":
            assert cold <= cur * (1 - g["cut_step"]) + 0.011
        assert cold <= g["max_cold_daily_usd"] + 0.011
    assert d["retarget"]["next_daily_usd"] <= min(v["retarget_requested_usd"], g["max_retarget_daily_usd"]) + 0.011


# ---------------------------------------------------------------- happy path and single rules
def test_default_env_is_dry_run_and_spend_disabled():
    assert G.SPEND_ENABLED is False and G.GROWTH_DRY_RUN is True
    d = GV.decide(state(), now=NOW)
    assert d["mode"] == "dry_run" and d["spend_enabled"] is False


def test_scaling_plan_under_the_envelope(cfg):
    d = GV.decide(state(), cfg, now=NOW)
    assert d["valid"] and d["status"] == "SCALE" and d["gates"]["graduation"]["passed"]
    assert d["boosts"][0]["status"] == "approved" and d["boosts"][0]["approved_daily_usd"] == 100.0   # min(req 120, approval 100, cap 250)
    assert d["retarget"]["next_daily_usd"] == 200.0
    assert d["cold"]["allowed"] and d["cold"]["next_daily_usd"] == cfg["governor"]["initial_daily_usd"]   # first cold day: $50 not $8K
    check_invariants(state(), d, cfg)


def test_cold_steps_up_20pct_per_decision_and_never_above_the_cold_cap(cfg):
    st = state(current={"cold_daily_usd": 1000, "retarget_daily_usd": 0, "retarget_requested_usd": 0}, boosts=[],
               budget=budget(daily_cap_usd=20000, monthly_cap_usd=300000), cash={"balance_usd": 500000, "spent_today_usd": 0,
                                                                                "spent_month_usd": 0, "line_180d_usd": 100000})
    d = GV.decide(st, cfg, now=NOW)
    assert d["cold"]["next_daily_usd"] == 1200.0
    st["current"]["cold_daily_usd"] = 7500
    assert GV.decide(st, cfg, now=NOW)["cold"]["next_daily_usd"] == cfg["governor"]["max_cold_daily_usd"]


def test_cac_hold_and_cut_lines_are_price_aware_and_learning_window_aware(cfg):
    g = cfg["governor"]["lines"]
    # day 12, $25: 4500/30 = $150 -> HOLD (111 < 150 <= 155)
    st = state(daily=[{"day": "d", "paid_media_usd": 4500, "paid_net_new_members": 30}])
    d = GV.decide(st, cfg, now=NOW)
    assert d["status"] == "HOLD" and d["gates"]["rules"]["rules"]["cac"]["status"] == "HOLD"
    assert d["gates"]["rules"]["scale_line"] == g["25"]["scale"]
    # same CAC at $30 -> SCALE (150 > 132 though) -> HOLD; at 4500/36=$125 -> SCALE at $30, HOLD at $25
    st = state(price_usd=30, daily=[{"day": "d", "paid_media_usd": 4500, "paid_net_new_members": 36}])
    assert GV.decide(st, cfg, now=NOW)["gates"]["rules"]["rules"]["cac"]["status"] == "SCALE"
    st["price_usd"] = 25
    assert GV.decide(st, cfg, now=NOW)["gates"]["rules"]["rules"]["cac"]["status"] == "HOLD"
    # learning window (day <= 7): $128 scale line at $25
    st = state(campaign_day=3, daily=[{"day": "d", "paid_media_usd": 4500, "paid_net_new_members": 36}])
    d = GV.decide(st, cfg, now=NOW)
    assert d["gates"]["rules"]["learning_window"] and d["gates"]["rules"]["rules"]["cac"]["status"] == "SCALE"
    # > hold_max one day -> HOLD, two days running -> CUT (-30%)
    over = {"day": "d", "paid_media_usd": 4500, "paid_net_new_members": 20}           # $225
    st = state(daily=[{"day": "a", "paid_media_usd": 4500, "paid_net_new_members": 80}] * 5 + [over],
               current={"cold_daily_usd": 1000, "retarget_daily_usd": 100, "retarget_requested_usd": 100},
               budget=budget(daily_cap_usd=5000, monthly_cap_usd=90000))
    assert GV.decide(st, cfg, now=NOW)["status"] == "HOLD"
    st["daily"].append(over)
    d = GV.decide(st, cfg, now=NOW)
    assert d["status"] == "CUT" and d["cold"]["next_daily_usd"] == 700.0 and d["retarget"]["next_daily_usd"] == 70.0


def test_unknown_price_is_a_zero_plan(cfg):
    d = GV.decide(state(price_usd=27), cfg, now=NOW)
    assert not d["valid"] and planned_total(d) == 0


@pytest.mark.parametrize("field,value,expect", [
    ("refund_rate_14d", 0.10, "HOLD"), ("refund_rate_14d", 0.13, "HOLD"),
    ("chargeback_rate_30d", 0.004, "HOLD"), ("chargeback_rate_30d", 0.005, "STOP"), ("chargeback_count_30d", 75, "STOP"),
    ("chargeback_count_30d", 55, "HOLD"),
])
def test_refund_and_chargeback_rules(cfg, field, value, expect):
    d = GV.decide(state(**{field: value}), cfg, now=NOW)
    assert d["status"] == expect
    if expect == "STOP":
        assert planned_total(d) == 0 and d["boosts"] == []


def test_renewal1_hold_only_inside_its_window_and_cohort(cfg):
    assert GV.decide(state(renewal1={"rate": 0.45, "cohort_n": 400}), cfg, now=NOW)["status"] == "SCALE"   # day 12: not yet
    st = state(campaign_day=30, renewal1={"rate": 0.45, "cohort_n": 400})
    d = GV.decide(st, cfg, now=NOW)
    assert d["status"] == "HOLD" and "renewal1" in d["gates"]["rules"]["rules"]
    assert GV.decide(state(campaign_day=30, renewal1={"rate": 0.45, "cohort_n": 20}), cfg, now=NOW)["status"] == "SCALE"
    assert GV.decide(state(campaign_day=30, renewal1={"rate": None, "cohort_n": 400}), cfg, now=NOW)["status"] == "HOLD"
    assert GV.decide(state(campaign_day=30, renewal1={"rate": 0.6, "cohort_n": 400}), cfg, now=NOW)["status"] == "SCALE"


def test_cash_headroom_rules(cfg):
    cash = {"balance_usd": 80000, "spent_today_usd": 0, "spent_month_usd": 0}
    assert GV.decide(state(cash={**cash, "line_180d_usd": 100000}), cfg, now=NOW)["status"] == "SCALE"      # 60%
    assert GV.decide(state(cash={**cash, "line_180d_usd": 300000}), cfg, now=NOW)["status"] == "HOLD"       # 20%
    d = GV.decide(state(cash={**cash, "line_180d_usd": 1000000}), cfg, now=NOW)                             # 6%
    assert d["status"] == "CUT"
    assert GV.decide(state(cash=cash), cfg, now=NOW)["status"] == "HOLD"                                    # no line -> no scaling


def test_graduation_gate_blocks_cold_until_all_thresholds_pass(cfg):
    base = state(current={"cold_daily_usd": 0, "retarget_daily_usd": 0, "retarget_requested_usd": 0}, boosts=[])
    for bad in ({"graduation": {"charge_today_purchases": 299, "factor": 0.7}},
                {"graduation": {"charge_today_purchases": 800, "factor": 0.6}},             # < 0.64 central at $25
                {"daily": [{"day": "d", "paid_media_usd": 3000, "paid_net_new_members": 20}] * 8},   # not >= $4K/day
                {"daily": [{"day": "d", "paid_media_usd": 4500, "paid_net_new_members": 30}] * 8},   # blended $150 > 111
                {"refund_rate_14d": 0.13}, {"chargeback_rate_30d": 0.004},
                {"campaign_day": 41, "renewal1": {"rate": 0.55, "cohort_n": 400}}):
        d = GV.decide({**base, **bad}, cfg, now=NOW)
        assert d["cold"]["next_daily_usd"] == 0 and not d["cold"]["allowed"], bad
        assert not d["gates"]["graduation"]["passed"]
    # the upside media-cost case lowers the factor line (0.48 at $25)
    d = GV.decide({**base, "graduation": {"charge_today_purchases": 800, "factor": 0.5, "media_cost_case": "upside"}}, cfg, now=NOW)
    assert d["gates"]["graduation"]["passed"]
    # day 41 with renewal 1 >= 58% passes
    d = GV.decide({**base, "campaign_day": 41, "renewal1": {"rate": 0.6, "cohort_n": 400}}, cfg, now=NOW)
    assert d["gates"]["graduation"]["passed"] and d["cold"]["next_daily_usd"] > 0


def test_pre_gate_cold_line_is_a_client_switch_default_off(cfg):
    base = state(graduation={"charge_today_purchases": 10, "factor": 0.1}, boosts=[],
                 current={"cold_daily_usd": 0, "retarget_daily_usd": 0, "retarget_requested_usd": 0})
    assert GV.decide(base, cfg, now=NOW)["cold"]["next_daily_usd"] == 0
    # The client sets this in the operator config file (GROWTH_CONFIG_PATH), never per request (Round 5 audit).
    cfg2 = G.validate(G._deep_merge(G.load(), {"governor": {"pre_gate_cold_daily_usd": 3000}}))
    d = GV.decide(base, cfg2, now=NOW)
    assert d["cold"]["next_daily_usd"] == 500.0 and "clipped" in " ".join(d["cold"]["why"])   # daily cap 500 binds
    d = GV.decide({**base, "budget": budget(daily_cap_usd=5000, monthly_cap_usd=90000)}, cfg2, now=NOW)
    assert d["cold"]["next_daily_usd"] == 3000.0 and "pre-gate" in " ".join(d["cold"]["why"])
    check_invariants(base, GV.decide(base, cfg2, now=NOW), cfg2)


# ---------------------------------------------------------------- boosts: every gate
@pytest.mark.parametrize("patch,reason", [
    ({"class": "PROMISING"}, "not WINNER"), ({"compliance_verdict": "flagged"}, "compliance"),
    ({"compliance_verdict": "human"}, "compliance"), ({"judge_passed": False}, "judge"),
    ({"approval": None}, "approval"), ({"approval": {"by": "", "at": "2026-10-14T00:00:00Z", "max_daily_usd": 100}}, "approval"),
    ({"approval": {"by": "g", "at": None, "max_daily_usd": 100}}, "approval"),
    ({"approval": {"by": "g", "at": "2026-10-14T00:00:00Z"}}, "approval"),
    ({"approval": {"by": "g", "at": "2027-01-01T00:00:00Z", "max_daily_usd": 100}}, "future"),
    ({"requested_daily_usd": float("nan")}, "invalid"), ({"requested_daily_usd": -5}, "invalid"),
    ({"approval": {"by": "g", "at": "2026-10-14T00:00:00Z", "max_daily_usd": float("inf")}}, "invalid"),
])
def test_boost_rejected_without_every_gate(cfg, patch, reason):
    d = GV.decide(state(boosts=[boost(**patch)]), cfg, now=NOW)
    assert d["valid"] and d["boosts"][0]["status"] == "rejected" and d["boosts"][0]["approved_daily_usd"] == 0
    assert any(reason.lower() in r.lower() for r in d["boosts"][0]["reasons"]), d["boosts"][0]["reasons"]


def test_boost_amount_is_the_minimum_of_request_approval_cap_and_envelope(cfg):
    cap = cfg["governor"]["max_boost_daily_usd"]
    d = GV.decide(state(boosts=[boost(requested_daily_usd=10000, approval={"by": "g", "at": "2026-10-14T00:00:00Z", "max_daily_usd": 10000})]),
                  cfg, now=NOW)
    assert d["boosts"][0]["approved_daily_usd"] == cap
    d = GV.decide(state(boosts=[boost(post_id=f"w{i}", requested_daily_usd=250, approval={"by": "g", "at": "2026-10-14T00:00:00Z", "max_daily_usd": 250})
                               for i in range(5)]), cfg, now=NOW)
    amts = [b["approved_daily_usd"] for b in d["boosts"]]
    assert sum(amts) <= 500 and amts[0] == 250 and amts[1] == 250 and amts[2] == 0        # daily cap 500 binds
    assert d["boosts"][2]["status"] == "rejected" and d["retarget"]["next_daily_usd"] == 0 and d["cold"]["next_daily_usd"] == 0


def test_boosts_take_precedence_over_retargeting_and_cold(cfg):
    st = state(budget=budget(daily_cap_usd=150), current={"cold_daily_usd": 1000, "retarget_daily_usd": 200, "retarget_requested_usd": 200})
    d = GV.decide(st, cfg, now=NOW)
    assert d["boosts"][0]["approved_daily_usd"] == 100 and d["retarget"]["next_daily_usd"] == 50 and d["cold"]["next_daily_usd"] == 0
    assert d["totals"]["planned_daily_usd"] == 150.0


# ---------------------------------------------------------------- bad input -> zero plan
@pytest.mark.parametrize("patch", [
    {"budget": None}, {"budget": budget(status="draft")}, {"budget": budget(approved_by="")}, {"budget": budget(approved_at=None)},
    {"budget": budget(expires_at="2026-10-01T00:00:00Z")}, {"budget": budget(expires_at="never")},
    {"budget": budget(daily_cap_usd=float("nan"))}, {"budget": budget(daily_cap_usd=-1)}, {"budget": budget(monthly_cap_usd=float("inf"))},
    {"budget": budget(cash_floor_usd="lots")}, {"budget": budget(daily_cap_usd=10**9)},
    {"cash": {"balance_usd": float("nan"), "spent_today_usd": 0, "spent_month_usd": 0}},
    {"cash": {"balance_usd": 1e9, "spent_today_usd": 0, "spent_month_usd": 0}},
    {"cash": {"balance_usd": 1000, "spent_today_usd": -1, "spent_month_usd": 0}},
    {"cash": {"balance_usd": 1000, "spent_today_usd": 0, "spent_month_usd": 0, "line_180d_usd": -5}},
    {"price_usd": float("nan")}, {"price_usd": "25.5"}, {"price_usd": None}, {"price_usd": 1e9},
    {"campaign_day": -1}, {"campaign_day": float("inf")}, {"campaign_day": "soon"},
    {"current": {"cold_daily_usd": float("nan")}}, {"current": {"retarget_requested_usd": -100}},
    {"daily": [{"day": "d", "paid_media_usd": float("nan"), "paid_net_new_members": 1}]},
    {"daily": [{"day": "d", "paid_media_usd": 100, "paid_net_new_members": -1}]},
    {"refund_rate_14d": 1.5}, {"refund_rate_14d": -0.1}, {"chargeback_rate_30d": "x"}, {"chargeback_count_30d": -1},
    {"renewal1": {"rate": 2, "cohort_n": 100}}, {"graduation": {"factor": float("nan")}},
])
def test_invalid_inputs_give_a_zero_stop_plan(cfg, patch):
    st = state(**patch)
    d = GV.decide(st, cfg, now=NOW)
    assert not d["valid"] and d["status"] == "STOP" and planned_total(d) == 0 and d["boosts"] == []
    assert d["reasons"] and "invalid input" in d["reasons"][0]
    check_invariants(st, d, cfg)


def test_empty_and_junk_states(cfg):
    for st in ({}, None, {"budget": "x"}, {"boosts": "x"}, {"daily": "x"}):
        try:
            d = GV.decide(st, cfg, now=NOW)
        except (TypeError, AttributeError):
            pytest.fail(f"decide crashed on {st!r}")
        assert not d["valid"] and planned_total(d) == 0


def test_zero_envelope_means_zero_plan_but_valid(cfg):
    for cash in ({"balance_usd": 20000, "spent_today_usd": 0, "spent_month_usd": 0, "line_180d_usd": 1e5},
                 {"balance_usd": 80000, "spent_today_usd": 500, "spent_month_usd": 0, "line_180d_usd": 1e5},
                 {"balance_usd": 80000, "spent_today_usd": 0, "spent_month_usd": 9000, "line_180d_usd": 1e5}):
        d = GV.decide(state(cash=cash), cfg, now=NOW)
        assert d["valid"] and planned_total(d) == 0


# ---------------------------------------------------------------- property tests: random and adversarial states
def _rand_money(rng: random.Random, p_bad: float = 0.08):
    if p_bad and rng.random() < p_bad:
        return rng.choice([2e6, -1, float("nan"), float("inf"), None, "x", True, [], {}])
    return rng.choice([0, 1, 49.99, 100, 250, 500, 999.5, 5000, 8000, 50000, 900000])


def _rand_state(rng: random.Random, hostile: bool = True) -> dict:
    pb = 0.08 if hostile else 0.0
    boosts = []
    for i in range(rng.randint(0, 6)):
        appr = rng.choice([None, {"by": rng.choice(["g", ""]), "at": rng.choice(["2026-10-14T00:00:00Z", None, "2027-01-01T00:00:00Z"]),
                                  "max_daily_usd": _rand_money(rng, pb)}])
        boosts.append({"post_id": f"p{i}", "class": rng.choice(G.CLASSES), "compliance_verdict": rng.choice(["pass", "flagged", "human", None]),
                       "judge_passed": rng.choice([True, False, None]), "requested_daily_usd": _rand_money(rng, pb), "approval": appr})
    daily = [{"day": f"d{i}", "paid_media_usd": _rand_money(rng, pb),
              "paid_net_new_members": rng.choice([0, 1, 10, 50, 200] + ([-1, float("nan")] if hostile else []))}
             for i in range(rng.randint(0, 9))]
    bud = budget(daily_cap_usd=_rand_money(rng, pb), monthly_cap_usd=_rand_money(rng, pb), cash_floor_usd=_rand_money(rng, pb),
                 status=rng.choice(["approved"] * 4 + (["draft", "revoked"] if hostile else [])),
                 expires_at=rng.choice(["2026-12-31T00:00:00Z"] * 3 + (["2026-10-01T00:00:00Z", None] if hostile else [])))
    cash = {"balance_usd": _rand_money(rng, pb), "spent_today_usd": _rand_money(rng, pb), "spent_month_usd": _rand_money(rng, pb),
            "line_180d_usd": rng.choice([None, 1e5, 1e5, 1e6] + ([-1, float("nan")] if hostile else []))}
    return {"price_usd": rng.choice([25, 25, 30, 30] + ([27, "25", None, float("nan")] if hostile else [])),
            "campaign_day": rng.choice([0, 3, 7, 8, 12, 26, 40, 41] + ([-1, None] if hostile else [])),
            "budget": rng.choice([bud] * 6 + ([None, "junk", []] if hostile else [])),
            "cash": rng.choice([cash] * 9 + (["junk"] if hostile else [])),
            "current": {"cold_daily_usd": _rand_money(rng, pb), "retarget_daily_usd": _rand_money(rng, pb), "retarget_requested_usd": _rand_money(rng, pb)},
            "daily": rng.choice([daily] * 9 + (["junk"] if hostile else [])),
            "refund_rate_14d": rng.choice([None, 0.0, 0.05, 0.1, 0.2] + ([-1, 2] if hostile else [])),
            "chargeback_rate_30d": rng.choice([None, 0.0, 0.002, 0.004, 0.006]), "chargeback_count_30d": rng.choice([None, 0, 10, 60, 80]),
            "renewal1": {"rate": rng.choice([None, 0.3, 0.55, 0.7]), "cohort_n": rng.choice([0, 50, 500])},
            "graduation": {"charge_today_purchases": rng.choice([0, 100, 300, 1000]), "factor": rng.choice([None, 0.1, 0.5, 0.7, 1.0]),
                           "media_cost_case": rng.choice(["central", "upside"]), "days_at_min_spend": rng.choice([0, 5, 10])},
            "boosts": boosts}


@pytest.mark.parametrize("hostile,min_valid", [(True, 5), (False, 1200)])
def test_property_random_states_never_break_the_invariants(cfg, hostile, min_valid):
    rng = random.Random(20261001)
    n_valid = 0
    for _ in range(1500):
        st = _rand_state(rng, hostile)
        d = GV.decide(st, cfg, now=NOW)
        check_invariants(st, d, cfg)
        n_valid += d["valid"]
    assert n_valid >= min_valid


def test_exhaustive_envelope_grid_caps_are_never_exceeded(cfg):
    """Every combination of daily cap, monthly room, cash headroom, boost requests and status is within the envelope."""
    grid = itertools.product([0, 100, 250, 500, 5000], [0, 100, 4000, 1e5], [0, 100, 1000, 5e5], [0, 1, 3], ["SCALE", "CUT", "STOP"])
    for daily_cap, month_room, head, n_boosts, status in grid:
        st = state(budget=budget(daily_cap_usd=daily_cap, monthly_cap_usd=month_room + 1000, cash_floor_usd=1000),
                   cash={"balance_usd": 1000 + head, "spent_today_usd": 0, "spent_month_usd": 1000, "line_180d_usd": 100000},
                   current={"cold_daily_usd": 2000, "retarget_daily_usd": 700, "retarget_requested_usd": 700},
                   boosts=[boost(post_id=f"w{i}", requested_daily_usd=300, approval={"by": "g", "at": "2026-10-14T00:00:00Z", "max_daily_usd": 300})
                           for i in range(n_boosts)])
        if status == "CUT":
            st["daily"] = [{"day": "d", "paid_media_usd": 4500, "paid_net_new_members": 10}] * 3
        if status == "STOP":
            st["chargeback_count_30d"] = 80
        d = GV.decide(st, cfg, now=NOW)
        assert d["valid"]
        total = planned_total(d)
        assert total <= min(daily_cap, month_room, head) + 0.011, (daily_cap, month_room, head, n_boosts, status, total)
        if status == "STOP":
            assert total == 0
        check_invariants(st, d, cfg)


def test_cold_never_jumps_more_than_one_step_over_a_long_run(cfg):
    st = state(boosts=[], current={"cold_daily_usd": 0, "retarget_daily_usd": 0, "retarget_requested_usd": 0},
               budget=budget(daily_cap_usd=50000, monthly_cap_usd=900000), cash={"balance_usd": 2e5, "spent_today_usd": 0,
                                                                                "spent_month_usd": 0, "line_180d_usd": 1e5})
    prev = 0.0
    for day in range(40):
        d = GV.decide(st, cfg, now=NOW + timedelta(days=day))
        nxt = d["cold"]["next_daily_usd"]
        assert nxt <= max(prev * 1.2, cfg["governor"]["initial_daily_usd"]) + 0.011 and nxt <= cfg["governor"]["max_cold_daily_usd"]
        prev = nxt
        st["current"]["cold_daily_usd"] = nxt
    assert prev == cfg["governor"]["max_cold_daily_usd"]


# ---------------------------------------------------------------- determinism, audit, executor
def test_decision_is_deterministic_and_input_is_not_mutated(cfg):
    st = state()
    snap = copy.deepcopy(st)
    a, b = GV.decide(st, cfg, now=NOW), GV.decide(copy.deepcopy(st), cfg, now=NOW)
    assert a == b and st == snap and a["state_hash"] == b["state_hash"] and a["config_fingerprint"] == b["config_fingerprint"]
    assert GV.decide(state(campaign_day=13), cfg, now=NOW)["state_hash"] != a["state_hash"]


def test_audit_log_is_append_only_and_hash_chained(cfg, tmp_path):
    path = tmp_path / "audit.jsonl"
    d1 = GV.decide(state(), cfg, now=NOW)
    r1 = GV.append_audit(d1, path=path)
    r2 = GV.append_audit(GV.decide(state(campaign_day=13), cfg, now=NOW), path=path)
    assert r1["prev_hash"] == "0" * 64 and r2["prev_hash"] == r1["hash"]
    assert GV.verify_audit(path) == {"ok": True, "entries": 2}
    lines = path.read_text().splitlines()
    e = json.loads(lines[0])
    e["decision"]["totals"]["planned_daily_usd"] = 999999
    path.write_text(json.dumps(e, sort_keys=True) + "\n" + lines[1] + "\n")
    assert GV.verify_audit(path)["ok"] is False
    assert GV.verify_audit(tmp_path / "missing.jsonl") == {"ok": True, "entries": 0}


def test_executor_refuses_in_every_state_and_never_spends(cfg):
    d = GV.decide(state(), cfg, now=NOW)
    with pytest.raises(GV.GovernorRefused, match="SPEND_ENABLED"):
        GV.execute(d, {"by": "g", "decision_hash": d["state_hash"]})
    with pytest.raises(GV.GovernorRefused, match="DRY_RUN"):
        GV.execute(d, {"by": "g", "decision_hash": d["state_hash"]}, spend_enabled=True)
    live = GV.decide(state(), cfg, spend_enabled=True, dry_run=False, now=NOW)
    assert live["mode"] == "live"
    with pytest.raises(GV.GovernorRefused, match="approval"):
        GV.execute(live, None, spend_enabled=True, dry_run=False)
    with pytest.raises(GV.GovernorRefused, match="approval"):
        GV.execute(live, {"by": "g", "decision_hash": "wrong"}, spend_enabled=True, dry_run=False)
    with pytest.raises(GV.GovernorRefused, match="live plan"):
        GV.execute(d, {"by": "g", "decision_hash": d["state_hash"]}, spend_enabled=True, dry_run=False)   # dry-run plan
    bad = GV.decide(state(price_usd=27), cfg, spend_enabled=True, dry_run=False, now=NOW)
    with pytest.raises(GV.GovernorRefused):
        GV.execute(bad, {"by": "g", "decision_hash": bad["state_hash"]}, spend_enabled=True, dry_run=False)
    # the only path that passes every check still spends nothing: there is no ad client to call
    res = GV.execute(live, {"by": "g", "decision_hash": live["state_hash"]}, spend_enabled=True, dry_run=False)
    assert res["executed"] is False and "no ad API client" in res["reason"]


def test_no_ad_api_hosts_anywhere_in_the_growth_package():
    import pathlib
    src = "\n".join(p.read_text() for p in pathlib.Path(GV.__file__).parent.glob("*.py"))
    for needle in ("/act_", "adaccount", "marketing-api", "business.tiktok.com/open_api", "ads/", "campaigns"):
        assert needle not in src.lower(), needle
