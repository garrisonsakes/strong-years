"""Rolling baselines (median/MAD, empirical-Bayes shrinkage) and velocity scoring / classes (growth/baselines,
growth/scoring). Adversarial: zero-history page, tiny samples, one-post page, missing components, breakout."""
from __future__ import annotations

import math
import random

import pytest

from growth import baselines as B, config as G, scoring as SC

PUB = "2026-10-01T12:00:00+00:00"


def snap(views, *, h=24, shares=None, saves=None, kw=None, optins=None, members=None, pv=None, clicks=None,
         page="pg1", platform="instagram", post="p", published=PUB) -> dict:
    return {"post_id": post, "page_id": page, "platform": platform, "horizon_h": h, "published_at": published, "views": views,
            "shares": shares, "saves": saves, "keyword_comments": kw, "optins": optins, "members": members,
            "profile_visits": pv, "link_clicks": clicks}


def history(n, median_views=2000, seed=1, **kw):
    rng = random.Random(seed)
    out = []
    for i in range(n):
        v = int(median_views * math.exp(rng.gauss(0, 0.5)))
        out.append(snap(v, shares=int(v * 0.004), saves=int(v * 0.006), kw=int(v * 0.002), post=f"h{i}",
                        published=f"2026-09-{(i % 28) + 1:02d}T12:00:00+00:00", **kw))
    return out


@pytest.fixture
def cfg():
    return G.load()


# ---------------------------------------------------------------- baselines
def test_zero_history_page_gets_the_cold_prior(cfg):
    b = B.compute("new", "tiktok", 24, [], None, cfg)
    assert b["n_posts"] == 0
    c = b["components"]["views"]
    assert c["prior"] == "cold_start" and c["shrink"] == 1.0
    assert math.isclose(c["center"], math.log1p(cfg["baselines"]["prior_views_24h"]["tiktok"]), rel_tol=1e-5)


def test_horizon_curve_scales_the_cold_prior(cfg):
    b1, b24 = B.compute("new", "instagram", 1, [], None, cfg), B.compute("new", "instagram", 24, [], None, cfg)
    assert b1["components"]["views"]["center"] < b24["components"]["views"]["center"]


def test_shrinkage_decreases_with_history(cfg):
    shrinks = [B.compute("pg", "instagram", 24, history(n), None, cfg)["components"]["views"]["shrink"] for n in (0, 1, 5, 30)]
    assert shrinks == sorted(shrinks, reverse=True) and shrinks[0] == 1.0 and shrinks[-1] < 0.25


def test_one_post_page_has_floor_spread_and_is_mostly_prior(cfg):
    b = B.compute("pg", "instagram", 24, [snap(50000)], None, cfg)
    c = b["components"]["views"]
    assert c["n"] == 1 and c["shrink"] > 0.8 and c["spread"] >= cfg["baselines"]["min_spread"]
    assert c["center"] < math.log1p(50000)          # one big post doesn't become the baseline


def test_network_prior_used_once_big_enough(cfg):
    net = history(12, median_views=20000, seed=3)
    b = B.compute("pg", "instagram", 24, [], net, cfg)
    assert b["components"]["views"]["prior"] == "network"
    assert b["components"]["views"]["center"] > B.compute("pg", "instagram", 24, [], None, cfg)["components"]["views"]["center"]
    assert B.compute("pg", "instagram", 24, [], net[:5], cfg)["components"]["views"]["prior"] == "cold_start"


def test_rolling_window_uses_only_the_newest_posts(cfg):
    old = history(30, median_views=100, seed=5)
    new = [{**s, "published_at": "2026-09-30T12:00:00+00:00", "post_id": f"n{i}"} for i, s in enumerate(history(30, median_views=10000, seed=6))]
    b = B.compute("pg", "instagram", 24, old + new, None, cfg)
    assert b["n_posts"] == 30 and b["components"]["views"]["center"] > math.log1p(3000)


