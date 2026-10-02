-- CANON UPDATE 6 (BRIEF.md, Oct 2 2026): "$12 today = Starter Books + a 7-day trial of the founding membership;
-- first $25 charge on day 7, then every month". The trial is a selling plan with a trial period on a subscription app
-- that supports one (INTEGRATION.md §9: the free Shopify Subscriptions app has no trial option). The membership line
-- is $0 at checkout; the books are a separate $12 one-time line on the same order. Day 7 arrives as a renewal order
-- (orders/paid, source_name subscription) and converts the row; no renewal order by trial_end + grace = lapse.
alter table public.shopify_products add column if not exists trial_days int check (trial_days is null or (trial_days between 1 and 31));
-- memberships.trial_end already exists (Stripe path). Lookups by status + period end for the lapse/reminder crons:
create index if not exists memberships_shopify_trialing on public.memberships (current_period_end) where processor = 'shopify' and status = 'trialing';
-- memberships.arm gains 'T' (the canon-6 trial arm). The constraint name is Postgres's default for an inline check.
alter table public.memberships drop constraint if exists memberships_arm_check;
alter table public.memberships add constraint memberships_arm_check check (arm is null or arm in ('A','B','T'));
