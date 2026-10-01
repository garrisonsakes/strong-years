import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { monthlyStatement, refundRateCheck, statementCsv } from "@/lib/affiliates";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** GET /api/admin/affiliates/statement?month=YYYY-MM → CSV (admin basic auth). Also runs the refund-rate fraud check. */
export async function GET(req: Request) {
  const month = new URL(req.url).searchParams.get("month") ?? new Date().toISOString().slice(0, 7);
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(month)) return NextResponse.json({ error: "month must be YYYY-MM" }, { status: 400 });
  const store = await getStore();
  const lines = await monthlyStatement(store, month);
  await refundRateCheck(store, month, lines);
  return new NextResponse(statementCsv(lines), {
    headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="affiliate-statement-${month}.csv"`, "Cache-Control": "no-store" },
  });
}
