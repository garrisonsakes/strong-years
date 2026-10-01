/**
 * Daily Practice content engine (OFFER.md 1.2 #1, FUNNEL.md 0.3):
 * weekday rhythm × 4 tracks × optional swap (sore knee / sore back / low energy).
 * Every movement step carries the SAFETY_RULES.md M-01..M-04 elements:
 * support cue, easier version, breathing cue, stop rule.
 */
import type { Track } from "./db/types";

export const TRACKS: { key: Track; name: string; blurb: string }[] = [
  { key: "rebuild", name: "Rebuild", blurb: "Chair-based. Fully seated or holding a sturdy counter." },
  { key: "steady", name: "Steady", blurb: "Standing, with the counter nearby." },
  { key: "strong", name: "Strong", blurb: "Bands and water jugs." },
  { key: "iron", name: "Iron", blurb: "Heavier loads, for the already strong." },
];

export type Swap = "knee" | "back" | "energy";
export const SWAPS: { key: Swap; label: string }[] = [
  { key: "knee", label: "Sore knee today" },
  { key: "back", label: "Sore back today" },
  { key: "energy", label: "Low energy today" },
];

export interface Step {
  name: string;
  dose: string;
  cue: string;
  easier: string;
}

export interface Session {
  key: string;
  dayType: string;
  title: string;
  minutes: number;
  track: Track;
  swap: Swap | null;
  support: string;
  steps: Step[];
  breath: string;
  stopRule: string;
  closer: string;
}

const STOP_RULE = "Stop if you feel chest pain, dizziness, shortness of breath or sharp pain. Mild effort is fine; sharp is not.";
const BREATH = "Breathe out as you push or stand. Never hold your breath.";

type DayType = "strength_legs" | "mobility" | "balance" | "strength_upper" | "breath_flow" | "walk" | "rest_stretch";

// JS getDay(): 0 Sunday … 6 Saturday
export const WEEKDAY_PLAN: Record<number, { type: DayType; title: string }> = {
  1: { type: "strength_legs", title: "Strength: legs first" },
  2: { type: "mobility", title: "Mobility: the gentlest day" },
  3: { type: "balance", title: "Balance: steady feet" },
  4: { type: "strength_upper", title: "Strength: upper body and grip" },
  5: { type: "breath_flow", title: "Breath and qigong flow" },
  6: { type: "walk", title: "Walk and talk" },
  0: { type: "rest_stretch", title: "Rest and stretch" },
};

const LEVEL_DOSE: Record<Track, { reps: string; sets: string; hold: string }> = {
  rebuild: { reps: "5 slow reps", sets: "1–2 rounds", hold: "10 seconds" },
  steady: { reps: "8 reps", sets: "2 rounds", hold: "15 seconds" },
  strong: { reps: "10 reps", sets: "2–3 rounds", hold: "20 seconds" },
  iron: { reps: "12 reps", sets: "3 rounds", hold: "30 seconds" },
};

function legs(track: Track, swap: Swap | null): Step[] {
  const d = LEVEL_DOSE[track];
  const knee = swap === "knee";
  const energy = swap === "energy";
  const standName =
    track === "rebuild" ? "Sit-to-stand from a higher seat" : track === "iron" ? "Tempo sit-to-stand holding a water jug" : "Sit-to-stand, arms crossed";
  return [
    { name: "Seated marches", dose: "30 seconds", cue: "Sit tall, lift one knee then the other.", easier: "Smaller lifts, hands on thighs." },
    knee
      ? { name: "Seated knee extensions", dose: d.reps + " each leg", cue: "Straighten the knee slowly, pause, lower slowly. Pain-free range only.", easier: "Straighten halfway." }
      : { name: standName, dose: `${d.reps}, ${energy ? "1 round" : d.sets}`, cue: "Chair against the wall. Feet flat. Lean forward, stand all the way up, sit down slower than you stood.", easier: "Add a firm cushion to the seat, or use your hands on your thighs." },
    knee
      ? { name: "Heel raises at the counter", dose: d.reps, cue: "Hands on the counter. Rise onto your toes, lower slowly.", easier: "Smaller rise." }
      : { name: track === "strong" || track === "iron" ? "Split squat at the counter" : "Counter mini-squats", dose: d.reps, cue: "Hold the counter. Knees follow your toes. Bend only as far as feels good.", easier: "Bend less. Keep both hands on the counter." },
    { name: "Calf raises", dose: d.reps, cue: "Hands on the counter. Up on the toes, slow down.", easier: "Do them seated." },
    { name: "Seated hamstring stretch", dose: `${d.hold} each leg`, cue: "Sit near the edge, one leg straight, heel down, lean forward from the hips.", easier: "Bend the straight knee a little." },
  ];
}

