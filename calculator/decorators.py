"""Custom decorators used in the calculator project."""

import os
from datetime import datetime
from functools import wraps


def log_action(func):
    """Log every successful call of the decorated function to data/logs.txt."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        os.makedirs("data", exist_ok=True)
        with open("data/logs.txt", "a", encoding="utf-8") as file:
            file.write(
                f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                f"{func.__name__} was called\n"
            )

        return result

    return wrapper
