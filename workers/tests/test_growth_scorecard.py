"""Scorecard, scorecard actions, block-level learning, early-signal stub, adapters' scorecard inputs, accessibility."""
from datetime import datetime, timezone

import pytest

from assemble import accessibility as ACC
from assemble import captions as C
from assemble import overlay, voice
from growth import actions as A
from growth import adapters as AD
from growth import allocator as AL
from growth import config as G
from growth import learning as L
from growth import predict as P
from growth import scorecard as SC

NOW = datetime(2026, 10, 20, 12, tzinfo=timezone.utc)
PAGES = [{"id": f"pg{i}", "slug": s, "status": "active", "locale": "en-US"} for i, s in
         enumerate(["@changyin", "@sunyoon.kitchen", "@sunyoon", "@changyin.strength"])]


def _read(**kw):
    r = {"post_id": "p1", "page_id": "pg0", "platform": "facebook", "horizon_h": 24, "reach": 5000, "views": 6000,
         "shares": 20, "saves": 30, "comments": 30, "keyword_comments": 20, "hold_3s": 0.6, "avg_watch_pct": 45,
         "optins": 3, "hook_block_id": "H1", "body_block_id": "B1", "close_block_id": "C1", "hook_family": "IF_EVERY",
         "body_family": "P01:F02", "close_family": "STRONG"}
    r.update(kw)
    return r


def test_scores_are_0_100_vs_baseline_with_shrinkage_and_flags():
    cfg = G.load()
    hist = [SC.raw_components(_read())[0] for _ in range(20)]
    typical = SC.score_read(_read(), hist, cfg)
    assert all(40 <= v <= 60 for v in typical["scores"].values())            # the page's typical post ~ 50
    big = SC.score_read(_read(shares=200), hist, cfg)["scores"]["shares"]
    small = SC.score_read(_read(shares=4, reach=50, views=60), hist, cfg)["scores"]["shares"]   # 8% on 50 reach
    assert big > 90 and 50 < small < big                                      # tiny samples are shrunk hard
    ig = SC.score_read(_read(platform="instagram", horizon_h=12, hold_3s=None, skip_rate=0.2), [], cfg)
    assert ig["provisional"] and ig["raw"]["hook"] == pytest.approx(0.8)
    assert not SC.score_read(_read(platform="instagram", horizon_h=24), [], cfg)["provisional"]
    yt = SC.score_read(_read(platform="youtube", reach=None, engaged_views=1000), [], cfg)
    assert yt["denominator"] == "engaged_views"
    w = cfg["scorecard"]["weights"]
    assert max(w, key=w.get) == "conversion" and sum(w.values()) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        G.load({"scorecard": {"weights": {**w, "conversion": 0.05, "shares": 0.31}}})
    row = SC.db_row(typical)
    assert row["hook_block_id"] == "H1" and set(row) >= {"conversion_score", "composite", "provisional"}


def _card(pid, page="pg0", h=24, comp=50.0, **scores):
    return {"post_id": pid, "page_id": page, "platform": "facebook", "horizon_h": h, "provisional": False,
            "scores": scores, "composite": comp, "hook_block_id": f"H-{pid}", "body_block_id": f"B-{pid}",
            "close_block_id": f"C-{pid}", "hook_family": "MYTH", "body_family": "P03:F02", "close_family": "BALANCE"}


def test_scorecard_actions():
    cards = [_card("a", hook=90), _card("b", body=88, hook=40), _card("c", shares=95), _card("d", non_follower=85),
             {**_card("e", hook=99), "provisional": True, "platform": "instagram", "horizon_h": 12}]
    posts = [{"post_id": "c", "pillar": "P03", "class": "PROMISING", "page_slug": "@changyin"}, {"post_id": "d", "pillar": "P09"}]
    out = A.scorecard_plan(cards, posts, PAGES, now=NOW)
    assert len(out["new_bodies"]) == 2 and out["new_bodies"][0]["keep_hook_block_id"] == "H-a"
    assert len(out["new_hooks"]) == 3 and {j["variant_role"] for j in out["new_hooks"]} == {"TEST"}
    assert {j["target_page_id"] for j in out["remix_jobs"]} == {"pg1", "pg2", "pg3"}           # every other page
    assert out["boost_candidates"][0]["status"] == "watch_until_winner"                         # governor: WINNERs only
    assert out["topic_boosts"][0]["pillar"] == "P09" and out["topic_boosts"][0]["multiplier"] == 2.0
    assert out["skipped_provisional"] == ["e"]
    # a gene under 30 twice in a row is benched for 14 days, and the allocator skips it
    o1 = A.scorecard_plan([_card("x", comp=20)], [], PAGES, now=NOW)
    assert not o1["bench"]
    o2 = A.scorecard_plan([_card("y", comp=25)], [], PAGES, now=NOW, gene_history=o1["gene_history"])
    assert {b["gene"] for b in o2["bench"]} == {"hook:MYTH", "body:P03:F02", "close:BALANCE"}
    page = {"id": "pg0", "slug": "@changyin"}
    plan = AL.plan_day(page, "facebook", "2026-10-21", [], now=NOW, benched=o2["benched"], seed=1)
    assert plan["arms_benched"] > 0
    assert all(s["hook_family"] != "MYTH" and s["body_family"] != "P03:F02" for s in plan["slots"])


