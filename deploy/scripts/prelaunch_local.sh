#!/usr/bin/env bash
# make prelaunch-local: the members app in LAUNCH_MODE=prelaunch on a real, migrated, seeded Postgres (via PostgREST),
# then 390px screenshots of /go and /waitlist (app/screenshots/40-*.png) with the no-gray-text / no-overflow checks.
# Local only: dev passwords, 127.0.0.1, no email provider keys (mail goes to the outbox table), no Shopify/Meta/AI keys.
#
#   deploy/scripts/prelaunch_local.sh [--no-build] [--no-screens] [--smoke] [--exit]   # --exit: stop the app after the checks
#   deploy/scripts/prelaunch_local.sh --down                                  # remove the containers and the DB volume
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE=(docker compose -f "$ROOT/deploy/local/prelaunch.compose.yml")
BUILD=1; SCREENS=1; EXIT=0; SMOKE=0
for a in "$@"; do case "$a" in
  --no-build) BUILD=0 ;; --no-screens) SCREENS=0 ;; --smoke) SMOKE=1 ;; --exit) EXIT=1 ;;
  --down) "${COMPOSE[@]}" down -v; exit 0 ;;
  *) echo "unknown option $a" >&2; exit 2 ;;
esac; done

export LOCAL_PG_PASSWORD="${LOCAL_PG_PASSWORD:-sy-local-only}"
export LOCAL_JWT_SECRET="${LOCAL_JWT_SECRET:-sy-local-only-jwt-secret-0123456789abcdef}"
PG_PORT="${LOCAL_PG_PORT:-54329}"; REST_PORT="${LOCAL_REST_PORT:-54321}"; APP_PORT="${APP_PORT:-3300}"
LOG="${TMPDIR:-/tmp}/sy-prelaunch-local.log"
DB_URL="postgres://postgres:${LOCAL_PG_PASSWORD}@127.0.0.1:${PG_PORT}/postgres"
step() { printf '\n== %s\n' "$*"; }

step "1/6 Postgres 16"
"${COMPOSE[@]}" up -d --wait postgres

step "2/6 migrations (app target, plain-Postgres bootstrap, RLS verified)"
APP_DATABASE_URL="$DB_URL" "$ROOT/deploy/scripts/db_migrate.sh" --target app --bootstrap

step "3/6 seed (PostgREST role, service_role grants, 24 fake .example waitlist rows)"
PGOPTIONS="-c client_min_messages=warning -c sy.local_pw=${LOCAL_PG_PASSWORD}" \
  psql "$DB_URL" -v ON_ERROR_STOP=1 -X -q -f "$ROOT/deploy/local/seed_prelaunch.sql"

step "4/6 PostgREST + /rest/v1 gateway"
"${COMPOSE[@]}" up -d postgrest gateway
SERVICE_KEY="$(LOCAL_JWT_SECRET="$LOCAL_JWT_SECRET" node -e '
const c=require("crypto"),b=o=>Buffer.from(JSON.stringify(o)).toString("base64url");
const h=b({alg:"HS256",typ:"JWT"}),p=b({role:"service_role",iss:"sy-local",iat:Math.floor(Date.now()/1e3),exp:Math.floor(Date.now()/1e3)+86400*30});
process.stdout.write(h+"."+p+"."+c.createHmac("sha256",process.env.LOCAL_JWT_SECRET).update(h+"."+p).digest("base64url"));')"
for i in $(seq 1 60); do
  code="$(curl -s -o /dev/null -w '%{http_code}' -H "authorization: Bearer $SERVICE_KEY" "http://127.0.0.1:${REST_PORT}/rest/v1/waitlist?select=id&limit=1" || true)"
  [ "$code" = 200 ] && break; sleep 1
done
[ "$code" = 200 ] || { echo "PostgREST not answering (last HTTP $code)" >&2; "${COMPOSE[@]}" logs --tail=30 postgrest >&2; exit 1; }
echo "  rest ok: $(curl -s -H "authorization: Bearer $SERVICE_KEY" -H 'prefer: count=exact' -o /dev/null -D - \
  "http://127.0.0.1:${REST_PORT}/rest/v1/waitlist?select=id&limit=1" | tr -d '\r' | awk -F/ 'tolower($0) ~ /^content-range/ {print $2" waitlist rows"}')"

step "5/6 members app (LAUNCH_MODE=prelaunch, real store) on http://localhost:${APP_PORT}"
cd "$ROOT/app"
[ -d node_modules ] || npm ci
# exported before the build: static pages (e.g. /go) are rendered at build time with this env, as on Vercel
export SUPABASE_URL="http://127.0.0.1:${REST_PORT}" SUPABASE_SERVICE_ROLE_KEY="$SERVICE_KEY" \
  LAUNCH_MODE=prelaunch BILLING_PROVIDER=shopify SUBSCRIPTION_ENGINE=shopify_subscriptions \
  SHOPIFY_STORE_DOMAIN=strongyears-local.myshopify.com SHOPIFY_CUSTOMER_ACCOUNT_URL=https://shopify.com/00000/account \
  SHOPIFY_WEBHOOK_SECRET=local-shopify-webhook-secret-0123456789 SHOPIFY_API_VERSION=2026-07 \
  NEXT_PUBLIC_SITE_URL="http://localhost:${APP_PORT}" SESSION_SECRET=local-session-secret-0123456789abcdef \
  CRON_SECRET=local-cron ADMIN_USER=admin ADMIN_PASSWORD=local-admin-only WAITLIST_MIN_FILL_MS=0
[ "$BUILD" = 0 ] || npm run build >/dev/null
if curl -s -o /dev/null "http://localhost:${APP_PORT}/"; then echo "port ${APP_PORT} is already in use (an old server?); stop it or set APP_PORT" >&2; exit 1; fi
setsid node_modules/.bin/next start -p "$APP_PORT" > "$LOG" 2>&1 &   # own process group: the trap stops next-server too
APP_PID=$!
trap 'kill -- -$APP_PID 2>/dev/null || kill $APP_PID 2>/dev/null || true' EXIT
for i in $(seq 1 60); do curl -sf -o /dev/null "http://localhost:${APP_PORT}/waitlist" && break; sleep 1; done
curl -sf -o /dev/null "http://localhost:${APP_PORT}/waitlist" || { tail -30 "$LOG" >&2; exit 1; }
echo "  up (log: $LOG). Admin: admin / local-admin-only. Email is blocked locally (outbox only)."

if [ "$SCREENS" = 1 ]; then
  step "6/6 screenshots at 390px + checks (no gray text, no horizontal overflow)"
  PRELAUNCH_BASE_URL="http://localhost:${APP_PORT}" npx playwright test --config playwright.prelaunch.config.ts
fi
if [ "$SMOKE" = 1 ]; then
  step "smoke (scripts/smoke.ts; locally 'health' and 'https' are expected to FAIL: no email config, http)"
  CRON_SECRET=local-cron node --experimental-strip-types scripts/smoke.ts "http://localhost:${APP_PORT}" || true
fi
if [ "$EXIT" = 1 ]; then echo "done (app stopped; DB kept: make prelaunch-local-down removes it)"; exit 0; fi
echo; echo "Running at http://localhost:${APP_PORT}/go and /waitlist. Ctrl-C stops the app; make prelaunch-local-down removes the DB."
wait "$APP_PID"
