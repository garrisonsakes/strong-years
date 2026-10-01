import type { Metadata } from "next";
import { COMMISSION_MONTHS, FTC_LINE, LINK_WINDOW_DAYS, TERMS_VERSION } from "@/lib/affiliates";

export const metadata: Metadata = { title: "Affiliates", description: "Recommend Strong Years and earn 30% of what the people you refer pay for 12 months." };

const ERR: Record<string, string> = {
  email: "Please enter a working email address.",
  name: "Please enter your name.",
  channel: "Please tell us where you'll share Strong Years.",
  ftc: "Please confirm you'll disclose the relationship every time.",
  terms: "Please confirm you've read the terms.",
  rate: "Too many applications from this connection. Please try again in an hour.",
};

export default async function Affiliates({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const errors = (sp.error ?? "").split(",").filter(Boolean);
  return (
    <div className="narrow space-y-8 py-10" data-testid="affiliates">
      <header>
        <h1 className="text-4xl">Recommend Strong Years</h1>
        <p className="mt-3 text-xl">If you know people who would like morning strength sessions with Chang Yin and Sun Yoon&apos;s recipes, you can earn a share of what they pay.</p>
      </header>

      <section className="card space-y-3 text-lg">
        <h2 className="text-2xl">The terms, in plain words</h2>
        <ul className="space-y-2">
          <li><span className="font-bold">30% commission</span> on what each person you refer pays us for {COMMISSION_MONTHS} months from their first order, renewals included. Gifts are excluded.</li>
          <li><span className="font-bold">{LINK_WINDOW_DAYS}-day link window:</span> your link (/go?ref=YOURCODE) credits a purchase made within {LINK_WINDOW_DAYS} days of the click. Your code credits a purchase whenever it is used.</li>
          <li><span className="font-bold">The buyer&apos;s price never changes</span> because of you. Your code carries exactly the public starter terms.</li>
          <li><span className="font-bold">Paid monthly</span> by statement, after the 14-day money-back window. Refunded or disputed charges are reversed.</li>
          <li><span className="font-bold">No self-referrals,</span> no paid ads on our brand names, no coupon sites, no spam, no health claims. Chang Yin and Sun Yoon are AI characters, and you must never say otherwise.</li>
          <li>
            <span className="font-bold">Disclose every time (FTC rules).</span> Put this, or the same meaning in your words, next to every link or code, before any &quot;more&quot; cut: &quot;{FTC_LINE}&quot;
          </li>
        </ul>
        <p>Every application is read by a person. Terms version {TERMS_VERSION} (draft, under legal review).</p>
      </section>

      {sp.sent ? (
        <p className="card text-xl font-bold" role="status" data-testid="affiliate-sent">Thank you. A person on our team will read your application and reply by email, usually within 3 business days.</p>
      ) : (
        <form method="post" action="/api/affiliates/apply" className="card space-y-5" data-testid="affiliate-form">
          {errors.length > 0 && (
            <div role="alert" className="rounded-xl border-2 border-alert bg-rice p-4 text-lg font-bold text-alert">
              {errors.map((e) => (
                <p key={e}>{ERR[e] ?? "Please check the form."}</p>
              ))}
            </div>
          )}
          <label className="block">
            <span className="label">Your name</span>
            <input className="field" name="name" required maxLength={80} autoComplete="name" />
          </label>
          <label className="block">
            <span className="label">Email</span>
            <input className="field" type="email" name="email" required maxLength={254} autoComplete="email" />
          </label>
          <label className="block">
            <span className="label">Where will you share it? (a link or a handle)</span>
            <input className="field" name="channel" required maxLength={200} />
          </label>
          <label className="block">
            <span className="label">Who is your audience? (optional)</span>
            <textarea className="field min-h-[120px]" name="audience" maxLength={600} />
          </label>
          <label className="flex gap-3 text-lg">
            <input className="check" type="checkbox" name="ftc" value="yes" required />
            <span>I will clearly disclose that I earn a commission, every time I share a link or code.</span>
          </label>
          <label className="flex gap-3 text-lg">
            <input className="check" type="checkbox" name="terms" value="yes" required />
            <span>I have read the terms above, including no self-referrals and no health claims.</span>
          </label>
          <button type="submit" className="btn-primary">Apply</button>
        </form>
      )}
    </div>
  );
}
