from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from dummy_hospital.models import Doctor
from dummy_hospital.services import (
    NotFoundError,
    create_doctor,
    delete_doctor,
    get_doctor,
    list_doctors,
    update_doctor,
)


def make_session() -> tuple[AsyncSession, AsyncMock]:
    mock = AsyncMock(spec=AsyncSession)
    return cast(AsyncSession, mock), mock


async def test_create_doctor_adds_typed_fields_and_flushes_without_commit() -> None:
    session, mock = make_session()

    doctor = await create_doctor(
        session,
        first_name="Elizabeth",
        last_name="Blackwell",
        specialty="General medicine",
        license_number="LIC-1",
        phone="555-0101",
        email="doctor@example.test",
        unit_id=3,
    )

    assert doctor.first_name == "Elizabeth"
    assert doctor.last_name == "Blackwell"
    assert doctor.specialty == "General medicine"
    assert doctor.license_number == "LIC-1"
    assert doctor.phone == "555-0101"
    assert doctor.email == "doctor@example.test"
    assert doctor.unit_id == 3
    mock.add.assert_called_once_with(doctor)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_get_doctor_returns_existing_doctor() -> None:
    session, mock = make_session()
    doctor = Doctor(first_name="Elizabeth", last_name="Blackwell")
    mock.get.return_value = doctor

    assert await get_doctor(session, 7) is doctor
    mock.get.assert_awaited_once_with(Doctor, 7)
    mock.commit.assert_not_awaited()


async def test_get_doctor_raises_not_found() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError, match="Doctor with id 404 not found"):
        await get_doctor(session, 404)


async def test_list_doctors_orders_and_paginates() -> None:
    session, mock = make_session()
    doctors = [Doctor(first_name="A", last_name="B")]
    mock.scalars.return_value = doctors

    assert await list_doctors(session) == doctors
    statement = cast(Select[tuple[Doctor]], mock.scalars.await_args.args[0])
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    sql = str(statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
    assert "ORDER BY doctor.doctor_id" in sql
    assert "LIMIT 50 OFFSET 0" in sql
    mock.commit.assert_not_awaited()


@pytest.mark.parametrize(("limit", "offset"), [(0, 0), (101, 0), (10, -1)])
async def test_list_doctors_validates_before_querying(limit: int, offset: int) -> None:
    session, mock = make_session()

    with pytest.raises(ValueError):
        await list_doctors(session, limit=limit, offset=offset)

    mock.scalars.assert_not_awaited()


async def test_update_doctor_keeps_omitted_and_clears_nullable_fields() -> None:
    session, mock = make_session()
    doctor = Doctor(
        first_name="Elizabeth",
        last_name="Blackwell",
        specialty="General medicine",
        unit_id=3,
    )
    mock.get.return_value = doctor

    result = await update_doctor(session, 7, specialty=None, unit_id=None)

    assert result is doctor
    assert doctor.first_name == "Elizabeth"
    assert doctor.last_name == "Blackwell"
    assert doctor.specialty is None
    assert doctor.unit_id is None
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_update_doctor_not_found_does_not_flush() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError):
        await update_doctor(session, 404, first_name="Nobody")

    mock.flush.assert_not_awaited()


async def test_delete_doctor_deletes_and_flushes_without_commit() -> None:
    session, mock = make_session()
    doctor = Doctor(first_name="Elizabeth", last_name="Blackwell")
    mock.get.return_value = doctor

    assert await delete_doctor(session, 7) is doctor
    mock.delete.assert_awaited_once_with(doctor)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_delete_doctor_not_found_does_not_delete() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError):
        await delete_doctor(session, 404)

    mock.delete.assert_not_awaited()
    mock.flush.assert_not_awaited()
