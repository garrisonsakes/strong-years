"use client";
import { useRef, useState } from "react";
import type { QuoteView } from "@/lib/quoteView";
import { AD_CONSENT_TEXT } from "@/lib/conversions/text";

type BumpKey = "wallplan" | "reset" | "kitchen";
const ORDER: BumpKey[] = ["reset", "kitchen", "wallplan"];
const bumpKey = (keys: BumpKey[]) => ORDER.filter((k) => keys.includes(k)).join(",");

interface Props {
  offer: string;
  /** One server-computed quote per bump combination, keyed by bumpKey(). "" = no bumps. */
  quotes: Record<string, QuoteView>;
  bumpsAllowed: BumpKey[];
  bumpVoice: "neutral" | "sun";
  gentle: boolean;
  leadId: string | null;
  prefill: { firstName: string; email: string };
  gift?: { months: number } | null;
}

type Errors = Record<string, string>;

export function CheckoutForm(p: Props) {
  const [bumps, setBumps] = useState<BumpKey[]>([]);
  const [sms, setSms] = useState(false);
  const [autoRenew, setAutoRenew] = useState(false);
  const [age, setAge] = useState(false);
  const [adc, setAdc] = useState(false);
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState<Errors>({});
  const consentRef = useRef<HTMLDivElement>(null);
  const q = p.quotes[bumpKey(bumps)] ?? p.quotes[""]!;
  const toggle = (k: BumpKey, on: boolean) => setBumps((cur) => (on ? [...cur.filter((x) => x !== k), k] : cur.filter((x) => x !== k)));

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const local: Errors = {};
    if (q.consentLabel && !autoRenew) local.auto_renew = "Please tick the box above to confirm the membership terms.";
    if (!age) local.age_18 = "Strong Years is for adults. Please confirm you are 18 or older.";
    if (Object.keys(local).length) {
      setErrors(local);
      consentRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    setBusy(true);
    setErrors({});
    const body = {
      offer: p.offer,
      bumps,
      gentle: p.gentle,
      leadId: p.leadId,
      firstName: String(f.get("first_name") ?? ""),
      email: String(f.get("email") ?? ""),
      phone: String(f.get("phone") ?? ""),
      smsConsent: sms,
      autoRenewConsent: autoRenew,
      ageConsent: age,
      adConsent: adc,
      quoteSig: q.sig ?? "",
      gift: p.gift
        ? { recipient_name: String(f.get("recipient_name") ?? ""), recipient_email: String(f.get("recipient_email") ?? ""), message: String(f.get("message") ?? ""), months: p.gift.months }
        : null,
    };
    try {
      const res = await fetch("/api/checkout", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = (await res.json()) as { redirectUrl?: string; errors?: { field: string; message: string }[]; error?: string };
      if (res.ok && data.redirectUrl) {
        window.location.assign(data.redirectUrl);
        return;
      }
      const next: Errors = {};
      for (const er of data.errors ?? []) next[er.field] = er.message;
      if (data.error) next.form = data.error;
      setErrors(next);
    } catch {
      setErrors({ form: "We couldn't reach the payment page. Please try again." });
    }
    setBusy(false);
  }

  const Err = ({ k }: { k: string }) =>
    errors[k] ? (
      <p role="alert" className="mt-2 rounded-lg bg-brass px-3 py-2 font-bold text-ink">
        {errors[k]}
      </p>
    ) : null;

  return (
    <form onSubmit={onSubmit} className="space-y-6" noValidate data-testid="checkout-form">
      {p.gift && (
        <fieldset className="card space-y-4">
          <legend className="px-2 text-2xl font-bold">Who is the gift for?</legend>
          <div>
            <label className="label" htmlFor="recipient_name">
              Their first name
            </label>
            <input id="recipient_name" name="recipient_name" className="field" required />
            <Err k="recipient_name" />
          </div>
          <div>
            <label className="label" htmlFor="recipient_email">
              Their email (we send Sun Yoon&apos;s welcome card here)
            </label>
            <input id="recipient_email" name="recipient_email" type="email" className="field" required />
            <Err k="recipient_email" />
          </div>
          <div>
            <label className="label" htmlFor="message">
              A note from you (optional)
            </label>
            <textarea id="message" name="message" rows={3} className="field" maxLength={300} />
          </div>
        </fieldset>
      )}

      <fieldset className="card space-y-4">
        <legend className="px-2 text-2xl font-bold">{p.gift ? "Your details" : "Your details"}</legend>
        <div>
          <label className="label" htmlFor="first_name">
            First name
          </label>
          <input id="first_name" name="first_name" className="field" autoComplete="given-name" defaultValue={p.prefill.firstName} required />
          <Err k="first_name" />
        </div>
        <div>
          <label className="label" htmlFor="email">
            Email
          </label>
          <input id="email" name="email" type="email" inputMode="email" autoComplete="email" className="field" defaultValue={p.prefill.email} required />
          <Err k="email" />
        </div>
        {!p.gift && (
          <>
            <label className="flex cursor-pointer items-start gap-3">
              <input type="checkbox" className="check" checked={sms} onChange={(e) => setSms(e.target.checked)} data-testid="sms-consent" />
              <span className="text-[18px]">Text me my daily session link. Msg frequency varies, about 1/day. Msg &amp; data rates may apply. Reply STOP to cancel, HELP for help. Consent is not a condition of purchase.</span>
            </label>
            {sms && (
              <div>
                <label className="label" htmlFor="phone">
                  Mobile number
                </label>
                <input id="phone" name="phone" type="tel" inputMode="tel" autoComplete="tel" className="field" />
                <Err k="phone" />
              </div>
            )}
            <label className="flex cursor-pointer items-start gap-3">
              <input type="checkbox" className="check" checked={adc} onChange={(e) => setAdc(e.target.checked)} data-testid="ad-consent" />
              <span className="text-[18px]">{AD_CONSENT_TEXT}</span>
            </label>
          </>
        )}
      </fieldset>

      {p.bumpsAllowed.length > 0 && (
        <fieldset className="space-y-3">
          <legend className="mb-2 text-2xl font-bold">Optional extras, one-time, yours to keep</legend>
          {ORDER.filter((k) => p.bumpsAllowed.includes(k)).map((k) => (
            <label key={k} className="flex cursor-pointer items-start gap-4 rounded-2xl border-[3px] border-dashed border-ink bg-cream p-5">
              <input type="checkbox" className="check" checked={bumps.includes(k)} onChange={(e) => toggle(k, e.target.checked)} data-testid={`bump-${k}`} />
              <span>
                {k === "reset" && (
                  <>
                    <strong>Add the 7-Day Strength Reset, $7.</strong> Seven follow-along sessions, six simple tests and a printable 7-day tracker. A PDF that&apos;s yours to keep, even if you cancel.
                  </>
                )}
                {k === "kitchen" && (
                  <>
                    <strong>Add Sun Yoon&apos;s Strong Kitchen, $17.</strong> 24 recipes with protein grams, soft-food versions and honest remedy grades, plus Chang Yin&apos;s 12-week printable. Yours to keep.
                  </>
                )}
                {k === "wallplan" &&
                  (p.bumpVoice === "sun" ? (
                    <>
                      <strong>Add The Wall Plan, $9.</strong> Put it on the fridge. You&apos;ll walk past it ten times a day and feel guilty nine of them. That&apos;s the point.
                    </>
                  ) : (
                    <>
                      <strong>Add The Wall Plan, $9.</strong> A printable 12-week wall plan for your level, a monthly retest sheet, a Strength Age chart and a habit tracker. Large print, made for the fridge. Yours to keep, even if you cancel.
                    </>
                  ))}
              </span>
            </label>
          ))}
        </fieldset>
      )}

      <div className="rounded-2xl border-[3px] border-ink bg-rice p-5" data-testid="terms-box">
        <p className="text-2xl font-bold">What you&apos;re agreeing to</p>
        <ul className="mt-2 space-y-1">
          {q.lines.map((l) => (
            <li key={l.label} className="flex justify-between gap-4">
              <span>{l.label}</span>
              <span className="font-bold">{l.amount}</span>
            </li>
          ))}
        </ul>
        <div className="my-3 h-[3px] bg-ink" />
        <ul className="space-y-2 text-[20px]">
          {q.terms.map((t) => (
            <li key={t} className="font-bold first:text-[22px]">
              {t}
            </li>
          ))}
        </ul>
      </div>

      <div ref={consentRef} className="space-y-4">
        {q.consentLabel && (
          <label className={`flex cursor-pointer items-start gap-3 rounded-xl border-2 p-4 ${errors.auto_renew ? "border-ink bg-brass" : "border-ink bg-rice"}`}>
            <input type="checkbox" className="check" checked={autoRenew} onChange={(e) => setAutoRenew(e.target.checked)} data-testid="auto-renew-consent" />
            <span className="font-bold">
              {q.consentLabel}{" "}
              <a href="/terms" target="_blank" className="text-ink underline">
                Membership &amp; Cancellation Policy
              </a>
            </span>
          </label>
        )}
        <Err k="auto_renew" />
        <label className={`flex cursor-pointer items-start gap-3 rounded-xl border-2 p-4 ${errors.age_18 ? "border-ink bg-brass" : "border-ink bg-rice"}`}>
          <input type="checkbox" className="check" checked={age} onChange={(e) => setAge(e.target.checked)} data-testid="age-consent" />
          <span className="font-bold">I am 18 or older.</span>
        </label>
        <Err k="age_18" />
      </div>

      <Err k="offer" />
      <Err k="form" />
      <div>
        <button type="submit" className="btn-primary sm:w-full" disabled={busy} data-testid="pay-button">
          {busy ? "Taking you to secure payment…" : q.buttonLabel}
        </button>
        <p className="fine mt-3 text-center font-bold">{q.underButton}</p>
      </div>
      <ul className="grid gap-2 text-[18px] sm:grid-cols-3">
        <li className="rounded-xl border-2 border-ink bg-rice p-3 font-bold">Secure card payment</li>
        <li className="rounded-xl border-2 border-ink bg-rice p-3 font-bold">Cancel online, in two screens at most. You never need to call</li>
        <li className="rounded-xl border-2 border-ink bg-rice p-3 font-bold">Built on published guidelines for older adults</li>
      </ul>
    </form>
  );
}
