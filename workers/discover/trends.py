"""Trend detection over normalized niche rows (normalize.rows), pure and deterministic.

  relative      rel_perf (vs the creator's own rolling median) and rel_niche (vs the platform median) per post
  velocity      metric per hour since publish; with repeated reads of one post (the hourly stream), the gain per hour
                between the last two reads (`velocity_from_reads`)
  gene trends   per platform x gene (hook:<grammar>, body:<pillar:format>, close:<keyword>): mean log2(1 + rel) over
                the recent window vs the prior window -> lift; rising = enough recent posts and lift >= rising_lift
                (or a strong recent mean with no prior history)
  transfer      a gene rising on TikTok / X / Facebook with no Instagram equivalent (absent on IG, or present but not
                performing) -> opportunity "to_instagram"; and a gene rising on Instagram with no equivalent on those
                platforms -> opportunity "from_instagram"
  feeds         daily top-20 (published in the last 48 h) and weekly top-50 (last 7 d) by trend score, plus
                (a) gate-refit rows (features + top-quartile label) for the virality gate / predictor refit and
                (b) allocator exploration observations: low-weight Beta updates on arm keys (allocator.arm_key) and
                body families, so a niche-proven gene gets explored sooner but never outweighs our own data.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from growth import allocator as AL
from growth import catalog as CAT
from discover.normalize import parse_dt

DEFAULTS = {"recent_days": 7, "prior_days": 30, "min_recent": 3, "rising_lift": 1.5, "new_gene_min_mean": 1.6,
            "ig_equivalent_min_mean": 1.0, "daily_top": 20, "daily_window_h": 48, "weekly_top": 50, "weekly_window_d": 7,
            "exploration_weight": 0.2, "exploration_top": 50, "reward_cap_rel": 8.0}
SOURCE_PLATFORMS = ("tiktok", "x", "facebook")
KITCHEN_PILLARS = {"P10", "P11", "P12", "P13"}


def _cfg(cfg):
    return {**DEFAULTS, **(cfg or {})}


def _l(rel) -> float:
    return math.log2(1.0 + max(0.0, float(rel or 0.0)))


def trend_score(r: dict) -> float:
    return round(_l(r.get("rel_perf")) + 0.5 * _l(r.get("rel_niche")), 4)


def velocity_from_reads(reads: list[dict]) -> float | None:
    """reads: [{captured_at, metric_value}] for ONE post -> gain per hour between the last two reads."""
    pts = sorted(((parse_dt(r.get("captured_at")), r.get("metric_value")) for r in reads
                  if parse_dt(r.get("captured_at")) and r.get("metric_value") is not None), key=lambda p: p[0])
    if len(pts) < 2:
        return None
    (t0, v0), (t1, v1) = pts[-2], pts[-1]
    h = (t1 - t0).total_seconds() / 3600.0
    return round((float(v1) - float(v0)) / h, 3) if h > 0 else None


def gene_trends(rows: list[dict], now: datetime, cfg: dict | None = None) -> dict[tuple[str, str], dict]:
    c = _cfg(cfg)
    rec_from = now - timedelta(days=c["recent_days"])
    pri_from = now - timedelta(days=c["prior_days"])
    acc: dict[tuple[str, str], dict] = {}
    for r in rows:
        t = parse_dt(r.get("published_at"))
        if t is None or t < pri_from or r.get("rel_perf") is None:
            continue
        win = "recent" if t >= rec_from else "prior"
        for g in r.get("genes") or []:
            a = acc.setdefault((r["platform"], g), {"recent": [], "prior": [], "posts": []})
            a[win].append(_l(r["rel_perf"]))
            if win == "recent":
                a["posts"].append((r["rel_perf"], r["id"]))
    out = {}
    for k, a in acc.items():
        rn, pn = len(a["recent"]), len(a["prior"])
        rm = sum(a["recent"]) / rn if rn else 0.0
        pm = sum(a["prior"]) / pn if pn else None
        lift = (rm / pm) if pm else None
        rising = rn >= c["min_recent"] and ((lift is not None and lift >= c["rising_lift"]) or
                                              (pm is None and rm >= c["new_gene_min_mean"]))
        out[k] = {"platform": k[0], "gene": k[1], "recent_n": rn, "prior_n": pn, "recent_mean": round(rm, 4),
                  "prior_mean": round(pm, 4) if pm is not None else None,
                  "lift": round(lift, 3) if lift is not None else None, "rising": rising,
                  "top_posts": [i for _, i in sorted(a["posts"], key=lambda p: (-p[0], p[1]))[:3]]}
    return out


def _equivalent(trends: dict, platform: str, gene: str, cfg: dict) -> bool:
    t = trends.get((platform, gene))
    return bool(t and (t["rising"] or t["recent_mean"] >= _l(cfg["ig_equivalent_min_mean"])))


def transfers(trends: dict, now: datetime, cfg: dict | None = None) -> list[dict]:
    c = _cfg(cfg)
    out = []
    for (plat, gene), t in sorted(trends.items()):
        if not t["rising"]:
            continue
        if plat in SOURCE_PLATFORMS and not _equivalent(trends, "instagram", gene, c):
            out.append({"kind": "transfer", "direction": "to_instagram", "gene": gene, "from_platform": plat,
                        "to_platforms": ["instagram"], "lift": t["lift"], "recent_mean": t["recent_mean"],
                        "recent_n": t["recent_n"], "evidence_post_ids": t["top_posts"],
                        "ig_state": "absent" if ("instagram", gene) not in trends else "underperforming",
                        "status": "open", "created_at": now.isoformat()})
        if plat == "instagram":
            missing = [p for p in SOURCE_PLATFORMS if not _equivalent(trends, p, gene, c)]
            if missing:
                out.append({"kind": "transfer", "direction": "from_instagram", "gene": gene, "from_platform": plat,
                            "to_platforms": missing, "lift": t["lift"], "recent_mean": t["recent_mean"],
                            "recent_n": t["recent_n"], "evidence_post_ids": t["top_posts"], "status": "open",
                            "created_at": now.isoformat()})
    out.sort(key=lambda o: (-(o["recent_mean"] or 0), o["gene"], o["from_platform"]))
    return out


def _length(r: dict) -> str:
    d = r.get("duration_s")
    return "S" if not d or float(d) < 30 else "M" if float(d) < 60 else "L"


def arm_of(r: dict) -> dict | None:
    """Map a niche post onto our arm space (allocator.arm_key) when its grammar is one we can produce."""
    g = r.get("hook_grammar")
    if g not in CAT.GRAMMARS or g in CAT.EXCLUDED_GRAMMARS or r.get("pillar") not in CAT.PILLAR_FORMATS:
        return None
    f = r.get("format") if r.get("format") in CAT.PILLAR_FORMATS[r["pillar"]] else CAT.PILLAR_FORMATS[r["pillar"]][0]
    spk = "DUO" if f in CAT.DUO_ONLY_FORMATS else "SUN" if r["pillar"] in KITCHEN_PILLARS else "CHANG"
    return {"pillar": r["pillar"], "grammar": g, "format": f, "speaker": spk, "length": _length(r)}


def exploration_observations(rows: list[dict], now: datetime, cfg: dict | None = None) -> list[dict]:
    c = _cfg(cfg)
    out = []
    ranked = sorted((r for r in rows if r.get("rel_perf") is not None), key=lambda r: (-trend_score(r), r["id"]))
    for r in ranked[: int(c["exploration_top"])]:
        reward = round(min(1.0, _l(r["rel_perf"]) / _l(c["reward_cap_rel"])), 4)
        obs = {"reward": reward, "weight": float(c["exploration_weight"]), "at": r.get("published_at") or now.isoformat(),
               "body_family": r.get("body_family"), "source": "discover", "niche_post": f"{r['platform']}:{r['id']}"}
        arm = arm_of(r)
        if arm:
            obs["arm_key"] = AL.arm_key(arm)
        out.append(obs)
    return out


def gate_refit_rows(rows: list[dict]) -> list[dict]:
    """Features + label (top quartile of trend score within platform) for the virality gate / predictor refit."""
    by: dict[str, list[float]] = {}
    for r in rows:
        if r.get("rel_perf") is not None:
            by.setdefault(r["platform"], []).append(trend_score(r))
    q3 = {p: sorted(v)[int(0.75 * (len(v) - 1))] for p, v in by.items() if v}
    return [{"platform": r["platform"], "hook_grammar": r.get("hook_grammar"), "pillar": r.get("pillar"),
             "format": r.get("format"), "lane": r.get("lane"), "duration_bucket": r.get("duration_bucket"),
             "cta_keyword": r.get("cta_keyword") or "", "claim_strength": r.get("claim_strength"),
             "hook_line_words": len((r.get("hook_line") or "").split()), "label_top_quartile": trend_score(r) >= q3[r["platform"]],
             "niche_post": f"{r['platform']}:{r['id']}"}
            for r in rows if r.get("rel_perf") is not None]


def _top(rows, since, n):
    sel = [r for r in rows if (parse_dt(r.get("published_at")) or since) >= since and r.get("rel_perf") is not None]
    return [{**{k: r.get(k) for k in ("platform", "id", "url", "account", "rel_perf", "rel_niche", "velocity_per_h",
                                      "hook_line", "pillar", "hook_grammar", "lane", "genes")},
             "trend_score": trend_score(r)}
            for r in sorted(sel, key=lambda r: (-trend_score(r), -(r.get("velocity_per_h") or 0), r["id"]))[:n]]


def detect(rows: list[dict], *, now: datetime | None = None, cfg: dict | None = None) -> dict:
    c = _cfg(cfg)
    now = now or datetime.now(timezone.utc)
    gt = gene_trends(rows, now, c)
    return {"daily_top20": _top(rows, now - timedelta(hours=c["daily_window_h"]), int(c["daily_top"])),
            "weekly_top50": _top(rows, now - timedelta(days=c["weekly_window_d"]), int(c["weekly_top"])),
            "rising_genes": sorted((t for t in gt.values() if t["rising"]),
                                   key=lambda t: (-t["recent_mean"], t["platform"], t["gene"])),
            "opportunities": transfers(gt, now, c),
            "gate_refit": gate_refit_rows(rows),
            "exploration_observations": exploration_observations(rows, now, c),
            "generated_at": now.isoformat()}
