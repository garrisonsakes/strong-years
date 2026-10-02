"""Modular variants and Trial Reels (ENGINE_100X §2.1, §5.1-5.4; Meta originality rules [S3][S20]; IG trial_params [S18]).

A master decomposes into three blocks: hook (frame 1 to the re-hook), body, close (the last line). Variants recombine
those blocks, and every variant carries a `variant_role`:

  TEST       an Instagram Trial Reel (surface "ig_trial": shown to non-followers first). At most ONE Trial Reel per
             (page, body) carries trial_params.graduation_strategy = SS_PERFORMANCE (the platform may auto-graduate
             it); the rest are MANUAL, so the platform can never put the same body into the follower feed twice.
  PLACEMENT  the one post of a master per page x platform (feed surfaces). Facebook gets its own caption and close.
  REMIX      a fresh render: new body id in the same body family, >= 3 cheap dimensions changed incl. a new voice take.

Rules enforced in code (here, in uniqueness.guard.check_variant and in tools/posting_rules.py):
  * every variant differs from the master default AND from each sibling variant in >= 2 of DIMENSIONS, and a TEST
    changes the opening (hook audio or first frame): a caption or length change alone is a low-value edit [S3]
  * the same body never posts twice to one page x surface within 30 days; Trial Reels are the bounded exception
    (<= max_trials_per_body per page on the ig_trial surface) and the follower feed still sees the body once
  * Trial Reels per page per day ramp 3 (weeks 1-2), 6 (week 3), then the configured cap (default 12, max 20), and
    every IG publish (feed + trial) stops at ig_publish_hard_stop, below the 100/24 h API limit
  * the uniqueness worker gates every variant (gate())
Graduation (graduate()): per body, the Trial Reel whose 6 h composite beats the page baseline becomes the main-feed
post. The scheduled IG placement then publishes that hook, or is skipped when the platform already auto-graduated
the SS_PERFORMANCE trial. The feed ledger never takes the same body twice.

Pure functions. No network, no rendering, no spend.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from growth import config as G

ROLES = ("TEST", "PLACEMENT", "REMIX")
DIMENSIONS = ("hook_audio", "first_frame", "on_screen_text", "caption", "length")
OPENING_DIMS = {"hook_audio", "first_frame"}
CAPTION_STYLES = ("standard", "question_first", "number_first", "story_first")
FEED_SURFACES = ("instagram", "facebook", "tiktok", "youtube", "threads", "x")
TRIAL_SURFACE = "ig_trial"
SIBLING = {"CHANG": "SUN", "SUN": "CHANG", "DUO": "CHANG"}
# platform-native close lines matched to each platform's strongest share action (ENGINE_100X §4.6, §1.1)
CLOSE_BY_PLATFORM = {"facebook": "Send this to your family group.", "instagram": "Send this to someone who needs it.",
                     "tiktok": "Send this to someone who needs it.", "youtube": "Save this for tonight.",
                     "threads": "Copy the link for someone you love.", "x": "Copy the link for someone you love."}
CAPTION_BY_PLATFORM = {"facebook": "fb_native_long", "instagram": "standard", "tiktok": "standard",
                       "youtube": "question_first", "threads": "story_first", "x": "number_first"}
# what each operator changes (ENGINE_100X §5: new hook, new first frame, new on-screen text, caption style,
# length cut 15/30/45 s, character-swap voice-over, reaction overlay)
OPS = {"new_hook": {"hook_audio", "first_frame", "on_screen_text"}, "new_first_frame": {"first_frame"},
       "new_on_screen_text": {"on_screen_text"}, "caption_style": {"caption"}, "length_cut": {"length"},
       "character_swap_vo": {"hook_audio"}, "reaction_overlay": {"first_frame"}}
# ordered recipes; each changes >= 2 dimensions including an opening dimension
RECIPES = (
    ("new_hook", "caption_style"),
    ("new_first_frame", "new_on_screen_text", "length_cut"),
    ("reaction_overlay", "caption_style", "length_cut"),
    ("character_swap_vo", "new_on_screen_text", "length_cut"),
    ("new_hook", "length_cut"),
    ("new_first_frame", "caption_style", "character_swap_vo"),
    ("reaction_overlay", "new_on_screen_text"),
    ("new_hook", "new_first_frame", "caption_style"),
)


def _h(*parts) -> str:
    return hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:10]


def _vcfg(cfg: dict | None) -> dict:
    return (cfg or G.load())["variants"]


# ---------------------------------------------------------------- blocks
def _span(t: str | None) -> tuple[float, float] | None:
    try:
        a, b = str(t).split("-")
        return float(a), float(b)
    except (ValueError, AttributeError):
        return None


def decompose(master: dict) -> dict:
    """master -> {"hook", "body", "close"} blocks with stable ids and families.
    Uses the script's beats ({"t": "0-3", "vo", "ost"}) when present: first beat = hook, last beat = close, the rest
    = body. Otherwise hook = [0, hook_s] (3 s) and close = the last close_s (4 s) of duration_s."""
    mid = str(master.get("master_id") or master.get("id") or "M")
    dur = float(master.get("duration_s") or master.get("seconds") or 42)
    beats = master.get("beats") or []
    if len(beats) >= 3 and all(_span(b.get("t")) for b in beats):
        h, c, body = beats[0], beats[-1], beats[1:-1]
        hs, cs = _span(h["t"]), _span(c["t"])
        hook = {"text": h.get("vo") or "", "on_screen": h.get("ost") or "", "start_s": hs[0], "end_s": hs[1]}
        close = {"text": c.get("vo") or "", "start_s": cs[0], "end_s": cs[1]}
        btxt = " ".join(b.get("vo") or "" for b in body)
        bodyb = {"text": btxt, "start_s": hs[1], "end_s": cs[0]}
        dur = max(dur, cs[1])
    else:
        hs, cs = float(master.get("hook_s") or 3.0), float(master.get("close_s") or 4.0)
        hook = {"text": master.get("hook_text") or master.get("hook") or "", "on_screen": master.get("hook_ost") or "",
                "start_s": 0.0, "end_s": hs}
        close = {"text": master.get("close_text") or "", "start_s": max(hs, dur - cs), "end_s": dur}
        bodyb = {"text": master.get("body_text") or "", "start_s": hs, "end_s": max(hs, dur - cs)}
    hook.update(id=master.get("hook_id") or f"H-{_h(mid, 'hook', hook['text'])}", family=master.get("hook_grammar") or "CUR")
    bodyb.update(id=master.get("body_id") or f"B-{_h(mid, 'body', bodyb['text'])}",
                 family=f"{master.get('pillar') or 'P?'}:{master.get('format') or 'F?'}")
    close.update(id=master.get("close_id") or f"C-{_h(mid, 'close', close['text'])}",
                 family=master.get("cta_keyword") or "close")
    return {"master_id": mid, "duration_s": dur, "hook": hook, "body": bodyb, "close": close}


def default_signature(blocks: dict) -> dict:
    return {"hook_audio": blocks["hook"]["id"], "first_frame": "F0", "on_screen_text": blocks["hook"].get("on_screen") or
            blocks["hook"]["text"], "caption": "standard", "length": int(round(blocks["duration_s"]))}


def dims_changed(a: dict, b: dict) -> set[str]:
    return {d for d in DIMENSIONS if a.get(d) != b.get(d)}


# ---------------------------------------------------------------- generator
def _apply(op: str, sig: dict, k: int, blocks: dict, hook_pool: list[dict], used_hooks: set, character: str,
           cuts: list[int]) -> tuple[dict, str | None] | None:
    s = dict(sig)
    new_hook = None
    if op == "new_hook":
        alt = next((h for h in hook_pool if h.get("id") not in used_hooks and h.get("id") != blocks["hook"]["id"]), None)
        if alt is None:
            return None
        new_hook = alt["id"]
        s.update(hook_audio=alt["id"], first_frame=f"F-{alt['id']}", on_screen_text=alt.get("on_screen") or alt.get("text"))
    elif op == "new_first_frame":
        s["first_frame"] = f"F{k + 1}"
    elif op == "new_on_screen_text":
        s["on_screen_text"] = f"OST-REWRITE-{k + 1}"      # slot: the writer rewrites the hook line (same claim)
    elif op == "caption_style":
        s["caption"] = CAPTION_STYLES[1 + k % (len(CAPTION_STYLES) - 1)]
    elif op == "length_cut":
        fit = [c for c in cuts if c < blocks["duration_s"] - 1 and c != sig["length"]]
        if not fit:
            return None
        s["length"] = fit[k % len(fit)]
    elif op == "character_swap_vo":
        s["hook_audio"] = f"VO-{SIBLING.get(character, 'SUN')}-{blocks['hook']['id']}"
    elif op == "reaction_overlay":
        s["first_frame"] = f"RX-{SIBLING.get(character, 'SUN')}-{k + 1}"
    return s, new_hook


def generate(master: dict, n: int, *, role: str = "TEST", page: str | None = None, hook_pool: list[dict] | None = None,
             existing: list[dict] | None = None, cfg: dict | None = None) -> list[dict]:
    """Up to n TEST variants of one master. Each differs from the master default and from every sibling (existing +
    new) in >= min_dims_changed dimensions, and changes the opening. Deterministic."""
    if role not in ("TEST",):
        raise ValueError("generate() makes TEST variants; use placement() / remix() for the other roles")
    vc = _vcfg(cfg)
    blocks = decompose(master)
    base = default_signature(blocks)
    page = page or master.get("page")
    pool = list(hook_pool or master.get("hook_pool") or [])
    used_hooks = {v.get("hook_id") for v in existing or []}
    sibs = [v["signature"] for v in existing or []] + [base]
    out: list[dict] = []
    k = 0
    for recipe in RECIPES * 2:
        if len(out) >= n:
            break
        sig, hook_id, ok = dict(base), blocks["hook"]["id"], True
        for op in recipe:
            r = _apply(op, sig, k, blocks, pool, used_hooks, master.get("character") or "CHANG", list(vc["length_cuts_s"]))
            if r is None:
                ok = False
                break
            sig, nh = r
            hook_id = nh or hook_id
        k += 1
        if not ok:
            continue
        ch = dims_changed(sig, base)
        if len(ch) < int(vc["min_dims_changed"]) or not (ch & OPENING_DIMS):
            continue
        if any(len(dims_changed(sig, s)) < int(vc["min_dims_changed"]) for s in sibs):
            continue
        used_hooks.add(hook_id)
        sibs.append(sig)
        cost = round(sum(float(vc["op_cost_usd"].get(op, 0.0)) for op in recipe), 2)
        out.append({"variant_id": f"V-{blocks['master_id']}-T{len(existing or []) + len(out) + 1}", "variant_role": "TEST",
                    "master_id": blocks["master_id"], "page": page, "surface": TRIAL_SURFACE, "platform": "instagram",
                    "body_id": blocks["body"]["id"], "hook_id": hook_id, "close_id": blocks["close"]["id"],
                    "hook_family": blocks["hook"]["family"], "body_family": blocks["body"]["family"],
                    "close_family": blocks["close"]["family"], "ops": list(recipe), "signature": sig,
                    "dims_changed": sorted(ch), "length_s": sig["length"], "cost_usd": cost})
    return out


def placement(master: dict, platform: str, *, page: str | None = None, cfg: dict | None = None) -> dict:
    """The PLACEMENT of a master on one platform: same blocks, platform-native caption style and close line.
    Facebook is always a native upload with its own caption and close (never the IG share-to-Facebook toggle)."""
    blocks = decompose(master)
    sig = default_signature(blocks)
    sig["caption"] = CAPTION_BY_PLATFORM.get(platform, "standard")
    out = {"variant_id": f"V-{blocks['master_id']}-P-{platform}", "variant_role": "PLACEMENT", "master_id": blocks["master_id"],
           "page": page or master.get("page"), "surface": platform, "platform": platform, "body_id": blocks["body"]["id"],
           "hook_id": blocks["hook"]["id"], "close_id": f"{blocks['close']['id']}-{platform}",
           "close_line": CLOSE_BY_PLATFORM.get(platform, ""), "hook_family": blocks["hook"]["family"],
           "body_family": blocks["body"]["family"], "close_family": blocks["close"]["family"], "ops": [],
           "signature": sig, "dims_changed": [], "length_s": sig["length"], "cost_usd": 0.0}
    if platform == "facebook":
        out.update(upload="native_fb_video_reels", share_to_facebook_from_ig=False, caption_source="fb_native")
    if platform == "instagram":
        out.update(share_to_facebook=False)
    return out


def fb_long_cut(master: dict, *, page: str | None = None, cfg: dict | None = None) -> dict:
    """Facebook-only 60-180 s follow-along cut from the same hook/body/close blocks (ENGINE_100X §1.3). It IS the
    master's Facebook placement (one body per page x surface), not a second Facebook post of the same body."""
    vc = _vcfg(cfg)
    lo, hi = vc["fb_long_s"]
    p = placement(master, "facebook", page=page, cfg=cfg)
    blocks = decompose(master)
    length = int(min(hi, max(lo, 2 * blocks["duration_s"] + 10)))
    p.update(variant_id=f"V-{blocks['master_id']}-P-facebook-long", variant="fb_long", length_s=length,
             ops=["fb_long"], cost_usd=float(vc["op_cost_usd"]["fb_long"]),
             recipe="hook + body + follow-along reps (B-roll, no new avatar seconds) + FB close")
    p["signature"] = {**p["signature"], "length": length}
    return p


