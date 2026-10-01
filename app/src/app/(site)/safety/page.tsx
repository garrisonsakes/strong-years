import type { Metadata } from "next";
import { LEGAL_UPDATED, LegalPage } from "@/components/LegalPage";
import { env } from "@/lib/config";
import { coverage, tzLabel } from "@/lib/safety/oncall";

export const metadata: Metadata = { title: "Crisis protocol for Ask Chang & Ask Sun" };
export const dynamic = "force-dynamic";

/** California SB 243 asks companion-chat operators to publish this protocol. */
export default function Safety() {
  const hours = process.env.ONCALL_HOURS ?? "07:00-23:00";
  const always = /^24\s*\/\s*7$/i.test(hours);
  const cov = coverage();
  return (
    <LegalPage
      title="Our crisis protocol for Ask Chang and Ask Sun"
      updated={LEGAL_UPDATED}
      intro={
        <p>
          <strong>If you are in danger now, call 911.</strong> If you&apos;re thinking about hurting yourself, call or text <strong>988</strong> (Suicide &amp; Crisis Lifeline), any time, free. For elder abuse, neglect or scams, call the Eldercare Locator at <strong>1-800-677-1116</strong>.
        </p>
      }
      sections={[
        {
          heading: "Who you are talking to",
          body: (
            <>
              <p>Chang Yin and Sun Yoon are AI characters, not people, and not doctors, therapists or nutritionists. They say so at the start of every chat and again at least every three hours while a conversation continues. The chat is for exercise and food. It is not therapy and it never gives medical or medication advice.</p>
            </>
          ),
        },
        {
          heading: "What we watch for",
          body: (
            <ul className="list-disc space-y-1 pl-6">
              <li>Thoughts of suicide or self-harm, including indirect ones (&ldquo;everyone would be better off without me&rdquo;, saving up pills).</li>
              <li>Medical emergencies: chest pain or pressure, trouble breathing, signs of a stroke, a fall with an injury or a head strike, not being able to get up, fainting.</li>
              <li>Abuse, neglect, threats or someone taking your money.</li>
              <li>Grief and loneliness, which get a gentler response and a person&apos;s follow-up.</li>
            </ul>
          ),
        },
        {
          heading: "How we detect it",
          body: (
            <>
              <p>Every message is checked before the AI answers. A rules-based check reads it first (it understands typos and odd spacing), then, where available, an AI safety check reads it with your recent messages for context.</p>
              <p>We fail safe: if the safety check is unavailable or unsure about a worrying message, we treat it as a possible crisis. Sometimes that means we check on someone who was fine. We&apos;d rather do that.</p>
            </>
          ),
        },
        {
          heading: "What happens next",
          body: (
            <ol className="list-decimal space-y-1 pl-6">
              <li>The character stops. You get a fixed message written by our team (never generated) with 988, 911 and the Eldercare Locator, as fits the situation.</li>
              <li>The event is logged and a real person on our team is alerted. Alerts contain a link to our private admin, not what you wrote.</li>
              <li>A person follows up with you by email. For grief and loneliness, that&apos;s within 24 hours.</li>
            </ol>
          ),
        },
        {
          heading: "When a person is on duty",
          body: (
            <>
              <p>
                {always
                  ? "A person on our team is on call around the clock."
                  : `A person on our team is on call from ${hours.replace("-", " to ")} (${tzLabel(process.env.ONCALL_TZ ?? "America/New_York")} time), every day. Outside those hours the chat tells you honestly that our team is offline and when a person will read your message (by ${cov.nextStaffed}), and points you to 988 and 911 in the meantime.`}
              </p>
              <p>We are an app, not an emergency service. We cannot send help to your home. Please call 911 for that.</p>
            </>
          ),
        },
        {
          heading: "Your data",
          body: (
            <p>Crisis events are kept separately, seen only by the people who follow up, and never used for advertising. See our consumer health data policy for details.</p>
          ),
        },
        {
          heading: "Reporting",
          body: (
            <p>
              We count (without names) how often the crisis protocol runs and will report those numbers as California law requires from July 2027. Questions or concerns about this protocol: <a href={`mailto:${env.supportEmail}`} className="font-bold text-ink underline">{env.supportEmail}</a>.
            </p>
          ),
        },
      ]}
    />
  );
}
