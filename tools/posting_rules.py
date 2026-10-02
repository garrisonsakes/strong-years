#!/usr/bin/env python3
"""Posting rules for reach with a 55+ audience (VIRALITY_SYSTEM.md §5). Pure + a CLI; no network, nothing posts.

  SLOTS_ET         per-platform slot windows (ET) the plan must sit inside
  HASHTAG_MAX      per-platform hashtag caps (IG 5 is a hard platform cap since Dec 2025)
  TRIAL_REEL_DAYS  every IG reel in a page's first 14 days carries ig_trial_reel = True
  remix_top3()     the daily rule: each page's top 3 posts of the last 24 h by (shares + saves) per view get
                   remix orders due within 24 h (new object / new set / same hook grammar, never a re-upload)
  check_variants() modular variants + Trial Reels + Facebook native (ENGINE_100X §1, §2.1, §5): every row has a
                   variant_role (TEST / PLACEMENT / REMIX); same body never twice on one page x surface in 30 d;
                   Trial Reels ramp 3/6/cap per page-day (default 12, max 20) and IG publishes stop below the
                   100/24 h API limit; a TEST differs in >= 2 dimensions incl. the opening and posts >= 6 h before
                   its body's feed placement; one SS_PERFORMANCE trial per page x body; Facebook is a native upload
                   with its own caption + close, 2 long cuts (60-180 s) and 1 text + 1 photo post per page-day,
                   <= 25 Facebook posts per Page per day. Numbers come from workers/growth/config.py (variants).

python3 tools/posting_rules.py            # checks data/content/posting_plan_90d.csv + script hashtags, writes
                                          # data/content/posting_plan_flags.csv (file_id, ig_trial_reel, slot_ok)
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "content")
sys.path.insert(0, os.path.join(ROOT, "workers"))
from growth import config as _GC  # noqa: E402
from growth import variants as GV  # noqa: E402

VCFG = _GC.load()["variants"]
TRIAL_REELS_PER_PAGE_DAY = int(VCFG["trial_reels_per_page_day"])      # default 12, validated <= 20
IG_PUBLISH_LIMIT_24H, IG_PUBLISH_HARD_STOP = int(VCFG["ig_publish_limit_24h"]), int(VCFG["ig_publish_hard_stop"])
FB_PAGE_DAILY_MAX = int(VCFG["fb_page_daily_max"])
FB_LONG_S = tuple(VCFG["fb_long_s"])
FB_CLOSE = GV.CLOSE_BY_PLATFORM["facebook"]
GRADUATION_H = int(VCFG["graduation_horizon_h"])
PLAT_SURFACE = {"ig_reels": "instagram", "fb_reels": "facebook", "tiktok": "tiktok", "yt_shorts": "youtube",
                "threads": "threads", "x": "x", "ig_trial": "ig_trial", "fb_text": "facebook", "fb_photo": "facebook"}

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
PAGE_START = {"@changyin": -7, "@sunyoon.kitchen": -7, "@changandsun": -7, "@changyin.strength": -7,
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


def trial_cap(page: str, day_index: int) -> int:
    """Trial Reels a page may publish on this day: 3/day in weeks 1-2, 6/day in week 3, then the configured cap."""
    return GV.trial_cap(int(day_index) - PAGE_START.get(page, -7))


def fb_long_target(cadence: int) -> int:
    """Facebook long cuts per page-day: 2 at full cadence, 1 while the page runs 3/day."""
    return min(int(VCFG["fb_long_per_page_day"]), cadence // 2) if cadence else 0


def _when(r: dict) -> datetime:
    return datetime.fromisoformat(f"{r['date']}T{r['slot_et']}:00")


def check_variants(main_rows: list[dict], var_rows: list[dict]) -> list[str]:
    """ENGINE_100X §1/§2.1/§5 rules over the placement plan (main_rows) and the Trial Reel + FB text/photo rows."""
    err: list[str] = []
    allr = main_rows + var_rows
    for r in var_rows:
        if not slot_ok(r["platform"], r["slot_et"]):
            err.append(f"{r['file_id']}: slot {r['slot_et']} ET outside the 06:00–21:30 ET envelope")
    for r in allr:
        if r.get("variant_role") not in GV.ROLES:
            err.append(f"{r['file_id']}: variant_role {r.get('variant_role')!r} not in {GV.ROLES}")
    # same body never twice on one page x feed surface within 30 days; Trial Reels capped per body
    win = timedelta(days=int(VCFG["body_repeat_days"]))
    last: dict[tuple, datetime] = {}
    trials_per_body: dict[tuple, int] = {}
    for r in sorted(allr, key=_when):
        surf = PLAT_SURFACE.get(r["platform"], r["platform"])
        if r["platform"] in ("fb_text", "fb_photo", "ig_story"):
            continue                                   # text/photo posts and Stories stickers carry no video body
        k = (r["page"], surf, r.get("body_id"))
        if surf == "ig_trial":
            trials_per_body[k] = trials_per_body.get(k, 0) + 1
            if trials_per_body[k] > int(VCFG["max_trials_per_body"]):
                err.append(f"{r['file_id']}: more than {VCFG['max_trials_per_body']} Trial Reels of body {r.get('body_id')}")
            continue
        t = _when(r)
        if k in last and t - last[k] < win:
            err.append(f"{r['file_id']}: body {r.get('body_id')} twice on {r['page']} x {surf} within 30 d")
        last[k] = t
    # Trial Reel caps, the IG hard stop, the FB per-Page budget
    # CANON UPDATE 6: Facebook is ONE page for every IG page's content, so its budget is counted per FB account over the
    # rows the account plan actually schedules (publish != held); a bare placement plan counts every row.
    import account_topology as AT
    trials, ig, fb = Counter(), Counter(), Counter()
    for r in allr:
        key = (r["page"], r["date"])
        if r["platform"] == "ig_trial":
            trials[key] += 1
        if r["platform"] in ("ig_trial", "ig_reels"):
            ig[key] += 1
        if r["platform"] in ("fb_reels", "fb_text", "fb_photo") and r.get("publish", "y") != "held":
            fb[(AT.fb_page_for(r["page"]) or r["page"], r["date"])] += 1
    day_index = {(r["page"], r["date"]): int(r["day_index"]) for r in allr}
    for key, n in trials.items():
        cap = trial_cap(key[0], day_index[key])
        if n > cap:
            err.append(f"Trial Reels {key[0]} {key[1]}: {n} > ramp cap {cap}")
    for key, n in ig.items():
        if n > IG_PUBLISH_HARD_STOP:
            err.append(f"IG publishes {key[0]} {key[1]}: {n} > hard stop {IG_PUBLISH_HARD_STOP} (API limit {IG_PUBLISH_LIMIT_24H})")
    for key, n in fb.items():
        if n > FB_PAGE_DAILY_MAX:
            err.append(f"Facebook posts {key[0]} {key[1]}: {n} > {FB_PAGE_DAILY_MAX}/Page/day")
    # TEST rows: >= 2 dimensions incl. the opening, pairwise distinct per body, >= 6 h before the feed placement,
    # one SS_PERFORMANCE per page x body (a first-14-days IG placement posted as a Trial Reel counts)
    feed_at = {(r["page"], r.get("body_id")): _when(r) for r in main_rows if r["platform"] == "ig_reels"}
    auto = Counter((r["page"], r.get("body_id")) for r in main_rows
                   if r["platform"] == "ig_reels" and r.get("graduation_strategy") == "SS_PERFORMANCE")
    sigs: dict[tuple, list[dict]] = defaultdict(list)
    for r in var_rows:
        if r["platform"] != "ig_trial":
            continue
        dims = set(filter(None, (r.get("dims_changed") or "").split("|")))
        if len(dims) < int(VCFG["min_dims_changed"]) or not dims & GV.OPENING_DIMS:
            err.append(f"{r['file_id']}: Trial Reel changes {sorted(dims)}: needs >= {VCFG['min_dims_changed']} incl. the opening")
        sig = json.loads(r.get("signature") or "{}")
        k = (r["page"], r.get("body_id"))
        for o in sigs[k]:
            if len(GV.dims_changed(sig, o)) < int(VCFG["min_dims_changed"]):
                err.append(f"{r['file_id']}: differs from a sibling Trial Reel in < {VCFG['min_dims_changed']} dimensions")
        sigs[k].append(sig)
        if k in feed_at and _when(r) + timedelta(hours=GRADUATION_H) > feed_at[k]:
            err.append(f"{r['file_id']}: Trial Reel posts < {GRADUATION_H} h before its body's feed placement")
        if r.get("graduation_strategy") == "SS_PERFORMANCE":
            auto[k] += 1
    for k, n in auto.items():
        if n > 1:
            err.append(f"{k[0]} body {k[1]}: {n} SS_PERFORMANCE trials (max 1: the feed would get the body twice)")
    # Facebook native: own caption + close on every video, long cuts in range and on target, 1 text + 1 photo a day
    fb_long, fb_cad = Counter(), {}
    for r in main_rows:
        if r["platform"] != "fb_reels":
            continue
        if r.get("variant") not in ("fb_native", "fb_long") or r.get("caption_source") != "fb_native" or r.get("close_line") != FB_CLOSE:
            err.append(f"{r['file_id']}: Facebook must be a native upload with its own caption and close (no IG cross-post)")
        if r.get("variant") == "fb_long":
            fb_long[(r["page"], r["date"])] += 1
            if not FB_LONG_S[0] <= int(r["seconds"]) <= FB_LONG_S[1]:
                err.append(f"{r['file_id']}: FB long cut {r['seconds']} s outside {FB_LONG_S[0]}-{FB_LONG_S[1]} s")
        fb_cad[(r["page"], r["date"])] = int(r.get("cadence_target") or 0)
    for key, cad in fb_cad.items():
        if fb_long[key] != fb_long_target(cad):
            err.append(f"FB long cuts {key[0]} {key[1]}: {fb_long[key]} != {fb_long_target(cad)}")
    # one text + one photo per FB PAGE per day (the variants CSV carries them under the FB page's name since canon 6;
    # an older per-IG-page CSV is accepted too)
    tp = Counter((AT.fb_page_for(r["page"]) or r["page"], r["date"], r["platform"]) for r in var_rows if r["platform"] in ("fb_text", "fb_photo"))
    for key in {(AT.fb_page_for(k[0]) or k[0], k[1]) for k in fb_cad}:
        for p in ("fb_text", "fb_photo"):
            if tp[(key[0], key[1], p)] < 1:
                err.append(f"{p} {key[0]} {key[1]}: {tp[(key[0], key[1], p)]} < 1")
    return err


def main() -> int:
    plan = os.path.join(DATA, "posting_plan_90d.csv")
    rows = list(csv.DictReader(open(plan))) if os.path.exists(plan) else []
    vpath = os.path.join(DATA, "posting_plan_variants_90d.csv")
    vrows = list(csv.DictReader(open(vpath))) if os.path.exists(vpath) else []
    problems, flags = check_plan(rows)
    # CANON UPDATE 6: the Facebook budget is per FB PAGE over the rows the account plan schedules.
    import account_topology as AT
    apath = AT.ACCOUNTS_CSV
    problems += check_variants(AT.load(apath) if apath.exists() else AT.apply(rows), vrows)
    problems += check_scripts(json.load(open(os.path.join(DATA, "scripts.json"))))
    with open(os.path.join(DATA, "posting_plan_flags.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file_id", "date", "page", "platform", "slot_et", "slot_ok", "prime", "ig_trial_reel"])
        w.writeheader()
        w.writerows(flags)
    ig = [f for f in flags if f["platform"] == "ig_reels"]
    print(f"posting rules: {len(rows)} plan rows, {sum(f['slot_ok'] for f in flags)} inside the 06:00–21:30 ET envelope; "
          f"page-days with a morning + evening prime slot {prime_coverage(flags):.0%}; "
          f"IG trial reels {sum(f['ig_trial_reel'] for f in ig)}/{len(ig)} IG rows; "
          f"Trial Reel TEST rows {sum(r['platform'] == 'ig_trial' for r in vrows)}, FB text/photo rows "
          f"{sum(r['platform'] in ('fb_text', 'fb_photo') for r in vrows)}; problems {len(problems)}")
    for p in problems[:30]:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    if "--ics" in sys.argv:          # SL-26.3: per-page .ics for the launch day and the week (tools/slots_ics.py)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import slots_ics
        sys.exit(slots_ics.main())
    sys.exit(main())
