"""Remake briefs: a proven niche post -> OUR version (mechanism, Chang's / Sun's angle, a running bit, N hooks, a lane)
-> script-queue item with provenance. We remake the IDEA and the gene (hook grammar x pillar x close), never the words
or the footage.

Plagiarism guard (guard()), applied to every line we write:
  * no reused line: no brief line equals (after normalisation) any sentence of the source text
  * no shared 7-word shingle with the source (same shingle definition as tools/build_content.py SHINGLE_N = 7)
  * visual concept only: the brief describes our own set and action; it carries no source frame, thumbnail, audio or
    media URL (the source URL lives only in provenance, for audit)
A hook that fails is replaced by the next template; a brief that still fails is not queued.
Every queued item must still pass /compliance/scan + the LLM judge + /uniqueness/check downstream (must_pass).
Pure; no network, no external AI: hooks come from our grammar templates, the script writer expands the brief later.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

from growth import catalog as CAT

SHINGLE_N = 7
KITCHEN_PILLARS = {"P10", "P11", "P12", "P13"}
# pillar -> (topic phrase, everyday object, mechanism (plain, no outcome promise), our set)
PILLAR_BRIEF = {
    "P01": ("standing up from a chair", "chair", "leg power is the first strength we lose and the easiest to measure",
            "SET-GARAGE"),
    "P02": ("getting up off the couch", "chair", "sit-to-stand uses the biggest muscles you own; they answer to practice",
            "SET-LIVING"),
    "P03": ("standing on one leg", "kitchen counter", "balance is a skill: the ankle and hip practise it or forget it",
            "SET-KITCHEN"),
    "P04": ("opening a stuck jar", "towel", "grip and carrying strength track everyday independence", "SET-KITCHEN"),
    "P05": ("tying your shoes", "towel", "joints keep the range they use; daily range keeps it", "SET-BEDROOM"),
    "P06": ("the stairs on a stiff morning", "stairs", "gentle loading within a pain-monitoring rule, red flags first",
            "SET-STAIRS"),
    "P07": ("slowing down your breathing", "pillow", "a long exhale shifts the body toward rest", "SET-BEDROOM"),
    "P08": ("moving slow and steady", "broom", "slow weight shifts train balance and calm at once", "SET-GARDEN"),
    "P09": ("winding down at night", "pillow", "a steady evening routine makes sleep easier to fall into", "SET-BEDROOM"),
    "P10": ("feeling heavy after dinner", "spoon", "fibre and a short walk after meals keep digestion moving",
            "SET-KITCHEN"),
    "P11": ("cooking for one", "soup pot", "a simple soup is protein, vegetables and water in one bowl", "SET-KITCHEN"),
    "P12": ("the honey jar in your pantry", "honey jar", "a few pantry foods have real studies; most viral ones don't",
            "SET-KITCHEN"),
    "P13": ("eating enough protein", "egg", "muscle needs protein at each meal, not just dinner", "SET-KITCHEN"),
    "P14": ("your calf muscles", "stairs", "one mechanism, shown with an anatomy inset", "SET-GARAGE"),
    "P15": ("what everyone says about getting older", "chair", "the popular claim, then what the evidence shows",
            "SET-LIVING"),
    "P16": ("turning seventy", "mirror", "a blunt truth about aging, then one thing to do today", "SET-LIVING"),
    "P17": ("forty years of marriage", "kitchen table", "couple life as the frame for one habit", "SET-KITCHEN"),
    "P18": ("your question from yesterday", "phone", "answer one real comment by first name", "SET-LIVING"),
    "P19": ("seven days of chair stands", "calendar", "a short series with a retest at the end", "SET-GARAGE"),
    "P20": ("being coached by an AI", "screen", "how we pick studies and who the real humans are", "SET-LIVING"),
}
HOOK_TEMPLATES = {
    "IF_EVERY": "If {topic} feels harder than it did five years ago, try this.",
    "NOT_X": "It's not your age. It's what you stopped doing with the {obj}.",
    "MYTH": "Everyone over sixty hears the same advice about {topic}. Half of it is wrong.",
    "WATCH": "Watch what I do with the {obj} every single morning.",
    "TEST_NOW": "Grab the {obj}. Thirty seconds. Let's see where you are.",
    "OBJ3": "The {obj}, a timer, and two minutes. That's the whole plan.",
    "SHARE": "Send this to someone who keeps putting off {topic}.",
    "DEMO": "Here's exactly how I handle {topic}, step by step.",
    "KITCHEN_SERIES": "Sun's kitchen, night three: {topic}, the way my mother did it.",
    "DEBUNK": "I tried the {obj} trick everyone is sharing. Here's what actually happened.",
    "CUR": "Nobody talks about {topic} after sixty. So I will.",
}
HOOK_ORDER = ("IF_EVERY", "NOT_X", "WATCH", "MYTH", "TEST_NOW", "OBJ3", "DEMO", "SHARE", "DEBUNK", "CUR",
              "KITCHEN_SERIES")
BITS_BY_SPEAKER = {
    "CHANG": ("No mirror flexing", "Hips. Now.", "Study card from the shorts pocket", "Tank top in January",
              "Welding metaphors", "The hidden kettlebell", "The chair is Coach", "Frank's excuses", "The AI winks"),
    "SUN": ("I'm older, so I'm right", "Dumpling count", "Seven out of ten", "Mandu the cat", "The apron", "Sun's visor",
            "Aigo", "Jajangmyeon Sunday", "Write this down", "Short version", "Phone calls from Mina"),
}
ANGLE = {
    "CHANG": "Chang (74, retired welder) does it on camera first, keeps score out loud and labels his number "
             "\"Chang's level\". Short sentences. Statement, pause, demonstration. Ends: \"Tell me your number.\"",
    "SUN": "Sun gives the verdict first, then the reason, then the kindness. Grams, not vibes; she asks for the study. "
           "Ends: \"Now go eat.\" or \"Send this to your sister.\"",
}


def _norm(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", (s or "").lower().replace("’", "'")))


def shingles(text: str, n: int = SHINGLE_N) -> set[str]:
    w = [t.strip("'") for t in re.findall(r"[a-z0-9']+", (text or "").lower().replace("’", "'"))]
    w = [t for t in w if t]
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def source_text(row: dict) -> str:
    return "\n".join(str(row.get(k) or "") for k in ("hook_line", "title_or_caption", "overlay_text", "transcript"))


def guard(lines: list[str], src: str) -> dict:
    src_lines = {_norm(x) for x in re.split(r"(?<=[.?!])\s+|\n", src or "") if _norm(x)}
    src_sh = shingles(src)
    reused = [l for l in lines if _norm(l) and _norm(l) in src_lines]
    shared = sorted({s for l in lines for s in shingles(l) & src_sh})
    return {"ok": not reused and not shared, "reused_lines": reused, "shared_shingles": shared}


def _pick(seq, key: str):
    return seq[int(hashlib.sha256(key.encode()).hexdigest(), 16) % len(seq)]


def hooks_for(row: dict, n: int = 3) -> list[dict]:
    topic, obj, _, _ = PILLAR_BRIEF.get(row.get("pillar"), PILLAR_BRIEF["P16"])
    src = source_text(row)
    order = [row.get("hook_grammar")] + [g for g in CAT.PROVEN_GRAMMARS] + list(HOOK_ORDER)
    out, seen = [], set()
    for g in order:
        if g not in HOOK_TEMPLATES or g in seen:
            continue
        if g == "KITCHEN_SERIES" and row.get("pillar") not in KITCHEN_PILLARS:
            continue
        seen.add(g)
        line = HOOK_TEMPLATES[g].format(topic=topic, obj=obj)
        if len(line.split()) > 16 or not guard([line], src)["ok"]:
            continue
        out.append({"grammar": g, "hook": line})
        if len(out) == n:
            break
    return out


def brief(row: dict, *, n_hooks: int = 3, opportunity: dict | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    p = row.get("pillar") if row.get("pillar") in PILLAR_BRIEF else "P16"
    topic, obj, mech, set_code = PILLAR_BRIEF[p]
    speaker = "SUN" if p in KITCHEN_PILLARS else "CHANG"
    key = f"{row.get('platform')}:{row.get('id')}"
    lane = row.get("lane") or "talking_head"
    visual = {"talking_head": f"{set_code}: {speaker.title()} to camera, the {obj} in frame, one push-in on the key line",
              "insert": f"{set_code}: {speaker.title()} at the counter with the {obj}; hands-only insert, our props",
              "movement": f"{set_code}: {speaker.title()} demonstrates with the {obj}, side 3/4, counter or chair for "
                          f"support, reps counted aloud"}[lane]
    hooks = hooks_for({**row, "pillar": p}, n_hooks)
    b = {"mechanism": mech, "topic": topic, "pillar": p, "format": CAT.PILLAR_FORMATS[p][0], "speaker": speaker,
         "angle": ANGLE[speaker], "running_bit": _pick(BITS_BY_SPEAKER[speaker], key), "hooks": hooks, "lane": lane,
         "visual_concept": visual, "close_family": row.get("close_family") or "close",
         "gene": {"hook": row.get("hook_family"), "body": row.get("body_family"), "close": row.get("close_family")}}
    written = [h["hook"] for h in hooks] + [b["angle"], b["mechanism"], b["visual_concept"]]
    g = guard(written, source_text(row))
    b["guard"] = g
    return b


def queue_item(row: dict, *, n_hooks: int = 3, opportunity: dict | None = None, reason: str = "top_performer",
               now: datetime | None = None, priority: int = 60) -> dict | None:
    """-> script-queue row (table remake_queue) or None when the guard fails or too few clean hooks exist."""
    now = now or datetime.now(timezone.utc)
    b = brief(row, n_hooks=n_hooks, opportunity=opportunity, now=now)
    if not b["guard"]["ok"] or len(b["hooks"]) < n_hooks:
        return None
    src = source_text(row)
    return {"kind": "remake", "status": "queued", "reason": reason, "priority": priority, "brief": b,
            "provenance": {"platform": row.get("platform"), "external_id": str(row.get("id")), "url": row.get("url"),
                           "creator": row.get("account"), "crawled_at": row.get("crawled_at"),
                           "source": row.get("source"), "rel_perf": row.get("rel_perf"),
                           "content_sha": hashlib.sha256(src.encode()).hexdigest(),
                           "opportunity": {k: opportunity.get(k) for k in ("gene", "direction", "from_platform")}
                           if opportunity else None},
            "must_pass": ["/compliance/scan", "llm_judge", "/uniqueness/check"],
            "media_policy": "visual concept only; no source media is downloaded, stored or re-hosted",
            "created_at": now.isoformat()}


def queue(rows: list[dict], feeds: dict | None = None, *, max_items: int = 20, now: datetime | None = None) -> list[dict]:
    """Script queue for one run: transfer opportunities first (their best evidence post), then the daily top list."""
    now = now or datetime.now(timezone.utc)
    by = {f"{r['platform']}:{r['id']}": r for r in rows}
    out, used = [], set()
    for o in (feeds or {}).get("opportunities", []):
        for pid in o.get("evidence_post_ids", [])[:1]:
            r = by.get(f"{o['from_platform']}:{pid}")
            if r and f"{r['platform']}:{r['id']}" not in used:
                q = queue_item(r, opportunity=o, reason=f"transfer:{o['direction']}", now=now, priority=75)
                if q:
                    out.append(q)
                    used.add(f"{r['platform']}:{r['id']}")
    for t in (feeds or {}).get("daily_top20", []):
        k = f"{t['platform']}:{t['id']}"
        if k in used or k not in by:
            continue
        q = queue_item(by[k], now=now)
        if q:
            out.append(q)
            used.add(k)
    return out[:max_items]
