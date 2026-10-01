-- =============================================================================
-- Chang Yin & Sun Yoon Content Factory: Supabase / Postgres 15+ schema
-- -----------------------------------------------------------------------------
-- State machine: ideas → briefs → scripts → compliance_reviews → shots → renders
--                → videos (masters) → variants (per platform) → posts → metrics
--                → comments / dm_leads / orders → experiments (bandit) → remix
-- Every provider call is a row in `renders` (idempotent on provider+request_id),
-- so cost, latency and failure rates are queryable per model, stage and page.
--
-- Apply with: psql "$SUPABASE_DB_URL" -f schema.sql   (idempotent-ish: IF NOT EXISTS)
-- Vector dims: 1024 for text embeddings (Voyage-3 / OpenAI text-embedding-3 @1024),
--              512 for ArcFace face embeddings.
-- =============================================================================

create extension if not exists pgcrypto;
create extension if not exists pg_trgm;
create extension if not exists vector;      -- Supabase: Database → Extensions → vector

-- ---------- enums ------------------------------------------------------------
do $$ begin
  create type platform_code as enum ('instagram','tiktok','youtube','facebook','threads','x');
exception when duplicate_object then null; end $$;

do $$ begin
  create type quality_tier as enum ('lean','standard','premium');
exception when duplicate_object then null; end $$;

do $$ begin
  create type risk_tier as enum ('green','yellow','red');
exception when duplicate_object then null; end $$;

do $$ begin
  create type content_format as enum ('R1_talk_prop','R2_prop_demo','R3_motion_exercise','R4_duo_dialogue','T1_text_native');
exception when duplicate_object then null; end $$;

do $$ begin
  create type brief_status as enum (
    'queued','claimed','scripting','compliance','human_review','shot_planning',
    'rendering','assembling','qa','awaiting_approval','approved','packaged',
    'scheduled','done','failed','blocked','cancelled');
exception when duplicate_object then null; end $$;

do $$ begin
  create type render_stage as enum ('keyframe','scene','motion','voice','lipsync','upscale','assemble','variant','qa','dub');
exception when duplicate_object then null; end $$;

do $$ begin
  create type job_status as enum ('submitted','running','completed','failed','timeout','cancelled');
exception when duplicate_object then null; end $$;

do $$ begin
  create type media_route as enum ('lipsync_talk','gen_scene','motion_transfer','library_broll','graphic');
exception when duplicate_object then null; end $$;

do $$ begin
  create type post_status as enum ('draft','scheduled','publishing','published','failed','removed_by_platform','deleted');
exception when duplicate_object then null; end $$;

do $$ begin
  create type account_status as enum ('setup','warming','active','restricted','paused','disabled');
exception when duplicate_object then null; end $$;

do $$ begin
  create type lead_stage as enum ('dm_sent','clicked','opted_in','trial','paid','churned','refunded','unsubscribed');
exception when duplicate_object then null; end $$;

-- ---------- helpers ----------------------------------------------------------
create or replace function set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at := now(); return new; end $$;

