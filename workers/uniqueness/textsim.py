"""Embedding-free script similarity: TF-IDF cosine, MinHash (5-word shingles) Jaccard estimate, and the longest
shared word run (PIPELINE §2.3 guard 2: > 6 consecutive shared words is a copy; safety lines and CTA lines excepted)."""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from common import disclosure

STOP = set("a an the and or but if to of in on at for with is are was were be been it its this that these those you "
           "your i me my we our he she him her they them his their as by so do does did not no yes just".split())
SAFETY_LINE_RX = re.compile(
    r"(stop if|hold (a|the) (counter|chair)|ask your doctor|check with your doctor|breathe out|go at your own pace|"
    r"not medical advice|ai characters?|comment [A-Z]{3,}|kidney disease|blood thinners?)", re.I)


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", (text or "").lower())


def strip_safety(text: str) -> str:
    for f in disclosure.all_footers() + list(disclosure.MOVEMENT_ADDON.values()):
        text = text.replace(f, " ")
    sents = re.split(r"(?<=[.!?])\s+", text or "")
    return " ".join(s for s in sents if not SAFETY_LINE_RX.search(s))


def tfidf_cosine(a: str, b: str, corpus: list[str] | None = None) -> float:
    docs = [tokens(a), tokens(b)] + [tokens(c) for c in (corpus or [])]
    n = len(docs)
    df = Counter(t for d in docs for t in set(d))
    def vec(d):
        tf = Counter(t for t in d if t not in STOP)
        return {t: (1 + math.log(c)) * (math.log((1 + n) / (1 + df[t])) + 1) for t, c in tf.items()}
    va, vb = vec(docs[0]), vec(docs[1])
    dot = sum(va[t] * vb.get(t, 0.0) for t in va)
    na = math.sqrt(sum(v * v for v in va.values()))
    nb = math.sqrt(sum(v * v for v in vb.values()))
    return round(dot / (na * nb), 4) if na and nb else 0.0


def shingles(text: str, k: int = 5) -> set[str]:
    t = tokens(text)
    return {" ".join(t[i:i + k]) for i in range(max(0, len(t) - k + 1))} or ({" ".join(t)} if t else set())


def minhash(text: str, num_perm: int = 128, k: int = 5) -> list[int]:
    sh = shingles(text, k)
    if not sh:
        return [2 ** 64 - 1] * num_perm
    sig = []
    for i in range(num_perm):
        salt = i.to_bytes(4, "little")
        sig.append(min(int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8, salt=salt).digest(), "little")
                       for s in sh))
    return sig


def minhash_jaccard(a: str, b: str, num_perm: int = 128) -> float:
    sa, sb = minhash(a, num_perm), minhash(b, num_perm)
    return round(sum(x == y for x, y in zip(sa, sb)) / num_perm, 4)


def longest_shared_run(a: str, b: str) -> tuple[int, str]:
    ta, tb = tokens(strip_safety(a)), tokens(strip_safety(b))
    best, end = 0, 0
    prev = [0] * (len(tb) + 1)
    for i in range(1, len(ta) + 1):
        cur = [0] * (len(tb) + 1)
        for j in range(1, len(tb) + 1):
            if ta[i - 1] == tb[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best, end = cur[j], i
        prev = cur
    return best, " ".join(ta[end - best:end])
