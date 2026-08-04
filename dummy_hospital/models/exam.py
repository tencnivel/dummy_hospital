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
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from dummy_hospital.db.base import Base

if TYPE_CHECKING:
    from dummy_hospital.models.doctor import Doctor
    from dummy_hospital.models.patient import Patient
    from dummy_hospital.models.unit import Unit


class Exam(Base):
    __tablename__ = "exam"
    __table_args__ = (
        PrimaryKeyConstraint("exam_id", name="exam_pkey"),
        Index("idx_exam_date", "exam_date"),
        Index("idx_exam_doctor_id", "doctor_id"),
        Index("idx_exam_patient_id", "patient_id"),
        Index("idx_exam_unit_id", "unit_id"),
    )

    exam_id: Mapped[int] = mapped_column(Integer, autoincrement=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "patient.patient_id",
            name="exam_patient_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    doctor_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "doctor.doctor_id",
            name="exam_doctor_id_fkey",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    unit_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "unit.unit_id",
            name="exam_unit_id_fkey",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    exam_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.current_timestamp(),
        nullable=False,
    )
    exam_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str | None] = mapped_column(
        String(50).evaluates_none(),
        server_default=text("'pending'::character varying"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    patient: Mapped[Patient] = relationship(back_populates="exams")
    doctor: Mapped[Doctor | None] = relationship(back_populates="exams")
    unit: Mapped[Unit | None] = relationship(back_populates="exams")
