import type { Metadata } from "next";
import Link from "next/link";
import { DemoBanner, Logo } from "@/components/Chrome";
import { MemberNav } from "@/components/MemberNav";
import { requireMember } from "@/lib/auth/server";

export const metadata: Metadata = { title: "Your Strong Years", robots: { index: false } };
export const dynamic = "force-dynamic";


export default async function MemberLayout({ children }: { children: React.ReactNode }) {
  const member = await requireMember();
  return (
    <>
      <DemoBanner />
      <header className="border-b-2 border-ink bg-paper">
        <div className="wrap flex min-h-[68px] items-center justify-between gap-4">
          <Logo href="/app" />
          <p className="hidden text-[18px] font-bold sm:block">Hello, {member.first_name}</p>
        </div>
        <MemberNav />
      </header>
      <main id="main" className="wrap py-8">
        {children}
      </main>
      <footer className="border-t-2 border-ink bg-ink py-6 text-rice">
        <div className="wrap space-y-2 text-fine text-rice">
          <p>Chang Yin and Sun Yoon are AI characters, not doctors. General fitness and nutrition education, not medical advice. Stop if you feel chest pain, dizziness or sharp pain. In an emergency, call 911.</p>
          <p>
            <Link href="/app/settings" className="font-bold text-rice underline">Settings</Link> ·{" "}
            <Link href="/app/printables" className="font-bold text-rice underline">Printables</Link> ·{" "}
            <Link href="/app/partner" className="font-bold text-rice underline">Partner seat</Link> ·{" "}
            <Link href="/app/chat?human=1" className="font-bold text-rice underline">Talk to a human</Link> ·{" "}
            <Link href="/safety" className="font-bold text-rice underline">Crisis protocol</Link> ·{" "}
            <Link href="/privacy" className="font-bold text-rice underline">Privacy</Link>
          </p>
        </div>
      </footer>
    </>
  );
}
