"""End-to-end sample: synthetic assets -> /voice/stitch -> /assemble -> /qa -> fingerprints.

Synthetic stand-ins: colour cards (for keyframes / lip-sync shots), an animated gradient clip (gen_scene),
testsrc2 (PiP inset), flite TTS voices through ffmpeg (Chang = 'kal', Sun = 'slt') with an ElevenLabs-style
character alignment, and a generated chord pad as the music bed.

Run: python -m tools.make_sample   (writes workers/out/sample/)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from assemble import assembler, voice
from assemble.graphics import colour_card
from common import config, media
from compliance import scanner
from qa import qa as QA

LINES = [
    (1, "chang", "Sit down. Stand up. No hands. How many in thirty seconds?"),
    (2, "chang", "Chair against the wall. Arms crossed. Feet flat."),
    (3, "chang", "Go. All the way up, all the way down. Breathe out as you stand."),
    (4, "chang", "Men seventy to seventy-four, under twelve is below average. Women, under ten."),
    (5, "sun", "He does twenty-two. Show-off. Your number is the one that matters."),
    (6, "chang", "Need your hands? Use them. Start today anyway. Comment STRONG for the chair builder."),
]
SCRIPT = {
    "title_internal": "sample: 30-second chair stand", "format": "R1_talk_prop", "pillar": "P01", "speaker_mode": "CHANG",
    "has_movement": True, "movement_tags": ["sit_to_stand"], "evidence": ["E11"],
    "safety_cue": "Chair against the wall. Breathe out as you stand. Caption add-on stop rule.",
    "hook": {"spoken": LINES[0][2], "on_screen": "30-SECOND CHAIR TEST"},
    "lines": [{"i": i, "speaker": s, "text": t, "on_screen": o} for (i, s, t), o in zip(
        LINES, ["", "Chair AGAINST the wall", "Breathe out as you stand", "", "", "Comment STRONG"])],
    "movement": {"present": True, "name": "chair stand", "regression": "hands on thighs; higher seat"},
    "cta": {"keyword": "STRONG", "deliverable": "8-Minute Chair Builder"},
}
VOICES = {"chang": "kal", "sun": "slt"}


def tts(text: str, voice_name: str, out: Path) -> tuple[Path, dict]:
    tf = out.with_suffix(".txt")
    tf.write_text(text)
    media.ffmpeg(["-f", "lavfi", "-i", f"flite=textfile={tf}:voice={voice_name}", "-af", "atempo=1.12,aresample=48000",
                  "-ac", "1", str(out)])
    dur = media.duration(out)
    # ElevenLabs-style character alignment (proportional; real runs get true timings from the API)
    lead, tail = 0.12, 0.10
    span = max(0.1, dur - lead - tail)
    n = len(text)
    starts = [round(lead + span * k / n, 4) for k in range(n)]
    ends = [round(lead + span * (k + 1) / n, 4) for k in range(n)]
    return out, {"characters": list(text), "character_start_times_seconds": starts, "character_end_times_seconds": ends}


def main(outdir: Path | None = None) -> dict:
    out = Path(outdir or config.OUTPUT_DIR / "sample")
    assets = out / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    # 1) voice lines -> stitch
    lines = []
    for i, spk, text in LINES:
        p, al = tts(text, VOICES[spk], assets / f"line_{i:02d}.wav")
        lines.append({"i": i, "speaker": spk, "url": str(p), "text": text, "alignment": al})
    shots_plan = [{"n": 1, "route": "lipsync_talk", "speaker": "chang", "voice_lines": [1]},
                  {"n": 6, "route": "lipsync_talk", "speaker": "sun", "voice_lines": [5]}]
    vs = voice.stitch({"brief_id": "sample", "gap_ms": 180, "lines": lines, "shots": shots_plan}, out / "work")
    lt = {l["i"]: l for l in vs["lines"]}

    # 2) synthetic media
    garage = colour_card("#7A3E1D", "GARAGE · CHANG", assets / "card_garage.png")
    wall = colour_card("#1F4E5F", "CHAIR · WALL", assets / "card_wall.png")
    kitchen = colour_card("#2E6B3A", "KITCHEN · SUN", assets / "card_kitchen.png")
    # stand-ins for generated / lip-synced / library video: the card with a moving highlight + light sensor grain
    def moving(card: Path, name: str, secs: float = 8.0) -> Path:
        dst = assets / f"{name}.mp4"
        media.ffmpeg(["-loop", "1", "-framerate", "30", "-t", f"{secs}", "-i", str(card), "-vf",
                      "scale=720:1280,drawbox=x='260+180*sin(2*PI*t/4)':y='520+60*sin(2*PI*t/3)':w=200:h=200:"
                      "color=white@0.18:t=fill,noise=alls=5:allf=t,format=yuv420p",
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dst)])
        return dst
    garage, wall, kitchen = moving(garage, "talk_chang"), moving(wall, "broll_wall"), moving(kitchen, "talk_sun")
    gen = assets / "gen_scene.mp4"
    media.ffmpeg(["-f", "lavfi", "-i", "gradients=s=720x1280:r=30:speed=0.03:c0=0x8a3b12:c1=0x1f4e5f:c2=0xe0b04a:n=3",
                  "-t", "6", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(gen)])
    pip = assets / "pip.mp4"
    media.ffmpeg(["-f", "lavfi", "-i", "testsrc2=s=480x480:r=30", "-t", "4", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(pip)])
    music = assets / "music_pad.wav"
    media.ffmpeg(["-f", "lavfi", "-i",
                  "aevalsrc='0.2*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.15*sin(2*PI*277.18*t)+0.12*sin(2*PI*329.63*t)"
                  "+0.05*sin(2*PI*440*t)':s=48000:d=60", "-ac", "2", str(music)])

    # 3) timeline (shot planner shape) + manifest (n8n 'Build Assembly Manifest' shape + optional extras)
    b2, b4, b5, b6 = lt[2]["start_s"], lt[4]["start_s"], lt[5]["start_s"], lt[6]["start_s"]
    timeline = [
        {"n": 1, "route": "lipsync_talk", "start_s": 0.0, "duration_s": b2, "src": str(garage), "layout": "full", "camera": "handheld_micro"},
        {"n": 2, "route": "gen_scene", "start_s": b2, "duration_s": b4 - b2, "src": str(gen), "layout": "full", "camera": "static"},
        {"n": 3, "route": "library_broll", "start_s": b4, "duration_s": b5 - b4, "src": str(wall), "layout": "full", "camera": "slow_push"},
        {"n": 4, "route": "graphic", "start_s": b4 + 0.3, "duration_s": 3.0, "src": {"url": str(pip)}, "layout": "pip_top"},
        {"n": 5, "route": "lipsync_talk", "start_s": b5, "duration_s": b6 - b5, "src": str(kitchen), "layout": "full", "camera": "slow_push"},
        {"n": 6, "route": "graphic", "start_s": b6, "duration_s": vs["duration_s"] - b6 + 0.4,
         "src": {"graphic": {"type": "number", "text": "8-minute chair builder"}}, "layout": "full", "camera": "slow_push"},
    ]
    on_screen = [{"text": SCRIPT["hook"]["on_screen"], "start_s": 0, "end_s": 2.4, "style": "hook"}]
    for ln in SCRIPT["lines"]:
        if ln["on_screen"] and ln["i"] in lt:
            on_screen.append({"text": ln["on_screen"], "start_s": lt[ln["i"]]["start_s"], "end_s": lt[ln["i"]]["end_s"], "style": "emphasis"})
    manifest = {
        "brief_id": "sample", "script_id": "sample", "page_id": None, "page_slug": "changyin", "locale": "en-US",
        "output": {"width": 1080, "height": 1920, "fps": 30, "codec": "h264", "profile": "high", "crf": 18,
                   "audio": {"codec": "aac", "sample_rate": 48000, "lufs": -14, "true_peak_db": -1}},
        "timeline": timeline, "voice_track": vs["track_url"], "words": vs["words"],
        "captions": {"font": "Figtree", "weight": 800, "size_px": 60, "fill": "#FFFFFF", "pill": "#111111",
                     "highlight": "#FFD84D", "position": "lower_center", "safe_bottom_pct": 22, "safe_top_pct": 12,
                     "max_words_per_chunk": 4},
        "on_screen": on_screen,
        "study_cards": [{"title": "Chair stand, men 70–74: under 12 is below average", "evidence_id": "E11",
                         "start_s": b4 + 0.2, "end_s": b4 + 2.4}],
        "music": {"mood": "warm_acoustic", "url": str(music), "gain_db": -20, "duck_under_voice_db": -8},
        "c2pa": {"sign": True}, "qa": {"export_frames": 12, "phash": True, "chromaprint": True},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    asm = assembler.assemble(manifest, out / "work")

    # 4) QA + compliance pass 2 on what was burned in
    qa = QA.run({"video_url": asm["master_url"], "asset_id": asm["asset_id"], "reference_urls": [],
                 "expected_on_screen": asm["expected_on_screen"], "script_text": asm["transcript"], "frames": 12,
                 "checks": QA.ALL_CHECKS,
                 "shot_map": [{"n": t["n"], "route": t["route"], "start_s": t["start_s"], "duration_s": t["duration_s"]}
                              for t in timeline]}, out / "work")
    comp1 = scanner.scan(SCRIPT)
    comp2 = scanner.scan(SCRIPT, pass_no=2, transcript=asm["transcript"], burned_in_text=asm["burned_in_text"])

    # 5) frames to eyeball: hook, caption highlight, PiP + study card, Sun shot, CTA card
    frames_dir = out / "frames"
    frames_dir.mkdir(exist_ok=True)
    looks = {"hook_1.0s": 1.0, "emphasis_line2": lt[2]["start_s"] + 0.8, "study_card_pip": b4 + 1.2,
             "sun_shot": b5 + 1.0, "cta_card": b6 + 1.5}
    for name, t in looks.items():
        media.extract_frame(Path(asm["local_path"]), t, frames_dir / f"{name}.png")
    report = {"master": asm["local_path"], "clean": asm["clean_url"], "duration_s": asm["duration_s"],
              "c2pa": asm["c2pa"], "loudness": asm["loudness"], "warnings": asm["warnings"],
              "phash_seconds": len(asm["phash_seq"]), "audio_fp_method": (asm["audio_fp"] or "").split(":")[0],
              "qa": {k: qa[k] for k in ("decision", "reasons", "route", "route_label", "checks", "skipped")},
              "qa_metrics": {k: v for k, v in qa["metrics"].items() if k != "ocr_samples"},
              "ocr_samples": qa["metrics"].get("ocr_samples", [])[:8],
              "compliance_pass1": comp1["verdict"], "compliance_pass2": comp2["verdict"],
              "compliance_pass2_missing": comp2["required_missing"], "frames": sorted(str(p) for p in frames_dir.glob("*.png")),
              "render_s": asm["render_s"]}
    (out / "sample_report.json").write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    r = main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(json.dumps({k: r[k] for k in ("master", "duration_s", "qa", "compliance_pass1", "compliance_pass2")}, indent=2))
