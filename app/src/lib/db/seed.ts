/**
 * Demo data for mock mode only (never runs against Supabase). Every row is flagged
 * is_demo so it can never be mistaken for real members, and the UI shows a
 * "demo mode" banner whenever the in-memory store is in use.
 */
import { computeStrengthAgeNumber } from "../quiz/strengthAge";
import type { Store } from "./store";
import type { Arm, Member, Membership, Track } from "./types";
import { isShopify } from "../billing/provider";
import { seedShopifyCatalog } from "../billing/shopify";

export const DEMO_EMAIL = "demo@strongyears.example";

const day = 86_400_000;
const iso = (msAgo: number) => new Date(Date.now() - msAgo).toISOString();
const ymd = (msAgo: number) => new Date(Date.now() - msAgo).toISOString().slice(0, 10);

async function member(store: Store, email: string, first: string, track: Track, extra: Partial<Member> = {}) {
  return store.insert("members", {
    email,
    first_name: first,
    phone: null,
    sex: "woman",
    age: 71,
    age_confirmed_at: iso(40 * day),
    track,
    active_program: null,
    program_started_at: null,
    sms_opt_in: false,
    reminder_channel: "email",
    reminder_time: "07:30",
    timezone: "America/Los_Angeles",
    memory_enabled: false,
    stripe_customer_id: `cus_mock_${first.toLowerCase()}`,
    stripe_payment_method: "pm_mock_visa",
    attribution: { utm_source: "ig", utm_medium: "dm", utm_campaign: "strong" },
    protected_weeks: [],
    is_demo: true,
    email_verified_at: iso(40 * day),
    created_at: iso(40 * day),
    ...extra,
  });
}

async function membership(store: Store, memberId: string, arm: Arm | null, patch: Partial<Membership>) {
  const row = await store.insert("memberships", {
    member_id: memberId,
    plan: "monthly",
    arm,
    offer_code: arm === "B" ? "founding" : "trial",
    price_cents: 2000,
    interval: "month",
    status: "active",
    founding: arm === "B",
    stripe_subscription_id: `sub_mock_${memberId.slice(0, 8)}`,
    trial_end: null,
    current_period_end: iso(-12 * day),
    first_paid_at: iso(18 * day),
    guarantee_until: null,
    cancel_at_period_end: false,
    canceled_at: null,
    paused_until: null,
    partner_seat: false,
    processor: "stripe",
    price_cell: arm === "B" ? "p2500" : null,
    checkout_intent_id: null,
    gift_credit_cents: 0,
    is_demo: true,
    ...patch,
  });
  lastMembershipId = row.id;
  return row;
}

let lastMembershipId: string | null = null;

async function order(store: Store, memberId: string, email: string, kind: "trial_fee" | "membership_charge" | "bump" | "front_end" | "gift", cents: number, msAgo: number, status: "paid" | "refunded" = "paid", sku?: string) {
  return store.insert("sy_orders", {
    member_id: memberId,
    membership_id: lastMembershipId,
    amount_refunded_cents: status === "refunded" ? cents : 0,
    email,
    offer_code: sku ?? kind,
    kind,
    description: `demo ${kind}`,
    amount_cents: cents,
    status,
    stripe_payment_intent: `pi_mock_${crypto.randomUUID().slice(0, 10)}`,
    stripe_invoice: null,
    checkout_intent_id: null,
    processor: "stripe",
    is_demo: true,
    created_at: iso(msAgo),
  });
}

