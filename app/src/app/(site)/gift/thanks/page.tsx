import Link from "next/link";
import { getShopCta } from "@/lib/shopCheckout";
import { livePrices } from "@/lib/livePricing";
import { RenewalNote } from "@/components/Pricing";
import { blitz } from "@/lib/config";
import { money } from "@/lib/pricing";
import { getFoundingOffer } from "@/lib/request";

export const dynamic = "force-dynamic";

export default async function GiftThanks() {
  const trialOn = blitz.trialArmEnabled;
  const offer = await getFoundingOffer();
  const shop = await getShopCta();
  return (
    <div className="narrow py-12" data-testid="gift-thanks">
      <h1 className="text-4xl">Thank you. Your gift is on its way.</h1>
      <p className="mt-4 text-lg">We&apos;ve emailed Sun Yoon&apos;s welcome card and a private link to start their gift, straight to their inbox. The gift is prepaid and never renews automatically.</p>
      <div className="card mt-10">
        <h2 className="text-2xl">{trialOn ? "And you? Start your own 7 days for $1." : "And you? Join as a founding member."}</h2>
        <Link href={trialOn ? "/checkout/trial" : "/join"} className="btn-primary mt-5">
          {shop ? shop.label : trialOn ? "Start 7 days for $1" : `Join for ${money(offer.priceCents)} today`}
        </Link>
        {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={trialOn ? "trial" : "founding"} priceCents={trialOn ? livePrices(offer).trialRenewCents : livePrices(offer).memberCents} />}
      </div>
    </div>
  );
}