def remix(master: dict, k: int, *, page: str | None = None, hook_pool: list[dict] | None = None,
          cfg: dict | None = None) -> dict:
    """REMIX: fresh render of the body family with a new set, a new voice take, a new hook and another length bucket.
    New body id (same family); >= remix_min_dims dimensions changed."""
    vc = _vcfg(cfg)
    blocks = decompose(master)
    base = default_signature(blocks)
    pool = [h for h in (hook_pool or master.get("hook_pool") or []) if h.get("id") != blocks["hook"]["id"]]
    alt = pool[k % len(pool)] if pool else None
    cuts = [c for c in vc["length_cuts_s"] if c != base["length"]] or [base["length"]]
    sig = {**base, "first_frame": f"SET{k + 1}", "hook_audio": f"RETAKE{k + 1}-{alt['id'] if alt else blocks['hook']['id']}",
           "on_screen_text": (alt.get("on_screen") or alt.get("text")) if alt else f"OST-REMIX-{k + 1}",
           "length": cuts[k % len(cuts)]}
    ch = dims_changed(sig, base)
    if len(ch) < int(vc["remix_min_dims"]):
        raise ValueError("remix changes fewer than remix_min_dims dimensions")
    return {"variant_id": f"V-{blocks['master_id']}-R{k + 1}", "variant_role": "REMIX", "master_id": blocks["master_id"],
            "page": page or master.get("page"), "surface": None, "body_id": f"{blocks['body']['id']}-R{k + 1}",
            "hook_id": alt["id"] if alt else blocks["hook"]["id"], "close_id": blocks["close"]["id"],
            "hook_family": blocks["hook"]["family"], "body_family": blocks["body"]["family"],
            "close_family": blocks["close"]["family"], "ops": ["new_set", "new_voice_take", "new_hook", "length_cut"],
            "signature": sig, "dims_changed": sorted(ch), "length_s": sig["length"], "fresh_render": True,
            "cost_usd": float(vc["op_cost_usd"]["new_hook"])}


