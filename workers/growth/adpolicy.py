"""Stricter ad-policy check for boost candidates (ADS.md §1 and §7, Meta personal-attributes / before-after /
health-claims policies, TikTok Spark equivalents). Runs on top of the organic compliance scanner, then the
MANDATORY LLM judge; anything flagged or unjudged goes to a human. This module never clears a post for spend on
its own: the governor still needs a human approval record.

check(texts, *, judge_fn) -> {"verdict": pass|flagged|human, "hits": [...], "scan": ..., "judge": ..., "judge_passed"}
"""
from __future__ import annotations

import re

from common import config as C
from compliance import scanner
from compliance import textnorm

# "you + attribute": second person + age / health / body / condition assertions (Meta personal attributes)
ATTRIBUTE = (r"(over|past|after|under)\s*\d{2}|\d{2}\s*\+|(your|you're|youre|you are|you have|you've|do you have|are you)"
             r"\s+(too\s+)?(old|older|elderly|senior|weak\w*|frail\w*|tired|overweight|fat|heavy|thin|skinny|disabled|"
             r"stiff|sore|achy|in pain|hurting|sick|ill|diabetic|arthrit\w*|menopaus\w*|lonely|depress\w*|anxious|"
             r"struggling|falling|fallen|dizzy|bloated|constipated|incontinent|forgetful)")
RX_YOU_ATTRIBUTE = re.compile(
    r"\b(are you|you're|youre|you are|do you|have you|if you|you've been|you have|your)\b[^.!?\n]{0,40}?\b"
    r"(over|past|under|turned|hit)\s*(\d{2}|sixty|seventy|fifty|eighty)\b"
    r"|\b(your|you're|youre|you are|you have|you've got|do you have|are you|if you have|if you are|if you're)\s+"
    r"(so\s+|too\s+|getting\s+|feeling\s+|always\s+|often\s+)?(old|older|elderly|senior|weak\w*|frail\w*|tired|exhausted|"
    r"overweight|fat|heavy|thin|skinny|disabled|stiff|sore|achy|in pain|hurting|sick|ill|diabetic|arthriti\w*|"
    r"menopaus\w*|lonely|depress\w*|anxious|struggling|falling|fallen|dizzy|bloated|constipated|incontinent|forgetful|"
    r"bad (knee|hip|back|shoulder)s?|(knee|hip|back|joint|shoulder) pain|arthritis|osteoporosis|diabetes|high blood pressure|"
    r"blood sugar|balance problems?|a fall)\b", re.I)
RX_BEFORE_AFTER = re.compile(r"\bbefore\s*(&|and|/|→|->|vs\.?)\s*after\b|\btransformation\b|\b\d+\s*(lbs?|pounds|kg)\s*(down|lost|gone)\b"
                             r"|\blost\s+\d+\s*(lbs?|pounds|kg)\b|\bweeks? (later|after)\b[^.!?\n]{0,30}\b(look|body|waist)", re.I)
RX_DISEASE = re.compile(r"\b(cure[sd]?|curing|reverse[sd]?|reversing|heal[sd]?|healing|treat[s]?|treating|fix(es|ed)?|fixing|"
                        r"eliminat\w*|get rid of|prevent[s]?|preventing)\b[^.!?\n]{0,40}\b(arthritis|diabetes|dementia|alzheimer|"
                        r"osteoporosis|cancer|stroke|heart disease|blood pressure|hypertension|blood sugar|cholesterol|depression|"
                        r"anxiety|insomnia|neuropathy|sciatica|pain|disease|condition|illness|falls?|falling)\b"
                        r"|\b(lower|drop|reduce)[s]?\b[^.!?\n]{0,20}\b(blood pressure|blood sugar|cholesterol|a1c)\b", re.I)
RX_FALL = re.compile(r"\bfall[- ]?(risk|prevention|proof)\b|\b(prevent|reduc|cut|stop|avoid)\w*\b[^.!?\n]{0,30}\bfall(s|ing)?\b"
                     r"|\bfall(s|ing)?\b[^.!?\n]{0,30}\b(prevent|reduc|cut|stop|avoid)\w*", re.I)
RX_INSTANT = re.compile(r"\b(instant(ly)?|overnight|in (seconds|minutes|24 hours|one day)|miracle|guaranteed (results?|to work)|"
                        r"never (fall|hurt|ache) again)\b", re.I)
RX_FEAR = re.compile(r"\b(nursing home|hospital bed|ambulance|wheelchair|die|dying|death|dead)\b", re.I)
RX_CREDENTIAL = re.compile(r"\b(doctor|dr\.?|physician|therapist|nurse|master|monk|guru|sensei)(?!\w)[^!?\n]{0,20}?\b(chang|sun)\b"
                           r"|\b(chang|sun)\b[^.!?\n]{0,20}\b(doctor|dr\.?|physician|therapist|nurse|master|monk|guru|sensei)(?!\w)", re.I)
