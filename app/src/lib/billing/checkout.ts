/**
 * Creates the checkout intent (our record of what the buyer saw and agreed to),
 * logs consent, then hands off to Stripe Checkout, or to the built-in simulator
 * when STRIPE_SECRET_KEY is absent.
 */
import { blitz, env, prices } from "../config";
import type { Store } from "../db/store";
import type { Arm, Attribution, CheckoutIntent } from "../db/types";
import { normalizeEmail } from "../members";
import { foundingTaken, holdsFoundingSpot, reserveFoundingSpot } from "../founding";
import { moneyExact } from "../pricing";
import { liveQuoteInputs } from "../livePricing";
import {
  AGE_CONSENT_TEXT,
  SMS_CONSENT_TEXT,
  foundingSpots,
  offerDef,
  quoteCheckout,
  type BumpKey,
  validateCheckout,
  type CheckoutQuote,
  type ConsentError,
  type OfferCode,
} from "../pricing";
import { mockCheckoutAllowed, processorFor, routeCheckout } from "./processors";
import { quoteSigMatches } from "../quoteSig";
import { resolveFoundingOffer, testCell } from "../blitz";
import { offerRules } from "../config";
import { PRELAUNCH_MESSAGE, isCheckoutOpen } from "../launch";

export interface StartCheckoutInput {
  offer: OfferCode;
  arm: Arm;
  bump?: boolean;
  bumps?: BumpKey[];
  gentle: boolean;
  visitorId?: string | null;
  email: string;
  firstName: string;
  phone: string;
  smsConsent: boolean;
  autoRenewConsent: boolean;
  ageConsent: boolean;
  /** M1: signature of the quote the buyer saw. Undefined only for internal callers. */
  quoteSig?: string;
  /** NEW-1: the member id of a logged-in session that started this checkout, if any. */
  authMemberId?: string | null;
  gift: CheckoutIntent["gift"];
  attribution: Attribution | null;
  leadId: string | null;
  ip: string | null;
  userAgent: string | null;
  /** Optional, unticked by default: hashed-email ad measurement (lib/conversions). */
  adConsent?: boolean;
  now?: Date;
}

export type StartCheckoutResult = { ok: true; redirectUrl: string; intentId: string; quote: CheckoutQuote } | { ok: false; errors: ConsentError[]; cohortFull?: boolean };

