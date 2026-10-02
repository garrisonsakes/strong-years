#!/usr/bin/env python3
"""Build HOOKS.md, SCRIPTS.md, JSON/CSV exports and the 30-day calendar from /data/content.
Also validates scripts against the machine-checkable parts of SAFETY_RULES.md.
Run: python3 tools/build_content.py   (from /home/claude/rebuild)
"""
import json, re, csv, os, sys, importlib.util, random, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "content")

CAT_NAMES = collections.OrderedDict([
    ("CUR", "Curiosity"), ("TST", "Test / Challenge"), ("MYT", "Myth"), ("FOD", "Fear of decline (inform, never sell on fear)"),
    ("IDN", "Identity"), ("BED", "Before bed"), ("KIT", "Kitchen"), ("CPL", "Couple"), ("BLT", "Blunt truth"), ("NUM", "Numbers"),
    ("LCH", "Founding launch week"),
])
PAGE = {"CY": "@changyin", "ST": "@changyin.strength", "MB": "@changyin.mobility", "SK": "@sunyoon.kitchen",
        "SY": "@sunyoon", "CS": "@changandsun", "ES": "@changyin.espanol"}
PILLAR = {
 "P01": "Strength proof & tests", "P02": "Legs & chair strength", "P03": "Balance & steady feet", "P04": "Grip, upper body & carry",
 "P05": "Mobility & stretching", "P06": "Back / knee / shoulder relief & rehab", "P07": "Breathwork & nervous system",
 "P08": "Tai chi / qigong / gentle yoga", "P09": "Sleep & evening", "P10": "Digestion & gut", "P11": "Sun's kitchen: recipes",
 "P12": "Kitchen remedies with evidence", "P13": "Protein & muscle food", "P14": "Physiology in 30s", "P15": "Myth-busting",
 "P16": "Blunt truths: aging, mindset, women 60+", "P17": "Couple life & relationships", "P18": "Community replies & Q&A",
 "P19": "Challenges & series", "P20": "Behind the AI / trust",
}
CTA_OK = {"STRONG", "BALANCE", "BACK", "KNEES", "SLEEP", "BREATH", "SOUP", "BEGIN", "TEST", "FAMILY", "GUT", "JOIN", "WAITLIST", "BOOK"}
CTA_DELIV = {
 "STRONG": "8-Minute Chair Builder", "BALANCE": "Steady Feet + the 10-second test", "BACK": "Morning Unlock (7 min, starts in bed)",
 "KNEES": "The Step Builder", "SLEEP": "Sleep Wind-Down (10 min)", "BREATH": "The 4-6 Breath (5 min)",
 "SOUP": "Sun Yoon's Three Soups", "BEGIN": "Where should I begin? start menu", "TEST": "Strength Age test (quiz)",
 "FAMILY": "Give Mom & Dad gift page", "GUT": "Sun Yoon's 7-Day Fiber Ladder (NEW flow, clone SOUP flow)",
 "JOIN": "Founding-membership link + full terms (NEW flow, clone TEST flow; DM states price, monthly renewal, cancel online, 14-day money-back before the /join link)",
 "WAITLIST": "Free waitlist (email, optional web push) + the day-1 starter session now (FUNNEL.md §4.18; runway mode only)",
 "BOOK": "Starter books on Shopify ({{EBOOK_PRICE}} one-time: 7-Day Strength Reset + Sun Yoon's Strong Kitchen) + the optional post-purchase founding offer (FUNNEL.md §4.19)",
}
SCRIPT_FILES = ("scripts_chang", "scripts_sun", "scripts_duo",                      # S01–S60 (original library)
                "scripts_blitz_chang", "scripts_blitz_sun", "scripts_blitz_duo",    # S61–S134 (blitz expansion)
                "scripts_launch",                                                   # S135–S150 (founding launch week, blitz canon)
                "scripts_runway")                                                   # S151–S190 (organic runway + CANON UPDATE 2 launch week)
RUNWAY_FROM = 151   # S151–S175 runway (value-first, free WAITLIST CTA in a minority); S176–S190 launch week (BOOK / JOIN / FAMILY)
RUNWAY_LAUNCH_FROM = 176
N_SCRIPTS, N_HOOKS = 190, 430
V2_FROM = 61   # scripts from S61 on are held to the POSTDB_FINDINGS §8 rules (30–59 s demos, 70–130 words, skip line, grammar tags)
GRAMMARS = {"OBJ3", "IF_EVERY", "MYTH", "WATCH", "TEST_NOW", "DEBUNK", "SHARE", "KITCHEN_SERIES", "DEMO", "LAUNCH"}
BLOCKED = json.load(open(os.path.join(ROOT, "prompts", "blocked_claims.json")))["patterns"]
# Condition hashtags (AUDIT_BUSINESS F15): organic posts can be boosted into ads, so no hashtag may name a condition,
# symptom or fall/injury topic. Use activity tags instead (fitness, cooking, aging-well, strength, balance, kitchen).
CONDITION_HASHTAG = re.compile(r"#\w*(arthrit|pain|bloat|bloodpressure|bloodsugar|bonehealth|circulation|constipat|cough|dizz|fallprevention|fallrecovery|fallrisk|fearoffall|guthealth|hearthealth|remedy|kneearthritis|replacement|lonel|menopaus|muscleloss|osteo|rehab|sarcopen|apnea|snor|stiff|diabet|insomnia|cholesterol|anxiety|depress|dementia|reflux|grief|widow|injur|backhealth|ibs|sciatica|neuropath|incontinen|hypertens|cancer|stroke)", re.I)
# Fall-outcome and percentage-outcome claims (coordinator rule, ADS.md §1, AUDIT_BUSINESS F15). Fall-prevention or
# fall-reduction claims are blocked in EVERY published field (scripts, hooks, ads). Percentage outcomes ("+174%", "−58%",
# "15–30% lower risk") are blocked in the prominent fields: thumbnails, titles, YT titles, on-screen text and hook lines.
# Prevalence ("22% of older adults") is allowed. Spoken/caption association stats stay, with population context (SAFETY C-03).
FALL_OUTCOME = re.compile(
    r"\b(prevent\w*|reduc\w*|cut|cuts|lower\w*|fewer|less|dropp?\w*|went down)\b[^.;?!\n]{0,40}\bfall(s|ing)?\b"
    r"|\bfall(s)?\b[^.;?!\n]{0,40}\b(reduc\w*|cut|lower\w*|fewer|less|dropp?ed|went down|prevent\w*)\b"
    r"|\bfall[- ]?(risk|prevention)\b|\bfalls?\s*[−-]\s?\d|#fallprevention|[−-]\s?\d+\s?%\s*falls?|\d+\s?(%|percent)\s*(fewer|less|lower)\s*falls?", re.I)
PCT_OUTCOME = re.compile(r"\d\s?(%|percent)(?!\s*of\b)", re.I)


def outcome_claim_hits(label, published, prominent):
    hits = []
    for k, v in published.items():
        for m in FALL_OUTCOME.finditer(v):
            hits.append(f"{label}: fall-outcome claim in {k}: …{v[max(0, m.start()-30): m.end()+20]}…")
    for k, v in prominent.items():
        for m in PCT_OUTCOME.finditer(v):
            hits.append(f"{label}: percentage-outcome claim in {k}: …{v[max(0, m.start()-30): m.end()+20]}…")
    return hits


# Mortality framing (coordinator rule; Meta personal-attributes policy; SAFETY S-03). No mortality/death/survival language at
# all in prominent fields (hook lines, hooks bank, on-screen text, thumbnails, titles) or anywhere in ads. In spoken text and
# captions a stat may stay only as a population finding ("in a study of 2,002 adults aged 51-80, people who ... tended to have
# longer lives"): risk framing ("84% higher death risk", "odds of survival") and any sentence pairing "you/your" with
# mortality are blocked.
MORT_TERM = re.compile(r"\b(death|deaths|dying|die|dies|mortality|survival|survive|live longer|longer lives?|longer-than-expected lives|life expectancy|lifespan)\b", re.I)
MORT_RISK = re.compile(r"\b(death|mortality) risk\b|\brisk of (death|dying)\b|\b(higher|lower|increased|reduced)\s+(all-cause\s+|cardiovascular\s+)*(mortality|death)\b"
                       r"|\b(odds|likelihood|chance)s? of surviv|\d\s?(%|percent)[^.\n]{0,50}\b(death|dying|mortality|surviv)", re.I)


def mortality_hits(label, prominent, body):
    hits = []
    for k, v in prominent.items():
        for m in MORT_TERM.finditer(v):
            hits.append(f"{label}: mortality language in prominent field {k}: …{v[max(0, m.start()-30): m.end()+20]}…")
    for k, v in body.items():
        for m in MORT_RISK.finditer(v):
            hits.append(f"{label}: mortality risk framing in {k}: …{v[max(0, m.start()-30): m.end()+20]}…")
        for sent in re.split(r"(?<=[.!?])\s+|\n", v):
            if MORT_TERM.search(sent) and re.search(r"\byou(r|'re)?\b", sent, re.I):
                hits.append(f"{label}: 'you'-directed mortality claim in {k}: {sent[:120]}")
    return hits


PROVEN = ("IF_EVERY", "NOT_X", "MYTH", "WATCH")   # POSTDB_FINDINGS §3/§8 rule 3 grammars
PROVEN_MIN_SHARE = 0.45


# ---------------- virality gate (VIRALITY_SYSTEM.md §2; rubric code in tools/virality.py) ----------------
def _load_virality():
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location("cs_virality", os.path.join(ROOT, "tools", "virality.py"))
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


VIR = _load_virality()
VIRALITY_HARD_FROM = V2_FROM      # S61+ (and every wave/new script) fails the build below VIR.THRESHOLD
VIRALITY_OFFER_FLOOR = 50         # launch/offer scripts (launch=True) sell to warm viewers; lower reach bar, still gated
VIRALITY_LEGACY_GATE = "REWRITE"  # S01–S60 below threshold: kept in the library, never scheduled, listed for rewrite


def virality_gate(s):
    """Score one script and return (problems, gate). gate is 'PASS', 'OFFER' (launch script above the offer floor)
    or 'REWRITE' (a legacy S01–S60 script below threshold: excluded from every calendar/plan queue)."""
    v = VIR.score(s)
    s["_virality"] = v
    n = int(s["id"][1:]) if s["id"][1:].isdigit() else 10**6
    floor = VIRALITY_OFFER_FLOOR if s.get("launch") else VIR.THRESHOLD
    if v["score"] >= floor:
        v["gate"] = "PASS" if v["score"] >= VIR.THRESHOLD else "OFFER"
        return [], v["gate"]
    if n >= VIRALITY_HARD_FROM:
        v["gate"] = "FAIL"
        return [f"{s['id']}: virality {v['score']} < {floor} ({v['hook_class']}): " + "; ".join(v["why"])], "FAIL"
    v["gate"] = VIRALITY_LEGACY_GATE
    return [], VIRALITY_LEGACY_GATE


def proven_grammar(hook, s):
    """Classify the spoken hook against the proven grammars, from the text itself (not from tags).
    IF_EVERY: 'If you [habit] every [time], [change]'. NOT_X: 'not X, not Y'. MYTH: a myth-bust hook (P15 or MB-EX script)
    that quotes/questions/negates the claim. WATCH: '…and (just) watch what happens / watch [it|the|my|your|his|how…]'."""
    h = hook.lower().replace("\u2019", "'")
    g = []
    if re.match(r"^if you\b", h) and re.search(r"\bevery\b", h): g.append("IF_EVERY")
    if re.search(r"\bnot\b[^?!]{0,40}[,.]\s*not\b", h): g.append("NOT_X")
    if (s.get("pillar") == "P15" or s.get("myth")) and (re.match(r"^['\"\u2018\u201c]", hook) or "?" in hook or re.search(r"\b(not|no)\b|n't\b", h)):
        g.append("MYTH")
    if re.search(r"\bwatch what happens\b|\band (just )?watch\b|\bwatch (it|the|my|your|his|her|how|this|me|what)\b", h): g.append("WATCH")
    return g
# BLITZ canon CX-GUAR: "guarantee" only in the refund-policy phrases "14-day money-back guarantee" / "money-back guarantee"
# (hyphen or space). Every other form stays banned; blocked_claims.json BC23 separately blocks a money-back guarantee
# placed next to a health outcome in the same sentence.
GUARANTEE_RX = (r"\bguarantee\w+|(?<!money.back )\bguarantee\b|"
                r"\bmoney.back guarantee(?=\s+(that|you|you'?ll|your|it|it'?ll|this)\b)")
BANNED = [r"\bmy friend\b", r"\bcur(e|es|ed|ing)\b", r"\bdetox\w*", r"\bcleanse\w*", r"\btoxins?\b", r"\binstantly\b",
          r"\bmiracle\b", GUARANTEE_RX, r"\bsecret\b", r"\bmaster\b", r"\bmonk\b", r"\btemple\b", r"\bqi heals?\b",
          r"\bboost\w* (your )?immun", r"\bburn (sugar|fat|belly)", r"\bmelt\w* (belly )?fat", r"\breverse\w*\b",
          r"\bhold your breath\b", r"\bno pain,? no gain\b", r"\banti-?aging (secret|miracle)", r"\bclinically proven\b",
          r"\bheal(s|ed|ing)? (your|the|my) \w+",
          r"\bfor life\b", r"\blifetime (price|access|membership)\b",   # canon: "locked for as long as you stay subscribed", never "for life"
          r"\bmrs\.? (chang|yin)\b", r"\bsun yin\b"]                     # Sun Yoon kept her family name (CHARACTERS.md §3)
HARD_BLOCK = [r"\bcur(e|es|ed|ing)\b", r"\breverse\w* (diabetes|arthritis|osteoporosis|aging|dementia)", r"\b(stop|quit|replace) (taking )?(your )?(medication|medicine|pills|insulin)"]
NEGATION_OK = [r"hold your breath", r"never hold your breath", r"no holding your breath", r"not instantly"]


# AUDIT H10 / AUDIT_FINAL: the same anti-evasion normalisation as the workers' scanner and the n8n regex nodes
# (NFKD fold, confusables, masks, dash/space collapse, repeated letters, leetspeak). Shared tables:
# workers/compliance/textnorm_data.json, loaded through workers/compliance/textnorm.py.
def _load_textnorm():
    import importlib.util as _ilu
    path = os.path.join(ROOT, "workers", "compliance", "textnorm.py")
    spec = _ilu.spec_from_file_location("cs_textnorm", path)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


TEXTNORM = _load_textnorm()


