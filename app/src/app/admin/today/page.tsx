import type { Metadata } from "next";
import { getStore } from "@/lib/db";
import { syncAppExceptions } from "@/lib/exceptions";
import { moneyExact } from "@/lib/pricing";
import { computeToday, type GateCheck, type TodayPost } from "@/lib/today";
import { AdminNav } from "../AdminNav";
import { MonetizationPanel } from "./MonetizationPanel";

export const metadata: Metadata = { title: "Today", robots: { index: false } };
export const dynamic = "force-dynamic";

const pct = (v: number | null) => (v === null ? "No data yet" : `${(v * 100).toFixed(1)}%`);
const num = (v: number | null) => (v === null ? "Not connected" : v.toLocaleString("en-US"));

function Tile({ label, value, sub, testId }: { label: string; value: string; sub?: string; testId?: string }) {
  return (
    <div className="card" data-testid={testId}>
      <p className="text-lg font-bold">{label}</p>
      <p className="font-display text-4xl">{value}</p>
      {sub && <p className="mt-1 text-[18px]">{sub}</p>}
    </div>
  );
}

function Posts({ title, rows, testId, empty }: { title: string; rows: TodayPost[]; testId: string; empty: string }) {
  return (
    <section data-testid={testId}>
      <h2 className="text-3xl">{title}</h2>
      {rows.length === 0 ? (
        <p className="card mt-4 text-lg">{empty}</p>
      ) : (
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[720px] border-2 border-ink bg-rice text-left text-[18px]">
            <thead className="bg-ink text-rice">
              <tr>
                {["Post", "Page", "Views 24 h", "Score", "Waitlist", "Books", "Members", "MRR"].map((h) => (
                  <th key={h} className="px-3 py-2">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((p) => (
                <tr key={p.post_id} className="border-t-2 border-ink">
                  <td className="px-3 py-2 font-bold">{p.post_id}</td>
                  <td className="px-3 py-2">{p.page ?? "unknown"}</td>
                  <td className="px-3 py-2">{p.views_24h === null ? "no data" : p.views_24h.toLocaleString("en-US")}</td>
                  <td className="px-3 py-2">{p.score === null ? "no data" : `${p.score.toFixed(2)}${p.class ? ` (${p.class})` : ""}`}</td>
                  <td className="px-3 py-2">{p.waitlist_confirmed}</td>
                  <td className="px-3 py-2">{p.ebook_buyers}</td>
                  <td className="px-3 py-2">{p.members}</td>
                  <td className="px-3 py-2">{moneyExact(p.mrr_cents)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function Gates({ title, rows }: { title: string; rows: GateCheck[] }) {
  return (
    <div className="card">
      <p className="text-xl font-bold">{title}</p>
      <ul className="mt-3 space-y-2 text-[18px]">
        {rows.map((g) => (
          <li key={g.name} className="flex flex-wrap gap-2">
            <span className={`rounded px-2 font-bold ${/pass|SCALE|true/i.test(g.status) ? "bg-jade text-rice" : /STOP|CUT|fail|false/i.test(g.status) ? "bg-alert text-rice" : "bg-brass text-ink"}`}>{g.status}</span>
            <span className="font-bold">{g.name}</span>
            <span>
              {g.value === null ? "no data" : g.value}
              {g.line !== null && g.line !== undefined ? ` (line ${g.line})` : ""}
              {g.why ? `: ${g.why}` : ""}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default async function TodayPage() {
  const store = await getStore();
  await syncAppExceptions(store);
  const t = await computeToday(store);
  const g = t.workers.governor;
  return (
    <div className="min-h-screen bg-paper">
      <AdminNav current="today" />
      <main id="main" className="wrap space-y-10 py-8" data-testid="admin-today">
        <section>
          <h1 className="text-4xl">Today</h1>
          <p className="mt-2 text-lg">Generated {new Date(t.generated_at).toUTCString()}. Money and members from our tables; reach and the governor from the workers.</p>
          {t.openExceptions > 0 && (
            <p className="mt-4 rounded-xl border-2 border-ink bg-brass p-4 text-lg font-bold">
              {t.openExceptions} open exception{t.openExceptions === 1 ? "" : "s"} waiting. <a href="/admin/exceptions" className="underline">Decide them</a>.
            </p>
          )}
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Tile testId="t-reach" label="Reach, 24 hours" value={num(t.reach_24h)} sub={t.workers.connected ? "Views across every page and platform" : t.workers.error ?? undefined} />
            <Tile testId="t-waitlist" label="Waitlist (confirmed)" value={t.waitlist.confirmed.toLocaleString("en-US")} sub={`${t.waitlist.new24h} new in 24 hours`} />
            <Tile testId="t-buyers" label="Book buyers" value={t.buyers.books.toLocaleString("en-US")} sub={`${t.buyers.new24h} new in 24 hours`} />
            <Tile testId="t-members" label="Paying members" value={t.members.paying.toLocaleString("en-US")} sub={`${t.members.new24h} new in 24 hours`} />
            <Tile testId="t-mrr" label="MRR" value={moneyExact(t.mrr.total)} sub={`30 days: new ${moneyExact(t.mrr.new30d)} · lost ${moneyExact(t.mrr.lost30d)} · net ${moneyExact(t.mrr.net30d)}`} />
            <Tile testId="t-renewal1" label="Renewal 1" value={pct(t.renewal1.rate)} sub={t.renewal1.due ? `${t.renewal1.renewed} of ${t.renewal1.due} first renewals paid` : "No first renewals due yet"} />
            <Tile testId="t-refunds" label="Refunds, 30 days" value={String(t.refunds.count30d)} sub={`${moneyExact(t.refunds.cents30d)} · rate ${pct(t.refunds.rate30d)}`} />
            <Tile testId="t-chargebacks" label="Chargebacks, 30 days" value={String(t.chargebacks.count30d)} sub={`ratio ${pct(t.chargebacks.ratio30d)} (stop at 0.5%)`} />
            <Tile testId="t-founding" label="Founding seats" value={`${t.founding.claimed.toLocaleString("en-US")} / ${t.founding.cap.toLocaleString("en-US")}`} sub={`${t.founding.left.toLocaleString("en-US")} left (real count)`} />
          </div>
        </section>

        <MonetizationPanel />

        <Posts title="Top 10 posts" rows={t.top} testId="top-posts" empty="No attributed posts yet. Posts show here once a waitlist sign-up, book buyer or member carries a post id." />
        <Posts title="Weakest 10 posts" rows={t.weakest} testId="weak-posts" empty="Fewer than 11 posts with data, so there is no bottom 10 yet." />

        <section data-testid="governor">
          <h2 className="text-3xl">Spend governor</h2>
          {!g ? (
            <p className="card mt-4 text-lg">{t.workers.error ?? "The governor has not planned yet."} No spend happens without the governor, SPEND_ENABLED=1 and a named human approval.</p>
          ) : (
            <div className="mt-4 space-y-4">
              <div className="card text-lg">
                <p>
                  <span className="font-bold">Status:</span> {g.status} · <span className="font-bold">Mode:</span> {g.mode} · <span className="font-bold">Spend switch:</span> {g.spend_enabled ? "on" : "off"} · <span className="font-bold">Planned today:</span> ${g.planned_daily_usd.toFixed(2)}
                </p>
                <p className="mt-1">Last plan: {g.decided_at ? new Date(g.decided_at).toUTCString() : "none"}</p>
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <Gates title="BLITZ §9 rules (the lines)" rows={g.blitz9} />
                {g.graduation ? <Gates title={`BLITZ §11 graduation gate: ${g.graduation.passed ? "PASSED" : "not passed"}`} rows={g.graduation.checks} /> : <p className="card text-lg">§11 graduation gate: no data yet.</p>}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
