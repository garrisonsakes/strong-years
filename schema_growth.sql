-- =============================================================================
-- Growth engine migration (workers/growth): metrics -> baselines -> scores -> winners -> remix / boost queues
--                                            -> bandit arms -> spend budgets / ledger / governor decisions
-- -----------------------------------------------------------------------------
-- Apply AFTER schema.sql:  psql "$SUPABASE_DB_URL" -f schema.sql -f schema_growth.sql   (idempotent: IF NOT EXISTS)
-- Security is identical to schema.sql §11: RLS enabled + forced on every table, deny by default, no anon or
-- authenticated grants, service_role only (n8n and the workers). spend_ledger and governor_decisions are
-- APPEND-ONLY: a trigger rejects UPDATE and DELETE for every role, service_role included.
-- Nothing here spends, posts or publishes: rows are queues, plans and decisions for n8n and a human.
-- =============================================================================

-- ---------- 1. post_metrics: one PostMetrics snapshot per post x horizon --------------------------------------
create table if not exists post_metrics (
  id                  bigserial primary key,
  post_id             uuid not null references posts(id) on delete cascade,
  page_id             uuid references pages(id),
  platform            platform_code not null,
  horizon_h           int  not null check (horizon_h in (1, 3, 6, 24, 72)),
  published_at        timestamptz not null,
  captured_at         timestamptz not null,
  age_h               numeric(8,3) not null check (age_h >= 0),
  views               bigint check (views >= 0),
  reach               bigint check (reach >= 0),
  likes               bigint check (likes >= 0),
  comments            bigint check (comments >= 0),
  shares              bigint check (shares >= 0),
  saves               bigint check (saves >= 0),
  profile_visits      bigint check (profile_visits >= 0),
  link_clicks         bigint check (link_clicks >= 0),
  follows             bigint check (follows >= 0),
  avg_watch_pct       numeric(5,2) check (avg_watch_pct between 0 and 100),
  keyword_comments    bigint check (keyword_comments >= 0),        -- comments rollup
  optins              bigint check (optins >= 0),                  -- dm_leads rollup (opted_in+) by attributed post
  buyers              bigint check (buyers >= 0),                  -- orders.attributed_post_id, one-time (ebook bundle, bumps)
  members             bigint check (members >= 0),                 -- orders.attributed_post_id, is_subscription
  interpolated        boolean not null default false,
  missing             text[] not null default '{}',                -- counters the platform does not expose
  rollups_as_of_now   text[] not null default '{}',
  source              text,
  created_at          timestamptz not null default now(),
  unique (post_id, horizon_h)
);
alter table post_metrics add column if not exists buyers bigint check (buyers >= 0);
create index if not exists ix_post_metrics_page on post_metrics(page_id, platform, horizon_h, published_at desc);

-- ---------- 2. page_baselines: robust centre/spread per component, EB-shrunk -------------------------------------
create table if not exists page_baselines (
  id              bigserial primary key,
  page_id         uuid not null references pages(id) on delete cascade,
  platform        platform_code not null,
  horizon_h       int  not null check (horizon_h in (1, 3, 6, 24, 72)),
  n_posts         int  not null default 0 check (n_posts >= 0),
  components      jsonb not null default '{}',                     -- {views:{center,spread,n,prior,shrink}, share_rate:..}
  config_version  text,
  computed_at     timestamptz not null default now(),
  unique (page_id, platform, horizon_h, computed_at)
);
create index if not exists ix_page_baselines_latest on page_baselines(page_id, platform, horizon_h, computed_at desc);

-- ---------- 3. post_scores: latest velocity score and class per post x horizon -----------------------------------
create table if not exists post_scores (
  id              bigserial primary key,
  post_id         uuid not null references posts(id) on delete cascade,
  page_id         uuid references pages(id),
  platform        platform_code not null,
  horizon_h       int  not null check (horizon_h in (1, 3, 6, 24, 72)),
  score           numeric(8,4),
  z               jsonb not null default '{}',
  components_used text[] not null default '{}',
  views           bigint,
  class           text not null check (class in ('WINNER','PROMISING','NORMAL','LOSER')),
  breakout        boolean not null default false,
  reward          numeric(6,4) check (reward between 0 and 1),
  conversion_norm numeric(6,4),
  reasons         text[] not null default '{}',
  config_version  text,
  scored_at       timestamptz not null default now(),
  unique (post_id, horizon_h)
);
create index if not exists ix_post_scores_class on post_scores(class, scored_at desc);

