"""Winner actions as QUEUED JOBS, never direct publishing or spending.

plan(scores, posts, pages, cfg, *, now, recent_remixes, ad_texts, judge_fn) -> {
  "remix_jobs":        L3 derivative requests for OTHER pages (PIPELINE §2.3 / §7.3): new hook from the same proven
                       grammar, different set and speaker pairing, new opening frame, new captions; must pass
                       /uniqueness/check (thresholds carried on the job) and, for YouTube, the July 2026 inauthentic /
                       mass-produced policy limits (one remix per source, stricter text threshold, fresh first frame
                       and fresh voice render).
  "boost_candidates":  Meta partnership ads / TikTok Spark candidates for WINNERs only, re-checked under the ad
                       policy (growth/adpolicy) with the mandatory judge; flagged/human -> human queue. A candidate is
                       never approved here: the governor needs a human approval record.
  "pin_suggestions":   pin / feature / highlight suggestions for a human to apply.
  "downweights":       LOSER arms for the allocator (reward 0, multiplier < 1).
}
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone

from growth import adpolicy
from growth import catalog as CAT
from growth import config as G
from growth import snapshots as S
from uniqueness import guard

CLASS_RANK = {"LOSER": 0, "NORMAL": 1, "PROMISING": 2, "WINNER": 3}


def _page_by_id(pages: list[dict]) -> dict[str, dict]:
    return {str(p["id"]): p for p in pages}


def _speakers(page: dict) -> tuple[str, ...]:
    dna = page.get("page_dna") or {}
    sp = tuple(dna.get("speakers") or CAT.PAGE_SPEAKERS.get(page.get("slug"), ()))
    return sp or CAT.SPEAKERS


def _pick_speaker(target: dict, source_speaker: str | None, fmt: str | None) -> str:
    opts = list(_speakers(target))
    if fmt in CAT.DUO_ONLY_FORMATS:
        return "DUO"
    for s in opts:                      # different speaker pairing first, but only from the target's own speakers
        if s != source_speaker:
            return s
    return opts[0]


def _arm(post: dict) -> dict:
    a = post.get("arm") or {}
    return {"pillar": a.get("pillar") or post.get("pillar"), "grammar": a.get("grammar") or post.get("grammar"),
            "format": a.get("format") or post.get("editorial_format"), "speaker": a.get("speaker") or post.get("speaker_mode"),
            "length": a.get("length") or post.get("length_bucket"), "set_code": post.get("set_code"),
            "hook_id": post.get("hook_id")}


def remix_jobs_for(score: dict, post: dict, pages: dict[str, dict], cfg: dict, now: datetime,
                   recent_remixes: list[dict]) -> list[dict]:
    r = cfg["remix"]
    src_page = pages.get(str(score.get("page_id")))
    if not src_page:
        return []
    arm = _arm(post)
    platform = score["platform"]
    # per-source cap: YouTube allows 1 remix per source (mass-produced policy), others variants_per_winner
    n_max = int(r["youtube"]["max_remixes_per_source"]) if platform == "youtube" else int(r["variants_per_winner"])
    existing = [j for j in recent_remixes if str(j.get("source_post_id")) == str(score["post_id"])]
    if len(existing) >= n_max:
        return []
    taken_targets = {str(j.get("target_page_id")) for j in existing}
    day_counts: dict[str, int] = {}
    for j in recent_remixes:
        d = S.parse_dt(j.get("created_at"))
        if d and (now - d) < timedelta(days=1):
            day_counts[str(j.get("target_page_id"))] = day_counts.get(str(j.get("target_page_id")), 0) + 1
    # candidate target pages: active, same locale family, not the source, not the localized child of the source
    cands = []
    for pid, p in pages.items():
        if pid == str(src_page["id"]) or pid in taken_targets:
            continue
        if p.get("status") not in (None, "active"):
            continue
        if (p.get("locale") or "en-US")[:2] != (src_page.get("locale") or "en-US")[:2]:
            continue
        if day_counts.get(pid, 0) >= int(r["max_per_target_page_per_day"]):
            continue
        fit = 0
        if arm["pillar"] and arm["pillar"] in ((p.get("page_dna") or {}).get("pillars") or []):
            fit += 2
        if arm["speaker"] and arm["speaker"] not in _speakers(p):
            fit += 1                    # a different speaker pairing is what we want
        cands.append((fit, p.get("slug") or pid, p))
    cands.sort(key=lambda c: (-c[0], c[1]))
    jobs = []
    earliest = now + timedelta(hours=float(r["min_stagger_h"]))
    src_when = S.parse_dt(post.get("published_at")) or now
    for fit, _, target in cands[: n_max - len(existing)]:
        fmt = arm["format"]
        speaker = _pick_speaker(target, arm["speaker"], fmt)
        th = {**guard.T, **(r.get("uniqueness_overrides") or {})}
        yt = platform == "youtube"
        if yt:
            th["text_network"] = min(th["text_network"], float(r["youtube"]["text_network_max"]))
            th["shared_run_max"] = min(th["shared_run_max"], int(r["youtube"]["shared_run_max"]))
        # never land in the same slot hour as the source (stagger rule 6)
        hour = (src_when.hour + 3 + len(jobs)) % 24
        jobs.append({
            "kind": "remix", "status": "queued", "priority": int(r["priority"]),
            "source_post_id": score["post_id"], "source_page_id": str(src_page["id"]), "source_platform": platform,
            "source_score": score.get("score"), "source_class": score.get("class"),
            "target_page_id": str(target["id"]), "target_page_slug": target.get("slug"),
            "earliest_at": earliest.isoformat(), "preferred_slot_hour": hour,
            "level": "L3", "grammar": arm["grammar"], "pillar": arm["pillar"], "editorial_format": fmt,
            "speaker": speaker, "length_bucket": arm["length"],
            "requirements": {
                "new_hook_same_grammar": True, "hook_gap_days": int(r["hook_gap_days"]), "source_hook_id": arm["hook_id"],
                "different_set": True, "exclude_set_codes": [arm["set_code"]] if arm["set_code"] else [],
                "different_speaker_pairing": speaker != arm["speaker"], "new_opening_frame": True,
                "new_captions": True, "new_voice_render": True, "same_evidence": True,
                "min_axes_changed": 4, "shared_run_max": th["shared_run_max"],
                "youtube_inauthentic_policy_2026_07": yt,
                "require_distinct_first_frame": bool(yt and r["youtube"]["require_distinct_first_frame"]),
            },
            "uniqueness_thresholds": th, "must_pass": ["/uniqueness/check", "/compliance/scan", "llm_judge"],
            "created_at": now.isoformat(),
        })
    return jobs


def boost_candidate_for(score: dict, post: dict, cfg: dict, now: datetime, ad_texts: dict | None, judge_fn) -> dict | None:
    b = cfg["boost"]
    if CLASS_RANK.get(score.get("class"), 0) < CLASS_RANK[b["min_class"]]:
        return None
    channel = b["platforms"].get(score["platform"])
    if not channel:
        return None
    texts = dict(ad_texts or {})
    texts.setdefault("caption", post.get("caption") or "")
    texts.setdefault("on_screen", " ".join(post.get("burned_in_text") or []))
    texts.setdefault("hook", post.get("hook") or "")
    if not any(v for v in texts.values()):
        chk = {"verdict": "human", "hits": [], "reasons": ["no ad text supplied: a human must attach and re-check"],
               "judge_passed": False}
    else:
        chk = adpolicy.check({k: v for k, v in texts.items() if isinstance(v, str)}, evidence=post.get("evidence") or [],
                             judge_fn=judge_fn, page_slug=post.get("page_slug") or "")
    status = {"pass": "awaiting_human_approval", "flagged": "flagged_human", "human": "needs_human"}[chk["verdict"]]
    return {"kind": "boost", "status": status, "post_id": score["post_id"], "page_id": score.get("page_id"),
            "platform": score["platform"], "channel": channel, "class": score["class"], "score": score.get("score"),
            "views": score.get("views"), "requested_daily_usd": float(b["default_max_daily_usd"]),
            "compliance": {"verdict": chk["verdict"], "hits": chk.get("hits", []), "judge_passed": chk.get("judge_passed"),
                           "reasons": chk.get("reasons", [])},
            "requires": ["human_approval", "governor_plan", "SPEND_ENABLED"], "ai_label_kept": True,
            "created_at": now.isoformat()}


def pin_suggestion_for(score: dict, cfg: dict, now: datetime) -> dict | None:
    p = cfg["pin"]
    if score.get("class") != "WINNER":
        return None
    action = p["platforms"].get(score["platform"])
    if not action:
        return None
    out = {"kind": "pin", "status": "suggested", "post_id": score["post_id"], "page_id": score.get("page_id"),
           "platform": score["platform"], "action": action, "score": score.get("score"), "created_at": now.isoformat()}
    if score["platform"] == "instagram" and (score.get("save_rate_z") or 0) >= float(p["highlight_min_save_rate_z"]):
        out["also"] = ["share_to_story", "add_to_highlight"]
    return out


def plan(scores: list[dict], posts: list[dict], pages: list[dict], cfg: dict | None = None, *,
         now: datetime | None = None, recent_remixes: list[dict] | None = None, ad_texts: dict[str, dict] | None = None,
         judge_fn=None) -> dict:
    cfg = cfg or G.load()
    now = now or datetime.now(timezone.utc)
    pages_by = _page_by_id(pages)
    posts_by = {str(p["post_id"]): p for p in posts}
    recent = list(recent_remixes or [])
    out = {"remix_jobs": [], "boost_candidates": [], "pin_suggestions": [], "downweights": [], "skipped": []}
    for sc in sorted(scores, key=lambda s: (s.get("score") or -99), reverse=True):
        post = posts_by.get(str(sc["post_id"]), {"post_id": sc["post_id"]})
        if sc.get("class") == "WINNER":
            jobs = remix_jobs_for(sc, post, pages_by, cfg, now, recent)
            out["remix_jobs"] += jobs
            recent += jobs
            bc = boost_candidate_for(sc, post, cfg, now, (ad_texts or {}).get(str(sc["post_id"])), judge_fn)
            if bc:
                out["boost_candidates"].append(bc)
            pin = pin_suggestion_for(sc, cfg, now)
            if pin:
                out["pin_suggestions"].append(pin)
        elif sc.get("class") == "LOSER":
            arm = _arm(post)
            out["downweights"].append({"post_id": sc["post_id"], "page_id": sc.get("page_id"), "platform": sc["platform"],
                                       "arm": arm, "reward": float(cfg["loser"]["reward"]),
                                       "weight_multiplier": float(cfg["loser"]["weight_multiplier"])})
        else:
            out["skipped"].append({"post_id": sc["post_id"], "class": sc.get("class")})
    out["counts"] = {k: len(v) for k, v in out.items() if isinstance(v, list)}
    return out


# ---------------------------------------------------------------- scorecard actions (growth/scorecard.py)
def _final(cards: list[dict], min_h: int = 6) -> dict[str, dict]:
    """Latest non-provisional read per post at >= min_h."""
    out: dict[str, dict] = {}
    for c in cards:
        if c.get("provisional") or int(c.get("horizon_h") or 0) < min_h:
            continue
        k = str(c["post_id"])
        if k not in out or int(c["horizon_h"]) > int(out[k]["horizon_h"]):
            out[k] = c
    return out


def genes_of(card: dict) -> list[str]:
    return [f"{k}:{card[f'{k}_family']}" for k in ("hook", "body", "close") if card.get(f"{k}_family")]


def scorecard_plan(cards: list[dict], posts: list[dict], pages: list[dict], cfg: dict | None = None, *,
                   now: datetime | None = None, recent_remixes: list[dict] | None = None,
                   gene_history: dict[str, list[float]] | None = None, benched: dict[str, str] | None = None,
                   ad_texts: dict[str, dict] | None = None, judge_fn=None) -> dict:
    """Scorecard rules -> queued jobs (never publishing or spending):
      hook >= 85                        -> 2 new bodies for that hook block
      body >= 85 and hook < 50          -> 3 new hooks for that body block (they run as Trial Reels)
      shares or saves >= 90             -> remix to every other page + a boost candidate (still WINNER-gated)
      non_follower >= 80                -> double that topic's (pillar) slots on the page for the next plan
      a gene's 24 h composite < 30 twice in a row -> bench the gene 14 days (allocator skips it)
    gene_history: gene -> earlier 24 h composites (oldest first); updated copy is returned as `gene_history`."""
    cfg = cfg or G.load()
    a = cfg["scorecard"]["actions"]
    now = now or datetime.now(timezone.utc)
    posts_by = {str(p["post_id"]): p for p in posts}
    pages_by = _page_by_id(pages)
    hist = {g: list(v) for g, v in (gene_history or {}).items()}
    bench = dict(benched or {})
    recent = list(recent_remixes or [])
    out = {"new_bodies": [], "new_hooks": [], "remix_jobs": [], "boost_candidates": [], "topic_boosts": [],
           "bench": [], "skipped_provisional": sorted({str(c["post_id"]) for c in cards if c.get("provisional")})}
    for pid, c in sorted(_final(cards).items(), key=lambda kv: -(kv[1].get("composite") or 0)):
        s, post = c.get("scores") or {}, posts_by.get(pid, {"post_id": pid})
        base = {"source_post_id": pid, "page_id": c.get("page_id"), "platform": c.get("platform"),
                "horizon_h": c.get("horizon_h"), "status": "queued", "created_at": now.isoformat()}
        if (s.get("hook") or 0) >= a["hook_strong"]:
            for k in range(int(a["new_bodies"])):
                out["new_bodies"].append({**base, "kind": "new_body", "n": k + 1, "keep_hook_block_id": c.get("hook_block_id"),
                                          "hook_family": c.get("hook_family"), "exclude_body_block_id": c.get("body_block_id"),
                                          "rule": f"hook {s['hook']:.0f} >= {a['hook_strong']}"})
        if (s.get("body") or 0) >= a["body_strong"] and s.get("hook") is not None and s["hook"] < a["hook_weak"]:
            for k in range(int(a["new_hooks"])):
                out["new_hooks"].append({**base, "kind": "new_hook", "n": k + 1, "keep_body_block_id": c.get("body_block_id"),
                                         "variant_role": "TEST", "exclude_hook_block_id": c.get("hook_block_id"),
                                         "rule": f"body {s['body']:.0f} >= {a['body_strong']} and hook {s['hook']:.0f} < {a['hook_weak']}"})
        if max(s.get("shares") or 0, s.get("saves") or 0) >= a["share_save_viral"]:
            r = copy.deepcopy(cfg)
            r["remix"]["variants_per_winner"] = max(1, len(pages_by) - 1)          # every other page
            sc_like = {"post_id": pid, "page_id": c.get("page_id"), "platform": c.get("platform"),
                       "score": c.get("composite"), "class": post.get("class") or "PROMISING"}
            jobs = remix_jobs_for(sc_like, post, pages_by, r, now, recent)
            for j in jobs:
                j["rule"] = "share/save >= 90: remix to all pages"
            out["remix_jobs"] += jobs
            recent += jobs
            if post.get("class") == "WINNER":
                bc = boost_candidate_for({**sc_like, "class": "WINNER", "views": c.get("denominator_value")}, post, cfg,
                                         now, (ad_texts or {}).get(pid), judge_fn)
            else:   # the governor only funds WINNERs: hold the candidate until the velocity class gets there
                bc = {"kind": "boost", "status": "watch_until_winner", "post_id": pid, "page_id": c.get("page_id"),
                      "platform": c.get("platform"), "class": post.get("class"), "created_at": now.isoformat()}
            if bc:
                bc["rule"] = "share/save >= 90"
                out["boost_candidates"].append(bc)
        if (s.get("non_follower") or 0) >= a["non_follower_strong"]:
            out["topic_boosts"].append({**base, "kind": "topic_boost", "pillar": post.get("pillar"),
                                        "multiplier": float(a["topic_slot_multiplier"]),
                                        "rule": f"non-follower {s['non_follower']:.0f} >= {a['non_follower_strong']}"})
    for c in sorted((c for c in cards if int(c.get("horizon_h") or 0) == 24 and not c.get("provisional")
                     and c.get("composite") is not None), key=lambda c: str(c.get("post_id"))):
        for g in genes_of(c):
            hist.setdefault(g, []).append(float(c["composite"]))
            tail = hist[g][-int(a["gene_bench_strikes"]):]
            if len(tail) == int(a["gene_bench_strikes"]) and all(v < a["gene_bench_below"] for v in tail) and g not in bench:
                until = (now + timedelta(days=int(a["bench_days"]))).isoformat()
                bench[g] = until
                out["bench"].append({"gene": g, "until": until, "rule": f"composite < {a['gene_bench_below']} "
                                                                        f"{a['gene_bench_strikes']}x in a row"})
    out["gene_history"] = hist
    out["benched"] = bench
    out["counts"] = {k: len(v) for k, v in out.items() if isinstance(v, list)}
    return out


# ---------------------------------------------------------------- MRR-weighted iteration (scorecard.value_score)
MRR_DEFAULTS = {"go_hard_money": 80.0, "go_hard_min_views": 5000, "go_hard_hooks": 5, "go_hard_trial_reels": 5,
                "reach_virality": 80.0, "reach_money_max": 40.0, "cta_swap_arms": ("FAMILY", "PLAN", "STRONG"),
                "spend_gate_mrr_usd": 30000, "readout_top": 10}


def _mcfg(cfg: dict) -> dict:
    m = dict(MRR_DEFAULTS)
    m.update(((cfg.get("value") or {}).get("actions") or {}))
    gov = cfg.get("governor") or {}
    for k in ("spend_gate_mrr_usd", "paid_media_min_mrr_usd"):
        if gov.get(k) is not None:
            m["spend_gate_mrr_usd"] = float(gov[k])
    return m


def mrr_plan(values: list[dict], posts: list[dict], pages: list[dict], cfg: dict | None = None, *,
             now: datetime | None = None, recent_remixes: list[dict] | None = None, current_mrr_usd: float = 0.0) -> dict:
    """values: scorecard.value_score rows. Queued jobs only (nothing publishes, sends or spends):
      money >= go_hard_money (and views >= go_hard_min_views) -> GO-HARD bundle:
          remake with 5 hooks on every other page, the Facebook long cut, 5 Trial Reels, an email feature (human
          sends), the DM pinned link, and a boost candidate HELD until the spend gate (MRR >= $30K, governor +
          human approval still required after that)
      virality >= reach_virality and money < reach_money_max -> reach remix + CTA-swap experiment (close block A/B)"""
    cfg = cfg or G.load()
    m = _mcfg(cfg)
    now = now or datetime.now(timezone.utc)
    posts_by = {str(p["post_id"]): p for p in posts}
    pages_by = _page_by_id(pages)
    recent = list(recent_remixes or [])
    out = {"go_hard": [], "remix_jobs": [], "fb_long_cuts": [], "trial_reels": [], "email_features": [],
           "dm_pins": [], "boost_candidates": [], "cta_experiments": []}
    for v in sorted(values, key=lambda x: (-(x.get("value") or 0), str(x.get("post_id")))):
        pid = str(v["post_id"])
        post = posts_by.get(pid, {"post_id": pid})
        base = {"source_post_id": pid, "page_id": v.get("page_id"), "platform": v.get("platform"), "status": "queued",
                "created_at": now.isoformat()}
        sc_like = {"post_id": pid, "page_id": v.get("page_id"), "platform": v.get("platform"), "score": v.get("value"),
                   "class": post.get("class") or "PROMISING"}
        if (v.get("money") or 0) >= m["go_hard_money"] and (v.get("views") or 0) >= m["go_hard_min_views"]:
            r = copy.deepcopy(cfg)
            r["remix"]["variants_per_winner"] = max(1, len(pages_by) - 1)
            jobs = remix_jobs_for(sc_like, post, pages_by, r, now, recent)
            for j in jobs:
                j.update(rule="GO-HARD", n_hooks=int(m["go_hard_hooks"]), source_platform=v.get("platform"))
                j["requirements"]["n_hooks"] = int(m["go_hard_hooks"])
            recent += jobs
            out["remix_jobs"] += jobs
            fb = {**base, "kind": "fb_long_cut", "builder": "growth.variants.fb_long_cut", "rule": "GO-HARD"}
            tr = {**base, "kind": "trial_reels", "count": int(m["go_hard_trial_reels"]), "variant_role": "TEST",
                  "surface": "ig_trial", "budget_check": "growth.variants.trial_budget", "rule": "GO-HARD"}
            em = {**base, "kind": "email_feature", "status": "draft", "audience": "members + waitlist (consented)",
                  "requires": ["human_send", "compliance_pass"], "rule": "GO-HARD"}
            dm = {**base, "kind": "dm_pinned_link", "status": "suggested", "keyword": post.get("cta_keyword"),
                  "action": "pin the post's keyword link in the DM flow + pinned first comment", "rule": "GO-HARD"}
            gate = float(m["spend_gate_mrr_usd"])
            bc = {**base, "kind": "boost", "status": "held_until_spend_gate", "gate_mrr_usd": gate,
                  "gate_open": float(current_mrr_usd or 0) >= gate,
                  "requires": ["spend_gate", "WINNER", "human_approval", "governor_plan", "SPEND_ENABLED"],
                  "rule": "GO-HARD"}
            out["fb_long_cuts"].append(fb)
            out["trial_reels"].append(tr)
            out["email_features"].append(em)
            out["dm_pins"].append(dm)
            out["boost_candidates"].append(bc)
            out["go_hard"].append({"post_id": pid, "value": v.get("value"), "money": v.get("money"),
                                   "mrr_usd": v.get("mrr_usd"), "remakes": len(jobs)})
        elif (v.get("virality") or 0) >= m["reach_virality"] and (v.get("money") or 0) < m["reach_money_max"]:
            r = copy.deepcopy(cfg)
            jobs = remix_jobs_for(sc_like, post, pages_by, r, now, recent)
            for j in jobs:
                j["rule"] = "reach remix: high virality, low MRR"
            recent += jobs
            out["remix_jobs"] += jobs
            cur = post.get("cta_keyword") or post.get("close_family") or "close"
            arms = [cur] + [a for a in m["cta_swap_arms"] if a != cur][:2]
            out["cta_experiments"].append({**base, "kind": "cta_swap_experiment", "dimension": "close",
                                           "arms": arms, "variant_role": "TEST", "keep_hook_and_body": True,
                                           "metric": "mrr_per_1k", "rule": "high virality, low MRR"})
    out["counts"] = {k: len(x) for k, x in out.items() if isinstance(x, list)}
    return out


def weekly_readout(values: list[dict], cfg: dict | None = None, n: int | None = None) -> dict:
    """Top posts of the week by attributed MRR, by views, and by both (the blended value score)."""
    n = int(n or _mcfg(cfg or G.load())["readout_top"])
    keep = ("post_id", "page_id", "platform", "value", "virality", "money", "views", "mrr_usd", "buyers", "mrr_per_1k")

    def top(key):
        return [{k: v.get(k) for k in keep} for v in sorted(values, key=lambda v: (-(v.get(key) or 0), str(v.get("post_id"))))[:n]]
    return {"by_mrr": top("mrr_usd"), "by_views": top("views"), "by_both": top("value")}
