from typing import List, Union

import requests
from ratelimit import limits

from nuclino.api.exceptions import raise_for_status_code
from nuclino.api.utils import sleep_and_retry
from nuclino.models.shared import NuclinoObject, get_loader

BASE_URL = 'https://api.nuclino.com/v0'

def join_url(base_url: str, path: str) -> str:
    """Join base URL with path, ensuring proper formatting"""
    return '/'.join(part.strip('/') for part in [base_url, path])

class Client:
    '''
    Base class for Nuclino API client. May be used as a context processor.
    '''

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        requests_per_minute: int = 140
    ):
        '''
        :param api_key:       your Nuclino API key.
        :param base_url:      base url to send API requests.
        :requests_per_minute: max requests per minute. If limit exceeded, client will wait
                              for some time before processing the next request.
        '''
        self.check_limit = sleep_and_retry()(
            limits(requests_per_minute, period=60)(lambda: None)
        )
        self.session = requests.Session()
        self.session.headers['Authorization'] = api_key
        self.timer = None
        self.base_url = base_url

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        """Close the session"""
        self.session.close()

    def _process_response(
        self,
        response: requests.models.Response
    ) -> Union[List, NuclinoObject, dict]:
        '''
        General method that processes API responses. Raises appropriate exceptions on HTTP
        errors, sends results to parser on 200 ok.

        :param response: response object, received after calling API.
        :returns: Parsed response data
        :raises: Various NuclinoHTTPException subclasses based on the error type
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

    def parse(self, source: dict) -> Union[List, NuclinoObject, dict]:
        '''
        Parse successful response dictionary. This method will determine the
        type of object, that was returned, and construct corresponding
        NuclinoObject as the return result.

        :param source: the "data" dictionary from Nuclino API response.
        :returns:      corresponsing NuclinoObject constructed from `source`.
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

    def get(self, path: str, params: dict = {}) -> Union[List, NuclinoObject, dict]:
        """Make a GET request to the API"""
        self.check_limit()
        response = self.session.get(join_url(self.base_url, path), params=params)
        return self._process_response(response)

    def delete(self, path: str) -> Union[List, NuclinoObject, dict]:
        """Make a DELETE request to the API"""
        self.check_limit()
        response = self.session.delete(join_url(self.base_url, path))
        return self._process_response(response)

    def post(self, path: str, data: dict) -> Union[List, NuclinoObject, dict]:
        """Make a POST request to the API"""
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.post(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._process_response(response)

    def put(self, path: str, data: dict) -> Union[List, NuclinoObject, dict]:
        """Make a PUT request to the API"""
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.put(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._process_response(response) 