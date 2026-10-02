"""Gene decomposition for niche posts: the SAME hook / body / close split and family names the scorecard uses
(growth.variants.decompose -> hook family = hook grammar, body family = pillar:format, close family = CTA keyword;
growth.actions.genes_of -> "hook:<grammar>", "body:<pillar:format>", "close:<keyword>").

Our own posts carry their grammar / pillar / format from the script. A crawled post only has public text (caption,
title, transcript, on-screen text), so the families are classified here with deterministic rules. Pure; no network.
"""
from __future__ import annotations

import re

from growth import catalog as CAT
from growth import variants as V

# order matters: the first rule that fires names the grammar (most specific first)
_G = [
    ("SHARE", r"^(send|share|tag|forward)\b|\b(send this to|share this with|tag (your|someone))\b"),
    ("MYTH", r"\b(myth|you'?ve been (told|lied)|everyone (says|thinks)|stop believing|nobody tells you|doctors? (won'?t|don'?t) tell)\b"),
    ("NOT_X", r"\b(it'?s not|isn'?t|aren'?t|is not|are not)\b[^.?!]{0,40}[.,;:]?\s*(it'?s|its|it is|they'?re|the real)\b"),
    ("DEBUNK", r"\b(doesn'?t work|does not work|is a scam|fake|debunk|the truth about|stop (doing|eating|taking))\b"),
    ("IF_EVERY", r"^(if|every|everyone who|when you|anyone over)\b|^\S+(\s+\S+){0,3}\s+if you\b"),
    ("WATCH", r"^(watch|look)\b|\b(watch what happens|see what happens|look what happens)\b"),
    ("TEST_NOW", r"\b(try this|right now|can you|test yourself|score yourself|how many|in \d+ seconds|count)\b"),
    ("KITCHEN_SERIES", r"\b(recipe|soup|broth|tea|boil|simmer|onion|ginger|garlic|kimchi|porridge|congee|dumpling)\b"),
    ("DEMO", r"\b(here'?s how|do this|like this|how to|step \d|follow along)\b"),
]
_GRAMMAR_RX = [(g, re.compile(rx, re.I)) for g, rx in _G]
_OBJECTS = {"chair", "towel", "wall", "jar", "spoon", "stairs", "stair", "bed", "onion", "banana", "egg", "eggs", "cup",
            "bottle", "broom", "door", "counter", "sock", "socks", "shoe", "shoes", "pillow", "kettlebell", "band", "can"}

# pillar keyword rules (CONTENT_SYSTEM.md §1); first match wins, ordered specific -> general
_P = [
    ("P20", r"\b(ai|artificial intelligence|behind the scenes)\b"),
    ("P18", r"\b(you asked|your question|reading (your )?comments|replying to)\b"),
    ("P19", r"\b(\d+[- ]day challenge|challenge|day \d+ of)\b"),
    ("P15", r"\b(myth|debunk|scam|doesn'?t work|lie)\b"),
    ("P07", r"\b(breath|breathe|breathing|exhale|inhale|vagus|nervous system|anxiety|calm)\b"),
    ("P09", r"\b(sleep|insomnia|bedtime|night|wake up at)\b"),
    ("P08", r"\b(tai chi|qigong|yoga)\b"),
    ("P03", r"\b(balance|fall|falls|steady|one leg|unsteady|wobbl)\w*"),
    ("P01", r"\b(test|how many|push-?ups?|sit[- ]to[- ]stand|chair stand|grip strength|strength age)\b"),
    ("P02", r"\b(legs?|squat|knees? strong|thigh|quad|step-?ups?|wall sit|chair)\b"),
    ("P04", r"\b(grip|carry|carries|arms?|shoulder press|upper body|towel wring|jar)\b"),
    ("P06", r"\b(back pain|knee pain|shoulder pain|sciatica|arthritis|stiff|rehab|relief)\b"),
    ("P05", r"\b(mobility|stretch|stretching|hips?|flexib|ankle|posture|spine)\w*"),
    ("P10", r"\b(gut|digest|bloat|constipat|fiber|fibre|prune|ferment)\w*"),
    ("P13", r"\b(protein|muscle food|grams|eggs?|tofu|beans)\b"),
    ("P12", r"\b(remedy|remedies|honey|ginger|kiwi|onion|garlic|turmeric|lemon)\b"),
    ("P11", r"\b(recipe|soup|broth|cook|cooking|kitchen|meal|porridge|kimchi|dumpling)\w*"),
    ("P17", r"\b(husband|wife|marriage|married|couple|grandkids?|grandchildren)\b"),
    ("P14", r"\b(muscle|bones?|calf|cells?|mitochondria|hormone|metabolism)\b"),
    ("P16", r"\b(aging|ageing|over (50|55|60|65|70)|retire|lonely|grief|old age|too old)\b"),
]
_PILLAR_RX = [(p, re.compile(rx, re.I)) for p, rx in _P]
_MOVEMENT = re.compile(r"\b(exercise|reps?|squat|stretch|lift|push-?ups?|step-?ups?|stand up|balance|walk|tai chi|yoga|"
                       r"follow along|workout|routine)\w*", re.I)
