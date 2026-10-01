import { describe, expect, it } from "vitest";
import fs from "node:fs";
import path from "node:path";
import {
  CHAIR_NORMS,
  balanceComponent,
  bandFor,
  chairComponent,
  chairMidpoint,
  computeStrengthAgeNumber,
  scoreStrengthAge,
  selfReportComponent,
  type StrengthAgeAnswers,
} from "@/lib/quiz/strengthAge";

const base: StrengthAgeAnswers = {
  taker: "self",
  sex: "woman",
  age: 70,
  safety: [],
  mobility: "none",
  chairReps: 12,
  usedHands: false,
  balanceStage: 3,
  jar: 1,
  carry: 1,
  floor: 1,
  stairs: 1,
  walking: 1,
  strengthFreq: 2,
  aches: ["nothing"],
};

describe("chair-stand norms", () => {
  it("uses the 60–64 band under 60 and the right midpoints", () => {
    expect(bandFor(52).label).toBe("60–64");
    expect(bandFor(72).label).toBe("70–74");
    expect(bandFor(93).label).toBe("90–94");
    expect(bandFor(95).label).toBe("90–94");
    expect(chairMidpoint(72, "woman")).toBe(12.5);
    expect(chairMidpoint(72, "man")).toBe(14.5);
    expect(chairMidpoint(72, "na")).toBe(13.5);
  });

  it("chair component = −2.5 × (reps − midpoint), clamped ±12, hands → at least +8", () => {
    expect(chairComponent(16.5, 72, "woman", false)).toBe(-10);
    expect(chairComponent(30, 72, "woman", false)).toBe(-12);
    expect(chairComponent(0, 72, "woman", false)).toBe(12);
    expect(chairComponent(16, 72, "woman", true)).toBe(8);
  });

  it("balance component including the 80+ adjustment", () => {
    expect([0, 1, 2, 3, 4].map((s) => balanceComponent(s, 70))).toEqual([10, 8, 5, 0, -3]);
    expect([3, 4].map((s) => balanceComponent(s, 82))).toEqual([-2, -5]);
  });

  it("self-report sums the item points × 0.5", () => {
    expect(selfReportComponent({ jar: 0, carry: 0, floor: 0, stairs: 0, walking: 0, strengthFreq: 0 })).toBe(-6);
    expect(selfReportComponent({ jar: 3, carry: 3, floor: 3, stairs: 3, walking: 3, strengthFreq: 3 })).toBe(10.5);
    expect(selfReportComponent({ jar: 1, carry: 1, floor: 4, stairs: 1, walking: 1, strengthFreq: 2 })).toBe(1);
  });
});

