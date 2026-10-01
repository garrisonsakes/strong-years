"""schema_growth.sql on a real Postgres 16 (same harness as tests/test_schema_sql.py): applies idempotently after
schema.sql, every growth table is RLS-forced and service_role only, the ledger and decision log are append-only
for every role, the ledger cap trigger refuses spend above the approved daily cap, and a boost can't be marked
approved without a passing judge and a named human."""
from __future__ import annotations

import uuid

import pytest

from common import config
from tests.test_schema_sql import BASE, SCHEMA, SQL, _psql, as_role, denied

GROWTH = config.SPEC_DIR / "schema_growth.sql"
PAGE = "00000000-0000-0000-0000-00000000000a"
TABLES = ["post_metrics", "page_baselines", "post_scores", "winners", "remix_jobs", "boost_queue", "bandit_arms",
          "spend_budgets", "spend_ledger", "governor_decisions"]
pytestmark = pytest.mark.skipif(BASE is None, reason="no Postgres available (set PGTEST_DSN)")


@pytest.fixture(scope="module")
def db():
    name = "cs_growth_" + uuid.uuid4().hex[:8]
    _psql(None, sql=f"create database {name}")
    for f in (SQL / "vault_stub.sql", SCHEMA, GROWTH, GROWTH, SQL / "seed.sql"):     # growth schema applied twice: idempotent
        _psql(name, "-f", "-", stdin=f.read_text())
    _psql(name, sql="""
        insert into posts (id, page_account_id, platform, scheduled_at, published_at, status)
          values ('00000000-0000-0000-0000-0000000000e1', '00000000-0000-0000-0000-0000000000a1', 'instagram', now() - interval '1 day',
                  now() - interval '1 day', 'published')
          on conflict do nothing;
        insert into spend_budgets (id, name, daily_cap_usd, monthly_cap_usd, cash_floor_usd, status, approved_by, approved_at)
          values ('00000000-0000-0000-0000-0000000000f1', 'launch', 500, 9000, 20000, 'approved', 'garrison', now());
        insert into spend_budgets (id, name, daily_cap_usd, monthly_cap_usd, cash_floor_usd, status)
          values ('00000000-0000-0000-0000-0000000000f2', 'draft', 500, 9000, 20000, 'draft');
    """.replace("{PAGE}", PAGE))
    yield name
    _psql(None, sql=f"drop database if exists {name} with (force)", check=False)


def _val(p) -> str:
    return p.stdout.strip().splitlines()[-1]


def test_all_growth_tables_exist_with_rls_forced(db):
    rows = _psql(db, sql="select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' "
                         "and relkind='r' and relrowsecurity and relforcerowsecurity").stdout.split()
    assert set(TABLES) <= set(rows)
    no_rls = _psql(db, sql="select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' "
                           "and relkind='r' and not relrowsecurity").stdout.split()
    assert no_rls == []


@pytest.mark.parametrize("table", TABLES)
@pytest.mark.parametrize("role", ["anon", "authenticated"])
def test_anon_and_users_are_denied(db, table, role):
    assert denied(as_role(db, role, f"select * from {table}"))
    assert denied(as_role(db, role, f"delete from {table}"))
    assert denied(as_role(db, role, f"select * from {table}", '{"app_role":"reviewer"}'))


def test_no_anon_grants_on_growth_views_and_functions(db):
    grants = _psql(db, sql="select count(*) from information_schema.role_table_grants where table_schema='public' "
                           "and grantee in ('anon','authenticated') and table_name in ('v_boost_approval_queue','v_remix_queue')").stdout.strip()
    assert grants == "0"
    assert denied(as_role(db, "anon", "select * from v_boost_approval_queue"))
    fn = _psql(db, sql="select proname from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' "
                       "and proname in ('growth_append_only','growth_ledger_cap_check') and has_function_privilege('anon', p.oid, 'execute')").stdout.split()
    assert fn == []
    sp = _psql(db, sql="select count(*) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' "
                       "and proname in ('growth_append_only','growth_ledger_cap_check') "
                       "and not coalesce(p.proconfig::text,'') like '%search_path=public, pg_temp%'").stdout.strip()
    assert sp == "0"


def test_service_role_can_write_and_read_queues(db):
    p = as_role(db, "service_role", f"""
        insert into post_metrics (post_id, page_id, platform, horizon_h, published_at, captured_at, age_h, views, shares)
          values ('00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', 24, now() - interval '25 hours', now() - interval '1 hour', 24, 1200, 9);
        insert into remix_jobs (source_post_id, source_page_id, source_platform, target_page_id, earliest_at)
          select '00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', id, now() + interval '48 hours' from pages where id <> '{PAGE}' limit 1;
        select count(*) from v_remix_queue""")
    assert p.returncode == 0, p.stderr


def test_post_metrics_constraints(db):
    bad = [f"insert into post_metrics (post_id, page_id, platform, horizon_h, published_at, captured_at, age_h, views) values "
           f"('00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', 12, now(), now(), 1, 1)",         # horizon not allowed
           f"insert into post_metrics (post_id, page_id, platform, horizon_h, published_at, captured_at, age_h, views) values "
           f"('00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', 1, now(), now(), 1, -1)",          # negative views
           f"insert into post_metrics (post_id, page_id, platform, horizon_h, published_at, captured_at, age_h, avg_watch_pct) values "
           f"('00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', 1, now(), now(), 1, 140)"]        # pct > 100
    for stmt in bad:
        p = as_role(db, "service_role", stmt)
        assert p.returncode != 0 and ("check constraint" in p.stderr or "violates" in p.stderr), stmt


