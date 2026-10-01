import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { isOp, type Filter, type FindOptions, type Store } from "./store";
import type { Rows, TableName } from "./types";

const PAGE = 1000;

/**
 * Supabase implementation. Runs server-side only with the service-role key
 * (RLS is enabled on every table; the service role bypasses it, the anon key
 * can only call the whitelisted RPCs defined in the migration).
 */
export class SupabaseStore implements Store {
  readonly kind = "supabase" as const;
  private client: SupabaseClient;

  constructor(url: string, serviceKey: string) {
    this.client = createClient(url, serviceKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }

  // The query builder's generic types are table-specific; we build them dynamically.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private applyFilter(query: any, filter: Record<string, unknown> | undefined) {
    if (!filter) return query;
    for (const [key, cond] of Object.entries(filter)) {
      if (isOp(cond)) {
        const c = cond as Record<string, unknown>;
        if (c.in !== undefined) query = query.in(key, c.in as unknown[]);
        if (c.neq !== undefined) query = query.neq(key, c.neq);
        if (c.gte !== undefined) query = query.gte(key, c.gte);
        if (c.lte !== undefined) query = query.lte(key, c.lte);
        if (c.gt !== undefined) query = query.gt(key, c.gt);
        if (c.lt !== undefined) query = query.lt(key, c.lt);
      } else if (cond === null) {
        query = query.is(key, null);
      } else {
        query = query.eq(key, cond);
      }
    }
    return query;
  }

  async insert<T extends TableName>(table: T, row: Partial<Rows[T]>): Promise<Rows[T]> {
    const { data, error } = await this.client.from(table).insert(row as never).select().single();
    if (error) throw new Error(`supabase insert ${table}: ${error.message}`);
    return data as Rows[T];
  }

  async update<T extends TableName>(table: T, id: string, patch: Partial<Rows[T]>): Promise<Rows[T] | null> {
    const body = table === "memberships" ? { ...patch, updated_at: new Date().toISOString() } : patch;
    const { data, error } = await this.client.from(table).update(body as never).eq("id", id).select().maybeSingle();
    if (error) throw new Error(`supabase update ${table}: ${error.message}`);
    return (data as Rows[T]) ?? null;
  }

  async get<T extends TableName>(table: T, id: string): Promise<Rows[T] | null> {
    const { data, error } = await this.client.from(table).select("*").eq("id", id).maybeSingle();
    if (error) throw new Error(`supabase get ${table}: ${error.message}`);
    return (data as Rows[T]) ?? null;
  }

  /**
   * PostgREST caps a response at 1,000 rows (H7). Without an explicit limit we
   * page with .range() until a short page comes back, so sums (MRR, processor
   * volume, KPIs) see every row.
   */
  async find<T extends TableName>(
    table: T,
    filter?: Filter<Rows[T]>,
    opts: FindOptions<Rows[T]> = {},
  ): Promise<Rows[T][]> {
    const build = () => {
      let q = this.applyFilter(this.client.from(table).select("*"), filter as Record<string, unknown>);
      q = q.order(opts.orderBy ?? "created_at", { ascending: !opts.desc }).order("id", { ascending: true });
      return q;
    };
    if (opts.limit !== undefined && opts.limit <= PAGE) {
      const { data, error } = await build().limit(opts.limit);
      if (error) throw new Error(`supabase find ${table}: ${error.message}`);
      return (data ?? []) as Rows[T][];
    }
    const out: Rows[T][] = [];
    const cap = opts.limit ?? Number.POSITIVE_INFINITY;
    for (let from = 0; out.length < cap; from += PAGE) {
      const { data, error } = await build().range(from, from + PAGE - 1);
      if (error) throw new Error(`supabase find ${table}: ${error.message}`);
      const rows = (data ?? []) as Rows[T][];
      out.push(...rows);
      if (rows.length < PAGE) break;
    }
    return out.slice(0, cap);
  }

  async findOne<T extends TableName>(
    table: T,
    filter: Filter<Rows[T]>,
    opts: FindOptions<Rows[T]> = {},
  ): Promise<Rows[T] | null> {
    const rows = await this.find(table, filter, { ...opts, limit: 1 });
    return rows[0] ?? null;
  }

  /** UPDATE ... WHERE <filter> RETURNING *: a single statement, so a status claim is atomic (H8). */
  async updateWhere<T extends TableName>(table: T, filter: Filter<Rows[T]>, patch: Partial<Rows[T]>): Promise<Rows[T][]> {
    const body = table === "memberships" ? { ...patch, updated_at: new Date().toISOString() } : patch;
    const query = this.applyFilter(this.client.from(table).update(body as never), filter as Record<string, unknown>);
    const { data, error } = await query.select();
    if (error) throw new Error(`supabase updateWhere ${table}: ${error.message}`);
    return (data ?? []) as Rows[T][];
  }

  async remove<T extends TableName>(table: T, filter: Filter<Rows[T]>): Promise<number> {
    const query = this.applyFilter(this.client.from(table).delete({ count: "exact" }), filter as Record<string, unknown>);
    const { count, error } = await query;
    if (error) throw new Error(`supabase delete ${table}: ${error.message}`);
    return count ?? 0;
  }

  async rpc(fn: string, args: Record<string, unknown>): Promise<unknown> {
    const { data, error } = await this.client.rpc(fn, args);
    if (error) throw new Error(`supabase rpc ${fn}: ${error.message}`);
    return data;
  }

  async count<T extends TableName>(table: T, filter?: Filter<Rows[T]>): Promise<number> {
    const query = this.applyFilter(
      this.client.from(table).select("id", { count: "exact", head: true }),
      filter as Record<string, unknown>,
    );
    const { count, error } = await query;
    if (error) throw new Error(`supabase count ${table}: ${error.message}`);
    return count ?? 0;
  }
}
