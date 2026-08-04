.PHONY: install run test lint format typecheck check

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
