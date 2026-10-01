import type { Metadata } from "next";

export const metadata: Metadata = { title: "Check your email", robots: { index: false } };

/** The same page for every accepted submission (new, already on the list, throttled, bot): nothing to enumerate. */
export default function WaitlistThanks() {
  return (
    <div className="narrow py-12" data-testid="waitlist-thanks">
      <h1 className="text-4xl">Check your email.</h1>
      <div className="card mt-6 space-y-3 text-lg">
        <p className="font-bold">We&apos;ve sent a message to the address you gave. Tap the button in it to confirm it&apos;s you.</p>
        <p>Until you confirm, we won&apos;t email you anything else. The link works for 72 hours.</p>
        <p>Nothing there after a few minutes? Look in your spam or promotions folder for &ldquo;Strong Years&rdquo;.</p>
      </div>
    </div>
  );
}
