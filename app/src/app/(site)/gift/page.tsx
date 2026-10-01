import type { Metadata } from "next";
import { CharacterArt } from "@/components/Art";
import { GiftChooser } from "@/components/GiftChooser";
import { prices } from "@/lib/config";
import { money } from "@/lib/pricing";
import { buildGiftQuotes } from "@/lib/checkoutQuotes";
import { redirectIfPrelaunch } from "@/lib/launchGuard";
import { isShopify } from "@/lib/billing/provider";

export const metadata: Metadata = { title: "Give Mom & Dad Strong Years" };
export const dynamic = "force-dynamic";

export default async function GiftPage() {
  await redirectIfPrelaunch();
  const { q3, q12 } = buildGiftQuotes(new Date());
  return (
    <div className="wrap py-10">
      <div className="grid items-center gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <h1 className="text-4xl sm:text-5xl">Give Mom &amp; Dad Strong Years.</h1>
          <p className="mt-5 max-w-prose text-lg">
            Eight minutes a day with Chang Yin, Sun Yoon&apos;s recipes every Sunday, and a Strength Age they retest every month. Prepaid. It never renews automatically, so nobody gets a surprise charge.
          </p>
          <ul className="mt-6 space-y-2">
            {[`3 months for ${money(prices.gift3)}, or 12 months for ${money(prices.gift12)}`, "A welcome card from Sun Yoon by email", "If they agree, you get a monthly note like “Mom did 18 sessions.”", "Bonus idea: take the Strength Age test together on a video call"].map((x) => (
              <li key={x} className="flex gap-3">
                <span className="marker !bg-jade" aria-hidden="true" />
                {x}
              </li>
            ))}
          </ul>
        </div>
        <CharacterArt who="sun" />
      </div>
      <div className="mx-auto mt-12 max-w-[720px]">
        {isShopify() ? (
          <div className="grid gap-4 sm:grid-cols-2" data-testid="gift-shopify">
            <a href="/join?offer=gift3" className="btn-primary sm:w-full">Give 3 months, {money(prices.gift3)}</a>
            <a href="/join?offer=gift12" className="btn-primary sm:w-full">Give 12 months, {money(prices.gift12)}</a>
            <p className="fine sm:col-span-2">You&apos;ll pay on our secure store and type their name and email there. We email them a private link to start. Prepaid, never renews.</p>
          </div>
        ) : (
          <GiftChooser q3={q3} q12={q12} />
        )}
      </div>
    </div>
  );
}
