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
