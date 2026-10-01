import type { Metadata } from "next";
import Link from "next/link";
import { LEGAL_UPDATED, LegalPage } from "@/components/LegalPage";
import { blitz, env, prices } from "@/lib/config";
import { moneyExact } from "@/lib/pricing";

export const metadata: Metadata = { title: "Refund policy" };
export const dynamic = "force-dynamic";

export default function Refunds() {
  const trialOn = blitz.trialArmEnabled;
  return (
    <LegalPage
      title="Refund policy"
      updated={LEGAL_UPDATED}
      intro={<p>The short version: your first membership charge has a 14-day money-back guarantee you can use yourself, in two taps. Add-ons are one-time purchases with their own terms. Gifts can be refunded until they&apos;re started.</p>}
      sections={[
        {
          heading: "Membership: 14-day money-back guarantee",
          body: (
            <>
              <p>If Strong Years isn&apos;t for you, go to Account and tap &ldquo;Refund my membership payment&rdquo; within 14 days of your first membership charge. We refund that charge in full and end your membership. You won&apos;t be charged again.</p>
              {trialOn && <p>If you started with the {moneyExact(prices.trialFee)} trial, the guarantee covers your first full membership charge, for 14 days from the day of that charge.</p>}
              <p>The guarantee covers your first membership charge only, not later monthly renewals. Cancel anytime to stop future charges; you keep access until the end of the month you paid for.</p>
              <p>We only tell you a refund is done after our payment processor confirms it. If your bank is still processing it, we say so and email you when it&apos;s confirmed.</p>
            </>
          ),
        },
        {
          heading: "One guarantee per person",
          body: (
            <p>The money-back guarantee can be used once per person. We recognise repeat requests by email address and by the card used. A repeat request isn&apos;t refused automatically: it goes to a person on our team, who replies by email within one business day.</p>
          ),
        },
        {
          heading: "Your bonus material",
          body: (
            <p>Your daily sessions, the coaches and the kitchen are available from day 1. The printable program book is a bonus that unlocks on day 15, after the money-back window closes. If you take the refund, the bonus isn&apos;t unlocked.</p>
          ),
        },
        {
          heading: "Add-ons (the Strength Reset, the Strong Kitchen, the Wall Plan and one-click extras)",
          body: (
            <>
              <p>Add-ons are one-time purchases, delivered straight away as downloads watermarked with your name, email and order number, and they never renew. They are not part of the self-serve membership refund.</p>
              <p>Add-ons are refunded on request within 14 days: reply to any of our emails. The Strong Years Kit (the physical box): 30 days, no need to send it back.</p>
            </>
          ),
        },
        {
          heading: "Gifts",
          body: (
            <p>A gift can be refunded in full to the person who paid, any time before the recipient starts it. Once started, it isn&apos;t refundable, but it never renews and nobody is ever charged for it.</p>
          ),
        },
        {
          heading: "Chargebacks",
          body: (
            <p>If something went wrong, please ask us first: it&apos;s faster than a chargeback. If a chargeback is opened, we stop any further charges on that membership straight away.</p>
          ),
        },
        {
          heading: "How to ask",
          body: (
            <p>
              Membership refunds: <Link href="/app/account" className="font-bold text-ink underline">your account</Link>. Anything else: reply to any email or write to{" "}
              <a href={`mailto:${env.supportEmail}`} className="font-bold text-ink underline">{env.supportEmail}</a>. Refunds usually show on your card in 5 to 10 days.
            </p>
          ),
        },
      ]}
    />
  );
}
