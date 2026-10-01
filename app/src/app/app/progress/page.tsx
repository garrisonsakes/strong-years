import Link from "next/link";
import { TrendChart } from "@/components/StrengthChart";
import { requireEntitled } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { computeStrongWeeks } from "@/lib/practice";
import { protectWeek } from "../actions";

export default async function Progress({ searchParams }: { searchParams: Promise<{ protected?: string }> }) {
  const sp = await searchParams;
  const { member } = await requireEntitled();
  const store = await getStore();
  const logs = await store.find("practice_logs", { member_id: member.id });
  const retests = await store.find("retests", { member_id: member.id }, { orderBy: "created_at" });
  const weeks = computeStrongWeeks(logs.map((l) => l.day), member.protected_weeks, new Date(), 12);
  const points = retests.map((r) => ({
    label: new Date(r.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
    value: r.strength_age,
  }));
  const last = retests[retests.length - 1];
  const first = retests[0];
  return (
    <div className="space-y-8" data-testid="progress">
      <h1 className="text-4xl">Your progress</h1>
      {sp.protected && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold">This week is marked as sick or traveling. Your streak is safe.</p>}
      <section className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
        <div className="card">
          <TrendChart title="Your Strength Age, retest by retest" points={points} testId="trend-chart" />
          {first && last && retests.length > 1 && (
            <p className="mt-4 text-lg font-bold">
              {last.strength_age < first.strength_age
                ? `From ${first.strength_age} to ${last.strength_age}. That's your work.`
                : last.strength_age === first.strength_age
                  ? "Holding steady is a result. Most people lose strength every year; you didn't."
                  : "Numbers move around: sleep, a cold, a busy month. Aim for 3 sessions a week and retest on the 1st."}
            </p>
          )}
          <p className="fine mt-3">Strength Age is a motivational estimate from published fitness norms, not a medical test.</p>
          <Link href="/app/retest" className="btn-jade mt-5" data-testid="retest-link">
            Take this month&apos;s retest (3 minutes)
          </Link>
        </div>
        <div className="card">
          <h2 className="text-2xl">Strong Weeks in a row: {weeks.streak}</h2>
          <p className="mt-1">3 sessions in a Monday-to-Sunday week. One missed week every 8 is covered automatically.</p>
          <ul className="mt-4 grid grid-cols-4 gap-2" aria-label="Last 12 weeks">
            {weeks.weeks.map((w) => (
              <li key={w.week} className={`rounded-lg border-2 border-ink p-2 text-center text-[16px] font-bold ${w.strong ? "bg-jade text-rice" : w.grace ? "bg-brass text-ink" : "bg-rice text-ink"}`}>
                {new Date(`${w.week}T12:00:00Z`).toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" })}
                <span className="block">{w.strong ? "Strong" : w.grace ? "Grace" : `${w.sessions}/3`}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4">Total sessions: {weeks.totalSessions}</p>
          <form action={protectWeek} className="mt-4">
            <button type="submit" className="btn-outline sm:w-full">
              I was sick or traveling this week
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
