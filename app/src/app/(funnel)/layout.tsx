import { DemoBanner, DisclosureStrip, Logo } from "@/components/Chrome";

/** Minimal chrome for quiz and checkout pages: no navigation, one job per page. */
export default function FunnelLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <DisclosureStrip />
      <DemoBanner />
      <header className="border-b-2 border-ink bg-paper">
        <div className="wrap flex min-h-[64px] items-center">
          <Logo />
        </div>
      </header>
      <main id="main" className="pb-16">
        {children}
      </main>
    </>
  );
}
