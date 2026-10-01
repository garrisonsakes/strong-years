import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from common import config, media
from qa import face, ocr, qa, scoring
from tests.conftest import AUTH

pytestmark = pytest.mark.skipif(not ocr.available(), reason="tesseract not installed")


def _run(path, **kw):
    req = {"video_url": str(path), "asset_id": Path(path).stem, "script_text": kw.pop("script", ""),
           "expected_on_screen": ["CHAIR TEST"], "frames": 6, "checks": qa.ALL_CHECKS,
           "shot_map": kw.pop("shot_map", None)}
    req.update(kw)
    return qa.run(req)


@pytest.fixture(scope="module")
def shot_map(synth, stitched):
    from tests.conftest import build_manifest
    return [{k: t[k] for k in ("n", "route", "start_s", "duration_s")} for t in build_manifest(synth, stitched)["timeline"]]


@pytest.fixture(scope="module")
def good(master, shot_map):
    return _run(master["local_path"], script=master["transcript"], shot_map=shot_map, context={"judge_passed": True})


def _variant(master, name, args):
    out = config.WORK_DIR / f"broken_{name}.mp4"
    media.ffmpeg(["-i", master["local_path"], *args, str(out)])
    return out


def test_good_master_passes_deterministic_qa(good):
    m = good["metrics"]
    assert m["spec_ok"] and m["duration_ok"] and m["ai_tag_present"]
    assert abs(m["lufs_integrated"] + 14) <= 1 and m["true_peak_db"] <= -1
    assert m["black_max_s"] <= 0.25 and m["freeze_max_s"] <= 0.25
    assert m["caption_cer"] is not None and m["caption_cer"] <= 0.03 and not m["caption_number_mismatch"]
    assert good["decision"] in ("pass", "review") and good["route"] == "approval"
    assert len(good["frames"]) == 6
    assert good["skipped"]["syncnet"]


def test_silent_variant_fails(master):
    r = _run(_variant(master, "silent", ["-c:v", "copy", "-af", "volume=0", "-c:a", "aac", "-ar", "48000"]))
    assert r["metrics"]["lufs_integrated"] <= -60 and r["decision"] == "fail" and r["route"] == "regen"


def test_black_frames_variant_fails(master):
    r = _run(_variant(master, "black", ["-vf", "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,3,4.3)'",
                                        "-c:v", "libx264", "-preset", "ultrafast", "-profile:v", "high", "-c:a", "copy"]))
    assert r["metrics"]["black_max_s"] > 0.6 and r["decision"] == "fail"


def test_frozen_variant_fails(master):
    r = _run(_variant(master, "frozen", ["-vf", "loop=loop=36:size=1:start=90,setpts=N/30/TB", "-t", "9",
                                         "-c:v", "libx264", "-preset", "ultrafast", "-profile:v", "high", "-c:a", "copy"]))
    assert r["metrics"]["freeze_max_s"] > 0.6 and r["decision"] == "fail"


def test_wrong_aspect_variant_fails(master):
    r = _run(_variant(master, "landscape", ["-vf", "scale=1920:1080", "-c:v", "libx264", "-preset", "ultrafast",
                                            "-c:a", "copy"]))
    assert r["metrics"]["spec_ok"] is False and any("spec" in x for x in r["reasons"]) and r["decision"] == "fail"


def test_missing_ai_tag_fails(master):
    z_top = 230
    r = _run(_variant(master, "notag", ["-vf", f"drawbox=x=30:y={z_top - 5}:w=300:h=90:color=0x7A3E1D:t=fill",
                                        "-c:v", "libx264", "-preset", "ultrafast", "-profile:v", "high", "-c:a", "copy"]))
    assert r["metrics"]["ai_tag_present"] is False and r["decision"] == "fail"


def test_graphic_freeze_is_excluded_only_inside_graphic_shots(master):
    no_map = _run(master["local_path"], script=master["transcript"], checks=["blackdetect", "freezedetect"])
    with_map = _run(master["local_path"], script=master["transcript"], checks=["blackdetect", "freezedetect"],
                    shot_map=[{"n": 4, "route": "graphic", "start_s": 0, "duration_s": 99}])
    assert with_map["metrics"]["freeze_max_s"] <= no_map["metrics"]["freeze_max_s"]


