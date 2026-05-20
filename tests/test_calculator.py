"""Unit tests for the Smart Calculator project."""

import os
import tempfile
import unittest

from calculator.calculator import Calculator
from calculator.history_manager import HistoryManager
from calculator.validators import VALID_OPERATORS, is_valid_number, is_valid_operator


class TestCalculator(unittest.TestCase):
    """Test calculator logic, validation, history, and file I/O."""

    def setUp(self):
        self.calculator = Calculator()

    def test_addition(self):
        result = self.calculator.perform_operation(10, 5, "+")
        self.assertEqual(result, 15)

    def test_subtraction(self):
        result = self.calculator.perform_operation(10, 3, "-")
        self.assertEqual(result, 7)

    def test_multiplication(self):
        result = self.calculator.perform_operation(4, 6, "*")
        self.assertEqual(result, 24)

    def test_division(self):
        result = self.calculator.perform_operation(20, 4, "/")
        self.assertEqual(result, 5)

    def test_power(self):
        result = self.calculator.perform_operation(2, 3, "**")
        self.assertEqual(result, 8)

    def test_modulus(self):
        result = self.calculator.perform_operation(10, 3, "%")
        self.assertEqual(result, 1)

    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            self.calculator.perform_operation(10, 0, "/")

    def test_modulus_by_zero(self):
        with self.assertRaises(ValueError):
            self.calculator.perform_operation(10, 0, "%")

    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            self.calculator.perform_operation(10, 5, "//")

    def test_history_add_record(self):
        self.calculator.perform_operation(1, 2, "+")
        history = self.calculator.history_manager.get_all()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["result"], 3)

    def test_statistics(self):
        manager = HistoryManager()
        manager.add_record(10, 5, "+", 15)
        manager.add_record(8, 2, "/", 4)
        manager.add_record(3, 5, "-", -2)

        stats = manager.get_statistics()

        self.assertEqual(stats["total_operations"], 3)
        self.assertEqual(stats["max_result"], 15)
        self.assertEqual(stats["min_result"], -2)
        self.assertEqual(stats["positive_results"], 2)

    def test_map_results_only(self):
        manager = HistoryManager()
        manager.add_record(1, 2, "+", 3)
        manager.add_record(4, 2, "*", 8)
        self.assertEqual(manager.get_results_only(), [3, 8])

    def test_filter_positive_results(self):
        manager = HistoryManager()
        manager.add_record(1, 2, "+", 3)
        manager.add_record(2, 5, "-", -3)
        self.assertEqual(len(manager.filter_positive_results()), 1)

    def test_history_generator(self):
        manager = HistoryManager()
        manager.add_record(1, 2, "+", 3)
        generated = list(manager.history_generator())
        self.assertEqual(generated[0]["operator"], "+")

    def test_json_save_and_load(self):
        manager = HistoryManager()
        manager.add_record(7, 3, "+", 10)

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "history.json")
            manager.save_to_json(path)

            second_manager = HistoryManager()
            second_manager.load_from_json(path)

        self.assertEqual(second_manager.get_all()[0]["result"], 10)

    def test_csv_export(self):
        manager = HistoryManager()
        manager.add_record(7, 3, "+", 10)

        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "history.csv")
            manager.export_to_csv(path)
            self.assertTrue(os.path.exists(path))

    def test_valid_number(self):
        self.assertTrue(is_valid_number("10"))
        self.assertTrue(is_valid_number("-3.5"))
        self.assertFalse(is_valid_number("abc"))

    def test_valid_operator(self):
        self.assertIsInstance(VALID_OPERATORS, tuple)
        self.assertTrue(is_valid_operator("+"))
        self.assertTrue(is_valid_operator("%"))
        self.assertFalse(is_valid_operator("//"))


if __name__ == "__main__":
    unittest.main()
