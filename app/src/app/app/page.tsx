import Link from "next/link";
import { PushOptIn } from "@/components/PushOptIn";
import { vapid } from "@/lib/push";
import { currentMembership, requireEntitled } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import type { Track } from "@/lib/db/types";
import { PROGRAM_DETAILS, programWeek } from "@/lib/content";
import { PROGRAMS } from "@/lib/pricing";
import { SWAPS, TRACKS, computeStrongWeeks, type Swap } from "@/lib/practice";
import { sessionFor, sessionView } from "@/lib/products";
import { completeSession, setTrack } from "./actions";

const SUN_NOTES = [
  "Chang Yin did his today too. He complained. You didn't. Good.",
  "Good. Now drink a glass of water. I'm watching.",
  "Eight minutes. See? Nobody died. Eat some protein.",
  "Seven out of ten. Because I love you. Tomorrow, eight.",
];

export default async function Today({ searchParams }: { searchParams: Promise<{ swap?: string; done?: string }> }) {
  const sp = await searchParams;
  const { member } = await requireEntitled();
  const store = await getStore();
  const membership = await currentMembership(member.id);
  const swap = SWAPS.some((s) => s.key === sp.swap) ? (sp.swap as Swap) : null;
  const now = new Date();
  const product = sessionFor(now, membership?.created_at ?? member.created_at);
  const view = sessionView(product, member.track, swap);
  const session = {
    key: `${now.toISOString().slice(0, 10)}:${view.id}:${member.track}:${swap ?? "none"}`,
    minutes: view.minutes,
    title: `Day ${view.dayNumber}: ${view.type}. ${view.title}${swap ? ` (${SWAPS.find((x) => x.key === swap)!.label.toLowerCase()} version)` : ""}`,
    closer: view.closer ?? "Same time tomorrow.",
  };
  const logs = await store.find("practice_logs", { member_id: member.id });
  const weeks = computeStrongWeeks(logs.map((l) => l.day), member.protected_weeks, now);
  const today = now.toISOString().slice(0, 10);
  const doneToday = logs.some((l) => l.day === today);
  const retests = await store.count("retests", { member_id: member.id });
  const chats = await store.count("chat_messages", { member_id: member.id, role: "user" });
  const program = PROGRAMS.find((p) => p.slug === member.active_program);
  const ageDays = (now.getTime() - new Date(member.created_at).getTime()) / 86_400_000;
  const checklist = [
    { label: "Do your first session (any level, any length)", done: logs.length > 0, href: "#session" },
    { label: "Check your track for tomorrow", done: logs.length > 1 || member.track !== "steady", href: "#track" },
    { label: "Set your daily reminder time", done: member.reminder_time !== "07:30" || member.sms_opt_in, href: "/app/settings" },
    { label: "Find your Strength Age", done: retests > 0, href: "/app/retest" },
    { label: "Pick your program", done: Boolean(member.active_program), href: "/app/programs" },
    { label: "Print your card or wall chart", done: false, href: "/app/printables" },
    { label: "Ask Chang Yin one question, or add your partner", done: chats > 0, href: "/app/chat" },
  ];
  const showChecklist = ageDays < 7 || !checklist[0]!.done || !checklist[3]!.done;
  const note = SUN_NOTES[(logs.length + now.getDate()) % 4]!;

  return (
    <div className="space-y-8" data-testid="today">
      {sp.done && (
        <section className="rounded-2xl border-[3px] border-ink bg-jade p-6 text-rice" role="status">
          <p className="font-display text-4xl text-rice">Done. ✓</p>
          <p className="mt-2 text-lg text-rice">{session.closer} — Chang Yin (AI coach)</p>
          <p className="mt-2 text-lg text-rice">
            This week: {weeks.thisWeek} of 3 for a Strong Week. {now.getDate() % 4 === 0 ? `Sun Yoon says: “${note}”` : ""}
          </p>
        </section>
      )}

      {/* F17: offer push reminders right after the first completed session, never before. */}
      {(sp.done || logs.length > 0) && <PushOptIn vapidPublicKey={vapid().publicKey} />}

      {showChecklist && (
        <section className="card bg-cream" aria-labelledby="first3">
          <h2 id="first3" className="text-2xl">
            Your first 3 days
          </h2>
          <ul className="mt-4 grid gap-2 md:grid-cols-2">
            {checklist.map((c) => (
              <li key={c.label}>
                <Link href={c.href} className="flex min-h-[48px] items-center gap-3 rounded-xl border-2 border-ink bg-rice px-3 py-2 font-bold text-ink no-underline">
                  <span aria-hidden="true" className={`inline-flex h-8 w-8 flex-none items-center justify-center rounded-md border-2 border-ink ${c.done ? "bg-jade text-rice" : "bg-rice"}`}>
                    {c.done ? "✓" : ""}
                  </span>
                  <span>
                    {c.label}
                    <span className="sr-only">{c.done ? " (done)" : " (not done yet)"}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section id="session" className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
        <div className="card">
          <p className="text-lg font-bold">Today&apos;s Daily Practice · {session.minutes} minutes</p>
          <h1 className="mt-1 text-3xl sm:text-4xl">{session.title}</h1>
          <div className="mt-5 flex w-full flex-col gap-4 rounded-xl border-2 border-ink bg-jade p-4 text-rice sm:aspect-video sm:justify-between" role="img" aria-label="Video player placeholder: Chang Yin (AI character) leads today's session. Captions on.">
            <span className="self-start rounded-full bg-ink px-3 py-1 text-[16px] font-bold text-rice">AI character</span>
            <div className="flex flex-col items-center gap-3">
              <span className="flex h-16 w-16 items-center justify-center rounded-full border-4 border-rice text-[28px] sm:h-20 sm:w-20 sm:text-[36px]" aria-hidden="true">
                ▶
              </span>
              <p className="text-center text-[18px] font-bold text-rice">Video placeholder: follow-along session with Chang Yin.</p>
            </div>
            <p className="rounded-lg bg-ink px-3 py-2 text-center text-[18px] font-bold text-rice">&ldquo;{view.opener ?? "Breathe out as you stand."}&rdquo;</p>
          </div>
          <p className="mt-4 rounded-xl border-2 border-ink bg-paper p-3">
            <strong>Your level: {TRACKS.find((t) => t.key === member.track)!.name}.</strong> {view.trackDescription}
          </p>
          {view.swapNote && (
            <p className="mt-3 rounded-xl border-2 border-ink bg-jade-light p-3" data-testid="swap-note">
              <strong>Today&apos;s swap:</strong> {view.swapNote}
            </p>
          )}
          <p className="mt-3 rounded-xl bg-brass p-3 font-bold">{view.safety.stop_rule}</p>
          <ol className="mt-4 space-y-3" data-testid="session-steps">
            {view.steps.map((st, i) => (
              <li key={`${st.name}-${i}`} className="rounded-xl border-2 border-ink p-4">
                <p className="text-xl font-bold">
                  {i + 1}. {st.variant.name} <span className="font-normal">· {st.variant.dose}</span>
                </p>
                {st.variant.advanced && <p className="mt-1 inline-block rounded-full bg-ink px-3 py-0.5 text-[16px] font-bold text-rice">Advanced: Chang&apos;s level, not your starting point</p>}
                <p className="mt-1">{st.variant.how}</p>
                {st.variant.cues.length > 0 && <p className="mt-1">{st.variant.cues.join(" ")}</p>}
                <p className="mt-1 font-bold">{st.variant.breathe}</p>
                {st.variant.safety.map((x) => (
                  <p key={x} className="mt-1">
                    <strong>Safety:</strong> {x}
                  </p>
                ))}
                <p className="mt-1">
                  <strong>You need:</strong> {st.variant.equipment}
                </p>
              </li>
            ))}
          </ol>
          <p className="mt-4">{view.safety.pain_rule}</p>
          <p className="mt-1 font-bold">{view.safety.emergency}</p>
          {doneToday && !sp.done ? (
            <p className="mt-6 rounded-xl border-2 border-ink bg-jade-light p-4 text-lg font-bold">Today is done. Same time tomorrow.</p>
          ) : (
            <form action={completeSession} className="mt-6 space-y-3">
              <input type="hidden" name="session_key" value={session.key} />
              <input type="hidden" name="minutes" value={session.minutes} />
              {swap && <input type="hidden" name="swap" value={swap} />}
              <fieldset>
                <legend className="label">How did it feel? (optional)</legend>
                <div className="grid gap-2 sm:grid-cols-3">
                  {[
                    ["easy", "Too easy"],
                    ["right", "Just right"],
                    ["hard", "Too hard"],
                  ].map(([v, l]) => (
                    <label key={v} className="choice cursor-pointer has-[:checked]:bg-jade has-[:checked]:text-rice">
                      <input type="radio" name="feel" value={v} className="check" />
                      {l}
                    </label>
                  ))}
                </div>
              </fieldset>
              <button type="submit" className="btn-primary sm:w-full" data-testid="mark-done">
                I did it. Mark today done
              </button>
            </form>
          )}
        </div>

        <aside className="space-y-6">
          <div className="card">
            <h2 className="text-2xl">Not your day?</h2>
            <p className="mt-1">One tap swaps in a modified version.</p>
            <div className="mt-3 grid gap-2">
              {SWAPS.map((s) => (
                <Link key={s.key} href={swap === s.key ? "/app" : `/app?swap=${s.key}`} className={swap === s.key ? "btn-jade sm:w-full" : "btn-outline sm:w-full"} aria-current={swap === s.key ? "true" : undefined}>
                  {swap === s.key ? `${s.label} (on)` : s.label}
                </Link>
              ))}
            </div>
          </div>
          <div id="track" className="card">
            <h2 className="text-2xl">Your track</h2>
            <form action={setTrack} className="mt-3 grid gap-2">
              {TRACKS.map((t) => (
                <button key={t.key} type="submit" name="track" value={t.key} className={`choice ${member.track === t.key ? "" : ""}`} aria-pressed={member.track === (t.key as Track)}>
                  <span>
                    {t.name}
                    <span className="block text-[17px] font-normal">{t.blurb}</span>
                  </span>
                </button>
              ))}
            </form>
          </div>
          <div className="card">
            <h2 className="text-2xl">Strong Weeks in a row: {weeks.streak}</h2>
            <p className="mt-1">A Strong Week is 3 sessions, Monday to Sunday. This week: {weeks.thisWeek} of 3.</p>
            <p className="mt-2">
              <Link href="/app/progress" className="font-bold text-jade underline">
                See your progress
              </Link>
            </p>
          </div>
          {program && member.program_started_at && (
            <div className="card">
              <h2 className="text-2xl">{program.name}</h2>
              <p className="mt-1 text-lg font-bold">Week {programWeek(member.program_started_at)} of 12</p>
              <p className="mt-1">This week: {PROGRAM_DETAILS[program.slug].weeks[programWeek(member.program_started_at) - 1]}</p>
            </div>
          )}
          {membership?.status === "trialing" && (
            <p className="rounded-xl border-2 border-ink bg-rice p-4 font-bold">
              You&apos;re on your 7-day trial.{" "}
              <Link href="/app/account" className="text-ink underline">
                See your plan and renewal date
              </Link>
            </p>
          )}
        </aside>
      </section>
    </div>
  );
}
