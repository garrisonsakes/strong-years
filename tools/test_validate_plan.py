"""pytest tools/test_validate_plan.py"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_posting_plan as bp  # noqa: E402
import validate_plan as vp  # noqa: E402

ROWS = bp.build()


def _fails(rows, needle):
    return any(needle in e for e in vp.validate(rows))


def test_built_plan_is_valid():
    assert vp.validate(ROWS) == []


def test_csv_on_disk_matches_build():
    assert [r["file_id"] for r in vp.load()] == [r["file_id"] for r in ROWS]


def test_duplicate_file_detected():
    rows = copy.deepcopy(ROWS)
    rows[1]["file_id"] = rows[0]["file_id"]
    assert _fails(rows, "used 2x")


def test_script_reuse_detected():
    rows = copy.deepcopy(ROWS)
    lib = [r for r in rows if r["script_id"] != "GEN-needed"]
    other = next(r for r in lib if r["uniqueness_group"] != lib[0]["uniqueness_group"])
    other["script_id"] = lib[0]["script_id"]
    assert _fails(rows, "reused")


def test_cadence_shortfall_detected():
    rows = [r for r in ROWS if not (r["page"] == "@changyin" and r["platform"] == "tiktok" and r["day_index"] == 10)]
    assert _fails(rows, "cadence @changyin tiktok D+10")


def test_waitlist_after_launch_detected():
    rows = copy.deepcopy(ROWS)
    r = next(r for r in rows if r["day_index"] == 20)
    r["cta_type"] = "waitlist"
    assert _fails(rows, "waitlist CTA after D0")


def test_offer_in_runway_detected():
    rows = copy.deepcopy(ROWS)
    r = next(r for r in rows if r["day_index"] == -6)
    r["cta_type"] = "join"
    assert _fails(rows, "offer CTA in runway")


def test_offer_cap_detected():
    rows = copy.deepcopy(ROWS)
    for r in rows:
        if r["day_index"] == 30 and r["page"] == "@changyin" and r["platform"] == "x":
            r["cta_type"] = "book"
    assert _fails(rows, "offer cap")


def test_movement_before_shoot_detected():
    rows = copy.deepcopy(ROWS)
    r = next(r for r in rows if r["day_index"] == -7 and r["platform"] == "ig_reels")
    r["render_lane"] = "movement"
    assert _fails(rows, "movement before shoot")


def test_ramp_and_rollout():
    for page in ("@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength"):
        assert [bp.cadence(page, d) for d in (-7, -5, -4, -1, 0, 6, 7, 90)] == [3, 3, 5, 5, 6, 6, 6, 6]
    assert len(bp.PAGES) == 4
    masters = {r["uniqueness_group"] for r in ROWS if r["day_index"] == 20}
    assert len(masters) == 24


def test_second_render_detected():
    rows = copy.deepcopy(ROWS)
    r = next(r for r in rows if r["platform"] == "yt_shorts")
    r["render_id"] = r["render_id"] + "-yt"
    assert _fails(rows, "renders")


def test_movement_cap_and_demo_detected():
    rows = copy.deepcopy(ROWS)
    g = next(r["uniqueness_group"] for r in rows if r["day_index"] == 30 and r["page"] == "@changyin" and r["render_lane"] == "talking_head")
    for r in rows:
        if r["uniqueness_group"] == g and r["platform"] in bp.VIDEO_PLATFORMS:
            r["render_lane"] = "movement"
    assert _fails(rows, "movement")


def test_broll_cap_detected():
    rows = copy.deepcopy(ROWS)
    for r in rows:
        if r["day_index"] == 40 and r["platform"] in bp.VIDEO_PLATFORMS:
            r["render_lane"] = "insert"
    assert _fails(rows, "B-roll cap")


# ---- variants: Trial Reels + Facebook native (ENGINE_100X §1, §2.1, §5) ------------------------------------------
VROWS = bp.build_variants(ROWS)
import account_topology as AT  # noqa: E402
# CANON UPDATE 6: the build adds one text + one photo per FB PAGE and 3 Stories per IG page per day (build_posting_plan __main__).
VROWS = AT.fb_text_photo_rows(VROWS) + AT.stories_rows(ROWS, bp.stage)
AROWS = AT.apply(ROWS)


def _vfails(rows, vrows, needle):
    return any(needle in e for e in vp.validate_all(rows, vrows))


def test_variant_plan_valid_and_ramped():
    assert vp.validate_all(ROWS, VROWS, AROWS) == []
    trials = [r for r in VROWS if r["platform"] == "ig_trial"]
    per = lambda d: sum(1 for r in trials if r["page"] == "@changyin" and r["day_index"] == d)
    assert (per(-7), per(7), per(14), per(60)) == (3, 6, 12, 12)
    assert all(r["variant_role"] == "TEST" for r in trials)
    assert sum(r["platform"] == "fb_text" for r in VROWS) == sum(r["platform"] == "fb_photo" for r in VROWS) > 0


def test_trial_cap_body_repeat_and_ss_performance_detected():
    v = copy.deepcopy(VROWS)
    t = [r for r in v if r["platform"] == "ig_trial" and r["page"] == "@changyin" and r["day_index"] == 2]
    v.append({**t[0], "file_id": "extra", "variant_id": "extra"})
    assert _vfails(ROWS, v, "ramp cap")
    rows = copy.deepcopy(ROWS)
    a, b = [r for r in rows if r["platform"] == "tiktok" and r["page"] == "@changyin"][:2]
    b["body_id"] = a["body_id"]
    assert _vfails(rows, VROWS, "twice on @changyin x tiktok within 30 d")
    v = copy.deepcopy(VROWS)
    t = [r for r in v if r["platform"] == "ig_trial" and r["day_index"] == 40]
    for r in t:
        r["graduation_strategy"] = "SS_PERFORMANCE"
    assert _vfails(ROWS, v, "SS_PERFORMANCE trials")


def test_low_value_trial_and_fb_crosspost_detected():
    v = copy.deepcopy(VROWS)
    t = next(r for r in v if r["platform"] == "ig_trial")
    t["dims_changed"] = "caption|length"
    assert _vfails(ROWS, v, "incl. the opening")
    rows = copy.deepcopy(ROWS)
    fb = next(r for r in rows if r["platform"] == "fb_reels")
    fb["variant"], fb["caption_source"] = "platform_package", "ig_crosspost"
    assert _vfails(rows, VROWS, "native upload")
    rows = copy.deepcopy(ROWS)
    fb = next(r for r in rows if r["variant"] == "fb_long")
    fb["seconds"] = 200
    assert _vfails(rows, VROWS, "outside 60-180 s")


def test_account_topology_canon6():
    """CANON UPDATE 6: 1 YouTube channel (4/day until the quota raise), 1 FB page (12 videos + 2 long + text + photo),
    TikTok accounts separate from IG pages, 3 Stories per IG page per day; held rows stay packaged, never scheduled."""
    day1 = AT.summary(AROWS, VROWS, 1)
    assert day1["@strongyears|yt_shorts"] == 4 and not any(k.endswith("|yt_shorts") and not k.startswith("@strongyears") for k in day1)
    assert day1["Strong Years|fb_reels"] == 14 and day1["Strong Years|fb_text"] == 1 and day1["Strong Years|fb_photo"] == 1
    assert all(day1[f"{p}|ig_story"] == 3 for p in bp.PAGES if p in AT.TT_ACCOUNTS)
    for p in bp.PAGES:
        assert day1[f"{AT.TT_ACCOUNTS[p]}|tiktok"] == 6 and AT.TT_ACCOUNTS[p] != p
    held = [r for r in AROWS if r["publish"] == "held"]
    assert held and all(r["platform"] in ("yt_shorts", "fb_reels") for r in held)
    # A YT row over the cap or a TikTok row on the IG handle is caught.
    bad = copy.deepcopy(AROWS)
    extra = next(r for r in bad if r["platform"] == "yt_shorts" and r["publish"] == "held")
    extra["publish"] = "y"
    assert any("youtube" in e for e in AT.validate(bad, VROWS))
    bad2 = copy.deepcopy(AROWS)
    tt = next(r for r in bad2 if r["platform"] == "tiktok")
    tt["account"] = tt["page"]
    assert any("separate accounts" in e for e in AT.validate(bad2, VROWS))
    # Dropping a Stories row is caught.
    assert any("stories" in e for e in AT.validate(AROWS, [v for v in VROWS if v["file_id"] != "ST-CY-+01-poll"]))
