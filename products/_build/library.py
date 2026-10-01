"""Shared exercise library for the 7-Day Strength Reset, Daily Practice Sessions and 12-Week Printable.

Every movement carries: a support cue (M-01), a breathing cue (M-04, never a breath-hold), an
easier version (M-02), a harder version, safety notes including SAFETY_RULES §4.2 contraindication
lines where the movement tag matches, and evidence IDs from EVIDENCE.md.
"""

STOP = "Stop if you feel chest pain or pressure, dizziness, unusual shortness of breath, or sharp pain."
EMERGENCY = "Chest pain, face drooping, arm weakness or trouble speaking? Call 911 now."
PAIN_RULE = ("Mild discomfort up to 3 out of 10 is okay if it settles by tomorrow. "
             "Sharper, or worse the next day: back off and ask your doctor or physical therapist.")
STAND_SLOW = "Sit a moment before you stand, then stand slowly while holding something steady."
CHAIR_SETUP = "Sturdy chair with no wheels and no arms (unless the easier version uses arms), pushed back against a wall so it cannot slide."

# SAFETY_RULES §4.2 auto-insert lines
CONTRA = {
    "isometric_hold": "Breathe through it. High blood pressure or a heart condition? Ask your doctor before long holds.",
    "floor_transfer": "Only try the floor with a sturdy chair or sofa next to you and someone home. Recent hip or knee replacement, or severe knee arthritis: follow your surgeon's or physical therapist's guidance first.",
    "deep_hip_flexion": "New hip? Follow your surgeon's precautions first.",
    "overhead_press_loaded": "Shoulder pain or a known rotator cuff problem? Only lift to a comfortable height, or skip it.",
    "spinal_twist_end_range": "Osteoporosis? Turn gently and only as far as comfortable. Never force the twist.",
    "neck": "Nods and half-turns only. Never full neck circles.",
    "standing_up_fast": STAND_SLOW,
    "gentle_impact": "Gentle impact. Skip it if you have osteoporosis without a training history, pelvic floor problems, or a joint replacement; do the heel raise without the drop instead.",
    "pelvic_floor": "If you have pelvic pain or leaking that isn't improving, a pelvic-floor physical therapist can check you.",
}

EX = {}

def ex(id, name, equip, setup, steps, cues, breathe, easier, harder, safety=(), tags=(), ev=()):
    EX[id] = dict(id=id, name=name, equip=equip, setup=setup, steps=list(steps), cues=list(cues),
                  breathe=breathe, easier=easier, harder=harder, safety=list(safety), tags=list(tags), ev=list(ev))

# ---------------------------------------------------------------- legs & lower body
ex("sit_to_stand", "Chair sit-to-stand", "Sturdy chair against a wall",
   CHAIR_SETUP + " Sit in the middle of the seat, feet flat, hip-width apart, a little behind your knees.",
   ["Cross your arms over your chest, or rest your hands on your thighs.",
    "Lean your chest forward, nose over toes.",
    "Push the floor away and stand all the way up. Squeeze your buttocks at the top.",
    "Reach your hips back and sit down slowly, like the chair is farther away than you think."],
   ["Nose over toes.", "Knees point the same way as your toes. Don't let them cave inward.", "Sit down slow. Two or three seconds."],
   "Breathe out as you stand. Breathe in as you sit.",
   "Put a firm cushion or folded blanket on the seat to make it higher, or push up with your hands on your thighs or on chair arms.",
   "Arms crossed, lower for a slow count of three, and pause one second just above the seat before touching down. Later: hold a gallon jug of water at your chest.",
   [], [], ["E01", "E02", "E11"])

ex("power_stand", "Power stand (fast up, slow down)", "Sturdy chair against a wall",
   CHAIR_SETUP,
   ["Sit tall, feet flat, arms crossed or hands on thighs.",
    "Stand up as quickly as you safely can. Think 'pop up'.",
    "Stand tall for one second.",
    "Lower slowly for a count of three."],
   ["Fast up, slow down.", "Quick is not the same as sloppy. Knees stay over toes."],
   "Breathe out hard as you stand.",
   "Normal-speed sit-to-stand with hands on your thighs.",
   "Hold a jug of water at your chest, or pause one second just above the seat on the way down.",
   ["Stop the fast part if you feel dizzy when you stand. Go back to normal speed."], [], ["E39", "E02"])

ex("wall_sit_high", "High wall sit", "A clear wall; chair beside you",
   "Stand with your back flat against a wall, feet about 1.5 feet (a forearm's length) in front of you, hip-width apart. A chair is beside you in case you want to sit.",
   ["Slide your back down the wall just a few inches, a quarter of the way to sitting.",
    "Hold, with your weight in your heels.",
    "Slide back up to finish."],
   ["Shallow is fine. This is not a contest of depth.", "Knees stay behind or over your toes."],
   "Keep breathing the whole time. Count your breaths out loud; talking keeps you from holding your breath.",
   "Slide down only 2 inches, or hold for just 10 seconds.",
   "Slide a little lower (never below where your knees are bent to a right angle), or hold up to 30 seconds.",
   [CONTRA["isometric_hold"]], ["isometric_hold"], ["E20", "E42"])

ex("heel_raise", "Heel raises at the counter", "Kitchen counter",
   "Stand facing your kitchen counter, both hands resting on it, feet hip-width apart.",
   ["Rise up onto the balls of your feet, as high as is comfortable.",
    "Pause one second at the top.",
    "Lower your heels slowly for a count of three."],
   ["Tall like someone is pulling a string on top of your head.", "Weight over the big toe and second toe, not rolling out."],
   "Breathe out as you rise.",
   "Sit in your chair and raise your heels from there, or hold the counter with both hands and rise only halfway.",
   "One hand on the counter. Later: one leg at a time, with both hands on the counter.",
   ["Calf cramps are common at first. Stretch and walk them out. One calf that is swollen, red and painful is not a cramp: that is for your doctor, today."], [], ["E47", "E13"])

ex("step_up", "Step-ups on the bottom stair", "Bottom stair with a handrail",
   "Stand facing the bottom step of your stairs. Hold the handrail the whole time. Good light, no rug, shoes on.",
   ["Step up with your right foot, placing the whole foot on the step.",
    "Push through that heel to bring your left foot up. Stand tall.",
    "Step down with the same leg you started with, slowly.",
    "Do all reps leading with one leg, then switch."],
   ["Whole foot on the step, not just the toes.", "Push through the heel of the top foot.", "Rail hand stays on the rail."],
   "Breathe out as you step up.",
   "Toe taps: tap the step with one foot, then the other, holding the rail. Or use a lower step, like a sturdy doorway threshold.",
   "Step up without pushing off the bottom foot. Later: carry a light bag of groceries in the hand that isn't on the rail.",
   ["If stairs make you dizzy or you have fallen on stairs, do toe taps only until you've practiced balance for two weeks."], [], ["E13", "E01"])

