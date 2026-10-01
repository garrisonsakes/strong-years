import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { mockCheckoutAllowed, processorFor } from "@/lib/billing/processors";
import { getStore } from "@/lib/db";
import { moneyExact } from "@/lib/pricing";
import { redirectIfPrelaunch } from "@/lib/launchGuard";

export const metadata: Metadata = { title: "Test payment", robots: { index: false } };
export const dynamic = "force-dynamic";

/** Demo stand-in for the Stripe-hosted page. Only exists while STRIPE_SECRET_KEY is unset. */
export default async function MockCheckout({ params, searchParams }: { params: Promise<{ intent: string }>; searchParams: Promise<{ declined?: string }> }) {
  const { intent: id } = await params;
  const { declined } = await searchParams;
  await redirectIfPrelaunch({}, { internalCheckout: true });
  const intent = await (await getStore()).get("checkout_intents", id);
  if (!mockCheckoutAllowed() || !intent || processorFor(intent.processor).status() !== "mock") notFound();
  if (intent.status === "complete") {
    return (
      <div className="narrow py-10">
        <p className="card text-xl font-bold">This payment is already complete.</p>
      </div>
    );
  }
  return (
    <div className="narrow py-10" data-testid="mock-checkout">
      <div className="rounded-2xl border-[3px] border-ink bg-brass p-4">
        <p className="text-xl font-bold">{intent.processor === "braintree" ? "Braintree" : "Stripe"} test-mode simulator</p>
        <p>No real card is charged. With real test keys, this step is the Stripe-hosted checkout page and you would use card 4242 4242 4242 4242.</p>
      </div>
      <div className="card mt-6">
        <p className="text-lg">Paying as {intent.email}</p>
        <ul className="mt-3 space-y-1">
          {intent.lines.map((l) => (
            <li key={l.label} className="flex justify-between gap-4">
              <span>{l.label}</span>
              <span className="font-bold">{moneyExact(l.cents)}</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 border-t-2 border-ink pt-3 text-2xl font-bold">Total today: {moneyExact(intent.amount_today_cents)}</p>
        <label className="label mt-6" htmlFor="card">
          Card number (test)
        </label>
        <input id="card" className="field" value="4242 4242 4242 4242" readOnly />
        {declined && (
          <p role="alert" className="mt-4 rounded-xl border-2 border-ink bg-brass p-3 font-bold">
            Your card was declined (test card 4000 0000 0000 0002). Nothing was charged.
          </p>
        )}
        <form action="/api/checkout/mock-complete" method="post" className="mt-6 space-y-3">
          <input type="hidden" name="intent" value={intent.id} />
          <button type="submit" name="outcome" value="success" className="btn-primary sm:w-full" data-testid="mock-pay">
            Pay {moneyExact(intent.amount_today_cents)} (test)
          </button>
          <button type="submit" name="outcome" value="decline" className="btn-outline sm:w-full">
            Simulate a declined card
          </button>
        </form>
      </div>
    </div>
  );
}
