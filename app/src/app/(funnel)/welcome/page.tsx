import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { currentMembership, currentPurchaser } from "@/lib/auth/server";
import { env, messaging } from "@/lib/config";
import { getStore } from "@/lib/db";
import { formatDate, moneyExact } from "@/lib/pricing";

export const metadata: Metadata = { title: "You're in", robots: { index: false } };
export const dynamic = "force-dynamic";

export default async function Welcome() {
  const session = await currentPurchaser();
  if (!session) redirect("/login");
  const member = session.member;
  // R2-1: a checkout for an email nobody has verified yet can't open the program.
  // The inbox owner opens it from the link in the welcome email.
  const mustVerify = session.scope === "purchase";
  const m = await currentMembership(member.id);
  const orders = await (await getStore()).find("sy_orders", { member_id: member.id });
  const trial = m?.status === "trialing";
  const date = m?.current_period_end ? formatDate(m.current_period_end, env.displayTimeZone) : null;
  return (
    <div className="narrow py-10" data-testid="welcome">
      <h1 className="text-4xl">You&apos;re in, {member.first_name}. Your first Daily Practice takes 8 minutes.</h1>
      {mustVerify ? (
        <section className="card mt-8 bg-cream" data-testid="verify-email">
          <h2 className="text-2xl">One quick step: open the link we just emailed you.</h2>
          <p className="mt-2 text-lg">
            We sent it to <strong>{member.email}</strong>. It confirms the email is yours, then takes you straight to Day 1. We ask once, so nobody else can open your program with your address.
          </p>
          <form action="/api/auth/magic" method="post" className="mt-4">
            <input type="hidden" name="email" value={member.email} />
            <button type="submit" className="btn-primary sm:w-full" data-testid="send-open-link">
              Email me the link again
            </button>
          </form>
        </section>
      ) : (
        <Link href="/app" className="btn-primary mt-8 sm:w-full" data-testid="start-day-1">
          Start Day 1 now
        </Link>
      )}
      <ol className="mt-10 space-y-4">
        <li className="card">
          <p className="text-xl font-bold">When do you have your morning tea?</p>
          <p className="mt-1">We&apos;ll send your daily session link then.</p>
          <Link href="/app/settings" className="mt-3 inline-block font-bold text-jade underline">
            Set my reminder time
          </Link>
        </li>
        <li className="card">
          <p className="text-xl font-bold">Put Strong Years on your home screen.</p>
          <p className="mt-1">On iPhone: tap the Share button, then &ldquo;Add to Home Screen&rdquo;. On Android: tap the three dots, then &ldquo;Add to Home screen&rdquo;.</p>
        </li>
        <li className="card">
          <p className="text-xl font-bold">Print your card for the fridge.</p>
          <Link href="/app/printables" className="mt-3 inline-block font-bold text-jade underline">
            Open printables
          </Link>
        </li>
      </ol>
      <section className="card mt-10 bg-cream">
        <h2 className="text-2xl">Your receipt</h2>
        <ul className="mt-3 space-y-1">
          {orders.map((o) => (
            <li key={o.id} className="flex justify-between gap-4">
              <span>{o.description}</span>
              <span className="font-bold">{moneyExact(o.amount_cents)}</span>
            </li>
          ))}
        </ul>
        {m && date && (
          <p className="mt-4 font-bold">
            {trial ? `Trial ends ${date}. You'll be charged ${moneyExact(m.price_cents)} then, and monthly after that, unless you cancel.` : `Next charge: ${moneyExact(m.price_cents)} on ${date}, then monthly until you cancel.`} Cancel here:{" "}
            <Link href="/app/account" className="text-ink underline">
              your account
            </Link>
            {messaging.smsEnabled ? " or text CANCEL." : ", or reply \u201ccancel\u201d to any email. We email you before every charge."}
          </p>
        )}
        <p className="fine mt-3">Chang Yin and Sun Yoon are AI characters. On your statement: STRONGYEARS MEMBER.</p>
      </section>
    </div>
  );
}
