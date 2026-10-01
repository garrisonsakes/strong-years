/**
 * Disclosure strings. Reviewer gate (FUNNEL.md, SAFETY_RULES.md §7): claims about
 * licensed review only render when REVIEWER_SIGNED=true AND reviewer names are set.
 * Until then, the FALLBACK text is shown verbatim.
 */
import { messaging, env } from "./config";

export function reviewerGate(claim: string, fallback: string): string {
  const named = Boolean(process.env.REVIEWER_PT_NAME);
  return env.reviewerSigned && named ? claim.replace("[PT NAME]", process.env.REVIEWER_PT_NAME ?? "").replace("[RD NAME]", process.env.REVIEWER_RD_NAME ?? "") : fallback;
}

export const copy = {
  get strip() {
    return `Chang Yin and Sun Yoon are AI characters. ${reviewerGate(
      "Every session is reviewed by a licensed physical therapist.",
      "Every session is built on published exercise guidelines for older adults.",
    )}`;
  },
  get disclosureBlock() {
    return [
      "Chang Yin and Sun Yoon are AI characters created by our team. They are not real people and they are not doctors.",
      reviewerGate(
        "Every session and recipe is reviewed by [PT NAME], PT, DPT and [RD NAME], RDN before it is published.",
        "Sessions and recipes are written by our team from published exercise and nutrition guidelines for older adults.",
      ),
      "This is general fitness and nutrition education, not medical advice. Talk to your doctor before starting a new exercise program, especially if you have a heart condition, recent surgery, a recent fall, dizziness, or take blood-thinning medication.",
    ].join(" ");
  },
  get footer() {
    return [
      "Chang Yin and Sun Yoon are AI characters; their story is fictional.",
      reviewerGate("Content reviewed by [PT NAME], PT, DPT and [RD NAME], RDN.", "Content built from published exercise and nutrition guidelines for older adults."),
      "General fitness and nutrition education, not medical advice. Consult your physician before beginning any exercise program.",
      `Membership renews automatically at the price shown until cancelled; we email you before every charge. Cancel online anytime in your account${messaging.smsEnabled ? " or by texting CANCEL" : " or by replying \u201ccancel\u201d to any email"}.`,
    ].join(" ");
  },
  get trustBuilt() {
    return reviewerGate("Reviewed by a licensed physical therapist", "Built on published guidelines for older adults");
  },
  quizFooter: "Created with AI characters. Not medical advice.",
};
