from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import router
from app.core.database import create_db_and_tables, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
