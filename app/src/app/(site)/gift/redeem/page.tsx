import type { Metadata } from "next";

export const metadata: Metadata = { title: "Start your gift", robots: { index: false } };

const ERRORS: Record<string, string> = {
  code: "We couldn't find that code. Check the email from Sun Yoon, or ask the person who gave it to you.",
  used: "This gift has already been started. Log in with the email address it was sent to.",
  busy: "Too many tries. Please wait a little and try again.",
};

export default async function Redeem({ searchParams }: { searchParams: Promise<{ code?: string; error?: string; sent?: string; to?: string }> }) {
  const { code, error, sent, to } = await searchParams;
  const message = error ? (ERRORS[error] ?? ERRORS.code) : null;
  return (
    <div className="narrow py-12">
      <h1 className="text-4xl">Someone gave you Strong Years.</h1>
      <p className="mt-4 text-lg">It&apos;s prepaid. It never renews by itself, and nobody will charge your card. When it ends, we&apos;ll ask whether you want to continue.</p>
      {sent ? (
        <div className="card mt-8" role="status" data-testid="gift-sent">
          <p className="text-xl font-bold">Check your email{to ? ` (${to})` : ""}.</p>
          <p className="mt-2">We&apos;ve sent a private link to the address the gift was sent to. Open it on this device to start. For your privacy, the gift only opens from that email.</p>
        </div>
      ) : (
        <>
          {message && <p role="alert" className="mt-4 rounded-xl border-2 border-ink bg-brass p-4 font-bold">{message}</p>}
          <p className="mt-6">The fastest way in is the link in your gift email. If you can&apos;t find it, type your gift code and we&apos;ll email a fresh link to you.</p>
          <form action="/api/gift/redeem" method="post" className="card mt-6 space-y-4">
            <div>
              <label className="label" htmlFor="code">Your gift code</label>
              <input id="code" name="code" className="field" defaultValue={code ?? ""} autoComplete="off" required />
            </div>
            <button type="submit" className="btn-primary">Email me my gift link</button>
          </form>
        </>
      )}
    </div>
  );
}
