from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.api.dependencies import get_session
from dummy_hospital.api.schemas.exam import ExamResponse
from dummy_hospital.services.exams import list_exams

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("", response_model=list[ExamResponse])
async def get_exams(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ExamResponse]:
    """Return a page of exams ordered by identifier."""
    exams = await list_exams(session, limit=limit, offset=offset)
    return [ExamResponse.model_validate(exam) for exam in exams]
