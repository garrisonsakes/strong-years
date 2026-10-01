import Link from "next/link";
import { currentMembership, entitlement, requireMember } from "@/lib/auth/server";
import { formatDate } from "@/lib/pricing";
import { getStore } from "@/lib/db";
import { PRINTABLES } from "@/lib/content";
import { entitledDownloads } from "@/lib/products";

/**
 * Downloads are yours-to-keep purchases as much as membership material: a Starter Books
 * buyer with no membership (cell A) signs in and downloads here; membership files need
 * an entitlement that grants access right now (entitledDownloads decides per file).
 */
export default async function Printables() {
  const member = await requireMember();
  const ent = await entitlement(member.id);
  const m = ent.access ? await currentMembership(member.id) : null;
  const orders = await (await getStore()).find("sy_orders", { member_id: member.id });
  const downloads = entitledDownloads(member, m, orders);
  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-4xl">Your downloads</h1>
        <p className="mt-2 text-lg">Large-print PDFs to keep, print, or read on a tablet. Each copy is stamped with your name, email and order number, for your personal use.</p>
        {downloads.length === 0 && <p className="mt-4 rounded-xl border-2 border-ink bg-cream p-4 text-lg font-bold">Nothing to download on this email address yet. If you bought with a different email, sign out and sign in with that one.</p>}
        <div className="mt-6 grid gap-5 md:grid-cols-2" data-testid="downloads">
          {downloads.map((d) => (
            <article key={d.file} className="card">
              <h2 className="text-2xl">{d.title}</h2>
              <p className="mt-2">{d.blurb}</p>
              {d.lockedUntil ? (
                <p className="mt-4 rounded-xl border-2 border-ink bg-cream p-3 font-bold" data-testid="locked-download">
                  Unlocks on {formatDate(d.lockedUntil, member.timezone)}, after your 14-day money-back window. Every session is already in the app today.
                </p>
              ) : (
                <a href={`/api/downloads/${d.file}`} className="btn-jade mt-4" download>
                  Download the PDF
                </a>
              )}
            </article>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-3xl">Print from the app</h2>
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          {PRINTABLES.map((p) => (
            <article key={p.slug} className="card">
              <h3 className="text-2xl">{p.name}</h3>
              <p className="mt-2">{p.blurb}</p>
              <Link href={`/app/printables/${p.slug}`} className="btn-outline mt-4">
                Open and print
              </Link>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