def test_robust_to_outliers(cfg):
    hist = history(29) + [snap(10_000_000, post="viral")]
    b = B.compute("pg", "instagram", 24, hist, None, cfg)
    assert b["components"]["views"]["center"] < math.log1p(5000)


def test_components_skip_rates_on_tiny_samples_and_missing_fields(cfg):
    assert set(B.components(snap(20, shares=5, saves=5, kw=5), cfg)) == {"views"}           # < min_views_for_rates
    assert set(B.components(snap(5000), cfg)) == {"views"}                                    # nothing else reported
    c = B.components(snap(5000, shares=20, pv=5, clicks=3), cfg)
    assert "share_rate" in c and "click_through" not in c                                     # pv < min_profile_visits
    assert B.components(snap(None), cfg) == {}
    assert B.components(snap(float("nan")), cfg) == {}


# ---------------------------------------------------------------- scoring
def test_zero_history_page_can_still_be_scored(cfg):
    r = SC.score_post([snap(30000, shares=400, saves=600, kw=120, h=24)], {}, cfg)
    assert r is not None and r["class"] in ("WINNER", "PROMISING") and r["score"] > 0
    assert 0 <= r["reward"] <= 1 and r["history"][0]["baseline_n"] == 0


def test_classes_against_a_real_baseline(cfg):
    base = B.by_key([B.compute("pg1", "instagram", h, history(30, seed=h), None, cfg) for h in G.HORIZONS])
    assert SC.score_post([snap(60000, shares=600, saves=900, kw=200, h=24)], base, cfg)["class"] == "WINNER"
    assert SC.score_post([snap(2000, shares=8, saves=12, kw=4, h=24)], base, cfg)["class"] == "NORMAL"
    r = SC.score_post([snap(80, shares=0, saves=0, kw=0, h=24)], base, cfg)
    assert r["class"] == "LOSER" and r["reward"] < 0.3


def test_winner_needs_six_hours_and_enough_views_and_components(cfg):
    base = B.by_key([B.compute("pg1", "instagram", h, history(30, seed=h), None, cfg) for h in G.HORIZONS])
    r = SC.score_post([snap(60000, shares=600, saves=900, kw=200, h=3)], base, cfg)
    assert r["class"] == "PROMISING" and any("wait" in x for x in r["reasons"])
    r = SC.score_post([snap(500, shares=50, saves=80, kw=30, h=6)], base, cfg)       # tiny but hot: too small to call
    assert r["class"] != "WINNER"
    cfg2 = G.load({"scoring": {"classes": {"WINNER": {"min_components": 3}}}})
    r = SC.score_post([snap(900000, h=6)], base, cfg2)                                # views only -> but breakout
    assert r["class"] == "WINNER" and r["breakout"]
    r = SC.score_post([snap(90000, h=6)], base, cfg2)                                 # one component, no breakout
    assert r["class"] != "WINNER"


def test_loser_needs_24h(cfg):
    base = B.by_key([B.compute("pg1", "instagram", h, history(30, seed=h), None, cfg) for h in G.HORIZONS])
    assert SC.score_post([snap(60, h=6)], base, cfg)["class"] == "NORMAL"
    assert SC.score_post([snap(60, h=24)], base, cfg)["class"] == "LOSER"


def test_breakout_views_is_a_winner_at_three_hours_whatever_the_rates(cfg):
    r = SC.score_post([snap(600000, h=3)], {}, cfg)
    assert r["class"] == "WINNER" and r["breakout"]
    assert SC.score_post([snap(600000, h=1)], {}, cfg)["class"] != "WINNER"


def test_latest_horizon_decides_and_history_is_kept(cfg):
    r = SC.score_post([snap(1000, h=1), snap(40000, shares=500, saves=700, kw=100, h=24), snap(3000, h=6)], {}, cfg)
    assert r["horizon_h"] == 24 and [h["horizon_h"] for h in r["history"]] == [1, 6, 24]


