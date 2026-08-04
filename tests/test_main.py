from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from dummy_hospital.db.session import get_session
from dummy_hospital.main import create_app


class ReadySession:
    async def execute(self, statement: Any) -> None:
        return None


class UnavailableSession:
    async def execute(self, statement: Any) -> None:
        raise SQLAlchemyError("database unavailable")


async def ready_session() -> AsyncIterator[ReadySession]:
    yield ReadySession()


async def unavailable_session() -> AsyncIterator[UnavailableSession]:
    yield UnavailableSession()


def test_create_app() -> None:
    application = create_app()

    assert isinstance(application, FastAPI)
    assert application.title == "Dummy Hospital API"


def test_liveness_does_not_require_database_configuration(monkeypatch: Any) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with TestClient(create_app()) as client:
        response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_with_available_database_dependency() -> None:
    application = create_app()
    application.dependency_overrides[get_session] = ready_session

    with TestClient(application) as client:
        response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_hides_database_error_details() -> None:
    application = create_app()
    application.dependency_overrides[get_session] = unavailable_session

    with TestClient(application) as client:
        response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}
