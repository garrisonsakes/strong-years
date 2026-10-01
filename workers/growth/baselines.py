"""Rolling per-page x platform x horizon baselines: robust centre (median) and spread (MAD x 1.4826) of each scored
component, with empirical-Bayes shrinkage toward a network prior (same platform, all pages) and, below that, a
cold-start prior from config. A page with zero history therefore still gets a usable baseline; a page with 30
posts is barely shrunk.

Components (all on a log scale so z-scores are symmetric):
  views          ln(1 + views)
  share_rate     ln(smoothed shares / views)         smoothed = (x + prior * k) / (views + k), k = rate_smoothing_views
  save_rate      ln(smoothed saves / views)
  keyword_rate   ln(smoothed keyword_comments / views)
  click_through  ln(smoothed link_clicks / profile_visits)   (profile visit -> link click)
  conv_per_1k    ln(1 + (optins + buyer_weight * buyers + member_weight * members) / views * 1000), smoothed the same way

Shrinkage (per component):
  centre = (n * page_median + k * prior_centre) / (n + k)          k = prior_strength pseudo-posts
  spread = max(min_spread, (n * page_mad + k * prior_spread) / (n + k))
"""
from __future__ import annotations

import math
import statistics

from growth import config as G

COMPONENTS = ("views", "share_rate", "save_rate", "keyword_rate", "click_through", "conv_per_1k")


def smoothed_rate(x, denom, prior: float, k: float) -> float | None:
    x, denom = G.num(x, lo=0), G.num(denom, lo=0)
    if x is None or denom is None:
        return None
    return (x + prior * k) / (denom + k)


def components(snapshot: dict, cfg: dict) -> dict[str, float]:
    """Log-scale component values for one snapshot. Components whose inputs are missing are left out."""
    b, s = cfg["baselines"], cfg["scoring"]
    pr, k = b["prior_rates"], float(b["rate_smoothing_views"])
    out: dict[str, float] = {}
    views = G.num(snapshot.get("views"), lo=0)
    if views is None:
        return out
    out["views"] = math.log1p(views)
    if views < float(s["min_views_for_rates"]):
        return out
    for comp, field in (("share_rate", "shares"), ("save_rate", "saves"), ("keyword_rate", "keyword_comments")):
        if snapshot.get(field) is not None:
            r = smoothed_rate(snapshot[field], views, pr[comp], k)
            if r is not None and r > 0:
                out[comp] = math.log(r)
    pv = G.num(snapshot.get("profile_visits"), lo=0)
    if pv is not None and snapshot.get("link_clicks") is not None and pv >= float(s["min_profile_visits_for_ctr"]):
        r = smoothed_rate(snapshot["link_clicks"], pv, pr["click_through"], float(s["min_profile_visits_for_ctr"]))
        if r is not None and r > 0:
            out["click_through"] = math.log(r)
    if any(snapshot.get(k) is not None for k in ("optins", "buyers", "members")):
        conv = (G.num(snapshot.get("optins"), lo=0) or 0) * float(s["optin_weight"]) + \
               (G.num(snapshot.get("buyers"), lo=0) or 0) * float(s.get("buyer_weight", 4.0)) + \
               (G.num(snapshot.get("members"), lo=0) or 0) * float(s["member_weight"])
        per_1k = smoothed_rate(conv, views / 1000.0, pr["conv_per_1k"], k / 1000.0)
        if per_1k is not None:
            out["conv_per_1k"] = math.log1p(per_1k)
    return out


def cold_prior(platform: str, horizon_h: int, cfg: dict) -> dict[str, dict]:
    b = cfg["baselines"]
    pv = float(b["prior_views_24h"].get(platform, 500)) * float(b["horizon_curve"][str(horizon_h)])
    pr, sp = b["prior_rates"], b["prior_spread"]
    out = {"views": {"center": math.log1p(pv), "spread": float(sp["views"])}}
    for comp in ("share_rate", "save_rate", "keyword_rate", "click_through"):
        out[comp] = {"center": math.log(float(pr[comp])), "spread": float(sp[comp])}
    out["conv_per_1k"] = {"center": math.log1p(float(pr["conv_per_1k"])), "spread": float(sp["conv_per_1k"])}
    return out


def _robust(values: list[float], min_spread: float) -> tuple[float, float]:
    med = statistics.median(values)
    mad = statistics.median([abs(v - med) for v in values]) * 1.4826 if len(values) > 1 else 0.0
    return med, max(min_spread, mad)


def _history_components(history: list[dict], cfg: dict) -> dict[str, list[float]]:
    cols: dict[str, list[float]] = {c: [] for c in COMPONENTS}
    for snap in history:
        for comp, v in components(snap, cfg).items():
            cols[comp].append(v)
    return cols


def compute(page_id: str, platform: str, horizon_h: int, page_history: list[dict], network_history: list[dict] | None,
            cfg: dict | None = None) -> dict:
    """Baseline record for one page x platform x horizon.

    page_history / network_history: snapshots (post_metrics rows) at this horizon; the newest window_posts of the
    page are used. The network prior is used when it has >= network_min_posts posts, else the cold-start prior.
    """
    cfg = cfg or G.load()
    b = cfg["baselines"]
    window = int(b["window_posts"])
    k = float(b["prior_strength"])
    min_spread = float(b["min_spread"])
    page_hist = sorted(page_history or [], key=lambda s: s.get("published_at") or "")[-window:]
    page_cols = _history_components(page_hist, cfg)
    cold = cold_prior(platform, horizon_h, cfg)
    net_cols = _history_components(network_history or [], cfg)
    out = {"page_id": page_id, "platform": platform, "horizon_h": horizon_h, "n_posts": len(page_hist),
           "config_version": cfg.get("version"), "components": {}}
    for comp in COMPONENTS:
        nv = net_cols[comp]
        if len(nv) >= int(b["network_min_posts"]):
            prior_c, prior_s = _robust(nv, min_spread)
            prior_src = "network"
        else:
            prior_c, prior_s, prior_src = cold[comp]["center"], cold[comp]["spread"], "cold_start"
        pv = page_cols[comp]
        n = len(pv)
        if n:
            pc, ps = _robust(pv, min_spread)
            center = (n * pc + k * prior_c) / (n + k)
            spread = max(min_spread, (n * ps + k * prior_s) / (n + k))
        else:
            center, spread = prior_c, prior_s
        out["components"][comp] = {"center": round(center, 6), "spread": round(spread, 6), "n": n,
                                   "prior": prior_src, "shrink": round(k / (n + k), 4)}
    return out


def by_key(baselines: list[dict]) -> dict[tuple, dict]:
    return {(b["page_id"], b["platform"], int(b["horizon_h"])): b for b in baselines}
