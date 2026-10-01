/** Result-page copy for both quizzes, from FUNNEL.md §3.1 / §3.2 (fallback reviewer strings only). */
import type { ProfileCode } from "./strengthAge";
import type { GutProfile } from "./gutEnergy";

export interface StrengthProfileCopy {
  name: string;
  headline: string;
  body: string[];
  track: string;
  days: string[];
  expect: string;
  button: string;
  fallback: string;
}

export const STRENGTH_PROFILES: Record<ProfileCode, StrengthProfileCopy> = {
  p1: {
    name: "Steady Oak",
    headline: "Your legs are younger than your birthday. Now let's keep it that way.",
    body: [
      "{first}, your Strength Age is {sa}, which is {gapAbs} years younger than you are. You stood up {reps} times in 30 seconds; the typical range for your age is {low} to {high}. You held the {stage} for 10 seconds.",
      "This is the group that has the most to protect. Strength and especially leg power drop fastest when people coast, and it usually happens quietly, over a winter, an illness, or a busy year. Your plan is built to push you a little, so you keep the lead you've built.",
    ],
    track: "Strong (Iron once the reps get easy; Steady on tired days)",
    days: [
      "Day 1: Legs, Strong level: tempo sit-to-stands with a water jug, split squats at the counter (12 min)",
      "Day 2: Balance + quick feet: side steps, heel-toe walk, single-leg reach (10 min)",
      "Day 3: Mobility + breath: hip openers, gentle rotations, 5 minutes of slow-exhale breathing (10 min)",
      "Day 4: Upper body + grip: band rows, wall push-ups to counter push-ups, farmer carries (12 min)",
      "Day 5: Power day: fast up, slow down chair stands, step-ups (10 min)",
      "Day 6: 20-minute tai chi flow, the long one",
      "Day 7: Rest, walk, and Sun Yoon's high-protein Sunday soup",
    ],
    expect: "Most people who train 3+ times a week notice the sessions feel easier within two to three weeks. Your chair-stand number may climb by a couple of reps; if you're already near the top of the range, your goal is to hold it and improve your one-leg balance time.",
    button: "Start my Steady Oak plan",
    fallback: "Want a finish line? Start the 12-week Strong at 70 program on day 1; all six programs are included.",
  },
  p2: {
    name: "Rooted but Rusty",
    headline: "You're right about where most people your age are. That's the problem, and the opportunity.",
    body: [
      "{first}, your Strength Age is {sa}. You did {reps} chair stands (typical for your age: {low} to {high}) and held the {stage}.",
      "Average at your age means the slide has started for most people: the armrests get used a little more each year. The good news is that average responds fast to training because you haven't been asking your legs for much. Three short sessions a week is enough to start moving your number.",
    ],
    track: "Steady (Strong on good days)",
    days: [
      "Day 1: Legs: sit-to-stands to a slow count, counter squats, calf raises (9 min)",
      "Day 2: Balance: the counter balance ladder, heel-toe walk along the counter (8 min)",
      "Day 3: Morning mobility + breath (8 min)",
      "Day 4: Upper body + grip: wall push-ups, band rows or towel rows, jug carries (9 min)",
      "Day 5: Legs + power: faster chair stands, step-ups on the bottom stair (9 min)",
      "Day 6: 15-minute tai chi flow",
      "Day 7: Rest, a 15-minute walk after lunch, Sun Yoon's egg-and-tofu breakfast",
    ],
    expect: "A realistic first goal is 1 to 3 more chair stands and one balance stage further. Sessions that feel hard on day 1 usually feel easy by day 14; that's when Chang Yin moves you up.",
    button: "Start my plan",
    fallback: "",
  },
  p3: {
    name: "Wobbly Foundations",
    headline: "Your legs have work to do, but first, let's make you steady.",
    body: [
      "{first}, you held the {stage} for 10 seconds but not the next one. That tells us exactly where to start. Balance is one of the most trainable things there is, and it often improves faster than strength. We'll begin at the kitchen counter and move you up a stage as each one gets easy.",
      "Please mention this result to your doctor at your next visit, especially if you've felt dizzy or unsteady; some causes of unsteadiness, like medicines or inner-ear issues, need a doctor's eye.",
    ],
    track: "Steady, always at the counter (Rebuild on tired days); program: Balance & Steady Feet",
    days: [
      "Day 1: Steady Feet 1: the counter balance ladder, weight shifts, heel and toe raises (8 min)",
      "Day 2: Legs: sit-to-stands, counter mini-squats (8 min)",
      "Day 3: Steady Feet 2: head turns while standing steady, reaching (8 min)",
      "Day 4: Walking Stronger 1: heel-toe walking along the counter, side steps (8 min)",
      "Day 5: Steady Feet 3 + legs (10 min)",
      "Day 6: Gentle tai chi, 12 minutes (tai chi has good evidence for balance in older adults)",
      "Day 7: Rest, plus Chang Yin's home safety checklist: lighting, rugs, grab bars, night lights",
    ],
    expect: "Our goal for month one is one balance stage further, or the same stage held more confidently. Balance often improves faster than strength.",
    button: "Start my Steady Feet plan",
    fallback: "",
  },
  p4: {
    name: "Stiff Engine",
    headline: "Your {joints} are talking. Here's how to train around them, and then through them.",
    body: [
      "{first}, your Strength Age is {sa}, and you told us your {joints} ache, with stairs or getting off the floor harder than you'd like. Joint aches are common and, for many people with everyday stiffness or arthritis, moving more (carefully) helps more than resting. Strengthening the muscles around the knee and hip is one of the most commonly recommended approaches for knee and hip osteoarthritis.",
      "Our rule: some mild discomfort during exercise that settles within a day is usually okay; sharp pain, swelling that lasts, or pain that's worse the next day means back off, and check with your doctor or physical therapist. If you've had a joint replaced, follow your surgeon's precautions first.",
    ],
    track: "Rebuild or Steady depending on the day (use the sore knee / sore back button); program: Back Strong or Strong at 70",
    days: [
      "Day 1: Knees & Stairs 1 or Back & Posture 1: pain-free-range strength (10 min)",
      "Day 2: Morning Unlock mobility (7 min)",
      "Day 3: Legs on the Rebuild track: seated knee extensions, sit-to-stands to a higher seat (use a cushion) (9 min)",
      "Day 4: Upper body + grip (8 min)",
      "Day 5: Track session 2 (10 min)",
      "Day 6: 12-minute gentle tai chi",
      "Day 7: Rest + walk + Sun Yoon's ginger-and-greens soup (comfort food, not a treatment)",
    ],
    expect: "A realistic goal is doing the stairs with less effort or a higher chair-stand number using a slightly higher seat. Joint comfort varies week to week; that's why you choose your level every day.",
    button: "Start my joint-friendly plan",
    fallback: "",
  },
  p5: {
    name: "Quiet Slide",
    headline: "Your legs are older than you are. Let's go get those years back.",
    body: [
      "{first}, your Strength Age is {sa}, {gapAbs} years older than your birthday. You did {reps} chair stands; typical for your age is {low} to {high}. This doesn't mean anything is wrong with you. It means your legs haven't been asked to work hard in a while, which is the most fixable problem on this page.",
      "The research here is genuinely encouraging: in supervised studies, even people in their 80s and 90s gained substantial leg strength in a few months of progressive training. The people who gain the most are usually the ones starting from the lowest point.",
    ],
    track: "Rebuild for week 1, then Steady",
    days: [
      "Day 1: The Chair Builder: sit-to-stands from a higher seat (add a firm cushion), seated leg lifts (8 min)",
      "Day 2: Balance at the counter, stages 1 to 3 (7 min)",
      "Day 3: Morning mobility + breath (7 min)",
      "Day 4: Upper body + grip on the Rebuild track (8 min)",
      "Day 5: The Chair Builder 2 (8 min)",
      "Day 6: 10-minute seated tai chi",
      "Day 7: Rest + 10-minute walk after your biggest meal + Sun Yoon's 30-gram-protein breakfast",
    ],
    expect: "For many people starting here, 2 to 4 more chair stands in the first month is realistic, and it often shows up first as “I didn't need the armrest.”",
    button: "Start my plan",
    fallback: "",
  },
  p6: {
    name: "Gentle Restart",
    headline: "We'll start gently, and we'll start with your doctor in the loop.",
    body: [
      "{first}, thank you for being honest in the safety questions. Because of {reason}, we skipped the standing tests today. That's the right call.",
      "Here's what we suggest: print or forward the one-page summary below to your doctor or physical therapist and ask, “Is it okay for me to do seated strength and breathing exercises for 10 minutes a day?” Most people in your situation hear “yes, and here's what to avoid,” and you can bring those notes to your plan.",
    ],
    track: "Rebuild (chair-based)",
    days: [
      "Day 1: Seated breathing and posture (6 min)",
      "Day 2: Seated leg strength: knee extensions, marches, heel raises (7 min)",
      "Day 3: Seated upper body with a towel (6 min)",
      "Day 4: Seated mobility: neck, shoulders, ankles (6 min)",
      "Day 5: Seated leg strength 2 (7 min)",
      "Day 6: Seated tai chi, 8 minutes",
      "Day 7: Rest + Sun Yoon's soft-food protein recipes",
    ],
    expect: "Once your doctor says go, the goal for month one is simply finishing three seated sessions a week.",
    button: "Start 7 days for $1",
    fallback: "",
  },
};

