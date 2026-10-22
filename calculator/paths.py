"""Stable storage paths, independent of the shell's working directory."""

from pathlib import Path

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
HISTORY_JSON = DATA_DIRECTORY / "history.json"
HISTORY_CSV = DATA_DIRECTORY / "history.csv"
ACTIVITY_LOG = DATA_DIRECTORY / "logs.txt"
