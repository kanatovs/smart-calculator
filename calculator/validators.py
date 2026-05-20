"""Validation helpers for calculator input."""

import re

# Tuple is used because valid operators are a fixed sequence of allowed values.
VALID_OPERATORS = ("+", "-", "*", "/", "**", "%")


def is_valid_number(value):
    """Return True if the provided string is a valid integer or decimal number."""
    pattern = r"^-?\d+(\.\d+)?$"
    return bool(re.fullmatch(pattern, value))


def is_valid_operator(operator):
    """Return True if the operator is supported by the calculator."""
    return operator in VALID_OPERATORS
