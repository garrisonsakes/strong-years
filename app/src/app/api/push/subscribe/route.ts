import { NextResponse } from "next/server";
import { currentMember, entitlement } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { parseSubscription, saveSubscription, vapid } from "@/lib/push";
import { LIMITS, hit } from "@/lib/rateLimit";

/** Stores this device's push subscription for the signed-in, entitled member. */
export async function POST(req: Request) {
  const member = await currentMember();
  if (!member) return NextResponse.json({ error: "Please log in." }, { status: 401 });
  if (!(await entitlement(member.id)).access) return NextResponse.json({ error: "Reminders are part of an active membership." }, { status: 403 });
  if (!vapid().configured) return NextResponse.json({ error: "Reminders on this device aren't switched on yet." }, { status: 503 });
  if (!(await hit(`push:${member.id}`, LIMITS.chatBurst))) return NextResponse.json({ error: "Too many tries." }, { status: 429 });
  const raw = await req.text();
  if (raw.length > 4096) return NextResponse.json({ error: "Bad request" }, { status: 413 });
  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  const sub = parseSubscription(body as Parameters<typeof parseSubscription>[0]);
  if (!sub) return NextResponse.json({ error: "That subscription doesn't look right." }, { status: 400 });
  await saveSubscription(await getStore(), member.id, sub, req.headers.get("user-agent"));
  return NextResponse.json({ ok: true });
}
