"""Product 2: Sun Yoon's Strong Kitchen ($17 front end)."""
import os, sys, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import render, cover_html, DISCLOSURE, PRODUCTS, box, say
from evidence import appendix_md
from recipes import R
from nutrition import calc, food, FDC, LABEL, line

NAME = "Sun Yoon's Strong Kitchen"
BYID = {r["id"]: r for r in R}
NUT = {r["id"]: calc(r) for r in R}


def rnd(x, n=10):
    return int(round(x / n) * n)


def per_str(rid):
    per = NUT[rid][0]
    return (round(per["protein_g"]), round(per["fiber_g"], 1), rnd(per["kcal"]), rnd(per["sodium_mg"]))


CAUTION = {
    "kimchi": "Kimchi is salty. Watching sodium? Small portions, or rinse it.",
    "leafy_greens": "On warfarin? Keep greens steady from week to week; don't suddenly change how much you eat. Ask your doctor.",
    "high_protein": "Kidney disease? Ask your doctor for your protein number (E28).",
    "honey": "Honey: never for babies under 1. Diabetes: honey counts as sugar (or leave it out).",
    "fiber": "High fiber. Go up slowly and drink water, or you'll feel it (E24).",
    "shellfish": "Shellfish allergy: swap in cubed firm tofu, or chicken breast cooked to 165°F.",
    "seaweed": "Thyroid condition? Seaweed can be very high in iodine (E58). Ask your doctor how much is okay for you.",
    "hot_oil": "Pour hot oil away from you, with dry hands. Keep grandkids and pets out of the kitchen for that step.",
    "braise_overcount": "Our sodium number is an overestimate: we count all the soy sauce, but most of it stays in the pot.",
    "kiwi": "Kiwi allergy (some people with latex allergy react to kiwi): swap a ripe persimmon or pear.",
}


def cautions(r):
    per = NUT[r["id"]][0]
    tags = list(r["tags"])
    if per["protein_g"] >= 30 and "high_protein" not in tags:
        tags.append("high_protein")
    if per["fiber_g"] >= 8 and "fiber" not in tags:
        tags.append("fiber")
    out = [CAUTION[t] for t in tags if t in CAUTION]
    if per["sodium_mg"] >= 750:
        out.append(f"This one is on the salty side (about {rnd(per['sodium_mg'])} mg sodium per serving). Watching sodium? Use half the paste or soy sauce and add water or unsalted broth.")
    return out


def recipe_md(r):
    p, f, k, na = per_str(r["id"])
    out = [f'<div class="recipe" markdown="1">\n',
           f"## {r['name']}\n",
           f"*{r['native']}* &nbsp;·&nbsp; Serves {r['serves']} &nbsp;·&nbsp; {r['active']} minutes hands-on, {r['total']} minutes total\n",
           say("sun", r["intro"]),
           '<table class="nut"><tr>'
           f'<td><span class="n">{p} g</span><br>protein</td>'
           f'<td><span class="n">{f} g</span><br>fiber</td>'
           f'<td><span class="n">{k}</span><br>calories</td>'
           f'<td><span class="n">{na} mg</span><br>sodium</td></tr></table>\n',
           '<p class="fine">Per serving. Calculated from USDA FoodData Central (E52); method and every ingredient value at the back of the book.</p>\n',
           "### You need\n"]
    for amt, txt, g, src in r["ings"]:
        out.append(f"- **{amt}** {txt}")
    out.append("\n### Steps\n")
    for i, s in enumerate(r["steps"], 1):
        out.append(f"{i}. {s}")
    out.append("")
    out.append(f"**Soft-food version:** {r['soft']}\n")
    out.append(f"**Keeps:** {r['store']}\n")
    cs = cautions(r)
    if cs:
        out.append(box("note", "Who should skip or ask first:", " ".join(cs)))
    out.append("</div>\n")
    return "\n".join(out)


# --------------------------------------------------------------- protein guide
def protein_md():
    rows = []
    for lb in [100, 120, 140, 160, 180, 200, 220]:
        kg = lb / 2.2046
        rows.append(f"| {lb} lb ({kg:.0f} kg) | {kg*1.0:.0f}–{kg*1.2:.0f} g | {kg*1.2:.0f}–{kg*1.5:.0f} g | {kg*1.0/3:.0f}–{kg*1.2/3:.0f} g |")
    foods = [("1 large egg", 50, 171287), ("3/4 cup plain nonfat Greek yogurt", 170, 170894),
             ("1/2 block (7 oz) firm tofu", 198, 172448), ("4 oz raw chicken breast (about 3 oz cooked)", 113, 171077),
             ("4 oz raw salmon", 113, 175167), ("1 can (5 oz) light tuna, drained", 113, 173709),
             ("4 oz raw top sirloin", 113, 174055), ("4 oz raw shrimp", 113, 175179),
             ("1/2 cup shelled edamame", 78, 168411), ("1 cup unsweetened soy milk", 243, 175215),
             ("1 cup 2% milk", 244, 171267), ("1/2 cup 2% cottage cheese", 113, 172182),
             ("2 Tbsp peanut butter", 32, 172470), ("1 cup cooked brown rice", 195, 169704)]
    frows = []
    for name, g, src in foods:
        f = food(src)
        pr = f["protein_g"] * g / 100
        le = f.get("leucine_g")
        le_s = f"{le*g/100:.1f} g" if le is not None else "not reported"
        frows.append(f"| {name} | {pr:.0f} g | {le_s} | {src} |")
    return f"""
# Protein: how much, and how to fit it in

{say("sun", "Short version: most people over 65 eat protein at dinner and forget it at breakfast. Your muscles don't save it up for later. Spread it out. Grams, not vibes.")}

An international expert group (PROT-AGE) recommends that adults over 65 eat **1.0 to 1.2 grams of protein per kilogram of body weight a day**, and **1.2 to 1.5 g/kg** if they are active or recovering from illness, unless they have severe kidney disease. They suggest **25 to 30 grams per meal**, with about 2.5 to 2.8 grams of leucine, the amino acid that switches muscle building on (E28).

<div class="box stop" markdown="1">
<span class="label">Kidney disease? Ask your doctor for your number first.</span> These targets are for adults without severe kidney disease. If you have kidney disease, diabetes with kidney changes, or have been told to limit protein, your doctor or dietitian sets your number (E28).
</div>

## Your daily number

Find your weight. Read across.

| Your weight | Daily protein (1.0–1.2 g/kg) | If active or recovering (1.2–1.5 g/kg) | Per meal, 3 meals |
|---|---|---|---|
""" + "\n".join(rows) + f"""

Most people land at **25 to 30 grams at each meal**. That's why almost every breakfast, lunch and dinner in this book has 25 grams or more per serving. The snacks have about 14 to 16.

## What 25 grams looks like

Protein and leucine per portion, calculated from USDA FoodData Central (E52). "Not reported" means USDA doesn't list leucine for that food.

| Food | Protein | Leucine | USDA FDC ID |
|---|---|---|---|
""" + "\n".join(frows) + f"""

**Sun's plate:** a fist of rice or noodles, a palm-and-a-half of protein (or two eggs plus tofu), and two fists of vegetables. Breakfast counts. Breakfast counts most.

**Hard to chew?** Soft protein is still protein: eggs cooked until firm, tofu, fish, Greek yogurt, cottage cheese, the chicken and ginger rice porridge, and ground meat in soups. Every recipe in this book has a soft-food version.

**Not hungry?** Eat the protein first, then the rice. And drink protein: a cup of soy milk or milk adds 7 to 8 grams.
"""


