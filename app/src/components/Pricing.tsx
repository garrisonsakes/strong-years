import Link from "next/link";
import { blitz, messaging, offerRules, prices } from "@/lib/config";
import type { FoundingOffer } from "@/lib/blitz";
import type { Arm } from "@/lib/db/types";
import { money, moneyExact } from "@/lib/pricing";
import { livePrices } from "@/lib/livePricing";

/** Round 9: `priceCents` is required and must come from lib/livePricing.ts (cap-aware). */
export function RenewalNote({ offer, priceCents }: { offer: "trial" | "founding" | "reset" | "kitchen"; priceCents: number }) {
  const p = moneyExact(priceCents);
  // F09: only offer "text CANCEL" while texting works.
  const orText = messaging.smsEnabled ? ", or by texting CANCEL" : "";
  const text =
    offer === "trial"
      ? `$1 today for 7 days, then ${p} every month until you cancel. We remind you 48 hours before every charge. Cancel online in two screens at most${orText}.`
      : offer === "founding"
        ? `${p} charged today for your first month, then ${p} every month until you cancel. We email you 48 hours before every charge. 14-day money-back guarantee. Cancel online in two screens at most${orText}.`
        : `Includes 7 days of Strong Years, then ${p}/month until you cancel. We remind you 48 hours before. Cancel online anytime.`;
  return <p className="fine mt-3 max-w-prose">{text}</p>;
}

export function CohortCounter({ claimed, cap }: { claimed: number; cap: number }) {
  const pct = Math.min(100, (claimed / cap) * 100);
  return (
    <div className="mt-4 rounded-xl border-2 border-ink bg-paper p-4" data-testid="cohort-counter">
      <p className="text-[20px] font-bold">
        {claimed.toLocaleString("en-US")} of {cap.toLocaleString("en-US")} founding spots claimed
      </p>
      <div className="mt-2 h-4 w-full rounded-full border-2 border-ink bg-rice" aria-hidden="true">
        <div className="h-full rounded-full bg-jade" style={{ width: `${Math.max(pct, claimed > 0 ? 2 : 0)}%` }} />
      </div>
      <p className="fine mt-2">
        A live count from our member database. When {cap.toLocaleString("en-US")} founding members have joined, the founding price closes. No countdown timers, no made-up numbers.
      </p>
    </div>
  );
}

export function PricingCards({ arm, offer, shop }: { arm: Arm; offer: FoundingOffer; shop?: { label: string; note: string; memberCents: number; cohortOpen: boolean } | null }) {
  const live = livePrices(offer);
  const trialRenew = money(live.trialRenewCents);
  const founding = money(live.memberCents);
  const spots = { claimed: offer.claimed, cap: offer.cap, open: offer.cohortOpen };
  const trialCard = (
    <div key="A" className="card flex flex-col border-t-[10px] border-t-persimmon" data-testid="arm-a-card">
      <h3 className="text-3xl">7 days of Strong Years for $1</h3>
      <p className="mt-2 text-lg" data-testid="trial-renew">Then {trialRenew} a month. Renews monthly until you cancel.</p>
      <ul className="mt-4 space-y-2">
        {["Your Daily Practice every day", "All six 12-week programs", "Sun Yoon's recipes every Sunday", "Your first Strength Age test", "The Wednesday live Q&A with a real human coach"].map((x) => (
          <li key={x} className="flex gap-3">
            <span className="marker" aria-hidden="true" />
            <span>{x}</span>
          </li>
        ))}
      </ul>
      <div className="mt-auto pt-6">
        <Link href="/checkout/trial" className="btn-primary sm:w-full">
          Start 7 days for $1
        </Link>
        <RenewalNote offer="trial" priceCents={live.trialRenewCents} />
        <p className="fine mt-2">14-day money-back guarantee on your first full membership charge, counted from that charge.</p>
      </div>
    </div>
  );
  const foundingCard = (
    <div key="B" className="card flex flex-col border-t-[10px] border-t-jade" data-testid="arm-b-card">
      {shop ? (
        <>
          <h3 className="text-3xl">{shop.cohortOpen ? `Founding membership: ${money(shop.memberCents)} a month` : `Strong Years: ${money(shop.memberCents)} a month`}</h3>
          <p className="mt-2 text-lg">Start with the starter books, then add the membership with one tap. {shop.cohortOpen ? `The founding price stays ${money(shop.memberCents)} a month for as long as you stay subscribed.` : ""}</p>
        </>
      ) : (
        <>
          <h3 className="text-3xl">{offer.founding ? `Founding membership: ${founding} today` : `Strong Years: ${founding} today`}</h3>
          <p className="mt-2 text-lg">{offer.founding ? `Your first month is charged today, and your founding price stays ${founding} a month for as long as you stay subscribed.` : `Your first month is charged today, then ${founding} a month until you cancel.`}</p>
        </>
      )}
      <ul className="mt-4 space-y-2">
        {["Everything in Strong Years, from today", ...(offer.founding ? ["Founding price locked while you stay subscribed (pauses included)"] : []), `${offerRules.guaranteeDaysFoundingArm}-day money-back guarantee`, "Cancel online in two screens at most"].map((x) => (
          <li key={x} className="flex gap-3">
            <span className="marker !bg-jade" aria-hidden="true" />
            <span>{x}</span>
          </li>
        ))}
      </ul>
      {spots.open ? <CohortCounter claimed={spots.claimed} cap={spots.cap} /> : <p className="mt-4 rounded-xl border-2 border-ink bg-paper p-4 font-bold">The founding cohort is full. New members join at {founding} a month.</p>}
      <div className="mt-auto pt-6">
        <Link href="/join" className="btn-jade sm:w-full" data-testid="founding-cta">
          {shop ? shop.label : spots.open ? "Join as a founding member" : "Join Strong Years"}
        </Link>
        {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer="founding" priceCents={live.memberCents} />}
      </div>
    </div>
  );
  if (!blitz.trialArmEnabled) return <div className="mx-auto max-w-[640px]">{foundingCard}</div>;
  return <div className="grid gap-6 lg:grid-cols-2">{arm === "B" ? [foundingCard, trialCard] : [trialCard, foundingCard]}</div>;
}

