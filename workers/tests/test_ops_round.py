"""Ops round: the exceptions client and its callers (compliance human route, uniqueness, governor boost requests),
recorded boost approvals reaching the governor, /growth/summary, the manual fallback post pack, and the compliance
`templates` scan over the app's lifecycle emails and the DM flows (must pass)."""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from fastapi.testclient import TestClient

from app import app
from common import exceptions as exc
from compliance.__main__ import main as compliance_main
from growth import approvals
from packager import fallback
from tests.conftest import AUTH

ROOT = Path(__file__).resolve().parents[2]


def _mock_client(calls: list):
    def handler(req: httpx.Request) -> httpx.Response:
        calls.append(json.loads(req.content))
        assert req.headers["authorization"] == "Bearer " + "t" * 40
        return httpx.Response(201, json={"id": "e1", "created": True, "status": "open"})
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_exceptions_client_skips_when_unconfigured_and_posts_when_configured(monkeypatch):
    monkeypatch.delenv("APP_URL", raising=False)
    assert exc.post_exception("compliance_flag", "x", source="t")["status"] == "skipped"
    assert exc.post_exception("nonsense", "x", source="t")["status"] == "error"
    monkeypatch.setenv("APP_URL", "https://members.strongyears.com")
    monkeypatch.setenv("EXCEPTIONS_API_TOKEN", "t" * 40)
    calls: list = []
    r = exc.post_exception("boost_approval", "Boost b1", source="governor", dedupe_key="boost:b1",
                           payload={"boost_id": "b1", "requested_daily_usd": 50}, client=_mock_client(calls))
    assert r == {"status": "created", "id": "e1"}
    assert calls[0]["type"] == "boost_approval" and calls[0]["dedupe_key"] == "boost:b1"
    bad = exc.post_exception("compliance_flag", "x", source="t",
                             client=httpx.Client(transport=httpx.MockTransport(lambda r: (_ for _ in ()).throw(httpx.ConnectError("down")))))
    assert bad["status"] == "error"                       # never raises


def test_compliance_human_route_and_uniqueness_deny_post_exceptions(monkeypatch):
    sent = []
    monkeypatch.setattr(exc, "post_exception", lambda *a, **k: sent.append((a, k)) or {"status": "created"})
    c = TestClient(app)
    r = c.post("/compliance/scan", json={"text": "Walk after dinner."}, headers=AUTH).json()
    assert r["final"]["verdict"] == "human"               # no judge key in tests → human
    assert sent[-1][0][0] == "compliance_flag" and sent[-1][1]["source"] == "compliance"
    words = "the morning chair builder trains the muscles you use to stand up from a chair slowly with your arms crossed "
    cand = {"id": "V1", "page_id": "p1", "platform": "ig", "script_text": words * 3, "scheduled_at": "2026-10-12T15:00:00Z"}
    sib = {**cand, "id": "V2", "page_id": "p2"}
    u = c.post("/uniqueness/check", json={"candidate": cand, "siblings": [sib]}, headers=AUTH).json()
    assert u["allow"] is False
    assert sent[-1][0][0] == "compliance_flag" and sent[-1][1]["dedupe_key"] == "uniqueness:V1"


def test_boost_approval_recorded_then_used_by_the_governor_and_summary(monkeypatch, tmp_path):
    monkeypatch.setenv("GROWTH_APPROVALS_PATH", str(tmp_path / "appr.jsonl"))
    monkeypatch.setattr("growth.governor.audit_path", lambda: tmp_path / "audit.jsonl")
    sent = []
    monkeypatch.setattr(exc, "post_exception", lambda *a, **k: sent.append((a, k)) or {"status": "created"})
    c = TestClient(app)
    at = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    assert c.post("/growth/approvals/boost", json={"boost_id": "b1", "approval": {"by": "", "at": at, "max_daily_usd": 40}},
                  headers=AUTH).json()["ok"] is False                          # a named human is required
    state = {"boosts": [{"boost_id": "b1", "post_id": "P1", "class": "WINNER", "compliance_verdict": "pass",
                         "judge_passed": True, "requested_daily_usd": 50}]}
    plan = c.post("/growth/governor/plan", json={"state": state}, headers=AUTH).json()
    assert plan["approval_requests"][0]["boost_id"] == "b1" and sent[-1][0][0] == "boost_approval"
    ok = c.post("/growth/approvals/boost", json={"boost_id": "b1", "approval": {"by": "garrison", "at": at, "max_daily_usd": 40}},
                headers=AUTH).json()
    assert ok["ok"] is True
    attached = approvals.attach(state)
    assert attached["boosts"][0]["approval"]["by"] == "garrison"
    assert approvals.pending(attached) == []
    plan2 = c.post("/growth/governor/plan", json={"state": state}, headers=AUTH).json()
    assert plan2["approval_requests"] == []
    s = c.get("/growth/summary", headers=AUTH).json()
    assert s["reach_24h"] is None and s["governor"]["mode"] == "dry_run" and s["governor"]["spend_enabled"] is False
    assert isinstance(s["governor"]["blitz9"], list)


def _item(**kw):
    base = {"post_id": "S151", "page": "changyin", "platform": "ig", "variant_id": "S151-ig-v1", "is_aigc": True,
            "uniqueness": {"allow": True, "reasons": []}, "video": "https://cdn.example/S151-ig.mp4",
            "caption": "Laundry basket, full. Hug it close. Chang Yin is an AI character. Not medical advice.",
            "hashtags": ["#strongyears"], "first_comment": "Comment STRONG for the chair builder.",
            "scheduled_at": "2026-10-12 08:00"}
    return {**base, **kw}


def test_fallback_pack_carries_the_uniqueness_variant_and_holds_the_rest(tmp_path):
    items = [_item(), _item(platform="tt", variant_id="S151-tt-v1"), _item(platform="x", variant_id="S151-x-v1"),
             _item(platform="yt", uniqueness={"allow": False, "reasons": ["tfidf 0.91 vs S150"]}),
             _item(platform="fb", variant_id="S151-fb-v1", is_aigc=False),
             _item(platform="th", variant_id="S151-th-v1", caption="This tea cures arthritis. AI character.")]
    m = fallback.build_pack("2026-10-12", items, tmp_path)
    assert {p["platform"] for p in m["packed"]} == {"ig", "tt", "x"}
    assert {h["platform"] for h in m["held"]} == {"yt", "fb", "th"}
    day = tmp_path / "2026-10-12"
    assert "S151-ig-v1" in (day / "changyin/ig/checklist.md").read_text()
    assert "AI info" in (day / "changyin/ig/checklist.md").read_text()
    assert "AI-generated content" in (day / "changyin/tt/checklist.md").read_text()
    meta = list(csv.reader((day / "meta_business_suite.csv").open()))
    buf = list(csv.reader((day / "buffer.csv").open()))
    assert len(meta) == 2 and meta[1][-1] == "S151-ig-v1"
    assert len(buf) == 3
    assert len(list(csv.reader((day / "held.csv").open()))) == 4


def test_lifecycle_templates_and_dm_flows_pass_the_compliance_cli():
    files = [str(ROOT / "app/content/lifecycle/sequences.json"), *map(str, sorted((ROOT / "workers/dm/flows").glob("*.json")))]
    assert compliance_main(["templates", *files]) == 0