_INSERT = re.compile(r"\b(recipe|soup|tea|cook|boil|onion|ginger|garlic|honey|food|meal|plate|drink)\w*", re.I)
_CTA = [
    (re.compile(r"\b(?i:comment|type|reply|write)\s+[\"'“‘]?([A-Z][A-Z0-9]{1,15})\b"), None),
    (re.compile(r"\blink in (?:my )?bio\b", re.I), "LINK"),
    (re.compile(r"\b(?:save this|save it)\b", re.I), "SAVE"),
    (re.compile(r"\b(?:send this|share this|tag (?:your|someone))\b", re.I), "SHARE"),
    (re.compile(r"\bfollow (?:me|for)\b", re.I), "FOLLOW"),
]
LANES = ("talking_head", "insert", "movement")


def hook_line(post: dict) -> str:
    """The hook = the first sentence a viewer meets: the explicit hook line, else the transcript's first sentence,
    else the overlay text, else the first sentence of the caption/title."""
    for k in ("hook_line", "transcript", "overlay_text", "title_or_caption"):
        t = (post.get(k) or "").strip()
        if t:
            first = re.split(r"(?<=[.?!])\s+|\n", t, maxsplit=1)[0]
            return first.strip()[:200]
    return ""


def grammar(hook: str) -> str:
    h = (hook or "").strip().replace("’", "'")
    for g, rx in _GRAMMAR_RX:
        if rx.search(h):
            return g
    first = [re.sub(r"[^\w-]", "", w).lower() for w in h.split()[:3]]
    if any(w in _OBJECTS for w in first):
        return "OBJ3"
    return "CUR"


def pillar_matched(text: str) -> bool:
    return any(rx.search(text or "") for _, rx in _PILLAR_RX)


def pillar(text: str) -> str:
    for p, rx in _PILLAR_RX:
        if rx.search(text or ""):
            return p
    return "P16"


def fmt(pillar_code: str, text: str) -> str:
    """Primary format of the pillar (CONTENT_SYSTEM §1). A crawled post's format is approximated by its pillar's first
    primary format, except a visible step routine on a pillar that has a demo format."""
    opts = CAT.PILLAR_FORMATS.get(pillar_code) or ("F02",)
    return opts[0]


def lane(text: str) -> str:
    if _MOVEMENT.search(text or ""):
        return "movement"
    if _INSERT.search(text or ""):
        return "insert"
    return "talking_head"


def close_family(text: str) -> str:
    for rx, fam in _CTA:
        m = rx.search(text or "")
        if m:
            return fam or m.group(1).upper()
    return "close"


def all_text(post: dict) -> str:
    return " ".join(str(post.get(k) or "") for k in ("hook_line", "title_or_caption", "overlay_text", "transcript",
                                                       "hashtags"))


def derive(post: dict) -> dict:
    """{hook_grammar, pillar, format, lane, cta_keyword, hook_family, body_family, close_family, genes,
    hook_block_id, body_block_id, close_block_id} through growth.variants.decompose (the scorecard's own split)."""
    text = all_text(post)
    hook = hook_line(post)
    g = grammar(hook)
    p = pillar(text)
    f = fmt(p, text)
    cta = close_family(text)
    dur = post.get("duration_s")
    master = {"master_id": f"N-{post.get('platform')}-{post.get('id')}", "duration_s": float(dur) if dur else 30.0,
              "hook_text": hook, "body_text": post.get("transcript") or post.get("title_or_caption") or "",
              "close_text": "", "hook_grammar": g, "pillar": p, "format": f,
              "cta_keyword": None if cta == "close" else cta}
    b = V.decompose(master)
    fams = {"hook_family": b["hook"]["family"], "body_family": b["body"]["family"], "close_family": b["close"]["family"]}
    return {"hook_line": hook, "hook_grammar": g, "pillar": p, "format": f, "lane": lane(text), "cta_keyword": cta,
            **fams, "hook_block_id": b["hook"]["id"], "body_block_id": b["body"]["id"],
            "close_block_id": b["close"]["id"],
            "genes": [f"{k}:{fams[k + '_family']}" for k in ("hook", "body", "close")]}
