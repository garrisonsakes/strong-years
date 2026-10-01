"""Metrics adapters (growth/adapters, growth/net): fixture-driven parsing for every platform, counters the platform
does not expose are never faked as 0, and the live path is SSRF-safe and OFF by default (no network in tests)."""
from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from growth import adapters, config as G, net

FIX = json.loads((Path(__file__).parent / "fixtures" / "growth_metrics.json").read_text())


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setattr(G, "GROWTH_LIVE_METRICS", False)
    monkeypatch.setattr(net, "resolve", lambda host, port: (_ for _ in ()).throw(AssertionError("DNS must not be called")))


# ---------------------------------------------------------------- parsers (pure, fixture-driven)
@pytest.mark.parametrize("platform", list(G.PLATFORMS))
def test_every_platform_parses_to_the_one_capture_shape(platform):
    fx = FIX[platform]
    cap = adapters.parse(platform, fx["raw"], duration_s=fx.get("duration_s"), captured_at="2026-10-01T13:00:00Z")
    assert cap["captured_at"] == "2026-10-01T13:00:00Z" and cap["source"]
    for k, v in fx["expect"].items():
        assert cap.get(k) == v, (platform, k, cap.get(k), v)
    # counters the platform doesn't expose are absent AND listed, never 0
    for k in fx["expect_missing"]:
        assert k in cap["missing"] and cap.get(k) is None, (platform, k)
    assert set(cap) - {"captured_at", "source", "missing", "avg_watch_pct"} <= set(adapters.PLATFORM_COUNTERS)


def test_instagram_watch_pct_from_ms_and_duration():
    raw = {"data": [{"name": "views", "values": [{"value": 1000}]}, {"name": "ig_reels_avg_watch_time", "values": [{"value": 12000}]}]}
    assert adapters.parse("instagram", raw, duration_s=30)["avg_watch_pct"] == 40.0
    assert adapters.parse("instagram", raw)["avg_watch_pct"] is None                     # no duration -> unknown, not 0
    assert adapters.parse("instagram", raw, duration_s=5)["avg_watch_pct"] == 100.0      # capped


def test_graph_insights_total_value_and_breakdown_shapes():
    raw = {"data": [{"name": "views", "total_value": {"value": 42}},
                    {"name": "shares", "values": [{"value": {"story": 3, "dm": 4}}]}]}
    cap = adapters.parse("instagram", raw)
    assert cap["views"] == 42 and cap["shares"] == 7


def test_youtube_dimensioned_report_sums_counts_and_averages_ratios():
    raw = {"columnHeaders": [{"name": "day"}, {"name": "views"}, {"name": "averageViewPercentage"}],
           "rows": [["2026-10-01", 100, 40.0], ["2026-10-02", 50, 60.0]]}
    cap = adapters.parse("youtube", raw)
    assert cap["views"] == 150 and cap["avg_watch_pct"] == 50.0


def test_youtube_data_api_fallback_shape():
    cap = adapters.parse("youtube", {"statistics": {"viewCount": "123", "likeCount": "4", "commentCount": "1"}})
    assert cap["views"] == 123 and cap["likes"] == 4 and "shares" in cap["missing"]


def test_tiktok_picks_the_requested_video_from_a_list():
    raw = {"data": {"videos": [{"id": "a", "view_count": 1}, {"id": "b", "view_count": 99, "share_count": 3, "duration": 30,
                                 "average_time_watched": 9}]}}
    cap = adapters.tt_parse(raw, video_id="b")
    assert cap["views"] == 99 and cap["shares"] == 3 and cap["avg_watch_pct"] == 30.0


def test_x_shares_is_retweets_plus_quotes_and_saves_are_bookmarks():
    raw = {"data": {"id": "1", "public_metrics": {"impression_count": 500, "retweet_count": 2, "quote_count": 3,
                                                  "bookmark_count": 7, "like_count": 10, "reply_count": 1},
                    "non_public_metrics": {"user_profile_clicks": 4, "url_link_clicks": 2}}}
    cap = adapters.parse("x", raw)
    assert cap["views"] == 500 and cap["shares"] == 5 and cap["saves"] == 7
    assert cap["profile_visits"] == 4 and cap["link_clicks"] == 2 and "reach" in cap["missing"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1, "abc", None, True, 1e14])
def test_garbage_counter_values_become_missing_not_zero(bad):
    raw = {"data": [{"name": "views", "values": [{"value": bad}]}]}
    cap = adapters.parse("instagram", raw)
    assert cap.get("views") is None and "views" in cap["missing"]


def test_unknown_platform_and_non_object_payload_rejected():
    with pytest.raises(ValueError):
        adapters.parse("snapchat", {})
    with pytest.raises(ValueError):
        adapters.parse("instagram", [1, 2])


def test_adapter_registry_is_complete_and_extensible():
    assert set(adapters.PARSERS) == set(adapters.FETCHERS) == set(G.PLATFORMS)
    # the contract a future X/Grok adapter must satisfy: parse(raw, *, duration_s, captured_at) and fetch(post, token, client)
    for p in G.PLATFORMS:
        assert callable(adapters.PARSERS[p]) and callable(adapters.FETCHERS[p])


