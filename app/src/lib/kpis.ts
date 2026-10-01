import type { Store } from "./db/store";
import { foundingClaimed, mrrCents } from "./members";
import { offerRules } from "./config";

export interface Kpis {
  mrrCents: number;
  /**
 * H7: every find() here pages through all rows on Supabase (no 1,000-row cap).
 */
/** H12: MRR that will stop at period end (cancel_at_period_end); not counted in mrrCents. */
  scheduledChurnCents: number;
  mrrByArm: { A: number; B: number; other: number };
  activeByArm: { A: number; B: number; gift: number };
  paying: number;
  trials: number;
  paused: number;
  trialConversions: number;
  trialConversionRate: number | null;
  churned30d: number;
  churnRate30d: number | null;
  cancelFlowStarts30d: number;
  saves30d: number;
  refunds: { count: number; cents: number };
  chargebacks: { count: number; ratio: number | null };
  cohort: { claimed: number; cap: number; left: number };
  revenue30dCents: number;
  leads: number;
  crisisOpen: number;
  priceTest: { cell: string; exposures: number; checkouts: number; members: number; refunded: number; mrrCents: number; conversion: number | null }[];
  processors: { id: string; volume30dCents: number; orders30d: number }[];
}

export async function computeKpis(store: Store, now = new Date()): Promise<Kpis> {
  const since = new Date(now.getTime() - 30 * 86_400_000).toISOString();
  const memberships = await store.find("memberships");
  const orders = await store.find("sy_orders");
  const cancellations = await store.find("cancellations", { created_at: { gte: since } });

  let mrr = 0;
  let scheduledChurn = 0;
  const mrrByArm = { A: 0, B: 0, other: 0 };
  const activeByArm = { A: 0, B: 0, gift: 0 };
  let paying = 0;
  let trials = 0;
  let paused = 0;
  for (const m of memberships) {
    const c = mrrCents(m);
    mrr += c;
    if (m.cancel_at_period_end && (m.status === "active" || m.status === "past_due")) scheduledChurn += mrrCents({ ...m, cancel_at_period_end: false });
    if (m.arm === "A") mrrByArm.A += c;
    else if (m.arm === "B") mrrByArm.B += c;
    else mrrByArm.other += c;
    const live = m.status === "active" || m.status === "past_due" || m.status === "trialing";
    if (live) {
      if (m.plan === "gift") activeByArm.gift++;
      else if (m.arm === "A") activeByArm.A++;
      else if (m.arm === "B") activeByArm.B++;
    }
    if (m.status === "active" || m.status === "past_due") paying += m.plan === "gift" ? 0 : 1;
    if (m.status === "trialing") trials++;
    if (m.status === "paused") paused++;
  }

  // Trial conversions: memberships that started with a trial and have a first paid charge.
  const trialStarted = memberships.filter((m) => m.trial_end !== null);
  const trialEnded = trialStarted.filter((m) => m.trial_end && new Date(m.trial_end) <= now);
  const converted = trialStarted.filter((m) => m.first_paid_at !== null);
  const trialConversionRate = trialEnded.length ? converted.length / trialEnded.length : null;

  const churned = memberships.filter((m) => m.canceled_at && m.canceled_at >= since && m.plan !== "gift").length;
  const payingAtStart = memberships.filter((m) => m.first_paid_at && m.first_paid_at < since && m.plan !== "gift").length;
  const refunded = orders.filter((o) => o.status === "refunded");
  const disputed = orders.filter((o) => o.status === "disputed");
  const charges30 = orders.filter((o) => o.created_at >= since);
  const claimed = await foundingClaimed(store);

  return {
    mrrCents: mrr,
    scheduledChurnCents: scheduledChurn,
    mrrByArm,
    activeByArm,
    paying,
    trials,
    paused,
    trialConversions: converted.length,
    trialConversionRate,
    churned30d: churned,
    churnRate30d: payingAtStart ? churned / payingAtStart : null,
    cancelFlowStarts30d: cancellations.length,
    saves30d: cancellations.filter((c) => c.outcome === "saved_pause" || c.outcome === "saved_downgrade").length,
    refunds: { count: refunded.length, cents: orders.reduce((s, o) => s + (o.amount_refunded_cents ?? (o.status === "refunded" ? o.amount_cents : 0)), 0) },
    chargebacks: { count: disputed.length, ratio: charges30.length ? disputed.filter((o) => o.created_at >= since).length / charges30.length : null },
    cohort: { claimed, cap: offerRules.foundingCap, left: Math.max(0, offerRules.foundingCap - claimed) },
    revenue30dCents: charges30.filter((o) => o.status === "paid").reduce((s, o) => s + o.amount_cents, 0),
    leads: await store.count("leads"),
    crisisOpen: await store.count("crisis_events", { handled_at: null }),
    priceTest: await priceTestReport(store),
    processors: (["stripe", "braintree"] as const).map((id) => {
      const o = charges30.filter((x) => (x.processor ?? "stripe") === id && x.status === "paid");
      return { id, volume30dCents: o.reduce((sum, x) => sum + x.amount_cents, 0), orders30d: o.length };
    }),
  };
}

/**
 * H7: every find() here pages through all rows on Supabase (no 1,000-row cap).
 */
/** Blitz $25 vs $30 test: unique exposures (from sticky visitor ids), checkouts started, members, refunds, MRR. */
export async function priceTestReport(store: Store) {
  const exposures = await store.find("analytics_events", { name: "price_cell_exposure" });
  const intents = await store.find("checkout_intents", { offer_code: "founding" });
  const memberships = await store.find("memberships", { arm: "B" });
  const cells = new Set<string>([
    ...exposures.map((e) => String(e.payload.cell ?? "")),
    ...intents.map((i) => i.price_cell ?? ""),
    ...memberships.map((m) => m.price_cell ?? ""),
  ]);
  cells.delete("");
  return [...cells].sort().map((cell) => {
    const vids = new Set(exposures.filter((e) => e.payload.cell === cell).map((e) => String(e.payload.vid ?? e.id)));
    const ms = memberships.filter((m) => m.price_cell === cell);
    const members = ms.filter((m) => m.status !== "refunded").length;
    return {
      cell,
      exposures: vids.size,
      checkouts: intents.filter((i) => i.price_cell === cell).length,
      members,
      refunded: ms.filter((m) => m.status === "refunded").length,
      mrrCents: ms.reduce((sum, m) => sum + mrrCents(m), 0),
      conversion: vids.size ? members / vids.size : null,
    };
  });
}