ex("split_squat", "Counter split squat (Iron track)", "Kitchen counter",
   "Stand side-on to the counter, one hand on it. Step one foot back about two feet, back heel up.",
   ["Bend both knees and lower straight down, a few inches.",
    "Front knee stays over the front foot.",
    "Push through the front heel to rise."],
   ["Straight down, like an elevator.", "Most of your weight on the front leg.", "Stay tall."],
   "Breathe out as you rise.",
   "Make the step smaller and only lower 2 or 3 inches. Or go back to sit-to-stands.",
   "Lower a little deeper (never let the back knee touch the floor), or hold a jug in the hand away from the counter.",
   ["Advanced. Only if your knees feel good with step-ups."], [], ["E02"])

ex("hip_hinge", "Counter hip hinge", "Kitchen counter",
   "Stand arm's length from the counter, hands resting on it, feet hip-width apart, soft knees.",
   ["Push your hips back, like closing a car door with your bottom.",
    "Let your chest tip forward with a long, flat back. Hands slide along the counter.",
    "Stop when you feel a stretch in the back of your thighs.",
    "Squeeze your buttocks to stand tall again."],
   ["Hips go back, not down.", "Long back, chest proud. No rounding.", "Stand up by squeezing your buttocks."],
   "Breathe out as you stand tall.",
   "Smaller movement, hands stay on the counter the whole time.",
   "Pick up a jug of water from the seat of a chair using the same hinge, and set it back down. Later: from a lower surface, like a step.",
   ["Osteoporosis or a past spine fracture: this is the safe way to bend. Keep your back long; never round forward under load."], [], ["E40", "E02"])

ex("side_step", "Side steps along the counter", "Kitchen counter",
   "Stand facing the counter, both hands resting on it.",
   ["Step sideways to the right, then bring your left foot to meet it.",
    "Take 10 steps to the right, then 10 back to the left.",
    "Toes point forward the whole time."],
   ["Stay tall.", "Small, controlled steps.", "Feet don't cross."],
   "Breathe normally. Talk or count out loud.",
   "Fewer steps, slower.",
   "Bend your knees slightly and stay low, or tie a resistance loop above your knees.",
   [], [], ["E13"])

ex("seated_knee_ext", "Seated knee straightening", "Sturdy chair against a wall",
   CHAIR_SETUP + " Sit tall with your back against the backrest.",
   ["Straighten your right knee until your leg is level, or as close as you can.",
    "Squeeze the front of your thigh for two seconds.",
    "Lower slowly. Do all reps, then switch legs."],
   ["Toes point to the ceiling.", "Squeeze, then lower slowly."],
   "Breathe out as you straighten your leg.",
   "Straighten only halfway.",
   "Hold for 5 seconds at the top, or add a light ankle weight later.",
   [], [], ["E01", "E13"])

ex("seated_march", "Seated march", "Sturdy chair against a wall",
   CHAIR_SETUP + " Sit tall near the front of the seat, hands on the sides of the seat.",
   ["Lift your right knee a few inches, lower it.",
    "Lift your left knee, lower it.",
    "Keep a steady rhythm."],
   ["Sit tall. Don't lean back.", "Lift from the hip."],
   "Breathe steadily. Count out loud.",
   "Lift the feet only an inch, or march more slowly.",
   "March faster, or pump your arms too.",
   [], [], ["E23"])

ex("standing_march", "Standing march at the counter", "Kitchen counter",
   "Stand facing the counter, one or both hands resting on it.",
   ["Lift one knee to a comfortable height, lower it.",
    "Lift the other knee.",
    "Keep a steady rhythm."],
   ["Stand tall.", "Knee up, foot down softly."],
   "Breathe steadily. You should be able to talk.",
   "Sit and do the seated march.",
   "Lift knees higher, march faster, or let one hand hover above the counter.",
   [], [], ["E23", "E13"])

# ---------------------------------------------------------------- upper body & grip
ex("wall_pushup", "Wall push-up", "A clear wall",
   "Stand arm's length from a wall. Hands on the wall at shoulder height, a little wider than your shoulders. Shoes on, non-slip floor.",
   ["Bend your elbows and bring your chest toward the wall.",
    "Elbows point back at an angle, not straight out.",
    "Push the wall away until your arms are straight."],
   ["Body in one straight line, head to heels.", "Chest to the wall, not your chin."],
   "Breathe out as you push away.",
   "Stand closer to the wall and move only halfway.",
   "Step your feet farther back. When 15 are easy, move to counter push-ups.",
   [], [], ["E01", "E02"])

ex("counter_pushup", "Counter push-up", "Kitchen counter (sturdy, not a rolling island)",
   "Hands on the edge of the kitchen counter, a little wider than your shoulders. Walk your feet back until your body is on a slant.",
   ["Lower your chest toward the counter edge.",
    "Push back up until your arms are straight."],
   ["Straight line from head to heels.", "Squeeze your buttocks so your hips don't sag."],
   "Breathe out as you push up.",
   "Wall push-ups.",
   "Lower slowly for three seconds. Later (Iron track): a sturdy low bench or bottom stair, only if the counter version is easy for 12 reps.",
   ["Wrist pain? Make fists or hold the counter edge instead of flat palms."], [], ["E01", "E02"])

ex("jug_row", "One-arm jug row at the counter", "Kitchen counter + a jug or bag (start with a half-full gallon jug, about 4 pounds)",
   "Stand side-on to the counter. Put your left hand on the counter. Step your left foot forward and hinge forward a little with a long, flat back. Jug in your right hand, arm hanging.",
   ["Pull the jug up toward your ribs, elbow close to your body.",
    "Squeeze your shoulder blade toward your spine.",
    "Lower slowly. Do all reps, then switch sides."],
   ["Pull with your elbow, not your hand.", "Long back. Don't twist."],
   "Breathe out as you pull.",
   "Stand upright and pull a towel looped around a sturdy door handle (see Towel row), or use a lighter jug.",
   "Full gallon jug (about 8 pounds), or a bag with a few cans. Pause for one second at the top.",
   ["Osteoporosis: keep the hinge small and the back long."], [], ["E01", "E02"])

ex("towel_row", "Seated towel pull-apart", "A hand towel; sturdy chair against a wall",
   CHAIR_SETUP + " Sit tall. Hold a hand towel in front of your chest with both hands, arms straight.",
   ["Pull your hands apart as hard as you can, like stretching the towel.",
    "At the same time, squeeze your shoulder blades together and down.",
    "Hold three seconds, relax."],
   ["Shoulders down, away from your ears.", "Chest proud."],
   "Breathe out as you pull. Never hold your breath.",
   "Pull gently, hold for one second.",
   "Use a resistance band instead of a towel and pull it apart to your chest.",
   [], [], ["E01"])

