"use client";
import { useEffect, useRef, useState } from "react";

export function QuizFrame({ step, total, onBack, onRestart, children, footer }: { step: number; total: number; onBack?: () => void; onRestart?: () => void; children: React.ReactNode; footer: string }) {
  const headingRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    headingRef.current?.querySelector<HTMLElement>("h1,h2")?.focus();
  }, [step]);
  return (
    <div className="narrow py-8 sm:py-12">
      <div className="mb-6 flex min-h-[48px] items-center justify-between gap-4">
        {onBack ? (
          <span className="flex gap-2">
            <button type="button" onClick={onBack} className="min-h-[48px] rounded-btn border-2 border-ink bg-rice px-4 py-2 text-[18px] font-bold text-ink hover:bg-cream">
              Back
            </button>
            {onRestart && (
              <button type="button" onClick={onRestart} className="min-h-[48px] rounded-btn px-3 py-2 text-[18px] font-bold text-ink underline">
                Start over
              </button>
            )}
          </span>
        ) : (
          <span />
        )}
        {step > 0 && (
          <p className="text-[18px] font-bold" aria-live="polite">
            Question {step} of {total}
          </p>
        )}
      </div>
      {step > 0 && (
        <div className="mb-8 h-3 w-full rounded-full border-2 border-ink bg-paper" aria-hidden="true">
          <div className="h-full rounded-full bg-jade" style={{ width: `${Math.min(100, (step / total) * 100)}%` }} />
        </div>
      )}
      <div ref={headingRef}>{children}</div>
      <p className="fine mt-12 border-t-2 border-ink pt-4">{footer}</p>
    </div>
  );
}

export function Q({ title, body, children }: { title: string; body?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div>
      <h1 tabIndex={-1} className="text-3xl outline-none sm:text-4xl">
        {title}
      </h1>
      {body && <div className="mt-4 max-w-prose text-lg">{body}</div>}
      <div className="mt-8 space-y-3">{children}</div>
    </div>
  );
}

