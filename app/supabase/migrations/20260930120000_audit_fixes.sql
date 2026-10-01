-- Audit fixes (AUDIT_CODE.md, Sep 30 2026). Idempotent; apply after the two earlier migrations.

-- ---------- members: H4 phone lookup, one-refund-per-person, L7 revocation, CCPA opt-out
alter table public.members add column if not exists phone_digits text;
alter table public.members add column if not exists card_fingerprint text;
alter table public.members add column if not exists session_version int not null default 1;
alter table public.members add column if not exists ad_opt_out boolean not null default false;
create index if not exists members_phone_digits_idx on public.members (phone_digits);
create index if not exists members_card_fp_idx on public.members (card_fingerprint);

-- ---------- memberships: H8 one membership per checkout intent; H3 gift credit
alter table public.memberships add column if not exists checkout_intent_id uuid;
alter table public.memberships add column if not exists gift_credit_cents int not null default 0;
create unique index if not exists memberships_intent_uniq on public.memberships (checkout_intent_id) where checkout_intent_id is not null;

-- ---------- sy_orders: C4/H1 per-membership refunds; H8 no duplicate lines per intent
alter table public.sy_orders add column if not exists membership_id uuid references public.memberships(id) on delete set null;
alter table public.sy_orders add column if not exists amount_refunded_cents int not null default 0;
alter table public.sy_orders drop constraint if exists sy_orders_status_check;
alter table public.sy_orders drop constraint if exists orders_status_check;
alter table public.sy_orders add constraint sy_orders_status_check check (status in ('paid','refund_pending','refunded','disputed'));
create index if not exists sy_orders_membership_idx on public.sy_orders (membership_id);
create index if not exists sy_orders_invoice_idx on public.sy_orders (stripe_invoice);
create unique index if not exists sy_orders_intent_line_uniq on public.sy_orders (checkout_intent_id, kind, offer_code) where checkout_intent_id is not null;

-- ---------- checkout_intents: H8 atomic claim status; M2 one-time success login
alter table public.checkout_intents drop constraint if exists checkout_intents_status_check;
alter table public.checkout_intents add constraint checkout_intents_status_check check (status in ('open','fulfilling','complete','failed'));
alter table public.checkout_intents add column if not exists completed_at timestamptz;
alter table public.checkout_intents add column if not exists login_consumed_at timestamptz;

-- ---------- gifts: C1 claim link to the recipient (never a session from a code)
alter table public.gifts add column if not exists claim_token_hash text;
alter table public.gifts add column if not exists claim_expires_at timestamptz;
alter table public.gifts add column if not exists applied_as text check (applied_as in ('gift_membership','extension','credit'));

-- ---------- stripe_events: L2 in-flight claim
alter table public.stripe_events add column if not exists claimed_at timestamptz;

-- ---------- one guarantee refund per person (AUDIT_BUSINESS F08)
create table if not exists public.refund_ledger (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  card_fingerprint text,
  member_id uuid not null references public.members(id) on delete cascade,
  membership_id uuid not null references public.memberships(id) on delete cascade,
  amount_cents int not null,
  processor_refund_id text,
  created_at timestamptz not null default now()
);
create index if not exists refund_ledger_email_idx on public.refund_ledger (lower(email));
create index if not exists refund_ledger_fp_idx on public.refund_ledger (card_fingerprint);
alter table public.refund_ledger enable row level security;
revoke all on public.refund_ledger from anon, authenticated;

-- ---------- enum widenings
alter table public.support_tickets drop constraint if exists support_tickets_reason_check;
alter table public.reminders drop constraint if exists reminders_kind_check;
alter table public.reminders add constraint reminders_kind_check check (kind in ('pre_charge_48h','annual_30d','ca_annual_notice'));
alter table public.consent_log drop constraint if exists consent_log_kind_check;
alter table public.consent_log add constraint consent_log_kind_check
  check (kind in ('auto_renew','sms','age_18','memory','partner_auto_renew','family_share','do_not_sell_share'));

-- ---------- M13: column-level grants only (latent: used only if Supabase Auth is enabled)
revoke update on public.members from authenticated;
grant update (first_name, reminder_time, reminder_channel, timezone, memory_enabled, protected_weeks, ad_opt_out)
  on public.members to authenticated;

-- ---------- H7: aggregate KPIs in SQL (no 1,000-row cap)
create or replace function public.processor_volume_cents(p_processor text, p_since timestamptz) returns bigint
language sql stable security definer set search_path = public, pg_temp as $$
  select coalesce(sum(amount_cents), 0)::bigint from public.sy_orders
  where processor = p_processor and status = 'paid' and created_at >= p_since;
$$;
revoke all on function public.processor_volume_cents(text, timestamptz) from public, anon, authenticated;

create or replace function public.founding_cohort_count() returns int
language sql stable security definer set search_path = public, pg_temp as $$
  select count(*)::int from public.memberships
  where founding = true and status in ('active','past_due','paused','canceled','expired');
$$;

-- ---------- AUDIT_FINAL NEW-1: checkout never takes over an existing account
alter table public.checkout_intents add column if not exists auth_member_id uuid;
alter table public.checkout_intents add column if not exists buyer_is_owner boolean;
alter table public.checkout_intents add column if not exists verification text check (verification in ('pending','confirmed','rejected'));
alter table public.checkout_intents add column if not exists verify_token_hash text;
alter table public.checkout_intents add column if not exists verify_expires_at timestamptz;
alter table public.checkout_intents add column if not exists stripe_customer_id text;
create index if not exists checkout_intents_verify_idx on public.checkout_intents (verify_token_hash);
alter table public.memberships add column if not exists pending_verification boolean not null default false;
alter table public.memberships add column if not exists stripe_customer_id text;

-- ---------- Web push (retention nudges until SMS is approved)
create table if not exists public.push_subscriptions (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  endpoint text not null unique,
  p256dh text not null,
  auth text not null,
  user_agent text,
  failures int not null default 0,
  last_sent_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists push_subscriptions_member_idx on public.push_subscriptions (member_id);
alter table public.push_subscriptions enable row level security;
revoke all on public.push_subscriptions from anon, authenticated;
alter table public.outbox drop constraint if exists outbox_channel_check;
alter table public.outbox add constraint outbox_channel_check check (channel in ('email','sms','alert','push'));
alter table public.reminders drop constraint if exists reminders_kind_check;
alter table public.reminders add constraint reminders_kind_check check (kind in ('pre_charge_48h','annual_30d','ca_annual_notice','daily_nudge'));

-- ---------- Watermarked downloads are logged
create table if not exists public.download_events (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  file text not null,
  order_ref text not null,
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);
create index if not exists download_events_member_idx on public.download_events (member_id, created_at);
alter table public.download_events enable row level security;
revoke all on public.download_events from anon, authenticated;
