-- Round 5 audit (AUDIT_FINAL.md "Round 5: Shopify launch path").
-- refunds/create can be delivered before the orders/paid it belongs to (a retried delivery). The refund is parked
-- here by order line; orders/paid consults it and provisions nothing for a line that was already refunded.
create table if not exists public.shopify_early_refunds (
  id uuid primary key default gen_random_uuid(),
  shopify_order_id text not null,
  shopify_line_id text not null,
  shopify_refund_id text,
  amount_cents int,
  restock_type text,
  created_at timestamptz not null default now(),
  unique (shopify_line_id, shopify_refund_id)
);
alter table public.shopify_early_refunds enable row level security;
revoke all on public.shopify_early_refunds from anon, authenticated;
grant all on public.shopify_early_refunds to service_role;

-- Founding seat ledger (shopify/src/seatLedger.ts rules, executed by the members app): every inventory adjustment
-- carries a reference URI; processed URIs are stored so a redelivered webhook never adjusts twice.
create table if not exists public.shopify_seat_ledger (
  id uuid primary key default gen_random_uuid(),
  ref text not null unique,
  delta int not null,
  shopify_order_id text,
  created_at timestamptz not null default now()
);
alter table public.shopify_seat_ledger enable row level security;
revoke all on public.shopify_seat_ledger from anon, authenticated;
grant all on public.shopify_seat_ledger to service_role;
