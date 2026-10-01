"""Rebuilds refs/manifest.json from the canon (CHARACTERS.md wardrobe table + VIDEO_RE.md §9.2.1 master prompts).
Run only when the canon changes; the output is LOCKED (render_refs.py verifies every sha256)."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V = (ROOT / "VIDEO_RE.md").read_text(encoding="utf-8")
C = (ROOT / "CHARACTERS.md").read_text(encoding="utf-8")


def grab(label):
    return re.search(re.escape(label) + r"\*{0,2}\s*`([^`]+)`", V).group(1)


CHANG = grab("**Chang (append the wardrobe-code text):")
SUN = grab("**Sun Yoon (append the wardrobe-code text):")
CNEG = grab("**Chang negative prompt (always):")
SNEG = grab("**Sun negative prompt (always):")
HNEG = grab("**House negative additions** (from the forensics; append to both):")


def ward(code):
    return re.search(r"\| \*\*" + re.escape(code) + r"\*\* \| [^|]+\| ([^|]+)\|", C).group(1).strip().replace("**", "").rstrip(".")


LOCK_C = "Same person as the reference images; keep facial structure, hairline, beard, eyebrow scar and body proportions identical."
LOCK_S = "Same person as the reference images; keep facial structure, silver bob, tortoiseshell clip, mole beside the left nostril and body proportions identical."
LOCK_D = "Same two people as the reference images; keep both faces, hairlines, Chang's beard and eyebrow scar, Sun's bob, clip and mole identical."

CHANG_SHOTS = [
    ("C01", "front neutral, head and shoulders, plain warm-gray wall", "C-CASUAL", "none"),
    ("C02", "three-quarter left, warm smile, head and shoulders", "C-CASUAL", "none"),
    ("C03", "three-quarter right, warm smile, head and shoulders", "C-CASUAL", "none"),
    ("C04", "left profile, head and shoulders", "C-CASUAL", "none"),
    ("C05", "right profile, head and shoulders", "C-CASUAL", "none"),
    ("C06", "front, mid laugh, eyes creased", "C-CASUAL", "none"),
    ("C07", "full body front, standing tall, arms relaxed", "C-TRAIN-A", "SET-GARAGE"),
    ("C08", "full body back view, shoulders and slight upper-back rounding visible", "C-TRAIN-A", "SET-GARAGE"),
    ("C09", "full body side view, sit-to-stand start position on a wooden chair against the wall", "C-TRAIN-A", "SET-GARAGE"),
    ("C10", "medium-full, holding a 12 kg kettlebell close at the chest, forearm tendons visible", "C-TRAIN-A", "SET-GARAGE"),
    ("C11", "close-up of both hands palms up: calluses, gold wedding band on the left hand", "C-TRAIN-A", "SET-GARAGE"),
    ("C12", "close-up of the back of the right hand: burn scar, age spots, chalk", "C-TRAIN-A", "SET-GARAGE"),
    ("C13", "medium, writing on a clipboard log by the pegboard", "C-TRAIN-A", "SET-GARAGE"),
    ("C14", "full body, outdoors at the fence rail, one hand on the rail", "C-TRAIN-B", "SET-YARD"),
    ("C15", "full body, tai chi opening posture on a foggy promenade by a steel railing", "C-TRAIN-B", "SET-PROM"),
    ("C16", "medium, kitchen counter, sleeves rolled, pink floral apron", "C-KITCHEN", "SET-KITCHEN"),
    ("C17", "medium-full, seated on the sofa, reading glasses in hand", "C-CASUAL", "SET-LIVING"),
    ("C18", "medium, evening lamp light, relaxed", "C-CASUAL", "SET-LIVING"),
    ("C19", "medium, formal, standing by the window", "C-FORMAL", "SET-LIVING"),
    ("C20", "medium, seated on the bed edge, reading glasses on forehead", "C-BED", "SET-BED"),
    ("C21", "full body, on the bottom step of a five-step stoop, one hand on the handrail", "C-TRAIN-A", "SET-STOOP"),
    ("C22", "medium, at the table with a study card and a cup of barley tea, explaining with one hand", "C-CASUAL", "SET-TABLE"),
    ("C23", "full body walking toward camera on the promenade, handheld eye level", "C-TRAIN-B", "SET-PROM"),
    ("C24", "close-up, front, natural window light, skin texture and pores visible, no smile", "C-CASUAL", "none"),
]
SUN_SHOTS = [
    ("S01", "front neutral, head and shoulders, plain warm-gray wall", "S-CARDI-JADE", "none"),
    ("S02", "three-quarter left, mischievous smirk, reading glasses on", "S-CARDI-JADE", "none"),
    ("S03", "three-quarter right, smirk, glasses hanging on the cord", "S-CARDI-JADE", "none"),
    ("S04", "left profile showing the tortoiseshell clip", "S-CARDI-JADE", "none"),
    ("S05", "right profile", "S-CARDI-JADE", "none"),
    ("S06", "front, laughing, eyes creased", "S-CARDI-JADE", "none"),
    ("S07", "full body standing in the kitchen", "S-KITCHEN", "SET-KITCHEN"),
    ("S08", "medium, stirring a pot on the gas stove, steam", "S-KITCHEN", "SET-KITCHEN"),
    ("S09", "medium, weighing tofu on a digital scale, reading glasses on", "S-KITCHEN", "SET-KITCHEN"),
    ("S10", "close-up of hands: jade bangle on the left wrist, gold wedding band, chopping scallions", "S-KITCHEN", "SET-KITCHEN"),
    ("S11", "medium, seated at the table, blunt look straight to camera", "S-CARDI-JADE", "SET-TABLE"),
    ("S12", "medium, seated in the living room", "S-CARDI-MUSTARD", "SET-LIVING"),
    ("S13", "full body walking on the promenade", "S-WALK", "SET-PROM"),
    ("S14", "full body at the backyard fence, balance stance, one hand hovering over the rail", "S-WALK", "SET-YARD"),
    ("S15", "full body, resistance band row", "S-TRAIN", "SET-GARAGE"),
    ("S16", "medium, formal, standing by the window", "S-FORMAL", "SET-LIVING"),
    ("S17", "medium, evening lamp", "S-BED", "SET-BED"),
    ("S18", "medium, writing on the fridge whiteboard with a marker", "S-KITCHEN", "SET-KITCHEN"),
    ("S19", "close-up, front, window light, the mole beside the left nostril visible", "S-CARDI-JADE", "none"),
    ("S20", "medium, holding a bowl of soup toward camera, steam", "S-KITCHEN", "SET-KITCHEN"),
    ("S21", "medium, in the produce aisle holding a napa cabbage", "S-WALK", "SET-MARKET"),
    ("S22", "medium-full, seated on the sofa, arms crossed, amused", "S-CARDI-MUSTARD", "SET-LIVING"),
    ("S23", "full body back view walking away on the promenade", "S-WALK", "SET-PROM"),
    ("S24", "close-up of the reading glasses on the jade beaded cord and the pearl stud earring", "S-CARDI-JADE", "none"),
]
DUO = [
    ("D01", "both on the sofa, Sun on the left, Chang on the right, relaxed, laughing", "C-CASUAL + S-CARDI-JADE", "SET-LIVING"),
    ("D02", "garage: Chang lifting a 12 kg kettlebell, Sun in the doorway with arms crossed", "C-TRAIN-A + S-CARDI-MUSTARD", "SET-GARAGE"),
    ("D03", "kitchen side by side at the counter", "C-KITCHEN + S-KITCHEN", "SET-KITCHEN"),
    ("D04", "walking side by side on the foggy promenade", "C-TRAIN-B + S-WALK", "SET-PROM"),
    ("D05", "at the table, Sun pointing at a study card, Chang reading over his glasses", "C-CASUAL + S-CARDI-JADE", "SET-TABLE"),
    ("D06", "backyard fence, both in a balance stance, one hand hovering over the rail", "C-TRAIN-B + S-WALK", "SET-YARD"),
]


def item(i, who, shot, code, setc):
    if who == "chang":
        pos, neg, lock, refs = f"{CHANG}, wearing {ward(code)}", f"{CNEG}, {HNEG}", LOCK_C, ([] if i == "C01" else ["C01", "C02"])
    elif who == "sun":
        pos, neg, lock, refs = f"{SUN}, wearing {ward(code)}", f"{SNEG}, {HNEG}", LOCK_S, ([] if i == "S01" else ["S01", "S02"])
    else:
        cc, sc = [x.strip() for x in code.split("+")]
        pos = f"Two people. Left: {SUN}, wearing {ward(sc)}. Right: {CHANG}, wearing {ward(cc)}"
        neg, lock, refs = f"{CNEG}, {SNEG}, {HNEG}, extra people", LOCK_D, ["C01", "C02", "S01", "S02"]
    if i in ("C02", "S02"):
        refs = [refs[0]]
    scene = f"Shot: {shot}." + (f" Set {setc} (the empty set plate is a background reference)." if setc != "none" else "")
    prompt = f"{pos}. {scene} 9:16 vertical. {lock}"
    return {"id": i, "character": who, "shot": shot, "wardrobe_code": code, "set_code": setc, "prompt": prompt,
            "negative_prompt": neg, "aspect_ratio": "9:16", "model": "Nano Banana (Gemini image) primary; NB Pro fallback",
            "refs_required": refs, "seed": int(hashlib.sha256(i.encode()).hexdigest()[:8], 16) % 2_000_000_000,
            "candidates": 4, "locked": True, "sha256": hashlib.sha256((prompt + "\n" + neg).encode()).hexdigest()}


if __name__ == "__main__":
    items = [item(s[0], "chang", *s[1:]) for s in CHANG_SHOTS] + [item(s[0], "sun", *s[1:]) for s in SUN_SHOTS] + \
            [item(s[0], "duo", *s[1:]) for s in DUO]
    man = {"version": "2026-10-01",
           "status": "LOCKED: master prompts verbatim from CHARACTERS §13.1 / VIDEO_RE §9.2.1 plus the wardrobe-code text "
                     "(§4.5 / §5.5). Do not paraphrase. Any edit changes sha256 and render_refs.py refuses the item.",
           "order": "Generate C01 and S01 first; a person picks one candidate each; then C02/S02 with those as refs; then the "
                    "rest with the two locked refs (<= 5 refs per call); duo last.",
           "counts": {"chang": 24, "sun": 24, "duo": 6}, "items": items}
    (HERE / "manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(items), "items")
