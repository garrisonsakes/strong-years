"""n8n_growth_workflow.json <-> worker contract: valid importable JSON, every worker URL exists in the FastAPI app,
connections resolve, Code nodes parse, the hourly and nightly chains are wired in the documented order, the
governor is called in dry-run and ends in a human-approval notification, and no node touches an ads API."""
from __future__ import annotations

import json
import re
import shutil
import subprocess

import pytest

from app import app
from common import config

WF = json.loads((config.SPEC_DIR / "n8n_growth_workflow.json").read_text())
ROUTES = {(m.upper(), path) for path, ops in app.openapi()["paths"].items() for m in ops}
NODES = {n["name"]: n for n in WF["nodes"]}


def _worker_calls():
    out = []
    for n in WF["nodes"]:
        url = str(n.get("parameters", {}).get("url", ""))
        m = re.search(r"\$env\.(RENDER_WORKER_URL|QA_WORKER_URL|COMPLIANCE_WORKER_URL)\s*\}\}(/[^'\" ]+)", url)
        if m:
            out.append((n["name"], n["parameters"].get("method", "GET").upper(), m.group(2)))
    return out


def _downstream(name: str) -> list[str]:
    return [c["node"] for branch in WF["connections"].get(name, {}).get("main", []) for c in branch]


def test_importable_shape():
    assert isinstance(WF["nodes"], list) and isinstance(WF["connections"], dict) and WF["name"]
    assert len(WF["nodes"]) >= 40 and len({n["id"] for n in WF["nodes"]}) == len(WF["nodes"])
    for n in WF["nodes"]:
        assert n["type"].startswith("n8n-nodes-base.") and "typeVersion" in n and "position" in n and "parameters" in n


def test_every_worker_endpoint_exists_and_the_six_growth_calls_are_made():
    calls = _worker_calls()
    paths = {p for _, _, p in calls}
    assert paths == {"/growth/metrics/normalize", "/growth/baselines", "/growth/score", "/growth/actions", "/growth/allocate",
                     "/growth/governor/plan"}
    for name, method, path in calls:
        assert (method, path) in ROUTES, f"{name}: {method} {path} not served by workers/app.py"
    assert "/growth/governor/execute" not in paths                                 # n8n never calls the executor


def test_connections_resolve():
    for src, outs in WF["connections"].items():
        assert src in NODES, src
        for branch in outs["main"]:
            for c in branch:
                assert c["node"] in NODES, (src, c["node"])


def test_hourly_chain_order():
    chain = ["Hourly: Growth Tick", "Supabase: Recent Published Posts", "Supabase: Raw Captures (metrics)",
             "Supabase: Order Rollup (orders by post)", "Build Normalize Request", "Worker: Normalize Metrics", "Rows: post_metrics",
             "Supabase: Upsert post_metrics", "Supabase: post_metrics History (30d)", "Build Baselines Request", "Worker: Baselines",
             "Supabase: Insert page_baselines", "Build Score Request", "Worker: Score", "Rows: post_scores + winners",
             "Supabase: Upsert post_scores", "Supabase: Upsert winners", "Any winners or losers?"]
    for a, b in zip(chain, chain[1:]):
        assert b in _downstream(a), (a, b)
    assert "Worker: Winner Actions" in NODES and "Supabase: Insert remix_jobs" in _downstream("Rows: remix_jobs + boost_queue")
    assert "Supabase: Insert boost_queue" in _downstream("Supabase: Insert remix_jobs")
    assert "Slack: Growth Hourly Summary" in _downstream("Supabase: Insert boost_queue")
    assert NODES["Hourly: Growth Tick"]["type"] == "n8n-nodes-base.scheduleTrigger"


def test_nightly_chain_allocator_then_governor_dry_run_then_human_notification():
    chain = ["Nightly 23:10: Allocator + Governor", "Supabase: Active Page Accounts", "Supabase: Bandit Observations (30d)",
             "Supabase: Recent Briefs (7d)", "Build Allocate Requests", "Worker: Allocate Slots", "Rows: briefs (slot plan)",
             "Supabase: Insert briefs (queued)", "Supabase: Approved Budget", "Supabase: Ledger (month)", "Supabase: Approved Boosts",
             "Build Governor State", "Worker: Governor Plan (dry run)", "Supabase: Insert governor_decisions",
             "Slack: Governor Plan for Approval"]
    for a, b in zip(chain, chain[1:]):
        assert b in _downstream(a), (a, b)
    assert NODES["Slack: Governor Plan for Approval"]["type"] == "n8n-nodes-base.slack"
    assert NODES["Slack: Growth Hourly Summary"]["type"] == "n8n-nodes-base.slack"
    gov = NODES["Worker: Governor Plan (dry run)"]
    assert "dry" in gov["name"].lower()
    code = NODES["Build Governor State"]["parameters"]["jsCode"]
    assert "SPEND_ENABLED" not in code or "false" in code.lower()


