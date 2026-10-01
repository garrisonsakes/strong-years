import { env, mode } from "../config";
import { MemoryStore } from "./memory";
import type { Store } from "./store";
import { SupabaseStore } from "./supabase";
import { seedDemoData } from "./seed";

const g = globalThis as unknown as { __syStore?: Store; __sySeeded?: Promise<void> };

/**
 * Returns the process-wide store. Supabase when configured, otherwise an in-memory
 * store seeded with clearly-labelled demo data (is_demo = true).
 */
export async function getStore(): Promise<Store> {
  if (!g.__syStore) {
    if (mode.mockDb) {
      const mem = new MemoryStore();
      g.__syStore = mem;
      if (process.env.SY_SKIP_SEED !== "1") g.__sySeeded = seedDemoData(mem);
    } else {
      g.__syStore = new SupabaseStore(env.supabaseUrl, env.supabaseServiceKey);
    }
  }
  if (g.__sySeeded) await g.__sySeeded;
  return g.__syStore;
}

/** Test helper: swap in a fresh store. */
export function setStoreForTests(store: Store) {
  g.__syStore = store;
  g.__sySeeded = undefined;
}

export type { Store } from "./store";
