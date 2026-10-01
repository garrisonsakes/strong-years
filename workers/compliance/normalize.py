"""Normalise the two script shapes used in this repo into one structure.

- prompts/02_script_writer.md output: hook{spoken,on_screen}, lines[{text,on_screen,speaker}], claims, movement, cta
- CHARACTERS.md §12.4 / data/content/scripts.json: hook_line, beats[{vo,ost,speaker}], caption, regression, cta_line
- plain text snippets (self-tests, captions)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from compliance.textnorm import canon

TAG_RX = re.compile(r"\[[^\]]*\]")        # ElevenLabs performance tags: [warmly], [pause]
EID_RX = re.compile(r"\bE\d{2}b?\b")


@dataclass
class Unit:
    source: str        # spoken | on_screen | caption | cta | safety_cue | transcript | packaging:<platform>
    index: int
    text: str


@dataclass
class NormScript:
    id: str = ""
    pillar: str = ""
    myth_bust: bool = False
    has_movement: bool = False
    movement_tags: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    regression: str = ""
    safety_cue: str = ""
    speaker: str = ""
    units: list[Unit] = field(default_factory=list)
    kind: str = "script"   # script | snippet

    def text(self, *sources: str) -> str:
        return "\n".join(u.text for u in self.units if not sources or u.source in sources)

    @property
    def spoken(self) -> str:
        return " ".join(u.text for u in self.units if u.source == "spoken")


def clean(t: str | None) -> str:
    """Canonical text (AUDIT H10: NFKC, zero-width stripped, confusables mapped) without performance tags."""
    return re.sub(r"\s+", " ", TAG_RX.sub("", canon(t or ""))).strip()


def normalize(obj: dict | str, evidence: list[str] | None = None, kind: str | None = None) -> NormScript:
    if isinstance(obj, str):
        ev = list(evidence or []) + [e for e in EID_RX.findall(obj) if e not in (evidence or [])]
        return NormScript(kind=kind or "snippet", evidence=ev, units=[Unit("spoken", 0, clean(obj))])
    s = obj
    ns = NormScript(kind=kind or "script")
    ns.id = str(s.get("id") or s.get("script_id") or s.get("title_internal") or s.get("title") or "")
    ns.pillar = str(s.get("pillar") or "")
    ns.myth_bust = bool(s.get("myth_bust")) or ns.pillar == "P15"
    mv = s.get("movement") or {}
    ns.has_movement = bool(s.get("has_movement") or mv.get("present"))
    ns.movement_tags = list(s.get("movement_tags") or [])
    ev = list(s.get("evidence") or [])
    for c in s.get("claims") or []:
        ev.extend(c.get("evidence_ids") or [])
    if evidence:
        ev.extend(evidence)
    ns.evidence = sorted(set(ev))
    ns.regression = clean(s.get("regression") or mv.get("regression") or "")
    ns.safety_cue = clean(s.get("safety_cue") or "")
    ns.speaker = str(s.get("speaker") or s.get("speaker_mode") or "")

    units: list[Unit] = []
    hook = s.get("hook") or {}
    if isinstance(hook, dict):
        if hook.get("spoken"):
            units.append(Unit("spoken", -1, clean(hook["spoken"])))
        if hook.get("on_screen"):
            units.append(Unit("on_screen", -1, clean(hook["on_screen"])))
    for i, ln in enumerate(s.get("lines") or []):
        if ln.get("text"):
            units.append(Unit("spoken", ln.get("i", i), clean(ln["text"])))
        if ln.get("on_screen"):
            units.append(Unit("on_screen", ln.get("i", i), clean(ln["on_screen"])))
    for i, b in enumerate(s.get("beats") or []):
        if isinstance(b, (list, tuple)):          # tuple beats (tools/build_content.py sources)
            vo, ost = (b[2] if len(b) > 2 else ""), (b[3] if len(b) > 3 else "")
        else:
            vo, ost = b.get("vo") or b.get("text") or "", b.get("ost") or b.get("on_screen") or ""
        if vo:
            units.append(Unit("spoken", i, clean(vo)))
        if ost:
            units.append(Unit("on_screen", i, clean(ost)))
    # Paid-ad shape (data/content/ad_scripts.json): every viewer-facing field is scanned.
    # compliance_note / ad_name / optimization_event are internal and never published.
    for i, h in enumerate(s.get("hook_variants_first_2s") or []):
        units.append(Unit("spoken", -10 - i, clean(h)))
        units.append(Unit("on_screen", -10 - i, clean(h)))
    for i, b in enumerate(s.get("body") or []):
        if isinstance(b, dict):
            if b.get("vo_or_action"):
                units.append(Unit("spoken", 100 + i, clean(b["vo_or_action"])))
            if b.get("on_screen_text"):
                units.append(Unit("on_screen", 100 + i, clean(b["on_screen_text"])))
    for fld, src, idx in (("headline", "on_screen", 900), ("end_card", "on_screen", 901),
                          ("starter_variant_end_card", "on_screen", 902), ("trial_variant_end_card", "on_screen", 903), ("primary_text", "caption", 1),
                          ("offer_line", "caption", 2), ("starter_variant_line", "caption", 3), ("trial_variant_line", "caption", 4)):
        if isinstance(s.get(fld), str) and s[fld].strip() and not any(
                clean(s[fld]) in u.text for u in units if u.source == src):
            units.append(Unit(src, idx, clean(s[fld])))
    if not s.get("lines") and not s.get("beats") and s.get("hook_line"):
        units.append(Unit("spoken", -1, clean(s["hook_line"])))
    if s.get("thumbnail_text"):
        units.append(Unit("on_screen", 999, clean(s["thumbnail_text"])))
    cta = s.get("cta") or {}
    if isinstance(cta, dict) and cta.get("spoken") and not any(cta["spoken"] in u.text for u in units):
        units.append(Unit("cta", 0, clean(cta["spoken"])))
    if s.get("caption"):
        units.append(Unit("caption", 0, canon(s["caption"]).strip()))
    for u in units:
        ev_inline = EID_RX.findall(u.text)
        for e in ev_inline:
            if e not in ns.evidence:
                ns.evidence.append(e)
    ns.units = units
    # movement tags may also be food/topic tags in scripts.json; has_movement is authoritative
    return ns
