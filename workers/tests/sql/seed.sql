-- Seed one of everything the probes need (runs as superuser, after schema.sql).
insert into vault.secrets values ('tok_ig_changyin', '{"access_token":"IGSECRET","user_id":"178"}') on conflict do nothing;
insert into pages (id, slug, display_name, disclosure_line)
  values ('00000000-0000-0000-0000-00000000000a', 'changyin', 'Chang Yin', 'AI characters') on conflict do nothing;
insert into page_accounts (id, page_id, platform, handle, token_vault_key)
  values ('00000000-0000-0000-0000-0000000000a1', '00000000-0000-0000-0000-00000000000a', 'instagram', 'changyin', 'tok_ig_changyin')
  on conflict do nothing;
insert into briefs (id, page_id, target_date, format)
  values ('00000000-0000-0000-0000-0000000000b1', '00000000-0000-0000-0000-00000000000a', current_date, 'R1_talk_prop') on conflict do nothing;
insert into scripts (id, brief_id, script) values ('00000000-0000-0000-0000-0000000000c1', '00000000-0000-0000-0000-0000000000b1', '{}')
  on conflict do nothing;
insert into videos (id, brief_id, script_id, page_id, status)
  values ('00000000-0000-0000-0000-0000000000d1', '00000000-0000-0000-0000-0000000000b1', '00000000-0000-0000-0000-0000000000c1',
          '00000000-0000-0000-0000-00000000000a', 'awaiting_approval') on conflict do nothing;
