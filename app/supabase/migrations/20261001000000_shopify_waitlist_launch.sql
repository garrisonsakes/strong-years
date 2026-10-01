-- Round 10 (CANON UPDATE 2, Oct 1 2026): Shopify commerce, organic-first launch
-- (waitlist, launch sequence), post-level attribution, server-side conversion
-- events. RLS deny-by-default on every new table: anon/authenticated get nothing;
-- the app's server uses the service role. Mirrors src/lib/db/types.ts.

-- ---------- billing provider: shopify ----------
alter table public.memberships drop constraint if exists memberships_processor_check;
alter table public.memberships add constraint memberships_processor_check check (processor in ('stripe','braintree','shopify'));
alter table public.sy_orders drop constraint if exists sy_orders_processor_check;
alter table public.sy_orders add constraint sy_orders_processor_check check (processor in ('stripe','braintree','shopify'));
alter table public.checkout_intents drop constraint if exists checkout_intents_processor_check;
alter table public.checkout_intents add constraint checkout_intents_processor_check check (processor in ('stripe','braintree','shopify'));

alter table public.members add column if not exists shopify_customer_id text unique;
alter table public.members add column if not exists shopify_customer_updated_at timestamptz;

alter table public.memberships add column if not exists shopify_contract_id text unique;
alter table public.memberships add column if not exists shopify_origin_order_id text unique;
alter table public.memberships add column if not exists shopify_customer_id text;
alter table public.memberships add column if not exists shopify_revision bigint;
alter table public.memberships add column if not exists shopify_last_attempt_id text;
alter table public.memberships add column if not exists grace_until timestamptz;

alter table public.sy_orders add column if not exists shopify_order_id text;
alter table public.sy_orders add column if not exists shopify_line_id text;
create unique index if not exists sy_orders_shopify_line_kind on public.sy_orders (shopify_line_id, kind) where shopify_line_id is not null;
create index if not exists sy_orders_shopify_order on public.sy_orders (shopify_order_id) where shopify_order_id is not null;

alter table public.checkout_intents add column if not exists ad_consent boolean not null default false;

-- Sign-in by 6-digit email code (same row as the one-time link).
alter table public.magic_links add column if not exists code_hash text;
alter table public.magic_links add column if not exists attempts int not null default 0;

alter table public.support_tickets drop constraint if exists support_tickets_reason_check;
alter table public.support_tickets add constraint support_tickets_reason_check check (reason in
  ('talk_to_human','crisis_followup','grief_followup','cancel_by_email','retest_drop','refund_review','dispute','privacy_request','chat_offline_review','shopify_review'));

alter table public.consent_log drop constraint if exists consent_log_kind_check;
alter table public.consent_log add constraint consent_log_kind_check check (kind in
  ('auto_renew','sms','age_18','memory','partner_auto_renew','family_share','do_not_sell_share','ad_tracking','waitlist_email','waitlist_push'));

-- Catalog -> entitlement map. Shopify ids are DATA: insert one row per (variant, selling plan).
create table if not exists public.shopify_products (
  id uuid primary key default gen_random_uuid(),
  sku text not null unique,
  entitlement text not null check (entitlement in ('ebook','founding','standard','essentials','annual','gift','bump')),
  title text not null,
  shopify_product_id text not null,
  shopify_variant_id text not null,
  selling_plan_id text,
  inventory_item_id text,
  price_cents int not null check (price_cents >= 0),
  recurring_cents int check (recurring_cents >= 0),
  interval text check (interval in ('month','year')),
  includes_ebook boolean not null default false,
  gift_months int check (gift_months in (3,12)),
  cell text check (cell ~ '^[a-z0-9]{1,12}$'),
  cohort text check (cohort in ('founding','standard')),
  active boolean not null default true,
  created_at timestamptz not null default now()
);
create unique index if not exists shopify_products_variant_plan on public.shopify_products (shopify_variant_id, coalesce(selling_plan_id, ''));

