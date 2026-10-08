from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.api.dependencies import get_session
from dummy_hospital.api.schemas.unit import UnitResponse
from dummy_hospital.services.units import list_units

router = APIRouter(prefix="/units", tags=["units"])


@router.get("", response_model=list[UnitResponse])
async def get_units(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[UnitResponse]:
    """Return a page of hospital units ordered by identifier."""
    units = await list_units(session, limit=limit, offset=offset)
    return [UnitResponse.model_validate(unit) for unit in units]
