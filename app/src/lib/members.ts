import type { Store } from "./db/store";
import type { Attribution, Member, Membership, Sex } from "./db/types";

/**
 * NEW-1: one canonical form for every email we store or look up, so case,
 * whitespace, full-width letters or invisible characters can't create a second
 * spelling of someone else's address (or dodge the "existing member" check).
 */
export function normalizeEmail(raw: string): string {
  return raw
    .normalize("NFKC")
    .replace(/[\u00AD\u200B-\u200F\u2060-\u206F\uFEFF]/g, "")
    .trim()
    .toLowerCase();
}

export function defaultMember(email: string, firstName: string): Partial<Member> {
  return {
    email: normalizeEmail(email),
    first_name: firstName.trim() || "Friend",
    phone: null,
    sex: null,
    age: null,
    age_confirmed_at: null,
    track: "steady",
    active_program: null,
    program_started_at: null,
    sms_opt_in: false,
    reminder_channel: "email",
    reminder_time: "07:30",
    timezone: "America/Los_Angeles",
    memory_enabled: false,
    stripe_customer_id: null,
    stripe_payment_method: null,
    attribution: null,
    protected_weeks: [],
    phone_digits: null,
    card_fingerprint: null,
    session_version: 1,
    email_verified_at: null,
    ad_opt_out: false,
    is_demo: false,
  };
}

/** H4: indexed phone lookup key (last 10 digits). */
export function phoneDigits(p: string | null | undefined): string | null {
  const d = (p ?? "").replace(/[^0-9]/g, "").slice(-10);
  return d.length === 10 ? d : null;
}

export async function findMemberByEmail(store: Store, email: string): Promise<Member | null> {
  return store.findOne("members", { email: normalizeEmail(email) });
}

export interface UpsertMemberInput {
  email: string;
  firstName: string;
  phone?: string | null;
  smsOptIn?: boolean;
  ageConfirmed?: boolean;
  attribution?: Attribution | null;
  stripeCustomerId?: string | null;
  stripePaymentMethod?: string | null;
  sex?: Sex | null;
  age?: number | null;
  track?: Member["track"];
}

export async function upsertMember(store: Store, input: UpsertMemberInput): Promise<Member> {
  const existing = await findMemberByEmail(store, input.email);
  const now = new Date().toISOString();
  if (existing) {
    const patch: Partial<Member> = {};
    if (input.phone && !existing.phone) {
      patch.phone = input.phone;
      patch.phone_digits = phoneDigits(input.phone);
    }
    if (input.smsOptIn) {
      patch.sms_opt_in = true;
      patch.reminder_channel = "sms";
    }
    if (input.ageConfirmed && !existing.age_confirmed_at) patch.age_confirmed_at = now;
    // NEW-1: a checkout never replaces an existing member's Stripe customer or card.
    if (input.stripeCustomerId && !existing.stripe_customer_id) patch.stripe_customer_id = input.stripeCustomerId;
    if (input.stripePaymentMethod && !existing.stripe_payment_method) patch.stripe_payment_method = input.stripePaymentMethod;
    if (input.attribution && !existing.attribution) patch.attribution = input.attribution;
    if (input.sex && !existing.sex) patch.sex = input.sex;
    if (input.age && !existing.age) patch.age = input.age;
    if (Object.keys(patch).length === 0) return existing;
    return (await store.update("members", existing.id, patch))!;
  }
  return store.insert("members", {
    ...defaultMember(input.email, input.firstName),
    phone: input.phone ?? null,
    phone_digits: phoneDigits(input.phone),
    sms_opt_in: Boolean(input.smsOptIn),
    reminder_channel: input.smsOptIn ? "sms" : "email",
    age_confirmed_at: input.ageConfirmed ? now : null,
    attribution: input.attribution ?? null,
    stripe_customer_id: input.stripeCustomerId ?? null,
    stripe_payment_method: input.stripePaymentMethod ?? null,
    sex: input.sex ?? null,
    age: input.age ?? null,
    track: input.track ?? "steady",
  });
}

/** Founding spots claimed: founding memberships ever started, minus refunded ones (spot released). */
export async function foundingClaimed(store: Store): Promise<number> {
  return store.count("memberships", { founding: true, status: { in: ["active", "past_due", "paused", "canceled", "expired"] } });
}

/** H12: scheduled cancellations are not recurring revenue (reported as "scheduled churn"). */
export function mrrCents(m: Membership): number {
  if (!["active", "past_due"].includes(m.status)) return 0;
  if (m.cancel_at_period_end) return 0;
  if (m.plan === "gift") return 0; // prepaid gifts excluded from MRR by default (BLITZ.md)
  const partner = m.partner_seat ? 800 : 0;
  if (m.interval === "year") return Math.round(m.price_cents / 12) + partner;
  return m.price_cents + partner;
}
