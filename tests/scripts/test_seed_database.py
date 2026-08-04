from collections.abc import Iterable
from datetime import datetime
from types import TracebackType
from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_hospital.core.config import Settings
from scripts import seed_database
from scripts.seed_database import (
    MAX_SEED_OBJECTS,
    SeedCounts,
    SeedData,
    build_seed_data,
    ensure_not_production,
    normalize_phone,
    persist_seed_data,
    run_seed,
    validate_counts,
)


def snapshot(seed: int) -> list[tuple[object, ...]]:
    data = build_seed_data(
        seed=seed,
        counts=SeedCounts(units=2, doctors=3, patients=4, exams=5),
    )
    return (
        [
            (patient.first_name, patient.last_name, patient.date_of_birth, patient.gender)
            for patient in data.patients
        ]
        + [
            (doctor.first_name, doctor.last_name, doctor.specialty, doctor.license_number)
            for doctor in data.doctors
        ]
        + [
            (exam.exam_date, exam.exam_type, exam.status, exam.notes, exam.result)
            for exam in data.exams
        ]
    )


def test_generation_is_deterministic_for_the_same_seed() -> None:
    assert snapshot(42) == snapshot(42)
    assert snapshot(42) != snapshot(43)


def test_generation_returns_requested_counts_and_total() -> None:
    data = build_seed_data(
        seed=42,
        counts=SeedCounts(units=3, doctors=5, patients=7, exams=11),
    )

    assert len(data.units) == 3
    assert len(data.doctors) == 5
    assert len(data.patients) == 7
    assert len(data.exams) == 11
    assert data.total == 26


def test_exam_relationships_are_consistent() -> None:
    data = build_seed_data(
        seed=42,
        counts=SeedCounts(units=2, doctors=4, patients=5, exams=12),
    )

    for exam in data.exams:
        assert exam.patient in data.patients
        assert exam.doctor in data.doctors
        assert exam.unit is exam.doctor.unit
        assert isinstance(exam.exam_date, datetime)
        assert exam.patient.date_of_birth is not None
        assert exam.exam_date.date() >= exam.patient.date_of_birth


def test_generated_values_fit_database_lengths() -> None:
    data = build_seed_data(
        seed=42,
        counts=SeedCounts(units=12, doctors=25, patients=30, exams=40),
    )

    assert len({unit.unit_code for unit in data.units}) == len(data.units)
    for unit in data.units:
        assert len(unit.unit_name) <= 100
        assert unit.unit_code is not None
        assert len(unit.unit_code) <= 20

    assert len({doctor.license_number for doctor in data.doctors}) == len(data.doctors)
    for doctor in data.doctors:
        assert len(doctor.first_name) <= 100
        assert len(doctor.last_name) <= 100
        assert doctor.specialty is not None
        assert len(doctor.specialty) <= 100
        assert doctor.license_number is not None
        assert len(doctor.license_number) <= 50
        assert doctor.phone is not None
        assert len(doctor.phone) <= 20
        assert doctor.email is not None
        assert len(doctor.email) <= 100

    assert len({patient.email for patient in data.patients}) == len(data.patients)
    for patient in data.patients:
        assert patient.first_name is not None
        assert len(patient.first_name) <= 100
        assert patient.last_name is not None
        assert len(patient.last_name) <= 100
        assert patient.phone is not None
        assert len(patient.phone) <= 20
        assert patient.email is not None
        assert len(patient.email) <= 100

    for exam in data.exams:
        assert exam.exam_type is not None
        assert len(exam.exam_type) <= 100
        assert exam.status is not None
        assert len(exam.status) <= 50


def test_zero_doctors_and_units_leave_exam_assignments_empty() -> None:
    data = build_seed_data(
        seed=42,
        counts=SeedCounts(units=0, doctors=0, patients=2, exams=3),
    )

    assert data.units == []
    assert data.doctors == []
    assert all(exam.patient in data.patients for exam in data.exams)
    assert all(exam.doctor is None for exam in data.exams)
    assert all(exam.unit is None for exam in data.exams)


def test_units_can_be_assigned_to_exams_without_doctors() -> None:
    data = build_seed_data(
        seed=42,
        counts=SeedCounts(units=2, doctors=0, patients=1, exams=4),
    )

    assert all(exam.doctor is None for exam in data.exams)
    assert all(exam.unit in data.units for exam in data.exams)


def test_zero_patients_is_valid_when_no_exams_are_requested() -> None:
    data = build_seed_data(
        seed=42,
        counts=SeedCounts(units=1, doctors=1, patients=0, exams=0),
    )

    assert data.patients == []
    assert data.exams == []


@pytest.mark.parametrize(
    "counts",
    [
        SeedCounts(units=-1),
        SeedCounts(doctors=-1),
        SeedCounts(patients=-1),
        SeedCounts(exams=-1),
    ],
)
def test_negative_counts_are_rejected(counts: SeedCounts) -> None:
    with pytest.raises(ValueError, match="must be nonnegative"):
        validate_counts(counts)


def test_exams_require_at_least_one_patient() -> None:
    with pytest.raises(ValueError, match="at least one patient"):
        validate_counts(SeedCounts(patients=0, exams=1))


def test_production_environment_is_rejected() -> None:
    with pytest.raises(ValueError, match="disabled in production"):
        ensure_not_production("production")

    ensure_not_production("development")
    ensure_not_production("test")
    ensure_not_production("staging")


