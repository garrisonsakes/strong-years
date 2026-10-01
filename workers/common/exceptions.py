"""Client for the members app's exceptions queue (POST {APP_URL}/api/exceptions, Bearer EXCEPTIONS_API_TOKEN).

Used by the compliance "human" route, the uniqueness guard and the spend governor so a person decides in
/admin/exceptions. Best effort and never raises: with APP_URL / EXCEPTIONS_API_TOKEN unset it returns
{"status": "skipped"} and the caller carries on (the pipeline's own human queue still holds the item).
Idempotent on the app side by (type, dedupe_key), so retries and re-runs never duplicate an item.
Payloads carry ids and rule codes only: never message bodies, emails or names.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import httpx

log = logging.getLogger("workers.exceptions")

TYPES = {"compliance_flag", "judge_disagreement", "upload_auth_failure", "refund_review", "chargeback_review",
         "plan_switch_request", "consent_price_mismatch", "crisis_escalation", "boost_approval"}


def _cfg() -> tuple[str, str]:
    return os.environ.get("APP_URL", "").rstrip("/"), os.environ.get("EXCEPTIONS_API_TOKEN", "")


def enabled() -> bool:
    base, token = _cfg()
    return bool(base.startswith("https://") or base.startswith("http://localhost") or base.startswith("http://app")) and len(token) >= 32


def post_exception(type: str, title: str, *, source: str, ref: str | None = None, detail: str = "",
                   severity: str = "normal", dedupe_key: str | None = None, payload: dict[str, Any] | None = None,
                   client: httpx.Client | None = None) -> dict:
    if type not in TYPES:
        return {"status": "error", "error": f"unknown type {type}"}
    if not enabled():
        return {"status": "skipped", "reason": "APP_URL / EXCEPTIONS_API_TOKEN unset"}
    base, token = _cfg()
    body = {"type": type, "title": title[:200], "source": source[:60], "ref": ref, "detail": detail[:4000],
            "severity": severity, "dedupe_key": (dedupe_key or f"{source}:{ref or title}")[:200], "payload": payload or {}}
    try:
        c = client or httpx.Client(timeout=10)
        r = c.post(f"{base}/api/exceptions", json=body, headers={"Authorization": f"Bearer {token}"})
        if r.status_code in (200, 201):
            j = r.json()
            return {"status": "created" if j.get("created") else "exists", "id": j.get("id")}
        return {"status": "error", "http_status": r.status_code}
    except Exception as e:  # noqa: BLE001 - best effort by design
        log.warning("exceptions post failed: %s", e.__class__.__name__)
        return {"status": "error", "error": e.__class__.__name__}
