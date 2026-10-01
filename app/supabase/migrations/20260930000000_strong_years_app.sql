-- =============================================================================
-- Strong Years members app: Supabase / Postgres schema
-- Column names match src/lib/db/types.ts exactly (the app's SupabaseStore reads
-- and writes these tables with the service-role key, server-side only).
-- RLS is ON for every table. The anon/authenticated roles get NO table access,
-- except members reading their own rows if you later move to Supabase Auth
-- (auth_user_id = auth.uid()). Public numbers go through SECURITY DEFINER RPCs.
-- Apply: supabase db push   (or paste into the SQL editor)
-- =============================================================================

create extension if not exists pgcrypto;

-- ---------- members -----------------------------------------------------------
create table if not exists public.members (
  id uuid primary key default gen_random_uuid(),
  auth_user_id uuid unique,                      -- optional link to auth.users
  email text not null unique,
  first_name text not null,
  phone text,
  sex text check (sex in ('woman','man','na')),
  age int check (age between 18 and 120),
  age_confirmed_at timestamptz,                  -- 18+ gate
  track text not null default 'steady' check (track in ('rebuild','steady','strong','iron')),
  active_program text,
  program_started_at timestamptz,
  sms_opt_in boolean not null default false,
  reminder_channel text not null default 'email' check (reminder_channel in ('sms','email')),
  reminder_time text not null default '07:30',
  timezone text not null default 'America/Los_Angeles',
  memory_enabled boolean not null default false, -- AI memory is opt-in
  stripe_customer_id text,
  stripe_payment_method text,
  attribution jsonb,                             -- utm_*, mc_id, fbclid (first touch)
  protected_weeks text[] not null default '{}',  -- "sick / traveling" weeks (Strong Weeks grace)
  is_demo boolean not null default false,
  created_at timestamptz not null default now()
);
create index if not exists members_stripe_customer_idx on public.members (stripe_customer_id);

-- ---------- memberships -------------------------------------------------------
create table if not exists public.memberships (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  plan text not null check (plan in ('monthly','essentials','annual','gift')),
  arm text check (arm in ('A','B')),             -- A = $1 trial, B = charge-today founding
  offer_code text not null,
  price_cents int not null,
  interval text not null check (interval in ('month','year','none')),
  status text not null check (status in ('incomplete','trialing','active','past_due','paused','canceled','refunded','expired')),
  founding boolean not null default false,
  stripe_subscription_id text unique,
  trial_end timestamptz,
  current_period_end timestamptz,
  first_paid_at timestamptz,
  guarantee_until timestamptz,
  cancel_at_period_end boolean not null default false,
  canceled_at timestamptz,
  paused_until timestamptz,
  partner_seat boolean not null default false,
  is_demo boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists memberships_member_idx on public.memberships (member_id);
create index if not exists memberships_due_idx on public.memberships (status, current_period_end);
create index if not exists memberships_founding_idx on public.memberships (founding, status);

-- ---------- sy_orders (renamed from orders: H11, avoids clash with the n8n schema) ------------------------------------------------------------
create table if not exists public.sy_orders (
  id uuid primary key default gen_random_uuid(),
  member_id uuid references public.members(id) on delete set null,
  email text not null,
  offer_code text not null,
  kind text not null check (kind in ('trial_fee','front_end','bump','upsell_program','upsell_kit','downsell_printables','gift','membership_charge')),
  description text not null,
  amount_cents int not null,
  status text not null check (status in ('paid','refunded','disputed')),
  stripe_payment_intent text,
  stripe_invoice text,
  checkout_intent_id uuid,
  is_demo boolean not null default false,
  created_at timestamptz not null default now()
);
create index if not exists sy_orders_member_idx on public.sy_orders (member_id);
create index if not exists sy_orders_pi_idx on public.sy_orders (stripe_payment_intent);
create unique index if not exists sy_orders_invoice_uniq on public.sy_orders (stripe_invoice) where stripe_invoice is not null and kind = 'membership_charge';

-- ---------- checkout intents (what the buyer saw, before paying) --------------
create table if not exists public.checkout_intents (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  first_name text not null,
  phone text,
  offer_code text not null,
  arm text,
  bump boolean not null default false,
  gentle boolean not null default false,
  amount_today_cents int not null,
  lines jsonb not null default '[]',
  membership_price_cents int,
  trial_days int not null default 0,
  consent_id uuid,
  sms_consent boolean not null default false,
  age_confirmed boolean not null default false,
  gift jsonb,
  attribution jsonb,
  lead_id uuid,
  status text not null default 'open' check (status in ('open','complete','failed')),
  stripe_session_id text,
  member_id uuid references public.members(id) on delete set null,
  created_at timestamptz not null default now()
);

-- ---------- consent log (ROSCA / state ARL: keep >= 3–4 years) ---------------
create table if not exists public.consent_log (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  member_id uuid references public.members(id) on delete set null,
  kind text not null check (kind in ('auto_renew','sms','age_18','memory','partner_auto_renew','family_share')),
  checked boolean not null,
  text_shown text not null,                     -- the exact rendered terms
  price_cents int,
  first_charge_at timestamptz,
  offer_code text,
  ip text,
  user_agent text,
  created_at timestamptz not null default now()
);
create index if not exists consent_email_idx on public.consent_log (email);

-- ---------- quiz leads (first-party only; never sent to ad platforms) --------
create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  first_name text not null,
  phone text,
  sms_consent boolean not null default false,
  quiz text not null check (quiz in ('strength_age','gut_energy')),
  profile_code text not null,
  result jsonb not null,
  answers jsonb not null,
  flags text[] not null default '{}',
  attribution jsonb,
  created_at timestamptz not null default now()
);
create index if not exists leads_email_idx on public.leads (email);

