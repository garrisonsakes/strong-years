import type { Metadata } from "next";
import Link from "next/link";
import { LaunchCountdown } from "@/components/LaunchCountdown";
import { CharacterArt } from "@/components/Art";
import { env } from "@/lib/config";
import { AD_CONSENT_TEXT } from "@/lib/conversions/text";
import { formatDate, money } from "@/lib/pricing";
import { REF_CODE, WAITLIST_EMAIL_CONSENT_TEXT } from "@/lib/waitlist";
import { signFormTime } from "@/lib/waitlistTokens";
import { waitlistFacts } from "@/lib/waitlistView";

export const metadata: Metadata = {
  title: "Join the Strong Years waitlist",
  description: "Get the first email when Strong Years opens, with first access at the founding price. Free, no queue, one-click unsubscribe.",
};
export const dynamic = "force-dynamic";

const ERRORS: Record<string, string> = {
  email: "Please check your email address.",
  consent: "Please tick the box so we're allowed to email you when it opens.",
  busy: "Too many tries from this connection. Please wait a few minutes and try again.",
  server: "Something went wrong on our side. Nothing was saved. Please try again.",
};

/**
 * The free waitlist (organic-first launch). Honest by construction: the countdown
 * only ever counts to the real CHECKOUT_OPENS_AT, the founding counter is the real
 * count, there's no queue or position, and no testimonials exist yet so none are shown.
 */
