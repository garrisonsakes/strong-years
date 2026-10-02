"""Caption OCR (tesseract) vs the script: char error rate + number check; AI-tag presence check."""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

from assemble.layout import H, W, safe_zone

NUM_WORDS = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7",
             "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12"}


def available() -> bool:
    return shutil.which("tesseract") is not None


def tesseract(img: Image.Image, psm: int = 6) -> str:
    with tempfile.NamedTemporaryFile(suffix=".png") as tf:
        img.save(tf.name)
        p = subprocess.run(["tesseract", tf.name, "stdout", "--psm", str(psm), "-l", "eng"], capture_output=True,
                           text=True, timeout=60)
    return p.stdout.strip()


def _pill_crop(band: np.ndarray) -> tuple[int, int, int, int] | None:
    """Bounding box of the dark caption pill inside the band (luma < 45 on enough pixels)."""
    dark = band < 45
    rows = np.where(dark.mean(axis=1) > 0.25)[0]
    cols = np.where(dark.mean(axis=0) > 0.25)[0]
    if rows.size < 20 or cols.size < 60:
        return None
    return int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1


def caption_text(frame: Image.Image, platform: str = "master") -> str | None:
    z = safe_zone(platform)
    # captions are bottom-anchored at the safe-zone line and at most 2 lines (~200 px incl. the pill padding)
    y0, y1 = max(0, z.bottom - 200), min(H, z.bottom + 6)
    g = np.asarray(frame.convert("L").resize((W, H)))[y0:y1]
    box = _pill_crop(g)
    if box is None:
        return None
    x0, a, x1, b = box
    x0, x1, a, b = x0 + 22, x1 - 22, a + 4, b - 4       # stay inside the rounded pill corners
    if x1 - x0 < 40 or b - a < 20:
        return None
    rgb = np.asarray(frame.convert("RGB").resize((W, H)))[y0:y1][a:b, x0:x1].astype(np.int16)
    # caption text is white or yellow on a near-black pill: keep bright pixels, render black-on-white for tesseract
    bright = (rgb.max(axis=2) > 150)
    mask = np.where(bright, 0, 255).astype(np.uint8)
    img = Image.fromarray(mask).resize((mask.shape[1] * 2 // 3 or 1, mask.shape[0] * 2 // 3 or 1))
    txt = tesseract(img, psm=6)
    return re.sub(r"\s+", " ", txt).strip() or None


def ai_tag_text(frame: Image.Image, platform: str = "master") -> str:
    z = safe_zone(platform)
    crop = frame.convert("RGB").resize((W, H)).crop((20, z.top - 10, 560, z.top + 90))
    rgb = np.asarray(crop).astype(np.int16)
    mask = np.where(rgb.min(axis=2) > 200, 0, 255).astype(np.uint8)
    return tesseract(Image.fromarray(mask), psm=7)


def ai_tag_present(text: str, expected: str = "AI character") -> bool:
    t = re.sub(r"[^a-z]", "", text.lower())
    e = re.sub(r"[^a-z]", "", expected.lower())
    return e in t or (e[:2] in t and "charact" in t) or _lev(t, e) <= 2


def _norm(t: str) -> str:
    t = t.lower().replace("’", "'").replace("‘", "'")
    return " ".join(re.sub(r"[^a-z0-9' ]+", " ", t).split())


def _lev(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def denoise(ocr: str, reference: str) -> str:
    """Drop tesseract edge noise: tokens with no letters/digits, and stray 1–2 char tokens not in the reference."""
    vocab = set(_norm(reference).split())
    keep = []
    for tok in ocr.split():
        n = _norm(tok)
        if not n:
            continue
        if len(n) <= 2 and n not in vocab and not n.isdigit():
            continue
        keep.append(tok)
    return " ".join(keep)


def best_window_cer(ocr: str, script: str) -> tuple[float, str]:
    """Min char error rate of `ocr` against any window of the script with a similar word count."""
    o = _norm(ocr)
    sw = _norm(script).split()
    if not o or not sw:
        return 1.0, ""
    n = len(o.split())
    best, best_s = 1.0, ""
    for size in {max(1, n - 1), n, n + 1}:
        for i in range(0, max(1, len(sw) - size + 1)):
            cand = " ".join(sw[i:i + size])
            cer = _lev(o, cand) / max(len(cand), 1)
            if cer < best:
                best, best_s = cer, cand
    return round(best, 4), best_s


def numbers_in(t: str) -> set[str]:
    toks = _norm(t).split()
    out = set(re.findall(r"\d+", t))
    out |= {NUM_WORDS[x] for x in toks if x in NUM_WORDS}
    return out


def caption_check(frames: list[tuple[float, Image.Image]], script_text: str, expected: list[str] | None = None,
                  platform: str = "master") -> dict:
    """OCR sampled frames; CER vs script (+ expected on-screen strings); flag digits not present in the script."""
    reference = script_text + " " + " ".join(expected or [])
    ref_nums = numbers_in(reference)
    rows, total_err, total_len, mismatch = [], 0.0, 0, False
    for t, im in frames:
        txt = caption_text(im, platform)
        txt = denoise(txt, reference) if txt else txt
        if not txt or len(_norm(txt)) < 2:
            continue
        cer, match = best_window_cer(txt, reference)
        bad_nums = sorted(numbers_in(txt) - ref_nums)
        mismatch |= bool(bad_nums)
        n = max(len(match), 1)
        total_err += cer * n
        total_len += n
        rows.append({"t": t, "ocr": txt, "match": match, "cer": cer, "bad_numbers": bad_nums})
    return {"caption_cer": round(total_err / total_len, 4) if total_len else None,
            "caption_number_mismatch": mismatch, "ocr_frames": len(rows), "ocr_samples": rows[:40]}


# SL-08.1 frame-1 hook check (present, <= 7 words, contrast), see qa/frame1.py
def check_frame1(src, platform: str = "ig", expected: str | None = None, **kw) -> dict:
    from qa.frame1 import check_frame1 as _f  # noqa: PLC0415 (frame1 imports this module)
    return _f(src, platform, expected, **kw)