export function OtherWaysToStart({ arm, offer }: { arm: Arm; offer: FoundingOffer }) {
  if (!blitz.frontEndPagesEnabled) {
    return (
      <div className="mx-auto mt-10 max-w-[640px]">
        <div className="card">
          <p className="text-xl font-bold">Buying for your mom or dad? 3 months {money(prices.gift3)}, or a year {money(prices.gift12)}.</p>
          <p className="mt-2">Prepaid, never auto-renews. They get a card from Sun Yoon.</p>
          <Link href="/gift" className="btn-outline mt-4 sm:w-full">
            Give Strong Years
          </Link>
        </div>
      </div>
    );
  }
  const p = money(livePrices(offer).frontEndRenewCents[arm]);
  const attach = arm === "B" ? `Plus your first month of Strong Years today (${p}), then ${p}/month until you cancel.` : `Includes 7 days of Strong Years, then ${p}/month unless you cancel.`;
  return (
    <div className="mt-10 space-y-4">
      <h3 className="text-2xl">Other ways to start</h3>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card flex flex-col">
          <p className="text-xl font-bold">Rather own something first? 7-Day Strength Reset, {money(prices.reset)}.</p>
          <p className="mt-2">Seven follow-along sessions and a printable plan, yours to keep. {attach}</p>
          <div className="mt-auto pt-4">
            <Link href="/reset" className="btn-outline sm:w-full">
              See the {money(prices.reset)} Reset
            </Link>
          </div>
        </div>
        <div className="card flex flex-col">
          <p className="text-xl font-bold">Here for the food? Sun Yoon&apos;s Strong Kitchen, {money(prices.kitchen)}.</p>
          <p className="mt-2">Her recipe collection plus Chang Yin&apos;s 12-week printable. {attach}</p>
          <div className="mt-auto pt-4">
            <Link href="/kitchen" className="btn-outline sm:w-full">
              See the {money(prices.kitchen)} Kitchen
            </Link>
          </div>
        </div>
        <div className="card flex flex-col">
          <p className="text-xl font-bold">Buying for your mom or dad? 3 months {money(prices.gift3)}, or a year {money(prices.gift12)}.</p>
          <p className="mt-2">Prepaid, never auto-renews. They get a card from Sun Yoon.</p>
          <div className="mt-auto pt-4">
            <Link href="/gift" className="btn-outline sm:w-full">
              Give Strong Years
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
