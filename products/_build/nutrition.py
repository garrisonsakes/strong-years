"""Per-serving nutrition from USDA FDC SR Legacy (E52) + label data (E53)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
FDC = json.load(open(os.path.join(HERE, "fdc_sr_legacy_subset.json")))
LABEL = {  # per 100 g, Open Food Facts (E53)
    "gochujang": dict(desc="Gochujang, Sempio (label, Open Food Facts 8801005000178)", kcal=233, protein_g=5.0, fiber_g=2.7, sodium_mg=2640, leucine_g=None),
    "chunjang": dict(desc="Chunjang black bean paste, Obok (label, Open Food Facts 8801126032447)", kcal=200, protein_g=20.0, fiber_g=0.0, sodium_mg=3200, leucine_g=None),
}
KEYS = ["kcal", "protein_g", "fiber_g", "sodium_mg"]


def food(src):
    if src is None:
        return None
    if isinstance(src, str):
        return LABEL[src]
    return FDC[str(src)]


def line(g, src):
    f = food(src)
    out = {k: 0.0 for k in KEYS}
    missing = []
    if f is None or g == 0:
        return out, missing
    for k in KEYS:
        v = f.get(k)
        if v is None:
            missing.append(k)
            v = 0.0
        out[k] = v * g / 100.0
    return out, missing


def calc(r):
    tot = {k: 0.0 for k in KEYS}
    rows = []
    for amt, txt, g, src in r["ings"]:
        v, miss = line(g, src)
        for k in KEYS:
            tot[k] += v[k]
        rows.append(dict(amt=amt, txt=txt, g=g, src=src, v=v, miss=miss))
    per = {k: tot[k] / r["serves"] for k in KEYS}
    return per, tot, rows


if __name__ == "__main__":
    from recipes import R
    for r in R:
        per, tot, rows = calc(r)
        miss = [f"{x['txt'][:18]}:{','.join(x['miss'])}" for x in rows if x['miss']]
        print(f"{r['id']:3} {r['name'][:42]:42} P {per['protein_g']:5.1f}  F {per['fiber_g']:4.1f}  kcal {per['kcal']:5.0f}  Na {per['sodium_mg']:5.0f}  {miss}")
