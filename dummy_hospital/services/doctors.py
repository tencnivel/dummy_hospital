from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.models.doctor import Doctor
from dummy_hospital.services._sentinel import UNSET, Unset
from dummy_hospital.services.exceptions import NotFoundError


async def create_doctor(
    session: AsyncSession,
    *,
    first_name: str,
    last_name: str,
    specialty: str | None = None,
    license_number: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    unit_id: int | None = None,
) -> Doctor:
    """Add a doctor and flush it without committing the caller's transaction."""
    doctor = Doctor(
        first_name=first_name,
        last_name=last_name,
        specialty=specialty,
        license_number=license_number,
        phone=phone,
        email=email,
        unit_id=unit_id,
    )
    session.add(doctor)
    await session.flush()
    return doctor


async def get_doctor(session: AsyncSession, doctor_id: int) -> Doctor:
    """Return a doctor by primary key or raise NotFoundError."""
    doctor = await session.get(Doctor, doctor_id)
    if doctor is None:
        raise NotFoundError("Doctor", doctor_id)
    return doctor


async def list_doctors(
    session: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Doctor]:
    """Return a deterministic page of doctors ordered by primary key."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    if offset < 0:
        raise ValueError("offset must be greater than or equal to 0")

    result = await session.scalars(
        select(Doctor).order_by(Doctor.doctor_id).limit(limit).offset(offset)
    )
    return list(result)


async def update_doctor(
    session: AsyncSession,
    doctor_id: int,
    *,
    first_name: str | Unset = UNSET,
    last_name: str | Unset = UNSET,
    specialty: str | None | Unset = UNSET,
    license_number: str | None | Unset = UNSET,
    phone: str | None | Unset = UNSET,
    email: str | None | Unset = UNSET,
    unit_id: int | None | Unset = UNSET,
) -> Doctor:
    """Apply provided fields and flush without committing the transaction."""
    doctor = await get_doctor(session, doctor_id)

    if not isinstance(first_name, Unset):
        doctor.first_name = first_name
    if not isinstance(last_name, Unset):
        doctor.last_name = last_name
    if not isinstance(specialty, Unset):
        doctor.specialty = specialty
    if not isinstance(license_number, Unset):
        doctor.license_number = license_number
    if not isinstance(phone, Unset):
        doctor.phone = phone
    if not isinstance(email, Unset):
        doctor.email = email
    if not isinstance(unit_id, Unset):
        doctor.unit_id = unit_id

    await session.flush()
    return doctor


async def delete_doctor(session: AsyncSession, doctor_id: int) -> Doctor:
    """Delete a doctor and flush without committing the transaction."""
    doctor = await get_doctor(session, doctor_id)
    await session.delete(doctor)
    await session.flush()
    return doctor
