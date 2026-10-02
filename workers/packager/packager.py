"""Per-platform packaging normaliser (after prompts/06 'LLM: Platform Packaging') + compliance pass 2.

Enforces, deterministically:
- exact caption footer (SAFETY §7, reviewer gate) always last on IG / TikTok / FB captions and the YT description,
  with the movement add-on immediately before it when the script has movement;
- AI flags: tiktok.is_aigc = true, youtube.contains_synthetic_media = true (§5.2), plus ai_label metadata for
  IG/FB/Threads/X (IG/FB "AI info" comes from C2PA; the account-level label is a manual precondition);
- platform length and hashtag limits, banned tags, dedupe, no links in X bodies, CTA routing where DM automation
  doesn't exist (TikTok US comment triggers, YouTube);
- UTM + pid links for bio / DM automation (PIPELINE §7.1 attribution chain). Links never go into captions.
"""
from __future__ import annotations

import re
from urllib.parse import urlencode

from common import disclosure
from compliance import caption_rules
from compliance.rules import CONDITION_HASHTAG_RX

LIMITS = {
    # caption body chars (before footer), total chars, hashtag count
    "instagram": {"total": 2200, "hashtags": (3, 5), "line1": 125},
    "tiktok": {"body": 150, "total": 2200, "hashtags": (3, 5)},
    "youtube": {"title": 60, "title_hard": 100, "total": 5000, "hashtags": (3, 3), "tags_chars": 500},
    "facebook": {"total": 2200, "hashtags": (0, 2)},
    "threads": {"total": 450, "hard": 500, "hashtags": (0, 1)},
    "x": {"total": 270, "hard": 280, "hashtags": (0, 2)},
}
UTM_SOURCE = {"instagram": "ig", "tiktok": "tt", "youtube": "yt", "facebook": "fb", "threads": "threads", "x": "x"}
BANNED_TAGS = {"#fyp", "#foryou", "#foryoupage", "#viral", "#xyzbca", "#trending", "#explorepage", "#followforfollow",
               "#f4f", "#like4like", "#detox", "#cure", "#antiaging", "#miracle", "#weightlosshack"}
DEFAULT_DM = {"instagram": True, "facebook": True, "tiktok": False, "youtube": False, "threads": False, "x": False}
URL_RX = re.compile(r"(https?://\S+|www\.\S+)", re.I)


