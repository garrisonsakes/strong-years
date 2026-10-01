"""Anti-evasion text normalisation for the claims scanner (AUDIT H10 + AUDIT_FINAL H10 regression).

All tables live in textnorm_data.json, which is shared with the n8n regex Code nodes (embedded by
tools/patch_workflow.py) and with tools/build_content.py, so all three normalise the same way.

canon(t)     NFKC, invisible/format characters stripped, confusables folded, stray combining marks on ASCII
             dropped. This is the text we show and use for structural checks (Spanish accents kept).
variants(t)  canon + match-only folds that the blocked-claim regexes also run over:
             fold     NFKD + strip every combining mark (cüres, Detöx, mírácle, cúres -> ASCII)
             collapse spaced/dotted/dashed single letters (c.u.r.e.s, c — u — r — e — s, c*u*r*e) and 1-char
                      separators inside words (cu_res, de.tox, mir-a-cle)
             masks    a word with mask characters (* # _ . ? digits ...) is matched against the stem list with
                      every mask = one letter (c*res -> cures, d#tox -> detox, m1racle -> miracle)
             join     split words whose concatenation is a claim stem (cu res, de tox, mira cle)
             squash   repeated letters (cuuuures, deeetox)
             leet     0->o 3->e 1->i/l ... (cur3s, d3t0x, p1lls)
is_benign()  non-health uses of look-alike words (cured meats, curing time, digital detox, reverse lunges),
             only when the sentence has no health/body word.
"""
from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

DATA_PATH = Path(__file__).with_name("textnorm_data.json")
DATA = json.loads(DATA_PATH.read_text())

INVISIBLE_RX = re.compile("[" + DATA["invisible_class"].encode().decode("unicode_escape") + "]")
CONFUSABLES: dict[str, str] = DATA["confusables"]
_CONF_TABLE = str.maketrans(CONFUSABLES)
LEET: dict[str, str] = DATA["leet"]
STEMS: list[str] = DATA["stems"]
JOIN_STEMS = set(DATA["join_stems"])
_SEP = re.escape(DATA["separators"])
_MASK = DATA["mask_chars"]
HEALTH_RX = re.compile(r"\b(" + DATA["health_words"] + r")\b", re.I)
BENIGN = [(b["family"], re.compile(b["rx"], re.I)) for b in DATA["benign"]]
FAMILY_TERMS = DATA["family_of_rule_terms"]

# Separators: ANY non-letter/non-digit character (all Unicode punctuation, symbols, spaces: U+2027, U+2E31, ...)
_SEPCH = r"(?:[^\w]|_)"
_SPACED_RX = re.compile(r"(?<![A-Za-z])(?:[A-Za-z]" + _SEPCH + r"{1,3}){2,}[A-Za-z](?![A-Za-z])")
_INNER_SEP_RX = re.compile(r"(?<=[A-Za-z])(?:(?![\s'\-])[^\w]|_)(?=[A-Za-z])")
TEXTSPEAK: dict[str, str] = DATA.get("textspeak", {})
FUZZY_MIN = int(DATA.get("fuzzy_min_len", 5))
FUZZY_STEMS = [x for x in dict.fromkeys(STEMS + DATA.get("fuzzy_extra_stems", [])) if len(x) >= FUZZY_MIN]
FUZZY_EXCLUDE = set(DATA.get("fuzzy_exclude", []))
_HYPHEN_RX = re.compile(r"(?<=[A-Za-z])-(?=[A-Za-z])")
_TOKEN_RX = re.compile(r"\S+")
_EID_RX = re.compile(r"^[Ee]\d{2}b?$")


def canon(text: str | None) -> str:
    t = unicodedata.normalize("NFKC", text or "")
    t = INVISIBLE_RX.sub("", t)
    t = t.translate(_CONF_TABLE)
    return re.sub(r"(?<=[A-Za-z])[̀-ͯ]+", "", t)


SYMBOL_LETTERS: dict[str, str] = DATA.get("symbol_letters", {})
UNIT_TOKEN_RX = re.compile(DATA.get("unit_token_rx", r"^\d"))


def symletters(text: str) -> str:
    """Symbol look-alikes INSIDE words only: ¢ures/©ures -> cures, detøx -> detox, µures -> uures.
    Units and numbers ('20 μg', '5°C', '10µl') are never folded into words."""
    def rep(m):
        tok = m.group(0)
        core = tok.strip(".,;:!?\"'()[]")
        if not re.search(r"[A-Za-z]", tok) or UNIT_TOKEN_RX.search(core):
            return tok
        return "".join(SYMBOL_LETTERS.get(ch, ch) for ch in tok)
    return _TOKEN_RX.sub(rep, text)


