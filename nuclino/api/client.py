from time import sleep
from typing import Any, Dict, Mapping, Optional, Union, cast

import requests
from ratelimit import limits

from nuclino.api.exceptions import (
    NuclinoResponseFormatError,
    NuclinoTimeoutError,
    NuclinoTransportError,
    raise_for_status_code,
)
from nuclino.api.utils import sleep_and_retry
from nuclino.models.shared import NuclinoList, NuclinoObject, get_loader

BASE_URL = 'https://api.nuclino.com/v0'
DEFAULT_REQUEST_TIMEOUT = 10.0
DEFAULT_REQUESTS_PER_MINUTE = 150

ResponseData = Union[NuclinoList[Any], NuclinoObject, Dict[str, Any]]


def join_url(base_url: str, path: str) -> str:
    """
    Join base URL with path, ensuring proper formatting.

    Args:
        base_url: The base URL (e.g., 'https://api.nuclino.com/v0')
        path: The path to append (e.g., '/workspaces')

    Returns:
        The properly joined URL
    """
    return '/'.join(part.strip('/') for part in [base_url, path])


class Client:
    """
    Base class for Nuclino API client. Handles authentication, rate limiting, and HTTP requests.
    Can be used as a context manager to automatically handle session cleanup.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        max_rate_limit_retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        """
        Initialize a new Nuclino API client.

        Args:
            api_key: Your Nuclino API key for authentication
            base_url: Base URL for API requests. Defaults to 'https://api.nuclino.com/v0'
            requests_per_minute: Maximum number of requests allowed per minute.
            request_timeout: Request timeout in seconds.
            max_rate_limit_retries: Number of times to retry HTTP 429 responses.
            session: Optional pre-configured requests session to use.

        Raises:
            ValueError: If api_key is empty, requests_per_minute is less than 1,
                        or max_rate_limit_retries is negative
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        if requests_per_minute < 1:
            raise ValueError("requests_per_minute must be at least 1")
        if request_timeout <= 0:
            raise ValueError("request_timeout must be greater than 0")
        if max_rate_limit_retries < 0:
            raise ValueError("max_rate_limit_retries cannot be negative")

        self.check_limit = sleep_and_retry()(
            limits(requests_per_minute, period=60)(lambda: None)
        )
        self._owns_session = session is None
        self.session: requests.Session = session if session is not None else requests.Session()
        self.session.headers['Authorization'] = api_key
        self.base_url: str = base_url
        self.request_timeout: float = request_timeout
        self.max_rate_limit_retries: int = max_rate_limit_retries

    def __enter__(self) -> 'Client':
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Exit the context manager and clean up resources."""
        self.close()

    def close(self) -> None:
        """Close the session and clean up resources."""
        if self._owns_session:
            self.session.close()

    def _extract_retry_after(self, response: requests.Response) -> Optional[int]:
        """Extract retry delay from standard headers or Nuclino error payloads."""
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return max(0, int(float(retry_after)))
            except ValueError:
                pass

        try:
            content = response.json()
        except ValueError:
            return None

        if not isinstance(content, Mapping):
            return None

        value = content.get("retry_after")
        if value is None:
            value = content.get("retryAfter")
        if value is None:
            return None

        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return None

    def _handle_response(self, response: requests.Response) -> ResponseData:
        """
        Process an API response, handling errors and parsing the response data.

        Args:
            response: The response object from the API request

        Returns:
            The parsed response data.
        """
        if not 200 <= response.status_code < 300:
            try:
                raw_content = response.json()
            except ValueError:
                raise_for_status_code(
                    response.status_code,
                    response.reason or "Request failed",
                    {"raw_content": response.text},
                )

            if not isinstance(raw_content, Mapping):
                raise_for_status_code(
                    response.status_code,
                    response.reason or "Request failed",
                    {"raw_content": response.text},
                )

            content = dict(raw_content)
            message = content.get('message', 'Unknown error')
            if response.status_code == 429 and 'retry_after' not in content:
                retry_after = self._extract_retry_after(response)
                if retry_after is not None:
                    content = {**content, 'retry_after': retry_after}
            raise_for_status_code(response.status_code, message, content)

        if response.status_code == 204 or not response.content:
            return {}

        try:
            raw_content = response.json()
        except ValueError:
            raise_for_status_code(
                response.status_code,
                "Invalid JSON response from API",
                {"raw_content": response.text},
            )

        if not isinstance(raw_content, Mapping):
            raise NuclinoResponseFormatError(
                response.status_code,
                "Invalid JSON response from API",
                {"raw_content": response.text},
            )

        content = dict(raw_content)
        if content.get("status") != "success":
            raise NuclinoResponseFormatError(
                response.status_code,
                "Invalid API response status",
                content,
            )
        if 'data' not in content:
            raise NuclinoResponseFormatError(
                response.status_code,
                "Invalid API response: missing data",
                content,
            )

        data = content['data']
        if not isinstance(data, Mapping):
            raise NuclinoResponseFormatError(
                response.status_code,
                "Invalid JSON response from API",
                content,
            )

        return self.parse(data)

    def parse(self, source: Mapping[str, Any]) -> ResponseData:
        """
        Parse API response data into appropriate Nuclino objects.

        Args:
            source: The raw response data dictionary from the API

        Returns:
            The parsed data.
        """
        if 'object' not in source:
            return dict(source)

        func = get_loader(source['object'])
        result = func(source, cast(Any, self))

        if isinstance(result, NuclinoObject):
            return result
        if isinstance(result, NuclinoList):
            return NuclinoList(
                [
                    self.parse(item) if isinstance(item, Mapping) else item
                    for item in result
                ],
                metadata=result.metadata,
            )
        if isinstance(result, list):
            return NuclinoList(
                [
                    self.parse(item) if isinstance(item, Mapping) else item
                    for item in result
                ],
            )
        return dict(result)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> ResponseData:
        attempts = 0
        url = join_url(self.base_url, path)

        while True:
            self.check_limit()
            try:
                response = self.session.request(
                    method,
                    url,
                    params=params or None,
                    json=data,
                    timeout=self.request_timeout,
                )
            except requests.Timeout as exc:
                raise NuclinoTimeoutError(
                    "Request timed out",
                    {"method": method, "path": path},
                ) from exc
            except requests.RequestException as exc:
                raise NuclinoTransportError(
                    str(exc),
                    {"method": method, "path": path},
                ) from exc

            if response.status_code == 429 and attempts < self.max_rate_limit_retries:
                attempts += 1
                retry_after = self._extract_retry_after(response)
                sleep(retry_after if retry_after is not None else 1)
                continue

            return self._handle_response(response)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> ResponseData:
        """Make a GET request to the API."""
        return self._request("GET", path, params=params)

    def delete(self, path: str) -> ResponseData:
        """Make a DELETE request to the API."""
        return self._request("DELETE", path)

    def post(self, path: str, data: Dict[str, Any]) -> ResponseData:
        """Make a POST request to the API."""
        return self._request("POST", path, data=data)

    def put(self, path: str, data: Dict[str, Any]) -> ResponseData:
        """Make a PUT request to the API."""
        return self._request("PUT", path, data=data)
