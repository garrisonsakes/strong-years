-- Ascension ladder (BRIEF.md CANON UPDATE 4, ASCENSION.md): R2 Strength Age history uses public.retests (extra jsonb
-- holds the six-test fields); R3 coached cohorts, enrollments, check-ins and coach notes; R4 clinical-interest capture
-- (interest only, filed to the exceptions queue for the client's clinical team); exposure log for every in-app offer.
-- RLS on every new table, service_role only (same policy as every earlier migration). Idempotent.

-- Catalog, order kinds and exception types learn the coached rung.
alter table public.shopify_products drop constraint if exists shopify_products_entitlement_check;
alter table public.shopify_products add constraint shopify_products_entitlement_check
  check (entitlement in ('ebook','founding','standard','essentials','annual','gift','bump','coached'));

alter table public.sy_orders drop constraint if exists sy_orders_kind_check;
alter table public.sy_orders add constraint sy_orders_kind_check
  check (kind in ('trial_fee','front_end','bump','upsell_program','upsell_kit','downsell_printables','gift','membership_charge','coached_charge'));

alter table public.exceptions drop constraint if exists exceptions_type_check;
alter table public.exceptions add constraint exceptions_type_check
  check (type in ('compliance_flag','judge_disagreement','upload_auth_failure','refund_review','chargeback_review',
                  'plan_switch_request','consent_price_mismatch','crisis_escalation','boost_approval','affiliate_application',
                  'affiliate_fraud','coach_flag','clinical_interest'));

create table if not exists public.coach_cohorts (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  coach_name text,
  coach_credential text,
  coach_bio text,
  cap int not null check (cap between 1 and 60),
  status text not null default 'draft' check (status in ('draft','open','running','closed')),
  starts_on date,
  call_url text check (call_url is null or call_url ~ '^https://'),
  call_time text,
  created_at timestamptz not null default now(),
  -- A cohort is never sold without a named, credentialed coach.
  check (status = 'draft' or (coach_name is not null and coach_credential is not null))
);

create table if not exists public.coached_enrollments (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  cohort_id uuid not null references public.coach_cohorts(id),
  status text not null default 'active' check (status in ('active','ended','refunded')),
  sku text not null,
  shopify_order_id text not null unique,
  started_at timestamptz not null,
  paid_through timestamptz not null,
  created_at timestamptz not null default now()
);
create unique index if not exists coached_enrollments_one_active on public.coached_enrollments (member_id) where status = 'active';
create index if not exists coached_enrollments_cohort on public.coached_enrollments (cohort_id, status);

create table if not exists public.coach_checkins (
  id uuid primary key default gen_random_uuid(),
  enrollment_id uuid not null references public.coached_enrollments(id) on delete cascade,
  member_id uuid not null references public.members(id) on delete cascade,
  cohort_id uuid not null references public.coach_cohorts(id),
  week int not null check (week between 1 and 12),
  sessions_done int not null check (sessions_done between 0 and 14),
  effort int not null check (effort between 1 and 5),
  concern boolean not null default false,
  win text not null default '' check (length(win) <= 600),
  question text not null default '' check (length(question) <= 600),
  created_at timestamptz not null default now(),
  unique (enrollment_id, week)
);

create table if not exists public.coach_notes (
  id uuid primary key default gen_random_uuid(),
  enrollment_id uuid not null references public.coached_enrollments(id) on delete cascade,
  member_id uuid not null references public.members(id) on delete cascade,
  author text not null,
  body text not null check (length(body) between 1 and 2000),
  visible_to_member boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.clinical_interest (
  id uuid primary key default gen_random_uuid(),
  member_id uuid references public.members(id) on delete set null,
  name text not null check (length(name) between 1 and 80),
  email text not null check (email ~ '^[^\s@]+@[^\s@]+\.[^\s@]+$'),
  state text not null check (state ~ '^[A-Z]{2}$'),
  consent boolean not null check (consent),
  consent_text text not null,
  exception_id uuid,
  status text not null default 'new' check (status in ('new','sent_to_clinical_team','closed')),
  created_at timestamptz not null default now()
);

create table if not exists public.ascension_exposures (
  id uuid primary key default gen_random_uuid(),
  member_id uuid not null references public.members(id) on delete cascade,
  rung text not null check (rung in ('R3','R4','R5')),
  triggers text[] not null default '{}',
  cell text,
  day date not null,
  created_at timestamptz not null default now(),
  unique (member_id, rung, day)
);

do $$
declare t text;
begin
  foreach t in array array['coach_cohorts','coached_enrollments','coach_checkins','coach_notes','clinical_interest','ascension_exposures'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format('revoke all on public.%I from public, anon, authenticated', t);
    execute format('grant all on public.%I to service_role', t);
  end loop;
end $$;
