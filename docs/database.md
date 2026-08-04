# Database

## Local development connection

The application reads `DATABASE_URL` from the environment or a local `.env`
file. `.env.example` contains the supplied local development connection string.
The application does not open a connection during module import; the async
engine and sessions are created on first database use.

## Current schema

`db_dump/dummy_hospital_schema_1.sql` is the immutable reference dump of the
existing PostgreSQL schema. It currently defines:

- the `gender_type` enum;
- `patient`, `doctor`, `unit`, and `exam` tables;
- their sequences, indexes, unique constraints, and foreign keys.

The scaffold does not yet contain ORM mappings and does not alter this schema.

## Migration policy

Alembic is wired to `dummy_hospital.db.base.Base.metadata`, but the versions
directory is intentionally empty. The next database phase should:

1. map the existing schema exactly in SQLAlchemy, including PostgreSQL-specific
   types, nullability, defaults, indexes, constraints, and deletion behavior;
2. compare metadata with the live database and the reference dump;
3. create a baseline revision that can build an empty database;
4. stamp that baseline on the existing database only after parity is verified;
5. use subsequent Alembic revisions for all schema changes.

Tests must use an isolated test database or dependency overrides. They must not
run migrations or destructive operations against the local development database.
