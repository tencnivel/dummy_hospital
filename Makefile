.PHONY: install run test lint format typecheck check seed-db check-env compose-up compose-down compose-shell compose-seed

# Host targets: run directly on the host and require uv and the development dependencies.
install:
	uv sync --extra dev

run:
	uv run uvicorn dummy_hospital.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy dummy_hospital scripts tests

check: lint typecheck test

# Shared target: can run on the host or from inside the app container.
seed-db:
	uv run --no-sync python scripts/seed_database.py

# Host Compose targets: run on the host and manage or execute commands in containers.
check-env:
	@test -f .env || { echo "Error: .env does not exist. Copy .env.example first."; exit 1; }
	@if grep -nE '<[^>]+>' .env; then \
		echo "Error: replace the placeholders listed above in .env."; \
		exit 1; \
	fi

compose-up: check-env
	docker compose up --build

compose-down:
	docker compose down

compose-shell:
	docker compose exec dummy_hospital_app sh

compose-seed:
	docker compose exec dummy_hospital_app make seed-db
