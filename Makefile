.PHONY: install dev build-css init-db test lint create-admin db

install:
	uv sync
	cd frontend && npm ci

db:
	docker compose up -d

dev:
	uv run uvicorn app.main:app --reload --port 8000 & cd frontend && npm run watch

build-css:
	cd frontend && npm run build

init-db:
	uv run python -m app.cli init-db

test:
	uv run pytest -q

lint:
	uv run ruff check .

create-admin:
	uv run python -m app.cli create-admin --name "$(NAME)" --email "$(EMAIL)"

