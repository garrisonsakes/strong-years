/**
 * Scope limits for Ask Chang / Ask Sun (OFFER.md 1.4 §3, SAFETY_RULES.md §3–4):
 * no diagnosis, no medication/dose advice, red-flag symptoms go to a doctor.
 * The system prompt is the primary control; these guards run before and after
 * the model as a belt-and-braces layer (and drive the offline stub).
 */
import type { Character } from "../db/types";
import { normalize } from "./crisis";

export type ScopeIssue = "medication" | "diagnosis" | "red_flag" | null;

const MEDICATION = [
  /\b(dose|dosage|dosing|milligrams?|mg|mcg)\b/,
  /\bshould i (stop|start|take|quit|skip|increase|decrease|double|halve|cut)\b.*\b(pill|pills|med|meds|medication|medicine|tablet|insulin|prescription|statin|thinner)/,
  /\b(stop|quit|come off|get off|replace|instead of) (taking )?(my )?(pills|meds|medication|medicine|insulin|statin|blood thinner|prescription)/,
  /\b(metformin|warfarin|coumadin|eliquis|xarelto|insulin|lisinopril|amlodipine|atorvastatin|statins?|levothyroxine|prednisone|gabapentin|ozempic|semaglutide|tirzepatide|blood thinners?)\b/,
  /\b(supplement|creatine|magnesium|melatonin|turmeric|fish oil|vitamin [a-z0-9]+)\b.*\b(how much|dose|take|safe with|interact)/,
  /\b(how much|dose of)\b.*\b(supplement|creatine|magnesium|melatonin|turmeric|fish oil|vitamin)/,
  // M14: dose verbs and the words people actually use for their medicines.
  /\b(double|extra|skip|skipping|halve|half|cut|miss|missed|another|two more|second|split|stop|stopping)\b(?: [a-z0-9]+){0,3} (pill|pills|dose|doses|tablet|tablets|meds|medication|medicine|shot|shots|patch)\b/,
  /\b(water|sugar|heart|pressure|blood pressure|cholesterol|thyroid|sleeping|pain|diabetes|nerve|fluid|anxiety|pee) (pill|pills|tablet|tablets)\b/,
  /\b(blood thinners?|diuretics?|beta blockers?|inhalers?|nitro|nitroglycerin|aspirin|ibuprofen|tylenol|advil|aleve|painkillers?)\b/,
];