# --------------------------------------------------------------- fiber ladder
def fiber_md():
    def fib(g, src):
        return food(src)["fiber_g"] * g / 100
    kiwi = fib(150, 168153)
    brown = fib(195, 169704)
    white = food(168935)["fiber_g"] * 186 / 100
    edam = fib(78, 168411)
    flax = fib(7, 169414)
    prune = fib(47.5, 168162)
    oats = fib(40, 173904)
    broc = fib(91, 170379)
    bokc = fib(170, 170390)
    carrot = fib(61, 170393)
    total = kiwi + (brown - white) + edam + flax + prune + oats + broc + bokc + carrot
    return f"""
# The fiber ladder

{say("sun", "Everybody wants the magic tea. There is no magic tea. There is fiber, water and walking. Boring. Works. Write this down.")}

In a large review of studies (the Lancet, 2019), people eating **25 to 29 grams of fiber a day** had 15 to 30% lower rates of death from any cause and from heart disease, and lower rates of type 2 diabetes and colorectal cancer, than people eating the least. More fiber was linked with more benefit (E24). Those are links from long-term studies, not a promise. It's still the best-supported thing in this whole chapter.

The ladder adds fiber **slowly**, one rung every 3 days, so your gut can adjust. Fiber numbers are calculated from USDA FoodData Central (E52).

<div class="box stop" markdown="1">
<span class="label">Before you climb:</span> go up slowly and drink water, or you'll feel it (gas and bloating are common for the first days of each rung). **Ask your doctor first** if you've had a bowel blockage, have Crohn's disease or a narrowed bowel, have trouble swallowing, or have been told to eat low-fiber. **Not for the ladder, for your doctor, today:** blood in your stool, black stool, unexplained weight loss, severe belly pain, or a change in your bowel habits that lasts more than a few weeks.
</div>

| Rung | Days | Add this | Fiber added |
|---|---|---|---|
| 1 | 1–3 | **2 green kiwis a day** (the Kitchen yogurt bowl uses them). In a 4-week study of 75 people with chronic constipation, 2 kiwis a day worked about as well as prunes or psyllium, with the fewest side effects and less bloating (E25). | +{kiwi:.1f} g |
| 2 | 4–6 | **Swap 1 cup of white rice for brown rice** once a day. | +{brown-white:.1f} g |
| 3 | 7–9 | **1/2 cup shelled edamame** as a snack or in a bowl. | +{edam:.1f} g |
| 4 | 10–12 | **5 prunes** (about 50 g) + **1 Tbsp ground flaxseed** on yogurt or oatmeal. In the Prune Study, postmenopausal women eating 50 g of prunes a day kept their hip bone density steady over 12 months compared with controls (E27). | +{prune+flax:.1f} g |
| 5 | 13–15 | **Oatmeal breakfast**, 1/2 cup dry oats (the savory oatmeal counts). | +{oats:.1f} g |
| 6 | 16–21 | **A vegetable at every meal:** for example 1 cup broccoli at lunch, 1 cup cooked bok choy at dinner, a carrot as a snack. | +{broc+bokc+carrot:.1f} g |

**All six rungs add about {total:.0f} grams a day.** You probably don't need all six. Count one normal day of eating with the numbers on the recipes and the list below, then climb only as many rungs as it takes to reach the 25 to 29 gram zone.

**Where the fiber is (per portion, USDA E52):** 2 green kiwis {kiwi:.1f} g · 5 prunes {prune:.1f} g · 1/2 cup edamame {edam:.1f} g · 1/2 cup dry oats {oats:.1f} g · 1 cup cooked brown rice {brown:.1f} g (white rice {white:.1f} g) · 1 Tbsp ground flaxseed {flax:.1f} g · 1 cup broccoli {broc:.1f} g · 1 medium carrot {carrot:.1f} g.

**Walk after meals.** Light walking after eating, even 2 to 5 minutes, lowers the blood-sugar rise compared with sitting (E23). Chang calls it the digestion walk. He walks to the mailbox and back three times and calls it a lap.

<table class="write"><thead><tr><th>Rung</th><th>Start date</th><th>How I felt (gas, bloating, regular?)</th><th>Keep it? Y/N</th></tr></thead><tbody>
<tr><td>1</td><td></td><td></td><td></td></tr><tr><td>2</td><td></td><td></td><td></td></tr><tr><td>3</td><td></td><td></td><td></td></tr>
<tr><td>4</td><td></td><td></td><td></td></tr><tr><td>5</td><td></td><td></td><td></td></tr><tr><td>6</td><td></td><td></td><td></td></tr></tbody></table>
"""


