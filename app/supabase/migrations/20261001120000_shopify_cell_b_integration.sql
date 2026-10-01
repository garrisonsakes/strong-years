-- Integration round (INTEGRATION.md, Oct 1 2026): cell B on the free Shopify Subscriptions app.
-- Cell B ("$12 today = books + first month, then $25/mo") is the founding variant on the SAME monthly selling plan as
-- founding_monthly plus the STARTER12 first-payment-only discount code (STARTER12S on the standard plan after the
-- founding close). Two catalog rows now share (variant, selling plan) and are told apart by discount_code.
-- product_handle: /b and /join redirect to the product page (selling plans don't work with cart permalinks).
alter table public.shopify_products add column if not exists product_handle text;
alter table public.shopify_products add column if not exists discount_code text check (discount_code ~ '^[A-Z0-9]{2,32}$');
drop index if exists public.shopify_products_variant_plan;
create unique index if not exists shopify_products_variant_plan_code
  on public.shopify_products (shopify_variant_id, coalesce(selling_plan_id, ''), coalesce(discount_code, ''));

-- Essentials switch requests from the members app cancel flow (Shopify Subscriptions has no self-serve product swap;
-- a person handles the queue within 1 business day, or the Admin API when the app owns the contract).
create table if not exists public.plan_change_requests (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  membership_id uuid references public.memberships(id) on delete set null,
  shopify_contract_id text,
  from_plan text not null,
  to_plan text not null check (to_plan in ('essentials','annual')),
  status text not null default 'open' check (status in ('open','done','declined','failed')),
  method text not null check (method in ('admin_api','human_queue')),
  note text,
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);
alter table public.plan_change_requests enable row level security;
revoke all on public.plan_change_requests from anon, authenticated;
grant all on public.plan_change_requests to service_role;

-- example rows (replace ids; the verify phase of shopify/ writes out/members-catalog.<store>.json with these columns)
-- insert into public.shopify_products (sku, entitlement, title, shopify_product_id, shopify_variant_id, selling_plan_id, inventory_item_id, price_cents, recurring_cents, interval, includes_ebook, gift_months, cell, cohort, product_handle, discount_code) values
--  ('founding_monthly','founding','Founding membership','<product id>','<founding variant id>','<monthly plan id>','<inventory item id>',2500,2500,'month',false,null,null,'founding','founding-membership',null),
--  ('bundle_m12','founding','Starter books + first month of founding membership','<product id>','<founding variant id>','<monthly plan id>','<inventory item id>',1200,2500,'month',true,null,'m12','founding','founding-membership','STARTER12');

-- cancel-flow plan-change tickets
alter table public.support_tickets drop constraint if exists support_tickets_reason_check;
alter table public.support_tickets add constraint support_tickets_reason_check check (reason in
  ('talk_to_human','crisis_followup','grief_followup','cancel_by_email','retest_drop','refund_review','dispute','privacy_request','chat_offline_review','shopify_review','plan_change'));
