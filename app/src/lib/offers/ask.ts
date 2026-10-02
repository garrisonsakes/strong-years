/**
 * The two human-handled request paths (MONETIZATION_ENGINE.md §3): a group quote (5+ gift seats) and price help
 * ("pay what you can", decided by a person). Both are a support ticket (holds the email and message) plus an
 * exceptions-queue item (never holds them) plus one `ask` row in offer_events. No price is promised by software.
 */
import type { Store } from "../db/store";
import { raiseException } from "../exceptions";
import { sendEmail } from "../notify";

export const ASK_KINDS = ["group", "price"] as const;
export type AskKind = (typeof ASK_KINDS)[number];

export const ASK_COPY: Record<AskKind, { title: string; intro: string; messageLabel: string; reply: string; sla: string }> = {
  group: {
    title: "A group rate for 5 or more people",
    intro: "Senior centers, church groups, walking clubs, a family of cousins: for 5 or more people we put together a quote by hand. Each person gets their own prepaid gift seat. Nothing renews. Nothing is charged until you approve the quote.",
    messageLabel: "Tell us about the group (who they are, roughly how many, any start date)",
    reply: "A person on our team will email you a quote within 2 business days. Nothing is charged until you say yes.",
    sla: "2 business days",
  },
  price: {
    title: "Ask for a lower price",
    intro: "If money is tight, tell us. A person on our team reads every request and can offer a lower price for a while. There is no automatic discount, nothing to prove, and nothing is charged by sending this. Day 1 stays free for everyone.",
    messageLabel: "Anything you'd like us to know (optional, a sentence is plenty)",
    reply: "A person on our team will reply by email within 2 business days. Nothing is charged by sending this.",
    sla: "2 business days",
  },
};

const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$/;
const clean = (v: unknown, n: number) => (typeof v === "string" ? v.replace(/[\u0000-\u0008\u000B-\u001F<>]/g, "").trim().slice(0, n) : "");

export interface AskInput { kind: string; firstName: unknown; email: unknown; message: unknown; seats?: unknown; visitorId: string | null }

export async function submitAsk(store: Store, x: AskInput): Promise<{ ok: true } | { ok: false; error: string }> {
  if (!(ASK_KINDS as readonly string[]).includes(x.kind)) return { ok: false, error: "kind" };
  const kind = x.kind as AskKind;
  const email = clean(x.email, 254).toLowerCase();
  const firstName = clean(x.firstName, 60);
  const message = clean(x.message, 1000);
  const seats = kind === "group" ? Math.max(0, Math.min(500, Math.floor(Number(x.seats) || 0))) : null;
  if (!EMAIL.test(email)) return { ok: false, error: "email" };
  if (!firstName) return { ok: false, error: "first_name" };
  if (kind === "group" && (seats ?? 0) < 5) return { ok: false, error: "seats" };
  const reason = kind === "group" ? "group_quote" : "price_help";
  const t = await store.insert("support_tickets", { member_id: null, email, reason, message: `${firstName}${seats ? ` · ${seats} seats` : ""}: ${message}`, status: "open" });
  await raiseException(store, {
    type: reason,
    title: kind === "group" ? `Group quote request (${seats} seats)` : "Price-help request",
    detail: `Support ticket ${t.id.slice(0, 8)} holds the contact and message. Reply within ${ASK_COPY[kind].sla}. ${kind === "group" ? "Quote = gift seats with the GROUP5 code (20% off 5+) or a draft order." : "If approved, issue a single-use SYHELP code (shopify/config/catalog.ts HARDSHIP_POLICY)."}`,
    ref: t.id,
    source: "ask",
  });
  try {
    await store.insert("offer_events", { kind: "ask", visitor_id: x.visitorId, member_id: null, surface: "ask", experiment: null, arm: null, offer: kind === "group" ? "group_quote" : "hardship_request", rule: null, shown_price_cents: null, revenue_cents: 0, channel: null, ref: null, day: new Date().toISOString().slice(0, 10) });
  } catch {
    /* measurement only */
  }
  await sendEmail({ to: email, template: `ASK_${kind}`, subject: kind === "group" ? "We got your group request" : "We got your note", text: `${firstName}, thank you. ${ASK_COPY[kind].reply}` });
  return { ok: true };
}
