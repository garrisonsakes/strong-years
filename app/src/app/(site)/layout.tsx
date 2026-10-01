import { DemoBanner, DisclosureStrip, SiteFooter, SiteHeader } from "@/components/Chrome";

export default function SiteLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <DisclosureStrip />
      <DemoBanner />
      <SiteHeader />
      <main id="main">{children}</main>
      <SiteFooter />
    </>
  );
}
