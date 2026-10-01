import Link from "next/link";
import type { Member, Membership } from "@/lib/db/types";
import { accessUntil, withinGuarantee } from "@/lib/billing/cancel";
import { shopifyConfig } from "@/lib/billing/shopify";
import { formatDate, moneyExact } from "@/lib/pricing";
import { env } from "@/lib/config";
import { requestAnnual, requestRefund } from "@/app/app/actions";
import { canOfferAnnual } from "@/lib/billing/planChange";

const LAPSED: Record<string, string> = {
  none: "Your account doesn't have a membership yet, so the sessions and coaches aren't open.",
  ended: "Your membership has ended, so the sessions and coaches are closed. Your progress is saved for 90 days.",
  refunded: "Your membership was refunded and has ended. Your progress is saved for 90 days.",
};

function planName(m: Membership): string {
  if (m.plan === "essentials") return "Strong Years Essentials";
  if (m.plan === "gift") return "Strong Years (gift)";
  if (m.plan === "annual") return m.founding ? "Founding membership, yearly" : "Strong Years, yearly";
  return m.founding ? "Founding membership" : "Strong Years monthly";
}

function statusLine(m: Membership, tz: string, now: number): { text: string; tone: "ok" | "warn" | "ended" } {
  const until = accessUntil(m);
  if (m.status === "refunded") return { text: "Refunded and ended.", tone: "ended" };
  if (m.status === "expired") return { text: "Ended.", tone: "ended" };
  if (m.status === "paused") return { text: "Paused. Nothing is charged while paused.", tone: "warn" };
  if (m.status === "canceled" || m.cancel_at_period_end) return { text: `Cancelled. You have access until ${until ? formatDate(until, tz) : "the end of your paid period"}.`, tone: "warn" };
  if (m.status === "past_due") {
    const g = m.grace_until ? new Date(m.grace_until).getTime() : null;
    if (g && g <= now) return { text: "Your last payment didn't go through, so the sessions are closed until it does. Update your card below.", tone: "ended" };
    return { text: `Your last payment didn't go through. Everything stays open${m.grace_until ? ` until ${formatDate(m.grace_until, tz)}` : ""} while you update your card.`, tone: "warn" };
  }
  return { text: "Active", tone: "ok" };
}

/**
 * The membership page in Shopify mode. Everything shown comes from our database
 * (kept current by Shopify webhooks). Cancel, pause, card and the yearly switch
 * happen on the Shopify customer account page; the 14-day refund happens here.
 */
