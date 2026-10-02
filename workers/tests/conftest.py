"""Shared fixtures: an isolated output/work dir and one short synthetic master (≈9 s) reused by QA/uniqueness tests."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from common import config, media

TOKEN = "test-worker-token"
AUTH = {"X-Worker-Token": TOKEN}


@pytest.fixture(scope="session", autouse=True)
def _isolated_dirs(tmp_path_factory):
    root = tmp_path_factory.mktemp("workers")
    config.OUTPUT_DIR = root / "out"
    config.WORK_DIR = root / "work"
    config.X264_PRESET = "superfast"   # ultrafast drops CABAC/8x8dct -> reports Constrained Baseline
    config.PUBLIC_BASE_URL = ""
    config.WORKER_TOKEN = TOKEN                 # auth is ON in tests (AUDIT H9); clients send AUTH headers
    config.DEV_NO_AUTH = False
    config.C2PA_ALLOW_DEV_CERT = True           # production default is off (AUDIT M10)
    config.REVIEWER_SIGNED = False
    config.REQUIRE_JUDGE = True                 # production default: the LLM judge is mandatory
    os.environ.pop("ANTHROPIC_API_KEY", None)   # tests never call the real API; judge results are stubbed
    config.LOCAL_MEDIA_ROOTS = [str(root)]      # synthetic assets live under the session tmp root
    config.ensure_dirs()
    yield root


def tts(text: str, voice: str, out: Path) -> tuple[Path, dict]:
    tf = out.with_suffix(".txt")
    tf.write_text(text)
    media.ffmpeg(["-f", "lavfi", "-i", f"flite=textfile={tf}:voice={voice}", "-af", "atempo=1.12,aresample=48000",
                  "-ac", "1", str(out)])
    dur = media.duration(out)
    n = len(text)
    span = max(0.1, dur - 0.22)
    return out, {"characters": list(text),
                 "character_start_times_seconds": [0.12 + span * k / n for k in range(n)],
                 "character_end_times_seconds": [0.12 + span * (k + 1) / n for k in range(n)]}


def moving_clip(out: Path, colour: str, secs: float = 6, size: str = "720x1280") -> Path:
    media.ffmpeg(["-f", "lavfi", "-i", f"color=c={colour}:s={size}:r=30:d={secs}", "-vf",
                  "drawbox=x='200+160*sin(2*PI*t/3)':y='500+80*sin(2*PI*t/2)':w=220:h=220:color=white@0.25:t=fill,"
                  "noise=alls=5:allf=t,format=yuv420p", "-c:v", "libx264", "-preset", "ultrafast", str(out)])
    return out


LINES = [(1, "chang", "Chair against the wall. Arms crossed."),
         (2, "sun", "Breathe out as you stand."),
         (3, "chang", "Comment STRONG for the plan.")]


@pytest.fixture(scope="session")
def synth(tmp_path_factory):
    """Synthetic raw assets: per-line TTS with alignment, moving clips, PiP clip, music pad."""
    d = config.OUTPUT_DIR.parent / "assets"      # inside LOCAL_MEDIA_ROOTS (AUDIT H9 fetch policy)
    d.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, spk, text in LINES:
        p, al = tts(text, "kal" if spk == "chang" else "slt", d / f"line{i}.wav")
        lines.append({"i": i, "speaker": spk, "url": str(p), "text": text, "alignment": al})
    music = d / "music.wav"
    media.ffmpeg(["-f", "lavfi", "-i", "aevalsrc='0.2*sin(2*PI*220*t)+0.1*sin(2*PI*330*t)':s=48000:d=20", "-ac", "2", str(music)])
    pip = d / "pip.mp4"
    media.ffmpeg(["-f", "lavfi", "-i", "testsrc2=s=320x320:r=30", "-t", "3", "-c:v", "libx264", "-preset", "ultrafast",
                  "-pix_fmt", "yuv420p", str(pip)])
    return {"dir": d, "lines": lines, "music": music, "pip": pip,
            "clip_a": moving_clip(d / "a.mp4", "0x7A3E1D"), "clip_b": moving_clip(d / "b.mp4", "0x1F4E5F")}


def build_manifest(synth: dict, stitched: dict, **over) -> dict:
    lt = {l["i"]: l for l in stitched["lines"]}
    b2, b3 = lt[2]["start_s"], lt[3]["start_s"]
    timeline = [
        {"n": 1, "route": "lipsync_talk", "start_s": 0, "duration_s": b2, "src": str(synth["clip_a"]), "layout": "full",
         "camera": "handheld_micro"},
        {"n": 2, "route": "lipsync_talk", "start_s": b2, "duration_s": b3 - b2, "src": str(synth["clip_b"]), "layout": "full"},
        {"n": 3, "route": "graphic", "start_s": b2 + 0.2, "duration_s": 1.5, "src": {"url": str(synth["pip"])}, "layout": "pip_top"},
        {"n": 4, "route": "graphic", "start_s": b3, "duration_s": 9.2 - b3,
         "src": {"graphic": {"type": "number", "text": "8-minute plan"}}, "layout": "full", "camera": "slow_push"},
    ]
    m = {"brief_id": "test", "page_slug": "changyin", "locale": "en-US", "timeline": timeline,
         "voice_track": stitched["track_url"], "words": stitched["words"],
         "captions": {"size_px": 60, "fill": "#FFFFFF", "pill": "#111111", "highlight": "#FFD84D",
                      "safe_bottom_pct": 22, "safe_top_pct": 12, "max_words_per_chunk": 4},
         "on_screen": [{"text": "CHAIR TEST", "start_s": 0, "end_s": 2.0, "style": "hook"}],
         "study_cards": [{"title": "Chair stand: a screening test", "evidence_id": "E11", "start_s": 0.5, "end_s": 2.5}],
         "music": {"url": str(synth["music"]), "gain_db": -20}, "c2pa": {"sign": True},
         "qa": {"export_frames": 6, "phash": True, "chromaprint": True},
         # the flite test voice runs ~3.2 words/s (sped up to keep the suite fast); production voices come from
         # assemble.voice.tts_request (speed cap + sentence pauses) and are enforced. Unit tests cover enforce mode.
         "accessibility": {"mode": "warn"}}
    m.update(over)
    return m


@pytest.fixture(scope="session")
def stitched(synth):
    from assemble import voice
    return voice.stitch({"brief_id": "test", "gap_ms": 150, "lines": synth["lines"],
                         "shots": [{"n": 1, "route": "lipsync_talk", "speaker": "chang", "voice_lines": [1]},
                                   {"n": 2, "route": "lipsync_talk", "speaker": "both", "voice_lines": [2, 3]}]})


@pytest.fixture(scope="session")
def master(synth, stitched):
    from assemble import assembler
    res = assembler.assemble(build_manifest(synth, stitched))
    return res


@pytest.fixture(scope="session")
def data_scripts():
    return json.loads((config.SPEC_DIR / "data" / "content" / "scripts.json").read_text())


@pytest.fixture
def judge_pass(monkeypatch):
    """Stub a passing LLM judge (layer 2) for tests that exercise the happy path."""
    from compliance import judge as J
    calls = []

    def fake(subject, regex_hits, **kw):
        calls.append(subject)
        return {"status": "ok", "verdict": "pass", "confidence": 0.95, "model": "stub"}
    monkeypatch.setattr(J, "judge", fake)
    return calls
