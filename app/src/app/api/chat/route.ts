import { NextResponse } from "next/server";
import { currentMember, entitlement } from "@/lib/auth/server";
import { env, mode } from "@/lib/config";
import { getStore } from "@/lib/db";
import { handleChatTurn } from "@/lib/ai/chat";
import { LIMITS, hit } from "@/lib/rateLimit";

export async function POST(req: Request) {
  const member = await currentMember();
  if (!member) return NextResponse.json({ error: "Please log in." }, { status: 401 });
  // H2: chat is part of the membership, not of having an account.
  if (!(await entitlement(member.id)).access) {
    return NextResponse.json({ error: "Ask Chang and Ask Sun are part of an active membership. In an emergency, call 911. To talk to someone now, call or text 988." }, { status: 403 });
  }
  // AUDIT_FINAL C2 / Round 7: rules alone catch about 70% of crisis messages they've never
  // seen, so every non-local deploy needs the model. With no key (or an outage) the turn
  // still runs the rules (a crisis is escalated), but nothing else gets a coach reply:
  // handleChatTurn answers with the offline message (988 / 911 / Eldercare / a human).
  if (env.chatRequiresModel && mode.mockAi) console.error("ANTHROPIC_API_KEY missing: coach chat is offline (crisis classifier required)");
  if (!member.age_confirmed_at) return NextResponse.json({ error: "Please confirm you are 18 or older first." }, { status: 403 });
  const len = Number(req.headers.get("content-length") ?? 0);
  if (len > 16_000) return NextResponse.json({ error: "That message is too long." }, { status: 413 });
  let body: { character?: string; text?: string };
  try {
    body = (await req.json()) as { character?: string; text?: string };
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  const text = String(body.text ?? "").trim();
  if (!text) return NextResponse.json({ error: "Type a message first." }, { status: 400 });
  // M5: per-member daily cap and a burst cap. Crisis wording is never rate limited:
  // the limiter runs after the member's words are known to be ordinary.
  const character = body.character === "sun" ? "sun" : "chang";
  const store = await getStore();
  const { keywordClassify } = await import("@/lib/safety/crisis");
  const urgent = keywordClassify(text).category !== null;
  if (!urgent && (!(await hit(`chat:day:${member.id}`, LIMITS.chatPerMember)) || !(await hit(`chat:burst:${member.id}`, LIMITS.chatBurst)))) {
    return NextResponse.json({ error: "You've sent a lot of messages today. Chang and Sun will be back tomorrow. In an emergency, call 911, or call or text 988." }, { status: 429 });
  }
  const res = await handleChatTurn(store, member, character, text);
  const view = (m: typeof res.reply, clearable = false) => ({ id: m.id, role: m.role, content: m.content, safety: m.safety, clearable });
  const clearable = res.safety === "crisis" || res.safety === "support";
  return NextResponse.json({ reply: view(res.reply, clearable), notice: res.notice ? view(res.notice) : null, safety: res.safety, offline: res.safety === "offline" });
}
