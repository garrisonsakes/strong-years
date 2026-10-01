/**
 * Offer catalog, checkout maths and the exact auto-renewal disclosure text.
 * ROSCA + state auto-renewal laws (OFFER.md 2.3, FUNNEL.md 5.1/5.5): the renewal
 * terms sit directly above the pay button, the consent box is separate and
 * unticked, and the exact text shown is stored in the consent log.
 */
import { blitz, messaging, offerRules, prices } from "./config";
import type { Arm } from "./db/types";

export type OfferCode = "trial" | "founding" | "reset" | "kitchen" | "gift3" | "gift12";

export interface OfferDef {
  code: OfferCode;
  name: string;
  short: string;
  kind: "membership" | "front_end" | "gift";
  frontEndCents?: number;
  giftMonths?: number;
  includes: string[];
}

export const PROGRAMS = [
  { slug: "strong-at-70", name: "Strong at 70" },
  { slug: "back-strong", name: "Back Strong" },
  { slug: "steady-feet", name: "Balance & Steady Feet" },
  { slug: "gut-reset", name: "Gut Reset with Sun Yoon" },
  { slug: "grip-hands", name: "Grip & Hands" },
  { slug: "walk-stronger", name: "Walk Stronger" },
] as const;

export function offerDef(code: OfferCode): OfferDef {
  switch (code) {
    case "trial":
      return {
        code,
        name: "7 days of Strong Years for $1",
        short: "$1 trial",
        kind: "membership",
        includes: [
          "Your Daily Practice: a new 8–12 minute session every day",
          "All six 12-week programs",
          "Monthly Strength Age retest",
          "Sun Yoon's Sunday recipes and grocery list",
          "Wednesday live Q&A with a real human coach",
        ],
      };
    case "founding":
      return {
        code,
        name: "Founding membership",
        short: "Founding membership",
        kind: "membership",
        includes: [
          "Everything in Strong Years, starting today",
          "Founding price locked while you stay subscribed (pauses included)",
          "14-day money-back guarantee, self-serve from your account",
        ],
      };
    case "reset":
      return {
        code,
        name: "7-Day Strength Reset",
        short: "$7 Strength Reset",
        kind: "front_end",
        frontEndCents: prices.reset,
        includes: ["7 follow-along sessions", "A printable 7-day plan, yours to keep"],
      };
    case "kitchen":
      return {
        code,
        name: "Sun Yoon's Strong Kitchen + Chang Yin's 12-Week Printable",
        short: "$17 Strong Kitchen",
        kind: "front_end",
        frontEndCents: prices.kitchen,
        includes: [
          "Sun Yoon's Strong Kitchen recipe collection (soft-food versions included)",
          "Weekly grocery template",
          "Chang Yin's printable 12-week plan",
        ],
      };
    case "gift3":
      return {
        code,
        name: "Give Strong Years: 3 months",
        short: "3-month gift",
        kind: "gift",
        giftMonths: 3,
        includes: ["3 months of Strong Years, prepaid", "A welcome card from Sun Yoon", "Never renews automatically"],
      };
    case "gift12":
      return {
        code,
        name: "Give Strong Years: 12 months",
        short: "12-month gift",
        kind: "gift",
        giftMonths: 12,
        includes: ["12 months of Strong Years, prepaid", "A welcome card from Sun Yoon", "Never renews automatically"],
      };
  }
}

export function isOfferCode(v: unknown): v is OfferCode {
  return typeof v === "string" && ["trial", "founding", "reset", "kitchen", "gift3", "gift12"].includes(v);
}

export function money(cents: number): string {
  const dollars = cents / 100;
  return Number.isInteger(dollars) ? `$${dollars}` : `$${dollars.toFixed(2)}`;
}

