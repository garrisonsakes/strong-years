"""Validate data/content/posting_plan_90d.csv. Exit 1 on any violation.

Checks: file uniqueness, uniqueness-group shape (one page, all 6 platforms once, YouTube = distinct cut), each library
script used once network-wide, cadence per page x platform x day, page start dates, CTA ratios (ORGANIC_ENGINE §1.3,
§3.2, §5.2 + the plan's D+7 rule), movement lane only after the performer shoot, 55+ slot window, allocator pillar cap.
CANON UPDATE 4: 4 pages; ONE render per master (one render_id shared by the 4 video files, Threads/X are text);
movement only on demo scripts and <= 1 per page per day (~1 in 6); B-roll ("insert") <= 25% of the day's masters.
Variants (ENGINE_100X §1, §2.1, §5): data/content/posting_plan_variants_90d.csv (Trial Reels + FB text/photo) is
checked together with the placement plan by tools/posting_rules.check_variants (validate_all).
"""
from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_posting_plan as bp  # noqa: E402
import posting_rules as PR  # noqa: E402


def load(path: Path = bp.OUT_CSV) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def validate(rows: list[dict]) -> list[str]:
    err: list[str] = []
    # 1 files
    for fid, c in Counter(r["file_id"] for r in rows).items():
        if c > 1:
            err.append(f"file {fid} used {c}x")
    # 2 groups
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["uniqueness_group"]].append(r)
    for g, rs in groups.items():
        if len({r["page"] for r in rs}) != 1:
            err.append(f"group {g} spans pages")
        plats = Counter(r["platform"] for r in rs)
        if set(plats) != set(bp.PLATFORMS) or max(plats.values()) != 1:
            err.append(f"group {g} platforms {dict(plats)}")
        for r in rs:
            if r["platform"] == "yt_shorts" and r["variant"] != "yt_distinct_cut":
                err.append(f"group {g} YouTube is not a distinct cut")
            if (r["platform"] in ("threads", "x")) != (r["render_lane"] == "carousel_text"):
                err.append(f"{r['file_id']} lane {r['render_lane']} wrong for {r['platform']}")
        rids = {r["render_id"] for r in rs if r["platform"] in bp.VIDEO_PLATFORMS}
        if len(rids) != 1 or "" in rids:
            err.append(f"group {g} has {len(rids)} renders (canon: one render per master)")
    # 3 scripts once network-wide
    s_groups: dict[str, set] = defaultdict(set)
    for r in rows:
        if r["script_id"] != "GEN-needed":
            s_groups[r["script_id"]].add(r["uniqueness_group"])
    for s, gs in s_groups.items():
        if len(gs) > 1:
            err.append(f"script {s} reused in {len(gs)} groups")
    # 4 cadence + start dates
    cnt = Counter((r["page"], r["platform"], int(r["day_index"])) for r in rows)
    for page in bp.PAGES:
        for d in range(bp.D_FIRST, bp.D_LAST + 1):
            want = bp.cadence(page, d)
            for p in bp.PLATFORMS:
                got = cnt.get((page, p, d), 0)
                if got != want:
                    err.append(f"cadence {page} {p} D{d:+d}: {got} != {want}")
    # 5 CTA ratios (per page x platform x day)
    by = defaultdict(list)
    for r in rows:
        by[(r["page"], r["platform"], int(r["day_index"]))].append(r["cta_type"])
    post_launch, offers_post = 0, 0
    for (page, p, d), cts in by.items():
        c = Counter(cts)
        off = c["book"] + c["join"]
        ld = bp.local_d(page, d)          # Spanish page: its own runway/launch clock (CHARACTERS_ES.md); US pages: ld == d
        if ld < 0:
            if off:
                err.append(f"offer CTA in runway {page} {p} D{d:+d}")
            if c["waitlist"] < bp.waitlist_target(len(cts)) or c["waitlist"] > (len(cts) + 1) // 2:
                err.append(f"runway waitlist ratio {page} {p} D{d:+d}: {c['waitlist']}/{len(cts)}")
        else:
            if c["waitlist"]:
                err.append(f"waitlist CTA after D0 {page} {p} D{d:+d}")
            if off > bp.offer_cap(ld):
                err.append(f"offer cap {page} {p} D{d:+d}: {off} > {bp.offer_cap(ld)}")
            post_launch += len(cts)
            offers_post += off
    if post_launch and offers_post / post_launch > 0.20:
        err.append(f"post-launch offer share {offers_post / post_launch:.1%} > 20%")
    # 6 movement lane after the shoot, 7 slot window, 8 pillar cap
    pill = Counter()
    for g, rs in groups.items():
        r = rs[0]
        pill[(r["page"], r["day_index"], r["pillar"])] += 1
    for k, v in pill.items():
        if v > bp.MAX_PER_PILLAR_PER_DAY:
            err.append(f"pillar cap {k}: {v}")
    if set(r["page"] for r in rows) - set(bp.PAGES):
        err.append(f"pages outside the canon roster: {sorted(set(r['page'] for r in rows) - set(bp.PAGES))}")
    scripts = bp.load_all()
    mv, br, day_m = Counter(), Counter(), Counter()
    for g, rs in groups.items():
        r = next((x for x in rs if x["platform"] == "ig_reels"), rs[0])
        d = int(r["day_index"])
        day_m[d] += 1
        if r["render_lane"] == "movement":
            mv[(r["page"], d)] += 1
            s = scripts.get(r["script_id"], {})
            if r["demo"] != "y" or (r["script_id"] != "GEN-needed" and not s.get("has_movement")):
                err.append(f"movement without an exercise demo {g}")
        if r["render_lane"] == "insert":
            br[d] += 1
    for k, v in mv.items():
        if v > bp.MAX_MOVEMENT_PER_PAGE_DAY:
            err.append(f"movement cap {k}: {v} > {bp.MAX_MOVEMENT_PER_PAGE_DAY}")
    for d, v in br.items():
        if v > int(bp.BROLL_SHARE * day_m[d]):
            err.append(f"B-roll cap D{d:+d}: {v} of {day_m[d]} masters > 25%")
    for r in rows:
        if r["render_lane"] == "movement" and int(r["day_index"]) < bp.MOVEMENT_FIRST_POST_D:
            err.append(f"movement before shoot {r['file_id']}")
        if not ("06:30" <= r["slot_et"] <= "21:30"):
            err.append(f"slot outside 55+ window {r['file_id']} {r['slot_et']}")
    return err


def validate_all(rows: list[dict], vrows: list[dict], acc_rows: list[dict] | None = None) -> list[str]:
    import account_topology as AT
    # CANON UPDATE 6 topology: caps per publishing account (1 YT channel, 1 FB page, TikTok accounts != IG pages, Stories).
    acc = acc_rows if acc_rows is not None else AT.apply(rows)
    return validate(rows) + PR.check_variants(acc, vrows) + AT.validate(acc, vrows)


def main() -> int:
    import account_topology as AT
    rows = load()
    vrows = load(bp.VAR_CSV) if bp.VAR_CSV.exists() else []
    acc = AT.load() if AT.ACCOUNTS_CSV.exists() else None
    errs = validate_all(rows, vrows, acc)
    for e in errs[:50]:
        print("FAIL", e)
    print(f"{len(rows)} placements + {len(vrows)} variant rows (Trial Reels, FB text/photo), "
          f"{len({r['uniqueness_group'] for r in rows})} groups: {'OK' if not errs else f'{len(errs)} violations'}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