def tn_finditer(pat, text, flags=0):
    """Yield (match, variant_text) for `pat` over every normalised variant of `text`. A variant hit whose words
    already appear verbatim in the canonical text is left to the canonical pass; non-health look-alikes
    ("cured meats", "digital detox") are skipped exactly as in the workers' scanner."""
    rx = re.compile(pat, flags)
    vs = TEXTNORM.variants(text)
    base = vs[0].lower()
    seen = set()
    for vi, v in enumerate(vs):
        for m in rx.finditer(v):
            g = m.group(0)
            if not g.strip() or (vi and g.lower() in base):
                continue
            a = max(v.rfind(".", 0, m.start()), v.rfind("!", 0, m.start()), v.rfind("?", 0, m.start())) + 1
            b = min([i for i in (v.find(".", m.end()), v.find("!", m.end()), v.find("?", m.end())) if i >= 0] or [len(v)])
            if TEXTNORM.is_benign(g, v[a:b + 1]):
                continue
            if (g.lower(), m.start() if vi == 0 else -1) in seen:
                continue
            seen.add((g.lower(), m.start() if vi == 0 else -1))
            yield m, v
SUPPORT_TAGS = {"sit_to_stand","balance_static","balance_dynamic","weight_shift","step_up","heel_raise","squat_to_chair","floor_transfer","isometric_hold","power","walking","hip_flexor_stretch","push_incline","plank_incline"}


def load_evidence_ids():
    txt = open(os.path.join(ROOT, "EVIDENCE.md")).read()
    return set(re.findall(r"^\| (E\d{2}b?) \|", txt, flags=re.M))


def load_hooks():
    rows = []
    for line in open(os.path.join(DATA, "hooks.psv")):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("|")
        rows.append(dict(id=f"H{len(rows)+1:03d}", cat=f[0], pillar=f[1], format=f[2], cta=f[3], page=f[4], speaker=f[5],
                         evidence=[e for e in f[6].split(",") if e], test_first=(f[7] == "*"), hook=f[8]))
    return rows


