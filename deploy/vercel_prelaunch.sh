#!/usr/bin/env bash
# One command: the members app on Vercel in LAUNCH_MODE=prelaunch (waitlist, /go hub, /b redirects live; checkout shut),
# app migrations applied to Supabase, production env set, then scripts/smoke.ts against the deployed URL.
#
#   DRY_RUN=1 (default) prints every step and every env NAME it would set (never values) and touches nothing.
#   DRY_RUN=0 does it.                                          make prelaunch-deploy [APPLY=1]
#
# Required: VERCEL_TOKEN SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY SUPABASE_DB_URL and RESEND_API_KEY or POSTMARK_SERVER_TOKEN,
#           plus the three the health check needs: MAILING_ADDRESS EMAIL_FROM SUPPORT_EMAIL.
# Optional: VERCEL_PROJECT (default strong-years-members), VERCEL_SCOPE (team slug), SITE_URL (https://members.<domain>;
#           default = the deployment URL), SESSION_SECRET CRON_SECRET ADMIN_USER ADMIN_PASSWORD (generated when unset and
#           written to deploy/.prelaunch-generated.env, mode 600: move them to the vault), SKIP_TESTS=1, VERCEL_CLI,
#           and any of PASSTHROUGH below (copied to Vercel only when set in your shell).
# It never prints a secret, never creates accounts, never sends email, never opens checkout (LAUNCH_MODE=prelaunch).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DRY_RUN="${DRY_RUN:-1}"
PROJECT="${VERCEL_PROJECT:-strong-years-members}"
VERCEL="${VERCEL_CLI:-npx --yes vercel@latest}"
GEN_FILE="$ROOT/deploy/.prelaunch-generated.env"
PASSTHROUGH=(ANTHROPIC_API_KEY ANTHROPIC_MODEL EMAIL_PROVIDER VAPID_PUBLIC_KEY VAPID_PRIVATE_KEY VAPID_SUBJECT NEXT_PUBLIC_VAPID_PUBLIC_KEY
  RATE_LIMIT_KV_URL RATE_LIMIT_KV_TOKEN ADMIN_TOTP_SECRET PRIVACY_EMAIL DIGEST_EMAIL ONCALL_EMAIL
  SHOPIFY_STORE_DOMAIN SHOPIFY_WEBHOOK_SECRET SHOPIFY_ADMIN_TOKEN SHOPIFY_LOCATION_ID SHOPIFY_CUSTOMER_ACCOUNT_URL SHOPIFY_GRACE_DAYS
  FRONT_END_CELLS FRONT_END_DEFAULT_CELL FRONT_END_CELL_TEST FOUNDING_COHORT_CAP FOUNDING_CLOSE_DATE CHECKOUT_OPENS_AT
  GROWTH_API_TOKEN EXCEPTIONS_API_TOKEN GROWTH_WORKER_URL WORKER_TOKEN META_PIXEL_ID META_CAPI_TOKEN
  TRUSTED_PROXY_HOPS CLIENT_IP_HEADER WARM_INVITE_BATCH)

say()  { printf '%s\n' "$*"; }
step() { printf '\n== %s\n' "$*"; }
run()  { if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] $*"; else say "  \$ $*"; eval "$@"; fi; }
mask() { [ -n "${1:-}" ] && say "<set, ${#1} chars>" || say "<MISSING>"; }

step "0. preflight (DRY_RUN=$DRY_RUN)"
missing=()
for v in VERCEL_TOKEN SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY SUPABASE_DB_URL MAILING_ADDRESS EMAIL_FROM SUPPORT_EMAIL; do
  say "  $v $(mask "${!v:-}")"; [ -n "${!v:-}" ] || missing+=("$v")
