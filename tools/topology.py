#!/usr/bin/env python3
"""CANON UPDATE 6 account topology and the launch-week velocity ramp (BRIEF.md CANON 6; ENGINE_SAVAGE20 §B(b) 7).

  python3 tools/topology.py [--date YYYY-MM-DD] [--json]          print the D1..D7 slot counts per account
  python3 tools/slots_ics.py --canon6 [--date ...] [--out DIR]    one .ics per ACCOUNT for launch day and the week

Accounts at launch: 4 Instagram pages (each with its own Threads and X), 4 TikTok accounts, ONE Facebook page, ONE
YouTube Shorts channel. Steady state per CANON 6 (reached on D7 of the ramp): IG page 6 main + 20 Trial Reels +
3 Stories/day, Threads 12 and X 6 per page, TikTok 26/account, Facebook 16/day (12 videos + 2 long cuts + 1 text +
1 photo), YouTube 4/day until the quota raise (then 6). The ramp is an [A] assumption for brand-new accounts: feed
posts exist before Trial Reels start, volume steps up daily, and any "limit"/"unavailable" message stops trials for
that account (NEXT50 RO-1). D1 Instagram and Facebook Reels are the 6 rendered day-1 posts
(production/launch_day/day1_plan.json); every other D1 video slot is GEN-needed and is skipped if no QA-passed file
exists. The first 10 Threads + 10 X slots each day are the hook pre-screen (workers/growth/hook_prescreen.py).
Rows use the posting_plan_90d.csv column names that tools/slots_ics.py reads. Offline; writes nothing by itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IG_PAGES = ("@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength")
X_HANDLE = {"@changyin": "@changyin", "@sunyoon.kitchen": "@sunyoon_kitchen", "@changandsun": "@changandsun",
            "@changyin.strength": "@changyinstrong"}
FB_PAGE = "@changandsun"          # the ONE Facebook page (Chang & Sun) [verify name in Business Suite]
YT_CHANNEL = "@changandsun"       # the ONE YouTube Shorts channel [verify handle]
PAGE_CTA = {"@changyin": "WAITLIST", "@sunyoon.kitchen": "SOUP", "@changandsun": "WAITLIST", "@changyin.strength": "STRONG"}

# account -> (platform, handle). Account ids double as calendar file names.
ACCOUNTS: list[dict] = (
    [{"account": f"ig_{p.lstrip('@').replace('.', '_')}", "platform": "instagram", "handle": p, "page": p} for p in IG_PAGES]
    + [{"account": f"th_{p.lstrip('@').replace('.', '_')}", "platform": "threads", "handle": p, "page": p} for p in IG_PAGES]
    + [{"account": f"x_{X_HANDLE[p].lstrip('@')}", "platform": "x", "handle": X_HANDLE[p], "page": p} for p in IG_PAGES]
    + [{"account": f"tt_{p.lstrip('@').replace('.', '_')}", "platform": "tiktok", "handle": p, "page": p} for p in IG_PAGES]
    + [{"account": "fb_changandsun", "platform": "facebook", "handle": FB_PAGE, "page": FB_PAGE},
       {"account": "yt_changandsun", "platform": "youtube", "handle": YT_CHANNEL, "page": YT_CHANNEL}])

STEADY = {"ig_reels": 6, "ig_trial": 20, "ig_story": 3, "threads": 12, "x": 6, "tiktok": 26,
          "fb_reels": 12, "fb_long": 2, "fb_text": 1, "fb_photo": 1, "yt_shorts": 4}
# per account per day, D1..D7 [A]; D7 == STEADY (YouTube 4 until the quota raise)
RAMP = {"ig_reels": (3, 3, 4, 5, 6, 6, 6), "ig_trial": (0, 2, 5, 10, 15, 20, 20), "ig_story": (1, 2, 3, 3, 3, 3, 3),
        "threads": (3, 6, 8, 10, 12, 12, 12), "x": (2, 3, 4, 5, 6, 6, 6), "tiktok": (1, 3, 6, 10, 16, 20, 26),
        "fb_reels": (2, 4, 6, 8, 10, 12, 12), "fb_long": (0, 0, 1, 1, 2, 2, 2), "fb_text": (1, 1, 1, 1, 1, 1, 1),
        "fb_photo": (0, 1, 1, 1, 1, 1, 1), "yt_shorts": (1, 2, 3, 4, 4, 4, 4)}
D1_IG_MAIN_NEW_PAGE = 1           # @changandsun / @changyin.strength have no rendered day-1 post: one intro, GEN-needed
ACCOUNT_LANES = {"instagram": ("ig_reels", "ig_trial", "ig_story"), "threads": ("threads",), "x": ("x",),
                 "tiktok": ("tiktok",), "facebook": ("fb_reels", "fb_long", "fb_text", "fb_photo"), "youtube": ("yt_shorts",)}
WINDOW = {"ig_reels": ("08:00", "21:00"), "ig_trial": ("07:30", "22:00"), "threads": ("07:00", "21:30"),
          "x": ("07:00", "21:00"), "tiktok": ("07:00", "22:00"), "fb_reels": ("08:00", "21:30"), "fb_long": ("12:00", "20:00"),
          "fb_text": ("10:30", "10:30"), "fb_photo": ("15:30", "15:30"), "yt_shorts": ("09:00", "20:00")}
STORY_SLOTS = (("09:00", "poll"), ("13:00", "question box"), ("19:30", "link sticker"))
PROBE_SLOTS = ("07:00", "19:00")  # hook pre-screen text posts (hook_prescreen.SLOTS)


def _hm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _mins(s: str) -> int:
    h, m = map(int, s.split(":"))
    return h * 60 + m


def spread(n: int, lane: str, offset: int = 0) -> list[str]:
    """n slots evenly inside the lane window, shifted by `offset` minutes so sibling accounts never share a minute."""
    a, b = map(_mins, WINDOW[lane])
    if n <= 0:
        return []
    if n == 1 or a == b:
        return [_hm(min(b, a + offset))] * n if n == 1 else [_hm(a + offset + i * 7) for i in range(n)]
    step = (b - a) / (n - 1)
    return [_hm(min(23 * 60 + 55, int(a + i * step) + offset)) for i in range(n)]


def day1_posts() -> list[dict]:
    d = json.loads((ROOT / "production" / "launch_day" / "day1_plan.json").read_text(encoding="utf-8"))
    return d["posts"]


def count(lane: str, day_index: int, page: str | None = None) -> int:
    n = RAMP[lane][min(day_index, 7) - 1]
    if lane == "ig_reels" and day_index == 1 and page in ("@changandsun", "@changyin.strength"):
        return D1_IG_MAIN_NEW_PAGE
    return n


def _row(day: date, i: int, acc: dict, lane: str, slot: str, **kw) -> dict:
    return {"date": day.isoformat(), "day_index": str(i), "page": acc["account"], "handle": acc["handle"],
            "platform": lane, "slot_et": slot, "file_id": kw.get("file_id", ""), "script_id": kw.get("script_id", ""),
            "cta_keyword": kw.get("cta", PAGE_CTA.get(acc["page"], "")), "seconds": kw.get("seconds", ""),
            "variant_role": kw.get("role", "TEST" if lane == "ig_trial" else "PLACEMENT"), "note": kw.get("note", "")}


def rows_for_day(launch: date, i: int) -> list[dict]:
    day = launch + timedelta(days=i - 1)
    d1 = day1_posts() if i == 1 else []
    out: list[dict] = []
    for k, acc in enumerate(ACCOUNTS):
        off = (k % 4) * 4
        for lane in ACCOUNT_LANES[acc["platform"]]:
            n = count(lane, i, acc["page"])
            if lane == "ig_story":
                for slot, kind in STORY_SLOTS[:n]:
                    out.append(_row(day, i, acc, lane, _hm(_mins(slot) + off), role="STORY",
                                    note=f"Story: {kind}" + (" (link sticker to /go)" if kind == "link sticker" else "")))
                continue
            if i == 1 and lane in ("ig_reels", "fb_reels"):
                plat = "ig" if lane == "ig_reels" else "fb"
                mine = [p for p in d1 if (p["page"] == acc["page"] if plat == "ig" else True)]
                if plat == "fb":   # ONE FB page: the first post of each day-1 page, at their FB times
                    mine = [p for p in d1 if p["post_id"].endswith("-1")][:n]
                for p in mine[:n]:
                    t = p["variants"][plat]["scheduled_at"][11:16]
                    out.append(_row(day, i, acc, lane, t, file_id=p["post_id"], script_id=p["script_id"],
                                    cta=p["cta_keyword"], seconds=p["target_seconds"], note="day-1 render (READY_FOR_HUMAN_REVIEW only)"))
                for t in spread(n - len(mine[:n]), lane, off):
                    out.append(_row(day, i, acc, lane, t, note="GEN-needed: skip if no QA-passed file"))
                continue
            slots = spread(n, lane, off)
            if lane in ("threads", "x"):
                probes = min(n, 3 if (k % 4) < 2 else 2)      # 3+3+2+2 = the day's top 10 hooks per lane
                for j, t in enumerate(slots):
                    probe = j < probes
                    t = _hm(_mins(PROBE_SLOTS[j % 2]) + 10 * (j // 2)) if probe else t
                    out.append(_row(day, i, acc, lane, _hm(_mins(t) + off), role="TEXT_PROBE" if probe else "PLACEMENT",
                                    note="hook pre-screen text post: read at 6 h" if probe else "text post"))
                continue
            for t in slots:
                out.append(_row(day, i, acc, lane, t, note="GEN-needed: skip if no QA-passed file"))
    taken: set[tuple[str, str]] = set()
    for r in sorted(out, key=lambda r: (r["page"], r["file_id"] == "", r["slot_et"])):   # one post per account-minute
        while (r["page"], r["slot_et"]) in taken:
            r["slot_et"] = _hm(_mins(r["slot_et"]) + 2)
        taken.add((r["page"], r["slot_et"]))
    return out


def week(launch: date) -> list[dict]:
    return [r for i in range(1, 8) for r in rows_for_day(launch, i)]


def totals(rows: list[dict]) -> dict:
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        out.setdefault(r["date"], {}).setdefault(r["platform"], 0)
        out[r["date"]][r["platform"]] += 1
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="launch day (default: the next 08:00 ET)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    from slots_ics import next_launch_date  # noqa: PLC0415
    launch = date.fromisoformat(a.date) if a.date else next_launch_date()
    t = totals(week(launch))
    if a.json:
        print(json.dumps(t, indent=1))
    else:
        for d, v in t.items():
            print(d, sum(v.values()), " ".join(f"{k}={n}" for k, n in sorted(v.items())))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main())
