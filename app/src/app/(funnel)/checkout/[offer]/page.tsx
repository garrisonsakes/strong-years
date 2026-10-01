import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { CheckoutForm } from "@/components/CheckoutForm";
import { blitz } from "@/lib/config";
import { getStore } from "@/lib/db";
import type { Arm } from "@/lib/db/types";
import { buildQuotes } from "@/lib/checkoutQuotes";
import { offerDef, type OfferCode } from "@/lib/pricing";
import { getArm, getFoundingOffer } from "@/lib/request";
import { redirectIfPrelaunch } from "@/lib/launchGuard";

export const metadata: Metadata = { title: "Checkout", robots: { index: false } };
export const dynamic = "force-dynamic";

const PAGE_OFFERS: OfferCode[] = ["trial", "founding", "reset", "kitchen"];

export default async function CheckoutPage({ params, searchParams }: { params: Promise<{ offer: string }>; searchParams: Promise<Record<string, string | undefined>> }) {
  const { offer } = await params;
  const sp = await searchParams;
  if (!PAGE_OFFERS.includes(offer as OfferCode)) notFound();
  await redirectIfPrelaunch(sp, { internalCheckout: true });
  const code = offer as OfferCode;
  const qs = new URLSearchParams(Object.entries(sp).filter((e): e is [string, string] => typeof e[1] === "string")).toString();
  // The founding checkout lives at /join. Switched-off offers route there too.
  if (code === "founding" || (code === "trial" && !blitz.trialArmEnabled) || ((code === "reset" || code === "kitchen") && !blitz.frontEndPagesEnabled)) {
    redirect(`/join${qs ? `?${qs}` : ""}`);
  }
  const cookieArm = await getArm();
  const arm: Arm = code === "trial" ? "A" : cookieArm;
  const founding = await getFoundingOffer();
  const gentle = sp.gentle === "1";
  let prefill = { firstName: "", email: "" };
  if (sp.lead) {
    const lead = await (await getStore()).get("leads", sp.lead);
    if (lead) prefill = { firstName: lead.first_name, email: lead.email };
  }
  const { quotes, bumpsAllowed } = buildQuotes({ offer: code, arm, gentle, founding });
  const def = offerDef(code);
  const heading = code === "trial" ? "Start your 7 days of Strong Years for $1" : code === "reset" ? "Get the 7-Day Strength Reset" : "Get Sun Yoon's Strong Kitchen";

  return (
    <div className="narrow py-8">
      {sp.canceled && <p className="mb-6 rounded-xl border-2 border-ink bg-brass p-4 font-bold">No payment was taken. You can try again below, or come back anytime.</p>}
      <h1 className="text-3xl sm:text-4xl">{heading}</h1>
      <ul className="mt-5 space-y-2">
        {def.includes.map((x) => (
          <li key={x} className="flex gap-3">
            <span className="marker !bg-jade" aria-hidden="true" />
            {x}
          </li>
        ))}
        {code !== "trial" && (
          <li className="flex gap-3">
            <span className="marker !bg-jade" aria-hidden="true" />
            {arm === "B" ? "Plus your first month of Strong Years, starting today" : "Plus 7 days of Strong Years"}
          </li>
        )}
      </ul>
      <div className="mt-8">
        <CheckoutForm offer={code} quotes={quotes} bumpsAllowed={bumpsAllowed} bumpVoice={code === "kitchen" ? "sun" : "neutral"} gentle={gentle} leadId={sp.lead ?? null} prefill={prefill} />
      </div>
      <p className="fine mt-10">
        Chang Yin and Sun Yoon are AI characters. Sessions and recipes are built from published guidelines for older adults. General fitness education, not medical advice. On your statement: STRONGYEARS MEMBER.
      </p>
    </div>
  );
}
