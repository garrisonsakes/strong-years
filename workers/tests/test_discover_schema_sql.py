"""schema_discover.sql on a real Postgres 16 (same harness as tests/test_schema_sql.py): applies idempotently after
schema.sql + schema_growth.sql, every discover table is RLS-forced with deny-by-default for anon and authenticated,
service_role can write, a remake brief can't be queued without a passing guard and provenance, and
v_post_attribution counts only a lead's first subscription order as new MRR."""
from __future__ import annotations

import json
import uuid

import pytest

from common import config
from tests.test_schema_sql import BASE, SCHEMA, SQL, _psql, as_role, denied

GROWTH = config.SPEC_DIR / "schema_growth.sql"
DISCOVER = config.SPEC_DIR / "schema_discover.sql"
TABLES = ["niche_posts", "niche_post_reads", "niche_opportunities", "remake_queue", "discover_feeds"]
pytestmark = pytest.mark.skipif(BASE is None, reason="no Postgres available (set PGTEST_DSN)")


@pytest.fixture(scope="module")
def db():
    name = "cs_discover_" + uuid.uuid4().hex[:8]
    _psql(None, sql=f"create database {name}")
    for f in (SQL / "vault_stub.sql", SCHEMA, GROWTH, DISCOVER, DISCOVER, SQL / "seed.sql"):   # discover twice: idempotent
        _psql(name, "-f", "-", stdin=f.read_text())
    yield name
    _psql(None, sql=f"drop database if exists {name} with (force)", check=False)


def q(db, sql):
    return _psql(db, "-Atq", sql=sql).stdout.strip()


def test_rls_forced_everywhere(db):
    for t in TABLES:
        assert q(db, f"select relrowsecurity and relforcerowsecurity from pg_class where relname = '{t}'") == "t", t


@pytest.mark.parametrize("role", ["anon", "authenticated"])
@pytest.mark.parametrize("table", TABLES)
def test_deny_by_default(db, role, table):
    assert denied(as_role(db, role, f"select * from {table}"))
    assert denied(as_role(db, role, f"delete from {table}"))


@pytest.mark.parametrize("role", ["anon", "authenticated"])
def test_attribution_view_denied(db, role):
    assert denied(as_role(db, role, "select * from v_post_attribution"))


def test_service_role_writes_and_unique_external_id(db):
    ins = ("insert into niche_posts (platform, external_id, source, content_sha, genes) "
           "values ('tiktok', '1', 'tiktok_research', 'abc', array['hook:WATCH'])")
    assert as_role(db, "service_role", ins).returncode == 0
    p = as_role(db, "service_role", ins + "; " + ins)
    assert p.returncode != 0 and "duplicate key" in p.stderr
    assert as_role(db, "service_role", "insert into niche_posts (platform, external_id, source, content_sha) "
                                       "values ('myspace', '1', 'x', 'a')").returncode != 0


def test_remake_queue_requires_guard_and_provenance(db):
    prov = json.dumps({"platform": "tiktok", "external_id": "1", "content_sha": "abc"})
    ok = json.dumps({"guard": {"ok": True}})
    bad = json.dumps({"guard": {"ok": False}})
    base = "insert into remake_queue (reason, brief, provenance) values ('top_performer', '{b}'::jsonb, '{p}'::jsonb)"
    assert as_role(db, "service_role", base.format(b=ok, p=prov)).returncode == 0
    assert as_role(db, "service_role", base.format(b=bad, p=prov)).returncode != 0
    assert as_role(db, "service_role", base.format(b=ok, p=json.dumps({"platform": "tiktok"}))).returncode != 0


def test_attribution_counts_first_subscription_only(db):
    acc = q(db, "select id from page_accounts limit 1")
    if not acc:
        pytest.skip("seed has no page account")
    _psql(db, sql=f"""
      insert into posts (id, page_account_id, platform, scheduled_at, published_at, status)
        values ('00000000-0000-0000-0000-0000000000c1', '{acc}', 'instagram', now() - interval '1 day', now() - interval '1 day', 'published')
        on conflict do nothing;
      insert into orders (provider, external_order_id, amount_usd, is_subscription, plan_price_usd, attributed_post_id, created_at)
        values ('shopify', 'o1', 12, true, 25, '00000000-0000-0000-0000-0000000000c1', now() - interval '20 hours'),
               ('shopify', 'o2', 12, false, null, '00000000-0000-0000-0000-0000000000c1', now() - interval '19 hours');
    """)
    row = q(db, "select mrr_usd || '|' || buyers from v_post_attribution where post_id = '00000000-0000-0000-0000-0000000000c1'")
    assert row == "25.00|1"
