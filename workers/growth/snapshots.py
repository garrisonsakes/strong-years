"""Raw captures -> PostMetrics snapshots at the fixed horizons t = 1h / 3h / 6h / 24h / 72h.

  build(post, captures, rollups, cfg) -> {"snapshots": [PostMetrics...], "dropped": [...], "age_h": float}

PostMetrics (one row of post_metrics):
  post_id, page_id, platform, horizon_h, published_at, captured_at, age_h, views, reach, likes, comments, shares,
  saves, profile_visits, link_clicks, follows, avg_watch_pct, keyword_comments, optins, buyers, members,
  interpolated (bool), missing ([counters the platform doesn't expose]), source

Rules (config "snapshots"):
  * a capture counts for horizon h when its age is inside window_h[h]; the capture nearest to h wins
  * two captures closer than duplicate_window_s are one snapshot (the later one wins: counters only grow)
  * clock skew: a capture up to clock_skew_tolerance_h BEFORE publish is clamped to age 0; one more than
    future_tolerance_h in the future of `now` is dropped; anything older than max_age_h is dropped
  * counters are monotone non-decreasing over time on every platform we use, so a later capture with a smaller
    value is a platform restatement: we keep the max seen so far (never lets a metric go backwards)
  * when no capture sits inside a window but two captures bracket h and both are within [h/3, 3h], the counters
    are interpolated on a log-time axis (views grow roughly log-linearly after the first hour) and flagged
  * rollups (keyword_comments / optins / buyers / members: comments, dm_leads, one-time orders, subscription orders
    attributed to the post) are DB facts keyed by post_id: they attach to every snapshot as of
    that capture time when given as a time series, or as totals when given as scalars (then flagged as-of now)
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from growth import config as G

ROLLUPS = ("keyword_comments", "optins", "buyers", "members")


def parse_dt(x) -> datetime | None:
    if x is None or x == "":
        return None
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        v = G.num(x, lo=0, hi=4102444800)             # unix seconds up to 2100
        return None if v is None else datetime.fromtimestamp(v, tz=timezone.utc)
    s = str(x).strip().replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _age_h(t: datetime, published: datetime) -> float:
    return (t - published).total_seconds() / 3600.0


def _clean_capture(c: dict) -> dict:
    out = {"missing": list(c.get("missing") or []), "source": c.get("source")}
    for k in G.COUNTERS:
        if k in ROLLUPS:
            continue
        v = G.num(c.get(k), lo=0, hi=1e13)
        if v is None:
            if k not in out["missing"]:
                out["missing"].append(k)
        else:
            out[k] = int(v)
    w = G.num(c.get("avg_watch_pct"), lo=0, hi=100)
    out["avg_watch_pct"] = w
    if w is None and "avg_watch_pct" not in out["missing"]:
        out["missing"].append("avg_watch_pct")
    return out


def normalize_captures(captures: list[dict], published: datetime, now: datetime, cfg: dict) -> tuple[list[dict], list[dict]]:
    """Sort, de-duplicate, clamp clock skew, drop future/ancient captures, enforce monotone counters."""
    sc = cfg["snapshots"]
    kept, dropped = [], []
    rows = []
    for i, c in enumerate(captures or []):
        t = parse_dt(c.get("captured_at"))
        if t is None:
            dropped.append({"index": i, "reason": "captured_at missing or unparsable"})
            continue
        age = _age_h(t, published)
        if age < -float(sc["clock_skew_tolerance_h"]):
            dropped.append({"index": i, "reason": f"captured {-age:.2f} h before publish (beyond clock-skew tolerance)"})
            continue
        if _age_h(t, now) > float(sc["future_tolerance_h"]):
            dropped.append({"index": i, "reason": "captured in the future"})
            continue
        if age > float(sc["max_age_h"]):
            dropped.append({"index": i, "reason": "older than max_age_h"})
            continue
        row = _clean_capture(c)
        row["captured_at"] = t
        row["age_h"] = max(0.0, age)          # clock skew inside tolerance -> clamp to publish time
        rows.append((t, i, row))
    rows.sort(key=lambda r: (r[0], r[1]))
    dup_s = float(sc["duplicate_window_s"])
    for t, i, row in rows:
        if kept and (t - kept[-1]["captured_at"]).total_seconds() < dup_s:
            prev = kept[-1]
            dropped.append({"index": i, "reason": f"duplicate of capture at {prev['captured_at'].isoformat()}"})
            for k in G.COUNTERS:                # merge: counters only grow
                if k in row and (k not in prev or row[k] > prev[k]):
                    prev[k] = row[k]
                    prev["missing"] = [m for m in prev["missing"] if m != k]
            if row.get("avg_watch_pct") is not None:
                prev["avg_watch_pct"] = row["avg_watch_pct"]
                prev["missing"] = [m for m in prev["missing"] if m != "avg_watch_pct"]
            prev["captured_at"], prev["age_h"] = t, row["age_h"]
            continue
        if kept:                                # monotone counters: never let a metric go backwards
            prev = kept[-1]
            for k in G.COUNTERS:
                if k in prev and (k not in row or row[k] < prev[k]):
                    row[k] = prev[k]
                    row["missing"] = [m for m in row["missing"] if m != k]
        kept.append(row)
    return kept, dropped


def _interp(a: dict, b: dict, h: float) -> dict:
    """Log-time interpolation of counters between captures a (before h) and b (after h)."""
    la, lb, lh = math.log(max(a["age_h"], 0.05)), math.log(max(b["age_h"], 0.05)), math.log(h)
    w = 0.0 if lb <= la else (lh - la) / (lb - la)
    w = min(1.0, max(0.0, w))
    out = {"missing": sorted(set(a["missing"]) | set(b["missing"])), "source": b.get("source"),
           "captured_at": a["captured_at"] + (b["captured_at"] - a["captured_at"]) * w, "age_h": h, "interpolated": True}
    for k in G.COUNTERS:
        if k in a and k in b:
            out[k] = int(round(a[k] + (b[k] - a[k]) * w))
        elif k in b:
            out[k] = b[k]
    if a.get("avg_watch_pct") is not None and b.get("avg_watch_pct") is not None:
        out["avg_watch_pct"] = a["avg_watch_pct"] + (b["avg_watch_pct"] - a["avg_watch_pct"]) * w
    else:
        out["avg_watch_pct"] = b.get("avg_watch_pct", a.get("avg_watch_pct"))
    return out


def pick_horizons(kept: list[dict], cfg: dict) -> dict[int, dict]:
    sc = cfg["snapshots"]
    out: dict[int, dict] = {}
    for h in G.HORIZONS:
        lo, hi = sc["window_h"][str(h)]
        inside = [r for r in kept if lo <= r["age_h"] <= hi]
        if inside:
            best = min(inside, key=lambda r: (abs(r["age_h"] - h), -r["age_h"]))
            out[h] = {**best, "interpolated": False}
            continue
        if not sc.get("interpolate"):
            continue
        before = [r for r in kept if r["age_h"] < lo]
        after = [r for r in kept if r["age_h"] > hi]
        if before and after:
            a, b = before[-1], after[0]
            ratio = float(sc["interpolate_max_ratio"])
            if a["age_h"] >= h / ratio and b["age_h"] <= h * ratio and a["age_h"] > 0:
                out[h] = _interp(a, b, float(h))
    return out


def _rollup_at(rollups: dict | None, key: str, at: datetime) -> tuple[int | None, bool]:
    """rollups[key] is an int total (as-of now) or a list of {"at": iso, "count": n} cumulative points."""
    if not rollups or key not in rollups:
        return None, False
    v = rollups[key]
    if isinstance(v, list):
        best = None
        for p in v:
            t = parse_dt((p or {}).get("at"))
            n = G.num((p or {}).get("count"), lo=0, hi=1e12)
            if t is None or n is None:
                continue
            if t <= at and (best is None or t > best[0]):
                best = (t, int(n))
        return (best[1] if best else 0), False
    n = G.num(v, lo=0, hi=1e12)
    return (None if n is None else int(n)), True


def build(post: dict, captures: list[dict], rollups: dict | None = None, cfg: dict | None = None,
          now: datetime | None = None) -> dict:
    cfg = cfg or G.load()
    now = now or datetime.now(timezone.utc)
    published = parse_dt(post.get("published_at"))
    if published is None:
        raise ValueError("post.published_at is required")
    if post.get("platform") not in G.PLATFORMS:
        raise ValueError("post.platform must be one of " + ", ".join(G.PLATFORMS))
    kept, dropped = normalize_captures(captures, published, now, cfg)
    picked = pick_horizons(kept, cfg)
    snaps = []
    for h in G.HORIZONS:
        r = picked.get(h)
        if not r:
            continue
        snap = {"post_id": post["post_id"], "page_id": post.get("page_id"), "platform": post["platform"], "horizon_h": h,
                "published_at": published.isoformat(), "captured_at": r["captured_at"].isoformat(),
                "age_h": round(r["age_h"], 3), "interpolated": bool(r.get("interpolated")), "source": r.get("source"),
                "missing": list(r["missing"])}
        for k in G.COUNTERS:
            if k in ROLLUPS:
                continue
            snap[k] = r.get(k)
        snap["avg_watch_pct"] = None if r.get("avg_watch_pct") is None else round(float(r["avg_watch_pct"]), 2)
        asof_now = []
        for k in ROLLUPS:
            val, scalar = _rollup_at(rollups, k, r["captured_at"])
            snap[k] = val
            if val is None:
                snap["missing"].append(k)
            elif scalar:
                asof_now.append(k)
        snap["rollups_as_of_now"] = asof_now
        snap["missing"] = sorted(set(snap["missing"]))
        snaps.append(snap)
    return {"post_id": post["post_id"], "snapshots": snaps, "dropped": dropped, "captures_kept": len(kept),
            "age_h": round(max(0.0, _age_h(now, published)), 3),
            "horizons_available": [s["horizon_h"] for s in snaps],
            "horizons_missing": [h for h in G.HORIZONS if h not in picked and h <= max(0.0, _age_h(now, published))]}


def latest_horizon(snapshots: list[dict]) -> dict | None:
    return max(snapshots, key=lambda s: s["horizon_h"]) if snapshots else None


def hours_between(a, b) -> float | None:
    da, db = parse_dt(a), parse_dt(b)
    return None if da is None or db is None else abs((da - db).total_seconds()) / 3600.0


def plus_hours(t, h: float) -> datetime:
    return parse_dt(t) + timedelta(hours=h)
