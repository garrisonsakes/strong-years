import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { blitz } from "@/lib/config";
import { startCheckout } from "@/lib/billing/checkout";
import { isOfferCode, type BumpKey } from "@/lib/pricing";
import { getArm, getAttribution, getVisitorId, clientMeta } from "@/lib/request";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { currentPurchaser } from "@/lib/auth/server";
import { normalizeEmail } from "@/lib/members";
import type { Arm } from "@/lib/db/types";
import { refuseIfPrelaunch } from "@/lib/launchGuard";

interface Body {
  offer?: string;
  bump?: boolean;
  bumps?: string[];
  gentle?: boolean;
  leadId?: string | null;
  firstName?: string;
  email?: string;
  phone?: string;
  smsConsent?: boolean;
  autoRenewConsent?: boolean;
  ageConsent?: boolean;
  adConsent?: boolean;
  quoteSig?: string;
  gift?: { recipient_name: string; recipient_email: string; message: string; months: number } | null;
}

export async function POST(req: Request) {
  // Organic launch: in prelaunch every checkout API refuses on the server.
  const closed = await refuseIfPrelaunch(req, "json");
  if (closed) return closed;
  if (!(await hit(`checkout:ip:${clientIp(req)}`, LIMITS.checkoutPerIp))) {
    return NextResponse.json({ error: "Too many tries. Please wait a few minutes. Nothing was charged." }, { status: 429 });
  }
  let b: Body;
  try {
    b = (await req.json()) as Body;
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  if (!isOfferCode(b.offer)) return NextResponse.json({ error: "Unknown offer" }, { status: 400 });
  if (b.offer === "trial" && !blitz.trialArmEnabled) return NextResponse.json({ error: "This offer isn't available." }, { status: 400 });
  if ((b.offer === "reset" || b.offer === "kitchen") && !blitz.frontEndPagesEnabled) return NextResponse.json({ error: "This offer isn't available." }, { status: 400 });
  const cookieArm = await getArm();
  const arm: Arm = b.offer === "trial" ? "A" : b.offer === "founding" ? "B" : cookieArm;
  const meta = await clientMeta();
  const store = await getStore();
  const signedIn = (await currentPurchaser())?.member ?? null;
  try {
    const res = await startCheckout(store, {
      offer: b.offer,
      arm,
      bump: Boolean(b.bump),
      bumps: (Array.isArray(b.bumps) ? b.bumps : []).filter((x): x is BumpKey => x === "wallplan" || x === "reset" || x === "kitchen"),
      visitorId: await getVisitorId(),
      gentle: Boolean(b.gentle),
      email: String(b.email ?? ""),
      firstName: String(b.firstName ?? ""),
      phone: String(b.phone ?? ""),
      smsConsent: b.smsConsent === true,
      autoRenewConsent: b.autoRenewConsent === true,
      ageConsent: b.ageConsent === true,
      adConsent: b.adConsent === true,
      quoteSig: String(b.quoteSig ?? ""),
      // NEW-1: only a signed-in session for this same email counts as the account owner.
      authMemberId: signedIn && normalizeEmail(signedIn.email) === normalizeEmail(String(b.email ?? "")) ? signedIn.id : null,
      gift: b.gift
        ? {
            recipient_name: String(b.gift.recipient_name ?? "").slice(0, 60),
            recipient_email: normalizeEmail(String(b.gift.recipient_email ?? "")),
            message: String(b.gift.message ?? "").slice(0, 300),
            months: b.offer === "gift3" ? 3 : 12,
          }
        : null,
      attribution: await getAttribution(),
      leadId: b.leadId ?? null,
      ip: meta.ip,
      userAgent: meta.userAgent,
    });
    if (!res.ok) return NextResponse.json({ errors: res.errors }, { status: 422 });
    return NextResponse.json({ redirectUrl: res.redirectUrl });
  } catch (err) {
    console.error("checkout failed", err);
    return NextResponse.json({ error: "We couldn't start the payment. Nothing was charged. Please try again." }, { status: 500 });
  }
}
