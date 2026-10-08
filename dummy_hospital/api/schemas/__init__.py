"""Pydantic request and response DTOs owned by the HTTP API."""

from dummy_hospital.api.schemas.doctor import DoctorResponse
from dummy_hospital.api.schemas.exam import ExamResponse
from dummy_hospital.api.schemas.patient import PatientResponse
from dummy_hospital.api.schemas.unit import UnitResponse

__all__ = ["DoctorResponse", "ExamResponse", "PatientResponse", "UnitResponse"]
