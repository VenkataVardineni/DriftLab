"""Tests for data loading."""

import pytest
import pandas as pd
from driftlab.io.load import load_dataframe


def test_load_csv(tmp_path):
    p = tmp_path / "a.csv"
    pd.DataFrame({"x": [1, 2]}).to_csv(p, index=False)
    df = load_dataframe(str(p))
    assert list(df.columns) == ["x"]
    assert len(df) == 2


def test_load_parquet(tmp_path):
    pytest.importorskip("pyarrow")
    p = tmp_path / "a.parquet"
    pd.DataFrame({"x": [1, 2, 3]}).to_parquet(p, index=False)
    df = load_dataframe(str(p))
    assert list(df.columns) == ["x"]
    assert len(df) == 3
