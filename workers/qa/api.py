"""QA worker endpoints: POST /qa (n8n 'Worker: Deterministic QA') and POST /qa/score (routing only)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from common import config
from common.auth import require_token
from qa import qa, scoring

router = APIRouter(tags=["qa"], dependencies=[Depends(require_token)])


@router.post("/qa")
def qa_endpoint(body: dict[str, Any]) -> dict:
    if not body.get("video_url"):
        raise HTTPException(status_code=422, detail="video_url required")
    return qa.run(body)          # errors -> sanitised by common/errors.py (AUDIT L12)


@router.post("/qa/score")
def score_endpoint(body: dict[str, Any]) -> dict:
    return scoring.score(body.get("metrics") or {}, vision_decision=body.get("vision_decision"),
                         trusted=bool(body.get("trusted")), risk_tier=body.get("risk_tier", "green"),
                         attempts=int(body.get("attempts", 1)), uniqueness_allow=body.get("uniqueness_allow", True),
                         judge_passed=body.get("judge_passed"), require_judge=config.REQUIRE_JUDGE)
