#!/usr/bin/env python3
"""Go / no-go before the first real post. Offline: reads local files and env only, sends nothing.

  python3 tools/preflight.py [--secrets deploy/secrets.env]      exit 1 while anything is NO-GO

Repo checks (launch gate, content build) prove the code is ready; this script also checks what lives outside git
and what only Garrison can supply, so "ready" means ready on the machine that will run launch day.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    tail = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode == 0, (tail[-1] if tail else "")


def checks(secrets: Path) -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []
    posts = ROOT / "data" / "posts.csv"
    transcripts = list((ROOT / "data" / "transcripts").glob("*.json"))
    out.append(("competitor corpus (data/posts.csv + data/transcripts/)", posts.exists() and len(transcripts) > 0,
                "present" if posts.exists() else "missing: the plagiarism guard has nothing to compare against. Copy the "
                "POSTDB data (POSTDB_FINDINGS.md) into data/ on this machine"))
    seeds = [ROOT / "production/refs/out/concepts" / f for f in ("chang_a.png", "chang_b.png", "sun_a.png")]
    out.append(("approved character faces (production/refs/out/concepts/)", all(p.exists() for p in seeds),
                "present" if all(p.exists() for p in seeds) else "missing: run the render bake-off and approve faces"))
    ok, msg = _run([sys.executable, "tools/launch_gate.py", "--skip-briefs"])
    out.append(("launch gate (keywords, corpus, captions)", ok, msg))
    if secrets.exists():
        ok, msg = _run([sys.executable, "deploy/scripts/check_secrets.py", "--level", "L", str(secrets)])
        out.append((f"launch secrets ({secrets.relative_to(ROOT) if secrets.is_relative_to(ROOT) else secrets})", ok, msg))
    else:
        out.append(("launch secrets", False, f"{secrets} not found: fill it from deploy/secrets.example.env"))
    ok, msg = _run([sys.executable, "deploy/scripts/check_secrets.py", "--repo-only"])
    out.append(("no secrets tracked in git", ok, msg))
    return out


MANUAL = [
    "Shopify store created (never K9SUPPS), Subscriptions app installed, `npm run provision:live` done, 7-day trial verified with a dev-store test order",
    "Members app deployed (LAUNCH_MODE=live), Supabase migrated, Resend domain verified",
    "IG pages created by Garrison, AI-generated label on, bios from production/bios.md, Threads/X linked",
    "TikTok accounts created (manual posting until the API audit passes); FB page and YT channel named and created",
    "Ops box up (deploy/README.md 'Capacity'), cron installed, /health/details shows disk_free_gb and ffmpeg true",
    "Reviewer sign-off (attorney, PT/dietitian, cultural): REVIEWER_SIGNED=1",
    "YouTube quota request filed (docs/platform_reviews/youtube_api_compliance.md); 4/day until granted",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secrets", type=Path, default=ROOT / "deploy" / "secrets.env")
    a = ap.parse_args(argv)
    res = checks(a.secrets)
    for name, ok, msg in res:
        print(f"{'GO   ' if ok else 'NO-GO'}  {name}: {msg}")
    print("\nConfirm by hand (these cannot be checked offline):")
    for m in MANUAL:
        print(f"  [ ] {m}")
    bad = sum(not ok for _, ok, _ in res)
    print(f"\n{'READY: all automated checks GO' if not bad else f'NOT READY: {bad} automated check(s) NO-GO'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