def test_remix_job_cannot_target_its_own_page(db):
    p = as_role(db, "service_role", f"insert into remix_jobs (source_post_id, source_page_id, source_platform, target_page_id, earliest_at) "
                                    f"values ('00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', '{PAGE}', now())")
    assert p.returncode != 0 and "violates check constraint" in p.stderr


def test_boost_cannot_be_approved_without_passing_judge_and_named_human(db):
    base = (f"insert into boost_queue (post_id, page_id, platform, channel, class, status, requested_daily_usd, compliance, "
            f"approved_by, approved_at, approved_max_daily_usd) values ('00000000-0000-0000-0000-0000000000e1', '{PAGE}', 'instagram', "
            f"'meta_partnership', 'WINNER', 'approved', 50, %s, %s, %s, %s)")
    ok = base % ("'{\"verdict\":\"pass\",\"judge_passed\":true}'", "'garrison'", "now()", "50")
    assert as_role(db, "service_role", ok).returncode == 0
    for comp, by, at, mx in (("'{\"verdict\":\"flagged\",\"judge_passed\":true}'", "'garrison'", "now()", "50"),
                             ("'{\"verdict\":\"pass\",\"judge_passed\":false}'", "'garrison'", "now()", "50"),
                             ("'{\"verdict\":\"pass\"}'", "'garrison'", "now()", "50"),
                             ("'{\"verdict\":\"pass\",\"judge_passed\":true}'", "null", "now()", "50"),
                             ("'{\"verdict\":\"pass\",\"judge_passed\":true}'", "'garrison'", "null", "50"),
                             ("'{\"verdict\":\"pass\",\"judge_passed\":true}'", "'garrison'", "now()", "null")):
        p = as_role(db, "service_role", base % (comp, by, at, mx))
        assert p.returncode != 0 and "violates check constraint" in p.stderr, (comp, by, at, mx)


def test_spend_budget_needs_approver_and_known_price(db):
    p = as_role(db, "service_role", "insert into spend_budgets (name, daily_cap_usd, monthly_cap_usd, cash_floor_usd, status) "
                                    "values ('x', 1, 1, 1, 'approved')")
    assert p.returncode != 0 and "violates check constraint" in p.stderr
    p = as_role(db, "service_role", "insert into spend_budgets (name, daily_cap_usd, monthly_cap_usd, cash_floor_usd, price_usd) "
                                    "values ('x', 1, 1, 1, 27)")
    assert p.returncode != 0 and "violates check constraint" in p.stderr
    p = as_role(db, "service_role", "insert into spend_budgets (name, daily_cap_usd, monthly_cap_usd, cash_floor_usd) values ('x', 100, 50, 1)")
    assert p.returncode != 0                                                        # monthly < daily


def test_ledger_cap_trigger_refuses_spend_above_the_daily_cap(db):
    bud = "00000000-0000-0000-0000-0000000000f1"
    ok = (f"insert into spend_ledger (budget_id, day, spend_class, amount_usd, source) values ('{bud}', '2026-10-15', 'boost', 300, 'planned');"
          f"insert into spend_ledger (budget_id, day, spend_class, amount_usd, source) values ('{bud}', '2026-10-15', 'retarget', 200, 'planned')")
    assert as_role(db, "service_role", ok).returncode == 0
    over = ok + f"; insert into spend_ledger (budget_id, day, spend_class, amount_usd, source) values ('{bud}', '2026-10-15', 'cold', 0.01, 'planned')"
    p = as_role(db, "service_role", over)
    assert p.returncode != 0 and "exceed the daily cap" in p.stderr
    p = as_role(db, "service_role", "insert into spend_ledger (budget_id, day, spend_class, amount_usd, source) values "
                                    "('00000000-0000-0000-0000-0000000000f2', '2026-10-15', 'boost', 1, 'planned')")
    assert p.returncode != 0 and "not approved" in p.stderr
    p = as_role(db, "service_role", f"insert into spend_ledger (budget_id, day, spend_class, amount_usd, source) values ('{bud}', '2026-10-15', 'boost', -1, 'planned')")
    assert p.returncode != 0


def test_ledger_and_decisions_are_append_only_for_every_role(db):
    _psql(db, sql="insert into spend_ledger (budget_id, day, spend_class, amount_usd, source) values "
                  "('00000000-0000-0000-0000-0000000000f1', '2026-10-16', 'boost', 10, 'reported');"
                  "insert into governor_decisions (decided_at, mode, status, valid, state_hash, config_fingerprint, planned_daily_usd, decision) "
                  "values (now(), 'dry_run', 'SCALE', true, 'h', 'f', 10, '{}')")
    for role in ("service_role", "postgres"):
        for stmt in ("update spend_ledger set amount_usd = 0", "delete from spend_ledger",
                     "update governor_decisions set planned_daily_usd = 0", "delete from governor_decisions"):
            p = _psql(db, sql=f"begin; set local role {role}; {stmt}; rollback;", check=False) if role != "postgres" \
                else _psql(db, sql=f"begin; {stmt}; rollback;", check=False)
            assert p.returncode != 0 and "append-only" in p.stderr, (role, stmt)
    p = _psql(db, sql="begin; set local role service_role; select count(*) from governor_decisions; rollback;")
    assert _val(p) == "1"
