"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { GutEnergyAnswers, RedFlag } from "@/lib/quiz/gutEnergy";
import { LeadForm, MultiChoice, Q, QuizFrame, SingleChoice, track, useSaved } from "./QuizKit";

type A = Partial<GutEnergyAnswers>;

const FOOTER = "Sun Yoon is an AI character. Recipes and advice are built from published nutrition guidance for older adults. Not medical advice.";

type Single = { key: keyof GutEnergyAnswers; title: string; options: string[] };

const SINGLES: Single[] = [
  { key: "ageBand", title: "Your age", options: ["50–59", "60–69", "70–79", "80+"] },
  { key: "weight", title: "Your approximate weight (optional, helps us set your protein number)", options: ["Under 130 lb", "130–159 lb", "160–189 lb", "190–219 lb", "220+ lb", "Skip"] },
  { key: "breakfast", title: "A usual breakfast looks like:", options: ["Toast, cereal, a pastry or fruit, and coffee", "Eggs, Greek yogurt, cottage cheese, tofu, or leftovers with protein", "Just coffee or tea", "I skip breakfast"] },
  { key: "proteinMeals", title: "How many of your meals include a palm-sized serving of protein (meat, fish, eggs, tofu, beans, Greek yogurt)?", options: ["3", "2", "1", "0"] },
  { key: "tiredWhen", title: "When do you usually feel most tired?", options: ["Mid-morning", "After lunch through mid-afternoon", "Early evening", "All day", "Not often"] },
  { key: "afterMeal", title: "After your biggest meal, you usually:", options: ["Sit or lie down", "Do chores or potter around", "Go for a walk"] },
  { key: "bloating", title: "How often do you feel uncomfortably full or bloated after eating?", options: ["Most meals", "A few times a week", "Rarely"] },
  { key: "bathroom", title: "Bathroom regularity:", options: ["Like clockwork", "Sometimes stuck", "Often stuck", "Often loose"] },
  { key: "plants", title: "Servings of vegetables, fruit, beans or whole grains per day:", options: ["5 or more", "3–4", "1–2", "0–1"] },
  { key: "fluids", title: "Glasses of water or tea per day (not counting coffee or alcohol):", options: ["6+", "4–5", "2–3", "0–1"] },
  { key: "sleep", title: "Most nights you:", options: ["Sleep 7+ hours and wake rested", "Sleep enough but wake tired", "Wake up 2 or more times", "Struggle to fall asleep"] },
  { key: "caffeine", title: "Your last coffee or caffeinated tea of the day is usually:", options: ["Before noon", "Afternoon", "Evening", "I don't drink caffeine"] },
  { key: "alcohol", title: "Alcohol in a typical week:", options: ["None", "1–3 drinks", "4–7 drinks", "8+"] },
  { key: "chewing", title: "Is chewing or swallowing tougher foods hard for you?", options: ["No", "Sometimes", "Yes"] },
];

