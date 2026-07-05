# Setup instructions
setup-ingestion:
	cd ingestion && uv sync

setup-api:
	cd api && uv sync

setup-ml:
	cd ml && uv venv --python 3.11 && uv sync

setup-all:	setup-ingestion setup-api setup-ml

# Run shortcuts

# uvicorn - automatic reload flag on (local only)
run-api:
	cd api && uv run uvicorn main:app --reload

run-ingestion:
	cd ingestion && uv run python cfpb_client.py

# Testing shortcuts

test-api:
	cd api && uv add --dev pytest httpx

test-ml:
	cd ml && uv run pytest

test-ingestion:
	cd ingestion && uv run pytest

test-all: test-api test-ml test-ingestion

# Lint is added to the uv -> dependencies
lint-all:
	cd api && uv run ruff check .
	cd ml && uv run ruff check .
	cd ingestion && uv run ruff check .

# Docker commands:

up:
	docker compose up -d

down:
	docker compose down -v

logs:
	docker compose logs -f
	

# PHONY declaration
.PHONY: setup-ingestion setup-api setup-ml setup-all \
		run-api run-ingestion \
		test-api test-ml test-ingestion \
		lint-all up down logs