ex("bottle_curl", "Water-bottle curl", "Two full water bottles, or two soup cans; chair",
   CHAIR_SETUP + " Sit tall, a bottle in each hand, arms hanging, palms facing forward.",
   ["Bend your elbows and bring the bottles toward your shoulders.",
    "Lower slowly all the way down."],
   ["Elbows stay by your sides.", "No swinging."],
   "Breathe out as you curl up.",
   "One arm at a time, or empty bottles.",
   "Heavier: a half-gallon jug (about 4 pounds), then a full gallon jug (about 8 pounds), one at a time.",
   [], [], ["E01"])

ex("seated_press", "Seated overhead press (to comfortable height)", "Two water bottles; chair",
   CHAIR_SETUP + " Sit tall, a bottle in each hand at shoulder height, palms facing each other.",
   ["Press the bottles up toward the ceiling, only as high as is comfortable.",
    "Lower slowly back to your shoulders."],
   ["Ribs down. Don't arch your back.", "Only to comfortable height."],
   "Breathe out as you press up.",
   "One arm at a time, or press forward and up at a slant instead of straight up.",
   "Heavier bottles or a half-gallon jug in each hand; stand at the counter to press.",
   [CONTRA["overhead_press_loaded"]], ["overhead_press_loaded"], ["E01"])

ex("towel_wring", "Towel wring (grip)", "A small towel",
   "Sit or stand. Hold a rolled hand towel with both hands in front of you, like a bicycle handlebar.",
   ["Wring the towel hard, like squeezing out water: right hand one way, left hand the other.",
    "Hold three seconds. Switch directions."],
   ["Squeeze from your whole hand, not just your fingertips.", "Shoulders relaxed."],
   "Breathe out as you squeeze.",
   "Squeeze a soft ball or rolled sock instead.",
   "Use a damp towel, or hold each wring for five seconds.",
   ["Hand arthritis flaring today? Squeeze gently, or skip and do the finger spread only."], [], ["E07"])

ex("carry", "Grocery carry", "Two grocery bags, jugs or kettlebells; clear hallway",
   "Hold a bag or jug in each hand at your sides. Clear path, shoes on, walk along a counter or hallway wall where possible.",
   ["Stand tall, shoulders down.",
    "Walk slowly and steadily for the set time.",
    "Set the load down by hinging at the hips with a long back, not by rounding."],
   ["Tall, like you're proud of the groceries.", "Short, steady steps."],
   "Breathe steadily. You should be able to talk.",
   "One light bag, and keep your free hand trailing along the counter.",
   "Heavier: two full gallon jugs (about 8 pounds each). Iron track: two heavier bags or kettlebells.",
   ["Pick up and put down with a hinge. Never round your back to lift."], [], ["E07", "E01"])

# ---------------------------------------------------------------- balance (Otago-style, E13)
ex("tandem_stand", "Heel-to-toe stand at the counter", "Kitchen counter",
   "Stand facing the counter, both hands resting on it. Shoes on.",
   ["Place one foot directly in front of the other, heel touching toe.",
    "Stand tall and hold.",
    "Switch which foot is in front."],
   ["Eyes on something still at eye level.", "Soft knees. Tall head."],
   "Breathe slowly and steadily.",
   "Half-step stance: front foot's heel beside the big toe of the back foot. Both hands on the counter.",
   "Lift one hand to hover just above the counter. Later: both hands hovering.",
   ["Balance drills always start with support. Hands hover, they don't wander away from the counter."], [], ["E13", "E50"])

ex("single_leg", "One-leg stand at the counter", "Kitchen counter",
   "Stand facing the counter, both hands resting on it. Shoes on.",
   ["Shift your weight to your left foot.",
    "Lift your right foot a few inches off the floor.",
    "Hold, then switch."],
   ["Stand tall. Don't lean on the counter.", "Squeeze the buttock of the standing leg."],
   "Breathe slowly. Count out loud.",
   "Just shift your weight onto one foot, keeping the other toe lightly on the floor.",
   "One hand hovering above the counter, then both hands hovering, right next to the counter.",
   ["No barefoot drills on slippery floors, no socks on hard floors, no rugs under your feet."], [], ["E09", "E13"])

ex("heel_toe_walk", "Heel-to-toe walk along the counter", "Kitchen counter",
   "Stand at one end of the counter, one hand resting on it. Clear floor, shoes on.",
   ["Step forward, placing your heel directly in front of the toes of the other foot.",
    "Take 10 steps along the counter.",
    "Turn carefully and walk back."],
   ["Eyes forward, not down at your feet.", "Slow is correct."],
   "Breathe steadily.",
   "Walk with your feet slightly apart, not touching, holding the counter.",
   "Let your hand hover above the counter. Later: walk backward along the counter with one hand resting on it (normal steps).",
   [], [], ["E13"])

ex("weight_shift", "Weight shifts", "Kitchen counter or chair back",
   "Stand facing the counter, feet hip-width apart, both hands resting on it.",
   ["Slowly shift your weight to your right foot. Pause.",
    "Shift to your left foot. Pause.",
    "Then shift forward toward your toes and back toward your heels."],
   ["Move from your ankles and hips, like a tree swaying.", "Feet stay flat on the floor."],
   "Breathe slowly.",
   "Do it seated: shift your weight side to side on the chair.",
   "Make the shifts bigger, or let one hand hover.",
   [], [], ["E13", "E17"])

ex("clock_reach", "Clock reach", "Kitchen counter",
   "Stand side-on to the counter, near hand resting on it. Imagine you're standing in the middle of a clock.",
   ["Reach your free arm forward to 12 o'clock. Back to center.",
    "Reach out to the side, 3 o'clock. Back to center.",
    "Reach gently behind, only as far as comfortable. Back to center.",
    "Turn around and repeat with the other arm."],
   ["Follow your hand with your eyes.", "Feet stay planted."],
   "Breathe out as you reach.",
   "Smaller reaches, and only to the front and side.",
   "Stand on one foot while you reach to 12 o'clock, holding the counter.",
   [CONTRA["spinal_twist_end_range"]], ["spinal_twist_end_range"], ["E13"])

ex("sit_stand_nohands", "Sit-to-stand without hands (balance version)", "Sturdy chair against a wall",
   CHAIR_SETUP,
   ["Sit with feet slightly narrower than usual.",
    "Stand up without using your hands.",
    "Balance for two seconds at the top before sitting back down slowly."],
   ["Find your balance at the top before you move.", "Slow down."],
   "Breathe out as you stand.",
   "Use your hands on your thighs.",
   "Feet together.",
   [], [], ["E13"])

# ---------------------------------------------------------------- mobility & stretch
ex("ankle_pumps", "Ankle pumps and circles", "Chair or bed",
   "Sit tall in your chair (or lie on your bed).",
   ["Point your toes away, then pull them toward you. That's one pump.",
    "Then draw slow circles with your feet, both directions."],
   ["Big, slow movements.", "Feel your calves work."],
   "Breathe slowly.",
   "Smaller movements.",
   "Lift one foot off the floor while you circle.",
   ["Great before you stand up from sitting or lying. " + STAND_SLOW], ["standing_up_fast"], ["E47", "E46"])

