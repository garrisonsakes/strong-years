# Strong Years: one entry point for the ops stack (deploy/) and the checks. Nothing here posts, sends or spends.
COMPOSE = docker compose --env-file deploy/.env -f deploy/docker-compose.yml
DRY_RUN ?= 0
BOOTSTRAP ?= 0
TARGET ?= all

.PHONY: help up down logs ps db-migrate db-verify n8n-import check-secrets test test-app test-workers test-shopify validate-content

help:
	@echo "make up | down | logs | ps | db-migrate [DRY_RUN=1] [BOOTSTRAP=1] [TARGET=all|pipeline|app] | db-verify"
	@echo "make n8n-import [APPLY=1] | check-secrets [SECRETS=deploy/secrets.env] | test | validate-content"

up: n8n-import          ## build the workers image and start postgres, redis, n8n (main + worker), workers, assembly, caddy
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

db-migrate:             ## schema.sql + schema_growth.sql (pipeline) and app migrations (members app), idempotent, then RLS check
	deploy/scripts/db_migrate.sh --target $(TARGET) $(if $(filter 1,$(DRY_RUN)),--dry-run) $(if $(filter 1,$(BOOTSTRAP)),--bootstrap)

db-verify:
	deploy/scripts/db_migrate.sh --target $(TARGET) --verify-only

n8n-import:             ## prepare workflows with publishing/spend nodes disabled unless LAUNCH_MODE=live (APPLY=1 imports)
	python3 deploy/scripts/n8n_import.py $(if $(filter 1,$(APPLY)),--apply)

check-secrets:
	python3 deploy/scripts/check_secrets.py $(or $(SECRETS),deploy/secrets.env)

test: test-app test-workers test-shopify validate-content

test-app:
	cd app && npm run typecheck && npm run lint && npm test && npm run build && npm run test:e2e

test-workers:
	cd workers && python3 -m pytest

test-shopify:
	cd shopify && npm run check

validate-content:
	python3 tools/build_content.py
	cd workers && python3 -m compliance templates ../app/content/lifecycle/sequences.json dm/flows/*.json
