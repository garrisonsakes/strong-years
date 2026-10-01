#!/usr/bin/env python3
"""Prepare (and optionally import) the n8n workflows with every publishing and spend node DISABLED unless
LAUNCH_MODE=live. The repo's workflow files are never modified; prepared copies go to deploy/n8n/prepared/.

  python3 deploy/scripts/n8n_import.py            # prepare + report (default; imports nothing)
  python3 deploy/scripts/n8n_import.py --apply    # also: docker compose exec n8n n8n import:workflow …
Exit 1 if a node that publishes or spends would be enabled while LAUNCH_MODE != live.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deploy" / "n8n" / "prepared"
WORKFLOWS = ["n8n_core_workflow.json", "n8n_growth_workflow.json"]
NAME_RX = re.compile(r"publisher tick|ig: create reel|ig: publish|tiktok: direct post|yt: init|yt: upload|upload-post: publish|"
                     r"governor execute|governor: execute|boost: launch|ads? api", re.I)
URL_RX = re.compile(r"media_publish|/media\b|open\.tiktokapis\.com/v2/post|googleapis\.com/upload|upload-post\.com|"
                    r"/growth/governor/execute|graph\.facebook\.com/[^ ]*/(ads|adsets|campaigns)", re.I)


def gated(node: dict) -> bool:
    url = json.dumps(node.get("parameters", {}).get("url", ""))
    return bool(NAME_RX.search(node.get("name", "")) or URL_RX.search(url))


def prepare(live: bool) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"launch_mode": "live" if live else "not live", "workflows": {}}
    for wf in WORKFLOWS:
        data = json.loads((ROOT / wf).read_text(encoding="utf-8"))
        names = []
        for n in data["nodes"]:
            if gated(n):
                names.append(n["name"])
                if live:
                    n.pop("disabled", None)
                else:
                    n["disabled"] = True
        data["active"] = False      # a person activates each workflow in the n8n UI after a look
        (OUT / wf).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["workflows"][wf] = {"gated_nodes": names, "state": "enabled" if live else "disabled"}
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    live = os.environ.get("LAUNCH_MODE", "prelaunch") == "live"
    rep = prepare(live)
    print(json.dumps(rep, indent=2))
    for wf in WORKFLOWS:
        data = json.loads((OUT / wf).read_text(encoding="utf-8"))
        if not live and any(gated(n) and not n.get("disabled") for n in data["nodes"]):
            print(f"refusing: {wf} has an enabled publishing/spend node", file=sys.stderr)
            return 1
    if a.apply:
        for wf in WORKFLOWS:
            cmd = ["docker", "compose", "-f", str(ROOT / "deploy/docker-compose.yml"), "exec", "-T", "n8n",
                   "n8n", "import:workflow", f"--input=/prepared/{wf}"]
            print("+", " ".join(cmd))
            subprocess.run(cmd, check=True)
    else:
        print("prepared only (use --apply to import into the running n8n container)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
