"""Scorecard: per post, per read (1 / 6 / 12 / 24 h and 7 d), a 0-100 score per component against the page's
rolling baseline with empirical-Bayes shrinkage, and a weighted composite (conversion weighs most).

Components (raw value = a rate in [0, 1]; denominator = reach, else views; YouTube uses engagedViews [S27]):
  hook          3 s hold: IG 1 - reels_skip_rate [S17], FB retention graph at 3 s [S16], else `hold_3s`
  body          retention through the body: retention(close start) / retention(3 s) from the curve, else avg watch %
  close         close action rate: (keyword comments + DM button taps + link clicks + follows) / reach
  shares        shares / reach            saves        saves / reach          conversation   comments / reach
  non_follower  non-follower reach share  conversion   (opt-ins + 4 x buyers + 10 x members) / views
  novelty       1 - max text similarity vs the page's last 30 posts (novelty())
Shrinkage, twice: the post's own rate is pulled toward the baseline centre by rate_pseudo_count pseudo-viewers
(small posts can't swing), and the page baseline (last window_posts reads at the same platform x horizon, logit
scale) is pulled toward the network/prior centre with prior_strength pseudo-posts (young pages borrow).
  score_c = 100 * Phi((logit(v_shrunk) - mu_page) / sigma_page)        50 = the page's typical post
  composite = sum(w_c * score_c) / sum(w_c) over the components the platform reported
Instagram reads under 24 h are flagged provisional (insights can lag up to 48 h [S17]): actions wait for 24 h.
Each card carries the hook / body / close block ids and families so learning can attribute scores to blocks.
Pure; no network.
"""
from __future__ import annotations

import math

from growth import config as G

COMPONENTS = ("hook", "body", "close", "shares", "saves", "conversation", "non_follower", "conversion", "novelty")
_EPS = 1e-4


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def logit(p: float) -> float:
    p = min(1 - _EPS, max(_EPS, p))
    return math.log(p / (1 - p))


def _n(x) -> float | None:
    return G.num(x, lo=0)


def _frac(x) -> float | None:
    v = _n(x)
    if v is None:
        return None
    return v / 100.0 if v > 1.0 else v


def _curve_at(curve, t: float) -> float | None:
    """retention curve [[t_s, frac], ...] (Facebook post_video_retention_graph, normalised by the adapter) at t."""
    pts = sorted((float(a), _frac(b)) for a, b in (curve or []) if _n(a) is not None and _frac(b) is not None)
    if not pts:
        return None
    if t <= pts[0][0]:
        return pts[0][1]
    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * (t - t0) / max(1e-9, t1 - t0)
    return pts[-1][1]


def denominator(read: dict) -> tuple[float | None, str]:
    if read.get("platform") == "youtube" and _n(read.get("engaged_views")):
        return _n(read["engaged_views"]), "engaged_views"
    if _n(read.get("reach")):
        return _n(read["reach"]), "reach"
    return _n(read.get("views")), "views"


def raw_components(read: dict) -> tuple[dict[str, float], float | None, str]:
    """{component: raw rate} for what this platform reported, plus the denominator used."""
    den, den_name = denominator(read)
    views = _n(read.get("engaged_views")) if read.get("platform") == "youtube" and _n(read.get("engaged_views")) \
        else _n(read.get("views")) or den
    out: dict[str, float] = {}
    curve = read.get("retention_curve")
    hook = _frac(read.get("hold_3s"))
    if hook is None and _frac(read.get("skip_rate")) is not None:
        hook = 1.0 - _frac(read["skip_rate"])
    if hook is None and curve:
        hook = _curve_at(curve, 3.0)
    if hook is not None:
        out["hook"] = hook
    body = None
    if curve:
        dur = _n(read.get("duration_s")) or 0
        close_at = _n(read.get("close_start_s")) or (0.85 * dur if dur else None)
        r3 = _curve_at(curve, 3.0)
        if close_at and r3:
            body = min(1.0, (_curve_at(curve, close_at) or 0.0) / r3)
    if body is None:
        body = _frac(read.get("avg_watch_pct"))
    if body is not None:
        out["body"] = body
    if den:
        acts = sum(_n(read.get(k)) or 0 for k in ("keyword_comments", "dm_taps", "link_clicks", "follows"))
        if any(read.get(k) is not None for k in ("keyword_comments", "dm_taps", "link_clicks", "follows")):
            out["close"] = min(1.0, acts / den)
        for c, k in (("shares", "shares"), ("saves", "saves"), ("conversation", "comments")):
            if _n(read.get(k)) is not None:
                out[c] = min(1.0, _n(read[k]) / den)
        if _n(read.get("nonfollower_reach")) is not None and _n(read.get("reach")):
            out["non_follower"] = min(1.0, _n(read["nonfollower_reach"]) / _n(read["reach"]))
    if "non_follower" not in out and _frac(read.get("non_follower_share")) is not None:
        out["non_follower"] = _frac(read["non_follower_share"])
    if views and any(read.get(k) is not None for k in ("optins", "buyers", "members")):
        conv = (_n(read.get("optins")) or 0) + 4 * (_n(read.get("buyers")) or 0) + 10 * (_n(read.get("members")) or 0)
        out["conversion"] = min(1.0, conv / views)
    if _frac(read.get("novelty")) is not None:
        out["novelty"] = _frac(read["novelty"])
    return out, den, den_name


def novelty(text: str, recent_texts: list[str]) -> float:
    """1 - max TF-IDF cosine vs the page's last 30 posts (uniqueness.textsim)."""
    from uniqueness import textsim
    recent = [t for t in recent_texts[-30:] if t]
    if not text or not recent:
        return 1.0
    return round(1.0 - max(textsim.tfidf_cosine(text, t, recent) for t in recent), 4)