export function SingleChoice<T extends string | number>({ options, value, onPick }: { options: { label: string; value: T }[]; value: T | undefined; onPick: (v: T) => void }) {
  return (
    <div role="radiogroup" className="space-y-3">
      {options.map((o) => (
        <button key={String(o.value)} type="button" role="radio" aria-checked={value === o.value} className="choice" onClick={() => onPick(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function MultiChoice<T extends string>({ options, noneLabel, value, onChange, onDone }: { options: { label: string; value: T }[]; noneLabel: string; value: T[] | undefined; onChange: (v: T[]) => void; onDone: (v: T[]) => void }) {
  const sel = value ?? [];
  const noneChosen = value !== undefined && value.length === 0;
  return (
    <div className="space-y-3">
      {options.map((o) => {
        const on = sel.includes(o.value);
        return (
          <button key={o.value} type="button" role="checkbox" aria-checked={on} className="choice" onClick={() => onChange(on ? sel.filter((x) => x !== o.value) : [...sel, o.value])}>
            <span aria-hidden="true" className={`inline-flex h-7 w-7 flex-none items-center justify-center rounded-md border-2 ${on ? "border-rice bg-rice text-jade" : "border-ink"}`}>
              {on ? "✓" : ""}
            </span>
            {o.label}
          </button>
        );
      })}
      <button type="button" role="checkbox" aria-checked={noneChosen} className="choice" onClick={() => onDone([])}>
        <span aria-hidden="true" className={`inline-flex h-7 w-7 flex-none items-center justify-center rounded-md border-2 ${noneChosen ? "border-rice bg-rice text-jade" : "border-ink"}`}>
          {noneChosen ? "✓" : ""}
        </span>
        {noneLabel}
      </button>
      {sel.length > 0 && (
        <button type="button" className="btn-ink mt-4" onClick={() => onDone(sel)}>
          Continue
        </button>
      )}
    </div>
  );
}

export function Countdown({ seconds, label, onDone }: { seconds: number; label: string; onDone?: () => void }) {
  const [left, setLeft] = useState<number | null>(null);
  useEffect(() => {
    if (left === null) return;
    if (left <= 0) {
      onDone?.();
      speak("Stop. Well done.");
      return;
    }
    if (left === 10 && seconds > 10) speak("10 seconds left");
    const t = setTimeout(() => setLeft(left - 1), 1000);
    return () => clearTimeout(t);
  }, [left, seconds, onDone]);
  const start = () => {
    speak("3, 2, 1, go");
    setLeft(seconds);
  };
  return (
    <div className="card text-center">
      <p className="font-display text-[72px] leading-none" aria-live="polite" aria-atomic="true">
        {left === null ? seconds : left}
        <span className="text-[28px]"> sec</span>
      </p>
      {left === null || left <= 0 ? (
        <button type="button" className="btn-primary mt-4" onClick={start}>
          {left === null ? label : "Start again"}
        </button>
      ) : (
        <button type="button" className="btn-outline mt-4" onClick={() => setLeft(null)}>
          Stop the timer
        </button>
      )}
    </div>
  );
}

function speak(text: string) {
  try {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      const u = new SpeechSynthesisUtterance(text);
      u.rate = 0.85;
      window.speechSynthesis.speak(u);
    }
  } catch {
    /* audio is optional */
  }
}

export function track(name: string, data: Record<string, unknown> = {}) {
  try {
    const body = JSON.stringify({ name, data });
    if (navigator.sendBeacon) navigator.sendBeacon("/api/events", new Blob([body], { type: "application/json" }));
    else void fetch("/api/events", { method: "POST", headers: { "Content-Type": "application/json" }, body, keepalive: true });
  } catch {
    /* analytics must never break the quiz */
  }
}

export function useSaved<T>(key: string, initial: T): [T, (v: T) => void] {
  const [state, setState] = useState<T>(initial);
  useEffect(() => {
    try {
      const raw = localStorage.getItem(key);
      if (raw) setState(JSON.parse(raw) as T);
    } catch {
      /* storage may be blocked */
    }
  }, [key]);
  const set = (v: T) => {
    setState(v);
    try {
      localStorage.setItem(key, JSON.stringify(v));
    } catch {
      /* ignore */
    }
  };
  return [state, set];
}

export function LeadForm({ heading, button, onSubmit, busy, error }: { heading: string; button: string; busy: boolean; error: string | null; onSubmit: (v: { firstName: string; email: string; sms: boolean; phone: string }) => void }) {
  const [sms, setSms] = useState(false);
  return (
    <form
      className="space-y-5"
      onSubmit={(e) => {
        e.preventDefault();
        const f = new FormData(e.currentTarget);
        onSubmit({ firstName: String(f.get("first_name") ?? ""), email: String(f.get("email") ?? ""), sms, phone: String(f.get("phone") ?? "") });
      }}
    >
      <h1 tabIndex={-1} className="text-3xl outline-none sm:text-4xl">
        {heading}
      </h1>
      <p className="text-lg">Where should we send it, along with your 7-day plan and printable cards?</p>
      <div>
        <label className="label" htmlFor="first_name">
          First name
        </label>
        <input className="field" id="first_name" name="first_name" autoComplete="given-name" required />
      </div>
      <div>
        <label className="label" htmlFor="email">
          Email
        </label>
        <input className="field" id="email" name="email" type="email" autoComplete="email" inputMode="email" required />
      </div>
      <label className="flex cursor-pointer items-start gap-3 rounded-xl border-2 border-ink bg-rice p-4">
        <input type="checkbox" className="check" checked={sms} onChange={(e) => setSms(e.target.checked)} name="sms" />
        <span className="text-[18px]">
          Text me my daily session link. Msg frequency varies, about 1/day. Msg &amp; data rates may apply. Reply STOP to cancel, HELP for help. Consent is not a condition of purchase.
        </span>
      </label>
      {sms && (
        <div>
          <label className="label" htmlFor="phone">
            Mobile number
          </label>
          <input className="field" id="phone" name="phone" type="tel" autoComplete="tel" inputMode="tel" required />
        </div>
      )}
      {error && (
        <p role="alert" className="rounded-xl border-2 border-ink bg-brass p-3 font-bold">
          {error}
        </p>
      )}
      <button type="submit" className="btn-primary" disabled={busy}>
        {busy ? "One moment…" : button}
      </button>
      <p className="fine">We never sell your information. Your answers stay with us and are never shared with advertisers. Unsubscribe anytime.</p>
    </form>
  );
}
