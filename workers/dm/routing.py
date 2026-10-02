"""Intent → offer routing (MONETIZATION_ENGINE.md §2). Data in dm/offer_routing.json; this file only evaluates it.

The same evaluator exists in app/src/lib/offers/route.ts (the app test checks both read identical data, and
tests/test_offer_routing.py checks the shared fixture vectors). A rule picks an offer FAMILY; prices come from the
catalog and the visitor's sticky front-end cell, never from a rule.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROUTING_PATH = Path(__file__).resolve().parent / "offer_routing.json"
_cache: dict[str, dict] = {}


def table(path: Path = ROUTING_PATH) -> dict:
    key = str(path)
    if key not in _cache:
        _cache[key] = json.loads(path.read_text(encoding="utf-8"))
    return _cache[key]


def _cond(value: Any, cond: Any) -> bool:
    if isinstance(cond, dict):
        for op, arg in cond.items():
            if op == "exists":
                if (value is not None) != bool(arg):
                    return False
                continue
            if op == "lacks":
                if isinstance(value, (list, tuple, set)) and arg in value:
                    return False
                continue
            if value is None:
                return False
            if op == "in" and value not in arg:
                return False
            if op == "nin" and value in arg:
                return False
            if op == "has" and not (isinstance(value, (list, tuple, set)) and arg in value):
                return False
            if op in ("lt", "lte", "gt", "gte"):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return False
                if (op == "lt" and not value < arg) or (op == "lte" and not value <= arg) or \
                   (op == "gt" and not value > arg) or (op == "gte" and not value >= arg):
                    return False
        return True
    if value is None:
        return False
    if isinstance(cond, list):
        return value in cond
    return value == cond


def matches(ctx: dict, when: dict) -> bool:
    return all(_cond(ctx.get(k), c) for k, c in when.items())


def route(ctx: dict, data: dict | None = None) -> dict:
    """First matching rule → {offer, rule, variant?, alt?, prefer_email?, bump?}. Disabled offers fall through."""
    data = data or table()
    ctx = {**ctx}
    if ctx.get("keyword") and not ctx.get("pillar"):
        ctx["pillar"] = data["keyword_pillar"].get(str(ctx["keyword"]).upper(), "general")
    if ctx.get("goal") and ctx.get("goal") != "start":
        ctx["pillar"] = ctx["goal"]
    for r in data["rules"]:
        if not matches(ctx, r["when"]):
            continue
        if not data["offers"].get(r["offer"], {}).get("enabled", False):
            continue
        out = {"offer": r["offer"], "rule": r["id"]}
        for k in ("variant", "alt", "prefer_email"):
            if k in r:
                out[k] = r[k]
        b = bump_for(ctx.get("pillar"), data)
        if out["offer"] == "front_end" and b:
            out["bump"] = b
        return out
    return {"offer": "front_end", "rule": "fallback"}


def bump_for(pillar: str | None, data: dict | None = None) -> dict | None:
    data = data or table()
    b = data["bumps"]["by_pillar"].get(pillar or "general") or data["bumps"]["by_pillar"]["general"]
    return {"sku": b["sku"], "frame": b["frame"], "second": b.get("second")} if b.get("sku") else None


def thank_you_offer(cell: str, pillar: str | None, data: dict | None = None) -> str:
    data = data or table()
    t = data["thank_you"].get(cell) or data["thank_you"]["e12"]
    return t.get(pillar or "", t["default"])


def winback(lapse_days: int, data: dict | None = None) -> dict:
    data = data or table()
    for t in data["winback"]["tiers"]:
        if lapse_days <= t["max_days"]:
            return t
    return data["winback"]["tiers"][-1]


def fnv1a(s: str) -> int:
    """Same hash as app/src/lib/blitz.ts fnv1a (UTF-16 code units; ASCII ids only here)."""
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h


def fmix32(h: int) -> int:
    """murmur3 finalizer. Plain fnv1a % 2 is the parity of the odd characters in the input, so two 2-arm experiments
    hashed that way put every person in the SAME arm of both (confounded). Mixing fixes it."""
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def assign(experiment_id: str, subject: str, data: dict | None = None) -> str | None:
    """Sticky arm for (experiment, subject). Same formula as app/src/lib/offers/experiments.ts. fe_cell mirrors the
    live cell assignment (plain fnv1a, app/src/lib/billing/shopify.ts) so the readout labels match what was sold."""
    data = data or table()
    exp = next((e for e in data["experiments"] if e["id"] == experiment_id), None)
    if not exp or not subject:
        return None
    h = fnv1a(f"{exp['salt']}:{subject}")
    if exp.get("hash") != "fnv1a":
        h = fmix32(h)
    return exp["arms"][h % len(exp["arms"])]


def context_from_contact(c: dict, ev: dict | None = None, *, mode: str = "launch", hour: int | None = None) -> dict:
    """The DM bot's view of a person: answers to the 2 qualify questions, first keyword, tags written by webhooks."""
    tags = set(c.get("tags") or [])
    ans = c.get("answers") or {}
    prior = [p for p, t in (("books", "book_buyer"), ("member", "member"), ("annual", "annual"), ("gift_buyer", "gift_buyer"),
                            ("coached", "coached")) if t in tags]
    ctx = {
        "mode": mode,
        "surface": "dm",
        "keyword": (c.get("first_kw") or "").upper() or None,
        "platform": (ev or {}).get("platform") or (c.get("key", ":").split(":", 1)[0] or None),
        "goal": ans.get("goal"),
        "audience": ans.get("audience") or ("parent" if "tagger" in tags else None),
        "tagger": "tagger" in tags,
        "follower": c.get("follower"),
        "hardship": "hardship" in tags,
        "prior": prior,
        "hour": hour,
    }
    return {k: v for k, v in ctx.items() if v is not None}
