import { requireMember } from "@/lib/auth/server";
import { PushOptIn } from "@/components/PushOptIn";
import { vapid } from "@/lib/push";
import { getStore } from "@/lib/db";
import { SMS_CONSENT_TEXT } from "@/lib/pricing";
import { deleteMemory, saveSettings, setMemory } from "../actions";

export default async function Settings({ searchParams }: { searchParams: Promise<{ saved?: string; deleted?: string; error?: string }> }) {
  const sp = await searchParams;
  const member = await requireMember();
  const memory = await (await getStore()).find("memory_items", { member_id: member.id });
  return (
    <div className="narrow space-y-8" data-testid="settings">
      <h1 className="text-4xl">Settings</h1>
      {sp.saved && <p className="rounded-xl border-2 border-ink bg-jade-light p-4 font-bold" role="status">Saved.</p>}
      {sp.error === "phone" && <p className="rounded-xl border-2 border-ink bg-brass p-4 font-bold" role="alert">Please add a mobile number to get texts.</p>}

      <PushOptIn vapidPublicKey={vapid().publicKey} variant="settings" />

      <form action={saveSettings} className="card space-y-4">
        <h2 className="text-2xl">Your daily reminder</h2>
        <label className="label" htmlFor="reminder_time">When do you have your morning tea?</label>
        <input id="reminder_time" name="reminder_time" type="time" defaultValue={member.reminder_time} className="field max-w-[220px]" />
        <label className="label" htmlFor="reminder_channel">Send it by</label>
        <select id="reminder_channel" name="reminder_channel" defaultValue={member.reminder_channel} className="field max-w-[280px]">
          <option value="sms">Text message</option>
          <option value="email">Email</option>
        </select>
        <label className="flex items-start gap-3 rounded-xl border-2 border-ink p-4">
          <input type="checkbox" name="sms_opt_in" defaultChecked={member.sms_opt_in} className="check" />
          <span className="text-[18px]">{SMS_CONSENT_TEXT}</span>
        </label>
        <label className="label" htmlFor="phone">Mobile number</label>
        <input id="phone" name="phone" type="tel" defaultValue={member.phone ?? ""} className="field" />
        <p className="fine">Texts go out between 8am and 9pm your time. Reply STOP to any text to stop them.</p>
        <button type="submit" className="btn-jade">Save reminder settings</button>
      </form>

      <section id="memory" className="card space-y-4">
        <h2 className="text-2xl">What Chang and Sun remember</h2>
        <p>Memory is off unless you turn it on. When it&apos;s on, the coach chat can remember things you tell it (your level, sore spots, your grandkids&apos; names) so it can help you better. It&apos;s never shared with advertisers. You can delete any of it, anytime.</p>
        <form action={setMemory} className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label className="flex items-start gap-3">
            <input type="checkbox" name="memory" defaultChecked={member.memory_enabled} className="check" data-testid="memory-toggle" />
            <span className="font-bold">Let Ask Chang and Ask Sun remember what I tell them.</span>
          </label>
          <button type="submit" className="btn-outline">Save</button>
        </form>
        {sp.deleted && <p className="rounded-xl border-2 border-ink bg-jade-light p-3 font-bold" role="status">Deleted.</p>}
        {memory.length === 0 ? (
          <p className="font-bold">Nothing is remembered right now.</p>
        ) : (
          <>
            <ul className="space-y-2" data-testid="memory-list">
              {memory.map((m) => (
                <li key={m.id} className="flex items-center justify-between gap-3 rounded-xl border-2 border-ink p-3">
                  <span>
                    {m.fact}
                    {m.sensitive && <span className="ml-2 rounded-full bg-ink px-2 py-0.5 text-[15px] font-bold text-rice">health detail</span>}
                  </span>
                  <form action={deleteMemory}>
                    <input type="hidden" name="id" value={m.id} />
                    <button type="submit" className="rounded-btn border-2 border-ink bg-rice px-4 py-2 font-bold text-ink hover:bg-cream">Delete</button>
                  </form>
                </li>
              ))}
            </ul>
            <form action={deleteMemory}>
              <input type="hidden" name="id" value="all" />
              <button type="submit" className="btn-outline">Delete everything it remembers</button>
            </form>
          </>
        )}
      </section>

      <section className="card space-y-3">
        <h2 className="text-2xl">Account</h2>
        <p>Signed in as {member.email}.</p>
        <form action="/api/auth/logout" method="post">
          <button type="submit" className="btn-outline">Log out</button>
        </form>
      </section>
    </div>
  );
}
