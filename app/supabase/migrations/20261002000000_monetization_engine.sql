-- Monetization engine (MONETIZATION_ENGINE.md §5-6): one append-only offer_events table is the attribution table for
-- every offer surface. kind = exposure (an arm/offer was shown, with the price shown), conversion (orders/paid line,
-- with the revenue), ask (a group-quote or price-help request). Subjects are the signed visitor id and/or member id;
-- never an email. Two new request types for the human queue. RLS: service_role only. Idempotent.

create table if not exists public.offer_events (
  id uuid primary key default gen_random_uuid(),
  kind text not null check (kind in ('exposure','conversion','ask')),
  visitor_id text check (visitor_id is null or visitor_id ~ '^[0-9a-f-]{36}$'),
  member_id uuid references public.members(id) on delete set null,
  surface text not null check (length(surface) <= 40),
  experiment text check (experiment is null or length(experiment) <= 40),
  arm text check (arm is null or length(arm) <= 40),
  offer text not null check (length(offer) <= 40),
  rule text check (rule is null or length(rule) <= 40),
  shown_price_cents int check (shown_price_cents is null or shown_price_cents >= 0),
  revenue_cents int not null default 0 check (revenue_cents >= 0),
  channel text check (channel is null or length(channel) <= 20),
  ref text check (ref is null or length(ref) <= 120),
  day date not null default current_date,
  created_at timestamptz not null default now()
);
-- One exposure row per (subject, surface, experiment, offer, day); conversions are unique per order line (ref).
create unique index if not exists offer_events_exposure_day on public.offer_events
  (coalesce(visitor_id, ''), coalesce(member_id::text, ''), surface, coalesce(experiment, ''), offer, day) where kind = 'exposure';
create unique index if not exists offer_events_conversion_ref on public.offer_events (ref) where kind = 'conversion';
create index if not exists offer_events_vid on public.offer_events (visitor_id, kind);
create index if not exists offer_events_day on public.offer_events (day, kind);

alter table public.offer_events enable row level security;
alter table public.offer_events force row level security;
revoke all on public.offer_events from public, anon, authenticated;
grant all on public.offer_events to service_role;

alter table public.exceptions drop constraint if exists exceptions_type_check;
alter table public.exceptions add constraint exceptions_type_check
  check (type in ('compliance_flag','judge_disagreement','upload_auth_failure','refund_review','chargeback_review',
                  'plan_switch_request','consent_price_mismatch','crisis_escalation','boost_approval','affiliate_application',
                  'affiliate_fraud','coach_flag','clinical_interest','group_quote','price_help'));

alter table public.support_tickets drop constraint if exists support_tickets_reason_check;
alter table public.support_tickets add constraint support_tickets_reason_check check (reason in
  ('talk_to_human','crisis_followup','grief_followup','cancel_by_email','retest_drop','refund_review','dispute','privacy_request',
   'chat_offline_review','shopify_review','plan_change','group_quote','price_help'));
