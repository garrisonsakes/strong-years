"use client";
import { useEffect, useRef, useState } from "react";

interface Msg {
  id: string;
  role: "user" | "assistant" | "system_notice";
  content: string;
  safety: string | null;
  /** Round 7: a resources reply the member can answer with "That's not what I meant". */
  clearable?: boolean;
}

/** Round 7: shown whenever the model is unavailable. Every line is a real way to get help. */
function OfflinePanel({ onRetry }: { onRetry: () => void }) {
  return (
    <div role="alert" className="mt-4 space-y-3 rounded-2xl border-2 border-ink bg-brass p-4 text-ink" data-testid="chat-offline">
      <p className="text-xl font-bold">The coach chat is offline right now.</p>
      <ul className="space-y-2">
        <li>
          Thinking about hurting yourself, or in crisis: call or text <a href="tel:988" className="font-bold underline">988</a>, any time.
        </li>
        <li>
          Emergency: call <a href="tel:911" className="font-bold underline">911</a>.
        </li>
        <li>
          Local help for older adults and caregivers: Eldercare Locator, <a href="tel:18006771116" className="font-bold underline">1-800-677-1116</a> (weekdays).
        </li>
        <li>
          <a href="#human" className="font-bold underline" data-testid="offline-human">Reach a real person on our team</a>
        </li>
      </ul>
      <button type="button" className="btn-outline" onClick={onRetry} data-testid="chat-retry">
        Try the chat again
      </button>
    </div>
  );
}

export function ChatClient({ character, firstName, initial, opener }: { character: "chang" | "sun"; firstName: string; initial: Msg[]; opener: string }) {
  const [msgs, setMsgs] = useState<Msg[]>(initial);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [offline, setOffline] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);
  const name = character === "chang" ? "Chang Yin" : "Sun Yoon";
  useEffect(() => endRef.current?.scrollIntoView({ block: "end" }), [msgs.length]);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const t = text.trim();
    if (!t || busy) return;
    setBusy(true);
    setError(null);
    setMsgs((m) => [...m, { id: `local-${Date.now()}`, role: "user", content: t, safety: null }]);
    setText("");
    try {
      const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ character, text: t }) });
      const data = (await res.json()) as { reply?: Msg; notice?: Msg | null; error?: string; offline?: boolean };
      if (!res.ok || !data.reply) throw new Error(data.error ?? "The coach couldn't answer just now.");
      setMsgs((m) => [...m, ...(data.notice ? [data.notice] : []), data.reply!]);
      if (data.offline) setOffline(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
    setBusy(false);
  }

  async function notWhatIMeant(id: string) {
    if (busy) return;
    setBusy(true);
    setError(null);
    setMsgs((m) => m.map((x) => (x.id === id ? { ...x, clearable: false } : x)));
    try {
      const res = await fetch("/api/chat/clear", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messageId: id }) });
      const data = (await res.json()) as { reply?: Msg; error?: string; offline?: boolean };
      if (!res.ok || !data.reply) throw new Error(data.error ?? "Something went wrong.");
      setMsgs((m) => [...m, data.reply!]);
      if (data.offline) setOffline(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    }
    setBusy(false);
  }

  return (
    <section className="card" aria-label={`Chat with ${name}`}>
      <div className="max-h-[60vh] space-y-4 overflow-y-auto pr-1" aria-live="polite" data-testid="chat-log">
        <div className="max-w-[85%] rounded-2xl border-2 border-ink bg-cream p-4">
          <p className="font-bold">{name} (AI character)</p>
          <p className="mt-1">
            Hello, {firstName}. {opener} What can I help you with today?
          </p>
        </div>
        {msgs.map((m) => {
          const crisis = m.safety?.startsWith("crisis") || m.safety === "offline";
          const mine = m.role === "user";
          return (
            <div key={m.id} className={`max-w-[85%] whitespace-pre-line rounded-2xl border-2 p-4 ${mine ? "ml-auto border-ink bg-jade text-rice" : crisis ? "border-ink bg-brass text-ink" : "border-ink bg-rice text-ink"}`} data-safety={m.safety ?? undefined}>
              <p className={`font-bold ${mine ? "text-rice" : ""}`}>{mine ? "You" : crisis ? "Important: from the Strong Years team" : m.role === "system_notice" ? "Reminder from Strong Years" : `${name} (AI character)`}</p>
              <p className={`mt-1 ${mine ? "text-rice" : ""}`}>{m.content}</p>
              {crisis && m.clearable && (
                <button type="button" className="btn-outline mt-3 bg-rice" onClick={() => notWhatIMeant(m.id)} disabled={busy} data-testid="not-what-i-meant">
                  That&apos;s not what I meant
                </button>
              )}
            </div>
          );
        })}
        <div ref={endRef} />
      </div>
      {error && <p role="alert" className="mt-3 rounded-xl bg-brass p-3 font-bold">{error}</p>}
      {offline && <OfflinePanel onRetry={() => setOffline(false)} />}
      <form onSubmit={send} className={`mt-4 flex flex-col gap-3 sm:flex-row ${offline ? "hidden" : ""}`}>
        <label htmlFor="chat-input" className="sr-only">Your message</label>
        <input id="chat-input" className="field" value={text} onChange={(e) => setText(e.target.value)} placeholder={`Ask ${character === "chang" ? "Chang" : "Sun"} anything about moving or eating`} maxLength={2000} data-testid="chat-input" />
        <button type="submit" className="btn-primary sm:w-auto" disabled={busy} data-testid="chat-send">
          {busy ? "Thinking…" : "Send"}
        </button>
      </form>
      <p className="fine mt-3">
        {name} is an AI character, not a doctor, and can&apos;t give medical or medication advice. <a href="#human" className="font-bold text-ink underline">Talk to a human</a> ·{" "}
        <a href="/safety" className="font-bold text-ink underline">Our crisis protocol</a>
      </p>
    </section>
  );
}
