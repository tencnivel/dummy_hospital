from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.api.dependencies import get_session
from dummy_hospital.api.schemas.patient import PatientResponse
from dummy_hospital.services.patients import list_patients

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientResponse])
async def get_patients(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[PatientResponse]:
    """Return a page of patients ordered by identifier."""
    patients = await list_patients(session, limit=limit, offset=offset)
    return [PatientResponse.model_validate(patient) for patient in patients]
