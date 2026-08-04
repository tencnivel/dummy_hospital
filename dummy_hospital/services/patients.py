from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.models.patient import GenderType, Patient
from dummy_hospital.services.exceptions import NotFoundError


class _Unset:
    """Sentinel type used to distinguish an omitted field from an explicit null."""

    __slots__ = ()


_UNSET = _Unset()


async def create_patient(
    session: AsyncSession,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    date_of_birth: date | None = None,
    gender: GenderType | None = None,
    phone: str | None = None,
    email: str | None = None,
    address: str | None = None,
) -> Patient:
    """Add a patient and flush it without committing the caller's transaction."""
    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=gender,
        phone=phone,
        email=email,
        address=address,
    )
    session.add(patient)
    await session.flush()
    return patient


async def get_patient(session: AsyncSession, patient_id: int) -> Patient:
    """Return a patient by primary key or raise NotFoundError."""
    patient = await session.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Patient", patient_id)
    return patient


async def list_patients(
    session: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Patient]:
    """Return a deterministic page of patients ordered by primary key."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    if offset < 0:
        raise ValueError("offset must be greater than or equal to 0")

    result = await session.scalars(
        select(Patient).order_by(Patient.patient_id).limit(limit).offset(offset)
    )
    return list(result)


async def update_patient(
    session: AsyncSession,
    patient_id: int,
    *,
    first_name: str | None | _Unset = _UNSET,
    last_name: str | None | _Unset = _UNSET,
    date_of_birth: date | None | _Unset = _UNSET,
    gender: GenderType | None | _Unset = _UNSET,
    phone: str | None | _Unset = _UNSET,
    email: str | None | _Unset = _UNSET,
    address: str | None | _Unset = _UNSET,
) -> Patient:
    """Apply provided fields and flush without committing the transaction."""
    patient = await get_patient(session, patient_id)

    if not isinstance(first_name, _Unset):
        patient.first_name = first_name
    if not isinstance(last_name, _Unset):
        patient.last_name = last_name
    if not isinstance(date_of_birth, _Unset):
        patient.date_of_birth = date_of_birth
    if not isinstance(gender, _Unset):
        patient.gender = gender
    if not isinstance(phone, _Unset):
        patient.phone = phone
    if not isinstance(email, _Unset):
        patient.email = email
    if not isinstance(address, _Unset):
        patient.address = address

    await session.flush()
    return patient


async def delete_patient(session: AsyncSession, patient_id: int) -> Patient:
    """Delete a patient and flush without committing the transaction."""
    patient = await get_patient(session, patient_id)
    await session.delete(patient)
    await session.flush()
    return patient
