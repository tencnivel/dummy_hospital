from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.api.dependencies import get_session
from dummy_hospital.api.schemas.doctor import DoctorResponse
from dummy_hospital.services.doctors import list_doctors

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorResponse])
async def get_doctors(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[DoctorResponse]:
    """Return a page of doctors ordered by identifier."""
    doctors = await list_doctors(session, limit=limit, offset=offset)
    return [DoctorResponse.model_validate(doctor) for doctor in doctors]
