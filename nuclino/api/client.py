from typing import Any, Dict, List, Optional, Union

import requests
from ratelimit import limits

from nuclino.api.exceptions import (
    raise_for_status_code,
)
from nuclino.api.utils import sleep_and_retry
from nuclino.models.shared import NuclinoObject, get_loader

BASE_URL = 'https://api.nuclino.com/v0'

ResponseData = Union[List[NuclinoObject], NuclinoObject, Dict[str, Any]]

def join_url(base_url: str, path: str) -> str:
    """
    Join base URL with path, ensuring proper formatting.
    
    Args:
        base_url: The base URL (e.g., 'https://api.nuclino.com/v0')
        path: The path to append (e.g., '/workspaces')
    
    Returns:
        str: The properly joined URL
    
    Example:
        >>> join_url('https://api.nuclino.com/v0', '/workspaces')
        'https://api.nuclino.com/v0/workspaces'
        >>> join_url('https://api.nuclino.com/v0/', '/workspaces/')
        'https://api.nuclino.com/v0/workspaces'
    """
    return '/'.join(part.strip('/') for part in [base_url, path])


class Client:
    '''
    Base class for Nuclino API client. Handles authentication, rate limiting, and HTTP requests.
    Can be used as a context manager to automatically handle session cleanup.

    Attributes:
        session (requests.Session): The HTTP session used for making requests
        base_url (str): The base URL for all API requests
        check_limit (Callable): Rate limiting function

    Example:
        >>> client = Client(api_key="your-api-key")
        >>> workspace = client.get("/workspaces/123")
        >>> print(workspace["name"])
        
        # Using as context manager
        >>> with Client(api_key="your-api-key") as client:
        ...     workspace = client.get("/workspaces/123")
    '''

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        requests_per_minute: int = 140
    ) -> None:
        '''
        Initialize a new Nuclino API client.

        Args:
            api_key: Your Nuclino API key for authentication
            base_url: Base URL for API requests. Defaults to 'https://api.nuclino.com/v0'
            requests_per_minute: Maximum number of requests allowed per minute. 
                               If exceeded, the client will wait before making more requests.
                               Defaults to 140.

        Raises:
            ValueError: If api_key is empty or requests_per_minute is less than 1
        '''
        if not api_key:
            raise ValueError("API key cannot be empty")
        if requests_per_minute < 1:
            raise ValueError("requests_per_minute must be at least 1")

        self.check_limit = sleep_and_retry()(
            limits(requests_per_minute, period=60)(lambda: None)
        )
        self.session = requests.Session()
        self.session.headers['Authorization'] = api_key
        self.timer = None
        self.base_url = base_url

    def __enter__(self) -> 'Client':
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Exit the context manager and clean up resources."""
        self.close()

    def close(self) -> None:
        """Close the session and clean up resources."""
        self.session.close()

    def _handle_response(
        self,
        response: requests.models.Response
    ) -> ResponseData:
        '''
        Process an API response, handling errors and parsing the response data.

        Args:
            response: The response object from the API request

        Returns:
            Union[List[NuclinoObject], NuclinoObject, dict]: The parsed response data.
            - For single objects: A NuclinoObject instance
            - For lists: A list of NuclinoObject instances
            - For other data: A dictionary

        Raises:
            NuclinoAuthenticationError: When authentication fails (401)
            NuclinoPermissionError: When permission is denied (403)
            NuclinoRateLimitError: When rate limit is exceeded (429)
            NuclinoServerError: When server errors occur (5xx)
            NuclinoHTTPException: For other HTTP errors
            ValueError: When response JSON is invalid or missing required fields
        '''
        try:
            content = response.json()
        except ValueError:
            raise_for_status_code(
                response.status_code,
                "Invalid JSON response from API",
                {"raw_content": response.text}
            )

        if response.status_code != 200:
            message = content.get('message', 'Unknown error')
            raise_for_status_code(response.status_code, message, content)
        
        if 'data' not in content:
            raise_for_status_code(
                500,
                "API response missing 'data' field",
                content
            )
            
        return self.parse(content['data'])

    def parse(self, source: Dict[str, Any]) -> ResponseData:
        '''
        Parse API response data into appropriate Nuclino objects.

        Args:
            source: The raw response data dictionary from the API

        Returns:
            Union[List[NuclinoObject], NuclinoObject, dict]: The parsed data
            - For single objects: A NuclinoObject instance
            - For lists: A list of NuclinoObject instances
            - For other data: The original dictionary

        Example:
            >>> data = {"object": "workspace", "id": "123", "name": "My Workspace"}
            >>> result = client.parse(data)
            >>> isinstance(result, Workspace)
            True
        '''
        if 'object' not in source:
            return source
        func = get_loader(source['object'])
        result = func(source, self)
        if isinstance(result, NuclinoObject):
            return result
        elif isinstance(result, list):
            return [self.parse(li) for li in result]
        else:
            return source

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> ResponseData:
        """
        Make a GET request to the API.

        Args:
            path: The API endpoint path (e.g., '/workspaces/123')
            params: Optional query parameters to include in the request

        Returns:
            Union[List[NuclinoObject], NuclinoObject, dict]: The parsed response data

        Raises:
            NuclinoHTTPException: If the request fails
            NuclinoRateLimitError: If rate limit is exceeded
        """
        self.check_limit()
        response = self.session.get(join_url(self.base_url, path), params=params or {})
        return self._handle_response(response)

    def delete(self, path: str) -> ResponseData:
        """
        Make a DELETE request to the API.

        Args:
            path: The API endpoint path (e.g., '/items/123')

        Returns:
            Union[List[NuclinoObject], NuclinoObject, dict]: The parsed response data

        Raises:
            NuclinoHTTPException: If the request fails
            NuclinoRateLimitError: If rate limit is exceeded
        """
        self.check_limit()
        response = self.session.delete(join_url(self.base_url, path))
        return self._handle_response(response)

    def post(self, path: str, data: Dict[str, Any]) -> ResponseData:
        """
        Make a POST request to the API.

        Args:
            path: The API endpoint path (e.g., '/items')
            data: The request body data to send

        Returns:
            Union[List[NuclinoObject], NuclinoObject, dict]: The parsed response data

        Raises:
            NuclinoHTTPException: If the request fails
            NuclinoRateLimitError: If rate limit is exceeded
        """
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.post(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._handle_response(response)

    def put(self, path: str, data: Dict[str, Any]) -> ResponseData:
        """
        Make a PUT request to the API.

        Args:
            path: The API endpoint path (e.g., '/items/123')
            data: The request body data to send

        Returns:
            Union[List[NuclinoObject], NuclinoObject, dict]: The parsed response data

        Raises:
            NuclinoHTTPException: If the request fails
            NuclinoRateLimitError: If rate limit is exceeded
        """
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.put(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._handle_response(response) 