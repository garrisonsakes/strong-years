import type { Metadata } from "next";
import { getShopCta } from "@/lib/shopCheckout";
import { livePrices } from "@/lib/livePricing";
import Link from "next/link";
import { notFound } from "next/navigation";
import { leadResultExpired } from "@/lib/leadAccess";
import { PricingCards, RenewalNote } from "@/components/Pricing";
import { prices } from "@/lib/config";
import { getStore } from "@/lib/db";
import { money } from "@/lib/pricing";
import { GUT_PROFILES, fill } from "@/lib/quiz/profiles";
import { DIMENSION_ORDER, type Dimension, type GutEnergyResult } from "@/lib/quiz/gutEnergy";
import { getArm, getFoundingOffer } from "@/lib/request";
import { blitz } from "@/lib/config";

export const metadata: Metadata = { title: "Your kitchen plan", robots: { index: false } };
export const dynamic = "force-dynamic";

const LABEL: Record<Dimension, string> = { fuel: "Fuel", rhythm: "Rhythm", flow: "Flow", rest: "Rest", comfort: "Comfort" };

export default async function GutResult({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const store = await getStore();
  const lead = await store.get("leads", id);
  if (!lead || lead.quiz !== "gut_energy" || leadResultExpired(lead)) notFound();
  const r = lead.result as unknown as GutEnergyResult;
  const profile = r.profile ?? "b6";
  const c = GUT_PROFILES[profile];
  const arm = await getArm();
  const founding = await getFoundingOffer();
  const x = r.lowest ? r.display[r.lowest] : null;
  const useFounding = arm === "B" || !blitz.trialArmEnabled;
  const ctaHref = `${useFounding ? "/join" : "/checkout/trial"}?lead=${lead.id}`;
  const shop = await getShopCta();
  const ctaLabel = shop ? shop.label : useFounding ? `Join for ${money(founding.priceCents)} today` : "Start 7 days for $1";

  return (
    <div className="wrap py-10">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,420px)_1fr]" data-testid="gut-result">
        <div className="card h-fit border-4">
          <p className="text-lg font-bold">Your five scores</p>
          <ul className="mt-3 space-y-3">
            {DIMENSION_ORDER.map((d) => (
              <li key={d}>
                <div className="flex justify-between font-bold">
                  <span>{LABEL[d]}</span>
                  <span>{r.display[d]}/10</span>
                </div>
                <div className="mt-1 h-4 w-full rounded-full border-2 border-ink bg-rice" aria-hidden="true">
                  <div className="h-full rounded-full bg-jade" style={{ width: `${Math.max(4, r.display[d] * 10)}%` }} />
                </div>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-lg">
            Your profile: <strong>{c.name}</strong>
          </p>
          <p className="mt-3 font-display text-2xl italic">&ldquo;{c.note}&rdquo;</p>
          <p className="fine">— Sun Yoon (AI character)</p>
          <div className="my-4 h-2 w-full bg-brass" aria-hidden="true" />
          <p className="font-bold">Your protein target</p>
          <p>{r.protein ? `About ${r.protein.lowG}–${r.protein.highG} grams of protein a day, roughly 25–30 grams per meal.` : "About 25–30 grams at each meal."}</p>
          <p className="fine mt-2">If you have kidney disease, ask your doctor before eating more protein.</p>
        </div>
        <div>
          <h1 className="text-3xl sm:text-4xl">{c.headline}</h1>
          <p className="mt-4 max-w-prose">{fill(c.body, { x })}</p>
          {r.pharmacistNote && (
            <p className="card mt-5 max-w-prose">
              Some medicines can affect appetite, digestion, sleep and energy. Bring a list to your pharmacist and ask, &ldquo;Could any of these be making me tired or affecting my stomach?&rdquo; Pharmacists are glad to do this, often for free.
            </p>
          )}
          {c.plan.length > 0 && (
            <>
              <h2 className="mt-8 text-2xl">Your 7-day kitchen plan</h2>
              <ol className="mt-3 space-y-2">
                {c.plan.map((p) => (
                  <li key={p} className="flex gap-3">
                    <span className="marker !bg-jade" aria-hidden="true" />
                    {p}
                  </li>
                ))}
              </ol>
              <p className="mt-5">
                <strong>Tonight&apos;s recipes:</strong> {c.recipes}
              </p>
            </>
          )}
        </div>
      </section>

      <section className="card mt-10 border-t-[10px] border-t-persimmon" data-testid="result-offer">
        {profile === "b6" ? (
          <>
            <h2 className="text-3xl">Next: Chang Yin&apos;s free Strength Age test.</h2>
            <div className="mt-6 flex max-w-lg flex-col gap-3">
              <Link href="/quiz/strength-age" className="btn-jade sm:w-full">
                Find my Strength Age (free)
              </Link>
              <Link href={ctaHref} className="btn-outline sm:w-full">
                {ctaLabel}
              </Link>
              {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={useFounding ? "founding" : "trial"} priceCents={useFounding ? livePrices(founding).memberCents : livePrices(founding).trialRenewCents} />}
            </div>
          </>
        ) : (
          <>
            <h2 className="text-3xl">Sun Yoon&apos;s full kitchen, every Sunday, inside Strong Years.</h2>
            <p className="mt-3 max-w-prose">3 new recipes every Sunday, the Gut Reset with Sun Yoon 12-week program, and your Daily Practice with Chang Yin.</p>
            <div className="mt-6 max-w-lg">
              <Link href={ctaHref} className="btn-primary sm:w-full" data-testid="result-cta">
                {ctaLabel}
              </Link>
              {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={useFounding ? "founding" : "trial"} priceCents={useFounding ? livePrices(founding).memberCents : livePrices(founding).trialRenewCents} />}
            </div>
            {blitz.frontEndPagesEnabled ? (
              <p className="mt-4">
                <Link href={`/kitchen?lead=${lead.id}`} className="font-bold text-ink underline">
                  Food first: Sun Yoon&apos;s Strong Kitchen, {money(prices.kitchen)}.
                </Link>
              </p>
            ) : (
              <p className="mt-4 font-bold">Want her whole cookbook? Add Sun Yoon&apos;s Strong Kitchen ({money(prices.kitchen)}) on the next page.</p>
            )}
          </>
        )}
      </section>
      <section className="mt-12">
        <h2 className="text-3xl">Two ways to start</h2>
        <div className="mt-6">
          <PricingCards arm={arm} offer={founding} />
        </div>
      </section>
    </div>
  );
}
