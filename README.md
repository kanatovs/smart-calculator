# Smart Calculator

A Python calculator with a dark Tkinter interface, operation history, and JSON/CSV persistence. Arithmetic, history storage, and the interface live in separate modules. No third-party Python packages are required.

## Features

- Addition, subtraction, multiplication, division, powers, and modulus.
- Integer and decimal input, including `.5`, `+2`, and `1e-3`.
- Operation history with identifiers and timestamps; search by operator.
- Save and load JSON; export CSV.
- Statistics: operation count, most frequent operator, minimum, maximum, mean, and positive result count.
- Operand and result validation: complex values, booleans, NaN, infinity, and overflowing values are rejected before entering history.
- Full JSON structure validation before replacing the history in memory.
- Atomic JSON/CSV writes: the destination is replaced only after the temporary file is written, flushed, and synchronized successfully.

## Run

Use Python 3.11 or newer with Tkinter. The standard Windows Python installer includes Tkinter; Linux may require the system package `python3-tk` and a graphical session. CI covers Python 3.11–3.13 on Windows and Ubuntu.

From the project directory:

```bash
python main.py
```

On Windows, `py main.py` is another option. Run `python -m tkinter` to check that Tkinter can open a window.

Enter two numbers and select an operator. `Save JSON` saves the history, `Load JSON` replaces it with the saved records, and `Export CSV` creates a table. `Clear History` only clears memory; use `Save JSON` afterward to save an empty history.

## Data files

The application creates `data/` beside `main.py`, independently of the shell's working directory:

| File | Contents |
| --- | --- |
| `data/history.json` | Saved history available through `Load JSON` |
| `data/history.csv` | Most recent CSV export |
| `data/logs.txt` | Log of successful calculator calls |

These runtime files are ignored by Git. The project directory must be writable for persistence. If logging fails, the calculation still succeeds and a warning is written to the console. Save, export, and load errors appear in an application dialog.

History is not loaded at startup or saved automatically on exit. Use `Load JSON` and `Save JSON` explicitly. A failed load, including a missing file, preserves both the current history and its next identifier. A valid empty JSON array, `[]`, explicitly replaces it with empty history.

The [JSON example](examples/history.json) and [CSV example](examples/history.csv) contain synthetic records. To try the JSON example, first back up any existing history, create `data/` if needed, copy `examples/history.json` to `data/history.json`, and select `Load JSON`. Tests use temporary directories and never overwrite runtime data.

## History format

The JSON root must be an array of records. Each record contains exactly six fields:

```json
{
    "id": 1,
    "operand1": 12.0,
    "operand2": 4.0,
    "operator": "/",
    "result": 3.0,
    "timestamp": "2026-01-01 12:00:00"
}
```

Identifiers must be unique positive integers. Operands and results must be finite Python `int` or `float` values within the supported floating-point range; booleans are rejected. Operators must be `+`, `-`, `*`, `/`, `**`, or `%`. Timestamps use `YYYY-MM-DD HH:MM:SS` and must represent valid dates and times. Validation checks the entire file before replacing history, preserves record order, and sets the next identifier after the largest loaded identifier. Imported results are validated as numbers; they are not recalculated from their operands.

## Checks

```bash
python -m unittest discover -s tests -v
python -m compileall -q calculator main.py tests
```

Tests cover arithmetic, statistics, JSON and CSV contents, overflow, negative fractional powers, invalid JSON and encoding, failed loads, interrupted writes, failed file replacement, logging errors, and storage error dialogs. Dialog tests substitute message boxes and do not open a window. The [GitHub Actions workflow](.github/workflows/tests.yml) runs the unit tests on Windows and Ubuntu with Python 3.11, 3.12, and 3.13.

## Structure

```text
main.py                       # Tkinter interface
calculator/
  calculator.py               # Operation execution and validation
  operations.py               # Operation and BinaryOperation class hierarchy
  validators.py               # Numeric input and supported operators
  history_manager.py          # History, statistics, JSON/CSV
  paths.py                    # Stable runtime paths
  decorators.py               # Successful operation log
examples/                     # Synthetic history files
tests/                        # Unit and regression tests
.github/workflows/tests.yml   # Automated checks
```

The project demonstrates abstract classes, inheritance and polymorphism, composition of `Calculator` and `HistoryManager`, a logging decorator, a history generator, `map`/`filter`, and regular expressions for input validation.

## Limitations

- The GUI converts input to Python `float`. Normal rounding applies, such as the result of `0.1 + 0.2`; this is not a financial precision model.
- The calculator accepts only finite real operands and results. Integers too large to convert to a finite float are also rejected. Extremely large integer powers are checked before allocating their result.
- Fractional powers of negative bases are rejected, including mathematically real roots such as `(-8) ** (1/3)`. There is no separate root operation.
- Multiple instances writing the same history file are not coordinated; the last successful save replaces the previous file.
- Atomic replacement preserves the old file on ordinary write failures. It does not provide backups or a guarantee against every filesystem or power failure.
- Automated tests do not verify the window's appearance on every screen size.

## Contributors

- **Alikhan:** `main.py`, user interaction, styling, input fields, result display, search, statistics window, and integration.
- **Sabyrzhan:** calculator logic, operation classes, history manager, JSON/CSV, decorator, validation, generator, and original tests.
