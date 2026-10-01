/**
 * Round 9: one definition of "a real deploy" and the config it must have.
 * Edge-safe (no imports), used by middleware, email, the health check and the
 * boot-time check in instrumentation.ts.
 *
 * Local means `next dev` / vitest, or an in-memory demo build that says so with
 * LOCAL_DEMO_BUILD=true (the e2e and screenshot servers). That flag is ignored on
 * Vercel production and whenever Supabase is configured. Everything else is a deploy.
 */
import { billingConfigProblems } from "./billing/provider";

type Env = Record<string, string | undefined>;

export function hasRealData(e: Env = process.env): boolean {
  return Boolean((e.SUPABASE_URL || e.NEXT_PUBLIC_SUPABASE_URL) && e.SUPABASE_SERVICE_ROLE_KEY);
}

export function isDeployed(e: Env = process.env): boolean {
  if (e.NODE_ENV === "development" || e.NODE_ENV === "test") return false;
  // ALLOW_RULES_ONLY_CHAT (Round 7) is accepted as the old name of the same switch.
  const saysLocal = e.LOCAL_DEMO_BUILD === "true" || e.ALLOW_RULES_ONLY_CHAT === "true";
  return !(saysLocal && e.VERCEL_ENV !== "production" && !hasRealData(e));
}

const PLACEHOLDER = /\[|\]|set [A-Z_]+|to be confirmed|example\.(com|org|net)\b|\.example\b|changeme|change-me|todo|xxx/i;

function badUrl(raw: string | undefined): string | null {
  if (!raw) return "missing";
  let u: URL;
  try {
    u = new URL(raw);
  } catch {
    return "not a URL";
  }
  if (u.protocol !== "https:") return "must be https";
  if (/^(localhost|127\.|0\.0\.0\.0|\[::1\]|.*\.local$|.*\.internal$)/i.test(u.hostname)) return "points at a local host";
  if (PLACEHOLDER.test(u.hostname)) return "placeholder domain";
  return null;
}

function badText(raw: string | undefined, minLen: number): string | null {
  if (!raw || !raw.trim()) return "missing";
  if (PLACEHOLDER.test(raw)) return "placeholder";
  if (raw.trim().length < minLen) return "too short";
  return null;
}

function badEmail(raw: string | undefined): string | null {
  if (!raw) return "missing";
  const addr = raw.match(/<([^>]+)>/)?.[1] ?? raw;
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(addr.trim())) return "not an email address";
  if (PLACEHOLDER.test(addr)) return "placeholder";
  return null;
}

/**
 * What would make every email wrong (localhost links, a placeholder postal address,
 * a fake sender). Names and reasons only, never values.
 */
export function emailConfigProblems(e: Env = process.env): string[] {
  const out: string[] = [];
  const add = (name: string, why: string | null) => why && out.push(`${name}: ${why}`);
  add("NEXT_PUBLIC_SITE_URL", badUrl(e.NEXT_PUBLIC_SITE_URL));
  add("MAILING_ADDRESS", badText(e.MAILING_ADDRESS, 12));
  add("EMAIL_FROM", badEmail(e.EMAIL_FROM));
  add("SUPPORT_EMAIL", badEmail(e.SUPPORT_EMAIL));
  return out;
}

/** Everything a deploy must have before it serves anyone (health check + boot log). */
export function deployConfigProblems(e: Env = process.env): string[] {
  const out = emailConfigProblems(e);
  for (const name of ["SESSION_SECRET", "CRON_SECRET", "ADMIN_USER", "ADMIN_PASSWORD"]) {
    if (!e[name] || PLACEHOLDER.test(e[name]!)) out.push(`${name}: ${e[name] ? "placeholder" : "missing"}`);
  }
  if (e.SESSION_SECRET && e.SESSION_SECRET.length < 32) out.push("SESSION_SECRET: shorter than 32 characters");
  // Organic launch config (lib/launch.ts mirrors these rules).
  const mode = (e.LAUNCH_MODE ?? "").trim().toLowerCase();
  if (mode && mode !== "live" && mode !== "prelaunch") out.push("LAUNCH_MODE: must be prelaunch or live");
  const opens = (e.CHECKOUT_OPENS_AT ?? "").trim();
  if (opens && (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2})$/.test(opens) || Number.isNaN(Date.parse(opens)))) out.push("CHECKOUT_OPENS_AT: not an ISO timestamp with a time zone");
  if (e.GROWTH_API_TOKEN && e.GROWTH_API_TOKEN.length < 32) out.push("GROWTH_API_TOKEN: shorter than 32 characters (endpoint stays off)");
  // CANON UPDATE 2: the Shopify store, webhook secret and customer account page.
  out.push(...billingConfigProblems(e));
  return out;
}
