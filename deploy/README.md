# deploy/

| Command | What it does | Touches |
|---|---|---|
| `make prelaunch-deploy` | `deploy/vercel_prelaunch.sh` **dry run**: prints every step and every env name (never values) | nothing |
| `make prelaunch-deploy APPLY=1` | Members app → Vercel in `LAUNCH_MODE=prelaunch`: local gates (typecheck, lint, unit), app migrations on Supabase (dry run, then apply, RLS verified), `vercel link`, production env, `vercel deploy --prod`, `scripts/smoke.ts` against the URL | Vercel project, Supabase DB |
| `make prelaunch-local [EXIT=1] [NO_BUILD=1] [SMOKE=1]` | Same app in prelaunch on a local Postgres 16 + PostgREST (`deploy/local/`), migrated with `--bootstrap`, seeded with 24 fake `.example` waitlist rows; 390px screenshots of `/go`, `/go?p=tt-cy`, `/waitlist` → `app/screenshots/40-*.png` + `40-checks.json` (fails on any gray / low-contrast text or horizontal overflow) | Docker on this machine |
| `make prelaunch-local-down` | Removes the local containers and DB volume | Docker |
| `make db-migrate [DRY_RUN=1] [TARGET=app]` | `scripts/db_migrate.sh` (ledger, idempotent, RLS check) | the DB in `APP_DATABASE_URL` / `DATABASE_URL` |
| `make up` / `check-secrets` / `n8n-import` | Hetzner ops stack (n8n, workers, Caddy); see LAUNCH_RUNBOOK.md §3 | the ops box |

## `vercel_prelaunch.sh` inputs

Required: `VERCEL_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL` (the direct Postgres connection string, for migrations), `RESEND_API_KEY` **or** `POSTMARK_SERVER_TOKEN`, `MAILING_ADDRESS`, `EMAIL_FROM`, `SUPPORT_EMAIL`.

Set by the script: `LAUNCH_MODE=prelaunch`, `BILLING_PROVIDER=shopify`, `SUBSCRIPTION_ENGINE=shopify_subscriptions`, `SHOPIFY_API_VERSION=2026-07`. `SESSION_SECRET`, `CRON_SECRET`, `ADMIN_PASSWORD` are generated when not given and written to `deploy/.prelaunch-generated.env` (mode 600, git-ignored): move them to the vault. `NEXT_PUBLIC_SITE_URL` = `SITE_URL` if given, else the deployment URL (then a second deploy).

Copied when present in your shell: the Shopify block, VAPID, rate-limit KV, `ANTHROPIC_API_KEY`, `CHECKOUT_OPENS_AT`, growth/exceptions tokens, Meta pixel/CAPI and the rest of `PASSTHROUGH` in the script. Without the Shopify block the waitlist, `/go` and `/b` work but `/api/health` is 503, so the smoke "health is ok" check fails until it is set.

Never set: any `STRIPE_*`, `LOCAL_DEMO_BUILD`, `ALLOW_RULES_ONLY_CHAT`, `ALLOW_MOCK_CHECKOUT_IN_PROD_BUILD`. Checkout stays shut until `CHECKOUT_OPENS_AT` or `/admin` "Open checkout now".

Smoke in prelaunch (17 checks): health, https, `/waitlist` form and no $1 copy, `/join` → `/waitlist`, checkout API refuses, forged Shopify / unsigned Stripe webhooks refused, cron and growth closed, `/go` hub leads with the waitlist, `/b?t=STRONG` → `/waitlist` with keyword + post id carried, `/admin` and `/app` locked, no password field, CSP. Locally (`SMOKE=1`) health and https fail by design (no email config, http).
