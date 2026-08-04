from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Index, Integer, PrimaryKeyConstraint, String, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from dummy_hospital.db.base import Base

if TYPE_CHECKING:
    from dummy_hospital.models.exam import Exam


class GenderType(enum.StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


gender_type = ENUM(
    GenderType,
    name="gender_type",
    values_callable=lambda enum_class: [member.value for member in enum_class],
)


class Patient(Base):
    __tablename__ = "patient"
    __table_args__ = (
        PrimaryKeyConstraint("patient_id", name="patient_pkey"),
        Index("idx_patient_last_name", "last_name"),
    )

    patient_id: Mapped[int] = mapped_column(Integer, autoincrement=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[GenderType | None] = mapped_column(gender_type, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=True,
    )

    exams: Mapped[list[Exam]] = relationship(
        back_populates="patient",
        passive_deletes="all",
    )
