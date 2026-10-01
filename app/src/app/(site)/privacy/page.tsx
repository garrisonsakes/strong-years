import type { Metadata } from "next";
import Link from "next/link";
import { LEGAL_UPDATED, LegalPage } from "@/components/LegalPage";
import { env, messaging } from "@/lib/config";

export const metadata: Metadata = { title: "Privacy policy" };
export const dynamic = "force-dynamic";

const PROCESSORS: [string, string][] = [
  ["Stripe", "payments and card storage (we never see your full card number)"],
  ["Supabase", "our database hosting (United States)"],
  ["Vercel", "website hosting"],
  ["Anthropic", "the AI behind Ask Chang and Ask Sun, and our safety check (it does not train on your messages under our agreement)"],
  ["Resend or Postmark", "sending our emails"],
  ["Twilio", messaging.smsEnabled ? "sending the texts you asked for" : "texts, once we switch them on (not active today)"],
  ["Meta (Facebook / Instagram)", "advertising measurement only, as described in section 5"],
];

export default function Privacy() {
  return (
    <LegalPage
      title="Privacy policy"
      updated={LEGAL_UPDATED}
      intro={
        <p>
          This policy explains what {env.legalEntity} (&ldquo;Strong Years&rdquo;, &ldquo;we&rdquo;) collects, why, who we share it with and your choices. Health-related information has its own, stricter policy:{" "}
          <Link href="/health-data" className="font-bold text-ink underline">Consumer health data privacy policy</Link>.
        </p>
      }
      sections={[
        {
          heading: "What we collect",
          body: (
            <ul className="list-disc space-y-1 pl-6">
              <li><strong>Contact details:</strong> your first name, email, and your mobile number if you ask for texts.</li>
              <li><strong>Account and billing:</strong> your plan, charges, refunds, cancellations and the exact terms you agreed to. Card details are held by Stripe, not us.</li>
              <li><strong>Quiz answers and results</strong>, your practice log, Strength Age retests, and what you tell Ask Chang and Ask Sun. These are consumer health data (see the separate policy).</li>
              <li><strong>Technical data:</strong> IP address, browser type, and first-party cookies that keep you logged in, remember your price, and record which ad or link brought you here (utm tags, a click id).</li>
            </ul>
          ),
        },
        {
          heading: "How we use it",
          body: (
            <ul className="list-disc space-y-1 pl-6">
              <li>To run your membership: sessions, reminders, receipts, renewal notices, cancellations and refunds.</li>
              <li>To send the messages you ask for (quiz results, the Sunday recipe email, texts if you opted in).</li>
              <li>To keep you safe in the coach chat (see our <Link href="/safety" className="font-bold text-ink underline">crisis protocol</Link>).</li>
              <li>To understand which ads and pages work, in the limited way described in section 5.</li>
              <li>To meet legal duties, such as keeping records of the renewal terms you agreed to for at least four years.</li>
            </ul>
          ),
        },
        {
          heading: "Coach memory",
          body: <p>Ask Chang and Ask Sun only remember things if you turn memory on in Settings. You can see every item, delete any of them, or delete all of them, anytime.</p>,
        },
        {
          heading: "Who we share it with",
          body: (
            <>
              <p>We use these service providers to run Strong Years. They may only use your information to provide their service to us.</p>
              <ul className="list-disc space-y-1 pl-6">
                {PROCESSORS.map(([n, d]) => (
                  <li key={n}>
                    <strong>{n}:</strong> {d}.
                  </li>
                ))}
              </ul>
              <p>We don&apos;t sell your information for money. We never share quiz answers, results, chat messages or anything about your health with advertisers.</p>
            </>
          ),
        },
        {
          id: "advertising",
          heading: "Advertising, and your right to opt out",
          body: (
            <>
              <p>
                To see which ads work, we tell Meta when someone completes the Strength Age quiz or makes a purchase, with your email (and phone, if given) in a scrambled, hashed form. The event carries a neutral page address and no answers, results or health words. Nothing at all is sent for the gut &amp; energy quiz.
              </p>
              <p>
                Under California law this counts as &ldquo;sharing&rdquo; for cross-context advertising. You can opt out on our{" "}
                <Link href="/privacy-choices" className="font-bold text-ink underline">Your Privacy Choices</Link> page, and we honour the Global Privacy Control signal your browser may send automatically. Once you opt out, nothing about you is sent to Meta.
              </p>
            </>
          ),
        },
        {
          heading: "How long we keep it",
          body: (
            <ul className="list-disc space-y-1 pl-6">
              <li>Account, practice and chat data: while you&apos;re a member, then 90 days after you leave (in case you come back), then deleted unless you ask us to keep it.</li>
              <li>Quiz leads who never join: 12 months.</li>
              <li>Billing records and the renewal terms you agreed to: at least 4 years, as required by law.</li>
              <li>Crisis-protocol records: 2 years, then deleted.</li>
            </ul>
          ),
        },
        {
          heading: "Your rights",
          body: (
            <>
              <p>Depending on where you live (including California, Colorado, Connecticut, Virginia, Oregon, Texas and Washington), you can ask to see, correct, download or delete your information, and to opt out of targeted advertising. We give these rights to everyone.</p>
              <p>
                Email <a href={`mailto:${env.privacyEmail}`} className="font-bold text-ink underline">{env.privacyEmail}</a> from the address on your account. We reply within 45 days. If we say no, you can appeal by replying to our answer; we decide appeals within 45 days.
              </p>
            </>
          ),
        },
        {
          heading: "Children",
          body: <p>Strong Years is for adults 18 and over. We don&apos;t knowingly collect information from anyone younger.</p>,
        },
        {
          heading: "Security",
          body: <p>Data is encrypted in transit, stored with access controls, and login links are single-use. No system is perfect; if something goes wrong, we&apos;ll tell you as the law requires.</p>,
        },
        {
          heading: "Changes and contact",
          body: (
            <p>
              We&apos;ll email members before any material change. {env.legalEntity}, {env.mailingAddress}. <a href={`mailto:${env.privacyEmail}`} className="font-bold text-ink underline">{env.privacyEmail}</a>
            </p>
          ),
        },
      ]}
    />
  );
}
