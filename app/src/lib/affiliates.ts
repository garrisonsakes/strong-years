/**
 * Affiliates: 30% of what a referred customer pays for 12 months from their first
 * order, a 60-day link window, no self-referral, FTC disclosure required.
 *
 * - Apply at /affiliates → an `affiliates` row (pending) + an `affiliate_application`
 *   exception. A person approves it in /admin/exceptions; approval assigns the code.
 * - The code works two ways: on links (/go?ref=CODE, /b?ref=CODE → utm_source=affiliate,
 *   utm_campaign=CODE, carried into the Shopify order's attributes) and as a Shopify
 *   discount code with exactly the public starter terms (the buyer's price never
 *   changes because of an affiliate; created by a person, see the approval note).
 * - orders/paid → creditAffiliateOrder(): first order opens a 12-month referral,
 *   every paid line in the window (renewals included, gifts excluded) earns 30%,
 *   payable after the 14-day money-back window; refunded or disputed lines are
 *   reversed on the statement. Fraud checks raise `affiliate_fraud` exceptions.
 */
import type { Store } from "./db/store";
import type { Affiliate, AffiliateCommission, Attribution, ExceptionRow } from "./db/types";
import { raiseException } from "./exceptions";
import { normalizeEmail } from "./members";
import { addDays, addMonths } from "./pricing";

export const COMMISSION_RATE = 0.3;
export const COMMISSION_MONTHS = 12;
export const LINK_WINDOW_DAYS = 60;
export const HOLD_DAYS = 14;
export const VELOCITY_LIMIT_24H = 25;
export const TERMS_VERSION = "2026-10-01-draft";
export const FTC_LINE = "I'm a Strong Years affiliate and earn a commission if you join through my link or code. Your price is the same either way.";

const CODE_RX = /^[A-Z0-9]{4,20}$/;
/**
 * Round 6: Shopify discount codes the store already owns (shopify/config/catalog.ts). An affiliate code is
 * matched against the order's discount codes, so a code that collides with (or merely starts like) a system
 * code would credit every cell-B / page / win-back order to that affiliate. Never allocate one of these.
 */
export const RESERVED_CODE_STEMS = ["STARTER", "WINBACK", "GROUP", "CHANG", "SUNYOON", "CHANGANDSUN", "FAMILY", "JOIN", "BOOK"] as const;
export function isReservedCode(code: string): boolean {
  const c = code.toUpperCase();
  return RESERVED_CODE_STEMS.some((stem) => c === stem || c.startsWith(stem));
}

export function cleanRef(raw: unknown): string | null {
  const v = typeof raw === "string" ? raw.trim().toUpperCase() : "";
  return CODE_RX.test(v) ? v : null;
}

export interface ApplyInput {
  email: string;
  name: string;
  channel: string;
  audience: string;
  ftcAck: boolean;
  termsAck: boolean;
}

export type ApplyResult = { ok: true; affiliate: Affiliate; created: boolean } | { ok: false; errors: string[] };

export async function applyAffiliate(store: Store, input: ApplyInput): Promise<ApplyResult> {
  const errors: string[] = [];
  const email = normalizeEmail(input.email ?? "");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) errors.push("email");
  const name = (input.name ?? "").replace(/[<>\u0000-\u001F]/g, "").trim().slice(0, 80);
  if (name.length < 2) errors.push("name");
  const channel = (input.channel ?? "").replace(/[<>\u0000-\u001F]/g, "").trim().slice(0, 200);
  if (channel.length < 3) errors.push("channel");
  if (!input.ftcAck) errors.push("ftc");
  if (!input.termsAck) errors.push("terms");
  if (errors.length) return { ok: false, errors };
  const existing = await store.findOne("affiliates", { email });
  if (existing) return { ok: true, affiliate: existing, created: false };
  const member = await store.findOne("members", { email });
  const affiliate = await store.insert("affiliates", {
    email,
    name,
    channel,
    audience_note: (input.audience ?? "").replace(/[<>\u0000-\u001F]/g, "").trim().slice(0, 600),
    code: null,
    status: "pending",
    ftc_ack: true,
    terms_version: TERMS_VERSION,
    member_id: member?.id ?? null,
    exception_id: null,
    approved_by: null,
    approved_at: null,
  });
  const { row } = await raiseException(store, {
    type: "affiliate_application",
    title: `Affiliate application: ${name}`,
    detail: `Channel: ${channel}\nAudience: ${affiliate.audience_note || "(not given)"}\nFTC disclosure acknowledged. Terms ${TERMS_VERSION}.`,
    ref: affiliate.id,
    source: "app:affiliates",
    dedupe_key: `affiliate:${affiliate.id}`,
  });
  await store.update("affiliates", affiliate.id, { exception_id: row.id });
  return { ok: true, affiliate: { ...affiliate, exception_id: row.id }, created: true };
}

