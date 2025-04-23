# Nuclino Python API Client

A Python client library for interacting with the [Nuclino API](https://api.nuclino.com/v0). This library provides a clean, Pythonic interface to Nuclino's REST API, making it easy to manage workspaces, items, and collections programmatically.

## Features

- Full support for Nuclino API v0
- Object-oriented interface with proper type hints
- Automatic rate limiting handling
- Comprehensive error handling
- Convenient helper methods for common operations
- Support for both items and collections management
- Built-in pagination handling

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

### Error Handling

The library provides detailed error handling with specific exception classes:

- `NuclinoAuthenticationError`: Authentication failures
- `NuclinoPermissionError`: Permission-related issues
- `NuclinoValidationError`: Invalid request parameters
- `NuclinoNotFoundError`: Resource not found
- `NuclinoRateLimitError`: Rate limit exceeded
- `NuclinoServerError`: Server-side errors

### Rate Limiting

Built-in rate limiting support helps prevent API quota exhaustion:

- Automatic request rate monitoring
- Built-in retry mechanism
- Configurable requests per minute limit

### Type Safety

The library is fully typed with Python type hints:

- All methods have proper return type annotations
- TypedDict definitions for API request/response data
- Support for IDE autocompletion
- Mypy compatibility

## API Reference

### Main Client

```python
class Client:
    def __init__(self, api_key: str, base_url: str = "https://api.nuclino.com/v0", requests_per_minute: int = 140)
```

### Item Operations

```python
def get_items(
    team_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    limit: Optional[int] = None,
    after: Optional[str] = None
) -> List[Union[Item, Collection]]

def get_item(item_id: str) -> Union[Item, Collection]

def create_item(
    workspace_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    object: str = 'item',
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
    index: Optional[int] = None
) -> Collection

def update_collection(
    collection_id: str,
    title: Optional[str] = None
) -> Collection

def delete_collection(collection_id: str) -> BaseDeleteResponse
```

## Error Handling

```python
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for the [Nuclino API](https://api.nuclino.com/v0)
- Inspired by modern Python API client design patterns
