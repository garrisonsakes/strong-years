"""Self-audit of every product source against SAFETY_RULES.md (blocked claims, identity, movement, food cautions).
Prints each hit with context and a verdict. Exit code 1 if any unresolved BLOCK remains."""
import re, os, json, glob, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sorted(glob.glob(os.path.join(P, "*.md"))) + sorted(glob.glob(os.path.join(P, "programs", "*.md"))) + [os.path.join(P, "sessions.json"), os.path.join(P, "kitchen_recipes.json"), os.path.join(P, "programs.json")]

BLOCK = [  # SAFETY §3.1 + D-04..D-07 + M-04 + T-04 + CHARACTERS never-says
    r"\bcure[sd]?\b|\bcuring\b", r"heal(s|ed|ing)? (your|the|my) (arthritis|diabetes|blood pressure|cancer|heart|liver|kidney|thyroid|dementia|alzheimer'?s|neuropathy|osteoporosis)",
    r"reverse[sd]? (diabetes|arthritis|osteoporosis|aging|dementia|alzheimer'?s|heart disease)",
    r"(treats?|treatment for) (diabetes|hypertension|cancer|arthritis|depression|anxiety disorder|insomnia|ibs|gerd)",
    r"prevent[s]? (cancer|dementia|alzheimer'?s|stroke|heart attack)", r"\bdetox\b|cleanse (your )?(liver|colon|kidneys|blood)|flush (out )?toxins|\bcleanses?\b",
    r"lower(s)? (your )?blood pressure (instantly|in minutes|fast|immediately)", r"burn (sugar|belly fat|fat) (fast|instantly|overnight)|\bburns? sugar\b",
    r"melt(s)? (belly )?fat|target(ed)? fat loss|spot reduc", r"boost(s)? (your )?immune system", r"anti-?aging (secret|miracle)|fountain of youth|add (\d+ )?years to your life|live to 100",
    r"\bmiracle\b|secret (doctors|big pharma)|doctors (hate|don't want)|big pharma|they don't want you to know",
    r"\bguarantee[ds]?\b|100% (safe|effective|natural)|no side effects|works for everyone", r"clinically proven",
    r"instead of (your )?(medication|medicine|pills|surgery|doctor)", r"(stop|quit|reduce|replace) (taking )?(your )?(medication|medicine|pills|insulin|blood thinner|statin)",
    r"natural (alternative|replacement) (to|for)", r"never (get sick|go to the (doctor|hospital))", r"fix (your )?(knee|back|hip|shoulder) (forever|for good|permanently)", r"pain[- ]free (forever|guaranteed)",
    r"\bI am real\b|I'm a real person|\bnot AI\b|this is really me|my real name", r"\bmonk\b|\bpriest\b|\blama\b|\bshifu\b|\bsifu\b|\bguru\b|\bclergy\b|\bmaster\b",
    r"I cured my|this fixed my|went away|haven't been sick since|never went to the hospital because|my doctor was shocked",
    r"monastery|temple secret|\bsacred\b|ancient chinese secret|ancient wisdom|qi will heal|\bbuddha\b|\bdharma\b|meridian", r"\bqi\b",
    r"hold your breath", r"only \d+ spots left|price goes up|\bwas \$\d+", r"\bmy friend\b", r"healing journey", r"superfood", r"no pain,? no gain",
    r"\binstantly\b", r"\bsit-?ups?\b|\bcrunch(es)?\b|toe[- ]touch", r"\bfasting\b|skip (a )?meals?", r"raw eggs?|runny|raw sprouts?|unpasteurized", r"red wine",
    r"\b(Dr\.|physician|nurse|physiotherapist|dietitian|nutritionist|pharmacist|acupuncturist|licensed|certified)\b",
    r"reviewed by|science-checked|PT-reviewed", r"\bneck circles?\b|full circles",
    r"fall[- ]risk|risk (of|for) falling|fall prevention|prevent(s|ing)? falls|fewer falls|cut falls|falls? (dropped|down|were|lower|reduc)|rate of falls|reduc\w* falls|near-falls?",
    r"text \**CANCEL", r"\$20 (a|every|/) ?month|\$20/mo",
    # CANON UPDATE 2/3: no $1 trial, no "for life", no retired prices
    r"\$1\b(?![\d.,])|7 days for \$1|\$1 (7-day )?trial|for life\b|\$19\.99|\$99\b|\$25 or \$30",
]
# Allowed contexts (MB-EX myth-bust with negation + evidence, commerce guarantee, referral language, safety negations)
ALLOW = [
    (r"money-back guarantee|guarantee\.\*\*|30-day guarantee", "commerce refund guarantee (OFFER/BLITZ), not a health claim — whitelist in checker"),
    (r"✗ \*\*Myth:\*\*|Don't bother|No competent evidence that detox|\bMyth\b", "MB-EX myth-bust row with negation + evidence ID"),
    (r"never hold your breath|Never hold your breath|never \"hold your breath\"|not holding your breath|No breath holds|no breath-holds|Never hold", "safety negation (M-04)"),
    (r"(ask|asks|tell|Tell|Ask|ask your) (your )?(doctor or )?(physical therapist|pharmacist|dietitian|doctor or dietitian|doctor, physical therapist or dietitian)|your doctor or dietitian|doctor or pharmacist|pelvic-floor physical therapist|physical therapist's|your doctor, physical therapist or dietitian|surgeon's or physical therapist|doctor, your physical therapist|replace your doctor, physical therapist or dietitian|I'm not a doctor or physical therapist|not a nutritionist|doctor, physical therapist|a physical therapist can|your doctor and your pharmacist|physiotherapist-guided", "referral to a human professional, not a character credential"),
    (r"Never full neck circles|never full circles|No big circles with the neck|Never full neck|Nods and half-turns only", "safety negation (neck)"),
    (r"no runny|No runny|runny yolks|No raw-egg|no raw sprouts|Sprouts are always cooked|not runny|Not runny|always cooked|until no runny egg", "food-safety negation (E54/E55)"),
    (r"sit-ups|crunches|toe-touch", "only allowed inside an E40 caution"),
    (r"one long sigh|went away", "context check"),
    (r"licensed humans|reviewed by licensed", "reviewer claim — must be FALLBACK"),
    (r"\binstantly\b", "must be inside a myth-bust"),
    (r"skip (a )?meals?", "context check"),
]

