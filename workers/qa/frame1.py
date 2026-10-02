"""Frame-1 OCR check per variant (ENGINE_SAVAGE20 §B(b) item 4, SL-08.1). The last automated check before a person
uploads a file: on the first frame a viewer sees, the platform hook must be
  - present (OCR finds real words in the hook zone),
  - short (<= 7 words, VIRALITY_SYSTEM §3 R1; the AI tag and the caption pill are outside the zone), and
  - legible (WCAG contrast ratio >= 4.5 between the text pixels and their own background, per word box).
The hook zone is the band the variant renderer burns into: from the safe-zone top + 80 px (below the AI tag) to
200 px above the safe-zone bottom (above the caption pill). Needs tesseract (and ffmpeg for a video path).
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from assemble.layout import H, W, safe_zone
from assemble.virality_gate import HOOK_MAX_WORDS
from qa import ocr

MIN_CONTRAST = 4.5
MIN_CONF = 55
PLATFORM_ZONE = {"ig": "instagram", "fb": "facebook", "tt": "tiktok", "yt": "youtube", "th": "threads", "x": "x"}


def _lum(rgb: np.ndarray) -> float:
    c = rgb.astype(float) / 255.0
    c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return float(0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2])


def contrast_ratio(a: np.ndarray, b: np.ndarray) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


def box_contrast(rgb: np.ndarray) -> float:
    """Contrast of a word box: split its pixels at the luma midpoint (Otsu-lite) and compare the two medians."""
    px = rgb.reshape(-1, 3).astype(float)
    y = px @ np.array([0.299, 0.587, 0.114])
    t = (np.percentile(y, 5) + np.percentile(y, 95)) / 2
    dark, light = px[y < t], px[y >= t]
    if len(dark) < 4 or len(light) < 4:
        return 1.0
    return contrast_ratio(np.median(dark, axis=0), np.median(light, axis=0))


def _tsv(img: Image.Image) -> list[dict]:
    with tempfile.NamedTemporaryFile(suffix=".png") as tf:
        img.save(tf.name)
        p = subprocess.run(["tesseract", tf.name, "stdout", "--psm", "11", "-l", "eng", "tsv"], capture_output=True,
                           text=True, timeout=60)
    rows = []
    lines = p.stdout.splitlines()
    for line in lines[1:]:
        f = line.split("\t")
        if len(f) == 12 and f[11].strip():
            try:
                conf = float(f[10])
            except ValueError:
                continue
            rows.append({"text": f[11].strip(), "conf": conf, "x": int(f[6]), "y": int(f[7]), "w": int(f[8]), "h": int(f[9])})
    return rows


def hook_zone(platform: str) -> tuple[int, int]:
    z = safe_zone(PLATFORM_ZONE.get(platform, platform))
    return z.top + 80, z.bottom - 200


def check_frame1(src: str | Path | Image.Image, platform: str = "ig", expected: str | None = None,
                 max_words: int = HOOK_MAX_WORDS, min_contrast: float = MIN_CONTRAST) -> dict:
    """-> {ok, words, text, contrast_min, problems}. `expected` (the variant's on_screen_hook) adds a match check."""
    if not ocr.available():
        return {"ok": None, "status": "skipped", "problems": ["tesseract not installed"]}
    if isinstance(src, Image.Image):
        frame = src
    else:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "f1.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-frames:v", "1", str(out)], check=True,
                           capture_output=True, timeout=120)
            frame = Image.open(out).convert("RGB")
            frame.load()
    rgb = np.asarray(frame.convert("RGB").resize((W, H)))
    y0, y1 = hook_zone(platform)
    band = rgb[y0:y1]
    words = []
    luma = band.astype(float) @ np.array([0.299, 0.587, 0.114])
    sc = 0.5                                               # 60-110 px burned-in type -> tesseract's sweet spot
    for mask in (luma > 170, luma < 70):                   # light text, then dark text -> black on white
        bw = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8))
        bw = bw.resize((int(bw.width * sc), int(bw.height * sc)))
        found = [{**w, "x": int(w["x"] / sc), "y": int(w["y"] / sc), "w": int(w["w"] / sc), "h": int(w["h"] / sc)}
                 for w in _tsv(bw) if w["conf"] >= MIN_CONF and re.search(r"[A-Za-z0-9]{2,}|^[AIai0-9]$", w["text"])]
        if len(found) > len(words):
            words = found
    problems = []
    text = " ".join(w["text"] for w in sorted(words, key=lambda w: (w["y"] // 40, w["x"])))
    if not words:
        problems.append("no readable hook text on frame 1")
    n = len(words)
    if n > max_words:
        problems.append(f"frame-1 hook is {n} words (max {max_words})")
    contrasts = [box_contrast(band[w["y"]:w["y"] + w["h"], w["x"]:w["x"] + w["w"]]) for w in words if w["w"] > 2 and w["h"] > 2]
    cmin = min(contrasts) if contrasts else None
    if cmin is not None and cmin < min_contrast:
        problems.append(f"frame-1 text contrast {cmin} < {min_contrast}")
    if expected:
        want = set(re.findall(r"[a-z0-9]{3,}", expected.lower()))
        got = set(re.findall(r"[a-z0-9]{3,}", text.lower()))
        if want and len(want & got) / len(want) < 0.5:
            problems.append(f"frame-1 text '{text[:60]}' does not match the planned hook '{expected[:60]}'")
    return {"ok": not problems, "words": n, "text": text, "contrast_min": cmin, "problems": problems}