-- ---------- 3b. post_scores_components: the scorecard (workers/growth/scorecard.py) -----------------------------------
-- One row per post x read (1 / 6 / 12 / 24 h, 7 d = 168 h). Every component is 0-100 against the page's rolling
-- baseline (empirical-Bayes shrunk); 50 = the page's typical post. Instagram reads under 24 h are provisional.
create table if not exists post_scores_components (
  id                  bigserial primary key,
  post_id             uuid not null references posts(id) on delete cascade,
  page_id             uuid references pages(id),
  platform            platform_code not null,
  horizon_h           int  not null check (horizon_h in (1, 6, 12, 24, 168)),
  provisional         boolean not null default false,
  denominator         text not null default 'reach' check (denominator in ('reach','views','engaged_views')),
  hook_score          numeric(5,2) check (hook_score between 0 and 100),
  body_score          numeric(5,2) check (body_score between 0 and 100),
  close_score         numeric(5,2) check (close_score between 0 and 100),
  shares_score        numeric(5,2) check (shares_score between 0 and 100),
  saves_score         numeric(5,2) check (saves_score between 0 and 100),
  conversation_score  numeric(5,2) check (conversation_score between 0 and 100),
  non_follower_score  numeric(5,2) check (non_follower_score between 0 and 100),
  conversion_score    numeric(5,2) check (conversion_score between 0 and 100),
  novelty_score       numeric(5,2) check (novelty_score between 0 and 100),
  composite           numeric(5,2) check (composite between 0 and 100),
  raw                 jsonb not null default '{}',
  hook_block_id       text,
  body_block_id       text,
  close_block_id      text,
  config_version      text,
  scored_at           timestamptz not null default now(),
  unique (post_id, horizon_h)
);
create index if not exists ix_psc_blocks on post_scores_components(hook_block_id, body_block_id, close_block_id);
create index if not exists ix_psc_page on post_scores_components(page_id, platform, horizon_h, scored_at desc);

-- ---------- 4. winners: first/last time a post was WINNER and what was queued for it ------------------------------
create table if not exists winners (
  post_id         uuid primary key references posts(id) on delete cascade,
  page_id         uuid references pages(id),
  platform        platform_code not null,
  best_score      numeric(8,4),
  best_horizon_h  int,
  breakout        boolean not null default false,
  first_seen_at   timestamptz not null default now(),
  last_seen_at    timestamptz not null default now(),
  actions         jsonb not null default '{}',                     -- {remix: n, boost: id, pin: action}
  status          text not null default 'open' check (status in ('open','actioned','expired','retracted'))
);

-- ---------- 5. remix_jobs: L3 derivative requests for OTHER pages (queued, never auto-published) ------------------
create table if not exists remix_jobs (
  id                  uuid primary key default gen_random_uuid(),
  source_post_id      uuid not null references posts(id) on delete cascade,
  source_page_id      uuid not null references pages(id),
  source_platform     platform_code not null,
  target_page_id      uuid not null references pages(id),
  status              text not null default 'queued'
                      check (status in ('queued','claimed','briefed','uniqueness_failed','compliance_failed','done','rejected','cancelled')),
  priority            int  not null default 90,
  earliest_at         timestamptz not null,
  preferred_slot_hour int  check (preferred_slot_hour between 0 and 23),
  level               text not null default 'L3' check (level in ('L3','L4')),
  payload             jsonb not null default '{}',                 -- grammar, pillar, format, speaker, requirements, thresholds
  brief_id            uuid references briefs(id) on delete set null,
  uniqueness_result   jsonb,
  attempts            int  not null default 0,
  last_error          text,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),
  check (source_page_id <> target_page_id),
  unique (source_post_id, target_page_id)
);
create or replace trigger trg_remix_jobs_updated before update on remix_jobs for each row execute function set_updated_at();
create index if not exists ix_remix_jobs_queue on remix_jobs(status, priority desc, earliest_at);

