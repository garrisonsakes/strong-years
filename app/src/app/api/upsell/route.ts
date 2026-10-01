import { NextResponse } from "next/server";
import { currentPurchaser } from "@/lib/auth/server";
import { chargeUpsell, type UpsellKey } from "@/lib/billing/actions";
import { getStore } from "@/lib/db";
import { PROGRAMS } from "@/lib/pricing";
import { refuseIfPrelaunch } from "@/lib/launchGuard";

const NEXT: Record<UpsellKey, { yes: string; no: string }> = {
  program: { yes: "/upsell/kit", no: "/upsell/printables" },
  printables: { yes: "/upsell/kit", no: "/upsell/kit" },
  kit: { yes: "/welcome", no: "/welcome" },
};

export async function POST(req: Request) {
  const closed = await refuseIfPrelaunch(req, "redirect");
  if (closed) return closed;
  const base = new URL(req.url).origin;
  // R2-1: the upsell ladder is part of finishing a purchase, so a checkout session is enough.
  const member = (await currentPurchaser())?.member;
  if (!member) return NextResponse.redirect(`${base}/login`, 303);
  const form = await req.formData();
  const key = String(form.get("key") ?? "") as UpsellKey;
  const flow = String(form.get("flow") ?? "");
  if (!(key in NEXT)) return NextResponse.redirect(`${base}/welcome`, 303);
  const after = flow === "gift" && key === "kit" ? "/gift/thanks" : NEXT[key].yes;
  let detail: string | null = null;
  if (key === "program") {
    const slug = String(form.get("program") ?? "");
    const program = PROGRAMS.find((p) => p.slug === slug);
    if (!program) return NextResponse.redirect(`${base}/upsell/program?error=choose`, 303);
    detail = program.slug;
  }
  const res = await chargeUpsell(await getStore(), member, key, detail);
  if (!res.ok) return NextResponse.redirect(`${base}/upsell/${key}?error=charge${flow ? `&flow=${flow}` : ""}`, 303);
  return NextResponse.redirect(`${base}${after}${flow && after !== "/gift/thanks" ? `?flow=${flow}` : ""}`, 303);
}
