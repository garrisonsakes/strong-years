"""Growth endpoints sit behind the same auth as every other worker route (common/auth, AUDIT H9), validate input,
and never spend: the executor endpoint reports a refusal in every environment."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import app
from growth import config as G
from tests.conftest import AUTH
from tests.test_growth_governor import NOW, state

FIX = json.loads((Path(__file__).parent / "fixtures" / "growth_metrics.json").read_text())
ENDPOINTS = [("POST", "/growth/metrics/normalize"), ("POST", "/growth/metrics/fetch"), ("POST", "/growth/baselines"),
             ("POST", "/growth/score"), ("POST", "/growth/actions"), ("POST", "/growth/allocate"),
             ("POST", "/growth/governor/plan"), ("POST", "/growth/governor/execute"), ("GET", "/growth/governor/audit"),
             ("GET", "/growth/config")]


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "GROWTH_AUDIT_PATH", str(tmp_path / "audit.jsonl"))
    return TestClient(app)


@pytest.mark.parametrize("method,path", ENDPOINTS)
def test_every_growth_endpoint_requires_the_worker_token(client, method, path):
    r = client.request(method, path, json={} if method == "POST" else None)
    assert r.status_code == 401
    r = client.request(method, path, json={} if method == "POST" else None, headers={"X-Worker-Token": "wrong"})
    assert r.status_code == 401


def test_normalize_parses_platform_payloads_and_reports_errors(client):
    body = {"now": "2026-10-02T13:00:00Z", "posts": [
        {"post_id": "p1", "page_id": "pg1", "platform": "instagram", "published_at": "2026-10-01T12:00:00Z", "duration_s": 32,
         "captures": [{"captured_at": "2026-10-01T13:00:00Z", "raw": FIX["instagram"]["raw"]},
                      {"captured_at": "2026-10-02T12:00:00Z", "raw": FIX["instagram"]["raw"]}],
         "rollups": {"keyword_comments": 40, "optins": 3}},
        {"post_id": "p2", "platform": "nope", "published_at": "2026-10-01T12:00:00Z"}]}
    r = client.post("/growth/metrics/normalize", json=body, headers=AUTH)
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["results"][0]["horizons_available"] == [1, 24] and out["snapshots"][0]["views"] == 125400
    assert out["snapshots"][0]["keyword_comments"] == 40 and out["snapshots"][0]["members"] is None
    assert out["errors"] == [{"post_id": "p2", "error": "post.platform must be one of " + ", ".join(G.PLATFORMS)}]


def test_fetch_is_disabled_by_default(client):
    r = client.post("/growth/metrics/fetch", json={"posts": [{"post_id": "p", "platform": "instagram", "published_at": "2026-10-01T12:00:00Z",
                                                              "external_post_id": "1"}], "tokens": {"instagram": "t"}}, headers=AUTH)
    assert r.status_code == 200 and r.json()["live"] is False and r.json()["errors"][0]["error"] == "live metrics disabled"


def test_baselines_score_actions_allocate_round_trip(client):
    snaps = [{"post_id": f"h{i}", "page_id": "pg1", "platform": "instagram", "horizon_h": 24, "published_at": f"2026-09-{i + 1:02d}T12:00:00Z",
              "views": 2000 + 100 * i, "shares": 8, "saves": 12, "keyword_comments": 4} for i in range(12)]
    r = client.post("/growth/baselines", json={"history": snaps, "pages": ["pg1", "pg2"]}, headers=AUTH)
    assert r.status_code == 200
    rows = r.json()["baselines"]
    assert {b["page_id"] for b in rows} == {"pg1", "pg2"} and len(rows) == 2 * len(G.PLATFORMS) * len(G.HORIZONS)
    hot = {"post_id": "w1", "page_id": "pg1", "platform": "instagram", "horizon_h": 24, "published_at": "2026-10-01T12:00:00Z",
           "views": 90000, "shares": 900, "saves": 1500, "keyword_comments": 300, "optins": 40, "members": 3}
    r = client.post("/growth/score", json={"snapshots": [hot], "baselines": rows}, headers=AUTH)
    assert r.status_code == 200 and r.json()["counts"]["WINNER"] == 1
    scores = r.json()["scores"]
    pages = [{"id": "pg1", "slug": "changyin", "status": "active"}, {"id": "pg2", "slug": "sunyoon-kitchen", "status": "active"}]
    r = client.post("/growth/actions", json={"scores": scores, "posts": [{"post_id": "w1", "caption": "AI character. Chair test.",
                                                                           "arm": {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02"}}],
                                             "pages": pages, "now": NOW.isoformat()}, headers=AUTH)
    assert r.status_code == 200
    out = r.json()
    assert out["counts"]["remix_jobs"] == 1 and out["remix_jobs"][0]["target_page_id"] == "pg2"
    assert out["boost_candidates"][0]["status"] in ("needs_human", "flagged_human")      # no judge key in tests -> human
    r = client.post("/growth/allocate", json={"page": pages[0], "platform": "instagram", "cadence": 7, "seed": 1,
                                              "observations": [{"arm_key": "pillar=P01|grammar=IF_EVERY|format=F02|speaker=CHANG|length=M",
                                                                "reward": 0.9, "at": "2026-10-01T00:00:00Z"}]}, headers=AUTH)
    assert r.status_code == 200 and len(r.json()["slots"]) == 7 and r.json()["explore_share"] >= 0.2
    r = client.post("/growth/allocate", json={"page": pages[0], "platform": "snapchat"}, headers=AUTH)
    assert r.status_code == 422


def test_governor_plan_is_dry_run_audited_and_execute_refuses(client, tmp_path):
    r = client.post("/growth/governor/plan", json={"state": state(), "now": NOW.isoformat()}, headers=AUTH)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["mode"] == "dry_run" and d["valid"] and d["audit"]["hash"]
    r = client.get("/growth/governor/audit", headers=AUTH)
    assert r.json() == {"ok": True, "entries": 1}
    r = client.post("/growth/governor/execute", json={"decision": d, "approval": {"by": "g", "decision_hash": d["state_hash"]}}, headers=AUTH)
    assert r.status_code == 200 and r.json()["ok"] is False and r.json()["executed"] is False and "SPEND_ENABLED" in r.json()["refused"]
    assert client.get("/growth/governor/audit", headers=AUTH).json()["entries"] == 2
    r = client.post("/growth/governor/plan", json={"state": {"budget": "junk"}}, headers=AUTH)
    assert r.status_code == 200 and r.json()["status"] == "STOP" and not r.json()["valid"]
    r = client.post("/growth/governor/plan", json={"state": state(), "config_overrides": {"allocator": {"explore_floor": 0.05}}}, headers=AUTH)
    assert r.status_code == 422                                                           # config floor can't be lowered
    r = client.post("/growth/governor/plan", json={"state": state(), "now": "yesterday"}, headers=AUTH)
    assert r.status_code == 422


def test_config_endpoint_reports_switches_and_health_details_show_growth(client):
    r = client.get("/growth/config", headers=AUTH)
    assert r.status_code == 200
    j = r.json()
    assert j["mode"] == "dry_run" and j["env"]["SPEND_ENABLED"] is False and j["env"]["GROWTH_LIVE_METRICS"] is False
    assert j["config"]["allocator"]["explore_floor"] >= 0.2 and j["fingerprint"]
    h = client.get("/health/details", headers=AUTH).json()
    assert h["growth"]["spend_enabled"] is False and h["growth"]["dry_run"] is True


def test_request_level_overrides_cannot_flip_the_env_switches(client):
    body = {"state": state(), "now": NOW.isoformat(), "config_overrides": {"SPEND_ENABLED": True}}
    r = client.post("/growth/governor/plan", json=body, headers=AUTH)
    assert r.status_code == 200 and r.json()["mode"] == "dry_run"
    assert r.json()["boosts"][0]["approved_daily_usd"] == 100.0                      # approval record still binds
    assert G.SPEND_ENABLED is False
    # Round 5 audit: governor caps are not request parameters at all (422), so a cap can't be lifted in the same call.
    body["config_overrides"] = {"governor": {"max_boost_daily_usd": 999999}}
    r = client.post("/growth/governor/plan", json=body, headers=AUTH)
    assert r.status_code == 422