# --------------------------------------------------------------- grocery lists
SHOP = {
    171287: ("Dairy & eggs", "Large eggs", "count", 50, "eggs"),
    170894: ("Dairy & eggs", "Plain nonfat Greek yogurt", "unit", 907, "tub (32 oz)"),
    175215: ("Dairy & eggs", "Unsweetened soy milk", "unit", 946, "quart"),
    172448: ("Tofu", "Firm tofu", "unit", 397, "block (14 oz)"),
    174290: ("Tofu", "Extra-firm tofu", "unit", 397, "block (14 oz)"),
    172449: ("Tofu", "Soft tofu", "unit", 397, "block (14 oz)"),
    171077: ("Meat & fish", "Boneless, skinless chicken breast", "lb", 454, ""),
    173627: ("Meat & fish", "Boneless, skinless chicken thighs", "lb", 454, ""),
    171505: ("Meat & fish", "Ground turkey", "lb", 454, ""),
    174055: ("Meat & fish", "Top sirloin", "lb", 454, ""),
    174051: ("Meat & fish", "Lean beef chuck or brisket", "lb", 454, ""),
    174030: ("Meat & fish", "90% lean ground beef", "lb", 454, ""),
    168230: ("Meat & fish", "Pork loin", "lb", 454, ""),
    168258: ("Meat & fish", "Lean pork shoulder", "lb", 454, ""),
    175167: ("Meat & fish", "Salmon fillets", "lb", 454, ""),
    175179: ("Meat & fish", "Raw shrimp, peeled (frozen is fine)", "lb", 454, ""),
    173709: ("Pantry", "Light tuna in water", "unit", 113, "can (5 oz)"),
    170005: ("Produce", "Scallions", "unit", 90, "bunch"),
    169231: ("Produce", "Fresh ginger", "oz", 28.35, ""),
    169230: ("Produce", "Garlic", "unit", 30, "head"),
    168462: ("Produce", "Spinach (baby or regular)", "oz", 28.35, ""),
    169957: ("Produce", "Mung bean sprouts", "unit", 340, "bag (12 oz)"),
    170393: ("Produce", "Carrots", "count", 61, "medium"),
    169291: ("Produce", "Zucchini", "count", 196, "medium"),
    170000: ("Produce", "Onions", "count", 130, "medium"),
    170027: ("Produce", "Russet potatoes", "count", 213, "medium"),
    169975: ("Produce", "Green cabbage", "unit", 900, "small head"),
    170390: ("Produce", "Bok choy or baby bok choy", "lb", 454, ""),
    170379: ("Produce", "Broccoli florets", "lb", 454, ""),
    169242: ("Produce", "Fresh shiitake mushrooms", "oz", 28.35, ""),
    169251: ("Produce", "White mushrooms", "unit", 227, "pack (8 oz)"),
    168409: ("Produce", "Cucumbers", "count", 200, "medium"),
    170457: ("Produce", "Tomatoes", "count", 123, "medium"),
    168153: ("Produce", "Green kiwis", "count", 75, ""),
    169247: ("Produce", "Green-leaf or romaine lettuce", "unit", 300, "head"),
    168177: ("Produce", "Asian pear (or Bosc pear)", "count", 240, "large"),
    169246: ("Produce", "Leek", "count", 89, ""),
    168451: ("Produce", "Daikon radish", "lb", 454, ""),
    168410: ("Frozen", "Shelled edamame", "unit", 340, "bag (12 oz)"),
    168411: ("Frozen", "Shelled edamame", "unit", 340, "bag (12 oz)"),
    170016: ("Frozen", "Peas", "unit", 454, "bag (16 oz)"),
    172688: ("Bread & grains", "Whole-wheat bread", "unit", 640, "loaf (about 20 slices)"),
    169704: ("Bread & grains", "Brown rice (dry)", "rice", 0, ""),
    168931: ("Bread & grains", "Short-grain white rice (dry)", "cup", 200, ""),
    168910: ("Bread & grains", "Whole-wheat spaghetti (dry)", "pasta", 0, ""),
    173904: ("Bread & grains", "Old-fashioned rolled oats", "cup", 80, ""),
    171609: ("Pantry", "Low-sodium chicken broth", "unit", 960, "carton (32 oz)"),
    170392: ("Pantry", "Kimchi", "unit", 454, "jar (16 oz)"),
    170187: ("Pantry", "Walnuts", "oz", 28.35, ""),
    169414: ("Pantry", "Ground flaxseed", "oz", 28.35, ""),
    168458: ("Pantry", "Roasted seaweed sheets", "count", 2.5, "sheets"),
    170496: ("Pantry", "Dried wakame seaweed", "wakame", 0, ""),
    168152: ("Pantry", "Dried jujubes (red dates)", "count", 4, ""),
}
PANTRY = ["low-sodium soy sauce", "toasted sesame oil", "canola oil", "toasted sesame seeds", "rice or white vinegar",
          "honey", "sugar", "salt", "cornstarch", "gochujang", "miso or doenjang", "Korean chili flakes or red pepper flakes",
          "tahini", "reduced-fat mayonnaise", "chunjang (black bean paste)", "white or black pepper"]

