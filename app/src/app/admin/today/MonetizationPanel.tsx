import { getStore } from "@/lib/db";
import { moneyExact } from "@/lib/pricing";
import { computeMonetization } from "@/lib/offers/metrics";

const pct = (v: number | null) => (v === null ? "no data" : `${(v * 100).toFixed(1)}%`);
const cents = (v: number | null) => (v === null ? "no data" : moneyExact(v));

/**
 * Money per person (MONETIZATION_ENGINE.md §6): RPV, RPC, take rate per rung, and the weekly arm readout.
 * Self-contained so /admin/today only mounts it; /admin/monetization shows it alone with a 30-day window.
 */
export async function MonetizationPanel({ days = 7 }: { days?: number }) {
  const m = await computeMonetization(await getStore(), new Date(), days);
  return (
    <section data-testid="monetization">
      <h2 className="text-3xl">Money per person, last {days} days</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="card" data-testid="m-rpv">
          <p className="text-lg font-bold">Revenue per visitor (RPV)</p>
          <p className="font-display text-4xl">{cents(m.rpv_cents)}</p>
          <p className="mt-1 text-[18px]">{moneyExact(m.revenue_cents)} first-purchase revenue / {m.visitors.toLocaleString("en-US")} offer-page visitors</p>
        </div>
        <div className="card" data-testid="m-rpc">
          <p className="text-lg font-bold">Revenue per conversation (RPC)</p>
          <p className="font-display text-4xl">{cents(m.dm.rpc_cents)}</p>
          <p className="mt-1 text-[18px]">
            {m.dm.conversations === null ? (m.dm.error ?? "DM worker not connected") : `${moneyExact(m.dm.revenue_cents)} DM revenue / ${m.dm.conversations.toLocaleString("en-US")} conversations · qualified ${pct(m.dm.qualified_share)}`}
          </p>
        </div>
      </div>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[640px] border-2 border-ink bg-rice text-left text-[18px]" data-testid="m-takes">
          <thead className="bg-ink text-rice">
            <tr>{["Rung", "Offer", "Buyers", "Out of", "Take rate", "How it's counted"].map((h) => <th key={h} className="px-3 py-2">{h}</th>)}</tr>
          </thead>
          <tbody>
            {m.takes.map((t) => (
              <tr key={t.rung} className="border-t-2 border-ink">
                <td className="px-3 py-2 font-bold">{t.rung}</td>
                <td className="px-3 py-2">{t.label}</td>
                <td className="px-3 py-2">{t.buyers}</td>
                <td className="px-3 py-2">{t.base}</td>
                <td className="px-3 py-2 font-bold">{pct(t.rate)}</td>
                <td className="px-3 py-2">{t.definition}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h3 className="mt-6 text-2xl">Experiment arms (revenue per visitor)</h3>
      {m.arms.length === 0 ? (
        <p className="card mt-3 text-lg">No exposures logged yet. Arms appear once /b, the DM bot or the thank-you page log an exposure.</p>
      ) : (
        <div className="mt-3 overflow-x-auto">
          <table className="w-full min-w-[640px] border-2 border-ink bg-rice text-left text-[18px]" data-testid="m-arms">
            <thead className="bg-ink text-rice">
              <tr>{["Experiment", "Arm", "Visitors", "Buyers", "Revenue", "RPV"].map((h) => <th key={h} className="px-3 py-2">{h}</th>)}</tr>
            </thead>
            <tbody>
              {m.arms.map((a) => (
                <tr key={`${a.experiment}-${a.arm}`} className="border-t-2 border-ink">
                  <td className="px-3 py-2 font-bold">{a.experiment}</td>
                  <td className="px-3 py-2">{a.arm}</td>
                  <td className="px-3 py-2">{a.visitors}</td>
                  <td className="px-3 py-2">{a.buyers}</td>
                  <td className="px-3 py-2">{moneyExact(a.revenue_cents)}</td>
                  <td className="px-3 py-2 font-bold">{moneyExact(a.rpv_cents)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
