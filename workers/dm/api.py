"""DM bot endpoints.

  GET  /dm/webhook    Meta's subscription check (hub.verify_token == DM_VERIFY_TOKEN → hub.challenge)
  POST /dm/webhook    Instagram + Messenger events; X-Hub-Signature-256 verified with META_APP_SECRET (fail closed)
  POST /dm/followups  due nudges / check-ins inside each person's 24-hour window (n8n cron; X-Worker-Token)
  GET  /dm/outbox     what is queued (X-Worker-Token); nothing is delivered unless DM_SEND_ENABLED=1
"""
from __future__ import annotations

import hmac
import json
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from common.auth import require_token
from dm.bot import Bot, Store, parse_webhook, verify_signature

router = APIRouter(prefix="/dm", tags=["dm"])
_bot: Bot | None = None


def bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(Store())
    return _bot


@router.get("/webhook")
def verify(mode: str = Query("", alias="hub.mode"), token: str = Query("", alias="hub.verify_token"),
           challenge: str = Query("", alias="hub.challenge")):
    want = os.environ.get("DM_VERIFY_TOKEN", "")
    if mode == "subscribe" and want and hmac.compare_digest(token, want):
        return PlainTextResponse(challenge[:200])
    raise HTTPException(403, "verification failed")


@router.post("/webhook")
async def webhook(request: Request) -> dict:
    secret = os.environ.get("META_APP_SECRET", "")
    if not secret:
        raise HTTPException(503, "META_APP_SECRET not configured")
    body = await request.body()
    if len(body) > 1_000_000 or not verify_signature(secret, body, request.headers.get("x-hub-signature-256")):
        raise HTTPException(401, "bad signature")
    try:
        payload = json.loads(body)
    except ValueError:
        raise HTTPException(400, "invalid json")
    n = 0
    for ev in parse_webhook(payload):
        n += len(bot().handle(ev))
    return {"ok": True, "actions": n}


@router.post("/followups", dependencies=[Depends(require_token)])
def followups() -> dict:
    return {"ok": True, "actions": len(bot().due_followups())}


@router.get("/outbox", dependencies=[Depends(require_token)])
def outbox() -> dict:
    rows = bot().store.outbox()
    return {"queued": len(rows), "actions": rows[-200:]}
