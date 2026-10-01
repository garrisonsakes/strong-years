import type { Metadata } from "next";

export const metadata: Metadata = { title: "Confirm your email", robots: { index: false } };
export const dynamic = "force-dynamic";

/**
 * The email link lands here; confirming takes one button press (a POST), so mail
 * scanners that open links don't confirm on anyone's behalf.
 */
export default async function WaitlistConfirm({ searchParams }: { searchParams: Promise<{ token?: string; error?: string }> }) {
  const { token, error } = await searchParams;
  const clean = token && /^[A-Za-z0-9_-]{10,100}$/.test(token) ? token : null;
  return (
    <div className="narrow py-12" data-testid="waitlist-confirm">
      <h1 className="text-4xl">{error ? "That link didn't work" : "One tap to confirm"}</h1>
      {error === "expired" && <p className="card mt-6 text-lg font-bold" role="alert">This link has expired or was already used. If you&apos;re already confirmed, you&apos;re all set. Otherwise, join again and we&apos;ll send a fresh one.</p>}
      {error === "busy" && <p className="card mt-6 text-lg font-bold" role="alert">Too many tries from this connection. Please wait a few minutes and use the link again.</p>}
      {clean && !error ? (
        <form action="/api/waitlist/confirm" method="post" className="card mt-6 space-y-4">
          <input type="hidden" name="token" value={clean} />
          <p className="text-lg">Confirm this is your email, and you&apos;re on the Strong Years waitlist.</p>
          <button type="submit" className="btn-primary" data-testid="waitlist-confirm-button">Yes, confirm my email</button>
        </form>
      ) : (
        <p className="mt-6">
          <a href="/waitlist" className="btn-outline">Back to the waitlist</a>
        </p>
      )}
    </div>
  );
}