-- ---------- practice, retests ------------------------------------------------
create table if not exists public.practice_logs (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  day date not null,
  session_key text not null,
  track text not null,
  swap text,
  minutes int not null,
  created_at timestamptz not null default now(),
  unique (member_id, day)
);

create table if not exists public.retests (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  chair_reps int not null,
  balance_stage int not null check (balance_stage between 0 and 4),
  used_hands boolean not null default false,
  strength_age int not null,
  age_at_test int not null,
  extra jsonb not null default '{}',
  created_at timestamptz not null default now()
);
create index if not exists retests_member_idx on public.retests (member_id, created_at);

-- ---------- AI chat, memory, crisis ------------------------------------------
create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  character text not null check (character in ('chang','sun')),
  role text not null check (role in ('user','assistant','system_notice')),
  content text not null,
  safety text,
  created_at timestamptz not null default now()
);
create index if not exists chat_member_idx on public.chat_messages (member_id, character, created_at);

create table if not exists public.memory_items (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  fact text not null,
  sensitive boolean not null default false,     -- consumer health data (e.g. WA MHMDA)
  source text not null check (source in ('stub','llm','member')),
  created_at timestamptz not null default now()
);

create table if not exists public.crisis_events (
  id uuid primary key default gen_random_uuid(),
  member_id uuid references public.members(id) on delete set null,
  surface text not null check (surface in ('chat','dm','email')),
  category text not null check (category in ('self_harm','medical_emergency','abuse','grief')),
  detected_by text not null,
  excerpt text not null,
  alerted boolean not null default false,
  handled_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.support_tickets (
  id uuid primary key default gen_random_uuid(),
  member_id uuid references public.members(id) on delete set null,
  email text,
  reason text not null,
  message text not null,
  status text not null default 'open' check (status in ('open','closed')),
  created_at timestamptz not null default now()
);

-- ---------- partners, gifts, cancellations, reminders ------------------------
create table if not exists public.partners (
  id uuid primary key default gen_random_uuid(),
  owner_member_id uuid not null references public.members(id) on delete cascade,
  partner_name text not null,
  partner_email text not null,
  share_progress boolean not null default false,
  status text not null default 'active' check (status in ('active','removed')),
  created_at timestamptz not null default now()
);

create table if not exists public.gifts (
  id uuid primary key default gen_random_uuid(),
  gifter_email text not null,
  gifter_name text not null,
  recipient_name text not null,
  recipient_email text not null,
  message text not null default '',
  months int not null check (months in (3,12)),
  amount_cents int not null,
  code text not null unique,
  redeemed_member_id uuid references public.members(id) on delete set null,
  redeemed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.cancellations (
  id uuid primary key default gen_random_uuid(),
  membership_id uuid not null references public.memberships(id) on delete cascade,
  member_id uuid not null,
  reason text,
  offer_shown text,
  outcome text not null check (outcome in ('canceled','saved_pause','saved_downgrade','undone')),
  created_at timestamptz not null default now()
);

create table if not exists public.reminders (
  id uuid primary key default gen_random_uuid(),
  membership_id uuid not null references public.memberships(id) on delete cascade,
  kind text not null check (kind in ('pre_charge_48h','annual_30d')),
  charge_at timestamptz not null,
  sent_at timestamptz not null,
  created_at timestamptz not null default now(),
  unique (membership_id, kind, charge_at)
);

-- ---------- integrations ------------------------------------------------------
create table if not exists public.stripe_events (
  id text primary key,                          -- Stripe event id (idempotency)
  type text not null,
  livemode boolean not null default false,
  processed_at timestamptz,
  error text,
  summary text,
  created_at timestamptz not null default now()
);

create table if not exists public.analytics_events (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  member_id uuid,
  lead_id uuid,
  payload jsonb not null default '{}',          -- sanitised; no condition words, no answers
  sent_to_meta boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.outbox (
  id uuid primary key default gen_random_uuid(),
  channel text not null check (channel in ('email','sms','alert')),
  "to" text not null,
  subject text,
  body text not null,
  template text not null,
  provider text not null,
  status text not null check (status in ('sent','stubbed','failed')),
  created_at timestamptz not null default now()
);

create table if not exists public.magic_links (
  id uuid primary key default gen_random_uuid(),
  token_hash text not null unique,
  member_id uuid not null references public.members(id) on delete cascade,
  expires_at timestamptz not null,
  used_at timestamptz,
  created_at timestamptz not null default now()
);

-- ---------- updated_at trigger ------------------------------------------------
create or replace function public.touch_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;
drop trigger if exists memberships_touch on public.memberships;
create trigger memberships_touch before update on public.memberships for each row execute function public.touch_updated_at();

-- ---------- Row Level Security -----------------------------------------------
do $$
declare t text;
begin
  foreach t in array array['members','memberships','sy_orders','checkout_intents','consent_log','leads','practice_logs','retests',
    'chat_messages','memory_items','crisis_events','support_tickets','partners','gifts','cancellations','reminders',
    'stripe_events','analytics_events','outbox','magic_links']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on public.%I from anon, authenticated', t);
  end loop;
end $$;

-- Optional member self-access (only used if you add Supabase Auth on the client).
create policy members_self_read on public.members for select to authenticated using (auth_user_id = auth.uid());
create policy members_self_update on public.members for update to authenticated using (auth_user_id = auth.uid()) with check (auth_user_id = auth.uid());
create policy memberships_self_read on public.memberships for select to authenticated
  using (member_id in (select id from public.members where auth_user_id = auth.uid()));
create policy practice_self on public.practice_logs for all to authenticated
  using (member_id in (select id from public.members where auth_user_id = auth.uid()))
  with check (member_id in (select id from public.members where auth_user_id = auth.uid()));
create policy retests_self on public.retests for all to authenticated
  using (member_id in (select id from public.members where auth_user_id = auth.uid()))
  with check (member_id in (select id from public.members where auth_user_id = auth.uid()));
create policy memory_self on public.memory_items for select to authenticated
  using (member_id in (select id from public.members where auth_user_id = auth.uid()));
create policy memory_self_delete on public.memory_items for delete to authenticated
  using (member_id in (select id from public.members where auth_user_id = auth.uid()));
grant select, update on public.members to authenticated;
grant select on public.memberships to authenticated;
grant select, insert, update on public.practice_logs, public.retests to authenticated;
grant select, delete on public.memory_items to authenticated;
-- consent_log, crisis_events, stripe_events, sy_orders, leads: service role only.

-- ---------- Public RPC: the real founding cohort counter ----------------------
create or replace function public.founding_cohort_count() returns int
language sql stable security definer set search_path = public as $$
  select count(*)::int from public.memberships
  where founding = true and status in ('active','past_due','paused','canceled','expired');
$$;
revoke all on function public.founding_cohort_count() from public;
grant execute on function public.founding_cohort_count() to anon, authenticated;
