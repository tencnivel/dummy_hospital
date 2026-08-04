from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from dummy_hospital.db.base import Base

if TYPE_CHECKING:
    from dummy_hospital.models.exam import Exam
    from dummy_hospital.models.unit import Unit


class Doctor(Base):
    __tablename__ = "doctor"
    __table_args__ = (
        PrimaryKeyConstraint("doctor_id", name="doctor_pkey"),
        UniqueConstraint("license_number", name="doctor_license_number_key"),
        Index("idx_doctor_last_name", "last_name"),
        Index("idx_doctor_unit_id", "unit_id"),
    )

    doctor_id: Mapped[int] = mapped_column(Integer, autoincrement=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "unit.unit_id",
            name="doctor_unit_id_fkey",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
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

    unit: Mapped[Unit | None] = relationship(back_populates="doctors")
    exams: Mapped[list[Exam]] = relationship(
        back_populates="doctor",
        passive_deletes=True,
    )
