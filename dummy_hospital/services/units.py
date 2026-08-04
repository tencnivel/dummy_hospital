from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.models.unit import Unit
from dummy_hospital.services._sentinel import UNSET, Unset
from dummy_hospital.services.exceptions import NotFoundError


async def create_unit(
    session: AsyncSession,
    *,
    unit_name: str,
    unit_code: str | None = None,
    description: str | None = None,
) -> Unit:
    """Add a unit and flush it without committing the caller's transaction."""
    unit = Unit(unit_name=unit_name, unit_code=unit_code, description=description)
    session.add(unit)
    await session.flush()
    return unit


async def get_unit(session: AsyncSession, unit_id: int) -> Unit:
    """Return a unit by primary key or raise NotFoundError."""
    unit = await session.get(Unit, unit_id)
    if unit is None:
        raise NotFoundError("Unit", unit_id)
    return unit


async def list_units(
    session: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[Unit]:
    """Return a deterministic page of units ordered by primary key."""
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    if offset < 0:
        raise ValueError("offset must be greater than or equal to 0")

    result = await session.scalars(select(Unit).order_by(Unit.unit_id).limit(limit).offset(offset))
    return list(result)


async def update_unit(
    session: AsyncSession,
    unit_id: int,
    *,
    unit_name: str | Unset = UNSET,
    unit_code: str | None | Unset = UNSET,
    description: str | None | Unset = UNSET,
) -> Unit:
    """Apply provided fields and flush without committing the transaction."""
    unit = await get_unit(session, unit_id)

    if not isinstance(unit_name, Unset):
        unit.unit_name = unit_name
    if not isinstance(unit_code, Unset):
        unit.unit_code = unit_code
    if not isinstance(description, Unset):
        unit.description = description

    await session.flush()
    return unit


async def delete_unit(session: AsyncSession, unit_id: int) -> Unit:
    """Delete a unit and flush without committing the transaction."""
    unit = await get_unit(session, unit_id)
    await session.delete(unit)
    await session.flush()
    return unit
