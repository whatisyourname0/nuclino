"""HTTP-specific exceptions for Nuclino API."""

from typing import Any, Mapping, Optional

from .base import NuclinoBaseException


class NuclinoHTTPException(NuclinoBaseException):
    """Base exception for HTTP-related errors in the Nuclino API."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_data: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.response_data = dict(response_data or {})
        super().__init__(f"{status_code}: {message}")


class NuclinoAuthenticationError(NuclinoHTTPException):
    """Raised when authentication fails (HTTP 401)."""


class NuclinoPermissionError(NuclinoHTTPException):
    """Raised when the user lacks permission to access a resource (HTTP 403)."""


class NuclinoNotFoundError(NuclinoHTTPException):
    """Raised when a requested resource is not found (HTTP 404)."""


class NuclinoValidationError(NuclinoHTTPException):
    """Raised when the request is invalid (HTTP 400)."""


class NuclinoRateLimitError(NuclinoHTTPException):
    """Raised when API rate limiting is exceeded (HTTP 429)."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response_data: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(status_code, message, response_data)
        retry_after = self.response_data.get("retry_after")
        if retry_after is None:
            retry_after = self.response_data.get("retryAfter")
        if isinstance(retry_after, str) and retry_after.isdigit():
            retry_after = int(retry_after)
        self.retry_after = retry_after if isinstance(retry_after, int) else None


class NuclinoServerError(NuclinoHTTPException):
    """Raised when server-side errors occur (HTTP 5xx)."""


class NuclinoTimeoutError(NuclinoHTTPException):
    """Raised when the request times out."""


def raise_for_status_code(
    status_code: int,
    message: str,
    response_data: Optional[Mapping[str, Any]] = None,
) -> None:
    """Raise the appropriate exception based on the HTTP status code."""

    exception_map = {
        400: NuclinoValidationError,
        401: NuclinoAuthenticationError,
        403: NuclinoPermissionError,
        404: NuclinoNotFoundError,
        429: NuclinoRateLimitError,
    }

    if status_code in exception_map:
        raise exception_map[status_code](status_code, message, response_data)
    if 500 <= status_code < 600:
        raise NuclinoServerError(status_code, message, response_data)
    raise NuclinoHTTPException(status_code, message, response_data)
