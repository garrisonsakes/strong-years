/**
 * Warm-list import (data/warm_lists/README.md): K9SUPPS and Unignorable subscribers who
 * asked, inside their own brand's email, to hear when Strong Years opens.
 *
 * Consent rules, by construction:
 *  - a row is imported only when the source brand still holds email consent for it
 *    AND the person opted in to the Strong Years waitlist themselves (a click on the
 *    "Add me" button in the warm email, recorded by the ESP as a tag or property);
 *    being on the K9SUPPS or Unignorable list alone is never enough;
 *  - bounced, complained, cleaned, unsubscribed and non-US rows are suppressed;
 *  - SMS consent is never read, never stored and never used (email only);
 *  - ad-measurement consent is never set by an import (nobody saw that checkbox);
 *  - an address already on the waitlist (any status, including unsubscribed) or
 *    unsubscribed from our lifecycle mail is left exactly as it is;
 *  - imported rows land as `pending` and receive nothing but the standard double
 *    opt-in email (sent in batches by /api/cron/warm-invites). Until the inbox
 *    confirms, no launch email goes to them.
 */
import { randomToken, sha256Hex } from "./auth/session";
import { env } from "./config";
import type { Store } from "./db/store";
import type { WaitlistEntry } from "./db/types";
import { normalizeEmail } from "./members";
import { sendEmail } from "./notify";
import { CONFIRM_TTL_MS, isValidEmail, newReferralCode, waitlistLinks } from "./waitlist";

export const WARM_BRANDS = {
  k9supps: { name: "K9SUPPS", audience: "dog owners 50+" },
  unignorable: { name: "Unignorable", audience: "women 40+ and their parents" },
} as const;
export type WarmBrand = keyof typeof WARM_BRANDS;
export const isWarmBrand = (b: string | null | undefined): b is WarmBrand => Boolean(b && b in WARM_BRANDS);

export const WARM_MEDIUM = "warm_list";
export const MAX_IMPORT_BYTES = 5 * 1024 * 1024;
export const MAX_IMPORT_ROWS = 50_000;

/** Canonical template column → accepted headers (case- and punctuation-insensitive). */
export const COLUMN_ALIASES: Record<string, string[]> = {
  email: ["email", "email address", "e-mail"],
  first_name: ["first name", "first_name", "fname", "firstname"],
  email_consent: ["email_consent", "email marketing consent", "status", "member status", "subscription status"],
  email_consent_at: ["email_consent_at", "email marketing consent timestamp", "confirm_time", "optin_time"],
  consent_source: ["consent_source", "source", "signup source", "list source"],
  sy_waitlist_optin: ["sy_waitlist_optin", "strong years waitlist opt-in", "sy waitlist optin"],
  sy_waitlist_optin_at: ["sy_waitlist_optin_at", "strong years waitlist opt-in at", "sy waitlist optin at"],
  tags: ["tags"],
  suppression: ["suppression", "email suppressions", "suppression reason", "suppressed reason"],
  bounced: ["bounced", "hard bounce", "is bounced"],
  country: ["country", "address country", "location country", "cc"],
};

/** The Mailchimp tag the warm email's "Add me" link applies (Klaviyo: the profile property). */
export const OPTIN_TAG = "sy-waitlist-yes";

const TRUE = new Set(["true", "yes", "y", "1", "subscribed", "consented", "opted in", "opted_in"]);
const SUPPRESS_STATUS = new Set(["unsubscribed", "cleaned", "bounced", "complained", "spam_complaint", "never_subscribed", "archived", "pending", "transactional"]);
const SUPPRESS_REASON = /bounce|complain|spam|unsub|invalid|suppress|manual|clean/i;
const US = new Set(["", "us", "usa", "united states", "united states of america"]);

/** RFC 4180 CSV (quoted fields, doubled quotes, CRLF/LF, a leading BOM). */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  const s = text.replace(/^﻿/, "");
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (quoted) {
      if (c === '"' && s[i + 1] === '"') {
        field += '"';
        i++;
      } else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"' && field === "") quoted = true;
    else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && s[i + 1] === "\n") i++;
      row.push(field);
      if (row.some((f) => f.trim() !== "")) rows.push(row);
      row = [];
      field = "";
    } else field += c;
  }
  row.push(field);
  if (row.some((f) => f.trim() !== "")) rows.push(row);
  return rows;
}

const norm = (h: string) => h.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

export function mapHeaders(header: string[]): Record<string, number> {
  const out: Record<string, number> = {};
  header.forEach((h, i) => {
    const n = norm(h);
    for (const [col, aliases] of Object.entries(COLUMN_ALIASES)) {
      if (out[col] === undefined && aliases.some((a) => norm(a) === n)) out[col] = i;
    }
  });
  return out;
}

