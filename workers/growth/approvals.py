"""Human approval records for boosts, written by the members app when a person approves a boost in
/admin/exceptions (POST /growth/approvals/boost). Append-only JSONL; the latest record per boost wins.

The governor plan endpoint attaches a recorded approval to a state boost that has none (matched by boost_id, else
post_id), so the approval a person gave in the admin is the one the governor checks (I3: WINNER + compliance pass +
judge + named human). Recording an approval spends nothing: spend still needs SPEND_ENABLED=1, GROWTH_DRY_RUN=0,
a plan-bound approval for execute, and there is no ad API client in this codebase.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from common import config as C
from growth import snapshots as S


def path() -> Path:
    p = os.environ.get("GROWTH_APPROVALS_PATH", "")
    return Path(p) if p else C.OUTPUT_DIR / "growth" / "boost_approvals.jsonl"


def validate(boost_id: str, approval: dict) -> list[str]:
    errs = []
    if not isinstance(boost_id, str) or not boost_id or len(boost_id) > 80 or not all(ch.isalnum() or ch in "-_" for ch in boost_id):
        errs.append("boost_id invalid")
    by = str((approval or {}).get("by") or "").strip()
    if not by:
        errs.append("approval.by required (a named human)")
    at = S.parse_dt((approval or {}).get("at"))
    if at is None:
        errs.append("approval.at invalid")
    elif at > datetime.now(timezone.utc):
        errs.append("approval.at in the future")
    try:
        mx = float((approval or {}).get("max_daily_usd"))
        if not (0 <= mx <= 100000):
            errs.append("approval.max_daily_usd out of range")
    except (TypeError, ValueError):
        errs.append("approval.max_daily_usd invalid")
    return errs


def record(boost_id: str, approval: dict, *, exception_id: str | None = None) -> dict:
    errs = validate(boost_id, approval)
    if errs:
        return {"ok": False, "errors": errs}
    row = {"boost_id": boost_id, "approval": {"by": str(approval["by"]).strip(), "at": str(approval["at"]),
                                              "max_daily_usd": float(approval["max_daily_usd"])},
           "exception_id": exception_id, "recorded_at": datetime.now(timezone.utc).isoformat()}
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    return {"ok": True, "record": row}


def load() -> dict[str, dict]:
    p = path()
    out: dict[str, dict] = {}
    if not p.is_file():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            out[row["boost_id"]] = row["approval"]
        except (ValueError, KeyError, TypeError):
            continue
    return out


def attach(state: dict) -> dict:
    """A copy of state whose approval-less boosts carry the recorded human approval, if one exists."""
    recorded = load()
    if not recorded or not isinstance(state, dict) or not isinstance(state.get("boosts"), list):
        return state
    boosts = []
    for b in state["boosts"]:
        if isinstance(b, dict) and not b.get("approval"):
            key = b.get("boost_id") or b.get("post_id")
            if key in recorded:
                b = {**b, "approval": recorded[key]}
        boosts.append(b)
    return {**state, "boosts": boosts}


def pending(state: dict) -> list[dict]:
    """Boosts that qualify for a person's decision: WINNER, compliance pass, judge passed, no approval yet."""
    out = []
    for b in (state or {}).get("boosts") or []:
        if isinstance(b, dict) and not b.get("approval") and b.get("class") == "WINNER" \
                and b.get("compliance_verdict") == "pass" and b.get("judge_passed") is True:
            out.append(b)
    return out
