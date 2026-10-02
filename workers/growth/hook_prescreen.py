"""Zero-render hook pre-screen on text surfaces (ENGINE_SAVAGE20 #2).

Each morning the top 10 candidate hooks for the next renders go out as plain-text posts on Threads and X, in the
character's voice, from the page the hook belongs to. At 6 h, engagement per impression ranks them; only the top N
are rendered. Text lanes have their own audiences, so the result is a PRIOR, not a verdict: each hook gets a Beta
prior with weight 5 for the allocator's hook arm.

  plan(day, hooks, ...)       -> probe rows (role text_probe, 07:00 / 19:00 ET slots alternating, one page each)
  package_probes(probes)      -> fallback-pack items (packager/text_probe.py runs /package rules on Threads and X)
  score(probes, captures, n)  -> ranked rows + `render` picks + Beta priors; captures in growth/adapters shape
Nothing here posts. While APIs are gated, a person posts from the fallback pack and reads the 6 h numbers into the
manual CSV import (growth/manual_import.py, canonical template).
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from compliance import caption_rules, scanner

PAGE_CODE = {"CY": "@changyin", "SK": "@sunyoon.kitchen", "CS": "@changandsun", "ST": "@changyin.strength",
             "MB": "@changyin.mobility", "SY": "@sunyoon"}
SPEAKER_SIGN = {"CHANG": "— Chang Yin (AI character)", "SUN": "— Sun Yoon (AI character)",
                "BOTH": "— Chang & Sun (AI characters)"}
SLOTS = ("07:00", "19:00")
READ_AT_H = 6.0
READ_WINDOW_H = (5.0, 9.0)
PRIOR_WEIGHT = 5.0
TOP_K = 10
RENDER_N = 6


def select(hooks: list[dict], k: int = TOP_K, already: set[str] | None = None) -> list[dict]:
    """Top-k untested hooks: ranked by `rank_score` (if given) then test_first, one per normalised text, each passing
    the deterministic compliance scan and the handle allowlist."""
    seen, out = set(already or ()), []
    ranked = sorted(hooks, key=lambda h: (-(h.get("rank_score") or 0.0), not h.get("test_first"), str(h.get("id"))))
    for h in ranked:
        hid, text = str(h.get("id")), (h.get("hook") or h.get("text") or "").strip()
        key = re.sub(r"[^a-z0-9]", "", text.lower())
        if not text or hid in seen or key in seen:
            continue
        if caption_rules.foreign_handles(text) or scanner.scan(text=text)["verdict"] != "pass":
            continue
        seen |= {hid, key}
        out.append(h)
        if len(out) == k:
            break
    return out


def probe_text(h: dict) -> str:
    text, _ = caption_rules.rewrite_time_words((h.get("hook") or h.get("text") or "").strip())
    return f"{text}\n\n{SPEAKER_SIGN.get(str(h.get('speaker', '')).upper(), '— the Strong Years team (AI characters)')}"


def plan(day: str, hooks: list[dict], k: int = TOP_K, already: set[str] | None = None,
         platforms: tuple[str, ...] = ("th", "x")) -> list[dict]:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
        raise ValueError("day must be YYYY-MM-DD")
    rows = []
    for i, h in enumerate(select(hooks, k, already)):
        slot = SLOTS[i % len(SLOTS)]
        page = PAGE_CODE.get(str(h.get("page", "")).upper(), h.get("page") or "@changyin")
        for pl in platforms:
            rows.append({"probe_id": f"TP-{day}-{h['id']}-{pl}", "hook_id": h["id"], "page": page, "platform": pl,
                         "role": "text_probe", "text": probe_text(h),
                         "scheduled_at": datetime.fromisoformat(f"{day}T{slot}").replace(tzinfo=ZoneInfo("America/New_York")).isoformat(),
                         "read_at_h": READ_AT_H})
    return rows


def package_probes(probes: list[dict]) -> list[dict]:
    from packager.text_probe import package_probe  # noqa: PLC0415
    return [package_probe(p) for p in probes]


def _dt(x) -> datetime:
    return datetime.fromisoformat(str(x).replace("Z", "+00:00"))


def engagement(c: dict) -> tuple[float | None, int]:
    views = c.get("views")
    if not views:
        return None, 0
    acts = sum(int(c.get(k) or 0) for k in ("likes", "comments", "shares", "saves"))
    return acts / views, int(views)


def score(probes: list[dict], captures: dict[str, list[dict]], render_n: int = RENDER_N, now: datetime | None = None) -> dict:
    """captures: probe_id -> [capture]. Per hook: the capture nearest to posted+6 h inside 5–9 h, summed over its
    platforms. Rate = (likes+replies+reposts/quotes+bookmarks)/impressions, shrunk toward the day's pooled rate with
    PRIOR_WEIGHT·100 pseudo-impressions so a 40-view post can't win on 3 likes."""
    per_hook: dict[str, dict] = {}
    pending = []
    for p in probes:
        posted = _dt(p.get("posted_at") or p["scheduled_at"])
        best = None
        for c in captures.get(p["probe_id"], []):
            age = (_dt(c["captured_at"]) - posted).total_seconds() / 3600
            if READ_WINDOW_H[0] <= age <= READ_WINDOW_H[1] and (best is None or abs(age - READ_AT_H) < best[0]):
                best = (abs(age - READ_AT_H), c)
        h = per_hook.setdefault(p["hook_id"], {"hook_id": p["hook_id"], "page": p["page"], "acts": 0.0, "views": 0,
                                               "platforms": []})
        if best is None:
            pending.append(p["probe_id"])
            continue
        rate, views = engagement(best[1])
        if rate is not None:
            h["acts"] += rate * views
            h["views"] += views
            h["platforms"].append(p["platform"])
    pool_v = sum(h["views"] for h in per_hook.values())
    pool = (sum(h["acts"] for h in per_hook.values()) / pool_v) if pool_v else 0.0
    m = PRIOR_WEIGHT * 100
    rows = []
    for h in per_hook.values():
        h["rate_raw"] = round(h["acts"] / h["views"], 5) if h["views"] else None
        h["rate"] = round((h["acts"] + pool * m) / (h["views"] + m), 5) if h["views"] else None
        rows.append(h)
    read = sorted((r for r in rows if r["rate"] is not None), key=lambda r: -r["rate"])
    for i, r in enumerate(read):
        q = 1.0 - i / max(1, len(read) - 1) if len(read) > 1 else 0.5
        r["beta_prior"] = {"alpha": round(1 + PRIOR_WEIGHT * q, 3), "beta": round(1 + PRIOR_WEIGHT * (1 - q), 3)}
    return {"ranked": read, "render": [r["hook_id"] for r in read[:render_n]], "pending": pending,
            "unread": [r["hook_id"] for r in rows if r["rate"] is None], "pooled_rate": round(pool, 5)}


def read_due(probes: list[dict], now: datetime) -> list[dict]:
    """Probes whose 6 h read is due (posted + 6 h <= now): the list a person reads by hand while APIs are gated."""
    return [p for p in probes if _dt(p.get("posted_at") or p["scheduled_at"]) + timedelta(hours=READ_AT_H) <= now]
