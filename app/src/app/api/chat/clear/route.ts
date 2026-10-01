import { NextResponse } from "next/server";
import { currentMember, entitlement } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { clearCrisisFlag } from "@/lib/ai/chat";

/**
 * Round 7: "That's not what I meant", tapped under a resources reply. The alert and
 * crisis log stay; the member's message is un-flagged and the coach answers it
 * (unless the model is confident it is a crisis, or the chat is offline).
 */
export async function POST(req: Request) {
  const member = await currentMember();
  if (!member) return NextResponse.json({ error: "Please log in." }, { status: 401 });
  if (!(await entitlement(member.id)).access) return NextResponse.json({ error: "In an emergency, call 911. To talk to someone now, call or text 988." }, { status: 403 });
  let body: { messageId?: unknown };
  try {
    body = (await req.json()) as { messageId?: unknown };
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  const res = await clearCrisisFlag(await getStore(), member, String(body.messageId ?? "").slice(0, 64));
  if (!res.ok) {
    const error = res.reason === "already_cleared" ? "Already noted. You can keep chatting." : res.reason === "expired" ? "That was a while ago. Just send a new message." : "We couldn't find that message.";
    return NextResponse.json({ error, reason: res.reason }, { status: res.reason === "not_found" ? 404 : 409 });
  }
  const m = res.reply;
  return NextResponse.json({ reply: { id: m.id, role: m.role, content: m.content, safety: m.safety, clearable: false }, safety: res.safety, offline: res.safety === "offline" });
}
