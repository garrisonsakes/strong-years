-- Minimal stand-in for Supabase Vault on plain Postgres (tests only). On Supabase, vault.decrypted_secrets
-- decrypts pgsodium-encrypted secrets; here the stub just stores them so the access rules can be tested.
create schema if not exists vault;
create table if not exists vault.secrets (name text primary key, secret text not null);
create or replace view vault.decrypted_secrets as select name, secret as decrypted_secret from vault.secrets;
revoke all on schema vault from public;
