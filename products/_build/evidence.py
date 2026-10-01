"""Parse EVIDENCE.md so every product appendix quotes the exact same wording and sources."""
import os, re
EV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "EVIDENCE.md")


def load():
    ev = {}
    for line in open(EV_PATH):
        m = re.match(r"\|\s*(E\d+b?)\s*\|(.*)\|\s*([^|]*)\|\s*(.*)\|\s*$", line)
        if m:
            eid, finding, grade, source = [x.strip() for x in m.groups()]
            ev[eid] = dict(id=eid, finding=finding, grade=grade, source=source)
    return ev


EV = load()


def _clean(md):
    # strip bold markers for the plain appendix
    return md.replace("**", "")


# Product-copy policy (coordinator, Sep 30 2026): no fall-risk / fall-reduction / fall-prevention claims anywhere in the
# paid products. Fall-outcome studies are not cited in products; screening tools are described without fall-risk wording.
EXCLUDE_IN_PRODUCTS = {"E12", "E14", "E36"}
PRODUCT_FINDING = {
    "E04": "Around age 75, muscle mass drops about 0.6–1% per year while strength drops 2.5–4% per year. Strength declines 2–5× faster than mass.",
    "E11": "CDC STEADI 30-second chair stand (17-inch chair, arms crossed), used in the CDC's older-adult screening. Below-average scores: men 60–64 <14, 65–69 <12, 70–74 <12, 75–79 <11, 80–84 <10, 85–89 <8, 90–94 <7. Women 60–64 <12, 65–69 <11, 70–74 <10, 75–79 <10, 80–84 <9, 85–89 <8, 90–94 <4. If arms are used to stand, the score is 0.",
    "E13": "Otago Exercise Programme: a home programme of leg strengthening, balance exercises and walking designed for older adults, studied in 7 trials with 1,503 people (mean age 81.6). We use its exercise types and progressions; we make no outcome claim from it.",
    "E50": "CDC STEADI 4-Stage Balance Test: feet side by side, semi-tandem (instep beside big toe), tandem (heel to toe), one leg; up to 10 s each, stop at the first stage not held. The CDC uses the tandem stand as a screening checkpoint: under 10 s is worth discussing with a clinician.",
    "E51": "CDC STEADI Timed Up and Go: stand from a chair, walk 10 feet (3 m) at normal pace, turn, walk back, sit. The CDC uses 12 seconds or more as a screening threshold worth discussing with a clinician. Always have someone stand by.",
}


def appendix_md(ids, title="Where the numbers come from", intro=None):
    ids = sorted(set(ids) - EXCLUDE_IN_PRODUCTS, key=lambda x: (int(re.sub(r"\D", "", x)), x))
    out = [f"# {title}\n"]
    out.append(intro or (
        "Every number and health statement in this book traces to one of the entries below. "
        "They are the same evidence IDs our whole team uses (EVIDENCE.md). Grade A means a Cochrane review, a large "
        "meta-analysis or a guideline body. B means a single good trial or a small meta-analysis. C means an "
        "observational study: it shows a link, not cause and effect. D means lab, physiology or label data.\n"))
    out.append("")
    for i in ids:
        e = EV.get(i)
        if not e:
            raise KeyError(f"Evidence ID {i} not found in EVIDENCE.md")
        src = _clean(e["source"])
        # make bare URLs wrap nicely
        out.append(f'<div class="keep" markdown="1">\n\n**{i}** (grade {e["grade"]}). {_clean(PRODUCT_FINDING.get(i, e["finding"]))}\n\n'
                   f'<p class="src">Source: {src}</p>\n\n</div>\n')
    return "\n".join(out)