WEEKS = [
    dict(n=1, title="Easy start", note="Lots of 10-minute breakfasts and lunches while you get used to the rhythm.",
         menu=[("Mon", "B4", "L4", "D2"), ("Tue", "B3", "D2 (leftovers)", "S4"), ("Wed", "B4", "L4", "D3"),
               ("Thu", "B3", "D3 (leftovers)", "D5"), ("Fri", "B2", "L2", "S2"), ("Sat", "B4", "S2 (leftovers)", "D1"),
               ("Sun", "B5", "D1 (leftovers)", "S3")],
         cook={"B4": 6, "B3": 4, "B2": 1, "B5": 1, "L4": 4, "L2": 1, "D2": 1, "S4": 1, "D3": 1, "D5": 1, "S2": 1, "D1": 1, "S3": 1, "N1": 2, "N2": 1}),
    dict(n=2, title="Soup week", note="Big pots on Monday and Thursday feed you for two days each.",
         menu=[("Mon", "B1", "L5", "S1"), ("Tue", "B1 (leftovers)", "S1 (leftovers)", "D4"), ("Wed", "B4", "D4 (leftovers)", "D6"),
               ("Thu", "B3", "L3", "S5"), ("Fri", "B4", "S5 (leftovers)", "D2"), ("Sat", "B5", "D2 (leftovers)", "S4"),
               ("Sun", "B2", "L4", "D1 (freeze 2 portions)")],
         cook={"B1": 1, "L5": 1, "S1": 1, "D4": 1, "B4": 4, "D6": 1, "B3": 2, "L3": 1, "S5": 1, "D2": 1, "B5": 1, "S4": 1, "B2": 1, "L4": 2, "D1": 1, "N3": 2, "N2": 1}),
    dict(n=3, title="Fiber week", note="Leans on the higher-fiber recipes. Pair it with rungs 3 to 5 of the fiber ladder.",
         menu=[("Mon", "B3", "L1", "D3"), ("Tue", "B4", "L1 (leftovers)", "D6"), ("Wed", "B3", "D3 (leftovers)", "S2"),
               ("Thu", "B4", "S2 (leftovers)", "D2"), ("Fri", "B5", "D2 (leftovers)", "S3"), ("Sat", "B1", "L3", "D4"),
               ("Sun", "B1 (leftovers)", "D4 (leftovers)", "S4")],
         cook={"B3": 4, "L1": 1, "D3": 1, "B4": 4, "D6": 1, "S2": 1, "D2": 1, "B5": 1, "S3": 1, "B1": 1, "L3": 1, "D4": 1, "S4": 1, "N1": 2, "N3": 1}),
    dict(n=4, title="Chang's choice", note="Jajangmyeon on Monday because he asked nicely. Wraps for dinner on Thursday.",
         menu=[("Mon", "B2", "L2", "D1"), ("Tue", "B4", "D1 (leftovers)", "D5"), ("Wed", "B3", "L4", "S1"),
               ("Thu", "B5", "S1 (leftovers)", "L5"), ("Fri", "B4", "L3", "S5"), ("Sat", "B1", "S5 (leftovers)", "D6"),
               ("Sun", "B1 (leftovers)", "L4", "D2 (freeze 2 portions)")],
         cook={"B2": 1, "L2": 1, "D1": 1, "B4": 4, "D5": 1, "B3": 2, "L4": 4, "S1": 1, "B5": 1, "L5": 1, "L3": 1, "S5": 1, "B1": 1, "D6": 1, "D2": 1, "N2": 1, "N1": 1}),
]


def fmt_qty(src, g):
    sec, name, mode, unit_g, unit_lbl = SHOP[src]
    if mode == "count":
        n = math.ceil(g / unit_g - 0.05)
        if unit_lbl == "eggs" and n >= 12:
            return f"{n} eggs ({n // 12} dozen" + (f" + {n % 12}" if n % 12 else "") + ")"
        return f"{n} {unit_lbl}".strip()
    if mode == "unit":
        n = max(1, math.ceil(g / unit_g - 0.05))
        if n > 1:
            if unit_lbl.endswith("bunch"):
                unit_lbl += "es"
            elif unit_lbl.startswith("loaf"):
                unit_lbl = unit_lbl.replace("loaf", "loaves", 1)
            elif "(" in unit_lbl:
                a, b = unit_lbl.split(" (", 1)
                unit_lbl = a + "s (" + b
            else:
                unit_lbl += "s"
        return f"{n} {unit_lbl}"
    if mode == "lb":
        lb = g / 454
        q = math.ceil(lb * 4 - 0.05) / 4
        return f"{q:g} lb"
    if mode == "oz":
        return f"{math.ceil(g / 28.35):d} oz"
    if mode == "cup":
        return f"{math.ceil(g / unit_g * 4 - 0.05) / 4:g} cups"
    if mode == "rice":
        cooked = g / 195
        dry = math.ceil(cooked / 3 * 4) / 4
        return f"{dry:g} cups dry (makes about {cooked:.0f} cups cooked)"
    if mode == "pasta":
        oz = g / 70
        return f"{math.ceil(oz):d} oz dry"
    if mode == "wakame":
        return f"{g/10/28.35:.1f} oz dried"
    return f"{g:.0f} g"


