import type { Metadata } from "next";
import { Logo } from "@/components/Chrome";
import { mode, offerRules } from "@/lib/config";
import { getStore } from "@/lib/db";
import { computeKpis } from "@/lib/kpis";
import { moneyExact } from "@/lib/pricing";
import { growthReport, launchKpis } from "@/lib/growth";
import { getLaunchState } from "@/lib/launch";
import { billingProviderId } from "@/lib/billing/provider";

export const metadata: Metadata = { title: "Admin", robots: { index: false } };
export const dynamic = "force-dynamic";

const pct = (v: number | null) => (v === null ? "—" : `${(v * 100).toFixed(1)}%`);

export default async function Admin({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const store = await getStore();
  const launch = await getLaunchState(store);
  const lk = await launchKpis(store);
  const growth = await growthReport(store);
  const hooks = await store.find("shopify_webhooks", {}, { orderBy: "created_at", desc: true, limit: 15 });
  const k = await computeKpis(store);
  const crisis = await store.find("crisis_events", {}, { orderBy: "created_at", desc: true, limit: 50 });
  const tickets = await store.find("support_tickets", { status: "open" }, { orderBy: "created_at", desc: true, limit: 20 });
  const events = await store.find("stripe_events", {}, { orderBy: "created_at", desc: true, limit: 15 });
  const outbox = await store.find("outbox", {}, { orderBy: "created_at", desc: true, limit: 10 });
  const tiles: [string, string, string?][] = [
    ["MRR", moneyExact(k.mrrCents), `Arm A ${moneyExact(k.mrrByArm.A)} · Arm B ${moneyExact(k.mrrByArm.B)} (gifts and scheduled cancellations excluded)`],
    ["Scheduled churn", moneyExact(k.scheduledChurnCents), "MRR that ends at period end (cancelled, still has access)"],
    ["Paying members", String(k.paying), `Active by arm: A ${k.activeByArm.A} · B ${k.activeByArm.B} · gift ${k.activeByArm.gift}`],
    ["Trials running", String(k.trials), `${k.trialConversions} converted · rate ${pct(k.trialConversionRate)}`],
    ["Founding cohort", Number.isFinite(k.cohort.cap) ? `${k.cohort.claimed.toLocaleString("en-US")} / ${k.cohort.cap.toLocaleString("en-US")}` : k.cohort.claimed.toLocaleString("en-US"), Number.isFinite(k.cohort.cap) ? `${k.cohort.left.toLocaleString("en-US")} spots left (real count)` : "no seat cap; closes on the founding close date"],
    ["Churn, 30 days", String(k.churned30d), `rate ${pct(k.churnRate30d)} · paused ${k.paused}`],
    ["Cancel flow, 30 days", `${k.cancelFlowStarts30d} started`, `${k.saves30d} saved by pause/downgrade`],
    ["Refunds", String(k.refunds.count), moneyExact(k.refunds.cents)],
    ["Chargebacks", String(k.chargebacks.count), `30-day ratio ${pct(k.chargebacks.ratio)} (stop scaling at 0.5%)`],
    ["Revenue, 30 days", moneyExact(k.revenue30dCents), `${k.leads} quiz leads total`],
  ];
  return (
    <div className="min-h-screen bg-paper">
      <header className="border-b-2 border-ink">
        <div className="wrap flex min-h-[68px] items-center justify-between">
          <Logo href="/admin" />
          <p className="font-bold">Admin</p>
        </div>
      </header>
      <main id="main" className="wrap space-y-10 py-8" data-testid="admin">
        {mode.anyMock && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold">Demo mode: these numbers include clearly flagged demo rows (is_demo).</p>}
        <nav aria-label="Admin screens" className="flex flex-wrap gap-3 text-lg font-bold">
          <a href="/admin/today" className="rounded-lg border-2 border-ink bg-rice px-3 py-1 text-ink">Today</a>
          <a href="/admin/exceptions" className="rounded-lg border-2 border-ink bg-rice px-3 py-1 text-ink">Exceptions</a>
          <a href={`/api/admin/affiliates/statement?month=${new Date().toISOString().slice(0, 7)}`} className="rounded-lg border-2 border-ink bg-rice px-3 py-1 text-ink">Affiliate statement (CSV)</a>
        </nav>
        <section>
          <h1 className="text-4xl">Today&apos;s numbers</h1>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tiles.map(([label, value, sub]) => (
              <div key={label} className="card">
                <p className="text-lg font-bold">{label}</p>
                <p className="font-display text-4xl">{value}</p>
                {sub && <p className="mt-1 text-[18px]">{sub}</p>}
              </div>
            ))}
          </div>
          <p className="fine mt-3">MRR = active paying memberships × monthly price (annual ÷ 12), partner seats included, prepaid gifts excluded. Founding cap: {offerRules.foundingCapped ? offerRules.foundingCap.toLocaleString("en-US") : "none (closes on the founding close date)"}.</p>
        </section>

        <section id="launch" className="space-y-4">
          <h2 className="text-3xl">Launch and waitlist</h2>
          {sp.launch === "opened" && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status">Checkout is open.</p>}
          {sp.launch === "confirm" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="alert">Type OPEN to confirm.</p>}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="card">
              <p className="text-lg font-bold">Checkout</p>
              <p className="font-display text-3xl" data-testid="launch-state">{launch.live ? "Open" : "Prelaunch"}</p>
              <p className="mt-1 text-[18px]">{launch.live ? `since ${launch.liveSince ? new Date(launch.liveSince).toLocaleString("en-US") : "now"} (${launch.reason.replace(/_/g, " ")})` : launch.opensAt ? `opens ${launch.opensAt.toLocaleString("en-US")}` : "no opening date set"} · billing: {billingProviderId()}</p>
            </div>
            <div className="card">
              <p className="text-lg font-bold">Waitlist (confirmed)</p>
              <p className="font-display text-3xl" data-testid="waitlist-size">{lk.waitlist.confirmed.toLocaleString("en-US")}</p>
              <p className="mt-1 text-[18px]">{lk.waitlist.pending} unconfirmed · {lk.waitlist.unsubscribed} left · {lk.waitlist.withPush} with push · {lk.waitlist.referralRewards} referral rewards</p>
            </div>
            <div className="card">
              <p className="text-lg font-bold">Post-launch conversion</p>
              <p className="font-display text-3xl">{pct(lk.postLaunch.conversion)}</p>
              <p className="mt-1 text-[18px]">{lk.postLaunch.converted} confirmed waitlisters became members</p>
            </div>
            <div className="card">
              <p className="text-lg font-bold">Launch sends</p>
              <p className="font-display text-3xl">{lk.sends.email} emails</p>
              <p className="mt-1 text-[18px]">{lk.sends.push} pushes · ad events: {lk.conversions.sent} sent, {lk.conversions.pending + lk.conversions.failed} queued, {lk.conversions.skipped} skipped</p>
            </div>
          </div>
          {!launch.live && (
            <form action="/api/admin/launch" method="post" className="card flex flex-wrap items-end gap-4">
              <label className="block">
                <span className="label">Open checkout now (type OPEN)</span>
                <input name="confirm" className="field max-w-[220px]" autoComplete="off" />
              </label>
              <button type="submit" className="btn-ink">Open checkout</button>
              <p className="fine w-full">This can&apos;t be undone from here. The launch emails start on the next cron run (every 15 minutes).</p>
            </form>
          )}
          <h3 className="text-2xl">Per post (first touch)</h3>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse bg-rice text-left text-[18px]" data-testid="post-kpis">
              <thead>
                <tr>
                  {["Post", "Platform / page", "Keywords", "Waitlist (confirmed)", "Quiz opt-ins", "Book buyers", "Members", "MRR"].map((h) => (
                    <th key={h} className="border-2 border-ink p-2">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {growth.first_touch.length === 0 && (
                  <tr>
                    <td colSpan={8} className="border-2 border-ink p-3 font-bold">No attributed posts yet.</td>
                  </tr>
                )}
                {growth.first_touch.slice(0, 50).map((r) => (
                  <tr key={r.post_id}>
                    <td className="border-2 border-ink p-2 font-bold">{r.post_id}</td>
                    <td className="border-2 border-ink p-2">{[r.platform, r.page].filter(Boolean).join(" / ")}</td>
                    <td className="border-2 border-ink p-2">{r.keywords.join(", ")}</td>
                    <td className="border-2 border-ink p-2">{r.waitlist_signups} ({r.waitlist_confirmed})</td>
                    <td className="border-2 border-ink p-2">{r.quiz_optins}</td>
                    <td className="border-2 border-ink p-2">{r.ebook_buyers}</td>
                    <td className="border-2 border-ink p-2">{r.members} ({r.paying_members} paying)</td>
                    <td className="border-2 border-ink p-2">{moneyExact(r.mrr_cents)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="fine">Unattributed: {growth.unattributed.waitlist_confirmed} waitlisters, {growth.unattributed.members} members, {moneyExact(growth.unattributed.mrr_cents)} MRR. Demo members are excluded. The same data, first and last touch, is at /api/growth/posts for the growth engine.</p>
        </section>

        <section id="price-test">
          <h2 className="text-3xl">Founding price test</h2>
          <p className="mt-1">Sticky 50/50 by visitor. Pick the winner on MRR added per visitor after refunds, with at least 300 purchases per cell (BLITZ.md).</p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[640px] border-collapse bg-rice text-left text-[18px]" data-testid="price-test-table">
              <thead>
                <tr>
                  {["Cell", "Visitors", "Checkouts started", "Members", "Refunded", "MRR", "Members / visitor", "MRR / visitor"].map((h) => (
                    <th key={h} className="border-2 border-ink p-2">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {k.priceTest.length === 0 && (
                  <tr>
                    <td colSpan={8} className="border-2 border-ink p-3 font-bold">No exposures yet.</td>
                  </tr>
                )}
                {k.priceTest.map((c) => (
                  <tr key={c.cell}>
                    <td className="border-2 border-ink p-2 font-bold">{c.cell}</td>
                    <td className="border-2 border-ink p-2">{c.exposures}</td>
                    <td className="border-2 border-ink p-2">{c.checkouts}</td>
                    <td className="border-2 border-ink p-2">{c.members}</td>
                    <td className="border-2 border-ink p-2">{c.refunded}</td>
                    <td className="border-2 border-ink p-2">{moneyExact(c.mrrCents)}</td>
                    <td className="border-2 border-ink p-2">{pct(c.conversion)}</td>
                    <td className="border-2 border-ink p-2">{c.exposures ? moneyExact(Math.round(c.mrrCents / c.exposures)) : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3">
            Processors (30 days):{" "}
            {k.processors.map((p) => `${p.id} ${moneyExact(p.volume30dCents)} across ${p.orders30d} charges`).join(" · ")}
          </p>
        </section>

        <section id="crisis">
          <h2 className="text-3xl">Crisis and support log ({k.crisisOpen} open)</h2>
          <p className="mt-1">Every crisis message gets fixed referral text, is logged here, and pages the on-call human. Respond within 1 hour during staffed hours. Needed for SB 243 reporting.</p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[720px] border-collapse bg-rice text-left text-[18px]">
              <thead>
                <tr>
                  {["When", "Category", "Detected by", "Excerpt", "Alerted", "Status"].map((h) => (
                    <th key={h} className="border-2 border-ink p-2">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {crisis.length === 0 && (
                  <tr>
                    <td colSpan={6} className="border-2 border-ink p-3 font-bold">No events logged.</td>
                  </tr>
                )}
                {crisis.map((c) => (
                  <tr key={c.id} id={`crisis-${c.id}`}>
                    <td className="border-2 border-ink p-2">{new Date(c.created_at).toLocaleString("en-US")}</td>
                    <td className="border-2 border-ink p-2 font-bold">{c.category.replace("_", " ")}</td>
                    <td className="border-2 border-ink p-2">{c.detected_by}</td>
                    <td className="border-2 border-ink p-2">
                      {c.excerpt}
                      {c.member_cleared_at && <span className="mt-1 block font-bold">Member said &ldquo;That&apos;s not what I meant&rdquo; ({new Date(c.member_cleared_at).toLocaleString("en-US")}). Still follow up.</span>}
                    </td>
                    <td className="border-2 border-ink p-2">{c.alerted ? "Yes" : "No"}</td>
                    <td className="border-2 border-ink p-2">
                      {c.handled_at ? (
                        "Handled"
                      ) : (
                        <form action="/api/admin/crisis" method="post">
                          <input type="hidden" name="id" value={c.id} />
                          <button type="submit" className="rounded-btn border-2 border-ink bg-rice px-3 py-1 font-bold text-ink">Mark handled</button>
                        </form>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section>
          <h2 className="text-3xl">Open tickets (talk to a human, follow-ups)</h2>
          <ul className="mt-3 space-y-2">
            {tickets.length === 0 && <li className="font-bold">None open.</li>}
            {tickets.map((t) => (
              <li key={t.id} id={`ticket-${t.id}`} className="card">
                <p className="font-bold">{t.reason.replace(/_/g, " ")} · {t.email}</p>
                <p>{t.message}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div>
            <h2 className="text-3xl">Shopify webhooks</h2>
            <ul className="mt-3 space-y-1 text-[18px]" data-testid="shopify-webhooks">
              {hooks.length === 0 && <li className="font-bold">None received yet.</li>}
              {hooks.map((h) => (
                <li key={h.id} className="rounded-lg border-2 border-ink bg-rice p-2">
                  <strong>{h.topic}</strong> · {h.status} · {h.summary ?? ""}
                </li>
              ))}
            </ul>
            <h2 className="mt-6 text-3xl">Stripe events</h2>
            <ul className="mt-3 space-y-1 text-[18px]">
              {events.map((e) => (
                <li key={e.id} className="rounded-lg border-2 border-ink bg-rice p-2">
                  <strong>{e.type}</strong> · {e.error ? `ERROR: ${e.error}` : e.summary ?? "pending"}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="text-3xl">Outbox (latest messages)</h2>
            <ul className="mt-3 space-y-1 text-[18px]">
              {outbox.map((o) => (
                <li key={o.id} className="rounded-lg border-2 border-ink bg-rice p-2">
                  <strong>{o.channel}</strong> · {o.template} · {o.to} · {o.status}
                </li>
              ))}
            </ul>
          </div>
        </section>
      </main>
    </div>
  );
}
