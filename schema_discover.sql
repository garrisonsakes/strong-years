-- =============================================================================
-- Niche discovery migration (workers/discover): crawled public top performers -> genes -> trends / transfer
-- opportunities -> remake briefs (script queue with provenance)
-- -----------------------------------------------------------------------------
-- Apply AFTER schema.sql and schema_growth.sql (v_post_attribution reads post_metrics):
--   psql "$SUPABASE_DB_URL" -f schema.sql -f schema_growth.sql -f schema_discover.sql      (idempotent)
-- Security = schema.sql §11: RLS enabled AND forced on every table, NO policies (deny by default), no anon or
-- authenticated grants, service_role only (n8n and the workers).
-- Stores public METADATA and transcript text only: never media, thumbnails, audio, cookies or credentials.
-- =============================================================================

-- ---------- 1. niche_posts: one row per (platform, external_id), refreshed by each crawl ---------------------
create table if not exists niche_posts (
  id                 bigserial primary key,
  platform           text not null check (platform in ('instagram','facebook','tiktok','youtube','threads','x')),
  external_id        text not null,
  url                text,
  creator            text,
  creator_followers  bigint check (creator_followers >= 0),
  published_at       timestamptz,
  crawled_at         timestamptz not null default now(),
  source             text not null check (source in ('youtube_api','tiktok_research','meta_graph','meta_content_library',
                                                     'threads_api','x_api','ytdlp','public_page')),
  seed               text,
  views              bigint check (views >= 0),
  engaged_views      bigint check (engaged_views >= 0),
  likes              bigint check (likes >= 0),
  comments           bigint check (comments >= 0),
  shares             bigint check (shares >= 0),
  saves              bigint check (saves >= 0),
  duration_s         numeric(8,2) check (duration_s >= 0),
  title_or_caption   text not null default '',
  hashtags           text not null default '',
  transcript         text not null default '',
  overlay_text       text not null default '',
  hook_line          text not null default '',
  cta_keyword        text,
  topic              text,
  claim_strength     text check (claim_strength in ('none','soft','strong')),
  -- derived genes: same hook / body / close decomposition as growth/scorecard (variants.decompose)
  pillar             text,
  format             text,
  lane               text check (lane in ('talking_head','insert','movement')),
  hook_grammar       text,
  hook_family        text,
  body_family        text,
  close_family       text,
  hook_block_id      text,
  body_block_id      text,
  close_block_id     text,
  genes              text[] not null default '{}',
  metric             text check (metric in ('views','engagement','none')),
  metric_value       numeric,
  rel_perf           numeric(12,3),
  rel_niche          numeric(12,3),
  velocity_per_h     numeric(14,3),
  content_sha        text not null,
  unique (platform, external_id)
);
create index if not exists ix_niche_posts_pub on niche_posts(platform, published_at desc);
create index if not exists ix_niche_posts_genes on niche_posts using gin (genes);

-- ---------- 2. niche_post_reads: hourly stream snapshots (velocity between reads) -------------------------------
create table if not exists niche_post_reads (
  id             bigserial primary key,
  niche_post_id  bigint not null references niche_posts(id) on delete cascade,
  captured_at    timestamptz not null default now(),
  metric_value   numeric check (metric_value >= 0),
  unique (niche_post_id, captured_at)
);

-- ---------- 3. niche_opportunities: cross-platform transfer records ------------------------------------------
create table if not exists niche_opportunities (
  id                 bigserial primary key,
  kind               text not null default 'transfer' check (kind in ('transfer')),
  direction          text not null check (direction in ('to_instagram','from_instagram')),
  gene               text not null,
  from_platform      text not null,
  to_platforms       text[] not null,
  lift               numeric(10,3),
  recent_mean        numeric(10,4),
  recent_n           int not null check (recent_n >= 0),
  evidence_post_ids  text[] not null default '{}',
  status             text not null default 'open' check (status in ('open','queued','done','dismissed')),
  created_at         timestamptz not null default now()
);
create index if not exists ix_niche_opps_open on niche_opportunities(status, created_at desc);

-- ---------- 4. remake_queue: plagiarism-guarded remake briefs -> script writer (provenance kept) ---------------
create table if not exists remake_queue (
  id             bigserial primary key,
  status         text not null default 'queued' check (status in ('queued','claimed','scripted','rejected')),
  reason         text not null,
  priority       int not null default 60,
  brief          jsonb not null,
  provenance     jsonb not null,
  must_pass      text[] not null default array['/compliance/scan','llm_judge','/uniqueness/check'],
  created_at     timestamptz not null default now(),
  -- the guard ran and passed, and provenance names the source post
  constraint remake_guard_passed check ((brief->'guard'->>'ok')::boolean is true),
  constraint remake_has_provenance check (provenance ? 'platform' and provenance ? 'external_id' and provenance ? 'content_sha')
);
create index if not exists ix_remake_queue on remake_queue(status, priority desc, created_at);

-- ---------- 5. discover_feeds: daily top-20 / weekly top-50 / allocator exploration / gate-refit snapshots -----
create table if not exists discover_feeds (
  id          bigserial primary key,
  kind        text not null check (kind in ('daily_top20','weekly_top50','exploration','gate_refit')),
  payload     jsonb not null,
  created_at  timestamptz not null default now()
);
create index if not exists ix_discover_feeds on discover_feeds(kind, created_at desc);

-- ---------- 6. v_post_attribution: our posts' views + attributed new MRR + one-time buyers (value_score input) --
-- New MRR = the plan price of a lead's FIRST subscription order (renewals are not new MRR); buyers = one-time orders.
create or replace view v_post_attribution as
select p.id as post_id,
       (select max(m.views) from post_metrics m where m.post_id = p.id) as views,
       coalesce((select sum(coalesce(o.plan_price_usd, o.amount_usd)) from orders o
                  where o.attributed_post_id = p.id and o.is_subscription
                    and not exists (select 1 from orders o2 where o2.lead_id = o.lead_id and o2.is_subscription
                                     and o2.created_at < o.created_at)), 0) as mrr_usd,
       (select count(*) from orders o where o.attributed_post_id = p.id and not o.is_subscription) as buyers
from posts p
where p.published_at > now() - interval '14 days';

-- =============================================================================
-- SECURITY: deny by default, service_role only.
-- =============================================================================
do $$ declare t text; begin
  foreach t in array array['niche_posts','niche_post_reads','niche_opportunities','remake_queue','discover_feeds'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('alter table public.%I force row level security', t);
    execute format('revoke all on table public.%I from public, anon, authenticated', t);
    execute format('grant all on table public.%I to service_role', t);
  end loop;
end $$;
revoke all on all sequences in schema public from public, anon, authenticated;
grant all on all sequences in schema public to service_role;
alter view public.v_post_attribution set (security_invoker = true);
revoke all on public.v_post_attribution from public, anon, authenticated;
grant select on public.v_post_attribution to service_role;
comment on table niche_posts is 'Public metadata of niche top performers (workers/discover). No media is stored or re-hosted.';
comment on table remake_queue is 'Remake briefs: our angle on a proven idea; guard = no reused line, no shared 7-word shingle, visual concept only.';
