"""Growth endpoints (all behind common/auth.require_token like every other worker route).

  POST /growth/metrics/normalize   raw platform captures (+ DB rollups) -> post_metrics snapshots at 1/3/6/24/72 h
  POST /growth/metrics/fetch       live pull for listed posts (GROWTH_LIVE_METRICS=1 only) -> same shape
  POST /growth/baselines           post_metrics history -> page_baselines rows
  POST /growth/score               snapshots + baselines -> post_scores rows (class WINNER/PROMISING/NORMAL/LOSER)
  POST /growth/actions             scores + posts + pages -> remix_jobs / boost_queue / pin suggestions / downweights
  POST /growth/allocate            page x platform x day -> tomorrow's slot plan (Thompson sampling)
  POST /growth/governor/plan       state -> action plan (dry-run unless SPEND_ENABLED=1 and GROWTH_DRY_RUN=0) + audit
  POST /growth/governor/execute    executor stub: refuses unless enabled, live and human-approved; wires no ad API
  GET  /growth/config              effective config (+ fingerprint) and the env switches
  GET  /growth/governor/audit      audit-chain verification
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from common import exceptions as exc_client
from common import supabase
from common.auth import require_token
from growth import approvals
from growth import actions, adapters, allocator, baselines, config as G, governor, scoring, snapshots
from growth import health, learning, scorecard, variants

router = APIRouter(prefix="/growth", tags=["growth"], dependencies=[Depends(require_token)])


def _now(x) -> datetime | None:
    if x is None:
        return None
    d = snapshots.parse_dt(x)
    if d is None:
        raise ValueError("now must be an ISO-8601 timestamp")
    return d


class PostIn(BaseModel):
    post_id: str
    page_id: Optional[str] = None
    platform: str
    published_at: str
    external_post_id: Optional[str] = None
    duration_s: Optional[float] = None
    captures: list[dict[str, Any]] = Field(default_factory=list)      # raw platform payloads or already-parsed captures
    raw_format: str = "platform"                                      # "platform" (adapter parses) | "capture"
    rollups: dict[str, Any] = Field(default_factory=dict)             # keyword_comments / optins / members (DB facts)


class NormalizeRequest(BaseModel):
    posts: list[PostIn]
    now: Optional[str] = None
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/metrics/normalize")
def normalize_endpoint(req: NormalizeRequest) -> dict:
    cfg = G.load(req.config_overrides)
    now = _now(req.now) or datetime.now(timezone.utc)
    out, errors = [], []
    for p in req.posts:
        try:
            caps = []
            for c in p.captures:
                if p.raw_format == "platform":
                    parsed = adapters.parse(p.platform, c.get("raw") or c, duration_s=p.duration_s, captured_at=c.get("captured_at"))
                    caps.append(parsed)
                else:
                    caps.append(c)
            res = snapshots.build(p.model_dump(), caps, p.rollups, cfg, now=now)
            out.append(res)
        except ValueError as e:
            errors.append({"post_id": p.post_id, "error": str(e)[:200]})
    return {"results": out, "snapshots": [s for r in out for s in r["snapshots"]], "errors": errors,
            "config_version": cfg["version"]}


class FetchRequest(BaseModel):
    posts: list[PostIn]
    tokens: dict[str, str] = Field(default_factory=dict)              # platform -> bearer token (from Vault via n8n)
    now: Optional[str] = None
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/metrics/fetch")
def fetch_endpoint(req: FetchRequest) -> dict:
    cfg = G.load(req.config_overrides)
    now = _now(req.now) or datetime.now(timezone.utc)
    if not G.GROWTH_LIVE_METRICS:
        return {"results": [], "snapshots": [], "errors": [{"post_id": p.post_id, "error": "live metrics disabled"} for p in req.posts],
                "live": False}
    out, errors = [], []
    for p in req.posts:                                  # pragma: no cover - needs live APIs
        tok = req.tokens.get(p.platform)
        try:
            if not tok:
                raise ValueError(f"no token for {p.platform}")
            kw = {}
            if p.platform == "youtube":
                kw = {"start": p.published_at[:10], "end": now.date().isoformat()}
            cap = adapters.fetch(p.platform, p.model_dump(), tok, **kw)
            cap["captured_at"] = now.isoformat()
            res = snapshots.build(p.model_dump(), list(p.captures) + [cap], p.rollups, cfg, now=now)
            res["capture"] = cap
            out.append(res)
        except ValueError as e:
            errors.append({"post_id": p.post_id, "error": str(e)[:200]})
    return {"results": out, "snapshots": [s for r in out for s in r["snapshots"]], "errors": errors, "live": True}


class BaselineRequest(BaseModel):
    history: list[dict[str, Any]]                                     # post_metrics rows, any pages/platforms/horizons
    pages: Optional[list[str]] = None                                 # restrict output to these page_ids
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/baselines")
def baselines_endpoint(req: BaselineRequest) -> dict:
    cfg = G.load(req.config_overrides)
    groups: dict[tuple, list[dict]] = {}
    net: dict[tuple, list[dict]] = {}
    for s in req.history:
        if s.get("horizon_h") not in G.HORIZONS or s.get("platform") not in G.PLATFORMS:
            continue
        groups.setdefault((str(s.get("page_id")), s["platform"], int(s["horizon_h"])), []).append(s)
        net.setdefault((s["platform"], int(s["horizon_h"])), []).append(s)
    keys = set(groups)
    if req.pages:
        for pid in req.pages:
            for pl in G.PLATFORMS:
                for h in G.HORIZONS:
                    keys.add((str(pid), pl, h))
    rows = []
    for page_id, platform, h in sorted(keys):
        page_hist = groups.get((page_id, platform, h), [])
        others = [s for s in net.get((platform, h), []) if str(s.get("page_id")) != page_id]
        rows.append(baselines.compute(page_id, platform, h, page_hist, others, cfg))
    return {"baselines": rows, "config_version": cfg["version"]}


class ScoreRequest(BaseModel):
    snapshots: list[dict[str, Any]]
    baselines: list[dict[str, Any]] = Field(default_factory=list)
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/score")
def score_endpoint(req: ScoreRequest) -> dict:
    cfg = G.load(req.config_overrides)
    rows = scoring.score_many(req.snapshots, req.baselines, cfg)
    return {"scores": rows, "winners": [r for r in rows if r["class"] == "WINNER"],
            "counts": {c: sum(1 for r in rows if r["class"] == c) for c in G.CLASSES}, "config_version": cfg["version"]}


class ActionsRequest(BaseModel):
    scores: list[dict[str, Any]]
    posts: list[dict[str, Any]] = Field(default_factory=list)         # arm, caption, burned_in_text, evidence, set_code...
    pages: list[dict[str, Any]] = Field(default_factory=list)         # id, slug, status, locale, page_dna
    recent_remixes: list[dict[str, Any]] = Field(default_factory=list)
    ad_texts: dict[str, dict[str, str]] = Field(default_factory=dict)  # post_id -> {primary_text, headline, ...}
    now: Optional[str] = None
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/actions")
def actions_endpoint(req: ActionsRequest) -> dict:
    cfg = G.load(req.config_overrides)
    return actions.plan(req.scores, req.posts, req.pages, cfg, now=_now(req.now), recent_remixes=req.recent_remixes,
                        ad_texts=req.ad_texts)


class AllocateRequest(BaseModel):
    page: dict[str, Any]
    platform: str
    date: Optional[str] = None
    observations: list[dict[str, Any]] = Field(default_factory=list)  # {arm_key|arm, reward, at, weight}
    cadence: Optional[int] = None
    recent: list[dict[str, Any]] = Field(default_factory=list)        # recent slots/briefs on this page (uniqueness)
    used_bits: list[str] = Field(default_factory=list)
    seed: Optional[int] = None
    now: Optional[str] = None
    benched: dict[str, str] = Field(default_factory=dict)             # gene -> until (scorecard bench)
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/allocate")
def allocate_endpoint(req: AllocateRequest) -> dict:
    cfg = G.load(req.config_overrides)
    if req.platform not in G.PLATFORMS:
        raise ValueError("platform must be one of " + ", ".join(G.PLATFORMS))
    now = _now(req.now)
    return allocator.plan_day(req.page, req.platform, req.date or allocator.tomorrow(now), req.observations, cfg,
                              cadence=req.cadence, recent=req.recent, used_bits=req.used_bits, seed=req.seed, now=now,
                              benched=req.benched)


class ScorecardRequest(BaseModel):
    reads: list[dict[str, Any]]                                       # scorecard.read_from_capture rows
    history: list[dict[str, Any]] = Field(default_factory=list)       # [{page_id, platform, horizon_h, raw}] oldest first
    posts: list[dict[str, Any]] = Field(default_factory=list)
    pages: list[dict[str, Any]] = Field(default_factory=list)
    recent_remixes: list[dict[str, Any]] = Field(default_factory=list)
    gene_history: dict[str, list[float]] = Field(default_factory=dict)
    benched: dict[str, str] = Field(default_factory=dict)
    now: Optional[str] = None
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/scorecard")
def scorecard_endpoint(req: ScorecardRequest) -> dict:
    """Score reads (0-100 per component, table post_scores_components) and queue the scorecard actions."""
    cfg = G.load(req.config_overrides)
    hist: dict[tuple, list[dict]] = {}
    for h in req.history:
        hist.setdefault((h.get("page_id"), h.get("platform"), int(h.get("horizon_h") or 0)), []).append(h.get("raw") or {})
    cards = scorecard.score_many(req.reads, hist, cfg)
    plan = actions.scorecard_plan(cards, req.posts, req.pages, cfg, now=_now(req.now), recent_remixes=req.recent_remixes,
                                  gene_history=req.gene_history, benched=req.benched)
    return {"cards": cards, "rows": [scorecard.db_row(c) for c in cards], "actions": plan, "config_version": cfg["version"]}


class VariantsRequest(BaseModel):
    master: dict[str, Any]
    n: int = Field(default=2, ge=0, le=20)
    page_age_days: int = 30
    trials_today: int = 0
    ig_published_24h: int = 0
    live: list[dict[str, Any]] = Field(default_factory=list)          # live variants on the page (30 d)
    auto_taken: list[list[str]] = Field(default_factory=list)         # [page, body_id] with an SS_PERFORMANCE trial
    now: Optional[str] = None
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/variants")
def variants_endpoint(req: VariantsRequest) -> dict:
    """TEST variants (IG Trial Reels) for one master, capped by the ramp and the IG hard stop, gated by uniqueness."""
    cfg = G.load(req.config_overrides)
    budget = variants.trial_budget(req.page_age_days, req.trials_today, req.ig_published_24h, cfg)
    vs = variants.generate(req.master, min(req.n, budget), existing=[v for v in req.live if v.get("master_id") ==
                                                                     req.master.get("master_id")], cfg=cfg)
    variants.assign_trial_params(vs, {tuple(x) for x in req.auto_taken})
    acc, rej = variants.gate(vs, req.live, now=_now(req.now))
    return {"variants": acc, "rejected": rej, "budget": budget, "config_version": cfg["version"]}


class ReadoutRequest(BaseModel):
    cards: list[dict[str, Any]]
    benched: dict[str, str] = Field(default_factory=dict)
    gate_report: dict[str, Any] = Field(default_factory=dict)        # tools/refit_gate.py report
    plan: dict[str, Any] = Field(default_factory=dict)               # last /growth/scorecard actions
    week_of: str
    post: bool = True


@router.post("/readout")
def readout_endpoint(req: ReadoutRequest) -> dict:
    """Weekly plain-English readout -> /admin/exceptions (and so the 07:00 digest). Best effort."""
    text = learning.weekly_readout(req.cards, req.benched, req.gate_report, learning.next_tests_from(req.plan), req.week_of)
    posted = learning.post_readout(text, req.week_of) if req.post else {"status": "not_posted"}
    return {"text": text, "posted": posted}


class GovernorRequest(BaseModel):
    state: dict[str, Any]
    now: Optional[str] = None
    audit: bool = True
    actor: str = "n8n"
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/governor/plan")
def governor_plan_endpoint(req: GovernorRequest) -> dict:
    cfg = G.load(req.config_overrides)
    state = approvals.attach(req.state)
    d = governor.decide(state, cfg, now=_now(req.now))
    if req.audit:
        d["audit"] = governor.append_audit(d, actor=req.actor)
    # Boosts that qualify but have no named human approval go to /admin/exceptions (idempotent per boost).
    queued = []
    for b in approvals.pending(state):
        key = str(b.get("boost_id") or b.get("post_id") or "")
        if not key:
            continue
        r = exc_client.post_exception("boost_approval", f"Boost {key}: ${b.get('requested_daily_usd')}/day requested",
                                      source="governor", ref=str(b.get("post_id") or key), dedupe_key=f"boost:{key}",
                                      detail="WINNER, compliance pass, judge passed. Approve a daily ceiling or reject.",
                                      payload={"boost_id": key, "requested_daily_usd": b.get("requested_daily_usd"),
                                               "post_id": b.get("post_id")})
        queued.append({"boost_id": key, **r})
    d["approval_requests"] = queued
    return d


class BoostApprovalIn(BaseModel):
    boost_id: str
    approval: dict[str, Any]
    exception_id: Optional[str] = None


@router.post("/approvals/boost")
def boost_approval_endpoint(req: BoostApprovalIn) -> dict:
    """The members app records a person's boost approval (by, at, max_daily_usd). Spends nothing."""
    res = approvals.record(req.boost_id, req.approval, exception_id=req.exception_id)
    if res.get("ok"):
        governor.append_audit({"boost_approval": res["record"]}, actor=f"human:{res['record']['approval']['by']}")
    return res


