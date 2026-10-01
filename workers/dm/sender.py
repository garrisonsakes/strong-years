"""Delivery of queued DM actions to the Meta Graph API. OFF by default.

Nothing is sent unless DM_SEND_ENABLED=1 and a page access token is configured (META_PAGE_TOKEN_<PAGE_ID>, held in
the secrets vault). With it off, queued actions stay in the outbox as "dry_run" so a person can read exactly what
would have gone out. Messages are sent with messaging_type RESPONSE and never with a message tag.
"""
from __future__ import annotations

import os

GRAPH = "https://graph.facebook.com/v21.0"


def enabled() -> bool:
    return os.environ.get("DM_SEND_ENABLED", "0") == "1"


def build_request(action: dict) -> tuple[str, dict] | None:
    """(url, json body) for one action, or None for actions that are not Graph sends."""
    if action.get("type") == "public_reply":
        return f"{GRAPH}/{action['comment_id']}/replies" if action.get("platform") == "ig" else f"{GRAPH}/{action['comment_id']}/comments", \
            {"message": action["text"]}
    if action.get("type") != "dm":
        return None
    recipient = {"comment_id": action["private_reply_to_comment"]} if action.get("private_reply_to_comment") else {"id": action["to"]}
    msg: dict = {"text": action["text"][:1000]}
    if action.get("quick_replies"):
        msg["quick_replies"] = [{"content_type": "text", "title": q["title"][:20], "payload": q["payload"]} for q in action["quick_replies"][:13]]
    if action.get("buttons"):
        btns = [{"type": "web_url", "url": b["url"], "title": b["title"][:20]} if "url" in b else
                {"type": "postback", "title": b["title"][:20], "payload": b["payload"]} for b in action["buttons"][:3]]
        msg = {"attachment": {"type": "template", "payload": {"template_type": "button", "text": action["text"][:640], "buttons": btns}}}
    assert "tag" not in action, "automation never uses message tags"
    return f"{GRAPH}/{action.get('page') or 'me'}/messages", {"recipient": recipient, "messaging_type": "RESPONSE", "message": msg}


def deliver(action: dict, client=None) -> dict:  # pragma: no cover - live path, needs Meta credentials
    req = build_request(action)
    if req is None:
        return {"status": "not_a_send"}
    if not enabled():
        return {"status": "dry_run", "request": req[1]}
    token = os.environ.get(f"META_PAGE_TOKEN_{action.get('page')}", "")
    if not token:
        return {"status": "error", "error": "no page token"}
    import httpx
    c = client or httpx.Client(timeout=15)
    r = c.post(req[0], json=req[1], headers={"Authorization": f"Bearer {token}"})
    return {"status": "sent" if r.status_code < 300 else "error", "http_status": r.status_code}
