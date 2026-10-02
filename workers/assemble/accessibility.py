"""Accessibility defaults for a 55+ audience (ENGINE_100X §4.2, §4.4, holes #3; [S40][S41][S43]).

check(manifest, words, total) -> {"errors", "warnings", "speech_rate_wps", "speech_spans"}; the assembler raises on
errors unless manifest.accessibility.mode == "warn" (legacy jobs only).
  * caption size: captions >= 56 px (CaptionStyle clamps; a smaller request is reported), hook text >= 72 px cap
    height (overlay.hook_min_size derives the font size from the real cap height)
  * contrast: caption fill / highlight on the pill >= 7:1 and never gray (layout.validate_text_colours)
  * no music under speech: the mix mutes the music bed in every speech span (speech_spans); a manifest that asks
    for music under speech is refused
  * speech rate: words / (speech seconds - pauses >= 250 ms) <= 2.5 words/s (POSTDB mega-hits ran 2.3 w/s)
  * pauses between sentences: >= 250 ms after each sentence end (warning; the TTS request inserts 300 ms)
"""
from __future__ import annotations

import re

from assemble import captions as C
from assemble.layout import validate_text_colours

MAX_WPS = 2.5
PAUSE_S = 0.25
CAPTION_MIN_PX = 56
SPAN_MERGE_GAP_S = 0.7
SPAN_PAD_S = 0.15


def speech_spans(words: list[C.Word], total: float | None = None) -> list[tuple[float, float]]:
    """Merged [start, end] windows where someone is speaking (padded), for gating the music bed."""
    spans: list[list[float]] = []
    for w in sorted(words, key=lambda w: w.start):
        a, b = max(0.0, w.start - SPAN_PAD_S), w.end + SPAN_PAD_S
        if spans and a - spans[-1][1] <= SPAN_MERGE_GAP_S:
            spans[-1][1] = max(spans[-1][1], b)
        else:
            spans.append([a, b])
    if total:
        spans = [[a, min(b, total)] for a, b in spans if a < total]
    return [(round(a, 3), round(b, 3)) for a, b in spans]


def speech_rate(words: list[C.Word]) -> float | None:
    ws = sorted(words, key=lambda w: w.start)
    if len(ws) < 2:
        return None
    span = ws[-1].end - ws[0].start
    pauses = sum(max(0.0, b.start - a.end) for a, b in zip(ws, ws[1:]) if b.start - a.end >= PAUSE_S)
    talk = span - pauses
    return round(len(ws) / talk, 3) if talk > 0 else None


def check(manifest: dict, words: list[C.Word], total: float | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    cap = manifest.get("captions") or {}
    if cap.get("size_px") is not None and float(cap["size_px"]) < CAPTION_MIN_PX:
        warnings.append(f"caption size {cap['size_px']} px raised to {CAPTION_MIN_PX} px (55+ readability)")
    try:
        validate_text_colours(cap.get("fill", "#FFFFFF"), cap.get("pill", "#111111"), "caption fill")
        validate_text_colours(cap.get("highlight", "#FFD84D"), cap.get("pill", "#111111"), "caption highlight")
    except ValueError as e:
        errors.append(str(e))
    mus = manifest.get("music") or {}
    if mus.get("under_speech"):
        errors.append("music under speech is not allowed: the bed plays only between spoken lines")
    rate = speech_rate(words)
    if rate is not None and rate > MAX_WPS:
        errors.append(f"speech rate {rate:.2f} words/s > {MAX_WPS} (55+ pace: re-voice with the capped TTS speed)")
    ws = sorted(words, key=lambda w: w.start)
    short = sum(1 for a, b in zip(ws, ws[1:]) if re.search(r"[.!?]$", a.text) and b.start - a.end < PAUSE_S)
    if short:
        warnings.append(f"{short} sentence end(s) followed by < {int(PAUSE_S * 1000)} ms pause")
    return {"errors": errors, "warnings": warnings, "speech_rate_wps": rate, "speech_spans": speech_spans(words, total),
            "mode": (manifest.get("accessibility") or {}).get("mode", "enforce")}
