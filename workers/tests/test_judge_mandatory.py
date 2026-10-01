"""Two-layer compliance: deterministic scan, then a MANDATORY LLM judge. No key, error, timeout or bad output
routes to human review. Nothing reaches auto_publish or approval without a passing judge result."""
from __future__ import annotations

import json
import shutil

import httpx
import pytest
from fastapi.testclient import TestClient

from app import app
from common import config
from compliance import judge as J
from compliance import scanner
from qa import scoring
from tests.conftest import AUTH
from tests.test_workflow import NODE_NAMES, _claude, _run_node

CLEAN = "Walk for three minutes after dinner."
PASS = {"status": "ok", "verdict": "pass", "confidence": 0.95}


def test_config_default_requires_judge():
    src = (config.WORKERS_DIR / "common" / "config.py").read_text()
    assert 'os.environ.get("REQUIRE_JUDGE", "1")' in src and config.REQUIRE_JUDGE


@pytest.mark.parametrize("judge,want", [
    (None, "human"), ({"status": "skipped", "verdict": None}, "human"), ({"status": "error", "verdict": "human"}, "human"),
    ({"status": "timeout", "verdict": "human"}, "human"), ({"status": "ok", "verdict": None}, "human"),
    ({"status": "ok", "verdict": "pass", "confidence": 0.5}, "human"), (PASS, "pass"),
    ({"status": "ok", "verdict": "revise", "confidence": 0.9}, "revise"),
])
def test_combine_requires_passing_judge(judge, want):
    det = scanner.scan(text=CLEAN)
    assert det["verdict"] == "pass"
    out = scanner.combine_with_judge(det, judge, require_judge=True)
    assert out["verdict"] == want and out["judge_passed"] == (want == "pass")


def test_deterministic_block_stays_block_even_without_judge():
    det = scanner.scan(text="This tea cures arthritis.")
    assert scanner.combine_with_judge(det, None, require_judge=True)["verdict"] == "block"
    assert scanner.combine_with_judge(det, PASS, require_judge=True)["verdict"] == "block"   # judge can't clear it


def test_judge_timeout_and_errors_route_human():
    def slow(_req):
        raise httpx.ReadTimeout("slow")
    j = J.judge({"x": 1}, [], api_key="k", client=httpx.Client(transport=httpx.MockTransport(slow)))
    assert j["status"] == "timeout" and j["verdict"] == "human"
    junk = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"content": [{"type": "text", "text": "no json"}]})))
    assert J.judge({"x": 1}, [], api_key="k", client=junk)["status"] == "error"
    assert J.judge({"x": 1}, [], api_key="")["status"] == "skipped"


def test_scan_endpoint_no_key_goes_human():
    c = TestClient(app, headers=AUTH)
    for body in ({"text": CLEAN}, {"text": CLEAN, "judge": False}, {"script": {"lines": [{"text": CLEAN}]}}):
        r = c.post("/compliance/scan", json=body).json()
        assert r["verdict"] == "pass" and r["final"]["verdict"] == "human" and r["final"]["judge_passed"] is False
        assert r["judge"]["status"] == "skipped"


def test_scan_endpoint_with_passing_judge(judge_pass):
    r = TestClient(app, headers=AUTH).post("/compliance/scan", json={"text": CLEAN}).json()
    assert r["final"]["verdict"] == "pass" and r["final"]["judge_passed"] is True and judge_pass


def test_package_pass2_needs_judge(monkeypatch):
    c = TestClient(app, headers=AUTH)
    body = {"packaging": {"instagram": {"caption": "Walk after dinner."}}, "burned_in_text": ["AI character"]}
    r = c.post("/package", json=body).json()
    assert r["pass2_ok"] is False and any(i["id"] == "LLM-JUDGE" for i in r["pass2_issues"])
    monkeypatch.setattr(J, "judge", lambda *a, **k: {"status": "timeout", "verdict": "human"})
    assert c.post("/package", json=body).json()["pass2_ok"] is False
    monkeypatch.setattr(J, "judge", lambda *a, **k: dict(PASS))
    assert c.post("/package", json=body).json()["pass2_ok"] is True


def test_qa_routing_requires_judge():
    good = {"spec_ok": True, "lufs_integrated": -14, "true_peak_db": -1.5, "ai_tag_present": True, "c2pa_trusted": True}
    for jp in (None, False):
        assert scoring.score(good, vision_decision="pass", trusted=True, judge_passed=jp, require_judge=True)["route"] == "human"
    assert scoring.score(good, vision_decision="pass", trusted=True, judge_passed=True, require_judge=True)["route"] == "auto"
    assert scoring.score(good, vision_decision="pass", trusted=False, judge_passed=True, require_judge=True)["route"] == "approval"
    c = TestClient(app, headers=AUTH)
    assert c.post("/qa/score", json={"metrics": good, "vision_decision": "pass", "trusted": True}).json()["route"] == "human"


def test_n8n_judge_node_continues_on_error_with_timeout():
    wf = json.loads((config.SPEC_DIR / "n8n_core_workflow.json").read_text())
    n = next(x for x in wf["nodes"] if x["name"] == "LLM: Compliance Judge (Claude)")
    assert n["onError"] == "continueRegularOutput" and n["parameters"]["options"]["timeout"] == 120000
    assert "Parse Verdict" in NODE_NAMES


PV_NODES = {"Parse Script + Regex Pre-Scan": {"claim": {"brief": {"id": "b1"}}, "attempt": 1, "script": {}, "regex_hits": []},
            "Save Script (Supabase)": {"id": "s1"},
            "Worker: Compliance Scan": {"verdict": "pass", "mbex_candidates": [], "blocks": [], "required_missing": []}}


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("judge_input,verdict,ok", [
    ({"error": {"message": "401 invalid x-api-key"}}, "human", False),         # no / bad key
    ({"error": {"message": "timeout of 120000ms exceeded"}}, "human", False),  # timeout
    ({"content": [{"type": "text", "text": "I cannot comply"}]}, "human", False),  # bad JSON
    (_claude({"verdict": "pass", "confidence": 0.95}), "pass", True),
    (_claude({"verdict": "pass", "confidence": 0.6}), "human", False),
])
def test_n8n_parse_verdict_never_passes_without_judge(tmp_path, judge_input, verdict, ok):
    out = _run_node("Parse Verdict", PV_NODES, judge_input, tmp_path)
    assert out["verdict"] == verdict and out["judge"]["judge_ok"] is ok and out["can_revise"] is False


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_n8n_decide_qa_route_requires_judge_ok(tmp_path):
    pv = {"claim": {"brief": {"id": "b1", "attempts": 1}, "page": {"id": "p1", "auto_publish": True}},
          "judge": {"risk_tier": "green", "judge_ok": False}, "script_id": "s1"}
    good = {"lufs_integrated": -14, "true_peak_db": -1.4, "caption_cer": 0, "spec_ok": True, "ai_tag_present": True,
            "duration_ok": True, "black_max_s": 0, "freeze_max_s": 0, "c2pa_trusted": True}
    nodes = {"Parse Verdict": pv, "Worker: Deterministic QA": {"metrics": good},
             "Worker: Assemble Master (Remotion/ffmpeg)": {"asset_id": "a1", "duration_s": 30},
             "Worker: Uniqueness Guard": {"allow": True}}
    assert _run_node("Decide QA Route", nodes, _claude({"decision": "pass"}), tmp_path)["route"] == "human"
    pv["judge"]["judge_ok"] = True
    assert _run_node("Decide QA Route", nodes, _claude({"decision": "pass"}), tmp_path)["route"] == "auto"
