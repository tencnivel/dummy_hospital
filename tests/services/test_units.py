from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from dummy_hospital.models import Unit
from dummy_hospital.services import (
    NotFoundError,
    create_unit,
    delete_unit,
    get_unit,
    list_units,
    update_unit,
)


def make_session() -> tuple[AsyncSession, AsyncMock]:
    mock = AsyncMock(spec=AsyncSession)
    return cast(AsyncSession, mock), mock


async def test_create_unit_adds_typed_fields_and_flushes_without_commit() -> None:
    session, mock = make_session()

    unit = await create_unit(
        session,
        unit_name="Cardiology",
        unit_code="CARD",
        description="Cardiac care",
    )

    assert unit.unit_name == "Cardiology"
    assert unit.unit_code == "CARD"
    assert unit.description == "Cardiac care"
    mock.add.assert_called_once_with(unit)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_get_unit_returns_existing_unit() -> None:
    session, mock = make_session()
    unit = Unit(unit_name="Cardiology")
    mock.get.return_value = unit

    assert await get_unit(session, 7) is unit
    mock.get.assert_awaited_once_with(Unit, 7)
    mock.commit.assert_not_awaited()


async def test_get_unit_raises_not_found() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError, match="Unit with id 404 not found"):
        await get_unit(session, 404)


async def test_list_units_orders_and_paginates() -> None:
    session, mock = make_session()
    units = [Unit(unit_name="Cardiology")]
    mock.scalars.return_value = units

    assert await list_units(session) == units
    statement = cast(Select[tuple[Unit]], mock.scalars.await_args.args[0])
    dialect = postgresql.dialect()  # type: ignore[no-untyped-call]
    sql = str(statement.compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
    assert "ORDER BY unit.unit_id" in sql
    assert "LIMIT 50 OFFSET 0" in sql
    mock.commit.assert_not_awaited()


@pytest.mark.parametrize(("limit", "offset"), [(0, 0), (101, 0), (10, -1)])
async def test_list_units_validates_before_querying(limit: int, offset: int) -> None:
    session, mock = make_session()

    with pytest.raises(ValueError):
        await list_units(session, limit=limit, offset=offset)

    mock.scalars.assert_not_awaited()


async def test_update_unit_keeps_omitted_and_clears_nullable_fields() -> None:
    session, mock = make_session()
    unit = Unit(unit_name="Cardiology", unit_code="CARD", description="Cardiac care")
    mock.get.return_value = unit

    result = await update_unit(session, 7, description=None)

    assert result is unit
    assert unit.unit_name == "Cardiology"
    assert unit.unit_code == "CARD"
    assert unit.description is None
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_update_unit_not_found_does_not_flush() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError):
        await update_unit(session, 404, unit_name="Missing")

    mock.flush.assert_not_awaited()


async def test_delete_unit_deletes_and_flushes_without_commit() -> None:
    session, mock = make_session()
    unit = Unit(unit_name="Cardiology")
    mock.get.return_value = unit

    assert await delete_unit(session, 7) is unit
    mock.delete.assert_awaited_once_with(unit)
    mock.flush.assert_awaited_once_with()
    mock.commit.assert_not_awaited()
    mock.rollback.assert_not_awaited()


async def test_delete_unit_not_found_does_not_delete() -> None:
    session, mock = make_session()
    mock.get.return_value = None

    with pytest.raises(NotFoundError):
        await delete_unit(session, 404)

    mock.delete.assert_not_awaited()
    mock.flush.assert_not_awaited()
