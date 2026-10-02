"""Arm catalogue for the content allocator: pillars, hook grammars, editorial formats, characters, running bits.

The worker image ships only SAFETY_RULES / EVIDENCE / prompts, so the catalogue is embedded here and
tests/test_growth_allocator.py::test_catalog_in_sync_with_specs keeps it in sync with:
  CONTENT_SYSTEM.md §1 (pillars and their primary formats), HOOKS.md (categories), tools/build_content.py
  (GRAMMARS, PROVEN), CHARACTERS.md §7 (the 24 running bits).
"""
from __future__ import annotations

# CONTENT_SYSTEM.md §1: pillar -> primary formats
PILLAR_FORMATS: dict[str, tuple[str, ...]] = {
    "P01": ("F02", "F16", "F23"), "P02": ("F01", "F17", "F15"), "P03": ("F02", "F15", "F32"),
    "P04": ("F15", "F02"), "P05": ("F20", "F05", "F01"), "P06": ("F14", "F03"), "P07": ("F21",),
    "P08": ("F22",), "P09": ("F05",), "P10": ("F06", "F31"), "P11": ("F31", "F12"), "P12": ("F06",),
    "P13": ("F18", "F12"), "P14": ("F13", "F30"), "P15": ("F04", "F28"), "P16": ("F07", "F35"),
    "P17": ("F08", "F34", "F35"), "P18": ("F09", "F10", "F26"), "P19": ("F11",), "P20": ("F08", "F28"),
}
PILLARS: tuple[str, ...] = tuple(PILLAR_FORMATS)

# tools/build_content.py GRAMMARS (script hook grammar tags, POSTDB_FINDINGS §8) + NOT_X from PROVEN.
# LAUNCH is the founding-week grammar: the allocator never schedules it on its own (offer weeks are manual).
GRAMMARS: tuple[str, ...] = ("OBJ3", "IF_EVERY", "MYTH", "WATCH", "TEST_NOW", "DEBUNK", "SHARE", "KITCHEN_SERIES",
                             "DEMO", "NOT_X")
PROVEN_GRAMMARS: tuple[str, ...] = ("IF_EVERY", "NOT_X", "MYTH", "WATCH")
EXCLUDED_GRAMMARS: tuple[str, ...] = ("LAUNCH",)

SPEAKERS: tuple[str, ...] = ("CHANG", "SUN", "DUO")
# Formats that need both characters on screen (CONTENT_SYSTEM §2) and formats one character carries alone.
DUO_ONLY_FORMATS = {"F08", "F34"}

# CHARACTERS.md §7: 24 running bits (short names; the script generator expands them from the bible)
RUNNING_BITS: tuple[str, ...] = (
    "No mirror flexing", "I'm older, so I'm right", "Hips. Now.", "Study card from the shorts pocket",
    "Dumpling count", "Tank top in January", "Seven out of ten", "Mandu the cat", "Fridge balance leaderboard",
    "Short version", "The apron", "Frank's excuses", "Welding metaphors", "Sun's visor", "Printer ink", "Aigo",
    "The AI winks", "Anniversary countdown", "Jajangmyeon Sunday", "The hidden kettlebell", "Phone calls from Mina",
    "The chair is Coach", "Write this down", "Old photos",
)

# CONTENT_SYSTEM §8.1: page slugs -> lead speakers (defaults; a request's page profile overrides)
PAGE_SPEAKERS: dict[str, tuple[str, ...]] = {
    "changyin": ("CHANG", "DUO"), "sunyoon-kitchen": ("SUN", "DUO"), "sunyoon": ("SUN", "DUO", "CHANG"),
    "changyin-strength": ("CHANG",), "changyin-mobility": ("CHANG",),
    "changyin-espanol": ("CHANG",),
}
