"""Canonical niche items -> (a) rows in the data/posts.csv schema (POSTDB_FINDINGS) and (b) `niche_posts` table rows
(schema_discover.sql) carrying the derived genes (genes.derive = the scorecard's hook / body / close decomposition).

rel_perf keeps the posts.csv definition: the post's metric / the rolling median of the same account's 15 nearest posts
in time (excluding itself). Accounts with < 3 posts in the batch fall back to the niche baseline (platform median).
The metric is views; where a platform hides other accounts' views (Instagram business_discovery, Threads), it is
engagement (likes + 2 x comments + 3 x shares), compared only against the same metric. Pure; no network.
"""
from __future__ import annotations

import hashlib
import re
import statistics
from datetime import datetime, timezone

from discover import genes as GN

POSTS_CSV_COLUMNS = ("platform", "account", "id", "url", "date", "views", "likes", "comments", "shares", "duration_s",
                     "title_or_caption", "hashtags", "cta_keyword", "cta_type", "topic", "hook_type", "claim_strength",
                     "format", "props", "notes", "rel_perf", "duration_bucket", "hook_line", "overlay_text")
PLATFORM_LABEL = {"instagram": "Instagram", "facebook": "Facebook", "tiktok": "TikTok", "youtube": "YouTube",
                  "threads": "Threads", "x": "X"}
PILLAR_TOPIC = {"P01": "strength tests", "P02": "legs/chair strength", "P03": "balance", "P04": "grip/upper body",
                "P05": "mobility/stretching", "P06": "pain relief/rehab", "P07": "anxiety/nervous system", "P08": "tai chi/qigong/yoga",
                "P09": "sleep", "P10": "gut/digestion", "P11": "recipes", "P12": "kitchen remedy", "P13": "protein/muscle food",
                "P14": "physiology", "P15": "myth-busting", "P16": "longevity/aging", "P17": "relationships", "P18": "Q&A",
                "P19": "challenge/series", "P20": "behind the AI"}
GRAMMAR_HOOK_TYPE = {"IF_EVERY": "if you do X -> outcome", "MYTH": "myth / you're doing it wrong",
                     "NOT_X": "myth / you're doing it wrong", "DEBUNK": "myth / you're doing it wrong",
                     "WATCH": "curiosity (watch what happens)", "TEST_NOW": "question", "SHARE": "callout (audience/geo)",
                     "KITCHEN_SERIES": "how-to / direct promise", "DEMO": "do this (before/when X)", "OBJ3": "statement / aphorism",
                     "CUR": "statement / aphorism"}
_STRONG = re.compile(r"\b(cure[sd]?|reverse[sd]?|eliminate[sd]?|melt[s]?|heal[s]?|detox|guarantee[sd]?|miracle|never again)\b", re.I)
_SOFT = re.compile(r"\b(help[s]?|support[s]?|may|can improve|better|boost[s]?|ease[s]?)\b", re.I)
_55 = re.compile(r"\b(over (?:50|55|60|65|70|75|80)|after (?:50|55|60|65|70)|seniors?|older adults?|elderly|grandm\w*|"
                 r"grandp\w*|retire\w*|50s|60s|70s|80s|aging|ageing)\b", re.I)


def parse_dt(x) -> datetime | None:
    if not x:
        return None
    try:
        d = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def duration_bucket(d) -> str:
    if d in (None, ""):
        return "unknown"
    d = float(d)
    for hi, lab in ((30, "<30s"), (45, "30-44s"), (60, "45-59s"), (90, "60-89s"), (180, "90-179s")):
        if d < hi:
            return lab
    return "180s+"


def engagement(it: dict) -> float:
    return float((it.get("likes") or 0) + 2 * (it.get("comments") or 0) + 3 * (it.get("shares") or 0))


def metric(it: dict) -> tuple[str, float | None]:
    v = it.get("engaged_views") if it.get("platform") == "youtube" and it.get("engaged_views") else it.get("views")
    if v is not None:
        return "views", float(v)
    if any(it.get(k) is not None for k in ("likes", "comments", "shares")):
        return "engagement", engagement(it)
    return "none", None


def cta_type(fam: str) -> str:
    return {"close": "none", "LINK": "link in bio only", "SAVE": "follow/save/share only", "SHARE": "follow/save/share only",
            "FOLLOW": "follow/save/share only"}.get(fam, "keyword -> DM lead magnet")


def claim_strength(text: str) -> str:
    return "strong" if _STRONG.search(text or "") else "soft" if _SOFT.search(text or "") else "none"


def niche_match(text: str) -> bool:
    return bool(_55.search(text or "")) or GN.pillar_matched(text)