ex("shoulder_rolls", "Shoulder rolls", "Chair",
   "Sit or stand tall.",
   ["Lift your shoulders up toward your ears.",
    "Roll them back and down.",
    "Relax. Repeat."],
   ["Big, slow circles, backward.", "Let your arms hang heavy."],
   "Breathe in as you lift, out as you roll down.",
   "Just shrug up and let go.",
   "Add arm circles: small circles out to the sides, forward and back.",
   [], [], ["E30"])

ex("neck_nods", "Neck nods and half-turns", "Chair",
   "Sit tall.",
   ["Slowly nod yes: look a little down, then back to level.",
    "Slowly turn your head to the right, only as far as comfortable. Back to center.",
    "Turn to the left. Back to center."],
   ["Small and slow.", "Chin stays level when you turn."],
   "Breathe slowly.",
   "Make the movement even smaller.",
   "Add a chin tuck: gently slide your chin straight back, making a double chin, hold two seconds.",
   [CONTRA["neck"], "Dizzy with head movements? Keep it tiny, keep your eyes open, and tell your doctor."], ["neck"], ["E30"])

ex("chin_tuck", "Chin tuck", "Chair or wall",
   "Sit or stand tall, back of the head near a wall if you like.",
   ["Slide your chin straight back, making a double chin. Keep your eyes level.",
    "Hold two seconds. Relax."],
   ["Slide back, don't tip down.", "Tall neck."],
   "Breathe normally.",
   "Smaller movement, one-second hold.",
   "Hold five seconds.",
   [CONTRA["neck"]], ["neck"], ["E30"])

ex("wall_slide", "Wall slides", "A clear wall",
   "Stand with your back against a wall, feet a few inches out. Forearms on the wall in a goalpost shape, elbows bent.",
   ["Slide your arms up the wall only as far as comfortable.",
    "Slide back down to the goalpost."],
   ["Ribs down.", "Slow and smooth."],
   "Breathe in as you slide up, out as you slide down.",
   "Face the wall and walk your fingertips up it instead.",
   "Hold for two seconds at the top.",
   [CONTRA["overhead_press_loaded"]], [], ["E30"])

ex("seated_rotation", "Gentle seated turn", "Chair",
   "Sit tall, feet flat. Cross your arms over your chest.",
   ["Turn your chest to the right, only as far as comfortable. Eyes follow.",
    "Return to center.",
    "Turn to the left."],
   ["Grow tall first, then turn.", "Hips stay still."],
   "Breathe out as you turn.",
   "Smaller turns.",
   "Place one hand on the opposite knee as a light guide. Never pull into the turn.",
   [CONTRA["spinal_twist_end_range"]], ["spinal_twist_end_range"], ["E40", "E30"])

ex("chest_lift", "Seated chest lift", "Chair",
   "Sit near the front of the seat, feet flat, hands resting on your thighs.",
   ["Lift your chest up toward the ceiling, growing tall.",
    "Gently squeeze your shoulder blades back.",
    "Relax without slumping."],
   ["Grow tall.", "Look straight ahead, not up."],
   "Breathe in as you lift, out as you relax.",
   "Smaller lift.",
   "Hold three seconds at the top.",
   [], [], ["E30", "E40"])

ex("calf_stretch", "Calf stretch at the wall", "Wall or counter",
   "Stand facing a wall or counter, hands on it. Step one foot back, heel down.",
   ["Bend the front knee and lean gently toward the wall until you feel a stretch in the back calf.",
    "Hold, breathing slowly. Switch legs."],
   ["Back heel stays down.", "Toes point forward."],
   "Breathe slowly through the stretch.",
   "Smaller step back.",
   "Bigger step back, or bend the back knee slightly to reach the lower calf.",
   [], [], ["E30"])

ex("hip_flexor", "Standing hip-front stretch", "Kitchen counter",
   "Stand side-on to the counter, near hand on it. Step one foot back into a small split stance.",
   ["Tuck your tailbone under slightly and squeeze the buttock of the back leg.",
    "Shift your hips forward a little until you feel a gentle stretch at the front of the back hip.",
    "Hold, then switch sides."],
   ["Stay tall. Don't arch your back.", "Small movement, big squeeze."],
   "Breathe slowly.",
   "Smaller step.",
   "Reach the arm on the back-leg side up toward the ceiling, to comfortable height.",
   [], [], ["E30"])

ex("hamstring_seated", "Seated hamstring stretch (long back)", "Chair",
   CHAIR_SETUP + " Sit near the front edge. Straighten one leg in front of you, heel on the floor, toes up.",
   ["Sit tall, hands on your bent knee.",
    "Hinge forward from your hips with a long, flat back until you feel a stretch behind the straight knee.",
    "Hold. Switch legs."],
   ["Chest proud. Bend from the hips, not the back.", "A gentle stretch is enough."],
   "Breathe slowly.",
   "Lean only an inch or two.",
   "Pull your toes toward you a little more.",
   ["Osteoporosis or a past spine fracture: keep the back long. Never curl down toward your toes."], [], ["E40", "E30"])

ex("figure4", "Seated hip stretch (figure-4)", "Chair",
   CHAIR_SETUP + " Sit tall.",
   ["Rest your right ankle on your left knee, or as close as you can.",
    "Sit tall and let the right knee relax down.",
    "For more, hinge forward a little with a long back. Hold. Switch."],
   ["Tall back.", "Relax the knee, don't push it."],
   "Breathe slowly.",
   "Rest the ankle on your shin instead of your knee, or skip crossing and just let the knee drop out a little.",
   "Hinge forward a little farther with a long back.",
   [CONTRA["deep_hip_flexion"]], ["deep_hip_flexion"], ["E30"])

ex("bed_bridge", "Bridge on the bed", "Your bed",
   "Lie on your back on your bed, knees bent, feet flat, arms by your sides.",
   ["Squeeze your buttocks and lift your hips a few inches.",
    "Hold one second.",
    "Lower slowly."],
   ["Push through your heels.", "Lift with your buttocks, not your back."],
   "Breathe out as you lift.",
   "Just squeeze your buttocks without lifting.",
   "Hold three seconds at the top, or lift higher.",
   [STAND_SLOW], ["standing_up_fast"], ["E30"])

ex("standing_birddog", "Standing bird-dog at the counter", "Kitchen counter",
   "Stand facing the counter, both hands on it.",
   ["Slide your right foot back and lift it a few inches behind you, toes on or just off the floor.",
    "At the same time, if steady, reach your left arm forward along the counter.",
    "Return. Switch sides."],
   ["Long back. No arching.", "Squeeze the buttock of the moving leg."],
   "Breathe out as you reach.",
   "Leg only; both hands stay on the counter.",
   "Hold the reach for three seconds.",
   [], [], ["E30", "E40"])

