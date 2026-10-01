"""POST /compliance/scan (pass 1 or 2, optional LLM judge) and POST /compliance/judge."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from common import config
from common.auth import require_token
from common import exceptions as exc_client
from compliance import judge as J
from compliance import scanner

router = APIRouter(prefix="/compliance", tags=["compliance"], dependencies=[Depends(require_token)])


class ScanRequest(BaseModel):
    script: Optional[dict[str, Any]] = None
    text: Optional[str] = None
    evidence: list[str] = Field(default_factory=list)
    pass_no: int = Field(1, alias="pass")
    kind: Optional[str] = None                       # script | snippet (auto)
    reviewer_signed: bool = False
    locale: str = "en-US"
    market: str = "US"
    page_slug: str = ""
    risk_tier: str = "green"
    page_dna: dict[str, Any] = Field(default_factory=dict)
    packaging: Optional[dict[str, Any]] = None       # pass 2: 06_caption_hashtag_writer output
    transcript: Optional[str] = None                 # pass 2: ASR transcript of the master
    burned_in_text: Optional[list[str]] = None       # pass 2: on-screen overlay strings incl. the AI tag
    has_movement: Optional[bool] = None
    paid_partnership: bool = False
    judge: bool = True                               # LLM judge (mandatory when REQUIRE_JUDGE=1: skipping it -> human)

    model_config = {"populate_by_name": True}


@router.post("/scan")
def scan_endpoint(req: ScanRequest) -> dict:
    # AUDIT M4: the reviewer gate comes from the worker env only; request fields are ignored.
    reviewer_signed = config.REVIEWER_SIGNED
    result = scanner.scan(
        req.script, text=req.text, evidence=req.evidence, pass_no=req.pass_no, kind=req.kind,
        reviewer_signed=reviewer_signed, locale=req.locale, packaging=req.packaging, transcript=req.transcript,
        burned_in_text=req.burned_in_text, has_movement=req.has_movement, paid_partnership=req.paid_partnership,
        page_footer=req.page_dna.get("caption_footer"))
    j = None
    if req.judge or config.REQUIRE_JUDGE:
        subject = req.script if req.script is not None else (
            {"pass": 2, "packaging": req.packaging, "transcript": req.transcript, "burned_in_text": req.burned_in_text}
            if req.pass_no == 2 else {"text": req.text})
        j = J.judge(subject, result["regex_hits"], market=req.market, locale=req.locale,
                    page_slug=req.page_slug, risk_tier=req.risk_tier,
                    market_rules=str(req.page_dna.get("market_rules", "")))
        result["judge"] = j
    result["final"] = scanner.combine_with_judge(result, j, require_judge=config.REQUIRE_JUDGE)
    result["exception"] = _queue_for_human(req, result)
    return result


def _h(text: str | None) -> str:
    import hashlib
    return hashlib.sha256((text or "").encode()).hexdigest()[:16]


def _queue_for_human(req: "ScanRequest", result: dict) -> dict | None:
    """The judge's "human" route (and judge vs scanner disagreements) go to /admin/exceptions. Ids and rule codes only."""
    final = result.get("final") or {}
    sid = str((req.script or {}).get("id") or (req.script or {}).get("script_id") or "") if isinstance(req.script, dict) else ""
    ref = sid or None
    j = result.get("judge") or {}
    det, jv = final.get("deterministic"), j.get("verdict") if j.get("status") == "ok" else None
    rules = sorted({str(h.get("id") or h.get("rule")) for h in result.get("regex_hits", [])})[:20]
    if jv and det and jv != det and "block" not in (jv, det):
        return exc_client.post_exception("judge_disagreement", f"Judge says {jv}, scanner says {det} ({sid or 'text'})",
                                         source="compliance", ref=ref, detail="Rules: " + ", ".join(rules),
                                         dedupe_key=f"judge:{sid or _h(req.text)}:{req.pass_no}",
                                         payload={"pass_no": req.pass_no, "deterministic": det, "judge": jv})
    if final.get("verdict") == "human":
        return exc_client.post_exception("compliance_flag", f"Human review needed ({sid or 'text'}, pass {req.pass_no})",
                                         source="compliance", ref=ref,
                                         detail="; ".join(final.get("reasons", []))[:1500] + ("\nRules: " + ", ".join(rules) if rules else ""),
                                         dedupe_key=f"human:{sid or _h(req.text)}:{req.pass_no}",
                                         payload={"pass_no": req.pass_no, "rules": rules})
    return None


class JudgeRequest(BaseModel):
    script: dict[str, Any]
    regex_hits: list[dict[str, Any]] = Field(default_factory=list)
    market: str = "US"
    locale: str = "en-US"
    page_slug: str = ""
    risk_tier: str = "green"
    market_rules: str = ""


@router.post("/judge")
def judge_endpoint(req: JudgeRequest) -> dict:
    return J.judge(req.script, req.regex_hits, market=req.market, locale=req.locale, page_slug=req.page_slug,
                   risk_tier=req.risk_tier, market_rules=req.market_rules)


@router.get("/selftest")
def selftest_endpoint() -> dict:
    from compliance import selftest
    return selftest.run()
