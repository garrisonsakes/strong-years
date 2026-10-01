"""Round 5 audit: governor caps can't be lifted per request, and execute() refuses a plan made under any
config other than the operator's file/defaults."""
from __future__ import annotations

import pytest

from growth import config as G, governor as GV
from tests.test_growth_governor import NOW, boost, state


def test_governor_overrides_are_refused():
    with pytest.raises(G.ProtectedOverride):
        G.load({"governor": {"max_boost_daily_usd": 1e6}})
    with pytest.raises(G.ProtectedOverride):
        G.load({"governor": {"pre_gate_cold_daily_usd": 3000}})
    # non-governor what-ifs still work
    assert G.load({"scoring": {}})["governor"]["max_boost_daily_usd"] == G.DEFAULTS["governor"]["max_boost_daily_usd"]


def test_governor_plan_endpoint_refuses_cap_overrides(monkeypatch):
    monkeypatch.setenv("WORKER_TOKEN", "t" * 40)
    from common import config as C
    monkeypatch.setattr(C, "WORKER_TOKEN", "t" * 40, raising=False)
    from fastapi.testclient import TestClient
    from app import app
    c = TestClient(app, raise_server_exceptions=False)
    h = {"X-Worker-Token": "t" * 40}
    r = c.post("/growth/governor/plan", json={"state": state(), "now": NOW.isoformat(), "audit": False,
                                              "config_overrides": {"governor": {"max_cold_daily_usd": 5e6}}}, headers=h)
    assert r.status_code == 422
    r = c.post("/growth/governor/plan", json={"state": state(), "now": NOW.isoformat(), "audit": False}, headers=h)
    assert r.status_code == 200 and r.json()["boosts"][0]["approved_daily_usd"] <= G.DEFAULTS["governor"]["max_boost_daily_usd"]


def test_execute_refuses_foreign_config_fingerprint():
    cfg = G.load()
    cfg2 = dict(cfg)
    cfg2["governor"] = dict(cfg["governor"], max_boost_daily_usd=1e6)
    d = GV.decide(state(boosts=[boost(requested_daily_usd=5000, approval={"by": "x", "at": "2026-10-14T00:00:00Z", "max_daily_usd": 5000})]),
                  cfg2, spend_enabled=True, dry_run=False, now=NOW)
    assert d["mode"] == "live" and d["valid"]
    with pytest.raises(GV.GovernorRefused, match="config_fingerprint"):
        GV.execute(d, {"by": "g", "decision_hash": d["state_hash"]}, spend_enabled=True, dry_run=False)
    # the operator's own config still reaches the (unwired) executor
    d = GV.decide(state(), cfg, spend_enabled=True, dry_run=False, now=NOW)
    res = GV.execute(d, {"by": "g", "decision_hash": d["state_hash"]}, spend_enabled=True, dry_run=False)
    assert res["executed"] is False and "no ad API client" in res["reason"]
