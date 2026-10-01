-- Blitz canon + processor abstraction (Sep 30 2026).
alter table public.memberships add column if not exists processor text not null default 'stripe' check (processor in ('stripe','braintree'));
alter table public.memberships add column if not exists price_cell text;          -- 'p2500' | 'p3000' | 'default' | 'standard'
alter table public.sy_orders add column if not exists processor text not null default 'stripe' check (processor in ('stripe','braintree'));
alter table public.checkout_intents add column if not exists processor text not null default 'stripe' check (processor in ('stripe','braintree'));
alter table public.checkout_intents add column if not exists price_cell text;
alter table public.checkout_intents add column if not exists visitor_id text;        -- sticky sy_vid cookie (price-test analysis)
create index if not exists sy_orders_processor_volume_idx on public.sy_orders (processor, status, created_at);
create index if not exists memberships_price_cell_idx on public.memberships (price_cell);
create index if not exists analytics_events_name_idx on public.analytics_events (name, created_at);

-- Texts are recorded as 'skipped' until SMS_ENABLED (10DLC approval).
alter table public.outbox drop constraint if exists outbox_status_check;
alter table public.outbox add constraint outbox_status_check check (status in ('sent','stubbed','skipped','failed'));