export function GutQuiz() {
  const router = useRouter();
  const [a, setA] = useSaved<A>("sy_quiz_b", {});
  const [idx, setIdx] = useSaved<number>("sy_quiz_b_step", 0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTips, setShowTips] = useState(false);
  // steps: 0 intro, 1 red flags, 2..15 singles, 16 meds, 17 lead
  const total = 17;
  const stopped = (a.redFlags?.length ?? 0) > 0 && idx >= 2;

  const go = (n: number, patch: A = {}) => {
    setA({ ...a, ...patch });
    setIdx(n);
    track(n === 1 ? "q_b_start" : "q_b_step", { n });
    window.scrollTo({ top: 0 });
  };
  const back = idx > 0 ? () => setIdx(idx - 1) : undefined;

  async function submit(v: { firstName: string; email: string; sms: boolean; phone: string }) {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/leads", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ quiz: "gut_energy", answers: a, ...v }) });
      const data = (await res.json()) as { id?: string; error?: string };
      if (!res.ok || !data.id) throw new Error(data.error ?? "Something went wrong. Please try again.");
      try {
        localStorage.removeItem("sy_quiz_b");
        localStorage.removeItem("sy_quiz_b_step");
      } catch {
        /* ignore */
      }
      router.push(`/quiz/gut-energy/result/${data.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setBusy(false);
    }
  }

  let body: React.ReactNode;
  if (stopped) {
    body = (
      <Q title="I'm going to be blunt, because I care.">
        <div className="card space-y-4 text-lg" data-testid="redflag-stop">
          <p>These are things to show a doctor, soon. Please call your doctor&apos;s office this week and tell them exactly what you ticked. No recipe or kitchen trick should replace that check.</p>
          <p className="font-bold">If the pain is severe, or you&apos;re vomiting blood, call 911.</p>
          <p>— Sun Yoon (an AI character, not a doctor)</p>
        </div>
        <button type="button" className="btn-outline" onClick={() => setShowTips(true)}>
          Show me gentle kitchen tips anyway
        </button>
        {showTips && (
          <ul className="card space-y-2">
            {["Drink a glass of water or barley tea with each meal.", "Eat slowly. Put the spoon down between bites.", "Soft, warm foods are kind: congee, steamed egg, soft tofu.", "A short, easy walk after meals, if you feel well enough."].map((t) => (
              <li key={t} className="flex gap-3">
                <span className="marker !bg-jade" aria-hidden="true" />
                {t}
              </li>
            ))}
          </ul>
        )}
        <button type="button" className="btn-ink" onClick={() => go(1, { redFlags: undefined })}>
          I ticked something by mistake
        </button>
      </Q>
    );
  } else if (idx === 0) {
    body = (
      <Q title="Why am I so tired after I eat?" body="Fourteen questions. Be honest with me, and I'll be honest with you. At the end you get a 7-day kitchen plan and three recipes to start tonight. — Sun Yoon">
        <button type="button" className="btn-primary" onClick={() => go(1)}>
          Start
        </button>
      </Q>
    );
  } else if (idx === 1) {
    body = (
      <Q title="First, anything here in the last 3 months?" body="Tick all that apply.">
        <MultiChoice<RedFlag>
          value={a.redFlags}
          onChange={(v) => setA({ ...a, redFlags: v })}
          onDone={(v) => {
            if (v.length) track("q_b_stop");
            go(2, { redFlags: v });
          }}
          noneLabel="None of these"
          options={[
            { label: "Losing weight without trying", value: "weight_loss" },
            { label: "Blood in your stool, or black, tarry stools", value: "blood_stool" },
            { label: "Trouble swallowing, or food getting stuck", value: "swallowing" },
            { label: "Vomiting that keeps coming back", value: "vomiting" },
            { label: "A change in bathroom habits lasting more than a few weeks, with no clear reason", value: "bowel_change" },
            { label: "Severe or constant belly pain", value: "belly_pain" },
          ]}
        />
      </Q>
    );
  } else if (idx >= 2 && idx < 2 + SINGLES.length) {
    const s = SINGLES[idx - 2]!;
    body = (
      <Q title={s.title}>
        <SingleChoice value={a[s.key] as number | undefined} onPick={(v) => go(idx + 1, { [s.key]: v } as A)} options={s.options.map((label, value) => ({ label, value }))} />
      </Q>
    );
  } else if (idx === 2 + SINGLES.length) {
    body = (
      <Q title="Do you take 5 or more medicines or supplements daily?">
        <SingleChoice value={a.manyMeds === undefined ? undefined : a.manyMeds ? 1 : 0} onPick={(v) => go(idx + 1, { manyMeds: v === 1 })} options={[{ label: "Yes", value: 1 }, { label: "No", value: 0 }]} />
      </Q>
    );
  } else {
    body = <LeadForm heading="Your kitchen plan is ready." button="Show my plan" busy={busy} error={error} onSubmit={submit} />;
  }

  return (
    <QuizFrame step={Math.min(idx, total)} total={total} onBack={back} onRestart={() => { setA({}); setIdx(0); }} footer={FOOTER}>
      {body}
      {idx === 0 && (
        <p className="mt-6">
          Looking for the strength test instead?{" "}
          <Link href="/quiz/strength-age" className="font-bold text-jade underline">
            Find your Strength Age
          </Link>
        </p>
      )}
    </QuizFrame>
  );
}