def test_caption_ocr_catches_wrong_numbers():
    assert ocr.best_window_cer("Men under twelve is below", "men under twelve is below average")[0] == 0
    assert ocr.best_window_cer("Men undr twelve", "men under twelve is below average")[0] < 0.1
    assert ocr.numbers_in("under 13") - ocr.numbers_in("under twelve") == {"13"}


# ---------- scoring / routing ----------
GOOD = {"lufs_integrated": -14.2, "true_peak_db": -1.5, "caption_cer": 0.0, "caption_number_mismatch": False,
        "black_max_s": 0, "freeze_max_s": 0, "spec_ok": True, "ai_tag_present": True, "duration_ok": True,
        "face_sim_median": 0.6, "face_sim_min": 0.45, "syncnet_conf": 7, "syncnet_dist": 7}


@pytest.mark.parametrize("patch,det", [({}, "pass"), ({"face_sim_median": 0.5}, "review"), ({"face_sim_median": 0.4}, "fail"),
                                       ({"lufs_integrated": -15.5}, "review"), ({"lufs_integrated": -17}, "fail"),
                                       ({"true_peak_db": -0.5}, "review"), ({"caption_cer": 0.02}, "review"),
                                       ({"caption_cer": 0.0, "caption_number_mismatch": True}, "fail"),
                                       ({"freeze_max_s": 0.4}, "review"), ({"black_max_s": 0.7}, "fail"),
                                       ({"syncnet_conf": 5}, "review"), ({"syncnet_dist": 9.5}, "fail"),
                                       ({"spec_ok": False}, "fail"), ({"ai_tag_present": False}, "fail"),
                                       ({"face_sim_median": None, "syncnet_conf": None}, "pass")])
def test_bands_match_prompt_07(patch, det):
    assert scoring.deterministic({**GOOD, **patch})[0] == det


def test_routes():
    assert scoring.score(GOOD, vision_decision="pass", trusted=True)["route_label"] == "auto_publish"
    assert scoring.score(GOOD, vision_decision="pass", trusted=True, risk_tier="yellow")["route"] == "approval"
    assert scoring.score(GOOD, vision_decision="review", trusted=True)["route"] == "approval"
    assert scoring.score(GOOD, trusted=False)["route"] == "approval"
    bad = {**GOOD, "spec_ok": False}
    assert scoring.score(bad, attempts=1)["route_label"] == "re_render"
    assert scoring.score(bad, attempts=3)["route"] == "human"
    assert scoring.score(GOOD, uniqueness_allow=False)["route"] == "human"


def test_thresholds_in_sync_with_n8n_decide_qa_route():
    wf = json.loads((config.SPEC_DIR / "n8n_core_workflow.json").read_text())
    code = next(n for n in wf["nodes"] if n["name"] == "Decide QA Route")["parameters"]["jsCode"]
    for frag in ["x >= 0.55, x => x >= 0.45", "x >= 0.40, x => x >= 0.32", "x >= 6.0, x => x >= 4.5",
                 "x <= 8.0, x => x <= 9.0", "Math.abs(x + 14) <= 1, x => Math.abs(x + 14) <= 2",
                 "x <= -1.0, x => x <= -0.3", "x <= 0.01", "x <= 0.03", "x <= 0.25, x => x <= 0.6",
                 "m.ai_tag_present === false", "Worker: Uniqueness Guard"]:
        assert frag in code, frag


def test_face_hook_skips_cleanly_without_models():
    ok, why = face.available()
    if ok:
        pytest.skip("insightface installed")
    r = face.face_similarity([], [])
    assert r["face_sim_median"] is None and r["face_status"] == "skipped" and why


def test_qa_api(master):
    from app import app
    c = TestClient(app, headers=AUTH)
    r = c.post("/qa", json={"video_url": master["local_path"], "checks": ["ffprobe", "ebur128"], "frames": 2})
    assert r.status_code == 200 and r.json()["metrics"]["spec_ok"]
    assert c.post("/qa", json={}).status_code == 422
    r = c.post("/qa/score", json={"metrics": GOOD, "vision_decision": "pass", "trusted": True, "judge_passed": True})
    assert r.json()["route"] == "auto"
