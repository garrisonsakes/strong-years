"""QA scoring + routing (prompts/07 deterministic bands; PIPELINE §1.1/§4.6/§5.4 routing).

Mirrors the n8n Code node 'Decide QA Route' exactly, plus three worker-side checks it now also reads:
ai_tag_present (SAFETY D-02), duration_ok, and the uniqueness guard.
Routes: auto (auto_publish) | approval | regen (re-render, max 3 attempts) | human.
"""
from __future__ import annotations

RANK = {"pass": 0, "review": 1, "fail": 2}
ROUTE_LABEL = {"auto": "auto_publish", "approval": "approval", "regen": "re_render", "human": "human"}
MAX_ATTEMPTS = 3

# (metric, pass predicate, review predicate) — anything else fails
BANDS = [
    ("face_sim_median", lambda x: x >= 0.55, lambda x: x >= 0.45),
    ("face_sim_min", lambda x: x >= 0.40, lambda x: x >= 0.32),
    ("syncnet_conf", lambda x: x >= 6.0, lambda x: x >= 4.5),
    ("syncnet_dist", lambda x: x <= 8.0, lambda x: x <= 9.0),
    ("lufs_integrated", lambda x: abs(x + 14) <= 1, lambda x: abs(x + 14) <= 2),
    ("true_peak_db", lambda x: x <= -1.0, lambda x: x <= -0.3),
]


def deterministic(m: dict) -> tuple[str, list[str]]:
    det, reasons = "pass", []

    def band(name, val, ok, rev):
        nonlocal det
        if val is None:
            return
        if ok(val):
            return
        if rev(val):
            det = "review" if det == "pass" else det
            reasons.append(f"{name}={val} (review)")
        else:
            det = "fail"
            reasons.append(f"{name}={val} (fail)")

    for name, ok, rev in BANDS:
        band(name, m.get(name), ok, rev)
    num_bad = bool(m.get("caption_number_mismatch"))
    band("caption_cer", m.get("caption_cer"), lambda x: x <= 0.01 and not num_bad, lambda x: x <= 0.03 and not num_bad)
    if m.get("caption_cer") is None and num_bad:
        det = "fail"
        reasons.append("caption number mismatch (fail)")
    bf = max(m.get("black_max_s") or 0, m.get("freeze_max_s") or 0)
    band("black_freeze_s", bf, lambda x: x <= 0.25, lambda x: x <= 0.6)
    if m.get("spec_ok") is False:
        det = "fail"
        reasons.append("spec (res/fps/codec): " + "; ".join(m.get("spec_problems") or []))
    if m.get("ai_tag_present") is False:
        det = "fail"
        reasons.append("D-02 AI corner tag not found (fail)")
    if m.get("duration_ok") is False:
        det = "fail"
        reasons.append(f"duration {m.get('duration_s')}s outside {m.get('duration_bounds')} (fail)")
    if m.get("c2pa_present") is False:       # AUDIT M10: unsigned masters never auto-publish
        det = "review" if det == "pass" else det
        reasons.append("c2pa missing (re-sign) (review)")
    if m.get("c2pa_trusted") is False:
        reasons.append("c2pa signed with an untrusted (dev) certificate: no auto-publish")
    return det, reasons


def combine(det: str, vision: str | None) -> str:
    return max([det, vision or "review"], key=lambda d: RANK.get(d, 1)) if vision is not None else det


def route(decision: str, *, trusted: bool = False, risk_tier: str = "green", attempts: int = 1,
          uniqueness_allow: bool = True, c2pa_trusted: bool | None = None, judge_passed: bool | None = None,
          require_judge: bool = False) -> str:
    if not uniqueness_allow:
        return "human"          # a duplicate isn't fixed by re-rendering the same script
    if decision == "fail":
        return "regen" if attempts < MAX_ATTEMPTS else "human"
    if require_judge and judge_passed is not True:
        return "human"          # mandatory LLM judge: no auto-publish or approval without a passing judge result
    if decision == "pass" and trusted and risk_tier == "green" and c2pa_trusted is not False:
        return "auto"
    return "approval"


def score(metrics: dict, *, vision_decision: str | None = None, trusted: bool = False, risk_tier: str = "green",
          attempts: int = 1, uniqueness_allow: bool = True, judge_passed: bool | None = None,
          require_judge: bool = False) -> dict:
    det, reasons = deterministic(metrics)
    decision = combine(det, vision_decision)
    r = route(decision, trusted=trusted, risk_tier=risk_tier, attempts=attempts, uniqueness_allow=uniqueness_allow,
              c2pa_trusted=metrics.get("c2pa_trusted"), judge_passed=judge_passed, require_judge=require_judge)
    if require_judge and judge_passed is not True:
        reasons.append("mandatory LLM judge result missing or not passing")
    if not uniqueness_allow:
        reasons.append("uniqueness guard denied")
    return {"deterministic": det, "decision": decision, "reasons": reasons, "route": r, "route_label": ROUTE_LABEL[r]}
