from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExamResponse(BaseModel):
    """Exam representation returned by the HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    exam_id: int
    patient_id: int
    doctor_id: int | None
    unit_id: int | None
    exam_date: datetime
    exam_type: str | None
    status: str | None
    notes: str | None
    result: str | None
    created_at: datetime | None
    updated_at: datetime | None
