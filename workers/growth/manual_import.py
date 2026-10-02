"""Manual metrics CSV import (ENGINE_SAVAGE20 §B(b) item 5, SL-28.1).

Until Meta app review, the TikTok audit and the YouTube quota land, nobody can pull insights by API. A person exports
the platform's own CSV once or twice a day and this turns it into the same capture shape the API adapters produce
(growth/adapters._capture), keyed by the post's permalink / external id, so growth/snapshots.build() and the scorer
treat hand-read numbers exactly like API numbers. One row per post per read.

Recognised exports (headers as of Oct 2026; aliases cover the older names; unknown columns are ignored):
  ig  Meta Business Suite / Professional dashboard → Instagram content export
  fb  Meta Business Suite → Facebook content export
  tt  TikTok Studio → Analytics → Content → Export
  yt  YouTube Studio → Analytics → Advanced mode → Content → Export (Table data.csv)
  canonical  our own template: platform, permalink, captured_at, views, likes, comments, shares, saves, ...
Counters that a format does not carry are listed in `missing`, never written as 0.
"""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime, timezone
from pathlib import Path

from growth import adapters

ALIASES: dict[str, tuple[str, ...]] = {
    "external_post_id": ("post id", "video id", "content", "media id", "id"),
    "permalink": ("permalink", "video link", "link", "url", "post link"),
    "published_at": ("publish time", "post time", "video publish time", "date posted", "created time", "published_at"),
    "duration_s": ("duration (sec)", "duration", "video duration", "duration_s"),
    "views": ("views", "plays", "video views", "total views", "total plays", "3-second video views"),
    "reach": ("reach", "accounts reached", "reached audience"),
    "likes": ("likes", "total likes", "reactions"),
    "comments": ("comments", "total comments", "comments added"),
    "shares": ("shares", "total shares"),
    "saves": ("saves", "saved", "add to favorites", "favorites", "total favorites"),
    "profile_visits": ("profile visits", "profile views"),
    "follows": ("follows", "new followers", "subscribers", "subscribers gained", "followers gained"),
    "link_clicks": ("link clicks",),
    "avg_watch_s": ("average watch time", "average seconds viewed", "average view duration", "avg. watch time (sec)",
                    "average watch time (sec)"),
    "avg_watch_pct": ("average percentage viewed (%)", "average percentage viewed", "watched full video (%)",
                      "watched full video"),
    "captured_at": ("captured_at", "read at", "exported at"),
    "platform": ("platform",),
}
SIGNATURES = [   # (format, headers that must all be present, case-insensitive)
    ("canonical", ("platform", "permalink", "captured_at")),
    ("yt", ("video publish time",)), ("yt", ("average percentage viewed (%)",)),
    ("tt", ("video link", "total views")), ("tt", ("post time", "total likes")),
    ("fb", ("page id",)), ("fb", ("page name", "permalink")),
    ("ig", ("account username", "permalink")), ("ig", ("account id", "permalink")),
]
PLATFORM_FROM_HOST = (("instagram.com", "ig"), ("facebook.com", "fb"), ("fb.watch", "fb"), ("tiktok.com", "tt"),
                      ("youtube.com", "yt"), ("youtu.be", "yt"), ("threads.", "th"), ("x.com", "x"), ("twitter.com", "x"))


def _norm(h: str) -> str:
    return re.sub(r"\s+", " ", (h or "").replace("﻿", "").strip().lower())


def detect_format(headers: list[str]) -> str | None:
    hs = {_norm(h) for h in headers}
    for fmt, need in SIGNATURES:
        if all(n in hs for n in need):
            return fmt
    return None


def _num(x) -> float | None:
    s = str(x or "").strip().replace(",", "").replace("%", "")
    if s in ("", "-", "--", "n/a"):
        return None
    m = re.fullmatch(r"(\d+):(\d{2})(?::(\d{2}))?", s)          # 0:12 or 1:02:03 durations
    if m:
        a, b, c = m.groups()
        return float(int(a) * 3600 + int(b) * 60 + int(c)) if c else float(int(a) * 60 + int(b))
    s = re.sub(r"\s*s(ec)?$", "", s)
    mult = 1.0
    if s[-1:] in ("K", "k", "M", "m"):
        mult, s = (1e3 if s[-1] in "Kk" else 1e6), s[:-1]
    try:
        return float(s) * mult
    except ValueError:
        return None


