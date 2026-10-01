import type { Metadata } from "next";
import { WaitlistPushOptIn } from "@/components/WaitlistPushOptIn";
import { getStore } from "@/lib/db";
import { vapid } from "@/lib/push";
import { REFERRAL_BONUS_NAME, WAITLIST_PUSH_CONSENT_TEXT, confirmedReferrals, waitlistLinks } from "@/lib/waitlist";
import { signUnsub, verifyAccess } from "@/lib/waitlistTokens";

export const metadata: Metadata = { title: "You're on the list", robots: { index: false } };
export const dynamic = "force-dynamic";

export default async function WaitlistConfirmed({ searchParams }: { searchParams: Promise<{ k?: string }> }) {
  const { k } = await searchParams;
  const id = verifyAccess(k);
  const entry = id ? await (await getStore()).get("waitlist", id) : null;
  if (!entry || entry.status !== "confirmed" || !k) {
    return (
      <div className="narrow py-12">
        <h1 className="text-4xl">This page link has expired</h1>
        <p className="mt-4 text-lg">Use the newest email from us; every one has a fresh link.</p>
      </div>
    );
  }
  const links = waitlistLinks(entry);
  const friends = await confirmedReferrals(await getStore(), entry.id);
  const v = vapid();
  return (
    <div className="narrow space-y-6 py-12" data-testid="waitlist-confirmed">
      <h1 className="text-4xl">You&apos;re on the list{entry.first_name ? `, ${entry.first_name}` : ""}.</h1>
      <p className="text-lg">When checkout opens, you get the email first, at the founding price. There&apos;s no queue: everyone on the list hears at the same moment.</p>
      <a href={`/waitlist/starter?k=${encodeURIComponent(k)}`} className="btn-primary" data-testid="starter-link">Start Day 1 now (free, 9 minutes)</a>
      {v.configured && <WaitlistPushOptIn vapidPublicKey={v.publicKey} access={k} consentText={WAITLIST_PUSH_CONSENT_TEXT} />}
      <section className="card space-y-3">
        <h2 className="text-2xl">Know someone who&apos;d like this?</h2>
        <p>Send them your link. When one of them confirms their email, you get {REFERRAL_BONUS_NAME}, free. That&apos;s the whole reward: it doesn&apos;t move anyone up a list, because there isn&apos;t one.</p>
        <p className="break-all rounded-xl border-2 border-ink bg-paper p-3 font-bold" data-testid="referral-link">{links.referral}</p>
        <p>{friends === 0 ? "No friends have confirmed yet." : `${friends} friend${friends === 1 ? " has" : "s have"} confirmed.`}{entry.referral_reward_at ? " Your Wall Plan is unlocked: it's in your email." : ""}</p>
      </section>
      <form action="/api/waitlist/unsubscribe" method="post">
        <input type="hidden" name="u" value={signUnsub(entry.id)} />
        <button type="submit" className="btn-outline">Leave the waitlist</button>
      </form>
    </div>
  );
}