# ---------------------------------------------------------------- Trial Reel caps and graduation strategy
def trial_cap(page_age_days: int, cfg: dict | None = None) -> int:
    vc = _vcfg(cfg)
    if page_age_days < 0:
        return 0
    for until, n in vc["trial_ramp"]:
        if page_age_days < int(until):
            return min(int(n), int(vc["trial_reels_per_page_day"]))
    return min(int(vc["trial_reels_per_page_day"]), int(vc["trial_reels_max"]), 20)


def trial_budget(page_age_days: int, trials_today: int, ig_published_24h: int, cfg: dict | None = None) -> int:
    """How many more Trial Reels this page may publish now: the ramped cap, and never past the hard stop."""
    vc = _vcfg(cfg)
    return max(0, min(trial_cap(page_age_days, cfg) - int(trials_today), int(vc["ig_publish_hard_stop"]) - int(ig_published_24h)))


def assign_trial_params(trials: list[dict], auto_taken: set[tuple] | None = None) -> list[dict]:
    """At most one SS_PERFORMANCE Trial Reel per (page, body); every other one is MANUAL. `auto_taken` holds the
    (page, body) pairs that already have one (e.g. a first-14-days IG placement posted as a Trial Reel)."""
    taken = set(auto_taken or ())
    for t in trials:
        key = (t.get("page"), t.get("body_id"))
        strat = "MANUAL" if key in taken else "SS_PERFORMANCE"
        taken.add(key)
        t["trial_params"] = {"graduation_strategy": strat}
    return trials


