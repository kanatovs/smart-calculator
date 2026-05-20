# Smart Calculator with Operation History

## Project Description

Smart Calculator is a modular Python system for arithmetic calculations. It has a Tkinter graphical interface, operation history, JSON saving/loading, CSV export, statistics, input validation, logging, unit tests, and a package-based code structure.

The project is designed as a small real-world financial/calculation record system. It follows modular architecture: the GUI, calculator logic, operation classes, validation, decorators, and history storage are separated into different files.

## Features

- Addition, subtraction, multiplication, division, power, and modulus
- Dark Tkinter GUI
- Operation history
- Save and load history with JSON
- Export history to CSV
- Search history by operator
- Statistics for total operations, most used operator, max/min/average result, and positive results
- Regex input validation
- Custom logging decorator
- Custom generator for history traversal
- `lambda`, `map`, and `filter` for data transformation
- Unit tests with `unittest`

## Project Structure

```text
calculator_final/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── calculator/
│   ├── __init__.py
│   ├── calculator.py
│   ├── decorators.py
│   ├── history_manager.py
│   ├── operations.py
│   └── validators.py
├── data/
│   ├── history.csv
│   └── history.json
└── tests/
    ├── __init__.py
    └── test_calculator.py
```

## Architecture and Logic Flow

1. The user enters two numbers in the GUI.
2. `validators.py` checks the input using regex.
3. The user selects an operator.
4. `Calculator` chooses the correct operation class.
5. The selected operation object calculates the result.
6. `HistoryManager` saves the result as a dictionary record.
7. History can be saved to JSON, loaded from JSON, exported to CSV, searched, or analyzed.
8. Unit tests check operation logic, validation, history, JSON, CSV, generator, and functional tools.

## OOP Design

```text
Operation (abstract base class)
└── BinaryOperation
    ├── Addition
    ├── Subtraction
    ├── Multiplication
    ├── Division
    ├── Power
    └── Modulus
```

### OOP Principles Used

- **Classes and objects:** calculator operations are represented as classes.
- **Encapsulation:** operands are stored as protected attributes `_operand1` and `_operand2` and accessed through properties.
- **Inheritance:** all concrete operations inherit from `BinaryOperation`, which inherits from `Operation`.
- **Polymorphism:** every operation class has its own `calculate()` method.
- **Association:** `Calculator` uses `HistoryManager` to store operation records.

## Data Management

The project uses these collections:

- **List:** stores all history records.
- **Dictionary:** stores one operation record with id, operands, operator, result, and timestamp.
- **Set-like logic / fixed operator collection:** operator validation checks allowed operators.
- **Tuple:** `VALID_OPERATORS` stores the fixed sequence of supported operators.

The project uses file persistence:

- `json` for saving and loading history.
- `csv` for exporting history.
- `os` for creating the `data/` directory when needed.

## Functional Programming

The project uses functional tools in `history_manager.py`:

- `lambda` in result transformations.
- `map()` in `get_results_only()`.
- `filter()` in `filter_positive_results()`.

## Decorator, Generator, and Regex

- `@log_action` logs successful calculator operations to `data/logs.txt`.
- `history_generator()` yields history records one by one.
- `re.fullmatch()` validates numeric input.

## Individual Contributions

- **Alikhan:** GUI in `main.py`, user interaction, dark interface design, input fields, result display, search button, statistics window, final integration.
- **Sabyrzhan:** calculator logic, OOP operation classes, history manager, JSON/CSV persistence, decorator, validation, generator, and unit tests.

## Quality Assurance

- Modular package structure with `__init__.py`
- Clear function and class names
- Docstrings for modules, classes, and main methods
- Error handling for invalid input, invalid operators, division by zero, and modulus by zero
- Unit tests for core logic and file operations

## How to Run

```bash
python main.py
```

On Windows, this can also work:

```bash
py main.py
```

## How to Run Tests

```bash
python -m unittest discover -s tests -v
```

Expected result:

```text
Ran 18 tests
OK
```

## Requirements

No external packages are required. The project uses only Python standard library modules:

- tkinter
- unittest
- json
- csv
- os
- re
- abc
- datetime
- functools
- tempfile
