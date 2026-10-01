"""Deterministic compliance scanner (checker pass 1 on script JSON, pass 2 on packaging/captions/transcript).

Output follows SAFETY_RULES.md §9 plus `verdict`, `regex_hits` (same shape as the n8n 'Regex Pre-Scan' node)
and `mbex_candidates` (myth-bust exception hits that still need the LLM judge's semantic confirmation).
"""
from __future__ import annotations

import re
from dataclasses import asdict

from common import disclosure
from compliance import rules as R
from compliance import textnorm
from compliance.normalize import NormScript, Unit, normalize

OBFUSCATION_SKIP: set[str] = set()   # rules not re-run on the collapsed / leetspeak variants (none so far)
INTERNAL_KEYS = {"compliance_note", "ad_name", "optimization_event", "evidence_note", "writer_notes", "id", "shot"}

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
MYTH_MARK_RX = re.compile(r"\b(myth|false|fake|nope|wrong)\b|✗|❌|✖|\bX\b", re.I)


def _sentences(text: str) -> list[tuple[int, int, str]]:
    out, pos = [], 0
    for part in SENT_SPLIT.split(text):
        if not part:
            continue
        start = text.find(part, pos)
        out.append((start, start + len(part), part))
        pos = start + len(part)
    return out


def _context(text: str, start: int, end: int) -> tuple[str, str, str]:
    """(clause_before_match, sentence, next_sentence)"""
    sents = _sentences(text)
    for k, (a, b, s) in enumerate(sents):
        if a <= start < b or (start >= a and end <= b):
            nxt = sents[k + 1][2] if k + 1 < len(sents) else ""
            return text[a:start], s, nxt
    return text[:start], text, ""


def _negated(before: str, sentence: str, nxt: str, match: str) -> bool:
    """Negation in the same clause before the match, or a question answered by a negation
    ("Sit-ups for a strong core? Not for older spines.")."""
    clause = re.split(r"[,;:—–]| but | and then ", before)[-1]
    if R.NEGATION_RX.search(clause):
        return True
    if sentence.rstrip().endswith("?") and nxt:
        first_clause = re.split(r"[,;:—–.]", nxt.strip())[0]
        return bool(R.NEGATION_RX.search(first_clause))
    return False


def _hit(rule: R.Rule, unit: Unit, m: re.Match) -> dict:
    return {"id": rule.id, "severity": rule.severity, "match": m.group(0), "meaning": rule.meaning,
            "source": rule.source, "where": unit.source, "unit": unit.index}


def _strip_disclosures(text: str) -> str:
    for f in disclosure.all_footers() + list(disclosure.MOVEMENT_ADDON.values()):
        text = text.replace(f, " ")
    return text