def grocery_md(w):
    need = {}
    for rid, mult in w["cook"].items():
        r = BYID[rid]
        for amt, txt, g, src in r["ings"]:
            if src in SHOP:
                key = SHOP[src][1]
                need.setdefault(key, [src, 0.0])
                need[key][1] += g * mult
    by = {}
    for key, (src, g) in need.items():
        by.setdefault(SHOP[src][0], []).append((key, fmt_qty(src, g)))
    lines = [f"## Week {w['n']}: {w['title']}\n", f"{w['note']} Cooking for two; recipes marked leftovers are made the day before.\n",
             "| Day | Breakfast | Lunch | Dinner |", "|---|---|---|---|"]

    def nm(code):
        base = code.split(" ")[0]
        rest = code[len(base):]
        return f"{BYID[base]['name']}{rest}"
    for d, b, l, dn in w["menu"]:
        lines.append(f"| {d} | {nm(b)} | {nm(l)} | {nm(dn)} |")
    snacks = [k for k in w["cook"] if k.startswith("N")]
    lines.append(f"\n**Snacks this week:** {', '.join(BYID[s]['name'] for s in snacks)}.\n")
    lines.append(f"### Shopping list, week {w['n']}\n")
    order = ["Produce", "Meat & fish", "Tofu", "Dairy & eggs", "Frozen", "Bread & grains", "Pantry"]
    lines.append('<div class="twocol" markdown="1">\n')
    for sec in order:
        if sec in by:
            lines.append(f"**{sec}**\n")
            for key, q in sorted(by[sec]):
                lines.append(f"- ☐ {key}: {q}")
            lines.append("")
    lines.append("</div>\n")
    lines.append(f"**Check you have:** {', '.join(PANTRY)}.\n")
    return "\n".join(lines)


def groceries_md():
    out = ["# Four weeks of menus and grocery lists\n",
           say("sun", "Plan on Sunday, shop once, cook big twice. People who plan eat better and waste less. Also they don't call me at six o'clock asking what to make."),
           "Each week feeds two people: breakfast, lunch, dinner and snacks. Quantities are added up from the recipes and rounded **up** to what you'd actually buy. Cooking for one? Buy half, and freeze the second half of each soup and braise in single portions.\n"]
    for w in WEEKS:
        out.append(grocery_md(w))
    return "\n".join(out)


