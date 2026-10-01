import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";
import { clientMeta, getAttribution, getVisitorId } from "@/lib/request";
import { normalizeEmail } from "@/lib/members";
import { signupWaitlist, validateSignup, REF_CODE } from "@/lib/waitlist";
import { formTimeOk } from "@/lib/waitlistTokens";

export const runtime = "nodejs";

const MAX_BODY = 4 * 1024;

/**
 * Waitlist signup (a plain HTML form post, works without JavaScript).
 *
 * Anti-enumeration: every accepted submission, whatever the email's state (new,
 * pending, confirmed, unsubscribed, throttled, a bot caught by the honeypot or the
 * timing check), gets the identical 303 to /waitlist/thanks. Only input errors that
 * don't depend on the database (bad address, consent box unticked) say anything.
 */
export async function POST(req: Request) {
  const base = new URL(req.url).origin;
  const thanks = () => NextResponse.redirect(`${base}/waitlist/thanks`, 303);
  const back = (error: string, ref?: string) => NextResponse.redirect(`${base}/waitlist?error=${error}${ref && REF_CODE.test(ref) ? `&ref=${ref}` : ""}#join`, 303);

  const len = Number(req.headers.get("content-length") ?? "0");
  if (len > MAX_BODY) return new NextResponse("Too large", { status: 413 });
  const raw = await req.text();
  if (raw.length > MAX_BODY) return new NextResponse("Too large", { status: 413 });
  const f = new URLSearchParams(raw);
  const get = (k: string, max = 300) => (f.get(k) ?? "").slice(0, max);

  if (!(await hit(`waitlist:ip:${clientIp(req)}`, LIMITS.waitlistPerIp))) return back("busy");

  const ref = get("ref", 20).trim().toUpperCase();
  // Bots: the hidden field must stay empty and the form must have been open a few seconds.
  if (get("website") !== "" || !formTimeOk(get("ft", 80))) return thanks();

  const input = {
    email: get("email", 320),
    firstName: get("first_name", 120),
    emailConsent: get("consent_email") === "1",
    adConsent: get("consent_ads") === "1",
  };
  const errors = validateSignup(input);
  if (errors.length) return back(errors[0]!.field === "consent" ? "consent" : "email", ref);

  // Per-address limit answers exactly like success (it can't be used to probe the list).
  if (!(await hit(`waitlist:email:${normalizeEmail(input.email)}`, LIMITS.waitlistPerEmail))) return thanks();

  const meta = await clientMeta();
  try {
    await signupWaitlist(await getStore(), {
      ...input,
      ref,
      visitorId: await getVisitorId(),
      attribution: await getAttribution(),
      ip: meta.ip,
      userAgent: meta.userAgent,
    });
  } catch (err) {
    console.error("waitlist signup failed", (err as Error).message);
    return back("server", ref);
  }
  return thanks();
}
