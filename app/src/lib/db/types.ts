export type Arm = "A" | "B";
export type Track = "rebuild" | "steady" | "strong" | "iron";
export type ProcessorId = "stripe" | "braintree" | "shopify";
export type Sex = "woman" | "man" | "na";

/**
 * One touch: where a visit came from. Post-level fields come from bio links, DM
 * links and waitlist links (see lib/analytics/attribution.ts for the URL format).
 * Validated and length-limited on the way in; never used for pricing.
 */
export interface TouchPoint {
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_content?: string;
  utm_term?: string;
  mc_id?: string;
  /** ig | tt | yt | fb | th | email | dm | web | other */
  platform?: string;
  /** The brand page / account handle that posted (e.g. changyin.strong). */
  page?: string;
  post_id?: string;
  /** The comment/DM keyword (e.g. JOIN, STRONG). */
  keyword?: string;
  character?: "chang" | "sun";
  landing_path?: string;
  at?: string;
}

export interface Attribution {
  /** Post-level first touch (same validation as TouchPoint). */
  platform?: string;
  page?: string;
  post_id?: string;
  keyword?: string;
  character?: "chang" | "sun";
  /** The most recent attributed visit before this record was written. */
  last_touch?: TouchPoint;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_content?: string;
  utm_term?: string;
  mc_id?: string;
  fbclid?: string;
  landing_path?: string;
  first_seen_at?: string;
  /** CCPA/CPRA "Do Not Sell or Share" or a Global Privacy Control signal: never sent to ad platforms. */
  ad_opt_out?: boolean;
}

export interface Member {
  id: string;
  email: string;
  first_name: string;
  phone: string | null;
  sex: Sex | null;
  age: number | null;
  age_confirmed_at: string | null;
  track: Track;
  active_program: string | null;
  program_started_at: string | null;
  sms_opt_in: boolean;
  reminder_channel: "sms" | "email";
  reminder_time: string;
  timezone: string;
  memory_enabled: boolean;
  stripe_customer_id: string | null;
  stripe_payment_method: string | null;
  attribution: Attribution | null;
  protected_weeks: string[];
  /** Digits only (last 10) for indexed SMS lookups. */
  phone_digits: string | null;
  /** Card fingerprint of the first card used (one guarantee refund per person). */
  card_fingerprint: string | null;
  /** Bumped to revoke every session (logout everywhere, refund, first email verification). */
  session_version: number;
  /**
   * R2-1: set the first time someone proves they own this inbox (login link, gift
   * claim link, purchase confirmation link). Until then no session can read the
   * account: a checkout only gets a short purchase-scoped session.
   */
  email_verified_at: string | null;
  /** CCPA/CPRA "Do Not Sell or Share" + GPC. */
  ad_opt_out: boolean;
  /** Shopify customer this member was provisioned from (billing provider "shopify"). */
  shopify_customer_id?: string | null;
  /** updated_at of the newest customers/update applied (out-of-order guard). */
  shopify_customer_updated_at?: string | null;
  is_demo: boolean;
  created_at: string;
}

export type MembershipStatus =
  | "incomplete"
  | "trialing"
  | "active"
  | "past_due"
  | "paused"
  | "canceled"
  | "refunded"
  | "expired";

export type Plan = "monthly" | "essentials" | "annual" | "gift";