def _dt(x) -> datetime | None:
    if not x:
        return None
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    d = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def body_rule_violations(candidates: list[dict], ledger: list[dict], cfg: dict | None = None,
                         now: datetime | None = None) -> list[str]:
    """Same body twice on one page x feed surface within body_repeat_days, or more than max_trials_per_body Trial
    Reels of one body on one page. `ledger` = posts already published or scheduled ({page, surface, body_id, at})."""
    vc = _vcfg(cfg)
    now = now or datetime.now(timezone.utc)
    win = timedelta(days=int(vc["body_repeat_days"]))
    seen: dict[tuple, int] = {}
    for e in ledger:
        at = _dt(e.get("at") or e.get("published_at") or e.get("scheduled_at"))
        if at is None or abs(now - at) <= win:
            k = (e.get("page"), e.get("surface"), e.get("body_id"))
            seen[k] = seen.get(k, 0) + 1
    out = []
    for c in candidates:
        k = (c.get("page"), c.get("surface"), c.get("body_id"))
        if c.get("surface") == TRIAL_SURFACE:
            if seen.get(k, 0) >= int(vc["max_trials_per_body"]):
                out.append(f"{c.get('variant_id')}: {seen[k]} Trial Reels of body {c.get('body_id')} on {c.get('page')} "
                           f"already (max {vc['max_trials_per_body']})")
        elif seen.get(k, 0) >= 1:
            out.append(f"{c.get('variant_id')}: body {c.get('body_id')} already on {c.get('page')} x {c.get('surface')} "
                       f"within {vc['body_repeat_days']} d")
        seen[k] = seen.get(k, 0) + 1
    return out


