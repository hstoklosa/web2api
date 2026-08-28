from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    NotFoundError,
    SchemaGenerationError,
    SchemaValidationError,
)


async def not_found_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


async def schema_generation_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"message": str(exc)},
    )


async def schema_validation_error_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"message": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register domain error handlers on the FastAPI app."""
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(SchemaGenerationError, schema_generation_error_handler)
    app.add_exception_handler(SchemaValidationError, schema_validation_error_handler)
