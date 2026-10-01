import { billingMembership, requireEntitled } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { formatDate, moneyExact } from "@/lib/pricing";
import { env, prices } from "@/lib/config";
import { addPartner, removePartner } from "../actions";

const ERR: Record<string, string> = {
  plan: "Partner seats are added to a monthly membership. Gift memberships can't add a partner yet.",
  consent: "Please tick the box to agree to the added monthly charge.",
  details: "Please add your partner's first name and email.",
};

export default async function Partner({ searchParams }: { searchParams: Promise<{ error?: string; added?: string; removed?: string }> }) {
  const sp = await searchParams;
  const { member } = await requireEntitled();
  const m = await billingMembership(member.id);
  const partner = await (await getStore()).findOne("partners", { owner_member_id: member.id, status: "active" });
  const next = m?.current_period_end ? formatDate(m.current_period_end, env.displayTimeZone) : "your next charge date";
  return (
    <div className="narrow space-y-6" data-testid="partner">
      <h1 className="text-4xl">Doing it together?</h1>
      <p className="text-lg">Add your partner for {moneyExact(prices.partner)} a month. They get their own level, their own Strength Age and their own progress.</p>
      {sp.error && <p role="alert" className="rounded-xl border-2 border-ink bg-brass p-4 font-bold">{ERR[sp.error] ?? "Something went wrong."}</p>}
      {sp.added && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold">Added. We&apos;ve emailed them a welcome from Sun Yoon.</p>}
      {sp.removed && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold">Partner seat removed. No more partner charges.</p>}
      {partner ? (
        <div className="card">
          <p className="text-xl font-bold">{partner.partner_name} ({partner.partner_email})</p>
          <p className="mt-2">{moneyExact(prices.partner)}/month is added to your membership charge until you remove the seat.</p>
          <form action={removePartner} className="mt-4">
            <button type="submit" className="btn-outline">Remove partner seat</button>
          </form>
        </div>
      ) : (
        <form action={addPartner} className="card space-y-4">
          <div>
            <label className="label" htmlFor="name">Partner&apos;s first name</label>
            <input id="name" name="name" className="field" required />
          </div>
          <div>
            <label className="label" htmlFor="email">Partner&apos;s email</label>
            <input id="email" name="email" type="email" className="field" required />
          </div>
          <label className="flex items-start gap-3"><input type="checkbox" name="share" className="check" /> <span>Let us see each other&apos;s weekly ticks (optional).</span></label>
          <div className="rounded-xl border-[3px] border-ink bg-rice p-4 text-[20px] font-bold">
            Adds {moneyExact(prices.partner)} a month to your membership, starting {next}, renewing monthly until you remove the seat or cancel. Remove it anytime on this page.
          </div>
          <label className="flex items-start gap-3 rounded-xl border-2 border-ink p-4">
            <input type="checkbox" name="consent" className="check" />
            <span className="font-bold">I agree to add {moneyExact(prices.partner)}/month to my membership until I remove the seat or cancel.</span>
          </label>
          <button type="submit" className="btn-primary">Add my partner for {moneyExact(prices.partner)}/month</button>
        </form>
      )}
    </div>
  );
}