export interface Membership {
  id: string;
  member_id: string;
  plan: Plan;
  arm: Arm | null;
  offer_code: string;
  price_cents: number;
  interval: "month" | "year" | "none";
  status: MembershipStatus;
  founding: boolean;
  stripe_subscription_id: string | null;
  trial_end: string | null;
  current_period_end: string | null;
  first_paid_at: string | null;
  guarantee_until: string | null;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
  paused_until: string | null;
  partner_seat: boolean;
  processor: ProcessorId;
  price_cell: string | null;
  checkout_intent_id: string | null;
  /** Gift months credited onto a paying membership (H3): billing continues, credit applies. */
  gift_credit_cents: number;
  /** NEW-1: bought with this member's email by someone not signed in as them; no access until confirmed. */
  pending_verification: boolean;
  /** The Stripe customer that pays for this membership (may differ from members.stripe_customer_id). */
  stripe_customer_id: string | null;
  /** Shopify Subscriptions: the contract that bills this membership. */
  shopify_contract_id?: string | null;
  /** The Shopify order that created the contract (orders/paid and contracts/create meet here). */
  shopify_origin_order_id?: string | null;
  shopify_customer_id?: string | null;
  /** Highest contract revision_id applied: older subscription_contracts/* events are ignored. */
  shopify_revision?: number | null;
  /** Highest billing attempt id applied: an older success/failure arriving late changes nothing. */
  shopify_last_attempt_id?: string | null;
  /** After a failed billing attempt: access continues until this moment, then stops until a payment succeeds. */
  grace_until?: string | null;
  is_demo: boolean;
  created_at: string;
  updated_at: string;
}

export type OrderKind =
  | "trial_fee"
  | "front_end"
  | "bump"
  | "upsell_program"
  | "upsell_kit"
  | "downsell_printables"
  | "gift"
  | "membership_charge"
  | "coached_charge";

export interface Order {
  id: string;
  member_id: string | null;
  email: string;
  offer_code: string;
  kind: OrderKind;
  description: string;
  amount_cents: number;
  status: "paid" | "refund_pending" | "refunded" | "disputed";
  stripe_payment_intent: string | null;
  stripe_invoice: string | null;
  checkout_intent_id: string | null;
  /** The membership this charge belongs to (H1: refunds are scoped per membership). */
  membership_id: string | null;
  amount_refunded_cents: number;
  processor: ProcessorId;
  shopify_order_id?: string | null;
  /** Shopify line item id: (shopify_line_id, kind) is unique, so a replayed order never double-records. */
  shopify_line_id?: string | null;
  is_demo: boolean;
  created_at: string;
}

export interface CheckoutIntent {
  id: string;
  email: string;
  first_name: string;
  phone: string | null;
  offer_code: string;
  arm: Arm | null;
  bump: boolean;
  gentle: boolean;
  amount_today_cents: number;
  lines: { label: string; cents: number; kind: string; sku?: string }[];
  membership_price_cents: number | null;
  trial_days: number;
  consent_id: string | null;
  sms_consent: boolean;
  age_confirmed: boolean;
  gift: { recipient_name: string; recipient_email: string; message: string; months: number } | null;
  attribution: Attribution | null;
  /** Ticked the optional ad-measurement box at checkout (applied at fulfilment if the buyer owns the email). */
  ad_consent?: boolean;
  lead_id: string | null;
  status: "open" | "fulfilling" | "complete" | "failed";
  completed_at: string | null;
  /** M2: the success URL signs the buyer in once. */
  login_consumed_at: string | null;
  /** NEW-1: set when checkout started from a logged-in session for this same email. */
  auth_member_id: string | null;
  /** NEW-1: true only when the buyer provably owns the account (new account, or logged in). */
  buyer_is_owner: boolean | null;
  /** NEW-1: purchase made with an existing member's email, awaiting the inbox owner's confirmation. */
  verification: "pending" | "confirmed" | "rejected" | null;
  verify_token_hash: string | null;
  verify_expires_at: string | null;
  /** The Stripe customer this checkout created (never merged into another member). */
  stripe_customer_id: string | null;
  processor: ProcessorId;
  price_cell: string | null;
  visitor_id: string | null;
  stripe_session_id: string | null;
  member_id: string | null;
  created_at: string;
}

export type ConsentKind = "auto_renew" | "sms" | "age_18" | "memory" | "partner_auto_renew" | "family_share" | "do_not_sell_share" | "ad_tracking" | "waitlist_email" | "waitlist_push";