class HealthRequest(BaseModel):
    posts: list[dict[str, Any]]                                        # account, platform, published_at, views, likes
    now: Optional[str] = None
    config_overrides: dict[str, Any] = Field(default_factory=dict)


@router.post("/health")
def health_endpoint(req: HealthRequest) -> dict:
    """POSTDB Rule 0: per-account distribution state (SUPPRESSED / WATCH / DORMANCY_RISK / HEALTHY / NEW)."""
    cfg = G.load(req.config_overrides)
    now = health._dt(req.now) if req.now else None
    rows = health.check(req.posts, cfg, now)
    return {"accounts": rows, "alerts": [r for r in rows if r["state"] in ("SUPPRESSED", "DORMANCY_RISK")],
            "config_version": cfg["version"]}


@router.get("/summary")
def summary_endpoint() -> dict:
    """For /admin/today and the 7am digest: reach and post scores (when the pipeline DB is connected) and the
    governor's last plan with its BLITZ §9 rule lines and §11 graduation checks. Missing data stays null."""
    last = None
    p = governor.audit_path()
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if isinstance(e.get("decision"), dict) and "totals" in e["decision"]:
                last = e["decision"]
    gov = None
    if last:
        rules = ((last.get("gates") or {}).get("rules") or {}).get("rules") or {}
        grad = (last.get("gates") or {}).get("graduation")
        num = lambda x: x if isinstance(x, (int, float)) and not isinstance(x, bool) else None  # noqa: E731
        gov = {"status": last.get("status", "unknown"), "mode": last.get("mode", "dry_run"),
               "spend_enabled": bool(last.get("spend_enabled")),
               "planned_daily_usd": float((last.get("totals") or {}).get("planned_daily_usd") or 0),
               "decided_at": last.get("decided_at"),
               "blitz9": [{"name": k, "status": r.get("status", "?"), "value": num(r.get("value", r.get("rate"))),
                           "line": r.get("line"), "why": r.get("why")} for k, r in rules.items()],
               "graduation": None if not grad else {
                   "passed": bool(grad.get("passed")),
                   "checks": [{"name": k, "status": "pass" if c.get("pass") else "fail", "value": num(c.get("value")),
                               "line": c.get("line"), "why": c.get("why")} for k, c in (grad.get("checks") or {}).items()]}}
    reach, posts = None, []
    if supabase.enabled():  # pragma: no cover - needs a live project
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        rows = supabase.select("post_scores", {"select": "post_id,views,score,class", "horizon_h": "eq.24",
                               "scored_at": f"gte.{since}", "limit": "2000"})
        posts = [{"post_id": str(r["post_id"]), "views_24h": r.get("views"), "score": r.get("score"),
                  "class": r.get("class")} for r in rows]
        reach = sum(int(r.get("views") or 0) for r in rows)
    return {"reach_24h": reach, "posts": posts, "governor": gov}


