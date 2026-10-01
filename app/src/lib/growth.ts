/**
 * Post-level results for the growth engine and /admin: opt-ins, members and MRR per
 * post_id, under first-touch and last-touch credit. Aggregates only: no emails, no
 * names, no answers, no ids of people. MRR uses the same rule as the admin
 * (lib/members.ts mrrCents: paying, not scheduled to cancel, gifts excluded).
 */
import { postKey } from "./analytics/attribution";
import type { Store } from "./db/store";
import type { Attribution, Membership } from "./db/types";
import { mrrCents } from "./members";

export interface PostRow {
  post_id: string;
  platform: string | null;
  page: string | null;
  character: string | null;
  keywords: string[];
  waitlist_signups: number;
  waitlist_confirmed: number;
  quiz_optins: number;
  /** Bought the starter books (alone or in the "$12 = books + first month" bundle). */
  ebook_buyers: number;
  members: number;
  paying_members: number;
  mrr_cents: number;
}

export interface GrowthReport {
  generated_at: string;
  mrr_rule: string;
  first_touch: PostRow[];
  last_touch: PostRow[];
  unattributed: { waitlist_confirmed: number; members: number; mrr_cents: number };
  totals: { waitlist_confirmed: number; ebook_buyers: number; members: number; mrr_cents: number };
}

type Touch = "first" | "last";

function emptyRow(k: NonNullable<ReturnType<typeof postKey>>): PostRow {
  return { post_id: k.post_id, platform: k.platform, page: k.page, character: k.character, keywords: [], waitlist_signups: 0, waitlist_confirmed: 0, quiz_optins: 0, ebook_buyers: 0, members: 0, paying_members: 0, mrr_cents: 0 };
}

export async function growthReport(store: Store, now = new Date()): Promise<GrowthReport> {
  const [waitlist, leads, members, memberships, orders] = await Promise.all([store.find("waitlist"), store.find("leads"), store.find("members", { is_demo: false }), store.find("memberships"), store.find("sy_orders", { status: "paid" })]);
  const ebookSkus = new Set((await store.find("shopify_products", { includes_ebook: true })).map((r) => r.sku));
  const bookBuyers = new Set(orders.filter((o) => o.member_id && (o.kind === "front_end" || ebookSkus.has(o.offer_code))).map((o) => o.member_id!));
  const byMember = new Map<string, Membership[]>();
  for (const m of memberships) if (m.plan !== "gift") byMember.set(m.member_id, [...(byMember.get(m.member_id) ?? []), m]);

  const build = (touch: Touch) => {
    const rows = new Map<string, PostRow>();
    const bump = (a: Attribution | null | undefined, fn: (r: PostRow) => void) => {
      const k = postKey(a, touch);
      if (!k) return false;
      const row = rows.get(k.post_id) ?? emptyRow(k);
      if (k.keyword && !row.keywords.includes(k.keyword) && row.keywords.length < 10) row.keywords.push(k.keyword);
      row.platform ??= k.platform;
      row.page ??= k.page;
      row.character ??= k.character;
      fn(row);
      rows.set(k.post_id, row);
      return true;
    };
    for (const w of waitlist) {
      bump(w.attribution, (r) => {
        r.waitlist_signups++;
        if (w.status === "confirmed" || w.confirmed_at) r.waitlist_confirmed++;
      });
    }
    for (const l of leads) bump(l.attribution, (r) => r.quiz_optins++);
    for (const m of members) {
      const ms = byMember.get(m.id) ?? [];
      if (bookBuyers.has(m.id)) bump(m.attribution, (r) => r.ebook_buyers++);
      if (ms.length === 0) continue;
      const mrr = ms.reduce((s, x) => s + mrrCents(x), 0);
      const paying = ms.some((x) => x.status === "active" || x.status === "past_due");
      bump(m.attribution, (r) => {
        r.members++;
        if (paying) r.paying_members++;
        r.mrr_cents += mrr;
      });
    }
    return [...rows.values()].sort((a, b) => b.mrr_cents - a.mrr_cents || b.members - a.members || b.waitlist_confirmed - a.waitlist_confirmed || a.post_id.localeCompare(b.post_id));
  };

  let unWl = 0;
  let unMembers = 0;
  let unMrr = 0;
  let totWl = 0;
  let totMembers = 0;
  let totMrr = 0;
  for (const w of waitlist) {
    if (!(w.status === "confirmed" || w.confirmed_at)) continue;
    totWl++;
    if (!postKey(w.attribution, "first")) unWl++;
  }
  for (const m of members) {
    const ms = byMember.get(m.id) ?? [];
    if (ms.length === 0) continue;
    const mrr = ms.reduce((s, x) => s + mrrCents(x), 0);
    totMembers++;
    totMrr += mrr;
    if (!postKey(m.attribution, "first")) {
      unMembers++;
      unMrr += mrr;
    }
  }
  return {
    generated_at: now.toISOString(),
    mrr_rule: "active or past_due, not cancelling at period end, gifts excluded, annual / 12, partner seat included",
    first_touch: build("first"),
    last_touch: build("last"),
    unattributed: { waitlist_confirmed: unWl, members: unMembers, mrr_cents: unMrr },
    totals: { waitlist_confirmed: totWl, ebook_buyers: members.filter((m) => bookBuyers.has(m.id)).length, members: totMembers, mrr_cents: totMrr },
  };
}

export interface LaunchKpis {
  waitlist: { pending: number; confirmed: number; unsubscribed: number; withPush: number; referralRewards: number };
  /** Confirmed waitlisters who became members / confirmed waitlisters. */
  postLaunch: { converted: number; conversion: number | null };
  sends: { email: number; push: number; failed: number };
  conversions: { pending: number; sent: number; failed: number; skipped: number };
}

export async function launchKpis(store: Store): Promise<LaunchKpis> {
  const wl = await store.find("waitlist");
  const confirmed = wl.filter((w) => w.status === "confirmed" || (w.status === "unsubscribed" && w.confirmed_at));
  const converted = wl.filter((w) => w.confirmed_at && w.converted_at).length;
  const sends = await store.find("launch_sends");
  const conv = await store.find("conversion_outbox");
  const pushOwners = new Set((await store.find("waitlist_push")).map((p) => p.waitlist_id));
  return {
    waitlist: {
      pending: wl.filter((w) => w.status === "pending").length,
      confirmed: wl.filter((w) => w.status === "confirmed").length,
      unsubscribed: wl.filter((w) => w.status === "unsubscribed").length,
      withPush: pushOwners.size,
      referralRewards: wl.filter((w) => w.referral_reward_at).length,
    },
    postLaunch: { converted, conversion: confirmed.length ? converted / confirmed.length : null },
    sends: {
      email: sends.filter((s) => s.channel === "email" && s.status === "sent").length,
      push: sends.filter((s) => s.channel === "push" && s.status === "sent").length,
      failed: sends.filter((s) => s.status === "failed").length,
    },
    conversions: {
      pending: conv.filter((c) => c.status === "pending").length,
      sent: conv.filter((c) => c.status === "sent").length,
      failed: conv.filter((c) => c.status === "failed").length,
      skipped: conv.filter((c) => c.status === "skipped").length,
    },
  };
}
