"""Discover endpoints (behind common/auth.require_token like every worker route). Nothing here posts or spends.

  GET  /discover/seeds    seed queries + creators (data/discover/seeds.json) and counts
  POST /discover/crawl    pushed source payloads -> niche rows (posts.csv shape + niche_posts rows); with
                          DISCOVER_LIVE=1 and live=true, crawls the seeds itself (official APIs -> yt-dlp -> public)
  POST /discover/trends   niche rows -> daily top-20, weekly top-50, rising genes, transfer opportunities,
                          gate-refit rows, allocator exploration observations
  POST /discover/remake   niche rows + trend feeds -> plagiarism-guarded remake briefs for the script queue
  POST /discover/value    scorecard cards + attribution -> value scores (virality x MRR), MRR action plan, weekly readout
"""
from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from common import config
from common.auth import require_token
from discover import crawl, normalize, remake, trends
from growth import actions, scorecard
from growth import config as G
from growth import snapshots

router = APIRouter(prefix="/discover", tags=["discover"], dependencies=[Depends(require_token)])


def _now(x):
    if x is None:
        return None
    d = snapshots.parse_dt(x)
    if d is None:
        raise HTTPException(422, "now must be an ISO-8601 timestamp")
    return d


def load_seeds() -> dict:
    return json.loads((config.SPEC_DIR / "data" / "discover" / "seeds.json").read_text())


@router.get("/seeds")
def seeds():
    s = load_seeds()
    return {"counts": {"queries": len(s["queries"]), "creators": len(s["creators"]),
                       "to_verify": sum(1 for c in s["creators"] if c.get("status") == "to_verify")}, **s}


class CrawlIn(BaseModel):
    mode: str = "daily"
    payloads: list[dict[str, Any]] = Field(default_factory=list)
    live: bool = False
    now: Optional[str] = None


@router.post("/crawl")
def crawl_ep(body: CrawlIn):
    if body.mode not in ("daily", "stream"):
        raise HTTPException(422, "mode must be daily or stream")
    now = _now(body.now)
    if body.live:
        if not crawl.LIVE:
            raise HTTPException(409, "live crawling is off (DISCOVER_LIVE=0)")
        res = crawl.run(load_seeds(), crawl.Crawler(crawl.live_fetcher(), crawl.live_runner()), now=now, mode=body.mode)
    else:
        res = crawl.from_payloads(body.payloads, now=now, mode=body.mode)
    res["niche_posts"] = [normalize.db_row(r) for r in res["rows"]]
    res["posts_csv"] = [normalize.posts_csv_row(r) for r in res["rows"]]
    return res


class TrendsIn(BaseModel):
    rows: list[dict[str, Any]]
    now: Optional[str] = None
    cfg: dict[str, Any] = Field(default_factory=dict)


@router.post("/trends")
def trends_ep(body: TrendsIn):
    return trends.detect(body.rows, now=_now(body.now), cfg=body.cfg)


class RemakeIn(BaseModel):
    rows: list[dict[str, Any]]
    feeds: dict[str, Any] = Field(default_factory=dict)
    max_items: int = Field(20, ge=1, le=100)
    now: Optional[str] = None


@router.post("/remake")
def remake_ep(body: RemakeIn):
    q = remake.queue(body.rows, body.feeds, max_items=body.max_items, now=_now(body.now))
    return {"remake_queue": q, "count": len(q)}


class ValueIn(BaseModel):
    cards: list[dict[str, Any]]
    attribution: dict[str, dict[str, Any]] = Field(default_factory=dict)     # post_id -> {views, mrr_usd, buyers}
    history: list[dict[str, Any]] = Field(default_factory=list)
    mode: str = "default"
    posts: list[dict[str, Any]] = Field(default_factory=list)
    pages: list[dict[str, Any]] = Field(default_factory=list)
    current_mrr_usd: float = 0.0
    now: Optional[str] = None


@router.post("/value")
def value_ep(body: ValueIn):
    cfg = G.load()
    try:
        vals = [scorecard.value_score(c, body.attribution.get(str(c.get("post_id")), {}), body.history, cfg, body.mode)
                for c in body.cards]
    except ValueError as e:
        raise HTTPException(422, str(e)) from e
    plan = actions.mrr_plan(vals, body.posts, body.pages, cfg, now=_now(body.now), current_mrr_usd=body.current_mrr_usd)
    return {"values": vals, "plan": plan, "readout": actions.weekly_readout(vals, cfg)}
