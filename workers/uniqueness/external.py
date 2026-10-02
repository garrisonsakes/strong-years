"""Competitor-corpus similarity gate (ENGINE_SAVAGE20 §B(b) item 2, SL-22.1).

Every script / caption we ship is compared with what the niche already published: data/posts.csv (captions, hook
lines, overlay text), data/transcripts/*.json (Whisper transcripts of the reference creator) and `niche_posts`
rows from the discover crawler (a JSONL export or rows passed in). It FAILS when either
  - a 7-word shingle is shared with any corpus document (safety lines, the footer and CTA lines excepted), or
  - TF-IDF cosine (IDF over the whole corpus) against any one document is >= COSINE_MAX.
Remakes reuse the idea and the gene, never the words (discover/remake.py), and this is the check that proves it.
Offline: reads local files only.
"""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

from uniqueness import textsim

SHINGLE_K = 7
COSINE_MAX = 0.50
ROOT = Path(__file__).resolve().parents[2]
csv.field_size_limit(10 ** 8)


def _shingles(text: str, k: int = SHINGLE_K) -> set[str]:
    t = textsim.tokens(text)
    return {" ".join(t[i:i + k]) for i in range(len(t) - k + 1)}


def load_corpus(root: Path | None = None, niche_rows: list[dict] | None = None) -> list[dict]:
    """[{id, source, text}] from posts.csv, transcripts and niche_posts (data/discover/niche_posts.jsonl if present)."""
    root = Path(root or ROOT)
    docs: list[dict] = []
    p = root / "data" / "posts.csv"
    if p.is_file():
        with p.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                text = " ".join(r.get(k) or "" for k in ("hook_line", "title_or_caption", "overlay_text", "transcript"))
                if text.strip():
                    docs.append({"id": r.get("id") or "", "source": f"posts.csv:{r.get('account', '')}", "text": text})
    for t in sorted((root / "data" / "transcripts").glob("*.json")):
        try:
            text = json.loads(t.read_text(encoding="utf-8")).get("text") or ""
        except (ValueError, OSError):
            continue
        if text.strip():
            docs.append({"id": t.stem, "source": "transcript", "text": text})
    rows = list(niche_rows or [])
    nj = root / "data" / "discover" / "niche_posts.jsonl"
    if nj.is_file():
        rows += [json.loads(line) for line in nj.read_text(encoding="utf-8").splitlines() if line.strip()]
    for r in rows:
        text = " ".join(str(r.get(k) or "") for k in ("hook_line", "title_or_caption", "overlay_text", "transcript"))
        if text.strip():
            docs.append({"id": str(r.get("external_id") or r.get("id") or ""), "source": "niche_posts", "text": text})
    return docs


class CorpusIndex:
    """Precomputed shingles and TF-IDF vectors so 300 briefs × ~300 documents stays well under a second each."""

    def __init__(self, docs: list[dict]):
        self.docs = docs
        toks = [textsim.tokens(d["text"]) for d in docs]
        self.n = len(docs) + 1
        self.df = Counter(t for d in toks for t in set(d))
        self.vecs = [self._vec(t) for t in toks]
        self.shingle_owner: dict[str, int] = {}
        for i, d in enumerate(docs):
            for s in _shingles(d["text"]):
                self.shingle_owner.setdefault(s, i)

    def _vec(self, toks: list[str]) -> dict[str, float]:
        tf = Counter(t for t in toks if t not in textsim.STOP)
        v = {t: (1 + math.log(c)) * (math.log((1 + self.n) / (1 + self.df.get(t, 0))) + 1) for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def check(self, text: str, cosine_max: float = COSINE_MAX) -> dict:
        body = textsim.strip_safety(text or "")
        shared = sorted(s for s in _shingles(body) if s in self.shingle_owner)
        v = self._vec(textsim.tokens(body))
        best, best_i = 0.0, -1
        for i, dv in enumerate(self.vecs):
            c = sum(x * dv.get(t, 0.0) for t, x in v.items())
            if c > best:
                best, best_i = c, i
        reasons = []
        if shared:
            d = self.docs[self.shingle_owner[shared[0]]]
            reasons.append(f"shares {len(shared)} {SHINGLE_K}-word shingle(s) with {d['source']}:{d['id']} "
                           f"(e.g. '{shared[0]}')")
        if best >= cosine_max:
            d = self.docs[best_i]
            reasons.append(f"TF-IDF cosine {best:.2f} >= {cosine_max} vs {d['source']}:{d['id']}")
        return {"allow": not reasons, "max_cosine": round(best, 4),
                "nearest": (self.docs[best_i]["source"] + ":" + self.docs[best_i]["id"]) if best_i >= 0 else None,
                "shared_shingles": shared[:5], "reasons": reasons}


_DEFAULT: CorpusIndex | None = None


def default_index() -> CorpusIndex:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = CorpusIndex(load_corpus())
    return _DEFAULT


def script_text(s: dict) -> str:
    """Spoken lines + on-screen text + caption of a script/brief/day-1 post (dict beats)."""
    parts = [s.get("hook_line") or ""]
    for b in s.get("beats") or []:
        if isinstance(b, dict):
            parts += [b.get("vo") or "", b.get("ost") or ""]
        else:
            parts += [str(b[2] or ""), str(b[3] or "")]
    parts.append(s.get("caption") or "")
    for v in (s.get("variants") or {}).values():
        if isinstance(v, dict):
            parts.append(v.get("caption") or "")
    return "\n".join(p for p in parts if p)


def check_external(candidate: dict | str, index: CorpusIndex | None = None, cosine_max: float = COSINE_MAX) -> dict:
    text = candidate if isinstance(candidate, str) else script_text(candidate)
    return (index or default_index()).check(text, cosine_max)
