"""HTTP-specific exceptions for Nuclino API.

This module contains all HTTP-related exceptions that can be raised by the Nuclino API client.
Each exception corresponds to a specific HTTP status code or error condition.
"""

from typing import Optional

from .base import NuclinoBaseException


class NuclinoHTTPException(NuclinoBaseException):
    """
    Base exception for HTTP-related errors in the Nuclino API.

    Attributes:
        status_code (int): The HTTP status code that triggered this exception
        message (str): A human-readable error message
        response_data (dict): The raw response data from the API, if available

    Example:
        >>> try:
        ...     client.get_workspace("123")
        ... except NuclinoHTTPException as e:
        ...     print(f"HTTP {e.status_code}: {e.message}")
        ...     print("Response data:", e.response_data)
    """
    def __init__(self, status_code: int, message: str, response_data: Optional[dict] = None):
        self.status_code = status_code
        self.message = message
        self.response_data = response_data or {}
        super().__init__(f"{status_code}: {message}")


class NuclinoAuthenticationError(NuclinoHTTPException):
    """
    Raised when authentication fails (HTTP 401).
    
    This typically occurs when:
    - The API key is invalid or expired
    - The API key is missing
    - The API key has been revoked
    
    Example:
        >>> try:
        ...     client.get_workspace("123")
        ... except NuclinoAuthenticationError as e:
        ...     print("Authentication failed. Please check your API key.")
    """
    pass


class NuclinoPermissionError(NuclinoHTTPException):
    """
    Raised when the user doesn't have permission to access a resource (HTTP 403).
    
    This typically occurs when:
    - The user doesn't have access to the requested workspace/team
    - The user's role doesn't allow the requested operation
    - The resource is private or restricted
    
    Example:
        >>> try:
        ...     client.get_workspace("123")
        ... except NuclinoPermissionError as e:
        ...     print("You don't have permission to access this workspace.")
    """
    pass


class NuclinoNotFoundError(NuclinoHTTPException):
    """
    Raised when a requested resource is not found (HTTP 404).
    
    This typically occurs when:
    - The resource ID is invalid
    - The resource has been deleted
    - The resource exists but is not accessible to the user
    
    Example:
        >>> try:
        ...     client.get_item("non-existent-id")
        ... except NuclinoNotFoundError as e:
        ...     print("The requested item could not be found.")
    """
    pass


class NuclinoValidationError(NuclinoHTTPException):
    """
    Raised when the request is invalid (HTTP 400).
    
    This typically occurs when:
    - Required fields are missing
    - Field values are invalid
    - Request parameters are malformed
    
    Example:
        >>> try:
        ...     client.create_item(workspace_id="123", title="")
        ... except NuclinoValidationError as e:
        ...     print("Invalid request:", e.message)
        ...     print("Fields:", e.response_data.get('fields', {}))
    """
    pass


class NuclinoRateLimitError(NuclinoHTTPException):
    """
    Raised when API rate limit is exceeded (HTTP 429).
    
    Attributes:
        retry_after (Optional[int]): Number of seconds to wait before retrying
    
    This typically occurs when:
    - Too many requests are made within a short time period
    - The API quota has been exceeded
    
    Example:
        >>> try:
        ...     client.get_workspace("123")
        ... except NuclinoRateLimitError as e:
        ...     if e.retry_after:
        ...         print(f"Rate limit exceeded. Try again in {e.retry_after} seconds")
        ...     else:
        ...         print("Rate limit exceeded. Please wait before retrying.")
    """
    def __init__(self, status_code: int, message: str, response_data: Optional[dict] = None):
        super().__init__(status_code, message, response_data)
        self.retry_after = response_data.get('retry_after') if response_data else None


class NuclinoServerError(NuclinoHTTPException):
    """
    Raised when server-side errors occur (HTTP 5xx).
    
    This typically occurs when:
    - The Nuclino API is experiencing internal issues
    - There are temporary service disruptions
    - The API is undergoing maintenance
    
    Example:
        >>> try:
        ...     client.get_workspace("123")
        ... except NuclinoServerError as e:
        ...     print("Nuclino is experiencing technical difficulties.")
        ...     print("Please try again later.")
    """
    pass


class NuclinoTimeoutError(NuclinoHTTPException):
    """
    Raised when the request times out.
    
    This typically occurs when:
    - The network connection is slow or unstable
    - The server is taking too long to respond
    - There are connectivity issues
    
    Example:
        >>> try:
        ...     client.get_workspace("123")
        ... except NuclinoTimeoutError as e:
        ...     print("Request timed out. Please check your connection.")
    """
    pass


def raise_for_status_code(status_code: int, message: str, response_data: Optional[dict] = None) -> None:
    """
    Raise the appropriate exception based on the HTTP status code.
    
    This function maps HTTP status codes to their corresponding exception classes
    and raises the appropriate exception with the provided message and response data.
    
    Args:
        status_code: HTTP status code from the API response
        message: Error message to include in the exception
        response_data: Optional dictionary containing the full API response data
    
    Raises:
        NuclinoValidationError: For 400 Bad Request
        NuclinoAuthenticationError: For 401 Unauthorized
        NuclinoPermissionError: For 403 Forbidden
        NuclinoNotFoundError: For 404 Not Found
        NuclinoRateLimitError: For 429 Too Many Requests
        NuclinoServerError: For 5xx Server Errors
        NuclinoHTTPException: For all other HTTP errors
    
    Example:
        >>> try:
        ...     raise_for_status_code(404, "Workspace not found", {"id": "123"})
        ... except NuclinoNotFoundError as e:
        ...     print(f"Error {e.status_code}: {e.message}")
        ...     print("Response data:", e.response_data)
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