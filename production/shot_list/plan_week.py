"""Runway week 1 render/post queue: D-21 … D-15 from data/content/runway_calendar_R21.csv (21-day runway; pass
--calendar for R14/R7). Resolves every script id against data/content/*scripts*.json, writes the queue
(week_queue_D-21_D-15.json + .csv) and validates the selected scripts with the compliance CLI
(`python -m compliance scan … --strict`, deterministic). Exit code 1 if any script blocks or isn't found.
Publishes nothing; the queue feeds the render worker (n8n) or the manual fallback pack.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTENT = ROOT / "data/content"


def scripts_index() -> dict[str, dict]:
    idx = {}
    for p in sorted(CONTENT.glob("*scripts*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        for s in data if isinstance(data, list) else []:
            if isinstance(s, dict) and s.get("id"):
                idx.setdefault(s["id"], {**s, "_file": p.name})
    return idx


def plan(calendar: Path, d_from: int, d_to: int) -> tuple[list[dict], list[str]]:
    idx = scripts_index()
    rows, missing = [], []
    with calendar.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = int(r["D"])
            if not (d_from <= d <= d_to):
                continue
            for part in [x.strip() for x in r["posts"].split("|") if x.strip()]:
                m = re.match(r"^(S\d+)\s*\(([^)]*)\)", part)
                if not m:
                    continue
                sid, tag = m.group(1), m.group(2)
                s = idx.get(sid)
                if not s:
                    missing.append(sid)
                    continue
                rows.append({"D": d, "stage": r["stage"], "page": r["page"], "script_id": sid, "tag": tag,
                             "title": s.get("title"), "speaker": s.get("speaker"), "format": s.get("format"),
                             "hook_line": s.get("hook_line"), "target_seconds": s.get("target_seconds"),
                             "has_movement": s.get("has_movement"), "source": s["_file"],
                             "platforms_per_video": int(r.get("videos_per_platform") or 0),
                             "threads_x_text_posts": int(r.get("threads_x_text_posts") or 0),
                             "status": "queued for render (uniqueness variant per platform at packaging)"})
    return rows, missing


def validate(script_ids: list[str], out_dir: Path) -> dict:
    idx = scripts_index()
    sel = [{k: v for k, v in idx[s].items() if k != "_file"} for s in dict.fromkeys(script_ids)]
    f = out_dir / "week_scripts_for_scan.json"
    f.write_text(json.dumps(sel, ensure_ascii=False), encoding="utf-8")
    rep = out_dir / "week_compliance_report.json"
    proc = subprocess.run([sys.executable, "-m", "compliance", "scan", str(f), "--strict", "--json", str(rep)],
                          cwd=ROOT / "workers", capture_output=True, text=True)
    tail = [ln for ln in proc.stdout.splitlines() if "scripts:" in ln]
    return {"exit_code": proc.returncode, "summary": tail[-1] if tail else proc.stdout[-300:], "report": rep.name, "scripts": len(sel)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calendar", default=str(CONTENT / "runway_calendar_R21.csv"))
    ap.add_argument("--from", dest="d_from", type=int, default=-21)
    ap.add_argument("--to", dest="d_to", type=int, default=-15)
    a = ap.parse_args(argv)
    rows, missing = plan(Path(a.calendar), a.d_from, a.d_to)
    name = f"week_queue_D{a.d_from}_D{a.d_to}"
    v = validate([r["script_id"] for r in rows], HERE)
    out = {"calendar": Path(a.calendar).name, "days": [a.d_from, a.d_to], "videos": len(rows), "missing_scripts": missing,
           "compliance": v, "queue": rows}
    (HERE / f"{name}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (HERE / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["D", "page", "script_id", "tag", "title", "speaker", "format", "target_seconds", "source"])
        for r in rows:
            w.writerow([r["D"], r["page"], r["script_id"], r["tag"], r["title"], r["speaker"], r["format"], r["target_seconds"], r["source"]])
    print(f"{len(rows)} videos D{a.d_from}..D{a.d_to}; missing {missing or 'none'}; compliance: {v['summary']} (exit {v['exit_code']})")
    return 1 if missing or v["exit_code"] != 0 else 0


if __name__ == "__main__":
    sys.exit(main())
