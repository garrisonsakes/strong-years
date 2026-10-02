"""Caption rules for hand-posted and scheduled captions (ENGINE_SAVAGE20 §B(b) item 3, SL-06.4 + SL-06.5).

SL-06.4 time-relative words: captions are written days before a person posts them, so "today", "tonight",
"this morning", "yesterday", "tomorrow" ... are rewritten to evergreen wording. Spoken lines are untouched (the
render is what it is); only caption / description / text fields.
SL-06.5 handle allowlist: a caption may mention only our own handles. Any other @handle (a competitor, a creator, a
real person) is a blocking issue: the item is held, never auto-edited, because removing a name can change meaning.
"""
from __future__ import annotations

import re

OUR_HANDLES = frozenset({
    "@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength", "@changyin.mobility", "@sunyoon",
    "@changyin.espanol", "@donchuyylupe", "@strongyears",
})
# longest phrases first; replacement keeps the original's leading capital
TIME_REWRITES: list[tuple[str, str]] = [
    (r"\blater today\b", "later"), (r"\bstarting today\b", "starting now"), (r"\bfrom today\b", "from now on"),
    (r"\btoday's\b", "this"), (r"\btoday\b", "now"),
    (r"\btonight's\b", "the evening"), (r"\btonight\b", "at night"),
    (r"\blast night\b", "one night"),
    (r"\bthis (morning|afternoon|evening)\b", r"in the \1"),
    (r"\btomorrow morning\b", "the next morning"), (r"\btomorrow\b", "the next day"),
    (r"\byesterday\b", "recently"),
    (r"\bthis weekend\b", "on the weekend"),
    (r"\bright now\b", "now"),
]
_TIME_RX = [(re.compile(p, re.I), r) for p, r in TIME_REWRITES]
# Required safety wording is never rewritten: the SAFETY_RULES §4.3 red-flag line ("That's for your doctor, today.")
# and emergency lines ("Call 911 now", "...today" urgency) must stay verbatim or pass 2 reports them missing.
SAFETY_KEEP_RX = re.compile(r"for your doctor,? today|call 911[^.\n]*|see (a|your) doctor today|seek care today", re.I)


def _protected(text: str) -> list[tuple[int, int]]:
    return [m.span() for m in SAFETY_KEEP_RX.finditer(text or "")]


def _inside(span: tuple[int, int], keep: list[tuple[int, int]]) -> bool:
    return any(a <= span[0] and span[1] <= b for a, b in keep)
HANDLE_RX = re.compile(r"(?<![\w.@/])@[A-Za-z0-9_](?:[A-Za-z0-9_.]*[A-Za-z0-9_])?")


def _keep_case(m: re.Match, repl: str) -> str:
    out = m.expand(repl)
    return out[:1].upper() + out[1:] if m.group(0)[:1].isupper() else out


def rewrite_time_words(text: str) -> tuple[str, list[str]]:
    notes = []
    text = text or ""
    for rx, repl in _TIME_RX:
        keep = _protected(text)

        def sub(m, repl=repl, keep=keep):
            if _inside(m.span(), keep):
                return m.group(0)
            notes.append(f"'{m.group(0)}' -> '{m.expand(repl)}'")
            return _keep_case(m, repl)
        text = rx.sub(sub, text)
    text = re.sub(r"\bnow now\b", "now", text, flags=re.I)
    return text, notes


def time_words(text: str) -> list[str]:
    keep = _protected(text)
    return [m.group(0) for rx, _ in _TIME_RX for m in rx.finditer(text or "") if not _inside(m.span(), keep)]


def foreign_handles(text: str, allow: frozenset[str] | set[str] = OUR_HANDLES) -> list[str]:
    allowed = {h.lower() for h in allow}
    return sorted({h for h in HANDLE_RX.findall(text or "") if h.lower() not in allowed})


def apply(text: str, allow: frozenset[str] | set[str] = OUR_HANDLES) -> dict:
    """-> {text, rewrites, blocked_handles, ok}. ok is False only for foreign handles (rewrites are automatic)."""
    new, notes = rewrite_time_words(text)
    bad = foreign_handles(new, allow)
    return {"text": new, "rewrites": notes, "blocked_handles": bad, "ok": not bad}
