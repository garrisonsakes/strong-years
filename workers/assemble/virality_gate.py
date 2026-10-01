"""Render-time virality preflight (VIRALITY_SYSTEM.md §3). Pure: no ffmpeg, no I/O.

Every master must carry, before a frame is encoded:
  R1 frame-1 hook text: an on_screen item with style "hook" that starts at t <= 0.05 s, <= 7 words, high contrast
     (the overlay renderer already refuses gray / < 7:1 text; we check the words and the timing here).
  R2 caption burn-in: word timings present whenever there is a voice track (sound-off viewing).
  R3 pattern interrupt by second 3: a new visual event (shot cut, PiP, study card, non-hook on-screen text)
     starting in (0.4 s, 3.0 s].
  R4 loop-friendly ending: no sign-off in the last spoken line and <= 0.8 s of dead air after the last word.
  R5 9:16 safe areas: 1080x1920 output and caption safe-zone overrides no looser than the platform zone.
  R6 cover-frame rule (checked in variants.cover via cover_text_ok): cover text <= 6 words, taken from the hook.

mode: manifest["virality_gate"] = "enforce" (default) raises in the assembler; "warn" reports only (legacy jobs).
"""
from __future__ import annotations

import re

from assemble.layout import H, SAFE_ZONES, W

HOOK_MAX_WORDS = 7
HOOK_START_MAX_S = 0.05
INTERRUPT_MIN_S, INTERRUPT_BY_S = 0.4, 3.0
DEAD_AIR_MAX_S = 0.8
COVER_MAX_WORDS = 6
SIGNOFF_RX = re.compile(r"\b(bye|goodbye|see you( next time| tomorrow)?|thanks for watching|that'?s (it|all)( for today)?|"
                        r"follow for more|until next time|take care)\W*$", re.I)


def _words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", (text or "").strip()) if re.search(r"\w", w)]


def cover_text_ok(text: str | None) -> list[str]:
    if not text:
        return ["R6 cover: cover_text missing (the cover must restate the frame-1 hook)"]
    n = len(_words(text))
    return [] if n <= COVER_MAX_WORDS else [f"R6 cover: cover_text {n} words > {COVER_MAX_WORDS}"]


def check(manifest: dict, total: float, words: list | None = None) -> dict:
    errors: list[str] = []
    warns: list[str] = []
    texts = manifest.get("on_screen") or []
    hooks = [t for t in texts if t.get("style") == "hook"]
    first = min(hooks, key=lambda t: float(t.get("start_s", 0)), default=None)
    if first is None:
        errors.append("R1 frame-1 hook: no on_screen item with style 'hook'")
    else:
        if float(first.get("start_s", 0)) > HOOK_START_MAX_S:
            errors.append(f"R1 frame-1 hook starts at {float(first.get('start_s', 0)):.2f} s (must be on frame 1)")
        n = len(_words(first.get("text", "")))
        if n > HOOK_MAX_WORDS:
            errors.append(f"R1 frame-1 hook is {n} words (max {HOOK_MAX_WORDS})")
        if float(first.get("end_s", 0)) - float(first.get("start_s", 0)) < 1.0:
            warns.append("R1 frame-1 hook is on screen < 1.0 s")

    ws = words if words is not None else (manifest.get("words") or [])
    if manifest.get("voice_track") and not ws:
        errors.append("R2 captions: voice track has no word timings, captions would not burn in")

    events = []
    for s in manifest.get("timeline") or []:
        events.append(float(s.get("start_s", 0)))
    events += [float(t.get("start_s", 0)) for t in texts if t.get("style") != "hook"]
    events += [float(c.get("start_s", 0)) for c in manifest.get("study_cards") or []]
    events += [float(t) for t in manifest.get("pattern_interrupts_s") or []]   # explicit zoom/punch-in cues
    if not any(INTERRUPT_MIN_S < e <= INTERRUPT_BY_S for e in events):
        errors.append(f"R3 pattern interrupt: no new visual event in ({INTERRUPT_MIN_S}, {INTERRUPT_BY_S}] s")

    def _end(w):
        return float(w.end if hasattr(w, "end") else w.get("end_s", w.get("end", 0)))

    def _txt(w):
        return str(w.text if hasattr(w, "text") else w.get("word") or w.get("text") or "")
    if ws:
        tail_words = " ".join(_txt(w) for w in ws[-6:])
        if SIGNOFF_RX.search(tail_words):
            errors.append(f"R4 loop: sign-off at the end ('{tail_words[-40:]}') breaks the loop")
        dead = total - max(_end(w) for w in ws)
        if dead > DEAD_AIR_MAX_S:
            warns.append(f"R4 loop: {dead:.1f} s of dead air after the last word (max {DEAD_AIR_MAX_S})")

    out = manifest.get("output") or {}
    if (int(out.get("width", W)), int(out.get("height", H))) != (W, H):
        errors.append(f"R5 9:16: output {out.get('width')}x{out.get('height')} is not {W}x{H}")
    cap = manifest.get("captions") or {}
    pt, pb = (round(v * 100, 2) for v in SAFE_ZONES.get(manifest.get("platform", "master"), SAFE_ZONES["master"])[:2])
    if cap.get("safe_top_pct") is not None and float(cap["safe_top_pct"]) < pt:
        errors.append(f"R5 safe area: safe_top_pct {cap['safe_top_pct']} looser than {pt}")
    if cap.get("safe_bottom_pct") is not None and float(cap["safe_bottom_pct"]) < pb:
        errors.append(f"R5 safe area: safe_bottom_pct {cap['safe_bottom_pct']} looser than {pb}")

    if manifest.get("cover_text") is not None:
        errors += cover_text_ok(manifest.get("cover_text"))
    return {"errors": errors, "warnings": warns, "pass": not errors,
            "mode": manifest.get("virality_gate", "enforce"), "frame1_hook": (first or {}).get("text")}
