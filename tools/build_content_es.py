#!/usr/bin/env python3
"""Spanish content build + validation (CHARACTERS_ES.md; @donchuyylupe).

Sources: data/content/hooks_es.psv (HES01–HES40) + data/content/scripts_es.py (ES01–ES40).
Outputs: SCRIPTS_ES.md (generated), data/content/scripts_es.json, data/content/hooks_es.json.
Runs standalone (python3 tools/build_content_es.py) and as a hook from tools/build_content.py (run(bc) -> problems).

Rules (Spanish layer on top of the English machine-checkable SAFETY rules):
  * every prompts/blocked_claims.json regex (English BC01–BC25 + Spanish BC26–BC37) over every published field, through
    the same anti-evasion normalisation as the workers' scanner (tools/build_content.tn_finditer);
  * Spanish condition terms: blocked in prominent fields (hook, frame-1 text, title, YT title, thumbnail) and in hashtags;
  * falls / percentages / mortality: same policy as English (falls everywhere, % in prominent fields, mortality everywhere);
  * "garantía" only as "garantía de devolución de 14 días" and never next to a health result; "de por vida" banned;
    membership captions must say "bloqueado mientras sigas suscrito" (plus the other S-02 terms);
  * runway: no price, no "{{", no membership words; LISTA (free waitlist) a minority and says "gratis";
  * launch: LIBRO / UNIRME / FAMILIA only, full terms, an AI line spoken or on screen, no urgency;
  * structure: 30–59 s, 70–135 spoken words, hook = HES line verbatim (<= 18 words), frame-1 text <= 7 words, skip line
    verbatim, "Comente/Comenta <CTA>" in the last beats and caption line 1, movement = support cue + easier version;
  * grammar tags match the Spanish detectors; proven-grammar share >= 45%; running bits; AI winks >= 1 per 20.
"""
from __future__ import annotations

import collections
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "content")
PAGE = "@donchuyylupe"
N = 40
RUNWAY_N = 25
CTA_ES = {"FUERTE", "EQUILIBRIO", "ESPALDA", "RODILLAS", "SUEÑO", "RESPIRA", "SOPA", "EMPEZAR", "PRUEBA", "FAMILIA",
          "LISTA", "LIBRO", "UNIRME"}
CTA_DELIV_ES = {
    "FUERTE": "La silla de 8 minutos de Don Chuy (clon de STRONG)", "EQUILIBRIO": "Pies firmes + la prueba de 4 etapas (BALANCE)",
    "ESPALDA": "La rutina de la mañana, 7 min, empieza en la cama (BACK)", "RODILLAS": "Los escalones (KNEES)",
    "SUEÑO": "Rutina de 10 minutos para la noche (SLEEP)", "RESPIRA": "Respiración 4-6, 5 min (BREATH)",
    "SOPA": "Los tres caldos de Doña Lupe / escalera de fibra (SOUP/GUT)", "EMPEZAR": "¿Por dónde empiezo? menú (BEGIN)",
    "PRUEBA": "Las tres pruebas: silla, un pie, piso (TEST)", "FAMILIA": "Página del regalo (FAMILY)",
    "LISTA": "Lista de espera gratis (FUNNEL.md §4.20; runway only)", "LIBRO": "Libros de inicio en Shopify (FUNNEL.md §4.21)",
    "UNIRME": "Membresía Fundadora + términos completos (FUNNEL.md §4.22)",
}
SPEAKERS = {"CHUY", "LUPE", "DUO"}
BEAT_SPEAKERS = {"CHUY", "LUPE", "FRANK", "MARISOL", "TOÑA"}
GRAMMARS_ES = {"OBJ3", "IF_EVERY", "NOT_X", "MYTH", "WATCH", "TEST_NOW", "SHARE", "DEMO"}
PROVEN = ("IF_EVERY", "NOT_X", "MYTH", "WATCH")
PROVEN_MIN_SHARE = 0.45
MAX_WPM = {"CHUY": 150, "LUPE": 170, "DUO": 160}   # designed-voice pace + 15 (Chuy 135, Lupe 155)
SUPPORT_RX = re.compile(r"silla|pared|mesa|barandal|lavabo|cama|banca|mostrador|encimera|sof[aá]|respaldo|hombro", re.I)
HEALTH_EXEMPT = {"P16", "P17", "P20"}

