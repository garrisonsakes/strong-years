"""Rebuilds refs_es/manifest.json from the Spanish canon (CHARACTERS_ES.md §13.1 master prompts + the wardrobe tables
§4.5 / §5.5 / §15). Same schema and lock as production/refs/manifest.json: run only when the canon changes; the
output is LOCKED (production/refs/render_refs.py-style sha256 check over prompt + "\\n" + negative_prompt).

  python3 production/refs_es/build_manifest.py
"""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
C = (ROOT / "CHARACTERS_ES.md").read_text(encoding="utf-8")


def grab(label):
    return re.search(re.escape(label) + r"\*{0,2}\s*`([^`]+)`", C).group(1)


CHUY = grab("**Don Chuy master prompt (append the wardrobe-code text):")
LUPE = grab("**Doña Lupe master prompt (append the wardrobe-code text):")
CARMEN = grab("**Doña Carmen master prompt (append the wardrobe-code text):")
CHNEG = grab("**Don Chuy negative prompt (always):")
LUNEG = grab("**Doña Lupe negative prompt (always):")
CANEG = grab("**Doña Carmen negative prompt (always):")
HNEG = grab("**House negative additions (append to all):")


def ward(code):
    return re.search(r"\| \*\*" + re.escape(code) + r"\*\* \| [^|]+\| ([^|]+)\|", C).group(1).strip().replace("**", "").rstrip(".")


LOCK = {
    "chuy": "Same person as the reference images; keep facial structure, white mustache, hairline, thumb-knuckle scar and body proportions identical.",
    "lupe": "Same person as the reference images; keep facial structure, arched eyebrows, silver bun with the red-and-gold pin, cheek beauty mark and body proportions identical.",
    "carmen": "Same person as the reference images; keep facial structure, silver bun with the tortoiseshell comb, laugh lines and body proportions identical.",
    "duo_es": "Same two people as the reference images; keep both faces identical: Chuy's white mustache and thumb scar, Lupe's arched eyebrows, bun pin and beauty mark.",
}
MASTER = {"chuy": (CHUY, CHNEG), "lupe": (LUPE, LUNEG), "carmen": (CARMEN, CANEG)}
FIRST = {"chuy": "CH", "lupe": "LU", "carmen": "CA"}

