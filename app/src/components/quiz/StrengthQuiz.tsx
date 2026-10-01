"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { Ache, Mobility, SafetyFlag, StrengthAgeAnswers, Taker } from "@/lib/quiz/strengthAge";
import { Countdown, LeadForm, MultiChoice, Q, QuizFrame, SingleChoice, track, useSaved } from "./QuizKit";

type A = Partial<StrengthAgeAnswers>;
type StepId = "intro" | "q1" | "q2" | "q3" | "q4" | "safe" | "q5" | "seated" | "t1" | "t2" | "q6" | "q7" | "q8" | "q9" | "q10" | "q11" | "q12" | "q13" | "q14" | "lead";

const FOOTER = "Chang Yin is an AI character. Created with AI characters. Not medical advice. The tests come from published senior fitness research (CDC STEADI, Rikli & Jones).";

function stepsFor(a: A): StepId[] {
  const steps: StepId[] = ["intro", "q1", "q2", "q3", "q4"];
  const safe = (a.safety?.length ?? 0) > 0;
  if (safe) steps.push("safe");
  else {
    steps.push("q5");
    const seated = a.mobility === "walker" || a.mobility === "wheelchair";
    if (seated) steps.push("seated");
    else if (a.taker !== "other") steps.push("t1", "t2");
  }
  steps.push("q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13", "q14", "lead");
  return steps;
}

