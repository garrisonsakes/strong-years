import { NextResponse } from "next/server";
import { currentMember } from "@/lib/auth/server";
import { getStore } from "@/lib/db";

/** Removes this device (or, with no endpoint, every device) from push reminders. */
export async function POST(req: Request) {
  const member = await currentMember();
  if (!member) return NextResponse.json({ error: "Please log in." }, { status: 401 });
  let endpoint: string | null = null;
  try {
    const b = (await req.json()) as { endpoint?: unknown };
    endpoint = typeof b.endpoint === "string" ? b.endpoint : null;
  } catch {
    endpoint = null;
  }
  const store = await getStore();
  const n = endpoint ? await store.remove("push_subscriptions", { member_id: member.id, endpoint }) : await store.remove("push_subscriptions", { member_id: member.id });
  return NextResponse.json({ ok: true, removed: n });
}
