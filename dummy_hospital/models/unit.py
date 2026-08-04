from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from dummy_hospital.db.base import Base

if TYPE_CHECKING:
    from dummy_hospital.models.doctor import Doctor
    from dummy_hospital.models.exam import Exam


class Unit(Base):
    __tablename__ = "unit"
    __table_args__ = (
        PrimaryKeyConstraint("unit_id", name="unit_pkey"),
        UniqueConstraint("unit_code", name="unit_unit_code_key"),
    )

    unit_id: Mapped[int] = mapped_column(Integer, autoincrement=True, nullable=False)
    unit_name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    doctors: Mapped[list[Doctor]] = relationship(
        back_populates="unit",
        passive_deletes=True,
    )
    exams: Mapped[list[Exam]] = relationship(
        back_populates="unit",
        passive_deletes=True,
    )