# ---------------------------------------------------------------- breath & tai chi / qigong
ex("cyclic_sigh", "Cyclic sighing", "Chair",
   "Sit comfortably, feet flat, hands in your lap.",
   ["Breathe in through your nose.",
    "At the top, sip in a little more air through your nose.",
    "Let it all out slowly through your mouth, longer than the in-breath.",
    "Repeat at a relaxed pace."],
   ["Two sniffs in, one long sigh out.", "No holding at any point."],
   "The out-breath is always longer than the in-breath. No breath holds.",
   "Just breathe slowly through your nose, making the out-breath a little longer.",
   "Build up to 5 minutes.",
   ["If you feel light-headed, return to normal breathing."], [], ["E18"])

ex("breath_46", "4-6 breathing", "Chair",
   "Sit tall, one hand on your belly.",
   ["Breathe in through your nose for a count of 4.",
    "Breathe out gently for a count of 6.",
    "No pause at the top or bottom."],
   ["Belly rises first.", "Soft shoulders."],
   "In for 4, out for 6. That is about 6 breaths a minute. No holds.",
   "In for 3, out for 4.",
   "Continue for 5 minutes.",
   ["If you feel light-headed, go back to normal breathing."], [], ["E19"])

ex("sky_lift", "Holding up the sky (baduanjin piece 1)", "Space to stand; chair behind you",
   "Stand tall, feet hip-width apart, knees soft, chair behind you. Interlace your fingers in front of your belly, palms up.",
   ["Breathe in and lift your hands slowly up the front of your body, turning palms to the ceiling as they pass your face.",
    "Press gently upward, only to a comfortable height.",
    "Breathe out and float your arms down to the sides."],
   ["Slow, like moving through warm water.", "Look straight ahead."],
   "Breathe in as the hands rise, out as they come down.",
   "Sit and do it seated, or lift only to shoulder height.",
   "Rise onto your toes a little at the top, holding the chair back with one hand if needed.",
   [CONTRA["overhead_press_loaded"]], [], ["E17"])

ex("draw_bow", "Drawing the bow (baduanjin piece 2, high stance)", "Space to stand; chair beside you",
   "Stand with feet a little wider than your hips, knees slightly bent. A high stance, not a deep squat.",
   ["Bring both hands in front of your chest.",
    "Push your left hand out to the left like holding a bow, while your right elbow pulls back like drawing the string. Eyes follow the left hand.",
    "Return to center. Switch sides."],
   ["Knees over toes.", "Grow tall through the top of the head."],
   "Breathe out as you draw the bow, in as you return.",
   "Sit tall in your chair and do the arm movement only.",
   "Bend your knees a little more (never below comfortable).",
   [], [], ["E17"])

ex("heaven_earth", "Separating heaven and earth (baduanjin piece 3)", "Space to stand; chair behind you",
   "Stand tall, feet hip-width apart, hands in front of your belly.",
   ["Lift your right hand up past your face and press the palm toward the ceiling, to comfortable height.",
    "At the same time, press your left palm down beside your hip.",
    "Bring both hands back to center. Switch."],
   ["One hand reaches up, one presses down.", "Long spine."],
   "Breathe in as you separate, out as you return.",
   "Seated, or lift only to shoulder height.",
   "Slower, with a longer out-breath.",
   [CONTRA["overhead_press_loaded"]], [], ["E17"])

ex("owl_look", "Looking back (baduanjin piece 4, gentle)", "Space to stand or sit",
   "Stand or sit tall, arms relaxed by your sides.",
   ["Turn your palms outward and slowly turn your head to look over your right shoulder, only as far as comfortable.",
    "Return to center. Switch."],
   ["Chin level.", "Shoulders stay down."],
   "Breathe out as you turn, in as you return.",
   "Turn your eyes more than your head.",
   "Hold the turn for one slow breath.",
   [CONTRA["neck"], CONTRA["spinal_twist_end_range"]], ["neck"], ["E17"])

ex("fists", "Punching with a steady gaze (baduanjin piece 7, high stance)", "Space to stand; chair beside you",
   "Stand with feet a little wider than hips, knees soft, loose fists at your waist, palms up.",
   ["Slowly punch your right fist forward, turning it palm down.",
    "Open the hand, grip the air, and pull the fist back to the waist.",
    "Switch sides."],
   ["Slow punch. This is not boxing.", "Eyes steady and focused."],
   "Breathe out as you punch.",
   "Seated, same arm movement.",
   "Bend your knees a little more, keeping them over your toes.",
   [], [], ["E17"])

ex("heel_drop", "Heel raise and gentle drop (baduanjin piece 8, modified)", "Kitchen counter",
   "Stand facing the counter, hands on it.",
   ["Rise up onto your toes.",
    "Lower your heels quickly but gently to the floor, like a soft bump.",
    "Or simply lower slowly, which is the version most people should use."],
   ["Tall spine.", "Soft bump, never a stomp."],
   "Breathe in as you rise, out as you lower.",
   "Heel raise with a slow lower, no drop.",
   "Ten gentle drops.",
   [CONTRA["gentle_impact"]], ["gentle_impact"], ["E17", "E29"])

ex("cloud_hands", "Cloud hands (tai chi, simplified)", "Space to stand; counter or chair nearby",
   "Stand with feet a little wider than hips, knees soft, near the counter.",
   ["Shift your weight to the right foot while your right hand floats across in front of your face and your left hand floats low in front of your belly.",
    "Shift to the left foot and let the hands switch, like wiping a big window slowly.",
    "Keep shifting side to side."],
   ["Move from your waist and legs, not just your arms.", "In tai chi we call it sinking: really, it's lowering your center of mass. Soft knees."],
   "Breathe slowly; no need to match the breath to the moves.",
   "Keep one hand on the counter and move the other hand only.",
   "Add a small side step with each shift, next to the counter.",
   [], [], ["E15", "E17"])

ex("walk", "Walk and talk", "Shoes, a safe route (hallway, mall, sidewalk)",
   "Good shoes. A route with no ice, good light, and benches or rails if possible. Cane or walker if you use one.",
   ["Walk at an easy pace for 2 minutes to warm up.",
    "Pick up the pace to 'can talk, can't sing' for the middle minutes.",
    "Slow down for the last 2 minutes."],
   ["Tall. Eyes ahead, not at your feet.", "Arms swing naturally.", "Heel, then toe."],
   "Breathe easy and steady. The talk test: you should be able to speak in short sentences.",
   "Walk indoors: kitchen to front door and back, touching the counter as you pass. Or march seated.",
   "Add 1-minute faster stretches, or a gentle hill.",
   ["Chest pain, pressure, or unusual breathlessness: stop, sit, and call your doctor. If it doesn't settle in a few minutes, call 911."], [], ["E22", "E23", "E10"])