def test_register_adds_an_adapter_behind_the_same_switches(monkeypatch):
    def parse_fn(raw, *, duration_s=None, captured_at=None):
        return adapters._capture({"views": raw.get("n")}, captured_at=captured_at, missing=["reach"], source="grok_test")

    def fetch_fn(post, token, client=None, **kw):
        return parse_fn(net.request_json("GET", "https://api.x.com/2/grok/1", token=token, client=client))
    monkeypatch.setitem(adapters.PARSERS, "x", adapters.PARSERS["x"])
    monkeypatch.setitem(adapters.FETCHERS, "x", adapters.FETCHERS["x"])
    adapters.register("x", parse_fn, fetch_fn)
    assert adapters.parse("x", {"n": 7})["views"] == 7
    with pytest.raises(net.NetPolicyError):
        adapters.fetch("x", {"external_post_id": "1"}, "t")              # still off unless GROWTH_LIVE_METRICS=1
    with pytest.raises(TypeError):
        adapters.register("x", None, fetch_fn)


# ---------------------------------------------------------------- live path: off by default, SSRF-safe
def test_fetch_refused_when_live_metrics_disabled():
    with pytest.raises(net.NetPolicyError):
        adapters.fetch("instagram", {"external_post_id": "123"}, "tok")
    with pytest.raises(net.NetPolicyError):
        net.request_json("GET", "https://graph.facebook.com/v22.0/1/insights")


@pytest.mark.parametrize("url", ["http://graph.facebook.com/x", "https://evil.example.com/x", "https://graph.facebook.com.evil.com/x",
                                 "https://user:pw@graph.facebook.com/x", "https://localhost/x", "https://127.0.0.1/x",
                                 "ftp://graph.facebook.com/x"])
def test_check_url_rejects_non_https_and_unlisted_hosts(url, monkeypatch):
    monkeypatch.setattr(net, "resolve", lambda host, port: ["157.240.1.1"])
    with pytest.raises(net.NetPolicyError):
        net.check_url(url)


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.5", "192.168.1.2", "169.254.169.254", "::1", "fc00::1", "0.0.0.0"])
def test_check_url_rejects_hosts_resolving_to_private_addresses(ip, monkeypatch):
    monkeypatch.setattr(net, "resolve", lambda host, port: [ip])
    with pytest.raises(net.NetPolicyError):
        net.check_url("https://graph.facebook.com/v22.0/1/insights")


def test_check_url_accepts_allow_listed_public_host(monkeypatch):
    monkeypatch.setattr(net, "resolve", lambda host, port: ["157.240.1.1", "2a03:2880:f10c:83:face:b00c:0:25de"])
    net.check_url("https://graph.facebook.com/v22.0/1/insights")


@pytest.mark.parametrize("bad_id", ["", "a/b", "../x", "1 2", "x" * 65, "{id}", "a?b=c"])
def test_platform_ids_are_validated_before_entering_urls(bad_id):
    with pytest.raises(net.NetPolicyError):
        net.safe_id(bad_id)


def test_live_request_refuses_redirects_and_caps_bytes(monkeypatch):
    """With the switch forced on and DNS stubbed, a mock transport proves redirects are refused and the byte cap
    holds. No real socket is opened (httpx MockTransport)."""
    monkeypatch.setattr(G, "GROWTH_LIVE_METRICS", True)
    monkeypatch.setattr(net, "resolve", lambda host, port: ["157.240.1.1"])
    monkeypatch.setattr(net, "MAX_BYTES", 100)
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["auth"] = req.headers.get("authorization")
        seen["url"] = str(req.url)
        if req.url.path.endswith("/redirect"):
            return httpx.Response(302, headers={"location": "https://evil.example.com/"})
        if req.url.path.endswith("/big"):
            return httpx.Response(200, content=b"{" + b" " * 500 + b"}")
        if req.url.path.endswith("/notjson"):
            return httpx.Response(200, content=b"<html>")
        return httpx.Response(200, json={"data": []})
    client = httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False)
    assert net.request_json("GET", "https://graph.facebook.com/v22.0/1/insights", token="T", client=client) == {"data": []}
    assert seen["auth"] == "Bearer T" and "T" not in seen["url"]          # token in the header, never in the URL
    for path in ("redirect", "big", "notjson"):
        with pytest.raises(net.NetPolicyError):
            net.request_json("GET", f"https://graph.facebook.com/v22.0/1/{path}", token="T", client=client)


def test_fetch_builds_the_documented_urls_without_network(monkeypatch):
    monkeypatch.setattr(G, "GROWTH_LIVE_METRICS", True)
    monkeypatch.setattr(net, "resolve", lambda host, port: ["157.240.1.1"])
    calls = []

    def fake(method, url, **kw):
        calls.append((method, url, kw.get("params"), kw.get("body")))
        return FIX["instagram"]["raw"] if "facebook" in url else {"data": []}
    monkeypatch.setattr(net, "request_json", fake)
    post = {"external_post_id": "17895695668004550", "duration_s": 30, "published_at": "2026-10-01"}
    adapters.fetch("instagram", post, "T")
    adapters.fetch("tiktok", post, "T")
    adapters.fetch("youtube", post, "T", start="2026-10-01", end="2026-10-02")
    adapters.fetch("threads", post, "T")
    adapters.fetch("x", post, "T")
    hosts = [httpx.URL(c[1]).host for c in calls]
    assert all(h in G.METRICS_ALLOWED_HOSTS for h in hosts)
    assert calls[1][3] == {"filters": {"video_ids": ["17895695668004550"]}}
    assert "video==17895695668004550" in calls[2][2]["filters"]