export async function uniqueCode(store: Store, name: string): Promise<string> {
  let stem = name.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 8).padEnd(4, "X");
  if (isReservedCode(stem)) stem = `AF${stem.slice(0, 6)}`;
  for (let i = 0; i < 50; i++) {
    const code = `${stem}${String(10 + Math.floor(Math.random() * 90))}`;
    if (isReservedCode(code)) continue;
    if (!(await store.findOne("affiliates", { code }))) return code;
  }
  throw new Error("could not allocate an affiliate code");
}

/** Called by decideException for affiliate_application items. */
export async function onAffiliateDecision(store: Store, exc: ExceptionRow, decision: "approve" | "reject" | "resolve", actor: string, now = new Date()): Promise<string[]> {
  if (!exc.ref) return [];
  const a = await store.get("affiliates", exc.ref);
  if (!a || a.status !== "pending") return [];
  if (decision !== "approve") {
    await store.update("affiliates", a.id, { status: "rejected" });
    return [`affiliate ${a.name} rejected`];
  }
  const code = await uniqueCode(store, a.name);
  await store.update("affiliates", a.id, { status: "approved", code, approved_by: actor, approved_at: now.toISOString() });
  return [
    `affiliate ${a.name} approved with code ${code}; link: /go?ref=${code}`,
    `Shopify (a person, once): Discounts → Amount off products → code ${code}: $13 off Founding Membership, subscription purchases, first payment only, once per customer (the same terms as STARTER12, so the buyer's price is the public price).`,
  ];
}

export interface CreditInput {
  memberId: string;
  email: string;
  shopifyOrderId: string;
  discountCodes: string[];
  attribution: Attribution | null;
  renewal: boolean;
  paidAt: Date;
}

function linkRef(a: Attribution | null, paidAt: Date): string | null {
  if (!a) return null;
  const within = (iso: string | undefined) => !!iso && paidAt.getTime() - new Date(iso).getTime() <= LINK_WINDOW_DAYS * 86_400_000 && new Date(iso).getTime() <= paidAt.getTime() + 60_000;
  const lt = a.last_touch;
  if (lt?.utm_source === "affiliate" && within(lt.at)) return cleanRef(lt.utm_campaign);
  if (a.utm_source === "affiliate" && within(a.first_seen_at)) return cleanRef(a.utm_campaign);
  return null;
}

/** Commission for one order. Idempotent per sy_orders row (unique sy_order_id). Never throws. */
export async function creditAffiliateOrder(store: Store, x: CreditInput): Promise<{ commissions: number; reason?: string }> {
  try {
    let referral = await store.findOne("affiliate_referrals", { member_id: x.memberId });
    if (!referral) {
      if (x.renewal) return { commissions: 0, reason: "renewal without referral" };
      const codes = x.discountCodes.map((c) => cleanRef(c)).filter((c): c is string => !!c && !isReservedCode(c));
      let affiliate: Affiliate | null = null;
      let via: "code" | "link" = "code";
      for (const c of codes) {
        affiliate = await store.findOne("affiliates", { code: c, status: "approved" });
        if (affiliate) break;
      }
      if (!affiliate) {
        const ref = linkRef(x.attribution, x.paidAt);
        if (ref) {
          affiliate = await store.findOne("affiliates", { code: ref, status: "approved" });
          via = "link";
        }
      }
      if (!affiliate) return { commissions: 0, reason: "no affiliate" };
      if (affiliate.email === normalizeEmail(x.email) || (affiliate.member_id && affiliate.member_id === x.memberId)) {
        await raiseException(store, {
          type: "affiliate_fraud",
          title: `Self-referral blocked (${affiliate.code})`,
          detail: `Order ${x.shopifyOrderId} was placed by the affiliate's own account. No commission was recorded.`,
          ref: affiliate.id,
          severity: "high",
          source: "app:affiliates",
          dedupe_key: `self:${affiliate.id}:${x.shopifyOrderId}`,
        });
        return { commissions: 0, reason: "self-referral" };
      }
      try {
        referral = await store.insert("affiliate_referrals", {
          affiliate_id: affiliate.id,
          member_id: x.memberId,
          via,
          started_at: x.paidAt.toISOString(),
          ends_at: addMonths(x.paidAt, COMMISSION_MONTHS).toISOString(),
          first_order_id: x.shopifyOrderId,
        });
      } catch {
        referral = await store.findOne("affiliate_referrals", { member_id: x.memberId });
        if (!referral) return { commissions: 0, reason: "referral race" };
      }
      await velocityCheck(store, affiliate, x.paidAt);
    }
    if (x.paidAt.getTime() >= new Date(referral.ends_at).getTime()) return { commissions: 0, reason: "outside 12 months" };
    const lines = await store.find("sy_orders", { shopify_order_id: x.shopifyOrderId, member_id: x.memberId });
    let n = 0;
    for (const o of lines) {
      if (o.kind === "gift" || o.status !== "paid" || o.amount_cents <= 0) continue;
      try {
        await store.insert("affiliate_commissions", {
          affiliate_id: referral.affiliate_id,
          referral_id: referral.id,
          sy_order_id: o.id,
          shopify_line_id: o.shopify_line_id ?? null,
          base_cents: o.amount_cents,
          commission_cents: Math.floor(o.amount_cents * COMMISSION_RATE),
          paid_at: x.paidAt.toISOString(),
          payable_after: addDays(x.paidAt, HOLD_DAYS).toISOString(),
        });
        n++;
      } catch {
        // already credited (webhook replay)
      }
    }
    return { commissions: n };
  } catch (err) {
    console.error("affiliate credit failed", (err as Error).message);
    return { commissions: 0, reason: "error" };
  }
}