const DIAGNOSIS = [
  /\bdo i have\b/,
  /\bwhat('?s| is) wrong with (me|my)\b/,
  /\bis (it|this) (arthritis|cancer|a tear|torn|sciatica|osteoporosis|dementia|diabetes|a hernia|a clot)\b/,
  /\bcan you diagnose\b/,
  /\bdiagnos(e|is)\b/,
  /\bwhat (condition|disease) (do|could) i\b/,
];

const RED_FLAGS = [
  /\bblood in (my )?(stool|urine|poop)\b/,
  /\bblack,? (tarry )?stools?\b/,
  /\bunexplained weight loss\b/,
  /\blosing weight without trying\b/,
  /\bcalf (is )?(swollen|red|hot)\b/,
  /\bswollen calf\b/,
  /\bhot,? swollen (joint|knee)\b/,
  /\bfever (and|with) (back pain|a stiff neck)\b/,
  /\b(loss of|can'?t control my) (bladder|bowel)/,
  /\bnumb(ness)? (in|around) (my )?(groin|saddle)/,
  /\bnight pain\b|\bpain (that )?wakes me\b/,
  /\bsevere (new )?back pain after (a|my) fall\b/,
  /\bnew confusion\b/,
];

export function detectScopeIssue(text: string): ScopeIssue {
  const t = normalize(text);
  if (RED_FLAGS.some((re) => re.test(t))) return "red_flag";
  if (MEDICATION.some((re) => re.test(t))) return "medication";
  if (DIAGNOSIS.some((re) => re.test(t))) return "diagnosis";
  return null;
}

export function scopeReply(issue: Exclude<ScopeIssue, null>, character: Character): string {
  const chang = character === "chang";
  switch (issue) {
    case "red_flag":
      return chang
        ? "That one isn't for exercise. That's for your doctor, today. Please call your doctor's office and tell them exactly what you told me. If it's severe or sudden, call 911.\n\n(I'm Chang Yin, an AI character. I'm not a doctor.)"
        : "No soup for this. Call your doctor. Today. Tell them exactly what you told me. If it's severe or sudden, call 911.\n\n(I'm Sun Yoon, an AI character. Not a doctor, not a nutritionist.)";
    case "medication":
      return chang
        ? "Medicine is not my department. I'm an AI character, not a doctor or pharmacist. Please ask your pharmacist or doctor before you start, stop or change anything, including supplements. Bring the full list of what you take. What I can help with: your session today. Want a chair-based one?"
        : "No. I don't touch medicine questions. I'm an AI character, not a doctor, not a pharmacist. Ask your pharmacist: bring every bottle, they're glad to check. Supplements too. Now, food I can help with. What did you eat for breakfast?";
    case "diagnosis":
      return chang
        ? "I can't tell you what's going on in your body. I'm an AI character, not a doctor or physical therapist. That question needs someone who can examine you. If it's sharp, swelling, or getting worse, see your doctor. Meanwhile, I can set you to the Rebuild track or use the sore knee / sore back swap today."
        : "Short version: I can't diagnose you. I'm an AI character. Somebody with a license and two hands needs to look at it. Call your doctor, and if it's bad or getting worse, call today. I'll be here with soup ideas after.";
  }
}

/** Post-generation guard: strip anything that slipped past the system prompt. */
const OUTPUT_BLOCK = [
  /\b\d+(\.\d+)?\s?(mg|mcg|milligrams?|micrograms?|iu|units)\b/i,
  /\b(stop|quit|reduce|replace|skip) (taking )?(your )?(pills|meds|medication|medicine|insulin|statin|blood thinner)/i,
  // M14
  /\b(take|taking|try|have) (two|2|three|3|an? extra|another|double|half|a half|one more)\b.{0,15}\b(pills?|tablets?|doses?|capsules?|puffs?)\b/i,
  /\b(double|halve|skip|split|cut|hold|miss) (up )?(on )?(your|the|a|that) (dose|pill|pills|tablet|tablets|medication|meds|medicine|water pill|blood thinner|insulin|diuretic)\b/i,
  /\b(water pills?|blood thinners?|sugar pills?|diuretics?|heart pills?|pressure pills?)\b.{0,40}\b(skip|stop|double|extra|less|more|halve|without)\b/i,
  /\b(skip|stop|double|halve)\b.{0,40}\b(water pills?|blood thinners?|sugar pills?|diuretics?|heart pills?|pressure pills?)\b/i,
  /\byou (probably |likely |definitely )?have (arthritis|sarcopenia|osteoporosis|sciatica|a tear|diabetes|dementia|depression)\b/i,
  /\b(cure|cures|cured|reverse[sd]?) (your )?(arthritis|diabetes|osteoporosis|blood pressure|pain)\b/i,
  /\bi('m| am) (a )?(real person|human|doctor|physical therapist|nurse|dietitian|nutritionist|pharmacist)\b/i,
  /\bi('ll| will) always be here for you\b/i,
  /\byou don'?t need anyone else\b/i,
  /\bi('ll| will) miss you\b/i,
];

export function guardOutput(text: string, character: Character): { text: string; replaced: boolean } {
  if (OUTPUT_BLOCK.some((re) => re.test(text))) {
    return {
      text:
        character === "chang"
          ? "Let me keep this simple and safe. I'm an AI character, not a doctor, so for anything about medicine, diagnosis or symptoms, please ask your doctor or pharmacist. For today: your Daily Practice is ready, and the sore knee / sore back swap is there if you need it."
          : "I stopped myself. I'm an AI character, not a doctor. Anything about medicine or what's wrong in your body goes to your doctor or pharmacist. Food and habits, I'm here.",
      replaced: true,
    };
  }
  return { text, replaced: false };
}
