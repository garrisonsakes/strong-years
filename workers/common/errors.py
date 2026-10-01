"""AUDIT L12: map internal failures to sanitised HTTP errors. ffmpeg stderr, paths and upstream bodies are
logged server-side under an error id and never echoed to the caller."""
from __future__ import annotations

import logging
import uuid

import httpx
from fastapi import Request
from fastapi.responses import JSONResponse

from common.media import MediaError
from common.storage import FetchError

log = logging.getLogger("workers")


def classify(e: Exception) -> tuple[int, str]:
    if isinstance(e, FetchError):
        return 422, str(e)                               # our own policy messages carry no internals
    if isinstance(e, KeyError):
        return 422, f"missing field: {e.args[0]!s}"[:120]
    if isinstance(e, (httpx.HTTPError,)):
        return 502, "upstream request failed"
    if isinstance(e, MediaError):
        return 500, "media processing failed"
    if isinstance(e, FileNotFoundError):
        return 422, "input file not found"
    if isinstance(e, ValueError):
        msg = str(e).splitlines()[0][:200] if str(e) else "invalid input"
        return 422, msg if "/" not in msg else "invalid input"
    return 500, "internal error"


def install(app) -> None:
    async def handler(request: Request, exc: Exception):
        status, msg = classify(exc)
        eid = uuid.uuid4().hex[:12]
        log.error("worker error %s on %s: %r", eid, request.url.path, exc)
        return JSONResponse(status_code=status, content={"detail": msg, "error_id": eid})
    for t in (FetchError, KeyError, httpx.HTTPError, MediaError, FileNotFoundError, ValueError, Exception):
        app.add_exception_handler(t, handler)
