from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dummy_hospital import __version__
from dummy_hospital.api.health import router as health_router
from dummy_hospital.api.v1.router import router as api_v1_router
from dummy_hospital.db.session import dispose_engine


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await dispose_engine()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Dummy Hospital API",
        version=__version__,
        lifespan=lifespan,
    )
    application.include_router(health_router)
    application.include_router(api_v1_router, prefix="/api/v1")
    return application


app = create_app()
