from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UnitResponse(BaseModel):
    """Hospital unit representation returned by the HTTP API."""

    model_config = ConfigDict(from_attributes=True)

    unit_id: int
    unit_name: str
    unit_code: str | None
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None
