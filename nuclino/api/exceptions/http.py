"""HTTP-specific exceptions for Nuclino API."""

from typing import Optional

from .base import NuclinoBaseException


class NuclinoHTTPException(NuclinoBaseException):
    """Base exception for HTTP-related errors."""
    def __init__(self, status_code: int, message: str, response_data: Optional[dict] = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data or {}
        super().__init__(f"{status_code}: {message}")


class NuclinoAuthenticationError(NuclinoHTTPException):
    """Raised when authentication fails (401 errors)."""
    pass


class NuclinoPermissionError(NuclinoHTTPException):
    """Raised when the user doesn't have permission to access a resource (403 errors)."""
    pass


class NuclinoNotFoundError(NuclinoHTTPException):
    """Raised when a requested resource is not found (404 errors)."""
    pass


class NuclinoValidationError(NuclinoHTTPException):
    """Raised when the request is invalid (400 errors)."""
    pass


class NuclinoRateLimitError(NuclinoHTTPException):
    """Raised when API rate limit is exceeded (429 errors)."""
    def __init__(self, status_code: int, message: str, response_data: Optional[dict] = None):
        super().__init__(status_code, message, response_data)
        self.retry_after = response_data.get('retry_after') if response_data else None


class NuclinoServerError(NuclinoHTTPException):
    """Raised when server-side errors occur (5xx errors)."""
    pass


class NuclinoTimeoutError(NuclinoHTTPException):
    """Raised when the request times out."""
    pass


def raise_for_status_code(status_code: int, message: str, response_data: Optional[dict] = None) -> None:
    """
    Raise the appropriate exception based on the HTTP status code.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response_data: Optional response data from the API
    
    Raises:
        NuclinoHTTPException: Or one of its subclasses based on the status code
    """
    exception_map = {
        400: NuclinoValidationError,
        401: NuclinoAuthenticationError,
        403: NuclinoPermissionError,
        404: NuclinoNotFoundError,
        429: NuclinoRateLimitError,
    }
    
    if status_code in exception_map:
        raise exception_map[status_code](status_code, message, response_data)
    elif 500 <= status_code < 600:
        raise NuclinoServerError(status_code, message, response_data)
    else:
        raise NuclinoHTTPException(status_code, message, response_data) 