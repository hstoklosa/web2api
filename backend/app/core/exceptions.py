from fastapi import status


class AppError(Exception):
    """Base for domain errors caught by API handlers.

    The message becomes the response's `detail`, which the frontend shows as
    is, so it must make sense to an end user.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers: dict[str, str] | None = None


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}


class SchemaGenerationError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY


class SchemaGenerationBusyError(SchemaGenerationError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class SchemaGenerationTimeoutError(SchemaGenerationError):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT


class SchemaValidationError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY


class BlockedURLError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT


class FetchError(AppError):
    status_code = status.HTTP_502_BAD_GATEWAY


class FetchTimeoutError(FetchError):
    status_code = status.HTTP_504_GATEWAY_TIMEOUT
