import type { Rows, TableName } from "./types";

export type Op<V> = { gte?: V; lte?: V; gt?: V; lt?: V; in?: V[]; neq?: V };
export type Filter<T> = { [K in keyof T]?: T[K] | Op<T[K]> };

export interface FindOptions<T> {
  orderBy?: keyof T & string;
  desc?: boolean;
  limit?: number;
}

/**
 * Minimal table API implemented twice: in memory (demo/tests) and on Supabase
 * (production). Domain code only talks to this interface.
 */
export interface Store {
  readonly kind: "memory" | "supabase";
  insert<T extends TableName>(table: T, row: Partial<Rows[T]>): Promise<Rows[T]>;
  update<T extends TableName>(table: T, id: string, patch: Partial<Rows[T]>): Promise<Rows[T] | null>;
  get<T extends TableName>(table: T, id: string): Promise<Rows[T] | null>;
  find<T extends TableName>(table: T, filter?: Filter<Rows[T]>, opts?: FindOptions<Rows[T]>): Promise<Rows[T][]>;
  findOne<T extends TableName>(table: T, filter: Filter<Rows[T]>, opts?: FindOptions<Rows[T]>): Promise<Rows[T] | null>;
  /** Conditional update: only rows matching `filter` change. Atomic in both stores (H8). */
  updateWhere<T extends TableName>(table: T, filter: Filter<Rows[T]>, patch: Partial<Rows[T]>): Promise<Rows[T][]>;
  remove<T extends TableName>(table: T, filter: Filter<Rows[T]>): Promise<number>;
  count<T extends TableName>(table: T, filter?: Filter<Rows[T]>): Promise<number>;
  /** Server-side SQL function (Supabase only). Callers fall back when absent. */
  rpc?(fn: string, args: Record<string, unknown>): Promise<unknown>;
}

export function isOp(v: unknown): v is Op<unknown> {
  if (v === null || typeof v !== "object" || Array.isArray(v)) return false;
  const keys = Object.keys(v as object);
  return keys.length > 0 && keys.every((k) => ["gte", "lte", "gt", "lt", "in", "neq"].includes(k));
}

export function matches<T>(row: T, filter: Filter<T> | undefined): boolean {
  if (!filter) return true;
  for (const [key, cond] of Object.entries(filter) as [keyof T, unknown][]) {
    const value = row[key] as unknown;
    if (isOp(cond)) {
      const c = cond as Op<unknown>;
      if (c.in !== undefined && !c.in.includes(value)) return false;
      if (c.neq !== undefined && value === c.neq) return false;
      if (c.gte !== undefined && !(value !== null && value !== undefined && (value as never) >= (c.gte as never))) return false;
      if (c.lte !== undefined && !(value !== null && value !== undefined && (value as never) <= (c.lte as never))) return false;
      if (c.gt !== undefined && !(value !== null && value !== undefined && (value as never) > (c.gt as never))) return false;
      if (c.lt !== undefined && !(value !== null && value !== undefined && (value as never) < (c.lt as never))) return false;
    } else if (cond === null) {
      // Postgres semantics: a column never written is NULL.
      if (value !== null && value !== undefined) return false;
    } else if (value !== cond) {
      return false;
    }
  }
  return true;
}