def _truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    cut = cut[: cut.rfind(" ")] if " " in cut[limit // 2:] else cut
    return cut.rstrip(" ,;:-") + "…"


def norm_hashtags(tags, lo_hi: tuple[int, int]) -> tuple[list[str], list[str]]:
    notes, out, seen = [], [], set()
    for t in tags or []:
        t = "#" + re.sub(r"[^\w]", "", str(t).lstrip("#")).lower()
        if len(t) < 3 or t in seen:
            continue
        if t in BANNED_TAGS:
            notes.append(f"dropped banned tag {t}")
            continue
        if CONDITION_HASHTAG_RX.search(t):  # AUDIT_FINAL round 5: canon, no condition / fall hashtags
            notes.append(f"dropped condition tag {t}")
            continue
        seen.add(t)
        out.append(t)
    lo, hi = lo_hi
    if len(out) > hi:
        notes.append(f"hashtags trimmed {len(out)}->{hi}")
        out = out[:hi]
    if len(out) < lo:
        notes.append(f"only {len(out)} hashtags (target {lo}-{hi})")
    return out, notes


def _strip_disclosures(text: str) -> str:
    for f in disclosure.all_footers() + list(disclosure.MOVEMENT_ADDON.values()):
        text = text.replace(f, "")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _strip_hashtags(text: str) -> str:
    return re.sub(r"(?:\s*#\w+)+\s*$", "", text).strip()


def with_footer(body: str, tags: list[str], footer: str, addon: str | None, limit: int) -> str:
    tail = "\n\n".join(x for x in [" ".join(tags) if tags else "", addon or "", footer] if x)
    room = limit - len(tail) - 2
    return (_truncate(body, max(room, 20)) + "\n\n" + tail).strip()


def links(page_slug: str, brief_id: str, site: str, path: str = "start", post_ids: dict | None = None) -> dict:
    out = {}
    for pl, src in UTM_SOURCE.items():
        q = {"utm_source": src, "utm_medium": "organic_short", "utm_campaign": page_slug,
             "utm_content": f"{str(brief_id)[:8]}-{src}"}
        if post_ids and post_ids.get(pl):
            q["pid"] = post_ids[pl]
        out[pl] = f"{site.rstrip('/')}/{path.lstrip('/')}?{urlencode(q)}"
    return out


def package(pk: dict, *, page_dna: dict | None = None, script: dict | None = None, locale: str = "en-US",
            market: str = "US", reviewer_signed: bool = False, page_slug: str = "", brief_id: str = "",
            site_base_url: str = "https://example.com", post_ids: dict | None = None) -> dict:
    dna = page_dna or {}
    reviewer_signed = bool(reviewer_signed)          # caller passes config.REVIEWER_SIGNED (AUDIT M4)
    has_movement = bool((script or {}).get("has_movement") or ((script or {}).get("movement") or {}).get("present"))
    footer = disclosure.footer(locale, reviewer_signed)
    dna_footer = (dna.get("caption_footer") or "").strip()
    notes: list[str] = []
    if dna_footer and dna_footer != footer:
        notes.append("page_dna.caption_footer differs from the SAFETY §7 string for this reviewer state; used §7 string")
    addon = disclosure.movement_addon(locale) if has_movement else None
    dm = {**DEFAULT_DM, **(dna.get("dm_automation") or {})}
    if market.upper() == "US":
        dm["tiktok"] = False          # ManyChat TikTok comment triggers are not available in the US
    kw = ((script or {}).get("cta") or {}).get("keyword") or (script or {}).get("cta_keyword") or ""
    out = {k: dict(v) for k, v in (pk or {}).items() if isinstance(v, dict)}

    def fix_cta(text: str, pl: str, repl: str) -> str:
        if kw and not dm.get(pl) and re.search(rf"\bcomment\s+{re.escape(kw)}\b", text, re.I):
            notes.append(f"{pl}: no DM automation -> CTA rewritten to '{repl}'")
            text = re.sub(rf"[^.\n]*\bcomment\s+{re.escape(kw)}\b[^.\n]*\.?", repl, text, flags=re.I)
        return text

    ig = out.get("instagram")
    if ig is not None:
        tags, n = norm_hashtags(ig.get("hashtags"), LIMITS["instagram"]["hashtags"]); notes += n
        body = _strip_hashtags(_strip_disclosures(ig.get("caption", "")))
        first = body.split("\n", 1)[0]
        if len(first) > LIMITS["instagram"]["line1"]:
            notes.append("instagram: line 1 over 125 chars (truncated before 'more')")
        ig.update(caption=with_footer(body, tags, footer, addon, LIMITS["instagram"]["total"]), hashtags=tags,
                  ai_label=True, ai_info_expected_from_c2pa=True)
    tt = out.get("tiktok")
    if tt is not None:
        tags, n = norm_hashtags(tt.get("hashtags"), LIMITS["tiktok"]["hashtags"]); notes += n
        body = fix_cta(_strip_hashtags(_strip_disclosures(tt.get("caption", ""))), "tiktok", "Full plan: link in bio.")
        body = _truncate(body, LIMITS["tiktok"]["body"])
        tt.update(caption=with_footer(body, tags, footer, addon, LIMITS["tiktok"]["total"]), hashtags=tags, is_aigc=True)
    yt = out.get("youtube")
    if yt is not None:
        title = URL_RX.sub("", yt.get("title", "")).strip()
        if len(title) > LIMITS["youtube"]["title"]:
            notes.append(f"youtube: title {len(title)} chars > 60 (truncated)")
            title = _truncate(title, LIMITS["youtube"]["title"])
        tags, n = norm_hashtags(yt.get("hashtags") or [t for t in (yt.get("tags") or []) if str(t).startswith("#")],
                                LIMITS["youtube"]["hashtags"]); notes += n
        body = fix_cta(_strip_hashtags(_strip_disclosures(yt.get("description", ""))), "youtube",
                       "Free plan → link in channel.")
        plain_tags, total = [], 0
        for t in yt.get("tags") or []:
            t = str(t).lstrip("#").strip()
            if t and total + len(t) + 1 <= LIMITS["youtube"]["tags_chars"]:
                plain_tags.append(t)
                total += len(t) + 1
        yt.update(title=title, description=with_footer(body, tags, footer, addon, LIMITS["youtube"]["total"]),
                  tags=plain_tags, contains_synthetic_media=True)
    fb = out.get("facebook")
    if fb is not None:
        tags, n = norm_hashtags(fb.get("hashtags"), LIMITS["facebook"]["hashtags"]); notes += n
        body = fix_cta(_strip_hashtags(_strip_disclosures(fb.get("caption", ""))), "facebook", "Free plan: link in bio.")
        fb.update(caption=with_footer(body, tags, footer, addon, LIMITS["facebook"]["total"]), hashtags=tags, ai_label=True)
    th = out.get("threads")
    if th is not None:
        text = _strip_disclosures(th.get("text", ""))
        if len(text) > LIMITS["threads"]["total"]:
            notes.append("threads: text over 450 chars (truncated)")
        th.update(text=_truncate(text, LIMITS["threads"]["total"]), ai_label=True)
    x = out.get("x")
    if x is not None:
        text = _strip_disclosures(x.get("text", ""))
        if URL_RX.search(text):
            notes.append("x: link removed from body (links depress reach and cost $0.20/post)")
            text = re.sub(r"\s{2,}", " ", URL_RX.sub("", text)).strip()
        if len(text) > LIMITS["x"]["total"]:
            notes.append("x: text over 270 chars (truncated)")
        x.update(text=_truncate(text, LIMITS["x"]["total"]), ai_label=True)
    caption_issues = []                       # SL-06.4 evergreen time words, SL-06.5 handle allowlist
    for pl, d in out.items():
        for field in ("caption", "description", "text", "title"):
            if isinstance(d.get(field), str):
                r = caption_rules.apply(d[field])
                d[field] = r["text"]
                notes += [f"{pl}.{field}: {n}" for n in r["rewrites"]]
                caption_issues += [f"{pl}.{field}: handle {h} is not one of ours" for h in r["blocked_handles"]]
    return {"packaging": out, "notes": notes, "footer": footer, "movement_addon": addon, "caption_issues": caption_issues,
            "links": links(page_slug or "page", brief_id or "brief", site_base_url, post_ids=post_ids)}