async function velocityCheck(store: Store, a: Affiliate, now: Date) {
  const since = new Date(now.getTime() - 86_400_000).toISOString();
  const recent = await store.count("affiliate_referrals", { affiliate_id: a.id, started_at: { gte: since } });
  if (recent > VELOCITY_LIMIT_24H) {
    await raiseException(store, {
      type: "affiliate_fraud",
      title: `Unusual referral volume (${a.code}): ${recent} in 24 hours`,
      detail: `Check for cookie stuffing, incentivised sign-ups or coupon-site leakage before the next statement.`,
      ref: a.id,
      severity: "high",
      source: "app:affiliates",
      dedupe_key: `velocity:${a.id}:${now.toISOString().slice(0, 10)}`,
    });
  }
}

export interface StatementLine {
  affiliate_code: string;
  affiliate_name: string;
  shopify_order_id: string;
  paid_at: string;
  base_cents: number;
  commission_cents: number;
  state: "payable" | "held" | "reversed";
}

/** Lines whose commission was earned in `month` (YYYY-MM, UTC). Refunded/disputed lines are reversed (0). */
export async function monthlyStatement(store: Store, month: string, now = new Date()): Promise<StatementLine[]> {
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(month)) throw new Error("month must be YYYY-MM");
  const start = new Date(`${month}-01T00:00:00Z`);
  const end = addMonths(start, 1);
  const rows: AffiliateCommission[] = await store.find("affiliate_commissions", { paid_at: { gte: start.toISOString(), lt: end.toISOString() } });
  const out: StatementLine[] = [];
  for (const c of rows) {
    const a = await store.get("affiliates", c.affiliate_id);
    const o = await store.get("sy_orders", c.sy_order_id);
    const reversed = !o || o.status === "refunded" || o.status === "disputed" || o.status === "refund_pending";
    const state: StatementLine["state"] = reversed ? "reversed" : new Date(c.payable_after) <= now ? "payable" : "held";
    out.push({
      affiliate_code: a?.code ?? "?",
      affiliate_name: a?.name ?? "?",
      shopify_order_id: o?.shopify_order_id ?? "",
      paid_at: c.paid_at,
      base_cents: c.base_cents,
      commission_cents: reversed ? 0 : c.commission_cents,
      state,
    });
  }
  return out.sort((a, b) => a.affiliate_code.localeCompare(b.affiliate_code) || a.paid_at.localeCompare(b.paid_at));
}

const csvCell = (v: string | number) => {
  const s = String(v);
  // Spreadsheet formula injection guard + quoting.
  const safe = /^[=+\-@\t\r]/.test(s) ? `'${s}` : s;
  return /[",\n]/.test(safe) ? `"${safe.replace(/"/g, '""')}"` : safe;
};

export function statementCsv(lines: StatementLine[]): string {
  const head = ["affiliate_code", "affiliate_name", "shopify_order_id", "paid_at", "base_usd", "commission_usd", "state"];
  const body = lines.map((l) => [l.affiliate_code, l.affiliate_name, l.shopify_order_id, l.paid_at, (l.base_cents / 100).toFixed(2), (l.commission_cents / 100).toFixed(2), l.state].map(csvCell).join(","));
  const totals = new Map<string, number>();
  for (const l of lines) if (l.state === "payable") totals.set(l.affiliate_code, (totals.get(l.affiliate_code) ?? 0) + l.commission_cents);
  const foot = [...totals].map(([code, c]) => [code, "TOTAL PAYABLE", "", "", "", (c / 100).toFixed(2), "payable"].map(csvCell).join(","));
  return [head.join(","), ...body, ...foot].join("\n") + "\n";
}

/** Refund-rate check per affiliate (run with the statement): ≥ 5 referrals and > 30% reversed → exception. */
export async function refundRateCheck(store: Store, month: string, lines: StatementLine[]): Promise<number> {
  const by = new Map<string, { n: number; rev: number }>();
  for (const l of lines) {
    const e = by.get(l.affiliate_code) ?? { n: 0, rev: 0 };
    e.n++;
    if (l.state === "reversed") e.rev++;
    by.set(l.affiliate_code, e);
  }
  let raised = 0;
  for (const [code, e] of by) {
    if (e.n >= 5 && e.rev / e.n > 0.3) {
      const a = await store.findOne("affiliates", { code });
      await raiseException(store, {
        type: "affiliate_fraud",
        title: `High refund rate (${code}): ${e.rev} of ${e.n} lines reversed in ${month}`,
        detail: "Hold the payout and review the traffic source before paying.",
        ref: a?.id ?? code,
        severity: "high",
        source: "app:affiliates",
        dedupe_key: `refunds:${code}:${month}`,
      });
      raised++;
    }
  }
  return raised;
}
