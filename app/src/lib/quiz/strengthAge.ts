/**
 * Quiz A "What's your Strength Age?" — scoring exactly as FUNNEL.md §3.1.
 * Pure functions, unit tested in tests/unit/strengthAge.test.ts.
 *
 * Strength Age is a motivational fitness estimate from published senior fitness
 * norms (Rikli & Jones Senior Fitness Test, CDC STEADI cutoffs). It is not a
 * medical test or diagnosis, and the UI says so wherever the number appears.
 */
import type { Sex } from "../db/types";

export type Taker = "self" | "helping" | "other";
export type Mobility = "none" | "cane_some" | "cane_most" | "walker" | "wheelchair";
export type SafetyFlag = "chest" | "dizzy" | "fall" | "surgery" | "doctor_limit";
export type Ache = "knees" | "hips" | "lower_back" | "shoulders" | "hands" | "nothing";

export interface StrengthAgeAnswers {
  taker: Taker;
  sex: Sex;
  age: number;
  safety: SafetyFlag[]; // empty = "None of these"
  mobility: Mobility;
  chairReps?: number | null;
  usedHands?: boolean;
  armCurls?: number | null;
  /** 0 = couldn't hold position 1; 1–4 = last position held for 10 s */
  balanceStage?: number | null;
  jar: number; // Q6 index 0..3
  carry: number; // Q7 index 0..3
  floor: number; // Q8 index 0..4 (4 = "not sure, I avoid the floor")
  stairs: number; // Q9 index 0..3
  walking: number; // Q10 index 0..3
  strengthFreq: number; // Q11 index 0..3
  aches: Ache[];
  goal?: number; // Q13 index
  minutes?: number; // Q14 minutes
}

export type ProfileCode = "p1" | "p2" | "p3" | "p4" | "p5" | "p6";

export interface Band {
  label: string;
  min: number;
  max: number;
  womenMid: number;
  menMid: number;
  womenCut: number;
  menCut: number;
  /** Rikli & Jones "normal range" for display */
  womenRange: [number, number];
  menRange: [number, number];
}

export const CHAIR_NORMS: Band[] = [
  { label: "60–64", min: 0, max: 64, womenMid: 14.5, menMid: 16.5, womenCut: 12, menCut: 14, womenRange: [12, 17], menRange: [14, 19] },
  { label: "65–69", min: 65, max: 69, womenMid: 13.5, menMid: 15.0, womenCut: 11, menCut: 12, womenRange: [11, 16], menRange: [12, 18] },
  { label: "70–74", min: 70, max: 74, womenMid: 12.5, menMid: 14.5, womenCut: 10, menCut: 12, womenRange: [10, 15], menRange: [12, 17] },
  { label: "75–79", min: 75, max: 79, womenMid: 12.5, menMid: 14.0, womenCut: 10, menCut: 11, womenRange: [10, 15], menRange: [11, 17] },
  { label: "80–84", min: 80, max: 84, womenMid: 11.5, menMid: 12.5, womenCut: 9, menCut: 10, womenRange: [9, 14], menRange: [10, 15] },
  { label: "85–89", min: 85, max: 89, womenMid: 10.5, menMid: 11.0, womenCut: 8, menCut: 8, womenRange: [8, 13], menRange: [8, 14] },
  // Oldest published band; age 95 (top of the Q3 picker) also uses it.
  { label: "90–94", min: 90, max: 200, womenMid: 7.5, menMid: 9.5, womenCut: 4, menCut: 7, womenRange: [4, 11], menRange: [7, 12] },
];

export function bandFor(age: number): Band {
  // Under 60: compared with 60–64 (FUNNEL.md Q3).
  return CHAIR_NORMS.find((b) => age >= b.min && age <= b.max) ?? CHAIR_NORMS[CHAIR_NORMS.length - 1]!;
}

export function chairMidpoint(age: number, sex: Sex | null): number {
  const b = bandFor(age);
  if (sex === "woman") return b.womenMid;
  if (sex === "man") return b.menMid;
  return (b.womenMid + b.menMid) / 2;
}

export function chairCutoff(age: number, sex: Sex | null): number {
  const b = bandFor(age);
  if (sex === "woman") return b.womenCut;
  if (sex === "man") return b.menCut;
  return (b.womenCut + b.menCut) / 2;
}

export function typicalRange(age: number, sex: Sex | null): [number, number] {
  const b = bandFor(age);
  if (sex === "woman") return b.womenRange;
  if (sex === "man") return b.menRange;
  return [
    Math.round((b.womenRange[0] + b.menRange[0]) / 2),
    Math.round((b.womenRange[1] + b.menRange[1]) / 2),
  ];
}

const clamp = (v: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, v));

export function chairComponent(reps: number, age: number, sex: Sex | null, usedHands: boolean): number {
  let c = clamp(-2.5 * (reps - chairMidpoint(age, sex)), -12, 12);
  if (usedHands) c = Math.max(c, 8);
  return c;
}

export function balanceComponent(stage: number, age: number): number {
  if (stage <= 0) return 10;
  if (stage === 1) return 8;
  if (stage === 2) return 5;
  if (stage === 3) return age >= 80 ? -2 : 0;
  return age >= 80 ? -5 : -3;
}

const JAR = [-1, 0, 2, 3];
const CARRY = [-2, 0, 2, 4];
const FLOOR = [-3, 0, 3, 5, 2];
const STAIRS = [-2, 0, 2, 4];
const WALKING = [-2, 0, 2, 4];
const STRENGTH = [-2, -1, 0, 1];

