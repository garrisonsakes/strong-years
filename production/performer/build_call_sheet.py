"""Performer call sheet for the driving-video shoot: all 205 clips from products/VIDEO_PRODUCTION_QUEUE.json
(driving_clip_shotlist), grouped by set and equipment so props move once, with a running schedule.
Writes call_sheet.csv and call_sheet.html (printable, black on white).
"""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MIN_PER_CLIP = 2.0          # 3 angles (front / 45° / side) x 10-20 s + A-pose + reset
START_MIN = 8 * 60          # 08:00 call
BREAK_EVERY = 50            # minutes of shooting between 10-minute breaks
LUNCH_AT = 12 * 60 + 30


def clips() -> list[dict]:
    q = json.loads((ROOT / "products/VIDEO_PRODUCTION_QUEUE.json").read_text(encoding="utf-8"))
    order = {"SET-GARAGE": 0, "SET-STOOP": 1, "SET-YARD": 2, "SET-PROM": 3, "SET-LIVING": 4, "SET-BED": 5, "SET-KITCHEN": 6}
    vers = {"easier": 0, "main": 1, "harder": 2}
    return sorted(q["driving_clip_shotlist"], key=lambda c: (order.get(c.get("set_for_blocking"), 9), c.get("equipment", ""),
                                                             c.get("exercise", ""), vers.get(c.get("version"), 5)))


def hhmm(m: float) -> str:
    return f"{int(m // 60):02d}:{int(m % 60):02d}"


def schedule(cs: list[dict]) -> list[dict]:
    t, since_break, out, lunched = START_MIN + 45, 0.0, [], False   # 45 min: wardrobe, warm-up, camera check
    for i, c in enumerate(cs, 1):
        if not lunched and t >= LUNCH_AT:
            t += 45
            lunched = True
            since_break = 0
        if since_break >= BREAK_EVERY:
            t += 10
            since_break = 0
        out.append({"n": i, "time": hhmm(t), **c})
        t += MIN_PER_CLIP
        since_break += MIN_PER_CLIP
    return out


def main() -> None:
    rows = schedule(clips())
    cols = ["n", "time", "id", "exercise", "name", "version", "what_to_perform", "setup", "equipment", "set_for_blocking", "clip_seconds", "form_check"]
    with (HERE / "call_sheet.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols + ["front", "45deg", "side", "notes"])
        for r in rows:
            w.writerow([r.get(c, "") for c in cols] + ["", "", "", ""])
    end = rows[-1]["time"] if rows else "-"
    trs = "\n".join(
        "<tr>" + "".join(f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in ["n", "time", "id", "name", "version", "what_to_perform", "setup", "equipment", "set_for_blocking", "form_check"])
        + "<td class=box>&#9744; F &#9744; 45 &#9744; S</td></tr>" for r in rows)
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Performer call sheet</title>
<style>
body{{font:13px/1.35 Arial,Helvetica,sans-serif;color:#000;background:#fff;margin:16px}}
h1{{font-size:22px;margin:0 0 6px}} p{{margin:4px 0}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #000;padding:4px;vertical-align:top;text-align:left}}
th{{background:#000;color:#fff}} td.box{{white-space:nowrap;font-size:14px}}
@media print{{tr{{page-break-inside:avoid}} th{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}}}
</style></head><body>
<h1>Strong Years driving-video shoot: performer call sheet</h1>
<p><b>{len(rows)} clips</b> · call 08:00 · first clip {rows[0]['time'] if rows else '-'} · last clip about {end} · 10-minute break every {BREAK_EVERY} minutes, 45-minute lunch.</p>
<p><b>Before any capture:</b> signed performer release (TEMPLATES/performer_release.md, counsel-reviewed) · form reviewer on set · iPhone 4K 30p, tripod-locked 9:16, 1x lens, 3–3.5 m away, lens at hip height (1.0–1.1 m), full body with 8–10% margin · fitted C-TRAIN-A silhouette (tank, knee-length shorts) · props identical to SET-GARAGE (8/12/20 kg bells, the same wooden chair, 5-step stoop) · 1–2 s A-pose at the start of each take · 2-1-2 tempo, reps counted aloud.</p>
<p><b>Stop rule:</b> the performer stops any movement that hurts or feels unsafe; nobody pushes through for a take.</p>
<table><thead><tr><th>#</th><th>Time</th><th>Clip ID</th><th>Exercise</th><th>Version</th><th>Perform</th><th>Setup</th><th>Equipment</th><th>Set</th><th>Form check</th><th>Takes</th></tr></thead>
<tbody>
{trs}
</tbody></table></body></html>
"""
    (HERE / "call_sheet.html").write_text(doc, encoding="utf-8")
    print(len(rows), "clips; last clip", end)


if __name__ == "__main__":
    main()