export type SkipReason =
  | "invalid_email"
  | "duplicate_in_file"
  | "no_brand_consent"
  | "suppressed_bounce_or_complaint"
  | "not_us"
  | "no_waitlist_optin"
  | "already_on_waitlist"
  | "unsubscribed_from_strong_years";

export interface WarmRow {
  email: string;
  firstName: string | null;
  optinAt: string | null;
  consentSource: string | null;
}

/** One row → either a clean candidate or the first rule it fails (in this order). */
export function classifyRow(cells: string[], cols: Record<string, number>): { ok: true; row: WarmRow } | { ok: false; reason: SkipReason } {
  const get = (c: string) => (cols[c] === undefined ? "" : (cells[cols[c]!] ?? "").trim());
  const email = normalizeEmail(get("email"));
  if (!isValidEmail(email)) return { ok: false, reason: "invalid_email" };
  const status = get("email_consent").toLowerCase();
  const suppression = get("suppression");
  if (TRUE.has(get("bounced").toLowerCase()) || SUPPRESS_REASON.test(suppression) || ["cleaned", "bounced", "complained", "spam_complaint"].includes(status)) {
    return { ok: false, reason: "suppressed_bounce_or_complaint" };
  }
  if (!TRUE.has(status) || SUPPRESS_STATUS.has(status)) return { ok: false, reason: "no_brand_consent" };
  if (!US.has(get("country").toLowerCase())) return { ok: false, reason: "not_us" };
  const tags = get("tags").toLowerCase().split(/[,;|]/).map((t) => t.trim().replace(/^"|"$/g, ""));
  if (!TRUE.has(get("sy_waitlist_optin").toLowerCase()) && !tags.includes(OPTIN_TAG)) return { ok: false, reason: "no_waitlist_optin" };
  const at = get("sy_waitlist_optin_at");
  const parsed = at ? new Date(at) : null;
  const first = get("first_name").normalize("NFKC").replace(/[\u0000-\u001F\u007F<>]/g, "").slice(0, 60);
  return {
    ok: true,
    row: {
      email,
      firstName: first || null,
      optinAt: parsed && !Number.isNaN(parsed.getTime()) ? parsed.toISOString() : null,
      consentSource: get("consent_source").slice(0, 120) || null,
    },
  };
}

export interface ImportSummary {
  brand: WarmBrand;
  batch: string;
  committed: boolean;
  rows: number;
  imported: number;
  skipped: Partial<Record<SkipReason, number>>;
  /** Columns the file had that the importer read (and the ones it ignored on purpose). */
  columns: { mapped: string[]; ignored: string[] };
  errors: string[];
}

export function importText(brand: WarmBrand, batch: string, optinAt: string | null): string {
  return `Imported from the ${WARM_BRANDS[brand].name} email list (batch ${batch}): the subscriber clicked "Add me to the Strong Years waitlist" in a ${WARM_BRANDS[brand].name} email${optinAt ? ` at ${optinAt}` : ""}. Nothing is sent until the Strong Years confirmation email is confirmed. SMS and ad-measurement consent were not imported.`;
}

/**
 * Parse, classify and (when `commit`) insert. Without `commit` it is a dry run that
 * reports exactly what a commit would do and writes nothing.
 */
