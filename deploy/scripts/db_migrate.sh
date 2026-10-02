#!/usr/bin/env bash
# Applies the database schemas in order, idempotently, then verifies RLS.
#   pipeline DB : schema.sql, schema_growth.sql, schema_discover.sql   (idempotent by design: re-applied whenever their checksum changes)
#   app DB      : app/supabase/migrations/*.sql in name order (applied once each; a changed applied file aborts)
# A ledger table deploy.schema_migrations(target, file, sha256, applied_at) records what ran.
#
#   PIPELINE_DATABASE_URL=… APP_DATABASE_URL=… deploy/scripts/db_migrate.sh [--dry-run] [--bootstrap] [--verify-only] [--target all|pipeline|app]
# DATABASE_URL is the default for both. --bootstrap adds the Supabase roles/auth.uid()/vault stand-ins (plain Postgres only).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DRY=0; BOOT=0; VERIFY_ONLY=0; TARGET=all
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;; --bootstrap) BOOT=1 ;; --verify-only) VERIFY_ONLY=1 ;;
    --target) TARGET="$2"; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac; shift
done
PIPE_URL="${PIPELINE_DATABASE_URL:-${DATABASE_URL:-}}"
APP_URL="${APP_DATABASE_URL:-${DATABASE_URL:-}}"

export PGOPTIONS="${PGOPTIONS:--c client_min_messages=warning}"
psqlx() { psql "$1" -v ON_ERROR_STOP=1 -X -q -At "${@:2}"; }
sha() { sha256sum "$1" | cut -d' ' -f1; }

ledger() {
  psqlx "$1" -c "create schema if not exists deploy; revoke all on schema deploy from public;
    create table if not exists deploy.schema_migrations (target text not null, file text not null, sha256 text not null,
      applied_at timestamptz not null default now(), primary key (target, file));"
}

apply_set() { # url target mode(rerun|once) files...
  local url="$1" target="$2" mode="$3"; shift 3
  [ "$DRY" = 1 ] || ledger "$url"
  for f in "$@"; do
    local name; name="$(basename "$f")"; local h; h="$(sha "$f")"
    local have=""
    if [ "$DRY" = 0 ]; then have="$(psqlx "$url" -c "select sha256 from deploy.schema_migrations where target='$target' and file='$name'")"; fi
    if [ -n "$have" ] && [ "$have" = "$h" ]; then echo "  = $target/$name (unchanged, skipped)"; continue; fi
    if [ -n "$have" ] && [ "$mode" = once ]; then echo "  ! $target/$name changed after it was applied: write a new migration instead" >&2; exit 3; fi
    if [ "$DRY" = 1 ]; then echo "  + $target/$name (would apply)"; continue; fi
    echo "  + $target/$name"
    psqlx "$url" -1 -f - < "$f" >/dev/null
    psqlx "$url" -c "insert into deploy.schema_migrations(target, file, sha256) values ('$target', '$name', '$h')
      on conflict (target, file) do update set sha256 = excluded.sha256, applied_at = now()"
  done
}

verify() { psqlx "$1" -f - < "$ROOT/deploy/sql/verify_rls.sql" && echo "  RLS verified ($2): every public table has RLS on; anon has no table grants"; }

run_target() { # url target
  local url="$1" target="$2"
  [ -n "$url" ] || { echo "no database URL for $target (set ${target^^}_DATABASE_URL or DATABASE_URL)" >&2; exit 2; }
  echo "[$target]"
  if [ "$VERIFY_ONLY" = 0 ]; then
    if [ "$BOOT" = 1 ]; then
      if [ "$DRY" = 1 ]; then echo "  + bootstrap (would apply)"; else psqlx "$url" -f - < "$ROOT/deploy/sql/bootstrap_plain_postgres.sql" >/dev/null; echo "  + bootstrap"; fi
    fi
    if [ "$target" = pipeline ]; then
      apply_set "$url" pipeline rerun "$ROOT/schema.sql" "$ROOT/schema_growth.sql" "$ROOT/schema_discover.sql"
    else
      mapfile -t files < <(ls "$ROOT"/app/supabase/migrations/*.sql | sort)
      apply_set "$url" app once "${files[@]}"
    fi
  fi
  [ "$DRY" = 1 ] || verify "$url" "$target"
}

case "$TARGET" in
  pipeline) run_target "$PIPE_URL" pipeline ;;
  app) run_target "$APP_URL" app ;;
  all) run_target "$PIPE_URL" pipeline; run_target "$APP_URL" app ;;
  *) echo "--target all|pipeline|app" >&2; exit 2 ;;
esac
echo "done"
