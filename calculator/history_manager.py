"""History manager for saving, loading, searching, and analyzing operations."""

import csv
import json
import os
import statistics
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from calculator.validators import is_valid_operator, require_finite_real

FIELDS = ("id", "operand1", "operand2", "operator", "result", "timestamp")
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


@contextmanager
def atomic_text_file(filename, newline=None):
    """Replace a destination only after its complete contents are safely written."""
    destination = Path(filename)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline=newline,
            dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp",
            delete=False,
        ) as file:
            temporary_name = file.name
            yield file
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_name, destination)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)


def validate_records(records):
    """Validate the full JSON schema before replacing any in-memory history."""
    if not isinstance(records, list):
        raise ValueError("History must be a JSON array of operation records")
    seen_ids = set()
    validated = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict) or set(record) != set(FIELDS):
            raise ValueError(f"Record {index} must contain exactly: {', '.join(FIELDS)}")
        record_id = record["id"]
        if isinstance(record_id, bool) or not isinstance(record_id, int) or record_id < 1:
            raise ValueError(f"Record {index} must have a positive integer id")
        if record_id in seen_ids:
            raise ValueError(f"Record {index} has a duplicate id")
        seen_ids.add(record_id)
        for field in ("operand1", "operand2", "result"):
            require_finite_real(record[field], f"Record {index} {field}")
        if not is_valid_operator(record["operator"]):
            raise ValueError(f"Record {index} has an unsupported operator")
        timestamp = record["timestamp"]
        if not isinstance(timestamp, str):
            raise ValueError(f"Record {index} must have a timestamp string")
        try:
            parsed_timestamp = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        except ValueError as error:
            raise ValueError(f"Record {index} timestamp must use YYYY-MM-DD HH:MM:SS") from error
        if parsed_timestamp.strftime(TIMESTAMP_FORMAT) != timestamp:
            raise ValueError(f"Record {index} timestamp must use YYYY-MM-DD HH:MM:SS")
        validated.append(record.copy())
    return validated


def reject_json_constant(value):
    """Reject JSON's nonstandard NaN and Infinity extensions."""
    raise ValueError(f"History contains a non-finite number: {value}")


class HistoryManager:
    """Manage calculator operation records and file persistence."""

    def __init__(self):
        self.history = []
        self._next_id = 1

    def add_record(self, operand1, operand2, operator, result):
        """Add one operation record to history and return the created record."""
        require_finite_real(operand1, "First operand")
        require_finite_real(operand2, "Second operand")
        require_finite_real(result, "Result")
        if not is_valid_operator(operator):
            raise ValueError("Invalid operator")
        record = {
            "id": self._next_id,
            "operand1": operand1,
            "operand2": operand2,
            "operator": operator,
            "result": result,
            "timestamp": datetime.now().strftime(TIMESTAMP_FORMAT),
        }
        self.history.append(record)
        self._next_id += 1
        return record.copy()

    def get_all(self):
        """Return all history records."""
        return [record.copy() for record in self.history]

    def clear_history(self):
        """Remove all history records and reset the next record id."""
        self.history = []
        self._next_id = 1

    def save_to_json(self, filename):
        """Atomically save valid history; preserve the old file if saving fails."""
        records = validate_records(self.history)
        with atomic_text_file(filename) as file:
            json.dump(records, file, indent=4, allow_nan=False)
            file.write("\n")

    def load_from_json(self, filename):
        """Replace history only after a complete successful read and validation."""
        with open(filename, "r", encoding="utf-8") as file:
            records = validate_records(json.load(file, parse_constant=reject_json_constant))
        next_id = max((record["id"] for record in records), default=0) + 1
        self.history = records
        self._next_id = next_id

    def export_to_csv(self, filename):
        """Atomically export valid history to a CSV file."""
        records = validate_records(self.history)
        with atomic_text_file(filename, newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)

    def search_by_operator(self, operator):
        """Return records that match the selected operator."""
        return [item for item in self.history if item["operator"] == operator]

    def get_results_only(self):
        """Return only operation results using map and lambda."""
        return list(map(lambda item: item["result"], self.history))

    def filter_positive_results(self):
        """Return records with positive results using filter and lambda."""
        return list(filter(lambda item: item["result"] > 0, self.history))

    def history_generator(self):
        """Yield history records one by one."""
        for item in self.history:
            yield item

    def get_statistics(self):
        """Return total operations, most used operator, and result statistics."""
        if not self.history:
            return {
                "total_operations": 0,
                "most_used_operator": None,
                "max_result": None,
                "min_result": None,
                "average_result": None,
                "positive_results": 0,
            }

        operator_count = {}
        results = self.get_results_only()
        positive_results = self.filter_positive_results()

        for item in self.history_generator():
            operator = item["operator"]
            operator_count[operator] = operator_count.get(operator, 0) + 1

        most_used = max(operator_count, key=operator_count.get)

        return {
            "total_operations": len(self.history),
            "most_used_operator": most_used,
            "max_result": max(results),
            "min_result": min(results),
            "average_result": statistics.mean(results),
            "positive_results": len(positive_results),
        }
