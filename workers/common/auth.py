"""Worker authentication (AUDIT H9): fail closed.

Accepted credentials, on every endpoint except the bare /health liveness probe:
  1. X-Worker-Token: <WORKER_TOKEN>                      (the n8n header credential)
  2. X-Worker-Timestamp: <unix seconds> + X-Worker-Signature: sha256=<hex HMAC-SHA256(WORKER_TOKEN, ts + "." + body)>
     (replay window HMAC_MAX_SKEW_S)
With WORKER_TOKEN unset every request gets 503, unless DEV_NO_AUTH=1 (local development only).
"""
from __future__ import annotations

import hashlib
import hmac
import time

from fastapi import HTTPException, Request

from common import config


def sign(body: bytes, ts: int | None = None, token: str | None = None) -> dict:
    """Headers for an HMAC-signed request (used by tests and any non-n8n caller)."""
    ts = int(ts if ts is not None else time.time())
    mac = hmac.new((token or config.WORKER_TOKEN).encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return {"X-Worker-Timestamp": str(ts), "X-Worker-Signature": f"sha256={mac}"}


def auth_mode() -> str:
    if config.WORKER_TOKEN:
        return "token"
    return "disabled (DEV_NO_AUTH=1)" if config.DEV_NO_AUTH else "unconfigured (fail closed)"


async def require_token(request: Request) -> None:
    expected = config.WORKER_TOKEN
    if not expected:
        if config.DEV_NO_AUTH:
            return
        raise HTTPException(status_code=503, detail="worker auth not configured: set WORKER_TOKEN (or DEV_NO_AUTH=1 for local dev)")
    tok = request.headers.get("x-worker-token")
    if tok is not None:
        if hmac.compare_digest(tok, expected):
            return
        raise HTTPException(status_code=401, detail="invalid credentials")
    sig, ts = request.headers.get("x-worker-signature"), request.headers.get("x-worker-timestamp")
    if sig and ts and ts.isdigit() and abs(time.time() - int(ts)) <= config.HMAC_MAX_SKEW_S:
        body = await request.body()
        want = sign(body, int(ts), expected)["X-Worker-Signature"]
        if hmac.compare_digest(sig, want):
            return
    raise HTTPException(status_code=401, detail="invalid credentials")
