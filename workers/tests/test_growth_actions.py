"""Winner actions are QUEUED JOBS (growth/actions, growth/adpolicy): remixes go to OTHER pages with the uniqueness
and YouTube-policy constraints attached, boost candidates are re-checked under the stricter ad policy with the
mandatory judge and never approved here, pins are suggestions, losers are down-weighted. Nothing publishes."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from growth import actions as A, adpolicy, config as G

NOW = datetime(2026, 10, 2, 9, 0, tzinfo=timezone.utc)
PAGES = [
    {"id": "A", "slug": "changyin", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P01", "P02", "P15"], "speakers": ["CHANG", "DUO"]}},
    {"id": "B", "slug": "sunyoon-kitchen", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P11", "P12", "P15"], "speakers": ["SUN", "DUO"]}},
    {"id": "C", "slug": "changandsun", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P15", "P17"], "speakers": ["DUO", "CHANG", "SUN"]}},
    {"id": "D", "slug": "changyin-strength", "status": "active", "locale": "en-US", "page_dna": {"pillars": ["P01", "P02"], "speakers": ["CHANG"]}},
    {"id": "E", "slug": "changyin-espanol", "status": "active", "locale": "es-US", "page_dna": {"pillars": ["P01"], "speakers": ["CHANG"]}},
    {"id": "F", "slug": "paused", "status": "paused", "locale": "en-US", "page_dna": {"pillars": ["P15"]}},
]


def score(post_id="w1", page="A", platform="instagram", cls="WINNER", sc=2.1, views=90000, **k):
    d = {"post_id": post_id, "page_id": page, "platform": platform, "class": cls, "score": sc, "views": views, "save_rate_z": 0.5}
    d.update(k)
    return d


def post(post_id="w1", **k):
    d = {"post_id": post_id, "published_at": "2026-10-01T15:00:00+00:00", "set_code": "S03", "hook_id": "H_IF_017",
         "arm": {"pillar": "P15", "grammar": "IF_EVERY", "format": "F04", "speaker": "CHANG", "length": "M"},
         "caption": "AI character. If you drink onion water every morning, watch what happens. 14-day money-back guarantee. $25 per month, cancel anytime.",
         "burned_in_text": ["IF YOU DRINK THIS EVERY MORNING"], "hook": "Onion water every morning?", "evidence": ["E25"],
         "page_slug": "changyin"}
    d.update(k)
    return d


def judge_ok(subject, hits, **kw):
    return {"status": "ok", "verdict": "pass", "confidence": 0.95, "model": "stub"}


def judge_down(subject, hits, **kw):
    return {"status": "skipped", "verdict": "human", "confidence": 0.0, "reason": "no key"}


@pytest.fixture
def cfg():
    return G.load()


# ---------------------------------------------------------------- remix jobs
def test_remixes_go_to_other_active_same_language_pages_with_stagger(cfg):
    out = A.plan([score()], [post()], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    jobs = out["remix_jobs"]
    assert 1 <= len(jobs) <= cfg["remix"]["variants_per_winner"]
    targets = {j["target_page_id"] for j in jobs}
    assert "A" not in targets and "E" not in targets and "F" not in targets        # not self, not Spanish, not paused
    for j in jobs:
        assert j["kind"] == "remix" and j["status"] == "queued" and j["priority"] == 90 and j["level"] == "L3"
        assert datetime.fromisoformat(j["earliest_at"]) >= NOW + timedelta(hours=48)
        assert j["preferred_slot_hour"] != 15                                      # never the source's slot hour
        req = j["requirements"]
        assert req["new_hook_same_grammar"] and req["different_set"] and req["new_opening_frame"] and req["new_captions"]
        assert req["exclude_set_codes"] == ["S03"] and j["grammar"] == "IF_EVERY" and j["pillar"] == "P15"
        assert "/uniqueness/check" in j["must_pass"] and "llm_judge" in j["must_pass"]
        assert j["uniqueness_thresholds"]["text_network"] <= 0.80
    # pages that run the pillar and a different speaker come first
    assert jobs[0]["target_page_id"] in ("B", "C")
    assert all(j["speaker"] != "CHANG" or j["target_page_id"] == "D" for j in jobs)   # different pairing when the page allows


def test_per_source_and_per_target_daily_caps(cfg):
    recent = [{"source_post_id": "w1", "target_page_id": "B", "created_at": NOW.isoformat()}]
    out = A.plan([score()], [post()], PAGES, cfg, now=NOW, recent_remixes=recent, judge_fn=judge_ok)
    assert all(j["target_page_id"] != "B" for j in out["remix_jobs"])
    assert len(out["remix_jobs"]) <= cfg["remix"]["variants_per_winner"] - 1
    recent = [{"source_post_id": "w1", "target_page_id": t, "created_at": NOW.isoformat()} for t in ("B", "C", "D")]
    assert A.plan([score()], [post()], PAGES, cfg, now=NOW, recent_remixes=recent, judge_fn=judge_ok)["remix_jobs"] == []
    # another winner the same hour can't land a second remix on the same target page today
    two = A.plan([score("w1"), score("w2", sc=2.0)], [post("w1"), post("w2")], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    per_target: dict = {}
    for j in two["remix_jobs"]:
        per_target[j["target_page_id"]] = per_target.get(j["target_page_id"], 0) + 1
    assert max(per_target.values()) <= cfg["remix"]["max_per_target_page_per_day"]


def test_youtube_winner_is_limited_by_the_july_2026_policy(cfg):
    out = A.plan([score(platform="youtube")], [post()], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    assert len(out["remix_jobs"]) == 1
    j = out["remix_jobs"][0]
    assert j["requirements"]["youtube_inauthentic_policy_2026_07"] and j["requirements"]["require_distinct_first_frame"]
    assert j["requirements"]["new_voice_render"]
    assert j["uniqueness_thresholds"]["text_network"] <= 0.70 and j["uniqueness_thresholds"]["shared_run_max"] <= 4
    assert out["boost_candidates"] == [] and out["pin_suggestions"] == []          # no YouTube boost/pin channel


def test_duo_only_format_forces_duo_speaker(cfg):
    p = post(arm={"pillar": "P17", "grammar": "SHARE", "format": "F08", "speaker": "DUO", "length": "S"})
    out = A.plan([score()], [p], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    assert all(j["speaker"] == "DUO" for j in out["remix_jobs"])


# ---------------------------------------------------------------- boost candidates
def test_boost_candidate_waits_for_a_human_even_when_everything_passes(cfg):
    out = A.plan([score()], [post()], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    bc = out["boost_candidates"]
    assert len(bc) == 1 and bc[0]["status"] == "awaiting_human_approval" and bc[0]["channel"] == "meta_partnership"
    assert bc[0]["compliance"]["verdict"] == "pass" and bc[0]["compliance"]["judge_passed"] is True
    assert "human_approval" in bc[0]["requires"] and "SPEND_ENABLED" in bc[0]["requires"] and bc[0]["ai_label_kept"]
    assert bc[0]["requested_daily_usd"] == cfg["boost"]["default_max_daily_usd"]


def test_boost_goes_to_human_when_the_judge_is_unavailable(cfg):
    out = A.plan([score()], [post()], PAGES, cfg, now=NOW, judge_fn=judge_down)
    assert out["boost_candidates"][0]["status"] == "needs_human"
    assert out["boost_candidates"][0]["compliance"]["judge_passed"] is False


def test_boost_uses_the_real_judge_module_by_default_and_fails_closed(cfg):
    out = A.plan([score()], [post()], PAGES, cfg, now=NOW)                         # no ANTHROPIC_API_KEY in tests
    assert out["boost_candidates"][0]["status"] == "needs_human"


@pytest.mark.parametrize("text,rule", [
    ("Are you over 60 and tired all the time? AI character.", "AD-ATTR"),
    ("If you have knee pain, do this. AI character.", "AD-ATTR"),
    ("Before and after: 30 days of chair squats. AI character.", "AD-B/A"),
    ("She lost 12 lbs in a month. AI character.", "AD-B/A"),
    ("This drink lowers blood pressure. AI character.", "AD-DISEASE"),
    ("Reverse arthritis with one stretch. AI character.", "AD-DISEASE"),
    ("Prevent falls with this 2-minute drill. AI character.", "AD-FALL"),
    ("Cut your fall risk in half. AI character.", "AD-FALL"),
    ("Instant relief, guaranteed results. AI character.", "AD-INSTANT"),
    ("Nobody wants a nursing home. AI character.", "AD-FEAR"),
    ("Dr. Chang explains. AI character.", "AD-CRED"),
    ("A chair, a wall, two minutes. Join for $25 a month, cancel anytime.", "AD-AI"),
    ("AI character. Join today for $25.", "AD-PRICE"),
])
def test_ad_policy_flags_targeting_before_after_disease_falls(cfg, text, rule):
    hits = adpolicy.deterministic({"primary_text": text})
    assert rule in {h["rule"] for h in hits}, hits


def test_ad_policy_clean_copy_passes_deterministic_rules():
    clean = ("AI character, created by a team. Chair stands, two minutes, most mornings. Sun's soup after. "
             "Membership $25 per month, renews monthly, cancel online anytime. 14-day money-back guarantee.")
    assert adpolicy.deterministic({"primary_text": clean}) == []


def test_ad_policy_evasion_normalised():
    hits = adpolicy.deterministic({"primary_text": "Prеvent fаlls. AI character."})   # Cyrillic е / а
    assert "AD-FALL" in {h["rule"] for h in hits}


def test_flagged_boost_candidate_is_routed_to_human_not_queued_for_approval(cfg):
    p = post(caption="AI character. Are you over 65 and tired? Prevent falls today. $25/month, cancel anytime.")
    out = A.plan([score()], [p], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    bc = out["boost_candidates"][0]
    assert bc["status"] == "flagged_human" and {"AD-ATTR", "AD-FALL"} <= {h["rule"] for h in bc["compliance"]["hits"]}


def test_organic_scanner_block_flags_the_boost(cfg):
    p = post(caption="AI character. This detox tea melts belly fat. $25 per month, cancel anytime.")
    out = A.plan([score()], [p], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    assert out["boost_candidates"][0]["status"] == "flagged_human"


def test_boost_without_any_ad_text_needs_a_human(cfg):
    p = post(caption="", burned_in_text=[], hook="")
    out = A.plan([score()], [p], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    assert out["boost_candidates"][0]["status"] == "needs_human"


def test_only_winners_get_boost_or_pin_and_losers_are_downweighted(cfg):
    scores = [score("p", cls="PROMISING", sc=1.0), score("n", cls="NORMAL", sc=0.1), score("l", cls="LOSER", sc=-1.4)]
    out = A.plan(scores, [post("p"), post("n"), post("l")], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    assert out["remix_jobs"] == [] and out["boost_candidates"] == [] and out["pin_suggestions"] == []
    assert len(out["downweights"]) == 1
    d = out["downweights"][0]
    assert d["post_id"] == "l" and d["reward"] == 0.0 and 0 < d["weight_multiplier"] < 1 and d["arm"]["grammar"] == "IF_EVERY"
    assert out["counts"]["skipped"] == 2


def test_pin_suggestions_per_platform_and_highlight_on_high_saves(cfg):
    out = A.plan([score(platform="instagram", save_rate_z=1.4), score("t", platform="tiktok"), score("x", platform="x"),
                  score("th", platform="threads"), score("fb", platform="facebook")],
                 [post(), post("t"), post("x"), post("th"), post("fb")], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    pins = {p["platform"]: p for p in out["pin_suggestions"]}
    assert pins["instagram"]["action"] == "pin_to_grid" and "add_to_highlight" in pins["instagram"]["also"]
    assert pins["tiktok"]["action"] == "pin_to_profile" and pins["facebook"]["action"] == "feature_on_page"
    assert all(p["status"] == "suggested" for p in pins.values())
    assert {b["platform"] for b in out["boost_candidates"]} == {"instagram", "tiktok", "facebook"}
    assert out["boost_candidates"][1]["channel"] in ("tiktok_spark", "meta_partnership")


def test_nothing_in_the_plan_publishes_or_spends(cfg):
    out = A.plan([score()], [post()], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    statuses = {j["status"] for k in ("remix_jobs", "boost_candidates", "pin_suggestions") for j in out[k]}
    assert statuses <= {"queued", "awaiting_human_approval", "flagged_human", "needs_human", "suggested"}
    assert not any(s in ("published", "approved", "executed", "live") for s in statuses)


def test_missing_post_context_and_unknown_page_are_tolerated(cfg):
    out = A.plan([score(page="ZZZ")], [], PAGES, cfg, now=NOW, judge_fn=judge_ok)
    assert out["remix_jobs"] == [] and len(out["boost_candidates"]) == 1
