#!/usr/bin/env python3
"""Posting rules for reach with a 55+ audience (VIRALITY_SYSTEM.md §5). Pure + a CLI; no network, nothing posts.

  SLOTS_ET         per-platform slot windows (ET) the plan must sit inside
  HASHTAG_MAX      per-platform hashtag caps (IG 5 is a hard platform cap since Dec 2025)
  TRIAL_REEL_DAYS  every IG reel in a page's first 14 days carries ig_trial_reel = True
  remix_top3()     the daily rule: each page's top 3 posts of the last 24 h by (shares + saves) per view get
                   remix orders due within 24 h (new object / new set / same hook grammar, never a re-upload)

python3 tools/posting_rules.py            # checks data/content/posting_plan_90d.csv + script hashtags, writes
                                          # data/content/posting_plan_flags.csv (file_id, ig_trial_reel, slot_ok)
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "content")

# 55+ timing, ET. Pew (June 2025): 65+ use YouTube 84%, Facebook 71%, Instagram 50%, TikTok 37%. Older viewers are
# morning-heavy; POSTDB rule 16 (Yang Mun scheduled 8–11am ET + evening, n = 45, no clear winner) says these are slot
# tests, not findings [A]. Hard rule: every slot inside the 06:00–21:30 ET envelope (no late-night posts to a 55+
# audience). Soft rule, reported: each page x platform x day has at least one slot in a morning PRIME window and one
# in an evening PRIME window; the allocator puts that day's highest-scoring master in the first morning prime slot.
ENVELOPE_ET = ("06:00", "21:30")
PRIME_ET = {
    "ig_reels": [("06:30", "09:30"), ("18:30", "21:00")],
    "fb_reels": [("06:00", "09:30"), ("18:00", "21:00")],
    "tiktok":   [("07:00", "10:00"), ("18:30", "21:30")],
    "yt_shorts": [("06:30", "10:30"), ("17:00", "21:30")],
    "threads":  [("06:30", "10:00"), ("18:00", "21:30")],
    "x":        [("06:30", "10:00"), ("18:00", "21:30")],
}
SLOTS_ET = PRIME_ET   # back-compat name
# IG: 5 max (Mosseri, 18 Dec 2025, enforced); hashtags help search, not reach. Threads: one topic tag per post.
# YouTube ignores all tags on a video with more than 15 and shows 3 above the title. FB / TikTok / X: [A] small sets.
HASHTAG_MAX = {"ig_reels": 5, "fb_reels": 3, "tiktok": 5, "yt_shorts": 3, "threads": 1, "x": 2}
TRIAL_REEL_DAYS = 14
REMIX_TOP_N, REMIX_DUE_H = 3, 24
PAGE_START = {"@changyin": -7, "@sunyoon.kitchen": -7, "@changandsun": -7, "@changyin.strength": 15,
              "@changyin.mobility": 15, "@sunyoon": 22, "@changyin.espanol": 30}


def _m(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def slot_ok(platform: str, hhmm: str) -> bool:
    return _m(ENVELOPE_ET[0]) <= _m(hhmm) <= _m(ENVELOPE_ET[1])


def in_prime(platform: str, hhmm: str) -> str | None:
    for k, (a, b) in enumerate(PRIME_ET.get(platform) or []):
        if _m(a) <= _m(hhmm) <= _m(b):
            return "morning" if k == 0 else "evening"
    return None


def hashtags(text: str | list | None) -> list[str]:
    t = " ".join(text) if isinstance(text, list) else (text or "")
    return re.findall(r"#\w+", t)


def hashtag_ok(platform: str, text) -> bool:
    return len(hashtags(text)) <= HASHTAG_MAX.get(platform, 5)


def ig_trial_reel(page: str, day_index: int) -> bool:
    start = PAGE_START.get(page, -7)
    return 0 <= int(day_index) - start < TRIAL_REEL_DAYS


def check_plan(rows: list[dict]) -> tuple[list[str], list[dict]]:
    problems, flags = [], []
    for r in rows:
        ok = slot_ok(r["platform"], r["slot_et"])
        if not ok:
            problems.append(f"{r['file_id']}: {r['platform']} slot {r['slot_et']} ET outside the 06:00–21:30 ET envelope")
        tr = r["platform"] == "ig_reels" and ig_trial_reel(r["page"], int(r["day_index"]))
        flags.append({"file_id": r["file_id"], "date": r["date"], "page": r["page"], "platform": r["platform"],
                      "slot_et": r["slot_et"], "slot_ok": ok, "prime": in_prime(r["platform"], r["slot_et"]) or "",
                      "ig_trial_reel": tr})
    return problems, flags


def prime_coverage(flags: list[dict]) -> float:
    days: dict[tuple, set] = {}
    for f in flags:
        days.setdefault((f["page"], f["platform"], f["date"]), set()).add(f["prime"])
    return sum(1 for v in days.values() if {"morning", "evening"} <= v) / max(1, len(days))


def check_scripts(scripts: list[dict]) -> list[str]:
    out = []
    for s in scripts:
        h = s.get("hashtags") or {}
        for key, pl in (("ig", "ig_reels"), ("tt", "tiktok")):
            if key in h and not hashtag_ok(pl, h[key]):
                out.append(f"{s['id']}: {len(hashtags(h[key]))} hashtags on {pl} (max {HASHTAG_MAX[pl]})")
    return out


def remix_top3(post_scores: list[dict], now: datetime) -> list[dict]:
    """Daily rule: per page, the top 3 posts published in the last 24 h by share_save_z (then reward) each get one
    remix order due within 24 h. Remix = same hook grammar, new object or set, fresh render; never the same file."""
    recent = [p for p in post_scores if p.get("published_at")
              and now - datetime.fromisoformat(str(p["published_at"]).replace("Z", "+00:00")) <= timedelta(hours=24)]
    by_page: dict[str, list[dict]] = {}
    for p in recent:
        by_page.setdefault(p.get("page_id"), []).append(p)
    orders = []
    for page, ps in by_page.items():
        ps.sort(key=lambda p: (p.get("share_save_z") if p.get("share_save_z") is not None else -99, p.get("reward") or 0),
                reverse=True)
        for rank, p in enumerate(ps[:REMIX_TOP_N], 1):
            orders.append({"page_id": page, "source_post_id": p["post_id"], "rank": rank, "hook_grammar": p.get("grammar"),
                           "due_by": (now + timedelta(hours=REMIX_DUE_H)).isoformat(), "kind": "remix",
                           "rule": "remix top-3 within 24 h: same hook grammar, new object/set, fresh render; no re-upload"})
    return orders


def main() -> int:
    plan = os.path.join(DATA, "posting_plan_90d.csv")
    rows = list(csv.DictReader(open(plan))) if os.path.exists(plan) else []
    problems, flags = check_plan(rows)
    problems += check_scripts(json.load(open(os.path.join(DATA, "scripts.json"))))
    with open(os.path.join(DATA, "posting_plan_flags.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file_id", "date", "page", "platform", "slot_et", "slot_ok", "prime", "ig_trial_reel"])
        w.writeheader()
        w.writerows(flags)
    ig = [f for f in flags if f["platform"] == "ig_reels"]
    print(f"posting rules: {len(rows)} plan rows, {sum(f['slot_ok'] for f in flags)} inside the 06:00–21:30 ET envelope; "
          f"page-days with a morning + evening prime slot {prime_coverage(flags):.0%}; "
          f"IG trial reels {sum(f['ig_trial_reel'] for f in ig)}/{len(ig)} IG rows; problems {len(problems)}")
    for p in problems[:30]:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
