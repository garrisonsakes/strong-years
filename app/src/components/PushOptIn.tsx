"use client";
import { useEffect, useState } from "react";

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const pad = "=".repeat((4 - (base64.length % 4)) % 4);
  const raw = atob((base64 + pad).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

type State = "hidden" | "offer" | "working" | "on" | "denied" | "error";

/**
 * Opt-in for a once-a-day nudge on this device. Shown after the first session
 * (never on the first visit), and in Settings. Nothing is asked of the browser
 * until the member taps the button.
 */
export function PushOptIn({ vapidPublicKey, variant = "card" }: { vapidPublicKey: string; variant?: "card" | "settings" }) {
  const [state, setState] = useState<State>("hidden");

  useEffect(() => {
    const supported = typeof window !== "undefined" && "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
    if (!supported || !vapidPublicKey) return;
    let dismissed = false;
    try {
      dismissed = variant === "card" && localStorage.getItem("sy_push_dismissed") === "1";
    } catch {
      /* storage blocked */
    }
    if (Notification.permission === "denied") {
      setState(variant === "settings" ? "denied" : "hidden");
      return;
    }
    navigator.serviceWorker
      .getRegistration("/")
      .then((reg) => reg?.pushManager.getSubscription())
      .then((sub) => setState(sub ? (variant === "settings" ? "on" : "hidden") : dismissed ? "hidden" : "offer"))
      .catch(() => setState(dismissed ? "hidden" : "offer"));
  }, [vapidPublicKey, variant]);

  async function enable() {
    setState("working");
    try {
      const reg = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        setState("denied");
        return;
      }
      const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: urlBase64ToUint8Array(vapidPublicKey) as BufferSource });
      const res = await fetch("/api/push/subscribe", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(sub.toJSON()) });
      setState(res.ok ? "on" : "error");
    } catch {
      setState("error");
    }
  }

  async function disable() {
    try {
      const reg = await navigator.serviceWorker.getRegistration("/");
      const sub = await reg?.pushManager.getSubscription();
      if (sub) {
        await fetch("/api/push/unsubscribe", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ endpoint: sub.endpoint }) });
        await sub.unsubscribe();
      }
    } catch {
      /* ignore */
    }
    setState("offer");
  }

  function notNow() {
    try {
      localStorage.setItem("sy_push_dismissed", "1");
    } catch {
      /* storage blocked */
    }
    setState("hidden");
  }

  if (state === "hidden") return null;
  return (
    <section className="card border-[3px] border-jade" aria-labelledby="push-title" data-testid="push-optin">
      <h2 id="push-title" className="text-2xl">
        {state === "on" ? "Daily reminders are on for this device." : "Want a gentle nudge tomorrow?"}
      </h2>
      {state === "offer" || state === "working" ? (
        <>
          <p className="mt-2 text-lg">One short reminder a day, at your reminder time, only if you haven&apos;t done your session yet. Plus a heads-up before any charge. Nothing else, and you can turn it off anytime.</p>
          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <button type="button" className="btn-jade sm:w-auto" onClick={enable} disabled={state === "working"} data-testid="push-enable">
              {state === "working" ? "One moment…" : "Yes, remind me on this device"}
            </button>
            {variant === "card" && (
              <button type="button" className="btn-outline sm:w-auto" onClick={notNow}>
                Not now
              </button>
            )}
          </div>
        </>
      ) : state === "on" ? (
        <button type="button" className="btn-outline mt-4 sm:w-auto" onClick={disable}>
          Turn off reminders on this device
        </button>
      ) : state === "denied" ? (
        <p className="mt-2 text-lg">Your browser is blocking notifications from us. You can allow them in your browser settings, or keep using email reminders.</p>
      ) : (
        <p className="mt-2 text-lg" role="alert">That didn&apos;t work on this device. Email reminders still come as usual.</p>
      )}
    </section>
  );
}
