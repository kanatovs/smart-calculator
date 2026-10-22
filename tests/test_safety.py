"""Regression tests for invalid arithmetic and history data loss."""

import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from calculator.calculator import Calculator
from calculator.history_manager import HistoryManager
from calculator.paths import ACTIVITY_LOG, DATA_DIRECTORY, HISTORY_CSV, HISTORY_JSON
from calculator.validators import is_valid_number
from main import CalculatorApp


class CalculatorSafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.folder = Path(self.directory.name)
        log_patch = patch("calculator.decorators.ACTIVITY_LOG", self.folder / "logs.txt")
        log_patch.start()
        self.addCleanup(log_patch.stop)
        self.calculator = Calculator()

    def assert_operation_rejected(self, first, second, operator, message):
        with self.assertRaisesRegex(ValueError, message):
            self.calculator.perform_operation(first, second, operator)
        self.assertEqual(self.calculator.history_manager.get_all(), [])
        self.assertFalse((self.folder / "logs.txt").exists())

    def test_negative_fractional_power_never_enters_history(self):
        self.assert_operation_rejected(-1, 0.5, "**", "fractional power")

    def test_negative_integer_power_is_supported(self):
        self.assertEqual(self.calculator.perform_operation(-2, -3, "**"), -0.125)

    def test_power_overflow_is_a_readable_validation_error(self):
        self.assert_operation_rejected(1e308, 2, "**", "too large")

    def test_enormous_integer_power_is_rejected_before_allocation(self):
        self.assert_operation_rejected(2, 10**100, "**", "too large")

    def test_zero_to_negative_power_is_a_validation_error(self):
        self.assert_operation_rejected(0, -1, "**", "Zero cannot")

    def test_infinite_arithmetic_results_are_rejected(self):
        for first, second, operator in (
            (1e308, 1e308, "+"), (-1e308, 1e308, "-"),
            (1e308, 10, "*"), (1e308, 1e-308, "/"),
        ):
            with self.subTest(operator=operator):
                self.assert_operation_rejected(first, second, operator, "not finite")

    def test_non_real_and_non_finite_operands_are_rejected(self):
        for invalid in (float("nan"), float("inf"), -float("inf"), 1j, True, "3", 10**400):
            for position in (0, 1):
                with self.subTest(value=repr(invalid), position=position):
                    operands = [2, 3]
                    operands[position] = invalid
                    self.assert_operation_rejected(*operands, "+", "operand")

    def test_numeric_input_supports_common_decimal_forms(self):
        for text in ("10", "-3.5", "+.5", "2.", "1e-3", "-2E+6"):
            with self.subTest(text=text):
                self.assertTrue(is_valid_number(text))

    def test_numeric_input_rejects_unbounded_or_invalid_values(self):
        for text in ("nan", "inf", "1e309", "9" * 400, "1+2j", "", "--2", " 2 ", None):
            with self.subTest(text=text):
                self.assertFalse(is_valid_number(text))

    def test_logging_permission_error_does_not_lose_successful_calculation(self):
        with patch("pathlib.Path.open", side_effect=PermissionError("read only")):
            with self.assertLogs("calculator.decorators", level="WARNING"):
                self.assertEqual(self.calculator.perform_operation(2, 3, "+"), 5)
        self.assertEqual(self.calculator.history_manager.get_all()[0]["result"], 5)

    def test_storage_paths_do_not_follow_working_directory(self):
        previous = Path.cwd()
        try:
            os.chdir(self.folder)
            self.assertEqual(DATA_DIRECTORY, Path(__file__).resolve().parents[1] / "data")
            self.assertEqual(HISTORY_JSON.parent, DATA_DIRECTORY)
            self.assertEqual(HISTORY_CSV.parent, DATA_DIRECTORY)
            self.assertEqual(ACTIVITY_LOG.parent, DATA_DIRECTORY)
            self.assertEqual(self.calculator.perform_operation(1, 2, "+"), 3)
        finally:
            os.chdir(previous)


class HistorySafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "history.json"
        self.manager = HistoryManager()
        self.manager.add_record(2, 3, "+", 5)
        self.original = self.manager.get_all()

    def assert_invalid_load_preserves_history(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        original_file = self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.manager.load_from_json(self.path)
        self.assertEqual(self.manager.get_all(), self.original)
        self.assertEqual(self.path.read_bytes(), original_file)
        self.assertEqual(self.manager.add_record(4, 5, "+", 9)["id"], 2)
        self.manager = HistoryManager()
        record = self.original[0]
        self.manager.add_record(record["operand1"], record["operand2"], record["operator"], record["result"])
        self.original = self.manager.get_all()

    def test_malformed_json_preserves_history_and_next_id(self):
        self.path.write_text('[{"id":', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.manager.load_from_json(self.path)
        self.assertEqual(self.manager.get_all(), self.original)
        self.assertEqual(self.manager.add_record(1, 1, "+", 2)["id"], 2)

    def test_missing_file_does_not_clear_history(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.load_from_json(self.path)
        self.assertEqual(self.manager.get_all(), self.original)

    def test_invalid_utf8_preserves_history_file_and_next_id(self):
        invalid_data = b'[\xff]'
        self.path.write_bytes(invalid_data)
        with self.assertRaises(UnicodeDecodeError):
            self.manager.load_from_json(self.path)
        self.assertEqual(self.manager.get_all(), self.original)
        self.assertEqual(self.path.read_bytes(), invalid_data)
        self.assertEqual(self.manager.add_record(1, 1, "+", 2)["id"], 2)

    def test_non_array_json_is_rejected(self):
        for data in ({}, None, "history", 123):
            with self.subTest(data=data):
                self.assert_invalid_load_preserves_history(data)

    def test_record_fields_are_required_and_unknown_fields_are_rejected(self):
        record = self.original[0]
        for field in record:
            with self.subTest(missing=field):
                bad = record.copy()
                del bad[field]
                self.assert_invalid_load_preserves_history([bad])
        self.assert_invalid_load_preserves_history([dict(record, note="unsupported")])
        self.assert_invalid_load_preserves_history([42])

    def test_invalid_ids_operators_and_timestamps_are_rejected(self):
        changes = (
            ("id", 0), ("id", -1), ("id", True), ("id", 1.5),
            ("operator", "//"), ("operator", None),
            ("timestamp", "2026-02-30 12:00:00"),
            ("timestamp", "2026-1-1 12:00:00"), ("timestamp", 123),
        )
        for field, value in changes:
            with self.subTest(field=field, value=value):
                bad = self.original[0].copy()
                bad[field] = value
                self.assert_invalid_load_preserves_history([bad])

    def test_duplicate_ids_are_rejected(self):
        self.assert_invalid_load_preserves_history(self.original * 2)

    def test_invalid_numeric_fields_are_rejected(self):
        for field in ("operand1", "operand2", "result"):
            for value in ("3", True, None, float("inf"), float("nan"), 10**400):
                with self.subTest(field=field, value=repr(value)):
                    bad = self.original[0].copy()
                    bad[field] = value
                    self.assert_invalid_load_preserves_history([bad])

    def test_one_bad_record_does_not_partially_load_good_records(self):
        first = dict(self.original[0], id=10)
        bad = dict(self.original[0], id=11, result="bad")
        self.assert_invalid_load_preserves_history([first, bad])

    def test_load_uses_highest_id_and_preserves_record_order(self):
        records = [dict(self.original[0], id=10), dict(self.original[0], id=3)]
        self.path.write_text(json.dumps(records), encoding="utf-8")
        self.manager.load_from_json(self.path)
        self.assertEqual(self.manager.get_all(), records)
        self.assertEqual(self.manager.add_record(1, 1, "+", 2)["id"], 11)

    def test_empty_history_is_a_valid_explicit_load(self):
        self.path.write_text("[]", encoding="utf-8")
        self.manager.load_from_json(self.path)
        self.assertEqual(self.manager.get_all(), [])
        self.assertEqual(self.manager.add_record(1, 1, "+", 2)["id"], 1)

    def test_direct_add_rejects_bad_values_without_consuming_an_id(self):
        with self.assertRaises(ValueError):
            self.manager.add_record(1, 2, "+", 1j)
        self.assertEqual(self.manager.get_all(), self.original)
        self.assertEqual(self.manager.add_record(1, 2, "+", 3)["id"], 2)

    def test_json_serialization_failure_preserves_existing_file(self):
        self.path.write_text("existing file", encoding="utf-8")

        def failing_dump(records, file, **kwargs):
            file.write("partial content")
            raise OSError("disk full")

        with patch("calculator.history_manager.json.dump", side_effect=failing_dump):
            with self.assertRaises(OSError):
                self.manager.save_to_json(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "existing file")
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])
        self.assertEqual(self.manager.get_all(), self.original)

    def test_atomic_replace_failure_preserves_existing_file_and_cleans_temp(self):
        self.manager.save_to_json(self.path)
        original_bytes = self.path.read_bytes()
        with patch("calculator.history_manager.os.replace", side_effect=PermissionError("locked")):
            with self.assertRaises(PermissionError):
                self.manager.save_to_json(self.path)
        self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_sync_failure_preserves_existing_json_and_csv(self):
        for method in (self.manager.save_to_json, self.manager.export_to_csv):
            with self.subTest(method=method.__name__):
                original_bytes = b"previous saved data\n"
                self.path.write_bytes(original_bytes)
                with patch("calculator.history_manager.os.fsync", side_effect=OSError("disk full")):
                    with self.assertRaises(OSError):
                        method(self.path)
                self.assertEqual(self.path.read_bytes(), original_bytes)
                self.assertEqual(list(self.path.parent.iterdir()), [self.path])
                self.assertEqual(self.manager.get_all(), self.original)

    def test_csv_write_failure_preserves_existing_export(self):
        self.path.write_text("existing CSV", encoding="utf-8")
        with patch("calculator.history_manager.csv.DictWriter.writerows", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.manager.export_to_csv(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), "existing CSV")
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_csv_export_contents_match_history(self):
        self.manager.export_to_csv(self.path)
        with self.path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(rows[0]["result"], "5")
        self.assertEqual(rows[0]["timestamp"], self.original[0]["timestamp"])

    def test_mean_does_not_overflow_for_valid_large_results(self):
        self.manager.clear_history()
        for _ in range(3):
            self.manager.add_record(sys.float_info.max, 0, "+", sys.float_info.max)
        self.assertEqual(self.manager.get_statistics()["average_result"], sys.float_info.max)

    def test_get_all_does_not_expose_mutable_history(self):
        records = self.manager.get_all()
        records[0]["result"] = "bad"
        records.clear()
        self.assertEqual(self.manager.get_all(), self.original)

    def test_examples_are_valid_and_export_equivalent_records(self):
        examples = Path(__file__).resolve().parents[1] / "examples"
        self.manager.load_from_json(examples / "history.json")
        self.manager.export_to_csv(self.path)
        self.assertEqual(self.path.read_text(), (examples / "history.csv").read_text())


class GuiStorageErrorTests(unittest.TestCase):
    def setUp(self):
        self.app = CalculatorApp.__new__(CalculatorApp)
        self.app.calculator = Calculator()
        self.app.json_file = HISTORY_JSON
        self.app.csv_file = HISTORY_CSV
        self.app.refresh_history_list = Mock()

    def test_save_and_export_failures_show_error_without_success_message(self):
        for method, storage_method in (
            (self.app.save_history, "save_to_json"),
            (self.app.export_csv, "export_to_csv"),
        ):
            with self.subTest(method=storage_method):
                with patch.object(self.app.calculator.history_manager, storage_method,
                                  side_effect=PermissionError("read only")), \
                        patch("main.messagebox.showerror") as error, \
                        patch("main.messagebox.showinfo") as success:
                    method()
                    self.assertIn("Permission denied", error.call_args.args[1])
                    success.assert_not_called()

    def test_invalid_load_leaves_gui_history_intact(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("not JSON", encoding="utf-8")
            self.app.json_file = path
            self.app.calculator.history_manager.add_record(1, 2, "+", 3)
            with patch("main.messagebox.showerror") as error, \
                    patch("main.messagebox.showinfo") as success:
                self.app.load_history()
        self.assertIn("Invalid history data", error.call_args.args[1])
        self.assertEqual(self.app.calculator.history_manager.get_all()[0]["result"], 3)
        self.app.refresh_history_list.assert_not_called()
        success.assert_not_called()

    def test_missing_load_explains_how_to_create_history(self):
        with tempfile.TemporaryDirectory() as folder:
            self.app.json_file = Path(folder) / "missing.json"
            with patch("main.messagebox.showerror") as error:
                self.app.load_history()
        self.assertIn("Save JSON first", error.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
