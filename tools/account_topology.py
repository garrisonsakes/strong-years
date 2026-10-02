"""Account topology (BRIEF.md CANON UPDATE 6, Oct 2 2026) applied to the content plan.

The placement plan (posting_plan_90d.csv) is per IG page x platform: every master is packaged for every platform. That is
the CONTENT plan. The ACCOUNT plan here maps each placement to the account that publishes it and applies the real
account caps, because the canon topology is not "one account per platform per page":

  Instagram  4 pages (6 at $30K retained): 6 main + 20 Trial Reels + 3 Stories a day each; Threads 12, X 6 per page.
  TikTok     4 accounts (6 at $30K), SEPARATE from the IG pages, 26 posts a day each (6 masters + 20 cuts/variants).
  Facebook   ONE page to start (2 at $30K): 16 a day = 12 videos + 2 long cuts + 1 text + 1 photo.
  YouTube    ONE Shorts channel: 6 a day (4 until the quota raise; the API default is 10,000 units ~ 6 uploads/day).

So YouTube keeps 4 (6) of the 24 daily masters, Facebook keeps 12 videos + 2 long cuts of the 24 (the rest are "held":
packaged, approved, never scheduled on that account), TikTok rows go to the page's own TikTok account, and 3 Stories
rows per IG page per day are added (poll / question box / link sticker) because Stories are a primary conversion path
(canon 6: 8% of page views, 1.5% link tap, 6% buy). Everything is a config row, not a rebuild (scale-on-MRR ladder).

Output: data/content/posting_plan_accounts_90d.csv (one row per placement, with account, publish y/held, hold_reason) and
Stories rows appended to the variants CSV (platform ig_story). validate_plan.py checks the caps.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "data" / "content"
ACCOUNTS_CSV = CONTENT / "posting_plan_accounts_90d.csv"

# ---- the topology (canon 6). Each entry is a config row; the governor's scale ladder flips `live_from_rung`.
# Chang and Sun never share an account (Garrison, Oct 2): one YT channel and one FB page PER CHARACTER.
PAGE_CHARACTER = {"@changyin": "CHANG", "@changyin.strength": "CHANG", "@sunyoon.kitchen": "SUN", "@sunyoon": "SUN"}
YT_CHANNELS = {"CHANG": "@changyin", "SUN": "@sunyoon"}   # each in its own Google Cloud project = its own quota
YT_PER_DAY_UNTIL_QUOTA_RAISE = 4             # 10,000 units/day default quota per project; the raise request is filed on D0
YT_PER_DAY_AFTER_QUOTA_RAISE = 6
YT_QUOTA_RAISED = False                       # flip when Google approves the extension (LAUNCH_RUNBOOK §11)
FB_PAGES = {"Chang Yin": {"pages": ["@changyin", "@changyin.strength"], "live_from_rung": 0},
            "Sun Yoon": {"pages": ["@sunyoon.kitchen", "@sunyoon"], "live_from_rung": 0}}
FB_VIDEOS_PER_DAY = 12                       # native Reels per FB page
FB_LONG_PER_DAY = 2                          # 60-180 s long cuts per FB page
FB_TEXT_PER_DAY = 1
FB_PHOTO_PER_DAY = 1
TT_ACCOUNTS = {                               # IG page -> its own TikTok account (separate handle, separate login, separate device)
    "@changyin": "@changyin.tt", "@sunyoon.kitchen": "@sunyoon.kitchen.tt", "@sunyoon": "@sunyoon.tt",
    "@changyin.strength": "@changyin.strength.tt",
    "@donchuy": "@donchuy.tt", "@lupe.cocina": "@lupe.cocina.tt", "@chuyylupe": "@chuyylupe.tt",
}
TT_PER_ACCOUNT_DAY = 26                      # 6 masters + 20 cuts (TikTok has no Trial Reels; cuts are ordinary posts)
STORIES_PER_PAGE_DAY = 3
STORY_KINDS = ["poll", "question", "link"]   # one of each, in this order, every day
STORY_SLOTS = ["08:15", "13:15", "19:15"]    # between the main slots; 55+ window


def yt_per_day() -> int:
    return YT_PER_DAY_AFTER_QUOTA_RAISE if YT_QUOTA_RAISED else YT_PER_DAY_UNTIL_QUOTA_RAISE


def fb_page_for(page: str) -> str | None:
    for name, spec in FB_PAGES.items():
        if page in spec["pages"]:
            return name
    return None


def account_for(page: str, platform: str) -> str | None:
    """The publishing account of a (page, platform) placement; None when the platform has no account for that page."""
    if platform in ("ig_reels", "ig_trial", "ig_story", "threads", "x"):
        return page
    if platform == "tiktok":
        return TT_ACCOUNTS.get(page)
    if platform == "yt_shorts":
        return YT_CHANNELS.get(PAGE_CHARACTER.get(page, ""))
    if platform in ("fb_reels", "fb_text", "fb_photo"):
        return fb_page_for(page)
    return None


def _slot_key(r: dict) -> tuple:
    return (int(r["day_index"]), r["slot_et"], r["page"])


def apply(rows: list[dict]) -> list[dict]:
    """Return a copy of every placement row with `account`, `publish` (y|held) and `hold_reason`.

    Per account per day: YouTube keeps yt_per_day() distinct cuts, chosen round-robin across pages in slot order so every
    page's best slot is represented; Facebook keeps FB_VIDEOS_PER_DAY fb_native + FB_LONG_PER_DAY fb_long the same way.
    Held rows stay in the plan (approved content, reusable tomorrow) but are never scheduled on that account.
    """
    out = [dict(r) for r in rows]
    for r in out:
        r["account"] = account_for(r["page"], r["platform"]) or ""
        r["publish"] = "y" if r["account"] else "held"
        r["hold_reason"] = "" if r["account"] else "no account for this platform/page"
    by_day: dict[tuple, list[dict]] = defaultdict(list)
    for r in out:
        if r["publish"] == "y" and r["platform"] in ("yt_shorts", "fb_reels"):
            by_day[(r["account"], r["platform"], r.get("variant", ""), int(r["day_index"]))].append(r)
    for (account, plat, variant, _d), rs in by_day.items():
        if plat == "yt_shorts":
            cap = yt_per_day()
        elif variant == "fb_long":
            cap = FB_LONG_PER_DAY
        else:
            cap = FB_VIDEOS_PER_DAY
        # round-robin across pages: page A slot 1, page B slot 1, ... then slot 2 ...
        per_page: dict[str, list[dict]] = defaultdict(list)
        for r in sorted(rs, key=_slot_key):
            per_page[r["page"]].append(r)
        order: list[dict] = []
        i = 0
        while any(per_page.values()):
            for p in sorted(per_page):
                if i < len(per_page[p]):
                    order.append(per_page[p][i])
            i += 1
            if i > 50:
                break
        for k, r in enumerate(order):
            if k >= cap:
                r["publish"] = "held"
                r["hold_reason"] = f"{plat} cap {cap}/day on {account}" + (" (YouTube quota; 6 after the raise)" if plat == "yt_shorts" and not YT_QUOTA_RAISED else "")
    return out


def stories_rows(rows: list[dict], stage) -> list[dict]:
    """3 Stories per IG page per day (poll, question box, link sticker), in the variants CSV shape."""
    days: dict[tuple, dict] = {}
    for r in rows:
        if r["platform"] == "ig_reels":
            days.setdefault((r["page"], int(r["day_index"])), r)
    out: list[dict] = []
    for (page, d), r in sorted(days.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        code = r["uniqueness_group"].split("-")[1]
        for k in range(STORIES_PER_PAGE_DAY):
            kind = STORY_KINDS[k % len(STORY_KINDS)]
            out.append({"date": r["date"], "day_index": d, "stage": stage(d), "page": page, "platform": "ig_story",
                        "slot_et": STORY_SLOTS[k], "variant_role": "PLACEMENT", "target_group": r["uniqueness_group"],
                        "body_id": "", "hook_id": "", "variant_id": f"ST-{code}-{d:+03d}-{kind}",
                        "file_id": f"ST-{code}-{d:+03d}-{kind}", "ops": f"story_{kind}", "dims_changed": "", "signature": "",
                        "graduation_strategy": "", "seconds": 0, "cost_usd": 0.0, "script_id": r["script_id"],
                        "pillar": r["pillar"], "hook_grammar": r["hook_grammar"],
                        "cta_keyword": r["cta_keyword"] if kind == "link" else ""})
    return out


def fb_text_photo_rows(vrows: list[dict]) -> list[dict]:
    """Collapse the per-IG-page fb_text / fb_photo rows to one of each per FB PAGE per day (canon 6: one FB page)."""
    seen: set[tuple] = set()
    out: list[dict] = []
    for r in vrows:
        if r["platform"] in ("fb_text", "fb_photo"):
            acct = fb_page_for(r["page"])
            key = (acct, r["platform"], int(r["day_index"]))
            if not acct or key in seen:
                continue
            seen.add(key)
            r = dict(r)
            r["page"] = acct
            out.append(r)
        else:
            out.append(r)
    return out


def summary(acc_rows: list[dict], vrows: list[dict], day: int = 1) -> dict:
    """Posts per account on one day (what a human poster or W4 schedules)."""
    c: Counter = Counter()
    for r in acc_rows:
        if int(r["day_index"]) == day and r["publish"] == "y":
            c[(r["account"], r["platform"])] += 1
    for r in vrows:
        if int(r["day_index"]) == day:
            c[(account_for(r["page"], r["platform"]) or r["page"], r["platform"])] += 1
    return {f"{a}|{p}": n for (a, p), n in sorted(c.items())}


def validate(acc_rows: list[dict], vrows: list[dict]) -> list[str]:
    err: list[str] = []
    per: Counter = Counter()
    for r in acc_rows:
        if r["publish"] != "y":
            continue
        per[(r["account"], r["platform"], r.get("variant", ""), int(r["day_index"]))] += 1
        if r["platform"] == "tiktok" and r["account"] == r["page"]:
            err.append(f"tiktok account equals the IG page handle for {r['file_id']} (canon 6: separate accounts)")
    for (account, plat, variant, d), n in per.items():
        if plat == "yt_shorts" and (account not in YT_CHANNELS.values() or n > yt_per_day()):
            err.append(f"youtube D{d:+d}: {n} on {account} > {yt_per_day()} (one channel per character; quota)")
        if plat == "fb_reels" and variant == "fb_long" and n > FB_LONG_PER_DAY:
            err.append(f"facebook long cuts D{d:+d}: {n} > {FB_LONG_PER_DAY} on {account}")
        if plat == "fb_reels" and variant != "fb_long" and n > FB_VIDEOS_PER_DAY:
            err.append(f"facebook videos D{d:+d}: {n} > {FB_VIDEOS_PER_DAY} on {account}")
    yt_days = Counter(int(r["day_index"]) for r in acc_rows if r["publish"] == "y" and r["platform"] == "yt_shorts")
    for d, n in yt_days.items():
        if n > yt_per_day() * len(YT_CHANNELS):
            err.append(f"youtube network D{d:+d}: {n} > {yt_per_day() * len(YT_CHANNELS)}")
    st: Counter = Counter()
    kinds: dict[tuple, set] = defaultdict(set)
    for r in vrows:
        if r["platform"] == "ig_story":
            st[(r["page"], int(r["day_index"]))] += 1
            kinds[(r["page"], int(r["day_index"]))].add(r["ops"])
    ig_days = {(r["page"], int(r["day_index"])) for r in acc_rows if r["platform"] == "ig_reels"}
    for key in ig_days:
        if st.get(key, 0) != STORIES_PER_PAGE_DAY or kinds.get(key) != {f"story_{k}" for k in STORY_KINDS}:
            err.append(f"stories {key}: {st.get(key, 0)} rows, kinds {sorted(kinds.get(key, []))} (want 3: poll, question, link)")
    fbtp: Counter = Counter((r["page"], r["platform"], int(r["day_index"])) for r in vrows if r["platform"] in ("fb_text", "fb_photo"))
    for (acct, plat, d), n in fbtp.items():
        if acct not in FB_PAGES or n > 1:
            err.append(f"{plat} D{d:+d}: {n} on {acct} (one per FB page per day)")
    return err


AFIELDS_EXTRA = ["account", "publish", "hold_reason"]


def write(acc_rows: list[dict], fields: list[str], path: Path = ACCOUNTS_CSV) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields + AFIELDS_EXTRA)
        w.writeheader()
        w.writerows(acc_rows)


def load(path: Path = ACCOUNTS_CSV) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


if __name__ == "__main__":
    acc = load()
    print(json.dumps(summary(acc, [], 1), indent=1))
