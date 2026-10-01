import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { parseSubscription, vapid } from "@/lib/push";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { clientMeta } from "@/lib/request";
import { saveWaitlistPush } from "@/lib/waitlist";
import { verifyAccess } from "@/lib/waitlistTokens";

export const runtime = "nodejs";

/** A confirmed waitlister turns on the launch notification for this device (explicit tap + browser prompt). */
export async function POST(req: Request) {
  if (!(await hit(`waitlist:push:${clientIp(req)}`, LIMITS.waitlistLinkPerIp))) return NextResponse.json({ error: "Too many tries." }, { status: 429 });
  if (!vapid().configured) return NextResponse.json({ error: "Notifications aren't switched on yet." }, { status: 503 });
  const raw = await req.text();
  if (raw.length > 4096) return NextResponse.json({ error: "Bad request" }, { status: 413 });
  let body: { k?: unknown; subscription?: unknown };
  try {
    body = JSON.parse(raw) as typeof body;
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  const id = verifyAccess(typeof body.k === "string" ? body.k : null);
  if (!id) return NextResponse.json({ error: "This link has expired." }, { status: 401 });
  const sub = parseSubscription((body.subscription ?? {}) as Parameters<typeof parseSubscription>[0]);
  if (!sub) return NextResponse.json({ error: "That subscription doesn't look right." }, { status: 400 });
  const ok = await saveWaitlistPush(await getStore(), id, sub, await clientMeta());
  return ok ? NextResponse.json({ ok: true }) : NextResponse.json({ error: "Please confirm your email first." }, { status: 403 });
}
