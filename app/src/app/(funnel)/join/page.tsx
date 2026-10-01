import type { Metadata } from "next";
import { CheckoutForm } from "@/components/CheckoutForm";
import { ExposureBeacon } from "@/components/ExposureBeacon";
import { getStore } from "@/lib/db";
import { buildQuotes } from "@/lib/checkoutQuotes";
import { money } from "@/lib/pricing";
import { getArm, getFoundingOffer, logPriceExposure } from "@/lib/request";
import { blitz } from "@/lib/config";
import { redirectIfPrelaunch } from "@/lib/launchGuard";
import { redirect } from "next/navigation";
import { isShopify } from "@/lib/billing/provider";
import { shopifyJoinUrl } from "@/lib/shopCheckout";

export const metadata: Metadata = {
  title: "Join Strong Years",
  description: "Founding membership: your Daily Practice with Chang Yin, Sun Yoon's Kitchen and a monthly Strength Age retest. 14-day money-back guarantee.",
};
export const dynamic = "force-dynamic";

/**
 * /join: the founding checkout that JOIN keyword DMs, ads and email route to.
 * One page, one offer, the form above the fold on desktop, no images to load.
 */
export default async function Join({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  // Organic launch: before checkout opens, /join is the waitlist (server-side).
  await redirectIfPrelaunch(sp);
  // CANON UPDATE 2: checkout is the Shopify store. The cell comes from the signed
  // visitor id (sy_v on launch links sets it), so a waitlister keeps their cell.
  if (isShopify()) {
    const url = await shopifyJoinUrl(sp);
    if (url) redirect(url);
    return (
      <div className="narrow py-12" data-testid="join-unavailable">
        <h1 className="text-4xl">Checkout is being set up</h1>
        <p className="mt-4 text-lg">Nothing was charged. Please try again in a few minutes, or reply to any of our emails and a person will help.</p>
      </div>
    );
  }
  // FUNNEL.md 5.6: a visitor in the $1-then-$25 cell (T25) never sees /join's
  // charge-today terms; they get the trial checkout. Launch emails link here for
  // every cell, so each waitlister lands on exactly the cell they were assigned.
  if (blitz.trialArmEnabled && (await getArm()) === "A") {
    const qs = new URLSearchParams(Object.entries(sp).filter((e): e is [string, string] => typeof e[1] === "string" && e[0] !== "sy_v")).toString();
    redirect(`/checkout/trial${qs ? `?${qs}` : ""}`);
  }
  const offer = await getFoundingOffer();
  await logPriceExposure();
  let prefill = { firstName: "", email: "" };
  if (sp.lead) {
    const lead = await (await getStore()).get("leads", sp.lead);
    if (lead) prefill = { firstName: lead.first_name, email: lead.email };
  }
  const gentle = sp.gentle === "1";
  const { quotes, bumpsAllowed } = buildQuotes({ offer: "founding", arm: "B", gentle, founding: offer });
  const price = money(offer.priceCents);
  const pct = Math.min(100, (offer.claimed / offer.cap) * 100);

  return (
    <div className="wrap grid items-start gap-10 py-8 lg:grid-cols-[1fr_minmax(0,560px)]" data-testid="join">
      <ExposureBeacon />
      <section className="lg:sticky lg:top-6">
        {sp.canceled && <p className="mb-6 rounded-xl border-2 border-ink bg-brass p-4 font-bold">No payment was taken. You can try again, or come back anytime.</p>}
        {sp.lapsed && (
          <p className="mb-6 rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="status" data-testid="lapsed">
            {sp.lapsed === "none"
              ? "Your account doesn't have a membership yet, so the sessions and coaches aren't open. You can join below."
              : "Your membership has ended, so the sessions and coaches are closed. Your progress is saved for 90 days. Join again below whenever you like."}
          </p>
        )}
        <h1 className="text-4xl sm:text-5xl">{offer.founding ? `Join as a founding member: ${price} today.` : `Join Strong Years: ${price} today.`}</h1>
        <p className="mt-4 max-w-prose text-lg">
          Your Daily Practice with Chang Yin, 8 to 12 minutes a day at your level, with a chair-based version of everything. Sun Yoon&apos;s recipes every Sunday. A Strength Age you retest every month.
        </p>
        <ul className="mt-6 space-y-2">
          {[
            `${price} today for your first month, then ${price} a month until you cancel`,
            offer.founding ? "Founding price locked while you stay subscribed (pauses included)" : "Cancel online anytime, in two screens at most",
            "14-day money-back guarantee",
            "Chang Yin and Sun Yoon are AI characters. The practices are real.",
          ].map((x) => (
            <li key={x} className="flex gap-3 text-lg font-bold">
              <span className="marker !bg-jade" aria-hidden="true" />
              {x}
            </li>
          ))}
        </ul>
        <div className="mt-6 rounded-xl border-2 border-ink bg-rice p-4" data-testid="join-cohort">
          {offer.cohortOpen ? (
            <>
              <p className="text-lg font-bold">
                {offer.claimed.toLocaleString("en-US")} of {offer.cap.toLocaleString("en-US")} founding spots claimed
              </p>
              <div className="mt-2 h-4 w-full rounded-full border-2 border-ink bg-paper" aria-hidden="true">
                <div className="h-full rounded-full bg-jade" style={{ width: `${Math.max(pct, offer.claimed > 0 ? 2 : 0)}%` }} />
              </div>
              <p className="fine mt-2">A live count from our member database. No timers, no made-up numbers.</p>
            </>
          ) : (
            <p className="text-lg font-bold">The founding cohort is full. New members join at the standard price of {price} a month.</p>
          )}
        </div>
      </section>
      <section aria-label="Checkout">
        <CheckoutForm offer="founding" quotes={quotes} bumpsAllowed={bumpsAllowed} bumpVoice="neutral" gentle={gentle} leadId={sp.lead ?? null} prefill={prefill} />
        <p className="fine mt-8">
          General fitness and nutrition education, not medical advice. Check with your doctor before starting new exercise. On your statement: STRONGYEARS MEMBER.
        </p>
      </section>
    </div>
  );
}
