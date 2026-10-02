"""Block-level learning: attribute scorecard rows to hook / body / close blocks and their families ("genes"),
rank genes, and write the weekly plain-English readout for the exceptions digest.

  attribute(cards)        block id -> {kind, family, n, mean component score, mean composite}
                          hook blocks are credited with the hook score, body blocks with the body score, close blocks
                          with the close score; every block also carries the composite of the posts it ran in
  gene_table(cards)       gene ("hook:IF_EVERY", "body:P01:F02", "close:STRONG") -> n and composite shrunk toward 50
                          with k pseudo-posts (a gene seen twice can't top the table)
  weekly_readout(...)     top 5 genes, 5 benched, gate changes (tools/refit_gate.py report), next week's tests
  post_readout(text)      best effort to /admin/exceptions (type growth_readout), which feeds the 07:00 digest
Uses only the final read per post (24 h, else the latest non-provisional one). Pure apart from post_readout().
"""
from __future__ import annotations

from datetime import datetime, timezone

KINDS = ("hook", "body", "close")


def final_reads(cards: list[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for c in cards:
        if c.get("provisional") or c.get("composite") is None:
            continue
        k, h = str(c.get("post_id")), int(c.get("horizon_h") or 0)
        cur = best.get(k)
        # 24 h is the decision read; otherwise the latest horizon available
        rank = (h == 24, h)
        if cur is None or rank > (int(cur["horizon_h"]) == 24, int(cur["horizon_h"])):
            best[k] = c
    return list(best.values())


def attribute(cards: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for c in final_reads(cards):
        for kind in KINDS:
            bid = c.get(f"{kind}_block_id")
            if not bid:
                continue
            b = out.setdefault(bid, {"kind": kind, "family": c.get(f"{kind}_family"), "n": 0, "score_sum": 0.0,
                                     "score_n": 0, "composite_sum": 0.0, "posts": []})
            b["n"] += 1
            b["composite_sum"] += float(c["composite"])
            b["posts"].append(c.get("post_id"))
            s = (c.get("scores") or {}).get(kind)
            if s is not None:
                b["score_sum"] += float(s)
                b["score_n"] += 1
    for b in out.values():
        b["mean_component"] = round(b.pop("score_sum") / b["score_n"], 2) if b["score_n"] else None
        b["mean_composite"] = round(b.pop("composite_sum") / b["n"], 2)
    return out


def gene_table(cards: list[dict], k: float = 3.0) -> list[dict]:
    acc: dict[str, list[float]] = {}
    for c in final_reads(cards):
        for kind in KINDS:
            fam = c.get(f"{kind}_family")
            if fam:
                acc.setdefault(f"{kind}:{fam}", []).append(float(c["composite"]))
    rows = [{"gene": g, "n": len(v), "mean": round(sum(v) / len(v), 2),
             "shrunk": round((sum(v) + 50.0 * k) / (len(v) + k), 2)} for g, v in acc.items()]
    return sorted(rows, key=lambda r: (-r["shrunk"], r["gene"]))


def weekly_readout(cards: list[dict], benched: dict[str, str] | None = None, gate_report: dict | None = None,
                   next_tests: list[str] | None = None, week_of: str | None = None) -> str:
    genes = gene_table(cards)
    top = [g for g in genes if g["n"] >= 2][:5] or genes[:5]
    lines = [f"Strong Years growth readout, week of {week_of or datetime.now(timezone.utc).date().isoformat()}",
             f"{len(final_reads(cards))} posts had a final read this week. Scores are 0-100; 50 is a page's typical post.",
             "", "What worked (top 5 genes):"]
    lines += [f"- {g['gene']}: {g['shrunk']:.0f} across {g['n']} post(s)" for g in top] or ["- not enough reads yet"]
    lines += ["", "Benched for 14 days (scored under 30 twice in a row):"]
    lines += [f"- {g} until {str(u)[:10]}" for g, u in list((benched or {}).items())[:5]] or ["- nothing benched"]
    lines += ["", "Gate changes (rubric weights refit from our own 24 h scores):"]
    ch = (gate_report or {}).get("changes") or []
    if (gate_report or {}).get("status") == "insufficient_data":
        lines.append(f"- none: {gate_report.get('reason')}")
    elif not ch:
        lines.append("- none this week")
    else:
        verb = "applied" if gate_report.get("applied") else "proposed (dry run, not applied)"
        lines += [f"- {c['component']}: {c['old']} -> {c['new']} points ({verb})" for c in ch]
    lines += ["", "Next week's tests:"]
    lines += [f"- {t}" for t in (next_tests or [])] or ["- keep the 20% exploration floor; no new directives"]
    return "\n".join(lines)


def next_tests_from(plan: dict | None) -> list[str]:
    """Plain-English test list from growth.actions.scorecard_plan output."""
    p = plan or {}
    out = []
    if p.get("new_hooks"):
        out.append(f"{len(p['new_hooks'])} new hooks on bodies that hold but don't stop the scroll (run as Trial Reels)")
    if p.get("new_bodies"):
        out.append(f"{len(p['new_bodies'])} new bodies behind hooks that stop the scroll")
    if p.get("remix_jobs"):
        out.append(f"{len(p['remix_jobs'])} remixes of share/save standouts on the other pages")
    if p.get("topic_boosts"):
        out.append(f"double slots for {len(p['topic_boosts'])} topic(s) that reach non-followers")
    return out


def post_readout(text: str, week_of: str, client=None) -> dict:
    from common import exceptions as exc_client
    return exc_client.post_exception("growth_readout", f"Growth readout, week of {week_of}", source="growth",
                                     ref=f"readout-{week_of}", detail=text, severity="low",
                                     dedupe_key=f"growth_readout:{week_of}", client=client)
