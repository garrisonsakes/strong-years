"""Render worker endpoints used by n8n: POST /voice/stitch, POST /assemble, POST /variants."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from assemble import assembler, variants, voice
from common.auth import require_token

router = APIRouter(tags=["render"], dependencies=[Depends(require_token)])


def _guard(fn, body):
    """Errors propagate to the app-level handlers in common/errors.py (sanitised 422/502/500, AUDIT L12)."""
    return fn(body)


@router.post("/voice/stitch")
def stitch_endpoint(body: dict[str, Any]) -> dict:
    return _guard(voice.stitch, body)


@router.post("/assemble")
def assemble_endpoint(body: dict[str, Any]) -> dict:
    return _guard(assembler.assemble, body)


@router.post("/variants")
def variants_endpoint(body: dict[str, Any]) -> dict:
    return _guard(variants.render_variants, body)