export async function startCheckout(store: Store, input: StartCheckoutInput): Promise<StartCheckoutResult> {
  const now = input.now ?? new Date();
  // Organic launch: in prelaunch nothing can start a payment, whichever route calls this.
  if (!(await isCheckoutOpen(store, now))) return { ok: false, errors: [{ field: "form", message: PRELAUNCH_MESSAGE }] };
  const domain = env.siteUrl.replace(/^https?:\/\//, "");
  // Round 8: live holds count too, so a full cohort shows the standard price right away.
  const claimed = await foundingTaken(store, now);
  const spots = foundingSpots(claimed);
  // Blitz: price cell (sticky per visitor) and real cohort state decide the membership price.
  const fo = resolveFoundingOffer({
    visitorId: input.visitorId ?? null,
    claimed,
    cap: offerRules.foundingCap,
    testOn: blitz.enabled && blitz.priceTestOn,
    cells: blitz.priceCells,
    defaultCents: blitz.enabled ? blitz.defaultPriceCents : prices.founding,
    standardCents: blitz.enabled ? blitz.standardPriceCents : prices.founding,
  });
  const quote = quoteCheckout({
    offer: input.offer,
    arm: input.arm,
    bump: input.bump,
    bumps: input.bumps,
    now,
    gentle: input.gentle,
    timeZone: env.displayTimeZone,
    domain,
    // Round 9: the same inputs every page's price mention uses (lib/livePricing.ts).
    ...liveQuoteInputs(fo, input.arm),
  });
  const errors = validateCheckout({
    quote,
    autoRenewChecked: input.autoRenewConsent,
    ageChecked: input.ageConsent,
    email: input.email,
    firstName: input.firstName,
    smsChecked: input.smsConsent,
    phone: input.phone,
    foundingSpotsLeft: spots.left,
  });
  const def = offerDef(input.offer);
  if (def.kind === "gift") {
    if (!input.gift?.recipient_name.trim()) errors.push({ field: "recipient_name", message: "Who is the gift for?" });
    if (!input.gift || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.gift.recipient_email)) {
      errors.push({ field: "recipient_email", message: "Please add their email so we can send the welcome card." });
    }
  }
  if (errors.length) return { ok: false, errors };
  if (input.quoteSig !== undefined && !quoteSigMatches(quote, input.quoteSig)) {
    return { ok: false, errors: [{ field: "form", message: "The price or terms changed while this page was open. Nothing was charged. Please reload the page, read the updated terms, and try again." }] };
  }

  const email = normalizeEmail(input.email);
  const base = { email, member_id: null, ip: input.ip, user_agent: input.userAgent, offer_code: input.offer };
  let consentId: string | null = null;
  if (quote.requiresAutoRenewConsent) {
    const c = await store.insert("consent_log", {
      ...base,
      kind: "auto_renew",
      checked: true,
      text_shown: [...quote.terms, `Checkbox: ${quote.consentLabel}`].join("\n"),
      price_cents: quote.recurring?.priceCents ?? null,
      first_charge_at: quote.recurring?.nextChargeAt.toISOString() ?? null,
    });
    consentId = c.id;
  }
  await store.insert("consent_log", { ...base, kind: "age_18", checked: true, text_shown: AGE_CONSENT_TEXT, price_cents: null, first_charge_at: null });
  if (input.smsConsent) {
    await store.insert("consent_log", { ...base, kind: "sms", checked: true, text_shown: SMS_CONSENT_TEXT, price_cents: null, first_charge_at: null });
  }

  const intent = await store.insert("checkout_intents", {
    email,
    first_name: input.firstName.trim(),
    phone: input.smsConsent ? input.phone.trim() : null,
    offer_code: input.offer,
    arm: def.kind === "gift" ? null : input.arm,
    bump: quote.lines.some((l) => l.kind === "bump"),
    gentle: input.gentle,
    amount_today_cents: quote.todayCents,
    lines: quote.lines,
    membership_price_cents: quote.recurring?.priceCents ?? null,
    trial_days: quote.recurring?.trialDays ?? 0,
    consent_id: consentId,
    sms_consent: input.smsConsent,
    age_confirmed: input.ageConsent,
    gift: def.kind === "gift" ? input.gift : null,
    attribution: input.attribution,
    // Recorded as consent only at fulfilment, and only if the buyer owns the email (NEW-1).
    // A Do Not Sell/Share or GPC signal on this request outranks the box.
    ad_consent: input.adConsent === true && !input.attribution?.ad_opt_out && def.kind !== "gift",
    lead_id: input.leadId,
    status: "open",
    processor: "stripe",
    // The live test cell: p2500 / p3000 (founding) or trial2500 (the $1 trial), logged per intent.
    price_cell: def.kind === "gift" ? null : testCell(input.arm, fo, prices.monthly),
    visitor_id: input.visitorId ?? null,
    auth_member_id: input.authMemberId ?? null,
    buyer_is_owner: null,
    verification: null,
    verify_token_hash: null,
    verify_expires_at: null,
    stripe_customer_id: null,
    stripe_session_id: null,
    member_id: null,
  });

  // Round 8: take a founding spot atomically before any payment page exists.
  if (holdsFoundingSpot(intent) && !(await reserveFoundingSpot(store, intent.id, offerRules.foundingCap, now))) {
    await store.update("checkout_intents", intent.id, { status: "failed" });
    const standard = blitz.enabled ? blitz.standardPriceCents : prices.founding;
    return {
      ok: false,
      cohortFull: true,
      errors: [
        {
          field: "form",
          message: `The last founding spot was taken while you were checking out, so we stopped here. Nothing was charged. Membership is now ${moneyExact(standard)} a month (the standard price). Reload the page to see the updated terms before you decide.`,
        },
      ],
    };
  }

  const route = await routeCheckout(store, input.visitorId ?? intent.id, quote.todayCents);
  if (!route.id) return { ok: false, errors: [{ field: "form", message: "Payments are paused for a moment. Nothing was charged. Please try again shortly." }] };
  const processor = processorFor(route.id);
  if (processor.status() === "mock" && !mockCheckoutAllowed()) {
    return { ok: false, errors: [{ field: "form", message: "Payments aren't switched on yet. Nothing was charged." }] };
  }
  const { redirectUrl, externalId } = await processor.createCheckout({ ...intent, processor: route.id }, quote);
  await store.update("checkout_intents", intent.id, { processor: route.id, stripe_session_id: route.id === "stripe" ? externalId : null });
  return { ok: true, redirectUrl, intentId: intent.id, quote };
}