export interface ConsentRecord {
  id: string;
  email: string;
  member_id: string | null;
  kind: ConsentKind;
  checked: boolean;
  text_shown: string;
  price_cents: number | null;
  first_charge_at: string | null;
  offer_code: string | null;
  ip: string | null;
  user_agent: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  email: string;
  first_name: string;
  phone: string | null;
  sms_consent: boolean;
  quiz: "strength_age" | "gut_energy";
  profile_code: string;
  /** First-party only. Never sent to ad platforms (OFFER.md 2.6). */
  result: Record<string, unknown>;
  answers: Record<string, unknown>;
  flags: string[];
  attribution: Attribution | null;
  created_at: string;
}

export interface PracticeLog {
  id: string;
  member_id: string;
  day: string; // YYYY-MM-DD
  session_key: string;
  track: Track;
  swap: string | null;
  minutes: number;
  created_at: string;
}

export interface Retest {
  id: string;
  member_id: string;
  chair_reps: number;
  balance_stage: number;
  used_hands: boolean;
  strength_age: number;
  age_at_test: number;
  extra: Record<string, number | null>;
  created_at: string;
}

export type Character = "chang" | "sun";

export interface ChatMessage {
  id: string;
  member_id: string;
  character: Character;
  role: "user" | "assistant" | "system_notice";
  content: string;
  safety: string | null;
  created_at: string;
}

export interface MemoryItem {
  id: string;
  member_id: string;
  fact: string;
  sensitive: boolean;
  source: "stub" | "llm" | "member";
  created_at: string;
}

export type CrisisCategory = "self_harm" | "medical_emergency" | "abuse" | "grief";

export interface CrisisEvent {
  id: string;
  member_id: string | null;
  surface: "chat" | "dm" | "email";
  category: CrisisCategory;
  detected_by: "keyword" | "llm" | "keyword+llm" | "context" | "fail_closed";
  excerpt: string;
  alerted: boolean;
  handled_at: string | null;
  /** The member's flagged chat message, when the event came from chat. */
  chat_message_id?: string | null;
  /** The resources reply shown to the member (the one "That's not what I meant" sits under). */
  reply_message_id?: string | null;
  /** Round 7: the member tapped "That's not what I meant" after seeing the resources (the alert stays logged). */
  member_cleared_at?: string | null;
  created_at: string;
}

export interface SupportTicket {
  id: string;
  member_id: string | null;
  email: string | null;
  reason: "talk_to_human" | "crisis_followup" | "grief_followup" | "cancel_by_email" | "retest_drop" | "refund_review" | "dispute" | "privacy_request" | "chat_offline_review" | "shopify_review" | "plan_change";
  message: string;
  status: "open" | "closed";
  created_at: string;
}

export interface Partner {
  id: string;
  owner_member_id: string;
  partner_name: string;
  partner_email: string;
  share_progress: boolean;
  status: "active" | "removed";
  created_at: string;
}

export interface Gift {
  id: string;
  gifter_email: string;
  gifter_name: string;
  recipient_name: string;
  recipient_email: string;
  message: string;
  months: number;
  amount_cents: number;
  code: string;
  redeemed_member_id: string | null;
  redeemed_at: string | null;
  /** C1: redemption emails a one-time claim link to the recipient; no session from a code. */
  claim_token_hash: string | null;
  claim_expires_at: string | null;
  applied_as: "gift_membership" | "extension" | "credit" | null;
  created_at: string;
}

export interface PushSubscriptionRow {
  id: string;
  member_id: string;
  endpoint: string;
  p256dh: string;
  auth: string;
  user_agent: string | null;
  failures: number;
  last_sent_at: string | null;
  created_at: string;
}

/**
 * Round 8: a founding spot held for one checkout. Taken atomically at checkout-session
 * creation (DB advisory lock), confirmed at fulfilment, released on expiry.
 */
export interface FoundingHold {
  id: string;
  intent_id: string;
  status: "held" | "confirmed" | "released";
  expires_at: string;
  confirmed_at: string | null;
  created_at: string;
}

export interface DownloadEvent {
  id: string;
  member_id: string;
  file: string;
  order_ref: string;
  ip: string | null;
  user_agent: string | null;
  created_at: string;
}

