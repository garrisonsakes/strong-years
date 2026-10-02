"""Velocity score and class per post.

score(snapshots_for_post, baseline_lookup, cfg) -> post_scores row:
  {post_id, page_id, platform, horizon_h, score, z: {component: z}, components_used, views, class, reasons,
   reward, breakout, config_version}

  z_c    = clip((value_c - centre_c) / spread_c, -z_clip, z_clip)             from growth/baselines
  score  = sum(w_c * z_c) / sum(w_c) over the components available for this snapshot
  class  (evaluated on the latest available horizon, top-down):
    WINNER     score >= 1.5 at >= 6 h with >= 1,000 views and >= 2 components,  OR  breakout (>= 500K views at >= 3 h,
               or >= 5x the page's median views at >= 6 h once the page has 5 posts at that horizon)
    PROMISING  score >= 0.75 at >= 1 h
    LOSER      score <= -1.0 at >= 24 h
    NORMAL     otherwise (including anything that is too young or too small to call)
  reward = clip(w_ss * Phi(z_share_save / scale) + w_v * Phi(score / scale) + w_c * conversion_norm, 0, 1)
           the allocator's Bernoulli reward; (shares + saves) per view is the primary term (VIRALITY_SYSTEM.md §4),
           falling back to the velocity term when the platform reports neither shares nor saves
           (conversion_norm = 0 when no rollups are known: no evidence, no credit)
"""
from __future__ import annotations

import math

from growth import baselines as B
from growth import config as G


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def zscores(snapshot: dict, baseline: dict, cfg: dict) -> tuple[dict[str, float], dict[str, float]]:
    comps = B.components(snapshot, cfg)
    clip = float(cfg["scoring"]["z_clip"])
    z = {}
    for c, v in comps.items():
        bc = (baseline.get("components") or {}).get(c)
        if not bc or not bc.get("spread"):
            continue
        z[c] = max(-clip, min(clip, (v - float(bc["center"])) / float(bc["spread"])))
    return z, comps


def composite(z: dict[str, float], cfg: dict) -> float | None:
    w = cfg["scoring"]["weights"]
    num = sum(float(w[c]) * z[c] for c in z if c in w)
    den = sum(float(w[c]) for c in z if c in w)
    return None if den <= 0 else num / den


def conversion_norm(snapshot: dict, cfg: dict) -> float | None:
    r = cfg["scoring"]["reward"]
    views = G.num(snapshot.get("views"), lo=1)
    if views is None or all(snapshot.get(k) is None for k in ("optins", "buyers", "members")):
        return None
    opt = (G.num(snapshot.get("optins"), lo=0) or 0) / views * 1000
    buy = (G.num(snapshot.get("buyers"), lo=0) or 0) / views * 1000
    mem = (G.num(snapshot.get("members"), lo=0) or 0) / views * 1000
    # waitlist opt-ins, ebook buyers and members each saturate at their target rate; members weigh most
    return min(1.0, 0.3 * min(1.0, opt / float(r["target_optins_per_1k"])) +
               0.3 * min(1.0, buy / float(r.get("target_buyers_per_1k", 0.5))) +
               0.4 * min(1.0, mem / float(r["target_members_per_1k"])))


def reward(score: float | None, conv: float | None, cfg: dict, share_save_z: float | None = None) -> float:
    """Bandit reward in [0, 1]. Unknown velocity counts as baseline (0.5); unknown conversions earn no conversion
    credit (0), so a post with measured conversions is never ranked below one whose rollups are missing. The n8n
    normalize node therefore always sends optins / buyers / members (0 when none) once the DB feeds exist."""
    r = cfg["scoring"]["reward"]
    vel = phi(score / float(r["score_scale"])) if score is not None else 0.5
    # primary reward: (shares + saves) per view; unknown counts as baseline (0.5), like velocity
    ss = phi(share_save_z / float(r["score_scale"])) if share_save_z is not None else vel
    v = float(r.get("share_save_weight", 0.0)) * ss + float(r["velocity_weight"]) * vel + \
        float(r["conversion_weight"]) * (conv or 0.0)
    return max(0.0, min(1.0, v)) if math.isfinite(v) else 0.5