def baseline(history: list[dict], cfg: dict | None = None, network: dict | None = None) -> dict[str, dict]:
    """history: earlier raw component dicts for this page x platform x horizon (newest last). Returns
    {component: {mu, sigma, n, center}} on the logit scale, shrunk toward the network centre (or the prior)."""
    sc = (cfg or G.load())["scorecard"]
    k, floor, s0 = float(sc["prior_strength"]), float(sc["min_spread"]), float(sc["prior_spread"])
    hist = history[-int(sc["window_posts"]):]
    out = {}
    for c in COMPONENTS:
        vals = [logit(h[c]) for h in hist if h.get(c) is not None]
        mu0 = (network or {}).get(c, {}).get("mu", logit(float(sc["prior_rates"][c])))
        n = len(vals)
        mp = sum(vals) / n if n else mu0
        vp = sum((v - mp) ** 2 for v in vals) / (n - 1) if n > 1 else s0 ** 2
        mu = (n * mp + k * mu0) / (n + k)
        sigma = max(floor, math.sqrt((n * vp + k * s0 ** 2) / (n + k)))
        out[c] = {"mu": mu, "sigma": sigma, "n": n, "center": 1 / (1 + math.exp(-mu))}
    return out


def score_read(read: dict, history: list[dict], cfg: dict | None = None, network: dict | None = None) -> dict:
    """One scorecard row (table post_scores_components)."""
    cfg = cfg or G.load()
    sc = cfg["scorecard"]
    raw, den, den_name = raw_components(read)
    base = baseline(history, cfg, network)
    m = float(sc["rate_pseudo_count"])
    scores = {}
    for c, v in raw.items():
        b = base[c]
        n = den if (den and c != "novelty") else None
        shrunk = (v * n + m * b["center"]) / (n + m) if n else v
        scores[c] = round(100.0 * phi((logit(shrunk) - b["mu"]) / b["sigma"]), 2)
    w = sc["weights"]
    den_w = sum(float(w[c]) for c in scores)
    comp = round(sum(float(w[c]) * s for c, s in scores.items()) / den_w, 2) if den_w else None
    h = int(read.get("horizon_h") or 0)
    prov_before = int((sc.get("provisional_before_h") or {}).get(read.get("platform"), 0))
    return {"post_id": read.get("post_id"), "page_id": read.get("page_id"), "platform": read.get("platform"),
            "horizon_h": h, "provisional": h < prov_before, "denominator": den_name, "denominator_value": den,
            "scores": scores, "raw": {c: round(v, 6) for c, v in raw.items()}, "composite": comp,
            "baseline_n": min((base[c]["n"] for c in scores), default=0),
            "hook_block_id": read.get("hook_block_id"), "body_block_id": read.get("body_block_id"),
            "close_block_id": read.get("close_block_id"), "hook_family": read.get("hook_family"),
            "body_family": read.get("body_family"), "close_family": read.get("close_family"),
            "variant_role": read.get("variant_role"), "config_version": cfg.get("version")}


def score_many(reads: list[dict], history_by_key: dict[tuple, list[dict]] | None = None,
               cfg: dict | None = None) -> list[dict]:
    """Score reads in time order; each read's raw components join its page x platform x horizon history after it
    is scored (so a post never counts toward its own baseline)."""
    cfg = cfg or G.load()
    hist = {k: list(v) for k, v in (history_by_key or {}).items()}
    out = []
    for r in sorted(reads, key=lambda r: (str(r.get("published_at") or ""), int(r.get("horizon_h") or 0))):
        if int(r.get("horizon_h") or 0) not in tuple(cfg["scorecard"]["horizons_h"]):
            continue
        key = (r.get("page_id"), r.get("platform"), int(r["horizon_h"]))
        card = score_read(r, hist.get(key, []), cfg)
        out.append(card)
        hist.setdefault(key, []).append(card["raw"])
    return out


def read_from_capture(capture: dict, post: dict, horizon_h: int, rollups: dict | None = None) -> dict:
    """Adapter capture (growth/adapters.parse: counters + its `scorecard` extras such as skip_rate, retention_curve,
    hold_3s, engaged_views) + the post's block ids/families + our own DB rollups (keyword comments, DM taps,
    opt-ins, buyers, members, novelty) -> one scorecard read."""
    r = {k: v for k, v in capture.items() if k not in ("scorecard", "missing", "source")}
    r.update(capture.get("scorecard") or {})
    r.update({k: v for k, v in (rollups or {}).items() if v is not None})
    for k in ("post_id", "page_id", "platform", "published_at", "duration_s", "close_start_s", "variant_role",
              "hook_block_id", "body_block_id", "close_block_id", "hook_family", "body_family", "close_family"):
        if post.get(k) is not None:
            r[k] = post[k]
    r["horizon_h"] = int(horizon_h)
    return r


def db_row(card: dict) -> dict:
    """Shape for table post_scores_components (schema_growth.sql)."""
    s = card["scores"]
    return {"post_id": card["post_id"], "page_id": card.get("page_id"), "platform": card["platform"],
            "horizon_h": card["horizon_h"], "provisional": card["provisional"], "denominator": card["denominator"],
            **{f"{c}_score": s.get(c) for c in COMPONENTS}, "composite": card["composite"], "raw": card["raw"],
            "hook_block_id": card.get("hook_block_id"), "body_block_id": card.get("body_block_id"),
            "close_block_id": card.get("close_block_id"), "config_version": card.get("config_version")}
