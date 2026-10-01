"""RT01: the guided monthly Strength Age retest (app video). Six tests from E11/E49/E50/E51."""
from sessions_spec import seg, same


def T(r, s, st, i):
    return dict(rebuild=r, steady=s, strong=st, iron=i)


RETEST = dict(n=0, weekday="Any (day 30, 60, 90...)", type="Guided retest", title="Your Strength Age retest", set="SET-KITCHEN", wardrobe="C-TRAIN-B",
    evidence=["E06", "E09", "E11", "E49", "E50", "E51", "E40", "E43"],
    swaps=dict(sore_knee="Skip the step test and the Up and Go today; do them another day.", sore_back="Skip the sit-and-reach.",
               low_energy="Do the chair stand and balance only; finish the rest tomorrow."),
    segments=[
    seg("Welcome", "intro", 45, vo=["Retest day. Same chair, same shoes, same time of day as last time.", "Six tests. About twelve minutes with rests. A helper is welcome.",
                                    "These are fitness checks from senior fitness research. Not a medical test.", "Chest pain, dizziness, unusual breathlessness: stop, and call your doctor."],
        ost=["Strength Age retest", "Not a medical test", "Stop if chest pain or dizziness"]),
    seg("Test 1: 30-second chair stand", "block", 75, T(("sit_to_stand", "easier", "30 seconds, hands allowed (write H)"), ("sit_to_stand", "main", "30 seconds, arms crossed"),
                                                        ("sit_to_stand", "main", "30 seconds, arms crossed"), ("sit_to_stand", "main", "30 seconds, arms crossed")),
        vo=["Chair against the wall. Sit in the middle. Arms crossed.", "Three, two, one, go. All the way up, all the way down.", "Breathe out as you stand. Ten seconds left.", "Stop. Enter your number."],
        ost=["Count full stands"]),
    seg("Test 2: four-stage balance", "block", 105, T(("tandem_stand", "easier", "Stages 1–2, both hands hovering over the counter"), ("tandem_stand", "main", "Stages 1–4, hand hovering"),
                                                      ("tandem_stand", "main", "Stages 1–4, hand hovering"), ("tandem_stand", "main", "Stages 1–4, hand hovering")),
        vo=["At the counter. Hand hovering just above it. Helper beside you.", "Feet together, ten seconds. Then half step. Then heel to toe. Then one foot.",
            "Touch the counter or move your feet, and that stage is over. Breathe.", "Enter the last stage you held for ten seconds."],
        ost=["Stop at the first stage you can't hold"]),
    seg("Test 3: arm curl", "block", 60, same("bottle_curl", "30 seconds, seated, same weight as last time", "30 seconds, 5 lb (women) / 8 lb (men) or your usual jug", "30 seconds, same weight as last time", "30 seconds, same weight as last time", ("main",) * 4),
        vo=["Sit tall. Weight in your stronger hand. Same weight as last time.", "Go. Full curls. Elbow by your side.", "Breathe out as you curl. Stop. Enter your number."]),
    seg("Test 4: two-minute step test", "block", 150, T(("seated_march", "main", "2 minutes seated march, tracking only"), ("standing_march", "main", "2 minutes, knees to the tape mark, hand on the counter"),
                                                        ("standing_march", "main", "2 minutes, knees to the tape"), ("standing_march", "main", "2 minutes, knees to the tape")),
        vo=["Tape on the counter halfway between your kneecap and hip bone. Hand on the counter.", "March, lifting each knee to the tape. Count the right knee.",
            "Slow down or rest any time. The clock keeps running.", "Breathe. Heart condition or breathless easily? Skip this one until your doctor says okay.", "Stop. Keep walking slowly for a minute. Don't sit straight away."],
        ost=["Count right-knee lifts", "Skip if breathless easily"]),
    seg("Test 5: chair sit-and-reach", "block", 70, same("hamstring_seated", "Skip if seated reach is uncomfortable", "2 tries, best one, long back", "2 tries, best one, long back", "2 tries, best one, long back", ("easier", "main", "main", "main")),
        vo=["Front edge of the chair. One leg straight, heel down.", "Long back. Hinge forward from the hips. Hold two seconds.", "Osteoporosis or a past spine fracture: skip this one.", "Breathe out as you reach. Measure fingertips to shoe. Enter your best."],
        ost=["Osteoporosis: skip this test"]),
    seg("Test 6: Timed Up and Go", "block", 75, T(("walk", "easier", "Only with your walker or cane and a helper beside you"), ("walk", "main", "Stand, walk 10 feet at normal pace, turn, back, sit"),
                                                  ("walk", "main", "Stand, walk 10 feet at normal pace, turn, back, sit"), ("walk", "main", "Stand, walk 10 feet at normal pace, turn, back, sit")),
        vo=["Chair against the wall. Tape on the floor ten feet away. Helper with the timer, walking beside you.", "Normal pace. Not a race. Go.",
            "Stand, walk to the tape, turn, walk back, sit. Breathe.", "Twelve seconds or more? Mention it to your doctor. Balance training is exactly what helps."],
        ost=["Normal pace, not a race", "12 s or more: tell your doctor"]),
    seg("Your result", "close", 45, vo=["The app shows your Strength Age and your chart.", "Up? Good. Same? Also fine. It's a month.", "A number that moves when you do the work. Same time tomorrow."],
        ost=["Strength Age: a fitness estimate, not a diagnosis"]),
])
