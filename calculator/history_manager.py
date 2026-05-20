"""History manager for saving, loading, searching, and analyzing operations."""

import csv
import json
import os
from datetime import datetime


class HistoryManager:
    """Manage calculator operation records and file persistence."""

    def __init__(self):
        self.history = []
        self._next_id = 1

    def add_record(self, operand1, operand2, operator, result):
        """Add one operation record to history and return the created record."""
        record = {
            "id": self._next_id,
            "operand1": operand1,
            "operand2": operand2,
            "operator": operator,
            "result": result,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.history.append(record)
        self._next_id += 1
        return record

    def get_all(self):
        """Return all history records."""
        return self.history

    def clear_history(self):
        """Remove all history records and reset the next record id."""
        self.history = []
        self._next_id = 1

    def save_to_json(self, filename):
        """Save operation history to a JSON file."""
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.history, file, indent=4)

    def load_from_json(self, filename):
        """Load operation history from a JSON file if it exists."""
        if not os.path.exists(filename):
            self.history = []
            self._next_id = 1
            return

        with open(filename, "r", encoding="utf-8") as file:
            self.history = json.load(file)

        if self.history:
            self._next_id = max(item["id"] for item in self.history) + 1
        else:
            self._next_id = 1

    def export_to_csv(self, filename):
        """Export operation history to a CSV file."""
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "id",
                    "operand1",
                    "operand2",
                    "operator",
                    "result",
                    "timestamp",
                ],
            )
            writer.writeheader()
            writer.writerows(self.history)

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
            "average_result": sum(results) / len(results),
            "positive_results": len(positive_results),
        }