export interface RefundLedger {
  id: string;
  email: string;
  card_fingerprint: string | null;
  member_id: string;
  membership_id: string;
  amount_cents: number;
  processor_refund_id: string | null;
  created_at: string;
}

export interface Cancellation {
  id: string;
  membership_id: string;
  member_id: string;
  reason: string | null;
  offer_shown: string | null;
  outcome: "canceled" | "saved_pause" | "saved_downgrade" | "undone";
  created_at: string;
}

export interface Reminder {
  id: string;
  membership_id: string;
  kind: "pre_charge_48h" | "annual_30d" | "ca_annual_notice" | "daily_nudge";
  charge_at: string;
  sent_at: string;
  created_at: string;
}

export interface StripeEventRow {
  id: string; // Stripe event id
  type: string;
  livemode: boolean;
  claimed_at: string | null;
  processed_at: string | null;
  error: string | null;
  summary: string | null;
  created_at: string;
}

export interface AnalyticsEvent {
  id: string;
  name: string;
  member_id: string | null;
  lead_id: string | null;
  /** Sanitised payload (no condition words, no quiz answers). */
  payload: Record<string, unknown>;
  sent_to_meta: boolean;
  created_at: string;
}

export interface OutboxMessage {
  id: string;
  channel: "email" | "sms" | "alert" | "push";
  to: string;
  subject: string | null;
  body: string;
  template: string;
  provider: string;
  status: "sent" | "stubbed" | "skipped" | "failed";
  created_at: string;
}

export interface MagicLink {
  id: string;
  token_hash: string;
  member_id: string;
  expires_at: string;
  used_at: string | null;
  /** Six-digit sign-in code sent in the same email (hashed with the member id). */
  code_hash?: string | null;
  /** Wrong code entries against this row; 5 burns it. */
  attempts?: number;
  created_at: string;
}

/** Singleton row (id "main"): the admin "Open checkout now" switch and the observed go-live time. */
export interface LaunchStateRow {
  id: string;
  opened_at: string | null;
  opened_by: string | null;
  live_seen_at: string | null;
  created_at: string;
}

export interface WaitlistEntry {
  id: string;
  /** Canonical (normalizeEmail). Unique. */
  email: string;
  first_name: string | null;
  status: "pending" | "confirmed" | "unsubscribed";
  confirm_token_hash: string | null;
  confirm_expires_at: string | null;
  /** Last time we emailed this address because of a signup (throttles resends). */
  last_signup_email_at: string | null;
  confirmed_at: string | null;
  unsubscribed_at: string | null;
  /** Asked for ad measurement on the form; applied (consent_log) only once the inbox is confirmed. */
  ad_consent_requested: boolean;
  /** The signed-visitor id at signup: carries the sticky 3-cell assignment into launch links. */
  visitor_id: string | null;
  referral_code: string;
  referred_by: string | null;
  /** When this person's referral reward (the bonus PDF) unlocked. One reward, no queue. */
  referral_reward_at: string | null;
  attribution: Attribution | null;
  member_id: string | null;
  converted_at: string | null;
  ip: string | null;
  user_agent: string | null;
  created_at: string;
}

export interface WaitlistPush {
  id: string;
  waitlist_id: string;
  endpoint: string;
  p256dh: string;
  auth: string;
  failures: number;
  created_at: string;
}

/** One row per (waitlist entry, step): the idempotency key for the launch sequence. */
export interface LaunchSend {
  id: string;
  waitlist_id: string;
  step: string;
  channel: "email" | "push";
  status: "claimed" | "sent" | "failed" | "skipped";
  sent_at: string | null;
  created_at: string;
}

export type ConversionPlatform = "meta" | "tiktok";

/** Server-side ad-platform events, deduplicated by (platform, event_id). Hashed email only. */
export interface ConversionOutboxRow {
  id: string;
  platform: ConversionPlatform;
  event_id: string;
  event_name: string;
  /** The outbound event without any access token. */
  payload: Record<string, unknown>;
  email_hash: string;
  status: "pending" | "sent" | "failed" | "skipped";
  attempts: number;
  next_attempt_at: string;
  last_error: string | null;
  sent_at: string | null;
  created_at: string;
}

