import type { Metadata } from "next";
import Link from "next/link";
import { getStore } from "@/lib/db";
import { giftForClaimToken } from "@/lib/gifts";

export const metadata: Metadata = { title: "Start your gift", robots: { index: false } };
export const dynamic = "force-dynamic";

/** Showing this page changes nothing (email scanners may open links); the button does. */
export default async function Claim({ searchParams }: { searchParams: Promise<{ token?: string; error?: string }> }) {
  const { token = "", error } = await searchParams;
  const gift = await giftForClaimToken(await getStore(), token);
  if (!gift) {
    return (
      <div className="narrow py-12">
        <h1 className="text-4xl">This gift link has expired or was already used.</h1>
        <p className="mt-4 text-lg">If you&apos;ve started your gift already, log in with your email. Otherwise, enter your gift code and we&apos;ll send a fresh link.</p>
        <p className="mt-6 flex flex-wrap gap-3">
          <Link href="/login" className="btn-primary">Log in</Link>
          <Link href="/gift/redeem" className="btn-outline">Enter my gift code</Link>
        </p>
      </div>
    );
  }
  return (
    <div className="narrow py-12">
      <h1 className="text-4xl">{gift.gifter_name} gave you {gift.months} months of Strong Years.</h1>
      <p className="mt-4 text-lg">It&apos;s prepaid. It never renews by itself, and nobody will charge your card.</p>
      {gift.message && <blockquote className="mt-4 rounded-xl border-2 border-ink bg-cream p-4 text-lg">&ldquo;{gift.message}&rdquo;</blockquote>}
      {error === "age" && <p role="alert" className="mt-4 rounded-xl border-2 border-ink bg-brass p-4 font-bold">Strong Years is for adults 18 and over.</p>}
      <form action="/api/gift/claim" method="post" className="card mt-8 space-y-4">
        <input type="hidden" name="token" value={token} />
        <div>
          <label className="label" htmlFor="first_name">Your first name</label>
          <input id="first_name" name="first_name" className="field" defaultValue={gift.recipient_name} required />
        </div>
        <label className="flex cursor-pointer items-start gap-3">
          <input type="checkbox" name="age" className="check" required />
          <span className="font-bold">I am 18 or older.</span>
        </label>
        <label className="flex cursor-pointer items-start gap-3">
          <input type="checkbox" name="share" className="check" />
          <span>Send {gift.gifter_name} a monthly note with my session count (optional, you can turn it off anytime).</span>
        </label>
        <button type="submit" className="btn-primary" data-testid="claim-gift">Start my gift</button>
      </form>
    </div>
  );
}
