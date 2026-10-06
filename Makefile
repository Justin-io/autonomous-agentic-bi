.PHONY: install test test-cov build-frontend run run-frontend docker-build docker-up clean

PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
UVICORN := .venv/bin/uvicorn

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	cd frontend && npm install

test:
	$(PYTEST) tests/ -v

test-cov:
	$(PYTEST) tests/ -v --tb=short

build-frontend:
	cd frontend && npm run build

run:
	$(UVICORN) api.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

docker-build:
	docker compose build

docker-up:
	docker compose up -d

clean:
	rm -rf __pycache__ .pytest_cache data/ *.duckdb
