from functools import wraps
from time import sleep
from typing import Any, Callable, TypeVar

T = TypeVar('T', bound=Callable[..., Any])

def sleep_and_retry(sleep_time: float = 1) -> Callable[[T], T]:
    """
    Decorator that makes a rate-limited function sleep and retry on error.
    
    Args:
        sleep_time: Time to sleep between retries in seconds
        
    Returns:
        A decorator function that adds sleep and retry functionality
    """
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    sleep(sleep_time)
                    continue
        return wrapper  # type: ignore
    return decorator 