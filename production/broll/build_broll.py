"""60 no-face B-roll prompts (no people, faces or hands) per set code -> broll_prompts.json."""
import json
from pathlib import Path

STYLE = ("Photorealistic, shot on iPhone at eye level, natural light, handheld micro-shake, 9:16 vertical, 24-30 fps, "
         "documentary realism. No people, no faces, no hands, no text, no logos, no readable labels.")
NEG = ("people, person, face, faces, hands, fingers, body parts, text, letters, words, logos, readable labels, watermark, "
       "floating objects, liquid changing colour, cartoon, CGI look, oversaturated")
SHOTS = {
    "SET-GARAGE": ["Wooden chair pushed against a garage wall, morning sidelight through the open door, dust in the air",
                   "Three kettlebells (8, 12, 20 kg, unmarked) lined up on a rubber mat, slow push-in",
                   "Resistance bands hanging on a pegboard, gentle sway",
                   "Clipboard log on a nail, pencil on a string, light moving across it",
                   "Convex safety mirror in a garage corner reflecting the empty room",
                   "Squat rack with an unloaded barbell, slow pan left to right",
                   "Chalk bowl on a stool, a puff of chalk dust settling",
                   "Garage door rising, morning light flooding the concrete floor",
                   "Empty sturdy chair and a kitchen-height counter, locked-off wide",
                   "Water bottle and a folded towel on a workbench, morning light",
                   "Floor-level slider past a rubber mat and the chair legs",
                   "Wall clock with no readable numbers, soft-focus garage behind"],
    "SET-KITCHEN": ["Onggi crocks on a sunny windowsill, slow push-in",
                    "Gas stove flame igniting under a pot, blue flame close-up",
                    "Soup simmering in a pot, steam rising in window light",
                    "Digital kitchen scale with a block of tofu, display out of focus",
                    "Chopping board with sliced scallions and garlic, overhead locked-off",
                    "Rice cooker steam vent puffing, kitchen in soft focus",
                    "Kimchi in a glass jar on the counter, top-down slow rotate",
                    "Fridge whiteboard with marker scribbles out of focus, slow rack focus to a jar of chopsticks",
                    "Bowls of banchan arranged on a wooden tray, overhead",
                    "Ladle lifting soup from a pot, steam, shallow depth of field",
                    "Barley tea poured into a cup from a kettle on a stand, light through the glass",
                    "Grocery bag on the counter: cabbage, eggs, tofu, beans (no labels readable)",
                    "Kettle starting to steam on the stove",
                    "Clean dish rack with two bowls drying, afternoon light"],
    "SET-YARD": ["Wooden fence rail in morning light, dew on the wood",
                 "Persimmon tree branches with ripe fruit swaying",
                 "Clothesline with a laundry basket below, breeze",
                 "Garden path pavers, slow dolly forward",
                 "Bench beside the fence, golden hour",
                 "Bird feeder swaying, soft background",
                 "Watering can beside raised vegetable beds, morning light",
                 "Wind chime moving on the porch eave, garden behind"],
    "SET-PROM": ["Foggy waterfront promenade at 7 am, steel railing leading into fog",
                 "Empty promenade bench, gulls in the distance",
                 "Footpath with morning puddles reflecting the sky",
                 "Steel railing close-up with fog droplets",
                 "Sunrise breaking through fog over calm water, locked-off wide"],
    "SET-LIVING": ["Sofa with a knitted throw and a reading lamp switching on",
                   "Floor mat unrolled in a living room, afternoon light",
                   "Bookshelf with plants, slow pan, spines unreadable",
                   "Window with sheer curtains moving in a breeze",
                   "Armchair and a side table with reading glasses folded"],
    "SET-BED": ["Bedside lamp with warm light, folded pajamas on the bed",
                "Made bed with a plumped pillow, still life, slow push-in",
                "Night window with soft city lights bokeh"],
    "SET-TABLE": ["Study card face-down on a wooden table beside barley tea",
                  "Fruit bowl with apples and persimmons, late-morning light",
                  "Notebook and pencil on a table, slow rack focus",
                  "Two cups of tea steaming on a table, top-down"],
    "SET-STOOP": ["Five-step stoop with a handrail, morning sun",
                  "Bottom stair close-up, worn edge, slow tilt up the handrail",
                  "Front door with a welcome mat, afternoon light"],
    "SET-MARKET": ["Produce aisle of an Asian supermarket: napa cabbage stack, labels out of focus",
                   "Bins of mushrooms and greens, slow dolly",
                   "Tofu packages in a chilled case, labels unreadable",
                   "Farmers-market stall with persimmons and pears under an awning"],
    "SET-BATH": ["Grab bar beside a bathroom sink, morning light",
                 "Bath mat and slip-resistant shoes beside the tub"],
}

if __name__ == "__main__":
    items = []
    for setc, lst in SHOTS.items():
        for s in lst:
            n = len(items) + 1
            items.append({"id": f"BR{n:02d}", "set_code": setc, "prompt": f"{s}. {STYLE}", "negative_prompt": NEG,
                          "duration_s": 4 if n % 3 == 0 else 6,
                          "pipeline": "Nano Banana 2 keyframe (set plate as reference) -> Veo 3.1 image-to-video, audio off",
                          "ai_label": "AI-generated: C2PA-signed and platform AI label when published"})
    assert len(items) == 60, len(items)
    Path(__file__).with_name("broll_prompts.json").write_text(json.dumps(
        {"version": "2026-10-01", "rule": "No-face B-roll only (no people, faces or hands): no likeness, no identity lock; "
         "still AI-labelled and C2PA-signed when used.", "count": 60, "items": items}, indent=2, ensure_ascii=False) + "\n")
    print(len(items))
