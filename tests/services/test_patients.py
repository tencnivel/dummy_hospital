from datetime import date
from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from dummy_hospital.models import GenderType, Patient
from dummy_hospital.services import (
    NotFoundError,
    create_patient,
    delete_patient,
    get_patient,
    list_patients,
    update_patient,
)


def make_session() -> tuple[AsyncSession, AsyncMock]:
    mock = AsyncMock(spec=AsyncSession)
    return cast(AsyncSession, mock), mock


async def test_create_patient_adds_typed_fields_and_flushes_without_commit() -> None:
    session, mock = make_session()
    birth_date = date(1985, 6, 15)

    patient = await create_patient(
        session,
        first_name="Ada",
        last_name="Lovelace",
        date_of_birth=birth_date,
        gender=GenderType.FEMALE,
        phone="555-0100",
        email="ada@example.test",
        address="1 Computing Lane",
    )

    assert patient.first_name == "Ada"
    assert patient.last_name == "Lovelace"
    assert patient.date_of_birth == birth_date
    assert patient.gender is GenderType.FEMALE
    assert patient.phone == "555-0100"
    assert patient.email == "ada@example.test"
    assert patient.address == "1 Computing Lane"
    mock.add.assert_called_once_with(patient)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()
    mock.refresh.assert_not_awaited()


async def test_get_patient_returns_existing_patient_without_transaction_control() -> None:
    session, mock = make_session()
    patient = Patient(first_name="Ada")
    mock.get.return_value = patient

    result = await get_patient(session, 7)

    assert result is patient
    mock.get.assert_awaited_once_with(Patient, 7)
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_get_patient_raises_service_not_found_error() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError, match="Patient with id 404 not found") as caught:
        await get_patient(session, 404)

    assert caught.value.entity == "Patient"
    assert caught.value.entity_id == 404
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_list_patients_orders_and_paginates_without_commit() -> None:
    session, mock = make_session()
    patients = [Patient(first_name="Ada"), Patient(first_name="Grace")]
    mock.scalars.return_value = patients

    result = await list_patients(session, limit=10, offset=3)

    assert result == patients
    statement = cast(Select[tuple[Patient]], mock.scalars.await_args.args[0])
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    sql = str(statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
    assert "ORDER BY patient.patient_id" in sql
    assert "LIMIT 10 OFFSET 3" in sql
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


@pytest.mark.parametrize(
    ("limit", "offset", "message"),
    [
        (0, 0, "limit must be between 1 and 100"),
        (101, 0, "limit must be between 1 and 100"),
        (10, -1, "offset must be greater than or equal to 0"),
    ],
)
async def test_list_patients_rejects_invalid_pagination(
    limit: int,
    offset: int,
    message: str,
) -> None:
    session, mock = make_session()

    with pytest.raises(ValueError, match=message):
        await list_patients(session, limit=limit, offset=offset)

    mock.scalars.assert_not_awaited()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_update_patient_distinguishes_omitted_fields_from_explicit_none() -> None:
    session, mock = make_session()
    patient = Patient(
        first_name="Ada",
        last_name="Lovelace",
        gender=GenderType.FEMALE,
        email="ada@example.test",
    )
    mock.get.return_value = patient

    result = await update_patient(
        session,
        7,
        first_name=None,
        email="new@example.test",
    )

    assert result is patient
    assert patient.first_name is None
    assert patient.last_name == "Lovelace"
    assert patient.gender is GenderType.FEMALE
    assert patient.email == "new@example.test"
    mock.get.assert_awaited_once_with(Patient, 7)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_update_patient_raises_not_found_without_flushing() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError, match="Patient with id 404 not found"):
        await update_patient(session, 404, last_name="Nobody")

    mock.flush.assert_not_awaited()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_delete_patient_deletes_and_flushes_without_commit() -> None:
    session, mock = make_session()
    patient = Patient(first_name="Ada")
    mock.get.return_value = patient

    result = await delete_patient(session, 7)

    assert result is patient
    mock.get.assert_awaited_once_with(Patient, 7)
    mock.delete.assert_awaited_once_with(patient)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_delete_patient_raises_not_found_without_deleting() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError, match="Patient with id 404 not found"):
        await delete_patient(session, 404)

    mock.delete.assert_not_awaited()
    mock.flush.assert_not_awaited()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()
