SHELL := /bin/bash
APP_DIR := $(CURDIR)
VENV_DIR := $(APP_DIR)/.venv
PYTHON := $(VENV_DIR)/bin/python3
PIP := $(VENV_DIR)/bin/pip
PY := $(VENV_DIR)/bin/python
PYTEST := $(VENV_DIR)/bin/pytest
UVICORN := $(VENV_DIR)/bin/uvicorn
DB_PATH ?= /Users/tongwei/.openclaw/data/in-spirit-case-auth.db
SCHEMA_FILE ?= /Users/tongwei/.openclaw/control-plane/in-spirit-case-auth-model-routing-db-schema-v1.sql
SMOKE_SCRIPT := $(APP_DIR)/scripts/smoke-test.sh
SEED_SCRIPT := $(APP_DIR)/scripts/seed-admin.py
ENV_FILE := $(APP_DIR)/.env

.PHONY: help venv install init-db seed test run smoke bootstrap clean

help:
	@echo "Available targets:"
	@echo "  make venv         - create local virtualenv"
	@echo "  make install      - install dependencies"
	@echo "  make init-db      - initialize sqlite database from schema"
	@echo "  make seed         - seed admin and case accounts"
	@echo "  make test         - run pytest"
	@echo "  make run          - start FastAPI dev server"
	@echo "  make smoke        - run curl smoke test"
	@echo "  make bootstrap    - full setup: venv/install/init-db/seed/test"
	@echo "  make clean        - remove local virtualenv"

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

init-db:
	@mkdir -p $$(dirname "$(DB_PATH)")
	@if [ ! -f "$(SCHEMA_FILE)" ]; then \
		echo "Schema file not found: $(SCHEMA_FILE)"; \
		exit 1; \
	fi
	sqlite3 "$(DB_PATH)" < "$(SCHEMA_FILE)"
	@echo "Database initialized: $(DB_PATH)"

seed: install
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo ".env file not found at $(ENV_FILE). Copy .env.template first."; \
		exit 1; \
	fi
	$(PY) "$(SEED_SCRIPT)"

test: install
	PYTHONPATH=$(APP_DIR) $(PYTEST)

run: install
	PYTHONPATH=$(APP_DIR) $(UVICORN) app.main:app --reload --host 127.0.0.1 --port 8010

smoke:
	@if [ ! -x "$(SMOKE_SCRIPT)" ]; then chmod +x "$(SMOKE_SCRIPT)"; fi
	$(SMOKE_SCRIPT)

bootstrap: venv install init-db seed test
	@echo "Bootstrap complete."

clean:
	rm -rf "$(VENV_DIR)"

REPORT_ROOT := /Users/tongwei/.openclaw/reports

.PHONY: ops-report ops-daily-report ops-weekly-report ops-monthly-report ops-audit-export

ops-audit-export: install
	@mkdir -p "$(REPORT_ROOT)"
	$(PY) "$(APP_DIR)/scripts/export-audit-log.py" --format md --limit 200 --output "$(REPORT_ROOT)/audit-latest.md"
	$(PY) "$(APP_DIR)/scripts/export-audit-log.py" --format csv --limit 500 --output "$(REPORT_ROOT)/audit-latest.csv"

ops-daily-report: install
	@mkdir -p "$(REPORT_ROOT)" "$(REPORT_ROOT)/daily"
	@if [ ! -x "$(APP_DIR)/scripts/ops-daily-check.sh" ]; then chmod +x "$(APP_DIR)/scripts/ops-daily-check.sh"; fi
	"$(APP_DIR)/scripts/ops-daily-check.sh" > "$(REPORT_ROOT)/ops-daily-check-latest.txt" 2>&1
	$(PY) "$(APP_DIR)/scripts/render-daily-report.py"

ops-weekly-report: install
	@mkdir -p "$(REPORT_ROOT)/weekly"
	$(PY) "$(APP_DIR)/scripts/ops-weekly-summary.py"

ops-monthly-report: install
	@mkdir -p "$(REPORT_ROOT)/monthly"
	$(PY) "$(APP_DIR)/scripts/ops-monthly-summary.py"

ops-report: ops-audit-export ops-daily-report ops-weekly-report ops-monthly-report
	@echo "Ops report pipeline complete."