ex("seated_chest_press", "Seated chest press", "Two water bottles or a light band; sturdy chair against a wall",
   CHAIR_SETUP + " Sit tall, a bottle in each hand at chest height, elbows bent and pointing down and out.",
   ["Press the bottles straight out in front of your chest until your arms are straight.",
    "Pause one second.",
    "Bring them back slowly to your chest."],
   ["Shoulders down, away from your ears.", "Push like you're closing a heavy drawer."],
   "Breathe out as you press.",
   "Empty hands, pressing against the air slowly, or one arm at a time.",
   "Loop a resistance band behind the chair back and press against it, or hold for 3 seconds with arms straight.",
   [], [], ["E01"])

ex("seated_hinge", "Seated hip hinge", "Sturdy chair against a wall",
   CHAIR_SETUP + " Sit near the front of the seat, feet flat and wide, hands on your thighs.",
   ["Keep your back long and tip your chest forward from the hips, sliding your hands toward your knees.",
    "Go only as far as your back stays long.",
    "Squeeze your buttocks and sit tall again."],
   ["Long back, proud chest.", "Bend at the hips, not the belly."],
   "Breathe out as you sit tall.",
   "A smaller tip forward.",
   "Hold a water bottle against your chest.",
   ["Osteoporosis: this is the safe bending pattern. Keep the back long, never curl."], [], ["E40"])

# ================================================================== program movements (added for the 12-week programs)
ex("floor_practice", "Floor practice with a chair (kneel and rise)", "Sturdy chair or sofa that can't slide, a folded towel or cushion, someone home",
   "Stand beside a sturdy chair or sofa, one hand on the seat. Put a folded towel on the floor for your knee. Someone else is home.",
   ["Holding the chair, step one foot back and lower that knee gently onto the towel. You're in a half-kneel.",
    "Bring the other knee down if it's comfortable. Both hands on the chair seat.",
    "To rise: bring one foot forward, flat on the floor (half-kneel).",
    "Push down through the front foot and your hands on the chair, and stand up. Stand still a moment before you walk."],
   ["Hands on the chair the whole time.", "Slow down. Up is a push, not a jump."],
   "Breathe out as you push up.",
   "Only the first step: lower into a half-kneel on the towel and come back up, holding the chair. Or skip the floor and do sit-to-stands.",
   "Iron: from kneeling, sit down onto the floor beside the chair, then roll to your knees and rise with the chair. Only with someone home.",
   [CONTRA["floor_transfer"], "New knee? Kneeling may not be allowed yet. Ask your surgeon.", STAND_SLOW], ["floor_transfer", "standing_up_fast"], ["E45", "E08"])

ex("suitcase_lift", "Suitcase lift (one-hand hinge)", "A jug or bag; sturdy chair against a wall; counter",
   "Stand beside a chair with a jug on the seat next to your right foot. Left hand can rest on the counter.",
   ["Push your hips back with a long back and bend your knees a little.",
    "Grip the jug handle and stand up tall, squeezing your buttocks.",
    "Lower it back to the seat the same way. Do all reps, then switch sides."],
   ["Hips back. Long back.", "Don't lean toward the jug. Stay square."],
   "Breathe out as you stand.",
   "A lighter jug, and lift it from a higher surface like the counter's edge of a table.",
   "A heavier bag, or lift from the bottom step instead of the chair.",
   ["Osteoporosis or a past spine fracture: long back always, never round to reach."], [], ["E40", "E02"])

ex("band_row", "Seated band row", "Resistance band with a door anchor (door closed, locked, opening away from you); chair",
   CHAIR_SETUP + " Face the closed door, band anchored at chest height, one end in each hand, arms straight.",
   ["Pull your elbows back past your ribs.", "Squeeze your shoulder blades together.", "Return slowly."],
   ["Elbows close to your body.", "Tall chest, shoulders down."],
   "Breathe out as you pull.",
   "Sit closer to the door so the band is slacker, or do the towel pull-apart.",
   "Scoot back for more tension, or pause 2 seconds with elbows back.",
   ["Check the band for nicks before every use. Door must open away from you and be locked."], [], ["E01", "E02"])

ex("band_pull_apart", "Band pull-apart", "Light resistance band; chair",
   CHAIR_SETUP + " Sit tall. Hold the band in front of your chest, hands shoulder-width apart.",
   ["Pull the band apart toward your chest by opening your arms.", "Squeeze your shoulder blades.", "Return slowly."],
   ["Shoulders down.", "Slow on the way back."],
   "Breathe out as you pull apart.",
   "Hands wider apart on the band (less tension), or the towel pull-apart.",
   "Hands closer together, or a 2-second squeeze.",
   [], [], ["E01"])

ex("stair_climb", "Stair practice with the rail", "Stairs with a handrail, good light",
   "Stand at the bottom of the stairs. One hand on the rail the whole time. Shoes on, no clutter on the steps.",
   ["Walk up one step at a time at a steady pace, whole foot on each step.",
    "At the top, turn carefully, holding the rail.",
    "Walk down, leading with your stronger leg if one is sore, rail in hand."],
   ["Whole foot on the step.", "Rail hand never lets go."],
   "Breathe steadily. Rest at the top as long as you like.",
   "Just the bottom 3 steps, up and down.",
   "Two flights, or carry a light bag in the free hand.",
   ["Chest pain or unusual breathlessness on stairs: stop, sit, and call your doctor."], [], ["E13"])

ex("pelvic_tilt_bed", "Pelvic tilt on the bed", "Your bed",
   "Lie on your back on your bed, knees bent, feet flat.",
   ["Gently flatten your lower back into the mattress by tightening your belly.",
    "Hold two seconds.", "Relax back to your natural curve."],
   ["Small movement.", "Belly tightens, bottom stays down."],
   "Breathe out as you flatten.",
   "An even smaller movement, one-second hold.",
   "Hold five seconds.",
   ["Osteoporosis or a past spine fracture: keep it small and gentle.", STAND_SLOW], ["standing_up_fast"], ["E30", "E40"])

ex("clam_bed", "Side-lying clamshell on the bed", "Your bed",
   "Lie on your side on the bed, knees bent, head on a pillow, hips stacked.",
   ["Keeping your feet together, lift your top knee a few inches.",
    "Pause.", "Lower slowly. Do all reps, then turn over."],
   ["Hips stay stacked. Don't roll back.", "Small and controlled."],
   "Breathe out as you lift.",
   "Smaller lift.",
   "Loop a light band above your knees.",
   ["New hip? Side-lying may not be allowed yet; ask your surgeon.", STAND_SLOW], ["standing_up_fast"], ["E30"])

ex("counter_side_plank", "Side lean at the counter", "Kitchen counter",
   "Stand side-on to the counter, about a foot away. Put your forearm on the counter edge.",
   ["Lean your body into your forearm in a straight line, feet together.",
    "Hold, keeping your hips from sagging.", "Stand up tall. Switch sides."],
   ["Straight line from head to heels.", "Keep talking. Your breathing never stops."],
   "Breathe normally the whole time. Count out loud.",
   "Stand closer to the counter, or hold for 5 seconds.",
   "Step farther away, or hold up to 20 seconds.",
   [CONTRA["isometric_hold"]], ["isometric_hold"], ["E30"])

