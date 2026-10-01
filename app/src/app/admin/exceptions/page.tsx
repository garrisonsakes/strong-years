import type { Metadata } from "next";
import { getStore } from "@/lib/db";
import { actionsFor, openExceptions, syncAppExceptions, TYPE_LABEL } from "@/lib/exceptions";
import { AdminNav } from "../AdminNav";

export const metadata: Metadata = { title: "Exceptions", robots: { index: false } };
export const dynamic = "force-dynamic";

const BUTTON: Record<string, string> = { approve: "btn-jade", reject: "btn-primary", resolve: "btn-ink" };

export default async function ExceptionsPage({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const store = await getStore();
  await syncAppExceptions(store);
  const open = await openExceptions(store);
  const decided = (await store.find("exceptions", { status: { neq: "open" } }, { orderBy: "decided_at", desc: true, limit: 30 })) ?? [];
  const events = await store.find("exception_events", {}, { orderBy: "created_at", desc: true, limit: 40 });
  return (
    <div className="min-h-screen bg-paper">
      <AdminNav current="exceptions" />
      <main id="main" className="wrap space-y-10 py-8" data-testid="admin-exceptions">
        <section>
          <h1 className="text-4xl">Exceptions</h1>
          <p className="mt-2 text-lg">Everything a person must decide. Each decision is recorded with your admin name and cannot be edited afterwards.</p>
          {sp.done && <p className="mt-4 rounded-xl border-2 border-ink bg-jade-light p-4 text-lg font-bold" role="status">Recorded: {sp.done}.</p>}
          {sp.error && <p className="mt-4 rounded-xl border-2 border-ink bg-brass p-4 text-lg font-bold" role="alert">Not recorded: {sp.error.replace(/_/g, " ")}.</p>}
        </section>

        <section data-testid="open-exceptions">
          <h2 className="text-3xl">Open ({open.length})</h2>
          {open.length === 0 ? (
            <p className="card mt-4 text-lg">Nothing waiting. New items arrive from the workers and from billing, crisis and affiliate reviews.</p>
          ) : (
            <ul className="mt-4 space-y-4">
              {open.map((x) => (
                <li key={x.id} className="card" data-testid="exception" data-type={x.type}>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`rounded px-2 font-bold ${x.severity === "critical" ? "bg-alert text-rice" : x.severity === "high" ? "bg-persimmon text-rice" : "bg-cream text-ink"}`}>{x.severity}</span>
                    <span className="font-bold">{TYPE_LABEL[x.type]}</span>
                    <span>from {x.source} · {new Date(x.created_at).toUTCString()}</span>
                  </div>
                  <p className="mt-2 text-xl font-bold">{x.title}</p>
                  {x.detail && <p className="mt-2 whitespace-pre-wrap text-[18px]">{x.detail}</p>}
                  {x.ref && <p className="mt-1 text-[18px]">Ref: {x.ref}</p>}
                  <form method="post" action="/api/admin/exceptions" className="mt-4 space-y-3">
                    <input type="hidden" name="id" value={x.id} />
                    {x.type === "boost_approval" && (
                      <label className="block">
                        <span className="label">Approved daily ceiling, USD (at most the requested {String((x.payload as { requested_daily_usd?: number }).requested_daily_usd ?? "?")})</span>
                        <input className="field max-w-xs" name="max_daily_usd" inputMode="decimal" defaultValue={String((x.payload as { requested_daily_usd?: number }).requested_daily_usd ?? "")} />
                      </label>
                    )}
                    <label className="block">
                      <span className="label">Note (optional)</span>
                      <input className="field" name="note" maxLength={1000} />
                    </label>
                    <div className="flex flex-wrap gap-3">
                      {actionsFor(x.type).map((a) => (
                        <button key={a} type="submit" name="decision" value={a} className={BUTTON[a]}>
                          {a[0]!.toUpperCase() + a.slice(1)}
                        </button>
                      ))}
                    </div>
                  </form>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <h2 className="text-3xl">Recently decided</h2>
          {decided.length === 0 ? (
            <p className="card mt-4 text-lg">No decisions yet.</p>
          ) : (
            <ul className="mt-4 space-y-2 text-[18px]">
              {decided.map((x) => (
                <li key={x.id} className="card">
                  <span className="font-bold">{x.status}</span> by {x.decided_by} · {TYPE_LABEL[x.type]} · {x.title}
                  {x.decision_note ? ` · "${x.decision_note}"` : ""}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <h2 className="text-3xl">Audit trail</h2>
          {events.length === 0 ? (
            <p className="card mt-4 text-lg">No events yet.</p>
          ) : (
            <ul className="mt-4 space-y-1 text-[18px]">
              {events.map((e) => (
                <li key={e.id}>
                  {new Date(e.created_at).toUTCString()} · <span className="font-bold">{e.action}</span> by {e.actor} · item {e.exception_id.slice(0, 8)}
                  {e.note ? ` · ${e.note}` : ""}
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}
