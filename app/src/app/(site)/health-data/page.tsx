import type { Metadata } from "next";
import Link from "next/link";
import { LEGAL_UPDATED, LegalPage } from "@/components/LegalPage";
import { env } from "@/lib/config";

export const metadata: Metadata = { title: "Consumer health data privacy policy" };

/** Washington My Health My Data Act (RCW 19.373) and similar state laws (NV SB 370, CT). */
export default function HealthData() {
  return (
    <LegalPage
      title="Consumer health data privacy policy"
      updated={LEGAL_UPDATED}
      intro={
        <p>
          This policy covers information that identifies you and relates to your physical or mental health, as defined by Washington&apos;s My Health My Data Act and similar laws. It applies to everyone, wherever you live. Our general <Link href="/privacy" className="font-bold text-ink underline">privacy policy</Link> covers everything else.
        </p>
      }
      sections={[
        {
          heading: "The consumer health data we collect",
          body: (
            <ul className="list-disc space-y-1 pl-6">
              <li>Quiz answers: safety questions (chest pain, dizziness, a recent fall or surgery, a doctor&apos;s limit), mobility aids, aches, chair-stand and balance results; for the gut &amp; energy quiz, questions about digestion, energy, sleep and medicines.</li>
              <li>Your Strength Age and retest results, practice log and the &ldquo;sore knee / sore back&rdquo; swaps you choose.</li>
              <li>What you write to Ask Chang and Ask Sun, and the memory items (only if you turn memory on). Items about health are marked sensitive.</li>
              <li>Crisis-protocol records when a message raises a safety concern.</li>
            </ul>
          ),
        },
        {
          heading: "Where it comes from",
          body: <p>Only from you: the quiz, the app and the chat. We don&apos;t buy health data or collect it from other companies.</p>,
        },
        {
          heading: "Why we collect and use it",
          body: (
            <ul className="list-disc space-y-1 pl-6">
              <li>To give you your result and a safe starting level (for example, the chair-based track).</li>
              <li>To run your sessions, retests and the coach chat you asked for.</li>
              <li>To keep you safe: stopping the chat and alerting a person when a message suggests a crisis.</li>
            </ul>
            ),
        },
        {
          heading: "Your consent",
          body: (
            <p>We collect this data only when you choose to give it to us for the purpose shown at the time (taking the quiz, using the app, turning on memory). You can withdraw consent at any time by deleting items in Settings or asking us to delete your data. We never make consent a condition of cancelling.</p>
          ),
        },
        {
          heading: "Who we share it with",
          body: (
            <>
              <p>Only processors that help us provide the service you asked for, under contracts that limit them to that: Supabase (database hosting), Anthropic (processing chat messages to write a reply and run the safety check), and our email provider (to send you your own result).</p>
              <p>
                <strong>We never sell consumer health data, and we never share it with advertisers.</strong> Quiz answers, results and chat never go to Meta or any ad platform.
              </p>
            </>
          ),
        },
        {
          heading: "Your rights",
          body: (
            <>
              <p>You can ask us to confirm whether we have your consumer health data, see it and a list of the processors it went to, delete it, and withdraw your consent.</p>
              <p>
                Email <a href={`mailto:${env.privacyEmail}`} className="font-bold text-ink underline">{env.privacyEmail}</a> with the subject &ldquo;Health data request&rdquo;. We verify it&apos;s you by replying to the email on your account, and answer within 45 days (we may extend once by 45 days and will tell you why). If we decline, you can appeal by replying; if you&apos;re still not satisfied, you can contact the Washington State Attorney General at atg.wa.gov.
              </p>
            </>
          ),
        },
        {
          heading: "Keeping it safe",
          body: <p>Health data is stored encrypted, visible only to the few team members who need it, and never included in on-call alerts.</p>,
        },
      ]}
    />
  );
}
