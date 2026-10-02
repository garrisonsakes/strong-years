"""MRR-weighted iteration: scorecard.value_score blends virality with attributed MRR per 1K views + buyers (default
50/50, print mode 30/70); actions.mrr_plan turns high-MRR posts into the GO-HARD bundle (5-hook remakes on every other
page, FB long cut, 5 Trial Reels, email feature draft, DM pinned link, boost HELD until the spend gate) and
high-virality / low-MRR posts into a reach remix + CTA-swap experiment; weekly_readout ranks by MRR, views and both.
Nothing here publishes, sends or spends."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from growth import actions as A, config as G, scorecard as SC

NOW = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
PAGES = [
    {"id": "A", "slug": "changyin", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P01", "P02"], "speakers": ["CHANG", "DUO"]}},
    {"id": "B", "slug": "sunyoon-kitchen", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P11"], "speakers": ["SUN", "DUO"]}},
    {"id": "C", "slug": "changandsun", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P01"], "speakers": ["DUO", "CHANG", "SUN"]}},
    {"id": "D", "slug": "changyin-strength", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P01"], "speakers": ["CHANG"]}},
]
CARD = {"post_id": "p1", "page_id": "A", "platform": "instagram",
        "scores": {"hook": 70, "body": 60, "shares": 75, "saves": 65, "conversion": 99}}


def post(pid="p1", **k):
    d = {"post_id": pid, "published_at": "2026-10-01T15:00:00+00:00", "cta_keyword": "STRONG",
         "arm": {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02", "speaker": "CHANG", "length": "M"}}
    d.update(k)
    return d


def test_virality_excludes_conversion():
    w = G.load()["scorecard"]["weights"]
    v = SC.virality_score(CARD)
    exp = sum(w[c] * s for c, s in CARD["scores"].items() if c != "conversion") / sum(w[c] for c in CARD["scores"] if c != "conversion")
    assert v == round(exp, 2)


def test_weights_default_50_50_and_print_30_70():
    att = {"views": 200000, "mrr_usd": 5000, "buyers": 60}
    d = SC.value_score(CARD, att)
    p = SC.value_score(CARD, att, mode="print")
    assert d["weights"] == {"virality": 0.5, "money": 0.5} and p["weights"] == {"virality": 0.3, "money": 0.7}
    assert d["value"] == pytest.approx(0.5 * d["virality"] + 0.5 * d["money"], abs=0.01)
    assert p["value"] == pytest.approx(0.3 * p["virality"] + 0.7 * p["money"], abs=0.01)
    assert d["money"] > d["virality"] and p["value"] > d["value"]          # money-heavy post gains in print mode
    assert d["mrr_per_1k"] == 25.0 and d["buyers_per_1k"] == 0.3
    with pytest.raises(ValueError):
        SC.value_score(CARD, att, mode="yolo")


def test_money_rises_with_mrr_per_1k_and_small_posts_shrink():
    lo = SC.value_score(CARD, {"views": 100000, "mrr_usd": 10, "buyers": 0})
    hi = SC.value_score(CARD, {"views": 100000, "mrr_usd": 3000, "buyers": 30})
    assert hi["money"] > 80 > 30 > lo["money"]
    tiny = SC.value_score(CARD, {"views": 40, "mrr_usd": 25, "buyers": 1})          # 625 $/1K on 40 views
    assert tiny["money"] < hi["money"]
    hist = [{"mrr_per_1k": 30.0, "buyers_per_1k": 0.4}] * 30                       # a page that already prints money
    assert SC.value_score(CARD, {"views": 100000, "mrr_usd": 3000, "buyers": 30}, hist)["money"] < hi["money"]


def test_go_hard_bundle_never_spends():
    v = SC.value_score(CARD, {"views": 150000, "mrr_usd": 4000, "buyers": 50})
    plan = A.mrr_plan([v], [post()], PAGES, now=NOW, current_mrr_usd=12000)
    assert plan["counts"]["go_hard"] == 1
    remakes = plan["remix_jobs"]
    assert {j["target_page_id"] for j in remakes} == {"B", "C", "D"}               # every other page
    assert all(j["n_hooks"] == 5 and j["requirements"]["n_hooks"] == 5 and j["rule"] == "GO-HARD" for j in remakes)
    assert plan["fb_long_cuts"][0]["builder"] == "growth.variants.fb_long_cut"
    assert plan["trial_reels"][0]["count"] == 5 and plan["trial_reels"][0]["variant_role"] == "TEST"
    assert plan["email_features"][0]["status"] == "draft" and "human_send" in plan["email_features"][0]["requires"]
    assert plan["dm_pins"][0]["keyword"] == "STRONG"
    b = plan["boost_candidates"][0]
    assert b["status"] == "held_until_spend_gate" and b["gate_mrr_usd"] == 30000 and b["gate_open"] is False
    assert {"spend_gate", "human_approval", "governor_plan", "SPEND_ENABLED"} <= set(b["requires"])
    opened = A.mrr_plan([v], [post()], PAGES, now=NOW, current_mrr_usd=31000)["boost_candidates"][0]
    assert opened["gate_open"] is True and opened["status"] == "held_until_spend_gate"   # governor + human still decide


def test_go_hard_needs_views():
    v = SC.value_score(CARD, {"views": 2000, "mrr_usd": 200, "buyers": 5})
    v["money"] = 95.0
    assert A.mrr_plan([v], [post()], PAGES, now=NOW)["counts"]["go_hard"] == 0


def test_viral_but_not_paying_gets_reach_remix_and_cta_swap():
    card = {**CARD, "scores": {"hook": 97, "body": 95, "shares": 98, "saves": 96, "conversion": 5}}
    v = SC.value_score(card, {"views": 900000, "mrr_usd": 0, "buyers": 0})
    assert v["virality"] >= 80 and v["money"] < 40
    plan = A.mrr_plan([v], [post()], PAGES, now=NOW)
    assert plan["counts"]["go_hard"] == 0 and plan["remix_jobs"]
    assert all("reach remix" in j["rule"] for j in plan["remix_jobs"])
    exp = plan["cta_experiments"][0]
    assert exp["arms"][0] == "STRONG" and len(set(exp["arms"])) == 3 and exp["keep_hook_and_body"] is True


def test_weekly_readout_by_mrr_views_and_both():
    vals = [{"post_id": "a", "mrr_usd": 900, "views": 10000, "value": 60},
            {"post_id": "b", "mrr_usd": 50, "views": 2000000, "value": 70},
            {"post_id": "c", "mrr_usd": 400, "views": 500000, "value": 85}]
    r = A.weekly_readout(vals, n=2)
    assert [x["post_id"] for x in r["by_mrr"]] == ["a", "c"]
    assert [x["post_id"] for x in r["by_views"]] == ["b", "c"]
    assert [x["post_id"] for x in r["by_both"]] == ["c", "b"]
