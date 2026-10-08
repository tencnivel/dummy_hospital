from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from dummy_hospital.models import GenderType


class PatientResponse(BaseModel):
    """Patient representation returned by the HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    patient_id: int
    first_name: str | None
    last_name: str | None
    date_of_birth: date | None
    gender: GenderType | None
    phone: str | None
    email: str | None
    address: str | None
    created_at: datetime | None
    updated_at: datetime | None
