import { validTwilioSignature } from "@/lib/twilio";
import { env, messaging } from "@/lib/config";
import { getStore } from "@/lib/db";
import { cancelMembership } from "@/lib/billing/actions";
import { billingMembership } from "@/lib/auth/server";
import { phoneDigits } from "@/lib/members";

export const runtime = "nodejs";

/**
 * Twilio inbound SMS webhook. Makes "text CANCEL" real once texting is on.
 *
 * H4: fails closed. Without SMS_ENABLED and TWILIO_AUTH_TOKEN every request is
 * refused, and every request must carry a valid X-Twilio-Signature.
 * M9: CANCEL is also a carrier opt-out keyword, so Twilio may swallow our reply.
 * We treat it as both: texts stop, the membership is cancelled, and the
 * confirmation goes by email (as the terms promise).
 */
function twiml(msg: string) {
  const safe = msg.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><Response><Message>${safe}</Message></Response>`, { headers: { "Content-Type": "text/xml" } });
}

export async function POST(req: Request) {
  const token = process.env.TWILIO_AUTH_TOKEN;
  if (!messaging.smsEnabled || !token) return new Response("forbidden", { status: 403 });
  const raw = await req.text();
  const params = new URLSearchParams(raw);
  if (!validTwilioSignature(`${env.siteUrl}/api/sms/inbound`, params, req.headers.get("x-twilio-signature"), token)) {
    return new Response("forbidden", { status: 403 });
  }
  const digits = phoneDigits(params.get("From"));
  const body = (params.get("Body") ?? "").trim().toUpperCase();
  const store = await getStore();
  // H4/H7: indexed lookup, not a scan of the whole members table.
  const members = digits ? await store.find("members", { phone_digits: digits }) : [];

  const optOut = ["STOP", "STOPALL", "UNSUBSCRIBE", "END", "QUIT", "CANCEL"].includes(body);
  if (optOut) for (const m of members) await store.update("members", m.id, { sms_opt_in: false, reminder_channel: "email" });

  if (body === "CANCEL") {
    const member = members[0];
    if (!member) return new Response(null, { status: 204 });
    const m = await billingMembership(member.id);
    if (m && !m.cancel_at_period_end && !["canceled", "refunded", "expired"].includes(m.status)) {
      // cancelMembership sends the confirmation by email.
      await cancelMembership(store, m, null, null);
    }
    return new Response(null, { status: 204 }); // Twilio sends the carrier opt-out confirmation
  }
  if (optOut) return new Response(null, { status: 204 });
  if (body === "HELP") return twiml(`Strong Years: help at ${env.supportEmail}. Reply CANCEL to cancel your membership (confirmation by email), STOP to stop texts.`);
  return twiml(`Strong Years: this number is automated. Reply CANCEL to cancel, STOP to stop texts, or email ${env.supportEmail}.`);
}