function upper(track: Track, swap: Swap | null): Step[] {
  const d = LEVEL_DOSE[track];
  const back = swap === "back";
  return [
    { name: "Shoulder rolls", dose: "10 slow rolls", cue: "Sit or stand tall, roll back and down.", easier: "Smaller circles." },
    { name: track === "rebuild" ? "Wall push-ups" : track === "iron" ? "Counter push-ups" : "Wall push-ups, feet further back", dose: d.reps, cue: "Hands at shoulder height, body in one line, lower your chest toward the wall.", easier: "Step your feet closer to the wall." },
    back
      ? { name: "Seated towel pull-apart", dose: d.reps, cue: "Hold a towel wide, pull it apart, squeeze your shoulder blades gently.", easier: "Hold the towel lower, smaller pull." }
      : { name: track === "rebuild" ? "Seated towel rows" : "Band rows (door anchor) or towel rows", dose: d.reps, cue: "Pull elbows back, squeeze shoulder blades, return slowly.", easier: "Lighter band or looser towel." },
    { name: "Towel wring (grip)", dose: "5 wrings each direction", cue: "Wring a small towel like you're squeezing out water.", easier: "Use a thinner towel." },
    back
      ? { name: "Seated jug hold", dose: d.hold, cue: "Sit tall, hold a light jug beside you. No carrying today.", easier: "Half-full jug." }
      : { name: track === "rebuild" ? "Seated jug hold" : "Farmer carry with water jugs", dose: track === "rebuild" ? d.hold : "2 lengths of the kitchen", cue: "Stand tall, shoulders down, slow steps near the counter.", easier: "Half-full jugs, or one at a time." },
  ];
}

function balance(track: Track): Step[] {
  const d = LEVEL_DOSE[track];
  return [
    { name: "Weight shifts", dose: "10 each side", cue: "Stand at the counter, one hand hovering. Shift your weight side to side.", easier: "Hold the counter with both hands." },
    { name: "Feet-together stand", dose: d.hold, cue: "Feet touching, eyes forward.", easier: "Feet slightly apart." },
    { name: track === "rebuild" ? "Half-step stand" : "Heel-to-toe stand", dose: `${d.hold} each side`, cue: "One foot in front of the other at the counter. Grab the counter any time.", easier: "Half-step instead of heel-to-toe." },
    { name: "Heel-toe walk along the counter", dose: "2 lengths", cue: "Hand on the counter, slow steps, heel touches toe.", easier: "Normal steps, just slower." },
    { name: track === "iron" || track === "strong" ? "One-foot stand" : "Heel and toe raises", dose: track === "iron" || track === "strong" ? `${d.hold} each foot` : LEVEL_DOSE[track].reps, cue: "Counter within reach. Stand tall.", easier: "Both feet down, one hand on the counter." },
  ];
}