-- ---------- 6. boost_queue: partnership-ad / Spark candidates awaiting a human, then the governor ------------------
create table if not exists boost_queue (
  id                    uuid primary key default gen_random_uuid(),
  post_id               uuid not null references posts(id) on delete cascade,
  page_id               uuid references pages(id),
  platform              platform_code not null,
  channel               text not null check (channel in ('meta_partnership','tiktok_spark')),
  class                 text not null check (class in ('WINNER','PROMISING','NORMAL','LOSER')),
  score                 numeric(8,4),
  status                text not null default 'needs_human'
                        check (status in ('awaiting_human_approval','flagged_human','needs_human','approved','rejected',
                                          'planned','executed','paused','cancelled')),
  requested_daily_usd   numeric(10,2) not null default 0 check (requested_daily_usd >= 0),
  compliance            jsonb not null default '{}',               -- {verdict, hits, judge_passed, reasons}
  approved_by           text,
  approved_at           timestamptz,
  approved_max_daily_usd numeric(10,2) check (approved_max_daily_usd >= 0),
  ai_label_kept         boolean not null default true,
  created_at            timestamptz not null default now(),
  updated_at            timestamptz not null default now(),
  -- an approval needs all three fields, and only a compliance pass with a passing judge may be approved
  check (status <> 'approved' or (approved_by is not null and approved_at is not null and approved_max_daily_usd is not null)),
  check (status <> 'approved' or (compliance->>'verdict' = 'pass' and (compliance->>'judge_passed')::boolean is true))
);
create or replace trigger trg_boost_queue_updated before update on boost_queue for each row execute function set_updated_at();
create index if not exists ix_boost_queue_open on boost_queue(status, created_at) where status in ('awaiting_human_approval','flagged_human','needs_human','approved');

-- ---------- 7. bandit_arms: allocator posterior per page x platform x arm (decayed) ------------------------------
create table if not exists bandit_arms (
  page_id         uuid not null references pages(id) on delete cascade,
  platform        platform_code not null,
  arm_key         text not null,                                   -- pillar=P01|grammar=IF_EVERY|format=F02|speaker=CHANG|length=M
  alpha           numeric not null default 1 check (alpha >= 1),
  beta            numeric not null default 1 check (beta >= 1),
  pulls           int not null default 0 check (pulls >= 0),
  reward_sum      numeric not null default 0 check (reward_sum >= 0),
  last_reward_at  timestamptz,
  decayed_at      timestamptz not null default now(),
  primary key (page_id, platform, arm_key)
);

-- ---------- 8. spend_budgets: the approved-budget record the governor requires ------------------------------------
create table if not exists spend_budgets (
  id              uuid primary key default gen_random_uuid(),
  name            text not null,
  daily_cap_usd   numeric(12,2) not null check (daily_cap_usd >= 0),
  monthly_cap_usd numeric(12,2) not null check (monthly_cap_usd >= 0 and monthly_cap_usd >= daily_cap_usd),
  cash_floor_usd  numeric(12,2) not null check (cash_floor_usd >= 0),
  price_usd       numeric(6,2) not null default 25 check (price_usd in (25, 30)),
  status          text not null default 'draft' check (status in ('draft','approved','revoked','expired')),
  approved_by     text,
  approved_at     timestamptz,
  expires_at      timestamptz,
  notes           text,
  created_at      timestamptz not null default now(),
  check (status <> 'approved' or (approved_by is not null and approved_at is not null))
);

-- ---------- 9. spend_ledger: append-only, planned and reported spend by class ---------------------------------------
create table if not exists spend_ledger (
  id              bigserial primary key,
  budget_id       uuid references spend_budgets(id),
  day             date not null,
  spend_class     text not null check (spend_class in ('boost','retarget','cold')),
  ref             text,                                            -- post_id / campaign id
  amount_usd      numeric(12,2) not null check (amount_usd >= 0),
  source          text not null check (source in ('planned','reported')),
  decision_id     bigint,
  created_at      timestamptz not null default now()
);
create index if not exists ix_spend_ledger_day on spend_ledger(day, spend_class, source);