create table if not exists public.shopify_webhooks (
  id text primary key,                -- X-Shopify-Webhook-Id
  topic text not null,
  status text not null check (status in ('processing','processed','ignored')),
  summary text,
  processed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.shopify_inventory (
  id uuid primary key default gen_random_uuid(),
  inventory_item_id text not null,
  location_id text not null,
  available int not null,
  shopify_updated_at timestamptz not null,
  created_at timestamptz not null default now(),
  unique (inventory_item_id, location_id)
);

-- ---------- organic-first launch ----------
create table if not exists public.launch_state (
  id text primary key,
  opened_at timestamptz,
  opened_by text,
  live_seen_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.waitlist (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  first_name text,
  status text not null check (status in ('pending','confirmed','unsubscribed')),
  confirm_token_hash text unique,
  confirm_expires_at timestamptz,
  last_signup_email_at timestamptz,
  confirmed_at timestamptz,
  unsubscribed_at timestamptz,
  ad_consent_requested boolean not null default false,
  visitor_id text,
  referral_code text not null unique,
  referred_by uuid references public.waitlist(id) on delete set null,
  referral_reward_at timestamptz,
  attribution jsonb,
  member_id uuid references public.members(id) on delete set null,
  converted_at timestamptz,
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);
create index if not exists waitlist_status on public.waitlist (status);
create index if not exists waitlist_referred_by on public.waitlist (referred_by);

create table if not exists public.waitlist_push (
  id uuid primary key default gen_random_uuid(),
  waitlist_id uuid not null references public.waitlist(id) on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  failures int not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists public.launch_sends (
  id uuid primary key default gen_random_uuid(),
  waitlist_id uuid not null references public.waitlist(id) on delete cascade,
  step text not null check (step in ('e1','e2','e3','p1','p2')),
  channel text not null check (channel in ('email','push')),
  status text not null check (status in ('claimed','sent','failed','skipped')),
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  unique (waitlist_id, step)                 -- the idempotency key under double cron
);

-- ---------- server-side conversion events ----------
create table if not exists public.conversion_outbox (
  id uuid primary key default gen_random_uuid(),
  platform text not null check (platform in ('meta','tiktok')),
  event_id text not null,
  event_name text not null check (event_name in ('Lead','CompleteRegistration','StartTrial','Purchase','Subscribe')),
  payload jsonb not null,
  email_hash text not null check (email_hash ~ '^[0-9a-f]{64}$'),
  status text not null check (status in ('pending','sent','failed','skipped')),
  attempts int not null default 0,
  next_attempt_at timestamptz not null default now(),
  last_error text,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  unique (platform, event_id)
);
create index if not exists conversion_outbox_due on public.conversion_outbox (status, next_attempt_at);

-- ---------- RLS: deny by default ----------
do $$
declare t text;
begin
  foreach t in array array['shopify_products','shopify_webhooks','shopify_inventory','launch_state','waitlist','waitlist_push','launch_sends','conversion_outbox']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on public.%I from anon, authenticated', t);
    execute format('grant all on public.%I to service_role', t);
  end loop;
end $$;

-- ---------- growth engine: per-post results (service role only) ----------
-- First-touch credit. Aggregates only: no emails, names or answers.
create or replace view public.growth_post_kpis
with (security_invoker = true) as
with
wl as (
  select attribution->>'post_id' as post_id,
         count(*) as waitlist_signups,
         count(*) filter (where confirmed_at is not null) as waitlist_confirmed
  from public.waitlist where attribution ? 'post_id' group by 1
),
q as (
  select attribution->>'post_id' as post_id, count(*) as quiz_optins
  from public.leads where attribution ? 'post_id' group by 1
),
books as (
  select m.attribution->>'post_id' as post_id, count(distinct m.id) as ebook_buyers
  from public.members m
  join public.sy_orders o on o.member_id = m.id and o.status = 'paid'
  left join public.shopify_products p on p.sku = o.offer_code
  where not m.is_demo and m.attribution ? 'post_id' and (o.kind = 'front_end' or coalesce(p.includes_ebook, false))
  group by 1
),
mem as (
  select m.attribution->>'post_id' as post_id,
         count(distinct m.id) as members,
         sum(case when ms.status in ('active','past_due') and not ms.cancel_at_period_end and ms.plan <> 'gift'
                  then (case when ms.interval = 'year' then round(ms.price_cents / 12.0) else ms.price_cents end)
                       + (case when ms.partner_seat then 800 else 0 end)
                  else 0 end)::bigint as mrr_cents
  from public.members m
  join public.memberships ms on ms.member_id = m.id and ms.plan <> 'gift'
  where not m.is_demo and m.attribution ? 'post_id'
  group by 1
)
select p.post_id,
       coalesce(wl.waitlist_signups, 0) as waitlist_signups,
       coalesce(wl.waitlist_confirmed, 0) as waitlist_confirmed,
       coalesce(q.quiz_optins, 0) as quiz_optins,
       coalesce(books.ebook_buyers, 0) as ebook_buyers,
       coalesce(mem.members, 0) as members,
       coalesce(mem.mrr_cents, 0) as mrr_cents
from (select post_id from wl union select post_id from q union select post_id from books union select post_id from mem) p
left join wl using (post_id) left join q using (post_id) left join books using (post_id) left join mem using (post_id);

revoke all on public.growth_post_kpis from public, anon, authenticated;
grant select on public.growth_post_kpis to service_role;

-- ---------- example catalog rows (replace the ids with your store's; README "Shopify setup") ----------
-- insert into public.shopify_products (sku, entitlement, title, shopify_product_id, shopify_variant_id, selling_plan_id, inventory_item_id, price_cents, recurring_cents, interval, includes_ebook, gift_months, cell, cohort) values
--  ('ebook_e12','ebook','Strong Years starter books','<product id>','<variant id $12>',null,null,1200,null,null,true,null,'e12',null),
--  ('founding_monthly','founding','Founding membership','<product id>','<founding variant id>','<selling plan id $25/mo>','<inventory item id>',2500,2500,'month',false,null,null,'founding');
