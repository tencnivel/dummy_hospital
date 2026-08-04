from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from dummy_hospital.models import GenderType, Patient
from dummy_hospital.services import create_patient


class IntegrationTestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    test_database_url: str | None = Field(default=None, validation_alias="TEST_DATABASE_URL")


def require_test_database_url() -> str:
    test_database_url = IntegrationTestSettings().test_database_url
    if test_database_url is None:
        pytest.skip("TEST_DATABASE_URL is not configured")

    return test_database_url


@pytest_asyncio.fixture
async def database_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(require_test_database_url())

    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            session = AsyncSession(bind=connection, expire_on_commit=False)
            try:
                yield session
            finally:
                await session.close()
                await transaction.rollback()
    finally:
        await engine.dispose()


@pytest.mark.integration
async def test_create_patient_persists_patient_until_transaction_rollback(
    database_session: AsyncSession,
) -> None:
    patient = await create_patient(
        database_session,
        first_name="Integration",
        last_name="Patient",
        gender=GenderType.UNKNOWN,
        email="integration.patient@example.test",
    )

    assert patient.patient_id is not None

    row = (
        await database_session.execute(
            select(
                Patient.first_name,
                Patient.last_name,
                Patient.gender,
                Patient.email,
            ).where(Patient.patient_id == patient.patient_id)
        )
    ).one()
    assert row == (
        "Integration",
        "Patient",
        GenderType.UNKNOWN,
        "integration.patient@example.test",
    )
