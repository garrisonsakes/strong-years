import Link from "next/link";
import { copy } from "@/lib/copy";
import { env, mode } from "@/lib/config";
import { isShopify } from "@/lib/billing/provider";

export function DisclosureStrip() {
  return (
    <div className="bg-ink text-rice">
      <p className="wrap py-2 text-fine">
        {copy.strip}{" "}
        <Link href="/how-we-make-this" className="font-bold text-rice underline">
          How we make this
        </Link>
      </p>
    </div>
  );
}

export function DemoBanner() {
  // On the Shopify launch path Stripe is unused, so a missing Stripe key is not "simulated payments" (no banner to real visitors).
  const simulatedPayments = mode.mockStripe && !isShopify();
  if (!mode.mockDb && !simulatedPayments) return null;
  const parts = [mode.mockDb && "data is in-memory demo data (resets on restart)", simulatedPayments && "payments are simulated, no card is charged", mode.mockAi && "coach replies are scripted"].filter(Boolean);
  return (
    <div className="no-print border-b-2 border-ink bg-brass text-ink" role="note">
      <p className="wrap py-2 text-fine font-bold">Demo mode: {parts.join("; ")}.</p>
    </div>
  );
}

export function Logo({ href = "/start", light = false }: { href?: string; light?: boolean }) {
  return (
    <Link href={href} className={`inline-flex items-center gap-3 no-underline ${light ? "text-rice" : "text-ink"}`} aria-label="Strong Years home">
      <svg width="40" height="40" viewBox="0 0 40 40" aria-hidden="true">
        <rect width="40" height="40" rx="10" fill="#1F5A46" />
        <path d="M11 27 L11 17 M29 27 L29 17 M8 22 H32" stroke="#FFFFFF" strokeWidth="3.5" strokeLinecap="round" />
        <circle cx="20" cy="12" r="3" fill="#E7B85A" />
      </svg>
      <span className="font-display text-[26px] leading-none">Strong Years</span>
    </Link>
  );
}

export function SiteHeader() {
  return (
    <header className="border-b-2 border-ink bg-paper">
      <div className="wrap flex min-h-[72px] items-center justify-between gap-4">
        <Logo />
        <nav aria-label="Account" className="flex items-center gap-3">
          <Link href="/login" className="rounded-btn border-2 border-ink bg-rice px-4 py-2 text-[18px] font-bold text-ink no-underline hover:bg-cream">
            Log in
          </Link>
        </nav>
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="mt-16 bg-ink text-rice">
      <div className="wrap space-y-5 py-12">
        <Logo href="/start" light />
        <p className="max-w-prose text-fine text-rice">{copy.footer}</p>
        <nav aria-label="Legal" className="flex flex-wrap gap-x-6 gap-y-3 text-[18px]">
          {[
            ["/terms", "Terms & cancellation"],
            ["/refunds", "Refund policy"],
            ["/privacy", "Privacy"],
            ["/health-data", "Consumer health data"],
            ["/privacy-choices", "Your privacy choices"],
            ["/safety", "Crisis protocol"],
            ["/how-we-make-this", "How we make this"],
            ["/gift", "Give Strong Years"],
            ["/login", "Log in"],
          ].map(([href, label]) => (
            <Link key={href} href={href!} className="font-bold text-rice underline">
              {label}
            </Link>
          ))}
        </nav>
        <p className="text-fine text-rice">
          Contact: <a className="text-rice underline" href={`mailto:${env.supportEmail}`}>{env.supportEmail}</a> · {env.mailingAddress} · On your card statement: STRONGYEARS MEMBER
        </p>
      </div>
    </footer>
  );
}
