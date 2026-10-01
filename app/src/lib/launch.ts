/**
 * Organic-first launch mode.
 *
 *   LAUNCH_MODE=prelaunch (default) : the brand's pages post for up to 21 days while
 *     /join and every checkout API refuse on the server and show the free waitlist.
 *   LAUNCH_MODE=live                 : checkout is open.
 *   CHECKOUT_OPENS_AT=<ISO time>     : in prelaunch, checkout opens by itself at this
 *     instant. It's the only thing the waitlist countdown ever counts down to.
 *
 * Plus one operational switch that needs no redeploy: "Open checkout now" in /admin
 * writes launch_state.opened_at. Nothing can close checkout again from the admin
 * (that's a deploy with LAUNCH_MODE=prelaunch and no opened_at, on purpose rare).
 *
 * Unknown LAUNCH_MODE values fail closed (prelaunch). An unparsable
 * CHECKOUT_OPENS_AT is ignored (no countdown, no auto-open) and reported by
 * launchConfigProblems() for /api/health.
 */
import type { Store } from "./db/store";
import type { LaunchStateRow } from "./db/types";

export type LaunchMode = "prelaunch" | "live";

export interface LaunchConfig {
  mode: LaunchMode;
  opensAt: Date | null;
  /** The raw value was set but couldn't be parsed. */
  opensAtInvalid: boolean;
}

export const LAUNCH_ROW_ID = "main";

type Env = Record<string, string | undefined>;

export function launchConfigFromEnv(e: Env = process.env): LaunchConfig {
  const raw = (e.LAUNCH_MODE ?? "").trim().toLowerCase();
  const mode: LaunchMode = raw === "live" ? "live" : "prelaunch";
  const at = (e.CHECKOUT_OPENS_AT ?? "").trim();
  if (!at) return { mode, opensAt: null, opensAtInvalid: false };
  // Only full ISO timestamps with a time zone: "2026-10-21T16:00:00Z" or "...-07:00".
  const ok = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d{1,3})?)?(Z|[+-]\d{2}:\d{2})$/.test(at);
  const d = ok ? new Date(at) : null;
  if (!d || Number.isNaN(d.getTime())) return { mode, opensAt: null, opensAtInvalid: true };
  return { mode, opensAt: d, opensAtInvalid: false };
}

export function launchConfigProblems(e: Env = process.env): string[] {
  const out: string[] = [];
  const raw = (e.LAUNCH_MODE ?? "").trim().toLowerCase();
  if (raw && raw !== "live" && raw !== "prelaunch") out.push("LAUNCH_MODE: must be prelaunch or live (treated as prelaunch)");
  if (launchConfigFromEnv(e).opensAtInvalid) out.push("CHECKOUT_OPENS_AT: not an ISO timestamp with a time zone (ignored)");
  return out;
}

export type LaunchReason = "env_live" | "opens_at_passed" | "admin_opened" | "prelaunch";

export interface LaunchState {
  live: boolean;
  reason: LaunchReason;
  /** The real opening time from env, if any (what the countdown shows). */
  opensAt: Date | null;
  /** When checkout actually opened, as far as we know. Anchors the launch sequence. */
  liveSince: Date | null;
}

/** Pure: decides the launch state from env config and the DB row. */
export function resolveLaunch(cfg: LaunchConfig, row: Pick<LaunchStateRow, "opened_at" | "live_seen_at"> | null, now: Date): LaunchState {
  const candidates: { at: Date | null; reason: LaunchReason }[] = [];
  if (row?.opened_at) candidates.push({ at: new Date(row.opened_at), reason: "admin_opened" });
  if (cfg.mode === "prelaunch" && cfg.opensAt && cfg.opensAt.getTime() <= now.getTime()) candidates.push({ at: cfg.opensAt, reason: "opens_at_passed" });
  if (cfg.mode === "live") candidates.push({ at: row?.live_seen_at ? new Date(row.live_seen_at) : null, reason: "env_live" });
  if (candidates.length === 0) return { live: false, reason: "prelaunch", opensAt: cfg.opensAt, liveSince: null };
  const known = candidates.filter((c) => c.at !== null).sort((a, b) => a.at!.getTime() - b.at!.getTime());
  const first = known[0] ?? candidates[0]!;
  return { live: true, reason: first.reason, opensAt: cfg.opensAt, liveSince: first.at };
}

async function readRow(store: Store): Promise<LaunchStateRow | null> {
  return store.get("launch_state", LAUNCH_ROW_ID);
}

async function ensureRow(store: Store): Promise<void> {
  if (await readRow(store)) return;
  try {
    await store.insert("launch_state", { id: LAUNCH_ROW_ID, opened_at: null, opened_by: null, live_seen_at: null });
  } catch {
    /* another request created it */
  }
}

export async function getLaunchState(store: Store, now = new Date(), cfg = launchConfigFromEnv()): Promise<LaunchState> {
  return resolveLaunch(cfg, await readRow(store), now);
}

export async function isCheckoutOpen(store: Store, now = new Date()): Promise<boolean> {
  return (await getLaunchState(store, now)).live;
}

/** Admin switch: opens checkout now. Idempotent; the first opening time is kept. */
export async function openCheckoutNow(store: Store, by: string, now = new Date()): Promise<LaunchState> {
  await ensureRow(store);
  await store.updateWhere("launch_state", { id: LAUNCH_ROW_ID, opened_at: null }, { opened_at: now.toISOString(), opened_by: by.slice(0, 60) });
  return getLaunchState(store, now);
}

/**
 * Cron: with LAUNCH_MODE=live there is no timestamp in env, so the first job that
 * sees checkout open records when (conditional update: two racing runs agree).
 */
export async function anchorLiveSince(store: Store, now = new Date()): Promise<LaunchState> {
  const state = await getLaunchState(store, now);
  if (!state.live || state.liveSince) return state;
  await ensureRow(store);
  await store.updateWhere("launch_state", { id: LAUNCH_ROW_ID, live_seen_at: null }, { live_seen_at: now.toISOString() });
  return getLaunchState(store, now);
}

export const PRELAUNCH_MESSAGE = "Checkout isn't open yet. Join the free waitlist and we'll email you the moment it opens.";