done
if [ -n "${RESEND_API_KEY:-}" ]; then MAIL_VAR=RESEND_API_KEY; elif [ -n "${POSTMARK_SERVER_TOKEN:-}" ]; then MAIL_VAR=POSTMARK_SERVER_TOKEN
else MAIL_VAR=""; missing+=("RESEND_API_KEY|POSTMARK_SERVER_TOKEN"); fi
say "  email provider: ${MAIL_VAR:-<MISSING>}"
case "${SUPABASE_URL:-https://x}" in https://*) ;; *) missing+=("SUPABASE_URL must be https");; esac
[ -z "${SITE_URL:-}" ] || case "$SITE_URL" in https://*) ;; *) missing+=("SITE_URL must be https");; esac
if [ ${#missing[@]} -gt 0 ]; then
  say "  missing/invalid: ${missing[*]}"
  [ "$DRY_RUN" = 1 ] && say "  (dry run continues with placeholders)" || { say "refusing to deploy"; exit 2; }
fi
shop_missing=()
for v in SHOPIFY_STORE_DOMAIN SHOPIFY_WEBHOOK_SECRET SHOPIFY_CUSTOMER_ACCOUNT_URL SHOPIFY_ADMIN_TOKEN; do [ -n "${!v:-}" ] || shop_missing+=("$v"); done
[ ${#shop_missing[@]} -eq 0 ] || say "  warning: Shopify block not set (${shop_missing[*]}): the waitlist, /go and /b work, but /api/health
           reports them and the smoke 'health is ok' check will FAIL until they are set (LAUNCH_RUNBOOK.md §3)"
command -v psql >/dev/null || { [ "$DRY_RUN" = 1 ] && say "  note: psql not found (needed for migrations)" || { say "psql required"; exit 2; }; }
SCOPE_ARG=""; [ -z "${VERCEL_SCOPE:-}" ] || SCOPE_ARG="--scope $VERCEL_SCOPE"
VC="$VERCEL --token \"\$VERCEL_TOKEN\" $SCOPE_ARG"

step "1. local gates (typecheck, lint, unit; SKIP_TESTS=1 skips)"
if [ "${SKIP_TESTS:-0}" = 1 ]; then say "  skipped"; else run "(cd '$ROOT/app' && npm run typecheck && npm run lint && npm test)"; fi

step "2. app migrations on Supabase (dry run first, then apply; idempotent ledger; RLS verified)"
run "APP_DATABASE_URL=\"\$SUPABASE_DB_URL\" '$ROOT/deploy/scripts/db_migrate.sh' --target app --dry-run"
run "APP_DATABASE_URL=\"\$SUPABASE_DB_URL\" '$ROOT/deploy/scripts/db_migrate.sh' --target app"

step "3. link the Vercel project ($PROJECT), root = app/"
run "(cd '$ROOT/app' && $VC link --yes --project '$PROJECT')"

step "4. production env (names only; values never printed)"
gen() { # NAME length: reuse the shell value, else generate once and remember it
  local n="$1" len="$2"
  if [ -z "${!n:-}" ]; then
    if [ -f "$GEN_FILE" ] && grep -q "^$n=" "$GEN_FILE"; then export "$n=$(grep "^$n=" "$GEN_FILE" | cut -d= -f2-)"
    else export "$n=$(openssl rand -hex "$len")"
      if [ "$DRY_RUN" = 1 ]; then say "  would generate $n (written to deploy/.prelaunch-generated.env, mode 600)"
      else umask 077; echo "$n=${!n}" >> "$GEN_FILE"; say "  generated $n → deploy/.prelaunch-generated.env (move to the vault)"; fi
    fi
  fi
}
gen SESSION_SECRET 32; gen CRON_SECRET 24; gen ADMIN_PASSWORD 16
export ADMIN_USER="${ADMIN_USER:-admin}"
export LAUNCH_MODE=prelaunch BILLING_PROVIDER=shopify SUBSCRIPTION_ENGINE=shopify_subscriptions SHOPIFY_API_VERSION=2026-07
SET=(LAUNCH_MODE BILLING_PROVIDER SUBSCRIPTION_ENGINE SHOPIFY_API_VERSION SUPABASE_URL SUPABASE_SERVICE_ROLE_KEY
  MAILING_ADDRESS EMAIL_FROM SUPPORT_EMAIL SESSION_SECRET CRON_SECRET ADMIN_USER ADMIN_PASSWORD)
[ -z "$MAIL_VAR" ] || SET+=("$MAIL_VAR")
[ -z "${SITE_URL:-}" ] || { export NEXT_PUBLIC_SITE_URL="$SITE_URL"; SET+=(NEXT_PUBLIC_SITE_URL); }
for v in "${PASSTHROUGH[@]}"; do [ -z "${!v:-}" ] || SET+=("$v"); done
for v in "${SET[@]}"; do
  say "  $v $( [ "$v" = LAUNCH_MODE ] || [ "$v" = BILLING_PROVIDER ] || [ "$v" = SUBSCRIPTION_ENGINE ] || [ "$v" = SHOPIFY_API_VERSION ] && echo "= ${!v}" || mask "${!v:-}")"
  # rm first (ignore "not found"), then add from stdin so the value never appears in argv or logs
  run "(cd '$ROOT/app' && { $VC env rm $v production --yes >/dev/null 2>&1 || true; printf '%s' \"\$$v\" | $VC env add $v production >/dev/null; })"
done
say "  not set on purpose: STRIPE_* (Shopify launch path), LOCAL_DEMO_BUILD / ALLOW_RULES_ONLY_CHAT / ALLOW_MOCK_CHECKOUT_IN_PROD_BUILD (local only)"

step "5. deploy to production (vercel.json crons: launch, reminders, lifecycle, digest, warm-invites)"
if [ "$DRY_RUN" = 1 ]; then say "  [dry-run] (cd app && vercel deploy --prod --yes) → DEPLOY_URL"; DEPLOY_URL="https://<deployment>.vercel.app"
else DEPLOY_URL="$(cd "$ROOT/app" && eval "$VC deploy --prod --yes" | tail -1)"; say "  deployed: $DEPLOY_URL"; fi
if [ -z "${SITE_URL:-}" ]; then
  say "  NEXT_PUBLIC_SITE_URL not given: setting it to the deployment URL and redeploying so email links are https"
  export NEXT_PUBLIC_SITE_URL="$DEPLOY_URL"
  run "(cd '$ROOT/app' && { $VC env rm NEXT_PUBLIC_SITE_URL production --yes >/dev/null 2>&1 || true; printf '%s' \"\$NEXT_PUBLIC_SITE_URL\" | $VC env add NEXT_PUBLIC_SITE_URL production >/dev/null; })"
  if [ "$DRY_RUN" = 0 ]; then DEPLOY_URL="$(cd "$ROOT/app" && eval "$VC deploy --prod --yes" | tail -1)"; else say "  [dry-run] vercel deploy --prod --yes (again)"; fi
fi
TARGET="${SITE_URL:-$DEPLOY_URL}"

step "6. smoke against $TARGET (prelaunch expectations: /waitlist form, /join → /waitlist, /go hub, /b → /waitlist, doors shut)"
run "(cd '$ROOT/app' && CRON_SECRET=\"\$CRON_SECRET\" node --experimental-strip-types scripts/smoke.ts '$TARGET')"

step "done"
say "  Next (by a person): add the custom domain in Vercel → Domains, set SITE_URL and re-run; Shopify webhooks → $TARGET/api/webhooks/shopify;"
say "  open checkout only via CHECKOUT_OPENS_AT or /admin 'Open checkout now' (LAUNCH_RUNBOOK.md §1, §3, §9)."
[ "$DRY_RUN" = 1 ] && say "  This was a dry run. DRY_RUN=0 (or make prelaunch-deploy APPLY=1) to do it."
exit 0