export async function importWarmList(store: Store, csv: string, opts: { brand: WarmBrand; commit: boolean; batch?: string; now?: Date }): Promise<ImportSummary> {
  const now = opts.now ?? new Date();
  const batch = (opts.batch ?? `${opts.brand}-${now.toISOString().slice(0, 10)}`).replace(/[^A-Za-z0-9_-]/g, "").slice(0, 60);
  const summary: ImportSummary = { brand: opts.brand, batch, committed: opts.commit, rows: 0, imported: 0, skipped: {}, columns: { mapped: [], ignored: [] }, errors: [] };
  const skip = (r: SkipReason) => (summary.skipped[r] = (summary.skipped[r] ?? 0) + 1);
  if (csv.length > MAX_IMPORT_BYTES) {
    summary.errors.push(`file larger than ${MAX_IMPORT_BYTES} bytes`);
    return summary;
  }
  const [header, ...rows] = parseCsv(csv);
  if (!header) {
    summary.errors.push("empty file");
    return summary;
  }
  const cols = mapHeaders(header);
  summary.columns.mapped = Object.keys(cols);
  summary.columns.ignored = header.filter((_, i) => !Object.values(cols).includes(i));
  for (const required of ["email", "email_consent"]) if (cols[required] === undefined) summary.errors.push(`missing column: ${required}`);
  if (cols.sy_waitlist_optin === undefined && cols.tags === undefined) summary.errors.push("missing column: sy_waitlist_optin (or a Mailchimp TAGS column)");
  if (rows.length > MAX_IMPORT_ROWS) summary.errors.push(`more than ${MAX_IMPORT_ROWS} rows: split the file`);
  if (summary.errors.length) return summary;

  const seen = new Set<string>();
  for (const cells of rows) {
    summary.rows++;
    const c = classifyRow(cells, cols);
    if (!c.ok) {
      skip(c.reason);
      continue;
    }
    const { row } = c;
    if (seen.has(row.email)) {
      skip("duplicate_in_file");
      continue;
    }
    seen.add(row.email);
    if (await store.findOne("waitlist", { email: row.email })) {
      skip("already_on_waitlist");
      continue;
    }
    const pref = await store.findOne("email_prefs", { email: row.email });
    if (pref?.unsubscribed_at) {
      skip("unsubscribed_from_strong_years");
      continue;
    }
    summary.imported++;
    if (!opts.commit) continue;
    let entry: WaitlistEntry | null = null;
    for (let attempt = 0; attempt < 3 && !entry; attempt++) {
      try {
        entry = await store.insert("waitlist", {
          email: row.email,
          first_name: row.firstName,
          status: "pending",
          confirm_token_hash: null,
          confirm_expires_at: null,
          last_signup_email_at: null,
          confirmed_at: null,
          unsubscribed_at: null,
          ad_consent_requested: false,
          visitor_id: null,
          referral_code: newReferralCode(),
          referred_by: null,
          referral_reward_at: null,
          attribution: { utm_source: opts.brand, utm_medium: WARM_MEDIUM, utm_campaign: batch, landing_path: "/import", first_seen_at: row.optinAt ?? now.toISOString() },
          member_id: null,
          converted_at: null,
          ip: null,
          user_agent: null,
        });
      } catch {
        if (await store.findOne("waitlist", { email: row.email })) break;
      }
    }
    if (!entry) {
      summary.imported--;
      skip("already_on_waitlist");
      continue;
    }
    await store.insert("consent_log", { email: row.email, member_id: null, kind: "waitlist_email", checked: true, text_shown: importText(opts.brand, batch, row.optinAt), price_cents: null, first_charge_at: null, offer_code: null, ip: null, user_agent: null });
  }
  return summary;
}

export const isWarmImport = (e: Pick<WaitlistEntry, "attribution">) => e.attribution?.utm_medium === WARM_MEDIUM && isWarmBrand(e.attribution?.utm_source);

/**
 * Cron: send the double opt-in email to imported rows that haven't had one, at most
 * `limit` per run. Each send is claimed first (last_signup_email_at null → now), so two
 * overlapping runs never email anyone twice.
 */
export async function sendWarmInvites(store: Store, opts: { limit?: number; now?: Date; token?: () => string } = {}): Promise<{ sent: number; considered: number }> {
  const now = opts.now ?? new Date();
  const limit = Math.max(1, Math.min(opts.limit ?? Number(process.env.WARM_INVITE_BATCH || 100), 1000));
  const candidates = (await store.find("waitlist", { status: "pending", last_signup_email_at: null, confirm_token_hash: null }, { orderBy: "created_at", limit: limit * 5 })).filter(isWarmImport);
  let sent = 0;
  for (const c of candidates) {
    if (sent >= limit) break;
    const token = opts.token ? opts.token() : randomToken(24);
    const hash = await sha256Hex(token);
    const [claimed] = await store.updateWhere("waitlist", { id: c.id, status: "pending", last_signup_email_at: null }, { last_signup_email_at: now.toISOString(), confirm_token_hash: hash, confirm_expires_at: new Date(now.getTime() + CONFIRM_TTL_MS).toISOString() });
    if (!claimed) continue;
    const brand = WARM_BRANDS[claimed.attribution!.utm_source as WarmBrand].name;
    const link = `${env.siteUrl}/waitlist/confirm?token=${token}`;
    await sendEmail({
      to: claimed.email,
      from: "team",
      template: "WL1w_warm_confirm",
      subject: "Confirm your spot on the Strong Years waitlist",
      secrets: [token, link],
      manageLine: `Didn't ask for this? Ignore it and you'll never hear from us, or leave now: ${waitlistLinks(claimed).unsubscribe}`,
      text: [
        `${claimed.first_name ? `${claimed.first_name}, you` : "You"} tapped "Add me" in a ${brand} email, so here is the one step left. Tap to confirm this is your email address (the link works for 72 hours):`,
        link,
        "Until you confirm, Strong Years won't send you anything else. If you don't confirm, this is the only email you'll get from us.",
        "What you signed up for: an email the moment checkout opens, with first access at the founding price, and at most 3 launch emails in the 72 hours after that.",
      ].join("\n\n"),
    });
    sent++;
  }
  return { sent, considered: candidates.length };
}
