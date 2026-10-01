import type { Metadata } from "next";
import { LEGAL_UPDATED, LegalPage } from "@/components/LegalPage";
import { currentMember } from "@/lib/auth/server";
import { adsOptedOut } from "@/lib/request";
import { headers } from "next/headers";

export const metadata: Metadata = { title: "Your privacy choices" };
export const dynamic = "force-dynamic";

export default async function PrivacyChoices({ searchParams }: { searchParams: Promise<{ done?: string }> }) {
  const { done } = await searchParams;
  const member = await currentMember();
  const gpc = (await headers()).get("sec-gpc") === "1";
  const optedOut = (await adsOptedOut()) || Boolean(member?.ad_opt_out);
  return (
    <LegalPage
      title="Your privacy choices"
      updated={LEGAL_UPDATED}
      intro={<p>Opt out of the &ldquo;sale&rdquo; or &ldquo;sharing&rdquo; of your personal information for advertising (California, and the other states with similar rights).</p>}
      sections={[
        {
          heading: "What this turns off",
          body: (
            <p>We send Meta a scrambled (hashed) email when someone completes the Strength Age quiz or buys, so we can see which ads work. California calls that &ldquo;sharing&rdquo;. When you opt out, we send nothing about you to Meta or any ad platform. Health information is never shared, opted out or not.</p>
          ),
        },
        {
          heading: "Global Privacy Control",
          body: (
            <p>If your browser sends the Global Privacy Control signal, we treat it as an opt-out automatically.{gpc ? " Your browser is sending it right now, so you're already opted out on this device." : ""}</p>
          ),
        },
      ]}
    >
      <div className="card space-y-4" data-testid="privacy-choices">
        {done && <p role="status" className="rounded-xl border-2 border-ink bg-jade p-4 font-bold text-rice">Done. You&apos;re opted out.</p>}
        <p className="text-xl font-bold">Status: {optedOut ? "opted out. Nothing about you is shared for advertising." : "not opted out."}</p>
        {!optedOut && (
          <form action="/api/privacy/opt-out" method="post">
            <button type="submit" className="btn-primary" data-testid="opt-out">Do not sell or share my personal information</button>
          </form>
        )}
        <p className="fine">{member ? "This applies to your account on every device." : "This applies to this browser. Log in first to apply it to your account on every device."}</p>
      </div>
    </LegalPage>
  );
}
