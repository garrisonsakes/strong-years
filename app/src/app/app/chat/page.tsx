import { ChatClient } from "@/components/ChatClient";
import { requireEntitled } from "@/lib/auth/server";
import { coverage } from "@/lib/safety/oncall";
import { getStore } from "@/lib/db";
import { CLEAR_WINDOW_MS, disclosureLine } from "@/lib/ai/chat";
import { confirmAdult, talkToHuman } from "../actions";

export default async function Chat({ searchParams }: { searchParams: Promise<{ human?: string; with?: string }> }) {
  const sp = await searchParams;
  const { member } = await requireEntitled();
  const cov = coverage();
  const character = sp.with === "sun" ? "sun" : "chang";
  const store = await getStore();
  const history = (await store.find("chat_messages", { member_id: member.id, character }, { orderBy: "created_at", desc: true, limit: 30 })).reverse();
  // Round 7: resources replies from the last 24 hours the member hasn't answered yet.
  const clearable = new Set(
    (await store.find("crisis_events", { member_id: member.id, member_cleared_at: null }, { orderBy: "created_at", desc: true, limit: 30 }))
      .filter((e) => e.reply_message_id && Date.now() - new Date(e.created_at).getTime() < CLEAR_WINDOW_MS)
      .map((e) => e.reply_message_id!),
  );

  if (!member.age_confirmed_at) {
    return (
      <div className="narrow card space-y-4" data-testid="age-gate">
        <h1 className="text-3xl">Ask Chang &amp; Sun is for adults.</h1>
        <p>Please confirm you are 18 or older to use the coach chat.</p>
        <form action={confirmAdult}>
          <button type="submit" className="btn-primary">I am 18 or older</button>
        </form>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-4xl">Ask {character === "chang" ? "Chang" : "Sun"}</h1>
        <nav aria-label="Choose a coach" className="flex gap-2">
          <a href="/app/chat?with=chang" aria-current={character === "chang" ? "page" : undefined} className={character === "chang" ? "btn-jade" : "btn-outline"}>Chang Yin</a>
          <a href="/app/chat?with=sun" aria-current={character === "sun" ? "page" : undefined} className={character === "sun" ? "btn-jade" : "btn-outline"}>Sun Yoon</a>
        </nav>
      </div>
      <p className="sticky top-0 z-10 rounded-xl border-2 border-ink bg-ink p-4 font-bold text-rice" data-testid="ai-disclosure">
        {disclosureLine(character)} Memory is {member.memory_enabled ? "on (see or delete it in Settings)" : "off"}.
      </p>
      <ChatClient
        character={character}
        firstName={member.first_name}
        initial={history.map((h) => ({ id: h.id, role: h.role, content: h.content, safety: h.safety, clearable: clearable.has(h.id) }))}
        opener={disclosureLine(character)}
      />
      <section id="human" className="card space-y-3">
        <h2 className="text-2xl">Talk to a human</h2>
        {sp.human === "sent" ? (
          <p className="font-bold" role="status">
            Sent. A real person on our team will reply by email within 24 hours{cov.staffedNow ? "" : `. Our team is offline now and back at ${cov.nextStaffed}`}.
          </p>
        ) : (
          <form action={talkToHuman} className="space-y-3">
            <label className="label" htmlFor="message">What would you like help with?</label>
            <textarea id="message" name="message" rows={3} className="field" required />
            <button type="submit" className="btn-ink" data-testid="talk-human">Send to a real person</button>
          </form>
        )}
        <p className="fine">If this is an emergency, call 911. If you are thinking about hurting yourself, call or text 988.</p>
      </section>
    </div>
  );
}