/**
 * Shopify catalog → entitlement map. Shopify IDs are data, not code: one row per
 * (variant, selling plan) the store sells. Prices here mirror Shopify for display;
 * Shopify charges what Shopify charges, and nothing a visitor sends can pick a row.
 */
export type ShopifyEntitlement = "ebook" | "founding" | "standard" | "essentials" | "annual" | "gift" | "bump" | "coached";

export interface ShopifyProductRow {
  id: string;
  /** Our stable key, e.g. ebook_e12, founding_monthly, bundle_m12, gift3. */
  sku: string;
  entitlement: ShopifyEntitlement;
  title: string;
  shopify_product_id: string;
  shopify_variant_id: string;
  /** Null for one-time products; the selling plan id for subscriptions. */
  selling_plan_id: string | null;
  /** Inventory item of the variant (the founding cap is inventory on the founding plan variant). */
  inventory_item_id: string | null;
  /** Charged today. */
  price_cents: number;
  /** Every later cycle (subscriptions). */
  recurring_cents: number | null;
  interval: "month" | "year" | null;
  /** The subscription's first cycle also includes the ebook bundle (test cell B). */
  includes_ebook: boolean;
  gift_months: number | null;
  /** Front-end test cell this row serves (e7, e12, e15, m12), or null. */
  cell: string | null;
  /** founding = only while the cohort is open; standard = only after; null = always. */
  cohort: "founding" | "standard" | null;
  active: boolean;
  /**
   * Storefront product handle. /b and /join redirect to the PRODUCT PAGE (the theme's offer form adds the selling
   * plan and records consent); selling plans don't work with cart permalinks (shopify.dev "Create cart permalinks").
   */
  product_handle: string | null;
  /**
   * Cell B in the Shopify Subscriptions engine: the same (variant, selling plan) as the plain membership row plus a
   * first-payment-only discount code (STARTER12 / STARTER12S). matchLine prefers the row whose code is on the order.
   */
  discount_code: string | null;
  created_at: string;
}

/** A member asked to switch plans from the cancel flow (Shopify Subscriptions has no self-serve product swap). */
export interface PlanChangeRequest {
  id: string;
  member_id: string;
  membership_id: string | null;
  shopify_contract_id: string | null;
  from_plan: string;
  to_plan: "essentials" | "annual";
  status: "open" | "done" | "declined" | "failed";
  method: "admin_api" | "human_queue";
  note: string | null;
  created_at: string;
  resolved_at: string | null;
}

/** One row per delivered Shopify webhook id (idempotency + audit log). */
export interface ShopifyWebhookRow {
  id: string;
  topic: string;
  status: "processing" | "processed" | "ignored";
  summary: string | null;
  processed_at: string | null;
  created_at: string;
}

/** DB mirror of Shopify inventory (inventory_levels/update), per item and location. */
export interface ShopifyInventoryRow {
  id: string;
  inventory_item_id: string;
  location_id: string;
  available: number;
  shopify_updated_at: string;
  created_at: string;
}

/** refunds/create that arrived before its orders/paid (Round 5 audit). Consulted by orders/paid. */
export interface ShopifyEarlyRefundRow {
  id: string;
  shopify_order_id: string;
  shopify_line_id: string;
  shopify_refund_id: string | null;
  amount_cents: number | null;
  restock_type: string | null;
  created_at: string;
}

/** Founding seat ledger: one row per inventory adjustment reference (idempotent across redelivered webhooks). */
export interface ShopifySeatLedgerRow {
  id: string;
  ref: string;
  delta: number;
  shopify_order_id: string | null;
  created_at: string;
}

/* ------------------------------------------------------------------ ops: exceptions queue */

export type ExceptionType =
  | "compliance_flag"
  | "judge_disagreement"
  | "upload_auth_failure"
  | "refund_review"
  | "chargeback_review"
  | "plan_switch_request"
  | "consent_price_mismatch"
  | "crisis_escalation"
  | "boost_approval"
  | "affiliate_application"
  | "affiliate_fraud"
  | "coach_flag"
  | "clinical_interest";

