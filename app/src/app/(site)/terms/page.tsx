import type { Metadata } from "next";
import { livePrices } from "@/lib/livePricing";
import Link from "next/link";
import { LEGAL_UPDATED, LegalPage } from "@/components/LegalPage";
import { blitz, env, messaging, offerRules } from "@/lib/config";
import { getFoundingOffer } from "@/lib/request";
import { money } from "@/lib/pricing";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Terms of service" };

export default async function Terms() {
  const offer = await getFoundingOffer();
  const live = livePrices(offer);
  const fp = money(live.memberCents);
  const trialOn = blitz.trialArmEnabled;
  const cancelOther = messaging.smsEnabled ? "Or text CANCEL, or reply “cancel” to any email." : "Or reply “cancel” to any of our emails.";
  return (
    <LegalPage
      title="Terms of service"
      updated={LEGAL_UPDATED}
      intro={<p>These terms are an agreement between you and {env.legalEntity} (&ldquo;Strong Years&rdquo;). The membership summary comes first because it&apos;s what most people need.</p>}
      sections={[
        {
          id: "membership",
          heading: "Membership, renewal and cancellation (the short version)",
          body: (
            <div className="card space-y-3" data-testid="terms-summary">
              {trialOn && <p><strong>$1 trial:</strong> $1 today for 7 days. Then <span data-testid="terms-trial-renew">{money(live.trialRenewCents)}</span> every month, on the same date, until you cancel.</p>}
              <p><strong>{offer.founding ? "Founding membership" : "Membership"}:</strong> {fp} today for your first month (the exact amount is shown above the pay button), then the same amount every month, on the same date, until you cancel.{offer.founding ? ` Your founding price stays the same for as long as you stay subscribed. Limited to the first ${offerRules.foundingCap.toLocaleString("en-US")} founding members; after that, new members pay the standard price.` : ""}</p>
              <p><strong>Optional extras at checkout</strong> (the $7 Strength Reset, the $17 Strong Kitchen, the $9 Wall Plan): one-time payments, yours to keep, delivered as downloads watermarked with your email. They never renew. Refunded on request within 14 days.</p>
              <p><strong>Gifts:</strong> prepaid for 3 or 12 months. They never renew automatically.</p>
              <p><strong>Reminders:</strong> we email you 48 hours before every charge{messaging.smsEnabled ? " (and text you, if you asked for texts)" : ""}. Monthly members also get a yearly summary of their membership. Yearly plans get a reminder 30 days before renewal. Price changes get 30 days&apos; notice by email, and you can cancel before they apply.</p>
              <p><strong>Cancel anytime, online:</strong> Account, then Cancel membership. At most two screens: one optional question and one offer, with a Finish canceling button right beside it, the same size. {cancelOther} Nobody will call you, and you never need to call us to cancel{env.billingPhone ? ` (billing questions: ${env.billingPhone})` : ""}. Your cancellation is confirmed on screen and by email, and you keep access until the end of the period you paid for.</p>
              <p><strong>Refunds:</strong> 14-day money-back guarantee on your first membership charge, self-serve in your account (one guarantee per person). Add-ons and gifts: see the <Link href="/refunds" className="font-bold text-ink underline">refund policy</Link>.</p>
              <p><strong>On your statement:</strong> STRONGYEARS MEMBER.</p>
              <p className="fine">We keep a record of the terms you saw and agreed to at checkout (the exact wording, the date and time, and the price) for at least four years.</p>
            </div>
          ),
        },
        {
          heading: "Who can use Strong Years",
          body: <p>You must be 18 or older and able to agree to these terms. One membership is for one person; a partner seat adds a second person in your household.</p>,
        },
        {
          id: "exercise-risk",
          heading: "Exercise safety and your responsibility",
          body: (
            <>
              <p><strong>Talk to your doctor before you start, especially if you have a heart or lung condition, recent surgery, a recent fall, dizziness, osteoporosis, or take blood-thinning medicine.</strong> Strong Years is general fitness and nutrition education, not medical care, physical therapy or a diagnosis.</p>
              <p>Exercise, including balance practice and chair stands, carries a risk of injury, including falls. Use a sturdy chair against a wall and a counter or a person nearby for balance work, follow the easier version when in doubt, and stop at once if you feel chest pain, shortness of breath, dizziness or sharp pain. By using the sessions you accept these risks, to the extent the law allows.</p>
            </>
          ),
        },
        {
          heading: "The AI characters",
          body: (
            <>
              <p>Chang Yin and Sun Yoon are AI characters, not real people, and not doctors, therapists, dietitians or pharmacists. Their replies can be wrong. Don&apos;t use them for medical decisions, medicines or emergencies. They say they are AI at the start of every chat and at least every three hours.</p>
              <p>Our <Link href="/safety" className="font-bold text-ink underline">crisis protocol</Link> explains what happens if a message suggests you may be in danger. Please be kind: don&apos;t use the chat to harass, to seek harmful instructions, or to try to break its safety rules.</p>
            </>
          ),
        },
        {
          heading: "Your content and ours",
          body: (
            <p>Sessions, recipes, printables and videos are ours or licensed to us. Your membership gives you a personal, non-transferable licence to use them while you&apos;re a member; downloads you bought are yours to keep for personal use. Please don&apos;t resell or republish them. What you write stays yours; you let us store and process it to run the service, as our privacy policy describes.</p>
          ),
        },
        {
          heading: "Changes to the service or the price",
          body: <p>We may improve or change features. We&apos;ll tell you by email at least 30 days before any price change to your membership, and you can cancel before it applies. A founding price doesn&apos;t change while you stay subscribed.</p>,
        },
        {
          heading: "Ending your membership",
          body: <p>You can cancel anytime as described above. We may suspend or end an account that breaks these terms, commits fraud or abuses refunds; we&apos;ll tell you why and refund any unused prepaid period unless the law says otherwise.</p>,
        },
        {
          heading: "Disclaimers and limits of liability",
          body: (
            <p>Strong Years is provided &ldquo;as is&rdquo;. To the extent the law allows, we are not liable for indirect or consequential losses, and our total liability for any claim is limited to what you paid us in the 12 months before it. Nothing here limits liability that can&apos;t legally be limited, such as for death or personal injury caused by our negligence, or your rights as a consumer.</p>
          ),
        },
        {
          heading: "Disputes",
          body: (
            <p>Please contact us first; most things are fixed with one email. [Governing law, venue, and any arbitration or class-action terms are to be written by counsel. Until then, you keep every right you have under your own state&apos;s consumer law.]</p>
          ),
        },
        {
          heading: "Contact",
          body: (
            <p>
              {env.legalEntity}, {env.mailingAddress}. <a href={`mailto:${env.supportEmail}`} className="font-bold text-ink underline">{env.supportEmail}</a>
            </p>
          ),
        },
      ]}
    />
  );
}
