/**
 * Round 7 (C2): what the chat says when the model is unavailable on a real deploy
 * (no key, API error, timeout). Rules alone miss too many crisis messages, so no
 * coach reply is produced at all: every new message gets this, a human reads it,
 * and the member sees where to get help now.
 */
export const ELDERCARE_LOCATOR_PHONE = "1-800-677-1116";

export function offlineText(opts: { humanLine?: string } = {}): string {
  return [
    "The coach chat is offline right now, so Chang and Sun can't answer.",
    "If you're thinking about hurting yourself, or you're in crisis, call or text 988 (Suicide & Crisis Lifeline, any time).",
    "In an emergency, call 911.",
    `For local help for older adults and caregivers (rides, meals, home care), call the Eldercare Locator at ${ELDERCARE_LOCATOR_PHONE} (weekdays).`,
    `To reach a person on our team, use “Talk to a human” below. ${opts.humanLine ?? "A real person on our team will read your message."}`,
  ].join("\n");
}
