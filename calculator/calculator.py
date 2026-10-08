"""Main calculator class that connects operations with history storage."""

from calculator.decorators import log_action
from calculator.history_manager import HistoryManager
from calculator.operations import (
    Addition,
    Division,
    Modulus,
    Multiplication,
    Power,
    Subtraction,
)
from calculator.validators import is_valid_operator, require_finite_real


class Calculator:
    """Perform calculator operations and store every successful result."""

    def __init__(self):
        self.history_manager = HistoryManager()

    @log_action
    def perform_operation(self, operand1, operand2, operator):
        """Perform the selected arithmetic operation and save it to history."""
        operation_map = {
            "+": Addition,
            "-": Subtraction,
            "*": Multiplication,
            "/": Division,
            "**": Power,
            "%": Modulus,
        }

        if not is_valid_operator(operator):
            raise ValueError("Invalid operator")

        require_finite_real(operand1, "First operand")
        require_finite_real(operand2, "Second operand")
        operation = operation_map[operator](operand1, operand2)
        try:
            result = operation.calculate()
        except OverflowError as error:
            raise ValueError("Result is too large; try smaller numbers") from error
        except ZeroDivisionError as error:
            raise ValueError("Zero cannot be raised to a negative power") from error
        require_finite_real(result, "Result")

        self.history_manager.add_record(operand1, operand2, operator, result)
        return result
