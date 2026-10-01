"""Best-effort Supabase PostgREST access (asset registration, library lookups, sibling fingerprints).
Every function returns None / [] when SUPABASE_URL or SUPABASE_SERVICE_KEY is unset."""
from __future__ import annotations

import uuid

import httpx

from common import config


def enabled() -> bool:
    return bool(config.SUPABASE_URL and config.SUPABASE_SERVICE_KEY)


def _headers(extra: dict | None = None) -> dict:
    h = {"apikey": config.SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {config.SUPABASE_SERVICE_KEY}",
         "Content-Type": "application/json"}
    h.update(extra or {})
    return h


def insert(table: str, row: dict) -> dict | None:  # pragma: no cover - needs a live project
    if not enabled():
        return None
    r = httpx.post(f"{config.SUPABASE_URL}/rest/v1/{table}", json=row,
                   headers=_headers({"Prefer": "return=representation"}), timeout=30)
    r.raise_for_status()
    data = r.json()
    return data[0] if isinstance(data, list) and data else data


def select(path: str, params: dict | None = None) -> list[dict]:  # pragma: no cover - needs a live project
    if not enabled():
        return []
    r = httpx.get(f"{config.SUPABASE_URL}/rest/v1/{path}", params=params, headers=_headers(), timeout=30)
    r.raise_for_status()
    return r.json()


def asset_url(asset_id: str) -> str | None:
    """AUDIT L13: asset_id must be a UUID and goes through `params=`, never string interpolation."""
    aid = str(uuid.UUID(str(asset_id)))            # raises ValueError on anything else ("x&or=...")
    rows = select("assets", {"id": f"eq.{aid}", "select": "public_url"})
    return rows[0]["public_url"] if rows else None