# ---------------------------------------------------------------- graduation
def graduate(trials: list[dict], page_baseline: float, feed_ledger: list[dict], cfg: dict | None = None) -> list[dict]:
    """Per (page, body): decide what the IG main feed gets. trials: [{variant_id, page, body_id, composite_6h,
    auto_graduated?, trial_params}]; page_baseline = the page's 6 h composite baseline (50 on the scorecard scale).
      skip_placement   the platform auto-graduated the SS_PERFORMANCE trial: it IS the feed post; skip the placement
      graduate         best manual trial beats the baseline: the placement publishes that variant's hook
      keep_master      no trial beat the baseline: the placement publishes the master's own hook
      already_in_feed  the body is already in the main feed: nothing graduates (the feed never gets a body twice)"""
    in_feed = {(e.get("page"), e.get("body_id")) for e in feed_ledger if e.get("surface") in ("instagram", "ig_feed")}
    by_body: dict[tuple, list[dict]] = {}
    for t in trials:
        by_body.setdefault((t.get("page"), t.get("body_id")), []).append(t)
    out = []
    for key, ts in sorted(by_body.items(), key=lambda kv: str(kv[0])):
        base = {"page": key[0], "body_id": key[1]}
        if key in in_feed:
            out.append({**base, "action": "already_in_feed", "variant_id": None})
            continue
        auto = [t for t in ts if t.get("auto_graduated")]
        if auto:
            out.append({**base, "action": "skip_placement", "variant_id": auto[0]["variant_id"],
                        "reason": "platform auto-graduated the SS_PERFORMANCE Trial Reel"})
            in_feed.add(key)
            continue
        scored = [t for t in ts if t.get("composite_6h") is not None]
        best = max(scored, key=lambda t: float(t["composite_6h"]), default=None)
        if best is not None and float(best["composite_6h"]) > float(page_baseline):
            out.append({**base, "action": "graduate", "variant_id": best["variant_id"],
                        "reason": f"6 h composite {float(best['composite_6h']):.1f} > page baseline {float(page_baseline):.1f}"})
        else:
            out.append({**base, "action": "keep_master", "variant_id": None,
                        "reason": "no Trial Reel beat the page baseline at 6 h"})
        in_feed.add(key)
    return out


# ---------------------------------------------------------------- uniqueness gate
def gate(variants: list[dict], live: list[dict], thresholds: dict | None = None,
         now: datetime | None = None) -> tuple[list[dict], list[dict]]:
    """Every variant goes through uniqueness.guard.check_variant against the live variants (and the ones accepted
    before it in this batch). Returns (accepted, rejected-with-reasons)."""
    from uniqueness import guard
    acc, rej, pool = [], [], list(live)
    for v in variants:
        r = guard.check_variant(v, pool, thresholds, now)
        if r["allow"]:
            acc.append(v)
            pool.append(v)
        else:
            rej.append({**v, "uniqueness": r})
    return acc, rej
