"""Content allocator: Thompson sampling over pillar x hook grammar x editorial format x speaker x length bucket,
per page and platform, producing tomorrow's slot plan for the script generator.

Arms (growth/catalog): only pillar -> format pairs from CONTENT_SYSTEM §1, speakers the page runs, DUO for the
duo-only formats, no LAUNCH grammar, no platform-restricted formats off their platforms.

Posterior per arm: Beta(alpha, beta) with alpha = 1 + decayed successes + prior, beta = 1 + decayed failures + prior, where each
observation contributes reward r in [0, 1] (growth/scoring.reward, or a LOSER downweight) with weight
0.5 ** (age_days / half_life_days). An arm with no observations borrows up to hier_prior_max pseudo-observations from
its factor marginals (pillar, grammar, format, speaker, length means), so a new combination of proven parts starts
warm and a new combination of losing parts starts cold.

Slot plan for a day: n = min(cadence_target, max_cadence) slots.
  * exploit slots (1 - explore_floor): draw theta ~ Beta for every eligible arm, take the best not-yet-used arms
    subject to the constraints below
  * explore slots (>= explore_floor, hard floor 20%): the least-observed eligible arms (ties broken by a seeded RNG)
Constraints: max_per_pillar_per_day; no consecutive slots with the same grammar; the (pillar, grammar, format)
triple is not repeated on the page within the uniqueness_days window (recent plan input); running bits assigned
(>= 1 per DUO video, >= 1 per solo_bit_every solo videos) with a cooldown; slot hours from the page profile.
Deterministic for a given seed.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

from growth import catalog as CAT
from growth import config as G

LENGTHS = ("S", "M", "L")


def arm_key(a: dict) -> str:
    return "|".join(f"{k}={a[k]}" for k in ("pillar", "grammar", "format", "speaker", "length"))


def parse_arm_key(key: str) -> dict:
    return dict(kv.split("=", 1) for kv in key.split("|"))


def eligible_arms(page: dict, platform: str, cfg: dict) -> list[dict]:
    a = cfg["allocator"]
    dna = page.get("page_dna") or {}
    pillars = [p for p in (dna.get("pillars") or CAT.PILLARS) if p in CAT.PILLAR_FORMATS]
    speakers = tuple(dna.get("speakers") or CAT.PAGE_SPEAKERS.get(page.get("slug"), CAT.SPEAKERS))
    grammars = [g for g in (dna.get("grammars") or CAT.GRAMMARS) if g in CAT.GRAMMARS and g not in CAT.EXCLUDED_GRAMMARS]
    only = a["platform_formats_only"]
    out = []
    for p in pillars:
        for f in CAT.PILLAR_FORMATS[p]:
            if f in only and platform not in only[f]:
                continue
            spk_opts = ("DUO",) if f in CAT.DUO_ONLY_FORMATS else speakers
            if f in CAT.DUO_ONLY_FORMATS and "DUO" not in speakers and len(speakers) < 2 and "DUO" not in CAT.SPEAKERS:
                continue
            for s in spk_opts:
                for g in grammars:
                    for ln in LENGTHS:
                        if f in a["render_format"]["text_formats"] and ln != "S":
                            continue
                        out.append({"pillar": p, "grammar": g, "format": f, "speaker": s, "length": ln})
    return out


def decay_weight(age_days: float, half_life: float) -> float:
    return 0.5 ** (max(0.0, age_days) / max(0.01, half_life))


def posterior(observations: list[dict], arms: list[dict], cfg: dict, now: datetime) -> dict[str, dict]:
    """observations: [{"arm_key" | arm fields, "reward": 0..1, "at": iso, "weight": optional}]"""
    a = cfg["allocator"]
    hl = float(a["half_life_days"])
    stats: dict[str, list[float]] = {}
    for o in observations or []:
        key = o.get("arm_key") or (arm_key(o["arm"]) if o.get("arm") else None)
        r = G.num(o.get("reward"), lo=0, hi=1)
        if not key or r is None:
            continue
        at = o.get("at")
        try:
            t = datetime.fromisoformat(str(at).replace("Z", "+00:00")) if at else now
            t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        except ValueError:
            t = now
        w = decay_weight((now - t).total_seconds() / 86400.0, hl) * float(G.num(o.get("weight"), lo=0, hi=10) or 1.0)
        s = stats.setdefault(key, [0.0, 0.0])
        s[0] += w * r
        s[1] += w * (1.0 - r)
    # Hierarchical prior. Every arm carries k0 neutral pseudo-observations centred on the neutral mean (0.5), plus
    # up to `cap` pseudo-observations borrowed from its five factor marginals (pillar, grammar, format, speaker,
    # length), each marginal shrunk toward the global mean by k0 and weighted by its own evidence. A factor nobody has
    # observed pulls toward neutral instead of contributing nothing, so an arm that shares one factor with a winner
    # starts slightly warm and an arm that shares four starts clearly warm. With ~1,000 arms per page x platform this is
    # what keeps a lucky draw from an unseen arm from crowding out proven ones.
    facs = ("pillar", "grammar", "format", "speaker", "length")
    marg: dict[str, dict[str, list[float]]] = {k: {} for k in facs}
    for key, (succ, fail) in stats.items():
        for fac, val in parse_arm_key(key).items():
            m = marg[fac].setdefault(val, [0.0, 0.0])
            m[0] += succ
            m[1] += fail
    k0 = float(a.get("prior_strength", 20))
    cap = float(a["hier_prior_max"])
    # The neutral centre is fixed (config prior_mean, 0.5): growth/scoring.reward is defined against the page baseline,
    # so a baseline post earns ~0.5 by construction. A data-driven global mean would let one all-wins arm warm every
    # other arm on the page.
    global_mean = float(a.get("prior_mean", 0.5))
    out = {}
    for arm in arms:
        key = arm_key(arm)
        succ, fail = stats.get(key, [0.0, 0.0])
        n_direct = succ + fail
        num, den, evidence, n_fac = 0.0, 0.0, 0.0, 0
        for fac in facs:
            m = marg[fac].get(arm[fac], [0.0, 0.0])
            n_f = m[0] + m[1]
            r_f = (m[0] + global_mean * k0) / (n_f + k0)          # shrunk marginal rate
            w_f = min(cap, n_f)
            num += r_f * w_f + global_mean                         # one neutral vote per factor
            den += w_f + 1.0
            evidence += w_f
            n_fac += 1 if n_f >= 1.0 else 0
        prior_mean = num / den
        borrowed = min(cap, evidence / len(facs))
        pseudo = k0 + borrowed
        ps, pf = prior_mean * pseudo, (1.0 - prior_mean) * pseudo
        out[key] = {"alpha": 1.0 + succ + ps, "beta": 1.0 + fail + pf, "n": round(n_direct, 3), "prior_n": round(ps + pf, 3),
                    "prior_mean": round(prior_mean, 4), "evidence": round(n_direct + borrowed, 3), "factors_seen": n_fac,
                    "mean": (1.0 + succ + ps) / (2.0 + succ + fail + ps + pf)}
    return out


def hook_family_posterior(observations: list[dict], cfg: dict, now: datetime) -> dict[str, dict]:
    """Hook-family arm (VIRALITY_SYSTEM.md §4): one Beta per hook grammar pooled across every pillar/format/speaker/length,
    so a hook family that wins anywhere on the page is pulled forward everywhere within a day or two. Proven families
    (POSTDB §3/§8 rule 3) start slightly warm; everything else starts neutral."""
    a = cfg["allocator"]
    hl, k0 = float(a["half_life_days"]), float(a.get("hook_family_prior_strength", 10.0))
    neutral, bonus = float(a.get("prior_mean", 0.5)), float(a.get("hook_family_proven_bonus", 0.05))
    stats: dict[str, list[float]] = {g: [0.0, 0.0] for g in CAT.GRAMMARS}
    for o in observations or []:
        key = o.get("arm_key") or (arm_key(o["arm"]) if o.get("arm") else None)
        r = G.num(o.get("reward"), lo=0, hi=1)
        if not key or r is None:
            continue
        g = parse_arm_key(key).get("grammar")
        try:
            t = datetime.fromisoformat(str(o.get("at")).replace("Z", "+00:00")) if o.get("at") else now
            t = t if t.tzinfo else t.replace(tzinfo=timezone.utc)
        except ValueError:
            t = now
        w = decay_weight((now - t).total_seconds() / 86400.0, hl) * float(G.num(o.get("weight"), lo=0, hi=10) or 1.0)
        st = stats.setdefault(g, [0.0, 0.0])
        st[0] += w * r
        st[1] += w * (1.0 - r)
    out = {}
    for g, (succ, fail) in stats.items():
        m0 = neutral + (bonus if g in CAT.PROVEN_GRAMMARS else 0.0)
        al, be = 1.0 + succ + m0 * k0, 1.0 + fail + (1.0 - m0) * k0
        out[g] = {"alpha": al, "beta": be, "n": round(succ + fail, 3), "mean": round(al / (al + be), 4)}
    return out


def _bit_for(slot_i: int, speaker: str, used: list[str], cfg: dict, rng: random.Random, solo_count: int) -> str | None:
    a = cfg["allocator"]
    need = speaker == "DUO" or (solo_count % int(a["solo_bit_every"]) == 0)
    if not need:
        return None
    cool = int(a["bit_cooldown"])
    pool = [b for b in CAT.RUNNING_BITS if b not in used[-cool:]]
    return rng.choice(pool) if pool else None


def _render_format(fmt: str, speaker: str, cfg: dict) -> str:
    rf = cfg["allocator"]["render_format"]
    if fmt in rf["text_formats"]:
        return rf["text"]
    if speaker == "DUO" or fmt in CAT.DUO_ONLY_FORMATS:
        return rf["duo"]
    if fmt in rf["motion"]:
        return "R3_motion_exercise"
    if fmt in rf["prop"]:
        return "R2_prop_demo"
    return "R1_talk_prop"


def plan_day(page: dict, platform: str, date: str, observations: list[dict], cfg: dict | None = None, *,
             cadence: int | None = None, recent: list[dict] | None = None, used_bits: list[str] | None = None,
             seed: int | None = None, now: datetime | None = None) -> dict:
    cfg = cfg or G.load()
    a = cfg["allocator"]
    now = now or datetime.now(timezone.utc)
    rng = random.Random(seed if seed is not None else f"{page.get('id')}|{platform}|{date}")
    arms = eligible_arms(page, platform, cfg)
    if not arms:
        raise ValueError("no eligible arms for this page/platform")
    post = posterior(observations, arms, cfg, now)
    fam = hook_family_posterior(observations, cfg, now)
    fam_theta = {g: rng.betavariate(f["alpha"], f["beta"]) for g, f in sorted(fam.items())}
    fam_w = float(a.get("hook_family_weight", 0.35))
    n = max(1, min(int(a["max_cadence"]), int(cadence or page.get("daily_post_target") or a["max_cadence"])))
    explore_floor = max(G.MIN_EXPLORE_FLOOR, float(a["explore_floor"]))
    n_explore = max(1, int(math.ceil(n * explore_floor))) if n > 1 else (1 if rng.random() < explore_floor else 0)
    n_exploit = n - n_explore
    hours = list((page.get("page_dna") or {}).get("slot_hours") or a["default_slot_hours"])
    hours = sorted(hours)[:n] if len(hours) >= n else sorted(hours) + [(hours[-1] + 1 + i) % 24 for i in range(n - len(hours))]
    recent_triples = {(r.get("pillar"), r.get("grammar"), r.get("format") or r.get("editorial_format")) for r in (recent or [])}
    n_pillars = len({x["pillar"] for x in arms})
    pillar_cap = max(int(a["max_per_pillar_per_day"]), math.ceil(n / max(1, n_pillars)))   # a 2-pillar page can still fill 9 slots
    per_pillar: dict[str, int] = {}
    chosen: list[dict] = []
    used_keys: set[str] = set()
    last_grammar = None

    def ok(arm: dict) -> bool:
        if arm_key(arm) in used_keys:
            return False
        if per_pillar.get(arm["pillar"], 0) >= pillar_cap:
            return False
        if (arm["pillar"], arm["grammar"], arm["format"]) in recent_triples:
            return False
        if last_grammar and arm["grammar"] == last_grammar:
            return False
        return True

    def take(arm: dict, mode: str, theta: float | None):
        nonlocal last_grammar
        used_keys.add(arm_key(arm))
        per_pillar[arm["pillar"]] = per_pillar.get(arm["pillar"], 0) + 1
        last_grammar = arm["grammar"]
        chosen.append({"arm": arm, "mode": mode, "theta": theta, "posterior": post[arm_key(arm)]})

    # exploit: Thompson draws in three tiers: arms with direct observations (>= exploit_min_direct) whose posterior
    # mean is not below neutral, then arms that resemble observed ones in >= exploit_min_factors of the five factors
    # (borrowed evidence, again not below neutral), then the rest. Unseen arms are what the exploration floor is for;
    # with ~1,000 arms per page x platform, letting them compete on lucky draws would make the exploit slots random,
    # and arms with evidence of being below baseline must never outrank an unseen one.
    min_direct = float(a.get("exploit_min_direct", 1.0))
    min_factors = int(a.get("exploit_min_factors", 3))
    # each arm's Thompson draw is blended with its hook family's draw (the hook-family arm)
    draws = [((1 - fam_w) * rng.betavariate(post[arm_key(x)]["alpha"], post[arm_key(x)]["beta"])
              + fam_w * fam_theta.get(x["grammar"], 0.5), i, x) for i, x in enumerate(arms)]
    draws.sort(key=lambda d: (-d[0], d[1]))
    neutral = float(a.get("prior_mean", 0.5))
    tiers = (lambda p: p["n"] >= min_direct and p["mean"] >= neutral,            # proven, not below baseline
             lambda p: p["factors_seen"] >= min_factors and p["mean"] >= neutral,  # resembles proven arms
             lambda p: True)                                                       # everything else (losers last)
    for tier in tiers:
        pool = lambda x, t=tier: t(post[arm_key(x)])
        for theta, _, arm in draws:
            if len(chosen) >= n_exploit:
                break
            if pool(arm) and ok(arm):
                take(arm, "exploit", round(theta, 4))
    # explore: least-observed arms (seeded tie-break); among the unseen, the best hook family (posterior mean) first,
    # which with no data is the proven grammars (warm prior) and afterwards whatever family is winning on the page
    unseen = sorted(arms, key=lambda x: (post[arm_key(x)]["n"], -fam.get(x["grammar"], {"mean": 0.5})["mean"],
                                         0 if x["grammar"] in CAT.PROVEN_GRAMMARS else 1, rng.random()))
    for arm in unseen:
        if len(chosen) >= n:
            break
        if ok(arm):
            take(arm, "explore", None)
    # if constraints starved the plan, relax the grammar-adjacency and recent-triple rules (least-observed first)
    if len(chosen) < n:
        last_grammar = None
        for arm in unseen:
            if len(chosen) >= n:
                break
            if arm_key(arm) not in used_keys and per_pillar.get(arm["pillar"], 0) < pillar_cap:
                take(arm, "explore", None)
    bits_used = list(used_bits or [])
    slots = []
    solo_count = 0
    lb = a["length_buckets"]
    for i, c in enumerate(chosen):
        arm = c["arm"]
        if arm["speaker"] != "DUO":
            solo_count += 1
        bit = _bit_for(i, arm["speaker"], bits_used, cfg, rng, solo_count)
        if bit:
            bits_used.append(bit)
        lo, hi, tgt = lb[arm["length"]]
        slots.append({"slot_index": i, "hour": hours[i] if i < len(hours) else hours[-1], "pillar": arm["pillar"],
                      "grammar": arm["grammar"], "editorial_format": arm["format"], "speaker": arm["speaker"],
                      "length_bucket": arm["length"], "length_s": {"min": lo, "max": hi, "target": tgt},
                      "render_format": _render_format(arm["format"], arm["speaker"], cfg), "running_bit": bit,
                      "arm_key": arm_key(arm), "mode": c["mode"], "theta": c["theta"],
                      "posterior_mean": round(c["posterior"]["mean"], 4), "observations": c["posterior"]["n"],
                      "proven_grammar": arm["grammar"] in CAT.PROVEN_GRAMMARS, "priority": 50})
    explore_share = sum(1 for s in slots if s["mode"] == "explore") / max(1, len(slots))
    return {"page_id": page.get("id"), "page_slug": page.get("slug"), "platform": platform, "date": date,
            "cadence": n, "slots": slots, "explore_share": round(explore_share, 3),
            "explore_floor": explore_floor, "arms_considered": len(arms), "config_version": cfg.get("version"),
            "hook_families": {g: {"mean": f["mean"], "n": f["n"]} for g, f in sorted(fam.items(), key=lambda kv: -kv[1]["mean"])},
            "seed": seed, "used_bits": bits_used[-int(a["bit_cooldown"]):]}


def tomorrow(now: datetime | None = None) -> str:
    return ((now or datetime.now(timezone.utc)) + timedelta(days=1)).date().isoformat()
