import { readFile } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { REFERRAL_BONUS_FILE } from "@/lib/waitlist";
import { watermarkPdf } from "@/lib/watermark";
import { verifyAccess } from "@/lib/waitlistTokens";

export const runtime = "nodejs";

/** The referral reward: served only once it has unlocked, watermarked like every paid PDF. */
export async function GET(req: Request) {
  if (!(await hit(`waitlist:bonus:${clientIp(req)}`, LIMITS.waitlistLinkPerIp))) return NextResponse.json({ error: "Too many tries." }, { status: 429 });
  const id = verifyAccess(new URL(req.url).searchParams.get("k"));
  if (!id) return NextResponse.json({ error: "This link has expired. Use the newest email from us." }, { status: 401 });
  const store = await getStore();
  const entry = await store.get("waitlist", id);
  if (!entry || entry.status !== "confirmed" || !entry.referral_reward_at) return NextResponse.json({ error: "This unlocks when a friend you shared your link with confirms their email." }, { status: 403 });
  const buf = await readFile(path.join(process.cwd(), "content", "downloads", REFERRAL_BONUS_FILE));
  const orderRef = `WL-${entry.id.slice(0, 8).toUpperCase()}`;
  const stamped = await watermarkPdf(new Uint8Array(buf), { name: entry.first_name ?? "Strong Years waitlist", email: entry.email, orderRef });
  return new NextResponse(new Uint8Array(stamped), {
    headers: { "Content-Type": "application/pdf", "Content-Disposition": 'attachment; filename="strong-years-wall-plan.pdf"', "Cache-Control": "private, no-store" },
  });
}
