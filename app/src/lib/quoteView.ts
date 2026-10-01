import { moneyExact, type CheckoutQuote } from "./pricing";

export interface QuoteView {
  todayLabel: string;
  lines: { label: string; amount: string }[];
  terms: string[];
  consentLabel: string | null;
  buttonLabel: string;
  underButton: string;
  /** M1: HMAC of the exact quote, sent back at submit. */
  sig?: string;
}

export function toView(q: CheckoutQuote): QuoteView {
  return {
    todayLabel: moneyExact(q.todayCents),
    lines: [...q.lines.map((l) => ({ label: l.label, amount: moneyExact(l.cents) })), { label: "Total today", amount: moneyExact(q.todayCents) }],
    terms: q.terms,
    consentLabel: q.consentLabel,
    buttonLabel: q.buttonLabel,
    underButton: q.underButton,
  };
}