def test_briefs_from_the_allocator_are_queued_not_published():
    code = NODES["Rows: briefs (slot plan)"]["parameters"]["jsCode"]
    assert "'queued'" in code or '"queued"' in code
    assert "published" not in code.lower() and "approved" not in code.lower()


def test_no_ads_api_or_publishing_calls():
    blob = json.dumps(WF).lower()
    for needle in ("/act_", "adaccounts", "marketing", "ads_management", "business-api.tiktok.com/open_api/v1.3/ad",
                   "/media_publish", "upload-post", "uploadpost"):
        assert needle not in blob, needle
    for n in WF["nodes"]:
        url = str(n.get("parameters", {}).get("url", "")).lower()
        if n["type"] == "n8n-nodes-base.httpRequest":
            assert "supabase_url" in url or "worker_url" in url, (n["name"], url)


def test_supabase_writes_target_growth_tables_only():
    tables = set()
    for n in WF["nodes"]:
        url = str(n.get("parameters", {}).get("url", ""))
        m = re.search(r"/rest/v1/(\w+)", url)
        if m and n["parameters"].get("method", "GET").upper() in ("POST", "PATCH", "PUT"):
            tables.add(m.group(1))
    assert tables <= {"post_metrics", "page_baselines", "post_scores", "winners", "remix_jobs", "boost_queue", "briefs",
                      "governor_decisions", "bandit_arms", "spend_ledger", "rpc"}
    assert "posts" not in tables and "spend_budgets" not in tables                 # never publishes, never approves budgets


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_code_nodes_parse(tmp_path):
    n_code = 0
    for n in WF["nodes"]:
        code = n.get("parameters", {}).get("jsCode")
        if not code:
            continue
        n_code += 1
        f = tmp_path / "c.js"
        f.write_text("async function main($input,$,$env,DateTime,$json){\n" + code + "\n}\n")
        r = subprocess.run(["node", "--check", str(f)], capture_output=True, text=True)
        assert r.returncode == 0, (n["name"], r.stderr[-400:])
    assert n_code >= 8


def test_governor_state_builder_runs_on_mock_data(tmp_path):
    """The Code node that builds the governor state must produce the shape growth/governor.decide validates."""
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    code = NODES["Build Governor State"]["parameters"]["jsCode"]
    mocks = {"Supabase: Approved Budget": [{"id": "b1", "daily_cap_usd": 500, "monthly_cap_usd": 9000, "cash_floor_usd": 20000,
                                           "price_usd": 25, "status": "approved", "approved_by": "g", "approved_at": "2026-10-01T00:00:00Z"}],
             "Supabase: Ledger (month)": [{"day": "2026-10-14", "amount_usd": 100, "source": "reported", "spend_class": "boost"}],
             "Supabase: Approved Boosts": [{"post_id": "w1", "class": "WINNER", "requested_daily_usd": 100, "approved_by": "g",
                                            "approved_at": "2026-10-14T00:00:00Z", "approved_max_daily_usd": 100,
                                            "compliance": {"verdict": "pass", "judge_passed": True}}]}
    harness = (
        "const NODES = " + json.dumps(mocks) + ";\n"
        "const $ = (n) => { if (!(n in NODES)) throw new Error('missing mock for ' + n); const rows = NODES[n];"
        " return { first: () => ({ json: Array.isArray(rows) ? rows[0] : rows }), all: () => (Array.isArray(rows) ? rows : [rows]).map(j => ({ json: j })) }; };\n"
        "const $input = { first: () => ({ json: {} }), all: () => [] };\n"
        "const $env = {}; const $now = { toISO: () => '2026-10-15T06:00:00Z', toISODate: () => '2026-10-15' }; const DateTime = { now: () => $now };\n"
        "const out = (() => {\n" + code + "\n})();\n"
        "console.log(JSON.stringify(out[0].json));\n")
    f = tmp_path / "gov.js"
    f.write_text(harness)
    r = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
    out = json.loads(r.stdout)
    st = out.get("state") or out
    from growth import config as G, governor as GV
    from datetime import datetime, timezone
    v, errs = GV.validate_state(st, G.load(), datetime(2026, 10, 15, 6, tzinfo=timezone.utc))
    assert errs == [], errs
    assert v["daily_cap_usd"] == 500 and v["boosts"] and v["boosts"][0]["approval"]["max"] == 100
