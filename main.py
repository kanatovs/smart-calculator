import tkinter as tk
from tkinter import messagebox

from calculator.calculator import Calculator
from calculator.paths import HISTORY_CSV, HISTORY_JSON
from calculator.validators import VALID_OPERATORS, is_valid_number, is_valid_operator


BG_COLOR = "#1e1e1e"
CARD_COLOR = "#2a2a2a"
ENTRY_COLOR = "#333333"
BUTTON_COLOR = "#3a3a3a"
BUTTON_ACTIVE = "#4a4a4a"
TEXT_COLOR = "#f5f5f5"
MUTED_TEXT = "#cfcfcf"
ACCENT_COLOR = "#6ea8fe"
LISTBOX_BG = "#252526"
LISTBOX_SELECT = "#3d6fb4"


class CalculatorApp:
    """Tkinter graphical interface for the calculator system."""

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Calculator")
        self.root.geometry("760x620")
        self.root.configure(bg=BG_COLOR)

        self.calculator = Calculator()
        self.json_file = HISTORY_JSON
        self.csv_file = HISTORY_CSV

        self.create_widgets()

    def create_widgets(self):
        """Create all Tkinter widgets for the application window."""
        title_label = tk.Label(
            self.root,
            text="Smart Calculator with History",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title_label.pack(pady=12)

        input_frame = tk.Frame(self.root, bg=CARD_COLOR, bd=0, highlightthickness=1, highlightbackground="#3a3a3a")
        input_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            input_frame,
            text="First Number:",
            font=("Arial", 11),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).grid(row=0, column=0, padx=15, pady=12, sticky="e")

        self.entry_operand1 = tk.Entry(
            input_frame,
            width=20,
            font=("Arial", 11),
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat"
        )
        self.entry_operand1.grid(row=0, column=1, padx=10, pady=12)

        tk.Label(
            input_frame,
            text="Second Number:",
            font=("Arial", 11),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).grid(row=1, column=0, padx=15, pady=12, sticky="e")

        self.entry_operand2 = tk.Entry(
            input_frame,
            width=20,
            font=("Arial", 11),
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat"
        )
        self.entry_operand2.grid(row=1, column=1, padx=10, pady=12)

        button_frame = tk.Frame(self.root, bg=BG_COLOR)
        button_frame.pack(pady=12)

        for index, operator in enumerate(VALID_OPERATORS):
            tk.Button(
                button_frame,
                text=operator,
                width=8,
                font=("Arial", 11, "bold"),
                bg=BUTTON_COLOR,
                fg=TEXT_COLOR,
                activebackground=BUTTON_ACTIVE,
                activeforeground=TEXT_COLOR,
                relief="flat",
                bd=0,
                command=lambda op=operator: self.perform_operation(op)
            ).grid(row=0, column=index, padx=6, pady=6)

        self.result_label = tk.Label(
            self.root,
            text="Result: ",
            font=("Arial", 14, "bold"),
            bg=BG_COLOR,
            fg=ACCENT_COLOR
        )
        self.result_label.pack(pady=10)

        history_label = tk.Label(
            self.root,
            text="Operation History",
            font=("Arial", 13, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        history_label.pack(pady=6)

        history_container = tk.Frame(self.root, bg=BG_COLOR)
        history_container.pack(pady=5)

        self.history_listbox = tk.Listbox(
            history_container,
            width=95,
            height=15,
            font=("Consolas", 10),
            bg=LISTBOX_BG,
            fg=TEXT_COLOR,
            selectbackground=LISTBOX_SELECT,
            selectforeground=TEXT_COLOR,
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3a3a3a"
        )
        self.history_listbox.pack(side="left")

        scrollbar = tk.Scrollbar(
            history_container,
            command=self.history_listbox.yview,
            bg=BUTTON_COLOR,
            troughcolor=BG_COLOR,
            activebackground=BUTTON_ACTIVE
        )
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        action_frame = tk.Frame(self.root, bg=BG_COLOR)
        action_frame.pack(pady=12)

        self.make_button(action_frame, "Save JSON", self.save_history, 14).grid(row=0, column=0, padx=5, pady=5)
        self.make_button(action_frame, "Load JSON", self.load_history, 14).grid(row=0, column=1, padx=5, pady=5)
        self.make_button(action_frame, "Export CSV", self.export_csv, 14).grid(row=0, column=2, padx=5, pady=5)
        self.make_button(action_frame, "Show Stats", self.show_statistics, 14).grid(row=0, column=3, padx=5, pady=5)
        self.make_button(action_frame, "Clear History", self.clear_history, 14).grid(row=0, column=4, padx=5, pady=5)

        extra_frame = tk.Frame(self.root, bg=BG_COLOR)
        extra_frame.pack(pady=10)

        tk.Label(
            extra_frame,
            text="Search by operator:",
            font=("Arial", 10),
            bg=BG_COLOR,
            fg=MUTED_TEXT
        ).grid(row=0, column=0, padx=5, pady=5)

        self.entry_search_operator = tk.Entry(
            extra_frame,
            width=10,
            font=("Arial", 10),
            bg=ENTRY_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat"
        )
        self.entry_search_operator.grid(row=0, column=1, padx=5, pady=5)

        self.make_button(extra_frame, "Search", self.search_by_operator, 12).grid(row=0, column=2, padx=5, pady=5)
        self.make_button(extra_frame, "Show All", self.refresh_history_list, 12).grid(row=0, column=3, padx=5, pady=5)

    def make_button(self, parent, text, command, width):
        """Create a styled Tkinter button."""
        return tk.Button(
            parent,
            text=text,
            width=width,
            font=("Arial", 10, "bold"),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            activebackground=BUTTON_ACTIVE,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            command=command
        )

    def get_input_values(self):
        """Validate user input and return both operands as floats."""
        operand1 = self.entry_operand1.get().strip()
        operand2 = self.entry_operand2.get().strip()

        if not is_valid_number(operand1) or not is_valid_number(operand2):
            raise ValueError("Please enter valid numbers")

        return float(operand1), float(operand2)

    def perform_operation(self, operator):
        """Run a selected calculator operation and update the result label."""
        try:
            operand1, operand2 = self.get_input_values()
            result = self.calculator.perform_operation(operand1, operand2, operator)
            self.result_label.config(text=f"Result: {result}")
            self.refresh_history_list()
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def refresh_history_list(self, records=None):
        """Refresh the listbox with all records or selected records."""
        self.history_listbox.delete(0, tk.END)

        if records is None:
            records = self.calculator.history_manager.get_all()

        for item in records:
            line = (
                f"ID: {item['id']} | "
                f"{item['operand1']} {item['operator']} {item['operand2']} = {item['result']} | "
                f"{item['timestamp']}"
            )
            self.history_listbox.insert(tk.END, line)

    def save_history(self):
        """Save operation history to a JSON file."""
        try:
            self.calculator.history_manager.save_to_json(self.json_file)
        except (OSError, ValueError) as error:
            self.show_storage_error("save history", error)
        else:
            messagebox.showinfo("Success", f"History saved to {self.json_file}")

    def load_history(self):
        """Load operation history from a JSON file."""
        try:
            self.calculator.history_manager.load_from_json(self.json_file)
        except (OSError, ValueError) as error:
            self.show_storage_error("load history", error)
        else:
            self.refresh_history_list()
            messagebox.showinfo("Success", "History loaded from JSON")

    def export_csv(self):
        """Export operation history to a CSV file."""
        try:
            self.calculator.history_manager.export_to_csv(self.csv_file)
        except (OSError, ValueError) as error:
            self.show_storage_error("export history", error)
        else:
            messagebox.showinfo("Success", f"History exported to {self.csv_file}")

    def show_storage_error(self, action, error):
        """Report file errors without discarding the user's current history."""
        if isinstance(error, FileNotFoundError):
            detail = "No saved history file was found. Save JSON first."
        elif isinstance(error, PermissionError):
            detail = "Permission denied. Check that the data folder is writable."
        elif isinstance(error, ValueError):
            detail = f"Invalid history data: {error}"
        else:
            detail = f"File access failed: {error}"
        messagebox.showerror(
            "Storage error", f"Could not {action}.\n{detail}\nCurrent history remains in memory."
        )

    def show_statistics(self):
        """Show calculated statistics in a message box."""
        stats = self.calculator.history_manager.get_statistics()

        message = (
            f"Total operations: {stats['total_operations']}\n"
            f"Most used operator: {stats['most_used_operator']}\n"
            f"Max result: {stats['max_result']}\n"
            f"Min result: {stats['min_result']}\n"
            f"Average result: {stats['average_result']}\n"
            f"Positive results: {stats['positive_results']}"
        )

        messagebox.showinfo("Statistics", message)

    def clear_history(self):
        """Clear all operation history from memory."""
        self.calculator.history_manager.clear_history()
        self.refresh_history_list()
        messagebox.showinfo("Success", "History cleared")

    def search_by_operator(self):
        """Search history records by a valid operator."""
        operator = self.entry_search_operator.get().strip()

        if not is_valid_operator(operator):
            messagebox.showerror("Error", "Please enter a valid operator")
            return

        results = self.calculator.history_manager.search_by_operator(operator)
        self.refresh_history_list(results)


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()