def test_phone_normalization_removes_formatting_and_enforces_length() -> None:
    assert normalize_phone("+1 (555) 123-4567 ext. 890", 1) == "15551234567890"
    assert normalize_phone("not a phone", 12) == "5550000012"
    assert len(normalize_phone("1" * 30, 1)) == 20


def test_total_object_count_is_bounded() -> None:
    validate_counts(SeedCounts(units=0, doctors=0, patients=1, exams=MAX_SEED_OBJECTS - 1))

    with pytest.raises(ValueError, match=f"must not exceed {MAX_SEED_OBJECTS:,}"):
        validate_counts(SeedCounts(units=0, doctors=0, patients=1, exams=MAX_SEED_OBJECTS))


class FakeTransaction:
    def __init__(self, events: list[str]) -> None:
        self.events = events
        self.is_active = True

    async def commit(self) -> None:
        self.events.append("commit")
        self.is_active = False

    async def rollback(self) -> None:
        self.events.append("rollback")
        self.is_active = False


class FakeSession:
    def __init__(
        self,
        *,
        scalar_results: list[int | None],
        flush_error: Exception | None = None,
    ) -> None:
        self.events: list[str] = []
        self.scalar_results = scalar_results
        self.flush_error = flush_error
        self.transaction = FakeTransaction(self.events)
        self.added: list[object] = []

    async def begin(self) -> FakeTransaction:
        self.events.append("begin")
        return self.transaction

    async def execute(self, _statement: object) -> None:
        self.events.append("lock")

    async def scalar(self, _statement: object) -> int | None:
        self.events.append("check")
        return self.scalar_results.pop(0)

    def add_all(self, instances: Iterable[object]) -> None:
        self.events.append("add")
        self.added.extend(instances)

    async def flush(self) -> None:
        self.events.append("flush")
        if self.flush_error is not None:
            raise self.flush_error


class FakeSessionContext:
    def __init__(self, session: FakeSession) -> None:
        self.session = session

    async def __aenter__(self) -> AsyncSession:
        return cast(AsyncSession, self.session)

    async def __aexit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.session.events.append("exit")


class FakeSessionFactory:
    def __init__(self, session: FakeSession) -> None:
        self.session = session

    def __call__(self) -> FakeSessionContext:
        return FakeSessionContext(self.session)


def install_fake_session(
    monkeypatch: pytest.MonkeyPatch,
    *,
    scalar_results: list[int | None] | None = None,
    flush_error: Exception | None = None,
) -> FakeSession:
    session = FakeSession(
        scalar_results=scalar_results or [None, None, None, None],
        flush_error=flush_error,
    )
    factory = FakeSessionFactory(session)
    monkeypatch.setattr(seed_database, "get_session_factory", lambda: factory)
    return session


def empty_seed_data() -> SeedData:
    return SeedData(units=[], doctors=[], patients=[], exams=[])


async def test_persist_acquires_lock_checks_tables_then_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = install_fake_session(monkeypatch)

    await persist_seed_data(empty_seed_data(), dry_run=False)

    assert session.events == [
        "begin",
        "lock",
        "check",
        "check",
        "check",
        "check",
        "add",
        "flush",
        "commit",
        "exit",
    ]
    assert "rollback" not in session.events


async def test_persist_dry_run_rolls_back_without_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = install_fake_session(monkeypatch)

    await persist_seed_data(empty_seed_data(), dry_run=True)

    assert session.events[-3:] == ["flush", "rollback", "exit"]
    assert "commit" not in session.events


async def test_persist_rejects_nonempty_tables_and_rolls_back(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = install_fake_session(monkeypatch, scalar_results=[1, None, None, None])

    with pytest.raises(RuntimeError, match="refusing to seed non-empty tables: unit"):
        await persist_seed_data(empty_seed_data(), dry_run=False)

    assert session.events[:2] == ["begin", "lock"]
    assert session.events[-2:] == ["rollback", "exit"]
    assert "add" not in session.events
    assert "flush" not in session.events
    assert "commit" not in session.events


async def test_persist_flush_failure_rolls_back_without_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = install_fake_session(monkeypatch, flush_error=RuntimeError("flush failed"))

    with pytest.raises(RuntimeError, match="flush failed"):
        await persist_seed_data(empty_seed_data(), dry_run=False)

    assert session.events[-3:] == ["flush", "rollback", "exit"]
    assert "commit" not in session.events


async def test_run_seed_hides_password_and_delegates_persistence(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    persist_mock = AsyncMock()
    monkeypatch.setattr(seed_database, "persist_seed_data", persist_mock)
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://seed_user:top-secret@localhost/hospital",
        app_env="development",
    )
    counts = SeedCounts(units=0, doctors=0, patients=0, exams=0)

    await run_seed(settings=settings, seed=7, counts=counts, dry_run=True)

    output = capsys.readouterr().out
    assert "top-secret" not in output
    assert "***" in output
    assert "seed=7" in output
    persist_mock.assert_awaited_once()


async def test_run_seed_rejects_production_before_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    persist_mock = AsyncMock()
    monkeypatch.setattr(seed_database, "persist_seed_data", persist_mock)
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://seed_user:top-secret@localhost/hospital",
        app_env="production",
    )

    with pytest.raises(ValueError, match="disabled in production"):
        await run_seed(
            settings=settings,
            seed=7,
            counts=SeedCounts(units=0, doctors=0, patients=0, exams=0),
            dry_run=False,
        )

    persist_mock.assert_not_awaited()