def ctx(t, m, w=90):
    a, b = max(0, m.start() - w), min(len(t), m.end() + w)
    return t[a:b].replace("\n", " ")

total_block = 0
report = []
for f in files:
    t = open(f).read()
    if f.endswith(".json"):
        t = json.dumps(json.load(open(f)), ensure_ascii=False)
    name = os.path.basename(f)
    for pat in BLOCK:
        for m in re.finditer(pat, t, re.I):
            c = ctx(t, m)
            verdict = None
            for ap, why in ALLOW:
                if re.search(ap, c):
                    verdict = why
                    break
            report.append((name, m.group(0), verdict, c))
            if verdict is None:
                total_block += 1

# ---------- structural checks on sessions.json (M-01..M-04, M-06/M-07, duration, evidence IDs)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from evidence import EV
S = json.load(open(os.path.join(P, "sessions.json")))
ALL = S["sessions"] + S.get("guided_tests", [])
if os.path.exists(os.path.join(P, "programs.json")):
    for pg in json.load(open(os.path.join(P, "programs.json")))["programs"]:
        ALL += pg["sessions"]
SUP = re.compile(r"chair|counter|wall|rail|fence|sit|seated|hold|hands? on|bed|bench|shoes|walker|clear path", re.I)
BR = re.compile(r"breath|breathe|sigh|count out loud", re.I)
struct = []
def secs(t):
    m, s_ = t.split(":"); return int(m) * 60 + int(s_)
for ss in ALL:
    if ss.get("has_movement", True) and not (450 <= ss["duration_s"] <= 750):
        struct.append(f"{ss['id']} duration {ss['duration']}")
    intro = " ".join(b["vo"] for b in ss["segments"][0]["beats"])
    if ss.get("has_movement", True) and not re.search(r"stop|dizz", intro, re.I):
        struct.append(f"{ss['id']} intro lacks stop rule")
    for e in ss["evidence"]:
        if e not in EV: struct.append(f"{ss['id']} unknown evidence {e}")
    for g in ss["segments"]:
        if not g["tracks"]: continue
        st = secs(g["start"])
        early = " ".join(b["vo"] for b in g["beats"] if secs(b["t"]) - st <= 10)
        if not SUP.search(early): struct.append(f"{g['id']} no support cue in first 10 s: {early[:60]}")
        allvo = " ".join(b["vo"] for b in g["beats"])
        if not BR.search(allvo): struct.append(f"{g['id']} no breathing cue")
        if not any(o.startswith("Easier:") for o in g["on_screen"]): struct.append(f"{g['id']} no regression on screen")
        for tr, x in g["tracks"].items():
            d = x["dose"].lower()
            sets = [int(n) for n in re.findall(r"(\d+) sets", d)]
            reps = [int(n) for n in re.findall(r"of (\d+)(?! seconds)(?!\d)", d)]
            moving = x["exercise"] in ("carry", "suitcase_carry", "walk", "seated_march", "standing_march", "cyclic_sigh", "breath_46", "cloud_hands", "stair_climb")
            holds = [] if moving else ([int(n) for n in re.findall(r"(\d+) seconds", d)] if re.search(r"hold|× \d+ seconds", d) else [])
            over = any(n > 3 for n in sets) or any(n > 12 for n in reps) or any(n > 30 for n in holds)
            if over and not x["advanced"]:
                struct.append(f"{g['id']} {tr} dose beyond M-06 defaults without Advanced label: {x['dose']}")
print(f"STRUCTURAL CHECKS ({len(ALL)} sessions: sessions.json + programs.json):", "all passed" if not struct else "")
for x in struct: print("  [BLOCK]", x)
total_block += len(struct)

for name, hit, v, c in report:
    tag = "OK  " if v else "BLOCK"
    print(f"[{tag}] {name}: '{hit}' {'('+v+')' if v else ''}\n        …{c}…")
print(f"\nUnresolved: {total_block}")
sys.exit(1 if total_block else 0)
