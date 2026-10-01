"use client";
import { useEffect, useState } from "react";

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const pad = "=".repeat((4 - (base64.length % 4)) % 4);
  const raw = atob((base64 + pad).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from([...raw].map((c) => c.charCodeAt(0)));
}

type State = "hidden" | "offer" | "working" | "on" | "denied" | "error";

/**
 * Optional launch notification for a confirmed waitlister. Nothing is asked of the
 * browser until they tap the button (explicit consent, then the browser's own prompt).
 */
export function WaitlistPushOptIn({ vapidPublicKey, access, consentText }: { vapidPublicKey: string; access: string; consentText: string }) {
  const [state, setState] = useState<State>("hidden");

  useEffect(() => {
    const supported = "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
    if (!supported || !vapidPublicKey) return;
    setState(Notification.permission === "denied" ? "denied" : "offer");
  }, [vapidPublicKey]);

  async function enable() {
    setState("working");
    try {
      const reg = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
      if ((await Notification.requestPermission()) !== "granted") {
        setState("denied");
        return;
      }
      const sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: urlBase64ToUint8Array(vapidPublicKey) as BufferSource });
      const res = await fetch("/api/waitlist/push", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ k: access, subscription: sub.toJSON() }) });
      setState(res.ok ? "on" : "error");
    } catch {
      setState("error");
    }
  }

  if (state === "hidden") return null;
  return (
    <section className="card border-[3px] border-jade" aria-labelledby="wl-push" data-testid="waitlist-push">
      <h2 id="wl-push" className="text-2xl">
        {state === "on" ? "This device will get the launch notification." : "Want a notification on this device too?"}
      </h2>
      {(state === "offer" || state === "working") && (
        <>
          <p className="mt-2 text-lg">{consentText}</p>
          <button type="button" className="btn-jade mt-4 sm:w-auto" onClick={enable} disabled={state === "working"}>
            {state === "working" ? "One moment…" : "Yes, notify this device"}
          </button>
        </>
      )}
      {state === "denied" && <p className="mt-2 text-lg">Your browser is blocking notifications from us. That&apos;s fine: the email is enough.</p>}
      {state === "error" && (
        <p className="mt-2 text-lg" role="alert">
          That didn&apos;t work on this device. You&apos;ll still get the email.
        </p>
      )}
    </section>
  );
}
