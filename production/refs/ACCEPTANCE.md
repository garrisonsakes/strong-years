# Reference pack acceptance checklist (54 images: Chang 24, Sun 24, duo 6)

A person (content lead) signs off each image before it is locked. Generate 4 candidates per item (`render_refs.py`), pick one or reject all. Reject = regenerate with the same locked prompt and a new seed; never edit the prompt (the sha256 lock refuses it).

## Every image
- [ ] Photorealistic, iPhone eye-level look, natural light; no plastic or airbrushed skin; pores and age spots visible.
- [ ] No text, letters, logos or watermarks anywhere (no garbled labels on props).
- [ ] Hands: five fingers each, natural joints, no fused or extra fingers; props held believably.
- [ ] Teeth: no uniform white band; natural for the age.
- [ ] No costume clichés from the negative prompts (robe, monk, topknot, conical hat, geisha, dragon-lady, caricature makeup).
- [ ] Wardrobe matches the code text exactly (colour, garment, shoes); set matches the set code.
- [ ] 9:16, subject inside the safe area (top 220 px and bottom 420 px free of the face).

## Chang (C01–C24)
- [ ] 74-ish, lean tradesman build (15–18% body-fat look), not a bodybuilder; slight upper-back rounding.
- [ ] White crew cut receding at the temples; trimmed 1 cm white beard and mustache; bushy white eyebrows.
- [ ] Small scar through the OUTER LEFT eyebrow (his left).
- [ ] Gold wedding band on the LEFT hand; burn scar on the BACK of the RIGHT hand (C11/C12 especially).
- [ ] Same face as the locked C01 and C02 (compare side by side at 100%).

## Sun Yoon (S01–S24)
- [ ] 76-ish, petite (155 cm), upright; silver-white chin-length bob, side part, tortoiseshell clip on the LEFT.
- [ ] Mole beside the LEFT nostril; coral-rose lipstick; pearl studs; jade bangle on the LEFT wrist; gold band.
- [ ] Reading glasses on a jade-green beaded cord (S-CARDI looks).
- [ ] Hanbok only in S16 if the holiday variant is chosen; never in health content.
- [ ] Same face as the locked S01 and S02.

## Duo (D01–D06)
- [ ] Sun on the left, Chang on the right (house framing); both faces match their locked refs.
- [ ] Height difference believable (170 cm vs 155 cm); no third person; no merged hands.

## Lock
- [ ] Selected file renamed `<ID>.png`, its sha256 written into `refs/locked.json` with the reviewer's name and date.
- [ ] ArcFace similarity to C01/S01 ≥ 0.6 when the QA worker's face model is installed (workers/qa/face.py).
- [ ] C2PA: reference images are internal and never published.
