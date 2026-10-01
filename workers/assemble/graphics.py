"""Full-frame graphic shots (route 'graphic'): study card, number card, checklist, timer (static), title.
House design: our own branded card (SAFETY V-03: never a fake journal page), high contrast only."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from assemble.layout import H, W, safe_zone, validate_text_colours
from assemble.overlay import _wrap, font
from common import evidence

CREAM, INK, ACCENT, NIGHT = "#FFF6E5", "#111111", "#C8102E", "#101820"


def _centered_lines(d: ImageDraw.ImageDraw, text: str, size: int, fill: str, top: int, max_w: int,
                    cx: int, bottom_limit: int | None = None) -> int:
    words = text.split()
    while True:   # shrink until the block stays above the caption band
        f = font(size)
        asc, desc = f.getmetrics()
        n = len(_wrap(words, f, max_w))
        if bottom_limit is None or top + n * int((asc + desc) * 1.1) <= bottom_limit or size <= 48:
            break
        size -= 6
    y = top
    for ln in _wrap(words, f, max_w):
        s = " ".join(words[i] for i in ln)
        d.text((cx - f.getlength(s) / 2, y), s, font=f, fill=fill)
        y += int((asc + desc) * 1.1)
    return y


def render_graphic(spec: dict, out: Path) -> Path:
    kind = (spec.get("type") or "title").lower()
    text = spec.get("text") or ""
    z = safe_zone("master")
    if kind == "study_card":
        bg, fg = CREAM, INK
    elif kind in ("number", "timer"):
        bg, fg = NIGHT, "#FFFFFF"
    else:
        bg, fg = spec.get("background", NIGHT), spec.get("color", "#FFFFFF")
    validate_text_colours(fg, bg, f"graphic {kind}")
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    cx, max_w = z.center_x, z.width - 40
    limit = z.bottom - 240          # caption band (2 lines) starts ~200 px above the safe-zone line
    if kind == "study_card":
        eid = spec.get("source_evidence_id")
        cit = evidence.citation(eid) or spec.get("citation") or ""
        d.rectangle([0, 0, 24, H], fill=ACCENT)
        y = _centered_lines(d, text, 76, fg, int(H * 0.47), max_w, cx, limit - 120)
        _centered_lines(d, cit + (f" · {eid}" if eid else ""), 44, fg, y + 40, max_w, cx, limit)
    elif kind == "checklist":
        items = spec.get("items") or [s.strip() for s in text.split("·") if s.strip()]
        f = font(64)
        y = int(H * 0.47)
        for it in items[:3]:
            d.rounded_rectangle([z.left, y + 8, z.left + 56, y + 64], radius=12, outline=fg, width=6)
            d.line([z.left + 12, y + 36, z.left + 26, y + 52, z.left + 48, y + 18], fill=fg, width=8)
            d.text((z.left + 84, y), it, font=f, fill=fg)
            y += 110
    else:   # number, timer (static read-out), title
        # text sits below the emphasis band (40% H) and above the caption band
        _centered_lines(d, text, 130 if kind in ("number", "timer") else 96, fg, int(H * 0.47), max_w, cx, limit)
    img.save(out)
    return out


def colour_card(colour: str, label: str, out: Path, size=(W, H)) -> Path:
    """Synthetic stand-in for generated shots (sample/tests). Text kept out of the caption band."""
    img = Image.new("RGB", size, colour)
    d = ImageDraw.Draw(img)
    # simple depth cue so motion (push-in / handheld) is visible and pHash differs per card
    for i in range(0, size[1], 160):
        d.rectangle([0, i, size[0], i + 60], fill=_shade(colour, 0.88))
    d.ellipse([size[0] * 0.25, size[1] * 0.42, size[0] * 0.75, size[1] * 0.70], fill=_shade(colour, 0.7))
    f = font(72)
    d.text((size[0] / 2 - f.getlength(label) / 2, size[1] * 0.52), label, font=f, fill="#FFFFFF")
    img.save(out)
    return out


def _shade(hexcol: str, k: float) -> str:
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))
