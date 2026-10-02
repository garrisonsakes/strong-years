#!/usr/bin/env python3
"""
organic_max_sheet.py — writes the Organic-max family (R30–R35, tools/organic_engine.py main_max) into
economics.xlsx sheet `Organic_Max` (created or replaced; every other sheet is left untouched and verified) and
appends r20/r30…r35 views/posts and r30…r35 MRR/cash columns to mrr_blitz_daily.csv (existing columns unchanged).

    python3 tools/organic_max_sheet.py

Sheet layout: inputs (row 5+), run table (formulas over the daily block), solver, ascension, sensitivity,
3-way comparison, sources; daily block from row DAILY0 (day, then MRR / views / posts / cash per run).
"""
import csv, hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
import organic_engine as oe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX = os.path.join(ROOT, "economics.xlsx")
CSV = os.path.join(ROOT, "mrr_blitz_daily.csv")
SHEET = "Organic_Max"
DAILY0 = 260           # header row of the daily block; day 1 on DAILY0 + 1
TAGS = ["r20", "r30", "r31", "r32", "r33", "r34", "r35"]
B = Font(bold=True)
HEAD = PatternFill("solid", fgColor="000000"); HF = Font(bold=True, color="FFFFFF")


def snapshot(wb, skip):
    h = {}
    for ws in wb.worksheets:
        if ws.title == skip:
            continue
        m = hashlib.md5()
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    m.update(f"{c.coordinate}={c.value!r};".encode())
        h[ws.title] = (m.hexdigest(), ws.max_row, ws.max_column)
    return h


def hdr(ws, r, vals):
    for j, v in enumerate(vals, 1):
        c = ws.cell(r, j, v); c.font = HF; c.fill = HEAD; c.alignment = Alignment(wrap_text=True, vertical="top")


