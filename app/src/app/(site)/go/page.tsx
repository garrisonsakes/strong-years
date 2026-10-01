import { cleanRef } from "@/lib/affiliates";
import type { Metadata } from "next";
import Link from "next/link";
import { CharacterArt } from "@/components/Art";
import { getStore } from "@/lib/db";
import { getLaunchState } from "@/lib/launch";
import { money } from "@/lib/pricing";
import { waitlistFacts } from "@/lib/waitlistView";
import { getShopCta } from "@/lib/shopCheckout";
import { cleanPageParam, goTiles, type GoFacts } from "@/lib/bioLinks";

export const metadata: Metadata = {
  title: "Strong Years links",
  description: "Everything from the Chang Yin and Sun Yoon pages in one place: the free waitlist, Day 1 free, the Strength Age test and the starter books.",
};
export const dynamic = "force-dynamic";

/**
 * /go (and /tt): the bio-link hub, one page with two modes (ORGANIC_ENGINE.md §3.2).
 * Runway (prelaunch): the free waitlist first. Launch: the starter books first.
 * "p" says which page the person came from and becomes attribution for everything
 * they tap. No countdown here but the real one, no counts that aren't real.
 */
export default async function Go({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const page = cleanPageParam(sp.p ?? sp.page);
  const store = await getStore();
  const state = await getLaunchState(store);
  const f = await waitlistFacts();
  const cta = state.live ? await getShopCta() : null;
  const facts: GoFacts = {
    mode: state.live ? "launch" : "runway",
    frontEndToday: cta ? money(cta.todayCents) : null,
    memberPrice: money(f.memberCents),
    cohortOpen: f.cohortOpen,
    page,
  };
  const q = new URLSearchParams();
  if (page) q.set("page", page);
  for (const k of ["platform", "utm_source", "utm_medium", "utm_campaign", "post_id", "character"] as const) {
    const v = sp[k];
    if (typeof v === "string" && v.length <= 200) q.set(k, v);
  }
  // Affiliate links: /go?ref=CODE → utm_source=affiliate, utm_campaign=CODE on every tile (credited at orders/paid within 60 days).
  const ref = cleanRef(sp.ref);
  if (ref) {
    q.set("ref", ref);
    q.set("utm_source", "affiliate");
    q.set("utm_campaign", ref);
  }
  if (!q.get("platform")) q.set("platform", page?.startsWith("yt-") ? "yt" : page?.startsWith("tt-") ? "tt" : page?.startsWith("fb-") ? "fb" : "ig");
  if (!q.get("utm_medium")) q.set("utm_medium", "bio");
  const tiles = goTiles(facts, q.toString());
  const sun = (page ?? "").includes("sunyoon");

  return (
    <div className="narrow space-y-8 py-8" data-testid="go" data-mode={facts.mode}>
      <header className="flex items-center gap-4">
        <CharacterArt who={sun ? "sun" : "chang"} className="w-20 shrink-0" />
        <div>
          <h1 className="text-3xl sm:text-4xl">{sun ? "Sun Yoon's links" : "Chang Yin's links"}</h1>
          <p className="mt-1 text-lg">Chang Yin and Sun Yoon are AI characters made by a team of real people. The practices and recipes are real.</p>
        </div>
      </header>
      {ref && <p className="rounded-xl border-2 border-ink bg-cream p-4 text-lg" data-testid="go-affiliate">You came from a partner&apos;s link. They earn a commission if you buy; your price is the same.</p>}
      <ul className="grid gap-4">
        {tiles.map((t) => (
          <li key={t.testId}>
            <Link href={t.href} className={`${t.primary ? "btn" : "btn-outline"} block w-full text-left`} data-testid={t.testId}>
              <span className="block text-xl font-bold">{t.title}</span>
              <span className="block text-base font-normal">{t.note}</span>
            </Link>
          </li>
        ))}
      </ul>
      {facts.mode === "runway" && state.opensAt && (
        <p className="text-lg font-bold" data-testid="go-opens">Checkout opens {state.opensAt.toLocaleDateString("en-US", { month: "long", day: "numeric" })}. The waitlist is free and gets the first email.</p>
      )}
      {facts.mode === "launch" && (
        <p className="text-base">
          Membership is {facts.memberPrice} a month, renewing until you cancel, cancel online anytime. The full terms are on the product page before you pay. Giving it to a parent? Gifts are prepaid and never renew.
        </p>
      )}
      <p className="text-base">
        Questions? <Link href="/safety">Safety and who runs this</Link> · <Link href="/how-we-make-this">How we make this</Link>
      </p>
    </div>
  );
}