COND = (r"diabet\w*|az[uú]car|glucosa|presi[oó]n alta|presi[oó]n arterial|hipertensi[oó]n|colesterol|triglic[eé]ridos|artritis|"
        r"artrosis|reumas?|osteoporosis|menopausia|bochornos|ci[aá]tica|neuropat[ií]as?|insomnio|ansiedad|depresi[oó]n|"
        r"demencia|alzh?eimer|pr[oó]stata|c[aá]ncer|infartos?|derrames?|embolias?|inflamaci[oó]n|dolor(es)?")
COND_RX = re.compile(r"\b(" + COND + r")\b", re.I)
HASHTAG_ES = re.compile(r"#\w*(diabet|azucar|azúcar|glucosa|presion|presión|hiperten|colesterol|artrit|artros|reuma|dolor|"
                        r"menopaus|osteopor|remedio|cura|insomni|ansiedad|depres|caida|caída|rodilla|inflama|higado|hígado|"
                        r"rinon|riñon|riñón|prostat|próstat|cancer|cáncer|demencia)", re.I)
FALL_ES = re.compile(r"\bca[ií]das?\b", re.I)          # any fall wording at all in published fields (stricter than English)
PCT = re.compile(r"\d\s?(%|por ciento)", re.I)
MORT_ES = re.compile(r"\b(muertes?|morir|mortalidad|sobreviv\w*|supervivencia|vivir m[aá]s|vida m[aá]s larga|esperanza de vida|"
                     r"longevidad|a[ñn]os de vida)\b", re.I)
GARANTIA = re.compile(r"\bgarantiza\w*|\bgarantizad\w*|garant[ií]a(?! de devoluci[oó]n de 14 d[ií]as)|garant[ií]a de devoluci[oó]n"
                      r"[^.!?\n]{0,120}\b(fuerte|fuerza|duerm\w*|dolor\w*|peso|kilos|libras|equilibrio|ca[ií]das?|resultados?|joven|"
                      r"az[uú]car|presi[oó]n)\b", re.I)
BANNED_ES = [r"\bde por vida\b", r"\bpara toda la vida\b", r"\bvitalici\w*", r"\bpara siempre\b", r"\bal instante\b",
             r"\binstant[aá]ne\w*", r"\bmilagr\w*", r"\bsecreto\b", r"\bmaestro\b", r"\bmonje\b", r"\btemplo\b",
             r"\bcurander\w*", r"\bsobador\w*", r"\bhueser\w*", r"\bcham[aá]n\b", r"\bvieja\b", r"\bgord(it)?[oa]s?\b",
             r"\bsuperalimento\w*", r"\bdesintoxic\w*", r"\btoxinas?\b", r"\bpapeles\b", r"\bmigra(ci[oó]n)?\b",
             r"\bdeport\w*", r"\bsi dios quiere\b", r"\bdios te\b", r"\bvirgen\b", r"\bmi amigo\b",
             r"\bsin dolor no hay\b", r"\bcl[ií]nicamente comprobado\b", r"\bquema(r)? grasa\b", r"\btestimonio\w*",
             r"\bmis (alumnos|pacientes|clientes)\b"]
URGENCY_ES = re.compile(r"\b(quedan pocos|pocos lugares|lugares disponibles|[uú]ltim[ao]s? (oportunidad|lugares|horas|d[ií]as)|"
                        r"termina (hoy|esta noche|a medianoche)|ap[uú]r[ae]te|ap[uú]rese|solo quedan|no te lo pierdas|"
                        r"se acaba hoy)\b", re.I)
