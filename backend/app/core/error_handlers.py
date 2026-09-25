from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
        headers=exc.headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register domain error handlers on the FastAPI app."""
    app.add_exception_handler(AppError, app_error_handler)
