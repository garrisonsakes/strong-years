"""Raw captures -> PostMetrics snapshots at 1/3/6/24/72 h (growth/snapshots). Adversarial: clock skew, future
captures, duplicates, restated (shrinking) counters, missing horizons, interpolation limits, NaN, rollup series."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from growth import config as G, snapshots as S

PUB = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
POST = {"post_id": "p1", "page_id": "pg1", "platform": "instagram", "published_at": PUB.isoformat()}


def cap(h: float, **k) -> dict:
    d = {"captured_at": (PUB + timedelta(hours=h)).isoformat(), "views": int(1000 * h), "shares": int(10 * h), "source": "t"}
    d.update(k)
    return d


@pytest.fixture
def cfg():
    return G.load()


def test_exact_horizons_and_shape(cfg):
    res = S.build(POST, [cap(h) for h in G.HORIZONS], {"keyword_comments": 5, "optins": 2, "members": 0}, cfg,
                  now=PUB + timedelta(hours=80))
    assert res["horizons_available"] == list(G.HORIZONS) and res["horizons_missing"] == [] and res["dropped"] == []
    s = res["snapshots"][3]
    assert s["horizon_h"] == 24 and s["views"] == 24000 and s["age_h"] == 24.0 and not s["interpolated"]
    for k in G.SNAPSHOT_FIELDS:
        assert k in s
    assert s["keyword_comments"] == 5 and s["optins"] == 2 and s["members"] == 0
    assert s["rollups_as_of_now"] == ["keyword_comments", "optins", "members"]   # scalars are flagged as-of-now
    assert "likes" in s["missing"] and s["likes"] is None


def test_missing_horizons_are_reported_not_invented(cfg):
    res = S.build(POST, [cap(1), cap(24)], None, cfg, now=PUB + timedelta(hours=30))
    assert res["horizons_available"] == [1, 24]
    assert res["horizons_missing"] == [3, 6]                 # 72 h hasn't happened yet, so it isn't "missing"
    for s in res["snapshots"]:
        assert s["keyword_comments"] is None and "keyword_comments" in s["missing"]


def test_too_young_post_has_no_horizons(cfg):
    res = S.build(POST, [cap(0.2)], None, cfg, now=PUB + timedelta(minutes=15))
    assert res["snapshots"] == [] and res["horizons_missing"] == []


def test_zero_captures(cfg):
    res = S.build(POST, [], None, cfg, now=PUB + timedelta(hours=100))
    assert res["snapshots"] == [] and res["horizons_missing"] == list(G.HORIZONS)


def test_clock_skew_before_publish_is_clamped_within_tolerance_and_dropped_beyond(cfg):
    early_ok = cap(-0.1, views=0)                          # 6 min "before" publish: clock skew -> age 0
    early_bad = cap(-1.0, views=0)                         # an hour before publish: not this post's capture
    kept, dropped = S.normalize_captures([early_ok, early_bad, cap(1)], PUB, PUB + timedelta(hours=2), cfg)
    assert [r["age_h"] for r in kept] == [0.0, 1.0]
    assert len(dropped) == 1 and "before publish" in dropped[0]["reason"]


def test_future_captures_and_ancient_captures_are_dropped(cfg):
    now = PUB + timedelta(hours=2)
    kept, dropped = S.normalize_captures([cap(1), cap(3)], PUB, now, cfg)
    assert [r["age_h"] for r in kept] == [1.0] and dropped[0]["reason"] == "captured in the future"
    kept, dropped = S.normalize_captures([cap(1), cap(24 * 40)], PUB, PUB + timedelta(days=41), cfg)
    assert [r["age_h"] for r in kept] == [1.0] and dropped[0]["reason"] == "older than max_age_h"


def test_duplicate_captures_merge_keeping_the_larger_counters(cfg):
    a = cap(1, views=1000, shares=10)
    b = {**cap(1, views=990, shares=12), "captured_at": (PUB + timedelta(hours=1, seconds=20)).isoformat()}
    kept, dropped = S.normalize_captures([b, a], PUB, PUB + timedelta(hours=2), cfg)
    assert len(kept) == 1 and len(dropped) == 1 and "duplicate" in dropped[0]["reason"]
    assert kept[0]["views"] == 1000 and kept[0]["shares"] == 12


def test_counters_never_go_backwards_on_platform_restatement(cfg):
    kept, _ = S.normalize_captures([cap(1, views=5000), cap(3, views=4200), cap(6, views=6000)], PUB, PUB + timedelta(hours=7), cfg)
    assert [r["views"] for r in kept] == [5000, 5000, 6000]


def test_unordered_input_is_sorted(cfg):
    kept, _ = S.normalize_captures([cap(6), cap(1), cap(3)], PUB, PUB + timedelta(hours=7), cfg)
    assert [r["age_h"] for r in kept] == [1.0, 3.0, 6.0]


def test_nearest_capture_wins_inside_a_window(cfg):
    res = S.build(POST, [cap(20), cap(25), cap(33)], None, cfg, now=PUB + timedelta(hours=40))
    s = next(x for x in res["snapshots"] if x["horizon_h"] == 24)
    assert s["age_h"] == 25.0 and s["views"] == 25000


def test_interpolation_between_bracketing_captures_is_flagged_and_bounded(cfg):
    # 3 h window is [2.25, 4.5]; captures at 2 h and 5 h bracket it within the x3 ratio -> interpolated, log-time
    res = S.build(POST, [cap(2, views=2000), cap(5, views=5000)], None, cfg, now=PUB + timedelta(hours=6))
    s = next(x for x in res["snapshots"] if x["horizon_h"] == 3)
    assert s["interpolated"] and 2000 < s["views"] < 5000 and s["age_h"] == 3.0
    # captures too far apart (1 h and 20 h for the 3 h horizon: 20 > 3*3) -> no interpolation
    res = S.build(POST, [cap(1), cap(20)], None, cfg, now=PUB + timedelta(hours=21))
    assert 3 not in res["horizons_available"] and 6 not in res["horizons_available"]
    # interpolation can be switched off
    res = S.build(POST, [cap(2, views=2000), cap(5, views=5000)], None, G.load({"snapshots": {"interpolate": False}}),
                  now=PUB + timedelta(hours=6))
    assert 3 not in res["horizons_available"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -5, "x", 1e15, True])
def test_garbage_counter_values_become_missing(cfg, bad):
    res = S.build(POST, [cap(1, views=bad, shares=3)], None, cfg, now=PUB + timedelta(hours=2))
    s = res["snapshots"][0]
    assert s["views"] is None and "views" in s["missing"] and s["shares"] == 3


def test_unparsable_timestamps_are_dropped_not_fatal(cfg):
    res = S.build(POST, [{"captured_at": "yesterday-ish", "views": 1}, {"views": 2}, cap(1)], None, cfg, now=PUB + timedelta(hours=2))
    assert len(res["dropped"]) == 2 and res["horizons_available"] == [1]


def test_rollup_time_series_attach_as_of_each_capture(cfg):
    roll = {"optins": [{"at": (PUB + timedelta(hours=2)).isoformat(), "count": 3}, {"at": (PUB + timedelta(hours=20)).isoformat(), "count": 9}],
            "members": 4, "buyers": [{"at": (PUB + timedelta(hours=5)).isoformat(), "count": 2}]}
    res = S.build(POST, [cap(1), cap(6), cap(24)], roll, cfg, now=PUB + timedelta(hours=30))
    by = {s["horizon_h"]: s for s in res["snapshots"]}
    assert by[1]["optins"] == 0 and by[6]["optins"] == 3 and by[24]["optins"] == 9
    assert by[1]["members"] == 4 and by[1]["rollups_as_of_now"] == ["members"]
    assert by[1]["buyers"] == 0 and by[6]["buyers"] == 2 and by[24]["buyers"] == 2


def test_invalid_post_rejected(cfg):
    with pytest.raises(ValueError):
        S.build({"post_id": "p", "platform": "instagram"}, [], None, cfg)
    with pytest.raises(ValueError):
        S.build({"post_id": "p", "platform": "myspace", "published_at": PUB.isoformat()}, [], None, cfg)


def test_parse_dt_accepts_iso_z_naive_and_unix_and_rejects_junk():
    assert S.parse_dt("2026-10-01T12:00:00Z") == PUB
    assert S.parse_dt("2026-10-01T12:00:00") == PUB
    assert S.parse_dt(PUB.timestamp()) == PUB
    assert S.parse_dt("not a date") is None and S.parse_dt(None) is None and S.parse_dt(float("nan")) is None
    assert S.parse_dt(True) is None
