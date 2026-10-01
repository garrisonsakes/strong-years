"""Render the locked reference pack (refs/manifest.json). DRY_RUN by default: prints and writes the request plan,
calls nothing. With DRY_RUN=0 and GEMINI_API_KEY it calls the Gemini image API over plain HTTP (no SDK); the
Higgsfield path is a stub (its Soul training is a manual step in their app). Spending happens only when a person
runs it with DRY_RUN=0. Every prompt's sha256 is verified against the manifest before anything is sent.

  python3 production/refs/render_refs.py [--only C01,S01] [--candidates 4]
  DRY_RUN=0 GEMINI_API_KEY=... python3 production/refs/render_refs.py --only C01
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
GEMINI_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class Locked(Exception):
    pass


def load_manifest(path: Path = HERE / "manifest.json") -> dict:
    man = json.loads(path.read_text(encoding="utf-8"))
    for it in man["items"]:
        h = hashlib.sha256((it["prompt"] + "\n" + it["negative_prompt"]).encode()).hexdigest()
        if h != it["sha256"]:
            raise Locked(f"{it['id']}: prompt changed since it was locked (sha256 mismatch)")
    return man


def gemini_request(item: dict, ref_images: list[bytes]) -> dict:
    parts = [{"text": f"{item['prompt']}\n\nAvoid: {item['negative_prompt']}"}]
    parts += [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(b).decode()}} for b in ref_images[:5]]
    return {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": item["aspect_ratio"]}}}


def call_gemini(body: dict, key: str) -> list[bytes]:  # pragma: no cover - network, only with DRY_RUN=0
    req = urllib.request.Request(GEMINI_URL.format(model=GEMINI_MODEL), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        j = json.load(r)
    out = []
    for c in j.get("candidates", []):
        for p in (c.get("content") or {}).get("parts", []):
            if "inlineData" in p:
                out.append(base64.b64decode(p["inlineData"]["data"]))
    return out


def higgsfield_stub(item: dict) -> dict:
    """Higgsfield Soul is trained by hand in their app on the locked C01–C10 / S01–S08 picks; no API call here."""
    return {"provider": "higgsfield", "status": "manual", "note": "train Soul on the locked refs in the Higgsfield app"}


def plan(man: dict, only: set[str] | None, candidates: int) -> list[dict]:
    rows = []
    for it in man["items"]:
        if only and it["id"] not in only:
            continue
        rows.append({"id": it["id"], "refs": it["refs_required"], "candidates": candidates, "model": GEMINI_MODEL,
                     "sha256": it["sha256"], "prompt_chars": len(it["prompt"])})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--candidates", type=int, default=4)
    a = ap.parse_args(argv)
    man = load_manifest()
    only = {x.strip() for x in a.only.split(",") if x.strip()} or None
    rows = plan(man, only, a.candidates)
    dry = os.environ.get("DRY_RUN", "1") != "0"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "plan.json").write_text(json.dumps({"dry_run": dry, "jobs": rows}, indent=2), encoding="utf-8")
    print(f"{'DRY RUN: ' if dry else ''}{len(rows)} reference jobs x {a.candidates} candidates -> {OUT / 'plan.json'}")
    if dry:
        return 0
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        print("GEMINI_API_KEY unset; refusing", file=sys.stderr)
        return 2
    items = {it["id"]: it for it in man["items"]}
    for r in rows:  # pragma: no cover - live path
        refs = []
        for rid in r["refs"]:
            p = HERE / "locked" / f"{rid}.png"
            if not p.is_file():
                print(f"{r['id']}: locked ref {rid} missing; generate and lock it first", file=sys.stderr)
                return 3
            refs.append(p.read_bytes())
        for n in range(a.candidates):
            for i, img in enumerate(call_gemini(gemini_request(items[r["id"]], refs), key)):
                (OUT / f"{r['id']}_cand{n}_{i}.png").write_bytes(img)
    return 0


if __name__ == "__main__":
    sys.exit(main())
