from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.models.exam import Exam
from dummy_hospital.services._sentinel import UNSET, Unset
from dummy_hospital.services.exceptions import NotFoundError


async def create_exam(
    session: AsyncSession,
    *,
    patient_id: int,
    doctor_id: int | None = None,
    unit_id: int | None = None,
    exam_date: datetime | Unset = UNSET,
    exam_type: str | None = None,
    status: str | None | Unset = UNSET,
    notes: str | None = None,
    result: str | None = None,
) -> Exam:
    """Add an exam and flush it without committing the caller's transaction."""
    exam = Exam(
        patient_id=patient_id,
        doctor_id=doctor_id,
        unit_id=unit_id,
        exam_type=exam_type,
        notes=notes,
        result=result,
    )
    if not isinstance(exam_date, Unset):
        exam.exam_date = exam_date
    if not isinstance(status, Unset):
        exam.status = status

    session.add(exam)
    await session.flush()
    return exam


async def get_exam(session: AsyncSession, exam_id: int) -> Exam:
    """Return an exam by primary key or raise NotFoundError."""
    exam = await session.get(Exam, exam_id)
    if exam is None:
        raise NotFoundError("Exam", exam_id)
    return exam


async def list_exams(
    session: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Exam]:
    """Return a deterministic page of exams ordered by primary key."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    if offset < 0:
        raise ValueError("offset must be greater than or equal to 0")

    result = await session.scalars(select(Exam).order_by(Exam.exam_id).limit(limit).offset(offset))
    return list(result)


async def update_exam(
    session: AsyncSession,
    exam_id: int,
    *,
    patient_id: int | Unset = UNSET,
    doctor_id: int | None | Unset = UNSET,
    unit_id: int | None | Unset = UNSET,
    exam_date: datetime | Unset = UNSET,
    exam_type: str | None | Unset = UNSET,
    status: str | None | Unset = UNSET,
    notes: str | None | Unset = UNSET,
    result: str | None | Unset = UNSET,
) -> Exam:
    """Apply provided fields and flush without committing the transaction."""
    exam = await get_exam(session, exam_id)

    if not isinstance(patient_id, Unset):
        exam.patient_id = patient_id
    if not isinstance(doctor_id, Unset):
        exam.doctor_id = doctor_id
    if not isinstance(unit_id, Unset):
        exam.unit_id = unit_id
    if not isinstance(exam_date, Unset):
        exam.exam_date = exam_date
    if not isinstance(exam_type, Unset):
        exam.exam_type = exam_type
    if not isinstance(status, Unset):
        exam.status = status
    if not isinstance(notes, Unset):
        exam.notes = notes
    if not isinstance(result, Unset):
        exam.result = result

    await session.flush()
    return exam


async def delete_exam(session: AsyncSession, exam_id: int) -> Exam:
    """Delete an exam and flush without committing the transaction."""
    exam = await get_exam(session, exam_id)
    await session.delete(exam)
    await session.flush()
    return exam