ex("pallof_press", "Band press-out (anti-twist)", "Resistance band anchored at chest height in a closed, locked door; or a partner holding it",
   "Stand side-on to the door, band in both hands at your chest, feet hip-width, soft knees. Chair behind you.",
   ["Press your hands straight out in front of your chest.",
    "Don't let the band turn you. Hold two seconds.", "Bring your hands back. Do all reps, then face the other way."],
   ["Stay square. The band pulls, you don't turn.", "Ribs down."],
   "Breathe out as you press.",
   "Do it seated, or stand closer to the door.",
   "Step farther from the door, or hold 5 seconds.",
   ["Door must open away from you and be locked."], [], ["E30"])

ex("suitcase_carry", "One-side carry", "One grocery bag or jug; clear hallway along a counter",
   "Hold one bag in one hand at your side. Clear path. Free hand can trail along the counter.",
   ["Stand tall. Don't lean away from the bag.", "Walk slowly for the set time.", "Set it down with a hinge. Switch hands."],
   ["Tall like a lamppost.", "Shoulders level."],
   "Breathe steadily. You should be able to talk.",
   "A lighter bag, free hand on the counter the whole time.",
   "A heavier bag, or a longer walk.",
   ["Pick up and put down with a hinge. Never round your back to lift."], [], ["E30", "E07"])

ex("knee_rock_bed", "Knee rocks on the bed", "Your bed",
   "Lie on your back on the bed, knees bent, feet flat together, arms out to the sides.",
   ["Let both knees drift gently to the right, only as far as comfortable.",
    "Bring them back to the middle.", "Drift to the left."],
   ["Small and slow.", "Shoulders stay on the bed."],
   "Breathe out as the knees drift.",
   "A tiny movement, a few inches.",
   "Pause for one slow breath on each side.",
   [CONTRA["spinal_twist_end_range"], STAND_SLOW], ["spinal_twist_end_range", "standing_up_fast"], ["E30", "E40"])

ex("toe_walk", "Toe walk along the counter", "Kitchen counter",
   "Stand at one end of the counter, one hand resting on it.",
   ["Rise onto the balls of your feet.", "Walk 10 small steps along the counter on your toes.", "Lower your heels, turn carefully, walk back."],
   ["Tall.", "Small steps."],
   "Breathe steadily.",
   "Heel raises in place instead.",
   "Hand hovering, still right next to the counter.",
   [], [], ["E13"])

ex("heel_walk", "Heel walk along the counter", "Kitchen counter",
   "Stand at one end of the counter, one hand resting on it.",
   ["Lift your toes and walk on your heels, 10 small steps.", "Turn carefully, walk back."],
   ["Toes up.", "Small steps. Hand on the counter."],
   "Breathe steadily.",
   "Toe lifts in place, holding the counter.",
   "20 steps.",
   [], [], ["E13"])

ex("backward_walk", "Backward walk along the counter", "Kitchen counter, clear floor",
   "Stand at one end of the counter, one hand resting on it the whole time. Check the path behind you is clear.",
   ["Take normal-size steps backward, toe then heel.", "10 steps.", "Stop, then walk forward to the start."],
   ["Hand stays on the counter.", "Slow. Look where you're going first."],
   "Breathe steadily.",
   "Five small steps.",
   "Ten steps, slower.",
   ["Only ever with a hand resting on the counter."], [], ["E13"])

ex("step_over", "Step over a rolled towel", "Kitchen counter, a rolled bath towel",
   "Lay a rolled towel on the floor alongside the counter. Stand beside it, one hand on the counter.",
   ["Step over the towel sideways with the near foot, then the other.", "Step back over.", "Turn around and repeat facing the other way."],
   ["Lift the knee. Clear the towel.", "Hand on the counter."],
   "Breathe steadily.",
   "A flat towel instead of rolled.",
   "Step over forward and back, still holding the counter.",
   [], [], ["E13"])

ex("brush_knee", "Brush knee (tai chi, simplified)", "Space to stand near the counter; chair behind you",
   "Stand with feet hip-width, knees soft, counter within reach.",
   ["Step forward with the left foot, heel first, into a short stance.",
    "As you shift your weight forward, the left hand brushes past the left knee and the right hand pushes forward slowly.",
    "Shift back, step back to center. Switch sides."],
   ["Short step, not a lunge.", "Weight moves slowly from back foot to front foot."],
   "Breathe out as you push forward.",
   "Arms only, feet together, one hand on the counter.",
   "Four steps across the room and back, near the counter.",
   [], [], ["E15", "E17"])

ex("parting_mane", "Parting the horse's mane (tai chi, simplified)", "Space to stand near the counter; chair behind you",
   "Stand with feet hip-width, knees soft, counter within reach.",
   ["Imagine holding a ball at your chest, right hand on top.",
    "Step the left foot forward at a slight angle and shift your weight into it as the left arm sweeps up to shoulder height and the right hand presses down by the hip.",
    "Shift back, bring the ball back, switch sides."],
   ["Short step.", "Slow like honey."],
   "Breathe out as the arm sweeps up.",
   "Arms only, feet together, holding the counter with one hand.",
   "Step forward across the room, left then right, near the counter.",
   [], [], ["E15", "E17"])

ex("big_steps", "Big-step walking drill", "Hallway or along the counter",
   "Stand at one end of a hallway or the counter. One hand can trail along the wall or counter.",
   ["Walk 10 steps a little longer than your normal step.", "Land on your heel, roll through, push off your toes.", "Swing your arms. Turn carefully, walk back normally."],
   ["Heel, roll, push.", "Tall. Eyes ahead."],
   "Breathe steadily.",
   "Normal-length steps, hand on the counter.",
   "20 steps, a little faster.",
   [], [], ["E10", "E13"])

ex("finger_spread", "Finger spreads", "A thick rubber band (optional); table",
   "Sit at a table, forearms resting on it.",
   ["Spread all five fingers as wide as comfortable.", "Hold two seconds.", "Bring them back together."],
   ["Spread, don't force.", "Slow."],
   "Breathe normally.",
   "No band, smaller spread.",
   "Loop a thick rubber band around the fingers and thumb and spread against it.",
   ["Hand arthritis: stay in the comfortable range. Mild ache that settles by tomorrow is okay; a hot, swollen joint is for your doctor."], [], ["E59"])

ex("fist_flat", "Fist, flat, hook", "Table",
   "Sit at a table, forearm resting on it, hand relaxed.",
   ["Make a gentle fist, thumb outside.", "Open to a flat hand, fingers straight.", "Bend just the finger tips into a hook. Back to flat."],
   ["Gentle fist, not a squeeze.", "Move slowly through each shape."],
   "Breathe normally.",
   "Smaller movements, fewer reps.",
   "Hold each shape for 3 seconds.",
   ["Hand arthritis: stay in the comfortable range."], [], ["E59"])

