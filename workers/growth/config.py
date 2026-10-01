"""Growth-engine configuration. Every threshold, cap, weight and prior used by growth/ lives here.

Nothing in growth/ hard-codes a tuning constant: modules read `load()`. A JSON file at GROWTH_CONFIG_PATH is
deep-merged over DEFAULTS, and a request may pass `config_overrides` for what-if runs. What a request can NEVER
change is the env-only safety switches below (the REVIEWER_SIGNED pattern, AUDIT M4):

  SPEND_ENABLED=1        the only way the spend executor may run at all (default 0)
  GROWTH_DRY_RUN=0       governor plans are dry-run unless this is 0 as well (default 1)
  GROWTH_LIVE_METRICS=1  the metrics adapters may call platform APIs (default 0: fixture/push mode only)
  METRICS_ALLOWED_HOSTS  comma list of exact API hosts the adapters may reach (SSRF allow-list)

Legend: [A] = assumption to confirm with live data, [C] = client decision, [B] = from BLITZ.md (canon).
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path

HORIZONS: tuple[int, ...] = (1, 3, 6, 24, 72)
PLATFORMS: tuple[str, ...] = ("instagram", "facebook", "tiktok", "youtube", "threads", "x")
CLASSES: tuple[str, ...] = ("WINNER", "PROMISING", "NORMAL", "LOSER")
COUNTERS: tuple[str, ...] = ("views", "reach", "likes", "comments", "shares", "saves", "profile_visits",
                             "link_clicks", "follows", "keyword_comments", "optins", "buyers", "members")
SNAPSHOT_FIELDS: tuple[str, ...] = COUNTERS + ("avg_watch_pct",)
MIN_EXPLORE_FLOOR = 0.20          # brief: "an exploration floor of at least 20%"; config cannot go below it

# ---- env-only switches (read at import; tests set the module attributes) -----------------------------------
SPEND_ENABLED = os.environ.get("SPEND_ENABLED", "0") == "1"
GROWTH_DRY_RUN = os.environ.get("GROWTH_DRY_RUN", "1") != "0"
GROWTH_LIVE_METRICS = os.environ.get("GROWTH_LIVE_METRICS", "0") == "1"
METRICS_ALLOWED_HOSTS = [h.strip().lower() for h in os.environ.get(
    "METRICS_ALLOWED_HOSTS",
    "graph.facebook.com,graph.instagram.com,graph.threads.net,open.tiktokapis.com,business-api.tiktok.com,"
    "youtubeanalytics.googleapis.com,api.x.com").split(",") if h.strip()]
GROWTH_AUDIT_PATH = os.environ.get("GROWTH_AUDIT_PATH", "")     # default: OUTPUT_DIR/growth/governor_audit.jsonl
GROWTH_CONFIG_PATH = os.environ.get("GROWTH_CONFIG_PATH", "")

DEFAULTS: dict = {
    "version": "growth-2026-09-30",
    # ---------------------------------------------------------------- snapshots (adapters -> horizons)
    "snapshots": {
        # a raw capture counts for horizon h when its age (hours since publish) is inside [lo, hi]
        "window_h": {"1": [0.75, 1.5], "3": [2.25, 4.5], "6": [4.5, 9.0], "24": [18.0, 36.0], "72": [54.0, 108.0]},
        "interpolate": True,              # log-time interpolation between two bracketing captures
        "interpolate_max_ratio": 3.0,     # ...only when both are within [h/3, 3h]
        "clock_skew_tolerance_h": 0.25,   # captured up to 15 min "before" publish = clock skew -> clamp to 0
        "future_tolerance_h": 0.25,       # captured more than 15 min in the future -> rejected
        "duplicate_window_s": 60,         # captures closer than this are the same snapshot
        "max_age_h": 24 * 30,
    },
    # ---------------------------------------------------------------- baselines
    "baselines": {
        "window_posts": 30,               # rolling: last N posts per page x platform x horizon [A]
        "prior_strength": 8,              # empirical-Bayes pseudo-posts pulling a young page toward the prior [A]
        "network_min_posts": 10,          # network (all pages, same platform) prior used once it has this many posts
        "min_spread": 0.15,               # floor on the robust spread (log units) so z never explodes
        "rate_smoothing_views": 200,      # beta-binomial pseudo-views on every rate (tiny samples) [A]
        # cold-start priors (page with zero history, no network data yet) [A]: median views at 24 h per platform,
        # the horizon curve relative to 24 h, rate priors, and spreads in natural-log units.
        "prior_views_24h": {"instagram": 1500, "facebook": 1500, "tiktok": 800, "youtube": 500, "threads": 150, "x": 300},
        "horizon_curve": {"1": 0.10, "3": 0.30, "6": 0.50, "24": 1.0, "72": 1.6},
        "prior_rates": {"share_rate": 0.004, "save_rate": 0.006, "keyword_rate": 0.002,
                        "click_through": 0.15, "conv_per_1k": 0.5},
        "prior_spread": {"views": 0.9, "share_rate": 0.6, "save_rate": 0.6, "keyword_rate": 0.7,
                         "click_through": 0.5, "conv_per_1k": 0.8},
    },
    # ---------------------------------------------------------------- scoring
    "scoring": {
        "weights": {"views": 0.35, "share_rate": 0.15, "save_rate": 0.15, "keyword_rate": 0.15,
                    "click_through": 0.05, "conv_per_1k": 0.15},
        "z_clip": 4.0,
        "optin_weight": 1.0, "buyer_weight": 4.0, "member_weight": 10.0,   # conv_per_1k = (optins + 4 x ebook buyers
                                                                           # + 10 x members) per 1,000 views [A]
        "min_views_for_rates": 50,        # below this, rate components are left out (too noisy)
        "min_profile_visits_for_ctr": 20,
        "classes": {
            # evaluated top-down on the latest available horizon; see scoring.classify()
            "WINNER": {"min_score": 1.5, "min_horizon_h": 6, "min_views": 1000, "min_components": 2},
            "PROMISING": {"min_score": 0.75, "min_horizon_h": 1},
            "LOSER": {"max_score": -1.0, "min_horizon_h": 24, "min_views_or_age": True},
            "breakout_views": 500000,     # PIPELINE §7.2 breakout: >= 500K views -> WINNER at >= 3 h
            "breakout_min_horizon_h": 3,
        },
        # bandit reward = clip(w_v * Phi(score / scale) + w_c * conversion_norm, 0, 1)
        "reward": {"velocity_weight": 0.6, "conversion_weight": 0.4, "score_scale": 1.5,
                   "target_optins_per_1k": 2.0, "target_buyers_per_1k": 0.5, "target_members_per_1k": 0.2},
    },
    # ---------------------------------------------------------------- winner actions
    "remix": {
        "variants_per_winner": 3,         # N remix requests for OTHER pages per winner [C]
        "max_per_target_page_per_day": 1,
        "min_stagger_h": 48,              # PIPELINE §2.3 / CONTENT_SYSTEM §8.2
        "priority": 90,                   # briefs.priority for remix of winners (PIPELINE)
        "hook_gap_days": 21,              # same hook on another page needs >= 21 days + different set/format/script
        # YouTube July 2026 inauthentic / mass-produced policy: stricter text threshold and a hard cap per source
        "youtube": {"max_remixes_per_source": 1, "text_network_max": 0.70, "shared_run_max": 4,
                    "require_distinct_first_frame": True, "require_fresh_voice_render": True},
        "uniqueness_overrides": {},       # merged over uniqueness.guard.T for remix checks
    },
    "boost": {
        "platforms": {"instagram": "meta_partnership", "facebook": "meta_partnership", "tiktok": "tiktok_spark"},
        "min_class": "WINNER",
        "default_max_daily_usd": 50,      # starting cap written onto a candidate; the governor's caps still bind [C]
    },
    "pin": {
        "platforms": {"instagram": "pin_to_grid", "tiktok": "pin_to_profile", "threads": "pin_to_profile",
                      "x": "pin_to_profile", "facebook": "feature_on_page"},
        "highlight_min_save_rate_z": 1.0, # IG: also suggest story + highlight when saves are unusually high
    },
    "loser": {"reward": 0.0, "weight_multiplier": 0.8},
    # ---------------------------------------------------------------- allocator
    "allocator": {
        "explore_floor": 0.20,            # hard minimum 0.20 (MIN_EXPLORE_FLOOR)
        "half_life_days": 14,             # arm-level decay: evidence halves every 14 days [A]
        "prior_mean": 0.5,                # neutral reward: a baseline post scores ~0.5 (growth/scoring.reward)
        "prior_strength": 20.0,           # neutral pseudo-observations on every arm (~1,000 arms per page x platform:
                                          # a diffuse prior would let lucky unseen draws crowd out proven arms) [A]
        "hier_prior_max": 8.0,            # max pseudo-observations an arm borrows from its factor marginals [A]
        "exploit_min_direct": 1.0,        # exploit tier 1: arms with >= this many (decayed) direct observations
        "exploit_min_factors": 3,         # exploit tier 2: arms sharing >= 3 of 5 observed factors; tier 3: the rest
        "max_cadence": 9,                 # 6-9 posts/day/platform per page (brief)
        "max_per_pillar_per_day": 2,
        "solo_bit_every": 3,              # CHARACTERS.md §7: >= 1 running bit per duo video, >= 1 per 3 solo videos
        "bit_cooldown": 6,                # a bit is not reused on a page until 6 others have run
        "length_buckets": {"S": [20, 34, 28], "M": [35, 47, 42], "L": [48, 59, 54]},   # [min_s, max_s, target_s]
        "default_slot_hours": [7, 9, 11, 13, 15, 17, 19, 20, 21],
        "platform_formats_only": {"F36": ["instagram", "facebook"], "F37": ["threads", "x", "facebook"]},
        "render_format": {                # editorial format -> briefs.format (content_format enum)
            "duo": "R4_duo_dialogue", "text": "T1_text_native",
            "motion": ["F01", "F11", "F14", "F17", "F20", "F21", "F22", "F23", "F25", "F34"],
            "prop": ["F04", "F06", "F18", "F19", "F28", "F30", "F31"],
            "text_formats": ["F36", "F37"],
        },
    },
    # ---------------------------------------------------------------- spend governor (BLITZ.md §9, §11)
    "governor": {
        # §9 lines per price, paid media per paid net new member. Days 1-7 carry the x1.15 learning allowance.
        # $25 values are the §9 table [B]; $30 learning lines = x1.15 of the day-8+ lines (derived, §3).
        "lines": {
            "25": {"scale": 111, "hold_max": 155, "learning_scale": 128, "learning_hold_max": 178},
            "30": {"scale": 132, "hold_max": 185, "learning_scale": 152, "learning_hold_max": 213},
        },
        "learning_days": 7,
        "cut_consecutive_days": 2,        # "> CUT two days running -> Meta -30%"
        "cut_step": 0.30,
        "scale_step": 0.20,               # "spend steps back toward plan at +20%/day"
        "initial_daily_usd": 50,          # first day of a newly approved campaign (0 -> this, never more) [C]
        "refunds_14d": {"scale_max": 0.08, "hold_max": 0.12},                    # > 12% -> stop scaling
        "chargebacks_30d": {"ok_rate": 0.0035, "ok_count": 50, "stop_rate": 0.005, "stop_count": 75},
        "renewal1": {"scale_min": 0.58, "hold_min": 0.50, "window_start_day": 25, "min_cohort": 100},
        "cash_headroom": {"ok_min": 0.30, "hold_min": 0.10},                     # < 10% -> cut
        "graduation": {                   # §11 (cold prospecting only)
            "cac_line": {"25": 111, "30": 132},
            "min_daily_spend_usd": 4000, "days_running": 5,
            "factor_central": {"25": 0.64, "30": 0.57},
            "factor_upside": {"25": 0.48, "30": 0.43},
            "min_purchases": 300,
            "renewal1_min": 0.58, "renewal1_gate_day": 40,
            "refund_max": 0.12, "chargeback_rate_max": 0.0035,
        },
        "boost_requires_class": "WINNER",
        "max_boost_daily_usd": 250,       # per-boost daily ceiling, whatever a human approves [C]
        "max_retarget_daily_usd": 1000,   # retargeting (engaged viewers) daily ceiling [C]
        "max_cold_daily_usd": 8000,       # BLITZ §11 R4 settings: Meta $8K/day after graduation [B]
        "pre_gate_cold_daily_usd": 0,     # 0 = no cold budget before §11 passes. BLITZ §12 R7 runs $3K/day flat on
                                          # days 1-10 to buy the gate's numbers: set 3000 to allow that [C]
        "max_abs_usd": 1_000_000,         # sanity bound: any money input above this is treated as invalid
    },
}


def _deep_merge(base: dict, over: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _check_finite(obj, path="") -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _check_finite(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _check_finite(v, f"{path}[{i}]")
    elif isinstance(obj, float) and not math.isfinite(obj):
        raise ValueError(f"growth config: non-finite value at {path}")


def validate(cfg: dict) -> dict:
    _check_finite(cfg)
    a = cfg["allocator"]
    if float(a["explore_floor"]) < MIN_EXPLORE_FLOOR:
        raise ValueError(f"growth config: allocator.explore_floor must be >= {MIN_EXPLORE_FLOOR}")
    if not 1 <= int(a["max_cadence"]) <= 9:
        raise ValueError("growth config: allocator.max_cadence must be 1..9")
    c = cfg["scoring"]["classes"]
    if not c["WINNER"]["min_score"] > c["PROMISING"]["min_score"] > c["LOSER"]["max_score"]:
        raise ValueError("growth config: class thresholds must satisfy WINNER > PROMISING > LOSER")
    g = cfg["governor"]
    if not (0 < g["cut_step"] < 1 and 0 < g["scale_step"] <= 1):
        raise ValueError("growth config: governor steps must be fractions")
    for price, ln in g["lines"].items():
        if not (0 < ln["scale"] <= ln["hold_max"] and 0 < ln["learning_scale"] <= ln["learning_hold_max"]):
            raise ValueError(f"growth config: governor lines for ${price} must satisfy scale <= hold_max")
    for k in ("max_boost_daily_usd", "max_retarget_daily_usd", "max_cold_daily_usd", "pre_gate_cold_daily_usd",
              "initial_daily_usd", "max_abs_usd"):
        if num(g[k], lo=0) is None:
            raise ValueError(f"growth config: governor.{k} must be a finite number >= 0")
    return cfg


_cache: dict = {}


# Round 5 audit: the governor's money caps and gate lines are NOT what-if parameters. A request's
# config_overrides may tune scoring/allocation, but any key under "governor" is refused (they come only from
# DEFAULTS or the GROWTH_CONFIG_PATH file the operator controls), so an authenticated caller (n8n, or anyone
# holding its token) can never lift a cap or open cold spend in the same request that asks for a plan.
PROTECTED_OVERRIDE_KEYS = ("governor",)


class ProtectedOverride(ValueError):
    pass


def reject_protected_overrides(overrides: dict | None) -> None:
    for k in PROTECTED_OVERRIDE_KEYS:
        if overrides and k in overrides:
            raise ProtectedOverride(f"config_overrides.{k} is not allowed: caps and gates come only from the operator's config file")


def load(overrides: dict | None = None) -> dict:
    """DEFAULTS <- GROWTH_CONFIG_PATH file <- overrides (request what-ifs; never governor.*). Validated every time."""
    reject_protected_overrides(overrides)
    path = GROWTH_CONFIG_PATH
    key = (path, Path(path).stat().st_mtime if path and Path(path).is_file() else None)
    if key not in _cache:
        base = DEFAULTS
        if path and Path(path).is_file():
            base = _deep_merge(DEFAULTS, json.loads(Path(path).read_text()))
        _cache.clear()
        _cache[key] = validate(base)
    cfg = _cache[key]
    return validate(_deep_merge(cfg, overrides)) if overrides else copy.deepcopy(cfg)


def fingerprint(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]


def num(x, *, lo: float | None = None, hi: float | None = None) -> float | None:
    """A finite float inside [lo, hi], else None. Every external number goes through this (NaN, inf, '12', None)."""
    if isinstance(x, bool) or x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(v):
        return None
    if lo is not None and v < lo:
        return None
    if hi is not None and v > hi:
        return None
    return v


def price_key(price, lines: dict) -> str | None:
    """'25' / '30' when the price has governor lines, else None (unknown price -> fail safe, no increases)."""
    p = num(price, lo=0, hi=10_000)
    if p is None:
        return None
    k = str(int(round(p)))
    return k if abs(p - round(p)) < 1e-9 and k in lines else None