def _dt(x) -> str | None:
    s = str(x or "").strip()
    if not s:
        return None
    for fmt in (None, "%m/%d/%Y %H:%M", "%b %d, %Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00")) if fmt is None else datetime.strptime(s, fmt)
            return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).isoformat()
        except ValueError:
            continue
    return None


def _platform(fmt: str, row: dict, permalink: str) -> str | None:
    if fmt != "canonical":
        return fmt
    p = (row.get("platform") or "").strip().lower()
    if p:
        return {"instagram": "ig", "facebook": "fb", "tiktok": "tt", "youtube": "yt", "threads": "th"}.get(p, p)
    return next((code for host, code in PLATFORM_FROM_HOST if host in permalink), None)


def normalize_manual_csv(src: str | Path, *, captured_at: str | None = None, fmt: str | None = None) -> dict:
    """CSV path or text -> {format, rows: [{post: {...}, capture: {...}}], skipped: [reasons]}."""
    text = Path(src).read_text(encoding="utf-8-sig") if isinstance(src, Path) or (
        isinstance(src, str) and "\n" not in src and Path(src).is_file()) else str(src)
    reader = csv.DictReader(io.StringIO(text))
    headers = reader.fieldnames or []
    fmt = fmt or detect_format(headers)
    if not fmt:
        raise ValueError(f"unrecognised export: headers {headers[:8]}")
    col = {}
    for key, names in ALIASES.items():
        for h in headers:
            if _norm(h) in names and key not in col:
                col[key] = h
    rows, skipped = [], []
    default_at = captured_at or datetime.now(timezone.utc).isoformat()
    for i, r in enumerate(reader, start=2):
        g = lambda k: r.get(col[k]) if k in col else None  # noqa: E731
        permalink = (g("permalink") or "").strip()
        ext = (g("external_post_id") or "").strip()
        if _norm(ext) == "total" or _norm(r.get(headers[0]) or "") == "total":
            continue                                  # YouTube's totals row
        if not ext and permalink:
            ext = [s for s in re.split(r"[/?#]", permalink.split("://", 1)[-1])[1:] if s][-1:] or [""]
            ext = ext[0]
        platform = _platform(fmt, {"platform": g("platform")}, permalink)
        if not (ext or permalink) or not platform:
            skipped.append(f"row {i}: no post id / permalink / platform")
            continue
        values = {k: adapters._n(_num(g(k))) for k in adapters.PLATFORM_COUNTERS if k in col}
        dur = _num(g("duration_s"))
        pct = _num(g("avg_watch_pct"))
        values["avg_watch_pct"] = adapters._pct(pct) if pct is not None else adapters._watch_pct_from_seconds(_num(g("avg_watch_s")), dur)
        missing = [k for k in adapters.PLATFORM_COUNTERS if values.get(k) is None]
        cap = adapters._capture(values, captured_at=_dt(g("captured_at")) or default_at, missing=missing,
                                source=f"manual_csv:{fmt}")
        rows.append({"post": {"platform": platform, "external_post_id": ext, "permalink": permalink or None,
                              "published_at": _dt(g("published_at")), "duration_s": dur}, "capture": cap})
    return {"format": fmt, "rows": rows, "skipped": skipped}


def join_posted_log(rows: list[dict], posted: list[dict]) -> tuple[list[dict], list[dict]]:
    """Attach our post_id/variant_id from the fallback pack's posted log (packager.fallback.read_posted_log) by
    permalink or external id. Returns (matched, unmatched)."""
    by_ext = {(p["platform"], p["external_post_id"]): p for p in posted if p.get("external_post_id")}
    by_link = {p["permalink"].rstrip("/"): p for p in posted if p.get("permalink")}
    matched, unmatched = [], []
    for r in rows:
        po = r["post"]
        hit = by_link.get((po.get("permalink") or "").rstrip("/")) or by_ext.get((po["platform"], po["external_post_id"]))
        if hit:
            matched.append({**r, "post": {**po, "post_id": hit.get("post_id"), "variant_id": hit.get("variant_id"),
                                          "page": hit.get("page"), "published_at": po.get("published_at") or hit.get("posted_at")}})
        else:
            unmatched.append(r)
    return matched, unmatched
