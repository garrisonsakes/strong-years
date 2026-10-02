"""Fixture tests for the day-1 launch kit. All HTTP is mocked (httpx.MockTransport); nothing reaches the network.

  cd production/launch_day && python3 -m pytest tests -q
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import httpx
import pytest

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "workers")]


@pytest.fixture(scope="module")
def rd(tmp_path_factory):
    out = tmp_path_factory.mktemp("day1")
    os.environ["DAY1_OUT"] = str(out)
    os.environ["DRY_RUN"] = "1"
    os.environ["DRY_SEC_PER_WORD"] = "0.45"  # accessibility gate caps speech at 2.5 words/s
    for k in ("OUTPUT_DIR", "WORK_DIR"):
        os.environ.pop(k, None)
    import render_day1
    importlib.reload(render_day1)
    # Concept renders are gitignored (production/refs/out/); use placeholder seeds when absent (fresh clones, CI).
    if not all(p.exists() for ps in render_day1.SEEDS.values() for p in ps):
        from PIL import Image
        seeds = out / "seeds"
        seeds.mkdir()
        for ch, ps in render_day1.SEEDS.items():
            render_day1.SEEDS[ch] = [seeds / p.name for p in ps]
            for p in render_day1.SEEDS[ch]:
                Image.new("RGB", (64, 64), (128, 96, 64)).save(p)
    render_day1._bootstrap_workers(out)
    return render_day1


def test_plan_builds_and_passes():
    import build_day1_plan as B
    plan, problems = B.build()
    assert problems == []
    posts = plan["posts"]
    assert len(posts) == 6
    for page in ("@changyin", "@sunyoon.kitchen"):
        mine = [p for p in posts if p["page"] == page]
        assert len(mine) == 3
        assert sum(p["cta_keyword"] == "WAITLIST" for p in mine) <= 1
    for p in posts:
        assert set(p["variants"]) == {"ig", "fb"}
        assert all(v["scheduled_at"].startswith("2026-10-01T") and v["scheduled_at"].endswith("-04:00") for v in p["variants"].values())
        assert all(v["caption"].rstrip().endswith("not medical advice. Check with your doctor before starting new exercise.")
                   for v in p["variants"].values())
        assert len(p["render"]["inserts"]) == 2
        routes = [b["route"] for b in p["beats"]]
        assert routes[0] == "talk" and routes[-1] == "talk" and routes.count("insert") == 2
    assert all(p["validation"]["uniqueness_guard"] == "allow" for p in posts)
    on_disk = json.loads((HERE / "day1_plan.json").read_text())
    assert on_disk["validation_summary"]["all_pass"] is True


def test_voice_samples_pass_compliance():
    from compliance import scanner
    vs = json.loads((HERE / "voice_samples/voice_samples.json").read_text())
    vd = json.loads((ROOT / "production/voices/voice_design.json").read_text())
    for ch in ("chang", "sun"):
        c = vs["characters"][ch]
        assert c["voice_design_prompt"] == vd["voices"][ch]["description"]
        assert len(c["approval_lines"]) == 3
        for line in c["approval_lines"]:
            assert scanner.scan(text=line)["verdict"] == "pass", line


@pytest.mark.parametrize("url,ok", [
    ("https://generativelanguage.googleapis.com/v1beta/models/x:generateContent", True),
    ("https://api.elevenlabs.io/v1/text-to-voice/design", True),
    ("https://queue.fal.run/fal-ai/kling-video/requests/1/status", True),
    ("https://v3.fal.media/files/a.mp4", True),
    ("http://api.elevenlabs.io/v1/x", False),
    ("https://evil.example.com/x", False),
    ("https://fal.media.evil.com/x", False),
    ("https://evilfal.media/x", False),
    ("https://user:pw@api.elevenlabs.io/v1/x", False),
])
def test_ssrf_allow_list(rd, url, ok):
    http = rd.SafeHttp(transport=httpx.MockTransport(lambda r: httpx.Response(200)), resolver=lambda h, p: ["93.184.216.34"])
    if ok:
        http.check(url)
    else:
        with pytest.raises(rd.NetPolicyError):
            http.check(url)


def test_private_ip_and_redirect_refused(rd):
    http = rd.SafeHttp(transport=httpx.MockTransport(lambda r: httpx.Response(200)), resolver=lambda h, p: ["10.0.0.5"])
    with pytest.raises(rd.NetPolicyError):
        http.check("https://api.elevenlabs.io/v1/x")
    http = rd.SafeHttp(transport=httpx.MockTransport(lambda r: httpx.Response(302, headers={"location": "http://169.254.169.254/"})),
                       resolver=lambda h, p: ["93.184.216.34"])
    with pytest.raises(rd.NetPolicyError):
        http.request("GET", "https://v3.fal.media/files/a.mp4")


def test_live_refuses_without_keys(rd, monkeypatch, tmp_path):
    monkeypatch.setenv("DRY_RUN", "0")
    for k in ("GEMINI_API_KEY", "ELEVENLABS_API_KEY", "FAL_KEY"):
        monkeypatch.delenv(k, raising=False)
    with pytest.raises(SystemExit):
        rd.build_ctx(tmp_path)


def test_live_stops_at_review_gate(rd, monkeypatch, tmp_path):
    """Live mode (mock transport, fake DNS) generates lock-pack candidates and then stops for a human sign-off."""
    monkeypatch.setenv("DRY_RUN", "0")
    for k in ("GEMINI_API_KEY", "ELEVENLABS_API_KEY", "FAL_KEY"):
        monkeypatch.setenv(k, "test-key")
    monkeypatch.setenv("REF_CANDIDATES", "1")
    mock = rd.MockBackend(tmp_path / "_mock")
    cx, _ = rd.build_ctx(tmp_path, transport=httpx.MockTransport(mock.handler), resolver=lambda h, p: ["93.184.216.34"])
    monkeypatch.setattr(rd, "REFS", tmp_path / "refs_root")        # never write production/refs/locked from a test
    with pytest.raises(rd.AwaitingApproval):
        rd.stage_refs(cx)
    assert len(json.loads((tmp_path / "refs/pack.json").read_text())) == 16
    assert not (tmp_path / "refs/locked.json").exists()
    assert all(c.startswith("POST generativelanguage.googleapis.com") for c in mock.calls)


def test_dry_run_end_to_end_one_post_and_resume(rd, capsys):
    out = Path(os.environ["DAY1_OUT"])
    assert rd.main(["--only", "D1-SK-2"]) == 0
    first = capsys.readouterr().out
    assert "DRY RUN" in first and "no network" in first
    pdir = out / "@sunyoon.kitchen" / "D1-SK-2"
    for f in ("master.mp4", "ig.mp4", "fb.mp4", "ig_cover.jpg", "fb_cover.jpg", "caption_ig.txt", "caption_fb.txt",
              "first_comment.txt", "qa.json", "post.json"):
        assert (pdir / f).is_file(), f
    post = json.loads((pdir / "post.json").read_text())
    assert post["status"] in ("READY_FOR_HUMAN_REVIEW", "HOLD")
    assert post["pack"]["held"] == [] and len(post["pack"]["packed"]) == 2
    assert (pdir / "pack/2026-10-01/@sunyoon.kitchen/ig/checklist.md").read_text().count("AI info") >= 1
    qa = json.loads((pdir / "qa.json").read_text())
    if "ai_tag" not in (qa.get("skipped") or {}):   # OCR check needs tesseract (installed in CI)
        assert qa["metrics"]["ai_tag_present"] is True
    assert -16 <= qa["metrics"]["lufs_integrated"] <= -12
    costs = json.loads((out / "costs_summary.json").read_text())
    assert costs["dry_run"] is True and costs["total_usd_estimate"] > 0
    shots = json.loads((pdir / "_src/assembly_manifest.json").read_text())["timeline"]
    assert sum(s["route"] == "broll" for s in shots) == 2
    # resume: nothing is re-requested
    assert rd.main(["--only", "D1-SK-2"]) == 0
    assert "mock HTTP calls: 0" in capsys.readouterr().out
