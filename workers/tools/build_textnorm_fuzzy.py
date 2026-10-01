"""Regenerate `fuzzy_exclude` in compliance/textnorm_data.json (dev-time only; needs `pip install wordfreq`).

The runtime fuzzy fold maps a token within edit distance 1 of a blocked stem (stems >= 5 letters) onto that stem,
unless the token is itself a real word. This script lists those real words: every lowercase a–z string at edit distance
1 (incl. adjacent transposition) of a stem whose English or Spanish Zipf frequency is >= 1.0 (e.g. 'cares', 'curas', 'heels'). The list is committed,
so the workers, the n8n nodes and build_content.py need no dictionary at runtime.
Run: python -m tools.build_textnorm_fuzzy
"""
from __future__ import annotations

import json
import string
from pathlib import Path

from wordfreq import zipf_frequency

DATA = Path(__file__).resolve().parent.parent / "compliance" / "textnorm_data.json"


def edits1(w: str) -> set[str]:
    letters = string.ascii_lowercase
    splits = [(w[:i], w[i:]) for i in range(len(w) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    replaces = [a + c + b[1:] for a, b in splits if b for c in letters]
    inserts = [a + c + b for a, b in splits for c in letters]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    return set(deletes + replaces + inserts + transposes)


def main() -> dict:
    d = json.loads(DATA.read_text())
    stems = [s for s in d["stems"] + d.get("fuzzy_extra_stems", []) if len(s) >= d.get("fuzzy_min_len", 5)]
    excl = set()
    for s in stems:
        for w in edits1(s):
            if w != s and (zipf_frequency(w, "en") >= 1.0 or zipf_frequency(w, "es") >= 1.0):
                excl.add(w)
    d["fuzzy_exclude"] = sorted(excl - set(d["stems"]))
    DATA.write_text(json.dumps(d, ensure_ascii=True, indent=1))
    return {"stems": len(stems), "excluded_real_words": len(d["fuzzy_exclude"])}


if __name__ == "__main__":
    print(main())
