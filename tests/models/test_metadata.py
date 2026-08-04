from typing import cast

from sqlalchemy import DateTime, String, Table, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import configure_mappers
from sqlalchemy.schema import CreateTable

from dummy_hospital.db.base import Base
from dummy_hospital.models import Doctor, Exam, GenderType, Patient, Unit


def test_all_existing_tables_are_registered() -> None:
    assert set(Base.metadata.tables) == {"doctor", "exam", "patient", "unit"}


def test_primary_keys_use_named_constraints_and_postgresql_integer_sequences() -> None:
    expected = {
        Patient: ("patient_id", "patient_pkey"),
        Doctor: ("doctor_id", "doctor_pkey"),
        Unit: ("unit_id", "unit_pkey"),
        Exam: ("exam_id", "exam_pkey"),
    }

    for model, (column_name, constraint_name) in expected.items():
        table = cast(Table, model.__table__)
        column = table.c[column_name]
        dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
        ddl = str(CreateTable(table).compile(dialect=dialect))
        assert table.primary_key.name == constraint_name
        assert list(table.primary_key.columns) == [column]
        assert column.autoincrement is True
        assert f"{column_name} SERIAL NOT NULL" in ddl


def test_gender_uses_the_existing_native_postgresql_enum() -> None:
    gender_column = Patient.__table__.c.gender

    assert isinstance(gender_column.type, ENUM)
    assert gender_column.type.native_enum is True
    assert gender_column.type.name == "gender_type"
    # PostgreSQL's default search path resolves this unqualified native type to
    # public.gender_type.
    assert gender_column.type.schema is None
    assert gender_column.type.enums == [member.value for member in GenderType]


def test_varchar_lengths_and_nullability_match_the_dump() -> None:
    first_name_type = Doctor.__table__.c.first_name.type
    license_number_type = Doctor.__table__.c.license_number.type
    phone_type = Doctor.__table__.c.phone.type
    status_type = Exam.__table__.c.status.type

    assert isinstance(first_name_type, String)
    assert isinstance(license_number_type, String)
    assert isinstance(phone_type, String)
    assert isinstance(status_type, String)
    assert first_name_type.length == 100
    assert Doctor.__table__.c.first_name.nullable is False
    assert license_number_type.length == 50
    assert phone_type.length == 20
    assert Patient.__table__.c.first_name.nullable is True
    assert Unit.__table__.c.unit_name.nullable is False
    assert Exam.__table__.c.patient_id.nullable is False
    assert Exam.__table__.c.exam_date.nullable is False
    assert status_type.length == 50


def test_named_unique_constraints_and_indexes_match_the_dump() -> None:
    doctor_table = cast(Table, Doctor.__table__)
    unit_table = cast(Table, Unit.__table__)
    doctor_unique_names = {
        constraint.name
        for constraint in doctor_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    unit_unique_names = {
        constraint.name
        for constraint in unit_table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    indexes = {
        table.name: {index.name for index in table.indexes}
        for table in Base.metadata.tables.values()
    }

    assert doctor_unique_names == {"doctor_license_number_key"}
    assert unit_unique_names == {"unit_unit_code_key"}
    assert indexes == {
        "doctor": {"idx_doctor_last_name", "idx_doctor_unit_id"},
        "exam": {
            "idx_exam_date",
            "idx_exam_doctor_id",
            "idx_exam_patient_id",
            "idx_exam_unit_id",
        },
        "patient": {"idx_patient_last_name"},
        "unit": set(),
    }


def test_foreign_keys_keep_names_targets_and_delete_actions() -> None:
    foreign_keys: dict[str, tuple[str, str | None]] = {}
    for table in Base.metadata.tables.values():
        for foreign_key in table.foreign_keys:
            constraint = foreign_key.constraint
            assert constraint is not None
            constraint_name = constraint.name
            assert isinstance(constraint_name, str)
            foreign_keys[constraint_name] = (foreign_key.target_fullname, foreign_key.ondelete)

    assert foreign_keys == {
        "doctor_unit_id_fkey": ("unit.unit_id", "SET NULL"),
        "exam_doctor_id_fkey": ("doctor.doctor_id", "SET NULL"),
        "exam_patient_id_fkey": ("patient.patient_id", "CASCADE"),
        "exam_unit_id_fkey": ("unit.unit_id", "SET NULL"),
    }


def test_timestamp_defaults_remain_timezone_naive_without_onupdate() -> None:
    timestamp_columns = [
        Patient.__table__.c.created_at,
        Patient.__table__.c.updated_at,
        Doctor.__table__.c.created_at,
        Doctor.__table__.c.updated_at,
        Unit.__table__.c.created_at,
        Unit.__table__.c.updated_at,
        Exam.__table__.c.exam_date,
        Exam.__table__.c.created_at,
        Exam.__table__.c.updated_at,
    ]

    for column in timestamp_columns:
        assert isinstance(column.type, DateTime)
        assert column.type.timezone is False
        assert column.server_default is not None
        assert str(column.server_default.arg) == "CURRENT_TIMESTAMP"
        assert column.onupdate is None

    assert str(Exam.__table__.c.status.server_default.arg) == "'pending'::character varying"


def test_relationships_are_bidirectional_and_respect_database_deletes() -> None:
    configure_mappers()

    assert Patient.exams.property.back_populates == "patient"
    assert Patient.exams.property.passive_deletes == "all"
    assert Exam.patient.property.back_populates == "exams"
    assert Doctor.exams.property.passive_deletes is True
    assert Unit.doctors.property.passive_deletes is True
    assert Unit.exams.property.passive_deletes is True
