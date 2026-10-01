# Chang & Sun content-factory workers
PY ?= python3
PORT ?= 8080

.PHONY: install install-dev test test-sql test-fast test-growth sample selftest compliance-report patch-workflow serve docker clean

install:
	$(PY) -m pip install -r requirements.txt

install-dev:
	$(PY) -m pip install -r requirements-dev.txt

test:            ## full suite (synthesises audio/video; ~4–5 min on 2 CPUs)
	$(PY) -m pytest

test-fast:       ## no media rendering: compliance, packaging, workflow contract, growth
	$(PY) -m pytest tests/test_compliance.py tests/test_packaging.py tests/test_workflow.py tests/test_growth_*.py -q

sample:          ## end-to-end sample video -> out/sample/ (master, frames/, sample_report.json); dev C2PA cert
	C2PA_ALLOW_DEV_CERT=1 $(PY) -m tools.make_sample

test-sql:        ## schema.sql + schema_growth.sql security tests (local Postgres 16 as root, or PGTEST_DSN)
	$(PY) -m pytest tests/test_schema_sql.py tests/test_growth_schema_sql.py -q

test-growth:     ## growth engine: adapters, snapshots, scoring, actions, allocator, governor (property tests), API, workflow
	$(PY) -m pytest tests/test_growth_*.py -q

selftest:        ## SAFETY_RULES §10–11 cases
	$(PY) -m compliance selftest

compliance-report:   ## deterministic scan of the organic scripts + paid ad scripts -> out/compliance_report.json
	mkdir -p out && $(PY) -m compliance scan ../data/content/scripts.json ../data/content/ad_scripts.json --json out/compliance_report.json

patch-workflow:  ## (idempotent) reconcile ../n8n_core_workflow.json with the worker endpoints
	$(PY) -m tools.patch_workflow

serve:
	uvicorn app:app --host 0.0.0.0 --port $(PORT)

docker:
	cd .. && docker build -f workers/Dockerfile -t changsun-workers .

clean:
	rm -rf out .pytest_cache
