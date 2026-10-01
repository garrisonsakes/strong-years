import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { currentPurchaser } from "@/lib/auth/server";
import { prices } from "@/lib/config";
import { moneyExact, PROGRAMS } from "@/lib/pricing";
import { redirectIfPrelaunch } from "@/lib/launchGuard";

export const metadata: Metadata = { title: "One more thing", robots: { index: false } };
export const dynamic = "force-dynamic";

/**
 * One-click post-purchase ladder (FUNNEL.md 5.3): $27 keep-forever program →
 * (declined) $7 printables → $29 kit → welcome. Price and terms sit next to every
 * button; every "no" link is plain and equally readable.
 */
export default async function UpsellPage({ params, searchParams }: { params: Promise<{ step: string }>; searchParams: Promise<{ error?: string; flow?: string }> }) {
  const { step } = await params;
  const { error, flow } = await searchParams;
  await redirectIfPrelaunch({}, { internalCheckout: true });
  const member = (await currentPurchaser())?.member;
  if (!member) redirect("/login");
  const gift = flow === "gift";
  const noHref = step === "program" ? "/upsell/printables" : step === "printables" ? "/upsell/kit" : gift ? "/gift/thanks" : "/welcome";

  const ErrorNote = () =>
    error ? (
      <p role="alert" className="mb-6 rounded-xl border-2 border-ink bg-brass p-4 font-bold">
        {error === "choose" ? "Please choose a program first." : "That didn't go through, and nothing was charged. You can skip this and continue."}
      </p>
    ) : null;

  const Card = ({ children }: { children: React.ReactNode }) => (
    <div className="narrow py-10" data-testid={`upsell-${step}`}>
      <p className="mb-4 inline-block rounded-full bg-jade px-4 py-1 font-bold text-rice">Your order is complete. One optional extra:</p>
      <ErrorNote />
      <div className="card">{children}</div>
    </div>
  );

  if (step === "program") {
    return (
      <Card>
        <h1 className="text-3xl">Pick the program you want to keep forever.</h1>
        <p className="mt-4">
          Your membership includes all six 12-week programs while you&apos;re a member. For {moneyExact(prices.programUpsell)} once, choose one and keep it forever, even if you cancel one day. Twelve weeks of sessions, a printable progress booklet, and Strength Age checkpoints at weeks 0, 6 and 12.
        </p>
        <form action="/api/upsell" method="post" className="mt-6 space-y-3">
          <input type="hidden" name="key" value="program" />
          <fieldset className="space-y-3">
            <legend className="label">Choose one</legend>
            {PROGRAMS.map((p) => (
              <label key={p.slug} className="choice cursor-pointer has-[:checked]:bg-jade has-[:checked]:text-rice">
                <input type="radio" name="program" value={p.slug} className="check" required />
                {p.name}
              </label>
            ))}
          </fieldset>
          <p className="font-bold">One payment of {moneyExact(prices.programUpsell)} on the card you just used. No subscription.</p>
          <button type="submit" className="btn-primary sm:w-full" data-testid="upsell-yes">
            Yes, keep my program forever for {moneyExact(prices.programUpsell)}
          </button>
        </form>
        <Link href={noHref} className="btn-outline mt-3 sm:w-full" data-testid="upsell-no">
          No thanks, continue
        </Link>
      </Card>
    );
  }
  if (step === "printables") {
    return (
      <Card>
        <h1 className="text-3xl">Just the paper, then?</h1>
        <p className="mt-4">The large-print exercise cards, the weekly plan sheets and the fridge Strength Age chart, to print at home or at any drugstore photo counter. {moneyExact(prices.printablesDownsell)}, yours to keep.</p>
        <form action="/api/upsell" method="post" className="mt-6">
          <input type="hidden" name="key" value="printables" />
          <p className="mb-3 font-bold">One payment of {moneyExact(prices.printablesDownsell)}. No subscription.</p>
          <button type="submit" className="btn-primary sm:w-full" data-testid="upsell-yes">
            Yes, add the printables for {moneyExact(prices.printablesDownsell)}
          </button>
        </form>
        <Link href={noHref} className="btn-outline mt-3 sm:w-full" data-testid="upsell-no">
          No thanks
        </Link>
      </Card>
    );
  }
  if (step === "kit") {
    return (
      <Card>
        <h1 className="text-3xl">{gift ? "Want to add the three things Chang Yin uses to the gift?" : "Want the three things Chang Yin uses?"}</h1>
        <p className="mt-4">
          You don&apos;t need equipment to start. By week 3 or 4, many people are ready for more resistance, and a kit on the table is a good reminder to press play. Inside: 3 resistance loops (light, medium, heavy), a door anchor, and a grip trainer, with a large-print card showing how Chang Yin uses each one.
        </p>
        <form action="/api/upsell" method="post" className="mt-6">
          <input type="hidden" name="key" value="kit" />
          {gift && <input type="hidden" name="flow" value="gift" />}
          <p className="mb-3 font-bold">One payment of {moneyExact(prices.kitUpsell)}, shipping included. No subscription.</p>
          <button type="submit" className="btn-primary sm:w-full" data-testid="upsell-yes">
            Yes, send the kit ({moneyExact(prices.kitUpsell)})
          </button>
        </form>
        <Link href={noHref} className="btn-outline mt-3 sm:w-full" data-testid="upsell-no">
          No thanks, I&apos;ll use water jugs
        </Link>
      </Card>
    );
  }
  notFound();
}
