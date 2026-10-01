#!/usr/bin/env python3
"""make check-secrets: validates a filled secrets file against secrets.example.env, and the repo against leaks.

  python3 deploy/scripts/check_secrets.py [deploy/secrets.env] [--level R|L] [--repo-only]
Checks: (1) every key marked R (or R+L with --level L) is set; no placeholder values; self-generated tokens are 32+
chars; (2) secrets.example.env holds no values; (3) no secrets file or key material is tracked by git and no tracked
file contains a live-looking key string. Prints key NAMES only, never values.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "deploy" / "secrets.example.env"
LONG = {"WORKER_TOKEN", "EXCEPTIONS_API_TOKEN", "GROWTH_API_TOKEN", "CRON_SECRET", "SESSION_SECRET", "N8N_ENCRYPTION_KEY"}
PLACEHOLDER = re.compile(r"^(changeme|change_me|todo|xxx+|placeholder|your[-_].*|<.*>|\.\.\.)$", re.I)
KEY_PATTERNS = [
    ("anthropic", r"sk-ant-[A-Za-z0-9_-]{20,}"), ("openai-style", r"\bsk-[A-Za-z0-9]{32,}"),
    ("shopify", r"shp(at|ss|ca|pa)_[a-f0-9]{32}"), ("stripe-live", r"\b[sr]k_live_[A-Za-z0-9]{16,}"),
    ("aws", r"\bAKIA[0-9A-Z]{16}\b"), ("slack-webhook", r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]{20,}"),
    ("private-key", r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), ("google", r"AIza[0-9A-Za-z_-]{35}"),
    ("github", r"gh[pousr]_[A-Za-z0-9]{36}"), ("resend", r"\bre_[A-Za-z0-9]{20,}"),
    ("supabase-jwt", r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}"),
]


def parse(path: Path) -> dict[str, tuple[str, str]]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Z][A-Z0-9_]*)=([^#]*?)\s*(#\s*([RLO])\b.*)?$", line.strip())
        if m:
            out[m.group(1)] = (m.group(2).strip().strip('"').strip("'"), m.group(4) or "O")
    return out


def check_file(path: Path, level: str) -> list[str]:
    spec, have, errs = parse(EXAMPLE), parse(path), []
    need = {"R"} if level == "R" else {"R", "L"}
    for k, (_, lvl) in spec.items():
        v = have.get(k, ("", ""))[0]
        if lvl in need and not v:
            errs.append(f"missing {k} ({lvl})")
        elif v and PLACEHOLDER.match(v):
            errs.append(f"placeholder value for {k}")
        elif v and k in LONG and len(v) < 32:
            errs.append(f"{k} shorter than 32 characters")
    return errs


def check_repo() -> list[str]:
    errs = [f"secrets.example.env has a value for {k}" for k, (v, _) in parse(EXAMPLE).items() if v]
    try:
        files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return errs + ["not a git repository (skipped tracked-file scan)"]
    for f in files:
        name = Path(f).name
        if name in (".env", "secrets.env") or name.endswith((".pem", ".key", ".p12")) or (name.startswith(".env") and name != ".env.example"):
            errs.append(f"tracked secrets/key file: {f}")
            continue
        p = ROOT / f
        if not p.is_file() or p.stat().st_size > 2_000_000 or p.suffix in (".png", ".jpg", ".pdf", ".mp4", ".xlsx", ".pkl", ".ttf", ".woff2", ".task"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, rx in KEY_PATTERNS:
            if re.search(rx, text):
                errs.append(f"{f}: looks like a {label} key")
    return errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", default=str(ROOT / "deploy" / "secrets.env"))
    ap.add_argument("--level", choices=["R", "L"], default="R")
    ap.add_argument("--repo-only", action="store_true")
    a = ap.parse_args(argv)
    errs = check_repo()
    if not a.repo_only:
        p = Path(a.file)
        errs += check_file(p, a.level) if p.is_file() else [f"{p} not found (copy deploy/secrets.example.env and fill it)"]
    for e in errs:
        print("FAIL", e)
    print("check-secrets:", "OK" if not errs else f"{len(errs)} problem(s)")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
