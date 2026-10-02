#!/usr/bin/env bash
# Nightly backup of the ops box state that is NOT in Supabase: the n8n Postgres (workflows, credentials, execution
# history) and the DM bot SQLite. Keeps BACKUP_KEEP_DAYS (default 14) under BACKUP_DIR. Run from /etc/cron.d/strongyears
# (deploy/cloud-init.yaml). Also turn on Hetzner Backups for the server so a copy lives off the box.
set -euo pipefail
cd "$(dirname "$0")/../.."
DIR="${BACKUP_DIR:-/opt/strongyears/backups}"
KEEP="${BACKUP_KEEP_DAYS:-14}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
COMPOSE="docker compose --env-file deploy/.env -f deploy/docker-compose.yml"
mkdir -p "$DIR"
$COMPOSE exec -T postgres pg_dump -U n8n -d n8n -Fc > "$DIR/n8n_$STAMP.dump.part"
mv "$DIR/n8n_$STAMP.dump.part" "$DIR/n8n_$STAMP.dump"
$COMPOSE exec -T workers python3 -c "
import sqlite3, sys, os
src = '/data/out/dm/dm.sqlite3'
if not os.path.exists(src): sys.exit(0)
dst = '/data/out/dm/backup.sqlite3'
s = sqlite3.connect(src); d = sqlite3.connect(dst); s.backup(d); d.close(); s.close()
sys.stdout.buffer.write(open(dst, 'rb').read()); os.remove(dst)
" > "$DIR/dm_$STAMP.sqlite3"
[ -s "$DIR/dm_$STAMP.sqlite3" ] || rm -f "$DIR/dm_$STAMP.sqlite3"
find "$DIR" -type f -mtime +"$KEEP" -delete
echo "backup ok $STAMP $(du -sh "$DIR" | cut -f1)"
