from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from assemble import assembler, c2pa_sign, variants, voice
from assemble import captions as C
from assemble.layout import H, W, contrast_ratio, safe_zone, validate_text_colours
from assemble.overlay import CaptionStyle, OverlayPlan, build_states, render_state
from common import media
from tests.conftest import build_manifest
from tests.conftest import AUTH


# ---------- captions / layout (pure) ----------
def _words(txt, step=0.3):
    return [C.Word(w, i * step, i * step + step * 0.9) for i, w in enumerate(txt.split())]


def test_chunking_limits_and_punctuation():
    ch = C.chunk_words(_words("Sit down. Stand up now please with your arms crossed tight"), max_words=4)
    assert all(len(c.words) <= 4 for c in ch)
    assert ch[0].text == "Sit down."            # sentence end breaks the chunk
    st = C.word_states(ch)
    assert all(b > a for a, b, _, _ in st)
    assert [s[3] for s in st[:2]] == [0, 1]      # word-by-word highlight index advances


def test_tags_stripped_from_words():
    ws = C.clean_words([{"word": "[warmly]", "start_s": 0, "end_s": 0.1}, {"word": "Hi", "start_s": 0.1, "end_s": 0.3}])
    assert [w.text for w in ws] == ["Hi"]


def test_high_contrast_rules():
    assert contrast_ratio("#FFFFFF", "#111111") > 15 and contrast_ratio("#FFD84D", "#111111") > 10
    with pytest.raises(ValueError):
        validate_text_colours("#888888", "#111111")          # gray text is refused (client rule)
    with pytest.raises(ValueError):
        CaptionStyle.from_manifest({"fill": "#9A9A9A"})
    assert CaptionStyle.from_manifest({"size_px": 40}).size_px == 52   # V-04 minimum


def test_safe_zones_respect_v04_and_platforms():
    for pl in ("master", "instagram", "tiktok", "youtube", "facebook"):
        z = safe_zone(pl)
        assert z.top >= 180 and H - z.bottom >= 250
    assert safe_zone("tiktok").right <= int(W * 0.86)


def test_overlay_state_pixels_inside_safe_zone():
    z = safe_zone("master")
    plan = OverlayPlan(duration=3.0, zone=z, style=CaptionStyle(), words=_words("Chair against the wall"),
                       texts=[{"text": "CHAIR TEST", "start_s": 0, "end_s": 1, "style": "hook"}])
    states = build_states(plan)
    assert states[0][0] == 0 and abs(states[-1][1] - 3.0) < 0.05
    img = render_state(plan, states[1][2])
    a = np.asarray(img)[..., 3]
    ys, xs = np.nonzero(a)
    assert ys.min() >= z.top and ys.max() <= z.bottom            # nothing in platform UI bands
    tag = np.asarray(img)[z.top:z.top + 70, 40:300]
    assert (tag[..., 3] > 0).mean() > 0.3 and (tag[..., :3].min(axis=2) > 240).any()   # white text on dark pill


# ---------- voice stitch ----------
def test_voice_stitch_words_lines_segments(stitched):
    assert stitched["duration_s"] > 3
    assert [l["i"] for l in stitched["lines"]] == [1, 2, 3]
    assert stitched["lines"][1]["start_s"] > stitched["lines"][0]["end_s"]         # gap inserted
    assert stitched["words"][0]["word"] == "Chair" and all(w["end_s"] > w["start_s"] for w in stitched["words"])
    seg = {s["shot_n"]: s for s in stitched["segments"]}
    assert set(seg) == {1, 2} and set(seg[2]["speakers"]) == {"chang", "sun"}
    assert media.duration(seg[2]["speakers"]["chang"].replace("file://", "")) == pytest.approx(
        media.duration(seg[2]["speakers"]["sun"].replace("file://", "")), abs=0.01)


def test_alignment_fallback_is_proportional():
    ws = voice.words_from_alignment(None, "one two three", 3.0)
    assert [w["word"] for w in ws] == ["one", "two", "three"] and ws[-1]["end_s"] <= 3.0


# ---------- assembler (end to end on the synthetic master) ----------
def test_master_spec_loudness_c2pa(master):
    p = Path(master["local_path"])
    info = media.ffprobe(p)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next(s for s in info["streams"] if s["codec_type"] == "audio")
    assert (v["width"], v["height"], v["codec_name"], v["profile"]) == (1080, 1920, "h264", "High")
    assert media.parse_rate(v["avg_frame_rate"]) == pytest.approx(30, abs=0.01)
    assert (a["codec_name"], int(a["sample_rate"])) == ("aac", 48000)
    assert master["duration_s"] == pytest.approx(9.2, abs=0.15)
    assert abs(master["loudness"]["lufs_integrated"] + 14) <= 1.0
    assert master["loudness"]["true_peak_db"] <= -1.0
    if c2pa_sign.backend() == "stub":
        pytest.skip("no C2PA backend installed")
    assert master["c2pa"]["present"] and master["c2pa"]["ai_generated"]


