#!/usr/bin/env python3
"""Weekly gate refit: recompute the virality rubric weights (tools/virality.py WEIGHTS, 100 points) from our own
24 h scorecard composites (workers/growth/scorecard.py, table post_scores_components).

For every rubric row c, the feature is the share of its points a script earned (parts[c] / WEIGHTS[c], 0..1) and
the outcome is the post's 24 h composite. importance_c = max(0, Pearson r(feature_c, composite)). Target weights
are 100 * importance_c / sum(importance). The new weights blend toward the target by lambda = n / (n + 200)
(capped at 0.5), move at most 30% per week per row, never drop below 1 point, and still sum to 100.

  python3 tools/refit_gate.py --scores scores_24h.json            # dry run: report only (default)
  python3 tools/refit_gate.py --scores scores_24h.json --apply    # also writes data/content/rubric_weights.json,
                                                                   # which tools/virality.py loads over WEIGHTS
scores_24h.json: [{"script_id": "S154", "composite": 71.2, "horizon_h": 24, "provisional": false}, ...] (an export
of post_scores_components joined to posts.script_id). Below MIN_POSTS rows it reports insufficient_data and
changes nothing. No network.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import virality as V  # noqa: E402

OVERRIDE = ROOT / "data/content/rubric_weights.json"
REPORT = ROOT / "data/content/refit_gate_report.json"
MIN_POSTS, LAMBDA_K, LAMBDA_MAX, MAX_STEP, FLOOR = 50, 200.0, 0.5, 0.30, 1.0


def _corr(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def refit(scores: list[dict], scripts: dict[str, dict], weights: dict[str, float] | None = None) -> dict:
    w0 = dict(weights or V.WEIGHTS)
    rows = [r for r in scores if int(r.get("horizon_h") or 24) == 24 and not r.get("provisional")
            and r.get("composite") is not None and r.get("script_id") in scripts]
    if len(rows) < MIN_POSTS:
        return {"status": "insufficient_data", "n": len(rows), "reason": f"{len(rows)} scored posts with scripts (< {MIN_POSTS})",
                "old": w0, "new": w0, "changes": [], "applied": False}
    parts = [V.score(scripts[r["script_id"]])["parts"] for r in rows]
    y = [float(r["composite"]) for r in rows]
    corr = {c: round(_corr([p.get(c, 0.0) / w0[c] if w0[c] else 0.0 for p in parts], y), 4) for c in w0}
    imp = {c: max(0.0, v) for c, v in corr.items()}
    tot = sum(imp.values())
    target = {c: (100.0 * imp[c] / tot if tot else w0[c]) for c in w0}
    lam = min(LAMBDA_MAX, len(rows) / (len(rows) + LAMBDA_K))
    lo = {c: max(FLOOR, w0[c] * (1 - MAX_STEP)) for c in w0}
    hi = {c: max(lo[c], w0[c] * (1 + MAX_STEP)) for c in w0}
    new = {c: (1 - lam) * w0[c] + lam * target[c] for c in w0}
    for _ in range(50):                       # clamp to +-30% / floor, then hand the residue to the free rows
        new = {c: min(hi[c], max(lo[c], v)) for c, v in new.items()}
        resid = 100.0 - sum(new.values())
        free = [c for c in new if (resid > 0 and new[c] < hi[c] - 1e-9) or (resid < 0 and new[c] > lo[c] + 1e-9)]
        if abs(resid) < 1e-6 or not free:
            break
        tot_free = sum(new[c] for c in free)
        for c in free:
            new[c] += resid * new[c] / tot_free
    new = {c: round(v, 1) for c, v in new.items()}
    drift = round(100.0 - sum(new.values()), 1)                 # rounding residue onto the largest row
    big = max(new, key=new.get)
    new[big] = round(new[big] + drift, 1)
    changes = [{"component": c, "old": w0[c], "new": new[c], "corr": corr[c]} for c in w0 if abs(new[c] - w0[c]) >= 0.1]
    return {"status": "ok", "n": len(rows), "lambda": round(lam, 3), "corr": corr, "old": w0, "new": new,
            "changes": changes, "applied": False}


def load_scripts() -> dict[str, dict]:
    lib = {s["id"]: s for s in json.loads((ROOT / "data/content/scripts.json").read_text(encoding="utf-8"))}
    w2 = ROOT / "data/content/wave2_scripts.json"
    if w2.exists():
        for s in json.loads(w2.read_text(encoding="utf-8")):
            lib.setdefault(s["id"], s)
    return lib


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scores", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    rep = refit(json.loads(Path(a.scores).read_text()), load_scripts())
    if a.apply and rep["status"] == "ok" and rep["changes"]:
        OVERRIDE.write_text(json.dumps(rep["new"], indent=1) + "\n")
        rep["applied"] = True
    REPORT.write_text(json.dumps(rep, indent=1) + "\n")
    print(f"refit_gate: {rep['status']} n={rep['n']} changes={len(rep['changes'])} applied={rep['applied']} -> "
          f"{REPORT.relative_to(ROOT)}")
    for c in rep["changes"]:
        print(f"  {c['component']}: {c['old']} -> {c['new']} (r={c['corr']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
