"use client";
import { useState } from "react";
import type { QuoteView } from "@/lib/quoteView";
import { CheckoutForm } from "./CheckoutForm";

export function GiftChooser({ q3, q12 }: { q3: QuoteView; q12: QuoteView }) {
  const [months, setMonths] = useState<3 | 12>(3);
  const q = months === 3 ? q3 : q12;
  return (
    <div className="space-y-6">
      <div role="radiogroup" aria-label="Gift length" className="grid gap-3 sm:grid-cols-2">
        {([3, 12] as const).map((m) => (
          <button key={m} type="button" role="radio" aria-checked={months === m} className="choice justify-between" onClick={() => setMonths(m)} data-testid={`gift-${m}`}>
            <span>{m} months</span>
            <span>{m === 3 ? q3.todayLabel : q12.todayLabel}</span>
          </button>
        ))}
      </div>
      <CheckoutForm key={months} offer={months === 3 ? "gift3" : "gift12"} quotes={{ "": q }} bumpsAllowed={[]} bumpVoice="neutral" gentle={false} leadId={null} prefill={{ firstName: "", email: "" }} gift={{ months }} />
    </div>
  );
}
