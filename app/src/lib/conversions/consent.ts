/**
 * Ad-measurement consent (opt-in). Nothing leaves for an ad platform unless the
 * person ticked an unticked box saying so, and nothing that says otherwise has
 * happened since:
 *   - a later "Do Not Sell or Share" (consent_log do_not_sell_share) or account flag;
 *   - a Global Privacy Control signal / our opt-out cookie on the request (ad_opt_out);
 *   - leaving the waitlist (withdraws it; logged as do_not_sell_share).
 * Washington MHMD / CA CPRA: consent is separate, specific and revocable, and
 * events from health-context surfaces (quizzes) are never forwarded at all.
 */
import type { Store } from "../db/store";
import type { Attribution } from "../db/types";
import { normalizeEmail } from "../members";

import { AD_CONSENT_TEXT } from "./text";

export { AD_CONSENT_TEXT };

export interface ConsentContext {
  email: string | null | undefined;
  memberId?: string | null;
  attribution?: Attribution | null;
}

export async function hasAdConsent(store: Store, ctx: ConsentContext): Promise<boolean> {
  if (ctx.attribution?.ad_opt_out) return false;
  let email = ctx.email ? normalizeEmail(ctx.email) : null;
  if (ctx.memberId) {
    const m = await store.get("members", ctx.memberId);
    if (m?.ad_opt_out) return false;
    email = email ?? m?.email ?? null;
  }
  if (!email) return false;
  const byEmail = await store.findOne("members", { email });
  if (byEmail?.ad_opt_out) return false;
  const rows = await store.find("consent_log", { email, kind: { in: ["ad_tracking", "do_not_sell_share"] } }, { orderBy: "created_at", desc: true, limit: 10 });
  const latest = rows[0];
  if (!latest) return false;
  // Same timestamp for a grant and a withdrawal: the withdrawal wins (fail safe).
  const newest = rows.filter((r) => r.created_at === latest.created_at);
  return newest.every((r) => r.kind === "ad_tracking" && r.checked);
}

export async function recordAdConsent(store: Store, email: string, meta: { memberId?: string | null; ip: string | null; userAgent: string | null; source: string }): Promise<void> {
  await store.insert("consent_log", {
    email: normalizeEmail(email),
    member_id: meta.memberId ?? null,
    kind: "ad_tracking",
    checked: true,
    text_shown: `${AD_CONSENT_TEXT} (source: ${meta.source})`,
    price_cents: null,
    first_charge_at: null,
    offer_code: null,
    ip: meta.ip,
    user_agent: meta.userAgent,
  });
}

export async function withdrawAdConsent(store: Store, email: string, meta: { memberId?: string | null; ip: string | null; userAgent: string | null; source: string }): Promise<void> {
  await store.insert("consent_log", {
    email: normalizeEmail(email),
    member_id: meta.memberId ?? null,
    kind: "do_not_sell_share",
    checked: true,
    text_shown: `Do not sell or share my personal information (source: ${meta.source})`,
    price_cents: null,
    first_charge_at: null,
    offer_code: null,
    ip: meta.ip,
    user_agent: meta.userAgent,
  });
}