export default async function Waitlist({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const f = await waitlistFacts();
  const ref = (sp.ref ?? "").toUpperCase();
  const error = sp.error ? (ERRORS[sp.error] ?? ERRORS.server) : null;
  const price = money(f.memberCents);
  const capText = f.cap.toLocaleString("en-US");

  return (
    <div className="wrap grid items-start gap-x-10 gap-y-8 py-8 lg:grid-cols-[1fr_minmax(0,540px)]" data-testid="waitlist">
      <section className="lg:col-start-1 lg:row-start-1">
        {sp.from === "checkout" && !f.live && (
          <p className="mb-6 rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="status" data-testid="waitlist-closed-note">
            Checkout isn&apos;t open yet, so nothing can be bought or charged today. Join the free waitlist and you&apos;ll hear the moment it opens.
          </p>
        )}
        <h1 className="text-4xl sm:text-5xl">{f.live ? "Strong Years is open." : "Strong Years opens soon. Be the first to hear."}</h1>
        <p className="mt-4 max-w-prose text-lg">
          Eight to twelve minutes a day with Chang Yin, at your level, with a chair version of everything. Sun Yoon&apos;s recipes every Sunday. A Strength Age you retest every month.
        </p>

        {f.live ? (
          <a href="/join" className="btn-primary mt-6" data-testid="waitlist-join-now">See the founding membership</a>
        ) : (
          <div className="mt-6 rounded-xl border-2 border-ink bg-rice p-4" data-testid="waitlist-opening">
            {f.opensAt ? (
              <>
                <p className="text-lg font-bold">Checkout opens {formatDate(f.opensAt, env.displayTimeZone)}.</p>
                <LaunchCountdown opensAtIso={f.opensAt.toISOString()} initialMs={f.opensAt.getTime() - Date.now()} />
              </>
            ) : (
              <p className="text-lg font-bold">The opening date isn&apos;t set yet. Everyone on the list gets the same email at the same moment when it is.</p>
            )}
          </div>
        )}
      </section>

      <section aria-label="Join the waitlist" id="join" className="lg:col-start-2 lg:row-span-2 lg:row-start-1">
        <form action="/api/waitlist" method="post" className="card space-y-5" data-testid="waitlist-form">
          <h2 className="text-2xl">{f.live ? "Not ready yet? Get the free session" : "Join the free waitlist"}</h2>
          {error && (
            <p role="alert" className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" data-testid="waitlist-error">
              {error}
            </p>
          )}
          <input type="hidden" name="ft" value={signFormTime()} />
          {REF_CODE.test(ref) && <input type="hidden" name="ref" value={ref} />}
          {/* Honeypot: people never see or fill this; bots that fill every field get a polite no-op. */}
          <div aria-hidden="true" style={{ position: "absolute", left: "-10000px", width: 1, height: 1, overflow: "hidden" }}>
            <label htmlFor="website">Leave this empty</label>
            <input id="website" name="website" type="text" tabIndex={-1} autoComplete="off" defaultValue="" />
          </div>
          <div>
            <label className="label" htmlFor="first_name">First name (optional)</label>
            <input id="first_name" name="first_name" className="field" autoComplete="given-name" maxLength={60} />
          </div>
          <div>
            <label className="label" htmlFor="email">Email</label>
            <input id="email" name="email" type="email" className="field" autoComplete="email" required maxLength={254} />
          </div>
          <label className="flex items-start gap-3 rounded-xl border-2 border-ink bg-rice p-4">
            <input type="checkbox" name="consent_email" value="1" className="check" required />
            <span className="font-bold">{WAITLIST_EMAIL_CONSENT_TEXT}</span>
          </label>
          <label className="flex items-start gap-3 rounded-xl border-2 border-dashed border-ink bg-cream p-4">
            <input type="checkbox" name="consent_ads" value="1" className="check" />
            <span>{AD_CONSENT_TEXT}</span>
          </label>
          <button type="submit" className="btn-primary sm:w-full" data-testid="waitlist-submit">
            Put me on the list
          </button>
          <p className="fine">
            We&apos;ll send one email to confirm it&apos;s you. Nothing else is sent until you tap it. Free; no card.{" "}
            <Link href="/privacy" className="font-bold underline">Privacy</Link>
          </p>
        </form>
        <div className="mt-8 hidden lg:block">
          <CharacterArt who="chang" />
        </div>
      </section>
      <section className="lg:col-start-1 lg:row-start-2">
        <h2 className="text-2xl">What joining the list gets you</h2>
        <ul className="mt-3 space-y-2">
          {[
            "Today: Day 1 of the Daily Practice, the chair version, free.",
            "The opening email first, with access at the founding price.",
            "At most 3 launch emails in the 72 hours after opening. Then nothing unless you join.",
            "No queue and no places in line. Everyone hears at once.",
          ].map((x) => (
            <li key={x} className="flex gap-3 text-lg">
              <span className="marker !bg-jade" aria-hidden="true" />
              {x}
            </li>
          ))}
        </ul>

        <div className="mt-6 rounded-xl border-2 border-ink bg-rice p-4" data-testid="waitlist-cohort">
          {!f.cohortOpen ? (
            <p className="text-lg font-bold">The founding cohort is full. New members join at {price} a month.</p>
          ) : !Number.isFinite(f.cap) ? (
            <p className="text-lg font-bold">
              Founding membership: {price} a month, locked for as long as you stay subscribed. Open to everyone{f.closeDate ? ` until ${f.closeDate}` : " until the founding close date"}.
            </p>
          ) : f.claimed < 1000 ? (
            <p className="text-lg font-bold">
              Founding membership: {price} a month, locked for as long as you stay subscribed. Open to the first {capText} members{f.closeDate ? ` or until ${f.closeDate}, whichever comes first` : ""}.
            </p>
          ) : (
            <p className="text-lg font-bold">
              {f.claimed.toLocaleString("en-US")} of {capText} founding seats taken. Founding price: {price} a month, locked while you stay subscribed.
            </p>
          )}
          {Number.isFinite(f.cap) && <p className="fine mt-2">A live count from our member database. No timers, no made-up numbers.</p>}
        </div>

        <p className="mt-6 max-w-prose">
          Chang Yin and Sun Yoon are AI characters, and their story is fictional. The sessions are built on published exercise guidelines for older adults. We don&apos;t show reviews yet, because nobody has used it yet.{" "}
          <Link href="/how-we-make-this" className="font-bold underline">How we make this</Link>
        </p>
      </section>

    </div>
  );
}
