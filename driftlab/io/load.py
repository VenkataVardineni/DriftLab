"""Data loading utilities."""

import pandas as pd
from pathlib import Path
from typing import Any


def load_dataframe(file_path: str, **kwargs: Any) -> pd.DataFrame:
    """
    Load a tabular file into a pandas DataFrame.

    Supports .csv, .parquet, and .pq by extension. Optional dependency:
    pyarrow or fastparquet for Parquet.

    Args:
        file_path: Path to data file
        **kwargs: Passed to pd.read_csv or pd.read_parquet

    Returns:
        Loaded DataFrame
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix in (".parquet", ".pq"):
        return pd.read_parquet(file_path, **kwargs)
    return pd.read_csv(file_path, **kwargs)

