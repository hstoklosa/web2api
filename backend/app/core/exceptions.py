class AppError(Exception):
    """Base for domain errors caught by API handlers."""


class NotFoundError(AppError):
    pass


class SchemaGenerationError(AppError):
    pass


class SchemaValidationError(AppError):
    pass
