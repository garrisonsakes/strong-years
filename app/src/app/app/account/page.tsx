import Link from "next/link";
import { currentMembership, memberships, requireMember } from "@/lib/auth/server";
import { env, messaging, mode } from "@/lib/config";
import { grantsAccess } from "@/lib/entitlement";
import { accessUntil, withinGuarantee } from "@/lib/billing/cancel";
import { describeNextCharge } from "@/lib/billing/webhook";
import { formatDate, moneyExact } from "@/lib/pricing";
import { openPortal, requestRefund, resume, runDemoClock, undoCancellation } from "../actions";
import { isShopify } from "@/lib/billing/provider";
import { ShopifyAccount } from "@/components/ShopifyAccount";
import { getStore } from "@/lib/db";

const NOTICE: Record<string, string> = {
  undone: "Your cancellation is undone. Your membership continues.",
  resumed: "Welcome back. Your membership is active again.",
  clock: "Demo billing clock ran: reminders and any due charges were processed.",
};

export default async function Account({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const member = await requireMember();
  const m = await currentMembership(member.id);
  if (isShopify()) {
    const chargeCount = m ? await (await getStore()).count("sy_orders", { membership_id: m.id, kind: "membership_charge", status: "paid" }) : 0;
    return <ShopifyAccount member={member} m={m} sp={sp} chargeCount={chargeCount} />;
  }
  const all = await memberships(member.id);
  const others = all.filter((x) => x.id !== m?.id && grantsAccess(x));
  const pending = all.filter((x) => x.pending_verification && x.status !== "canceled");
  const tz = member.timezone || env.displayTimeZone;
  const notice = Object.keys(NOTICE).find((k) => sp[k]);
  const planName = !m ? "No membership" : m.plan === "essentials" ? "Strong Years Essentials" : m.plan === "gift" ? "Strong Years (gift)" : m.plan === "annual" ? "Strong Years yearly" : m.founding ? "Strong Years founding membership" : "Strong Years monthly";

  return (
    <div className="narrow space-y-6" data-testid="account">
      <h1 className="text-4xl">Your membership</h1>
      {notice && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status">{NOTICE[notice]}</p>}
      {sp.paused && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="status">Your membership is paused, so the sessions and coaches are resting too. Resume below whenever you like.</p>}
      {sp.refund === "done" && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status">Refunded. Your card company confirmed it; it usually shows in 5–10 days. Your membership has ended.</p>}
      {sp.refund === "pending" && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status">Refund requested. Your bank is still processing it, and we&apos;ll email you when it&apos;s confirmed. You won&apos;t be charged again.</p>}
      {sp.refund === "review" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="alert">A person on our team will finish this refund by email within one business day. Nothing has changed yet.</p>}
      {sp.refund === "ineligible" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="alert">This is outside the self-serve refund window. Reply to any email and a person will help.</p>}
      {sp.portal === "demo" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold">Demo mode: with Stripe keys set, this button opens the Stripe Customer Portal to update your card and download invoices.</p>}

      {m ? (
        <section className="card space-y-3">
          <p className="text-2xl font-bold">{planName}</p>
          <p>
            Status:{" "}
            <strong>
              {m.cancel_at_period_end || m.status === "canceled"
                ? `Cancelled. Access until ${accessUntil(m) ? formatDate(accessUntil(m)!, tz) : "the end of your period"}.`
                : m.status === "trialing"
                  ? `7-day trial, ends ${formatDate(m.trial_end ?? m.current_period_end!, tz)}`
                  : m.status === "paused"
                    ? `Paused until ${m.paused_until ? formatDate(m.paused_until, tz) : "you resume"}. Nothing is charged while paused.`
                    : m.status === "refunded"
                      ? "Refunded and ended."
                      : m.status === "past_due"
                        ? "Your last payment didn't go through. Please update your card."
                        : "Active"}
            </strong>
          </p>
          {m.plan !== "gift" && <p>Price: {moneyExact(m.price_cents)} a month{m.partner_seat ? ` + ${moneyExact(800)} partner seat` : ""}{m.founding ? ", founding price locked while you stay subscribed" : ""}.</p>}
          {describeNextCharge(m) && m.status !== "paused" && m.plan !== "gift" && <p className="text-lg font-bold">Next charge: {describeNextCharge(m)}</p>}
          {(m.gift_credit_cents ?? 0) > 0 && <p>Gift credit: {moneyExact(m.gift_credit_cents)}, used on your next charges before your card.</p>}
          {m.plan === "gift" && m.current_period_end && <p>Prepaid gift until {formatDate(m.current_period_end, tz)}. It never renews and nothing will be charged.</p>}
          <p>On your statement: STRONGYEARS MEMBER.</p>
        </section>
      ) : (
        <p className="card">You don&apos;t have an active membership. <Link href="/start" className="font-bold underline">See ways to start</Link></p>
      )}

      {pending.length > 0 && (
        <p className="card font-bold" data-testid="pending-purchase">
          A purchase made with your email address is waiting for your confirmation. We emailed you a link: open it to confirm, or to tell us it wasn&apos;t you. Until then it doesn&apos;t change anything on your account.
        </p>
      )}
      {others.map((o) => (
        <p key={o.id} className="card" data-testid="other-membership">
          Also on your account: a prepaid gift until {o.current_period_end ? formatDate(o.current_period_end, tz) : "its end date"}. It never renews and has nothing to cancel.
        </p>
      ))}

      {m && m.plan !== "gift" && (
        <section className="grid gap-3 sm:grid-cols-2">
          <form action={openPortal}>
            <button type="submit" className="btn-outline sm:w-full">Update card or see invoices</button>
          </form>
          {m.cancel_at_period_end ? (
            <form action={undoCancellation}>
              <button type="submit" className="btn-outline sm:w-full">Undo cancellation</button>
            </form>
          ) : m.status === "paused" ? (
            <form action={resume}>
              <button type="submit" className="btn-outline sm:w-full">Resume now</button>
            </form>
          ) : m.status !== "refunded" && m.status !== "canceled" ? (
            <Link href="/app/account/cancel" className="btn-outline sm:w-full" data-testid="cancel-link">
              Cancel membership
            </Link>
          ) : null}
          {withinGuarantee(m) && (
            <form action={requestRefund} className="sm:col-span-2">
              <p className="mb-2 font-bold">You&apos;re inside your money-back window (until {formatDate(m.guarantee_until!, tz)}).</p>
              <button type="submit" className="btn-outline sm:w-full">Refund my membership payment</button>
              <p className="fine mt-2">
                This refunds your membership charge and ends the membership. Add-ons are one-time purchases with their own terms. One money-back guarantee per person.{" "}
                <Link href="/refunds" className="font-bold underline">Refund policy</Link>
              </p>
            </form>
          )}
          {m.status === "paused" && (
            <Link href="/app/account/cancel" className="btn-outline sm:w-full">
              Cancel membership
            </Link>
          )}
        </section>
      )}

      <section className="card">
        <h2 className="text-2xl">Other ways to cancel</h2>
        <p className="mt-2">
          {messaging.smsEnabled ? "Text CANCEL to our number, or reply" : "Reply"} &ldquo;cancel&rdquo; to any of our emails. Nobody will call you, and you never need to call us to cancel{env.billingPhone ? ` (for billing questions our line is ${env.billingPhone})` : ""}.
        </p>
      </section>

      {mode.mockStripe && m && (
        <form action={runDemoClock} className="rounded-2xl border-2 border-ink bg-brass p-5">
          <p className="font-bold">Demo tools (test mode only): run the billing clock and the 48-hour reminder job now.</p>
          <label className="mt-3 flex items-start gap-3"><input type="checkbox" name="fast_forward" className="check" /> <span>Pretend my trial or billing period ended just now.</span></label>
          <button type="submit" className="btn-ink mt-3">Run billing clock</button>
        </form>
      )}
    </div>
  );
}
