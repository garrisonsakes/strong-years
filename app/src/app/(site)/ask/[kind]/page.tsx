import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ASK_COPY, ASK_KINDS, type AskKind } from "@/lib/offers/ask";

export const metadata: Metadata = { title: "Ask us", robots: { index: false } };
export const dynamic = "force-dynamic";

const ERRORS: Record<string, string> = {
  email: "Please check your email address.",
  first_name: "Please add your first name.",
  seats: "Group rates start at 5 people. For fewer, a gift is the simplest way.",
  busy: "We've had a lot of requests from this connection. Please try again in an hour.",
  form: "Something went wrong sending the form. Please try again.",
};

/** /ask/group and /ask/price: human-handled requests (MONETIZATION_ENGINE.md §3). Plain form, no JavaScript needed. */
export default async function Ask({ params, searchParams }: { params: Promise<{ kind: string }>; searchParams: Promise<Record<string, string | undefined>> }) {
  const { kind } = await params;
  const sp = await searchParams;
  if (!(ASK_KINDS as readonly string[]).includes(kind)) notFound();
  const c = ASK_COPY[kind as AskKind];
  return (
    <div className="narrow space-y-6 py-8" data-testid={`ask-${kind}`}>
      <h1 className="text-4xl">{c.title}</h1>
      <p className="text-xl">{c.intro}</p>
      {sp.sent ? (
        <p className="card text-xl font-bold" data-testid="ask-sent">Thank you. {c.reply}</p>
      ) : (
        <form method="post" action="/api/offers/ask" className="card space-y-5">
          <input type="hidden" name="kind" value={kind} />
          {sp.error && <p className="rounded-xl border-2 border-ink bg-brass p-3 text-lg font-bold" role="alert">{ERRORS[sp.error] ?? ERRORS.form}</p>}
          <div>
            <label className="label" htmlFor="first_name">Your first name</label>
            <input id="first_name" name="first_name" className="field" required maxLength={60} autoComplete="given-name" />
          </div>
          <div>
            <label className="label" htmlFor="email">Your email (we reply here)</label>
            <input id="email" name="email" type="email" className="field" required autoComplete="email" />
          </div>
          {kind === "group" && (
            <div>
              <label className="label" htmlFor="seats">How many people?</label>
              <input id="seats" name="seats" type="number" min={5} max={500} defaultValue={5} className="field" required inputMode="numeric" />
            </div>
          )}
          <div>
            <label className="label" htmlFor="message">{c.messageLabel}</label>
            <textarea id="message" name="message" className="field min-h-[120px]" maxLength={1000} />
          </div>
          <button type="submit" className="btn-primary">Send to a person</button>
          <p className="text-lg">Chang Yin and Sun Yoon are AI characters. A real person on our team reads this.</p>
        </form>
      )}
      <p className="text-lg">
        Day 1 is free for everyone: <Link href="/start" className="font-bold underline">start Day 1</Link>.
      </p>
    </div>
  );
}