export function moneyExact(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export function addDays(d: Date, days: number): Date {
  return new Date(d.getTime() + days * 86_400_000);
}

export function addMonths(d: Date, months: number): Date {
  const r = new Date(d.getTime());
  const day = r.getUTCDate();
  r.setUTCDate(1);
  r.setUTCMonth(r.getUTCMonth() + months);
  const last = new Date(Date.UTC(r.getUTCFullYear(), r.getUTCMonth() + 1, 0)).getUTCDate();
  r.setUTCDate(Math.min(day, last));
  return r;
}

export function formatDate(d: Date | string, timeZone = "America/Los_Angeles"): string {
  const date = typeof d === "string" ? new Date(d) : d;
  return date.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric", timeZone });
}

export type Sku = "trial_fee" | "reset" | "kitchen" | "wallplan" | "membership" | "gift3" | "gift12";

export interface CheckoutLine {
  label: string;
  cents: number;
  kind: "trial_fee" | "front_end" | "bump" | "membership_first_month" | "gift";
  sku: Sku;
}

/** Order bumps. In blitz mode the $7 Reset and $17 Kitchen ride on the founding checkout as bumps. */
export type BumpKey = "wallplan" | "reset" | "kitchen";
export const BUMPS: Record<BumpKey, { label: string; cents: number }> = {
  wallplan: { label: "The Wall Plan (printable 12-week wall plan, retest sheet and habit tracker)", cents: prices.bump },
  reset: { label: "7-Day Strength Reset (7 sessions + printable plan, yours to keep)", cents: prices.reset },
  kitchen: { label: "Sun Yoon's Strong Kitchen + 12-Week Printable (yours to keep)", cents: prices.kitchen },
};
export const BUMP_ORDER: BumpKey[] = ["reset", "kitchen", "wallplan"];

export interface CheckoutQuote {
  offer: OfferCode;
  arm: Arm | null;
  lines: CheckoutLine[];
  todayCents: number;
  recurring: null | {
    priceCents: number;
    interval: "month";
    /** Date of the first recurring charge after today's payment */
    nextChargeAt: Date;
    trialDays: number;
    founding: boolean;
  };
  guaranteeDays: number | null;
  requiresAutoRenewConsent: boolean;
  /** The terms box, rendered as plain sentences (shown above the pay button and logged). */
  terms: string[];
  consentLabel: string | null;
  buttonLabel: string;
  underButton: string;
  bumpAllowed: boolean;
  /** Which bumps may be offered on this checkout. */
  bumpsAllowed: BumpKey[];
}

export interface QuoteInput {
  offer: OfferCode;
  arm: Arm;
  /** Legacy single bump flag = The Wall Plan. */
  bump?: boolean;
  bumps?: BumpKey[];
  /** Blitz: once the founding cohort is full, the offer becomes a standard (unlocked) membership. */
  cohortOpen?: boolean;
  standardCents?: number;
  /** Whether reminder texts are live (SMS_ENABLED); otherwise reminders go by email only. */
  smsOn?: boolean;
  now: Date;
  monthlyCents?: number;
  foundingCents?: number;
  gentle?: boolean;
  timeZone?: string;
  domain?: string;
}

/**
 * Arm A = $1 trial (and $7/$17 front ends with 7 days of membership included).
 * Arm B = charge-today founding membership (and $7/$17 front ends + first month today).
 */
export function quoteCheckout(input: QuoteInput): CheckoutQuote {
  const monthly = input.monthlyCents ?? prices.monthly;
  const founding = input.foundingCents ?? prices.founding;
  const tz = input.timeZone ?? "America/Los_Angeles";
  const domain = input.domain ?? "strongyears.com";
  const def = offerDef(input.offer);
  const lines: CheckoutLine[] = [];
  const bumpAllowed = !input.gentle && def.kind !== "gift";
  const smsOn = input.smsOn ?? messaging.smsEnabled;
  const remindBy = smsOn ? "by email and text" : "by email";
  // F09: "text CANCEL" is only offered while texting actually works.
  const cancelHow = `Cancel anytime online in at most two screens at ${domain}/account${smsOn ? ", by texting CANCEL" : ""}. Emailing us also works: a person reads it within one business day, so use your account for a same-day cancel.`;
  const cohortOpen = input.cohortOpen ?? true;
  // Reset/Kitchen are bumps only on the founding checkout (never on their own product page).
  const bumpsAllowed: BumpKey[] = bumpAllowed
    ? BUMP_ORDER.filter((b) => b === "wallplan" || input.offer === "founding")
    : [];
  const chosen = new Set<BumpKey>([...(input.bumps ?? []), ...(input.bump ? (["wallplan"] as BumpKey[]) : [])]);

  if (def.kind === "gift") {
    const cents = input.offer === "gift3" ? prices.gift3 : prices.gift12;
    lines.push({ label: def.name, cents, kind: "gift", sku: input.offer === "gift3" ? "gift3" : "gift12" });
    const todayCents = cents;
    return {
      offer: input.offer,
      arm: null,
      lines,
      todayCents,
      recurring: null,
      guaranteeDays: null,
      requiresAutoRenewConsent: false,
      terms: [
        `Today: ${money(todayCents)}, one payment.`,
        `This gift is prepaid for ${def.giftMonths} months and never renews automatically. Nobody is charged again.`,
        "When the gift ends, we ask the recipient whether they want to continue on their own card. Nothing continues without their fresh consent.",
        "Refundable in full to you until the recipient starts the gift.",
      ],
      consentLabel: null,
      buttonLabel: `Pay ${money(todayCents)} for the gift`,
      underButton: "One payment. No subscription. No automatic renewal.",
      bumpAllowed: false,
      bumpsAllowed: [],
    };
  }

  // Arm B uses the founding price; arm A uses the monthly price after the trial.
  const armB = input.arm === "B";
  const standardPath = armB && !cohortOpen;
  const priceCents = armB ? (standardPath ? (input.standardCents ?? founding) : founding) : cohortOpen ? monthly : (input.standardCents ?? monthly);
  const memberLine = standardPath ? "Strong Years membership, first month" : "Strong Years founding membership, first month";
  let nextChargeAt: Date;
  let trialDays = 0;

  if (input.offer === "trial" || input.offer === "founding") {
    if (input.offer === "trial") {
      lines.push({ label: "7-day trial of Strong Years", cents: prices.trialFee, kind: "trial_fee", sku: "trial_fee" });
      trialDays = offerRules.trialDays;
      nextChargeAt = addDays(input.now, trialDays);
    } else {
      lines.push({ label: memberLine, cents: priceCents, kind: "membership_first_month", sku: "membership" });
      nextChargeAt = addMonths(input.now, 1);
    }
  } else {
    lines.push({ label: def.name, cents: def.frontEndCents ?? 0, kind: "front_end", sku: input.offer === "reset" ? "reset" : "kitchen" });
    if (armB) {
      lines.push({ label: memberLine, cents: priceCents, kind: "membership_first_month", sku: "membership" });
      nextChargeAt = addMonths(input.now, 1);
    } else {
      trialDays = offerRules.trialDays;
      nextChargeAt = addDays(input.now, trialDays);
    }
  }

  for (const b of BUMP_ORDER) {
    if (chosen.has(b) && bumpsAllowed.includes(b)) lines.push({ label: BUMPS[b].label, cents: BUMPS[b].cents, kind: "bump", sku: b });
  }

  const todayCents = lines.reduce((s, l) => s + l.cents, 0);
  const price = moneyExact(priceCents);
  const next = formatDate(nextChargeAt, tz);
  const isFoundingPath = armB && input.offer !== "trial" && !standardPath;
  const guaranteeDays = armB && input.offer !== "trial" ? offerRules.guaranteeDaysFoundingArm : offerRules.guaranteeDaysTrialArm;

  const terms: string[] = [];
  if (input.offer === "trial") {
    terms.push(`Today: ${moneyExact(todayCents)}. Your 7-day trial starts now.`);
    terms.push(`On ${next}, your Strong Years membership renews at ${price}, then ${price} every month on the same date, until you cancel.`);
    terms.push(`${cancelHow} Cancel before ${next} and you won't be charged again.`);
    terms.push(`We'll remind you ${remindBy} 48 hours before your trial ends.`);
    terms.push(`14-day money-back guarantee on your first full membership charge (${price}), counted from the day of that charge, self-serve from your account. One guarantee per person.`);
  } else if (input.offer === "founding") {
    const extras = lines.filter((l) => l.kind === "bump");
    terms.push(
      `Today: ${moneyExact(todayCents)}. That is your first month of Strong Years, charged now${extras.length ? `, plus ${extras.map((l) => `${moneyExact(l.cents)} for ${l.label.split(" (")[0]}`).join(" and ")} (one-time, yours to keep)` : ""}.`,
    );
    terms.push(
      standardPath
        ? `On ${next}, your membership renews at ${price}, then ${price} every month on the same date, until you cancel.`
        : `On ${next}, your membership renews at ${price}, then ${price} every month on the same date, until you cancel. Your founding price stays at ${price} for as long as you stay subscribed.`,
    );
    terms.push(cancelHow);
    terms.push(`We'll remind you ${remindBy} 48 hours before every charge.`);
    terms.push(`14-day money-back guarantee: tap Refund in your account within 14 days of today and you get the full ${price} membership charge back (one guarantee per person).${extras.length ? " Add-ons are one-time purchases: faulty or not as described, we fix or refund them on request within 14 days." : ""}`);
  } else if (armB) {
    const productName = def.name;
    terms.push(`Today: ${moneyExact(todayCents)}. That is ${money(def.frontEndCents ?? 0)} for the ${productName} (yours to keep) plus your first month of Strong Years (${price}).`);
    terms.push(`On ${next}, your membership renews at ${price}, then every month on the same date, until you cancel.`);
    terms.push(cancelHow);
    terms.push(`We'll remind you ${remindBy} 48 hours before every charge.`);
    terms.push("14-day money-back guarantee on the membership charge, self-serve from your account.");
  } else {
    const productName = def.name;
    terms.push(`Today: ${moneyExact(todayCents)} for the ${productName} (yours to keep). It includes 7 days of Strong Years.`);
    terms.push(`On ${next}, your membership renews at ${price}/month until you cancel.`);
    terms.push(`${cancelHow} Cancel before ${next} and you won't be charged again.`);
    terms.push(`We'll remind you ${remindBy} 48 hours before.`);
    terms.push("14-day money-back guarantee on your first full membership charge, counted from the day of that charge.");
  }

  const consentLabel = `I agree to the automatic renewal terms above: ${moneyExact(todayCents)} today, then ${price}/month from ${next} until I cancel. I can cancel online anytime.`;

  const buttonLabel =
    input.offer === "trial"
      ? "Start my $1 trial"
      : input.offer === "founding"
        ? `Join for ${money(priceCents)} today`
        : `Pay ${moneyExact(todayCents)} and start`;

  return {
    offer: input.offer,
    arm: input.arm,
    lines,
    todayCents,
    recurring: { priceCents, interval: "month", nextChargeAt, trialDays, founding: isFoundingPath },
    guaranteeDays,
    requiresAutoRenewConsent: true,
    terms,
    consentLabel,
    buttonLabel,
    underButton: `Then ${price}/month from ${next}. Cancel anytime online.`,
    bumpAllowed,
    bumpsAllowed,
  };
}

export interface ConsentInput {
  quote: CheckoutQuote;
  autoRenewChecked: boolean;
  ageChecked: boolean;
  email: string;
  firstName: string;
  smsChecked: boolean;
  phone: string;
  foundingSpotsLeft: number;
}

export type ConsentError = { field: string; message: string };

/** Server-side validation. Nothing is ever pre-ticked, and nothing is inferred. */
export function validateCheckout(input: ConsentInput): ConsentError[] {
  const errors: ConsentError[] = [];
  if (!input.firstName.trim()) errors.push({ field: "first_name", message: "Please tell us your first name." });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.email.trim())) {
    errors.push({ field: "email", message: "Please check your email address." });
  }
  if (input.quote.requiresAutoRenewConsent && !input.autoRenewChecked) {
    errors.push({ field: "auto_renew", message: "Please tick the box above to confirm the membership terms." });
  }
  if (!input.ageChecked) errors.push({ field: "age_18", message: "Strong Years is for adults. Please confirm you are 18 or older." });
  if (input.smsChecked && !/^\+?[0-9 ()-]{10,20}$/.test(input.phone.trim())) {
    errors.push({ field: "phone", message: "Please enter a mobile number for your daily text, or untick the text box." });
  }
  if (input.quote.recurring?.founding && input.foundingSpotsLeft <= 0) {
    // L4: only mention the trial when the trial arm is actually on.
    errors.push({
      field: "offer",
      message: blitz.trialArmEnabled
        ? "The founding cohort is full. The $1 trial is still open."
        : "The founding cohort just filled up. Nothing was charged. Please reload the page to see the current membership price.",
    });
  }
  return errors;
}

export const SMS_CONSENT_TEXT =
  "Text me my daily session link. Msg frequency varies, about 1/day. Msg & data rates may apply. Reply STOP to cancel, HELP for help. Consent is not a condition of purchase.";

export const AGE_CONSENT_TEXT = "I am 18 or older.";

export function foundingSpots(claimed: number, cap = offerRules.foundingCap) {
  const left = Math.max(0, cap - claimed);
  return { claimed, cap, left, open: left > 0 };
}
