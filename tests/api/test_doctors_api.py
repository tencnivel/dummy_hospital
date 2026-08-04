from collections.abc import AsyncIterator
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.api.v1 import doctors as doctors_api
from dummy_hospital.db.session import get_session
from dummy_hospital.main import create_app
from dummy_hospital.models import Doctor

stubbed_session = cast(AsyncSession, object())


async def stub_session() -> AsyncIterator[AsyncSession]:
    yield stubbed_session


def test_list_doctors_returns_serialized_page(monkeypatch: pytest.MonkeyPatch) -> None:
    list_doctors_mock = AsyncMock(
        return_value=[
            Doctor(
                doctor_id=7,
                first_name="Meredith",
                last_name="Grey",
                specialty="General Surgery",
                license_number="MED-00000007",
                phone="5550107",
                email="meredith.grey@example.test",
                unit_id=2,
            )
        ]
    )
    monkeypatch.setattr(doctors_api, "list_doctors", list_doctors_mock)
    application = create_app()
    application.dependency_overrides[get_session] = stub_session

    with TestClient(application) as client:
        response = client.get("/api/v1/doctors?limit=10&offset=5")

    assert response.status_code == 200
    assert response.json() == [
        {
            "doctor_id": 7,
            "first_name": "Meredith",
            "last_name": "Grey",
            "specialty": "General Surgery",
            "license_number": "MED-00000007",
            "phone": "5550107",
            "email": "meredith.grey@example.test",
            "unit_id": 2,
            "created_at": None,
            "updated_at": None,
        }
    ]
    list_doctors_mock.assert_awaited_once_with(stubbed_session, limit=10, offset=5)


def test_list_doctors_validates_pagination_before_service_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    list_doctors_mock = AsyncMock(return_value=[])
    monkeypatch.setattr(doctors_api, "list_doctors", list_doctors_mock)
    application = create_app()
    application.dependency_overrides[get_session] = stub_session

    with TestClient(application) as client:
        response = client.get("/api/v1/doctors?limit=101&offset=-1")

    assert response.status_code == 422
    list_doctors_mock.assert_not_awaited()
