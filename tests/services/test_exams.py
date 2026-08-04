from datetime import datetime
from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from dummy_hospital.models import Exam
from dummy_hospital.services import (
    NotFoundError,
    create_exam,
    delete_exam,
    get_exam,
    list_exams,
    update_exam,
)


def make_session() -> tuple[AsyncSession, AsyncMock]:
    mock = AsyncMock(spec=AsyncSession)
    return cast(AsyncSession, mock), mock


async def test_create_exam_adds_fields_and_leaves_server_defaults_unset() -> None:
    session, mock = make_session()

    exam = await create_exam(
        session,
        patient_id=11,
        doctor_id=2,
        unit_id=3,
        exam_type="MRI",
        notes="Initial scan",
        result="Clear",
    )

    assert exam.patient_id == 11
    assert exam.doctor_id == 2
    assert exam.unit_id == 3
    assert exam.exam_type == "MRI"
    assert exam.notes == "Initial scan"
    assert exam.result == "Clear"
    assert "exam_date" not in exam.__dict__
    assert "status" not in exam.__dict__
    mock.add.assert_called_once_with(exam)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_create_exam_accepts_explicit_date_and_nullable_status() -> None:
    session, _mock = make_session()
    exam_date = datetime(2026, 1, 2, 9, 30)

    exam = await create_exam(session, patient_id=11, exam_date=exam_date, status=None)

    assert exam.exam_date == exam_date
    assert exam.status is None
    assert "status" in exam.__dict__
    assert Exam.__table__.c.status.type.should_evaluate_none is True


async def test_get_exam_returns_existing_exam() -> None:
    session, mock = make_session()
    exam = Exam(patient_id=11)
    mock.get.return_value = exam

    assert await get_exam(session, 7) is exam
    mock.get.assert_awaited_once_with(Exam, 7)
    mock.commit.assert_not_awaited()


async def test_get_exam_raises_not_found() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError, match="Exam with id 404 not found"):
        await get_exam(session, 404)


async def test_list_exams_orders_and_paginates() -> None:
    session, mock = make_session()
    exams = [Exam(patient_id=11)]
    mock.scalars.return_value = exams

    assert await list_exams(session) == exams
    statement = cast(Select[tuple[Exam]], mock.scalars.await_args.args[0])
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    sql = str(statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
    assert "ORDER BY exam.exam_id" in sql
    assert "LIMIT 50 OFFSET 0" in sql
    mock.commit.assert_not_awaited()


@pytest.mark.parametrize(("limit", "offset"), [(0, 0), (101, 0), (10, -1)])
async def test_list_exams_validates_before_querying(limit: int, offset: int) -> None:
    session, mock = make_session()

    with pytest.raises(ValueError):
        await list_exams(session, limit=limit, offset=offset)

    mock.scalars.assert_not_awaited()


async def test_update_exam_keeps_omitted_and_clears_nullable_fields() -> None:
    session, mock = make_session()
    exam_date = datetime(2026, 1, 2, 9, 30)
    exam = Exam(
        patient_id=11,
        doctor_id=2,
        unit_id=3,
        exam_date=exam_date,
        exam_type="MRI",
        status="pending",
        notes="Initial scan",
    )
    mock.get.return_value = exam

    result = await update_exam(
        session,
        7,
        doctor_id=None,
        status=None,
        notes="Updated",
    )

    assert result is exam
    assert exam.patient_id == 11
    assert exam.unit_id == 3
    assert exam.exam_date == exam_date
    assert exam.exam_type == "MRI"
    assert exam.doctor_id is None
    assert exam.status is None
    assert exam.notes == "Updated"
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_update_exam_updates_non_nullable_fields_with_non_null_values() -> None:
    session, mock = make_session()
    old_date = datetime(2026, 1, 2, 9, 30)
    new_date = datetime(2026, 2, 3, 10, 45)
    exam = Exam(patient_id=11, exam_date=old_date)
    mock.get.return_value = exam

    await update_exam(session, 7, patient_id=12, exam_date=new_date)

    assert exam.patient_id == 12
    assert exam.exam_date == new_date


async def test_update_exam_not_found_does_not_flush() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError):
        await update_exam(session, 404, patient_id=12)

    mock.flush.assert_not_awaited()


async def test_delete_exam_deletes_and_flushes_without_commit() -> None:
    session, mock = make_session()
    exam = Exam(patient_id=11)
    mock.get.return_value = exam

    assert await delete_exam(session, 7) is exam
    mock.delete.assert_awaited_once_with(exam)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_delete_exam_not_found_does_not_delete() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError):
        await delete_exam(session, 404)

    mock.delete.assert_not_awaited()
    mock.flush.assert_not_awaited()
