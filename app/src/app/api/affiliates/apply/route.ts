import { NextResponse } from "next/server";
import { applyAffiliate } from "@/lib/affiliates";
import { getStore } from "@/lib/db";
import { clientIp, hit } from "@/lib/rateLimit";

export const runtime = "nodejs";

export async function POST(req: Request) {
  if (!(await hit(`affiliate:ip:${clientIp(req)}`, { max: 5, windowMs: 60 * 60_000 }))) return NextResponse.redirect(new URL("/affiliates?error=rate", req.url), 303);
  const f = await req.formData();
  const res = await applyAffiliate(await getStore(), {
    email: String(f.get("email") ?? ""),
    name: String(f.get("name") ?? ""),
    channel: String(f.get("channel") ?? ""),
    audience: String(f.get("audience") ?? ""),
    ftcAck: f.get("ftc") === "yes",
    termsAck: f.get("terms") === "yes",
  });
  const url = new URL("/affiliates", req.url);
  if (res.ok) url.searchParams.set("sent", "1");
  else url.searchParams.set("error", res.errors.join(","));
  return NextResponse.redirect(url, 303);
}