def scan_rules(ns: NormScript) -> tuple[list[dict], list[dict], list[dict]]:
    """Returns (hits, mbex_candidates, neutralized)."""
    hits, mbex, neutral = [], [], []
    on_screen_all = ns.text("on_screen")
    for unit in ns.units:
      vts = textnorm.variants(_strip_disclosures(unit.text))
      base_lc = vts[0].lower()
      for vi, text in enumerate(vts):
        for rule in R.all_rules():
            if vi and rule.id in OBFUSCATION_SKIP:
                continue
            for m in rule.rx.finditer(text):
                if not m.group(0).strip():
                    continue
                # Variants only add what obfuscation hid. If the matched words already appear verbatim in the
                # canonical text, the canonical pass (with its full context rules) has decided them.
                if vi and m.group(0).lower() in base_lc:
                    continue
                before, sentence, nxt = _context(text, m.start(), m.end())
                negated = _negated(before, sentence, nxt, m.group(0))
                if rule.negatable and negated:
                    neutral.append({**_hit(rule, unit, m), "reason": "negated in context"})
                    continue
                if textnorm.is_benign(m.group(0), sentence + " " + nxt if sentence.rstrip().endswith("?") else sentence):
                    neutral.append({**_hit(rule, unit, m), "reason": "non-health use of a look-alike word"})
                    continue
                if rule.id == "BC07" and R.REFERRAL_RX.search(text[max(0, m.start() - 12): m.end() + 30]):
                    neutral.append({**_hit(rule, unit, m), "reason": "referral to a real licensed professional"})
                    continue
                if rule.mbex and ns.myth_bust:
                    # MB-EX: (a) myth-bust script, (c) on-screen text carries MYTH/✗, (d) evidence cited.
                    # (b) "the sentence debunks it" is semantic: the heuristic is recorded, the LLM judge decides.
                    conds = {
                        "a_myth_bust_script": True,
                        "c_on_screen_marked": unit.source != "on_screen" or bool(MYTH_MARK_RX.search(text)),
                        "d_evidence_present": bool(ns.evidence),
                    }
                    if all(conds.values()):
                        conds["b_negation_heuristic"] = negated or bool(R.NEGATION_RX.search(sentence + " " + nxt))
                        mbex.append({**_hit(rule, unit, m), "conditions": conds,
                                     "needs": "LLM judge must confirm (b) semantically (SAFETY_RULES §3.1 MB-EX)"})
                        continue
                    hits.append({**_hit(rule, unit, m), "mbex_failed": [k for k, v in conds.items() if not v]})
                    continue
                hits.append({**_hit(rule, unit, m), **({"obfuscated": True} if vi else {})})
    return _dedupe(hits), _dedupe(mbex), neutral


def _strings(obj, key: str = "") -> list[str]:
    if isinstance(obj, str):
        return [] if key in INTERNAL_KEYS else [obj]
    if isinstance(obj, dict):
        return [s for k, v in obj.items() for s in _strings(v, k)]
    if isinstance(obj, (list, tuple)):
        return [s for v in obj for s in _strings(v, key)]
    return []


def evasion_checks(*sources) -> tuple[list[dict], list[dict]]:
    """AUDIT H10: homoglyph words (Latin mixed with another script) block; invisible characters need a rewrite."""
    blocks, rewrites = [], []
    texts = [s for src in sources for s in _strings(src)]
    mixed = sorted({t for s in texts for t in textnorm.mixed_script_tokens(s)})
    if mixed:
        blocks.append({"rule": "H10-HOMOGLYPH", "span": ", ".join(mixed[:5]),
                       "fix": "Mixed-script (look-alike) letters in a word. Retype it in plain Latin letters."})
    if any(textnorm.has_invisible(s) for s in texts):
        rewrites.append({"rule": "H10-INVISIBLE", "from": "zero-width/format characters",
                         "to": "remove invisible characters from the text"})
    return blocks, rewrites