# --------------------------------------------------------------- remedies
REMEDIES = [
    ("Good evidence", [
        dict(name="Honey for a cough with a cold", ev="E32",
             study="Across studies of upper-respiratory infections, honey eased symptoms, especially how often and how badly people coughed, compared with usual care (E32).",
             how="1 to 2 teaspoons of honey stirred into warm (not boiling) water or ginger tea, or straight off the spoon, up to a few times a day while you have the cough.",
             skip="Never give honey to babies under 1 year. Diabetes: honey counts as sugar. A cough with fever over a few days, shortness of breath, chest pain or blood: not for honey, for your doctor.",
             sun="In the studies it beat usual care for a cough with a cold. It costs less than most of the cough aisle. Tastier, too."),
        dict(name="Two green kiwis a day for constipation", ev="E25",
             study="In a 4-week study of 75 people with chronic constipation, 2 green kiwis a day improved bowel movements about as much as 100 g of prunes or 12 g of psyllium, with the fewest side effects, the highest satisfaction and less bloating (E25). An exploratory study: good, not huge.",
             how="Two green kiwis a day, peeled, or scoop them with a spoon. Breakfast is easiest (Morning yogurt bowl).",
             skip="Kiwi allergy (more common in people with latex allergy). Go up slowly and drink water. Blood in the stool, black stool, weight loss you can't explain, or a big change in your bowel habits: doctor, not kiwi.",
             sun="Put the onion in the soup. Put the kiwi in your mouth."),
        dict(name="The after-dinner walk", ev="E23",
             study="Light walking after meals, even 2 to 5 minutes, lowers the rise in blood sugar after eating compared with sitting (E23).",
             how="Walk 5 to 15 minutes after your biggest meal. Inside counts: kitchen to front door and back, along the counter.",
             skip="If you have diabetes, keep taking your medicines exactly as prescribed; this is on top, not instead. Chest pain or unusual breathlessness when you walk: stop and call your doctor.",
             sun="Not a remedy. A walk. That's why it works."),
        dict(name="Fiber, 25 to 29 grams a day", ev="E24",
             study="In a large Lancet review, people eating 25 to 29 g of fiber a day had 15 to 30% lower rates of death and heart disease and lower rates of type 2 diabetes and colorectal cancer than people eating the least (E24). These are links from long-term studies.",
             how="Climb the fiber ladder: kiwi, brown rice, edamame, prunes and flax, oats, vegetables at every meal.",
             skip="Go up slowly with water. Ask your doctor first if you've had a bowel blockage, have Crohn's disease or a narrowed bowel, trouble swallowing, or were told to eat low-fiber.",
             sun="Boring. Works. Most things that work are boring."),
        dict(name="Salt substitute (potassium salt)", ev="E35",
             study="In a trial of 20,995 older adults at high risk, those using a salt substitute that was 25% potassium chloride had fewer strokes, fewer major heart events and fewer deaths than those using regular salt (E35).",
             how="Only with your doctor's okay: use the salt substitute in place of regular salt at the table and in cooking.",
             skip="**Kidney disease, or on blood-pressure pills like ACE inhibitors, or any medicine that raises potassium? Ask your doctor first. This one is not optional.** Too much potassium can be dangerous for those people.",
             sun="Good evidence. Also the one on this page most likely to hurt the wrong person. Ask first."),
    ]),
    ("Some evidence", [
        dict(name="Kimchi and other fermented foods", ev="E26",
             study="In a 10-week study of 36 adults, a diet high in fermented foods (yogurt, kefir, kimchi, sauerkraut, kombucha; about 6 servings a day by the end) increased gut-microbe diversity and lowered 19 inflammation-related proteins in the blood (E26). Small and short: interesting, not proven for health outcomes.",
             how="A small side of kimchi with meals, plain yogurt with breakfast. You don't need six servings to enjoy it.",
             skip="Kimchi is salty: watching sodium, small portions or rinse it. Very spicy kimchi can bother reflux. Weakened immune system (for example during chemotherapy): ask your care team which fermented foods are okay for you.",
             sun="My mother would say it was obvious. Science took until 2021. Fine. Welcome."),
        dict(name="Ginger for nausea", ev="E33",
             study="Ginger for nausea has reasonable support in research reviews. For knee osteoarthritis pain, ginger had only a small effect compared with placebo, with more stomach complaints (E33). So: may help a little.",
             how="Ginger tea: 5 or 6 thin slices of fresh ginger simmered in 2 cups of water for 10 minutes. Add honey if you like.",
             skip="Food amounts of ginger are fine for most people. Ginger **supplements** (capsules, extracts): on blood thinners? Ask your doctor first. Nausea that won't stop, vomiting blood, or black stool: doctor, today.",
             sun="Good in tea. Better in bulgogi."),
        dict(name="Gargling plain water in cold season", ev="E56",
             study="In one Japanese trial of 387 healthy adults aged 18 to 65, gargling plain water daily for 60 days was linked with 36% fewer upper-respiratory infections than usual care. There was no fake-gargle comparison, and nobody over 65 was studied (E56).",
             how="A few gargles of plain tap water, after you come home, in cold season.",
             skip="If you have trouble swallowing or choke easily, skip it. Salt-water gargles for a sore throat are fine for comfort; don't swallow them if you watch your sodium.",
             sun="One study. Young people. Cheap. Harmless. I do it. I don't brag about it."),
    ]),
    ("Tradition only: enjoy it as food", [
        dict(name="Chicken and ginger soup for a cold", ev="E57",
             study="Chicken soup slowed white blood cells in a lab dish. The researchers themselves said whether it helps people is 'untested' (E57). What's true: when you're sick, warm fluids, salt and protein you can actually swallow help you keep eating and drinking.",
             how="Chicken, ginger and jujube soup, or the rice porridge.",
             skip="Watch sodium if you're on a salt limit (make it with low-sodium broth). Fever that lasts, shortness of breath, confusion: doctor.",
             sun="It won't fix your cold. It will make you feel looked after. That's not nothing."),
        dict(name="Barley tea (boricha)", ev=None,
             study="No good research on health effects. It's a warm, caffeine-free drink many Korean families drink instead of water.",
             how="1 Tbsp roasted barley (or a barley tea bag) in 4 cups water, simmer 5 minutes. Hot or cold.",
             skip="Celiac disease or gluten sensitivity: barley has gluten, skip it.",
             sun="It's water that tastes like toast. Drink more water. That's the whole trick."),
        dict(name="Jujube (red date) tea", ev=None,
             study="No trustworthy human research for the claims you'll read online. Dried jujubes are a sweet fruit.",
             how="6 dried jujubes, sliced, plus 3 slices of ginger, simmered in 4 cups water for 20 minutes.",
             skip="Dried fruit is sugar: diabetes, count it. Watch for the pits if you have dentures.",
             sun="Sweet, warm, lovely at night. Enjoy it. Don't expect it to do your homework."),
        dict(name="Seaweed soup (miyeok-guk)", ev="E58",
             study="Eaten for birthdays and after childbirth in Korea. No good research on it as a remedy. Seaweed does contain a lot of iodine, and the amount varies hugely: commercially sold seaweeds measured 16 to 2,984 micrograms of iodine per gram (E58).",
             how="The seaweed soup recipe in this book.",
             skip="Thyroid condition (especially autoimmune thyroid disease)? Ask your doctor how much seaweed is okay (E58).",
             sun="I eat it on birthdays. That's the tradition. The birthday is the medicine."),
        dict(name="Rice porridge (jook) for an upset stomach", ev=None,
             study="No trials. It's easy to swallow, easy to digest, and gets fluid and some protein in when nothing else sounds good.",
             how="The chicken and ginger rice porridge, made thinner with extra broth.",
             skip="Vomiting that won't stop, signs of dehydration (very little urine, dizziness), blood, or severe belly pain: doctor, today.",
             sun="What mothers feed children when they're sick. Also what children should feed mothers."),
        dict(name="Peppermint tea for the stomach", ev="E34",
             study="The research is for enteric-coated peppermint oil capsules, which improved IBS symptoms and belly pain compared with placebo (E34). That's a pharmacy product, not tea. For the tea itself: tradition.",
             how="A mug after dinner if you like it.",
             skip="Peppermint can make reflux and heartburn worse. Thinking about the capsules? That's a supplement: ask your doctor or pharmacist, especially if you take prescriptions.",
             sun="Nice tea. Not the same as the study. Know the difference."),
    ]),
]

MYTHS = [
    ("Onion in a glass of water, or onion slices in your socks", "No evidence of any benefit to your body (EVIDENCE.md, deliberately-not-claimed list). Put the onion in the soup."),
    ("Detox teas and 'cleanses'", "No competent evidence that detox products do anything. Your liver and kidneys already do this job, every day, for free."),
    ("A drink that 'burns sugar' after dinner", "No drink has that evidence. The after-dinner walk does (E23)."),
    ("Anything that 'lowers blood pressure instantly'", "Slow breathing can lower blood pressure for a short time (E19). Resting blood pressure comes down over weeks of training, like wall sits and strength work (E20), plus food and the medicines your doctor manages. Never stop or change blood-pressure medicine on your own."),
    ("Salt or bay leaves under your feet, cabbage leaves for any pain", "No evidence. For back pain, the thing with the evidence is exercise: 249 trials (E30)."),
]


