# Spanish reference pack acceptance checklist (78 images: Don Chuy 24, Doña Lupe 24, duo 6, Doña Carmen 24 staged)

Source: `manifest.json` (built by `build_manifest.py` from CHARACTERS_ES.md §13.1; same schema and sha256 lock as production/refs/). Render with `render_refs_es.py` (DRY_RUN by default). A person (content lead) **and the community cultural reviewer** (CHARACTERS_ES.md §14.1) sign off each image before it is locked. Generate 4 candidates per item, pick one or reject all. Reject = regenerate with the same locked prompt and a new seed; never edit the prompt. **Gate:** nothing is generated before the Spanish page's $30K retained-MRR rung opens (CANON UPDATE 5); Carmen's 24 only when her page opens.

## Every image
- [ ] Photorealistic, iPhone eye-level look, natural light; no plastic or airbrushed skin; pores, age spots and sun damage visible.
- [ ] No text, letters, logos or watermarks anywhere (the tiendita sign and hardware-store calendar carry no readable brand).
- [ ] Hands: five fingers each, natural joints; props (cubetas, costal, comal, nopales) held believably.
- [ ] Teeth natural for the age; no uniform white band.
- [ ] **No caricature:** no sombrero, charro, poncho, serape, mariachi outfit, folklórico dress, flower crown, Frida styling, rebozo-as-costume, cartoon mustache, "spicy" makeup, poverty staging.
- [ ] **No religious objects** in frame (altar, saint, rosary, medal) and no flags.
- [ ] Wardrobe matches the code text exactly (colour, garment, shoes); set matches the set code (CHARACTERS_ES.md §6).
- [ ] 9:16, subject inside the safe area (top 220 px and bottom 420 px free of the face).

## Don Chuy (CH01–CH24)
- [ ] 74-ish bricklayer build: broad shoulders, strong forearms, thick callused hands, small belly; not a bodybuilder.
- [ ] Thick, neatly trimmed WHITE mustache (not cartoonish, not handlebar); light white stubble; short side-combed white hair.
- [ ] Healed scar across the LEFT thumb knuckle (CH13 especially); gold band on the LEFT hand.
- [ ] Same face as the locked CH01 and CH02 (compare side by side at 100%).

## Doña Lupe (LU01–LU24)
- [ ] 72-ish, petite (152 cm), straight posture; silver hair with a few dark strands in a LOW bun; red-and-gold enamel pin on the RIGHT.
- [ ] Arched soft-brown eyebrows; beauty mark on the RIGHT cheekbone; rose-brown lipstick; gold hoops; thin gold bracelet on the RIGHT wrist.
- [ ] Reading glasses on a TURQUOISE beaded chain in the cardigan looks.
- [ ] Same face as the locked LU01 and LU02.

## Duo (DL01–DL06)
- [ ] Lupe on the left, Chuy on the right (house framing); both faces match their locked refs.
- [ ] Height difference believable (172 cm vs 152 cm); no third person; no merged hands.
- [ ] DL03: Chuy in the floral apron reads as affectionate comedy, not mockery.

## Doña Carmen (CA01–CA24, STAGED)
- [ ] 72-ish, sturdy and strong, defined arms; silver low bun with a tortoiseshell comb; glasses on her head; gold hoops.
- [ ] Clearly a different person from Doña Lupe (face shape, build, hair accessory) when the two contact sheets sit side by side.
- [ ] Same face as the locked CA01 and CA02.

## Lock
- [ ] Selected file renamed `<ID>.png` in `production/refs_es/locked/`, its sha256 written into `refs_es/locked.json` with both reviewers' names and the date.
- [ ] ArcFace similarity to CH01 / LU01 / CA01 ≥ 0.6 when the QA worker's face model is installed (workers/qa/face.py).
- [ ] C2PA: reference images are internal and never published.
