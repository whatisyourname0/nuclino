from functools import wraps
from time import sleep
from typing import Any, Callable, Optional, TypeVar

from ratelimit.exception import RateLimitException

from nuclino.api.exceptions import NuclinoValidationError

T = TypeVar('T', bound=Callable[..., Any])


def sleep_and_retry(sleep_time: float = 1) -> Callable[[T], T]:
    """Retry only local ratelimit exceptions after sleeping."""

    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            while True:
                try:
                    return func(*args, **kwargs)
                except RateLimitException as exc:
                    wait_time = max(sleep_time, exc.period_remaining)
                    sleep(wait_time)

        return wrapper  # type: ignore[return-value]

    return decorator


def validate_limit(limit: Optional[int]) -> Optional[int]:
    """Validate Nuclino list endpoint limits."""
    if limit is None:
        return None
    if not 1 <= limit <= 100:
        raise NuclinoValidationError(400, "limit must be between 1 and 100")
    return limit


def validate_parent_scope(
    workspace_id: Optional[str],
    parent_id: Optional[str],
) -> None:
    """Require exactly one creation scope for items and collections."""
    if workspace_id is None and parent_id is None:
        raise NuclinoValidationError(400, "Must specify either workspace_id or parent_id")
    if workspace_id is not None and parent_id is not None:
        raise NuclinoValidationError(400, "Cannot specify both workspace_id and parent_id")


def validate_item_object(object_name: str) -> str:
    """Validate supported Nuclino item object values."""
    if object_name not in {"item", "collection"}:
        raise NuclinoValidationError(400, "object must be either 'item' or 'collection'")
    return object_name
