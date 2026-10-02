"""Packager support for the `text_probe` role (ENGINE_SAVAGE20 #2): a hook posted as plain text on Threads or X.

Runs the same deterministic /package rules as a video caption (length limits, no links on X, AI line kept, evergreen
time words, handle allowlist) and returns an item in the fallback-pack shape (packager/fallback.build_pack). There is
no media, so the uniqueness guard's media checks don't apply; the competitor-corpus text gate does.
"""
from __future__ import annotations

from packager.packager import package

KEY = {"th": "threads", "x": "x"}


def package_probe(p: dict, corpus_check=None) -> dict:
    if p.get("platform") not in KEY:
        raise ValueError("text probes go to Threads (th) or X (x) only")
    key = KEY[p["platform"]]
    res = package({key: {"text": p["text"]}}, script={"has_movement": False})
    text = res["packaging"][key]["text"]
    ext = corpus_check(text) if corpus_check else {"allow": True, "reasons": []}
    allow = ext["allow"] and not res["caption_issues"]
    return {"post_id": p["probe_id"], "variant_id": p["probe_id"], "page": p["page"], "platform": p["platform"],
            "role": "text_probe", "caption": text, "hashtags": [], "first_comment": "", "video": "",
            "scheduled_at": p["scheduled_at"], "is_aigc": True, "read_at_h": p.get("read_at_h", 6),
            "uniqueness": {"allow": allow, "reasons": ext["reasons"] + res["caption_issues"]},
            "notes": res["notes"]}
