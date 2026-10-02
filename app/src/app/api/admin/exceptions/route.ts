import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { decideException, type Decision } from "@/lib/exceptions";
import { crossSiteReason } from "@/lib/adminGuard";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** Behind the admin basic auth (middleware). The deciding person is the authenticated admin user. */
function actorFrom(req: Request): string {
  const h = req.headers.get("authorization") ?? "";
  if (!h.startsWith("Basic ")) return "";
  try {
    return Buffer.from(h.slice(6), "base64").toString("utf8").split(":")[0]!.trim();
  } catch {
    return "";
  }
}

export async function POST(req: Request) {
  // Round 6: a boost/affiliate approval must come from our own admin page, never a forged cross-site form.
  if (crossSiteReason(req)) return NextResponse.json({ error: "Cross-site request refused." }, { status: 403 });
  const form = await req.formData();
  const id = String(form.get("id") ?? "");
  const decision = String(form.get("decision") ?? "") as Decision;
  if (!["approve", "reject", "resolve"].includes(decision) || !/^[0-9a-f-]{36}$/.test(id)) return NextResponse.json({ error: "invalid" }, { status: 400 });
  const maxRaw = String(form.get("max_daily_usd") ?? "").trim();
  const actor = actorFrom(req) || process.env.ADMIN_USER || "admin";
  const store = await getStore();
  const res = await decideException(store, { id, decision, actor, note: String(form.get("note") ?? ""), maxDailyUsd: maxRaw ? Number(maxRaw) : undefined });
  const url = new URL("/admin/exceptions", req.url);
  url.searchParams.set(res.ok ? "done" : "error", res.ok ? decision : res.reason);
  return NextResponse.redirect(url, 303);
}
