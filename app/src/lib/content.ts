/**
 * Sun Yoon's Kitchen (weekly recipes + grocery list + one honestly graded remedy),
 * 12-week programs and printables. Recipes come from FUNNEL.md §3.2 and CHARACTERS.md §3.
 * Every food item carries its "who should skip or ask first" line (SAFETY_RULES.md §5).
 */
import { PROGRAMS } from "./pricing";

export interface Recipe {
  slug: string;
  name: string;
  korean?: string;
  proteinG: number;
  minutes: number;
  soft: boolean;
  ingredients: string[];
  steps: string[];
  sunNote: string;
  caution: string | null;
}

export const RECIPES: Recipe[] = [
  {
    slug: "gyeran-jjim",
    name: "Steamed egg custard",
    korean: "gyeran-jjim",
    proteinG: 13,
    minutes: 15,
    soft: true,
    ingredients: ["2 large eggs", "3/4 cup water or low-sodium broth", "1 scallion, finely sliced", "1/2 tsp soy sauce", "A few drops of sesame oil"],
    steps: ["Whisk the eggs with the water or broth until smooth.", "Pour into a small heatproof bowl, add the scallion.", "Steam over simmering water, lid on, 10–12 minutes, until just set.", "Finish with soy sauce and sesame oil."],
    sunNote: "Soft, cheap, done in fifteen minutes. No excuses.",
    caution: "Cook eggs until set. No raw or runny eggs for older adults.",
  },
  {
    slug: "doenjang-tofu-stew",
    name: "Doenjang tofu stew",
    korean: "doenjang jjigae",
    proteinG: 24,
    minutes: 25,
    soft: true,
    ingredients: ["1 block firm tofu (14 oz), cubed", "2 tbsp doenjang (soybean paste)", "1 small zucchini, diced", "1/2 onion, diced", "3 cups water", "1 scallion"],
    steps: ["Dissolve the doenjang in the water in a pot.", "Add onion and zucchini, simmer 8 minutes.", "Add tofu, simmer 8 more minutes.", "Top with scallion. Two bowls tonight, two for tomorrow."],
    sunNote: "24 grams of protein a bowl. Eat it twice. Grams, not vibes.",
    caution: "Doenjang is salty. Watching sodium? Use 1 tbsp and more vegetables.",
  },
  {
    slug: "chicken-congee",
    name: "Congee with shredded chicken and ginger",
    proteinG: 22,
    minutes: 45,
    soft: true,
    ingredients: ["1/2 cup rice", "6 cups water or low-sodium broth", "1 cooked chicken breast, shredded", "Thumb of ginger, sliced", "Scallion, white pepper"],
    steps: ["Simmer rice with the water or broth and ginger, stirring now and then, 40 minutes.", "Stir in the chicken for the last 5 minutes.", "Season with white pepper and scallion."],
    sunNote: "For tired days and slow stomachs. It's a hug in a bowl, not medicine.",
    caution: null,
  },
  {
    slug: "japgokbap",
    name: "Mixed-grain rice",
    korean: "japgokbap",
    proteinG: 7,
    minutes: 50,
    soft: false,
    ingredients: ["1 cup white rice", "1/4 cup barley", "1/4 cup brown rice", "2 tbsp black beans (soaked)"],
    steps: ["Rinse everything, soak 30 minutes.", "Cook in the rice cooker on the mixed-grain setting (or 1.25× water).", "Eat with protein and vegetables first, rice last."],
    sunNote: "Half your white rice becomes this. Your afternoon will thank you.",
    caution: "Go up slowly on fibre and drink water, or you'll feel it.",
  },
  {
    slug: "steamed-fish",
    name: "Steamed fish with ginger and scallion",
    proteinG: 28,
    minutes: 20,
    soft: true,
    ingredients: ["2 white fish fillets (cod or tilapia)", "Thumb of ginger, julienned", "2 scallions", "1 tbsp soy sauce", "1 tbsp hot oil (optional)"],
    steps: ["Lay the fish on a plate with half the ginger.", "Steam 8–10 minutes until it flakes.", "Top with scallion and the rest of the ginger, spoon soy over it."],
    sunNote: "Chang says it's too plain. Chang is wrong.",
    caution: null,
  },
  {
    slug: "spinach-namul",
    name: "Sesame spinach",
    korean: "sigeumchi namul",
    proteinG: 4,
    minutes: 10,
    soft: true,
    ingredients: ["1 bunch spinach", "1 tsp sesame oil", "1 tsp toasted sesame seeds", "1 small garlic clove, grated", "Pinch of salt"],
    steps: ["Blanch the spinach 30 seconds, rinse in cold water, squeeze dry.", "Toss with the rest."],
    sunNote: "A side dish that counts as a vegetable. Two, if you eat it all.",
    caution: "On warfarin? Keep leafy greens steady week to week, don't suddenly change. Ask your doctor.",
  },
  {
    slug: "miyeok-guk",
    name: "Seaweed soup",
    korean: "miyeok-guk",
    proteinG: 18,
    minutes: 35,
    soft: true,
    ingredients: ["1/2 oz dried miyeok (wakame)", "4 oz beef or 1 block tofu", "1 tsp sesame oil", "1 tbsp soup soy sauce", "6 cups water"],
    steps: ["Soak the seaweed 20 minutes, cut into pieces.", "Sauté beef or tofu in sesame oil, add seaweed, sauté 2 minutes.", "Add water, simmer 20 minutes, season."],
    sunNote: "Birthday soup in our house. Also Tuesday soup.",
    caution: "Seaweed is high in iodine. Thyroid condition? Ask your doctor how often.",
  },
  {
    slug: "silken-tofu-breakfast",
    name: "Silken tofu with soy and scallion",
    proteinG: 20,
    minutes: 3,
    soft: true,
    ingredients: ["1 block silken tofu", "1 tbsp soy sauce", "1 scallion", "Sesame seeds"],
    steps: ["Slide the tofu onto a plate.", "Top with soy, scallion and sesame. Done."],
    sunNote: "Three minutes. 20 grams of protein. Toast is not breakfast. Toast is a plate.",
    caution: null,
  },
  {
    slug: "boricha",
    name: "Barley tea",
    korean: "boricha",
    proteinG: 0,
    minutes: 15,
    soft: true,
    ingredients: ["2 tbsp roasted barley", "8 cups water"],
    steps: ["Boil the barley in the water 10 minutes.", "Strain. Drink warm or cold all day."],
    sunNote: "Water with flavour. You'll drink more of it. That's the point.",
    caution: null,
  },
];

