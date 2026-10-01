"""POST /package: normalise the LLM packaging and run compliance pass 2 (n8n 'Worker: Package + Pass 2').

Response keeps the shape the n8n 'Pass 2 clean?' IF and 'Worker: Render Platform Variants' read:
{packaging, pass2_ok, pass2_issues, links, notes, compliance}
"""
from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from common import config
from common.auth import require_token
from compliance import judge as J
from compliance import scanner
from packager.packager import package

router = APIRouter(tags=["packaging"], dependencies=[Depends(require_token)])


class PackageRequest(BaseModel):
    packaging: dict[str, Any]
    page_dna: dict[str, Any] = Field(default_factory=dict)
    script: Optional[dict[str, Any]] = None
    locale: str = "en-US"
    market: str = "US"
    reviewer_signed: bool = False
    page_slug: str = ""
    brief_id: str = ""
    site_base_url: Optional[str] = None
    post_ids: Optional[dict[str, str]] = None
    transcript: Optional[str] = None
    burned_in_text: Optional[list[str]] = None
    upstream_issues: list[dict[str, Any]] = Field(default_factory=list)
    paid_partnership: bool = False


def run(req: PackageRequest) -> dict:
    # AUDIT M4: the reviewer gate comes from the worker env only; request fields are ignored.
    reviewer_signed = config.REVIEWER_SIGNED
    res = package(req.packaging, page_dna=req.page_dna, script=req.script, locale=req.locale, market=req.market,
                  reviewer_signed=reviewer_signed, page_slug=req.page_slug, brief_id=req.brief_id,
                  site_base_url=req.site_base_url or req.page_dna.get("site_base_url")
                  or os.environ.get("SITE_BASE_URL", "https://example.com"), post_ids=req.post_ids)
    comp = scanner.scan(req.script, pass_no=2, locale=req.locale, reviewer_signed=reviewer_signed,
                        packaging=res["packaging"], transcript=req.transcript, burned_in_text=req.burned_in_text,
                        paid_partnership=req.paid_partnership)
    issues = [{"where": b.get("where", "packaging"), "id": b["rule"], "match": b["span"], "severity": "block"}
              for b in comp["blocks"]]
    issues += [{"where": "packaging", "id": "REQUIRE", "match": m, "severity": "block"} for m in comp["required_missing"]]
    issues += [{"where": r.get("where", "packaging"), "id": r["rule"], "match": r["from"], "severity": "revise"}
               for r in comp["rewrites"]]
    # Layer 2: the mandatory LLM judge on exactly what gets published (captions, burned-in text, transcript).
    j = None
    if config.REQUIRE_JUDGE:
        j = J.judge({"pass": 2, "script": req.script, "packaging": res["packaging"], "transcript": req.transcript,
                     "burned_in_text": req.burned_in_text}, comp["regex_hits"], market=req.market, locale=req.locale,
                    page_slug=req.page_slug)
        if not scanner.judge_passed(j):
            issues.append({"where": "packaging", "id": "LLM-JUDGE", "severity": "human",
                           "match": f"judge {j.get('status')}: {j.get('verdict') or j.get('reason', '')}"[:200]})
    # MB-EX spans in captions need the judge's semantic OK
    if not scanner.judge_passed(j):
        issues += [{"where": h["where"], "id": h["id"], "match": h["match"], "severity": "mbex_confirm"}
                   for h in comp["mbex_candidates"]]
    final = scanner.combine_with_judge(comp, j, require_judge=config.REQUIRE_JUDGE)
    return {**res, "pass2_ok": not issues, "pass2_issues": issues, "upstream_issues": req.upstream_issues,
            "judge": j, "final": final,
            "compliance": {k: comp[k] for k in ("verdict", "blocks", "rewrites", "required_missing", "flags")}}


@router.post("/package")
def package_endpoint(req: PackageRequest) -> dict:
    return run(req)


class FallbackRequest(BaseModel):
    day: str
    items: list[dict[str, Any]]


@router.post("/package/fallback")
def fallback_endpoint(req: FallbackRequest) -> dict:
    """Daily manual post pack (packager/fallback.py). Writes files under OUTPUT_DIR/packs; posts nothing."""
    from common import config as _C
    from packager import fallback
    return fallback.build_pack(req.day, req.items, _C.OUTPUT_DIR / "packs")