def test_block_attribution_readout_and_predictor_stub():
    cards = [_card("a", comp=80, hook=90), _card("b", comp=70, hook=70), _card("a", h=6, comp=10)]
    att = L.attribute(cards)
    assert att["H-a"]["mean_component"] == 90 and att["H-a"]["mean_composite"] == 80    # 24 h read wins
    txt = L.weekly_readout(cards, {"hook:STORY": "2026-11-03T00:00:00+00:00"},
                           {"status": "ok", "changes": [{"component": "share", "old": 8, "new": 9.5}], "applied": False},
                           ["3 new hooks"], week_of="2026-10-19")
    for s in ("top 5 genes", "Benched", "share: 8 -> 9.5 points (proposed", "Next week's tests", "hook:MYTH"):
        assert s in txt
    assert L.post_readout(txt, "2026-10-19")["status"] == "skipped"                  # APP_URL unset in tests
    few = [dict(_card(f"p{i}", h=h, comp=50 + i % 7, hook=40 + i % 30)) for i in range(150) for h in (1, 24)]
    pr = P.EarlySignalPredictor()
    assert pr.train(few)["trained"] is False and pr.predict(few[0]) is None
    many = [dict(_card(f"p{i}", h=h, comp=30 + (i % 40), hook=30 + (i % 40))) for i in range(210) for h in (1, 24)]
    r = pr.train(many)
    assert r["trained"] and r["n"] == 210 and 0 <= pr.predict(many[0]) <= 100


def test_adapters_feed_scorecard_inputs():
    raw = {"data": [{"name": "fb_reels_total_plays", "values": [{"value": 5000}]},
                    {"name": "blue_reels_play_count", "values": [{"value": 4100}]},
                    {"name": "post_video_retention_graph", "values": [{"value": {"0": 1.0, "2": 0.8, "4": 0.6, "40": 0.3}}]}]}
    cap = AD.parse("facebook", raw, duration_s=42)
    assert cap["scorecard"]["hold_3s"] == pytest.approx(0.7) and cap["scorecard"]["first_plays"] == 4100
    read = SC.read_from_capture(cap, {"post_id": "p", "platform": "facebook", "duration_s": 42, "close_start_s": 38}, 24)
    assert SC.raw_components(read)[0]["hook"] == pytest.approx(0.7)
    ig = AD.parse("instagram", {"data": [{"name": "reels_skip_rate", "values": [{"value": 35}]}]})
    assert ig["scorecard"]["skip_rate"] == pytest.approx(0.35) and "reels_skip_rate" in AD.IG_METRICS
    yt = AD.parse("youtube", {"columnHeaders": [{"name": "views"}, {"name": "engagedViews"}], "rows": [[900, 600]]})
    assert yt["scorecard"]["engaged_views"] == 600


def _w(text, start, end):
    return C.Word(text, start, end)


def test_accessibility_defaults():
    slow = [_w("Stand", 0.0, 0.4), _w("up.", 0.4, 0.8), _w("Sit", 1.2, 1.6), _w("down.", 1.6, 2.0)]
    fast = [_w(f"w{i}", i * 0.2, i * 0.2 + 0.18) for i in range(20)]
    assert ACC.check({}, slow)["errors"] == [] and ACC.speech_rate(slow) == pytest.approx(2.5, abs=0.01)
    assert any("speech rate" in e for e in ACC.check({}, fast)["errors"])
    assert any("music under speech" in e for e in ACC.check({"music": {"under_speech": True}}, slow)["errors"])
    assert ACC.check({}, [_w("One.", 0, 0.3), _w("Two", 0.35, 0.6)])["warnings"]       # 50 ms after a sentence
    assert ACC.speech_spans(slow, 10) == [(0.0, 2.15)]
    assert overlay.cap_height(overlay.hook_min_size()) >= 72
    assert overlay.CaptionStyle.from_manifest({"size_px": 50}).size_px == 56
    body = voice.tts_request("Stand up. Sit down.", voice_settings={"speed": 1.2})
    assert body["voice_settings"]["speed"] == 0.95 and "[short pause]" in body["text"]
    assert '<break time="0.3s" />' in voice.tts_request("A. B.", model_id="eleven_multilingual_v2")["text"]
    al = {"characters": list("Hi <b/> you"), "character_start_times_seconds": [i * 0.1 for i in range(11)],
          "character_end_times_seconds": [i * 0.1 + 0.1 for i in range(11)]}
    assert [w["word"] for w in voice.words_from_alignment(al, "", 1.1)] == ["Hi", "you"]