def _rel(items: list[dict]) -> None:
    """In place: rel_perf (creator rolling median, 15 nearest) and rel_niche (platform x metric median)."""
    niche: dict[tuple, list[float]] = {}
    for it in items:
        m, v = metric(it)
        it["_metric"], it["_value"] = m, v
        if v is not None:
            niche.setdefault((it["platform"], m), []).append(v)
    nmed = {k: statistics.median(v) for k, v in niche.items() if v}
    by_creator: dict[tuple, list[dict]] = {}
    for it in items:
        by_creator.setdefault((it["platform"], it.get("creator") or "?", it["_metric"]), []).append(it)
    for (plat, _, m), group in by_creator.items():
        group.sort(key=lambda i: str(i.get("published_at") or ""))
        for idx, it in enumerate(group):
            v = it["_value"]
            base_n = nmed.get((plat, m))
            it["rel_niche"] = round(v / base_n, 3) if v is not None and base_n else None
            others = sorted(range(len(group)), key=lambda j: abs(j - idx))[1:16]
            peer = [group[j]["_value"] for j in others if group[j]["_value"] is not None]
            if v is None:
                it["rel_perf"], it["baseline"] = None, None
            elif len(peer) >= 2 and statistics.median(peer) > 0:
                it["rel_perf"], it["baseline"] = round(v / statistics.median(peer), 3), "creator"
            else:
                it["rel_perf"], it["baseline"] = it["rel_niche"], "niche"


def rows(items: list[dict], *, now: datetime | None = None) -> list[dict]:
    """Canonical items -> enriched rows (posts.csv columns + niche_posts fields)."""
    now = now or datetime.now(timezone.utc)
    items = [dict(i) for i in items if i.get("platform") and i.get("id")]
    _rel(items)
    out = []
    for it in items:
        g = GN.derive(it)
        text = GN.all_text(it)
        pub = parse_dt(it.get("published_at"))
        age_h = max(1.0, (now - pub).total_seconds() / 3600.0) if pub else None
        out.append({
            "platform": it["platform"], "account": it.get("creator") or "", "id": str(it["id"]), "url": it.get("url") or "",
            "date": pub.date().isoformat() if pub else "", "published_at": pub.isoformat() if pub else None,
            "views": it.get("views"), "engaged_views": it.get("engaged_views"), "likes": it.get("likes"),
            "comments": it.get("comments"), "shares": it.get("shares"), "saves": it.get("saves"),
            "duration_s": it.get("duration_s"), "title_or_caption": it.get("title_or_caption") or "",
            "hashtags": it.get("hashtags") or "", "cta_keyword": g["cta_keyword"] if g["cta_keyword"] != "close" else "",
            "cta_type": cta_type(g["cta_keyword"]), "topic": PILLAR_TOPIC.get(g["pillar"], "unknown"),
            "hook_type": GRAMMAR_HOOK_TYPE.get(g["hook_grammar"], "none/unknown"), "claim_strength": claim_strength(text),
            "format": g["format"], "props": "", "notes": f"discover:{it.get('source')}", "rel_perf": it.get("rel_perf"),
            "rel_niche": it.get("rel_niche"), "baseline": it.get("baseline"), "metric": it["_metric"],
            "metric_value": it["_value"], "duration_bucket": duration_bucket(it.get("duration_s")),
            "hook_line": g["hook_line"], "overlay_text": it.get("overlay_text") or "", "transcript": it.get("transcript") or "",
            "velocity_per_h": round(it["_value"] / age_h, 3) if it["_value"] is not None and age_h else None,
            "creator_followers": it.get("creator_followers"), "source": it.get("source"), "seed": it.get("seed"),
            "seed_kind": "creator" if str(it.get("seed") or "").startswith("C") else "query",
            "niche_match": niche_match(text), "pillar": g["pillar"], "hook_grammar": g["hook_grammar"], "lane": g["lane"],
            "hook_family": g["hook_family"], "body_family": g["body_family"], "close_family": g["close_family"],
            "hook_block_id": g["hook_block_id"], "body_block_id": g["body_block_id"], "close_block_id": g["close_block_id"],
            "genes": g["genes"], "crawled_at": now.isoformat(),
        })
    return out


def posts_csv_row(r: dict) -> dict:
    out = {c: r.get(c) for c in POSTS_CSV_COLUMNS}
    out["platform"] = PLATFORM_LABEL.get(r["platform"], r["platform"])
    out["id"] = f"{r['platform']}_{r['id']}"
    return {k: ("" if v is None else v) for k, v in out.items()}


def db_row(r: dict) -> dict:
    """Shape for table niche_posts (schema_discover.sql). Never stores media: metadata + transcript text only."""
    keys = ("platform", "url", "views", "engaged_views", "likes", "comments", "shares", "saves", "duration_s",
            "title_or_caption", "hashtags", "transcript", "overlay_text", "hook_line", "cta_keyword", "topic", "pillar",
            "format", "lane", "hook_grammar", "hook_family", "body_family", "close_family", "hook_block_id",
            "body_block_id", "close_block_id", "genes", "rel_perf", "rel_niche", "metric", "metric_value",
            "velocity_per_h", "creator_followers", "claim_strength", "source", "seed", "published_at", "crawled_at")
    out = {k: r.get(k) for k in keys}
    out.update(external_id=r["id"], creator=r.get("account") or None,
               content_sha=hashlib.sha256((r.get("title_or_caption", "") + "\n" + r.get("transcript", "")).encode()).hexdigest())
    return out
