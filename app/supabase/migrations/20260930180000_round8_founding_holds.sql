-- Round 8 (AUDIT_FINAL §7): atomic founding cap.
-- A founding checkout takes a spot when its checkout session is created, inside one
-- transaction serialised by an advisory lock; fulfilment confirms it the same way.
-- Mirrors src/lib/founding.ts (used by the in-memory store).

create table if not exists public.founding_holds (
  id uuid primary key default gen_random_uuid(),
  intent_id uuid not null unique,
  status text not null default 'held' check (status in ('held','confirmed','released')),
  expires_at timestamptz not null,
  confirmed_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists founding_holds_status_idx on public.founding_holds (status, expires_at);
alter table public.founding_holds enable row level security;
revoke all on public.founding_holds from anon, authenticated;

-- Spots taken = founding memberships (refunds release the spot) + unexpired holds
-- + confirmed holds whose membership row isn't written yet. One checkout's own hold
-- can be left out (p_except).
create or replace function public.founding_taken(p_except uuid default null)
returns int language sql stable as $$
  select
    (select count(*) from public.memberships m
      where m.founding and m.status in ('active','past_due','paused','canceled','expired'))::int
  + (select count(*) from public.founding_holds h
      where h.status = 'held' and h.expires_at > now()
        and (p_except is null or h.intent_id <> p_except))::int
  + (select count(*) from public.founding_holds h
      where h.status = 'confirmed'
        and (p_except is null or h.intent_id <> p_except)
        and not exists (select 1 from public.memberships m where m.checkout_intent_id = h.intent_id))::int
$$;

create or replace function public.reserve_founding_spot(p_intent_id uuid, p_cap int, p_hold_minutes int)
returns boolean language plpgsql security definer set search_path = public as $$
begin
  -- Every reservation and confirmation queues here, so the count and the insert
  -- can't interleave (8 or 50 buyers at cap-2 get exactly 2 spots).
  perform pg_advisory_xact_lock(hashtext('strong_years_founding_cap'));
  if public.founding_taken(p_intent_id) >= p_cap then
    return false;
  end if;
  insert into public.founding_holds (intent_id, status, expires_at)
  values (p_intent_id, 'held', now() + make_interval(mins => p_hold_minutes))
  on conflict (intent_id) do update
    set status = 'held', expires_at = excluded.expires_at, confirmed_at = null;
  return true;
end $$;

create or replace function public.confirm_founding_spot(p_intent_id uuid, p_cap int)
returns boolean language plpgsql security definer set search_path = public as $$
declare h public.founding_holds;
begin
  perform pg_advisory_xact_lock(hashtext('strong_years_founding_cap'));
  select * into h from public.founding_holds where intent_id = p_intent_id;
  if found and h.status = 'confirmed' then
    return true;
  end if;
  if not (found and h.status = 'held' and h.expires_at > now())
     and public.founding_taken(p_intent_id) >= p_cap then
    update public.founding_holds set status = 'released' where intent_id = p_intent_id;
    return false;
  end if;
  insert into public.founding_holds (intent_id, status, expires_at, confirmed_at)
  values (p_intent_id, 'confirmed', now(), now())
  on conflict (intent_id) do update set status = 'confirmed', confirmed_at = now();
  return true;
end $$;

revoke all on function public.founding_taken(uuid) from public, anon, authenticated;
revoke all on function public.reserve_founding_spot(uuid, int, int) from public, anon, authenticated;
revoke all on function public.confirm_founding_spot(uuid, int) from public, anon, authenticated;
grant execute on function public.founding_taken(uuid) to service_role;
grant execute on function public.reserve_founding_spot(uuid, int, int) to service_role;
grant execute on function public.confirm_founding_spot(uuid, int) to service_role;
