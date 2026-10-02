"""n8n_discover_workflow.json <-> worker contract: importable, DISABLED until live, every worker URL is served, the
three schedules (daily 03:00 ET crawl, hourly stream, weekly top-50 + readout) are wired in order, Code nodes parse,
and no node posts, spends or calls a platform / ads API directly (all crawling happens in the worker)."""
from __future__ import annotations

import json
import re
import shutil
import subprocess

import pytest

from app import app
from common import config

WF = json.loads((config.SPEC_DIR / "n8n_discover_workflow.json").read_text())
ROUTES = {(m.upper(), path) for path, ops in app.openapi()["paths"].items() for m in ops}
NODES = {n["name"]: n for n in WF["nodes"]}


def _down(name):
    return [c["node"] for b in WF["connections"].get(name, {}).get("main", []) for c in b]


def _path(start, n):
    out, cur = [start], start
    for _ in range(n):
        nxt = _down(cur)
        if not nxt:
            break
        cur = nxt[-1] if cur == "Worker: Discover Trends" else nxt[0]
        out.append(cur)
    return out


def test_importable_and_disabled():
    assert WF["active"] is False and WF["settings"]["timezone"] == "America/New_York"
    assert len({n["id"] for n in WF["nodes"]}) == len(WF["nodes"])
    crawls = [n for n in WF["nodes"] if n["name"].startswith("Worker: Discover Crawl")]
    assert len(crawls) == 2 and all(n.get("disabled") is True for n in crawls)     # n8n_import re-enables only when live
    for n in WF["nodes"]:
        assert n["type"].startswith("n8n-nodes-base.") and "typeVersion" in n and "position" in n
    for src, outs in WF["connections"].items():
        assert src in NODES and all(c["node"] in NODES for b in outs["main"] for c in b)


def test_schedules():
    crons = {n["name"]: n["parameters"]["rule"]["interval"][0] for n in WF["nodes"] if n["type"].endswith("scheduleTrigger")}
    assert crons["Daily 03:00 ET: Discover Crawl"] == {"field": "cronExpression", "expression": "0 3 * * *"}
    assert crons["Hourly: Discover Stream"] == {"field": "hours", "hoursInterval": 1}
    assert crons["Weekly Mon 04:00 ET: Top-50 + Readout"]["expression"] == "0 4 * * 1"


def test_worker_calls_exist_and_cover_the_loop():
    calls = []
    for n in WF["nodes"]:
        m = re.search(r"\$env\.QA_WORKER_URL\s*\}\}(/[^'\" ]+)", str(n["parameters"].get("url", "")))
        if m:
            calls.append((n["parameters"].get("method", "GET").upper(), m.group(1)))
    assert {p for _, p in calls} == {"/discover/crawl", "/discover/trends", "/discover/remake", "/discover/value"}
    for c in calls:
        assert c in ROUTES, c


def test_chain_order():
    d = _path("Daily 03:00 ET: Discover Crawl", 12)
    assert d.index("Worker: Discover Crawl (daily)") < d.index("Supabase: Upsert niche_posts (daily)") < \
        d.index("Worker: Discover Trends") < d.index("Worker: Discover Remake Briefs") < d.index("Supabase: Insert remake_queue")
    assert {"Supabase: Insert niche_opportunities", "Supabase: Insert discover_feeds (daily)"} <= set(_down("Worker: Discover Trends"))
    h = _path("Hourly: Discover Stream", 6)
    assert h[-1] == "Supabase: Insert niche_post_reads" and "Worker: Discover Crawl (stream)" in h
    w = _path("Weekly Mon 04:00 ET: Top-50 + Readout", 10)
    assert w.index("Worker: Discover Trends (weekly)") < w.index("Worker: Discover Value (MRR x virality)") < w.index("Slack: Weekly Readout")


def test_no_direct_platform_or_ads_calls():
    blob = json.dumps(WF).lower()
    for host in ("graph.facebook.com", "open.tiktokapis.com", "googleapis.com", "api.x.com", "graph.threads.net",
                 "instagram.com", "tiktok.com", "/ads", "adaccount", "/governor/execute"):
        assert host not in blob, host
    urls = [str(n["parameters"].get("url", "")) for n in WF["nodes"] if n["type"].endswith("httpRequest")]
    assert all("$env.SUPABASE_URL" in u or "$env.QA_WORKER_URL" in u for u in urls)


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_code_nodes_parse():
    for n in WF["nodes"]:
        if n["type"].endswith(".code"):
            src = "(async () => {\n" + n["parameters"]["jsCode"] + "\n})"
            p = subprocess.run(["node", "--check", "-"], input=src, capture_output=True, text=True)
            assert p.returncode == 0, (n["name"], p.stderr)
