import { describe, expect, it } from "vitest";
import { proteinTarget, scoreGutEnergy, type GutEnergyAnswers } from "@/lib/quiz/gutEnergy";

const best: GutEnergyAnswers = {
  redFlags: [],
  ageBand: 2,
  weight: 1,
  breakfast: 1, // 3
  proteinMeals: 0, // 4
  tiredWhen: 4, // rhythm 3
  afterMeal: 2, // 4
  bloating: 2, // 4
  bathroom: 0, // 4
  plants: 0, // 4
  fluids: 0, // 3
  sleep: 0, // 4
  caffeine: 0, // 3
  alcohol: 0, // 3
  chewing: 0, // 3
  manyMeds: false,
};

describe("scoreGutEnergy", () => {
  it("perfect answers score 10 everywhere → B6 Steady Burner", () => {
    const r = scoreGutEnergy(best);
    expect(r.display).toEqual({ fuel: 10, rhythm: 10, flow: 10, rest: 10, comfort: 10 });
    expect(r.profile).toBe("b6");
    expect(r.lowest).toBeNull();
  });

  it("toast-and-coffee breakfast with little protein → B1 Running on Toast", () => {
    const r = scoreGutEnergy({ ...best, breakfast: 0, proteinMeals: 3 });
    expect(r.scores.fuel).toBe(0);
    expect(r.profile).toBe("b1");
  });

  it("post-lunch crash + sitting → B2", () => {
    expect(scoreGutEnergy({ ...best, tiredWhen: 1, afterMeal: 0 }).profile).toBe("b2");
  });

  it("low fibre/fluids → B3; poor sleep → B4; bloating → B5", () => {
    expect(scoreGutEnergy({ ...best, bathroom: 2, plants: 3, fluids: 3 }).profile).toBe("b3");
    expect(scoreGutEnergy({ ...best, sleep: 3, caffeine: 2, alcohol: 3 }).profile).toBe("b4");
    expect(scoreGutEnergy({ ...best, bloating: 0, chewing: 2 }).profile).toBe("b5");
  });

  it("'tired all day' subtracts 1 from Rest and floors at 0", () => {
    const r = scoreGutEnergy({ ...best, tiredWhen: 3, sleep: 3, caffeine: 2, alcohol: 3 });
    expect(r.scores.rest).toBe(0);
  });

  it("ties break in order Fuel, Rhythm, Flow, Rest, Comfort", () => {
    const r = scoreGutEnergy({ ...best, breakfast: 0, proteinMeals: 3, tiredWhen: 1, afterMeal: 0 });
    expect(r.scores.fuel).toBe(0);
    expect(r.scores.rhythm).toBe(0);
    expect(r.profile).toBe("b1");
  });

  it("any red flag stops the quiz with no profile and no offer", () => {
    const r = scoreGutEnergy({ ...best, redFlags: ["blood_stool"] });
    expect(r.stop).toBe(true);
    expect(r.profile).toBeNull();
  });

  it("protein target is 1.0–1.2 g/kg from the weight band midpoint; skipped weight → null", () => {
    expect(proteinTarget(1)).toEqual({ lowG: 65, highG: 80 }); // 145 lb ≈ 65.8 kg
    expect(proteinTarget(5)).toBeNull();
  });

  it("flags the pharmacist note for 5+ medicines", () => {
    expect(scoreGutEnergy({ ...best, manyMeds: true }).pharmacistNote).toBe(true);
  });
});
