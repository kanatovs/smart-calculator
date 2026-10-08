"""Validation helpers for calculator input."""

import math
import re

# Tuple is used because valid operators are a fixed sequence of allowed values.
VALID_OPERATORS = ("+", "-", "*", "/", "**", "%")


def is_valid_number(value):
    """Accept finite decimal input, including scientific notation."""
    if not isinstance(value, str):
        return False
    pattern = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
    return bool(re.fullmatch(pattern, value)) and math.isfinite(float(value))


def require_finite_real(value, name="Number"):
    """Reject complex values, booleans, NaN, infinity, and excessive integers."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a real number")
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f"{name} is too large or is not finite")
    return value


def is_valid_operator(operator):
    """Return True if the operator is supported by the calculator."""
    return operator in VALID_OPERATORS
