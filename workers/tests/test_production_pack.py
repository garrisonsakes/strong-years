"""production/: the locked reference manifest, DRY_RUN render/voice scripts, the 150 render jobs, the D-21..D-15
week queue (compliance CLI must pass), the 205-clip performer call sheet and the 60 no-face B-roll prompts."""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / "production"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_reference_manifest_is_locked_and_complete(tmp_path):
    rr = _load(P / "refs/render_refs.py")
    man = rr.load_manifest()
    by = {}
    for it in man["items"]:
        by[it["character"]] = by.get(it["character"], 0) + 1
        assert "documentary realism" in it["prompt"] and "Same" in it["prompt"]
    assert by == {"chang": 24, "sun": 24, "duo": 6}
    bad = json.loads((P / "refs/manifest.json").read_text())
    bad["items"][0]["prompt"] += " younger"
    f = tmp_path / "m.json"
    f.write_text(json.dumps(bad))
    with pytest.raises(rr.Locked):
        rr.load_manifest(f)


def test_scripts_default_to_dry_run(monkeypatch):
    monkeypatch.delenv("DRY_RUN", raising=False)
    assert _load(P / "refs/render_refs.py").main(["--only", "C01"]) == 0
    assert _load(P / "voices/design_voices.py").main([]) == 0
    plan = json.loads((P / "voices/out/plan.json").read_text())
    assert plan["dry_run"] is True and len(plan["requests"]) == 16


def test_render_jobs_call_sheet_and_broll():
    jobs = json.loads((P / "shot_list/render_jobs_first150.json").read_text())["jobs"]
    assert len(jobs) == 150 and jobs[0]["priority"] == "P0"
    assert all(j["driving_clip_id"] for j in jobs if j["render_mode"] == "performer_driving_video")
    rows = list(csv.DictReader((P / "performer/call_sheet.csv").open()))
    assert len(rows) == 205 and len({r["id"] for r in rows}) == 205
    html = (P / "performer/call_sheet.html").read_text()
    assert "color:#000" in html and "gray" not in html.lower() and "grey" not in html.lower()
    b = json.loads((P / "broll/broll_prompts.json").read_text())
    assert b["count"] == 60 and all("No people, no faces" in i["prompt"] for i in b["items"])


def test_plan_week_queue_passes_the_compliance_cli():
    r = subprocess.run([sys.executable, str(P / "shot_list/plan_week.py")], capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    q = json.loads((P / "shot_list/week_queue_D-21_D-15.json").read_text())
    assert q["videos"] > 30 and q["missing_scripts"] == [] and q["compliance"]["exit_code"] == 0
    assert {row["D"] for row in q["queue"]} == set(range(-21, -14))
