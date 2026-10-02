"""Content allocator (growth/allocator, growth/catalog): Thompson sampling over pillar x grammar x format x speaker
x length with a hard 20% exploration floor, decay, cadence and uniqueness constraints; the catalogue stays in sync
with CONTENT_SYSTEM.md, tools/build_content.py and CHARACTERS.md."""
from __future__ import annotations

import ast
import re
from datetime import datetime, timedelta, timezone

import pytest

from common import config as C
from growth import allocator as AL, catalog as CAT, config as G

NOW = datetime(2026, 10, 1, 23, 10, tzinfo=timezone.utc)
PAGE = {"id": "A", "slug": "changyin", "daily_post_target": 7,
        "page_dna": {"pillars": ["P01", "P02", "P03", "P05", "P14", "P15", "P20"], "speakers": ["CHANG", "DUO"]}}


@pytest.fixture
def cfg():
    return G.load()


def obs(arm: dict, reward: float, days_ago: float = 1.0) -> dict:
    return {"arm": arm, "reward": reward, "at": (NOW - timedelta(days=days_ago)).isoformat()}


# ---------------------------------------------------------------- catalogue <-> specs
def test_catalog_in_sync_with_specs():
    cs = (C.SPEC_DIR / "CONTENT_SYSTEM.md").read_text()
    for pillar, formats in CAT.PILLAR_FORMATS.items():
        row = next(l for l in cs.splitlines() if l.startswith(f"| {pillar} |"))
        assert all(f in row for f in formats), (pillar, formats)
    src = (C.SPEC_DIR / "tools" / "build_content.py").read_text()
    grammars = ast.literal_eval(re.search(r"^GRAMMARS = (\{.*\})$", src, re.M).group(1))
    proven = ast.literal_eval(re.search(r"^PROVEN = (\(.*\))", src, re.M).group(1))
    assert set(CAT.GRAMMARS) | set(CAT.EXCLUDED_GRAMMARS) == grammars | {"NOT_X"}
    assert set(CAT.PROVEN_GRAMMARS) == set(proven)
    assert "LAUNCH" in CAT.EXCLUDED_GRAMMARS
    ch = (C.SPEC_DIR / "CHARACTERS.md").read_text()
    assert "### 24 running bits" in ch and len(CAT.RUNNING_BITS) == 24
    assert len(set(CAT.RUNNING_BITS)) == 24


# ---------------------------------------------------------------- arms
def test_eligible_arms_respect_page_dna_platform_and_duo_formats(cfg):
    arms = AL.eligible_arms(PAGE, "instagram", cfg)
    assert arms and all(a["pillar"] in PAGE["page_dna"]["pillars"] for a in arms)
    assert all(a["format"] in CAT.PILLAR_FORMATS[a["pillar"]] for a in arms)
    assert all(a["grammar"] != "LAUNCH" for a in arms)
    assert all(a["speaker"] == "DUO" for a in arms if a["format"] in CAT.DUO_ONLY_FORMATS)
    assert all(a["speaker"] in ("CHANG", "DUO") for a in arms)
    for platform in G.PLATFORMS:                                                     # platform-restricted formats stay home
        for a in AL.eligible_arms(PAGE, platform, cfg):
            only = cfg["allocator"]["platform_formats_only"].get(a["format"])
            assert only is None or platform in only


