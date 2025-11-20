PYTHON ?= python3
UVICORN ?= uvicorn
CELERY ?= celery
APP_MODULE ?= app.main:app

.PHONY: install install-dev fmt lint typecheck test api worker clean

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install -r requirements-dev.txt

fmt:
	ruff check . --fix
	black .
	isort .

lint:
	ruff check .
	black . --check
	isort . --check-only

typecheck:
	mypy .

test:
	pytest

api:
	PYTHONPATH=.. $(UVICORN) $(APP_MODULE) --reload --host 0.0.0.0 --port 8000

worker:
	$(CELERY) -A workers.ai_worker.app worker --loglevel=info

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache .coverage htmlcov

.PHONY: migrate revision

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(msg)"

.PHONY: seed
seed:
	PYTHONPATH=.. $(PYTHON) -m backend.db.seeds.seed_initial