def remedies_md():
    out = ["# Remedies, graded honestly\n",
           say("sun", "Everybody's grandmother had remedies. Mine too. Some of them work. Some of them are just love in a pot. Both are fine, as long as nobody lies to you about which is which. So here's which is which."),
           "Three grades. **Good evidence:** solid trials or big reviews. **Some evidence:** small or early studies, or studies in different people than you. **Tradition only, enjoy it as food:** no good research, but it's food, and food is allowed to just be food.\n",
           box("stop", "None of these take the place of your medicine or your doctor.", "Never stop, start or change a medicine because of a food. If you take prescriptions, ask your pharmacist before adding anything new, especially supplements. Chest pain, trouble breathing, fainting, blood in your stool or vomit, confusion: that's not for soup. Call your doctor today, or 911.")]
    for grade, items in REMEDIES:
        out.append(f"## {grade}\n")
        for it in items:
            out.append(f'<div class="keep" markdown="1">\n\n### {it["name"]}\n\n<p class="dose">{grade}</p>\n\n'
                       f"**What the research says:** {it['study']}\n\n**How Sun makes it:** {it['how']}\n\n"
                       f"**Who should skip or ask first:** {it['skip']}\n\n</div>\n")
            out.append(say("sun", it["sun"]))
    out.append("## Don't bother\n")
    out.append("The internet loves these. The evidence doesn't. Each one is marked **Myth** so nobody screenshots it the wrong way.\n")
    out.append("| Myth | What's actually true |")
    out.append("|---|---|")
    for m, t in MYTHS:
        out.append(f"| ✗ **Myth:** {m} | {t} |")
    out.append("")
    return "\n".join(out)


# --------------------------------------------------------------- method appendix
def method_md():
    out = ["# How we calculated the numbers\n",
           "**Source.** Every ingredient is matched to a food in the USDA FoodData Central SR Legacy database (April 2018 release, downloaded from fdc.nal.usda.gov, E52). We took energy (kcal), protein, total dietary fiber and sodium per 100 grams, multiplied by the grams used, added up the recipe and divided by the number of servings.\n",
           "**Two pastes aren't in the USDA database:** gochujang and chunjang. For those we used the manufacturer label values recorded on Open Food Facts (Sempio gochujang, Obok chunjang, E53). The chunjang label's protein (20 g per 100 g) looks high for a bean paste, so treat the protein in Chang's black bean noodles as a slight overestimate (the paste adds about 3.6 g per serving).\n",
           "**Rules we followed.**\n",
           "- Meat, fish and tofu are weighed **raw**, matched to raw USDA values. Rice and pasta are weighed **cooked**, matched to cooked values (1 cup cooked brown rice = 195 g; 1 cup cooked whole-wheat pasta = 140 g).\n"
           "- Salt, soy sauce and pastes are counted in full at the amounts listed. \"Pinch\" and \"to taste\" items, and water, count as zero.\n"
           "- Dried wakame is calculated as its soaked weight (1/2 oz dry ≈ 140 g soaked) using USDA raw wakame.\n"
           "- Where USDA reports no value for a nutrient (fiber in raw shrimp and short-grain white rice), we counted zero. Shrimp has essentially no fiber; white rice has a little, so those fiber numbers are slightly low.\n"
           "- Soy-braised eggs: all the soy sauce is counted even though most stays in the pot, so sodium is overstated.\n"
           "- Brand, ripeness and exact size change real numbers. Treat these as good estimates, within about 10%.\n",
           "Numbers are rounded: protein to the nearest gram, fiber to 0.1 g, calories and sodium to the nearest 10.\n",
           "## Ingredient-by-ingredient tables\n",
           "Totals are for the whole recipe; the recipe page shows per serving (total ÷ servings).\n"]
    for r in R:
        per, tot, rows = NUT[r["id"]]
        t = [f'<div class="keep" markdown="1">\n\n### {r["name"]} (serves {r["serves"]})\n',
             '<table class="small"><thead><tr><th>Ingredient</th><th>Grams</th><th>Source ID</th><th>Protein g</th><th>Fiber g</th><th>kcal</th><th>Sodium mg</th></tr></thead><tbody>']
        for x in rows:
            if x["src"] is None:
                sid = "not counted"
            elif isinstance(x["src"], str):
                sid = "label (E53)"
            else:
                sid = f"FDC {x['src']}"
            v = x["v"]
            nm = x["txt"].split(",")[0].split("(")[0].strip()
            t.append(f"<tr><td>{nm}</td><td>{x['g']:g}</td><td>{sid}</td><td>{v['protein_g']:.1f}</td><td>{v['fiber_g']:.1f}</td><td>{v['kcal']:.0f}</td><td>{v['sodium_mg']:.0f}</td></tr>")
        t.append(f"<tr><td><strong>Total</strong></td><td></td><td></td><td><strong>{tot['protein_g']:.1f}</strong></td><td><strong>{tot['fiber_g']:.1f}</strong></td><td><strong>{tot['kcal']:.0f}</strong></td><td><strong>{tot['sodium_mg']:.0f}</strong></td></tr>")
        t.append(f"<tr><td><strong>Per serving</strong></td><td></td><td></td><td><strong>{per['protein_g']:.1f}</strong></td><td><strong>{per['fiber_g']:.1f}</strong></td><td><strong>{per['kcal']:.0f}</strong></td><td><strong>{per['sodium_mg']:.0f}</strong></td></tr>")
        t.append("</tbody></table>\n\n</div>\n")
        out.append("\n".join(t))
    return "\n".join(out)


INTRO_SAY = say("sun", "I'm Sun Yoon. I'm 76, I'm his wife, and I'm an AI character. A team of people made me. My lunch counter, my mother's market stall, fifty years with that man: that's a story. The recipes are real food, tested the way home cooks test things, and the numbers come from the USDA, not from my feelings.\n\nThis book has three jobs. Get enough protein into you, because muscle needs it and most people over 65 don't eat enough at breakfast. Get enough fiber into you, slowly. And tell you the truth about kitchen remedies, because the internet won't.\n\nCheap food. Lots of protein. No nonsense. Now go eat.")


