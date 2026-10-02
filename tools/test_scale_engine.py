"""Scale family R30–R36 (tools/organic_engine.py, BLITZ.md §14).
    python3 -m pytest -q tools/test_scale_engine.py"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "workers"))
import organic_engine as oe  # noqa: E402

def test_r30a_reproduces_the_approved_projection_column_for_column():
    """Every cell of data/projection_aggressive_central.csv (180 days × 37 columns) to its display rounding: integers
    ±0.5, margin ±0.05, and cash_plus_contracted ±1 (the sum of two rounded columns)."""
    ref = list(csv.DictReader(open(os.path.join(ROOT, "data", "projection_aggressive_central.csv"))))
    rows = oe.sc_run(oe.R30A, days=len(ref))
    assert len(rows) == len(ref) == 180
    for w, x in zip(rows, ref):
        for c in oe.SC_CSV_COLS:
            a, e = float(w[c]), float(x[c])
            tol = 1.0 if c == "cash_plus_contracted" else 0.05 if c == "margin_pct" else 0.5
            assert abs(a - e) <= tol + 1e-9, (c, w["day"], a, e)


def test_engine_ladder_gate_and_cap_equal_the_governor_config():
    from growth import config as G
    cfg = G.load()
    rules = [(r["retained_mrr_usd"], r["pages_open"], r["masters_per_page"], r["trial_reels_per_page"], r["generation_tier"])
             for r in cfg["governor"]["scale_rules"]]
    assert rules == oe.SC_LADDER
    assert oe.SC["gate"] == cfg["governor"]["spend_gate"]["retained_mrr_usd"]
    assert oe.SC["cap_share"] == cfg["governor"]["all_in_cap"]["share_of_mrr"]


def test_every_scale_input_is_labelled_with_a_range_and_a_source():
    for key, label, c, lo, hi, unit, src in oe.SC_INPUTS:
        assert label and src and unit is not None
        assert lo <= c <= hi, key


def test_canonical_runs_gate_ladder_and_cap_on_trailing_7_day_retained():
    for r in oe.RUNS_SCALE:
        rows = oe.sc_run(r)
        for i, w in enumerate(rows):
            t7 = sum(x["retained_MRR"] for x in rows[max(0, i - 7):i]) / 7.0
            assert abs(w["metric"] - t7) < 1e-6
            if t7 < 30000:
                assert w["paid_spend"] == 0
            assert w["paid_spend"] <= max(0.0, 0.25 * t7 / 30 - w["fixed"] - w["gen_cost"]) + 1e-9
            if i:
                assert w["level"] >= rows[i - 1]["level"]                 # the ladder never steps down
        if not r["ladder"]:
            assert {w["pages"] for w in rows} == {4}


def test_variant_runs_change_only_what_they_name():
    base = oe.sc_run(oe.R30)
    no_asc = oe.sc_run(oe.R35)
    assert all(abs(a["retained_MRR"] - b["retained_MRR"]) < 1e-6 for a, b in zip(base, no_asc))   # coached never in retained
    assert no_asc[59]["booked_MRR"] < base[59]["booked_MRR"]
    no_fb = oe.sc_run(oe.R36)
    assert all(w["views_fb"] == 0 and w["fb_posts"] == 0 for w in no_fb)
    assert oe.sc_summary(oe.sc_run(oe.R31))["rt100K"] < oe.sc_summary(base)["rt100K"]


def test_appended_csv_columns_match_the_engine_and_old_columns_survive():
    import hashlib
    raw = list(csv.reader(open(os.path.join(ROOT, "mrr_blitz_daily.csv"))))
    # the 69 columns that existed before the scale round (r1…r26, legacy Organic-max r30_MRR…r35_posts) are byte-identical
    assert hashlib.md5(repr([r[:69] for r in raw]).encode()).hexdigest() == "bc953d61ad5072d534be1354f03653db"
    rd = csv.DictReader(open(os.path.join(ROOT, "mrr_blitz_daily.csv")))
    cols = rd.fieldnames
    data = list(rd)
    assert len(cols) == 69 + 5 * len(oe.SC_TAGS)
    for tag, r in zip(oe.SC_TAGS, oe.RUNS_SCALE):
        rows = oe.sc_run(r)
        for k in ("booked_MRR", "retained_MRR", "cash_scale", "views_scale", "posts_scale"):
            assert f"{tag}_{k}" in cols
        for d in (1, 30, 180):
            x = next(z for z in data if int(float(z["day"])) == d)
            assert abs(float(x[f"{tag}_retained_MRR"]) - rows[d - 1]["retained_MRR"]) < 0.01
            assert abs(float(x[f"{tag}_booked_MRR"]) - rows[d - 1]["booked_MRR"]) < 0.01
