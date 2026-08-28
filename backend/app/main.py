from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import router
from app.core.database import create_db_and_tables, engine
from app.core.error_handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
register_exception_handlers(app)