export type ExceptionStatus = "open" | "approved" | "rejected" | "resolved";

/** One item a person must look at. Workers post them (POST /api/exceptions); the app raises its own. */
export interface ExceptionRow {
  id: string;
  type: ExceptionType;
  status: ExceptionStatus;
  severity: "low" | "normal" | "high" | "critical";
  source: string;
  title: string;
  detail: string;
  /** What the item is about (post id, boost id, order id, affiliate id). Never an email or a message body. */
  ref: string | null;
  /** Idempotency: the same (type, dedupe_key) is one item, however often a worker posts it. */
  dedupe_key: string;
  payload: Record<string, unknown>;
  decided_by: string | null;
  decided_at: string | null;
  decision_note: string | null;
  created_at: string;
}

/** Append-only audit trail for exceptions. */
export interface ExceptionEvent {
  id: string;
  exception_id: string;
  action: "created" | "repeated" | "approve" | "reject" | "resolve";
  actor: string;
  note: string | null;
  created_at: string;
}

/** The governor's human-approval record for one boost, written when a person approves it in /admin/exceptions. */
export interface GovernorApproval {
  id: string;
  boost_id: string;
  exception_id: string;
  approved_by: string;
  approved_at: string;
  max_daily_usd: number;
  forwarded: "pending" | "sent" | "failed" | "not_configured";
  created_at: string;
}

/** One row per digest day: the 7am digest is sent once. */
export interface DigestRun {
  id: string;
  day: string;
  status: "claimed" | "sent" | "failed";
  sent_at: string | null;
  created_at: string;
}

/* ------------------------------------------------------------------ lifecycle email */

/** One row per (recipient, sequence, step): the idempotency key of the lifecycle engine. */
export interface EmailSend {
  id: string;
  email: string;
  member_id: string | null;
  sequence: string;
  step: string;
  status: "claimed" | "sent" | "skipped" | "failed";
  reason: string | null;
  sent_at: string | null;
  created_at: string;
}

/** Marketing / lifecycle email consent per address. Transactional mail ignores it; lifecycle mail never does. */
export interface EmailPref {
  id: string;
  email: string;
  lifecycle_opt_in: boolean;
  coach_opt_in: boolean;
  unsubscribed_at: string | null;
  source: string;
  created_at: string;
}

/* ------------------------------------------------------------------ affiliates */

export interface Affiliate {
  id: string;
  email: string;
  name: string;
  /** Where they will post (URL or handle). */
  channel: string;
  audience_note: string;
  /** The code on links (/go?ref=CODE) and the Shopify discount code. Set on approval. */
  code: string | null;
  status: "pending" | "approved" | "rejected" | "suspended";
  ftc_ack: boolean;
  terms_version: string;
  member_id: string | null;
  exception_id: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
}

/** A referred customer: commissions accrue on their membership charges for 12 months from started_at. */
export interface AffiliateReferral {
  id: string;
  affiliate_id: string;
  member_id: string;
  via: "code" | "link";
  started_at: string;
  ends_at: string;
  first_order_id: string;
  created_at: string;
}

export interface AffiliateCommission {
  id: string;
  affiliate_id: string;
  referral_id: string;
  sy_order_id: string;
  shopify_line_id: string | null;
  base_cents: number;
  commission_cents: number;
  paid_at: string;
  /** Payable after the 14-day money-back window. */
  payable_after: string;
  created_at: string;
}

/* ------------------------------------------------------------------ ascension ladder (ASCENSION.md, CANON UPDATE 4) */

/** R3: one coached group. The cap is honest: seats = active enrollments, counted from this DB. */
export interface CoachCohort {
  id: string;
  name: string;
  /** Null until a coach is hired; the page shows a placeholder and sells nothing. */
  coach_name: string | null;
  coach_credential: string | null;
  coach_bio: string | null;
  cap: number;
  status: "draft" | "open" | "running" | "closed";
  starts_on: string | null;
  /** Weekly group call (video link) and its plain-words time, shown only to enrolled members. */
  call_url: string | null;
  call_time: string | null;
  created_at: string;
}

