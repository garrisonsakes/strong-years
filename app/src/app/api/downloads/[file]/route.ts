import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";
import { currentMember, currentMembership, entitlement } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import { ALL_DOWNLOAD_FILES, entitledDownloads } from "@/lib/products";
import { watermarkPdf } from "@/lib/watermark";
import { clientMeta } from "@/lib/request";
import type { Order } from "@/lib/db/types";

/** Which purchase a file belongs to, for the watermark and the download log. */
function orderRefFor(file: string, orders: Order[], membershipId: string | null): string {
  const paid = orders.filter((o) => o.status === "paid" || o.status === "refund_pending");
  const by = (...skus: string[]) => paid.find((o) => skus.includes(o.offer_code) || (skus.includes("reset") && /^(ebook_|bundle_m12)/.test(o.offer_code)));
  const o = file.startsWith("strength_reset") ? by("reset") : file === "strong_kitchen.pdf" ? by("kitchen", "reset") : file === "twelve_week_printable.pdf" ? by("kitchen", "wallplan") : null;
  if (o) return `SY-${o.id.slice(0, 8).toUpperCase()}`;
  return membershipId ? `M-${membershipId.slice(0, 8).toUpperCase()}` : "M-UNKNOWN";
}

export const runtime = "nodejs";

/** Paid PDFs live outside public/ and are served only to members entitled to them. */
export async function GET(_req: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  if (!ALL_DOWNLOAD_FILES.includes(file)) return NextResponse.json({ error: "Not found" }, { status: 404 });
  const member = await currentMember();
  if (!member) return NextResponse.json({ error: "Please log in." }, { status: 401 });
  // H2: membership files need a membership that grants access right now; one-time
  // purchases (Reset, Kitchen, Wall Plan) stay downloadable, they're yours to keep.
  const ent = await entitlement(member.id);
  const store = await getStore();
  const orders = await store.find("sy_orders", { member_id: member.id });
  const current = ent.access ? await currentMembership(member.id) : null;
  const d = entitledDownloads(member, current, orders).find((x) => x.file === file);
  if (!d) return NextResponse.json({ error: "This download isn't part of your plan." }, { status: 403 });
  if (d.lockedUntil) return NextResponse.json({ error: `This unlocks on ${new Date(d.lockedUntil).toDateString()}.` }, { status: 403 });
  const buf = await readFile(path.join(process.cwd(), "content", "downloads", file));
  // F08: every copy carries the buyer's name, email and order, and every download is logged.
  const orderRef = orderRefFor(file, orders, current?.id ?? null);
  const stamped = await watermarkPdf(new Uint8Array(buf), { name: member.first_name, email: member.email, orderRef });
  const meta = await clientMeta();
  await store.insert("download_events", { member_id: member.id, file, order_ref: orderRef, ip: meta.ip, user_agent: meta.userAgent });
  return new NextResponse(new Uint8Array(stamped), {
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${file.replace(/_(2000|2500|3000|3500)(?=\.pdf$)/, "")}"`,
      "Cache-Control": "private, no-store",
    },
  });
}
