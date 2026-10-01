import type { Metadata } from "next";
import { FrontEndPage } from "@/components/FrontEndPage";
import { redirect } from "next/navigation";
import { blitz } from "@/lib/config";
import { getArm, getFoundingOffer } from "@/lib/request";

export const metadata: Metadata = { title: "7-Day Strength Reset" };
export const dynamic = "force-dynamic";

export default async function Page({ searchParams }: { searchParams: Promise<{ lead?: string }> }) {
  const { lead } = await searchParams;
  // Blitz: the product is an order bump on /join; the standalone page is off by default.
  if (!blitz.frontEndPagesEnabled) redirect(`/join${lead ? `?lead=${lead}` : ""}`);
  return <FrontEndPage kind="reset" arm={await getArm()} leadId={lead} offer={await getFoundingOffer()} />;
}
