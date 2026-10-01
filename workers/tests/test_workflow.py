"""n8n_core_workflow.json <-> worker contract: every worker URL the workflow calls exists in the FastAPI app,
connections resolve, and every Code node still parses (node --check) after the patch."""
import json
import re
import shutil
import subprocess

import pytest

from app import app
from common import config
from tests.conftest import AUTH

WF = json.loads((config.SPEC_DIR / "n8n_core_workflow.json").read_text())
ROUTES = {(m.upper(), path) for path, ops in app.openapi()["paths"].items() for m in ops}


def worker_calls():
    out = []
    for n in WF["nodes"]:
        url = str(n.get("parameters", {}).get("url", ""))
        m = re.search(r"(RENDER_WORKER_URL|QA_WORKER_URL|COMPLIANCE_WORKER_URL)\)?\s*\+\s*'([^']+)'", url)
        if m:
            out.append((n["name"], n["parameters"].get("method", "GET"), m.group(2)))
    return out


def test_every_worker_endpoint_exists():
    calls = worker_calls()
    paths = {p for _, _, p in calls}
    assert {"/voice/stitch", "/assemble", "/qa", "/variants", "/compliance/scan", "/uniqueness/check", "/package"} <= paths
    for name, method, path in calls:
        assert (method, path) in ROUTES, f"{name}: {method} {path} not served by workers/app.py"


def test_connections_resolve_and_new_nodes_wired():
    names = {n["name"] for n in WF["nodes"]}
    for src, outs in WF["connections"].items():
        assert src in names
        for branch in outs["main"]:
            for c in branch:
                assert c["node"] in names, (src, c["node"])
    c = WF["connections"]
    assert c["Save Script (Supabase)"]["main"][0][0]["node"] == "Worker: Compliance Scan"
    assert c["Worker: Compliance Scan"]["main"][0][0]["node"] == "LLM: Compliance Judge (Claude)"
    assert c["Worker: Deterministic QA"]["main"][0][0]["node"] == "Worker: Uniqueness Guard"
    assert c["Parse Packaging + Compliance Pass 2"]["main"][0][0]["node"] == "Worker: Package + Pass 2"
    assert c["Worker: Package + Pass 2"]["main"][0][0]["node"] == "Pass 2 clean?"


def test_patch_is_idempotent(tmp_path):
    from tools.patch_workflow import patch
    p = tmp_path / "wf.json"
    p.write_text(json.dumps(WF))
    assert patch(p)["changed"] == []


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_code_nodes_parse(tmp_path):
    for n in WF["nodes"]:
        code = n.get("parameters", {}).get("jsCode")
        if not code:
            continue
        f = tmp_path / "c.js"
        f.write_text("async function main($input,$,$env,DateTime,$json){\n" + code + "\n}\n")
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, (n["name"], r.stderr[-400:])


def test_health():
    from fastapi.testclient import TestClient
    assert TestClient(app).get("/health").json() == {"ok": True}           # liveness only, no details unauthenticated
    assert TestClient(app).get("/health/details").status_code == 401
    h = TestClient(app, headers=AUTH).get("/health/details").json()
    assert h["ok"] and h["ffmpeg"] and h["font"] == "Figtree-ExtraBold.ttf"


def _run_node(name: str, nodes: dict, input_json: dict, tmp_path) -> dict:
    """Execute one patched Code node in node.js with mocked $() / $input / $env (mock-data run)."""
    code = next(n for n in WF["nodes"] if n["name"] == name)["parameters"]["jsCode"]
    harness = (
        "const NODES = " + json.dumps(nodes) + ";\n"
        "const $ = (n) => { if (!(n in NODES)) throw new Error('missing mock for ' + n); "
        "return { first: () => ({ json: NODES[n] }), all: () => [{ json: NODES[n] }] }; };\n"
        "const $input = { first: () => ({ json: " + json.dumps(input_json) + " }), all: () => [] };\n"
        "const $env = {};\n"
        "const out = (() => {\n" + code + "\n})();\n"
        "console.log(JSON.stringify(out[0].json));\n")
    f = tmp_path / f"{re.sub(r'[^a-z]', '_', name.lower())}.js"
    f.write_text(harness)
    r = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
    return json.loads(r.stdout)


def _claude(obj):
    return {"content": [{"type": "text", "text": json.dumps(obj)}]}


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_parse_verdict_merges_worker_scan(tmp_path):
    claim = {"brief": {"id": "b1"}}
    ps = {"claim": claim, "attempt": 1, "script": {}, "regex_hits": [
        {"id": "BC05", "severity": "block", "match": "Detox", "meaning": "detox"}]}
    mbex = {"verdict": "pass", "mbex_candidates": [{"id": "BC05", "match": "Detox"}], "blocks": [], "required_missing": []}
    nodes = {"Parse Script + Regex Pre-Scan": ps, "Save Script (Supabase)": {"id": "s1"}, "Worker: Compliance Scan": mbex}
    out = _run_node("Parse Verdict", nodes, _claude({"verdict": "pass", "confidence": 0.95}), tmp_path)
    assert out["verdict"] == "pass" and out["regex_hits"] == []          # MB-EX span confirmed by the judge
    nodes["Worker: Compliance Scan"] = {"verdict": "block", "mbex_candidates": [], "required_missing": [],
                                        "blocks": [{"rule": "M-04", "span": "hold your breath", "fix": "Valsalva"}]}
    ps["regex_hits"] = []
    out = _run_node("Parse Verdict", nodes, _claude({"verdict": "pass", "confidence": 0.95}), tmp_path)
    assert out["verdict"] == "revise" and out["can_revise"] and "M-04" in out["feedback"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_decide_qa_route_reads_worker_metrics(tmp_path):
    pv = {"claim": {"brief": {"id": "b1", "attempts": 1}, "page": {"id": "p1", "auto_publish": True}},
          "judge": {"risk_tier": "green", "judge_ok": True}, "script_id": "s1"}
    good = {"lufs_integrated": -14, "true_peak_db": -1.4, "caption_cer": 0, "spec_ok": True, "ai_tag_present": True,
            "duration_ok": True, "black_max_s": 0, "freeze_max_s": 0}
    nodes = {"Parse Verdict": pv, "Worker: Deterministic QA": {"metrics": good},
             "Worker: Assemble Master (Remotion/ffmpeg)": {"asset_id": "a1", "duration_s": 30},
             "Worker: Uniqueness Guard": {"allow": True}}
    assert _run_node("Decide QA Route", nodes, _claude({"decision": "pass"}), tmp_path)["route"] == "auto"
    nodes["Worker: Uniqueness Guard"] = {"allow": False, "reasons": ["audio: same voice track"]}
    assert _run_node("Decide QA Route", nodes, _claude({"decision": "pass"}), tmp_path)["route"] == "human"
    nodes["Worker: Uniqueness Guard"] = {"allow": True}
    nodes["Worker: Deterministic QA"] = {"metrics": {**good, "ai_tag_present": False}}
    out = _run_node("Decide QA Route", nodes, _claude({"decision": "pass"}), tmp_path)
    assert out["decision"] == "fail" and out["route"] == "regen"
NODE_NAMES = {n["name"] for n in WF["nodes"]}
