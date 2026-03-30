"""Tests for dataset fingerprints."""

import pandas as pd
from driftlab.fingerprint import fingerprint_dataframe, fingerprint_pair


def test_fingerprint_stable_dtypes():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    fp = fingerprint_dataframe(df, sample_rows=5)
    assert fp["row_count"] == 2
    assert fp["column_count"] == 2
    assert "int" in fp["columns"]["a"].lower() or fp["columns"]["a"] == "int64"
    assert "sample_sha256" in fp


def test_fingerprint_pair():
    ref = pd.DataFrame({"x": [1.0, 2.0]})
    cur = pd.DataFrame({"x": [3.0, 4.0]})
    pair = fingerprint_pair(ref, cur, sample_rows=0)
    assert pair["reference"]["row_count"] == 2
    assert "sample_sha256" not in pair["reference"]
