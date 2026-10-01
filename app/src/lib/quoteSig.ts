/**
 * M1: the terms a buyer agrees to are the terms they saw. Every quote rendered
 * on /join or /checkout carries an HMAC of its price, next-charge date and exact
 * terms text; at submit the server re-quotes and rejects on any difference
 * (for example, the founding cap closing or the date rolling over mid-checkout).
 */
import { createHmac, timingSafeEqual } from "node:crypto";
import { env } from "./config";
import type { CheckoutQuote } from "./pricing";

export function signQuote(q: CheckoutQuote): string {
  const payload = JSON.stringify({
    today: q.todayCents,
    lines: q.lines.map((l) => [l.kind, l.sku ?? null, l.cents]),
    recurring: q.recurring ? [q.recurring.priceCents, q.recurring.nextChargeAt.toISOString().slice(0, 10), q.recurring.trialDays] : null,
    terms: q.terms,
    consent: q.consentLabel,
  });
  return createHmac("sha256", env.sessionSecret).update(`quote:${payload}`).digest("base64url");
}

export function quoteSigMatches(q: CheckoutQuote, sig: string): boolean {
  const a = Buffer.from(signQuote(q));
  const b = Buffer.from(sig);
  return a.length === b.length && timingSafeEqual(a, b);
}
