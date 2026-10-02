import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { submitAsk } from "@/lib/offers/ask";
import { getVisitorId } from "@/lib/request";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";

export const runtime = "nodejs";

/** POST /api/offers/ask (plain HTML form, works without JavaScript) → 303 back to /ask/<kind>. */
export async function POST(req: Request) {
  const form = await req.formData().catch(() => null);
  const kind = String(form?.get("kind") ?? "");
  const back = (q: string) => NextResponse.redirect(new URL(`/ask/${/^(group|price)$/.test(kind) ? kind : "price"}?${q}`, req.url), 303);
  if (!form) return back("error=form");
  if (!(await hit(`ask:ip:${clientIp(req)}`, LIMITS.leadsPerIp))) return back("error=busy");
  const r = await submitAsk(await getStore(), {
    kind,
    firstName: form.get("first_name"),
    email: form.get("email"),
    message: form.get("message"),
    seats: form.get("seats"),
    visitorId: await getVisitorId(),
  });
  return r.ok ? back("sent=1") : back(`error=${r.error}`);
}
