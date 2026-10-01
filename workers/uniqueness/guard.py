"""Uniqueness guard across sibling pages (PIPELINE §2.3). allow/deny for one candidate vs its siblings.

Unit of uniqueness = (platform, page). Same page, other platforms = L1 cross-posting (allowed). Guards:
 1. semantic/text: TF-IDF cosine > 0.86 vs same page (90 d) or > 0.80 vs another page (14 d); MinHash Jaccard >= 0.5
    vs another page is also treated as a copy (embedding-free proxy for scripts.embedding / script_similarity()).
 2. lexical: > 6 consecutive shared words vs another page (safety + CTA lines excepted).
 3. visual: same platform, different page: > 40% of seconds within pHash Hamming <= 10.
 4. audio: the same voice track (fingerprint similarity >= 0.80) on another page.
 6. stagger: sibling derivatives (same idea / parent brief) on other pages >= 48 h apart and never the same slot hour.
"""
from __future__ import annotations

from datetime import datetime, timezone

from uniqueness import audiofp, phash, textsim

T = {"text_same_page": 0.86, "text_network": 0.80, "minhash_network": 0.50, "shared_run_max": 6,
     "phash_overlap": 0.40, "phash_dist": 10, "audio_sim": 0.80, "stagger_h": 48.0,
     "same_page_days": 90, "network_days": 14}


def _dt(x) -> datetime | None:
    if not x:
        return None
    if isinstance(x, datetime):
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    s = str(x).replace("Z", "+00:00")
    if len(s) == 10:
        s += "T00:00:00+00:00"
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _age_days(sib: dict, now: datetime) -> float | None:
    d = _dt(sib.get("created_at") or sib.get("scheduled_at"))
    return None if d is None else abs((now - d).total_seconds()) / 86400


def check(candidate: dict, siblings: list[dict], thresholds: dict | None = None, now: datetime | None = None) -> dict:
    th = {**T, **(thresholds or {})}
    now = now or _dt(candidate.get("scheduled_at")) or datetime.now(timezone.utc)
    reasons: list[str] = []
    cmp: list[dict] = []
    c_page, c_pl = candidate.get("page_id"), candidate.get("platform")
    c_text = candidate.get("script_text") or ""
    corpus = [s.get("script_text") or "" for s in siblings]
    c_when = _dt(candidate.get("scheduled_at"))
    for s in siblings:
        if s.get("id") and s.get("id") == candidate.get("id"):
            continue
        same_page = s.get("page_id") == c_page
        age = _age_days(s, now)
        row = {"sibling": s.get("id") or s.get("post_id"), "page_id": s.get("page_id"), "platform": s.get("platform"),
               "same_page": same_page}
        # text
        if c_text and s.get("script_text"):
            cos = textsim.tfidf_cosine(c_text, s["script_text"], corpus)
            row["text_cosine"] = cos
            if same_page:
                if (age is None or age <= th["same_page_days"]) and cos > th["text_same_page"] and \
                        s.get("platform") in (None, c_pl) and not candidate.get("allow_same_page_repost"):
                    reasons.append(f"text: cosine {cos} > {th['text_same_page']} vs same-page post {row['sibling']}")
            elif age is None or age <= th["network_days"]:
                jac = textsim.minhash_jaccard(c_text, s["script_text"])
                run, words = textsim.longest_shared_run(c_text, s["script_text"])
                row.update({"minhash_jaccard": jac, "shared_run": run})
                if cos > th["text_network"]:
                    reasons.append(f"text: cosine {cos} > {th['text_network']} vs page {s.get('page_id')}")
                if jac >= th["minhash_network"]:
                    reasons.append(f"text: MinHash Jaccard {jac} >= {th['minhash_network']} vs page {s.get('page_id')}")
                if run > th["shared_run_max"]:
                    reasons.append(f"lexical: {run} consecutive shared words ('{words}') vs page {s.get('page_id')}")
        # visual (same platform, other page)
        if not same_page and s.get("phash_seq") and candidate.get("phash_seq") and \
                (c_pl in (None, "all") or s.get("platform") in (None, c_pl)):
            ov = phash.seq_overlap(candidate["phash_seq"], s["phash_seq"], th["phash_dist"])
            row["phash_overlap"] = ov
            if ov > th["phash_overlap"]:
                reasons.append(f"visual: {ov:.0%} of seconds within Hamming <= {th['phash_dist']} vs page {s.get('page_id')}")
        # audio (any platform, other page)
        if not same_page and s.get("audio_fp") and candidate.get("audio_fp"):
            sim = audiofp.similarity(candidate["audio_fp"], s["audio_fp"])
            row["audio_sim"] = sim
            if sim >= th["audio_sim"]:
                reasons.append(f"audio: same voice track (similarity {sim}) as page {s.get('page_id')}")
        # stagger (sibling derivatives)
        related = (candidate.get("idea_id") and s.get("idea_id") == candidate.get("idea_id")) or \
                  (candidate.get("parent_brief_id") and s.get("brief_id") == candidate.get("parent_brief_id")) or \
                  (s.get("parent_brief_id") and s.get("parent_brief_id") == candidate.get("brief_id"))
        s_when = _dt(s.get("scheduled_at"))
        if related and not same_page and c_when and s_when:
            gap_h = abs((c_when - s_when).total_seconds()) / 3600
            row["gap_h"] = round(gap_h, 2)
            if gap_h < th["stagger_h"]:
                reasons.append(f"stagger: sibling derivative on page {s.get('page_id')} only {gap_h:.1f} h apart (< 48 h)")
            if c_when.hour == s_when.hour:
                reasons.append(f"stagger: same slot hour ({c_when.hour:02d}:00) as sibling on page {s.get('page_id')}")
        cmp.append(row)
    return {"allow": not reasons, "reasons": reasons, "comparisons": cmp, "thresholds": th,
            "checked": len(cmp)}