def test_posterior_decays_old_evidence_and_borrows_a_hierarchical_prior(cfg):
    arm = {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02", "speaker": "CHANG", "length": "M"}
    fresh = AL.posterior([obs(arm, 1.0, 0)], [arm], cfg, NOW)[AL.arm_key(arm)]
    stale = AL.posterior([obs(arm, 1.0, 140)], [arm], cfg, NOW)[AL.arm_key(arm)]
    assert fresh["n"] == 1.0 and stale["n"] < 0.01 and fresh["mean"] > stale["mean"]
    sibling = {**arm, "length": "L"}                                                 # unseen arm, shares 4 factors
    post = AL.posterior([obs(arm, 1.0, 0)] * 3, [arm, sibling], cfg, NOW)
    assert post[AL.arm_key(sibling)]["n"] == 0 and post[AL.arm_key(sibling)]["prior_n"] > 0
    assert post[AL.arm_key(sibling)]["mean"] > 0.5
    loser_sib = {**arm, "length": "S"}
    post = AL.posterior([obs(arm, 0.0, 0)] * 3, [arm, loser_sib], cfg, NOW)
    assert post[AL.arm_key(loser_sib)]["mean"] < 0.5


def test_posterior_ignores_garbage_observations(cfg):
    arm = {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02", "speaker": "CHANG", "length": "M"}
    bad = [{"arm": arm, "reward": float("nan")}, {"arm": arm, "reward": 2.0}, {"arm": arm, "reward": -1}, {"reward": 1.0},
           {"arm": arm, "reward": 1.0, "at": "garbage", "weight": float("inf")}]
    p = AL.posterior(bad, [arm], cfg, NOW)[AL.arm_key(arm)]
    assert p["n"] == 1.0                                                              # only the garbage-dated one counts (at -> now)


# ---------------------------------------------------------------- plans
def test_plan_has_cadence_slots_and_the_exploration_floor(cfg):
    plan = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, seed=7, now=NOW)
    assert plan["cadence"] == 7 and len(plan["slots"]) == 7
    assert plan["explore_share"] >= 0.20 and plan["explore_floor"] >= G.MIN_EXPLORE_FLOOR
    for i, s in enumerate(plan["slots"]):
        assert s["slot_index"] == i and 0 <= s["hour"] <= 23 and s["length_s"]["min"] <= s["length_s"]["target"] <= s["length_s"]["max"]
        assert s["render_format"] in ("R1_talk_prop", "R2_prop_demo", "R3_motion_exercise", "R4_duo_dialogue", "T1_text_native")
        assert s["mode"] in ("exploit", "explore") and s["priority"] == 50
    assert plan["slots"][0]["hour"] < plan["slots"][-1]["hour"]


def test_cadence_is_capped_at_nine_and_floor_holds_at_every_cadence(cfg):
    for n in range(1, 13):
        plan = AL.plan_day(PAGE, "tiktok", "2026-10-02", [], cfg, cadence=n, seed=n, now=NOW)
        assert plan["cadence"] == min(n, 9)
        if plan["cadence"] > 1:
            assert plan["explore_share"] >= 0.20
    with pytest.raises(ValueError):
        G.load({"allocator": {"max_cadence": 12}})


def test_plan_is_deterministic_for_a_seed_and_varies_across_seeds(cfg):
    a = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, seed=1, now=NOW)
    b = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, seed=1, now=NOW)
    c = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, seed=2, now=NOW)
    assert [s["arm_key"] for s in a["slots"]] == [s["arm_key"] for s in b["slots"]]
    assert [s["arm_key"] for s in a["slots"]] != [s["arm_key"] for s in c["slots"]]
    d = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, now=NOW)              # default seed = page|platform|date
    e = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, now=NOW)
    assert [s["arm_key"] for s in d["slots"]] == [s["arm_key"] for s in e["slots"]]