ex("thumb_touch", "Thumb touches", "Table",
   "Sit, forearm resting on a table.",
   ["Touch your thumb to the tip of each finger, one at a time, making an O.", "Then back from little finger to index."],
   ["Round O shapes.", "Slow and exact."],
   "Breathe normally.",
   "Touch the pad of each finger instead of the tip.",
   "Press each touch gently for 2 seconds.",
   [], [], ["E59"])

ex("wrist_curl", "Wrist curls with a bottle", "A full water bottle; table",
   "Sit, forearm resting on the table, hand over the edge, palm up, holding the bottle.",
   ["Curl your wrist up.", "Lower slowly.", "Then turn palm down and lift the back of the hand."],
   ["Forearm stays on the table.", "Slow down."],
   "Breathe out as you lift.",
   "An empty bottle, or no weight.",
   "A half-full half-gallon jug.",
   [], [], ["E01"])

ex("book_pinch", "Book pinch hold", "A paperback book",
   "Sit or stand tall. Hold a paperback by its spine between your thumb and fingers, letting it hang.",
   ["Pinch and hold.", "Put it down before your grip gives out.", "Switch hands."],
   ["Fingers straight, thumb opposite.", "Shoulders relaxed."],
   "Breathe normally. Count out loud.",
   "A thinner, lighter book, 5 seconds.",
   "A thicker book, up to 20 seconds.",
   ["Hand arthritis flaring today: skip it and do finger spreads."], [], ["E07"])

ex("ball_squeeze", "Soft ball squeeze", "A soft ball or rolled sock",
   "Sit, holding a soft ball in one hand.",
   ["Squeeze gently for 3 seconds.", "Relax fully.", "Switch hands after the set."],
   ["Whole hand squeezes.", "Relax all the way between reps."],
   "Breathe out as you squeeze.",
   "A rolled sock, gentle squeeze.",
   "A firmer ball, 5-second squeeze.",
   ["Hand arthritis: squeeze gently, never to pain above 3 out of 10."], [], ["E07", "E59"])

ex("jar_twist", "Jar lid practice", "An empty jar with a screw lid, a dish towel",
   "Sit at a table. Hold the jar steady with one hand, a towel under it so it doesn't slide.",
   ["Screw the lid on firmly.", "Twist it open.", "Switch hands for holding and turning."],
   ["Grip with the whole hand.", "Turn from the forearm, not just the fingers."],
   "Breathe out as you twist.",
   "A loose lid.",
   "Wrap a rubber band around the lid and screw it tighter each week.",
   [], [], ["E07"])

ex("hand_stretch", "Prayer and wrist stretch", "None",
   "Sit tall.",
   ["Press your palms together in front of your chest.", "Lower your hands a little until you feel a gentle stretch in the wrists.", "Hold. Then shake the hands out."],
   ["Gentle stretch only.", "Shoulders down."],
   "Breathe slowly.",
   "Smaller stretch, 10 seconds.",
   "Hold 20 seconds.",
   ["Carpal tunnel symptoms (numb, tingling fingers) that get worse: skip it and tell your doctor."], [], ["E59"])


def get(i):
    return EX[i]

# Short on-screen regression labels (≤ 6 words) for video overlays (M-02)
EASY_SHORT = {
    "floor_practice": "Half-kneel only, or chair stands", "suitcase_lift": "Lighter jug, higher surface",
    "band_row": "Closer to the door, or towel", "band_pull_apart": "Hands wider on the band",
    "stair_climb": "Bottom 3 steps only", "pelvic_tilt_bed": "Smaller, one-second hold",
    "clam_bed": "Smaller lift", "counter_side_plank": "Closer to counter, 5 s",
    "pallof_press": "Seated, closer to the door", "suitcase_carry": "Lighter bag, hand on counter",
    "knee_rock_bed": "A tiny movement", "toe_walk": "Heel raises in place", "heel_walk": "Toe lifts in place",
    "backward_walk": "Five small steps", "step_over": "Flat towel", "brush_knee": "Arms only, feet together",
    "parting_mane": "Arms only, hold the counter", "big_steps": "Normal steps, hand on counter",
    "finger_spread": "Smaller spread, no band", "fist_flat": "Smaller movements", "thumb_touch": "Finger pads, not tips",
    "wrist_curl": "Empty bottle", "book_pinch": "Thinner book, 5 seconds", "ball_squeeze": "Rolled sock, gentle",
    "jar_twist": "A loose lid", "hand_stretch": "Smaller stretch, 10 s",
    "sit_to_stand": "Higher seat, hands on thighs", "power_stand": "Normal speed, hands on thighs",
    "wall_sit_high": "Only 2 inches down, 10 s", "heel_raise": "Seated, or rise halfway",
    "step_up": "Toe taps, hand on rail", "split_squat": "Smaller step, 2-inch dip",
    "hip_hinge": "Smaller hinge, hands stay down", "side_step": "Fewer, slower steps",
    "seated_knee_ext": "Straighten halfway", "seated_march": "Lift feet one inch",
    "standing_march": "Sit and march", "wall_pushup": "Closer to wall, half range",
    "counter_pushup": "Wall push-ups", "jug_row": "Towel pull or lighter jug",
    "towel_row": "Pull gently, 1-second hold", "bottle_curl": "One arm, or empty bottles",
    "seated_press": "One arm, press at a slant", "towel_wring": "Squeeze a rolled sock",
    "carry": "One light bag, hand on counter", "tandem_stand": "Half-step, both hands down",
    "single_leg": "Toe stays on the floor", "heel_toe_walk": "Feet apart, hold the counter",
    "weight_shift": "Do it seated", "clock_reach": "Smaller reaches, front and side",
    "sit_stand_nohands": "Hands on thighs", "ankle_pumps": "Smaller movements",
    "shoulder_rolls": "Just shrug and let go", "neck_nods": "Even smaller movements",
    "chin_tuck": "Smaller, 1-second hold", "wall_slide": "Walk fingertips up the wall",
    "seated_rotation": "Smaller turns", "chest_lift": "Smaller lift",
    "calf_stretch": "Smaller step back", "hip_flexor": "Smaller step, both hands down",
    "hamstring_seated": "Lean only an inch", "figure4": "Ankle on shin, or skip crossing",
    "bed_bridge": "Squeeze without lifting", "standing_birddog": "Leg only, both hands down",
    "cyclic_sigh": "Just slow nose breathing", "breath_46": "In for 3, out for 4",
    "sky_lift": "Seated, to shoulder height", "draw_bow": "Seated, arms only",
    "heaven_earth": "Seated, to shoulder height", "owl_look": "Turn the eyes more",
    "fists": "Seated, same arm movement", "heel_drop": "Slow lower, no drop",
    "cloud_hands": "Seated, or one hand on counter", "walk": "Indoors, touching the counter",
    "seated_chest_press": "Empty hands, one arm", "seated_hinge": "Smaller tip forward",
}
