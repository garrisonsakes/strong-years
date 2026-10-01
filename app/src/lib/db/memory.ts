import { matches, type Filter, type FindOptions, type Store } from "./store";
import type { Rows, TableName } from "./types";

type Tables = { [K in TableName]: Map<string, Rows[K]> };

function emptyTables(): Tables {
  return {
    members: new Map(),
    memberships: new Map(),
    sy_orders: new Map(),
    checkout_intents: new Map(),
    consent_log: new Map(),
    leads: new Map(),
    practice_logs: new Map(),
    retests: new Map(),
    chat_messages: new Map(),
    memory_items: new Map(),
    crisis_events: new Map(),
    support_tickets: new Map(),
    partners: new Map(),
    gifts: new Map(),
    cancellations: new Map(),
    reminders: new Map(),
    stripe_events: new Map(),
    analytics_events: new Map(),
    outbox: new Map(),
    magic_links: new Map(),
    refund_ledger: new Map(),
    push_subscriptions: new Map(),
    download_events: new Map(),
    founding_holds: new Map(),
    launch_state: new Map(),
    waitlist: new Map(),
    waitlist_push: new Map(),
    launch_sends: new Map(),
    conversion_outbox: new Map(),
    shopify_products: new Map(),
    plan_change_requests: new Map(),
    shopify_webhooks: new Map(),
    shopify_inventory: new Map(),
    shopify_early_refunds: new Map(),
    shopify_seat_ledger: new Map(),
    exceptions: new Map(),
    exception_events: new Map(),
    governor_approvals: new Map(),
    digest_runs: new Map(),
    email_sends: new Map(),
    email_prefs: new Map(),
    affiliates: new Map(),
    affiliate_referrals: new Map(),
    affiliate_commissions: new Map(),
  };
}

let seq = 0;

/** Mirrors the unique constraints in the Supabase migrations. */
const UNIQUE: Partial<Record<TableName, string[][]>> = {
  memberships: [["checkout_intent_id"], ["stripe_subscription_id"], ["shopify_contract_id"], ["shopify_origin_order_id"]],
  sy_orders: [["checkout_intent_id", "kind", "offer_code"], ["shopify_line_id", "kind"]],
  members: [["email"], ["shopify_customer_id"]],
  gifts: [["code"]],
  magic_links: [["token_hash"]],
  push_subscriptions: [["endpoint"]],
  founding_holds: [["intent_id"]],
  waitlist: [["email"], ["referral_code"]],
  waitlist_push: [["endpoint"]],
  launch_sends: [["waitlist_id", "step"]],
  conversion_outbox: [["platform", "event_id"]],
  shopify_products: [["sku"], ["shopify_variant_id", "selling_plan_id", "discount_code"]],
  shopify_inventory: [["inventory_item_id", "location_id"]],
  shopify_early_refunds: [["shopify_line_id", "shopify_refund_id"]],
  shopify_seat_ledger: [["ref"]],
  exceptions: [["type", "dedupe_key"]],
  governor_approvals: [["boost_id"]],
  digest_runs: [["day"]],
  email_sends: [["email", "sequence", "step"]],
  email_prefs: [["email"]],
  affiliates: [["email"], ["code"]],
  affiliate_referrals: [["member_id"]],
  affiliate_commissions: [["sy_order_id"]],
};

/** In-memory store used when Supabase env vars are absent (demo + unit tests). */
export class MemoryStore implements Store {
  readonly kind = "memory" as const;
  private tables: Tables = emptyTables();

  async insert<T extends TableName>(table: T, row: Partial<Rows[T]>): Promise<Rows[T]> {
    const now = new Date(Date.now() + seq++ / 1000).toISOString();
    const id = (row as { id?: string }).id ?? crypto.randomUUID();
    const map = this.tables[table] as Map<string, Rows[T]>;
    if (map.has(id)) throw new Error(`duplicate key ${table}.${id}`);
    for (const cols of UNIQUE[table] ?? []) {
      const r = row as Record<string, unknown>;
      if (cols.some((c) => r[c] === undefined || r[c] === null)) continue;
      for (const other of map.values()) {
        if (cols.every((c) => (other as unknown as Record<string, unknown>)[c] === r[c])) throw new Error(`duplicate key ${table}(${cols.join(",")})`);
      }
    }
    const full = { created_at: now, ...row, id } as unknown as Rows[T];
    if (table === "memberships" && !(full as { updated_at?: string }).updated_at) {
      (full as { updated_at?: string }).updated_at = now;
    }
    map.set(id, structuredClone(full));
    return structuredClone(full);
  }

  async update<T extends TableName>(table: T, id: string, patch: Partial<Rows[T]>): Promise<Rows[T] | null> {
    const map = this.tables[table] as Map<string, Rows[T]>;
    const existing = map.get(id);
    if (!existing) return null;
    const next = { ...existing, ...patch } as Rows[T];
    if (table === "memberships") (next as { updated_at?: string }).updated_at = new Date().toISOString();
    map.set(id, structuredClone(next));
    return structuredClone(next);
  }

  async get<T extends TableName>(table: T, id: string): Promise<Rows[T] | null> {
    const row = (this.tables[table] as Map<string, Rows[T]>).get(id);
    return row ? structuredClone(row) : null;
  }

  async find<T extends TableName>(
    table: T,
    filter?: Filter<Rows[T]>,
    opts: FindOptions<Rows[T]> = {},
  ): Promise<Rows[T][]> {
    let rows = [...(this.tables[table] as Map<string, Rows[T]>).values()].filter((r) => matches(r, filter));
    const orderBy = opts.orderBy ?? ("created_at" as keyof Rows[T] & string);
    rows.sort((a, b) => {
      const av = a[orderBy] as unknown as string | number;
      const bv = b[orderBy] as unknown as string | number;
      if (av === bv) return 0;
      const cmp = av > bv ? 1 : -1;
      return opts.desc ? -cmp : cmp;
    });
    if (opts.limit !== undefined) rows = rows.slice(0, opts.limit);
    return rows.map((r) => structuredClone(r));
  }

  async findOne<T extends TableName>(
    table: T,
    filter: Filter<Rows[T]>,
    opts: FindOptions<Rows[T]> = {},
  ): Promise<Rows[T] | null> {
    const rows = await this.find(table, filter, { ...opts, limit: 1 });
    return rows[0] ?? null;
  }

  // No await between the match and the write: atomic on the single JS thread.
  async updateWhere<T extends TableName>(table: T, filter: Filter<Rows[T]>, patch: Partial<Rows[T]>): Promise<Rows[T][]> {
    const map = this.tables[table] as Map<string, Rows[T]>;
    const out: Rows[T][] = [];
    for (const [id, row] of map) {
      if (!matches(row, filter)) continue;
      const next = { ...row, ...patch } as Rows[T];
      map.set(id, structuredClone(next));
      out.push(structuredClone(next));
    }
    return out;
  }

  async remove<T extends TableName>(table: T, filter: Filter<Rows[T]>): Promise<number> {
    const map = this.tables[table] as Map<string, Rows[T]>;
    let n = 0;
    for (const [id, row] of map) {
      if (matches(row, filter)) {
        map.delete(id);
        n++;
      }
    }
    return n;
  }

  async count<T extends TableName>(table: T, filter?: Filter<Rows[T]>): Promise<number> {
    return [...(this.tables[table] as Map<string, Rows[T]>).values()].filter((r) => matches(r, filter)).length;
  }
}
