import { notFound } from "next/navigation";
import { PrintButton } from "@/components/PrintButton";
import { requireEntitled } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { PRINTABLES } from "@/lib/content";
import { kitchenPlan } from "@/lib/products";
import { WEEKDAY_PLAN, buildSession } from "@/lib/practice";

export default async function Printable({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const p = PRINTABLES.find((x) => x.slug === slug);
  if (!p) notFound();
  const { member } = await requireEntitled();
  let body: React.ReactNode = null;
  if (slug === "weekly-plan") {
    const days = [1, 2, 3, 4, 5, 6, 0];
    body = (
      <table className="w-full border-collapse text-[24px]">
        <tbody>
          {days.map((d) => (
            <tr key={d}>
              <th className="border-2 border-ink p-3 text-left">{["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][d]}</th>
              <td className="border-2 border-ink p-3">{WEEKDAY_PLAN[d]!.title}</td>
              <td className="w-20 border-2 border-ink p-3 text-center">☐</td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  } else if (slug === "grocery-list") {
    const k = kitchenPlan(new Date());
    body = (
      <ul className="columns-1 text-[24px] sm:columns-2">
        {k.groceries.map((g) => (
          <li key={g.item}>
            ☐ {g.item} ({g.amounts.join(" + ")})
          </li>
        ))}
      </ul>
    );
  } else if (slug === "strength-age-chart") {
    const retests = await (await getStore()).find("retests", { member_id: member.id });
    body = (
      <table className="w-full border-collapse text-[24px]">
        <thead>
          <tr>
            {["Month", "Chair stands", "Balance stage", "Strength Age"].map((h) => (
              <th key={h} className="border-2 border-ink p-3 text-left">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[...retests.map((r) => [new Date(r.created_at).toLocaleDateString("en-US", { month: "long" }), r.chair_reps, r.balance_stage, r.strength_age]), ...Array.from({ length: 12 - Math.min(12, retests.length) }, () => ["", "", "", ""])].map((row, i) => (
            <tr key={i}>
              {row.map((c, j) => (
                <td key={j} className="h-14 border-2 border-ink p-3">{String(c)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  } else {
    const s = buildSession(new Date("2026-10-05T12:00:00"), member.track, null);
    body = (
      <div className="grid gap-4 sm:grid-cols-2">
        {s.steps.map((st) => (
          <div key={st.name} className="rounded-xl border-4 border-ink p-4 text-[22px]">
            <p className="font-display text-[30px]">{st.name}</p>
            <p>{st.dose}</p>
            <p className="mt-2">{st.cue}</p>
            <p className="mt-2 font-bold">Easier: {st.easier}</p>
          </div>
        ))}
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <div className="no-print"><PrintButton /></div>
      <h1 className="text-4xl">{p.name}</h1>
      {body}
      <p className="fine">Strong Years · Chang Yin and Sun Yoon are AI characters · Stop if you feel chest pain, dizziness or sharp pain.</p>
    </div>
  );
}