describe("scoreStrengthAge", () => {
  it("an average 70-year-old woman scores within a year or two of her age (P2)", () => {
    const r = scoreStrengthAge(base);
    expect(r.kind).toBe("tested");
    expect(r.strengthAge).toBe(71); // 12 stands vs a 12.5 midpoint → +1.25 years
    expect(r.profile).toBe("p2");
    expect(r.typical).toEqual([10, 15]);
  });

  it("a strong result is younger and routes to P1 Steady Oak", () => {
    const r = scoreStrengthAge({ ...base, chairReps: 17, balanceStage: 4, jar: 0, carry: 0, floor: 0, stairs: 0, walking: 0, strengthFreq: 0 });
    expect(r.strengthAge).toBeLessThanOrEqual(65);
    expect(r.profile).toBe("p1");
    expect(r.track).toBe("strong");
  });

  it("a weak result is older and routes to P5 Quiet Slide", () => {
    const r = scoreStrengthAge({ ...base, chairReps: 9, balanceStage: 3, carry: 2, stairs: 1 });
    expect(r.gap!).toBeGreaterThanOrEqual(5);
    expect(r.profile).toBe("p5");
  });

  it("balance stage ≤ 2 routes to P3 Wobbly Foundations before anything else", () => {
    const r = scoreStrengthAge({ ...base, chairReps: 17, balanceStage: 2 });
    expect(r.profile).toBe("p3");
    expect(r.flags.balance).toBe(true);
  });

  it("joint aches + hard stairs route to P4 Stiff Engine", () => {
    const r = scoreStrengthAge({ ...base, aches: ["knees"], stairs: 2 });
    expect(r.flags.joint).toBe(true);
    expect(r.profile).toBe("p4");
  });

  it("clamps to [age−15, age+20] and never below 40", () => {
    expect(computeStrengthAgeNumber({ age: 70, sex: "woman", chairReps: 40, usedHands: false, balanceStage: 4, selfReport: -6 })).toBe(55);
    expect(computeStrengthAgeNumber({ age: 70, sex: "woman", chairReps: 0, usedHands: true, balanceStage: 0, selfReport: 12 })).toBe(90);
    expect(computeStrengthAgeNumber({ age: 50, sex: "man", chairReps: 40, usedHands: false, balanceStage: 4, selfReport: -6 })).toBe(40);
  });

  it("safety screen: any red flag → Safe Mode, no number, P6", () => {
    const r = scoreStrengthAge({ ...base, safety: ["chest"] });
    expect(r.kind).toBe("safe_mode");
    expect(r.strengthAge).toBeNull();
    expect(r.profile).toBe("p6");
    expect(r.safeModeReasons[0]).toMatch(/chest/);
  });

  it("walker or wheelchair → Safe Mode with the Rebuild track", () => {
    const r = scoreStrengthAge({ ...base, mobility: "walker" });
    expect(r.kind).toBe("safe_mode");
    expect(r.track).toBe("rebuild");
  });

  it("fewer than 5 stands or couldn't hold stage 1 → P6", () => {
    expect(scoreStrengthAge({ ...base, chairReps: 4 }).profile).toBe("p6");
    expect(scoreStrengthAge({ ...base, balanceStage: 0 }).profile).toBe("p6");
  });

  it("taking it for someone else → questionnaire-only estimate clamped to ±10", () => {
    const r = scoreStrengthAge({ ...base, taker: "other", jar: 3, carry: 3, floor: 3, stairs: 3, walking: 3, strengthFreq: 3 });
    expect(r.kind).toBe("questionnaire_only");
    expect(r.strengthAge).toBe(80);
    expect(r.adultChild).toBe(true);
  });

  it("flags the under-60 comparison note", () => {
    expect(scoreStrengthAge({ ...base, age: 55 }).under60Note).toBe(true);
  });
});

describe("CHAIR_NORMS match FUNNEL.md §3.1 exactly", () => {
  const md = fs.readFileSync(path.join(__dirname, "..", "..", "..", "FUNNEL.md"), "utf8");
  const section = md.slice(md.indexOf("**Chair-stand reference midpoints**"));
  const rows = [...section.matchAll(/^\| (\d{2})–(\d{2}) \| ([\d.]+) \| ([\d.]+) \| < (\d+) \/ < (\d+) \|$/gm)].slice(0, 7);
  const ranges = (sex: "women" | "men") => {
    const m = section.match(new RegExp(`\\b${sex} ((?:\\d+–\\d+(?:, )?)+)`))!;
    return m[1]!.split(", ").map((r) => r.split("–").map(Number) as [number, number]);
  };

  it("has the same 7 bands in order", () => {
    expect(rows).toHaveLength(7);
    expect(CHAIR_NORMS.map((b) => b.label)).toEqual(rows.map((r) => `${r[1]}–${r[2]}`));
  });

  it.each([0, 1, 2, 3, 4, 5, 6])("row %i: midpoints, STEADI cutoffs and Rikli-Jones ranges", (i) => {
    const r = rows[i]!;
    const b = CHAIR_NORMS[i]!;
    expect(b.womenMid).toBe(Number(r[3]));
    expect(b.menMid).toBe(Number(r[4]));
    expect(b.womenCut).toBe(Number(r[5]));
    expect(b.menCut).toBe(Number(r[6]));
    expect(b.womenRange).toEqual(ranges("women")[i]);
    expect(b.menRange).toEqual(ranges("men")[i]);
    // midpoint is the middle of the normal range; the cutoff is its lower bound
    expect((b.womenRange[0] + b.womenRange[1]) / 2).toBe(b.womenMid);
    expect((b.menRange[0] + b.menRange[1]) / 2).toBe(b.menMid);
    expect(b.womenRange[0]).toBe(b.womenCut);
    expect(b.menRange[0]).toBe(b.menCut);
    if (i > 0) expect(b.min).toBe(Number(r[1]));
    if (i < 6) expect(b.max).toBe(Number(r[2]));
  });
});
