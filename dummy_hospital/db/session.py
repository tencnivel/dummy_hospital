from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dummy_hospital.core.config import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    """Create the engine on first use rather than during module import."""
    return create_async_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session


async def dispose_engine() -> None:
    """Dispose initialized connection pools during application shutdown."""
    if get_engine.cache_info().currsize == 0:
        return

    engine = get_engine()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
    await engine.dispose()
