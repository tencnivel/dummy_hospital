from __future__ import annotations

import argparse
import asyncio
import re
from dataclasses import dataclass
from datetime import date, datetime, time

from faker import Faker
from sqlalchemy import func, select
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.core.config import Settings, get_settings
from dummy_hospital.db.session import dispose_engine, get_session_factory
from dummy_hospital.models import Doctor, Exam, GenderType, Patient, Unit

SPECIALTIES = (
    "Cardiology",
    "Dermatology",
    "Emergency Medicine",
    "Family Medicine",
    "Neurology",
    "Oncology",
    "Pediatrics",
    "Radiology",
)
EXAM_TYPES = (
    "Blood test",
    "CT scan",
    "MRI",
    "Physical examination",
    "Ultrasound",
    "X-ray",
)
EXAM_STATUSES = ("pending", "completed", "cancelled")
UNIT_NAMES = (
    "Cardiology",
    "Emergency",
    "Intensive Care",
    "Neurology",
    "Oncology",
    "Pediatrics",
    "Radiology",
    "Surgery",
)
MAX_SEED_OBJECTS = 100_000
EXAM_DATE_START = datetime(2024, 1, 1)
EXAM_DATE_END = datetime(2025, 12, 31, 23, 59, 59)
# Stable signed-bigint namespace used only to serialize this seeder's transactions.
SEED_ADVISORY_LOCK_ID = 4_922_997_578_575_740_755


@dataclass(frozen=True)
class SeedCounts:
    units: int = 8
    doctors: int = 20
    patients: int = 100
    exams: int = 200


@dataclass
class SeedData:
    units: list[Unit]
    doctors: list[Doctor]
    patients: list[Patient]
    exams: list[Exam]

    @property
    def total(self) -> int:
        return len(self.units) + len(self.doctors) + len(self.patients) + len(self.exams)


def validate_counts(counts: SeedCounts) -> None:
    for name, count in (
        ("units", counts.units),
        ("doctors", counts.doctors),
        ("patients", counts.patients),
        ("exams", counts.exams),
    ):
        if count < 0:
            raise ValueError(f"{name} must be nonnegative")
    if counts.exams > 0 and counts.patients == 0:
        raise ValueError("at least one patient is required when exams is greater than zero")
    if sum((counts.units, counts.doctors, counts.patients, counts.exams)) > MAX_SEED_OBJECTS:
        raise ValueError(f"total generated objects must not exceed {MAX_SEED_OBJECTS:,}")


def ensure_not_production(app_env: str) -> None:
    if app_env == "production":
        raise ValueError("database seeding is disabled in production")


def normalize_phone(raw_phone: str, fallback_index: int) -> str:
    digits = re.sub(r"\D", "", raw_phone)
    return (digits or f"555{fallback_index:07d}")[:20]


def build_unit_name(index: int) -> str:
    if index < len(UNIT_NAMES):
        return UNIT_NAMES[index]
    return f"Clinical Unit {index + 1}"


def build_email(first_name: str, last_name: str, category: str, index: int) -> str:
    local_part = re.sub(
        r"[^a-z0-9]+",
        ".",
        f"{first_name}.{last_name}".lower(),
    ).strip(".")
    local_part = local_part or category
    suffix = f".{category}{index + 1}@example.test"
    return f"{local_part[: 100 - len(suffix)]}{suffix}"


