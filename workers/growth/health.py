"""Account health: distribution state per account, separate from creative quality.

POSTDB_FINDINGS §2 Rule 0: the same Yang Mun script did 40-100x better on a healthy IG account than on TikTok, and
TikTok median reach fell 97% after a 279-day gap while like rate stayed flat (4.87% -> 4.92%). Viewers liked the
posts as much as before; far fewer were shown them. So we watch each account's reach against its own history and
its siblings, and act on the account, not the hook.

check(account_posts, cfg, now) -> one row per account:
  {account, platform, state, recent_median, prior_median, ratio, sibling_ratio, like_rate_ratio, gap_h, reasons,
   actions}
  state     SUPPRESSED  recent median views < suppressed_ratio x prior median (or < sibling_ratio x siblings)
            WATCH       recent median < watch_ratio x prior
            DORMANCY_RISK  no post for max_gap_h (checked first-class: the gap is what preceded their collapse)
            HEALTHY / NEW (too little history to call)
  actions   the playbook for that state; nothing here posts, deletes or spends.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import median

from growth import config as G

ACTIONS = {
    "SUPPRESSED": [
        "pause Trial Reels and cross-posted re-cuts on this account for 72 h (keep 1-2 fresh native posts/day)",
        "check the account status / recommendation-eligibility screen and the AI label on the last 20 posts",
        "check the last 7 days for near-duplicates (uniqueness guard) and remove nothing without a human",
        "shift tomorrow's volume to sibling accounts of the same character",
    ],
    "WATCH": ["hold volume flat (no ramp step) and route only fresh masters here until the ratio recovers"],
    "DORMANCY_RISK": ["post one fresh native video now; never let an account go silent (their 279-day gap preceded -97%)"],
    "HEALTHY": [],
    "NEW": [],
}


def _dt(v) -> datetime | None:
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _like_rate(posts: list[dict]) -> float | None:
    v = sum(float(p.get("views") or 0) for p in posts)
    return sum(float(p.get("likes") or 0) for p in posts) / v if v > 0 else None


def check(posts: list[dict], cfg: dict | None = None, now: datetime | None = None) -> list[dict]:
    """posts: {account, platform, published_at, views, likes?} at one comparable horizon (e.g. 24 h)."""
    cfg = cfg or G.load()
    h = cfg["health"]
    now = now or datetime.now(timezone.utc)
    rec_from = now - timedelta(days=int(h["recent_days"]))
    pri_from = rec_from - timedelta(days=int(h["prior_days"]))
    by: dict[tuple[str, str], list[dict]] = {}
    for p in posts:
        d = _dt(p.get("published_at"))
        if d is None or p.get("views") is None:
            continue
        by.setdefault((str(p.get("account")), str(p.get("platform"))), []).append({**p, "_d": d})
    recent_med = {k: median([float(p["views"]) for p in v if p["_d"] >= rec_from])
                  for k, v in by.items() if any(p["_d"] >= rec_from for p in v)}
    out = []
    for (acct, plat), ps in sorted(by.items()):
        rec = [p for p in ps if p["_d"] >= rec_from]
        pri = [p for p in ps if pri_from <= p["_d"] < rec_from]
        gap_h = (now - max(p["_d"] for p in ps)).total_seconds() / 3600
        rm = median([float(p["views"]) for p in rec]) if rec else None
        pm = median([float(p["views"]) for p in pri]) if pri else None
        sib = [m for (a, pl), m in recent_med.items() if pl == plat and a != acct]
        sm = median(sib) if sib else None
        ratio = rm / pm if rm is not None and pm else None
        sratio = rm / sm if rm is not None and sm else None
        lr_r, lr_p = _like_rate(rec), _like_rate(pri)
        lrr = lr_r / lr_p if lr_r is not None and lr_p else None
        reasons: list[str] = []
        state = "HEALTHY"
        enough = len(rec) >= int(h["min_posts_recent"])
        if gap_h >= float(h["max_gap_h"]):
            state = "DORMANCY_RISK"
            reasons.append(f"no post for {gap_h:.0f} h (>= {h['max_gap_h']} h)")
        elif not enough or len(pri) < int(h["min_posts_prior"]):
            state = "NEW"
            reasons.append(f"history too thin ({len(rec)} recent, {len(pri)} prior posts)")
        if enough and state != "DORMANCY_RISK":
            if ratio is not None and len(pri) >= int(h["min_posts_prior"]) and ratio < float(h["suppressed_ratio"]):
                state = "SUPPRESSED"
                reasons.append(f"recent median {rm:.0f} = {ratio:.0%} of prior {pm:.0f}")
            elif sratio is not None and sratio < float(h["sibling_ratio"]):
                state = "SUPPRESSED"
                reasons.append(f"recent median {rm:.0f} = {sratio:.0%} of sibling {plat} accounts ({sm:.0f})")
            elif ratio is not None and len(pri) >= int(h["min_posts_prior"]) and ratio < float(h["watch_ratio"]):
                state = "WATCH"
                reasons.append(f"recent median {rm:.0f} = {ratio:.0%} of prior {pm:.0f}")
        if state in ("SUPPRESSED", "WATCH") and lrr is not None and abs(lrr - 1) <= float(h["engagement_stable_band"]):
            reasons.append(f"like rate steady ({lrr:.2f}x prior): distribution, not creative")
        out.append({"account": acct, "platform": plat, "state": state,
                    "recent_median": rm, "prior_median": pm,
                    "ratio": None if ratio is None else round(ratio, 3),
                    "sibling_ratio": None if sratio is None else round(sratio, 3),
                    "like_rate_ratio": None if lrr is None else round(lrr, 3),
                    "gap_h": round(gap_h, 1), "reasons": reasons, "actions": ACTIONS[state]})
    return out
