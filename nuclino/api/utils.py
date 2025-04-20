from functools import wraps
from time import sleep


def sleep_and_retry(sleep_time: float = 1):
    """
    Decorator that makes a rate-limited function sleep and retry on error.
    
    :param sleep_time: Time to sleep between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    sleep(sleep_time)
                    continue
        return wrapper
    return decorator 