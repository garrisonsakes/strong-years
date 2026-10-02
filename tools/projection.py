#!/usr/bin/env python3
"""Projection of record, rebuilt as code (the v5 CSV in data/projection_master.csv was committed without its
generator). Formulas follow CLAUDE.md "v5 inputs"; `--scenario v5` reproduces the CSV's funnel within rounding.

  python3 tools/projection.py [--scenario v5|launch] [--days 90] [--csv out.csv]

Scenarios
  v5      the committed model: 300 posts from day 1, $12 front end that always includes the trial, coached from d10.
  launch  CANON 7 + Oct 2 decisions: real D1-D7 account ramp (tools/topology.py), $19.99 front end with the
          membership trial as the default choice (TAKE of buyers keep it), a price-elasticity haircut on the
          purchase rate for $12 -> $19.99, no seat cap, coaching deferred to day 30.

Every number marked [A] is an assumption to replace with test data (the price split tests).
"""
from __future__ import annotations

import argparse
import csv
import math
import sys

HIT = 1 + 40 / 150
MULT = {"ig": 1.0, "tt": 0.7, "fb": 0.8, "yt": 0.5, "thx": 0.15}
FEE = 0.029                    # card processing on every charge
NET_MEMBER = 23.84             # v5 booked $ per member-month (= $25 net of fees/reserve, as in the CSV)


def views_per_video(d: int) -> float:
    ramp = {1: 500, 2: 750, 3: 1000, 4: 1500, 5: 2000, 6: 2500, 7: 3000, 8: 3500, 9: 4000, 10: 5000}
    v = ramp.get(d) or (min(9000, 5000 + 1000 * (d - 10)) if d <= 14 else 10000)
    return v * HIT


def mix_full(rung: bool) -> dict:
    p = 6 if rung else 4
    return {"ig": p * 26, "stories": p * 3, "thx": p * 18, "tt": p * 26, "fb": 32 if rung else 16, "yt": 4}


# tools/topology.py D1..D7 per FB page / YT channel (4 IG, 4 TT; FB and YT doubled per character in run()), then steady state
RAMP = {1: {"ig": 8, "stories": 4, "thx": 20, "tt": 4, "fb": 3, "yt": 1},
        2: {"ig": 20, "stories": 8, "thx": 36, "tt": 12, "fb": 6, "yt": 2},
        3: {"ig": 36, "stories": 12, "thx": 48, "tt": 24, "fb": 9, "yt": 3},
        4: {"ig": 60, "stories": 12, "thx": 60, "tt": 40, "fb": 11, "yt": 4},
        5: {"ig": 84, "stories": 12, "thx": 72, "tt": 64, "fb": 14, "yt": 4},
        6: {"ig": 104, "stories": 12, "thx": 72, "tt": 80, "fb": 16, "yt": 4},
        7: {"ig": 104, "stories": 12, "thx": 72, "tt": 104, "fb": 16, "yt": 4}}

SCEN = {
    "v5": dict(ramp=False, front=12.0, take=1.0, elastic=1.0, coached_from=10, books_only_front=12.0),
    "ramp12": dict(ramp=True, front=12.0, take=1.0, elastic=1.0, coached_from=30, books_only_front=12.0),
    "launch": dict(ramp=True, front=19.99, take=0.65, elastic=0.80, coached_from=30, books_only_front=19.99),
}


def run(name: str, days: int = 90) -> list[dict]:
    s = SCEN[name]
    out, trials, paying, coached, cash, rung = [], [], 0.0, 0.0, 0.0, False   # no pre-launch spend (Garrison, Oct 2)
    for d in range(1, days + 1):
        m = RAMP[d] if (s["ramp"] and d in RAMP) else mix_full(rung)
        if not s["ramp"] and d >= 8:
            m = dict(m, yt=6)
        if s["ramp"]:   # Oct 2: one FB page and one YT channel PER CHARACTER (Chang and Sun never share an account)
            m = dict(m, fb=m["fb"] * 2, yt=m["yt"] * 2)
        vpv = views_per_video(d)
        v_ig = m["ig"] * vpv
        v_st = 0.08 * v_ig
        v_rest = vpv * (m["tt"] * MULT["tt"] + m["fb"] * MULT["fb"] + m["yt"] * MULT["yt"] + m["thx"] * MULT["thx"])
        views = v_ig + v_st + v_rest
        feed = views - v_st
        dm_land = feed * 0.0015 * 0.15 * 0.95 * 0.45 * 0.70
        bio_land = feed * 0.002 * 0.70
        st_land = v_st * 0.015 * 0.70
        organic = (dm_land * 0.08 + bio_land * 0.04 + st_land * 0.06) * s["elastic"]
        seeded = (1500 * 0.10 / 3 if d <= 3 else 0) + (30000 * 0.015 / 14 if d <= 14 else 0)
        buyers = organic + seeded * s["elastic"]
        new_trials = buyers * s["take"]
        upfront = new_trials * s["front"] + (buyers - new_trials) * s["books_only_front"]
        trials.append((d, new_trials))
        converting = sum(n for (dd, n) in trials if dd + 7 == d) * 0.60
        paying = paying * (1 - 0.07 / 30) + converting
        in_trial = sum(n for (dd, n) in trials if d - 7 < dd <= d)
        renew = converting * 25 + paying * 25 / 30            # day-7 first charges + daily share of renewals
        if d >= s["coached_from"]:
            coached = coached * (1 - 0.07 / 30) + 0.05 * converting
        booked = (in_trial + paying) * NET_MEMBER + coached * 147
        retained = (in_trial * 0.60 + paying) * NET_MEMBER + coached * 147
        cash_in = (upfront + renew + coached * 147 / 30) * (1 - FEE)
        posts = sum(m.values())
        cost = 17.4 + 0.272 * posts          # v5 calibration: $99/day at 300 posts, $142/day at 458 (renders + review + fixed)
        cash += cash_in - cost
        if retained >= 30000:
            rung = True
        out.append({"day": d, "posts": posts, "views": round(views), "buyers": round(buyers, 1),
                    "new_trials": round(new_trials, 1), "upfront_cash": round(upfront), "in_trial": round(in_trial),
                    "paying": round(paying), "booked_MRR": round(booked), "retained_MRR": round(retained),
                    "cash_in": round(cash_in), "cost": round(cost, 1), "cash_cum": round(cash)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="launch", choices=sorted(SCEN))
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--csv")
    a = ap.parse_args(argv)
    rows = run(a.scenario, a.days)
    if a.csv:
        with open(a.csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    for r in rows:
        if r["day"] in (1, 2, 3, 4, 7, 8, 14, 15, 21, 28, 30, 45, 60, 90):
            print(" ".join(f"{k}={v}" for k, v in r.items()))
    for t in (10000, 30000, 100000, 250000):
        hit = next((r["day"] for r in rows if r["retained_MRR"] >= t), None)
        print(f"retained ${t // 1000}K: day {hit}")
    first_pos = next((r["day"] for r in rows if r["cash_in"] > r["cost"]), None)
    be = next((r["day"] for r in rows if r["cash_cum"] >= 0), None)
    print(f"daily cash positive from day {first_pos}; cumulative cash positive from day {be}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
