"""Deterministic signal checks: spec (ffprobe), loudness (EBU R128), black/freeze detection, duration bounds."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from common import media

SPEC = {"width": 1080, "height": 1920, "fps": 30.0, "vcodec": "h264", "profile": "High", "acodec": "aac",
        "sample_rate": 48000}
DURATION_BOUNDS = {"master": (8.0, 90.0), "instagram": (3.0, 180.0), "tiktok": (3.0, 600.0),
                   "youtube": (3.0, 180.0), "facebook": (3.0, 90.0), "x": (1.0, 140.0), "threads": (1.0, 300.0)}


def spec(path: str | Path) -> dict:
    info = media.ffprobe(path)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), {})
    m = {
        "width": v.get("width"), "height": v.get("height"),
        "fps": round(media.parse_rate(v.get("avg_frame_rate") or v.get("r_frame_rate")), 3),
        "vcodec": v.get("codec_name"), "profile": v.get("profile"), "pix_fmt": v.get("pix_fmt"),
        "acodec": a.get("codec_name"), "sample_rate": int(a["sample_rate"]) if a.get("sample_rate") else None,
        "duration_s": round(float(info.get("format", {}).get("duration", 0) or 0), 3),
    }
    problems = []
    for k in ("width", "height", "vcodec", "profile", "acodec", "sample_rate"):
        if m.get(k) != SPEC[k]:
            problems.append(f"{k}={m.get(k)} (want {SPEC[k]})")
    if abs((m["fps"] or 0) - SPEC["fps"]) > 0.05:
        problems.append(f"fps={m['fps']} (want 30)")
    m["spec_ok"] = not problems
    m["spec_problems"] = problems
    return m


def black_freeze(path: str | Path, pix_th: float = 0.10, black_min: float = 0.1, freeze_noise: str = "-60dB",
                 freeze_min: float = 0.25) -> dict:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-an", "-vf",
                        f"blackdetect=d={black_min}:pix_th={pix_th},freezedetect=n={freeze_noise}:d={freeze_min}",
                        "-f", "null", "-"], capture_output=True, text=True, timeout=900)
    err = p.stderr
    blacks = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]
    fstarts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", err)]
    fdurs = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", err)]
    fends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", err)]
    if len(fstarts) > len(fdurs):   # freeze running until the end of the file
        dur = media.duration(path)
        fdurs += [dur - s for s in fstarts[len(fdurs):]]
    return {
        "black_segments": [{"start": a, "end": b, "dur": round(b - a, 3)} for a, b in blacks],
        "freeze_segments": [{"start": s, "dur": round(d, 3)} for s, d in zip(fstarts, fdurs)],
        "black_max_s": round(max([b - a for a, b in blacks], default=0.0), 3),
        "freeze_max_s": round(max(fdurs, default=0.0), 3),
        "_freeze_end_count": len(fends),
    }


def loudness(path: str | Path) -> dict:
    m = media.loudness(path)
    if m["lufs_integrated"] is None:
        m["lufs_integrated"] = -70.0          # silent / no audio: ebur128 gating floor
    return m


def duration_check(dur: float, platform: str = "master", bounds: dict | None = None) -> dict:
    lo, hi = DURATION_BOUNDS.get(platform, DURATION_BOUNDS["master"])
    if bounds:
        lo, hi = float(bounds.get("min_s", lo)), float(bounds.get("max_s", hi))
    return {"duration_ok": lo <= dur <= hi, "duration_bounds": [lo, hi]}
