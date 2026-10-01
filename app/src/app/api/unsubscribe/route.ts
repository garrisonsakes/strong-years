import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { unsubscribe, verifyUnsubscribe } from "@/lib/lifecycle/engine";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function emailFrom(url: URL): string {
  try {
    return Buffer.from(url.searchParams.get("e") ?? "", "base64url").toString("utf8").slice(0, 254);
  } catch {
    return "";
  }
}

const page = (title: string, body: string, status = 200) =>
  new NextResponse(
    `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title><meta name="robots" content="noindex"></head><body style="margin:0;background:#FBF6EC;color:#16120E;font:20px/1.55 system-ui,sans-serif"><main style="max-width:640px;margin:0 auto;padding:32px 16px"><h1 style="font-size:36px;line-height:1.2">${title}</h1>${body}</main></body></html>`,
    { status, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } },
  );

/** The link in the email: a page with one button (a GET never unsubscribes, so link scanners can't). */
export async function GET(req: Request) {
  const url = new URL(req.url);
  const email = emailFrom(url);
  if (!verifyUnsubscribe(email, url.searchParams.get("t") ?? "")) return page("This link doesn't work", "<p>It may be incomplete. Reply to any of our emails and a person will take you off the list.</p>", 400);
  const action = `/api/unsubscribe?${url.searchParams.toString()}`.replace(/&/g, "&amp;");
  return page(
    "Stop these emails?",
    `<p>Tips, onboarding, offers and the daily coach email will stop. Billing notices about a paid membership (receipts, renewal and payment notices) still arrive while you have one.</p><form method="post" action="${action}"><button type="submit" style="min-height:56px;padding:12px 24px;font:700 20px system-ui;background:#16120E;color:#FFFFFF;border:2px solid #16120E;border-radius:12px;cursor:pointer">Unsubscribe</button></form>`,
  );
}

/** RFC 8058 one-click (body "List-Unsubscribe=One-Click") and the page's button. */
export async function POST(req: Request) {
  const url = new URL(req.url);
  const email = emailFrom(url);
  if (!verifyUnsubscribe(email, url.searchParams.get("t") ?? "")) return NextResponse.json({ error: "invalid link" }, { status: 400 });
  const ct = req.headers.get("content-type") ?? "";
  const oneClick = ct.includes("application/x-www-form-urlencoded") && (await req.text()).includes("List-Unsubscribe=One-Click");
  await unsubscribe(await getStore(), email, oneClick ? "rfc8058_one_click" : "unsubscribe_page");
  if (oneClick) return new NextResponse("unsubscribed", { status: 200 });
  return page("You're unsubscribed", "<p>Done. No more tips, onboarding or offer emails. Changed your mind? Reply to any email and a person will add you back.</p>");
}
