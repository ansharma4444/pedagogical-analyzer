"""
storage.py
Lightweight CSV-based persistence so analysis results survive a page
refresh or app restart, without needing a database server.

Keeping this in its own module (instead of directly inside the Streamlit
app) means the persistence strategy could be swapped for SQLite or a real
database later without touching the UI or analysis code at all.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "results.csv")

COLUMNS = ["App Name", "Target Grade", "Reading Grade", "Cognitive Level", "Alignment Score"]


def load_results() -> pd.DataFrame:
    """Load saved results from disk, or an empty (correctly-shaped) frame if none exist yet."""
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)


def save_results(df: pd.DataFrame) -> None:
    """Persist the full results table to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(DATA_FILE, index=False)


def append_result(df: pd.DataFrame, record: dict) -> pd.DataFrame:
    """Add one new record to the results table, persist it, and return the updated table."""
    row = {col: record[col] for col in COLUMNS}
    updated = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_results(updated)
    return updated