export type EvidenceGrade = "good evidence" | "some evidence" | "tradition only, enjoy it as food";

export interface Remedy {
  name: string;
  grade: EvidenceGrade;
  note: string;
  skip: string;
}

export const REMEDIES: Remedy[] = [
  { name: "A 10-minute walk after your biggest meal", grade: "good evidence", note: "Short walks after eating lower the rise in blood sugar after the meal compared with sitting, in studies of adults.", skip: "If walking is unsafe today, march in place at the counter." },
  { name: "Two kiwis a day for regularity", grade: "some evidence", note: "A small study found two kiwis a day worked about as well as prunes for constipation, with fewer side effects.", skip: "Kiwi allergy? Skip it. Go up slowly and drink water." },
  { name: "Honey in warm water for a cough", grade: "some evidence", note: "Honey can ease cough symptoms a little. It's comfort, not a treatment for an infection.", skip: "Never for babies under 1. Diabetes? It counts as sugar." },
  { name: "Ginger and jujube tea", grade: "tradition only, enjoy it as food", note: "A warm, caffeine-free evening drink in our kitchen. Enjoy it. It isn't a sleep treatment.", skip: "Taking ginger supplements with blood thinners? Ask your doctor. Tea amounts in food are usually fine." },
  { name: "Onion in water overnight", grade: "tradition only, enjoy it as food", note: "No good evidence for any health effect. Put the onion in the soup, where it belongs.", skip: "—" },
];

export interface KitchenWeek {
  weekOf: string;
  recipes: Recipe[];
  groceries: string[];
  remedy: Remedy;
  sunMessage: string;
}

const SUN_MESSAGES = [
  "Three recipes. One grocery list. No excuses. Protein at every meal, and call your sister.",
  "This week, soup. It's cheap, it's soft, and it makes two days of lunch. Eat, sweetheart.",
  "Chang ate toast for breakfast on Tuesday. We don't talk about Tuesday. Make the tofu.",
];