def test_master_outputs_for_downstream(master):
    assert master["asset_id"] and master["master_url"] and master["clean_url"]
    assert len(master["phash_seq"]) == pytest.approx(master["duration_s"], abs=1.5)
    assert master["audio_fp"].split(":")[0] in ("chromaprint", "spectral")
    assert len(master["frames"]) == 6
    assert "AI character" in master["burned_in_text"]
    assert master["transcript"].startswith("Chair against the wall.")


def test_master_frames_captions_and_tag(master, tmp_path):
    """Look at pixels: caption pill bottom-anchored in the safe zone, AI tag top-left, study card lower-left."""
    z = safe_zone("master")
    f = media.extract_frame(Path(master["local_path"]), 1.5, tmp_path / "f.png")
    im = np.asarray(Image.open(f).convert("RGB")).astype(int)
    band = im[z.bottom - 120:z.bottom - 10, 200:800]
    assert (band.max(axis=2) < 40).mean() > 0.3               # dark caption pill
    assert (band.min(axis=2) > 230).mean() > 0.02             # white caption text
    tag = im[z.top + 10:z.top + 50, 50:260]
    assert (tag.min(axis=2) > 230).mean() > 0.05              # white "AI character" text
    card = im[1000:1250, z.left + 30:z.left + 500]
    assert ((card[..., 0] > 235) & (card[..., 1] > 225)).mean() > 0.4   # cream study card (E11 at 0.5–2.5 s)


def test_ai_tag_is_mandatory(synth, stitched):
    with pytest.raises(assembler.AssemblyError):
        assembler.assemble(build_manifest(synth, stitched, ai_tag=""))


def test_timeline_planning_pip_and_gaps():
    base, pips, warns = assembler.plan_timeline(
        [{"n": 1, "start_s": 0.5, "duration_s": 2, "src": "a"}, {"n": 2, "start_s": 1, "duration_s": 1, "src": "p", "layout": "pip_top"},
         {"n": 3, "start_s": 2.5, "duration_s": 2, "src": "b", "layout": "split"}], 5.0)
    assert base[0]["_a"] == 0 and base[0]["_b"] == 2.5 and base[1]["_b"] == 5.0
    assert pips[0]["position"] == "top_right" and any("split" in w for w in warns)
    assert assembler.frame_times(30.0)[:1] == [0.5] and len(assembler.frame_times(30.0)) == 12


def test_variants_hook_trim_c2pa_cover(master):
    res = variants.render_variants({"master_url": master["master_url"], "video_id": "v1", "variants": [
        {"platform": "tiktok", "on_screen_hook": "Can you do this?", "cover_text": "YOUR NUMBER?", "max_s": 6,
         "safe_zone": {"right_pct": 14, "bottom_pct": 22}},
        {"platform": "threads", "render": False}]})
    assert res["source"] == "clean_mezzanine"
    tt, th = res["variants"]
    assert tt["rendered"] and tt["hook_burned"] and tt["trimmed"] and tt["duration_s"] <= 6.1
    assert Path(tt["cover_url"].replace("file://", "")).exists()
    if c2pa_sign.backend() != "stub":
        assert tt["c2pa"]["present"]
    assert th["rendered"] is False


def test_c2pa_roundtrip(tmp_path):
    if c2pa_sign.backend() == "stub":
        pytest.skip("TODO: install c2pa-python or c2patool")
    src = tmp_path / "s.mp4"
    media.ffmpeg(["-f", "lavfi", "-i", "testsrc2=s=320x240:d=1", "-c:v", "libx264", "-preset", "ultrafast", str(src)])
    assert c2pa_sign.read(src)["present"] is False
    info = c2pa_sign.sign(src, tmp_path / "o.mp4")
    assert info["signed"] and info["ai_generated"] and info["dev_cert"]


def test_render_api_stitch(synth):
    from app import app
    c = TestClient(app, headers=AUTH)
    r = c.post("/voice/stitch", json={"brief_id": "api", "lines": synth["lines"][:1], "shots": []})
    assert r.status_code == 200 and r.json()["words"]
    r = c.post("/assemble", json={"timeline": [], "voice_track": None})
    assert r.status_code == 422
