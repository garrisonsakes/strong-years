import type { Metadata } from "next";
import { AdminNav } from "../AdminNav";
import { MonetizationPanel } from "../today/MonetizationPanel";

export const metadata: Metadata = { title: "Money per person", robots: { index: false } };
export const dynamic = "force-dynamic";

/** The weekly readout (MONETIZATION_ENGINE.md §5-6): ?days=7 (default) or 30. */
export default async function MonetizationPage({ searchParams }: { searchParams: Promise<{ days?: string }> }) {
  const days = (await searchParams).days === "30" ? 30 : 7;
  return (
    <div className="min-h-screen bg-paper">
      <AdminNav current="today" />
      <main id="main" className="wrap space-y-6 py-8">
        <p className="text-lg">
          Window: <a href="/admin/monetization?days=7" className="font-bold underline">7 days</a> · <a href="/admin/monetization?days=30" className="font-bold underline">30 days</a>
        </p>
        <MonetizationPanel days={days} />
      </main>
    </div>
  );
}
