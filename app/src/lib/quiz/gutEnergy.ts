/**
 * Quiz B "The Gut & Energy Check" (Sun Yoon's quiz) — scoring exactly as FUNNEL.md §3.2.
 * Answers are option indexes. Pure and unit tested.
 */

export type RedFlag =
  | "weight_loss"
  | "blood_stool"
  | "swallowing"
  | "vomiting"
  | "bowel_change"
  | "belly_pain";

export interface GutEnergyAnswers {
  redFlags: RedFlag[]; // empty = "None of these"
  ageBand: number; // Q1 index 0..3
  weight: number; // Q2 index 0..4, 5 = skip
  breakfast: number; // Q3
  proteinMeals: number; // Q4
  tiredWhen: number; // Q5
  afterMeal: number; // Q6
  bloating: number; // Q7
  bathroom: number; // Q8
  plants: number; // Q9
  fluids: number; // Q10
  sleep: number; // Q11
  caffeine: number; // Q12
  alcohol: number; // Q13
  chewing: number; // Q14
  manyMeds: boolean; // Q15 (not scored)
}

export type Dimension = "fuel" | "rhythm" | "flow" | "rest" | "comfort";
export type GutProfile = "b1" | "b2" | "b3" | "b4" | "b5" | "b6";

const Q3 = [0, 3, 0, 1];
const Q4 = [4, 2, 1, 0];
const Q5_RHYTHM = [1, 0, 2, 0, 3];
const Q5_REST_ADJ = [0, 0, 0, -1, 0];
const Q6 = [0, 2, 4];
const Q7 = [0, 2, 4];
const Q8 = [4, 2, 0, 1];
const Q9 = [4, 3, 1, 0];
const Q10 = [3, 2, 1, 0];
const Q11 = [4, 1, 1, 0];
const Q12 = [3, 1, 0, 3];
const Q13 = [3, 2, 1, 0];
const Q14 = [3, 1, 0];

const at = (t: number[], i: number) => t[Math.min(t.length - 1, Math.max(0, Math.round(i)))] ?? 0;

export const DIMENSION_ORDER: Dimension[] = ["fuel", "rhythm", "flow", "rest", "comfort"];

export const PROFILE_FOR: Record<Dimension, GutProfile> = {
  fuel: "b1",
  rhythm: "b2",
  flow: "b3",
  rest: "b4",
  comfort: "b5",
};

export interface GutEnergyResult {
  stop: boolean;
  scores: Record<Dimension, number>;
  display: Record<Dimension, number>;
  lowest: Dimension | null;
  profile: GutProfile | null;
  protein: { lowG: number; highG: number } | null;
  pharmacistNote: boolean;
}

const WEIGHT_MID_LB = [120, 145, 175, 205, 235];

export function proteinTarget(weightIndex: number): { lowG: number; highG: number } | null {
  const lb = WEIGHT_MID_LB[weightIndex];
  if (lb === undefined) return null;
  const kg = lb / 2.2046;
  const round5 = (g: number) => Math.round(g / 5) * 5;
  return { lowG: round5(kg * 1.0), highG: round5(kg * 1.2) };
}

export function scoreGutEnergy(a: GutEnergyAnswers): GutEnergyResult {
  const zero = { fuel: 0, rhythm: 0, flow: 0, rest: 0, comfort: 0 };
  if (a.redFlags.length > 0) {
    return { stop: true, scores: zero, display: zero, lowest: null, profile: null, protein: null, pharmacistNote: false };
  }
  const fuel = ((at(Q3, a.breakfast) + at(Q4, a.proteinMeals)) / 7) * 10;
  const rhythm = ((at(Q5_RHYTHM, a.tiredWhen) + at(Q6, a.afterMeal)) / 7) * 10;
  const flow = ((at(Q8, a.bathroom) + at(Q9, a.plants) + at(Q10, a.fluids)) / 11) * 10;
  const restRaw = at(Q11, a.sleep) + at(Q12, a.caffeine) + at(Q13, a.alcohol) + at(Q5_REST_ADJ, a.tiredWhen);
  const rest = (Math.max(0, restRaw) / 10) * 10;
  const comfort = ((at(Q7, a.bloating) + at(Q14, a.chewing)) / 7) * 10;
  const scores: Record<Dimension, number> = { fuel, rhythm, flow, rest, comfort };

  let lowest: Dimension = "fuel";
  for (const d of DIMENSION_ORDER) {
    if (scores[d] < scores[lowest]) lowest = d; // strict < keeps the tie-break order
  }
  const allStrong = DIMENSION_ORDER.every((d) => scores[d] >= 7);
  const display = Object.fromEntries(DIMENSION_ORDER.map((d) => [d, Math.round(scores[d])])) as Record<Dimension, number>;

  return {
    stop: false,
    scores,
    display,
    lowest: allStrong ? null : lowest,
    profile: allStrong ? "b6" : PROFILE_FOR[lowest],
    protein: proteinTarget(a.weight),
    pharmacistNote: a.manyMeds,
  };
}
