from typing import Any, Mapping, Optional


class NuclinoError(Exception):
    """Base exception class for all Nuclino client errors."""

    category = "unknown"


class NuclinoBaseException(NuclinoError):
    """Backward-compatible base class for Nuclino exceptions."""


class NuclinoClientValidationError(NuclinoBaseException):
    """Raised when SDK validation fails before making an API request."""

    category = "client_validation"

    def __init__(
        self,
        message: str,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.message = message
        self.details = dict(details or {})
        super().__init__(message)


class NuclinoTransportError(NuclinoBaseException):
    """Raised when a request fails before receiving an HTTP response."""

    category = "transport"

    def __init__(
        self,
        message: str,
        request_data: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.message = message
        self.request_data = dict(request_data or {})
        super().__init__(message)