export interface GutProfileCopy {
  name: string;
  headline: string;
  note: string;
  body: string;
  plan: string[];
  recipes: string;
}

export const GUT_PROFILES: Record<GutProfile, GutProfileCopy> = {
  b1: {
    name: "Running on Toast",
    headline: "You're running your body on toast and coffee. No wonder it's tired.",
    note: "I love toast. But toast is not breakfast. Toast is a plate.",
    body: "Your Fuel score is {x}/10. Most of your meals are light on protein, and breakfast especially. As we get older, our muscles need more protein per meal to maintain themselves than they did when we were young, and many older adults eat most of their protein at dinner. Spreading it out, about 25–30 grams at each meal, is one of the simplest changes you can make, and it pairs with strength exercise: food gives your muscles the material, exercise tells them to use it.",
    plan: [
      "Days 1–2: Add one protein to breakfast: two eggs, or a cup of Greek yogurt, or Sun Yoon's silken tofu with soy and scallion",
      "Days 3–4: Make lunch palm + fist: a palm of protein, a fist of vegetables",
      "Day 5: Cook a pot of her doenjang tofu stew (24g protein a bowl), eat it twice",
      "Day 6: Snack swap: cottage cheese or a boiled egg instead of crackers",
      "Day 7: Count it once: write down your protein for one day. Most people are surprised",
    ],
    recipes: "Steamed egg custard (gyeran-jjim), 13g/bowl; Congee with shredded chicken and ginger, 22g/bowl; Doenjang tofu stew, 24g/bowl.",
  },
  b2: {
    name: "The 2 PM Slump",
    headline: "You're not lazy. Your lunch is putting you to sleep.",
    note: "After lunch, Chang Yin walks around the block. Then he tells everyone he feels young. It's the walk, not him.",
    body: "Your Rhythm score is {x}/10. A big, starchy meal followed by sitting is a common recipe for an afternoon crash. Research in adults shows that even a short, easy walk after eating, as little as 2 to 5 minutes and better at 10 to 15, lowers the rise in blood sugar after the meal compared with sitting. Many people notice they feel more awake too.",
    plan: [
      "Every day: a 10-minute walk (or 10 minutes of Chang Yin's After-Meal Movement indoors) within 30 minutes of your biggest meal",
      "Days 1–3: Build lunch in this order: vegetables and protein first, rice or bread last",
      "Days 4–5: Swap half your white rice for Sun Yoon's mixed-grain rice (japgokbap)",
      "Day 6: Move your biggest meal earlier in the day if you can",
      "Day 7: Score your afternoon energy 1 to 5 each day, and compare with day 1",
    ],
    recipes: "Japgokbap mixed-grain rice; Steamed fish with ginger and scallion; Spinach namul (sesame spinach).",
  },
  b3: {
    name: "Slow River",
    headline: "Things are moving slowly. Let's get the river running again, gently.",
    note: "Everybody wants to talk about energy. Nobody wants to talk about the bathroom. I will talk about the bathroom.",
    body: "Your Flow score is {x}/10: low fiber, low fluids, or not-so-regular bathroom trips. Adults over 50 are generally advised to get about 21 grams of fiber a day (women) or 30 grams (men), and most get far less. Add fiber slowly, over two to three weeks, with more water, or you'll feel bloated. Walking helps too. If constipation is new for you, lasts, or comes with pain or blood, see your doctor.",
    plan: [
      "Day 1: Add one glass of water or barley tea (boricha) with breakfast and lunch",
      "Days 2–3: Add one serving: a pear, a handful of berries, or a spoon of cooked beans",
      "Days 4–5: Seaweed soup (miyeok-guk) or a vegetable soup once a day",
      "Day 6: Add a 10-minute walk after breakfast",
      "Day 7: One mixed-grain meal (oats, barley or japgokbap)",
    ],
    recipes: "Miyeok-guk seaweed soup; Boricha barley tea; Oat-and-pear warm breakfast bowl.",
  },
  b4: {
    name: "Wired-Tired",
    headline: "Tired all day, wide awake at night. Let's fix the evening first.",
    note: "You drink coffee at 3 o'clock and then you blame the moon.",
    body: "Your Rest score is {x}/10. Caffeine stays in the body for many hours, so an afternoon coffee can still be working at bedtime. Alcohol can help you fall asleep but tends to break up sleep later in the night. A calmer evening routine, a consistent wake time, and daytime movement and daylight all help. If you snore loudly, stop breathing at night, or feel sleepy while driving, please talk to your doctor; these can be signs of a sleep condition that needs a proper check.",
    plan: [
      "Day 1: Last caffeine before noon",
      "Day 2: Morning light: 10 minutes outside within an hour of waking",
      "Days 3–4: Chang Yin's Sleep Wind-Down session (10 minutes, slow-exhale breathing, 4 in, 6 out)",
      "Day 5: Same wake time every day this week, including the weekend",
      "Day 6: Warm, light dinner 3 hours before bed (Sun Yoon's congee)",
      "Day 7: Note your nights 1–5 and compare with day 1",
    ],
    recipes: "Plain congee with egg; Jujube and ginger tea (a warm caffeine-free evening drink; kitchen tradition, not a sleep treatment); Soft tofu soup.",
  },
  b5: {
    name: "Tender Belly",
    headline: "Your stomach wants smaller, softer and slower. Let's give it that.",
    note: "Eat like you're not in a hurry. You're not in a hurry.",
    body: "Your Comfort score is {x}/10: frequent bloating or fullness, or chewing that's harder than it used to be. Eating smaller meals, slowing down, and choosing soft, moist, protein-rich foods often helps comfort and makes sure you still get enough protein. If chewing is getting harder, a dentist visit can make a big difference. If bloating is new, persistent or painful, please talk to your doctor.",
    plan: [
      "Days 1–2: Put the fork down between bites; aim for 20 minutes per meal",
      "Days 3–4: Four smaller meals instead of three big ones",
      "Day 5: Soft protein day: steamed egg custard, soft tofu, fish congee",
      "Day 6: Keep a note of foods that seem to bother you (no cutting out whole food groups on your own)",
      "Day 7: A gentle walk after your biggest meal",
    ],
    recipes: "Gyeran-jjim steamed egg custard; Soft tofu with warm soy dressing; Fish congee.",
  },
  b6: {
    name: "Steady Burner",
    headline: "Your kitchen is in good shape. Now your legs need to catch up with your plate.",
    note: "Good. Don't get proud. Go see Chang Yin.",
    body: "You're eating protein, fiber and water, moving after meals and sleeping reasonably well. The next thing most people at this stage are missing is strength training. Take Chang Yin's free Strength Age test next; it takes three minutes.",
    plan: [],
    recipes: "",
  },
};

export function fill(template: string, vars: Record<string, string | number | null | undefined>): string {
  return template.replace(/\{(\w+)\}/g, (_, k: string) => (vars[k] === undefined || vars[k] === null ? "" : String(vars[k])));
}
