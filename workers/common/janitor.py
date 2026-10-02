"""Disk janitor for the ops box. At 300-458 renders a day the assembly worker writes roughly 10-25 GB/day
(job dirs with segments, WAVs and frames, plus masters in OUTPUT_DIR); without cleanup a 160 GB disk fills
in about a week and every render, n8n run and Postgres write fails at once.

  * WORK_DIR: job dirs older than WORK_TTL_HOURS (default 6) are removed. QA and packaging read them within
    minutes of the render, so 6 h is a wide margin.
  * OUTPUT_DIR: rendered media (mp4/mov/wav/mp3/m4a/png/jpg/jpeg/webp) older than OUTPUT_TTL_DAYS (default 7)
    is removed. Posting happens within 48 h of render; R2 (when enabled) keeps the durable copy. Databases,
    JSON, CSV and logs are never touched.
  * headroom(): free space check the assembler runs before each job (MIN_FREE_GB: 2 GB default, 15 GB on the ops box via compose), so a full
    disk fails one render loudly instead of corrupting Postgres.

Run from the host cron: `docker compose exec -T workers python3 -m common.janitor` (deploy/README.md).
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

from common import config

MEDIA_EXT = {".mp4", ".mov", ".wav", ".mp3", ".m4a", ".png", ".jpg", ".jpeg", ".webp"}


def _f(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


def free_gb(path: Path) -> float:
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    return shutil.disk_usage(p).free / 1e9


class DiskFull(RuntimeError):
    pass


def headroom(path: Path | None = None, min_gb: float | None = None) -> float:
    need = _f("MIN_FREE_GB", 2) if min_gb is None else min_gb
    have = free_gb(path or config.WORK_DIR)
    if have < need:
        raise DiskFull(f"disk: {have:.1f} GB free < {need:.0f} GB (MIN_FREE_GB); run common.janitor or grow the volume")
    return have


def sweep(now: float | None = None, work_ttl_h: float | None = None, output_ttl_d: float | None = None) -> dict:
    now = time.time() if now is None else now
    work_cut = now - 3600 * (_f("WORK_TTL_HOURS", 6) if work_ttl_h is None else work_ttl_h)
    out_cut = now - 86400 * (_f("OUTPUT_TTL_DAYS", 7) if output_ttl_d is None else output_ttl_d)
    r = {"work_dirs_removed": 0, "work_files_removed": 0, "output_files_removed": 0, "bytes_freed": 0}

    work = Path(config.WORK_DIR)
    if work.is_dir():
        for child in work.iterdir():
            try:
                if child.is_symlink():
                    continue
                newest = max([child.stat().st_mtime] + [f.stat().st_mtime for f in child.rglob("*") if f.is_file()]) \
                    if child.is_dir() else child.stat().st_mtime
                if newest >= work_cut:
                    continue
                size = sum(f.stat().st_size for f in child.rglob("*") if f.is_file()) if child.is_dir() else child.stat().st_size
                if child.is_dir():
                    shutil.rmtree(child)
                    r["work_dirs_removed"] += 1
                else:
                    child.unlink()
                    r["work_files_removed"] += 1
                r["bytes_freed"] += size
            except FileNotFoundError:
                continue

    out = Path(config.OUTPUT_DIR)
    if out.is_dir():
        for f in out.rglob("*"):
            try:
                if f.is_file() and not f.is_symlink() and f.suffix.lower() in MEDIA_EXT and f.stat().st_mtime < out_cut:
                    r["bytes_freed"] += f.stat().st_size
                    f.unlink()
                    r["output_files_removed"] += 1
            except FileNotFoundError:
                continue
    r["free_gb"] = round(free_gb(work if work.exists() else out), 1)
    return r


if __name__ == "__main__":  # pragma: no cover - CLI
    res = sweep()
    print(json.dumps(res))
    sys.exit(2 if res["free_gb"] < _f("MIN_FREE_GB", 2) else 0)
