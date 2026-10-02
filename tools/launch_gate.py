#!/usr/bin/env python3
"""Launch gate: the offline checks that must be green before anyone posts (ENGINE_SAVAGE20 §B(b) 1–3 and #1).

  python3 tools/launch_gate.py [--ci] [--skip-briefs]       exit 1 on any failure (CI: .github/workflows/ci.yml)

  1. keyword registry  every CTA keyword in the day-1 plan / scripts has a flow and a manual reply (tools/keyword_registry)
  2. competitor corpus each day-1 post (spoken + on-screen + every caption) shares no 7-word shingle with, and has
                       TF-IDF cosine < 0.50 to, any posts.csv / transcript / niche_posts document (uniqueness/external)
  3. caption rules     day-1 captions and first comments: no time-relative words (required safety lines exempt),
                       no @handle outside our allowlist (compliance/caption_rules)
  4. product briefs    tools/product_to_scripts builds >= 300 briefs through the virality gate (skipped with --skip-briefs)
Secrets are a separate step (deploy/scripts/check_secrets.py). Offline; reads local files only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "workers"), str(ROOT / "tools")]

from compliance import caption_rules  # noqa: E402
from uniqueness import external  # noqa: E402

DAY1 = ROOT / "production" / "launch_day" / "day1_plan.json"


def day1_posts(path: Path = DAY1) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["posts"]


def check_keywords() -> list[str]:
    import keyword_registry  # noqa: PLC0415
    return [f"keyword: {e}" for e in keyword_registry.run()["errors"]]


def check_corpus(posts: list[dict], index: external.CorpusIndex | None = None) -> list[str]:
    out = []
    for p in posts:
        r = external.check_external(p, index)
        if not r["allow"]:
            out.append(f"corpus: {p['post_id']}: " + "; ".join(r["reasons"]))
    return out


def check_captions(posts: list[dict]) -> list[str]:
    out = []
    for p in posts:
        fields = [(f"{k}.caption", v.get("caption") or "") for k, v in (p.get("variants") or {}).items()]
        fields += [("first_comment", p.get("first_comment") if isinstance(p.get("first_comment"), str) else
                    json.dumps(p.get("first_comment") or ""))]
        for name, text in fields:
            tw = caption_rules.time_words(text)
            if tw:
                out.append(f"caption: {p['post_id']} {name}: time-relative words {tw} (rewrite to evergreen)")
            fh = caption_rules.foreign_handles(text)
            if fh:
                out.append(f"caption: {p['post_id']} {name}: handles not on the allowlist {fh}")
    return out


def check_briefs(min_n: int = 300) -> list[str]:
    import product_to_scripts  # noqa: PLC0415
    r = product_to_scripts.build(min_n)
    return [] if r["ok"] else [f"briefs: only {r['kept']} passed the gates (need {min_n}); rejected {r['rejected']}"]


def run(briefs: bool = True) -> dict:
    posts = day1_posts()
    fails = check_keywords() + check_corpus(posts) + check_captions(posts) + (check_briefs() if briefs else [])
    return {"ok": not fails, "failures": fails, "posts": len(posts)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ci", action="store_true", help="non-interactive; same checks")
    ap.add_argument("--skip-briefs", action="store_true")
    a = ap.parse_args(argv)
    r = run(briefs=not a.skip_briefs)
    for f in r["failures"]:
        print(" FAIL", f)
    print(f"launch gate: {'OK' if r['ok'] else 'FAILED'} ({r['posts']} day-1 posts, {len(r['failures'])} failures)")
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
