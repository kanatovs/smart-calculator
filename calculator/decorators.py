"""Custom decorators used in the calculator project."""

import logging
from datetime import datetime
from functools import wraps

from calculator.paths import ACTIVITY_LOG


def log_action(func):
    """Log successful calls without turning a logging failure into a failed calculation."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        try:
            ACTIVITY_LOG.parent.mkdir(parents=True, exist_ok=True)
            with ACTIVITY_LOG.open("a", encoding="utf-8") as file:
                file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                    f"{func.__name__} was called\n"
                )
        except OSError as error:
            logging.getLogger(__name__).warning("Could not write activity log: %s", error)

        return result

    return wrapper
