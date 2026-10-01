"""Daily Practice Sessions 15–30 (weeks 3–5). Same rotation and schema as sessions_spec.py.
Segments with an empty vo list get Chang's lines from the exercise library (support cue, first step, two cues, breathing cue)."""
from sessions_spec import session, seg, same, SESSIONS


def T(r, s, st, i):
    return dict(rebuild=r, steady=s, strong=st, iron=i)


def march(secs=40):
    return seg("Warm-up march", "warmup", secs, T(("seated_march", "main", f"{secs} seconds"), ("standing_march", "main", f"{secs} seconds"),
                                                  ("standing_march", "harder", f"{secs} seconds"), ("standing_march", "harder", f"{secs} seconds")),
               vo=["Ankle pumps first if you've been sitting. Stand slowly. Hand on the counter.", "March. Easy rhythm. Breathe steady."])


def easy_stands():
    return seg("Easy sit-to-stands", "warmup", 30, same("sit_to_stand", "3 easy reps", "5 easy reps", "5 easy reps", "5 easy reps", ("easier", "main", "main", "main")),
               vo=["Chair against the wall. Five easy ones.", "Breathe out as you stand."])


def sigh_cool(secs=40):
    return seg("Cool-down breathing", "cooldown", secs, same("cyclic_sigh", f"{secs} seconds", f"{secs} seconds", f"{secs} seconds", f"{secs} seconds", ("main",) * 4),
               vo=["Sit down. Two sniffs in through the nose. One long sigh out.", "No holding."])


def intro(day, kind, lines, extra_ost=()):
    return seg("Welcome", "intro", 35, vo=lines, ost=[f"Day {day} · {kind}", "Stop if chest pain, dizziness or sharp pain"] + list(extra_ost))