export interface CoachedEnrollment {
  id: string;
  member_id: string;
  cohort_id: string;
  status: "active" | "ended" | "refunded";
  /** Catalog sku the seat was bought on (coached_monthly, coached_97, coached_197). */
  sku: string;
  /** The FIRST coached order: one seat per order, replay-safe. */
  shopify_order_id: string;
  started_at: string;
  /** Extended by one month per paid coached order (renewals included). */
  paid_through: string;
  created_at: string;
}

export interface CoachCheckin {
  id: string;
  enrollment_id: string;
  member_id: string;
  cohort_id: string;
  week: number;
  sessions_done: number;
  /** 1 (very easy) to 5 (very hard). */
  effort: number;
  /** "Something hurt or worried me": goes to the coach, and to the exceptions queue as a coach_flag. */
  concern: boolean;
  win: string;
  question: string;
  created_at: string;
}

export interface CoachNote {
  id: string;
  enrollment_id: string;
  member_id: string;
  author: string;
  body: string;
  visible_to_member: boolean;
  created_at: string;
}

/** R4: interest capture only. Name, email, state, consent; filed to the exceptions queue for the client's clinical team. */
export interface ClinicalInterest {
  id: string;
  member_id: string | null;
  name: string;
  email: string;
  state: string;
  consent: boolean;
  consent_text: string;
  exception_id: string | null;
  status: "new" | "sent_to_clinical_team" | "closed";
  created_at: string;
}

/** Every time an in-app trigger showed a rung offer (honest measurement of the ladder). */
export interface AscensionExposure {
  id: string;
  member_id: string;
  rung: "R3" | "R4" | "R5";
  triggers: string[];
  cell: string | null;
  day: string;
  created_at: string;
}

export interface Rows {
  members: Member;
  memberships: Membership;
  sy_orders: Order;
  checkout_intents: CheckoutIntent;
  consent_log: ConsentRecord;
  leads: Lead;
  practice_logs: PracticeLog;
  retests: Retest;
  chat_messages: ChatMessage;
  memory_items: MemoryItem;
  crisis_events: CrisisEvent;
  support_tickets: SupportTicket;
  partners: Partner;
  gifts: Gift;
  cancellations: Cancellation;
  reminders: Reminder;
  stripe_events: StripeEventRow;
  analytics_events: AnalyticsEvent;
  outbox: OutboxMessage;
  magic_links: MagicLink;
  refund_ledger: RefundLedger;
  push_subscriptions: PushSubscriptionRow;
  download_events: DownloadEvent;
  founding_holds: FoundingHold;
  launch_state: LaunchStateRow;
  waitlist: WaitlistEntry;
  waitlist_push: WaitlistPush;
  launch_sends: LaunchSend;
  conversion_outbox: ConversionOutboxRow;
  shopify_products: ShopifyProductRow;
  plan_change_requests: PlanChangeRequest;
  shopify_webhooks: ShopifyWebhookRow;
  shopify_inventory: ShopifyInventoryRow;
  shopify_early_refunds: ShopifyEarlyRefundRow;
  shopify_seat_ledger: ShopifySeatLedgerRow;
  exceptions: ExceptionRow;
  exception_events: ExceptionEvent;
  governor_approvals: GovernorApproval;
  digest_runs: DigestRun;
  email_sends: EmailSend;
  email_prefs: EmailPref;
  affiliates: Affiliate;
  affiliate_referrals: AffiliateReferral;
  affiliate_commissions: AffiliateCommission;
  coach_cohorts: CoachCohort;
  coached_enrollments: CoachedEnrollment;
  coach_checkins: CoachCheckin;
  coach_notes: CoachNote;
  clinical_interest: ClinicalInterest;
  ascension_exposures: AscensionExposure;
}

export type TableName = keyof Rows;
