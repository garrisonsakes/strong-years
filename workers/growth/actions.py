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
