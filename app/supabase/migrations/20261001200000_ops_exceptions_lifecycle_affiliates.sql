-- Ops round (Oct 1 2026): exceptions queue + audit trail, the governor's boost approvals, the 7am digest ledger,
-- the lifecycle email engine (sends ledger + consent), and affiliates (applications, referrals, commissions).
-- Every table: RLS on with NO policies (deny by default), nothing for anon/authenticated, all for service_role.
-- Idempotent: safe to run twice (deploy/scripts/db_migrate.sh runs every migration on every deploy).

create table if not exists public.exceptions (
  id uuid primary key default gen_random_uuid(),
  type text not null check (type in ('compliance_flag','judge_disagreement','upload_auth_failure','refund_review',
    'chargeback_review','plan_switch_request','consent_price_mismatch','crisis_escalation','boost_approval',
    'affiliate_application','affiliate_fraud')),
  status text not null default 'open' check (status in ('open','approved','rejected','resolved')),
  severity text not null default 'normal' check (severity in ('low','normal','high','critical')),
  source text not null,
  title text not null check (char_length(title) <= 200),
  detail text not null default '' check (char_length(detail) <= 4000),
  ref text check (ref is null or char_length(ref) <= 120),
  dedupe_key text not null check (char_length(dedupe_key) <= 200),
  payload jsonb not null default '{}'::jsonb,
  decided_by text,
  decided_at timestamptz,
  decision_note text,
  created_at timestamptz not null default now(),
  unique (type, dedupe_key),
  check (status = 'open' or (decided_by is not null and decided_at is not null))
);
create index if not exists ix_exceptions_open on public.exceptions(status, created_at) where status = 'open';

create table if not exists public.exception_events (
  id uuid primary key default gen_random_uuid(),
  exception_id uuid not null references public.exceptions(id) on delete restrict,
  action text not null check (action in ('created','repeated','approve','reject','resolve')),
  actor text not null,
  note text,
  created_at timestamptz not null default now()
);
create index if not exists ix_exception_events_item on public.exception_events(exception_id, created_at);

-- The audit trail is append-only for every role (service_role included).
create or replace function public.exception_events_append_only() returns trigger
language plpgsql set search_path = public, pg_temp as $$
begin
  raise exception 'exception_events is append-only' using errcode = 'insufficient_privilege';
end $$;
drop trigger if exists trg_exception_events_append_only on public.exception_events;
create trigger trg_exception_events_append_only before update or delete on public.exception_events
  for each row execute function public.exception_events_append_only();

create table if not exists public.governor_approvals (
  id uuid primary key default gen_random_uuid(),
  boost_id text not null unique,
  exception_id uuid not null references public.exceptions(id),
  approved_by text not null check (char_length(approved_by) > 0),
  approved_at timestamptz not null,
  max_daily_usd numeric(10,2) not null check (max_daily_usd >= 0),
  forwarded text not null default 'pending' check (forwarded in ('pending','sent','failed','not_configured')),
  created_at timestamptz not null default now()
);

create table if not exists public.digest_runs (
  id uuid primary key default gen_random_uuid(),
  day date not null unique,
  status text not null check (status in ('claimed','sent','failed')),
  sent_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.email_sends (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  member_id uuid,
  sequence text not null,
  step text not null,
  status text not null check (status in ('claimed','sent','skipped','failed')),
  reason text,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  unique (email, sequence, step)
);
create index if not exists ix_email_sends_recent on public.email_sends(email, sent_at);

create table if not exists public.email_prefs (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  lifecycle_opt_in boolean not null default true,
  coach_opt_in boolean not null default false,
  unsubscribed_at timestamptz,
  source text not null default 'signup',
  created_at timestamptz not null default now()
);

create table if not exists public.affiliates (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  name text not null,
  channel text not null,
  audience_note text not null default '',
  code text unique check (code is null or code ~ '^[A-Z0-9]{4,20}$'),
  status text not null default 'pending' check (status in ('pending','approved','rejected','suspended')),
  ftc_ack boolean not null check (ftc_ack),
  terms_version text not null,
  member_id uuid,
  exception_id uuid,
  approved_by text,
  approved_at timestamptz,
  created_at timestamptz not null default now(),
  check (status <> 'approved' or (code is not null and approved_by is not null and approved_at is not null))
);

create table if not exists public.affiliate_referrals (
  id uuid primary key default gen_random_uuid(),
  affiliate_id uuid not null references public.affiliates(id),
  member_id uuid not null unique,
  via text not null check (via in ('code','link')),
  started_at timestamptz not null,
  ends_at timestamptz not null,
  first_order_id text not null,
  created_at timestamptz not null default now(),
  check (ends_at <= started_at + interval '12 months 1 day')
);

create table if not exists public.affiliate_commissions (
  id uuid primary key default gen_random_uuid(),
  affiliate_id uuid not null references public.affiliates(id),
  referral_id uuid not null references public.affiliate_referrals(id),
  sy_order_id uuid not null unique,
  shopify_line_id text,
  base_cents int not null check (base_cents >= 0),
  commission_cents int not null check (commission_cents >= 0 and commission_cents <= ceil(base_cents * 0.30)),
  paid_at timestamptz not null,
  payable_after timestamptz not null,
  created_at timestamptz not null default now()
);

do $$
declare t text;
begin
  foreach t in array array['exceptions','exception_events','governor_approvals','digest_runs','email_sends','email_prefs',
                           'affiliates','affiliate_referrals','affiliate_commissions'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format('revoke all on public.%I from public, anon, authenticated', t);
    execute format('grant all on public.%I to service_role', t);
  end loop;
end $$;
revoke all on function public.exception_events_append_only() from public, anon, authenticated;
