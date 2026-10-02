"""Rule tables for the deterministic compliance scanner.

Sources (authoritative order): SAFETY_RULES.md > prompts/blocked_claims.json > the extra deterministic
rules below (each cites the SAFETY_RULES rule it enforces).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from common import config

SEVERITY_RANK = {"flag": 0, "revise": 1, "rewrite": 1, "human": 2, "block": 3}


@dataclass
class Rule:
    id: str
    severity: str                 # block | revise | human | flag
    pattern: str
    meaning: str
    source: str                   # blocked_claims.json | SAFETY_RULES.md §3.1 | deterministic
    mbex: bool = False            # eligible for the myth-bust exception (SAFETY §3.1 MB-EX)
    negatable: bool = False       # a negation in the same clause ("never hold your breath") neutralises it
    strip_reviewer_strings: bool = False
    rx: re.Pattern = field(init=False, repr=False)

    def __post_init__(self):
        self.rx = re.compile(self.pattern, re.I)


# Blocked-claims IDs the MB-EX may cover. It NEVER covers disease-cure (BC01), reversal (BC02),
# medication substitution (BC04), credentials/clergy/testimonials (BC07/08/09) or disease immunity (BC12).
MBEX_ELIGIBLE_BC = {"BC03", "BC05", "BC06", "BC10", "BC11", "BC13", "BC14", "BC15", "BC19", "BC20", "BC22"}
# BLITZ canon CX-GUAR: the refund-policy phrases are whitelisted inside BC14 / SR3.1 line 12 (lookbehind);
# BC23 (money-back guarantee next to a health outcome) is never MB-EX-eligible.
COMMERCE_GUARANTEE_PHRASES = ("14-day money-back guarantee", "money-back guarantee")
# Blocked-claims rules whose hit is neutralised by a negation in the same clause.
NEGATABLE_BC = {"BC03", "BC16", "BC17", "BC18", "BC24"}

# SAFETY_RULES §3.1 embedded copy (used if the markdown can't be parsed). Kept verbatim.
SAFETY_31_FALLBACK = r"""
cure[sd]?|curing|heal(s|ed|ing)? (your|the|my) (arthritis|diabetes|blood pressure|cancer|heart|liver|kidney|thyroid|dementia|alzheimer'?s|neuropathy|osteoporosis)
reverse[sd]? (diabetes|arthritis|osteoporosis|aging|dementia|alzheimer'?s|heart disease)
(treats?|treatment for) (diabetes|hypertension|cancer|arthritis|depression|anxiety disorder|insomnia|ibs|gerd)
prevent[s]? (cancer|dementia|alzheimer'?s|stroke|heart attack)            → REWRITE: "is linked with lower risk of" + evidence ID required
detox|cleanse (your )?(liver|colon|kidneys|blood)|flush (out )?toxins
lower(s)? (your )?blood pressure (instantly|in minutes|fast|immediately)
burn (sugar|belly fat|fat) (fast|instantly|overnight)
melt(s)? (belly )?fat|target(ed)? fat loss|spot reduc
boost(s)? (your )?immune system                                          → REWRITE: "supports normal immune function" only with nutrient evidence, else delete
anti-?aging (secret|miracle)|fountain of youth|add (\d+ )?years to your life|live to 100
miracle|secret (doctors|big pharma)|doctors (hate|don't want)|big pharma|they don't want you to know
(?<!money.back )guarantee\b|guarantee[ds]\b|money.back guarantee (that|you|you'?ll|your|it|it'?ll|this)\b|money.back guarantee\b[^.!?\n]{0,120}\b(stronger|sleep\w*|pain\w*|lose|lost|losing|weight|fat|balance|falls?|results?|feel better|younger|fix\w*|heal\w*|improve\w*|works? for you|see a difference|notice)|(stronger|sleep\w*|pain\w*|lose|lost|losing|weight|fat|balance|falls?|results?|feel better|younger|fix\w*|heal\w*|improve\w*|works? for you|see a difference|notice)\b[^.!?\n]{0,120}\bmoney.back guarantee|100% (safe|effective|natural)|no side effects|works for everyone
clinically proven                                                         → REWRITE: "studied in [n] people" + evidence ID
instead of (your )?(medication|medicine|pills|surgery|doctor)
(stop|quit|reduce|replace) (taking )?(your )?(medication|medicine|pills|insulin|blood thinner|statin)
natural (alternative|replacement) (to|for) (medication|statins|metformin|antidepressants)
never (get sick|go to the (doctor|hospital))
(this|it) (will|can) fix (your )?(knee|back|hip|shoulder) (forever|for good|permanently)
pain[- ]free (forever|guaranteed)
"""
# Index (0-based) of §3.1 lines the MB-EX can NOT cover: cure, reverse, treat, medication phrases.
SAFETY_31_NO_MBEX_KEYWORDS = ("cure", "reverse", "treat", "instead of", "stop|quit", "natural (alternative")


def parse_safety_31(md_text: str | None) -> list[tuple[str, str, str]]:
    """Return [(regex, severity, note)] from the ```...``` block under '### 3.1' in SAFETY_RULES.md."""
    block = None
    if md_text:
        m = re.search(r"### 3\.1[^\n]*\n```\n(.*?)```", md_text, re.S)
        if m:
            block = m.group(1)
    if block is None:
        block = SAFETY_31_FALLBACK
    out = []
    for raw in block.strip().splitlines():
        if not raw.strip():
            continue
        pat, _, note = raw.partition("→")
        pat = pat.strip()
        sev = "revise" if note.strip().upper().startswith("REWRITE") else "block"
        out.append((pat, sev, note.strip()))
    return out


def _safety_rules_text() -> str | None:
    try:
        return Path(config.SAFETY_RULES_PATH).read_text()
    except OSError:
        return None


@lru_cache(maxsize=1)
def blocked_claims_doc() -> dict:
    return json.loads(Path(config.BLOCKED_CLAIMS_PATH).read_text())


# --- BRIEF.md CANON UPDATE hard lines (AUDIT_FINAL round 5) ----------------------------------------
# Same condition-hashtag stems as tools/build_content.py CONDITION_HASHTAG (kept in sync by a test).
CONDITION_HASHTAG_PATTERN = (
    r"#\w*(arthrit|pain|bloat|bloodpressure|bloodsugar|bonehealth|circulation|constipat|cough|dizz|fallprevention|"
    r"fallrecovery|fallrisk|fearoffall|guthealth|hearthealth|remedy|kneearthritis|replacement|lonel|menopaus|muscleloss|"
    r"osteo|rehab|sarcopen|apnea|snor|stiff|diabet|insomnia|cholesterol|anxiety|depress|dementia|reflux|grief|widow|"
    r"injur|backhealth|ibs|sciatica|neuropath|incontinen|hypertens|cancer|stroke)")
CONDITION_HASHTAG_RX = re.compile(CONDITION_HASHTAG_PATTERN, re.I)
CANON_FALL_PATTERN = (
    r"\b(prevent\w*|reduc\w*|cut|cuts|cutting|lower\w*|fewer|less|halve\w*|slash\w*|drop\w*|went down)\b[^.;?!]{0,40}\bfall(s|ing)?\b"
    r"(?![- ]?(asleep|behind|apart|for|in love|off the wagon|into))"
    r"|\bfall(s|ing)?\b[^.;?!]{0,40}\b(reduc\w*|cut in half|lower\w*|fewer|less|dropp?ed|went down|prevent\w*|halve\w*)\b"
    r"|\b(never|won'?t|will not|stop) fall(ing)?( again| down)?\b"
    r"|\bfall[- ]?(prevention|proof)\b|\bfalls?\s*[−-]\s?\d|[−-]\s?\d+\s?%\s*falls?|\d+\s?(%|percent)\s*(fewer|less|lower)\s*falls?")
CANON_MORTALITY_PATTERN = (
    r"\byou('ll| will| are going to|'re going to)?\s+(live|survive)\s+(longer|\d+ (more )?years)\b"
    r"|\byou('ll| will| are going to|'re going to)?\s+die\s+(sooner|earlier|early|younger|first)\b"
    r"|\b(cut|cuts|lower\w*|reduc\w*|slash\w*|halve\w*)\s+your\s+(risk|chances?|odds)\s+of\s+(death|dying|an early death|early death)\b"
    r"|\b(add|adds|adding)\s+(\w+\s+)?years\s+to\s+your\s+life\b")

# --- Extra deterministic rules (all cite SAFETY_RULES.md) ------------------------------------------
EXTRA_RULES: list[Rule] = [
    # 3.1: disease "goes away" phrasing (self-test #1)
    Rule("SR3.1-GONE", "block",
         r"\b(arthritis|diabetes|blood pressure|hypertension|osteoporosis|neuropathy|dementia|alzheimer'?s|cancer|sciatica|"
         r"insomnia|depression|anxiety|ibs|gerd|reflux|constipation|pain)\b[^.!?]{0,30}\b(will be gone|goes away|go away|"
         r"went away|disappears?|disappeared|vanish(es|ed)?|is gone|was gone|all gone)\b",
         "Disease or symptom disappearance claim", "SAFETY_RULES.md §3.1 / D-06"),
    # D-04 claiming to be human
    Rule("D-04", "block",
         r"\b(i am real|i'?m real\b|i'?m a real (person|human|man|woman)|i am a real (person|human|man|woman)|"
         r"(i'?m|i am|we'?re|we are) not (an? )?ai\b|this is really me|my real name|i was born in 19\d\d)",
         "Character claims to be human, real or alive", "SAFETY_RULES.md D-04"),
    # D-05 credentials about Chang/Sun (self-claims and titles)
    Rule("D-05", "block",
         r"\b(i'?m|i am|i was|as) an? (doctor|physician|nurse|physical therapist|physiotherapist|dietitian|nutritionist|"
         r"pharmacist|tcm practitioner|acupuncturist|licensed \w+|certified \w+)\b|"
         r"\b(dr\.?|doctor|master|shifu|sifu|guru|lama)\s+(chang|sun|yin|yoon)\b|"
         r"\b(chang|sun|yin|yoon)\b[^.!?]{0,20}\b(is|was)\s+an?\s+(doctor|physician|nurse|physical therapist|dietitian|"
         r"nutritionist|pharmacist|acupuncturist|monk|priest)\b|\bmaster of\b|\b(monk|priest|lama|shifu|sifu|guru|clergy)\b",
         "Credential or clergy claim", "SAFETY_RULES.md D-05"),
    # D-06 fictional backstory as evidence
    Rule("D-06", "block",
         r"\b(i cured my|this (fixed|cured|healed) my|my (arthritis|knee|back|hip|shoulder|pain|diabetes|blood pressure)"
         r"[^.!?]{0,15}\b(went away|is gone|disappeared|healed)|i haven'?t been sick since|"
         r"i never (went|go|stepped foot) (to|in) the (hospital|doctor)|my doctor was (shocked|amazed|stunned))",
         "Character's own experience used as proof of a health outcome", "SAFETY_RULES.md D-06"),
    # D-07 religious / mystic framing
    Rule("D-07", "block",
         r"\b(monastery|temple secret|(at|in|from) the temple|sacred|ancient chinese secret|ancient wisdom|qi will heal|"
         r"buddha|dharma|meridian cleans\w*)\b",
         "Religious or mystic authority framing", "SAFETY_RULES.md D-07"),
    Rule("D-07-QI", "revise", r"\b(qi|chi) (flow|energy|heals?|blockage|unblock)",
         "'qi' used as a mechanism (cultural vocabulary only)", "SAFETY_RULES.md D-07"),
    # D-09 naming real creators
    Rule("D-09", "block", r"\byang ?mun\b", "Names a real creator/competitor", "SAFETY_RULES.md D-09"),
    # T-01 / T-03 testimonials and side-character results
    Rule("T-01", "block",
         r"\b(member results|customer (said|says|review)|before[- ]and[- ]after (photo|pic|result)s?|"
         r"(5|five)[- ]star reviews?|here'?s what (our )?members (say|said))\b",
         "Fabricated testimonial/review/result", "SAFETY_RULES.md T-01"),
    Rule("T-03", "block",
         r"\b(frank|mina|daniel|mandu|the kids|the grandkids)('s)?\b[^.!?]{0,25}\b(lost \d+|healed|cured|fixed|"
         r"got rid of|dropped \d+|(knee|back|hip) is healed|no longer needs)",
         "Side character reports a product/health result", "SAFETY_RULES.md T-03"),
    Rule("T-03b", "block", r"\bsince joining (the|our) (club|plan|program)\b",
         "Result attributed to joining", "SAFETY_RULES.md T-03"),
    # T-04 fake scarcity / anchors
    Rule("T-04", "block",
         r"\b(only \d+ (\w+ )?(spots?|seats?|places?|memberships?)( left)?|\d+ (\w+ )?(spots?|seats?) left|price goes up (at|tonight|tomorrow)|"
         r"last chance|ends (tonight|at midnight)|closes (tonight|at midnight)|hurry[,!]? (before|while|up|and (join|buy|grab))|selling fast|don'?t miss out|was \$\d+|normally \$\d+)",
         "Fake scarcity or price anchor", "SAFETY_RULES.md T-04"),
    # AUDIT_FINAL round 5 (Shopify launch path): a quoted result attributed to a named person with an age or a
    # "member since" tag reads as a testimonial. Real member quotes go through the permission path, never scripts.
    Rule("T-01b", "block",
         r"[\"\u201c][^\"\u201d]{8,160}[\"\u201d]\s*[-\u2013\u2014,]\s*[A-Z][a-z]+\.?( [A-Z]\.?)?,?\s*(\d{2}\b|member since|age \d)",
         "Attributed quote reads as a testimonial", "SAFETY_RULES.md T-01"),
    # BRIEF.md CANON UPDATE 2 + 6: no "$1" ever, no FREE trial, no trial of any other length; the ONLY trial wording allowed is
    # the canon-6 "7-day trial" (es: "prueba de 7 días") of the $12 Starter Books offer, whose first charge is on day 7. The
    # founding price is "locked while you stay subscribed", never "for life".
    Rule("CANON-TRIAL", "block",
         r"(\$\s?1(?![\d,.])\s*(for|today|to start|trial|a day)|\b(for|just|only)\s*\$\s?1\b(?![\d,.])|"
         r"\b(free|\$\s?\d+|(?!7\b|seven\b)\d+[- ]day|(?!seven\b)(one|two|three|five|ten|fourteen|thirty)[- ]day) trial\b|"
         r"\b(free|no[- ]cost|no[- ]charge) (7|seven)[- ]day trial\b|\btrial (offer|arm|month|week)\b|\bstart (your|a|the) free trial\b)",
         "'$1' / free trial / non-7-day trial (CANON UPDATE 2 + 6: the only trial is the paid $12 → 7-day trial, first charge day 7)", "BRIEF.md CANON UPDATE 6"),
    Rule("CANON-FORLIFE", "block",
         r"\b(locked|price|rate|founding price|membership)\b[^.!?\n]{0,30}\bfor\s+life\b|\blifetime (price|rate|lock)\b|\bfor life of (your|the) membership\b",
         "'for life' price promise (say 'locked for as long as you stay subscribed')", "OFFER.md §0.1"),
    # M-04 breath holding under load (self-test #5) - negation-aware
    Rule("M-04", "block", r"\b(hold (your|the|a) breath|bear down)\b",
         "Breath-holding / Valsalva cue", "SAFETY_RULES.md M-04 (E42)", negatable=True),
    # §4.2 spinal_flexion_loaded is not used in general content (self-test #6) - negation-aware
    Rule("M-4.2-SF", "block", r"\b(sit-?ups?|crunch(es)?|weighted toe[- ]touch(es)?|toe[- ]touch(es)? with weight)\b",
         "Loaded spinal flexion (not used in general content, E40)", "SAFETY_RULES.md §4.2", negatable=True),
    Rule("M-4.2-NECK", "block", r"\b(full )?neck (circles|rolls)\b",
         "Full neck circles (replace with nods/half-turns)", "SAFETY_RULES.md §4.2", negatable=True),
    Rule("M-4.2-BR", "block", r"\b(wim hof|hyperventilat\w*|breath (hold|retention) (of|for) \d+)",
         "Breath-retention styles are not used", "SAFETY_RULES.md §4.2", negatable=True),
    # §5 food bans
    Rule("F-FAST", "block", r"\b(intermittent fasting|skip (breakfast|dinner|lunch|meals?)|fast(ing)? for \d+ hours)\b",
         "Fasting / meal skipping is not used for this audience", "SAFETY_RULES.md §5", negatable=True),
    Rule("F-RAW", "block", r"\b(raw eggs?|raw sprouts|unpasteuri[sz]ed)\b", "Foodborne-illness risk foods",
         "SAFETY_RULES.md §5", negatable=True),
    Rule("F-ALC", "block", r"\b(red wine|alcohol|a drink)\b[^.!?]{0,30}\b(for your heart|is good for|heart health|protects)",
         "Alcohol as health", "SAFETY_RULES.md §5", negatable=True),
    Rule("F-HERB", "block", r"\b\d+\s?(mg|g|grams|ml)\b[^.!?]{0,25}\b(ginseng|astragalus|dong quai|ginkgo|he shou wu|licorice root)",
         "Medicinal herb dosing", "SAFETY_RULES.md §5 herbs_tcm"),
    # Supplement dosing in general content (self-test #8)
    Rule("SUP-DOSE", "block",
         r"\b(take|taking|add|use|scoop)\b[^.!?]{0,15}\b\d+(\.\d+)?\s?(g|mg|mcg|grams|iu|capsules?|scoops?)\b[^.!?]{0,20}"
         r"\b(creatine|collagen|magnesium|vitamin \w+|fish oil|protein powder|turmeric|ashwagandha|supplement\w*)|"
         r"\b\d+(\.\d+)?\s?(g|mg|mcg|grams|iu)\b\s+(of\s+)?(creatine|collagen|magnesium|vitamin \w+|fish oil|turmeric|ashwagandha)",
         "Supplement dose in general content (no dosing, route to Later phase + human)", "SAFETY_RULES.md §5 supplement_any"),
    Rule("SUP-OUTCOME", "block",
         r"\b(creatine|collagen|magnesium|supplement\w*|capsules?|pills?)\b[^.!?]{0,40}\b(muscles? come back|"
         r"rebuilds?|fix(es)?|cures?|melts?|reverses?|gives you back)",
         "Supplement outcome claim", "SAFETY_RULES.md §5 / DSHEA"),
    # S-01 / S-03 commerce
    Rule("S-01", "block",
         r"\b(comment|dm|join|subscribe)\b[^.!?]{0,30}\b(to|and) (fix|heal|cure|reverse|lose|get rid of|live longer|"
         r"never fall|stop (your )?pain)",
         "CTA promises a health outcome", "SAFETY_RULES.md S-01"),
    Rule("S-03", "block",
         r"\bif you don'?t (join|buy|sign up|subscribe)\b|\b(nursing home|you'?ll fall)\b[^.!?]{0,40}\b(join|buy|sign up|subscribe|membership)",
         "Guilt/fear pressure tied to purchase", "SAFETY_RULES.md S-03"),
    # AUDIT_FINAL round 5: BRIEF.md CANON UPDATE hard lines, enforced deterministically in the publish path
    # (the LLM judge is a second layer, not the only one). [^.;?!] spans newlines on purpose: a claim split
    # across caption lines is still one claim.
    Rule("CANON-FALL", "block", CANON_FALL_PATTERN,
         "Fall-prevention / fall-reduction outcome claim (never allowed, any field)", "BRIEF.md CANON UPDATE", negatable=True),
    Rule("CANON-MORT", "block", CANON_MORTALITY_PATTERN,
         "'You'-directed mortality / lifespan claim", "BRIEF.md CANON UPDATE"),
    Rule("CANON-HASHTAG", "block", CONDITION_HASHTAG_PATTERN,
         "Condition / symptom / fall hashtag (use activity tags)", "BRIEF.md CANON UPDATE"),
]

# AUDIT M4: any credential noun near a review verb, either order. Referrals ("get it checked by your doctor",
# "ask your doctor", "cleared by your doctor") are excluded in scanner.reviewer_claim().
_CRED = (r"((licensed|credentialed|registered|certified|board[- ]certified|real|our|a|an|the|two|expert|human)\s+){0,3}"
         r"(pts?|dpts?|physical therapists?|physios?|physiotherapists?|dietitians?|dieticians?|rds?|nutritionists?|"
         r"doctors?|physicians?|mds?|nurses?|clinicians?|experts?|professionals?|humans?|specialists?|team of (doctors|experts|clinicians))")
# noun-first claims need an owning/credential determiner ("our PT signs off"), not "your doctor checks"
_CRED_OWN = (r"(licensed|credentialed|registered|certified|board[- ]certified|real|our|human)\s+(licensed\s+|registered\s+)?"
             r"(pts?|dpts?|physical therapists?|physios?|physiotherapists?|dietitians?|dieticians?|rds?|nutritionists?|"
             r"doctors?|physicians?|mds?|nurses?|clinicians?|experts?|professionals?|humans?|specialists?|team)")
_VERB = r"(review(s|ed|ing)?|check(s|ed|ing)?|approv(e|es|ed|ing)|vet(s|ted|ting)?|verif(y|ies|ied|ying)|sign(s|ed)? off|signs? off|fact[- ]check(s|ed)?|screen(s|ed)|oversee[sn]?|supervis(e|es|ed))"
REVIEWER_CLAIM_RX = re.compile(
    r"\b(" + _VERB + r"\s+(by|with)\s+" + _CRED + r"|" + _CRED_OWN + r"\s+(also\s+|personally\s+)?" + _VERB + r"\b"
    r"|(science|content|pt|dietitian|doctor|expert)[- ](checked|reviewed|approved|vetted|verified)"
    r"|licensed (humans|professionals)|revisado por profesionales|by the signed pt)", re.I)
REFERRAL_CLAIM_RX = re.compile(
    r"\b(should|must|needs? to|ought to|worth)\s+(be|being|get|getting)\s+(checked|seen|looked at|evaluated|examined|screened|reviewed)\s+by"
    r"|\b(get|have|getting|having)\s+(it|that|this|them|those|your \w+)?\s*(checked|looked at|reviewed|screened|cleared)\s+by"
    r"|\b(checked|cleared|screened|seen|examined)\s+by\s+(your|her|his|their|a|the)\s+(own\s+)?"
    r"(doctor|physician|gp|pt|physio|physical therapist|dietitian|pharmacist|nurse|clinician|surgeon|team)\b"
    r"\s*(first|today|this week|before|if|when|,|\.|$)"
    r"|\b(ask|see|call|tell|check with)\s+(your|a|her|his)\s+(doctor|pt|physio|pharmacist|dietitian)", re.I)

# §3.2 flagged terms (evidence ID required)
FLAG_TERMS = re.compile(
    r"\b(inflammation|anti-inflammatory|hormones?|testosterone|estrogen|metabolism|blood sugar|insulin|cholesterol|"
    r"blood pressure|gut health|microbiome|immune|memory|brain|dementia|cortisol|vagus|HRV|bone density|osteoporosis|"
    r"arthritis|sciatica|neuropathy|prostate|menopause|constipation|IBS|reflux|sleep apnea|longevity|lifespan|mortality)\b",
    re.I)

# C-04 invented statistics (need an evidence ID)
STAT_RX = re.compile(r"(\b\d{1,3}(\.\d+)?\s?%|\b\d{1,3}(\.\d+)? percent\b|\b\d+ out of \d+\b|\bstudies (show|prove|say)\b|"
                     r"\bresearch (shows|proves|says)\b|\bscience (says|shows|proves)\b)", re.I)

NEGATION_RX = re.compile(
    r"\b(no|not|never|don'?t|do not|doesn'?t|does not|isn'?t|won'?t|can'?t|cannot|skip|avoid|instead of|without|"
    r"forget|myth|false|nope|close (it|the video)|stop believing|fake|wrong|nothing|zero|avoid\w*|against it|"
    r"recommend against|won'?t|isn'?t|aren'?t|doesn'?t)\b|✗|❌", re.I)

# BC07 "licensed" is fine when it refers the viewer to a real professional ("a licensed counselor can help").
REFERRAL_RX = re.compile(r"\b(a|see a|ask a|find a|your)\s+licensed\s+(counselor|counsellor|therapist|professional|"
                         r"physical therapist|pt|physio|dietitian|doctor|clinician|pharmacist)", re.I)

# Round 6: Spanish cues (CHARACTERS_ES.md scripts) are recognised too, so an ES script with a real cue is not
# sent to "revise" for lacking the English wording. The cue must still be present in the script.
SUPPORT_RX = re.compile(r"\b(counter|chair|wall|rail|railing|sink|bed|sofa|couch|headboard|bench|table|doorframe|door frame|"
                        r"walker|cane|kitchen counter|corner|"
                        r"encimera|mesada|silla|pared|baranda|barandal|pasamanos|lavabo|fregadero|cama|sof[aá]|mesa|"
                        r"marco de la puerta|andador|bast[oó]n|respaldo)\b", re.I)
REGRESSION_RX = re.compile(r"\b(easier|regression|hands on (your )?thighs|higher (seat|chair)|partial|half range|"
                           r"smaller range|wall support|use (your|the) hands|start (with|here)|beginner|shorter hold|"
                           r"fewer reps|hold the counter|two hands)\b", re.I)
STOP_RULE_RX = re.compile(r"\bstop if\b[^.]{0,80}\b(pain|dizz\w+|chest)", re.I)
BREATH_CUE_RX = re.compile(r"\b(breathe (out|through|in|slowly|normally)|exhale|keep breathing|breathing|breathe|"
                           r"exhal[ae]n?|exhalando|(suelt[ae]n?|saqu[ae]n?|sac[ae]n?|bot[ae]n?) el aire|respir\w+)\b", re.I)
PAIN_RULE_RX = re.compile(r"\b(3 out of 10|3/10|three out of ten)\b", re.I)
ADVANCED_LABEL_RX = re.compile(r"(chang'?s level|his level|not your starting point|don'?t start here|not where you start)", re.I)

STRENGTH_TAGS = {"sit_to_stand", "squat_to_chair", "isometric_hold", "push_incline", "plank_incline", "step_up",
                 "heel_raise", "power", "carry", "grip", "hinge", "load_light", "overhead_press_loaded", "deadlift",
                 "row", "lunge"}
SUPPORT_TAGS = {"sit_to_stand", "balance_static", "balance_dynamic", "weight_shift", "step_up", "heel_raise",
                "squat_to_chair", "floor_transfer", "isometric_hold", "power", "walking", "hip_flexor_stretch",
                "push_incline", "plank_incline"}
MOVEMENT_TAGS = SUPPORT_TAGS | STRENGTH_TAGS | {"spinal_twist_gentle", "extension_gentle", "overhead_reach", "posture",
                                                  "breath_slow", "standing_up_fast", "deep_hip_flexion",
                                                  "jumping_impact", "inversion_head_below_heart", "pelvic_floor",
                                                  "spinal_twist_end_range", "neck_circles_full"}
ADVANCED_TAGS = {"pistol", "floor_rise_no_hands", "deep_squat", "heavy_carry", "advanced"}

# §4.2 contraindication table: tag -> (required cue regex, cue text to add, severity when missing)
CONTRAINDICATIONS: dict[str, tuple[str | None, str, str]] = {
    "spinal_flexion_loaded": (None, "Not used in general content (E40). Use hinge, bird-dog or wall-slide.", "block"),
    "breath_retention": (None, "Not used. Slow breathing / extended exhale only (E18–E19).", "block"),
    "neck_circles_full": (None, "Replace with nods and half-turns. Never full circles.", "block"),
    "spinal_twist_end_range": (r"only as far as (is )?comfortable|comfortable range|gentle", "only as far as comfortable", "revise"),
    "floor_transfer": (r"(chair|sofa|couch)[^.]{0,40}(next to|beside|nearby)|someone (is )?home|chair version",
                       "Only try the floor with a sturdy chair or sofa next to you and someone home.", "revise"),
    "deep_hip_flexion": (r"new hip|surgeon", "New hip? Follow your surgeon's precautions first.", "revise"),
    "isometric_hold": (r"breathe through|ask your doctor|blood pressure", "Breathe through it. High blood pressure or heart "
                       "condition? Ask your doctor before long holds.", "revise"),
    "inversion_head_below_heart": (r"glaucoma", "Skip if you have glaucoma or blood-pressure dizziness.", "revise"),
    "jumping_impact": (r"gentle impact", "Label it 'gentle impact' (heel drops only).", "revise"),
    "standing_up_fast": (r"sit (for )?a moment|stand (up )?slowly|slowly stand|take your time standing|"
                         r"sit on the edge|pause before", "Sit a moment before you stand, then stand slowly.", "revise"),
    "overhead_press_loaded": (r"comfortable height|landmine|incline", "only to comfortable height", "revise"),
    "pelvic_floor": (r"pelvic[- ]floor (physio|physical therapist|pt)", "If you have pelvic pain or leaking that isn't "
                     "improving, a pelvic-floor physio can check you.", "revise"),
}

# §5 food/remedy cautions: trigger regex (text or tag) -> (required regex, caution line)
FOOD_CAUTIONS: dict[str, tuple[str, str, str]] = {
    "honey": (r"\bhoney\b", r"under (1|one)|babies|infants", "Never for babies under 1."),
    "blood_thinner_supps": (r"\b(ginger|turmeric|garlic) (supplements?|capsules?|pills?)|\bfish oil\b",
                            r"blood thinners?", "On blood thinners? Ask your doctor first."),
    "grapefruit": (r"\bgrapefruit\b", r"interact|labels?|medicine", "Grapefruit interacts with many medicines. Check your labels."),
    "potassium_salt": (r"\b(salt substitute|potassium (salt|chloride)|lo-?salt|nusalt|nu-salt)\b",
                       r"kidney", "Kidney disease or on blood-pressure pills like ACE inhibitors? Ask your doctor first."),
    "high_protein": (r"\b\d(\.\d)?\s?(to|–|-)?\s?(\d(\.\d)?)?\s?(g|grams?) (of protein )?(per|/|a) ?(kg|kilo)",
                     r"kidney", "Kidney disease? Ask your doctor for your number."),
    "fiber_increase": (r"\b(more fiber|fiber up|increase (your )?fiber|add fiber|\d+ ?g(rams)? of fiber)\b",
                       r"slow(ly)?|water", "Go up slowly and drink water, or you'll feel it."),
    "kimchi": (r"\b(kimchi|sauerkraut)\b", r"salt(y)?|sodium|rinse", "Kimchi is salty. Watching sodium? Small portions or rinse."),
    "vitamin_k_greens": (r"\b(warfarin|coumadin)\b", r"steady|consistent|ask your doctor",
                         "On warfarin? Keep greens steady, don't suddenly change. Ask your doctor."),
    "peppermint_oil": (r"\bpeppermint oil\b", r"reflux", "Can make reflux worse."),
    "supplement_any": (r"\b(supplements?|capsules?)\b", r"don'?t replace|pharmacist|ask your doctor",
                       "Supplements don't replace food or medicine. Ask your doctor or pharmacist, especially if you take prescriptions."),
}
# tag -> FOOD_CAUTIONS key (tags used in data/content/scripts.json)
FOOD_TAG_MAP = {"honey": "honey", "high_protein": "high_protein", "fiber_increase": "fiber_increase",
                "kimchi": "kimchi", "fermented_foods": "kimchi", "potassium_salt": "potassium_salt",
                "salt_substitute": "potassium_salt", "grapefruit": "grapefruit", "peppermint_oil": "peppermint_oil",
                "leafy_greens_vitamin_K": "vitamin_k_greens", "fish_oil": "blood_thinner_supps",
                "ginger_supplement": "blood_thinner_supps", "turmeric_supplement": "blood_thinner_supps",
                "garlic_supplement": "blood_thinner_supps", "supplement_any": "supplement_any"}

# §4.3 red-flag symptoms -> must carry the red-flag / emergency line
RED_FLAG_RX = re.compile(
    r"\b(chest pain|pressure in (your|the) chest|short(ness)? of breath at rest|fainting|fainted|sudden (weakness|numbness)|"
    r"trouble speaking|sudden severe headache|new confusion|calf (swelling|redness)|blood in (your )?stool|black stool|"
    r"vomiting blood|unexplained weight loss|fever with back pain|loss of (bladder|bowel) control|saddle (area )?numbness|"
    r"night pain|head strike|hit (your|his|her) head|hot,? swollen joint|severe new back pain)\b", re.I)
RED_FLAG_LINE_RX = re.compile(r"(for (your|her|his|a) doctor|(call|see|tell|ask|phone) (your|her|his|their|a) doctor|"
                              r"cleared by (your|a) doctor|call 911|call 999|call 112|call for help|emergency|urgent care|"
                              r"doctor,? today|doctor this week)", re.I)

# BS06: sensitive topics that route to a human
HUMAN_TOPICS_RX = re.compile(r"\b(pelvic floor|incontinence|leaking|sexual|erectile|libido|grief|widow(er)?|suicid\w*|"
                             r"self[- ]harm|eating disorder|binge|purge|medication timing|when to take your (pills|medication))\b",
                             re.I)

SUBSCRIPTION_RX = re.compile(r"\b(subscription|membership|members'? club|monthly plan|auto-?renew\w*)\b|"
                             r"\$\s?\d+(\.\d\d)?\s?(/|per |a |each )\s?(mo|month)\b", re.I)
SUBSCRIPTION_TERMS = {
    "price": re.compile(r"\$\s?\d+|\{\{\s*\w*PRICE\w*\s*\}\}", re.I),   # template placeholders filled at publish
    "interval": re.compile(r"\b(per|a|each|every|/)\s?(month|mo|year|week)\b|\bmonthly\b|\bannual(ly)?\b", re.I),
    "renews": re.compile(r"\brenew(s|al)?\b", re.I),
    "cancel": re.compile(r"cancel online( anytime)?", re.I),
}

DISCLOSURE_TAG_RX = re.compile(r"\b(ai character|personaje ia|personaje de ia)\b", re.I)


@lru_cache(maxsize=1)
def all_rules() -> list[Rule]:
    rules: list[Rule] = []
    for p in blocked_claims_doc().get("patterns", []):
        sev = p.get("severity", "block")
        rules.append(Rule(p["id"], sev, p["regex"], p.get("meaning", ""), "blocked_claims.json",
                          mbex=p["id"] in MBEX_ELIGIBLE_BC, negatable=p["id"] in NEGATABLE_BC))
    for i, (pat, sev, note) in enumerate(parse_safety_31(_safety_rules_text()), start=1):
        head = pat.split("|")[0]
        no_mbex = any(k in pat for k in ("cure", "reverse", "treat", "instead of", "(stop|quit", "natural (alternative",
                                               "money.back"))
        rules.append(Rule(f"SR3.1-{i:02d}", sev, r"\b(?:" + pat + r")", note or f"SAFETY_RULES §3.1 line {i}: {head}",
                          "SAFETY_RULES.md §3.1", mbex=not no_mbex,
                          negatable=bool(re.search(r"instantly|overnight", pat))))
    rules.extend(EXTRA_RULES)
    return rules


@lru_cache(maxsize=1)
def evidence_rows() -> dict[str, str]:
    """E-ID -> full table row text from EVIDENCE.md (for existence checks and number matching)."""
    try:
        txt = Path(config.EVIDENCE_PATH).read_text()
    except OSError:
        return {}
    rows = {}
    for m in re.finditer(r"^\| (E\d{2}b?) \|(.*)$", txt, re.M):
        rows[m.group(1)] = m.group(2)
    return rows


def required_lines() -> dict:
    return blocked_claims_doc().get("required_lines", {})
