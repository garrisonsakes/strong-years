"""Manual fallback post pack: when API publishing is off, blocked (app audits pending) or down, a person posts by hand
from this pack. One folder per day → page → platform, plus two bulk-scheduling CSVs.

Each item is one platform VARIANT as the uniqueness worker approved it (variant_id, uniqueness.allow == True, its own
hook/cover/trim per platform). Items the uniqueness guard denied, or whose caption or first comment doesn't pass the
deterministic compliance scan, or that lack the AI flag, are HELD (listed in held.csv with the reason) and never
packed. Nothing here posts, schedules or uploads anything.

  out/packs/<day>/<page>/<platform>/
      video.txt          where the approved variant file is (path or URL) + checksum when local
      caption.txt        exact caption (footer and disclosure included by /package)
      hashtags.txt       one per line
      first_comment.txt  the pinned/first comment (never a link on X)
      checklist.md       the manual steps incl. the platform's AI label
  out/packs/<day>/meta_business_suite.csv   bulk-schedule rows for Facebook + Instagram
  out/packs/<day>/buffer.csv                 bulk-schedule rows for Buffer (TikTok, YouTube, Threads, X…)
  out/packs/<day>/held.csv                   items not packed, with the reason
  out/packs/<day>/manifest.json

CSV headers follow each tool's bulk-upload template as of Oct 2026; download the current template in Business
Suite (Planner → Bulk upload) and Buffer (Publish → Bulk import) and compare headers before the first upload.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from compliance import caption_rules, scanner

AI_LABEL = {
    "ig": "Instagram: tap 'Advanced settings' → turn ON 'AI info' (Add AI label). The account bio already says AI characters.",
    "fb": "Facebook: in the composer turn ON 'AI info' / 'Made with AI'. Keep the AI-character line in the caption.",
    "tt": "TikTok: More options → turn ON 'AI-generated content'. Keep the caption disclosure.",
    "yt": "YouTube Studio: 'Altered or synthetic content' → YES. Keep the description disclosure.",
    "th": "Threads: keep the AI-character line in the post text (no separate label control as of Oct 2026; check the composer).",
    "x": "X: keep the AI-character line in the post; no link in the post body (link goes in the bio).",
}
PLATFORM_NAME = {"ig": "Instagram", "fb": "Facebook", "tt": "TikTok", "yt": "YouTube", "th": "Threads", "x": "X"}
SAFE_ID = re.compile(r"^[A-Za-z0-9_.@-]{1,80}$")


def _hold_reason(it: dict) -> str | None:
    if not SAFE_ID.match(str(it.get("page", ""))) or str(it.get("platform")) not in AI_LABEL:
        return "bad page or platform"
    u = it.get("uniqueness") or {}
    if u.get("allow") is not True:
        return "uniqueness guard did not allow this variant: " + "; ".join(map(str, u.get("reasons", [])))[:200]
    if not it.get("variant_id"):
        return "no uniqueness-approved variant_id"
    if not it.get("is_aigc", False):
        return "AI flag missing (is_aigc must be true)"
    for field in ("caption", "first_comment"):
        text = it.get(field) or ""
        if text and scanner.scan(text=text)["verdict"] != "pass":
            return f"{field} does not pass the compliance scan"
    if it.get("platform") == "x" and re.search(r"https?://", (it.get("caption") or "") + (it.get("first_comment") or "")):
        return "link in an X post"
    bad = caption_rules.foreign_handles((it.get("caption") or "") + "\n" + (it.get("first_comment") or ""))
    if bad:
        return "caption mentions handles that are not ours (SL-06.5): " + ", ".join(bad)
    if "AI" not in (it.get("caption") or ""):
        return "caption lacks the AI-character disclosure"
    return None


def checklist(it: dict) -> str:
    p = it["platform"]
    return "\n".join([
        f"# {PLATFORM_NAME[p]} · {it['page']} · {it.get('scheduled_at', 'time: see calendar')}",
        "",
        f"Variant: {it['variant_id']} (uniqueness-approved for {PLATFORM_NAME[p]}; do not swap in another platform's file)",
        "",
        "- [ ] Open video.txt and download/attach exactly that file.",
        "- [ ] Paste caption.txt unchanged (the disclosure and footer are part of it).",
        "- [ ] Add hashtags.txt (already in the caption where the platform needs it; do not add trending tags).",
        f"- [ ] {AI_LABEL[p]}",
        "- [ ] Cover: use the variant's cover frame (the AI-character tag must be visible).",
        "- [ ] Post at the scheduled time (the 48 h sibling stagger is already applied).",
        "- [ ] Paste first_comment.txt as the first comment and pin it." if p in ("ig", "fb", "tt", "yt", "th") else
        "- [ ] Post first_comment.txt as a reply in the thread (no link).",
        "- [ ] Trial or feed: post exactly as the slot says (trial = Instagram 'Trial' toggle ON; feed = OFF).",
        "- [ ] Do NOT use Instagram's 'Share to Facebook' toggle or any cross-post option: each platform gets its own file.",
        "- [ ] More than 30 min past the slot? Skip it and write 'skipped' in posted_log.csv. Never post late.",
        "- [ ] Fill one row in posted_log.csv: posted_at, the live permalink (required), your name, trial y/n, AI label y/n.",
        "- [ ] Never reply to comments as Chang Yin or Sun Yoon in the first person about personal pain; crisis words → the safety protocol.",
        "",
    ])


def build_pack(day: str, items: list[dict], out_root: Path) -> dict:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
        raise ValueError("day must be YYYY-MM-DD")
    root = Path(out_root) / day
    root.mkdir(parents=True, exist_ok=True)
    packed, held = [], []
    meta_rows, buffer_rows = [], []
    log_rows = []
    for it in items:
        it = dict(it)
        rewrites = []
        for field in ("caption", "first_comment"):
            if isinstance(it.get(field), str):
                it[field], notes = caption_rules.rewrite_time_words(it[field])
                rewrites += notes
        why = _hold_reason(it)
        if why:
            held.append({"post_id": it.get("post_id", ""), "page": it.get("page", ""), "platform": it.get("platform", ""), "reason": why})
            continue
        d = root / it["page"] / it["platform"]
        d.mkdir(parents=True, exist_ok=True)
        src = str(it.get("video") or "")
        sha = ""
        if src and not src.startswith("http") and Path(src).is_file():
            sha = hashlib.sha256(Path(src).read_bytes()).hexdigest()
        (d / "video.txt").write_text(f"{src}\n{('sha256 ' + sha) if sha else ''}\n", encoding="utf-8")
        (d / "caption.txt").write_text(it.get("caption", ""), encoding="utf-8")
        (d / "hashtags.txt").write_text("\n".join(it.get("hashtags") or []) + "\n", encoding="utf-8")
        (d / "first_comment.txt").write_text(it.get("first_comment", ""), encoding="utf-8")
        (d / "checklist.md").write_text(checklist(it), encoding="utf-8")
        packed.append({"post_id": it.get("post_id"), "page": it["page"], "platform": it["platform"], "variant_id": it["variant_id"],
                       "dir": str(d.relative_to(root)), "caption_rewrites": rewrites})
        log_rows.append({"post_id": it.get("post_id", ""), "page": it["page"], "platform": it["platform"],
                         "variant_id": it["variant_id"], "scheduled_at": it.get("scheduled_at", ""),
                         "trial": "y" if it.get("trial") else "n", "status": "due"})
        when = it.get("scheduled_at", "")
        if it["platform"] in ("ig", "fb"):
            meta_rows.append([PLATFORM_NAME[it["platform"]], it["page"], when, it.get("caption", ""), src, it.get("first_comment", ""), it["variant_id"]])
        else:
            buffer_rows.append([it.get("caption", ""), src, PLATFORM_NAME[it["platform"]], it["page"], when, it["variant_id"]])
    with (root / "meta_business_suite.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Platform", "Page", "Scheduled time", "Text", "Video URL", "First comment", "Variant ID"])
        w.writerows(meta_rows)
    with (root / "buffer.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Text", "Video URL", "Channel", "Profile", "Posting Time", "Variant ID"])
        w.writerows(buffer_rows)
    with (root / "held.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["post_id", "page", "platform", "reason"])
        w.writeheader()
        w.writerows(held)
    write_posted_log_template(root / "posted_log.csv", log_rows)
    manifest = {"day": day, "packed": packed, "held": held, "meta_rows": len(meta_rows), "buffer_rows": len(buffer_rows)}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- posted log (SAVAGE20 #4 minimal slice)
POSTED_LOG_FIELDS = ["post_id", "page", "platform", "variant_id", "scheduled_at", "trial", "status", "posted_at",
                     "permalink", "posted_by", "ai_label", "notes"]
PERMALINK_HOSTS = {"ig": ("instagram.com",), "fb": ("facebook.com", "fb.watch", "fb.com"), "tt": ("tiktok.com",),
                   "yt": ("youtube.com", "youtu.be"), "th": ("threads.net", "threads.com"), "x": ("x.com", "twitter.com")}
SKIP_AFTER_MIN = 30


def write_posted_log_template(path: Path, rows: list[dict]) -> None:
    """One row per packed placement; the poster fills posted_at, permalink, posted_by, ai_label (or status=skipped)."""
    with Path(path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=POSTED_LOG_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in POSTED_LOG_FIELDS})


def _ts(x: str):
    from datetime import datetime
    return datetime.fromisoformat(str(x).strip().replace("Z", "+00:00"))


def read_posted_log(path: Path) -> dict:
    """Validate a filled posted_log.csv -> {posted: [...], skipped: [...], problems: [...]}.

    status=posted needs posted_at (ISO with offset), an https permalink on that platform's host, posted_by and
    ai_label=y. Posting more than 30 min after the slot is reported as a problem (the rule is skip, not late).
    posted rows carry external_post_id = the permalink path's last segment, for posts.external_post_id, manual metrics
    import (growth/manual_import.py) and attribution."""
    from urllib.parse import urlparse
    out = {"posted": [], "skipped": [], "due": [], "problems": []}
    with Path(path).open(encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f), start=2):
            st = (r.get("status") or "").strip().lower()
            where = f"row {i} {r.get('post_id', '')}/{r.get('platform', '')}"
            if st == "skipped":
                out["skipped"].append(r)
                continue
            if st != "posted":
                out["due"].append(r)
                continue
            u = urlparse((r.get("permalink") or "").strip())
            host = (u.hostname or "").lower()
            if u.scheme != "https" or not any(host == h or host.endswith("." + h) for h in PERMALINK_HOSTS.get(r.get("platform", ""), ())):
                out["problems"].append(f"{where}: permalink missing or not a {r.get('platform')} URL")
                continue
            try:
                posted, sched = _ts(r["posted_at"]), (_ts(r["scheduled_at"]) if r.get("scheduled_at") else None)
                if posted.tzinfo is None:
                    raise ValueError
            except (KeyError, ValueError):
                out["problems"].append(f"{where}: posted_at must be ISO 8601 with a UTC offset")
                continue
            if not (r.get("posted_by") or "").strip():
                out["problems"].append(f"{where}: posted_by is empty")
            if (r.get("ai_label") or "").strip().lower() != "y":
                out["problems"].append(f"{where}: AI label not confirmed (ai_label must be y)")
            if sched and (posted - sched).total_seconds() > SKIP_AFTER_MIN * 60:
                out["problems"].append(f"{where}: posted {int((posted - sched).total_seconds() // 60)} min late (rule: skip after {SKIP_AFTER_MIN})")
            ext = [seg for seg in u.path.split("/") if seg][-1:] or [""]
            out["posted"].append({**r, "posted_at": posted.isoformat(), "external_post_id": ext[0],
                                  "permalink": u.geturl()})
    return out
