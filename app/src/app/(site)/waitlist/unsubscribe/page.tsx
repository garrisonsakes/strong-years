import type { Metadata } from "next";

export const metadata: Metadata = { title: "Leave the waitlist", robots: { index: false } };
export const dynamic = "force-dynamic";

/** One button (mail scanners that open links don't press it). */
export default async function Unsubscribe({ searchParams }: { searchParams: Promise<{ u?: string; done?: string; error?: string }> }) {
  const { u, done, error } = await searchParams;
  return (
    <div className="narrow py-12" data-testid="waitlist-unsubscribe">
      {done ? (
        <>
          <h1 className="text-4xl">You&apos;ve left the waitlist.</h1>
          <p className="card mt-6 text-lg">We won&apos;t send you any more launch emails or notifications, and we&apos;ve withdrawn any ad-measurement permission you gave.</p>
        </>
      ) : (
        <>
          <h1 className="text-4xl">Leave the Strong Years waitlist?</h1>
          {error && <p className="card mt-6 font-bold" role="alert">{error === "busy" ? "Too many tries. Please wait a few minutes." : "That link didn't work. Use the link in the newest email from us."}</p>}
          {u && /^[0-9a-f-]{36}\.[A-Za-z0-9_-]{10,40}$/.test(u) && (
            <form action="/api/waitlist/unsubscribe" method="post" className="card mt-6 space-y-4">
              <input type="hidden" name="u" value={u} />
              <p className="text-lg">You won&apos;t get the launch email or any notifications.</p>
              <button type="submit" className="btn-ink" data-testid="unsubscribe-button">Yes, take me off the list</button>
            </form>
          )}
        </>
      )}
    </div>
  );
}