export async function seedDemoData(store: Store) {
  if ((await store.count("members")) > 0) return;
  await seedShopifyCatalog(store);
  const shop = isShopify();

  // The demo member used by "Enter the demo member area".
  const pat = await member(store, DEMO_EMAIL, "Pat", "steady", {
    memory_enabled: true,
    active_program: "strong-at-70",
    program_started_at: iso(20 * day),
    sms_opt_in: true,
    phone: "+15555550123",
    reminder_channel: "sms",
  });
  await membership(store, pat.id, "B", {
    ...(shop ? { processor: "shopify" as const, offer_code: "founding_monthly", stripe_subscription_id: null, shopify_contract_id: "5550000001", shopify_origin_order_id: "6660000001", shopify_customer_id: "4440000001", price_cell: "m12" } : {}),
    price_cents: 2500,
    first_paid_at: iso(18 * day),
    current_period_end: iso(-12 * day),
    guarantee_until: iso(4 * day),
    created_at: iso(18 * day),
  });
  await order(store, pat.id, pat.email, "membership_charge", 2500, 18 * day);
  await order(store, pat.id, pat.email, "bump", 700, 18 * day, "paid", "reset");
  await order(store, pat.id, pat.email, "bump", 900, 18 * day, "paid", "wallplan");

  // ~5 weeks of practice: 3–4 sessions most weeks, one light week.
  const pattern = [1, 2, 4, 6, 8, 9, 11, 13, 15, 16, 18, 22, 23, 25, 27, 29, 30, 32, 34];
  for (const d of pattern) {
    await store.insert("practice_logs", { member_id: pat.id, day: ymd(d * day), session_key: `demo-${d}`, track: "steady", swap: null, minutes: 9, created_at: iso(d * day) });
  }
  // Strength Age history: quiz baseline, then monthly retests.
  const tests = [
    { ago: 62, reps: 10, stage: 2 },
    { ago: 32, reps: 12, stage: 3 },
    { ago: 2, reps: 13, stage: 3 },
  ];
  for (const t of tests) {
    await store.insert("retests", {
      member_id: pat.id,
      chair_reps: t.reps,
      balance_stage: t.stage,
      used_hands: false,
      age_at_test: 71,
      strength_age: computeStrengthAgeNumber({ age: 71, sex: "woman", chairReps: t.reps, usedHands: false, balanceStage: t.stage, selfReport: 0 }),
      extra: { step_test: null, arm_curl: null, sit_reach: null, up_and_go: null },
      created_at: iso(t.ago * day),
    });
  }
  await store.insert("memory_items", { member_id: pat.id, fact: "Has a grandson named Leo", sensitive: false, source: "member" });
  await store.insert("memory_items", { member_id: pat.id, fact: "Mentioned a sore left knee on stairs", sensitive: true, source: "member" });
  await store.insert("chat_messages", { member_id: pat.id, character: "chang", role: "assistant", content: "Morning, Pat. Legs today. Chair against the wall. Same time tomorrow.", safety: null, created_at: iso(1 * day) });

  // A small, clearly-labelled demo population for the admin dashboard.
  const names = ["Ruth", "Walt", "June", "Harold", "Mae", "Frank", "Irene", "Glen", "Doris", "Ray", "Lou", "Bev"];
  for (const [i, name] of names.entries()) {
    const post = ["DEMO_IG_REEL_01", "DEMO_TT_02", "DEMO_IG_REEL_01", "DEMO_YT_03"][i % 4]!;
    const m = await member(store, `${name.toLowerCase()}@demo.strongyears.example`, name, i % 2 ? "rebuild" : "steady", {
      attribution: { platform: post.includes("TT") ? "tt" : post.includes("YT") ? "yt" : "ig", page: "changyin.strong", post_id: post, keyword: "JOIN", character: "chang", utm_source: "ig", utm_medium: "bio" },
    });
    if (i < 3) {
      // No $1 trial (CANON UPDATE 2): these demo rows are failed renewals inside the grace period.
      await membership(store, m.id, "B", { status: "past_due", founding: true, grace_until: iso(-(i + 2) * day), current_period_end: iso((i + 1) * day) });
      await order(store, m.id, m.email, "membership_charge", 2500, 32 * day);
    } else if (i < 6) {
      await membership(store, m.id, "A", { trial_end: iso(20 * day), first_paid_at: iso(20 * day), guarantee_until: iso(-10 * day) });
      await order(store, m.id, m.email, "trial_fee", 100, 27 * day);
      await order(store, m.id, m.email, "membership_charge", 2000, 20 * day);
    } else if (i < 9) {
      await membership(store, m.id, "B", { guarantee_until: iso(-2 * day) });
      await order(store, m.id, m.email, "membership_charge", 2000, 16 * day);
    } else if (i === 9) {
      await membership(store, m.id, "B", { cancel_at_period_end: true, canceled_at: iso(3 * day) });
      await order(store, m.id, m.email, "membership_charge", 2000, 25 * day);
      await store.insert("cancellations", { membership_id: m.id, member_id: m.id, reason: "no_time", offer_shown: "pause", outcome: "canceled" });
    } else if (i === 10) {
      await membership(store, m.id, "B", { status: "refunded", founding: true, canceled_at: iso(5 * day) });
      await order(store, m.id, m.email, "membership_charge", 2000, 9 * day, "refunded");
    } else {
      await membership(store, m.id, "A", { status: "paused", paused_until: iso(-30 * day) });
      await store.insert("cancellations", { membership_id: m.id, member_id: m.id, reason: "traveling", offer_shown: "pause", outcome: "saved_pause" });
    }
  }

  // Demo waitlist (prelaunch dashboard), flagged by the .example addresses.
  const wl = [
    ["DEMO_IG_REEL_01", "confirmed"],
    ["DEMO_IG_REEL_01", "confirmed"],
    ["DEMO_TT_02", "confirmed"],
    ["DEMO_TT_02", "pending"],
    ["DEMO_YT_03", "confirmed"],
    ["DEMO_IG_REEL_01", "unsubscribed"],
  ] as const;
  for (const [i, [post, status]] of wl.entries()) {
    await store.insert("waitlist", {
      email: `waitlist${i + 1}@demo.strongyears.example`,
      first_name: null,
      status,
      confirm_token_hash: null,
      confirm_expires_at: null,
      last_signup_email_at: iso((10 - i) * day),
      confirmed_at: status === "pending" ? null : iso((9 - i) * day),
      unsubscribed_at: status === "unsubscribed" ? iso(2 * day) : null,
      ad_consent_requested: false,
      visitor_id: null,
      referral_code: `DEMO${"ABCDEF"[i]}234`,
      referred_by: null,
      referral_reward_at: null,
      attribution: { platform: "ig", page: "changyin.strong", post_id: post, keyword: "STRONG", character: "chang" },
      member_id: null,
      converted_at: null,
      ip: null,
      user_agent: null,
      created_at: iso((10 - i) * day),
    });
  }
}