def classify(score: float | None, horizon_h: int, views: int | None, n_components: int, cfg: dict,
             page_median_views: float | None = None) -> tuple[str, list[str]]:
    c = cfg["scoring"]["classes"]
    views = views or 0
    if views >= int(c["breakout_views"]) and horizon_h >= int(c["breakout_min_horizon_h"]):
        return "WINNER", [f"breakout: {views} views at {horizon_h} h"]
    rel = float(c.get("breakout_rel_median", 0) or 0)
    if rel and page_median_views and page_median_views > 0 and views >= int(c.get("breakout_rel_min_views", 0)) \
            and horizon_h >= int(c.get("breakout_rel_min_horizon_h", 6)) and views >= rel * page_median_views:
        return "WINNER", [f"breakout: {views} views = {views / page_median_views:.1f}x the page median at {horizon_h} h"]
    if score is None:
        return "NORMAL", ["no scorable components"]
    w = c["WINNER"]
    if score >= float(w["min_score"]) and horizon_h >= int(w["min_horizon_h"]) and views >= int(w["min_views"]) \
            and n_components >= int(w["min_components"]):
        return "WINNER", [f"score {score:.2f} >= {w['min_score']} at {horizon_h} h, {views} views, {n_components} components"]
    why = []                                  # why a winner-level score is not (yet) a WINNER
    if score >= float(w["min_score"]):
        if horizon_h < int(w["min_horizon_h"]):
            why.append(f"score {score:.2f} but only {horizon_h} h old: wait for the {w['min_horizon_h']} h horizon")
        if views < int(w["min_views"]):
            why.append(f"score {score:.2f} on only {views} views (< {w['min_views']}): too small to call")
        if n_components < int(w["min_components"]):
            why.append(f"score {score:.2f} from {n_components} component(s) (< {w['min_components']}): too thin to call")
    p = c["PROMISING"]
    if score >= float(p["min_score"]) and horizon_h >= int(p["min_horizon_h"]):
        return "PROMISING", [f"score {score:.2f} >= {p['min_score']} at {horizon_h} h"] + why
    lo = c["LOSER"]
    if score <= float(lo["max_score"]) and horizon_h >= int(lo["min_horizon_h"]):
        return "LOSER", [f"score {score:.2f} <= {lo['max_score']} at {horizon_h} h"]
    if score <= float(lo["max_score"]):
        why.append(f"score {score:.2f} but only {horizon_h} h old: LOSER needs the {lo['min_horizon_h']} h horizon")
    return "NORMAL", why or [f"score {score:.2f} within the normal band"]


def score_post(snapshots: list[dict], baseline_lookup: dict[tuple, dict], cfg: dict | None = None) -> dict | None:
    """Score one post from its snapshots (any subset of horizons) and the baselines keyed
    (page_id, platform, horizon_h). Uses the latest horizon for the class; earlier horizons are reported."""
    cfg = cfg or G.load()
    snaps = sorted([s for s in snapshots if s.get("horizon_h") in G.HORIZONS], key=lambda s: s["horizon_h"])
    if not snaps:
        return None
    per_h = []
    for s in snaps:
        key = (s.get("page_id"), s.get("platform"), int(s["horizon_h"]))
        base = baseline_lookup.get(key)
        if base is None:
            base = B.compute(s.get("page_id"), s.get("platform"), int(s["horizon_h"]), [], None, cfg)
        z, comps = zscores(s, base, cfg)
        sc = composite(z, cfg)
        per_h.append({"horizon_h": int(s["horizon_h"]), "score": None if sc is None else round(sc, 4),
                      "z": {k: round(v, 4) for k, v in z.items()}, "components_used": sorted(z),
                      "views": s.get("views"), "interpolated": bool(s.get("interpolated")), "baseline_n": base.get("n_posts", 0)})
    latest = per_h[-1]
    last_snap = snaps[-1]
    lb = baseline_lookup.get((last_snap.get("page_id"), last_snap.get("platform"), int(last_snap["horizon_h"]))) or {}
    cls, reasons = classify(latest["score"], latest["horizon_h"], last_snap.get("views"), len(latest["components_used"]), cfg,
                            lb.get("median_views") if int(lb.get("n_posts") or 0) >= 5 else None)
    conv = conversion_norm(last_snap, cfg)
    return {"post_id": last_snap["post_id"], "page_id": last_snap.get("page_id"), "platform": last_snap.get("platform"),
            "horizon_h": latest["horizon_h"], "score": latest["score"], "z": latest["z"],
            "components_used": latest["components_used"], "views": last_snap.get("views"),
            "class": cls, "reasons": reasons, "breakout": any("breakout" in r for r in reasons),
            "conversion_norm": None if conv is None else round(conv, 4),
            "reward": round(reward(latest["score"], conv, cfg, latest["z"].get("share_save_rate")), 4),
            "share_save_z": latest["z"].get("share_save_rate"),
            "retention_proxy": _retention_proxy(snaps),
            "save_rate_z": latest["z"].get("save_rate"), "history": per_h, "config_version": cfg.get("version")}


def _retention_proxy(snaps: list[dict]) -> float | None:
    """Mean watch-through at the 1 h and 3 h horizons (VIRALITY_SYSTEM.md §4); None when the platform gave none."""
    vals = [B.retention_value(s) for s in snaps if int(s.get("horizon_h") or 0) in B.RETENTION_HORIZONS]
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 4) if vals else None


def score_many(snapshots: list[dict], baselines: list[dict], cfg: dict | None = None) -> list[dict]:
    cfg = cfg or G.load()
    lookup = B.by_key(baselines)
    by_post: dict[str, list[dict]] = {}
    for s in snapshots:
        by_post.setdefault(str(s.get("post_id")), []).append(s)
    out = []
    for pid, snaps in by_post.items():
        r = score_post(snaps, lookup, cfg)
        if r:
            out.append(r)
    out.sort(key=lambda r: (r["score"] if r["score"] is not None else -99), reverse=True)
    return out