MEMBER_MENTION = re.compile(r"\b(membres[ií]a|miembros?|suscri\w*|fundador\w*|al mes|por mes|/mes|cada mes)\b", re.I)
MEMBER_TERMS = ("{{founding_price}}/mes", "se renueva cada mes", "cancela en línea cuando quieras",
                "garantía de devolución de 14 días", "bloqueado mientras sigas suscrito", "fecha de cierre")
BOOK_TERMS = ("{{ebook_price}}", "un solo pago", "no es suscripción", "tuyos para quedártelos")
GIFT_TERMS = ("$49", "$119", "nunca se renueva solo")
AI_LINE = re.compile(r"\b(soy|somos|son|es|eres)\s+(un |una )?(personajes? de )?(ia|inteligencia artificial)\b|"
                     r"personajes? de (ia|inteligencia artificial)|de inteligencia artificial", re.I)
BITS_ES = {1: r"despacio, pero diario", 2: r"\bla jefa\b", 3: r"\btoña\b|audio de whatsapp", 4: r"eso dice él",
           5: r"calendario|calendar", 6: r"tortillas?", 7: r"seis y medio|\b(siete|ocho) de diez\b|calificaci",
           8: r"\bpirata\b", 9: r"bigote", 10: r"\ben corto\b", 11: r"delantal|apron", 12: r"\bfrank\b",
           13: r"\bblock\b|mezcla|nivelad", 14: r"sombrilla|parasol", 15: r"cuaderno|red pen|notebook", 16: r"ay, jesús",
           17: r"inteligencia artificial|\bia\b|renderiz|pixeles|4k", 18: r"aniversario|52 años", 19: r"danz[oó]n",
           20: r"escond\w*[^.]{0,60}cubetas?|cubetas?[^.]{0,60}escond", 21: r"marisol", 22: r"chiles?|maceta",
           23: r"ap[uú]ntale|ap[uú]ntele|handwritten card", 24: r"\bfoto\b|1975"}
PLACEHOLDERS = {"{{EBOOK_PRICE}}", "{{FOUNDING_PRICE}}", "{{DOMAIN}}"}