function mobility(swap: Swap | null): Step[] {
  return [
    { name: "Bed or chair knee rocks", dose: "10 each side", cue: "Knees together, rock gently side to side.", easier: "Smaller rocks." },
    { name: "Seated cat-cow", dose: "8 slow rounds", cue: "Hands on knees. Round your back, then lift your chest.", easier: "Smaller movement." },
    { name: "Hip hinge at the counter", dose: swap === "back" ? "5 gentle reps" : "8 reps", cue: "Hands on the counter, push hips back, back long.", easier: "Tiny hinge, just the start." },
    { name: "Gentle seated turns", dose: "5 each side", cue: "Turn only as far as comfortable. No forcing.", easier: "Turn your head and shoulders only." },
    { name: "Ankle circles", dose: "10 each direction", cue: "Seated, draw circles with your toes.", easier: "Point and flex instead." },
  ];
}

function breathFlow(): Step[] {
  return [
    { name: "Slow-exhale breathing", dose: "10 breaths", cue: "In through the nose for 4, out for 6. No holds.", easier: "In for 3, out for 5." },
    { name: "Tai chi weight shifts", dose: "8 each side", cue: "Stand at the counter, knees soft, shift slowly from foot to foot.", easier: "Do it seated, shifting through your hips." },
    { name: "Baduanjin: holding up the sky", dose: "6 slow reps", cue: "Lift the arms overhead only as far as comfortable, breathe out as they come down.", easier: "Arms to shoulder height." },
    { name: "Cloud hands (seated or standing)", dose: "1 minute", cue: "Slow, soft arms passing in front of you.", easier: "Seated." },
    { name: "Closing breath", dose: "5 breaths", cue: "Hands on belly, long slow exhale.", easier: "Just breathe normally and notice it." },
  ];
}

function walk(track: Track, swap: Swap | null): Step[] {
  const mins = swap === "energy" ? 5 : track === "rebuild" ? 6 : track === "steady" ? 10 : 15;
  return [
    { name: "Warm-up marches", dose: "1 minute", cue: "At the counter, easy marches.", easier: "Seated marches." },
    { name: track === "rebuild" ? "Indoor walk, hallway laps" : "Walk outside or indoors", dose: `${mins} minutes`, cue: "Chang talks, you walk. Easy pace, you can still chat.", easier: "Walk for 2 minutes, rest, repeat." },
    { name: "Sit and breathe", dose: "1 minute", cue: "Sit down, long slow exhale.", easier: "—" },
  ];
}

function stretch(): Step[] {
  return [
    { name: "Seated neck nods and half-turns", dose: "5 each", cue: "Slow nods, then look halfway over each shoulder. No full circles.", easier: "Smaller movement." },
    { name: "Doorway chest stretch", dose: "20 seconds", cue: "Forearm on the door frame, step through gently.", easier: "Hands clasped behind your back, seated." },
    { name: "Seated figure-four", dose: "20 seconds each side", cue: "Ankle on the other knee only if comfortable. New hip? Follow your surgeon's precautions and skip this one.", easier: "Cross at the ankles instead." },
    { name: "Calf stretch at the wall", dose: "20 seconds each", cue: "Hands on the wall, back heel down.", easier: "Seated, pull the toes up with a towel." },
  ];
}

export function dayTypeFor(date: Date): DayType {
  return WEEKDAY_PLAN[date.getDay()]!.type;
}

export function buildSession(date: Date, track: Track, swap: Swap | null): Session {
  const plan = WEEKDAY_PLAN[date.getDay()]!;
  let steps: Step[];
  switch (plan.type) {
    case "strength_legs":
      steps = legs(track, swap);
      break;
    case "strength_upper":
      steps = upper(track, swap);
      break;
    case "balance":
      steps = balance(swap === "energy" ? "rebuild" : track);
      break;
    case "mobility":
      steps = mobility(swap);
      break;
    case "breath_flow":
      steps = breathFlow();
      break;
    case "walk":
      steps = walk(track, swap);
      break;
    default:
      steps = stretch();
  }
  if (swap === "energy") steps = steps.slice(0, 3);
  const baseMinutes = { rebuild: 8, steady: 9, strong: 10, iron: 12 }[track];
  const minutes = swap === "energy" ? 5 : plan.type === "walk" ? baseMinutes + 4 : baseMinutes;
  const iso = date.toISOString().slice(0, 10);
  return {
    key: `${iso}:${plan.type}:${track}:${swap ?? "none"}`,
    dayType: plan.type,
    title: swap ? `${plan.title} (${SWAPS.find((s) => s.key === swap)!.label.toLowerCase()} version)` : plan.title,
    minutes,
    track,
    swap,
    support: track === "rebuild" ? "Sturdy chair without wheels, pushed against a wall. Counter within reach." : "Kitchen counter within reach. Chair against the wall behind you.",
    steps,
    breath: BREATH,
    stopRule: STOP_RULE,
    closer: plan.type.startsWith("strength") ? "That's your legs taken care of today. Same time tomorrow." : "Good. Every day, a little. Same time tomorrow.",
  };
}

