"""POST /uniqueness/check -> {allow, reasons, comparisons}; POST /uniqueness/fingerprint -> {phash_seq, audio_fp}."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from common import exceptions as exc_client
from common import storage, supabase
from common.auth import require_token
from uniqueness import audiofp, guard, phash

router = APIRouter(prefix="/uniqueness", tags=["uniqueness"], dependencies=[Depends(require_token)])


class Fingerprintable(BaseModel):
    video_url: Optional[str] = None
    phash_seq: Optional[list[str]] = None
    audio_fp: Optional[str] = None

    model_config = {"extra": "allow"}


class CheckRequest(BaseModel):
    candidate: dict[str, Any]
    siblings: Optional[list[dict[str, Any]]] = None      # omit to fetch from Supabase (needs SUPABASE_* env)
    thresholds: dict[str, Any] = Field(default_factory=dict)


def _fill_fingerprints(item: dict) -> dict:
    if item.get("video_url") and (not item.get("phash_seq") or not item.get("audio_fp")):
        p = storage.fetch(item["video_url"])
        item.setdefault("phash_seq", phash.video_phash_seq(p))
        if not item.get("audio_fp"):
            item["audio_fp"] = audiofp.fingerprint(p)
    return item


def fetch_siblings(candidate: dict) -> list[dict]:  # pragma: no cover - needs a live project
    """Recent videos on other pages (14 d) + this page (90 d) with their fingerprints and scripts. [A] PostgREST
    embedding names follow schema.sql FKs (videos.master_asset_id -> assets, videos.script_id -> scripts)."""
    since = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    rows = supabase.select(
        "videos?select=id,page_id,created_at,brief_id,"
        "brief:briefs(idea_id,parent_brief_id,target_date,slot_index),script:scripts(full_text),"
        f"master:assets!master_asset_id(phash_seq,audio_fp)&created_at=gte.{since}&limit=500")
    out = []
    for r in rows:
        out.append({"id": r["id"], "page_id": r["page_id"], "created_at": r["created_at"], "brief_id": r.get("brief_id"),
                    "idea_id": (r.get("brief") or {}).get("idea_id"),
                    "parent_brief_id": (r.get("brief") or {}).get("parent_brief_id"),
                    "scheduled_at": (r.get("brief") or {}).get("target_date"),
                    "script_text": (r.get("script") or {}).get("full_text"),
                    "phash_seq": (r.get("master") or {}).get("phash_seq"),
                    "audio_fp": (r.get("master") or {}).get("audio_fp")})
    return out


@router.post("/check")
def check_endpoint(req: CheckRequest) -> dict:
    cand = _fill_fingerprints(dict(req.candidate))
    source = "request"
    sibs = req.siblings
    if sibs is None:
        sibs, source = (fetch_siblings(cand), "supabase") if supabase.enabled() else ([], "none (SUPABASE_* unset)")
    sibs = [_fill_fingerprints(dict(s)) for s in sibs]
    res = guard.check(cand, sibs, req.thresholds)
    res["siblings_source"] = source
    if not res.get("allow", True):
        cid = str(cand.get("id") or cand.get("variant_id") or cand.get("post_id") or "candidate")
        res["exception"] = exc_client.post_exception(
            "compliance_flag", f"Uniqueness guard denied {cid}", source="uniqueness", ref=cid,
            detail="; ".join(str(r) for r in res.get("reasons", []))[:1500], dedupe_key=f"uniqueness:{cid}",
            payload={"platform": cand.get("platform"), "page": cand.get("page_id") or cand.get("page")})
    return res


@router.post("/fingerprint")
def fingerprint_endpoint(req: Fingerprintable) -> dict:
    p = storage.fetch(req.video_url) if req.video_url else None
    if p is None:
        return {"error": "video_url required"}
    return {"phash_seq": phash.video_phash_seq(p), "audio_fp": audiofp.fingerprint(p),
            "audio_fp_method": "chromaprint" if audiofp.chromaprint_available() else "spectral"}
