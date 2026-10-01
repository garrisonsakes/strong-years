"""SQL security tests for schema.sql (AUDIT_CODE C3, L14, H11) on a real Postgres 16 + pgvector.

Connection: PGTEST_DSN (e.g. postgresql://postgres:postgres@localhost:5432/postgres in CI), otherwise the local
cluster via `runuser -u postgres -- psql` when running as root. Skipped when neither is available.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from common import config

SQL = Path(__file__).parent / "sql"
SCHEMA = config.SPEC_DIR / "schema.sql"
ACC = "00000000-0000-0000-0000-0000000000a1"
VID = "00000000-0000-0000-0000-0000000000d1"


def _base_cmd() -> list[str] | None:
    if os.environ.get("PGTEST_DSN"):
        return ["psql", os.environ["PGTEST_DSN"]]
    if shutil.which("psql") and shutil.which("runuser") and os.geteuid() == 0:
        p = subprocess.run(["runuser", "-u", "postgres", "--", "psql", "-Atqc", "select 1"], capture_output=True, text=True)
        if p.returncode == 0:
            return ["runuser", "-u", "postgres", "--", "psql"]
    return None


BASE = _base_cmd()
pytestmark = pytest.mark.skipif(BASE is None, reason="no Postgres available (set PGTEST_DSN)")


def _psql(db: str | None, *args: str, sql: str | None = None, check=True, stdin: str | None = None) -> subprocess.CompletedProcess:
    cmd = list(BASE)
    if db:
        if os.environ.get("PGTEST_DSN"):
            cmd[1] = os.environ["PGTEST_DSN"].rsplit("/", 1)[0] + "/" + db
        else:
            cmd += ["-d", db]
    cmd += ["-v", "ON_ERROR_STOP=1", "-Atq", *args]
    if sql is not None:
        cmd += ["-c", sql]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, input=stdin)
    if check and p.returncode != 0:
        raise AssertionError(p.stderr)
    return p


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    name = "cs_sec_" + uuid.uuid4().hex[:8]
    _psql(None, sql=f"create database {name}")
    for f in (SQL / "vault_stub.sql", SCHEMA, SCHEMA, SQL / "seed.sql"):   # schema applied twice: idempotent
        _psql(name, "-f", "-", stdin=f.read_text())       # via stdin: the postgres OS user can't read tmp dirs
    yield name
    _psql(None, sql=f"drop database if exists {name} with (force)", check=False)


def as_role(db: str, role: str, stmt: str, claims: str | None = None) -> subprocess.CompletedProcess:
    pre = f"set request.jwt.claims = '{claims}'; " if claims is not None else ""
    return _psql(db, sql=f"begin; {pre}set local role {role}; {stmt}; rollback;", check=False)


def denied(p: subprocess.CompletedProcess) -> bool:
    return p.returncode != 0 and ("permission denied" in p.stderr or "service_role only" in p.stderr)


@pytest.mark.parametrize("role", ["anon", "authenticated"])
def test_C3_anon_and_users_cannot_read_tokens(db, role):
    assert denied(as_role(db, role, f"select get_publish_token('{ACC}')"))
    assert denied(as_role(db, role, "select token_vault_key from page_accounts"))
    assert denied(as_role(db, role, "select * from vault.decrypted_secrets"))
    assert denied(as_role(db, role, "select * from claim_due_posts(10)"))


@pytest.mark.parametrize("role", ["anon", "authenticated"])
def test_C3_cannot_approve_videos(db, role):
    reviewer = '{"app_role":"reviewer"}'
    assert denied(as_role(db, role, f"select review_video('{VID}', 'approved', 'x')", reviewer))
    assert denied(as_role(db, role, f"update videos set status = 'approved' where id = '{VID}'", reviewer))
    assert denied(as_role(db, role, "select create_variants_and_posts('{}'::jsonb)"))


@pytest.mark.parametrize("stmt", ["delete from blocked_claims", "update prompt_versions set active = false",
                                  "insert into briefs(page_id, target_date, format) values "
                                  "('00000000-0000-0000-0000-00000000000a', current_date, 'R1_talk_prop')",
                                  "select * from dm_leads", "select * from orders", "select claim_next_brief('x')"])
def test_C3_no_writes_or_pii_for_anon(db, stmt):
    assert denied(as_role(db, "anon", stmt))
    assert denied(as_role(db, "authenticated", stmt, '{"app_role":"reviewer"}'))


def test_C3_reviewer_read_only_surface(db):
    p = as_role(db, "authenticated", "select count(*) from videos", "{}")
    assert p.returncode == 0 and p.stdout.strip().splitlines()[-1] == "0"          # non-reviewer sees nothing
    p = as_role(db, "authenticated", "select count(*) from videos", '{"app_role":"reviewer"}')
    assert p.returncode == 0 and p.stdout.strip().splitlines()[-1] == "1"
    p = as_role(db, "authenticated", "select count(*) from v_human_queue", '{"app_role":"reviewer"}')
    assert p.returncode == 0 and p.stdout.strip().splitlines()[-1] == "1"
    assert denied(as_role(db, "anon", "select count(*) from v_human_queue"))


def test_C3_service_role_still_works(db):
    p = as_role(db, "service_role", f"select get_publish_token('{ACC}')->>'access_token'")
    assert p.returncode == 0 and p.stdout.strip().splitlines()[-1] == "IGSECRET"
    p = as_role(db, "service_role", f"select review_video('{VID}', 'approved', 'tester')->>'ok'")
    assert p.returncode == 0 and p.stdout.strip().splitlines()[-1] == "true"


def test_C3_token_function_refuses_even_if_regranted(db):
    p = _psql(db, sql=f"begin; grant execute on function get_publish_token(uuid) to anon; set local role anon; "
                      f"select get_publish_token('{ACC}'); rollback;", check=False)
    assert p.returncode != 0 and "service_role only" in p.stderr


def test_C3_rls_on_every_table_and_no_anon_execute(db):
    no_rls = _psql(db, sql="select c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace "
                           "where n.nspname='public' and c.relkind='r' and not c.relrowsecurity").stdout.split()
    assert no_rls == []
    exec_anon = _psql(db, sql="select p.proname from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                              "where n.nspname='public' and has_function_privilege('anon', p.oid, 'execute') "
                              "and not exists (select 1 from pg_depend d where d.objid=p.oid and d.deptype='e')").stdout.split()
    assert exec_anon == ["is_reviewer"]
    grants = _psql(db, sql="select count(*) from information_schema.role_table_grants "
                           "where table_schema='public' and grantee='anon'").stdout.strip()
    assert grants == "0"


def test_L14_search_path_on_every_function(db):
    missing = _psql(db, sql="select p.proname from pg_proc p join pg_namespace n on n.oid=p.pronamespace "
                            "where n.nspname='public' and not exists (select 1 from pg_depend d where d.objid=p.oid "
                            "and d.deptype='e') and not coalesce(p.proconfig::text,'') like '%search_path=public, pg_temp%'"
                    ).stdout.split()
    assert missing == []


def test_views_are_security_invoker(db):
    v = _psql(db, sql="select c.relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where "
                      "n.nspname='public' and c.relkind='v' and not coalesce(c.reloptions::text,'') like '%security_invoker=true%'"
              ).stdout.split()
    assert v == []


def test_H11_pipeline_orders_name_documented():
    s = SCHEMA.read_text()
    assert "create table if not exists orders" in s and "sy_orders" in s
    assert "sy_orders" in (config.WORKERS_DIR / "README.md").read_text()
