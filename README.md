# Nuclino Python API Client

A Python client library for interacting with the [Nuclino API](https://api.nuclino.com/v0). This library provides a clean, Pythonic interface to Nuclino's REST API, making it easy to manage workspaces, items, and collections programmatically.

## Features

- Typed client methods and object models
- Support for core Nuclino API v0 resources
- Configurable client-side request throttling
- Structured exception hierarchy
- Convenient helper methods for common operations
- Support for items, collections, workspaces, teams, users, and files
- Cursor-based list endpoints via `limit` and `after`
- Search support for items and collections via `search`

## Installation

```bash
pip install nuclino
```

## Quick Start

```python
from nuclino import NuclinoAPI

# Initialize the client
client = NuclinoAPI(api_key="your-api-key")

# Get items from a workspace
items = client.get_items(workspace_id="your-workspace-id")

# Search items in a workspace
matches = client.get_items(workspace_id="your-workspace-id", search="hello")

# Create a new item
new_item = client.create_item(
    workspace_id="your-workspace-id",
    title="My New Item",
    content="This is the content of my new item"
)

# Update an item
updated_item = client.update_item(
    item_id="your-item-id",
    title="Updated Title",
    content="Updated content"
)

# Delete an item
client.delete_item("your-item-id")
```

## Features in Detail

### Items and Collections

The library supports all operations on both items and collections:

- Create, read, update, and delete items
- Create, read, update, and delete collections
- Organize items within collections
- Manage item content and metadata
- List and search endpoints expose `content` as `None` until you fetch the full item

### Error Handling

The library provides detailed error handling with specific exception classes:

- `NuclinoError`: Root exception for all SDK and API failures
- `NuclinoClientValidationError`: Invalid request parameters detected before sending a request
- `NuclinoAuthenticationError`: Authentication failures
- `NuclinoPermissionError`: Permission-related issues
- `NuclinoValidationError`: HTTP `400 fail` responses returned by the API
- `NuclinoNotFoundError`: Resource not found
- `NuclinoRateLimitError`: Rate limit exceeded
- `NuclinoTransportError`: Network or connection failures before any HTTP response is received
- `NuclinoTimeoutError`: Request timed out before any HTTP response is received
- `NuclinoResponseFormatError`: HTTP response did not match Nuclino's documented envelope
- `NuclinoServerError`: Server-side errors

### Rate Limiting

Built-in rate limiting support helps prevent API quota exhaustion:

- Automatic client-side request throttling
- Automatic retry handling for rate-limit responses
- Configurable requests per minute limit
- Defaults to Nuclino's documented 150 requests per minute per API key

### Type Safety

The library exposes typed client methods and model objects:

- Public methods have return type annotations
- Models preserve the raw API payload while exposing Python-style attribute access
- Support for IDE autocompletion
- Checked with ty in CI

## API Reference

### Main Client

```python
class NuclinoAPI:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.nuclino.com/v0",
        requests_per_minute: int = 150,
        request_timeout: float = 10.0,
        max_rate_limit_retries: int = 3,
        session: requests.Session | None = None,
    )
```

### Item Operations

```python
def get_items(
    team_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None
) -> List[Union[Item, Collection]]

def get_item(item_id: str) -> Union[Item, Collection]

def create_item(
    workspace_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    object: str = "item",
    title: Optional[str] = None,
    content: Optional[str] = None,
    index: Optional[int] = None
) -> Union[Item, Collection]

def update_item(
    item_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> Union[Item, Collection]

def delete_item(item_id: str) -> BaseDeleteResponse
```

### Collection Operations

```python
def get_collection(collection_id: str) -> Collection

def create_collection(
    workspace_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    title: Optional[str] = None,
    content: Optional[str] = None,
    index: Optional[int] = None
) -> Collection

def update_collection(
    collection_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None
) -> Collection

def delete_collection(collection_id: str) -> BaseDeleteResponse
```

## Error Handling

```python
from nuclino.api import (
    NuclinoError,
    NuclinoResponseFormatError,
    NuclinoTransportError,
)

try:
    client.get_item("non-existent-id")
except NuclinoNotFoundError:
    print("Item not found")
except NuclinoAuthenticationError:
    print("Invalid API key")
except NuclinoPermissionError:
    print("Insufficient permissions")
except NuclinoRateLimitError as e:
    print(f"Rate limit exceeded. Try again in {e.retry_after} seconds")
```

Or branch from the shared root exception:

```python
from nuclino.api import NuclinoError, NuclinoTransportError, NuclinoResponseFormatError

try:
    client.get_items(workspace_id="workspace-id")
except NuclinoError as exc:
    if exc.category == "client_validation":
        print("Fix request parameters before retrying")
    elif isinstance(exc, NuclinoTransportError):
        print("Network issue, safe to retry")
    elif isinstance(exc, NuclinoResponseFormatError):
        print("Nuclino returned an unexpected success envelope")
    else:
        print(f"API returned {exc}")
```

## Development

```bash
uv sync --dev
uv run ruff check .
uv run ty check
uv run pytest
uv build
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built for the [Nuclino API](https://api.nuclino.com/v0)
- Inspired by modern Python API client design patterns
