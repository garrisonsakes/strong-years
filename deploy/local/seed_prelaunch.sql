-- Local prelaunch seed (make prelaunch-local), applied after deploy/scripts/db_migrate.sh --bootstrap --target app.
-- 1) What Supabase provides and plain Postgres doesn't: the PostgREST login role and service_role's table grants.
-- 2) A small, clearly-fake waitlist (every address ends in .example, attribution post ids start with LOCAL_) so the
--    prelaunch counters and /admin have something to show. Idempotent: re-running changes nothing.
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'authenticator') then
    execute format('create role authenticator login noinherit password %L', current_setting('sy.local_pw'));
  end if;
end $$;
grant anon, authenticated, service_role to authenticator;
grant usage on schema public to anon, authenticated, service_role;
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant execute on all functions in schema public to service_role;
alter default privileges in schema public grant all on tables to service_role;
alter default privileges in schema public grant all on sequences to service_role;

insert into public.waitlist (email, status, referral_code, confirmed_at, unsubscribed_at, attribution, created_at)
select format('local%s@waitlist.strongyears.example', i),
       s.status,
       format('LOCAL%s', lpad(i::text, 4, '0')),
       case when s.status = 'pending' then null else now() - (i || ' hours')::interval end,
       case when s.status = 'unsubscribed' then now() - interval '1 hour' else null end,
       jsonb_build_object('platform', s.platform, 'page', s.page, 'post_id', 'LOCAL_' || upper(s.platform) || '_' || i,
                          'keyword', 'STRONG', 'character', s.who),
       now() - (i || ' hours')::interval
from generate_series(1, 24) as i
cross join lateral (select
  (array['confirmed','confirmed','confirmed','pending','confirmed','unsubscribed'])[1 + i % 6] as status,
  (array['ig','tt','yt','fb'])[1 + i % 4] as platform,
  (array['changyin.strong','sunyoon.kitchen'])[1 + i % 2] as page,
  (array['chang','sun'])[1 + i % 2] as who) s
on conflict (email) do nothing;

notify pgrst, 'reload schema';
