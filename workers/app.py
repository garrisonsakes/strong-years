"""FastAPI app for the Chang & Sun content-factory workers.

One image, every endpoint; deploy it twice (RENDER_WORKER_URL for render, QA_WORKER_URL for QA) or once.
  render : POST /voice/stitch  POST /assemble  POST /variants
  qa     : POST /qa  POST /qa/score
  gates  : POST /compliance/scan  POST /compliance/judge  GET /compliance/selftest
           POST /uniqueness/check  POST /uniqueness/fingerprint  POST /package
  growth : POST /growth/metrics/normalize  /growth/metrics/fetch  /growth/baselines  /growth/score  /growth/actions
           /growth/allocate  /growth/governor/plan  /growth/governor/execute  GET /growth/config  /growth/governor/audit
  dm     : GET/POST /dm/webhook (Meta signature, not the worker token)  POST /dm/followups  GET /dm/outbox
  ops    : GET /health (liveness, unauthenticated, no details)  GET /health/details  GET /files/{key}
Every endpoint except /health requires X-Worker-Token or an HMAC signature (common/auth.py, AUDIT H9).
Run: WORKER_TOKEN=... uvicorn app:app --host 0.0.0.0 --port 8080
"""
from __future__ import annotations

import logging
import os
import shutil

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

from assemble import api as render_api
from assemble import c2pa_sign
from common import auth, config, errors, janitor, storage
from compliance import api as compliance_api
from discover import api as discover_api
from dm import api as dm_api
from growth import api as growth_api
from growth import config as growth_config
from packager import api as packaging_api
from qa import api as qa_api
from qa import face, ocr
from uniqueness import api as uniqueness_api
from uniqueness import audiofp

config.ensure_dirs()
log = logging.getLogger("workers")
if not config.WORKER_TOKEN and not config.DEV_NO_AUTH:
    log.error("WORKER_TOKEN is not set: every endpoint will answer 503 (fail closed). Set DEV_NO_AUTH=1 for local dev.")

app = FastAPI(title="ChangSun content workers", version="1.1.0")
errors.install(app)
for r in (render_api.router, qa_api.router, compliance_api.router, uniqueness_api.router, packaging_api.router,
          growth_api.router, dm_api.router):
    app.include_router(r)
app.include_router(discover_api.router)


async def _files_auth(request: Request) -> None:
    if not config.PUBLIC_FILES:
        await auth.require_token(request)


@app.get("/files/{key:path}", dependencies=[Depends(_files_auth)])
def files(key: str):
    """Local outputs when R2 isn't configured. Authenticated unless PUBLIC_FILES=1; confined to OUTPUT_DIR."""
    try:
        p = storage.confine(config.OUTPUT_DIR, key)
    except ValueError:
        raise HTTPException(status_code=404, detail="not found") from None
    if not p.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(p)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/health/details", dependencies=[Depends(auth.require_token)])
def health_details() -> dict:
    return {
        "ok": True,
        "auth": auth.auth_mode(),
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "tesseract": ocr.available(),
        "chromaprint": audiofp.chromaprint_available(),
        "c2pa_backend": c2pa_sign.backend(),
        "c2pa_cert": "configured" if (config.C2PA_SIGN_CERT and config.C2PA_PRIVATE_KEY)
                     else ("dev (untrusted)" if config.C2PA_ALLOW_DEV_CERT else "missing: masters are unsigned, no auto-publish"),
        "insightface": face.available()[0],
        "syncnet": False,
        "llm_judge": bool(os.environ.get(config.ANTHROPIC_API_KEY_ENV)),
        "reviewer_signed": config.REVIEWER_SIGNED,
        "storage": "r2" if storage.r2_enabled() else "local",
        "disk_free_gb": round(janitor.free_gb(config.WORK_DIR), 1),
        "fetch_allowed_hosts": storage.allowed_hosts(),
        "font": config.CAPTION_FONT.name if config.CAPTION_FONT.exists() else None,
        "growth": {"spend_enabled": growth_config.SPEND_ENABLED, "dry_run": growth_config.GROWTH_DRY_RUN,
                   "live_metrics": growth_config.GROWTH_LIVE_METRICS, "config": growth_config.load()["version"]},
    }
