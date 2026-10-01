import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { parseException, raiseException } from "@/lib/exceptions";
import { alertOnCall } from "@/lib/notify";
import { clientIp, hit } from "@/lib/rateLimit";
import { safeEqual } from "@/lib/safeEqual";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Workers post items for a person to decide (compliance "human" verdicts, judge
 * disagreements, uniqueness denials, upload/auth failures, boost approvals, DM crisis
 * escalations).  Authorization: Bearer $EXCEPTIONS_API_TOKEN (32+ chars; unset = 404).
 * Idempotent on (type, dedupe_key): a repeat returns the existing item (200, created false).
 */
export async function POST(req: Request) {
  const token = process.env.EXCEPTIONS_API_TOKEN ?? "";
  if (token.length < 32) return NextResponse.json({ error: "Not found" }, { status: 404 });
  if (!(await hit(`exceptions:ip:${clientIp(req)}`, { max: 600, windowMs: 60 * 60_000 }))) return NextResponse.json({ error: "Too many requests" }, { status: 429 });
  if (!safeEqual(req.headers.get("authorization") ?? "", `Bearer ${token}`)) return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  const raw = await req.text();
  if (raw.length > 16_000) return NextResponse.json({ error: "too large" }, { status: 413 });
  let body: unknown;
  try {
    body = JSON.parse(raw);
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }
  const parsed = parseException(body);
  if (!parsed.ok) return NextResponse.json({ error: "invalid", details: parsed.errors }, { status: 422 });
  const store = await getStore();
  const { row, created } = await raiseException(store, parsed.item);
  if (created && (row.severity === "critical" || row.type === "crisis_escalation")) await alertOnCall(`${row.title}`, "exceptions");
  return NextResponse.json({ id: row.id, status: row.status, created }, { status: created ? 201 : 200 });
}
