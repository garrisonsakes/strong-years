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

## Capacity (ops box, sized for 458 posts/day)

Measured Oct 2 on 4 vCPU: one 35 s 1080×1920 x264 pass takes 11 s (veryfast) and 17 s with the still-image zoompan; `medium` (the assembly default) is about 2× that. A master is about 3 passes plus QA (~70 s on 4 vCPU at veryfast); every page × platform cut is its own render (uniqueness rule), about 1 pass plus QA (~35 s).

Estimated render wall time per day at `medium` (estimates from the benchmark, not a production run):

| Day load | Renders | CCX23, 3 render vCPU | CCX33, 6 render vCPU |
|---|---|---|---|
| 300 posts (launch) | 30 masters + 300 cuts | ~9.5 h | ~4.7 h |
| 458 posts ($30K rung) | 30 masters + 458 cuts | ~13.5 h (too tight) | ~6.7 h |

So the box is a **CCX33** (8 vCPU, 32 GB, 240 GB) with Hetzner Backups on. At 458 posts that still leaves a 3× margin. If renders ever exceed 12 h a day, set `X264_PRESET=fast` before adding a box.

Disk: renders write 10–25 GB a day. `common.janitor` (cron every 30 min) removes job dirs older than 6 h and rendered media older than 7 days, and the assembler refuses a job when free space drops below `MIN_FREE_GB` (15). `GET /health/details` reports `disk_free_gb`.

Cron (`/etc/cron.d/strongyears`, written by cloud-init; log `/var/log/strongyears-cron.log`):
- every 30 min: disk janitor (exit 2 = still under the free-space floor).
- every 15 min: Shopify webhook self-heal (`shopify/scripts/webhooks-heal.ts`; exit 2 = re-created a topic, so reconcile orders).
- 03:15 UTC: `deploy/scripts/backup.sh` dumps the n8n Postgres and the DM SQLite and keeps 14 days. Members data lives in Supabase (its own backups).

Third-party ceilings that matter more than the box: YouTube Data API 6 uploads per project per day (`docs/platform_reviews/youtube_api_compliance.md`), TikTok posts stay private until the API audit passes (post by hand), and Meta Graph rate limits per page.