def fold(text: str) -> str:
    """NFKD, drop every combining mark, then symbol look-alikes inside words (match-only)."""
    t = symletters(text)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.category(ch).startswith("M"))   # same set as JS \p{M}
    return t.translate(_CONF_TABLE)


def collapse(text: str) -> str:
    t = _SPACED_RX.sub(lambda m: re.sub(r"[^A-Za-z]", "", m.group(0)), text)
    return _INNER_SEP_RX.sub("", t)


def dehyphen(text: str) -> str:
    return _HYPHEN_RX.sub("", text)


def squash(text: str, n: int = 2) -> str:
    """Runs of >= n identical letters -> one letter (match-only)."""
    return re.sub(r"([A-Za-z])\1{" + str(n - 1) + r",}", r"\1", text)


def squash_stems(text: str) -> str:
    """Doubled letters squashed only where the result is a known stem ('cuures' -> 'cures'; 'current' untouched)."""
    def rep(m):
        pre, core, post = _split_token(m.group(0))
        sq = squash(core, 2)
        return pre + sq.lower() + post if sq != core and sq.lower() in STEMS else m.group(0)
    return _TOKEN_RX.sub(rep, text)


MULTICHAR: list[tuple[str, str]] = [tuple(x) for x in DATA.get("multichar", [])]


def multichar(text: str) -> str:
    """Multi-character leet/lookalikes inside words: c|_|res -> cures, /\\ -> a, |) -> d, (_) -> u ...
    Only tokens that also contain a letter (emoticons and separators like ' | ' stay untouched)."""
    def rep(m):
        tok = m.group(0)
        if not re.search(r"[A-Za-z]", tok):
            return tok
        for seq, r in MULTICHAR:
            tok = tok.replace(seq, r)
        return tok
    return _TOKEN_RX.sub(rep, text)


def textspeak(text: str) -> str:
    """'ur' -> 'your', 'b4' -> 'before' ... (whole tokens only)."""
    def rep(m):
        pre, core, post = _split_token(m.group(0))
        r = TEXTSPEAK.get(core.lower())
        return pre + r + post if r else m.group(0)
    return _TOKEN_RX.sub(rep, text)


def _lev1(a: str, b: str) -> bool:
    """Levenshtein distance <= 1."""
    if a == b:
        return True
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]:
            return True          # adjacent transposition ('cuers' -> 'cures'): Damerau distance 1
        return len(diff) == 1
    if la > lb:
        a, b, la, lb = b, a, lb, la
    i = 0
    while i < la and a[i] == b[i]:
        i += 1
    return a[i:] == b[i + 1:]


@lru_cache(maxsize=16384)
def _fuzzy_stem(tok: str) -> str | None:
    t = tok.lower()
    if len(t) < FUZZY_MIN or not t.isalpha() or not t.isascii() or t in FUZZY_EXCLUDE or t in STEMS:
        return None
    for st in FUZZY_STEMS:
        if _lev1(t, st):
            return st
    return None


def fuzzy(text: str) -> str:
    """Non-words at edit distance <= 1 of a blocked stem (stems >= 5 letters) become the stem:
    'lnstantly' -> 'instantly', 'clinicaIly' -> 'clinically', 'cuers' -> 'cures'. Real English/Spanish words at
    distance 1 ('cares', 'curas', 'heels') are listed in fuzzy_exclude and never folded."""
    def rep(m):
        pre, core, post = _split_token(m.group(0))
        f = _fuzzy_stem(core)
        return pre + f + post if f else m.group(0)
    return _TOKEN_RX.sub(rep, text)


def _split_token(tok: str) -> tuple[str, str, str]:
    """(leading punctuation, core, trailing punctuation incl. possessive/contraction 's 're 'll 've 'd 'm)."""
    m = re.match(r"^([\"'(\[]*)(.*?)((?:['\u2019](?:s|re|ll|ve|d|m))?[.,;:!?\"')\]]*)$", tok)
    return m.group(1), m.group(2), m.group(3)


@lru_cache(maxsize=4096)
def _mask_match(core: str) -> str | None:
    """Treat every non-letter inside a word as one unknown letter; return the stem it can only be."""
    if not re.search(r"[A-Za-z]", core) or not any(ch in _MASK for ch in core) or _EID_RX.match(core):
        return None
    if len(re.sub(r"[^A-Za-z]", "", core)) < 2 or re.fullmatch(r"[\d.,:%/+-]+[A-Za-z]{0,3}", core):
        return None                           # numbers with units (5g, 30-second, 4-6, 70%) are not masked words
    pat = "".join("[a-z]" if ch in _MASK else re.escape(ch.lower()) for ch in core)
    rx = re.compile(pat)
    for s in STEMS:
        if len(s) == len(core) and rx.fullmatch(s):
            return s
    return None


