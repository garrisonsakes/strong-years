import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { fulfillCheckoutIntent } from "@/lib/billing/fulfill";
import { stripe } from "@/lib/billing/stripeClient";
import { SESSION_COOKIE } from "@/lib/auth/session";
import { purchaseCookieOptions, sessionCookieOptions, sessionCookieValue } from "@/lib/auth/server";
import { offerDef, type OfferCode } from "@/lib/pricing";
import { refuseIfPrelaunch } from "@/lib/launchGuard";

/**
 * Stripe success_url. Verifies the session with Stripe, fulfils idempotently (in case the
 * webhook hasn't arrived yet), saves the payment method for one-click upsells, signs the
 * buyer in, then starts the upsell ladder.
 */
export async function GET(req: Request) {
  const closed = await refuseIfPrelaunch(req, "redirect");
  if (closed) return closed;
  const url = new URL(req.url);
  const intentId = url.searchParams.get("intent") ?? "";
  const store = await getStore();
  const intent = await store.get("checkout_intents", intentId);
  if (!intent) return NextResponse.redirect(new URL("/start", url.origin), 303);

  const s = intent.processor === "braintree" ? null : stripe();
  let memberId = intent.member_id;
  if (s) {
    const sessionId = url.searchParams.get("session_id") ?? intent.stripe_session_id;
    if (!sessionId) return NextResponse.redirect(new URL("/start", url.origin), 303);
    const session = await s.checkout.sessions.retrieve(sessionId, { expand: ["subscription", "payment_intent", "subscription.default_payment_method"] });
    if (session.metadata?.intent_id !== intent.id || session.status !== "complete") {
      return NextResponse.redirect(new URL(`/checkout/${intent.offer_code}?canceled=1`, url.origin), 303);
    }
    const sub = typeof session.subscription === "object" ? session.subscription : null;
    const pi = typeof session.payment_intent === "object" ? session.payment_intent : null;
    const pm = sub?.default_payment_method ? (typeof sub.default_payment_method === "string" ? sub.default_payment_method : sub.default_payment_method.id) : pi?.payment_method ? String(typeof pi.payment_method === "string" ? pi.payment_method : pi.payment_method.id) : null;
    const pmObj = sub && typeof sub.default_payment_method === "object" ? sub.default_payment_method : null;
    const res = await fulfillCheckoutIntent(store, intent.id, {
      stripeCustomerId: typeof session.customer === "string" ? session.customer : session.customer?.id ?? null,
      stripeSubscriptionId: sub?.id ?? (typeof session.subscription === "string" ? session.subscription : null),
      stripePaymentIntentId: pi?.id ?? null,
      stripeInvoiceId: typeof session.invoice === "string" ? session.invoice : session.invoice?.id ?? null,
      stripePaymentMethodId: pm,
      cardFingerprint: pmObj?.card?.fingerprint ?? null,
    });
    // NEW-1: the card is only saved onto the account when the buyer owns it.
    const owner = (await store.get("checkout_intents", intent.id))?.buyer_is_owner === true;
    if (owner && pm && !res.member.stripe_payment_method) await store.update("members", res.member.id, { stripe_payment_method: pm });
    if (res.membership && !res.membership.stripe_subscription_id && sub) await store.update("memberships", res.membership.id, { stripe_subscription_id: sub.id });
    memberId = res.member.id;
  } else if (intent.status !== "complete") {
    return NextResponse.redirect(new URL(`/checkout/mock/${intent.id}`, url.origin), 303);
  }
  if (!memberId) return NextResponse.redirect(new URL("/login", url.origin), 303);

  const def = offerDef(intent.offer_code as OfferCode);
  const fresh = await store.get("checkout_intents", intent.id);
  // NEW-1: checkout never signs anyone into an account that existed before it. Only a
  // brand-new account (or a buyer who was already signed in as that member) continues.
  if (def.kind !== "gift" && fresh?.buyer_is_owner !== true) {
    return NextResponse.redirect(new URL("/checkout/check-email", url.origin), 303);
  }
  // L15: gift buyers' cards aren't kept, so there's no one-click add-on after a gift.
  const next = def.kind === "gift" ? "/gift/thanks" : intent.gentle ? "/welcome" : "/upsell/program";
  const res = NextResponse.redirect(new URL(next, url.origin), 303);
  if (fresh?.buyer_is_owner !== true) return res; // gift bought with an existing member's email: no session
  // M2: this URL signs the buyer in once, within 30 minutes of paying. After that
  // (browser history, a shared device) it just continues to the next page.
  const completedAt = fresh?.completed_at ? new Date(fresh.completed_at).getTime() : 0;
  if (completedAt && Date.now() - completedAt < 30 * 60_000) {
    const [claimed] = await store.updateWhere("checkout_intents", { id: intent.id, login_consumed_at: null }, { login_consumed_at: new Date().toISOString() });
    if (claimed) {
      // R2-1: typing an email at checkout proves nothing. An unverified email only gets a
      // short purchase-scoped session (upsells, receipt), never the account; the welcome
      // email carries the link that verifies the inbox and opens the program.
      const verified = Boolean((await store.get("members", memberId))?.email_verified_at);
      if (verified) res.cookies.set(SESSION_COOKIE, await sessionCookieValue(memberId, "full"), sessionCookieOptions);
      else res.cookies.set(SESSION_COOKIE, await sessionCookieValue(memberId, "purchase"), purchaseCookieOptions);
    }
  }
  return res;
}