def build_seed_data(*, seed: int, counts: SeedCounts) -> SeedData:
    validate_counts(counts)
    fake = Faker()
    fake.seed_instance(seed)

    units = [
        Unit(
            unit_name=build_unit_name(index),
            unit_code=f"UNIT-{index + 1:03d}",
            description=fake.sentence(nb_words=8),
        )
        for index in range(counts.units)
    ]

    doctors: list[Doctor] = []
    for index in range(counts.doctors):
        first_name = fake.first_name()[:100]
        last_name = fake.last_name()[:100]
        doctor = Doctor(
            first_name=first_name,
            last_name=last_name,
            specialty=fake.random_element(elements=SPECIALTIES)[:100],
            license_number=f"MED-{index + 1:08d}",
            phone=normalize_phone(fake.phone_number(), index),
            email=build_email(first_name, last_name, "doctor", index),
            unit=units[index % len(units)] if units else None,
        )
        doctors.append(doctor)

    patients: list[Patient] = []
    for index in range(counts.patients):
        first_name = fake.first_name()[:100]
        last_name = fake.last_name()[:100]
        patient = Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=fake.date_between(
                start_date=date(1925, 1, 1),
                end_date=date(2025, 12, 31),
            ),
            gender=fake.random_element(elements=tuple(GenderType)),
            phone=normalize_phone(fake.phone_number(), counts.doctors + index),
            email=build_email(first_name, last_name, "patient", index),
            address=fake.address().replace("\n", ", "),
        )
        patients.append(patient)

    exams: list[Exam] = []
    for index in range(counts.exams):
        assigned_patient = patients[index % len(patients)]
        assigned_doctor: Doctor | None = doctors[index % len(doctors)] if doctors else None
        assigned_unit = (
            assigned_doctor.unit
            if assigned_doctor is not None
            else (units[index % len(units)] if units else None)
        )
        status = fake.random_element(elements=EXAM_STATUSES)
        if assigned_patient.date_of_birth is None:
            raise RuntimeError("generated patient is missing a date of birth")
        exam_date_start = max(
            EXAM_DATE_START,
            datetime.combine(assigned_patient.date_of_birth, time.min),
        )
        exam = Exam(
            patient=assigned_patient,
            doctor=assigned_doctor,
            unit=assigned_unit,
            exam_date=fake.date_time_between(
                start_date=exam_date_start,
                end_date=EXAM_DATE_END,
            ),
            exam_type=fake.random_element(elements=EXAM_TYPES)[:100],
            status=status[:50],
            notes=fake.sentence(nb_words=10),
            result=(fake.sentence(nb_words=8) if status == "completed" else None),
        )
        exams.append(exam)

    return SeedData(units=units, doctors=doctors, patients=patients, exams=exams)


async def find_populated_tables(session: AsyncSession) -> list[str]:
    populated: list[str] = []
    for table_name, model, primary_key in (
        ("unit", Unit, Unit.unit_id),
        ("doctor", Doctor, Doctor.doctor_id),
        ("patient", Patient, Patient.patient_id),
        ("exam", Exam, Exam.exam_id),
    ):
        if await session.scalar(select(primary_key).select_from(model).limit(1)) is not None:
            populated.append(table_name)
    return populated


async def acquire_seed_lock(session: AsyncSession) -> None:
    """Serialize this script's check-and-insert sequence for the transaction."""
    await session.execute(select(func.pg_advisory_xact_lock(SEED_ADVISORY_LOCK_ID)))


async def persist_seed_data(data: SeedData, *, dry_run: bool) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        transaction = await session.begin()
        try:
            await acquire_seed_lock(session)
            populated_tables = await find_populated_tables(session)
            if populated_tables:
                joined_names = ", ".join(populated_tables)
                raise RuntimeError(f"refusing to seed non-empty tables: {joined_names}")

            session.add_all([*data.units, *data.doctors, *data.patients, *data.exams])
            await session.flush()
            if dry_run:
                await transaction.rollback()
            else:
                await transaction.commit()
        except BaseException:
            if transaction.is_active:
                await transaction.rollback()
            raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Populate the database with deterministic dummy data."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--units", type=int, default=8)
    parser.add_argument("--doctors", type=int, default=20)
    parser.add_argument("--patients", type=int, default=100)
    parser.add_argument("--exams", type=int, default=200)
    parser.add_argument("--dry-run", action="store_true")
    return parser


async def run_seed(*, settings: Settings, seed: int, counts: SeedCounts, dry_run: bool) -> None:
    ensure_not_production(settings.app_env)
    validate_counts(counts)
    target = make_url(settings.database_url).render_as_string(hide_password=True)
    mode = "dry run" if dry_run else "commit"
    print(
        f"Target: {target} | seed={seed} | units={counts.units}, doctors={counts.doctors}, "
        f"patients={counts.patients}, exams={counts.exams} | mode={mode}"
    )

    data = build_seed_data(seed=seed, counts=counts)
    await persist_seed_data(data, dry_run=dry_run)
    action = "validated and rolled back" if dry_run else "committed"
    print(f"Seed data {action}: {data.total} ORM objects")


async def async_main(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    counts = SeedCounts(
        units=args.units,
        doctors=args.doctors,
        patients=args.patients,
        exams=args.exams,
    )
    try:
        validate_counts(counts)
        ensure_not_production(get_settings().app_env)
    except ValueError as exc:
        parser.error(str(exc))

    try:
        await run_seed(
            settings=get_settings(),
            seed=args.seed,
            counts=counts,
            dry_run=args.dry_run,
        )
    finally:
        await dispose_engine()


def main() -> None:
    parser = build_parser()
    asyncio.run(async_main(parser.parse_args(), parser))


if __name__ == "__main__":
    main()
