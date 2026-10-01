-- Fails (raises) when any public table has RLS off, or anon/authenticated hold any privilege on a public table.
do $$
declare bad text;
begin
  select string_agg(c.relname, ', ' order by c.relname) into bad
    from pg_class c join pg_namespace n on n.oid = c.relnamespace
   where n.nspname = 'public' and c.relkind in ('r', 'p') and not c.relrowsecurity;
  if bad is not null then raise exception 'RLS is OFF on: %', bad; end if;
  -- anon and PUBLIC: no table privileges at all.
  select string_agg(distinct g.table_name || ':' || g.grantee, ', ') into bad
    from information_schema.role_table_grants g
    join pg_class c on c.relname = g.table_name
    join pg_namespace n on n.oid = c.relnamespace and n.nspname = g.table_schema
   where g.table_schema = 'public' and c.relkind in ('r', 'p') and g.grantee in ('anon', 'PUBLIC');
  if bad is not null then raise exception 'anon/PUBLIC hold table privileges: %', bad; end if;
  -- authenticated: only where a row policy for authenticated exists (e.g. the pipeline's reviewer read policies).
  select string_agg(distinct g.table_name, ', ') into bad
    from information_schema.role_table_grants g
    join pg_class c on c.relname = g.table_name
    join pg_namespace n on n.oid = c.relnamespace and n.nspname = g.table_schema
   where g.table_schema = 'public' and c.relkind in ('r', 'p') and g.grantee = 'authenticated'
     and not exists (select 1 from pg_policy p where p.polrelid = c.oid
                       and (p.polroles @> array[(select oid from pg_roles where rolname = 'authenticated')]
                            or p.polroles = array[0::oid]));
  if bad is not null then raise exception 'authenticated holds table privileges without a row policy on: %', bad; end if;
  raise notice 'RLS verification passed: % public tables, all RLS on, no anon grants, authenticated only behind row policies',
    (select count(*) from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relkind in ('r','p'));
end $$;
