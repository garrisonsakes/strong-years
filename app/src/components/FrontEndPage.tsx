import Link from "next/link";
import { CharacterArt } from "./Art";
import { RenewalNote } from "./Pricing";
import { prices } from "@/lib/config";
import type { Arm } from "@/lib/db/types";
import { money } from "@/lib/pricing";
import { livePrices } from "@/lib/livePricing";
import type { FoundingOffer } from "@/lib/blitz";

export function FrontEndPage({ kind, arm, leadId, offer }: { kind: "reset" | "kitchen"; arm: Arm; leadId?: string; offer: FoundingOffer }) {
  const renew = livePrices(offer).frontEndRenewCents[arm];
  const reset = kind === "reset";
  const price = reset ? prices.reset : prices.kitchen;
  const href = `/checkout/${kind}${leadId ? `?lead=${leadId}` : ""}`;
  const attach = arm === "B" ? `Plus your first month of Strong Years today (${money(renew)}), then ${money(renew)}/month until you cancel.` : `Includes 7 days of Strong Years, then ${money(renew)}/month unless you cancel.`;
  return (
    <div className="wrap py-10">
      <div className="grid items-center gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <h1 className="text-4xl sm:text-5xl">{reset ? "Seven days. Seven short sessions. One stronger week." : "Cheap food, lots of protein, and no nonsense."}</h1>
          <p className="mt-5 max-w-prose text-lg">
            {reset
              ? "The 7-Day Strength Reset: seven follow-along sessions with Chang Yin, 8 to 12 minutes each, chair-based versions of everything, and a printable plan for the fridge. Yours to keep."
              : "Sun Yoon's Strong Kitchen: Korean, Korean-Chinese and Chinese home dishes adapted for protein and fiber, soft-food versions, soups, and remedies with honest evidence grades (good evidence, some evidence, or tradition only). Plus Chang Yin's printable 12-week plan."}
          </p>
          <p className="mt-4 text-2xl font-bold">{money(price)}</p>
          <div className="mt-6 max-w-md">
            <Link href={href} className="btn-primary sm:w-full">
              {reset ? `Get the Reset for ${money(price)}` : `Get the Kitchen for ${money(price)}`}
            </Link>
            <p className="fine mt-3 font-bold">{attach}</p>
            <RenewalNote offer={kind} priceCents={renew} />
            <p className="fine mt-2">14-day money-back guarantee on your first full membership charge.</p>
          </div>
        </div>
        <CharacterArt who={reset ? "chang" : "sun"} />
      </div>
      <section className="mt-14 grid gap-6 md:grid-cols-3">
        {(reset
          ? [
              ["Days 1 to 3", "Legs, balance, and a gentle mobility day. The Chair Builder starts you where you are."],
              ["Days 4 to 6", "Upper body and grip, a power day, and a longer tai chi flow."],
              ["Day 7", "Rest, a walk, and your first Strength Age retest to see where you started."],
            ]
          : [
              ["Protein at every meal", "25 to 30 grams, the easy way: eggs, tofu, fish, soups. Kidney disease? Ask your doctor for your number."],
              ["Soft-food versions", "Every recipe has a version that's easy to chew."],
              ["Honest remedy grades", "Sun Yoon grades every kitchen remedy. Onion in water? Tradition only. Put the onion in the soup."],
            ]
        ).map(([h, b]) => (
          <div key={h} className="card">
            <h2 className="text-2xl">{h}</h2>
            <p className="mt-2">{b}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