def test_constraints_no_repeat_arm_no_adjacent_grammar_pillar_cap_recent_triples(cfg):
    recent = [{"pillar": "P15", "grammar": "MYTH", "format": "F04"}]
    for seed in range(20):
        plan = AL.plan_day(PAGE, "instagram", "2026-10-02", [], cfg, cadence=9, seed=seed, recent=recent, now=NOW)
        keys = [s["arm_key"] for s in plan["slots"]]
        assert len(set(keys)) == len(keys)
        per_pillar: dict = {}
        for s in plan["slots"]:
            per_pillar[s["pillar"]] = per_pillar.get(s["pillar"], 0) + 1
            assert (s["pillar"], s["grammar"], s["editorial_format"]) != ("P15", "MYTH", "F04")
        assert max(per_pillar.values()) <= max(cfg["allocator"]["max_per_pillar_per_day"], -(-9 // len(PAGE["page_dna"]["pillars"])))
        grams = [s["grammar"] for s in plan["slots"]]
        assert all(grams[i] != grams[i + 1] for i in range(len(grams) - 1))


def test_exploit_slots_follow_the_evidence(cfg):
    """40 good observations on P01 x IF_EVERY arms and 40 bad ones on P02 x DEBUNK arms (spread over formats and
    lengths, as real data is): exploit slots lean on the proven factors and never on the losing pair. Chance level
    for 'P01 or IF_EVERY' is about 24% on this page; the per-pillar cap (2/day) and no-adjacent-grammar rule cap it
    well below 100%."""
    import random
    arms = AL.eligible_arms(PAGE, "instagram", cfg)
    rng = random.Random(0)
    good = [a for a in arms if a["pillar"] == "P01" and a["grammar"] == "IF_EVERY"]
    bad = [a for a in arms if a["pillar"] == "P02" and a["grammar"] == "DEBUNK"]
    observations = [obs(rng.choice(good), rng.uniform(0.7, 1.0), rng.uniform(0, 10)) for _ in range(40)]
    observations += [obs(rng.choice(bad), rng.uniform(0.0, 0.3), rng.uniform(0, 10)) for _ in range(40)]
    hits = total = bad_hits = 0
    for seed in range(30):
        plan = AL.plan_day(PAGE, "instagram", "2026-10-02", observations, cfg, cadence=7, seed=seed, now=NOW)
        exploit = [s for s in plan["slots"] if s["mode"] == "exploit"]
        total += len(exploit)
        hits += sum(1 for s in exploit if s["pillar"] == "P01" or s["grammar"] == "IF_EVERY")
        bad_hits += sum(1 for s in exploit if s["pillar"] == "P02" and s["grammar"] == "DEBUNK")
    assert hits / total >= 0.40 and bad_hits / total <= 0.03


def test_single_proven_arm_is_exploited_more_than_any_other_arm(cfg):
    good = {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02", "speaker": "CHANG", "length": "M"}
    observations = [obs(good, 1.0, d) for d in range(12)]
    counts: dict = {}
    for seed in range(40):
        plan = AL.plan_day(PAGE, "instagram", "2026-10-02", observations, cfg, cadence=7, seed=seed, now=NOW)
        for s in plan["slots"]:
            if s["mode"] == "exploit":
                counts[s["arm_key"]] = counts.get(s["arm_key"], 0) + 1
    top = max(counts, key=counts.get)
    assert top == AL.arm_key(good) and counts[top] >= 20


def test_loser_downweight_observations_cool_an_arm(cfg):
    arm = {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02", "speaker": "CHANG", "length": "M"}
    hot = AL.posterior([obs(arm, 0.9, 1)] * 5, [arm], cfg, NOW)[AL.arm_key(arm)]["mean"]
    cooled = AL.posterior([obs(arm, 0.9, 1)] * 5 + [{"arm": arm, "reward": 0.0, "weight": 0.8, "at": NOW.isoformat()}] * 5,
                          [arm], cfg, NOW)[AL.arm_key(arm)]["mean"]
    assert cooled < hot


def test_running_bits_every_duo_and_every_third_solo_with_cooldown(cfg):
    duo_page = {"id": "C", "slug": "sunyoon", "page_dna": {"pillars": ["P17", "P16", "P15"], "speakers": ["DUO"]}}
    plan = AL.plan_day(duo_page, "instagram", "2026-10-02", [], cfg, cadence=9, seed=3, now=NOW)
    bits = [s["running_bit"] for s in plan["slots"]]
    cool = cfg["allocator"]["bit_cooldown"]
    assert all(b for b in bits)                                                   # every duo video has a bit
    for i in range(len(bits)):                                                    # ...not reused within the cooldown
        assert bits[i] not in bits[max(0, i - cool):i]
    solo = {"id": "D", "slug": "changyin-strength", "page_dna": {"pillars": ["P01", "P02", "P03", "P04"], "speakers": ["CHANG"]}}
    plan = AL.plan_day(solo, "instagram", "2026-10-02", [], cfg, cadence=9, seed=3, now=NOW)
    assert sum(1 for s in plan["slots"] if s["running_bit"]) >= 3
    assert plan["used_bits"] and len(plan["used_bits"]) <= cfg["allocator"]["bit_cooldown"]


def test_page_without_eligible_arms_raises(cfg):
    with pytest.raises(ValueError):
        AL.plan_day({"id": "Z", "page_dna": {"pillars": ["P99"]}}, "instagram", "2026-10-02", [], cfg, now=NOW)


def test_text_native_formats_only_short_on_threads_and_x(cfg):
    page = {"id": "T", "slug": "changyin", "page_dna": {"pillars": ["P16", "P01"], "speakers": ["SUN", "CHANG"]}}
    for platform in ("threads", "x"):
        plan = AL.plan_day(page, platform, "2026-10-02", [], cfg, cadence=6, seed=1, now=NOW)
        for s in plan["slots"]:
            if s["render_format"] == "T1_text_native":
                assert s["length_bucket"] == "S"
        assert not any(s["editorial_format"] == "F36" for s in plan["slots"])


def test_tomorrow_helper():
    assert AL.tomorrow(NOW) == "2026-10-02"


# ---------- VIRALITY_SYSTEM.md §4: hook-family arm, exploration floor unchanged ----------
def test_hook_family_arm_learns_across_arms_and_keeps_floor(cfg):
    page = {"id": "p1", "slug": "changyin", "daily_post_target": 9}
    arms = AL.eligible_arms(page, "instagram", cfg)
    g = sorted({a["grammar"] for a in arms})[-1]
    wins = [obs(a, 0.95, 1) for a in [x for x in arms if x["grammar"] == g][:15]]
    fam = AL.hook_family_posterior(wins, cfg, NOW)
    assert fam[g]["mean"] == max(f["mean"] for f in fam.values()) and fam[g]["n"] > 10
    plan = AL.plan_day(page, "instagram", "2026-10-02", wins, cfg, seed=7, now=NOW)
    assert plan["explore_share"] >= 0.2 and next(iter(plan["hook_families"])) == g
    assert sum(1 for s in plan["slots"] if s["grammar"] == g) >= 2
