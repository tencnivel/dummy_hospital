from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DoctorResponse(BaseModel):
    """Doctor representation returned by the HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    doctor_id: int
    first_name: str
    last_name: str
    specialty: str | None
    license_number: str | None
    phone: str | None
    email: str | None
    unit_id: int | None
    created_at: datetime | None
    updated_at: datetime | None
