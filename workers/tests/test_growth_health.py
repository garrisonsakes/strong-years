"""growth/health.py: POSTDB Rule 0 (distribution state per account) and relative breakouts (rule 11)."""
from datetime import datetime, timedelta, timezone

from growth import config as G, health, scoring

NOW = datetime(2026, 11, 1, 12, tzinfo=timezone.utc)


def _posts(acct, plat, days, views, likes_rate=0.05, every_h=12):
    out, t = [], NOW - timedelta(days=days[0])
    while t < NOW - timedelta(days=days[1]):
        out.append({"account": acct, "platform": plat, "published_at": t.isoformat(), "views": views, "likes": views * likes_rate})
        t += timedelta(hours=every_h)
    return out


def test_collapse_with_steady_likes_is_suppressed_distribution():
    posts = _posts("@changyin", "tiktok", (28, 7), 60000) + _posts("@changyin", "tiktok", (7, 0), 1800)
    r = health.check(posts, G.load(), NOW)[0]
    assert r["state"] == "SUPPRESSED" and r["ratio"] < 0.3
    assert any("distribution, not creative" in x for x in r["reasons"]) and r["actions"]


def test_healthy_dip_watch_new_and_dormant():
    cfg = G.load()
    ok = health.check(_posts("a", "instagram", (28, 0), 10000), cfg, NOW)[0]
    assert ok["state"] == "HEALTHY"
    watch = health.check(_posts("a", "instagram", (28, 7), 10000) + _posts("a", "instagram", (7, 0), 5000), cfg, NOW)[0]
    assert watch["state"] == "WATCH"
    assert health.check(_posts("a", "x", (3, 0), 100), cfg, NOW)[0]["state"] == "NEW"
    dormant = health.check(_posts("a", "instagram", (28, 3), 10000), cfg, NOW)[0]
    assert dormant["state"] == "DORMANCY_RISK" and dormant["gap_h"] >= 36


def test_sibling_gap_flags_one_account():
    posts = _posts("@sunyoon", "tiktok", (7, 0), 400) + _posts("@changyin", "tiktok", (7, 0), 9000) + \
        _posts("@changyin.strength", "tiktok", (7, 0), 8000)
    rows = {r["account"]: r for r in health.check(posts, G.load(), NOW)}
    assert rows["@sunyoon"]["state"] == "SUPPRESSED" and rows["@changyin"]["state"] != "SUPPRESSED"


def test_relative_breakout_is_a_winner_on_small_pages():
    cfg = G.load()
    cls, why = scoring.classify(0.2, 6, 6000, 3, cfg, page_median_views=1000)
    assert cls == "WINNER" and "6.0x the page median" in why[0]
    assert scoring.classify(0.2, 6, 4000, 3, cfg, page_median_views=1000)[0] != "WINNER"
    assert scoring.classify(0.2, 3, 6000, 3, cfg, page_median_views=1000)[0] != "WINNER"   # too young
