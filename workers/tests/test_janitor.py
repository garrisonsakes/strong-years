"""common/janitor: stale job dirs and old rendered media are reaped; databases and fresh work are kept;
the assembler's headroom guard refuses a job on a nearly full disk."""
from __future__ import annotations

import os
import time

import pytest

from common import config, janitor


def _age(p, hours):
    t = time.time() - hours * 3600
    os.utime(p, (t, t))


def test_sweep_reaps_only_stale_work_and_old_media(tmp_path, monkeypatch):
    work, out = tmp_path / "work", tmp_path / "out"
    monkeypatch.setattr(config, "WORK_DIR", work)
    monkeypatch.setattr(config, "OUTPUT_DIR", out)
    old_job = work / "asm_old"; old_job.mkdir(parents=True)
    (old_job / "seg_00.mp4").write_bytes(b"x" * 1000); _age(old_job / "seg_00.mp4", 10); _age(old_job, 10)
    live_job = work / "asm_live"; live_job.mkdir()
    (live_job / "seg_00.mp4").write_bytes(b"x"); _age(live_job, 10)          # dir is old, but a file inside is fresh
    (out / "masters").mkdir(parents=True)
    old_mp4, new_mp4 = out / "masters/a.mp4", out / "masters/b.mp4"
    db, js = out / "dm/dm.sqlite3", out / "masters/a.json"
    db.parent.mkdir()
    for f in (old_mp4, new_mp4, db, js):
        f.write_bytes(b"y" * 10)
    for f in (old_mp4, db, js):
        _age(f, 24 * 30)
    r = janitor.sweep()
    assert not old_job.exists() and live_job.exists()
    assert not old_mp4.exists() and new_mp4.exists() and db.exists() and js.exists()
    assert r["work_dirs_removed"] == 1 and r["output_files_removed"] == 1 and r["bytes_freed"] == 1010


def test_headroom_refuses_when_disk_is_nearly_full(tmp_path):
    assert janitor.headroom(tmp_path, min_gb=0) >= 0
    with pytest.raises(janitor.DiskFull):
        janitor.headroom(tmp_path, min_gb=10 ** 9)