RX_AI_DISCLOSURE = re.compile(r"\bai[- ]?(character|generated|created|persona|made)\b|\bis an ai\b", re.I)
RX_PRICE = re.compile(r"\$\s?\d+(\.\d{2})?|\b\d+\s?(dollars|usd)\b", re.I)
RX_RECURRING = re.compile(r"(per|a|/)\s?month|monthly|renew|cancel (online )?anytime|subscription", re.I)

RULES = (("AD-ATTR", "personal attribute asserted about the viewer (you + age/health/body)", RX_YOU_ATTRIBUTE, "flag"),
         ("AD-B/A", "before/after transformation framing", RX_BEFORE_AFTER, "flag"),
         ("AD-DISEASE", "disease / condition outcome claim", RX_DISEASE, "flag"),
         ("AD-FALL", "fall-prevention or fall-risk claim", RX_FALL, "flag"),
         ("AD-INSTANT", "instant / miracle / guaranteed result", RX_INSTANT, "flag"),
         ("AD-FEAR", "sensational or fear-based imagery language", RX_FEAR, "flag"),
         ("AD-CRED", "AI character implied as a credentialed professional", RX_CREDENTIAL, "flag"))


def _norm(t: str) -> str:
    try:
        return textnorm.canon(t)
    except Exception:            # pragma: no cover - canon is total; defensive
        return t or ""


def deterministic(texts: dict[str, str], *, has_price: bool | None = None) -> list[dict]:
    hits = []
    for field, raw in (texts or {}).items():
        if not raw:
            continue
        t = _norm(str(raw))
        for rid, meaning, rx, sev in RULES:
            for m in rx.finditer(t):
                hits.append({"rule": rid, "field": field, "span": m.group(0)[:80], "meaning": meaning, "severity": sev})
    joined = " \n ".join(str(v) for v in (texts or {}).values() if v)
    if joined and not RX_AI_DISCLOSURE.search(_norm(joined)):
        hits.append({"rule": "AD-AI", "field": "*", "span": "", "meaning": "AI disclosure missing from the ad text",
                     "severity": "flag"})
    if RX_PRICE.search(joined or "") and not RX_RECURRING.search(joined or ""):
        hits.append({"rule": "AD-PRICE", "field": "*", "span": RX_PRICE.search(joined).group(0),
                     "meaning": "price shown without recurring terms", "severity": "flag"})
    return hits


def check(texts: dict[str, str], *, evidence: list[str] | None = None, judge_fn=None, market: str = "US",
          locale: str = "en-US", page_slug: str = "", require_judge: bool | None = None) -> dict:
    """Deterministic ad rules + organic scanner (pass 2 shape) + mandatory judge. `judge_fn` defaults to the
    compliance judge (which is `skipped` without ANTHROPIC_API_KEY -> verdict human)."""
    require_judge = C.REQUIRE_JUDGE if require_judge is None else require_judge
    hits = deterministic(texts)
    packaging = {"caption": texts.get("caption") or texts.get("primary_text") or "", "title": texts.get("headline") or "",
                 "hashtags": texts.get("hashtags") or []}
    scan = scanner.scan(None, text=" ".join(str(v) for v in texts.values() if v), evidence=evidence or [], pass_no=1,
                        kind="snippet", reviewer_signed=C.REVIEWER_SIGNED, locale=locale, paid_partnership=True)
    subject = {"kind": "paid_ad_candidate", "texts": texts, "packaging": packaging, "ad_rule_hits": hits}
    if judge_fn is None:
        from compliance import judge as J
        judge_fn = J.judge
    j = judge_fn(subject, scan["regex_hits"] + [{"id": h["rule"], "severity": "flag", "match": h["span"],
                                                 "meaning": h["meaning"], "where": h["field"]} for h in hits],
                 market=market, locale=locale, page_slug=page_slug, risk_tier="red")
    final = scanner.combine_with_judge(scan, j, require_judge=require_judge)
    verdict = "pass"
    reasons: list[str] = list(final.get("reasons") or [])
    if scan["verdict"] == "block" or final["verdict"] == "block":
        verdict, reasons = "flagged", reasons + ["organic scanner blocks this text"]
    elif hits:
        verdict, reasons = "flagged", reasons + [f"{h['rule']}: {h['meaning']}" for h in hits]
    elif not final.get("judge_passed"):
        verdict, reasons = "human", reasons + ["LLM judge did not pass"]
    elif final["verdict"] != "pass":
        verdict, reasons = "human", reasons + [f"final verdict {final['verdict']}"]
    return {"verdict": verdict, "hits": hits, "scan_verdict": scan["verdict"], "judge": j,
            "judge_passed": bool(final.get("judge_passed")), "final": final, "reasons": reasons}
