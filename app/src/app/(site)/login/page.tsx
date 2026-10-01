import type { Metadata } from "next";
import { env, mode } from "@/lib/config";
import { loginDemoLink, loginError } from "@/lib/loginView";

export const metadata: Metadata = { title: "Log in" };
export const dynamic = "force-dynamic";

export default async function Login({ searchParams }: { searchParams: Promise<{ sent?: string; link?: string; error?: string }> }) {
  const { sent, link: rawLink, error: code } = await searchParams;
  // L1: fixed messages only; the link only in the demo, only to our own verify route.
  const error = loginError(code);
  const link = loginDemoLink(rawLink, { mockDb: mode.mockDb, siteUrl: env.siteUrl });
  return (
    <div className="narrow py-12">
      <h1 className="text-4xl">Log in to Strong Years</h1>
      <p className="mt-4 text-lg">No password. Type the email you used at checkout and we&apos;ll send you a 6-digit code and a link. Either one signs you in.</p>
      {error && <p role="alert" className="mt-4 rounded-xl border-2 border-ink bg-brass p-4 font-bold">{error}</p>}
      {sent ? (
        <div className="card mt-8" data-testid="login-sent">
          <p className="text-xl font-bold">Check your email. The code and the link work for 30 minutes.</p>
          <form action="/api/auth/code" method="post" className="mt-5 space-y-4">
            <label className="label" htmlFor="code">The 6-digit code from the email</label>
            <input id="code" name="code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9 ]{6,7}" maxLength={7} className="field max-w-[260px] text-2xl tracking-normal" required />
            <button type="submit" className="btn-primary">Sign me in</button>
          </form>
          <p className="mt-5">
            No email after a few minutes? Check spam, or{" "}
            <a href="/login" className="font-bold text-ink underline">send a new code</a>.
          </p>
          {link && (
            <p className="mt-4">
              Demo mode (no email provider set), so here is your link:{" "}
              <a href={link} className="font-bold text-jade underline">
                Log me in
              </a>
            </p>
          )}
        </div>
      ) : (
        <form action="/api/auth/magic" method="post" className="card mt-8 space-y-4">
          <label className="label" htmlFor="email">Email</label>
          <input id="email" name="email" type="email" className="field" autoComplete="email" required />
          <button type="submit" className="btn-primary">Email me a sign-in code</button>
        </form>
      )}
      {mode.mockDb && (
        <form action="/api/auth/demo" method="post" className="mt-8 rounded-2xl border-2 border-ink bg-brass p-5">
          <p className="font-bold">Demo mode: explore the member area as the demo member &ldquo;Pat&rdquo; (test data).</p>
          <button type="submit" className="btn-ink mt-3" data-testid="demo-login">Enter the demo member area</button>
        </form>
      )}
    </div>
  );
}