CHUY_SHOTS = [
    ("front neutral, head and shoulders, plain warm-gray wall", "CH-TRABAJO", "none"),
    ("three-quarter left, warm smile, head and shoulders", "CH-TRABAJO", "none"),
    ("three-quarter right, mustache twitch suppressing a laugh", "CH-TRABAJO", "none"),
    ("left profile, head and shoulders", "CH-TRABAJO", "none"),
    ("right profile, head and shoulders", "CH-TRABAJO", "none"),
    ("front, chest laugh, eyes creased", "CH-TRABAJO", "none"),
    ("full body front, standing tall beside the wooden chair against the wall", "CH-TRAIN", "SET-ES-PATIO"),
    ("full body side view, sit-to-stand start position on the wooden chair against the wall", "CH-TRAIN", "SET-ES-PATIO"),
    ("medium-full, carrying two orange sand buckets by the handles, shoulders down", "CH-TRAIN", "SET-ES-COCHERA"),
    ("medium-full, hugging the canvas sandbag close to the belly", "CH-TRAIN", "SET-ES-COCHERA"),
    ("full body, hanging from the doorway pull-up bar, feet touching the floor", "CH-TRAIN", "SET-ES-COCHERA"),
    ("close-up of both hands palms up: calluses, thick fingers, gold wedding band on the left hand", "CH-TRAIN", "SET-ES-COCHERA"),
    ("close-up of the left hand: healed scar across the thumb knuckle, age spots", "CH-TRAIN", "SET-ES-COCHERA"),
    ("medium, grooming his mustache in the kitchen window reflection", "CH-TRABAJO", "SET-ES-COCINA"),
    ("medium-full, squatting to water a chile plant in a clay pot", "CH-PATIO", "SET-ES-PATIO"),
    ("full body, one hand on the black iron handrail, foot on the bottom porch step", "CH-CAMINAR", "SET-ES-ESCALONES"),
    ("full body walking toward camera on the sidewalk under jacaranda trees, handheld eye level", "CH-CAMINAR", "SET-ES-BANQUETA"),
    ("medium, at the table with a study card and a cafecito, explaining with one hand", "CH-TRABAJO", "SET-ES-COMEDOR"),
    ("medium, kitchen counter, sleeves rolled, wearing the red-and-white floral apron over his shirt", "CH-TRABAJO", "SET-ES-COCINA"),
    ("medium-full, seated on the sofa, reading glasses in hand, the dog on the rug", "CH-TRABAJO", "SET-ES-SALA"),
    ("medium, Sunday shirt, standing by the photo wall", "CH-DOMINGO", "SET-ES-SALA"),
    ("medium, seated on the bed edge, reading glasses on his forehead", "CH-NOCHE", "SET-ES-RECAMARA"),
    ("full body, kneeling to half-kneel beside the chair (floor-rise practice), one hand on the seat", "CH-TRAIN", "SET-ES-PATIO"),
    ("close-up, front, natural window light, skin texture and pores visible, no smile", "CH-TRABAJO", "none"),
]
LUPE_SHOTS = [
    ("front neutral, head and shoulders, plain warm-gray wall", "LU-CARDI-ROSA", "none"),
    ("three-quarter left, one eyebrow arched, reading glasses on", "LU-CARDI-ROSA", "none"),
    ("three-quarter right, eye-roll, glasses hanging on the chain", "LU-CARDI-ROSA", "none"),
    ("left profile showing the low bun", "LU-CARDI-ROSA", "none"),
    ("right profile showing the red-and-gold hair pin", "LU-CARDI-ROSA", "none"),
    ("front, laughing with eyes closed", "LU-CARDI-ROSA", "none"),
    ("full body standing in the kitchen by the talavera backsplash", "LU-COCINA", "SET-ES-COCINA"),
    ("medium, flipping a tortilla on the comal, steam", "LU-COCINA", "SET-ES-COCINA"),
    ("medium, weighing cooked beans on a digital scale, reading glasses on", "LU-COCINA", "SET-ES-COCINA"),
    ("close-up of hands: gold chain bracelet on the right wrist, gold band, chopping nopales", "LU-COCINA", "SET-ES-COCINA"),
    ("medium, seated at the table with the floral oilcloth, blunt look straight to camera", "LU-CARDI-ROSA", "SET-ES-COMEDOR"),
    ("medium, holding a phone playing a voice message, skeptical eyebrow", "LU-CARDI-AZUL", "SET-ES-COMEDOR"),
    ("medium, writing balance seconds on the kitchen calendar with a marker", "LU-COCINA", "SET-ES-COCINA"),
    ("full body walking on the sidewalk with the navy parasol open", "LU-CAMINAR", "SET-ES-BANQUETA"),
    ("full body at the porch handrail, balance stance, one hand hovering over the rail", "LU-CAMINAR", "SET-ES-ESCALONES"),
    ("full body, resistance band row anchored to the patio post", "LU-ENTRENA", "SET-ES-PATIO"),
    ("medium-full, seated on the sofa, arms crossed, amused", "LU-CARDI-AZUL", "SET-ES-SALA"),
    ("medium, holding up a handwritten card to camera", "LU-CARDI-ROSA", "SET-ES-COMEDOR"),
    ("medium, holding a bowl of caldo toward camera, steam", "LU-COCINA", "SET-ES-COCINA"),
    ("medium, at a produce stall holding a bundle of nopales", "LU-CAMINAR", "SET-ES-MERCADO"),
    ("medium, party dress, standing by the window", "LU-FIESTA", "SET-ES-SALA"),
    ("medium, evening lamp, hair in a loose braid", "LU-NOCHE", "SET-ES-RECAMARA"),
    ("close-up, front, window light, the beauty mark on the right cheekbone visible", "LU-CARDI-ROSA", "none"),
    ("close-up of the reading glasses on the turquoise beaded chain and the gold hoop earring", "LU-CARDI-ROSA", "none"),
]
CARMEN_SHOTS = [
    ("front neutral, head and shoulders, plain warm-gray wall", "CA-CARDI-TERRA", "none"),
    ("three-quarter left, warm teacher smile", "CA-CARDI-TERRA", "none"),
    ("three-quarter right, eyebrows raised, about to make a point", "CA-CARDI-TERRA", "none"),
    ("left profile showing the tortoiseshell comb", "CA-CARDI-TERRA", "none"),
    ("right profile", "CA-CARDI-TERRA", "none"),
    ("front, laughing", "CA-CARDI-TERRA", "none"),
    ("full body front on the concrete patio beside the lemon tree", "CA-PATIO", "SET-ES-PATIO"),
    ("full body side view, sit-to-stand start position on a chair against the wall", "CA-PATIO", "SET-ES-PATIO"),
    ("medium-full, carrying a bucket of sand by the handle, shoulders down", "CA-PATIO", "SET-ES-PATIO"),
    ("close-up of both hands gripping the bucket handle", "CA-PATIO", "SET-ES-PATIO"),
    ("full body, step-up on the bottom porch step, hand on the rail", "CA-CAMINAR", "SET-ES-ESCALONES"),
    ("full body walking on the park track, evening", "CA-CAMINAR", "SET-ES-PARQUE"),
    ("full body standing in the kitchen by the comal", "CA-COCINA", "SET-ES-COCINA"),
    ("medium, ladling frijoles de olla from a clay pot", "CA-COCINA", "SET-ES-COCINA"),
    ("medium, cracking eggs into a bowl, glasses on her head", "CA-COCINA", "SET-ES-COCINA"),
    ("close-up of hands chopping nopales", "CA-COCINA", "SET-ES-COCINA"),
    ("medium, seated at the table, explaining with a pencil and a notebook", "CA-CARDI-TERRA", "SET-ES-COMEDOR"),
    ("medium-full, seated on the sofa beneath the photo wall", "CA-CARDI-TERRA", "SET-ES-SALA"),
    ("medium, kneeling to half-kneel beside a chair (floor-rise practice)", "CA-PATIO", "SET-ES-PATIO"),
    ("medium, party dress, standing by the window", "CA-FIESTA", "SET-ES-SALA"),
    ("medium, evening, cardigan over the shoulders", "CA-NOCHE", "SET-ES-RECAMARA"),
    ("full body back view walking away on the park track", "CA-CAMINAR", "SET-ES-PARQUE"),
    ("close-up, front, natural light, skin texture and laugh lines visible", "CA-CARDI-TERRA", "none"),
    ("close-up of the tortoiseshell comb in the silver bun", "CA-CARDI-TERRA", "none"),
]
DUO = [
    ("both on the sofa, Lupe on the left, Chuy on the right, laughing", "CH-TRABAJO + LU-CARDI-ROSA", "SET-ES-SALA"),
    ("garage: Chuy carrying two sand buckets, Lupe in the doorway with arms crossed", "CH-TRAIN + LU-CARDI-AZUL", "SET-ES-COCHERA"),
    ("kitchen side by side at the comal, Chuy in the floral apron", "CH-TRABAJO + LU-COCINA", "SET-ES-COCINA"),
    ("walking side by side on the sidewalk, Lupe with the parasol", "CH-CAMINAR + LU-CAMINAR", "SET-ES-BANQUETA"),
    ("at the table, Lupe pointing at a study card, Chuy reading over his glasses", "CH-TRABAJO + LU-CARDI-ROSA", "SET-ES-COMEDOR"),
    ("patio, both in a balance stance by the chair against the wall, one hand hovering", "CH-TRAIN + LU-ENTRENA", "SET-ES-PATIO"),
]