def _load_bc():
    if "cs_build_content" in sys.modules:
        return sys.modules["cs_build_content"]
    spec = importlib.util.spec_from_file_location("cs_build_content", os.path.join(ROOT, "tools", "build_content.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules["cs_build_content"] = m
    spec.loader.exec_module(m)
    return m


def load_hooks():
    rows = []
    for line in open(os.path.join(DATA, "hooks_es.psv"), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = line.rstrip("\n").split("|")
        rows.append(dict(id=f"HES{len(rows) + 1:02d}", stage=f[0], speaker=f[1], pillar=f[2], format=f[3], cta=f[4],
                         grammar=[g for g in f[5].split("+") if g], ev=[e for e in f[6].split(",") if e], hook=f[7], gloss=f[8]))
    return rows


def load_scripts(hooks):
    spec = importlib.util.spec_from_file_location("scripts_es", os.path.join(DATA, "scripts_es.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = []
    for i, s in enumerate(m.SCRIPTS):
        h = hooks[i] if i < len(hooks) else {}
        s = dict(s)
        s.update(page=PAGE, hook_id=h.get("id"), speaker=h.get("speaker"), pillar=h.get("pillar"), format=h.get("format"),
                 cta=h.get("cta"), grammar=h.get("grammar", []), ev=h.get("ev", []), stage=h.get("stage"),
                 hcat="LCH" if h.get("stage") == "launch" else s.get("hcat", "CUR"))
        out.append(s)
    return out


def norm(t):
    return re.sub(r"[^\wáéíóúñü ]", "", t.lower()).strip()


def detect_grammar(hook, s):
    h = hook.lower().strip()
    g = []
    if re.match(r"^¿?si\b", h) and re.search(r"\bcada\b|\btodos los d[ií]as\b|\btodas las (mañanas|noches)\b", h):
        g.append("IF_EVERY")
    if re.search(r"\bno\b[^?!]{0,40}[,.:]\s*(no|ni)\b", h):
        g.append("NOT_X")
    if (s.get("pillar") == "P15" or s.get("myth")) and (re.match(r"^[\"'“‘¿]", hook.strip()) or "?" in hook or re.search(r"\bno\b", h)):
        g.append("MYTH")
    if re.search(r"\bmir[ae] (lo que pasa|c[oó]mo|lo que trae|esto)\b", h):
        g.append("WATCH")
    words = [norm(w) for w in hook.split()[:3]]
    if s.get("obj") and any(w.startswith(norm(s["obj"])) for w in words):
        g.append("OBJ3")
    if re.search(r"\bprueba\b", h) and re.search(r"\bhoy\b|\bahora\b|\?", h):
        g.append("TEST_NOW")
    if re.match(r"^(m[aá]nd[ae]selo|m[aá]ndaselo|etiquet[ae]|comp[aá]rt[ae]lo|p[aá]saselo)", h):
        g.append("SHARE")
    return g


# Required boilerplate (skip lines, spoken offer terms, AI lines, gift prices) is legally fixed wording: excluded from the
# uniqueness check, which is about creative lines only.
SHINGLE_EXEMPT = re.compile(r"\{\{|garant[ií]a de devoluci[oó]n|bloqueado mientras|se renueva|cancel|personajes? de ia|"
                            r"inteligencia artificial|cuarenta y nueve|ciento diecinueve|cinco mil|\bcoment[ae] [a-zñ]{4,}\b|"
                            r"lista de espera es gratis|despacio, pero diario|primero la verdad, luego el pan dulce|eso dice él|"
                            r"donde empezamos, no donde", re.I)


def shingle_set(s, n=7):
    out = []
    for b in s["beats"]:
        t = b[2].replace(s["skip"], " ")
        for sent in re.split(r"(?<=[.!?])\s+", t):
            if SHINGLE_EXEMPT.search(sent):
                continue
            toks = norm(sent).split()
            out += [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    return out


def published(s):
    return {"spoken": " ".join(b[2] for b in s["beats"]), "on_screen": " ".join(b[3] for b in s["beats"]),
            "caption": s["caption"], "title": s["title"], "yt_title": s["yt"], "thumbnail": s["thumb"]}


def validate(scripts, hooks, ev_ids, bc):
    P = []
    if len(hooks) != N or len(scripts) != N:
        P.append(f"ES: need {N} hooks and {N} scripts (got {len(hooks)} / {len(scripts)})")
    if [s["id"] for s in scripts] != [f"ES{i:02d}" for i in range(1, N + 1)]:
        P.append("ES: script ids must run ES01–ES40 in order")
    if [h["stage"] for h in hooks] != ["runway"] * RUNWAY_N + ["launch"] * (N - RUNWAY_N):
        P.append("ES: hooks must be 25 runway then 15 launch")
    seen_line, shingles = {}, {}
    for s in scripts:
        sid = s["id"]
        if s["speaker"] not in SPEAKERS:
            P.append(f"{sid}: speaker {s['speaker']}")
        if s["cta"] not in CTA_ES:
            P.append(f"{sid}: CTA {s['cta']} not in the Spanish keyword map")
        for b in s["beats"]:
            if b[1] not in BEAT_SPEAKERS:
                P.append(f"{sid}: beat speaker {b[1]}")
        spoken = " ".join(b[2] for b in s["beats"])
        ost = " ".join(b[3] for b in s["beats"])
        shots = " ".join(b[4] for b in s["beats"])
        s["_spoken"], s["_wc"] = spoken, len(spoken.split())
        hook = s["beats"][0][2]
        # structure
        if not 70 <= s["_wc"] <= 135:
            P.append(f"{sid}: spoken words {s['_wc']} outside 70–135")
        wpm = s["_wc"] / s["secs"] * 60
        if wpm > MAX_WPM.get(s["speaker"], 160):
            P.append(f"{sid}: {wpm:.0f} wpm > {MAX_WPM.get(s['speaker'])} for {s['speaker']} (voice targets, CHARACTERS_ES §13.3)")
        if not 30 <= s["secs"] <= 59:
            P.append(f"{sid}: {s['secs']} s outside 30–59")
        ends = [tuple(int(x) for x in b[0].split("-")) for b in s["beats"]]
        if ends[0][0] != 0 or any(a[1] != b[0] for a, b in zip(ends, ends[1:])) or ends[-1][1] != s["secs"]:
            P.append(f"{sid}: beat times must be contiguous from 0 to secs")
        if hook != next((h["hook"] for h in hooks if h["id"] == s["hook_id"]), None):
            P.append(f"{sid}: first spoken line != {s['hook_id']} verbatim")
        if len(hook.split()) > 18:
            P.append(f"{sid}: hook > 18 words")
        if len(s["beats"][0][3].split()) > 7:
            P.append(f"{sid}: frame-1 on-screen text > 7 words")
        if s["skip"] not in spoken + " " + ost:
            P.append(f"{sid}: skip line not verbatim in spoken/on-screen text")
        last = " ".join(b[2] for b in s["beats"][-2:])
        if not re.search(rf"\bComent[ae] {s['cta']}\b", last):
            P.append(f"{sid}: last beats don't say 'Comente/Comenta {s['cta']}'")
        if not re.match(rf"Coment[ae] {s['cta']}\b", s["caption"]):
            P.append(f"{sid}: caption line 1 must start with 'Comente/Comenta {s['cta']}'")
        for e in s["ev"]:
            if e not in ev_ids:
                P.append(f"{sid}: evidence {e} not in EVIDENCE.md")
        if not s["ev"] and s["pillar"] not in HEALTH_EXEMPT:
            P.append(f"{sid}: no evidence on a health pillar")
        if s["move"]:
            if not s.get("regression"):
                P.append(f"{sid}: movement without an easier version")
            if not SUPPORT_RX.search(spoken + " " + s["safety"]):
                P.append(f"{sid}: movement without a support cue (silla/pared/mesa/barandal/lavabo…)")
        # grammar
        det = detect_grammar(hook, s)
        s["_proven"] = [g for g in det if g in PROVEN]
        if not s["grammar"] or set(s["grammar"]) - GRAMMARS_ES:
            P.append(f"{sid}: grammar tags {s['grammar']} not in {sorted(GRAMMARS_ES)}")
        for g in ("IF_EVERY", "WATCH", "NOT_X"):
            if (g in s["grammar"]) != (g in det):
                P.append(f"{sid}: grammar tag {g} doesn't match the hook text")
        for g in ("OBJ3", "TEST_NOW", "SHARE", "MYTH"):
            if g in s["grammar"] and g not in det:
                P.append(f"{sid}: grammar tag {g} not detected in the hook")
        n = norm(hook)
        if n in seen_line:
            P.append(f"{sid}: hook duplicates {seen_line[n]}")
        seen_line[n] = sid
        for sh in shingle_set(s):
            if sh in shingles and shingles[sh] != sid:
                P.append(f"{sid}: 7-word shingle repeats {shingles[sh]}: '{sh}'")
                break
            shingles.setdefault(sh, sid)
        # language rules over every published field
        pub = published(s)
        text = " ".join(pub.values())
        for f, t in pub.items():
            for p in bc.BLOCKED:
                for m, v in bc.tn_finditer(p["regex"], t, flags=re.I):
                    P.append(f"{sid}: blocked-claims {p['id']} ({p['severity']}) in {f}: …{v[max(0, m.start() - 30): m.end() + 30]}…")
        prominent = {"hook": hook, "frame1": s["beats"][0][3], "title": s["title"], "yt": s["yt"], "thumb": s["thumb"]}
        for f, t in prominent.items():
            for rx, what in ((COND_RX, "condition term"), (PCT, "percentage")):
                m = rx.search(t)
                if m:
                    P.append(f"{sid}: {what} '{m.group(0)}' in prominent field {f}")
        for f, t in pub.items():
            for rx, what in ((FALL_ES, "fall wording"), (MORT_ES, "mortality framing"), (GARANTIA, "garantía rule"), (URGENCY_ES, "urgency")):
                for m, v in bc.tn_finditer(rx.pattern, t, flags=re.I):
                    P.append(f"{sid}: {what} '{m.group(0)}' in {f}")
            for pat in BANNED_ES:
                for m, v in bc.tn_finditer(pat, t, flags=re.I):
                    P.append(f"{sid}: banned '{m.group(0)}' in {f}")
        for tag in s["ig"] + s["tt"]:
            if HASHTAG_ES.search(tag) or bc.CONDITION_HASHTAG.search(tag):
                P.append(f"{sid}: condition hashtag {tag}")
        for ph in re.findall(r"\{\{\w+\}\}", text):
            if ph not in PLACEHOLDERS:
                P.append(f"{sid}: unknown placeholder {ph}")
        # bits
        if s["speaker"] == "DUO" and not s.get("bit"):
            P.append(f"{sid}: duo script needs a running bit (CHARACTERS_ES §7)")
        if s.get("bit"):
            if s["bit"] not in BITS_ES:
                P.append(f"{sid}: unknown bit {s['bit']}")
            elif not re.search(BITS_ES[s["bit"]], (spoken + " " + ost + " " + shots).lower()):
                P.append(f"{sid}: bit {s['bit']} not visible in the beats")
        if s.get("wink") and not AI_LINE.search(spoken + " " + ost) and not re.search(BITS_ES[17], spoken.lower()):
            P.append(f"{sid}: wink=True without an AI line")
        # stage rules
        cap_l = s["caption"].lower()
        so_l = (spoken + " " + ost).lower()
        if s["stage"] == "runway":
            if "$" in text or "{{" in text:
                P.append(f"{sid}: runway script states a price or placeholder (Spanish checkout not open)")
            if s.get("launch"):
                P.append(f"{sid}: runway script flagged launch=True")
            for m in MEMBER_MENTION.finditer(text):
                P.append(f"{sid}: runway script mentions '{m.group(0)}'")
            if s["cta"] in ("LIBRO", "UNIRME", "FAMILIA"):
                P.append(f"{sid}: offer CTA in the runway")
        else:
            if not s.get("launch"):
                P.append(f"{sid}: launch script must set launch=True")
            if s["cta"] not in ("LIBRO", "UNIRME", "FAMILIA"):
                P.append(f"{sid}: launch CTA must be LIBRO, UNIRME or FAMILIA")
            if not AI_LINE.search(spoken + " " + ost):
                P.append(f"{sid}: offer script without an AI line ('soy/somos personaje(s) de IA')")
            if s["cta"] == "FAMILIA":
                for need in GIFT_TERMS:
                    if need.lower() not in cap_l:
                        P.append(f"{sid}: FAMILIA caption missing '{need}'")
            if s["cta"] == "LIBRO":
                for need in BOOK_TERMS:
                    if need not in cap_l:
                        P.append(f"{sid}: LIBRO caption missing '{need}'")
                if "{{ebook_price}}" not in so_l:
                    P.append(f"{sid}: LIBRO spoken/on-screen must state {{{{EBOOK_PRICE}}}}")
            if s["cta"] != "FAMILIA":
                if MEMBER_MENTION.search(s["caption"]) or MEMBER_MENTION.search(spoken + " " + ost):
                    for need in MEMBER_TERMS:
                        if need not in cap_l:
                            P.append(f"{sid}: membership mentioned but caption missing '{need}'")
                if MEMBER_MENTION.search(spoken + " " + ost):
                    for need in ("{{founding_price}}", "cancel", "renuev"):
                        if need not in so_l:
                            P.append(f"{sid}: membership in spoken/on-screen without '{need}' (S-02)")
        if s["cta"] == "LISTA":
            if "gratis" not in cap_l or not re.search(r"\bgratis\b", spoken, re.I):
                P.append(f"{sid}: LISTA must say 'gratis' (spoken and caption)")
            if s["stage"] != "runway":
                P.append(f"{sid}: LISTA is runway-only")
    rw = [s for s in scripts if s["stage"] == "runway"]
    if sum(s["cta"] == "LISTA" for s in rw) * 2 >= len(rw):
        P.append("ES runway: LISTA must be a minority CTA")
    share = sum(1 for s in scripts if s["_proven"]) / max(1, len(scripts))
    if share < PROVEN_MIN_SHARE:
        P.append(f"ES: proven hook grammar share {share:.0%} < {PROVEN_MIN_SHARE:.0%}")
    solo = [s for s in scripts if s["speaker"] != "DUO"]
    if sum(1 for s in solo if s.get("bit")) * 3 < len(solo):
        P.append("ES: solo scripts need a running bit in at least 1 of 3")
    if sum(1 for s in scripts if s.get("wink")) * 20 < len(scripts):
        P.append("ES: AI winks below 1 per 20 videos")
    return P


def to_json(s):
    return {"id": s["id"], "page": s["page"], "lang": "es-US", "speaker": s["speaker"], "format": s["format"], "pillar": s["pillar"],
            "hook_id": s["hook_id"], "title": s["title"], "target_seconds": s["secs"], "hook_line": s["beats"][0][2],
            "beats": [{"t": b[0], "speaker": b[1], "vo": b[2], "ost": b[3], "shot": b[4]} for b in s["beats"]],
            "spoken_word_count": s["_wc"], "has_movement": s["move"], "movement_tags": s["tags"], "safety_cue": s["safety"],
            "regression": s["regression"], "cta_keyword": s["cta"], "cta_deliverable": CTA_DELIV_ES[s["cta"]],
            "caption": s["caption"], "hashtags": {"ig": s["ig"], "tt": s["tt"], "yt_title": s["yt"]}, "evidence": s["ev"],
            "evidence_note": s["note"], "running_bit": s.get("bit") or "", "wink": bool(s.get("wink")), "myth_bust": bool(s.get("myth")),
            "music": s["music"], "thumbnail_text": s["thumb"], "demo": bool(s.get("demo")), "hook_object": s.get("obj", ""),
            "hook_grammar": s["grammar"], "hook_grammar_detected": detect_grammar(s["beats"][0][2], s), "launch_week": bool(s.get("launch")),
            "stage": s["stage"], "prop": s["prop"], "skip_line": s["skip"], "hook_category": s["hcat"],
            "review": {"cultural_reviewer": "", "language_reviewer": "", "status": "PENDING (CHARACTERS_ES.md §14)"}}


def md(scripts, hooks):
    L = ["# SCRIPTS_ES.md: Don Chuy & Doña Lupe, 40 Spanish scripts (25 runway + 15 launch)\n",
         f"Page **{PAGE}** (CHARACTERS_ES.md). Source: `data/content/hooks_es.psv` + `data/content/scripts_es.py`; validated by "
         "`tools/build_content_es.py` (also run by `tools/build_content.py`). Machine-readable: `data/content/scripts_es.json`. "
         "Every script needs the cultural and language reviewers' sign-off before it renders (CHARACTERS_ES.md §14). "
         "The Spanish page opens at the $30K retained-MRR rung (BRIEF.md CANON UPDATE 5).\n",
         "## Summary\n"]
    c = collections.Counter
    L.append(f"- Speakers: {dict(c(s['speaker'] for s in scripts))}")
    L.append(f"- CTAs: {dict(c(s['cta'] for s in scripts))}")
    L.append(f"- Proven hook grammar (IF_EVERY / NOT_X / MYTH / WATCH): {sum(1 for s in scripts if s['_proven'])}/{len(scripts)}")
    L.append(f"- Words: {min(s['_wc'] for s in scripts)}–{max(s['_wc'] for s in scripts)}; seconds: {min(s['secs'] for s in scripts)}–{max(s['secs'] for s in scripts)}")
    L.append(f"- AI winks: {sum(1 for s in scripts if s.get('wink'))}; offer scripts with an AI line: all {sum(1 for s in scripts if s['stage'] == 'launch')}\n")
    L.append("## The 40 hooks (HES01–HES40)\n")
    L.append("| ID | Stage | Speaker | Pillar | CTA | Grammar | Hook (ES) | EN gloss |")
    L.append("|---|---|---|---|---|---|---|---|")
    for h in hooks:
        L.append(f"| {h['id']} | {h['stage']} | {h['speaker']} | {h['pillar']} | {h['cta']} | {'+'.join(h['grammar'])} | {h['hook']} | {h['gloss']} |")
    for stage, title in (("runway", "Runway (ES01–ES25)"), ("launch", "Launch (ES26–ES40)")):
        L.append(f"\n## {title}\n")
        for s in [x for x in scripts if x["stage"] == stage]:
            L.append(f"### {s['id']} · {s['title']} · {s['speaker']} · {s['secs']} s · {s['pillar']} · {s['format']} · CTA {s['cta']}")
            L.append(f"Hook {s['hook_id']} ({'+'.join(s['grammar'])}) · evidence {', '.join(s['ev']) or '—'} · bit {s.get('bit') or '—'} · prop: {s['prop']}\n")
            L.append("| t | who | dice | en pantalla | toma |")
            L.append("|---|---|---|---|---|")
            for b in s["beats"]:
                L.append(f"| {b[0]} | {b[1]} | {b[2]} | {b[3]} | {b[4]} |")
            L.append(f"\n**Skip line:** {s['skip']}  ")
            if s["move"]:
                L.append(f"**Easier version:** {s['regression']}  ")
            L.append(f"**Caption:** {s['caption'].replace(chr(10), ' / ')}  ")
            L.append(f"**Hashtags:** {' '.join(s['ig'])} · TikTok {' '.join(s['tt'])} · YT: {s['yt']} · thumb: {s['thumb']}\n")
    return "\n".join(L) + "\n"


def run(bc=None):
    """Validate; on PASS write SCRIPTS_ES.md + JSON. Returns (problems, summary)."""
    bc = bc or _load_bc()
    hooks = load_hooks()
    scripts = load_scripts(hooks)
    problems = validate(scripts, hooks, bc.load_evidence_ids(), bc)
    if not problems:
        bc.write_generated_md(os.path.join(ROOT, "SCRIPTS_ES.md"), md(scripts, hooks))
        json.dump([to_json(s) for s in scripts], open(os.path.join(DATA, "scripts_es.json"), "w"), indent=1, ensure_ascii=False)
        json.dump(hooks, open(os.path.join(DATA, "hooks_es.json"), "w"), indent=1, ensure_ascii=False)
    summary = (f"spanish scripts: {len(scripts)} {dict(collections.Counter(s['speaker'] for s in scripts))}; "
               f"CTAs {dict(collections.Counter(s['cta'] for s in scripts))}; proven grammar "
               f"{sum(1 for s in scripts if s.get('_proven'))}/{len(scripts)}; blocked-claims {len(bc.BLOCKED)} regexes "
               f"({sum(1 for p in bc.BLOCKED if p.get('lang') == 'es')} Spanish); problems {len(problems)}")
    return problems, summary


if __name__ == "__main__":
    probs, summ = run()
    print(summ)
    if probs:
        print("PROBLEMS:")
        [print(" -", p) for p in probs]
        sys.exit(1)
    print("SPANISH VALIDATION: PASS")
