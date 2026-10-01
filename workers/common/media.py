"""Thin, testable wrappers around ffmpeg / ffprobe."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


class MediaError(RuntimeError):
    pass


def have(binary: str) -> bool:
    return shutil.which(binary) is not None


def run(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    """Run a command; raise MediaError with the stderr tail on failure."""
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        tail = "\n".join((p.stderr or "").strip().splitlines()[-25:])
        raise MediaError(f"{cmd[0]} failed ({p.returncode}): {tail}")
    return p


def ffmpeg(args: Iterable[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *args], timeout=timeout)


def ffprobe(path: str | Path) -> dict:
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)], timeout=120)
    return json.loads(p.stdout)


def duration(path: str | Path) -> float:
    info = ffprobe(path)
    d = info.get("format", {}).get("duration")
    if d is None:
        for s in info.get("streams", []):
            if s.get("duration"):
                return float(s["duration"])
        return 0.0
    return float(d)


def has_audio(path: str | Path) -> bool:
    return any(s.get("codec_type") == "audio" for s in ffprobe(path).get("streams", []))


def is_image(path: str | Path) -> bool:
    return Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def parse_rate(r: str | None) -> float:
    if not r or r in ("0/0",):
        return 0.0
    if "/" in r:
        a, b = r.split("/")
        return float(a) / float(b) if float(b) else 0.0
    return float(r)


def loudness(path: str | Path) -> dict:
    """EBU R128 integrated loudness, LRA and true peak via ffmpeg ebur128."""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vn", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True, timeout=600)
    err = p.stderr
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else ""
    def grab(pattern):
        m = re.search(pattern, summary)
        return float(m.group(1)) if m else None
    i = grab(r"I:\s+(-?[\d.]+|-inf) LUFS") if "I:" in summary else None
    return {
        "lufs_integrated": i,
        "lra": grab(r"LRA:\s+(-?[\d.]+) LU"),
        "true_peak_db": grab(r"Peak:\s+(-?[\d.]+) dBFS"),
    }


def extract_frame(video: str | Path, t: float, out: str | Path, width: int | None = None) -> Path:
    vf = ["-vf", f"scale={width}:-2"] if width else []
    ffmpeg(["-ss", f"{max(t, 0):.3f}", "-i", str(video), "-frames:v", "1", *vf, "-q:v", "2", str(out)])
    return Path(out)