def test_conversions_lift_reward_and_score(cfg):
    plain = SC.score_post([snap(20000, shares=80, saves=120, kw=40, h=24)], {}, cfg)
    zero = SC.score_post([snap(20000, shares=80, saves=120, kw=40, optins=0, members=0, h=24)], {}, cfg)
    conv = SC.score_post([snap(20000, shares=80, saves=120, kw=40, optins=60, members=5, h=24)], {}, cfg)
    buyers = SC.score_post([snap(20000, shares=80, saves=120, kw=40, optins=0, members=0, h=24) | {"buyers": 12}], {}, cfg)
    assert conv["reward"] > plain["reward"] >= zero["reward"] and conv["score"] > plain["score"] > zero["score"]
    assert buyers["reward"] > zero["reward"] and buyers["score"] > zero["score"]
    assert conv["conversion_norm"] is not None and plain["conversion_norm"] is None and zero["conversion_norm"] == 0.0
    assert conv["reward"] >= plain["reward"]                                   # measured conversions never rank below unknown


def test_z_scores_are_clipped(cfg):
    r = SC.score_post([snap(10**12, h=24)], {}, cfg)
    assert abs(r["z"]["views"]) <= cfg["scoring"]["z_clip"]


def test_score_many_groups_by_post_and_sorts(cfg):
    snaps = [snap(50000, shares=500, saves=800, kw=100, h=24, post="a"), snap(100, h=24, post="b"), snap(100, h=1, post="b")]
    out = SC.score_many(snaps, [], cfg)
    assert [r["post_id"] for r in out] == ["a", "b"] and out[1]["horizon_h"] == 24


def test_unknown_horizons_and_empty_input(cfg):
    assert SC.score_post([], {}, cfg) is None
    assert SC.score_post([snap(100, h=5)], {}, cfg) is None
    assert SC.score_many([], [], cfg) == []


def test_reward_is_bounded_for_any_input(cfg):
    for s in (None, -50, 50, 0.0, float("nan")):
        for c in (None, 0.0, 1.0, 5.0):
            v = SC.reward(None if s is None or (isinstance(s, float) and math.isnan(s)) else s, c, cfg)
            assert 0.0 <= v <= 1.0


def test_config_validation_guards_class_order():
    with pytest.raises(ValueError):
        G.load({"scoring": {"classes": {"PROMISING": {"min_score": 2.0}}}})
    with pytest.raises(ValueError):
        G.load({"allocator": {"explore_floor": 0.1}})
    with pytest.raises(ValueError):
        G.load({"governor": {"max_boost_daily_usd": float("nan")}})


# ---------- VIRALITY_SYSTEM.md §4: shares+saves per view is the primary reward; 1 h / 3 h retention proxy ----------
def test_share_save_rate_drives_reward(cfg):
    hi = SC.score_post([snap(5000, shares=150, saves=200, kw=0, h=24)], {}, cfg)
    lo = SC.score_post([snap(5000, shares=2, saves=3, kw=60, h=24)], {}, cfg)     # keyword bait, no shares/saves
    assert hi["share_save_z"] > 0 > lo["share_save_z"]
    assert hi["reward"] > lo["reward"] + 0.2
    w = cfg["scoring"]["weights"]
    assert w["share_save_rate"] == max(w.values())


def test_retention_proxy_uses_1h_and_3h_only(cfg):
    s1 = {**snap(400, shares=4, saves=4, kw=0, h=1), "avg_watch_s": 18, "duration_s": 40}
    s3 = {**snap(1200, shares=12, saves=12, kw=0, h=3), "avg_watch_pct": 55}
    s24 = {**snap(3000, shares=30, saves=30, kw=0, h=24), "avg_watch_pct": 0.9}
    r = SC.score_post([s1, s3, s24], {}, cfg)
    assert r["retention_proxy"] == round((0.45 + 0.55) / 2, 4)
    assert "retention" in r["history"][0]["components_used"] and "retention" not in r["components_used"]
