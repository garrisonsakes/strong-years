import { requireEntitled } from "@/lib/auth/server";
import { PROGRAM_DETAILS, programWeek } from "@/lib/content";
import { PROGRAMS } from "@/lib/pricing";
import { chooseProgram } from "../actions";

export default async function Programs() {
  const { member } = await requireEntitled();
  return (
    <div className="space-y-6" data-testid="programs">
      <h1 className="text-4xl">12-week programs</h1>
      <p className="text-lg">One active program at a time. Your Daily Practice follows it.</p>
      <div className="grid gap-5 md:grid-cols-2">
        {PROGRAMS.map((p) => {
          const active = member.active_program === p.slug;
          const d = PROGRAM_DETAILS[p.slug];
          const week = active ? programWeek(member.program_started_at) : null;
          return (
            <article key={p.slug} className={`card ${active ? "border-4 border-jade" : ""}`}>
              <h2 className="text-2xl">{p.name}</h2>
              <p className="mt-2">{d.blurb}</p>
              {active && week ? (
                <>
                  <p className="mt-3 text-xl font-bold">Week {week} of 12: {d.weeks[week - 1]}</p>
                  <div className="mt-2 h-4 w-full rounded-full border-2 border-ink bg-rice" aria-hidden="true">
                    <div className="h-full rounded-full bg-jade" style={{ width: `${(week / 12) * 100}%` }} />
                  </div>
                </>
              ) : (
                <form action={chooseProgram} className="mt-4">
                  <input type="hidden" name="program" value={p.slug} />
                  <button type="submit" className="btn-outline">
                    {member.active_program ? "Switch to this program" : "Start this program"}
                  </button>
                </form>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
