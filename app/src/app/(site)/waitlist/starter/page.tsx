import type { Metadata } from "next";
import { getStore } from "@/lib/db";
import { buildSession } from "@/lib/practice";
import { verifyAccess } from "@/lib/waitlistTokens";

export const metadata: Metadata = { title: "Day 1: the chair version", robots: { index: false } };
export const dynamic = "force-dynamic";

/** A fixed Monday: legs day, Rebuild track (the gentlest), chair version. */
const DAY_ONE = new Date("2026-10-05T12:00:00Z");

export default async function Starter({ searchParams }: { searchParams: Promise<{ k?: string }> }) {
  const { k } = await searchParams;
  const id = verifyAccess(k);
  const entry = id ? await (await getStore()).get("waitlist", id) : null;
  if (!entry || entry.status !== "confirmed") {
    return (
      <div className="narrow py-12">
        <h1 className="text-4xl">This link has expired</h1>
        <p className="mt-4 text-lg">Use the newest email from us, or join the waitlist again.</p>
        <a href="/waitlist" className="btn-outline mt-6">Back to the waitlist</a>
      </div>
    );
  }
  const s = buildSession(DAY_ONE, "rebuild", null);
  return (
    <div className="narrow space-y-6 py-10" data-testid="waitlist-starter">
      <h1 className="text-4xl">Day 1: {s.title}</h1>
      <p className="text-lg">{s.minutes} minutes. {s.support}</p>
      <ol className="space-y-4">
        {s.steps.map((st, i) => (
          <li key={st.name} className="card">
            <p className="text-xl font-bold">
              {i + 1}. {st.name}: {st.dose}
            </p>
            <p className="mt-2">{st.cue}</p>
            <p className="mt-2"><strong>Easier:</strong> {st.easier}</p>
          </li>
        ))}
      </ol>
      <p className="card text-lg"><strong>Breathing:</strong> {s.breath}</p>
      <p className="rounded-xl border-2 border-ink bg-brass p-4 text-lg font-bold">{s.stopRule}</p>
      <p className="text-lg">{s.closer} — Chang Yin (AI character)</p>
      <p className="fine">General fitness education, not medical advice. Check with your doctor before starting new exercise.</p>
    </div>
  );
}