/* ---------------- Strong Weeks (streaks with grace) ---------------- */

/** Monday of the ISO week containing `d`, as YYYY-MM-DD (UTC). */
export function weekKey(d: Date): string {
  const x = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  const dow = (x.getUTCDay() + 6) % 7; // Monday = 0
  x.setUTCDate(x.getUTCDate() - dow);
  return x.toISOString().slice(0, 10);
}

export interface StrongWeeks {
  streak: number;
  thisWeek: number;
  thisWeekStrong: boolean;
  graceAvailable: boolean;
  weeks: { week: string; sessions: number; strong: boolean; protected: boolean; grace: boolean }[];
  totalSessions: number;
}

/**
 * A Strong Week = 3+ sessions Monday–Sunday (FUNNEL.md 7.2 Loop 2).
 * Grace: one automatic "rest week" pass per 8 weeks, plus any week the member marked
 * "I was sick / traveling". The current week never breaks the streak while it's in progress.
 */
export function computeStrongWeeks(days: string[], protectedWeeks: string[], today: Date, lookback = 26): StrongWeeks {
  const counts = new Map<string, number>();
  const uniqueDays = [...new Set(days)];
  for (const day of uniqueDays) {
    const wk = weekKey(new Date(`${day}T12:00:00Z`));
    counts.set(wk, (counts.get(wk) ?? 0) + 1);
  }
  const current = weekKey(today);
  const weeks: StrongWeeks["weeks"] = [];
  for (let i = lookback - 1; i >= 0; i--) {
    const d = new Date(`${current}T12:00:00Z`);
    d.setUTCDate(d.getUTCDate() - i * 7);
    const wk = weekKey(d);
    const sessions = counts.get(wk) ?? 0;
    weeks.push({ week: wk, sessions, strong: sessions >= 3, protected: protectedWeeks.includes(wk), grace: false });
  }

  // Walk back from last week; the current week only counts if already strong
  // (it never breaks the chain while it is still in progress).
  const thisWeekEntry = weeks[weeks.length - 1]!;
  let streak = thisWeekEntry.strong ? 1 : 0;
  let lastAuto: number | null = null;
  for (let i = weeks.length - 2; i >= 0; i--) {
    const w = weeks[i]!;
    if (w.strong) {
      streak++;
      continue;
    }
    if (w.protected) {
      w.grace = true; // "I was sick / traveling": keeps the chain, adds nothing
      continue;
    }
    const prev = weeks[i - 1];
    const bridges = prev !== undefined && (prev.strong || prev.protected);
    const allowed = lastAuto === null || lastAuto - i >= 8;
    if (bridges && allowed) {
      w.grace = true; // automatic rest-week pass, at most one per 8 weeks
      lastAuto = i;
      continue;
    }
    break;
  }
  const graceUsedRecently = weeks.slice(-9, -1).some((w) => w.grace && !w.protected);
  return {
    streak,
    thisWeek: thisWeekEntry.sessions,
    thisWeekStrong: thisWeekEntry.strong,
    graceAvailable: !graceUsedRecently,
    weeks,
    totalSessions: uniqueDays.length,
  };
}