export function ShopifyAccount({ member, m, sp, chargeCount }: { member: Member; m: Membership | null; sp: Record<string, string | undefined>; chargeCount: number }) {
  const tz = member.timezone || env.displayTimeZone;
  const now = Date.now();
  const manage = shopifyConfig.customerAccountUrl();
  const s = m ? statusLine(m, tz, now) : null;
  const live = m && !["refunded", "expired"].includes(m.status) && !(m.status === "canceled" && !m.cancel_at_period_end);
  const offerYearly = Boolean(m && canOfferAnnual(m, chargeCount));

  return (
    <div className="narrow space-y-6 py-2" data-testid="account">
      <h1 className="text-4xl">Your membership</h1>
      {sp.lapsed && LAPSED[sp.lapsed] && (
        <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="status" data-testid="lapsed">
          {LAPSED[sp.lapsed]}
        </p>
      )}
      {sp.paused && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="status">Your membership is paused, so the sessions and coaches are resting too. Resume it on your store account below whenever you like.</p>}
      {sp.refund === "done" && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status">Refunded. It usually shows on your card in 5–10 days. Your membership has ended and you won&apos;t be charged again.</p>}
      {sp.refund === "review" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="alert">A person on our team will finish this refund by email within one business day. Nothing has changed yet.</p>}
      {sp.refund === "ineligible" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="alert">This is outside the self-serve refund window. Reply to any email and a person will help.</p>}
      {sp.annual === "requested" && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status" data-testid="annual-requested">Got it. A person on our team emails you within 1 business day with the $249 Founding Annual checkout; your monthly plan ends the day you pay it, so you are never charged for both. Nothing changes until then.</p>}

      {m && s ? (
        <section className="card space-y-3" aria-labelledby="plan-name" data-testid="membership-card">
          <p id="plan-name" className="font-display text-3xl">{planName(m)}</p>
          <p className={`inline-block rounded-xl border-2 border-ink px-3 py-1 text-lg font-bold ${s.tone === "ok" ? "bg-jade text-rice" : s.tone === "warn" ? "bg-brass text-ink" : "bg-rice text-ink"}`} data-testid="membership-status">
            {s.text}
          </p>
          {m.plan !== "gift" && (
            <p className="text-lg">
              <strong>{moneyExact(m.price_cents)}</strong> a {m.interval === "year" ? "year" : "month"}
              {m.founding ? ", the founding price, locked for as long as you stay subscribed (pauses included)." : "."}
            </p>
          )}
          {live && m.status !== "paused" && !m.cancel_at_period_end && m.current_period_end && m.plan !== "gift" && (
            <p className="text-lg font-bold">Next charge: {formatDate(m.current_period_end, tz)}, {moneyExact(m.price_cents)}. We email you before every charge.</p>
          )}
          {m.first_paid_at && <p>Member since {formatDate(m.first_paid_at, tz)}.</p>}
        </section>
      ) : (
        <section className="card space-y-4">
          <p className="text-xl font-bold">You don&apos;t have a membership on this email address yet.</p>
          <p>If you bought with a different email, sign out and sign in with that one.</p>
          <a href="/join" className="btn-primary">See how to join</a>
        </section>
      )}

      {m && live && m.plan !== "gift" && (
        <section className="card space-y-4" aria-labelledby="manage" data-testid="manage">
          <h2 id="manage" className="text-2xl">Change or cancel</h2>
          <p>
            Your subscription lives on the Strong Years store; card changes, pauses and the final cancel step happen there, signed in with the same email. Cancelling takes two taps, and nobody will call you.
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <Link href="/app/account/cancel" className="btn-outline sm:w-full" data-testid="manage-cancel">
              {m.status === "paused" ? "Resume or cancel" : "Cancel, pause or pay less"}
            </Link>
            <a href={manage} className="btn-outline sm:w-full" data-testid="manage-card" rel="noopener">
              Update my card
            </a>
            {offerYearly && (
              <form action={requestAnnual} className="sm:col-span-2">
                <button type="submit" className="btn-jade sm:w-full" data-testid="manage-yearly">
                  Switch to yearly: $249 a year at the founding price
                </button>
                <p className="fine mt-2">Shopify can&apos;t swap plans by itself: a person on our team sends you the $249 checkout within 1 business day and ends the monthly plan the day you pay it. Nothing changes until then.</p>
              </form>
            )}
          </div>
        </section>
      )}

      {m && withinGuarantee(m, now) && m.plan !== "gift" && (
        <section className="card space-y-3" aria-labelledby="refund" data-testid="refund">
          <h2 id="refund" className="text-2xl">14-day money-back guarantee</h2>
          <p>You&apos;re inside your money-back window, until {formatDate(m.guarantee_until!, tz)}. One tap refunds your membership charge in full and ends the membership.</p>
          <form action={requestRefund}>
            <button type="submit" className="btn-outline sm:w-auto">Refund my membership payment</button>
          </form>
          <p className="fine">
            Books and add-ons are one-time purchases with their own terms. One money-back guarantee per person.{" "}
            <Link href="/refunds" className="font-bold underline">Refund policy</Link>
          </p>
        </section>
      )}

      <section className="card">
        <h2 className="text-2xl">Other ways to cancel</h2>
        <p className="mt-2">Reply &ldquo;cancel&rdquo; to any of our emails and a person will do it for you. You never need to call{env.billingPhone ? ` (for billing questions our line is ${env.billingPhone})` : ""}.</p>
      </section>
    </div>
  );
}
