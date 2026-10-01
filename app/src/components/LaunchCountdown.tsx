"use client";
import { useEffect, useState } from "react";

function parts(ms: number) {
  const m = Math.max(0, Math.floor(ms / 60_000));
  return { days: Math.floor(m / 1440), hours: Math.floor((m % 1440) / 60), minutes: m % 60 };
}

function label(ms: number): string {
  if (ms <= 0) return "Checkout is open now. Reload this page to join.";
  const p = parts(ms);
  const bits = [p.days ? `${p.days} day${p.days === 1 ? "" : "s"}` : null, p.hours ? `${p.hours} hour${p.hours === 1 ? "" : "s"}` : null, !p.days ? `${p.minutes} minute${p.minutes === 1 ? "" : "s"}` : null].filter(Boolean);
  return `That's in ${bits.join(", ")}.`;
}

/**
 * Counts down to the real CHECKOUT_OPENS_AT and nothing else. The server renders the
 * first value (so it reads correctly without JavaScript); this only keeps it current.
 */
export function LaunchCountdown({ opensAtIso, initialMs }: { opensAtIso: string; initialMs: number }) {
  const [ms, setMs] = useState(initialMs);
  useEffect(() => {
    const at = Date.parse(opensAtIso);
    const tick = () => setMs(at - Date.now());
    tick();
    const t = setInterval(tick, 30_000);
    return () => clearInterval(t);
  }, [opensAtIso]);
  return (
    <p className="mt-1 text-lg font-bold" data-testid="launch-countdown" aria-live="off">
      {label(ms)}
    </p>
  );
}
