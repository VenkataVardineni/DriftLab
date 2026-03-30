"""Lightweight dataset fingerprints for run manifests."""

from __future__ import annotations

import hashlib
from typing import Any, Dict

import pandas as pd


def fingerprint_dataframe(df: pd.DataFrame, sample_rows: int = 5) -> Dict[str, Any]:
    """
    Stable fingerprint: row/column counts, dtype map, optional sample hash.

    sample_rows: first N rows hashed as CSV bytes for cheap content sanity;
    set 0 to skip hashing (faster on huge frames).
    """
    columns = {str(c): str(df[c].dtype) for c in df.columns}
    out: Dict[str, Any] = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": columns,
    }
    if sample_rows > 0 and len(df) > 0:
        chunk = df.head(sample_rows)
        payload = chunk.to_csv(index=False).encode("utf-8")
        out["sample_sha256"] = hashlib.sha256(payload).hexdigest()
    return out


def fingerprint_pair(ref: pd.DataFrame, cur: pd.DataFrame, sample_rows: int = 5) -> Dict[str, Any]:
    return {
        "reference": fingerprint_dataframe(ref, sample_rows=sample_rows),
        "current": fingerprint_dataframe(cur, sample_rows=sample_rows),
    }
