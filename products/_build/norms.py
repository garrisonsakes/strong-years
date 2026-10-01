"""Senior Fitness Test normal ranges (middle 50%), E49; CDC STEADI tools, E11/E50/E51."""
BANDS = ["60–64", "65–69", "70–74", "75–79", "80–84", "85–89", "90–94"]

CHAIR = {"W": ["12–17", "11–16", "10–15", "10–15", "9–14", "8–13", "4–11"],
         "M": ["14–19", "12–18", "12–17", "11–17", "10–15", "8–14", "7–12"]}
CHAIR_STEADI_BELOW = {"W": ["under 12", "under 11", "under 10", "under 10", "under 9", "under 8", "under 4"],
                      "M": ["under 14", "under 12", "under 12", "under 11", "under 10", "under 8", "under 7"]}
ARM = {"W": ["13–19", "12–18", "12–17", "11–17", "10–16", "10–15", "8–13"],
       "M": ["16–22", "15–21", "14–21", "13–19", "13–19", "11–17", "10–14"]}
STEP = {"W": ["75–107", "73–107", "68–101", "68–100", "60–91", "55–85", "44–72"],
        "M": ["87–115", "86–116", "80–110", "73–109", "71–103", "59–91", "52–86"]}
REACH = {"W": ["−0.6 to +4.8", "−0.5 to +4.5", "−1.0 to +4.0", "−1.5 to +3.5", "−2.0 to +3.0", "−2.5 to +2.5", "−4.5 to +1.0"],
         "M": ["−2.5 to +4.0", "−3.0 to +3.0", "−3.5 to +2.5", "−4.0 to +2.0", "−5.5 to +1.5", "−5.5 to +0.5", "−6.5 to −0.5"]}
# Strength Age chair-stand midpoints (middle of the normal range), same method as FUNNEL.md §3.1
MID = {"W": [14.5, 13.5, 12.5, 12.5, 11.5, 10.5, 7.5], "M": [16.5, 15.0, 14.5, 14.0, 12.5, 11.0, 9.5]}
BAL = [("Couldn't hold position 1", "+10"), ("Held position 1 only (feet together)", "+8"),
       ("Held position 2 (half step)", "+5"), ("Held position 3 (heel to toe)", "0 (age 80+: −2)"),
       ("Held position 4 (one foot)", "−3 (age 80+: −5)")]


def table(name, data, unit=""):
    rows = ["| Age | Women | Men |", "|---|---|---|"]
    for i, b in enumerate(BANDS):
        rows.append(f"| {b} | {data['W'][i]}{unit} | {data['M'][i]}{unit} |")
    return "\n".join(rows) + "\n"


def mid_table():
    rows = ["| Age | Women midpoint | Men midpoint |", "|---|---|---|"]
    for i, b in enumerate(BANDS):
        rows.append(f"| {b} | {MID['W'][i]} | {MID['M'][i]} |")
    return "\n".join(rows) + "\n"
