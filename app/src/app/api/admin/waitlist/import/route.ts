import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { MAX_IMPORT_BYTES, importWarmList, isWarmBrand } from "@/lib/warmImport";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Warm-list CSV import (admin; basic auth + lockout in middleware). Body: the CSV
 * (text/csv). Query: brand=k9supps|unignorable, batch=<label>, commit=1 to write.
 * Without commit=1 it is a dry run: the same summary, nothing written, nothing sent.
 * Invites (the double opt-in email) go out later from /api/cron/warm-invites.
 *
 *   curl -u "$ADMIN_USER:$ADMIN_PASSWORD" -H 'content-type: text/csv' \
 *     --data-binary @k9supps.csv "https://members.strongyears.com/api/admin/waitlist/import?brand=k9supps"
 */
export async function POST(req: Request) {
  const url = new URL(req.url);
  const origin = req.headers.get("origin");
  const site = req.headers.get("sec-fetch-site");
  if ((origin && origin !== url.origin) || (site && site !== "same-origin" && site !== "none")) {
    return NextResponse.json({ error: "Cross-site request refused." }, { status: 403 });
  }
  const brand = url.searchParams.get("brand");
  if (!isWarmBrand(brand)) return NextResponse.json({ error: "brand must be k9supps or unignorable" }, { status: 400 });
  const len = Number(req.headers.get("content-length") ?? 0);
  if (len > MAX_IMPORT_BYTES) return NextResponse.json({ error: "file too large; split it" }, { status: 413 });
  const csv = await req.text();
  if (csv.length > MAX_IMPORT_BYTES) return NextResponse.json({ error: "file too large; split it" }, { status: 413 });
  const summary = await importWarmList(await getStore(), csv, {
    brand,
    commit: url.searchParams.get("commit") === "1",
    batch: url.searchParams.get("batch") ?? undefined,
  });
  return NextResponse.json(summary, { status: summary.errors.length ? 422 : 200, headers: { "Cache-Control": "no-store" } });
}