-- ---------- 10. governor_decisions: append-only decision log (mirrors the worker's hash-chained JSONL) ----------
create table if not exists governor_decisions (
  id                 bigserial primary key,
  decided_at         timestamptz not null,
  mode               text not null check (mode in ('dry_run','live')),
  status             text not null check (status in ('SCALE','HOLD','CUT','STOP')),
  valid              boolean not null,
  state_hash         text not null,
  config_fingerprint text not null,
  planned_daily_usd  numeric(12,2) not null default 0 check (planned_daily_usd >= 0),
  decision           jsonb not null,
  audit_hash         text,
  prev_hash          text,
  approved_by        text,                                         -- set when a human approves the plan in the review app
  approved_at        timestamptz,
  created_at         timestamptz not null default now()
);
create index if not exists ix_governor_decisions_time on governor_decisions(decided_at desc);

-- Append-only guard: no UPDATE / DELETE on the ledger or the decision log, for any role.
create or replace function growth_append_only() returns trigger
language plpgsql set search_path = public, pg_temp as $$
begin
  raise exception '% is append-only (no % allowed)', tg_table_name, tg_op using errcode = 'insufficient_privilege';
end $$;
drop trigger if exists trg_spend_ledger_append_only on spend_ledger;
create trigger trg_spend_ledger_append_only before update or delete on spend_ledger
  for each row execute function growth_append_only();
drop trigger if exists trg_governor_decisions_append_only on governor_decisions;
create trigger trg_governor_decisions_append_only before update or delete on governor_decisions
  for each row execute function growth_append_only();

-- Ledger sanity: a planned/reported day never exceeds the approved daily cap (belt and braces on the governor).
create or replace function growth_ledger_cap_check() returns trigger
language plpgsql set search_path = public, pg_temp as $$
declare cap numeric; total numeric;
begin
  if new.budget_id is null then return new; end if;
  select daily_cap_usd into cap from spend_budgets where id = new.budget_id and status = 'approved';
  if cap is null then
    raise exception 'spend_ledger: budget % is not approved', new.budget_id using errcode = 'check_violation';
  end if;
  select coalesce(sum(amount_usd), 0) into total from spend_ledger
   where budget_id = new.budget_id and day = new.day and source = new.source;
  if total + new.amount_usd > cap then
    raise exception 'spend_ledger: % spend for % would exceed the daily cap (% + % > %)', new.source, new.day, total, new.amount_usd, cap
      using errcode = 'check_violation';
  end if;
  return new;
end $$;
drop trigger if exists trg_spend_ledger_cap on spend_ledger;
create trigger trg_spend_ledger_cap before insert on spend_ledger for each row execute function growth_ledger_cap_check();

-- ---------- views ------------------------------------------------------------------------------------------------
create or replace view v_boost_approval_queue as
select b.id, b.post_id, pg.slug as page, b.platform, b.channel, b.class, b.score, b.status, b.requested_daily_usd,
       b.compliance->>'verdict' as compliance_verdict, (b.compliance->>'judge_passed')::boolean as judge_passed,
       po.permalink, b.created_at
from boost_queue b
join pages pg on pg.id = b.page_id
left join posts po on po.id = b.post_id
where b.status in ('awaiting_human_approval','flagged_human','needs_human')
order by b.score desc nulls last, b.created_at;

create or replace view v_remix_queue as
select r.id, r.status, r.priority, r.earliest_at, src.slug as source_page, tgt.slug as target_page, r.source_platform,
       r.payload->>'grammar' as grammar, r.payload->>'pillar' as pillar, r.payload->>'editorial_format' as editorial_format,
       r.payload->>'speaker' as speaker, r.brief_id, r.created_at
from remix_jobs r
join pages src on src.id = r.source_page_id
join pages tgt on tgt.id = r.target_page_id
where r.status = 'queued'
order by r.priority desc, r.earliest_at;

-- =============================================================================
-- SECURITY (same policy as schema.sql §11): deny by default, service_role only, append-only guards above.
-- =============================================================================
do $$ declare t text; begin
  foreach t in array array['post_metrics','page_baselines','post_scores','post_scores_components','winners',
                           'remix_jobs','boost_queue','bandit_arms','spend_budgets','spend_ledger','governor_decisions'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format('revoke all on table public.%I from public, anon, authenticated', t);
    execute format('grant all on table public.%I to service_role', t);
  end loop;
end $$;
revoke all on all sequences in schema public from public, anon, authenticated;
grant all on all sequences in schema public to service_role;
do $$ declare v text; begin
  foreach v in array array['v_boost_approval_queue','v_remix_queue'] loop
    execute format('alter view public.%I set (security_invoker = true)', v);
    execute format('revoke all on public.%I from public, anon, authenticated', v);
    execute format('grant select on public.%I to service_role', v);
  end loop;
end $$;
do $$ declare f record; begin
  for f in select p.oid::regprocedure as sig from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.proname in ('growth_append_only','growth_ledger_cap_check') loop
    execute format('alter function %s set search_path = public, pg_temp', f.sig);
    execute format('revoke all on function %s from public, anon, authenticated', f.sig);
    execute format('grant execute on function %s to service_role', f.sig);
  end loop;
end $$;
comment on table spend_ledger is 'Append-only. The governor (workers/growth/governor.py) plans; reported rows come from finance. No ad API is called by this system.';
comment on table governor_decisions is 'Append-only log of governor plans; mirrors the hash-chained JSONL audit in the worker.';