def unmask(text: str) -> str:
    def rep(m):
        pre, core, post = _split_token(m.group(0))
        s = _mask_match(core)
        return pre + s + post if s else m.group(0)
    return _TOKEN_RX.sub(rep, text)


def join_split(text: str) -> str:
    """'cu res', 'de tox', 'mira cle', 'cu—res' -> the claim stem (only when the join is a known claim stem)."""
    toks = re.split(r"(\s+|[—–-]+)", text)
    words = [(i, t) for i, t in enumerate(toks) if t and not re.fullmatch(r"\s+|[—–-]+", t)]
    for a in range(len(words)):
        for b in (a + 1, a + 2):
            if b >= len(words):
                break
            parts = [re.sub(r"[^A-Za-z]", "", words[k][1]) for k in range(a, b + 1)]
            joined = "".join(parts).lower()
            if joined in JOIN_STEMS and all(parts) and max(len(p) for p in parts) < len(joined):
                i0, i1 = words[a][0], words[b][0]
                toks[i0:i1 + 1] = [joined] + [""] * (i1 - i0)
                return join_split("".join(toks))
    return text


def _leet_token(tok: str, one: str) -> str:
    if not re.search(r"[A-Za-z]", tok) or not re.search(r"[0-9@$!|€+(<]", tok) or _EID_RX.match(tok):
        return tok
    pre, core, post = _split_token(tok)
    if re.fullmatch(r"[\d.,:%/+-]+[A-Za-z]{0,3}", core):
        return tok
    return pre + "".join(one if ch == "1" else LEET.get(ch, ch) for ch in core) + post


def leet(text: str, one: str = "i") -> str:
    return _TOKEN_RX.sub(lambda m: _leet_token(m.group(0), one), text)


def variants(text: str) -> list[str]:
    """canon first; then every match-only fold (deduplicated)."""
    return list(_variants(text))


@lru_cache(maxsize=8192)
def _variants(text: str) -> tuple[str, ...]:
    c = canon(text)
    f = unmask(fold(c))              # masks first: collapse would delete the '*' in 'c*res'
    k = collapse(f)
    d = dehyphen(k)
    u = unmask(d)
    j = join_split(u)
    s1, s2 = squash(j, 3), squash_stems(squash(j, 3))
    ts = textspeak(s2)
    z = fuzzy(ts)
    mc = multichar(fold(c))                       # multi-char lookalikes first, then the usual chain
    mk = collapse(unmask(mc))
    mcs = [mc, mk, leet(mk, "i"), leet(mk, "l"), fuzzy(leet(mk, "i")), fuzzy(leet(mk, "l"))]
    cands = [c, f, k, d, u, j, s1, s2, leet(d, "i"), leet(d, "l"), leet(j, "i"), leet(j, "l"), unmask(leet(k, "i")),
             unmask(k), join_split(leet(u, "i")), squash_stems(squash(leet(j, "i"), 3)),
             ts, z, fuzzy(leet(ts, "i")), fuzzy(leet(ts, "l")), *mcs]
    out: list[str] = []
    for v in cands:
        if v not in out:
            out.append(v)
    return tuple(out)


def family_of(term: str) -> str | None:
    t = term.lower()
    for fam, stem in FAMILY_TERMS.items():
        if stem in t:
            return fam
    return None


def is_benign(match: str, sentence: str) -> bool:
    """A look-alike word in a clearly non-health phrase ('cured meats', 'curing time', 'digital detox'),
    and no health/body word anywhere in the sentence."""
    fam = family_of(match)
    if not fam or HEALTH_RX.search(sentence):
        return False
    return any(f == fam and rx.search(sentence) for f, rx in BENIGN)


def _script(ch: str) -> str:
    try:
        return unicodedata.name(ch).split(" ")[0]
    except ValueError:
        return "?"


def mixed_script_tokens(text: str) -> list[str]:
    """Words containing Latin letters plus letters from another script (after NFKC, before confusable mapping)."""
    t = INVISIBLE_RX.sub("", unicodedata.normalize("NFKC", text or ""))
    bad = []
    for tok in re.findall(r"\w+", t):
        if UNIT_TOKEN_RX.search(tok):
            continue                          # '20μg', 'μg', 'μmol' are units, not homoglyph words
        scripts = {_script(ch) for ch in tok if ch.isalpha()}
        if "LATIN" in scripts and len(scripts) > 1:
            bad.append(tok)
    return bad


def has_invisible(text: str) -> bool:
    return bool(INVISIBLE_RX.search(unicodedata.normalize("NFKC", text or "")))
