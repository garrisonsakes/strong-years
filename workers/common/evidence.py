"""EVIDENCE.md lookups (study-card citations must match EVIDENCE.md exactly: SAFETY_RULES V-03)."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from common import config


@lru_cache(maxsize=1)
def rows() -> dict[str, dict]:
    try:
        txt = Path(config.EVIDENCE_PATH).read_text()
    except OSError:
        return {}
    out = {}
    for line in txt.splitlines():
        m = re.match(r"^\| (E\d{2}b?) \|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        finding = cells[0] if cells else ""
        grade = cells[1] if len(cells) > 1 else ""
        source = cells[2] if len(cells) > 2 else ""
        citation = re.split(r"\s+[—–-]\s+https?://", source)[0].strip()
        out[m.group(1)] = {"id": m.group(1), "finding": finding, "grade": grade, "source": source, "citation": citation}
    return out


def citation(eid: str | None) -> str | None:
    if not eid:
        return None
    r = rows().get(eid)
    return r["citation"] if r else None
