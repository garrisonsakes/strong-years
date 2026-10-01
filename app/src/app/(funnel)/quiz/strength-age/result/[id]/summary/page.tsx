import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { leadResultExpired } from "@/lib/leadAccess";
import { PrintButton } from "@/components/PrintButton";
import { getStore } from "@/lib/db";
import { STRENGTH_PROFILES } from "@/lib/quiz/profiles";
import type { StrengthAgeResult } from "@/lib/quiz/strengthAge";

export const metadata: Metadata = { title: "Summary for your doctor", robots: { index: false } };

/** FUNNEL.md P6: one-page summary to print or forward to a doctor or physical therapist. */
export default async function DoctorSummary({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const lead = await (await getStore()).get("leads", id);
  if (!lead || lead.quiz !== "strength_age" || leadResultExpired(lead)) notFound();
  const r = lead.result as unknown as StrengthAgeResult;
  const plan = STRENGTH_PROFILES.p6.days;
  return (
    <div className="narrow py-8">
      <div className="no-print mb-6">
        <PrintButton />
      </div>
      <article className="card space-y-4">
        <h1 className="text-3xl">Exercise plan summary for {lead.first_name}</h1>
        <p>
          From the Strong Years Strength Age questionnaire on {new Date(lead.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}. Strong Years is a general fitness program for older adults; this is not a medical assessment.
        </p>
        <p>
          <strong>Why the standing tests were skipped:</strong> {r.safeModeReasons.join(", ") || "safety answers"}.
        </p>
        <p>
          <strong>Question for you:</strong> Is it okay for {lead.first_name} to do seated strength and breathing exercises for about 10 minutes a day? Anything to avoid?
        </p>
        <h2 className="text-2xl">Proposed first week (Rebuild track, all seated)</h2>
        <ul className="space-y-1">
          {plan.map((d) => (
            <li key={d}>{d}</li>
          ))}
        </ul>
        <h2 className="text-2xl">Stop rules we teach</h2>
        <p>Stop for chest pain or pressure, dizziness, shortness of breath, or sharp pain. Breathe out on effort; never hold the breath. Sit a moment before standing up.</p>
        <h2 className="text-2xl">Doctor&apos;s notes</h2>
        <div className="h-40 rounded-xl border-2 border-ink" />
        <p className="fine">Chang Yin and Sun Yoon are AI characters. Sessions are built by our team from published exercise guidelines for older adults.</p>
      </article>
    </div>
  );
}