def _dedupe(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for h in items:
        k = (h["id"], h["match"].lower(), h["where"], h.get("unit"))
        if k not in seen:
            seen.add(k)
            out.append(h)
    return out


def _any(rx: re.Pattern | str, text: str) -> bool:
    return bool((re.compile(rx, re.I) if isinstance(rx, str) else rx).search(text))


def reviewer_claim(text: str) -> str | None:
    """First span claiming credentialed review (SAFETY §7 / AUDIT M4), ignoring referrals to the viewer's own doctor."""
    for m in R.REVIEWER_CLAIM_RX.finditer(text):
        window = text[max(0, m.start() - 40): m.end() + 30]
        if R.REFERRAL_CLAIM_RX.search(window):
            continue
        return m.group(0)
    return None


def structural_checks(ns: NormScript, reviewer_signed: bool) -> dict:
    """Script-level REQUIRE / evidence / movement / food / red-flag checks."""
    blocks, rewrites, flags, missing, auto, human = [], [], [], [], [], []
    content = ns.text("spoken", "on_screen", "cta", "caption", "transcript")
    body = ns.text("spoken", "on_screen", "cta", "transcript")
    everything = content + "\n" + ns.safety_cue + "\n" + ns.regression
    ev_rows = R.evidence_rows()

    # --- Evidence (C-01, C-04, C-07, §3.2)
    unknown = [e for e in ns.evidence if ev_rows and e not in ev_rows]
    for e in unknown:
        rewrites.append({"rule": "C-01", "from": e, "to": "use an evidence ID that exists in EVIDENCE.md"})
    # flag terms are detected on every normalised variant too (fuzzy/leet/spacing tricks can't hide 'immune')
    flag_terms = sorted({m.group(0).lower() for v in textnorm.variants(body) for m in R.FLAG_TERMS.finditer(v)})
    for t in flag_terms:
        flags.append({"rule": "3.2", "term": t, "evidence_present": bool(ns.evidence)})
    if flag_terms and not ns.evidence:
        blocks.append({"rule": "C-07", "span": ", ".join(flag_terms[:5]),
                       "fix": "Health claim with no evidence field. Cite an EVIDENCE.md ID or remove the claim."})
    stat = R.STAT_RX.search(content)
    if stat and not ns.evidence:
        blocks.append({"rule": "C-04", "span": stat.group(0),
                       "fix": "Statistic with no evidence ID. Cite the EVIDENCE.md entry or delete the number."})
    if ns.evidence and ev_rows:
        cited = " ".join(ev_rows.get(e, "") for e in ns.evidence).replace(",", "")
        for m in re.finditer(r"\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\s?%", body):
            num = m.group(0).replace(",", "").replace(" ", "")
            bare = num.rstrip("%")
            if num.endswith("%"):
                ok = re.search(r"(?<![\d.])" + re.escape(bare) + r"\s?%", cited) is not None
            else:
                ok = re.search(r"(?<![\d.])" + re.escape(bare) + r"(?![\d])", cited) is not None
            if not ok:
                rewrites.append({"rule": "C-01", "from": m.group(0),
                                 "to": f"number not found in cited evidence {ns.evidence}; match EVIDENCE.md exactly"})

    # --- Reviewer gate (§7)
    if not reviewer_signed:
        m = reviewer_claim(everything)
        if m:
            blocks.append({"rule": "§7-reviewer", "span": m,
                           "fix": "No 'reviewed by licensed' wording until reviewer_signed = true. Use the FALLBACK string."})

    # --- Movement safety (§4.1, §4.2)
    tags = set(ns.movement_tags)
    move_tags = tags & R.MOVEMENT_TAGS
    for tag in sorted(tags & set(R.CONTRAINDICATIONS)):
        req, cue, sev = R.CONTRAINDICATIONS[tag]
        if req is None:
            blocks.append({"rule": "§4.2", "span": tag, "fix": cue})
        elif not _any(req, everything):
            (blocks if sev == "block" else missing).append(
                {"rule": "§4.2", "span": tag, "fix": cue} if sev == "block" else f"§4.2 {tag}: add \"{cue}\"")
    if ns.kind == "script" and ns.has_movement:
        needs_support = bool(move_tags & R.SUPPORT_TAGS) or not move_tags
        if needs_support and not R.SUPPORT_RX.search(everything):
            missing.append("M-01 support cue (hold a counter/chair, chair against a wall)")
        if not (ns.regression or R.REGRESSION_RX.search(everything)):
            missing.append("M-02 regression (easier version, spoken or on screen)")
        if R.STOP_RULE_RX.search(everything):
            pass
        else:
            auto.append("movement_addon_en (M-03 stop rule appended to caption before the footer)")
        if move_tags & R.STRENGTH_TAGS and not R.BREATH_CUE_RX.search(everything):
            missing.append("M-04 breathing cue ('breathe out as you stand/push')")
        if ns.pillar == "P06" and not R.PAIN_RULE_RX.search(everything):
            missing.append("M-05 pain rule ('mild discomfort up to 3 out of 10 is okay if it settles by tomorrow')")
        if (tags & R.ADVANCED_TAGS) and not R.ADVANCED_LABEL_RX.search(everything):
            missing.append("M-07 label advanced feats 'Chang's level — not your starting point' and show the beginner version")

    # --- Food / remedy cautions (§5, C-05, C-06)
    triggered = {R.FOOD_TAG_MAP[t] for t in tags if t in R.FOOD_TAG_MAP}
    for key, (trig, _req, _line) in R.FOOD_CAUTIONS.items():
        for m in re.finditer(trig, content, re.I):
            before, sentence, nxt = _context(content, m.start(), m.end())
            if key == "supplement_any" and _negated(before, sentence, nxt, m.group(0)):
                continue
            triggered.add(key)
            break
    for key in sorted(triggered):
        _trig, req, line = R.FOOD_CAUTIONS[key]
        if not re.search(req, everything, re.I):
            missing.append(f"C-06 {key}: add \"{line}\"")

    # --- Red flags (§4.3)
    for m in R.RED_FLAG_RX.finditer(content):
        _b, sentence, nxt = _context(content, m.start(), m.end())
        if re.search(r"\bstop\b", sentence + " " + nxt[:24], re.I):
            continue   # the standard stop rule is not a red-flag topic
        if not R.RED_FLAG_LINE_RX.search(everything):
            missing.append(f"§4.3 red flag '{m.group(0)}': add the red-flag line "
                           "(\"That one isn't for exercise. That's for your doctor, today.\") and no exercise as the fix")
        break

    # --- Human-review topics (BS06)
    for m in R.HUMAN_TOPICS_RX.finditer(content):
        human.append(f"BS06 sensitive topic: {m.group(0)}")
        break

    # --- Subscription language (S-02)
    subs = [m for m in R.SUBSCRIPTION_RX.finditer(content)
            if not _negated(*_context(content, m.start(), m.end()), m.group(0))]
    if subs:
        lacking = [k for k, rx in R.SUBSCRIPTION_TERMS.items() if not rx.search(content)]
        if lacking:
            missing.append("S-02 subscription mention must state price, billing interval, that it renews and "
                           f"'cancel online anytime' (missing: {', '.join(lacking)})")
    return {"blocks": blocks, "rewrites": rewrites, "flags": flags, "required_missing": missing,
            "auto_inserted": auto, "human_review_reasons": human}


def disclosure_checks(packaging: dict | None, *, locale: str, reviewer_signed: bool, has_movement: bool,
                      burned_in_text: list[str] | None, paid_partnership: bool = False,
                      page_footer: str | None = None) -> dict:
    """Pass 2 disclosure checks (D-02, D-03, §5.2 flags, T-05, X links, reviewer gate)."""
    blocks, missing = [], []
    expected_footer = (page_footer or disclosure.footer(locale, reviewer_signed)).strip()
    if not reviewer_signed and reviewer_claim(expected_footer):
        blocks.append({"rule": "§7-reviewer", "span": expected_footer[:60],
                       "fix": "page_dna.caption_footer carries a review claim but reviewer_signed = false"})
        expected_footer = disclosure.footer(locale, False)
    addon = disclosure.movement_addon(locale)
    if burned_in_text is not None:
        if not any(R.DISCLOSURE_TAG_RX.search(t or "") for t in burned_in_text):
            missing.append(f"D-02 burned-in corner tag '{disclosure.ai_tag(locale)}'")
    if packaging:
        for pl, field in (("instagram", "caption"), ("tiktok", "caption"), ("youtube", "description"),
                          ("facebook", "caption")):
            pk = packaging.get(pl)
            if not pk:
                continue
            cap = (pk.get(field) or "").rstrip()
            if not cap.endswith(expected_footer):
                missing.append(f"D-03 {pl}: caption must end with the exact footer")
            elif has_movement:
                head = cap[: -len(expected_footer)].rstrip()
                if not head.endswith(addon):
                    missing.append(f"§7 {pl}: movement add-on must sit immediately before the footer")
            if paid_partnership and not re.match(r"\s*(#ad\b|paid partnership)", cap, re.I):
                missing.append(f"T-05 {pl}: caption must start with #ad or 'Paid partnership'")
        tt = packaging.get("tiktok")
        if tt is not None and tt.get("is_aigc") is not True:
            blocks.append({"rule": "D-01/§5.2", "span": "tiktok.is_aigc", "fix": "is_aigc must be true on every TikTok post"})
        yt = packaging.get("youtube")
        if yt is not None and yt.get("contains_synthetic_media") is not True:
            blocks.append({"rule": "D-01/§5.2", "span": "youtube.contains_synthetic_media",
                           "fix": "containsSyntheticMedia must be true on every upload"})
        x = packaging.get("x")
        if x and re.search(r"https?://|www\.", x.get("text") or ""):
            blocks.append({"rule": "PIPELINE §2.2", "span": "x.text link", "fix": "No links in the X post body"})
    return {"blocks": blocks, "required_missing": missing}


def verdict_of(result: dict) -> str:
    if result["blocks"] or any(h["severity"] == "block" for h in result["regex_hits"]):
        return "block"
    if result["human_review_reasons"]:
        return "human"
    if result["rewrites"] or result["required_missing"] or result["regex_hits"]:
        return "revise"
    return "pass"


def packaging_units(packaging: dict | None, transcript: str | None, burned_in_text: list[str] | None) -> list[Unit]:
    units: list[Unit] = []
    for pl, pk in (packaging or {}).items():
        if not isinstance(pk, dict):
            continue
        for field in ("caption", "description", "title", "text", "on_screen_hook", "cover_text", "pinned_comment", "alt_text"):
            if pk.get(field):
                units.append(Unit("caption" if field in ("caption", "description", "text") else "on_screen",
                                  0, f"{pk[field]}"))
        # AUDIT_FINAL round 5: hashtag / tag lists are published too, so they are scanned too.
        for field in ("hashtags", "tags"):
            if isinstance(pk.get(field), list) and pk[field]:
                units.append(Unit("caption", 0, " ".join("#" + str(t).lstrip("#") for t in pk[field])))
    if transcript:
        units.append(Unit("transcript", 0, transcript))
    for i, t in enumerate(burned_in_text or []):
        units.append(Unit("on_screen", 500 + i, t))
    return units


def scan(script: dict | str | None = None, *, text: str | None = None, evidence: list[str] | None = None,
         pass_no: int = 1, kind: str | None = None, reviewer_signed: bool = False, locale: str = "en-US",
         packaging: dict | None = None, transcript: str | None = None, burned_in_text: list[str] | None = None,
         has_movement: bool | None = None, paid_partnership: bool = False, page_footer: str | None = None) -> dict:
    """Main entry. Pass 1: script JSON (or snippet). Pass 2: packaging + transcript + burned-in text (+ script ctx)."""
    src = script if script is not None else (text or "")
    ns = normalize(src, evidence=evidence, kind=kind)
    if pass_no == 2:
        # Pass 2 judges only what viewers see/hear; the script supplies context (pillar, evidence, movement).
        ns.units = packaging_units(packaging, transcript, burned_in_text)
        ns.kind = "packaging"
    if has_movement is not None:
        ns.has_movement = has_movement
    hits, mbex, neutral = scan_rules(ns)
    st = structural_checks(ns, reviewer_signed) if ns.kind != "packaging" else {
        "blocks": [], "rewrites": [], "flags": [], "required_missing": [], "auto_inserted": [], "human_review_reasons": []}
    if ns.kind == "packaging":
        # reviewer gate + evidence-free stats still apply to what's published
        extra = structural_checks(ns, reviewer_signed)
        st["blocks"] = [b for b in extra["blocks"] if b["rule"] in ("§7-reviewer", "C-04")]
        dc = disclosure_checks(packaging, locale=locale, reviewer_signed=reviewer_signed,
                               has_movement=ns.has_movement, burned_in_text=burned_in_text,
                               paid_partnership=paid_partnership, page_footer=page_footer)
        st["blocks"] += dc["blocks"]
        st["required_missing"] += dc["required_missing"]
    if ns.kind == "snippet":
        # Snippets (self-tests, comment replies) get content rules only; completeness REQUIREs need a full script.
        st["required_missing"] = [m for m in st["required_missing"] if m.startswith("§4.3")]
        st["auto_inserted"] = []
    ev_blocks, ev_rewrites = evasion_checks(script if script is not None else text, packaging, transcript, burned_in_text)
    st["blocks"] += ev_blocks
    st["rewrites"] += ev_rewrites
    blocks = st["blocks"] + [{"rule": h["id"], "span": h["match"], "where": h["where"], "fix": h["meaning"]}
                             for h in hits if h["severity"] == "block"]
    rewrites = st["rewrites"] + [{"rule": h["id"], "from": h["match"], "to": h["meaning"], "where": h["where"]}
                                 for h in hits if h["severity"] in ("revise", "rewrite")]
    human = list(st["human_review_reasons"])
    if any(h["id"] == "BC21" for h in hits):
        human.append("BC21 supplement mention: route to human review (never the lead)")
    result = {
        "script_id": ns.id, "pass_no": pass_no, "kind": ns.kind,
        "blocks": blocks, "rewrites": rewrites, "flags": st["flags"], "required_missing": st["required_missing"],
        "auto_inserted": st["auto_inserted"] + (["caption_footer_" + disclosure.lang(locale)] if pass_no == 1 and ns.kind == "script" else []),
        "human_review_reasons": human, "mbex_candidates": mbex, "neutralized": neutral,
        "regex_hits": [{k: h[k] for k in ("id", "severity", "match", "meaning", "where")} for h in hits],
        "evidence": ns.evidence, "myth_bust": ns.myth_bust, "has_movement": ns.has_movement,
    }
    result["verdict"] = verdict_of(result)
    result["pass"] = result["verdict"] == "pass"
    result["requires_llm_confirmation"] = bool(mbex)
    return result


def judge_passed(judge: dict | None) -> bool:
    """The judge actually ran, returned JSON, said pass, with confidence >= 0.8."""
    return bool(judge) and judge.get("status") == "ok" and judge.get("verdict") == "pass" \
        and float(judge.get("confidence", 1)) >= 0.8


def combine_with_judge(scan_result: dict, judge: dict | None, require_judge: bool = False) -> dict:
    """Final verdict = worst of deterministic scan and LLM judge (rank block > human > revise > pass).

    require_judge=True (the pipeline: /compliance/scan, /package): the judge is mandatory. Missing key, error,
    timeout or bad output -> "human" (or "block" if the scan blocks). Nothing is "pass" without a passing judge.

    - A deterministic block overrides an LLM pass (PIPELINE §1.4).
    - MB-EX candidates only pass when the judge ran and passed/confirmed; without a judge they go to a human.
    - Judge confidence < 0.8 -> human.
    """
    rank = {"pass": 0, "revise": 1, "human": 2, "block": 3}
    det = scan_result["verdict"]
    reasons = []
    ok = judge_passed(judge)
    if require_judge and (not judge or judge.get("status") != "ok" or not judge.get("verdict")):
        why = (judge or {}).get("status") or "not run"
        reasons.append(f"mandatory LLM judge unavailable ({why}): routed to human review")
        return {"verdict": "block" if det == "block" else "human", "deterministic": det,
                "judge": (judge or {}).get("verdict"), "judge_passed": False, "reasons": reasons}
    if not judge or judge.get("status") == "skipped" or not judge.get("verdict"):
        final = det
        if scan_result.get("requires_llm_confirmation") and final == "pass":
            final = "human"
            reasons.append("MB-EX candidate needs semantic confirmation and the LLM judge was skipped")
        return {"verdict": final, "deterministic": det, "judge": (judge or {}).get("verdict"), "judge_passed": False,
                "reasons": reasons}
    jv = judge.get("verdict", "human")
    if jv == "pass" and float(judge.get("confidence", 1)) < 0.8:
        jv = "human"
        reasons.append("judge confidence < 0.8")
    final = max([det, jv], key=lambda v: rank.get(v, 2))
    if require_judge and final == "pass" and not ok:
        final = "human"
    return {"verdict": final, "deterministic": det, "judge": judge.get("verdict"), "judge_passed": ok, "reasons": reasons}
