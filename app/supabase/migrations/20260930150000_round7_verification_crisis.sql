-- Round 7 (AUDIT_FINAL §6)
-- R2-1: email verification. A checkout for an unverified email only gets a
-- purchase-scoped session; the first inbox proof sets email_verified_at and bumps
-- session_version (revoking any earlier checkout session). Full sessions require it.
alter table public.members add column if not exists email_verified_at timestamptz;

-- Backfill: members who already proved their inbox with a login link keep their
-- sessions. Everyone else verifies on their next login (one-time sign-out).
update public.members m
   set email_verified_at = s.first_used
  from (select member_id, min(used_at) as first_used
          from public.magic_links
         where used_at is not null
         group by member_id) s
 where s.member_id = m.id
   and m.email_verified_at is null;

-- Crisis: link the event to the flagged chat message, and record when the member
-- tapped "That's not what I meant" after seeing the resources (the alert stays logged).
alter table public.crisis_events add column if not exists chat_message_id uuid;
alter table public.crisis_events add column if not exists reply_message_id uuid;
alter table public.crisis_events add column if not exists member_cleared_at timestamptz;
create index if not exists crisis_events_chat_message_idx on public.crisis_events (chat_message_id);