def intro_md():
    idx = []
    for cat, label in [("Breakfast", "Breakfast"), ("Lunch", "Lunch"), ("Dinner", "Dinner"), ("Soup", "Soups"), ("Snack", "Snacks")]:
        items = [r for r in R if r["cat"] == cat]
        idx.append(f"| **{label}** | | | |")
        for r in items:
            p, f, k, na = per_str(r["id"])
            idx.append(f"| {r['name']} | {p} g | {f} g | {k} |")
    return f"""
# Start here {{: .nobreak}}

{INTRO_SAY}

## What's inside

- **24 recipes:** Korean, Korean-Chinese and Chinese home food, made with things you can buy at a regular US supermarket (plus a few jars from an Asian grocery or online: gochujang, kimchi, chunjang). Every recipe lists protein, fiber, calories and sodium per serving, a soft-food version, how long it keeps, and who should skip or ask first.
- **The protein guide:** your daily number and what 25 to 30 grams per meal looks like.
- **The fiber ladder:** six rungs, three days each.
- **Four weeks of menus and grocery lists** for two people.
- **Remedies, graded honestly:** good evidence, some evidence, or tradition only.
- **The method:** every ingredient's USDA value, so you can check my math. I'd check it.

## Every recipe at a glance (per serving)

| Recipe | Protein | Fiber | Calories |
|---|---|---|---|
""" + "\n".join(idx) + f"""

## Kitchen safety for older cooks

Adults over 65 are at higher risk of food poisoning: the immune system is slower, food stays in the gut longer, and the stomach makes less acid (E55). So in this kitchen:

- **Eggs are always cooked until the yolk and white are firm.** No runny yolks, no raw-egg drinks, no raw sprouts (E54, E55).
- **Use a thermometer.** Poultry 165°F. Ground meat 160°F. Beef and pork steaks, chops and roasts 145°F, then rest 3 minutes. Fish 145°F or until it flakes and is opaque. Shrimp until pink and opaque. Leftovers reheated to 165°F (E54).
- **Two-hour rule:** cooked food goes in the fridge within 2 hours.
- **Knife toward the board, never toward your hand.** Sit on a stool to chop if standing tires you.
- **Allergies:** these recipes use soy, wheat (soy sauce contains wheat; use tamari if you avoid gluten), sesame, eggs, fish, shellfish, peanuts in one swap, and walnuts. Swaps are given where they're easy.

<div class="box note" markdown="1">
<span class="label">If you take medicines:</span> food doesn't replace them, and nothing in this book asks you to change them. Warfarin users: keep leafy greens steady rather than starting or stopping them suddenly. Kidney disease: ask your doctor for your protein and potassium limits. Salt-restricted: every recipe shows sodium, and the salty ones say so.
</div>
"""


def build():
    parts = [intro_md(), protein_md(), fiber_md()]
    for cat, label in [("Breakfast", "Breakfast"), ("Lunch", "Lunch"), ("Dinner", "Dinner"), ("Soup", "Soups"), ("Snack", "Snacks")]:
        parts.append(f"# {label}\n")
        first = True
        for r in [r for r in R if r["cat"] == cat]:
            md = recipe_md(r)
            if first:
                md = md.replace('<div class="recipe" markdown="1">', '<div class="recipe first" markdown="1">', 1)
                first = False
            parts.append(md)
    parts += [groceries_md(), remedies_md(), method_md()]
    ids = ["E19", "E20", "E23", "E24", "E25", "E26", "E27", "E28", "E30", "E32", "E33", "E34", "E35", "E52", "E53", "E54", "E55", "E56", "E57", "E58"]
    parts.append(appendix_md(ids))
    md = "\n\n".join(parts)
    css = """
.recipe { page-break-before: always; }
.recipe.first { page-break-before: avoid; }
table.nut { width: 100%; border-collapse: separate; border-spacing: 6pt 0; margin: 4pt -6pt 2pt -6pt; }
.twocol ul { list-style: none; padding-left: 0; }
table.nut td { background: #FFFFFF; border: 2pt solid #1F5A46; border-radius: 8pt; text-align: center; padding: 6pt 4pt; font-size: 14pt; width: 25%; }
table.nut .n { font-family: 'Fraunces'; font-weight: 700; font-size: 20pt; color: #B3311C; }
"""
    cover = cover_html("Sun Yoon's", "Strong Kitchen", "24 Korean and Chinese home recipes with the protein counted.<br>A fiber ladder, four weeks of grocery lists, and kitchen remedies graded honestly.",
                       "With Chang Yin, who eats most of it.", DISCLOSURE.replace("exercises and recipes", "recipes"))
    out_pdf = os.path.join(PRODUCTS, "strong_kitchen.pdf")
    out_md = os.path.join(PRODUCTS, "strong_kitchen.md")
    hdr = f"<!-- Source for {NAME}. Generated by products/_build/build_kitchen.py from recipes.py + USDA FDC SR Legacy (E52). Edit recipes.py, then re-run. -->"
    render(md, out_pdf, NAME, cover=cover, out_md=out_md, md_header=hdr, extra_css=css)
    # machine-readable nutrition for the app
    data = []
    for r in R:
        per, tot, rows = NUT[r["id"]]
        data.append(dict(id=r["id"], name=r["name"], native=r["native"], category=r["cat"], serves=r["serves"],
                         minutes_active=r["active"], minutes_total=r["total"],
                         per_serving={k: round(v, 1) for k, v in per.items()},
                         ingredients=[dict(amount=a, item=t, grams=g, source=(f"FDC {s}" if isinstance(s, int) else s)) for a, t, g, s in r["ings"]],
                         steps=r["steps"], soft_food=r["soft"], storage=r["store"], cautions=cautions(r)))
    json.dump(data, open(os.path.join(PRODUCTS, "kitchen_recipes.json"), "w"), indent=1, ensure_ascii=False)
    return out_pdf


if __name__ == "__main__":
    print(build())
