import Link from "next/link";
import { redirect } from "next/navigation";
import { billingMembership, requireMember } from "@/lib/auth/server";
import { env } from "@/lib/config";
import { CANCEL_REASONS, accessUntil, isCancelReason, saveOfferFor, withinGuarantee } from "@/lib/billing/cancel";
import { formatDate } from "@/lib/pricing";
import { isShopify } from "@/lib/billing/provider";
import { shopifyConfig } from "@/lib/billing/shopify";
import { acceptDowngrade, acceptPause, finishCancel, requestEssentials, requestRefund, undoCancellation } from "../../actions";
import { canOfferEssentials, PLAN_CHANGE_SLA } from "@/lib/billing/planChange";

/**
 * Cancel online in at most two screens (FUNNEL.md 7.8):
 *   Screen 1: optional reason (or "Skip and cancel now", which cancels immediately)
 *   Screen 2: ONE save offer beside an equally prominent "Finish canceling" button
 * The confirmation shows only after the membership is already cancelled.
 */
export default async function Cancel({ searchParams }: { searchParams: Promise<{ reason?: string; done?: string }> }) {
  const sp = await searchParams;
  const member = await requireMember();
  const m = await billingMembership(member.id);
  if (!m) redirect("/app/account");
  const tz = env.displayTimeZone;

  // Shopify launch path (INTEGRATION.md §4): the cancellation itself happens on Shopify's account page
  // (pause, skip or cancel, no call). Our page shows exactly ONE save offer, Essentials $12/mo, as a request
  // a person applies within 1 business day, beside an equally prominent "Finish canceling" link. No third screen.
  if (isShopify()) {
    const manage = shopifyConfig.customerAccountUrl();
    if (sp.done === "essentials_requested") {
      return (
        <div className="narrow space-y-6" data-testid="cancel-essentials-requested">
          <h1 className="text-4xl">Got it. We&apos;re switching you to Essentials, $12 a month.</h1>
          <p className="card text-lg">
            A person on our team applies the change within {PLAN_CHANGE_SLA} and emails you when it&apos;s done. Nothing on your bill changes until then, and if your renewal lands first we refund the difference. If you&apos;d still rather cancel, that&apos;s one tap on your account page, no call.
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <a href={manage} className="btn-outline sm:w-full" data-testid="finish-cancel">Cancel on my account page instead</a>
            <Link href="/app" className="btn-outline sm:w-full">Back to today&apos;s session</Link>
          </div>
        </div>
      );
    }
    const offerEssentials = canOfferEssentials(m);
    return (
      <div className="narrow space-y-6" data-testid="cancel-shopify">
        <h1 className="text-4xl">Cancel, pause, or pay less. Your choice, no call.</h1>
        <p className="text-lg">
          Your membership is billed by our Shopify store. Cancelling there takes two screens: your account page, then confirm. You keep access until the end of the period you&apos;ve paid for, and nothing is charged after that.
        </p>
        <div className="grid gap-4 sm:grid-cols-2">
          {offerEssentials ? (
            <form action={requestEssentials} className="flex flex-col justify-end">
              <button type="submit" className="btn-jade sm:w-full" data-testid="save-offer">Switch to Essentials, $12 a month</button>
            </form>
          ) : (
            <a href={manage} className="btn-jade sm:w-full text-center" data-testid="save-offer">Pause instead (free, up to 3 months)</a>
          )}
          <a href={manage} className="btn sm:w-full border-2 border-ink bg-rice text-ink text-center hover:bg-cream" data-testid="finish-cancel">Finish canceling</a>
        </div>
        {offerEssentials ? (
          <p className="fine">
            Essentials keeps the Daily Practice and the monthly Strength Age retest, without the AI chat, live Q&amp;A or programs. Shopify can&apos;t swap plans by itself, so a person on our team applies it within {PLAN_CHANGE_SLA} and emails you; until then your bill doesn&apos;t change. Pausing (1 to 3 months, free) is also on your account page.
          </p>
        ) : (
          <p className="fine">Pausing is free and nothing is charged while paused. Both options are on your Shopify account page.</p>
        )}
        {withinGuarantee(m) && (
          <form action={requestRefund} className="card">
            <p className="font-bold">Within your 14-day money-back window? You can get a full refund here, right now.</p>
            <button type="submit" className="btn-outline mt-3">Refund my membership charge</button>
          </form>
        )}
      </div>
    );
  }

  if (sp.done) {
    const until = accessUntil(m);
    return (
      <div className="narrow space-y-6" data-testid="cancel-done">
        {sp.done === "canceled" && (
          <>
            <h1 className="text-4xl">Your membership is cancelled.</h1>
            <p className="card text-lg">
              You won&apos;t be charged again. {until ? `You have access until ${formatDate(until, tz)}.` : ""} Your streak, Strength Age history and what the coach remembers are saved for 90 days if you come back. We&apos;ve emailed you a confirmation.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <form action={undoCancellation}>
                <button type="submit" className="btn-outline sm:w-full">Undo cancellation</button>
              </form>
              <Link href="/app" className="btn-outline sm:w-full">Back to today&apos;s session</Link>
            </div>
            {withinGuarantee(m) && (
              <form action={requestRefund} className="card">
                <p className="font-bold">Within your money-back window? You can get a full refund here.</p>
                <button type="submit" className="btn-outline mt-3">Refund my payments</button>
              </form>
            )}
          </>
        )}
        {sp.done === "paused" && (
          <>
            <h1 className="text-4xl">Paused. Nothing is charged while you&apos;re away.</h1>
            <p className="card text-lg">Your membership restarts on {m.paused_until ? formatDate(m.paused_until, tz) : "the date you chose"}. We&apos;ll remind you a week before. You can resume or cancel anytime from your account.</p>
            <Link href="/app/account" className="btn-outline">Back to my account</Link>
          </>
        )}
        {sp.done === "downgraded" && (
          <>
            <h1 className="text-4xl">You&apos;re on Essentials, $12 a month.</h1>
            <p className="card text-lg">It starts at your next charge date and renews monthly until you cancel. Cancel anytime from your account in two screens at most.</p>
            <Link href="/app/account" className="btn-outline">Back to my account</Link>
          </>
        )}
      </div>
    );
  }

  const reason = isCancelReason(sp.reason) ? sp.reason : null;
  if (sp.reason !== undefined) {
    const offer = saveOfferFor(reason, m);
    return (
      <div className="narrow space-y-6" data-testid="cancel-screen-2">
        <p className="text-lg font-bold">Step 2 of 2</p>
        <h1 className="text-4xl">{offer.heading}</h1>
        <p className="text-lg">{offer.body}</p>
        <div className="grid gap-4 sm:grid-cols-2">
          {offer.kind === "pause" ? (
            <form action={acceptPause} className="space-y-3">
              {reason && <input type="hidden" name="reason" value={reason} />}
              <label className="label" htmlFor="months">Pause for</label>
              <select id="months" name="months" className="field" defaultValue="1">
                <option value="1">1 month</option>
                <option value="2">2 months</option>
                <option value="3">3 months</option>
              </select>
              <button type="submit" className="btn-jade sm:w-full" data-testid="save-offer">{offer.button}</button>
            </form>
          ) : (
            <form action={acceptDowngrade} className="flex flex-col justify-end">
              {reason && <input type="hidden" name="reason" value={reason} />}
              <button type="submit" className="btn-jade sm:w-full" data-testid="save-offer">{offer.button}</button>
            </form>
          )}
          <form action={finishCancel} className="flex flex-col justify-end">
            {reason && <input type="hidden" name="reason" value={reason} />}
            <button type="submit" className="btn sm:w-full border-2 border-ink bg-rice text-ink hover:bg-cream" data-testid="finish-cancel">
              Finish canceling
            </button>
          </form>
        </div>
        <p className="fine">Finish canceling stops all future charges immediately. You keep access until the end of the period you&apos;ve paid for.</p>
      </div>
    );
  }

  return (
    <div className="narrow space-y-6" data-testid="cancel-screen-1">
      <p className="text-lg font-bold">Step 1 of 2</p>
      <h1 className="text-4xl">We&apos;ll cancel it right now. Can we ask why?</h1>
      <p className="text-lg">Optional. Tap one, or skip.</p>
      <ul className="grid gap-3 sm:grid-cols-2">
        {CANCEL_REASONS.map((r) => (
          <li key={r.code}>
            <Link href={`/app/account/cancel?reason=${r.code}`} className="choice no-underline" data-testid={`reason-${r.code}`}>
              {r.label}
            </Link>
          </li>
        ))}
      </ul>
      <form action={finishCancel}>
        <button type="submit" className="btn sm:w-full border-2 border-ink bg-ink text-rice hover:bg-jade-dark" data-testid="skip-cancel">
          Skip and cancel now
        </button>
      </form>
    </div>
  );
}