export function kitchenWeek(date: Date): KitchenWeek {
  const weekIndex = Math.floor(date.getTime() / (7 * 86_400_000));
  const n = RECIPES.length;
  const recipes = [0, 1, 2].map((k) => RECIPES[(weekIndex * 3 + k) % n]!);
  const groceries = [...new Set(recipes.flatMap((r) => r.ingredients.map((i) => i.replace(/^[0-9/ .]+(tbsp|tsp|cup|cups|oz|block)?\s*/i, "").trim())))].filter(Boolean);
  const monday = new Date(date);
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));
  return {
    weekOf: monday.toISOString().slice(0, 10),
    recipes,
    groceries,
    remedy: REMEDIES[weekIndex % REMEDIES.length]!,
    sunMessage: SUN_MESSAGES[weekIndex % SUN_MESSAGES.length]!,
  };
}

export const PROGRAM_DETAILS: Record<(typeof PROGRAMS)[number]["slug"], { blurb: string; weeks: string[] }> = {
  "strong-at-70": { blurb: "Legs first, then everything else. Progressive strength for the life you actually live.", weeks: ["Chair Builder", "Chair Builder 2", "Step-ups", "Carries", "Tempo stands", "Checkpoint", "Split squats", "Power days", "Floor practice (with a chair)", "Heavier carries", "Consolidate", "Final checkpoint"] },
  "back-strong": { blurb: "Move with less stiffness. Hinges, bird-dogs and walking, never loaded sit-ups.", weeks: ["Morning Unlock", "Hip hinges", "Wall slides", "Bird-dog at the counter", "Carries", "Checkpoint", "Hinge + carry", "Walking stronger", "Rotation, gently", "Longer holds", "Consolidate", "Final checkpoint"] },
  "steady-feet": { blurb: "Otago-style balance progressions plus tai chi, always at the counter.", weeks: ["Counter ladder", "Weight shifts", "Heel-toe walk", "Head turns", "Side steps", "Checkpoint", "One-foot practice", "Tai chi steps", "Reaching", "Dual tasks", "Consolidate", "Final checkpoint"] },
  "gut-reset": { blurb: "Sun Yoon's 12 weeks: protein at breakfast, fibre slowly, walks after meals.", weeks: ["Protein breakfast", "Palm + fist lunch", "Soup week", "After-meal walks", "Fibre, slowly", "Checkpoint", "Fermented foods", "Soft-food week", "Water and tea", "Eating slower", "Consolidate", "Final checkpoint"] },
  "grip-hands": { blurb: "Jars, bags and grandchildren. Towel wrings, carries and finger work.", weeks: ["Towel wrings", "Finger spreads", "Jug carries", "Band pulls", "Hangs (counter)", "Checkpoint", "Heavier carries", "Pinch grips", "Wrist mobility", "Mixed", "Consolidate", "Final checkpoint"] },
  "walk-stronger": { blurb: "From hallway laps to a long walk you enjoy. Pace, posture and legs.", weeks: ["Hallway laps", "10 minutes", "Posture", "Hills (gentle)", "Intervals", "Checkpoint", "20 minutes", "Stairs", "Uneven ground", "30 minutes", "Consolidate", "Final checkpoint"] },
};

export function programWeek(startedAt: string | null, now = new Date()): number {
  if (!startedAt) return 1;
  const weeks = Math.floor((now.getTime() - new Date(startedAt).getTime()) / (7 * 86_400_000)) + 1;
  return Math.min(12, Math.max(1, weeks));
}

export const PRINTABLES = [
  { slug: "weekly-plan", name: "This week's plan", blurb: "One page for the fridge: each day's session and length." },
  { slug: "grocery-list", name: "Sun Yoon's grocery list", blurb: "This Sunday's three recipes, one list, large print." },
  { slug: "strength-age-chart", name: "Strength Age fridge chart", blurb: "Write your monthly numbers. Watch the line move." },
  { slug: "exercise-cards", name: "Large-print exercise cards", blurb: "The five moves Chang uses most, with the easier version of each." },
] as const;

export { PROGRAMS };