def main():
    out = oe.main_max()
    res = out["res"]
    series = {"r20": out["rows20"]}
    for tag, x in zip(TAGS[1:], res):
        series[tag] = x[1]

    # ---------------- csv ----------------
    with open(CSV, newline="") as f:
        rd = csv.DictReader(f); fields = list(rd.fieldnames); data = list(rd)
    new = ["r20_views", "r20_posts"] + [f"{t}_{k}" for k in ("MRR", "cash", "views", "posts") for t in TAGS[1:]]
    fields += [c for c in new if c not in fields]
    byday = {int(float(x["day"])): x for x in data}
    for tag, rows in series.items():
        for d in rows:
            x = byday.get(d["d"])
            if x is None:
                continue
            if tag != "r20":
                x[f"{tag}_MRR"] = f"{d['mrr']:.2f}"; x[f"{tag}_cash"] = f"{d['cash']:.2f}"
            x[f"{tag}_views"] = f"{d['views']:.0f}"; x[f"{tag}_posts"] = f"{d['posts']:.1f}"
    with open(CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(data)

    # ---------------- workbook ----------------
    wb = openpyxl.load_workbook(XLSX)
    before = snapshot(wb, SHEET)
    if SHEET in wb.sheetnames:
        del wb[SHEET]
    ws = wb.create_sheet(SHEET)
    ws.column_dimensions["A"].width = 46; ws.column_dimensions["B"].width = 60
    for j in range(3, 30):
        ws.column_dimensions[L(j)].width = 12
    ws["A1"] = "Organic-max plan: 80 Trial Reels/day, $0 media (runs R30–R35; engine tools/organic_engine.py main_max; writer tools/organic_max_sheet.py; BLITZ.md §14)"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = ("Every input is labelled; ASSUMPTION = no published source. MRR = membership MRR only (cell B members at $25 contracted). "
                "Ascension (coached, labs, supplements) is reported separately and never added to MRR. Cash in R34/R35 includes ascension contribution. "
                "Result cells in the run table are formulas over the daily block from row %d." % DAILY0)
    ws["A2"].alignment = Alignment(wrap_text=True)

    # daily block first (formulas point at it)
    cols = {}
    hdrs = ["day"]
    for k in ("MRR", "views", "posts", "cash"):
        for t in TAGS:
            cols[(t, k)] = len(hdrs) + 1; hdrs.append(f"{t}_{k}")
    ws.cell(DAILY0 - 1, 1, "Daily series (day 1 = checkout opens). r20 = current plan for reference.").font = B
    hdr(ws, DAILY0, hdrs)
    for i in range(360):
        r = DAILY0 + 1 + i
        ws.cell(r, 1, i + 1)
        for t in TAGS:
            d = series[t][i]
            ws.cell(r, cols[(t, "MRR")], round(d["mrr"], 2)); ws.cell(r, cols[(t, "views")], round(d["views"]))
            ws.cell(r, cols[(t, "posts")], round(d["posts"], 1)); ws.cell(r, cols[(t, "cash")], round(d["cash"], 2))
    last = DAILY0 + 360
    rng = lambda t, k: f"${L(cols[(t, k)])}${DAILY0 + 1}:${L(cols[(t, k)])}${last}"

    # inputs
    r = 4
    ws.cell(r, 1, "1. New inputs (central / upside)").font = B; r += 1
    hdr(ws, r, ["key", "label", "central", "upside", "unit", "source / rationale"]); r += 1
    for k, lab, c, u, unit, src in oe.MX_INPUTS:
        for j, v in enumerate([k, lab, str(c) if not isinstance(c, (int, float)) else c, str(u) if not isinstance(u, (int, float)) else u, unit, src], 1):
            ws.cell(r, j, v).alignment = Alignment(wrap_text=True, vertical="top")
        r += 1

    # run table with formulas
    r += 1
    ws.cell(r, 1, "2. Runs (formulas over the daily block; cf+ / breakeven / retained / cost are engine values)").font = B; r += 1
    hdr(ws, r, ["run", "description", "posts/day d30", "views/day d1", "views/day d30", "views/day d90", "MRR d4", "MRR d14", "MRR d30", "MRR d60",
                "MRR d90", "MRR d180", "retained d30", "$10K day", "$50K day", "$100K day", "cash low", "low day", "cf+ day", "breakeven day", "cost/day d30", "seeded waitlist"]); r += 1
    allruns = [("r20", "R20 (CURRENT reference)", out["s20"])] + [(t, x[0]["name"], x[5]) for t, x in zip(TAGS[1:], res)]
    for t, nm, sm in allruns:
        ws.cell(r, 1, t.upper()); ws.cell(r, 2, nm).alignment = Alignment(wrap_text=True, vertical="top")
        mr, vr, pr, cr = rng(t, "MRR"), rng(t, "views"), rng(t, "posts"), rng(t, "cash")
        ws.cell(r, 3, f"=INDEX({pr},30)"); ws.cell(r, 4, f"=INDEX({vr},1)"); ws.cell(r, 5, f"=INDEX({vr},30)"); ws.cell(r, 6, f"=INDEX({vr},90)")
        for j, d in zip(range(7, 13), (4, 14, 30, 60, 90, 180)):
            ws.cell(r, j, f"=INDEX({mr},{d})")
        ws.cell(r, 13, round(sm["ret30"], 2))
        for j, tgt in zip((14, 15, 16), (10000, 50000, 100000)):
            ws.cell(r, j, f'=IFERROR(MATCH(TRUE,INDEX({mr}>={tgt},0),0),"none")')
        ws.cell(r, 17, f"=MIN({cr})"); ws.cell(r, 18, f"=MATCH(MIN({cr}),{cr},0)")
        ws.cell(r, 19, sm["cfpos"] if sm["cfpos"] < 999 else "none"); ws.cell(r, 20, sm["beday"] if sm["beday"] < 999 else "none")
        ws.cell(r, 21, round(sm["cost30"], 2)); ws.cell(r, 22, round(sm.get("seed", 0)))
        r += 1
    u = out["r34u"]
    ws.cell(r, 1, "R34U"); ws.cell(r, 2, "R34 with every organic input at upside (values)")
    for j, v in zip(range(3, 23), [u["p30"], u["v1"], u["v30"], u["v90"], u["m4"], u["m14"], u["m30"], None, u["m90"], u["m180"], u["ret30"], u["d10"], u["d50"], u["d100"], u["low"], u["lowday"], u["cfpos"], u["beday"], u["cost30"], 0]):
        ws.cell(r, j, round(v, 2) if isinstance(v, float) else v)
    r += 2

    # solver
    sol, ref = out["sol"], out["sol_ref"]
    ws.cell(r, 1, "3. Solver: organic input REQUIRED (one at a time, all others at R34 central) for $100K MRR by day 30 with $0 media").font = B; r += 1
    hdr(ws, r, ["input", "central", "upside", "required", "required ÷ central", "required ÷ upside", "note"]); r += 1
    vpt = ref["vpt30"]; dmr = ref["dm_rate"]
    rows = [
        ("Views per Trial Reel at day 30 (mean, after decay)", vpt, vpt * oe.MXU["tr_rel"] / oe.MXC["tr_rel"], vpt * sol["tr_rel"] / oe.MXC["tr_rel"] if sol["tr_rel"] else None, "tr_rel solved"),
        ("Graduation rate (share of trials → feed)", oe.MXC["grad_rate"], oe.MXU["grad_rate"], sol["grad_rate"], "not reachable even at 100% (graduates are capped by 6 feed slots/page)" if sol["grad_rate"] is None else ""),
        ("Graduate uplift at 100% graduation", oe.MXC["grad_up"], oe.MXU["grad_up"], sol["grad_both"], "every feed post a graduate"),
        ("DM→purchase per keyword commenter (open × click × load × conversion × subB × intent)", dmr, dmr * oe.MXU["dm_mult"], dmr * sol["dm_mult"] if sol["dm_mult"] else None, "vendor band 2–5% unqualified, 12–25% qualified (V-)"),
        ("Landing visitor → $12 subscription purchase (cvr_org, before subB)", 0.05, 0.08, sol["cvr_org"], "tripwire benchmarks 1.5–15%"),
        ("Seeded waitlist on day 1 (names)", 0, oe.MXU["seed_opt"] * (100000 + 50000 * 0.35), sol["seed_wl"], "R35 default lists seed %d" % round(oe.prep(oe.R35)["seed_wl"])),
        ("Organic reach multiplier (all lanes); views/day d30", ref["v30"], ref["v30"] * 1.75, ref["v30"] * sol["reach"] if sol["reach"] else None, "×%.2f central reach" % sol["reach"] if sol["reach"] else ""),
    ]
    for nm, c, up, req, note in rows:
        ws.cell(r, 1, nm); ws.cell(r, 2, c); ws.cell(r, 3, up); ws.cell(r, 4, req if req is not None else "not reachable")
        if req is not None and c:
            ws.cell(r, 5, f"=D{r}/B{r}")
        if req is not None and up:
            ws.cell(r, 6, f"=D{r}/C{r}")
        ws.cell(r, 7, note); r += 1
    r += 1

    # ascension
    ws.cell(r, 1, "4. Ascension lines (NOT MRR)").font = B; r += 1
    hdr(ws, r, ["run", "supplement MRR d90", "supplement MRR d180", "coached run-rate d90 ($/mo)", "coached run-rate d180", "labs gross cumulative d180"]); r += 1
    for t, x in zip(TAGS[1:], res):
        sm = x[5]
        if "supp90" in sm:
            for j, v in enumerate([t.upper(), sm["supp90"], sm["supp180"], sm["coach90"], sm["coach180"], sm["labs180"]], 1):
                ws.cell(r, j, round(v) if isinstance(v, float) else v)
            r += 1
    r += 1

    # sensitivity
    ws.cell(r, 1, "5. Sensitivity (FLAG = moves day-30 MRR by > $5K)").font = B; r += 1
    hdr(ws, r, ["base", "change", "MRR d30", "Δ d30", "retained d30", "MRR d90", "MRR d180", "cash low", "$100K day", "flag"]); r += 1
    for x in out["sens"]:
        sm = x["summ"]
        for j, v in enumerate([x["base"], x["name"], sm["m30"], x["d30_delta"], sm["ret30"], sm["m90"], sm["m180"], sm["low"], sm["d100"], "FLAG" if x["flag"] else None], 1):
            ws.cell(r, j, round(v, 2) if isinstance(v, float) else v)
        r += 1
    r += 1

    # comparison
    o_rows, osm = out["orig"]; _, oym = out["orig_ym"]; s20 = out["s20"]; s34 = res[4][5]; s35 = res[5][5]
    ws.cell(r, 1, "6. 3-way comparison").font = B; r += 1
    hdr(ws, r, ["measure", "ORIGINAL (YM-style, 1 page, 3/day, $19.99 ebook + Whop)", "ORIGINAL at YM launch-era reach ×12.8", "CURRENT (R20)", "UPDATED R34", "UPDATED R35"]); r += 1
    rows20 = out["rows20"]; rows34 = res[4][1]; rows35 = res[5][1]
    comp = [
        ("posts/day (d30)", 3, 3, s20["p30"], s34["p30"], s35["p30"]),
        ("views/day d30", osm["v30"], oym["v30"], s20["v30"], s34["v30"], s35["v30"]),
        ("views/day d90", osm["v90"], oym["v90"], s20["v90"], s34["v90"], s35["v90"]),
        ("MRR d30", osm["m30"], oym["m30"], s20["m30"], s34["m30"], s35["m30"]),
        ("MRR d90", osm["m90"], oym["m90"], s20["m90"], s34["m90"], s35["m90"]),
        ("MRR d180", osm["m180"], oym["m180"], s20["m180"], s34["m180"], s35["m180"]),
        ("cost/day (d30)", osm["cost"], oym["cost"], s20["cost30"], s34["cost30"], s35["cost30"]),
        ("breakeven day (cumulative cash ≥ 0)", osm["be"], oym["be"], s20["beday"], s34["beday"], s35["beday"]),
        ("features (SYSTEM_RECAP §2 rows; ORIGINAL = observed)", 8, 8, 79, 98, 98),
    ]
    for row in comp:
        for j, v in enumerate(row, 1):
            ws.cell(r, j, round(v, 1) if isinstance(v, float) else v)
        r += 1
    ws.cell(r, 1, "ORIGINAL cost = 3 posts × $1.12 + $16/day tools (no team opex); with our $30.5K/month opex it never breaks even. CURRENT/UPDATED cost includes $1,017/day fixed opex.").alignment = Alignment(wrap_text=True)
    r += 2

    ws.cell(r, 1, "7. Sources").font = B; r += 1
    for nm, src in oe.MX_SOURCES:
        ws.cell(r, 1, nm); ws.cell(r, 2, src); r += 1
    assert r < DAILY0 - 2, f"layout overflow: row {r} reaches the daily block"
    wb.save(XLSX)

    # verify other sheets untouched
    wb2 = openpyxl.load_workbook(XLSX)
    after = snapshot(wb2, SHEET)
    assert before == after, "another sheet changed"
    print("Organic_Max written; other sheets verified identical:", len(after), "sheets")


if __name__ == "__main__":
    main()