const pick = (table: number[], i: number) => table[clamp(Math.round(i), 0, table.length - 1)] ?? 0;

export function selfReportComponent(a: Pick<StrengthAgeAnswers, "jar" | "carry" | "floor" | "stairs" | "walking" | "strengthFreq">): number {
  const sum =
    pick(JAR, a.jar) +
    pick(CARRY, a.carry) +
    pick(FLOOR, a.floor) +
    pick(STAIRS, a.stairs) +
    pick(WALKING, a.walking) +
    pick(STRENGTH, a.strengthFreq);
  return sum * 0.5;
}

/** Core formula shared by the quiz and the monthly in-app retest. */
export function computeStrengthAgeNumber(input: {
  age: number;
  sex: Sex | null;
  chairReps: number;
  usedHands: boolean;
  balanceStage: number;
  selfReport: number;
}): number {
  const { age } = input;
  const raw =
    age +
    chairComponent(input.chairReps, age, input.sex, input.usedHands) +
    balanceComponent(input.balanceStage, age) +
    input.selfReport;
  const rounded = Math.round(raw);
  return Math.max(40, clamp(rounded, age - 15, age + 20));
}

export interface StrengthAgeResult {
  kind: "tested" | "questionnaire_only" | "safe_mode";
  strengthAge: number | null;
  age: number;
  gap: number | null;
  profile: ProfileCode;
  flags: { balance: boolean; joint: boolean; hands: boolean };
  safeModeReasons: string[];
  chairReps: number | null;
  balanceStage: number | null;
  band: string;
  typical: [number, number];
  under60Note: boolean;
  track: "rebuild" | "steady" | "strong";
  aches: Ache[];
  adultChild: boolean;
}

const SAFETY_REASON: Record<SafetyFlag, string> = {
  chest: "chest discomfort when active",
  dizzy: "dizziness or fainting",
  fall: "a recent fall",
  surgery: "a recent surgery or hospital stay",
  doctor_limit: "your doctor's advice to limit activity",
};

export function isSafeMode(a: Pick<StrengthAgeAnswers, "safety" | "mobility">): boolean {
  return a.safety.length > 0 || a.mobility === "walker" || a.mobility === "wheelchair";
}

export function scoreStrengthAge(a: StrengthAgeAnswers): StrengthAgeResult {
  const age = clamp(Math.round(a.age), 45, 95);
  const band = bandFor(age);
  const typical = typicalRange(age, a.sex);
  const S = selfReportComponent(a);
  const safeMode = isSafeMode(a);
  const safeModeReasons = [
    ...a.safety.map((s) => SAFETY_REASON[s]),
    ...(a.mobility === "walker" ? ["using a walker"] : []),
    ...(a.mobility === "wheelchair" ? ["using a wheelchair"] : []),
  ];
  const jointAche = a.aches.some((x) => x === "knees" || x === "hips" || x === "lower_back");
  const jointHard = a.stairs >= 2 || a.floor === 2 || a.floor === 3;
  const joint = jointAche && jointHard;
  const adultChild = a.taker !== "self";
  const base = { age, band: band.label, typical, under60Note: a.age < 60, aches: a.aches, adultChild };

  if (safeMode) {
    return {
      ...base,
      kind: "safe_mode",
      strengthAge: null,
      gap: null,
      profile: "p6",
      flags: { balance: false, joint, hands: false },
      safeModeReasons,
      chairReps: null,
      balanceStage: null,
      track: "rebuild",
    };
  }

  if (a.taker === "other") {
    const offset = clamp(2 * S, -10, 10);
    const sa = Math.max(40, Math.round(age + offset));
    const gap = sa - age;
    const profile: ProfileCode = joint ? "p4" : gap <= -5 ? "p1" : gap >= 5 ? "p5" : "p2";
    return {
      ...base,
      kind: "questionnaire_only",
      strengthAge: sa,
      gap,
      profile,
      flags: { balance: false, joint, hands: false },
      safeModeReasons: [],
      chairReps: null,
      balanceStage: null,
      track: trackFor(profile),
    };
  }

  const reps = clamp(Math.round(a.chairReps ?? 0), 0, 40);
  const stage = clamp(Math.round(a.balanceStage ?? 0), 0, 4);
  const usedHands = Boolean(a.usedHands);
  const sa = computeStrengthAgeNumber({ age, sex: a.sex, chairReps: reps, usedHands, balanceStage: stage, selfReport: S });
  const gap = sa - age;
  const flags = {
    balance: stage <= 2,
    joint,
    hands: usedHands || reps < chairCutoff(age, a.sex),
  };

  let profile: ProfileCode;
  if (reps < 5 || stage === 0) profile = "p6";
  else if (flags.balance) profile = "p3";
  else if (flags.joint) profile = "p4";
  else if (gap <= -5) profile = "p1";
  else if (gap >= 5) profile = "p5";
  else profile = "p2";

  return {
    ...base,
    kind: "tested",
    strengthAge: sa,
    gap,
    profile,
    flags,
    safeModeReasons: [],
    chairReps: reps,
    balanceStage: stage,
    track: trackFor(profile),
  };
}

export function trackFor(profile: ProfileCode): "rebuild" | "steady" | "strong" {
  if (profile === "p1") return "strong";
  if (profile === "p5" || profile === "p6") return "rebuild";
  return "steady";
}

export const STAGE_NAMES = [
  "none of the positions",
  "feet-together stand",
  "half-step stand",
  "heel-to-toe stand",
  "one-foot stand",
];
