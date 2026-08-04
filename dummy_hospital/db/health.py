from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_database_ready(session: AsyncSession) -> None:
    """Raise if PostgreSQL cannot execute a minimal query."""
    await session.execute(text("SELECT 1"))
