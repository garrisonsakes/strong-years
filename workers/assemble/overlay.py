"""PIL compositor for every burned-in element: word-by-word captions, hook/emphasis text, study-card inset,
the persistent "AI character" corner tag (SAFETY_RULES D-02).

All overlay states are rendered as full-frame RGBA PNGs and fed to ffmpeg as ONE concat-demuxer stream,
so the final encode needs a single overlay filter however many caption states there are.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from assemble import captions as C
from assemble.layout import FPS, H, W, Zone, hex_to_rgb, safe_zone, validate_text_colours
from common import config


@dataclass
class CaptionStyle:
    font: str = "Figtree"
    size_px: int = 60                 # 56–64 px (ENGINE_100X §4.4: captions >= 56 px; SAFETY V-04 min 52)
    fill: str = "#FFFFFF"
    highlight: str = "#FFD84D"
    pill: str = "#111111"
    pill_alpha: float = 0.88
    max_words_per_chunk: int = 4
    safe_bottom_pct: float = 22
    safe_top_pct: float = 12
    uppercase: bool = False

    @classmethod
    def from_manifest(cls, d: dict | None) -> "CaptionStyle":
        d = d or {}
        known = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        st = cls(**known)
        st.size_px = int(min(64, max(CAPTION_MIN_PX, st.size_px)))
        validate_text_colours(st.fill, st.pill, "caption fill")
        validate_text_colours(st.highlight, st.pill, "caption highlight")
        return st


@lru_cache(maxsize=32)
def font(size: int, path: str | None = None) -> ImageFont.FreeTypeFont:
    p = Path(path or config.CAPTION_FONT)
    if not p.exists():
        raise FileNotFoundError(f"caption font missing: {p} (run from repo with workers/fonts present)")
    return ImageFont.truetype(str(p), size)


# ENGINE_100X §4.4 / holes #3 (older eyes, [S43]): hook text >= 72 px cap height on 1080x1920, captions and other
# on-screen text >= 56 px. The hook size is derived from the font's real cap height, never assumed.
CAPTION_MIN_PX = 56
HOOK_MIN_CAP_PX = 72


def cap_height(size: int) -> int:
    b = font(size).getbbox("H")
    return int(b[3] - b[1])


@lru_cache(maxsize=4)
def hook_min_size(min_cap_px: int = HOOK_MIN_CAP_PX) -> int:
    s = CAPTION_MIN_PX
    while cap_height(s) < min_cap_px and s < 200:
        s += 2
    return s


def _rgba(hexcol: str, alpha: float = 1.0) -> tuple[int, int, int, int]:
    r, g, b = hex_to_rgb(hexcol)
    return (r, g, b, int(round(255 * alpha)))


def _wrap(words: list[str], f: ImageFont.FreeTypeFont, max_w: int) -> list[list[int]]:
    """Greedy wrap -> list of lines (word indices)."""
    lines, cur = [], []
    space = f.getlength(" ")
    width = 0.0
    for i, w in enumerate(words):
        wl = f.getlength(w)
        if cur and width + space + wl > max_w:
            lines.append(cur)
            cur, width = [], 0.0
        width = width + (space if cur else 0) + wl
        cur.append(i)
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(img: Image.Image, words: list[str], *, size: int, fill: str, pill: str, pill_alpha: float,
                    center_x: int, max_w: int, anchor_y: int, anchor: str = "bottom", highlight_idx: int | None = None,
                    highlight: str | None = None, max_lines: int = 2, min_size: int = 52, pad_x: int = 28,
                    pad_y: int = 16, radius: int = 26) -> tuple[int, int, int, int]:
    """Draw words on a rounded pill. Returns the pill box (x0, y0, x1, y1)."""
    validate_text_colours(fill, pill, "text")
    s = size
    while True:
        f = font(s)
        lines = _wrap(words, f, max_w - 2 * pad_x)
        if len(lines) <= max_lines or s <= min_size:
            break
        s -= 2
    asc, desc = f.getmetrics()
    line_h = int((asc + desc) * 1.08)
    space = f.getlength(" ")
    widths = [sum(f.getlength(words[i]) for i in ln) + space * (len(ln) - 1) for ln in lines]
    box_w = int(max(widths) + 2 * pad_x)
    box_h = int(line_h * len(lines) + 2 * pad_y)
    x0 = int(center_x - box_w / 2)
    y0 = anchor_y - box_h if anchor == "bottom" else anchor_y
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=radius, fill=_rgba(pill, pill_alpha))
    y = y0 + pad_y
    for ln, lw in zip(lines, widths):
        x = center_x - lw / 2
        for i in ln:
            col = highlight if (highlight_idx is not None and i == highlight_idx and highlight) else fill
            d.text((x, y), words[i], font=f, fill=_rgba(col))
            x += f.getlength(words[i]) + space
        y += line_h
    img.alpha_composite(layer)
    return (x0, y0, x0 + box_w, y0 + box_h)


def draw_ai_tag(img: Image.Image, text: str, zone: Zone, size: int = 34) -> tuple[int, int, int, int]:
    """Persistent top-left tag: white text on a dark pill at 70% opacity (D-02). The text itself stays fully
    opaque white so it never reads as gray (client rule); the 70% applies to the pill."""
    size = max(size, 28)
    f = font(size)
    tw = f.getlength(text)
    asc, desc = f.getmetrics()
    pad_x, pad_y = 18, 9
    x0, y0 = 40, zone.top + 6
    box = (x0, y0, int(x0 + tw + 2 * pad_x), int(y0 + asc + desc + 2 * pad_y))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=(0, 0, 0, int(255 * 0.70)))
    d.text((x0 + pad_x, y0 + pad_y), text, font=f, fill=(255, 255, 255, 255))
    img.alpha_composite(layer)
    return box


def draw_study_card(img: Image.Image, title: str, citation: str, zone: Zone, eid: str | None = None,
                    bottom_y: int | None = None) -> tuple[int, int, int, int]:
    """Lower-third-left study card inset (CHARACTERS §13.2). Near-black on cream; citation exactly as EVIDENCE.md."""
    bg, fg, accent = "#FFF6E5", "#111111", "#C8102E"
    validate_text_colours(fg, bg, "study card")
    ft, fc = font(44), font(34)
    max_w = 640
    t_lines = _wrap(title.split(), ft, max_w - 60)
    c_words = (citation + (f" · {eid}" if eid else "")).split()
    c_lines = _wrap(c_words, fc, max_w - 60)
    ta, td = ft.getmetrics()
    ca, cd = fc.getmetrics()
    h = 28 + len(t_lines) * (ta + td + 4) + 10 + len(c_lines) * (ca + cd + 2) + 26
    x0 = zone.left
    y1 = bottom_y if bottom_y is not None else int(H * 0.66)
    y0 = y1 - h
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x0, y0, x0 + max_w, y1], radius=22, fill=_rgba(bg, 0.97))
    d.rounded_rectangle([x0, y0, x0 + 12, y1], radius=6, fill=_rgba(accent))
    y = y0 + 28
    tw = title.split()
    for ln in t_lines:
        d.text((x0 + 36, y), " ".join(tw[i] for i in ln), font=ft, fill=_rgba(fg))
        y += ta + td + 4
    y += 10
    for ln in c_lines:
        d.text((x0 + 36, y), " ".join(c_words[i] for i in ln), font=fc, fill=_rgba(fg))
        y += ca + cd + 2
    img.alpha_composite(layer)
    return (x0, y0, x0 + max_w, y1)


@dataclass
class OverlayPlan:
    duration: float
    zone: Zone
    style: CaptionStyle
    words: list[C.Word] = field(default_factory=list)
    texts: list[dict] = field(default_factory=list)        # {text, start_s, end_s, style: hook|emphasis}
    study_cards: list[dict] = field(default_factory=list)  # {title, citation, evidence_id, start_s, end_s}
    ai_tag: str | None = "AI character"
    include_hook: bool = True


def _q(t: float) -> float:
    return round(round(t * FPS) / FPS, 4)


def build_states(plan: OverlayPlan) -> list[tuple[float, float, tuple]]:
    """Piecewise-constant overlay states [(start, end, key)] covering [0, duration]."""
    chunks = C.chunk_words(plan.words, max_words=plan.style.max_words_per_chunk)
    wstates = C.word_states(chunks)
    events = []
    for s, e, ci, wi in wstates:
        events.append((s, e, ("cap", ci, wi)))
    for k, t in enumerate(plan.texts):
        if t.get("style") == "hook" and not plan.include_hook:
            continue
        events.append((float(t["start_s"]), float(t["end_s"]), ("txt", k)))
    for k, sc in enumerate(plan.study_cards):
        events.append((float(sc["start_s"]), float(sc["end_s"]), ("card", k)))
    cuts = {0.0, _q(plan.duration)}
    for s, e, _ in events:
        cuts.add(_q(max(0.0, min(s, plan.duration))))
        cuts.add(_q(max(0.0, min(e, plan.duration))))
    cuts = sorted(cuts)
    out: list[tuple[float, float, tuple]] = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-6:
            continue
        mid = (a + b) / 2
        active = tuple(sorted(key for s, e, key in events if s <= mid < e))
        if out and out[-1][2] == active:
            out[-1] = (out[-1][0], b, active)
        else:
            out.append((a, b, active))
    plan._chunks = chunks  # type: ignore[attr-defined]
    return out


def render_state(plan: OverlayPlan, key: tuple) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    z, st = plan.zone, plan.style
    chunks = getattr(plan, "_chunks", [])
    for item in key:
        if item[0] == "card":
            sc = plan.study_cards[item[1]]
            draw_study_card(img, sc.get("title", ""), sc.get("citation", ""), z, sc.get("evidence_id"),
                            bottom_y=z.bottom - 230)
    for item in key:
        if item[0] == "txt":
            t = plan.texts[item[1]]
            words = t["text"].split()
            if t.get("style") == "hook":
                hs = hook_min_size()
                draw_text_block(img, words, size=max(78, hs), fill="#FFF6E5", pill="#111111", pill_alpha=0.9,
                                center_x=W // 2, max_w=z.width + 40, anchor_y=z.top + 90, anchor="top",
                                max_lines=4, min_size=hs)
            else:
                draw_text_block(img, words, size=64, fill="#FFFFFF", pill="#111111", pill_alpha=0.88,
                                center_x=z.center_x, max_w=z.width, anchor_y=int(H * 0.40), anchor="top",
                                max_lines=2, min_size=CAPTION_MIN_PX)
    for item in key:
        if item[0] == "cap":
            ch = chunks[item[1]]
            words = [w.text.upper() if st.uppercase else w.text for w in ch.words]
            draw_text_block(img, words, size=st.size_px, fill=st.fill, pill=st.pill, pill_alpha=st.pill_alpha,
                            center_x=z.center_x, max_w=z.width, anchor_y=z.bottom, anchor="bottom",
                            highlight_idx=item[2], highlight=st.highlight, max_lines=2, min_size=CAPTION_MIN_PX)
    if plan.ai_tag:
        draw_ai_tag(img, plan.ai_tag, z)
    return img


def render_track(plan: OverlayPlan, outdir: Path) -> Path:
    """Render every state to PNG and write an ffmpeg concat list. Returns the list path."""
    outdir.mkdir(parents=True, exist_ok=True)
    states = build_states(plan)
    cache: dict[tuple, Path] = {}
    lines = ["ffconcat version 1.0"]
    last = None
    for a, b, key in states:
        if key not in cache:
            p = outdir / f"ov_{len(cache):04d}.png"
            render_state(plan, key).save(p, compress_level=1)
            cache[key] = p
        lines.append(f"file '{cache[key].name}'")
        lines.append(f"duration {b - a:.4f}")
        last = cache[key]
    if last is not None:
        lines.append(f"file '{last.name}'")
    lst = outdir / "overlays.ffconcat"
    lst.write_text("\n".join(lines) + "\n")
    return lst


def burned_in_strings(plan: OverlayPlan) -> list[str]:
    """Every string the viewer will see burned in (used by compliance pass 2 and caption OCR QA)."""
    out = [t["text"] for t in plan.texts if t.get("style") != "hook" or plan.include_hook]
    out += [f"{sc.get('title', '')} {sc.get('citation', '')}".strip() for sc in plan.study_cards]
    if plan.ai_tag:
        out.append(plan.ai_tag)
    return out
