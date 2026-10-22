"""Operation classes for the Smart Calculator project."""

from abc import ABC, abstractmethod


class Operation(ABC):
    """Abstract base class for all calculator operations."""

    def __init__(self, operand1, operand2=None):
        self._operand1 = operand1
        self._operand2 = operand2

    @abstractmethod
    def calculate(self):
        """Calculate and return the result of the operation."""

    @property
    def operand1(self):
        """Return the first operand."""
        return self._operand1

    @property
    def operand2(self):
        """Return the second operand."""
        return self._operand2


class BinaryOperation(Operation):
    """Parent class for operations that use two operands."""

    def __init__(self, operand1, operand2):
        super().__init__(operand1, operand2)


class Addition(BinaryOperation):
    """Addition operation."""

    def calculate(self):
        """Return the sum of two operands."""
        return self.operand1 + self.operand2


class Subtraction(BinaryOperation):
    """Subtraction operation."""

    def calculate(self):
        """Return the difference between two operands."""
        return self.operand1 - self.operand2


class Multiplication(BinaryOperation):
    """Multiplication operation."""

    def calculate(self):
        """Return the product of two operands."""
        return self.operand1 * self.operand2


class Division(BinaryOperation):
    """Division operation."""

    def calculate(self):
        """Return the quotient of two operands."""
        if self.operand2 == 0:
            raise ValueError("Cannot divide by zero")
        return self.operand1 / self.operand2


class Power(BinaryOperation):
    """Power operation."""

    def calculate(self):
        """Return the first operand raised to the power of the second operand."""
        if self.operand1 < 0 and self.operand2 % 1 != 0:
            raise ValueError("A negative number cannot be raised to a fractional power")
        if isinstance(self.operand1, int) and isinstance(self.operand2, int):
            # Check the finite numeric range before allocating an enormous integer.
            float(self.operand1) ** self.operand2
        return self.operand1 ** self.operand2


class Modulus(BinaryOperation):
    """Modulus operation."""

    def calculate(self):
        """Return the remainder after division."""
        if self.operand2 == 0:
            raise ValueError("Cannot take modulus by zero")
        return self.operand1 % self.operand2
