"""Exact disclosure strings from SAFETY_RULES.md §7 and D-02.

Reviewer gate: the "reviewed by licensed professionals" variants may only be used when PAGE DNA
`reviewer_signed` is true. Until then the FALLBACK strings are published exactly.
"""
from __future__ import annotations

FOOTER = {
    ("en", True): ("Chang & Sun are AI characters. Content is educational, reviewed by licensed professionals, "
                   "and not medical advice. Check with your doctor before starting new exercise."),
    ("en", False): ("Chang & Sun are AI characters. Content is educational, built on published research, "
                    "and not medical advice. Check with your doctor before starting new exercise."),
    ("es", True): ("Chang y Sun son personajes de IA. Contenido educativo revisado por profesionales con licencia; "
                   "no es consejo médico. Consulta a tu médico antes de empezar un ejercicio nuevo."),
    ("es", False): ("Chang y Sun son personajes de IA. Contenido educativo basado en investigación publicada; "
                    "no es consejo médico. Consulta a tu médico antes de empezar un ejercicio nuevo."),
}

MOVEMENT_ADDON = {
    "en": "Go at your own pace. Hold a counter or chair. Stop if you feel chest pain, dizziness, or sharp pain.",
    # [A] SAFETY_RULES.md §7 only defines the EN add-on; this ES line is our translation and needs the
    # Spanish-market reviewer's sign-off (EXPANSION.md) before the ES page goes live.
    "es": "Ve a tu ritmo. Apóyate en una encimera o una silla. Detente si sientes dolor en el pecho, mareo o dolor agudo.",
}

AI_TAG = {"en": "AI character", "es": "Personaje IA"}


def lang(locale: str | None) -> str:
    return (locale or "en").split("-")[0].lower() if (locale or "en").split("-")[0].lower() in ("en", "es") else "en"


def footer(locale: str | None, reviewer_signed: bool) -> str:
    return FOOTER[(lang(locale), bool(reviewer_signed))]


def movement_addon(locale: str | None) -> str:
    return MOVEMENT_ADDON[lang(locale)]


def ai_tag(locale: str | None) -> str:
    return AI_TAG[lang(locale)]


def all_footers() -> list[str]:
    return list(FOOTER.values())
