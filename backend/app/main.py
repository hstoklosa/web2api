from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.main import router
from app.core.database import create_db_and_tables, engine
from app.core.exceptions import (
    NotFoundError,
    SchemaGenerationError,
    SchemaValidationError,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    try:
        yield
    finally:
        await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


@app.exception_handler(SchemaGenerationError)
async def schema_generation_error_handler(
    request: Request, exc: SchemaGenerationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"message": str(exc)},
    )


@app.exception_handler(SchemaValidationError)
async def schema_validation_error_handler(
    request: Request, exc: SchemaValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"message": str(exc)},
    )