# ------------------------------------------------------------------ WEEK 3
session(n=15, weekday="Monday", type="Strength", title="Floor-ready legs", set="SET-GARAGE", wardrobe="C-TRAIN-A",
        swaps=dict(sore_knee="Skip the floor practice; sit-to-stands from a higher seat.", sore_back="Seated hinge instead of the suitcase lift.",
                   low_energy="One set each, skip the floor practice."),
        segments=[
    intro(15, "Strength", ["Week three. Monday. New move today: the floor.", "Getting down and up is a skill. Practise it before you ever need it.",
                           "Someone else home for that part. Sturdy chair next to you. Towel for your knee.", "Chest pain, dizziness, sharp pain: stop and sit."]),
    march(), easy_stands(),
    seg("Legs", "block", 120, T(("sit_to_stand", "easier", "3 sets of 6, hands on thighs"), ("sit_to_stand", "main", "3 sets of 10"),
                                ("sit_to_stand", "harder", "3 sets of 10, jug at chest"), ("split_squat", "main", "3 sets of 10 each leg (advanced)")),
        vo=["Chair against the wall. Three sets.", "Nose over toes. Push the floor away. Sit down slow.", "Breathe out as you stand."]),
    seg("Suitcase lift", "block", 80, T(("seated_hinge", "main", "2 sets of 8"), ("suitcase_lift", "main", "2 sets of 8 each side, half-gallon jug"),
                                        ("suitcase_lift", "main", "3 sets of 8 each side, gallon jug"), ("suitcase_lift", "harder", "3 sets of 10 each side, heavy bag from the step"))),
    seg("Push", "block", 80, T(("seated_chest_press", "main", "2 sets of 10"), ("wall_pushup", "harder", "2 sets of 10, feet back"),
                               ("counter_pushup", "main", "3 sets of 8"), ("counter_pushup", "harder", "3 sets of 12, 3-second lower"))),
    seg("Band row", "block", 70, T(("towel_row", "main", "4 pulls, 3-second squeeze"), ("band_row", "main", "2 sets of 10"),
                                   ("band_row", "main", "3 sets of 10"), ("band_row", "harder", "3 sets of 12, 2-second pause"))),
    seg("Floor practice", "block", 90, T(("sit_to_stand", "easier", "1 set of 5 (no floor today)"), ("floor_practice", "easier", "2 half-kneels each side, holding the chair"),
                                         ("floor_practice", "main", "2 kneel-and-rise, holding the chair"), ("floor_practice", "harder", "2 sit-to-floor and rise, someone home")),
        vo=["Chair or sofa right beside you. Towel down. Someone else is home.", "Step back. Lower one knee to the towel. Hands on the chair.",
            "Front foot flat. Push through it and your hands. Stand. Stand still a moment.", "Breathe out as you push up. Earn the floor.",
            "New knee, severe knee pain, or dizziness: skip the floor. Chair stands instead."],
        ost=["Only with a sturdy chair and someone home"]),
    seg("Heel raises", "block", 45, T(("heel_raise", "easier", "2 sets of 12, seated"), ("heel_raise", "main", "2 sets of 12"),
                                      ("heel_raise", "harder", "2 sets of 12, one hand"), ("heel_raise", "harder", "2 sets of 10 each leg"))),
    seg("Calf stretch", "cooldown", 45, same("calf_stretch", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    sigh_cool(35),
    seg("Close", "close", 25, vo=["You practised the floor. That's the one people skip.", "Earn the floor. Same time tomorrow."]),
])

session(n=16, weekday="Tuesday", type="Mobility", title="Back and hips, gently", set="SET-LIVING", wardrobe="C-CASUAL",
        swaps=dict(sore_knee="Skip the figure-4 and hip-front stretch.", sore_back="Chest lift, wall slides, breathing only.", low_energy="Seated moves only."),
        segments=[
    intro(16, "Mobility", ["Tuesday. Mobility. The back and the hips.", "Move with less stiffness. That's the goal. Nothing forced.", "Sharp pain or dizziness? Stop."]),
    seg("Ankle pumps", "warmup", 30, same("ankle_pumps", "10 pumps", "10 pumps + circles", "10 pumps + circles", "10 pumps + circles", ("main",) * 4)),
    seg("Chest lift", "block", 40, same("chest_lift", "6 lifts", "8 lifts", "8 lifts, 3-second hold", "10 lifts, 3-second hold", ("easier", "main", "harder", "harder"))),
    seg("Seated hinge", "block", 50, same("seated_hinge", "6 small hinges", "8 hinges", "8 hinges, bottle at chest", "10 hinges, bottle at chest", ("easier", "main", "harder", "harder"))),
    seg("Gentle seated turn", "block", 50, same("seated_rotation", "4 each side", "6 each side", "6 each side", "8 each side", ("easier", "main", "main", "main"))),
    seg("Standing hip-front stretch", "block", 60, T(("hip_flexor", "easier", "20 seconds each side, both hands down"), ("hip_flexor", "main", "2 × 20 seconds each side"),
                                                     ("hip_flexor", "harder", "2 × 20 seconds each side, arm up"), ("hip_flexor", "harder", "2 × 30 seconds each side, arm up"))),
    seg("Standing bird-dog", "block", 55, T(("standing_birddog", "easier", "4 each side, leg only"), ("standing_birddog", "main", "6 each side"),
                                             ("standing_birddog", "harder", "8 each side, 3-second hold"), ("standing_birddog", "harder", "10 each side, 3-second hold"))),
    seg("Wall slides", "block", 45, same("wall_slide", "6 finger walks", "8 slides", "8 slides, 2-second hold", "10 slides, 2-second hold", ("easier", "main", "harder", "harder"))),
    seg("Figure-4 hip stretch", "block", 50, same("figure4", "20 seconds each side, ankle on shin", "30 seconds each side", "30 seconds each side", "30 seconds each side, hinge forward", ("easier", "main", "main", "harder"))),
    seg("Seated hamstring stretch", "block", 50, same("hamstring_seated", "20 seconds each leg", "30 seconds each leg", "30 seconds each leg", "30 seconds each leg", ("easier", "main", "main", "harder"))),
    seg("4-6 breathing", "cooldown", 60, same("breath_46", "1 minute, in 3 out 4", "1 minute", "1 minute", "1 minute", ("easier", "main", "main", "main"))),
    seg("Close", "close", 25, vo=["Stiff in the morning? Tomorrow, notice the first ten minutes. Tell me if it's easier by next week.", "Same time tomorrow."]),
])

session(n=17, weekday="Wednesday", type="Balance", title="New steps", set="SET-KITCHEN", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Skip the step-overs; weight shifts and heel-to-toe stand instead.", sore_back="Skip backward walking.", low_energy="Toe and heel walks, heel-to-toe stand."),
        segments=[
    intro(17, "Balance", ["Wednesday. Balance. Four new steps today, all at the counter.", "Shoes on. Clear floor. Hand on the counter the whole time for anything new.", "Dizzy? Sit down."]),
    seg("Weight shifts", "warmup", 40, same("weight_shift", "5 each way, seated", "6 each way", "8 each way", "8 each way, hand hovering", ("easier", "main", "harder", "harder"))),
    seg("Toe walk", "block", 50, T(("heel_raise", "easier", "10 seated heel raises"), ("toe_walk", "easier", "10 heel raises at the counter"),
                                   ("toe_walk", "main", "2 lengths, hand on the counter"), ("toe_walk", "harder", "2 lengths, hand hovering"))),
    seg("Heel walk", "block", 50, T(("ankle_pumps", "main", "15 toe lifts, seated"), ("heel_walk", "easier", "10 toe lifts at the counter"),
                                    ("heel_walk", "main", "2 lengths, hand on the counter"), ("heel_walk", "main", "2 lengths, hand on the counter"))),
    seg("Step over a towel", "block", 60, T(("seated_march", "harder", "10 high knee lifts, seated"), ("step_over", "easier", "6 steps over a flat towel each way"),
                                            ("step_over", "main", "8 steps over a rolled towel each way"), ("step_over", "harder", "8 forward and back, hand on the counter"))),
    seg("Heel-to-toe stand", "block", 70, T(("tandem_stand", "easier", "3 × 15 seconds each side, half-step"), ("tandem_stand", "main", "3 × 20 seconds each side"),
                                            ("tandem_stand", "harder", "3 × 20 seconds each side, hand hovering"), ("tandem_stand", "harder", "3 × 30 seconds each side, hands hovering"))),
    seg("One-leg stand", "block", 70, T(("single_leg", "easier", "3 × 10 seconds each side, toe down"), ("single_leg", "main", "3 × 15 seconds each side"),
                                        ("single_leg", "harder", "3 × 20 seconds each side, hand hovering"), ("single_leg", "harder", "3 × 30 seconds each side, hands hovering"))),
    seg("Backward walk", "block", 50, T(("weight_shift", "easier", "5 front-to-back shifts, seated"), ("backward_walk", "easier", "5 small steps, hand on the counter"),
                                        ("backward_walk", "main", "2 × 10 steps, hand on the counter"), ("backward_walk", "harder", "3 × 10 steps, slower, hand on the counter")),
        vo=["Hand resting on the counter. Look behind you first. Path clear.", "Normal steps backward. Toe, then heel.", "Breathe steadily. Slow is correct."],
        ost=["Backward: hand stays on the counter"]),
    seg("Sit-to-stand, no hands", "block", 45, T(("sit_to_stand", "easier", "1 set of 6"), ("sit_stand_nohands", "main", "1 set of 8"),
                                                 ("sit_stand_nohands", "harder", "2 sets of 6, feet together"), ("sit_stand_nohands", "harder", "2 sets of 8, feet together"))),
    sigh_cool(30),
    seg("Close", "close", 25, vo=["New steps. You did all four.", "Tonight: heel-to-toe while you brush your teeth. Hand on the sink."]),
])

session(n=18, weekday="Thursday", type="Strength", title="Carry and climb", set="SET-STOOP", wardrobe="C-TRAIN-A",
        swaps=dict(sore_knee="Seated knee straightening instead of stairs.", sore_back="Two-hand carry only, light bags.", low_energy="Power stands and one carry."),
        segments=[
    intro(18, "Strength", ["Thursday. Carry and climb. Real life moves.", "Stairs with a rail, a bag or two, and your chair.", "Chest pain or unusual breathlessness on the stairs: stop, sit, call your doctor."]),
    march(), easy_stands(),
    seg("Power stands", "block", 100, T(("sit_to_stand", "easier", "3 sets of 5, normal speed"), ("power_stand", "main", "3 sets of 5"),
                                        ("power_stand", "harder", "3 sets of 6, jug at chest"), ("power_stand", "harder", "3 sets of 8, gallon jug at chest (advanced)"))),
    seg("Stair practice", "block", 100, T(("seated_march", "harder", "3 × 30 seconds, knees high"), ("stair_climb", "easier", "Bottom 3 steps, up and down, 3 times"),
                                          ("stair_climb", "main", "1 flight up and down, twice"), ("stair_climb", "harder", "2 flights, a light bag in the free hand")),
        vo=["Bottom of the stairs. Hand on the rail. The whole time.", "Whole foot on each step. Steady pace.", "Breathe steadily. Rest at the top as long as you like."]),
    seg("One-side carry", "block", 70, T(("towel_wring", "main", "3 wrings each way"), ("suitcase_carry", "easier", "2 × 20 seconds each side, light bag"),
                                         ("suitcase_carry", "main", "2 × 30 seconds each side"), ("suitcase_carry", "harder", "3 × 30 seconds each side, heavier bag"))),
    seg("Band pull-apart", "block", 55, same("band_pull_apart", "2 sets of 8, towel", "2 sets of 10", "3 sets of 10", "3 sets of 12", ("easier", "main", "main", "harder"))),
    seg("Curls", "block", 55, same("bottle_curl", "2 sets of 10, bottles", "2 sets of 10, half-gallon jug", "3 sets of 10, half-gallon jug", "3 sets of 10, gallon jug", ("main", "harder", "harder", "harder"))),
    sigh_cool(40),
    seg("Close", "close", 25, vo=["Carry and climb. That's groceries and grandkids.", "Tomorrow: breath and two new tai chi forms."]),
])

session(n=19, weekday="Friday", type="Breath + qigong", title="Two new forms", set="SET-YARD", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Arms-only versions, feet together.", sore_back="Seated breathing and sky lift only.", low_energy="Breathing and cloud hands."),
        segments=[
    intro(19, "Breath + tai chi", ["Friday. Breath and two new tai chi forms: brush knee, and parting the horse's mane.",
                                   "Short steps. Slow. Counter or fence within reach.", "Dizzy or light-headed: sit down."]),
    seg("Cyclic sighing", "block", 90, same("cyclic_sigh", "90 seconds", "90 seconds", "90 seconds", "90 seconds", ("main",) * 4)),
    seg("Holding up the sky", "block", 50, same("sky_lift", "4 reps, seated", "5 reps", "6 reps", "6 reps, rise onto toes", ("easier", "main", "main", "harder"))),
    seg("Brush knee", "block", 80, same("brush_knee", "4 each side, arms only", "4 each side", "6 each side", "4 steps across and back", ("easier", "main", "main", "harder")),
        vo=["Near the fence. Feet hip-width. Soft knees.", "Short step forward, heel first. Hand brushes past the knee. Other hand pushes forward.",
            "Weight moves slowly front. Breathe out as you push.", "Tai chi is slow balance practice: weight shifts, short steps, turning. Balance is one of the most trainable things there is."],
        ost=["Short step, slow shift"]),
    seg("Parting the horse's mane", "block", 80, same("parting_mane", "4 each side, arms only", "4 each side", "6 each side", "4 steps across and back", ("easier", "main", "main", "harder"))),
    seg("Cloud hands", "block", 60, same("cloud_hands", "1 minute, seated", "1 minute", "1 minute", "1 minute with side steps", ("easier", "main", "main", "harder"))),
    seg("Heel raise and slow lower", "block", 40, T(("heel_raise", "easier", "8 seated"), ("heel_drop", "easier", "8, slow lower, no drop"),
                                                    ("heel_drop", "easier", "10, slow lower"), ("heel_drop", "main", "8 gentle drops")),
        vo=["Hands on the counter. Up on the toes.", "Lower slowly. Iron can use a soft bump, if bones and joints allow.", "Breathe in as you rise, out as you lower."]),
    seg("4-6 breathing", "cooldown", 60, same("breath_46", "1 minute", "1 minute", "1 minute", "1 minute", ("main",) * 4)),
    seg("Close", "close", 25, vo=["Two new forms. Slow like honey.", "Tomorrow: big steps on the walk."]),
])

session(n=20, weekday="Saturday", type="Walk-and-talk", title="Big steps", set="SET-PROM", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Normal-length steps, flat route, easy pace.", sore_back="Easy pace, rest on benches.", low_energy="Easy pace throughout."),
        segments=[
    intro(20, "Walk", ["Saturday. We walk. Today a drill: bigger steps.", "Good shoes. Flat route. Indoors counts.", "Chest pain or unusual breathlessness? Stop, sit, call your doctor."]),
    seg("Easy walk", "block", 120, T(("seated_march", "main", "2 minutes, or walker lengths of the hallway"), ("walk", "easier", "2 minutes easy"),
                                     ("walk", "easier", "2 minutes easy"), ("walk", "easier", "2 minutes easy"))),
    seg("Big-step drill", "block", 60, T(("seated_march", "harder", "1 minute, big knee lifts"), ("big_steps", "easier", "2 × 10 steps along the counter"),
                                         ("big_steps", "main", "2 × 10 big steps"), ("big_steps", "harder", "2 × 20 big steps, a little faster"))),
    seg("Brisk", "block", 90, T(("seated_march", "harder", "1 minute faster, 30 seconds easy"), ("walk", "main", "90 seconds, a little faster"),
                                ("walk", "main", "90 seconds brisk"), ("walk", "harder", "90 seconds brisk, uphill if you have one"))),
    seg("Easy", "block", 60, T(("seated_march", "main", "1 minute easy"), ("walk", "easier", "1 minute easy"), ("walk", "easier", "1 minute easy"), ("walk", "easier", "1 minute easy"))),
    seg("Brisk", "block", 90, T(("seated_march", "harder", "1 minute faster, 30 seconds easy"), ("walk", "main", "90 seconds, a little faster"),
                                ("walk", "main", "90 seconds brisk"), ("walk", "harder", "90 seconds brisk"))),
    seg("Cool-down walk", "cooldown", 70, T(("seated_march", "easier", "70 seconds slow"), ("walk", "easier", "70 seconds slow"), ("walk", "easier", "70 seconds slow"), ("walk", "easier", "70 seconds slow"))),
    seg("Calf stretch at the rail", "cooldown", 40, same("calf_stretch", "20 seconds each leg, both hands on the rail", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Close", "close", 25, vo=["Heel, roll, push. Walk tall.", "Tomorrow: rest, stretch, and your three-week check."]),
])

session(n=21, weekday="Sunday", type="Rest + stretch", title="Three weeks in", set="SET-LIVING", wardrobe="C-CASUAL",
        swaps=dict(sore_knee="Skip the figure-4.", sore_back="Tiny knee rocks only if comfortable.", low_energy="Breathing and the check-in."),
        segments=[
    intro(21, "Rest + stretch", ["Sunday. Three weeks in.", "Easy stretches, some on the bed, then your check-in.", "Anything sharp? Stop."]),
    seg("Cyclic sighing", "block", 60, same("cyclic_sigh", "1 minute", "1 minute", "1 minute", "1 minute", ("main",) * 4)),
    seg("Neck nods and half-turns", "block", 40, same("neck_nods", "4 nods, 2 turns each side", "5 nods, 3 turns each side", "5 nods, 3 turns each side", "5 nods, 3 turns each side", ("easier", "main", "main", "main"))),
    seg("Knee rocks on the bed", "block", 50, same("knee_rock_bed", "4 each side, tiny", "6 each side", "6 each side", "8 each side, pause", ("easier", "main", "main", "harder"))),
    seg("Bed bridge", "block", 45, same("bed_bridge", "6 squeezes", "10 bridges", "10 bridges, 3-second hold", "12 bridges, 3-second hold", ("easier", "main", "harder", "harder"))),
    seg("Ankle pumps before standing", "block", 30, same("ankle_pumps", "10 pumps", "10 pumps", "10 pumps", "10 pumps", ("main",) * 4),
        vo=["Sit up slowly. Ankle pumps. Ten.", "Sit a moment before you stand. Then stand slowly, holding something."], ost=["Sit a moment before you stand"]),
    seg("Seated hamstring stretch", "block", 55, same("hamstring_seated", "20 seconds each leg", "30 seconds each leg", "30 seconds each leg", "30 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Calf stretch", "block", 45, same("calf_stretch", "20 seconds each leg, both hands on the counter", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Three-week check-in", "checkin", 95, vo=["Log. Sessions in three weeks. Your best chair-stand set.", "Your best one-leg time. How your back feels in the morning, one to five.",
                                                  "Easy two sessions in a row? The app offers the next level. You choose.", "Retest on day 30. Next Thursday you'll get a mini check."],
        ost=["Retest: day 30 · mini check: day 25"]),
    seg("Close", "close", 30, vo=["Three weeks. Strong is a habit, and you're building one.", "Call someone today."], sun=["And eat breakfast with protein. I'm watching."]),
])

# ------------------------------------------------------------------ WEEK 4
session(n=22, weekday="Monday", type="Strength", title="Heavier jug, slower lowering", set="SET-GARAGE", wardrobe="C-TRAIN-A",
        swaps=dict(sore_knee="Higher seat, half range; skip the floor.", sore_back="Seated hinge and towel pull-apart.", low_energy="One set each."),
        segments=[
    intro(22, "Strength", ["Week four. Monday. Same moves, slower lowering.", "Slow on the way down is where strength grows.", "Chair against the wall. Counter close. Chest pain, dizziness, sharp pain: stop."]),
    march(), easy_stands(),
    seg("Legs", "block", 120, T(("sit_to_stand", "easier", "3 sets of 8, hands on thighs"), ("sit_to_stand", "harder", "3 sets of 8, 3-second lower"),
                                ("sit_to_stand", "harder", "3 sets of 10, jug at chest, 3-second lower"), ("split_squat", "harder", "3 sets of 10 each leg, jug (advanced)"))),
    seg("Push", "block", 90, T(("seated_chest_press", "harder", "3 sets of 10, band"), ("counter_pushup", "main", "2 sets of 8"),
                               ("counter_pushup", "harder", "3 sets of 10, 3-second lower"), ("counter_pushup", "harder", "3 sets of 12, 3-second lower"))),
    seg("Band row", "block", 70, T(("towel_row", "main", "5 pulls, 3-second squeeze"), ("band_row", "main", "3 sets of 10"),
                                   ("band_row", "harder", "3 sets of 10, pause"), ("band_row", "harder", "3 sets of 12, pause"))),
    seg("Suitcase lift", "block", 70, T(("seated_hinge", "main", "2 sets of 8"), ("suitcase_lift", "main", "2 sets of 10 each side"),
                                        ("suitcase_lift", "main", "3 sets of 10 each side"), ("suitcase_lift", "harder", "3 sets of 10 each side, heavier"))),
    seg("High wall sit", "block", 55, T(("seated_knee_ext", "main", "2 sets of 10 each leg"), ("wall_sit_high", "main", "2 holds of 20 seconds"),
                                        ("wall_sit_high", "main", "3 holds of 20 seconds"), ("wall_sit_high", "harder", "3 holds of 30 seconds")),
        vo=["Back on the wall. A few inches down. Chair beside you.", "Keep talking. Count out loud with me.", "High blood pressure or a heart condition? Keep it short and ask your doctor about longer holds."],
        ost=["Keep breathing: count out loud"]),
    seg("Calf stretch", "cooldown", 45, same("calf_stretch", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    sigh_cool(35),
    seg("Close", "close", 25, vo=["Slow down. That's where it counts.", "Same time tomorrow."]),
])

session(n=23, weekday="Tuesday", type="Mobility", title="Shoulders, ankles, neck", set="SET-YARD", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Seated moves only.", sore_back="Skip the bird-dog.", low_energy="Seated moves and breathing."),
        segments=[
    intro(23, "Mobility", ["Tuesday. Mobility. Shoulders, ankles, neck.", "Small, slow, comfortable.", "Sharp pain or dizziness? Stop."]),
    seg("Ankle pumps and circles", "warmup", 40, same("ankle_pumps", "10 pumps + circles", "10 pumps + circles", "10 pumps + circles, foot lifted", "10 pumps + circles, foot lifted", ("main", "main", "harder", "harder"))),
    seg("Chin tucks", "block", 40, same("chin_tuck", "5 tucks", "6 tucks, 2-second hold", "8 tucks", "8 tucks, 5-second hold", ("easier", "main", "main", "harder"))),
    seg("Neck nods and half-turns", "block", 40, same("neck_nods", "4 nods, 2 turns each side", "5 nods, 3 turns each side", "5 nods, 3 turns each side", "5 nods, 3 turns each side", ("easier", "main", "main", "main"))),
    seg("Shoulder rolls", "block", 30, same("shoulder_rolls", "6 rolls", "8 rolls", "8 rolls + circles", "8 rolls + circles", ("main", "main", "harder", "harder"))),
    seg("Wall slides", "block", 50, same("wall_slide", "6 finger walks", "8 slides", "10 slides, 2-second hold", "10 slides, 2-second hold", ("easier", "main", "harder", "harder"))),
    seg("Calf stretch", "block", 50, same("calf_stretch", "20 seconds each leg", "2 × 20 seconds each leg", "2 × 20 seconds each leg, bent knee too", "2 × 30 seconds each leg", ("easier", "main", "harder", "harder"))),
    seg("Standing bird-dog", "block", 50, T(("standing_birddog", "easier", "4 each side, leg only"), ("standing_birddog", "main", "8 each side"),
                                             ("standing_birddog", "harder", "8 each side, 3-second hold"), ("standing_birddog", "harder", "10 each side, 3-second hold"))),
    seg("Gentle seated turn", "block", 45, same("seated_rotation", "4 each side", "6 each side", "6 each side", "8 each side", ("easier", "main", "main", "main"))),
    seg("Prayer and wrist stretch", "block", 40, same("hand_stretch", "10 seconds, twice", "20 seconds, twice", "20 seconds, twice", "20 seconds, twice", ("easier", "main", "main", "main"))),
    seg("4-6 breathing", "cooldown", 60, same("breath_46", "1 minute, in 3 out 4", "1 minute", "1 minute", "1 minute", ("easier", "main", "main", "main"))),
    seg("Close", "close", 25, vo=["Loose shoulders, happy neck.", "Tomorrow, balance."]),
])

session(n=24, weekday="Wednesday", type="Balance", title="Put the steps together", set="SET-KITCHEN", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Stands only, no walking drills.", sore_back="Front reaches only.", low_energy="Heel-to-toe stand, one-leg stand."),
        segments=[
    intro(24, "Balance", ["Wednesday. Balance. We put the new steps together.", "Counter for everything. Chair behind you.", "Dizzy? Sit down."]),
    seg("Weight shifts", "warmup", 40, same("weight_shift", "5 each way, seated", "6 each way", "8 each way", "8 each way, hand hovering", ("easier", "main", "harder", "harder"))),
    seg("Heel-to-toe walk", "block", 60, T(("heel_toe_walk", "easier", "2 lengths, feet apart, holding on"), ("heel_toe_walk", "main", "3 lengths"),
                                           ("heel_toe_walk", "harder", "3 lengths, hand hovering"), ("heel_toe_walk", "harder", "4 lengths, hand hovering"))),
    seg("Toe and heel walks", "block", 60, T(("heel_raise", "easier", "10 seated heel raises + 10 toe lifts"), ("toe_walk", "main", "1 length toes + 1 length heels"),
                                             ("toe_walk", "main", "2 lengths toes + 2 heels"), ("toe_walk", "harder", "2 lengths toes + 2 heels, hand hovering"))),
    seg("Step over a towel", "block", 55, T(("seated_march", "harder", "10 high knee lifts, seated"), ("step_over", "main", "8 each way"),
                                            ("step_over", "harder", "8 forward and back"), ("step_over", "harder", "10 forward and back"))),
    seg("One-leg stand + reach", "block", 70, T(("single_leg", "easier", "3 × 10 seconds each side, toe down"), ("single_leg", "main", "3 × 20 seconds each side"),
                                                ("clock_reach", "harder", "4 reaches on one foot each side, hand on the counter"), ("clock_reach", "harder", "6 reaches on one foot each side"))),
    seg("Backward walk", "block", 50, T(("weight_shift", "easier", "5 front-to-back shifts, seated"), ("backward_walk", "main", "2 × 10 steps"),
                                        ("backward_walk", "harder", "3 × 10 steps"), ("backward_walk", "harder", "3 × 10 steps")),
        vo=["Hand resting on the counter. Look behind you. Clear.", "Normal steps backward.", "Breathe steadily."]),
    seg("Cloud hands", "block", 60, same("cloud_hands", "1 minute, seated", "1 minute", "1 minute with side steps", "90 seconds with side steps", ("easier", "main", "harder", "harder"))),
    sigh_cool(30),
    seg("Close", "close", 25, vo=["Update the fridge chart.", "Tomorrow: strength and your mini check."]),
])

session(n=25, weekday="Thursday", type="Strength", title="Strength and your mini check", set="SET-GARAGE", wardrobe="C-TRAIN-A",
        swaps=dict(sore_knee="Skip the check; do seated knee straightening.", sore_back="Skip the carry.", low_energy="Just the mini check."),
        segments=[
    intro(25, "Strength + mini check", ["Thursday. Short strength today, then a mini check: 30-second chair stands and the balance stand.",
                                        "A number that moves. Before your renewal date, you get to see it.", "Chest pain, dizziness, sharp pain: stop."],
          extra_ost=["Mini check: chair stands + balance"]),
    march(),
    seg("Power stands", "block", 90, T(("sit_to_stand", "easier", "2 sets of 5"), ("power_stand", "main", "2 sets of 5"),
                                       ("power_stand", "harder", "2 sets of 6, jug"), ("power_stand", "harder", "3 sets of 6, jug (advanced)"))),
    seg("Band pull-apart", "block", 50, same("band_pull_apart", "2 sets of 8, towel", "2 sets of 10", "3 sets of 10", "3 sets of 12", ("easier", "main", "main", "harder"))),
    seg("Carry", "block", 60, T(("towel_wring", "main", "3 wrings each way"), ("carry", "main", "2 walks of 30 seconds"),
                                ("carry", "harder", "2 walks of 40 seconds, heavier"), ("carry", "harder", "3 walks of 45 seconds, heavy"))),
    seg("Rest before the check", "checkin", 60, vo=["Sit. Drink some water. One minute.", "Chair against the wall. Arms crossed, or hands on thighs if you need them. Same way as day one.",
                                                    "Ready the timer. I'll count you in."]),
    seg("Mini check: 30-second chair stand", "block", 60, T(("sit_to_stand", "easier", "30 seconds, count stands, hands allowed (write H)"), ("sit_to_stand", "main", "30 seconds, count full stands"),
                                                            ("sit_to_stand", "main", "30 seconds, count full stands"), ("sit_to_stand", "main", "30 seconds, count full stands")),
        vo=["Chair against the wall. Arms crossed.", "Three, two, one, go. Stand all the way up, sit all the way down.", "Breathe out as you stand. Ten seconds left.", "Stop. Write your number."],
        ost=["30-second chair stand", "Write your number"]),
    seg("Mini check: balance stand", "block", 70, T(("tandem_stand", "easier", "Half-step stand, both hands hovering over the counter: seconds held (up to 10)"), ("tandem_stand", "main", "Heel-to-toe, hand hovering: seconds held (up to 10)"),
                                                   ("single_leg", "main", "One-leg stand, hand hovering: seconds held (up to 10)"), ("single_leg", "main", "One-leg stand, hand hovering: seconds held (up to 10)")),
        vo=["At the counter. Hand hovering just above it. Grab it any time.", "Hold up to ten seconds. The moment you touch the counter or move your feet, that's your time.",
            "Breathe. Switch feet if you like. Write your best time."], ost=["Up to 10 seconds · grab the counter anytime"]),
    seg("Close", "close", 35, vo=["Compare with day one. Up by even one? That's real.", "Didn't move? Tired days happen. The full retest is day 30.", "Muscle is a savings account. You've been depositing."]),
])

session(n=26, weekday="Friday", type="Breath + qigong", title="The whole flow", set="SET-PROM", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Arms-only, seated.", sore_back="Seated breathing and sky lift.", low_energy="Breathing and cloud hands."),
        segments=[
    intro(26, "Breath + qigong", ["Friday. The whole flow. Everything you've learned, one after another.", "Chair behind you. Slow like honey.", "Light-headed or dizzy: sit."]),
    seg("Cyclic sighing", "block", 90, same("cyclic_sigh", "90 seconds", "90 seconds", "90 seconds", "90 seconds", ("main",) * 4)),
    seg("Holding up the sky", "block", 45, same("sky_lift", "4 reps, seated", "5 reps", "6 reps", "6 reps, rise onto toes", ("easier", "main", "main", "harder"))),
    seg("Drawing the bow", "block", 45, same("draw_bow", "3 each side, seated", "4 each side", "5 each side", "5 each side", ("easier", "main", "main", "harder"))),
    seg("Separating heaven and earth", "block", 45, same("heaven_earth", "3 each side, seated", "4 each side", "5 each side", "5 each side", ("easier", "main", "main", "harder"))),
    seg("Looking back", "block", 40, same("owl_look", "3 each side, eyes more than head", "3 each side", "4 each side", "4 each side", ("easier", "main", "main", "main"))),
    seg("Punching with a steady gaze", "block", 45, same("fists", "4 each side, seated", "5 each side", "6 each side", "6 each side", ("easier", "main", "main", "harder"))),
    seg("Brush knee", "block", 55, same("brush_knee", "4 each side, arms only", "4 each side", "6 each side", "4 steps across and back", ("easier", "main", "main", "harder"))),
    seg("Parting the horse's mane", "block", 55, same("parting_mane", "4 each side, arms only", "4 each side", "6 each side", "4 steps across and back", ("easier", "main", "main", "harder"))),
    seg("Cloud hands", "block", 60, same("cloud_hands", "1 minute, seated", "1 minute", "1 minute", "1 minute with side steps", ("easier", "main", "main", "harder"))),
    seg("4-6 breathing", "cooldown", 60, same("breath_46", "1 minute", "1 minute", "1 minute", "1 minute", ("main",) * 4)),
    seg("Close", "close", 25, vo=["The whole flow. Four weeks ago you didn't know it.", "Tomorrow: walk."]),
])

session(n=27, weekday="Saturday", type="Walk-and-talk", title="Longer walk", set="SET-PROM", wardrobe="C-TRAIN-B",
        swaps=dict(sore_knee="Flat, easy pace, shorter.", sore_back="Easy pace, benches.", low_energy="Easy pace."),
        segments=[
    intro(27, "Walk", ["Saturday. A longer steady walk today, with Sun.", "Good shoes. Flat route. Indoors counts.", "Chest pain or unusual breathlessness: stop, sit, call your doctor."]),
    seg("Easy walk", "block", 120, T(("seated_march", "main", "2 minutes"), ("walk", "easier", "2 minutes easy"), ("walk", "easier", "2 minutes easy"), ("walk", "easier", "2 minutes easy"))),
    seg("Steady walk", "block", 240, T(("seated_march", "main", "4 minutes, 1 on 30 seconds off, or hallway lengths"), ("walk", "main", "4 minutes steady"),
                                       ("walk", "main", "4 minutes brisk"), ("walk", "harder", "4 minutes brisk, hills")),
        vo=["Steady pace. Tall. Arms swing.", "Can talk, can't sing.", "Sun, you're ahead of me.", "Breathe steady."], sun=["Walk faster, old man."]),
    seg("Big-step drill", "block", 50, T(("seated_march", "harder", "30 seconds big knee lifts"), ("big_steps", "main", "10 big steps"),
                                         ("big_steps", "main", "20 big steps"), ("big_steps", "harder", "20 big steps, faster"))),
    seg("Cool-down walk", "cooldown", 80, T(("seated_march", "easier", "80 seconds slow"), ("walk", "easier", "80 seconds slow"), ("walk", "easier", "80 seconds slow"), ("walk", "easier", "80 seconds slow"))),
    seg("Calf stretch at the rail", "cooldown", 40, same("calf_stretch", "20 seconds each leg, both hands on the rail", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Close", "close", 25, vo=["Tell me your steps. Adults over 60 in one big study: benefit levelled off around six to eight thousand a day.", "Tomorrow: month-one reflection."],
        ost=["Study: adults 60+, 6,000–8,000 steps/day"]),
])

session(n=28, weekday="Sunday", type="Rest + stretch", title="Month one", set="SET-LIVING", wardrobe="C-CASUAL",
        swaps=dict(sore_knee="Skip the figure-4.", sore_back="Skip the bridge.", low_energy="Breathing and reflection."),
        segments=[
    intro(28, "Rest + stretch", ["Sunday. Four weeks. A month.", "Gentle stretches, then a look back at your month.", "Anything sharp? Stop."]),
    seg("Cyclic sighing", "block", 60, same("cyclic_sigh", "1 minute", "1 minute", "1 minute", "1 minute", ("main",) * 4)),
    seg("Chin tucks", "block", 30, same("chin_tuck", "5 tucks", "6 tucks", "6 tucks", "6 tucks, 5-second hold", ("easier", "main", "main", "harder"))),
    seg("Gentle seated turn", "block", 45, same("seated_rotation", "3 each side", "5 each side", "5 each side", "5 each side", ("easier", "main", "main", "main"))),
    seg("Seated hamstring stretch", "block", 55, same("hamstring_seated", "20 seconds each leg", "30 seconds each leg", "30 seconds each leg", "30 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Figure-4 hip stretch", "block", 50, same("figure4", "20 seconds each side, ankle on shin", "30 seconds each side", "30 seconds each side", "30 seconds each side", ("easier", "main", "main", "main"))),
    seg("Pelvic tilt on the bed", "block", 45, same("pelvic_tilt_bed", "6 small tilts", "8 tilts", "10 tilts, 2-second hold", "10 tilts, 5-second hold", ("easier", "main", "main", "harder"))),
    seg("Ankle pumps before standing", "block", 30, same("ankle_pumps", "10 pumps", "10 pumps", "10 pumps", "10 pumps", ("main",) * 4),
        vo=["Sit up slowly. Ankle pumps.", "Sit a moment before you stand. Then stand slowly, holding something."], ost=["Sit a moment before you stand"]),
    seg("Calf stretch", "block", 45, same("calf_stretch", "20 seconds each leg, both hands on the counter", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Month-one reflection", "checkin", 80, vo=["Look at your log. How many sessions this month?", "Your mini check from Thursday, next to day one.",
                                                   "One thing that's easier in real life. Stairs. Groceries. Getting off the sofa.", "Write it down. That's the one that matters.",
                                                   "Your full Strength Age retest is day 30. Chang walks you through it in the app."]),
    seg("Close", "close", 30, vo=["A month. You're not done yet. Neither am I.", "Same time tomorrow."], sun=["Eight out of ten. Two months in a row and I'll consider a nine."]),
])

# ------------------------------------------------------------------ WEEK 5 start
session(n=29, weekday="Monday", type="Strength", title="Month two begins", set="SET-GARAGE", wardrobe="C-TRAIN-A",
        swaps=dict(sore_knee="Higher seat, skip the floor.", sore_back="Seated hinge, towel pull-apart.", low_energy="One set each."),
        segments=[
    intro(29, "Strength", ["Month two. Monday.", "If last month's moves felt easy, the app is offering your next level today. You decide.", "Chair against the wall. Chest pain, dizziness, sharp pain: stop."]),
    march(), easy_stands(),
    seg("Legs", "block", 120, T(("sit_to_stand", "main", "3 sets of 6, arms crossed if you can"), ("sit_to_stand", "harder", "3 sets of 10, 3-second lower"),
                                ("power_stand", "harder", "3 sets of 6, jug at chest"), ("split_squat", "harder", "3 sets of 12 each leg, jug (advanced)"))),
    seg("Push", "block", 90, T(("seated_chest_press", "harder", "3 sets of 12, band"), ("counter_pushup", "main", "3 sets of 8"),
                               ("counter_pushup", "harder", "3 sets of 12, 3-second lower"), ("counter_pushup", "harder", "3 sets of 12, 3-second lower, 1-second pause"))),
    seg("Band row", "block", 70, T(("band_row", "easier", "3 sets of 8, close to the door"), ("band_row", "main", "3 sets of 10"),
                                   ("band_row", "harder", "3 sets of 12, pause"), ("band_row", "harder", "3 sets of 12, stronger band, pause"))),
    seg("Floor practice", "block", 80, T(("sit_to_stand", "easier", "1 set of 6 (no floor)"), ("floor_practice", "main", "2 kneel-and-rise, holding the chair"),
                                         ("floor_practice", "main", "3 kneel-and-rise, holding the chair"), ("floor_practice", "harder", "2 sit-to-floor and rise, someone home")),
        vo=["Chair beside you. Towel down. Someone home.", "Kneel, then rise through the front foot. Hands on the chair.", "Breathe out as you push up. Stand still a moment.", "New knee or dizziness: chair stands instead."],
        ost=["Only with a sturdy chair and someone home"]),
    seg("Heel raises", "block", 45, T(("heel_raise", "easier", "2 sets of 12, seated"), ("heel_raise", "harder", "2 sets of 12, one hand"),
                                      ("heel_raise", "harder", "2 sets of 8 each leg"), ("heel_raise", "harder", "3 sets of 10 each leg"))),
    seg("Calf stretch", "cooldown", 45, same("calf_stretch", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    sigh_cool(30),
    seg("Close", "close", 25, vo=["Month two. Strong is a habit.", "Tomorrow: mobility, then your full retest in the app."]),
])

session(n=30, weekday="Tuesday", type="Mobility", title="Loosen up before the retest", set="SET-LIVING", wardrobe="C-CASUAL",
        swaps=dict(sore_knee="Seated only.", sore_back="Chest lift, wall slides, breathing.", low_energy="Seated moves, then the retest another day."),
        segments=[
    intro(30, "Mobility", ["Day 30. Easy mobility today, because it's retest day.", "Loosen up now. Then open the app and Chang walks you through your six tests.", "Anything sharp? Stop."],
          extra_ost=["Today: Strength Age retest in the app"]),
    seg("Ankle pumps", "warmup", 30, same("ankle_pumps", "10 pumps + circles", "10 pumps + circles", "10 pumps + circles", "10 pumps + circles", ("main",) * 4)),
    seg("Shoulder rolls", "warmup", 30, same("shoulder_rolls", "6 rolls", "8 rolls", "8 rolls + circles", "8 rolls + circles", ("main", "main", "harder", "harder"))),
    seg("Chest lift", "block", 40, same("chest_lift", "6 lifts", "8 lifts", "8 lifts, 3-second hold", "10 lifts, 3-second hold", ("easier", "main", "harder", "harder"))),
    seg("Seated hinge", "block", 45, same("seated_hinge", "6 small hinges", "8 hinges", "8 hinges", "10 hinges", ("easier", "main", "main", "main"))),
    seg("Standing hip-front stretch", "block", 55, T(("hip_flexor", "easier", "20 seconds each side, both hands down"), ("hip_flexor", "main", "20 seconds each side"),
                                                     ("hip_flexor", "main", "2 × 20 seconds each side"), ("hip_flexor", "harder", "2 × 20 seconds each side, arm up"))),
    seg("Calf stretch", "block", 45, same("calf_stretch", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", "20 seconds each leg", ("easier", "main", "main", "main"))),
    seg("Weight shifts", "block", 40, same("weight_shift", "5 each way, seated", "6 each way", "6 each way", "8 each way", ("easier", "main", "main", "main"))),
    seg("Wall slides", "block", 45, same("wall_slide", "6 finger walks", "8 slides", "8 slides", "10 slides", ("easier", "main", "main", "main"))),
    seg("Seated hamstring stretch", "block", 50, same("hamstring_seated", "20 seconds each leg", "20 seconds each leg", "30 seconds each leg", "30 seconds each leg", ("easier", "main", "main", "main"))),
    seg("4-6 breathing", "cooldown", 60, same("breath_46", "1 minute", "1 minute", "1 minute", "1 minute", ("main",) * 4)),
    seg("Close", "close", 30, vo=["Loose and ready. Water. Rest ten minutes.", "Then the retest. Same chair, same shoes, same way as day one.", "Tell me your Strength Age."]),
])
