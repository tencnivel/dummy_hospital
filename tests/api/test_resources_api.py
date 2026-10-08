from collections.abc import AsyncIterator
from datetime import date, datetime
from types import ModuleType
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.api.v1 import exams as exams_api
from dummy_hospital.api.v1 import patients as patients_api
from dummy_hospital.api.v1 import units as units_api
from dummy_hospital.db.session import get_session
from dummy_hospital.main import create_app
from dummy_hospital.models import Exam, GenderType, Patient, Unit

stubbed_session = cast(AsyncSession, object())


async def stub_session() -> AsyncIterator[AsyncSession]:
    yield stubbed_session


def test_list_patients_returns_serialized_page(monkeypatch: pytest.MonkeyPatch) -> None:
    list_patients_mock = AsyncMock(
        return_value=[
            Patient(
                patient_id=3,
                first_name="Ellis",
                last_name="Grey",
                date_of_birth=date(1953, 2, 1),
                gender=GenderType.FEMALE,
                phone="5550103",
                email="ellis.grey@example.test",
                address="Seattle",
            )
        ]
    )
    monkeypatch.setattr(patients_api, "list_patients", list_patients_mock)
    application = create_app()
    application.dependency_overrides[get_session] = stub_session

    with TestClient(application) as client:
        response = client.get("/api/v1/patients?limit=10&offset=5")

    assert response.status_code == 200
    assert response.json() == [
        {
            "patient_id": 3,
            "first_name": "Ellis",
            "last_name": "Grey",
            "date_of_birth": "1953-02-01",
            "gender": "female",
            "phone": "5550103",
            "email": "ellis.grey@example.test",
            "address": "Seattle",
            "created_at": None,
            "updated_at": None,
        }
    ]
    list_patients_mock.assert_awaited_once_with(stubbed_session, limit=10, offset=5)


def test_list_units_returns_serialized_page(monkeypatch: pytest.MonkeyPatch) -> None:
    list_units_mock = AsyncMock(
        return_value=[
            Unit(
                unit_id=4,
                unit_name="Cardiology",
                unit_code="CARD",
                description="Cardiac care",
            )
        ]
    )
    monkeypatch.setattr(units_api, "list_units", list_units_mock)
    application = create_app()
    application.dependency_overrides[get_session] = stub_session

    with TestClient(application) as client:
        response = client.get("/api/v1/units?limit=20&offset=2")

    assert response.status_code == 200
    assert response.json() == [
        {
            "unit_id": 4,
            "unit_name": "Cardiology",
            "unit_code": "CARD",
            "description": "Cardiac care",
            "created_at": None,
            "updated_at": None,
        }
    ]
    list_units_mock.assert_awaited_once_with(stubbed_session, limit=20, offset=2)


def test_list_exams_returns_serialized_page(monkeypatch: pytest.MonkeyPatch) -> None:
    list_exams_mock = AsyncMock(
        return_value=[
            Exam(
                exam_id=8,
                patient_id=3,
                doctor_id=7,
                unit_id=4,
                exam_date=datetime(2026, 10, 8, 12, 30),
                exam_type="Consultation",
                status="completed",
                notes="Follow-up",
                result="Stable",
            )
        ]
    )
    monkeypatch.setattr(exams_api, "list_exams", list_exams_mock)
    application = create_app()
    application.dependency_overrides[get_session] = stub_session

    with TestClient(application) as client:
        response = client.get("/api/v1/exams?limit=5&offset=1")

    assert response.status_code == 200
    assert response.json() == [
        {
            "exam_id": 8,
            "patient_id": 3,
            "doctor_id": 7,
            "unit_id": 4,
            "exam_date": "2026-10-08T12:30:00",
            "exam_type": "Consultation",
            "status": "completed",
            "notes": "Follow-up",
            "result": "Stable",
            "created_at": None,
            "updated_at": None,
        }
    ]
    list_exams_mock.assert_awaited_once_with(stubbed_session, limit=5, offset=1)


@pytest.mark.parametrize(
    ("api_module", "service_name", "path"),
    [
        (patients_api, "list_patients", "/api/v1/patients"),
        (units_api, "list_units", "/api/v1/units"),
        (exams_api, "list_exams", "/api/v1/exams"),
    ],
)
def test_list_endpoints_validate_pagination_before_service_call(
    monkeypatch: pytest.MonkeyPatch,
    api_module: ModuleType,
    service_name: str,
    path: str,
) -> None:
    service_mock = AsyncMock(return_value=[])
    monkeypatch.setattr(api_module, service_name, service_mock)
    application = create_app()
    application.dependency_overrides[get_session] = stub_session

    with TestClient(application) as client:
        response = client.get(f"{path}?limit=101&offset=-1")

    assert response.status_code == 422
    service_mock.assert_not_awaited()
