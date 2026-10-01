import { NextResponse, type NextRequest } from "next/server";
import { ARM_COOKIE, ATTR_COOKIE, LAST_TOUCH_COOKIE, attributionFromUrl, encodeAttribution, touchFromUrl } from "@/lib/analytics/attribution";
import { SESSION_COOKIE, verifySession } from "@/lib/auth/session";
import { VID_COOKIE } from "@/lib/blitz";
import { parseBasicAuth, safeEqual } from "@/lib/safeEqual";
import { signVid, verifyVid } from "@/lib/vid";
import { AdminGuard, splitPasswordAndCode, verifyTotp } from "@/lib/adminGuard";
import { trustedClientIp } from "@/lib/clientIp";
import { isDeployed } from "@/lib/deployEnv";

/** Query parameter on launch links: a signed visitor id (lib/vid.ts). */
const LINK_VID_PARAM = "sy_v";

const REAL_DATA = Boolean(process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL);
// Dev defaults only apply to the in-memory demo. With real data, missing secrets lock the doors.
const SESSION_SECRET = process.env.SESSION_SECRET || (REAL_DATA ? "" : "dev-only-session-secret-change-me-0123456789");

/**
 * Admin: HTTP Basic auth, then (if ADMIN_TOTP_SECRET is set) a 6-digit authenticator
 * code typed after the password. Round 8: lockout by trusted client IP AND by
 * username, with exponential backoff (lib/adminGuard.ts), so rotating
 * X-Forwarded-For doesn't reset anything.
 */
async function adminCredentialsOk(user: string, rawPass: string): Promise<boolean> {
  // Round 9: on any real deploy both are required (no defaults); only a local
  // in-memory demo gets admin / strongyears-demo.
  const local = !isDeployed() && !REAL_DATA;
  const wantUser = process.env.ADMIN_USER || (local ? "admin" : "");
  const wantPass = process.env.ADMIN_PASSWORD || (local ? "strongyears-demo" : "");
  if (!wantUser || !wantPass) return false; // not configured: locked
  const totp = process.env.ADMIN_TOTP_SECRET;
  const { password, code } = totp ? splitPasswordAndCode(rawPass) : { password: rawPass, code: "" };
  // L6: constant-time compares, all evaluated.
  const okUser = safeEqual(user, wantUser);
  const okPass = safeEqual(password, wantPass);
  const okCode = totp ? await verifyTotp(totp, code) : true;
  return okUser && okPass && okCode;
}

const g = globalThis as unknown as { __syAdminGuard?: AdminGuard };
const adminGuard = (g.__syAdminGuard ??= new AdminGuard());

const unauthorized = () => new NextResponse("Authentication required", { status: 401, headers: { "WWW-Authenticate": 'Basic realm="Strong Years admin"' } });

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  if (pathname.startsWith("/admin") || pathname.startsWith("/api/admin")) {
    const creds = parseBasicAuth(req.headers.get("authorization"));
    if (!creds) return unauthorized();
    const keys = AdminGuard.keys(trustedClientIp(req.headers), creds.user);
    const wait = adminGuard.retryAfter(keys);
    if (wait > 0) {
      return new NextResponse(`Too many failed attempts. Try again in ${Math.ceil(wait / 60)} minute${wait > 60 ? "s" : ""}.`, { status: 429, headers: { "Retry-After": String(wait) } });
    }
    if (!(await adminCredentialsOk(creds.user, creds.pass))) {
      adminGuard.fail(keys);
      return unauthorized();
    }
    adminGuard.success(keys);
    return NextResponse.next();
  }

  if (pathname.startsWith("/app")) {
    const ok = SESSION_SECRET ? await verifySession(req.cookies.get(SESSION_COOKIE)?.value, SESSION_SECRET) : null;
    if (!ok) {
      const url = req.nextUrl.clone();
      url.pathname = "/login";
      url.search = `?next=${encodeURIComponent(pathname)}`;
      return NextResponse.redirect(url);
    }
  }

  // Anything assigned here is also forwarded on the request, so the page rendering
  // this very request already sees the arm and attribution.
  const set: [string, string, number][] = [];
  // Launch links (waitlist emails and pushes) carry the waitlister's own signed visitor
  // id, so the sticky cell assignment (Shopify front-end cell, or the Stripe price cell)
  // follows the person to whatever device opens the email. Only ids we signed are
  // accepted; a forged or edited value is ignored.
  const linkVid = req.nextUrl.searchParams.get(LINK_VID_PARAM);
  const linkVidOk = SESSION_SECRET && linkVid && linkVid.length <= 120 ? await verifyVid(linkVid, SESSION_SECRET) : null;
  if (linkVidOk && req.cookies.get(VID_COOKIE)?.value !== linkVid) {
    set.push([VID_COOKIE, linkVid!, 365 * 86400]);
  } else if (SESSION_SECRET && !(await verifyVid(req.cookies.get(VID_COOKIE)?.value, SESSION_SECRET))) {
    // Sticky visitor id: drives the deterministic 50/50 price cell (src/lib/blitz.ts).
    // L5: signed, so the price cell can't be chosen by editing the cookie.
    set.push([VID_COOKIE, await signVid(crypto.randomUUID(), SESSION_SECRET), 365 * 86400]);
  }
  const attr = attributionFromUrl(req.nextUrl);
  if (attr && !req.cookies.get(ATTR_COOKIE)) set.push([ATTR_COOKIE, encodeAttribution(attr), 90 * 86400]);
  // Last touch: every attributed visit overwrites it (first touch above never changes).
  const touch = touchFromUrl(req.nextUrl);
  if (touch) set.push([LAST_TOUCH_COOKIE, encodeAttribution(touch), 90 * 86400]);
  const forced = req.nextUrl.searchParams.get("arm");
  // QA override only. Normal visitors get their arm from a sticky hash of the signed
  // visitor id (lib/blitz.ts assignArm, ARM_B_SHARE), logged with every exposure.
  if (forced === "A" || forced === "B") set.push([ARM_COOKIE, forced, 180 * 86400]);
  if (set.length === 0) return NextResponse.next();
  const headers = new Headers(req.headers);
  const jar = new Map(req.cookies.getAll().map((c) => [c.name, c.value]));
  for (const [k, v] of set) jar.set(k, v);
  headers.set("cookie", [...jar].map(([k, v]) => `${k}=${v}`).join("; "));
  const res = NextResponse.next({ request: { headers } });
  for (const [k, v, maxAge] of set) res.cookies.set(k, v, { maxAge, path: "/", sameSite: "lax" });
  return res;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt|api/stripe/webhook|api/webhooks|api/cron|api/sms|api/growth|api/exceptions|api/unsubscribe).*)"],
};
