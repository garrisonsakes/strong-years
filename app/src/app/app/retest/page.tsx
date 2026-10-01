import Link from "next/link";
import { Countdown } from "@/components/quiz/QuizKit";
import { requireEntitled } from "@/lib/auth/server";
import { saveRetest } from "../actions";

function resultMessage(sa: number, prev: number | null, reps: number | null, prevReps: number | null, stage: number | null, prevStage: number | null) {
  if (prev === null) return `Your Strength Age is ${sa}. That's your starting line. Retest on the 1st of next month.`;
  const bigDrop = sa - prev >= 5 || (prevReps !== null && reps !== null && prevReps - reps >= 4) || (prevStage !== null && stage !== null && prevStage - stage >= 2);
  if (bigDrop) return "That's a bigger change than usual. It may be nothing, but sudden changes in strength or balance are worth mentioning to your doctor, especially if you've been unwell, changed medicines or felt dizzy. For now we've set you to the Rebuild track, and a person from our team will check in by email.";
  if (sa < prev) return `Your Strength Age went from ${prev} to ${sa}. You did ${reps} stands${prevReps !== null && reps !== null ? `, ${reps - prevReps >= 0 ? reps - prevReps : 0} more than last time` : ""}. That's your work.`;
  if (sa === prev) return "Holding steady is a result. Most people lose strength every year; you didn't this month. Want Chang Yin to move you up a level? Tap “Too easy” after your next session.";
  return "Numbers move around: sleep, a cold, a busy month. Aim for 3 a week this month and retest on the 1st.";
}

export default async function Retest({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const { member } = await requireEntitled();
  const num = (v: string | undefined) => (v === undefined ? null : Number(v));
  if (sp.result) {
    return (
      <div className="narrow space-y-6" data-testid="retest-result">
        <h1 className="text-4xl">Your Strength Age: {sp.result}</h1>
        <p className="card text-lg">{resultMessage(Number(sp.result), num(sp.prev), num(sp.reps), num(sp.prevReps), num(sp.stage), num(sp.prevStage))}</p>
        <p className="fine">Strength Age is a motivational estimate from published fitness norms, not a medical test.</p>
        <Link href="/app/progress" className="btn-jade">See your chart</Link>
      </div>
    );
  }
  return (
    <div className="narrow space-y-6">
      <h1 className="text-4xl">Monthly Strength Age retest</h1>
      <p className="text-lg">3 minutes, one chair, one counter. The chair stand and balance test set your number; the other four are tracked as their own lines.</p>
      <form action={saveRetest} className="space-y-6">
        {!member.age && (
          <fieldset className="card space-y-3">
            <legend className="px-2 text-xl font-bold">About you (asked once)</legend>
            <label className="label" htmlFor="age">Your age</label>
            <input id="age" name="age" type="number" min={45} max={95} className="field max-w-[160px]" required />
            <label className="label" htmlFor="sex">Compare me with</label>
            <select id="sex" name="sex" className="field max-w-[280px]">
              <option value="woman">Women</option>
              <option value="man">Men</option>
              <option value="na">Combined averages</option>
            </select>
          </fieldset>
        )}
        <div className="card space-y-3">
          <h2 className="text-2xl">1. Chair stand, 30 seconds</h2>
          <p>Chair against the wall, arms crossed, stand all the way up and sit all the way down. Stop if anything hurts, or you feel dizzy or short of breath.</p>
          <Countdown seconds={30} label="Start my 30 seconds" />
          <label className="label" htmlFor="chair_reps">How many full stands?</label>
          <input id="chair_reps" name="chair_reps" type="number" min={0} max={40} className="field max-w-[160px]" required />
          <label className="flex items-start gap-3"><input type="checkbox" name="used_hands" className="check" /> <span>I needed my hands or arms.</span></label>
        </div>
        <div className="card space-y-3">
          <h2 className="text-2xl">2. Four-stage balance, at the counter</h2>
          <label className="label" htmlFor="balance_stage">Last position you held for 10 seconds</label>
          <select id="balance_stage" name="balance_stage" className="field" required defaultValue="">
            <option value="" disabled>Choose one</option>
            <option value="0">I couldn&apos;t hold position 1</option>
            <option value="1">Position 1: feet together</option>
            <option value="2">Position 2: half step</option>
            <option value="3">Position 3: heel to toe</option>
            <option value="4">Position 4: one foot</option>
          </select>
        </div>
        <details className="card">
          <summary className="cursor-pointer text-xl font-bold">3–6. The other four tests (optional)</summary>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            {[
              ["step_test", "2-minute step test (knee lifts)"],
              ["arm_curl", "Arm curls in 30 seconds (water bottle)"],
              ["sit_reach", "Seated reach (inches past or short of toes, minus for short)"],
              ["up_and_go", "Timed up-and-go (seconds)"],
            ].map(([k, l]) => (
              <div key={k}>
                <label className="label" htmlFor={k}>{l}</label>
                <input id={k} name={k} type="number" step="0.1" className="field" />
              </div>
            ))}
          </div>
        </details>
        <button type="submit" className="btn-primary" data-testid="save-retest">Save my retest</button>
      </form>
    </div>
  );
}
