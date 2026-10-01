"""Spend governor: a pure, deterministic function from (state, config) to an action plan, plus an append-only,
hash-chained audit log. It NEVER calls an ad API. The executor stub below refuses unless SPEND_ENABLED=1,
GROWTH_DRY_RUN=0 and a human approval record exist, and even then it only reports that no ad client is wired.

decide(state, cfg, *, spend_enabled, dry_run, now) -> decision

Spend classes: boost (a WINNER post amplified as a Meta partnership ad / TikTok Spark), retarget (engaged viewers),
cold (prospecting). Order of allocation under the caps: boosts, then retargeting, then cold.

Hard invariants (property-tested in tests/test_growth_governor.py):
  I1  planned_total <= daily_cap - spent_today, <= monthly_cap - spent_month, <= balance - cash_floor   (all >= 0)
  I2  every boost <= min(requested, approval.max_daily_usd, governor.max_boost_daily_usd)
  I3  a boost is approved only with class WINNER, compliance verdict pass, judge_passed and a human approval record
  I4  cold > 0 only when the §11 graduation gate passes (or the client-set pre-gate line applies) AND status is not STOP
  I5  cold never rises by more than scale_step per decision and only under SCALE; falls by cut_step under CUT
  I6  without an approved, unexpired budget record, or with any invalid input (NaN, inf, negative, absurd), the plan
      is all zeros with status STOP and valid=false
  I7  the decision is identical for identical inputs (no clock reads inside decide; `now` is an argument)
  I8  SPEND_ENABLED=0 or dry_run -> mode "dry_run": the plan is advisory and execute() refuses

BLITZ.md §9 rules (price-aware, days 1-7 learning lines) and §11 graduation thresholds are read from config
["governor"]; nothing is hard-coded here.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from common import config as C
from growth import config as G
from growth import snapshots as S

STATUS_RANK = {"SCALE": 0, "HOLD": 1, "CUT": 2, "STOP": 3}


class GovernorRefused(RuntimeError):
    """The executor stub refused to run (expected in every environment until the client wires an ad client)."""


def _worst(*statuses: str) -> str:
    return max(statuses, key=lambda s: STATUS_RANK[s])


def _money(x, cfg, *, allow_zero=True) -> float | None:
    v = G.num(x, lo=0 if allow_zero else 1e-9, hi=float(cfg["governor"]["max_abs_usd"]))
    return v


def _rate(x) -> float | None:
    return G.num(x, lo=0, hi=1)


def _round(x: float) -> float:
    return float(math.floor(x * 100 + 1e-9) / 100.0)     # never round UP money


def _dict(x, errs: list[str], name: str) -> dict:
    if x is None:
        return {}
    if not isinstance(x, dict):
        errs.append(f"{name} must be an object")
        return {}
    return dict(x)


def _list(x, errs: list[str], name: str) -> list:
    if x is None:
        return []
    if not isinstance(x, list):
        errs.append(f"{name} must be a list")
        return []
    return list(x)


def validate_state(state: dict, cfg: dict, now: datetime) -> tuple[dict, list[str]]:
    """Coerce every number through growth.config.num; anything absurd (wrong type, NaN, inf, negative, beyond the
    sanity bound) is a reason to STOP. Never raises on junk input."""
    errs: list[str] = []
    st = _dict(state, errs, "state")
    budget = _dict(st.get("budget"), errs, "budget")
    cash = _dict(st.get("cash"), errs, "cash")
    cur = _dict(st.get("current"), errs, "current")
    out = {"price_key": G.price_key(st.get("price_usd"), cfg["governor"]["lines"]),
           "campaign_day": G.num(st.get("campaign_day"), lo=0, hi=10000)}
    if out["price_key"] is None:
        errs.append("price_usd has no governor lines (25 or 30 expected)")
    if out["campaign_day"] is None:
        errs.append("campaign_day invalid")
    for k in ("daily_cap_usd", "monthly_cap_usd", "cash_floor_usd"):
        v = _money(budget.get(k), cfg)
        if v is None:
            errs.append(f"budget.{k} invalid")
        out[k] = v
    if budget.get("status", "approved") != "approved" or not str(budget.get("approved_by") or "").strip():
        errs.append("budget record is not approved by a named human")
    exp = S.parse_dt(budget.get("expires_at"))
    if budget.get("expires_at") and exp is None:
        errs.append("budget.expires_at unparsable")
    if exp is not None and exp <= now:
        errs.append("budget record expired")
    if S.parse_dt(budget.get("approved_at")) is None:
        errs.append("budget.approved_at missing")
    out["budget_id"] = budget.get("id")
    for k in ("balance_usd", "spent_today_usd", "spent_month_usd"):
        v = _money(cash.get(k), cfg)
        if v is None:
            errs.append(f"cash.{k} invalid")
        out[k] = v
    line = cash.get("line_180d_usd")
    out["line_180d_usd"] = _money(line, cfg) if line is not None else None
    if line is not None and out["line_180d_usd"] is None:
        errs.append("cash.line_180d_usd invalid")
    out["cold_daily_usd"] = _money(cur.get("cold_daily_usd", 0), cfg)
    out["retarget_daily_usd"] = _money(cur.get("retarget_daily_usd", 0), cfg)
    out["retarget_requested_usd"] = _money(cur.get("retarget_requested_usd", cur.get("retarget_daily_usd", 0)), cfg)
    for k in ("cold_daily_usd", "retarget_daily_usd", "retarget_requested_usd"):
        if out[k] is None:
            errs.append(f"current.{k} invalid")
    daily = []
    for i, d in enumerate(_list(st.get("daily"), errs, "daily")):
        d = _dict(d, errs, f"daily[{i}]")
        m = _money(d.get("paid_media_usd"), cfg)
        n = G.num(d.get("paid_net_new_members"), lo=0, hi=1e7)
        if m is None or n is None:
            errs.append(f"daily[{i}] invalid")
            continue
        daily.append({"day": (d or {}).get("day"), "paid_media_usd": m, "members": n})
    out["daily"] = daily
    for k in ("refund_rate_14d", "chargeback_rate_30d"):
        v = st.get(k)
        out[k] = None if v is None else _rate(v)
        if v is not None and out[k] is None:
            errs.append(f"{k} invalid (must be 0..1)")
    cc = st.get("chargeback_count_30d")
    out["chargeback_count_30d"] = None if cc is None else G.num(cc, lo=0, hi=1e7)
    if cc is not None and out["chargeback_count_30d"] is None:
        errs.append("chargeback_count_30d invalid")
    r1 = _dict(st.get("renewal1"), errs, "renewal1")
    out["renewal1_rate"] = None if r1.get("rate") is None else _rate(r1.get("rate"))
    out["renewal1_n"] = G.num(r1.get("cohort_n", 0), lo=0, hi=1e8)
    if r1.get("rate") is not None and out["renewal1_rate"] is None:
        errs.append("renewal1.rate invalid")
    gr = _dict(st.get("graduation"), errs, "graduation")
    out["grad_purchases"] = G.num(gr.get("charge_today_purchases", 0), lo=0, hi=1e8)
    out["grad_factor"] = None if gr.get("factor") is None else G.num(gr.get("factor"), lo=0, hi=10)
    out["grad_case"] = "upside" if gr.get("media_cost_case") == "upside" else "central"
    out["grad_days_over_4k"] = G.num(gr.get("days_at_min_spend", 0), lo=0, hi=1000)
    if gr.get("factor") is not None and out["grad_factor"] is None:
        errs.append("graduation.factor invalid")
    boosts = []
    for i, b in enumerate(_list(st.get("boosts"), errs, "boosts")):
        b = _dict(b, errs, f"boosts[{i}]")
        req = _money(b.get("requested_daily_usd"), cfg)
        appr = _dict(b.get("approval"), errs, f"boosts[{i}].approval")
        amax = _money(appr.get("max_daily_usd"), cfg) if appr else None
        boosts.append({"post_id": b.get("post_id"), "class": b.get("class"), "compliance_verdict": b.get("compliance_verdict"),
                       "judge_passed": bool(b.get("judge_passed")), "requested": req,
                       "approval": {"by": str(appr.get("by") or "").strip(), "at": S.parse_dt(appr.get("at")), "max": amax}
                       if appr else None, "invalid": req is None or (appr and amax is None)})
    out["boosts"] = boosts
    return out, errs


def rules_status(v: dict, cfg: dict) -> tuple[str, dict]:
    """BLITZ §9 rule table -> per-rule status and the worst of them."""
    g = cfg["governor"]
    ln = g["lines"][v["price_key"]]
    learning = v["campaign_day"] <= float(g["learning_days"])
    scale_line = ln["learning_scale"] if learning else ln["scale"]
    hold_max = ln["learning_hold_max"] if learning else ln["hold_max"]
    rules: dict[str, dict] = {}
    # paid media per paid net new member (latest day), plus consecutive-days-over-CUT count
    cac = None
    over = 0
    for d in reversed(v["daily"]):
        c = (d["paid_media_usd"] / d["members"]) if d["members"] > 0 else (math.inf if d["paid_media_usd"] > 0 else None)
        if cac is None:
            cac = c
        if c is not None and c > hold_max:
            over += 1
        else:
            break
    if cac is None:
        rules["cac"] = {"status": "HOLD", "value": None, "why": "no paid-media / member data yet: no scaling"}
    elif cac <= scale_line:
        rules["cac"] = {"status": "SCALE", "value": cac, "line": scale_line}
    elif cac <= hold_max:
        rules["cac"] = {"status": "HOLD", "value": cac, "line": hold_max}
    else:
        cut = over >= int(g["cut_consecutive_days"])
        rules["cac"] = {"status": "CUT" if cut else "HOLD", "value": None if cac == math.inf else cac, "line": hold_max,
                        "days_over": over, "why": f"> {hold_max} {'two days running' if cut else 'today; cut if it repeats'}"}
    # refunds
    rf = g["refunds_14d"]
    if v["refund_rate_14d"] is None:
        rules["refunds"] = {"status": "SCALE", "value": None, "why": "not yet measurable"}
    elif v["refund_rate_14d"] > float(rf["hold_max"]):
        rules["refunds"] = {"status": "HOLD", "value": v["refund_rate_14d"], "why": "> 12%: stop scaling"}
    elif v["refund_rate_14d"] > float(rf["scale_max"]):
        rules["refunds"] = {"status": "HOLD", "value": v["refund_rate_14d"]}
    else:
        rules["refunds"] = {"status": "SCALE", "value": v["refund_rate_14d"]}
    # chargebacks
    cb = g["chargebacks_30d"]
    rate, cnt = v["chargeback_rate_30d"], v["chargeback_count_30d"]
    if rate is None and cnt is None:
        rules["chargebacks"] = {"status": "SCALE", "value": None, "why": "not yet measurable"}
    elif (rate or 0) >= float(cb["stop_rate"]) or (cnt or 0) >= float(cb["stop_count"]):
        rules["chargebacks"] = {"status": "STOP", "rate": rate, "count": cnt, "why": ">= 0.5% or >= 75: stop"}
    elif (rate or 0) >= float(cb["ok_rate"]) or (cnt or 0) >= float(cb["ok_count"]):
        rules["chargebacks"] = {"status": "HOLD", "rate": rate, "count": cnt}
    else:
        rules["chargebacks"] = {"status": "SCALE", "rate": rate, "count": cnt}
    # renewal 1 (days 25+, once the cohort is big enough)
    r1 = g["renewal1"]
    if v["campaign_day"] >= float(r1["window_start_day"]) and v["renewal1_n"] >= float(r1["min_cohort"]):
        if v["renewal1_rate"] is None:
            rules["renewal1"] = {"status": "HOLD", "value": None, "why": "renewal-1 not reported in window: hold"}
        elif v["renewal1_rate"] < float(r1["hold_min"]):
            rules["renewal1"] = {"status": "HOLD", "value": v["renewal1_rate"], "why": "< 50%: hold spend"}
        elif v["renewal1_rate"] < float(r1["scale_min"]):
            rules["renewal1"] = {"status": "HOLD", "value": v["renewal1_rate"]}
        else:
            rules["renewal1"] = {"status": "SCALE", "value": v["renewal1_rate"]}
    else:
        rules["renewal1"] = {"status": "SCALE", "value": v["renewal1_rate"], "why": "outside the day-25+ window or cohort too small"}
    # cash headroom to the 180-day line
    ch = g["cash_headroom"]
    if v["line_180d_usd"] and v["line_180d_usd"] > 0:
        head = (v["balance_usd"] - v["cash_floor_usd"]) / v["line_180d_usd"]
        if head < float(ch["hold_min"]):
            rules["cash"] = {"status": "CUT", "value": head, "why": "< 10% headroom: cut to the CUT-line equilibrium"}
        elif head < float(ch["ok_min"]):
            rules["cash"] = {"status": "HOLD", "value": head}
        else:
            rules["cash"] = {"status": "SCALE", "value": head}
    else:
        rules["cash"] = {"status": "HOLD", "value": None, "why": "no 180-day cash line supplied: no scaling"}
    worst = _worst(*(r["status"] for r in rules.values()))
    return worst, {"learning_window": learning, "scale_line": scale_line, "hold_max": hold_max, "rules": rules}


def graduation(v: dict, cfg: dict) -> dict:
    """BLITZ §11: all of 1, 2 (or 2b), 4 on >= 300 charge-today purchases; 3 only from day 40."""
    gg = cfg["governor"]["graduation"]
    pk = v["price_key"]
    checks: dict[str, dict] = {}
    days = [d for d in v["daily"] if d["paid_media_usd"] >= float(gg["min_daily_spend_usd"])][-int(gg["days_running"]):]
    if len(days) >= int(gg["days_running"]) and sum(d["members"] for d in days) > 0:
        blended = sum(d["paid_media_usd"] for d in days) / sum(d["members"] for d in days)
        checks["1_blended_cac"] = {"pass": blended <= float(gg["cac_line"][pk]), "value": blended, "line": gg["cac_line"][pk]}
    else:
        checks["1_blended_cac"] = {"pass": False, "value": None, "why": f"needs {gg['days_running']} days at >= ${gg['min_daily_spend_usd']}/day"}
    need = float(gg["factor_upside" if v["grad_case"] == "upside" else "factor_central"][pk])
    checks["2_factor"] = {"pass": v["grad_factor"] is not None and v["grad_factor"] >= need, "value": v["grad_factor"],
                          "line": need, "case": v["grad_case"]}
    checks["purchases"] = {"pass": v["grad_purchases"] >= float(gg["min_purchases"]), "value": v["grad_purchases"],
                           "line": gg["min_purchases"]}
    checks["4_refunds_chargebacks"] = {"pass": (v["refund_rate_14d"] or 0) <= float(gg["refund_max"]) and
                                       (v["chargeback_rate_30d"] or 0) < float(gg["chargeback_rate_max"])}
    if v["campaign_day"] >= float(gg["renewal1_gate_day"]):
        checks["3_renewal1"] = {"pass": v["renewal1_rate"] is not None and v["renewal1_rate"] >= float(gg["renewal1_min"]),
                                "value": v["renewal1_rate"], "line": gg["renewal1_min"]}
    else:
        checks["3_renewal1"] = {"pass": True, "why": "not due before day 40"}
    return {"passed": all(c["pass"] for c in checks.values()), "checks": checks}


def _zero_plan(reasons: list[str], *, mode: str, spend_enabled: bool, now: datetime, cfg: dict, state_hash: str,
               valid: bool = False, status: str = "STOP", extra: dict | None = None) -> dict:
    d = {"mode": mode, "spend_enabled": spend_enabled, "valid": valid, "status": status, "reasons": reasons,
         "cold": {"allowed": False, "current_daily_usd": 0.0, "next_daily_usd": 0.0},
         "retarget": {"next_daily_usd": 0.0}, "boosts": [],
         "totals": {"planned_daily_usd": 0.0, "remaining_daily_cap": 0.0, "remaining_monthly_cap": 0.0, "cash_headroom_usd": 0.0},
         "decided_at": now.isoformat(), "config_version": cfg.get("version"), "config_fingerprint": G.fingerprint(cfg),
         "state_hash": state_hash}
    d.update(extra or {})
    return d


def decide(state: dict, cfg: dict | None = None, *, spend_enabled: bool | None = None, dry_run: bool | None = None,
           now: datetime | None = None) -> dict:
    cfg = cfg or G.load()
    g = cfg["governor"]
    spend_enabled = G.SPEND_ENABLED if spend_enabled is None else bool(spend_enabled)
    dry_run = G.GROWTH_DRY_RUN if dry_run is None else bool(dry_run)
    now = now or datetime.now(timezone.utc)
    mode = "live" if (spend_enabled and not dry_run) else "dry_run"
    state_hash = hashlib.sha256(json.dumps(state, sort_keys=True, default=str).encode()).hexdigest()[:16]
    v, errs = validate_state(state, cfg, now)
    if errs:
        return _zero_plan(["invalid input: " + "; ".join(errs)], mode=mode, spend_enabled=spend_enabled, now=now, cfg=cfg,
                          state_hash=state_hash)
    status, rule_detail = rules_status(v, cfg)
    grad = graduation(v, cfg)
    reasons = [f"{k}: {r['status']}" + (f" ({r['why']})" if r.get("why") else "") for k, r in rule_detail["rules"].items()]
    remaining_daily = max(0.0, v["daily_cap_usd"] - v["spent_today_usd"])
    remaining_month = max(0.0, v["monthly_cap_usd"] - v["spent_month_usd"])
    cash_head = max(0.0, v["balance_usd"] - v["cash_floor_usd"])
    envelope = min(remaining_daily, remaining_month, cash_head)
    if status == "STOP":
        return _zero_plan(reasons + ["STOP rule tripped: all spend classes 0"], mode=mode, spend_enabled=spend_enabled,
                          now=now, cfg=cfg, state_hash=state_hash, valid=True, status="STOP",
                          extra={"gates": {"rules": rule_detail, "graduation": grad},
                                 "totals": {"planned_daily_usd": 0.0, "remaining_daily_cap": _round(remaining_daily),
                                            "remaining_monthly_cap": _round(remaining_month), "cash_headroom_usd": _round(cash_head)}})
    # ---- boosts first: proven winners, compliance PASS + judge, human approval, per-boost cap
    boost_cap = float(g["max_boost_daily_usd"])
    boosts_out, planned = [], 0.0
    for b in v["boosts"]:
        why = []
        if b["invalid"]:
            why.append("invalid amount")
        if b["class"] != g["boost_requires_class"]:
            why.append(f"class {b['class']} is not {g['boost_requires_class']}")
        if b["compliance_verdict"] != "pass":
            why.append(f"compliance verdict {b['compliance_verdict']!r} is not pass")
        if not b["judge_passed"]:
            why.append("LLM judge did not pass")
        if not b["approval"] or not b["approval"]["by"] or b["approval"]["at"] is None or b["approval"]["max"] is None:
            why.append("no human approval record (by, at, max_daily_usd)")
        elif b["approval"]["at"] > now:
            why.append("approval dated in the future")
        if why:
            boosts_out.append({"post_id": b["post_id"], "status": "rejected", "approved_daily_usd": 0.0, "reasons": why})
            continue
        amt = min(b["requested"], b["approval"]["max"], boost_cap, max(0.0, envelope - planned))
        amt = _round(amt)
        if amt <= 0:
            boosts_out.append({"post_id": b["post_id"], "status": "rejected", "approved_daily_usd": 0.0,
                               "reasons": ["no budget envelope left"]})
            continue
        planned += amt
        boosts_out.append({"post_id": b["post_id"], "status": "approved", "approved_daily_usd": amt,
                           "reasons": [f"min(requested {b['requested']}, approval {b['approval']['max']}, cap {boost_cap}, envelope)"]})
    # ---- retargeting (engaged viewers): allowed under SCALE/HOLD/CUT within the envelope, never above its request
    retarget = 0.0
    if v["retarget_requested_usd"] > 0:
        retarget = _round(min(v["retarget_requested_usd"], float(g["max_retarget_daily_usd"]), max(0.0, envelope - planned)))
        if status == "CUT":
            retarget = _round(min(retarget, v["retarget_daily_usd"] * (1 - float(g["cut_step"]))))
        planned += retarget
    # ---- cold prospecting: only after graduation (or the client-set pre-gate flat line), stepped by status
    cold_now = v["cold_daily_usd"]
    pre_gate = float(g.get("pre_gate_cold_daily_usd", 0) or 0)
    cold_allowed = grad["passed"] or pre_gate > 0
    cold_why = []
    if grad["passed"]:
        if status == "SCALE":
            nxt = cold_now * (1 + float(g["scale_step"])) if cold_now > 0 else float(g["initial_daily_usd"])
            cold_why.append(f"SCALE: +{int(g['scale_step'] * 100)}%/day toward plan")
        elif status == "HOLD":
            nxt = cold_now
            cold_why.append("HOLD: flat")
        else:
            nxt = cold_now * (1 - float(g["cut_step"]))
            cold_why.append(f"CUT: -{int(g['cut_step'] * 100)}%")
        nxt = min(nxt, float(g["max_cold_daily_usd"]))
    elif pre_gate > 0:
        nxt = pre_gate if status in ("SCALE", "HOLD") else min(pre_gate, cold_now * (1 - float(g["cut_step"])))
        cold_why.append(f"pre-gate flat line ${pre_gate:g}/day (client decision governor.pre_gate_cold_daily_usd), "
                        "graduation not yet passed")
    else:
        nxt = 0.0
        cold_why.append("graduation gate (§11) not passed: no cold budget")
    cold_next = _round(min(nxt, max(0.0, envelope - planned)))
    planned += cold_next
    if cold_next < nxt - 0.01:
        cold_why.append("clipped by the budget envelope")
    return {"mode": mode, "spend_enabled": spend_enabled, "valid": True, "status": status,
            "reasons": reasons + (["graduation passed"] if grad["passed"] else ["graduation not passed"]),
            "cold": {"allowed": cold_allowed and cold_next > 0, "current_daily_usd": _round(cold_now), "next_daily_usd": cold_next,
                     "why": cold_why},
            "retarget": {"next_daily_usd": retarget}, "boosts": boosts_out,
            "totals": {"planned_daily_usd": _round(planned), "remaining_daily_cap": _round(remaining_daily),
                       "remaining_monthly_cap": _round(remaining_month), "cash_headroom_usd": _round(cash_head),
                       "envelope": _round(envelope)},
            "gates": {"rules": rule_detail, "graduation": grad}, "budget_id": v["budget_id"],
            "decided_at": now.isoformat(), "config_version": cfg.get("version"), "config_fingerprint": G.fingerprint(cfg),
            "state_hash": state_hash}


# ---------------------------------------------------------------- audit log (append-only, hash-chained)
def audit_path() -> Path:
    return Path(G.GROWTH_AUDIT_PATH) if G.GROWTH_AUDIT_PATH else C.OUTPUT_DIR / "growth" / "governor_audit.jsonl"


def _last_hash(path: Path) -> str:
    if not path.is_file():
        return "0" * 64
    last = ""
    with path.open("rb") as f:
        for line in f:
            if line.strip():
                last = line
    if not last:
        return "0" * 64
    try:
        return json.loads(last)["hash"]
    except (ValueError, KeyError):
        return "0" * 64


def append_audit(decision: dict, *, actor: str = "governor", path: Path | None = None) -> dict:
    path = path or audit_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    prev = _last_hash(path)
    body = {"prev_hash": prev, "actor": actor, "decision": decision}
    h = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    entry = {**body, "hash": h}
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True, default=str) + "\n")
    return {"hash": h, "prev_hash": prev, "path": str(path)}


def verify_audit(path: Path | None = None) -> dict:
    path = path or audit_path()
    if not path.is_file():
        return {"ok": True, "entries": 0}
    prev, n = "0" * 64, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        body = {k: e[k] for k in ("prev_hash", "actor", "decision")}
        h = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
        if e.get("prev_hash") != prev or e.get("hash") != h:
            return {"ok": False, "entries": n, "broken_at": n}
        prev, n = h, n + 1
    return {"ok": True, "entries": n}


# ---------------------------------------------------------------- executor stub: never calls an ad API
def execute(decision: dict, approval: dict | None = None, *, spend_enabled: bool | None = None,
            dry_run: bool | None = None) -> dict:
    spend_enabled = G.SPEND_ENABLED if spend_enabled is None else bool(spend_enabled)
    dry_run = G.GROWTH_DRY_RUN if dry_run is None else bool(dry_run)
    if not spend_enabled:
        raise GovernorRefused("SPEND_ENABLED is not 1: the executor refuses")
    if dry_run:
        raise GovernorRefused("GROWTH_DRY_RUN is not 0: the executor refuses")
    if not decision or decision.get("mode") != "live" or not decision.get("valid"):
        raise GovernorRefused("decision is not a valid live plan")
    if not approval or not str(approval.get("by") or "").strip() or approval.get("decision_hash") != decision.get("state_hash"):
        raise GovernorRefused("no human approval bound to this exact decision (approval.decision_hash must equal state_hash)")
    # The plan must have been made under the operator's config (file/defaults), not a per-request what-if.
    if decision.get("config_fingerprint") != G.fingerprint(G.load()):
        raise GovernorRefused("decision was planned under a different config than the operator's (config_fingerprint mismatch)")
    # Deliberately unimplemented: no Meta / TikTok ads client exists in this codebase, and none is called here.
    return {"executed": False, "reason": "no ad API client is wired; plan recorded only", "planned": decision["totals"]}