export function StrengthQuiz() {
  const router = useRouter();
  const [a, setA] = useSaved<A>("sy_quiz_a", {});
  const [idx, setIdx] = useSaved<number>("sy_quiz_a_step", 0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const steps = stepsFor(a);
  const safeIdx = Math.min(idx, steps.length - 1);
  const id = steps[safeIdx]!;
  const total = steps.length - 1;

  const next = (patch: A = {}) => {
    const merged = { ...a, ...patch };
    setA(merged);
    const nextSteps = stepsFor(merged);
    const pos = nextSteps.indexOf(id);
    const n = Math.min(pos + 1, nextSteps.length - 1);
    setIdx(n);
    if (id === "intro") track("q_a_start");
    else track("q_a_step", { n });
    window.scrollTo({ top: 0 });
  };
  const back = safeIdx > 0 ? () => setIdx(safeIdx - 1) : undefined;

  async function submit(v: { firstName: string; email: string; sms: boolean; phone: string }) {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz: "strength_age", answers: a, ...v }),
      });
      const data = (await res.json()) as { id?: string; error?: string };
      if (!res.ok || !data.id) throw new Error(data.error ?? "Something went wrong. Please try again.");
      try {
        localStorage.removeItem("sy_quiz_a");
        localStorage.removeItem("sy_quiz_a_step");
      } catch {
        /* ignore */
      }
      router.push(`/quiz/strength-age/result/${data.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setBusy(false);
    }
  }

  let body: React.ReactNode = null;
  switch (id) {
    case "intro":
      body = (
        <Q
          title="What's your Strength Age?"
          body={
            <>
              <p>Your birthday gives you one age. Your legs and balance give you another. Find yours with two simple fitness tests used in senior fitness research, and get a free 7-day plan.</p>
              <p className="mt-4">
                <strong>You&apos;ll need:</strong> a sturdy chair without wheels pushed against a wall, a kitchen counter, and 3 minutes. If you can, have someone nearby.
              </p>
            </>
          }
        >
          <button type="button" className="btn-primary" onClick={() => next()}>
            Start the test
          </button>
        </Q>
      );
      break;
    case "q1":
      body = (
        <Q title="Who is taking the test today?">
          <SingleChoice<Taker>
            value={a.taker}
            onPick={(v) => next({ taker: v })}
            options={[
              { label: "Me", value: "self" },
              { label: "I'm helping my mom, dad or partner take it right now", value: "helping" },
              { label: "I'm taking it for someone else who isn't here (answers only, no tests)", value: "other" },
            ]}
          />
        </Q>
      );
      break;
    case "q2":
      body = (
        <Q title="Are you a woman or a man?">
          <SingleChoice
            value={a.sex ?? undefined}
            onPick={(v) => next({ sex: v })}
            options={[
              { label: "Woman", value: "woman" as const },
              { label: "Man", value: "man" as const },
              { label: "Prefer not to say (we'll compare with combined averages)", value: "na" as const },
            ]}
          />
        </Q>
      );
      break;
    case "q3": {
      const age = a.age ?? 70;
      body = (
        <Q title="How old are you?" body={a.taker && a.taker !== "self" ? "Or the person taking the test." : undefined}>
          <div className="card flex items-center justify-between gap-4">
            <button type="button" className="btn-outline !w-20" aria-label="One year younger" onClick={() => setA({ ...a, age: Math.max(45, age - 1) })}>
              −
            </button>
            <label className="sr-only" htmlFor="age">
              Age
            </label>
            <select id="age" className="field max-w-[140px] text-center font-display text-[36px]" value={age} onChange={(e) => setA({ ...a, age: Number(e.target.value) })}>
              {Array.from({ length: 51 }, (_, i) => 45 + i).map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
            <button type="button" className="btn-outline !w-20" aria-label="One year older" onClick={() => setA({ ...a, age: Math.min(95, age + 1) })}>
              +
            </button>
          </div>
          {age < 60 && <p className="rounded-xl border-2 border-ink bg-rice p-4">Our comparisons start at age 60, so we&apos;ll compare you with 60 to 64-year-olds. You&apos;ll likely look younger than you are. Good.</p>}
          <button type="button" className="btn-ink" onClick={() => next({ age })}>
            Continue
          </button>
        </Q>
      );
      break;
    }
    case "q4":
      body = (
        <Q title="Safety check first. In the last few months, has any of these happened?" body="Tick all that apply.">
          <MultiChoice<SafetyFlag>
            value={a.safety}
            onChange={(v) => setA({ ...a, safety: v })}
            onDone={(v) => next({ safety: v })}
            noneLabel="None of these"
            options={[
              { label: "Chest pain, pressure or tightness when active", value: "chest" },
              { label: "Dizziness, fainting or nearly fainting", value: "dizzy" },
              { label: "A fall", value: "fall" },
              { label: "Surgery or a hospital stay", value: "surgery" },
              { label: "A doctor told you to limit physical activity", value: "doctor_limit" },
            ]}
          />
        </Q>
      );
      break;
    case "safe":
      body = (
        <Q title="Thank you for telling us.">
          <p className="card text-lg">Let&apos;s skip the standing tests today. Please show your doctor the plan we&apos;ll make you before you start. We&apos;ll include a one-page summary you can print or forward.</p>
          <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold">If you have chest pain, trouble breathing or feel faint right now, stop and call 911.</p>
          <button type="button" className="btn-ink" onClick={() => next()}>
            Continue with a few questions
          </button>
        </Q>
      );
      break;
    case "q5":
      body = (
        <Q title="Do you use any of these to get around?">
          <SingleChoice<Mobility>
            value={a.mobility}
            onPick={(v) => next({ mobility: v })}
            options={[
              { label: "No", value: "none" },
              { label: "A cane, sometimes", value: "cane_some" },
              { label: "A cane, most of the time", value: "cane_most" },
              { label: "A walker", value: "walker" },
              { label: "A wheelchair", value: "wheelchair" },
            ]}
          />
        </Q>
      );
      break;
    case "seated":
      body = (
        <Q title="A seated test instead" body="Arm curl with a water bottle: how many curls in 30 seconds with your stronger arm? We track this for you; it doesn't set a Strength Age number. Skip it if you'd rather.">
          <Countdown seconds={30} label="Start my 30 seconds" />
          <label className="label" htmlFor="curls">
            How many curls?
          </label>
          <input id="curls" className="field max-w-[160px]" type="number" min={0} max={60} inputMode="numeric" defaultValue={a.armCurls ?? ""} onChange={(e) => setA({ ...a, armCurls: e.target.value === "" ? null : Number(e.target.value) })} />
          <button type="button" className="btn-ink" onClick={() => next()}>
            Continue
          </button>
        </Q>
      );
      break;
    case "t1":
      body = (
        <Q title="Test 1: Stand up, sit down, for 30 seconds.">
          <ol className="card list-decimal space-y-2 pl-10 text-lg">
            <li>Push a sturdy chair against a wall so it can&apos;t slide.</li>
            <li>Sit in the middle of the seat, feet flat, about shoulder-width apart.</li>
            <li>Cross your arms over your chest. If you need your hands to stand, that&apos;s okay, just tick the box below.</li>
            <li>When the timer says go, stand all the way up, then sit all the way down. That&apos;s one.</li>
            <li>Repeat as many times as you comfortably can in 30 seconds. Stop anytime if anything hurts, or you feel dizzy or short of breath.</li>
          </ol>
          {a.mobility?.startsWith("cane") && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold">Using a cane: do this with the kitchen counter right in front of you, and someone nearby if you can.</p>}
          <Countdown seconds={30} label="Start my 30 seconds" />
          <label className="label" htmlFor="reps">
            How many full stands did you do?
          </label>
          <input id="reps" className="field max-w-[160px] text-[28px]" type="number" min={0} max={40} inputMode="numeric" defaultValue={a.chairReps ?? ""} onChange={(e) => setA({ ...a, chairReps: e.target.value === "" ? null : Number(e.target.value) })} />
          <label className="flex cursor-pointer items-start gap-3 rounded-xl border-2 border-ink bg-rice p-4">
            <input type="checkbox" className="check" checked={Boolean(a.usedHands)} onChange={(e) => setA({ ...a, usedHands: e.target.checked })} />
            <span>I needed to use my hands or arms.</span>
          </label>
          <button type="button" className="btn-ink" onClick={() => (a.chairReps === undefined || a.chairReps === null ? undefined : next())}>
            {a.chairReps === undefined || a.chairReps === null ? "Enter your number to continue" : "Continue"}
          </button>
        </Q>
      );
      break;
    case "t2":
      body = (
        <Q title="Test 2: How steady are you?" body="Stand next to your kitchen counter with one hand hovering just above it. Don't hold on unless you need to; if you need to, that position is finished. Hold each position for 10 seconds. Stop at the first one you can't hold.">
          <ol className="space-y-3">
            {["Feet side by side, touching", "One foot slightly ahead, the arch of the front foot beside the big toe of the back foot", "One foot directly in front of the other, heel touching toe", "Stand on one foot"].map((s, i) => (
              <li key={s} className="card">
                <p className="text-lg font-bold">
                  Position {i + 1}: {s}
                </p>
                <div className="mt-3">
                  <Countdown seconds={10} label={`Time position ${i + 1}`} />
                </div>
              </li>
            ))}
          </ol>
          <p className="label mt-6">Which was the last position you held for the full 10 seconds?</p>
          <SingleChoice
            value={a.balanceStage ?? undefined}
            onPick={(v) => next({ balanceStage: v })}
            options={[
              { label: "I couldn't hold position 1", value: 0 },
              { label: "Position 1: feet together", value: 1 },
              { label: "Position 2: half step", value: 2 },
              { label: "Position 3: heel to toe", value: 3 },
              { label: "Position 4: one foot", value: 4 },
            ]}
          />
        </Q>
      );
      break;
    case "q6":
      body = (
        <Q title="Can you open a new, sealed jar?">
          <SingleChoice value={a.jar} onPick={(v) => next({ jar: v })} options={["Easily", "With some effort", "I usually need a tool or someone's help", "No"].map((label, value) => ({ label, value }))} />
        </Q>
      );
      break;
    case "q7":
      body = (
        <Q title="Could you carry two full gallon jugs of water (about 8 pounds each) from the car to the kitchen?">
          <SingleChoice value={a.carry} onPick={(v) => next({ carry: v })} options={["Yes, easily", "Yes, with a rest", "Only one at a time", "No"].map((label, value) => ({ label, value }))} />
        </Q>
      );
      break;
    case "q8":
      body = (
        <Q title="If you were sitting on the floor, how would you get up?">
          <SingleChoice value={a.floor} onPick={(v) => next({ floor: v })} options={["Without using my hands", "Using one hand or a knee", "I'd need furniture to push on", "I couldn't get up on my own", "I'm not sure, I avoid the floor"].map((label, value) => ({ label, value }))} />
        </Q>
      );
      break;
    case "q9":
      body = (
        <Q title="A flight of about 10 stairs. What's true for you?">
          <SingleChoice value={a.stairs} onPick={(v) => next({ stairs: v })} options={["Up without holding the rail", "Up, holding the rail", "Up, holding the rail and stopping to rest", "I avoid stairs"].map((label, value) => ({ label, value }))} />
        </Q>
      );
      break;
    case "q10":
      body = (
        <Q title="Walking with people your age, you usually:">
          <SingleChoice value={a.walking} onPick={(v) => next({ walking: v })} options={["Keep up easily or lead", "Keep up, but it takes effort", "Fall behind", "I don't walk far"].map((label, value) => ({ label, value }))} />
        </Q>
      );
      break;
    case "q11":
      body = (
        <Q title="In a normal week, how often do you do strength exercise (weights, bands, bodyweight)?">
          <SingleChoice value={a.strengthFreq} onPick={(v) => next({ strengthFreq: v })} options={["2 or more times", "Once", "Rarely", "Never"].map((label, value) => ({ label, value }))} />
        </Q>
      );
      break;
    case "q12":
      body = (
        <Q title="Anywhere that often aches or feels stiff?" body="Tick all that apply.">
          <MultiChoice<Ache>
            value={a.aches?.filter((x) => x !== "nothing")}
            onChange={(v) => setA({ ...a, aches: v })}
            onDone={(v) => next({ aches: v.length ? v : ["nothing"] })}
            noneLabel="Nothing in particular"
            options={[
              { label: "Knees", value: "knees" },
              { label: "Hips", value: "hips" },
              { label: "Lower back", value: "lower_back" },
              { label: "Shoulders or neck", value: "shoulders" },
              { label: "Hands or wrists", value: "hands" },
            ]}
          />
        </Q>
      );
      break;
    case "q13":
      body = (
        <Q title="A year from now, what would you most love to do more easily?">
          <SingleChoice
            value={a.goal}
            onPick={(v) => next({ goal: v })}
            options={["Get down on the floor with my grandchildren, and back up", "Travel and walk all day without paying for it", "Garden, carry and lift things myself", "Keep living independently in my own home", "Feel steady and stop worrying about falling", "Look and feel strong again"].map((label, value) => ({ label, value }))}
          />
        </Q>
      );
      break;
    case "q14":
      body = (
        <Q title="How many minutes could you give this, most days?">
          <SingleChoice value={a.minutes} onPick={(v) => next({ minutes: v })} options={[5, 10, 15, 20].map((m) => ({ label: m === 20 ? "20 or more" : String(m), value: m }))} />
        </Q>
      );
      break;
    case "lead":
      body = <LeadForm heading="Your Strength Age is ready." button="Show my Strength Age" busy={busy} error={error} onSubmit={submit} />;
      break;
  }

  return (
    <QuizFrame step={safeIdx} total={total} onBack={back} onRestart={() => { setA({}); setIdx(0); }} footer={FOOTER}>
      {body}
    </QuizFrame>
  );
}
