from typing import Any, Optional, Dict


class AppException(Exception):
    """Base application exception for domain and business logic errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details


class NotFoundException(AppException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class BadRequestException(AppException):
    """Raised when request payload or parameters are invalid."""

    def __init__(self, message: str = "Bad request payload.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="BAD_REQUEST",
            status_code=400,
            details=details,
        )


class UnauthorizedException(AppException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Authentication required.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenException(AppException):
    """Raised when authenticated user lacks permission for action."""

    def __init__(self, message: str = "Access forbidden.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class ConflictException(AppException):
    """Raised when action conflicts with existing resource state."""

    def __init__(self, message: str = "Resource conflict.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class ValidationException(AppException):
    """Raised when business validation rules fail."""

    def __init__(self, message: str = "Validation error.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class ServiceUnavailableException(AppException):
    """Raised when dependent external service or DB is unavailable."""

    def __init__(self, message: str = "Service temporarily unavailable.", details: Optional[Any] = None) -> None:
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=533,
            details=details,
        )