-- =============================================================================
-- 1. CHARACTERS
-- =============================================================================
create table if not exists characters (
  id                uuid primary key default gen_random_uuid(),
  slug              text unique not null,                 -- 'chang', 'sun', later 'maestro-es'
  display_name      text not null,                        -- 'Chang Yin'
  heritage_note     text,                                 -- how heritage is handled (see bible)
  bible_md          text not null default '',             -- injected into {{CHARACTER_BIBLE}}
  bible_version     int  not null default 1,
  voice_provider    text not null default 'elevenlabs',
  voice_id          text,                                 -- ElevenLabs voice id (designed voice)
  voice_model       text not null default 'eleven_v3',
  voice_settings    jsonb not null default '{"stability":0.5,"similarity_boost":0.8,"style":0.35}',
  voice_by_locale   jsonb not null default '{}',          -- {"es-US":{"voice_id":"..","model":".."}}
  face_centroid     vector(512),                          -- ArcFace centroid of approved refs
  is_ai_disclosed   boolean not null default true check (is_ai_disclosed), -- hard invariant
  active            boolean not null default true,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create or replace trigger trg_characters_updated before update on characters for each row execute function set_updated_at();

create table if not exists character_refs (
  id            uuid primary key default gen_random_uuid(),
  character_id  uuid not null references characters(id) on delete cascade,
  ref_code      text not null,                            -- 'CHANG_REF_FRONT', 'CHANG_REF_34L', 'CHANG_REF_BODY'
  kind          text not null check (kind in ('face','body','wardrobe','set','expression')),
  url           text not null,                            -- R2 public/presigned URL
  embedding     vector(512),                              -- ArcFace (face refs only)
  approved      boolean not null default false,
  notes         text,
  created_at    timestamptz not null default now(),
  unique (character_id, ref_code)
);

-- =============================================================================
-- 2. PAGES, PLATFORMS, ACCOUNTS
-- =============================================================================
create table if not exists platforms (
  code                  platform_code primary key,
  display_name          text not null,
  api_publish_cap_24h   int,          -- official cap per account per rolling 24h
  min_spacing_minutes   int not null default 60,
  max_duration_s        int,
  notes                 text
);

insert into platforms (code, display_name, api_publish_cap_24h, min_spacing_minutes, max_duration_s, notes) values
 ('instagram','Instagram Reels',100,90,180,'Graph API content publishing: 100 API posts / 24h / account; trial_params for Trial Reels'),
 ('facebook','Facebook Reels',30,60,90,'/{page_id}/video_reels: 30 API reels / 24h / Page; 3–90 s'),
 ('threads','Threads',250,45,300,'Threads API: 250 posts / 24h / profile'),
 ('tiktok','TikTok',null,90,300,'Content Posting API: 6 req/min per user token; creator daily cap returned by API; is_aigc flag; audited app required for public posts'),
 ('youtube','YouTube Shorts',null,90,180,'Data API: 100 videos.insert per project per day (quota) — shard projects; status.containsSyntheticMedia'),
 ('x','X',null,45,140,'Pay-per-use API: ~$0.015/post, ~$0.20 with URL — no links in body')
on conflict (code) do nothing;

create table if not exists pages (
  id                  uuid primary key default gen_random_uuid(),
  slug                text unique not null,               -- 'chang-strength', 'sun-says', 'chang-kitchen', 'maestro-chang-es'
  display_name        text not null,
  character_ids       uuid[] not null default '{}',
  locale              text not null default 'en-US',
  market              text not null default 'US',         -- 'US','EU','UK','LATAM','BR'
  timezone            text not null default 'America/New_York',
  page_dna            jsonb not null default '{}',        -- pillars, voice modifiers, sets, wardrobe, camera, caption style, hashtag bank, hook mix, music palette
  cta_keywords        text[] not null default '{}',       -- e.g. {STRONG,BALANCE,KITCHEN}
  deliverables        jsonb not null default '{}',        -- keyword → {"asset_url":..., "title":...}
  disclosure_line     text not null,                      -- FALLBACK "AI characters · built on published guidelines" until reviewer_signed; only then "AI characters · content reviewed by [NAME], PT, DPT"
  reviewer_name       text,
  reviewer_credential text,
  reviewer_signed     boolean not null default false,     -- SAFETY_RULES §7: no "reviewed by" claim until a contract is signed
  default_tier        quality_tier not null default 'lean',
  format_mix          jsonb not null default '{"R1_talk_prop":3,"R2_prop_demo":2,"R3_motion_exercise":1,"R4_duo_dialogue":1}',
  daily_budget_usd    numeric(10,2) not null default 40,
  auto_publish        boolean not null default false,     -- flips true after 14 clean days
  trusted_since       date,
  strikes_90d         int not null default 0,
  status              text not null default 'setup' check (status in ('setup','active','paused','retired')),
  parent_page_id      uuid references pages(id),          -- localized pages point to source page
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now()
);
create or replace trigger trg_pages_updated before update on pages for each row execute function set_updated_at();

create table if not exists page_accounts (
  id                    uuid primary key default gen_random_uuid(),
  page_id               uuid not null references pages(id) on delete cascade,
  platform              platform_code not null references platforms(code),
  handle                text not null,
  external_account_id   text,                             -- IG user id, FB page id, TT open_id, YT channel id, Threads user id, X user id
  publisher             text not null default 'official' check (publisher in ('official','upload_post','blotato','ayrshare','manual')),
  publisher_ref         text,                             -- upload-post "user" / blotato account id
  token_vault_key       text,                             -- Supabase Vault secret name (never store tokens in clear)
  gcp_project_shard     text,                             -- YouTube: which GCP project quota to use
  ai_profile_label      boolean not null default false,   -- IG "AI-generated profile" label set in app
  ai_label_verified_at  timestamptz,
  daily_post_target     int not null default 3,           -- ramps 1→3→6→9
  status                account_status not null default 'setup',
  warmup_started_at     date,
  last_publish_at       timestamptz,
  health_notes          text,
  created_at            timestamptz not null default now(),
  unique (page_id, platform),
  unique (platform, handle)
);

-- =============================================================================
-- 3. PROMPTS, EVIDENCE, BLOCKED CLAIMS, GLOSSARY
-- =============================================================================
create table if not exists prompt_versions (
  id            uuid primary key default gen_random_uuid(),
  prompt_key    text not null,     -- 'idea_miner','script_writer','compliance_judge','shot_planner','variant_generator','caption_writer','qa_vision','localization_adapter'
  version       int  not null,
  system_text   text not null,
  user_template text not null,
  model         text not null,
  temperature   numeric(3,2) not null default 0.7,
  max_tokens    int not null default 4000,
  active        boolean not null default false,
  notes         text,
  created_at    timestamptz not null default now(),
  unique (prompt_key, version)
);
create unique index if not exists ux_prompt_active on prompt_versions(prompt_key) where active;

create table if not exists evidence (
  id              text primary key,      -- 'E01' … mirrors EVIDENCE.md
  finding         text not null,
  grade           text not null,         -- A, A-, B+, B, C, D
  source_url      text,
  how_to_say      text,
  markets_allowed text[] not null default '{US,UK,EU,LATAM,BR}',
  last_verified   date,
  active          boolean not null default true
);

create table if not exists blocked_claims (
  id                  text primary key,  -- 'BC01'
  severity            text not null check (severity in ('block','revise','human')),
  regex               text,              -- null for semantic-only
  meaning             text not null,
  allowed_alternative text,
  active              boolean not null default true
);

create table if not exists glossary (
  locale      text not null,
  term        text not null,
  translation text not null,
  note        text,
  primary key (locale, term)
);

-- =============================================================================
-- 4. IDEAS → BRIEFS → SCRIPTS → COMPLIANCE → SHOTS
-- =============================================================================
create table if not exists ideas (
  id                  uuid primary key default gen_random_uuid(),
  page_id             uuid references pages(id),          -- null = network-level idea
  cluster             text not null,
  pillar              text,
  working_title       text not null,
  angle               text,
  visual_proof        text,
  audience_pain       text[] default '{}',
  hook_options        jsonb not null default '[]',
  format              content_format,
  lead_character      text check (lead_character in ('chang','sun','both')),
  evidence_ids        text[] not null default '{}',
  needs_new_evidence  boolean not null default false,
  risk_tier           risk_tier not null default 'green',
  risk_notes          text,
  cta_keyword         text,
  explore             boolean not null default false,
  source_refs         jsonb not null default '[]',
  origin              text not null default 'miner' check (origin in ('miner','remix','human','localization','comment_reply')),
  parent_post_id      uuid,                               -- set for remixes (FK added below)
  embedding           vector(1024),
  status              text not null default 'new' check (status in ('new','approved','killed','briefed','cooldown')),
  created_at          timestamptz not null default now()
);
create index if not exists ix_ideas_status on ideas(status, risk_tier);
create index if not exists ix_ideas_cluster on ideas(cluster);

create table if not exists experiments (
  id              uuid primary key default gen_random_uuid(),
  name            text not null,
  hypothesis      text,
  unit            text not null check (unit in ('post','page','lead','offer')),
  primary_metric  text not null,            -- 'pi_24h','keyword_rate','rpm_funnel','trial_to_paid','mrr_per_lead'
  scope           jsonb not null default '{}',
  status          text not null default 'running' check (status in ('draft','running','stopped','concluded')),
  started_at      timestamptz default now(),
  ended_at        timestamptz,
  result          jsonb
);

create table if not exists experiment_arms (
  id              uuid primary key default gen_random_uuid(),
  experiment_id   uuid not null references experiments(id) on delete cascade,
  arm_key         text not null,            -- e.g. 'cluster=floor-rise|format=F3|hook=test|char=chang' or 'price=15'
  config          jsonb not null default '{}',
  alpha           numeric not null default 1,  -- Beta posterior (Thompson sampling)
  beta            numeric not null default 1,
  pulls           int not null default 0,
  reward_sum      numeric not null default 0,
  updated_at      timestamptz not null default now(),
  unique (experiment_id, arm_key)
);

create table if not exists briefs (
  id                  uuid primary key default gen_random_uuid(),
  idea_id             uuid references ideas(id),
  page_id             uuid not null references pages(id),
  target_date         date not null,
  slot_index          int  not null default 0,            -- 0..8 within the day
  format              content_format not null,             -- render archetype R1–R4 (drives model routing)
  editorial_format    text,                                -- CHARACTERS.md F## (content format)
  pillar              text,                                -- CHARACTERS.md P##
  hook_id             text,                                -- HOOKS.md H### if used
  speaker_mode        text check (speaker_mode in ('CHANG','SUN','DUO')),
  quality_tier        quality_tier not null default 'lean',
  locale              text not null default 'en-US',
  brief               jsonb not null default '{}',        -- idea + chosen hook + constraints handed to script writer
  status              brief_status not null default 'queued',
  priority            int not null default 50,            -- remix of winners = 90
  attempts            int not null default 0,
  claimed_at          timestamptz,
  claimed_by          text,                               -- n8n execution id
  parent_brief_id     uuid references briefs(id),         -- derivatives / localizations
  experiment_arm_id   uuid references experiment_arms(id),
  last_error          text,
  created_at          timestamptz not null default now(),
  updated_at          timestamptz not null default now(),
  unique (page_id, target_date, slot_index, locale)
);
create or replace trigger trg_briefs_updated before update on briefs for each row execute function set_updated_at();
create index if not exists ix_briefs_queue on briefs(status, priority desc, target_date);

create table if not exists scripts (
  id                  uuid primary key default gen_random_uuid(),
  brief_id            uuid not null references briefs(id) on delete cascade,
  attempt             int not null default 1,
  locale              text not null default 'en-US',
  script              jsonb not null,
  hook_text           text generated always as (script->'hook'->>'spoken') stored,
  full_text           text,                               -- concatenated spoken lines (for trigram + embeddings)
  word_count          int,
  model               text,
  prompt_version_id   uuid references prompt_versions(id),
  parent_script_id    uuid references scripts(id),        -- derivative/localization lineage
  embedding           vector(1024),
  status              text not null default 'draft' check (status in ('draft','approved','rejected','superseded')),
  input_tokens        int, output_tokens int, cost_usd numeric(10,4),
  created_at          timestamptz not null default now(),
  unique (brief_id, attempt, locale)
);
create index if not exists ix_scripts_trgm on scripts using gin (full_text gin_trgm_ops);

create table if not exists compliance_reviews (
  id              uuid primary key default gen_random_uuid(),
  script_id       uuid not null references scripts(id) on delete cascade,
  regex_hits      jsonb not null default '[]',
  verdict         text not null check (verdict in ('pass','revise','block','human')),
  confidence      numeric(3,2),
  result          jsonb not null default '{}',
  reviewer        text not null default 'llm' check (reviewer in ('llm','human','credentialed')),
  reviewer_name   text,
  decided_at      timestamptz not null default now()
);
create index if not exists ix_compliance_script on compliance_reviews(script_id, decided_at desc);

create table if not exists shots (
  id                uuid primary key default gen_random_uuid(),
  script_id         uuid not null references scripts(id) on delete cascade,
  n                 int not null,
  route             media_route not null,
  model_hint        text,
  start_s           numeric(6,2) not null,
  duration_s        numeric(6,2) not null,
  speaker           text,
  voice_lines       int[] default '{}',
  keyframe_prompt   text,
  reference_ids     text[] default '{}',
  motion_prompt     text,
  driving_asset_id  uuid,
  library_asset_id  uuid,
  graphic_spec      jsonb,
  layout            text default 'full',
  status            text not null default 'planned' check (status in ('planned','keyframed','rendered','failed','reused')),
  output_asset_id   uuid,
  unique (script_id, n)
);

-- =============================================================================
-- 5. ASSETS & RENDERS (every provider call)
-- =============================================================================
create table if not exists assets (
  id                uuid primary key default gen_random_uuid(),
  kind              text not null check (kind in ('keyframe','video_clip','audio','driving_video','broll','music','graphic','master','variant','thumbnail','reference')),
  storage_key       text not null unique,                -- r2://bucket/key
  public_url        text,
  mime              text,
  duration_s        numeric(8,3),
  width             int, height int, fps numeric(5,2),
  bytes             bigint,
  sha256            text,
  phash_seq         text[],                              -- per-second perceptual hashes (hex) for dup detection
  audio_fp          text,                                -- chromaprint fingerprint
  tags              text[] default '{}',
  character_id      uuid references characters(id),
  page_id           uuid references pages(id),
  source            text not null default 'generated' check (source in ('generated','library','performer','licensed','uploaded')),
  license           jsonb,                               -- performer release id, music license, etc.
  c2pa              jsonb,                               -- manifest summary (claim generator, ai assertions)
  created_at        timestamptz not null default now()
);
create index if not exists ix_assets_kind_tags on assets using gin (tags);

alter table shots drop constraint if exists fk_shots_driving;
alter table shots add constraint fk_shots_driving foreign key (driving_asset_id) references assets(id);
alter table shots drop constraint if exists fk_shots_library;
alter table shots add constraint fk_shots_library foreign key (library_asset_id) references assets(id);
alter table shots drop constraint if exists fk_shots_output;
alter table shots add constraint fk_shots_output foreign key (output_asset_id) references assets(id);

create table if not exists renders (
  id                uuid primary key default gen_random_uuid(),
  brief_id          uuid references briefs(id) on delete cascade,
  shot_id           uuid references shots(id) on delete set null,
  stage             render_stage not null,
  provider          text not null,                       -- 'fal','wavespeed','gemini','elevenlabs','heygen','higgsfield','self_gpu','assembler'
  model             text not null,                       -- 'fal-ai/kling-video/v3/standard/image-to-video'
  request_id        text,
  idempotency_key   text,                                -- brief_id:shot_n:stage:attempt
  status            job_status not null default 'submitted',
  attempt           int not null default 1,
  input             jsonb not null default '{}',
  output            jsonb,
  output_asset_id   uuid references assets(id),
  cost_usd          numeric(10,4),
  latency_s         numeric(10,2),
  error             text,
  submitted_at      timestamptz not null default now(),
  completed_at      timestamptz,
  unique (provider, request_id),
  unique (idempotency_key)
);
create index if not exists ix_renders_open on renders(status, provider) where status in ('submitted','running');
create index if not exists ix_renders_brief on renders(brief_id, stage);

create table if not exists videos (
  id                uuid primary key default gen_random_uuid(),
  brief_id          uuid not null references briefs(id) on delete cascade,
  script_id         uuid not null references scripts(id),
  page_id           uuid not null references pages(id),
  master_asset_id   uuid references assets(id),
  duration_s        numeric(6,2),
  qa_decision       text check (qa_decision in ('pass','review','fail')),
  qa_metrics        jsonb,                               -- deterministic metrics
  qa_vision         jsonb,                               -- 07_qa_vision_checker output
  human_decision    text check (human_decision in ('approved','rejected','fix_requested')),
  human_notes       text,
  reviewed_by       text,
  reviewed_at       timestamptz,
  total_cost_usd    numeric(10,4),
  status            text not null default 'qa' check (status in ('qa','awaiting_approval','approved','rejected','packaged','published','archived')),
  created_at        timestamptz not null default now()
);
create index if not exists ix_videos_status on videos(status);

create table if not exists variants (
  id                uuid primary key default gen_random_uuid(),
  video_id          uuid not null references videos(id) on delete cascade,
  platform          platform_code not null,
  asset_id          uuid references assets(id),           -- platform-specific render (hook text, cover, trims)
  packaging         jsonb not null default '{}',          -- 06_caption_hashtag_writer output for this platform
  caption           text,
  title             text,
  hashtags          text[] default '{}',
  on_screen_hook    text,
  max_sim_same_page numeric(4,3),                         -- uniqueness guard outputs
  max_sim_network   numeric(4,3),
  status            text not null default 'ready' check (status in ('ready','scheduled','published','skipped')),
  created_at        timestamptz not null default now(),
  unique (video_id, platform)
);

-- =============================================================================
-- 6. POSTS & METRICS
-- =============================================================================
create table if not exists posts (
  id                uuid primary key default gen_random_uuid(),
  variant_id        uuid references variants(id) on delete set null,
  page_account_id   uuid not null references page_accounts(id),
  platform          platform_code not null,
  kind              text not null default 'video' check (kind in ('video','text','image','carousel')),
  body_text         text,                                 -- for text-native Threads/X posts
  scheduled_at      timestamptz not null,
  published_at      timestamptz,
  external_post_id  text,
  permalink         text,
  utm               jsonb not null default '{}',          -- {source, medium, campaign, content}
  is_trial_reel     boolean not null default false,
  ai_label_applied  boolean not null default true,
  status            post_status not null default 'scheduled',
  attempts          int not null default 0,
  last_error        text,
  created_at        timestamptz not null default now(),
  unique (platform, external_post_id)
);
create index if not exists ix_posts_due on posts(status, scheduled_at);
create index if not exists ix_posts_account on posts(page_account_id, published_at desc);

alter table ideas drop constraint if exists fk_ideas_parent_post;
alter table ideas add constraint fk_ideas_parent_post foreign key (parent_post_id) references posts(id);

create table if not exists metrics (
  id                    bigserial primary key,
  post_id               uuid not null references posts(id) on delete cascade,
  captured_at           timestamptz not null default now(),
  hours_since_publish   numeric(8,2),
  views                 bigint, reach bigint,
  likes                 bigint, comments bigint, shares bigint, saves bigint,
  avg_watch_s           numeric(8,2),
  avg_watch_pct         numeric(5,2),                     -- avg_watch_s / duration
  completion_rate       numeric(5,2),
  hold_3s_rate          numeric(5,2),                     -- where exposed (else null; proxy computed in view)
  profile_visits        bigint, follows bigint,
  link_clicks           bigint,
  keyword_comments      bigint,                           -- from comments table rollup
  dm_optins             bigint,                           -- from dm_leads rollup
  revenue_usd           numeric(12,2),                    -- attributed (orders)
  raw                   jsonb
);
create index if not exists ix_metrics_post_time on metrics(post_id, captured_at desc);

create table if not exists comments (
  id                    uuid primary key default gen_random_uuid(),
  post_id               uuid references posts(id) on delete cascade,
  platform              platform_code not null,
  platform_comment_id   text not null,
  author_hash           text,                             -- sha256(handle) — no raw PII needed for mining
  text                  text not null,
  like_count            int default 0,
  commented_at          timestamptz,
  is_keyword            boolean not null default false,
  keyword               text,
  is_question           boolean not null default false,
  sentiment             text,
  crisis_flag           boolean not null default false,   -- self-harm / medical emergency language → human now
  used_in_idea_id       uuid references ideas(id),
  source                text not null default 'own' check (source in ('own','competitor')),
  competitor_handle     text,
  created_at            timestamptz not null default now(),
  unique (platform, platform_comment_id)
);
create index if not exists ix_comments_crisis on comments(crisis_flag) where crisis_flag;

-- =============================================================================
-- 7. DM LEADS, ORDERS (attribution)
-- =============================================================================
create table if not exists dm_leads (
  id                uuid primary key default gen_random_uuid(),
  page_id           uuid not null references pages(id),
  platform          platform_code not null,
  contact_ref       text not null,                        -- ManyChat subscriber id or IGSID/PSID
  keyword           text,
  source_post_id    uuid references posts(id),
  first_touch_at    timestamptz not null default now(),
  email             text,
  email_consent     boolean not null default false,
  sms_consent       boolean not null default false,
  stage             lead_stage not null default 'dm_sent',
  utm               jsonb not null default '{}',
  crisis_flag       boolean not null default false,
  mrr_usd           numeric(10,2) default 0,
  notes             text,
  updated_at        timestamptz not null default now(),
  unique (platform, contact_ref, keyword)
);
create or replace trigger trg_dm_leads_updated before update on dm_leads for each row execute function set_updated_at();
create index if not exists ix_dm_leads_post on dm_leads(source_post_id);

-- NOTE (AUDIT H11): pipeline attribution orders. The Strong Years app's table is `sy_orders`; the names never collide.
create table if not exists orders (
  id                  uuid primary key default gen_random_uuid(),
  lead_id             uuid references dm_leads(id),
  provider            text not null check (provider in ('shopify','stripe','whop','skool','other')),
  external_order_id   text not null,
  sku                 text,
  amount_usd          numeric(10,2) not null,
  is_subscription     boolean not null default false,
  plan_price_usd      numeric(10,2),                      -- 12 / 15 / 20 / 25 / 30 split test
  attributed_post_id  uuid references posts(id),
  attribution_model   text not null default 'last_touch_dm' check (attribution_model in ('last_touch_dm','utm_last_click','coupon','first_touch')),
  utm                 jsonb not null default '{}',
  created_at          timestamptz not null default now(),
  unique (provider, external_order_id)
);

-- =============================================================================
-- 8. HOOK LIBRARY, BUDGETS, FAILURES, HUMAN QUEUE
-- =============================================================================
create table if not exists hook_library (
  id            uuid primary key default gen_random_uuid(),
  page_id       uuid references pages(id),                -- null = network-wide
  archetype     text not null,
  example_line  text not null,
  source_post_id uuid references posts(id),
  wins          int not null default 0,
  trials        int not null default 0,
  win_rate      numeric generated always as (case when trials > 0 then wins::numeric / trials else null end) stored,
  created_at    timestamptz not null default now()
);

create table if not exists budgets (
  page_id     uuid not null references pages(id),
  day         date not null,
  cap_usd     numeric(10,2) not null,
  spent_usd   numeric(10,2) not null default 0,
  primary key (page_id, day)
);

create table if not exists job_failures (             -- dead-letter queue
  id            bigserial primary key,
  workflow      text not null,
  node          text,
  brief_id      uuid references briefs(id) on delete set null,
  render_id     uuid references renders(id) on delete set null,
  payload       jsonb,
  error         text,
  retry_count   int not null default 0,
  resolved      boolean not null default false,
  created_at    timestamptz not null default now()
);
create index if not exists ix_job_failures_open on job_failures(resolved, created_at);

-- =============================================================================
-- 9. RPC FUNCTIONS (called by n8n via PostgREST /rpc/*)
-- =============================================================================

-- 9.1 Claim one queued brief atomically and return everything the workflow needs.
create or replace function claim_next_brief(p_worker text)
returns jsonb language plpgsql security definer as $$
declare
  b briefs%rowtype;
  result jsonb;
begin
  select * into b from briefs
   where status = 'queued'
     and target_date <= current_date + 1
   order by priority desc, target_date, slot_index
   limit 1
   for update skip locked;

  if not found then
    return null;
  end if;

  -- daily budget guard
  if exists (select 1 from budgets bu where bu.page_id = b.page_id and bu.day = current_date
             and bu.spent_usd >= bu.cap_usd) then
    return jsonb_build_object('skipped', true, 'reason', 'budget_cap', 'brief_id', b.id);
  end if;

  update briefs set status = 'claimed', claimed_at = now(), claimed_by = p_worker, attempts = attempts + 1
   where id = b.id;

  select jsonb_build_object(
    'brief',      to_jsonb(b) - 'status',
    'page',       (select to_jsonb(p) from pages p where p.id = b.page_id),
    'characters', (select coalesce(jsonb_agg(jsonb_build_object(
                      'slug', c.slug, 'display_name', c.display_name, 'bible_md', c.bible_md,
                      'voice_id', coalesce(c.voice_by_locale->b.locale->>'voice_id', c.voice_id),
                      'voice_model', coalesce(c.voice_by_locale->b.locale->>'model', c.voice_model),
                      'voice_settings', c.voice_settings,
                      'refs', (select coalesce(jsonb_agg(jsonb_build_object('code', r.ref_code, 'url', r.url, 'kind', r.kind)), '[]'::jsonb)
                                 from character_refs r where r.character_id = c.id and r.approved))), '[]'::jsonb)
                    from characters c
                    join pages p on c.id = any(p.character_ids)
                   where p.id = b.page_id and c.active),
    'prompts',    (select jsonb_object_agg(pv.prompt_key, jsonb_build_object(
                      'id', pv.id, 'system', pv.system_text, 'user', pv.user_template,
                      'model', pv.model, 'temperature', pv.temperature, 'max_tokens', pv.max_tokens))
                    from prompt_versions pv where pv.active),
    'evidence_index', (select coalesce(string_agg(e.id || ' | ' || e.finding || ' | ' || e.grade, E'\n' order by e.id), '')
                       from evidence e join pages p on p.id = b.page_id
                      where e.active and p.market = any(e.markets_allowed)),
    'blocked_claims', (select coalesce(jsonb_agg(to_jsonb(bc)), '[]'::jsonb) from blocked_claims bc where bc.active),
    'recent_hooks', (select coalesce(jsonb_agg(h.hook_text), '[]'::jsonb) from (
                       select s.hook_text from scripts s join briefs b2 on b2.id = s.brief_id
                        where b2.page_id = b.page_id and s.status = 'approved'
                        order by s.created_at desc limit 20) h),
    'hook_library', (select coalesce(jsonb_agg(jsonb_build_object('archetype', hl.archetype, 'line', hl.example_line, 'win_rate', hl.win_rate)), '[]'::jsonb)
                       from (select * from hook_library
                              where page_id = b.page_id or page_id is null
                              order by win_rate desc nulls last limit 15) hl),
    'accounts',   (select coalesce(jsonb_agg(jsonb_build_object('id', pa.id, 'platform', pa.platform, 'status', pa.status,
                      'daily_post_target', pa.daily_post_target, 'publisher', pa.publisher)), '[]'::jsonb)
                    from page_accounts pa where pa.page_id = b.page_id and pa.status in ('warming','active')),
    'driving_videos', (select coalesce(jsonb_agg(jsonb_build_object('id', a.id, 'tags', a.tags, 'duration_s', a.duration_s, 'url', a.public_url)), '[]'::jsonb)
                         from assets a where a.kind = 'driving_video'),
    'broll_index',    (select coalesce(jsonb_agg(jsonb_build_object('id', a.id, 'tags', a.tags, 'duration_s', a.duration_s)), '[]'::jsonb)
                         from (select * from assets where kind = 'broll' order by created_at desc limit 300) a)
  ) into result;

  return result;
end $$;

-- 9.2 Uniqueness guard: returns max cosine similarity vs same page (90d) and network same-platform (14d).
create or replace function script_similarity(p_page_id uuid, p_embedding vector, p_exclude_brief uuid default null)
returns jsonb language plpgsql stable as $$
declare
  same_page numeric;
  network   numeric;
begin
  select max(1 - (s.embedding <=> p_embedding)) into same_page
    from scripts s join briefs b on b.id = s.brief_id
   where b.page_id = p_page_id and s.embedding is not null
     and s.created_at > now() - interval '90 days'
     and (p_exclude_brief is null or b.id <> p_exclude_brief);

  select max(1 - (s.embedding <=> p_embedding)) into network
    from scripts s join briefs b on b.id = s.brief_id
   where b.page_id <> p_page_id and s.embedding is not null
     and s.created_at > now() - interval '14 days';

  return jsonb_build_object('same_page', coalesce(same_page, 0), 'network', coalesce(network, 0),
         'ok', coalesce(same_page, 0) <= 0.86 and coalesce(network, 0) <= 0.80);
end $$;

-- 9.3 Claim posts due for publishing (respects per-account spacing).
create or replace function claim_due_posts(p_limit int default 10)
returns setof jsonb language plpgsql security definer as $$
declare r record;
begin
  for r in
    select po.id
      from posts po
      join page_accounts pa on pa.id = po.page_account_id
      join platforms pl on pl.code = po.platform
     where po.status = 'scheduled'
       and po.scheduled_at <= now()
       and pa.status in ('warming','active')
       and (pa.last_publish_at is null or pa.last_publish_at < now() - make_interval(mins => pl.min_spacing_minutes))
     order by po.scheduled_at
     limit p_limit
     for update of po skip locked
  loop
    update posts set status = 'publishing', attempts = attempts + 1 where id = r.id;
    return next (
      select jsonb_build_object(
        'post', to_jsonb(po),
        'account', to_jsonb(pa) - 'token_vault_key',
        'token_vault_key', pa.token_vault_key,
        'variant', to_jsonb(v),
        'asset_url', a.public_url,
        'page_slug', pg.slug)
        from posts po
        join page_accounts pa on pa.id = po.page_account_id
        join pages pg on pg.id = pa.page_id
        left join variants v on v.id = po.variant_id
        left join assets a on a.id = v.asset_id
       where po.id = r.id);
  end loop;
end $$;

-- 9.4 Budget accounting (called after every render completes).
create or replace function add_spend(p_page_id uuid, p_usd numeric)
returns void language plpgsql as $$
begin
  insert into budgets(page_id, day, cap_usd, spent_usd)
  select p_page_id, current_date, p.daily_budget_usd, p_usd from pages p where p.id = p_page_id
  on conflict (page_id, day) do update set spent_usd = budgets.spent_usd + excluded.spent_usd;
end $$;

-- 9.5 Thompson-sampling reward update for a post's experiment arm.
create or replace function bandit_update(p_arm_id uuid, p_reward numeric)
returns void language plpgsql as $$
begin
  -- reward in [0,1]: 1 = winner (PI >= 2 & quality), 0.5 = average, 0 = dud
  update experiment_arms
     set alpha = alpha + greatest(0, least(1, p_reward)),
         beta  = beta  + (1 - greatest(0, least(1, p_reward))),
         pulls = pulls + 1,
         reward_sum = reward_sum + p_reward,
         updated_at = now()
   where id = p_arm_id;
end $$;

-- 9.6 Requeue a brief after QA failure (optionally only some shots need re-render).
create or replace function requeue_brief(p_brief_id uuid, p_reason text, p_rerender_shots int[] default '{}')
returns void language plpgsql as $$
begin
  update briefs
     set status = case when attempts >= 3 then 'failed'::brief_status else 'queued'::brief_status end,
         priority = least(priority + 10, 99),
         last_error = p_reason,
         brief = brief || jsonb_build_object('rerender_shots', to_jsonb(p_rerender_shots), 'regen_reason', p_reason),
         claimed_by = null
   where id = p_brief_id;
end $$;

-- 9.7 Create variants + posts atomically from the packaging step.
-- p_payload: {"video_id": uuid, "posts": [{"platform","asset_id","packaging","caption","title","hashtags","on_screen_hook",
--             "page_account_id","scheduled_at","status","kind","body_text","is_trial_reel","utm"}]}
create or replace function create_variants_and_posts(p_payload jsonb)
returns jsonb language plpgsql as $$
declare
  it jsonb; v_id uuid; n int := 0;
begin
  -- R5-14: the DB itself refuses a scheduled post for a video the judge has not approved (the n8n gate is upstream,
  -- but a buggy workflow edit must not be able to schedule unjudged content).
  if exists (select 1 from jsonb_array_elements(p_payload->'posts') x where coalesce(x->>'status','draft') = 'scheduled')
     and not exists (select 1 from videos v where v.id = (p_payload->>'video_id')::uuid and v.status in ('approved','packaged')) then
    raise exception 'create_variants_and_posts: video % is not approved; scheduled posts refused', p_payload->>'video_id';
  end if;
  for it in select * from jsonb_array_elements(p_payload->'posts') loop
    insert into variants(video_id, platform, asset_id, packaging, caption, title, hashtags, on_screen_hook, status)
    values ((p_payload->>'video_id')::uuid, (it->>'platform')::platform_code, nullif(it->>'asset_id','')::uuid,
            coalesce(it->'packaging','{}'), it->>'caption', it->>'title',
            coalesce((select array_agg(x) from jsonb_array_elements_text(coalesce(it->'hashtags','[]')) x), '{}'),
            it->>'on_screen_hook', 'scheduled')
    on conflict (video_id, platform) do update set packaging = excluded.packaging, caption = excluded.caption
    returning id into v_id;

    insert into posts(variant_id, page_account_id, platform, kind, body_text, scheduled_at, utm, is_trial_reel, status)
    values (v_id, (it->>'page_account_id')::uuid, (it->>'platform')::platform_code, coalesce(it->>'kind','video'),
            it->>'body_text', (it->>'scheduled_at')::timestamptz, coalesce(it->'utm','{}'),
            coalesce((it->>'is_trial_reel')::boolean, false), coalesce((it->>'status')::post_status, 'draft'));
    n := n + 1;
  end loop;
  update videos set status = 'packaged' where id = (p_payload->>'video_id')::uuid and status = 'approved';
  return jsonb_build_object('posts_created', n);
end $$;

-- 9.8 Human review decision from the review UI / Slack button.
create or replace function review_video(p_video_id uuid, p_decision text, p_reviewer text, p_notes text default null)
returns jsonb language plpgsql security definer as $$
declare v videos%rowtype;
begin
  select * into v from videos where id = p_video_id for update;
  if not found then return jsonb_build_object('ok', false, 'error', 'video not found'); end if;

  update videos set human_decision = p_decision, human_notes = p_notes, reviewed_by = p_reviewer, reviewed_at = now(),
                    status = case p_decision when 'approved' then 'approved' when 'rejected' then 'rejected' else status end
   where id = p_video_id;

  if p_decision = 'approved' then
    update posts po set status = 'scheduled',
           scheduled_at = greatest(po.scheduled_at, now() + interval '10 minutes')
      from variants va
     where va.id = po.variant_id and va.video_id = p_video_id and po.status = 'draft';
    update briefs set status = 'scheduled' where id = v.brief_id;
  elsif p_decision = 'rejected' then
    update posts po set status = 'deleted' from variants va
     where va.id = po.variant_id and va.video_id = p_video_id and po.status in ('draft','scheduled');
    update briefs set status = 'cancelled', last_error = p_notes where id = v.brief_id;
  elsif p_decision = 'fix_requested' then
    update posts po set status = 'deleted' from variants va
     where va.id = po.variant_id and va.video_id = p_video_id and po.status in ('draft','scheduled');
    perform requeue_brief(v.brief_id, 'human: ' || coalesce(p_notes,''), '{}');
  end if;
  return jsonb_build_object('ok', true, 'decision', p_decision);
end $$;

-- 9.9 Publishing token from Supabase Vault (service role only). Secret JSON: {"access_token":"...","user_id":"..."}.
create or replace function get_publish_token(p_account_id uuid)
returns jsonb language plpgsql security definer set search_path = public, pg_temp as $$
declare k text; sec text; r text;
begin
  -- Defence in depth (C3): even if EXECUTE were re-granted by mistake, only service_role decrypts.
  -- `role` is the caller's SET ROLE (PostgREST sets anon/authenticated/service_role); SECURITY DEFINER
  -- changes current_user to the owner but not this setting. Direct superuser sessions (role = none) are allowed.
  r := coalesce(nullif(current_setting('role', true), ''), 'none');
  if r <> 'service_role' and not (r = 'none' and exists (select 1 from pg_roles where rolname = session_user and rolsuper)) then
    raise exception 'get_publish_token: service_role only' using errcode = '42501';
  end if;
  select token_vault_key into k from page_accounts where id = p_account_id;
  if k is null then return jsonb_build_object('error', 'no token_vault_key'); end if;
  select decrypted_secret into sec from vault.decrypted_secrets where name = k;
  return coalesce(sec::jsonb, jsonb_build_object('error', 'secret not found'));
end $$;
revoke all on function get_publish_token(uuid) from public;   -- anon/authenticated revoked in §11.3

-- 9.10 Record a publish attempt. Failed posts retry up to 3× with 15-minute backoff.
create or replace function mark_post_result(p_post_id uuid, p_ok boolean, p_external_id text, p_permalink text, p_error text)
returns void language plpgsql as $$
begin
  if p_ok then
    update posts set status = 'published', published_at = now(), external_post_id = p_external_id,
                     permalink = p_permalink, last_error = null
     where id = p_post_id;
    update page_accounts pa set last_publish_at = now()
      from posts po where po.id = p_post_id and pa.id = po.page_account_id;
    update variants set status = 'published' from posts po where po.id = p_post_id and variants.id = po.variant_id;
  else
    update posts set status = case when attempts >= 3 then 'failed'::post_status else 'scheduled'::post_status end,
                     scheduled_at = now() + interval '15 minutes', last_error = p_error
     where id = p_post_id;
  end if;
end $$;

-- 9.11 Error-workflow sink: log failure and requeue the brief this execution had claimed.
create or replace function log_failure(p_execution_id text, p_workflow text, p_node text, p_error text, p_payload jsonb default '{}')
returns jsonb language plpgsql as $$
declare b_id uuid;
begin
  select id into b_id from briefs where claimed_by = p_execution_id order by claimed_at desc limit 1;
  insert into job_failures(workflow, node, brief_id, payload, error) values (p_workflow, p_node, b_id, p_payload, p_error);
  if b_id is not null then
    perform requeue_brief(b_id, left('node ' || coalesce(p_node,'?') || ': ' || coalesce(p_error,''), 500), '{}');
  end if;
  return jsonb_build_object('brief_id', b_id);
end $$;

-- =============================================================================
-- 10. VIEWS: performance, winners, human queue, cost
-- =============================================================================

-- Latest snapshot at or after ~24h for each post (falls back to latest available).
create or replace view v_post_24h as
select distinct on (m.post_id)
  m.post_id, po.platform, pa.page_id, po.published_at, m.hours_since_publish,
  m.views, m.likes, m.comments, m.shares, m.saves, m.avg_watch_pct, m.completion_rate,
  m.hold_3s_rate, m.keyword_comments, m.dm_optins, m.revenue_usd
from metrics m
join posts po on po.id = m.post_id
join page_accounts pa on pa.id = po.page_account_id
where m.hours_since_publish >= 20
order by m.post_id, m.hours_since_publish asc;

-- Page × platform baselines over trailing 14 days.
create or replace view v_page_baseline as
select page_id, platform,
  percentile_cont(0.5)  within group (order by views)                                  as median_views,
  percentile_cont(0.75) within group (order by (coalesce(shares,0)+coalesce(saves,0))::numeric / nullif(views,0)) as p75_share_save_rate,
  percentile_cont(0.75) within group (order by coalesce(keyword_comments,0)::numeric / nullif(views,0))           as p75_keyword_rate,
  percentile_cont(0.5)  within group (order by coalesce(revenue_usd,0) * 1000 / nullif(views,0))                  as median_rpm,
  count(*) as n
from v_post_24h
where published_at > now() - interval '14 days'
group by page_id, platform;

create or replace view v_post_scores as
select p.*,
  b.median_views,
  (p.views::numeric / nullif(b.median_views,0))                                         as pi,        -- performance index
  ((coalesce(p.shares,0)+coalesce(p.saves,0))::numeric / nullif(p.views,0))              as share_save_rate,
  (coalesce(p.keyword_comments,0)::numeric / nullif(p.views,0))                          as keyword_rate,
  (coalesce(p.revenue_usd,0) * 1000 / nullif(p.views,0))                                  as rpm_funnel,
  case
    when p.views >= 500000 or p.views::numeric / nullif(b.median_views,0) >= 5 then 'breakout'
    when p.views::numeric / nullif(b.median_views,0) >= 2
         and ( (coalesce(p.shares,0)+coalesce(p.saves,0))::numeric / nullif(p.views,0) >= b.p75_share_save_rate
            or coalesce(p.keyword_comments,0)::numeric / nullif(p.views,0) >= b.p75_keyword_rate) then 'winner'
    when coalesce(p.revenue_usd,0) * 1000 / nullif(p.views,0) >= 2 * nullif(b.median_rpm,0) then 'converter'
    when p.views::numeric / nullif(b.median_views,0) < 0.5 then 'dud'
    else 'average'
  end as label
from v_post_24h p
left join v_page_baseline b on b.page_id = p.page_id and b.platform = p.platform;

create or replace view v_human_queue as
select v.id as video_id, pg.slug as page, v.qa_decision, v.status, v.created_at,
       b.target_date, b.slot_index, s.script->>'title_internal' as title,
       (select cr.verdict from compliance_reviews cr where cr.script_id = s.id order by decided_at desc limit 1) as compliance_verdict,
       a.public_url as master_url
from videos v
join briefs b  on b.id = v.brief_id
join pages pg  on pg.id = v.page_id
join scripts s on s.id = v.script_id
left join assets a on a.id = v.master_asset_id
where v.status = 'awaiting_approval'
order by b.target_date, b.slot_index;

create or replace view v_cost_by_day as
select date_trunc('day', r.submitted_at)::date as day, b.page_id, r.stage, r.provider, r.model,
       count(*) as jobs,
       count(*) filter (where r.status = 'failed') as failed,
       sum(coalesce(r.cost_usd,0)) as usd,
       avg(r.latency_s) as avg_latency_s
from renders r left join briefs b on b.id = r.brief_id
group by 1,2,3,4,5;

create or replace view v_provider_health_30m as
select provider, model,
       count(*) as jobs,
       count(*) filter (where status in ('failed','timeout'))::numeric / nullif(count(*),0) as failure_rate
from renders
where submitted_at > now() - interval '30 minutes'
group by provider, model;

-- =============================================================================
-- 11. SECURITY (AUDIT_CODE C3, L14): deny by default, service_role only.
-- -----------------------------------------------------------------------------
-- Threat model: the anon key is public by design and `authenticated` is any signed-up
-- user. Neither may read tokens, prompts, scripts or PII, write any table, or run any RPC.
--   * n8n and the workers use service_role (BYPASSRLS) and are the only callers of RPCs.
--   * The review UI signs in as `authenticated` with the JWT claim app_role = 'reviewer'.
--     Reviewers may READ videos, posts and v_human_queue. They record decisions through the
--     n8n Review webhook, which calls review_video() with the service key. There is no
--     direct write path for reviewers.
--   * Publishing tokens live only in Supabase Vault (encrypted at rest with pgsodium).
--     page_accounts stores just the secret *name*. get_publish_token() is the only decrypt
--     path and only service_role can execute it.
-- Pipeline table `orders` is NOT the app's table: the Strong Years app uses `sy_orders`.
-- Run the pipeline in its own Supabase project, or at least keep the two names apart.
-- =============================================================================

-- Roles exist on Supabase. Create them on plain Postgres so this file (and the SQL tests) apply anywhere.
do $$ begin
  if not exists (select 1 from pg_roles where rolname = 'anon')          then create role anon nologin; end if;
  if not exists (select 1 from pg_roles where rolname = 'authenticated') then create role authenticated nologin; end if;
  if not exists (select 1 from pg_roles where rolname = 'service_role')  then create role service_role nologin bypassrls; end if;
end $$;

-- Reviewer claim from the PostgREST JWT (request.jwt.claims). Returns false outside PostgREST.
create or replace function is_reviewer() returns boolean
language sql stable set search_path = public, pg_temp as $$
  select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'app_role', '') = 'reviewer'
$$;

-- 11.1 RLS on EVERY table in public, with no permissive policy unless listed below (deny by default).
do $$ declare t record; begin
  for t in select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
            where n.nspname = 'public' and c.relkind in ('r', 'p')
              and not exists (select 1 from pg_depend d where d.objid = c.oid and d.deptype = 'e') loop
    execute format('alter table public.%I enable row level security', t.relname);
    execute format('alter table public.%I force row level security', t.relname);  -- owner too; service_role bypasses
  end loop;
end $$;

-- 11.2 Table / sequence / view privileges: nothing for anon; read-only reviewer surface for authenticated.
revoke all on all tables    in schema public from public, anon, authenticated;
revoke all on all sequences in schema public from public, anon, authenticated;
grant usage on schema public to anon, authenticated, service_role;
grant all on all tables    in schema public to service_role;
grant all on all sequences in schema public to service_role;
alter default privileges in schema public revoke all on tables    from public, anon, authenticated;
alter default privileges in schema public revoke all on sequences from public, anon, authenticated;
alter default privileges in schema public revoke execute on functions from public, anon, authenticated;

drop policy if exists reviewers_update_videos on videos;      -- removed: any user could approve (C3)
drop policy if exists reviewers_read_videos on videos;
create policy reviewers_read_videos on videos for select to authenticated using (is_reviewer());
drop policy if exists reviewers_read_posts on posts;
create policy reviewers_read_posts on posts for select to authenticated using (is_reviewer());
grant select on videos, posts to authenticated;               -- rows still filtered by the policies above

-- Views run with the caller's rights so RLS applies through them (PG15+).
do $$ declare v record; begin
  for v in select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
            where n.nspname = 'public' and c.relkind = 'v' loop
    execute format('alter view public.%I set (security_invoker = true)', v.relname);
  end loop;
end $$;
grant select on v_human_queue to authenticated;               -- needs the reviewer policy on underlying tables
drop policy if exists reviewers_read_briefs on briefs;
create policy reviewers_read_briefs on briefs for select to authenticated using (is_reviewer());
drop policy if exists reviewers_read_pages on pages;
create policy reviewers_read_pages on pages for select to authenticated using (is_reviewer());
drop policy if exists reviewers_read_scripts on scripts;
create policy reviewers_read_scripts on scripts for select to authenticated using (is_reviewer());
drop policy if exists reviewers_read_assets on assets;
create policy reviewers_read_assets on assets for select to authenticated using (is_reviewer());
drop policy if exists reviewers_read_compliance on compliance_reviews;
create policy reviewers_read_compliance on compliance_reviews for select to authenticated using (is_reviewer());
grant select (id, slug, display_name) on pages to authenticated;
grant select on briefs, scripts, assets, compliance_reviews to authenticated;
-- dm_leads, orders, page_accounts, prompt_versions, blocked_claims, budgets, ...: no grant, no policy.

-- 11.3 Functions: fixed search_path on every function (L14); EXECUTE for service_role only (C3).
do $$ declare f record; begin
  for f in select p.oid::regprocedure as sig from pg_proc p join pg_namespace n on n.oid = p.pronamespace
            where n.nspname = 'public' and p.prokind = 'f'
              and not exists (select 1 from pg_depend d where d.objid = p.oid and d.deptype = 'e') loop
    execute format('alter function %s set search_path = public, pg_temp', f.sig);
    execute format('revoke all on function %s from public, anon, authenticated', f.sig);
    execute format('grant execute on function %s to service_role', f.sig);
  end loop;
end $$;
-- RLS helper must stay callable by the roles whose policies use it (it only reads the caller's own JWT).
grant execute on function is_reviewer() to authenticated, anon;

-- 11.4 Token decryption: Vault only, service_role only. Belt and braces on the Vault schema itself.
do $$ begin
  if exists (select 1 from pg_namespace where nspname = 'vault') then
    execute 'revoke all on schema vault from anon, authenticated';
    execute 'revoke all on all tables in schema vault from anon, authenticated';
  end if;
end $$;
comment on column page_accounts.token_vault_key is
  'Name of the Supabase Vault secret (encrypted). Tokens are never stored in this table. Decrypt only via get_publish_token() as service_role.';

-- =============================================================================
-- 12. VECTOR INDEXES (create after ~1k rows for good HNSW quality)
-- =============================================================================
create index if not exists ix_scripts_embedding on scripts using hnsw (embedding vector_cosine_ops);
create index if not exists ix_ideas_embedding   on ideas   using hnsw (embedding vector_cosine_ops);
