"""Summary tables for POSTING_PLAN.md from data/content/posting_plan_90d.csv (prints markdown)."""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_posting_plan as bp  # noqa: E402

REVIEW_S = 20                 # human review seconds per judged post (brief)
ASSEMBLY_MIN_PER_FILE = 1.5   # [A] ffmpeg assembly CPU-minutes per packaged video file on the VPS
LEAD_DAYS = 2                 # briefs ready 48 h ahead (ORGANIC_ENGINE §6.2)
CANON_LIB = 190               # unique scripts (S01-S190); runway_scripts.json = S151-S190 again (40)


def gen_seconds(lane: str, s: int) -> dict:
    """Generated seconds per master by provider (mirrors COSTS.md lane recipes, before retake factors)."""
    if lane == "talking_head":
        return {"lipsync": s + 8, "motion": 0, "insert": 16}
    if lane == "movement":
        return {"lipsync": 0.4 * s + 8, "motion": 0.6 * s, "insert": 8}
    if lane == "insert":
        return {"lipsync": 0, "motion": 0, "insert": 24}
    return {"lipsync": 0, "motion": 0, "insert": 0}


def main() -> None:
    rows = list(csv.DictReader(bp.OUT_CSV.open(encoding="utf-8")))
    pages = list(bp.PAGES)
    g = {}
    for r in rows:
        g.setdefault(r["uniqueness_group"], r)
    masters = list(g.values())
    out = []
    P = out.append

    # posts/day per page (phase table)
    P("### Posts per day (all 6 platforms) by phase\n")
    phases = [(-7, -5), (-4, -1), (0, 6), (7, 14), (15, 17), (18, 21), (22, 24), (25, 28), (29, 29), (30, 36), (37, 90)]
    cnt = Counter((r["page"], int(r["day_index"])) for r in rows)
    P("| Days | Dates | " + " | ".join(pages) + " | Total/day | Per platform per page |")
    P("|---|---|" + "---|" * (len(pages) + 2))
    for a, b in phases:
        vals = [cnt.get((p, a), 0) for p in pages]
        per = sorted({bp.cadence(p, a) for p in pages if bp.cadence(p, a)})
        da, db = bp.D0 + timedelta(days=a), bp.D0 + timedelta(days=b)
        P(f"| D{a:+d}…D{b:+d} | {da:%b %d}–{db:%b %d} | " + " | ".join(str(v) for v in vals) + f" | **{sum(vals)}** | {'/'.join(map(str, per))} |")
    # posts/month
    P("\n### Posts per month per page (all platforms)\n")
    mon = Counter((r["page"], r["date"][:7]) for r in rows)
    months = sorted({r["date"][:7] for r in rows})
    P("| Page | " + " | ".join(months) + " | Total |")
    P("|---|" + "---|" * (len(months) + 1))
    for p in pages:
        v = [mon.get((p, m), 0) for m in months]
        P(f"| {p} | " + " | ".join(f"{x:,}" for x in v) + f" | {sum(v):,} |")
    tv = [sum(mon.get((p, m), 0) for p in pages) for m in months]
    P("| **Total** | " + " | ".join(f"**{x:,}**" for x in tv) + f" | **{sum(tv):,}** |")
    P(f"\n({months[0]} starts Oct 1 = D−7; {months[-1]} ends Jan 6 = D+90.) Platform split: every page posts the same count on all 6 platforms.\n")

    # scripts needed vs available
    P("### Source scripts needed vs available\n")
    by_d = defaultdict(Counter)
    for m in masters:
        by_d[int(m["day_index"])]["need"] += 1
        by_d[int(m["day_index"])]["gen" if m["script_id"] == "GEN-needed" else "lib"] += 1
    first_gen = {}
    for m in sorted(masters, key=lambda x: int(x["day_index"])):
        if m["script_id"] == "GEN-needed":
            first_gen.setdefault(m["page"], int(m["day_index"]))
    lib_by_page = Counter(m["page"] for m in masters if m["script_id"] != "GEN-needed")
    P("| Page | Library scripts (used) | First GEN-needed day | build_content.py must deliver by | GEN scripts D−7…D+90 |")
    P("|---|---|---|---|---|")
    gen_by_page = Counter(m["page"] for m in masters if m["script_id"] == "GEN-needed")
    for p in pages:
        fg = first_gen.get(p)
        due = fg - LEAD_DAYS if fg is not None else None
        P(f"| {p} | {lib_by_page[p]} | D{fg:+d} ({bp.D0 + timedelta(days=fg):%b %d}) | D{due:+d} ({bp.D0 + timedelta(days=due):%b %d}) | {gen_by_page[p]:,} |")
    P(f"| **Network** | **{sum(lib_by_page.values())}** of {CANON_LIB} | **D{min(first_gen.values()):+d}** | **D{min(first_gen.values()) - LEAD_DAYS:+d} (tonight)** | **{sum(gen_by_page.values()):,}** |")
    P("\n| Days | Scripts needed/day | From library/day | GEN-needed/day | Cumulative GEN backlog at end |")
    P("|---|---|---|---|---|")
    cum = 0
    for a, b in phases:
        need = sum(by_d[d]["need"] for d in range(a, b + 1))
        lib = sum(by_d[d]["lib"] for d in range(a, b + 1))
        gen = sum(by_d[d]["gen"] for d in range(a, b + 1))
        cum += gen
        n = b - a + 1
        P(f"| D{a:+d}…D{b:+d} | {need / n:.1f} | {lib / n:.1f} | {gen / n:.1f} | {cum:,} |")

    # review + render
    P("\n### Human review and render load\n")
    P("| Days | Posts/day | Human review min/day (20 s/post) | Generated s/day: lip-sync · motion control · Veo inserts | Output video min/day (all video files) | Assembly CPU-min/day |")
    P("|---|---|---|---|---|---|")
    perday = defaultdict(lambda: Counter())
    for r in rows:
        d = int(r["day_index"])
        perday[d]["posts"] += 1
        if r["platform"] in bp.VIDEO_PLATFORMS:
            perday[d]["vid_s"] += int(r["seconds"])
            perday[d]["files"] += 1
    gens = defaultdict(Counter)
    vrow = {}  # lanes come from each group's IG row (the group's first row is a text platform only if mis-ordered)
    for r in rows:
        if r["platform"] == "ig_reels":
            vrow[r["uniqueness_group"]] = r
    for r in vrow.values():
        for k, v in gen_seconds(r["render_lane"], int(r["seconds"])).items():
            gens[int(r["day_index"])][k] += v
    for a, b in phases:
        n = b - a + 1
        def avg(f):
            return sum(f(d) for d in range(a, b + 1)) / n
        P(f"| D{a:+d}…D{b:+d} | {avg(lambda d: perday[d]['posts']):.0f} | {avg(lambda d: perday[d]['posts']) * REVIEW_S / 60:.0f} | "
          f"{avg(lambda d: gens[d]['lipsync']):,.0f} · {avg(lambda d: gens[d]['motion']):,.0f} · {avg(lambda d: gens[d]['insert']):,.0f} | "
          f"{avg(lambda d: perday[d]['vid_s']) / 60:,.0f} | {avg(lambda d: perday[d]['files']) * ASSEMBLY_MIN_PER_FILE:,.0f} |")
    lanes = Counter(r["render_lane"] for r in vrow.values() if int(r["day_index"]) >= 7)
    tot = sum(lanes.values())
    P(f"\nLane mix of masters D+7…D+90: " + ", ".join(f"{k} {v / tot:.0%}" for k, v in lanes.most_common()))
    ctas = Counter(r["cta_type"] for r in rows)
    P("CTA mix of all posts: " + ", ".join(f"{k} {v:,} ({v / len(rows):.1%})" for k, v in ctas.most_common()))
    json.dump({"lane_mix_d7_plus": {k: v / tot for k, v in lanes.items()}}, open(bp.ROOT / "data/content/posting_plan_lane_mix.json", "w"), indent=1)
    print("\n".join(out))


if __name__ == "__main__":
    main()
