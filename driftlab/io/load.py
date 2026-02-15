"""Data loading utilities."""

import pandas as pd
from pathlib import Path
from typing import Optional


def load_dataframe(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to CSV file
        **kwargs: Additional arguments to pass to pd.read_csv
        
    Returns:
        Loaded DataFrame
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    return pd.read_csv(file_path, **kwargs)

