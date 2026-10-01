"""Design the two character voices with ElevenLabs Voice Design. DRY_RUN by default: writes the request plan and
calls nothing. With DRY_RUN=0 and ELEVENLABS_API_KEY it asks for N previews per character (plain HTTP, no SDK) and
saves the audio for a person to pick; the chosen voice is then created and its voice_id locked by hand.
Designed voices only, never cloned from anyone.

  python3 production/voices/design_voices.py
  DRY_RUN=0 ELEVENLABS_API_KEY=... python3 production/voices/design_voices.py --only chang
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
URL = "https://api.elevenlabs.io/v1/text-to-voice/design"


def requests_for(design: dict, only: set[str] | None) -> list[dict]:
    out = []
    for name, v in design["voices"].items():
        if only and name not in only:
            continue
        for n in range(design["candidates"]):
            out.append({"character": name, "candidate": n,
                        "body": {"voice_description": v["description"], "text": v["preview_text"], "seed": 1000 + n,
                                 "model_id": os.environ.get("ELEVEN_TTV_MODEL", "eleven_ttv_v3")}})
    return out


def call(body: dict, key: str) -> list[bytes]:  # pragma: no cover - network, DRY_RUN=0 only
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "xi-api-key": key})
    with urllib.request.urlopen(req, timeout=120) as r:
        j = json.load(r)
    return [base64.b64decode(p["audio_base_64"]) for p in j.get("previews", [])]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    design = json.loads((HERE / "voice_design.json").read_text(encoding="utf-8"))
    only = {x for x in a.only.split(",") if x} or None
    reqs = requests_for(design, only)
    dry = os.environ.get("DRY_RUN", "1") != "0"
    OUT.mkdir(exist_ok=True)
    (OUT / "plan.json").write_text(json.dumps({"dry_run": dry, "requests": reqs}, indent=2), encoding="utf-8")
    print(f"{'DRY RUN: ' if dry else ''}{len(reqs)} voice-design requests -> {OUT / 'plan.json'}")
    if dry:
        return 0
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        print("ELEVENLABS_API_KEY unset; refusing", file=sys.stderr)
        return 2
    for r in reqs:  # pragma: no cover
        for i, audio in enumerate(call(r["body"], key)):
            (OUT / f"{r['character']}_cand{r['candidate']}_{i}.mp3").write_bytes(audio)
    return 0


if __name__ == "__main__":
    sys.exit(main())
