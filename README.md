# Dummy Hospital API

Initial FastAPI backend scaffold for the Dummy Hospital application.

## Requirements

- Python 3.12 or newer
- PostgreSQL
- [uv](https://docs.astral.sh/uv/)
- Make (optional convenience wrapper for development commands)

## Local setup

```bash
cp .env.example .env
uv sync --extra dev
uv run uvicorn dummy_hospital.main:app --reload
```

The example configuration points to the existing local development database.
Do not use those credentials outside local development.

## Endpoints

- `GET /healthz` checks application liveness without accessing PostgreSQL.
- `GET /readyz` executes `SELECT 1` against PostgreSQL and returns HTTP 503 if it is unavailable.
- Application routes will live under `/api/v1`; resource routers exist but intentionally expose no CRUD endpoints yet.
- Interactive OpenAPI documentation is available at `/docs` while the application is running.

## Development checks

```bash
make check
```

The individual commands are `make lint`, `make typecheck`, and `make test`. Without Make,
run the corresponding `uv run ruff check .`, `uv run mypy dummy_hospital tests`, and
`uv run pytest` commands directly.

### PostgreSQL integration tests

Integration tests use the database configured by `TEST_DATABASE_URL` and skip when it is not
configured. A dedicated test database is strongly recommended. To create one, an administrator
must create the database with the application role as owner before that role loads the schema:

```bash
createdb --owner=dummy_hospital dummy_hospital_test  # run as a PostgreSQL administrator
psql -h localhost -U dummy_hospital -d dummy_hospital_test \
  -f db_dump/dummy_hospital_schema_1.sql
# TEST_DATABASE_URL=postgresql+asyncpg://.../dummy_hospital_test
uv run pytest -m integration
```

Each test runs in a transaction that is rolled back. The current `dummy_hospital` role does
not have permission to create databases, so database creation requires an administrator.

## Database migrations

Alembic is configured, but there are intentionally no revisions yet. Do not run
autogeneration until the SQLAlchemy models reproduce the existing PostgreSQL
schema exactly. See [docs/database.md](docs/database.md).

The original schema dump under `db_dump/` is reference material and must not be
edited by application tooling.
