import type { Metadata } from "next";
import { getShopCta } from "@/lib/shopCheckout";
import { livePrices } from "@/lib/livePricing";
import Link from "next/link";
import { notFound } from "next/navigation";
import { leadResultExpired } from "@/lib/leadAccess";
import { OtherWaysToStart, PricingCards, RenewalNote } from "@/components/Pricing";
import { prices } from "@/lib/config";
import { getStore } from "@/lib/db";
import { money } from "@/lib/pricing";
import { STRENGTH_PROFILES, fill } from "@/lib/quiz/profiles";
import { STAGE_NAMES, type StrengthAgeResult } from "@/lib/quiz/strengthAge";
import { getArm, getFoundingOffer } from "@/lib/request";
import { blitz } from "@/lib/config";

export const metadata: Metadata = { title: "Your Strength Age", robots: { index: false } };
export const dynamic = "force-dynamic";

const JOINT_WORDS: Record<string, string> = { knees: "knees", hips: "hips", lower_back: "lower back", shoulders: "shoulders", hands: "hands" };

function nextRetestDate() {
  const d = new Date();
  const first = new Date(d.getFullYear(), d.getMonth() + 1, 1);
  return first.toLocaleDateString("en-US", { month: "long", day: "numeric" });
}

export default async function StrengthResult({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const store = await getStore();
  const lead = await store.get("leads", id);
  if (!lead || lead.quiz !== "strength_age" || leadResultExpired(lead)) notFound();
  const r = lead.result as unknown as StrengthAgeResult & { sex: string };
  const copy = STRENGTH_PROFILES[r.profile];
  const arm = await getArm();
  const founding = await getFoundingOffer();
  const trialOn = blitz.trialArmEnabled;
  const joints = r.aches.filter((x) => x in JOINT_WORDS).map((x) => JOINT_WORDS[x]!);
  const jointText = joints.length ? joints.join(" and ") : "joints";
  const vars = {
    first: lead.first_name,
    sa: r.strengthAge,
    gapAbs: r.gap === null ? "" : Math.abs(r.gap),
    reps: r.chairReps,
    low: r.typical[0],
    high: r.typical[1],
    stage: STAGE_NAMES[r.balanceStage ?? 0],
    joints: jointText,
    reason: r.safeModeReasons.join(", ") || "your answers",
  };
  const gentle = r.profile === "p6";
  const useFounding = !trialOn || (arm === "B" && !gentle);
  const offerHref = `${useFounding ? "/join" : "/checkout/trial"}?lead=${lead.id}${gentle ? "&gentle=1" : ""}`;
  const buttonBase = copy.button === "Start 7 days for $1" ? "Start my plan" : copy.button;
  const shop = await getShopCta();
  const offerLabel = shop ? shop.label : useFounding ? `${buttonBase}: ${money(founding.priceCents)} today` : `${buttonBase}: 7 days for $1`;

  return (
    <div className="wrap py-10">
      <section className="grid gap-8 lg:grid-cols-[minmax(0,420px)_1fr]" data-testid="strength-result">
        <div className="card h-fit border-4">
          {r.kind === "safe_mode" ? (
            <>
              <p className="text-lg font-bold">Your starting line</p>
              <p className="font-display text-4xl">The Rebuild track (chair-based)</p>
              <p className="mt-3">We skipped the standing tests today, so there&apos;s no Strength Age number yet. That&apos;s the right call.</p>
            </>
          ) : (
            <>
              <p className="text-lg font-bold">Your Strength Age</p>
              <p className="font-display text-[88px] leading-none text-persimmon" data-testid="strength-age-number">
                {r.strengthAge}
              </p>
              <p className="mt-2 text-lg">Your birthday age: {r.age}</p>
              {r.gap !== null && r.gap !== 0 && (
                <p className="mt-1 text-lg font-bold">
                  That&apos;s {Math.abs(r.gap)} year{Math.abs(r.gap) === 1 ? "" : "s"} {r.gap < 0 ? "younger" : "older"} than your birthday age.
                </p>
              )}
              {r.gap === 0 && <p className="mt-1 text-lg font-bold">Right on your birthday age.</p>}
              {r.kind === "tested" ? (
                <ul className="mt-4 space-y-1">
                  <li>
                    Chair stands: {r.chairReps} in 30 seconds (typical for {r.band}: {r.typical[0]}–{r.typical[1]})
                  </li>
                  <li>Balance: held the {STAGE_NAMES[r.balanceStage ?? 0]} for 10 seconds</li>
                </ul>
              ) : (
                <p className="mt-4 font-bold">Estimated from answers only. Take the two tests together for a real number.</p>
              )}
            </>
          )}
          <p className="mt-4 text-lg">
            Your profile: <strong>{copy.name}</strong>
          </p>
          <p className="mt-1">Retest date: {nextRetestDate()}</p>
          <div className="my-4 h-2 w-full bg-brass" aria-hidden="true" />
          <p className="fine">Strength Age is a motivational estimate from published fitness norms, not a medical test.</p>
          {r.under60Note && <p className="fine mt-2">We compared you with 60 to 64-year-olds, where our comparisons start.</p>}
        </div>

        <div>
          <h1 className="text-3xl sm:text-4xl">{fill(copy.headline, vars)}</h1>
          {copy.body.map((p) => (
            <p key={p} className="mt-4 max-w-prose">
              {fill(p, vars)}
            </p>
          ))}
          {gentle && (
            <Link href={`/quiz/strength-age/result/${lead.id}/summary`} className="btn-outline mt-6">
              Open your one-page summary for your doctor
            </Link>
          )}
          <h2 className="mt-8 text-2xl">Your track: {copy.track}</h2>
          <h3 className="mt-6 text-2xl">Your first 7 days{gentle ? " (once your doctor says go)" : ""}</h3>
          <ol className="mt-3 space-y-2">
            {copy.days.map((d) => (
              <li key={d} className="flex gap-3">
                <span className="marker !bg-jade" aria-hidden="true" />
                {d}
              </li>
            ))}
          </ol>
          <p className="mt-6 max-w-prose">
            <strong>What to expect by your first retest:</strong> {copy.expect}
          </p>
        </div>
      </section>

      {r.adultChild && (
        <section className="card mt-10 bg-cream">
          <h2 className="text-2xl">Doing this for your mom or dad?</h2>
          <p className="mt-3 max-w-prose">
            Two options. Give them Strong Years (3 months {money(prices.gift3)} or 12 months {money(prices.gift12)}, prepaid, never auto-renews) with a welcome card from Sun Yoon. Or start it yourself and add them as your partner for {money(prices.partner)}/month if you live together. Either way, you can do the monthly retest together on a video call.
          </p>
          <div className="mt-5 flex flex-col gap-3 sm:flex-row">
            <Link href="/gift" className="btn-jade">
              Give 3 months ({money(prices.gift3)})
            </Link>
            <Link href={offerHref} className="btn-outline">
              Start it myself
            </Link>
          </div>
        </section>
      )}

      <section className="card mt-10 border-t-[10px] border-t-persimmon" data-testid="result-offer">
        {gentle ? (
          <>
            <h2 className="text-3xl">When you&apos;re ready, the chair-based Rebuild track is inside Strong Years.</h2>
            <p className="mt-3 max-w-prose">
              {useFounding
                ? `Membership is ${money(shop ? shop.memberCents : founding.priceCents)} a month with a 14-day money-back guarantee, and we'll remind you before it renews. There's no rush: start once your doctor says yes.`
                : "You can try it for 7 days for $1, and we'll remind you 48 hours before it renews."}{" "}
              We&apos;ve emailed you your plan and the doctor summary. In 3 days we&apos;ll send one note asking whether your doctor said yes.
            </p>
            <div className="mt-6 max-w-md">
              <Link href={offerHref} className="btn-outline sm:w-full">
                {shop ? shop.label : useFounding ? `Join when I'm ready: ${money(founding.priceCents)}` : "Start 7 days for $1"}
              </Link>
              {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={useFounding ? "founding" : "trial"} priceCents={useFounding ? livePrices(founding).memberCents : livePrices(founding).trialRenewCents} />}
            </div>
          </>
        ) : (
          <>
            <h2 className="text-3xl">Your plan runs inside Strong Years as your Daily Practice.</h2>
            {copy.fallback && <p className="mt-3 max-w-prose">{copy.fallback}</p>}
            <div className="mt-6 max-w-lg">
              <Link href={offerHref} className="btn-primary sm:w-full" data-testid="result-cta">
                {offerLabel}
              </Link>
              {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={useFounding ? "founding" : "trial"} priceCents={useFounding ? livePrices(founding).memberCents : livePrices(founding).trialRenewCents} />}
            </div>
            {blitz.frontEndPagesEnabled ? (
              <p className="mt-4">
                <Link href={`/reset?lead=${lead.id}`} className="font-bold text-ink underline">
                  Rather own something first? 7-Day Strength Reset, {money(prices.reset)}.
                </Link>
              </p>
            ) : (
              <p className="mt-4 font-bold">Want something to keep? Add the 7-Day Strength Reset ({money(prices.reset)}) on the next page.</p>
            )}
          </>
        )}
      </section>

      {!gentle && (
        <section className="mt-12">
          <h2 className="text-3xl">Two ways to start</h2>
          <div className="mt-6">
            <PricingCards arm={arm} offer={founding} />
          </div>
          <OtherWaysToStart arm={arm} offer={founding} />
          <p className="mt-8">
            <Link href="/start#begin" className="font-bold text-jade underline">
              More about what&apos;s inside, the guarantee and common questions
            </Link>
          </p>
        </section>
      )}
    </div>
  );
}