class ExecuteRequest(BaseModel):
    decision: dict[str, Any]
    approval: Optional[dict[str, Any]] = None


@router.post("/governor/execute")
def governor_execute_endpoint(req: ExecuteRequest) -> dict:
    try:
        res = governor.execute(req.decision, req.approval)
        governor.append_audit({"execute": res, "state_hash": req.decision.get("state_hash")}, actor="executor")
        return {"ok": True, **res}
    except governor.GovernorRefused as e:
        governor.append_audit({"execute_refused": str(e), "state_hash": (req.decision or {}).get("state_hash")}, actor="executor")
        return {"ok": False, "executed": False, "refused": str(e)}


@router.get("/governor/audit")
def governor_audit_endpoint() -> dict:
    return governor.verify_audit()


@router.get("/config")
def config_endpoint() -> dict:
    cfg = G.load()
    return {"config": cfg, "fingerprint": G.fingerprint(cfg),
            "env": {"SPEND_ENABLED": G.SPEND_ENABLED, "GROWTH_DRY_RUN": G.GROWTH_DRY_RUN,
                    "GROWTH_LIVE_METRICS": G.GROWTH_LIVE_METRICS, "METRICS_ALLOWED_HOSTS": G.METRICS_ALLOWED_HOSTS},
            "mode": "live" if (G.SPEND_ENABLED and not G.GROWTH_DRY_RUN) else "dry_run"}
