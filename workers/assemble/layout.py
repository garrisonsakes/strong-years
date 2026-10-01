"""Frame geometry, safe zones and colour rules.

Safe zones (fractions of the 1080x1920 frame) keep burned-in text out of platform UI:
- prompts/07 + n8n manifest: top 12%, bottom 22%, right 14% on TikTok.
- SAFETY_RULES V-04: at least 180 px from the top and 250 px from the bottom (both looser than the % zones).
The master uses the union of every platform's zones so a single master is safe everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass

W, H, FPS = 1080, 1920, 30

SAFE_ZONES = {
    #            top    bottom  left   right
    "master":    (0.12, 0.22, 0.06, 0.14),
    "instagram": (0.12, 0.20, 0.06, 0.12),
    "tiktok":    (0.12, 0.22, 0.06, 0.14),
    "youtube":   (0.12, 0.20, 0.06, 0.12),
    "facebook":  (0.12, 0.20, 0.06, 0.12),
    "threads":   (0.10, 0.15, 0.06, 0.08),
    "x":         (0.10, 0.15, 0.06, 0.08),
}
MIN_TOP_PX, MIN_BOTTOM_PX = 180, 250           # SAFETY_RULES V-04


@dataclass(frozen=True)
class Zone:
    top: int
    bottom: int     # y of the lowest usable pixel row
    left: int
    right: int      # x of the right-most usable column

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def center_x(self) -> int:
        return (self.left + self.right) // 2


def safe_zone(platform: str = "master", overrides: dict | None = None) -> Zone:
    top, bottom, left, right = SAFE_ZONES.get(platform, SAFE_ZONES["master"])
    o = overrides or {}
    top = o.get("top_pct", top * 100) / 100
    bottom = o.get("bottom_pct", bottom * 100) / 100
    right = o.get("right_pct", right * 100) / 100
    left = o.get("left_pct", left * 100) / 100
    return Zone(top=max(int(H * top), MIN_TOP_PX), bottom=min(int(H * (1 - bottom)), H - MIN_BOTTOM_PX),
                left=int(W * left), right=int(W * (1 - right)))


# ---- colour rules (client: never gray text; SAFETY V-04 high contrast only) -------------------------
def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def rel_luminance(rgb: tuple[int, int, int]) -> float:
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    a, b = rel_luminance(hex_to_rgb(fg)), rel_luminance(hex_to_rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def is_grayish(hexcol: str) -> bool:
    """Mid-luminance, low-saturation colours read as gray text. Pure white/near-black are fine."""
    r, g, b = hex_to_rgb(hexcol)
    mx, mn = max(r, g, b), min(r, g, b)
    sat = 0 if mx == 0 else (mx - mn) / mx
    return sat < 0.12 and 40 < mx < 235


MIN_CONTRAST = 7.0      # WCAG AAA for text


def validate_text_colours(fill: str, background: str, what: str = "text") -> None:
    if is_grayish(fill):
        raise ValueError(f"{what} colour {fill} reads as gray (client rule: never gray text)")
    cr = contrast_ratio(fill, background)
    if cr < MIN_CONTRAST:
        raise ValueError(f"{what} contrast {cr:.1f}:1 ({fill} on {background}) is below {MIN_CONTRAST}:1")
