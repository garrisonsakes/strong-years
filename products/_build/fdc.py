"""USDA FoodData Central (SR Legacy, April 2018 release) lookup helper.
Builds a compact JSON of the nutrients we report: kcal (1008), protein (1003), fiber (1079),
sodium (1093), leucine (1213) per 100 g, keyed by fdc_id."""
import csv, json, sys, os, re
D = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FDC_DIR")
OUT = os.path.join(os.path.dirname(__file__), "fdc_sr_legacy_subset.json")
NUT = {"1008": "kcal", "1003": "protein_g", "1079": "fiber_g", "1093": "sodium_mg", "1213": "leucine_g"}
def build():
    foods = {}
    with open(os.path.join(D, "food.csv")) as f:
        for r in csv.DictReader(f):
            foods[r["fdc_id"]] = {"desc": r["description"]}
    with open(os.path.join(D, "food_nutrient.csv")) as f:
        for r in csv.DictReader(f):
            k = NUT.get(r["nutrient_id"])
            if k and r["fdc_id"] in foods:
                foods[r["fdc_id"]][k] = float(r["amount"])
    json.dump(foods, open(OUT, "w"))
    print(len(foods))
if __name__ == "__main__":
    build()