def item(i, who, shot, code, setc, status="LOCKED"):
    if who == "duo_es":
        cc, lc = [x.strip() for x in code.split("+")]
        pos = f"Two people. Left: {LUPE}, wearing {ward(lc)}. Right: {CHUY}, wearing {ward(cc)}"
        neg = f"{CHNEG}, {LUNEG}, {HNEG}, extra people"
        refs = ["CH01", "CH02", "LU01", "LU02"]
    else:
        m, n = MASTER[who]
        pos, neg = f"{m}, wearing {ward(code)}", f"{n}, {HNEG}"
        p = FIRST[who]
        refs = [] if i == f"{p}01" else ([f"{p}01"] if i == f"{p}02" else [f"{p}01", f"{p}02"])
    scene = f"Shot: {shot}." + (f" Set {setc} (the empty set plate is a background reference)." if setc != "none" else "")
    prompt = f"{pos}. {scene} 9:16 vertical. {LOCK[who]}"
    return {"id": i, "character": who, "shot": shot, "wardrobe_code": code, "set_code": setc, "prompt": prompt,
            "negative_prompt": neg, "aspect_ratio": "9:16", "model": "Nano Banana (Gemini image) primary; NB Pro fallback",
            "refs_required": refs, "seed": int(hashlib.sha256(("es-" + i).encode()).hexdigest()[:8], 16) % 2_000_000_000,
            "candidates": 4, "locked": status == "LOCKED", "stage": status,
            "sha256": hashlib.sha256((prompt + "\n" + neg).encode()).hexdigest()}


def build():
    items = [item(f"CH{k:02d}", "chuy", *s) for k, s in enumerate(CHUY_SHOTS, 1)] + \
            [item(f"LU{k:02d}", "lupe", *s) for k, s in enumerate(LUPE_SHOTS, 1)] + \
            [item(f"DL{k:02d}", "duo_es", *s) for k, s in enumerate(DUO, 1)] + \
            [item(f"CA{k:02d}", "carmen", *s, status="STAGED") for k, s in enumerate(CARMEN_SHOTS, 1)]
    return {"version": "2026-10-02",
            "status": "LOCKED: master prompts verbatim from CHARACTERS_ES.md §13.1 plus the wardrobe-code text (§4.5 / §5.5 / §15). "
                      "Do not paraphrase. Any edit changes sha256 and the renderer refuses the item. Doña Carmen (CA01–CA24) is "
                      "STAGED: generated only when her page opens (the $50K rung or the day-30 switch rule, CHARACTERS_ES.md §0).",
            "order": "Generate CH01 and LU01 first; a person and the community reviewer pick one candidate each; then CH02/LU02 "
                     "with those as refs; then the rest with the two locked refs (<= 5 refs per call); duo last. Carmen only when opened.",
            "gate": "Spanish page opens at the $30K retained-MRR rung (BRIEF.md CANON UPDATE 5); no generation spend before the governor flips it.",
            "counts": {"chuy": len(CHUY_SHOTS), "lupe": len(LUPE_SHOTS), "duo_es": len(DUO), "carmen": len(CARMEN_SHOTS)},
            "items": items}


if __name__ == "__main__":
    man = build()
    assert man["counts"] == {"chuy": 24, "lupe": 24, "duo_es": 6, "carmen": 24}, man["counts"]
    (HERE / "manifest.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(man["items"]), "items")