def load_scripts():
    out = []
    for name in SCRIPT_FILES:
        spec = importlib.util.spec_from_file_location(name, os.path.join(DATA, name + ".py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        out.extend(m.SCRIPTS)
    return out


def words(s):
    return len([w for w in re.split(r"\s+", s.strip()) if w])


def validate(scripts, hooks, ev_ids):
    hook_ids = {h["id"]: h for h in hooks}
    problems = []
    for s in scripts:
        sid = s["id"]
        spoken = " ".join(b[2] for b in s["beats"] if b[2])
        s["_spoken"] = spoken
        s["_wc"] = words(spoken)
        lo, hi = {"CHANG": (55, 110), "SUN": (50, 105), "DUO": (60, 110)}[s["speaker"]]
        if int(sid[1:]) < V2_FROM and not lo <= s["_wc"] <= hi:  # S61+ use the v2 range (70–130) in validate_v2
            problems.append(f"{sid}: word count {s['_wc']} outside {lo}-{hi}")
        if s["hook_id"] not in hook_ids:
            problems.append(f"{sid}: unknown hook {s['hook_id']}")
        if s["cta"] not in CTA_OK:
            problems.append(f"{sid}: CTA {s['cta']} not in keyword map")
        last = " ".join(b[2] for b in s["beats"][-2:])
        if f"Comment {s['cta']}" not in last:
            problems.append(f"{sid}: last beats don't say 'Comment {s['cta']}'")
        if not s["caption"].startswith(f"Comment {s['cta']}"):
            problems.append(f"{sid}: caption line 1 must start with 'Comment {s['cta']}' (FUNNEL rule)")
        for e in s["ev"]:
            if e not in ev_ids:
                problems.append(f"{sid}: evidence {e} not in EVIDENCE.md")
        if not s["ev"] and s["pillar"] not in ("P16", "P17", "P20"):
            problems.append(f"{sid}: no evidence on a health pillar")
        if s["move"]:
            if not s.get("regression"):
                problems.append(f"{sid}: movement without regression")
            if SUPPORT_TAGS & set(s["tags"]) and not re.search(r"counter|chair|wall|rail|sink|bed|sofa|headboard|bench", spoken + s["safety"], re.I):
                problems.append(f"{sid}: movement without support cue")
        text = (spoken + " " + " ".join(b[3] for b in s["beats"]) + " " + s["caption"]).lower()
        for pat in BANNED:
            for m, vtext in tn_finditer(pat, text):
                ctx = vtext[max(0, m.start()-40): m.end()+20].lower()
                if any(re.search(n, ctx) for n in NEGATION_OK):
                    continue
                if s.get("myth") and not any(re.search(h, m.group(0)) for h in HARD_BLOCK):
                    continue  # SAFETY MB-EX: myth-bust exception (semantic check still runs in pipeline)
                problems.append(f"{sid}: banned pattern '{m.group(0)}' … {ctx!r}")
        for tag in s["ig"] + s["tt"]:
            if CONDITION_HASHTAG.search(tag):
                problems.append(f"{sid}: condition hashtag {tag} (use an activity tag: fitness, cooking, aging-well, strength, balance, kitchen)")
        s["_proven"] = proven_grammar(s["beats"][0][2], s)
        if int(sid[1:]) >= V2_FROM:
            problems.extend(validate_v2(s))
            for k in ("IF_EVERY", "WATCH"):  # grammar tags must match what the hook text actually does
                if (k in s["grammar"]) != (k in s["_proven"]):
                    problems.append(f"{sid}: grammar tag {k} doesn't match the hook text")
        problems.extend(virality_gate(s)[0])
    problems.extend(validate_uniqueness(scripts))
    share = sum(1 for s in scripts if s["_proven"]) / len(scripts)
    if share < PROVEN_MIN_SHARE:
        problems.append(f"proven hook grammar share {share:.0%} < {PROVEN_MIN_SHARE:.0%} (POSTDB §8 rule 3)")
    rw = [s for s in scripts if int(s["id"][1:]) >= RUNWAY_FROM]
    if rw and sum(1 for s in rw if s["_proven"]) / len(rw) < PROVEN_MIN_SHARE:
        problems.append(f"runway/launch set S{RUNWAY_FROM}+: proven hook grammar share below {PROVEN_MIN_SHARE:.0%}")
    rwy = [s for s in rw if int(s["id"][1:]) < RUNWAY_LAUNCH_FROM]
    if rwy and sum(1 for s in rwy if s["cta"] == "WAITLIST") * 2 >= len(rwy):
        problems.append("runway set: WAITLIST must be a minority CTA (value-first runway)")
    return problems


def validate_v2(s):
    """POSTDB_FINDINGS §8 + BLITZ rules for the expansion scripts (S61+)."""
    sid, P = s["id"], []
    ost = " ".join(b[3] for b in s["beats"])
    if not 70 <= s["_wc"] <= 130:
        P.append(f"{sid}: v2 word count {s['_wc']} outside 70-130 (rule 4)")
    if not 30 <= s["secs"] <= 59:
        P.append(f"{sid}: v2 target {s['secs']} s outside 30-59 s (rule 1)")
    if int(s["beats"][-1][0].split("-")[1]) != s["secs"]:
        P.append(f"{sid}: last beat end != secs")
    hook = s["beats"][0][2]
    if len(hook.split()) > 22:
        P.append(f"{sid}: hook line >22 words")
    if len(s["beats"][0][3].split()) > 7:
        P.append(f"{sid}: frame-1 on-screen text >7 words")
    for k in ("prop", "grammar", "skip", "hcat"):
        if not s.get(k):
            P.append(f"{sid}: missing v2 field '{k}'")
    if set(s.get("grammar", [])) - GRAMMARS:
        P.append(f"{sid}: unknown grammar tag {set(s['grammar']) - GRAMMARS}")
    if s.get("skip") and s["skip"] not in s["_spoken"] + " " + ost:
        P.append(f"{sid}: 3-second skip/safety line not found verbatim in spoken or on-screen text")
    if "OBJ3" in s.get("grammar", []):
        first = [re.sub(r"[^\w'-]", "", w).lower().strip("'") for w in hook.split()[:3]]
        if not any(w.startswith(s.get("obj", "@@").lower()) for w in first):
            P.append(f"{sid}: OBJ3 but '{s.get('obj')}' is not in the first three words {first}")
    if s["cta"] == "JOIN":  # SAFETY S-02 + BLITZ founding terms
        for need in ("{{FOUNDING_PRICE}}/month", "renews monthly", "Cancel online anytime", "14-day money-back", "5,000"):
            if need not in s["caption"]:
                P.append(f"{sid}: JOIN caption missing '{need}' (S-02 / founding terms)")
        spoken_ost = (s["_spoken"] + " " + ost).lower()
        for need in ("{{founding_price}}", "cancel", "renew"):
            if need not in spoken_ost:
                P.append(f"{sid}: JOIN spoken/on-screen text missing '{need}' (S-02)")
    if s["cta"] == "FAMILY" and s.get("launch"):
        for need in ("$49", "$119", "never auto-renews"):
            if need not in s["caption"]:
                P.append(f"{sid}: gift caption missing '{need}' (S-04)")
    if s.get("launch") and s["hcat"] != "LCH":
        P.append(f"{sid}: launch script must use hook category LCH")
    if int(sid[1:]) >= RUNWAY_FROM:
        P.extend(validate_runway(s, ost))
    return P


# CANON UPDATE 2 offer rules for S151+ (ORGANIC_ENGINE.md §5, FUNNEL.md §4.18–4.19, SAFETY S-02/T-04).
MEMBER_MENTION = re.compile(r"\b(membership|member|members|subscri\w*|founding (price|seats?|cohort|members?)|per month|/month|a month)\b", re.I)
MEMBER_TERMS = ("{{FOUNDING_PRICE}}/month", "renews monthly", "Cancel online anytime", "14-day money-back guarantee",
                "locked for as long as you stay subscribed", "5,000")
BOOK_TERMS = ("{{EBOOK_PRICE}} one-time", "not a subscription", "yours to keep")


def validate_runway(s, ost):
    sid, P = s["id"], []
    n = int(sid[1:])
    spoken_ost = s["_spoken"] + " " + ost
    everything = spoken_ost + " " + s["caption"]
    if n < RUNWAY_LAUNCH_FROM:
        # runway: checkout is closed, so no price, no subscription talk, no launch flag
        if "$" in everything or "{{" in everything:
            P.append(f"{sid}: runway script states a price or offer placeholder (checkout is closed during the runway)")
        if s.get("launch"):
            P.append(f"{sid}: runway script flagged launch=True")
        for m in re.finditer(r"\b(membership|subscri\w*|founding)\b", everything, re.I):
            P.append(f"{sid}: runway script mentions '{m.group(0)}' (no offer terms before checkout opens)")
    else:
        if not s.get("launch"):
            P.append(f"{sid}: launch-week script must set launch=True")
        if s["cta"] not in ("BOOK", "JOIN", "FAMILY"):
            P.append(f"{sid}: launch-week CTA must be BOOK, JOIN or FAMILY")
    if s["cta"] == "WAITLIST":
        if n >= RUNWAY_LAUNCH_FROM:
            P.append(f"{sid}: WAITLIST is a runway-only keyword")
        if "free" not in s["caption"].lower() or not re.search(r"\bfree\b", s["_spoken"], re.I):
            P.append(f"{sid}: WAITLIST script must say it's free (spoken and caption)")
    if s["cta"] == "BOOK":
        for need in BOOK_TERMS:
            if need not in s["caption"]:
                P.append(f"{sid}: BOOK caption missing '{need}'")
        if "{{EBOOK_PRICE}}" not in spoken_ost or "one-time" not in spoken_ost:
            P.append(f"{sid}: BOOK spoken/on-screen text must state {{{{EBOOK_PRICE}}}} and 'one-time'")
    # any membership mention in a launch script carries the full recurring terms (S-02), in the canon wording
    if n >= RUNWAY_LAUNCH_FROM and s["cta"] != "FAMILY":
        cap_wo_book = s["caption"].replace("not a subscription", "")
        spoken_wo_book = re.sub(r"not a subscription", "", spoken_ost, flags=re.I)
        if MEMBER_MENTION.search(cap_wo_book) or MEMBER_MENTION.search(spoken_wo_book):
            for need in MEMBER_TERMS:
                if need not in s["caption"]:
                    P.append(f"{sid}: membership mentioned but caption missing '{need}' (S-02 / CANON UPDATE 2)")
            if MEMBER_MENTION.search(spoken_wo_book):
                for need in ("{{founding_price}}", "cancel", "renew"):
                    if need not in spoken_ost.lower():
                        P.append(f"{sid}: membership mentioned in spoken/on-screen text without '{need}' (S-02)")
    if re.search(r"\b(spots?|seats?) left\b|\bends (tonight|at midnight)\b|\blast chance\b|\bhurry\b|\bonly \d+ left\b", everything, re.I):
        P.append(f"{sid}: urgency/scarcity wording (T-04: real cap and live count only)")
    return P


def validate_uniqueness(scripts):
    """CONTENT_SYSTEM §8.2: no reused hook, hook line, or frame-1 set+prop+hook combination across pages."""
    P, seen_h, seen_line, seen_sp = [], {}, {}, {}
    for s in scripts:
        if s["hook_id"] in seen_h:
            P.append(f"{s['id']}: hook {s['hook_id']} already used by {seen_h[s['hook_id']]}")
        seen_h[s["hook_id"]] = s["id"]
        norm = re.sub(r"[^a-z0-9 ]", "", s["beats"][0][2].lower())
        if norm in seen_line:
            P.append(f"{s['id']}: hook line duplicates {seen_line[norm]}")
        seen_line[norm] = s["id"]
        if s.get("prop"):
            key = (s["beats"][0][4].split("|")[0].strip(), s["prop"].lower())
            if key in seen_sp and seen_sp[key][1] != s["page"]:
                P.append(f"{s['id']}: set+prop {key} already used on {seen_sp[key][1]} by {seen_sp[key][0]}")
            seen_sp.setdefault(key, (s["id"], s["page"]))
    return P


def blocked_claims_scan(label, fields):
    """Run every prompts/blocked_claims.json regex (case-insensitive) over published text. Returns hit strings."""
    hits = []
    for fname, text in fields.items():
        for p in BLOCKED:
            for m, vtext in tn_finditer(p["regex"], text, flags=re.I):
                ctx = vtext[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
                hits.append(f"{label}: blocked-claims {p['id']} ({p['severity']}) in {fname}: …{ctx}…")
    return hits


def script_published_text(s):
    return {"spoken": " ".join(b[2] for b in s["beats"]), "on_screen": " ".join(b[3] for b in s["beats"]),
            "caption": s["caption"], "title": s["title"], "yt_title": s["yt"], "thumbnail": s["thumb"]}


def hooks_md(hooks):
    by_cat = collections.OrderedDict((c, []) for c in CAT_NAMES)
    for h in hooks:
        by_cat[h["cat"]].append(h)
    first = [h for h in hooks if h["test_first"]]
    L = []
    L.append(f"# HOOKS.md: {len(hooks)} hooks for Chang Yin & Sun Yoon\n")
    L.append("H001–H300 are the original bank. **H301–H390 are the blitz bank**: one hook per expansion script S61–S150, written to the POSTDB_FINDINGS §8 grammars (object or body part in the first three words; 'If you [habit] every [time]'; myth 'not X, not Y'; 'watch what happens'; tests the viewer does right now; share triggers) plus the LCH founding-launch-week hooks. Each blitz hook is already produced as a script in SCRIPTS.md.\n")
    L.append("Machine-readable copies: `data/content/hooks.json` and `data/content/hooks.csv` (same IDs). Source of truth: `data/content/hooks.psv`, rebuilt with `python3 tools/build_content.py`.\n")
    L.append("**Columns:** ID · hook (spoken + on-screen; most are ≤12 words and the writer may tighten; on-screen ≤7 words) · pillar · suggested format · CTA keyword · home page · speaker · evidence ID(s). **★ = test first** (30 hooks, 3 per category).\n")
    L.append("**Rules for using a hook**")
    L.append("1. The hook is the first spoken line *and* the first on-screen text (the on-screen version may be trimmed to ≤7 words). Frame 1 is motion or a prop, never a still talking head.")
    L.append("2. The script writer can tighten the wording but can't change the claim. Any number in a hook must match its evidence ID (SAFETY C-01).")
    L.append("3. A hook runs **once per page**. It can run again on a *different* page after 21 days, with a different set, script and format (CONTENT_SYSTEM.md §8.2 uniqueness rules).")
    L.append("4. Fear-of-decline hooks inform. They are never paired with a sales line (SAFETY S-03).")
    L.append("5. Myth hooks that name a banned term (\"detox\", \"instantly\") must follow the myth-bust exception MB-EX: debunk it, label it MYTH/✗, and say what the evidence supports instead.\n")
    L.append("**CTA keyword → what the DM sends** (FUNNEL.md §4):\n")
    L.append("| Keyword | Deliverable |\n|---|---|")
    for k, v in CTA_DELIV.items():
        L.append(f"| {k} | {v} |")
    L.append("\n**Page codes:** " + " · ".join(f"{k} = {v}" for k, v in PAGE.items() if k != "ES") + "\n")
    L.append("---\n\n## ★ The 30 to test first (week 1)\n")
    L.append("Why these 30: each one is (a) a participation hook (the viewer does something in the first 5 s) or a hard number from an A/C-grade study, (b) mapped to a live ManyChat keyword, and (c) spread across all 10 categories and all 3 launch pages. Run each as 2 variants (different frame 1). Keep the top 10 by 3-second hold × comment-keyword rate.\n")
    L.append("| # | ID | Hook | Cat | Pillar | CTA | Page | Ev |\n|---|---|---|---|---|---|---|---|")
    for i, h in enumerate(first, 1):
        L.append(f"| {i} | {h['id']} | {h['hook']} | {h['cat']} | {h['pillar']} | {h['cta']} | {h['page']} | {','.join(h['evidence'])} |")
    for c, name in CAT_NAMES.items():
        L.append(f"\n---\n\n## {c}: {name} ({len(by_cat[c])})\n")
        L.append("| ID | ★ | Hook | Pillar | Fmt | CTA | Page | Spk | Ev |\n|---|---|---|---|---|---|---|---|---|")
        for h in by_cat[c]:
            L.append(f"| {h['id']} | {'★' if h['test_first'] else ''} | {h['hook']} | {h['pillar']} | {h['format']} | {h['cta']} | {h['page']} | {h['speaker'][0]} | {','.join(h['evidence'])} |")
    L.append("\n---\n\n## Pillar legend\n")
    for k, v in PILLAR.items():
        L.append(f"- **{k}** {v}")
    L.append("\n## Hook-writing formulas (for the idea-miner / variant generator to make 50 more per week)\n")
    formulas = [
        ("Participation command", "\"[Verb]. [Verb]. [Constraint]. How many/long?\"", "Sit down. Stand up. No hands. How many in 30 seconds?"),
        ("Number + population", "\"[n] people, [age]. [What they did].\"", "670 adults over 70. A 24-week tai chi class. Try one move."),
        ("Quoted myth + reversal", "\"'[myth]' [short rebuttal].\"", "\"Walking is enough.\" Walking is wonderful. It isn't enough."),
        ("Viral-trend redirect", "\"Everybody is [trend]. [Better, evidence-based thing].\"", "Everybody is putting onions in water. Put the onion in the soup."),
        ("Identity call-out", "\"For [specific group who feels unseen].\"", "For the women who raised everyone and never did one thing for themselves."),
        ("Habit stack", "\"[Existing habit]? Do this at the same time.\"", "Brushing your teeth tonight? Do this at the same time."),
        ("Character reveal", "\"I [weighed/graded/hid] his [thing]. [Result].\"", "I weighed my husband's breakfast. He was 20 grams short."),
        ("Warning sign → hope", "\"The day you [loss] is a warning. Start here.\"", "The day you need your arms to stand up is a warning. Start here."),
        ("Blunt verdict", "\"[Hard truth]. [Kind action].\"", "Loneliness is a health problem. Call someone. Today."),
        ("Couple bit", "\"He [vanity/habit]. So I [response].\"", "He flexes in the microwave. So I made a sign."),
    ]
    L.append("| Formula | Pattern | Example |\n|---|---|---|")
    for a, b, c in formulas:
        L.append(f"| {a} | {b} | {c} |")
    return "\n".join(L) + "\n"


def scripts_md(scripts, hooks):
    hk = {h["id"]: h for h in hooks}
    L = [f"# SCRIPTS.md: {len(scripts)} ready-to-produce scripts\n"]
    pc = collections.Counter(s["page"] for s in scripts)
    L.append("**Original library (S01–S60):** 30 Chang Yin (S01–S30) · 20 Sun Yoon (S31–S50) · 10 Duo (S51–S60), each 20–45 s.  ")
    L.append("**Blitz expansion (S61–S150):** 90 scripts written to POSTDB_FINDINGS §8: visible physical demos of 30–59 s (70–130 spoken words), the object or body part in the first three words, the 'If you [habit] every [time]' / myth / 'watch what happens' grammars, the US kitchen-item series (Kitchen Gym #1–3, Sun Checks Your Kitchen #1–16), tests the viewer does right now, Sun's public debunks of viral remedies, share triggers and a ~3-second skip/safety line in every script. **S135–S150 are the founding launch week** (doors-open, pinned-post variants, gift-for-parents, challenge kickoffs) built for the charge-today founding offer (BLITZ.md).  ")
    L.append("**Organic runway + launch week (S151–S190, CANON UPDATE 2):** 25 value-first runway scripts (free WAITLIST keyword in 8; the rest route to the waitlist through runway-mode DM flows) and 15 launch-week scripts for the Shopify ebook front end (BOOK, `{{EBOOK_PRICE}}` one-time) and the founding membership (post-purchase offer or JOIN; 'locked for as long as you stay subscribed'). Also rendered on their own in RUNWAY_SCRIPTS.md.  ")
    L.append("**By page:** " + " · ".join(f"{p} {n}" for p, n in sorted(pc.items(), key=lambda x: -x[1])) + ". Coverage tables: SCRIPTS_COVERAGE.md.\n")
    L.append("Machine-readable copy: `data/content/scripts.json` (CHARACTERS.md §12.4 schema, plus optional v2 keys `hook_grammar`, `series`, `launch_week`, `prop`, `skip_line`). Source: `data/content/scripts_*.py` and `scripts_launch.py`, rebuilt and validated with `python3 tools/build_content.py`.\n")
    L.append("**Offer placeholders in launch scripts:** `{{FOUNDING_PRICE}}` (the live founding price from the $25/$30 split, one value per render) and `{{DOMAIN}}`. The 5,000 founding cap is real and publicly counted; no script states a 'spots left' number (SAFETY T-04). Every JOIN script states price, monthly renewal, cancel online anytime and the 14-day money-back (SAFETY S-02).\n")
    L.append("**Production notes that apply to every script**")
    L.append("- Burned-in `AI character` corner tag on every frame (SAFETY D-02). The caption footer and the movement add-on are auto-appended (SAFETY §7). They're **not** repeated in the captions below.")
    L.append("- Shot strings: `SET-CODE | wardrobe | action | camera`. Sets and wardrobe codes are in CHARACTERS.md §4.5, §5.5 and §6. Every movement shot passes form QC (SAFETY M-08).")
    L.append("- Study-card insets use the house card design with the real citation (SAFETY V-03), lower-left, 2 s.")
    L.append("- On-screen text: max 2 lines, 52–64 px, white on a dark pill or near-black on cream. **No gray text.**")
    L.append("- Word counts are spoken words. At ~140 wpm (Chang) / ~155 wpm (Sun) plus demo pauses, S01–S60 land in 20–45 s and S61–S150 in 30–59 s (the return-era sweet spot, POSTDB §3b).\n")
    L.append("## Index\n")
    L.append("| ID | Page | Spk | Fmt | Pillar | Hook | Secs | Words | CTA | Evidence | Grammar / series |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for s in scripts:
        gs = " ".join(s.get("grammar", [])) + (f" · {s['series']}" if s.get("series") else "")
        L.append(f"| {s['id']} | {s['page']} | {s['speaker']} | {s['format']} | {s['pillar']} | {s['hook_id']} | {s['secs']} | {s['_wc']} | {s['cta']} | {', '.join(s['ev']) or 'none (opinion/offer)'} | {gs or '—'} |")
    for s in scripts:
        h = hk[s["hook_id"]]
        L.append(f"\n---\n\n## {s['id']}: {s['title']}")
        L.append(f"**Page** {s['page']} · **Speaker** {s['speaker']} · **Format** {s['format']} · **Pillar** {s['pillar']} ({PILLAR[s['pillar']]}) · **Hook** {s['hook_id']} · **Target** {s['secs']} s · **Spoken words** {s['_wc']} · **CTA** `{s['cta']}` → {CTA_DELIV[s['cta']]}\n")
        L.append(f"**Hook line:** \"{s['beats'][0][2]}\"\n")
        if s.get("_virality"):
            v = s["_virality"]
            L.append(f"**Virality (VIRALITY_SYSTEM.md §2):** {v['score']} · gate {v.get('gate', '')} · hook class {v['hook_class']}"
                     + (" · needs: " + "; ".join(v["why"]) if v["why"] else "") + "\n")
        if int(s["id"][1:]) >= V2_FROM:
            meta = [f"**Grammar:** {', '.join(s['grammar'])}", f"**Frame-1 prop:** {s['prop']}"]
            if s.get("series"): meta.append(f"**Series:** {s['series']}")
            if s.get("launch"): meta.append("**Founding launch week**")
            L.append(" · ".join(meta) + "  ")
            L.append(f"**3-second skip/safety line:** \"{s['skip']}\"\n")
        L.append("| Time (s) | Speaker | Spoken | On-screen text | Shot (set · wardrobe · action · camera) |\n|---|---|---|---|---|")
        for b in s["beats"]:
            L.append(f"| {b[0]} | {b[1]} | {b[2] or '(no line; action)'} | {b[3] or '—'} | {b[4].replace(' | ', ' · ')} |")
        L.append(f"\n**Full spoken script ({s['_wc']} words):** {s['_spoken']}\n")
        if s["move"]:
            L.append(f"**Safety cue:** {s['safety']}  ")
            L.append(f"**Regression:** {s['regression']}  ")
            L.append(f"**Movement tags:** {', '.join(s['tags'])}\n")
        else:
            L.append(f"**Safety / cautions:** {s['safety']}\n")
        L.append("**Caption** (footer auto-appended):")
        L.append("```\n" + s["caption"] + "\n```")
        L.append(f"**Hashtags:** IG/FB {' '.join(s['ig'])} · TikTok {' '.join(s['tt'])}  ")
        L.append(f"**YouTube Shorts title:** {s['yt']}  ")
        L.append(f"**Evidence:** {', '.join(s['ev']) or 'none (opinion content, no health claim)'}: {s['note']}  ")
        extras = []
        if s.get("bit"): extras.append(f"Running bit: {s['bit']}")
        extras.append(f"Wink: {'yes' if s.get('wink') else 'no'}")
        extras.append(f"Thumbnail: \"{s['thumb']}\"")
        extras.append(f"Music: {s['music']}")
        if s.get("myth"): extras.append("Myth-bust exception MB-EX applies")
        L.append("**Production:** " + " · ".join(extras))
    return "\n".join(L) + "\n"


def to_schema(s):
    out = {
        "id": s["id"], "page": s["page"], "speaker": s["speaker"], "format": s["format"], "pillar": s["pillar"],
        "hook_id": s["hook_id"], "title": s["title"], "target_seconds": s["secs"], "hook_line": s["beats"][0][2],
        "beats": [{"t": b[0], "speaker": b[1], "vo": b[2], "ost": b[3], "shot": b[4]} for b in s["beats"]],
        "spoken_word_count": s["_wc"], "has_movement": s["move"], "movement_tags": s["tags"], "safety_cue": s["safety"],
        "regression": s["regression"], "cta_keyword": s["cta"], "cta_deliverable": CTA_DELIV[s["cta"]],
        "cta_line": next((b[2] for b in reversed(s["beats"]) if "Comment" in b[2]), ""),
        "caption": s["caption"], "hashtags": {"ig": s["ig"], "tt": s["tt"], "yt_title": s["yt"]},
        "evidence": s["ev"], "evidence_note": s["note"], "running_bit": s.get("bit", ""), "wink": s.get("wink", False),
        "myth_bust": s.get("myth", False), "music": s["music"], "thumbnail_text": s["thumb"],
        "demo": bool(s.get("demo")), "hook_object": s.get("obj") or "",   # virality rubric inputs (tools/virality.py)
    }
    if s.get("_virality"):  # VIRALITY_SYSTEM.md §2: score, gate and the rubric parts (tools/virality.py)
        v = s["_virality"]
        out["virality"] = {"score": v["score"], "gate": v.get("gate", "PASS" if v["pass"] else "FAIL"), "top_decile": v["top_decile"],
                           "hook_class": v["hook_class"], "parts": v["parts"], "why": v["why"]}
    if int(s["id"][1:]) >= V2_FROM:  # optional v2 keys (additive; the §12.4 fields above are unchanged)
        out.update({"hook_grammar": s["grammar"], "series": s.get("series", ""), "launch_week": bool(s.get("launch")),
                    "prop": s["prop"], "skip_line": s["skip"], "hook_category": s["hcat"]})
    return out


# ---------------- 30-day calendar ----------------
SLOTS = [("06:45", "AM routine"), ("08:30", "Test/Challenge"), ("11:00", "Myth/Numbers"), ("12:45", "Kitchen/Lunch"),
         ("16:00", "Story/Couple"), ("19:00", "Series"), ("21:00", "Before bed")]
# preferred hook categories per slot per page (first match wins; then any category)
SLOT_CATS = {
 "CY": [["TST","CUR","IDN"], ["TST","NUM"], ["MYT","NUM"], ["FOD","IDN","CUR"], ["IDN","FOD","CUR"], None, ["BED"]],
 "SK": [["KIT","CUR"], ["TST","NUM","KIT"], ["MYT","NUM"], ["KIT"], ["BLT","IDN"], None, ["BED","BLT"]],
 "CS": [["CPL","CUR"], ["CPL","TST"], ["CPL","MYT","NUM"], ["CPL","KIT"], ["CPL","BLT","IDN"], None, ["BED","CPL"]],
}
SHARE = {  # share-of-feed targets (%), mirrored in CONTENT_SYSTEM.md §3
 "CY": {"P01":12,"P02":9,"P03":12,"P04":6,"P05":5,"P06":5,"P07":4,"P08":5,"P09":4,"P10":2,"P13":3,"P14":7,"P15":8,"P16":4,"P17":2,"P18":4,"P19":6,"P20":2},
 "SK": {"P10":15,"P11":22,"P12":13,"P13":15,"P14":2,"P15":12,"P16":8,"P17":3,"P18":5,"P19":5},
 "CS": {"P01":6,"P03":8,"P07":5,"P09":2,"P13":6,"P15":6,"P16":15,"P17":35,"P18":8,"P19":6,"P20":3},
}
PILLAR_DEFAULT = {  # pillar -> (format, CTA) for NEW briefs
 "P01":("F02","TEST"),"P02":("F17","STRONG"),"P03":("F15","BALANCE"),"P04":("F15","STRONG"),"P05":("F20","BACK"),
 "P06":("F14","KNEES"),"P07":("F21","BREATH"),"P08":("F22","BALANCE"),"P09":("F05","SLEEP"),"P10":("F06","GUT"),
 "P11":("F31","SOUP"),"P12":("F06","SOUP"),"P13":("F18","SOUP"),"P14":("F13","STRONG"),"P15":("F28","BEGIN"),
 "P16":("F07","BEGIN"),"P17":("F08","BEGIN"),"P18":("F10","BEGIN"),"P19":("F11","STRONG"),"P20":("F08","BEGIN"),
}
LAUNCH_PAGES = ["CY", "SK", "CS"]
THEMES = [
 "Launch: the 3 tests", "Legs first", "Balance week begins", "Myth day", "Kitchen protein", "Couple challenge", "Rest & breath",
 "Grip & hands", "Floor skills", "Tai chi day", "Gut week begins", "Knees & stairs", "Sun answers comments", "Sunday soup",
 "Back day", "Numbers day", "Women who lift", "Walk after dinner", "Sleep week", "Family share day", "Fermentation day",
 "Strength Age retest prompt", "Myth day II", "Qigong evening", "Steady-feet home", "Cooking for one", "Anniversary countdown",
 "Power (fast feet)", "Recap: your numbers", "Day 30: retest + celebrate"]
FIXED = {("CY", 1, 5): "S19", ("CS", 27, 4): "S60",  # (page, day, slot index) -> script
         # founding launch week (S135–S150): doors-open + pinned variants day 1, gifts/tours/terms days 2–6, 30-Day Balance kickoff day 7
         ("CY", 1, 0): "S136", ("CY", 1, 4): "S135", ("CY", 2, 3): "S139", ("CY", 3, 4): "S140", ("CY", 6, 4): "S138", ("CY", 7, 4): "S137",
         ("SK", 1, 0): "S144", ("SK", 1, 3): "S141", ("SK", 4, 4): "S143", ("SK", 5, 3): "S142",
         ("CS", 1, 0): "S146", ("CS", 1, 1): "S147", ("CS", 1, 4): "S145", ("CS", 3, 3): "S148", ("CS", 5, 4): "S149", ("CS", 6, 2): "S150"}
RUNWAY_SRC = []
BLITZ_HOOK_FROM = 301  # H301+ are already produced as scripts on their own page; never scheduled as bare hooks


def build_calendar(hooks, scripts):
    hk = {h["id"]: h for h in hooks}
    def home(h):
        if h["page"] in ("CY", "ST", "MB"): return "CY"
        if h["page"] == "SK": return "SK"
        if h["page"] == "SY": return "CS" if h["cta"] in ("BEGIN", "FAMILY") else "SK"
        return "CS"
    pool = {p: [h for h in hooks if home(h) == p and int(h["id"][1:]) < BLITZ_HOOK_FROM] for p in LAUNCH_PAGES}  # H391+ are produced as S151+
    for p in pool:  # starred first
        pool[p] = [h for h in pool[p] if h["test_first"]] + [h for h in pool[p] if not h["test_first"]]
    page_map = {"@changyin": "CY", "@changyin.strength": "CY", "@changyin.mobility": "CY", "@sunyoon.kitchen": "SK",
                "@sunyoon": "SK", "@changandsun": "CS"}
    fixed_ids = set(FIXED.values())
    launch_handles = {"@changyin", "@sunyoon.kitchen", "@changandsun"}
    # S61+ scripts written for the day-15/22 pages stay on those pages (CONTENT_SYSTEM §8.2); only S01–S60 keep the old mapping
    spool = {p: [s for s in scripts if page_map[s["page"]] == p and s["id"] not in fixed_ids and int(s["id"][1:]) < RUNWAY_FROM
                 and (int(s["id"][1:]) < V2_FROM or s["page"] in launch_handles)
                 and (s.get("_virality") or {}).get("gate") != VIRALITY_LEGACY_GATE] for p in LAUNCH_PAGES}
    used, mix = set(), {p: collections.Counter() for p in LAUNCH_PAGES}
    rows = []
    def take_script(p, cats):
        for s in spool[p]:
            c = hk[s["hook_id"]]["cat"]
            if cats is None or c in cats:
                spool[p].remove(s); used.add(s["hook_id"]); return s
        return None
    def take_hook(p, cats):
        for h in pool[p]:
            if h["id"] in used: continue
            if cats is None or h["cat"] in cats:
                used.add(h["id"]); return h
        return None
    def deficit_pillar(p):
        n = sum(mix[p].values()) + 1
        return max(SHARE[p], key=lambda k: SHARE[p][k] / 100 - mix[p][k] / n)
    for day in range(1, 31):
        for p in LAUNCH_PAGES:
            cells = []
            for si in range(len(SLOTS)):
                cats = SLOT_CATS[p][si]
                if (p, day, si) in FIXED:
                    s = next(x for x in scripts if x["id"] == FIXED[(p, day, si)])
                    used.add(s["hook_id"]); mix[p][s["pillar"]] += 1
                    cells.append(f"**{s['id']}** ({s['format']}·{s['cta']})"); continue
                if si == 5:  # series slot
                    if p == "CY":
                        cells.append(f"7-Day Strong D{day}" if day <= 7 else f"30-Day Balance D{day-7}"); mix[p]["P19"] += 1
                    elif p == "SK":
                        cells.append(f"Fiber Ladder D{day}" if day <= 7 else ("Sunday Soup" if day % 7 == 0 else f"Sun Answers #{day-7}"))
                        mix[p]["P19" if day <= 7 else "P18"] += 1
                    else:
                        cells.append("50th countdown" if day >= 20 else ("Loser does dishes" if day % 7 == 3 else f"Frank's Comeback ep{day}"))
                        mix[p]["P17"] += 1
                    continue
                if day > 7 and si == 2 and day % 2 == 0:
                    cells.append(f"REMIX wk{(day-1)//7} winner"); continue
                if si == 6 and day > 3 and day % 4 == 0:
                    cells.append("REPLY video (F09)"); mix[p]["P18"] += 1; continue
                if day <= 12:
                    s = take_script(p, cats)
                    if s:
                        mix[p][s["pillar"]] += 1; cells.append(f"**{s['id']}** ({s['format']}·{s['cta']})"); continue
                h = take_hook(p, cats) or (take_hook(p, None) if day > 14 else None)
                if h:
                    mix[p][h["pillar"]] += 1; cells.append(f"{h['id']} ({h['format']}·{h['cta']})"); continue
                pl = deficit_pillar(p); f, c = PILLAR_DEFAULT[pl]
                mix[p][pl] += 1; cells.append(f"NEW {pl}/{f}·{c}")
            rows.append((day, THEMES[day-1], PAGE[p], cells))
    return rows, used, mix


def calendar_md(rows):
    L = ["| Day | Theme | Page | " + " | ".join(f"{t} {l}" for t, l in SLOTS) + " |",
         "|---|---|---|" + "---|" * len(SLOTS)]
    for d, th, p, cells in rows:
        L.append(f"| {d} | {th} | {p} | " + " | ".join(cells) + " |")
    return "\n".join(L)


# ---------------- organic-first runway calendar (ORGANIC_ENGINE.md §1; CANON UPDATE 2) ----------------
# D0 = the day checkout opens. Pages start posting on D−R (R = runway length, client decision 7–21). The legacy 30-day
# calendar (build_calendar) is reused as the value-post queue: rollout day k of that calendar = page-age day k here.
# Its blitz launch cells (S135–S150) never run during the runway; the canon-compatible ones move to D+7…D+13.
RUNWAY_ORDER = {  # per page, in run order (spread across the runway; WAITLIST posts land in the second half)
 "CY": ["S158", "S159", "S152", "S154", "S153", "S151", "S157", "S155", "S156"],
 "SK": ["S167", "S160", "S161", "S162", "S166", "S165", "S164", "S163"],
 "CS": ["S169", "S168", "S172", "S170", "S171", "S173", "S174", "S175"],
}
LAUNCH_FIXED = {  # D-offset -> scripts (launch week; offer posts are capped at 2 per page per day)
 "CY": {0: ["S176", "S177"], 1: ["S178"], 2: ["S180"], 3: ["S179"]},
 "SK": {0: ["S181"], 1: ["S182"], 2: ["S183"], 3: ["S184"], 4: ["S185"]},
 "CS": {0: ["S186"], 1: ["S187"], 2: ["S188"], 3: ["S189"], 6: ["S190"]},
}
LEGACY_WEEK2 = {"CY": ["S136", "S137", "S138", "S139"], "SK": ["S144", "S142", "S143"], "CS": ["S147", "S148", "S149", "S150"]}
RETIRED_FOR_THIS_LAUNCH = ["S135", "S140", "S141", "S145", "S146"]   # 'doors open today' wording; reuse at a future doors-open moment
SLOT_PRIORITY = [1, 3, 5, 0, 4, 2, 6]   # Test, Kitchen, Series, AM, Story, Myth, Bed: what survives when cadence < 7
LATER_PAGES = [("@changyin.strength", 15), ("@changyin.mobility", 15), ("@sunyoon", 22), ("@changyin.espanol", 30)]


def page_cadence(age_day):
    """Videos per page per platform for a page on its age_day (0 = first posting day). PIPELINE.md §5.4 ramp."""
    wk = age_day // 7 + 1
    return {1: 2, 2: 3, 3: 5}.get(wk, 6)


def build_runway_calendar(cal_rows, R):
    """Rows: (D, stage, page, videos_per_platform, ig_trial, text_posts, [items]) for D = −R … +30."""
    queue = {}
    for d, th, handle, cells in cal_rows:
        p = {v: k for k, v in PAGE.items()}[handle]
        order = [cells[i] for i in SLOT_PRIORITY]
        for c in order:
            c = c.replace("**", "")
            sid = c.split(" ")[0]
            if sid.startswith("S") and sid[1:].isdigit() and int(sid[1:]) >= 135:
                continue   # blitz launch cells: handled by LEGACY_WEEK2 / retired
            queue.setdefault(p, []).append(c)
    rw_day = {}
    for p, ids in RUNWAY_ORDER.items():
        for i, sid in enumerate(ids):
            rw_day.setdefault(p, {}).setdefault(-R + round(i * (R - 1) / max(1, len(ids) - 1)), []).append(sid)
    rows = []
    for D in range(-R, 31):
        stage = "RUNWAY" if D < 0 else ("LAUNCH WEEK" if D <= 6 else ("WEEK 2" if D <= 13 else "SCALE"))
        for p in LAUNCH_PAGES:
            age = D + R
            n = page_cadence(age)
            if D >= 7 and age >= 21:
                n = 7          # target cadence; up to 9 only on pages that clear the growth gates (§6)
            items = []
            items += [f"{sid} (runway·{next(x for x in RUNWAY_SRC if x['id'] == sid)['cta']})" for sid in rw_day.get(p, {}).get(D, [])]
            items += [f"{sid} (launch·{next(x for x in RUNWAY_SRC if x['id'] == sid)['cta']})" for sid in LAUNCH_FIXED[p].get(D, [])]
            if 7 <= D <= 13 and LEGACY_WEEK2[p]:
                items.append(f"{LEGACY_WEEK2[p].pop(0)} (blitz library, JOIN-path terms)")
            while len(items) < n:
                items.append(queue[p].pop(0) if queue.get(p) else "NEW (growth engine: winner remix / idea miner)")
            ig_trial = 1 if age >= 7 else 0
            text = 2 if age < 7 else (3 if age < 14 else (5 if 0 <= D <= 6 else 4))
            rows.append((D, stage, PAGE[p], len(items), ig_trial, text, items))
        for handle, start in LATER_PAGES:   # later pages: canon rollout days relative to page day 1, never on D0
            sd = -R + start - 1
            if sd == 0: sd = 1
            if D >= sd:
                n = page_cadence(D - sd) if handle != "@changyin.espanol" else 3
                rows.append((D, stage, handle, n, 1 if D - sd >= 7 else 0, 2, ["page library + NEW (see CONTENT_SYSTEM §8.1)"]))
    return rows


def runway_calendar_md(rows, R):
    L = [f"| D | Stage | Page | Videos/platform | IG Trial | Threads/X text | Posts (in slot order) |", "|---|---|---|---|---|---|---|"]
    for D, st, pg, n, tr, tx, items in rows:
        new = [i for i in items if i.startswith("NEW (growth engine")]
        shown = [i for i in items if not i.startswith("NEW (growth engine")] + ([f"NEW ×{len(new)} (growth engine: winner remix / idea miner)"] if new else [])
        L.append(f"| {D:+d} | {st} | {pg} | {n} | {tr} | {tx} | {' · '.join(shown)} |")
    return "\n".join(L)


def runway_calendar_summary(all_rows):
    L = ["| Runway | Pages on D0 | Video masters before D0 (3 launch pages) | Avg videos/page/platform on D0–D6 | Total video masters D−R…D+30 (all pages) | Runway scripts placed | Launch scripts placed |",
         "|---|---|---|---|---|---|---|"]
    for R, rows in all_rows.items():
        pre = sum(n for D, st, pg, n, *_ in rows if D < 0 and pg in ("@changyin", "@sunyoon.kitchen", "@changandsun"))
        lw = [n for D, st, pg, n, *_ in rows if 0 <= D <= 6 and pg in ("@changyin", "@sunyoon.kitchen", "@changandsun")]
        pages0 = len({pg for D, st, pg, *_ in rows if D == 0})
        tot = sum(r[3] for r in rows)
        rws = sum(1 for r in rows for i in r[6] if "(runway·" in i)
        lch = sum(1 for r in rows for i in r[6] if "(launch·" in i)
        L.append(f"| {R} days | {pages0} | {pre} | {sum(lw)/len(lw):.1f} | {tot} | {rws}/25 | {lch}/15 |")
    return "\n".join(L)


# ---------------- paid ad scripts (ADS_SCRIPTS.md / ad_scripts.json) ----------------
AD_FORMATS = ("UGC talking head", "Follow-along", "Quiz", "Sun blunt", "Adult-child gift")
# ADS.md §1 + §7: Meta personal-attribute, health-condition, before/after and fall/agency rules. Case-insensitive.
AD_RULES = [
    ("condition word", r"\b(pain(ful)?|aches?|aching|stiff(ness)?|sore(ness)?|arthriti\w*|osteo\w*|diabet\w*|blood (pressure|sugar)|hypertens\w*|cholesterol|insomnia|anxi\w*|depress\w*|menopaus\w*|constipat\w*|bloat\w*|gut|ibs|reflux|sciatica|neuropath\w*|incontinen\w*|dementia|memory loss|alzheim\w*|heart (disease|condition|attack|problem)s?|stroke|obes\w*|overweight|weight loss|lose weight|injur\w*|surgery|replacement|sarcopeni\w*|frail\w*|diseases?|disorders?|symptoms?|kidneys?|liver|inflammat\w*|dizz\w*|fatigue|tired(ness)?|chronic|conditions?)\b"),
    ("fall / agency / screening claim", r"\b(falls?|falling|fallen|fall[- ]risk|cdc|steadi|prevent\w*|screening|at[- ]risk)\b"),
    ("before/after transformation", r"\b(before (and|&|/) ?after|transform\w*|results in \d+ days)\b"),
    ("viewer personal attribute", r"\b(are you|you're|you are) (over|older|a senior|\d\d|in your \d0s)\b|\bat your age\b|\byour (age|knees?|back|hips?|joints?|balance|bones?|body|weight|health|legs|muscles?|heart|condition|pain)\b|\bif you('ve| have)? (fallen|struggle|suffer|been diagnosed)\b"),
    ("fear / urgency bait", r"\b(before it'?s too late|don'?t wait until|only \d+ (spots|left)|ends (tonight|at midnight)|last chance|hurry up|act now)\b"),
]


def load_ads():
    spec = importlib.util.spec_from_file_location("ad_scripts_src", os.path.join(DATA, "ad_scripts_src.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def ad_published_text(a):
    return {"hooks": " | ".join(a["hooks"]), "body_vo": " ".join(b[1] for b in a["body"]), "body_ost": " ".join(b[2] for b in a["body"]),
            "primary_text": a["primary"], "headline": a["headline"], "end_card": a["end"], "cta": a["cta"]}


def validate_ads(M):
    P, ids = [], set()
    ads = M.ADS
    if len(ads) != 40:
        P.append(f"ads: expected 40, found {len(ads)}")
    for a in ads:
        aid = a["id"]
        if aid in ids: P.append(f"{aid}: duplicate id")
        ids.add(aid)
        if a["fmt"] not in AD_FORMATS: P.append(f"{aid}: format '{a['fmt']}' not in {AD_FORMATS}")
        if len(a["hooks"]) != 3: P.append(f"{aid}: needs exactly 3 hook variants")
        for h in a["hooks"]:
            if len(h.split()) > 10: P.append(f"{aid}: hook variant >10 words (must play in the first 2 s): {h!r}")
        if "AI character" not in a["primary"][:220]: P.append(f"{aid}: 'AI character' disclosure not in the first lines of primary text (ADS rule 1)")
        if not any("AI character" in b[2] or "AI character" in b[1] for b in a["body"][:2]) and a["fmt"] != "Adult-child gift" and "carousel" not in a["concept"].lower():
            pass  # the burned-in 'AI character' tag is required on every frame (production rule); body mention is optional
        if a["offer"] == "founding":
            if M.FOUNDING_LINE not in a["primary"]: P.append(f"{aid}: founding offer line (full recurring terms) missing from primary text")
        elif a["offer"] == "gift":
            if M.GIFT_LINE not in a["primary"]: P.append(f"{aid}: gift terms line missing from primary text (S-04)")
        else:
            P.append(f"{aid}: unknown offer '{a['offer']}'")
        if len(a["headline"]) > 45: P.append(f"{aid}: headline >45 chars ({len(a['headline'])})")
        if not a.get("compliance"): P.append(f"{aid}: missing compliance note")
        txt = ad_published_text(a)
        allt = " ".join(txt.values()) + " " + M.STARTER_LINE + " " + M.GIFT_STARTER_LINE
        for name, rx in AD_RULES:
            for mm in re.finditer(rx, allt, flags=re.I):
                P.append(f"{aid}: ad rule '{name}': '{mm.group(0)}' … {allt[max(0, mm.start()-40): mm.end()+20]!r}")
        P.extend(blocked_claims_scan(aid, txt))
        P.extend(mortality_hits(aid, txt, {}))
        P.extend(outcome_claim_hits(aid, txt, {"hooks": txt["hooks"], "on_screen": txt["body_ost"], "headline": txt["headline"], "end_card": txt["end_card"]}))
    return P


def ad_to_json(a, M):
    starter_line = M.STARTER_LINE if a["offer"] == "founding" else M.GIFT_STARTER_LINE
    offer_line = M.FOUNDING_LINE if a["offer"] == "founding" else M.GIFT_LINE
    return {
        "id": a["id"], "source_concept": a["concept"], "format": a["fmt"], "character": a["character"], "audience": a["audience"],
        "length_seconds": a["secs"], "hook_variants_first_2s": a["hooks"],
        "body": [{"t": b[0], "vo_or_action": b[1], "on_screen_text": b[2]} for b in a["body"]],
        "on_screen_text": ["AI character (burned-in tag, top-left, full contrast, every frame)"] + [b[2] for b in a["body"]] + [a["end"]],
        "cta_button": a["cta"], "destination": a["dest"], "starter_variant_destination": "/b?t=BOOK" if a["offer"] == "founding" else "/q/a?mode=helper",
        "primary_text": a["primary"], "headline": a["headline"], "end_card": a["end"],
        "offer": a["offer"], "offer_line": offer_line, "starter_variant_line": starter_line,
        "starter_variant_end_card": M.END_STARTER, "optimization_event": a["optimize"], "compliance_note": a["compliance"],
        "ad_name": f"BLITZ_{a['audience'].split(',')[0].strip().replace(' ', '')}_{a['id']}_{{hook#}}_{a['fmt'].split()[0].upper()}_{{yyyymmdd}}",
    }


def ads_md(M):
    ads = M.ADS
    L = ["# ADS_SCRIPTS.md: 40 Meta ad scripts for the founding launch\n"]
    L.append("Built from ADS.md's 25 concepts (and its hook bank) for the BLITZ canon's **Founding Membership** (cells F25/F30, charged today), with a **starter variant line** on every ad (CANON UPDATE 3's launch default, cell B: $12 today = both Starter Books + the first founding month, then $25/mo) so the same creative runs in both live cells (OFFER.md §0.1; the day-10 and day-40 gates pick the winner). There is no $1 trial. Paid ads run only after the BLITZ.md §11 gate. Machine-readable copy: `data/content/ad_scripts.json`. Source: `data/content/ad_scripts_src.py`, validated by `python3 tools/build_content.py` (ADS.md §1/§7 rules + prompts/blocked_claims.json).\n")
    fc = collections.Counter(a["fmt"] for a in ads)
    L.append("**Mix:** " + " · ".join(f"{k} {fc[k]}" for k in AD_FORMATS) + f". Founding-offer ads: {sum(a['offer']=='founding' for a in ads)} · gift ads: {sum(a['offer']=='gift' for a in ads)}.\n")
    L.append("## Rules every ad follows\n")
    L.append("1. **AI disclosure:** burned-in `AI character` tag top-left from frame 1 (full contrast, never faded); 'AI character' in the first line of primary text; C2PA metadata left intact so Meta's AI label applies.")
    L.append("2. **No condition words, no viewer attributes, no before/after, no outcome, screening or agency claims, no mortality language.** The validator rejects them in hooks, body, on-screen text, primary text, headline and end card.")
    L.append("3. **Offer terms wherever a price appears.** Founding ads carry the full Founding Membership line (below); gift ads carry the gift line; starter variants carry the starter line. No countdowns, no 'spots left': the cap is the first 5,000 members or `{{FOUNDING_CLOSE_DATE}}`, whichever comes first, with the real count on the terms page (FUNNEL.md `{{COUNT_LINE}}`). Cancel copy says online, two screens at most; it never mentions texting and never denies the billing phone line.")
    L.append("4. **Reviewer gate:** no reviewer is signed, so only FALLBACK wording ships (no review or credential claims). Concept 14 runs as 14-F.")
    L.append("5. **Product-led:** every video shows a real product screen (session, level switch, retest chart, recipe card, cancel flow, gift card).")
    L.append("6. **Design:** captions 60–72 px, Rice on Ink or Ink on Paper, max 2 lines; no gray text; no slash or mono-label decorations.\n")
    L.append("## Offer lines (exact text)\n")
    L.append(f"- **Founding Membership (the plain $25 page, /join):** {M.FOUNDING_LINE}")
    L.append(f"- **Starter variant (launch default, cell B):** {M.STARTER_LINE} Destination `/b?t=BOOK`. End card: {M.END_STARTER}.")
    L.append(f"- **Gift:** {M.GIFT_LINE} Starter variant: {M.GIFT_STARTER_LINE}")
    L.append(f"- **Founding end card:** {M.END_FOUNDING}\n")
    L.append("## Optimization (Meta events)\n")
    L.append("- **Founding and quiz ads:** optimize for `Subscribe`, sent server-side (CAPI) at the founding checkout with value = month-one price and deduplicated with `Purchase`. In the T25 cell, `Subscribe` fires on the day-7 conversion, so optimize that cell for `StartTrial` with its modelled value (ADS.md §5.1).")
    L.append("- **Gift ads:** optimize for `Purchase` (value = gift price). Gifts are cash today, not MRR (BLITZ.md), so judge them on recipient conversion at gift end.")
    L.append("- **If the pixel or domain is health-restricted** (ADS.md §4.1): fall back to `Purchase`, then `Lead` with a cost cap, and judge on back-end MRR added per $ (BLITZ.md kill/scale table).")
    L.append("- **Naming:** `BLITZ_FOUNDING_{aud}_{ad}_{hook#}_{fmt}_{yyyymmdd}` for every ad that states the founding offer (the cap auto-pause pauses ads whose name contains `FOUNDING`, BLITZ_OPS.md §1.5 gap 4) and `BLITZ_GIFT_…` for gift ads, one ad set per ad, 3 hook variants as 3 ads. Days 1–3 decide on cost per purchase and purchase ÷ opt-in (BLITZ.md rules).\n")
    L.append("## Index\n")
    L.append("| ID | Format | Concept | Audience | Offer | Destination | Headline |\n|---|---|---|---|---|---|---|")
    for a in ads:
        L.append(f"| {a['id']} | {a['fmt']} | {a['concept']} | {a['audience']} | {a['offer']} | `{a['dest']}` | {a['headline']} |")
    for a in ads:
        j = ad_to_json(a, M)
        L.append(f"\n---\n\n## {a['id']}: {a['concept']}")
        L.append(f"**Format** {a['fmt']} · **Character** {a['character']} · **Audience** {a['audience']} · **Length** {str(a['secs']) + ' s' if a['secs'] else 'static carousel'} · **CTA button** {a['cta']} → `{a['dest']}` (starter variant → `{j['starter_variant_destination']}`)\n")
        L.append("**Hook variants (first 2 s; each ships as its own ad):**")
        for i, h in enumerate(a["hooks"], 1):
            L.append(f"{i}. \"{h}\"")
        L.append("\n| Time | VO / action | On-screen text |\n|---|---|---|")
        L.append("| 0–2 | Hook variant (spoken + on screen) | Hook text + `AI character` tag |")
        for b in a["body"]:
            L.append(f"| {b[0]} | {b[1]} | {b[2]} |")
        L.append(f"| end | End card | {a['end']} |")
        L.append(f"\n**Primary text:**\n```\n{a['primary']}\n```")
        L.append(f"**Starter variant (cell B):** replace the offer line with \"{j['starter_variant_line']}\"  ")
        L.append(f"**Headline:** {a['headline']}  ")
        L.append(f"**Optimization:** {a['optimize']}  ")
        L.append(f"**Compliance note:** {a['compliance']}")
    return "\n".join(L) + "\n"


def coverage_md(scripts, M):
    L = ["# SCRIPTS_COVERAGE.md: organic and paid coverage\n"]
    L.append(f"Generated by `python3 tools/build_content.py` from {len(scripts)} organic scripts (S01–S{len(scripts):02d}) and {len(M.ADS)} ad scripts (A01–A{len(M.ADS)}).\n")
    pages = ["@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength", "@changyin.mobility", "@sunyoon"]
    def table(title, key, keys, note=""):
        L.append(f"## {title}\n")
        if note: L.append(note + "\n")
        L.append("| Key | " + " | ".join(pages) + " | Total |\n|---|" + "---|" * (len(pages) + 1))
        for k in keys:
            row = [sum(1 for s in scripts if s["page"] == p and key(s) == k) for p in pages]
            if sum(row):
                L.append(f"| {k} | " + " | ".join(str(x) if x else "·" for x in row) + f" | {sum(row)} |")
        tot = [sum(1 for s in scripts if s["page"] == p) for p in pages]
        L.append("| **Total** | " + " | ".join(f"**{x}**" for x in tot) + f" | **{sum(tot)}** |\n")
    L.append("## Hook grammar (POSTDB_FINDINGS §3/§8 rule 3)\n")
    L.append("Classified from the spoken hook text by `proven_grammar()` in tools/build_content.py, not from tags. The build fails below 45%.\n")
    prov = [s for s in scripts if s["_proven"]]
    L.append(f"**Proven-grammar share: {len(prov)}/{len(scripts)} = {len(prov)/len(scripts):.0%}** (S01–S60: {sum(1 for s in prov if int(s['id'][1:]) < V2_FROM)}/60 · S61–S150: {sum(1 for s in prov if V2_FROM <= int(s['id'][1:]) < RUNWAY_FROM)}/90 · S151–S190: {sum(1 for s in prov if int(s['id'][1:]) >= RUNWAY_FROM)}/40).\n")
    L.append(f"| Grammar | Scripts | Share of {len(scripts)} | Example |\n|---|---|---|---|")
    names = {"IF_EVERY": "If you [habit] every [time], [change]", "NOT_X": "The number one ___ / 'not X, not Y'", "MYTH": "Myth-bust (quoted or questioned viral claim)", "WATCH": "…and just watch what happens"}
    for k in PROVEN:
        ss = [s for s in scripts if k in s["_proven"]]
        ex = ss[0]["beats"][0][2] if ss else ""
        L.append(f"| {names[k]} | {len(ss)} | {len(ss)/len(scripts):.0%} | {ss[0]['id'] if ss else ''}: \"{ex}\" |")
    L.append(f"| **Any proven grammar** (a hook can match two) | **{len(prov)}** | **{len(prov)/len(scripts):.0%}** | |\n")
    L.append("| Proven share by page | " + " | ".join(f"{p}" for p in ["@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength", "@changyin.mobility", "@sunyoon"]) + " |\n|---|---|---|---|---|---|---|")
    L.append("| Scripts | " + " | ".join(f"{sum(1 for s in prov if s['page']==p)}/{sum(1 for s in scripts if s['page']==p)}" for p in ["@changyin", "@sunyoon.kitchen", "@changandsun", "@changyin.strength", "@changyin.mobility", "@sunyoon"]) + " |\n")
    L.append("Hashtags: no script carries a condition hashtag (validator rule `CONDITION_HASHTAG`, AUDIT_BUSINESS F15).\n")
    L.append("## Virality gate (VIRALITY_SYSTEM.md §2, `tools/virality.py`)\n")
    vs = [s["_virality"] for s in scripts if s.get("_virality")]
    L.append(VIR.report(vs) + f". Hard gate (build fails) from S{VIRALITY_HARD_FROM}; launch/offer scripts need ≥{VIRALITY_OFFER_FLOOR}; "
             f"S01–S{VIRALITY_HARD_FROM - 1} below {VIR.THRESHOLD} are marked `REWRITE` and never scheduled.\n")
    L.append("| Band | Scripts |\n|---|---|")
    for name, lo, hi in (("top decile ≥85", 85, 1000), ("70–84", 70, 85), ("60–69 (pass)", 60, 70), ("below 60", 0, 60)):
        ids = [v["id"] for v in vs if lo <= v["score"] < hi]
        L.append(f"| {name} | {len(ids)}: {', '.join(ids)} |")
    rw = [v for v in vs if v.get("gate") == VIRALITY_LEGACY_GATE]
    L.append(f"\n**REWRITE backlog (legacy, unscheduled):** {len(rw)}: " + ", ".join(f"{v['id']} ({v['score']})" for v in rw) + "\n")
    hc = collections.Counter(v["hook_class"] for v in vs)
    L.append("Hook classes: " + " · ".join(f"{k} {n}" for k, n in hc.most_common()) + ".\n")
    L.append("## Summary\n")
    new = [s for s in scripts if int(s["id"][1:]) >= V2_FROM]
    L.append(f"- Organic scripts: **{len(scripts)}** ({len(scripts) - len(new)} original + {len(new)} expansion, of which {sum(1 for s in new if s.get('launch'))} are founding-launch-week).")
    L.append(f"- Expansion scripts with a visible physical demo (movement or food/prop demo on screen): {sum(1 for s in new if s.get('demo'))}/{len(new)}; target length 30–59 s: {sum(1 for s in new if 30 <= s['secs'] <= 59)}/{len(new)}; spoken words {min(s['_wc'] for s in new)}–{max(s['_wc'] for s in new)}.")
    gram = collections.Counter(g for s in new for g in s["grammar"])
    L.append("- Expansion grammar tags: " + " · ".join(f"{g} {gram[g]}" for g in sorted(gram, key=lambda x: -gram[x])) + ".")
    ser = collections.Counter(s["series"].split(":")[0].split("#")[0].strip() for s in new if s.get("series"))
    L.append("- Series: " + " · ".join(f"{k} {v}" for k, v in ser.items()) + ".")
    L.append(f"- Every expansion script has a unique hook (H301–H390), a ~3-second skip/safety line, and a unique frame-1 set + prop; the validator enforces all three across pages.\n")
    table("Page × pillar", lambda s: s["pillar"], sorted(PILLAR), "Pillar names: " + " · ".join(f"{k} {v}" for k, v in PILLAR.items()) + ".")
    table("Page × format", lambda s: s["format"], sorted({s["format"] for s in scripts}, key=lambda x: int(x[1:])),
          "F38 = Doors Open / Offer Card and F39 = Pinned Post were added for the launch week (CONTENT_SYSTEM.md §2).")
    table("Page × CTA keyword", lambda s: s["cta"], sorted(CTA_OK))
    L.append("## Page × hook grammar (expansion scripts only; a script can carry several)\n")
    L.append("| Grammar | " + " | ".join(pages) + " | Total |\n|---|" + "---|" * (len(pages) + 1))
    for g in sorted(gram, key=lambda x: -gram[x]):
        row = [sum(1 for s in new if s["page"] == p and g in s["grammar"]) for p in pages]
        L.append(f"| {g} | " + " | ".join(str(x) if x else "·" for x in row) + f" | {sum(row)} |")
    L.append("")
    L.append("## Page × pillar × format × CTA (every combination in use)\n")
    L.append("| Page | Pillar | Format | CTA | Scripts |\n|---|---|---|---|---|")
    combos = collections.defaultdict(list)
    for s in scripts:
        combos[(s["page"], s["pillar"], s["format"], s["cta"])].append(s["id"])
    for (p, pl, f, c), ids in sorted(combos.items(), key=lambda x: (pages.index(x[0][0]), x[0][1], int(x[0][2][1:]), x[0][3])):
        L.append(f"| {p} | {pl} | {f} | {c} | {', '.join(ids)} |")
    L.append("\n## Paid ads: format × audience × offer\n")
    L.append("| Format | Ads | Audiences | Offer | Destinations |\n|---|---|---|---|---|")
    for f in AD_FORMATS:
        A = [a for a in M.ADS if a["fmt"] == f]
        L.append(f"| {f} | {len(A)} ({', '.join(a['id'] for a in A)}) | {', '.join(sorted({x.strip() for a in A for x in a['audience'].split(',')}))} | {', '.join(sorted({a['offer'] for a in A}))} | {', '.join(sorted({a['dest'] for a in A}))} |")
    src = collections.Counter(a["concept"].split()[0] for a in M.ADS)
    L.append("\nADS.md concepts used as sources: " + ", ".join(f"{k} ×{v}" for k, v in sorted(src.items())) + ". Concepts 14 (real PT), 19 (real paid family) and 20 (real members) need real people; 14 and 19 run in FALLBACK/AI-character form (A09, A39) and 20 waits for verified member data.")
    return "\n".join(L) + "\n"


def runway_md(rw, hooks):
    """RUNWAY_SCRIPTS.md: the S151–S190 organic runway + launch-week set on its own (same renderer as SCRIPTS.md)."""
    body = scripts_md(rw, hooks).split("\n## Index\n", 1)[1]
    run = [s for s in rw if int(s["id"][1:]) < RUNWAY_LAUNCH_FROM]
    lau = [s for s in rw if int(s["id"][1:]) >= RUNWAY_LAUNCH_FROM]
    prov = [s for s in rw if s["_proven"]]
    def mix(ss, key):
        return " · ".join(f"{k} {v}" for k, v in sorted(collections.Counter(key(s) for s in ss).items(), key=lambda x: -x[1]))
    L = [f"# RUNWAY_SCRIPTS.md: {len(rw)} organic runway + launch-week scripts (S{RUNWAY_FROM}–S{RUNWAY_FROM + len(rw) - 1})\n"]
    L.append("Written for CANON UPDATE 2 (Oct 1 2026): organic-first, Shopify ebook front end, no $1 trial, founding membership offered after the ebook purchase. Schedule, platform rules and the launch-week interlock: ORGANIC_ENGINE.md. DM flows: FUNNEL.md §4.18 (WAITLIST) and §4.19 (BOOK); JOIN stays §4.17. Source: `data/content/scripts_runway.py` (hooks H391–H430 in `data/content/hooks.psv`); machine-readable copy `data/content/runway_scripts.json`. Validated with the rest of the library by `python3 tools/build_content.py`.\n")
    L.append(f"- **Runway (S{RUNWAY_FROM}–S{RUNWAY_LAUNCH_FROM - 1}): {len(run)}** · speakers {mix(run, lambda s: s['speaker'])} · CTAs {mix(run, lambda s: s['cta'])}. WAITLIST is a minority CTA ({sum(s['cta'] == 'WAITLIST' for s in run)}/{len(run)}); the value keywords route to the waitlist while runway mode is on. No price, no '$', no subscription talk before checkout opens (validator).")
    L.append(f"- **Launch week (S{RUNWAY_LAUNCH_FROM}–S{RUNWAY_FROM + len(rw) - 1}): {len(lau)}** · speakers {mix(lau, lambda s: s['speaker'])} · CTAs {mix(lau, lambda s: s['cta'])}. Every BOOK script states `{{{{EBOOK_PRICE}}}}`, one-time, not a subscription, yours to keep; every script that mentions the membership carries the full terms (price/month, renews monthly, cancel online anytime, 14-day money-back guarantee, locked for as long as you stay subscribed, first 5,000 with the live count). No countdowns, no 'spots left', no midnight price jumps.")
    L.append(f"- **Proven hook grammar: {len(prov)}/{len(rw)} = {len(prov)/len(rw):.0%}** (floor 45%): " + mix([s for s in rw for _ in s['_proven']] and [dict(g=g) for s in rw for g in s['_proven']], lambda d: d['g']) + ".")
    L.append("- **Every script:** AI disclosure (burned-in `AI character` tag + caption footer, auto-appended), a ~3-second who-should-skip line, an evidence ID on every health claim, no condition hashtags, no fall-outcome / percentage-outcome / mortality framing, Sun Yoon always by her own name, Chang never 'Master'.")
    L.append("- **Placeholders:** `{{EBOOK_PRICE}}` (live ebook cell: $7 / $12 / $15, default $12), `{{FOUNDING_PRICE}}` ($25 default), `{{DOMAIN}}`. One value per render, filled by the pipeline from live config.\n")
    L.append("## Index\n" + body)
    return "\n".join(L) + "\n"


# ---------------- Wave 2: GEN scripts for the posting plan (data/content/scripts_wave2.py) ----------------
# One source script per plan uniqueness_group that was "GEN-needed" from D−7 to D+7. Validated with the library's
# rules plus plan-match, render-lane, running-bit rotation and 7-word-shingle uniqueness, then rendered to
# WAVE2_SCRIPTS.md and data/content/wave2_scripts.json. tools/assign_scripts.py writes the ids into the plan CSV.
WAVE2_FILE = "scripts_wave2"
PLAN_CSV = os.path.join(DATA, "posting_plan_90d.csv")
CALL_SHEET = os.path.join(ROOT, "production", "performer", "call_sheet.csv")
WAVE2_D_FROM, WAVE2_D_TO = -7, 7
WAVE2_TIMES = {6: ["0-3", "3-11", "11-19", "19-27", "27-35", "35-42"],
               7: ["0-3", "3-10", "10-17", "17-24", "24-31", "31-37", "37-42"],
               8: ["0-3", "3-9", "9-15", "15-21", "21-27", "27-32", "32-37", "37-42"]}
SPEAKER_PAGE = {"CHANG": "@changyin", "SUN": "@sunyoon.kitchen", "DUO": "@changandsun"}
# CHARACTERS.md §7: the 24 running bits, each with the words that must show up when it's used (spoken, on-screen or shot)
BITS = {1: ("NO MIRROR FLEXING", r"mirror flexing"), 2: ("I'm older, so I'm right", r"older,? so (i'm|she's|i am|she is) (also )?right"),
        3: ("Hips. Now.", r"hips\. now"), 4: ("The study card from the shorts pocket", r"show me the study|study card from|shorts pocket"),
        5: ("Dumpling count", r"dumpling"), 6: ("The tank top in January", r"tank top"), 7: ("Seven out of ten", r"seven out of ten|7/10"),
        8: ("Mandu the cat", r"\bmandu\b"), 9: ("Fridge balance leaderboard", r"leaderboard"), 10: ("Short version:", r"short version"),
        11: ("The apron", r"\bapron\b"), 12: ("Frank's excuses", r"\bfrank\b"), 13: ("The welding metaphors", r"\bweld"),
        14: ("Sun's visor", r"\bvisor\b"), 15: ("Printer ink", r"\bprinter\b"), 16: ("Aigo", r"\baigo\b"),
        17: ("The AI winks", r"\b(i'm|we're|he's|she's) (an )?ai\b|\bpixels?\b|\brender\b|\b4k\b"), 18: ("The anniversary countdown", r"anniversary"),
        19: ("Jajangmyeon Sunday", r"jajangmyeon"), 20: ("The hidden kettlebell", r"\bhid(e|es|den)?\b[^.]{0,60}kettlebell|kettlebell[^.]{0,60}\bhid(e|es|den)?\b"),
        21: ("Phone calls from Mina", r"\bmina\b"), 22: ("The chair called Coach", r"\bcoach\b"), 23: ("Write this down", r"write this down"),
        24: ("Old photos", r"\bphoto\b|\b1976\b")}
BIT_WINDOW_DAYS = 3        # the same bit never twice on one page inside any 3-day window
SHINGLE_N = 7
OFFER_AI_LINE = re.compile(r"\b(i'm|i am|we're|we are) (an )?ai\b|\bai (coach|characters?)\b", re.I)
PLAN_GRAMMARS = {"OBJ3", "IF_EVERY", "MYTH_NOT", "WATCH", "TEST_NOW", "SHARE", "DEMO"}


def load_wave2():
    spec = importlib.util.spec_from_file_location(WAVE2_FILE, os.path.join(DATA, WAVE2_FILE + ".py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    out = []
    for s in m.SCRIPTS:
        s = dict(s)
        if s["beats"] and len(s["beats"][0]) == 4:   # (speaker, spoken, on-screen, shot) → add time codes from the beat count
            s["beats"] = [(t,) + tuple(b) for t, b in zip(WAVE2_TIMES[len(s["beats"])], s["beats"])]
        s.setdefault("secs", 42); s.setdefault("wink", False); s.setdefault("series", "")
        s.setdefault("hook_id", "HW" + s["id"][1:])
        s["launch"] = s["cta"] in ("BOOK", "JOIN")
        out.append(s)
    return out


def load_plan_groups(path=PLAN_CSV):
    groups = collections.OrderedDict()
    if not os.path.exists(path):
        return groups
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        groups.setdefault(r["uniqueness_group"], []).append(r)
    return groups


def shingles(text, n=SHINGLE_N):
    w = [t.strip("'") for t in re.findall(r"[a-z0-9']+", text.lower().replace("\u2019", "'"))]
    w = [t for t in w if t]
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def plan_grammar_ok(g, hook, s):
    h = hook.lower().replace("’", "'")
    prov = proven_grammar(hook, s)
    if g == "IF_EVERY": return "IF_EVERY" in prov
    if g == "WATCH": return "WATCH" in prov
    if g == "MYTH_NOT": return "NOT_X" in prov or "MYTH" in prov
    if g == "OBJ3":
        first = [re.sub(r"[^\w'-]", "", w).lower().strip("'") for w in hook.split()[:3]]
        return any(w.startswith(s.get("obj", "@@").lower()) for w in first)
    if g == "TEST_NOW": return bool(re.search(r"\b(right now|now|today|seconds?|count|score yourself|try it)\b", h))
    if g == "SHARE": return bool(re.search(r"\b(send|share|tag|forward)\b", h))
    if g == "DEMO": return bool(s.get("demo", True)) and bool(re.search(r"\b(watch|look|here's|this is|like this|see)\b", h))
    return False


def validate_wave2(w2, library, hooks, ev_ids, plan_groups):
    P = []
    hook_ids = {h["id"] for h in hooks}
    clips = {r["id"] for r in csv.DictReader(open(CALL_SHEET, newline="", encoding="utf-8"))} if os.path.exists(CALL_SHEET) else set()
    ids = [s["id"] for s in w2]
    if len(set(ids)) != len(ids): P.append("wave2: duplicate script ids")
    lib_ids = {s["id"] for s in library}
    for s in w2:
        if s["id"] in lib_ids: P.append(f"{s['id']}: wave2 id collides with the library")
    groups_seen = collections.Counter(s.get("group") for s in w2)
    for g, n in groups_seen.items():
        if n > 1: P.append(f"wave2: group {g} has {n} scripts (one source script per uniqueness group)")
    # every GEN-needed group in the D−7…D+7 window is covered
    for g, rows in plan_groups.items():
        d = int(rows[0]["day_index"])
        if WAVE2_D_FROM <= d <= WAVE2_D_TO and any(r["script_id"] == "GEN-needed" for r in rows) and g not in groups_seen:
            P.append(f"WARN wave2: plan group {g} (D{d:+d}) is GEN-needed but has no wave2 script yet")
    lib_sh = set()
    for s in library:
        lib_sh |= shingles(" ".join(b[2] for b in s["beats"]))
    seen_sh = {}
    seen_line = {re.sub(r"[^a-z0-9 ]", "", s["beats"][0][2].lower()): s["id"] for s in library}
    seen_sp = {}
    for s in library:
        if s.get("prop"): seen_sp.setdefault((s["beats"][0][4].split("|")[0].strip(), s["prop"].lower()), (s["id"], s["page"]))
    bit_use = collections.defaultdict(list)   # page -> [(day, bit, id)]
    for s in w2:
        sid = s["id"]
        rows = plan_groups.get(s.get("group"), [])
        if not rows:
            P.append(f"{sid}: group {s.get('group')} not in the posting plan"); continue
        r0 = next((r for r in rows if r["render_lane"] != "carousel_text"), rows[0])
        day = int(r0["day_index"])
        s["_day"], s["_date"] = day, r0["date"]
        for r in rows:
            if r["script_id"] not in ("GEN-needed", sid):
                P.append(f"{sid}: plan rows of {s['group']} already carry script {r['script_id']}")
                break
        want = {"page": r0["page"], "pillar": r0["pillar"], "format": r0["format"], "speaker": r0["character"],
                "lane": r0["render_lane"], "cta": r0["cta_keyword"]}
        for k, v in want.items():
            if s.get(k) != v:
                P.append(f"{sid}: {k} {s.get(k)!r} doesn't match the plan row ({v!r})")
        if SPEAKER_PAGE.get(s["speaker"]) != s["page"]:
            P.append(f"{sid}: speaker {s['speaker']} on {s['page']}")
        cta_type = {"BOOK": "book", "JOIN": "join", "WAITLIST": "waitlist"}.get(s["cta"], "none")
        if r0["cta_type"] != cta_type:
            P.append(f"{sid}: CTA type {cta_type} doesn't match the plan ({r0['cta_type']})")
        if not s.get("grammar") or s["grammar"][0] != r0["hook_grammar"]:
            P.append(f"{sid}: grammar[0] must be the plan's hook grammar {r0['hook_grammar']}")
        spoken = " ".join(b[2] for b in s["beats"] if b[2])
        ost = " ".join(b[3] for b in s["beats"])
        shots = " ".join(b[4] for b in s["beats"])
        s["_spoken"], s["_wc"] = spoken, words(spoken)
        hook = s["beats"][0][2]
        # --- library rules (validate + validate_v2 + runway/launch offer rules)
        if s["hook_id"] in hook_ids: P.append(f"{sid}: hook id {s['hook_id']} collides with the hook bank")
        if s["cta"] not in CTA_OK: P.append(f"{sid}: CTA {s['cta']} not in keyword map")
        if f"Comment {s['cta']}" not in " ".join(b[2] for b in s["beats"][-2:]): P.append(f"{sid}: last beats don't say 'Comment {s['cta']}'")
        if not s["caption"].startswith(f"Comment {s['cta']}"): P.append(f"{sid}: caption line 1 must start with 'Comment {s['cta']}'")
        for e in s["ev"]:
            if e not in ev_ids: P.append(f"{sid}: evidence {e} not in EVIDENCE.md")
        if not s["ev"] and s["pillar"] not in ("P16", "P17", "P20"): P.append(f"{sid}: no evidence on a health pillar")
        if s["move"]:
            if not s.get("regression"): P.append(f"{sid}: movement without regression")
            if SUPPORT_TAGS & set(s["tags"]) and not re.search(r"counter|chair|wall|rail|sink|bed|sofa|headboard|bench", spoken + s["safety"], re.I):
                P.append(f"{sid}: movement without support cue")
        text = (spoken + " " + ost + " " + s["caption"]).lower()
        for pat in BANNED:
            for m, vtext in tn_finditer(pat, text):
                ctx = vtext[max(0, m.start() - 40): m.end() + 20].lower()
                if any(re.search(n, ctx) for n in NEGATION_OK): continue
                if s.get("myth") and not any(re.search(h, m.group(0)) for h in HARD_BLOCK): continue
                P.append(f"{sid}: banned pattern '{m.group(0)}' … {ctx!r}")
        if re.search(r"\bSun (Yin|Chang)\b|\bMrs\.? (Chang|Yin)\b", spoken + ost + s["caption"] + s["title"] + s["yt"]):
            P.append(f"{sid}: Sun Yoon keeps her own surname")
        for tag in s["ig"] + s["tt"]:
            if CONDITION_HASHTAG.search(tag): P.append(f"{sid}: condition hashtag {tag}")
        s["_proven"] = proven_grammar(hook, s)
        s["grammar_v2"] = s["grammar"]
        P.extend(validate_v2_core(s, ost))
        P.extend(virality_gate(s)[0])   # VIRALITY_SYSTEM.md §2: every generated script clears the same bar
        if not plan_grammar_ok(s["grammar"][0], hook, s):
            P.append(f"{sid}: hook doesn't do the plan grammar {s['grammar'][0]}: {hook!r}")
        for k in ("IF_EVERY", "WATCH"):
            if (k in s["grammar"]) != (k in s["_proven"]):
                P.append(f"{sid}: grammar tag {k} doesn't match the hook text")
        if set(s["grammar"]) - GRAMMARS - PLAN_GRAMMARS: P.append(f"{sid}: unknown grammar tag {set(s['grammar']) - GRAMMARS - PLAN_GRAMMARS}")
        everything = spoken + " " + ost + " " + s["caption"]
        if day < 0:   # runway: checkout closed
            if "$" in everything or "{{" in everything: P.append(f"{sid}: runway script states a price or offer placeholder")
            for m in re.finditer(r"\b(membership|subscri\w*|founding)\b", everything, re.I):
                P.append(f"{sid}: runway script mentions '{m.group(0)}'")
            if s["cta"] in ("BOOK", "JOIN"): P.append(f"{sid}: offer CTA during the runway")
        elif s["cta"] == "WAITLIST":
            P.append(f"{sid}: WAITLIST is a runway-only keyword")
        if s["cta"] == "WAITLIST" and ("free" not in s["caption"].lower() or not re.search(r"\bfree\b", spoken, re.I)):
            P.append(f"{sid}: WAITLIST script must say it's free (spoken and caption)")
        if s["cta"] == "BOOK":
            for need in BOOK_TERMS:
                if need not in s["caption"]: P.append(f"{sid}: BOOK caption missing '{need}'")
            if "{{EBOOK_PRICE}}" not in spoken + ost or "one-time" not in spoken + ost:
                P.append(f"{sid}: BOOK spoken/on-screen text must state {{{{EBOOK_PRICE}}}} and 'one-time'")
        if s["cta"] in ("BOOK", "JOIN") and not OFFER_AI_LINE.search(spoken + " " + ost):
            P.append(f"{sid}: offer script needs a spoken or on-screen AI disclosure line")
        cap_wo = s["caption"].replace("not a subscription", "")
        so_wo = re.sub(r"not a subscription", "", spoken + " " + ost, flags=re.I)
        if day >= 0 and (MEMBER_MENTION.search(cap_wo) or MEMBER_MENTION.search(so_wo)):
            for need in MEMBER_TERMS:
                if need not in s["caption"]: P.append(f"{sid}: membership mentioned but caption missing '{need}'")
            if MEMBER_MENTION.search(so_wo):
                for need in ("{{founding_price}}", "cancel", "renew"):
                    if need not in (spoken + " " + ost).lower(): P.append(f"{sid}: membership mentioned in spoken/on-screen text without '{need}'")
        if re.search(r"\block(ed|s)?\b", everything, re.I) and "locked for as long as you stay subscribed" not in everything:
            P.append(f"{sid}: price-lock wording must be 'locked for as long as you stay subscribed'")
        if re.search(r"\b(forever|lifetime|for good)\b", everything, re.I): P.append(f"{sid}: open-ended price/term wording")
        if re.search(r"\b(spots?|seats?) left\b|\bends (tonight|at midnight)\b|\blast chance\b|\bhurry\b|\bonly \d+ left\b", everything, re.I):
            P.append(f"{sid}: urgency/scarcity wording (T-04)")
        # --- render lane
        if s["lane"] == "insert":
            if any(not b[1].endswith("-VO") for b in s["beats"]): P.append(f"{sid}: insert lane is voice-over only (speaker must end in -VO)")
            if re.search(r"lip-sync|to camera|\bMC DRV-", shots): P.append(f"{sid}: insert lane shot shows a face or a performer clip")
        elif s["lane"] == "talking_head":
            if shots.count("VEO INSERT") > 2: P.append(f"{sid}: talking_head allows at most 2 Veo inserts")
            if re.search(r"\bMC DRV-", shots) or s.get("clip"): P.append(f"{sid}: talking_head script references a performer clip")
            if any(b[1].endswith("-VO") for b in s["beats"]): P.append(f"{sid}: talking_head beats are lip-synced, not VO")
        elif s["lane"] == "movement":
            if s.get("clip") not in clips: P.append(f"{sid}: movement clip {s.get('clip')!r} not in production/performer/call_sheet.csv")
            elif f"MC {s['clip']}" not in s["beats"][0][4]: P.append(f"{sid}: frame 1 must cite the performer clip 'MC {s['clip']}'")
            if not s["move"]: P.append(f"{sid}: movement lane script must set move=True")
            if day < -2: P.append(f"{sid}: movement lane before the shoot (D−2)")
        else:
            P.append(f"{sid}: unknown lane {s['lane']}")
        # --- running bit
        b = s.get("bitn")
        if b not in BITS:
            P.append(f"{sid}: running bit number {b!r} not in CHARACTERS.md §7 (1–24)")
        else:
            if not re.search(BITS[b][1], (spoken + " " + ost + " " + shots).lower().replace("’", "'")):
                P.append(f"{sid}: running bit {b} ({BITS[b][0]}) not visible in the script")
            if b == 24 and s["pillar"] not in ("P16", "P17"): P.append(f"{sid}: old photos are for love/wisdom content only")
            bit_use[s["page"]].append((day, b, sid))
        # --- uniqueness
        norm = re.sub(r"[^a-z0-9 ]", "", hook.lower())
        if norm in seen_line: P.append(f"{sid}: hook line duplicates {seen_line[norm]}")
        seen_line[norm] = sid
        key = (s["beats"][0][4].split("|")[0].strip(), s["prop"].lower())
        if key in seen_sp and seen_sp[key][1] != s["page"]: P.append(f"{sid}: set+prop {key} already used on {seen_sp[key][1]} by {seen_sp[key][0]}")
        seen_sp.setdefault(key, (sid, s["page"]))
        for sh in shingles(spoken):
            if sh in lib_sh: P.append(f"{sid}: 7-word shingle repeats the library: '{sh}'")
            elif sh in seen_sh and seen_sh[sh] != sid: P.append(f"{sid}: 7-word shingle repeats {seen_sh[sh]}: '{sh}'")
            seen_sh.setdefault(sh, sid)
    for page, uses in bit_use.items():
        uses.sort()
        for i, (d1, b1, s1) in enumerate(uses):
            for d2, b2, s2 in uses[i + 1:]:
                if d2 - d1 >= BIT_WINDOW_DAYS: break
                if b1 == b2: P.append(f"{s2}: running bit {b1} repeats {s1} on {page} within {BIT_WINDOW_DAYS} days")
    if w2:
        share = sum(1 for s in w2 if s.get("_proven")) / len(w2)
        if share < PROVEN_MIN_SHARE: P.append(f"wave2: proven hook grammar share {share:.0%} < {PROVEN_MIN_SHARE:.0%}")
    for s in w2:   # SAFETY scans shared with the library
        pub = script_published_text(s)
        P.extend(blocked_claims_scan(s["id"], pub))
        prom = {"on_screen": pub["on_screen"], "thumbnail": s["thumb"], "title": s["title"], "yt_title": s["yt"], "hook_line": s["beats"][0][2]}
        P.extend(outcome_claim_hits(s["id"], pub, prom))
        P.extend(mortality_hits(s["id"], prom, {"spoken": pub["spoken"], "caption": pub["caption"]}))
    return P


def validate_v2_core(s, ost):
    """The POSTDB §8 / BLITZ structure rules from validate_v2 that don't depend on the S-number ranges."""
    sid, P = s["id"], []
    if not 70 <= s["_wc"] <= 130: P.append(f"{sid}: word count {s['_wc']} outside 70-130")
    if not 30 <= s["secs"] <= 59: P.append(f"{sid}: target {s['secs']} s outside 30-59 s")
    if int(s["beats"][-1][0].split("-")[1]) != s["secs"]: P.append(f"{sid}: last beat end != secs")
    if len(s["beats"][0][2].split()) > 22: P.append(f"{sid}: hook line >22 words")
    if len(s["beats"][0][3].split()) > 7: P.append(f"{sid}: frame-1 on-screen text >7 words")
    for k in ("prop", "grammar", "skip", "hcat", "obj", "group", "lane", "title", "thumb", "yt", "music", "note"):
        if not s.get(k): P.append(f"{sid}: missing field '{k}'")
    if s["hcat"] not in CAT_NAMES: P.append(f"{sid}: hook category {s['hcat']} unknown")
    if s.get("skip") and s["skip"] not in s["_spoken"] + " " + ost: P.append(f"{sid}: skip/safety line not found verbatim in spoken or on-screen text")
    if s["cta"] == "JOIN":
        for need in ("{{FOUNDING_PRICE}}/month", "renews monthly", "Cancel online anytime", "14-day money-back", "5,000"):
            if need not in s["caption"]: P.append(f"{sid}: JOIN caption missing '{need}'")
        so = (s["_spoken"] + " " + ost).lower()
        for need in ("{{founding_price}}", "cancel", "renew"):
            if need not in so: P.append(f"{sid}: JOIN spoken/on-screen text missing '{need}'")
    return P


def wave2_md(w2, hooks, plan_groups):
    fake = hooks + [dict(id=s["hook_id"]) for s in w2]
    body = scripts_md(w2, fake).split("\n## Index\n", 1)[1]
    for s in w2:
        extra = (f"**Plan group** `{s['group']}` · **First post** {s['_date']} (D{s['_day']:+d}) · **Render lane** {s['lane']}"
                 + (f" · **Performer clip** `{s['clip']}`" if s.get("clip") else "")
                 + f" · **Running bit** #{s['bitn']} {BITS[s['bitn']][0]} · **Plan grammar** {s['grammar'][0]}")
        body = body.replace(f"\n## {s['id']}: {s['title']}\n", f"\n## {s['id']}: {s['title']}\n{extra}  \n", 1)
    def mix(key):
        return " · ".join(f"{k} {v}" for k, v in sorted(collections.Counter(key(s) for s in w2).items(), key=lambda x: (-x[1], str(x[0]))))
    rows = sum(len(plan_groups.get(s["group"], [])) for s in w2)
    L = [f"# WAVE2_SCRIPTS.md: {len(w2)} generated source scripts ({w2[0]['id']}–{w2[-1]['id']}) for the posting plan, D{WAVE2_D_FROM:+d}…D{WAVE2_D_TO:+d}\n"]
    L.append(f"One source script per `uniqueness_group` that `data/content/posting_plan_90d.csv` marked `GEN-needed` from D{WAVE2_D_FROM:+d} (Oct 1) to D{WAVE2_D_TO:+d} (Oct 15): {len(w2)} groups, {rows} plan rows (each group posts once on all 6 platforms; Threads/X get the text cut). Source: `data/content/scripts_wave2.py`; machine-readable copy `data/content/wave2_scripts.json`. `python3 tools/assign_scripts.py` writes these ids into the plan's `script_id` column. Validated by `python3 tools/build_content.py` (validate_wave2) and `cd workers && python3 -m compliance scan ../data/content/wave2_scripts.json`.\n")
    L.append(f"- **Pages:** {mix(lambda s: s['page'])} · **speakers** {mix(lambda s: s['speaker'])} · **lanes** {mix(lambda s: s['lane'])}.")
    L.append(f"- **CTAs:** {mix(lambda s: s['cta'])}. Runway rows (D<0) carry no price, no '$' and no membership talk; WAITLIST says it's free. BOOK states `{{{{EBOOK_PRICE}}}}` one-time / not a subscription / yours to keep; JOIN carries price per month, monthly renewal, cancel online anytime, the 14-day money-back guarantee, 'locked for as long as you stay subscribed' and the real 5,000 cap. Every offer script has a spoken AI line.")
    prov = collections.Counter(g for s in w2 for g in s["_proven"])
    L.append(f"- **Proven hook grammar: {sum(1 for s in w2 if s['_proven'])}/{len(w2)} = {sum(1 for s in w2 if s['_proven'])/len(w2):.0%}** (floor 45%): " + " · ".join(f"{k} {v}" for k, v in prov.most_common()) + f". Plan grammars: {mix(lambda s: s['grammar'][0])}.")
    L.append(f"- **Render lanes:** movement scripts cite a performer clip from `production/performer/call_sheet.csv` in frame 1 (`MC DRV-…`); insert scripts are voice-over only (every beat speaker `-VO`, hands and props, no face); talking-head scripts use at most 2 Veo inserts.")
    L.append(f"- **Running bits:** every script carries one of the 24 (CHARACTERS.md §7); no bit repeats on a page inside {BIT_WINDOW_DAYS} days. Uses: " + " · ".join(f"#{k} {v}" for k, v in sorted(collections.Counter(s['bitn'] for s in w2).items())) + ".")
    L.append(f"- **Uniqueness:** no spoken {SHINGLE_N}-word shingle repeats across the {len(w2)} wave-2 scripts or the 190 library scripts; hook lines and set+prop combinations are new.")
    L.append("- **Every script:** 30–59 s (42 s target, 70–130 spoken words), a ~3-second who-should-skip line, evidence IDs on health claims, no condition hashtags, no fall-outcome / percentage-outcome / mortality framing, Sun Yoon always by her own name, Chang never 'Master', AI tag + caption footer auto-appended (SAFETY D-02/D-03).\n")
    L.append("## Index\n" + body)
    return "\n".join(L) + "\n"


def build_wave2(library, hooks, ev_ids):
    if not os.path.exists(os.path.join(DATA, WAVE2_FILE + ".py")):
        return [], "wave2: no source file"
    w2 = load_wave2()
    plan_groups = load_plan_groups()
    problems = validate_wave2(w2, library, hooks, ev_ids, plan_groups)
    # GEN-needed rows still being written (wave2 is produced in batches) are warnings, not failures
    warnings = [p for p in problems if p.startswith("WARN ")]
    problems = [p for p in problems if not p.startswith("WARN ")]
    if warnings:
        print(f"WARNINGS ({len(warnings)} GEN-needed plan groups without a wave2 script yet; first: {warnings[0][5:]})")
    if not problems:
        write_generated_md(os.path.join(ROOT, "WAVE2_SCRIPTS.md"), wave2_md(w2, hooks, plan_groups))
        out = []
        for s in w2:
            j = to_schema(s)
            j.update({"plan_group": s["group"], "render_lane": s["lane"], "performer_clip": s.get("clip", ""),
                      "running_bit_n": s["bitn"], "first_post_date": s["_date"], "day_index": s["_day"], "hook_grammar": s["grammar"]})
            out.append(j)
        json.dump(out, open(os.path.join(DATA, "wave2_scripts.json"), "w"), indent=1, ensure_ascii=False)
    prov = sum(1 for s in w2 if s.get("_proven"))
    summary = (f"wave2 scripts: {len(w2)} {dict(collections.Counter(s['speaker'] for s in w2))}; lanes {dict(collections.Counter(s['lane'] for s in w2))}; "
               f"proven grammar {prov}/{len(w2)}; CTAs {dict(collections.Counter(s['cta'] for s in w2))}; problems {len(problems)}")
    return problems, summary


GEN_HEADER = "> GENERATED by tools/build_content.py — edit the sources in data/content/, not this file.\n\n"


def write_generated_md(path, text):
    """Every generated .md starts with GEN_HEADER so nobody hand-edits it (a rebuild would overwrite the edit)."""
    open(path, "w").write(GEN_HEADER + text)


def main():
    ev_ids = load_evidence_ids()
    hooks = load_hooks()
    scripts = load_scripts()
    problems = validate(scripts, hooks, ev_ids)
    # hooks evidence check
    for h in hooks:
        for e in h["evidence"]:
            if e not in ev_ids:
                problems.append(f"{h['id']}: evidence {e} missing")
        if h["cta"] not in CTA_OK:
            problems.append(f"{h['id']}: CTA {h['cta']}")
        if len(h["hook"].split()) > 16:
            problems.append(f"{h['id']}: hook >16 words ({len(h['hook'].split())})")
    assert len(hooks) == N_HOOKS, len(hooks)
    assert sum(h["test_first"] for h in hooks) == 30
    assert len(scripts) == N_SCRIPTS, len(scripts)
    assert [s["id"] for s in scripts] == [f"S{i:02d}" for i in range(1, N_SCRIPTS + 1)], f"script IDs must run S01–S{N_SCRIPTS} in order"
    assert [s["hook_id"] for s in scripts if int(s["id"][1:]) >= RUNWAY_FROM] == [f"H{i}" for i in range(391, 431)], "S151–S190 use H391–H430 in order"
    orig = collections.Counter(s["speaker"] for s in scripts[:60])
    assert orig == {"CHANG": 30, "SUN": 20, "DUO": 10}, orig
    counts = collections.Counter(s["speaker"] for s in scripts)
    # SAFETY_RULES blocked-claims regexes (prompts/blocked_claims.json) over every published field of all 150 scripts
    bc_hits = []
    for s in scripts:
        bc_hits += blocked_claims_scan(s["id"], script_published_text(s))
    problems += bc_hits
    oc_hits = []
    for s in scripts:
        pub = script_published_text(s)
        prom = {"on_screen": pub["on_screen"], "thumbnail": s["thumb"], "title": s["title"], "yt_title": s["yt"], "hook_line": s["beats"][0][2]}
        oc_hits += outcome_claim_hits(s["id"], pub, prom)
        oc_hits += mortality_hits(s["id"], prom, {"spoken": pub["spoken"], "caption": pub["caption"]})
    for h in hooks:
        oc_hits += outcome_claim_hits(h["id"], {"hook": h["hook"]}, {"hook": h["hook"]})
        oc_hits += mortality_hits(h["id"], {"hook": h["hook"]}, {})
    problems += oc_hits
    # paid ads
    M = load_ads()
    ad_problems = validate_ads(M)
    problems += ad_problems

    write_generated_md(os.path.join(ROOT, "HOOKS.md"), hooks_md(hooks))
    json.dump(hooks, open(os.path.join(DATA, "hooks.json"), "w"), indent=1, ensure_ascii=False)
    with open(os.path.join(DATA, "hooks.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "category", "pillar", "format", "cta", "page", "speaker", "evidence", "test_first", "hook"])
        for h in hooks:
            w.writerow([h["id"], h["cat"], h["pillar"], h["format"], h["cta"], PAGE[h["page"]], h["speaker"], ";".join(h["evidence"]), int(h["test_first"]), h["hook"]])
    write_generated_md(os.path.join(ROOT, "SCRIPTS.md"), scripts_md(scripts, hooks))
    write_generated_md(os.path.join(ROOT, "ADS_SCRIPTS.md"), ads_md(M))
    json.dump([ad_to_json(a, M) for a in M.ADS], open(os.path.join(DATA, "ad_scripts.json"), "w"), indent=1, ensure_ascii=False)
    write_generated_md(os.path.join(ROOT, "SCRIPTS_COVERAGE.md"), coverage_md(scripts, M))
    json.dump([to_schema(s) for s in scripts], open(os.path.join(DATA, "scripts.json"), "w"), indent=1, ensure_ascii=False)
    rw = [s for s in scripts if int(s["id"][1:]) >= RUNWAY_FROM]
    write_generated_md(os.path.join(ROOT, "RUNWAY_SCRIPTS.md"), runway_md(rw, hooks))
    json.dump([to_schema(s) for s in rw], open(os.path.join(DATA, "runway_scripts.json"), "w"), indent=1, ensure_ascii=False)

    rows, used, mix = build_calendar(hooks, [dict(s) for s in scripts])
    cal = calendar_md(rows)
    write_generated_md(os.path.join(DATA, "calendar_30d.md"), cal + "\n")
    with open(os.path.join(DATA, "calendar_30d.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["day", "theme", "page"] + [f"{t} {l}" for t, l in SLOTS])
        for d, th, p, cells in rows:
            w.writerow([d, th, p] + cells)
    global RUNWAY_SRC
    RUNWAY_SRC = [s for s in scripts if int(s["id"][1:]) >= RUNWAY_FROM]
    rc_all = {}
    for R in (21, 14, 7):
        rc = build_runway_calendar(rows, R)
        rc_all[R] = rc
        with open(os.path.join(DATA, f"runway_calendar_R{R}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["D", "stage", "page", "videos_per_platform", "ig_trial_reels", "threads_x_text_posts", "posts"])
            for D, st, pg, n, tr, tx, items in rc:
                w.writerow([D, st, pg, n, tr, tx, " | ".join(items)])
        placed = [i.split(" ")[0] for r in rc for i in r[6] if "(runway·" in i or "(launch·" in i]
        if sorted(placed) != [f"S{i}" for i in range(RUNWAY_FROM, N_SCRIPTS + 1)]:
            problems.append(f"runway calendar R={R}: S{RUNWAY_FROM}–S{N_SCRIPTS} not each placed exactly once")
    oe_path = os.path.join(ROOT, "ORGANIC_ENGINE.md")
    if os.path.exists(oe_path):
        txt = open(oe_path).read()
        for tag, body in (("RUNWAY_SUMMARY", runway_calendar_summary(rc_all)), ("RUNWAY_CALENDAR", runway_calendar_md(rc_all[21], 21))):
            a, b = f"<!-- {tag}:START -->", f"<!-- {tag}:END -->"
            if a in txt:
                pre, rest = txt.split(a, 1); _, post = rest.split(b, 1)
                txt = pre + a + "\n<!-- GENERATED by tools/build_content.py (build_runway_calendar): edit the sources, not this block -->\n" + body + "\n" + b + post
        open(oe_path, "w").write(txt)
    cs_path = os.path.join(ROOT, "CONTENT_SYSTEM.md")
    if os.path.exists(cs_path):
        txt = open(cs_path).read()
        start, end = "<!-- CALENDAR:START -->", "<!-- CALENDAR:END -->"
        if start in txt:
            pre, rest = txt.split(start, 1)
            _, post = rest.split(end, 1)
            txt = pre + start + "\n<!-- GENERATED by tools/build_content.py from data/content/: edit the sources, not this block -->\n" + cal + "\n" + end + post
            open(cs_path, "w").write(txt)

    print(f"hooks: {len(hooks)} (★{sum(h['test_first'] for h in hooks)}), scripts: {len(scripts)} {dict(counts)}")
    print(f"word counts: S01–S60 {min(s['_wc'] for s in scripts[:60])}–{max(s['_wc'] for s in scripts[:60])} · S61–S150 {min(s['_wc'] for s in scripts[60:])}–{max(s['_wc'] for s in scripts[60:])}")
    print(f"ads: {len(M.ADS)} " + str(dict(collections.Counter(a['fmt'] for a in M.ADS))))
    n_fields = sum(len(script_published_text(s)) for s in scripts) + sum(len(ad_published_text(a)) for a in M.ADS)
    print(f"fall/percentage/mortality-framing scan: {len(oc_hits) + sum('outcome claim' in p for p in ad_problems)} hits")
    print(f"blocked-claims scan: {len(BLOCKED)} regexes × {len(scripts)} scripts + {len(M.ADS)} ads ({n_fields} text fields): {len(bc_hits) + sum('blocked-claims' in p for p in ad_problems)} hits")
    rwy = [s for s in rw if int(s["id"][1:]) < RUNWAY_LAUNCH_FROM]
    print(f"runway/launch scripts S{RUNWAY_FROM}–S{N_SCRIPTS}: {len(rw)} (runway {len(rwy)}, launch {len(rw) - len(rwy)}) "
          f"{dict(collections.Counter(s['speaker'] for s in rw))}; proven grammar {sum(1 for s in rw if s['_proven'])}/{len(rw)}; "
          f"CTAs {dict(collections.Counter(s['cta'] for s in rw))}")
    print(f"calendar rows: {len(rows)}, hooks scheduled: {len(used)}")
    print(VIR.report([s["_virality"] for s in scripts]) + "; REWRITE (legacy, unscheduled): "
          + ", ".join(s["id"] for s in scripts if s["_virality"].get("gate") == VIRALITY_LEGACY_GATE))
    for p in mix:
        tot = sum(mix[p].values()); print(p, "pillar mix:", {k: round(100*v/tot) for k, v in sorted(mix[p].items())})
    w2_problems, w2_summary = build_wave2(scripts, hooks, ev_ids)
    print(w2_summary)
    problems += w2_problems
    if problems:
        print("PROBLEMS:"); [print(" -", p) for p in problems]; sys.exit(1)
    print("VALIDATION: PASS")


if __name__ == "__main__":
    main()
