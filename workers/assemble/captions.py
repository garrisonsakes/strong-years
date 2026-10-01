"""Word timings -> caption chunks (word-by-word highlight), per CHARACTERS.md §13.2 / SAFETY_RULES V-04."""
from __future__ import annotations

import re
from dataclasses import dataclass

TAG_RX = re.compile(r"\[[^\]]*\]")


@dataclass
class Word:
    text: str
    start: float
    end: float


@dataclass
class Chunk:
    words: list[Word]
    start: float
    end: float

    @property
    def text(self) -> str:
        return " ".join(w.text for w in self.words)


def clean_words(raw: list[dict]) -> list[Word]:
    out = []
    for w in raw or []:
        t = TAG_RX.sub("", str(w.get("word") or w.get("text") or "")).strip()
        if not t:
            continue
        s = float(w.get("start_s", w.get("start", 0.0)))
        e = float(w.get("end_s", w.get("end", s + 0.2)))
        out.append(Word(t, s, max(e, s + 0.05)))
    out.sort(key=lambda w: w.start)
    return out


def chunk_words(words: list[Word], max_words: int = 4, max_chars: int = 26, max_gap: float = 0.6,
                hold: float = 0.35) -> list[Chunk]:
    """Group words into short caption chunks. Break on sentence punctuation, long pauses, word/char limits."""
    chunks: list[list[Word]] = []
    cur: list[Word] = []
    for w in words:
        if cur:
            gap = w.start - cur[-1].end
            chars = len(" ".join(x.text for x in cur + [w]))
            if len(cur) >= max_words or chars > max_chars or gap > max_gap or re.search(r"[.!?]$", cur[-1].text):
                chunks.append(cur)
                cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)
    out: list[Chunk] = []
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1][0].start if i + 1 < len(chunks) else None
        end = c[-1].end + hold
        if nxt is not None:
            end = min(end, nxt)
        out.append(Chunk(c, c[0].start, max(end, c[-1].end)))
    return out


def word_states(chunks: list[Chunk]) -> list[tuple[float, float, int, int]]:
    """[(start, end, chunk_index, active_word_index)] covering each chunk's lifetime."""
    states = []
    for ci, c in enumerate(chunks):
        for wi, w in enumerate(c.words):
            s = w.start if wi else c.start
            e = c.words[wi + 1].start if wi + 1 < len(c.words) else c.end
            if e > s:
                states.append((s, e, ci, wi))
    return states
